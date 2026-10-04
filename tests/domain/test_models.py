"""PatternGrid 领域模型的行为测试。"""

import unittest

from jingwei.domain.models import PatternGrid


class PatternGridTests(unittest.TestCase):
    def test_new_grid_is_empty_and_has_requested_size(self):
        grid = PatternGrid(3, 2)

        self.assertEqual(grid.width, 3)
        self.assertEqual(grid.height, 2)
        self.assertTrue(grid.is_empty())
        self.assertEqual(
            grid.to_matrix(),
            ((False, False, False), (False, False, False)),
        )

    def test_set_get_toggle_and_copy_are_independent(self):
        grid = PatternGrid(2, 2)
        grid.set(1, 0, True)

        self.assertTrue(grid.get(1, 0))
        self.assertFalse(grid.toggle(1, 0))
        self.assertFalse(grid.get(1, 0))

        clone = grid.copy()
        clone.set(0, 1, True)

        self.assertFalse(grid.get(0, 1))
        self.assertTrue(clone.get(0, 1))

    def test_out_of_range_coordinates_raise_value_error(self):
        grid = PatternGrid(2, 2)

        with self.assertRaises(ValueError):
            grid.set(2, 0, True)

        with self.assertRaises(ValueError):
            grid.get(-1, 0)

    def test_invalid_dimensions_and_cells_raise_value_error(self):
        with self.assertRaises(ValueError):
            PatternGrid(0, 2)

        with self.assertRaises(ValueError):
            PatternGrid(2, 2, [[False, False]])


if __name__ == "__main__":
    unittest.main()
