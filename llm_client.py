# llm_client.py
"""
LLM client with support for Groq API and offline mock.
Provides intelligent fallback and configurable prompting.
"""

import os
import re
import random
from typing import Optional
from dotenv import load_dotenv
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from logging_config import get_logger

logger = get_logger("llm_client")

load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "30"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


class GroqLLMClient:
    """LLM client for Groq API with retry logic and error handling."""

    def __init__(self, api_key: str):
        """Initialize with API key."""
        if not api_key:
            raise ValueError("GROQ_API_KEY cannot be empty")
        self.api_key = api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_crop_from_prompt(self, prompt: str) -> str:
        """
        Analyze crop issue using Groq API with automatic retry.
        
        Args:
            prompt: Agronomy analysis prompt
            
        Returns:
            LLM response text
        """
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Prompt cannot be empty")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        body = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior field agronomist. "
                        "You ALWAYS return short, actionable steps for farmers."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.4,
        }

        try:
            logger.debug(f"Calling Groq API (model: {GROQ_MODEL})")
            resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=GROQ_TIMEOUT)

            if resp.status_code != 200:
                error_msg = f"Groq API error: {resp.status_code} - {resp.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            data = resp.json()
            result = data["choices"][0]["message"]["content"]
            logger.info("Groq API response received successfully")
            return result

        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Groq response format: {data}")
            raise RuntimeError("Invalid response format from Groq API") from e
        except requests.RequestException as e:
            logger.error(f"Network error calling Groq API: {e}")
            raise


class MockLLMClient:
    """Mock LLM client for offline operation with heuristic responses."""

    def analyze_crop_from_prompt(self, prompt: str) -> str:
        """
        Analyze crop issue using keyword heuristics (offline, no API needed).
        
        Args:
            prompt: Agronomy analysis prompt
            
        Returns:
            Heuristic diagnosis text
        """
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Prompt cannot be empty")

        text = prompt.lower()

        # Extract the farmer's description
        farmer_text = ""
        m = re.search(r'farmer description of the problem:\s*"""(.*?)"""', prompt, flags=re.I | re.S)
        if m:
            farmer_text = m.group(1).strip().lower()

        if DEBUG:
            logger.debug(f"MockLLM extracted farmer text: '{farmer_text[:80]}'")

        # PRIORITY 1: Water stress
        water_keywords = ["dry", "wilting", "wilt", "drought", "cracked", "moisture", "parched"]
        if any(k in farmer_text for k in water_keywords):
            if DEBUG:
                logger.debug("MockLLM: Detected WATER STRESS")
            return f"""Looks like water stress.
1) Water deeply at the base in the early morning.
2) Mulch to preserve soil moisture.
3) Avoid frequent shallow watering.

Based on farmer observation: '{farmer_text[:100]}'"""

        # PRIORITY 2: Disease/spots
        disease_keywords = ["spot", "lesion", "blight", "mottle", "necrosis", "discolor", "disease"]
        if any(k in farmer_text for k in disease_keywords):
            if DEBUG:
                logger.debug("MockLLM: Detected DISEASE/SPOTS")
            return f"""Likely a leaf disease (possible fungal or bacterial).
1) Remove and safely dispose of the most affected leaves.
2) Improve airflow and avoid overhead watering.
3) If it worsens, photograph and consult a local agronomist before spraying.

Based on farmer observation: '{farmer_text[:100]}'"""

        # PRIORITY 3: Pests/insects
        pest_keywords = ["insect", "caterpillar", "hole", "worm", "borer", "pest", "bug", "larvae", "egg"]
        if any(k in farmer_text for k in pest_keywords):
            if DEBUG:
                logger.debug("MockLLM: Detected PEST/INSECT")
            return f"""Likely insect feeding damage.
1) Inspect undersides of leaves for eggs or caterpillars.
2) Handpick visible pests and remove them.
3) Use a spot spray of a low-toxicity insecticide only if damage is heavy.

Based on farmer observation: '{farmer_text[:100]}'"""

        # PRIORITY 4: Nutrient deficiency
        nutrient_keywords = ["yellow", "chlorosis", "pale", "nitrogen", "nutrient", "deficiency"]
        if any(k in farmer_text for k in nutrient_keywords):
            if DEBUG:
                logger.debug("MockLLM: Detected NUTRIENT DEFICIENCY")
            return f"""Likely nutrient deficiency (nitrogen or iron).
1) Apply a low-dose nitrogen fertilizer now.
2) Monitor new leaf color over 7–10 days.
3) Mulch and keep even soil moisture.

Based on farmer observation: '{farmer_text[:100]}'"""

        # FALLBACK: Generic templates
        if DEBUG:
            logger.debug("MockLLM: Using FALLBACK template")
        templates = [
            f"""This could be multiple issues. Here are immediate steps:
1) Remove the most damaged leaves carefully.
2) Inspect for pests and disease spots.
3) Check soil moisture and improve airflow.

Based on: '{farmer_text[:100]}'""",
            f"""I need more information, but try these steps:
1) Take a clear close-up photo of the affected area.
2) Remove heavily damaged tissue to prevent spread.
3) Show samples to a local agronomist if symptoms worsen.

Based on: '{farmer_text[:100]}'""",
        ]

        return random.choice(templates)


def get_llm_client():
    """Get configured LLM client (Groq or Mock)."""
    if GROQ_API_KEY:
        logger.info("Using Groq LLM client")
        return GroqLLMClient(GROQ_API_KEY)
    logger.warning("No GROQ_API_KEY found; using offline MockLLMClient")
    return MockLLMClient()
