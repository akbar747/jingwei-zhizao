"""教学关卡目录测试。"""

import unittest

from jingwei.game.catalog import LEVELS
from jingwei.game.levels import LevelDefinition


class LevelCatalogTests(unittest.TestCase):
    def test_catalog_has_unique_levels(self):
        self.assertGreaterEqual(len(LEVELS), 6)
        self.assertEqual(len({level.level_id for level in LEVELS}), len(LEVELS))
        self.assertEqual(len({level.name for level in LEVELS}), len(LEVELS))

    def test_first_three_sizes_match_the_tutorial_arc(self):
        self.assertEqual(
            [(level.width, level.height) for level in LEVELS[:3]],
            [(8, 8), (12, 12), (16, 16)],
        )

    def test_every_level_target_is_loadable_and_has_repeated_rows(self):
        for level in LEVELS:
            grid = level.create_grid()
            self.assertIsInstance(level, LevelDefinition)
            self.assertEqual(grid.width, level.width)
            self.assertEqual(grid.height, level.height)
            self.assertEqual(grid.to_matrix(), level.target)
            self.assertFalse(grid.is_empty())
            self.assertLess(len(set(level.target)), len(level.target))

    def test_every_level_has_player_facing_copy(self):
        for level in LEVELS:
            self.assertTrue(level.name)
            self.assertTrue(level.description)
            self.assertTrue(level.hint)
            self.assertGreater(level.par_seconds, 0)


if __name__ == "__main__":
    unittest.main()
