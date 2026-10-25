"""Geometry checks for upward reservation, including cascading collisions."""
import unittest
from sidebar_placement import DEFAULT, RESERVATIONS, Rect, placement, reserve_upward, too_close


class PlacementChecks(unittest.TestCase):
    def test_audited_layouts_keep_existing_slot(self):
        selected, trace = reserve_upward(DEFAULT, (r for _, r in RESERVATIONS))
        self.assertEqual(selected, DEFAULT)
        self.assertEqual(trace, [])
        self.assertTrue(all(not too_close(selected, r) for _, r in RESERVATIONS))

    def test_chained_collisions_recheck_previous_obstacles(self):
        boxes = [Rect(0, -170, 77, 77), Rect(0, -80, 77, 77), Rect(0, 0, 77, 77)]
        selected, steps = reserve_upward(Rect(0, 0, 77, 77), boxes)
        self.assertEqual(selected.y, -257)
        # The first move clears both lower boxes; the second clears the upper.
        self.assertEqual(len(steps), 2)
        self.assertTrue(all(not too_close(selected, r) for r in boxes))
        self.assertEqual(reserve_upward(Rect(0, 0, 77, 77), reversed(boxes))[0], selected)

    def test_gap_and_horizontal_separation(self):
        self.assertFalse(too_close(Rect(0, 0, 77, 77), Rect(0, 87, 77, 77)))
        self.assertTrue(too_close(Rect(0, 0, 77, 77), Rect(0, 86, 77, 77)))
        self.assertEqual(reserve_upward(DEFAULT, [Rect(100, -202, 77, 77)])[0], DEFAULT)
        self.assertEqual(reserve_upward(DEFAULT, [Rect(0, -190, 77, 77)])[0].y, -277)

    def test_icon_is_centered_and_runtime_sensing_is_not_claimed(self):
        data = placement()
        icon = data['icon']
        for axis in (0, 1):
            self.assertEqual(icon['position'][axis] + icon['native_frame'][axis] / 2,
                             icon['button_position'][axis] + icon['button_size'][axis] / 2)
        self.assertFalse(data['runtime_collision_detection'])
        self.assertFalse(data['requires_custom_launcher'])
        self.assertEqual(data['excluded_families'], ['TNO and its submods'])


if __name__ == '__main__':
    unittest.main()
