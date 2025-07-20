#!/usr/bin/env python3
"""
Test script to verify JSON fixer and voice director fixes
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.json_fixer import JSONFixer
from agents.voice_director_agent import VoiceDirectorAgent
from models.video_models import Language, Platform, VideoCategory

def test_json_fixer():
    """Test the JSON fixer fixes"""
    print("🧪 Testing JSON Fixer Fixes")
    print("=" * 50)
    
    # Test with a mock API key
    json_fixer = JSONFixer("test_key")
    
    # Test 1: Type validation
    print("\n1. Testing type validation...")
    test_data = {
        "strategy": "single",
        "primary_personality": "narrator",
        "primary_gender": "female",
        "use_multiple_voices": False,
        "voice_changes_per_clip": False,
        "reasoning": "Test reasoning",
        "clip_voice_plan": []
    }
    
    expected_structure = {
        "strategy": str,
        "primary_personality": str,
        "primary_gender": str,
        "use_multiple_voices": bool,
        "voice_changes_per_clip": bool,
        "reasoning": str,
        "clip_voice_plan": list
    }
    
    try:
        result = json_fixer.validate_json_structure(test_data, expected_structure)
        print(f"✅ Type validation result: {result}")
    except Exception as e:
        print(f"❌ Type validation failed: {e}")
    
    # Test 2: JSON parsing
    print("\n2. Testing JSON parsing...")
    test_json = '{"strategy": "single", "primary_personality": "narrator"}'
    
    try:
        result = json_fixer.fix_json(test_json, expected_structure)
        print(f"✅ JSON parsing result: {result is not None}")
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")

def test_voice_director():
    """Test the voice director fixes"""
    print("\n🧪 Testing Voice Director Fixes")
    print("=" * 50)
    
    # Test with a mock API key
    voice_director = VoiceDirectorAgent("test_key")
    
    # Test 1: Voice configuration generation
    print("\n1. Testing voice configuration generation...")
    
    try:
        voice_config = voice_director.analyze_content_and_select_voices(
            topic="Test topic",
            script="This is a test script for voice generation.",
            language=Language.ENGLISH_US,
            platform=Platform.INSTAGRAM,
            category=VideoCategory.COMEDY,
            duration_seconds=5,
            num_clips=4
        )
        
        if voice_config and "clip_voices" in voice_config:
            clip_count = len(voice_config["clip_voices"])
            print(f"✅ Voice config generated: {clip_count} clips")
            
            # Check if all clips have proper indices
            for i, clip in enumerate(voice_config["clip_voices"]):
                if clip.get("clip_index") == i:
                    print(f"   ✅ Clip {i}: {clip.get('voice_name', 'unknown')}")
                else:
                    print(f"   ❌ Clip {i}: index mismatch - {clip.get('clip_index')}")
        else:
            print("❌ Voice config generation failed")
            
    except Exception as e:
        print(f"❌ Voice director test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing JSON and Voice Director Fixes")
    print("=" * 60)
    
    test_json_fixer()
    test_voice_director()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 