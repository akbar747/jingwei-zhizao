"""织坊订单变体：同一关卡的多种玩法修饰。

订单不改变核心织造规则，只改变外部约束（时限、压缩门槛、目标可见性），
因此可以用纯 Python 建模并单独测试。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random


class OrderModifier(Enum):
    """订单修饰类型。"""

    FREE = "free"
    URGENT = "urgent"
    MASTERPIECE = "masterpiece"
    MEMORY = "memory"
    BLIND = "blind"

    @property
    def display_name(self) -> str:
        return {
            OrderModifier.FREE: "常规订单",
            OrderModifier.URGENT: "加急订单",
            OrderModifier.MASTERPIECE: "精品订单",
            OrderModifier.MEMORY: "记忆订单",
            OrderModifier.BLIND: "盲织订单",
        }[self]

    @property
    def rule_text(self) -> str:
        return {
            OrderModifier.FREE: "标准时限，常规规格。",
            OrderModifier.URGENT: "时限压缩 45%，考验织造节奏。",
            OrderModifier.MASTERPIECE: "花本压缩率需达到 85%。",
            OrderModifier.MEMORY: "目标纹样只预览 3 秒。",
            OrderModifier.BLIND: "隐藏实时匹配提示，凭真功夫织造。",
        }[self]


ORDER_MODIFIERS: tuple[OrderModifier, ...] = (
    OrderModifier.FREE,
    OrderModifier.URGENT,
    OrderModifier.MASTERPIECE,
    OrderModifier.MEMORY,
    OrderModifier.BLIND,
)

# 抽签池不包含常规订单，保证重玩时确实换一种体验。
_RANDOM_POOL: tuple[OrderModifier, ...] = (
    OrderModifier.URGENT,
    OrderModifier.MASTERPIECE,
    OrderModifier.MEMORY,
    OrderModifier.BLIND,
)

_TIME_MULTIPLIER: dict[OrderModifier, float] = {
    OrderModifier.FREE: 1.0,
    OrderModifier.URGENT: 0.55,
    OrderModifier.MASTERPIECE: 1.2,
    OrderModifier.MEMORY: 1.0,
    OrderModifier.BLIND: 1.0,
}

_CRAFT_FLOOR: dict[OrderModifier, float] = {
    OrderModifier.FREE: 0.70,
    OrderModifier.URGENT: 0.70,
    OrderModifier.MASTERPIECE: 0.85,
    OrderModifier.MEMORY: 0.70,
    OrderModifier.BLIND: 0.70,
}


@dataclass(frozen=True)
class OrderSettings:
    """一次订单的实际参数。"""

    modifier: OrderModifier
    time_limit_seconds: float
    minimum_compression: float
    preview_seconds: float = 0.0

    @property
    def urgent(self) -> bool:
        return self.modifier is OrderModifier.URGENT

    @property
    def hidden_target(self) -> bool:
        return self.modifier is OrderModifier.MEMORY

    @property
    def hides_match_hint(self) -> bool:
        return self.modifier is OrderModifier.BLIND


def apply_modifier(base_seconds: float, modifier: OrderModifier) -> OrderSettings:
    """把关卡基准时限转换为具体订单参数。"""

    if base_seconds <= 0:
        raise ValueError("基准时限必须大于0")
    if not isinstance(modifier, OrderModifier):
        raise TypeError("modifier 必须是 OrderModifier")

    preview = 3.0 if modifier is OrderModifier.MEMORY else 0.0
    return OrderSettings(
        modifier=modifier,
        time_limit_seconds=base_seconds * _TIME_MULTIPLIER[modifier],
        minimum_compression=_CRAFT_FLOOR[modifier],
        preview_seconds=preview,
    )


def choose_modifier(*, seed: int | None = None, allow_free: bool = False) -> OrderModifier:
    """确定性地抽取一个订单修饰。

    ``seed`` 相同时结果稳定，便于测试与“重放同一订单”；不传 seed 时使用
    系统随机源，保证每次重开有变化。
    """

    if allow_free:
        return OrderModifier.FREE
    rng = random.Random(seed)
    return rng.choice(_RANDOM_POOL)