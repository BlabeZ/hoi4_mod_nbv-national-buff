"""Classify and render the local modifier registry; no game files are modified."""
import collections
import html
import json
import math
import re
from pathlib import Path

from modifier_localisation import enrich_modifiers

HERE = Path(__file__).resolve().parent
GUIDE = HERE.parent
CATEGORIES = ['政治', '工业', '陆军', '海军', '空军', '情报']
SLUGS = dict(zip(CATEGORIES, ['politics', 'industry', 'army', 'navy', 'air', 'intelligence']))
MECHANISM_GROUPS = {
    '陆军': ('additional_brigade_column_size', 'automatic_grant_medal_chance',
        'choose_preferred_tactics_cost', 'coastal_bunker_effectiveness_factor',
        'equipment_capture', 'equipment_capture_factor', 'equipment_capture_for_controller',
        'equipment_capture_factor_for_controller', 'field_officer_promotion_penalty',
        'grant_medal_cost_factor', 'railway_gun_bombardment_factor', 'unit_medal_effectiveness',
        'army_fuel_capacity_factor'),
    '工业': ('cic_to_overlord_factor', 'cic_to_target_factor', 'dockyard_donations',
        'equipment_upgrade_xp_cost', 'mic_to_overlord_factor', 'mic_to_target_factor',
        'military_factory_donations', 'scientist_xp_gain_factor', 'special_project_speed_factor'),
    '海军': ('floating_harbor_duration', 'floating_harbor_range', 'refit_ic_cost',
        'refit_speed', 'shore_bombardment_collateral_damage_factor',
        'underway_replenishment_range'),
    '空军': ('static_anti_air_damage_factor', 'static_anti_air_hit_chance_factor',
        'tech_air_damage_factor', 'naval_strike_agility_factor'),
    '情报': ('enemy_spy_negative_status_factor', 'foreign_subversive_activites',
        'subversive_activites_upkeep', 'local_factory_sabotage', 'boost_ideology_mission_factor',
        'boost_resistance_factor', 'control_trade_mission_factor',
        'diplomatic_pressure_mission_factor', 'root_out_resistance_effectiveness_factor'),
    '政治': ('annex_cost_factor', 'annex_subject_cost_factor', 'can_guarantee_other_ideologies',
        'can_master_build_for_us', 'disabled_ideas', 'embargo_cost_factor',
        'embargo_threshold_factor', 'female_random_country_leader_chance',
        'forced_surrender_limit', 'guarantee_cost', 'improve_relations_maintain_cost_factor',
        'max_surrender_limit_offset', 'power_balance_daily', 'power_balance_weekly',
        'puppet_cost_factor', 'required_garrison_factor', 'send_volunteer_factor',
        'send_volunteer_size', 'peace_score_ratio_transferred_to_overlord',
        'peace_score_ratio_transferred_to_players'),
}
MECHANISM_CATEGORY = {key: category for category, keys in MECHANISM_GROUPS.items() for key in keys}
for category, doctrines in {
    '陆军': ['cat_deep_battle', 'cat_grand_battle_plan', 'cat_mass_assault',
        'cat_mass_mobilization', 'cat_mobile_warfare', 'cat_superior_firepower',
        'marines_doctrine', 'mountaineers_doctrine', 'paratroopers_doctrine',
        'rangers_doctrine', 'special_forces_generic'],
    '海军': ['cat_base_strike', 'cat_fleet_in_being', 'cat_trade_interdiction'],
    '空军': ['cat_battlefield_support', 'cat_operational_integrity', 'cat_strategic_destruction'],
}.items():
    MECHANISM_CATEGORY.update({name+'_cost_factor': category for name in doctrines})


def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def classify(r, rules):
    k, t, tags = r['key'].lower(), r['template'] or '', set(r['engine_categories'])
    related = []
    for tag, cat in [('naval', '海军'), ('air', '空军'), ('army', '陆军'), ('intelligence_agency', '情报')]:
        if tag in tags:
            related.append(cat)
    if re.search(r'conscription|manpower|population', k):
        related.append('陆军')
    if '<EquipmentModule>' in t:
        for marker, cat in [('ship_', '海军'), ('tank_', '陆军'), ('air_', '空军')]:
            if marker in k:
                related.append(cat)
    if r['key'] in rules:
        return rules[r['key']]['category'], related, '人工审查规则'
    if k in MECHANISM_CATEGORY:
        return MECHANISM_CATEGORY[k], related, '机制人工归类补充'
    if k.startswith('license_'):
        return '工业', related, '装备生产许可证机制'
    if '<Operation>' in t or re.search(r'intel|operative|agency|encrypt|decrypt|crypto|operation_(cost|risk|outcome)', k):
        return '情报', related, '情报机制与参数模板'
    if any(x in t for x in ['<Building>', '<Resource>', '<Technology>', '<EquipmentModule>']) or re.search(
            r'production|industrial|industry|research|construction|building|resource|fuel|energy|consumer_goods|conversion_cost|design_cost|military_industrial', k):
        return '工业', related, '建设生产科研资源机制'
    if re.search(r'^ai_', k):
        return '政治', related, 'AI策略控制单列政治高级项'
    if re.search(r'naval|navy|ship|convoy|submarine|carrier|torpedo|fleet|admiral|screening|sortie|^repair_speed_factor$', k):
        return '海军', related, '海战与舰队机制'
    if re.search(r'^air_|airforce|fighter|bomber|bombing|pilot|^ace_|^ground_attack|^cas_|^aircraft', k):
        return '空军', related, '航空任务与飞机机制'
    if any(x in t for x in ['<Ideology>', '<IdeaCategory>', '<IdeaGroup>']) or re.search(
            r'politic|stability|war_support|conscription|manpower|population|autonomy|diploma|opinion|ideology|drift|legitimacy|resistance|compliance|occupation|trade|faction|war_goal|wargoal|tension', k):
        return '政治', related, '政治外交人口治理机制'
    if re.search(r'army|land_|infantry|artillery|armo[u]?r|cavalry|motorized|mechanized|division|special_forces|supply|attrition|training|planning|reinforce|dig_in|combat|breakthrough|recon|organisation|organization|coordination', k):
        return '陆军', related, '陆战与后勤机制'
    if '<SpecialProject>' in t:
        return '工业', related, '特别项目研发归工业'
    for tag, cat in [('intelligence_agency', '情报'), ('naval', '海军'), ('air', '空军'), ('army', '陆军'),
                     ('unit_leader', '陆军'), ('war_production', '工业'), ('military_advancements', '工业'), ('scientist', '工业')]:
        if tag in tags:
            return cat, related, '原版机制标签辅助归类'
    if '<CombatTactic>' in t or '<Trait>' in t or '<Doctrine>' in t or '<Unit>' in t:
        return '陆军', related, '军事对象模板默认归类，需结合具体对象'
    return '政治', related, '公共机制归政治，未细分人工复核'


def binding_advice(r):
    k = r['key']
    if 'Boolean' in r['doc_display']:
        return '布尔规则开关；按是/否展示，先确认作用对象'
    if k.startswith('ai_'):
        return 'AI行为参数；放高级说明，不作为玩家国家战力总量'
    if 'against' in k or 'targeted' in k:
        return '涉及指定目标国家或对象；不能直接解释为无条件国家总量'
    if k.startswith('state_') or k.startswith('local_') or 'terrain_limit' in k:
        return '地区或条件相关；区分国家来源与地区最终效果，读取路径待实测'
    if '<Operation>' in (r['template'] or ''):
        return '指定秘密行动修正；参数是行动类型，国家读取及实际行动应用需核验'
    if r['buff_mods']:
        return '现有BUFF模组尝试以国家modifier@读取；仍需校验键名、单位、范围与刷新'
    if any('/ideas/' in e['relative_file'] or '/dynamic_modifiers/' in e['relative_file'] or
           '/country_leader/' in e['relative_file'] for e in r['examples']):
        return '有国家效果定义语境；可列国家统计候选，尚未逐项运行验证'
    return '对象与读取作用域待核验；引擎Categories不是国家读取白名单'


def enrich(data, game):
    records = data['records']
    loc_summary = enrich_modifiers(records, game)
    policy = json.loads((HERE/'modifier_priority_rules.json').read_text(encoding='utf-8'))
    rules = policy['rules']
    by_key = {r['key']: r for r in records}
    max_n = max(r['definition_count'] for r in records)
    max_f = max(r['file_count'] for r in records)
    for r in records:
        k = r['key']
        r['category'], secondary, r['category_basis'] = classify(r, rules)
        r['related_categories'] = [x for x in dict.fromkeys(secondary) if x != r['category']]
        rule = rules.get(k)
        if rule:
            r['priority'] = rule['priority']
            r['priority_reason'] = rule['reason']
            r['priority_basis'] = '人工候选审查'
        elif r['buff_mods']:
            r['priority'], r['priority_reason'], r['priority_basis'] = 'P1', '现有BUFF模组已选取的补充指标，仍需核验读值', '模组采纳候选'
        elif not k.startswith('ai_') and r['file_count'] >= 20 and r['definition_count'] >= 50:
            r['priority'], r['priority_reason'], r['priority_basis'] = 'P1', '原版跨文件使用较广，建议作为分类页候选复核', '频次筛选待人工复核'
        elif r['definition_count'] or r['reference_count']:
            r['priority'], r['priority_reason'], r['priority_basis'] = 'P2', '原版有静态使用记录，适合作为扩展或专项指标', '源码使用证据'
        else:
            r['priority'], r['priority_reason'], r['priority_basis'] = 'P3', '引擎注册支持，本扫描未发现修正定义赋值；按需要选取', '注册目录'
        r['evidence_score'] = round(40*math.log1p(r['definition_count'])/math.log1p(max_n)
            +25*math.log1p(r['file_count'])/math.log1p(max_f)
            +15*min(r['family_count'], 5)/5+20*len(r['buff_mods'])/2, 2)
        relatives = list(rule.get('related_keys', [])) if rule else []
        if k.endswith('_factor') and k[:-7] in by_key:
            relatives.append(k[:-7])
        if k+'_factor' in by_key:
            relatives.append(k+'_factor')
        r['related_keys'] = [x for x in dict.fromkeys(relatives) if x in by_key and x != k]
        r['related_unregistered_keys'] = [x for x in relatives if x not in by_key]
        r['binding_advice'] = binding_advice(r)
        if r['description_zh']:
            r['effect_summary'] = r['description_zh']
            r['effect_basis'] = '原版中文说明'
        elif r['doc_description']:
            r['effect_summary'] = (r['name_zh'] or k) + '。引擎模板说明：' + r['doc_description']
            r['effect_basis'] = '原版模板说明与明确标注的编辑名称'
        elif r['name_zh']:
            r['effect_summary'] = '作用项：' + r['name_zh'] + '。本地原版未提供详细公式说明。'
            r['effect_basis'] = '原版名称，公式未确认'
        else:
            r['effect_summary'] = '作用名称未确认；保留原始键与定义位置供复核。'
            r['effect_basis'] = '未确认，不据键名编造公式'
        r['warnings'] = []
        if any(e['case_normalized'] for e in r['buff_mod_expressions']):
            r['warnings'].append('BUFF模组原字符串为大写；此处仅归并覆盖统计，不证明引擎大小写兼容')
        if k == 'repair_speed_factor':
            r['warnings'].append('原版为船只修理速度；两BUFF模组的工厂修复标签错配，应改用industry_repair_factor')
        if k == 'army_non_core_defence_factor':
            r['warnings'].append('UI版还将此值错误用于非核心攻击标签；正确攻击键是army_non_core_attack_factor')
        if k == 'sortie_efficiency':
            r['warnings'].append('普通版重复用于两个标签；重复引用不增加独立指标数')
        if k == 'own_operative_detection_chance_factor':
            r['warnings'].append('UI版两个条目重复引用')
        if k == 'operation_risk':
            r['warnings'].append('已由<Operation>_risk模板的operation参数确认；纠正此前仅搜索固定标题的疑点')
        if k == 'max_organisation':
            r['warnings'].append('原版标签列naval，但源码也在陆军单位属性中使用同名键；频次包含不同对象语境，不能合并解释为国家组织度')
        if r['localisation_editorial_name']:
            r['warnings'].append('中文名由模板说明与对象名称组合，属于编辑名称')
    data['localisation_summary'] = loc_summary
    data['classification_policy'] = policy['category_policy']
    data['unmatched_curated_rules'] = [k for k in rules if k not in by_key]
    data['statistics']['categories'] = {c: {
        'total': sum(r['category']==c for r in records),
        'with_definitions': sum(r['category']==c and r['definition_count']>0 for r in records),
        'p0': sum(r['category']==c and r['priority']=='P0' for r in records),
        'p1': sum(r['category']==c and r['priority']=='P1' for r in records)} for c in CATEGORIES}
    data['statistics']['priority_counts'] = dict(collections.Counter(r['priority'] for r in records))
    data['statistics']['boolean_keys'] = sum('Boolean' in r['doc_display'] for r in records)
    return data


def md_cell(s, limit=None):
    s = str(s or '').replace('|', '\\|').replace('\n', ' ').replace('\r', '')
    return s[:limit]+'…' if limit and len(s)>limit else s


def file_link(label, path, line=None):
    p = Path(path).as_posix() + (':' + str(line) if line else '')
    return '['+label+'](<' + p + '>)'


def table(records, brief=False):
    lines = ['| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |',
             '|---|---|---:|---|---|']
    for r in records:
        selected = '、'.join({'decision':'决议','ui':'UI'}[x] for x in r['buff_mods']) or '未选'
        name = r['name_zh'] or r['name_en'] or '名称待核验'
        label = file_link(r['key'], r['doc_source'], r['doc_line']) + '<br>' + md_cell(name)
        reason = r['priority_reason'] if brief else r['effect_summary']
        lines.append('| '+r['priority']+' | '+label+' | '+str(r['definition_count'])+'／'+str(r['file_count'])+
                     ' | '+selected+' | '+md_cell(reason, 160)+' |')
    return '\n'.join(lines)


def render_markdown(data, out):
    records = data['records']
    ordered = sorted(records, key=lambda r:(r['priority'], -r['evidence_score'], r['key']))
    stats = data['statistics']
    for category in CATEGORIES:
        group = [r for r in ordered if r['category']==category]
        content = '# '+category+'修正目录\n\n'
        content += '共 '+str(len(group))+' 项；这是主类归档，跨领域关联和完整字段见 [离线检索页](../catalog.html) 与 [完整数据](data/catalog.json)。\n\n'
        content = content.replace('(data/catalog.json)', '(../data/catalog.json)')
        content += '“定义次数”是本机原版源码的上下文过滤赋值计数，不是存档触发率。P0 为核心候选，P1 为分类页重点候选，P2 为专项扩展，P3 为仅注册或未发现定义赋值。名称由模板组合时可在检索页查看标记。\n\n'
        content += table(group)
        content += '\n'
        (out/'categories').mkdir(parents=True, exist_ok=True)
        (out/'categories'/ (SLUGS[category]+'.md')).write_text(content, encoding='utf-8')
    p0 = [r for r in ordered if r['priority']=='P0']
    important = '# 重要修正词条与选择依据\n\n'
    important += '本表是第一轮完整目录候选；国家全局 BUFF UI 的最终选项请优先使用 [二次筛选白名单](global-buff-review/README.md)。\n\n'
    important += '推荐优先级与源码证据评分分别列出。P0/P1 是统计页面候选，不代表已经逐项确认 ROOT.modifier@ 的读值、单位或实时性。\n\n'
    important += '证据分 = 40 × log(1+定义次数)/log(1+最大定义次数) + 25 × log(1+文件数)/log(1+最大文件数) + 15 × min(内容类型数,5)/5 + 20 × 模组采纳数/2。对数压缩抑制重复脚本的影响；该分数仅用于同优先级内排序。采纳数按规范键归并，大小写差异单独记录。\n\n'
    important += '人工核心候选共 **'+str(len(p0))+' 项**。AI倾向、目标限定与对象局部数值不会仅因高频自动变成通用国家总量。\n\n'
    for c in CATEGORIES:
        important += '## '+c+'\n\n'+table([r for r in p0 if r['category']==c], True)+'\n\n'
    omitted = sorted([r for r in records if r['priority']=='P0' and not r['buff_mods']],key=lambda r:-r['definition_count'])
    important += '## 两个 BUFF 模组遗漏的核心候选\n\n'+table(omitted, True)+'\n\n'
    important += '## P1 分类页重点候选\n\n这些项目适合分类页或专项详情。部分来自频次门槛筛选，仍需人工确认具体统计对象；完整数据逐项保留 priority_basis。\n\n'
    for c in CATEGORIES:
        important += '### '+c+'\n\n'+table([r for r in ordered if r['category']==c and r['priority']=='P1'], True)+'\n\n'
    important += '## 关联解读\n\n'
    important += '政治点固定增量与获取系数、征兵比例与征兵系数、工厂产出与效率上限／增长／保持、陆军攻击与核心／非核心条件、国家修正与目标国家修正应分别显示。同族名称和共同出现不构成计算公式。完整数据的 related_keys 是人工或同族命名关联；cooccurring_keys 是同一脚本定义块中共同出现的统计关联，均不能直接当作因果或相加／连乘关系。\n'
    (out/'important-modifiers.md').write_text(important,encoding='utf-8')
    catrows = '\n'.join('| '+c+' | '+str(v['total'])+' | '+str(v['with_definitions'])+' | '+str(v['p0'])+' | '+str(v['p1'])+' |' for c,v in stats['categories'].items())
    index = f'''# 原版修正完整目录与重要词条分析

统计日期：2026-10-24。游戏版本：**{data['game_version']}**。数据来自本机原版安装的引擎文档、简体中文与英文本地化，以及 common、events、history 中的规则脚本，包含已整合到原版安装的 DLC 玩法内容。

本次目录共 **{stats['registry_keys']:,} 个具体修正键**，来自 **{stats['fixed_blocks']} 个固定键**和 **{stats['template_blocks']} 个参数模板定义块**。模板展开后的建筑、地形、行动、学说等对象变体属于独立具体键。3 个脚本自定义声明已在引擎文档中出现，合并元数据后不增加总数。

已扫描 **{stats['scanned_files']:,} 个规则文件**，记录 **{stats['occurrences']['definition']:,} 处修正定义赋值**，覆盖 **{stats['keys_with_definitions']} 个键**。另外保留 {stats['occurrences']['other_assignment']:,} 处其他同名赋值和 {stats['occurrences']['reference']} 处动态读取引用；它们没有混入修正定义频次。

## 使用入口

- [国家全局 BUFF 二次筛选](global-buff-review/README.md)：后续展示白名单以二次作用域与来源复核结果为准。
- [可搜索和筛选的离线目录](catalog.html)：六类筛选、重要性、频次排序、模组覆盖、单项详情与源码链接。
- [重要词条分析](important-modifiers.md)：核心候选、两模组遗漏、高频证据和关联解释。
- [完整结构化数据](data/catalog.json)：每项的名称、作用证据、模板、类型、分类、频次、来源、关联、推荐和核验标记。
- [逐次出现记录](data/occurrences.jsonl)：每个匹配的文件、行号、值、父块路径和分类规则。
- [源文件哈希清单](data/source-manifest.json)：用于版本更新后复核。
- [核验结果](verification.json)：注册数量、模板、计数和链接等一致性检查。
- [离线页面功能核验](html-verification.json)：搜索、筛选、排序、分页和转义；使用 DOM 模拟执行页面原脚本，未包含浏览器视觉测试。

## 六类归档

每项分配一个主类，并保留关联军种标签。工业包括科研、资源、燃油和船坞产出；情报包括各军种情报；征兵和人口归政治、关联陆军。引擎 Categories 原样保留，不能把它当成严格作用域白名单。

| 主类 | 全部键 | 有定义赋值的键 | P0 核心候选 | P1 分类候选 |
|---|---:|---:|---:|---:|
{catrows}

分类目录：{' · '.join('['+c+'](categories/'+SLUGS[c]+'.md)' for c in CATEGORIES)}。

工业键数量较多，主要因为建筑与地形限制等参数模板展开了大量具体变体；数量不代表展示优先级。当前选出 {stats['priority_counts']['P0']} 个 P0 核心候选及 {stats['priority_counts']['P1']} 个 P1 分类页候选，其中 30 个 P1 由频次门槛初筛，仍保留待人工复核标记。

两个 BUFF 模组按原始字符串分别选取 126／128 个不同键；与完整注册表做明确标记的大小写归并后，分别匹配 125／128 项，合计覆盖 128 个规范键。普通版的 initiative 未匹配；大写字段的归并只用于覆盖统计，不证明运行兼容。两模组未选的 P0 核心候选共 15 项，见重要词条分析。

## 必要信息与作用证据

每项记录规范 key、原版中英文名称、作用说明及来源、引擎机制标签、原文数值类型和显示精度、参数模板与对象、六类归属、读取建议、两模组覆盖、原版使用次数／文件数／内容类型数、示例源码、关联词条和推荐理由。

固定键的引擎定义没有详细 Description，所以作用说明优先采用原版中文说明，其次原版名称与使用语境。参数项使用模板说明和对象名称；编辑组合名称有明确标记。缺失名称或公式保留为待核验，不按英文键名编造效果。

当前有 {data['localisation_summary']['counts'].get('has_chinese_name',0):,} 项提供中文名称，其中 {data['localisation_summary']['counts'].get('template_derived',0):,} 项采用明确标记的模板组合名；{data['localisation_summary']['counts'].get('unmatched',0)} 项尚无可靠名称映射，保留原始键。原版中文详细说明覆盖 {data['localisation_summary']['counts'].get('has_chinese_description',0)} 项；“已收录”不等于“公式与实际运行行为均已验证”。

原版文档将大部分项记为 Number，这不等于应该按整数显示，也不能据此否定百分比。{stats['boolean_keys']} 个 Boolean 项应按开关处理。具体单位、正负有利方向、叠加公式和 ROOT.modifier@ 可读性需要按机制核验；factor 后缀本身不足以证明一律连乘。

## 频次口径

扫描先去除注释并区分引号字符串，识别 key = value 的父块上下文。modifier 等载荷、动态修正定义体和明确机制数据目录内的赋值计为定义；条件、AI权重、变量操作及无法确认的同名赋值另列。原版史料中的 local_supplies 等地区初始属性不会直接当作国家 BUFF 频次。具体分类规则保存在生成器 usage_kind 中，每条证据也保存规则名。

频次是**静态源码使用量**，不是运行触发率、持续时间、修正强度或战略价值；包含可选国家路线和安装内容，不模拟当前存档、DLC启用组合或引擎内部生成效果。零赋值键仍保留，它可能仅被引擎使用、预留，或需要未选定内容。以源码频次、跨文件覆盖、两模组选取和人工游戏机制审查共同判断重要性。

原版定义包含基础对象属性与条件修正，定义出现不自动代表国家总量可读。typed_data_body 为按目录语境判断的定义候选，完整证据保留供复核。共现关联只表示位于同一赋值块，不表示两个值可以相加或连乘。

## 本轮纠正和扩展

此前只查固定标题而对 operation_risk 留下疑点；本轮完整展开发现它由 <Operation>_risk 模板、operation 参数生成，已确认在引擎注册目录中。普通版 initiative 不在完整目录，规范主动性键是 initiative_factor。两个模组中的大写 SPECIAL_FORCES_* 按规范小写键归并统计，但大小写运行兼容仍未由本次静态分析证明。

两版工厂修复标签对应船只修理值、UI版非核心攻击读成防御、重复项等原有问题继续保留。模组选取只是候选证据，不能替代正确性检查。

## 可重复生成

生成器：[build_vanilla_modifier_catalog.py](../tools/build_vanilla_modifier_catalog.py)。在项目中运行：

```powershell
python .\\hoi4-modding-guide\\tools\\build_vanilla_modifier_catalog.py --stage all
```

只刷新分类、本地化或推荐规则时可使用 --stage render 复用扫描结果。整个流程只读取游戏及模组文件，输出写入本资料目录。本次没有启动游戏，不包含逐项运行读数验证。
'''
    (out/'README.md').write_text(index,encoding='utf-8')


def render_html(data, out):
    fields = ['key','name_zh','name_en','category','related_categories','category_basis','priority','priority_basis',
        'priority_reason','definition_count','file_count','family_count','content_families','reference_count',
        'other_assignment_count','evidence_score','buff_mods','effect_summary','effect_basis','engine_categories',
        'doc_display','doc_source','doc_line','template','parameter','binding_advice','related_keys','cooccurring_keys',
        'localisation_method','warnings','examples','localisation_sources']
    payload = [{k:r[k] for k in fields} for r in data['records']]
    json_data = json.dumps(payload,ensure_ascii=False).replace('</','<\\/')
    page = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HOI4 原版修正目录</title><style>
:root{color-scheme:light;--ink:#192b40;--muted:#627286;--line:#dce4ec;--blue:#175b89}*{box-sizing:border-box}body{margin:0;background:#f3f6f9;color:var(--ink);font:15px/1.6 "Microsoft YaHei",system-ui,sans-serif}header,main{max-width:1480px;margin:auto;padding:28px 36px}header{padding-bottom:12px}h1{font-size:30px;margin:0 0 8px}p{margin:8px 0}.sub{color:var(--muted)}.stats{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.card{background:white;border:1px solid var(--line);border-radius:10px;padding:12px 22px}.card b{font-size:25px;color:var(--blue)}.filters{display:flex;gap:12px;flex-wrap:wrap;background:white;padding:18px;border:1px solid var(--line);border-radius:10px}input,select,button{font:inherit;padding:9px 11px;border:1px solid #b8c8d8;border-radius:6px;background:white;color:var(--ink)}input{flex:1;min-width:270px}button{cursor:pointer}button:disabled{opacity:.4}table{width:100%;border-collapse:collapse;background:white}th{text-align:left;background:#e8eff5;padding:11px;position:sticky;top:0}td{padding:12px 11px;border-bottom:1px solid var(--line);vertical-align:top}td.num{text-align:right;white-space:nowrap}code{font:13px/1.5 Consolas,monospace;overflow-wrap:anywhere}summary{cursor:pointer;list-style-position:outside}.tag{display:inline-block;padding:1px 7px;border-radius:5px;background:#e6eff7;font-size:12px}.P0{background:#d8eee7;color:#166044}.P1{background:#dfeafa;color:#235b98}.details{background:#f6f8fb;border-radius:6px;padding:12px;margin-top:10px;font-size:13px;max-width:840px}.details p{margin:7px 0}a{color:var(--blue)}.pager{display:flex;justify-content:space-between;align-items:center;margin:14px 0}.note{padding:10px 14px;border-left:3px solid #7197b1;background:#e9f0f6}.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:8px}footer{color:var(--muted);font-size:13px;margin:22px 0}@media(max-width:800px){header,main{padding:18px}th,td{padding:8px}h1{font-size:24px}.optional{display:none}}
</style><header><div class="sub">本机原版 · __VERSION__ · 2026-10-24</div><h1>修正目录与重要词条</h1><p>按政治、工业、陆军、海军、空军和情报检索。展开词条查看作用证据、关联和源码位置。</p><div class="stats"><div class="card"><b>4,484</b><br>注册具体键</div><div class="card"><b>722 + 42</b><br>固定键与模板块</div><div class="card"><b>__USED__</b><br>有原版定义赋值</div><div class="card"><b>__P0__</b><br>核心候选</div></div><p class="note">频次是源码定义出现次数，不是存档触发率。国家读取、单位与最终战斗属性需分别核验。模板衍生名称和未确认信息在详情中标出。</p></header>
<main><div class="filters"><input id="q" placeholder="搜索中文名称、修正键、作用或关联"><select id="cat"><option value="">全部六类</option><option>政治</option><option>工业</option><option>陆军</option><option>海军</option><option>空军</option><option>情报</option></select><select id="tier"><option value="">所有优先级</option><option value="P0">P0 核心候选</option><option value="P1">P1 分类重点</option><option value="P2">P2 专项扩展</option><option value="P3">P3 注册目录</option></select><select id="coverage"><option value="">所有模组覆盖</option><option value="yes">BUFF 模组已选</option><option value="no">两模组未选</option></select><select id="sort"><option value="priority">按优先级与证据分</option><option value="definition_count">按定义次数</option><option value="file_count">按文件数</option><option value="key">按修正键</option></select><label><input id="used" type="checkbox" style="min-width:0">仅有定义赋值</label></div>
<div class="pager"><span id="count"></span><div><button id="prev">上一页</button> <span id="page"></span> <button id="next">下一页</button></div></div><div class="tablewrap"><table><thead><tr><th>分类</th><th>词条与作用详情</th><th>优先级</th><th>定义次数</th><th>文件数</th><th class="optional">BUFF 模组</th><th class="optional">证据分</th></tr></thead><tbody id="body"></tbody></table></div>
<footer>数据完全保存在本文件中，不需要联网。<a href="README.md">方法与范围</a> · <a href="important-modifiers.md">重要词条分析</a> · <a href="data/catalog.json">完整 JSON</a> · <a href="data/occurrences.jsonl">逐次源码证据</a></footer></main>
<script id="catalog-data" type="application/json">__DATA__</script><script>
const DATA=JSON.parse(document.getElementById('catalog-data').textContent),$=id=>document.getElementById(id);let page=0,filtered=[];const size=60;
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const src=(p,l,label)=>'<a href="'+esc('file:///'+p.replaceAll('\\','/'))+'">'+esc(label||p.split(/[\\/]/).pop())+'</a> 第 '+esc(l)+' 行';
function detail(r){return '<div class="details"><p><b>作用：</b>'+esc(r.effect_summary)+'</p><p><b>证据：</b>'+esc(r.effect_basis)+'；名称映射 '+esc(r.localisation_method)+'</p><p><b>读取建议：</b>'+esc(r.binding_advice)+'</p><p><b>推荐理由：</b>'+esc(r.priority_reason)+'（'+esc(r.priority_basis)+'）</p><p><b>引擎标签：</b>'+esc(r.engine_categories.join(', '))+'；原文格式 '+esc(r.doc_display)+'</p><p><b>模板与对象：</b>'+esc(r.template||'固定键')+' / '+esc(r.parameter||'—')+'</p><p><b>关联词条：</b>'+esc(r.related_keys.join(', ')||'—')+'</p><p><b>共现：</b>'+esc(r.cooccurring_keys.map(x=>x.key+' ('+x.shared_definition_blocks+')').join(', ')||'—')+'；仅统计关联</p><p><b>内容类型：</b>'+esc(r.content_families.join(', ')||'未发现定义')+'</p><p><b>其他赋值／读取引用：</b>'+r.other_assignment_count+' / '+r.reference_count+'</p><p><b>注册源：</b>'+src(r.doc_source,r.doc_line)+'</p>'+r.examples.slice(0,3).map(x=>'<p>'+src(x.file,x.line,x.relative_file)+'<br><code>'+esc(x.context.join(' > '))+' > '+esc(r.key)+' = '+esc(x.value)+'</code></p>').join('')+r.warnings.map(x=>'<p class="note">'+esc(x)+'</p>').join('')+'</div>'}
function render(){const terms=$('q').value.toLowerCase().trim().split(/\s+/).filter(Boolean);filtered=DATA.filter(r=>(!$('cat').value||r.category===$('cat').value)&&(!$('tier').value||r.priority===$('tier').value)&&(!$('used').checked||r.definition_count>0)&&(!$('coverage').value||($('coverage').value==='yes'?r.buff_mods.length>0:r.buff_mods.length===0))&&terms.every(t=>[r.key,r.name_zh,r.name_en,r.effect_summary,r.related_keys.join(' ')].join(' ').toLowerCase().includes(t)));const order=$('sort').value;filtered.sort((a,b)=>order==='key'?a.key.localeCompare(b.key):order==='priority'?a.priority.localeCompare(b.priority)||b.evidence_score-a.evidence_score:b[order]-a[order]||a.key.localeCompare(b.key));const pages=Math.max(1,Math.ceil(filtered.length/size));page=Math.min(page,pages-1);$('count').textContent='匹配 '+filtered.length.toLocaleString()+' / '+DATA.length.toLocaleString()+' 项';$('page').textContent=(page+1)+' / '+pages;$('prev').disabled=page===0;$('next').disabled=page>=pages-1;$('body').innerHTML=filtered.slice(page*size,(page+1)*size).map(r=>'<tr><td>'+esc(r.category)+'</td><td><details><summary><b>'+esc(r.name_zh||r.name_en||'名称待核验')+'</b><br><code>'+esc(r.key)+'</code></summary>'+detail(r)+'</details></td><td><span class="tag '+r.priority+'">'+r.priority+'</span></td><td class="num">'+r.definition_count+'</td><td class="num">'+r.file_count+'</td><td class="optional">'+(r.buff_mods.map(x=>x==='ui'?'UI':'决议').join('、')||'未选')+'</td><td class="num optional">'+r.evidence_score+'</td></tr>').join('')||'<tr><td colspan="7">没有匹配词条</td></tr>'}
['q','cat','tier','coverage','sort','used'].forEach(id=>$(id).addEventListener(id==='q'?'input':'change',()=>{page=0;render()}));$('prev').onclick=()=>{page--;render()};$('next').onclick=()=>{page++;render()};render();
</script></html>'''
    page = page.replace('__DATA__',json_data).replace('__VERSION__',html.escape(data['game_version']))
    page = page.replace('__USED__',str(data['statistics']['keys_with_definitions'])).replace('__P0__',str(data['statistics']['priority_counts'].get('P0',0)))
    (out/'catalog.html').write_text(page,encoding='utf-8')


def verify(data, out):
    records = data['records']
    keys = {r['key'] for r in records}
    checks = {
        'unique_registry_keys': len(keys)==len(records)==4484,
        'fixed_and_template_blocks': data['statistics']['fixed_blocks']==722 and data['statistics']['template_blocks']==42,
        'operation_risk_template_resolved': next(r for r in records if r['key']=='operation_risk')['template']=='<Operation>_risk',
        'boolean_type_preserved': data['statistics']['boolean_keys']==14,
        'category_partition': sum(x['total'] for x in data['statistics']['categories'].values())==len(records),
        'all_have_effect_evidence_label': all(r['effect_basis'] for r in records),
        'all_have_binding_advice': all(r['binding_advice'] for r in records),
        'definition_total_consistent': sum(r['definition_count'] for r in records)==data['statistics']['occurrences']['definition'],
        'priority_partition': sum(data['statistics']['priority_counts'].values())==len(records),
        'related_keys_exist': all(k in keys for r in records for k in r['related_keys']),
        'local_sources_exist': all(Path(r['doc_source']).is_file() for r in records),
    }
    result = {'date':'2026-10-24','checks':checks,'all_passed':all(checks.values()),
              'runtime_validation':'not performed','statistics':data['statistics'],
              'localisation':data['localisation_summary']['counts']}
    dump(out/'verification.json',result)
    assert result['all_passed'], result
    print(json.dumps(result,ensure_ascii=False,indent=2))


def render(data, game, out):
    enrich(data,game)
    dump(out/'data/catalog.json',data)
    dump(out/'data/localisation-audit.json',data['localisation_summary'])
    render_markdown(data,out)
    render_html(data,out)
    verify(data,out)
