"""纹样编辑历史（撤销/重做）测试。"""

import unittest

from jingwei.domain.models import PatternGrid
from jingwei.ui.history import PatternAction, PatternHistory


class PatternHistoryTests(unittest.TestCase):
    def setUp(self):
        self.grid = PatternGrid(2, 2)

    def test_undo_restores_previous_value(self):
        history = PatternHistory()
        self.grid.set(0, 0, True)
        history.push(PatternAction.from_change(0, 0, False, True))

        undone = history.undo(self.grid)

        self.assertEqual(undone, (0, 0))
        self.assertFalse(self.grid.get(0, 0))

    def test_redo_reapplies_value(self):
        history = PatternHistory()
        self.grid.set(0, 0, True)
        history.push(PatternAction.from_change(0, 0, False, True))
        history.undo(self.grid)

        redone = history.redo(self.grid)

        self.assertEqual(redone, (0, 0))
        self.assertTrue(self.grid.get(0, 0))

    def test_push_clears_redo_stack(self):
        history = PatternHistory()
        self.grid.set(0, 0, True)
        history.push(PatternAction.from_change(0, 0, False, True))
        history.undo(self.grid)

        self.grid.set(1, 1, True)
        history.push(PatternAction.from_change(1, 1, False, True))

        self.assertFalse(history.can_redo)
        self.assertTrue(history.can_undo)

    def test_undo_without_history_returns_none(self):
        history = PatternHistory()

        self.assertIsNone(history.undo(self.grid))
        self.assertIsNone(history.redo(self.grid))

    def test_history_respects_limit(self):
        history = PatternHistory(limit=2)
        for column in range(3):
            history.push(PatternAction.from_change(column, 0, False, True))

        self.assertEqual(history.undo_depth, 2)

    def test_clear_removes_all_history(self):
        history = PatternHistory()
        history.push(PatternAction.from_change(0, 0, False, True))

        history.clear()

        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_grouped_action_undoes_multiple_cells(self):
        history = PatternHistory()
        for column in range(2):
            self.grid.set(column, 0, True)
        history.push(
            PatternAction(
                changes=((0, 0, False, True), (1, 0, False, True)),
            )
        )

        history.undo(self.grid)

        self.assertFalse(self.grid.get(0, 0))
        self.assertFalse(self.grid.get(1, 0))


if __name__ == "__main__":
    unittest.main()