"""通关结算摘要：把评级结果翻译成可展示、可评测的结论。"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.game.stars import StarResult

_HEADLINES: dict[int, str] = {
    0: "从头再来",
    1: "再练一手",
    2: "匠心初成",
    3: "织造名匠",
}

_ENCOURAGEMENTS: dict[int, str] = {
    0: "先照目标画出轮廓，再点亮第一颗星。",
    1: "已点亮一颗星，试着提升匹配或压缩率。",
    2: "距满星只差一步，补上缺失的星章。",
    3: "形、技、速全部达成，这是一件可收藏的佳作。",
}


@dataclass(frozen=True)
class ResultSummary:
    """一次通关的展示摘要。"""

    level_name: str
    stars: int
    stars_label: str
    score: float
    match_ratio: float
    compression_ratio: float
    elapsed_seconds: float
    skill_line: str
    headline: str
    encouragement: str


def build_result_summary(level_name: str, result: StarResult) -> ResultSummary:
    """由三星评级构造通关摘要。"""

    skills = []
    if result.shape_star:
        skills.append("形")
    if result.craft_star:
        skills.append("技")
    if result.speed_star:
        skills.append("速")
    stars = result.stars
    return ResultSummary(
        level_name=level_name,
        stars=stars,
        stars_label=result.stars_label,
        score=result.score,
        match_ratio=result.match_ratio,
        compression_ratio=result.compression_ratio,
        elapsed_seconds=result.elapsed_seconds,
        skill_line=" · ".join(skills) if skills else "未获得星章",
        headline=_HEADLINES[stars],
        encouragement=_ENCOURAGEMENTS[stars],
    )