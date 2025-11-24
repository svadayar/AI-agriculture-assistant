# eye_of_the_agronomist.py
"""
Crop issue analysis using image + description + weather context.
Calls LLM for agronomy reasoning.
"""

import base64
import os
import re
from typing import Optional
from dotenv import load_dotenv

from llm_client import get_llm_client
from weather_client import fetch_weather_snapshot
from logging_config import get_logger

logger = get_logger("eye_of_the_agronomist")

load_dotenv()

REGION_HINT = os.getenv("REGION_HINT", "unspecified region")


def infer_image_hints(image_path: str, plant_part: str) -> str:
    """
    Generate context-aware image hints based on plant part.
    Can be extended to analyze actual image pixels if PIL is available.
    
    Args:
        image_path: Path to the image file
        plant_part: Type of plant part in image (leaf, pest, soil, fruit)
        
    Returns:
        Human-readable hint text
    """
    hints = []
    
    if plant_part.lower() == "leaf":
        hints.append("Look for yellowing, spots, necrosis, or unusual discoloration.")
    elif plant_part.lower() == "pest":
        hints.append("Look for insects, webbing, eggs, or visible feeding damage.")
    elif plant_part.lower() == "soil":
        hints.append("Check for compaction, cracking, color, and moisture state.")
    elif plant_part.lower() == "fruit":
        hints.append("Look for rot, cracks, discoloration, or deformity.")
    
    # Try to get image dimensions for context
    try:
        from PIL import Image
        if os.path.exists(image_path):
            img = Image.open(image_path)
            if img.size[0] > 0 and img.size[1] > 0:
                hints.append(f"Image dimensions: {img.size[0]}×{img.size[1]}.")
                logger.debug(f"Image info: {img.format} {img.size}")
    except ImportError:
        logger.debug("PIL not available; skipping image dimension check")
    except Exception as e:
        logger.warning(f"Error reading image: {e}")
    
    return " ".join(hints) if hints else "Farmer uploaded a crop image."


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image file to base64 string (for future vision APIs).
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded image string
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        IOError: If file cannot be read
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except IOError as e:
        logger.error(f"Cannot read image file {image_path}: {e}")
        raise


def build_agronomy_prompt(
    farmer_text: str,
    crop_type: str,
    plant_part: str,
    region_hint: str,
    weather_summary: str,
    image_hint: str,
) -> str:
    """Build the LLM prompt with all context."""
    return f"""
Farmer location/region: {region_hint}
Weather right now: {weather_summary}

Crop: {crop_type}
Plant part shown: {plant_part}

Farmer description of the problem:
\"\"\"{farmer_text}\"\"\"

Image notes:
{image_hint}

Your tasks:
1. Say the MOST LIKELY problem (disease, pest, nutrient deficiency, water stress, mechanical damage).
2. Explain WHY this is likely, using weather if relevant (e.g. high humidity → fungal).
3. Give 3–5 short, numbered actions the farmer can do right now with low cost.
4. If you mention spraying, tell them to confirm locally and avoid spraying before rain.
5. If you are not sure, say so and tell them to take a sample to a local agronomist.

Keep it short, farmer-friendly, no jargon.
""".strip()


def analyze_crop_issue(
    image_path: str,
    farmer_text: str,
    crop_type: str,
    plant_part: str,
    lat: float = 35.5,
    lon: float = -80.0,
):
    """Analyze crop issue with comprehensive error handling."""
    try:
        llm = get_llm_client()

        # image to b64 (for future vision models — Groq text endpoint won't read it)
        img_b64 = encode_image_to_base64(image_path)

        # fetch weather
        weather_info = fetch_weather_snapshot(lat=lat, lon=lon)
        weather_summary = weather_info["summary_text"]

        # generate context-aware image hints
        image_hint = infer_image_hints(image_path, plant_part)

        prompt = build_agronomy_prompt(
            farmer_text=farmer_text,
            crop_type=crop_type,
            plant_part=plant_part,
            region_hint=REGION_HINT,
            weather_summary=weather_summary,
            image_hint=image_hint,
        )

        logger.debug(f"Sending prompt to LLM ({len(prompt)} chars)")
        raw_answer = llm.analyze_crop_from_prompt(prompt)
        
        # Extract summary
        summary = extract_summary(raw_answer)
        logger.info(f"Analysis complete. Summary: {summary}")
        
        return raw_answer

    except Exception as e:
        logger.error(f"Crop analysis failed: {e}", exc_info=True)
        raise


def extract_summary(response: str, max_sentences: int = 2) -> str:
    """
    Extract a brief summary from LLM response for UI display.
    
    Args:
        response: Full LLM response text
        max_sentences: Number of sentences to extract
        
    Returns:
        Summary text (or fallback if response is invalid)
    """
    if not response or len(response.strip()) == 0:
        return "No response available."
    
    try:
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', response.strip())
        
        if not sentences:
            return response[:100].strip()
        
        summary = " ".join(sentences[:max_sentences])
        if len(sentences) > max_sentences:
            summary += "..."
        
        return summary
    except Exception as e:
        logger.warning(f"Error extracting summary: {e}")
        return response[:100].strip()
