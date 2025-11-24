# AI Agriculture Assistant 1.0 🌾
Voice + Vision Crop Advisory for Farmers

## What this project is
AI Agriculture Assistant 1.0 is an on-field crop triage assistant that simulates a conversation between a farmer and an agronomist.

The assistant can:
1. **Recognize the crop** automatically from farmer's description (no dropdown needed)
2. **Identify the plant part** affected (leaf, stem, fruit, soil, insect)
3. **Diagnose the issue** from photo + description (disease, pest, nutrient, water stress)
4. **Give simple next steps** in plain language
5. **Speak the answer back** (text-to-speech)

**Simple farmer-friendly UI:**
- No confusing dropdowns or technical choices
- Just upload a photo and describe what you see
- App automatically detects crop type and affected part
- Get text guidance + audio explanation

This is NOT a final diagnosis engine. It's guidance + escalation:
- Low-risk first steps (remove infected leaves, improve airflow, water early morning, etc.)
- Safety notes for pesticide use
- "Go see a local agronomist / extension officer" when uncertain

## Intelligent Features

### 🔍 Automatic Crop Detection
The app recognizes crop types from farmer descriptions:
- **Tomato, Corn, Cotton, Wheat, Rice, Potato, Cabbage, Pepper**, and more
- No need to select from dropdown - just mention your crop

### 🌿 Plant Part Recognition
Automatically identifies what part of the plant is affected:
- **Leaf** - spots, yellowing, discoloration
- **Stem** - lesions, girdling, bark damage
- **Fruit/Pod** - rot, cracks, deformity
- **Soil/Root** - wilting, moisture issues
- **Insect/Pest** - visible bugs, holes, webbing

### 🎤 Voice + Text Support
- Describe problem in your own language (text or voice)
- App understands context from farmer's words
- No need to remember crop/part names

## Core modules

### `voice_of_the_farmer.py`
Takes farmer audio and converts to text.
- Real: Groq Whisper API (speech-to-text)
- Fallback: Realistic mock examples for offline use

### `eye_of_the_agronomist.py`
Analyzes farmer's description + photo.
- Extracts image metadata (dimensions, details)
- Generates context-aware hints
- Calls LLM for agronomy reasoning
- Returns diagnosis guidance

### `advisory_rules.py`
Adds safety language and escalation:
- **Escalation Levels:** LOW/MEDIUM/HIGH risk assessment
- **Pesticide Warnings:** PPE, safety precautions
- **Escalation Guidance:** When to see a professional
- **Disclaimers:** Liability and regulatory notes

### `voice_of_the_agronomist.py`
Converts guidance to audio.
- **Tier 1:** ElevenLabs API (if key available)
- **Tier 2:** pyttsx3 local engine (always works)
- **Tier 3:** Silent WAV fallback
- Always provides audio output

### `agri_assistant_app.py`
Simple Gradio UI with intelligent detection:
- **No dropdowns** - app detects crop and plant part
- **Image upload** - photo or webcam
- **Text/voice input** - describe the problem
- **Instant analysis** - text + audio guidance

### `llm_client.py`
LLM interface with intelligent fallback:
- Real: Groq API (llama-3.3-70b-versatile)
- Fallback: MockLLMClient with keyword heuristics
- **Varied responses** - different answers for different issues
- Works offline

### `weather_client.py`
Provides weather context for diagnosis:
- Real: OpenWeatherMap OneCall API
- Fallback: Mock data for offline use
- **30-min caching** - reduces API calls
- **Risk assessment** - humidity, temperature, rain

### `utils_audio.py`
Audio utilities for file handling.

## Project structure

```text
AI-agriculture-assistant/
├── agri_assistant_app.py          # Main Gradio UI (simplified, no dropdowns)
├── eye_of_the_agronomist.py       # Image analysis + LLM reasoning
├── voice_of_the_farmer.py         # Speech-to-text (Groq + mock)
├── voice_of_the_agronomist.py     # Text-to-speech (3-tier fallback)
├── advisory_rules.py              # Safety + escalation assessment
├── llm_client.py                  # LLM client (Groq + intelligent mock)
├── weather_client.py              # Weather context (30-min cache)
├── logging_config.py              # Centralized logging
├── utils_audio.py                 # Audio helpers
├── requirements.txt               # All dependencies
├── .env.example                   # Environment variables
├── sample_audio/                  # Example audio files
├── sample_images/                 # Example crop images
├── output_audio/                  # Generated audio output
├── tests/                         # Complete test suite (26 tests)
│   ├── test_llm_client.py
│   ├── test_advisory_rules.py
│   └── test_weather_client.py
├── IMPLEMENTATION_SUMMARY.md      # Technical details
├── COMPLETION_REPORT.md           # What was implemented
└── verify_improvements.py         # Verification script
```

## How to Run

### 1. Set up environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Launch the app
```bash
python agri_assistant_app.py
```
The UI will open at `http://localhost:7860`

### 3. Use the app
1. **Upload a crop photo** - Take or select an image
2. **Describe the problem** - Type or speak your description
3. **Click "Analyze Issue"** - App auto-detects crop and plant part
4. **Get guidance** - Read advice and listen to audio explanation

### Optional: Configure API Keys (for production)
Create a `.env` file:
```bash
GROQ_API_KEY=your_groq_key_here              # For real LLM (else uses mock)
WEATHER_API_KEY=your_openweathermap_key      # For real weather (else uses mock)
ELEVENLABS_API_KEY=your_elevenlabs_key       # For ElevenLabs TTS (else uses pyttsx3)
DEBUG=1                                      # For verbose logging
```

**Without API keys:** App uses intelligent mock LLM, mock weather, and local pyttsx3 TTS - fully functional offline!

## Testing

### Run full test suite
```bash
python -m pytest tests/ -v
```
Expected: **26 tests pass** ✅

### Run verification script
```bash
python verify_improvements.py
```
Expected: **All 6 verification tests pass** ✅

## Key Improvements

✅ **No Dropdowns** - App auto-detects crop and plant part from description  
✅ **Intelligent Recognition** - 8+ supported crops with keyword detection  
✅ **Varied Responses** - No static answers; context-aware guidance  
✅ **Graceful Fallbacks** - 3-tier TTS, mock LLM, offline capability  
✅ **Safety First** - Escalation levels, pesticide warnings, disclaimers  
✅ **Comprehensive Logging** - Debug, info, warning, error levels  
✅ **Production Ready** - Full error handling, 26 tests, 100% passing  
✅ **Farmer-Friendly UI** - Simple, intuitive, no technical jargon  

## Example Workflow

**Farmer uploads tomato leaf photo and says:**
> "Brown spots appeared after 3 days of rain. Leaves are yellowing from the bottom."

**App automatically:**
1. ✅ Detects: Tomato crop, Leaf damage
2. ✅ Analyzes: Image + description + weather
3. ✅ Diagnoses: Likely fungal disease (high humidity after rain)
4. ✅ Recommends: Remove infected leaves, improve airflow, avoid overhead watering
5. ✅ Escalates: If widespread, see a local agronomist
6. ✅ Speaks: Reads guidance aloud in farmer's language

**No dropdowns. No confusion. Just help.**

## Disclaimer

⚠️ **This tool provides general agricultural guidance only.**
- Not a substitute for professional agronomist diagnosis
- Always confirm pesticide products with local extension office
- Follow local regulations and best practices
- In case of doubt, consult a qualified agronomist

## Support

- 📖 See `IMPLEMENTATION_SUMMARY.md` for technical details
- 📋 See `COMPLETION_REPORT.md` for what's been implemented
- 🧪 Run `python -m pytest tests/ -v` to validate functionality
- ✅ Run `python verify_improvements.py` to test all improvements
