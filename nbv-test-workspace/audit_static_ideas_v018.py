"""Independent inventory of all shipped ideas and current displayed source coverage.

Audit only: no production write. Uses its own small lexer/tree scanner, not
NBV's production parser/generator. Missing final braces are retained as evidence.
"""
from pathlib import Path
import re, json, hashlib
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'hoi4-national-buff'
GAME = Path('E:/Steam/steamapps/common/Hearts of Iron IV')
DATA = MOD/'tools/data'

TOKEN = re.compile(r'#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}]|[<>!=?]+|[^\s{}<>!=?#"]+')
def parse(text):
    toks=[(m.group(),text.count('\n',0,m.start())+1) for m in TOKEN.finditer(text) if not m.group().startswith('#')]
    pos=0; unclosed=[]
    def block(path=(), nested=False):
        nonlocal pos
        out=[]
        while pos<len(toks):
            key,line=toks[pos];pos+=1
            if key=='}':
                if not nested: raise ValueError('Unexpected close '+str(line))
                return out
            if key=='{':
                out.append({'key':None,'value':block(path+('<anonymous>',),True),'line':line});continue
            if pos<len(toks) and toks[pos][0] in ('=','>','<','>=','<=','!=','?=','=='):
                op=toks[pos][0];pos+=1
                value,vl=toks[pos];pos+=1
                if value=='{': value=block(path+(key,),True)
                else: value=value.strip('"')
                out.append({'key':key,'value':value,'line':line,'operator':op})
            else: out.append({'key':None,'value':key.strip('"'),'line':line})
        if nested: unclosed.append(path)
        return out
    return block(),unclosed

def numeric(value):
    try:
        return Decimal(value) if isinstance(value,str) else None
    except InvalidOperation: return None

def fields(node,key): return [x for x in node['value'] if x['key']==key]
def scalar(node,key,default=None):
    x=fields(node,key)
    return x[0]['value'] if len(x)==1 and isinstance(x[0]['value'],str) else default
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

registry={r['key']:r for r in read(DATA/'metric-index.json')['records']}
shown={r['key'] for r in read(DATA/'display-layout.json')['records']}
bindings=read(DATA/'source-bindings.json')
sources={}
allrows=[]
for p in DATA.glob('*source-bindings.json'):
    d=read(p)
    for key,rows in d.get('by_modifier',{}).items():
        for r in rows: allrows.append((p.name,key,r))
for key,rows in bindings['by_modifier'].items():
    for r in rows: sources[(r['source_id'],key)]=r
rejects=defaultdict(list)
for r in bindings['excluded']: rejects[r['source_id']].append(r)
safe={'country','hidden_ideas','economy','mobilization_laws','trade_laws','army_spirit','academy_spirit','division_command_spirit','navy_spirit','naval_academy_spirit','naval_command_spirit','air_force_spirit','air_force_command_spirit'}

loc=defaultdict(set)
for p in (GAME/'localisation/simp_chinese').rglob('*.yml'):
    for m in re.finditer(r'^\s*([\w.\-]+):\d*\s+"((?:\\.|[^"\\])*)"',p.read_text(encoding='utf-8-sig',errors='replace'),re.M):
        loc[m[1]].add(m[2])
traits={}
for p in (GAME/'common/country_leader').glob('*.txt'):
    tree,unclosed=parse(p.read_text(encoding='utf-8-sig'))
    for root in tree:
        if root['key']=='leader_traits':
            for t in root['value']:
                if isinstance(t['value'],list): traits[t['key']]=t

files=[];ideas=[];candidate=[];trait_candidate=[];nondirect=[];fail=[];nonliteral=[]
for p in sorted((GAME/'common/ideas').rglob('*.txt')):
    text=p.read_text(encoding='utf-8-sig');rel=p.relative_to(GAME).as_posix()
    try: tree,unclosed=parse(text)
    except Exception as exc: fail.append({'file':rel,'error':str(exc)});continue
    files.append({'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unclosed_paths':unclosed})
    for root in tree:
        if root['key']!='ideas':continue
        for cat in root['value']:
            if not isinstance(cat['value'],list): continue
            for idea in cat['value']:
                if not isinstance(idea['value'],list):continue
                base={'idea':idea['key'],'file':rel,'line':idea['line'],'category':cat['key'],'safe_category':cat['key'] in safe,'name_key':scalar(idea,'name',idea['key'])}
                base['names_zh']=sorted(loc.get(base['name_key'],set()))
                base['rejections']=rejects[idea['key']]
                direct=[];traitrows=[]
                for m in fields(idea,'modifier'):
                    if not isinstance(m['value'],list):continue
                    for kv in m['value']:
                        n=numeric(kv['value'])
                        if kv['key'] in shown and n is None:
                            nonliteral.append({**base,'modifier':kv['key'],'value':kv['value'],'modifier_line':kv['line']})
                        if kv['key'] not in registry or n is None or n==0: continue
                        row={**base,'modifier':kv['key'],'modifier_name':registry[kv['key']]['name'],'value_literal':kv['value'],'modifier_line':kv['line'],'displayed':kv['key'] in shown,'covered':(idea['key'],kv['key']) in sources}
                        candidate.append(row);direct.append(row)
                for field in fields(idea,'traits'):
                    if not isinstance(field['value'],list):continue
                    for tok in field['value']:
                        t=traits.get(tok['value'])
                        if not t:continue
                        for kv in t['value']:
                            n=numeric(kv['value'])
                            if kv['key'] not in registry or n is None or n==0:continue
                            exact=[];other=[]
                            for tab,key,r in allrows:
                                if key != kv['key']:continue
                                if r.get('idea_token')==idea['key']:exact.append({'table':tab,'id':r['id']})
                                if r.get('trait_id',r.get('source_id'))==t['key']:other.append({'table':tab,'id':r['id']})
                            row={**base,'trait':t['key'],'modifier':kv['key'],'modifier_name':registry[kv['key']]['name'],'value_literal':kv['value'],'displayed':kv['key'] in shown,'exact_idea_token_candidates':exact,'other_trait_role_candidate_count':len(other),'other_trait_role_examples':other[:3]}
                            trait_candidate.append(row);traitrows.append(row)
                for kind in ('targeted_modifier','equipment_bonus','research_bonus','on_add','on_remove'):
                    for fld in fields(idea,kind):
                        if not isinstance(fld['value'],list):continue
                        vals=[{'key':x['key'],'value':x['value'],'line':x['line'],'displayed':x['key'] in shown} for x in fld['value'] if x['key'] in registry]
                        nondirect.append({**base,'field':kind,'field_line':fld['line'],'selected_keys':vals})
                ideas.append({**base,'direct_nonzero_registry_count':len(direct),'direct_nonzero_displayed_count':sum(r['displayed'] for r in direct),'traits_nonzero_displayed_count':sum(r['displayed'] for r in traitrows),'fields':[x['key'] for x in idea['value']]})

displayed=[r for r in candidate if r['displayed']]
missing=[r for r in displayed if not r['covered']]
safe_miss=[r for r in missing if r['safe_category']]
def aggregate(rows, key):return dict(sorted(Counter(str(r[key]) for r in rows).items()))
out={'scope':'Vanilla 1.19.3 ideas database, current 519 UI keys; independent parser inventory; no runtime activation claim','statistics':{'files':len(files),'ideas':len(ideas),'parse_failures':len(fail),'all_direct_nonzero_registry_candidates':len(candidate),'all_direct_nonzero_displayed_candidates':len(displayed),'safe_category_displayed_candidates':sum(r['safe_category'] for r in displayed),'safe_category_displayed_covered':sum(r['safe_category'] and r['covered'] for r in displayed),'safe_category_displayed_missing':len(safe_miss),'safe_category_displayed_missing_ideas':len({r['idea'] for r in safe_miss}),'other_category_displayed_direct_missing':sum(not r['safe_category'] for r in missing),'trait_displayed_candidates':sum(r['displayed'] for r in trait_candidate),'safe_missing_by_file':aggregate(safe_miss,'file'),'safe_missing_by_reason':dict(Counter(r['rejections'][0]['reason'] if r['rejections'] else 'none' for r in safe_miss))},'files':files,'parse_failures':fail,'ideas':ideas,'missing_direct_displayed':missing,'all_direct_candidates':candidate,'trait_candidates':trait_candidate,'non_direct_blocks':nondirect}
dest=ROOT/'nbv-test-workspace/static-idea-coverage-audit-v018.json'
out['nonliteral_displayed_direct_values']=nonliteral
out['statistics']['nonliteral_displayed_direct_values']=len(nonliteral)
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out['statistics'],ensure_ascii=True,indent=2))
print(str(dest))
