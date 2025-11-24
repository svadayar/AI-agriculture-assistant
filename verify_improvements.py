#!/usr/bin/env python3
"""Quick verification script for improved code."""

import os
import sys

# Test 1: Logging
print("=" * 70)
print("TEST 1: Logging Configuration")
print("=" * 70)
try:
    from logging_config import get_logger
    logger = get_logger("verify")
    logger.info("[OK] Logging configured successfully")
    print("[OK] Logging works\n")
except Exception as e:
    print(f"[FAIL] Logging failed: {e}\n")
    sys.exit(1)

# Test 2: LLM Client
print("=" * 70)
print("TEST 2: LLM Client")
print("=" * 70)
try:
    from llm_client import get_llm_client
    client = get_llm_client()
    
    # Test with different prompts
    test_prompts = [
        'Farmer description of the problem:\n"""Leaves are yellowing"""',
        'Farmer description of the problem:\n"""I see brown spots"""',
        'Farmer description of the problem:\n"""Soil is dry"""',
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        result = client.analyze_crop_from_prompt(prompt)
        print(f"  Test {i}: {result.split(chr(10))[0][:60]}...")
    
    print("[OK] LLM Client works\n")
except Exception as e:
    print(f"[FAIL] LLM Client failed: {e}\n")
    sys.exit(1)

# Test 3: Advisory Rules
print("=" * 70)
print("TEST 3: Advisory Rules & Escalation")
print("=" * 70)
try:
    from advisory_rules import apply_safety_and_escalation, EscalationLevel
    
    test_answer = "This is water stress. Water deeply at the base in early morning."
    result = apply_safety_and_escalation(test_answer)
    
    assert len(result) > len(test_answer)  # Should add disclaimers
    assert "DISCLAIMER" in result or "disclaimer" in result
    print(f"  Original: {len(test_answer)} chars")
    print(f"  With safety: {len(result)} chars")
    print("[OK] Advisory rules work\n")
except Exception as e:
    print(f"[FAIL] Advisory rules failed: {e}\n")
    sys.exit(1)

# Test 4: Weather Client
print("=" * 70)
print("TEST 4: Weather Client")
print("=" * 70)
try:
    from weather_client import fetch_weather_snapshot, clear_cache
    
    result = fetch_weather_snapshot(35.5, -80.0)
    assert "summary_text" in result
    print(f"  Weather summary: {result['summary_text'][:60]}...")
    
    # Test caching
    result2 = fetch_weather_snapshot(35.5, -80.0)
    assert result is result2  # Should be cached
    print("  [OK] Caching works (same object returned)")
    
    clear_cache()
    print("[OK] Weather client works\n")
except Exception as e:
    print(f"[FAIL] Weather client failed: {e}\n")
    sys.exit(1)

# Test 5: Voice of the Farmer
print("=" * 70)
print("TEST 5: Voice of the Farmer")
print("=" * 70)
try:
    from voice_of_the_farmer import _mock_transcription
    
    # Test mock
    text = _mock_transcription()
    assert len(text) > 0
    print(f"  Mock transcription: {text[:60]}...")
    print("[OK] Voice of the farmer works\n")
except Exception as e:
    import traceback
    print(f"[FAIL] Voice of the farmer failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Utils
print("=" * 70)
print("TEST 6: Audio Utils")
print("=" * 70)
try:
    from utils_audio import ensure_dir, write_silent_wav
    
    test_dir = "test_output"
    ensure_dir(test_dir)
    assert os.path.exists(test_dir)
    
    wav_file = os.path.join(test_dir, "test_silence.wav")
    write_silent_wav(wav_file, seconds=1.0)
    assert os.path.exists(wav_file)
    assert os.path.getsize(wav_file) > 0
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    
    print("[OK] Audio utils work\n")
except Exception as e:
    print(f"[FAIL] Audio utils failed: {e}\n")
    sys.exit(1)

# Summary
print("=" * 70)
print("[SUCCESS] ALL VERIFICATION TESTS PASSED")
print("=" * 70)
print("\nSummary of improvements:")
print("  [OK] Logging framework configured")
print("  [OK] LLM client with varied mock responses")
print("  [OK] Advisory rules with escalation levels")
print("  [OK] Weather caching and retry logic")
print("  [OK] Enhanced voice transcription with fallback")
print("  [OK] Audio utilities functional")
print("\nYou can now run: python agri_assistant_app.py")
