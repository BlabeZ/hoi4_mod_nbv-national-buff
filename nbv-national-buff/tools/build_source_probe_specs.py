"""Define reproducible, test-addon-only native source lifecycle checks."""
import json
from pathlib import Path
from build_mod import write

PROBES = []


def phase(name, effects, present, delta, guards=None):
    return dict(name=name, effects=effects, present=present, delta=delta, guards=guards or [])


def add(name, source_id, key, value, category, name_contains, phases, cleanup=None):
    PROBES.append(dict(name=name, source_id=source_id, key=key, contribution=value,
                       category=category, name_contains=name_contains, phases=phases, cleanup=cleanup or []))


for name, token, character, slot, trait, key, value, display in [
    ('army_advisor', 'franz_halder', 'GER_franz_halder', 'army_chief', 'army_chief_offensive_2', 'army_attack_factor', .1, '陆军进攻'),
    ('political_advisor', 'martin_bormann', 'GER_martin_bormann', 'political_advisor', 'GER_secretary_to_the_fuhrer', 'political_power_factor', .1, '元首秘书'),
    ('high_command', 'ferdinand_schorner', 'GER_ferdinand_schorner', 'high_command', 'army_infantry_2', 'army_infantry_attack_factor', .1, '步兵部队'),
    ('theorist', 'walther_wever', 'GER_walther_wever', 'theorist', 'air_warfare_theorist', 'air_doctrine_cost_factor', -.1, '空战理论家'),
]:
    remove = 'deactivate_advisor = ' + token
    activate = 'activate_advisor = ' + token
    trait_args = '{ character = ' + character + ' slot = ' + slot + ' trait = ' + trait + ' }'
    add(name, ':'.join((character, slot, token, trait)), key, value, 'advisor', display, [
        phase('inactive', [remove], False, 0),
        phase('hired', [activate], True, value),
        phase('trait_removed', ['remove_trait = ' + trait_args], False, 0),
        phase('trait_restored', ['add_trait = ' + trait_args], True, value),
        phase('dismissed', [remove], False, 0),
    ])

other_role = dict(source_id='GER_werner_von_fritsch:army_chief:werner_von_fritsch_army_chief:army_chief_army_high_command',
                  key='army_artillery_attack_factor', present=False)
add('advisor_role_isolation', 'GER_werner_von_fritsch:high_command:werner_von_fritsch_high_command:army_logistics_2',
    'attrition', -.08, 'advisor', '陆军后勤', [
    phase('inactive', ['deactivate_advisor = werner_von_fritsch_army_chief', 'deactivate_advisor = werner_von_fritsch_high_command'], False, 0, [other_role]),
    phase('hired', ['activate_advisor = werner_von_fritsch_high_command'], True, -.08, [other_role]),
    phase('dismissed', ['deactivate_advisor = werner_von_fritsch_high_command'], False, 0, [other_role]),
])

add('technology', 'basic_machine_tools', 'production_factory_max_efficiency_factor', .1, 'technology', '基础机床', [
    phase('inactive', ['set_technology = { basic_machine_tools = 0 popup = no }'], False, 0),
    phase('researched', ['set_technology = { basic_machine_tools = 1 popup = no }'], True, .1),
    phase('removed', ['set_technology = { basic_machine_tools = 0 popup = no }'], False, 0),
    phase('restored', ['set_technology = { basic_machine_tools = 1 popup = no }'], True, .1),
])
add('grand_doctrine', 'new_mobile_warfare', 'army_speed_factor', .1, 'grand_doctrine', '机动作战', [
    phase('inactive', ['set_grand_doctrine = superior_firepower'], False, 0),
    phase('active', ['set_grand_doctrine = new_mobile_warfare'], True, .1),
    phase('removed', ['set_grand_doctrine = superior_firepower'], False, 0),
    phase('restored', ['set_grand_doctrine = new_mobile_warfare'], True, .1),
])
locked_reward = dict(source_id='defensive_postures:reward:5', key='dig_in_speed_factor', present=False)
add('subdoctrine_reward', 'defensive_postures:reward:1', 'dig_in_speed_factor', .05, 'subdoctrine_reward', '防御态势', [
    phase('unearned', ['set_sub_doctrine = defensive_postures'], False, 0, [locked_reward]),
    phase('mastered', ['add_mastery = { amount = 100 sub_doctrine = defensive_postures }'], True, .05, [locked_reward]),
    phase('inactive', ['set_sub_doctrine = mobile_infantry'], False, 0, [locked_reward]),
    phase('reset_on_return', ['set_sub_doctrine = defensive_postures'], False, 0, [locked_reward]),
    phase('restored', ['add_mastery = { amount = 100 sub_doctrine = defensive_postures }'], True, .05, [locked_reward]),
])
add('singular_modifier_reward', 'coastal_defence_fleet:reward:1', 'refit_speed', .15, 'subdoctrine_reward', '岸防舰艇', [
    phase('unearned', ['set_grand_doctrine = new_fleet_in_being', 'set_sub_doctrine = coastal_defence_fleet'], False, 0),
    phase('mastered', ['add_mastery = { amount = 100 sub_doctrine = coastal_defence_fleet }'], True, .15),
    phase('inactive', ['set_grand_doctrine = new_base_strike'], False, 0),
])
add('doctrine_milestone', 'new_mobile_warfare:milestone:1', 'land_reinforce_rate', .02, 'doctrine_milestone', '机动作战', [
    phase('unearned', ['set_grand_doctrine = new_mobile_warfare', 'set_sub_doctrine = defensive_postures'], False, 0),
    phase('completed', ['add_mastery = { amount = 500 sub_doctrine = defensive_postures }'], True, .02),
    phase('inactive', ['set_grand_doctrine = superior_firepower'], False, 0),
    phase('reset_on_return', ['set_grand_doctrine = new_mobile_warfare', 'set_sub_doctrine = defensive_postures'], False, 0),
    phase('restored', ['add_mastery = { amount = 500 sub_doctrine = defensive_postures }'], True, .02),
])
add('dynamic_modifier', 'african_union_executive_council_modifier', 'political_power_gain', -.1, 'dynamic_modifier', '执行理事会', [
    phase('inactive', ['if = { limit = { has_dynamic_modifier = african_union_executive_council_modifier } remove_dynamic_modifier = { modifier = african_union_executive_council_modifier } }'], False, 0),
    phase('active', ['add_dynamic_modifier = { modifier = african_union_executive_council_modifier }'], True, -.1),
    phase('removed', ['remove_dynamic_modifier = { modifier = african_union_executive_council_modifier }'], False, 0),
])
add('active_decision', 'improved_worker_conditions', 'stability_weekly', .005, 'active_decision', '改善工作环境', [
    phase('inactive', ['remove_decision = improved_worker_conditions'], False, 0),
    phase('active', ['activate_decision = improved_worker_conditions'], True, .005),
    phase('removed', ['remove_decision = improved_worker_conditions'], False, 0),
])

for probe in PROBES:
    probe['expected_value_text'] = {
        'army_advisor': '+10.0%', 'political_advisor': '+10.0%', 'high_command': '+10.0%',
        'theorist': '-10.0%', 'advisor_role_isolation': '-8.0%', 'technology': '+10.0%',
        'grand_doctrine': '+10.0%', 'subdoctrine_reward': '+5.0%', 'singular_modifier_reward': '+15.0%',
        'doctrine_milestone': '+2.0%', 'dynamic_modifier': '-0.10', 'active_decision': '+0.50%',
    }[probe['name']]

add('variable_dynamic_spirit', 'GER_army_modifier', 'supply_consumption_factor', .15,
    'dynamic_modifier_variable', '德意志国防军', [
    phase('initial', ['set_variable = { GER_military_supply_consumption_factor = 0.15 }',
                      'if = { limit = { NOT = { has_dynamic_modifier = GER_army_modifier } } add_dynamic_modifier = { modifier = GER_army_modifier } }'], True, 0),
    dict(phase('changed_input', ['set_variable = { GER_military_supply_consumption_factor = 0.20 }'], True, None),
         refresh_cache=False, expected_value_text='+20.0%'),
    dict(phase('zero', ['set_variable = { GER_military_supply_consumption_factor = 0 }'], False, -.15), expected_value_text=''),
    dict(phase('tiny', ['set_variable = { GER_military_supply_consumption_factor = 0.00001 }'], True, -.14999), expected_value_text='+0.001%'),
    phase('removed', ['remove_dynamic_modifier = { modifier = GER_army_modifier }'], False, -.15),
    phase('restored', ['set_variable = { GER_military_supply_consumption_factor = 0.15 }',
                       'add_dynamic_modifier = { modifier = GER_army_modifier }'], True, 0),
])
PROBES[-1]['expected_value_text'] = '+15.0%'

for name, source, key, contribution, display, baseline, delta, value_text in [
    ('ideology_embargo', 'fascism', 'embargo_cost_factor', 1, '法西斯主义', 'democratic', 1.5, '+100.0%'),
    ('ideology_hidden', 'fascism', 'join_faction_tension', -.1, '法西斯主义', 'democratic', -.9, '-10.0%'),
    ('ideology_percentage_points', 'fascism', 'civilian_intel_to_others', 15, '法西斯主义', 'democratic', -5, '+15.0%'),
]:
    add(name, source, key, contribution, 'ideology', display, [
        phase('inactive', ['set_politics = { ruling_party = ' + baseline + ' }'], False, 0),
        phase('active', ['set_politics = { ruling_party = ' + source + ' }'], True, delta),
        phase('removed', ['set_politics = { ruling_party = ' + baseline + ' }'], False, 0),
        phase('restored', ['set_politics = { ruling_party = ' + source + ' }'], True, delta),
    ])
    PROBES[-1]['expected_value_text'] = value_text

if __name__ == '__main__':
    write(Path(__file__).resolve().parent / 'data/source-probe-specs.json',
          json.dumps(dict(probes=PROBES), ensure_ascii=False, indent=2) + '\n')
    print('Prepared', len(PROBES), 'native source lifecycle probes.')
