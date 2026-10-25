"""Read-only independent audit of the installed HOI4 modifier registry."""
import collections
import json
import re
from pathlib import Path
from zipfile import ZipFile

GAME = Path(r'E:\Steam\steamapps\common\Hearts of Iron IV')
doc = GAME / 'documentation/modifiers_documentation.md'
lines = doc.read_text(encoding='utf-8-sig').splitlines()
records = []
for i, line in enumerate(lines):
    if not line.startswith('## '):
        continue
    heading = re.sub(r'<span[^>]*></span>', '', line[3:]).strip()
    if heading.startswith('Modifiers for scope') or heading == 'Table of Content':
        continue
    block = []
    for j in range(i + 1, len(lines)):
        if lines[j].startswith('## '):
            break
        block.append(lines[j])
    body = '\n'.join(block)
    def field(name):
        match = re.search(r'^\* \*\*' + name + r'\*\*: (.*)$', body, re.M)
        return match.group(1) if match else ''
    types = field('Modified types').split(', ') if field('Modified types') else []
    placeholders = re.findall(r'<[^>]+>', heading)
    if placeholders:
        assert len(placeholders) == 1 and types, (heading, types)
    keys = [heading.replace(placeholders[0], x) for x in types] if placeholders else [heading]
    records.append(dict(heading=heading, line=i+1, template=bool(placeholders), types=types,
                        keys=keys, description=field('Description'), categories=field('Categories')))
origin = collections.defaultdict(list)
for record in records:
    for key in record['keys']:
        origin[key].append({'line':record['line'], 'heading':record['heading']})
custom = []
for path in (GAME / 'common/modifier_definitions').glob('*.txt'):
    for lineno, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        match = re.match(r'^(\w+)\s*=\s*\{', line)
        if match:
            custom.append(dict(key=match.group(1), file=str(path.relative_to(GAME)), line=lineno,
                               in_documentation=match.group(1) in origin))
archives = []
for path in GAME.rglob('*.zip'):
    try:
        with ZipFile(path) as z:
            scripts = [x.filename for x in z.infolist() if re.search(r'(^|/)(common|events|history)/.*\.(txt|lua)$', x.filename)]
            archives.append(dict(path=str(path.relative_to(GAME)), files=len(z.infolist()),
                                 script_files=len(scripts), examples=scripts[:5]))
    except Exception as exc:
        archives.append(dict(path=str(path.relative_to(GAME)), error=str(exc)))
result = dict(
    headings=len(records), fixed_headings=sum(not r['template'] for r in records),
    template_headings=sum(r['template'] for r in records),
    expanded_template_occurrences=sum(len(r['keys']) for r in records if r['template']),
    expanded_all_occurrences=sum(len(r['keys']) for r in records),
    unique_documented_keys=len(origin),
    duplicate_keys={k:v for k,v in origin.items() if len(v)>1},
    duplicate_template_headings={k:v for k,v in collections.Counter(r['heading'] for r in records if r['template']).items() if v>1},
    templates=[dict(heading=r['heading'], line=r['line'], count=len(r['keys'])) for r in records if r['template']],
    custom=custom,
    total_union=len(set(origin)|{x['key'] for x in custom}),
    with_description=sum(bool(r['description']) for r in records),
    without_description=sum(not r['description'] for r in records),
    archives=archives,
    script_roots=[dict(root=root, txt_count=len(list((GAME/root).rglob('*.txt')))) for root in ('common','events','history','dlc','integrated_dlc')],
    version=json.loads((GAME/'launcher-settings.json').read_text(encoding='utf-8-sig'))['version'],
)
print(json.dumps(result, ensure_ascii=False, indent=2))
