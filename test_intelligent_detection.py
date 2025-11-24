#!/usr/bin/env python3
"""
Demo script showing intelligent crop and plant part detection.
Demonstrates the farmer-friendly features of the enhanced app.
"""

from agri_assistant_app import detect_crop_from_text, detect_plant_part_from_text

def test_intelligent_detection():
    """Test intelligent crop and plant part detection."""
    
    print("=" * 80)
    print("AI AGRICULTURE ASSISTANT - INTELLIGENT DETECTION DEMO")
    print("=" * 80)
    
    # Test cases simulating real farmer descriptions
    test_cases = [
        {
            "description": "My tomato leaves have brown spots that appeared after 3 days of rain",
            "expected_crop": "tomato",
            "expected_part": "leaf",
        },
        {
            "description": "Corn stalk is yellowing from the bottom, wilting despite watering",
            "expected_crop": "corn",
            "expected_part": "soil",  # Or "stem", but soil/root is likely cause
        },
        {
            "description": "Cotton bolls have dark spots and are rotting before harvest",
            "expected_crop": "cotton",
            "expected_part": "fruit",
        },
        {
            "description": "I see small holes and insects on my wheat leaves",
            "expected_crop": "wheat",
            "expected_part": "insect/pest",
        },
        {
            "description": "Rice paddies have white powdery substance on the leaves",
            "expected_crop": "rice",
            "expected_part": "leaf",
        },
        {
            "description": "Potato plants are wilting and leaves are yellowing from bottom",
            "expected_crop": "potato",
            "expected_part": "soil",
        },
        {
            "description": "Cabbage leaves have holes and webbing, looks like pest damage",
            "expected_crop": "cabbage",
            "expected_part": "insect/pest",
        },
        {
            "description": "Pepper fruits are cracked and deformed, soft spots appearing",
            "expected_crop": "pepper",
            "expected_part": "fruit",
        },
        {
            "description": "Stem is girdled and I see lesions, bark is peeling",
            "expected_crop": "other",  # Generic crop
            "expected_part": "stem",
        },
        {
            "description": "Unknown plant looks sick, not sure what crop it is",
            "expected_crop": "other",
            "expected_part": "leaf",  # Default
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        desc = test["description"]
        expected_crop = test["expected_crop"]
        expected_part = test["expected_part"]
        
        detected_crop = detect_crop_from_text(desc)
        detected_part = detect_plant_part_from_text(desc)
        
        crop_match = "✅" if detected_crop == expected_crop else "❌"
        part_match = "✅" if detected_part == expected_part else "❌"
        
        print(f"\n[TEST {i}] Farmer says:")
        print(f"  '{desc}'")
        print(f"  Crop:      {crop_match} Detected: {detected_crop:12} (Expected: {expected_crop})")
        print(f"  Plant Part: {part_match} Detected: {detected_part:15} (Expected: {expected_part})")
        
        if detected_crop == expected_crop and detected_part == expected_part:
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    if failed == 0:
        print("✅ All detection tests passed!")
        print("\nThe app successfully recognizes:")
        print("  • 8+ crop types (tomato, corn, cotton, wheat, rice, potato, cabbage, pepper)")
        print("  • 5 plant parts (leaf, stem, fruit, soil, insect/pest)")
        print("  • Context from farmer's natural language description")
        print("\n🌾 Farmers can now use the app without selecting dropdowns!")
        return True
    else:
        print(f"⚠️  {failed} detection tests failed")
        print("Consider adding more keywords to CROP_KEYWORDS or PLANT_PART_KEYWORDS")
        return False


if __name__ == "__main__":
    success = test_intelligent_detection()
    exit(0 if success else 1)
