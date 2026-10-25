"""Native idea/status sources and unavailable landmark regression probes.

The source catalogue supplies lookup indices; expected native contributions are
checked against independent fixtures below. No production file or game profile
is modified by this module. Each country event establishes its own real ROOT.
"""
from collections import defaultdict
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT.parent / "nbv-test-workspace/smoke-addon"
SOV_IDEAS = {
    "trotskyite_plot_nsb": {"stability_factor": -.2, "political_power_factor": -.15},
    "SOV_politicized_military": {
        "command_abilities_cost_factor": .1, "land_doctrine_cost_factor": .2,
        "naval_doctrine_cost_factor": .2, "air_doctrine_cost_factor": .2,
        "drift_defence_factor": .1, "army_core_defence_factor": .03,
    },
}
CURVES = {
    "stability_bad_modifier": {"industrial_capacity_factory": -.5, "industrial_capacity_dockyard": -.5,
                               "political_power_factor": -.2},
    "stability_good_modifier": {"industrial_capacity_factory": .2, "industrial_capacity_dockyard": .2,
                                "consumer_goods_factor": -.2, "political_power_factor": .1},
    "war_support_bad_modifier": {"mobilization_speed": -.5, "command_power_gain_mult": -.95,
                                 "surrender_limit": -.3},
    "war_support_good_modifier": {"mobilization_speed": .3, "army_core_attack_factor": .1,
                                  "army_core_defence_factor": .1, "command_power_gain_mult": .5},
}
POINTS = (("neutral", .5), ("p000", 0), ("p025", .25), ("p050", .5), ("p075", .75), ("p100", 1))
LANDMARK = "landmark_berlin_reichstag"
LANDMARK_NAME = "帝国议会"
LANDMARK_PHASES = ("native", "partial_damage", "full_damage", "repaired", "removed", "restored",
                   "unrelated_factory_damage", "factory_repaired")
BUILDING_DIAGNOSTICS = (
    ("country_gt0", False, f"{LANDMARK} > 0"),
    ("country_lt2", False, f"{LANDMARK} < 2"),
    ("state_gt0", True, f"{LANDMARK} > 0"),
    ("state_lt2", True, f"{LANDMARK} < 2"),
    ("country_damage_free", False, "NOT = { has_damaged_buildings = yes }"),
    ("province_gt0", True, f"any_province_building_level = {{ province = {{ id = 6521 }} building = {LANDMARK} level > 0 }}"),
    ("province_lt2", True, f"any_province_building_level = {{ province = {{ id = 6521 }} building = {LANDMARK} level < 2 }}"),
)
NUMBER = r"[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+\-]?\d+)?"


def _entries():
    manifest = json.loads((ROOT / "tools/data/source-display-manifest.json").read_text(encoding="utf-8"))
    by_pair = defaultdict(list)
    for row in manifest["records"]:
        by_pair[row["source_id"], row["key"]].append(row)
    tables = {}
    for filename in ("source-bindings.json", "special-source-bindings.json"):
        table = json.loads((ROOT / "tools/data" / filename).read_text(encoding="utf-8"))
        for key, rows in table["by_modifier"].items():
            for row in rows:
                tables[row["source_id"], key] = row
    required = [(source, key, value) for source, keys in {**SOV_IDEAS, **CURVES}.items()
                for key, value in keys.items()]
    required += [("country_is_at_peace", "decryption_power_factor", -.5)]
    result = {}
    for source, key, value in required:
        matches = by_pair[source, key]
        assert len(matches) == 1, ("Missing or duplicate special-source probe binding", source, key, len(matches))
        row = {**tables[source, key], **matches[0]}
        assert abs(float(row["value_literal"]) - value) < 1e-8, (source, key, row["value_literal"])
        result[source, key] = row
    return result


def _landmark_metric():
    registry = json.loads((ROOT / "tools/data/metric-index.json").read_text(encoding="utf-8"))["records"]
    row = next(row for row in registry if row["key"] == "stability_factor")
    assert row["id"] == 5, "The omitted-source probe uses the stable stability metric ID."
    return row


def _sample(row, kind, phase, guard):
    prefix = f'kind={kind} index={row["index"]} phase={phase}'
    return [
        "set_temp_variable = { nbv_special_active = 0 }",
        f'if = {{ limit = {{ {guard} }} set_temp_variable = {{ nbv_special_active = 1 }} }}',
        f'log = "NBV_SPECIAL_VALUE {prefix} country=[ROOT.GetTag] active=[?nbv_special_active|0] '
        f'total=[?ROOT.modifier@{row["key"]}|6] stability=[?ROOT.has_stability|6] '
        f'war_support=[?ROOT.has_war_support|6] END_SPECIAL_VALUE"',
        f'log = "NBV_SPECIAL_TEXT {prefix} text=[NBVSource{row["index"]}] END_SPECIAL_TEXT"',
        f'set_temp_variable = {{ nbv_entry_id = {row["metric_id"]} }}',
        f'log = "NBV_SPECIAL_ROW {prefix} text=[NBVRowValue] END_SPECIAL_ROW"',
        f'log = "NBV_SPECIAL_TOOLTIP {prefix} text=[NBVRowTooltip] END_SPECIAL_TOOLTIP"',
    ]


def build_steps():
    rows = _entries()
    helper = ["add_namespace = nbv_special_probe"]
    steps = [' log = "NBV_SPECIAL_BEGIN"']
    number = 0

    def event(tag, body):
        nonlocal number
        number += 1
        helper.extend([f"country_event = {{ id = nbv_special_probe.{number} hidden = yes is_triggered_only = yes",
                       " immediate = {"] + ["  " + line for line in body] + [" }", "}"])
        steps.append(f" {tag} = {{ country_event = {{ id = nbv_special_probe.{number} }} }}")

    # Observe native SOV ideas before removal. No artificial initial injection
    # can disguise another missed idea file or an incorrect name alias.
    body = []
    for source, keys in SOV_IDEAS.items():
        for phase in ("native", "removed", "restored"):
            if phase == "removed":
                body.append(f"remove_ideas = {source}")
            elif phase == "restored":
                body.append(f"add_ideas = {source}")
            body.append("force_update_dynamic_modifier = yes")
            for key in keys:
                body.extend(_sample(rows[source, key], "sov", phase, f"has_idea = {source}"))
    event("SOV", body)
    body = []
    for source, keys in SOV_IDEAS.items():
        for key in keys:
            body.extend(_sample(rows[source, key], "sov_wrong_root", "absent", f"has_idea = {source}"))
    event("GER", body)

    landmark_metric = _landmark_metric()
    body = []
    for phase in LANDMARK_PHASES:
        if phase == "partial_damage":
            body.append(f"64 = {{ damage_building = {{ type = {LANDMARK} province = 6521 damage = 0.5 }} }}")
        elif phase == "full_damage":
            body.append(f"64 = {{ damage_building = {{ type = {LANDMARK} province = 6521 damage = 1 }} }}")
        elif phase in ("repaired", "restored"):
            # Rebuild a clean copy; do not assume negative damage is supported.
            body += [f"64 = {{ set_building_level = {{ type = {LANDMARK} province = 6521 level = 0 }} }}",
                     f"64 = {{ set_building_level = {{ type = {LANDMARK} province = 6521 level = 1 }} }}"]
        elif phase == "removed":
            body.append(f"64 = {{ set_building_level = {{ type = {LANDMARK} province = 6521 level = 0 }} }}")
        elif phase == "unrelated_factory_damage":
            body.append("64 = { damage_building = { type = arms_factory damage = 0.5 } }")
        elif phase == "factory_repaired":
            # The isolated 1936 Brandenburg history contains five arms factories.
            # Reset only this disposable fixture to demonstrate that national
            # damage queries detect factories but cannot detect landmark damage.
            body += ["64 = { set_building_level = { type = arms_factory level = 0 } }",
                     "64 = { set_building_level = { type = arms_factory level = 5 } }"]
        body.append("force_update_dynamic_modifier = yes")
        for label, state_scope, condition in BUILDING_DIAGNOSTICS:
            prefix = f"NBV_SPECIAL_BUILDING_TRIGGER phase={phase} trigger={label}"
            lines = [f'if = {{ limit = {{ {condition} }} log = "{prefix} result=yes" }}',
                     f'else = {{ log = "{prefix} result=no" }}']
            body.extend(["64 = {"] + lines + ["}"] if state_scope else lines)
        # There is intentionally no NBVSource lookup for this unavailable
        # source. Read the normal full metric tooltip and ensure the unreliable
        # attribution stays absent even while the engine total changes.
        prefix = f'phase={phase} metric_id={landmark_metric["id"]}'
        body += [f'log = "NBV_SPECIAL_OMIT_VALUE {prefix} country=[ROOT.GetTag] '
                 'total=[?ROOT.modifier@stability_factor|6] END_SPECIAL_OMIT_VALUE"',
                 f'set_temp_variable = {{ nbv_entry_id = {landmark_metric["id"]} }}',
                 f'log = "NBV_SPECIAL_OMIT_ROW {prefix} text=[NBVRowValue] END_SPECIAL_OMIT_ROW"',
                 f'log = "NBV_SPECIAL_OMIT_TOOLTIP {prefix} text=[NBVRowTooltip] END_SPECIAL_OMIT_TOOLTIP"']
    event("GER", body)

    # Liberia has no native country ideas or leader traits in the 1936 history.
    # Separate real ROOT events keep German source fixtures and wars out of the
    # status curves. The analyzer also verifies peace and actual effective input.
    for family, driver in (("stability", "has_stability"), ("war_support", "has_war_support")):
        body = [f"set_temp_variable = {{ nbv_special_saved_status = ROOT.{driver} }}",
                'if = { limit = { has_war = no } log = "NBV_SPECIAL_PEACE family=' + family + ' passed=yes" }',
                'else = { log = "NBV_SPECIAL_PEACE family=' + family + ' passed=no" }']
        if family == "stability":
            # Native LIB has 100% support for its democratic ruling party.
            # Remove that +15% contribution in this disposable fixture while
            # leaving the government unchanged, so the base setter reaches
            # every requested effective endpoint, including genuine zero.
            body += ["set_popularities = { neutrality = 100 }", "force_update_dynamic_modifier = yes",
                     "set_temp_variable = { nbv_special_saved_status = ROOT.has_stability }"]
        for phase, point in list(POINTS) + [("restored", None)]:
            body.append(f"set_{family} = " + ("nbv_special_saved_status" if point is None else str(point)))
            if family == "stability" and phase == "restored":
                body.append("set_popularities = { democratic = 100 }")
            body.append("force_update_dynamic_modifier = yes")
            for source, keys in CURVES.items():
                if source.startswith(family + "_"):
                    for key in keys:
                        entry = rows[source, key]
                        body.extend(_sample(entry, family, phase, entry["activation_script"]))
        event("LIB", body)

    # A native peace-only modifier has a real on/off lifecycle independent of
    # its tooltip condition. Diplomacy changes remain inside the disposable run.
    peace = rows["country_is_at_peace", "decryption_power_factor"]
    body = []
    for phase in ("peace", "war", "restored"):
        if phase == "war":
            body.append("declare_war_on = { target = HAI type = annex_everything }")
        elif phase == "restored":
            body.append("white_peace = HAI")
        body.append("force_update_dynamic_modifier = yes")
        body.extend(_sample(peace, "peace", phase, "has_war = no"))
    event("LIB", body)
    path = ADDON / "events/nbv_special_probe_events.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(helper) + "\n", encoding="utf-8")
    # Remove only the exact obsolete file this helper created in the addon.
    # The native building triggers below require no dynamic token registration.
    token_path = (ADDON / "common/synchronized_dynamic_tokens/nbv_special_probe_tokens.txt").resolve()
    assert token_path.parent == (ADDON / "common/synchronized_dynamic_tokens").resolve()
    if token_path.exists():
        token_path.unlink()
    steps.append(' log = "NBV_SPECIAL_END"')
    return steps


def _curve_value(source, key, driver):
    endpoint = CURVES[source][key]
    if "_bad_" in source:
        return endpoint * max(0, (0.5 - driver) * 2)
    return endpoint * max(0, (driver - 0.5) * 2)


def _family_value(family, key, driver):
    return sum(_curve_value(source, key, driver) for source, keys in CURVES.items()
               if source.startswith(family + "_") and key in keys)


def analyze(content):
    from analyze_smoke_test import plain, is_expanded
    rows = _entries()
    values, texts, tips, row_texts = (defaultdict(list) for _ in range(4))
    prefix = r"kind=(\w+) index=(\d+) phase=(\w+)"
    value_pattern = (r"NBV_SPECIAL_VALUE " + prefix + r" country=(\w+) active=([01]) total=(" + NUMBER
                     + r") stability=(" + NUMBER + r") war_support=(" + NUMBER + r") END_SPECIAL_VALUE")
    for kind, index, phase, country, active, total, stability, war_support in re.findall(value_pattern, content):
        values[kind, int(index), phase].append(dict(country=country, active=active == "1", total=float(total),
                                                   stability=float(stability), war_support=float(war_support)))
    for marker, dest in (("TEXT", texts), ("TOOLTIP", tips), ("ROW", row_texts)):
        for kind, index, phase, text in re.findall(r"NBV_SPECIAL_" + marker + " " + prefix
                                                  + r" text=(.*?) END_SPECIAL_" + marker, content, re.S):
            dest[kind, int(index), phase].append(text.strip())
    expected_ids = set()

    def sample(entry, kind, phase):
        captures = values.get((kind, entry["index"], phase), [])
        return captures[0] if len(captures) == 1 else None

    def check(entry, kind, phase, country, present, contribution, delta, baseline_phase, require_absent_name=False):
        ident = kind, entry["index"], phase
        expected_ids.add(ident)
        observed = sample(entry, kind, phase)
        baseline = sample(entry, kind, baseline_phase)
        leafs, tooltips, formatted = texts.get(ident, []), tips.get(ident, []), row_texts.get(ident, [])
        leaf = leafs[0] if len(leafs) == 1 else ""
        tip = tooltips[0] if len(tooltips) == 1 else ""
        row_value = formatted[0] if len(formatted) == 1 else ""
        label = entry.get("display_name") or entry.get("display_name_zh") or entry["name_zh"]
        leaf_numbers = re.findall("(" + NUMBER + r")\s*(%?)", plain(leaf))
        displayed = (float(leaf_numbers[-1][0]) / (100 if leaf_numbers[-1][1] else 1)) if leaf_numbers else None
        leaf_ok = (is_expanded(leaf) and label in plain(leaf) and "\n" not in leaf
                   and displayed is not None and abs(displayed - contribution) <= .00006
                   and not any(term + "：" in plain(leaf) for term in
                               ("领袖", "顾问", "科技", "学说", "民族精神", "法案", "动态修正", "决议", "阵营", "政体"))) if present else not leaf
        tip_ok = (len(tooltips) == 1 and is_expanded(tip) and len(formatted) == 1 and is_expanded(row_value)
                  and plain(row_value) in plain(tip.splitlines()[0])
                  and (plain(leaf) in plain(tip) if present else (label not in plain(tip) if require_absent_name else True))
                  and not any(term in tip for term in ("其他来源", "无法拆分", "作用项：", "公式说明")))
        actual_delta = observed["total"] - baseline["total"] if observed and baseline else None
        total_ok = actual_delta is not None and (delta is None or abs(actual_delta - delta) <= .00025)
        presence_ok = bool(observed) and observed["country"] == country and observed["active"] == present
        return dict(kind=kind, source_id=entry["source_id"], key=entry["key"], index=entry["index"], phase=phase,
                    contribution=contribution, present=present, observation=observed, expected_total_delta=delta,
                    actual_total_delta=actual_delta, source_text=leaf, leaf_passed=leaf_ok,
                    tooltip_passed=tip_ok, total_passed=total_ok, presence_passed=presence_ok,
                    passed=len(leafs) == 1 and leaf_ok and tip_ok and total_ok and presence_ok)

    sov, wrong_root, status, peace_checks, landmark_checks = [], [], [], [], []
    for source, keys in SOV_IDEAS.items():
        for key, contribution in keys.items():
            entry = rows[source, key]
            baseline = sample(entry, "sov", "native")
            for phase in ("native", "removed", "restored"):
                observed = sample(entry, "sov", phase)
                delta = -contribution if phase == "removed" else 0
                # Removing a stability idea also changes native political-power
                # scaling. Account for that independent curve, never sum the
                # source fragments under test to obtain an expected total.
                indirect = 0
                if key == "political_power_factor" and observed and baseline:
                    indirect = (_family_value("stability", key, observed["stability"])
                                - _family_value("stability", key, baseline["stability"]))
                result = check(entry, "sov", phase, "SOV", phase != "removed", contribution, delta + indirect,
                               "native", require_absent_name=True)
                result["indirect_stability_curve_delta"] = indirect
                sov.append(result)
            wrong_root.append(check(entry, "sov_wrong_root", "absent", "GER", False, 0, 0, "absent", True))

    building_triggers = defaultdict(list)
    for phase, trigger, result in re.findall(r"NBV_SPECIAL_BUILDING_TRIGGER phase=(\w+) trigger=(\w+) result=(yes|no)", content):
        building_triggers[phase, trigger].append(result == "yes")
    omit_values, omit_tips, omit_rows = (defaultdict(list) for _ in range(3))
    for phase, metric, country, total in re.findall(r"NBV_SPECIAL_OMIT_VALUE phase=(\w+) metric_id=(\d+) country=(\w+) total=("
                                                   + NUMBER + r") END_SPECIAL_OMIT_VALUE", content):
        omit_values[phase].append(dict(metric_id=int(metric), country=country, total=float(total)))
    for marker, dest in (("ROW", omit_rows), ("TOOLTIP", omit_tips)):
        for phase, metric, text in re.findall(r"NBV_SPECIAL_OMIT_" + marker + r" phase=(\w+) metric_id=(\d+) text=(.*?) END_SPECIAL_OMIT_"
                                              + marker, content, re.S):
            dest[phase].append((int(metric), text.strip()))
    baseline_omit = omit_values["native"][0] if len(omit_values["native"]) == 1 else None
    metric_id = _landmark_metric()["id"]
    for phase in LANDMARK_PHASES:
        # The first two native engine runs established that partial and full
        # landmark damage disable the full +5% global effect. The third run
        # disproved has_damaged_buildings as a usable landmark health query.
        delta = -.05 if phase in ("partial_damage", "full_damage", "removed") else 0
        captures = omit_values.get(phase, [])
        observed = captures[0] if len(captures) == 1 else None
        tip_captures, row_captures = omit_tips.get(phase, []), omit_rows.get(phase, [])
        tip = tip_captures[0][1] if len(tip_captures) == 1 else ""
        row_value = row_captures[0][1] if len(row_captures) == 1 else ""
        actual_delta = observed["total"] - baseline_omit["total"] if observed and baseline_omit else None
        total_ok = actual_delta is not None and abs(actual_delta - delta) <= .00025
        omitted_ok = bool(tip) and LANDMARK_NAME not in plain(tip) and LANDMARK not in tip
        tip_ok = (len(tip_captures) == len(row_captures) == 1
                  and tip_captures[0][0] == row_captures[0][0] == metric_id
                  and is_expanded(tip) and is_expanded(row_value)
                  and plain(row_value) in plain(tip.splitlines()[0]) and omitted_ok)
        native = {label: building_triggers[phase, label][0] for label, _, _ in BUILDING_DIAGNOSTICS
                  if len(building_triggers[phase, label]) == 1}
        diagnostics_complete = len(native) == len(BUILDING_DIAGNOSTICS)
        expected_native = {label: (phase != "removed" if label.endswith("_gt0") else True)
                           for label, _, _ in BUILDING_DIAGNOSTICS}
        expected_native["country_damage_free"] = phase != "unrelated_factory_damage"
        building_ok = diagnostics_complete and native == expected_native
        result = dict(kind="landmark_unavailable", source_id=LANDMARK, key="stability_factor", metric_id=metric_id,
                      phase=phase, source_available=False, observation=observed,
                      expected_total_delta=delta, actual_total_delta=actual_delta, total_passed=total_ok,
                      source_omitted=omitted_ok, tooltip_passed=tip_ok, native_building_triggers=native,
                      expected_building_triggers=expected_native, building_passed=building_ok,
                      native_query_cannot_detect_landmark_damage=phase in ("partial_damage", "full_damage"),
                      passed=bool(observed) and observed["country"] == "GER" and observed["metric_id"] == metric_id
                      and total_ok and tip_ok and building_ok)
        landmark_checks.append(result)

    peace_flags = re.findall(r"NBV_SPECIAL_PEACE family=(\w+) passed=(yes|no)", content)
    points = dict(POINTS)
    for source, keys in CURVES.items():
        family = "stability" if source.startswith("stability_") else "war_support"
        for key in keys:
            entry = rows[source, key]
            baseline = sample(entry, family, "neutral")
            for phase in list(points) + ["restored"]:
                observed = sample(entry, family, phase)
                driver = observed[family] if observed else .5
                contribution = _curve_value(source, key, driver)
                present = abs(contribution) > 1e-7
                delta = (_family_value(family, key, driver) - _family_value(family, key, baseline[family])) if baseline else None
                result = check(entry, family, phase, "LIB", present, contribution, delta, "neutral")
                target_ok = phase == "restored" or (bool(observed) and abs(driver - points[phase]) <= .0001)
                result.update(requested_input=points.get(phase), actual_input=driver, input_target_passed=target_ok)
                result["passed"] = result["passed"] and target_ok
                status.append(result)
    entry = rows["country_is_at_peace", "decryption_power_factor"]
    for phase in ("peace", "war", "restored"):
        peace_checks.append(check(entry, "peace", phase, "LIB", phase != "war", -.5,
                                  .5 if phase == "war" else 0, "peace", True))
    coverage = all(set(logs) == expected_ids and all(len(captures) == 1 for captures in logs.values())
                   for logs in (values, texts, tips, row_texts))
    expected_building_triggers = {(phase, label) for phase in LANDMARK_PHASES for label, _, _ in BUILDING_DIAGNOSTICS}
    building_trigger_coverage = (set(building_triggers) == expected_building_triggers
                                and all(len(captures) == 1 for captures in building_triggers.values()))
    omit_coverage = all(set(logs) == set(LANDMARK_PHASES) and all(len(captures) == 1 for captures in logs.values())
                        for logs in (omit_values, omit_tips, omit_rows))
    groups = {"sov": sov, "sov_wrong_root": wrong_root, "landmark_unavailable": landmark_checks,
              "status_curves": status, "peace": peace_checks}
    group_passes = {key: bool(checks) and all(c["passed"] for c in checks) for key, checks in groups.items()}
    neutral_peace_ok = sorted(peace_flags) == [("stability", "yes"), ("war_support", "yes")]
    boundary_ok = content.count("NBV_SPECIAL_BEGIN") == content.count("NBV_SPECIAL_END") == 1
    return dict(special_source_checks=groups, special_source_group_passes=group_passes,
                special_source_observation_count=len(values), special_source_expected_count=len(expected_ids),
                special_omitted_source_observation_count=len(omit_values), special_omitted_source_expected_count=len(LANDMARK_PHASES),
                special_omitted_source_coverage=omit_coverage, special_landmark_source_implemented=False,
                special_source_coverage=coverage, special_curve_country_peace_passed=neutral_peace_ok,
                special_building_trigger_coverage=building_trigger_coverage,
                special_sources_passed=boundary_ok and coverage and omit_coverage and building_trigger_coverage
                and neutral_peace_ok and all(group_passes.values()))
