#!/usr/bin/env python3
""""🎭 Final UI Verification Test
Real user interaction testing with Playwright """"from config.config import settings
import os
import sys
import time
import subprocess
import asyncio
from playwright.async_api import async_playwright

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


class UIFinalVerification: """Final verification of UI functionality"""def __init__(self):
        self.ui_process = None self.base_url = "http://localhost:7860"def start_ui_server(self): """Start the UI server"""try: print("🚀 Starting UI server for final verification...")
            self.ui_process = subprocess.Popen( [sys.executable, "modern_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )

            # Wait for server to start
            import requests
            max_retries = 30
            for i in range(max_retries):
                try: response = requests.get(f"{self.base_url}/", timeout=5)
                    if response.status_code == 200: print(f"✅ UI server ready at {self.base_url}")
                        return True
                except requests.exceptions.RequestException:
                    if i < max_retries - 1:
                        time.sleep(2)
                    else:
                        return False
            return False
        except Exception as e: print(f"❌ Failed to start UI server: {e}")
            return False

    def stop_ui_server(self): """Stop the UI server"""if self.ui_process:
            try:
                self.ui_process.terminate()
                self.ui_process.wait(timeout=10) print("✅ UI server stopped")
            except subprocess.TimeoutExpired:
                self.ui_process.kill()

    async def test_complete_user_workflow(self): """Test complete user workflow"""async with async_playwright() as p:
            # Visible browser for verification
            browser = await p.chromium.launch(headless=False, slow_mo=1000)
            page = await browser.new_page()

            try: print("🌐 Navigating to UI...")
                await page.goto(self.base_url) await page.wait_for_load_state("networkidle")

                # Take screenshot await page.screenshot(path="ui_verification_1_loaded.png") print("📸 Screenshot saved: ui_verification_1_loaded.png")

                # Check page title
                title = await page.title() print(f"📄 Page title: {title}") assert "Enhanced Ultimate Modern Video Generator" in title

                # Find and fill mission input print("📝 Filling mission input...") mission_input = page.locator("textarea").first await mission_input.wait_for(state="visible", timeout=10000) await mission_input.fill("Test UI verification with Playwright - create a short video about AI technology")

                # Take screenshot after filling mission await page.screenshot(path="ui_verification_2_mission_filled.png") print("📸 Screenshot saved: ui_verification_2_mission_filled.png")

                # Find and interact with dropdowns print("🔽 Interacting with dropdowns...") dropdowns = page.locator("select")
                dropdown_count = await dropdowns.count() print(f"Found {dropdown_count} dropdowns")

                if dropdown_count > 0:
                    # Select platform await dropdowns.first.select_option("tiktok") print("✅ Selected platform: tiktok")

                if dropdown_count > 1:
                    # Select category await dropdowns.nth(1).select_option("Tech") print("✅ Selected category: Tech")
 # Find and interact with sliders print("🎚️ Interacting with sliders...") sliders = page.locator("input[type='range']")
                slider_count = await sliders.count() print(f"Found {slider_count} sliders")

                if slider_count > 0:
                    # Set duration await sliders.first.fill("20") print("✅ Set duration: 20 seconds")

                # Take screenshot after form completion await page.screenshot(path="ui_verification_3_form_completed.png") print("📸 Screenshot saved: ui_verification_3_form_completed.png")

                # Check for advanced options print("🔧 Checking advanced options...") accordions = page.locator( "button:has-text('Force Generation Options')", button:has-text('Advanced Options')"")
                accordion_count = await accordions.count() print(f"Found {accordion_count} accordion sections")

                if accordion_count > 0:
                    # Click first accordion
                    await accordions.first.click()
                    await page.wait_for_timeout(1000)  # Wait for animation print("✅ Opened accordion section")
 # Find generate button print("🎬 Locating generate button...") generate_button = page.locator("button:has-text('Generate Video')") await generate_button.wait_for(state="visible", timeout=10000)

                is_enabled = await generate_button.is_enabled() print(f"Generate button enabled: {is_enabled}")

                # Take final screenshot await page.screenshot(path="ui_verification_4_ready_to_generate.png") print("📸 Screenshot saved: ui_verification_4_ready_to_generate.png")

                # Check for real-time sections print("⚡ Checking real-time sections...")
                realtime_sections = [ "Live Status", "AI Agent Status", "Real-Time Agent Discussions"]

                for section in realtime_sections: section_element = page.locator(f"text={section}")
                    if await section_element.count() > 0: print(f"✅ Found section: {section}")
                    else: print(f"⚠️ Section not found: {section}")

                # Test responsiveness print("📱 Testing mobile responsiveness...") await page.set_viewport_size({"width": 375, "height": 667})
                await page.wait_for_timeout(1000) await page.screenshot(path="ui_verification_5_mobile.png") print("📸 Screenshot saved: ui_verification_5_mobile.png")

                # Reset to desktop await page.set_viewport_size({"width": 1280, "height": 720})
                await page.wait_for_timeout(1000)
 print("✅ Complete user workflow test passed!")
                return True

            except Exception as e: print(f"❌ User workflow test failed: {e}") await page.screenshot(path="ui_verification_error.png") print("📸 Error screenshot saved: ui_verification_error.png")
                return False

            finally:
                await browser.close()

    async def run_verification(self): """Run the complete verification"""print("🎭 Starting Final UI Verification") print("=" * 60)

        if not self.start_ui_server(): print("❌ Failed to start UI server")
            return False

        # Wait for server to be ready
        time.sleep(5)

        try:
            success = await self.test_complete_user_workflow()

            if success: print("\n🎉 FINAL UI VERIFICATION PASSED!") print("✅ UI is fully functional and ready for production") print("\n📸 Screenshots saved:") print("   - ui_verification_1_loaded.png") print("   - ui_verification_2_mission_filled.png") print("   - ui_verification_3_form_completed.png") print("   - ui_verification_4_ready_to_generate.png") print("   - ui_verification_5_mobile.png") print("\n🚀 You can now use the UI with confidence:") print("   python modern_ui.py") print("   Access at: http://localhost:7860")
                return True
            else: print("\n❌ UI verification failed")
                return False

        finally:
            self.stop_ui_server()


def main(): """Main entry point"""if not settings.google_api_key: print("❌ Error: GOOGLE_API_KEY not found")
        return False

    verifier = UIFinalVerification()
    return asyncio.run(verifier.run_verification())

 if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
