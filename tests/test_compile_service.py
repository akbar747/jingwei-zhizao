"""应用层编译服务的行为测试。"""

import unittest

from jingwei.application.compile_service import CompileService
from jingwei.domain.compiler import WeavePlan
from jingwei.domain.models import PatternGrid


class CompileServiceTests(unittest.TestCase):
    def test_compile_returns_weave_plan_from_domain_compiler(self):
        grid = PatternGrid(
            3,
            2,
            [
                [True, False, True],
                [True, False, True],
            ],
        )

        plan = CompileService().compile(grid)

        self.assertIsInstance(plan, WeavePlan)
        self.assertEqual(len(plan.picks), 2)
        self.assertEqual(plan.report.unique_card_count, 1)
        self.assertEqual([pick.card_id for pick in plan.picks], ["C01", "C01"])


if __name__ == "__main__":
    unittest.main()
