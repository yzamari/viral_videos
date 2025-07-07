"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Disable external API calls in tests
@pytest.fixture(autouse=True)
def disable_external_apis():
    """Automatically mock external API calls"""
    with patch('src.scrapers.youtube_scraper.build') as mock_youtube:
        with patch('google.generativeai.configure') as mock_genai:
            with patch('requests.get') as mock_requests:
                # Setup default returns
                mock_youtube.return_value = Mock()
                mock_requests.return_value = Mock(status_code=200, json=lambda: {})
                yield
                
@pytest.fixture
def mock_settings():
    """Mock application settings"""
    from src.config.config import Settings
    return Settings(
        gcp_project_id="test-project",
        gcs_bucket_name="test-bucket",
        google_api_key="test-gemini-key",
        youtube_api_key="test-youtube-key"
    ) 