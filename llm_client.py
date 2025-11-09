# llm_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # you can change to llama3-8b-8192 if needed


class GroqLLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze_crop_from_prompt(self, prompt: str) -> str:
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

        resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)

        # DEBUG: show what Groq sent back if it's not OK
        if resp.status_code != 200:
            print("❌ Groq API error:")
            print("Status:", resp.status_code)
            print("Response:", resp.text)
            # return a safe fallback instead of crashing the app
            return (
                "I could not contact the AI model right now. "
                "Please check your GROQ_API_KEY or internet connection."
            )

        data = resp.json()

        # Groq follows the OpenAI-style response:
        # data["choices"][0]["message"]["content"]
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            print("⚠️ Unexpected Groq response format:", data)
            return "The AI model returned an unexpected response format."


class MockLLMClient:
    def analyze_crop_from_prompt(self, prompt: str) -> str:
        # very basic fallback
        return (
            "It looks like the plant is stressed. Start with low-risk actions: "
            "remove the worst leaves, avoid watering on leaves, and improve airflow. "
            "If it spreads fast, show the sample to a local agronomist."
        )


def get_llm_client():
    if GROQ_API_KEY:
        return GroqLLMClient(GROQ_API_KEY)
    return MockLLMClient()
