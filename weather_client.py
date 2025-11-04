"""
weather_client.py
Fetches local weather context for agronomy reasoning:
- humidity
- temperature
- recent rain / upcoming rain

We keep it lightweight: this is NOT full forecast modeling.
We just provide risk signals that the LLM can use.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

def fetch_weather_snapshot(lat: float, lon: float) -> dict:
    """
    Get current weather conditions and short outlook near the farm.
    Returns a dict with humidity, temp_c, rain_mm_last_hour, rain_mm_next_hour (if available).
    If no WEATHER_API_KEY is set, returns a safe fallback.
    """

    if not WEATHER_API_KEY:
        # Fallback so your pipeline doesn't break if key isn't set.
        return {
            "humidity": None,
            "temp_c": None,
            "rain_mm_last_hour": None,
            "rain_mm_next_hour": None,
            "summary_text": (
                "No live weather data. Assume normal humidity and typical temperature."
            ),
        }

    # Example with OpenWeatherMap current+minutely endpoint
    # You can switch this to any provider. Just keep return format the same.

    url = (
        "https://api.openweathermap.org/data/2.5/onecall"
        f"?lat={lat}&lon={lon}&exclude=daily,alerts&units=metric&appid={WEATHER_API_KEY}"
    )

    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return {
            "humidity": None,
            "temp_c": None,
            "rain_mm_last_hour": None,
            "rain_mm_next_hour": None,
            "summary_text": (
                "Weather service unavailable. Assume normal humidity and temperature."
            ),
        }

    data = resp.json()

    # current conditions
    current = data.get("current", {})
    humidity = current.get("humidity")  # %
    temp_c = current.get("temp")        # °C

    # rain in last hour
    rain_last_hour = None
    if "rain" in current and "1h" in current["rain"]:
        rain_last_hour = current["rain"]["1h"]  # mm

    # rain forecast in next ~hour (use minutely if available)
    rain_next_hour = None
    minutely = data.get("minutely", [])
    # sum next 60min precip
    if minutely:
        rain_next_hour = sum(p.get("precipitation", 0.0) for p in minutely[:60])

    # Build short agronomy-friendly summary
    risks = []
    if humidity and humidity >= 80:
        risks.append("High humidity can increase fungal disease risk.")
    if rain_last_hour and rain_last_hour > 0:
        risks.append("It recently rained, leaves may be wet.")
    if rain_next_hour and rain_next_hour > 0:
        risks.append("More rain likely soon, sprays may wash off.")
    if temp_c and temp_c >= 32:
        risks.append("High heat can stress plants and burn leaves if sprayed mid-day.")
    if temp_c and temp_c <= 10:
        risks.append("Low temperature can slow nutrient uptake.")

    if not risks:
        risks.append("No major immediate stress indicators from weather.")

    return {
        "humidity": humidity,
        "temp_c": temp_c,
        "rain_mm_last_hour": rain_last_hour,
        "rain_mm_next_hour": rain_next_hour,
        "summary_text": " ".join(risks),
    }
