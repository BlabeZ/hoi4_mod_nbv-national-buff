"""Prepare a separate HOI4 user directory and TEST-ONLY modifier injection addon.

Does not change the user's existing playsets, settings, saves or installed mods.
The injection addon is never part of the release mod or installation descriptor.
"""
from pathlib import Path
import hashlib
import json
from build_mod import write
from display_layout import load_display_records

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent / 'nbv-test-workspace'
PROFILE = WORK / 'profile'
ADDON = WORK / 'smoke-addon'
ROWS = json.loads((ROOT / 'tools/data/metric-index.json').read_text(encoding='utf-8'))['records']
DISPLAY_ROWS = load_display_records()
ISOLATED = ('political_power_factor', 'mobilization_speed', 'surrender_limit', 'consumer_goods_factor',
            'industrial_capacity_dockyard', 'industrial_capacity_factory', 'command_power_gain_mult')


def display_signature(records):
    """Identify the exact ordered GUI selection independently of the registry."""
    selection = [{key: row[key] for key in
                  ('id', 'category', 'display_priority_band', 'display_order')}
                 for row in records]
    encoded = json.dumps(selection, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def main():
    WORK.mkdir(exist_ok=True)
    PROFILE.mkdir(exist_ok=True)
    write(ADDON / 'descriptor.mod', 'name="NBV isolated smoke test"\nsupported_version="1.19.*"\n')
    write(PROFILE / 'mod/nbv.mod', 'name="National Buff Viewer"\npath="' + ROOT.as_posix() + '"\nsupported_version="1.19.*"\n')
    write(PROFILE / 'mod/nbv_smoke.mod', 'name="NBV isolated smoke test"\npath="' + ADDON.as_posix() + '"\nsupported_version="1.19.*"\n')
    write(PROFILE / 'dlc_load.json', json.dumps(dict(disabled_dlcs=[], enabled_mods=['mod/nbv.mod', 'mod/nbv_smoke.mod'])))
    write(PROFILE / 'settings.txt', '''language="l_simp_chinese"
graphics={
 size={ x=1366 y=768 }
 min_gui={ x=1280 y=720 }
 gui_scale=1.000000
 fullScreen=no
 borderless=no
 shadows=no
 multi_sampling=0
 vsync=yes
}
master_volume=0.000000
autosave="NEVER"
autosave_tocloud=no
save_career_to_cloud=no
hints=no
save_as_binary=no
''')
    write(ADDON / 'common/on_actions/nbv_smoke_on_actions.txt', '''on_actions = {
 on_startup = {
  effect = {
   GER = { country_event = { id = nbv_smoke.1 } }
  }
 }
}
''')
    # Use the same modest nonzero addition for every engine-registered key.
    # Integers may truncate, caps may clamp and some modifiers require conditions.
    # The report must compare actual deltas; successful loading alone is NOT validation.
    idea = 'ideas = { country = { nbv_smoke_probe = { picture = generic_political_reform allowed = { always = no } removal_cost = -1 modifier = {\n'
    idea += ''.join(' ' + r['key'] + ' = 0.125\n' for r in ROWS)
    idea += '} }\n'
    for key in ISOLATED:
        idea += ' nbv_smoke_' + key + ' = { picture = generic_political_reform allowed = { always = no } removal_cost = -1 modifier = { ' + key + ' = 0.125 } }\n'
    idea += '} }\n'
    write(ADDON / 'common/ideas/nbv_smoke_ideas.txt', idea)
    steps = ['nbv_smoke_run = {', ' log = "NBV_SMOKE_BEGIN country=[ROOT.GetTag]"',
             ' log = "NBV_DISPLAY_LAYOUT count=' + str(len(DISPLAY_ROWS)) + ' sha256=' + display_signature(DISPLAY_ROWS) + '"',
             ' nbv_open = yes',
             ' if = { limit = { check_variable = { nbv_page = 1 } has_country_flag = nbv_window_open } log = "NBV_ASSERT first_open PASS" }',
             ' else = { log = "NBV_ASSERT first_open FAIL" }']
    for i, category in enumerate(('政治', '工业', '陆军', '海军', '空军', '情报'), 1):
        counts = [sum(r['category'] == category and r['display_priority_band'] == band for r in DISPLAY_ROWS) for band in ('high', 'low')]
        steps += [' nbv_select_page_' + str(i) + ' = yes',
                  ' if = { limit = { nbv_prepare_view = yes } log = "NBV_COUNTS page=' + str(i) + ' high=[?nbv_high_count|0] low=[?nbv_low_count|0]" }',
                  ' if = { limit = { nbv_prepare_view = yes check_variable = { nbv_high_count = ' + str(counts[0]) + ' } check_variable = { nbv_low_count = ' + str(counts[1]) + ' } } log = "NBV_ASSERT page_' + str(i) + ' PASS" }',
                  ' else = { log = "NBV_ASSERT page_' + str(i) + ' FAIL" }']
        # Exercise the actual single-grid cell resolvers and all seven display slots.
        steps.append(' if = { limit = { nbv_prepare_view = yes }')
        for band, columns in (('high', 3), ('low', 4)):
            members = [r for r in DISPLAY_ROWS if r['category'] == category and r['display_priority_band'] == band]
            for offset, row in enumerate(members):
                start = (offset // columns) * columns
                code = start + 1 if band == 'high' else -(start + 1)
                slot = offset % columns + 1
                stem = 'NBV' + band.title()
                steps += ['  set_temp_variable = { nbv_row_id = ' + str(code) + ' }',
                          '  if = { limit = { nbv_resolve_' + band + '_' + str(slot) + ' = yes }',
                          '   log = "NBV_CELL page=' + str(i) + ' row=' + str(code) + ' band=' + band + ' slot=' + str(slot) + ' expected=' + str(row['id']) + ' resolved=[?nbv_entry_id|0] name=[' + stem + 'Name' + str(slot) + '] value=[' + stem + 'Value' + str(slot) + ']"',
                          '  }']
        steps.append(' }')
    steps += [' nbv_close = yes', ' nbv_open = yes',
              ' if = { limit = { check_variable = { nbv_page = 6 } has_country_flag = nbv_window_open } log = "NBV_ASSERT remember_page PASS" }',
              ' else = { log = "NBV_ASSERT remember_page FAIL" }',
              ' nbv_select_page_1 = yes']
    source_manifest = json.loads((ROOT / 'tools/data/source-display-manifest.json').read_text(encoding='utf-8'))
    for source_id, key, trait in (('sour_loser', 'drift_defence_factor', False),
                                  ('limited_conscription', 'conscription', False),
                                  ('limited_exports', 'industrial_capacity_factory', False),
                                  ('GER_der_fuhrer', 'political_power_factor', True)):
        entry = next(r for r in source_manifest['records'] if r['source_id'] == source_id and r['key'] == key)
        source_fn = 'NBVSource' + str(entry['index'])
        remove = 'remove_country_leader_trait' if trait else 'remove_ideas'
        add = 'add_country_leader_trait' if trait else 'add_ideas'
        for phase in ('before', 'absent', 'restored'):
            if phase == 'absent':
                steps.append(' ' + remove + ' = ' + source_id)
            elif phase == 'restored':
                steps.append(' ' + add + ' = ' + source_id)
            if trait:
                # Test-only: leader changes invalidate the country's cached
                # modifiers but are not necessarily rebuilt inside one event.
                steps.append(' force_update_dynamic_modifier = yes')
            steps.append(' log = "NBV_SOURCE source=' + source_id + ' phase=' + phase + ' value=[?ROOT.modifier@' + key + '|4] text=[' + source_fn + '] END_SOURCE"')
        steps += [' set_temp_variable = { nbv_entry_id = ' + str(entry['metric_id']) + ' }',
                  ' log = "NBV_TOOLTIP id=' + str(entry['metric_id']) + ' text=[NBVRowTooltip] END_TOOLTIP"']
    # Presentation regressions found in review: nonzero rounded to zero, and a
    # vanilla trait title containing its own newline. These fixtures are isolated.
    for source_id, key, trait in (('ENG_mi6_ns', 'enemy_operative_detection_chance', False),
                                  ('army_guerilla_organizer_1', 'dig_in_speed_factor', True)):
        entry = next(r for r in source_manifest['records'] if r['source_id'] == source_id and r['key'] == key)
        add = 'add_country_leader_trait' if trait else 'add_ideas'
        remove = 'remove_country_leader_trait' if trait else 'remove_ideas'
        steps += [' ' + add + ' = ' + source_id, ' force_update_dynamic_modifier = yes',
                  ' log = "NBV_EDGE source=' + source_id + ' text=[NBVSource' + str(entry['index']) + '] END_EDGE"',
                  ' ' + remove + ' = ' + source_id, ' force_update_dynamic_modifier = yes']
    for row in ROWS:
        steps.append(' log = "NBV_BEFORE ' + row['key'] + '=[?ROOT.modifier@' + row['key'] + '|4]"')
    steps.append(' add_ideas = nbv_smoke_probe')
    for row in ROWS:
        steps.append(' log = "NBV_AFTER ' + row['key'] + '=[?ROOT.modifier@' + row['key'] + '|4]"')
    steps.append(' remove_ideas = nbv_smoke_probe')
    for key in ISOLATED:
        steps += [' log = "NBV_ISOLATED_BEFORE ' + key + '=[?ROOT.modifier@' + key + '|4]"',
                  ' add_ideas = nbv_smoke_' + key,
                  ' log = "NBV_ISOLATED_AFTER ' + key + '=[?ROOT.modifier@' + key + '|4]"',
                  ' remove_ideas = nbv_smoke_' + key]
    # Exercise the same scripted-localisation dispatcher used by the dynamic GUI cells.
    for row in ROWS:
        steps += [' set_temp_variable = { nbv_entry_id = ' + str(row['id']) + ' }',
                  ' log = "NBV_DISPATCH ' + str(row['id']) + ' name=[NBVRowName] value=[NBVRowValue]"']
    steps.append(' nbv_toggle_zero_filter = yes')
    for i in range(1, 7):
        steps += [' nbv_select_page_' + str(i) + ' = yes',
                  ' if = { limit = { nbv_prepare_view = yes } log = "NBV_FILTER_COUNTS page=' + str(i) + ' high=[?nbv_high_count|0] low=[?nbv_low_count|0]" }']
    steps += [' nbv_toggle_zero_filter = yes', ' nbv_select_page_1 = yes']
    from source_smoke_probes import build_steps
    steps.append(' log = "NBV_LEADER_NAME name=[ROOT.GetLeader] END_LEADER_NAME"')
    steps += build_steps()
    from dynamic_extended_smoke_probes import build_steps as build_dynamic_steps
    steps += build_dynamic_steps()
    from faction_smoke_probes import build_steps as build_faction_steps
    steps += build_faction_steps()
    for ident, value in [('positive', '15'), ('negative', '-15'), ('fraction', '0.5')]:
        steps += [' set_temp_variable = { nbv_format_probe = ' + value + ' }',
                  ' log = "NBV_FORMAT probe=' + ident + ' text=[?nbv_format_probe|-=%%1] END_FORMAT"']
    from special_source_smoke_probes import build_steps as build_special_steps
    steps += build_special_steps()
    steps += [' log = "NBV_SMOKE_END"', '}']
    write(ADDON / 'common/scripted_effects/nbv_smoke_effects.txt', '\n'.join(steps) + '\n')
    write(ADDON / 'events/nbv_smoke_events.txt', '''add_namespace = nbv_smoke
country_event = {
 id = nbv_smoke.1
 hidden = yes
 is_triggered_only = yes
 immediate = { nbv_smoke_run = yes }
}
''')
    print(json.dumps(dict(profile=PROFILE.as_posix(), addon=ADDON.as_posix(), records=len(ROWS),
                         display_count=len(DISPLAY_ROWS), display_layout_sha256=display_signature(DISPLAY_ROWS))))


if __name__ == '__main__':
    main()
