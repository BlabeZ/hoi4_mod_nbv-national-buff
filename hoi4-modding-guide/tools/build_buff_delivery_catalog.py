"""Build the final selected BUFF catalogue; read source catalogues without altering them.

Python 3.9+, standard library only. Run from any working directory.
Only writes buff-statistics-mod/01-buff-catalog.md and its two data products.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / 'vanilla-modifier-catalog/global-buff-review/data/display-catalog.json'
ORIGINAL = ROOT / 'vanilla-modifier-catalog/data/catalog.json'
OUT = ROOT / 'buff-statistics-mod'
CATEGORIES = ('政治', '工业', '陆军', '海军', '空军', '情报')
PRIORITIES = ('P0', 'P1', 'P2', 'P3')
EXPECTED = {'政治': (92, 2), '工业': (105, 4), '陆军': (160, 6),
            '海军': (78, 14), '空军': (48, 3), '情报': (38, 9)}
EXPECTED_BANDS = {'政治': (35, 59), '工业': (30, 79), '陆军': (51, 115),
                  '海军': (32, 60), '空军': (25, 26), '情报': (25, 22)}


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def distinct(items):
    return list(dict.fromkeys(x for x in items if x))


def source_path(path):
    return str(path).replace('\\', '/')


def link(label, path, line=None):
    target = source_path(path) + (':' + str(line) if line else '')
    return '[' + label + '](<' + target + '>)'


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', '<br>')


def make_catalog():
    review, original = load(REVIEW), load(ORIGINAL)
    original_by_key = {r['key']: r for r in original['records']}
    selected = sorted((r for r in review['records'] if r['group'] in ('A', 'B')),
                      key=lambda r: (CATEGORIES.index(r['category']), PRIORITIES.index(r['old_priority']), r['key']))
    files = {}

    def reference(path, line):
        path = source_path(path)
        if path not in files:
            files[path] = 's%03d' % (len(files) + 1)
        return {'file_id': files[path], 'line': int(line)}

    records = []
    category_order = Counter()
    for row in selected:
        old = original_by_key[row['key']]
        priority = row['old_priority']
        band = 'high' if priority in ('P0', 'P1') else 'low'
        category_order[row['category']] += 1
        display = old.get('doc_display', '')
        decimals = re.fullmatch(r'Number with (\d+) decimal places', display)
        conditions = distinct(row['conditions'])
        notes = distinct(row['source_notes'])
        effect = row['effect_summary']
        if row['key'] == 'air_invasion_plan_cap':
            effect = '空降作战计划上限的国家修正分量；原版中英文说明的计数对象不一致，最终单位待实测。'
            notes.append('中文_DESC写“最大师数量”，英文_DESC写可同时规划和准备的空降入侵数量；不能与air_invasion_division_cap合并。')

        # Preserve a small, representative selection; never relabel weak variable evidence as strong.
        examples, roles, seen = [], set(), set()
        for example in row['evidence']:
            kind = example.get('kind', 'manual_review')
            loc = (source_path(example['file']), example['line'])
            if loc in seen or kind in roles:
                continue
            if kind == 'variable_examples' and examples:
                continue
            seen.add(loc)
            roles.add(kind)
            examples.append(dict(reference(*loc), kind=kind, label=example.get('label', '来源')))
            if len(examples) == 3:
                break
        if not examples:
            # Evidence outside the focus/spirit tracer stays explicitly auxiliary.
            for example in old.get('examples', [])[:2]:
                examples.append(dict(reference(example['file'], example['line']),
                                     kind='all_context_definition',
                                     label='全语料赋值；不作为国策／国家精神证据'))

        name_sources = [s for s in old.get('localisation_sources', [])
                        if '/simp_chinese/' in source_path(s['path'])]
        description_sources = old.get('localisation_description_sources', [])
        description_sources = [s for s in description_sources
                               if '/simp_chinese/' in source_path(s['path'])
                               or row['key'] == 'air_invasion_plan_cap']
        record = {
            'key': row['key'],
            'name': row['name_zh'],
            'category': row['category'],
            'source_grade': row['group'],
            'priority': priority,
            'display_priority_band': band,
            'grid_columns': 3 if band == 'high' else 4,
            'display_order': category_order[row['category']],
            'effect_summary': effect,
            'conditions': conditions,
            'notes': distinct(notes),
            'read_expression': row['read_expression'],
            'runtime_read_validated': False,
            'unit': {
                'registry_display': display,
                'registry_decimal_places': int(decimals.group(1)) if decimals else None,
                'source': reference(old['doc_source'], old['doc_line']),
                'unit_confirmed': False,
            },
            'name_origin': {
                'method': old.get('localisation_method'),
                'editorial_label': bool(old.get('localisation_editorial_name'))
                                   or row['name_zh'] != row.get('original_name_zh'),
                'sources': [dict(reference(s['path'], s['line']), key=s['key']) for s in name_sources],
            },
            'effect_sources': [dict(reference(s['path'], s['line']), key=s['key'])
                               for s in description_sources],
            'source_summary': {
                'strong_focus_or_country_spirit_evidence': row['has_strong_focus_or_spirit_evidence'],
                'country_spirit_definitions': row['country_spirit_direct_count'],
                'unique_focus_count': row['focus_unique_count'],
                'definitions_all_contexts': row['definition_count_all_contexts'],
                'examples': examples,
            },
        }
        if row['name_zh'] != row.get('original_name_zh'):
            record['original_name'] = row.get('original_name_zh')
        records.append(record)

    categories = {category: {'A': sum(r['category'] == category and r['source_grade'] == 'A' for r in records),
                             'B': sum(r['category'] == category and r['source_grade'] == 'B' for r in records)}
                  for category in CATEGORIES}
    for category, counts in categories.items():
        counts['total'] = counts['A'] + counts['B']
        counts['high'] = sum(r['category'] == category and r['display_priority_band'] == 'high' for r in records)
        counts['low'] = sum(r['category'] == category and r['display_priority_band'] == 'low' for r in records)
    manifest = [{'path': source_path(p), 'sha256': sha256(p)} for p in (REVIEW, ORIGINAL)]
    return {
        'schema_version': 2,
        'date': review['date'],
        'game_version': review['game_version'],
        'record_count': len(records),
        'source_grades': dict(Counter(r['source_grade'] for r in records)),
        'priorities': dict(Counter(r['priority'] for r in records)),
        'display_priority_bands': dict(Counter(r['display_priority_band'] for r in records)),
        'grid_layout': {
            'flow': 'vertical_sections',
            'high': {'priorities': ['P0', 'P1'], 'grid_columns': 3, 'section_order': 1},
            'low': {'priorities': ['P2', 'P3'], 'grid_columns': 4, 'section_order': 2},
        },
        'ui_requirements': {
            'target': 'current_player_country_only',
            'pages': list(CATEGORIES),
            'navigation': {
                'control': 'page_buttons', 'position': 'top',
                'fixed_outside_content_scroll': True,
                'highlight_active_page': True,
                'visible_content_pages': 1,
            },
            'initial_category': '政治',
            'remember_category_on_close': True,
            'restore_category_on_reopen': True,
            'refresh_on_tag_change': True,
            'color_policy': '复用原版字体红绿颜色，逐键继承原版数值的利弊方向；中性项按原版规则。',
            'status': '用户确认的实现要求；尚未进行游戏内验证。',
        },
        'categories': categories,
        'scope_contract': review['scope_contract'],
        'field_contract': {
            'source_grade': 'A=发现可信国策/国家精神来源；B=本次未检出上述来源但明确选入。不是优先级或运行验证等级。',
            'priority': '保留权威筛选数据的old_priority：P0/P1映射high，P2/P3映射low；不按A/B分高低。',
            'grid_columns': '游戏UI要求：high位于前方区域、每行3列，low位于后方区域、每行4列；两个区域纵向排列，不是横向7列。每条的值表示所属区列数，不是词条跨度。Markdown仍每条独立一行。',
            'display_order': '每类别从1开始的连续顺序；按P0、P1、P2、P3，再按稳定key排序。数值变化不改变顺序，A/B不参与排序。',
            'source_files': '证据用file_id查本表，再按line定位本机文件；仅保留代表性证据，完整链见权威筛选目录。',
            'read_expression': '国家作用域的候选读取表达式，未逐项游戏内验证；不得拿地方/装备/单位读数补足。',
            'unit': 'registry_display仅说明注册文档的小数位，不证明百分比、天数、点数或最终容量。所有unit_confirmed=false。',
            'unconfirmed_defaults': {'physical_unit': None, 'display_multiplier': None, 'beneficial_sign': None,
                                     'aggregation_formula': None, 'refresh_validated': False},
            'effect_summary': '尽量沿用确认过的中文说明；缺公式时只保留作用对象。air_invasion_plan_cap另标中英文计数对象冲突。',
            'counts': '国家精神为定义计数，国策为独立国策去重数；不等于当前国家同时生效次数。',
        },
        'input_manifest': manifest,
        'source_files': {identifier: path for path, identifier in files.items()},
        'records': records,
    }, review


def source_link(data, ref, label):
    return link(label, data['source_files'][ref['file_id']], ref['line'])


def render_markdown(data):
    lines = [
        '# 最终 BUFF 修正清单', '',
        '版本：%s。整理日期：%s。' % (data['game_version'], data['date']), '',
        '本清单仅包含最终选中的 **559 项**：A 类 **521 项**、B 类 **38 项**。按六类分表，技术键是唯一标识。', '',
        '| 分类 | A：有国策／国家精神证据 | B：其他已选候选 | 高优先级 | 低优先级 | 合计 |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for category, counts in data['categories'].items():
        lines.append('| %s | %s | %s | %s | %s | %s |' % (category, counts['A'], counts['B'], counts['high'], counts['low'], counts['total']))
    lines += [
        '| **合计** | **521** | **38** | **198** | **361** | **559** |', '',
        'A/B 是**来源证据等级**，不是重要性、当前生效状态或读取成功等级。B 类包含其他来源和用户明确指定的待验证项；没有国策／国家精神命中不等于原版从未使用。', '',
        '**游戏内页面导航**：政治、工业、陆军、海军、空军、情报六个页面，由窗口顶端固定排列的六个页面按钮切换；高亮当前页面，下方词条独立滚动。首次政治页，后续恢复上次关闭的分类页。', '',
        '**展示优先级沿用已有 P0/P1/P2/P3 分级**：P0、P1 共198项归高优先级，放在游戏页面前方区域、每行3列；P2、P3 共361项归低优先级，放在后方区域、每行4列。两区纵向排列，不是横向7列。A/B不用于决定高低。此映射是当前展示安排，不重新评定原有分级。', '',
        '每类别固定按 P0 → P1 → P2 → P3、同级按技术键排序；数值增减不改变位置。JSON 的 `display_order` 从每类别的 1 开始连续编号，`grid_columns` 表示所属展示区为 3 列或 4 列。三列／四列是**游戏 UI 布局要求**；Markdown 按高、低小节保留每项独立数据行，便于查阅来源。', '',
        '## 范围与读法', '',
        data['scope_contract']['include'], '',
        '排除：' + data['scope_contract']['exclude'], '',
        data['scope_contract']['label'], '',
        '**所有候选读取仍未逐项游戏内验证。** 候选形式为 `[?ROOT.modifier@技术键]`；每项精确表达式见配套 JSON。来源存在不能证明当前国家非零、来源全部同时生效或最终单位属性。', '',
        '原版注册文档只写了数值的小数位。本表 `D0`／`D1`／`D2`／`D3` 分别表示原文的 0／1／2／3 位小数，**不代表百分比、天数、点数、倍率或正负优劣**。这些显示含义和刷新行为仍需实测；不能仅按 `_factor` 后缀决定乘以 100 或着色。', '',
        '“作用对象；公式未确认”表示原版没有可直接采用的详细说明。表中作用与名称重复时压缩为“同名称”；编辑名称或模板名称的原始来源保存在 JSON。共同限制不在每行重复。', '',
        '## 必须分开的同名或相近项', '',
        '| 项目 | 独立技术键 | 展示约束 |',
        '|---|---|---|',
        '| 冬季损耗 | winter_attrition、winter_attrition_factor | 基础项与比例项分列，不能相加；这里只读国家分量。 |',
        '| 炎热损耗 | heat_attrition_factor | 仅使用已选国家比例项；地方天气基础项不进入本清单。 |',
        '| 陆军师损耗 | attrition | 不混入州控制者或具体部队的实际损耗。 |',
        '| 陆军师训练时间 | training_time_army、training_time_army_factor | 基础项与比例项分列；基础项单位与读取尚待实测。 |',
        '| 投降界限 | surrender_limit、forced_surrender_limit | 常规项与强制阈值项分列，不能相加或替代。 |',
        '| 恶劣天气惩罚 | air_weather_penalty、navy_weather_penalty | 分别属于空军与海军，不把实际空域／海域天气数值加入国家读数。 |',
        '| 登陆与空降容量 | naval_invasion_capacity、naval_invasion_division_cap、naval_invasion_plan_cap；air_invasion_division_cap、air_invasion_plan_cap | 总容量、每计划师容量、计划数上限分列。原版部分中英文说明有差异，修正分量不等于最终上限。 |',
        '| 资源与建设 | local_resources_factor、production_speed_…_factor | 名称有local或涉及某类设施仍可包含国家分量；不得混入某州的最终资源、速度、槽位或地形值。 |',
        '| 设计商与军工机构 | 五类设计商聘用费用、military_industrial_organization_funds_gain | 只保留国家通用费用／经费分量，不纳入具体机构、装备、模块、生产线及设计商科研修正。 |', '',
        '## 六类完整清单', '',
        '“证据”链接为原版代表性来源；“登记”链接定位键与显示格式，“说明”链接定位原版中文说明。“其他赋值”仅提供全语料定义位置，不改变 B 类的国策／国家精神证据状态。没有实际赋值证据的候选明确标为“仅登记”。完整国策路径、未入选原因不混入本表。', '',
    ]
    for category in CATEGORIES:
        counts = data['categories'][category]
        lines += ['### %s（%s 项：A %s／B %s）' % (category, counts['total'], counts['A'], counts['B']), '']
        current_band = None
        for row in data['records']:
            if row['category'] != category:
                continue
            if row['display_priority_band'] != current_band:
                current_band = row['display_priority_band']
                title = ('高优先级：P0／P1，前方区域每行3列' if current_band == 'high'
                         else '低优先级：P2／P3，后方区域每行4列')
                lines += ['#### %s（%s 项）' % (title, counts[current_band]), '',
                          '| 名称／技术键 | 优先级／来源 | 作用摘要 | 条件与特殊说明 | 格式与依据 |',
                          '|---|:---:|---|---|---|']
            effect = row['effect_summary']
            m = re.fullmatch(r'作用项：(.*?)。本地原版未提供详细公式说明。', effect)
            if m:
                effect = ('同名称' if m.group(1) in (row['name'], row.get('original_name')) else '作用对象：' + m.group(1)) + '；公式未确认。'
            conditions = '；'.join(distinct(row['conditions'] + row['notes'])) or '—'
            decimals = row['unit']['registry_decimal_places']
            refs = ['D%s' % decimals if decimals is not None else '格式待核', source_link(data, row['unit']['source'], '登记')]
            examples = row['source_summary']['examples']
            if examples:
                label = '其他赋值' if examples[0]['kind'] == 'all_context_definition' else '证据'
                refs.append(source_link(data, examples[0], label))
            else:
                refs.append('仅登记' if row['source_summary']['definitions_all_contexts'] == 0 else '赋值语境见完整目录')
            if row['effect_sources']:
                refs.append(source_link(data, row['effect_sources'][0], '说明'))
            lines.append('| %s<br>%s | %s | %s | %s | %s |' % (
                cell(row['name']), '<code>' + cell(row['key']) + '</code>', row['priority'] + '／' + row['source_grade'],
                cell(effect), cell(conditions), ' · '.join(refs)))
            # Keep the next Markdown subsection separated from the table.
            if row['display_order'] == counts['high']:
                lines.append('')
        lines.append('')
    lines += [
        '## 数据文件与复现', '',
        '- [精简白名单 JSON](data/buff-display-whitelist.json)：仅 559 项，包含优先级、三列／四列布局、稳定排序、读取候选、证据摘要、名称来源、原版显示格式和验证状态。',
        '- [交付校验结果](data/catalog-verification.json)：数量、分类、优先级、布局列数、排序、唯一键、名称、来源路径与输入／输出 SHA-256。',
        '- [生成脚本](../tools/build_buff_delivery_catalog.py)：Python 3.9+ 标准库；运行后只重建本清单和上述两个 JSON。',
        '- [权威筛选数据](../vanilla-modifier-catalog/global-buff-review/data/display-catalog.json)：本清单选择和条件的来源。',
        '- [原始完整目录](../vanilla-modifier-catalog/data/catalog.json)：注册显示格式、本地化来源和原版作用说明的来源。', '',
        '```powershell', 'python .\tools\build_buff_delivery_catalog.py', '```', '',
        '以上命令在 hoi4-modding-guide 目录运行。原版及已有筛选文件只读；本次交付不修改游戏或安装模组。', '',
    ]
    return '\n'.join(lines)


def verify(data, review, markdown):
    rows = data['records']
    source_by_key = {r['key']: r for r in review['records'] if r['group'] in ('A', 'B')}
    refs = [ref for row in rows for ref in [row['unit']['source']] + row['name_origin']['sources']
            + row['effect_sources'] + row['source_summary']['examples']]
    line_counts = {identifier: len(Path(path).read_text(encoding='utf-8-sig').splitlines())
                   for identifier, path in data['source_files'].items()}
    local_links = []
    for bracketed, plain in re.findall(r'\]\((?:<([^>]+)>|([^\)]+))\)', markdown):
        path = Path(re.sub(r':\d+$', '', bracketed or plain))
        local_links.append(path if path.is_absolute() else OUT / path)
    generated = {OUT / 'data/buff-display-whitelist.json', OUT / 'data/catalog-verification.json'}
    checks = {
        'exactly_559_unique_selected_keys': len(rows) == len({r['key'] for r in rows}) == 559,
        'same_keys_as_authoritative_selection': {r['key'] for r in rows} == set(source_by_key),
        'grades_521_A_38_B': data['source_grades'] == {'A': 521, 'B': 38},
        'six_categories_expected_counts': all((data['categories'][c]['A'], data['categories'][c]['B']) == EXPECTED[c] for c in CATEGORIES),
        'priorities_preserved': all(r['priority'] == source_by_key[r['key']]['old_priority'] and r['priority'] in PRIORITIES for r in rows),
        'priority_bands_198_high_361_low': data['display_priority_bands'] == {'high': 198, 'low': 361},
        'six_categories_priority_band_counts': all((data['categories'][c]['high'], data['categories'][c]['low']) == EXPECTED_BANDS[c] for c in CATEGORIES),
        'priority_band_mapping': all(r['display_priority_band'] == ('high' if r['priority'] in ('P0', 'P1') else 'low') for r in rows),
        'grid_columns_3_high_4_low': all(r['grid_columns'] == (3 if r['display_priority_band'] == 'high' else 4) for r in rows),
        'grid_sections_vertical_high_before_low': data['grid_layout']['flow'] == 'vertical_sections' and data['grid_layout']['high']['section_order'] == 1 and data['grid_layout']['low']['section_order'] == 2,
        'confirmed_ui_requirements_preserved': data['ui_requirements']['target'] == 'current_player_country_only' and data['ui_requirements']['initial_category'] == '政治' and all(data['ui_requirements'][k] for k in ('remember_category_on_close', 'restore_category_on_reopen', 'refresh_on_tag_change')),
        'six_top_page_buttons': data['ui_requirements']['pages'] == list(CATEGORIES) and data['ui_requirements']['navigation'] == {'control': 'page_buttons', 'position': 'top', 'fixed_outside_content_scroll': True, 'highlight_active_page': True, 'visible_content_pages': 1},
        'stable_category_priority_key_order': rows == sorted(rows, key=lambda r: (CATEGORIES.index(r['category']), PRIORITIES.index(r['priority']), r['key'])),
        'display_order_contiguous_per_category': all([r['display_order'] for r in rows if r['category'] == c] == list(range(1, data['categories'][c]['total'] + 1)) for c in CATEGORIES),
        'markdown_high_low_sections_per_category': markdown.count('#### 高优先级：') == 6 and markdown.count('#### 低优先级：') == 6,
        'no_empty_or_placeholder_names': all(r['name'] and r['name'] not in (r['key'], '名称待核验') and source_by_key[r['key']]['has_confirmed_display_name'] for r in rows),
        'no_C_records': all(r['source_grade'] in ('A', 'B') for r in rows),
        'all_runtime_validation_false': all(r['runtime_read_validated'] is False and source_by_key[r['key']]['runtime_read_validated'] is False for r in rows),
        'all_unit_validation_false': all(r['unit']['unit_confirmed'] is False for r in rows),
        'read_expressions_preserved': all(r['read_expression'] == source_by_key[r['key']]['read_expression'] == '[?ROOT.modifier@' + r['key'] + ']' for r in rows),
        'grades_match_strong_evidence': all((r['source_grade'] == 'A') == r['source_summary']['strong_focus_or_country_spirit_evidence'] for r in rows),
        'all_evidence_files_exist': all(Path(p).is_file() for p in data['source_files'].values()),
        'all_evidence_lines_positive': all(ref['line'] > 0 and ref['file_id'] in data['source_files'] for ref in refs),
        'all_evidence_lines_within_file': all(ref['line'] <= line_counts[ref['file_id']] for ref in refs),
        'all_markdown_local_links_resolve': all(p.is_file() or p in generated for p in local_links),
        'markdown_has_one_data_row_per_key': all(markdown.count('<code>' + r['key'] + '</code>') == 1 for r in rows),
        'input_hashes_unchanged': all(sha256(Path(item['path'])) == item['sha256'] for item in data['input_manifest']),
    }
    result = {'date': data['date'], 'all_passed': all(checks.values()), 'checks': checks,
              'record_count': len(rows), 'source_grades': data['source_grades'], 'categories': data['categories'],
              'priorities': data['priorities'], 'display_priority_bands': data['display_priority_bands'],
              'input_manifest': data['input_manifest'],
              'generator': {'path': source_path(__file__), 'sha256': sha256(Path(__file__))}}
    if not result['all_passed']:
        raise AssertionError(result)
    return result


def main():
    data, review = make_catalog()
    markdown = render_markdown(data)
    verification = verify(data, review, markdown)
    json_path, md_path = OUT / 'data/buff-display-whitelist.json', OUT / '01-buff-catalog.md'
    dump(json_path, data)
    md_path.write_text(markdown, encoding='utf-8')
    verification['output_manifest'] = [{'path': source_path(p), 'sha256': sha256(p), 'bytes': p.stat().st_size}
                                       for p in (json_path, md_path)]
    dump(OUT / 'data/catalog-verification.json', verification)
    print(json.dumps({'all_passed': True, 'records': len(data['records']), 'categories': data['categories']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
