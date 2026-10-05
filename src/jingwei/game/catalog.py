"""首版三个教学关卡。"""

from __future__ import annotations

from jingwei.game.levels import LevelDefinition


def _frame(size: int) -> tuple[tuple[bool, ...], ...]:
    return tuple(
        tuple(
            row in (0, size - 1) or column in (0, size - 1)
            for column in range(size)
        )
        for row in range(size)
    )


def _diamond(size: int) -> tuple[tuple[bool, ...], ...]:
    center = (size - 1) / 2
    radius = size // 2
    return tuple(
        tuple(
            abs(column - center) + abs(row - center) <= radius
            for column in range(size)
        )
        for row in range(size)
    )


def _returning_pattern(size: int) -> tuple[tuple[bool, ...], ...]:
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


LEVELS: tuple[LevelDefinition, ...] = (
    LevelDefinition(
        level_id="L01",
        name="第一根经线",
        description="织出闭合回纹，认识经线提升与基础开口。",
        hint="重复的回纹行会共用同一张花本，先观察边框再编译。",
        target=_frame(8),
        par_seconds=90,
    ),
    LevelDefinition(
        level_id="L02",
        name="菱纹锦",
        description="织出完整菱纹，体验对称纹样和花本压缩。",
        hint="菱纹上下对称，很多提升行会自动合并成同一指令。",
        target=_diamond(12),
        par_seconds=120,
    ),
    LevelDefinition(
        level_id="L03",
        name="万纹回环",
        description="完成外框、内菱和回环纹交织的挑战作品。",
        hint="先保证外框完整，再处理内部回环结构。",
        target=_returning_pattern(16),
        par_seconds=150,
    ),
)


def get_level(index: int) -> LevelDefinition:
    """按索引读取关卡，越界时抛出清晰错误。"""
    if index < 0 or index >= len(LEVELS):
        raise IndexError(f"关卡索引越界: {index}")
    return LEVELS[index]
