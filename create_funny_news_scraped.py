#!/usr/bin/env python3
"""
Create Funny News Video with Scraped Media
"""

import asyncio
import aiohttp
import os
import subprocess
import json
from datetime import datetime
import random

async def scrape_funny_content():
    """Scrape funny news/fails from Reddit"""
    
    print("🔍 Scraping funny content from Reddit...")
    
    # Reddit API endpoints for funny content
    sources = [
        "https://www.reddit.com/r/funny/top/.json?t=day&limit=20",
        "https://www.reddit.com/r/PublicFreakout/top/.json?t=week&limit=10",
        "https://www.reddit.com/r/ContagiousLaughter/top/.json?t=week&limit=10",
        "https://www.reddit.com/r/AnimalsBeingDerps/top/.json?t=week&limit=10"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; FunnyNewsBot/1.0)'}
    
    all_content = []
    
    async with aiohttp.ClientSession() as session:
        for url in sources:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            
                            # Extract media
                            media_url = None
                            media_type = None
                            
                            # Reddit video
                            if post_data.get('is_video'):
                                reddit_video = post_data.get('media', {}).get('reddit_video', {})
                                if reddit_video.get('fallback_url'):
                                    media_url = reddit_video['fallback_url']
                                    media_type = 'video'
                            
                            # Direct image
                            elif post_data.get('url', '').endswith(('.jpg', '.png', '.gif')):
                                media_url = post_data['url']
                                media_type = 'image'
                            
                            # Preview image
                            elif post_data.get('preview'):
                                images = post_data['preview'].get('images', [])
                                if images:
                                    media_url = images[0]['source']['url'].replace('&amp;', '&')
                                    media_type = 'image'
                            
                            if media_url:
                                all_content.append({
                                    'title': post_data.get('title', ''),
                                    'url': media_url,
                                    'type': media_type,
                                    'score': post_data.get('score', 0),
                                    'subreddit': post_data.get('subreddit', '')
                                })
                                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    
    # Sort by score
    all_content.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"✅ Found {len(all_content)} funny media items")
    return all_content[:10]  # Top 10

async def download_media(content_list, output_dir):
    """Download media files"""
    
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []
    
    async with aiohttp.ClientSession() as session:
        for i, item in enumerate(content_list):
            try:
                print(f"📥 Downloading: {item['title'][:50]}...")
                
                ext = '.mp4' if item['type'] == 'video' else '.jpg'
                filename = f"{output_dir}/media_{i}{ext}"
                
                async with session.get(item['url']) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(filename, 'wb') as f:
                            f.write(content)
                        
                        downloaded.append({
                            'path': filename,
                            'type': item['type'],
                            'title': item['title']
                        })
                        
            except Exception as e:
                print(f"Failed to download: {e}")
    
    print(f"✅ Downloaded {len(downloaded)} media files")
    return downloaded

def create_video_ffmpeg(media_files, duration=20, output_path="funny_news_scraped.mp4"):
    """Create video using FFmpeg with scraped media"""
    
    print("🎬 Creating video with FFmpeg...")
    
    # Calculate time per clip
    time_per_clip = duration / len(media_files)
    
    # Create temp directory
    temp_dir = "temp_clips"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Process each media file
    clips = []
    for i, media in enumerate(media_files):
        output_clip = f"{temp_dir}/clip_{i}.mp4"
        
        if media['type'] == 'video':
            # Trim video
            cmd = [
                'ffmpeg', '-y', '-i', media['path'],
                '-t', str(time_per_clip),
                '-c:v', 'libx264', '-preset', 'fast',
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
                '-r', '30',
                output_clip
            ]
        else:
            # Image to video with zoom effect
            cmd = [
                'ffmpeg', '-y', '-loop', '1', '-i', media['path'],
                '-c:v', 'libx264', '-t', str(time_per_clip),
                '-vf', 'scale=1920*2:1080*2,zoompan=z=\'min(zoom+0.0015,1.5)\':d=125:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=1920x1080',
                '-r', '30', '-pix_fmt', 'yuv420p',
                output_clip
            ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            clips.append(output_clip)
        except:
            print(f"Failed to process {media['path']}")
    
    # Create concat file
    concat_file = f"{temp_dir}/concat.txt"
    with open(concat_file, 'w') as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")
    
    # Concatenate all clips
    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264', '-preset', 'medium',
        '-vf', 'setpts=0.8*PTS',  # Speed up slightly for funny effect
        output_path
    ]
    
    subprocess.run(cmd, check=True)
    
    # Cleanup
    for clip in clips:
        os.remove(clip)
    os.remove(concat_file)
    os.rmdir(temp_dir)
    
    print(f"✅ Video created: {output_path}")
    return output_path

async def create_funny_news_video():
    """Main function to create funny news video"""
    
    print("""
🎬 FUNNY NEWS VIDEO CREATOR
==========================
📸 Using SCRAPED MEDIA ONLY - NO VEO
⏱️  Duration: 20 seconds
🔍 Sources: Reddit funny content
""")
    
    # 1. Scrape funny content
    content = await scrape_funny_content()
    
    if not content:
        print("❌ No content found!")
        return
    
    print("\n📋 Top funny content found:")
    for i, item in enumerate(content[:5]):
        print(f"{i+1}. {item['title'][:60]}... (r/{item['subreddit']})")
    
    # 2. Download media
    media_dir = "scraped_funny_media"
    downloaded = await download_media(content, media_dir)
    
    if not downloaded:
        print("❌ No media downloaded!")
        return
    
    # 3. Create video
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"funny_news_{timestamp}.mp4"
    
    video_path = create_video_ffmpeg(downloaded, duration=20, output_path=output_file)
    
    # Cleanup
    for media in downloaded:
        os.remove(media['path'])
    os.rmdir(media_dir)
    
    print(f"\n✅ SUCCESS!")
    print(f"📹 Video saved as: {video_path}")
    print(f"⏱️  Duration: 20 seconds")
    print(f"📸 Used {len(downloaded)} scraped media files")
    print("🚫 NO VEO/AI generation was used")
    
    return video_path

if __name__ == "__main__":
    asyncio.run(create_funny_news_video())