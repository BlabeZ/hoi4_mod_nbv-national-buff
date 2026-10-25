#!/usr/bin/env python3
"""Build conservative vanilla idea contribution bindings for NBV tooltips.

Only this generator's JSON output is written.  A source is a direct, nonzero,
numeric country modifier of an active idea whose definition is unambiguous.
The number is NOT a replacement for ROOT.modifier@key, and the resulting list
is intentionally incomplete.  No residual / unknown / zero source is invented.

The bindings are valid only while the scanned vanilla idea definitions remain
the definitions loaded by the game.  A mod that overrides those IDs needs a
separate adapter; has_idea alone cannot detect a definition override.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from validate_mod import ParseError, TOKEN, parse_script  # no validation main() runs


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME = Path(r"E:\Steam\steamapps\common\Hearts of Iron IV")
SAFE_CATEGORIES = {
    "country", "hidden_ideas", "economy", "mobilization_laws", "trade_laws",
    "army_spirit", "academy_spirit", "division_command_spirit",
    "navy_spirit", "naval_academy_spirit", "naval_command_spirit",
    "air_force_spirit", "air_force_command_spirit",
}
IDEA_FIELDS = {
    "allowed", "available", "allowed_civil_war", "allowed_to_remove", "cancel",
    "cancel_if_invalid", "picture", "name", "cost", "removal_cost", "modifier",
    "default", "ai_will_do", "on_add", "on_remove", "rule", "research_bonus",
    "equipment_bonus", "targeted_modifier", "traits", "visible", "ledger",
    "level", "do_effect",
}
CONDITIONAL_FIELDS = {"do_effect", "enable", "trigger", "if", "conditional_modifier"}
NUMERIC = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")
TOKEN_ID = re.compile(r"[A-Za-z0-9_.-]+\Z")
LOC = re.compile(r'^\s*([A-Za-z0-9_.-]+):(?:\d+)?\s+"((?:[^"\\]|\\.)*)"')

# These shipped 1.19.3 files omit only the closing brace of their outer ideas
# wrapper. HOI4 accepts them at EOF. The strict parser correctly rejects them,
# but rejecting their entire contents also loses hundreds of valid spirits.
# Recover only the exact inspected bytes; never guess how to repair changed
# definitions or malformed third-party files. Original game files stay intact.
VERIFIED_OUTER_IDEAS_EOF = {
    "common/ideas/SOV.txt": "3c6c883aa521e8a34a5c6852716df86dde9b82db40dc41b1b5aa515af9608911",
    "common/ideas/persia.txt": "2e1b23ea425e93f90f79533e0c4666689dedf24ee293174d2d3ee034d6fc6ac9",
    "common/ideas/switzerland.txt": "8f67fd650041e6a6aa21bf73b607900d91dce76752b58f5d32d342d0326945be",
}


def parse_idea_file(text, filename, sha256):
    """Strict parse, with audited EOF-only recovery for shipped idea files.

    The byte hash is essential: brace balance alone cannot distinguish a lost
    outer brace from an earlier missing brace that changes category nesting.
    Return the tree and an optional explicit recovery record for the manifest.
    """
    try:
        return parse_script(text, filename), None
    except ParseError as original:
        if (VERIFIED_OUTER_IDEAS_EOF.get(filename) != sha256
                or not str(original).endswith(": unclosed block")):
            raise
        tokens = [match for match in TOKEN.finditer(text)
                  if match.lastgroup not in {"space", "comment"}]
        if ([token.group() for token in tokens[:3]] != ["ideas", "=", "{"]):
            raise
        opens = []
        for token in tokens:
            if token.lastgroup == "brace":
                if token.group() == "{":
                    opens.append(token.start())
                elif opens:
                    opens.pop()
                else:
                    raise original
        if opens != [tokens[2].start()]:
            raise
        tree = parse_script(text + "\n}\n", filename)
        if len(tree) != 1 or tree[0].key != "ideas" or not isinstance(tree[0].value, list):
            raise original
        return tree, {
            "file": filename,
            "sha256": sha256,
            "reason": "verified_vanilla_outer_ideas_eof_closure",
            "appended_closing_braces": 1,
            "source_files_modified": False,
        }


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def localizations(game):
    """Only verify a name exists; final display still resolves the native loc key."""
    result = {}
    for language in ("english", "simp_chinese"):
        values = defaultdict(list)
        for path in sorted((game / "localisation" / language).rglob("*.yml")):
            for line, text in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
                match = LOC.match(text)
                if match:
                    key, value = match.groups()
                    values[key].append({"text": value, "file": path.relative_to(game).as_posix(), "line": line})
        result[language] = values
    return result


def number(value):
    if not isinstance(value, str) or not NUMERIC.fullmatch(value):
        return None
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        return None
    return parsed if parsed.is_finite() else None


def build(game, index_path):
    index = json.loads(index_path.read_text(encoding="utf-8"))
    selected = {row["key"] for row in index["records"]}
    file_manifest, excluded, definitions, parse_failures, parse_recoveries = {}, [], [], [], []
    possible_failed_ids = set()
    for path in sorted((game / "common" / "ideas").glob("*.txt")):
        relative = path.relative_to(game).as_posix()
        text = path.read_text(encoding="utf-8-sig")
        file_manifest[relative] = {"sha256": digest(path)}
        try:
            tree, recovery = parse_idea_file(text, relative, file_manifest[relative]["sha256"])
            if recovery:
                parse_recoveries.append(recovery)
        except ParseError as error:
            parse_failures.append({"file": relative, "reason": str(error)})
            # Fail closed: even a parsed file's ID is rejected if it might also
            # be defined in a file whose full structure cannot be verified.
            possible_failed_ids.update(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=\s*\{", text))
            continue
        for outer in tree:
            if outer.key != "ideas" or not isinstance(outer.value, list):
                continue
            for category in outer.value:
                if not isinstance(category.value, list):
                    continue
                for idea in category.value:
                    if not isinstance(idea.value, list):
                        continue  # category settings such as law = yes
                    definitions.append((category.key, idea, relative))

    counts = Counter(idea.key for _, idea, _ in definitions)
    names = localizations(game)
    by_modifier = {key: [] for key in sorted(selected)}
    accepted_sources = set()
    ignored_blocks = Counter()

    def reject(idea, path, reason, modifier=None, line=None, **extra):
        record = {"source_id": idea.key, "source_file": path,
                  "source_line": line or idea.line, "reason": reason}
        if modifier is not None:
            record["modifier"] = modifier
        record.update(extra)
        excluded.append(record)

    for category, idea, path in definitions:
        if category not in SAFE_CATEGORIES:
            reject(idea, path, "category_not_adapted", category=category)
            continue
        if counts[idea.key] != 1 or idea.key in possible_failed_ids:
            reject(idea, path, "duplicate_or_unverifiable_source_definition")
            continue
        if not TOKEN_ID.fullmatch(idea.key or ""):
            reject(idea, path, "unsupported_source_identifier")
            continue
        field_counts = Counter(child.key for child in idea.value)
        uncertain = sorted((set(field_counts) & CONDITIONAL_FIELDS) | (set(field_counts) - IDEA_FIELDS))
        if uncertain:
            reject(idea, path, "conditional_or_unknown_idea_fields", fields=uncertain)
            continue
        if field_counts["traits"]:
            reject(idea, path, "trait_contribution_not_adapted")
            continue
        modifiers = [child for child in idea.value if child.key == "modifier"]
        if not modifiers:
            reject(idea, path, "no_direct_modifier")
            continue
        if len(modifiers) != 1 or not isinstance(modifiers[0].value, list):
            reject(idea, path, "ambiguous_modifier_block")
            continue
        name_fields = [child for child in idea.value if child.key == "name"]
        if len(name_fields) > 1:
            reject(idea, path, "ambiguous_name")
            continue
        name_key = name_fields[0].value if name_fields else idea.key
        if not isinstance(name_key, str) or not TOKEN_ID.fullmatch(name_key):
            reject(idea, path, "non_token_name")
            continue
        # Missing or conflicting Chinese source names are not shown as raw IDs.
        native_names = names["simp_chinese"].get(name_key, [])
        name_values = {entry["text"] for entry in native_names if entry["text"].strip()}
        if len(name_values) != 1:
            reject(idea, path, "missing_or_ambiguous_chinese_name", name_loc_key=name_key)
            continue
        direct = modifiers[0].value
        key_counts = Counter(child.key for child in direct)
        for child in idea.value:
            if child.key in {"equipment_bonus", "targeted_modifier", "research_bonus", "on_add", "on_remove"}:
                ignored_blocks[child.key] += 1
        for entry in direct:
            key = entry.key
            if key not in selected:
                if isinstance(entry.value, list):
                    ignored_blocks["nested_or_object_modifier"] += 1
                continue
            if key_counts[key] != 1:
                reject(idea, path, "duplicate_modifier_key", key, entry.line)
                continue
            parsed = number(entry.value)
            if parsed is None:
                reject(idea, path, "nonliteral_or_object_modifier_value", key, entry.line)
                continue
            if parsed == 0:
                reject(idea, path, "zero_value_not_displayed", key, entry.line)
                continue
            value = int(parsed) if parsed == parsed.to_integral_value() else float(parsed)
            by_modifier[key].append({
                "id": f"idea:{idea.key}:{key}",
                "source_id": idea.key,
                "source_type": "idea",
                "source_category": category,
                "name_loc_key": name_key,
                "name_zh": next(iter(name_values)),
                "value": value,
                "value_literal": entry.value,
                "activation": {"has_idea": idea.key},
                "activation_script": f"has_idea = {idea.key}",
                "source": {"file": path, "line": entry.line, "idea_line": idea.line,
                           "sha256": file_manifest[path]["sha256"]},
                "runtime_validated": False,
            })
            accepted_sources.add(idea.key)

    for values in by_modifier.values():
        values.sort(key=lambda row: (row["source_id"].casefold(), row["source"]["file"], row["source"]["line"]))
    return {
        "schema_version": 1,
        "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "scope": "vanilla_ideas_direct_constant_country_modifiers_only",
        "assumptions": [
            "The scanned vanilla idea definitions must match the definitions loaded by the game.",
            "has_idea is evaluated in the current player country at tooltip evaluation time.",
            "do_effect, traits, duplicate definitions and nonliteral values are excluded.",
            "Availability, visibility and cancellation rules select ownership; they are not substituted for has_idea.",
            "Only the direct modifier block is read; targeted, equipment, research and event-effect blocks are never counted.",
            "This is an incomplete source list, never a replacement for the engine total.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False,
                           "other_sources_row": False, "unknown_source_labels": False},
        "statistics": {
            "selected_modifier_count": len(selected),
            "covered_modifier_count": sum(bool(values) for values in by_modifier.values()),
            "binding_count": sum(len(values) for values in by_modifier.values()),
            "source_idea_count": len(accepted_sources),
            "scanned_file_count": len(file_manifest),
            "parsed_definition_count": len(definitions),
            "parse_failure_count": len(parse_failures),
            "verified_eof_recovery_count": len(parse_recoveries),
            "excluded_by_reason": dict(sorted(Counter(item["reason"] for item in excluded).items())),
            "ignored_non_direct_blocks": dict(sorted(ignored_blocks.items())),
        },
        "source_files": file_manifest,
        "by_modifier": by_modifier,
        "uncovered_modifier_keys": [key for key, values in by_modifier.items() if not values],
        "parse_failures": parse_failures,
        "parse_recoveries": parse_recoveries,
        "excluded": excluded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/source-bindings.json")
    args = parser.parse_args()
    data = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
