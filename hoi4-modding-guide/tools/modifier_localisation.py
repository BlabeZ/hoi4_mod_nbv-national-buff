"""Evidence-preserving HOI4 modifier localisation enrichment (Python 3.9).

No game/mod files are changed. ``enrich_modifiers`` updates records in place and
returns a coverage summary. Unmatched keys stay explicitly unmatched; fuzzy
string matching is deliberately excluded. Sources are absolute paths + lines.
"""
import re
from pathlib import Path
from collections import Counter

_ENTRY = re.compile(r'^\s*([^\s:#]+)\s*:\s*(?:\d+\s*)?"(.*)"\s*(?:#.*)?$')
_REF = re.compile(r'\$([^$|]+)(?:\|[^$]*)?\$')
_FORMAT = re.compile(r'§(?:[A-Za-z0-9!]|\[[^\]]*\])')

# Chinese explanatory labels translated from the template Description in the
# bundled engine documentation. They are editorial, not vanilla localisation.
_TEMPLATE_LABELS = {
    '<Building>_max_level_terrain_limit': ('地形允许的建筑等级上限', 'Maximum building level for terrain'),
    '<CombatTactic>_preferred_weight_factor': ('偏好战术权重系数', 'Preferred tactic weight factor'),
    '<Doctrine>_mastery_gain_factor': ('学说精通增长系数', 'Doctrine mastery gain factor'),
    '<Doctrine>_track_mastery_gain_factor': ('学说分支精通增长系数', 'Doctrine track mastery gain factor'),
    '<Equipment>_design_cost_factor': ('装备设计成本系数', 'Equipment design cost factor'),
    '<IdeaCategory>_category_type_cost_factor': ('理念类别成本系数', 'Idea category cost factor'),
    '<IdeaGroup>_cost_factor': ('理念组成本系数', 'Idea group cost factor'),
    '<Ideology>_acceptance': ('意识形态接受度', 'Ideology acceptance'),
    '<Ideology>_drift': ('意识形态支持度增长', 'Ideology drift'),
    '<Ideology>_drift_from_guarantees': ('保障独立带来的意识形态支持度增长', 'Ideology drift from guarantees'),
    '<ModifierStat>_factor': ('属性系数', 'Stat factor'),
    '<ModifierStatValue>_value_factor': ('属性数值系数', 'Stat value factor'),
    '<Operation>_cost': ('行动成本', 'Operation cost'),
    '<Operation>_outcome': ('行动结果', 'Operation outcome'),
    '<Operation>_risk': ('行动风险', 'Operation risk'),
    '<SpecialProject>_speed_factor': ('特别项目速度系数', 'Special project speed factor'),
    '<Technology>_cost_factor': ('科技成本系数', 'Technology cost factor'),
    '<Trait>_xp_gain_factor': ('特质经验获取系数', 'Trait XP gain factor'),
    'country_resource_<Resource>': ('国家资源数量', 'Country resource'),
    'country_resource_cost_<Resource>': ('国家资源消耗', 'Country resource cost'),
    'experience_gain_<Unit>_combat_factor': ('单位战斗经验获取系数', 'Unit combat XP gain factor'),
    'experience_gain_<Unit>_mission_factor': ('单位任务经验获取系数', 'Unit mission XP gain factor'),
    'experience_gain_<Unit>_training_factor': ('单位训练经验获取系数', 'Unit training XP gain factor'),
    'local_resources_<Resource>_factor': ('当地资源获取系数', 'Local resource factor'),
    'module_<EquipmentModule>_design_cost_factor': ('模块设计成本系数', 'Module design cost factor'),
    'production_cost_<Building>_factor': ('建筑建造成本系数', 'Building construction cost factor'),
    'production_cost_max_<NavalEquipment>': ('海军装备生产成本上限', 'Maximum naval equipment production cost'),
    'production_speed_<Building>_factor': ('国家建筑建造速度系数', 'Country building construction speed factor'),
    'repair_speed_<Building>_factor': ('国家建筑修理速度系数', 'Country building repair speed factor'),
    'state_<Building>_max_level_terrain_limit': ('地区地形允许的建筑等级上限', 'State maximum building level for terrain'),
    'state_production_speed_<Building>_factor': ('地区建筑建造速度系数', 'State building construction speed factor'),
    'state_repair_speed_<Building>_factor': ('地区建筑修理速度系数', 'State building repair speed factor'),
    'state_resource_<Resource>': ('地区资源数量', 'State resource'),
    'state_resource_cost_<Resource>': ('地区资源消耗', 'State resource cost'),
    'state_resources_<Resource>_factor': ('地区资源数量系数', 'State resource factor'),
    'temporary_state_resource_<Resource>': ('临时地区资源数量', 'Temporary state resource'),
    'trait_<Trait>_xp_gain_factor': ('特质经验获取系数', 'Trait XP gain factor'),
    'unit_<Unit>_design_cost_factor': ('单位设计成本系数', 'Unit design cost factor'),
}
_TERRAINS = ('water_shallow_sea', 'water_deep_ocean', 'water_fjords', 'mountain',
             'forest', 'desert', 'jungle', 'plains', 'urban', 'marsh', 'ocean',
             'hills', 'lakes', 'unknown')


def load_localisation(game_root):
    """Return {simp_chinese: {key: entry}, english: {key: entry}}.

    Both base localisation and localisation/replace are scanned. Duplicate
    definitions are recorded; the deterministic choice is not claimed to
    recreate the engine's complete DLC load order.
    """
    root = Path(game_root)
    result = {}
    for lang in ('simp_chinese', 'english'):
        entries = {}
        files = sorted((root / 'localisation').rglob('*_l_' + lang + '.yml'))
        files.sort(key=lambda p: ('replace' in p.parts, str(p).casefold()))
        for path in files:
            for line_no, line in enumerate(path.read_text(encoding='utf-8-sig', errors='replace').splitlines(), 1):
                match = _ENTRY.match(line)
                if not match:
                    continue
                key, value = match.groups()
                entry = {'key': key, 'text': value, 'path': str(path.resolve()), 'line': line_no}
                if key in entries:
                    entry['other_definitions'] = entries[key].get('other_definitions', []) + [
                        {k: entries[key][k] for k in ('text', 'path', 'line')}
                    ]
                entries[key] = entry
        result[lang] = entries
    return result


def _resolve(key, entries, seen=(), depth=0):
    entry = entries.get(key)
    if not entry or key in seen or depth > 12:
        return '$' + key + '$', []
    sources = [{'key': key, 'path': entry['path'], 'line': entry['line']}]
    def replace(match):
        child, child_sources = _resolve(match.group(1), entries, seen + (key,), depth + 1)
        sources.extend(child_sources)
        return child
    text = _REF.sub(replace, entry['text'])
    return text, sources


def _clean(text):
    text = re.sub(r'£[A-Za-z0-9_]+(?:\|\d+)?£?', '', text)
    return _FORMAT.sub('', text).replace('\\n', '\n').replace('\\"', '"').strip()


def _candidates(key):
    yield 'MODIFIER_' + key.upper(), 'exact_modifier_prefix'
    yield 'MODIFIERS_' + key.upper(), 'exact_modifiers_prefix'
    yield 'modifier_' + key, 'exact_lowercase_prefix'
    yield key, 'exact_key'
    yield key.upper(), 'exact_uppercase_key'


def _find_name(key, entries, game_root=None):
    for candidate, method in _candidates(key):
        if candidate in entries:
            return candidate, method, []
    # Vanilla scripted tooltip explicitly connects a script key with a label.
    for tt in (key + '_tt', key.upper() + '_TT', 'modifier_' + key + '_tt'):
        if tt not in entries:
            continue
        references = [r for r in _REF.findall(entries[tt]['text'])
                      if r in entries and r not in ('RIGHT', 'LEFT', 'VALUE')]
        references = list(dict.fromkeys(references))
        if len(references) == 1:
            return references[0], 'explicit_tooltip_reference', [
                {'key': tt, 'path': entries[tt]['path'], 'line': entries[tt]['line']}
            ]
    verified_aliases = {
        'refit_ic_cost': ('MODIFIER_INDUSTRIAL_REFIT_IC_COST_FACTOR', [
            ('common/dynamic_modifiers/0_dynamic_modifiers.txt', 880),
            ('history/countries/SOV - Soviet union.txt', 552),
            ('common/national_focus/soviet.txt', 3349),
            ('localisation/english/nsb_focus_l_english.yml', 1466)]),
        'attack_bonus_against': ('MODIFIER_ATTACK_BONUS_AGAINST_A_COUNTRY', [
            ('common/ideas/japan.txt', 4762),
            ('common/on_actions/14_sea_on_actions.txt', 1609),
            ('localisation/simp_chinese/SEA_focus_l_simp_chinese.yml', 498)]),
    }
    if game_root and key in verified_aliases:
        loc_key, links = verified_aliases[key]
        if loc_key in entries:
            return loc_key, 'reviewed_script_tooltip_chain', [
                {'key': key, 'path': str(Path(game_root)/p), 'line': line}
                for p, line in links]
    return None, 'unmatched', []


def _parameter_name(parameter, entries, template):
    for key in (parameter, parameter.upper(), 'MODIFIER_' + parameter.upper(),
                'STAT_ARMY_' + parameter.upper(), 'STAT_NAVY_' + parameter.upper(),
                'STAT_AIR_' + parameter.upper()):
        if key in entries:
            raw, sources = _resolve(key, entries)
            return _clean(raw), sources, True
    if '<Building>' in template and 'terrain_limit' in template:
        for terrain in _TERRAINS:
            if parameter.endswith('_' + terrain):
                building = parameter[:-len(terrain)-1]
                a, src_a, ok_a = _parameter_name(building, entries, '')
                b, src_b, ok_b = _parameter_name(terrain, entries, '')
                return a + ' / ' + b, src_a + src_b, ok_a and ok_b
    return parameter, [], False


def enrich_modifiers(records, game_root, localisation=None):
    """Mutate dict records with key/name fields, return summary, no file writes.

    Added fields: name_zh/name_en, description_zh/description_en,
    localisation_key, localisation_method, localisation_sources,
    localisation_description_sources, localisation_unresolved_tokens,
    localisation_has_duplicate_definitions. Unmatched text is an empty string.
    The alias list in summary only contains links evidenced by vanilla tooltips.
    """
    loc = localisation if localisation is not None else load_localisation(game_root)
    counts = Counter()
    aliases = []
    unmatched = []
    for record in records:
        key = record.get('key') or record.get('modifier') or record.get('name')
        if not key:
            raise ValueError('Modifier record lacks key/modifier/name')
        sources, description_sources, unresolved = [], [], []
        selected = None
        selected_method = 'unmatched'
        duplicates = False
        for lang, suffix in (('simp_chinese', 'zh'), ('english', 'en')):
            entries = loc[lang]
            name_key, method, evidence = _find_name(key, entries, game_root)
            record['name_' + suffix] = ''
            record['description_' + suffix] = ''
            record['localisation_key_' + suffix] = name_key or ''
            if not name_key:
                continue
            if selected is None:
                selected, selected_method = name_key, method
            raw, visited = _resolve(name_key, entries)
            record['name_' + suffix] = _clean(raw)
            sources.extend(evidence + visited)
            unresolved.extend(_REF.findall(raw))
            duplicates = duplicates or bool(entries[name_key].get('other_definitions'))
            description_candidates = [name_key + '_DESC', name_key + '_desc',
                                      key + '_desc', key + '_DESC']
            for desc_key in dict.fromkeys(description_candidates):
                if desc_key in entries:
                    raw, visited = _resolve(desc_key, entries)
                    record['description_' + suffix] = _clean(raw)
                    description_sources.extend(visited)
                    unresolved.extend(_REF.findall(raw))
                    break
        record['localisation_key'] = selected or ''
        record['localisation_method'] = selected_method
        record['localisation_sources'] = sources
        record['localisation_description_sources'] = description_sources
        record['localisation_unresolved_tokens'] = list(dict.fromkeys(unresolved))
        record['localisation_has_duplicate_definitions'] = duplicates
        record['localisation_editorial_name'] = False
        template = record.get('template')
        parameter = record.get('parameter')
        if not selected and template in _TEMPLATE_LABELS and isinstance(parameter, str):
            label_zh, label_en = _TEMPLATE_LABELS[template]
            source = {'key': template,
                      'path': str((Path(game_root) / 'documentation/modifiers_documentation.md').resolve()),
                      'line': record.get('doc_line')}
            for lang, suffix, label in (('simp_chinese', 'zh', label_zh), ('english', 'en', label_en)):
                parameter_name, visited, complete = _parameter_name(parameter, loc[lang], template)
                record['name_' + suffix] = label + '：' + parameter_name
                record['parameter_localisation_complete_' + suffix] = complete
                record['localisation_sources'].extend(visited)
            record['localisation_sources'].append(source)
            record['localisation_method'] = 'template_derived'
            record['localisation_editorial_name'] = True
            selected_method = 'template_derived'
            # Preserve descriptions as absent: the engine's original template
            # description already exists in record.doc_description.
            selected = 'derived:' + template
        counts[selected_method] += 1
        if record['name_zh']:
            counts['has_chinese_name'] += 1
        if record['description_zh']:
            counts['has_chinese_description'] += 1
        if not selected:
            unmatched.append(key)
        elif selected_method in ('explicit_tooltip_reference', 'reviewed_script_tooltip_chain'):
            aliases.append({'key': key, 'localisation_key': selected})
    return {'record_count': len(records), 'counts': dict(counts),
            'explicit_aliases': aliases, 'unmatched_keys': unmatched,
            'method_note': '直接名称使用精确键、标准前缀、原版 <key>_tt 或 modifier_<key>_tt 的单一本地化引用；另有人工审查的脚本到tooltip调用链，标为reviewed_script_tooltip_chain并保留源位置。不做模糊匹配。template_derived 是按引擎模板翻译组合的编辑名称，不是原版完整本地化；parameter_localisation_complete 可识别残留英文参数。未解析动态占位符原样保留，游戏图标标记从纯文本名称中去除。'}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-root', required=True)
    parser.add_argument('--audit-output', required=True)
    args = parser.parse_args()
    docs = Path(args.game_root) / 'documentation/modifiers_documentation.md'
    keys = []
    for line in docs.read_text(encoding='utf-8-sig').splitlines():
        if line.startswith('## '):
            key = re.sub(r'<span[^>]*></span>', '', line[3:]).strip()
            if re.fullmatch(r'[a-z0-9_]+', key):
                keys.append(key)
    records = [{'key': k} for k in dict.fromkeys(keys)]
    summary = enrich_modifiers(records, args.game_root)
    output = {'summary': summary, 'records': records}
    Path(args.audit_output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
