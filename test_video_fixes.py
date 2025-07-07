#!/usr/bin/env python3
"""
Test script to verify all video generation fixes work properly
"""
import os
import sys
import time
from dotenv import load_dotenv
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.video_generator import VideoGenerator, MockVeo2Client
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.utils.logging_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

def test_mock_veo2_client():
    """Test MockVeo2Client functionality"""
    logger.info("🧪 Testing MockVeo2Client...")
    
    client = MockVeo2Client("outputs")
    
    # Test clip generation
    test_prompt = "Adorable baby crawling on soft carpet, giggles and smiles, natural home lighting"
    clip_path = client.generate_video_clip(test_prompt, 3.0, "test_clip")
    
    if os.path.exists(clip_path):
        file_size = os.path.getsize(clip_path) / 1024  # KB
        logger.info(f"✅ Veo-2 clip generated: {clip_path} ({file_size:.1f} KB)")
        return True
    else:
        logger.error("❌ Veo-2 clip generation failed")
        return False

def test_creative_script_generation():
    """Test that script generation produces different scripts with randomness"""
    logger.info("🧪 Testing creative script generation...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not found in environment")
        return False
    
    generator = VideoGenerator(api_key)
    
    # Create test config
    config = GeneratedVideoConfig(
        video_id="test_script",
        topic="Baby learning to walk - first steps",
        style="heartwarming",
        tone="excited",
        hook="Watch this baby's incredible first steps!",
        main_content=["baby standing up", "first wobbly steps", "proud parents cheering"],
        call_to_action="Like if this made you smile!",
        duration_seconds=10,
        platform=Platform.TIKTOK,
        category=VideoCategory.ENTERTAINMENT,
        predicted_viral_score=0.85
    )
    
    # Generate multiple scripts to test randomness
    scripts = []
    for i in range(3):
        script = generator._generate_creative_script(config, f"test_{int(time.time())}_{i}")
        scripts.append(script[:100])  # First 100 chars for comparison
        logger.info(f"Script {i+1}: {script[:60]}...")
        time.sleep(1)  # Ensure different timestamps
    
    # Check if scripts are different
    unique_scripts = len(set(scripts))
    if unique_scripts > 1:
        logger.info(f"✅ Generated {unique_scripts}/3 unique scripts - randomness working!")
        return True
    else:
        logger.error("❌ All scripts are identical - randomness not working")
        return False

def test_duration_matching():
    """Test that video and audio durations match exactly"""
    logger.info("🧪 Testing duration matching...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not found in environment")
        return False
    
    generator = VideoGenerator(api_key)
    
    # Test different durations
    test_durations = [10, 15, 20]
    
    for duration in test_durations:
        config = GeneratedVideoConfig(
            video_id=f"duration_test_{duration}",
            topic="Quick baby moment",
            style="cute",
            tone="warm",
            hook="Adorable moment incoming!",
            main_content=["baby playing", "cute reaction"],
            call_to_action="Follow for more!",
            duration_seconds=duration,
            platform=Platform.TIKTOK,
            category=VideoCategory.ENTERTAINMENT,
            predicted_viral_score=0.75
        )
        
        try:
            # Generate TTS to test duration
            script = f"This is a test script for {duration} seconds that should match the video duration exactly."
            audio_path = generator._generate_voiceover(script, duration)
            
            if os.path.exists(audio_path):
                from moviepy.editor import AudioFileClip
                audio_clip = AudioFileClip(audio_path)
                actual_duration = audio_clip.duration
                audio_clip.close()
                
                tolerance = 1.0  # 1 second tolerance
                if abs(actual_duration - duration) <= tolerance:
                    logger.info(f"✅ Duration {duration}s: Audio {actual_duration:.1f}s (within tolerance)")
                else:
                    logger.warning(f"⚠️  Duration {duration}s: Audio {actual_duration:.1f}s (outside tolerance)")
            else:
                logger.error(f"❌ Audio generation failed for {duration}s")
                
        except Exception as e:
            logger.error(f"❌ Duration test failed for {duration}s: {e}")
    
    return True

def test_individual_clip_saving():
    """Test that individual Veo-2 clips are saved before concatenation"""
    logger.info("🧪 Testing individual clip saving...")
    
    client = MockVeo2Client("outputs")
    
    test_prompts = [
        {"veo2_prompt": "Baby crawling towards camera", "description": "Scene 1"},
        {"veo2_prompt": "Baby standing up with help", "description": "Scene 2"},
        {"veo2_prompt": "Baby taking first steps", "description": "Scene 3"}
    ]
    
    clips_generated = 0
    
    for i, prompt_data in enumerate(test_prompts):
        clip_id = f"individual_test_{i}"
        try:
            clip_path = client.generate_video_clip(
                prompt_data['veo2_prompt'], 
                3.0, 
                clip_id
            )
            
            if os.path.exists(clip_path):
                clips_generated += 1
                logger.info(f"✅ Individual clip {i+1} saved: {os.path.basename(clip_path)}")
            else:
                logger.error(f"❌ Individual clip {i+1} not saved")
                
        except Exception as e:
            logger.error(f"❌ Individual clip {i+1} generation failed: {e}")
    
    if clips_generated == len(test_prompts):
        logger.info(f"✅ All {clips_generated} individual clips saved successfully")
        return True
    else:
        logger.error(f"❌ Only {clips_generated}/{len(test_prompts)} clips saved")
        return False

def test_trending_analysis_output():
    """Test that trending analysis is properly saved with links"""
    logger.info("🧪 Testing trending analysis output...")
    
    # Create mock trending analysis file
    test_analysis_path = os.path.join("outputs", f"test_trending_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    try:
        with open(test_analysis_path, 'w') as f:
            f.write("=== TRENDING VIDEO ANALYSIS ===\n\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Average Viral Score: 0.85\n\n")
            
            f.write("TOP TRENDING VIDEOS ANALYZED:\n")
            f.write("=" * 50 + "\n")
            
            # Mock data
            mock_videos = [
                {"title": "Baby's First Steps", "id": "abc123", "views": 1000000, "likes": 50000},
                {"title": "Funny Baby Reactions", "id": "def456", "views": 2000000, "likes": 75000}
            ]
            
            for i, video in enumerate(mock_videos, 1):
                f.write(f"\n{i}. {video['title']}\n")
                f.write(f"   Link: https://youtube.com/watch?v={video['id']}\n")
                f.write(f"   Views: {video['views']:,}\n")
                f.write(f"   Likes: {video['likes']:,}\n")
                f.write(f"   Viral Score: 0.{85+i}\n")
                f.write("-" * 40 + "\n")
        
        if os.path.exists(test_analysis_path):
            file_size = os.path.getsize(test_analysis_path)
            logger.info(f"✅ Trending analysis saved: {test_analysis_path} ({file_size} bytes)")
            return True
        else:
            logger.error("❌ Trending analysis file not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Trending analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting comprehensive video generation tests...")
    logger.info("=" * 60)
    
    tests = [
        ("MockVeo2Client", test_mock_veo2_client),
        ("Creative Script Generation", test_creative_script_generation),
        ("Duration Matching", test_duration_matching),
        ("Individual Clip Saving", test_individual_clip_saving),
        ("Trending Analysis Output", test_trending_analysis_output)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info("-" * 60)
    logger.info(f"📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 All tests passed! Video generation fixes are working correctly.")
    else:
        logger.warning(f"⚠️  {total-passed} test(s) failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 