"""应用层编译服务。

界面只调用本服务，不直接依赖具体编译算法，后续替换算法或增加日志时
不需要修改窗口组件。
"""

from __future__ import annotations

from jingwei.domain.compiler import WeavePlan, compile_pattern
from jingwei.domain.models import PatternGrid


class CompileService:
    """把用户纹样转换为织造计划。"""

    def compile(self, grid: PatternGrid) -> WeavePlan:
        """调用领域编译器并返回不可变织造计划。"""
        return compile_pattern(grid)
