"""主窗口与应用接线的离屏冒烟测试。"""

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jingwei.domain.models import PatternGrid
from jingwei.game.catalog import LEVELS, get_level
from jingwei.game.orders import OrderModifier
from jingwei.game.progress import ProgressStore
from jingwei.ui.operations import SymmetryMode
from jingwei.ui.main_window import MainWindow


def fill_grid(grid: PatternGrid, target: tuple[tuple[bool, ...], ...]) -> None:
    for row, row_values in enumerate(target):
        for column, value in enumerate(row_values):
            grid.set(column, row, value)


class MainWindowSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _window(
        self,
        level_index: int = 0,
        *,
        progress: ProgressStore | None = None,
        modifier: OrderModifier = OrderModifier.FREE,
    ) -> MainWindow:
        return MainWindow(
            level_index=level_index,
            progress=progress or ProgressStore.in_memory(),
            modifier=modifier,
        )

    def test_default_window_loads_first_level_with_empty_canvas(self):
        window = self._window()

        self.assertTrue(window.canvas.grid.is_empty())
        self.assertEqual(window.target_canvas.grid.to_matrix(), LEVELS[0].target)
        self.assertIn(LEVELS[0].name, window.level_label.text())
        window.close()

    def test_perfect_target_compile_awards_three_stars(self):
        window = self._window()
        fill_grid(window.canvas.grid, LEVELS[0].target)

        window.compile_current_pattern()

        self.assertIn("★★★", window.stars_label.text())
        self.assertIn("形", window.ability_label.text())
        window.close()

    def test_load_next_level_resets_canvas_and_target(self):
        progress = ProgressStore.in_memory()
        progress.record("L01", stars=1, score=60.0, completed_at=5.0)
        window = self._window(progress=progress)
        window.load_level(1)

        self.assertTrue(window.canvas.grid.is_empty())
        self.assertEqual(window.canvas.grid.width, 12)
        self.assertEqual(window.canvas.grid.height, 12)
        self.assertEqual(window.target_canvas.grid.to_matrix(), LEVELS[1].target)
        self.assertIn(LEVELS[1].name, window.level_label.text())
        window.close()

    def test_weaving_step_updates_progress(self):
        window = self._window()
        fill_grid(window.canvas.grid, LEVELS[0].target)
        window.compile_current_pattern()

        window.weave_preview.advance_one_pick()

        self.assertIn("1/8", window.progress_label.text())
        window.close()

    def test_compile_custom_grid_still_works_in_free_mode(self):
        grid = PatternGrid(2, 2, [[True, False], [True, False]])
        window = MainWindow(grid, progress=ProgressStore.in_memory())

        plan = window.compile_current_pattern()

        self.assertEqual(plan.report.unique_card_count, 1)
        self.assertIn("花本指令：1", window.report_label.text())
        self.assertIn("自由", window.level_label.text())
        window.close()

    def test_modifying_pattern_marks_compile_result_stale(self):
        window = self._window()
        fill_grid(window.canvas.grid, LEVELS[0].target)
        window.compile_current_pattern()

        window.canvas.grid.set(0, 0, not window.canvas.grid.get(0, 0))
        window.canvas.patternChanged.emit()

        self.assertIn("已过期", window.status_label.text())
        window.close()

    def test_weaving_finish_shows_result_banner(self):
        window = self._window()
        fill_grid(window.canvas.grid, LEVELS[0].target)
        window.compile_current_pattern()
        for _ in range(window.weave_preview.total_picks):
            window.weave_preview.advance_one_pick()

        self.assertIn("织造完成", window.complete_label.text())
        self.assertIn("★★★", window.complete_label.text())
        window.close()

    def test_inspiration_fills_canvas_with_a_pattern(self):
        window = self._window()

        window.generate_inspiration()

        self.assertFalse(window.canvas.grid.is_empty())
        self.assertIn("灵感纹样", window.status_label.text())
        window.close()

    def test_alchemy_expands_and_is_undoable(self):
        window = self._window()
        window.canvas.grid.set(0, 0, True)
        window.canvas.update()

        window.apply_alchemy(SymmetryMode.QUAD)
        far = window.canvas.grid.width - 1

        self.assertTrue(window.canvas.grid.get(far, 0))
        self.assertTrue(window.canvas.grid.get(0, far))
        self.assertTrue(window.canvas.grid.get(far, far))

        window.canvas.undo()

        self.assertFalse(window.canvas.grid.get(far, 0))
        window.close()

    def test_undo_redo_buttons_follow_history(self):
        window = self._window()
        self.assertFalse(window.undo_button.isEnabled())

        window.canvas.grid.set(0, 0, True)
        window.canvas.patternChanged.emit()
        from jingwei.ui.history import PatternAction

        window.canvas.history.push(PatternAction.from_change(0, 0, False, True))
        window.canvas.canUndoChanged.emit(True)

        self.assertTrue(window.undo_button.isEnabled())

        window.undo_button.click()

        self.assertFalse(window.canvas.grid.get(0, 0))
        self.assertTrue(window.redo_button.isEnabled())

        window.redo_button.click()

        self.assertTrue(window.canvas.grid.get(0, 0))
        window.close()

    def test_weaving_finish_opens_celebration_overlay(self):
        window = self._window()
        fill_grid(window.canvas.grid, LEVELS[0].target)
        window.compile_current_pattern()
        for _ in range(window.weave_preview.total_picks):
            window.weave_preview.advance_one_pick()

        self.assertTrue(window.celebration.active)
        self.assertEqual(window.celebration.summary.stars, 3)
        window.celebration.dismiss()
        self.assertFalse(window.celebration.active)
        window.close()

    def test_compile_shows_compression_combo(self):
        window = self._window()
        fill_grid(window.canvas.grid, LEVELS[0].target)

        window.compile_current_pattern()

        self.assertIn("连击", window.combo_label.text())
        self.assertIn("花本压缩", window.combo_label.text())
        window.close()

    def test_default_time_label_shows_order_time(self):
        window = self._window()

        self.assertIn("订单", window.time_label.text())
        self.assertRegex(window.time_label.text(), r"\d{2}:\d{2}")
        window.close()

    def test_challenge_timeout_stops_weaving(self):
        window = self._window()
        fill_grid(window.canvas.grid, LEVELS[0].target)
        window.compile_current_pattern()
        window.start_weave_button.click()

        window.tick_challenge(1000)

        self.assertIn("00:00", window.time_label.text())
        self.assertIn("订单超时", window.status_label.text())
        window.close()

    def test_level_bar_shows_only_first_level_unlocked(self):
        window = self._window()

        self.assertTrue(window.level_buttons[0].isEnabled())
        self.assertFalse(window.level_buttons[1].isEnabled())
        self.assertFalse(window.level_buttons[2].isEnabled())
        window.close()

    def test_completing_level_unlocks_next_and_records_progress(self):
        progress = ProgressStore.in_memory()
        window = self._window(progress=progress)
        fill_grid(window.canvas.grid, LEVELS[0].target)
        window.compile_current_pattern()
        for _ in range(window.weave_preview.total_picks):
            window.weave_preview.advance_one_pick()

        self.assertIsNotNone(progress.get("L01"))
        self.assertTrue(window.level_buttons[1].isEnabled())
        self.assertIn("★", window.level_buttons[0].text())
        window.close()

    def test_cannot_load_locked_level(self):
        window = self._window()

        window.load_level(2)

        self.assertEqual(window._level_index, 0)
        self.assertIn("尚未解锁", window.status_label.text())
        window.close()

    def test_masterpiece_order_sets_compression_floor(self):
        window = self._window()
        window.apply_order(OrderModifier.MASTERPIECE)

        self.assertIn("精品订单", window.order_label.text())
        self.assertAlmostEqual(window.order.minimum_compression, 0.85)
        window.close()

    def test_memory_order_hides_target_after_preview(self):
        window = self._window()
        window.apply_order(OrderModifier.MEMORY)

        self.assertTrue(window.target_canvas.isVisibleTo(window))

        window._hide_target_for_memory_order()

        self.assertFalse(window.target_canvas.isVisibleTo(window))
        window.close()


if __name__ == "__main__":
    unittest.main()