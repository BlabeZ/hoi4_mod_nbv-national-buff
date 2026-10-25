#!/usr/bin/env python3
"""Bind verified literal national contributions from vanilla doctrines/technology.

Reads the installed definitions, never rewrites them. Unit/equipment/category
blocks and one-shot scripted effects are deliberately not traversed as national
modifiers. A doctrine reward requires both an active doctrine and its actual
mastery level; researching/unlocking a doctrine alone is insufficient.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from build_source_bindings import DEFAULT_GAME, ROOT, digest, localizations, number, TOKEN_ID
from validate_mod import Entry, ParseError, TOKEN, Token, parse_script


VERIFIED_SUBMARINE_EOF_FILE = "common/doctrines/subdoctrines/sea/navy_submarine_doctrines.txt"
VERIFIED_SUBMARINE_EOF_SHA256 = "b0fe32ce5ca0d8e0efba38f747cb1aa0851f29664d6594197d00869fc43fad38"


def parse_with_anonymous_blocks(text, filename):
    """Same ordered AST as validate_mod, plus doctrine's anonymous milestones."""
    tokens = []
    offset, line = 0, 1
    while offset < len(text):
        match = TOKEN.match(text, offset)
        if not match:
            raise ParseError(f"{filename}:{line}: unexpected token")
        kind, value = match.lastgroup, match.group()
        if kind not in ("space", "comment"):
            if kind == "string":
                value = value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
            tokens.append(Token(value, line, kind))
        line += match.group().count("\n")
        offset = match.end()
    cursor = 0

    def block(nested=False):
        nonlocal cursor
        result = []
        while cursor < len(tokens):
            first = tokens[cursor]
            cursor += 1
            if first.kind == "brace" and first.value == "}":
                if not nested:
                    raise ParseError(f"{filename}:{first.line}: unexpected closing brace")
                return result
            if first.kind == "brace" and first.value == "{":
                result.append(Entry(None, None, block(True), first.line))
                continue
            if first.kind not in ("atom", "string"):
                raise ParseError(f"{filename}:{first.line}: invalid key {first.value!r}")
            if cursor < len(tokens) and tokens[cursor].kind == "op":
                op = tokens[cursor].value
                cursor += 1
                if cursor >= len(tokens):
                    raise ParseError(f"{filename}:{first.line}: missing value")
                value_token = tokens[cursor]
                cursor += 1
                if value_token.kind == "brace" and value_token.value == "{":
                    if op != "=":
                        raise ParseError(f"{filename}:{first.line}: block comparison")
                    value = block(True)
                elif value_token.kind in ("atom", "string"):
                    value = value_token.value
                else:
                    raise ParseError(f"{filename}:{first.line}: invalid value")
                result.append(Entry(first.value, op, value, first.line))
            else:
                result.append(Entry(None, None, first.value, first.line))
        if nested:
            raise ParseError(f"{filename}: unclosed block")
        return result
    return block()


def parse_doctrine_file(text, filename, sha256):
    """Recover one inspected vanilla EOF omission without changing the parser.

    In shipped 1.19.3, the last long_range_submarines definition lacks its final
    closing brace. Earlier doctrines in the same file are complete. Content
    fingerprinting prevents this adapter from repairing a different omission.
    """
    try:
        return parse_with_anonymous_blocks(text, filename), None
    except ParseError as original:
        if (filename != VERIFIED_SUBMARINE_EOF_FILE
                or sha256 != VERIFIED_SUBMARINE_EOF_SHA256
                or not str(original).endswith(": unclosed block")):
            raise
        tokens = [match for match in TOKEN.finditer(text)
                  if match.lastgroup not in {"space", "comment"}]
        opens = []
        for index, token in enumerate(tokens):
            if token.lastgroup == "brace":
                if token.group() == "{":
                    opens.append(index)
                elif opens:
                    opens.pop()
                else:
                    raise original
        if (len(opens) != 1 or opens[0] < 2
                or [token.group() for token in tokens[opens[0] - 2:opens[0] + 1]]
                != ["long_range_submarines", "=", "{"]):
            raise
        tree = parse_with_anonymous_blocks(text + "\n}\n", filename)
        if (not tree or tree[-1].key != "long_range_submarines"
                or not isinstance(tree[-1].value, list)):
            raise original
        return tree, {
            "file": filename,
            "sha256": sha256,
            "reason": "verified_vanilla_long_range_submarines_eof_closure",
            "appended_closing_braces": 1,
            "source_files_modified": False,
        }


def find(entries, key):
    return [entry for entry in entries if entry.key == key]


def scalar(entries, key, default=None):
    matches = find(entries, key)
    return matches[0].value if len(matches) == 1 and isinstance(matches[0].value, str) else default


def canonical(value):
    return format(value.normalize(), "f")


class StaticNameError(ValueError):
    pass


def expand_static_name(text, language, names, *, stack=()):
    """Expand native noun aliases before folding lines, including nested aliases.

    Missing, conflicting, cyclic and dynamic aliases fail closed: preserving an
    unresolved native macro could reintroduce line breaks at game runtime.
    """
    macro = re.compile(r"\$([A-Za-z0-9_.-]+)\$")

    def replace(match):
        key = match.group(1)
        if key in stack or len(stack) >= 32:
            raise StaticNameError(f"cyclic_or_deep_alias:{key}")
        values = {row["text"] for row in names[language].get(key, []) if row["text"].strip()}
        if len(values) != 1:
            raise StaticNameError(f"missing_or_ambiguous_alias:{key}")
        return expand_static_name(next(iter(values)), language, names, stack=stack + (key,))

    text = macro.sub(replace, text)
    if "$" in text or "[" in text or "]" in text:
        raise StaticNameError("nonstatic_or_unsupported_name")
    # Native localization stores escaped newlines as text. Fold after recursive
    # expansion so a newline introduced by any alias is also removed.
    text = re.sub(r"(?:\\[nrt]|[\r\n\t])+", " ", text)
    text = text.replace('\\"', '"').replace('\\\\', '\\')
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise StaticNameError("empty_name")
    return text


def build(game, index_path):
    selected = {row["key"] for row in json.loads(index_path.read_text(encoding="utf-8"))["records"]}
    names = localizations(game)
    by_modifier = {key: [] for key in sorted(selected)}
    source_files, parse_failures, parse_recoveries, excluded = {}, [], [], []
    ignored = Counter()
    definitions = []
    tracks = {}
    possible_failed_ids = set()
    for relative_dir, kind in [
        ("common/doctrines/tracks", "track"),
        ("common/doctrines/grand_doctrines", "grand_doctrine"),
        ("common/doctrines/subdoctrines", "subdoctrine"),
        ("common/technologies", "technology"),
    ]:
        for path in sorted((game / relative_dir).rglob("*.txt")):
            relative = path.relative_to(game).as_posix()
            text = path.read_text(encoding="utf-8-sig")
            source_files[relative] = {"sha256": digest(path)}
            try:
                tree, recovery = parse_doctrine_file(text, relative, source_files[relative]["sha256"])
                if recovery:
                    parse_recoveries.append(recovery)
            except ParseError as error:
                parse_failures.append({"file": relative, "reason": str(error)})
                possible_failed_ids.update(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=\s*\{", text))
                continue
            if kind == "technology":
                tree = [tech for outer in tree if outer.key == "technologies"
                        and isinstance(outer.value, list) for tech in outer.value]
            for definition in tree:
                if not isinstance(definition.value, list) or not definition.key:
                    continue
                if kind == "track":
                    tracks.setdefault(definition.key, []).append((definition, relative))
                else:
                    definitions.append((kind, definition, relative))
    counts = Counter((kind, node.key) for kind, node, _ in definitions)
    accepted_sources = set()

    def reject(source_id, path, line, reason, **extra):
        excluded.append({"source_id": source_id, "source_file": path,
                         "source_line": line, "reason": reason, **extra})

    def native_name(key):
        if not isinstance(key, str) or not TOKEN_ID.fullmatch(key):
            return None
        values = {entry["text"] for entry in names["simp_chinese"].get(key, []) if entry["text"].strip()}
        return next(iter(values)) if len(values) == 1 else None

    def add_block(kind, node, path, source_id, name_key, activation, *, display=None,
                  reward_level=None, track=None):
        if not native_name(name_key):
            reject(source_id, path, node.line, "missing_or_ambiguous_chinese_name", name_loc_key=name_key)
            return
        if display and any(not native_name(key) for key in re.findall(r"\$([^$]+)\$", display)):
            reject(source_id, path, node.line, "missing_display_component_name")
            return
        try:
            display_template = display or f"${name_key}$"
            display_zh = expand_static_name(display_template, "simp_chinese", names)
            display_en = expand_static_name(display_template, "english", names)
            resolved_name_zh = expand_static_name(f"${name_key}$", "simp_chinese", names)
        except StaticNameError as error:
            reject(source_id, path, node.line, "unresolved_static_display_name", detail=str(error))
            return
        conditions = {"do_effect", "conditional_modifier", "enable", "trigger"} & {e.key for e in node.value}
        if conditions:
            reject(source_id, path, node.line, "conditional_modifier_not_adapted", fields=sorted(conditions))
            return
        direct = [e for e in node.value if e.key in selected]
        # Explicit country-level modifier containers occur at the activation
        # level only. Never recurse into unit, equipment, AI or scripted effects.
        for e in node.value:
            if e.key in {"modifiers", "modifier"} and isinstance(e.value, list):
                direct.extend(c for c in e.value if c.key in selected)
            elif isinstance(e.value, list) and e.key not in {"milestones", "rewards"}:
                ignored[e.key or "anonymous"] += 1
        duplicates = Counter(e.key for e in direct)
        found = False
        for entry in direct:
            key = entry.key
            if duplicates[key] != 1:
                reject(source_id, path, entry.line, "duplicate_modifier_key", modifier=key)
                continue
            value = number(entry.value)
            if value is None:
                reject(source_id, path, entry.line, "nonliteral_or_object_modifier_value", modifier=key)
                continue
            if value == 0:
                reject(source_id, path, entry.line, "zero_value_not_displayed", modifier=key)
                continue
            if len(parse_script(activation, source_id)) != 1:
                raise ValueError(f"Activation must be one AST entry: {source_id}")
            result = {
                "id": f"{kind}:{source_id}:{key}", "source_id": source_id,
                "source_type": kind, "source_category": kind,
                "name_loc_key": name_key, "name_zh": resolved_name_zh,
                "display_name_zh": display_zh, "display_name_en": display_en,
                "value": int(value) if value == value.to_integral_value() else float(value),
                "value_literal": canonical(value), "activation_script": activation,
                "activation": {"script": activation},
                "source": {"file": path, "line": entry.line, "definition_line": node.line,
                           "sha256": source_files[path]["sha256"]},
                "runtime_validated": False,
            }
            if reward_level is not None:
                result["reward_level"] = reward_level
            if track:
                result["track"] = track
            by_modifier[key].append(result)
            accepted_sources.add((kind, source_id))
            found = True
        if not found:
            reject(source_id, path, node.line, "no_selected_direct_nonzero_country_modifier")

    for kind, node, path in definitions:
        if counts[kind, node.key] != 1 or node.key in possible_failed_ids:
            reject(node.key, path, node.line, "duplicate_or_unverifiable_definition")
            continue
        if not TOKEN_ID.fullmatch(node.key):
            reject(node.key, path, node.line, "unsupported_source_identifier")
            continue
        name_key = scalar(node.value, "name", node.key)
        if kind == "technology":
            # Tech on_research_complete can unlock an idea/doctrine. Its effects
            # are handled by the owned object's adapter, never attributed again.
            # A has_tech-only source stayed visible after set_technology = 0 in
            # the isolated lifecycle probe. Require researched-array membership
            # too; lifecycle validation must verify this independent view.
            activation = (f"AND = {{ has_tech = {node.key} "
                          f"is_in_array = {{ array = researched_techs value = token:{node.key} }} }}")
            add_block(kind, node, path, node.key, name_key, activation)
            continue
        if scalar(node.value, "allow_in_multiple_tracks") == "yes":
            reject(node.key, path, node.line, "multiple_simultaneous_tracks_not_adapted")
            continue
        activation = f"has_doctrine = {node.key}"
        add_block(kind, node, path, node.key, name_key, activation)
        if kind == "subdoctrine":
            reward_nodes = find(node.value, "rewards")
            if len(reward_nodes) > 1:
                reject(node.key, path, node.line, "ambiguous_rewards_container")
                continue
            if not reward_nodes or not isinstance(reward_nodes[0].value, list):
                continue
            for level, reward in enumerate(reward_nodes[0].value, 1):
                source_id = f"{node.key}:reward:{level}"
                if not isinstance(reward.value, list) or not reward.key:
                    reject(source_id, path, reward.line, "unnamed_reward_not_displayed")
                    continue
                reward_key = f"{node.key}_{reward.key}"
                activation = f"AND = {{ has_doctrine = {node.key} has_mastery_level = {{ amount = {level} sub_doctrine = {node.key} }} }}"
                add_block("subdoctrine_reward", reward, path, source_id, name_key, activation,
                          display=f"${name_key}$ · ${reward_key}$", reward_level=level)
        else:
            milestone_nodes = find(node.value, "milestones")
            track_nodes = find(node.value, "tracks")
            if len(milestone_nodes) != 1 or len(track_nodes) != 1:
                continue
            milestones, track_list = milestone_nodes[0].value, track_nodes[0].value
            if not isinstance(milestones, list) or not isinstance(track_list, list) or len(milestones) != len(track_list):
                reject(node.key, path, node.line, "unmatched_milestones_and_tracks")
                continue
            track_ids = [entry.value for entry in track_list]
            for position, (milestone, track_id) in enumerate(zip(milestones, track_ids), 1):
                source_id = f"{node.key}:milestone:{position}"
                if not isinstance(track_id, str) or track_ids.count(track_id) != 1 or len(tracks.get(track_id, [])) != 1:
                    reject(source_id, path, milestone.line, "ambiguous_milestone_track")
                    continue
                track_node, _ = tracks[track_id][0]
                track_key = scalar(track_node.value, "name", track_id)
                activation = f"AND = {{ has_doctrine = {node.key} has_completed_track = {track_id} }}"
                add_block("doctrine_milestone", milestone, path, source_id, name_key, activation,
                          display=f"${name_key}$ · ${track_key}$", track=track_id)

    for values in by_modifier.values():
        values.sort(key=lambda row: (row["source_type"], row["source_id"], row["source"]["line"]))
    return {
        "schema_version": 1, "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "scope": "vanilla_current_doctrines_mastered_rewards_and_researched_technology_literal_national_modifiers",
        "assumptions": [
            "The scanned vanilla definitions must match those loaded by the game.",
            "Only direct literal selected national modifiers and explicit activation-level modifier containers are read.",
            "Unit/category/equipment/targeted/local blocks and one-shot effects are excluded, even when they contain a selected key.",
            "Grand and subdoctrines require has_doctrine (currently active), not historical completion or tech unlock.",
            "Rewards additionally require their one-based mastery level; later rewards are not assumed earned.",
            "Milestones require the currently active grand doctrine and its completed unique track.",
            "A technology's research completion effects do not duplicate contributions from the granted idea or doctrine.",
            "Technology sources require both has_tech and current researched_techs array membership; removal behavior requires engine lifecycle verification.",
            "Unresolved residuals and zero sources are never displayed.",
            "Display names recursively expand verified static native aliases and fold all line breaks; unresolved or dynamic names are excluded.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False, "other_sources_row": False,
                           "static_aliases_expanded": True, "one_line_per_source": True},
        "statistics": {
            "selected_modifier_count": len(selected),
            "covered_modifier_count": sum(bool(values) for values in by_modifier.values()),
            "binding_count": sum(map(len, by_modifier.values())),
            "source_count": len(accepted_sources),
            "source_count_by_type": dict(sorted(Counter(kind for kind, _ in accepted_sources).items())),
            "binding_count_by_type": dict(sorted(Counter(row["source_type"] for rows in by_modifier.values() for row in rows).items())),
            "scanned_file_count": len(source_files), "parsed_definition_count": len(definitions),
            "parse_failure_count": len(parse_failures),
            "verified_eof_recovery_count": len(parse_recoveries),
            "excluded_by_reason": dict(sorted(Counter(row["reason"] for row in excluded).items())),
            "ignored_nested_blocks": dict(sorted(ignored.items())),
        },
        "engine_probes": [
            {"source_id": "basic_machine_tools", "modifier": "production_factory_max_efficiency_factor", "value_literal": "0.1",
             "setup": "set_technology = { basic_machine_tools = 1 popup = no }",
             "remove": "set_technology = { basic_machine_tools = 0 popup = no }",
             "restore": "set_technology = { basic_machine_tools = 1 popup = no }"},
            {"source_id": "new_mobile_warfare", "modifier": "army_speed_factor", "value_literal": "0.1",
             "setup": "set_grand_doctrine = new_mobile_warfare", "remove": "set_grand_doctrine = superior_firepower",
             "restore": "set_grand_doctrine = new_mobile_warfare"},
            {"source_id": "defensive_postures:reward:1", "modifier": "dig_in_speed_factor", "value_literal": "0.05",
             "setup": "set_grand_doctrine = new_mobile_warfare set_sub_doctrine = defensive_postures",
             "activate": "add_mastery = { amount = 100 sub_doctrine = defensive_postures }",
             "remove": "set_sub_doctrine = mobile_infantry",
             "restore": "set_sub_doctrine = defensive_postures add_mastery = { amount = 100 sub_doctrine = defensive_postures }",
             "restoration_note": "Changing a subdoctrine resets mastery in engine tests; restoring activation alone must still hide the unearned reward.",
             "unearned_source_id": "defensive_postures:reward:5"},
            {"source_id": "coastal_defence_fleet:reward:1", "modifier": "refit_speed", "value_literal": "0.15",
             "setup": "set_grand_doctrine = new_fleet_in_being set_sub_doctrine = coastal_defence_fleet",
             "activate": "add_mastery = { amount = 100 sub_doctrine = coastal_defence_fleet }",
             "purpose": "Verify vanilla singular modifier container in doctrine reward."},
            {"source_id": "new_mobile_warfare:milestone:1", "modifier": "land_reinforce_rate", "value_literal": "0.02",
             "setup": "set_grand_doctrine = new_mobile_warfare set_sub_doctrine = defensive_postures",
             "activate": "add_mastery = { amount = 500 sub_doctrine = defensive_postures }",
             "remove": "set_grand_doctrine = superior_firepower",
             "restore": "set_grand_doctrine = new_mobile_warfare set_sub_doctrine = defensive_postures add_mastery = { amount = 500 sub_doctrine = defensive_postures }",
             "purpose": "Verify completed infantry track milestone remains gated by active grand doctrine."},
        ],
        "source_files": source_files, "by_modifier": by_modifier,
        "uncovered_modifier_keys": [key for key, rows in by_modifier.items() if not rows],
        "parse_failures": parse_failures, "parse_recoveries": parse_recoveries, "excluded": excluded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/doctrine-technology-source-bindings.json")
    args = parser.parse_args()
    data = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
