"""民族文化纹样库：为关卡、收藏册与灵感生成提供统一的纹样来源。

纹样为教学用途的“程式化演绎”，用于课堂展示经纬交织与文化母题，
不宣称是任何具体文物或织片的逐格复刻。每条纹样都保留文化来源说明。
"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.game.levels import LevelDefinition

Matrix = tuple[tuple[bool, ...], ...]


@dataclass(frozen=True)
class Motif:
    """一件带文化出处的纹样。"""

    motif_id: str
    name: str
    ethnic_group: str
    motif_type: str
    cultural_note: str
    reference: str
    pattern: Matrix

    @property
    def size(self) -> int:
        return len(self.pattern)


def _frame(size: int) -> Matrix:
    return tuple(
        tuple(row in (0, size - 1) or column in (0, size - 1) for column in range(size))
        for row in range(size)
    )


def _diamond(size: int) -> Matrix:
    center = (size - 1) / 2
    radius = size // 2
    return tuple(
        tuple(abs(column - center) + abs(row - center) <= radius for column in range(size))
        for row in range(size)
    )


def _returning(size: int) -> Matrix:
    center = (size - 1) / 2
    radius = size // 2
    rows: list[tuple[bool, ...]] = []
    for row in range(size):
        values: list[bool] = []
        for column in range(size):
            border = row in (0, size - 1) or column in (0, size - 1)
            diamond = abs(column - center) + abs(row - center) <= radius - 2
            diagonal = abs(column - row) <= 1 or abs(column + row - (size - 1)) <= 1
            values.append(border or (diamond and diagonal))
        rows.append(tuple(values))
    return tuple(rows)


def _hook_pattern(size: int) -> Matrix:
    """西兰卡普勾纹：中央方框内嵌四向回勾，强调对称与块面。"""

    cells = [[False] * size for _ in range(size)]
    border = max(1, size // 10)
    for row in range(size):
        for column in range(size):
            if row < border or row >= size - border or column < border or column >= size - border:
                cells[row][column] = True
    margin = max(2, size // 5)
    inner_top, inner_bottom = margin, size - 1 - margin
    inner_left, inner_right = margin, size - 1 - margin
    if inner_bottom <= inner_top or inner_right <= inner_left:
        return tuple(tuple(row) for row in cells)
    for column in range(inner_left, inner_right + 1):
        cells[inner_top][column] = True
        cells[inner_bottom][column] = True
    for row in range(inner_top, inner_bottom + 1):
        cells[row][inner_left] = True
        cells[row][inner_right] = True
    mid_top = (inner_top + inner_bottom) // 2
    mid_left = (inner_left + inner_right) // 2
    hook = max(1, size // 10)
    for offset in range(1, hook + 1):
        cells[inner_top + offset][mid_left] = True
        cells[inner_bottom - offset][mid_left] = True
        cells[inner_top + offset][mid_left - 1] = True
        cells[inner_bottom - offset][mid_left - 1] = True
        cells[mid_top][inner_left + offset] = True
        cells[mid_top][inner_right - offset] = True
        cells[mid_top - 1][inner_left + offset] = True
        cells[mid_top - 1][inner_right - offset] = True
    return tuple(tuple(row) for row in cells)


def _wave_bands(size: int) -> Matrix:
    """壮锦水波纹：连续波浪带，象征江河与生生不息。"""

    cells = [[False] * size for _ in range(size)]
    bands = (size - 1) / 2
    for row in range(size):
        upper = row <= bands
        distance = row if upper else size - 1 - row
        for column in range(size):
            phase = (column + distance) % 6
            if phase in (0, 1):
                cells[row][column] = True
        if not upper:
            cells[row][0] = cells[row][size - 1] = True
    return tuple(tuple(row) for row in cells)


def _mountain_cloud(size: int) -> Matrix:
    """蜀锦云雷纹：同心菱框加四角回旋，形似层叠云气。"""

    cells = [[False] * size for _ in range(size)]
    center = (size - 1) / 2
    rings = (max(1, size // 6), max(2, size // 3))
    for row in range(size):
        for column in range(size):
            distance = abs(column - center) + abs(row - center)
            if any(abs(distance - ring) <= 0.5 for ring in rings):
                cells[row][column] = True
    hook = max(1, size // 8)
    corners = ((0, 0, 1, 1), (0, size - 1, 1, -1), (size - 1, 0, -1, 1), (size - 1, size - 1, -1, -1))
    for row, column, row_step, column_step in corners:
        for offset in range(hook):
            current_row = row + row_step * offset
            current_column = column + column_step * offset
            cells[current_row][current_column] = True
            if offset < hook:
                cells[current_row][column + column_step * hook] = True
                cells[row + row_step * hook][current_column] = True
    return tuple(tuple(row) for row in cells)


MOTIFS: tuple[Motif, ...] = (
    Motif(
        motif_id="M01",
        name="回纹边框",
        ethnic_group="中华传统纹样",
        motif_type="几何回纹",
        cultural_note=(
            "回纹源自新石器时代彩陶与商周青铜器的连续方折纹样，"
            "在中国传统织锦中常以边框形式出现，寓意绵延不绝。"
        ),
        reference="中国历代几何纹样通识；教学程式化演绎。",
        pattern=_frame(8),
    ),
    Motif(
        motif_id="M02",
        name="菱格锦",
        ethnic_group="土家/壮/蜀共享母题",
        motif_type="菱格几何",
        cultural_note=(
            "菱形几何纹是土家西兰卡普、壮锦与蜀锦共享的母题，"
            "通过经纬交织的对角结构形成稳定的视觉中心。"
        ),
        reference="土家西兰卡普、壮锦、蜀锦常见菱格母题；教学程式化演绎。",
        pattern=_diamond(12),
    ),
    Motif(
        motif_id="M03",
        name="万纹回环",
        ethnic_group="中华传统纹样",
        motif_type="回环菱格",
        cultural_note=(
            "多层回环纹样把边框、菱格与回纹叠加，体现了传统织造"
            "“以简驭繁”的构图智慧，也最适合展示花本压缩的威力。"
        ),
        reference="中国传统回纹与回环构图；教学程式化演绎。",
        pattern=_returning(16),
    ),
    Motif(
        motif_id="M04",
        name="勾纹锦",
        ethnic_group="土家族",
        motif_type="西兰卡普勾纹",
        cultural_note=(
            "西兰卡普以通经断纬、反面挑织著称，勾纹与块面色彩是其典型"
            "视觉语言，常以粗轮廓勾出对称的几何骨架。"
        ),
        reference="土家织锦（西兰卡普）勾纹母题；教学程式化演绎，非文物复刻。",
        pattern=_hook_pattern(16),
    ),
    Motif(
        motif_id="M05",
        name="水波纹",
        ethnic_group="壮族",
        motif_type="壮锦水波",
        cultural_note=(
            "壮锦常用连续波浪与几何骨架表现江河、田园与生生不息，"
            "纹样节奏均匀，适合用重复花本高效表达。"
        ),
        reference="壮族壮锦水波与几何骨架母题；教学程式化演绎，非文物复刻。",
        pattern=_wave_bands(16),
    ),
    Motif(
        motif_id="M06",
        name="云雷纹",
        ethnic_group="汉族（蜀锦）",
        motif_type="蜀锦云雷",
        cultural_note=(
            "蜀锦中的云雷纹以层叠山形和回旋云气构成秩序感，"
            "体现“天圆地方”的宇宙想象与织造者的秩序美学。"
        ),
        reference="蜀锦云雷/云气纹母题；教学程式化演绎，非文物复刻。",
        pattern=_mountain_cloud(16),
    ),
)

_BY_ID: dict[str, Motif] = {motif.motif_id: motif for motif in MOTIFS}


def get_motif(motif_id: str) -> Motif:
    """按编号读取纹样，未知编号抛出 KeyError。"""

    try:
        return _BY_ID[motif_id]
    except KeyError as error:
        raise KeyError(f"纹样库中没有编号 {motif_id}") from error


def build_campaign_levels() -> tuple[LevelDefinition, ...]:
    """把纹样库转换成循序渐进的关卡。"""

    levels: list[LevelDefinition] = []
    for index, motif in enumerate(MOTIFS):
        levels.append(
            LevelDefinition(
                level_id=f"L{index + 1:02d}",
                name=motif.name,
                description=f"织出{motif.ethnic_group}的{motif.motif_type}。",
                hint=motif.cultural_note,
                target=motif.pattern,
                par_seconds=90 + index * 20,
            )
        )
    return tuple(levels)