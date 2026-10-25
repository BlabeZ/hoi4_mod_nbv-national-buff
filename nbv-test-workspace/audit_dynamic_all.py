import sys, json, re
from pathlib import Path
from collections import Counter

BASE = Path('D:/projects/hoi4_mod/1')
MOD = BASE / 'hoi4-national-buff'
GAME = Path('E:/Steam/steamapps/common/Hearts of Iron IV')
sys.path.insert(0, str(MOD / 'tools'))
from validate_mod import parse_script
from build_dynamic_source_bindings import fields, walk_paths, addition_scope
from build_source_bindings import localizations

def load(name):
    return json.loads((MOD / 'tools/data' / name).read_text(encoding='utf-8'))

literal, variable = load('dynamic-source-bindings.json'), load('dynamic-spirit-source-bindings.json')
registry = {r['key'] for r in load('metric-index.json')['records']}
display = {r['key'] for r in load('display-layout.json')['records']}
runtime_manifest = load('source-display-manifest.json')['records']
runtime = {(r['source_id'],r['key']) for r in runtime_manifest if r['source_type'] in ('dynamic_modifier','dynamic_modifier_variable')}
accepted = {(r['source_id'], k): r for d in (literal,variable) for k, rows in d['by_modifier'].items() for r in rows if r['source_type'] in ('dynamic_modifier','dynamic_modifier_variable')}
exclusions = {}
for row in literal['excluded'] + variable['excluded']:
    if row['source_type'] == 'dynamic_modifier' and row['reason'] != 'dynamic_variable_cached_contribution_not_exposed':
        exclusions.setdefault(row['source_id'], []).append(row)

sites = {}
for path in sorted(p for folder in ('common','events','history') for p in (GAME / folder).rglob('*.txt')):
    text = path.read_text(encoding='utf-8-sig',errors='replace')
    if 'add_dynamic_modifier' not in text:
        continue
    relative = path.relative_to(GAME).as_posix()
    for node, ancestors in walk_paths(parse_script(text, relative)):
        if node.key != 'add_dynamic_modifier' or not isinstance(node.value,list):
            continue
        modifier = fields(node.value,'modifier')
        if len(modifier) != 1:
            continue
        scope = fields(node.value,'scope')
        sites.setdefault(modifier[0].value, []).append(dict(file=relative,line=node.line, lexical_scope=addition_scope(relative,ancestors),ancestors=ancestors,scope=scope[0].value if scope else None))

names=localizations(GAME)
definitions, all_bindings = [], []
files=list((GAME/'common/dynamic_modifiers').rglob('*.txt'))
for path in sorted(files):
    relative=path.relative_to(GAME).as_posix()
    for node in parse_script(path.read_text(encoding='utf-8-sig'),relative):
        if not isinstance(node.value,list):
            continue
        name = fields(node.value,'name')
        name_key=name[0].value if name else node.key
        bindings=[]
        for entry in node.value:
            if entry.key not in registry:
                continue
            ident=(node.key,entry.key)
            binding=dict(source_id=node.key,key=entry.key,value=entry.value,file=relative,line=entry.line,displayed_key=entry.key in display,accepted=ident in accepted,runtime=ident in runtime)
            if ident not in accepted:
                matching=[r for r in exclusions.get(node.key,[]) if r.get('modifier',entry.key)==entry.key]
                binding['reasons']=list(dict.fromkeys(r['reason'] for r in matching)) or ['UNEXPLAINED']
            bindings.append(binding)
            all_bindings.append(binding)
        definitions.append(dict(source_id=node.key,file=relative,line=node.line,name_loc_key=name_key,name_zh=names['simp_chinese'].get(name_key,[]),bindings=bindings,addition_sites=sites.get(node.key,[]),reasons=list(dict.fromkeys(r['reason'] for r in exclusions.get(node.key,[])))))

# This independent audit expands the production scanner's deliberately coarse
# lexical scopes. It does not change any generated/runtime binding.
trees = {}
for definition in definitions:
    missing=[b for b in definition['bindings'] if b['displayed_key'] and not b['accepted']]
    if not missing:
        continue
    for site in definition['addition_sites']:
        site['audit_scope']=site['lexical_scope']
        if 'effect_tooltip' in site['ancestors']:
            site['audit_scope']='tooltip_only_not_executed'
        elif site['lexical_scope']=='unknown' and site['file'].startswith('common/decisions/'):
            relative=site['file']
            if relative not in trees:
                trees[relative]=parse_script((GAME/relative).read_text(encoding='utf-8-sig'))
            decision=[d for c in trees[relative] if isinstance(c.value,list) for d in c.value if d.key==site['ancestors'][1] and isinstance(d.value,list)]
            state_target=fields(decision[0].value,'state_target') if len(decision)==1 else []
            if len(state_target)==1 and state_target[0].value!='no' and 'FROM' in site['ancestors']:
                site['audit_scope']='state'
                site['audit_evidence']=dict(file=relative,line=state_target[0].line,field='state_target',value=state_target[0].value)
        elif site['lexical_scope']=='unknown' and 'var:target_state' in site['ancestors'] and site['file'].startswith('common/raids/'):
            site['audit_scope']='state'
            site['audit_evidence']=dict(file=site['file'],line=site['line'],field='var:target_state')
        elif definition['source_id']=='FIN_confederation_of_finno_russian_republics_dm' and site['lexical_scope']=='unknown':
            site['audit_scope']='state'
            site['audit_evidence']=dict(file='common/on_actions/09_aat_on_actions.txt',line=1834,field='on_state_control_changed.FROM.FROM; guarded by is_core_of = SOV')
        elif definition['source_id']=='NOR_defend_state_dmod' and site['lexical_scope']=='unknown':
            site['audit_scope']='state'
            site['audit_evidence']=dict(file='common/decisions/NOR.txt',line=1261,field='FROM state target invokes NOR_deploy_prep_dem; branch invokes NOR_deploy_prep_dem_1')
        elif definition['source_id']=='SOV_soviet_military_offensive' and site['lexical_scope']=='unknown':
            site['audit_scope']='state'
            site['audit_evidence']=dict(file='common/decisions/SOV.txt',line=12363,field='state IDs 195,208,244 populate SOV_military_offensive_states; also FROM/every_neighbor_state at 12197')
    actual=[s for s in definition['addition_sites'] if s['audit_scope']!='tooltip_only_not_executed']
    if 'missing_or_ambiguous_chinese_name' in definition['reasons']:
        definition['audit_disposition']='excluded_no_chinese_name'
    elif actual and all(s['audit_scope']=='state' for s in actual):
        definition['audit_disposition']='excluded_state_object'
    elif definition['source_id']=='SWI_dormant_citizen_militia' and all(s['audit_scope']=='country' for s in actual):
        definition['audit_disposition']='country_source_gap_same_country_scope_overexcluded'
    else:
        definition['audit_disposition']='REQUIRES_FURTHER_REVIEW'
    for b in missing:
        b['audit_disposition']=definition['audit_disposition']

def counts(rows):
    return dict(bindings=len(rows),sources=len({r['source_id'] for r in rows}),accepted_bindings=sum(r['accepted'] for r in rows),runtime_bindings=sum(r['runtime'] for r in rows),missing_bindings=sum(not r['accepted'] for r in rows),missing_sources=len({r['source_id'] for r in rows if not r['accepted']}),missing_by_reason=dict(Counter(reason for r in rows if not r['accepted'] for reason in r['reasons'])))

result=dict(file_count=len(files),definition_count=len(definitions),registry=counts(all_bindings),displayed=counts([r for r in all_bindings if r['displayed_key']]),accepted_missing_runtime=[r for r in all_bindings if r['accepted'] and not r['runtime']],definitions=definitions,unbound_displayed=[r for r in all_bindings if r['displayed_key'] and not r['accepted']])
result['displayed_missing_dispositions']={reason:dict(bindings=sum(r['audit_disposition']==reason for r in result['unbound_displayed']),sources=len({r['source_id'] for r in result['unbound_displayed'] if r['audit_disposition']==reason})) for reason in sorted({r['audit_disposition'] for r in result['unbound_displayed']})}
generated_source_text='\n'.join(p.read_text(encoding='utf-8-sig') for p in (MOD/'common/scripted_localisation').glob('*.txt'))
functions=set(re.findall(r'name\s*=\s*(NBVSource[0-9]+)\b',generated_source_text))
result['runtime_records_missing_generated_function']=[dict(source_id=r['source_id'],key=r['key'],index=r['index']) for r in runtime_manifest if r['source_type'] in ('dynamic_modifier','dynamic_modifier_variable') and 'NBVSource'+str(r['index']) not in functions]
out=BASE/'nbv-test-workspace/dynamic-complete-audit.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('definitions','unbound_displayed')},ensure_ascii=True,indent=2))
print('UNBOUND DISPLAYED SOURCES')
for definition in definitions:
    if any(b['displayed_key'] and not b['accepted'] for b in definition['bindings']):
        print(definition['source_id'], definition['reasons'],len([b for b in definition['bindings'] if b['displayed_key'] and not b['accepted']]), dict(Counter(s['lexical_scope'] for s in definition['addition_sites'])))
