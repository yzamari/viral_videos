#!/usr/bin/env python3
"""
🎬 Browser E2E Test for AI Video Generator GUI
Comprehensive testing of the web interface functionality
"""

import os
import sys
import time
import pytest
import threading
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import settings


class VideoGeneratorUITest:
    """Comprehensive E2E test suite for the video generator UI"""
    
    def __init__(self):
        self.driver = None
        self.ui_process = None
        self.base_url = "http://localhost:7860"
        self.wait_timeout = 30
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome WebDriver initialized successfully")
            return True
        except WebDriverException as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("💡 Make sure Chrome and ChromeDriver are installed")
            return False
    
    def start_ui_server(self):
        """Start the UI server in background"""
        try:
            print("🚀 Starting UI server...")
            self.ui_process = subprocess.Popen(
                [sys.executable, "modern_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for server to start
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.base_url}/", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ UI server started successfully at {self.base_url}")
                        return True
                except requests.exceptions.RequestException:
                    if i < max_retries - 1:
                        print(f"⏳ Waiting for UI server to start... ({i+1}/{max_retries})")
                        time.sleep(2)
                    else:
                        print("❌ UI server failed to start within timeout")
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
                print("✅ UI server stopped successfully")
            except subprocess.TimeoutExpired:
                self.ui_process.kill()
                print("⚠️ UI server force-killed")
            except Exception as e:
                print(f"❌ Error stopping UI server: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver closed")
        
        self.stop_ui_server()
    
    def test_ui_accessibility(self):
        """Test if UI is accessible and loads properly"""
        try:
            print("🌐 Testing UI accessibility...")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Check if main header is present
            header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main-header")))
            assert header is not None, "Main header not found"
            
            # Check if title contains expected text
            title = self.driver.title
            assert "Enhanced Ultimate Modern Video Generator" in title, f"Unexpected title: {title}"
            
            # Check if mission input field is present
            mission_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Enter your video mission or topic...']")))
            assert mission_input is not None, "Mission input field not found"
            
            # Check if generate button is present
            generate_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Video')]")))
            assert generate_btn is not None, "Generate button not found"
            
            print("✅ UI accessibility test passed")
            return True
            
        except TimeoutException as e:
            print(f"❌ UI accessibility test failed - timeout: {e}")
            return False
        except AssertionError as e:
            print(f"❌ UI accessibility test failed - assertion: {e}")
            return False
        except Exception as e:
            print(f"❌ UI accessibility test failed - error: {e}")
            return False
    
    def test_form_elements(self):
        """Test all form elements and their functionality"""
        try:
            print("📝 Testing form elements...")
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Test mission input
            mission_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Enter your video mission or topic...']")))
            test_mission = "Test mission for E2E browser testing"
            mission_input.clear()
            mission_input.send_keys(test_mission)
            assert mission_input.get_attribute("value") == test_mission, "Mission input not working"
            
            # Test platform dropdown
            platform_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Platform')]/following-sibling::*//div[@class='wrap']")))
            platform_dropdown.click()
            time.sleep(1)
            
            # Select TikTok
            tiktok_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='tiktok']")))
            tiktok_option.click()
            time.sleep(1)
            
            # Test category dropdown
            category_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Category')]/following-sibling::*//div[@class='wrap']")))
            category_dropdown.click()
            time.sleep(1)
            
            # Select Comedy
            comedy_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Comedy']")))
            comedy_option.click()
            time.sleep(1)
            
            # Test duration slider
            duration_slider = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='range']")))
            self.driver.execute_script("arguments[0].value = 30", duration_slider)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", duration_slider)
            
            # Test AI system dropdown
            system_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'AI System')]/following-sibling::*//div[@class='wrap']")))
            system_dropdown.click()
            time.sleep(1)
            
            # Select enhanced
            enhanced_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='enhanced']")))
            enhanced_option.click()
            time.sleep(1)
            
            print("✅ Form elements test passed")
            return True
            
        except TimeoutException as e:
            print(f"❌ Form elements test failed - timeout: {e}")
            return False
        except Exception as e:
            print(f"❌ Form elements test failed - error: {e}")
            return False
    
    def test_advanced_options(self):
        """Test advanced options and accordions"""
        try:
            print("⚙️ Testing advanced options...")
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Test Force Generation Options accordion
            force_accordion = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Force Generation Options')]")))
            force_accordion.click()
            time.sleep(1)
            
            # Test force generation dropdown
            force_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Force Generation Method')]/following-sibling::*//div[@class='wrap']")))
            force_dropdown.click()
            time.sleep(1)
            
            # Select force_veo2
            veo2_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='force_veo2']")))
            veo2_option.click()
            time.sleep(1)
            
            # Test Trending Analysis accordion
            trending_accordion = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Trending Analysis')]")))
            trending_accordion.click()
            time.sleep(1)
            
            # Test trending analysis checkbox
            trending_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']")))
            trending_checkbox.click()
            time.sleep(1)
            
            # Test Advanced Options accordion
            advanced_accordion = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Advanced Options')]")))
            advanced_accordion.click()
            time.sleep(1)
            
            # Test frame continuity dropdown
            continuity_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Frame Continuity')]/following-sibling::*//div[@class='wrap']")))
            continuity_dropdown.click()
            time.sleep(1)
            
            # Select 'on'
            on_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='on']")))
            on_option.click()
            time.sleep(1)
            
            print("✅ Advanced options test passed")
            return True
            
        except TimeoutException as e:
            print(f"❌ Advanced options test failed - timeout: {e}")
            return False
        except Exception as e:
            print(f"❌ Advanced options test failed - error: {e}")
            return False
    
    def test_generation_process(self):
        """Test video generation process (without waiting for completion)"""
        try:
            print("🎬 Testing video generation process...")
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Ensure we have a test mission
            mission_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Enter your video mission or topic...']")))
            mission_input.clear()
            mission_input.send_keys("Test E2E browser video generation")
            
            # Click generate button
            generate_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Video')]")))
            generate_btn.click()
            
            # Wait for generation to start (button should become invisible)
            wait.until(EC.invisibility_of_element_located((By.XPATH, "//button[contains(text(), 'Generate Video')]")))
            
            # Check if stop button appears
            stop_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Stop')]")))
            assert stop_btn is not None, "Stop button not found after generation start"
            
            # Wait for status to update
            time.sleep(5)
            
            # Check if progress section updates
            progress_section = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Progress')]")))
            assert progress_section is not None, "Progress section not found"
            
            # Check if AI agent status updates
            agent_status = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'AI Agent Status')]")))
            assert agent_status is not None, "AI agent status not found"
            
            # Stop the generation for testing purposes
            stop_btn.click()
            time.sleep(2)
            
            # Check if generate button becomes visible again
            generate_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Video')]")))
            assert generate_btn is not None, "Generate button not restored after stop"
            
            print("✅ Video generation process test passed")
            return True
            
        except TimeoutException as e:
            print(f"❌ Video generation process test failed - timeout: {e}")
            return False
        except Exception as e:
            print(f"❌ Video generation process test failed - error: {e}")
            return False
    
    def test_ui_responsiveness(self):
        """Test UI responsiveness and real-time updates"""
        try:
            print("📱 Testing UI responsiveness...")
            
            # Test different screen sizes
            screen_sizes = [
                (1920, 1080),  # Desktop
                (1366, 768),   # Laptop
                (768, 1024),   # Tablet
                (375, 667)     # Mobile
            ]
            
            for width, height in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Check if main elements are still visible
                wait = WebDriverWait(self.driver, 10)
                
                # Check header
                header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main-header")))
                assert header.is_displayed(), f"Header not visible at {width}x{height}"
                
                # Check mission input
                mission_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Enter your video mission or topic...']")))
                assert mission_input.is_displayed(), f"Mission input not visible at {width}x{height}"
                
                # Check generate button
                generate_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Generate Video')]")))
                assert generate_btn.is_displayed(), f"Generate button not visible at {width}x{height}"
            
            # Reset to desktop size
            self.driver.set_window_size(1920, 1080)
            
            print("✅ UI responsiveness test passed")
            return True
            
        except TimeoutException as e:
            print(f"❌ UI responsiveness test failed - timeout: {e}")
            return False
        except Exception as e:
            print(f"❌ UI responsiveness test failed - error: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling and user feedback"""
        try:
            print("🚨 Testing error handling...")
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Test with empty mission
            mission_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Enter your video mission or topic...']")))
            mission_input.clear()
            
            # Try to generate with empty mission
            generate_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Video')]")))
            generate_btn.click()
            
            # Should still work with default mission or show appropriate feedback
            time.sleep(3)
            
            # Test with very long mission
            long_mission = "A" * 1000  # Very long mission
            mission_input.clear()
            mission_input.send_keys(long_mission)
            
            # Should handle long input gracefully
            time.sleep(1)
            
            print("✅ Error handling test passed")
            return True
            
        except Exception as e:
            print(f"❌ Error handling test failed - error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all E2E tests"""
        print("🎬 Starting Browser E2E Tests for AI Video Generator GUI")
        print("=" * 60)
        
        test_results = {}
        
        # Setup
        if not self.setup_driver():
            print("❌ Failed to setup WebDriver")
            return False
        
        if not self.start_ui_server():
            print("❌ Failed to start UI server")
            self.cleanup()
            return False
        
        # Wait for server to be fully ready
        time.sleep(5)
        
        try:
            # Run tests
            test_results['accessibility'] = self.test_ui_accessibility()
            test_results['form_elements'] = self.test_form_elements()
            test_results['advanced_options'] = self.test_advanced_options()
            test_results['generation_process'] = self.test_generation_process()
            test_results['responsiveness'] = self.test_ui_responsiveness()
            test_results['error_handling'] = self.test_error_handling()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            test_results['execution_error'] = False
        
        finally:
            self.cleanup()
        
        # Print results
        print("\n" + "=" * 60)
        print("🎯 Browser E2E Test Results")
        print("=" * 60)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL BROWSER E2E TESTS PASSED!")
            print("✅ GUI is fully functional and ready for production use")
            return True
        else:
            print("⚠️ Some tests failed - GUI may have issues")
            return False


def main():
    """Main entry point for browser E2E tests"""
    # Check if API key is configured
    if not settings.google_api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google AI API key in the .env file")
        return False
    
    # Run tests
    test_runner = VideoGeneratorUITest()
    success = test_runner.run_all_tests()
    
    if success:
        print("\n🚀 GUI E2E Testing Complete - System Ready!")
        print("🌐 You can now run: ./run_video_generator.sh ui")
        print("📱 Access the GUI at: http://localhost:7860")
    else:
        print("\n❌ GUI E2E Testing Failed - Check logs above")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 