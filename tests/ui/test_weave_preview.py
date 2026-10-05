"""织造预览状态机测试。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jingwei.domain.compiler import compile_pattern
from jingwei.domain.models import PatternGrid
from jingwei.ui.weave_preview import WeavePreview


class WeavePreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.grid = PatternGrid(3, 2, [[True, False, True], [False, True, False]])
        self.plan = compile_pattern(self.grid)
        self.preview = WeavePreview()

    def tearDown(self):
        self.preview.close()

    def test_set_plan_resets_progress(self):
        self.preview.set_plan(self.plan)

        self.assertEqual(self.preview.total_picks, 2)
        self.assertEqual(self.preview.completed_picks, 0)
        self.assertTrue(self.preview.can_start)

    def test_advance_one_pick_and_finish_once(self):
        self.preview.set_plan(self.plan)
        finished = []
        self.preview.weavingFinished.connect(lambda: finished.append(True))

        self.preview.advance_one_pick()
        self.assertEqual(self.preview.completed_picks, 1)
        self.assertFalse(finished)

        self.preview.advance_one_pick()
        self.assertEqual(self.preview.completed_picks, 2)
        self.assertEqual(finished, [True])

        self.preview.advance_one_pick()
        self.assertEqual(self.preview.completed_picks, 2)
        self.assertEqual(finished, [True])

    def test_reset_returns_to_beginning(self):
        self.preview.set_plan(self.plan)
        self.preview.advance_one_pick()

        self.preview.reset()

        self.assertEqual(self.preview.completed_picks, 0)
        self.assertFalse(self.preview.is_running)

    def test_empty_plan_cannot_start(self):
        self.preview.set_plan(compile_pattern(PatternGrid(3, 2)))

        self.assertFalse(self.preview.can_start)
        self.preview.start_animation()
        self.assertFalse(self.preview.is_running)


    def test_finish_starts_celebration_and_can_advance_to_end(self):
        self.preview.set_plan(self.plan)
        for _ in range(self.preview.total_picks):
            self.preview.advance_one_pick()

        self.assertTrue(self.preview.celebration_active)
        self.assertGreater(self.preview.celebration_frames_remaining, 0)

        while self.preview.celebration_active:
            self.preview.advance_celebration()

        self.assertFalse(self.preview.celebration_active)

    def test_reset_stops_celebration(self):
        self.preview.set_plan(self.plan)
        for _ in range(self.preview.total_picks):
            self.preview.advance_one_pick()

        self.preview.reset()

        self.assertFalse(self.preview.celebration_active)


if __name__ == "__main__":
    unittest.main()
