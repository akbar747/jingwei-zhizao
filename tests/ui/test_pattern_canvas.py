"""点阵画布组件的真实鼠标交互测试。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from jingwei.domain.models import PatternGrid
from jingwei.ui.canvas_geometry import cell_rect
from jingwei.ui.pattern_canvas import PatternCanvas


class PatternCanvasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.grid = PatternGrid(2, 2)
        self.canvas = PatternCanvas(self.grid)
        self.canvas.resize(100, 100)
        self.canvas.show()
        self.app.processEvents()

    def tearDown(self):
        self.canvas.close()

    def _cell_center(self, column: int, row: int) -> QPoint:
        """按控件真实尺寸计算单元中心，避免最小尺寸影响测试坐标。"""
        left, top, width, height = cell_rect(
            column,
            row,
            self.canvas.width(),
            self.canvas.height(),
            2,
            2,
        )
        return QPoint(int(left + width / 2), int(top + height / 2))

    def test_left_click_paints_cell_and_emits_change(self):
        changes = []
        self.canvas.patternChanged.connect(lambda: changes.append(True))

        QTest.mouseClick(
            self.canvas,
            Qt.LeftButton,
            pos=self._cell_center(0, 0),
        )

        self.assertTrue(self.grid.get(0, 0))
        self.assertEqual(changes, [True])

    def test_right_click_clears_cell(self):
        self.grid.set(0, 0, True)
        self.canvas.update()

        QTest.mouseClick(
            self.canvas,
            Qt.RightButton,
            pos=self._cell_center(0, 0),
        )

        self.assertFalse(self.grid.get(0, 0))

    def test_erase_mode_uses_left_button_to_clear(self):
        self.grid.set(1, 1, True)
        self.canvas.set_erase_mode(True)

        QTest.mouseClick(
            self.canvas,
            Qt.LeftButton,
            pos=self._cell_center(1, 1),
        )

        self.assertFalse(self.grid.get(1, 1))

    def test_signal_is_not_emitted_when_cell_value_does_not_change(self):
        changes = []
        self.canvas.patternChanged.connect(lambda: changes.append(True))

        QTest.mouseClick(
            self.canvas,
            Qt.LeftButton,
            pos=self._cell_center(0, 0),
        )
        QTest.mouseClick(
            self.canvas,
            Qt.LeftButton,
            pos=self._cell_center(0, 0),
        )

        self.assertEqual(len(changes), 1)


if __name__ == "__main__":
    unittest.main()
