"""
Integration tests for Viral Video Generator
"""
import pytest
from unittest.mock import patch, Mock
import tempfile

from src.scrapers.youtube_scraper import YouTubeScraper
from src.analyzers.video_analyzer import VideoAnalyzer
from src.generators.video_generator import VideoGenerator
from src.models.video_models import Platform, VideoCategory


class TestIntegration:
    """Integration tests for system components"""
    
    @pytest.fixture
    def temp_dir(self):
        """Temporary directory for outputs"""
        with tempfile.TemporaryDirectory() as td:
            yield td
            
    def test_scraper_analyzer_integration(self):
        """Test scraper to analyzer flow"""
        scraper = YouTubeScraper("test_key")
        analyzer = VideoAnalyzer("test_key")
        
        # Mock scraping
        with patch.object(scraper, 'get_trending_videos') as mock_get:
            mock_get.return_value = []
            videos = scraper.get_trending_videos()
            
        # Mock analysis
        with patch.object(analyzer.model, 'generate_content'):
            analyses = analyzer.batch_analyze(videos)
            assert isinstance(analyses, list)
            
    def test_full_pipeline(self, temp_dir):
        """Test complete pipeline"""
        # Initialize components
        scraper = YouTubeScraper("key1")
        analyzer = VideoAnalyzer("key2") 
        generator = VideoGenerator("key2", temp_dir)
        
        # Mock all external calls
        with patch('src.scrapers.youtube_scraper.build'):
            with patch.object(analyzer.model, 'generate_content'):
                with patch.object(generator.director, 'write_script'):
                    # Test pipeline runs without errors
                    videos = []
                    analyses = analyzer.batch_analyze(videos)
                    
                    if analyses:
                        config = generator.generate_video_config(
                            analyses=analyses,
                            platform=Platform.YOUTUBE,
                            category=VideoCategory.ENTERTAINMENT
                        )
                        assert config is not None 