"""游戏化主窗口：关卡、订单、三星评级、绘图与逐梭织造。"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from jingwei.application.compile_service import CompileService
from jingwei.domain.compiler import WeavePlan
from jingwei.domain.models import PatternGrid
from jingwei.game.album import get_album_entry
from jingwei.game.artifact import build_artifact, save_artifact_png
from jingwei.game.catalog import LEVELS, get_level
from jingwei.game.challenge import ChallengeClock, ChallengeSnapshot
from jingwei.game.feedback import calculate_compile_combo
from jingwei.game.levels import LevelDefinition
from jingwei.game.orders import OrderModifier, OrderSettings, apply_modifier, choose_modifier
from jingwei.game.progress import ProgressStore
from jingwei.game.stars import StarEngine, StarResult
from jingwei.ui.album_dialog import WeavingAlbumDialog
from jingwei.ui.pattern_canvas import PatternCanvas
from jingwei.ui.sound_player import SoundPlayer
from jingwei.ui.weave_preview import WeavePreview


class MainWindow(QMainWindow):
    """织造工坊主窗口。"""

    def __init__(
        self,
        grid: PatternGrid | None = None,
        parent: QWidget | None = None,
        level_index: int = 0,
        *,
        progress: ProgressStore | None = None,
        modifier: OrderModifier | None = None,
    ) -> None:
        super().__init__(parent)
        self._compile_service = CompileService()
        self._star_engine = StarEngine()
        self._sound = SoundPlayer()
        self._progress = progress if progress is not None else ProgressStore()
        self._challenge_clock: ChallengeClock | None = None
        self._challenge_timer = QTimer(self)
        self._challenge_timer.setInterval(1000)
        self._challenge_timer.timeout.connect(self._on_challenge_tick)
        self._target_preview_timer = QTimer(self)
        self._target_preview_timer.setSingleShot(True)
        self._target_preview_timer.timeout.connect(self._hide_target_for_memory_order)
        self._current_plan: WeavePlan | None = None
        self._last_star_result: StarResult | None = None
        self._finished_recorded = False
        self._free_mode = grid is not None
        self._level_index = None if self._free_mode else level_index
        self._level: LevelDefinition | None = None if self._free_mode else get_level(level_index)
        self._grid = grid if grid is not None else (None if self._level is None else self._level.create_blank_grid())
        self._order = apply_modifier(
            self._level.par_seconds if self._level is not None else 120,
            modifier if modifier is not None else (OrderModifier.FREE if self._free_mode else choose_modifier()),
        )

        self.setWindowTitle("经纬智造 · 织造工坊")
        self.setMinimumSize(1220, 860)

        self._build_ui()
        self._connect_signals()
        self._apply_style()
        self._refresh_hud()
        self._refresh_level_bar()
        self._update_report_placeholder()
        self._start_target_preview_if_needed()

    @property
    def current_plan(self) -> WeavePlan | None:
        return self._current_plan

    @property
    def level(self) -> LevelDefinition | None:
        return self._level

    @property
    def progress(self) -> ProgressStore:
        return self._progress

    @property
    def order(self) -> OrderSettings:
        return self._order

    @property
    def last_star_result(self) -> StarResult | None:
        return self._last_star_result

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
        layout.setSpacing(16)
        self.level_label = QLabel()
        self.level_label.setObjectName("levelTitle")
        self.order_label = QLabel()
        self.order_label.setObjectName("orderText")
        self.objective_label = QLabel()
        self.objective_label.setObjectName("objectiveText")
        self.objective_label.setWordWrap(True)
        self.score_label = QLabel()
        self.score_label.setObjectName("scoreText")
        self.stars_label = QLabel()
        self.stars_label.setObjectName("starsText")
        self.ability_label = QLabel("")
        self.ability_label.setObjectName("abilityText")
        self.time_label = QLabel()
        self.time_label.setObjectName("timeText")
        self.combo_label = QLabel("")
        self.combo_label.setObjectName("comboText")
        self.progress_label = QLabel()
        self.progress_label.setObjectName("progressText")
        layout.addWidget(self.level_label)
        layout.addWidget(self.order_label)
        layout.addWidget(self.objective_label, stretch=1)
        layout.addWidget(self.time_label)
        layout.addWidget(self.combo_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.ability_label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.stars_label)
        return hud

    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setFixedWidth(210)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(9)
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
            button.setMinimumHeight(36)
            layout.addWidget(button)

        layout.addSpacing(6)
        level_title = QLabel("织造关卡")
        level_title.setObjectName("panelTitle")
        layout.addWidget(level_title)
        self.level_bar = QGridLayout()
        self.level_bar.setSpacing(6)
        self.level_buttons: list[QPushButton] = []
        for index, level in enumerate(LEVELS):
            button = QPushButton(f"{index + 1}. {level.name}\n☆☆☆")
            button.setObjectName("levelButton")
            button.setMinimumHeight(46)
            button.clicked.connect(lambda _=False, i=index: self.load_level(i))
            self.level_bar.addWidget(button, index // 2, index % 2)
            self.level_buttons.append(button)
        layout.addLayout(self.level_bar)

        layout.addSpacing(6)
        self.album_button = QPushButton("纹样收藏册")
        self.album_button.setObjectName("goldButton")
        self.album_button.setMinimumHeight(38)
        layout.addWidget(self.album_button)
        self.export_button = QPushButton("导出当前作品卡")
        self.export_button.setMinimumHeight(36)
        layout.addWidget(self.export_button)
        layout.addStretch(1)

        tip = QLabel("左键绘制，右键擦除。\n三星 = 形（匹配）+ 技（压缩）+ 速（限时）。")
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
        self.canvas = PatternCanvas(self._grid if self._grid is not None else PatternGrid(2, 2))
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(title)
        layout.addWidget(self.canvas, stretch=1)
        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setMinimumWidth(300)
        panel.setMaximumWidth(380)
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
            self.target_canvas.set_grid(self._level.create_solution_grid())
        else:
            self.target_canvas.setVisible(False)
        self.order_hint_label = QLabel()
        self.order_hint_label.setObjectName("orderHint")
        self.order_hint_label.setWordWrap(True)
        layout.addWidget(self.order_hint_label)
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
        self.album_button.clicked.connect(self.show_album)
        self.export_button.clicked.connect(self.export_current_artifact)
        self.canvas.patternChanged.connect(self._on_pattern_changed)
        self.weave_preview.pickAdvanced.connect(self._on_pick_advanced)
        self.weave_preview.weavingFinished.connect(self._on_weaving_finished)

    # ---------- 订单与倒计时 ----------

    @staticmethod
    def _format_time(seconds: float) -> str:
        total = max(0, int(seconds + 0.999))
        return f"{total // 60:02d}:{total % 60:02d}"

    def apply_order(self, modifier: OrderModifier) -> OrderSettings:
        """切换订单修饰，刷新时限、门槛与提示文案。"""

        base = self._level.par_seconds if self._level is not None else 120
        self._order = apply_modifier(base, modifier)
        self.order_label.setText(self._order.modifier.display_name)
        self.order_hint_label.setText(self._order.modifier.rule_text)
        self._reset_challenge_clock()
        self._start_target_preview_if_needed()
        self._refresh_level_bar()
        return self._order

    def _reset_challenge_clock(self) -> None:
        self._challenge_timer.stop()
        if self._level is None:
            self._challenge_clock = None
            self.time_label.setText("自由模式")
            return
        self._challenge_clock = ChallengeClock(self._order.time_limit_seconds)
        self.time_label.setText(f"订单 {self._format_time(self._challenge_clock.remaining_seconds)}")

    def tick_challenge(self, seconds: float = 1.0) -> ChallengeSnapshot | None:
        if self._challenge_clock is None:
            return None
        snapshot = self._challenge_clock.tick(seconds)
        self.time_label.setText(f"订单 {self._format_time(snapshot.remaining_seconds)}")
        if snapshot.expired:
            self._challenge_timer.stop()
            self.weave_preview.stop_animation()
            self.status_label.setText("订单超时：点击“重织”后再试")
        return snapshot

    def _on_challenge_tick(self) -> None:
        self.tick_challenge(1.0)

    def _start_target_preview_if_needed(self) -> None:
        self._target_preview_timer.stop()
        if self._level is None or self._order.preview_seconds <= 0:
            self.target_canvas.setVisible(self._level is not None)
            return
        self.target_canvas.setVisible(True)
        self._target_preview_timer.start(int(self._order.preview_seconds * 1000))

    def _hide_target_for_memory_order(self) -> None:
        if self._level is not None and self._order.hidden_target:
            self.target_canvas.setVisible(False)
            self.status_label.setText("记忆订单：目标已隐藏，凭记忆完成纹样。")

    # ---------- 绘图与编译 ----------

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
        self._last_star_result = None
        self._finished_recorded = False
        self.weave_preview.set_plan(None)
        self.complete_label.setText("")
        self.combo_label.setText("")
        self._reset_challenge_clock()
        self.progress_label.setText(f"织造 0/{self.canvas.grid.height}")
        self._reset_score_display()
        self.status_label.setText(status)

    def _reset_score_display(self) -> None:
        if self._level is None:
            self.score_label.setText("自由模式")
            self.stars_label.setText("自由创作")
            self.ability_label.setText("")
        else:
            self.score_label.setText("得分 0.0")
            self.stars_label.setText("☆☆☆")
            self.ability_label.setText("形 技 速")

    def _refresh_hud(self) -> None:
        if self._level is None:
            self.level_label.setText("自由织造 · 无目标")
            self.objective_label.setText("自由创作模式：体验花本编译和逐梭织造。")
        else:
            self.level_label.setText(f"第{self._level_index + 1}关 · {self._level.name}")
            self.objective_label.setText(self._level.description)
        self.order_label.setText(self._order.modifier.display_name)
        self.order_hint_label.setText(self._order.modifier.rule_text)
        self.progress_label.setText(f"织造 0/{self.canvas.grid.height}")
        self._reset_score_display()
        self._reset_challenge_clock()

    def _refresh_level_bar(self) -> None:
        for index, button in enumerate(self.level_buttons):
            level_id = LEVELS[index].level_id
            record = self._progress.get(level_id)
            stars = "★" * (record.stars if record else 0) + "☆" * (3 - (record.stars if record else 0))
            unlocked = self._progress.is_level_unlocked(index)
            marker = "" if unlocked else "🔒"
            button.setText(f"{index + 1}. {LEVELS[index].name} {marker}\n{stars}")
            button.setEnabled(unlocked)
            button.setProperty("current", index == self._level_index)

    def load_level(self, index: int) -> LevelDefinition:
        level = get_level(index)
        if not self._progress.is_level_unlocked(index):
            self.status_label.setText("该关卡尚未解锁：请先完成上一件作品。")
            return level
        self._free_mode = False
        self._level_index = index
        self._level = level
        self._grid = level.create_blank_grid()
        self.canvas.set_grid(self._grid)
        self.target_canvas.setVisible(True)
        self.target_canvas.set_grid(level.create_solution_grid())
        self._current_plan = None
        self._last_star_result = None
        self._finished_recorded = False
        self.weave_preview.set_plan(None)
        self.complete_label.setText("")
        self.combo_label.setText("")
        self._order = apply_modifier(level.par_seconds, choose_modifier())
        self._refresh_hud()
        self._refresh_level_bar()
        self._update_report_placeholder("新关卡已载入")
        self.status_label.setText(f"{self._order.modifier.rule_text} {level.hint}")
        self._start_target_preview_if_needed()
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
        if self._level is not None and (self._challenge_clock is None or self._challenge_clock.expired):
            self._reset_challenge_clock()
        if self._level is not None:
            self._challenge_timer.start()
        self.weave_preview.start_animation()
        self.status_label.setText("织造中：赶在订单超时前完成作品。")

    def _step_weaving(self) -> None:
        if self._current_plan is None:
            self.compile_current_pattern()
        if self._current_plan is None or not self._current_plan.picks:
            self.status_label.setText("织造失败：请先绘制并编译有效纹样。")
            return
        self.weave_preview.advance_one_pick()

    def _reset_weaving(self) -> None:
        self._finished_recorded = False
        self._reset_challenge_clock()
        self.weave_preview.reset()
        self.progress_label.setText(f"织造 0/{self.weave_preview.total_picks}")
        self.status_label.setText("织造已重置，可以重新播放。")

    def _on_pick_advanced(self, completed: int) -> None:
        self._sound.play_shuttle()
        self.progress_label.setText(f"织造 {completed}/{self.weave_preview.total_picks}")

    def _on_weaving_finished(self) -> None:
        self._challenge_timer.stop()
        self._sound.play_success()
        if self._level is None or self._last_star_result is None:
            self.complete_label.setText("织造完成 · 自由创作")
            self.status_label.setText("织造完成。")
            return

        result = self._last_star_result
        elapsed = self._challenge_clock.duration_seconds - self._challenge_clock.remaining_seconds if self._challenge_clock else 0.0
        if not self._finished_recorded:
            self._finished_recorded = True
            self._progress.record(
                self._level.level_id,
                stars=result.stars,
                score=result.score,
                completed_at=elapsed,
                match_ratio=result.match_ratio,
                compression_ratio=result.compression_ratio,
                shape_star=result.shape_star,
                craft_star=result.craft_star,
                speed_star=result.speed_star,
            )
            self._progress.save()
            self._refresh_level_bar()
        self.complete_label.setText(
            f"织造完成 · {result.stars_label} · {result.score:.1f}分\n"
            f"形 {'✓' if result.shape_star else '×'}   技 {'✓' if result.craft_star else '×'}   速 {'✓' if result.speed_star else '×'}"
        )
        self.status_label.setText(
            f"织造完成！匹配率 {result.match_ratio:.0%}，"
            f"花本压缩 {result.compression_ratio:.0%}，本关最佳星级已保存。"
        )

    def compile_current_pattern(self) -> WeavePlan:
        plan = self._compile_service.compile(self.canvas.grid)
        self._current_plan = plan
        self._finished_recorded = False
        self.weave_preview.set_plan(plan)
        self.complete_label.setText("")
        combo = calculate_compile_combo(plan)
        self.combo_label.setText(combo.message)
        self._sound.play_compile()
        lines = [
            f"画布：{plan.warp_count} 列 × {plan.weft_count} 行",
            f"原始织造行：{plan.report.original_pick_count}",
            f"花本指令：{plan.report.unique_card_count}",
            f"压缩率：{plan.report.compression_ratio * 100:.1f}%",
        ]
        if self._level is not None and (plan.warp_count, plan.weft_count) == (self._level.width, self._level.height):
            elapsed = 0.0
            if self._challenge_clock is not None:
                elapsed = self._challenge_clock.duration_seconds - self._challenge_clock.remaining_seconds
            result = self._star_engine.evaluate(
                self.canvas.grid,
                self._level.target,
                compression_ratio=plan.report.compression_ratio,
                elapsed_seconds=elapsed,
                time_limit_seconds=self._order.time_limit_seconds,
                craft_threshold=self._order.minimum_compression,
            )
            self._last_star_result = result
            self.score_label.setText(f"得分 {result.score:.1f}")
            self.stars_label.setText(result.stars_label)
            self.ability_label.setText(
                f"形 {'✓' if result.shape_star else '×'} "
                f"技 {'✓' if result.craft_star else '×'} "
                f"速 {'✓' if result.speed_star else '×'}"
            )
            lines.extend(
                [
                    "",
                    "三星评级：",
                    f"★ 形 {'达成' if result.shape_star else '未达成'}（匹配 {result.match_ratio:.1%}）",
                    f"★ 技 {'达成' if result.craft_star else '未达成'}（压缩 ≥ {self._order.minimum_compression:.0%}）",
                    f"★ 速 {'达成' if result.speed_star else '未达成'}（订单 {self._format_time(self._order.time_limit_seconds)}）",
                    f"订单：{self._order.modifier.display_name}",
                ]
            )
            if not self._order.hides_match_hint:
                lines.append(f"错误单元：{int(round((1 - result.match_ratio) * plan.warp_count * plan.weft_count))}")
            self.status_label.setText(
                f"编译完成：{result.stars_label}，点击“开始织造”逐梭成布。"
            )
        else:
            self._last_star_result = None
            self.score_label.setText("自由模式")
            self.stars_label.setText("自由创作")
            self.ability_label.setText("")
            self.status_label.setText("编译完成：自由创作结果已就绪。")
        if plan.cards:
            lines.append("")
            lines.append("花本列表：")
            lines.extend(f"{card.card_id}：提升经线 {list(card.lifted_warp)}，出现 {card.occurrences} 次" for card in plan.cards)
        if plan.report.warnings:
            lines.append("")
            lines.append("警告：")
            lines.extend(plan.report.warnings)
        if self._order.hides_match_hint:
            lines.append("")
            lines.append("盲织订单：实时匹配提示已隐藏。")
        self.report_label.setText("\n".join(lines))
        self.progress_label.setText(f"织造 0/{plan.weft_count}")
        return plan

    def _update_report_placeholder(self, reason: str = "尚未编译") -> None:
        objective = "自由创作模式" if self._level is None else self._level.description
        self.report_label.setText(
            f"状态：{reason}\n目标：{objective}\n\n"
            "编译后显示三星评级：形（匹配度）、技（花本压缩）、速（订单时限）。"
        )

    # ---------- 收藏与导出 ----------

    def show_album(self) -> None:
        dialog = WeavingAlbumDialog(self._progress, self._level_lookup, self)
        dialog.exec()
        self._refresh_level_bar()

    def export_current_artifact(self) -> None:
        if self._level is None or self._last_star_result is None:
            QMessageBox.information(self, "导出作品卡", "请先编译并完成一件关卡作品。")
            return
        card = build_artifact(
            self._level,
            self._last_star_result,
            modifier=self._order.modifier,
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            "导出织锦作品卡",
            f"{self._level.name}-作品卡.png",
            "PNG 图片 (*.png)",
        )
        if path:
            save_artifact_png(card, path)

    @staticmethod
    def _level_id_lookup(level_id: str) -> LevelDefinition:
        return get_album_entry(level_id).level

    def _level_lookup(self, level_id: str) -> LevelDefinition:
        return self._level_id_lookup(level_id)

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #0F172A; color: #E2E8F0; font-family: "Microsoft YaHei UI", "Microsoft YaHei"; font-size: 10.5pt; }
            QFrame#hudPanel { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #111827, stop:0.55 #1E293B, stop:1 #3F2A20); border: 1px solid #475569; border-radius: 12px; }
            QFrame#sidePanel, QFrame#stagePanel { background: #172033; border: 1px solid #334155; border-radius: 12px; }
            QLabel#panelTitle { color: #F8FAFC; font-size: 13pt; font-weight: 700; padding-bottom: 4px; }
            QLabel#levelTitle { color: #FBBF24; font-size: 16pt; font-weight: 800; }
            QLabel#orderText { color: #F472B6; font-weight: 800; }
            QLabel#objectiveText, QLabel#hintText, QLabel#statusText, QLabel#orderHint { color: #94A3B8; }
            QLabel#scoreText, QLabel#progressText, QLabel#starsText, QLabel#completeText { color: #FDE68A; font-weight: 700; }
            QLabel#abilityText { color: #7DD3FC; font-weight: 700; }
            QLabel#comboText { color: #F472B6; font-weight: 800; }
            QLabel#timeText { color: #93C5FD; font-weight: 800; }
            QPushButton { background: #1E293B; border: 1px solid #475569; border-radius: 8px; padding: 7px 10px; color: #E2E8F0; }
            QPushButton:hover { background: #334155; }
            QPushButton:checked { background: #243B6B; border-color: #60A5FA; color: #FFFFFF; }
            QPushButton:disabled { color: #64748B; border-color: #334155; }
            QPushButton#primaryButton { background: #B64B3E; border-color: #F87171; color: #FFFFFF; font-weight: 700; }
            QPushButton#primaryButton:hover { background: #DC5A4C; }
            QPushButton#goldButton { background: #B7791F; border-color: #F6C453; color: #FFFFFF; font-weight: 700; }
            QPushButton#levelButton { text-align: left; padding: 6px 8px; }
        """)