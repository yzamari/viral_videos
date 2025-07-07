#!/usr/bin/env python3
"""
Test script for new Veo retry mechanism and AI-enhanced features
"""

import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import Platform, VideoCategory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_new_features():
    """Test the new retry mechanism and AI enhancements"""
    
    print("\n🧪 Testing New Veo Retry Mechanism & AI Features")
    print("=" * 60)
    
    # Initialize generator
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return
    
    generator = VideoGenerator(
        api_key=api_key,
        output_dir="outputs",
        use_real_veo2=True  # Will trigger retry mechanism
    )
    
    # Create test config
    from src.models.video_models import GeneratedVideoConfig
    
    test_config = GeneratedVideoConfig(
        video_id="test_new_features",
        target_platform=Platform.TIKTOK,
        category=VideoCategory.ENTERTAINMENT,
        topic="Amazing test of new AI features with retry mechanism",
        duration_seconds=15,
        style="engaging",
        tone="conversational",
        hook="Watch how the AI handles retries!",
        main_content=["Veo-3 attempt", "Veo-2 fallback", "Black screen ultimate fallback"],
        call_to_action="Follow for more AI tests!",
        tags=["ai", "test", "viral", "features"],
        predicted_viral_score=0.9,
        # New flags
        realistic_audio=True,  # Enable Google Cloud TTS
        narrative="neutral",
        feeling="energetic"
    )
    
    print("\n📋 Test Configuration:")
    print(f"- Duration: {test_config.duration_seconds}s")
    print(f"- Topic: {test_config.topic}")
    print(f"- Realistic Audio: {getattr(test_config, 'realistic_audio', False)}")
    print(f"- Feeling: {getattr(test_config, 'feeling', 'neutral')}")
    
    print("\n🔄 Expected Retry Sequence:")
    print("1. Try Veo-3 (will fail - not released)")
    print("2. Try Veo-2 (might fail if quota exceeded)")
    print("3. Wait 1 minute")
    print("4. Retry Veo-3")
    print("5. Retry Veo-2")
    print("6. Black screen fallback")
    
    print("\n🎨 AI Features Being Tested:")
    print("- AI-generated text overlays with custom fonts/colors")
    print("- Natural audio that reflects content")
    print("- Smart black screen messages")
    
    try:
        print("\n🚀 Starting generation...")
        result = generator.generate_video(test_config)
        
        print("\n✅ Generation Complete!")
        print(f"📁 Video saved to: {result.file_path}")
        print(f"📏 File size: {result.file_size_mb:.2f} MB")
        print(f"⏱️  Generation time: {result.generation_time_seconds:.1f}s")
        print(f"🎯 Viral score: {result.config.predicted_viral_score}")
        
        # Check what was actually used
        print("\n📊 Generation Details:")
        print(f"- AI Models: {', '.join(result.ai_models_used)}")
        
        # Display script preview
        print("\n📝 Generated Script Preview:")
        if result.audio_transcript:
            print(result.audio_transcript[:200] + "..." if len(result.audio_transcript) > 200 else result.audio_transcript)
        else:
            print("No audio transcript generated")
        
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()

def test_text_overlay_ai():
    """Test just the AI text overlay generation"""
    print("\n🎨 Testing AI Text Overlay Generation")
    print("=" * 60)
    
    from src.generators.video_generator import VideoGenerator
    
    # Create a mock generator to test overlay generation
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return
        
    generator = VideoGenerator(api_key=api_key)
    
    # Test config
    from src.models.video_models import GeneratedVideoConfig
    test_config = GeneratedVideoConfig(
        video_id="overlay_test",
        target_platform=Platform.TIKTOK,
        category=VideoCategory.ENTERTAINMENT,
        topic="Incredible AI-powered video creation test",
        duration_seconds=15,
        style="modern",
        tone="exciting",
        hook="AI creates perfect videos!",
        main_content=["Testing overlays"],
        call_to_action="Follow for more!",
        tags=["ai", "test"],
        predicted_viral_score=0.9,
        # Additional required fields
        target_audience="tech enthusiasts",
        visual_style="modern minimalist",
        color_scheme=["blue", "white", "black"],
        text_overlays=[{"text": "Test overlay", "position": "center", "timing": "0-3"}],
        transitions=["fade", "cut"],
        background_music_style="electronic",
        inspired_by_videos=[]
    )
    
    # Generate overlays
    overlays = generator._generate_text_overlays(test_config, 15.0)
    
    print("\n📋 Generated Overlays:")
    for i, overlay in enumerate(overlays, 1):
        print(f"\nOverlay {i}:")
        print(f"  Text: {overlay['text']}")
        print(f"  Font: {overlay.get('font', 'default')}")
        print(f"  Color: {overlay['color']}")
        print(f"  Position: {overlay['position']}")
        print(f"  Timing: {overlay['start']}s - {overlay['end']}s")
        print(f"  Size: {overlay['fontsize']}pt")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test new Veo features")
    parser.add_argument('--overlays-only', action='store_true', 
                       help='Test only text overlay generation')
    
    args = parser.parse_args()
    
    if args.overlays_only:
        test_text_overlay_ai()
    else:
        test_new_features() 