#!/usr/bin/env python3
"""
Multi-Source Hebrew News Aggregator
Creates news videos from Ynet, Rotter, and BBC in Hebrew
"""

import asyncio
import os
from datetime import datetime
from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper
from src.news_aggregator.agents.news_discussion_agents import NewsDiscussionModerator, NewsItem
from src.news_aggregator.overlays.professional_templates import create_breaking_news_overlay
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import subprocess
import ssl
import certifi


class HebrewMultiSourceNews:
    """Aggregates news from multiple sources in Hebrew"""
    
    def __init__(self):
        self.scraper = UniversalNewsScraper()
        self.moderator = NewsDiscussionModerator()
        self._setup_scrapers()
        self.font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        os.makedirs("hebrew_aggregated_news", exist_ok=True)
    
    def _setup_scrapers(self):
        """Configure scrapers for each source"""
        
        # Ynet configuration
        self.scraper.add_website_config('ynet', {
            'name': 'Ynet',
            'base_url': 'https://www.ynet.co.il',
            'language': 'he',
            'selectors': {
                'article_container': 'article.slotView, div.MultiArticleComponenta, div.article-short',
                'title': 'h2, h3, .slotTitle',
                'url': 'a[href]',
                'description': '.slotSubTitle, .description',
                'author': '.author',
                'date': 'time, .date'
            },
            'media_extraction': {
                'image_selector': 'img[src*="ynet"], img.image',
                'video_selector': 'video, iframe[src*="youtube"], iframe[src*="video"]'
            },
            'category_mapping': {
                'politics': ['פוליטי', 'כנסת', 'ממשלה', 'בחירות'],
                'security': ['ביטחון', 'צבא', 'צה"ל', 'איראן'],
                'sports': ['ספורט', 'כדורגל', 'מכבי', 'הפועל'],
                'economy': ['כלכלה', 'בורסה', 'שקל', 'דולר'],
                'tech': ['טכנולוגיה', 'הייטק', 'סטארטאפ']
            }
        })
        
        # Rotter configuration
        self.scraper.add_website_config('rotter', {
            'name': 'Rotter.net',
            'base_url': 'https://rotter.net/scoopscache.html',
            'language': 'he',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'he,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            'selectors': {
                'article_container': 'table tbody tr, div.forum_entry',
                'title': 'td font[size="3"] b, td b',
                'url': 'a[href*="scoops"]',
                'description': 'td:nth-child(2)',
                'author': 'td:last-child',
                'date': 'td:first-child'
            },
            'category_mapping': {
                'breaking': ['דחוף', 'בדיוק עכשיו', 'התרעה'],
                'exclusive': ['בלעדי', 'חשיפה', 'ראשון לפרסם']
            }
        })
        
        # BBC Hebrew configuration  
        self.scraper.add_website_config('bbc_hebrew', {
            'name': 'BBC Hebrew',
            'base_url': 'https://www.bbc.com/hebrew',
            'language': 'he',
            'selectors': {
                'article_container': 'article, div.media__content',
                'title': 'h2, h3.media__title',
                'url': 'a[href]',
                'description': '.media__summary',
                'author': '.byline',
                'date': 'time'
            },
            'media_extraction': {
                'image_selector': 'img.media__image, img[src*="bbc"]',
                'video_selector': 'video, div.media-player'
            }
        })
    
    async def aggregate_hebrew_news(self, duration_seconds=60, max_stories=10):
        """Aggregate news from all sources and create Hebrew video"""
        
        sources_list = []
        if 'ynet' in self.scraper.configs:
            sources_list.append('Ynet')
        if 'rotter' in self.scraper.configs:
            sources_list.append('Rotter.net')
        if 'bbc_hebrew' in self.scraper.configs:
            sources_list.append('BBC')
        
        print(f"""
🌐 אוסף חדשות בעברית ממקורות מרובים
====================================
📰 מקורות: {', '.join(sources_list)}
🇮🇱 שפה: עברית
⏱️  משך: {duration_seconds} שניות
📊 מקסימום סיפורים: {max_stories}
""")
        
        # Collect news from all sources
        all_articles = []
        
        # Scrape Ynet if configured
        if 'ynet' in self.scraper.configs:
            print("\n📱 אוסף מ-Ynet...")
            ynet_articles = await self.scraper.scrape_website('ynet', max_items=15)
            if ynet_articles:
                print(f"   ✅ נמצאו {len(ynet_articles)} כתבות")
                all_articles.extend([{**a, 'source': 'Ynet'} for a in ynet_articles])
        
        # Scrape Rotter if configured
        if 'rotter' in self.scraper.configs:
            print("\n🔥 אוסף מרוטר...")
            rotter_articles = await self.scraper.scrape_website('rotter', max_items=10)
            if rotter_articles:
                print(f"   ✅ נמצאו {len(rotter_articles)} סקופים")
                all_articles.extend([{**a, 'source': 'Rotter'} for a in rotter_articles])
        
        # Only scrape BBC if configured
        if 'bbc_hebrew' in self.scraper.configs:
            print("\n🌍 אוסף מ-BBC בעברית...")
            bbc_articles = await self.scraper.scrape_website('bbc_hebrew', max_items=10)
            if bbc_articles:
                print(f"   ✅ נמצאו {len(bbc_articles)} כתבות")
                all_articles.extend([{**a, 'source': 'BBC'} for a in bbc_articles])
        
        if not all_articles:
            print("❌ לא נמצאו כתבות!")
            return None
        
        # Sort by importance and recency
        print(f"\n📊 סה״כ נאספו {len(all_articles)} כתבות")
        
        # Download media
        print("\n📸 מוריד תמונות וסרטונים...")
        await self._download_all_media(all_articles)
        
        # AI selection of best stories
        print("\n🤖 בוחר את הסיפורים החשובים ביותר...")
        selected_articles = await self._select_best_stories(all_articles, max_stories)
        
        # Allocate durations
        print("\n⏱️  מחלק זמנים לכל סיפור...")
        story_durations = self._allocate_durations(selected_articles, duration_seconds)
        
        # Create video
        print("\n🎬 יוצר וידאו חדשות מאוחד...")
        output_path = await self._create_aggregated_video(selected_articles, story_durations, duration_seconds)
        
        return output_path
    
    async def _download_all_media(self, articles):
        """Download media for all articles"""
        # Create SSL context with certificate verification
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            for i, article in enumerate(articles):
                if article.get('media_url'):
                    try:
                        async with session.get(article['media_url']) as resp:
                            if resp.status == 200:
                                ext = article['media_url'].split('.')[-1][:3]
                                if ext not in ['jpg', 'png', 'mp4']:
                                    ext = 'jpg'
                                filename = f"hebrew_aggregated_news/{article['source']}_{i}.{ext}"
                                with open(filename, 'wb') as f:
                                    f.write(await resp.read())
                                article['local_media'] = filename
                                print(f"   ✅ הורדה: {article['source']} - {i}")
                    except:
                        pass
    
    async def _select_best_stories(self, articles, max_stories):
        """Use AI to select most important stories"""
        # Score based on source, recency, keywords
        scored = []
        
        for article in articles:
            score = 0.5  # Base score
            
            # Source weighting
            if article['source'] == 'Rotter':
                score += 0.2  # Breaking news bonus
            elif article['source'] == 'Ynet':
                score += 0.15  # Major outlet
            
            # Keywords
            title = article.get('title', '').lower()
            if any(word in title for word in ['דחוף', 'התרעה', 'עכשיו']):
                score += 0.3
            if any(word in title for word in ['בלעדי', 'חשיפה', 'ראשון']):
                score += 0.2
            
            # Has media
            if article.get('local_media'):
                score += 0.1
            
            scored.append((score, article))
        
        # Sort by score and select top stories
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [item[1] for item in scored[:max_stories]]
        
        return selected
    
    def _allocate_durations(self, articles, total_duration):
        """Allocate duration to each story"""
        # Reserve 3 seconds for intro/outro
        content_duration = total_duration - 3
        
        # First 3 stories get more time
        durations = []
        if len(articles) <= 3:
            per_story = content_duration / len(articles)
            durations = [per_story] * len(articles)
        else:
            # First 3 get 40% of time
            top_duration = (content_duration * 0.4) / 3
            # Rest share 60%
            rest_duration = (content_duration * 0.6) / (len(articles) - 3)
            
            durations = [top_duration] * 3 + [rest_duration] * (len(articles) - 3)
        
        return durations
    
    async def _create_aggregated_video(self, articles, durations, total_duration):
        """Create the final aggregated video"""
        segments = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create intro
        intro_path = self._create_hebrew_intro()
        segments.append(intro_path)
        
        # Create story segments
        for i, (article, duration) in enumerate(zip(articles, durations)):
            segment_path = self._create_story_segment(article, i+1, len(articles), duration)
            segments.append(segment_path)
        
        # Create outro
        outro_path = self._create_hebrew_outro(len(articles))
        segments.append(outro_path)
        
        # Compile video
        output_path = f"hebrew_aggregated_news/hebrew_news_{timestamp}.mp4"
        self._compile_segments(segments, output_path)
        
        # Cleanup
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        # Create report
        report_path = output_path.replace('.mp4', '_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"מהדורת חדשות בעברית - {timestamp}\n")
            f.write(f"{'='*50}\n")
            f.write(f"משך: {total_duration} שניות\n")
            f.write(f"מספר כתבות: {len(articles)}\n\n")
            
            for i, (article, dur) in enumerate(zip(articles, durations)):
                f.write(f"{i+1}. {article['title']}\n")
                f.write(f"   מקור: {article['source']}\n")
                f.write(f"   משך: {dur:.1f} שניות\n\n")
        
        print(f"""
✅ וידאו חדשות בעברית הושלם!
===========================
📹 קובץ: {output_path}
📄 דוח: {report_path}
⏱️  משך: {total_duration} שניות
📰 כתבות: {len(articles)}

📊 חלוקת מקורות:
- Ynet: {len([a for a in articles if a['source'] == 'Ynet'])}
- Rotter: {len([a for a in articles if a['source'] == 'Rotter'])}  
- BBC: {len([a for a in articles if a['source'] == 'BBC'])}

✅ מוכן לצפייה!
""")
        
        return output_path
    
    def _create_hebrew_intro(self):
        """Create Hebrew intro"""
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype(self.font_path, 80)
            font_medium = ImageFont.truetype(self.font_path, 50)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Gradient background
        for y in range(1080):
            gray = int(10 + (y / 1080) * 30)
            draw.rectangle([(0, y), (1920, y+1)], fill=(gray, gray, gray))
        
        draw.text((960, 350), "מהדורת חדשות", fill=(255, 255, 255), 
                 font=font_large, anchor="ma")
        draw.text((960, 500), "Ynet • Rotter • BBC", fill=(200, 200, 200), 
                 font=font_medium, anchor="ma")
        
        intro_path = "hebrew_aggregated_news/intro.jpg"
        img.save(intro_path)
        
        # Convert to video
        intro_video = "hebrew_aggregated_news/intro.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', intro_path,
            '-t', '2', '-vf', 'fade=t=in:d=0.5',
            '-c:v', 'libx264', '-preset', 'fast', intro_video
        ], capture_output=True)
        
        os.remove(intro_path)
        return intro_video
    
    def _create_story_segment(self, article, position, total, duration):
        """Create a story segment"""
        # Use overlay if media exists
        if article.get('local_media') and os.path.exists(article['local_media']):
            # Create overlay
            overlay = create_breaking_news_overlay(
                article['title'],
                f"{article['source']} - סיפור {position}/{total}",
                style='rtl'
            )
            overlay_path = f"hebrew_aggregated_news/overlay_{position}.png"
            overlay.save(overlay_path)
            
            # Apply overlay to media
            segment_path = f"hebrew_aggregated_news/segment_{position}.mp4"
            subprocess.run([
                'ffmpeg', '-y',
                '-i', article['local_media'],
                '-i', overlay_path,
                '-filter_complex', '[0:v][1:v]overlay=0:0',
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                segment_path
            ], capture_output=True)
            
            os.remove(overlay_path)
        else:
            # Create text-only segment
            segment_path = self._create_text_segment(article, position, total, duration)
        
        return segment_path
    
    def _create_text_segment(self, article, position, total, duration):
        """Create text-only segment"""
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
        
        # Source color coding
        source_colors = {
            'Ynet': (0, 150, 255),
            'Rotter': (255, 0, 0),
            'BBC': (200, 0, 200)
        }
        color = source_colors.get(article['source'], (150, 150, 150))
        
        # Header
        draw.rectangle([(0, 0), (1920, 120)], fill=color)
        draw.text((50, 40), article['source'], fill=(255, 255, 255), font=font_medium)
        draw.text((1870, 40), f"{position}/{total}", fill=(255, 255, 255), 
                 font=font_medium, anchor="ra")
        
        # Title
        draw.text((960, 400), article['title'], fill=(255, 255, 255), 
                 font=font_large, anchor="ma")
        
        # Description if available
        if article.get('description'):
            draw.text((960, 600), article['description'][:100] + "...", 
                     fill=(200, 200, 200), font=font_medium, anchor="ma")
        
        img_path = f"hebrew_aggregated_news/text_segment_{position}.jpg"
        img.save(img_path)
        
        segment_path = f"hebrew_aggregated_news/segment_{position}.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', img_path,
            '-t', str(duration), '-vf', 'scale=1920:1080',
            '-c:v', 'libx264', '-preset', 'fast', segment_path
        ], capture_output=True)
        
        os.remove(img_path)
        return segment_path
    
    def _create_hebrew_outro(self, story_count):
        """Create Hebrew outro"""
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
        
        outro_path = "hebrew_aggregated_news/outro.jpg"
        img.save(outro_path)
        
        outro_video = "hebrew_aggregated_news/outro.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', outro_path,
            '-t', '1', '-vf', 'fade=t=out:st=0.5:d=0.5',
            '-c:v', 'libx264', '-preset', 'fast', outro_video
        ], capture_output=True)
        
        os.remove(outro_path)
        return outro_video
    
    def _compile_segments(self, segments, output_path):
        """Compile all segments into final video"""
        concat_file = "hebrew_aggregated_news/concat.txt"
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
    """Run the Hebrew multi-source news aggregator"""
    aggregator = HebrewMultiSourceNews()
    
    # Create 60-second news video from all sources
    video_path = await aggregator.aggregate_hebrew_news(
        duration_seconds=60,
        max_stories=8
    )
    
    return video_path


if __name__ == "__main__":
    asyncio.run(main())