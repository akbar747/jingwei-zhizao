"""主窗口与应用接线的离屏冒烟测试。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jingwei.domain.models import PatternGrid
from jingwei.game.catalog import LEVELS
from jingwei.ui.main_window import MainWindow


class MainWindowSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_default_window_loads_first_level(self):
        window = MainWindow()

        self.assertEqual(window.canvas.grid.to_matrix(), LEVELS[0].target)
        self.assertIn(LEVELS[0].name, window.level_label.text())
        window.close()

    def test_perfect_target_compile_awards_three_stars(self):
        window = MainWindow()

        window.compile_current_pattern()

        self.assertIn("★★★", window.stars_label.text())
        self.assertIn("92.5", window.score_label.text())
        window.close()

    def test_load_next_level_resets_canvas_and_target(self):
        window = MainWindow()

        window.load_level(1)

        self.assertEqual(window.canvas.grid.width, 12)
        self.assertEqual(window.canvas.grid.height, 12)
        self.assertEqual(window.target_canvas.grid.to_matrix(), LEVELS[1].target)
        self.assertIn(LEVELS[1].name, window.level_label.text())
        window.close()

    def test_weaving_step_updates_progress(self):
        window = MainWindow()
        window.compile_current_pattern()

        window.weave_preview.advance_one_pick()

        self.assertIn("1/8", window.progress_label.text())
        window.close()

    def test_compile_custom_grid_still_works_in_free_mode(self):
        grid = PatternGrid(2, 2, [[True, False], [True, False]])
        window = MainWindow(grid)

        plan = window.compile_current_pattern()

        self.assertEqual(plan.report.unique_card_count, 1)
        self.assertIn("花本指令：1", window.report_label.text())
        self.assertIn("自由", window.level_label.text())
        window.close()

    def test_modifying_pattern_marks_compile_result_stale(self):
        window = MainWindow()
        window.compile_current_pattern()

        window.canvas.grid.set(0, 0, not window.canvas.grid.get(0, 0))
        window.canvas.patternChanged.emit()

        self.assertIn("已过期", window.status_label.text())
        window.close()



    def test_weaving_finish_shows_result_banner(self):
        window = MainWindow()
        window.compile_current_pattern()
        for _ in range(window.weave_preview.total_picks):
            window.weave_preview.advance_one_pick()

        self.assertIn("织造完成", window.complete_label.text())
        self.assertIn("★★★", window.complete_label.text())
        window.close()

    def test_compile_shows_compression_combo(self):
        window = MainWindow()

        window.compile_current_pattern()

        self.assertIn("连击", window.combo_label.text())
        self.assertIn("花本压缩", window.combo_label.text())
        window.close()
if __name__ == "__main__":
    unittest.main()