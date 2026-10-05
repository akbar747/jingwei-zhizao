"""玩家进度存档：关卡星级、最佳成绩与解锁状态。

存档使用 JSON，落在用户目录（默认 ``%APPDATA%/JingweiZhizao/progress.json``），
因此不需要联网，也不会把个人成绩写进仓库。文件损坏时静默回退为空进度，
保证软件始终可以启动。
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from jingwei.game.catalog import LEVELS


@dataclass(frozen=True)
class LevelRecord:
    """一个关卡的历史最佳成绩，包含三颗星的完整明细。"""

    stars: int
    best_score: float
    completed_at: float
    match_ratio: float = 0.0
    compression_ratio: float = 0.0
    shape_star: bool = False
    craft_star: bool = False
    speed_star: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.stars, int) or not 0 <= self.stars <= 3:
            raise ValueError("星级必须是 0 到 3 的整数")
        if self.best_score < 0:
            raise ValueError("最佳成绩不能为负数")
        if self.completed_at < 0:
            raise ValueError("完成时间不能为负数")


def default_progress_path() -> Path:
    """返回跨平台可写的默认存档路径。"""

    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / "JingweiZhizao" / "progress.json"
    return Path.home() / ".jingwei_zhizao" / "progress.json"


class ProgressStore:
    """管理关卡进度的读写；核心逻辑不依赖图形界面。"""

    def __init__(self, path: Path | None = None, *, load: bool = True) -> None:
        self.path = Path(path) if path is not None else default_progress_path()
        self._in_memory = not load
        self._records: dict[str, LevelRecord] = {}
        if load:
            self._load()

    @classmethod
    def in_memory(cls) -> "ProgressStore":
        """创建一个只存在于内存中的存档，方便测试和临时模式。"""

        return cls(load=False)

    @property
    def records(self) -> dict[str, LevelRecord]:
        """返回记录副本，避免调用方绕过持久化直接改写。"""

        return dict(self._records)

    def get(self, level_id: str) -> LevelRecord | None:
        return self._records.get(level_id)

    def total_stars(self) -> int:
        return sum(record.stars for record in self._records.values())

    def is_level_unlocked(self, index: int) -> bool:
        """第一关始终解锁；其余关卡要求前一关已通关。"""

        if index <= 0:
            return True
        if index >= len(LEVELS):
            return False
        previous = LEVELS[index - 1]
        return previous.level_id in self._records

    def record(
        self,
        level_id: str,
        *,
        stars: int,
        score: float,
        completed_at: float,
        match_ratio: float = 0.0,
        compression_ratio: float = 0.0,
        shape_star: bool = False,
        craft_star: bool = False,
        speed_star: bool = False,
    ) -> LevelRecord:
        """记录一次成绩，仅当星级或分数更好时覆盖历史最佳。"""

        candidate = LevelRecord(
            stars=stars,
            best_score=float(score),
            completed_at=completed_at,
            match_ratio=float(match_ratio),
            compression_ratio=float(compression_ratio),
            shape_star=bool(shape_star),
            craft_star=bool(craft_star),
            speed_star=bool(speed_star),
        )
        existing = self._records.get(level_id)
        if existing is not None and (candidate.stars, candidate.best_score) <= (
            existing.stars,
            existing.best_score,
        ):
            return existing
        self._records[level_id] = candidate
        return candidate

    def save(self) -> None:
        """原子写入 JSON，避免写入中途崩溃损坏存档。

        内存存档（``in_memory``）不落盘，供测试和自由模式使用。
        """

        if self._in_memory:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "records": {
                level_id: {
                    "stars": record.stars,
                    "best_score": record.best_score,
                    "completed_at": record.completed_at,
                    "match_ratio": record.match_ratio,
                    "compression_ratio": record.compression_ratio,
                    "shape_star": record.shape_star,
                    "craft_star": record.craft_star,
                    "speed_star": record.speed_star,
                }
                for level_id, record in self._records.items()
            },
        }
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        handle, temp_name = tempfile.mkstemp(
            prefix="progress-", suffix=".tmp", dir=str(self.path.parent)
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                stream.write(serialized)
            os.replace(temp_name, self.path)
        except BaseException:
            Path(temp_name).unlink(missing_ok=True)
            raise

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            raw_records = payload.get("records", {})
            if not isinstance(raw_records, dict):
                return
            for level_id, raw in raw_records.items():
                if not isinstance(raw, dict):
                    continue
                self._records[str(level_id)] = LevelRecord(
                    stars=int(raw["stars"]),
                    best_score=float(raw["best_score"]),
                    completed_at=float(raw["completed_at"]),
                    match_ratio=float(raw.get("match_ratio", 0.0)),
                    compression_ratio=float(raw.get("compression_ratio", 0.0)),
                    shape_star=bool(raw.get("shape_star", False)),
                    craft_star=bool(raw.get("craft_star", False)),
                    speed_star=bool(raw.get("speed_star", False)),
                )
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            self._records.clear()