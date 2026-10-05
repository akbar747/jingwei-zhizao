"""限时订单的纯Python倒计时模型。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChallengeSnapshot:
    """一次倒计时读取结果。"""

    elapsed_seconds: float
    remaining_seconds: float
    expired: bool
    progress_ratio: float


class ChallengeClock:
    """管理关卡倒计时，不依赖GUI定时器。"""

    def __init__(self, duration_seconds: float) -> None:
        if duration_seconds <= 0:
            raise ValueError("订单时间必须大于0")
        self.duration_seconds = float(duration_seconds)
        self._elapsed_seconds = 0.0

    @property
    def elapsed_seconds(self) -> float:
        return self._elapsed_seconds

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.duration_seconds - self._elapsed_seconds)

    @property
    def expired(self) -> bool:
        return self.remaining_seconds <= 0.0

    def snapshot(self) -> ChallengeSnapshot:
        return ChallengeSnapshot(
            elapsed_seconds=min(self._elapsed_seconds, self.duration_seconds),
            remaining_seconds=self.remaining_seconds,
            expired=self.expired,
            progress_ratio=min(1.0, self._elapsed_seconds / self.duration_seconds),
        )

    def tick(self, seconds: float = 1.0) -> ChallengeSnapshot:
        if seconds < 0:
            raise ValueError("倒计时增量不能为负数")
        self._elapsed_seconds = min(
            self.duration_seconds,
            self._elapsed_seconds + float(seconds),
        )
        return self.snapshot()

    def reset(self) -> ChallengeSnapshot:
        self._elapsed_seconds = 0.0
        return self.snapshot()
