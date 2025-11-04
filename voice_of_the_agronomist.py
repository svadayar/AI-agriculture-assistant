"""
voice_of_the_agronomist.py
Turn final agronomy guidance text into an audio file.

For now:
- We generate a silent WAV file in output_audio/
- We also write the text to output_audio/agri_reply_transcript.txt
  so you can read what would have been spoken.

In production:
- Call ElevenLabs / Azure TTS / etc.
"""

import os
from utils_audio import write_silent_wav, ensure_dir


def agronomist_response_to_speech(answer_text: str, output_path: str) -> str:
    """
    Create an audio file for the farmer to play.
    Currently just a silent WAV placeholder.

    Returns the path to the WAV file.
    """
    out_dir = os.path.dirname(output_path)
    ensure_dir(out_dir)

    # Write silent wav placeholder
    write_silent_wav(output_path, seconds=3.0)

    # Save transcript alongside
    transcript_path = os.path.join(out_dir, "agri_reply_transcript.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(answer_text)

    return output_path
