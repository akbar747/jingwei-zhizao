"""纹样收藏册目录测试。"""

import unittest

from jingwei.game.album import ALBUM, build_album_summaries, get_album_entry
from jingwei.game.catalog import LEVELS
from jingwei.game.progress import ProgressStore


class AlbumCatalogTests(unittest.TestCase):
    def test_album_covers_every_level(self):
        self.assertEqual(len(ALBUM), len(LEVELS))
        self.assertEqual(
            [entry.level_id for entry in ALBUM],
            [level.level_id for level in LEVELS],
        )

    def test_first_level_is_unlocked_and_rest_are_locked(self):
        summaries = build_album_summaries(ProgressStore.in_memory())

        self.assertTrue(summaries[0].unlocked)
        self.assertFalse(summaries[1].unlocked)
        self.assertIsNone(summaries[0].stars)

    def test_clearing_a_level_unlocks_the_next(self):
        progress = ProgressStore.in_memory()
        progress.record("L01", stars=2, score=80.0, completed_at=1.0)

        summaries = build_album_summaries(progress)

        self.assertTrue(summaries[1].unlocked)
        self.assertEqual(summaries[0].stars, 2)

    def test_unknown_entry_is_rejected(self):
        with self.assertRaises(KeyError):
            get_album_entry("NOPE")

    def test_every_entry_has_a_cultural_note(self):
        for entry in ALBUM:
            self.assertTrue(entry.cultural_note.strip())
            self.assertTrue(entry.title.strip())


if __name__ == "__main__":
    unittest.main()