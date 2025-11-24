"""
voice_of_the_farmer.py
Capture farmer audio and convert it to text.

Provides:
- Real transcription via Groq Whisper API (if key available)
- Fallback mock with varied examples
"""

import os
import random
from dotenv import load_dotenv
from logging_config import get_logger

logger = get_logger("voice_of_the_farmer")
load_dotenv()


def transcribe_farmer_audio(audio_path: str) -> str:
    """
    Convert farmer's audio to text using Groq Whisper API.
    Falls back to mock if no API key or error occurs.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    if not audio_path:
        logger.warning("No audio path provided")
        return ""

    # Try real transcription first
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if groq_api_key:
        try:
            return _transcribe_with_groq(audio_path, groq_api_key)
        except Exception as e:
            logger.warning(f"Groq transcription failed: {e}. Using mock.")
    
    # Fallback mock
    logger.info("Using mock transcription (no GROQ_API_KEY or API call failed)")
    return _mock_transcription()


def _transcribe_with_groq(audio_path: str, api_key: str) -> str:
    """
    Implement Whisper transcription via Groq API.
    
    Args:
        audio_path: Path to audio file
        api_key: Groq API key
        
    Returns:
        Transcribed text
    """
    try:
        import requests
        
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
            headers = {"Authorization": f"Bearer {api_key}"}
            
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            resp = requests.post(url, files=files, headers=headers, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("text", "")
                logger.info(f"Groq transcription successful: {len(text)} chars")
                return text
            else:
                logger.error(f"Groq API error: {resp.status_code}")
                raise RuntimeError(f"Groq API returned {resp.status_code}")
    except Exception as e:
        logger.error(f"Error in Groq transcription: {e}")
        raise


def _mock_transcription() -> str:
    """
    Return a realistic random mock transcription for testing.
    
    Returns:
        Sample farmer question text
    """
    examples = [
        "My tomato leaves have yellow spots after heavy rain. What should I do?",
        "I see small holes in the leaves and some insects underneath. How do I fix this?",
        "The soil is very dry and my plants are starting to wilt. I need help.",
        "There's a white powdery substance on the leaves. Is this a disease?",
        "My corn plants are yellowing from the bottom. What nutrient are they missing?",
        "I noticed brown lesions on the cotton leaves that are spreading. What can I do?",
        "There's black fungal growth on my rice leaves. Is it serious?",
    ]
    choice = random.choice(examples)
    logger.debug(f"Mock transcription selected: {choice[:50]}...")
    return choice
