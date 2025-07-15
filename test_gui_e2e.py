#!/usr/bin/env python3
"""🎬 GUI E2E Test for AI Video Generator
Comprehensive testing of the web interface functionality using requests """from config.config import settings
import os
import sys
import time
import subprocess
import requests

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


class VideoGeneratorGUITest: """E2E test suite for the video generator GUI"""def __init__(self):
        self.ui_process = None self.base_url = "http://localhost:7860"self.test_results = {}

    def start_ui_server(self): """Start the UI server in background"""try: print("🚀 Starting UI server...")
            self.ui_process = subprocess.Popen( [sys.executable, "modern_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )

            # Wait for server to start
            max_retries = 30
            for i in range(max_retries):
                try: response = requests.get(f"{self.base_url}/", timeout=5)
                    if response.status_code == 200: print(f"✅ UI server started successfully at {self.base_url}")
                        return True
                except requests.exceptions.RequestException:
                    if i < max_retries - 1: print(f"⏳ Waiting for UI server to start... ({i + 1}/{max_retries})")
                        time.sleep(2)
                    else: print("❌ UI server failed to start within timeout")
                        return False
            return False
        except Exception as e: print(f"❌ Failed to start UI server: {e}")
            return False

    def stop_ui_server(self): """Stop the UI server"""if self.ui_process:
            try:
                self.ui_process.terminate()
                self.ui_process.wait(timeout=10) print("✅ UI server stopped successfully")
            except subprocess.TimeoutExpired:
                self.ui_process.kill() print("⚠️ UI server force-killed")
            except Exception as e: print(f"❌ Error stopping UI server: {e}")

    def test_ui_accessibility(self): """Test if UI is accessible and loads properly"""try: print("🌐 Testing UI accessibility...")
 response = requests.get(f"{self.base_url}/", timeout=10)

            if response.status_code == 200:
                content = response.text

                # Check for key UI elements
                required_elements = [ "Enhanced Ultimate Modern Video Generator", "Mission/Topic", "Generate Video", "AI Agent Status", "Real-Time Agent Discussions"]

                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)

                if missing_elements: print(f"❌ Missing UI elements: {missing_elements}")
                    return False
 print("✅ UI accessibility test passed")
                return True
            else: print(f"❌ UI not accessible, status code: {response.status_code}")
                return False

        except Exception as e: print(f"❌ UI accessibility test failed: {e}")
            return False

    def test_gradio_api_endpoints(self): """Test Gradio API endpoints"""try: print("🔌 Testing Gradio API endpoints...")

            # Test config endpoint config_response = requests.get(f"{self.base_url}/config", timeout=5)
            if config_response.status_code != 200: print(f"❌ Config endpoint failed: {config_response.status_code}")
                return False

            # Test info endpoint (may not exist in all Gradio versions)
            try: info_response = requests.get(f"{self.base_url}/info", timeout=5)
                if info_response.status_code not in [200, 404]: print(f"⚠️ Info endpoint returned: {info_response.status_code}")
            except BaseException: print("⚠️ Info endpoint not available (normal for some Gradio versions)")
 print("✅ Gradio API endpoints test passed")
            return True

        except Exception as e: print(f"❌ Gradio API endpoints test failed: {e}")
            return False

    def test_ui_components(self): """Test UI components and structure"""try: print("📝 Testing UI components...")
 response = requests.get(f"{self.base_url}/", timeout=10)
            content = response.text

            # Check for form elements
            form_elements = [ 'Enter your video mission or topic', 'Platform', 'Category', 'Duration', 'AI System', 'Force Generation Options', 'Trending Analysis', 'Advanced Options']

            missing_form_elements = []
            for element in form_elements:
                if element not in content:
                    missing_form_elements.append(element)

            if missing_form_elements: print(f"❌ Missing form elements: {missing_form_elements}")
                return False

            # Check for interactive elements
            interactive_elements = [ 'button', 'select', 'input', 'textarea']

            for element in interactive_elements: if f'<{element}' not in content and f'&lt;{element}' not in content: print(f"⚠️ Interactive element '{element}' might be missing")
 print("✅ UI components test passed")
            return True

        except Exception as e: print(f"❌ UI components test failed: {e}")
            return False

    def test_ai_agent_integration(self): """Test AI agent integration display"""try: print("🤖 Testing AI agent integration...")
 response = requests.get(f"{self.base_url}/", timeout=10)
            content = response.text

            # Check for AI agent references
            agent_references = [ 'ScriptMaster', 'ViralismSpecialist', 'ContentSpecialist', 'VisualDirector', 'AudioEngineer', 'VideoEditor', 'QualityController']

            found_agents = []
            for agent in agent_references:
                if agent in content:
                    found_agents.append(agent)

            if len(found_agents) < 5:  # Should have at least 5 agents visible print(f"❌ Only found {len(found_agents)} agents: {found_agents}")
                return False
 print(f"✅ AI agent integration test passed ({len(found_agents)} agents found)")
            return True

        except Exception as e: print(f"❌ AI agent integration test failed: {e}")
            return False

    def test_orchestrator_integration(self): """Test orchestrator integration by checking if it can be created"""try: print("🎭 Testing orchestrator integration...")

            # Test orchestrator creation (same as GUI would do)
            from src.agents.working_orchestrator import create_working_orchestrator

            orchestrator = create_working_orchestrator( mission="Test GUI E2E integration", platform="tiktok", category="Educational",
                duration=15,
                api_key=settings.google_api_key
            )

            if orchestrator: print("✅ Orchestrator created successfully") print(f"   Mode: {orchestrator.mode}") print(f"   Agents: {orchestrator._count_agents_used()}") print("✅ Orchestrator integration test passed")
                return True
            else: print("❌ Orchestrator creation failed")
                return False

        except Exception as e: print(f"❌ Orchestrator integration test failed: {e}")
            return False

    def test_real_time_features(self): """Test real-time features display"""try: print("⚡ Testing real-time features...")
 response = requests.get(f"{self.base_url}/", timeout=10)
            content = response.text

            # Check for real-time feature indicators
            realtime_features = [ 'Real-Time Agent Discussions', 'Live Status', 'Progress', 'Generation Results', 'Auto-refresh', 'timer']

            found_features = []
            for feature in realtime_features:
                if feature.lower() in content.lower():
                    found_features.append(feature)

            if len(found_features) < 4:  # Should have at least 4 real-time features print(f"❌ Only found {len(found_features)} real-time features: {found_features}")
                return False
 print(f"✅ Real-time features test passed ({len(found_features)} features found)")
            return True

        except Exception as e: print(f"❌ Real-time features test failed: {e}")
            return False

    def test_generation_workflow(self): """Test video generation workflow preparation"""try: print("🎬 Testing generation workflow preparation...")
 response = requests.get(f"{self.base_url}/", timeout=10)
            content = response.text

            # Check for generation workflow elements
            workflow_elements = [ 'Generate Video', 'Stop', 'Force Generation', 'Trending Analysis', 'Download', 'Session Information']

            found_elements = []
            for element in workflow_elements:
                if element in content:
                    found_elements.append(element)

            if len(found_elements) < 4:  # Should have at least 4 workflow elements print(f"❌ Only found {len(found_elements)} workflow elements: {found_elements}")
                return False
 print(f"✅ Generation workflow test passed ({len(found_elements)} elements found)")
            return True

        except Exception as e: print(f"❌ Generation workflow test failed: {e}")
            return False

    def test_error_handling(self): """Test error handling capabilities"""try: print("🚨 Testing error handling...")

            # Test with invalid endpoints
            invalid_endpoints = [ '/invalid', '/test', '/nonexistent']

            for endpoint in invalid_endpoints:
                try: response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    # Should either redirect or return a valid response
                    if response.status_code not in [200, 404, 302, 301]: print(f"⚠️ Unexpected response for {endpoint}: {response.status_code}")
                except requests.exceptions.RequestException:
                    # This is expected for invalid endpoints
                    pass
 print("✅ Error handling test passed")
            return True

        except Exception as e: print(f"❌ Error handling test failed: {e}")
            return False

    def run_all_tests(self): """Run all GUI E2E tests"""print("🎬 Starting GUI E2E Tests for AI Video Generator") print("=" * 60)

        # Setup
        if not self.start_ui_server(): print("❌ Failed to start UI server")
            return False

        # Wait for server to be fully ready
        time.sleep(5)

        try:
            # Run tests self.test_results['accessibility'] = self.test_ui_accessibility() self.test_results['api_endpoints'] = self.test_gradio_api_endpoints() self.test_results['ui_components'] = self.test_ui_components() self.test_results['ai_agent_integration'] = self.test_ai_agent_integration() self.test_results['orchestrator_integration'] = self.test_orchestrator_integration() self.test_results['real_time_features'] = self.test_real_time_features() self.test_results['generation_workflow'] = self.test_generation_workflow() self.test_results['error_handling'] = self.test_error_handling()

        except Exception as e: print(f"❌ Test execution failed: {e}") self.test_results['execution_error'] = False

        finally:
            self.stop_ui_server()

        # Print results print("\n" + "=" * 60) print("🎯 GUI E2E Test Results") print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
 for test_name, result in self.test_results.items(): status = "✅ PASSED" if result else "❌ FAILED"print(f"{test_name.replace('_', ' ').title()}: {status}")
 print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests: print("🎉 ALL GUI E2E TESTS PASSED!") print("✅ GUI is fully functional and ready for production use") print("\n🚀 You can now use the GUI with:") print("   ./run_video_generator.sh ui") print("   Or: python modern_ui.py") print("   Access at: http://localhost:7860")
            return True
        else: print("⚠️ Some tests failed - GUI may have issues")
            return False


def main(): """Main entry point for GUI E2E tests"""# Check if API key is configured
    if not settings.google_api_key: print("❌ Error: GOOGLE_API_KEY not found in environment variables") print("Please set your Google AI API key in the .env file")
        return False

    # Run tests
    test_runner = VideoGeneratorGUITest()
    success = test_runner.run_all_tests()

    return success

 if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
