"""限时订单倒计时领域测试。"""

import unittest

from jingwei.game.challenge import ChallengeClock


class ChallengeClockTests(unittest.TestCase):
    def test_clock_counts_down_and_expires(self):
        clock = ChallengeClock(3)

        first = clock.tick()
        second = clock.tick(1.5)

        self.assertEqual(first.remaining_seconds, 2.0)
        self.assertFalse(first.expired)
        self.assertEqual(second.remaining_seconds, 0.5)
        self.assertFalse(second.expired)

    def test_clock_clamps_at_zero(self):
        clock = ChallengeClock(2)

        clock.tick(5)

        self.assertEqual(clock.remaining_seconds, 0.0)
        self.assertTrue(clock.expired)

    def test_reset_restores_full_duration(self):
        clock = ChallengeClock(4)
        clock.tick(3)

        clock.reset()

        self.assertEqual(clock.remaining_seconds, 4.0)
        self.assertFalse(clock.expired)

    def test_invalid_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            ChallengeClock(0)


if __name__ == "__main__":
    unittest.main()
