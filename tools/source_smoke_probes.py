"""Compile explicit source lifecycle probes into the isolated test addon only."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_steps():
    path = ROOT / 'tools/data/source-probe-specs.json'
    specs = json.loads(path.read_text(encoding='utf-8'))['probes']
    manifest = json.loads((ROOT / 'tools/data/source-display-manifest.json').read_text(encoding='utf-8'))
    steps = []
    for probe in specs:
        matches = [r for r in manifest['records'] if r['source_id'] == probe['source_id'] and r['key'] == probe['key']]
        assert len(matches) == 1, (probe['name'], len(matches))
        entry = matches[0]
        if entry.get('value_kind') != 'runtime':
            assert abs(float(entry['value_literal']) - probe['contribution']) < 1e-7, probe['name']
        source_fn = 'NBVSource' + str(entry['index'])
        for phase in probe['phases']:
            steps += [' ' + effect for effect in phase.get('effects', [])]
            # Force only the isolated test country to rebuild within this event.
            # Production rendering never calls this gameplay effect.
            if phase.get('refresh_cache', True):
                steps.append(' force_update_dynamic_modifier = yes')
            if probe['name'] == 'technology':
                for label, condition in (
                    ('has_tech', 'has_tech = basic_machine_tools'),
                    ('array', 'is_in_array = { array = researched_techs value = token:basic_machine_tools }'),
                ):
                    prefix = 'NBV_TECH_DIAGNOSTIC phase=' + phase['name'] + ' method=' + label
                    steps += [' if = { limit = { ' + condition + ' } log = "' + prefix + ' result=yes" }',
                              ' else = { log = "' + prefix + ' result=no" }']
            steps.append(' log = "NBV_EXPANDED_SOURCE probe=' + probe['name'] + ' phase=' + phase['name']
                         + ' value=[?ROOT.modifier@' + probe['key'] + '|4] text=[' + source_fn + '] END_EXPANDED_SOURCE"')
            if phase['present']:
                steps += [' set_temp_variable = { nbv_entry_id = ' + str(entry['metric_id']) + ' }',
                          ' log = "NBV_EXPANDED_TOOLTIP probe=' + probe['name'] + ' phase=' + phase['name']
                          + ' text=[NBVRowTooltip] END_EXPANDED_TOOLTIP"']
            for guard in phase.get('guards', []):
                guarded = [r for r in manifest['records'] if r['source_id'] == guard['source_id'] and r['key'] == guard['key']]
                assert len(guarded) == 1, guard
                steps.append(' log = "NBV_SOURCE_GUARD probe=' + probe['name'] + ' phase=' + phase['name']
                             + ' index=' + str(guarded[0]['index']) + ' text=[NBVSource' + str(guarded[0]['index']) + '] END_SOURCE_GUARD"')
        steps += [' ' + effect for effect in probe.get('cleanup', [])]
    return steps


def analyze(content):
    import re
    from analyze_smoke_test import plain, is_expanded
    specs = json.loads((ROOT / 'tools/data/source-probe-specs.json').read_text(encoding='utf-8'))['probes']
    logs, tooltips, guards = {}, {}, {}
    for name, phase, value, text in re.findall(r'NBV_EXPANDED_SOURCE probe=(\w+) phase=(\w+) value=([+\-0-9.]+) text=(.*?) END_EXPANDED_SOURCE', content, re.S):
        logs.setdefault((name, phase), []).append((float(value), text.strip()))
    for name, phase, text in re.findall(r'NBV_EXPANDED_TOOLTIP probe=(\w+) phase=(\w+) text=(.*?) END_EXPANDED_TOOLTIP', content, re.S):
        tooltips.setdefault((name, phase), []).append(text.strip())
    for name, phase, index, text in re.findall(r'NBV_SOURCE_GUARD probe=(\w+) phase=(\w+) index=(\d+) text=(.*?) END_SOURCE_GUARD', content, re.S):
        guards.setdefault((name, phase), []).append((int(index), text.strip()))
    checks = []
    for probe in specs:
        phase_checks = []
        first = logs.get((probe['name'], probe['phases'][0]['name']), [])
        baseline = first[0][0] if len(first) == 1 else None
        for phase in probe['phases']:
            samples = logs.get((probe['name'], phase['name']), [])
            value, text = samples[0] if len(samples) == 1 else (None, '')
            delta = value - baseline if value is not None and baseline is not None else None
            expected = phase['delta']
            valid_text = (is_expanded(text) and probe['name_contains'] in plain(text)
                          and phase.get('expected_value_text', probe.get('expected_value_text', '')) in plain(text)
                          and not any(label + '：' in plain(text) for label in ('领袖', '顾问', '科技', '学说', '民族精神', '法案', '动态修正', '决议', '阵营', '政体'))
                          and '\n' not in text) if phase['present'] else not text
            tips = tooltips.get((probe['name'], phase['name']), [])
            expected_guards = phase.get('guards', [])
            actual_guards = guards.get((probe['name'], phase['name']), [])
            guard_ok = len(expected_guards) == len(actual_guards) and all(
                is_expanded(text) and bool(text) if guard['present'] else not text
                for guard, (_, text) in zip(expected_guards, actual_guards))
            tip_ok = (len(tips) == 1 and is_expanded(tips[0]) and plain(text) in plain(tips[0])
                      and not any(term in tips[0] for term in ('其他来源', '无法拆分', '作用项：', '公式说明'))) if phase['present'] else not tips
            phase_checks.append(dict(phase=phase['name'], value=value, delta=delta,
                                     expected_delta=expected, source_text=text,
                                     passed=len(samples) == 1 and delta is not None
                                     and (expected is None or abs(delta - expected) <= .0002) and valid_text and tip_ok and guard_ok,
                                     text_passed=valid_text, tooltip_passed=tip_ok, guards_passed=guard_ok))
        checks.append(dict(name=probe['name'], source_id=probe['source_id'], category=probe['category'],
                           key=probe['key'], phases=phase_checks, passed=all(p['passed'] for p in phase_checks)))
    expected_keys = {(p['name'], s['name']) for p in specs for s in p['phases']}
    coverage = set(logs) == expected_keys
    return dict(expanded_source_checks=checks, expanded_source_coverage=coverage,
                expanded_sources_passed=bool(checks) and coverage and all(c['passed'] for c in checks))
