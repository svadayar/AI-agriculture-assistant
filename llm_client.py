"""
llm_client.py
LLM client wrappers.
Currently includes a MockLLMClient so the app can run offline.

In production:
- Replace MockLLMClient with real vision-capable LLM calls
  (Groq, OpenAI GPT-4o mini w/vision, etc.).
"""


class MockLLMClient:
    """
    Offline fallback.
    We pretend to "analyze" the image and farmer text, then return a short diagnosis-style answer.
    """

    def analyze_crop(
        self,
        farmer_text: str,
        crop_type: str,
        plant_part: str,
        region_hint: str,
        img_b64: str,
    ) -> str:
        # Very lightweight heuristic just to sound relevant
        # You can customize this to impress in demos :)
        base_issue = "leaf spots after rain" if "spot" in farmer_text.lower() or "rain" in farmer_text.lower() else "stress"

        if base_issue == "leaf spots after rain":
            answer = (
                f"It looks like a possible fungal leaf issue on {crop_type}. "
                "This often spreads in warm, wet weather. "
                "Remove the worst leaves so the fungus doesn't spread. "
                "Do not water from above. Water at the base in the early morning. "
                "Improve airflow by trimming the lower leaves so they don't touch wet soil. "
                "If many plants are affected, you may need a copper-based fungicide, "
                "but confirm with a local agronomist before spraying."
            )
        else:
            answer = (
                f"The {plant_part} looks stressed. Check if the soil is too dry or compacted. "
                "Water slowly in early morning so roots get moisture, not mid-day sun. "
                "If leaves curl or turn yellow from the bottom up, it might be nutrient deficiency. "
                "Add balanced fertilizer or compost, but avoid over-fertilizing all at once."
            )

        # We also add a nudge to escalate if bad:
        answer += (
            " If the problem spreads fast across the field, talk to your local "
            "agriculture extension officer for an on-site check."
        )

        return answer


def get_llm_client():
    """
    In future:
    - detect if real API keys are present
    - return production LLM client
    For now we always return MockLLMClient.
    """
    return MockLLMClient()
