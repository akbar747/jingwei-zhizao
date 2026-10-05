"""纹样收藏册：从民族文化纹样库生成可收藏条目。"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.models import PatternGrid
from jingwei.game.catalog import LEVELS
from jingwei.game.levels import LevelDefinition
from jingwei.game.motifs import MOTIFS
from jingwei.game.progress import ProgressStore


@dataclass(frozen=True)
class AlbumEntry:
    """收藏册中的一个纹样条目。"""

    level_id: str
    title: str
    motif: str
    cultural_note: str
    reference: str
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
    reference: str
    unlocked: bool
    stars: int | None
    best_score: float | None
    match_ratio: float | None
    compression_ratio: float | None
    shape_star: bool
    craft_star: bool
    speed_star: bool
    target: tuple[tuple[bool, ...], ...]


ALBUM: tuple[AlbumEntry, ...] = tuple(
    AlbumEntry(
        level_id=level.level_id,
        title=motif.name,
        motif=motif.motif_type,
        cultural_note=motif.cultural_note,
        reference=motif.reference,
        level=level,
    )
    for level, motif in zip(LEVELS, MOTIFS)
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
                reference=entry.reference,
                unlocked=progress.is_level_unlocked(index),
                stars=None if record is None else record.stars,
                best_score=None if record is None else record.best_score,
                match_ratio=None if record is None else record.match_ratio,
                compression_ratio=None if record is None else record.compression_ratio,
                shape_star=False if record is None else record.shape_star,
                craft_star=False if record is None else record.craft_star,
                speed_star=False if record is None else record.speed_star,
                target=entry.level.target,
            )
        )
    return tuple(summaries)