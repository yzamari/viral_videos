#!/usr/bin/env python3
"""
Simple Test Runner for AI Video Generator
Runs basic tests to verify system functionality
"""

import unittest
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 AI Video Generator - Basic Test Suite")
    print("=" * 60)
    
    test_results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Test 1: Import Core Components
    print("\n1️⃣ Testing Core Component Imports")
    try:
        from src.generators.director import Director
        from src.agents.voice_director_agent import VoiceDirectorAgent
        from src.agents.continuity_decision_agent import ContinuityDecisionAgent
        print("✅ Core agents imported successfully")
        test_results['passed'] += 1
    except ImportError as e:
        print(f"❌ Core agent import failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Test 2: Import Working Orchestrator
    print("\n2️⃣ Testing Working Orchestrator Import")
    try:
        from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
        print("✅ Working orchestrator imported successfully")
        test_results['passed'] += 1
    except ImportError as e:
        print(f"❌ Working orchestrator import failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Test 3: Create Orchestrator Instance
    print("\n3️⃣ Testing Orchestrator Creation")
    try:
        from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
        
        orchestrator = create_working_simple_orchestrator(
            topic="Test video generation",
            platform="instagram",
            category="education",
            duration=25,
            api_key=os.getenv('GOOGLE_API_KEY', 'test_key'),
            mode="simple"
        )
        
        if orchestrator is not None:
            print("✅ Orchestrator created successfully")
            print(f"   Session ID: {orchestrator.session_id}")
            print(f"   Agents used: {orchestrator._count_agents_used()}")
            test_results['passed'] += 1
        else:
            print("❌ Orchestrator creation returned None")
            test_results['failed'] += 1
    except Exception as e:
        print(f"❌ Orchestrator creation failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Test 4: Progress Tracking
    print("\n4️⃣ Testing Progress Tracking")
    try:
        progress = orchestrator.get_progress()
        if isinstance(progress, dict) and 'session_id' in progress:
            print("✅ Progress tracking working")
            print(f"   Progress: {progress.get('progress', 0)}%")
            print(f"   Phase: {progress.get('current_phase', 'unknown')}")
            test_results['passed'] += 1
        else:
            print("❌ Progress tracking returned invalid data")
            test_results['failed'] += 1
    except Exception as e:
        print(f"❌ Progress tracking failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Test 5: Agent Initialization
    print("\n5️⃣ Testing Individual Agent Initialization")
    try:
        api_key = os.getenv('GOOGLE_API_KEY', 'test_key')
        
        # Test Director
        director = Director(api_key)
        print("✅ Director agent initialized")
        
        # Test Voice Director
        voice_agent = VoiceDirectorAgent(api_key)
        print("✅ Voice Director agent initialized")
        
        # Test Continuity Agent
        continuity_agent = ContinuityDecisionAgent(api_key)
        print("✅ Continuity agent initialized")
        
        test_results['passed'] += 1
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Test 6: UI Component Check
    print("\n6️⃣ Testing UI Component Availability")
    try:
        import modern_ui
        print("✅ Modern UI module available")
        test_results['passed'] += 1
    except ImportError as e:
        print(f"❌ Modern UI import failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Test 7: Video Generator Import
    print("\n7️⃣ Testing Video Generator Import")
    try:
        from src.generators.video_generator import VideoGenerator
        print("✅ Video generator imported successfully")
        test_results['passed'] += 1
    except ImportError as e:
        print(f"❌ Video generator import failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Test 8: Model Enums
    print("\n8️⃣ Testing Model Enums")
    try:
        from src.models.video_models import Platform, VideoCategory, Language
        
        # Test enum values
        platform = Platform.INSTAGRAM
        category = VideoCategory.EDUCATION
        language = Language.ENGLISH_US
        
        print("✅ Model enums working")
        print(f"   Platform: {platform.value}")
        print(f"   Category: {category.value}")
        print(f"   Language: {language.value}")
        test_results['passed'] += 1
    except Exception as e:
        print(f"❌ Model enums failed: {e}")
        test_results['failed'] += 1
    test_results['total'] += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    
    success_rate = (test_results['passed'] / test_results['total']) * 100 if test_results['total'] > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if test_results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        return True
    else:
        print(f"\n⚠️  {test_results['failed']} test(s) failed. Please check the issues above.")
        return False

def check_system_status():
    """Check overall system status"""
    print("\n🔧 SYSTEM STATUS CHECK")
    print("-" * 40)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key and len(api_key) > 10:
        print("✅ API key configured")
    else:
        print("⚠️  API key not configured or invalid")
    
    # Check UI server
    try:
        import requests
        response = requests.get("http://localhost:7860", timeout=2)
        if response.status_code == 200:
            print("✅ UI server running at http://localhost:7860")
        else:
            print("⚠️  UI server not responding properly")
    except:
        print("⚠️  UI server not running")
    
    # Check output directory
    if os.path.exists('outputs'):
        print("✅ Output directory exists")
    else:
        print("⚠️  Output directory missing")
    
    # Check key files
    key_files = [
        'modern_ui.py',
        'src/agents/working_simple_orchestrator.py',
        'src/generators/video_generator.py',
        'src/generators/director.py'
    ]
    
    missing_files = []
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} key files")
        return False
    else:
        print("\n✅ All key files present")
        return True

def main():
    """Main test function"""
    print("🚀 Starting Basic System Tests...")
    
    # Check system status first
    system_ok = check_system_status()
    
    # Run basic tests
    tests_ok = run_basic_tests()
    
    # Final verdict
    print("\n" + "=" * 60)
    print("🎯 FINAL VERDICT")
    print("=" * 60)
    
    if system_ok and tests_ok:
        print("🎉 SYSTEM FULLY OPERATIONAL")
        print("✅ All components working correctly")
        print("✅ Ready for video generation")
        print("🌐 Access UI at: http://localhost:7860")
        return 0
    else:
        print("⚠️  SYSTEM HAS ISSUES")
        if not system_ok:
            print("❌ System status check failed")
        if not tests_ok:
            print("❌ Basic tests failed")
        print("🔧 Please fix issues before using")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 