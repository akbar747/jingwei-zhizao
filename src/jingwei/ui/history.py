"""纹样编辑历史：按笔画分组记录单元变化，支持撤销与重做。"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.models import PatternGrid

DEFAULT_HISTORY_LIMIT = 200


@dataclass(frozen=True)
class PatternAction:
    """一次可撤销操作，包含若干单元的前后值。"""

    changes: tuple[tuple[int, int, bool, bool], ...]

    @classmethod
    def from_change(
        cls, x: int, y: int, before: bool, after: bool
    ) -> "PatternAction":
        return cls(changes=((x, y, before, after),))

    @property
    def is_empty(self) -> bool:
        return not self.changes

    def apply(self, grid: PatternGrid, *, forward: bool) -> None:
        """把操作应用到网格；``forward=False`` 时撤销。"""

        for x, y, before, after in self.changes:
            grid.set(x, y, after if forward else before)


class PatternHistory:
    """维护撤销/重做栈；只依赖 PatternGrid，便于单元测试。"""

    def __init__(self, limit: int = DEFAULT_HISTORY_LIMIT) -> None:
        if limit <= 0:
            raise ValueError("历史记录上限必须大于0")
        self.limit = limit
        self._undo: list[PatternAction] = []
        self._redo: list[PatternAction] = []

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    @property
    def undo_depth(self) -> int:
        return len(self._undo)

    @property
    def redo_depth(self) -> int:
        return len(self._redo)

    def push(self, action: PatternAction) -> None:
        """记录新操作，并清空重做栈。"""

        if action.is_empty:
            return
        self._undo.append(action)
        if len(self._undo) > self.limit:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self, grid: PatternGrid) -> tuple[int, int] | None:
        if not self._undo:
            return None
        action = self._undo.pop()
        action.apply(grid, forward=False)
        self._redo.append(action)
        return _first_coordinate(action)

    def redo(self, grid: PatternGrid) -> tuple[int, int] | None:
        if not self._redo:
            return None
        action = self._redo.pop()
        action.apply(grid, forward=True)
        self._undo.append(action)
        return _first_coordinate(action)

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()


def _first_coordinate(action: PatternAction) -> tuple[int, int] | None:
    if action.is_empty:
        return None
    x, y, _before, _after = action.changes[0]
    return x, y