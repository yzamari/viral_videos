"""
End-to-end integration tests for the Viral Video Generator system
"""
import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from datetime import datetime

from src.scrapers.youtube_scraper import YouTubeScraper
from src.analyzers.video_analyzer import VideoAnalyzer
from src.generators.video_generator import VideoGenerator
from src.generators.director import Director
from src.models.video_models import Platform, VideoCategory, TrendingVideo
from src.utils.exceptions import GenerationFailedError


class TestEndToEnd:
    """End-to-end integration tests"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
            
    @pytest.fixture
    def mock_trending_videos(self):
        """Create mock trending videos"""
        return [
            TrendingVideo(
                video_id=f"video_{i}",
                platform=Platform.YOUTUBE,
                url=f"https://youtube.com/watch?v=video_{i}",
                title=f"Trending Video {i}",
                description="Amazing viral content",
                category=VideoCategory.ENTERTAINMENT,
                tags=["viral", "trending", "amazing"],
                view_count=1000000 + i * 100000,
                like_count=50000 + i * 5000,
                comment_count=5000 + i * 500,
                upload_date=datetime.now(),
                trending_position=i + 1,
                channel_id=f"channel_{i}",
                channel_name=f"Viral Channel {i}",
                channel_subscribers=100000,
                duration_seconds=180,
                thumbnail_url="https://example.com/thumb.jpg",
                has_captions=True,
                language="en"
            )
            for i in range(3)
        ]
        
    @patch('src.scrapers.youtube_scraper.build')
    @patch('src.analyzers.video_analyzer.genai.configure')
    @patch('src.generators.video_generator.genai.configure')
    @patch('src.generators.director.genai.configure')
    def test_full_workflow(self, mock_director_genai, mock_gen_genai, 
                          mock_analyzer_genai, mock_youtube_build, 
                          temp_output_dir, mock_trending_videos):
        """Test complete workflow from scraping to generation"""
        
        # 1. Setup - Initialize components
        youtube_key = "test_youtube_key"
        gemini_key = "test_gemini_key"
        
        scraper = YouTubeScraper(youtube_key)
        analyzer = VideoAnalyzer(gemini_key)
        generator = VideoGenerator(gemini_key, temp_output_dir)
        
        # 2. Mock scraping
        with patch.object(scraper, 'get_trending_videos', return_value=mock_trending_videos):
            trending_videos = scraper.get_trending_videos(max_results=3)
            
        assert len(trending_videos) == 3
        assert all(isinstance(v, TrendingVideo) for v in trending_videos)
        
        # 3. Mock analysis
        mock_analyses = []
        with patch.object(analyzer.model, 'generate_content') as mock_gen:
            mock_gen.return_value = Mock(text='{"content_themes": ["comedy", "viral"], "emotional_tone": "exciting"}')
            
            analyses = analyzer.batch_analyze(trending_videos[:2])
            assert len(analyses) == 2
            
        # 4. Mock video generation
        with patch.object(generator.director, 'write_script') as mock_write_script:
            mock_write_script.return_value = {
                'hook': {'text': 'Amazing!', 'type': 'shock'},
                'segments': [{'text': 'Content', 'duration': 10}],
                'cta': {'text': 'Subscribe!'},
                'duration': 30
            }
            
            # Mock video file creation
            with patch('src.generators.video_generator.concatenate_videoclips'):
                with patch('src.generators.video_generator.ColorClip'):
                    with patch('src.generators.video_generator.TextClip'):
                        with patch('src.generators.video_generator.CompositeVideoClip'):
                            # Create dummy file
                            dummy_file = os.path.join(temp_output_dir, "test_video.mp4")
                            with open(dummy_file, 'w') as f:
                                f.write("dummy video content")
                                
                            # Mock write_videofile to use dummy file
                            with patch('moviepy.video.VideoClip.VideoClip.write_videofile'):
                                config = generator.generate_video_config(
                                    analyses=analyses,
                                    platform=Platform.YOUTUBE,
                                    category=VideoCategory.ENTERTAINMENT
                                )
                                
                                generated_video = generator.generate_video(config)
                                
        # 5. Verify results
        assert generated_video is not None
        assert generated_video.video_id is not None
        assert generated_video.config == config
        assert generated_video.script is not None
        
    @patch('src.scrapers.youtube_scraper.build')
    def test_scraping_to_analysis_integration(self, mock_youtube_build):
        """Test integration between scraping and analysis"""
        # Setup
        scraper = YouTubeScraper("test_key")
        analyzer = VideoAnalyzer("test_key")
        
        # Mock YouTube API response
        mock_youtube = Mock()
        mock_youtube_build.return_value = mock_youtube
        mock_youtube.videos().list().execute.return_value = {
            'items': [{
                'id': 'test123',
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test',
                    'publishedAt': '2024-01-01T00:00:00Z',
                    'channelId': 'ch123',
                    'channelTitle': 'Test Channel',
                    'categoryId': '24'
                },
                'statistics': {
                    'viewCount': '1000000',
                    'likeCount': '50000',
                    'commentCount': '5000'
                },
                'contentDetails': {
                    'duration': 'PT5M'
                }
            }]
        }
        
        # Execute scraping
        videos = scraper.get_trending_videos(max_results=1)
        assert len(videos) == 1
        
        # Mock AI analysis
        with patch.object(analyzer.model, 'generate_content') as mock_gen:
            mock_gen.return_value = Mock(
                text='{"content_themes": ["test"], "emotional_tone": "neutral"}'
            )
            
            # Execute analysis
            analyses = analyzer.batch_analyze(videos)
            assert len(analyses) == 1
            assert analyses[0].video_id == 'test123'
            
    def test_error_propagation(self, temp_output_dir):
        """Test that errors propagate correctly through the system"""
        generator = VideoGenerator("test_key", temp_output_dir)
        
        # Test with invalid config
        with pytest.raises(Exception):
            generator.generate_video(None)
            
    @patch('src.generators.director.NewsScraper')
    def test_news_integration(self, mock_news_scraper_class):
        """Test news integration in script generation"""
        # Setup
        director = Director("test_key")
        
        # Mock news scraper
        mock_news_scraper = Mock()
        mock_news_scraper_class.return_value = mock_news_scraper
        mock_news_scraper.search_news.return_value = [
            {
                'title': 'Breaking News',
                'description': 'Important update',
                'published_at': datetime.now()
            }
        ]
        
        # Mock AI response
        with patch.object(director.model, 'generate_content') as mock_gen:
            mock_gen.return_value = Mock(
                text='{"hook": {"text": "News!"}, "segments": []}'
            )
            
            # Execute with news
            script = director.write_script(
                topic="Current Events",
                style="informative",
                duration=30,
                platform=Platform.YOUTUBE,
                category=VideoCategory.NEWS,
                patterns={},
                incorporate_news=True
            )
            
            # Verify news was fetched
            mock_news_scraper.search_news.assert_called()
            
    def test_platform_specific_generation(self, temp_output_dir):
        """Test generation for different platforms"""
        generator = VideoGenerator("test_key", temp_output_dir)
        
        platforms = [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM]
        
        for platform in platforms:
            # Mock director and video generation
            with patch.object(generator.director, 'write_script'):
                with patch.object(generator, '_create_scenes'):
                    with patch.object(generator, '_compose_video'):
                        config = generator.generate_video_config(
                            analyses=[],
                            platform=platform,
                            category=VideoCategory.ENTERTAINMENT
                        )
                        
                        # Verify platform-specific settings
                        assert config.target_platform == platform
                        if platform == Platform.TIKTOK:
                            assert config.duration_seconds == 15
                        else:
                            assert config.duration_seconds == 30 