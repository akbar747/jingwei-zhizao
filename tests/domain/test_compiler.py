"""纹样到花本指令的编译行为测试。"""

import unittest

from jingwei.domain.compiler import compile_pattern
from jingwei.domain.models import PatternGrid


class CompilePatternTests(unittest.TestCase):
    def test_identical_rows_share_one_card_and_keep_first_seen_order(self):
        grid = PatternGrid(
            3,
            3,
            [
                [True, False, True],
                [False, True, False],
                [True, False, True],
            ],
        )

        plan = compile_pattern(grid)

        self.assertEqual([pick.card_id for pick in plan.picks], ["C01", "C02", "C01"])
        self.assertEqual(plan.report.original_pick_count, 3)
        self.assertEqual(plan.report.unique_card_count, 2)
        self.assertAlmostEqual(plan.report.compression_ratio, 1 / 3)

    def test_card_records_first_row_and_occurrences(self):
        grid = PatternGrid(
            2,
            3,
            [
                [False, True],
                [False, True],
                [True, False],
            ],
        )

        plan = compile_pattern(grid)
        first_card = plan.cards[0]

        self.assertEqual(first_card.card_id, "C01")
        self.assertEqual(first_card.lifted_warp, (1,))
        self.assertEqual(first_card.first_source_row, 0)
        self.assertEqual(first_card.occurrences, 2)

    def test_pick_lifted_warp_matches_true_columns(self):
        grid = PatternGrid(4, 1, [[False, True, True, False]])

        plan = compile_pattern(grid)

        self.assertEqual(plan.picks[0].lifted_warp, (1, 2))
        self.assertEqual(plan.picks[0].source_row, 0)
        self.assertEqual(plan.picks[0].pick_index, 0)

    def test_empty_pattern_compiles_to_empty_plan_with_warning(self):
        plan = compile_pattern(PatternGrid(3, 3))

        self.assertEqual(plan.picks, ())
        self.assertEqual(plan.cards, ())
        self.assertEqual(plan.report.original_pick_count, 0)
        self.assertEqual(plan.report.unique_card_count, 0)
        self.assertTrue(plan.report.warnings)
        self.assertIn("纹样为空", plan.report.warnings[0])

    def test_plan_keeps_grid_dimensions(self):
        plan = compile_pattern(PatternGrid(5, 4))

        self.assertEqual(plan.warp_count, 5)
        self.assertEqual(plan.weft_count, 4)


if __name__ == "__main__":
    unittest.main()
