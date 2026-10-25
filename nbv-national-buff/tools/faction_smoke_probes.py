"""Faction-source engine probes, emitted ONLY into the isolated smoke addon."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT.parent / "nbv-test-workspace/smoke-addon"
PROBES = (
    {"name": "rule", "source_id": "war_declaration_rule_faction_leader_only", "key": "stability_factor",
     "coefficient": 0, "offset": -.05,
     "off": "set_faction_rule = war_declaration_rule_independent_countries_only",
     "on": "set_faction_rule = war_declaration_rule_faction_leader_only"},
    {"name": "scale", "source_id": "faction_manifest_conquest_of_territory:scale", "key": "offensive_war_stability_factor",
     "coefficient": .15, "offset": 0,
     "off": "set_faction_manifest = faction_manifest_defense_of_democracy",
     "on": "set_faction_manifest = faction_manifest_conquest_of_territory"},
    {"name": "reversed", "source_id": "faction_manifest_china_territorial_integrity:reversed", "key": "army_core_defence_factor",
     "coefficient": -.1, "offset": .1,
     "off": "set_faction_manifest = faction_manifest_defense_of_democracy",
     "on": "set_faction_manifest = faction_manifest_china_territorial_integrity"},
    {"name": "section", "source_id": "faction_manifest_containment_of_communism:section:manifest_fulfilled", "key": "required_garrison_factor",
     "coefficient": 0, "offset": -.15, "minimum": .75,
     "off": "set_faction_manifest = faction_manifest_defense_of_democracy",
     "on": "set_faction_manifest = faction_manifest_containment_of_communism"},
)
PHASES = ("inactive", "active", "removed")


def build_steps():
    manifest = json.loads((ROOT / "tools/data/source-display-manifest.json").read_text(encoding="utf-8"))
    helper = ["add_namespace = nbv_faction_probe"]
    event_number = 0

    def member_event(body):
        nonlocal event_number
        event_number += 1
        helper.extend([f"country_event = {{ id = nbv_faction_probe.{event_number} hidden = yes is_triggered_only = yes",
                       " immediate = {"] + ["  " + line for line in body] + [" }", "}"])
        return f" POL = {{ country_event = {{ id = nbv_faction_probe.{event_number} }} }}"

    steps = [
        ' log = "NBV_FACTION_BEGIN"',
        # Test-only diplomacy. Keep Poland alive for a genuinely separate event
        # ROOT; merely scoping POL inside the GER event does not change ROOT.
        " if = { limit = { NOT = { is_in_faction = yes } } create_faction = NBV_Test_Faction }",
        " set_faction_leader = yes",
        " POL = { if = { limit = { is_in_faction = yes } faction_leader = { remove_from_faction = POL } } }",
        " add_to_faction = POL",
        " set_politics = { ruling_party = fascism elections_allowed = no }",
        " POL = { set_politics = { ruling_party = fascism elections_allowed = no } }",
        # Conquest manifest uses non-core territory. Give it a concrete target,
        # while relying on the actual engine fulfillment for its expected value.
        " if = { limit = { LUX = { exists = yes } } annex_country = { target = LUX transfer_troops = no } }",
    ]
    for probe in PROBES:
        matches = [row for row in manifest["records"] if row["source_id"] == probe["source_id"] and row["key"] == probe["key"]]
        assert len(matches) == 1, (probe["name"], len(matches))
        entry = matches[0]
        source = "NBVSource" + str(entry["index"])
        temp = "nbv_source_value_" + str(entry["index"])
        for phase in PHASES:
            steps.append(" " + probe["on" if phase == "active" else "off"])

            def sample(role):
                prefix = f"probe={probe['name']} role={role} phase={phase}"
                return [
                    "force_update_dynamic_modifier = yes",
                    f'log = "NBV_FACTION_TEXT {prefix} text=[{source}] END_FACTION_TEXT"',
                    f'log = "NBV_FACTION_VALUE {prefix} country=[ROOT.GetTag] total=[?ROOT.modifier@{probe["key"]}|4] driver=[?ROOT.faction_manifest_fulfillment|4] source=[?{temp}|4] END_FACTION_VALUE"',
                    f"set_temp_variable = {{ nbv_entry_id = {entry['metric_id']} }}",
                    f'log = "NBV_FACTION_TOOLTIP {prefix} text=[NBVRowTooltip] END_FACTION_TOOLTIP"',
                ]

            steps += [" " + line for line in sample("leader")]
            steps.append(member_event(sample("member")))

    # 1.19.3 verified recipient model: only the faction leader's government
    # controls the legacy modifier, which is then applied to every member.
    legacy_matches = [row for row in manifest["records"]
                      if row["source_id"] == "democratic:faction_modifiers"
                      and row["key"] == "faction_trade_opinion_factor"]
    assert len(legacy_matches) == 1
    legacy_entry = legacy_matches[0]
    legacy_source = "NBVSource" + str(legacy_entry["index"])
    legacy_temp = "nbv_source_value_" + str(legacy_entry["index"])
    legacy = (
        ("both_fascist", []),
        ("leader_democratic", ["set_politics = { ruling_party = democratic elections_allowed = yes }"]),
        ("member_neutral", ["POL = { set_politics = { ruling_party = neutrality elections_allowed = no } }"]),
        ("leader_fascist", ["set_politics = { ruling_party = fascism elections_allowed = no }"]),
        ("member_democratic", ["POL = { set_politics = { ruling_party = democratic elections_allowed = yes } }"]),
        ("member_left", ["remove_from_faction = POL"]),
    )
    for phase, effects in legacy:
        steps += [" " + effect for effect in effects]

        def legacy_sample(role):
            return ["force_update_dynamic_modifier = yes",
                    f'log = "NBV_FACTION_LEGACY_TEXT phase={phase} role={role} text=[{legacy_source}] END_FACTION_LEGACY_TEXT"',
                    f'log = "NBV_FACTION_LEGACY phase={phase} role={role} country=[ROOT.GetTag] value=[?ROOT.modifier@faction_trade_opinion_factor|4] source=[?{legacy_temp}|4] END_FACTION_LEGACY"',
                    f"set_temp_variable = {{ nbv_entry_id = {legacy_entry['metric_id']} }}",
                    f'log = "NBV_FACTION_LEGACY_TOOLTIP phase={phase} role={role} text=[NBVRowTooltip] END_FACTION_LEGACY_TOOLTIP"']

        steps += [" " + line for line in legacy_sample("leader")]
        steps.append(member_event(legacy_sample("member")))
    steps += [" set_faction_manifest = faction_manifest_conquest_of_territory",
              ' log = "NBV_FACTION_END"']
    path = ADDON / "events/nbv_faction_probe_events.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(helper) + "\n", encoding="utf-8")
    return steps


def analyze(content):
    from analyze_smoke_test import plain, is_expanded
    table = json.loads((ROOT / "tools/data/faction-source-bindings.json").read_text(encoding="utf-8"))
    names = {(row["source_id"], key): row["display_name_zh"] for key, rows in table["by_modifier"].items() for row in rows}
    texts, values, tips = {}, {}, {}
    for probe, role, phase, text in re.findall(
            r"NBV_FACTION_TEXT probe=(\w+) role=(\w+) phase=(\w+) text=(.*?) END_FACTION_TEXT", content, re.S):
        texts.setdefault((probe, role, phase), []).append(text.strip())
    for probe, role, phase, country, total, driver, source in re.findall(
            r"NBV_FACTION_VALUE probe=(\w+) role=(\w+) phase=(\w+) country=(\w+) total=([+\-0-9.]+) driver=([+\-0-9.]+) source=([+\-0-9.]+) END_FACTION_VALUE", content):
        values.setdefault((probe, role, phase), []).append(dict(country=country, total=float(total), driver=float(driver), source=float(source)))
    for probe, role, phase, text in re.findall(
            r"NBV_FACTION_TOOLTIP probe=(\w+) role=(\w+) phase=(\w+) text=(.*?) END_FACTION_TOOLTIP", content, re.S):
        tips.setdefault((probe, role, phase), []).append(text.strip())
    checks = []
    for probe in PROBES:
        for role in ("leader", "member"):
            baseline = values.get((probe["name"], role, "inactive"), [])
            baseline = baseline[0]["total"] if len(baseline) == 1 else None
            phases = []
            for phase in PHASES:
                ident = (probe["name"], role, phase)
                samples, rows, tooltip = values.get(ident, []), texts.get(ident, []), tips.get(ident, [])
                value = samples[0] if len(samples) == 1 else None
                text = rows[0] if len(rows) == 1 else ""
                expected = 0.0
                if phase == "active" and value:
                    expected = probe["coefficient"] * value["driver"] + probe["offset"]
                    if "minimum" in probe and value["driver"] < probe["minimum"]:
                        expected = 0.0
                present = abs(expected) >= .00005
                label = names[probe["source_id"], probe["key"]]
                forbidden = ("领袖：", "顾问：", "科技：", "学说：", "民族精神：", "法案：", "动态修正：", "决议：", "阵营：", "政体：")
                text_ok = (is_expanded(text) and label in plain(text) and "\n" not in text
                           and not any(token in plain(text) for token in forbidden)) if present else not text
                tooltip_ok = (len(tooltip) == 1 and is_expanded(tooltip[0]) and plain(text) in plain(tooltip[0])) if present else len(tooltip) == 1
                delta = value["total"] - baseline if value and baseline is not None else None
                source_ok = value is not None and (abs(value["source"] - expected) <= .0003 if present else True)
                passed = (len(rows) == len(samples) == 1 and value["country"] == ("GER" if role == "leader" else "POL")
                          and delta is not None and abs(delta - expected) <= .0003 and source_ok and text_ok and tooltip_ok)
                phases.append(dict(phase=phase, expected_contribution=expected, native_sample=value,
                                   country_delta=delta, text=text, text_passed=text_ok, tooltip_passed=tooltip_ok,
                                   source_value_passed=source_ok, passed=passed))
            # A source that remained zero throughout is not evidence that a
            # runtime formula was tested; report it as a failed probe.
            positive_coverage = any(abs(row["expected_contribution"]) >= .00005 for row in phases)
            checks.append(dict(probe=probe["name"], role=role, key=probe["key"], phases=phases,
                               nonzero_case_exercised=positive_coverage,
                               passed=positive_coverage and all(row["passed"] for row in phases)))
    legacy = [dict(phase=phase, role=role, country=country, value=float(value), source=float(source)) for phase, role, country, value, source in re.findall(
        r"NBV_FACTION_LEGACY phase=(\w+) role=(\w+) country=(\w+) value=([+\-0-9.]+) source=([+\-0-9.]+) END_FACTION_LEGACY", content)]
    legacy_texts, legacy_tips = {}, {}
    for phase, role, text in re.findall(r"NBV_FACTION_LEGACY_TEXT phase=(\w+) role=(\w+) text=(.*?) END_FACTION_LEGACY_TEXT", content, re.S):
        legacy_texts.setdefault((phase, role), []).append(text.strip())
    for phase, role, text in re.findall(r"NBV_FACTION_LEGACY_TOOLTIP phase=(\w+) role=(\w+) text=(.*?) END_FACTION_LEGACY_TOOLTIP", content, re.S):
        legacy_tips.setdefault((phase, role), []).append(text.strip())
    legacy_checks = []
    legacy_phases = ("both_fascist", "leader_democratic", "member_neutral", "leader_fascist", "member_democratic", "member_left")
    for phase in legacy_phases:
        for role in ("leader", "member"):
            samples = [sample for sample in legacy if sample["phase"] == phase and sample["role"] == role]
            text_samples, tip_samples = legacy_texts.get((phase, role), []), legacy_tips.get((phase, role), [])
            text = text_samples[0] if len(text_samples) == 1 else ""
            expected = .5 if phase in ("leader_democratic", "member_neutral") else 0
            label = names["democratic:faction_modifiers", "faction_trade_opinion_factor"]
            text_ok = (is_expanded(text) and label in plain(text) and "\n" not in text
                       and not any(token in plain(text) for token in forbidden)) if expected else not text
            tooltip_ok = (len(tip_samples) == 1 and is_expanded(tip_samples[0])
                          and (plain(text) in plain(tip_samples[0]) if expected else True))
            sample = samples[0] if len(samples) == 1 else None
            passed = (len(samples) == len(text_samples) == 1 and sample["country"] == ("GER" if role == "leader" else "POL")
                      and abs(sample["value"] - expected) <= .0002
                      and (abs(sample["source"] - expected) <= .0002 if expected else True)
                      and text_ok and tooltip_ok)
            legacy_checks.append(dict(phase=phase, role=role, expected_contribution=expected,
                                      native_sample=sample, text=text, text_passed=text_ok,
                                      tooltip_passed=tooltip_ok, passed=passed))
    expected_keys = {(p["name"], role, phase) for p in PROBES for role in ("leader", "member") for phase in PHASES}
    coverage = set(values) == set(texts) == set(tips) == expected_keys and "NBV_FACTION_END" in content
    return dict(faction_source_checks=checks, faction_source_coverage=coverage,
                faction_sources_passed=coverage and bool(checks) and all(row["passed"] for row in checks)
                and all(row["passed"] for row in legacy_checks),
                faction_ideology_diagnostics=legacy, faction_ideology_source_checks=legacy_checks,
                faction_ideology_sources_passed=bool(legacy_checks) and all(row["passed"] for row in legacy_checks))
