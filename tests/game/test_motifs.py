"""民族文化纹样库测试。"""

import unittest

from jingwei.game.motifs import (
    MOTIFS,
    build_campaign_levels,
    get_motif,
)


class MotifLibraryTests(unittest.TestCase):
    def test_library_has_named_motifs(self):
        self.assertGreaterEqual(len(MOTIFS), 6)
        for motif in MOTIFS:
            self.assertTrue(motif.motif_id)
            self.assertTrue(motif.name)
            self.assertTrue(motif.ethnic_group)
            self.assertTrue(motif.cultural_note)
            self.assertTrue(motif.pattern)
            self.assertGreater(motif.size, 0)

    def test_patterns_are_square_and_non_empty(self):
        for motif in MOTIFS:
            self.assertEqual(len(motif.pattern), motif.size)
            self.assertTrue(all(len(row) == motif.size for row in motif.pattern))
            self.assertTrue(any(any(row) for row in motif.pattern))

    def test_get_motif_by_id(self):
        first = MOTIFS[0]
        self.assertIs(get_motif(first.motif_id), first)

    def test_unknown_motif_is_rejected(self):
        with self.assertRaises(KeyError):
            get_motif("nope")

    def test_campaign_levels_match_motif_count(self):
        levels = build_campaign_levels()

        self.assertEqual(len(levels), len(MOTIFS))
        self.assertEqual(
            [level.level_id for level in levels],
            [f"L{index + 1:02d}" for index in range(len(MOTIFS))],
        )

    def test_campaign_targets_match_motif_patterns(self):
        levels = build_campaign_levels()
        for level, motif in zip(levels, MOTIFS):
            self.assertEqual(level.target, motif.pattern)
            self.assertEqual(level.width, motif.size)
            self.assertIn(motif.name, level.name)

    def test_every_motif_has_a_source_note(self):
        for motif in MOTIFS:
            self.assertTrue(motif.reference.strip())


if __name__ == "__main__":
    unittest.main()