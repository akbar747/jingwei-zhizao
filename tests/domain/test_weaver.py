"""织物矩阵生成行为测试。"""

import unittest

from jingwei.domain.compiler import CompileReport, Pick, WeavePlan, compile_pattern
from jingwei.domain.models import PatternGrid
from jingwei.domain.weaver import build_weave_matrix


class WeaveMatrixTests(unittest.TestCase):
    def test_weave_matrix_uses_each_pick_as_one_weft_row(self):
        grid = PatternGrid(
            3,
            2,
            [
                [True, False, False],
                [False, True, False],
            ],
        )
        plan = compile_pattern(grid)

        matrix = build_weave_matrix(plan)

        self.assertEqual(
            matrix.cells,
            (
                (True, False, False),
                (False, True, False),
            ),
        )
        self.assertEqual(matrix.warp_count, 3)
        self.assertEqual(matrix.weft_count, 2)

    def test_malformed_plan_with_out_of_range_lift_is_rejected(self):
        pick = Pick(
            pick_index=0,
            source_row=0,
            card_id="C01",
            lifted_warp=(5,),
        )
        plan = WeavePlan(
            warp_count=3,
            weft_count=1,
            cards=(),
            picks=(pick,),
            report=CompileReport(1, 1, 0.0),
        )

        with self.assertRaises(ValueError):
            build_weave_matrix(plan)

    def test_pick_count_must_match_weft_count(self):
        plan = WeavePlan(
            warp_count=2,
            weft_count=3,
            cards=(),
            picks=(),
            report=CompileReport(0, 0, 0.0),
        )

        with self.assertRaises(ValueError):
            build_weave_matrix(plan)

    def test_negative_warp_index_is_rejected(self):
        pick = Pick(
            pick_index=0,
            source_row=0,
            card_id="C01",
            lifted_warp=(-1,),
        )
        plan = WeavePlan(
            warp_count=2,
            weft_count=1,
            cards=(),
            picks=(pick,),
            report=CompileReport(1, 1, 0.0),
        )

        with self.assertRaises(ValueError):
            build_weave_matrix(plan)


if __name__ == "__main__":
    unittest.main()
