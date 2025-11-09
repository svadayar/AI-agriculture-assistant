# eye_of_the_agronomist.py
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
    image_hint: str,
) -> str:
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
    llm = get_llm_client()

    # image to b64 (for future vision models — Groq text endpoint won’t read it)
    img_b64 = encode_image_to_base64(image_path)

    # fetch weather
    weather_info = fetch_weather_snapshot(lat=lat, lon=lon)
    weather_summary = weather_info["summary_text"]

    # we can add a simple image hint for now
    image_hint = "Farmer uploaded a crop image. Inspect for spots, yellowing, pests, or dryness."

    prompt = build_agronomy_prompt(
        farmer_text=farmer_text,
        crop_type=crop_type,
        plant_part=plant_part,
        region_hint=REGION_HINT,
        weather_summary=weather_summary,
        image_hint=image_hint,
    )

    print("🧠 Final prompt to Groq:\n", prompt)

    raw_answer = llm.analyze_crop_from_prompt(prompt)
    return raw_answer
