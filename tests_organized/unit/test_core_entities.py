"""
Unit Tests for Core Entities
Tests all core domain entities and their business logic
"""

import unittest
import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.entities.video_entity import VideoEntity, VideoStatus, Platform, VideoMetadata
from src.core.entities.session_entity import SessionEntity, SessionStatus
from src.core.entities.agent_entity import AgentEntity, AgentType, AgentStatus, AgentDecision


class TestVideoEntity(unittest.TestCase):
    """Test VideoEntity domain logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.video_id = "test_video_001"
        self.session_id = "test_session_001"
        self.mission = "Create engaging AI content"
        
    def test_video_entity_initialization(self):
        """Test video entity initialization with valid data"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM
        )
        
        self.assertEqual(video.id, self.video_id)
        self.assertEqual(video.session_id, self.session_id)
        self.assertEqual(video.mission, self.mission)
        self.assertEqual(video.platform, Platform.INSTAGRAM)
        self.assertEqual(video.status, VideoStatus.PENDING)
        self.assertEqual(video.progress_percentage, 0.0)
        self.assertEqual(video.current_stage, "initialized")
        self.assertIsNone(video.final_video_path)
        
    def test_video_entity_validation_empty_mission(self):
        """Test video entity validation with empty mission"""
        with self.assertRaises(ValueError) as context:
            VideoEntity(
                id=self.video_id,
                session_id=self.session_id,
                mission="",
                platform=Platform.INSTAGRAM
            )
        self.assertIn("Mission cannot be empty", str(context.exception))
        
    def test_video_entity_validation_empty_id(self):
        """Test video entity validation with empty ID"""
        with self.assertRaises(ValueError) as context:
            VideoEntity(
                id="",
                session_id=self.session_id,
                mission=self.mission,
                platform=Platform.INSTAGRAM
            )
        self.assertIn("Video ID cannot be empty", str(context.exception))
        
    def test_video_entity_validation_empty_session_id(self):
        """Test video entity validation with empty session ID"""
        with self.assertRaises(ValueError) as context:
            VideoEntity(
                id=self.video_id,
                session_id="",
                mission=self.mission,
                platform=Platform.INSTAGRAM
            )
        self.assertIn("Session ID cannot be empty", str(context.exception))
        
    def test_start_generation_from_pending(self):
        """Test starting generation from pending status"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM
        )
        
        video.start_generation()
        
        self.assertEqual(video.status, VideoStatus.GENERATING)
        self.assertEqual(video.current_stage, "script_generation")
        self.assertEqual(video.progress_percentage, 0.0)
        
    def test_start_generation_from_invalid_status(self):
        """Test starting generation from invalid status"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM,
            status=VideoStatus.COMPLETED
        )
        
        with self.assertRaises(ValueError) as context:
            video.start_generation()
        self.assertIn("Cannot start generation from status", str(context.exception))
        
    def test_complete_generation_success(self):
        """Test completing generation successfully"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM,
            status=VideoStatus.GENERATING
        )
        
        video_path = "/path/to/video.mp4"
        video.complete_generation(video_path)
        
        self.assertEqual(video.status, VideoStatus.COMPLETED)
        self.assertEqual(video.final_video_path, video_path)
        self.assertEqual(video.progress_percentage, 100.0)
        self.assertEqual(video.current_stage, "completed")
        self.assertIsNotNone(video.completed_at)
        
    def test_fail_generation(self):
        """Test failing generation"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM,
            status=VideoStatus.GENERATING
        )
        
        error_msg = "Generation failed due to API error"
        video.fail_generation(error_msg)
        
        self.assertEqual(video.status, VideoStatus.FAILED)
        self.assertEqual(video.error_message, error_msg)
        self.assertEqual(video.current_stage, "failed")
        
    def test_update_progress(self):
        """Test updating generation progress"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM,
            status=VideoStatus.GENERATING
        )
        
        video.update_progress(50.0, "audio_generation")
        
        self.assertEqual(video.progress_percentage, 50.0)
        self.assertEqual(video.current_stage, "audio_generation")
        
    def test_add_video_clip(self):
        """Test adding video clip"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM
        )
        
        clip_path = "/path/to/clip.mp4"
        video.add_video_clip(clip_path)
        
        self.assertIn(clip_path, video.video_clips)
        self.assertEqual(len(video.video_clips), 1)
        
    def test_add_audio_file(self):
        """Test adding audio file"""
        video = VideoEntity(
            id=self.video_id,
            session_id=self.session_id,
            mission=self.mission,
            platform=Platform.INSTAGRAM
        )
        
        audio_path = "/path/to/audio.mp3"
        video.add_audio_file(audio_path)
        
        self.assertIn(audio_path, video.audio_files)
        self.assertEqual(len(video.audio_files), 1)


class TestSessionEntity(unittest.TestCase):
    """Test SessionEntity domain logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.session_id = "test_session_001"
        self.session_name = "Test Session"
        self.base_path = "/tmp/test_session"
        
    def test_session_entity_initialization(self):
        """Test session entity initialization"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name
        )
        
        self.assertEqual(session.id, self.session_id)
        self.assertEqual(session.name, self.session_name)
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertEqual(session.total_videos, 0)
        self.assertEqual(session.completed_videos, 0)
        self.assertEqual(session.failed_videos, 0)
        
    def test_session_entity_with_base_path(self):
        """Test session entity initialization with base path"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name,
            base_path=self.base_path
        )
        
        self.assertEqual(session.base_path, self.base_path)
        self.assertEqual(session.video_clips_path, f"{self.base_path}/video_clips")
        self.assertEqual(session.audio_path, f"{self.base_path}/audio")
        self.assertEqual(session.images_path, f"{self.base_path}/images")
        self.assertEqual(session.scripts_path, f"{self.base_path}/scripts")
        self.assertEqual(session.metadata_path, f"{self.base_path}/metadata")
        self.assertEqual(session.final_output_path, f"{self.base_path}/final_output")
        self.assertEqual(session.logs_path, f"{self.base_path}/logs")
        
    def test_session_validation_empty_id(self):
        """Test session validation with empty ID"""
        with self.assertRaises(ValueError) as context:
            SessionEntity(
                id="",
                name=self.session_name
            )
        self.assertIn("Session ID cannot be empty", str(context.exception))
        
    def test_session_validation_empty_name(self):
        """Test session validation with empty name"""
        with self.assertRaises(ValueError) as context:
            SessionEntity(
                id=self.session_id,
                name=""
            )
        self.assertIn("Session name cannot be empty", str(context.exception))
        
    def test_add_video_id(self):
        """Test adding video ID to session"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name
        )
        
        video_id = "video_001"
        session.add_video(video_id)
        
        self.assertIn(video_id, session.video_ids)
        self.assertEqual(session.total_videos, 1)
        
    def test_complete_video(self):
        """Test completing a video in session"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name
        )
        
        video_id = "video_001"
        session.add_video(video_id)
        session.mark_video_completed(video_id)
        
        self.assertEqual(session.completed_videos, 1)
        
    def test_fail_video(self):
        """Test failing a video in session"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name
        )
        
        video_id = "video_001"
        session.add_video(video_id)
        session.mark_video_failed(video_id)
        
        self.assertEqual(session.failed_videos, 1)
        
    def test_complete_session(self):
        """Test completing a session"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name
        )
        
        session.complete_session()
        
        self.assertEqual(session.status, SessionStatus.COMPLETED)
        self.assertIsNotNone(session.completed_at)
        
    def test_pause_session(self):
        """Test pausing a session"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name
        )
        
        session.update_status(SessionStatus.PAUSED)
        
        self.assertEqual(session.status, SessionStatus.PAUSED)
        
    def test_resume_session(self):
        """Test resuming a session"""
        session = SessionEntity(
            id=self.session_id,
            name=self.session_name,
            status=SessionStatus.PAUSED
        )
        
        session.update_status(SessionStatus.ACTIVE)
        
        self.assertEqual(session.status, SessionStatus.ACTIVE)


class TestAgentEntity(unittest.TestCase):
    """Test AgentEntity domain logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent_id = "agent_001"
        self.agent_name = "Test Director"
        self.agent_type = AgentType.DIRECTOR
        
    def test_agent_entity_initialization(self):
        """Test agent entity initialization"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type
        )
        
        self.assertEqual(agent.id, self.agent_id)
        self.assertEqual(agent.name, self.agent_name)
        self.assertEqual(agent.agent_type, self.agent_type)
        self.assertEqual(agent.status, AgentStatus.IDLE)
        self.assertEqual(agent.expertise_level, 1.0)
        self.assertEqual(agent.total_decisions, 0)
        self.assertEqual(agent.successful_decisions, 0)
        self.assertEqual(agent.failed_decisions, 0)
        
    def test_agent_validation_empty_id(self):
        """Test agent validation with empty ID"""
        with self.assertRaises(ValueError) as context:
            AgentEntity(
                id="",
                name=self.agent_name,
                agent_type=self.agent_type
            )
        self.assertIn("Agent ID cannot be empty", str(context.exception))
        
    def test_agent_validation_empty_name(self):
        """Test agent validation with empty name"""
        with self.assertRaises(ValueError) as context:
            AgentEntity(
                id=self.agent_id,
                name="",
                agent_type=self.agent_type
            )
        self.assertIn("Agent name cannot be empty", str(context.exception))
        
    def test_agent_validation_invalid_expertise_level(self):
        """Test agent validation with invalid expertise level"""
        with self.assertRaises(ValueError) as context:
            AgentEntity(
                id=self.agent_id,
                name=self.agent_name,
                agent_type=self.agent_type,
                expertise_level=1.5
            )
        self.assertIn("Expertise level must be between 0.0 and 1.0", str(context.exception))
        
    def test_assign_task(self):
        """Test assigning task to agent"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type
        )
        
        session_id = "session_001"
        agent.assign_to_session(session_id)
        
        self.assertEqual(agent.status, AgentStatus.WORKING)
        self.assertEqual(agent.session_id, session_id)
        self.assertIsNotNone(agent.last_active_at)
        
    def test_complete_task(self):
        """Test completing agent task"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type,
            status=AgentStatus.WORKING
        )
        
        agent.complete_task()
        
        self.assertEqual(agent.status, AgentStatus.COMPLETED)
        self.assertIsNone(agent.current_task)
        self.assertEqual(agent.current_task_progress, 0.0)
        
    def test_fail_task(self):
        """Test failing agent task"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type,
            status=AgentStatus.WORKING
        )
        
        error_msg = "Task failed due to API error"
        agent.fail_task(error_msg)
        
        self.assertEqual(agent.status, AgentStatus.FAILED)
        self.assertIsNone(agent.current_task)
        self.assertEqual(agent.current_task_progress, 0.0)
        
    def test_update_task_progress(self):
        """Test updating task progress"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type,
            status=AgentStatus.WORKING
        )
        
        agent.update_task_progress(50.0)
        
        self.assertEqual(agent.current_task_progress, 50.0)
        self.assertIsNotNone(agent.last_active_at)
        
    def test_record_decision(self):
        """Test recording agent decision"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type
        )
        
        decision_id = agent.make_decision(
            decision_type="script_generation",
            decision_data={"style": "viral"},
            confidence_score=0.8,
            reasoning="Based on trending analysis"
        )
        
        self.assertEqual(agent.total_decisions, 1)
        self.assertIsNotNone(decision_id)
        self.assertEqual(len(agent.decisions), 1)
        
    def test_get_success_rate(self):
        """Test getting agent success rate"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type,
            total_decisions=10,
            successful_decisions=8
        )
        
        success_rate = agent.get_success_rate()
        
        self.assertEqual(success_rate, 80.0)
        
    def test_get_success_rate_no_decisions(self):
        """Test getting success rate with no decisions"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type
        )
        
        success_rate = agent.get_success_rate()
        
        self.assertEqual(success_rate, 0.0)
        
    def test_is_available(self):
        """Test checking if agent is available"""
        agent = AgentEntity(
            id=self.agent_id,
            name=self.agent_name,
            agent_type=self.agent_type
        )
        
        self.assertTrue(agent.is_available())
        
        agent.status = AgentStatus.WORKING
        self.assertFalse(agent.is_available())


if __name__ == '__main__':
    unittest.main() 