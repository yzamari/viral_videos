#!/usr/bin/env python3
"""
Rotter Dark Humor News - 30 Seconds
Satirical take on Israeli news with dark humor
"""

import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import asyncio
import random


class DarkHumorNewsGenerator:
    """Creates satirical news with dark humor twist"""
    
    def __init__(self):
        self.font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial Hebrew.ttc",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        self.best_font = self._find_font()
        os.makedirs("dark_humor_output", exist_ok=True)
    
    def _find_font(self):
        """Find best font for Hebrew/English"""
        for path in self.font_paths:
            if os.path.exists(path):
                return path
        return None
    
    def get_font(self, size):
        """Get font with fallback"""
        if self.best_font:
            try:
                return ImageFont.truetype(self.best_font, size)
            except:
                pass
        return ImageFont.load_default()
    
    def create_dark_frame(self, story, position, total):
        """Create a frame with dark humor styling"""
        
        # Dark background with noise
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        # Add some visual noise for gritty effect
        for _ in range(500):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            gray = random.randint(20, 40)
            draw.point((x, y), fill=(gray, gray, gray))
        
        # Fonts
        font_huge = self.get_font(100)
        font_large = self.get_font(60)
        font_medium = self.get_font(45)
        font_small = self.get_font(35)
        
        # Top banner - distressed red
        for i in range(120):
            r = 150 + random.randint(-20, 20)
            draw.rectangle([(0, i), (1920, i+1)], fill=(r, 0, 0))
        
        # Logo with sarcastic tagline
        draw.text((50, 30), "ROTTER.NET", fill=(255, 255, 255), font=font_large)
        draw.text((350, 45), "Your Daily Dose of Despair™", fill=(200, 200, 200), font=font_small)
        
        # Story number with dramatic effect
        draw.text((100, 200), str(position), fill=(200, 0, 0), font=font_huge)
        
        # Sarcastic category badges
        if story.get('sarcastic_badge'):
            badge_width = 300
            draw.rectangle([(300, 200), (300 + badge_width, 280)], fill=(100, 0, 0))
            draw.text((320, 220), story['sarcastic_badge'], fill=(255, 255, 255), font=font_medium)
        
        # Main headline with shadow
        headline_box_y = 350
        draw.rectangle([(50, headline_box_y), (1870, headline_box_y + 200)], fill=(0, 0, 0, 180))
        
        # Headline
        draw.text((960, headline_box_y + 50), story['headline'], 
                 fill=(255, 255, 255), font=font_large, anchor="ma")
        
        # Sarcastic subtitle
        draw.text((960, headline_box_y + 120), story['subtitle'], 
                 fill=(200, 200, 200), font=font_medium, anchor="ma")
        
        # Dark humor commentary
        if story.get('commentary'):
            comment_y = 650
            draw.rectangle([(100, comment_y), (1820, comment_y + 100)], fill=(20, 20, 20))
            draw.text((960, comment_y + 50), f'"{story["commentary"]}"', 
                     fill=(255, 200, 0), font=font_medium, anchor="ma")
        
        # Fake statistics for comedic effect
        if story.get('fake_stat'):
            stat_y = 800
            draw.text((100, stat_y), "📊 Totally Real Statistic:", fill=(150, 150, 150), font=font_small)
            draw.text((100, stat_y + 40), story['fake_stat'], fill=(255, 100, 100), font=font_medium)
        
        # Bottom ticker with sarcastic messages
        draw.rectangle([(0, 980), (1920, 1080)], fill=(20, 20, 20))
        draw.rectangle([(0, 980), (1920, 985)], fill=(100, 0, 0))
        
        # Scrolling text effect
        ticker_messages = [
            "BREAKING: Everything is fine, nothing to see here",
            "EXCLUSIVE: Politicians discovered telling truth (April Fools)",
            "URGENT: Coffee prices rise, productivity plummets nationwide"
        ]
        ticker_text = ticker_messages[position % len(ticker_messages)]
        draw.text((50, 1020), ticker_text, fill=(200, 200, 200), font=font_small)
        
        # Progress bar with "doom meter"
        progress = (position / total) * 1920
        draw.rectangle([(0, 1070), (progress, 1080)], fill=(200, 0, 0))
        draw.text((progress - 100, 1050), "DOOM LEVEL", fill=(255, 100, 100), font=font_small)
        
        return img
    
    async def create_dark_humor_news(self):
        """Create 30-second dark humor news video"""
        
        print("""
😈 CREATING DARK HUMOR NEWS
==========================
⏱️  30 seconds of satire
🎭 Dark comedy style
📰 Rotter scoops reimagined
""")
        
        # Dark humor news stories (30 seconds = 6 stories x 5 seconds each)
        stories = [
            {
                'headline': "Earthquake 4.2: Buildings Shake, Politicians Remain Unmoved",
                'subtitle': "Geological disaster still less destructive than Knesset session",
                'sarcastic_badge': "SHOCKING",
                'commentary': "Nature trying to compete with government for most damage",
                'fake_stat': "87% of citizens preferred the earthquake"
            },
            {
                'headline': "PM Announces Economic Package: Your Wallet Gets Lighter",
                'subtitle': "Revolutionary new diet plan for bank accounts",
                'sarcastic_badge': "WALLET WARNING",
                'commentary': "Side effects include crying and ramen noodles",
                'fake_stat': "Package weight: 10kg paper, 0g substance"
            },
            {
                'headline': "IDF Drone Crashes: Even Our Technology Wants Out",
                'subtitle': "Drone allegedly seeking asylum in Lebanon",
                'sarcastic_badge': "FLYING FAIL",
                'commentary': "Drone had better exit strategy than most startups",
                'fake_stat': "3rd device this week to attempt escape"
            },
            {
                'headline': "Mayor Arrested for Corruption: Water Still Wet",
                'subtitle': "Citizens shocked to find gambling in casino",
                'sarcastic_badge': "SURPRISE LEVEL: 0",
                'commentary': "In related news: sun rises in east",
                'fake_stat': "Corruption index: Yes"
            },
            {
                'headline': "Hospital Director Quits: Cites 'Sudden Sanity Attack'",
                'subtitle': "Mental health crisis as official develops conscience",
                'sarcastic_badge': "MEDICAL MIRACLE",
                'commentary': "Doctors baffled by rare honesty outbreak",
                'fake_stat': "1 in 1,000,000 officials affected"
            },
            {
                'headline': "Tech Exit $2B: Founders Can Now Afford Tel Aviv Parking",
                'subtitle': "Almost enough for 3-bedroom apartment (shared)",
                'sarcastic_badge': "STILL BROKE",
                'commentary': "Celebration dampened by capital gains reality",
                'fake_stat': "Parking spot value: $1.9B"
            }
        ]
        
        segments = []
        
        # Create intro with dark humor
        print("\n🎬 Creating sarcastic intro...")
        intro_img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))
        draw = ImageDraw.Draw(intro_img)
        
        # Glitch effect background
        for i in range(100):
            y = random.randint(0, 1080)
            draw.rectangle([(0, y), (1920, y+2)], fill=(random.randint(50, 100), 0, 0))
        
        font_title = self.get_font(100)
        font_sub = self.get_font(60)
        
        # Main title
        draw.text((960, 350), "ROTTER: DARK EDITION", fill=(255, 0, 0), 
                 font=font_title, anchor="ma")
        draw.text((960, 500), "News That Hurts to Laugh At", fill=(200, 200, 200), 
                 font=font_sub, anchor="ma")
        draw.text((960, 650), "Viewer Discretion: Probably Wise", fill=(150, 150, 150), 
                 font=self.get_font(40), anchor="ma")
        
        # Warning symbols
        draw.text((300, 800), "⚠️", fill=(255, 200, 0), font=font_title)
        draw.text((1620, 800), "⚠️", fill=(255, 200, 0), font=font_title)
        
        intro_path = "dark_humor_output/intro.jpg"
        intro_img.save(intro_path)
        
        # Convert to video with glitch effect
        intro_video = "dark_humor_output/intro.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', intro_path,
            '-t', '2',
            '-vf', 'scale=1920:1080,chromashift=rx=5:ry=-5:bx=-5:by=5',
            '-c:v', 'libx264',
            '-preset', 'fast',
            intro_video
        ]
        subprocess.run(cmd, capture_output=True)
        
        # If chromashift fails, fallback
        if not os.path.exists(intro_video):
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', intro_path,
                '-t', '2',
                '-vf', 'scale=1920:1080',
                '-c:v', 'libx264',
                '-preset', 'fast',
                intro_video
            ]
            subprocess.run(cmd, capture_output=True)
        
        segments.append(intro_video)
        os.remove(intro_path)
        
        # Create story segments
        print("\n😈 Creating dark humor stories...")
        story_duration = 4.5  # 6 stories × 4.5s = 27s + 2s intro + 1s outro = 30s
        
        for i, story in enumerate(stories):
            print(f"  {i+1}. {story['headline'][:40]}...")
            
            frame = self.create_dark_frame(story, i+1, len(stories))
            frame_path = f"dark_humor_output/story_{i}.jpg"
            frame.save(frame_path)
            
            # Video with shaky/glitchy effect for dark mood
            video_path = f"dark_humor_output/story_{i}.mp4"
            
            # Random subtle effects
            effects = [
                'crop=in_w-20:in_h-20,scale=1920:1080',  # Slight crop
                'scale=1920:1080,eq=brightness=-0.1:saturation=0.8',  # Darker
                'scale=1920:1080,noise=alls=20:allf=t',  # Film grain
                'scale=1920:1080,vignette=PI/4'  # Vignette
            ]
            
            effect = random.choice(effects)
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', frame_path,
                '-t', str(story_duration),
                '-vf', effect,
                '-c:v', 'libx264',
                '-preset', 'fast',
                video_path
            ]
            subprocess.run(cmd, capture_output=True)
            
            # Fallback if effect fails
            if not os.path.exists(video_path):
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', frame_path,
                    '-t', str(story_duration),
                    '-vf', 'scale=1920:1080',
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    video_path
                ]
                subprocess.run(cmd, capture_output=True)
            
            segments.append(video_path)
            os.remove(frame_path)
        
        # Create outro
        print("\n🎬 Creating cynical outro...")
        outro_img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))
        draw = ImageDraw.Draw(outro_img)
        
        # Static noise background
        for _ in range(2000):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            gray = random.randint(0, 50)
            draw.point((x, y), fill=(gray, gray, gray))
        
        draw.text((960, 400), "That's All, Folks!", fill=(255, 255, 255), 
                 font=font_title, anchor="ma")
        draw.text((960, 550), "Remember: It's Funny Because It's True", fill=(200, 0, 0), 
                 font=self.get_font(50), anchor="ma")
        draw.text((960, 700), "© Reality 2025", fill=(150, 150, 150), 
                 font=self.get_font(40), anchor="ma")
        
        outro_path = "dark_humor_output/outro.jpg"
        outro_img.save(outro_path)
        
        outro_video = "dark_humor_output/outro.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', outro_path,
            '-t', '1',
            '-vf', 'fade=t=out:st=0.5:d=0.5',
            '-c:v', 'libx264',
            '-preset', 'fast',
            outro_video
        ]
        subprocess.run(cmd, capture_output=True)
        segments.append(outro_video)
        os.remove(outro_path)
        
        # Compile with quick cuts
        print("\n🎬 Compiling dark humor edition...")
        concat_file = "dark_humor_output/concat.txt"
        with open(concat_file, 'w') as f:
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"dark_humor_output/rotter_dark_humor_{timestamp}.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            output_path
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Extract test frame
        test_frame = "dark_humor_output/preview.jpg"
        cmd = [
            'ffmpeg', '-y',
            '-i', output_path,
            '-ss', '10',
            '-frames:v', '1',
            test_frame
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Cleanup
        os.remove(concat_file)
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        print(f"""
😈 DARK HUMOR NEWS COMPLETE!
===========================
📹 Video: {output_path}
⏱️  Duration: 30 seconds
🎭 Stories: 6 satirical takes

📰 STORIES INCLUDED:
1. Earthquake vs Politicians (4.5s)
2. Economic Package Diet Plan (4.5s)
3. Escaping Drone (4.5s)
4. Corruption Surprise Level: 0 (4.5s)
5. Sanity Attack Epidemic (4.5s)
6. Parking More Than Tech Exit (4.5s)

🎨 DARK FEATURES:
- Sarcastic headlines
- Fake statistics
- Dark visual style
- Cynical commentary
- Doom meter
- Glitch effects

📸 Preview: {test_frame}

⚠️  Side effects may include:
- Uncomfortable laughter
- Existential crisis
- Sudden urge to emigrate
- Uncontrollable eye rolling

✅ Ready to spread the darkness!
""")
        
        return output_path


if __name__ == "__main__":
    generator = DarkHumorNewsGenerator()
    asyncio.run(generator.create_dark_humor_news())