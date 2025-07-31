"""
YouTube Trending Service - Real-time trending data from YouTube Data API
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
from ...utils.logging_config import get_logger

logger = get_logger(__name__)

class YouTubeTrendingService:
    """Fetches real trending data from YouTube Data API v3"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube service with API key"""
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.youtube = None
        
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("✅ YouTube API initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize YouTube API: {e}")
        else:
            logger.warning("⚠️ No YouTube API key provided - trending data will be limited")
    
    def get_trending_videos(self, 
                          region_code: str = 'US',
                          category_id: Optional[str] = None,
                          max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get trending videos from YouTube
        
        Args:
            region_code: ISO 3166-1 alpha-2 country code (default: US)
            category_id: YouTube category ID (optional)
            max_results: Maximum number of results (default: 50, max: 50)
            
        Returns:
            List of trending video data
        """
        if not self.youtube:
            logger.warning("YouTube API not available - returning empty list")
            return []
        
        try:
            # Get trending videos
            request_params = {
                'part': 'snippet,contentDetails,statistics',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': min(max_results, 50)
            }
            
            if category_id:
                request_params['videoCategoryId'] = category_id
            
            request = self.youtube.videos().list(**request_params)
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_data = self._parse_video_data(item)
                videos.append(video_data)
            
            logger.info(f"✅ Fetched {len(videos)} trending videos from YouTube")
            return videos
            
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error fetching trending videos: {e}")
            return []
    
    def search_trending_by_keyword(self,
                                 keyword: str,
                                 max_results: int = 25,
                                 order: str = 'viewCount',
                                 published_after: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Search for trending videos by keyword
        
        Args:
            keyword: Search query
            max_results: Maximum results to return
            order: Sort order (relevance, date, rating, viewCount, title)
            published_after: Only return videos published after this date
            
        Returns:
            List of video data sorted by trend metrics
        """
        if not self.youtube:
            return []
        
        try:
            # Set default published_after to last 7 days if not specified
            if not published_after:
                published_after = datetime.now() - timedelta(days=7)
            
            search_params = {
                'part': 'snippet',
                'q': keyword,
                'type': 'video',
                'order': order,
                'maxResults': min(max_results, 50),
                'publishedAfter': published_after.isoformat() + 'Z'
            }
            
            # Search for videos
            search_response = self.youtube.search().list(**search_params).execute()
            
            # Get video IDs
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                return []
            
            # Get detailed video information
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video_data = self._parse_video_data(item)
                videos.append(video_data)
            
            # Sort by engagement score
            videos.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            logger.info(f"✅ Found {len(videos)} trending videos for keyword: {keyword}")
            return videos
            
        except Exception as e:
            logger.error(f"❌ Error searching trending videos: {e}")
            return []
    
    def get_channel_latest_videos(self, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get latest videos from a specific channel"""
        if not self.youtube:
            return []
        
        try:
            # Get channel's uploads playlist
            channels_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channels_response.get('items'):
                return []
            
            uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=min(max_results, 50)
            ).execute()
            
            video_ids = [item['snippet']['resourceId']['videoId'] 
                        for item in playlist_response.get('items', [])]
            
            if not video_ids:
                return []
            
            # Get detailed video information
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video_data = self._parse_video_data(item)
                videos.append(video_data)
            
            return videos
            
        except Exception as e:
            logger.error(f"❌ Error fetching channel videos: {e}")
            return []
    
    def get_video_categories(self, region_code: str = 'US') -> Dict[str, str]:
        """Get list of video categories for a region"""
        if not self.youtube:
            return {}
        
        try:
            response = self.youtube.videoCategories().list(
                part='snippet',
                regionCode=region_code
            ).execute()
            
            categories = {}
            for item in response.get('items', []):
                category_id = item['id']
                category_name = item['snippet']['title']
                categories[category_id] = category_name
            
            return categories
            
        except Exception as e:
            logger.error(f"❌ Error fetching categories: {e}")
            return {}
    
    def analyze_trending_patterns(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in trending videos"""
        if not videos:
            return {}
        
        try:
            # Calculate averages and patterns
            total_views = sum(v['view_count'] for v in videos)
            avg_views = total_views / len(videos)
            avg_duration = sum(v['duration_seconds'] for v in videos) / len(videos)
            avg_engagement = sum(v['engagement_score'] for v in videos) / len(videos)
            
            # Extract common tags
            all_tags = []
            for video in videos:
                all_tags.extend(video.get('tags', []))
            
            # Count tag frequency
            tag_counts = {}
            for tag in all_tags:
                tag_lower = tag.lower()
                tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
            
            # Sort tags by frequency
            trending_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            
            # Analyze titles for common patterns
            title_words = []
            for video in videos:
                title_words.extend(video['title'].lower().split())
            
            # Count word frequency (excluding common words)
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were'}
            word_counts = {}
            for word in title_words:
                if word not in common_words and len(word) > 2:
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            trending_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            
            # Identify optimal upload times
            upload_hours = {}
            for video in videos:
                hour = video['published_at'].hour
                upload_hours[hour] = upload_hours.get(hour, 0) + 1
            
            best_upload_hours = sorted(upload_hours.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analysis = {
                'total_videos_analyzed': len(videos),
                'average_metrics': {
                    'views': int(avg_views),
                    'duration_seconds': int(avg_duration),
                    'engagement_score': round(avg_engagement, 4)
                },
                'trending_tags': [{'tag': tag, 'count': count} for tag, count in trending_tags],
                'trending_title_words': [{'word': word, 'count': count} for word, count in trending_words],
                'optimal_duration_range': {
                    'min_seconds': int(min(v['duration_seconds'] for v in videos)),
                    'max_seconds': int(max(v['duration_seconds'] for v in videos)),
                    'sweet_spot': int(avg_duration)
                },
                'best_upload_hours_utc': [{'hour': hour, 'frequency': freq} for hour, freq in best_upload_hours],
                'top_performing_videos': videos[:5],  # Top 5 by engagement
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing trending patterns: {e}")
            return {}
    
    def _parse_video_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse YouTube API video response into structured data"""
        try:
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            # Parse duration
            duration_iso = content_details.get('duration', 'PT0S')
            duration = isodate.parse_duration(duration_iso)
            duration_seconds = int(duration.total_seconds())
            
            # Calculate engagement metrics
            view_count = int(statistics.get('viewCount', 0))
            like_count = int(statistics.get('likeCount', 0))
            comment_count = int(statistics.get('commentCount', 0))
            
            # Calculate engagement score (likes + comments per 1000 views)
            engagement_score = 0
            if view_count > 0:
                engagement_score = ((like_count + comment_count) / view_count) * 1000
            
            # Parse published date
            published_at = datetime.fromisoformat(snippet.get('publishedAt', '').replace('Z', '+00:00'))
            
            return {
                'video_id': item.get('id', ''),
                'title': snippet.get('title', ''),
                'description': snippet.get('description', '')[:500],  # First 500 chars
                'channel_id': snippet.get('channelId', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': published_at,
                'duration_seconds': duration_seconds,
                'duration_formatted': str(duration),
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': comment_count,
                'engagement_score': round(engagement_score, 2),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'url': f"https://youtube.com/watch?v={item.get('id', '')}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing video data: {e}")
            return {}