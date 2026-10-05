"""通关庆典层：织物成品、星星、粒子与后续操作。"""

from __future__ import annotations

import math

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from jingwei.domain.compiler import WeavePlan
from jingwei.domain.weaver import build_weave_matrix
from jingwei.game.finale import ResultSummary

_PARTICLE_COUNT = 48


class CelebrationOverlay(QWidget):
    """覆盖在主窗口上的结算面板，带扩散粒子动画。"""

    exportRequested = Signal()
    replayRequested = Signal()
    nextLevelRequested = Signal()
    dismissed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._summary: ResultSummary | None = None
        self._cells: tuple[tuple[bool, ...], ...] | None = None
        self._particle_frames = 0
        self._particle_total = 60
        self._particle_timer = QTimer(self)
        self._particle_timer.setInterval(40)
        self._particle_timer.timeout.connect(self.advance_particles)
        self.setVisible(False)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._build_ui()

    @property
    def active(self) -> bool:
        return self._summary is not None

    @property
    def summary(self) -> ResultSummary | None:
        return self._summary

    @property
    def particle_frames_remaining(self) -> int:
        return self._particle_frames

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setAlignment(Qt.AlignCenter)
        self.card = QFrame()
        self.card.setObjectName("finaleCard")
        self.card.setFixedSize(620, 720)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(10)

        self.kicker_label = QLabel("织造完成")
        self.kicker_label.setObjectName("finaleKicker")
        self.kicker_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.kicker_label)

        self.title_label = QLabel()
        self.title_label.setObjectName("finaleTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.title_label)

        self.stars_view = _StarClothView()
        self.stars_view.setMinimumHeight(260)
        card_layout.addWidget(self.stars_view, stretch=1)

        self.skill_label = QLabel()
        self.skill_label.setObjectName("finaleSkill")
        self.skill_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.skill_label)

        self.metrics_label = QLabel()
        self.metrics_label.setObjectName("finaleMetrics")
        self.metrics_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.metrics_label)

        self.encouragement_label = QLabel()
        self.encouragement_label.setObjectName("finaleEncourage")
        self.encouragement_label.setAlignment(Qt.AlignCenter)
        self.encouragement_label.setWordWrap(True)
        card_layout.addWidget(self.encouragement_label)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self.export_button = QPushButton("导出作品卡")
        self.export_button.setObjectName("goldButton")
        self.replay_button = QPushButton("再织一次")
        self.next_button = QPushButton("下一关")
        self.close_button = QPushButton("返回工坊")
        for button in (self.export_button, self.replay_button, self.next_button, self.close_button):
            button.setMinimumHeight(38)
            buttons.addWidget(button)
        card_layout.addLayout(buttons)
        root.addWidget(self.card)

        self.export_button.clicked.connect(self.exportRequested.emit)
        self.replay_button.clicked.connect(self.replayRequested.emit)
        self.next_button.clicked.connect(self.nextLevelRequested.emit)
        self.close_button.clicked.connect(self.dismiss)

        self.setStyleSheet(
            """
            CelebrationOverlay { background: rgba(8, 12, 24, 190); }
            QFrame#finaleCard { background: #172033; border: 2px solid #C8952E; border-radius: 18px; }
            QLabel#finaleKicker { color: #F472B6; font-size: 12pt; font-weight: 800; letter-spacing: 2px; }
            QLabel#finaleTitle { color: #FBBF24; font-size: 24pt; font-weight: 900; }
            QLabel#finaleSkill { color: #7DD3FC; font-size: 14pt; font-weight: 800; }
            QLabel#finaleMetrics { color: #FDE68A; font-size: 12pt; font-weight: 700; }
            QLabel#finaleEncourage { color: #CBD5E1; font-size: 11pt; }
            QPushButton { background: #1E293B; border: 1px solid #475569; border-radius: 8px; padding: 7px 10px; color: #E2E8F0; }
            QPushButton:hover { background: #334155; }
            QPushButton#goldButton { background: #B7791F; border-color: #F6C453; color: #FFFFFF; font-weight: 700; }
            """
        )

    def show_result(self, summary: ResultSummary, plan: WeavePlan) -> None:
        """展示一次通关结算并启动粒子动画。"""

        self._summary = summary
        matrix = build_weave_matrix(plan) if plan.picks else None
        self._cells = None if matrix is None else matrix.cells
        self.stars_view.set_result(summary, self._cells)
        self.title_label.setText(summary.headline)
        self.stars_view.set_stars(summary.stars)
        self.skill_label.setText(f"{summary.stars_label}   星章 {summary.skill_line}")
        self.metrics_label.setText(
            f"得分 {summary.score:.1f}   ·   匹配 {summary.match_ratio:.0%}   ·   "
            f"压缩 {summary.compression_ratio:.0%}"
        )
        self.encouragement_label.setText(summary.encouragement)
        self._particle_frames = self._particle_total
        self._particle_timer.start()
        self.resize(self.parent().size() if self.parent() is not None else self.size())
        self.show()
        self.raise_()

    def advance_particles(self) -> None:
        if self._particle_frames <= 0:
            self._particle_timer.stop()
            return
        self._particle_frames -= 1
        self.stars_view.set_particle_progress(
            1.0 - self._particle_frames / self._particle_total
        )
        if self._particle_frames == 0:
            self._particle_timer.stop()

    def dismiss(self) -> None:
        self._particle_timer.stop()
        self._particle_frames = 0
        self._summary = None
        self.hide()
        self.dismissed.emit()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(8, 12, 24, 190))
        painter.end()


class _StarClothView(QWidget):
    """在庆典卡片内绘制织物矩阵、星星与扩散粒子。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cells: tuple[tuple[bool, ...], ...] | None = None
        self._stars = 0
        self._particle_progress = 0.0

    def set_result(self, summary: ResultSummary, cells: tuple[tuple[bool, ...], ...] | None) -> None:
        self._cells = cells
        self._stars = summary.stars
        self._particle_progress = 0.0
        self.update()

    def set_stars(self, stars: int) -> None:
        self._stars = stars
        self.update()

    def set_particle_progress(self, progress: float) -> None:
        self._particle_progress = max(0.0, min(1.0, progress))
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        painter.fillRect(rect, QColor("#F4E8CE"))

        margin = 22
        star_height = 54
        cloth_rect = QRectF(
            margin,
            margin,
            rect.width() - margin * 2,
            max(40, rect.height() - margin * 2 - star_height),
        )
        if self._cells:
            self._draw_cloth(painter, cloth_rect, self._cells)
        painter.setPen(QPen(QColor("#8C7A5A"), 1))
        painter.drawRect(cloth_rect)

        painter.setFont(_star_font(34))
        painter.setPen(QColor("#C8952E"))
        star_text = "★" * self._stars + "☆" * (3 - self._stars)
        painter.drawText(
            QRectF(0, cloth_rect.bottom() + 6, rect.width(), star_height),
            Qt.AlignHCenter | Qt.AlignVCenter,
            star_text,
        )

        if self._particle_progress > 0:
            self._draw_particles(painter, rect.center(), self._particle_progress)
        painter.end()

    @staticmethod
    def _draw_cloth(painter: QPainter, rect: QRectF, cells: tuple[tuple[bool, ...], ...]) -> None:
        warp_count = len(cells[0])
        weft_count = len(cells)
        cell_width = rect.width() / warp_count
        cell_height = rect.height() / weft_count
        painter.save()
        painter.setClipRect(rect)
        painter.fillRect(rect, QColor("#E9DCC3"))
        painter.setPen(QPen(QColor("#8C1D2B"), max(1.0, cell_width * 0.5)))
        for column in range(warp_count):
            x = rect.left() + (column + 0.5) * cell_width
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
        painter.setPen(Qt.NoPen)
        for row, row_cells in enumerate(cells):
            top = rect.top() + row * cell_height
            for column, lifted in enumerate(row_cells):
                if lifted:
                    continue
                painter.fillRect(
                    QRectF(rect.left() + column * cell_width, top, cell_width, cell_height),
                    QColor("#E9DCC3"),
                )
        painter.restore()

    @staticmethod
    def _draw_particles(painter: QPainter, center, progress: float) -> None:
        colors = (QColor("#FBBF24"), QColor("#F87171"), QColor("#F8FAFC"), QColor("#7DD3FC"))
        painter.setPen(Qt.NoPen)
        for index in range(_PARTICLE_COUNT):
            angle = index * math.tau / _PARTICLE_COUNT
            distance = 20 + progress * 220
            x = center.x() + math.cos(angle) * distance
            y = center.y() + math.sin(angle) * distance + progress * 70
            radius = max(1.0, 5.0 * (1.0 - progress))
            painter.setBrush(colors[index % len(colors)])
            painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2, radius * 2))


def _star_font(size: int) -> QFont:
    font = QFont()
    font.setFamilies(["Microsoft YaHei UI", "Microsoft YaHei", "SimHei"])
    font.setPointSize(size)
    font.setBold(True)
    return font