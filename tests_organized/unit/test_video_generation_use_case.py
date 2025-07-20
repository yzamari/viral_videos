"""
Comprehensive unit tests for VideoGenerationUseCase class
Tests all methods, business logic, and error conditions
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from datetime import datetime
import asyncio

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.use_cases.video_generation_use_case import VideoGenerationUseCase
from src.core.entities.video_entity import VideoEntity, VideoMetadata, VideoStatus
from src.core.entities.session_entity import SessionEntity
from src.models.video_models import Platform
from src.core.entities.session_entity import SessionStatus


class TestVideoGenerationUseCase(unittest.TestCase):
    """Test VideoGenerationUseCase"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_video_repository = Mock()
        self.mock_session_repository = Mock()
        self.mock_agent_repository = Mock()
        self.mock_video_generation_service = Mock()
        self.mock_script_generation_service = Mock()
        self.mock_audio_generation_service = Mock()
        
        self.use_case = VideoGenerationUseCase(
            video_repository=self.mock_video_repository,
            session_repository=self.mock_session_repository,
            agent_repository=self.mock_agent_repository,
            video_generation_service=self.mock_video_generation_service,
            script_generation_service=self.mock_script_generation_service,
            audio_generation_service=self.mock_audio_generation_service
        )
        
        # Test data
        self.test_video_entity = VideoEntity(
            id="video_123",
            session_id="session_123",
            mission="Test video mission",
            platform=Platform.TIKTOK,
            status=VideoStatus.PENDING,
            metadata=VideoMetadata(
                title="Test Video",
                description="Test video description",
                duration_seconds=15
            )
        )
        
        self.test_session_entity = SessionEntity(
            id="session_123",
            name="Test Session",
            created_at=datetime.now(),
            status=SessionStatus.ACTIVE
        )
    
    def test_init_success(self):
        """Test successful initialization"""
        self.assertIsNotNone(self.use_case.video_repository)
        self.assertIsNotNone(self.use_case.session_repository)
        self.assertIsNotNone(self.use_case.agent_repository)
        self.assertIsNotNone(self.use_case.video_generation_service)
        self.assertIsNotNone(self.use_case.script_generation_service)
        self.assertIsNotNone(self.use_case.audio_generation_service)
    
    def test_create_video_entity_success(self):
        """Test successful video entity creation"""
        # Setup mock
        self.mock_session_repository.get_by_id = AsyncMock(return_value=self.test_session_entity)
        self.mock_video_repository.save = AsyncMock(return_value=self.test_video_entity)
        
        # Test
        async def run_test():
            result = await self.use_case.create_video_generation_request(
                session_id="session_123",
                mission="Test video mission",
                platform=Platform.TIKTOK,
                generation_config={
                    "title": "Test Video",
                    "description": "Test video description",
                    "duration_seconds": 15
                }
            )
            
            self.assertIsInstance(result, VideoEntity)
            self.assertEqual(result.mission, "Test video mission")
            self.assertEqual(result.platform, Platform.TIKTOK)
            self.assertEqual(result.metadata.title, "Test Video")
            self.assertEqual(result.metadata.description, "Test video description")
            self.assertEqual(result.metadata.duration_seconds, 15)
        
        asyncio.run(run_test())
    
    def test_get_video_by_id_success(self):
        """Test successful video retrieval by ID"""
        # Setup mock
        self.mock_video_repository.get_by_id = AsyncMock(return_value=self.test_video_entity)
        
        # Test
        async def run_test():
            result = await self.use_case.get_video_by_id("video_123")
            
            self.assertEqual(result, self.test_video_entity)
            self.mock_video_repository.get_by_id.assert_called_once_with("video_123")
        
        asyncio.run(run_test())
    
    def test_get_video_by_id_not_found(self):
        """Test video retrieval when not found"""
        # Setup mock
        self.mock_video_repository.get_by_id = AsyncMock(return_value=None)
        
        # Test
        async def run_test():
            result = await self.use_case.get_video_by_id("nonexistent")
            
            self.assertIsNone(result)
            self.mock_video_repository.get_by_id.assert_called_once_with("nonexistent")
        
        asyncio.run(run_test())
    
    def test_get_videos_by_session_success(self):
        """Test successful video retrieval by session"""
        # Setup mock
        videos = [self.test_video_entity]
        self.mock_video_repository.get_by_session_id = AsyncMock(return_value=videos)
        
        # Test
        async def run_test():
            result = await self.use_case.get_videos_by_session("session_123")
            
            self.assertEqual(result, videos)
            self.mock_video_repository.get_by_session_id.assert_called_once_with("session_123")
        
        asyncio.run(run_test())
    
    def test_get_videos_by_session_empty(self):
        """Test video retrieval by session when empty"""
        # Setup mock
        self.mock_video_repository.get_by_session_id = AsyncMock(return_value=[])
        
        # Test
        async def run_test():
            result = await self.use_case.get_videos_by_session("session_123")
            
            self.assertEqual(result, [])
            self.mock_video_repository.get_by_session_id.assert_called_once_with("session_123")
        
        asyncio.run(run_test())
    
    def test_update_video_status_success(self):
        """Test successful video status update"""
        # Setup mock
        self.mock_video_repository.get_by_id = AsyncMock(return_value=self.test_video_entity)
        self.mock_video_repository.save = AsyncMock(return_value=self.test_video_entity)
        
        # Test
        async def run_test():
            result = await self.use_case.update_video_status("video_123", VideoStatus.GENERATING)
            
            self.assertEqual(result.status, VideoStatus.GENERATING)
            self.mock_video_repository.get_by_id.assert_called_once_with("video_123")
            self.mock_video_repository.save.assert_called_once()
        
        asyncio.run(run_test())
    
    def test_update_video_status_not_found(self):
        """Test video status update when not found"""
        # Setup mock
        self.mock_video_repository.get_by_id = AsyncMock(return_value=None)
        
        # Test
        async def run_test():
            with self.assertRaises(ValueError):
                await self.use_case.update_video_status("nonexistent", VideoStatus.GENERATING)
        
        asyncio.run(run_test())
    
    def test_delete_video_success(self):
        """Test successful video deletion"""
        # Setup mock
        self.mock_video_repository.get_by_id = AsyncMock(return_value=self.test_video_entity)
        self.mock_video_repository.delete = AsyncMock(return_value=True)
        
        # Test
        async def run_test():
            result = await self.use_case.delete_video("video_123")
            
            self.assertTrue(result)
            self.mock_video_repository.get_by_id.assert_called_once_with("video_123")
            self.mock_video_repository.delete.assert_called_once_with("video_123")
        
        asyncio.run(run_test())
    
    def test_delete_video_not_found(self):
        """Test video deletion when not found"""
        # Setup mock
        self.mock_video_repository.get_by_id = AsyncMock(return_value=None)
        
        # Test
        async def run_test():
            with self.assertRaises(ValueError):
                await self.use_case.delete_video("nonexistent")
        
        asyncio.run(run_test())
    
    def test_generate_video_success(self):
        """Test successful video generation"""
        # Setup mocks
        self.mock_video_repository.get_by_id = AsyncMock(return_value=self.test_video_entity)
        self.mock_script_generation_service.generate_script = AsyncMock(return_value={"script": "Test script"})
        self.mock_audio_generation_service.generate_audio = AsyncMock(return_value=["audio1.mp3"])
        self.mock_video_generation_service.generate_content = AsyncMock(return_value=(["video1.mp4"], ["image1.jpg"]))
        self.mock_video_generation_service.compose_final_video = AsyncMock(return_value="final_video.mp4")
        self.mock_video_repository.save = AsyncMock(return_value=self.test_video_entity)
        
        # Test
        async def run_test():
            result = await self.use_case.generate_video("video_123")
            
            self.assertEqual(result.status, VideoStatus.COMPLETED)
            self.assertIsNotNone(result.final_video_path)
            
            # Verify all services were called
            self.mock_script_generation_service.generate_script.assert_called_once()
            self.mock_audio_generation_service.generate_audio.assert_called_once()
            self.mock_video_generation_service.generate_content.assert_called_once()
            self.mock_video_generation_service.compose_final_video.assert_called_once()
        
        asyncio.run(run_test())
    
    def test_generate_video_script_failure(self):
        """Test video generation with script failure"""
        # Setup mocks
        self.mock_video_repository.get_by_id = AsyncMock(return_value=self.test_video_entity)
        self.mock_script_generation_service.generate_script = AsyncMock(side_effect=Exception("Script error"))
        self.mock_video_repository.save = AsyncMock(return_value=self.test_video_entity)
        
        # Test
        async def run_test():
            result = await self.use_case.generate_video("video_123")
            
            self.assertEqual(result.status, VideoStatus.FAILED)
            self.assertIsNotNone(result.error_message)
            self.assertIn("Script error", result.error_message)
        
        asyncio.run(run_test())
    
    def test_generate_video_audio_failure(self):
        """Test video generation with audio failure"""
        # Setup mocks
        self.mock_video_repository.get_by_id = AsyncMock(return_value=self.test_video_entity)
        self.mock_script_generation_service.generate_script = AsyncMock(return_value={"script": "Test script"})
        self.mock_audio_generation_service.generate_audio = AsyncMock(side_effect=Exception("Audio error"))
        self.mock_video_repository.save = AsyncMock(return_value=self.test_video_entity)
        
        # Test
        async def run_test():
            result = await self.use_case.generate_video("video_123")
            
            self.assertEqual(result.status, VideoStatus.FAILED)
            self.assertIsNotNone(result.error_message)
            self.assertIn("Audio error", result.error_message)
        
        asyncio.run(run_test())
    
    def test_generate_video_video_failure(self):
        """Test video generation with video failure"""
        # Setup mocks
        self.mock_video_repository.get_by_id = AsyncMock(return_value=self.test_video_entity)
        self.mock_script_generation_service.generate_script = AsyncMock(return_value={"script": "Test script"})
        self.mock_audio_generation_service.generate_audio = AsyncMock(return_value=["audio1.mp3"])
        self.mock_video_generation_service.generate_content = AsyncMock(side_effect=Exception("Video error"))
        self.mock_video_repository.save = AsyncMock(return_value=self.test_video_entity)
        
        # Test
        async def run_test():
            result = await self.use_case.generate_video("video_123")
            
            self.assertEqual(result.status, VideoStatus.FAILED)
            self.assertIsNotNone(result.error_message)
            self.assertIn("Video error", result.error_message)
        
        asyncio.run(run_test())
    
    def test_generate_video_invalid_session(self):
        """Test video generation with invalid session"""
        # Setup mock
        invalid_session = SessionEntity(
            id="session_123",
            name="Test Session",
            created_at=datetime.now(),
            status=SessionStatus.CANCELLED
        )
        invalid_session.can_add_videos = Mock(return_value=False)
        self.mock_session_repository.get_by_id = AsyncMock(return_value=invalid_session)
        
        # Test
        async def run_test():
            with self.assertRaises(ValueError):
                await self.use_case.create_video_generation_request(
                    session_id="session_123",
                    mission="Test video mission",
                    platform=Platform.TIKTOK,
                    generation_config={"title": "Test Video"}
                )
        
        asyncio.run(run_test())
    
    def test_validate_video_parameters_success(self):
        """Test successful video parameter validation"""
        # Valid parameters
        result = self.use_case._validate_video_parameters(
            mission="Test mission",
            platform=Platform.TIKTOK,
            generation_config={"duration_seconds": 30}
        )
        
        self.assertTrue(result)
    
    def test_validate_video_parameters_invalid_topic(self):
        """Test video parameter validation with invalid topic"""
        # Invalid topic
        with self.assertRaises(ValueError):
            self.use_case._validate_video_parameters(
                mission="",
                platform=Platform.TIKTOK,
                generation_config={"duration_seconds": 30}
            )
    
    def test_validate_video_parameters_invalid_duration(self):
        """Test video parameter validation with invalid duration"""
        # Invalid duration
        with self.assertRaises(ValueError):
            self.use_case._validate_video_parameters(
                mission="Test mission",
                platform=Platform.TIKTOK,
                generation_config={"duration_seconds": 0}
            )

if __name__ == '__main__':
    unittest.main() 