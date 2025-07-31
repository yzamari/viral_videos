#!/usr/bin/env python3
"""
Test VEO-3 Fast with JSON Prompts
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.veo_client_factory import VeoClientFactory, VeoModel
from src.generators.json_prompt_system import (
    VEOJsonPrompt, CameraConfig, LightingConfig, 
    SceneConfig, EffectsConfig, CameraMovement, 
    ShotType, VisualStyle, LightingStyle, Platform
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_json_prompt():
    """Test VEO-3 Fast with JSON prompt"""
    print("\n🚀 Testing VEO-3 Fast with JSON Prompts\n")
    
    # Create output directory
    output_dir = "test_veo3_json_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize factory
    factory = VeoClientFactory()
    
    # Create VEO-3 Fast client
    client = factory.create_client(VeoModel.VEO3_FAST, output_dir)
    
    if not client:
        print("❌ Failed to create VEO-3 Fast client")
        return False
    
    # Create a structured JSON prompt
    json_prompt = VEOJsonPrompt(
        description="A majestic eagle soaring through mountain peaks at sunset",
        style=VisualStyle.CINEMATIC,
        duration=8.0,
        platform=Platform.YOUTUBE,
        aspect_ratio="16:9",
        
        # Camera configuration
        camera=CameraConfig(
            shot_type=ShotType.WIDE,
            movement=CameraMovement.TRACKING,
            lens="24mm",
            aperture="f/4.0",
            frame_rate="24fps"
        ),
        
        # Lighting configuration
        lighting=LightingConfig(
            style=LightingStyle.GOLDEN_HOUR,
            mood="epic and majestic",
            key_light="warm sunset from behind mountains",
            fill_light="soft ambient sky light"
        ),
        
        # Scene configuration
        scene=SceneConfig(
            location="Rocky mountain range",
            time_of_day="golden hour sunset",
            weather="clear with light clouds",
            environment_details="snow-capped peaks, dramatic valleys"
        ),
        
        # Effects configuration
        effects=EffectsConfig(
            color_grading="warm orange and purple tones",
            film_grain="subtle cinematic grain",
            lens_flare=True
        ),
        
        keywords=["eagle", "mountains", "sunset", "cinematic", "majestic"],
        constraints=["no text overlays", "smooth camera movement", "realistic physics"]
    )
    
    # Test 1: Simple text prompt
    print("📝 Test 1: Traditional text prompt")
    text_prompt = "An eagle flying through mountains at sunset"
    
    video1 = client.generate_video(
        prompt=text_prompt,
        duration=5.0,
        clip_id="test_text_prompt",
        aspect_ratio="16:9"
    )
    
    if video1 and os.path.exists(video1):
        print(f"✅ Text prompt test successful: {video1}")
    else:
        print("❌ Text prompt test failed")
    
    # Test 2: JSON prompt
    print("\n📋 Test 2: Structured JSON prompt")
    print(f"JSON prompt preview:\n{json_prompt.to_json()[:500]}...\n")
    
    video2 = client.generate_video(
        prompt=json_prompt,
        duration=8.0,  # Will be overridden by JSON prompt duration
        clip_id="test_json_prompt",
        aspect_ratio="9:16"  # Will be overridden by JSON prompt aspect ratio
    )
    
    if video2 and os.path.exists(video2):
        print(f"✅ JSON prompt test successful: {video2}")
        file_size = os.path.getsize(video2) / (1024 * 1024)
        print(f"   File size: {file_size:.2f} MB")
        
        # Compare file sizes
        if video1:
            size1 = os.path.getsize(video1) / (1024 * 1024)
            print(f"\n📊 Comparison:")
            print(f"   Text prompt video: {size1:.2f} MB")
            print(f"   JSON prompt video: {file_size:.2f} MB")
            print(f"   JSON prompt provides more detailed control!")
        
        return True
    else:
        print("❌ JSON prompt test failed")
        return False

if __name__ == "__main__":
    success = test_json_prompt()
    
    if success:
        print("\n🎉 VEO-3 Fast JSON prompt integration successful!")
        print("✨ JSON prompts provide better control over:")
        print("   - Camera movements and angles")
        print("   - Lighting and mood")
        print("   - Scene composition")
        print("   - Visual effects")
        print("   - Overall video quality")
    else:
        print("\n⚠️ JSON prompt integration needs debugging")
    
    sys.exit(0 if success else 1)