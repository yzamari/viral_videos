"""
YouTube video scraper for news content
Searches YouTube for news videos and extracts clips
"""

import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import yt_dlp
import os

logger = logging.getLogger(__name__)

class YouTubeScraper:
    """Scrape YouTube videos related to news stories"""
    
    def __init__(self, download_dir: str = "outputs/youtube_clips"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': 'best[height<=720]',  # Limit to 720p for faster download
            'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
        }
    
    async def search_and_download(
        self,
        query: str,
        max_results: int = 3,
        max_duration: int = 300  # Max 5 minutes
    ) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos and download clips
        
        Args:
            query: Search query (news headline)
            max_results: Maximum number of results to return
            max_duration: Maximum video duration in seconds
            
        Returns:
            List of video metadata with local paths
        """
        try:
            # Search YouTube
            search_opts = {
                **self.ydl_opts,
                'extract_flat': 'in_playlist',
                'playlistend': max_results,
            }
            
            results = []
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                # Search for videos
                search_query = f"ytsearch{max_results}:{query} news"
                search_results = ydl.extract_info(search_query, download=False)
                
                if not search_results or 'entries' not in search_results:
                    logger.warning(f"No YouTube results for: {query}")
                    return []
                
                # Process each result
                for entry in search_results['entries']:
                    if not entry:
                        continue
                    
                    try:
                        # Get full video info
                        video_info = ydl.extract_info(
                            f"https://youtube.com/watch?v={entry.get('id', '')}",
                            download=False
                        )
                        
                        # Check duration
                        duration = video_info.get('duration', 0)
                        if duration > max_duration:
                            continue
                        
                        # Download video
                        logger.info(f"Downloading YouTube video: {video_info.get('title', 'Unknown')}")
                        ydl.download([video_info['webpage_url']])
                        
                        # Get downloaded file path
                        video_id = video_info.get('id', '')
                        ext = video_info.get('ext', 'mp4')
                        local_path = os.path.join(self.download_dir, f"{video_id}.{ext}")
                        
                        if os.path.exists(local_path):
                            results.append({
                                'type': 'video',
                                'url': video_info.get('webpage_url', ''),
                                'local_path': local_path,
                                'title': video_info.get('title', ''),
                                'duration': duration,
                                'channel': video_info.get('channel', ''),
                                'thumbnail': video_info.get('thumbnail', ''),
                                'source': 'youtube'
                            })
                            
                    except Exception as e:
                        logger.error(f"Failed to process YouTube video: {e}")
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []
    
    async def extract_clip(
        self,
        video_path: str,
        start_time: float = 0,
        duration: float = 10,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract a clip from a downloaded video
        
        Args:
            video_path: Path to the downloaded video
            start_time: Start time in seconds
            duration: Clip duration in seconds
            output_path: Output path for the clip
            
        Returns:
            Path to the extracted clip
        """
        try:
            if not output_path:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(
                    self.download_dir,
                    f"{base_name}_clip_{start_time}_{duration}.mp4"
                )
            
            # Use ffmpeg to extract clip
            import subprocess
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', video_path,
                '-t', str(duration),
                '-c', 'copy',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            if os.path.exists(output_path):
                return output_path
            
        except Exception as e:
            logger.error(f"Failed to extract clip: {e}")
        
        return None


class YouTubeNewsEnhancer:
    """Enhance news stories with YouTube video content"""
    
    def __init__(self):
        self.scraper = YouTubeScraper()
    
    async def enhance_news_items(
        self,
        news_items: List[Dict[str, Any]],
        search_videos: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Enhance news items with YouTube videos
        
        Args:
            news_items: List of news items to enhance
            search_videos: Whether to search for videos
            
        Returns:
            Enhanced news items with video content
        """
        if not search_videos:
            return news_items
        
        enhanced_items = []
        
        for item in news_items:
            try:
                # Search for related YouTube videos
                title = item.get('title', '')
                if not title:
                    enhanced_items.append(item)
                    continue
                
                logger.info(f"Searching YouTube for: {title}")
                videos = await self.scraper.search_and_download(
                    query=title,
                    max_results=1,  # One video per news item
                    max_duration=180  # Max 3 minutes
                )
                
                if videos:
                    # Add video to media assets
                    video = videos[0]
                    if 'media_assets' not in item:
                        item['media_assets'] = []
                    
                    item['media_assets'].append({
                        'type': 'video',
                        'url': video['local_path'],
                        'source': 'youtube',
                        'title': video['title'],
                        'duration': video['duration']
                    })
                    
                    logger.info(f"✅ Added YouTube video for: {title}")
                
                enhanced_items.append(item)
                
            except Exception as e:
                logger.error(f"Failed to enhance news item: {e}")
                enhanced_items.append(item)
        
        return enhanced_items