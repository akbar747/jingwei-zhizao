"""应用入口。"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from jingwei.domain.models import PatternGrid
from jingwei.ui.main_window import MainWindow


def _run_smoke_test() -> int:
    """无人工交互的应用冒烟检查，供CI和本地验证使用。"""
    app = QApplication.instance() or QApplication([sys.argv[0]])
    grid = PatternGrid(
        4,
        4,
        [
            [True, False, True, False],
            [False, True, False, True],
            [True, False, True, False],
            [False, True, False, True],
        ],
    )
    window = MainWindow(grid)
    plan = window.compile_current_pattern()
    app.processEvents()
    if plan.report.unique_card_count != 2:
        return 1
    window.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    """启动桌面窗口，或执行无窗口冒烟检查。"""
    arguments = list(sys.argv if argv is None else argv)
    if "--smoke-test" in arguments:
        return _run_smoke_test()

    app = QApplication(arguments)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
