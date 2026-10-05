"""关卡评分：比较玩家纹样与目标纹样，并加入花本压缩奖励。"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.models import PatternGrid


@dataclass(frozen=True)
class ScoreResult:
    """一次关卡评分结果。"""

    score: float
    stars: int
    match_ratio: float
    compression_ratio: float
    wrong_cells: int


class ScoreEngine:
    """确定性地计算玩家纹样得分和星级。"""

    def score(
        self,
        grid: PatternGrid,
        target: tuple[tuple[bool, ...], ...],
        compression_ratio: float = 0.0,
    ) -> ScoreResult:
        if not target:
            raise ValueError("目标纹样不能为空")

        target_height = len(target)
        target_width = len(target[0])
        if any(len(row) != target_width for row in target):
            raise ValueError("目标纹样每行长度必须一致")
        if grid.width != target_width or grid.height != target_height:
            raise ValueError("玩家画布尺寸与关卡目标不一致")

        matched = 0
        total = target_width * target_height
        for row, target_row in enumerate(target):
            for column, expected in enumerate(target_row):
                if grid.get(column, row) == expected:
                    matched += 1

        match_ratio = matched / total if total else 0.0
        compression = max(0.0, min(1.0, float(compression_ratio)))
        score = round(70.0 * match_ratio + 30.0 * compression, 1)

        if grid.is_empty():
            stars = 0
        elif match_ratio >= 0.98:
            stars = 3
        elif match_ratio >= 0.80:
            stars = 2
        elif match_ratio >= 0.55:
            stars = 1
        else:
            stars = 0

        return ScoreResult(
            score=score,
            stars=stars,
            match_ratio=match_ratio,
            compression_ratio=compression,
            wrong_cells=total - matched,
        )
