"""Regressions for vanilla anonymous asset blocks used by source discovery.

Run with Python 3.9+: python tools/test_script_parser.py
These checks parse representative script fragments; they do not emulate HOI4.
"""
import unittest

from validate_mod import ParseError, children, one, parse_script, scalar, script_signature, walk


class AnonymousBlockTests(unittest.TestCase):
    def test_anonymous_asset_then_dynamic_modifier(self):
        script = (
            'create_equipment_variant = {\n'
            ' optional_assets = {\n'
            '  { icon = "tank_icon" model = "tank_model" }\n'
            ' }\n'
            '}\n'
            'add_dynamic_modifier = {\n'
            ' modifier = SOV_army_dynamic_modifier\n'
            '}\n'
        )
        tree = parse_script(script, 'history/countries/SOV.txt')
        assets = one(one(tree, 'create_equipment_variant').value, 'optional_assets').value
        self.assertEqual((assets[0].key, assets[0].op, assets[0].line), (None, None, 3))
        self.assertEqual(scalar(assets[0].value, 'model'), 'tank_model')
        addition = one(tree, 'add_dynamic_modifier')
        self.assertEqual(addition.line, 6)
        self.assertEqual((one(addition.value, 'modifier').value, one(addition.value, 'modifier').line),
                         ('SOV_army_dynamic_modifier', 7))

    def test_multiple_anonymous_assets(self):
        tree = parse_script('optional_assets = { { icon = first } { icon = second } }\n'
                            'add_dynamic_modifier = { modifier = JAP_military }')
        assets = one(tree, 'optional_assets').value
        self.assertEqual([scalar(asset.value, 'icon') for asset in assets], ['first', 'second'])
        self.assertTrue(all(asset.key is None and asset.op is None for asset in assets))
        self.assertEqual(scalar(one(tree, 'add_dynamic_modifier').value, 'modifier'), 'JAP_military')

    def test_nested_anonymous_blocks_keep_lines(self):
        tree = parse_script('assets = {\n {\n  variants = {\n   { name = nested }\n  }\n }\n}\n'
                            'add_dynamic_modifier = { modifier = CHI_army }')
        anonymous = [entry for entry in walk(tree) if entry.key is None]
        self.assertEqual([entry.line for entry in anonymous], [2, 4])
        self.assertEqual([entry.value for entry in walk(tree) if entry.key == 'name'], ['nested'])
        self.assertEqual(one(tree, 'add_dynamic_modifier').line, 8)
        self.assertEqual(scalar(one(tree, 'add_dynamic_modifier').value, 'modifier'), 'CHI_army')

    def test_anonymous_empty_blocks_retained(self):
        tree = parse_script('assets = { {} { icon = x } {} }')
        assets = one(tree, 'assets').value
        self.assertEqual(len(assets), 3)
        self.assertEqual(script_signature(assets[0]), (None, None, ()))
        self.assertEqual(script_signature(assets[2]), (None, None, ()))
        self.assertEqual(script_signature(assets[1]), (None, None, (('icon', '=', 'x'),)))

    def test_comments_quotes_and_existing_lists(self):
        tree = parse_script('assets = { # { ignored comment\n'
                            ' { icon = "{literal}" name = "named # asset" }\n'
                            '}\n'
                            'tags = { GER JAP }\n'
                            'modifier = first\nmodifier = second\ncheck = { value >= 1 }')
        assets = one(tree, 'assets').value
        self.assertEqual(scalar(assets[0].value, 'icon'), '{literal}')
        self.assertEqual(scalar(assets[0].value, 'name'), 'named # asset')
        self.assertEqual([entry.value for entry in one(tree, 'tags').value], ['GER', 'JAP'])
        self.assertEqual([entry.value for entry in children(tree, 'modifier')], ['first', 'second'])
        self.assertEqual(one(one(tree, 'check').value, 'value').op, '>=')

    def test_malformed_anonymous_blocks_still_raise(self):
        for script in ('assets = { { icon = x }', 'assets = { { icon = x } } }',
                       'assets = { { icon = } }', 'assets > { { icon = x } }'):
            with self.subTest(script=script), self.assertRaises(ParseError):
                parse_script(script)


if __name__ == '__main__':
    unittest.main()
