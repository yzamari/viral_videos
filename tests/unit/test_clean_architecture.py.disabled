"""
Unit tests for clean architecture components
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

# Add src to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.entities.video_entity import VideoEntity, VideoStatus, Platform, VideoMetadata
from src.core.entities.session_entity import SessionEntity, SessionStatus
from src.core.entities.agent_entity import AgentEntity, AgentType, AgentStatus
from src.core.use_cases.video_generation_use_case import VideoGenerationUseCase
from src.infrastructure.repositories.file_video_repository import FileVideoRepository
from src.infrastructure.repositories.file_session_repository import FileSessionRepository
from src.infrastructure.repositories.file_agent_repository import FileAgentRepository
from src.infrastructure.services.existing_video_generation_service import ExistingVideoGenerationService
from src.infrastructure.services.existing_script_generation_service import ExistingScriptGenerationService
from src.infrastructure.services.existing_audio_generation_service import ExistingAudioGenerationService
from src.infrastructure.container import DIContainer, get_container, reset_container


class TestVideoEntity:
    """Test video entity"""
    
    def test_video_entity_creation(self):
        """Test video entity creation"""
        video = VideoEntity(
            id="test_video_1",
            session_id="test_session_1",
            mission="Test video about AI",
            platform=Platform.YOUTUBE
        )
        
        assert video.id == "test_video_1"
        assert video.session_id == "test_session_1"
        assert video.mission == "Test video about AI"
        assert video.platform == Platform.YOUTUBE
        assert video.status == VideoStatus.PENDING
        assert video.progress_percentage == 0.0
        assert video.current_stage == "initialized"
    
    def test_video_entity_validation(self):
        """Test video entity validation"""
        with pytest.raises(ValueError, match="Mission cannot be empty"):
            VideoEntity(
                id="test_video_1",
                session_id="test_session_1",
                mission="",
                platform=Platform.YOUTUBE
            )
        
        with pytest.raises(ValueError, match="Video ID cannot be empty"):
            VideoEntity(
                id="",
                session_id="test_session_1",
                mission="Test mission",
                platform=Platform.YOUTUBE
            )
    
    def test_video_entity_lifecycle(self):
        """Test video entity lifecycle"""
        video = VideoEntity(
            id="test_video_1",
            session_id="test_session_1",
            mission="Test video about AI",
            platform=Platform.YOUTUBE
        )
        
        # Start generation
        video.start_generation()
        assert video.status == VideoStatus.GENERATING
        assert video.current_stage == "script_generation"
        
        # Update progress
        video.update_progress(50.0, "audio_generation")
        assert video.progress_percentage == 50.0
        assert video.current_stage == "audio_generation"
        
        # Complete generation
        video.complete_generation("/path/to/final/video.mp4")
        assert video.status == VideoStatus.COMPLETED
        assert video.final_video_path == "/path/to/final/video.mp4"
        assert video.progress_percentage == 100.0
        assert video.completed_at is not None
    
    def test_video_entity_serialization(self):
        """Test video entity serialization"""
        video = VideoEntity(
            id="test_video_1",
            session_id="test_session_1",
            mission="Test video about AI",
            platform=Platform.YOUTUBE
        )
        
        # Test to_dict
        video_dict = video.to_dict()
        assert video_dict["id"] == "test_video_1"
        assert video_dict["platform"] == "youtube"
        assert video_dict["status"] == "pending"
        
        # Test from_dict
        video_restored = VideoEntity.from_dict(video_dict)
        assert video_restored.id == video.id
        assert video_restored.platform == video.platform
        assert video_restored.status == video.status


class TestSessionEntity:
    """Test session entity"""
    
    def test_session_entity_creation(self):
        """Test session entity creation"""
        session = SessionEntity(
            id="test_session_1",
            name="Test Session"
        )
        
        assert session.id == "test_session_1"
        assert session.name == "Test Session"
        assert session.status == SessionStatus.ACTIVE
        assert session.total_videos == 0
        assert session.completed_videos == 0
    
    def test_session_entity_video_management(self):
        """Test session entity video management"""
        session = SessionEntity(
            id="test_session_1",
            name="Test Session"
        )
        
        # Add videos
        session.add_video("video_1")
        session.add_video("video_2")
        
        assert session.total_videos == 2
        assert "video_1" in session.video_ids
        assert "video_2" in session.video_ids
        
        # Mark video completed
        session.mark_video_completed("video_1")
        assert session.completed_videos == 1
        
        # Mark video failed
        session.mark_video_failed("video_2")
        assert session.failed_videos == 1
    
    def test_session_entity_completion_rate(self):
        """Test session entity completion rate"""
        session = SessionEntity(
            id="test_session_1",
            name="Test Session"
        )
        
        session.add_video("video_1")
        session.add_video("video_2")
        session.add_video("video_3")
        
        session.mark_video_completed("video_1")
        session.mark_video_completed("video_2")
        
        assert session.get_completion_rate() == 66.67  # 2/3 * 100
        assert session.get_failure_rate() == 0.0


class TestAgentEntity:
    """Test agent entity"""
    
    def test_agent_entity_creation(self):
        """Test agent entity creation"""
        agent = AgentEntity(
            id="test_agent_1",
            name="Test Director",
            agent_type=AgentType.DIRECTOR
        )
        
        assert agent.id == "test_agent_1"
        assert agent.name == "Test Director"
        assert agent.agent_type == AgentType.DIRECTOR
        assert agent.status == AgentStatus.IDLE
        assert agent.expertise_level == 1.0
    
    def test_agent_entity_assignment(self):
        """Test agent entity assignment"""
        agent = AgentEntity(
            id="test_agent_1",
            name="Test Director",
            agent_type=AgentType.DIRECTOR
        )
        
        # Assign to session
        agent.assign_to_session("session_1", "video_1")
        assert agent.session_id == "session_1"
        assert agent.video_id == "video_1"
        assert agent.status == AgentStatus.WORKING
        
        # Start task
        agent.start_task("Generate script")
        assert agent.current_task == "Generate script"
        assert agent.current_task_progress == 0.0
        
        # Update progress
        agent.update_task_progress(50.0)
        assert agent.current_task_progress == 50.0
        
        # Complete task
        agent.complete_task()
        assert agent.status == AgentStatus.COMPLETED
        assert agent.current_task is None
    
    def test_agent_entity_decisions(self):
        """Test agent entity decision making"""
        agent = AgentEntity(
            id="test_agent_1",
            name="Test Director",
            agent_type=AgentType.DIRECTOR
        )
        
        # Make decision
        decision_id = agent.make_decision(
            decision_type="script_style",
            decision_data={"style": "viral", "tone": "engaging"},
            confidence_score=0.85,
            reasoning="Based on platform and audience analysis"
        )
        
        assert decision_id is not None
        assert agent.total_decisions == 1
        assert agent.average_confidence_score == 0.85
        
        # Mark decision successful
        agent.mark_decision_successful(decision_id)
        assert agent.successful_decisions == 1
        assert agent.get_success_rate() == 100.0


class TestFileRepositories:
    """Test file-based repositories"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.video_repo = FileVideoRepository(base_path=f"{self.temp_dir}/videos")
        self.session_repo = FileSessionRepository(base_path=f"{self.temp_dir}/sessions")
        self.agent_repo = FileAgentRepository(base_path=f"{self.temp_dir}/agents")
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_video_repository_crud(self):
        """Test video repository CRUD operations"""
        # Create video
        video = VideoEntity(
            id="test_video_1",
            session_id="test_session_1",
            mission="Test video about AI",
            platform=Platform.YOUTUBE
        )
        
        # Save video
        await self.video_repo.save(video)
        
        # Get video
        retrieved_video = await self.video_repo.get_by_id("test_video_1")
        assert retrieved_video is not None
        assert retrieved_video.id == "test_video_1"
        assert retrieved_video.mission == "Test video about AI"
        
        # List videos
        all_videos = await self.video_repo.list_all()
        assert len(all_videos) == 1
        assert all_videos[0].id == "test_video_1"
        
        # Delete video
        await self.video_repo.delete("test_video_1")
        deleted_video = await self.video_repo.get_by_id("test_video_1")
        assert deleted_video is None
    
    @pytest.mark.asyncio
    async def test_session_repository_crud(self):
        """Test session repository CRUD operations"""
        # Create session
        session = SessionEntity(
            id="test_session_1",
            name="Test Session"
        )
        
        # Save session
        await self.session_repo.save(session)
        
        # Get session
        retrieved_session = await self.session_repo.get_by_id("test_session_1")
        assert retrieved_session is not None
        assert retrieved_session.id == "test_session_1"
        assert retrieved_session.name == "Test Session"
        
        # List active sessions
        active_sessions = await self.session_repo.list_active()
        assert len(active_sessions) == 1
        assert active_sessions[0].id == "test_session_1"


class TestServices:
    """Test service implementations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.video_service = ExistingVideoGenerationService(output_base_path=self.temp_dir)
        self.script_service = ExistingScriptGenerationService()
        self.audio_service = ExistingAudioGenerationService(output_base_path=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_script_generation_service(self):
        """Test script generation service"""
        script_content = await self.script_service.generate_script(
            mission="AI in healthcare",
            platform=Platform.YOUTUBE,
            duration_seconds=30,
            config={"style": "educational", "tone": "professional"}
        )
        
        assert script_content is not None
        assert "hook" in script_content
        assert "segments" in script_content
        assert "call_to_action" in script_content
        assert script_content["total_duration"] == 30
        assert script_content["style"] == "educational"
        assert script_content["tone"] == "professional"
    
    @pytest.mark.asyncio
    async def test_audio_generation_service(self):
        """Test audio generation service"""
        script_content = {
            "hook": {"text": "Amazing AI insights!", "duration_seconds": 3},
            "segments": [
                {"text": "AI is transforming healthcare", "duration_seconds": 10},
                {"text": "Machine learning improves diagnosis", "duration_seconds": 12}
            ],
            "call_to_action": "Subscribe for more AI content!"
        }
        
        audio_files = await self.audio_service.generate_audio(
            script_content=script_content,
            config={"session_id": "test_session", "voice": "en-US-Standard-A"}
        )
        
        assert len(audio_files) == 3  # hook + 2 segments + call_to_action
        assert all(file.endswith('.mp3') for file in audio_files)
    
    @pytest.mark.asyncio
    async def test_video_generation_service(self):
        """Test video generation service"""
        script_content = {
            "hook": {"text": "Amazing AI insights!", "duration_seconds": 3},
            "segments": [
                {"text": "AI is transforming healthcare", "duration_seconds": 10}
            ]
        }
        
        video_clips, image_files = await self.video_service.generate_content(
            script_content=script_content,
            platform=Platform.YOUTUBE,
            config={"session_id": "test_session"}
        )
        
        assert len(video_clips) == 2  # hook + 1 segment
        assert len(image_files) == 2  # hook + 1 segment
        assert all(file.endswith('.mp4') for file in video_clips)
        assert all(file.endswith('.jpg') for file in image_files)


class TestDIContainer:
    """Test dependency injection container"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        reset_container()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
        reset_container()
    
    def test_container_initialization(self):
        """Test container initialization"""
        config = {
            "data_path": f"{self.temp_dir}/data",
            "output_path": f"{self.temp_dir}/outputs"
        }
        
        container = DIContainer(config)
        
        # Test repository access
        video_repo = container.get_video_repository()
        assert video_repo is not None
        
        session_repo = container.get_session_repository()
        assert session_repo is not None
        
        agent_repo = container.get_agent_repository()
        assert agent_repo is not None
        
        # Test service access
        video_service = container.get_video_generation_service()
        assert video_service is not None
        
        script_service = container.get_script_generation_service()
        assert script_service is not None
        
        audio_service = container.get_audio_generation_service()
        assert audio_service is not None
        
        # Test use case access
        video_use_case = container.get_video_generation_use_case()
        assert video_use_case is not None
    
    def test_global_container(self):
        """Test global container access"""
        config = {
            "data_path": f"{self.temp_dir}/data",
            "output_path": f"{self.temp_dir}/outputs"
        }
        
        container1 = get_container(config)
        container2 = get_container()
        
        # Should be the same instance
        assert container1 is container2
        
        # Test configuration
        assert container1.get_config()["data_path"] == f"{self.temp_dir}/data"


class TestVideoGenerationUseCase:
    """Test video generation use case"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Setup repositories
        self.video_repo = FileVideoRepository(base_path=f"{self.temp_dir}/videos")
        self.session_repo = FileSessionRepository(base_path=f"{self.temp_dir}/sessions")
        self.agent_repo = FileAgentRepository(base_path=f"{self.temp_dir}/agents")
        
        # Setup services
        self.video_service = ExistingVideoGenerationService(output_base_path=f"{self.temp_dir}/outputs")
        self.script_service = ExistingScriptGenerationService()
        self.audio_service = ExistingAudioGenerationService(output_base_path=f"{self.temp_dir}/outputs")
        
        # Setup use case
        self.use_case = VideoGenerationUseCase(
            video_repository=self.video_repo,
            session_repository=self.session_repo,
            agent_repository=self.agent_repo,
            video_generation_service=self.video_service,
            script_generation_service=self.script_service,
            audio_generation_service=self.audio_service
        )
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_create_video_generation_request(self):
        """Test creating video generation request"""
        # Create session first
        session = SessionEntity(
            id="test_session_1",
            name="Test Session"
        )
        await self.session_repo.save(session)
        
        # Create video generation request
        video = await self.use_case.create_video_generation_request(
            session_id="test_session_1",
            mission="AI in healthcare",
            platform=Platform.YOUTUBE,
            generation_config={
                "duration_seconds": 30,
                "style": "educational",
                "tone": "professional"
            }
        )
        
        assert video is not None
        assert video.session_id == "test_session_1"
        assert video.mission == "AI in healthcare"
        assert video.platform == Platform.YOUTUBE
        assert video.status == VideoStatus.PENDING
        
        # Verify video was saved
        saved_video = await self.video_repo.get_by_id(video.id)
        assert saved_video is not None
        assert saved_video.id == video.id
        
        # Verify session was updated
        updated_session = await self.session_repo.get_by_id("test_session_1")
        assert updated_session.total_videos == 1
        assert video.id in updated_session.video_ids
    
    @pytest.mark.asyncio
    async def test_get_video_status(self):
        """Test getting video status"""
        # Create and save video
        video = VideoEntity(
            id="test_video_1",
            session_id="test_session_1",
            mission="Test video",
            platform=Platform.YOUTUBE
        )
        await self.video_repo.save(video)
        
        # Get video status
        status = await self.use_case.get_video_status("test_video_1")
        
        assert status["id"] == "test_video_1"
        assert status["status"] == "pending"
        assert status["progress_percentage"] == 0.0
        assert status["current_stage"] == "initialized"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 