# -*- coding: utf-8 -*-
"""Apply only the requested selections, retaining all other user order."""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parent.parent / 'hoi4-national-buff'
WORK = ROOT.parent / 'nbv-test-workspace'
data = ROOT / 'tools/data'
evidence = WORK / 'release-v0110-evidence'
evidence.mkdir(exist_ok=True)
for filename in ('engine-validation.json', 'static-validation.json', 'delivery-audit.json', 'display-layout.json', 'display-order.md', 'same-name-modifier-audit.json'):
    if not (evidence / filename).exists():
        shutil.copyfile(data / filename, evidence / filename)
old = json.loads((evidence / 'display-layout.json').read_text(encoding='utf-8'))
source = Path(old['imported_from'])
baseline = (evidence / 'display-order.md').read_bytes()
assert source.read_bytes() == baseline, 'User list changed; re-evaluate before editing.'
additions = {
    '政治': ['可征募人口（比例加成）', '宗主国对附属国的人力要求'],
    '陆军': ['陆军师组织度（固定值）', '陆军经验增长（百分比）', '堑壕上限（百分比）'],
    '海军': ['海军经验增长（百分比）'],
    '空军': ['空军经验增长（百分比）'],
    '情报': ['旧版加密（百分比）', '旧版解密（百分比）'],
}
lines = baseline.decode('utf-8-sig').splitlines()
assert sum(line.strip() == '- 空军经验增长' for line in lines) == 2
lines = [line for line in lines if line.strip() != '- 空军经验增长']
for page, names in additions.items():
    start = lines.index('# ' + page)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith('# ')), len(lines))
    low = next(i for i in range(start + 1, end) if lines[i].strip() == '## 其他修正')
    insert_at = max(i for i in range(low + 1, end) if lines[i].strip().startswith('- ') and lines[i].strip()[1:].strip()) + 1
    lines[insert_at:insert_at] = ['- ' + name for name in names]
source.write_text('\n'.join(lines) + '\n', encoding='utf-8')
installer = ROOT / 'install-local.ps1'
installer.write_bytes(installer.read_bytes().replace(b'0.1.10', b'0.1.11'))
(WORK / 'run-v0111.ps1').write_bytes((WORK / 'run-v0110.ps1').read_bytes().replace(b'v0110', b'v0111'))
print(json.dumps({'source': str(source), 'new_keys': 8, 'existing_air_key_moved': 484, 'append': additions}, ensure_ascii=False))
