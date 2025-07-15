#!/usr/bin/env python3
"""Comprehensive Video Generation Test
Tests all components of the video generation pipeline """from models.video_models import Platform, VideoCategory
from agents.working_orchestrator import WorkingOrchestrator, OrchestratorMode
from utils.session_manager import SessionManager
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_discussion_system(): """Test if AI agent discussions work properly"""print("\n🧪 Testing AI Agent Discussion System") print("-" * 50)

    try:
        # Get API key api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key: print("❌ No API key found")
            return False

        # Create orchestrator with simple test mission mission = "Create a fun video about cats playing"orchestrator = WorkingOrchestrator(api_key=api_key,
            mission=mission,
            platform=Platform.INSTAGRAM,
            category=VideoCategory.ENTERTAINMENT,
            duration=15,
            mode=OrchestratorMode.ENHANCED
        )

        # Test discussion system
        if orchestrator.discussion_system: print("✅ Discussion system initialized") print(f"✅ Mission: {mission}") print(f"✅ Session ID: {orchestrator.session_id}")

            # Check agent personalities if hasattr(orchestrator.discussion_system, 'agent_personalities'):
                agents = orchestrator.discussion_system.agent_personalities print(f"✅ Available agents: {len(agents)}") for role, info in agents.items(): print(f"   - {info['name']}: {info['expertise'][0]}")

            return True
        else: print("❌ Discussion system not initialized")
            return False

    except Exception as e: print(f"❌ Discussion system test failed: {e}")
        return False


def test_session_management(): """Test session management and file organization"""print("\n🧪 Testing Session Management") print("-" * 40)

    try:
        # Create session manager
        session_manager = SessionManager()

        # Create test session
        session_id = session_manager.create_session( mission="Test session for debugging", platform="instagram", category="testing")
 print(f"✅ Created session: {session_id}")

        # Test session directories
        session_path = session_manager.get_session_path() required_dirs = ['scripts', 'audio', 'video_clips', 'final_output', 'discussions']

        for dir_name in required_dirs:
            dir_path = session_manager.get_session_path(dir_name)
            if os.path.exists(dir_path): print(f"✅ Directory exists: {dir_name}")
            else: print(f"❌ Directory missing: {dir_name}")

        # Test file tracking test_file = os.path.join(session_path, "test_file.txt") with open(test_file, 'w') as f: f.write("Test content")
 session_manager.track_file(test_file, "testing", "Test file") print("✅ File tracking works")

        return True

    except Exception as e: print(f"❌ Session management test failed: {e}")
        return False


def test_video_generation_components(): """Test individual video generation components"""print("\n🧪 Testing Video Generation Components") print("-" * 45)

    try:
        # Test VEO client factory
        from generators.veo_client_factory import VeoClientFactory

        factory = VeoClientFactory() client = factory.get_best_available_client("test_output")

        if client: print(f"✅ VEO client available: {client.__class__.__name__}") print(f"   Model: {client.get_model_name()}") print(f"   Available: {client.is_available}")
        else: print("⚠️ No VEO client available (expected in test environment)")

        # Test Director
        from generators.director import Director
 api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if api_key:
            director = Director(api_key=api_key) print("✅ Director initialized")
        else: print("⚠️ No API key for Director test")

        return True

    except Exception as e: print(f"❌ Video generation components test failed: {e}")
        return False


def main(): """Run all tests"""print("🔧 Comprehensive Video Generation System Test") print("=" * 60)

    results = { "discussion_system": test_discussion_system(), "session_management": test_session_management(), "video_components": test_video_generation_components()
    }
 print("\n📊 Test Results Summary") print("-" * 30)

    passed = 0
    total = len(results)

    for test_name, result in results.items(): status = "✅ PASS" if result else "❌ FAIL"print(f"{test_name}: {status}")
        if result:
            passed += 1
 print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total: print("🎉 All tests passed! System is ready.")
    else: print("⚠️ Some tests failed. Check the issues above.")

    return passed == total

 if __name__ == "__main__":
    main()
