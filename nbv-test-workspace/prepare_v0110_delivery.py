# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

workspace = Path(r'D:\projects\hoi4_mod\1')
root = workspace / 'hoi4-national-buff'
work = workspace / 'nbv-test-workspace'
evidence = work / 'release-v019-evidence'
evidence.mkdir(exist_ok=True)
for filename in ('engine-validation.json', 'static-validation.json', 'delivery-audit.json', 'display-layout.json'):
    target = evidence / filename
    if not target.exists():
        shutil.copyfile(root / 'tools/data' / filename, target)
layout = json.loads((evidence / 'display-layout.json').read_text(encoding='utf-8'))
source = Path(layout['imported_from'])
snapshot = root / 'tools/data/display-order.md'
backup = evidence / 'display-order.md'
if not backup.exists():
    assert source.read_bytes() == snapshot.read_bytes()
    backup.write_bytes(source.read_bytes())
text = backup.read_text(encoding='utf-8-sig')
old = '- 核研究专项计划速度\n'
assert text.count(old) == 1
new = text.replace(old, old + '- 地区最大工厂数（固定值）\n')
source.write_text(new, encoding='utf-8')
installer = root / 'install-local.ps1'
raw = installer.read_bytes()
installer.write_bytes(raw.replace(b'0.1.9', b'0.1.10'))
runner = work / 'run-v019.ps1'
(work / 'run-v0110.ps1').write_bytes(runner.read_bytes().replace(b'v019', b'v0110'))
with zipfile.ZipFile(workspace / 'dist/national-buff-ui-0.1.9.zip') as archive:
    unchanged = []
    for name in archive.namelist():
        rel = name.removeprefix('hoi4-national-buff/')
        if rel == 'tools/data/metric-index.json' or rel.endswith('-bindings.json'):
            assert archive.read(name) == (root / rel).read_bytes(), rel
            unchanged.append(rel)
print(json.dumps({'source': str(source), 'unchanged_binding_tables': len(unchanged)}, ensure_ascii=False))
