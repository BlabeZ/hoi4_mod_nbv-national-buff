#!/usr/bin/env python3
"""Read the vanilla input variables of currently held national dynamic modifiers.

These are live inputs, not an exported per-source engine cache. HOI4 applies
dynamic modifier values daily; a same-day input change can therefore precede
the total's next native refresh. This adapter never forces that refresh, writes
gameplay variables, infers a residual, or treats a coefficient as a live value.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from build_dynamic_source_bindings import build as build_literal_audit
from build_dynamic_source_bindings import fields, source_display_names
from build_source_bindings import DEFAULT_GAME, ROOT, digest, localizations
from validate_mod import parse_script


PLAIN_VARIABLE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
EXPLICIT_VARIABLE = re.compile(r"(?:ROOT|global|[A-Z]{3})\.[A-Za-z_][A-Za-z_0-9]*")


def root_expression(native):
    """Only documented scalar country/global references; no computed syntax."""
    if PLAIN_VARIABLE.fullmatch(native):
        return "ROOT." + native
    if EXPLICIT_VARIABLE.fullmatch(native):
        return native
    return None


def build(game: Path, index_path: Path):
    # Reuse the conservative adapter's current, fully rescanned audit. Its
    # variable exclusions have already passed ID, localisation, national-scope,
    # addition-site, duplicate-key, and current-native-enable validation. This
    # prevents accidentally reintroducing a targeted/state/conditional source
    # merely because it happens to use a variable rather than a literal.
    audited = build_literal_audit(game, index_path)
    candidates = [row for row in audited["excluded"]
                  if row["reason"] == "dynamic_variable_cached_contribution_not_exposed"]
    names = localizations(game)
    by_modifier = {key: [] for key in audited["by_modifier"]}
    trees, definitions = {}, {}
    excluded = []
    for candidate in candidates:
        relative = candidate["source_file"]
        source_id = candidate["source_id"]
        if relative not in trees:
            trees[relative] = parse_script((game / relative).read_text(encoding="utf-8-sig"), relative)
            definitions[relative] = {node.key: node for node in trees[relative] if isinstance(node.value, list)}
        definition = definitions[relative][source_id]
        native = candidate["value_expression"]
        expression = root_expression(native)
        if expression is None:
            excluded.append(dict(candidate, reason="unsupported_runtime_variable_expression"))
            continue
        source_name = fields(definition.value, "name")
        name_key = source_name[0].value if source_name else source_id
        display = source_display_names(names, name_key, allow_dynamic=True)
        # Preserve one compound node: grouped OR gates must never turn these
        # required clauses into independent alternatives.
        activation = (f"AND = {{ {candidate['activation_script']} "
                      f"NOT = {{ check_variable = {{ {expression} = 0 }} }} }}")
        row = {
            "id": f"dynamic_modifier_variable:{source_id}:{candidate['modifier']}",
            "source_id": source_id,
            "source_type": "dynamic_modifier_variable",
            "source_category": "dynamic_modifier_variable",
            "name_loc_key": name_key,
            "name_zh": next(iter({row['text'] for row in names['simp_chinese'][name_key] if row['text'].strip()})),
            **display,
            "value_kind": "runtime",
            # The two literal fields are coefficients for a source definition,
            # not values currently contributing in any country's save.
            "value": 1,
            "value_literal": "1",
            "value_expression": {"variable": expression, "coefficient": "1", "offset": "0"},
            "input_variable": native,
            "value_read_semantics": "current_native_dynamic_modifier_input",
            "cached_contribution_read": False,
            "activation_script": activation,
            "enable_evaluation": candidate['enable_evaluation'],
            "enable_script": candidate['enable_script'],
            "source": {
                "file": relative,
                "line": candidate["source_line"],
                "definition_line": definition.line,
                "sha256": audited["source_files"][relative]["sha256"],
            },
            "runtime_validated": False,
        }
        by_modifier[candidate["modifier"]].append(row)

    for rows in by_modifier.values():
        rows.sort(key=lambda row: (row["source_id"].casefold(), row["source"]["line"]))
    all_rows = [row for rows in by_modifier.values() for row in rows]
    identity = {(key, row["source_id"]) for key, rows in by_modifier.items() for row in rows}
    literal_identity = {(key, row["source_id"]) for key, rows in audited["by_modifier"].items()
                        for row in rows if row["source_type"] == "dynamic_modifier"}
    assert not identity & literal_identity, "runtime adapter must not duplicate fixed dynamic bindings"
    for key, variable in (("army_org_factor", "GER_military_army_org_factor"),
                          ("planning_speed", "GER_military_planning_speed"),
                          ("supply_consumption_factor", "GER_military_supply_consumption_factor")):
        matches = [row for row in by_modifier[key] if row["source_id"] == "GER_army_modifier"]
        assert len(matches) == 1 and matches[0]["input_variable"] == variable, (key, matches)
    return {
        "schema_version": 2,
        "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "scope": "current_country_held_dynamic_modifiers_live_native_inputs",
        "assumptions": [
            "Vanilla definitions and variables are those actually loaded in the game.",
            "Only COUNTRY has_dynamic_modifier ownership authorizes a source; state and character instances are not traversed.",
            "Only direct scalar native variable references are read; no residual is reconstructed or attributed.",
            "Source values are current native inputs, not independently exported cached contributions; same-day changes can precede the next daily total refresh.",
            "No force_update_dynamic_modifier call or gameplay-variable write is generated.",
            "Current native enable clauses are evaluated in country context; the same daily cache boundary applies to enable changes and value changes.",
            "Native dynamic source names retain audited country-context localisation functions; missing or ambiguous names remain omitted.",
            "All targeted/alternate-scope additions and ambiguous definitions are omitted under the existing national dynamic scope audit.",
            "Current zero inputs return no source row; unowned modifiers return no source row.",
            "value and value_literal contain the input coefficient, never a purported current contribution.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False,
                           "other_sources_row": False, "unknown_source_labels": False},
        "statistics": {
            "selected_modifier_count": len(by_modifier),
            "covered_modifier_count": sum(bool(rows) for rows in by_modifier.values()),
            "binding_count": len(all_rows),
            "source_count": len({row["source_id"] for row in all_rows}),
            "variable_count": len({row["input_variable"] for row in all_rows}),
            "binding_count_by_type": {"dynamic_modifier_variable": len(all_rows)},
            "source_count_by_type": {"dynamic_modifier_variable": len({row["source_id"] for row in all_rows})},
            "variable_reference_count_by_scope": dict(sorted(Counter(
                "current_country" if row["value_expression"]["variable"].startswith("ROOT.")
                else "global" if row["value_expression"]["variable"].startswith("global.")
                else "explicit_country" for row in all_rows).items())),
            "excluded_by_reason": dict(sorted(Counter(row["reason"] for row in excluded).items())),
            "fixed_binding_overlap_count": len(identity & literal_identity),
        },
        "evidence": [
            {"file": "common/dynamic_modifiers/0_dynamic_modifiers.txt", "line": 27,
             "claim": "Dynamic modifiers update daily; this adapter reads inputs without forcing an update."},
            {"file": "common/dynamic_modifiers/wuw_dynamic_modifiers.txt", "line": 592,
             "claim": "GER_army_modifier binds organisation, planning speed and supply consumption to country variables."},
            {"file": "history/countries/GER - Germany.txt", "line": 262,
             "claim": "1936 Germany initializes these three variables to 0.05, 0.25 and 0.15 before adding GER_army_modifier."},
        ],
        "source_files": audited["source_files"],
        "by_modifier": by_modifier,
        "inherited_scope_audit_statistics": audited["statistics"],
        "excluded": excluded,
        "engine_probes": [
            {"source_id": "GER_army_modifier", "key": "supply_consumption_factor",
             "input_variable": "GER_military_supply_consumption_factor", "initial_value": "0.15",
             "name_contains": "德意志国防军",
             "checks": ["owned_and_nonzero_visible", "input_value_change_reflected", "zero_hidden",
                        "unowned_hidden", "input_read_does_not_force_total_refresh"]},
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/dynamic-spirit-source-bindings.json")
    args = parser.parse_args()
    data = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
