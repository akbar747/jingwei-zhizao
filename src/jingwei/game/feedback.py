"""把花本压缩结果转换为游戏化连击反馈。"""

from __future__ import annotations

from dataclasses import dataclass

from jingwei.domain.compiler import WeavePlan


@dataclass(frozen=True)
class CompileCombo:
    """一次编译的连击反馈。"""

    reused_rows: int
    unique_cards: int
    compression_ratio: float
    multiplier: int
    message: str


def calculate_compile_combo(plan: WeavePlan) -> CompileCombo:
    """根据重复行数量生成可展示的压缩连击。"""
    report = plan.report
    if report.original_pick_count <= 0 or not plan.picks:
        return CompileCombo(
            reused_rows=0,
            unique_cards=0,
            compression_ratio=0.0,
            multiplier=1,
            message="先画一个纹样，再编译花本",
        )

    reused_rows = max(0, report.original_pick_count - report.unique_card_count)
    multiplier = 1 + int(report.compression_ratio * 3)
    message = (
        f"花本压缩 {report.compression_ratio:.0%} · "
        f"连击 x{multiplier} · 复用 {reused_rows} 行"
    )
    return CompileCombo(
        reused_rows=reused_rows,
        unique_cards=report.unique_card_count,
        compression_ratio=report.compression_ratio,
        multiplier=multiplier,
        message=message,
    )
