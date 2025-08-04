"""CSV Parser for News Sources"""

import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ...utils.logging_config import get_logger

logger = get_logger(__name__)


class NewsCSVParser:
    """Parse CSV files containing news sources and articles"""
    
    def __init__(self):
        self.supported_formats = {
            "sources": self._parse_sources_csv,
            "articles": self._parse_articles_csv,
            "media": self._parse_media_csv,
            "events": self._parse_events_csv
        }
    
    def parse_csv_file(self, csv_path: str, format_type: str = "auto") -> List[Dict[str, Any]]:
        """Parse CSV file and return structured data"""
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Auto-detect format type if needed
        if format_type == "auto":
            format_type = self._detect_format(csv_path)
        
        logger.info(f"Parsing CSV file: {csv_path} (format: {format_type})")
        
        # Parse based on format
        parser_func = self.supported_formats.get(format_type)
        if not parser_func:
            raise ValueError(f"Unsupported CSV format: {format_type}")
        
        return parser_func(csv_path)
    
    def _detect_format(self, csv_path: str) -> str:
        """Auto-detect CSV format based on headers"""
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if not headers:
                raise ValueError("CSV file has no headers")
            
            # Check headers to determine format
            headers_lower = [h.lower() for h in headers]
            
            if 'url' in headers_lower and 'source_type' in headers_lower:
                return "sources"
            elif 'title' in headers_lower and 'content' in headers_lower:
                return "articles"
            elif 'media_url' in headers_lower or 'video_url' in headers_lower:
                return "media"
            elif 'event' in headers_lower or 'match' in headers_lower:
                return "events"
            else:
                # Default to articles format
                return "articles"
    
    def _parse_sources_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Parse CSV containing news sources
        
        Expected columns:
        - url: Source URL
        - name: Source name
        - source_type: web, social_media, rss, etc.
        - category: news category (optional)
        - language: Language code (optional)
        - scraping_config: JSON config (optional)
        """
        
        sources = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                source = {
                    "url": row.get('url', '').strip(),
                    "name": row.get('name', '').strip(),
                    "source_type": row.get('source_type', 'web').strip(),
                    "category": row.get('category', 'general').strip(),
                    "language": row.get('language', 'en').strip()
                }
                
                # Parse scraping config if present
                if row.get('scraping_config'):
                    try:
                        source['scraping_config'] = json.loads(row['scraping_config'])
                    except:
                        source['scraping_config'] = {}
                
                if source['url']:
                    sources.append(source)
        
        logger.info(f"Parsed {len(sources)} sources from CSV")
        return sources
    
    def _parse_articles_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Parse CSV containing articles
        
        Expected columns:
        - title: Article title
        - content: Article content
        - url: Article URL (optional)
        - author: Author name (optional)
        - published_date: Publication date (optional)
        - category: Category (optional)
        - tags: Comma-separated tags (optional)
        - media_urls: Comma-separated media URLs (optional)
        - source_name: Source name (optional)
        """
        
        articles = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                article = {
                    "title": row.get('title', '').strip(),
                    "content": row.get('content', '').strip(),
                    "url": row.get('url', '').strip(),
                    "author": row.get('author', '').strip(),
                    "category": row.get('category', 'general').strip(),
                    "source_name": row.get('source_name', 'CSV Import').strip()
                }
                
                # Parse published date
                if row.get('published_date'):
                    try:
                        article['published_date'] = self._parse_date(row['published_date'])
                    except:
                        article['published_date'] = datetime.now()
                else:
                    article['published_date'] = datetime.now()
                
                # Parse tags
                if row.get('tags'):
                    article['tags'] = [tag.strip() for tag in row['tags'].split(',')]
                else:
                    article['tags'] = []
                
                # Parse media URLs
                if row.get('media_urls'):
                    article['media_urls'] = [url.strip() for url in row['media_urls'].split(',')]
                else:
                    article['media_urls'] = []
                
                # Add custom fields
                for key, value in row.items():
                    if key not in article and value:
                        article[f"custom_{key}"] = value
                
                if article['title'] and article['content']:
                    articles.append(article)
        
        logger.info(f"Parsed {len(articles)} articles from CSV")
        return articles
    
    def _parse_media_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Parse CSV containing media assets
        
        Expected columns:
        - media_url: Media URL
        - media_type: image, video, audio
        - title: Media title (optional)
        - description: Media description (optional)
        - duration: Duration in seconds for video/audio (optional)
        - article_id: Related article ID (optional)
        - thumbnail_url: Thumbnail URL for videos (optional)
        """
        
        media_assets = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                media = {
                    "url": row.get('media_url', row.get('url', '')).strip(),
                    "type": row.get('media_type', 'image').strip().lower(),
                    "title": row.get('title', '').strip(),
                    "description": row.get('description', '').strip(),
                    "article_id": row.get('article_id', '').strip()
                }
                
                # Parse duration for video/audio
                if row.get('duration'):
                    try:
                        media['duration'] = float(row['duration'])
                    except:
                        media['duration'] = None
                
                # Add thumbnail URL
                if row.get('thumbnail_url'):
                    media['thumbnail_url'] = row['thumbnail_url'].strip()
                
                if media['url']:
                    media_assets.append(media)
        
        logger.info(f"Parsed {len(media_assets)} media assets from CSV")
        return media_assets
    
    def _parse_events_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Parse CSV containing events (sports, conferences, etc.)
        
        Expected columns:
        - event_name: Event name
        - event_type: sports, conference, concert, etc.
        - date: Event date
        - location: Event location (optional)
        - participants: Comma-separated participants (optional)
        - result: Event result (optional)
        - highlights: Event highlights text (optional)
        - media_urls: Comma-separated media URLs (optional)
        - stats: JSON stats data (optional)
        """
        
        events = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                event = {
                    "name": row.get('event_name', '').strip(),
                    "type": row.get('event_type', 'general').strip(),
                    "location": row.get('location', '').strip(),
                    "result": row.get('result', '').strip(),
                    "highlights": row.get('highlights', '').strip()
                }
                
                # Parse date
                if row.get('date'):
                    try:
                        event['date'] = self._parse_date(row['date'])
                    except:
                        event['date'] = datetime.now()
                else:
                    event['date'] = datetime.now()
                
                # Parse participants
                if row.get('participants'):
                    event['participants'] = [p.strip() for p in row['participants'].split(',')]
                else:
                    event['participants'] = []
                
                # Parse media URLs
                if row.get('media_urls'):
                    event['media_urls'] = [url.strip() for url in row['media_urls'].split(',')]
                else:
                    event['media_urls'] = []
                
                # Parse stats
                if row.get('stats'):
                    try:
                        event['stats'] = json.loads(row['stats'])
                    except:
                        event['stats'] = {}
                
                if event['name']:
                    events.append(event)
        
        logger.info(f"Parsed {len(events)} events from CSV")
        return events
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date from various formats"""
        
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%B %d, %Y",
            "%d %B %Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        # If no format matches, try to parse as timestamp
        try:
            return datetime.fromtimestamp(float(date_str))
        except:
            raise ValueError(f"Unable to parse date: {date_str}")
    
    def create_sample_csv(self, output_dir: str = "samples"):
        """Create sample CSV files for each format"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Sample sources CSV
        sources_csv = os.path.join(output_dir, "sample_sources.csv")
        with open(sources_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'name', 'source_type', 'category', 'language'])
            writer.writerow(['https://www.ynet.co.il', 'Ynet', 'web', 'general', 'he'])
            writer.writerow(['https://www.cnn.com', 'CNN', 'web', 'general', 'en'])
            writer.writerow(['https://reddit.com/r/worldnews', 'Reddit World News', 'social_media', 'general', 'en'])
        
        # Sample articles CSV
        articles_csv = os.path.join(output_dir, "sample_articles.csv")
        with open(articles_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'content', 'url', 'author', 'published_date', 'category', 'tags', 'media_urls'])
            writer.writerow([
                'Breaking News: Major Event Happens',
                'This is the content of the breaking news article...',
                'https://example.com/article1',
                'John Doe',
                datetime.now().strftime('%Y-%m-%d'),
                'general',
                'breaking,news,important',
                'https://example.com/image1.jpg,https://example.com/video1.mp4'
            ])
        
        # Sample media CSV
        media_csv = os.path.join(output_dir, "sample_media.csv")
        with open(media_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['media_url', 'media_type', 'title', 'description', 'duration'])
            writer.writerow([
                'https://example.com/video.mp4',
                'video',
                'News Report Video',
                'Video showing the news event',
                '120'
            ])
        
        # Sample events CSV
        events_csv = os.path.join(output_dir, "sample_events.csv")
        with open(events_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['event_name', 'event_type', 'date', 'location', 'participants', 'result', 'highlights', 'media_urls'])
            writer.writerow([
                'World Cup Final',
                'sports',
                datetime.now().strftime('%Y-%m-%d'),
                'Stadium Name',
                'Team A,Team B',
                'Team A won 2-1',
                'Amazing match with great goals',
                'https://example.com/goal1.mp4,https://example.com/goal2.mp4'
            ])
        
        logger.info(f"Created sample CSV files in {output_dir}")
        return {
            "sources": sources_csv,
            "articles": articles_csv,
            "media": media_csv,
            "events": events_csv
        }