"""Reject special-source attribution when its country scope is not provable."""
from decimal import Decimal
import unittest

from validate_mod import parse_script
from build_special_source_bindings import build, landmark_plan, status_plan
from build_source_bindings import DEFAULT_GAME, ROOT


def building(body):
    return parse_script("landmark_test = { " + body + " }")[0]


class SpecialSourceTests(unittest.TestCase):
    def test_rejected_landmark_candidate_retains_its_exact_audit_gates(self):
        plan = landmark_plan(building('dlc_allowed={has_dlc="Test DLC"} '
            'level_cap={province_max=1} country_modifiers={'
            'enable_for_controllers={GER ENG} modifiers={stability_factor=0.05}} '
            'state_modifiers={local_manpower=0.8}'))
        self.assertEqual(plan['controllers'], ['GER', 'ENG'])
        self.assertIn('has_dlc = "Test DLC"', plan['activation_script'])
        self.assertIn('landmark_test > 0', plan['activation_script'])
        self.assertIn('landmark_test < 2', plan['activation_script'])
        self.assertIn('is_fully_controlled_by = ROOT', plan['activation_script'])
        self.assertIn('has_damaged_buildings = no', plan['activation_script'])
        self.assertIn('any_controlled_state = { is_fully_controlled_by = ROOT landmark_test > 0 }', plan['activation_script'])
        self.assertNotIn('building_level@', plan['activation_script'])
        self.assertNotIn('non_damaged_building_level', plan['activation_script'])
        self.assertEqual(plan['eligibility'],
                         'one_building_in_a_fully_controlled_state_and_no_damaged_buildings_anywhere_in_country')
        self.assertEqual([r.key for r in plan['modifiers']], ['stability_factor'])
        self.assertEqual(len(parse_script(plan['activation_script'])), 1)

    def test_unrestricted_controller_has_no_invented_tag(self):
        plan = landmark_plan(building('level_cap={province_max=1} '
            'country_modifiers={modifiers={stability_factor=0.05}}'))
        self.assertEqual(plan['controllers'], [])
        self.assertNotIn('tag =', plan['activation_script'])

    def test_unadapted_conditions_or_duplicate_blocks_fail(self):
        for text in (
            'level_cap={province_max=1} country_modifiers={enable={always=yes} modifiers={}}',
            'level_cap={province_max=2} country_modifiers={modifiers={}}',
            'level_cap={province_max=1} country_modifiers={enable_for_controllers={ROOT} modifiers={}}',
            'level_cap={province_max=1} country_modifiers={modifiers={}} country_modifiers={modifiers={}}',
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                landmark_plan(building(text))

    def test_status_formulas_have_zero_midpoint_and_correct_endpoints(self):
        for ident, literal, expected in (
            ('stability_good_modifier', '0.2', {'.5': '0', '.75': '.1', '1': '.2'}),
            ('stability_bad_modifier', '-.5', {'0': '-.5', '.25': '-.25', '.5': '0'}),
            ('war_support_good_modifier', '.3', {'.5': '0', '.75': '.15', '1': '.3'}),
            ('war_support_bad_modifier', '-.95', {'0': '-.95', '.25': '-.475', '.5': '0'}),
        ):
            expr = status_plan(ident, Decimal(literal))['value_expression']
            self.assertEqual(expr['variable'], 'ROOT.has_stability' if ident.startswith('stability_') else 'ROOT.has_war_support')
            for value, want in expected.items():
                self.assertEqual(Decimal(value) * Decimal(expr['coefficient']) + Decimal(expr['offset']),
                                 Decimal(want))

    def test_all_26_landmark_candidates_are_absent_from_production(self):
        result = build(DEFAULT_GAME, ROOT / 'tools/data/metric-index.json')
        production = [row for rows in result['by_modifier'].values() for row in rows]
        candidates = result['unavailable_landmark_candidates']
        self.assertEqual(len(candidates), 26)
        self.assertEqual(len(production), 15)
        self.assertTrue(all(row['source_type'] != 'landmark' for row in production))
        self.assertTrue(all(not row['source_id'].startswith('landmark_') for row in production))
        self.assertTrue(all(row['production_eligible'] is False for row in candidates))
        self.assertTrue(all(row['source']['file'] and row['value_literal'] for row in candidates))
        self.assertEqual({row['id'] for row in production} & {row['id'] for row in candidates}, set())
        self.assertEqual(result['statistics']['landmark_binding_count'], 0)
        self.assertEqual(result['statistics']['unavailable_landmark_binding_count'], 26)


if __name__ == '__main__':
    unittest.main()
