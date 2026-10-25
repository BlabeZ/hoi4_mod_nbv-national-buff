"""Generate NBV localization and row bindings from the approved, stable ID index.

Python 3.9+, standard library. Generated files use UTF-8 BOM for HOI4.
The game reads ROOT.modifier directly; these files never sum source modifiers.
"""
from collections import Counter
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import re
from display_names import metric_display_name
from mod_metadata import descriptor_text

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tools/data'
VERSION = '0.1.11'
SOURCE_TABLES = ('source-bindings.json', 'leader-source-bindings.json',
                 'advisor-source-bindings.json', 'doctrine-technology-source-bindings.json',
                 'dynamic-source-bindings.json', 'ideology-source-bindings.json',
                 'faction-source-bindings.json', 'dynamic-spirit-source-bindings.json',
                 'special-source-bindings.json')


def source_label(entry):
    """Source kind labels describe data, not instructions or explanations."""
    kind = entry.get('source_type', '')
    category = entry['source_category']
    if kind == 'country_leader_trait':
        return ('领袖', 'Leader')
    if kind == 'advisor_trait':
        return ('顾问', 'Advisor')
    if kind in ('grand_doctrine', 'subdoctrine', 'subdoctrine_reward', 'doctrine_milestone'):
        return ('学说', 'Doctrine')
    if kind == 'technology':
        return ('科技', 'Technology')
    if kind == 'dynamic_modifier':
        return ('动态修正', 'Dynamic modifier')
    if kind in ('active_decision', 'decision'):
        return ('决议', 'Decision')
    if category in ('economy', 'mobilization_laws', 'trade_laws'):
        return ('法案', 'Law')
    if 'spirit' in category:
        return ('军官团精神', 'Officer corps spirit')
    return ('民族精神', 'National spirit')


def write(path, content, bom=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig' if bom else 'utf-8', newline='\n') as stream:
        stream.write(content)


def escape(text):
    return str(text).replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '\\n')


def source_format(code, literal):
    """Avoid rendering a verified nonzero source as zero; keep native semantics."""
    digits = int(re.search(r'\d+$', code).group())
    value = abs(Decimal(literal)) * (100 if '%' in code and '%%' not in code else 1)
    while value < Decimal(10) ** -digits:
        digits += 1
    return re.sub(r'\d+$', str(digits), code)


def source_value_plan(entry, varname, base_format):
    """Read current native input into a private temporary value only."""
    if entry.get('value_kind') != 'runtime':
        return ([source_format(base_format, entry['value_literal'])],
                ['set_temp_variable = { ' + varname + ' = ' + entry['value_literal'] + ' }'])
    expression = entry['value_expression']
    variable = expression['variable']
    assert re.fullmatch(r'(?:ROOT|global|[A-Z]{3})\.[A-Za-z_][A-Za-z0-9_]*', variable), variable
    coefficient, offset = expression['coefficient'], expression['offset']
    assert all(re.fullmatch(r'[+-]?\d+(?:\.\d+)?', s) for s in (coefficient, offset))
    commands = ['set_temp_variable = { ' + varname + ' = ' + variable + ' }']
    if Decimal(coefficient) != 1:
        commands.append('multiply_temp_variable = { ' + varname + ' = ' + coefficient + ' }')
    if Decimal(offset) != 0:
        commands.append('add_to_temp_variable = { ' + varname + ' = ' + offset + ' }')
    digits = int(re.search(r'\d+$', base_format).group())
    maximum = 3 if '%' in base_format and '%%' not in base_format else 5
    formats = [re.sub(r'\d+$', str(d), base_format) for d in range(digits, max(digits, maximum) + 1)]
    return formats, commands


def build():
    catalog = json.loads((DATA / 'metric-index.json').read_text(encoding='utf-8'))
    bindings = json.loads((DATA / 'modifier-format-bindings.json').read_text(encoding='utf-8'))
    rows = catalog['records']
    formats = {r['key']: r for r in bindings['records']}
    icon_table = json.loads((DATA / 'modifier-icon-bindings.json').read_text(encoding='utf-8'))
    icons = {r['key']: r for r in icon_table['records']}
    assert len(rows) == len(formats) == 559
    assert [r['id'] for r in rows] == list(range(1, 560))
    assert set(formats) == {r['key'] for r in rows}
    assert len(icons) == 559 and set(icons) == set(formats)
    # English names are optional development input; the game has a Chinese fallback.
    source = ROOT.parent / 'hoi4-modding-guide/vanilla-modifier-catalog/data/catalog.json'
    english = {r['key']: r for r in json.loads(source.read_text(encoding='utf-8'))['records']} if source.exists() else {}
    source_tables = {}
    for filename in SOURCE_TABLES:
        path = DATA / filename
        if path.exists():
            source_tables[filename] = json.loads(path.read_text(encoding='utf-8'))
    by_modifier = {}
    for table in source_tables.values():
        for key, entries in table['by_modifier'].items():
            by_modifier.setdefault(key, []).extend(entries)
    zh = {
        'nbv_entry_tooltip': '修正统计',
        'nbv_window_title': '[ROOT.GetName] · 国家修正统计',
        'nbv_page_1': '政治', 'nbv_page_2': '工业', 'nbv_page_3': '陆军',
        'nbv_page_4': '海军', 'nbv_page_5': '空军', 'nbv_page_6': '情报',
        'nbv_high_title': '常用', 'nbv_low_title': '其他修正',
        'nbv_refresh': '刷新',
        'nbv_filter_button_text': '[NBVFilterLabel]',
        'nbv_filter_all': '全部词条', 'nbv_filter_active': '隐藏词条',
        'nbv_empty_state': '无词条',
        'nbv_row_name_text': '[NBVRowName]', 'nbv_row_value_text': '[NBVRowValue]',
        'nbv_row_tooltip': '[NBVRowTooltip]', 'nbv_empty_text': '',
    }
    en = {
        'nbv_entry_tooltip': 'Modifier Statistics',
        'nbv_window_title': '[ROOT.GetName] · National Modifier Statistics',
        'nbv_page_1': 'Politics', 'nbv_page_2': 'Industry', 'nbv_page_3': 'Army',
        'nbv_page_4': 'Navy', 'nbv_page_5': 'Air Force', 'nbv_page_6': 'Intelligence',
        'nbv_high_title': 'Common', 'nbv_low_title': 'Other modifiers',
        'nbv_refresh': 'Refresh',
        'nbv_filter_button_text': '[NBVFilterLabel]',
        'nbv_filter_all': 'All entries', 'nbv_filter_active': 'Hide entries',
        'nbv_empty_state': 'No entries',
        'nbv_row_name_text': '[NBVRowName]', 'nbv_row_value_text': '[NBVRowValue]',
        'nbv_row_tooltip': '[NBVRowTooltip]', 'nbv_empty_text': '',
    }
    manifest, source_script, source_manifest = [], [], []
    for band, count in (('high', 3), ('low', 4)):
        for slot in range(1, count + 1):
            for locale in (zh, en):
                for part in ('name', 'value'):
                    locale[f'nbv_{band}_{part}_{slot}_text'] = f'[NBV{band.title()}{part.title()}{slot}]'
                locale[f'nbv_{band}_tooltip_{slot}'] = f'[NBV{band.title()}Tooltip{slot}]'
    for row in rows:
        ident, key = row['id'], row['key']
        fmt = formats[key]
        assert re.fullmatch(r'[+\-=%0-9YGRWH.?]+', fmt['format_code']), (key, fmt['format_code'])
        expression = '[?ROOT.modifier@' + key + '|' + fmt['format_code'] + ']'
        source_en = english.get(key, {})
        name_en = metric_display_name(row, 'english', source_en.get('name_en'))
        fragments = []
        for entry in by_modifier.get(key, []):
            if float(entry['value']) == 0:
                continue
            source_index = len(source_manifest) + 1
            source_name = entry['name_loc_key']
            assert re.fullmatch(r'[A-Za-z0-9_.-]+', source_name), source_name
            if entry.get('display_name_zh'):
                source_name = 'nbv_source_name_' + str(source_index)
                zh[source_name] = re.sub(r'(?:\\n|[\r\n])+', ' ', entry['display_name_zh'])
                en[source_name] = re.sub(r'(?:\\n|[\r\n])+', ' ', entry.get('display_name_en') or entry['display_name_zh'])
            elif entry.get('requires_single_line_alias'):
                source_name = 'nbv_source_name_' + str(source_index)
                zh[source_name] = entry['name_single_line_zh']
                en[source_name] = entry['name_single_line_en']
            value_literal = entry['value_literal']
            assert re.fullmatch(r'[+-]?\d+(?:\.\d+)?', value_literal), value_literal
            activation = entry['activation_script']
            # A compound predicate is one AND node. Otherwise its individual
            # clauses would incorrectly become alternatives in grouped OR gates.
            from validate_mod import parse_script
            activation_nodes = parse_script(activation)
            assert len(activation_nodes) == 1 and activation_nodes[0].key in (
                'has_idea', 'has_country_leader_with_trait', 'has_tech', 'has_doctrine',
                'has_dynamic_modifier', 'has_decision', 'has_completed_track', 'has_government', 'AND'), activation
            varname = f'nbv_source_value_{source_index}'
            display_formats, calculations = source_value_plan(entry, varname, fmt['format_code'])
            source_fmt = display_formats[0]
            function = f'NBVSource{source_index}'
            fragments.append((f'[{function}]', [activation]))
            labels = source_label(entry)
            branches = []
            for ordinal, display_format in enumerate(display_formats):
                digits = int(re.search(r'\d+$', display_format).group())
                locname = f'nbv_source_line_{source_index}' + (f'_p{digits}' if ordinal else '')
                for locale, separator in ((zh, '：'), (en, ': ')):
                    source_text = '$' + source_name + '$'
                    if entry.get('source_type') == 'country_leader_trait':
                        # Resolve the current leader at display time so changing
                        # country or government cannot leave a cached name.
                        source_text = '[ROOT.GetLeader]' + separator + source_text + separator
                    else:
                        source_text += ' '
                    locale[locname] = '\\n' + source_text + '[?'+varname+'|'+display_format+']'
                commands = [activation] + calculations
                if entry.get('value_kind') == 'runtime':
                    scale = 100 if '%' in display_format and '%%' not in display_format else 1
                    threshold = format(Decimal(10) ** -digits / scale, 'f')
                    commands += ['OR = { check_variable = { ' + varname + ' = ' + threshold + ' compare = greater_than_or_equals } '
                                 'check_variable = { ' + varname + ' = -' + threshold + ' compare = less_than_or_equals } }']
                branches.append('    text = {\n        trigger = {\n            ' + '\n            '.join(commands)
                                + '\n        }\n        localization_key = ' + locname + '\n    }\n')
            source_script.append('defined_text = {\n    name = ' + function + '\n' + ''.join(branches)
                                 + '    text = { localization_key = nbv_empty_text }\n}\n')
            source_manifest.append(dict(index=source_index, metric_id=ident, key=key, source_id=entry['source_id'],
                                        source_category=entry['source_category'], activation_script=activation,
                                        source_type=entry.get('source_type', ''), source_labels=labels,
                                        name_loc_key=source_name, value_literal=value_literal,
                                        value_kind=entry.get('value_kind', 'literal'), value_expression=entry.get('value_expression'),
                                        display_formats=display_formats,
                                        source_format_code=source_fmt, source=entry['source']))
        # Keep every expansion short. Large flat strings can silently omit later
        # scripted-localisation calls in the engine. Inactive branches return
        # empty before expanding their descendants, so only active leaves run.
        layer = 0
        while len(fragments) > 8:
            grouped = []
            for offset in range(0, len(fragments), 8):
                members = fragments[offset:offset + 8]
                group_id = f'{ident}_{layer}_{offset // 8}'
                function = 'NBVSourceGroup' + group_id
                locname = 'nbv_source_group_' + group_id
                activations = list(dict.fromkeys(a for _, keys in members for a in keys))
                for locale in (zh, en):
                    locale[locname] = ''.join(ref for ref, _ in members)
                source_script.append('defined_text = {\n    name = ' + function + '\n    text = {\n        trigger = { OR = {\n' +
                                     ''.join('            ' + activation + '\n' for activation in activations) +
                                     '        } }\n        localization_key = ' + locname + '\n    }\n    text = { localization_key = nbv_empty_text }\n}\n')
                grouped.append((f'[{function}]', activations))
            fragments = grouped
            layer += 1
        for loc, name in ((zh, metric_display_name(row)), (en, name_en)):
            # Native text icons share the name's existing single-line region.
            # Only private NBV strings use these aliases; source names stay intact.
            icon_token = icons[key]['icon_token']
            assert re.fullmatch(r'nbv_mi_[A-Za-z0-9_]+(?:\|\d+)?', icon_token), icon_token
            display_name = '£' + icon_token + ' ' + name
            loc['nbv_row_name_' + str(ident)] = display_name
            loc['nbv_row_value_' + str(ident)] = expression
            loc['nbv_sources_' + str(ident)] = ''.join(ref for ref, _ in fragments)
            loc['nbv_row_tooltip_' + str(ident)] = '§Y' + display_name + '§!  ' + expression + '$nbv_sources_' + str(ident) + '$'
        manifest.append(dict(id=ident, key=key, category=row['category'], priority=row['priority'],
                             columns=row['grid_columns'], expression=expression,
                             format_confidence=fmt['confidence'], runtime_read_validated=row['runtime_read_validated']))
    for language, entries in (('simp_chinese', zh), ('english', en)):
        # Values already contain deliberate Clausewitz \\n escapes; retain those.
        content = 'l_' + language + ':\n' + ''.join(' ' + k + ':0 "' + escape(v).replace('\\\\n', '\\n') + '"\n' for k, v in entries.items())
        write(ROOT / 'localisation' / language / ('nbv_l_' + language + '.yml'), content, True)

    scripted = ['# Row dispatch adapted from BUFF UI GETBUFFName. IDs refer to the approved metric index.\n']
    scripted.append('''defined_text = {
    name = NBVRowContainer
    text = { trigger = { check_variable = { nbv_row_id = 10000 } } localization_key = nbv_high_heading_row }
    text = { trigger = { check_variable = { nbv_row_id = 20000 } } localization_key = nbv_low_heading_row }
    text = { trigger = { check_variable = { nbv_row_id < 0 } } localization_key = nbv_low_row }
    text = { localization_key = nbv_high_row }
}
''')
    for band, count in (('high', 3), ('low', 4)):
        for slot in range(1, count + 1):
            for part in ('Name', 'Value', 'Tooltip'):
                scripted.append(f'''defined_text = {{
    name = NBV{band.title()}{part}{slot}
    text = {{
        trigger = {{ nbv_resolve_{band}_{slot} = yes }}
        localization_key = "nbv_row_{part.lower()}_[?nbv_entry_id]"
    }}
    text = {{ localization_key = nbv_empty_text }}
}}
''')
    for name, prefix in (('NBVRowName', 'nbv_row_name_'), ('NBVRowValue', 'nbv_row_value_'), ('NBVRowTooltip', 'nbv_row_tooltip_')):
        scripted.append('defined_text = {\n    name = ' + name + '\n    text = {\n        trigger = {\n            meta_trigger = {\n                text = { set_temp_variable = { nbv_loc_id = nbv_entry_id } }\n            }\n        }\n        localization_key = "' + prefix + '[?nbv_loc_id]"\n    }\n    text = { localization_key = nbv_empty_text }\n}\n')
    scripted.append('defined_text = {\n    name = NBVFilterLabel\n    text = {\n        trigger = { has_country_flag = nbv_show_zero }\n        localization_key = nbv_filter_all\n    }\n    text = { localization_key = nbv_filter_active }\n}\n')
    for i in range(1, 7):
        scripted.append('defined_text = {\n    name = nbv_tab_' + str(i) + '_sprite\n    text = {\n        trigger = { check_variable = { nbv_page = ' + str(i) + ' } }\n        localization_key = GFX_nbv_tab_selected\n    }\n    text = { localization_key = GFX_nbv_tab_normal }\n}\n')
    write(ROOT / 'common/scripted_localisation/nbv_scripted_localisation.txt', '\n'.join(scripted))
    write(ROOT / 'common/scripted_localisation/nbv_source_localisation.txt', '# Only verified nonzero vanilla source definitions. Unattributed amounts are not displayed.\n' + '\n'.join(source_script))
    source_tokens = sorted({token for row in source_manifest
                            for token in re.findall(r'\btoken:([A-Za-z0-9_]+)', row['activation_script'])})
    write(DATA / 'source-display-manifest.json', json.dumps(dict(version=VERSION, record_count=len(source_manifest),
          covered_modifiers=len({r['key'] for r in source_manifest}), records=source_manifest,
          synchronized_source_tokens=source_tokens,
          input_hashes={name:hashlib.sha256((DATA/name).read_bytes()).hexdigest() for name in source_tables}), ensure_ascii=False, indent=2)+'\n')
    write(ROOT / 'descriptor.mod', descriptor_text(ROOT / 'descriptor.mod', VERSION))
    token_path = DATA / 'synchronized-tokens.json'
    if token_path.exists():
        tokens = json.loads(token_path.read_text(encoding='utf-8'))['tokens']
        assert set(tokens).issubset(formats)
        write(ROOT / 'common/synchronized_dynamic_tokens/nbv_tokens.txt',
              '# Modifier and source-membership tokens used by the national viewer.\n'
              + '\n'.join(sorted(set(tokens) | set(source_tokens))) + '\n')
    meta = dict(record_count=len(rows), categories=dict(Counter(r['category'] for r in rows)),
                format_confidence=dict(Counter(r['format_confidence'] for r in manifest)), records=manifest,
                index_sha256=hashlib.sha256((DATA / 'metric-index.json').read_bytes()).hexdigest(),
                bindings_sha256=hashlib.sha256((DATA / 'modifier-format-bindings.json').read_bytes()).hexdigest())
    meta['icon_bindings_sha256'] = hashlib.sha256((DATA / 'modifier-icon-bindings.json').read_bytes()).hexdigest()
    write(DATA / 'build-manifest.json', json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in meta.items() if k != 'records'}, ensure_ascii=False))


if __name__ == '__main__':
    build()
