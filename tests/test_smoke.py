"""主窗口与应用接线的离屏冒烟测试。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jingwei.domain.models import PatternGrid
from jingwei.ui.main_window import MainWindow


class MainWindowSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_compile_current_pattern_updates_report(self):
        grid = PatternGrid(
            2,
            2,
            [
                [True, False],
                [True, False],
            ],
        )
        window = MainWindow(grid)

        plan = window.compile_current_pattern()

        self.assertEqual(plan.report.unique_card_count, 1)
        self.assertIn("花本指令：1", window.report_label.text())
        window.close()

    def test_modifying_pattern_marks_compile_result_stale(self):
        window = MainWindow(PatternGrid(2, 2))
        window.compile_current_pattern()

        window.canvas.grid.set(0, 0, True)
        window.canvas.patternChanged.emit()

        self.assertIn("已过期", window.status_label.text())
        window.close()

    def test_default_grid_is_sixteen_by_sixteen(self):
        window = MainWindow()

        self.assertEqual(window.canvas.grid.width, 16)
        self.assertEqual(window.canvas.grid.height, 16)
        window.close()


if __name__ == "__main__":
    unittest.main()
