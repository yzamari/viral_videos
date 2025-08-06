#!/usr/bin/env python3
"""
Test Hebrew News with Static Data
Uses predefined articles instead of scraping
"""

import asyncio
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import subprocess
import aiohttp
import ssl
import certifi


class StaticHebrewNews:
    """Create Hebrew news video with static content"""
    
    def __init__(self):
        self.font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        os.makedirs("static_hebrew_news", exist_ok=True)
        
        # Static articles for testing
        self.articles = [
            {
                'title': 'רעידת אדמה בעוצמה 4.5 הורגשה בצפון הארץ',
                'source': 'Ynet',
                'description': 'רעידת אדמה הורגשה בצפון הארץ. אין דיווחים על נפגעים',
                'media_url': 'https://picsum.photos/1920/1080?random=1'
            },
            {
                'title': 'סקופ: שר בכיר שוקל להתפטר מהממשלה',
                'source': 'Rotter',
                'description': 'מקורות פוליטיים מדווחים על משבר בקואליציה',
                'media_url': 'https://picsum.photos/1920/1080?random=2'
            },
            {
                'title': 'מכבי תל אביב ניצחה 3-1 את הפועל בדרבי',
                'source': 'Ynet',
                'description': 'אייל גולסה כבש צמד שערים בניצחון הצהובים',
                'media_url': 'https://picsum.photos/1920/1080?random=3'
            },
            {
                'title': 'התרעה: גשם כבד צפוי בסוף השבוע',
                'source': 'Ynet',
                'description': 'השירות המטאורולוגי מזהיר מפני שיטפונות',
                'media_url': 'https://picsum.photos/1920/1080?random=4'
            },
            {
                'title': 'חשיפה: תוכנית כלכלית חדשה בהיקף 50 מיליארד',
                'source': 'Rotter',
                'description': 'הממשלה תאשר מחר תוכנית חירום כלכלית',
                'media_url': 'https://picsum.photos/1920/1080?random=5'
            }
        ]
    
    async def create_hebrew_news(self, duration_seconds=30):
        """Create Hebrew news video with static content"""
        
        print(f"""
🇮🇱 יוצר מהדורת חדשות בעברית
========================
📰 מקורות: Ynet, Rotter
⏱️  משך: {duration_seconds} שניות
📊 כתבות: {len(self.articles)}
""")
        
        # Download media
        print("\n📸 מוריד תמונות...")
        await self._download_media()
        
        # Allocate time per story
        time_per_story = (duration_seconds - 3) / len(self.articles)  # Reserve 3 sec for intro/outro
        
        # Create video segments
        segments = []
        
        # Intro
        intro_path = self._create_intro()
        segments.append(intro_path)
        
        # Story segments
        for i, article in enumerate(self.articles):
            segment_path = self._create_story_segment(article, i+1, len(self.articles), time_per_story)
            segments.append(segment_path)
        
        # Outro
        outro_path = self._create_outro(len(self.articles))
        segments.append(outro_path)
        
        # Compile final video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"static_hebrew_news/hebrew_news_{timestamp}.mp4"
        self._compile_video(segments, output_path)
        
        # Cleanup
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        print(f"""
✅ הושלם!
========
📹 קובץ: {output_path}
⏱️  משך: {duration_seconds} שניות
📰 כתבות: {len(self.articles)}
""")
        
        return output_path
    
    async def _download_media(self):
        """Download media for articles"""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            for i, article in enumerate(self.articles):
                if article.get('media_url'):
                    try:
                        async with session.get(article['media_url']) as resp:
                            if resp.status == 200:
                                filename = f"static_hebrew_news/media_{i}.jpg"
                                with open(filename, 'wb') as f:
                                    f.write(await resp.read())
                                article['local_media'] = filename
                                print(f"   ✅ {article['source']} - {i+1}")
                    except:
                        pass
    
    def _create_intro(self):
        """Create intro segment"""
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype(self.font_path, 80)
            font_medium = ImageFont.truetype(self.font_path, 50)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Title
        draw.text((960, 400), "מהדורת חדשות", fill=(255, 255, 255), 
                 font=font_large, anchor="ma")
        draw.text((960, 550), "Ynet • Rotter", fill=(200, 200, 200), 
                 font=font_medium, anchor="ma")
        
        intro_path = "static_hebrew_news/intro.jpg"
        img.save(intro_path)
        
        # Convert to video
        intro_video = "static_hebrew_news/intro.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', intro_path,
            '-t', '2', '-vf', 'fade=t=in:d=0.5',
            '-c:v', 'libx264', '-preset', 'fast', intro_video
        ], capture_output=True)
        
        os.remove(intro_path)
        return intro_video
    
    def _create_story_segment(self, article, position, total, duration):
        """Create a story segment"""
        img = Image.new('RGB', (1920, 1080), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype(self.font_path, 60)
            font_medium = ImageFont.truetype(self.font_path, 45)
            font_small = ImageFont.truetype(self.font_path, 35)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Load background image if available
        if article.get('local_media') and os.path.exists(article['local_media']):
            bg_img = Image.open(article['local_media'])
            bg_img = bg_img.resize((1920, 1080), Image.Resampling.LANCZOS)
            # Darken the image
            bg_img = bg_img.convert('RGBA')
            overlay = Image.new('RGBA', bg_img.size, (0, 0, 0, 180))
            bg_img = Image.alpha_composite(bg_img, overlay).convert('RGB')
            img = bg_img
            draw = ImageDraw.Draw(img)
        
        # Source badge
        source_colors = {'Ynet': (0, 150, 255), 'Rotter': (255, 0, 0)}
        color = source_colors.get(article['source'], (150, 150, 150))
        draw.rectangle([(50, 50), (250, 120)], fill=color)
        draw.text((150, 85), article['source'], fill=(255, 255, 255), 
                 font=font_medium, anchor="ma")
        
        # Position indicator
        draw.text((1870, 85), f"{position}/{total}", fill=(255, 255, 255), 
                 font=font_medium, anchor="ra")
        
        # Title - RTL aligned
        draw.text((960, 400), article['title'], fill=(255, 255, 255), 
                 font=font_large, anchor="ma")
        
        # Description if available
        if article.get('description'):
            draw.text((960, 600), article['description'], 
                     fill=(200, 200, 200), font=font_medium, anchor="ma")
        
        img_path = f"static_hebrew_news/story_{position}.jpg"
        img.save(img_path)
        
        segment_path = f"static_hebrew_news/segment_{position}.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', img_path,
            '-t', str(duration), '-vf', 'scale=1920:1080',
            '-c:v', 'libx264', '-preset', 'fast', segment_path
        ], capture_output=True)
        
        os.remove(img_path)
        return segment_path
    
    def _create_outro(self, story_count):
        """Create outro segment"""
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype(self.font_path, 70)
            font_medium = ImageFont.truetype(self.font_path, 50)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        draw.text((960, 400), "סוף המהדורה", fill=(255, 255, 255), 
                 font=font_large, anchor="ma")
        draw.text((960, 550), f"סוכמו {story_count} כתבות", 
                 fill=(200, 200, 200), font=font_medium, anchor="ma")
        
        outro_path = "static_hebrew_news/outro.jpg"
        img.save(outro_path)
        
        outro_video = "static_hebrew_news/outro.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', outro_path,
            '-t', '1', '-vf', 'fade=t=out:st=0.5:d=0.5',
            '-c:v', 'libx264', '-preset', 'fast', outro_video
        ], capture_output=True)
        
        os.remove(outro_path)
        return outro_video
    
    def _compile_video(self, segments, output_path):
        """Compile all segments into final video"""
        concat_file = "static_hebrew_news/concat.txt"
        with open(concat_file, 'w') as f:
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file, '-c:v', 'libx264',
            '-preset', 'fast', output_path
        ], capture_output=True)
        
        os.remove(concat_file)


async def main():
    """Test with static content"""
    generator = StaticHebrewNews()
    video_path = await generator.create_hebrew_news(duration_seconds=30)
    return video_path


if __name__ == "__main__":
    asyncio.run(main())