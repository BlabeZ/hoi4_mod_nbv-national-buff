"""Broad dynamic-source probes, emitted only into the isolated smoke addon.

The scan exercises every mapped current-country variable contribution and every
fixed dynamic contribution through BOTH the leaf and the complete UI tooltip.
It is intentionally driven by the current manifest, so scanner fixes expand the
test coverage without hard-coded source indices or counts.
"""
from collections import defaultdict
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT.parent / "nbv-test-workspace/smoke-addon"
TYPES = ("dynamic_modifier", "dynamic_modifier_variable")
CONDITIONAL_SOURCES = ("INS_royal_netherlands_east_indies_army", "INS_state_militia_sabotage_1")
LIFECYCLE_SOURCES = (
    ("GER_mefo_bills_modifier",),
    ("GER_airforce_modifier",),
    ("GER_navy_fascist_modifier",),
    ("SOV_the_red_army_dynamic_modifier", "SOV_the_red_army_dynamic_modifier_alt"),
    ("SOV_soviet_airforce_dynamic_modifier", "SOV_soviet_airforce_dynamic_modifier_alt"),
    ("ITA_regio_esercito_dynamic_modifier",),
    ("ITA_regia_marina_dynamic_modifier",),
    ("JAP_national_army_dm",),
    ("JAP_japanese_navy_dm",),
    ("GER_overburdened_state_modifier",),
    ("SOV_invaders_must_die",),
)


def _entries(include_conditional=False):
    manifest = json.loads((ROOT / "tools/data/source-display-manifest.json").read_text(encoding="utf-8"))
    bindings = {}
    for filename in ("dynamic-source-bindings.json", "dynamic-spirit-source-bindings.json"):
        table = json.loads((ROOT / "tools/data" / filename).read_text(encoding="utf-8"))
        for key, rows in table["by_modifier"].items():
            for row in rows:
                if row["source_type"] in TYPES:
                    bindings[row["source_id"], key] = row
    rows, skipped = [], []
    for row in manifest["records"]:
        if row["source_type"] not in TYPES:
            continue
        binding = bindings[row["source_id"], row["key"]]
        entry = dict(row, display_name=binding.get("display_name_zh", ""),
                     native_dynamic_name=binding.get("native_dynamic_name", False),
                     enable_script=binding.get("enable_script", ""))
        variable = (entry.get("value_expression") or {}).get("variable", "")
        if not include_conditional and binding.get("enable_evaluation") not in (None, "always_yes", "absent_enabled"):
            skipped.append(dict(source_id=entry["source_id"], key=entry["key"],
                                reason="conditional_enable_fixture_not_configured",
                                enable_evaluation=binding["enable_evaluation"]))
        elif entry.get("value_kind") == "runtime" and not variable.startswith("ROOT."):
            skipped.append(dict(source_id=entry["source_id"], key=entry["key"],
                                reason="external_country_or_global_input", variable=variable))
        else:
            rows.append(entry)
    return rows, skipped


def _conditional_entries():
    rows, _ = _entries(include_conditional=True)
    selected = []
    for source_id in CONDITIONAL_SOURCES:
        candidates = [row for row in rows if row["source_id"] == source_id]
        if candidates:
            candidates.sort(key=lambda row: (row["key"] != "army_attack_factor", row["index"]))
            selected.append(candidates[0])
    return selected


def _lifecycle(rows):
    selected = []
    for alternatives in LIFECYCLE_SOURCES:
        candidates = []
        for source_id in alternatives:
            candidates = [row for row in rows if row["source_id"] == source_id]
            if candidates:
                break
        assert candidates, ("missing lifecycle source", alternatives)
        # Prefer percentage metrics; all candidates still receive the full scan.
        candidates.sort(key=lambda row: ("%" not in row["source_format_code"], row["index"]))
        selected.append(candidates[0])
    return selected


def _is_runtime(entry):
    return entry.get("value_kind") == "runtime"


def _expected(entry, input_value):
    if not _is_runtime(entry):
        return float(entry["value_literal"])
    expr = entry["value_expression"]
    return input_value * float(expr["coefficient"]) + float(expr["offset"])


def _save_presence(entry):
    source_id = entry["source_id"]
    return ["set_temp_variable = { nbv_dynamic_probe_owned = 0 }",
            "if = { limit = { has_dynamic_modifier = " + source_id + " } set_temp_variable = { nbv_dynamic_probe_owned = 1 } }"]


def _save_input(entry):
    if not _is_runtime(entry):
        return []
    variable = entry["value_expression"]["variable"]
    return ["set_temp_variable = { nbv_dynamic_probe_input_existed = 0 }",
            "if = { limit = { has_variable = " + variable + " } set_temp_variable = { nbv_dynamic_probe_input_existed = 1 } }",
            "set_temp_variable = { nbv_dynamic_probe_saved_input = " + variable + " }"]


def _restore_input(entry):
    if not _is_runtime(entry):
        return []
    variable = entry["value_expression"]["variable"]
    return ["if = { limit = { check_variable = { nbv_dynamic_probe_input_existed = 1 } } set_variable = { " + variable + " = nbv_dynamic_probe_saved_input } }",
            "else = { clear_variable = " + variable + " }"]


def _sample(entry, kind, phase):
    prefix = "kind=" + kind + " index=" + str(entry["index"]) + " phase=" + phase
    source = "NBVSource" + str(entry["index"])
    value = "nbv_source_value_" + str(entry["index"])
    return [
        "set_temp_variable = { " + value + " = 0 }",
        'log = "NBV_DYNAMIC_TEXT ' + prefix + ' text=[' + source + '] END_DYNAMIC_TEXT"',
        'log = "NBV_DYNAMIC_VALUE ' + prefix + ' value=[?' + value + '|5] END_DYNAMIC_VALUE"',
        "set_temp_variable = { nbv_entry_id = " + str(entry["metric_id"]) + " }",
        'log = "NBV_DYNAMIC_TOOLTIP ' + prefix + ' text=[NBVRowTooltip] END_DYNAMIC_TOOLTIP"',
    ]


def build_steps():
    rows, _ = _entries()
    steps = ['log = "NBV_DYNAMIC_BEGIN"']
    # Observe a real initial German spirit before any fixture injection. This
    # specifically distinguishes initial UI expansion from forced test setup.
    baseline = next(row for row in rows if row["source_id"] == "GER_mefo_bills_modifier"
                    and row["key"] == "production_speed_arms_factory_factor")
    variable = baseline["value_expression"]["variable"]
    steps += _save_presence(baseline)
    steps += ['log = "NBV_DYNAMIC_BASELINE index=' + str(baseline["index"])
              + ' owned=[?nbv_dynamic_probe_owned|0] input=[?' + variable + '|5] END_DYNAMIC_BASELINE"']
    steps += _sample(baseline, "baseline", "native")

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["source_id"]].append(row)
    for source_id, group in grouped.items():
        steps += _save_presence(group[0])
        steps += ["if = { limit = { NOT = { has_dynamic_modifier = " + source_id + " } } add_dynamic_modifier = { modifier = " + source_id + " } }"]
        for entry in group:
            steps += _save_input(entry)
            if _is_runtime(entry):
                steps += ["set_variable = { " + entry["value_expression"]["variable"] + " = 0.125 }"]
            steps += _sample(entry, "scan", "active")
            steps += _restore_input(entry)
        steps += ["if = { limit = { check_variable = { nbv_dynamic_probe_owned = 0 } } remove_dynamic_modifier = { modifier = " + source_id + " } }"]

    for entry in _lifecycle(rows):
        source_id = entry["source_id"]
        steps += _save_presence(entry) + _save_input(entry)
        for phase in ("inactive", "active", "updated", "zero", "removed") if _is_runtime(entry) else ("inactive", "active", "removed"):
            if phase in ("inactive", "removed"):
                steps += ["if = { limit = { has_dynamic_modifier = " + source_id + " } remove_dynamic_modifier = { modifier = " + source_id + " } }"]
            elif phase == "active":
                steps += ["add_dynamic_modifier = { modifier = " + source_id + " }"]
            if _is_runtime(entry):
                value = {"inactive": ".125", "active": ".125", "updated": ".25", "zero": "0", "removed": ".125"}[phase]
                steps += ["set_variable = { " + entry["value_expression"]["variable"] + " = " + value + " }"]
            # No forced engine update: these are current-input source-display
            # tests, not tests of the daily cached aggregate contribution.
            steps += _sample(entry, "lifecycle", phase)
        steps += _restore_input(entry)
        steps += ["if = { limit = { check_variable = { nbv_dynamic_probe_owned = 1 } } add_dynamic_modifier = { modifier = " + source_id + " } }"]
    # A genuine INS event establishes ROOT=INS, so the native original_tag and
    # DLC conditions are tested in their intended country rather than mocked.
    helper = ["add_namespace = nbv_dynamic_probe"]
    event_number = 0
    for entry in _conditional_entries():
        source_id = entry["source_id"]
        if "original_tag = INS" in entry["enable_script"]:
            steps += _save_presence(entry) + _save_input(entry)
            steps += ["add_dynamic_modifier = { modifier = " + source_id + " }"]
            if _is_runtime(entry):
                steps += ["set_variable = { " + entry["value_expression"]["variable"] + " = .125 }"]
            steps += _sample(entry, "conditional_wrong_tag", "active")
            steps += _restore_input(entry)
            steps += ["if = { limit = { check_variable = { nbv_dynamic_probe_owned = 0 } } remove_dynamic_modifier = { modifier = " + source_id + " } }"]
        body = _save_presence(entry) + _save_input(entry)
        body += ["set_temp_variable = { nbv_dynamic_probe_enabled = 0 }",
                 "if = { limit = { " + entry["enable_script"] + " } set_temp_variable = { nbv_dynamic_probe_enabled = 1 } }",
                 'log = "NBV_DYNAMIC_CONDITION index=' + str(entry["index"])
                 + ' country=[ROOT.GetTag] enabled=[?nbv_dynamic_probe_enabled|0] END_DYNAMIC_CONDITION"']
        for phase in ("inactive", "active", "updated", "zero", "removed") if _is_runtime(entry) else ("inactive", "active", "removed"):
            if phase in ("inactive", "removed"):
                body += ["if = { limit = { has_dynamic_modifier = " + source_id + " } remove_dynamic_modifier = { modifier = " + source_id + " } }"]
            elif phase == "active":
                body += ["add_dynamic_modifier = { modifier = " + source_id + " }"]
            if _is_runtime(entry):
                value = {"inactive": ".125", "active": ".125", "updated": ".25", "zero": "0", "removed": ".125"}[phase]
                body += ["set_variable = { " + entry["value_expression"]["variable"] + " = " + value + " }"]
            body += _sample(entry, "conditional", phase)
        body += _restore_input(entry)
        body += ["if = { limit = { check_variable = { nbv_dynamic_probe_owned = 1 } } add_dynamic_modifier = { modifier = " + source_id + " } }"]
        event_number += 1
        helper += ["country_event = { id = nbv_dynamic_probe." + str(event_number)
                   + " hidden = yes is_triggered_only = yes immediate = {"] + body + ["} }"]
        steps += ["INS = { country_event = { id = nbv_dynamic_probe." + str(event_number) + " } }"]
    path = ADDON / "events/nbv_dynamic_probe_events.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(helper) + "\n", encoding="utf-8")
    steps += ['log = "NBV_DYNAMIC_END"']
    return [" " + line for line in steps]


def analyze(content):
    from analyze_smoke_test import plain, is_expanded
    rows, skipped = _entries()
    texts, values, tooltips = defaultdict(list), defaultdict(list), defaultdict(list)
    for kind, index, phase, text in re.findall(r"NBV_DYNAMIC_TEXT kind=(\w+) index=(\d+) phase=(\w+) text=(.*?) END_DYNAMIC_TEXT", content, re.S):
        texts[kind, int(index), phase].append(text.strip())
    for kind, index, phase, value in re.findall(r"NBV_DYNAMIC_VALUE kind=(\w+) index=(\d+) phase=(\w+) value=([+\-0-9.]+) END_DYNAMIC_VALUE", content):
        values[kind, int(index), phase].append(float(value))
    for kind, index, phase, text in re.findall(r"NBV_DYNAMIC_TOOLTIP kind=(\w+) index=(\d+) phase=(\w+) text=(.*?) END_DYNAMIC_TOOLTIP", content, re.S):
        tooltips[kind, int(index), phase].append(text.strip())
    expected_keys = set()

    def check(entry, kind, phase, present, expected):
        ident = kind, entry["index"], phase
        expected_keys.add(ident)
        leaves, nums, tips = texts.get(ident, []), values.get(ident, []), tooltips.get(ident, [])
        leaf = leaves[0] if len(leaves) == 1 else ""
        # Native localisation expands the textual sprite marker (£) into the
        # engine's icon control byte (0x13). Retain the sprite ID and all name
        # text; only normalise that representation before exact containment.
        label = (entry["display_name"] or "").replace("£", "\x13")
        if entry["native_dynamic_name"]:
            name_ok = (not any(token in leaf for token in ("[", "]", entry["source_id"], entry["name_loc_key"]))
                       and not re.search(r"\b(?:NORDIC_get_adjective|NORDIC_get_alliance_name|IRQ_navy_modifier_key)\b", leaf))
        else:
            name_ok = bool(label) and label in plain(leaf)
        leaf_ok = (is_expanded(leaf) and name_ok
                   and "\n" not in leaf) if present else not leaf
        value_ok = len(nums) == 1 and (abs(nums[0] - expected) <= .00006 if present else True)
        tooltip_ok = len(tips) == 1 and is_expanded(tips[0]) and (plain(leaf) in plain(tips[0]) if present else True)
        return dict(source_id=entry["source_id"], key=entry["key"], index=entry["index"],
                    kind=kind, phase=phase, expected=expected, present=present,
                    source_value=nums[0] if len(nums) == 1 else None,
                    source_text=leaf, leaf_passed=leaf_ok, value_passed=value_ok,
                    tooltip_passed=tooltip_ok,
                    passed=len(leaves) == 1 and leaf_ok and value_ok and tooltip_ok)

    scan = [check(row, "scan", "active", True, _expected(row, .125)) for row in rows]
    lifecycle = []
    for row in _lifecycle(rows):
        phases = ("inactive", "active", "updated", "zero", "removed") if _is_runtime(row) else ("inactive", "active", "removed")
        for phase in phases:
            present = phase in ("active", "updated")
            lifecycle.append(check(row, "lifecycle", phase, present,
                                   _expected(row, .25 if phase == "updated" else .125) if present else 0))
    baseline_logs = re.findall(r"NBV_DYNAMIC_BASELINE index=(\d+) owned=([01]) input=([+\-0-9.]+) END_DYNAMIC_BASELINE", content)
    baseline_entry = next(row for row in rows if row["source_id"] == "GER_mefo_bills_modifier"
                          and row["key"] == "production_speed_arms_factory_factor")
    owned, native_input = (baseline_logs[0][1] == "1", float(baseline_logs[0][2])) if len(baseline_logs) == 1 else (False, 0)
    baseline = check(baseline_entry, "baseline", "native", owned and native_input != 0,
                     _expected(baseline_entry, native_input))
    baseline.update(owned=owned, native_input=native_input)
    baseline["passed"] = baseline["passed"] and len(baseline_logs) == 1 and owned and abs(native_input - .1) < .00001
    conditions = defaultdict(list)
    for index, country, enabled in re.findall(r"NBV_DYNAMIC_CONDITION index=(\d+) country=(\w+) enabled=([01]) END_DYNAMIC_CONDITION", content):
        conditions[int(index)].append((country, enabled == "1"))
    conditional = []
    for row in _conditional_entries():
        if "original_tag = INS" in row["enable_script"]:
            result = check(row, "conditional_wrong_tag", "active", False, 0)
            result.update(native_condition_enabled=False, country="GER")
            conditional.append(result)
        condition = conditions.get(row["index"], [])
        enabled = len(condition) == 1 and condition[0] == ("INS", True)
        phases = ("inactive", "active", "updated", "zero", "removed") if _is_runtime(row) else ("inactive", "active", "removed")
        for phase in phases:
            present = enabled and phase in ("active", "updated")
            result = check(row, "conditional", phase, present,
                           _expected(row, .25 if phase == "updated" else .125) if present else 0)
            result.update(native_condition_enabled=enabled, country=condition[0][0] if len(condition) == 1 else None)
            result["passed"] = result["passed"] and enabled
            conditional.append(result)
    coverage = set(texts) == set(values) == set(tooltips) == expected_keys and "NBV_DYNAMIC_END" in content
    failures = [row for row in scan if not row["passed"]]
    return dict(dynamic_extended_passed=coverage and baseline["passed"] and not failures
                and all(row["passed"] for row in lifecycle + conditional),
                dynamic_extended_coverage=coverage,
                dynamic_native_baseline=baseline,
                dynamic_scan_binding_count=len(scan),
                dynamic_scan_source_count=len({row["source_id"] for row in scan}),
                dynamic_scan_variable_binding_count=sum(_is_runtime(row) for row in rows),
                dynamic_scan_fixed_binding_count=sum(not _is_runtime(row) for row in rows),
                dynamic_scan_passed_count=sum(row["passed"] for row in scan),
                dynamic_scan_failures=failures,
                dynamic_scan_excluded=skipped,
                dynamic_lifecycle_checks=lifecycle,
                dynamic_conditional_checks=conditional)
