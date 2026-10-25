# -*- coding: utf-8 -*-
"""Check the fixed-slot addition against the previous delivered release."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent / 'hoi4-national-buff'
PROFILE = Path(r'C:/Users/1/Documents/Paradox Interactive/Hearts of Iron IV')
GAME = Path(r'E:/Steam/steamapps/common/Hearts of Iron IV')


def h(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


runtime = read(WORK / 'v0110-runtime-hashes.json')
assert all(h(ROOT / rel) == checksum for rel, checksum in runtime.items())
engine = read(ROOT / 'tools/data/engine-validation.json')
assert engine['mod_version'] == '0.1.10' and engine['all_checks_passed']
assert engine['new_layout_count'] == 520 and engine['verified_read_count'] == 559
cleanup = read(WORK / 'cleanup-v0110.json')
assert all(cleanup[k] for k in ('completed', 'launcher_restored', 'playset_unchanged'))
launch = read(WORK / 'launch-v0110.json')
assert h(GAME / 'launcher-settings.json').upper() == launch['original_hash'].upper()
assert h(PROFILE / 'dlc_load.json').upper() == launch['playset_hash'].upper()
descriptor = PROFILE / 'mod/nbv_national_buff.mod'
descriptor_text = descriptor.read_text(encoding='utf-8-sig')
assert 'version="0.1.10"' in descriptor_text
assert f'path="{ROOT.as_posix()}"' in descriptor_text
current = read(ROOT / 'tools/data/display-layout.json')
assert current['record_count'] == 520
assert Path(current['imported_from']).read_bytes() == (ROOT / 'tools/data/display-order.md').read_bytes()
with zipfile.ZipFile(WORK.parent / 'dist/national-buff-ui-0.1.9.zip') as archive:
    old = json.loads(archive.read('hoi4-national-buff/tools/data/display-layout.json'))
    fields = ('id', 'key', 'name', 'category', 'display_priority_band', 'grid_columns', 'display_order')
    project = lambda rows: [{k: r[k] for k in fields} for r in rows]
    assert project([r for r in current['records'] if r['id'] != 142]) == project(old['records'])
    added = next(r for r in current['records'] if r['id'] == 142)
    assert added['name'] == '地区最大工厂数（固定值）'
    assert (added['category'], added['display_priority_band'], added['display_order']) == ('工业', 'low', 77)
    unchanged = []
    for name in archive.namelist():
        rel = name.removeprefix('hoi4-national-buff/')
        if rel == 'tools/data/metric-index.json' or rel.endswith('-bindings.json'):
            assert archive.read(name) == (ROOT / rel).read_bytes(), rel
            unchanged.append(rel)
    runtime_diff = [rel for rel in runtime if archive.read('hoi4-national-buff/' + rel) != (ROOT / rel).read_bytes()]
assert set(runtime_diff) == {
    'descriptor.mod', 'common/scripted_effects/nbv_effects.txt', 'common/scripted_triggers/nbv_triggers.txt',
    'localisation/english/nbv_l_english.yml', 'localisation/simp_chinese/nbv_l_simp_chinese.yml'
}, runtime_diff
audit = read(ROOT / 'tools/data/delivery-audit.json')
audit.pop('runtime_diff_from_v018', None)
audit.update(
    version='0.1.10', date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    descriptor_sha256=h(descriptor), source_manifest_sha256=h(ROOT / 'source-manifest.json'),
    display_layout_sha256=h(ROOT / 'tools/data/display-layout.json'), display_count=520,
    engine_report_sha256=h(ROOT / 'tools/data/engine-validation.json'),
    engine_test_version='0.1.10', engine_checks_passed=True,
    launcher_sha256=h(GAME / 'launcher-settings.json'), launcher_restored=True,
    user_playset_sha256=h(PROFILE / 'dlc_load.json'), user_playset_modified_by_install=False,
    runtime_files_changed_after_engine_test=False, runtime_diff_from_v019=runtime_diff,
    source_coverage_changes_in_this_release=False, selected_source_coverage_count=506,
    selected_source_contribution_count=27965, registry_and_binding_tables_unchanged=unchanged,
    other_519_selection_and_order_unchanged=True, new_display_ids=[142],
    homonym_audit_sha256=h(ROOT / 'tools/data/same-name-modifier-audit.json'),
)
(ROOT / 'tools/data/delivery-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('v0.1.10 verified: installed, 520 cells and 559 reads passed, settings restored, previous selection order and source bindings unchanged.')
print('Runtime difference from v0.1.9:', runtime_diff)
