#!/usr/bin/env python3
"""Bind national faction-rule and manifest contributions from installed vanilla.

Country-scope faction ownership and fulfillment are read live. One-shot goal
effects are represented by their actual idea/dynamic-modifier carrier elsewhere;
they are never counted a second time as an assumed historical faction reward.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from build_source_bindings import DEFAULT_GAME, ROOT, TOKEN_ID, digest, localizations, number
from validate_mod import ParseError, parse_script


def fields(entries, key):
    return [entry for entry in entries if entry.key == key]


def scalar(entries, key, default=None):
    values = fields(entries, key)
    return values[0].value if len(values) == 1 and isinstance(values[0].value, str) else default


def canonical(value):
    return format(value, "f")


def static_name(names, key, language, trail=()):
    if key in trail:
        raise ValueError("cyclic_name_alias")
    texts = {row["text"] for row in names[language].get(key, []) if row["text"].strip()}
    if len(texts) != 1:
        raise ValueError("missing_or_ambiguous_name")
    text = re.sub(r"\$([A-Za-z0-9_.-]+)\$",
                  lambda m: static_name(names, m.group(1), language, trail + (key,)), next(iter(texts)))
    if any(token in text for token in ("$", "[", "]")):
        raise ValueError("nonstatic_name")
    return re.sub(r"\s+", " ", re.sub(r"(?:\\[nrt]|[\r\n\t])+", " ", text)).strip()


def build(game, index_path):
    selected = {row["key"] for row in json.loads(index_path.read_text(encoding="utf-8"))["records"]}
    names = localizations(game)
    by_modifier = {key: [] for key in sorted(selected)}
    source_files, excluded, failures, definitions = {}, [], [], []
    for path in sorted((game / "common/factions").rglob("*.txt")):
        relative = path.relative_to(game).as_posix()
        source_files[relative] = {"sha256": digest(path)}
        try:
            tree = parse_script(path.read_text(encoding="utf-8-sig"), relative)
        except ParseError as error:
            failures.append({"file": relative, "reason": str(error)})
            continue
        constants = {entry.key: number(entry.value) for entry in tree
                     if entry.key and entry.key.startswith("@") and number(entry.value) is not None}
        for entry in tree:
            if isinstance(entry.value, list):
                definitions.append((relative, entry, constants))
    counts = Counter(entry.key for path, entry, _ in definitions
                     if path.startswith(("common/factions/rules/", "common/factions/goals/"))
                     and "/groups/" not in path)

    def reject(path, definition, reason, **extra):
        excluded.append({"source_file": path, "source_id": definition.key,
                         "source_line": definition.line, "reason": reason, **extra})

    def literal(value, constants):
        return constants.get(value) if isinstance(value, str) and value.startswith("@") else number(value)

    def add_block(path, definition, constants, block, source_id, kind, activation,
                  *, expression_mode=None, section=None):
        name_key = scalar(definition.value, "name", definition.key)
        try:
            zh, en = (static_name(names, name_key, language) for language in ("simp_chinese", "english"))
        except ValueError as error:
            reject(path, definition, "source_name_not_static_single_line", detail=str(error), name_loc_key=name_key)
            return
        counts = Counter(entry.key for entry in block)
        for entry in block:
            if entry.key not in selected:
                reject(path, definition, "outside_selected_national_modifier_catalogue", modifier=entry.key,
                       line=entry.line)
                continue
            if counts[entry.key] != 1:
                reject(path, definition, "duplicate_modifier_key", modifier=entry.key, line=entry.line)
                continue
            value = literal(entry.value, constants)
            if value is None or value == 0:
                reject(path, definition, "nonliteral_or_zero_modifier", modifier=entry.key, line=entry.line)
                continue
            row = {
                "id": f"{kind}:{source_id}:{entry.key}", "source_id": source_id,
                "source_type": kind, "source_category": kind,
                "name_loc_key": name_key, "name_zh": zh,
                "display_name_zh": zh, "display_name_en": en,
                "value": int(value) if value == value.to_integral_value() else float(value),
                "value_literal": canonical(value), "activation_script": activation,
                "source": {"file": path, "line": entry.line, "definition_line": definition.line,
                           "sha256": source_files[path]["sha256"]},
                "runtime_validated": False,
            }
            if expression_mode:
                reversed_scale = expression_mode == "reversed"
                row["value_kind"] = "runtime"
                row["value_expression"] = {
                    "variable": "ROOT.faction_manifest_fulfillment",
                    "coefficient": canonical(-value if reversed_scale else value),
                    "offset": canonical(value if reversed_scale else Decimal(0)),
                }
            if section:
                row["progress_section"] = section
            by_modifier[entry.key].append(row)

    for path, definition, constants in definitions:
        if not TOKEN_ID.fullmatch(definition.key or ""):
            continue
        if path.startswith("common/factions/rules/") and "/groups/" not in path:
            blocks = fields(definition.value, "modifier")
            if not blocks:
                continue
            if counts[definition.key] != 1 or len(blocks) != 1 or not isinstance(blocks[0].value, list):
                reject(path, definition, "ambiguous_rule_definition")
                continue
            # `trigger` checks who may perform a diplomatic action; it is not
            # an enable condition for the rule's country modifiers.
            activation = f"AND = {{ is_in_faction = yes has_active_rule = {definition.key} }}"
            add_block(path, definition, constants, blocks[0].value, definition.key, "faction_rule", activation)
        elif path.startswith("common/factions/goals/"):
            if scalar(definition.value, "is_manifest") != "yes":
                if fields(definition.value, "complete_effect"):
                    reject(path, definition, "goal_effects_use_actual_carrier_no_historical_double_count")
                continue
            progress = fields(definition.value, "ratio_progress")
            if counts[definition.key] != 1 or len(progress) != 1 or not isinstance(progress[0].value, list):
                reject(path, definition, "ambiguous_manifest_progress")
                continue
            base_gate = f"is_in_faction = yes has_faction_goal = {definition.key}"
            for mode in ("scale", "reversed"):
                blocks = fields(progress[0].value, mode)
                if len(blocks) > 1:
                    reject(path, definition, "ambiguous_manifest_scaling", mode=mode)
                    continue
                if not blocks:
                    continue
                nonzero = "faction_manifest_fulfillment < 1" if mode == "reversed" else "faction_manifest_fulfillment > 0"
                activation = f"AND = {{ {base_gate} {nonzero} }}"
                add_block(path, definition, constants, blocks[0].value,
                          f"{definition.key}:{mode}", "faction_manifest", activation, expression_mode=mode)
            sections = fields(progress[0].value, "progress_sections")
            if len(sections) > 1:
                reject(path, definition, "ambiguous_manifest_progress_sections")
                continue
            for section in sections[0].value if sections else []:
                if not isinstance(section.value, list):
                    continue
                min_value = literal(scalar(section.value, "min", "0"), constants)
                max_value = literal(scalar(section.value, "max", "1"), constants)
                if min_value is None or max_value is None or min_value > max_value:
                    reject(path, definition, "nonliteral_progress_section_bounds", section=section.key)
                    continue
                blocks = fields(section.value, "modifier")
                if len(blocks) != 1 or not isinstance(blocks[0].value, list):
                    reject(path, definition, "ambiguous_section_modifier", section=section.key)
                    continue
                # Boundaries are inclusive; native documentation explicitly
                # allows two sections to be active at a shared boundary.
                activation = (f"AND = {{ {base_gate} "
                              f"NOT = {{ faction_manifest_fulfillment < {canonical(min_value)} }} "
                              f"NOT = {{ faction_manifest_fulfillment > {canonical(max_value)} }} }}")
                add_block(path, definition, constants, blocks[0].value,
                          f"{definition.key}:section:{section.key}", "faction_manifest_section", activation,
                          section={"name": section.key, "min": canonical(min_value), "max": canonical(max_value)})
        elif path.startswith("common/factions/member_upgrades/") and fields(definition.value, "bonus"):
            reject(path, definition, "member_manpower_pool_bonus_not_country_modifier")

    # Older ideology faction modifiers follow the faction LEADER's government,
    # not the member's own ideology. An isolated 1.19.3 probe verified .5 for
    # both leader/member under a democratic leader, and zero after changing the
    # leader or leaving the faction, irrespective of the member's government.
    for path in sorted((game / "common/ideologies").glob("*.txt")):
        relative = path.relative_to(game).as_posix()
        source_files[relative] = {"sha256": digest(path)}
        try:
            tree = parse_script(path.read_text(encoding="utf-8-sig"), relative)
        except ParseError as error:
            failures.append({"file": relative, "reason": str(error)})
            continue
        for outer in tree:
            if outer.key != "ideologies" or not isinstance(outer.value, list):
                continue
            for ideology in outer.value:
                if not isinstance(ideology.value, list):
                    continue
                for block in fields(ideology.value, "faction_modifiers"):
                    if not isinstance(block.value, list):
                        reject(relative, ideology, "invalid_ideology_faction_modifier_block")
                        continue
                    activation = (f"AND = {{ is_in_faction = yes "
                                  f"faction_leader = {{ has_government = {ideology.key} }} }}")
                    add_block(relative, ideology, {}, block.value,
                              f"{ideology.key}:faction_modifiers", "faction_ideology", activation)

    for rows in by_modifier.values():
        rows.sort(key=lambda row: (row["source_type"], row["source_id"].casefold(), row["source"]["line"]))
    bindings = [row for rows in by_modifier.values() for row in rows]
    ids = {(row["source_type"], row["source_id"]) for row in bindings}
    for relative in ("common/factions/_documentation.md", "documentation/triggers_documentation.md",
                     "documentation/dynamic_variables_documentation.md", "documentation/effects_documentation.md"):
        source_files[relative] = {"sha256": digest(game / relative)}
    return {
        "schema_version": 2, "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "scope": "current_country_active_faction_rules_and_manifest_national_modifiers",
        "statistics": {
            "selected_modifier_count": len(selected), "covered_modifier_count": sum(bool(rows) for rows in by_modifier.values()),
            "binding_count": len(bindings), "binding_count_by_type": dict(sorted(Counter(row["source_type"] for row in bindings).items())),
            "source_count_by_type": dict(sorted(Counter(kind for kind, _ in ids).items())),
            "runtime_binding_count": sum(row.get("value_kind") == "runtime" for row in bindings),
            "source_file_count": len(source_files), "parse_failure_count": len(failures),
            "excluded_by_reason": dict(sorted(Counter(row["reason"] for row in excluded).items())),
        },
        "assumptions": [
            "Scanned vanilla definitions must be the definitions loaded by the game.",
            "Faction modifiers are evaluated only for the currently displayed COUNTRY and its current faction.",
            "Rule trigger/available conditions govern diplomatic use and selection, not the ownership of an already active rule.",
            "Manifest scale/reversed coefficients are applied to the engine's live faction_manifest_fulfillment; the range/collection calculation is not reconstructed.",
            "Manifest progress sections have inclusive bounds and require the corresponding current manifest.",
            "Goal rewards represented by ideas/dynamic modifiers are displayed through those carriers and are never duplicated as inferred completed-goal sources.",
            "Legacy ideology faction_modifiers follow the faction leader's government and are applied to every member; the member's own ideology is not the gate.",
            "Theater commander/unit bonuses, research project properties, manpower sharing pool values and peace-conference cost objects are omitted.",
            "Runtime zero contributions and unresolved residuals are omitted; the country's native total remains authoritative.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False, "other_sources_row": False,
                           "source_type_prefix": False},
        "engine_probes": [
            {"name": "faction_rule", "source_id": "war_declaration_rule_faction_leader_only", "key": "stability_factor", "contribution": -0.05,
             "inactive": ["set_faction_rule = war_declaration_rule_independent_countries_only"],
             "activate": ["set_faction_rule = war_declaration_rule_faction_leader_only"],
             "remove": ["set_faction_rule = war_declaration_rule_independent_countries_only"],
             "also_verify": "Repeat country total/activation for a non-leader faction member; the diplomatic trigger is not a modifier enable."},
            {"name": "faction_manifest_scale", "source_id": "faction_manifest_conquest_of_territory:scale", "key": "offensive_war_stability_factor", "coefficient": 0.15,
             "activate": ["set_faction_manifest = faction_manifest_conquest_of_territory"],
             "remove": ["set_faction_manifest = faction_manifest_defense_of_democracy"],
             "formula": "ROOT.faction_manifest_fulfillment * 0.15",
             "also_verify": "Log faction_manifest_fulfillment, direct source, country modifier before/after; rule out a stale progress value after manifest replacement."},
            {"name": "faction_manifest_reversed", "source_id": "faction_manifest_china_territorial_integrity:reversed", "key": "army_core_defence_factor", "coefficient": -0.1, "offset": 0.1,
             "activate": ["set_faction_manifest = faction_manifest_china_territorial_integrity"],
             "remove": ["set_faction_manifest = faction_manifest_defense_of_democracy"],
             "formula": "0.1 - ROOT.faction_manifest_fulfillment * 0.1"},
            {"name": "faction_manifest_section", "source_id": "faction_manifest_containment_of_communism:section:manifest_fulfilled", "key": "required_garrison_factor", "contribution": -0.15,
             "activate": ["set_faction_manifest = faction_manifest_containment_of_communism"],
             "remove": ["set_faction_manifest = faction_manifest_defense_of_democracy"],
             "note": "Requires the world's non-communist state ratio >= 0.75; log the engine fulfillment before asserting this contribution."},
        ],
        "source_files": source_files, "by_modifier": by_modifier,
        "parse_failures": failures, "excluded": excluded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/faction-source-bindings.json")
    args = parser.parse_args()
    data = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
