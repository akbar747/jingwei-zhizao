"""通关结算与庆典层测试。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jingwei.domain.compiler import compile_pattern
from jingwei.domain.models import PatternGrid
from jingwei.game.finale import build_result_summary
from jingwei.game.stars import StarEngine
from jingwei.ui.celebration_overlay import CelebrationOverlay


class ResultSummaryTests(unittest.TestCase):
    def test_three_stars_gets_finale_headline(self):
        target = ((True, True), (False, True))
        grid = PatternGrid(2, 2, [list(row) for row in target])
        result = StarEngine().evaluate(
            grid, target, compression_ratio=0.75, elapsed_seconds=10, time_limit_seconds=30
        )

        summary = build_result_summary("第一根经线", result)

        self.assertEqual(summary.stars, 3)
        self.assertEqual(summary.stars_label, "★★★")
        self.assertIn("名匠", summary.headline)
        self.assertEqual(summary.skill_line, "形 · 技 · 速")

    def test_missing_skills_are_reported(self):
        target = ((True, True), (False, True))
        grid = PatternGrid(2, 2, [list(row) for row in target])
        result = StarEngine().evaluate(
            grid, target, compression_ratio=0.1, elapsed_seconds=99, time_limit_seconds=30
        )

        summary = build_result_summary("第一根经线", result)

        self.assertEqual(summary.stars, 1)
        self.assertIn("形", summary.skill_line)
        self.assertIn("再练", summary.headline)

    def test_summary_carries_metrics(self):
        target = ((True, True), (False, True))
        grid = PatternGrid(2, 2, [list(row) for row in target])
        result = StarEngine().evaluate(
            grid, target, compression_ratio=0.5, elapsed_seconds=5, time_limit_seconds=30
        )

        summary = build_result_summary("菱纹锦", result)

        self.assertEqual(summary.level_name, "菱纹锦")
        self.assertAlmostEqual(summary.match_ratio, 1.0)
        self.assertAlmostEqual(summary.compression_ratio, 0.5)
        self.assertAlmostEqual(summary.score, result.score)


class CelebrationOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _summary(self):
        target = ((True, True, True), (False, True, False), (True, False, True))
        grid = PatternGrid(3, 3, [list(row) for row in target])
        result = StarEngine().evaluate(
            grid, target, compression_ratio=0.8, elapsed_seconds=8, time_limit_seconds=30
        )
        plan = compile_pattern(grid)
        return build_result_summary("万纹回环", result), plan

    def test_overlay_is_hidden_until_shown(self):
        overlay = CelebrationOverlay()
        summary, plan = self._summary()

        self.assertFalse(overlay.isVisible())

        overlay.show_result(summary, plan)

        self.assertTrue(overlay.isVisibleTo(overlay.parent()) or overlay.isVisible())
        self.assertTrue(overlay.active)
        overlay.close()

    def test_particles_advance_and_finish(self):
        overlay = CelebrationOverlay()
        summary, plan = self._summary()
        overlay.show_result(summary, plan)
        initial = overlay.particle_frames_remaining

        overlay.advance_particles()

        self.assertEqual(overlay.particle_frames_remaining, initial - 1)
        while overlay.particle_frames_remaining > 0:
            overlay.advance_particles()
        self.assertEqual(overlay.particle_frames_remaining, 0)
        overlay.close()

    def test_dismiss_hides_overlay(self):
        overlay = CelebrationOverlay()
        summary, plan = self._summary()
        overlay.show_result(summary, plan)

        overlay.dismiss()

        self.assertFalse(overlay.active)
        overlay.close()


if __name__ == "__main__":
    unittest.main()