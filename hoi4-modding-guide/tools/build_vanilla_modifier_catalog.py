"""Build a reproducible, read-only inventory of the installed HOI4 modifier registry.

Python 3.9+, standard library only. Source frequency is static, not savegame telemetry.
"""
import argparse
import bisect
import collections
import hashlib
import html
import itertools
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUIDE = HERE.parent
OUT = GUIDE / 'vanilla-modifier-catalog'
GAME_DEFAULT = Path(r'E:\Steam\steamapps\common\Hearts of Iron IV')
DATE = '2026-10-24'
CATEGORIES = ['政治', '工业', '陆军', '海军', '空军', '情报']
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[=!<>?]+|[^\s{}=!<>?#"]+')
REF = re.compile(r'(?:leader_modifier|unit_modifier|modifier)@([A-Za-z0-9_]+)')
CONTROL = {'trigger', 'limit', 'allowed', 'available', 'visible', 'enable', 'potential',
           'ai_will_do', 'ai_weight', 'ai_weights', 'ai_strategy', 'ai_strategy_plan',
           'prerequisites', 'gain_xp', 'gain_xp_leader', 'weight', 'factor', 'cancel_trigger',
           'bypass', 'abort', 'cancel_if_invalid', 'target_trigger', 'target_root_trigger'}
VARIABLE_OPS = {'set_variable', 'add_to_variable', 'subtract_from_variable', 'multiply_variable',
                'divide_variable', 'clamp_variable', 'set_temp_variable', 'add_to_temp_variable',
                'subtract_from_temp_variable', 'multiply_temp_variable', 'divide_temp_variable',
                'check_variable', 'check_variable_range', 'clamp_temp_variable', 'export_to_variable'}
MOD_BLOCKS = {'modifier', 'modifiers', 'country_modifier', 'state_modifier', 'targeted_modifier',
              'targeted_modifiers', 'non_shared_modifier', 'field_marshal_modifier',
              'corps_commander_modifier', 'equipment_bonus', 'equipment_modifiers',
              'sub_unit_modifiers', 'unit_modifiers', 'country_modifiers', 'global_modifier'}
DATA_FAMILIES = {'country_leader', 'unit_leader', 'technologies', 'doctrines', 'aces',
                 'occupation_laws', 'intelligence_agency_upgrades', 'intelligence_agencies',
                 'autonomous_states', 'resistance_compliance_modifiers', 'scientist_traits',
                 'difficulty_settings', 'terrain', 'medals', 'unit_medals', 'strategic_locations',
                 'technology_sharing', 'buildings', 'factions', 'ideologies', 'unit_tags'}


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def read(path):
    return path.read_text(encoding='utf-8-sig', errors='replace')


def script_items(text):
    """Yield assignment/reference events with parent blocks; ignore comments and quoted keys.

    This is a lexical context scanner, not an interpreter. '=' assignments are separated
    from comparisons, block names, variable operations and dynamic modifier references.
    """
    stack, block_lines, pending, previous = [], [], None, None
    newlines = [m.start() for m in re.finditer('\n', text)]
    for m in TOKEN.finditer(text):
        t = m.group()
        if t.startswith('#'):
            continue
        line = bisect.bisect_right(newlines, m.start()) + 1
        for ref in REF.finditer(t):
            yield {'kind': 'reference', 'key': ref.group(1), 'value': t,
                   'line': line, 'context': list(stack), 'context_lines': list(block_lines)}
        if pending is not None:
            key, keyline = pending
            pending = None
            if t == '{':
                stack.append(key)
                block_lines.append(keyline)
            else:
                yield {'kind': 'assignment', 'key': key, 'value': t,
                       'line': keyline, 'context': list(stack), 'context_lines': list(block_lines)}
        elif t == '{':
            stack.append('<anonymous>')
            block_lines.append(line)
        elif t == '}':
            if stack:
                stack.pop()
                block_lines.pop()
        elif t == '=' and previous and previous[0] not in '{}=<>!':
            pending = previous
        previous = (t, line)


def registry(game):
    path = game / 'documentation/modifiers_documentation.md'
    lines = read(path).splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith('## ')]
    records, blocks = {}, []
    for a, b in zip(starts, starts[1:] + [len(lines)]):
        title = re.sub(r'<span[^>]*></span>', '', lines[a][3:]).strip()
        body = '\n'.join(lines[a+1:b])
        if not re.search(r'^\* \*\*Categories\*\*:', body, re.M):
            continue
        def field(label):
            m = re.search(r'^\* \*\*' + label + r'\*\*: (.*)$', body, re.M)
            return m.group(1) if m else ''
        ph = re.findall(r'<[^>]+>', title)
        types = field('Modified types').split(', ') if field('Modified types') else []
        assert not ph or (len(ph) == 1 and types), title
        display = re.search(r'^\* (Number[^\n]*|Boolean[^\n]*)', body, re.M)
        block = {'heading': title, 'line': a+1, 'template': bool(ph), 'parameter_count': len(types)}
        blocks.append(block)
        for param in (types if ph else [None]):
            key = title.replace(ph[0], param) if ph else title
            assert key not in records, ('duplicate registry key', key)
            records[key] = {
                'key': key, 'registry_kind': 'template_expansion' if ph else 'fixed',
                'template': title if ph else None, 'parameter': param,
                'engine_categories': field('Categories').split(', '),
                'doc_source': str(path), 'doc_line': a+1, 'doc_description': field('Description'),
                'doc_display': display.group(1) if display else '',
                'definition_count': 0, 'other_assignment_count': 0, 'reference_count': 0,
                'files': [], 'content_families': [], 'examples': [], 'other_examples': [],
                'reference_examples': [], 'custom_definition': None,
            }
    for p in sorted((game/'common/modifier_definitions').glob('*.txt')):
        meta = collections.defaultdict(dict)
        for item in script_items(read(p)):
            if item['kind'] == 'assignment' and len(item['context']) == 1:
                k = item['context'][0]
                meta[k][item['key']] = item['value']
                meta[k]['source'] = str(p)
                meta[k].setdefault('line', item['line']-1)
        for k, v in meta.items():
            if k not in records:
                records[k] = {'key': k, 'registry_kind': 'custom_definition', 'template': None,
                    'parameter': None, 'engine_categories': [v.get('category', 'all')],
                    'doc_source': str(p), 'doc_line': v['line'], 'doc_description': '',
                    'doc_display': v.get('value_type', ''), 'definition_count': 0,
                    'other_assignment_count': 0, 'reference_count': 0, 'files': [],
                    'content_families': [], 'examples': [], 'other_examples': [], 'reference_examples': []}
            records[k]['custom_definition'] = v
    return records, blocks


def usage_kind(item, relative):
    parents = [x.lower() for x in item['context']]
    family = relative.parts[1] if relative.parts[0] == 'common' and len(relative.parts)>1 else relative.parts[0]
    if item['kind'] == 'reference':
        return 'reference', 'dynamic_modifier_read'
    if family == 'modifier_definitions':
        return 'other_assignment', 'registry_metadata'
    if any(p in VARIABLE_OPS for p in parents):
        return 'other_assignment', 'variable_operation'
    # A real nested modifier payload can occur inside a conditionally granted effect.
    mod_indices = [i for i, p in enumerate(parents) if p in MOD_BLOCKS]
    ctrl_indices = [i for i, p in enumerate(parents) if p in CONTROL]
    if mod_indices and (not ctrl_indices or max(mod_indices) > max(ctrl_indices)):
        return 'definition', 'modifier_payload'
    if ctrl_indices or any(p.startswith('ai_') for p in parents):
        return 'other_assignment', 'condition_or_ai_weight'
    if family in {'dynamic_modifiers', 'modifiers'} and len(parents) == 1:
        return 'definition', 'modifier_definition_body'
    if relative.name in {'event_modifiers.txt', 'triggered_modifiers.txt'} and len(parents) == 1:
        return 'definition', 'modifier_definition_body'
    if relative.parts[0] == 'common' and family in DATA_FAMILIES and parents:
        return 'definition', 'typed_data_body'
    return 'other_assignment', 'unclassified_assignment'


def apply_mod_coverage(records):
    audit = json.loads(read(GUIDE/'references/buff-visualization-audit.json'))
    lookup = {k.lower(): k for k in records}
    anomalies = []
    for r in records.values():
        r['buff_mods'] = []
        r['buff_mod_expressions'] = []
    for label, rows in [('decision', audit['basic']['readings']),
                        ('ui', [r for r in audit['ui']['slots'] if r['kind'] == 'modifier'])]:
        for row in rows:
            k = row['modifier']
            canonical = k if k in records else lookup.get(k.lower())
            if canonical:
                r = records[canonical]
                if label not in r['buff_mods']:
                    r['buff_mods'].append(label)
                r['buff_mod_expressions'].append({'mod': label, 'source_key': k, 'line': row['line'],
                    'format': row['format'], 'case_normalized': k != canonical})
            else:
                anomalies.append({'mod': label, 'key': k, 'line': row['line'], 'reason': 'not in expanded registry'})
    return anomalies


def scan(game):
    records, blocks = registry(game)
    lookup = {k.lower(): k for k in records}
    files, families = collections.defaultdict(set), collections.defaultdict(set)
    contexts = collections.defaultdict(set)
    manifest, totals = [], collections.Counter()
    occurrence_path = OUT/'data/occurrences.jsonl'
    occurrence_path.parent.mkdir(parents=True, exist_ok=True)
    source_paths = sorted(p for root in ['common', 'events', 'history']
                          for p in (game/root).rglob('*.txt')
                          if 'documentation' not in p.name.lower() and not p.name.lower().startswith('readme'))
    with occurrence_path.open('w', encoding='utf-8') as out:
        for n, p in enumerate(source_paths, 1):
            data = p.read_bytes()
            text = data.decode('utf-8-sig', errors='replace')
            rel = p.relative_to(game)
            family = '/'.join(rel.parts[:2]) if rel.parts[0] == 'common' else rel.parts[0]
            manifest.append({'path': str(p), 'relative_path': rel.as_posix(), 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest()})
            for item in script_items(text):
                canonical = item['key'] if item['key'] in records else lookup.get(item['key'].lower())
                if not canonical:
                    continue
                kind, rule = usage_kind(item, rel)
                r = records[canonical]
                r[kind + '_count'] += 1
                totals[kind] += 1
                evidence = {'file': str(p), 'relative_file': rel.as_posix(), 'line': item['line'],
                    'context': item['context'], 'context_lines': item['context_lines'],
                    'value': item['value'], 'classification_rule': rule}
                example_field = {'definition': 'examples', 'other_assignment': 'other_examples',
                                 'reference': 'reference_examples'}[kind]
                if len(r[example_field]) < 8:
                    r[example_field].append(evidence)
                out.write(json.dumps(dict(key=canonical, source_key=item['key'], kind=kind,
                                           **evidence), ensure_ascii=False) + '\n')
                if kind == 'definition':
                    files[canonical].add(str(p))
                    families[canonical].add(family)
                    contexts[(str(p), tuple(item['context']), tuple(item['context_lines']))].add(canonical)
            if n % 1000 == 0:
                print('scanned', n, '/', len(source_paths), flush=True)
    co = collections.defaultdict(collections.Counter)
    for group in contexts.values():
        for a, b in itertools.combinations(sorted(group), 2):
            co[a][b] += 1
            co[b][a] += 1
    for k, r in records.items():
        r['files'] = sorted(files[k])
        r['file_count'] = len(files[k])
        r['content_families'] = sorted(families[k])
        r['family_count'] = len(families[k])
        r['cooccurring_keys'] = [{'key': other, 'shared_definition_blocks': num}
                                for other, num in co[k].most_common(5)]
    anomalies = apply_mod_coverage(records)
    version = json.loads(read(game/'launcher-settings.json'))
    result = {'analysed_date': DATE, 'game_root': str(game), 'game_version': version.get('version'),
        'raw_version': version.get('rawVersion'), 'registry_blocks': blocks,
        'statistics': {'registry_keys': len(records), 'fixed_blocks': sum(not x['template'] for x in blocks),
            'template_blocks': sum(x['template'] for x in blocks), 'scanned_files': len(manifest),
            'occurrences': dict(totals), 'keys_with_definitions': sum(r['definition_count']>0 for r in records.values()),
            'keys_with_any_occurrence': sum(r['definition_count']+r['other_assignment_count']+r['reference_count']>0 for r in records.values())},
        'buff_mod_unmatched': anomalies, 'records': list(records.values())}
    dump(OUT/'data/registry-and-frequency.json', result)
    dump(OUT/'data/source-manifest.json', manifest)
    print(json.dumps(result['statistics'], ensure_ascii=False, indent=2))
    return result


def self_check():
    sample = '# army_attack_factor = 9\nideas={ a={ modifier={ army_attack_factor=0.1 } allowed={army_attack_factor>0} } }\nset_variable={army_attack_factor=3}\nx="army_attack_factor = 5"\ny=modifier@army_attack_factor'
    found = [x for x in script_items(sample) if x['key'] == 'army_attack_factor']
    assert [x['kind'] for x in found] == ['assignment', 'assignment', 'reference'], found
    assert found[0]['context'] == ['ideas', 'a', 'modifier']
    assert usage_kind(found[0], Path('common/ideas/test.txt'))[0] == 'definition'
    assert usage_kind(found[1], Path('common/scripted_effects/test.txt'))[0] == 'other_assignment'
    assert found[0]['line'] == 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path, default=GAME_DEFAULT)
    parser.add_argument('--stage', choices=['scan', 'render', 'all'], default='all')
    args = parser.parse_args()
    self_check()
    if args.stage in ['scan', 'all']:
        data = scan(args.game_root)
    else:
        data = json.loads(read(OUT/'data/registry-and-frequency.json'))
    if args.stage in ['render', 'all']:
        from render_modifier_catalog import render
        render(data, args.game_root, OUT)
