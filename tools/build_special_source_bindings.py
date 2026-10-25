#!/usr/bin/env python3
"""Build country-status sources and preserve unavailable landmark audit data.

Three engine probes disproved the available landmark health predicates.
Landmarks are retained solely as audit candidates, never production sources.
State modifiers, unknown engine state and residuals are never attributed.
The native stability/war-support curves retain exact definition provenance.
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
from validate_mod import ParseError, parse_script
from build_source_bindings import DEFAULT_GAME, ROOT, TOKEN_ID, digest, localizations, number
from build_dynamic_source_bindings import source_display_names


STATUS_CURVES = {
    "stability_good_modifier": ("stability", "has_stability", "good"),
    "stability_bad_modifier": ("stability", "has_stability", "bad"),
    "war_support_good_modifier": ("war_support", "has_war_support", "good"),
    "war_support_bad_modifier": ("war_support", "has_war_support", "bad"),
}


def field(block, key, default=None):
    matches = [node for node in block if node.key == key]
    if len(matches) > 1:
        raise ValueError("duplicate_" + key)
    return matches[0].value if matches else default


def render(value):
    if isinstance(value, list):
        return "{ " + " ".join(
            (str(node.key) + " " + str(node.op) + " " if node.key is not None else "")
            + render(node.value) for node in value) + " }"
    text = str(value)
    return json.dumps(text, ensure_ascii=False) if re.search(r"[\s{}#\"]", text) else text


def landmark_plan(node):
    """Preserve the rejected third-probe candidate; never use it in production.

    Provincial control can differ from state control; requiring full control
    prevents attributing an enemy-held landmark to the state's controller.
    Native landmark counts cannot reveal damage. The broad country predicate
    The third probe disproved has_damaged_buildings = no as a health guard:
    it remains true for a damaged provincial landmark. This candidate is
    deliberately retained only to document the failed approach. Production
    selection is fail-closed in add(): every landmark goes to audit data.
    """
    block = node.value
    if not isinstance(block, list) or not TOKEN_ID.fullmatch(node.key or ""):
        raise ValueError("unsupported_building_definition")
    cap = field(block, "level_cap", [])
    if not isinstance(cap, list) or field(cap, "province_max") != "1":
        raise ValueError("unsupported_building_level_cap")
    country = field(block, "country_modifiers")
    if not isinstance(country, list):
        raise ValueError("missing_country_modifiers")
    if any(e.key not in {"enable_for_controllers", "modifiers"} for e in country):
        raise ValueError("unadapted_country_modifier_condition")
    allowed = field(country, "enable_for_controllers", [])
    if not isinstance(allowed, list) or any(
            e.key is not None or not re.fullmatch(r"[A-Z]{3}", str(e.value)) for e in allowed):
        raise ValueError("unadapted_controller_list")
    controllers = [e.value for e in allowed]
    dlc = field(block, "dlc_allowed", [])
    if not isinstance(dlc, list) or any(e.key != "has_dlc" or isinstance(e.value, list) for e in dlc):
        raise ValueError("unadapted_dlc_condition")
    clauses = [f"has_dlc = {render(e.value)}" for e in dlc]
    if controllers:
        clauses.append("OR = { " + " ".join(f"tag = {tag}" for tag in controllers) + " }")
    key = node.key
    # The building-count trigger accepts comparison tokens (> / <), not '='.
    # Native STATE non_damaged_building_level rejects provincial landmarks.
    # Country/state/province count predicates include damaged copies. Never
    # mistake a count of one, or a zero dynamic query, for a health reading.
    clauses += ["has_damaged_buildings = no", f"{key} > 0", f"{key} < 2",
                "any_controlled_state = { is_fully_controlled_by = ROOT "
                f"{key} > 0 }}"]
    return {"activation_script": "AND = { " + " ".join(clauses) + " }",
            "controllers": controllers, "dlcs": [e.value for e in dlc],
            "modifiers": field(country, "modifiers", []),
            "eligibility": "one_building_in_a_fully_controlled_state_and_no_damaged_buildings_anywhere_in_country"}


def status_plan(source_id, value):
    variable, trigger, band = STATUS_CURVES[source_id]
    coefficient = Decimal(2) * value * (1 if band == "good" else -1)
    offset = -value if band == "good" else value
    return {"activation_script": f"AND = {{ {trigger} {'>' if band == 'good' else '<'} 0.5 }}",
            "value_kind": "runtime",
            "value_expression": {"variable": "ROOT." + trigger,
                                 "coefficient": format(coefficient, "f"),
                                 "offset": format(offset, "f")}}


def build(game, index_path):
    selected = {r["key"] for r in json.loads(index_path.read_text(encoding="utf-8"))["records"]}
    names = localizations(game)
    by_modifier = {key: [] for key in sorted(selected)}
    files, failures, excluded, accepted = {}, [], [], set()
    unavailable_landmark_candidates = []
    definitions = []
    for path in sorted((game / "common/buildings").glob("*.txt")):
        relative = path.relative_to(game).as_posix()
        files[relative] = {"sha256": digest(path)}
        try:
            for outer in parse_script(path.read_text(encoding="utf-8-sig"), relative):
                if outer.key == "buildings" and isinstance(outer.value, list):
                    definitions.extend((n, relative) for n in outer.value
                                       if isinstance(n.value, list) and n.key and n.key.startswith("landmark_"))
        except ParseError as error:
            failures.append({"file": relative, "reason": str(error)})
    counts = Counter(node.key for node, _ in definitions)

    def reject(source, path, reason, key=None, line=None):
        excluded.append({"source_id": source.key, "source_file": path,
                         "source_line": line or source.line, "modifier": key, "reason": reason})

    def add(node, path, entry, plan, kind):
        key, value = entry.key, number(entry.value)
        if key not in selected:
            reject(node, path, "modifier_not_in_registry", key, entry.line)
            return
        if value is None or value == 0:
            reject(node, path, "nonliteral_or_zero_value", key, entry.line)
            return
        try:
            display = source_display_names(names, node.key)
        except ValueError as error:
            reject(node, path, str(error), key, entry.line)
            return
        if kind == "country_status_curve":
            plan = status_plan(node.key, value)
        parse_script(plan["activation_script"])
        row = {"id": f"special:{node.key}:{key}", "source_id": node.key,
               "source_type": kind, "source_category": kind,
               "name_loc_key": node.key, "value": float(value),
               "value_literal": format(value, "f"),
               "activation_script": plan["activation_script"], **display,
               "source": {"file": path, "line": entry.line, "definition_line": node.line,
                          "sha256": files[path]["sha256"],
                          "block_path": "country_modifiers/modifiers" if kind == "landmark" else "static_modifier"},
               "runtime_validated": False}
        for name in ("value_kind", "value_expression", "controllers", "dlcs", "eligibility"):
            if name in plan:
                row[name] = plan[name]
        if kind == "landmark":
            # The public predicates tested in three engine runs cannot
            # distinguish an intact provincial landmark from a damaged one.
            # Its nominal value must never leak into the display source map.
            row["production_eligible"] = False
            row["candidate_status"] = "rejected_by_three_native_engine_health_probes"
            row["exclusion_reason"] = "provincial_landmark_health_unverifiable_with_tested_documented_queries"
            unavailable_landmark_candidates.append(row)
            reject(node, path, row["exclusion_reason"], key, entry.line)
            return
        by_modifier[key].append(row)
        accepted.add(node.key)

    for node, path in definitions:
        if counts[node.key] != 1:
            reject(node, path, "duplicate_definition")
            continue
        try:
            plan = landmark_plan(node)
        except ValueError as error:
            reject(node, path, str(error))
            continue
        entries = plan["modifiers"]
        if not isinstance(entries, list):
            reject(node, path, "invalid_country_modifiers")
            continue
        key_counts = Counter(e.key for e in entries)
        for entry in entries:
            if key_counts[entry.key] != 1:
                reject(node, path, "duplicate_modifier_key", entry.key, entry.line)
            else:
                add(node, path, entry, plan, "landmark")
    static_path = game / "common/modifiers/00_static_modifiers.txt"
    relative = static_path.relative_to(game).as_posix()
    files[relative] = {"sha256": digest(static_path)}
    static = parse_script(static_path.read_text(encoding="utf-8-sig"), relative)
    static_counts = Counter(n.key for n in static)
    for node in static:
        if node.key not in STATUS_CURVES and node.key != "country_is_at_peace":
            continue
        if static_counts[node.key] != 1:
            reject(node, relative, "duplicate_definition")
            continue
        kind = "country_status_curve" if node.key in STATUS_CURVES else "country_peace_status"
        for entry in node.value:
            add(node, relative, entry, {"activation_script": "AND = { has_war = no }"}, kind)
    for values in by_modifier.values():
        values.sort(key=lambda r: (r["source_type"], r["source_id"]))
    return {
        "schema_version": 1, "game_root": str(game),
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "scope": "country_status_sources_and_audited_unavailable_landmarks",
        "assumptions": [
            "Scanned vanilla definitions must match the currently loaded game.",
            "NO LANDMARK CANDIDATE IS A PRODUCTION SOURCE: all 26 native country-modifier bindings are retained only as unavailable audit candidates.",
            "Native national totals still include the engine's true landmark effects; this adapter does not add, subtract, or replace totals.",
            "Only landmark country_modifiers were audited; no state or unit modifier is counted.",
            "Three engine probes found provincial landmark dynamic level queries return zero, STATE non_damaged_building_level rejects landmarks, native counts retain damaged copies, and COUNTRY has_damaged_buildings misses damaged provincial landmarks.",
            "A damaged landmark can pass every tested candidate predicate while its true national effect is zero; no candidate activation is emitted into by_modifier.",
            "Country-status curves read the documented native has_stability/has_war_support numeric queries; inputs use the 0..1 range, never a cached substitute or source sum.",
            "Runtime_validated is false at generation; deployment requires corresponding engine probes.",
            "No dedicated current-state query for pride of the fleet or coastal protection was found in the shipped public documentation; no attribution is inferred from totals or fleet existence."],
        "display_policy": {"zero_sources": False, "unresolved_residual": False,
                           "other_sources_row": False, "source_type_prefix": False,
                           "one_line_per_source": True},
        "statistics": {"selected_modifier_count": len(selected),
                       "covered_modifier_count": sum(bool(v) for v in by_modifier.values()),
                       "binding_count": sum(map(len, by_modifier.values())),
                       "source_count": len(accepted),
                       "landmark_definition_count": len(definitions),
                       "landmark_binding_count": sum(r["source_type"] == "landmark" for v in by_modifier.values() for r in v),
                       "unavailable_landmark_binding_count": len(unavailable_landmark_candidates),
                       "unavailable_landmark_source_count": len({r["source_id"] for r in unavailable_landmark_candidates}),
                       "status_binding_count": sum(r["source_type"] != "landmark" for v in by_modifier.values() for r in v),
                       "parse_failure_count": len(failures),
                       "excluded_by_reason": dict(sorted(Counter(x["reason"] for x in excluded).items()))},
        "evidence": [
            {"file": "common/buildings/01_landmark_buildings.txt", "line": 12,
             "claim": "country_modifiers are enabled for the actual controller, separately from state_modifiers."},
            {"file": "documentation/triggers_documentation.md", "line": 1830,
             "claim": "Building count triggers support COUNTRY and STATE scope, including all native landmarks."},
            {"file": "common/scripted_localisation/SEA_CHI_scripted_loc.txt", "line": 350,
             "claim": "Vanilla scripted localisation itself tests landmark_tokyo_imperial_palace > 0 in state scope; lines367/384 likewise test National Diet and Hakko Ichiu."},
            {"file": "documentation/dynamic_variables_documentation.md", "line": 1101,
             "claim": "STATE scope documents building level numeric queries, but the first engine probe found zero for provincial landmarks; those queries are not used for landmark attribution."},
            {"file": "documentation/triggers_documentation.md", "line": 6554,
             "claim": "The STATE non_damaged_building_level trigger is documented for state buildings; the second engine probe rejected provincial landmarks, so the adapter does not use it."},
            {"file": "documentation/triggers_documentation.md", "line": 3684,
             "claim": "has_damaged_buildings is a COUNTRY predicate, but the third engine probe found it does not detect damaged provincial landmarks; it cannot establish landmark health."},
            {"file": "documentation/dynamic_variables_documentation.md", "line": 435,
             "claim": "COUNTRY numeric queries has_stability and has_war_support are auto-generated from the native triggers; their documented range is 0..1."},
            {"file": "documentation/triggers_documentation.md", "line": 5024,
             "claim": "has_war is the COUNTRY-scope predicate for whether the country is at war; no means peace."},
            {"file": "common/defines/00_defines.lua", "line": 350,
             "claim": "MIN_STABILITY/MAX_STABILITY and MIN_WAR_SUPPORT/MAX_WAR_SUPPORT define the native 0..1 bounds."},
            {"file": "documentation/triggers_documentation.md", "line": 2145,
             "claim": "clamp_temp_variable is permitted in triggers; effect documentation line2681 specifies var/min/max syntax."},
            {"file": relative, "line": 326,
             "claim": "Native stability curves are split at 50%; their literal endpoint effects are in the static definitions."}],
        "unavailable_sources": [
            {"source_id": "pride_of_the_fleet_country", "modifier": "war_support_factor", "native_value": "0.05",
             "reason": "dedicated_current_country_pride_of_fleet_query_not_found_in_shipped_public_docs", "source": {"file": relative, "line": 523}},
            {"source_id": "pride_of_the_fleet_sunk_temporary", "modifier": "war_support_factor", "native_value": "-0.10",
             "reason": "dedicated_current_country_sunk_pride_timer_query_not_found_in_shipped_public_docs", "source": {"file": relative, "line": 527}},
            {"source_id": "coastal_core_state_protection", "modifier": "stability_factor", "native_maximum": "0.1",
             "reason": "dedicated_live_coastal_protection_ratio_query_not_found_in_shipped_public_docs", "source": {"file": "common/defines/00_defines.lua", "line": 343}},
            {"source_id": "war_support_during_war", "modifier": "stability_factor",
             "reason": "wartime_curve_not_yet_engine_verified", "source": {"file": relative, "line": 356}}],
        "engine_probe_spec": {
            "status_sample_points": [0, 0.25, 0.5, 0.75, 1],
            "landmark": {"country": "GER", "state": 64, "province": 6521,
                         "building": "landmark_berlin_reichstag", "modifier": "stability_factor",
                         "nominal_value": 0.05,
                         "cases": ["intact", "partial_damage", "full_damage", "repaired", "foreign_controller", "multiple_copies", "unrelated_building_damaged_hides_landmark_source"]}},
        "engine_probe_observations": [{
            "probe": "first_native_reichstag_lifecycle",
            "country": "GER", "state": 64, "province": 6521,
            "building": "landmark_berlin_reichstag", "modifier": "stability_factor",
            "observed_native_totals": {"intact": "0.05", "partial_damage_0.5": "0",
                                       "full_damage": "0", "repaired": "0.05",
                                       "removed": "0", "restored": "0.05"},
            "observation": "Any tested damage disabled the full 0.05 national effect; no proportional 0.025 effect was observed.",
            "rejected_query": "STATE building_level@ / damaged_building_level@ / non_damaged_building_level@ all returned zero for this provincial building.",
            "rejected_comparator": "Native building count trigger rejected '=' as Not valid compare token.",
            "candidate_verification": "The second engine probe rejected the non_damaged_building_level predicate for provincial landmarks; see the later observation."}, {
            "probe": "second_native_reichstag_health_predicates",
            "country": "GER", "state": 64, "province": 6521,
            "building": "landmark_berlin_reichstag",
            "observation": "Native country/state/province building counts stay one while intact, partly damaged, and fully damaged; they become zero only after removal.",
            "rejected_predicate": "STATE non_damaged_building_level rejected the provincial landmark with Not a valid state building: building.",
            "candidate_verification": "The COUNTRY has_damaged_buildings fallback was subsequently disproved by the third engine probe."}, {
            "probe": "third_native_reichstag_country_damage_guard",
            "country": "GER", "state": 64, "province": 6521,
            "building": "landmark_berlin_reichstag", "modifier": "stability_factor",
            "observation": "has_damaged_buildings = no remained true for partly and fully damaged landmarks while their native national contribution was zero; it became false only when an unrelated factory was damaged.",
            "rejected_predicate": "COUNTRY has_damaged_buildings = no cannot prove a provincial landmark is intact.",
            "production_action": "All 26 landmark bindings are removed from by_modifier and retained only in unavailable_landmark_candidates; no residual or guessed substitute is displayed."}],
        "unavailable_landmark_candidates": unavailable_landmark_candidates,
        "source_files": files, "by_modifier": by_modifier, "parse_failures": failures, "excluded": excluded,
        "uncovered_modifier_keys": [key for key, rows in by_modifier.items() if not rows]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/special-source-bindings.json")
    args = parser.parse_args()
    result = build(args.game_root, args.index)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
