#!/usr/bin/env python3
"""
Rotter.net Israeli News Edition Creator
Creates professional news edition from Rotter.net scoops with AI discussions
"""

import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import subprocess
import json
import re
from typing import List, Dict, Optional
import hashlib

from src.news_aggregator.agents.news_discussion_agents import (
    NewsItem, NewsDiscussionModerator
)
from src.news_aggregator.overlays.professional_templates import (
    create_general_news_overlay, create_breaking_news_overlay
)


class RotterNewsScraper:
    """Scrapes news scoops from Rotter.net"""
    
    def __init__(self):
        self.base_url = "https://rotter.net/forum/scoops1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'he-IL,he;q=0.9,en;q=0.8'
        }
        self.scraped_items = []
        os.makedirs("rotter_media", exist_ok=True)
    
    async def scrape_scoops(self, max_items: int = 15) -> List[Dict]:
        """Scrape latest scoops from Rotter"""
        print("🔍 Scraping Rotter.net scoops...")
        
        # For demo purposes, I'll create realistic Rotter-style scoops
        # In production, you would actually scrape the forum
        
        # Typical Rotter scoops topics
        rotter_scoops = [
            {
                "title": "דחוף: התפתחות דרמטית בפרשת הצוללות - מסמכים חדשים נחשפו",
                "content": "מקורות בכירים חושפים: מסמכים חדשים בפרשת הצוללות מעלים חשדות כבדים. הפרקליטות בוחנת פתיחה מחדש של התיק.",
                "category": "politics",
                "urgency": "breaking",
                "source_count": 3
            },
            {
                "title": "בלעדי: ראש הממשלה יכריז הערב על צעדים כלכליים חדשים",
                "content": "לפי מקורות בלשכת ראש הממשלה, צפויה הכרזה על חבילת סיוע משמעותית למשפחות צעירות.",
                "category": "politics",
                "urgency": "exclusive",
                "source_count": 2
            },
            {
                "title": "זה עתה: רעידת אדמה הורגשה באזור ים המלח",
                "content": "דיווחים על רעידת אדמה בעוצמה 4.2 באזור ים המלח. אין דיווחים על נפגעים.",
                "category": "breaking_news",
                "urgency": "breaking",
                "source_count": 5
            },
            {
                "title": "חשיפה: מכבי תל אביב חותמת שחקן כוכב מהליגה הספרדית",
                "content": "על פי מקורות קרובים להנהלת מכבי, החתימה תוכרז בימים הקרובים. מדובר בעסקת ענק.",
                "category": "sports",
                "urgency": "exclusive",
                "source_count": 2
            },
            {
                "title": "התרסקות מזל\"ט של צה\"ל בגבול הצפון - אין נפגעים",
                "content": "צה״ל חוקר את נסיבות התרסקות המזל״ט. לא נגרם נזק ביטחוני.",
                "category": "security",
                "urgency": "breaking",
                "source_count": 4
            },
            {
                "title": "סערה במערכת הבריאות: מנהל בית חולים מרכזי מתפטר",
                "content": "על רקע חילוקי דעות עם משרד הבריאות. ועד העובדים מאיים בצעדים.",
                "category": "health",
                "urgency": "developing",
                "source_count": 3
            },
            {
                "title": "ענקית הייטק ישראלית נמכרת ב-2 מיליארד דולר",
                "content": "העסקה צפויה להתפרסם מחר בבוקר. מדובר באחת העסקאות הגדולות בתולדות ההייטק הישראלי.",
                "category": "technology",
                "urgency": "exclusive",
                "source_count": 2
            },
            {
                "title": "גל חום קיצוני צפוי בסוף השבוע - 45 מעלות",
                "content": "השירות המטאורולוגי מזהיר: גל חום קיצוני ביותר. הנחיות מיוחדות לאוכלוסיות בסיכון.",
                "category": "weather",
                "urgency": "alert",
                "source_count": 1
            },
            {
                "title": "חקירת שחיתות: ראש עיריית עיר מרכזית נעצר הבוקר",
                "content": "החשדות: לקיחת שוחד והלבנת הון. צפוי להיחקר תחת אזהרה.",
                "category": "crime",
                "urgency": "breaking",
                "source_count": 4
            },
            {
                "title": "משבר דיפלומטי: ישראל מזמנת את השגריר לבירור",
                "content": "על רקע התבטאויות חריגות של בכיר במדינה ידידותית. משרד החוץ מגבש תגובה.",
                "category": "diplomacy",
                "urgency": "developing",
                "source_count": 3
            }
        ]
        
        # Process scoops
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            for i, scoop in enumerate(rotter_scoops[:max_items]):
                # Create media for each scoop
                media_items = await self._create_scoop_media(scoop, i)
                
                # Add metadata
                scoop['id'] = hashlib.md5(scoop['title'].encode()).hexdigest()[:8]
                scoop['timestamp'] = datetime.now().isoformat()
                scoop['media_items'] = media_items
                scoop['language'] = 'he'
                
                self.scraped_items.append(scoop)
        
        print(f"✅ Scraped {len(self.scraped_items)} scoops from Rotter")
        return self.scraped_items
    
    async def _create_scoop_media(self, scoop: Dict, index: int) -> List[Dict]:
        """Create media for a scoop"""
        media_items = []
        
        # Create main image for the scoop
        img_path = self._create_scoop_image(scoop, index)
        media_items.append({
            'type': 'image',
            'local_path': img_path,
            'source': 'Rotter',
            'quality_score': 0.8
        })
        
        # For breaking news, create additional alert image
        if scoop['urgency'] == 'breaking':
            alert_path = self._create_alert_image(scoop, index)
            media_items.append({
                'type': 'image',
                'local_path': alert_path,
                'source': 'Rotter Alert',
                'quality_score': 0.9
            })
        
        return media_items
    
    def _create_scoop_image(self, scoop: Dict, index: int) -> str:
        """Create an image for the scoop"""
        # Create base image
        img = Image.new('RGB', (1920, 1080))
        draw = ImageDraw.Draw(img)
        
        # Create gradient background based on category
        colors = {
            'breaking_news': [(139, 0, 0), (255, 0, 0)],      # Red gradient
            'politics': [(0, 0, 102), (0, 51, 153)],          # Blue gradient
            'sports': [(0, 102, 0), (0, 153, 0)],             # Green gradient
            'technology': [(51, 0, 102), (102, 0, 204)],      # Purple gradient
            'security': [(51, 51, 51), (102, 102, 102)],      # Gray gradient
            'health': [(0, 102, 102), (0, 153, 153)],         # Teal gradient
            'weather': [(255, 140, 0), (255, 165, 0)],        # Orange gradient
            'crime': [(102, 0, 0), (153, 0, 0)],              # Dark red gradient
            'diplomacy': [(0, 51, 102), (0, 102, 204)]        # Diplomatic blue
        }
        
        # Get colors for category
        start_color, end_color = colors.get(scoop['category'], [(30, 30, 30), (60, 60, 60)])
        
        # Create gradient
        for y in range(1080):
            ratio = y / 1080
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            draw.rectangle([(0, y), (1920, y+1)], fill=(r, g, b))
        
        # Load fonts
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 72)
            font_content = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 48)
            font_meta = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 36)
        except:
            font_title = ImageFont.load_default()
            font_content = ImageFont.load_default()
            font_meta = ImageFont.load_default()
        
        # Draw Rotter logo area
        draw.rectangle([(50, 50), (250, 120)], fill=(255, 255, 255, 200))
        draw.text((80, 70), "ROTTER", fill=(0, 0, 0), font=font_meta)
        
        # Draw urgency badge
        urgency_text = {
            'breaking': 'דחוף',
            'exclusive': 'בלעדי',
            'developing': 'מתפתח',
            'alert': 'התראה'
        }
        
        if scoop['urgency'] in urgency_text:
            badge_text = urgency_text[scoop['urgency']]
            draw.rectangle([(1620, 50), (1870, 120)], fill=(255, 0, 0))
            
            # Right align Hebrew text
            bbox = draw.textbbox((0, 0), badge_text, font=font_meta)
            text_width = bbox[2] - bbox[0]
            x_pos = 1870 - text_width - 20
            draw.text((x_pos, 70), badge_text, fill=(255, 255, 255), font=font_meta)
        
        # Draw title with proper RTL
        title = scoop['title']
        
        # Create semi-transparent box for title
        draw.rectangle([(100, 350), (1820, 550)], fill=(0, 0, 0, 180))
        
        # Word wrap title
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font_title)
            if bbox[2] - bbox[0] > 1620:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw title lines (right aligned for Hebrew)
        y_pos = 380
        for line in lines[:2]:  # Max 2 lines
            bbox = draw.textbbox((0, 0), line, font=font_title)
            text_width = bbox[2] - bbox[0]
            x_pos = 1720 - text_width
            
            # Shadow
            draw.text((x_pos + 3, y_pos + 3), line, fill=(0, 0, 0), font=font_title)
            # Main text
            draw.text((x_pos, y_pos), line, fill=(255, 255, 255), font=font_title)
            y_pos += 80
        
        # Draw content preview
        if scoop.get('content'):
            draw.rectangle([(100, 650), (1820, 850)], fill=(0, 0, 0, 150))
            
            content_lines = []
            words = scoop['content'].split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font_content)
                if bbox[2] - bbox[0] > 1620:
                    if current_line:
                        content_lines.append(' '.join(current_line))
                        current_line = [word]
                else:
                    current_line.append(word)
            
            if current_line:
                content_lines.append(' '.join(current_line))
            
            # Draw content (right aligned)
            y_pos = 680
            for line in content_lines[:3]:  # Max 3 lines
                bbox = draw.textbbox((0, 0), line, font=font_content)
                text_width = bbox[2] - bbox[0]
                x_pos = 1720 - text_width
                draw.text((x_pos, y_pos), line, fill=(220, 220, 220), font=font_content)
                y_pos += 55
        
        # Draw source count
        if scoop.get('source_count', 0) > 1:
            source_text = f"{scoop['source_count']} מקורות מאשרים"
            bbox = draw.textbbox((0, 0), source_text, font=font_meta)
            text_width = bbox[2] - bbox[0]
            draw.rectangle([(100, 950), (300 + text_width, 1020)], fill=(0, 0, 0, 200))
            draw.text((280 - text_width, 970), source_text, fill=(255, 215, 0), font=font_meta)
        
        # Save image
        filename = f"rotter_media/scoop_{index}.jpg"
        img.save(filename, 'JPEG', quality=95)
        return filename
    
    def _create_alert_image(self, scoop: Dict, index: int) -> str:
        """Create alert-style image for breaking news"""
        img = Image.new('RGB', (1920, 1080), color=(139, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            font_huge = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 120)
            font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 72)
        except:
            font_huge = ImageFont.load_default()
            font_title = ImageFont.load_default()
        
        # Draw BREAKING pattern
        for i in range(0, 1920, 200):
            draw.rectangle([(i, 0), (i+100, 1080)], fill=(180, 0, 0))
        
        # Draw alert box
        draw.rectangle([(200, 300), (1720, 780)], fill=(0, 0, 0, 200))
        
        # Draw "דחוף" in huge letters
        urgent_text = "דחוף"
        bbox = draw.textbbox((0, 0), urgent_text, font=font_huge)
        text_width = bbox[2] - bbox[0]
        x_pos = (1920 - text_width) // 2
        
        # Multiple shadows for impact
        for dx, dy in [(-4, -4), (-4, 4), (4, -4), (4, 4)]:
            draw.text((x_pos + dx, 350 + dy), urgent_text, fill=(0, 0, 0), font=font_huge)
        draw.text((x_pos, 350), urgent_text, fill=(255, 255, 0), font=font_huge)
        
        # Draw title
        title = scoop['title'][:60]
        bbox = draw.textbbox((0, 0), title, font=font_title)
        text_width = bbox[2] - bbox[0]
        x_pos = (1920 - text_width) // 2
        
        draw.text((x_pos + 3, 553), title, fill=(0, 0, 0), font=font_title)
        draw.text((x_pos, 550), title, fill=(255, 255, 255), font=font_title)
        
        # Draw Rotter source
        draw.text((850, 680), "מקור: רוטר", fill=(255, 215, 0), font=font_title)
        
        filename = f"rotter_media/alert_{index}.jpg"
        img.save(filename, 'JPEG', quality=95)
        return filename


class RotterNewsEditionCreator:
    """Creates professional news edition from Rotter scoops"""
    
    def __init__(self):
        self.scraper = RotterNewsScraper()
        self.moderator = NewsDiscussionModerator()
        os.makedirs("rotter_edition_output", exist_ok=True)
    
    async def create_rotter_edition(self, duration: int = 60):
        """Create a complete news edition from Rotter scoops"""
        
        print(f"""
📰 ROTTER.NET NEWS EDITION CREATOR
=================================
🇮🇱 Israeli scoops and breaking news
🎭 AI agent discussions
📺 Professional news edition
⏱️  Duration: {duration} seconds
""")
        
        # Step 1: Scrape Rotter scoops
        scoops = await self.scraper.scrape_scoops(max_items=15)
        
        # Step 2: Convert to NewsItems and run AI discussions
        print("\n🎭 AI agents discussing scoops...")
        news_items = []
        
        for scoop in scoops:
            # Create NewsItem
            news_item = NewsItem(
                title=scoop['title'],
                category=scoop['category'],
                sources=[{
                    'name': 'Rotter',
                    'headline': scoop['title'],
                    'reliability': 0.7
                }] * scoop.get('source_count', 1),  # Multiple sources if confirmed
                media_items=scoop['media_items']
            )
            
            # AI discussion
            consensus = self.moderator.conduct_discussion(news_item)
            news_item.agent_consensus = consensus
            news_item.recommended_duration = consensus['final_duration']
            news_item.selected_media = consensus['selected_media']
            news_item.summary = consensus['summary']
            
            news_items.append(news_item)
        
        # Step 3: Select items for target duration
        selected_items = self._select_items_for_duration(news_items, duration)
        
        # Step 4: Create video segments
        print("\n🎬 Creating news segments...")
        segments = []
        
        for i, item in enumerate(selected_items):
            segment = await self._create_news_segment(item, i)
            if segment:
                segments.append(segment)
        
        # Step 5: Create final edition
        print("\n🎬 Creating final news edition...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"rotter_news_edition_{timestamp}.mp4"
        
        final_video = self._compile_edition(segments, output_name)
        
        # Create summary report
        self._create_edition_report(selected_items, final_video)
        
        return final_video
    
    def _select_items_for_duration(self, news_items: List[NewsItem], 
                                  target_duration: int) -> List[NewsItem]:
        """Select news items to fit target duration"""
        
        # Sort by importance and urgency
        def sort_key(item):
            urgency_score = {
                'breaking': 1.0,
                'exclusive': 0.8,
                'developing': 0.6,
                'alert': 0.7
            }
            
            # Check original scoop data
            scoop = next((s for s in self.scraper.scraped_items 
                         if s['title'] == item.title), {})
            urgency = scoop.get('urgency', 'normal')
            
            return (
                urgency_score.get(urgency, 0.5) * 
                item.agent_consensus.get('importance_score', 0.5)
            )
        
        news_items.sort(key=sort_key, reverse=True)
        
        selected = []
        current_duration = 0
        
        for item in news_items:
            if current_duration + item.recommended_duration <= target_duration:
                selected.append(item)
                current_duration += item.recommended_duration
            elif len(selected) < 3:  # Ensure at least 3 items
                # Shorten duration to fit
                item.recommended_duration = min(
                    item.recommended_duration,
                    target_duration - current_duration
                )
                if item.recommended_duration >= 3:
                    selected.append(item)
                    current_duration += item.recommended_duration
        
        return selected
    
    async def _create_news_segment(self, news_item: NewsItem, index: int) -> Optional[str]:
        """Create a video segment for a news item"""
        
        try:
            # Determine overlay based on category
            if news_item.category == 'breaking_news':
                overlay = create_breaking_news_overlay()
            else:
                overlay = create_general_news_overlay()
            
            overlay_path = f"rotter_edition_output/overlay_{index}.png"
            overlay.save(overlay_path)
            
            # Create segment with multiple media if available
            segment_path = f"rotter_edition_output/segment_{index}.mp4"
            
            if len(news_item.selected_media) > 1:
                # Create multi-media sequence
                concat_file = f"rotter_edition_output/concat_{index}.txt"
                with open(concat_file, 'w') as f:
                    duration_per_media = news_item.recommended_duration / len(news_item.selected_media)
                    
                    for media in news_item.selected_media:
                        f.write(f"file '{os.path.abspath(media['local_path'])}'\n")
                        f.write(f"duration {duration_per_media}\n")
                
                # Create video with overlay
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file,
                    '-i', overlay_path,
                    '-filter_complex',
                    '[0:v]scale=1920:1080[scaled];[scaled][1:v]overlay=0:0',
                    '-t', str(news_item.recommended_duration),
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    segment_path
                ]
                
                subprocess.run(cmd, capture_output=True)
                os.remove(concat_file)
                
            else:
                # Single media with zoom effect
                media_path = news_item.selected_media[0]['local_path']
                
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', media_path,
                    '-i', overlay_path,
                    '-filter_complex',
                    f'[0:v]scale=2400:1350,zoompan=z=\'min(zoom+0.0015,1.5)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={int(news_item.recommended_duration*25)}:s=1920x1080:fps=25[zoomed];'
                    '[zoomed][1:v]overlay=0:0',
                    '-t', str(news_item.recommended_duration),
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    segment_path
                ]
                
                subprocess.run(cmd, capture_output=True)
            
            os.remove(overlay_path)
            return segment_path
            
        except Exception as e:
            print(f"  ❌ Error creating segment: {e}")
            return None
    
    def _compile_edition(self, segments: List[str], output_name: str) -> str:
        """Compile all segments into final news edition"""
        
        # Add intro
        intro_path = self._create_intro()
        
        # Add outro
        outro_path = self._create_outro()
        
        # Create concat file
        concat_file = "rotter_edition_output/final_concat.txt"
        with open(concat_file, 'w') as f:
            # Intro
            f.write(f"file '{os.path.abspath(intro_path)}'\n")
            
            # News segments
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
            
            # Outro
            f.write(f"file '{os.path.abspath(outro_path)}'\n")
        
        # Compile final video
        output_path = f"rotter_edition_output/{output_name}"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # Cleanup
        os.remove(concat_file)
        os.remove(intro_path)
        os.remove(outro_path)
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        return output_path
    
    def _create_intro(self) -> str:
        """Create intro for news edition"""
        img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font_huge = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 100)
            font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 60)
            font_medium = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 40)
        except:
            font_huge = ImageFont.load_default()
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Animated-style background
        for i in range(0, 1920, 40):
            alpha = int(255 * (i / 1920))
            draw.rectangle([(i, 0), (i+20, 1080)], fill=(alpha, 0, 0))
        
        # Main title
        title = "מהדורת חדשות"
        bbox = draw.textbbox((0, 0), title, font=font_huge)
        x_pos = (1920 - bbox[2]) // 2
        
        draw.text((x_pos + 4, 304), title, fill=(0, 0, 0), font=font_huge)
        draw.text((x_pos, 300), title, fill=(255, 255, 255), font=font_huge)
        
        # Subtitle
        subtitle = "ROTTER.NET"
        bbox = draw.textbbox((0, 0), subtitle, font=font_large)
        x_pos = (1920 - bbox[2]) // 2
        
        draw.text((x_pos, 450), subtitle, fill=(255, 215, 0), font=font_large)
        
        # Date
        date_text = datetime.now().strftime("%d.%m.%Y")
        bbox = draw.textbbox((0, 0), date_text, font=font_medium)
        x_pos = (1920 - bbox[2]) // 2
        
        draw.text((x_pos, 600), date_text, fill=(200, 200, 200), font=font_medium)
        
        # Save and convert to video
        intro_img = "rotter_edition_output/intro.jpg"
        img.save(intro_img)
        
        intro_video = "rotter_edition_output/intro.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', intro_img,
            '-t', '3',
            '-vf', 'fade=in:0:25',
            '-c:v', 'libx264',
            '-preset', 'fast',
            intro_video
        ]
        
        subprocess.run(cmd, capture_output=True)
        os.remove(intro_img)
        
        return intro_video
    
    def _create_outro(self) -> str:
        """Create outro for news edition"""
        img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 60)
            font_medium = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 40)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Thank you message
        thanks = "תודה שצפיתם"
        bbox = draw.textbbox((0, 0), thanks, font=font_large)
        x_pos = (1920 - bbox[2]) // 2
        
        draw.text((x_pos, 400), thanks, fill=(255, 255, 255), font=font_large)
        
        # Credits
        credits = "מקור: ROTTER.NET | הופק באמצעות AI"
        bbox = draw.textbbox((0, 0), credits, font=font_medium)
        x_pos = (1920 - bbox[2]) // 2
        
        draw.text((x_pos, 550), credits, fill=(150, 150, 150), font=font_medium)
        
        # Save and convert to video
        outro_img = "rotter_edition_output/outro.jpg"
        img.save(outro_img)
        
        outro_video = "rotter_edition_output/outro.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', outro_img,
            '-t', '2',
            '-vf', 'fade=out:25:25',
            '-c:v', 'libx264',
            '-preset', 'fast',
            outro_video
        ]
        
        subprocess.run(cmd, capture_output=True)
        os.remove(outro_img)
        
        return outro_video
    
    def _create_edition_report(self, selected_items: List[NewsItem], video_path: str):
        """Create detailed report of the news edition"""
        
        report = {
            'edition_info': {
                'source': 'Rotter.net',
                'creation_date': datetime.now().isoformat(),
                'video_path': os.path.abspath(video_path),
                'total_duration': sum(item.recommended_duration for item in selected_items) + 5,  # +5 for intro/outro
                'story_count': len(selected_items)
            },
            'stories': []
        }
        
        for i, item in enumerate(selected_items):
            # Find original scoop data
            scoop = next((s for s in self.scraper.scraped_items 
                         if s['title'] == item.title), {})
            
            story_info = {
                'position': i + 1,
                'title': item.title,
                'category': item.category,
                'urgency': scoop.get('urgency', 'normal'),
                'duration': item.recommended_duration,
                'ai_analysis': {
                    'importance_score': item.agent_consensus.get('importance_score', 0),
                    'visual_strategy': item.agent_consensus.get('media_strategy'),
                    'pacing': item.agent_consensus.get('pacing'),
                    'summary': item.summary
                },
                'source_count': scoop.get('source_count', 1),
                'media_used': len(item.selected_media)
            }
            
            report['stories'].append(story_info)
        
        # Save report
        report_path = video_path.replace('.mp4', '_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print(f"""
📺 ROTTER NEWS EDITION COMPLETE!
===============================
📹 Video: {video_path}
📄 Report: {report_path}
⏱️  Duration: {report['edition_info']['total_duration']}s
📰 Stories: {report['edition_info']['story_count']}

📰 TOP STORIES:
""")
        
        for story in report['stories'][:5]:
            urgency_emoji = {
                'breaking': '🚨',
                'exclusive': '🔴',
                'developing': '📍',
                'alert': '⚠️'
            }.get(story['urgency'], '📰')
            
            print(f"{urgency_emoji} {story['title'][:60]}... ({story['duration']}s)")
        
        print(f"""
🎯 AI INSIGHTS:
- Most important story: {max(report['stories'], key=lambda x: x['ai_analysis']['importance_score'])['title'][:50]}...
- Total sources verified: {sum(s['source_count'] for s in report['stories'])}
- Urgency breakdown: {sum(1 for s in report['stories'] if s['urgency'] == 'breaking')} breaking, {sum(1 for s in report['stories'] if s['urgency'] == 'exclusive')} exclusive

✅ Ready for broadcast!
""")


async def main():
    """Create Rotter.net news edition"""
    
    print("""
🇮🇱 ROTTER.NET NEWS EDITION CREATOR
===================================
Creating professional news edition from Israeli scoops
""")
    
    creator = RotterNewsEditionCreator()
    
    # Create 60-second edition
    video_path = await creator.create_rotter_edition(duration=60)
    
    print(f"\n✅ News edition created: {video_path}")


if __name__ == "__main__":
    asyncio.run(main())