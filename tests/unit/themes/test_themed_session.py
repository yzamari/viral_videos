"""
Unit tests for Themed Session Manager
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.themes.managers.theme_manager import ThemeManager
from src.themes.managers.themed_session_manager import ThemedSessionManager
from src.themes.models.theme import Theme, ThemeCategory
from src.core.session_manager import SessionManager, SessionContext


class TestThemedSessionManager:
    """Test themed session manager functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def theme_manager(self, temp_dir):
        """Create theme manager"""
        return ThemeManager(f"{temp_dir}/themes")
    
    @pytest.fixture
    def session_manager(self, temp_dir):
        """Create mock session manager"""
        mock_manager = Mock(spec=SessionManager)
        
        # Mock session creation
        def create_session(name):
            session_context = Mock(spec=SessionContext)
            session_context.session_id = f"session_{len(mock_manager.sessions)}"
            session_context.name = name
            session_context.get_path = Mock(side_effect=lambda filename, subdir: 
                Path(temp_dir) / subdir / filename)
            
            # Store session
            if not hasattr(mock_manager, 'sessions'):
                mock_manager.sessions = {}
            mock_manager.sessions[session_context.session_id] = session_context
            
            return session_context
        
        mock_manager.create_session = Mock(side_effect=create_session)
        mock_manager.get_session = Mock(side_effect=lambda sid: 
            getattr(mock_manager, 'sessions', {}).get(sid))
        
        return mock_manager
    
    @pytest.fixture
    def themed_manager(self, theme_manager, session_manager):
        """Create themed session manager"""
        return ThemedSessionManager(theme_manager, session_manager)
    
    def test_create_themed_session_with_preset(self, themed_manager, temp_dir):
        """Test creating session with preset theme"""
        # Create paths for metadata
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Create themed session
        session = themed_manager.create_themed_session("preset_news_edition")
        
        assert session is not None
        assert session.session_id in themed_manager.active_sessions
        
        # Check active session tracking
        session_info = themed_manager.active_sessions[session.session_id]
        assert session_info["theme_id"] == "preset_news_edition"
        assert session_info["theme_name"] == "News Edition"
    
    def test_create_themed_session_with_override(self, themed_manager, temp_dir):
        """Test creating session with setting overrides"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        override_settings = {
            "duration": 120,
            "tone": "casual"
        }
        
        session = themed_manager.create_themed_session(
            "preset_tech",
            session_name="Tech Demo",
            override_settings=override_settings
        )
        
        assert session is not None
        
        # Check override settings tracked
        session_info = themed_manager.active_sessions[session.session_id]
        assert session_info["override_settings"] == override_settings
    
    def test_create_themed_session_invalid_theme(self, themed_manager):
        """Test creating session with invalid theme"""
        with pytest.raises(ValueError, match="Theme not found"):
            themed_manager.create_themed_session("invalid_theme_id")
    
    def test_generate_with_theme(self, themed_manager, temp_dir):
        """Test generating video with theme"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        session = themed_manager.generate_with_theme(
            "preset_sports",
            "Create exciting sports highlight reel"
        )
        
        assert session is not None
        assert session.session_id in themed_manager.active_sessions
        
        # Verify theme was applied
        session_info = themed_manager.active_sessions[session.session_id]
        assert session_info["theme_id"] == "preset_sports"
    
    def test_create_series_session(self, themed_manager, temp_dir):
        """Test creating series with consistent theme"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        sessions = themed_manager.create_series_session(
            "preset_news_edition",
            "Daily News",
            episode_count=5
        )
        
        assert len(sessions) == 5
        
        # Check each episode
        for i, session in enumerate(sessions):
            assert f"Episode {i+1}" in session.name
            
            # All should use same theme
            session_info = themed_manager.active_sessions[session.session_id]
            assert session_info["theme_id"] == "preset_news_edition"
    
    def test_get_session_theme(self, themed_manager, temp_dir):
        """Test retrieving theme from session"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Create themed session
        session = themed_manager.create_themed_session("preset_entertainment")
        
        # Get theme back
        theme = themed_manager.get_session_theme(session.session_id)
        
        assert theme is not None
        assert theme.theme_id == "preset_entertainment"
        assert theme.category == ThemeCategory.ENTERTAINMENT
    
    def test_apply_theme_to_existing_session(self, themed_manager, session_manager, temp_dir):
        """Test applying theme to existing session"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Create regular session
        regular_session = session_manager.create_session("Regular Session")
        
        # Apply theme
        success = themed_manager.apply_theme_to_existing_session(
            regular_session.session_id,
            "preset_tech",
            preserve_content=True
        )
        
        assert success is True
        
        # Verify theme applied
        theme = themed_manager.get_session_theme(regular_session.session_id)
        assert theme is not None
        assert theme.theme_id == "preset_tech"
    
    def test_list_themed_sessions(self, themed_manager, session_manager, temp_dir):
        """Test listing themed sessions"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock list_sessions
        def mock_list_sessions(limit=50):
            return [
                {
                    "session_id": sid,
                    "name": session.name,
                    "created_at": "2024-01-01T00:00:00"
                }
                for sid, session in getattr(session_manager, 'sessions', {}).items()
            ]
        
        session_manager.list_sessions = Mock(side_effect=mock_list_sessions)
        
        # Create multiple themed sessions
        themed_manager.create_themed_session("preset_news_edition", "News 1")
        themed_manager.create_themed_session("preset_news_edition", "News 2")
        themed_manager.create_themed_session("preset_sports", "Sports 1")
        
        # List all themed sessions
        all_sessions = themed_manager.list_themed_sessions()
        assert len(all_sessions) == 3
        
        # Filter by theme
        news_sessions = themed_manager.list_themed_sessions(theme_id="preset_news_edition")
        assert len(news_sessions) == 2
        assert all(s["theme_id"] == "preset_news_edition" for s in news_sessions)
    
    def test_theme_usage_stats(self, themed_manager, session_manager, temp_dir):
        """Test getting theme usage statistics"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock list_sessions
        session_manager.list_sessions = Mock(return_value=[
            {
                "session_id": sid,
                "name": session.name,
                "created_at": "2024-01-01T00:00:00"
            }
            for sid, session in getattr(session_manager, 'sessions', {}).items()
        ])
        
        # Create sessions with different themes
        for _ in range(5):
            themed_manager.create_themed_session("preset_news_edition")
        for _ in range(3):
            themed_manager.create_themed_session("preset_sports")
        for _ in range(2):
            themed_manager.create_themed_session("preset_tech")
        
        # Get stats
        stats = themed_manager.get_theme_usage_stats()
        
        assert stats["total_themed_sessions"] == 10
        assert len(stats["theme_usage"]) == 3
        
        # Check most popular
        assert stats["most_popular_theme"]["theme_id"] == "preset_news_edition"
        assert stats["most_popular_theme"]["usage_count"] == 5
        
        # Check category distribution
        assert stats["category_distribution"]["news"] == 5
        assert stats["category_distribution"]["sports"] == 3
        assert stats["category_distribution"]["tech"] == 2
    
    def test_theme_persistence_in_session(self, themed_manager, temp_dir):
        """Test that theme info is properly saved to session"""
        # Create paths
        metadata_dir = Path(temp_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Create themed session
        session = themed_manager.create_themed_session(
            "preset_entertainment",
            override_settings={"duration": 90}
        )
        
        # Check that theme info file would be created
        # (In real implementation, the file write would happen)
        session.get_path.assert_called_with("theme_info.json", "metadata")
        
        # Verify session tracking
        assert session.session_id in themed_manager.active_sessions
        session_info = themed_manager.active_sessions[session.session_id]
        assert session_info["theme_id"] == "preset_entertainment"
        assert session_info["override_settings"]["duration"] == 90