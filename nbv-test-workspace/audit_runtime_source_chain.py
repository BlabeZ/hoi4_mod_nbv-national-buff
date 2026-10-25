"""Read-only runtime pipeline and legacy idea coverage audit for NBV 0.1.8."""
import collections
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1] / 'hoi4-national-buff'
GAME = Path('E:/Steam/steamapps/common/Hearts of Iron IV')
sys.path.insert(0, str(ROOT / 'tools'))
sys.dont_write_bytecode = True
from build_mod import SOURCE_TABLES
from build_source_bindings import parse_idea_file, number
from validate_mod import parse_script

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

tables = {f: read_json(ROOT / 'tools/data' / f) for f in SOURCE_TABLES}
manifest = read_json(ROOT / 'tools/data/source-display-manifest.json')
rows = read_json(ROOT / 'tools/data/metric-index.json')['records']
selected = {r['key'] for r in rows}
displayed = {r['key'] for r in read_json(ROOT / 'tools/data/display-layout.json')['records']}
tokens_by_key = collections.defaultdict(set)
all_rows = []
for filename, table in tables.items():
    for key, entries in table['by_modifier'].items():
        for e in entries:
            if float(e['value']) == 0:
                continue
            all_rows.append((key, e['source_category'], e['source_id']))
            tokens_by_key[key].update(re.findall(r'\bhas_idea\s*=\s*(?:token:)?([A-Za-z0-9_.-]+)', e['activation_script']))
generated = [(r['key'], r['source_category'], r['source_id']) for r in manifest['records']]
traits = {}
for path in (GAME / 'common/country_leader').glob('*.txt'):
    tree = parse_script(path.read_text(encoding='utf-8-sig'))
    for outer in tree:
        if outer.key == 'leader_traits':
            for t in outer.value:
                if isinstance(t.value, list):
                    traits[t.key] = t

legacy = []
trait_spirits = []
legacy_categories = {'political_advisor','army_chief','navy_chief','air_chief','high_command','theorist'}
for path in (GAME / 'common/ideas').glob('*.txt'):
    rel = path.relative_to(GAME).as_posix()
    tree, _ = parse_idea_file(path.read_text(encoding='utf-8-sig'), rel, hashlib.sha256(path.read_bytes()).hexdigest())
    for outer in tree:
        if outer.key != 'ideas':
            continue
        for category in outer.value:
            if not isinstance(category.value, list):
                continue
            for idea in category.value:
                if not isinstance(idea.value, list):
                    continue
                trait_ids = [n.value for f in idea.value if f.key == 'traits' and isinstance(f.value, list)
                             for n in f.value if n.key is None]
                if category.key not in legacy_categories and not (category.key == 'country' and trait_ids):
                    continue
                contributions = []
                for t in trait_ids:
                    for f in traits.get(t, type('Empty', (), {'value': []})()).value:
                        value = number(f.value)
                        if f.key in selected and value not in (None, 0):
                            contributions.append({'key': f.key, 'trait': t, 'value': str(value),
                                                  'has_matching_idea_activation': idea.key in tokens_by_key[f.key]})
                for block in idea.value:
                    if block.key == 'modifier' and isinstance(block.value, list):
                        for f in block.value:
                            value = number(f.value)
                            if f.key in selected and value not in (None, 0):
                                contributions.append({'key':f.key, 'trait':None, 'value':str(value),
                                                      'has_matching_idea_activation':idea.key in tokens_by_key[f.key]})
                out = {'source_id':idea.key,'category':category.key,'file':rel,'line':idea.line,
                       'traits':trait_ids,'selected_contributions':contributions}
                (trait_spirits if category.key == 'country' else legacy).append(out)

engine = read_json(ROOT / 'tools/data/engine-validation.json')
loc_lengths = {}
for language in ('simp_chinese','english'):
    path=ROOT/'localisation'/language/('nbv_l_'+language+'.yml')
    loc = {}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        m=re.match(r'\s*([^:]+):0 "(.*)"$',line)
        if m and m[1].startswith(('nbv_source_line_', 'nbv_source_name_', 'nbv_source_group_', 'nbv_sources_')):
            loc[m[1]]=m[2]
    loc_lengths[language]={'maximum_generated_string_characters':max(map(len,loc.values())),
                          'longest_generated_strings': sorted(((k,len(v)) for k,v in loc.items()),key=lambda x:-x[1])[:5]}

result={
    'scope':'Read-only source mapping to generated tooltip pipeline; no claim of all vanilla source coverage.',
    'mod_version':manifest['version'],
    'table_bindings':len(all_rows),'generated_bindings':len(generated),
    'exact_multiset_match':collections.Counter(all_rows)==collections.Counter(generated),
    'unique_generated_identities':len(set(generated))==len(generated),
    'consecutive_indices':[r['index'] for r in manifest['records']]==list(range(1,len(generated)+1)),
    'source_table_hashes_match':all(manifest['input_hashes'][f]==hashlib.sha256((ROOT/'tools/data'/f).read_bytes()).hexdigest() for f in SOURCE_TABLES),
    'all_559_total_expressions':'ROOT.modifier@key (build_mod.py:146), independent of source tables and nation',
    'player_scope':'player_context and dynamic_lists change_scope=no; there is no list of permitted country tags.',
    'timed_ideas':'Same idea ownership predicate as permanent ideas; no duration distinction in source selection. Expiry lifecycle not exhaustively tested.',
    'country_trait_spirits':trait_spirits,
    'legacy_advisor_candidates':legacy,
    'legacy_advisor_summary':{'definition_count':len(legacy),
        'with_selected_contributions':sum(bool(x['selected_contributions']) for x in legacy),
        'missing_matching_activation':sum(any(not c['has_matching_idea_activation'] for c in x['selected_contributions']) for x in legacy),
        'registry_559_contribution_count':sum(len(x['selected_contributions']) for x in legacy),
        'displayed_519_contribution_count':sum(c['key'] in displayed for x in legacy for c in x['selected_contributions']),
        'displayed_519_definition_count':sum(any(c['key'] in displayed for c in x['selected_contributions']) for x in legacy),
        'qualification':'A matching has_idea token does not prove legacy traits match the current character role. Missing candidates are not all reachable; no runtime activity claim.'},
    'generated_localisation_lengths':loc_lengths,
    'native_empty_legacy_databases':{p:(GAME/p).stat().st_size for p in ['common/event_modifiers.txt','common/triggered_modifiers.txt','common/modifiers/01_event_modifiers.txt']},
    'engine_proof':{'dynamic_bindings_tested':engine['dynamic_scan_binding_count'],
        'dynamic_bindings_passed':engine['dynamic_scan_passed_count'],
        'dynamic_excluded_count':len(engine['dynamic_scan_excluded']),
        'dynamic_excluded_reasons':dict(collections.Counter(x['reason'] for x in engine['dynamic_scan_excluded'])),
        'source_checks':len(engine['source_checks']),
        'expanded_source_checks':len(engine['expanded_source_checks']),
        'dynamic_lifecycle_checks':len(engine['dynamic_lifecycle_checks']),
        'dynamic_conditional_checks':len(engine['dynamic_conditional_checks']),
        'ui_interaction_verified':engine['ui_interaction_verified'],
        'cross_tag_tested':engine['cross_tag_tested']},
}
out=Path(__file__).with_name('runtime-source-chain-audit.json')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k in ['table_bindings','generated_bindings','exact_multiset_match','unique_generated_identities','consecutive_indices','source_table_hashes_match','legacy_advisor_summary','engine_proof']},ensure_ascii=True,indent=2))
