"""关卡目录：由民族文化纹样库统一生成。

纹样的绘制函数、文化说明与关卡参数都集中在 ``jingwei.game.motifs``，
避免关卡、收藏册和展示文案三处各写一份导致漂移。
"""

from __future__ import annotations

from jingwei.game.levels import LevelDefinition
from jingwei.game.motifs import MOTIFS, build_campaign_levels

LEVELS: tuple[LevelDefinition, ...] = build_campaign_levels()

__all__ = ["LEVELS", "MOTIFS", "get_level"]


def get_level(index: int) -> LevelDefinition:
    """按索引读取关卡，越界时抛出清晰错误。"""

    if index < 0 or index >= len(LEVELS):
        raise IndexError(f"关卡索引越界: {index}")
    return LEVELS[index]