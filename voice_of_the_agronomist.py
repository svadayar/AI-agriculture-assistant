# voice_of_the_agronomist.py
"""
Turn agronomy guidance text into audio for the farmer.

TTS Strategy (3-tier fallback):
1. ElevenLabs (best quality, requires API key + cost)
2. Local pyttsx3 (free, offline, decent quality)
3. Silent WAV (fallback, user sees text)
"""

import os
import requests
from dotenv import load_dotenv

from utils_audio import ensure_dir, write_silent_wav
from logging_config import get_logger

logger = get_logger("voice_of_the_agronomist")

load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
OUTPUT_DIR = "output_audio"


def _elevenlabs_tts(text: str, output_path: str) -> None:
    """
    Call ElevenLabs API for TTS.
    
    Args:
        text: Text to convert to speech
        output_path: Path to save MP3 file
        
    Raises:
        RuntimeError: If API call fails
    """
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

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            error_msg = f"ElevenLabs failed: {resp.status_code}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        with open(output_path, "wb") as f:
            f.write(resp.content)
        logger.info(f"ElevenLabs TTS created: {output_path}")

    except requests.RequestException as e:
        logger.error(f"ElevenLabs network error: {e}")
        raise


def _local_tts(text: str, output_path: str) -> None:
    """
    Local TTS using pyttsx3 (free, offline).
    
    Args:
        text: Text to convert to speech
        output_path: Path to save WAV file
        
    Raises:
        ImportError: If pyttsx3 not installed
        RuntimeError: If TTS fails
    """
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Slow down for clarity
        engine.setProperty('volume', 0.9)
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        logger.info(f"Local TTS created: {output_path}")

    except ImportError:
        logger.error("pyttsx3 not installed. Cannot use local TTS.")
        raise ImportError("pyttsx3 required for local TTS")
    except Exception as e:
        logger.error(f"Local TTS error: {e}")
        raise RuntimeError(f"Local TTS failed: {e}") from e


def _save_transcript(answer_text: str) -> None:
    """
    Save response text to file for debugging/reference.
    
    Args:
        answer_text: Text to save
    """
    try:
        transcript_path = os.path.join(OUTPUT_DIR, "agri_reply_transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(answer_text)
        logger.debug(f"Transcript saved: {transcript_path}")
    except Exception as e:
        logger.warning(f"Could not save transcript: {e}")


def agronomist_response_to_speech(answer_text: str, output_path: str) -> str:
    """
    Main entry point. Try TTS in order: ElevenLabs → Local → Silent fallback.
    Always returns a path that exists.
    
    Args:
        answer_text: Final agronomy guidance text
        output_path: Preferred output path for audio
        
    Returns:
        Path to audio file (may be different from output_path if fallback used)
    """
    ensure_dir(OUTPUT_DIR)
    _save_transcript(answer_text)

    # 1. Try ElevenLabs if configured
    if ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID:
        try:
            _elevenlabs_tts(answer_text, output_path)
            logger.info("Using ElevenLabs TTS")
            return output_path
        except Exception as e:
            logger.warning(f"ElevenLabs failed: {e}. Trying next TTS option...")

    # 2. Try local pyttsx3
    try:
        local_wav = os.path.join(OUTPUT_DIR, "agri_reply_local.wav")
        _local_tts(answer_text, local_wav)
        logger.info("Using local pyttsx3 TTS")
        return local_wav
    except Exception as e:
        logger.warning(f"Local TTS failed: {e}. Falling back to silent audio...")

    # 3. Fallback: create silent WAV
    logger.warning("All TTS options failed. Using silent audio fallback.")
    fallback_wav = os.path.join(OUTPUT_DIR, "fallback_silence.wav")
    write_silent_wav(fallback_wav, seconds=2.0)
    return fallback_wav
