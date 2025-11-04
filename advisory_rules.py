"""
advisory_rules.py
Adds pesticide safety messages, escalation guidance, and general disclaimer
to the agronomy answer text before we return it to the farmer.
"""


def _needs_pesticide_disclaimer(text: str) -> bool:
    pesticide_keywords = [
        "spray", "fungicide", "insecticide", "pesticide", "treat with",
        "apply chemical", "copper", "neem", "imidacloprid", "pyrethrin"
    ]
    lowered = text.lower()
    return any(word in lowered for word in pesticide_keywords)


def _sounds_uncertain(text: str) -> bool:
    hedges = [
        "not sure", "could be", "might be", "possibly",
        "unclear", "cannot confirm", "can't confirm",
        "looks similar to"
    ]
    lowered = text.lower()
    return any(h in lowered for h in hedges)


def apply_safety_and_escalation(raw_answer: str) -> str:
    """
    Takes the raw LLM answer and appends:
    - PPE/regulatory warning if chemicals are mentioned
    - escalation guidance if uncertain
    - always-on disclaimer
    """
    final_parts = [raw_answer.strip()]

    if _needs_pesticide_disclaimer(raw_answer):
        final_parts.append(
            "⚠ Before using any chemical: "
            "Read the product label, follow local regulations, wear gloves and mask, "
            "and avoid spraying in mid-day heat."
        )

    if _sounds_uncertain(raw_answer):
        final_parts.append(
            "Bring a fresh sample (leaf / fruit / insect) to a local agriculture "
            "extension officer or agronomist to confirm before treating your whole field."
        )

    final_parts.append(
        "This tool gives general crop guidance based on your description and photo. "
        "Always confirm pesticide products, rates, and local regulations with a "
        "licensed agronomist before spraying anything."
    )

    return "\n\n".join(final_parts)
