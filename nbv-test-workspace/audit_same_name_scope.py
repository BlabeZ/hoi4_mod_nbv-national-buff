"""Read-only semantic-identity audit against the delivered v0.1.9 baseline."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'dist/national-buff-ui-0.1.9.zip'
CATALOG = ROOT / 'hoi4-modding-guide/vanilla-modifier-catalog/data/catalog.json'
REVIEW = ROOT / 'hoi4-modding-guide/vanilla-modifier-catalog/global-buff-review/data/display-catalog.json'
OUT = ROOT / 'nbv-test-workspace/same-name-scope-audit.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with zipfile.ZipFile(BASELINE) as archive:
        reg = json.loads(archive.read('hoi4-national-buff/tools/data/metric-index.json').decode('utf-8-sig'))['records']
        layout = json.loads(archive.read('hoi4-national-buff/tools/data/display-layout.json').decode('utf-8-sig'))
        markdown = archive.read('hoi4-national-buff/tools/data/display-order.md').decode('utf-8-sig')
    catalog = json.loads(CATALOG.read_text(encoding='utf-8-sig'))['records']
    review = json.loads(REVIEW.read_text(encoding='utf-8-sig'))['records']
    raw_by_key = {r['key']: r for r in catalog}
    review_by_key = {r['key']: r for r in review}
    registered = {r['key'] for r in reg}
    selected = {r['key'] for r in layout['records']}
    groups = defaultdict(list)
    for row in reg:
        groups[row['name']].append(row)
    name_groups = []
    for name, rows in groups.items():
        if len(rows) < 2:
            continue
        name_groups.append({
            'name': name,
            'records': [{k: r[k] for k in ('id', 'key', 'name', 'category')} | {
                'displayed_v019': r['key'] in selected,
                'registered_read_validated': r['runtime_read_validated'],
                'effect_summary': r['effect_summary'],
                'registry_display': raw_by_key[r['key']]['doc_display'],
                'authorised_to_add_this_turn': r['key'] == 'global_building_slots',
            } for r in rows],
        })
    collapsed = [r for r in layout['excluded_records'] if len(groups[r['name']]) > 1]
    absent_names = [r for r in layout['excluded_records'] if len(groups[r['name']]) == 1]
    for r in absent_names:
        assert '- ' + r['name'] + '\n' not in markdown

    overrides = {
        'autonomy_gain_ll_to_overlord': {
            'finding': 'country_candidate_outside_original_whitelist',
            'reason': 'Eight direct country-leader trait definitions exist. Leader contributions are now explicitly in scope; this is a separately omitted whitelist candidate, not a Markdown deduplication loss.',
            'runtime_read_validated': False,
            'current_sources_checked': [
                {'file': 'E:/Steam/steamapps/common/Hearts of Iron IV/common/country_leader/goe_traits.txt', 'line': 188, 'trait': 'sikh_activist', 'value': 0.35},
                {'file': 'E:/Steam/steamapps/common/Hearts of Iron IV/common/country_leader/goe_traits.txt', 'line': 383, 'trait': 'staunch_imperialist', 'value': -0.3},
            ],
        },
        'fuel_gain_from_states': {
            'finding': 'country_candidate_outside_original_whitelist',
            'reason': 'Synthetic refinery country_modifiers specifies a base contribution of 2.0 per hour, distinct from the displayed percentage factor. It is a country contribution, not a state modifier; its live read and final presentation unit need a separate engine check.',
            'runtime_read_validated': False,
            'current_sources_checked': [
                {'file': 'E:/Steam/steamapps/common/Hearts of Iron IV/common/buildings/00_buildings.txt', 'line': 273, 'path': 'buildings.synthetic_refinery.country_modifiers.modifiers', 'value': 2.0, 'comment': 'per hour'},
            ],
        },
        'enemy_operative_detection_chance_factor_over_occupied_tag': {
            'finding': 'local_scope_exclusion_confirmed',
            'reason': 'Italy mafia and Czechoslovak collaborator definitions are applied to states; no verified country-wide source was found.',
            'current_sources_checked': [
                {'file': 'E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/italy.txt', 'line': 20602, 'scope': 'every_controlled_state'},
                {'file': 'E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/czechoslovakia_mu.txt', 'line': 22575, 'scope': 'state'},
            ],
        },
        'enemy_operative_detection_chance_over_occupied_tag': {
            'finding': 'local_scope_exclusion_confirmed',
            'reason': 'The observed secret_police_oversight occupation-law contribution is inside state_modifier.',
            'current_sources_checked': [
                {'file': 'E:/Steam/steamapps/common/Hearts of Iron IV/common/occupation_laws/occupation_laws.txt', 'line': 243, 'scope': 'state_modifier'},
            ],
        },
        'research_sharing_per_country_bonus': {
            'finding': 'mechanism_parameter_pending',
            'reason': 'Observed assignments specify a technology_sharing_group base coefficient. It has not been established that these are accumulated into the country modifier read.',
            'runtime_read_validated': False,
        },
    }
    outside = []
    for r in review:
        if r['key'] in registered or r['name_zh'] not in groups:
            continue
        raw = raw_by_key[r['key']]
        outside.append({
            'key': r['key'], 'name': r['name_zh'], 'category': r['category'],
            'matching_registered_keys': [q['key'] for q in groups[r['name_zh']]],
            'matching_currently_displayed_keys': [q['key'] for q in groups[r['name_zh']] if q['key'] in selected],
            'original_group': r['group'], 'original_exclusion_class': r['exclusion_class'],
            'original_reason': r['decision_reason'],
            'definition_count': r['definition_count_all_contexts'],
            'raw_examples': raw['examples'],
            'current_audit': overrides.get(r['key'], {'finding': 'preserve_original_exclusion', 'reason': r['decision_reason']}),
            'added_to_production': False,
        })
    summary = {
        'baseline_version': '0.1.9', 'registry_count': len(reg), 'display_count': len(selected),
        'same_name_groups': len(name_groups),
        'same_name_group_keys': sum(len(g['records']) for g in name_groups),
        'same_name_omitted_keys': len(collapsed),
        'same_name_omitted_keys_after_authorised_building_slot_addition': len(collapsed) - 1,
        'absent_markdown_unique_name_keys': len(absent_names),
        'excluded_total': len(layout['excluded_records']),
        'full_catalog_count': len(catalog),
        'outside_registry_exact_name_matches': len(outside),
        'outside_registry_matches_current_display_name': sum(bool(r['matching_currently_displayed_keys']) for r in outside),
        'outside_registry_original_exclusion_counts': dict(Counter(r['original_exclusion_class'] for r in outside)),
        'outside_registry_new_country_candidates': [k for k, v in overrides.items() if v['finding'] == 'country_candidate_outside_original_whitelist'],
        'outside_registry_selected_A_or_B_count': sum(r['group'] in ('A', 'B') and r['key'] not in registered for r in review),
    }
    assert summary['same_name_groups'] == 22
    assert summary['same_name_omitted_keys'] == 23
    assert summary['absent_markdown_unique_name_keys'] == 17
    report = {
        'schema_version': 1, 'date': '2026-10-25', 'summary': summary,
        'scope': 'Exact Chinese display-name identity, distinct modifier keys. All 559 registry records and all 4484 catalog records were compared; semantic equivalence and runtime support of the outside-registry candidates are not asserted.',
        'production_changes_made_by_this_audit': False,
        'inputs': [{'path': str(p), 'sha256': sha(p)} for p in (BASELINE, CATALOG, REVIEW)],
        'baseline_same_name_groups': name_groups,
        'baseline_collapsed_records': collapsed,
        'baseline_unique_names_absent_from_user_markdown': absent_names,
        'outside_registry_matching_names': outside,
        'limitations': [
            'Absence from the user-edited Markdown is observable; the audit does not claim to know the intention behind each absent name.',
            'A distinct key is not proof of identical, active, or mutually exclusive mechanics; the semantic audit and engine tests should determine presentation.',
            'The v0.1.9 delivery archive provides a stable pre-edit baseline while the parent agent edits the live files.',
        ],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
