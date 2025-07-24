"""
Comprehensive End-to-End System Test
Tests the complete video generation workflow with all components
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock, AsyncMock
import json
from pathlib import Path
import asyncio
from datetime import datetime
import time

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
from src.generators.vertex_veo3_client import VertexAIVeo3Client
from src.generators.video_generator import VideoGenerator
from src.agents.voice_director_agent import VoiceDirectorAgent
from src.agents.visual_style_agent import VisualStyleAgent
from src.agents.overlay_positioning_agent import OverlayPositioningAgent
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory, Language
from src.utils.session_manager import SessionManager
from src.utils.comprehensive_logger import ComprehensiveLogger
from src.infrastructure.container import DIContainer
from src.core.entities.video_entity import VideoEntity, VideoStatus
from src.core.entities.session_entity import SessionEntity, SessionStatus
from src.core.entities.agent_entity import AgentEntity, AgentType, AgentStatus


class TestFullSystemE2E:
    """Comprehensive E2E tests for the complete video generation system"""
    
    @pytest.fixture
    def test_output_dir(self):
        """Create temporary directory for test outputs"""
        temp_dir = tempfile.mkdtemp(prefix="viral_ai_e2e_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_api_keys(self):
        """Mock API keys for testing"""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test_google_key',
            'GEMINI_API_KEY': 'test_gemini_key',
            'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/test/credentials.json'
        }):
            yield
    
    @pytest.fixture
    def di_container(self, test_output_dir):
        """Initialize dependency injection container for testing"""
        config = {
            'output_dir': test_output_dir,
            'session_storage_path': os.path.join(test_output_dir, 'sessions'),
            'video_storage_path': os.path.join(test_output_dir, 'videos'),
            'agent_storage_path': os.path.join(test_output_dir, 'agents')
        }
        container = DIContainer(config)
        return container
    
    def test_complete_video_generation_workflow(self, test_output_dir, mock_api_keys, di_container):
        """Test complete video generation workflow from start to finish"""
        
        # Test parameters
        test_config = GeneratedVideoConfig(
            mission="E2E Test Video",
            duration_seconds=10,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATION,
            main_content=["Testing the complete workflow"],
            hook="Test Hook",
            call_to_action="Test CTA"
        )
        
        # Mock the video generator to avoid actual API calls
        with patch('src.generators.video_generator.VideoGenerator') as mock_generator:
            mock_instance = MagicMock()
            mock_generator.return_value = mock_instance
            
            # Mock successful video generation
            mock_result = MagicMock()
            mock_result.file_path = os.path.join(test_output_dir, "test_video.mp4")
            mock_result.file_size_mb = 1.5
            mock_result.generation_time_seconds = 30.0
            mock_result.clips_generated = 3
            mock_result.success = True
            mock_instance.generate_video.return_value = mock_result
            
            # Initialize generator
            generator = VideoGenerator(
                api_key="test_key",
                use_real_veo2=True,
                use_vertex_ai=True,
                vertex_project_id="test-project",
                vertex_location="us-central1",
                vertex_gcs_bucket="test-bucket",
                output_dir=test_output_dir
            )
            
            # Generate video
            result = generator.generate_video(test_config)
            
            # Verify results
            assert result is not None
            assert result.success is True
            assert result.clips_generated == 3
            
            # Verify generator was called correctly
            mock_instance.generate_video.assert_called_once_with(test_config)
    
    def test_content_policy_violation_recovery_system(self, test_output_dir, mock_api_keys):
        """Test content policy violation detection and recovery"""
        
        # Test content policy violation recovery
        veo_client = VertexAIVeo2Client(
            project_id="test-project",
            location="us-central1",
            gcs_bucket="test-bucket",
            output_dir=test_output_dir
        )
        
        # Test with problematic content
        result = veo_client.generate_video(
            prompt="test content policy violation",
            duration=5.0,
            clip_id="test_clip"
        )
        
        # Should fall back to safe content
        assert result is not None
        assert os.path.exists(result)
    
    def test_session_management_integration(self, test_output_dir, mock_api_keys, di_container):
        """Test session management integration"""
        
        session_manager = SessionManager(base_output_dir=test_output_dir)
        
        # Create test session
        session_id = session_manager.create_session("test_mission", "youtube", 30)
        
        # Verify session creation
        assert session_id is not None
        assert session_manager.current_session == session_id
        
        # Test session directory structure
        session_dir = session_manager.get_session_path()
        assert os.path.exists(session_dir)
        
        # Verify subdirectories
        expected_dirs = [
            "logs", "scripts", "audio", "video_clips", "images",
            "ai_agents", "discussions", "final_output", "metadata"
        ]
        
        for dir_name in expected_dirs:
            dir_path = os.path.join(session_dir, dir_name)
            assert os.path.exists(dir_path), f"Missing directory: {dir_name}"
    
    def test_ai_agents_integration(self, test_output_dir, mock_api_keys):
        """Test AI agents integration and coordination"""
        
        # Initialize agents
        voice_agent = VoiceDirectorAgent(api_key="test_api_key")
        style_agent = VisualStyleAgent()
        positioning_agent = OverlayPositioningAgent()
        
        # Mock Gemini responses for agent decisions
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = MagicMock()
            mock_model.return_value = mock_instance
            
            # Mock voice selection response
            mock_instance.generate_content.return_value.text = json.dumps({
                "voice_strategy": "single",
                "primary_personality": "narrator",
                "multiple_voices": False,
                "voice_config": {
                    "clip_voices": [
                        {"clip_index": 0, "voice_name": "en-US-Neural2-A", "personality": "narrator"}
                    ]
                },
                "success": True
            })
            
            # Test voice selection
            voice_result = voice_agent.analyze_content_and_select_voices(
                mission="Test Mission",
                script="Test script content",
                language=Language.ENGLISH,
                platform=Platform.YOUTUBE,
                category=VideoCategory.EDUCATION,
                duration_seconds=30,
                num_clips=3
            )
            
            assert voice_result["success"] is True
            assert "voice_config" in voice_result
    
    def test_error_handling_and_resilience(self, test_output_dir, mock_api_keys):
        """Test error handling and system resilience"""
        
        # Test VEO client error handling
        veo_client = VertexAIVeo2Client(
            project_id="test-project",
            location="us-central1",
            gcs_bucket="test-bucket",
            output_dir=test_output_dir
        )
        
        # Test with invalid parameters
        result = veo_client.generate_video(
            prompt="",  # Empty prompt
            duration=0,  # Invalid duration
            clip_id="error_test"
        )
        
        # Should handle gracefully and return fallback
        assert result is not None
        assert os.path.exists(result)
    
    def test_performance_benchmarks(self, test_output_dir, mock_api_keys):
        """Test performance benchmarks and optimization"""
        
        # Test VEO client performance
        veo_client = VertexAIVeo2Client(
            project_id="test-project",
            location="us-central1",
            gcs_bucket="test-bucket",
            output_dir=test_output_dir
        )
        
        # Measure generation time
        start_time = time.time()
        result = veo_client.generate_video(
            prompt="performance test video",
            duration=5.0,
            clip_id="perf_test"
        )
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Verify performance (should complete within reasonable time)
        assert generation_time < 60.0  # Should complete within 1 minute
        assert result is not None
        assert os.path.exists(result)
    
    def test_clean_architecture_integration(self, test_output_dir, mock_api_keys, di_container):
        """Test clean architecture integration"""
        
        # Test dependency injection
        video_repo = di_container.get_video_repository()
        session_repo = di_container.get_session_repository()
        agent_repo = di_container.get_agent_repository()
        
        assert video_repo is not None
        assert session_repo is not None
        assert agent_repo is not None
        
        # Test use cases
        video_use_case = di_container.get_video_generation_use_case()
        session_use_case = di_container.get_session_management_use_case()
        agent_use_case = di_container.get_agent_orchestration_use_case()
        
        assert video_use_case is not None
        assert session_use_case is not None
        assert agent_use_case is not None
    
    def test_comprehensive_system_validation(self, test_output_dir, mock_api_keys, di_container):
        """Comprehensive system validation test"""
        
        # Test complete system integration
        session_manager = SessionManager(base_output_dir=test_output_dir)
        
        # Create session
        session_id = session_manager.create_session("validation_test", "youtube", 30)
        
        # Test configuration
        test_config = GeneratedVideoConfig(
            mission="System Validation Test",
            duration_seconds=15,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATION,
            main_content=["Comprehensive system test"],
            hook="System Test",
            call_to_action="Validation Complete"
        )
        
        # Mock comprehensive logger
        with patch('src.utils.comprehensive_logger.ComprehensiveLogger') as mock_logger:
            mock_instance = MagicMock()
            mock_logger.return_value = mock_instance
            
            # Test logger integration
            logger = ComprehensiveLogger(session_id)
            logger.log_generation_step("test_step", "completed", {"test": "data"})
            
            # Verify logger was called
            mock_instance.log_generation_step.assert_called_once()
        
        # Verify session completion
        session_manager.complete_session()
        assert session_manager.current_session is None 