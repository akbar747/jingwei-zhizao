"""纹样收藏册：把每个关卡的目标纹样整理成可收藏的文化条目。"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.models import PatternGrid
from jingwei.game.catalog import LEVELS
from jingwei.game.levels import LevelDefinition
from jingwei.game.progress import ProgressStore


@dataclass(frozen=True)
class AlbumEntry:
    """收藏册中的一个纹样条目。"""

    level_id: str
    title: str
    motif: str
    cultural_note: str
    level: LevelDefinition

    def create_grid(self) -> PatternGrid:
        """返回该纹样的可绘制副本。"""

        return self.level.create_grid()


@dataclass(frozen=True)
class AlbumSummary:
    """收藏册条目的展示状态。"""

    level_id: str
    title: str
    motif: str
    cultural_note: str
    unlocked: bool
    stars: int | None
    best_score: float | None
    target: tuple[tuple[bool, ...], ...]


def _entry(
    level_index: int,
    *,
    title: str,
    motif: str,
    cultural_note: str,
) -> AlbumEntry:
    level = LEVELS[level_index]
    return AlbumEntry(
        level_id=level.level_id,
        title=title,
        motif=motif,
        cultural_note=cultural_note,
        level=level,
    )


ALBUM: tuple[AlbumEntry, ...] = (
    _entry(
        0,
        title="第一根经线",
        motif="闭合回纹",
        cultural_note=(
            "回纹源自新石器时代彩陶与商周青铜器的连续方折纹样，"
            "在中国传统织锦中常以边框形式出现，寓意绵延不绝。"
        ),
    ),
    _entry(
        1,
        title="菱纹锦",
        motif="菱格纹",
        cultural_note=(
            "菱形几何纹是土家西兰卡普、壮锦与蜀锦共享的母题，"
            "通过经纬交织的对角结构形成稳定的视觉中心。"
        ),
    ),
    _entry(
        2,
        title="万纹回环",
        motif="回环菱格",
        cultural_note=(
            "多层回环纹样把边框、菱格与回纹叠加，体现了传统织造"
            "“以简驭繁”的构图智慧，也最适合展示花本压缩的威力。"
        ),
    ),
)

_BY_LEVEL_ID: dict[str, AlbumEntry] = {entry.level_id: entry for entry in ALBUM}


def get_album_entry(level_id: str) -> AlbumEntry:
    """按关卡编号读取收藏条目，未知编号抛出 KeyError。"""

    try:
        return _BY_LEVEL_ID[level_id]
    except KeyError as error:
        raise KeyError(f"收藏册中没有关卡 {level_id}") from error


def build_album_summaries(progress: ProgressStore) -> tuple[AlbumSummary, ...]:
    """结合进度生成收藏册展示状态。"""

    summaries: list[AlbumSummary] = []
    for index, entry in enumerate(ALBUM):
        record = progress.get(entry.level_id)
        summaries.append(
            AlbumSummary(
                level_id=entry.level_id,
                title=entry.title,
                motif=entry.motif,
                cultural_note=entry.cultural_note,
                unlocked=progress.is_level_unlocked(index),
                stars=None if record is None else record.stars,
                best_score=None if record is None else record.best_score,
                target=entry.level.target,
            )
        )
    return tuple(summaries)