"""程序化纹样生成测试。"""

import unittest

from jingwei.game.generator import (
    PATTERN_STYLES,
    generate_pattern,
    pattern_from_seed,
)


class GeneratorTests(unittest.TestCase):
    def test_same_seed_produces_same_pattern(self):
        first = pattern_from_seed(1234, size=12)
        second = pattern_from_seed(1234, size=12)

        self.assertEqual(first, second)

    def test_different_seeds_can_produce_different_patterns(self):
        patterns = {pattern_from_seed(seed, size=10) for seed in range(8)}

        self.assertGreater(len(patterns), 1)

    def test_pattern_is_square_and_non_empty(self):
        pattern = pattern_from_seed(7, size=9)

        self.assertEqual(len(pattern), 9)
        self.assertTrue(all(len(row) == 9 for row in pattern))
        self.assertTrue(any(any(row) for row in pattern))

    def test_generate_pattern_returns_style_and_matrix(self):
        result = generate_pattern(seed=5, size=12)

        self.assertIn(result.style, PATTERN_STYLES)
        self.assertEqual(len(result.cells), 12)
        self.assertTrue(result.style_label.strip())

    def test_invalid_size_is_rejected(self):
        with self.assertRaises(ValueError):
            pattern_from_seed(1, size=1)

    def test_style_is_deterministic_for_seed(self):
        self.assertEqual(
            generate_pattern(seed=99, size=12).style,
            generate_pattern(seed=99, size=12).style,
        )

    def test_unknown_style_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_pattern(seed=1, size=8, style="nope")


if __name__ == "__main__":
    unittest.main()