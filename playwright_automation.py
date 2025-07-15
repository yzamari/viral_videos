#!/usr/bin/env python3
""""
Playwright automation for video generator UI
Generates 5 videos about Israeli state heroes
""""

import asyncio
import time
import os
from playwright.async_api import async_playwright
import subprocess


class VideoGeneratorAutomation:
    def __init__(self):
        self.ui_process = None
        self.ui_url = "http://localhost:7860"

        # Israeli state heroes data
        self.heroes = [{"name": "David Ben-Gurion",
                        "mission": "David Ben-Gurion: The visionary founder of Israel who proclaimed independence in 1948. From a young Hebrew activist to Israel's first Prime Minister, he built a nation from scratch, led through war, and established democratic institutions. Known for his yoga practice, khaki outfits, and retirement to the Negev desert where he believed Israel's future lay.",
                        "platform": "instagram",
                        "category": "Educational",
                        "duration": 45},
                       {"name": "Golda Meir",
                        "mission": "Golda Meir: The Iron Lady of Israel who rose from Milwaukee schoolgirl to Prime Minister. She organized fundraisers as a teenager, became a teacher and kibbutznik, and led Israel through the Yom Kippur War. Known as the 'strong-willed, grey-bunned grandmother of the Jewish people' who David Ben-Gurion called 'the best man in the government'.",
                        "platform": "tiktok",
                        "category": "Educational",
                        "duration": 30},
                       {"name": "Ilan Ramon",
                        "mission": "Ilan Ramon: Israel's first astronaut and"
                            national hero who carried the nation's pride to space. A fighter pilot who destroyed Iraq's nuclear reactor in 1981, he brought kosher food and a Holocaust survivor's drawing to the Space Shuttle Columbia. His tragic death in 2003 united a nation in mourning for a true mensch among men."",
                        "platform": "youtube",
                        "category": "Educational",
                        "duration": 50},
                       {"name": "Hannah Senesh",
                        "mission": "Hannah Senesh: The poet-paratrooper who sacrificed everything for her people. At 23, she parachuted into Nazi-occupied Hungary to save Jews from Auschwitz. Captured, tortured, and executed by firing squad, she never revealed her mission. Her poetry lives on as a testament to courage, and streets across Israel bear her name.",
                        "platform": "instagram",
                        "category": "Educational",
                        "duration": 40},
                       {"name": "Theodor Herzl",
                        "mission": "Theodor Herzl: The father of modern Zionism who dreamed of a Jewish state when it seemed impossible. An Austrian journalist who faced opposition from his own community, he founded the Zionist Organization and promoted Jewish immigration to Palestine. His vision of 'If you will it, it is no dream' became reality 50 years later.",
                        "platform": "youtube",
                        "category": "Educational",
                        "duration": 55}]

    def start_ui_server(self):
        """Start the video generator UI server"""
        try:
            print("🚀 Starting video generator UI server...")
            self.ui_process = subprocess.Popen(
                ["python", "modern_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            time.sleep(10)
            print("✅ UI server started successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to start UI server: {e}")
            return False

    def stop_ui_server(self):
        """Stop the video generator UI server"""
        if self.ui_process:
            self.ui_process.terminate()
            self.ui_process.wait()
            print("🛑 UI server stopped")

    async def generate_hero_video(self, hero_data):
        """Generate a video for a specific hero"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                print(f"🎬 Generating video for {hero_data['name']}...")

                # Navigate to the UI
                await page.goto(self.ui_url)
                await page.wait_for_timeout(3000)

                # Fill in the form
                await page.fill('textarea[placeholder*="Enter your video mission"]', 
                    hero_data['mission'])
                await page.wait_for_timeout(1000)

                # Select platform
                await page.click('label:has-text("Platform")')
                await page.wait_for_timeout(500)
                await page.click(f'text="{hero_data["platform"]}"')
                await page.wait_for_timeout(500)

                # Select category
                await page.click('label:has-text("Category")')
                await page.wait_for_timeout(500)
                await page.click(f'text="{hero_data["category"]}"')
                await page.wait_for_timeout(500)

                # Set duration
                duration_slider = page.locator('input[type="range"]').first
                await duration_slider.fill(str(hero_data['duration']))
                await page.wait_for_timeout(500)

                # Set AI system to enhanced
                await page.click('label:has-text("AI System")')
                await page.wait_for_timeout(500)
                await page.click('text="enhanced"')
                await page.wait_for_timeout(500)

                # Click generate button
                await page.click('button:has-text("Generate Video")')
                print(f"✅ Started generation for {hero_data['name']}")

                # Wait for generation to complete (monitor progress)
                await self.wait_for_completion(page, hero_data['name'])

                # Download the video
                await self.download_video(page, hero_data['name'])

            except Exception as e:
                print(f"❌ Error generating video for {hero_data['name']}: {e}")

            finally:
                await browser.close()

    async def wait_for_completion(self, page, hero_name):
        """Wait for video generation to complete"""
        print(f"⏳ Waiting for {hero_name} video generation to complete...")

        # Wait for up to 10 minutes
        timeout = 600  # 10 minutes
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check if video element is visible
                video_element = page.locator('video')
                if await video_element.count() > 0 and await video_element.is_visible():
                    print(f"✅ {hero_name} video generation completed!")
                    return True

                # Check for download links
                download_links = page.locator('a:has-text("Download")')
                if await download_links.count() > 0:
                    print(f"✅ {hero_name} video generation completed!")
                    return True

                # Check progress
                progress_text = await page.locator('text*="Progress:"').text_content()
                if progress_text:
                    print(f"📊 {hero_name} progress: {progress_text}")

                await page.wait_for_timeout(5000)  # Wait 5 seconds

            except Exception as e:
                print(f"⏳ Still waiting for {hero_name}... ({e})")
                await page.wait_for_timeout(5000)

        print(f"⏰ Timeout waiting for {hero_name} video generation")
        return False

    async def download_video(self, page, hero_name):
        """Download the generated video"""
        try:
            # Look for download links
            download_links = page.locator('a:has-text("Download")')
            if await download_links.count() > 0:
                # Click the first download link
                async with page.expect_download() as download_info:
                    await download_links.first.click()

                download = await download_info.value
                # Save to a specific location
                download_path = f"hero_videos/{hero_name.replace(' ', '_')}_video.mp4"
                os.makedirs("hero_videos", exist_ok=True)
                await download.save_as(download_path)
                print(f"💾 Downloaded {hero_name} video to {download_path}")

        except Exception as e:
            print(f"❌ Error downloading {hero_name} video: {e}")

    async def generate_all_heroes(self):
        """Generate videos for all 5 heroes"""
        print("🎯 Starting generation of all 5 Israeli state hero videos...")

        for i, hero in enumerate(self.heroes, 1):
            print(f"\n🎬 Generating video {i}/5: {hero['name']}")
            await self.generate_hero_video(hero)

            # Wait between generations to avoid overloading
            if i < len(self.heroes):
                print("⏳ Waiting 30 seconds before next generation...")
                await asyncio.sleep(30)

        print("\n🎉 All 5 Israeli state hero videos generated!")

    async def run_automation(self):
        """Run the complete automation"""
        try:
            # Start UI server
            if not self.start_ui_server():
                return False

            # Wait for UI to be ready
            print("⏳ Waiting for UI to be ready...")
            await asyncio.sleep(15)

            # Generate all hero videos
            await self.generate_all_heroes()

            return True

        except Exception as e:
            print(f"❌ Automation error: {e}")
            return False

        finally:
            self.stop_ui_server()


async def main():
    """Main function to run the automation"""
    print("🎬 Israeli State Heroes Video Generator Automation")
    print("=" * 50)

    automation = VideoGeneratorAutomation()
    success = await automation.run_automation()

    if success:
        print("\n✅ Automation completed successfully!")
        print("📁 Check the 'hero_videos' directory for generated videos")
    else:
        print("\n❌ Automation failed!")

if __name__ == "__main__":
    asyncio.run(main())
