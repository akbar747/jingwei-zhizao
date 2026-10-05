"""程序化纹样生成：用确定性随机数离线生成传统织锦风格纹样。

同一个种子永远得到同一件纹样，因此可以复现、可以出题，也可以作为
自由模式的灵感来源。生成器不依赖网络，也不依赖任何外部素材。
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

PATTERN_STYLES: tuple[str, ...] = ("celestial", "lattice", "thunder", "rosette")

_STYLE_LABELS: dict[str, str] = {
    "celestial": "天圆回纹",
    "lattice": "菱格锦",
    "thunder": "云雷纹",
    "rosette": "团花纹",
}


@dataclass(frozen=True)
class GeneratedPattern:
    """一件程序化生成的纹样。"""

    style: str
    style_label: str
    seed: int
    size: int
    cells: tuple[tuple[bool, ...], ...]


def _empty(size: int) -> list[list[bool]]:
    return [[False for _ in range(size)] for _ in range(size)]


def _symmetrize(cells: list[list[bool]]) -> list[list[bool]]:
    size = len(cells)
    for row in range(size):
        for column in range(size):
            value = (
                cells[row][column]
                or cells[row][size - 1 - column]
                or cells[size - 1 - row][column]
                or cells[size - 1 - row][size - 1 - column]
            )
            cells[row][column] = value
            cells[row][size - 1 - column] = value
            cells[size - 1 - row][column] = value
            cells[size - 1 - row][size - 1 - column] = value
    return cells


def _celestial(size: int, rng: random.Random) -> list[list[bool]]:
    cells = _empty(size)
    center = (size - 1) / 2
    radius = size * 0.34
    for row in range(size):
        for column in range(size):
            distance = max(abs(column - center), abs(row - center))
            if abs(distance - radius) <= 0.75:
                cells[row][column] = True
    for _ in range(size):
        column = rng.randrange(size)
        row = rng.randrange(size)
        if abs(column - center) + abs(row - center) >= size * 0.4:
            cells[row][column] = True
    return _symmetrize(cells)


def _lattice(size: int, rng: random.Random) -> list[list[bool]]:
    """菱形骨架：只用对角线与稀疏节点，避免整片填满。"""

    cells = _empty(size)
    step = rng.choice((3, 4))
    center = (size - 1) / 2
    half = max(1.0, size * 0.34)
    for row in range(size):
        for column in range(size):
            distance = abs(column - center) + abs(row - center)
            if abs(distance - half) <= 0.7:
                cells[row][column] = True
            elif (column + row) % step == 0 and (row - column) % step == 0:
                cells[row][column] = True
    for index in range(size):
        if index % step == 0:
            cells[index][index] = True
            cells[index][size - 1 - index] = True
    return _symmetrize(cells)


def _thunder(size: int, rng: random.Random) -> list[list[bool]]:
    cells = _empty(size)
    arm = max(1, size // 4)
    for index in range(size):
        if index % max(2, arm) < arm:
            cells[index % size][index] = True
            cells[index][size - 1 - index] = True
    for _ in range(arm):
        row = rng.randrange(size)
        length = rng.randrange(1, arm + 1)
        start = rng.randrange(0, max(1, size - length))
        for offset in range(length):
            cells[row][start + offset] = True
    return _symmetrize(cells)


def _rosette(size: int, rng: random.Random) -> list[list[bool]]:
    """团花：同心方框 + 放射花瓣，形成饱满的中心构图。"""

    cells = _empty(size)
    center = (size - 1) / 2
    petals = rng.choice((4, 8))
    inner = max(1.0, size * 0.12)
    outer = max(inner + 1, size * 0.36)
    for row in range(size):
        for column in range(size):
            distance = max(abs(column - center), abs(row - center))
            if distance <= inner or abs(distance - outer) <= 0.8:
                cells[row][column] = True
    middle = (inner + outer) / 2
    for index in range(petals):
        row = int(round(center + middle * math.sin(index * math.tau / petals)))
        column = int(round(center + middle * math.cos(index * math.tau / petals)))
        if 0 <= row < size and 0 <= column < size:
            cells[row][column] = True
            cells[row][size - 1 - column] = True
            cells[size - 1 - row][column] = True
            cells[size - 1 - row][size - 1 - column] = True
    return _symmetrize(cells)


_GENERATORS = {
    "celestial": _celestial,
    "lattice": _lattice,
    "thunder": _thunder,
    "rosette": _rosette,
}


def pattern_from_seed(
    seed: int, size: int, style: str | None = None
) -> tuple[tuple[bool, ...], ...]:
    """按种子生成纹样矩阵。"""

    return generate_pattern(seed=seed, size=size, style=style).cells


def generate_pattern(
    seed: int,
    size: int,
    style: str | None = None,
) -> GeneratedPattern:
    """生成一件确定性的程序化纹样。"""

    if size < 4:
        raise ValueError("纹样尺寸至少为4，才能形成可辨识的图案")
    if style is not None and style not in _GENERATORS:
        raise ValueError(f"未知纹样风格: {style}")

    rng = random.Random(seed)
    chosen = style if style is not None else rng.choice(PATTERN_STYLES)
    cells = _GENERATORS[chosen](size, rng)
    if not any(any(row) for row in cells):
        cells[0][0] = True
        _symmetrize(cells)
    return GeneratedPattern(
        style=chosen,
        style_label=_STYLE_LABELS[chosen],
        seed=seed,
        size=size,
        cells=tuple(tuple(row) for row in cells),
    )