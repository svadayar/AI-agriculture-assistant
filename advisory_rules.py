"""
advisory_rules.py
Adds pesticide safety messages, escalation guidance, and general disclaimer
to the agronomy answer text before we return it to the farmer.
Includes escalation level assessment.
"""

from enum import Enum
from logging_config import get_logger

logger = get_logger("advisory_rules")


class EscalationLevel(Enum):
    """Risk levels for crop issues."""
    LOW = "low"               # Farmer can likely handle alone
    MEDIUM = "medium"         # Some risk; agronomist review recommended
    HIGH = "high"             # Definitely needs professional help
    UNKNOWN = "unknown"       # Can't assess


def _needs_pesticide_disclaimer(text: str) -> bool:
    """Check if response mentions chemical treatments."""
    pesticide_keywords = [
        "spray", "fungicide", "insecticide", "pesticide", "treat with",
        "apply chemical", "copper", "neem", "imidacloprid", "pyrethrin"
    ]
    lowered = text.lower()
    return any(word in lowered for word in pesticide_keywords)


def _sounds_uncertain(text: str) -> bool:
    """Check if response expresses uncertainty."""
    hedges = [
        "not sure", "could be", "might be", "possibly",
        "unclear", "cannot confirm", "can't confirm",
        "looks similar to", "resembles", "possibly indicates"
    ]
    lowered = text.lower()
    return any(h in lowered for h in hedges)


def _assess_escalation_level(raw_answer: str) -> EscalationLevel:
    """
    Determine severity level to guide user response.
    
    Args:
        raw_answer: LLM response text
        
    Returns:
        EscalationLevel enum value
    """
    text = raw_answer.lower()
    
    # High risk keywords
    high_risk_keywords = [
        "severe", "widespread", "blighting", "wilting widely",
        "heavy infestation", "complete loss", "should see agronomist",
        "definitely consult", "serious concern"
    ]
    
    if any(k in text for k in high_risk_keywords):
        return EscalationLevel.HIGH
    
    # Medium risk: chemicals or uncertainty
    if _needs_pesticide_disclaimer(text) or _sounds_uncertain(text):
        return EscalationLevel.MEDIUM
    
    return EscalationLevel.LOW


def _pesticide_warning() -> str:
    """Return pesticide safety message."""
    return (
        "⚠️ PESTICIDE SAFETY:\n"
        "- Read the product label carefully\n"
        "- Follow local regulations and restrictions\n"
        "- Wear gloves, mask, and eye protection\n"
        "- Avoid spraying in mid-day heat or before rain\n"
        "- Keep children and pets away from treated areas\n"
        "- Dispose of empty containers properly"
    )


def _escalation_guidance() -> str:
    """Return escalation message for uncertain diagnosis."""
    return (
        "❓ UNCERTAIN DIAGNOSIS:\n"
        "The diagnosis above is not definitive. Before taking action:\n"
        "1) Take clear, close-up photos of affected areas\n"
        "2) Bring a fresh sample (leaf/fruit/insect) to your local:\n"
        "   - Agriculture extension office\n"
        "   - Cooperative farming service\n"
        "   - Licensed agronomist\n"
        "3) Let them confirm before treating the entire field"
    )


def _get_disclaimer_for_level(level: EscalationLevel) -> str:
    """Return level-appropriate disclaimer."""
    if level == EscalationLevel.HIGH:
        return (
            "⚠️ IMPORTANT DISCLAIMER:\n"
            "This condition may require professional intervention. "
            "Bring samples to a licensed agronomist or extension officer "
            "before attempting treatment. Crop loss may occur if action is delayed."
        )
    elif level == EscalationLevel.MEDIUM:
        return (
            "⚠️ DISCLAIMER:\n"
            "This tool provides general crop guidance. "
            "Always confirm pesticide products, rates, and safety measures "
            "with a licensed agronomist before applying any chemicals. "
            "Follow local regulations and product labels."
        )
    else:
        return (
            "📋 DISCLAIMER:\n"
            "This tool provides general crop guidance based on your description. "
            "While these recommendations are low-risk, monitor your field closely "
            "and consult an agronomist if the problem persists or worsens."
        )


def apply_safety_and_escalation(raw_answer: str) -> str:
    """
    Takes the raw LLM answer and appends:
    - PPE/regulatory warning if chemicals are mentioned
    - Escalation guidance if uncertain
    - Level-appropriate disclaimer
    
    Args:
        raw_answer: Raw LLM response text
        
    Returns:
        Final answer with safety notes and disclaimers
    """
    if not raw_answer:
        logger.warning("Empty response to apply safety rules to")
        return "Unable to process the analysis. Please try again."
    
    final_parts = [raw_answer.strip()]
    
    # Assess severity
    level = _assess_escalation_level(raw_answer)
    logger.info(f"Escalation level: {level.value}")
    
    # Add pesticide warning if needed
    if _needs_pesticide_disclaimer(raw_answer):
        final_parts.append(_pesticide_warning())
    
    # Add escalation guidance if uncertain
    if _sounds_uncertain(raw_answer):
        final_parts.append(_escalation_guidance())
    
    # Add level-appropriate final disclaimer
    final_parts.append(_get_disclaimer_for_level(level))
    
    result = "\n\n".join(final_parts)
    logger.info(f"Safety rules applied. Final length: {len(result)} chars")
    
    return result
