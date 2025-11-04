"""
utils_audio.py
Audio helper utilities.
"""

import os
import wave
import struct


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def write_silent_wav(filepath: str, seconds: float = 2.0, sample_rate: int = 16000):
    """
    Create a tiny silent WAV so the UI always returns an audio file,
    even with mock TTS.
    """
    ensure_dir(os.path.dirname(filepath))

    num_samples = int(seconds * sample_rate)

    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)            # mono
        wf.setsampwidth(2)            # 16-bit
        wf.setframerate(sample_rate)

        for _ in range(num_samples):
            wf.writeframes(struct.pack('<h', 0))  # 16-bit little-endian zero
