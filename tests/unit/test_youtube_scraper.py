"""
Unit tests for YouTube scraper
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pandas as pd

from src.scrapers.youtube_scraper import YouTubeScraper
from src.models.video_models import TrendingVideo, Platform, VideoCategory
from src.utils.exceptions import APIException, RateLimitError


class TestYouTubeScraper:
    """Test suite for YouTube scraper"""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance"""
        return YouTubeScraper(api_key="test_api_key")
        
    @pytest.fixture
    def mock_youtube_response(self):
        """Mock YouTube API response"""
        return {
            'items': [
                {
                    'id': 'video123',
                    'snippet': {
                        'title': 'Test Video',
                        'description': 'Test description',
                        'publishedAt': '2024-01-01T00:00:00Z',
                        'channelId': 'channel123',
                        'channelTitle': 'Test Channel',
                        'categoryId': '24',
                        'tags': ['test', 'video'],
                        'thumbnails': {
                            'high': {'url': 'https://example.com/thumb.jpg'}
                        },
                        'defaultLanguage': 'en'
                    },
                    'statistics': {
                        'viewCount': '1000000',
                        'likeCount': '50000',
                        'commentCount': '5000'
                    },
                    'contentDetails': {
                        'duration': 'PT5M30S',
                        'caption': 'true'
                    }
                }
            ]
        }
        
    def test_init(self, scraper):
        """Test scraper initialization"""
        assert scraper.api_key == "test_api_key"
        assert scraper.youtube is not None
        assert scraper.pytrends is not None
        
    @patch('src.scrapers.youtube_scraper.build')
    def test_get_trending_videos_success(self, mock_build, scraper, mock_youtube_response):
        """Test successful trending videos fetch"""
        # Setup mock
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.videos().list().execute.return_value = mock_youtube_response
        mock_youtube.channels().list().execute.return_value = {
            'items': [{'statistics': {'subscriberCount': '100000'}}]
        }
        
        # Reinitialize scraper with mocked build
        scraper.__init__("test_api_key")
        
        # Execute
        videos = scraper.get_trending_videos(max_results=10)
        
        # Assert
        assert len(videos) == 1
        assert isinstance(videos[0], TrendingVideo)
        assert videos[0].video_id == 'video123'
        assert videos[0].title == 'Test Video'
        assert videos[0].view_count == 1000000
        assert videos[0].platform == Platform.YOUTUBE
        
    @patch('src.scrapers.youtube_scraper.build')
    def test_get_trending_videos_api_error(self, mock_build, scraper):
        """Test API error handling"""
        # Setup mock to raise exception
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.videos().list().execute.side_effect = Exception("API Error")
        
        # Reinitialize scraper
        scraper.__init__("test_api_key")
        
        # Execute and assert
        with pytest.raises(Exception):
            scraper.get_trending_videos()
            
    def test_parse_duration(self, scraper):
        """Test duration parsing"""
        assert scraper._parse_duration('PT5M30S') == 330  # 5:30
        assert scraper._parse_duration('PT1H2M3S') == 3723  # 1:02:03
        assert scraper._parse_duration('PT30S') == 30
        assert scraper._parse_duration('PT1H') == 3600
        assert scraper._parse_duration('invalid') == 0
        
    def test_map_category(self, scraper):
        """Test category mapping"""
        assert scraper._map_category('10') == VideoCategory.MUSIC
        assert scraper._map_category('20') == VideoCategory.GAMING
        assert scraper._map_category('24') == VideoCategory.ENTERTAINMENT
        assert scraper._map_category('999') == VideoCategory.OTHER
        
    @patch('src.scrapers.youtube_scraper.TrendReq')
    def test_get_search_trends(self, mock_trendreq_class, scraper):
        """Test Google Trends integration"""
        # Setup mock
        mock_pytrends = Mock()
        mock_trendreq_class.return_value = mock_pytrends
        
        # Create sample DataFrame
        trends_data = pd.DataFrame({
            'viral': [50, 60, 70],
            'trending': [40, 45, 50]
        })
        mock_pytrends.interest_over_time.return_value = trends_data
        
        # Reinitialize scraper
        scraper.__init__("test_api_key")
        
        # Execute
        result = scraper.get_search_trends(['viral', 'trending'])
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert 'viral' in result.columns
        assert 'trending' in result.columns
        
    @patch('src.scrapers.youtube_scraper.build')
    def test_search_videos(self, mock_build, scraper, mock_youtube_response):
        """Test video search functionality"""
        # Setup mock
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        
        # Mock search response
        search_response = {
            'items': [
                {'id': {'videoId': 'video123'}}
            ]
        }
        mock_youtube.search().list().execute.return_value = search_response
        mock_youtube.videos().list().execute.return_value = mock_youtube_response
        mock_youtube.channels().list().execute.return_value = {
            'items': [{'statistics': {'subscriberCount': '100000'}}]
        }
        
        # Reinitialize scraper
        scraper.__init__("test_api_key")
        
        # Execute
        videos = scraper.search_videos("test query")
        
        # Assert
        assert len(videos) == 1
        assert videos[0].video_id == 'video123'
        
    def test_parse_video_item_invalid(self, scraper):
        """Test handling of invalid video item"""
        invalid_item = {'id': 'test', 'snippet': {}}
        result = scraper._parse_video_item(invalid_item, 1)
        assert result is None
        
    @patch('src.scrapers.youtube_scraper.build')
    def test_rate_limit_handling(self, mock_build, scraper):
        """Test rate limit handling with retry"""
        # Setup mock
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        
        # First call fails, second succeeds
        mock_youtube.videos().list().execute.side_effect = [
            Exception("Rate limit"),
            {'items': []}
        ]
        
        # Reinitialize scraper
        scraper.__init__("test_api_key")
        
        # Execute with retry decorator
        # This should retry and eventually succeed
        videos = scraper.get_trending_videos()
        assert videos == [] 