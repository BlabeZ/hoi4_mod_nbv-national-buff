# -*- coding: utf-8 -*-
"""Read-only source audit; writes only its two audit artifacts beside this script."""
from pathlib import Path
import collections
import hashlib
import json

ROOT = Path('D:/projects/hoi4_mod/1')
DATA = ROOT / 'hoi4-national-buff/tools/data'
GAME = Path('E:/Steam/steamapps/common/Hearts of Iron IV')
OUT = ROOT / 'nbv-test-workspace'

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

registry = load(DATA / 'metric-index.json')
layout = load(DATA / 'display-layout.json')
formats = {r['key']: r for r in load(DATA / 'modifier-format-bindings.json')['records']}
by_id = {r['id']: r for r in registry['records']}
shown = {r['key'] for r in layout['records']}
tables = {p.name: load(p) for p in DATA.glob('*source-bindings.json')}

# Every statement below refers to shipped source or records its remaining uncertainty.
reviews = {
    'army_morale': (
        'independent_key_unit_pending',
        'army_morale_factor 有精确百分比模板；army_morale 是独立注册键，原版大型部队战术分支奖励直接赋值 0.1。基础恢复率增量的具体计量和最终计算层尚未通过引擎差分确认，不能直接套用百分比。',
        '陆军师组织度恢复速率（基础项，单位待核实）',
        [('common/doctrines/subdoctrines/land/infantry_subdoctrines.txt', 230), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 297)]),
    'army_org': (
        'distinct_fixed_and_percentage_confirmed',
        'army_org_tt 明确使用未缩放数值 +=1，army_org_factor_tt 使用 +=%1。分别为固定组织度增量与比例加成；不能合并为一个读数。日本、法国、中共及暹罗国家精神使用固定项，澳大利亚国家动态精神也使用固定项。',
        '陆军师组织度（固定值）',
        [('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 284), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 285), ('common/ideas/comchina.txt', 240), ('common/dynamic_modifiers/TAOG_dynamic_modifiers.txt', 984)]),
    'experience_gain_army_factor': (
        'distinct_fixed_and_percentage_confirmed',
        'experience_gain_army_tt 使用 +=2 固定值模板，experience_gain_army_factor_tt 使用 +=%1 百分比模板。当前只显示固定值，比例加成漏展示。',
        '陆军经验增长（百分比）',
        [('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 253), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 255)]),
    'max_dig_in_factor': (
        'distinct_fixed_and_percentage_confirmed',
        'max_dig_in_tt 为 +=1 固定堑壕增量，max_dig_in_factor_tt 为 +=%1 比例加成。当前显示固定项，比例项漏展示。',
        '堑壕上限（百分比）',
        [('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 765), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 766), ('common/ideas/switzerland.txt', 626)]),
    'dig_in_speed': (
        'independent_key_unit_pending',
        '两个键均独立注册且实际赋值。国家精神 SWI_spirit_of_helvetia_defensive_war 使用 dig_in_speed=0.3；领袖能力另有 6.0。dig_in_speed_factor 有百分比模板，但 dig_in_speed 的原版精确模板和计算层未确认。现有格式表按同名类比为百分比，不足以证明单位或两键等价。只列国家持有贡献，领袖能力的单位对象贡献仍排除。',
        '堑壕速度（基础项，单位待核实）',
        [('common/ideas/switzerland.txt', 625), ('common/abilities/generic_leader_abilities.txt', 379), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 343)]),
    'modifier_army_sub_unit_cavalry_attack_factor': (
        'distinct_modifier_route_scope_partly_confirmed',
        '与 cavalry_attack_factor 是两个独立注册键。unit_modifiers.txt 明确将长键注册为指定 sub_unit cavalry 的修正；短键为原生 cavalry 修正。两者都可由国家精神持有，前者已见军阀政府和意大利/阿富汗动态精神，不能因含 sub_unit 就当作单个单位对象排除。短键针对何种师分类、长键对营贡献如何聚合及二者叠加公式尚未做引擎战斗差分，不断言互为别名或给出完整公式。',
        '骑兵攻击（骑兵营修正）',
        [('common/units/unit_modifiers/unit_modifiers.txt', 1), ('common/units/unit_modifiers/unit_modifiers.txt', 23), ('common/ideas/china_warlord.txt', 111), ('common/ideas/poland.txt', 1891), ('common/dynamic_modifiers/bba_dynamic_modifiers.txt', 440)]),
    'modifier_army_sub_unit_cavalry_defence_factor': (
        'distinct_modifier_route_scope_partly_confirmed',
        '与 cavalry_defence_factor 是两个独立注册键。长键在 unit_modifiers.txt 明确注册为 sub_unit cavalry 防御；短键为原生 cavalry 防御。军阀政府及意大利/阿富汗动态精神对国家提供长键，不能用短键替代读取。准确战斗计算层仍待引擎差分，不能按同中文名合并。',
        '骑兵防御（骑兵营修正）',
        [('common/units/unit_modifiers/unit_modifiers.txt', 4), ('common/units/unit_modifiers/unit_modifiers.txt', 24), ('common/ideas/china_warlord.txt', 110), ('common/ideas/poland.txt', 1892), ('common/dynamic_modifiers/bba_dynamic_modifiers.txt', 459)]),
    'experience_gain_navy_factor': (
        'distinct_fixed_and_percentage_confirmed',
        'experience_gain_navy_tt 使用 +=2 固定值模板，experience_gain_navy_factor_tt 使用 +=%1 百分比模板。当前只显示固定值，比例加成漏展示。',
        '海军经验增长（百分比）',
        [('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 257), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 259)]),
    'navy_org': (
        'distinct_fixed_and_percentage_source_inferred',
        '中央军事委员会国家精神直接赋值 navy_org=5，原版 navy_org_factor 使用百分比模板。这强烈支持前者是未缩放固定组织度、后者为比例项；前者尚无精确 RIGHT 模板或本轮引擎差分，单位结论标为源码支持的推断。',
        '海军组织度（固定值）',
        [('common/ideas/comchina.txt', 243), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 286), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 288)]),
    'naval_morale_factor': (
        'independent_key_unit_pending_for_retained',
        '遗漏的 naval_morale_factor 有精确 +=%1 模板，是确定的百分比项。已显示 naval_morale 的单位却未确认：现有格式表引用 ITA_supermarina_rm_tt 的 MODIFIER_NAVAL_MORALE +10%，但实际国策修改 ITA_rm_naval_morale_factor，动态表写入 naval_morale_factor，不能据同名提示证明 naval_morale 的单位。比利时国家精神确实另用 naval_morale=0.15。应独立保留键并核实当前已显示项单位。',
        '海军组织度恢复速率（百分比）',
        [('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 302), ('common/ideas/belgium.txt', 373), ('localisation/english/bba_focus_l_english.yml', 1406), ('common/national_focus/italy.txt', 6276), ('common/dynamic_modifiers/bba_dynamic_modifiers.txt', 1039)]),
    'air_accidents': (
        'independent_key_unit_pending',
        'air_accidents_factor 有精确百分比模板。独立的 air_accidents 被暹罗国家精神气象广播赋值 -0.1，天气静态块也用该键；本页面只能读取国家持有部分。现有格式表援引 ETH_bring_in_foreign_advisors_tt 的 MODIFIER_AIR_ACCIDENTS -15%，但对应国策和动态表实际修改 air_accidents_factor。不能把该提示用来确认无 factor 项的单位、是否为百分点或二者计算层，更不能称两者是别名。',
        '空军事故几率（基础项，单位待核实）',
        [('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 73), ('common/ideas/siam.txt', 1428), ('localisation/english/bba_focus_l_english.yml', 116), ('common/national_focus/ethiopia.txt', 1218), ('common/dynamic_modifiers/bba_dynamic_modifiers.txt', 180)]),
    'experience_gain_air': (
        'distinct_fixed_and_percentage_confirmed',
        'experience_gain_air_tt 使用 +=2 固定值模板，experience_gain_air_factor_tt 使用 +=%1 百分比模板。当前只显示百分比，固定经验增量漏展示。',
        '空军经验增长（固定值）',
        [('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 261), ('localisation/simp_chinese/modifiers_l_simp_chinese.yml', 263)]),
}

def evidence(relative, line):
    path = GAME / relative
    text = path.read_text(encoding='utf-8-sig').splitlines()
    return {'file': path.as_posix(), 'line': line, 'text': text[line - 1]}

records = []
for binding in layout['same_name_bindings']:
    retained = by_id[binding['retained_id']]
    if retained['category'] not in ['陆军', '海军', '空军']:
        continue
    for other_id in binding['other_ids']:
        missing = by_id[other_id]
        key = missing['key']
        if key in shown:
            continue
        status, distinction, proposed, refs = reviews[key]
        refs = list(refs)
        for registry_key in (retained['key'], key):
            source = formats[registry_key]['registry_source']
            refs.append(('documentation/modifiers_documentation.md', source['line']))
        source_counts = {}
        samples = []
        for filename, table in tables.items():
            sources = table.get('by_modifier', {}).get(key, [])
            if not sources:
                continue
            source_counts[filename] = len(sources)
            for source in sources[:2]:
                samples.append({k: source[k] for k in ('source_id', 'source_type', 'name_zh', 'display_name_zh', 'value', 'value_expression', 'source') if k in source})
        format_rows = []
        for fmt_key in (retained['key'], key):
            f = formats[fmt_key]
            format_rows.append({'key': fmt_key, **{k: f[k] for k in ('format_code', 'confidence', 'method', 'value_type', 'display_multiplier')}})
        records.append({
            'name': binding['name'], 'category': retained['category'],
            'retained_id': retained['id'], 'retained_key': retained['key'],
            'omitted_id': other_id, 'omitted_key': key,
            'cause': binding['policy'], 'status': status,
            'distinction': distinction, 'proposed_disambiguated_name': proposed,
            'registered_as_separate_keys': True,
            'alias_equivalence_proven': False,
            'runtime_formula_verified_this_audit': False,
            'current_format_bindings_not_independent_proof': format_rows,
            'evidence': [evidence(rel, line) for rel, line in refs],
            'existing_country_source_binding_counts': source_counts,
            'existing_country_source_binding_total': sum(source_counts.values()),
            'source_samples': samples,
        })

assert len(records) == 12
assert {r['omitted_key'] for r in records} == set(reviews)
report = {
    'date': '2026-10-25', 'game_version': '1.19.3.0',
    'scope': 'Original 559-key registry; same Chinese-name military keys omitted by the display-layout first-binding policy.',
    'production_mutations': False,
    'limitations': ['No native C++ source is shipped with the game.', 'No engine gameplay-formula differential tests were run in this read-only audit.', 'Separate registered keys and actual assignments prove they must not be silently conflated by label; exact effect formula is stated only where evidenced.', 'Source binding counts are catalog candidates, not currently active effects.'],
    'counts': dict(collections.Counter(r['status'] for r in records)),
    'omitted_key_count': len(records),
    'input_sha256': {p.as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA / 'metric-index.json', DATA / 'display-layout.json', DATA / 'modifier-format-bindings.json']},
    'records': records,
}
(OUT / 'same-name-military-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
lines = [
    '# 军事页面同中文名遗漏复核', '',
    '核查日期：2026-10-25。范围：当前原始 559 键登记表与页面同名去重记录，游戏 1.19.3.0。本轮只读核查，未更改页面。', '',
    '共发现 12 组、12 个军事修正键因“同名保留首次绑定”未展示。5 组有原版精确模板确认固定值/百分比区别；海军组织度固定项另有原版 +5 赋值支持。其余独立键不能视作别名，但完整单位或计算层仍需核验。', '',
    '本地发行文件不包含原生 C++ 计算代码。本轮没有运行战斗属性差分测试；源码中的注册键、赋值和本地化格式不等于最终引擎计算公式。以下明确区分可确认内容与待核实内容。', '',
    '| 页面 | 同名 | 当前显示键 | 遗漏键 | 建议区分名称 |',
    '|---|---|---|---|---|',
]
for r in records:
    lines.append(f"| {r['category']} | {r['name']} | `{r['retained_key']}` | `{r['omitted_key']}` | {r['proposed_disambiguated_name']} |")
for r in records:
    lines.extend(['', f"## {r['category']}：{r['name']}", '', r['distinction'], '', f"已有国家来源候选绑定：{r['existing_country_source_binding_total']} 条。该数量不是当前存档的生效来源数。", '', '证据：', ''])
    for e in r['evidence']:
        lines.append(f"- [{Path(e['file']).name}:{e['line']}](<{e['file']}:{e['line']}>)：`{e['text'].strip()}`")
lines.extend(['', '## 对现有格式表的两项警示', '',
    '- `naval_morale` 的百分比推断引用了意大利提示，但实际赋值键是 `naval_morale_factor`，不能据此确认前者单位。',
    '- `air_accidents` 的百分比推断引用了埃塞俄比亚提示，但实际赋值键是 `air_accidents_factor`，不能据此确认前者单位。',
    '', '上述证据不足项已保留为待核实；没有将任何一组断言为别名，也没有未经确认批量补入页面。', ''])
(OUT / 'same-name-military-audit.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'omitted_keys': len(records), 'status_counts': report['counts']}, ensure_ascii=True))
