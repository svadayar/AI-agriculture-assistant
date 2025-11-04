"""
voice_of_the_farmer.py
Capture farmer audio and convert it to text.

Right now we provide:
- transcribe_farmer_audio(audio_path) -> str

In production:
- record mic input (if you want)
- send to Whisper / Groq / etc.
"""

def transcribe_farmer_audio(audio_path: str) -> str:
    """
    Mock transcription.
    Later: call real STT model with the audio file.
    """
    if not audio_path:
        return ""

    # Fake transcript to let the pipeline run
    return (
        "My tomato leaves have yellow and black spots after heavy rain "
        "for the last 3 days. What should I do?"
    )
