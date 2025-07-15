"""
YouTube trending videos scraper using YouTube Data API
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models.video_models import TrendingVideo, Platform, VideoCategory
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class YouTubeScraper:
    """Scrape trending videos from YouTube"""

    def __init__(self, api_key: Optional[str] = None, use_mock_data: bool = True):
        self.api_key = api_key
        self.use_mock_data = use_mock_data or not api_key

        if not self.use_mock_data and api_key:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            self.pytrends = None  # Initialize lazily when needed
        else:
            self.youtube = None
            self.pytrends = None
            logger.info("YouTube scraper initialized in mock mode - no API key provided")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_trending_videos(self,
                            max_results: int = 50,
                            region_code: str = 'US',
                            category_id: Optional[str] = None,
                            days_back: int = 6) -> List[TrendingVideo]:
        """
        Fetch trending videos from YouTube

        Args:
            max_results: Maximum number of videos to fetch
            region_code: Country code for trending videos
            category_id: YouTube category ID (optional)
            days_back: Number of days back to search for trending videos (default: 6)

        Returns:
            List of TrendingVideo objects
        """
        # Return mock data if no API key is available
        if self.use_mock_data:
            return self._get_mock_trending_videos(max_results, category_id, days_back)

        try:
            # Build request parameters
            request_params = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': min(max_results, 50)  # API limit
            }

            if category_id:
                request_params['videoCategoryId'] = category_id

            # Execute API request
            request = self.youtube.videos().list(**request_params)
            response = request.execute()

            trending_videos = []

            # Filter by upload date if days_back is specified
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for idx, item in enumerate(response.get('items', [])):
                try:
                    video = self._parse_video_item(item, idx + 1)
                    if video:
                        # Filter by upload date
                        if video.upload_date >= cutoff_date:
                            trending_videos.append(video)
                        else:
                            logger.debug(
                                f"Skipping video {video.title} - uploaded {video.upload_date} (before cutoff {cutoff_date})")
                except Exception as e:
                    logger.error(f"Error parsing video {item.get('id')}: {e}")
                    continue

            logger.info(f"Fetched {len(trending_videos)} trending videos from last {days_back} days")
            return trending_videos

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching trending videos: {e}")
            raise

    def _parse_video_item(
        self,
        item: Dict,
        position: int) -> Optional[TrendingVideo]:
        """Parse YouTube API response item into TrendingVideo model"""
        try:
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})

            # Parse duration from ISO 8601
            duration = self._parse_duration(content_details.get('duration', 'PT0S'))

            # Get channel details
            channel_id = snippet['channelId']
            channel_info = self._get_channel_info(channel_id)

            # Determine category
            category = self._map_category(snippet.get('categoryId'))

            video = TrendingVideo(
                video_id=item['id'],
                platform=Platform.YOUTUBE,
                url=f"https://www.youtube.com/watch?v={item['id']}",
                title=snippet['title'],
                description=snippet.get('description', ''),
                category=category,
                tags=snippet.get('tags', []),
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)),
                comment_count=int(statistics.get('commentCount', 0)),
                upload_date=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                trending_position=position,
                channel_id=channel_id,
                channel_name=snippet['channelTitle'],
                channel_subscribers=channel_info.get('subscriber_count'),
                duration_seconds=duration,
                thumbnail_url=snippet['thumbnails']['high']['url'],
                has_captions=content_details.get('caption') == 'true',
                language=snippet.get('defaultLanguage') or snippet.get('defaultAudioLanguage')
            )

            return video

        except Exception as e:
            logger.error(f"Error parsing video item: {e}")
            return None

    def _parse_duration(self, duration_str: str) -> int:
        """Convert ISO 8601 duration to seconds"""
        import re

        # Pattern: PT#H#M#S
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def _get_channel_info(self, channel_id: str) -> Dict:
        """Get channel subscriber count"""
        try:
            request = self.youtube.channels().list(
                part='statistics',
                id=channel_id
            )
            response = request.execute()

            if response['items']:
                stats = response['items'][0]['statistics']
                return {
                    'subscriber_count': int(stats.get('subscriberCount', 0))
                }
        except Exception as e:
            logger.warning(f"Could not fetch channel info for {channel_id}: {e}")

        return {}

    def _map_category(self, category_id: str) -> VideoCategory:
        """Map YouTube category ID to our VideoCategory enum"""
        # YouTube category mappings
        category_map = {
            '10': VideoCategory.MUSIC,
            '20': VideoCategory.GAMING,
            '24': VideoCategory.ENTERTAINMENT,
            '23': VideoCategory.COMEDY,
            '27': VideoCategory.EDUCATION,
            '28': VideoCategory.TECHNOLOGY,
            '17': VideoCategory.SPORTS,
            '25': VideoCategory.NEWS,
            '22': VideoCategory.LIFESTYLE,
        }

        return category_map.get(category_id, VideoCategory.OTHER)

    def get_search_trends(
        self,
        keywords: List[str],
        timeframe: str = 'now 7-d') -> pd.DataFrame:
        """
        Get Google Trends data for keywords

        Args:
            keywords: List of keywords to check trends for
            timeframe: Time range for trends (default: last 7 days)

        Returns:
            DataFrame with trends data
        """
        try:
            # Initialize pytrends lazily
            if self.pytrends is None:
                from pytrends.request import TrendReq
                self.pytrends = TrendReq(hl='en-US', tz=360)

            self.pytrends.build_payload(keywords, timeframe=timeframe, geo='US')
            trends_data = self.pytrends.interest_over_time()

            if not trends_data.empty:
                # Remove 'isPartial' column if present
                if 'isPartial' in trends_data.columns:
                    trends_data = trends_data.drop('isPartial', axis=1)

            return trends_data

        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            return pd.DataFrame()

    def get_related_queries(self, keyword: str) -> Dict[str, pd.DataFrame]:
        """Get related queries for a keyword from Google Trends"""
        try:
            # Initialize pytrends lazily
            if self.pytrends is None:
                from pytrends.request import TrendReq
                self.pytrends = TrendReq(hl='en-US', tz=360)

            self.pytrends.build_payload([keyword], timeframe='now 7-d', geo='US')
            related_queries = self.pytrends.related_queries()
            return related_queries.get(keyword, {})
        except Exception as e:
            logger.error(f"Error fetching related queries: {e}")
            return {}

    def search_videos(self,
                      query: str,
                      max_results: int = 50,
                      order: str = 'viewCount',
                      days_back: int = 6) -> List[TrendingVideo]:
        """
        Search for videos using YouTube API

        Args:
            query: Search query
            max_results: Maximum results to return
            order: Sort order (date, rating, relevance, title, viewCount)
            days_back: Number of days back to search for videos (default: 6)

        Returns:
            List of TrendingVideo objects
        """
        # Return mock data if no API key is available
        if self.use_mock_data:
            return self._get_mock_search_videos(query, max_results, days_back)

        try:
            # Calculate published_after from days_back
            published_after = datetime.now() - timedelta(days=days_back)

            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'order': order,
                'maxResults': min(max_results, 50),
                'publishedAfter': published_after.isoformat() + 'Z'
            }

            request = self.youtube.search().list(**search_params)
            response = request.execute()

            # Get video IDs
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]

            if not video_ids:
                logger.info(f"No videos found for query '{query}' in last {days_back} days")
                return []

            # Get full video details
            videos_request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            )
            videos_response = videos_request.execute()

            videos = []
            for idx, item in enumerate(videos_response.get('items', [])):
                video = self._parse_video_item(item, idx + 1)
                if video:
                    videos.append(video)

            logger.info(f"Found {len(videos)} videos for query '{query}' from last {days_back} days")
            return videos

        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []

    def _get_mock_trending_videos(
            self,
            max_results: int = 50,
            category_id: Optional[str] = None,
            days_back: int = 6) -> List[TrendingVideo]:
        """Generate mock trending videos for testing purposes"""
        logger.info(f"Generating {max_results} mock trending videos from last {days_back} days")

        mock_videos = []
        base_date = datetime.now() - timedelta(hours=12)  # Start from 12 hours ago

        mock_data = [
            {
                'title': 'Amazing AI Tool That Will Change Everything!',
                'description': 'This revolutionary AI tool is transforming how we work...',
                'category': VideoCategory.TECHNOLOGY,
                'tags': ['AI', 'technology', 'innovation', 'productivity'],
                'view_count': 1250000,
                'like_count': 45000,
                'comment_count': 3200,
                'channel_name': 'TechExplainer',
                'duration': 420
            },
            {
                'title': 'VIRAL Dance Challenge Goes WRONG!',
                'description': 'What started as a fun dance challenge turned into...',
                'category': VideoCategory.ENTERTAINMENT,
                'tags': ['dance', 'challenge', 'viral', 'funny'],
                'view_count': 2850000,
                'like_count': 78000,
                'comment_count': 12500,
                'channel_name': 'ViralDancer',
                'duration': 180
            },
            {
                'title': 'How I Made $10,000 in 30 Days',
                'description': 'Step by step guide to making money online...',
                'category': VideoCategory.EDUCATION,
                'tags': ['money', 'business', 'entrepreneur', 'success'],
                'view_count': 980000,
                'like_count': 32000,
                'comment_count': 5400,
                'channel_name': 'MoneyMaker',
                'duration': 720
            },
            {
                'title': 'Gaming Moments That Made Me RAGE QUIT',
                'description': 'These gaming fails will make you laugh and cry...',
                'category': VideoCategory.GAMING,
                'tags': ['gaming', 'fails', 'funny', 'compilation'],
                'view_count': 1680000,
                'like_count': 56000,
                'comment_count': 8900,
                'channel_name': 'GamerRage',
                'duration': 600
            },
            {
                'title': 'Ultimate Life Hacks That Actually Work',
                'description': 'These life hacks will save you time and money...',
                'category': VideoCategory.LIFESTYLE,
                'tags': ['life hacks', 'tips', 'productivity', 'DIY'],
                'view_count': 750000,
                'like_count': 28000,
                'comment_count': 2100,
                'channel_name': 'LifeHacker',
                'duration': 480
            }
        ]

        # Cycle through mock data to fill max_results
        for i in range(min(max_results, 50)):  # Limit to reasonable number
            data = mock_data[i % len(mock_data)]

            # Skip if category filter is specified and doesn't match
            if category_id:
                # Simple category mapping for mock data
                if (category_id == '28' and data['category'] != VideoCategory.TECHNOLOGY) or \
                   (category_id == '20' and data['category'] != VideoCategory.GAMING) or \
                   (category_id == '24' and data['category'] != VideoCategory.ENTERTAINMENT):
                    continue

            video_id = f"mock_video_{i:03d}"
            # Distribute videos across the days_back period
            hours_offset = (i * days_back * 24) // max_results
            upload_date = base_date - timedelta(hours=hours_offset)

            video = TrendingVideo(
                video_id=video_id,
                platform=Platform.YOUTUBE,
                url=f"https://www.youtube.com/watch?v={video_id}",
                title=f"{data['title']} #{i + 1}",
                description=data['description'],
                category=data['category'],
                tags=data['tags'],
                view_count=data['view_count'] + (i * 10000),  # Vary view counts
                like_count=data['like_count'] + (i * 500),
                comment_count=data['comment_count'] + (i * 50),
                upload_date=upload_date,
                trending_position=i + 1,
                channel_id=f"mock_channel_{i % 5:02d}",
                channel_name=f"{data['channel_name']}_{i % 5}",
                channel_subscribers=50000 + (i * 5000),
                duration_seconds=data['duration'],
                thumbnail_url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                has_captions=True,
                language='en'
            )

            mock_videos.append(video)

        logger.info(f"Generated {len(mock_videos)} mock trending videos from last {days_back} days")
        return mock_videos

    def _get_mock_search_videos(
        self,
        query: str,
        max_results: int = 50,
        days_back: int = 6) -> List[TrendingVideo]:
        """Generate mock search results for testing purposes"""
        logger.info(f"Generating {max_results} mock search videos for query '{query}' from last {days_back} days")

        # Create query-specific mock data
        query_lower = query.lower()
        mock_videos = []
        base_date = datetime.now() - timedelta(hours=6)  # Start from 6 hours ago

        # Query-specific templates
        if 'cat' in query_lower or 'pet' in query_lower:
            base_data = {
                'title': f'Cute Cat Video About {query}',
                'description': f'Amazing cat content related to {query}...',
                'category': VideoCategory.ENTERTAINMENT,
                'tags': ['cat', 'pets', 'cute', 'animals'],
                'channel_name': 'CatLover'
            }
        elif 'tech' in query_lower or 'ai' in query_lower:
            base_data = {
                'title': f'Latest Technology: {query}',
                'description': f'Deep dive into {query} technology...',
                'category': VideoCategory.TECHNOLOGY,
                'tags': ['technology', 'AI', 'innovation'],
                'channel_name': 'TechGuru'
            }
        else:
            base_data = {
                'title': f'Everything About {query}',
                'description': f'Comprehensive guide to {query}...',
                'category': VideoCategory.EDUCATION,
                'tags': [query, 'tutorial', 'guide'],
                'channel_name': 'LearnMore'
            }

        for i in range(min(max_results, 20)):  # Limit mock search results
            video_id = f"mock_search_{query.replace(' ', '_')}_{i:03d}"
            # Distribute videos across the days_back period
            hours_offset = (i * days_back * 24) // max_results
            upload_date = base_date - timedelta(hours=hours_offset)

            video = TrendingVideo(
                video_id=video_id,
                platform=Platform.YOUTUBE,
                url=f"https://www.youtube.com/watch?v={video_id}",
                title=f"{base_data['title']} #{i + 1}",
                description=base_data['description'],
                category=base_data['category'],
                tags=base_data['tags'],
                view_count=100000 + (i * 25000),
                like_count=5000 + (i * 200),
                comment_count=500 + (i * 50),
                upload_date=upload_date,
                trending_position=i + 1,
                channel_id=f"mock_search_channel_{i % 3:02d}",
                channel_name=f"{base_data['channel_name']}_{i % 3}",
                channel_subscribers=25000 + (i * 2000),
                duration_seconds=300 + (i * 60),
                thumbnail_url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                has_captions=True,
                language='en'
            )

            mock_videos.append(video)

        logger.info(f"Generated {len(mock_videos)} mock search videos for '{query}' from last {days_back} days")
        return mock_videos
