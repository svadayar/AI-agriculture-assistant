# Code Review & Improvement Suggestions
## AI Agriculture Assistant 1.0

---

## 🎯 Overall Assessment
**Strengths:**
- Clean modular architecture with single-responsibility principle
- Good separation of concerns (voice → eye → reasoning → safety → voice)
- Graceful fallbacks for offline/mock operation
- Safety-first design with escalation guidance
- Error handling in critical paths (API calls, file I/O)

**Areas for Improvement:**
1. **Debug logging** – Remove or conditionally enable debug prints
2. **Input validation** – Add checks for None/empty inputs early
3. **Error handling** – More granular error messages and recovery
4. **Configuration** – Move magic strings to constants
5. **Documentation** – Add docstrings and type hints throughout
6. **Testing** – No unit tests; add pytest suite
7. **Performance** – Cache weather/image processing, optimize image handling
8. **Unused code** – Base64 encoding not used; image analysis incomplete

---

## 📋 Detailed Suggestions by File

### 1. **llm_client.py**
**Issues:**
- Debug prints (`[MockLLM]`) should be conditional or removed
- No logging module usage (prints are hard to control)
- MockLLMClient keywords not case-insensitive for some edge cases
- No retry logic for Groq API failures

**Improvements:**
```python
# Add logging instead of prints
import logging
logger = logging.getLogger(__name__)

# Make debug prints optional
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Add retry logic for transient failures
from tenacity import retry, stop_after_attempt, wait_exponential

# Type hints throughout
from typing import Optional
def analyze_crop_from_prompt(self, prompt: str) -> str:
    """Analyze crop issue from prompt text."""

# Add timeout validation
if len(prompt) > 10000:
    logger.warning("Prompt exceeds recommended length")
```

**Actionable changes:**
- Replace print statements with logging module
- Add `GROQ_MODEL` and `GROQ_TIMEOUT` to constants
- Add retry decorator to GroqLLMClient API calls
- Add type hints to all methods

---

### 2. **eye_of_the_agronomist.py**
**Issues:**
- `img_b64` is computed but never used (no vision API integration)
- `infer_image_hints()` tries PIL import but it's not in requirements.txt
- `extract_summary()` doesn't handle edge cases (very short responses, etc.)
- Debug print statements
- No validation of `image_path` existence before encoding

**Improvements:**
```python
# Validate file existence first
import os
def encode_image_to_base64(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    # ... rest of code

# Remove unused b64 or prepare for vision API
# img_b64 = encode_image_to_base64(image_path)
# Eventually: groq.multimodal_analyze(prompt, img_b64)

# Better edge case handling in extract_summary
def extract_summary(response: str, max_sentences: int = 2) -> str:
    if not response or len(response.strip()) == 0:
        return "No response available."
    sentences = re.split(r'(?<=[.!?])\s+', response.strip())
    if not sentences:
        return response[:100]  # Fallback to first 100 chars
    # ... rest of code

# Add logging instead of print
```

**Actionable changes:**
- Add file existence validation before base64 encoding
- Remove debug prints; use logging
- Handle empty/None responses gracefully
- Update extract_summary to handle edge cases
- Add type hints and docstrings

---

### 3. **agri_assistant_app.py**
**Issues:**
- No input validation on `crop_type`, `plant_part` before analysis
- `farmer_text` defaulting to "No description provided." might hide user error
- No try/except around analyze_handler; UI could hang on error
- Hard-coded file paths
- Minimal error messages to user

**Improvements:**
```python
# Add validation
VALID_CROPS = ["tomato", "corn", "cotton", "wheat", "rice", "other"]
VALID_PARTS = ["leaf", "stem", "fruit", "soil", "insect/pest"]

def analyze_handler(...):
    if crop_type not in VALID_CROPS:
        raise ValueError(f"Invalid crop type: {crop_type}")
    if plant_part not in VALID_PARTS:
        raise ValueError(f"Invalid plant part: {plant_part}")
    
    # Validate at least one input provided
    if not crop_image:
        return "Error: Please upload a crop image.", None
    if not farmer_text and not farmer_audio:
        return "Error: Please describe the problem (text or voice).", None
    
    try:
        # ... existing logic
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return f"Error during analysis: {str(e)}", None

# Move paths to constants
OUTPUT_AUDIO_DIR = os.getenv("OUTPUT_AUDIO_DIR", "output_audio")
OUTPUT_AUDIO_PATH = os.path.join(OUTPUT_AUDIO_DIR, "agri_reply.wav")
```

**Actionable changes:**
- Add input validation for crop_type and plant_part
- Add try/except around analyze_handler with user-friendly error messages
- Move file paths to constants at top
- Validate that at least one of (text, audio) is provided

---

### 4. **advisory_rules.py**
**Issues:**
- Only basic keyword matching; doesn't check for confidence levels
- No indication of which rule matched (hard to debug)
- Could benefit from structured escalation levels
- Disclaimer text is repetitive

**Improvements:**
```python
# Add escalation levels
from enum import Enum

class EscalationLevel(Enum):
    LOW = "low"           # Farmer can likely handle alone
    MEDIUM = "medium"     # Some risk; agronomist review recommended
    HIGH = "high"         # Definitely needs professional help
    UNKNOWN = "unknown"   # Can't assess

def _assess_escalation_level(raw_answer: str) -> EscalationLevel:
    """Determine severity to guide user."""
    text = raw_answer.lower()
    
    # High risk keywords
    if any(k in text for k in ["fungal blight", "severe infestation", "wilting widely"]):
        return EscalationLevel.HIGH
    
    # Medium risk
    if _sounds_uncertain(raw_answer) or _needs_pesticide_disclaimer(raw_answer):
        return EscalationLevel.MEDIUM
    
    return EscalationLevel.LOW

# Structure the output better
def apply_safety_and_escalation(raw_answer: str) -> str:
    """Add safety notes and escalation guidance."""
    parts = [raw_answer.strip()]
    
    level = _assess_escalation_level(raw_answer)
    
    if _needs_pesticide_disclaimer(raw_answer):
        parts.append("⚠️ PESTICIDE SAFETY:\n" + _pesticide_warning())
    
    if _sounds_uncertain(raw_answer):
        parts.append("❓ UNCERTAIN DIAGNOSIS:\n" + _escalation_guidance())
    
    # Add level-appropriate disclaimer
    parts.append(_get_disclaimer_for_level(level))
    
    return "\n\n".join(parts)
```

**Actionable changes:**
- Add EscalationLevel enum
- Create _assess_escalation_level() function
- Refactor disclaimers into separate helper functions
- Add structured escalation messaging

---

### 5. **voice_of_the_farmer.py**
**Issues:**
- Mock transcription returns hard-coded string (obviously fake)
- No logging; no indication it's a mock
- No actual STT integration (Whisper, Groq, etc.)

**Improvements:**
```python
import logging
logger = logging.getLogger(__name__)

def transcribe_farmer_audio(audio_path: str) -> str:
    """
    Convert farmer's audio to text using Groq's Whisper API.
    Falls back to mock if no API key or error occurs.
    """
    if not audio_path:
        return ""
    
    # Try real transcription first
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if groq_api_key:
        try:
            return _transcribe_with_groq(audio_path, groq_api_key)
        except Exception as e:
            logger.warning(f"Groq transcription failed: {e}. Using mock.")
    
    # Fallback mock
    logger.info("Using mock transcription (no GROQ_API_KEY set)")
    return _mock_transcription()

def _mock_transcription() -> str:
    """Return a realistic mock transcription."""
    examples = [
        "My tomato leaves have yellow spots after rain.",
        "I see holes in the leaves and small insects.",
        "The soil is very dry and plants are wilting.",
    ]
    import random
    return random.choice(examples)

def _transcribe_with_groq(audio_path: str, api_key: str) -> str:
    """Implement real Whisper transcription via Groq."""
    # ... implementation
```

**Actionable changes:**
- Add logging instead of silent mock
- Implement real Groq Whisper integration
- Add graceful fallback with varied examples
- Document the mock nature clearly

---

### 6. **voice_of_the_agronomist.py**
**Issues:**
- Only supports ElevenLabs (expensive SaaS)
- No local TTS option (offline capability)
- Fallback is silent WAV (user hears nothing)
- Error messages could be clearer

**Improvements:**
```python
import logging
logger = logging.getLogger(__name__)

# Add local TTS option via pyttsx3 (free, offline)
def _local_tts(text: str, output_path: str):
    """Fallback TTS using pyttsx3 (free, no API key needed)."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        logger.info(f"Local TTS created: {output_path}")
    except ImportError:
        logger.warning("pyttsx3 not installed. Skipping local TTS.")
        raise

def agronomist_response_to_speech(answer_text: str, output_path: str) -> str:
    """
    Try TTS in order: ElevenLabs → Local (pyttsx3) → Silent fallback.
    """
    ensure_dir(os.path.dirname(output_path))
    
    # 1. Try ElevenLabs if configured
    if os.getenv("ELEVENLABS_API_KEY") and os.getenv("ELEVENLABS_VOICE_ID"):
        try:
            _elevenlabs_tts(answer_text, output_path)
            _save_transcript(answer_text)
            logger.info(f"ElevenLabs TTS: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"ElevenLabs failed: {e}")
    
    # 2. Try local TTS
    try:
        _local_tts(answer_text, output_path)
        _save_transcript(answer_text)
        logger.info(f"Local TTS: {output_path}")
        return output_path
    except Exception as e:
        logger.warning(f"Local TTS failed: {e}")
    
    # 3. Fallback to silent
    logger.warning("All TTS failed. Using silent audio.")
    fallback = os.path.join(os.path.dirname(output_path), "fallback_silence.wav")
    write_silent_wav(fallback, seconds=2.0)
    _save_transcript(answer_text)
    return fallback

def _save_transcript(text: str):
    """Helper to save transcript for debugging."""
    transcript_path = os.path.join(OUTPUT_DIR, "agri_reply_transcript.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(text)
```

**Actionable changes:**
- Add pyttsx3 as local TTS fallback
- Implement 3-tier TTS strategy (ElevenLabs → Local → Silent)
- Add logging throughout
- Extract transcript saving to helper function
- Update requirements.txt with pyttsx3

---

### 7. **weather_client.py**
**Issues:**
- No caching (API called every time, wasteful)
- Hard-coded risk thresholds (humidity >= 80%, temp >= 32°C, etc.)
- URL construction error (missing `/` after `onecall`)
- No retry logic for transient API failures

**Improvements:**
```python
import logging
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

# Add configuration constants
WEATHER_CONFIG = {
    "CACHE_DURATION_MINUTES": 30,
    "HUMIDITY_HIGH_THRESHOLD": 80,
    "TEMP_HIGH_THRESHOLD": 32,
    "TEMP_LOW_THRESHOLD": 10,
    "RAIN_RISK_THRESHOLD_MM": 0.1,
}

# Add simple in-memory cache
_weather_cache = {}

def fetch_weather_snapshot(lat: float, lon: float) -> dict:
    """Fetch and cache weather for the location."""
    cache_key = f"{lat},{lon}"
    
    # Check cache
    if cache_key in _weather_cache:
        cached_time, cached_data = _weather_cache[cache_key]
        if datetime.now() - cached_time < timedelta(
            minutes=WEATHER_CONFIG["CACHE_DURATION_MINUTES"]
        ):
            logger.debug(f"Using cached weather for {cache_key}")
            return cached_data
    
    # Fetch fresh data
    data = _fetch_from_api(lat, lon)
    _weather_cache[cache_key] = (datetime.now(), data)
    return data

def _fetch_from_api(lat: float, lon: float) -> dict:
    """Fetch from OpenWeatherMap with retry."""
    if not WEATHER_API_KEY:
        logger.warning("No WEATHER_API_KEY set")
        return _fallback_response()
    
    # Fix URL construction
    url = (
        "https://api.openweathermap.org/data/2.5/onecall"
        f"?lat={lat}&lon={lon}&exclude=daily,alerts&units=metric&appid={WEATHER_API_KEY}"
    )
    
    # Add retry
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return _parse_response(resp.json())
        except requests.RequestException as e:
            logger.warning(f"Weather API attempt {attempt+1} failed: {e}")
    
    return _fallback_response()

def _parse_response(data: dict) -> dict:
    """Extract and format weather data."""
    current = data.get("current", {})
    humidity = current.get("humidity")
    temp_c = current.get("temp")
    
    # Use config thresholds
    risks = []
    if humidity and humidity >= WEATHER_CONFIG["HUMIDITY_HIGH_THRESHOLD"]:
        risks.append("High humidity increases fungal disease risk.")
    # ... rest of checks using config
    
    return {
        "humidity": humidity,
        "temp_c": temp_c,
        "rain_mm_last_hour": _get_rain_last_hour(data),
        "rain_mm_next_hour": _get_rain_next_hour(data),
        "summary_text": " ".join(risks) if risks else "No immediate weather stress.",
    }

def _fallback_response() -> dict:
    """Return safe fallback when API unavailable."""
    return {
        "humidity": None,
        "temp_c": None,
        "rain_mm_last_hour": None,
        "rain_mm_next_hour": None,
        "summary_text": "Weather data unavailable.",
    }
```

**Actionable changes:**
- Add simple in-memory caching with 30-min TTL
- Extract risk thresholds to WEATHER_CONFIG dict
- Fix URL construction (add missing `/`)
- Add retry logic with exponential backoff
- Refactor into smaller helper functions
- Add logging throughout

---

### 8. **utils_audio.py**
**Status:** Generally good, minimal changes needed

**Minor improvements:**
```python
import logging
logger = logging.getLogger(__name__)

def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    logger.debug(f"Ensured directory exists: {path}")

def write_silent_wav(filepath: str, seconds: float = 2.0, sample_rate: int = 16000) -> None:
    """
    Create a silent WAV file for fallback scenarios.
    
    Args:
        filepath: Path to write WAV to
        seconds: Duration in seconds
        sample_rate: Sample rate (Hz)
    """
    if seconds <= 0:
        raise ValueError("Duration must be positive")
    
    ensure_dir(os.path.dirname(filepath))
    num_samples = int(seconds * sample_rate)
    
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        
        for _ in range(num_samples):
            wf.writeframes(struct.pack('<h', 0))
    
    logger.info(f"Created silent WAV: {filepath} ({seconds}s)")
```

---

## 🔧 Implementation Priority

### High Priority (1-2 days)
1. Add logging module throughout (replace all prints)
2. Add input validation to agri_assistant_app.py
3. Remove debug prints from MockLLMClient
4. Add type hints and docstrings

### Medium Priority (2-3 days)
5. Add file existence checks (eye_of_the_agronomist.py)
6. Implement weather caching
7. Add try/except error handling in agri_assistant_app.py
8. Refactor advisory_rules.py with escalation levels

### Lower Priority (1 week)
9. Integrate real Groq Whisper transcription
10. Add local TTS fallback (pyttsx3)
11. Add unit tests (pytest)
12. Add retry logic to API calls

---

## 📊 Testing Recommendations

```python
# tests/test_llm_client.py
import pytest
from llm_client import MockLLMClient

@pytest.fixture
def mock_client():
    return MockLLMClient()

def test_water_stress_detection(mock_client):
    prompt = 'Farmer description of the problem:\n"""Soil is very dry, plants wilting."""'
    response = mock_client.analyze_crop_from_prompt(prompt)
    assert "water stress" in response.lower()

def test_disease_detection(mock_client):
    prompt = 'Farmer description of the problem:\n"""I see brown spots on leaves."""'
    response = mock_client.analyze_crop_from_prompt(prompt)
    assert "disease" in response.lower() or "fungal" in response.lower()

# tests/test_advisory_rules.py
def test_pesticide_warning_added():
    raw = "Use fungicide spray"
    result = apply_safety_and_escalation(raw)
    assert "PPE" in result or "gloves" in result
```

---

## 📦 Updated requirements.txt

```
gradio>=4.0
python-dotenv>=1.0
requests>=2.31
pyaudio>=0.2.13
SpeechRecognition>=3.10
soundfile>=0.12
pyttsx3>=2.90
pillow>=10.0
tenacity>=8.2
pytest>=7.4
```

---

## ✅ Summary

The codebase is well-architected and functional. Main gaps are:
- **Logging** over prints (for production quality)
- **Input validation** (prevent silent failures)
- **Error recovery** (graceful degradation)
- **Testing** (pytest suite)
- **Documentation** (type hints, docstrings)

Start with logging and validation, then add caching and better error handling. The foundation is solid!
