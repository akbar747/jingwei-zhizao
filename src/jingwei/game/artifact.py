"""把完成的作品渲染成可导出的织锦作品卡（PNG）。

作品卡既是收藏册里的展示单元，也是可以直接放进竞赛答辩材料的成品图。
渲染只依赖 Qt 的离屏绘图能力，不访问网络、不依赖外部图片素材。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPen

from jingwei.game.levels import LevelDefinition
from jingwei.game.orders import OrderModifier
from jingwei.game.stars import StarResult

CARD_WIDTH = 720
CARD_HEIGHT = 1040

_PAPER = QColor("#F4E8CE")
_PAPER_DARK = QColor("#E7D6B4")
_INK = QColor("#1F2933")
_WARP = QColor("#8C1D2B")
_WEFT = QColor("#E9DCC3")
_GOLD = QColor("#C8952E")
_BG_TOP = QColor("#14203A")
_BG_BOTTOM = QColor("#2A1A1E")


@dataclass(frozen=True)
class ArtifactCard:
    """一张作品卡的完整可序列化数据。"""

    title: str
    motif: str
    cultural_note: str
    score: float
    stars: int
    shape_star: bool
    craft_star: bool
    speed_star: bool
    compression_ratio: float
    match_ratio: float
    order_name: str
    woven_at: str
    cells: tuple[tuple[bool, ...], ...]

    @property
    def stars_label(self) -> str:
        return "★" * self.stars + "☆" * (3 - self.stars)

    @property
    def skill_line(self) -> str:
        skills = []
        if self.shape_star:
            skills.append("形")
        if self.craft_star:
            skills.append("技")
        if self.speed_star:
            skills.append("速")
        return " · ".join(skills) if skills else "未获得星章"


def build_artifact(
    level: LevelDefinition,
    stars: StarResult,
    *,
    modifier: OrderModifier = OrderModifier.FREE,
    woven_at: str = "",
) -> ArtifactCard:
    """把关卡、评级和织物矩阵组装为作品卡数据。"""

    return ArtifactCard(
        title=level.name,
        motif=level.description,
        cultural_note=level.hint,
        score=stars.score,
        stars=stars.stars,
        shape_star=stars.shape_star,
        craft_star=stars.craft_star,
        speed_star=stars.speed_star,
        compression_ratio=stars.compression_ratio,
        match_ratio=stars.match_ratio,
        order_name=modifier.display_name,
        woven_at=woven_at,
        cells=tuple(tuple(row) for row in level.target),
    )


def _font(size: int, *, bold: bool = False) -> QFont:
    font = QFont()
    font.setFamilies(["Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans CJK SC", "SimHei"])
    font.setPointSize(size)
    font.setBold(bold)
    return font


def _draw_weave(painter: QPainter, rect: QRectF, cells: tuple[tuple[bool, ...], ...]) -> None:
    if not cells or not cells[0]:
        painter.fillRect(rect, _PAPER)
        return

    warp_count = len(cells[0])
    weft_count = len(cells)
    painter.save()
    painter.setClipRect(rect)
    painter.fillRect(rect, _WEFT)
    cell_width = rect.width() / warp_count
    cell_height = rect.height() / weft_count

    # 经线底纹：先铺一层竖向红线，再用纬线格覆盖未提升的位置。
    warp_pen = QPen(_WARP)
    warp_pen.setWidthF(max(1.0, cell_width * 0.55))
    painter.setPen(warp_pen)
    for column in range(warp_count):
        x = rect.left() + (column + 0.5) * cell_width
        painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))

    painter.setPen(Qt.NoPen)
    for row, row_cells in enumerate(cells):
        top = rect.top() + row * cell_height
        for column, lifted in enumerate(row_cells):
            if lifted:
                continue
            left = rect.left() + column * cell_width
            painter.fillRect(
                QRectF(left, top, cell_width, cell_height),
                _WEFT,
            )
    painter.setPen(QPen(QColor(140, 120, 90, 90), 1))
    painter.drawRect(rect)
    painter.restore()


def render_artifact_to_image(
    card: ArtifactCard,
    *,
    width: int = CARD_WIDTH,
    height: int = CARD_HEIGHT,
) -> QImage:
    """离屏渲染作品卡，返回 QImage，便于保存或测试。"""

    if width <= 0 or height <= 0:
        raise ValueError("作品卡尺寸必须大于0")

    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)

    background = QLinearGradient(0, 0, 0, height)
    background.setColorAt(0.0, _BG_TOP)
    background.setColorAt(1.0, _BG_BOTTOM)
    painter.fillRect(QRectF(0, 0, width, height), background)

    margin = width * 0.06
    painter.setPen(QPen(_GOLD, 2))
    painter.drawRoundedRect(QRectF(margin / 2, margin / 2, width - margin, height - margin), 18, 18)

    painter.setFont(_font(max(16, width // 28), bold=True))
    painter.setPen(_GOLD)
    painter.drawText(
        QRectF(margin, margin * 0.6, width - margin * 2, 40),
        Qt.AlignLeft | Qt.AlignVCenter,
        "经纬智造 · 数字织锦作品卡",
    )

    painter.setFont(_font(max(26, width // 16), bold=True))
    painter.setPen(QColor("#F8FAFC"))
    painter.drawText(
        QRectF(margin, margin * 0.6 + 48, width - margin * 2, 68),
        Qt.AlignLeft | Qt.AlignVCenter,
        card.title,
    )

    painter.setFont(_font(max(13, width // 38)))
    painter.setPen(QColor("#CBD5E1"))
    woven = card.woven_at or "未知时间"
    painter.drawText(
        QRectF(margin, margin * 0.6 + 116, width - margin * 2, 36),
        Qt.AlignLeft | Qt.AlignVCenter,
        card.order_name + "   ·   织成于 " + woven,
    )

    weave_top = margin * 0.6 + 168
    weave_size = width - margin * 2
    weave_rect = QRectF(margin, weave_top, weave_size, weave_size)
    _draw_weave(painter, weave_rect, card.cells)

    info_top = weave_rect.bottom() + margin * 0.5
    painter.setFont(_font(max(22, width // 20), bold=True))
    painter.setPen(_GOLD)
    painter.drawText(
        QRectF(margin, info_top, width - margin * 2, 50),
        Qt.AlignLeft | Qt.AlignVCenter,
        f"{card.stars_label}   {card.score:.1f} 分",
    )

    painter.setFont(_font(max(13, width // 38)))
    painter.setPen(QColor("#E2E8F0"))
    detail = (
        f"纹样匹配 {card.match_ratio:.0%}   ·   "
        f"花本压缩 {card.compression_ratio:.0%}   ·   星章 {card.skill_line}"
    )
    painter.drawText(
        QRectF(margin, info_top + 48, width - margin * 2, 32),
        Qt.AlignLeft | Qt.AlignVCenter,
        detail,
    )

    painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
    painter.drawLine(
        int(margin),
        int(info_top + 92),
        int(width - margin),
        int(info_top + 92),
    )

    painter.setFont(_font(max(12, width // 42)))
    painter.setPen(QColor("#94A3B8"))
    painter.drawText(
        QRectF(margin, info_top + 100, width - margin * 2, height - info_top - margin * 2),
        Qt.TextWordWrap | Qt.AlignTop,
        card.motif,
    )

    painter.end()
    return image


def save_artifact_png(card: ArtifactCard, path: Path | str) -> Path:
    """把作品卡保存为 PNG，返回实际写入路径。"""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    image = render_artifact_to_image(card)
    if not image.save(str(target), "PNG"):
        raise OSError(f"无法写入作品卡: {target}")
    return target