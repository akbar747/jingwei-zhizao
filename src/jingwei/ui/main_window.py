"""最小主窗口：承载点阵画布与花本编译报告。"""

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
from jingwei.ui.pattern_canvas import PatternCanvas


class MainWindow(QMainWindow):
    """MVP主窗口。

    当前只实现一条核心链路：绘制点阵、调用编译服务、显示花本统计。
    后续织造动画和导出功能会在保持本类职责清晰的前提下增加。
    """

    def __init__(
        self,
        grid: PatternGrid | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._grid = grid if grid is not None else PatternGrid(16, 16)
        self._compile_service = CompileService()
        self._current_plan: WeavePlan | None = None

        self.setWindowTitle("经纬智造 · 花楼提花机的可编程密码")
        self.setMinimumSize(1000, 680)

        self._build_ui()
        self._connect_signals()
        self._apply_style()

        self.status_label.setText("就绪：请绘制纹样，然后点击“编译花本”")
        self._update_report_placeholder()

    @property
    def current_plan(self) -> WeavePlan | None:
        """返回当前有效编译结果；尚未编译或已过期时为 None。"""
        return self._current_plan

    def _build_ui(self) -> None:
        """创建左侧工具区、中央画布和右侧编译报告。"""
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(16)

        self.canvas = PatternCanvas(self._grid)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        root_layout.addWidget(left_panel)
        root_layout.addWidget(self.canvas, stretch=1)
        root_layout.addWidget(right_panel)
        self.setCentralWidget(root)

    def _build_left_panel(self) -> QWidget:
        """创建绘图和编译操作区。"""
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setFixedWidth(190)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("操作")
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

        for button in (
            self.paint_button,
            self.erase_button,
            self.clear_button,
            self.compile_button,
        ):
            button.setMinimumHeight(38)
            layout.addWidget(button)

        layout.addStretch(1)

        tip = QLabel(
            "左键绘制，右键擦除。\n"
            "编译后，相同提升行会复用同一花本编号。"
        )
        tip.setWordWrap(True)
        tip.setObjectName("hintText")
        layout.addWidget(tip)
        return panel

    def _build_right_panel(self) -> QWidget:
        """创建编译报告和当前状态区域。"""
        panel = QFrame()
        panel.setObjectName("sidePanel")
        panel.setMinimumWidth(300)
        panel.setMaximumWidth(380)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("花本编译报告")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self.report_label = QLabel()
        self.report_label.setWordWrap(True)
        self.report_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.report_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.report_label)

        layout.addStretch(1)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("statusText")
        layout.addWidget(self.status_label)
        return panel

    def _connect_signals(self) -> None:
        """集中连接信号，便于后续替换为命令总线或撤销系统。"""
        self.paint_button.clicked.connect(self._activate_paint_mode)
        self.erase_button.clicked.connect(self._activate_erase_mode)
        self.clear_button.clicked.connect(self._clear_pattern)
        self.compile_button.clicked.connect(self.compile_current_pattern)
        self.canvas.patternChanged.connect(self._on_pattern_changed)

    def _activate_paint_mode(self) -> None:
        """切换到普通绘制模式。"""
        self.paint_button.setChecked(True)
        self.erase_button.setChecked(False)
        self.canvas.set_erase_mode(False)

    def _activate_erase_mode(self) -> None:
        """切换到橡皮模式。"""
        self.paint_button.setChecked(False)
        self.erase_button.setChecked(True)
        self.canvas.set_erase_mode(True)

    def _clear_pattern(self) -> None:
        """清空纹样，并使已有编译结果失效。"""
        self.canvas.grid.clear()
        self.canvas.update()
        self._current_plan = None
        self._update_report_placeholder("纹样已清空")
        self.status_label.setText("纹样已清空：请重新绘制并编译")

    def _on_pattern_changed(self) -> None:
        """纹样变化后标记旧的编译结果不可用。"""
        if self._current_plan is not None:
            self._current_plan = None
            self.status_label.setText("结果已过期：请重新点击“编译花本”")

    def compile_current_pattern(self) -> WeavePlan:
        """编译当前纹样，并把统计结果显示到右侧面板。"""
        plan = self._compile_service.compile(self.canvas.grid)
        self._current_plan = plan

        percent = plan.report.compression_ratio * 100
        lines = [
            f"画布：{plan.warp_count} 列 × {plan.weft_count} 行",
            f"原始织造行：{plan.report.original_pick_count}",
            f"花本指令：{plan.report.unique_card_count}",
            f"压缩率：{percent:.1f}%",
        ]

        if plan.cards:
            card_lines = [
                f"{card.card_id}：提升经线 {list(card.lifted_warp)}，"
                f"出现 {card.occurrences} 次"
                for card in plan.cards
            ]
            lines.append("")
            lines.append("花本列表：")
            lines.extend(card_lines)

        if plan.report.warnings:
            lines.append("")
            lines.append("警告：")
            lines.extend(plan.report.warnings)

        self.report_label.setText("\n".join(lines))
        if plan.report.warnings:
            self.status_label.setText("编译完成，但存在需要处理的警告")
        else:
            self.status_label.setText("编译完成：结果与当前纹样一致")
        return plan

    def _update_report_placeholder(self, reason: str = "尚未编译") -> None:
        """在没有有效结果时清空报告区域。"""
        grid = self.canvas.grid
        self.report_label.setText(
            f"原因：{reason}\n"
            f"当前画布：{grid.width} 列 × {grid.height} 行\n\n"
            "点击左侧“编译花本”后，此处将显示花本指令和统计信息。"
        )

    def _apply_style(self) -> None:
        """应用最小视觉规范，保证原型已经具备可展示的界面气质。"""
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #F7F1E3;
                color: #1D232A;
                font-family: "Microsoft YaHei UI", "Microsoft YaHei";
                font-size: 10.5pt;
            }
            QFrame#sidePanel {
                background: #FFFDF7;
                border: 1px solid #D8D2C4;
                border-radius: 10px;
            }
            QLabel#panelTitle {
                color: #243B6B;
                font-size: 13pt;
                font-weight: 700;
                padding-bottom: 4px;
            }
            QPushButton {
                background: #FFFFFF;
                border: 1px solid #BEB6A6;
                border-radius: 7px;
                padding: 7px 10px;
            }
            QPushButton:hover {
                background: #F2EADB;
            }
            QPushButton:checked {
                background: #243B6B;
                color: #FFFFFF;
                border-color: #243B6B;
            }
            QPushButton#primaryButton {
                background: #B64B3E;
                color: #FFFFFF;
                border-color: #B64B3E;
                font-weight: 700;
            }
            QPushButton#primaryButton:hover {
                background: #9F3E33;
            }
            QLabel#hintText, QLabel#statusText {
                color: #667085;
                font-size: 9.5pt;
            }
            """
        )
