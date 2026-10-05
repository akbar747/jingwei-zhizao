"""音效播放器的无声测试。"""

import unittest

from jingwei.ui.sound_player import SoundPlayer


class SoundPlayerTests(unittest.TestCase):
    def test_disabled_player_never_raises(self):
        player = SoundPlayer(enabled=False)

        player.play_compile()
        player.play_shuttle()
        player.play_success()

        self.assertFalse(player.enabled)

    def test_default_player_can_be_constructed(self):
        player = SoundPlayer(enabled=False)

        self.assertFalse(player.enabled)


if __name__ == "__main__":
    unittest.main()
