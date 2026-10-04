"""画布坐标与单元几何的纯函数工具。

把鼠标坐标换算逻辑从 Qt 控件中分离出来，使其可以独立测试，并避免
窗口缩放、边距或整数取整问题混入绘图业务。
"""

from __future__ import annotations

import math


def _validate_geometry(
    width: int | float,
    height: int | float,
    columns: int,
    rows: int,
) -> None:
    """校验画布像素尺寸和网格数量。"""
    if width <= 0 or height <= 0:
        raise ValueError("画布宽高必须大于0")
    if not isinstance(columns, int) or not isinstance(rows, int):
        raise ValueError("行数和列数必须是整数")
    if columns <= 0 or rows <= 0:
        raise ValueError("行数和列数必须大于0")


def cell_from_point(
    x: float,
    y: float,
    width: int | float,
    height: int | float,
    columns: int,
    rows: int,
) -> tuple[int, int] | None:
    """将画布内坐标换算为 ``(column, row)``，越界返回 ``None``。

    右边界和下边界视为画布外部，避免用户点击边界时意外落到最后一格。
    """
    _validate_geometry(width, height, columns, rows)

    if x < 0 or y < 0 or x >= width or y >= height:
        return None

    column = min(columns - 1, math.floor(x * columns / width))
    row = min(rows - 1, math.floor(y * rows / height))
    return column, row


def cell_rect(
    column: int,
    row: int,
    width: int | float,
    height: int | float,
    columns: int,
    rows: int,
) -> tuple[float, float, float, float]:
    """返回指定单元的 ``(left, top, cell_width, cell_height)``。"""
    _validate_geometry(width, height, columns, rows)

    if column < 0 or column >= columns or row < 0 or row >= rows:
        raise ValueError(f"单元坐标越界: ({column}, {row})")

    cell_width = width / columns
    cell_height = height / rows
    return column * cell_width, row * cell_height, cell_width, cell_height
