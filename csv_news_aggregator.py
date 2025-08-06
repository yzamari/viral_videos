#!/usr/bin/env python3
"""
CSV-Based News Aggregator
Flexible system for creating news from CSV files with any sources
"""

import csv
import os
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import subprocess
import json
from urllib.parse import urlparse
import ssl
import certifi

from src.news_aggregator.agents.news_discussion_agents import NewsDiscussionModerator, NewsItem
from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper
from src.news_aggregator.overlays.professional_templates import create_breaking_news_overlay


class CSVNewsAggregator:
    """Create news videos from CSV files with flexible content"""
    
    def __init__(self):
        self.scraper = UniversalNewsScraper()
        self.moderator = NewsDiscussionModerator()
        self.font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        os.makedirs("csv_news_output", exist_ok=True)
        os.makedirs("csv_news_media", exist_ok=True)
    
    async def create_news_from_csv(self, csv_path: str, 
                                  duration_seconds: int = 60,
                                  language: str = 'he',
                                  style: str = 'professional',
                                  platform: str = 'general',
                                  output_filename: Optional[str] = None):
        """Create news video from CSV file"""
        
        # Platform-specific settings
        platform_configs = {
            'tiktok': {
                'aspect_ratio': '9:16',
                'width': 1080,
                'height': 1920,
                'max_duration': 60,
                'avg_story_duration': 2.5,
                'font_scale': 1.2,
                'style_override': 'casual' if style == 'professional' else style,
                'transitions': True
            },
            'instagram': {
                'aspect_ratio': '9:16',
                'width': 1080,
                'height': 1920,
                'max_duration': 60,
                'avg_story_duration': 3.0,
                'font_scale': 1.1,
                'style_override': style,
                'transitions': True
            },
            'youtube': {
                'aspect_ratio': '16:9',
                'width': 1920,
                'height': 1080,
                'max_duration': 600,
                'avg_story_duration': 5.0,
                'font_scale': 1.0,
                'style_override': style,
                'transitions': False
            },
            'twitter': {
                'aspect_ratio': '16:9',
                'width': 1280,
                'height': 720,
                'max_duration': 140,
                'avg_story_duration': 3.5,
                'font_scale': 0.9,
                'style_override': 'casual',
                'transitions': False
            },
            'general': {
                'aspect_ratio': '16:9',
                'width': 1920,
                'height': 1080,
                'max_duration': 300,
                'avg_story_duration': 4.0,
                'font_scale': 1.0,
                'style_override': style,
                'transitions': False
            }
        }
        
        # Get platform config
        config = platform_configs.get(platform, platform_configs['general'])
        
        # Apply platform limits
        duration_seconds = min(duration_seconds, config['max_duration'])
        style = config['style_override']
        
        print(f"""
📄 CSV NEWS AGGREGATOR
=====================
📊 Input: {csv_path}
📱 Platform: {platform.upper()} ({config['aspect_ratio']})
⏱️  Duration: {duration_seconds} seconds
🌐 Language: {language}
🎨 Style: {style}
""")
        
        # Read and parse CSV
        articles = self._parse_csv(csv_path)
        if not articles:
            raise ValueError("No valid articles found in CSV")
        
        print(f"\n✅ Found {len(articles)} articles in CSV")
        
        # Process articles - download media, prepare content
        processed_articles = await self._process_articles(articles)
        
        # Select and order articles
        selected_articles = await self._select_articles(processed_articles, duration_seconds, config)
        
        # Create video
        output_path = await self._create_video(
            selected_articles, 
            duration_seconds, 
            language,
            style,
            config,
            output_filename
        )
        
        return output_path
    
    def _parse_csv(self, csv_path: str) -> List[Dict]:
        """Parse CSV file with flexible format support"""
        
        articles = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            
            # Detect delimiter
            delimiter = ','
            if '\t' in sample:
                delimiter = '\t'
            elif ';' in sample:
                delimiter = ';'
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                # Support multiple column naming conventions
                article = {}
                
                # Title (required)
                title = (row.get('title') or row.get('Title') or 
                        row.get('headline') or row.get('Headline') or
                        row.get('כותרת') or row.get('subject'))
                
                if not title:
                    continue
                
                article['title'] = title.strip()
                
                # Content/Description
                article['content'] = (row.get('content') or row.get('Content') or
                                    row.get('description') or row.get('Description') or
                                    row.get('summary') or row.get('Summary') or
                                    row.get('text') or row.get('תוכן') or
                                    row.get('body') or '')
                
                # URL (optional)
                article['url'] = (row.get('url') or row.get('URL') or 
                                row.get('link') or row.get('Link') or
                                row.get('source_url') or '')
                
                # Source name
                article['source'] = (row.get('source') or row.get('Source') or
                                   row.get('website') or row.get('Website') or
                                   row.get('מקור') or 'Unknown')
                
                # Media URLs (optional)
                article['image_url'] = (row.get('image') or row.get('Image') or
                                      row.get('image_url') or row.get('photo') or
                                      row.get('תמונה') or '')
                
                article['video_url'] = (row.get('video') or row.get('Video') or
                                      row.get('video_url') or row.get('וידאו') or '')
                
                # Category
                article['category'] = (row.get('category') or row.get('Category') or
                                     row.get('type') or row.get('קטגוריה') or 'general')
                
                # Date (optional)
                article['date'] = (row.get('date') or row.get('Date') or
                                 row.get('published') or row.get('תאריך') or '')
                
                # Author (optional)
                article['author'] = (row.get('author') or row.get('Author') or
                                   row.get('writer') or row.get('כותב') or '')
                
                # Priority/Importance (optional)
                priority = (row.get('priority') or row.get('Priority') or
                          row.get('importance') or row.get('חשיבות') or '5')
                try:
                    article['priority'] = int(priority)
                except:
                    article['priority'] = 5
                
                # Language (optional)
                article['language'] = (row.get('language') or row.get('Language') or
                                     row.get('lang') or row.get('שפה') or 'auto')
                
                # Real summary (for news with humor)
                article['real_summary'] = row.get('real_summary') or row.get('תקציר_אמיתי') or ''
                
                articles.append(article)
        
        return articles
    
    async def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles - download media, scrape if URL provided"""
        
        processed = []
        
        # Create SSL context with certificate verification
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            for i, article in enumerate(articles):
                print(f"\n📰 Processing {i+1}/{len(articles)}: {article['title'][:50]}...")
                
                # If URL provided and no content, try to scrape
                if article.get('url') and not article.get('content'):
                    await self._scrape_article_content(article, session)
                
                # Download media
                if article.get('image_url'):
                    await self._download_media(article, 'image_url', session, i)
                
                if article.get('video_url'):
                    await self._download_media(article, 'video_url', session, i)
                
                # If no media but URL provided, try to find media
                if article.get('url') and not (article.get('local_image') or article.get('local_video')):
                    await self._find_media_from_url(article, session, i)
                
                processed.append(article)
        
        return processed
    
    async def _scrape_article_content(self, article: Dict, session: aiohttp.ClientSession):
        """Try to scrape content from URL"""
        try:
            # Try to identify the domain and use appropriate scraper
            domain = urlparse(article['url']).netloc
            
            # Add basic scraper config for unknown sites
            site_id = f"dynamic_{domain.replace('.', '_')}"
            
            if site_id not in self.scraper.configs:
                self.scraper.add_website_config(site_id, {
                    'name': domain,
                    'base_url': f"https://{domain}",
                    'selectors': {
                        'article_container': 'article, main, .content, .post',
                        'title': 'h1, h2, .title',
                        'description': 'p, .description, .summary',
                        'author': '.author, .byline',
                        'date': 'time, .date'
                    },
                    'media_extraction': {
                        'image_selector': 'img',
                        'video_selector': 'video, iframe[src*="youtube"]'
                    }
                })
            
            # Scrape the specific URL
            result = await self.scraper._scrape_url(article['url'], site_id)
            
            if result:
                article['content'] = result.get('description', '') or result.get('content', '')
                if result.get('media_url'):
                    article['image_url'] = result['media_url']
        except:
            pass  # Keep original data if scraping fails
    
    async def _download_media(self, article: Dict, media_key: str, 
                            session: aiohttp.ClientSession, index: int):
        """Download media file"""
        url = article.get(media_key)
        if not url:
            return
        
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    ext = url.split('.')[-1].lower()[:4]
                    if ext not in ['jpg', 'jpeg', 'png', 'mp4', 'webm', 'gif']:
                        ext = 'jpg' if 'image' in media_key else 'mp4'
                    
                    filename = f"csv_news_media/{index}_{media_key}.{ext}"
                    with open(filename, 'wb') as f:
                        f.write(await resp.read())
                    
                    if 'image' in media_key:
                        article['local_image'] = filename
                    else:
                        article['local_video'] = filename
                    
                    print(f"   ✅ Downloaded {media_key}")
        except Exception as e:
            print(f"   ⚠️  Failed to download {media_key}: {e}")
    
    async def _find_media_from_url(self, article: Dict, session: aiohttp.ClientSession, index: int):
        """Try to find media from article URL"""
        if not article.get('url'):
            return
        
        try:
            # Identify the site from URL
            domain = urlparse(article['url']).netloc
            
            # Map domains to scraper configs
            site_mapping = {
                'www.ynet.co.il': 'ynet',
                'ynet.co.il': 'ynet',
                'rotter.net': 'rotter',
                'www.maariv.co.il': 'maariv',
                'maariv.co.il': 'maariv',
                'www.calcalist.co.il': 'calcalist',
                'calcalist.co.il': 'calcalist',
                'www.geektime.co.il': 'geektime',
                'geektime.co.il': 'geektime'
            }
            
            site_id = site_mapping.get(domain)
            
            if not site_id:
                # Try dynamic scraper for unknown sites
                site_id = f"dynamic_{domain.replace('.', '_')}"
                
                if site_id not in self.scraper.configs:
                    self.scraper.add_website_config(site_id, {
                        'name': domain,
                        'base_url': f"https://{domain}",
                        'selectors': {
                            'article_container': 'article, main, .content',
                            'title': 'h1',
                            'description': 'p',
                        },
                        'media_extraction': {
                            'image_selector': 'img[src], picture img',
                            'video_selector': 'video, iframe'
                        }
                    })
            
            # Scrape the URL
            result = await self.scraper._scrape_url(article['url'], site_id)
            
            if result and result.get('media_url'):
                article['image_url'] = result['media_url']
                await self._download_media(article, 'image_url', session, index)
                print(f"   ✅ Scraped image from {domain}")
            else:
                print(f"   ⚠️  No image found at {domain}")
        except Exception as e:
            print(f"   ⚠️  Failed to scrape from URL: {e}")
    
    async def _select_articles(self, articles: List[Dict], duration: int, config: Dict) -> List[Dict]:
        """Select and order articles based on importance and platform"""
        
        # Sort by priority
        articles.sort(key=lambda x: x.get('priority', 5), reverse=True)
        
        # Calculate how many articles we can fit
        # Platform-specific overhead
        overhead = 2 if config['aspect_ratio'] == '9:16' else 3  # Shorter intro/outro for mobile
        available_time = duration - overhead
        
        # Platform-specific pacing
        avg_duration_per_story = config['avg_story_duration']
        max_stories = min(len(articles), int(available_time / avg_duration_per_story))
        
        selected = articles[:max_stories]
        
        # Allocate durations based on platform
        if len(selected) > 0:
            base_duration = available_time / len(selected)
            for i, article in enumerate(selected):
                if config['aspect_ratio'] == '9:16':  # Mobile platforms
                    # Faster, more uniform pacing
                    article['duration'] = min(base_duration, avg_duration_per_story)
                else:  # Desktop platforms
                    if i == 0:  # First story gets slightly more time
                        article['duration'] = min(base_duration * 1.2, avg_duration_per_story * 1.5)
                    elif article.get('priority', 5) >= 9:  # High priority stories
                        article['duration'] = min(base_duration * 1.1, avg_duration_per_story * 1.3)
                    else:
                        article['duration'] = min(base_duration, avg_duration_per_story)
        
        return selected
    
    async def _create_video(self, articles: List[Dict], duration: int, 
                          language: str, style: str, config: Dict, output_filename: Optional[str]) -> str:
        """Create the final video"""
        
        segments = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create intro
        intro_path = self._create_intro(language, style, config)
        segments.append(intro_path)
        print(f"Created intro: {intro_path}")
        
        # Create article segments
        for i, article in enumerate(articles):
            segment_path = self._create_article_segment(article, i, len(articles), language, style, config)
            segments.append(segment_path)
            print(f"Created segment {i+1}: {segment_path} (duration: {article.get('duration', 0):.1f}s)")
        
        # Create outro
        outro_path = self._create_outro(len(articles), language, config)
        segments.append(outro_path)
        print(f"Created outro: {outro_path}")
        
        # Compile video
        if output_filename:
            output_path = output_filename
        else:
            output_path = f"csv_news_output/csv_news_{language}_{timestamp}.mp4"
        
        self._compile_video(segments, output_path)
        
        # Cleanup
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        # Create report
        report_path = output_path.replace('.mp4', '_report.json')
        self._create_report(articles, output_path, report_path)
        
        print(f"""
✅ CSV NEWS VIDEO COMPLETE!
=========================
📹 Video: {output_path}
📄 Report: {report_path}
⏱️  Duration: {duration} seconds
📰 Stories: {len(articles)}

📊 Sources included:
""")
        
        sources = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        for source, count in sources.items():
            print(f"   • {source}: {count} stories")
        
        return output_path
    
    def _create_intro(self, language: str, style: str, config: Dict) -> str:
        """Create intro segment"""
        width = config['width']
        height = config['height']
        img = Image.new('RGB', (width, height), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype(self.font_path, 80)
            font_medium = ImageFont.truetype(self.font_path, 50)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Title based on language
        if language == 'he':
            title = "מהדורת חדשות"
            subtitle = "מקורות מותאמים אישית"
        else:
            title = "NEWS EDITION"
            subtitle = "Custom Sources"
        
        # Center text based on dimensions
        center_x = width // 2
        center_y = height // 2
        
        if config['aspect_ratio'] == '9:16':  # Mobile
            draw.text((center_x, center_y - 100), title, fill=(255, 255, 255), 
                     font=font_large, anchor="ma")
            draw.text((center_x, center_y + 50), subtitle, fill=(200, 200, 200), 
                     font=font_medium, anchor="ma")
        else:  # Desktop
            draw.text((center_x, center_y - 150), title, fill=(255, 255, 255), 
                     font=font_large, anchor="ma")
            draw.text((center_x, center_y), subtitle, fill=(200, 200, 200), 
                     font=font_medium, anchor="ma")
        
        intro_path = "csv_news_output/intro.jpg"
        img.save(intro_path)
        
        intro_video = "csv_news_output/intro.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', intro_path,
            '-t', '2', '-vf', 'fade=t=in:d=0.5',
            '-c:v', 'libx264', '-preset', 'fast', intro_video
        ], capture_output=True)
        
        os.remove(intro_path)
        return intro_video
    
    def _create_article_segment(self, article: Dict, index: int, total: int, 
                              language: str, style: str, config: Dict) -> str:
        """Create segment for an article"""
        
        # If we have media, use it
        if article.get('local_image') or article.get('local_video'):
            media_path = article.get('local_video') or article.get('local_image')
            
            # Create overlay with proper parameters
            overlay_text = f"{index+1}/{total} - {article['source']}"
            
            # Create custom overlay with platform dimensions
            width = config['width']
            height = config['height']
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            try:
                # Scale fonts based on platform
                scale = config['font_scale']
                font_large = ImageFont.truetype(self.font_path, int(65 * scale))
                font_medium = ImageFont.truetype(self.font_path, int(45 * scale))
                font_small = ImageFont.truetype(self.font_path, int(35 * scale))
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Improved dark overlay for better text readability
            overlay_height = int(height * 0.46)  # Proportional to screen height
            gradient = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 0))
            
            # Create a stronger gradient for better text contrast
            for y in range(overlay_height):
                # Non-linear gradient for smoother transition
                progress = y / overlay_height
                alpha = int(255 * (progress ** 0.7) * 0.95)  # Stronger opacity
                for x in range(width):
                    gradient.putpixel((x, y), (0, 0, 0, alpha))
            
            overlay.paste(gradient, (0, height - overlay_height))
            
            # Add subtle dark overlay at top for header readability
            top_height = int(150 * config['font_scale'])
            top_overlay = Image.new('RGBA', (width, top_height), (0, 0, 0, 120))
            overlay.paste(top_overlay, (0, 0), top_overlay)
            
            # Source badge
            source_color = self._get_source_color(article.get('source', 'Unknown'))
            draw.rectangle([(50, 50), (350, 120)], fill=source_color + (255,))
            draw.text((200, 85), article['source'], fill=(255, 255, 255), 
                     font=font_medium, anchor="ma")
            
            # Position counter
            draw.text((width - 50, 85), overlay_text.split(' - ')[0], 
                     fill=(255, 255, 255), font=font_medium, anchor="ra")
            
            # Title with better RTL support and wrapping
            title_y = int(height * 0.65) if config['aspect_ratio'] == '9:16' else int(height * 0.65)
            title_lines = self._wrap_text(article['title'], font_large, width - 220)
            
            for i, line in enumerate(title_lines[:2]):  # Max 2 lines for title
                line_height = int(75 * config['font_scale'])
                if language == 'he':
                    # Right align with proper spacing from edge
                    draw.text((width - 70, title_y + (i * line_height)), line, 
                             fill=(255, 255, 255), font=font_large, anchor="ra")
                else:
                    draw.text((70, title_y + (i * line_height)), line, 
                             fill=(255, 255, 255), font=font_large)
            
            # Humor content with better layout
            if article.get('content'):
                line_height = int(75 * config['font_scale'])
                content_y = title_y + (len(title_lines[:2]) * line_height) + int(30 * config['font_scale'])
                content_lines = self._wrap_text(article['content'], font_medium, width - 220)
                
                for i, line in enumerate(content_lines[:2]):
                    content_line_height = int(55 * config['font_scale'])
                    if language == 'he':
                        draw.text((width - 70, content_y + (i * content_line_height)), line, 
                                 fill=(255, 200, 100), font=font_medium, anchor="ra")
                    else:
                        draw.text((70, content_y + (i * content_line_height)), line, 
                                 fill=(255, 200, 100), font=font_medium)
            
            # Real summary with better positioning
            if article.get('real_summary'):
                # Add separator line
                separator_y = content_y + int(120 * config['font_scale'])
                draw.line([(200, separator_y), (width - 200, separator_y)], fill=(100, 100, 100), width=2)
                
                summary_y = separator_y + 20
                summary_lines = self._wrap_text(article['real_summary'], font_small, width - 220)
                
                for i, line in enumerate(summary_lines[:2]):
                    summary_line_height = int(45 * config['font_scale'])
                    if language == 'he':
                        draw.text((width - 70, summary_y + (i * summary_line_height)), line, 
                                 fill=(200, 200, 200), font=font_small, anchor="ra")
                    else:
                        draw.text((70, summary_y + (i * summary_line_height)), line, 
                                 fill=(200, 200, 200), font=font_small)
            
            overlay_path = f"csv_news_output/overlay_{index}.png"
            overlay.save(overlay_path)
            
            # Apply overlay
            segment_path = f"csv_news_output/segment_{index}.mp4"
            
            if article.get('local_video'):
                # Video with overlay
                result = subprocess.run([
                    'ffmpeg', '-y',
                    '-i', media_path,
                    '-i', overlay_path,
                    '-filter_complex', '[0:v][1:v]overlay=0:0',
                    '-t', str(article['duration']),
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    segment_path
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"  ERROR creating video segment: {result.stderr}")
            else:
                # Image with overlay
                # First create a video from the image
                temp_video = f"csv_news_output/temp_{index}.mp4"
                
                # Check if it's a GIF
                if media_path.lower().endswith('.gif'):
                    # GIFs need different handling
                    result = subprocess.run([
                        'ffmpeg', '-y',
                        '-i', media_path,
                        '-t', str(article['duration']),
                        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                        '-c:v', 'libx264',
                        '-preset', 'fast',
                        temp_video
                    ], capture_output=True, text=True)
                else:
                    # Regular images
                    result = subprocess.run([
                        'ffmpeg', '-y',
                        '-loop', '1',
                        '-i', media_path,
                        '-t', str(article['duration']),
                        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                        '-c:v', 'libx264',
                        '-preset', 'fast',
                        temp_video
                    ], capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(temp_video):
                    # Then overlay the text
                    result = subprocess.run([
                        'ffmpeg', '-y',
                        '-i', temp_video,
                        '-i', overlay_path,
                        '-filter_complex', '[0:v][1:v]overlay=0:0',
                        '-c:v', 'libx264',
                        '-preset', 'fast',
                        segment_path
                    ], capture_output=True, text=True)
                    
                    os.remove(temp_video)
                
                if result.returncode != 0:
                    print(f"  ERROR creating image segment: {result.stderr}")
            
            if os.path.exists(segment_path):
                os.remove(overlay_path)
        else:
            # Text-only segment
            segment_path = self._create_text_segment(article, index, total, language, config)
        
        return segment_path
    
    def _create_text_segment(self, article: Dict, index: int, total: int, language: str, config: Dict) -> str:
        """Create text-only segment"""
        width = config['width']
        height = config['height']
        img = Image.new('RGB', (width, height), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        try:
            scale = config['font_scale']
            font_large = ImageFont.truetype(self.font_path, int(60 * scale))
            font_medium = ImageFont.truetype(self.font_path, int(45 * scale))
            font_small = ImageFont.truetype(self.font_path, int(35 * scale))
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Header with source
        source_color = self._get_source_color(article.get('source', 'Unknown'))
        header_height = int(120 * config['font_scale'])
        draw.rectangle([(0, 0), (width, header_height)], fill=source_color)
        draw.text((50, header_height // 2), article.get('source', 'Unknown'), 
                 fill=(255, 255, 255), font=font_medium, anchor="lm")
        draw.text((width - 50, header_height // 2), f"{index+1}/{total}", 
                 fill=(255, 255, 255), font=font_medium, anchor="ra")
        
        # Category badge
        if article.get('category'):
            badge_y = header_height + 30
            badge_height = int(70 * config['font_scale'])
            draw.rectangle([(50, badge_y), (350, badge_y + badge_height)], fill=(100, 100, 100))
            draw.text((200, badge_y + badge_height // 2), article['category'].upper(), 
                     fill=(255, 255, 255), font=font_small, anchor="ma")
        
        # Title
        title_lines = self._wrap_text(article['title'], font_large, width - 220)
        y_pos = int(350 * config['font_scale'])
        for line in title_lines[:2]:
            if language == 'he':
                draw.text((width - 50, y_pos), line, fill=(255, 255, 255), 
                         font=font_large, anchor="ra")
            else:
                draw.text((50, y_pos), line, fill=(255, 255, 255), font=font_large)
            y_pos += int(80 * config['font_scale'])
        
        # Content preview (humor)
        if article.get('content'):
            content_lines = self._wrap_text(article['content'], font_medium, width - 220)
            y_pos = int(550 * config['font_scale'])
            for line in content_lines[:2]:
                if language == 'he':
                    draw.text((width - 50, y_pos), line, fill=(255, 200, 100), 
                             font=font_medium, anchor="ra")
                else:
                    draw.text((50, y_pos), line, fill=(255, 200, 100), font=font_medium)
                y_pos += int(60 * config['font_scale'])
        
        # Real summary (if available)
        if article.get('real_summary'):
            # Add separator
            y_pos += 20
            draw.line([(100, y_pos), (width - 100, y_pos)], fill=(100, 100, 100), width=2)
            y_pos += 30
            
            summary_lines = self._wrap_text(article['real_summary'], font_small, width - 220)
            for line in summary_lines[:2]:
                if language == 'he':
                    draw.text((width - 50, y_pos), line, fill=(180, 180, 180), 
                             font=font_small, anchor="ra")
                else:
                    draw.text((50, y_pos), line, fill=(180, 180, 180), font=font_small)
                y_pos += int(50 * config['font_scale'])
        
        # Author and date
        bottom_y = height - int(180 * config['font_scale'])
        if article.get('author'):
            draw.text((50, bottom_y), f"By: {article['author']}", 
                     fill=(150, 150, 150), font=font_small)
        
        if article.get('date'):
            draw.text((width - 50, bottom_y), article['date'], 
                     fill=(150, 150, 150), font=font_small, anchor="ra")
        
        img_path = f"csv_news_output/text_segment_{index}.jpg"
        img.save(img_path)
        
        segment_path = f"csv_news_output/segment_{index}.mp4"
        result = subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', img_path,
            '-t', str(article['duration']), '-vf', f'scale={width}:{height}',
            '-c:v', 'libx264', '-preset', 'fast', segment_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ERROR creating text segment: {result.stderr}")
        elif os.path.exists(segment_path):
            os.remove(img_path)
        
        return segment_path
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _get_source_color(self, source: str) -> tuple:
        """Get color for source"""
        source_lower = source.lower()
        
        if 'ynet' in source_lower:
            return (0, 150, 255)
        elif 'rotter' in source_lower:
            return (255, 0, 0)
        elif 'bbc' in source_lower:
            return (200, 0, 200)
        elif 'cnn' in source_lower:
            return (200, 0, 0)
        else:
            return (100, 100, 100)
    
    def _create_outro(self, story_count: int, language: str, config: Dict) -> str:
        """Create outro segment"""
        width = config['width']
        height = config['height']
        img = Image.new('RGB', (width, height), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        try:
            scale = config['font_scale']
            font_large = ImageFont.truetype(self.font_path, int(70 * scale))
            font_medium = ImageFont.truetype(self.font_path, int(50 * scale))
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        center_x = width // 2
        center_y = height // 2
        
        if language == 'he':
            draw.text((center_x, center_y - 100), "סוף המהדורה", fill=(255, 255, 255), 
                     font=font_large, anchor="ma")
            draw.text((center_x, center_y + 50), f"סוכמו {story_count} כתבות", 
                     fill=(200, 200, 200), font=font_medium, anchor="ma")
        else:
            draw.text((center_x, center_y - 100), "End of Edition", fill=(255, 255, 255), 
                     font=font_large, anchor="ma")
            draw.text((center_x, center_y + 50), f"{story_count} Stories Covered", 
                     fill=(200, 200, 200), font=font_medium, anchor="ma")
        
        outro_path = "csv_news_output/outro.jpg"
        img.save(outro_path)
        
        outro_video = "csv_news_output/outro.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', outro_path,
            '-t', '2', '-vf', 'fade=t=out:st=1.5:d=0.5',
            '-c:v', 'libx264', '-preset', 'fast', outro_video
        ], capture_output=True)
        
        os.remove(outro_path)
        return outro_video
    
    def _compile_video(self, segments: List[str], output_path: str):
        """Compile all segments into final video"""
        concat_file = "csv_news_output/concat.txt"
        
        print(f"\nCompiling {len(segments)} segments into final video...")
        
        with open(concat_file, 'w') as f:
            for segment in segments:
                if os.path.exists(segment):
                    f.write(f"file '{os.path.abspath(segment)}'\n")
                    print(f"  Added: {segment}")
                else:
                    print(f"  WARNING: Missing segment: {segment}")
        
        result = subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file, '-c:v', 'libx264',
            '-preset', 'medium', '-crf', '23', output_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
        
        os.remove(concat_file)
    
    def _create_report(self, articles: List[Dict], video_path: str, report_path: str):
        """Create JSON report of the news edition"""
        report = {
            'video_path': os.path.abspath(video_path),
            'created': datetime.now().isoformat(),
            'article_count': len(articles),
            'articles': []
        }
        
        for article in articles:
            report['articles'].append({
                'title': article['title'],
                'source': article.get('source', 'Unknown'),
                'category': article.get('category', 'general'),
                'duration': article.get('duration', 0),
                'has_image': bool(article.get('local_image')),
                'has_video': bool(article.get('local_video')),
                'priority': article.get('priority', 5)
            })
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)


def create_sample_csv(output_path: str = "sample_news.csv"):
    """Create a sample CSV file with news articles"""
    
    sample_data = [
        {
            'title': 'רעידת אדמה בעוצמה 5.2 הורגשה בצפון הארץ',
            'content': 'רעידת אדמה בעוצמה 5.2 הורגשה הבוקר בצפון הארץ. המוקד היה באזור הכנרת. אין דיווחים על נפגעים או נזקים.',
            'source': 'חדשות 12',
            'category': 'חדשות',
            'priority': '9',
            'url': 'https://www.example.com/earthquake',
            'image_url': 'https://picsum.photos/1920/1080?random=1',
            'date': '2025-01-15',
            'author': 'כתב החדשות'
        },
        {
            'title': 'הממשלה אישרה תוכנית כלכלית חדשה',
            'content': 'הממשלה אישרה היום תוכנית כלכלית חדשה בהיקף של 50 מיליארד שקל. התוכנית כוללת הטבות מס והשקעות בתשתיות.',
            'source': 'כלכליסט',
            'category': 'כלכלה',
            'priority': '7',
            'url': 'https://www.example.com/economy',
            'image_url': 'https://picsum.photos/1920/1080?random=2'
        },
        {
            'title': 'Breaking: Major Tech Company Announces Layoffs',
            'content': 'A major technology company announced today that it will lay off 10,000 employees globally as part of restructuring efforts.',
            'source': 'TechCrunch',
            'category': 'tech',
            'priority': '8',
            'url': 'https://techcrunch.com/layoffs',
            'image_url': 'https://picsum.photos/1920/1080?random=3',
            'language': 'en'
        },
        {
            'title': 'מכבי תל אביב ניצחה 3-1 את הפועל',
            'content': 'מכבי תל אביב ניצחה הערב 3-1 את הפועל תל אביב בדרבי הגדול. השחקן הבולט היה אייל גולסה עם שני שערים.',
            'source': 'ספורט 5',
            'category': 'ספורט',
            'priority': '6',
            'video_url': 'https://www.example.com/derby.mp4'
        },
        {
            'title': 'מזג האוויר: גשם כבד צפוי בסוף השבוע',
            'content': 'על פי תחזית מזג האוויר, גשם כבד צפוי להגיע בסוף השבוע. הטמפרטורות צפויות לרדת משמעותית.',
            'source': 'השירות המטאורולוגי',
            'category': 'מזג אוויר',
            'priority': '5'
        }
    ]
    
    # Write CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['title', 'content', 'source', 'category', 'priority', 
                     'url', 'image_url', 'video_url', 'date', 'author', 'language']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in sample_data:
            writer.writerow(row)
    
    print(f"""
✅ Sample CSV created: {output_path}

📋 CSV Format:
- title: Article headline (required)
- content: Article text/summary
- source: Source name/website
- category: Category (news, sports, tech, etc.)
- priority: 1-10 (10 = most important)
- url: Article URL (optional - will scrape if no content)
- image_url: Direct image URL
- video_url: Direct video URL
- date: Publication date
- author: Author name
- language: Language code (he, en, etc.)

You can use any combination of these columns!
""")


async def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
Usage: python csv_news_aggregator.py <csv_file> [options]

Options:
  --duration SECONDS  Video duration (default: 60)
  --language LANG     Language code (default: he)
  --style STYLE       Visual style (default: professional)
  --output FILE       Output filename

Examples:
  python csv_news_aggregator.py news.csv
  python csv_news_aggregator.py news.csv --duration 30 --language en
  python csv_news_aggregator.py news.csv --output my_news.mp4

To create a sample CSV:
  python csv_news_aggregator.py --create-sample
""")
        return
    
    if sys.argv[1] == '--create-sample':
        create_sample_csv()
        return
    
    # Parse arguments
    csv_file = sys.argv[1]
    duration = 60
    language = 'he'
    style = 'professional'
    output = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--duration' and i + 1 < len(sys.argv):
            duration = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--language' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--style' and i + 1 < len(sys.argv):
            style = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Create aggregator and process
    aggregator = CSVNewsAggregator()
    video_path = await aggregator.create_news_from_csv(
        csv_file,
        duration_seconds=duration,
        language=language,
        style=style,
        output_filename=output
    )
    
    print(f"\n✅ Video created: {video_path}")


if __name__ == "__main__":
    asyncio.run(main())