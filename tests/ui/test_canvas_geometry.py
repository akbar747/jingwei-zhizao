"""画布坐标换算的纯函数测试，不需要创建GUI窗口。"""

import unittest

from jingwei.ui.canvas_geometry import cell_from_point, cell_rect


class CanvasGeometryTests(unittest.TestCase):
    def test_top_left_point_maps_to_origin_cell(self):
        self.assertEqual(cell_from_point(0, 0, 100, 80, 4, 2), (0, 0))

    def test_bottom_right_inside_point_maps_to_last_cell(self):
        self.assertEqual(cell_from_point(99, 79, 100, 80, 4, 2), (3, 1))

    def test_edge_and_outside_points_return_none(self):
        self.assertIsNone(cell_from_point(100, 40, 100, 80, 4, 2))
        self.assertIsNone(cell_from_point(40, 80, 100, 80, 4, 2))
        self.assertIsNone(cell_from_point(-1, 20, 100, 80, 4, 2))

    def test_cell_rect_partitions_canvas_without_gaps(self):
        self.assertEqual(cell_rect(2, 1, 100, 80, 4, 2), (50.0, 40.0, 25.0, 40.0))

    def test_invalid_canvas_arguments_raise_value_error(self):
        with self.assertRaises(ValueError):
            cell_from_point(0, 0, 0, 80, 4, 2)
        with self.assertRaises(ValueError):
            cell_rect(0, 0, 100, 80, 0, 2)


if __name__ == "__main__":
    unittest.main()
