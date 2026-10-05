"""游戏关卡定义。"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.models import PatternGrid


@dataclass(frozen=True)
class LevelDefinition:
    """一个可玩的织造关卡。"""

    level_id: str
    name: str
    description: str
    hint: str
    target: tuple[tuple[bool, ...], ...]
    par_seconds: int = 120

    def __post_init__(self) -> None:
        if not self.target:
            raise ValueError("关卡目标不能为空")
        width = len(self.target[0])
        if width == 0 or any(len(row) != width for row in self.target):
            raise ValueError("关卡目标必须是矩形")
        if self.par_seconds <= 0:
            raise ValueError("目标用时必须大于0")

    @property
    def width(self) -> int:
        """目标纹样列数。"""
        return len(self.target[0])

    @property
    def height(self) -> int:
        """目标纹样行数。"""
        return len(self.target)

    def create_grid(self) -> PatternGrid:
        """创建与关卡目标一致的玩家画布。"""
        return PatternGrid(self.width, self.height, [list(row) for row in self.target])
