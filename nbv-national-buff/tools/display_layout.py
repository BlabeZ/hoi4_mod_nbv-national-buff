"""Build the editable GUI selection/order without renumbering modifier IDs.

The 559-record registry remains authoritative for names, values, icons and
source bindings. The Markdown controls only which records the GUI lists and
their page, band and order. Duplicate modifier keys keep their first position.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import re
from display_names import metric_display_name

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tools/data'
PAGES = ['政治', '工业', '陆军', '海军', '空军', '情报']
BANDS = {'常用': 'high', '其他修正': 'low'}
SOURCE_NAME = 'display-order.md'
NORMALIZATIONS = {
    # Confirmed by the user on 2026-10-25: this line accidentally joined two items.
    '敌方特工情报获取率加强意识形态任务成果': ['敌方特工情报获取率', '加强意识形态任务成果'],
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_markdown(text, registry):
    by_name = defaultdict(list)
    for record in registry:
        by_name[record['name']].append(record)
        alias = metric_display_name(record)
        if alias != record['name']:
            by_name[alias].append(record)
    records, duplicates, normalized, ambiguous = [], [], [], []
    seen, pages, sections = {}, [], []
    page = band = None
    empty_bullets = 0
    section_counts = Counter()
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith('# '):
            page, band = line[2:].strip(), None
            if page not in PAGES or page in pages:
                raise ValueError(f'Invalid/repeated page at line {lineno}: {page}')
            pages.append(page)
            continue
        if line.startswith('## '):
            label = line[3:].strip()
            if page is None or label not in BANDS or (page, label) in sections:
                raise ValueError(f'Invalid/repeated section at line {lineno}: {label}')
            band = BANDS[label]
            sections.append((page, label))
            continue
        match = re.fullmatch(r'-\s*(.*)', line)
        if not match:
            raise ValueError(f'Unexpected Markdown content at line {lineno}: {line}')
        name = match.group(1).strip()
        if not name:
            empty_bullets += 1
            continue
        if page is None or band is None:
            raise ValueError(f'Entry outside a page/section at line {lineno}')
        names = NORMALIZATIONS.get(name, [name])
        if name in NORMALIZATIONS:
            normalized.append({'source_line': lineno, 'original': name, 'entries': names,
                               'reason': 'User-confirmed split of accidentally joined items.'})
        for actual_name in names:
            if actual_name not in by_name:
                raise ValueError(f'Unknown modifier name at line {lineno}: {actual_name}')
            candidates = by_name[actual_name]
            original = candidates[0]
            identity = original['key']
            if identity in seen:
                duplicates.append({'name': actual_name, 'source_line': lineno,
                                   'first_source_line': seen[identity]['source_line'],
                                   'retained_id': seen[identity]['id']})
                continue
            section_counts[(page, band)] += 1
            row = {key: original[key] for key in ('id', 'key', 'name')}
            row['name'] = metric_display_name(original)
            row.update(category=page, display_priority_band=band, grid_columns=3 if band == 'high' else 4,
                       display_order=section_counts[(page, band)], source_line=lineno)
            records.append(row)
            seen[identity] = row
            if len(candidates) > 1:
                ambiguous.append({'name': actual_name, 'retained_id': original['id'],
                                  'retained_key': original['key'],
                                  'other_ids': [r['id'] for r in candidates[1:]],
                                  'policy': 'Keep the first binding in the original exported registry.'})
    if pages != PAGES or sections != [(p, b) for p in PAGES for b in BANDS]:
        raise ValueError('Expected all six pages and Common/Other sections in GUI order.')
    if not records:
        raise ValueError('The display selection is empty.')
    selected = {r['id'] for r in records}
    return {'records': records, 'record_count': len(records),
            'categories': {p: sum(r['category'] == p for r in records) for p in PAGES},
            'bands': dict(Counter(r['display_priority_band'] for r in records)),
            'page_bands': {p: {b: section_counts[(p, b)] for b in BANDS.values()} for p in PAGES},
            'ignored_empty_bullets': empty_bullets, 'duplicates': duplicates,
            'normalizations': normalized, 'same_name_bindings': ambiguous,
            'excluded_records': [{k: r[k] for k in ('id', 'key', 'name', 'category')}
                                 for r in registry if r['id'] not in selected]}


def build(source=None):
    snapshot = DATA / SOURCE_NAME
    if source:
        source = Path(source).resolve()
        if source != snapshot.resolve():
            snapshot.write_bytes(source.read_bytes())
    registry_path = DATA / 'metric-index.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8-sig'))['records']
    manifest = parse_markdown(snapshot.read_text(encoding='utf-8-sig'), registry)
    manifest.update(schema_version=2, registry_count=len(registry),
                    source_markdown=SOURCE_NAME, source_sha256=digest(snapshot),
                    registry_sha256=digest(registry_path),
                    display_names_sha256=digest(ROOT / 'tools/display_names.py'),
                    policy='Markdown page and band order; ignore empty bullets; resolve explicit aliases before deduplicating by modifier key; first key occurrence wins; unqualified ambiguous native names retain the first registry binding; stable registry IDs are never renumbered.')
    if source:
        manifest['imported_from'] = str(source)
    with (DATA / 'display-layout.json').open('w', encoding='utf-8', newline='\n') as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return manifest


def load_display_records():
    registry_path = DATA / 'metric-index.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8-sig'))['records']
    lookup = {r['id']: r for r in registry}
    layout = json.loads((DATA / 'display-layout.json').read_text(encoding='utf-8'))
    if (digest(registry_path) != layout['registry_sha256']
            or digest(DATA / layout['source_markdown']) != layout['source_sha256']
            or digest(ROOT / 'tools/display_names.py') != layout.get('display_names_sha256')):
        raise ValueError('Display layout inputs changed; rebuild tools/display_layout.py first.')
    result = []
    for selection in layout['records']:
        original = lookup[selection['id']]
        if (any(original[k] != selection[k] for k in ('id', 'key'))
                or selection['name'] != metric_display_name(original)):
            raise ValueError('Display layout identity mismatch.')
        row = {**original, **selection}
        row['priority'] = 'P0' if row['display_priority_band'] == 'high' else 'P2'
        result.append(row)
    if len(result) != layout['record_count'] or len({r['id'] for r in result}) != len(result) or len({r['name'] for r in result}) != len(result):
        raise ValueError('Duplicate or inconsistent display layout.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Edited user Markdown to snapshot and import.')
    args = parser.parse_args()
    manifest = build(args.source)
    print(json.dumps({k: manifest[k] for k in ('record_count', 'categories', 'bands', 'page_bands', 'ignored_empty_bullets')}, ensure_ascii=False))
