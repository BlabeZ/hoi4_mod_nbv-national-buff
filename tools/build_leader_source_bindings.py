#!/usr/bin/env python3
"""Build conservative, current-country-leader trait contribution bindings.

Only the JSON report is generated.  Country leader traits are read from the
vanilla common/country_leader database, never from unit_leader.  A source is
shown only while has_country_leader_with_trait confirms the CURRENT leader
holds that trait.  Hidden/targeted/conditional/nested contributions are not
reconstructed, and no unexplained residual is invented.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from validate_mod import ParseError, parse_script
from build_source_bindings import localizations, number


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME = Path(r"E:\Steam\steamapps\common\Hearts of Iron IV")
TOKEN_ID = re.compile(r"[A-Za-z0-9_.-]+\Z")
SAFE_METADATA = {"random", "sprite", "name", "ai_will_do"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(game, index_path):
    index = json.loads(index_path.read_text(encoding="utf-8"))
    selected = {row["key"] for row in index["records"]}
    # The native modifier registry distinguishes modifier values from arbitrary
    # trait metadata.  Never treat a bare attack/defense/skill field as a buff.
    registry_path = ROOT.parent / "hoi4-modding-guide/vanilla-modifier-catalog/data/catalog.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    modifier_keys = {row["key"].lower() for row in registry["records"]}
    canonical = {key.lower(): key for key in selected}
    all_names = localizations(game)
    names = all_names["simp_chinese"]
    definitions, failures, files, excluded = [], [], {}, []
    uncertain_ids = set()
    for path in sorted((game / "common/country_leader").glob("*.txt")):
        relative = path.relative_to(game).as_posix()
        text = path.read_text(encoding="utf-8-sig")
        files[relative] = {"sha256": digest(path)}
        try:
            tree = parse_script(text, relative)
        except ParseError as error:
            failures.append({"file": relative, "reason": str(error)})
            uncertain_ids.update(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=\s*\{", text))
            continue
        for outer in tree:
            if outer.key == "leader_traits" and isinstance(outer.value, list):
                definitions.extend((trait, relative) for trait in outer.value
                                   if isinstance(trait.value, list))
    counts = Counter(trait.key.lower() for trait, _ in definitions if trait.key)
    by_modifier = {key: [] for key in sorted(selected)}
    accepted = set()

    def reject(trait, file, reason, **extra):
        excluded.append({"source_id": trait.key, "source_file": file,
                         "source_line": trait.line, "reason": reason, **extra})

    for trait, file in definitions:
        if not trait.key or not TOKEN_ID.fullmatch(trait.key):
            reject(trait, file, "unsupported_trait_identifier")
            continue
        if counts[trait.key.lower()] != 1 or trait.key in uncertain_ids:
            reject(trait, file, "duplicate_or_unverifiable_trait_definition")
            continue
        # Fail closed for hidden_modifier, targeted_modifier, do_effect, enable,
        # dynamic values, nested terrain/unit blocks, or unknown trait fields.
        # ai_will_do affects AI selection only; it does not scale the trait.
        bad_fields = []
        for field in trait.value:
            key = (field.key or "").lower()
            if key in SAFE_METADATA:
                if key != "ai_will_do" and isinstance(field.value, list):
                    bad_fields.append(key)
                continue
            if key not in modifier_keys or isinstance(field.value, list) or number(field.value) is None:
                bad_fields.append(key or "<bare_value>")
        if bad_fields:
            reject(trait, file, "conditional_nested_or_nonliteral_trait", fields=sorted(set(bad_fields)))
            continue
        direct_counts = Counter((field.key or "").lower() for field in trait.value)
        if any(count > 1 for key, count in direct_counts.items() if key != "ai_will_do"):
            reject(trait, file, "duplicate_trait_field")
            continue
        explicit_names = [field.value for field in trait.value if field.key == "name"]
        name_key = explicit_names[0] if explicit_names else trait.key
        if not isinstance(name_key, str) or not TOKEN_ID.fullmatch(name_key):
            reject(trait, file, "unsupported_trait_name")
            continue
        name_values = {entry["text"] for entry in names.get(name_key, []) if entry["text"].strip()}
        if len(name_values) != 1:
            reject(trait, file, "missing_or_ambiguous_chinese_name", name_loc_key=name_key)
            continue
        name_zh = next(iter(name_values))
        english_values = {entry["text"] for entry in all_names["english"].get(name_key, [])
                          if entry["text"].strip()}
        name_en = next(iter(english_values)) if len(english_values) == 1 else name_zh
        # Native trait labels occasionally intentionally wrap their rank onto a
        # second line.  The viewer requires exactly one physical source row, so
        # expose an alias-ready single-line spelling without changing vanilla.
        single_line = lambda text: re.sub(r"(?:\\n|[\r\n])+", " ", text)
        found = False
        for field in trait.value:
            key = canonical.get((field.key or "").lower())
            if key is None:
                continue
            value = number(field.value)
            if value == 0:
                continue
            found = True
            by_modifier[key].append({
                "id": f"leader_trait:{trait.key}:{key}",
                "source_id": trait.key,
                "source_type": "country_leader_trait",
                "source_category": "current_country_leader_trait",
                "name_loc_key": name_key,
                "name_zh": name_zh,
                "name_en": name_en,
                "name_single_line_zh": single_line(name_zh),
                "name_single_line_en": single_line(name_en),
                "requires_single_line_alias": any("\\n" in text or "\n" in text or "\r" in text
                                                  for text in (name_zh, name_en)),
                "value": int(value) if value == value.to_integral_value() else float(value),
                "value_literal": field.value,
                "activation": {"has_country_leader_with_trait": trait.key},
                "activation_script": f"has_country_leader_with_trait = {trait.key}",
                "source": {"file": file, "line": field.line, "trait_line": trait.line,
                           "sha256": files[file]["sha256"]},
                "runtime_validated": False,
            })
        if found:
            accepted.add(trait.key)
        else:
            reject(trait, file, "no_selected_nonzero_direct_modifier")
    for rows in by_modifier.values():
        rows.sort(key=lambda row: (row["source_id"].casefold(), row["source"]["file"], row["source"]["line"]))
    return {
        "schema_version": 1,
        "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "input_registry": {"path": str(registry_path), "sha256": digest(registry_path)},
        "scope": "vanilla_current_country_leader_direct_constant_traits_only",
        "assumptions": [
            "The scanned vanilla trait definitions must match the definitions loaded by the game.",
            "has_country_leader_with_trait checks only the current country leader, not all recruited leaders.",
            "Only common/country_leader is scanned; personal unit_leader stats are never included.",
            "Traits containing conditions, hidden/targeted blocks, nonliteral values or duplicate IDs are excluded.",
            "This is an incomplete source list, never a replacement for ROOT.modifier@key.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False,
                           "other_sources_row": False, "unknown_source_labels": False},
        "statistics": {
            "selected_modifier_count": len(selected),
            "covered_modifier_count": sum(bool(rows) for rows in by_modifier.values()),
            "binding_count": sum(len(rows) for rows in by_modifier.values()),
            "source_trait_count": len(accepted),
            "scanned_file_count": len(files),
            "parsed_definition_count": len(definitions),
            "parse_failure_count": len(failures),
            "excluded_by_reason": dict(sorted(Counter(row["reason"] for row in excluded).items())),
        },
        "source_files": files,
        "by_modifier": by_modifier,
        "uncovered_modifier_keys": [key for key, rows in by_modifier.items() if not rows],
        "parse_failures": failures,
        "excluded": excluded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/leader-source-bindings.json")
    args = parser.parse_args()
    result = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
