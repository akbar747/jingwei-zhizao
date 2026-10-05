"""纹样炼成：一键对称、镜像与回环变换。

这些操作把玩家手绘的一部分纹样自动扩展成传统织锦常见的对称构图，
既是易用性功能，也体现“纹样即程序”的可组合思想。
"""

from __future__ import annotations

from enum import Enum

from jingwei.domain.models import PatternGrid


class SymmetryMode(Enum):
    """一键纹样炼成模式。"""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    QUAD = "quad"
    DIAGONAL = "diagonal"

    @property
    def label(self) -> str:
        return {
            SymmetryMode.HORIZONTAL: "左右镜像",
            SymmetryMode.VERTICAL: "上下镜像",
            SymmetryMode.QUAD: "四向圆满",
            SymmetryMode.DIAGONAL: "对角翻折",
        }[self]

    @property
    def description(self) -> str:
        return {
            SymmetryMode.HORIZONTAL: "把左半边纹样镜像到右半边。",
            SymmetryMode.VERTICAL: "把上半边纹样镜像到下半边。",
            SymmetryMode.QUAD: "同时生成上下左右四个对称象限。",
            SymmetryMode.DIAGONAL: "沿主对角线翻折，生成斜向结构。",
        }[self]


def _mirror_horizontal(cells: list[list[bool]]) -> list[list[bool]]:
    width = len(cells[0])
    return [
        [row[column] or row[width - 1 - column] for column in range(width)]
        for row in cells
    ]


def _mirror_vertical(cells: list[list[bool]]) -> list[list[bool]]:
    height = len(cells)
    return [
        [
            cells[row][column] or cells[height - 1 - row][column]
            for column in range(len(cells[0]))
        ]
        for row in range(height)
    ]


def _transpose(cells: list[list[bool]]) -> list[list[bool]]:
    height = len(cells)
    width = len(cells[0])
    return [[cells[row][column] for row in range(height)] for column in range(width)]


def apply_symmetry(grid: PatternGrid, mode: SymmetryMode) -> None:
    """就地把选定的对称变换应用到纹样网格。"""

    if not isinstance(mode, SymmetryMode):
        raise TypeError("mode 必须是 SymmetryMode")

    cells = [list(row) for row in grid.to_matrix()]

    if mode is SymmetryMode.HORIZONTAL:
        transformed = _mirror_horizontal(cells)
    elif mode is SymmetryMode.VERTICAL:
        transformed = _mirror_vertical(cells)
    elif mode is SymmetryMode.QUAD:
        transformed = _mirror_vertical(_mirror_horizontal(cells))
    elif mode is SymmetryMode.DIAGONAL:
        transformed = _transpose(cells)
    else:  # pragma: no cover - Enum 已覆盖全部分支
        raise ValueError(f"未知对称模式: {mode}")

    for row in range(grid.height):
        for column in range(grid.width):
            value = transformed[row][column]
            if grid.get(column, row) != value:
                grid.set(column, row, value)

def describe_symmetry(
    grid: PatternGrid, mode: SymmetryMode
) -> "PatternAction":
    """返回一次对称变换产生的可撤销操作，不修改原网格。

    先记录变化前的值，再在临时网格上计算结果，最后与原始值比较，
    从而支持把整次“纹样炼成”作为一步撤销。
    """

    from jingwei.ui.history import PatternAction

    before = [list(row) for row in grid.to_matrix()]
    scratch = PatternGrid(grid.width, grid.height, [list(row) for row in before])
    apply_symmetry(scratch, mode)
    after = [list(row) for row in scratch.to_matrix()]

    changes: list[tuple[int, int, bool, bool]] = []
    for row in range(grid.height):
        for column in range(grid.width):
            if before[row][column] != after[row][column]:
                changes.append((column, row, before[row][column], after[row][column]))
    return PatternAction(changes=tuple(changes))
