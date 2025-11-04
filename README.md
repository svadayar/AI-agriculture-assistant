# AI Agriculture Assistant 1.0 🌾
Voice + Vision Crop Advisory for Farmers

## What this project is
AI Agriculture Assistant 1.0 is an on-field crop triage assistant that simulates a conversation between a farmer and an agronomist.

The assistant can:
1. Listen to a farmer's voice note (speech-to-text)
2. Look at a crop photo (leaf / pest / soil / fruit)
3. Reason about likely issues (disease, pest, nutrient, water stress)
4. Give simple next steps in plain language
5. Speak the answer back (text-to-speech)

This is NOT a final diagnosis engine. It’s guidance + escalation:
- Low-risk first steps (remove infected leaves, improve airflow, water early morning, etc.)
- Safety notes for pesticide use
- “Go see a local agronomist / extension officer” when uncertain

## Core modules
### `voice_of_the_farmer.py`
Takes farmer audio and turns it into text.
(Uses a mock speech recognizer by default so the project runs offline.)

### `eye_of_the_agronomist.py`
Analyzes the farmer’s description + photo metadata.
Calls a vision+LLM reasoning step (we ship a mock LLM so you can run locally).
Returns agronomy guidance text.

### `advisory_rules.py`
Adds safety language and escalation instructions to the LLM output:
- Wear PPE if spraying.
- Check local regulations.
- Bring a sample to an agronomist if we’re not confident.

### `voice_of_the_agronomist.py`
Converts final advice text into an audio file.
(Uses a mock TTS that just writes a placeholder .wav so you can run it offline.)

### `agri_assistant_app.py`
Gradio UI:
- Select crop
- Select plant part (leaf / pest / soil / fruit)
- Upload photo
- Speak or type the problem
- Get text + audio guidance

## Project structure

```text
AI-agriculture-assistant-1.0/
├── agri_assistant_app.py          # Main Gradio UI / orchestrator
├── eye_of_the_agronomist.py       # Vision + agronomy reasoning (LLM layer)
├── voice_of_the_farmer.py         # Speech-to-text
├── voice_of_the_agronomist.py     # Text-to-speech
├── advisory_rules.py              # Safety / escalation wrapper
├── llm_client.py                  # Mock and provider client wrappers
├── utils_audio.py                 # Helpers for audio file handling
├── requirements.txt
├── .env.example
├── sample_audio/
│   └── farmer_question_example.wav     (placeholder)
├── sample_images/
│   ├── tomato_leaf_spot.jpg            (placeholder)
│   ├── cotton_bollworm.jpg             (placeholder)
│   └── dry_soil_cracks.jpg             (placeholder)
└── output_audio/
    └── agri_reply_example.wav          (generated output goes here)

## steps to run
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agri_assistant_app.py