"""
weather_client.py
Fetches local weather context for agronomy reasoning:
- humidity
- temperature  
- recent rain / upcoming rain

With caching and retry logic for efficiency.
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from logging_config import get_logger

logger = get_logger("weather_client")

load_dotenv()

# Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# Risk thresholds (configurable)
WEATHER_CONFIG = {
    "CACHE_DURATION_MINUTES": 30,
    "HUMIDITY_HIGH_THRESHOLD": 80,
    "TEMP_HIGH_THRESHOLD": 32,
    "TEMP_LOW_THRESHOLD": 10,
    "RAIN_RISK_THRESHOLD_MM": 0.1,
    "API_TIMEOUT": 10,
    "RETRY_ATTEMPTS": 3,
}

# Simple in-memory cache
_weather_cache = {}


def fetch_weather_snapshot(lat: float, lon: float) -> dict:
    """
    Get current weather conditions with caching.
    Returns a dict with humidity, temp_c, rain info, and risk summary.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary with weather data and risk summary
    """
    cache_key = f"{lat},{lon}"
    
    # Check cache
    if cache_key in _weather_cache:
        cached_time, cached_data = _weather_cache[cache_key]
        age_minutes = (datetime.now() - cached_time).total_seconds() / 60
        
        if age_minutes < WEATHER_CONFIG["CACHE_DURATION_MINUTES"]:
            logger.debug(f"Using cached weather for {cache_key} ({age_minutes:.1f}m old)")
            return cached_data
        else:
            logger.debug(f"Cache expired for {cache_key}")
            del _weather_cache[cache_key]
    
    # Fetch fresh data
    data = _fetch_weather_with_retry(lat, lon)
    
    # Store in cache
    _weather_cache[cache_key] = (datetime.now(), data)
    logger.debug(f"Cached weather for {cache_key}")
    
    return data


def _fetch_weather_with_retry(lat: float, lon: float) -> dict:
    """
    Fetch weather with retry logic.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Weather data dictionary
    """
    if not WEATHER_API_KEY:
        logger.warning("No WEATHER_API_KEY set")
        return _fallback_response("Weather API not configured")
    
    for attempt in range(1, WEATHER_CONFIG["RETRY_ATTEMPTS"] + 1):
        try:
            logger.debug(f"Fetching weather (attempt {attempt}/{WEATHER_CONFIG['RETRY_ATTEMPTS']})")
            return _fetch_from_openweathermap(lat, lon)
        except requests.RequestException as e:
            logger.warning(f"Weather API attempt {attempt} failed: {e}")
            if attempt < WEATHER_CONFIG["RETRY_ATTEMPTS"]:
                continue
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            break
    
    return _fallback_response("Weather API unavailable")


def _fetch_from_openweathermap(lat: float, lon: float) -> dict:
    """
    Fetch from OpenWeatherMap OneCall API.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Parsed weather data
    """
    # Fix URL construction (add missing /)
    url = (
        "https://api.openweathermap.org/data/2.5/onecall"
        f"?lat={lat}&lon={lon}&exclude=daily,alerts&units=metric&appid={WEATHER_API_KEY}"
    )
    
    resp = requests.get(url, timeout=WEATHER_CONFIG["API_TIMEOUT"])
    resp.raise_for_status()
    
    return _parse_weather_response(resp.json())


def _parse_weather_response(data: dict) -> dict:
    """
    Extract and format weather data from OpenWeatherMap response.
    
    Args:
        data: API response JSON
        
    Returns:
        Formatted weather dictionary
    """
    current = data.get("current", {})
    humidity = current.get("humidity")  # %
    temp_c = current.get("temp")        # °C

    # Rain in last hour
    rain_last_hour = None
    if "rain" in current and "1h" in current["rain"]:
        rain_last_hour = current["rain"]["1h"]  # mm

    # Rain forecast in next hour (sum minutely precip)
    rain_next_hour = None
    minutely = data.get("minutely", [])
    if minutely:
        rain_next_hour = sum(p.get("precipitation", 0.0) for p in minutely[:60])

    # Build agronomy-friendly risk summary
    risks = _assess_weather_risks(humidity, temp_c, rain_last_hour, rain_next_hour)

    return {
        "humidity": humidity,
        "temp_c": temp_c,
        "rain_mm_last_hour": rain_last_hour,
        "rain_mm_next_hour": rain_next_hour,
        "summary_text": " ".join(risks) if risks else "No major immediate weather stress.",
    }


def _assess_weather_risks(humidity, temp_c, rain_last_hour, rain_next_hour) -> list:
    """
    Assess weather-based disease and stress risks.
    
    Args:
        humidity: Humidity percentage
        temp_c: Temperature in Celsius
        rain_last_hour: Rain in mm (last hour)
        rain_next_hour: Forecasted rain in mm (next hour)
        
    Returns:
        List of risk messages
    """
    risks = []
    
    if humidity and humidity >= WEATHER_CONFIG["HUMIDITY_HIGH_THRESHOLD"]:
        risks.append("High humidity can increase fungal disease risk.")
    
    if rain_last_hour and rain_last_hour > WEATHER_CONFIG["RAIN_RISK_THRESHOLD_MM"]:
        risks.append("It recently rained, leaves may be wet.")
    
    if rain_next_hour and rain_next_hour > WEATHER_CONFIG["RAIN_RISK_THRESHOLD_MM"]:
        risks.append("More rain likely soon, sprays may wash off.")
    
    if temp_c and temp_c >= WEATHER_CONFIG["TEMP_HIGH_THRESHOLD"]:
        risks.append("High heat can stress plants and burn leaves if sprayed mid-day.")
    
    if temp_c and temp_c <= WEATHER_CONFIG["TEMP_LOW_THRESHOLD"]:
        risks.append("Low temperature can slow nutrient uptake.")
    
    return risks


def _fallback_response(reason: str = "") -> dict:
    """
    Return safe fallback when weather data is unavailable.
    
    Args:
        reason: Why fallback was needed
        
    Returns:
        Default weather response
    """
    message = reason or "Weather data unavailable."
    logger.warning(f"Weather fallback: {message}")
    
    return {
        "humidity": None,
        "temp_c": None,
        "rain_mm_last_hour": None,
        "rain_mm_next_hour": None,
        "summary_text": message,
    }


def clear_cache() -> None:
    """Clear cached weather data (useful for testing)."""
    global _weather_cache
    _weather_cache.clear()
    logger.debug("Weather cache cleared")
