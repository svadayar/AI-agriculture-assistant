# voice_of_the_agronomist.py
"""
Turn agronomy guidance text into audio for the farmer.

Flow:
1. Try ElevenLabs (real voice)
2. If anything fails, fall back to a local silent wav
"""

import os
import requests
from dotenv import load_dotenv

# we'll reuse our silent wav helper
from utils_audio import ensure_dir, write_silent_wav

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

OUTPUT_DIR = "output_audio"


def _elevenlabs_tts(text: str, output_path: str):
    """Call ElevenLabs and write mp3."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8,
            "style": 0.4,
            "use_speaker_boost": True,
        },
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs failed: {resp.status_code} {resp.text}")

    with open(output_path, "wb") as f:
        f.write(resp.content)


def agronomist_response_to_speech(answer_text: str, output_path: str) -> str:
    """
    Main entry used by the app.
    Always returns a path that exists.
    """
    ensure_dir(OUTPUT_DIR)

    # 1. try elevenlabs if we have keys
    if ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID:
        try:
            _elevenlabs_tts(answer_text, output_path)
            # also save transcript (nice for debugging)
            with open(os.path.join(OUTPUT_DIR, "agri_reply_transcript.txt"), "w", encoding="utf-8") as tf:
                tf.write(answer_text)
            print("🔊 ElevenLabs TTS created:", output_path)
            return output_path
        except Exception as e:
            print("❌ ElevenLabs TTS error:", e)
            print("➡ Falling back to silent audio")

    # 2. fallback: create a tiny silent wav/mp3 so Gradio can still play something
    # if output_path had .mp3, we can just create a wav instead
    fallback_wav = os.path.join(OUTPUT_DIR, "fallback_silence.wav")
    write_silent_wav(fallback_wav, seconds=2.0)
    # also write the text
    with open(os.path.join(OUTPUT_DIR, "agri_reply_transcript.txt"), "w", encoding="utf-8") as tf:
        tf.write(answer_text)
    return fallback_wav
