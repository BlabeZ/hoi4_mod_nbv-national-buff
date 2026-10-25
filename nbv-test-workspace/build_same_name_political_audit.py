# -*- coding: utf-8 -*-
"""Read-only audit of political, industrial and intelligence name collisions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'hoi4-national-buff/tools/data'
GAME = Path('E:/Steam/steamapps/common/Hearts of Iron IV')
registry = json.loads((DATA / 'metric-index.json').read_text(encoding='utf-8'))
formats = {r['key']: r for r in json.loads((DATA / 'modifier-format-bindings.json').read_text(encoding='utf-8'))['records']}
by_key = {r['key']: r for r in registry['records']}

def evidence(path, start, end=None):
    lines = (GAME / path).read_text(encoding='utf-8-sig').splitlines()
    return {'file': str(GAME / path), 'line': start, 'end_line': end or start,
            'excerpt': '\n'.join(lines[start - 1:(end or start)])}

loc = 'localisation/english/modifiers_l_english.yml'
doc = 'documentation/modifiers_documentation.md'
traits = 'common/country_leader/00_traits.txt'
entries = [
    ('conscription_factor', 'conscription', 'confirmed_distinct',
     '国家的征募人口比例乘数；conscription 是征募人口基础比例的直接增量。两者都显示百分号，但不能合并。',
     '可征募人口（比例加成）',
     [evidence(loc, 678, 683), evidence('common/ideas/chile.txt', 525, 530), evidence(doc, 2272, 2280)]),
    ('recruitable_population_factor', 'conscription', 'out_of_scope_state',
     '州对象的可征募人口系数。注册类别只有 state；原版用于州动态修正、顺从度等。按用户排除州／地方对象规则继续排除，不能作为国家遗漏补入。',
     None,
     [evidence(doc, 4552, 4555), evidence('common/dynamic_modifiers/bba_dynamic_modifiers.txt', 269, 286), evidence('common/resistance_compliance_modifiers/compliance_modifiers.txt', 39, 45)]),
    ('send_volunteer_factor', 'send_volunteer_size', 'confirmed_distinct',
     '志愿军可派遣师数的比例加成；已显示的 size 是额外师数固定值。实际原版赋值分别有 2.0 比例与 3 个师。精确取整顺序未做引擎测试。',
     '志愿军陆军师数量上限（百分比）',
     [evidence(loc, 731, 733), evidence('common/country_leader/taog_traits.txt', 272, 280), evidence('common/country_leader/taog_traits.txt', 478, 487), evidence(doc, 4715, 4723)]),
    ('autonomy_gain_warscore_factor', 'autonomy_gain_warscore', 'distinct_key_formula_unverified',
     '两个独立已注册键，原版都在使用且都显示百分比；不能称为固定值／百分比配对。当前源码证据不足以确认两者在自治度增长计算中的相加／相乘顺序，需保留独立键并在接入前进一步验证。',
     '战争贡献度自治度增长（系数）',
     [evidence(doc, 2057, 2065), evidence(loc, 922, 925), evidence(loc, 1055), evidence(traits, 13038, 13044), evidence('common/factions/goals/faction_manifests.txt', 565, 571)]),
    ('autonomy_manpower_share_from_subjects', 'autonomy_manpower_share', 'confirmed_distinct',
     '宗主国对附属国人力要求的修正，区别于附属国自身提供人力份额的修正。英文名称和描述不同，日方共荣圈与领袖使用 from_subjects，自治等级对附属国设置 share。两者均为比例。',
     '附属国人力要求（宗主国）',
     [evidence(loc, 892, 894), evidence(loc, 2605, 2607), evidence(traits, 1552, 1560), evidence('common/dynamic_modifiers/SEA_dynamic_modifiers.txt', 441, 450), evidence('common/autonomous_states/puppet.txt', 17, 24)]),
    ('opinion_gain_monthly_factor', 'opinion_gain_monthly', 'confirmed_distinct',
     '改善关系获得评价的比例加成；已显示键为每月评价固定点数。原版分别赋值 -0.15 与 0.25，描述明确 factor 改善增长效率。',
     '改善关系获得的评价（百分比）',
     [evidence(loc, 426, 428), evidence(doc, 4268, 4276), evidence(traits, 2634, 2641), evidence(traits, 6070, 6085)]),
    ('opinion_gain_monthly_same_ideology_factor', 'opinion_gain_monthly_same_ideology', 'confirmed_distinct',
     '相同意识形态每月评价的比例加成；已显示键为固定评价点。原版精确模板明确百分比，固定键在里宾特洛甫特质中赋值 5。',
     '相同意识形态每月评价（百分比）',
     [evidence(loc, 429, 433), evidence(traits, 13377, 13384), evidence('common/ideas/chile.txt', 710, 715)]),
    ('global_building_slots', 'global_building_slots_factor', 'confirmed_distinct_requested_add',
     '所有州共享建筑位上限的固定数量加成；已显示键为百分比加成。原版精确模板分别 +=0 与 +=%1，实际 fixed 赋值含 2。',
     '地区最大工厂数（固定值）',
     [evidence(loc, 9, 13), evidence('common/ideas/british_raj_goe.txt', 1873, 1879), evidence(doc, 2852, 2860)]),
    ('operation_boost_resistance_outcome', 'boost_resistance_factor', 'distinct_key_formula_unverified',
     '两个单独赋值的修正键，英文也区分 effectiveness 与 efficiency；但当前行动配置的 outcome_modifiers 显式列出 boost_resistance_factor，未列出 operation_boost_resistance_outcome。后者是否由引擎自动接入、是否与前者处于同一计算通道未验证，不能仅凭中文同名断言别名或已覆盖。',
     '加强抵抗组织行动成果',
     [evidence(loc, 1457), evidence(loc, 1747), evidence(traits, 6078, 6088), evidence('common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt', 247, 252), evidence('common/operations/00_operations.txt', 1390, 1395)]),
    ('decryption_factor', 'decryption', 'confirmed_distinct_legacy_context',
     '旧式解密数值的比例加成；已显示键为解密等级／点数固定增量。基础科技为 decryption=1，且受未启用 La Resistance 条件限制；不是新版 decryption_power。',
     '解密（百分比）',
     [evidence(loc, 651, 654), evidence('common/technologies/electronic_mechanical_engineering.txt', 857, 864), evidence(doc, 2358, 2366)]),
    ('encryption_factor', 'encryption', 'confirmed_distinct_legacy_context',
     '旧式加密数值的比例加成；已显示键为加密等级／点数固定增量。基础科技为 encryption=1；不是新版密码强度系数。',
     '加密（百分比）',
     [evidence(loc, 647, 650), evidence('common/technologies/electronic_mechanical_engineering.txt', 728, 739), evidence(doc, 2453, 2461)]),
]

records = []
for missing, displayed, status, distinction, proposed_name, refs in entries:
    row = by_key[missing]
    records.append(dict(name=row['name'], category=row['category'], omitted_key=missing,
                        omitted_id=row['id'], displayed_key=displayed,
                        reason='Previously bound only the first key for the shared Chinese name.',
                        status=status, distinction=distinction, proposed_distinct_label=proposed_name,
                        format={k: formats[missing].get(k) for k in ['format_code', 'value_type', 'confidence', 'display_multiplier']},
                        evidence=refs))

report = dict(schema_version=1, game_version='1.19.3.0', read_only=True,
              scope=['政治', '工业', '情报'], collision_group_count=10,
              omitted_key_count_before_current_change=11,
              confirmed_distinct_global_omissions=8,
              includes_requested_fixed_slots=True,
              remaining_confirmed_distinct_global_omissions_after_requested_add=7,
              distinct_keys_needing_formula_validation=2,
              out_of_scope_state_keys=1,
              warning='静态证据核查；未进行各修正独立注入／公式对照，不宣称所有显示格式与效果算法已引擎验证。',
              records=records)
out = ROOT / 'nbv-test-workspace/same-name-political-audit.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
lines = ['# 政治／工业／情报同名修正核查', '',
         '核查原版 1.19.3.0 与本模组 559 键注册表。共 10 个同名组、11 个此前未显示键。', '',
         '其中 8 个是明确不同的全局词条（含本轮新增固定建筑位），2 个键的具体公式仍待验证，1 个仅属于州对象应继续排除。', '',
         '| 页面 | 中文名 | 已显示键 | 此前遗漏键 | 判断 |', '|---|---|---|---|---|']
for r in records:
    lines.append(f"| {r['category']} | {r['name']} | `{r['displayed_key']}` | `{r['omitted_key']}` | {r['distinction']} |")
lines += ['', '## 原版证据', '']
for r in records:
    lines += [f"### {r['omitted_key']}", '', r['distinction'], '']
    for ref in r['evidence']:
        lines.append(f"- [{Path(ref['file']).name}:{ref['line']}](<{ref['file']}:{ref['line']}>)")
    lines.append('')
lines += ['未修改生产文件；除用户明确要求的固定建筑位，其余不在本审计中自动增补。', '']
out.with_suffix('.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False,indent=2))
