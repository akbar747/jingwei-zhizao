"""根据花本织造计划生成确定性的织物矩阵。

教学模型采用简化规则：某根经线在某一梭被提升时，该经线覆盖当前纬线，
矩阵单元记为 ``True``；未提升则记为 ``False``。动画和视觉预览以后只能
读取该矩阵，不能自行推算另一套结果。
"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.compiler import WeavePlan


@dataclass(frozen=True)
class WeaveMatrix:
    """最终织物矩阵。``True`` 表示经线覆盖纬线。"""

    warp_count: int
    weft_count: int
    cells: tuple[tuple[bool, ...], ...]


def build_weave_matrix(plan: WeavePlan) -> WeaveMatrix:
    """将 WeavePlan 转换为逐梭排列的织物矩阵。

    发现投梭数量、行号或经线索引不一致时直接抛出 ``ValueError``，避免
    生成看似正常但实际不完整的织物结果。
    """

    if len(plan.picks) != plan.weft_count:
        raise ValueError(
            f"投梭数量 {len(plan.picks)} 与纬线数量 {plan.weft_count} 不一致"
        )

    rows: list[tuple[bool, ...]] = []
    for row_index, pick in enumerate(plan.picks):
        if pick.pick_index != row_index or pick.source_row != row_index:
            raise ValueError(
                f"第 {row_index} 梭的行号不连续: pick_index={pick.pick_index}, "
                f"source_row={pick.source_row}"
            )

        row = [False] * plan.warp_count
        for warp_index in pick.lifted_warp:
            if warp_index < 0 or warp_index >= plan.warp_count:
                raise ValueError(
                    f"第 {row_index} 梭包含越界经线索引: {warp_index}"
                )
            row[warp_index] = True
        rows.append(tuple(row))

    return WeaveMatrix(
        warp_count=plan.warp_count,
        weft_count=plan.weft_count,
        cells=tuple(rows),
    )
