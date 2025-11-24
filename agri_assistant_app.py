"""
agri_assistant_app.py
Gradio UI for AI Agriculture Assistant 1.0

Simplified, intelligent UI:
1. User uploads a photo (crop issue detection is automatic)
2. User describes the problem (text or voice)
3. App analyzes and returns guidance + audio
"""

import os
import re
import gradio as gr

from advisory_rules import apply_safety_and_escalation
from eye_of_the_agronomist import analyze_crop_issue
from voice_of_the_agronomist import agronomist_response_to_speech
from voice_of_the_farmer import transcribe_farmer_audio
from utils_audio import ensure_dir
from logging_config import get_logger

logger = get_logger("agri_assistant_app")

# Configuration constants
OUTPUT_AUDIO_DIR = os.getenv("OUTPUT_AUDIO_DIR", "output_audio")
OUTPUT_AUDIO_PATH = os.path.join(OUTPUT_AUDIO_DIR, "agri_reply.wav")

# Crop detection keywords for intelligent recognition
CROP_KEYWORDS = {
    "tomato": ["tomato", "tomatoes", "solanum", "nightshade"],
    "corn": ["corn", "maize", "zea mays", "grain", "stalk"],
    "cotton": ["cotton", "gossypium", "boll", "fiber"],
    "wheat": ["wheat", "grain", "triticum", "cereal"],
    "rice": ["rice", "paddy", "oryza", "grain"],
    "potato": ["potato", "spud", "solanum tuberosum", "tuber"],
    "cabbage": ["cabbage", "brassica", "cruciferous", "leafy"],
    "pepper": ["pepper", "capsicum", "chili", "bell"],
}

# Plant part detection keywords
PLANT_PART_KEYWORDS = {
    "leaf": ["leaf", "leaves", "foliage", "canopy", "yellowing", "spots", "discoloration", "necrosis"],
    "stem": ["stem", "stalk", "branch", "trunk", "bark", "girdling", "lesion"],
    "fruit": ["fruit", "pod", "boll", "ear", "head", "grain", "rot", "crack", "deform"],
    "soil": ["soil", "root", "ground", "earth", "wilting", "wilt", "moisture", "dry"],
    "insect/pest": ["insect", "pest", "bug", "worm", "beetle", "aphid", "caterpillar", "hole", "webbing", "egg"],
}

ensure_dir(OUTPUT_AUDIO_DIR)


def detect_crop_from_text(text: str) -> str:
    """
    Intelligently detect crop type from farmer's description.
    
    Args:
        text: Farmer's description of the problem
        
    Returns:
        Detected crop type, or "other" if uncertain
    """
    if not text:
        return "other"
    
    text_lower = text.lower()
    
    # Score each crop based on keyword matches
    crop_scores = {}
    for crop, keywords in CROP_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            crop_scores[crop] = score
    
    if crop_scores:
        detected_crop = max(crop_scores, key=crop_scores.get)
        logger.info(f"Detected crop from text: {detected_crop}")
        return detected_crop
    
    return "other"


def detect_plant_part_from_text(text: str) -> str:
    """
    Intelligently detect plant part from farmer's description.
    
    Args:
        text: Farmer's description of the problem
        
    Returns:
        Detected plant part, or "leaf" as default
    """
    if not text:
        return "leaf"
    
    text_lower = text.lower()
    
    # Score each part based on keyword matches
    part_scores = {}
    for part, keywords in PLANT_PART_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            part_scores[part] = score
    
    if part_scores:
        detected_part = max(part_scores, key=part_scores.get)
        logger.info(f"Detected plant part from text: {detected_part}")
        return detected_part
    
    return "leaf"  # Default to leaf if uncertain




def analyze_handler(
    farmer_text: str,
    farmer_audio,
    crop_image
) -> tuple:
    """
    Simplified analysis handler. Automatically detects crop and plant part.
    
    Args:
        farmer_text: Text description from farmer
        farmer_audio: Audio file from farmer (optional)
        crop_image: Path to crop image file
        
    Returns:
        (advice_text, audio_path, detected_info) tuple
    """
    try:
        if not crop_image:
            error_msg = "📸 Please upload a crop image to analyze."
            logger.warning(error_msg)
            return error_msg, None, "No image provided"
        
        # Get farmer description (text or audio)
        if (not farmer_text or farmer_text.strip() == "") and farmer_audio is not None:
            logger.info("Transcribing farmer audio...")
            farmer_text = transcribe_farmer_audio(farmer_audio)
        
        if not farmer_text or farmer_text.strip() == "":
            error_msg = "🗣️ Please describe the problem (text or voice)."
            logger.warning(error_msg)
            return error_msg, None, "No description provided"
        
        # Intelligently detect crop and plant part from description
        detected_crop = detect_crop_from_text(farmer_text)
        detected_part = detect_plant_part_from_text(farmer_text)
        
        detection_info = f"🔍 Detected: {detected_crop.title()} - {detected_part}"
        logger.info(f"Analysis started: crop={detected_crop}, part={detected_part}")
        
        # Step 1: Vision + LLM reasoning
        logger.debug("Calling crop issue analyzer...")
        raw_answer = analyze_crop_issue(
            image_path=crop_image,
            farmer_text=farmer_text,
            crop_type=detected_crop,
            plant_part=detected_part,
        )
        
        # Step 2: Add safety and escalation guidance
        logger.debug("Applying safety rules...")
        safe_answer = apply_safety_and_escalation(raw_answer)
        
        # Step 3: Synthesize audio
        logger.debug("Generating speech...")
        preferred_audio_path = OUTPUT_AUDIO_PATH
        # agronomist_response_to_speech may return a different path (local fallback), capture it
        try:
            returned_audio_path = agronomist_response_to_speech(safe_answer, preferred_audio_path)
        except Exception as e:
            logger.warning(f"TTS generation raised an error: {e}")
            returned_audio_path = preferred_audio_path

        # Prefer the returned path if present
        audio_path_to_read = returned_audio_path or preferred_audio_path

        # Wait shortly for the file to be written to disk (pyttsx3 may write asynchronously)
        try:
            import time
            wait_seconds = 3.0
            interval = 0.2
            elapsed = 0.0
            while (not os.path.exists(audio_path_to_read) or os.path.getsize(audio_path_to_read) == 0) and elapsed < wait_seconds:
                time.sleep(interval)
                elapsed += interval
        except Exception:
            # best-effort wait; proceed to read and handle errors below
            pass

        # Read audio file and return as tuple for Gradio
        try:
            import soundfile as sf
            audio_data, sample_rate = sf.read(audio_path_to_read)
            logger.info(f"Analysis complete. Returning audio from {audio_path_to_read}")
            return safe_answer, (sample_rate, audio_data), detection_info
        except ImportError:
            logger.warning("soundfile not available, returning file path")
            return safe_answer, audio_path_to_read, detection_info
        except Exception as e:
            logger.warning(f"Could not read audio file {audio_path_to_read}: {e}")
            # Fall back to returning the file path so Gradio can still attempt playback
            return safe_answer, audio_path_to_read, detection_info
    
    except Exception as e:
        error_msg = f"❌ Analysis failed: {str(e)}"
        logger.error(f"{error_msg}\n{type(e).__name__}: {e}", exc_info=True)
        return error_msg, None, "Error occurred"


def build_interface():
    """Build a simplified, farmer-friendly UI with intelligent crop detection."""
    with gr.Blocks(title="AI Agriculture Assistant 1.0", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# 🌾 AI Agriculture Assistant\n\n"
            "**Get instant crop guidance. Just upload a photo and describe the problem.**\n\n"
            "The app will automatically recognize your crop and the issue. "
            "You'll get text guidance and spoken advice.\n\n"
            "⚠️ *Disclaimer: This tool gives general guidance only. "
            "Always consult a local agronomist for confirmed diagnosis and treatment.*"
        )

        with gr.Group():
            gr.Markdown("### 📸 Step 1: Upload Crop Image")
            crop_image = gr.Image(
                label="Take or upload a photo of the problem area",
                type="filepath",
                sources=["upload", "webcam"],
            )

        with gr.Group():
            gr.Markdown("### 🗣️ Step 2: Describe What You See")
            
            farmer_text = gr.Textbox(
                label="Type a description (or skip if using voice)",
                placeholder="e.g., Brown spots on tomato leaves, appeared after rain, yellowing from bottom",
                lines=3,
                info="Mention the crop type, symptoms, and when it started"
            )

            farmer_audio = gr.Audio(
                label="Or speak your description",
                type="filepath",
                sources=["microphone"]
            )

        with gr.Group():
            analyze_button = gr.Button(
                "🔍 Analyze Issue",
                size="lg",
                variant="primary"
            )

        with gr.Group():
            gr.Markdown("### 📋 Results")
            
            detection_output = gr.Textbox(
                label="Crop Detection",
                interactive=False,
                value="Upload image and describe to detect crop"
            )
            
            advice_output = gr.Textbox(
                label="Assistant Guidance",
                lines=10,
                interactive=False,
                show_copy_button=True
            )

            audio_output = gr.Audio(
                label="🔊 Listen to Guidance",
                type="numpy",
                interactive=False
            )

        # Connect button to analysis handler
        analyze_button.click(
            fn=analyze_handler,
            inputs=[farmer_text, farmer_audio, crop_image],
            outputs=[advice_output, audio_output, detection_output]
        )
        
        gr.Markdown(
            "---\n\n"
            "### 💡 How to get best results:\n"
            "1. **Good lighting** - Natural light works best\n"
            "2. **Close-up photo** - Focus on the affected area\n"
            "3. **Describe symptoms** - Brown spots? Wilting? Insects visible?\n"
            "4. **Mention timing** - When did you first notice this? After rain? Heat wave?\n"
            "5. **Note crop type** - Helps us be more accurate\n\n"
            "**Supported crops:** Tomato, Corn, Cotton, Wheat, Rice, Potato, Cabbage, Pepper, and others"
        )

    return demo


if __name__ == "__main__":
    ui = build_interface()
    ui.launch(server_name="127.0.0.1", server_port=7860, share=False, show_error=True)
