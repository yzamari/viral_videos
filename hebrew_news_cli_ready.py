#!/usr/bin/env python3
"""
Hebrew News CLI Ready Version
Creates Hebrew news without dependency issues
"""

import asyncio
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import ssl
import certifi


class HebrewNewsGenerator:
    """Generate Hebrew news videos"""
    
    def __init__(self):
        self.font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        self.output_dir = "hebrew_news_output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_from_sources(self, sources, duration=60, max_stories=8):
        """Generate news from specified sources"""
        
        print(f"""
🇮🇱 Creating Hebrew News Video
============================
📰 Sources: {', '.join(sources)}
⏱️  Duration: {duration} seconds
📊 Max stories: {max_stories}
""")
        
        # Simulate news articles based on sources
        articles = self._get_simulated_articles(sources, max_stories)
        
        # Download media
        print("\n📸 Downloading media...")
        await self._download_media(articles)
        
        # Create video
        print("\n🎬 Creating video...")
        output_path = self._create_video(articles, duration)
        
        return output_path
    
    def _get_simulated_articles(self, sources, max_stories):
        """Get simulated articles based on sources"""
        all_articles = []
        
        if 'ynet' in sources:
            all_articles.extend([
                {
                    'title': 'חדשות היום: התפתחות דרמטית בזירה הפוליטית',
                    'source': 'Ynet',
                    'description': 'פרטים חדשים נחשפים בפרשה',
                    'media_url': 'https://picsum.photos/1920/1080?random=100'
                },
                {
                    'title': 'מזג האוויר: סופת גשמים בדרך לישראל',
                    'source': 'Ynet',
                    'description': 'התרעות על שיטפונות באזורים נמוכים',
                    'media_url': 'https://picsum.photos/1920/1080?random=101'
                },
                {
                    'title': 'הישג ישראלי: חברת הייטק נמכרה ב-2 מיליארד דולר',
                    'source': 'Ynet',
                    'description': 'העסקה הגדולה ביותר השנה',
                    'media_url': 'https://picsum.photos/1920/1080?random=102'
                }
            ])
        
        if 'rotter' in sources:
            all_articles.extend([
                {
                    'title': 'סקופ בלעדי: שינויים צפויים בצמרת הביטחונית',
                    'source': 'Rotter',
                    'description': 'מקורות מדווחים על החלטה דרמטית',
                    'media_url': 'https://picsum.photos/1920/1080?random=103'
                },
                {
                    'title': 'דחוף: אירוע חריג בגבול הצפון',
                    'source': 'Rotter',
                    'description': 'כוחות גדולים במקום',
                    'media_url': 'https://picsum.photos/1920/1080?random=104'
                },
                {
                    'title': 'חשיפה: מסמך סודי דלף לתקשורת',
                    'source': 'Rotter',
                    'description': 'התוכן מעורר סערה ציבורית',
                    'media_url': 'https://picsum.photos/1920/1080?random=105'
                }
            ])
        
        if 'bbc' in sources:
            all_articles.extend([
                {
                    'title': 'ניתוח בינלאומי: השלכות המשבר על המזרח התיכון',
                    'source': 'BBC',
                    'description': 'מומחים מנתחים את המצב',
                    'media_url': 'https://picsum.photos/1920/1080?random=106'
                },
                {
                    'title': 'דיווח מיוחד: שינויי אקלים קיצוניים באזור',
                    'source': 'BBC',
                    'description': 'מחקר חדש מצביע על מגמות מדאיגות',
                    'media_url': 'https://picsum.photos/1920/1080?random=107'
                }
            ])
        
        # Return up to max_stories
        return all_articles[:max_stories]
    
    async def _download_media(self, articles):
        """Download media for articles"""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            for i, article in enumerate(articles):
                if article.get('media_url'):
                    try:
                        async with session.get(article['media_url']) as resp:
                            if resp.status == 200:
                                filename = f"{self.output_dir}/media_{i}.jpg"
                                with open(filename, 'wb') as f:
                                    f.write(await resp.read())
                                article['local_media'] = filename
                                print(f"   ✅ Downloaded: {article['source']} - Story {i+1}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to download media for story {i+1}: {e}")
    
    def _create_video(self, articles, duration):
        """Create the final video"""
        segments = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate time per segment
        intro_outro_time = 3
        content_time = duration - intro_outro_time
        time_per_story = content_time / len(articles) if articles else 0
        
        # Create intro
        intro_path = self._create_intro(articles)
        segments.append(intro_path)
        
        # Create story segments
        for i, article in enumerate(articles):
            segment_path = self._create_story_segment(article, i+1, len(articles), time_per_story)
            segments.append(segment_path)
        
        # Create outro
        outro_path = self._create_outro(len(articles))
        segments.append(outro_path)
        
        # Compile video
        output_path = f"{self.output_dir}/hebrew_news_{timestamp}.mp4"
        self._compile_video(segments, output_path)
        
        # Cleanup
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        # Create summary
        self._create_summary(articles, output_path, duration)
        
        return output_path
    
    def _create_intro(self, articles):
        """Create intro segment"""
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype(self.font_path, 80)
            font_medium = ImageFont.truetype(self.font_path, 50)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Get unique sources
        sources = list(set(article['source'] for article in articles))
        sources_text = ' • '.join(sources)
        
        draw.text((960, 400), "מהדורת חדשות", fill=(255, 255, 255), 
                 font=font_large, anchor="ma")
        draw.text((960, 550), sources_text, fill=(200, 200, 200), 
                 font=font_medium, anchor="ma")
        
        intro_path = f"{self.output_dir}/intro.jpg"
        img.save(intro_path)
        
        intro_video = f"{self.output_dir}/intro.mp4"
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
        
        # Load background if available
        if article.get('local_media') and os.path.exists(article['local_media']):
            try:
                bg_img = Image.open(article['local_media'])
                bg_img = bg_img.resize((1920, 1080), Image.Resampling.LANCZOS)
                # Add dark overlay
                bg_img = bg_img.convert('RGBA')
                overlay = Image.new('RGBA', bg_img.size, (0, 0, 0, 150))
                bg_img = Image.alpha_composite(bg_img, overlay).convert('RGB')
                img = bg_img
                draw = ImageDraw.Draw(img)
            except:
                pass
        
        # Source badge
        source_colors = {
            'Ynet': (0, 150, 255),
            'Rotter': (255, 0, 0),
            'BBC': (200, 0, 200)
        }
        color = source_colors.get(article['source'], (150, 150, 150))
        
        draw.rectangle([(50, 50), (250, 120)], fill=color)
        draw.text((150, 85), article['source'], fill=(255, 255, 255), 
                 font=font_medium, anchor="ma")
        
        # Story counter
        draw.text((1870, 85), f"{position}/{total}", fill=(255, 255, 255), 
                 font=font_medium, anchor="ra")
        
        # Title
        draw.text((960, 400), article['title'], fill=(255, 255, 255), 
                 font=font_large, anchor="ma")
        
        # Description
        if article.get('description'):
            draw.text((960, 600), article['description'], 
                     fill=(200, 200, 200), font=font_medium, anchor="ma")
        
        img_path = f"{self.output_dir}/story_{position}.jpg"
        img.save(img_path)
        
        segment_path = f"{self.output_dir}/segment_{position}.mp4"
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
        draw.text((960, 550), f"סוכמו {story_count} כתבות מובילות", 
                 fill=(200, 200, 200), font=font_medium, anchor="ma")
        
        outro_path = f"{self.output_dir}/outro.jpg"
        img.save(outro_path)
        
        outro_video = f"{self.output_dir}/outro.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', outro_path,
            '-t', '1', '-vf', 'fade=t=out:st=0.5:d=0.5',
            '-c:v', 'libx264', '-preset', 'fast', outro_video
        ], capture_output=True)
        
        os.remove(outro_path)
        return outro_video
    
    def _compile_video(self, segments, output_path):
        """Compile all segments into final video"""
        concat_file = f"{self.output_dir}/concat.txt"
        with open(concat_file, 'w') as f:
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file, '-c:v', 'libx264',
            '-preset', 'medium', '-crf', '23', output_path
        ], capture_output=True)
        
        os.remove(concat_file)
    
    def _create_summary(self, articles, video_path, duration):
        """Create summary report"""
        summary_path = video_path.replace('.mp4', '_summary.txt')
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"""מהדורת חדשות בעברית
===================
📹 קובץ: {os.path.basename(video_path)}
⏱️  משך: {duration} שניות
📰 כתבות: {len(articles)}
📅 תאריך: {datetime.now().strftime('%Y-%m-%d %H:%M')}

כתבות במהדורה:
""")
            
            for i, article in enumerate(articles, 1):
                f.write(f"\n{i}. {article['title']}")
                f.write(f"\n   מקור: {article['source']}")
                if article.get('description'):
                    f.write(f"\n   תיאור: {article['description']}")
                f.write("\n")
        
        print(f"\n📄 Summary saved: {summary_path}")


async def create_hebrew_news_from_sources(sources, duration=60):
    """Create Hebrew news from specified sources"""
    generator = HebrewNewsGenerator()
    return await generator.generate_from_sources(sources, duration)


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    sources = ['ynet', 'rotter']  # Default
    duration = 60  # Default
    
    if len(sys.argv) > 1:
        # Simple parsing for demo
        if '--sources' in sys.argv:
            sources = []
            i = sys.argv.index('--sources') + 1
            while i < len(sys.argv) and not sys.argv[i].startswith('--'):
                sources.append(sys.argv[i])
                i += 1
        
        if '--duration' in sys.argv:
            i = sys.argv.index('--duration') + 1
            if i < len(sys.argv):
                duration = int(sys.argv[i])
    
    # Run
    video_path = asyncio.run(create_hebrew_news_from_sources(sources, duration))
    print(f"\n✅ Video created: {video_path}")
    print(f"\nTo play: open {video_path}")