# -*- coding: utf-8 -*-
"""Second-pass display selection for national modifiers; only writes local reports."""
import collections
import hashlib
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent/'vanilla-modifier-catalog'
OUT = BASE/'global-buff-review'
DATE = '2026-10-25'
CATS = ['政治', '工业', '陆军', '海军', '空军', '情报']
GROUPS = {'A':'国策／国家精神中出现，纳入必展词条库',
          'B':'未检出上述来源，仍需展示', 'C':'本轮不展示'}
REASONS = {'scope_excluded':'超出本轮作用域或明确排除',
           'unnamed':'无已确认显示名称，按用户要求不展示',
           'user_excluded':'用户指定移出',
           'low_value':'AI行为、非数值规则或展示价值较低',
           'unobserved':'仅注册／未发现定义，暂无展示需求',
           'pending':'国家来源或展示价值仍待确认'}


def read_json(p):
    return json.loads(p.read_text(encoding='utf-8'))


def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def md(s):
    return str(s or '').replace('|','\\|').replace('\n',' ').replace('\r','')


def link(label, p, line=None):
    return '['+md(label)+'](<'+Path(p).as_posix()+(':'+str(line) if line else '')+'>)'


def source_examples(evidence, policy):
    result = []
    for name in ['country_spirit_examples','focus_country_global_candidate_examples',
                 'focus_direct_examples','variable_examples']:
        for ex in evidence.get(name, [])[:2]:
            for field in ['source','modifier_source','reference_source','mutation_source']:
                src = ex.get(field)
                if src and src.get('file'):
                    label=ex.get('object_id') or ex.get('focus_id') or name
                    if name=='variable_examples':label='变量依赖辅助证据：'+label
                    result.append({'file':src['file'], 'line':src['line'],
                        'label':label,
                        'kind':name})
    for ex in policy.get('evidence',[])[:3]:
        src = ex.get('source', ex)
        p = src.get('file') or src.get('path')
        if p and src.get('line'):
            result.append({'file':p,'line':src['line'],
                'label':ex.get('note') or ex.get('relative_file') or '全国来源审查',
                'kind':'reviewed_scope_evidence'})
    unique = {}
    for x in result:
        unique.setdefault((x['file'],x['line']),x)
    return list(unique.values())[:8]


def exclusion(r, rule):
    k,t = r['key'],r['template'] or ''
    if rule.get('scope_reason') in ('unnamed','user_excluded'):
        return rule['scope_reason'],rule['reason']
    if k.startswith('ai_') or 'Boolean' in r['doc_display'] or k.endswith('_acceptance'):
        return 'low_value', rule.get('reason') or 'AI行为、外交接受倾向或布尔规则不作为BUFF数值展示；规则开关可另做状态徽章。'
    if rule.get('scope_reason') in ('low_display_value','low_player_numeric_value'):
        return 'low_value',rule['reason']
    if rule.get('decision') == 'exclude':
        return 'scope_excluded', rule['reason']
    if k.startswith(('state_','temporary_state_')) or t.startswith(('state_','temporary_state_')):
        return 'scope_excluded','州／地方对象的专属修正，不进入国家全局统计。'
    if not r['definition_count'] and not r['reference_count']:
        return 'unobserved',rule.get('reason') or '引擎已注册，但本机规则扫描未见定义赋值；本轮不为预留或未使用的模板变体设置展示行。'
    return 'pending',rule.get('reason') or '尚未满足国家全局来源与展示价值两项审查条件；本轮不显示，不等于该键无效。'


def build():
    original = read_json(BASE/'data/catalog.json')
    policy = read_json(HERE/'global_buff_review_policy.json')
    overrides = read_json(HERE/'global_buff_user_overrides.json')
    designers = read_json(HERE/'user_revision_designer_candidates.json')
    baseline = read_json(OUT/'data/before-user-revision-2026-10-25.json')
    summary = read_json(OUT/'data/focus-spirit-summary.json')
    scope = read_json(HERE/'global_buff_scope_notes.json')
    scope['scope_contract'] = overrides['scope_contract']
    supplement_path=OUT/'data/manual-source-supplements.json'
    supplements=read_json(supplement_path)['records'] if supplement_path.exists() else {}
    index = summary['records']
    if isinstance(index, list):
        index = {r['key']:r for r in index}
    rules = {k:dict(v) for k,v in policy['rules'].items()}
    requested = {}
    for item in overrides['include_sets']:
        for key in item['keys']:
            assert key not in requested, key
            requested[key] = item['request']
            rules[key] = {**rules.get(key,{}), **{k:v for k,v in item.items() if k not in ('request','keys')},
                'decision':'include','scope_reason':'national_component_user_requested',
                'review_group':'user_revision_2026_10_25'}
    for item in designers['records']:
        if item['key'] in requested and item['decision']=='include':
            rules[item['key']]['evidence'] = item.get('evidence',[])
    for key,rule in overrides['boundary_rules'].items():
        rules[key] = {**rules.get(key,{}),**rule}
    for key in overrides['exclude_keys']:
        rules[key] = {**rules.get(key,{}),'decision':'exclude',
            'reason':'用户在本轮明确指定不加入BUFF统计，覆盖此前B档推荐。',
            'scope_reason':'user_excluded'}
    records = []
    for old in original['records']:
        key=old['key']; rule=rules.get(key,{})
        name=re.sub(r'\$(RIGHT|LEFT|FACTOR|VALUE)\$', '', old['name_zh']).rstrip('：: ')
        named=bool(name.strip() or old['name_en'].strip())
        if overrides['exclude_unnamed'] and not named:
            rule={**rule,'decision':'exclude','scope_reason':'unnamed',
                'reason':'当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。'}
        ev=index.get(key,{})
        manual=supplements.get(key,{})
        count=lambda name:int(ev.get(name,0))
        present=bool(count('country_spirit_direct_count') or
            count('focus_country_global_candidate_count') or count('focus_direct_country_count') or
            manual.get('strong_focus_or_country_dynamic_spirit'))
        decision=rule.get('decision',policy['default_decision'])
        if 'Boolean' in old['doc_display'] or key.startswith('ai_'):
            decision='exclude'
        if decision=='include':
            group='A' if present else 'B'
            why=rule['reason']; subtype='selected'
        else:
            group='C'; subtype,why=exclusion(old,rule)
        name=overrides['display_labels'].get(key,name) if named else name
        notes=manual.get('caveats',[])[:]
        if key in requested and not present:
            notes.append('按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。')
        if key in requested and not old['definition_count']:
            notes.append('本次原版扫描未检出定义赋值；不能将仅注册解释为当前国家必有非零值，也不能将修正分量当作最终上限。')
        evidence=manual.get('evidence',[])[:5]+source_examples(ev,rule)
        focus_ids=set(ev.get('focus_country_global_candidate_focus_ids',[]))
        additional_focus_ids=set(manual.get('focus_ids',[]))-focus_ids
        focus_unique_count=count('focus_country_global_candidate_unique_focus_count')+len(additional_focus_ids)
        focus_ids.update(additional_focus_ids)
        records.append({
            'key':key,'name_zh':name,'original_name_zh':old['name_zh'],'name_en':old['name_en'],
            'category':rule.get('category',old['category']),
            'group':group,'group_label':GROUPS[group],'exclusion_class':subtype,
            'decision_reason':why,'conditions':rule.get('conditions',[]),
            'source_notes':notes,'has_confirmed_display_name':named,
            'user_requested':key in requested,'user_request_label':requested.get(key,''),
            'manual_source_reason':manual.get('reason',''),
            'scope_reason':rule.get('scope_reason','not_selected'),
            'review_group':rule.get('review_group','not_in_manual_whitelist'),
            'old_priority':old['priority'],'effect_summary':rule.get('effect_summary',old['effect_summary']),
            'country_spirit_direct_count':count('country_spirit_direct_count'),
            'focus_country_global_candidate_count':count('focus_country_global_candidate_count'),
            'focus_unique_count':focus_unique_count,
            'focus_ids':sorted(focus_ids),
            'focus_direct_country_count':count('focus_direct_country_count'),
            'focus_unknown_scope_count':count('focus_unknown_scope_count'),
            'focus_state_or_object_count':count('focus_state_or_object_count'),
            'focus_all_paths_count':count('focus_all_paths_count'),
            'variable_strong_count':count('variable_strong_count'),
            'variable_weak_count':count('variable_weak_count'),
            'hidden_idea_direct_count':count('hidden_idea_direct_count'),
            'dynamic_definition_count':count('dynamic_definition_count'),
            'country_applied_dynamic_definition_count':count('country_applied_dynamic_definition_count'),
            'excluded_nested_count':count('excluded_nested_count'),
            'debug_auxiliary_count':count('debug_auxiliary_count'),
            'has_strong_focus_or_spirit_evidence':present,
            'country_spirit_ids':ev.get('country_spirit_ids',[]),
            'definition_count_all_contexts':old['definition_count'],
            'file_count_all_contexts':old['file_count'],
            'buff_mods':old['buff_mods'],
            'template':old['template'],'parameter':old['parameter'],
            'doc_source':old['doc_source'],'doc_line':old['doc_line'],
            'read_expression':('[?ROOT.modifier@'+key+']') if group in 'AB' else None,
            'runtime_read_validated':False,
            'evidence':evidence[:10],
            'manual_source_supplement':manual,
            'source_summary':ev,
        })
    groups=collections.Counter(r['group'] for r in records)
    stats={'total':len(records),'groups':dict(groups),
        'selected':groups['A']+groups['B'],
        'categories':{c:{g:sum(r['category']==c and r['group']==g for r in records) for g in GROUPS} for c in CATS},
        'exclusion_classes':dict(collections.Counter(r['exclusion_class'] for r in records if r['group']=='C')),
        'strong_source_keys_total':sum(r['has_strong_focus_or_spirit_evidence'] for r in records),
        'old_p0_p1_removed':sum(r['old_priority'] in ('P0','P1') and r['group']=='C' for r in records),
        'old_buff_keys_removed':sum(bool(r['buff_mods']) and r['group']=='C' for r in records),
        'new_selected_without_buff_mods':sum(not r['buff_mods'] and r['group'] in 'AB' for r in records)}
    before={r['key']:r for r in baseline['selected_records']}
    after={r['key']:r for r in records if r['group'] in 'AB'}
    revision={'previous_statistics':baseline['statistics'],
        'added_keys':sorted(after.keys()-before.keys()),
        'removed_keys':sorted(before.keys()-after.keys()),
        'requested_already_selected_keys':sorted(set(requested)&before.keys()&after.keys()),
        'unnamed_total':sum(not r['has_confirmed_display_name'] for r in records),
        'unnamed_removed_from_selection':sum(r['key'] in before and not r['has_confirmed_display_name'] for r in records),
        'explicit_removals':overrides['exclude_keys'],
        'request_mapping':overrides['include_sets'],
        'boundary_rules':overrides['boundary_rules']}
    out={'date':DATE,'game_version':original['game_version'],
        'original_catalog_date':original['analysed_date'],
        'trace_statistics':summary.get('counts',{}),
        'scope_contract':scope['scope_contract'],'statistics':stats,
        'evidence_coverage':summary.get('coverage_limits',summary.get('method',{})),
        'selection_policy':{'precedence':'无名排除及本轮用户规则 > 旧人工策略；全局对象约束持续生效。',
            'base_policy_file':str(HERE/'global_buff_review_policy.json'),
            'user_override_file':str(HERE/'global_buff_user_overrides.json'),
            'base_policy_is_historical':True,'effective_scope':overrides['scope_contract']},
        'user_revision':revision,
        'records':records}
    dump(OUT/'data/display-catalog.json',out)
    return out, summary, scope


def table(records, excluded=False):
    lines=['| 修正键／名称 | 国家精神定义 | 国策关联 | 分类理由及条件 |',
           '|---|---:|---:|---|']
    for r in records:
        conditions='；条件：'+'、'.join(r['conditions']) if r['conditions'] else ''
        notes='；注意：'+'；'.join(r['source_notes']) if r['source_notes'] else ''
        evidence=r['evidence'][:1]
        proof='；'+link('来源',evidence[0]['file'],evidence[0]['line']) if evidence else ''
        lines.append('| '+link(r['key'],r['doc_source'],r['doc_line'])+'<br>'+md(r['name_zh'] or r['name_en'] or '名称待核验')+
            ' | '+str(r['country_spirit_direct_count'])+' | '+str(r['focus_unique_count'])+
            ' | '+md(r['decision_reason']+conditions+notes)+proof+' |')
    return '\n'.join(lines)+'\n'


def render_documents(data, summary, scope):
    records=data['records']; stats=data['statistics']
    ordered=sorted(records,key=lambda r:(CATS.index(r['category']),r['old_priority'],
        -r['country_spirit_direct_count'],-r['focus_country_global_candidate_count'],r['key']))
    for group,filename in [('A','A-focus-spirit-required.md'),('B','B-other-global-required.md')]:
        text='# '+GROUPS[group]+'\n\n'
        text+='复核日期：'+DATE+'。共 **'+str(stats['groups'].get(group,0))+' 项**。\n\n'
        if group=='A':
            text+='“必展”指必须纳入可显示的词条库；当前国家为零时可默认收起。国策或国家精神中出现只是来源证据，只有通过国家全局范围与展示价值审查的项才进入此表。\n\n'
        else:
            text+='“未检出”限定于本次静态追踪范围，不表示原版绝不可能经事件、参数化脚本或复杂变量链使用。该组包含科技、学说、情报升级等其他国家来源，以及用户明确指定但尚待国家读取验证的注册项；后者逐项标注，不宣称已验证全局读数。\n\n'
        text+='国家精神定义次数按非调试 ideas.country 直属 modifier 计；国策关联数按可信国家应用路径涉及的独立国策计，包含引用民族精神及动态修正。人工补充的国家动态精神与跨初始化变量链在完整数据中另列；变量同名弱链不混入强证据。\n\n'
        for cat in CATS:
            rows=[r for r in ordered if r['group']==group and r['category']==cat]
            if rows:text+='## '+cat+'（'+str(len(rows))+' 项）\n\n'+table(rows)+'\n'
        (OUT/filename).write_text(text,encoding='utf-8')
    excluded='# 本轮不展示的修正\n\n'
    excluded+='共 **'+str(stats['groups']['C'])+' 项**。本文件是排除审计，不是BUFF展示页面。无名称项保留技术键用于追溯，但不会进入展示白名单。以下区分无名称、用户指定移出、范围排除、低展示价值、仅注册未见使用、证据待确认；不把“本轮不显示”写成“引擎无效”。\n\n'
    for kind,label in REASONS.items():
        rows=[r for r in ordered if r['group']=='C' and r['exclusion_class']==kind]
        excluded+='## '+label+'（'+str(len(rows))+' 项）\n\n'+table(rows,True)+'\n'
    (OUT/'C-not-displayed.md').write_text(excluded,encoding='utf-8')
    changed=[r for r in ordered if r['old_priority'] in ('P0','P1') and r['group']=='C']
    changes='# 从上一轮重要候选中移出的项目\n\n'
    changes+='共 '+str(len(changed))+' 项。完整注册表中的重要候选经过国家全局范围、已确认名称和本轮用户增删规则筛选，以下项目不进入当前展示白名单。本次用户修订前后的差异见 [本轮调整清单](user-revision-2026-10-25.md)。\n\n'+table(changed,True)
    (OUT/'changes-from-first-pass.md').write_text(changes,encoding='utf-8')
    scope_text='# 国家全局范围与统计方法\n\n'
    scope_text+='本轮按用户确认保留国家持有的地区条件加成，只排除州／地方对象自身分量。2026-10-25的新要求覆盖此前天气、设计商和外交接纳度的整类排除：指定的天气相关国家分量、四种主义接纳度、六项设计商费用/经费纳入；无已确认名称项一律不展示。\n\n'
    scope_text+='领袖、法案／法律、顾问授予国家的修正与国策、民族精神等国家来源同样统计；只排除领袖本人技能和仅作用于其麾下单位的局部分量。运行页面只读取当前玩家国家，切换tag时重新绑定并刷新；不按来源类别扣掉国家合计。\n\n'
    scope_text+='当前有效规则：[用户覆盖规则](../../tools/global_buff_user_overrides.json)。[旧人工策略](../../tools/global_buff_review_policy.json)和[旧范围取证](../../tools/global_buff_scope_notes.json)保留为历史依据，冲突处以本轮覆盖规则为准。[本轮调整清单](user-revision-2026-10-25.md)逐项列出选择与同名边界。\n\n'
    for item in scope['principles']:
        scope_text+='## '+item['id']+'\n\n'+item['decision']+'\n\n'
        for src in item.get('evidence',[]):
            scope_text+='- '+link(src['note'],src['path'],src['line'])+'\n'
        scope_text+='\n'
    m=scope['manufacturers_and_mio']
    scope_text+='## 设计商与MIO的实现边界\n\n'
    scope_text+='五类设计商/工业企业聘用费用、国家持有的军工机构经费获取纳入；具体MIO、装备、模块、单位、生产线对象属性继续排除。军工机构研究加成按本次“不包括科技修正”继续排除，普通国家科研修正不受此限定影响。七项当前目录无已确认名称的MIO管理键仍不展示；原版存在候选本地化标签不等于本目录已确认对应映射，本轮不以猜测补名绕过隐藏规则。\n\n'
    scope_text+='国家ROOT.modifier@只读取该国家存储的合计，没有按来源扣除的现成参数。如果工业企业的普通国家modifier已经汇入同一国家总值，不能据“排除对象局部值”声称已从总量扣除该来源。纳入设计商国家管理修正也不等于把具体机构的局部值加入国家总值。\n\n'
    for src in m['evidence']:
        scope_text+='- '+link(src['note'],src['path'],src['line'])+'\n'
    scope_text+='\n## 来源追踪的覆盖边界\n\n'
    for s in summary.get('coverage_limits',[]):scope_text+='- '+s+'\n'
    scope_text+='\n## 计数与推荐规则\n\n'
    scope_text+='国家精神直属定义、独立国策关联、动态变量弱链、全语料频次分别保留，不能相加作为“生效次数”。仅修改变量不等于直接授予同名修正；去掉民族精神也不记为新增BUFF。A/B/C覆盖原4484个键，不删除原全量目录。\n\n'
    scope_text+='国家来源与展示资格分开判断：排除对象局部载荷、无名称及用户指定项，再应用明确纳入需求和人工白名单。仅注册但无原版赋值的明确指定项可作为待验证候选；已知只在地方使用的同名项不以地方数值充当国家值。当前规则由旧人工策略与优先级更高的用户覆盖文件共同生成。\n\n'
    scope_text+='“国家持有”不等于“无条件生效”；核心领土、特定兵种、海军任务、占领治理等保留条件说明。当前只提出读取候选，所有数值仍须逐项校验单位、基值、叠加和刷新。不能从国家总量推导具体师、舰、飞机、州或装备的最终属性。\n'
    scope_text+='\n## 人工补齐的国家动态精神来源\n\n'
    for r in records:
        extra=r['manual_source_supplement']
        if extra:
            scope_text+='### '+r['key']+'\n\n'+extra['reason']+'\n\n'
            for note in extra.get('caveats',[]):scope_text+='- '+note+'\n'
            for src in extra.get('evidence',[]):scope_text+='- '+link(src['label'],src['file'],src['line'])+'\n'
            scope_text+='\n'
    (OUT/'methodology.md').write_text(scope_text,encoding='utf-8')
    cat_table='| 分类 | A 国策／精神必展 | B 其他来源必展 | C 本轮不展示 |\n|---|---:|---:|---:|\n'
    for cat,v in stats['categories'].items():cat_table+='| '+cat+' | '+str(v['A'])+' | '+str(v['B'])+' | '+str(v['C'])+' |\n'
    report=f'''# 国家全局 BUFF 二次筛选

复核日期：{DATE}（Asia/Singapore）。原版：**{data['game_version']}**。第一轮完整目录采集于 {data['original_catalog_date']}，保留原始 4,484 项注册表，本轮另建展示白名单。

本轮选入 **{stats['selected']} 项**：A 类 {stats['groups'].get('A',0)} 项、B 类 {stats['groups'].get('B',0)} 项；其余 {stats['groups']['C']} 项分理由归入 C 类。词条入库不要求全部同时铺在首页，建议按六类分页、默认收起零值并可切换显示全部。

- [A：国策／国家精神中出现且必展](A-focus-spirit-required.md)
- [B：未检出上述来源但仍需展示](B-other-global-required.md)
- [C：本轮无需展示及逐项理由](C-not-displayed.md)
- [离线筛选页面](catalog.html)：可筛选 A/B/C、六类、旧 BUFF 模组覆盖，查看来源。
- [范围、方法与证据](methodology.md)
- [2026-10-25 用户指定增删及同名边界](user-revision-2026-10-25.md)
- [上一轮候选移出清单](changes-from-first-pass.md)
- [完整分类数据](data/display-catalog.json) · [国策／精神摘要](data/focus-spirit-summary.json) · [完整追踪链](data/focus-spirit-evidence.json)
- [人工来源补充](data/manual-source-supplements.json)：补齐国家历史初始化、动态精神和国策修改变量的调用链。
- [一致性核验](verification.json)
- [离线页面功能核验](html-verification.json)

{cat_table}

**保留**：国家的政治、建设、生产、科研、资源、陆海空、情报修正；领袖、法案／法律、顾问提供的国家修正也计入。保留国家持有的核心／非核心等地区条件加成和全国适用的兵种、任务、治理分量。指定的天气/气候、四种主义外交接纳度、五类设计商费用和军工机构经费获取按国家分量纳入。运行页面只读取当前玩家国家，切换tag后刷新。

**排除**：全部无已确认名称的词条、用户指定移出的4项、州／地方对象分量、具体单位／领袖／装备属性、指定目标国的双边数值、MIO／生产线自身属性，以及设计商相关科技修正。AI权重与布尔规则不进入BUFF数值列表。用户明确指定但未发现赋值的注册项入库并标记待读取验证；同名地方基础值不能混入国家统计。

原版国策通常通过民族精神、动态修正与 scripted_effect 间接授予加成。因此本轮追踪了对象引用链，而非只在国策文件中搜索修正键。国家精神只计非调试 ideas.country 的直属 modifier；法律、军种精神、顾问、制造商、hidden_ideas 等另列。动态修正必须有可信国家应用路径，定义文件夹本身不能证明其作用域。

两个 BUFF 模组曾采用的规范键中有 **{stats['old_buff_keys_removed']} 项**不再进入本轮白名单；原 P0/P1 候选中移出 **{stats['old_p0_p1_removed']} 项**。新增选入而两模组均未采用的有 **{stats['new_selected_without_buff_mods']} 项**。详见逐项表，不能把旧模组选取当作范围正确性的保证。

“未检出”不是绝对从未出现：事件后续、复杂作用域和参数化脚本等有静态追踪边界；变量同名链不作为强来源证据。本轮没有启动游戏验证读取与刷新。

设计商国家管理修正与具体机构对象属性分别处理。若某工业企业的普通国家 modifier 已进入同一国家总值，ROOT.modifier@没有按来源扣除的现成参数。不能把排除局部对象值解释为已从国家合计扣除某来源。

生成器：[build_global_buff_review.py](../../tools/build_global_buff_review.py)；当前选择以[用户覆盖规则](../../tools/global_buff_user_overrides.json)为最高优先级。来源改变时先运行同目录 focus_spirit_modifier_evidence.py，本次只改选择规则则直接运行生成器；游戏和模组源文件只读。
'''
    (OUT/'README.md').write_text(report,encoding='utf-8')


def render_revision(data):
    revision=data['user_revision']; stats=data['statistics']
    by_key={r['key']:r for r in data['records']}
    previous={r['key']:r['group'] for r in read_json(OUT/'data/before-user-revision-2026-10-25.json')['selected_records']}
    text='# 用户指定的 BUFF 展示名单修订\n\n'
    text+=f"日期：{DATE}。修订前 {revision['previous_statistics']['selected']} 项，新增 {len(revision['added_keys'])} 项，移出 {len(revision['removed_keys'])} 项，修订后 **{stats['selected']} 项**（A {stats['groups']['A']}、B {stats['groups']['B']}）。完整目录仍为 {stats['total']} 项，未入选的 {stats['groups']['C']} 项仅保留审计记录。\n\n"
    text+=f"移出项包括 **{revision['unnamed_removed_from_selection']} 个原已选无名词条和4个指定B档词条**。全目录共 {revision['unnamed_total']} 个未确认名称的键，均为C；不会以技术键或占位名称进入BUFF界面。此次指定词条中 {len(revision['requested_already_selected_keys'])} 项原已选入，继续保留，不重复计数。\n\n"
    text+='## 按用户清单对应到修正键\n\n| 用户要求 | 采用的键与本轮结果 |\n|---|---|\n'
    for item in revision['request_mapping']:
        values=[]
        for key in item['keys']:
            row=by_key[key]; old=previous.get(key,'C')
            values.append('`'+key+'`：'+('保留 '+old if old==row['group'] else old+' → '+row['group']))
        text+='| '+md(item['request'])+' | '+'<br>'.join(values)+' |\n'
    text+='\n## 同名、对象与科技边界\n\n'
    text+='- 四种主义指原版顶层的共产主义、民主主义、法西斯主义、中立主义；子意识形态不另外生成修正键。\n'
    text+='- 冬季损耗基础项与比例项分列；空军、海军恶劣天气惩罚分列；训练时间基础项与比例项分列。它们不是重复键，不能仅凭同名相加。\n'
    text+='- `forced_surrender_limit` 标注“强制阈值”，与常规 `surrender_limit` 分列。\n'
    text+='- 军用工厂、民用工厂、船坞、基础设施四种建设速度使用原有国家键；四个同名 `state_` 键继续排除。\n'
    text+='- 设计商增加五类国家聘用费用及军工机构经费获取，共6项。无名称MIO管理项、具体机构/装备/模块/生产线属性不加入。\n'
    for key,rule in revision['boundary_rules'].items():
        text+='- `'+key+'`：'+rule['reason']+'\n'
    text+='\n仅发现地方来源并不证明引擎拒绝国家使用；本轮依据已确认存储对象选择同名的国家版本。空降容量/计划上限、己方战场宽度等用户明确指定而无赋值记录的键，则保留注册候选标记，不能声称其国家读数已验证。\n\n'
    text+='## 新增进入展示库\n\n'+table([by_key[k] for k in revision['added_keys']])+'\n'
    text+='## 从原展示库移出\n\n'+table([by_key[k] for k in revision['removed_keys']],True)+'\n'
    text+='## 本轮明确要求且已在展示库的项目\n\n'+table([by_key[k] for k in revision['requested_already_selected_keys']])+'\n'
    text+='完整结果：[A档](A-focus-spirit-required.md) · [B档](B-other-global-required.md) · [C档审计](C-not-displayed.md) · [离线检索](catalog.html)。规则：[用户覆盖文件](../../tools/global_buff_user_overrides.json)；设计商取证：[候选审查](../../tools/user_revision_designer_candidates.json)；修订前名单：[快照](data/before-user-revision-2026-10-25.json)。\n'
    (OUT/'user-revision-2026-10-25.md').write_text(text,encoding='utf-8')


def render_html(data):
    fields=['key','name_zh','name_en','category','group','decision_reason','conditions',
        'country_spirit_direct_count','focus_country_global_candidate_count','focus_unique_count',
        'variable_weak_count','definition_count_all_contexts','buff_mods',
        'exclusion_class','effect_summary','evidence','old_priority','source_notes','manual_source_reason']
    payload=[{k:r[k] for k in fields} for r in data['records']]
    jsdata=json.dumps(payload,ensure_ascii=False).replace('</','<\\/')
    page=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>国家全局BUFF二次筛选</title>
<style>body{margin:0;background:#f3f6f9;color:#23344a;font:15px/1.65 "Microsoft YaHei",system-ui,sans-serif}main{max-width:1450px;margin:auto;padding:28px}h1{font-size:28px;margin:0}a{color:#17628f}.note{padding:12px 16px;background:#e6eff6;border-left:4px solid #4e7d9b}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}input,select,button{font:inherit;padding:8px 12px;border:1px solid #b8c5d2;border-radius:6px;background:white;color:inherit}input{min-width:300px;flex:1}button{cursor:pointer}button:disabled{opacity:.4}.tablewrap{overflow:auto;background:white;border:1px solid #d9e2eb;border-radius:8px}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:11px;border-bottom:1px solid #e0e6ed;vertical-align:top}th{background:#e5edf5;position:sticky;top:0}code{font:13px/1.6 Consolas,monospace;overflow-wrap:anywhere}summary{cursor:pointer}.details{font-size:13px;background:#f4f7fa;padding:12px;margin-top:10px;max-width:800px}.pager{display:flex;justify-content:space-between;gap:16px;margin:16px 0}.tag{padding:2px 8px;border-radius:4px;background:#e4eaf2}.A{background:#d9eee3}.B{background:#dceaf9}.C{background:#eee9e3}.small{font-size:13px;color:#5c6c7f}@media(max-width:800px){main{padding:14px}input{min-width:240px}.optional{display:none}th,td{padding:8px}}</style>
<main><p class="small">本机原版 · __VERSION__ · __DATE__</p><h1>国家全局 BUFF 二次筛选</h1><p>全部 4,484 个注册键 → A：__A__ 项 · B：__B__ 项 · C：__C__ 项</p><p class="note">默认显示有名称的 A+B 白名单。保留指定天气、主义接纳度及设计商国家管理项；排除州／地方对象和具体单位属性。C 与全部视图仅用于排除审计。</p><p><a href="README.md">统计说明</a> · <a href="A-focus-spirit-required.md">A 必展表</a> · <a href="B-other-global-required.md">B 补充表</a> · <a href="C-not-displayed.md">C 排除表</a> · <a href="methodology.md">方法与边界</a> · <a href="user-revision-2026-10-25.md">本轮指定调整</a></p>
<div class="filters"><input id="q" placeholder="搜索名称、修正键或判断理由"><select id="group"><option value="">全部 A/B/C</option><option value="A">A 国策／精神中出现且必展</option><option value="B">B 未检出但仍需展示</option><option value="C">C 本轮不展示</option><option value="AB" selected>仅展示白名单 A+B</option></select><select id="cat"><option value="">全部六类</option><option>政治</option><option>工业</option><option>陆军</option><option>海军</option><option>空军</option><option>情报</option></select><select id="coverage"><option value="">所有旧模组覆盖</option><option value="yes">旧BUFF模组采用</option><option value="no">两模组均未采用</option></select><select id="sort"><option value="source">按国家精神频次</option><option value="focus">按国策关联数</option><option value="key">按修正键</option></select></div>
<div class="pager"><span id="count"></span><div><button id="prev">上一页</button> <span id="page"></span> <button id="next">下一页</button></div></div><div class="tablewrap"><table><thead><tr><th>组别</th><th>分类</th><th>修正与证据</th><th>国家精神定义</th><th>国策关联</th><th class="optional">旧模组</th></tr></thead><tbody id="body"></tbody></table></div><p class="small">国策关联按独立国策计，变量同名弱链单列。未检出不等于绝对从未使用。所有读取均尚未逐项运行验证。</p></main>
<script id="catalog-data" type="application/json">__DATA__</script><script>
const DATA=JSON.parse(document.getElementById('catalog-data').textContent),$=id=>document.getElementById(id);let page=0,filtered=[];const size=60;
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function detail(r){return '<div class="details"><p><b>选择理由：</b>'+esc(r.decision_reason)+'</p>'+r.source_notes.map(n=>'<p class="note">'+esc(n)+'</p>').join('')+(r.manual_source_reason?'<p><b>人工来源复核：</b>'+esc(r.manual_source_reason)+'</p>':'')+'<p><b>条件：</b>'+esc(r.conditions.join('；')||'未额外标注；具体效果以源码为准')+'</p><p><b>作用：</b>'+esc(r.effect_summary)+'</p><p><b>全语料定义次数：</b>'+r.definition_count_all_contexts+'；<b>变量弱链：</b>'+r.variable_weak_count+'（不计强来源）</p>'+r.evidence.map(s=>'<p><a href="'+esc('file:///'+s.file.replaceAll('\\','/'))+'">'+esc(s.label)+'</a> 第 '+s.line+' 行<br><code>'+esc(s.file)+'</code></p>').join('')+'</div>'}
function render(){const terms=$('q').value.toLowerCase().trim().split(/\s+/).filter(Boolean),g=$('group').value;filtered=DATA.filter(r=>(!g||(g==='AB'?r.group!=='C':r.group===g))&&(!$('cat').value||r.category===$('cat').value)&&(!$('coverage').value||($('coverage').value==='yes'?r.buff_mods.length>0:!r.buff_mods.length))&&terms.every(t=>[r.key,r.name_zh,r.name_en,r.decision_reason].join(' ').toLowerCase().includes(t)));const s=$('sort').value;filtered.sort((a,b)=>s==='key'?a.key.localeCompare(b.key):(s==='focus'?b.focus_unique_count-a.focus_unique_count:b.country_spirit_direct_count-a.country_spirit_direct_count)||a.key.localeCompare(b.key));const pages=Math.max(1,Math.ceil(filtered.length/size));page=Math.max(0,Math.min(page,pages-1));$('count').textContent='匹配 '+filtered.length+' / '+DATA.length+' 项';$('page').textContent=(page+1)+' / '+pages;$('prev').disabled=page===0;$('next').disabled=page===pages-1;$('body').innerHTML=filtered.slice(page*size,(page+1)*size).map(r=>'<tr><td><span class="tag '+r.group+'">'+r.group+'</span></td><td>'+esc(r.category)+'</td><td><details><summary><b>'+esc(r.name_zh||r.name_en||'名称待核验')+'</b><br><code>'+esc(r.key)+'</code></summary>'+detail(r)+'</details></td><td>'+r.country_spirit_direct_count+'</td><td>'+r.focus_unique_count+'</td><td class="optional">'+(r.buff_mods.map(m=>m==='ui'?'UI':'决议').join('、')||'未选')+'</td></tr>').join('')||'<tr><td colspan="6">没有匹配词条</td></tr>'}
['q','group','cat','coverage','sort'].forEach(id=>$(id).addEventListener(id==='q'?'input':'change',()=>{page=0;render()}));$('prev').onclick=()=>{page--;render()};$('next').onclick=()=>{page++;render()};render();
</script></html>'''
    for a,b in {'__VERSION__':html.escape(data['game_version']),'__DATE__':DATE,'__DATA__':jsdata,
                '__A__':str(data['statistics']['groups'].get('A',0)),
                '__B__':str(data['statistics']['groups'].get('B',0)),
                '__C__':str(data['statistics']['groups'].get('C',0))}.items():page=page.replace(a,b)
    (OUT/'catalog.html').write_text(page,encoding='utf-8')


def verify(data):
    rows=data['records']; keys={r['key'] for r in rows}
    by_key={r['key']:r for r in rows}
    overrides=read_json(HERE/'global_buff_user_overrides.json')
    requested={key for item in overrides['include_sets'] for key in item['keys']}
    revision=data['user_revision']
    checks={
        'all_original_keys_partitioned':len(rows)==len(keys)==4484,
        'only_three_groups':{r['group'] for r in rows}=={'A','B','C'},
        'A_has_strong_source':all(r['has_strong_focus_or_spirit_evidence'] for r in rows if r['group']=='A'),
        'B_has_no_strong_source':all(not r['has_strong_focus_or_spirit_evidence'] for r in rows if r['group']=='B'),
        'all_requested_keys_registered':requested<=keys,
        'requested_global_keys_selected':all(by_key[k]['group'] in 'AB' for k in requested),
        'four_explicit_removals_excluded':all(by_key[k]['group']=='C' for k in overrides['exclude_keys']),
        'unnamed_not_selected':all(r['has_confirmed_display_name'] for r in rows if r['group'] in 'AB'),
        'unnamed_all_classified':all(r['exclusion_class']=='unnamed' and r['read_expression'] is None for r in rows if not r['has_confirmed_display_name']),
        'local_and_designer_research_boundaries':all(by_key[k]['group']=='C' for k in overrides['boundary_rules']),
        'selection_delta_balances':revision['previous_statistics']['selected']+len(revision['added_keys'])-len(revision['removed_keys'])==data['statistics']['selected'],
        'boolean_or_ai_not_in_numeric_list':all(r['group']=='C' for r in rows if r['key'].startswith('ai_') or r['key'] in ('can_guarantee_other_ideologies','crypto_department_enabled','nuclear_production','thermonuclear_production')),
        'state_templates_excluded':all(r['group']=='C' for r in rows if r['key'].startswith(('state_','temporary_state_'))),
        'core_attack_defence_retained':all(next(r for r in rows if r['key']==k)['group'] in 'AB' for k in ['army_core_attack_factor','army_core_defence_factor','army_non_core_attack_factor','army_non_core_defence_factor']),
        'no_runtime_success_claim':not any(r['runtime_read_validated'] for r in rows),
        'all_have_reasons':all(r['decision_reason'] for r in rows),
        'evidence_files_exist':all(Path(s['file']).is_file() for r in rows for s in r['evidence']),
    }
    manifest=[]
    for p in [BASE/'data/catalog.json',HERE/'global_buff_review_policy.json',HERE/'global_buff_scope_notes.json',HERE/'global_buff_user_overrides.json',HERE/'user_revision_designer_candidates.json',OUT/'data/before-user-revision-2026-10-25.json',OUT/'data/focus-spirit-summary.json',OUT/'data/manual-source-supplements.json']:
        manifest.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    result={'date':DATE,'checks':checks,'all_passed':all(checks.values()),'statistics':data['statistics'],'input_manifest':manifest}
    dump(OUT/'verification.json',result)
    assert result['all_passed'],result
    print(json.dumps(result['statistics'],ensure_ascii=False,indent=2))


if __name__=='__main__':
    result,summary,scope=build()
    render_documents(result,summary,scope)
    render_revision(result)
    render_html(result)
    verify(result)
