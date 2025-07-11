"""
Comprehensive End-to-End System Test
Tests the complete video generation workflow with all components
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import time

# Import core components
from src.generators.video_generator import VideoGenerator
from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
from src.generators.gemini_image_client import GeminiImageClient
from src.generators.enhanced_multilang_tts import EnhancedMultilingualTTS
from src.utils.session_manager import SessionManager
from src.utils.session_context import SessionContext
from src.agents.voice_director_agent import VoiceDirectorAgent
from src.agents.overlay_positioning_agent import OverlayPositioningAgent
from src.agents.visual_style_agent import VisualStyleAgent
from src.generators.enhanced_script_processor import EnhancedScriptProcessor

# Import clean architecture components
from src.core.entities.video_entity import VideoEntity
from src.core.entities.session_entity import SessionEntity
from src.core.entities.agent_entity import AgentEntity
from src.core.use_cases.video_generation_use_case import VideoGenerationUseCase
from src.core.use_cases.session_management_use_case import SessionManagementUseCase
from src.infrastructure.container import DIContainer

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
        container = DIContainer()
        container.configure({
            'output_dir': test_output_dir,
            'session_storage_path': os.path.join(test_output_dir, 'sessions'),
            'video_storage_path': os.path.join(test_output_dir, 'videos'),
            'agent_storage_path': os.path.join(test_output_dir, 'agents')
        })
        return container
    
    def test_complete_video_generation_workflow(self, test_output_dir, mock_api_keys, di_container):
        """Test complete video generation workflow from start to finish"""
        
        # Test parameters
        mission = "Smart technology in wellness"
        platform = "youtube"
        duration = 30
        style = "educational"
        tone = "professional"
        target_audience = "medical professionals"
        visual_style = "clean and modern"
        
        # Mock VEO responses to simulate content policy violations and recovery
        mock_veo_responses = [
            # First attempt - content policy violation
            {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 1,
                    "raiMediaFilteredReasons": ["Content filtered due to policy violation"]
                }
            },
            # Second attempt (rephrasing) - success
            {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 0,
                    "videos": [
                        {
                            "gcsUri": "gs://test-bucket/test-video.mp4",
                            "mimeType": "video/mp4"
                        }
                    ]
                }
            }
        ]
        
        with patch('src.generators.vertex_ai_veo2_client.requests.post') as mock_post:
            # Mock API responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = mock_veo_responses
            mock_post.return_value = mock_response
            
            # Mock GCS download
            with patch('src.generators.vertex_ai_veo2_client.subprocess.run') as mock_gsutil:
                mock_gsutil.return_value.returncode = 0
                
                # Mock file creation
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.write = Mock()
                    
                    # Initialize clean architecture components
                    video_use_case = di_container.get_video_generation_use_case()
                    session_use_case = di_container.get_session_management_use_case()
                    
                    # Test session creation
                    session_entity = session_use_case.create_session(
                        mission=mission,
                        platform=platform,
                        duration=duration,
                        style=style,
                        tone=tone,
                        target_audience=target_audience,
                        visual_style=visual_style
                    )
                    
                    assert session_entity is not None
                    assert session_entity.mission == mission
                    assert session_entity.platform == platform
                    assert session_entity.status == "active"
                    
                    # Test video generation with content policy recovery
                    video_entity = video_use_case.generate_video(
                        session_id=session_entity.session_id,
                        mission=mission,
                        platform=platform,
                        duration=duration,
                        style=style,
                        tone=tone,
                        target_audience=target_audience,
                        visual_style=visual_style
                    )
                    
                    assert video_entity is not None
                    assert video_entity.mission == mission
                    assert video_entity.platform == platform
                    assert video_entity.duration == duration
                    assert video_entity.status == "completed"
                    
                    # Verify content policy recovery was triggered
                    assert mock_post.call_count >= 2  # At least one retry
                    
                    # Test session completion
                    completed_session = session_use_case.complete_session(
                        session_entity.session_id,
                        video_entity.video_id
                    )
                    
                    assert completed_session.status == "completed"
                    assert video_entity.video_id in completed_session.generated_videos
    
    def test_content_policy_violation_recovery_system(self, test_output_dir, mock_api_keys):
        """Test the multi-strategy content policy violation recovery system"""
        
        # Initialize VEO client
        veo_client = VertexAIVeo2Client(
            project_id='test-project',
            location='us-central1',
            gcs_bucket='test-bucket',
            output_dir=test_output_dir
        )
        
        # Mock multiple violation responses followed by success
        violation_responses = [
            # Original prompt violation
            {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 1,
                    "raiMediaFilteredReasons": ["Content filtered - healthcare content"]
                }
            },
            # First rephrasing attempt violation
            {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 1,
                    "raiMediaFilteredReasons": ["Content filtered - medical terminology"]
                }
            },
            # Second rephrasing attempt violation
            {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 1,
                    "raiMediaFilteredReasons": ["Content filtered - AI terminology"]
                }
            },
            # Safe prompt strategy success
            {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 0,
                    "videos": [
                        {
                            "gcsUri": "gs://test-bucket/safe-video.mp4",
                            "mimeType": "video/mp4"
                        }
                    ]
                }
            }
        ]
        
        with patch('src.generators.vertex_ai_veo2_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = violation_responses
            mock_post.return_value = mock_response
            
            # Mock GCS download
            with patch('src.generators.vertex_ai_veo2_client.subprocess.run') as mock_gsutil:
                mock_gsutil.return_value.returncode = 0
                
                # Create test video file
                test_video_path = os.path.join(test_output_dir, 'test_video.mp4')
                with open(test_video_path, 'wb') as f:
                    f.write(b'fake video content')
                
                with patch('src.generators.vertex_ai_veo2_client.os.path.exists', return_value=True):
                    with patch('src.generators.vertex_ai_veo2_client.os.path.getsize', return_value=1024*1024):
                        # Test content policy recovery
                        result = veo_client.generate_video_clip(
                            prompt="AI in healthcare diagnosis and treatment",
                            duration=5.0,
                            clip_id="test_clip",
                            aspect_ratio="16:9"
                        )
                        
                        # Verify recovery system was triggered
                        assert mock_post.call_count >= 4  # Original + 3 rephrasing + safe prompts
                        assert result is not None
                        assert "test_clip" in result
    
    def test_session_management_integration(self, test_output_dir, mock_api_keys, di_container):
        """Test session management integration with video generation"""
        
        session_use_case = di_container.get_session_management_use_case()
        
        # Test session creation
        session = session_use_case.create_session(
            mission="Test mission",
            platform="youtube",
            duration=30,
            style="educational",
            tone="professional",
            target_audience="professionals",
            visual_style="modern"
        )
        
        assert session is not None
        assert session.status == "active"
        assert len(session.path_structure) > 0
        
        # Test progress tracking
        session_use_case.update_progress(session.session_id, "video_generation", "in_progress")
        updated_session = session_use_case.get_session(session.session_id)
        assert updated_session.progress["video_generation"] == "in_progress"
        
        # Test session completion
        completed_session = session_use_case.complete_session(session.session_id, "test_video_id")
        assert completed_session.status == "completed"
        assert "test_video_id" in completed_session.generated_videos
    
    def test_ai_agents_integration(self, test_output_dir, mock_api_keys):
        """Test AI agents integration and decision making"""
        
        # Initialize agents
        voice_agent = VoiceDirectorAgent()
        style_agent = VisualStyleAgent()
        positioning_agent = OverlayPositioningAgent()
        
        # Mock Gemini responses for agent decisions
        mock_gemini_responses = [
            # Voice agent response
            {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": json.dumps({
                                "strategy": "narrator_character",
                                "primary_personality": "professional",
                                "multiple_voices": True,
                                "reasoning": "Educational content requires professional narrator"
                            })
                        }]
                    }
                }]
            },
            # Style agent response
            {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": json.dumps({
                                "primary_style": "professional",
                                "color_palette": "clean",
                                "engagement_prediction": "high",
                                "reasoning": "Professional style matches target audience"
                            })
                        }]
                    }
                }]
            },
            # Positioning agent response
            {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": json.dumps({
                                "positioning": "bottom_third",
                                "strategy": "static",
                                "reasoning": "Bottom third positioning ensures readability"
                            })
                        }]
                    }
                }]
            }
        ]
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = mock_gemini_responses
            mock_post.return_value = mock_response
            
            # Test voice agent decision
            voice_config = voice_agent.analyze_content_and_select_voices(
                content="Educational content about technology",
                platform="youtube",
                duration=30
            )
            
            assert voice_config is not None
            assert "strategy" in voice_config
            
            # Test style agent decision
            style_decision = style_agent.analyze_optimal_style(
                mission="Technology education",
                target_audience="professionals",
                platform="youtube"
            )
            
            assert style_decision is not None
            assert "primary_style" in style_decision
            
            # Test positioning agent decision
            positioning_decision = positioning_agent.analyze_optimal_positioning(
                mission="Technology education",
                platform="youtube",
                style="professional",
                duration=30
            )
            
            assert positioning_decision is not None
            assert "positioning" in positioning_decision
    
    def test_error_handling_and_resilience(self, test_output_dir, mock_api_keys):
        """Test error handling and system resilience"""
        
        # Initialize components
        veo_client = VertexAIVeo2Client(
            project_id='test-project',
            location='us-central1',
            gcs_bucket='test-bucket',
            output_dir=test_output_dir
        )
        
        # Test API failure handling
        with patch('src.generators.vertex_ai_veo2_client.requests.post') as mock_post:
            # Simulate API failure
            mock_post.side_effect = Exception("API connection failed")
            
            # Test fallback creation
            result = veo_client.generate_video_clip(
                prompt="Test prompt",
                duration=5.0,
                clip_id="test_clip"
            )
            
            # Should create fallback video
            assert result is not None
            assert "test_clip" in result
    
    def test_performance_benchmarks(self, test_output_dir, mock_api_keys):
        """Test system performance benchmarks"""
        
        start_time = time.time()
        
        # Mock fast responses
        with patch('src.generators.vertex_ai_veo2_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 0,
                    "videos": [
                        {
                            "gcsUri": "gs://test-bucket/test-video.mp4",
                            "mimeType": "video/mp4"
                        }
                    ]
                }
            }
            mock_post.return_value = mock_response
            
            # Mock file operations
            with patch('src.generators.vertex_ai_veo2_client.subprocess.run') as mock_gsutil:
                mock_gsutil.return_value.returncode = 0
                
                with patch('src.generators.vertex_ai_veo2_client.os.path.exists', return_value=True):
                    with patch('src.generators.vertex_ai_veo2_client.os.path.getsize', return_value=1024*1024):
                        
                        # Initialize VEO client
                        veo_client = VertexAIVeo2Client(
                            project_id='test-project',
                            location='us-central1',
                            gcs_bucket='test-bucket',
                            output_dir=test_output_dir
                        )
                        
                        # Test generation speed
                        result = veo_client.generate_video_clip(
                            prompt="Test performance",
                            duration=5.0,
                            clip_id="perf_test"
                        )
                        
                        generation_time = time.time() - start_time
                        
                        # Performance assertions
                        assert result is not None
                        assert generation_time < 10.0  # Should complete within 10 seconds (mocked)
    
    def test_clean_architecture_integration(self, test_output_dir, mock_api_keys, di_container):
        """Test clean architecture integration with legacy components"""
        
        # Test that clean architecture components work with existing system
        video_use_case = di_container.get_video_generation_use_case()
        session_use_case = di_container.get_session_management_use_case()
        
        # Create session using clean architecture
        session = session_use_case.create_session(
            mission="Clean architecture test",
            platform="youtube",
            duration=30,
            style="educational",
            tone="professional",
            target_audience="developers",
            visual_style="modern"
        )
        
        assert session is not None
        assert isinstance(session, SessionEntity)
        
        # Mock video generation
        with patch('src.generators.vertex_ai_veo2_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "done": True,
                "response": {
                    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                    "raiMediaFilteredCount": 0,
                    "videos": [
                        {
                            "gcsUri": "gs://test-bucket/clean-arch-test.mp4",
                            "mimeType": "video/mp4"
                        }
                    ]
                }
            }
            mock_post.return_value = mock_response
            
            with patch('src.generators.vertex_ai_veo2_client.subprocess.run') as mock_gsutil:
                mock_gsutil.return_value.returncode = 0
                
                with patch('src.generators.vertex_ai_veo2_client.os.path.exists', return_value=True):
                    with patch('src.generators.vertex_ai_veo2_client.os.path.getsize', return_value=1024*1024):
                        
                        # Generate video using clean architecture
                        video = video_use_case.generate_video(
                            session_id=session.session_id,
                            mission="Clean architecture test",
                            platform="youtube",
                            duration=30,
                            style="educational",
                            tone="professional",
                            target_audience="developers",
                            visual_style="modern"
                        )
                        
                        assert video is not None
                        assert isinstance(video, VideoEntity)
                        assert video.status == "completed"
    
    def test_comprehensive_system_validation(self, test_output_dir, mock_api_keys, di_container):
        """Comprehensive system validation test"""
        
        # This test validates the entire system working together
        test_scenarios = [
            {
                "mission": "Smart technology in wellness",
                "platform": "youtube",
                "duration": 30,
                "style": "educational",
                "tone": "professional",
                "target_audience": "medical professionals",
                "visual_style": "clean and modern"
            },
            {
                "mission": "Sustainable energy solutions",
                "platform": "tiktok",
                "duration": 15,
                "style": "viral",
                "tone": "engaging",
                "target_audience": "young adults",
                "visual_style": "dynamic"
            },
            {
                "mission": "Financial literacy basics",
                "platform": "instagram",
                "duration": 20,
                "style": "professional",
                "tone": "informative",
                "target_audience": "professionals",
                "visual_style": "minimalist"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios):
            with patch('src.generators.vertex_ai_veo2_client.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "done": True,
                    "response": {
                        "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
                        "raiMediaFilteredCount": 0,
                        "videos": [
                            {
                                "gcsUri": f"gs://test-bucket/scenario-{i}.mp4",
                                "mimeType": "video/mp4"
                            }
                        ]
                    }
                }
                mock_post.return_value = mock_response
                
                with patch('src.generators.vertex_ai_veo2_client.subprocess.run') as mock_gsutil:
                    mock_gsutil.return_value.returncode = 0
                    
                    with patch('src.generators.vertex_ai_veo2_client.os.path.exists', return_value=True):
                        with patch('src.generators.vertex_ai_veo2_client.os.path.getsize', return_value=1024*1024):
                            
                            # Test each scenario
                            video_use_case = di_container.get_video_generation_use_case()
                            session_use_case = di_container.get_session_management_use_case()
                            
                            # Create session
                            session = session_use_case.create_session(**scenario)
                            assert session is not None
                            
                            # Generate video
                            video = video_use_case.generate_video(
                                session_id=session.session_id,
                                **scenario
                            )
                            
                            assert video is not None
                            assert video.status == "completed"
                            assert video.platform == scenario["platform"]
                            assert video.duration == scenario["duration"]
                            
                            # Complete session
                            completed_session = session_use_case.complete_session(
                                session.session_id,
                                video.video_id
                            )
                            
                            assert completed_session.status == "completed"
                            assert video.video_id in completed_session.generated_videos


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 