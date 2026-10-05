"""纹样炼成：对称与镜像变换测试。"""

import unittest

from jingwei.domain.models import PatternGrid
from jingwei.ui.operations import SymmetryMode, apply_symmetry


class SymmetryTests(unittest.TestCase):
    def setUp(self):
        self.grid = PatternGrid(4, 4)
        # 只在左上角点亮一个单元
        self.grid.set(0, 0, True)

    def test_horizontal_mirrors_left_to_right(self):
        apply_symmetry(self.grid, SymmetryMode.HORIZONTAL)

        self.assertTrue(self.grid.get(0, 0))
        self.assertTrue(self.grid.get(3, 0))
        self.assertFalse(self.grid.get(0, 3))

    def test_vertical_mirrors_top_to_bottom(self):
        apply_symmetry(self.grid, SymmetryMode.VERTICAL)

        self.assertTrue(self.grid.get(0, 0))
        self.assertTrue(self.grid.get(0, 3))
        self.assertFalse(self.grid.get(3, 0))

    def test_quad_fills_all_four_corners(self):
        apply_symmetry(self.grid, SymmetryMode.QUAD)

        self.assertTrue(self.grid.get(0, 0))
        self.assertTrue(self.grid.get(3, 0))
        self.assertTrue(self.grid.get(0, 3))
        self.assertTrue(self.grid.get(3, 3))

    def test_diagonal_transposes_around_main_diagonal(self):
        self.grid.clear()
        self.grid.set(1, 0, True)

        apply_symmetry(self.grid, SymmetryMode.DIAGONAL)

        self.assertTrue(self.grid.get(0, 1))

    def test_symmetry_preserves_original_cells(self):
        self.grid.clear()
        self.grid.set(1, 1, True)
        self.grid.set(2, 1, True)

        apply_symmetry(self.grid, SymmetryMode.QUAD)

        for row in range(4):
            for column in range(4):
                original_expected = (column, row) in {(1, 1), (2, 1)}
                if original_expected:
                    self.assertTrue(self.grid.get(column, row))

    def test_all_symmetry_modes_have_labels(self):
        for mode in SymmetryMode:
            self.assertTrue(mode.label.strip())
            self.assertTrue(mode.description.strip())

    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(TypeError):
            apply_symmetry(self.grid, "horizontal")


if __name__ == "__main__":
    unittest.main()