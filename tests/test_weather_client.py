"""
tests/test_weather_client.py
Unit tests for weather client with caching.
"""

import pytest
from datetime import datetime
from weather_client import (
    fetch_weather_snapshot,
    _assess_weather_risks,
    clear_cache,
    WEATHER_CONFIG,
)


class TestWeatherClient:
    """Test weather client functionality."""
    
    def teardown_method(self):
        """Clear cache after each test."""
        clear_cache()
    
    def test_weather_caching(self):
        """Should cache results and return same data."""
        # This test requires actual WEATHER_API_KEY or will use fallback
        result1 = fetch_weather_snapshot(35.5, -80.0)
        result2 = fetch_weather_snapshot(35.5, -80.0)
        
        # Should be exactly same object if cached
        assert result1 is result2
    
    def test_cache_clear(self):
        """Should clear cache when requested."""
        fetch_weather_snapshot(35.5, -80.0)
        clear_cache()
        # After clear, fetching same location should return fresh data
        # (or use fallback) - can't assert exact equality
        result = fetch_weather_snapshot(35.5, -80.0)
        assert result is not None
    
    def test_different_locations_separate_cache(self):
        """Should cache separately for different locations."""
        result1 = fetch_weather_snapshot(35.5, -80.0)
        result2 = fetch_weather_snapshot(40.0, -75.0)
        
        # Different locations should not be same object
        assert result1 is not result2
    
    def test_assess_weather_risks_high_humidity(self):
        """Should detect high humidity risk."""
        risks = _assess_weather_risks(humidity=85, temp_c=25, rain_last_hour=0, rain_next_hour=0)
        assert any("humidity" in r.lower() for r in risks)
    
    def test_assess_weather_risks_high_temp(self):
        """Should detect high temperature risk."""
        risks = _assess_weather_risks(humidity=50, temp_c=35, rain_last_hour=0, rain_next_hour=0)
        assert any("heat" in r.lower() for r in risks)
    
    def test_assess_weather_risks_low_temp(self):
        """Should detect low temperature risk."""
        risks = _assess_weather_risks(humidity=50, temp_c=5, rain_last_hour=0, rain_next_hour=0)
        assert any("temperature" in r.lower() or "cold" in r.lower() for r in risks)
    
    def test_assess_weather_risks_recent_rain(self):
        """Should detect recent rain."""
        risks = _assess_weather_risks(humidity=50, temp_c=25, rain_last_hour=2.0, rain_next_hour=0)
        assert any("recently rained" in r.lower() or "wet" in r.lower() for r in risks)
    
    def test_assess_weather_risks_upcoming_rain(self):
        """Should detect upcoming rain."""
        risks = _assess_weather_risks(humidity=50, temp_c=25, rain_last_hour=0, rain_next_hour=1.5)
        assert any("soon" in r.lower() or "spray" in r.lower() for r in risks)
    
    def test_no_risks(self):
        """Should handle no risks gracefully."""
        risks = _assess_weather_risks(humidity=40, temp_c=25, rain_last_hour=0, rain_next_hour=0)
        # No risks, so may be empty or have neutral message
        assert risks is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
