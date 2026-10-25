"""Interpret isolated engine logs; never infer a valid zero from a missing result."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from build_mod import write, VERSION
from display_layout import load_display_records
from display_names import metric_display_name
from prepare_smoke_test import display_signature

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent / 'nbv-test-workspace'
NUMBER = r'[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+\-]?\d+)?'
SOURCE_PROBES = (
    # Names match this test profile's installed 1.19.3 simp_chinese localisation:
    # ideas_l_simp_chinese.yml and traits_l_simp_chinese.yml.
    ('sour_loser', 'drift_defence_factor', 0.5, '苦涩的失败者'),
    ('limited_conscription', 'conscription', 0.025, '有限征兵'),
    ('limited_exports', 'industrial_capacity_factory', 0.05, '有限出口'),
    ('GER_der_fuhrer', 'political_power_factor', 0.1, '元首'),
)


def is_expanded(value):
    """Require actual text, not an unresolved scripted/localised expression."""
    return bool(value.strip()) and not any(token in value for token in
        ('nbv_row_', 'nbv_source_', '[NBV', '[?', 'Unlocalized')) \
        and not re.search(r'\$[^$\r\n]+\$|\bNBV(?:Source|High|Low|Row)\w*\b', value)


def plain(value):
    return ' '.join(re.sub(r'[§\x11].', '', value).replace('\\n', '\n').split())


def icon_text(value):
    """Normalise the engine's text-icon byte, retaining the actual icon ID."""
    return plain(value).replace('\x13', '£')


def metric_name_matches(value, row, icon):
    """One private icon and the registered Chinese display name must resolve."""
    actual = icon_text(value)
    return (bool(icon) and actual == '£' + icon['icon_token'] + ' ' + metric_display_name(row)
            and re.findall(r'£([A-Za-z0-9_]+(?:\|[0-9]+)?)', actual) == [icon['icon_token']])


def analyze_revision_checks(content, index, source_manifest, icon_map, display_records):
    """Check the new row dispatch and native-source probes independently.

    A successful legacy 559-entry injection run cannot satisfy these checks.
    Missing, duplicate, malformed or unresolved new records cause a failure.
    This tests engine evaluation, not mouse interaction or rendered scrolling.
    """
    expected_cells = {}
    for page, category in enumerate(index['categories'], 1):
        for band, columns in (('high', 3), ('low', 4)):
            members = [r for r in display_records if r['category'] == category
                       and r['display_priority_band'] == band]
            for offset, row in enumerate(members):
                start = (offset // columns) * columns
                code = start + 1 if band == 'high' else -(start + 1)
                expected_cells[row['id']] = (page, code, band, offset % columns + 1)
    cell_pattern = (r'NBV_CELL page=(\d+) row=(-?\d+) band=(high|low) slot=(\d+) '
                    r'expected=(\d+) resolved=(-?\d+) name=(.*?) value=([^\r\n]*)')
    cells = []
    for page, row, band, slot, expected, resolved, name, value in re.findall(cell_pattern, content):
        cells.append(dict(page=int(page), row=int(row), band=band, slot=int(slot),
                          expected=int(expected), resolved=int(resolved), name=name, value=value))
    ids = [r['expected'] for r in cells]
    metadata_failures = [r for r in cells if r['expected'] != r['resolved'] or
                         expected_cells.get(r['expected']) != (r['page'], r['row'], r['band'], r['slot'])]
    text_failures = [r['expected'] for r in cells if not is_expanded(r['name']) or not is_expanded(r['value'])]
    metric_map = {row['id']: row for row in index['records']}
    icon_failures = [dict(id=r['expected'], actual=icon_text(r['name'])) for r in cells
                     if r['expected'] not in metric_map or not metric_name_matches(
                         r['name'], metric_map[r['expected']], icon_map.get(r['expected']))]
    new_layout_checks = [
        dict(check=str(len(display_records)) + ' selected nonempty cells logged exactly once',
             passed=len(cells) == len(expected_cells) == len(display_records)
             and len(ids) == len(set(ids)) and set(ids) == set(expected_cells),
             actual_count=len(cells), missing_ids=sorted(set(expected_cells) - set(ids)),
             unexpected_ids=sorted(set(ids) - set(expected_cells))),
        dict(check='Cell page, encoded row, band, slot and resolved ID match catalog',
             passed=bool(cells) and not metadata_failures, failures=metadata_failures[:20]),
        dict(check='All cell names and values expanded', passed=bool(cells) and not text_failures,
             failed_ids=text_failures),
        dict(check='All ' + str(len(display_records)) + ' selected cell names retain their catalog text and exact private icon ID',
             passed=bool(cells) and not icon_failures, failures=icon_failures),
    ]
    # DOTALL is intentional: source fragments start with a newline, and tooltips
    # can contain multiple native contributions. Explicit end markers bound them.
    source_pattern = (r'NBV_SOURCE source=([A-Za-z0-9_]+) phase=(before|absent|restored) '
                      r'value=(' + NUMBER + r') text=(.*?) END_SOURCE')
    source_logs = {}
    source_count = 0
    for source_id, phase, value, text in re.findall(source_pattern, content, re.S):
        source_count += 1
        source_logs.setdefault(source_id, {}).setdefault(phase, []).append(dict(value=float(value), text=text))
    tooltip_logs = {}
    for metric_id, text in re.findall(r'NBV_TOOLTIP id=(\d+) text=(.*?) END_TOOLTIP', content, re.S):
        tooltip_logs.setdefault(int(metric_id), []).append(text)
    source_checks, tooltip_checks = [], []
    expected_metric_ids = set()
    for source_id, key, expected_delta, source_name in SOURCE_PROBES:
        bindings = [r for r in source_manifest.get('records', [])
                    if r['source_id'] == source_id and r['key'] == key]
        binding = bindings[0] if len(bindings) == 1 else None
        phases = source_logs.get(source_id, {})
        phases_complete = set(phases) == {'before', 'absent', 'restored'} and all(len(v) == 1 for v in phases.values())
        phase_values = {name: values[0] for name, values in phases.items() if len(values) == 1}
        before, absent, restored = (phase_values.get(name) for name in ('before', 'absent', 'restored'))
        delta = round(before['value'] - absent['value'], 6) if before and absent else None
        manifest_matches = bool(binding) and abs(float(binding['value_literal']) - expected_delta) <= 0.000001
        texts_valid = bool(before and absent and restored) and (
            is_expanded(before['text']) and is_expanded(restored['text'])
            and not plain(absent['text']) and source_name in plain(before['text'])
            and source_name in plain(restored['text']) and plain(before['text']) == plain(restored['text'])
            and all('£nbv_mi_' not in icon_text(p['text']) for p in (before, absent, restored)))
        values_valid = bool(before and absent and restored) and delta is not None \
            and abs(delta - expected_delta) <= 0.0002 and abs(restored['value'] - before['value']) <= 0.0002
        source_checks.append(dict(source_id=source_id, key=key, expected_delta=expected_delta, actual_delta=delta,
                                  passed=phases_complete and manifest_matches and texts_valid and values_valid,
                                  manifest_matches=manifest_matches, phases_complete=phases_complete,
                                  source_text_valid=texts_valid, restored_value_matches=values_valid,
                                  phases=phase_values))
        metric_id = binding['metric_id'] if binding else None
        if metric_id is not None:
            expected_metric_ids.add(metric_id)
        captures = tooltip_logs.get(metric_id, [])
        tooltip = captures[0] if len(captures) == 1 else ''
        has_source = bool(restored) and bool(plain(restored['text'])) and plain(restored['text']) in plain(tooltip)
        forbidden = [term for term in ('作用项', '公式', '其他来源', '无法拆分') if term in tooltip]
        metric = metric_map.get(metric_id)
        icon = icon_map.get(metric_id)
        expected_title = ('£' + icon['icon_token'] + ' ' + metric['name'] + ' ') if metric and icon else ''
        icon_title_valid = bool(expected_title) and icon_text(tooltip).startswith(expected_title) \
            and re.findall(r'£(nbv_mi_[A-Za-z0-9_]+(?:\|[0-9]+)?)', icon_text(tooltip)) == [icon['icon_token']]
        tooltip_checks.append(dict(metric_id=metric_id, source_id=source_id, count=len(captures),
                                   passed=len(captures) == 1 and is_expanded(tooltip) and has_source
                                   and source_name in plain(tooltip) and not forbidden and icon_title_valid,
                                   correct_source_present=has_source, icon_title_valid=icon_title_valid,
                                   forbidden_text=forbidden, text=tooltip))
    source_coverage = source_count == 12 and set(source_logs) == {r[0] for r in SOURCE_PROBES}
    tooltip_coverage = sum(map(len, tooltip_logs.values())) == 4 and set(tooltip_logs) == expected_metric_ids \
        and len(expected_metric_ids) == 4
    return dict(new_layout_count=len(cells), cell_expected_count=len(expected_cells),
                new_layout_checks=new_layout_checks,
                icon_cell_verified_count=len(cells) - len(icon_failures),
                new_layout_passed=all(r['passed'] for r in new_layout_checks),
                source_log_count=source_count, source_log_coverage=source_coverage,
                source_checks=source_checks, source_passed=source_coverage and all(r['passed'] for r in source_checks),
                tooltip_log_coverage=tooltip_coverage, tooltip_checks=tooltip_checks,
                tooltip_passed=tooltip_coverage and all(r['passed'] for r in tooltip_checks))


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--promote-reads', action='store_true', help='Mark only successfully injected country reads in the local implementation index.')
    args = parser.parse_args()
    log_path = WORK / 'profile/logs/game.log'
    error_path = WORK / 'profile/logs/error.log'
    content = log_path.read_text(encoding='utf-8-sig', errors='replace')
    errors = error_path.read_text(encoding='utf-8-sig', errors='replace')
    before = {k: float(v) for k, v in re.findall(r'NBV_BEFORE ([\w]+)=([+\-]?[0-9.]+)', content)}
    after = {k: float(v) for k, v in re.findall(r'NBV_AFTER ([\w]+)=([+\-]?[0-9.]+)', content)}
    isolated_before = {k: float(v) for k, v in re.findall(r'NBV_ISOLATED_BEFORE ([\w]+)=([+\-]?[0-9.]+)', content)}
    isolated_after = {k: float(v) for k, v in re.findall(r'NBV_ISOLATED_AFTER ([\w]+)=([+\-]?[0-9.]+)', content)}
    assertions = dict(re.findall(r'NBV_ASSERT (\w+) (PASS|FAIL)', content))
    filter_counts = {int(page): (int(high), int(low)) for page, high, low in re.findall(r'NBV_FILTER_COUNTS page=(\d) high=(\d+) low=(\d+)', content)}
    dispatch_records = re.findall(r'NBV_DISPATCH (\d+) name=(.*?) value=([^\r\n]*)', content)
    dispatch = {int(ident): dict(name=name, value=value) for ident, name, value in dispatch_records}
    index_path = ROOT / 'tools/data/metric-index.json'
    index = json.loads(index_path.read_text(encoding='utf-8'))
    display_records = load_display_records()
    display_hash = display_signature(display_records)
    display_logs = re.findall(r'NBV_DISPLAY_LAYOUT count=(\d+) sha256=([0-9a-f]{64})', content)
    display_provenance_passed = display_logs == [(str(len(display_records)), display_hash)]
    complete = 'NBV_SMOKE_END' in content
    if not complete:
        print(json.dumps(dict(completed=False, status='Game test is still loading or incomplete; previous completed report is preserved.')))
        return 1
    source_manifest = json.loads((ROOT / 'tools/data/source-display-manifest.json').read_text(encoding='utf-8'))
    icon_path = ROOT / 'tools/data/modifier-icon-bindings.json'
    icon_manifest = json.loads(icon_path.read_text(encoding='utf-8'))
    icon_map = {row['id']: row for row in icon_manifest['records']}
    revision_checks = analyze_revision_checks(content, index, source_manifest, icon_map, display_records)
    filter_checks = []
    for page, category in enumerate(index['categories'], 1):
        expected = tuple(sum(r['category'] == category and r['display_priority_band'] == band
                             and (not r['runtime_read_validated'] or abs(before.get(r['key'], 0)) > 0.00001)
                             for r in display_records) for band in ('high', 'low'))
        filter_checks.append(dict(page=page, expected=expected, actual=filter_counts.get(page), passed=filter_counts.get(page) == expected))
    dispatch_name_failures = [dict(id=row['id'], actual=icon_text(dispatch.get(row['id'], {}).get('name', '')))
                              for row in index['records'] if not metric_name_matches(
                                  dispatch.get(row['id'], {}).get('name', ''), row, icon_map.get(row['id']))]
    dispatch_passed = (len(dispatch_records) == len(dispatch) == 559
        and set(dispatch) == {r['id'] for r in index['records']} and not dispatch_name_failures
        and all(is_expanded(v['name']) and is_expanded(v['value']) for v in dispatch.values()))
    rows = []
    for row in index['records']:
        key = row['key']
        a, b = (isolated_before, isolated_after) if key in isolated_before and key in isolated_after else (before, after)
        delta = round(b[key] - a[key], 6) if key in a and key in b else None
        verified = complete and delta is not None and abs(delta - 0.125) <= 0.0002
        rows.append(dict(key=key, before=a.get(key), after=b.get(key), delta=delta,
                         injection_mode='isolated' if a is isolated_before else 'combined',
                         injected=0.125, read_verified=verified,
                         validation_scope='Direct country modifier read after a test-only country idea injection; not a UI/color or all-source validation.'))
    nbv_keys = {r['key'] for r in index['records']} | set(source_manifest.get('synchronized_source_tokens', []))
    nbv_errors = [line for line in errors.splitlines() if re.search(r'nbv|National Buff', line, re.I)
                  or any(('Token ' + key + ' is a dynamic token') in line for key in nbv_keys)]
    report = dict(game_version='1.19.3.0', mod_version=VERSION, completed=complete,
                  display_count=len(display_records), display_layout_sha256=display_hash,
                  display_layout_manifest_sha256=hashlib.sha256((ROOT / 'tools/data/display-layout.json').read_bytes()).hexdigest(),
                  display_layout_provenance_passed=display_provenance_passed,
                  display_layout_log_records=[dict(count=int(count), sha256=sha256) for count, sha256 in display_logs],
                  assertions=assertions, before_count=len(before), after_count=len(after),
                  filter_checks=filter_checks, dispatch_count=len(dispatch), dispatch_passed=dispatch_passed,
                  dispatch_log_count=len(dispatch_records), dispatch_name_failures=dispatch_name_failures,
                  icon_dispatch_verified_count=559 - len(dispatch_name_failures),
                  icon_manifest_sha256=hashlib.sha256(icon_path.read_bytes()).hexdigest(),
                  verified_read_count=sum(r['read_verified'] for r in rows),
                  nbv_errors=nbv_errors, all_error_lines=errors.splitlines(),
                  game_log_sha256=hashlib.sha256(log_path.read_bytes()).hexdigest(),
                  error_log_sha256=hashlib.sha256(error_path.read_bytes()).hexdigest(),
                  rows=rows, ui_interaction_verified=False, cross_tag_tested=False)
    report.update(revision_checks)
    from source_smoke_probes import analyze as analyze_expanded_sources
    report.update(analyze_expanded_sources(content))
    from dynamic_extended_smoke_probes import analyze as analyze_dynamic_sources
    report.update(analyze_dynamic_sources(content))
    from special_source_smoke_probes import analyze as analyze_special_sources
    report.update(analyze_special_sources(content))
    leader_names = re.findall(r'NBV_LEADER_NAME name=(.*?) END_LEADER_NAME', content)
    leader_source = next((r for r in report['source_checks'] if r['source_id'] == 'GER_der_fuhrer'), {})
    leader_text = plain(leader_source.get('phases', {}).get('restored', {}).get('text', ''))
    leader_name = plain(leader_names[0]) if len(leader_names) == 1 else ''
    report['leader_name_check'] = dict(name=leader_name, text=leader_text,
        passed=bool(leader_name) and (leader_name + '：元首：') in leader_text)
    from faction_smoke_probes import analyze as analyze_faction_sources
    report.update(analyze_faction_sources(content))
    format_logs = dict(re.findall(r'NBV_FORMAT probe=(\w+) text=(.*?) END_FORMAT', content))
    report['percentage_point_checks'] = [dict(name=k, text=plain(format_logs.get(k, '')),
        passed=plain(format_logs.get(k, '')).strip() == v) for k, v in
        [('positive', '+15.0%'), ('negative', '-15.0%'), ('fraction', '+0.5%')]]
    edge_logs = {key: value.strip() for key, value in re.findall(r'NBV_EDGE source=(\w+) text=(.*?) END_EDGE', content, re.S)}
    precision_text = plain(edge_logs.get('ENG_mi6_ns', ''))
    single_line_text = plain(edge_logs.get('army_guerilla_organizer_1', ''))
    report['source_presentation_checks'] = [
        dict(name='nonzero_contribution_precision', passed='0.05' in precision_text,
             text=precision_text),
        dict(name='single_line_source_name', passed=bool(single_line_text) and '\n' not in edge_logs.get('army_guerilla_organizer_1', '').replace('\\n', '\n')
             and '2.0%' in single_line_text, text=single_line_text),
    ]
    required_assertions = {'first_open', 'remember_page'} | {'page_' + str(i) for i in range(1, 7)}
    report['assertions_passed'] = required_assertions <= set(assertions) and all(v == 'PASS' for v in assertions.values())
    report['all_checks_passed'] = (complete and display_provenance_passed and report['assertions_passed']
        and len(before) == len(after) == 559 and report['verified_read_count'] == 559
        and all(r['passed'] for r in filter_checks) and dispatch_passed and not nbv_errors
        and report['new_layout_passed'] and report['source_passed'] and report['tooltip_passed']
        and all(check['passed'] for check in report['source_presentation_checks'])
        and report['expanded_sources_passed'] and report['faction_sources_passed']
        and report['dynamic_extended_passed'] and report['leader_name_check']['passed']
        and report['special_sources_passed']
        and all(r['passed'] for r in report['percentage_point_checks']))
    out = ROOT / 'tools/data/engine-validation.json'
    write(out, json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if args.promote_reads:
        assert complete and len(before) == len(after) == 559, 'Incomplete run: refusing to promote validation.'
        assert not nbv_errors, 'NBV engine errors remain: refusing to promote validation.'
        assert display_provenance_passed, 'Display selection/order differs from the prepared run: refusing to promote validation.'
        assert report['new_layout_passed'] and report['source_passed'] and report['tooltip_passed'], \
            '0.1.1 layout or source probes failed: refusing to promote validation.'
        verified_keys = {r['key'] for r in rows if r['read_verified']}
        for row in index['records']:
            row['runtime_read_validated'] = row['key'] in verified_keys
            row['runtime_validation_source'] = 'tools/data/engine-validation.json'
        index['runtime_validation_policy'] = 'Only matching +0.125 country-idea injection deltas are promoted; unchanged, clamped, and missing reads remain unverified.'
        write(index_path, json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('rows', 'all_error_lines')}, ensure_ascii=False))
    return 0 if report['all_checks_passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
