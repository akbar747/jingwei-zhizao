"""简单的Windows音效播放器，失败时静默降级。"""

from __future__ import annotations

import math
import os
import struct
import sys
import tempfile
import wave
from pathlib import Path


class SoundPlayer:
    """播放短促的程序化音效，不依赖外部音频资源。"""

    def __init__(self, enabled: bool | None = None) -> None:
        if enabled is None:
            enabled = (
                sys.platform == "win32"
                and os.environ.get("JINGWEI_DISABLE_SOUND") != "1"
                and os.environ.get("QT_QPA_PLATFORM") != "offscreen"
            )
        self.enabled = bool(enabled) and sys.platform == "win32"
        self._cache_dir = Path(tempfile.gettempdir()) / "jingwei-sfx"
        self._files: dict[tuple[int, int], Path] = {}

    def _tone_file(self, frequency: int, duration_ms: int) -> Path:
        key = (frequency, duration_ms)
        if key in self._files:
            return self._files[key]

        self._cache_dir.mkdir(parents=True, exist_ok=True)
        path = self._cache_dir / f"tone-{frequency}-{duration_ms}.wav"
        if not path.exists():
            sample_rate = 22050
            samples = int(sample_rate * duration_ms / 1000)
            with wave.open(str(path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                frames = bytearray()
                for index in range(samples):
                    fade = min(1.0, index / 80, (samples - index) / 120)
                    value = int(12000 * fade * math.sin(2 * math.pi * frequency * index / sample_rate))
                    frames.extend(struct.pack("<h", value))
                wav.writeframes(bytes(frames))
        self._files[key] = path
        return path

    def _play(self, frequency: int, duration_ms: int) -> None:
        if not self.enabled:
            return
        try:
            import winsound

            path = self._tone_file(frequency, duration_ms)
            winsound.PlaySound(
                str(path),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
        except Exception:
            return

    def play_compile(self) -> None:
        self._play(660, 90)

    def play_shuttle(self) -> None:
        self._play(330, 45)

    def play_success(self) -> None:
        self._play(880, 180)
