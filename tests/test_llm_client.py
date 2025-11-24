"""
tests/test_llm_client.py
Unit tests for LLM client functionality.
"""

import pytest
from llm_client import MockLLMClient


@pytest.fixture
def mock_client():
    return MockLLMClient()


class TestMockLLMClient:
    """Test MockLLMClient heuristic responses."""
    
    def test_water_stress_detection(self, mock_client):
        """Should detect water stress keywords."""
        prompt = 'Farmer description of the problem:\n"""Soil is very dry, plants wilting."""'
        response = mock_client.analyze_crop_from_prompt(prompt)
        assert "water stress" in response.lower()
        assert "water deeply" in response.lower()
    
    def test_disease_detection(self, mock_client):
        """Should detect disease/spot keywords."""
        prompt = 'Farmer description of the problem:\n"""I see brown spots on leaves."""'
        response = mock_client.analyze_crop_from_prompt(prompt)
        assert "disease" in response.lower() or "fungal" in response.lower()
        assert "remove" in response.lower()
    
    def test_pest_detection(self, mock_client):
        """Should detect insect/pest keywords."""
        prompt = 'Farmer description of the problem:\n"""There are holes and caterpillars."""'
        response = mock_client.analyze_crop_from_prompt(prompt)
        assert "insect" in response.lower() or "pest" in response.lower()
        assert "handpick" in response.lower()
    
    def test_nutrient_detection(self, mock_client):
        """Should detect nutrient deficiency keywords."""
        prompt = 'Farmer description of the problem:\n"""Leaves are yellowing."""'
        response = mock_client.analyze_crop_from_prompt(prompt)
        assert "nutrient" in response.lower() or "nitrogen" in response.lower()
        assert "fertilizer" in response.lower()
    
    def test_empty_prompt_raises_error(self, mock_client):
        """Should raise ValueError for empty prompt."""
        with pytest.raises(ValueError):
            mock_client.analyze_crop_from_prompt("")
    
    def test_fallback_response_for_unknown(self, mock_client):
        """Should return fallback for unknown keywords."""
        prompt = 'Farmer description of the problem:\n"""Plant looks strange."""'
        response = mock_client.analyze_crop_from_prompt(prompt)
        assert len(response) > 0
        # Should include extracted farmer text
        assert "based on" in response.lower() or "strange" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
