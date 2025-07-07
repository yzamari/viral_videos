#!/usr/bin/env python3
"""
Test script to verify topic-specific prompt generation fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory

def test_topic_specific_prompts():
    """Test that VEO prompts are generated based on the actual topic"""
    
    print("🧪 Testing Topic-Specific Prompt Generation")
    print("=" * 50)
    
    # Create a video generator
    generator = VideoGenerator(
        api_key="test",
        use_real_veo2=False  # Use mock for testing
    )
    
    # Test case 1: Funny cats
    print("\n1. Testing 'funny cats' topic:")
    config = GeneratedVideoConfig(
        target_platform=Platform.YOUTUBE,
        category=VideoCategory.COMEDY,
        duration_seconds=15,
        topic="funny cats playing",
        style="viral",
        tone="engaging",
        target_audience="cat lovers",
        hook="You won't believe what this cat does!",
        main_content=["Cat playing with toy"],
        call_to_action="Follow for more cats!",
        visual_style="cute",
        color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
        text_overlays=[],
        transitions=["fade"],
        background_music_style="upbeat",
        voiceover_style="enthusiastic",
        sound_effects=[],
        inspired_by_videos=[],
        predicted_viral_score=0.85,
        frame_continuity=True
    )
    
    # Test the topic-specific prompt generation
    prompts = generator._generate_topic_specific_fallback_prompts(config, 3)
    
    print(f"Generated {len(prompts)} prompts:")
    for i, prompt in enumerate(prompts):
        print(f"  Scene {i+1}: {prompt['description']}")
        print(f"  Prompt: {prompt['veo2_prompt'][:100]}...")
        
        # Validate that prompts contain cat-related content
        prompt_text = prompt['veo2_prompt'].lower()
        if 'cat' in prompt_text:
            print("  ✅ Contains cat content")
        else:
            print("  ❌ Missing cat content")
        
        # Check for generic creator content (should be avoided)
        generic_terms = ['creator', 'influencer', 'screen', 'studio', 'computer']
        has_generic = any(term in prompt_text for term in generic_terms)
        if has_generic:
            print("  ⚠️ Contains generic creator content")
        else:
            print("  ✅ No generic creator content")
        print()
    
    # Test case 2: News topic
    print("\n2. Testing 'political news' topic:")
    config.topic = "political news update"
    config.category = VideoCategory.NEWS
    
    news_prompts = generator._generate_topic_specific_fallback_prompts(config, 3)
    
    for i, prompt in enumerate(news_prompts):
        print(f"  Scene {i+1}: {prompt['description']}")
        prompt_text = prompt['veo2_prompt'].lower()
        
        # Check for news-related content
        news_terms = ['news', 'political', 'professional']
        has_news = any(term in prompt_text for term in news_terms)
        if has_news:
            print("  ✅ Contains news-related content")
        else:
            print("  ❌ Missing news content")
        print()
    
    print("🎯 Test completed! Check results above.")

if __name__ == "__main__":
    test_topic_specific_prompts() 