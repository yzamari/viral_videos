#!/usr/bin/env python3
"""
Test script to verify improvements:
1. Configurable video duration
2. Realistic amateur-style Veo-2 prompts
3. Enhanced TTS script generation
"""

import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from generators.video_generator import VideoGenerator
from models.video_models import GeneratedVideoConfig, Platform, VideoCategory

def test_configurable_duration():
    """Test that video duration can be configured"""
    print("🔧 Testing configurable video duration...")
    
    # Test different durations
    durations = [10, 15, 30, 60]
    
    for duration in durations:
        print(f"\n📏 Testing {duration}-second video...")
        
        # Create a test config
        config = GeneratedVideoConfig(
            topic="Test Baby Video",
            duration_seconds=duration,
            platform=Platform.YOUTUBE,
            category=VideoCategory.ENTERTAINMENT,
            style="viral",
            tone="excited",
            hook="Get ready for cuteness!",
            main_content=["Baby crawls", "Baby struggles", "Baby succeeds"],
            call_to_action="Like and subscribe!",
            text_overlays=[],
            color_scheme=["red", "blue"],
            predicted_viral_score=0.85
        )
        
        # Initialize video generator
        video_gen = VideoGenerator(
            api_key="test_key",
            output_dir="test_outputs"
        )
        
        # Test Veo-2 prompt generation
        prompts = video_gen._generate_veo2_prompts(config, "Test script")
        
        print(f"✅ Generated {len(prompts)} prompts for {duration}s video")
        
        # Check scene duration
        expected_scene_duration = duration / 3
        for prompt in prompts:
            assert abs(prompt['duration'] - expected_scene_duration) < 0.1, \
                f"Scene duration mismatch: expected {expected_scene_duration}, got {prompt['duration']}"
        
        print(f"✅ Scene durations correct: {expected_scene_duration:.1f}s each")
        
        # Test TTS script length
        tts_script = video_gen._clean_script_for_tts("Test script", duration)
        print(f"✅ TTS script ({duration}s): {tts_script[:50]}...")

def test_realistic_prompts():
    """Test that Veo-2 prompts include realistic amateur elements"""
    print("\n📱 Testing realistic amateur-style Veo-2 prompts...")
    
    config = GeneratedVideoConfig(
        topic="Baby Challenge",
        duration_seconds=15,
        platform=Platform.TIKTOK,
        category=VideoCategory.ENTERTAINMENT,
        style="viral",
        tone="excited",
        hook="Watch this!",
        main_content=["Baby tries", "Baby fails", "Baby wins"],
        call_to_action="Share this!",
        text_overlays=[],
        color_scheme=["orange"],
        predicted_viral_score=0.90
    )
    
    video_gen = VideoGenerator(
        api_key="test_key",
        output_dir="test_outputs"
    )
    
    prompts = video_gen._generate_veo2_prompts(config, "Cute baby video")
    
    # Check for amateur elements in prompts
    amateur_keywords = [
        "realistic", "amateur", "smartphone", "phone", "shaky", "handheld",
        "instagram", "tiktok", "snapchat", "vertical", "9:16", "natural",
        "authentic", "genuine", "viral", "social media", "budget"
    ]
    
    for i, prompt in enumerate(prompts):
        prompt_text = prompt['veo2_prompt'].lower()
        found_keywords = [kw for kw in amateur_keywords if kw in prompt_text]
        
        print(f"\n🎬 Scene {i+1} - {prompt['description']}")
        print(f"📱 Amateur keywords found: {', '.join(found_keywords)}")
        
        assert len(found_keywords) >= 5, \
            f"Scene {i+1} should have at least 5 amateur keywords, found {len(found_keywords)}"
        
        # Check for critical requirements
        assert "realistic" in prompt_text, f"Scene {i+1} missing 'realistic'"
        assert "vertical" in prompt_text or "9:16" in prompt_text, f"Scene {i+1} missing vertical format"
        assert any(social in prompt_text for social in ["instagram", "tiktok", "snapchat"]), \
            f"Scene {i+1} missing social media reference"
    
    print(f"✅ All {len(prompts)} prompts contain proper amateur elements")

def test_duration_based_narration():
    """Test that TTS scripts adapt to video duration"""
    print("\n🗣️  Testing duration-based narration...")
    
    video_gen = VideoGenerator(
        api_key="test_key",
        output_dir="test_outputs"
    )
    
    # Test different durations
    test_cases = [
        (10, 3),   # 10 seconds should have 3 lines
        (20, 5),   # 20 seconds should have 5 lines
        (30, 7),   # 30+ seconds should have 7 lines
        (60, 7)    # 60 seconds should also have 7 lines (max)
    ]
    
    for duration, expected_lines in test_cases:
        script = video_gen._clean_script_for_tts("Test script", duration)
        
        # Count exclamation points as a proxy for line count
        line_count = script.count('!') - 1  # Subtract final exclamation
        
        print(f"📏 {duration}s video: {line_count} lines (expected ~{expected_lines})")
        
        # Allow some flexibility (+/- 1 line)
        assert abs(line_count - expected_lines) <= 1, \
            f"Duration {duration}s: expected ~{expected_lines} lines, got {line_count}"
    
    print("✅ TTS scripts correctly adapt to video duration")

def main():
    """Run all tests"""
    print("🚀 Testing Viral Video Generator Improvements")
    print("=" * 50)
    
    try:
        # Create test output directory
        os.makedirs("test_outputs", exist_ok=True)
        
        # Run tests
        test_configurable_duration()
        test_realistic_prompts()
        test_duration_based_narration()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Improvements working correctly:")
        print("✅ Configurable video duration (via VIDEO_DURATION env var)")
        print("✅ Realistic amateur-style Veo-2 prompts")
        print("✅ Duration-adaptive TTS narration")
        print("✅ Social media style specifications")
        print("✅ Enhanced amateur camera elements")
        
        print("\n📋 Next Steps:")
        print("1. Set VIDEO_DURATION environment variable (default: 30)")
        print("2. Run: python main.py generate --platform youtube --category Entertainment --topic 'Baby Videos'")
        print("3. Check outputs/ directory for realistic Veo-2 prompts")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    finally:
        # Cleanup
        if os.path.exists("test_outputs"):
            import shutil
            shutil.rmtree("test_outputs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 