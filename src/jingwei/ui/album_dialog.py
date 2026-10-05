"""纹样收藏册对话框：展示进度、文化注解并导出作品卡。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from jingwei.domain.models import PatternGrid
from jingwei.game.album import AlbumSummary, build_album_summaries
from jingwei.game.artifact import build_artifact, save_artifact_png
from jingwei.game.levels import LevelDefinition
from jingwei.game.orders import OrderModifier
from jingwei.game.progress import ProgressStore
from jingwei.game.stars import star_result_from_record
from jingwei.ui.pattern_canvas import PatternCanvas


class _AlbumTile(QFrame):
    """收藏册中的单个纹样条目。"""

    def __init__(self, summary: AlbumSummary, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.summary = summary
        self.setObjectName("albumTile")
        self.setFixedWidth(230)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        header = QHBoxLayout()
        title = QLabel(summary.title if summary.unlocked else "？？？")
        title.setObjectName("albumTitle")
        stars = QLabel("★" * (summary.stars or 0) + "☆" * (3 - (summary.stars or 0)))
        stars.setObjectName("albumStars")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(stars)
        layout.addLayout(header)

        target_grid = _grid_from_matrix(summary.target)
        self.canvas = PatternCanvas(target_grid)
        self.canvas.set_read_only(True)
        self.canvas.setMinimumSize(190, 150)
        self.canvas.setMaximumHeight(170)
        self.canvas.setVisible(summary.unlocked)
        layout.addWidget(self.canvas)

        motif = QLabel(summary.motif)
        motif.setObjectName("albumMotif")
        layout.addWidget(motif)

        note = QLabel(summary.cultural_note)
        note.setWordWrap(True)
        note.setObjectName("albumNote")
        layout.addWidget(note)

        if summary.best_score is not None:
            score = QLabel(f"最佳成绩 {summary.best_score:.1f} 分")
            score.setObjectName("albumScore")
            layout.addWidget(score)
        else:
            score = QLabel("尚未织成" if summary.unlocked else "完成上一件作品后解锁")
            score.setObjectName("albumNote")
            layout.addWidget(score)

        self.export_button = QPushButton("导出作品卡")
        self.export_button.setEnabled(summary.unlocked and summary.stars is not None)
        layout.addWidget(self.export_button)
        layout.addStretch(1)


def _grid_from_matrix(matrix: tuple[tuple[bool, ...], ...]) -> PatternGrid:
    return PatternGrid(len(matrix[0]), len(matrix), [list(row) for row in matrix])


class WeavingAlbumDialog(QDialog):
    """以卡片网格展示全部纹样、解锁状态与文化注解。"""

    def __init__(
        self,
        progress: ProgressStore,
        level_lookup,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._progress = progress
        self._level_lookup = level_lookup
        self.setWindowTitle("纹样收藏册")
        self.setMinimumSize(790, 660)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        heading = QLabel(
            f"纹样收藏册 · 已收集 {self._collected_count()} / 3 · "
            f"累计 {progress.total_stars()} 星"
        )
        heading.setObjectName("albumHeading")
        root.addWidget(heading)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(12)
        summaries = build_album_summaries(progress)
        self.tiles: list[_AlbumTile] = []
        for index, summary in enumerate(summaries):
            tile = _AlbumTile(summary)
            tile.export_button.clicked.connect(
                lambda _=False, s=summary: self._export(s)
            )
            grid.addWidget(tile, index // 3, index % 3)
            self.tiles.append(tile)
        grid.setRowStretch(grid.rowCount(), 1)
        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        root.addWidget(close_button, alignment=Qt.AlignRight)

        self.setStyleSheet(
            """
            QDialog { background: #0F172A; color: #E2E8F0; }
            QLabel#albumHeading { color: #FBBF24; font-size: 15pt; font-weight: 800; }
            QFrame#albumTile { background: #172033; border: 1px solid #334155; border-radius: 12px; }
            QLabel#albumTitle { color: #F8FAFC; font-size: 12pt; font-weight: 700; }
            QLabel#albumStars { color: #FDE68A; font-weight: 700; }
            QLabel#albumMotif { color: #7DD3FC; }
            QLabel#albumNote { color: #94A3B8; }
            QLabel#albumScore { color: #FBBF24; font-weight: 700; }
            QPushButton { background: #1E293B; border: 1px solid #475569; border-radius: 8px; padding: 6px 10px; color: #E2E8F0; }
            QPushButton:hover { background: #334155; }
            QPushButton:disabled { color: #64748B; }
            """
        )

    def _collected_count(self) -> int:
        return sum(1 for record in self._progress.records.values() if record.stars > 0)

    def _export(self, summary: AlbumSummary) -> None:
        record = self._progress.get(summary.level_id)
        if record is None:
            return
        level: LevelDefinition = self._level_lookup(summary.level_id)
        result = star_result_from_record(record)
        card = build_artifact(level, result, modifier=OrderModifier.FREE)
        path, _ = QFileDialog.getSaveFileName(
            self,
            "导出织锦作品卡",
            f"{summary.title}-作品卡.png",
            "PNG 图片 (*.png)",
        )
        if path:
            save_artifact_png(card, path)