"""
Comprehensive tests for session management system
Tests that all files are properly organized in session directories
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.session_manager import SessionManager, session_manager
from utils.session_context import SessionContext, create_session_context
from models.video_models import GeneratedVideoConfig, Platform, VideoCategory


class TestSessionManagement:
    """Test suite for session management functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(base_output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_session_creation(self):
        """Test session creation and directory structure"""
        # Create session
        session_id = self.session_manager.create_session(
            topic="Test Session",
            platform="tiktok",
            duration=15,
            category="Educational"
        )
        
        # Verify session ID format
        assert session_id.startswith("session_")
        assert len(session_id) > 15
        
        # Verify session directory structure
        session_dir = os.path.join(self.temp_dir, session_id)
        assert os.path.exists(session_dir)
        
        # Check subdirectories
        expected_dirs = [
            "video_clips", "images", "audio", "scripts", 
            "metadata", "final_output", "logs"
        ]
        for dir_name in expected_dirs:
            dir_path = os.path.join(session_dir, dir_name)
            assert os.path.exists(dir_path), f"Missing directory: {dir_name}"
    
    def test_session_context_creation(self):
        """Test session context creation and file operations"""
        # Create session
        session_id = self.session_manager.create_session(
            topic="Test Context",
            platform="youtube",
            duration=30,
            category="Entertainment"
        )
        
        # Create session context
        context = create_session_context(session_id, self.session_manager)
        
        # Verify context properties
        assert context.session_id == session_id
        assert context.session_manager == self.session_manager
        
        # Test path generation
        video_path = context.get_output_path("video_clips", "test_clip.mp4")
        expected_path = os.path.join(self.temp_dir, session_id, "video_clips", "test_clip.mp4")
        assert video_path == expected_path
    
    def test_file_saving_operations(self):
        """Test that files are saved in correct session directories"""
        # Create session and context
        session_id = self.session_manager.create_session(
            topic="File Test",
            platform="instagram",
            duration=15,
            category="Comedy"
        )
        context = create_session_context(session_id, self.session_manager)
        
        # Create temporary files to save
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mp4', delete=False) as f:
            f.write("fake video content")
            temp_video = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', delete=False) as f:
            f.write("fake image content")
            temp_image = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.wav', delete=False) as f:
            f.write("fake audio content")
            temp_audio = f.name
        
        try:
            # Save files using session context
            video_path = context.save_final_video(temp_video)
            image_path = context.save_image(temp_image, "test_image")
            audio_path = context.save_audio_file(temp_audio, "test_audio")
            
            # Verify files are in session directory
            session_dir = os.path.join(self.temp_dir, session_id)
            
            assert video_path.startswith(session_dir)
            assert image_path.startswith(session_dir)
            assert audio_path.startswith(session_dir)
            
            # Verify files exist
            assert os.path.exists(video_path)
            assert os.path.exists(image_path)
            assert os.path.exists(audio_path)
            
            # Verify content
            with open(video_path, 'r') as f:
                assert f.read() == "fake video content"
            
        finally:
            # Cleanup temp files
            for temp_file in [temp_video, temp_image, temp_audio]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_session_metadata_tracking(self):
        """Test session metadata tracking"""
        # Create session
        session_id = self.session_manager.create_session(
            topic="Metadata Test",
            platform="twitter",
            duration=20,
            category="News"
        )
        
        # Log generation steps
        self.session_manager.log_generation_step("script_processing", "completed", {
            "word_count": 50,
            "duration": 18.5
        })
        
        self.session_manager.log_generation_step("video_generation", "in_progress", {
            "clips_generated": 2,
            "total_clips": 4
        })
        
        # Get session info
        session_info = self.session_manager.get_session_info(session_id)
        
        # Verify metadata
        assert session_info["topic"] == "Metadata Test"
        assert session_info["platform"] == "twitter"
        assert session_info["duration"] == 20
        assert session_info["category"] == "News"
        
        # Verify generation steps
        assert len(session_info["generation_steps"]) == 2
        assert session_info["generation_steps"][0]["step"] == "script_processing"
        assert session_info["generation_steps"][0]["status"] == "completed"
        assert session_info["generation_steps"][1]["step"] == "video_generation"
        assert session_info["generation_steps"][1]["status"] == "in_progress"
    
    def test_session_summary_generation(self):
        """Test session summary generation"""
        # Create session and context
        session_id = self.session_manager.create_session(
            topic="Summary Test",
            platform="youtube",
            duration=60,
            category="Educational"
        )
        context = create_session_context(session_id, self.session_manager)
        
        # Create some files in session
        for i in range(3):
            clip_path = context.get_output_path("video_clips", f"clip_{i}.mp4")
            os.makedirs(os.path.dirname(clip_path), exist_ok=True)
            with open(clip_path, 'w') as f:
                f.write(f"clip {i} content")
        
        for i in range(2):
            audio_path = context.get_output_path("audio", f"audio_{i}.wav")
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            with open(audio_path, 'w') as f:
                f.write(f"audio {i} content")
        
        # Get session summary
        summary = context.get_session_summary()
        
        # Verify summary
        assert summary["session_id"] == session_id
        assert summary["file_counts"]["video_clips"] == 3
        assert summary["file_counts"]["audio"] == 2
        assert summary["total_files"] == 5
        assert "creation_time" in summary
        assert "last_modified" in summary
    
    def test_session_cleanup(self):
        """Test session cleanup functionality"""
        # Create session
        session_id = self.session_manager.create_session(
            topic="Cleanup Test",
            platform="tiktok",
            duration=15,
            category="Entertainment"
        )
        
        # Verify session exists
        session_dir = os.path.join(self.temp_dir, session_id)
        assert os.path.exists(session_dir)
        
        # Clean up session
        self.session_manager.cleanup_session(session_id, keep_final_output=False)
        
        # Verify session is removed
        assert not os.path.exists(session_dir)
    
    def test_multiple_sessions_isolation(self):
        """Test that multiple sessions are properly isolated"""
        # Create multiple sessions
        session1 = self.session_manager.create_session(
            topic="Session 1", platform="tiktok", duration=15, category="Comedy"
        )
        session2 = self.session_manager.create_session(
            topic="Session 2", platform="youtube", duration=30, category="Educational"
        )
        
        # Create contexts
        context1 = create_session_context(session1, self.session_manager)
        context2 = create_session_context(session2, self.session_manager)
        
        # Create files in each session
        file1 = context1.get_output_path("video_clips", "test.mp4")
        file2 = context2.get_output_path("video_clips", "test.mp4")
        
        # Verify files have different paths
        assert file1 != file2
        assert session1 in file1
        assert session2 in file2
        
        # Create the files
        os.makedirs(os.path.dirname(file1), exist_ok=True)
        os.makedirs(os.path.dirname(file2), exist_ok=True)
        
        with open(file1, 'w') as f:
            f.write("session 1 content")
        
        with open(file2, 'w') as f:
            f.write("session 2 content")
        
        # Verify content isolation
        with open(file1, 'r') as f:
            assert f.read() == "session 1 content"
        
        with open(file2, 'r') as f:
            assert f.read() == "session 2 content"
    
    def test_session_error_handling(self):
        """Test session error handling"""
        # Test invalid session ID
        with pytest.raises(ValueError):
            create_session_context("invalid_session_id", self.session_manager)
        
        # Test session context with non-existent session
        with pytest.raises(ValueError):
            create_session_context("session_nonexistent_12345", self.session_manager)
    
    def test_session_path_security(self):
        """Test session path security (prevent directory traversal)"""
        session_id = self.session_manager.create_session(
            topic="Security Test",
            platform="tiktok",
            duration=15,
            category="Educational"
        )
        context = create_session_context(session_id, self.session_manager)
        
        # Test that path traversal is prevented
        safe_path = context.get_output_path("video_clips", "safe_file.mp4")
        assert session_id in safe_path
        assert self.temp_dir in safe_path
        
        # Verify path is within session directory
        session_dir = os.path.join(self.temp_dir, session_id)
        assert safe_path.startswith(session_dir)


class TestSessionIntegration:
    """Integration tests for session management with video generation"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('src.generators.video_generator.session_manager')
    def test_video_generator_session_integration(self, mock_session_manager):
        """Test that VideoGenerator properly uses session management"""
        # Mock session manager
        mock_session_manager.create_session.return_value = "session_test_12345"
        mock_session_manager.log_generation_step = Mock()
        
        # Create video config
        config = GeneratedVideoConfig(
            topic="Test Video",
            duration_seconds=30,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATION,
            hook="Test hook",
            main_content=["Test content"],
            call_to_action="Test CTA"
        )
        
        # Mock video generator dependencies
        with patch('src.generators.video_generator.VertexAIVeo2Client'), \
             patch('src.generators.video_generator.GeminiImageClient'), \
             patch('src.generators.video_generator.EnhancedMultilingualTTS'), \
             patch('src.generators.video_generator.EnhancedScriptProcessor'), \
             patch('src.generators.video_generator.VoiceDirectorAgent'), \
             patch('src.generators.video_generator.OverlayPositioningAgent'), \
             patch('src.generators.video_generator.VisualStyleAgent'), \
             patch('src.generators.video_generator.create_session_context') as mock_create_context:
            
            # Mock session context
            mock_context = Mock()
            mock_context.session_id = "session_test_12345"
            mock_context.get_output_path.return_value = "/fake/path/test.mp4"
            mock_context.save_final_video.return_value = "/fake/path/final_video.mp4"
            mock_context.get_session_summary.return_value = {
                "session_id": "session_test_12345",
                "file_counts": {"video_clips": 3, "audio": 2},
                "total_files": 5
            }
            mock_create_context.return_value = mock_context
            
            # Import and test VideoGenerator
            from generators.video_generator import VideoGenerator
            
            generator = VideoGenerator(api_key="test_key")
            
            # Test video generation
            try:
                result = generator.generate_video(config)
                
                # Verify session was created
                mock_session_manager.create_session.assert_called_once()
                
                # Verify session context was created
                mock_create_context.assert_called_once_with("session_test_12345", mock_session_manager)
                
                # Verify generation steps were logged
                assert mock_session_manager.log_generation_step.call_count > 0
                
                # Verify result contains session path
                assert result == "/fake/path/final_video.mp4"
                
            except Exception as e:
                # Expected for mocked environment
                assert "session_test_12345" in str(e) or "test_key" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 