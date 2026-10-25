# -*- coding: utf-8 -*-
from pathlib import Path
import json
import subprocess
import zipfile

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent.parent / 'nbv-national-buff'
fixture = WORK / 'installer-fixture'
fixture.mkdir(exist_ok=True)
installer = fixture / 'install-local.ps1'
installer.write_bytes((ROOT / 'install-local.ps1').read_bytes())
descriptor = fixture / 'descriptor.mod'
base = 'name="自定义中文显示名"\nversion="0.1.11"\nsupported_version="1.19.*"\npicture="preview.png"\ntags={ "Utilities" }\n'
descriptor.write_text(base, encoding='utf-8')
profile = WORK / 'isolated-user-directory'
registration = profile / 'mod/nbv_national_buff.mod'


def install(success=True):
    result = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(installer), '-UserDirectory', str(profile)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert (result.returncode == 0) == success, result.stderr.decode('utf-8', errors='replace')


install()
text = registration.read_text(encoding='utf-8-sig')
assert 'name="自定义中文显示名"' in text and 'picture="preview.png"' in text
assert f'path="{fixture.as_posix()}"' in text
registration.write_text(text + 'remote_file_id="1234567890"\n', encoding='utf-8')
install()
assert 'remote_file_id="1234567890"' in registration.read_text(encoding='utf-8')
before = registration.read_bytes()
descriptor.write_text(base + 'remote_file_id="9876543210"\n', encoding='utf-8')
install(False)
assert registration.read_bytes() == before
descriptor.write_text(base.replace('0.1.11', '0.1.12') + 'remote_file_id="1234567890"\n', encoding='utf-8')
install()
text = registration.read_text(encoding='utf-8')
assert 'version="0.1.12"' in text and 'remote_file_id="1234567890"' in text
assert 'name="自定义中文显示名"' in text
with zipfile.ZipFile(ROOT.parent / 'dist/national-buff-ui-0.1.11.zip') as archive:
    runtime_names = [name for name in archive.namelist() if name.startswith(tuple('hoi4-national-buff/' + part + '/' for part in ('common','interface','gfx','localisation'))) or name == 'hoi4-national-buff/descriptor.mod']
    changed = [name for name in runtime_names if archive.read(name) != (ROOT / name.removeprefix('hoi4-national-buff/')).read_bytes()]
assert not changed, changed
result = {'installer_cases_passed': 4, 'production_runtime_files_unchanged': len(runtime_names), 'runtime_changed': changed}
(WORK / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
