#!/usr/bin/env python3
"""Test the new tagging system for visual/dialogue separation"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generators.enhanced_script_processor import EnhancedScriptProcessor
from src.generators.director import Director
from config.config import settings

def test_tagging():
    """Test the tagging system"""
    
    # Test script with mixed visual and dialogue tags
    test_scripts = [
        "[VISUAL: Dragon breathing fire] DIALOGUE: The limit approaches infinity!",
        "DIALOGUE: Welcome to calculus! [VISUAL: Blackboard appears] DIALOGUE: Today we learn derivatives.",
        "[VISUAL: Explosion] DIALOGUE: This is amazing! [VISUAL: Another explosion] DIALOGUE: Science rocks!",
        # Old format for backward compatibility
        "The hero arrives [wide shot]. 'I am here!' (raises sword)",
        # Plain dialogue
        "Just plain dialogue without any tags.",
    ]
    
    processor = EnhancedScriptProcessor(api_key=settings.google_api_key)
    
    print("🧪 Testing Visual/Dialogue Tagging System\n")
    print("=" * 60)
    
    for i, script in enumerate(test_scripts, 1):
        print(f"\nTest {i}: Original Script")
        print(f"Input: {script}")
        
        # Clean visual descriptions
        cleaned = processor._clean_visual_descriptions(script)
        
        print(f"Output: {cleaned}")
        print("-" * 40)
    
    # Test with Director
    print("\n🎬 Testing Director with Tagging")
    print("=" * 60)
    
    director = Director(api_key=settings.google_api_key)
    
    # Test hook generation with new tagging
    test_mission = "Create educational content about calculus limits"
    
    print(f"\nMission: {test_mission}")
    print("Generating hook with visual/dialogue tags...")
    
    try:
        from src.models.video_models import Platform
        hook = director._create_hook(
            mission=test_mission,
            style="educational",
            platform=Platform.INSTAGRAM,
            patterns={},
            news_context=""
        )
        
        print(f"Generated Hook: {hook}")
        
        # Clean the hook for TTS
        if isinstance(hook, dict) and 'text' in hook:
            cleaned_hook = processor._clean_visual_descriptions(hook['text'])
            print(f"Cleaned for TTS: {cleaned_hook}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tagging()