"""将点阵纹样编译为可执行的花本提花指令。

当前实现采用教学化模型：纹样的每一行对应一次投纬；值为 ``True`` 的列
表示该经线在该梭次被提升。相同提升组合会被合并为同一张“花本”指令。
这使重复纹样行可以复用指令，形成稳定、可验证的映射关系。
"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.models import PatternGrid


@dataclass(frozen=True)
class Card:
    """一张去重后的花本指令。"""

    card_id: str
    lifted_warp: tuple[int, ...]
    first_source_row: int
    occurrences: int


@dataclass(frozen=True)
class Pick:
    """某一梭实际执行的花本指令。"""

    pick_index: int
    source_row: int
    card_id: str
    lifted_warp: tuple[int, ...]


@dataclass(frozen=True)
class CompileReport:
    """编译过程的可读统计结果。"""

    original_pick_count: int
    unique_card_count: int
    compression_ratio: float
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class WeavePlan:
    """完整织造计划：尺寸、花本表和按顺序排列的投梭记录。"""

    warp_count: int
    weft_count: int
    cards: tuple[Card, ...]
    picks: tuple[Pick, ...]
    report: CompileReport


@dataclass
class _CardBuilder:
    """编译期间使用的可变计数器，编译结束后转换为不可变 Card。"""

    card_id: str
    lifted_warp: tuple[int, ...]
    first_source_row: int
    occurrences: int = 0


def _lifted_columns(row: tuple[bool, ...]) -> tuple[int, ...]:
    """返回该行所有被提升经线的列号。"""
    return tuple(column for column, is_lifted in enumerate(row) if is_lifted)


def compile_pattern(grid: PatternGrid) -> WeavePlan:
    """把 PatternGrid 编译为确定性的 WeavePlan。

    算法按首次出现顺序为提升组合分配 ``C01``、``C02`` 等编号；
    相同组合始终复用同一编号。整个纹样为空时不生成假指令，而是返回
    空计划并附带警告，便于界面明确提示用户。
    """

    if not isinstance(grid, PatternGrid):
        raise TypeError("compile_pattern 只接受 PatternGrid")

    if grid.is_empty():
        warning = "纹样为空，未生成花本指令"
        return WeavePlan(
            warp_count=grid.width,
            weft_count=grid.height,
            cards=(),
            picks=(),
            report=CompileReport(
                original_pick_count=0,
                unique_card_count=0,
                compression_ratio=0.0,
                warnings=(warning,),
            ),
        )

    builders: dict[tuple[int, ...], _CardBuilder] = {}
    picks: list[Pick] = []

    for row_index in range(grid.height):
        lifted_warp = _lifted_columns(grid.row(row_index))

        builder = builders.get(lifted_warp)
        if builder is None:
            builder = _CardBuilder(
                card_id=f"C{len(builders) + 1:02d}",
                lifted_warp=lifted_warp,
                first_source_row=row_index,
            )
            builders[lifted_warp] = builder

        builder.occurrences += 1
        picks.append(
            Pick(
                pick_index=row_index,
                source_row=row_index,
                card_id=builder.card_id,
                lifted_warp=lifted_warp,
            )
        )

    cards = tuple(
        Card(
            card_id=builder.card_id,
            lifted_warp=builder.lifted_warp,
            first_source_row=builder.first_source_row,
            occurrences=builder.occurrences,
        )
        for builder in builders.values()
    )
    original_pick_count = grid.height
    unique_card_count = len(cards)
    compression_ratio = 1.0 - (unique_card_count / original_pick_count)

    return WeavePlan(
        warp_count=grid.width,
        weft_count=grid.height,
        cards=cards,
        picks=tuple(picks),
        report=CompileReport(
            original_pick_count=original_pick_count,
            unique_card_count=unique_card_count,
            compression_ratio=compression_ratio,
            warnings=(),
        ),
    )
