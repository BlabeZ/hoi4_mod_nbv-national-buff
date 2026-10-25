"""Regression checks for importing an edited, name-only display list."""
import copy
import unittest
from display_layout import parse_markdown, PAGES, BANDS


def document(sections):
    lines = []
    for page in PAGES:
        lines.append('# ' + page)
        for band in BANDS:
            lines.append('## ' + band)
            lines.extend('- ' + name for name in sections.get((page, band), []))
    return '\n'.join(lines)


def entry(ident, name, key=None):
    return dict(id=ident, name=name, key=key or 'metric_' + str(ident), category='政治')


class DisplayLayoutTests(unittest.TestCase):
    def test_reorder_move_remove_keeps_ids_and_registry(self):
        registry = [entry(1, '甲'), entry(2, '乙'), entry(3, '丙')]
        before = copy.deepcopy(registry)
        result = parse_markdown(document({('政治', '常用'): ['乙'], ('海军', '其他修正'): ['甲']}), registry)
        self.assertEqual([r['id'] for r in result['records']], [2, 1])
        self.assertEqual(result['records'][1]['category'], '海军')
        self.assertEqual(result['records'][1]['grid_columns'], 4)
        self.assertEqual([r['id'] for r in result['excluded_records']], [3])
        self.assertEqual(registry, before)

    def test_blank_and_duplicate_names_keep_first_position(self):
        result = parse_markdown(document({('政治', '常用'): ['', '乙', '甲', '乙'], ('陆军', '其他修正'): ['甲']}), [entry(1, '甲'), entry(2, '乙')])
        self.assertEqual([r['id'] for r in result['records']], [2, 1])
        self.assertEqual([r['display_order'] for r in result['records']], [1, 2])
        self.assertEqual(result['ignored_empty_bullets'], 1)
        self.assertEqual(len(result['duplicates']), 2)

    def test_same_label_different_keys_retains_original_first_binding(self):
        result = parse_markdown(document({('工业', '常用'): ['甲', '甲']}), [entry(7, '甲', 'first'), entry(19, '甲', 'factor')])
        self.assertEqual(result['records'][0]['key'], 'first')
        self.assertEqual(result['same_name_bindings'][0]['other_ids'], [19])

    def test_user_confirmed_join_splits_in_place(self):
        names = ['敌方特工情报获取率', '加强意识形态任务成果']
        result = parse_markdown(document({('情报', '其他修正'): [''.join(names)]}), [entry(529, names[0]), entry(538, names[1])])
        self.assertEqual([r['name'] for r in result['records']], names)
        self.assertEqual([r['display_order'] for r in result['records']], [1, 2])
        self.assertEqual(len(result['normalizations']), 1)

    def test_explicit_alias_preserves_both_native_homonyms(self):
        registry = [entry(109, '地区最大工厂数', 'global_building_slots_factor'),
                    entry(142, '地区最大工厂数', 'global_building_slots')]
        before = copy.deepcopy(registry)
        result = parse_markdown(document({('工业', '常用'): ['地区最大工厂数'],
                                         ('工业', '其他修正'): ['地区最大工厂数（固定值）']}), registry)
        self.assertEqual([r['id'] for r in result['records']], [109, 142])
        self.assertEqual(result['records'][1]['name'], '地区最大工厂数（固定值）')
        self.assertEqual(result['records'][1]['display_priority_band'], 'low')
        self.assertEqual(registry, before)

    def test_alias_and_native_name_for_same_key_keep_first_position(self):
        result = parse_markdown(document({('工业', '其他修正'):
            ['地区最大工厂数（固定值）', '地区最大工厂数']}),
            [entry(142, '地区最大工厂数', 'global_building_slots')])
        self.assertEqual([r['id'] for r in result['records']], [142])
        self.assertEqual(len(result['duplicates']), 1)

    def test_unknown_name_is_not_silently_dropped_or_fuzzy_matched(self):
        with self.assertRaisesRegex(ValueError, 'Unknown modifier'):
            parse_markdown(document({('政治', '常用'): ['甲甲']}), [entry(1, '甲')])

    def test_missing_and_repeated_sections_rejected(self):
        text = document({('政治', '常用'): ['甲']})
        for malformed in (text.replace('## 其他修正', '', 1), text + '\n# 政治'):
            with self.assertRaises(ValueError):
                parse_markdown(malformed, [entry(1, '甲')])


if __name__ == '__main__':
    unittest.main()
