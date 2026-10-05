"""游戏化主窗口：关卡、评分、绘图与逐梭织造。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from jingwei.application.compile_service import CompileService
from jingwei.domain.compiler import WeavePlan
from jingwei.domain.models import PatternGrid
from jingwei.game.catalog import LEVELS, get_level
from jingwei.game.levels import LevelDefinition
from jingwei.game.scoring import ScoreEngine, ScoreResult
from jingwei.ui.pattern_canvas import PatternCanvas
from jingwei.ui.weave_preview import WeavePreview


class MainWindow(QMainWindow):
    """织造工坊主窗口。"""

    def __init__(
        self,
        grid: PatternGrid | None = None,
        parent: QWidget | None = None,
        level_index: int = 0,
    ) -> None:
        super().__init__(parent)
        self._compile_service = CompileService()
        self._score_engine = ScoreEngine()
        self._current_plan: WeavePlan | None = None
        self._last_score: ScoreResult | None = None
        self._free_mode = grid is not None
        self._level_index = None if self._free_mode else level_index
        self._level: LevelDefinition | None = None if self._free_mode else get_level(level_index)
        self._grid = grid if grid is not None else self._level.create_grid()

        self.setWindowTitle("经纬智造 · 织造工坊")
        self.setMinimumSize(1180, 820)

        self._build_ui()
        self._connect_signals()
        self._apply_style()
        self._refresh_hud()
        self._update_report_placeholder()

    @property
    def current_plan(self) -> WeavePlan | None:
        return self._current_plan

    @property
    def level(self) -> LevelDefinition | None:
        return self._level

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)
        root_layout.addWidget(self._build_hud())

        main_row = QHBoxLayout()
        main_row.setSpacing(12)
        main_row.addWidget(self._build_left_panel())
        main_row.addWidget(self._build_center_panel(), stretch=1)
        main_row.addWidget(self._build_right_panel())
        root_layout.addLayout(main_row, stretch=1)
        root_layout.addWidget(self._build_weave_panel())
        self.setCentralWidget(root)

    def _build_hud(self) -> QWidget:
        hud = QFrame()
        hud.setObjectName("hudPanel")
        layout = QHBoxLayout(hud)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(20)
        self.level_label = QLabel()
        self.level_label.setObjectName("levelTitle")
        self.objective_label = QLabel()
        self.objective_label.setObjectName("objectiveText")
        self.objective_label.setWordWrap(True)
        self.score_label = QLabel()
        self.score_label.setObjectName("scoreText")
        self.stars_label = QLabel()
        self.stars_label.setObjectName("starsText")
        self.progress_label = QLabel()
        self.progress_label.setObjectName("progressText")
        layout.addWidget(self.level_label)
        layout.addWidget(self.objective_label, stretch=1)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.stars_label)
        return hud

    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setFixedWidth(190)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        title = QLabel("工匠工具")
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        self.paint_button = QPushButton("画笔")
        self.paint_button.setCheckable(True)
        self.paint_button.setChecked(True)
        self.erase_button = QPushButton("橡皮")
        self.erase_button.setCheckable(True)
        self.clear_button = QPushButton("清空纹样")
        self.compile_button = QPushButton("编译花本")
        self.compile_button.setObjectName("primaryButton")
        for button in (self.paint_button, self.erase_button, self.clear_button, self.compile_button):
            button.setMinimumHeight(38)
            layout.addWidget(button)
        layout.addStretch(1)
        tip = QLabel("左键绘制，右键擦除。\n编译会计算匹配率和花本压缩奖励。")
        tip.setWordWrap(True)
        tip.setObjectName("hintText")
        layout.addWidget(tip)
        return panel

    def _build_center_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("stagePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        title = QLabel("纹样设计台")
        title.setObjectName("panelTitle")
        self.canvas = PatternCanvas(self._grid)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(title)
        layout.addWidget(self.canvas, stretch=1)
        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setMinimumWidth(300)
        panel.setMaximumWidth(370)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        title = QLabel("关卡目标")
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        self.target_canvas = PatternCanvas(PatternGrid(2, 2))
        self.target_canvas.set_read_only(True)
        self.target_canvas.setMinimumSize(170, 170)
        self.target_canvas.setMaximumHeight(240)
        layout.addWidget(self.target_canvas)
        if self._level is not None:
            self.target_canvas.set_grid(self._level.create_grid())
        else:
            self.target_canvas.setVisible(False)
        self.report_label = QLabel()
        self.report_label.setWordWrap(True)
        self.report_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.report_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.report_label, stretch=1)
        self.next_level_button = QPushButton("下一关")
        self.next_level_button.setObjectName("goldButton")
        layout.addWidget(self.next_level_button)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("statusText")
        layout.addWidget(self.status_label)
        return panel

    def _build_weave_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("stagePanel")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        self.weave_preview = WeavePreview()
        layout.addWidget(self.weave_preview, stretch=1)
        controls = QVBoxLayout()
        controls.setSpacing(8)
        title = QLabel("织造剧场")
        title.setObjectName("panelTitle")
        controls.addWidget(title)
        self.start_weave_button = QPushButton("开始织造")
        self.start_weave_button.setObjectName("primaryButton")
        self.step_weave_button = QPushButton("下一梭")
        self.reset_weave_button = QPushButton("重织")
        self.complete_label = QLabel("")
        self.complete_label.setObjectName("completeText")
        self.complete_label.setWordWrap(True)
        controls.addWidget(self.start_weave_button)
        controls.addWidget(self.step_weave_button)
        controls.addWidget(self.reset_weave_button)
        controls.addWidget(self.complete_label)
        controls.addStretch(1)
        layout.addLayout(controls)
        return panel

    def _connect_signals(self) -> None:
        self.paint_button.clicked.connect(self._activate_paint_mode)
        self.erase_button.clicked.connect(self._activate_erase_mode)
        self.clear_button.clicked.connect(self._clear_pattern)
        self.compile_button.clicked.connect(self.compile_current_pattern)
        self.start_weave_button.clicked.connect(self._start_weaving)
        self.step_weave_button.clicked.connect(self._step_weaving)
        self.reset_weave_button.clicked.connect(self._reset_weaving)
        self.next_level_button.clicked.connect(self._next_level)
        self.canvas.patternChanged.connect(self._on_pattern_changed)
        self.weave_preview.pickAdvanced.connect(self._on_pick_advanced)
        self.weave_preview.weavingFinished.connect(self._on_weaving_finished)

    def _activate_paint_mode(self) -> None:
        self.paint_button.setChecked(True)
        self.erase_button.setChecked(False)
        self.canvas.set_erase_mode(False)

    def _activate_erase_mode(self) -> None:
        self.paint_button.setChecked(False)
        self.erase_button.setChecked(True)
        self.canvas.set_erase_mode(True)

    def _clear_pattern(self) -> None:
        self.canvas.grid.clear()
        self.canvas.update()
        self._invalidate_plan("纹样已清空：请重新绘制并编译")
        self._update_report_placeholder("纹样已清空")

    def _on_pattern_changed(self) -> None:
        if self._current_plan is not None:
            self._invalidate_plan("结果已过期：请重新点击“编译花本”")

    def _invalidate_plan(self, status: str) -> None:
        self._current_plan = None
        self._last_score = None
        self.weave_preview.set_plan(None)
        self.complete_label.setText("")
        self.progress_label.setText(f"织造 0/{self.canvas.grid.height}")
        self._reset_score_display()
        self.status_label.setText(status)

    def _reset_score_display(self) -> None:
        if self._level is None:
            self.score_label.setText("自由模式")
            self.stars_label.setText("自由创作")
        else:
            self.score_label.setText("得分 0.0")
            self.stars_label.setText("☆☆☆")

    def _refresh_hud(self) -> None:
        if self._level is None:
            self.level_label.setText("自由织造 · 无目标")
            self.objective_label.setText("自由创作模式：体验花本编译和逐梭织造。")
        else:
            self.level_label.setText(f"第{self._level_index + 1}关 · {self._level.name}")
            self.objective_label.setText(self._level.description)
        self.progress_label.setText(f"织造 0/{self.canvas.grid.height}")
        self._reset_score_display()

    def load_level(self, index: int) -> LevelDefinition:
        level = get_level(index)
        self._free_mode = False
        self._level_index = index
        self._level = level
        self._grid = level.create_grid()
        self.canvas.set_grid(self._grid)
        self.target_canvas.setVisible(True)
        self.target_canvas.set_grid(level.create_grid())
        self._current_plan = None
        self._last_score = None
        self.weave_preview.set_plan(None)
        self.complete_label.setText("")
        self._refresh_hud()
        self._update_report_placeholder("新关卡已载入")
        self.status_label.setText(f"{level.hint} 点击“编译花本”开始。")
        return level

    def _next_level(self) -> None:
        if self._level_index is None:
            return
        next_index = self._level_index + 1
        if next_index >= len(LEVELS):
            self.status_label.setText("已完成全部教学关卡，可以继续自由挑战。")
            return
        self.load_level(next_index)

    def _start_weaving(self) -> None:
        if self._current_plan is None:
            self.compile_current_pattern()
        if self._current_plan is None or not self._current_plan.picks:
            self.status_label.setText("织造失败：请先绘制并编译有效纹样。")
            return
        self.weave_preview.start_animation()
        self.status_label.setText("织造中：观察经线提升、梭子穿行和织物生长。")

    def _step_weaving(self) -> None:
        if self._current_plan is None:
            self.compile_current_pattern()
        if self._current_plan is None or not self._current_plan.picks:
            self.status_label.setText("织造失败：请先绘制并编译有效纹样。")
            return
        self.weave_preview.advance_one_pick()

    def _reset_weaving(self) -> None:
        self.weave_preview.reset()
        self.progress_label.setText(f"织造 0/{self.weave_preview.total_picks}")
        self.status_label.setText("织造已重置，可以重新播放。")

    def _on_pick_advanced(self, completed: int) -> None:
        self.progress_label.setText(f"织造 {completed}/{self.weave_preview.total_picks}")

    def _on_weaving_finished(self) -> None:
        if self._last_score is None:
            self.complete_label.setText("织造完成 · 自由创作")
            self.status_label.setText("织造完成。")
        else:
            stars = "★" * self._last_score.stars + "☆" * (3 - self._last_score.stars)
            self.complete_label.setText(
                f"织造完成 · {stars} · {self._last_score.score:.1f}分"
            )
            self.status_label.setText(
                f"织造完成！匹配率 {self._last_score.match_ratio:.0%}，得分 {self._last_score.score:.1f}。"
            )

    def compile_current_pattern(self) -> WeavePlan:
        plan = self._compile_service.compile(self.canvas.grid)
        self._current_plan = plan
        self.weave_preview.set_plan(plan)
        self.complete_label.setText("")
        lines = [
            f"画布：{plan.warp_count} 列 × {plan.weft_count} 行",
            f"原始织造行：{plan.report.original_pick_count}",
            f"花本指令：{plan.report.unique_card_count}",
            f"压缩率：{plan.report.compression_ratio * 100:.1f}%",
        ]
        if self._level is not None and (plan.warp_count, plan.weft_count) == (self._level.width, self._level.height):
            result = self._score_engine.score(self.canvas.grid, self._level.target, plan.report.compression_ratio)
            self._last_score = result
            self.score_label.setText(f"得分 {result.score:.1f}")
            self.stars_label.setText("★" * result.stars + "☆" * (3 - result.stars))
            lines.extend(["", "关卡评分：", f"纹样匹配：{result.match_ratio:.1%}", f"错误单元：{result.wrong_cells}", f"本关目标：{self._level.name}"])
            self.status_label.setText(f"编译完成：{'★' * result.stars}{'☆' * (3 - result.stars)}，点击“开始织造”。")
        else:
            self._last_score = None
            self.score_label.setText("自由模式")
            self.stars_label.setText("自由创作")
            self.status_label.setText("编译完成：自由创作结果已就绪。")
        if plan.cards:
            lines.append("")
            lines.append("花本列表：")
            lines.extend(f"{card.card_id}：提升经线 {list(card.lifted_warp)}，出现 {card.occurrences} 次" for card in plan.cards)
        if plan.report.warnings:
            lines.append("")
            lines.append("警告：")
            lines.extend(plan.report.warnings)
        self.report_label.setText("\n".join(lines))
        self.progress_label.setText(f"织造 0/{plan.weft_count}")
        return plan

    def _update_report_placeholder(self, reason: str = "尚未编译") -> None:
        objective = "自由创作模式" if self._level is None else self._level.description
        self.report_label.setText(f"状态：{reason}\n目标：{objective}\n\n编译后显示纹样匹配率、错误单元和花本压缩奖励。")

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #0F172A; color: #E2E8F0; font-family: "Microsoft YaHei UI", "Microsoft YaHei"; font-size: 10.5pt; }
            QFrame#hudPanel { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #111827, stop:0.55 #1E293B, stop:1 #3F2A20); border: 1px solid #475569; border-radius: 12px; }
            QFrame#sidePanel, QFrame#stagePanel { background: #172033; border: 1px solid #334155; border-radius: 12px; }
            QLabel#panelTitle { color: #F8FAFC; font-size: 13pt; font-weight: 700; padding-bottom: 4px; }
            QLabel#levelTitle { color: #FBBF24; font-size: 16pt; font-weight: 800; }
            QLabel#objectiveText, QLabel#hintText, QLabel#statusText { color: #94A3B8; }
            QLabel#scoreText, QLabel#progressText, QLabel#starsText, QLabel#completeText { color: #FDE68A; font-weight: 700; }
            QPushButton { background: #1E293B; border: 1px solid #475569; border-radius: 8px; padding: 7px 10px; color: #E2E8F0; }
            QPushButton:hover { background: #334155; }
            QPushButton:checked { background: #243B6B; border-color: #60A5FA; color: #FFFFFF; }
            QPushButton#primaryButton { background: #B64B3E; border-color: #F87171; color: #FFFFFF; font-weight: 700; }
            QPushButton#primaryButton:hover { background: #DC5A4C; }
            QPushButton#goldButton { background: #B7791F; border-color: #F6C453; color: #FFFFFF; font-weight: 700; }
        """)