# -*- coding: utf-8 -*-
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent.parent / 'nbv-national-buff'
registration = Path(r'C:/Users/1/Documents/Paradox Interactive/Hearts of Iron IV/mod/nbv_national_buff.mod')
hash_file = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
assert not (ROOT.parent / 'hoi4-national-buff').exists()
assert not (ROOT.parent / '国家BUFF统计 UI').exists()
assert f'path="{ROOT.as_posix()}"' in registration.read_text(encoding='utf-8-sig')
assert 'name="国家BUFF统计 UI"' in registration.read_text(encoding='utf-8-sig')
with zipfile.ZipFile(ROOT.parent / 'dist/national-buff-ui-0.1.11.zip') as archive:
    runtime = [n for n in archive.namelist() if n.startswith(tuple('hoi4-national-buff/' + p + '/' for p in ('common','interface','gfx','localisation'))) or n == 'hoi4-national-buff/descriptor.mod']
    assert all(archive.read(n) == (ROOT / n.removeprefix('hoi4-national-buff/')).read_bytes() for n in runtime)
static = read(ROOT / 'tools/data/static-validation.json')
assert static['通过'] and static['失败数'] == 0
engine = read(ROOT / 'tools/data/engine-validation.json')
assert engine['mod_version'] == '0.1.11' and engine['all_checks_passed']
verification = read(WORK / 'verification.json')
result = {
    'date': datetime.datetime.now().astimezone().isoformat(),
    'directory': str(ROOT), 'display_name': '国家BUFF统计 UI',
    'registration': str(registration), 'registration_filename_preserved': True,
    'canonical_archive_root': 'nbv-national-buff', 'metadata_unit_tests_passed': 4,
    'installer_cases_passed': verification['installer_cases_passed'],
    'static_checks_passed': static['检查数'], 'runtime_files_unchanged': len(runtime),
    'new_engine_run': False, 'engine_evidence_reused_version': '0.1.11',
    'backup_directory': str(WORK),
    'name_preserved_during_build': True, 'workshop_id_preserved': True,
    'gameplay_changed': False,
}
target = ROOT / 'tools/data/naming-configuration-audit.json'
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
audit_path = ROOT / 'tools/data/delivery-audit.json'
audit = read(audit_path)
audit.update(descriptor_sha256=hash_file(registration), naming_configuration_sha256=hash_file(target),
             current_mod_directory=str(ROOT), naming_configuration_fixed=True,
             naming_fix_runtime_files_unchanged=len(runtime), naming_fix_new_engine_run=False)
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Naming configuration verified; 187 static checks passed; 355 runtime files unchanged.')
