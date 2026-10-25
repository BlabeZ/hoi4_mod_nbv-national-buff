"""Verify v0.1.9 release state; write delivery evidence, never change gameplay."""
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


runtime = read(WORK / 'v019-runtime-hashes.json')
changed = [rel for rel, checksum in runtime.items() if h(ROOT / rel) != checksum]
assert not changed, changed
engine = read(ROOT / 'tools/data/engine-validation.json')
assert engine['mod_version'] == '0.1.9' and engine['all_checks_passed']
cleanup = read(WORK / 'cleanup-v019.json')
assert all(cleanup[k] for k in ('completed', 'launcher_restored', 'playset_unchanged'))
launch = read(WORK / 'launch-v019.json')
assert h(GAME / 'launcher-settings.json').upper() == launch['original_hash'].upper()
assert h(PROFILE / 'dlc_load.json').upper() == launch['playset_hash'].upper()
descriptor = PROFILE / 'mod/nbv_national_buff.mod'
assert 'version="0.1.9"' in descriptor.read_text(encoding='utf-8-sig')

# Only the entry icon position/comment and descriptor version change at runtime.
with zipfile.ZipFile(WORK.parent / 'dist/national-buff-ui-0.1.8.zip') as archive:
    runtime_diff = [rel for rel in runtime if archive.read('hoi4-national-buff/' + rel) != (ROOT / rel).read_bytes()]
assert set(runtime_diff) == {'descriptor.mod', 'interface/nbv.gui'}, runtime_diff
old_gui = archive_gui = None
with zipfile.ZipFile(WORK.parent / 'dist/national-buff-ui-0.1.8.zip') as archive:
    old_gui = archive.read('hoi4-national-buff/interface/nbv.gui').decode('utf-8')
new_gui = (ROOT / 'interface/nbv.gui').read_text(encoding='utf-8')
expected = old_gui.replace('            position = { x = 11 y = 8 }',
                          '            # Native ledger frame is 55x41; centre it inside the 71x71 button.\n'
                          '            position = { x = 11 y = 18 }')
assert new_gui == expected

audit = read(ROOT / 'tools/data/delivery-audit.json')
audit.update(
    version='0.1.9', date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    descriptor_sha256=h(descriptor), source_manifest_sha256=h(ROOT / 'source-manifest.json'),
    engine_report_sha256=h(ROOT / 'tools/data/engine-validation.json'),
    engine_test_version='0.1.9', engine_checks_passed=True,
    launcher_sha256=h(GAME / 'launcher-settings.json'), launcher_restored=True,
    user_playset_sha256=h(PROFILE / 'dlc_load.json'), user_playset_modified_by_install=False,
    runtime_files_changed_after_engine_test=False, runtime_diff_from_v018=runtime_diff,
    sidebar_icon_centered=True, sidebar_static_known_layout_reservation=True,
    sidebar_runtime_collision_detection=False, tno_compatibility=False,
    source_coverage_changes_in_this_release=False,
    sidebar_placement_sha256=h(ROOT / 'tools/data/sidebar-placement.json'),
    ui_visual_verified=False, third_party_combined_game_launch_tested=False,
)
(ROOT / 'tools/data/delivery-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('v0.1.9 verified: installed, engine passed, runtime hash unchanged after test, original settings restored.')
print('Runtime difference from v0.1.8:', runtime_diff)
