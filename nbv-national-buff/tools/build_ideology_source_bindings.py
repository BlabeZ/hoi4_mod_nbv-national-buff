#!/usr/bin/env python3
"""Map the current ruling ideology's literal national modifier contributions.

The owning ideology group, not its popularity or leader subtype, controls
these sources. Only `modifiers` and its explicit `hidden_modifier` wrapper
belong to this adapter. In particular, `faction_modifiers` is a different
scope and is deliberately not attributed to the ruling country here.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from validate_mod import ParseError, parse_script
from build_source_bindings import DEFAULT_GAME, ROOT, TOKEN_ID, digest, localizations, number


def native_name(names, key, language):
    """Require a unique, single-line native group label in each language."""
    candidates = {entry["text"] for entry in names[language].get(key, []) if entry["text"].strip()}
    if len(candidates) != 1:
        raise ValueError("missing_or_ambiguous_localisation_name")
    text = next(iter(candidates))
    if any(token in text for token in ("$", "[", "]")):
        raise ValueError("unresolved_localisation_name")
    return re.sub(r"\s+", " ", re.sub(r"(?:\\[nrt]|[\r\n\t])+", " ", text)).strip()


def build(game, index_path):
    selected = {row["key"] for row in json.loads(index_path.read_text(encoding="utf-8"))["records"]}
    names = localizations(game)
    by_modifier = {key: [] for key in sorted(selected)}
    source_files, definitions, parse_failures, excluded = {}, [], [], []
    possible_failed_ids = set()
    for path in sorted((game / "common/ideologies").glob("*.txt")):
        relative = path.relative_to(game).as_posix()
        text = path.read_text(encoding="utf-8-sig")
        source_files[relative] = {"sha256": digest(path)}
        try:
            tree = parse_script(text, relative)
        except ParseError as error:
            parse_failures.append({"file": relative, "reason": str(error)})
            possible_failed_ids.update(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=\s*\{", text))
            continue
        for outer in tree:
            if outer.key == "ideologies" and isinstance(outer.value, list):
                definitions.extend((node, relative) for node in outer.value if isinstance(node.value, list))
    counts = Counter(node.key for node, _ in definitions)
    accepted_sources = set()
    hidden_binding_count = 0

    def reject(node, path, reason, modifier=None, line=None, **extra):
        item = {"source_id": node.key, "source_type": "ideology", "source_file": path,
                "source_line": line or node.line, "reason": reason}
        if modifier is not None:
            item["modifier"] = modifier
        item.update(extra)
        excluded.append(item)

    for node, path in definitions:
        if counts[node.key] != 1 or node.key in possible_failed_ids:
            reject(node, path, "duplicate_or_unverifiable_definition")
            continue
        if not TOKEN_ID.fullmatch(node.key or ""):
            reject(node, path, "unsupported_source_identifier")
            continue
        try:
            name_zh = native_name(names, node.key, "simp_chinese")
            name_en = native_name(names, node.key, "english")
        except ValueError as error:
            reject(node, path, str(error))
            continue
        modifiers = [entry for entry in node.value if entry.key == "modifiers"]
        if len(modifiers) != 1 or not isinstance(modifiers[0].value, list):
            reject(node, path, "missing_or_ambiguous_country_modifiers")
            continue
        for sibling in node.value:
            if sibling.key in {"faction_modifiers", "foreign_modifier", "targeted_modifier", "member_modifier"}:
                if isinstance(sibling.value, list) and sibling.value:
                    reject(node, path, "non_country_scope_block", line=sibling.line,
                           block=sibling.key, selected_keys=[entry.key for entry in sibling.value if entry.key in selected])

        # hidden_modifier changes native presentation, not ownership/scope.
        # Do not recursively flatten arbitrary nested blocks: these may apply
        # only to a target, unit category, or condition.
        flat = []
        for entry in modifiers[0].value:
            if entry.key == "hidden_modifier" and isinstance(entry.value, list):
                flat.extend((child, "modifiers/hidden_modifier") for child in entry.value)
            else:
                flat.append((entry, "modifiers"))
        key_counts = Counter(entry.key for entry, _ in flat)
        for entry, block_path in flat:
            key = entry.key
            if isinstance(entry.value, list):
                reject(node, path, "nested_non_country_or_unadapted_block", key, entry.line, block_path=block_path)
                continue
            if key not in selected:
                reject(node, path, "modifier_not_in_selected_display_set", key, entry.line)
                continue
            if key_counts[key] != 1:
                reject(node, path, "duplicate_modifier_key", key, entry.line)
                continue
            value = number(entry.value)
            if value is None:
                reject(node, path, "nonliteral_modifier_value", key, entry.line)
                continue
            if value == 0:
                reject(node, path, "zero_value_not_displayed", key, entry.line)
                continue
            activation = f"has_government = {node.key}"
            assert len(parse_script(activation)) == 1
            by_modifier[key].append({
                "id": f"ideology:{node.key}:{key}", "source_id": node.key,
                "source_type": "ideology", "source_category": "ideology",
                "name_loc_key": node.key, "name_zh": name_zh,
                "display_name_zh": name_zh, "display_name_en": name_en,
                "value": int(value) if value == value.to_integral_value() else float(value),
                "value_literal": format(value, "f"),
                "activation": {"has_government": node.key}, "activation_script": activation,
                "source": {"file": path, "line": entry.line, "definition_line": node.line,
                           "block_path": block_path, "sha256": source_files[path]["sha256"]},
                "runtime_validated": False,
            })
            accepted_sources.add(node.key)
            hidden_binding_count += block_path == "modifiers/hidden_modifier"
    for rows in by_modifier.values():
        rows.sort(key=lambda row: (row["source_id"], row["source"]["line"]))
    return {
        "schema_version": 1, "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "scope": "current_ruling_ideology_group_literal_national_modifiers",
        "assumptions": [
            "Scanned vanilla ideology definitions must match the definitions loaded by the game.",
            "has_government checks the current ruling ideology group in COUNTRY scope; popularity and leader subtype do not activate these contributions.",
            "Only the group's modifiers block and its explicit hidden_modifier presentation wrapper are included.",
            "Faction, member, foreign, targeted and arbitrary nested modifiers are not interpreted as current-country ideology contributions.",
            "Values retain native raw units; e.g. civilian_intel_to_others = 15 is not changed to 0.15.",
            "Native names identify the ideology group that owns the modifier, not a party name or an inferred leader subtype.",
            "Rules and AI settings are not numeric modifier contributions; zero values and unresolved residuals are omitted.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False,
                           "other_sources_row": False, "unknown_source_labels": False,
                           "source_type_prefix": False, "one_line_per_source": True},
        "statistics": {
            "selected_modifier_count": len(selected),
            "covered_modifier_count": sum(bool(rows) for rows in by_modifier.values()),
            "binding_count": sum(map(len, by_modifier.values())),
            "source_count": len(accepted_sources),
            "hidden_modifier_binding_count": hidden_binding_count,
            "scanned_file_count": len(source_files), "parsed_definition_count": len(definitions),
            "parse_failure_count": len(parse_failures),
            "excluded_by_reason": dict(sorted(Counter(row["reason"] for row in excluded).items())),
        },
        "evidence": [
            {"file": "documentation/triggers_documentation.md", "line": 4007,
             "claim": "has_government tests the current country's ruling ideology group."},
            {"file": "documentation/effects_documentation.md", "line": 7526,
             "claim": "set_politics sets ruling_party to a new ideology group in country scope."},
            {"file": "common/ideologies/00_ideologies.txt", "line": 186,
             "claim": "Fascist national modifiers contain visible values and a hidden_modifier join_faction_tension contribution."},
        ],
        "engine_probes": [
            {"source_id": "fascism", "modifier": "embargo_cost_factor", "value_literal": "1",
             "name_contains": "法西斯主义", "setup": "set_politics = { ruling_party = democratic }",
             "activate": "set_politics = { ruling_party = fascism }",
             "remove": "set_politics = { ruling_party = democratic }",
             "restore": "set_politics = { ruling_party = fascism }",
             "baseline_ideology_contribution": "-0.5", "activation_total_delta": "1.5",
             "note": "Switching ideology also replaces the head of government; this key has no vanilla start leader contribution in the intended GER probe."},
            {"source_id": "democratic", "modifier": "embargo_cost_factor", "value_literal": "-0.5",
             "name_contains": "民主主义", "setup": "set_politics = { ruling_party = fascism }",
             "activate": "set_politics = { ruling_party = democratic }",
             "remove": "set_politics = { ruling_party = fascism }",
             "baseline_ideology_contribution": "1", "activation_total_delta": "-1.5"},
            {"source_id": "fascism", "modifier": "join_faction_tension", "value_literal": "-0.1",
             "name_contains": "法西斯主义", "setup": "set_politics = { ruling_party = democratic }",
             "activate": "set_politics = { ruling_party = fascism }",
             "remove": "set_politics = { ruling_party = democratic }",
             "restore": "set_politics = { ruling_party = fascism }",
             "baseline_ideology_contribution": "0.8", "activation_total_delta": "-0.9",
             "purpose": "Verify hidden_modifier retains national contribution while the source follows current ruling ideology."},
            {"source_id": "fascism", "modifier": "civilian_intel_to_others", "value_literal": "15.0",
             "name_contains": "法西斯主义", "setup": "set_politics = { ruling_party = democratic }",
             "activate": "set_politics = { ruling_party = fascism }",
             "remove": "set_politics = { ruling_party = democratic }",
             "baseline_ideology_contribution": "20.0", "activation_total_delta": "-5.0",
             "purpose": "Verify native raw intelligence values and matching source formatting, without dividing the contribution by 100."},
        ],
        "source_files": source_files, "by_modifier": by_modifier,
        "uncovered_modifier_keys": [key for key, rows in by_modifier.items() if not rows],
        "parse_failures": parse_failures, "excluded": excluded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/ideology-source-bindings.json")
    args = parser.parse_args()
    data = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
