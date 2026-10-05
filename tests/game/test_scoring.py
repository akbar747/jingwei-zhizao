"""游戏评分领域测试。"""

import unittest

from jingwei.domain.models import PatternGrid
from jingwei.game.scoring import ScoreEngine


class ScoreEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ScoreEngine()
        self.checkerboard = (
            (True, False, True, False),
            (False, True, False, True),
            (True, False, True, False),
            (False, True, False, True),
        )
        self.all_true = ((True, True, True, True),) * 4

    def test_exact_match_awards_three_stars(self):
        grid = PatternGrid(4, 4, [list(row) for row in self.checkerboard])

        result = self.engine.score(grid, self.checkerboard, compression_ratio=0.25)

        self.assertEqual(result.match_ratio, 1.0)
        self.assertEqual(result.wrong_cells, 0)
        self.assertEqual(result.stars, 3)
        self.assertAlmostEqual(result.score, 77.5)

    def test_partial_match_at_half_gets_no_star(self):
        rows = [list(row) for row in self.all_true]
        rows[2] = [False, False, False, False]
        rows[3] = [False, False, False, False]
        grid = PatternGrid(4, 4, rows)

        result = self.engine.score(grid, self.all_true, compression_ratio=0.0)

        self.assertEqual(result.match_ratio, 0.5)
        self.assertEqual(result.wrong_cells, 8)
        self.assertEqual(result.stars, 0)

    def test_partial_match_above_half_awards_one_star(self):
        rows = [list(row) for row in self.all_true]
        rows[3] = [False, False, False, False]
        grid = PatternGrid(4, 4, rows)

        result = self.engine.score(grid, self.all_true)

        self.assertEqual(result.match_ratio, 0.75)
        self.assertEqual(result.stars, 1)

    def test_empty_pattern_never_gets_stars(self):
        result = self.engine.score(
            PatternGrid(4, 4),
            self.all_true,
            compression_ratio=1.0,
        )

        self.assertEqual(result.score, 30.0)
        self.assertEqual(result.stars, 0)
        self.assertEqual(result.match_ratio, 0.0)

    def test_dimension_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.score(PatternGrid(3, 4), self.checkerboard)


if __name__ == "__main__":
    unittest.main()