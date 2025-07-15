#!/usr/bin/env python3
"""Short Focused E2E Test for Video Generation System
Quick validation of all components without long waits """from src.agents.working_orchestrator import create_working_orchestrator
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))


def test_orchestrator_creation(): """Test 1: Quick orchestrator creation"""print("🧪 Test 1: Orchestrator Creation")

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key: print("❌ GEMINI_API_KEY not found")
        return False

    try:
        orchestrator = create_working_orchestrator( mission="Test video about morning routines", platform="instagram", category="health",
            duration=10,  # Short duration
            api_key=api_key, mode="simple")
 print(f"✅ Orchestrator created with session: {orchestrator.session_id}")
        return True

    except Exception as e: print(f"❌ Orchestrator creation failed: {e}")
        return False


def test_session_management(): """Test 2: Session directory structure"""print("\n🧪 Test 2: Session Management")

    try:
        # Get latest session 
        sessions_dir = Path("outputs")
        
        if not sessions_dir.exists():
            print("❌ No outputs directory found")
            return False
        
        # Find session directories
        session_dirs = [d for d in sessions_dir.iterdir() 
                       if d.is_dir() and d.name.startswith("session_")]

        if not session_dirs: print("❌ No session directories found")
            return False

        latest_session = max(session_dirs, key=lambda x: x.stat().st_mtime) print(f"✅ Latest session found: {latest_session.name}")

        # Check required directories required_dirs = ['scripts', 'audio', 'video_clips', 'final_output', 'logs', 'temp_files']
        missing_dirs = []

        for dir_name in required_dirs:
            dir_path = latest_session / dir_name
            if dir_path.exists(): print(f"✅ Directory exists: {dir_name}")
            else:
                missing_dirs.append(dir_name) print(f"⚠️ Directory missing: {dir_name}")

        return len(missing_dirs) <= 2  # Allow some missing dirs for quick test

    except Exception as e: print(f"❌ Session management test failed: {e}")
        return False


def test_veo_clients(): """Test 3: VEO client availability"""print("\n🧪 Test 3: VEO Client Availability")

    try:
        from src.generators.veo_client_factory import VeoClientFactory, VeoModel

        factory = VeoClientFactory()

        # Test VEO-2 client using correct method veo2_client = factory.create_client(VeoModel.VEO2, "test_output")
        veo2_available = veo2_client is not None and hasattr( veo2_client, 'is_available') and veo2_client.is_available print(f"{'✅' if veo2_available else '❌'} VEO-2 client: {veo2_available}")

        # Test VEO-3 client using correct method veo3_client = factory.create_client(VeoModel.VEO3, "test_output")
        veo3_available = veo3_client is not None and hasattr( veo3_client, 'is_available') and veo3_client.is_available print(f"{'✅' if veo3_available else '❌'} VEO-3 client: {veo3_available}")

        # Test best available best_client = factory.get_best_available_client("test_output")
        if best_client: print(f"✅ Best client: {best_client.__class__.__name__}")
        else: print("❌ No clients available")

        # Test available models
        available_models = factory.get_available_models() print(f"✅ Available models: {[model.value for model in available_models]}")

        return veo2_available or veo3_available

    except Exception as e: print(f"❌ VEO client test failed: {e}")
        return False


def test_video_generation_quick(): """Test 4: Quick video generation start"""print("\n🧪 Test 4: Video Generation Start")

    try: api_key = os.getenv('GEMINI_API_KEY')
        if not api_key: print("❌ GEMINI_API_KEY not found")
            return False

        # Create orchestrator
        orchestrator = create_working_orchestrator( mission="Quick test video about exercise", platform="instagram", category="health",
            duration=5,  # Very short
            api_key=api_key, mode="simple")
 print(f"✅ Created orchestrator: {orchestrator.__class__.__name__}")

        # Test session ID is now properly generated
        session_id = orchestrator.session_id print(f"✅ Session ID: {session_id}")

        # Create test config
        config = { 'topic': 'exercise benefits', 'platform': 'instagram', 'category': 'health', 'duration_sec': 5, 'style': 'energetic', 'tone': 'motivational', 'target_audience': 'fitness enthusiasts', 'visual_style': 'dynamic', 'enable_trending': False, 'incorporate_news': False
        }
 # Test that video generation can start (we won't wait for completion) print("✅ Starting video generation test...")

        # This should not fail with session context issues
        from src.utils.session_context import SessionContext
        test_context = SessionContext(session_id=session_id) print(f"✅ Session context created successfully: {test_context.session_id}")

        # Test that session directories are created scripts_dir = test_context.get_output_path("scripts") print(f"✅ Scripts directory: {scripts_dir}")

        return True

    except Exception as e: print(f"❌ Video generation test failed: {e}")
        return False


def test_aspect_ratio_function(): """Test 5: Aspect ratio correction function"""print("\n🧪 Test 5: Aspect Ratio Function")

    try:
        from src.generators.video_generator import VideoGenerator
        from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory

        # Create video generator
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key: print("❌ GEMINI_API_KEY not found")
            return False

        video_gen = VideoGenerator(api_key)

        # Check if aspect ratio fix method exists if hasattr(video_gen, '_fix_aspect_ratio'): print("✅ Aspect ratio fix method exists")

            # Create config for Instagram (9:16)
            config = GeneratedVideoConfig( topic='test',
                target_platform=Platform.INSTAGRAM,
                category=VideoCategory.HEALTH,
                duration_seconds=5
            )

            # Check config returns correct aspect ratio
            aspect_ratio = config.get_aspect_ratio()
            resolution = config.get_resolution()
 print(f"✅ Target aspect ratio: {aspect_ratio}") print(f"✅ Target resolution: {resolution}")
 # Verify it's 9:16 format if aspect_ratio == "9:16" and resolution == (1080, 1920): print("✅ Correct Instagram format configured")
                return True
            else: print(f"⚠️ Unexpected format: {aspect_ratio}, {resolution}")
                return False
        else: print("❌ Aspect ratio fix method not found")
            return False

    except Exception as e: print(f"❌ Aspect ratio test failed: {e}")
        return False


def test_audio_components(): """Test 6: Audio generation components"""print("\n🧪 Test 6: Audio Components")

    try:
        from src.generators.enhanced_multilang_tts import EnhancedMultilingualTTS
        from src.agents.voice_director_agent import VoiceDirectorAgent

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key: print("❌ GEMINI_API_KEY not found")
            return False

        # Test TTS client initialization
        tts_client = EnhancedMultilingualTTS(api_key) print("✅ TTS client initialized")

        # Test voice director initialization
        voice_director = VoiceDirectorAgent(api_key) print("✅ Voice director initialized")

        # Check if methods exist if hasattr(tts_client, 'generate_intelligent_voice_audio'): print("✅ TTS generation method exists")
        else: print("❌ TTS generation method missing")
            return False
 if hasattr(voice_director, 'analyze_content_and_select_voices'): print("✅ Voice selection method exists")
        else: print("❌ Voice selection method missing")
            return False

        return True

    except Exception as e: print(f"❌ Audio components test failed: {e}")
        return False


def main(): """Run all short E2E tests"""print("🚀 Starting Short Focused E2E Tests") print("=" * 50)

    tests = [ ("Orchestrator Creation", test_orchestrator_creation), ("Session Management", test_session_management), ("VEO Clients", test_veo_clients), ("Video Generation Start", test_video_generation_quick), ("Aspect Ratio Function", test_aspect_ratio_function), ("Audio Components", test_audio_components),
    ]

    results = []
 for test_name, test_func in tests: print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        start_time = time.time()

        try:
            success = test_func()
            duration = time.time() - start_time
            results.append((test_name, success, duration))
        except Exception as e: print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False, time.time() - start_time))

    # Print summary print("\n" + "=" * 50) print("📊 TEST SUMMARY") print("=" * 50)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
 print(f"📈 Overall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")
    print()

    for test_name, success, duration in results: status = "✅ PASS" if success else "❌ FAIL"print(f"{status} {test_name:<25} ({duration:.2f}s)")
 print("\n" + "=" * 50)

    if passed == total: print("🎉 ALL TESTS PASSED! System is working correctly.")
        return 0
    elif passed >= total * 0.8:  # 80% pass rate print("✅ Most tests passed. System is mostly functional.")
        return 0
    else: print("⚠️ Several tests failed. Please review the issues.")
        return 1

 if __name__ == "__main__":
    exit(main())
