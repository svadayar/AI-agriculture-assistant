"""
eye_of_the_agronomist.py
Analyze crop images + farmer context using a vision-capable LLM.
Now enriched with local weather context.
"""

import base64
import os
from dotenv import load_dotenv

from llm_client import get_llm_client
from weather_client import fetch_weather_snapshot

load_dotenv()

REGION_HINT = os.getenv("REGION_HINT", "unspecified region")


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_agronomy_prompt(
    farmer_text: str,
    crop_type: str,
    plant_part: str,
    region_hint: str,
    weather_summary: str,
) -> str:
    """
    This prompt is what we'll (eventually) send to a real vision+LLM.
    It includes farmer observation, plant info, AND current weather risk factors.
    """
    return f"""
You are an experienced field agronomist helping a farmer.

Region: {region_hint}
Weather context: {weather_summary}

Crop: {crop_type}
Plant part shown in the image: {plant_part}

Farmer said:
\"\"\"{farmer_text}\"\"\"

Your job:
1. Identify the most likely issue: disease, pest, nutrient deficiency, water stress, or other.
2. Consider humidity, rain, temperature from the weather context (fungal risk, heat stress, spray wash-off).
3. Give simple next steps in short, clear sentences.
4. Start with low-risk actions (remove damaged leaves, adjust watering, improve airflow).
5. If you mention chemicals, say they must confirm with a local agronomist first.
6. If you are unsure, clearly say you are not fully sure and tell them to take a sample to an agronomist.

Return plain text, farmer-friendly language.
    """.strip()


def analyze_crop_issue(
    image_path: str,
    farmer_text: str,
    crop_type: str,
    plant_part: str,
    lat: float = 35.5,
    lon: float = -80.0,
):
    """
    Main entry point called by the UI.
    Returns raw (pre-safety-filtered) agronomy guidance string.

    image_path: local file path from Gradio upload
    farmer_text: transcribed farmer description or typed text
    crop_type: "tomato", "corn", etc.
    plant_part: "leaf", "soil", "fruit", "insect/pest", etc.
    lat/lon: location of the farm/plot so we can fetch weather context
             (for MVP you can hardcode one region)
    """

    # 1. get model client (mock for now)
    llm_client = get_llm_client()

    # 2. encode image into base64 (for future real vision model use)
    img_b64 = encode_image_to_base64(image_path)

    # 3. get weather context
    weather_info = fetch_weather_snapshot(lat=lat, lon=lon)
    weather_summary = weather_info["summary_text"]

    # 4. build structured agronomy+weather prompt
    _prompt_debug = build_agronomy_prompt(
        farmer_text=farmer_text,
        crop_type=crop_type,
        plant_part=plant_part,
        region_hint=REGION_HINT,
        weather_summary=weather_summary,
    )

    # 5. call mock LLM client right now
    #    (in production, you'd pass _prompt_debug + img_b64 to Groq/Gemini Vision)
    raw_answer = llm_client.analyze_crop(
        farmer_text=farmer_text,
        crop_type=crop_type,
        plant_part=plant_part,
        region_hint=REGION_HINT,
        img_b64=img_b64,
    )

    # 6. optionally, you could inject weather hints yourself even before LLM:
    #    for example: if humidity is super high and crop_type is tomato
    #    you could append fungal warning.
    #    We'll leave that to the LLM for now.

    return raw_answer
