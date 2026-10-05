"""逐梭织造预览组件。"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from jingwei.domain.compiler import WeavePlan
from jingwei.domain.weaver import WeaveMatrix, build_weave_matrix


class WeavePreview(QWidget):
    """按照WeavePlan逐梭推进，并绘制织物生长过程。"""

    weavingFinished = Signal()
    pickAdvanced = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plan: WeavePlan | None = None
        self._matrix: WeaveMatrix | None = None
        self._completed_picks = 0
        self._finished_emitted = False
        self._running = False
        self._timer = QTimer(self)
        self._timer.setInterval(260)
        self._timer.timeout.connect(self.advance_one_pick)
        self.setMinimumHeight(230)

    @property
    def total_picks(self) -> int:
        return len(self._plan.picks) if self._plan is not None else 0

    @property
    def completed_picks(self) -> int:
        return self._completed_picks

    @property
    def current_pick_index(self) -> int | None:
        if self._completed_picks <= 0:
            return None
        return self._completed_picks - 1

    @property
    def can_start(self) -> bool:
        return self._matrix is not None and self.total_picks > 0

    @property
    def is_running(self) -> bool:
        return self._running

    def set_plan(self, plan: WeavePlan | None) -> None:
        self._timer.stop()
        self._running = False
        self._plan = plan
        self._matrix = build_weave_matrix(plan) if plan and plan.picks else None
        self._completed_picks = 0
        self._finished_emitted = False
        self.update()

    def reset(self) -> None:
        self._timer.stop()
        self._running = False
        self._completed_picks = 0
        self._finished_emitted = False
        self.update()

    def advance_one_pick(self) -> None:
        if not self.can_start or self._completed_picks >= self.total_picks:
            return

        self._completed_picks += 1
        self.pickAdvanced.emit(self._completed_picks)
        self.update()

        if self._completed_picks == self.total_picks and not self._finished_emitted:
            self._finished_emitted = True
            self._timer.stop()
            self._running = False
            self.weavingFinished.emit()

    def start_animation(self) -> None:
        if not self.can_start:
            return
        if self._completed_picks >= self.total_picks:
            self.reset()
        self._running = True
        self._timer.start()
        self.update()

    def stop_animation(self) -> None:
        self._timer.stop()
        self._running = False
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#111827"))

        if self._matrix is None:
            painter.setPen(QColor("#9CA3AF"))
            painter.drawText(self.rect(), Qt.AlignCenter, "编译后开始织造")
            painter.end()
            return

        margin = 32
        width = max(1, self.width() - margin * 2)
        height = max(1, self.height() - margin * 2)
        warp_count = max(1, self._matrix.warp_count)
        weft_count = max(1, self._matrix.weft_count)

        for column in range(warp_count):
            x = margin + (column + 0.5) * width / warp_count
            active = (
                self.current_pick_index is not None
                and column in self._plan.picks[self.current_pick_index].lifted_warp
            )
            painter.setPen(QPen(QColor("#F59E0B" if active else "#475569"), 2 if active else 1))
            painter.drawLine(int(x), margin, int(x), self.height() - margin)

        if self._completed_picks:
            cloth_height = height * self._completed_picks / weft_count
            cloth_top = self.height() - margin - cloth_height
            painter.fillRect(QRectF(margin, cloth_top, width, cloth_height), QColor("#E7E5E4"))
            for row in range(self._completed_picks):
                row_top = cloth_top + row * cloth_height / self._completed_picks
                for column, covered in enumerate(self._matrix.cells[row]):
                    if not covered:
                        x = margin + column * width / warp_count
                        painter.fillRect(
                            QRectF(x, row_top, width / warp_count, cloth_height / self._completed_picks),
                            QColor("#94A3B8"),
                        )

        shuttle_y = margin + max(0, self._completed_picks - 1) * height / weft_count
        direction_right = self._completed_picks % 2 == 1
        shuttle_x = margin + (width * 0.82 if direction_right else width * 0.18)
        painter.setBrush(QColor("#B64B3E"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(shuttle_x - 24, shuttle_y - 7, 48, 14), 7, 7)

        painter.setPen(QColor("#CBD5E1"))
        painter.drawText(
            QRectF(margin, 6, width, 20),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"织造进度 {self._completed_picks}/{self.total_picks}",
        )
        painter.end()
