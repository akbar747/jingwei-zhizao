"""织锦作品卡导出测试。"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from jingwei.game.artifact import (
    ArtifactCard,
    build_artifact,
    render_artifact_to_image,
    save_artifact_png,
)
from jingwei.game.catalog import LEVELS
from jingwei.game.orders import OrderModifier, apply_modifier
from jingwei.game.stars import StarEngine


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.level = LEVELS[0]
        self.grid = self.level.create_grid()
        self.stars = StarEngine().evaluate(
            self.grid,
            self.level.target,
            compression_ratio=0.75,
            elapsed_seconds=20,
            time_limit_seconds=90,
        )

    def test_build_artifact_captures_level_and_stars(self):
        card = build_artifact(
            self.level,
            self.stars,
            modifier=OrderModifier.FREE,
            woven_at="2026-10-05 12:00",
        )

        self.assertIsInstance(card, ArtifactCard)
        self.assertEqual(card.title, "第一根经线")
        self.assertEqual(card.stars, 3)
        self.assertEqual(card.score, self.stars.score)
        self.assertEqual(card.order_name, "常规订单")
        self.assertEqual(card.woven_at, "2026-10-05 12:00")

    def test_render_produces_correct_canvas_size(self):
        card = build_artifact(self.level, self.stars, woven_at="2026-10-05 12:00")

        image = render_artifact_to_image(card, width=520, height=740)

        self.assertEqual(image.width(), 520)
        self.assertEqual(image.height(), 740)
        self.assertFalse(image.isNull())

    def test_save_writes_png_file(self):
        import tempfile
        from pathlib import Path

        card = build_artifact(self.level, self.stars, woven_at="2026-10-05 12:00")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "art.png"
            save_artifact_png(card, path)

            self.assertTrue(path.exists())
            loaded = QImage(str(path))
            self.assertFalse(loaded.isNull())
            self.assertEqual(loaded.width(), 720)

    def test_orders_are_recorded_on_the_card(self):
        order = apply_modifier(self.level.par_seconds, OrderModifier.URGENT)
        card = build_artifact(self.level, self.stars, modifier=order.modifier)

        self.assertEqual(card.order_name, "加急订单")


if __name__ == "__main__":
    unittest.main()