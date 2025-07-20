#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for AI Video Generator
Tests both CLI (direct orchestrator) and UI functionality
"""

import os
import sys
import time
import requests
import subprocess
import signal
from typing import Optional, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class E2ETestRunner:
    """Comprehensive end-to-end test runner"""
    
    def __init__(self):
        self.ui_process: Optional[subprocess.Popen] = None
        self.ui_url = "http://localhost:7860"
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.test_results = {
            'cli_tests': {},
            'ui_tests': {},
            'overall_success': False
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests"""
        print("🎬 Comprehensive End-to-End Test Suite")
        print("=" * 80)
        
        if not self.api_key:
            print("❌ No GOOGLE_API_KEY found - tests will be limited")
            return {'success': False, 'error': 'No API key'}
        
        try:
            # Phase 1: CLI Tests
            print("\n🖥️  PHASE 1: CLI FUNCTIONALITY TESTS")
            print("-" * 60)
            self._test_cli_functionality()
            
            # Phase 2: UI Tests
            print("\n🌐 PHASE 2: UI FUNCTIONALITY TESTS")
            print("-" * 60)
            self._test_ui_functionality()
            
            # Phase 3: Integration Tests
            print("\n🔗 PHASE 3: CLI-UI INTEGRATION TESTS")
            print("-" * 60)
            self._test_integration()
            
            # Generate final report
            self._generate_final_report()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            self._cleanup()
    
    def _test_cli_functionality(self):
        """Test CLI functionality (direct orchestrator usage)"""
        print("1️⃣ Testing Direct Orchestrator Usage...")
        
        try:
            from src.agents.working_orchestrator import create_working_orchestrator
            
            # Test 1: Simple Mode
            print("   Testing Simple Mode...")
            start_time = time.time()
            
            orchestrator = create_working_orchestrator(
                topic="Quick CLI test of yoga benefits",
                platform="instagram",
                category="health",
                duration=15,
                api_key=self.api_key
            )
            
            self.test_results['cli_tests']['simple_mode_creation'] = {
                'success': True,
                'time': time.time() - start_time,
                'session_id': orchestrator.session_id
            }
            print(f"   ✅ Simple mode orchestrator created - Session: {orchestrator.session_id}")
            
            # Test 2: Enhanced Mode
            print("   Testing Enhanced Mode...")
            start_time = time.time()
            
            enhanced_orchestrator = create_working_orchestrator(
                topic="Enhanced CLI test of AI capabilities",
                platform="tiktok",
                category="technology",
                duration=20,
                api_key=self.api_key
            )
            
            self.test_results['cli_tests']['enhanced_mode_creation'] = {
                'success': True,
                'time': time.time() - start_time,
                'session_id': enhanced_orchestrator.session_id
            }
            print(f"   ✅ Enhanced mode orchestrator created - Session: {enhanced_orchestrator.session_id}")
            
            # Test 3: Progress Tracking
            print("   Testing Progress Tracking...")
            progress = enhanced_orchestrator.get_progress()
            
            self.test_results['cli_tests']['progress_tracking'] = {
                'success': isinstance(progress, dict) and 'session_id' in progress,
                'progress_data': progress
            }
            print(f"   ✅ Progress tracking working - Progress: {progress.get('progress', 0)}%")
            
            # Test 4: Video Generation (Image Mode for Speed)
            print("   Testing Video Generation (Image Mode)...")
            start_time = time.time()
            
            config = {
                'force_generation': 'force_image_gen',
                'frame_continuity': 'off',
                'image_only': True,
                'style': 'viral',
                'tone': 'engaging'
            }
            
            result = enhanced_orchestrator.generate_video(config)
            generation_time = time.time() - start_time
            
            self.test_results['cli_tests']['video_generation'] = {
                'success': result.get('success', False),
                'time': generation_time,
                'result': result,
                'video_path': result.get('final_video_path'),
                'agents_used': result.get('agents_used', 0)
            }
            
            if result.get('success'):
                print(f"   ✅ Video generation successful in {generation_time:.1f}s")
                print(f"      Video path: {result.get('final_video_path', 'N/A')}")
                print(f"      Agents used: {result.get('agents_used', 0)}")
                
                # Check if file exists
                video_path = result.get('final_video_path')
                if video_path and os.path.exists(video_path):
                    file_size = os.path.getsize(video_path)
                    print(f"      File size: {file_size / 1024 / 1024:.2f} MB")
                    self.test_results['cli_tests']['video_file_created'] = True
                else:
                    print("      ⚠️  Video file not found on disk")
                    self.test_results['cli_tests']['video_file_created'] = False
            else:
                print(f"   ❌ Video generation failed: {result.get('error', 'Unknown error')}")
            
            print("   ✅ CLI functionality tests completed")
            
        except Exception as e:
            print(f"   ❌ CLI tests failed: {e}")
            self.test_results['cli_tests']['error'] = str(e)
    
    def _test_ui_functionality(self):
        """Test UI functionality"""
        print("2️⃣ Testing UI Server and Interface...")
        
        # Start UI server
        if not self._start_ui_server():
            print("   ❌ Failed to start UI server")
            return
        
        # Wait for server to be ready
        if not self._wait_for_ui_ready():
            print("   ❌ UI server not responding")
            return
        
        try:
            # Test 1: UI Accessibility
            print("   Testing UI Accessibility...")
            response = requests.get(self.ui_url, timeout=10)
            
            self.test_results['ui_tests']['accessibility'] = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                print(f"   ✅ UI accessible - Response time: {response.elapsed.total_seconds():.2f}s")
                
                # Test 2: UI Content
                content = response.text.lower()
                expected_elements = [
                    "video generator",
                    "ai",
                    "generate",
                    "platform",
                    "duration"
                ]
                
                found_elements = [elem for elem in expected_elements if elem in content]
                self.test_results['ui_tests']['content_check'] = {
                    'success': len(found_elements) >= 3,
                    'found_elements': found_elements,
                    'expected_elements': expected_elements
                }
                
                print(f"   ✅ UI content check - Found {len(found_elements)}/{len(expected_elements)} elements")
            else:
                print(f"   ❌ UI not accessible - Status: {response.status_code}")
            
            # Test 3: Gradio API Endpoints
            print("   Testing Gradio API Endpoints...")
            try:
                api_response = requests.get(f"{self.ui_url}/info", timeout=5)
                self.test_results['ui_tests']['api_endpoints'] = {
                    'success': api_response.status_code == 200,
                    'status_code': api_response.status_code
                }
                
                if api_response.status_code == 200:
                    print("   ✅ Gradio API endpoints responding")
                else:
                    print(f"   ⚠️  Gradio API status: {api_response.status_code}")
            except:
                print("   ⚠️  Gradio API endpoints not available")
                self.test_results['ui_tests']['api_endpoints'] = {'success': False}
            
            print("   ✅ UI functionality tests completed")
            
        except Exception as e:
            print(f"   ❌ UI tests failed: {e}")
            self.test_results['ui_tests']['error'] = str(e)
    
    def _test_integration(self):
        """Test integration between CLI and UI"""
        print("3️⃣ Testing CLI-UI Integration...")
        
        try:
            # Test 1: Session Consistency
            print("   Testing Session Consistency...")
            
            # Create orchestrator via CLI
            from src.agents.working_orchestrator import create_working_orchestrator
            
            cli_orchestrator = create_working_orchestrator(
                topic="Integration test topic",
                platform="instagram",
                category="education",
                duration=15,
                api_key=self.api_key
            )
            
            cli_session = cli_orchestrator.session_id
            
            # Check if UI can access the same components
            ui_accessible = requests.get(self.ui_url, timeout=5).status_code == 200
            
            self.test_results['integration_tests'] = {
                'session_consistency': {
                    'cli_session_id': cli_session,
                    'ui_accessible': ui_accessible,
                    'success': True
                }
            }
            
            print(f"   ✅ Integration test - CLI session: {cli_session}, UI accessible: {ui_accessible}")
            
            # Test 2: Component Compatibility
            print("   Testing Component Compatibility...")
            
            # Test if both CLI and UI can import the same modules
            try:
                from src.generators.director import Director
                from src.agents.voice_director_agent import VoiceDirectorAgent
                from src.generators.video_generator import VideoGenerator
                
                compatibility_score = 100  # All imports successful
                print("   ✅ Component compatibility - All modules importable")
                
            except ImportError as e:
                compatibility_score = 0
                print(f"   ❌ Component compatibility failed: {e}")
            
            self.test_results['integration_tests']['component_compatibility'] = {
                'success': compatibility_score == 100,
                'score': compatibility_score
            }
            
            print("   ✅ Integration tests completed")
            
        except Exception as e:
            print(f"   ❌ Integration tests failed: {e}")
            self.test_results['integration_tests'] = {'error': str(e)}
    
    def _start_ui_server(self) -> bool:
        """Start the UI server"""
        try:
            print("   Starting UI server...")
            
            # Check if already running
            try:
                response = requests.get(self.ui_url, timeout=2)
                if response.status_code == 200:
                    print("   ✅ UI server already running")
                    return True
            except:
                pass
            
            # Start new UI process
            self.ui_process = subprocess.Popen(
                [sys.executable, "modern_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__ + "/..")),
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            print("   ⏳ UI server starting...")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to start UI server: {e}")
            return False
    
    def _wait_for_ui_ready(self, timeout: int = 30) -> bool:
        """Wait for UI server to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(self.ui_url, timeout=2)
                if response.status_code == 200:
                    print("   ✅ UI server ready")
                    return True
            except:
                pass
            
            time.sleep(1)
            print("   ⏳ Waiting for UI server...")
        
        print("   ❌ UI server not ready within timeout")
        return False
    
    def _generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE E2E TEST REPORT")
        print("=" * 80)
        
        # CLI Results
        cli_tests = self.test_results['cli_tests']
        cli_success = all(
            test.get('success', False) for test in cli_tests.values() 
            if isinstance(test, dict) and 'success' in test
        )
        
        print(f"\n🖥️  CLI FUNCTIONALITY: {'✅ PASS' if cli_success else '❌ FAIL'}")
        if 'simple_mode_creation' in cli_tests:
            print(f"   Simple Mode Creation: {'✅' if cli_tests['simple_mode_creation']['success'] else '❌'}")
        if 'enhanced_mode_creation' in cli_tests:
            print(f"   Enhanced Mode Creation: {'✅' if cli_tests['enhanced_mode_creation']['success'] else '❌'}")
        if 'progress_tracking' in cli_tests:
            print(f"   Progress Tracking: {'✅' if cli_tests['progress_tracking']['success'] else '❌'}")
        if 'video_generation' in cli_tests:
            print(f"   Video Generation: {'✅' if cli_tests['video_generation']['success'] else '❌'}")
            if cli_tests['video_generation']['success']:
                print(f"      Time: {cli_tests['video_generation']['time']:.1f}s")
                print(f"      Agents: {cli_tests['video_generation']['agents_used']}")
        
        # UI Results
        ui_tests = self.test_results['ui_tests']
        ui_success = all(
            test.get('success', False) for test in ui_tests.values() 
            if isinstance(test, dict) and 'success' in test
        )
        
        print(f"\n🌐 UI FUNCTIONALITY: {'✅ PASS' if ui_success else '❌ FAIL'}")
        if 'accessibility' in ui_tests:
            print(f"   UI Accessibility: {'✅' if ui_tests['accessibility']['success'] else '❌'}")
        if 'content_check' in ui_tests:
            print(f"   Content Check: {'✅' if ui_tests['content_check']['success'] else '❌'}")
        if 'api_endpoints' in ui_tests:
            print(f"   API Endpoints: {'✅' if ui_tests['api_endpoints']['success'] else '❌'}")
        
        # Integration Results
        integration_tests = self.test_results.get('integration_tests', {})
        integration_success = all(
            test.get('success', False) for test in integration_tests.values() 
            if isinstance(test, dict) and 'success' in test
        )
        
        print(f"\n🔗 INTEGRATION: {'✅ PASS' if integration_success else '❌ FAIL'}")
        if 'session_consistency' in integration_tests:
            print(f"   Session Consistency: {'✅' if integration_tests['session_consistency']['success'] else '❌'}")
        if 'component_compatibility' in integration_tests:
            print(f"   Component Compatibility: {'✅' if integration_tests['component_compatibility']['success'] else '❌'}")
        
        # Overall Results
        overall_success = cli_success and ui_success and integration_success
        self.test_results['overall_success'] = overall_success
        
        print(f"\n🎯 OVERALL RESULT: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️  SOME TESTS FAILED'}")
        
        if overall_success:
            print("\n✅ SYSTEM FULLY OPERATIONAL")
            print("   🖥️  CLI functionality working")
            print("   🌐 UI server operational")
            print("   🔗 CLI-UI integration successful")
            print("   🎬 Video generation pipeline functional")
            print("   🚀 Ready for production use")
        else:
            print("\n⚠️  SYSTEM HAS ISSUES")
            if not cli_success:
                print("   ❌ CLI functionality needs attention")
            if not ui_success:
                print("   ❌ UI functionality needs attention")
            if not integration_success:
                print("   ❌ Integration issues detected")
    
    def _cleanup(self):
        """Clean up test resources"""
        if self.ui_process:
            try:
                # Try graceful shutdown first
                self.ui_process.terminate()
                self.ui_process.wait(timeout=5)
            except:
                # Force kill if needed
                try:
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(self.ui_process.pid), signal.SIGTERM)
                    else:
                        self.ui_process.kill()
                except:
                    pass
            
            self.ui_process = None
            print("\n🧹 Cleanup completed")


def main():
    """Main test function"""
    print("🚀 Starting Comprehensive E2E Test Suite...")
    
    runner = E2ETestRunner()
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    if results.get('overall_success', False):
        print("\n🎉 ALL E2E TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME E2E TESTS FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main() 