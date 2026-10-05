"""可交互的点阵纹样画布。"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from jingwei.domain.models import PatternGrid
from jingwei.ui.canvas_geometry import cell_from_point, cell_rect


class PatternCanvas(QWidget):
    """鼠标绘制二维纹样的画布组件。

    左键在普通模式下填色，右键始终擦除；开启橡皮模式后，左键也执行
    擦除。只有单元值确实发生变化时才发送 ``patternChanged``，避免界面
    因为重复拖动而执行无意义的编译失效和重绘。
    """

    patternChanged = Signal()

    def __init__(self, grid: PatternGrid, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._grid = grid
        self._erase_mode = False
        self._read_only = False
        self._is_painting = False
        self._paint_value = True
        self.setMinimumSize(320, 320)
        self.setMouseTracking(False)
        self.setAutoFillBackground(False)

    @property
    def grid(self) -> PatternGrid:
        """返回当前画布绑定的纹样模型。"""
        return self._grid

    def set_grid(self, grid: PatternGrid) -> None:
        """替换画布模型并立即重绘。"""
        if not isinstance(grid, PatternGrid):
            raise TypeError("PatternCanvas 只接受 PatternGrid")
        self._grid = grid
        self._is_painting = False
        self.update()

    def set_erase_mode(self, enabled: bool) -> None:
        """设置左键是否切换为擦除操作。"""
        self._erase_mode = bool(enabled)

    def set_read_only(self, enabled: bool) -> None:
        """设置只读预览，禁止鼠标修改纹样。"""
        self._read_only = bool(enabled)
        self._is_painting = False

    def _value_for_button(self, button: Qt.MouseButton) -> bool | None:
        """把鼠标按钮转换为单元值；未知按钮返回 None。"""
        if button == Qt.RightButton:
            return False
        if button == Qt.LeftButton:
            return not self._erase_mode
        return None

    def _paint_at(self, x: float, y: float) -> None:
        """把当前位置对应的单元设置为当前绘制值。"""
        cell = cell_from_point(
            x,
            y,
            self.width(),
            self.height(),
            self._grid.width,
            self._grid.height,
        )
        if cell is None:
            return

        column, row = cell
        if self._grid.get(column, row) == self._paint_value:
            return

        self._grid.set(column, row, self._paint_value)
        self.update()
        self.patternChanged.emit()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """开始一次鼠标绘制操作。"""
        if self._read_only:
            event.ignore()
            return
        value = self._value_for_button(event.button())
        if value is None:
            super().mousePressEvent(event)
            return

        self._is_painting = True
        self._paint_value = value
        position = event.position()
        self._paint_at(position.x(), position.y())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """拖动时持续绘制，并自动去重相同单元。"""
        if not self._is_painting:
            super().mouseMoveEvent(event)
            return

        position = event.position()
        self._paint_at(position.x(), position.y())
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """结束鼠标绘制操作。"""
        self._is_painting = False
        event.accept()

    def paintEvent(self, event) -> None:
        """绘制画布背景、网格和所有提升单元。"""
        del event  # QPainter 会使用当前控件状态，不需要事件对象本身。
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.fillRect(self.rect(), QColor("#F7F1E3"))

        canvas_width = self.width()
        canvas_height = self.height()

        for row in range(self._grid.height):
            for column in range(self._grid.width):
                left, top, width, height = cell_rect(
                    column,
                    row,
                    canvas_width,
                    canvas_height,
                    self._grid.width,
                    self._grid.height,
                )
                rect = QRectF(left, top, width, height)
                if self._grid.get(column, row):
                    painter.fillRect(rect, QColor("#1D232A"))

        painter.setPen(QPen(QColor("#BEB6A6"), 1))
        for column in range(self._grid.width + 1):
            x = canvas_width * column / self._grid.width
            painter.drawLine(int(x), 0, int(x), canvas_height)
        for row in range(self._grid.height + 1):
            y = canvas_height * row / self._grid.height
            painter.drawLine(0, int(y), canvas_width, int(y))

        painter.end()
