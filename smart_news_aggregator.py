#!/usr/bin/env python3
"""
Smart News Aggregator - Mixed media with intelligent durations
Scrapes both images AND videos from news sites
"""

import os
import subprocess
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import asyncio
import aiohttp
import json
import re
from src.news_aggregator.duration_manager import DurationManager
from src.news_aggregator.overlays.template_selector import get_overlay_for_content
from src.news_aggregator.overlays.enhanced_overlay import apply_text_to_frame


class SmartNewsAggregator:
    """Smart news aggregator with mixed media support"""
    
    def __init__(self, language='en', duration_preset='default'):
        self.language = language
        self.duration_manager = DurationManager()
        self.duration_preset = duration_preset
        os.makedirs("smart_news_media", exist_ok=True)
    
    async def scrape_mixed_media(self, sources: List[str], max_items: int = 20):
        """Scrape both images and videos from news sources"""
        print("🔍 Scraping mixed media from news sources...")
        
        scraped = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            # Example: Scrape from multiple sources
            if 'sport' in ' '.join(sources).lower():
                # Sports videos from Reddit
                print("\n⚽ Looking for sports videos...")
                try:
                    # Reddit sports videos
                    async with session.get('https://www.reddit.com/r/sports/top.json?limit=10',
                                         headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            for post in data['data']['children']:
                                post_data = post['data']
                                
                                # Check for video
                                if post_data.get('is_video'):
                                    video_url = post_data.get('media', {}).get('reddit_video', {}).get('fallback_url')
                                    if video_url:
                                        scraped.append({
                                            'url': video_url,
                                            'title': post_data.get('title', '')[:100],
                                            'source': 'Reddit Sports',
                                            'type': 'video',
                                            'duration': post_data.get('media', {}).get('reddit_video', {}).get('duration', 10),
                                            'category': 'sports',
                                            'upvotes': post_data.get('ups', 0)
                                        })
                                
                                # Also check for images
                                elif post_data.get('url', '').endswith(('.jpg', '.png', '.gif')):
                                    scraped.append({
                                        'url': post_data.get('url'),
                                        'title': post_data.get('title', '')[:100],
                                        'source': 'Reddit Sports',
                                        'type': 'image',
                                        'category': 'sports',
                                        'upvotes': post_data.get('ups', 0)
                                    })
                    
                    print(f"  ✅ Found {len([s for s in scraped if s['source'] == 'Reddit Sports'])} items")
                except Exception as e:
                    print(f"  ❌ Reddit error: {e}")
            
            # Add more sources based on input
            if 'news' in ' '.join(sources).lower():
                # Add general news sources
                scraped.extend(await self.scrape_news_sites(session))
            
            if 'tech' in ' '.join(sources).lower():
                # Add tech news
                scraped.extend(await self.scrape_tech_news(session))
        
        # Sort by relevance (upvotes, views, etc.)
        scraped.sort(key=lambda x: x.get('upvotes', 0), reverse=True)
        
        return scraped[:max_items]
    
    async def scrape_news_sites(self, session):
        """Scrape general news sites"""
        news_items = []
        
        # CNN example
        try:
            async with session.get('https://www.cnn.com', 
                                 headers={'User-Agent': 'Mozilla/5.0'}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for video elements
                    videos = soup.find_all('video', limit=3)
                    for video in videos:
                        source = video.find('source')
                        if source and source.get('src'):
                            news_items.append({
                                'url': source['src'],
                                'title': video.get('title', 'CNN Video News'),
                                'source': 'CNN',
                                'type': 'video',
                                'category': 'news'
                            })
                    
                    # Look for images
                    images = soup.find_all('img', src=True, limit=5)
                    for img in images[:5]:
                        if 'logo' not in img.get('src', '').lower():
                            news_items.append({
                                'url': img['src'],
                                'title': img.get('alt', 'CNN News')[:100],
                                'source': 'CNN',
                                'type': 'image',
                                'category': 'news'
                            })
        except Exception as e:
            print(f"  ❌ CNN scraping error: {e}")
        
        return news_items
    
    async def scrape_tech_news(self, session):
        """Scrape tech news with videos"""
        tech_items = []
        
        # Example: Tech news sites often have video content
        tech_items.extend([
            {
                'title': 'New iPhone 16 Features Revealed',
                'source': 'TechCrunch',
                'type': 'video',
                'category': 'tech',
                'url': 'https://example.com/video1.mp4',
                'duration': 8
            },
            {
                'title': 'AI Revolution: GPT-5 Announced',
                'source': 'The Verge',
                'type': 'image',
                'category': 'tech',
                'url': 'https://via.placeholder.com/1920x1080/0033CC/FFFFFF?text=AI+News'
            }
        ])
        
        return tech_items
    
    async def download_media_item(self, session, item, index):
        """Download a single media item"""
        try:
            ext = 'mp4' if item['type'] == 'video' else 'jpg'
            filename = f"smart_news_media/{item['source'].replace(' ', '_')}_{index}.{ext}"
            
            print(f"  📥 Downloading {item['type']}: {item['title'][:40]}...")
            
            # For demo, create placeholder if URL is not real
            if 'placeholder' in item['url'] or 'example.com' in item['url']:
                if item['type'] == 'image':
                    # Create placeholder image
                    img = Image.new('RGB', (1920, 1080), color=(0, 50, 150))
                    draw = ImageDraw.Draw(img)
                    
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
                    except:
                        font = ImageFont.load_default()
                    
                    draw.text((960, 540), item['title'][:50], 
                             fill=(255, 255, 255), font=font, anchor="mm")
                    
                    img.save(filename, 'JPEG')
                else:
                    # Create placeholder video
                    color = '0x0033CC' if item['category'] == 'tech' else '0xCC0000'
                    cmd = [
                        'ffmpeg', '-y',
                        '-f', 'lavfi',
                        '-i', f'color=c={color}:size=1920x1080:duration=5',
                        '-vf', f'drawtext=text=\'{item["title"][:40]}\':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
                        '-c:v', 'libx264',
                        '-preset', 'ultrafast',
                        '-t', str(item.get('duration', 5)),
                        filename
                    ]
                    subprocess.run(cmd, capture_output=True)
            else:
                # Download real media
                async with session.get(item['url'], timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(filename, 'wb') as f:
                            f.write(content)
            
            item['local_path'] = filename
            
            # Get video duration if not provided
            if item['type'] == 'video' and 'duration' not in item:
                probe_cmd = [
                    'ffprobe', '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'json', filename
                ]
                result = subprocess.run(probe_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    item['duration'] = float(data.get('format', {}).get('duration', 5))
            
            print(f"  ✅ Downloaded: {filename}")
            return item
            
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            return None
    
    def process_media_item(self, item, overlay_path, output_path):
        """Process a single media item with appropriate duration"""
        
        # Get optimal duration from duration manager
        duration = self.duration_manager.get_duration(item)
        
        print(f"  🎬 Processing: {item['title'][:40]}... ({duration}s)")
        
        if item['type'] == 'image':
            # Process image with Ken Burns effect
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', item['local_path'],
                '-i', overlay_path,
                '-filter_complex',
                f'[0:v]scale=2400:1350,zoompan=z=\'min(zoom+0.0015,1.5)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={duration*25}:s=1920x1080:fps=25[zoomed];'
                '[zoomed][1:v]overlay=0:0',
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
        else:
            # Process video - trim to optimal duration
            video_duration = item.get('duration', duration)
            use_duration = min(duration, video_duration)
            
            cmd = [
                'ffmpeg', '-y',
                '-i', item['local_path'],
                '-i', overlay_path,
                '-filter_complex',
                f'[0:v]scale=1920:1080,trim=duration={use_duration},setpts=PTS-STARTPTS[v];'
                '[v][1:v]overlay=0:0',
                '-t', str(use_duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-an',  # Remove audio for now
                output_path
            ]
        
        subprocess.run(cmd, capture_output=True)
        return duration
    
    async def create_smart_compilation(self, sources: List[str], 
                                     total_duration: int = 60,
                                     output_name: Optional[str] = None):
        """Create smart news compilation with mixed media"""
        
        print(f"""
🎬 SMART NEWS AGGREGATOR
=======================
📺 Sources: {', '.join(sources)}
⏱️  Duration: {total_duration} seconds
🎯 Mixed media: Images + Videos
📊 Smart duration calculation
""")
        
        # Scrape mixed media
        scraped_items = await self.scrape_mixed_media(sources)
        print(f"\n📊 Found {len(scraped_items)} media items")
        
        # Download media
        print("\n📥 Downloading media...")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            download_tasks = []
            for i, item in enumerate(scraped_items):
                task = self.download_media_item(session, item, i)
                download_tasks.append(task)
            
            downloaded = await asyncio.gather(*download_tasks)
            downloaded = [item for item in downloaded if item is not None]
        
        print(f"\n✅ Downloaded {len(downloaded)} items")
        
        # Calculate durations for all clips
        print("\n📊 Calculating optimal durations...")
        distributed = self.duration_manager.distribute_durations(
            downloaded, 
            total_duration=total_duration,
            min_clip_duration=2,
            max_clip_duration=10
        )
        
        # Show duration distribution
        print("\n⏱️  Duration Distribution:")
        for i, item in enumerate(distributed):
            print(f"  {i+1}. {item['title'][:40]}... - {item['duration']}s ({item['type']})")
        
        # Select appropriate overlay based on content
        overlay, template_name = get_overlay_for_content(distributed)
        overlay_path = f"smart_overlay_{template_name}.png"
        overlay.save(overlay_path)
        print(f"\n🎨 Selected overlay: {template_name}")
        
        # Process each clip
        print("\n🎬 Creating clips...")
        clips = []
        total_actual_duration = 0
        
        for i, item in enumerate(distributed):
            output = f"smart_clip_{i}.mp4"
            clip_duration = self.process_media_item(item, overlay_path, output)
            clips.append(output)
            total_actual_duration += clip_duration
        
        # Create final compilation
        print("\n🎬 Creating final compilation...")
        with open("smart_concat.txt", "w") as f:
            for clip in clips:
                f.write(f"file '{os.path.abspath(clip)}'\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not output_name:
            output_name = f"smart_news_{template_name}_{timestamp}.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'smart_concat.txt',
            '-c', 'copy',
            output_name
        ]
        
        subprocess.run(cmd, check=True)
        
        # Cleanup
        os.remove(overlay_path)
        os.remove("smart_concat.txt")
        for clip in clips:
            if os.path.exists(clip):
                os.remove(clip)
        
        # Results
        full_path = os.path.abspath(output_name)
        size = os.path.getsize(output_name) / (1024 * 1024)
        
        print(f"""
✅ SMART NEWS COMPILATION COMPLETE!
==================================
📹 Full Path: {full_path}
📏 Size: {size:.2f} MB
⏱️  Duration: {total_actual_duration} seconds
🎬 Clips: {len(clips)}
🎨 Template: {template_name}

📊 MEDIA BREAKDOWN:
""")
        
        # Show media type breakdown
        video_count = sum(1 for item in distributed if item['type'] == 'video')
        image_count = sum(1 for item in distributed if item['type'] == 'image')
        
        print(f"  • Videos: {video_count}")
        print(f"  • Images: {image_count}")
        
        print("\n📰 CONTENT:")
        for i, item in enumerate(distributed[:10]):  # Show first 10
            print(f"  {i+1}. [{item['type'].upper()}] {item['title'][:50]}... ({item['duration']}s)")
        
        if len(distributed) > 10:
            print(f"  ... and {len(distributed) - 10} more")
        
        return full_path


async def main():
    """Demo the smart news aggregator"""
    
    # Example 1: Sports compilation with mixed media
    aggregator = SmartNewsAggregator(language='en')
    
    # Create different types of compilations
    examples = [
        {
            'sources': ['sport', 'soccer', 'nba'],
            'duration': 60,
            'name': 'sports_highlights_60s.mp4'
        },
        {
            'sources': ['tech', 'ai', 'gadgets'],
            'duration': 45,
            'name': 'tech_news_45s.mp4'
        },
        {
            'sources': ['breaking', 'news', 'world'],
            'duration': 90,
            'name': 'breaking_news_90s.mp4'
        }
    ]
    
    print("Choose compilation type:")
    for i, ex in enumerate(examples):
        print(f"{i+1}. {ex['sources']} - {ex['duration']}s")
    
    # For demo, just run the first one
    example = examples[0]
    
    await aggregator.create_smart_compilation(
        sources=example['sources'],
        total_duration=example['duration'],
        output_name=example['name']
    )


if __name__ == "__main__":
    asyncio.run(main())