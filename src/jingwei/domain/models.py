"""领域层基础数据模型。

本模块只使用 Python 标准库，方便在没有图形界面的环境中直接测试。
"""

from __future__ import annotations


class PatternGrid:
    """表示用户绘制的二维点阵纹样。

    单元值为 ``True`` 时，表示该位置的经线在对应梭次被提升；
    ``False`` 表示经线不提升。坐标原点位于左上角，``x`` 为列、``y`` 为行。
    """

    def __init__(
        self,
        width: int,
        height: int,
        cells: list[list[bool]] | None = None,
    ) -> None:
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError("画布宽度和高度必须是整数")
        if width <= 0 or height <= 0:
            raise ValueError("画布宽度和高度必须大于0")

        self._width = width
        self._height = height

        if cells is None:
            self._cells = [[False for _ in range(width)] for _ in range(height)]
        else:
            self._cells = self._normalize_cells(cells)

    @property
    def width(self) -> int:
        """返回纹样的列数（经线数）。"""
        return self._width

    @property
    def height(self) -> int:
        """返回纹样的行数（纬线梭数）。"""
        return self._height

    def _normalize_cells(self, cells: list[list[bool]]) -> list[list[bool]]:
        """复制并校验外部传入的矩阵，避免调用方与模型共享可变列表。"""
        if len(cells) != self._height:
            raise ValueError("传入矩阵的行数与画布高度不一致")

        normalized: list[list[bool]] = []
        for row in cells:
            if len(row) != self._width:
                raise ValueError("传入矩阵的列数与画布宽度不一致")
            copied_row: list[bool] = []
            for value in row:
                if not isinstance(value, bool):
                    raise ValueError("纹样单元必须是布尔值")
                copied_row.append(value)
            normalized.append(copied_row)
        return normalized

    def _validate_coordinates(self, x: int, y: int) -> None:
        """统一校验坐标，防止所有读写入口产生越界行为。"""
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("坐标必须是整数")
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            raise ValueError(f"坐标越界: ({x}, {y})")

    def set(self, x: int, y: int, value: bool) -> None:
        """设置指定单元的布尔值。"""
        self._validate_coordinates(x, y)
        if not isinstance(value, bool):
            raise ValueError("纹样单元必须是布尔值")
        self._cells[y][x] = value

    def get(self, x: int, y: int) -> bool:
        """读取指定单元的布尔值。"""
        self._validate_coordinates(x, y)
        return self._cells[y][x]

    def toggle(self, x: int, y: int) -> bool:
        """翻转指定单元并返回翻转后的值。"""
        new_value = not self.get(x, y)
        self.set(x, y, new_value)
        return new_value

    def clear(self) -> None:
        """将全部单元恢复为未提升状态。"""
        for row in self._cells:
            for x in range(self._width):
                row[x] = False

    def copy(self) -> PatternGrid:
        """返回一个独立的深拷贝。"""
        return PatternGrid(self._width, self._height, self._cells)

    def is_empty(self) -> bool:
        """判断纹样是否没有任何提升单元。"""
        return not any(any(row) for row in self._cells)

    def row(self, y: int) -> tuple[bool, ...]:
        """以不可变元组返回指定行，避免调用方绕过坐标校验。"""
        if not isinstance(y, int) or y < 0 or y >= self._height:
            raise ValueError(f"行号越界: {y}")
        return tuple(self._cells[y])

    def to_matrix(self) -> tuple[tuple[bool, ...], ...]:
        """以不可变矩阵返回完整纹样快照。"""
        return tuple(tuple(row) for row in self._cells)
