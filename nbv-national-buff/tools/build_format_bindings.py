"""Build auditable localisation formats for the selected 559 national modifiers.

Original game and legacy mods are read only. Python 3.9+, standard library.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
GUIDE = WORKSPACE / 'hoi4-modding-guide'
WHITELIST = GUIDE / 'buff-statistics-mod/data/buff-display-whitelist.json'
CATALOG = GUIDE / 'vanilla-modifier-catalog/data/catalog.json'
GAME = Path('E:/Steam/steamapps/common/Hearts of Iron IV')
OUT = ROOT / 'tools/data/modifier-format-bindings.json'
LEGACY = {
    'decision': Path('E:/Steam/steamapps/workshop/content/394360/3440479297/localisation/simp_chinese/we_l_simp_chinese.yml'),
    'ui': Path('E:/Steam/steamapps/workshop/content/394360/3795966002/localisation/simp_chinese/BDUI_l_simp_chinese.yml'),
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path, line, kind, **extra):
    return dict(file=str(path).replace('\\', '/'), line=int(line), kind=kind, **extra)


def decimal_places(record):
    match = re.search(r'(\d+) decimal', record.get('doc_display', ''))
    return int(match.group(1)) if match else 2


def parse_format(raw, fallback):
    """Normalise token order without collapsing native percentage modes.

    Vanilla uses both `%` (fraction to percent) and `%%` (percent-point
    value). The latter also occurs in direct [?variable] expressions, e.g.
    goe_focus_l_english.yml's RAJ government-of-India-act tooltip and
    mun_ideas_l_english.yml's CZE Bata Corporation tooltip. Preserve it in
    the generated token; callers must not turn 15 native intel points into
    1500% or replace the raw modifier value merely for display.
    """
    digits = re.findall(r'\d+', raw)
    places = int(digits[-1]) if digits else fallback
    colour = '+' if '+' in raw else '-' if '-' in raw else next((c for c in 'YGR' if c in raw), '')
    percent_token = '%%' if '%%' in raw else '%' if '%' in raw else ''
    percent = bool(percent_token)
    code = colour + '=' + percent_token + str(places)
    direction = {'+': 'positive_good', '-': 'negative_good', 'Y': 'fixed_yellow',
                 'G': 'fixed_green', 'R': 'fixed_red', '': 'neutral'}[colour]
    return {'format_code': code,
            'value_type': 'percentage_points' if percent_token == '%%' else 'percentage' if percent else 'number',
            'precision': places, 'benefit_direction': direction,
            'precision_from_source': bool(digits),
            'display_multiplier': 100 if percent_token == '%' else 1}


def scan_localisation():
    loc, references, literals = defaultdict(list), defaultdict(list), defaultdict(list)
    paths = []
    for language in ('english', 'simp_chinese'):
        for path in sorted((GAME / 'localisation' / language).rglob('*.yml')):
            paths.append(path)
            for line_number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
                match = re.match(r'^\s*([^\s:#]+):\d*\s*"(.*)"\s*$', line)
                if not match:
                    continue
                key, value = match.groups()
                entry = source(path, line_number, 'vanilla_localisation', localisation_key=key)
                entry['value'] = value
                loc[key].append(entry)
                formats = re.findall(r'\$(?:RIGHT|VALUE)\|([^$]+)\$', value)
                if formats:
                    for label in re.findall(r'\$([A-Za-z0-9_]+)\$', value):
                        references[label].append((formats[0], entry))
                for literal in re.finditer(r'\$([A-Za-z0-9_]+)\$\s*:?\s*§([GRY])([+-]?\d+(?:\.\d+)?)(%?)§!', value):
                    label, colour, number, percentage = literal.groups()
                    if colour == 'Y':
                        direction = 'Y'
                    else:
                        positive = not number.startswith('-')
                        direction = '+' if (positive and colour == 'G') or (not positive and colour == 'R') else '-'
                    fmt = direction + '=' + percentage + str(len(number.partition('.')[2]))
                    literals[label].append((fmt, entry, literal.group(0)))
    return loc, references, literals, paths


def compact_entry(entry, kind=None, **extra):
    value = {k: v for k, v in entry.items() if k != 'value'}
    if kind:
        value['kind'] = kind
    value.update(extra)
    return value


def build():
    whitelist, catalog = read_json(WHITELIST), read_json(CATALOG)
    originals = {r['key']: r for r in catalog['records']}
    loc, references, literals, local_paths = scan_localisation()
    results, by_key = [], {}
    for row in whitelist['records']:
        key, old = row['key'], originals[row['key']]
        precision = decimal_places(old)
        candidates = []
        for loc_key in (key + '_tt', key, 'modifier_' + key + '_tt'):
            for entry in loc.get(loc_key, []):
                for fmt in re.findall(r'\$(?:RIGHT|VALUE)\|([^$]+)\$', entry['value']):
                    candidates.append((fmt, entry))
        output = {'key': key, 'name': row['name'], 'format_code': None,
                  'confidence': 'unresolved', 'method': None, 'sources': [], 'notes': [],
                  'runtime_validated': False, 'legacy_formats': []}
        if candidates:
            raw, chosen = candidates[0]
            output.update(parse_format(raw, precision), confidence='confirmed', method='exact_vanilla_tooltip')
            output['sources'] = [compact_entry(e, raw_format=f) for f, e in candidates]
            if len({parse_format(f, precision)['format_code'] for f, e in candidates}) > 1:
                output['notes'].append('中英文／重复原版模板格式不同，采用英文优先的首个精确模板；其余候选保留供核验。')
                output['confidence'] = 'source_inferred'
        elif old.get('custom_definition'):
            definition = old['custom_definition']
            colour = {'good': '+', 'bad': '-', 'neutral': 'Y'}.get(definition.get('color_type'), '')
            typ = definition.get('value_type', 'number')
            raw = colour + '=' + ('%' if typ == 'percentage' else '') + str(definition.get('precision', precision))
            output.update(parse_format(raw, precision), confidence='confirmed', method='custom_modifier_definition')
            output['sources'] = [source(definition['source'], definition['line'], 'modifier_definition',
                                        color_type=definition.get('color_type'), value_type=typ,
                                        precision=definition.get('precision'))]
        for item in old.get('buff_mod_expressions', []):
            output['legacy_formats'].append(source(LEGACY[item['mod']], item['line'], 'legacy_mod_expression',
                                                   mod=item['mod'], source_key=item['source_key'],
                                                   raw_format=item['format']))
        if output['format_code'] is None and output['legacy_formats']:
            legacy = sorted(output['legacy_formats'], key=lambda s: s['mod'] != 'ui')[0]
            output.update(parse_format(legacy['raw_format'], precision), confidence='source_inferred', method='legacy_mod_reuse')
            output['sources'] = [legacy]
            output['notes'].append('复用旧BUFF模组相同读取键的格式；旧模组不是引擎格式定义，仍需与游戏提示对照。')
        names = set(filter(None, [old.get('localisation_key'), old.get('localisation_key_zh'), old.get('localisation_key_en')]))
        if output['format_code'] is None:
            aliases = [candidate for name in sorted(names) for candidate in references.get(name, [])]
            if aliases:
                raw, entry = aliases[0]
                output.update(parse_format(raw, precision), confidence='source_inferred', method='same_label_vanilla_tooltip')
                output['sources'] = [compact_entry(entry, raw_format=raw)]
                output['notes'].append('精确本地化名称被另一原版数值模板引用，按该模板推断；同名不是同单位证明，需实测。')
        if output['format_code'] is None:
            examples = [candidate for name in sorted(names) for candidate in literals.get(name, [])]
            if examples:
                raw, entry, fragment = examples[0]
                parsed = parse_format(raw, precision)
                parsed['precision'] = precision
                parsed['format_code'] = re.sub(r'\d+$', str(precision), parsed['format_code'])
                output.update(parsed, confidence='source_inferred', method='vanilla_named_literal')
                output['sources'] = [compact_entry(entry, sample=fragment)]
                output['notes'].append('原版提示以该精确名称显示有颜色的数值；据此推断百分号和收益方向，小数位采用注册文档。')
        output['registry_source'] = source(old['doc_source'], old['doc_line'], 'modifier_registry', display=old['doc_display'])
        results.append(output)
        by_key[key] = output

    # Explicit cross-key analogies are filled below; no suffix-only automatic rule.
    apply_reviewed_overrides(by_key, originals, loc)
    for output in results:
        if output['format_code'] is None:
            old = originals[output['key']]
            output.update(parse_format('=' + str(decimal_places(old)), decimal_places(old)),
                          method='raw_number_pending_review')
            output['sources'] = [output['registry_source']]
            output['notes'].append('缺少可信的单位／收益方向依据：临时显示未缩放中性原值，不宣称最终单位；必须保留待核验提示。')
        if not output.get('precision_from_source', True):
            output['notes'].append('原格式未显式写小数位；补用该键注册文档的小数位。')
        if output['legacy_formats'] and output['method'] != 'legacy_mod_reuse':
            differences = [s for s in output['legacy_formats'] if parse_format(s['raw_format'], output['precision'])['format_code'] != output['format_code']]
            if differences:
                output['notes'].append('旧BUFF模组格式与本记录不同（可能仅精度不同）；原版精确模板或本条审查结论优先。')
    all_sources = [s for r in results for s in r['sources'] + r['legacy_formats'] + [r['registry_source']]]
    source_files = {path: Path(path).read_text(encoding='utf-8-sig').splitlines() for path in {s['file'] for s in all_sources}}
    inputs = sorted(set([WHITELIST, CATALOG, Path(__file__)] + list(LEGACY.values()) + local_paths
                        + list((GAME/'common/modifier_definitions').glob('*.txt'))
                        + [Path(path) for path in source_files]), key=str)
    verification = {
        '559_unique_keys': len(results) == len(by_key) == 559,
        'same_keyset_and_order_as_whitelist': [r['key'] for r in results] == [r['key'] for r in whitelist['records']],
        'valid_format_tokens_no_pipe': all(re.fullmatch(r'[+\-YGR]?=%{0,2}\d+', r['format_code']) for r in results),
        'every_record_has_sources': all(r['sources'] for r in results),
        'all_source_lines_exist': all(1 <= s['line'] <= len(source_files[s['file']]) for s in all_sources),
        'all_runtime_unvalidated': all(r['runtime_validated'] is False for r in results),
        'only_documented_confidence_levels': all(r['confidence'] in ('confirmed', 'source_inferred', 'unresolved') for r in results),
        'percentage_flag_matches_type': all(('%' in r['format_code']) == (r['value_type'] in ('percentage', 'percentage_points')) for r in results),
        'percentage_points_type_preserved': all(('%%' in r['format_code']) == (r['value_type'] == 'percentage_points') for r in results),
        'percentage_scaling_preserved': all(r['display_multiplier'] == (100 if '%' in r['format_code'] and '%%' not in r['format_code'] else 1) for r in results),
    }
    data = {'schema_version': 1, 'game_version': whitelist['game_version'],
            'policy': {
                'precedence': '精确原版RIGHT模板 > modifier_definitions > 旧BUFF同键表达式 > 精确名称引用/原版带色字面量 > 明确逐键类比；带replace标记的逐键复核可修正推断，保留被替代证据。不按_factor后缀批量猜测。',
                'confidence': {'confirmed': '静态精确原版格式或显式定义已确认；不是运行验证。',
                               'source_inferred': '旧mod、相同名称提示或明确逐键类比支持，仍需对照游戏。',
                               'unresolved': '不能确认单位或收益方向；未缩放中性原值作为临时显示。'},
                'format_code': '不含竖线；保留原版固定黄/绿/红色格式。+=为正向绿，-=为负向绿，%为乘100显示百分比，%%为原值附加百分号；两者不得归并。display_multiplier记录显示缩放，不改变原始读数。',
                'runtime_validated': False},
            'statistics': {'total': len(results), 'confidence': dict(Counter(r['confidence'] for r in results)),
                           'methods': dict(Counter(r['method'] for r in results)),
                           'value_types': dict(Counter(r['value_type'] for r in results)),
                           'benefit_directions': dict(Counter(r['benefit_direction'] for r in results)),
                           'legacy_mod_covered': sum(bool(r['legacy_formats']) for r in results)},
            'verification': dict(all_passed=all(verification.values()), checks=verification),
            'input_manifest': [{'file': str(p).replace('\\', '/'), 'sha256': sha(p)} for p in inputs],
            'records': results}
    assert len(results) == len(by_key) == 559
    assert set(by_key) == {r['key'] for r in whitelist['records']}
    assert all(r['format_code'] and '|' not in r['format_code'] and not r['runtime_validated'] for r in results)
    assert data['verification']['all_passed'], verification
    return data


def apply_reviewed_overrides(by_key, originals, loc):
    def assign(keys, code, reason, analogue=None, extra=(), confidence='source_inferred', replace=False):
        for key in keys.split():
            record = by_key[key]
            if record['format_code'] is not None and not replace:
                continue
            old = originals[key]
            refs = []
            if analogue:
                other = by_key[analogue]
                assert other['format_code'] is not None, analogue
                refs += [dict(s, analogue_key=analogue) for s in other['sources'][:2]]
            for item in old.get('localisation_sources', [])[:2] + old.get('localisation_description_sources', [])[:2]:
                refs.append(source(item['path'], item['line'], 'target_localisation', localisation_key=item['key']))
            samples = [e for e in old.get('examples', []) if 'debug' not in e['relative_file'].lower()]
            if samples:
                e = samples[0]
                refs.append(source(e['file'], e['line'], 'target_assignment', value=e['value'], context=e.get('context', [])))
            refs += list(extra)
            if replace and record['sources']:
                refs += [dict(s, superseded=True) for s in record['sources']]
            raw = code.replace('{p}', str(decimal_places(old)))
            record.update(parse_format(raw, decimal_places(old)), confidence=confidence,
                          method='reviewed_key_override', sources=refs or [record['registry_source']])
            record['notes'].append(reason)
            record['notes'].append('逐键审查推断，保留目标名称/说明、实际赋值及所用类比证据；并非引擎内置格式导出。')

    # Numeric additions: each listed key denotes a count/level/point delta, backed by
    # its own description and assignments. Do not absorb similarly named *_factor keys.
    assign('send_volunteer_size industrial_factory_donations military_factory_donations dockyard_donations',
           '+=0', '名称及原版赋值表示师数/工厂数的增量，不乘100；船坞捐赠未检出赋值，按同一捐赠机制列为推断。')
    assign('communism_acceptance democratic_acceptance fascism_acceptance neutrality_acceptance',
           '+=0', '四种意识形态接纳度使用15/30/75等评价点赋值；增加提高接纳，不是百分比。')
    assign('exiled_government_weekly_manpower', '+=0', '原版以700人等整数设置每周人力，按人数显示。')
    assign('legitimacy_daily opinion_gain_monthly opinion_gain_monthly_same_ideology', '+=2',
           '说明为每日正统性/每月评价点变化，原版存在0.1、0.25、5等赋值，保留两位而不乘100。')
    assign('army_leader_start_level navy_leader_start_attack_level navy_leader_start_defense_level navy_leader_start_level navy_leader_start_maneuvering_level',
           '+=0', '明确是新将领初始等级/技能点的国家修正；原版按1或2等整数赋值。')
    assign('air_invasion_division_cap air_invasion_plan_cap naval_invasion_plan_cap', '+=0',
           '英文说明明确计数对象为师或作战计划；按整数容量增量显示。空降两项仅登记，国家读数仍待实测。',
           analogue='naval_invasion_division_cap')
    assign('carrier_sortie_hours_delay', '-={p}', '名称明确为小时，原版学说赋值-2；延迟降低有利，保留数值小时而非百分比。')
    assign('navy_org', '+={p}', '原版赋值5组织度；与navy_org_factor百分比项独立。以未缩放组织度增量显示。')
    crypto = GAME / 'common/technologies/electronic_mechanical_engineering.txt'
    assign('encryption', '+=0', '旧式加密科技逐级提供encryption=1；保持等级/点数增量，不套用encryption_factor百分比。',
           extra=[source(crypto, 731, 'exact_technology_assignment', value='encryption = 1')])
    assign('decryption', '+=0', '旧式解密科技逐级提供decryption=1。BBA的一条手写提示显示百分号，与基础键/系数键区分有冲突；采用基础点数并保留冲突证据待实测。',
           extra=[source(crypto, 860, 'exact_technology_assignment', value='decryption = 1')], replace=True)

    # Precisely enumerated mechanics and analogous vanilla tooltips; this is not a
    # blanket `_factor => percent` or `cost => bad` heuristic.
    assign('war_support_weekly stability_weekly_factor war_support_weekly_factor', '+=%{p}',
           '对应每周稳定/战争支持的比例变化；与原版稳定度周增量带百分号提示、原版小数赋值对照。', analogue='stability_weekly')
    assign('autonomy_gain_ll_to_overlord_factor autonomy_gain_trade_factor autonomy_gain_warscore_factor', '+=%{p}',
           '说明是对租借/贸易/参战自治增长的影响系数，原版以-0.25等比例赋值；沿用自治增长系数格式。', analogue='autonomy_gain_global_factor')
    assign('faction_trade_opinion_factor opinion_gain_monthly_factor', '+=%{p}',
           '原版说明明确贸易评价/改善关系增长的系数，数值0.1/0.25是比例加成。', analogue='trade_opinion_factor')
    assign('embargo_cost_factor guarantee_cost improve_relations_maintain_cost_factor', '-=%{p}',
           '原版说明为外交行动费用，赋值-0.25/-0.5用于降低开销；与同机制政治费用系数格式一致。', analogue='political_advisor_cost_factor')
    assign('justify_war_goal_when_in_major_war_time', '-=%{p}',
           '属于战争目标正当化时间的条件比例修正，原版-0.35/-0.5降低等待；与普通正当化时间格式对应。', analogue='justify_war_goal_time')
    assign('enemy_declare_war_tension', '+=%{p}',
           '敌人对我国宣战造成的紧张度比例；原版0.1/-0.25赋值。更高提高敌方行动的世界紧张度代价，收益方向属情境推断。')
    assign('resistance_decay_on_our_occupied_states', '-=%{p}',
           '明确作用于被敌人占领的我国领土；抵抗衰减越慢对原主人越有利，与普通占领地区抵抗衰减方向相反。', analogue='resistance_decay')
    assign('resistance_garrison_penetration_chance', '-=%{p}',
           '驻军遭抵抗组织渗透的概率修正；原版-0.25/-0.1用于降低渗透损失。', analogue='resistance_damage_to_garrison')
    assign('send_volunteer_factor', '+=%{p}',
           '与整数send_volunteer_size独立，原版以0.3/2.0调整可派遣师数比例；按容量比例显示。', analogue='special_forces_cap')
    assign('send_volunteer_divisions_required', '-=%{p}',
           '降低派志愿军所需本国陆军数量门槛，原版-0.5/-0.75配合30师基础门槛；按门槛比例下降显示。',
           extra=[source(GAME/'common/defines/00_defines.lua', 140, 'base_rule', value='VOLUNTEERS_DIVISIONS_REQUIRED = 30')])
    assign('conversion_cost_mil_to_civ_factor', '-=%{p}',
           '与民转军转换费用同一机制、方向相反，目标是军转民费用比例，降低有利。', analogue='conversion_cost_civ_to_mil_factor')
    assign('energy_gain_factor', '+=%{p}',
           '煤炭产出能量效率的国家加成，原版国家精神按0.10设置；按获取效率比例展示。', analogue='fuel_gain_factor')
    assign('license_anti_tank_eq_cost_factor license_artillery_eq_cost_factor license_infantry_eq_cost_factor license_light_tank_eq_cost_factor license_armor_purchase_cost',
           '-=%{p}', '具体装备类生产许可费用：原版-1表示减免费用，使用同一通用生产许可费用百分比。', analogue='license_purchase_cost')
    assign('license_anti_tank_eq_production_speed_factor license_artillery_eq_production_speed_factor license_infantry_eq_production_speed_factor license_light_tank_eq_production_speed_factor',
           '+=%{p}', '许可生产速度按0.25设置，采用通用许可生产速度的比例格式。', analogue='license_production_speed')
    assign('license_anti_tank_eq_tech_difference_speed_factor license_artillery_eq_tech_difference_speed_factor license_infantry_eq_tech_difference_speed_factor license_light_tank_eq_tech_difference_speed_factor license_tech_difference_speed',
           '+=%{p}', '原版说明为科技差造成的许可生产速度调整，+0.5用于改善生产速度；按速度比例显示。', analogue='license_production_speed')
    assign('local_resources_oil_factor', '+=%{p}', '同一注册资源效率模板的石油参数；参照煤炭与全资源效率格式。', analogue='local_resources_factor')
    assign('nuclear_production_factor', '+=%{p}',
           '国家精神与科技使用0.1/0.15/0.5增加核弹生产率；不使用建筑对象中的3/2数值确定国家单位。',
           extra=[source(GAME/'common/ideas/british_raj_goe.txt',438,'country_modifier_assignment',value='0.15'),
                  source(GAME/'common/technologies/special_projects_tech.txt',72,'technology_assignment',value='0.5')])
    assign('production_speed_rocket_site_factor', '+=%{p}', '注册模板说明明确是建筑建设速度系数，与同模板军工厂速度格式相同。', analogue='production_speed_arms_factory_factor')
    assign('repair_speed_arms_factory_factor repair_speed_bunker_factor repair_speed_industrial_complex_factor repair_speed_infrastructure_factor repair_speed_rail_way_factor',
           '+=%{p}', '注册模板明确是建筑维修速度系数；原版0.10/0.25等赋值与通用维修速度格式一致。', analogue='repair_speed_factor')
    assign('special_project_facility_supply_consumption_factor navy_fuel_consumption_factor naval_supply_consumption_factor',
           '-=%{p}', '设施补给、海军燃油和海军补给均是消耗比例；原版负值减少消耗，与通用补给消耗格式一致。', analogue='supply_consumption_factor')
    assign('army_advisor_cost_factor navy_advisor_cost_factor air_advisor_cost_factor', '-=%{p}',
           '三军顾问费用与政治顾问费用同属聘用费用比例；原版以-0.25降低花费。', analogue='political_advisor_cost_factor')
    assign('army_breakthrough_against_major_factor', '+=%{p}', '对主要国家的突破系数，原版0.10/0.15是战斗属性加成；参照同类国家战斗属性比例。', analogue='army_attack_factor')
    assign('army_claim_attack_factor army_claim_defence_factor', '+=%{p}',
           '宣称领土攻防与核心领土攻防同为条件战斗比例，原版0.05赋值。', analogue='army_core_attack_factor')
    assign('army_experience_from_volunteers', '+=%{p}', '来自志愿军的经验增长效率，原版军种精神按0.5/0.05赋值，与经验获取比例对应。', analogue='experience_gain_army_factor')
    assign('army_fuel_capacity_factor', '+=%{p}', '陆军燃油容量比例，原版负数降低容量；更多容量有利。', analogue='max_fuel_factor')
    assign('army_retreat_speed_factor', '+=%{p}', '明确为撤退时部队速度，0.05等正值提升速度。', analogue='army_speed_factor')
    assign('coastal_bunker_effectiveness_factor', '+=%{p}', '海岸要塞效率按0.05/-0.5设置，正值增强防御效能。')
    assign('command_abilities_cost_factor grant_medal_cost_factor', '-=%{p}', '指挥能力/授勋费用用-0.15/-0.25降低消耗，按费用比例显示。')
    assign('dig_in_speed', '+=%{p}', '原版描述是构筑堑壕速度，领袖能力6.0与国家精神0.3表示速度加成；参照同作用的dig_in_speed_factor格式。', analogue='dig_in_speed_factor')
    assign('marines_special_forces_contribution_factor mountaineers_special_forces_contribution_factor paratroopers_special_forces_contribution_factor rangers_special_forces_contribution_factor',
           '-=%{p}', '四种特种部队对上限占用的贡献，原版升级一贯给-0.25以减少上限占用；不能套用“上限增加有利”的反方向。')
    assign('mechanized_defence_factor motorized_defence_factor modifier_army_sub_unit_marine_defence_factor modifier_army_sub_unit_military_police_defence_factor',
           '+=%{p}', '逐兵种防御加成，原版0.05/0.1；与同类步兵防御有色百分比提示对应。', analogue='modifier_army_sub_unit_infantry_defence_factor')
    assign('modifier_army_sub_unit_blackshirt_assault_battalion_max_org_factor modifier_army_sub_unit_category_special_forces_max_org_factor modifier_army_sub_unit_military_police_max_org_factor',
           '+=%{p}', '逐兵种组织度系数，区别基础组织度点数；同机制山地/海军陆战队模板明确显示百分比。', analogue='modifier_army_sub_unit_mountaineers_max_org_factor')
    assign('modifier_army_sub_unit_militia_org_recovery_cap_factor', '+=%{p}', '民兵组织度恢复上限的比例，原版-0.7降低恢复上限；提高上限有利。', analogue='army_org_factor')
    assign('modifier_army_sub_unit_mountaineers_attack_factor modifier_army_sub_unit_paratrooper_attack_factor',
           '+=%{p}', '逐兵种攻击系数，与原版步兵/骑兵攻击带色百分比提示同类。', analogue='modifier_army_sub_unit_infantry_attack_factor')
    assign('modifier_army_sub_unit_mountaineers_speed_factor', '+=%{p}', '山地步兵速度系数，与原版步兵速度提示一致。', analogue='modifier_army_sub_unit_infantry_speed_factor')
    assign('railway_gun_bombardment_factor', '+=%{p}', '列车炮轰击效果以0.25/-0.15调整效能，按效果比例显示。', analogue='shore_bombardment_bonus')
    assign('unit_infantry_design_cost_factor unit_mountaineers_design_cost_factor', '-=%{p}',
           '单位编成花费模板，与已明确的摩托化/机械化单位编成费用模板一致。', analogue='unit_motorized_design_cost_factor')
    assign('unit_medal_effectiveness', '+=%{p}', '单位勋章效能以-0.25/0.05调整，效果增强有利。')
    assign('winter_attrition', '-=%{p}', '原版天气0.4和国家精神-0.1指向损耗率；与冬季比例项独立，但两者均按百分比显示，降低有利。', analogue='winter_attrition_factor')
    assign('air_carrier_night_penalty_reduction_factor', '+=%{p}', '名称明确为夜间惩罚的降低量；正0.15/0.25属于收益，不能套用惩罚本身的负向绿色。', analogue='air_night_penalty')
    assign('carrier_night_traffic carrier_traffic', '+=%{p}', '航母夜间/常规起降能力由学说以0.3/0.15提升；参照舰载出击效率比例，仍为推断。', analogue='sortie_efficiency')
    assign('experience_gain_destroyer_combat_factor experience_gain_destroyer_training_factor', '+=%{p}',
           '注册说明为单位战斗/训练经验增长系数，驱逐舰参数的0.1加成按经验比例显示。', analogue='experience_gain_navy_factor')
    assign('mines_sweeping_by_fleets_factor mines_sweeping_by_air_factor', '+=%{p}',
           '原版说明明确影响海军扫雷效率，正0.1/0.2增加效率；参照同机制布雷/扫雷百分比。', analogue='mines_planting_by_air_factor')
    assign('naval_has_potf_in_combat_attack naval_has_potf_in_combat_defense', '+=%{p}',
           '原版说明为与舰队荣耀共同作战的舰船攻防奖励，0.1/0.05属比例加成。', analogue='navy_capital_ship_attack_factor')
    assign('naval_invasion_penalty', '-=%{p}', '英文说明明确增加此值会降低登陆作战效率，原版-0.15改善登陆表现。', analogue='amphibious_invasion')
    assign('naval_retreat_speed_after_initial_combat', '+=%{p}', '初次接战后的撤退速度由学说以0.2/0.15增加，快速撤退为该效果收益。', analogue='naval_retreat_speed')
    assign('transport_capacity underway_replenishment_convoy_cost', '-=%{p}',
           '分别降低部队运输船空间需求及补给运输船用量；原版-0.1/-0.2是减少需求的比例，非减去0.1艘船。', analogue='supply_consumption_factor')
    assign('underway_replenishment_range', '+=%{p}', '补给航程定义明确0.2表示+20%，科技同样以0.2调整补给距离。',
           extra=[source(GAME/'common/defines/00_defines.lua',1771,'explicit_percentage_comment',value='0.2 means +20%')])
    assign('air_detection', '+=%{p}', '对空探测效果由国家精神按0.1调整，结合探测效能说明推断为百分比；仍待实测。')
    assign('air_volunteer_cap', '+=%{p}', '空军志愿队基准由本国飞机比例及接收国机场比例限定，原版以1调整容量；推断为比例容量而非1架飞机。',
           extra=[source(GAME/'common/defines/00_defines.lua',444,'base_ratio',value='AIR_VOLUNTEER_PLANES_RATIO = 0.2'),
                  source(GAME/'common/defines/00_defines.lua',445,'base_ratio',value='AIR_VOLUNTEER_BASES_CAPACITY_LIMIT = 0.1')])
    assign('naval_strike_agility_factor', '+=%{p}', '对海任务机动性按0.02/0.03调整，沿用空军机动性百分比格式。', analogue='air_agility_factor')
    assign('static_anti_air_damage_factor', '+=%{p}', '科技每级0.1增加防空伤害，属于伤害比例；正值提高防御效果。', analogue='static_anti_air_hit_chance_factor')
    assign('tech_air_damage_factor', '-=%{p}', '名称对应防空对轰炸伤害的降低，原版-0.02用于减少空袭伤害；正负方向需与原版防空提示继续核验。')
    assign('boost_resistance_factor propaganda_mission_factor target_sabotage_factor', '+=%{p}',
           '具体任务效率在情报升级/国家精神中以0.1/0.25增强，参考情报任务效能百分比。', analogue='operation_infiltrate_outcome')
    assign('commando_trait_chance_factor occupied_operative_recruitment_chance', '+=%{p}',
           '特质或敌占区友方国籍特工招募几率，原版0.5/0.25用于提高几率；按概率比例显示。')
    assign('intel_from_operatives_factor', '+=%{p}', '特工与线人情报获取效果以0.1/0.15提高，与国家情报增益比例对应。', analogue='army_intel_factor')
    assign('operation_boost_resistance_outcome operation_coordinated_strike_outcome operation_make_resistance_contacts_outcome operation_steal_tech_outcome',
           '+=%{p}', '注册Operation outcome模板，与显式预定义operation_infiltrate_outcome的百分比/正向收益定义相同。', analogue='operation_infiltrate_outcome')
    assign('operation_steal_tech_risk', '-=%{p}', '行动风险系数，原版升级-0.25降低风险；不能把“更高风险”当收益。', analogue='operation_cost')
    assign('target_sabotage_cost', '-=%{p}', 'Operation cost模板，显式operation_cost定义为percentage且color_type=bad。', analogue='operation_cost')

    # Retain known scale without inventing a universal benefit direction.
    assign('forced_surrender_limit max_surrender_limit_offset', 'Y=%{p}',
           '赋值与投降阈值说明支持比例尺度，但强制阈值/最低阈值的正负收益不能仅套用普通投降界限；暂用黄色待实测。',
           analogue='surrender_limit', confidence='unresolved')
    assign('naval_retreat_chance naval_retreat_chance_after_initial_combat', 'Y=%{p}',
           '原版0.1/0.25和几率说明支持百分比；初次接战后英文说明涉及敌方退出，无法静态确认普遍收益方向，暂用黄色。', confidence='unresolved')
    assign('operative_death_on_capture_chance', 'Y=%{p}',
           '自杀药丸升级提供0.1，与降低泄密风险有关；“我方特工死亡增加”并非普通收益，暂保留黄色概率以免误导。',
           extra=[source(GAME/'common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt',271,'suicide_pills_upgrade',value='0.1')],
           confidence='unresolved')
    assign('cic_construction_boost', '+=%{p}',
           '原版建设提示直接用$MODIFIER_CIC_CONSTRUCTION_BOOST$: $VAL|H0%$显示此基础键，证明其单位为百分比；下一行另列_FACTOR。这里沿注册文档保留1位小数，建设速度提高显示正向绿色属于收益方向推断，不把国家读数注入测试当作格式验证。',
           extra=[source(GAME/'localisation/english/constructions_l_english.yml',122,'exact_named_value_format',
                         localisation_key='CIC_MAX_CONSTRUCTION_BOOST_MODIFIER',raw_format='H0%')])
    assign('army_morale', '+={p}', '只有原版学说0.1基础恢复率赋值，不能套用army_morale_factor百分比；暂显示未缩放原值，单位待核验。', confidence='unresolved')
    assign('consumer_goods_expected_value', 'Y=%1',
           '原版以该精确名称格式化GER_expected_consumer_goods_penalty为百分比；效果受消费品阈值/国策状态条件影响，沿用消费品黄色显示。',
           analogue='consumer_goods_factor',
           extra=[source(GAME/'localisation/english/wuw_ideas_l_english.yml',550,'exact_named_variable_format',
                         localisation_key='GER_CG_penalties_warning',raw_format='0.1%')])


def main():
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data['statistics'], ensure_ascii=False, indent=2))
    print('UNRESOLVED:', ', '.join(r['key'] for r in data['records'] if r['confidence'] == 'unresolved'))


if __name__ == '__main__':
    main()
