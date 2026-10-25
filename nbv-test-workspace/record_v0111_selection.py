# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent / 'hoi4-national-buff'
WORK = ROOT.parent / 'nbv-test-workspace'
data = ROOT / 'tools/data'
layout = json.loads((data / 'display-layout.json').read_text(encoding='utf-8'))
added_ids = [2, 43, 275, 234, 241, 379, 544, 542]
changed_ids = set(added_ids + [484])
records = [row for row in layout['records'] if row['id'] in changed_ids]
assert len(records) == 9 and all(row['display_priority_band'] == 'low' for row in records)
keys = {r['key'] for r in layout['records']}
counts = {k: 0 for k in keys}
for path in data.glob('*source-bindings.json'):
    table = json.loads(path.read_text(encoding='utf-8'))
    for key in keys:
        counts[key] += len(table.get('by_modifier', {}).get(key, []))
assert (sum(v > 0 for v in counts.values()), sum(counts.values())) == (514, 28931)
audit_path = data / 'same-name-modifier-audit.json'
audit = json.loads(audit_path.read_text(encoding='utf-8'))
audit['implementation_v0111'] = {
    'version': '0.1.11', 'new_display_ids': added_ids, 'moved_existing_ids': [484],
    'display_count': 528, 'records': records,
    'historical_audit_retained': True,
    'note': 'The earlier homonym findings are a 0.1.10 audit snapshot; these eight requested omissions are now displayed. Existing air experience percentage moved from Common to Other, without duplication.'
}
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
doc = ROOT.parent / '同名修正词条核查.md'
text = doc.read_text(encoding='utf-8')
marker = '# 同名修正词条核查\n'
note = '\n**0.1.11 执行更新：** 已按用户选择补入 8 项：陆军师组织度固定值、陆军／海军经验增长百分比、堑壕上限百分比、旧版加密／解密百分比、可征募人口比例加成、宗主国对附属国的人力要求。已有空军经验增长百分比已移至“其他修正”并明确名称。9 项均位于对应其他区末尾，当前共 528 项。\n\n以下保留 **0.1.10 审计快照**及当时的遗漏分类；上述 8 项已完成接入，不再属于当前未显示项。\n'
assert text.startswith(marker) and '0.1.11 执行更新' not in text
doc.write_text(text.replace(marker, marker + note, 1), encoding='utf-8')
files = sorted([p for s in ('common', 'interface', 'localisation') for p in (ROOT / s).rglob('*') if p.is_file()] + [ROOT / 'descriptor.mod'])
(WORK / 'v0111-runtime-hashes.json').write_text(json.dumps({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, indent=2), encoding='utf-8')
print('Selection recorded: 8 added, 1 moved; source candidates 514/528, contributions 28931.')
