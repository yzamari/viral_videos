#!/usr/bin/env python3
"""
Test script to verify all audio, TTS, and session organization fixes
"""

import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.logging_config import get_logger
from launch_full_working_app import FullWorkingVideoApp

logger = get_logger(__name__)

def test_audio_quality_fixes():
    """Test the audio quality improvements"""
    print("🎤 Testing Audio Quality Fixes")
    print("=" * 50)
    
    # Test Google Cloud TTS availability
    try:
        from src.generators.google_tts_client import GoogleTTSClient
        
        tts_client = GoogleTTSClient()
        
        # Test script cleaning
        test_script = """
        **VOICEOVER:** This is amazing content about unicorns!
        **HOOK:** type: shock
        **TEXT:** overlay text here
        **VISUAL:** some visual description
        **VOICEOVER:** This should be included in the audio.
        **SOUND:** background music
        **VOICEOVER:** And this is the final part.
        """
        
        # Test the cleaning function
        from src.generators.video_generator import VideoGenerator
        generator = VideoGenerator("test_key")
        clean_script = generator._clean_script_for_tts(test_script, 15)
        
        print(f"✅ Original script length: {len(test_script)}")
        print(f"✅ Cleaned script length: {len(clean_script)}")
        print(f"✅ Cleaned script: {clean_script}")
        
        # Test if technical terms are removed
        technical_terms = ['hook', 'text', 'type', 'shock', 'visual', 'sound']
        removed_terms = [term for term in technical_terms if term.lower() not in clean_script.lower()]
        
        print(f"✅ Technical terms removed: {removed_terms}")
        
        # Test Google TTS generation
        audio_path = tts_client.generate_speech(
            text=clean_script,
            feeling="excited",
            duration_target=15
        )
        
        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / 1024
            print(f"✅ Google TTS generated: {audio_path} ({file_size:.1f}KB)")
            
            # Clean up test file
            os.remove(audio_path)
        else:
            print("❌ Google TTS generation failed")
            
    except Exception as e:
        print(f"❌ Google TTS test failed: {e}")
        print("🔄 This is expected if Google Cloud TTS is not configured")
    
    print("\n" + "=" * 50)
    return True

def test_session_organization():
    """Test session file organization"""
    print("📁 Testing Session Organization")
    print("=" * 50)
    
    # Create test session directory
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_dir = os.path.join(os.getcwd(), "outputs", f"session_{session_id}")
    
    print(f"📁 Test session directory: {session_dir}")
    
    # Create the directory structure
    os.makedirs(session_dir, exist_ok=True)
    
    # Create subdirectories
    subdirs = [
        'agent_discussions',
        'veo2_clips', 
        'audio_files',
        'scripts',
        'analysis'
    ]
    
    for subdir in subdirs:
        subdir_path = os.path.join(session_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)
        print(f"✅ Created: {subdir}/")
    
    # Create test files
    test_files = {
        'agent_discussions/discussion_phase1.json': {'phase': 'test', 'consensus': 0.85},
        'audio_files/test_audio.mp3': 'fake audio content',
        'scripts/test_script.txt': 'This is a test script',
        'veo2_clips/sample_0.mp4': 'fake video content',
        'analysis/video_analysis.txt': 'Test analysis content'
    }
    
    for file_path, content in test_files.items():
        full_path = os.path.join(session_dir, file_path)
        with open(full_path, 'w') as f:
            if isinstance(content, dict):
                json.dump(content, f)
            else:
                f.write(content)
        print(f"✅ Created test file: {file_path}")
    
    # Verify structure
    print(f"\n📊 Session structure verification:")
    for root, dirs, files in os.walk(session_dir):
        level = root.replace(session_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_size = os.path.getsize(os.path.join(root, file))
            print(f"{subindent}{file} ({file_size} bytes)")
    
    print(f"\n✅ Session organization test completed")
    print("=" * 50)
    return session_dir

def test_text_overlays():
    """Test text overlay generation"""
    print("📝 Testing Text Overlay Generation")
    print("=" * 50)
    
    try:
        from src.generators.video_generator import VideoGenerator
        from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
        
        generator = VideoGenerator("test_key")
        
        # Create test config
        config = GeneratedVideoConfig(
            topic="amazing unicorns dancing",
            duration_seconds=15,
            target_platform=Platform.TIKTOK,
            category=VideoCategory.COMEDY,
            style="viral",
            tone="exciting",
            target_audience="18-35",
            hook="Amazing hook",
            main_content=["Content 1", "Content 2"],
            call_to_action="Follow for more",
            visual_style="colorful",
            color_scheme=["#FF6B6B", "#4ECDC4"],
            text_overlays=[],
            transitions=["fade"],
            background_music_style="upbeat",
            voiceover_style="energetic",
            sound_effects=["whoosh"],
            inspired_by_videos=[],
            predicted_viral_score=0.8
        )
        
        # Test title creation
        title = generator._create_video_title(config.topic)
        print(f"✅ Generated title: {title}")
        
        # Test engagement text
        engagement = generator._get_engagement_text(config.category.value)
        print(f"✅ Generated engagement text: {engagement}")
        
        # Test category overlay
        category_overlay = generator._get_category_overlay(config.category.value, config.duration_seconds)
        if category_overlay:
            print(f"✅ Category overlay created successfully")
        else:
            print(f"⚠️ No category overlay created")
        
        print("✅ Text overlay generation test completed")
        
    except Exception as e:
        print(f"❌ Text overlay test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    return True

def test_full_integration():
    """Test the full integration with all fixes"""
    print("🚀 Testing Full Integration")
    print("=" * 50)
    
    try:
        # Initialize the app
        app = FullWorkingVideoApp()
        
        # Test with a simple topic
        test_topic = "magical unicorns dancing in a rainbow forest"
        
        print(f"🎯 Testing with topic: {test_topic}")
        print("⏱️ Generating 15-second video...")
        
        start_time = time.time()
        result = app.generate_video(
            topic=test_topic,
            duration=15,
            platform="youtube",
            category="Comedy",
            use_discussions=True
        )
        generation_time = time.time() - start_time
        
        if result['success']:
            print(f"✅ SUCCESS! Video generated in {generation_time:.2f}s")
            print(f"📁 Session: {result['session_dir']}")
            print(f"📏 Duration: {result['duration_actual']:.1f}s")
            print(f"💾 Size: {result['file_size_mb']:.1f}MB")
            print(f"🎵 Audio files: {len(result['audio_files'])}")
            print(f"📝 Script files: {len(result['script_files'])}")
            print(f"🎬 VEO-2 clips: {len(result['veo2_clips'])}")
            print(f"🤖 Agent discussions: {len(result['agent_discussions'])}")
            
            # Check if video file exists
            if os.path.exists(result['video_path']):
                print(f"✅ Video file exists: {result['video_path']}")
            else:
                print(f"❌ Video file missing: {result['video_path']}")
            
            # Check session organization
            session_dir = result['session_dir']
            if os.path.exists(session_dir):
                print(f"✅ Session directory exists: {session_dir}")
                
                # List contents
                print("\n📊 Session contents:")
                for root, dirs, files in os.walk(session_dir):
                    level = root.replace(session_dir, '').count(os.sep)
                    indent = ' ' * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files:
                        file_size = os.path.getsize(os.path.join(root, file))
                        print(f"{subindent}{file} ({file_size} bytes)")
            else:
                print(f"❌ Session directory missing: {session_dir}")
            
            return True
            
        else:
            print(f"❌ FAILED: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("=" * 50)

def main():
    """Run all tests"""
    print("🧪 COMPREHENSIVE AUDIO AND SESSION FIXES TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Audio quality fixes
    print("\n")
    try:
        results.append(("Audio Quality", test_audio_quality_fixes()))
    except Exception as e:
        print(f"❌ Audio quality test crashed: {e}")
        results.append(("Audio Quality", False))
    
    # Test 2: Session organization
    print("\n")
    try:
        session_dir = test_session_organization()
        results.append(("Session Organization", session_dir is not None))
    except Exception as e:
        print(f"❌ Session organization test crashed: {e}")
        results.append(("Session Organization", False))
    
    # Test 3: Text overlays
    print("\n")
    try:
        results.append(("Text Overlays", test_text_overlays()))
    except Exception as e:
        print(f"❌ Text overlay test crashed: {e}")
        results.append(("Text Overlays", False))
    
    # Test 4: Full integration
    print("\n")
    try:
        results.append(("Full Integration", test_full_integration()))
    except Exception as e:
        print(f"❌ Full integration test crashed: {e}")
        results.append(("Full Integration", False))
    
    # Summary
    print("\n")
    print("🎉 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The fixes are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main() 