"""
Shared fixtures and configuration for all CI tests.
This file is automatically loaded by pytest and provides common fixtures.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Common test data
TEST_MISSION = "Create a video about artificial intelligence"
TEST_PLATFORM = "youtube"
TEST_LANGUAGE = "en"
TEST_DURATION = 60


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_session_manager(temp_dir):
    """Mock SessionManager for tests."""
    from src.session_manager import SessionManager
    
    with patch('src.session_manager.SessionManager') as MockSessionManager:
        mock_instance = Mock(spec=SessionManager)
        mock_instance.session_dir = temp_dir
        mock_instance.get_output_path.return_value = temp_dir
        mock_instance.get_session_path.return_value = Path(temp_dir)
        mock_instance.save_artifact.return_value = None
        MockSessionManager.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_core_decisions():
    """Mock CoreDecisions object for tests."""
    from src.core.entities import CoreDecisions, GeneratedVideoConfig
    
    config = GeneratedVideoConfig(
        topic=TEST_MISSION,
        duration=TEST_DURATION,
        platform=TEST_PLATFORM,
        language=TEST_LANGUAGE
    )
    
    decisions = CoreDecisions(
        video_config=config,
        mission=TEST_MISSION,
        target_platform=TEST_PLATFORM,
        language=TEST_LANGUAGE,
        duration=TEST_DURATION
    )
    
    return decisions


@pytest.fixture
def mock_session_context(mock_session_manager):
    """Mock SessionContext for tests."""
    from src.session_manager import SessionContext
    
    context = Mock(spec=SessionContext)
    context.session_manager = mock_session_manager
    context.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    context.mission = TEST_MISSION
    context.get_session_path.return_value = Path(mock_session_manager.session_dir)
    context.save_artifact.return_value = None
    
    return context


@pytest.fixture
def mock_ai_client():
    """Mock AI client for tests."""
    mock_client = MagicMock()
    mock_client.generate_content.return_value = MagicMock(text="Test response")
    mock_client.generate_text.return_value = "Test response"
    return mock_client


@pytest.fixture
def mock_video_config():
    """Mock video configuration."""
    from src.config.video_config import video_config
    return video_config


@pytest.fixture
def sample_script_segments():
    """Sample script segments for testing."""
    return [
        {
            "segment_number": 1,
            "narrator_text": "Welcome to our video about artificial intelligence.",
            "visual_description": "Modern AI interface with neural networks",
            "duration": 5.0
        },
        {
            "segment_number": 2,
            "narrator_text": "AI is transforming our world in amazing ways.",
            "visual_description": "Various AI applications in daily life",
            "duration": 5.0
        }
    ]


@pytest.fixture
def sample_audio_files(temp_dir):
    """Create sample audio files for testing."""
    audio_files = []
    for i in range(2):
        audio_path = os.path.join(temp_dir, f"audio_segment_{i+1}.mp3")
        # Create empty file
        Path(audio_path).touch()
        audio_files.append(audio_path)
    return audio_files


@pytest.fixture
def sample_video_clips(temp_dir):
    """Create sample video clips for testing."""
    clips = []
    for i in range(2):
        clip_path = os.path.join(temp_dir, f"clip_{i+1}.mp4")
        # Create empty file
        Path(clip_path).touch()
        clips.append(clip_path)
    return clips


@pytest.fixture
def mock_veo_client():
    """Mock VEO client for testing."""
    mock_client = MagicMock()
    mock_client.generate_video.return_value = "/path/to/generated/video.mp4"
    return mock_client


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    mock_client = MagicMock()
    mock_client.generate_image.return_value = b"fake_image_data"
    return mock_client


@pytest.fixture
def mock_tts_client():
    """Mock TTS client for testing."""
    mock_client = MagicMock()
    mock_client.synthesize_speech.return_value = MagicMock(audio_content=b"fake_audio_data")
    return mock_client


@pytest.fixture
def mock_social_media_credentials():
    """Mock social media credentials."""
    return {
        "instagram": {
            "username": "test_user",
            "password": "test_pass"
        },
        "youtube": {
            "api_key": "test_api_key"
        },
        "tiktok": {
            "access_token": "test_token"
        }
    }


@pytest.fixture
def multilanguage_test_data():
    """Test data for multiple languages including RTL."""
    return [
        {"code": "en", "text": "Hello World", "is_rtl": False},
        {"code": "es", "text": "Hola Mundo", "is_rtl": False},
        {"code": "he", "text": "שלום עולם", "is_rtl": True},
        {"code": "ar", "text": "مرحبا بالعالم", "is_rtl": True},
        {"code": "fa", "text": "سلام دنیا", "is_rtl": True}
    ]


@pytest.fixture
def mock_ffmpeg_available():
    """Mock ffmpeg availability check."""
    with patch('shutil.which', return_value='/usr/bin/ffmpeg'):
        yield


@pytest.fixture
def disable_gpu():
    """Disable GPU for tests to ensure they run on CI."""
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    yield
    # Restore after test
    if 'CUDA_VISIBLE_DEVICES' in os.environ:
        del os.environ['CUDA_VISIBLE_DEVICES']


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Reset any singleton instances to prevent test interference
    from src.utils.singleton_manager import SingletonManager
    if hasattr(SingletonManager, '_instances'):
        SingletonManager._instances.clear()
    yield


@pytest.fixture
def capture_logs():
    """Capture log output for assertions."""
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    
    yield log_capture
    
    # Remove handler after test
    root_logger.removeHandler(handler)


# Markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_api: Tests requiring API access")
    config.addinivalue_line("markers", "requires_ffmpeg: Tests requiring ffmpeg")
    config.addinivalue_line("markers", "gpu: Tests requiring GPU")