"""独立三星评级体系测试。"""

import unittest

from jingwei.domain.models import PatternGrid
from jingwei.game.stars import StarEngine


class StarEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = StarEngine()
        self.target = (
            (True, True, True, True),
            (False, False, False, False),
            (True, True, True, True),
            (False, False, False, False),
        )

    def _grid(self):
        return PatternGrid(4, 4, [list(row) for row in self.target])

    def test_perfect_run_earns_all_three_stars(self):
        result = self.engine.evaluate(
            self._grid(), self.target, compression_ratio=0.75, elapsed_seconds=20
        )

        self.assertTrue(result.shape_star)
        self.assertTrue(result.craft_star)
        self.assertTrue(result.speed_star)
        self.assertEqual(result.stars, 3)
        self.assertEqual(result.stars_label, "★★★")
        self.assertEqual(result.skill_names, ("形", "技", "速"))

    def test_imperfect_shape_loses_shape_star_but_keeps_speed(self):
        grid = self._grid()
        grid.set(0, 0, False)

        result = self.engine.evaluate(
            grid, self.target, compression_ratio=0.75, elapsed_seconds=30
        )

        self.assertFalse(result.shape_star)
        self.assertTrue(result.craft_star)
        self.assertTrue(result.speed_star)
        self.assertEqual(result.match_ratio, 15 / 16)

    def test_low_compression_loses_craft_star(self):
        result = self.engine.evaluate(
            self._grid(), self.target, compression_ratio=0.1, elapsed_seconds=10
        )

        self.assertFalse(result.craft_star)
        self.assertEqual(result.stars, 2)

    def test_over_time_loses_speed_star(self):
        result = self.engine.evaluate(
            self._grid(),
            self.target,
            compression_ratio=0.8,
            elapsed_seconds=200,
            time_limit_seconds=150,
        )

        self.assertFalse(result.speed_star)
        self.assertEqual(result.stars, 2)

    def test_empty_canvas_scores_zero(self):
        result = self.engine.evaluate(
            PatternGrid(4, 4), self.target, compression_ratio=1.0, elapsed_seconds=1
        )

        self.assertEqual(result.stars, 0)
        self.assertEqual(result.stars_label, "☆☆☆")
        self.assertEqual(result.score, 0.0)

    def test_score_grows_with_performance(self):
        poor = self.engine.evaluate(
            PatternGrid(4, 4), self.target, compression_ratio=0.0, elapsed_seconds=1
        )
        great = self.engine.evaluate(
            self._grid(), self.target, compression_ratio=0.9, elapsed_seconds=5
        )

        self.assertLess(poor.score, great.score)

    def test_dimension_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate(PatternGrid(3, 3), self.target)


if __name__ == "__main__":
    unittest.main()