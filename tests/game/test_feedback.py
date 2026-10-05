"""花本压缩连击反馈测试。"""

import unittest

from jingwei.domain.compiler import compile_pattern
from jingwei.domain.models import PatternGrid
from jingwei.game.feedback import calculate_compile_combo


class CompileComboTests(unittest.TestCase):
    def test_compression_produces_visible_multiplier(self):
        grid = PatternGrid(
            4,
            4,
            [
                [True, False, True, False],
                [True, False, True, False],
                [False, True, False, True],
                [False, True, False, True],
            ],
        )
        plan = compile_pattern(grid)

        combo = calculate_compile_combo(plan)

        self.assertEqual(combo.reused_rows, 2)
        self.assertEqual(combo.multiplier, 2)
        self.assertIn("连击", combo.message)
        self.assertIn("50%", combo.message)

    def test_empty_plan_gets_friendly_prompt(self):
        combo = calculate_compile_combo(compile_pattern(PatternGrid(4, 4)))

        self.assertEqual(combo.reused_rows, 0)
        self.assertEqual(combo.multiplier, 1)
        self.assertIn("先画", combo.message)


if __name__ == "__main__":
    unittest.main()
