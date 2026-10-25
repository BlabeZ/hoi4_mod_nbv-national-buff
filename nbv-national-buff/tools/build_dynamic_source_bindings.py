#!/usr/bin/env python3
"""Build conservative national dynamic-modifier / active-decision sources.

Only direct literal values are emitted here; the companion adapter reads live
native variables. Dynamic values and enable conditions are cached daily by
HOI4. Current enable conditions can therefore precede the cached total. This
adapter never forces that cache to refresh or tracks gameplay history.
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


DECISION_TARGET_FIELDS = {
    "target_trigger", "target_root_trigger", "targets", "target_array",
    "targets_dynamic", "state_target",
}
DYNAMIC_CONTROL_FIELDS = {
    "icon", "enable", "remove_trigger", "attacker_modifier", "name",
}
DECISION_UNSAFE_FIELDS = {"do_effect", "enable", "conditional_modifier", "scale"}
NATIVE_DYNAMIC_NAME_FUNCTIONS = {
    "NORDIC_get_adjective": "common/scripted_localisation/AAT_Nordics_scripted_loc.txt",
    "NORDIC_get_alliance_name": "common/scripted_localisation/AAT_Nordics_scripted_loc.txt",
    "IRQ_navy_modifier_key": "common/scripted_localisation/GOE_IRQ_scripted_loc.txt",
}


def fields(block, key):
    return [entry for entry in block if entry.key == key]


def always_yes(block):
    return isinstance(block, list) and len(block) == 1 and (
        block[0].key, block[0].op, block[0].value
    ) == ("always", "=", "yes")


def canonical(value):
    return format(value, "f")


def flatten_native_name(names, key, language, trail=(), allow_dynamic=False):
    """Resolve only static native aliases into one unambiguous source label."""
    if key in trail:
        raise ValueError("cyclic_localisation_alias")
    candidates = {row["text"] for row in names[language].get(key, []) if row["text"].strip()}
    if len(candidates) != 1:
        raise ValueError("missing_or_ambiguous_localisation_name")
    text = next(iter(candidates))
    text = re.sub(r"\$([A-Za-z0-9_.-]+)\$",
                  lambda match: flatten_native_name(names, match.group(1), language, trail + (key,), allow_dynamic),
                  text)
    inspected = text
    if allow_dynamic:
        def checked_function(match):
            name = match.group(1)
            if (name not in NATIVE_DYNAMIC_NAME_FUNCTIONS and
                    not re.fullmatch(r"(?:ROOT|[A-Z]{3})\.GetAdjective", name)):
                raise ValueError("unsupported_dynamic_name_context")
            return "NATIVE_COUNTRY_NAME"
        inspected = re.sub(r"\[([^\[\]]+)\]", checked_function, inspected)
    if "$" in inspected or "[" in inspected or "]" in inspected:
        raise ValueError("unresolved_dynamic_localisation_name")
    # Literal localisation line escapes are converted before whitespace folding.
    # Do not let one source inject a second tooltip contribution row.
    text = re.sub(r"\s+", " ", re.sub(r"(?:\\[nrt]|[\r\n\t])+", " ", text)).strip()
    if not text:
        raise ValueError("empty_localisation_name")
    return text


def source_display_names(names, key, allow_dynamic=False):
    """Retain native country-context names instead of replacing their meaning.

    The limited functions above are vanilla defined_text names audited in the
    same country scope; direct GetAdjective calls are country names. FROM,
    PREV, state/unit names, arbitrary functions and unresolved aliases are not
    accepted. Native localisation remains authoritative at runtime.
    """
    try:
        zh = flatten_native_name(names, key, "simp_chinese")
        en = flatten_native_name(names, key, "english")
        return {"display_name_zh": zh, "display_name_en": en,
                "native_dynamic_name": False}
    except ValueError:
        if not allow_dynamic:
            raise
        zh = flatten_native_name(names, key, "simp_chinese", allow_dynamic=True)
        en = flatten_native_name(names, key, "english", allow_dynamic=True)
        return {"display_name_zh": None, "display_name_en": None,
                "native_dynamic_name": True,
                "native_name_expressions": sorted(set(re.findall(r"\[([^\[\]]+)\]", zh + en))),
                "native_name_scope": "current_country"}


def render_native_trigger(entries):
    """Serialize original trigger AST without inferring gameplay state."""
    def atom(value):
        if re.fullmatch(r"[^\s{}=<>!\"#]+", value):
            return value
        return json.dumps(value, ensure_ascii=False)
    rendered = []
    for entry in entries:
        value = ("{ " + render_native_trigger(entry.value) + " }") if isinstance(entry.value, list) else atom(entry.value)
        rendered.append((atom(entry.key) + " " + entry.op + " " if entry.key is not None else "") + value)
    return " ".join(rendered)


def walk_paths(entries, ancestors=()):
    for entry in entries:
        yield entry, ancestors
        if isinstance(entry.value, list):
            yield from walk_paths(entry.value, ancestors + (entry.key,))


def addition_scope(relative, ancestors):
    """Conservative lexical scope evidence, never a substitute for runtime scope.

    Only an entirely known state/character usage set is excluded. Unknown
    scripted-effect contexts remain guarded by COUNTRY has_dynamic_modifier.
    """
    initial = "country" if relative.startswith(("history/countries/", "common/decisions/", "common/national_focus/")) else "unknown"
    current = initial
    for position, key in enumerate(ancestors):
        if key == "country_event":
            current = initial = "country"
        elif key in {"ROOT", "root"}:
            current = initial
        elif key in {"PREV", "FROM", "FROMFROM", "PREVPREV", "this", "THIS"}:
            current = "unknown"
        elif key and ((key.isdecimal() and not (position and ancestors[position - 1] == "random_list")) or key in {"capital_scope", "capital", "state"} or
                      key.startswith(("every_", "random_")) and key.endswith("_state")):
            current = "state"
        elif key in {"OWNER", "CONTROLLER", "owner", "controller", "overlord", "faction_leader"}:
            current = "country"
        elif key and ((re.fullmatch(r"[A-Z]{3}", key) and key not in {"AND", "NOT"}) or
                      key.startswith(("every_", "random_")) and key.endswith("_country")):
            current = "country"
        elif key and (key.startswith(("every_", "random_")) and (key.endswith("_unit_leader") or key.endswith("_character"))):
            current = "character"
    return current


def find_targeted_dynamic_additions(game):
    """A plain has_dynamic_modifier cannot count target-specific instances.

    Search every vanilla script file, not merely decision effect blocks. The
    generated audit records all explicit `scope` additions. Fail closed for an
    unparseable file by excluding each dynamic ID mentioned by an add block.
    Parameterized `$...$` modifier identifiers require fail-closed exclusions
    for all definitions, because their possible concrete IDs are unknown.
    """
    targeted, manifest, failures, unresolved, usages = {}, {}, [], [], {}
    for folder in ("common", "events", "history"):
        for path in sorted((game / folder).rglob("*.txt")):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if "add_dynamic_modifier" not in text:
                continue
            relative = path.relative_to(game).as_posix()
            manifest[relative] = {"sha256": digest(path)}
            try:
                tree = parse_script(text, relative)
            except ParseError as error:
                failures.append({"file": relative, "reason": str(error)})
                ids = re.findall(r"add_dynamic_modifier\s*=\s*\{[^{}]*?modifier\s*=\s*([^\s{}#]+)", text)
                for source_id in ids:
                    if TOKEN_ID.fullmatch(source_id):
                        targeted.setdefault(source_id, []).append({"file": relative, "reason": "unparsed_addition_file"})
                    else:
                        unresolved.append({"file": relative, "reason": "parameterized_added_dynamic_id_in_unparsed_file", "modifier": source_id})
                continue
            for entry, ancestors in walk_paths(tree):
                if entry.key != "add_dynamic_modifier" or not isinstance(entry.value, list):
                    continue
                modifiers = fields(entry.value, "modifier")
                if len(modifiers) != 1 or not isinstance(modifiers[0].value, str):
                    unresolved.append({"file": relative, "line": entry.line, "reason": "ambiguous_added_dynamic_id"})
                    continue
                source_id = modifiers[0].value
                if not TOKEN_ID.fullmatch(source_id):
                    unresolved.append({"file": relative, "line": entry.line, "reason": "parameterized_added_dynamic_id", "modifier": source_id})
                    continue
                usages.setdefault(source_id, []).append({"file": relative, "line": entry.line,
                                                        "lexical_scope": addition_scope(relative, ancestors)})
                if fields(entry.value, "scope"):
                    targeted.setdefault(source_id, []).append({"file": relative, "line": entry.line, "reason": "explicit_target_scope"})
    return targeted, manifest, failures, unresolved, usages


def build(game, index_path):
    selected = {row["key"] for row in json.loads(index_path.read_text(encoding="utf-8"))["records"]}
    names = localizations(game)
    by_modifier = {key: [] for key in sorted(selected)}
    excluded, parse_failures, source_files, definitions = [], [], {}, []
    possible_failed_ids = set()
    for folder, source_type in (("dynamic_modifiers", "dynamic_modifier"), ("decisions", "active_decision")):
        for path in sorted((game / "common" / folder).glob("*.txt")):
            relative = path.relative_to(game).as_posix()
            text = path.read_text(encoding="utf-8-sig")
            source_files[relative] = {"sha256": digest(path)}
            try:
                tree = parse_script(text, relative)
            except ParseError as error:
                parse_failures.append({"file": relative, "reason": str(error)})
                possible_failed_ids.update(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=\s*\{", text))
                continue
            if source_type == "dynamic_modifier":
                definitions.extend((source_type, entry, relative) for entry in tree if isinstance(entry.value, list))
            else:
                definitions.extend((source_type, entry, relative) for category in tree
                                   if isinstance(category.value, list) for entry in category.value
                                   if isinstance(entry.value, list))

    targeted, addition_files, addition_parse_failures, unresolved_additions, dynamic_usages = find_targeted_dynamic_additions(game)
    source_files.update(addition_files)
    # The accepted dynamic labels use these exact native defined_text functions.
    # Record and verify their defining files rather than guessing a translation.
    for function_name, relative in NATIVE_DYNAMIC_NAME_FUNCTIONS.items():
        path = game / relative
        text = path.read_text(encoding="utf-8-sig")
        assert re.search(r"\bname\s*=\s*" + re.escape(function_name) + r"\b", text), function_name
        source_files[relative] = {"sha256": digest(path)}
    counts = Counter((kind, entry.key) for kind, entry, _ in definitions)
    accepted = Counter()
    accepted_ids = set()

    def reject(kind, definition, path, reason, modifier=None, line=None, **extra):
        item = {"source_id": definition.key, "source_type": kind, "source_file": path,
                "source_line": line or definition.line, "reason": reason}
        if modifier is not None:
            item["modifier"] = modifier
        item.update(extra)
        excluded.append(item)

    for kind, definition, path in definitions:
        source_id = definition.key
        enable_script = None
        enable_evaluation = "absent_enabled"
        if kind == "active_decision" and not fields(definition.value, "modifier"):
            continue  # Still counted for duplicate-ID detection above.
        if not TOKEN_ID.fullmatch(source_id or ""):
            reject(kind, definition, path, "unsupported_identifier")
            continue
        if counts[kind, source_id] != 1 or source_id in possible_failed_ids:
            reject(kind, definition, path, "duplicate_or_unverifiable_source_definition")
            continue
        if kind == "dynamic_modifier":
            if unresolved_additions:
                reject(kind, definition, path, "unknown_parameterized_addition_scope")
                continue
            if source_id in targeted:
                reject(kind, definition, path, "targeted_instances_cannot_be_counted", addition_sites=targeted[source_id])
                continue
            usages = dynamic_usages.get(source_id, [])
            if usages and all(site["lexical_scope"] in {"state", "character"} for site in usages):
                reject(kind, definition, path, "only_non_country_additions", addition_sites=usages)
                continue
            enables = fields(definition.value, "enable")
            if len(enables) > 1 or (enables and not isinstance(enables[0].value, list)):
                reject(kind, definition, path, "ambiguous_enable_definition")
                continue
            if enables:
                enable_script = render_native_trigger(enables[0].value)
                # All supported national definitions can evaluate these clauses
                # in the same current-country context. Alternate runtime scopes
                # need additional provenance and remain excluded.
                if re.search(r"\b(?:FROM(?:FROM)*|PREV(?:PREV)*|THIS|this)\b", enable_script):
                    reject(kind, definition, path, "unsupported_enable_context")
                    continue
                enable_evaluation = "always_yes" if always_yes(enables[0].value) else "current_native_enable"
            if any(entry.key not in DYNAMIC_CONTROL_FIELDS and isinstance(entry.value, list)
                   for entry in definition.value):
                # Nested modifier definitions are not a documented direct
                # scalar dynamic modifier. Do not reinterpret them.
                reject(kind, definition, path, "nested_or_unknown_dynamic_definition")
                continue
            modifiers = definition.value
            activation = f"has_dynamic_modifier = {source_id}"
            if enables:
                activation = f"AND = {{ has_dynamic_modifier = {source_id} {enable_script} }}"
        else:
            target_fields = sorted({entry.key for entry in definition.value} & DECISION_TARGET_FIELDS)
            if target_fields:
                reject(kind, definition, path, "targeted_decision_instance_count_unknown", fields=target_fields)
                continue
            unsafe = sorted({entry.key for entry in definition.value} & DECISION_UNSAFE_FIELDS)
            if unsafe:
                reject(kind, definition, path, "conditional_decision_modifier_not_adapted", fields=unsafe)
                continue
            blocks = fields(definition.value, "modifier")
            if len(blocks) != 1 or not isinstance(blocks[0].value, list):
                reject(kind, definition, path, "ambiguous_direct_modifier_block")
                continue
            modifiers = blocks[0].value
            activation = f"has_decision = {source_id}"

        source_name = fields(definition.value, "name")
        if len(source_name) > 1:
            reject(kind, definition, path, "ambiguous_source_name")
            continue
        name_key = source_name[0].value if source_name else source_id
        if not isinstance(name_key, str) or not TOKEN_ID.fullmatch(name_key):
            reject(kind, definition, path, "dynamic_or_nontoken_source_name")
            continue
        chinese = {entry["text"] for entry in names["simp_chinese"].get(name_key, []) if entry["text"].strip()}
        if len(chinese) != 1:
            reject(kind, definition, path, "missing_or_ambiguous_chinese_name", name_loc_key=name_key)
            continue
        try:
            display = source_display_names(names, name_key, allow_dynamic=kind == "dynamic_modifier")
        except ValueError as error:
            reject(kind, definition, path, "source_name_not_static_single_line",
                   name_loc_key=name_key, detail=str(error))
            continue

        key_counts = Counter(entry.key for entry in modifiers)
        for entry in modifiers:
            if entry.key not in selected:
                continue
            if key_counts[entry.key] != 1:
                reject(kind, definition, path, "duplicate_modifier_key", entry.key, entry.line)
                continue
            value = number(entry.value)
            if value is None:
                reason = "dynamic_variable_cached_contribution_not_exposed" if kind == "dynamic_modifier" else "nonliteral_decision_modifier"
                reject(kind, definition, path, reason, entry.key, entry.line,
                       value_expression=str(entry.value), activation_script=activation,
                       enable_script=enable_script, enable_evaluation=enable_evaluation)
                continue
            if value == 0:
                reject(kind, definition, path, "zero_value_not_displayed", entry.key, entry.line)
                continue
            row = {
                "id": f"{kind}:{source_id}:{entry.key}", "source_id": source_id,
                "source_type": kind, "source_category": kind, "name_loc_key": name_key,
                "name_zh": next(iter(chinese)),
                **display,
                "value": int(value) if value == value.to_integral_value() else float(value),
                "value_literal": canonical(value), "activation_script": activation,
                "enable_script": enable_script, "enable_evaluation": enable_evaluation,
                "source": {"file": path, "line": entry.line, "definition_line": definition.line,
                           "sha256": source_files[path]["sha256"]},
                "runtime_validated": False,
            }
            by_modifier[entry.key].append(row)
            accepted[kind] += 1
            accepted_ids.add((kind, source_id))

    for values in by_modifier.values():
        values.sort(key=lambda row: (row["source_type"], row["source_id"].casefold(), row["source"]["line"]))
    return {
        "schema_version": 1, "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "scope": "current_country_literal_dynamic_modifiers_and_non_targeted_active_decisions",
        "assumptions": [
            "Scanned vanilla definitions must be the definitions loaded by the game.",
            "Activation is evaluated in the current player COUNTRY, never in a state, unit, or target scope.",
            "has_decision requires an active selected decision; visibility, availability and completion are not substituted for active status.",
            "Only the decision's direct modifier block is included; complete/remove effects granting ideas or dynamic modifiers are represented by their actual carrier only.",
            "Targeted decisions and dynamic modifiers added with scope are omitted because a Boolean trigger cannot count multiple active instances.",
            "Dynamic modifiers are updated daily; current native enable conditions may briefly precede the cached applied total. No cache refresh is forced.",
            "Variable entries are handed to the companion live-input adapter; they are not emitted as literal values by this table.",
            "For dynamic remove_trigger, the engine's actual ownership remains authoritative until it removes the modifier; no predicted removal is substituted.",
            "No historical decision/focus provenance is inferred; shared grants are not duplicated or attributed to an unverified origin.",
            "Chinese and English labels resolve static native aliases or audited country-context native dynamic names; missing and ambiguous labels are omitted. Static name newlines are folded into spaces.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False,
                           "other_sources_row": False, "unknown_source_labels": False},
        "statistics": {
            "selected_modifier_count": len(selected),
            "covered_modifier_count": sum(bool(values) for values in by_modifier.values()),
            "binding_count": sum(map(len, by_modifier.values())),
            "binding_count_by_type": dict(sorted(accepted.items())),
            "source_count_by_type": dict(sorted(Counter(kind for kind, _ in accepted_ids).items())),
            "scanned_definition_count": len(definitions),
            "source_file_count": len(source_files),
            "definition_parse_failure_count": len(parse_failures),
            "addition_parse_failure_count": len(addition_parse_failures),
            "unresolved_addition_count": len(unresolved_additions),
            "excluded_by_reason": dict(sorted(Counter(row["reason"] for row in excluded).items())),
        },
        "evidence": [
            {"file": "common/dynamic_modifiers/0_dynamic_modifiers.txt", "line": 6,
             "claim": "Optional enable disables the contribution when false."},
            {"file": "common/dynamic_modifiers/0_dynamic_modifiers.txt", "line": 27,
             "claim": "Dynamic modifiers update daily unless force_update_dynamic_modifier is used; this adapter never uses it."},
            {"file": "documentation/triggers_documentation.md", "line": 3693,
             "claim": "has_decision checks a country active selected decision."},
            {"file": "documentation/triggers_documentation.md", "line": 3775,
             "claim": "has_dynamic_modifier supports country scope; a targeted instance may specify scope."},
        ],
        "source_files": source_files, "by_modifier": by_modifier,
        "dynamic_addition_scope_audit": dynamic_usages,
        "parse_failures": parse_failures, "addition_parse_failures": addition_parse_failures,
        "unresolved_additions": unresolved_additions, "excluded": excluded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/dynamic-source-bindings.json")
    args = parser.parse_args()
    data = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
