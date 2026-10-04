"""领域层：不依赖图形界面的核心模型与算法。"""

from jingwei.domain.compiler import (
    Card,
    CompileReport,
    Pick,
    WeavePlan,
    compile_pattern,
)
from jingwei.domain.models import PatternGrid
from jingwei.domain.weaver import WeaveMatrix, build_weave_matrix

__all__ = [
    "Card",
    "CompileReport",
    "PatternGrid",
    "Pick",
    "WeaveMatrix",
    "WeavePlan",
    "build_weave_matrix",
    "compile_pattern",
]
