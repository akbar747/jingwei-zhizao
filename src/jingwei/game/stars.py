"""独立三星评级：形、技、速分别代表一项可追求的能力。

- 形（shape）：纹样匹配度，考察对传统纹样的忠实复现；
- 技（craft）：花本压缩率，考察对可编程提花指令的优化理解；
- 速（speed）：是否在订单时限内完成，考察匠人效率。

三颗星互相独立，因此同一件作品会有明确的重玩目标，而不是只看一个总分。
"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.models import PatternGrid

SHAPE_THRESHOLD = 0.98
CRAFT_THRESHOLD = 0.70
CRAFT_FLOOR = 0.60


@dataclass(frozen=True)
class StarResult:
    """一次三星评级的完整结果。"""

    match_ratio: float
    compression_ratio: float
    elapsed_seconds: float
    shape_star: bool
    craft_star: bool
    speed_star: bool
    score: float

    @property
    def stars(self) -> int:
        return int(self.shape_star) + int(self.craft_star) + int(self.speed_star)

    @property
    def stars_label(self) -> str:
        return "★" * self.stars + "☆" * (3 - self.stars)

    @property
    def skill_names(self) -> tuple[str, ...]:
        names: list[str] = []
        if self.shape_star:
            names.append("形")
        if self.craft_star:
            names.append("技")
        if self.speed_star:
            names.append("速")
        return tuple(names)


class StarEngine:
    """根据匹配度、压缩率和用时给出三颗独立星星。"""

    def evaluate(
        self,
        grid: PatternGrid,
        target: tuple[tuple[bool, ...], ...],
        *,
        compression_ratio: float = 0.0,
        elapsed_seconds: float = 0.0,
        time_limit_seconds: float | None = None,
        craft_threshold: float = CRAFT_THRESHOLD,
    ) -> StarResult:
        if not target:
            raise ValueError("目标纹样不能为空")

        target_height = len(target)
        target_width = len(target[0])
        if any(len(row) != target_width for row in target):
            raise ValueError("目标纹样每行长度必须一致")
        if grid.width != target_width or grid.height != target_height:
            raise ValueError("玩家画布尺寸与关卡目标不一致")
        if time_limit_seconds is not None and time_limit_seconds <= 0:
            raise ValueError("订单时限必须大于0")
        if elapsed_seconds < 0:
            raise ValueError("用时不能为负数")

        matched = 0
        total = target_width * target_height
        for row, target_row in enumerate(target):
            for column, expected in enumerate(target_row):
                if grid.get(column, row) == expected:
                    matched += 1

        match_ratio = matched / total if total else 0.0
        compression = max(0.0, min(1.0, float(compression_ratio)))
        minimum = max(CRAFT_FLOOR, float(craft_threshold))

        # 空画布直接零分，防止“什么都不画也拿压缩星”的漏洞。
        empty = grid.is_empty()
        shape_star = not empty and match_ratio >= SHAPE_THRESHOLD
        craft_star = not empty and compression >= minimum
        speed_star = not empty and (
            time_limit_seconds is None or elapsed_seconds <= time_limit_seconds
        )

        star_count = int(shape_star) + int(craft_star) + int(speed_star)
        score = round(
            70.0 * match_ratio
            + 20.0 * compression
            + 10.0 * (star_count / 3.0),
            1,
        )
        if empty:
            score = 0.0

        return StarResult(
            match_ratio=match_ratio,
            compression_ratio=compression,
            elapsed_seconds=float(elapsed_seconds),
            shape_star=shape_star,
            craft_star=craft_star,
            speed_star=speed_star,
            score=score,
        )