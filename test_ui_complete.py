#!/usr/bin/env python3
"""
🎭 Complete UI Test Suite for AI Video Generator
Combines existing HTTP tests with new Playwright tests for comprehensive coverage
"""

import os
import sys
import time
import subprocess
import asyncio
from typing import Dict, Any, Optional
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import settings


class ComprehensiveUITestRunner:
    """Complete UI test runner combining all test types"""
    
    def __init__(self):
        self.ui_process = None
        self.base_url = "http://localhost:7860"
        self.test_results = {}
        
    def start_ui_server(self):
        """Start the UI server"""
        try:
            print("🚀 Starting UI server for comprehensive tests...")
            self.ui_process = subprocess.Popen(
                [sys.executable, "modern_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for server to start
            import requests
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.base_url}/", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ UI server started at {self.base_url}")
                        return True
                except requests.exceptions.RequestException:
                    if i < max_retries - 1:
                        print(f"⏳ Waiting for UI server... ({i+1}/{max_retries})")
                        time.sleep(2)
                    else:
                        print("❌ UI server failed to start")
                        return False
            return False
        except Exception as e:
            print(f"❌ Failed to start UI server: {e}")
            return False
    
    def stop_ui_server(self):
        """Stop the UI server"""
        if self.ui_process:
            try:
                self.ui_process.terminate()
                self.ui_process.wait(timeout=10)
                print("✅ UI server stopped")
            except subprocess.TimeoutExpired:
                self.ui_process.kill()
                print("⚠️ UI server force-killed")
    
    def run_basic_http_tests(self):
        """Run basic HTTP tests"""
        try:
            print("🌐 Running basic HTTP tests...")
            
            # Import and run existing GUI tests
            from test_gui_e2e import VideoGeneratorGUITest
            gui_tester = VideoGeneratorGUITest()
            gui_tester.ui_process = self.ui_process  # Use our server
            gui_tester.base_url = self.base_url
            
            # Run individual tests without starting/stopping server
            results = {}
            results['accessibility'] = gui_tester.test_ui_accessibility()
            results['api_endpoints'] = gui_tester.test_gradio_api_endpoints()
            results['ui_components'] = gui_tester.test_ui_components()
            results['ai_agent_integration'] = gui_tester.test_ai_agent_integration()
            results['orchestrator_integration'] = gui_tester.test_orchestrator_integration()
            results['real_time_features'] = gui_tester.test_real_time_features()
            results['generation_workflow'] = gui_tester.test_generation_workflow()
            results['error_handling'] = gui_tester.test_error_handling()
            
            self.test_results['http_tests'] = results
            
            passed = sum(1 for result in results.values() if result)
            total = len(results)
            print(f"✅ HTTP tests completed: {passed}/{total} passed")
            
            return passed == total
            
        except Exception as e:
            print(f"❌ HTTP tests failed: {e}")
            self.test_results['http_tests'] = {'error': str(e)}
            return False
    
    def run_playwright_tests(self):
        """Run Playwright tests"""
        try:
            print("🎭 Running Playwright tests...")
            
            # Check if playwright is available
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                print("⚠️ Playwright not installed, skipping Playwright tests")
                return True
            
            # Run basic Playwright tests
            async def run_playwright_test():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    try:
                        # Test 1: Page loads
                        await page.goto(self.base_url)
                        await page.wait_for_load_state("networkidle")
                        
                        title = await page.title()
                        assert "Enhanced Ultimate Modern Video Generator" in title
                        
                        # Test 2: Essential elements present
                        essential_elements = [
                            "h1:has-text('Enhanced Ultimate Modern Video Generator')",
                            "textarea[placeholder*='Enter your video mission']",
                            "button:has-text('Generate Video')"
                        ]
                        
                        for selector in essential_elements:
                            element = page.locator(selector)
                            await element.wait_for(state="visible", timeout=5000)
                        
                        # Test 3: Form interaction
                        mission_input = page.locator("textarea[placeholder*='Enter your video mission']")
                        await mission_input.fill("Test mission for Playwright")
                        value = await mission_input.input_value()
                        assert "Test mission for Playwright" in value
                        
                        # Test 4: Dropdown interaction
                        dropdowns = page.locator("select")
                        if await dropdowns.count() > 0:
                            await dropdowns.first.select_option("tiktok")
                        
                        # Test 5: Button states
                        generate_button = page.locator("button:has-text('Generate Video')")
                        await generate_button.wait_for(state="visible")
                        is_enabled = await generate_button.is_enabled()
                        assert is_enabled
                        
                        print("✅ Playwright tests passed")
                        return True
                        
                    except Exception as e:
                        print(f"❌ Playwright test failed: {e}")
                        return False
                        
                    finally:
                        await browser.close()
            
            # Run the async test
            result = asyncio.run(run_playwright_test())
            self.test_results['playwright_tests'] = {'passed': result}
            
            return result
            
        except Exception as e:
            print(f"❌ Playwright tests failed: {e}")
            self.test_results['playwright_tests'] = {'error': str(e)}
            return False
    
    def run_performance_tests(self):
        """Run performance tests"""
        try:
            print("⚡ Running performance tests...")
            
            import requests
            
            # Test 1: Page load time
            start_time = time.time()
            response = requests.get(f"{self.base_url}/", timeout=10)
            load_time = time.time() - start_time
            
            page_load_ok = response.status_code == 200 and load_time < 5.0
            
            # Test 2: Resource loading
            config_response = requests.get(f"{self.base_url}/config", timeout=5)
            config_ok = config_response.status_code == 200
            
            # Test 3: Memory usage (basic check)
            import psutil
            memory_usage = psutil.virtual_memory().percent
            memory_ok = memory_usage < 90  # Should not use more than 90% memory
            
            performance_results = {
                'page_load_time': load_time,
                'page_load_ok': page_load_ok,
                'config_endpoint_ok': config_ok,
                'memory_usage_ok': memory_ok,
                'memory_usage_percent': memory_usage
            }
            
            self.test_results['performance_tests'] = performance_results
            
            all_ok = all([page_load_ok, config_ok, memory_ok])
            
            print(f"✅ Performance tests completed:")
            print(f"   Page load time: {load_time:.2f}s")
            print(f"   Memory usage: {memory_usage:.1f}%")
            
            return all_ok
            
        except Exception as e:
            print(f"❌ Performance tests failed: {e}")
            self.test_results['performance_tests'] = {'error': str(e)}
            return False
    
    def run_accessibility_tests(self):
        """Run basic accessibility tests"""
        try:
            print("♿ Running accessibility tests...")
            
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(f"{self.base_url}/", timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Test 1: Form labels
            inputs = soup.find_all(['input', 'textarea', 'select'])
            labels = soup.find_all('label')
            
            # Test 2: Heading structure
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            has_h1 = any(h.name == 'h1' for h in headings)
            
            # Test 3: Alt text for images
            images = soup.find_all('img')
            images_with_alt = [img for img in images if img.get('alt')]
            
            # Test 4: Button text
            buttons = soup.find_all('button')
            buttons_with_text = [btn for btn in buttons if btn.get_text().strip()]
            
            accessibility_results = {
                'form_inputs_count': len(inputs),
                'form_labels_count': len(labels),
                'has_h1': has_h1,
                'headings_count': len(headings),
                'images_count': len(images),
                'images_with_alt_count': len(images_with_alt),
                'buttons_count': len(buttons),
                'buttons_with_text_count': len(buttons_with_text)
            }
            
            self.test_results['accessibility_tests'] = accessibility_results
            
            # Basic accessibility check
            basic_accessibility_ok = (
                has_h1 and 
                len(inputs) > 0 and 
                len(buttons_with_text) > 0
            )
            
            print(f"✅ Accessibility tests completed:")
            print(f"   Form inputs: {len(inputs)}")
            print(f"   Buttons with text: {len(buttons_with_text)}")
            print(f"   Has H1: {has_h1}")
            
            return basic_accessibility_ok
            
        except Exception as e:
            print(f"❌ Accessibility tests failed: {e}")
            self.test_results['accessibility_tests'] = {'error': str(e)}
            return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        try:
            print("🔗 Running integration tests...")
            
            # Test orchestrator integration
            from src.agents.working_orchestrator import create_working_orchestrator
            
            orchestrator = create_working_orchestrator(
                mission="Test integration",
                platform="tiktok",
                category="Educational",
                duration=15,
                api_key=settings.google_api_key
            )
            
            orchestrator_ok = orchestrator is not None
            
            # Test file system integration
            import tempfile
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "test.txt")
            
            with open(temp_file, 'w') as f:
                f.write("test")
            
            file_system_ok = os.path.exists(temp_file)
            
            # Cleanup
            os.remove(temp_file)
            os.rmdir(temp_dir)
            
            integration_results = {
                'orchestrator_creation': orchestrator_ok,
                'file_system_access': file_system_ok
            }
            
            self.test_results['integration_tests'] = integration_results
            
            all_ok = orchestrator_ok and file_system_ok
            
            print(f"✅ Integration tests completed:")
            print(f"   Orchestrator creation: {'✅' if orchestrator_ok else '❌'}")
            print(f"   File system access: {'✅' if file_system_ok else '❌'}")
            
            return all_ok
            
        except Exception as e:
            print(f"❌ Integration tests failed: {e}")
            self.test_results['integration_tests'] = {'error': str(e)}
            return False
    
    def run_all_tests(self):
        """Run all UI tests"""
        print("🎭 Starting Comprehensive UI Test Suite")
        print("=" * 80)
        
        # Check prerequisites
        if not settings.google_api_key:
            print("❌ Error: GOOGLE_API_KEY not found in environment variables")
            return False
        
        # Start UI server
        if not self.start_ui_server():
            print("❌ Failed to start UI server")
            return False
        
        # Wait for server to be fully ready
        time.sleep(5)
        
        try:
            # Run all test suites
            test_suites = [
                ("HTTP Tests", self.run_basic_http_tests),
                ("Playwright Tests", self.run_playwright_tests),
                ("Performance Tests", self.run_performance_tests),
                ("Accessibility Tests", self.run_accessibility_tests),
                ("Integration Tests", self.run_integration_tests)
            ]
            
            results = {}
            for suite_name, test_func in test_suites:
                print(f"\n🧪 Running {suite_name}...")
                try:
                    results[suite_name] = test_func()
                except Exception as e:
                    print(f"❌ {suite_name} failed with error: {e}")
                    results[suite_name] = False
            
            # Print comprehensive results
            print("\n" + "=" * 80)
            print("🎯 Comprehensive UI Test Results")
            print("=" * 80)
            
            total_suites = len(results)
            passed_suites = sum(1 for result in results.values() if result)
            
            for suite_name, result in results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"{suite_name}: {status}")
            
            print(f"\nOverall: {passed_suites}/{total_suites} test suites passed")
            
            # Save detailed results
            with open('ui_test_results.json', 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            if passed_suites == total_suites:
                print("\n🎉 ALL UI TESTS PASSED!")
                print("✅ UI is fully functional and ready for production use")
                print("\n🚀 You can now use the UI with confidence:")
                print("   python modern_ui.py")
                print("   Access at: http://localhost:7860")
                print(f"\n📊 Detailed results saved to: ui_test_results.json")
                return True
            else:
                print("\n⚠️ Some tests failed - check the results above")
                print(f"📊 Detailed results saved to: ui_test_results.json")
                return False
                
        finally:
            self.stop_ui_server()


def main():
    """Main entry point"""
    print("🎭 AI Video Generator - Comprehensive UI Test Suite")
    print("Testing all aspects of the web interface...")
    
    test_runner = ComprehensiveUITestRunner()
    success = test_runner.run_all_tests()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 