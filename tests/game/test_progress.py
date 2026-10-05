"""进度存档领域测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from jingwei.game.progress import LevelRecord, ProgressStore


class ProgressStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "progress.json"
        self.store = ProgressStore(self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_new_progress_has_no_records(self):
        self.assertEqual(dict(self.store.records), {})
        self.assertEqual(self.store.total_stars(), 0)

    def test_record_score_keeps_best_result(self):
        self.store.record("L01", stars=2, score=80.0, completed_at=10.0)
        self.store.record("L01", stars=3, score=95.0, completed_at=20.0)
        self.store.record("L01", stars=1, score=70.0, completed_at=30.0)

        record = self.store.records["L01"]
        self.assertEqual(record.stars, 3)
        self.assertEqual(record.best_score, 95.0)
        self.assertEqual(record.completed_at, 20.0)

    def test_save_and_load_round_trip(self):
        self.store.record("L01", stars=3, score=92.5, completed_at=5.0)
        self.store.record("L02", stars=1, score=60.0, completed_at=8.0)
        self.store.save()

        reloaded = ProgressStore(self.path)

        self.assertEqual(reloaded.total_stars(), 4)
        self.assertEqual(reloaded.records["L01"].best_score, 92.5)
        self.assertEqual(reloaded.records["L02"].stars, 1)

    def test_corrupted_file_falls_back_to_empty(self):
        self.path.write_text("{not valid json", encoding="utf-8")

        store = ProgressStore(self.path)

        self.assertEqual(dict(store.records), {})
        self.assertEqual(store.total_stars(), 0)

    def test_stars_must_be_within_range(self):
        with self.assertRaises(ValueError):
            LevelRecord(stars=4, best_score=100.0, completed_at=0.0)

    def test_is_level_unlocked_only_when_previous_cleared(self):
        self.assertTrue(self.store.is_level_unlocked(0))
        self.assertFalse(self.store.is_level_unlocked(1))

        self.store.record("L01", stars=1, score=55.0, completed_at=1.0)

        self.assertTrue(self.store.is_level_unlocked(1))
        self.assertFalse(self.store.is_level_unlocked(2))


if __name__ == "__main__":
    unittest.main()