#!/usr/bin/env python3
"""
Comprehensive test to verify all critical fixes
"""

import os
import sys
import json
from datetime import datetime


def test_template_formatting():
    """Test if template formatting is fixed"""
    print("🧪 Testing Template String Formatting...")

    # Test the Director class directly
    sys.path.insert(0, 'src')

    try:
        from generators.director import Director
        from models.video_models import Platform, VideoCategory

        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ No API key for Director test")
            return False

        # Create Director instance
        director = Director(api_key)

        # Test script generation
        test_mission = "Create educational content about renewable energy"

        script_result = director.write_script(
            topic=test_mission,
            style="educational",
            duration=30,
            platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATION,
            patterns={'hooks': [], 'themes': [], 'success_factors': []},
            incorporate_news=False
        )

        # Check if script contains the actual mission
        script_str = json.dumps(script_result, indent=2)

        if 'renewable' in script_str.lower() and 'energy' in script_str.lower():
            print("✅ Template formatting is WORKING - script contains mission content")
            return True
        else:
            print("❌ Template formatting FAILED - script doesn't contain mission")
            print(f"   Script preview: {script_str[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Template formatting test failed: {e}")
        return False


def test_session_integration():
    """Test session management integration"""
    print("🧪 Testing Session Management...")

    try:
        from utils.session_manager import session_manager

        # Create test session
        test_session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session_id = session_manager.create_session(
            session_id=test_session_id,
            mission="Test renewable energy video",
            category="education",
            platform="youtube"
        )

        # Test session path
        session_path = session_manager.get_session_path()

        if os.path.exists(session_path):
            print(f"✅ Session management WORKING - session created at: {session_path}")

            # Test script saving
            test_script = {"text": "This is a test script about renewable energy"}
            script_file = session_manager.save_script(test_script, "test_script.json")

            if os.path.exists(script_file):
                print("✅ Script saving WORKING")
                return True
            else:
                print("❌ Script saving FAILED")
                return False
        else:
            print("❌ Session management FAILED - no session directory")
            return False

    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False


def test_working_orchestrator():
    """Test the WorkingOrchestrator with fixed components"""
    print("🧪 Testing WorkingOrchestrator...")

    try:
        from agents.working_orchestrator import WorkingOrchestrator, OrchestratorMode
        from models.video_models import Platform, VideoCategory

        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ No API key for orchestrator test")
            return False

        # Create orchestrator
        orchestrator = WorkingOrchestrator(
            api_key=api_key,
            mission="Create educational content about renewable energy",
            platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATION,
            duration=30,
            mode=OrchestratorMode.SIMPLE  # Use simple mode for faster testing
        )

        # Test session ID generation
        session_id = orchestrator.session_id

        if session_id and session_id.startswith('session_'):
            print(f"✅ WorkingOrchestrator WORKING - session ID: {session_id}")
            return True
        else:
            print("❌ WorkingOrchestrator FAILED - no valid session ID")
            return False

    except Exception as e:
        print(f"❌ WorkingOrchestrator test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("�� COMPREHENSIVE FIX VERIFICATION")
    print("=" * 50)

    tests = [
        ("Template Formatting", test_template_formatting),
        ("Session Integration", test_session_integration),
        ("Working Orchestrator", test_working_orchestrator)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
            print()

    # Summary
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 30)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 ALL CRITICAL FIXES ARE WORKING!")
        return True
    else:
        print("❌ Some fixes still need work")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
