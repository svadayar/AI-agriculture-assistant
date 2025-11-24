"""
tests/test_advisory_rules.py
Unit tests for safety and escalation rules.
"""

import pytest
from advisory_rules import (
    _needs_pesticide_disclaimer,
    _sounds_uncertain,
    _assess_escalation_level,
    apply_safety_and_escalation,
    EscalationLevel,
)


class TestAdvisoryRules:
    """Test advisory rules and escalation logic."""
    
    def test_pesticide_warning_detected(self):
        """Should detect pesticide keywords."""
        text = "Use fungicide spray"
        assert _needs_pesticide_disclaimer(text) is True
    
    def test_no_pesticide_warning(self):
        """Should not flag non-pesticide responses."""
        text = "Remove the affected leaves and improve airflow."
        assert _needs_pesticide_disclaimer(text) is False
    
    def test_uncertainty_detection(self):
        """Should detect uncertain language."""
        text = "This could be a fungal disease, but I'm not sure."
        assert _sounds_uncertain(text) is True
    
    def test_no_uncertainty(self):
        """Should not flag confident responses."""
        text = "This is definitely water stress."
        assert _sounds_uncertain(text) is False
    
    def test_escalation_level_high(self):
        """Should assess HIGH risk level."""
        text = "This is a severe widespread infection that requires professional help."
        level = _assess_escalation_level(text)
        assert level == EscalationLevel.HIGH
    
    def test_escalation_level_medium(self):
        """Should assess MEDIUM risk level."""
        text = "This could be a fungal disease. Use a fungicide spray."
        level = _assess_escalation_level(text)
        assert level == EscalationLevel.MEDIUM
    
    def test_escalation_level_low(self):
        """Should assess LOW risk level."""
        text = "Remove the damaged leaves and improve airflow."
        level = _assess_escalation_level(text)
        assert level == EscalationLevel.LOW
    
    def test_apply_safety_adds_disclaimer(self):
        """Should add disclaimer to all responses."""
        raw = "This looks like water stress."
        result = apply_safety_and_escalation(raw)
        assert "DISCLAIMER" in result or "disclaimer" in result
        assert "water stress" in result
    
    def test_apply_safety_adds_pesticide_warning(self):
        """Should add pesticide warning when chemicals mentioned."""
        raw = "Use fungicide spray on affected leaves."
        result = apply_safety_and_escalation(raw)
        assert "PESTICIDE" in result or "pesticide" in result
        assert "gloves" in result or "mask" in result
    
    def test_apply_safety_adds_escalation_guidance(self):
        """Should add escalation guidance when uncertain."""
        raw = "This could be a fungal or bacterial disease."
        result = apply_safety_and_escalation(raw)
        assert "UNCERTAIN" in result or "agronomist" in result
    
    def test_apply_safety_empty_response(self):
        """Should handle empty responses gracefully."""
        result = apply_safety_and_escalation("")
        assert len(result) > 0
        assert "Unable" in result or "Error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
