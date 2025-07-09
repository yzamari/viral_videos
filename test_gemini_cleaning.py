#!/usr/bin/env python3
"""
Test Gemini-based script cleaning to remove visual cues
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.video_generator import VideoGenerator

def test_gemini_cleaning():
    """Test Gemini script cleaning functionality"""
    
    # Test script with visual cues mixed in
    test_script = """
    {
        "hook": {
            "text": "This is amazing! You won't BELIEVE what's hiding in your child's favorite bedtime toy!",
            "type": "shock",
            "visual_cue": "Start with a close-up on a beloved, well-used stuffed animal",
            "duration_seconds": 3
        },
        "segments": [
            {
                "text": "Is your bed a toy wonderland? Think again! Camera shows messy bed with toys everywhere.",
                "visual": "Rapid montage of cluttered beds",
                "duration": 4,
                "transition": "quick cuts"
            },
            {
                "text": "They hog your space, collect dust, and sneaky monsters can hide there! Visual: animated dust particles.",
                "visual": "Close-up shots of dust on toys",
                "duration": 4,
                "transition": "zoom"
            }
        ],
        "cta": {
            "text": "Keep beds clear for super sleep! Toys belong on shelves. Sweet dreams! Scene fades to organized bedroom.",
            "type": "solution",
            "duration_seconds": 4
        }
    }
    """
    
    # Initialize generator
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print('❌ GEMINI_API_KEY not found')
        return
    
    generator = VideoGenerator(api_key=api_key, use_real_veo2=False)
    
    print("🧪 Testing Gemini script cleaning...")
    print(f"📝 Original script: {test_script[:200]}...")
    
    # Test the cleaning
    cleaned_script = generator._clean_script_for_tts(test_script, 15)
    
    print(f"\n✅ Cleaned script: {cleaned_script}")
    
    # Verify no visual cues remain
    visual_words = ['camera', 'visual', 'scene', 'cut', 'zoom', 'fade', 'shot', 'montage', 'close-up']
    has_visual_cues = any(word in cleaned_script.lower() for word in visual_words)
    
    if has_visual_cues:
        print("❌ FAIL: Visual cues still present in cleaned script")
    else:
        print("✅ SUCCESS: No visual cues found in cleaned script")
    
    # Test word count
    words = cleaned_script.split()
    target_words = int(15 * 2.2)
    print(f"📊 Word count: {len(words)} (target: {target_words})")
    
    if abs(len(words) - target_words) <= 5:
        print("✅ SUCCESS: Word count within target range")
    else:
        print(f"⚠️ WARNING: Word count outside target range")

if __name__ == "__main__":
    test_gemini_cleaning() 