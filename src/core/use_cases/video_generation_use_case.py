"""
Video Generation Use Case - Orchestrates video generation business logic
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..entities.video_entity import VideoEntity, VideoStatus, Platform, VideoMetadata
from ..entities.session_entity import SessionEntity
from ..entities.agent_entity import AgentEntity, AgentType
from ..interfaces.repositories import VideoRepository, SessionRepository, AgentRepository
from ..interfaces.services import VideoGenerationService, ScriptGenerationService, AudioGenerationService

logger = logging.getLogger(__name__)


class VideoGenerationUseCase:
    """
    Use case for video generation orchestration
    
    This class encapsulates the business logic for generating videos,
    coordinating between entities and external services.
    """
    
    def __init__(
        self,
        video_repository: VideoRepository,
        session_repository: SessionRepository,
        agent_repository: AgentRepository,
        video_generation_service: VideoGenerationService,
        script_generation_service: ScriptGenerationService,
        audio_generation_service: AudioGenerationService
    ):
        """Initialize use case with required dependencies"""
        self.video_repository = video_repository
        self.session_repository = session_repository
        self.agent_repository = agent_repository
        self.video_generation_service = video_generation_service
        self.script_generation_service = script_generation_service
        self.audio_generation_service = audio_generation_service
    
    async def create_video_generation_request(
        self,
        session_id: str,
        mission: str,
        platform: Platform,
        generation_config: Dict[str, Any]
    ) -> VideoEntity:
        """
        Create a new video generation request
        
        Args:
            session_id: ID of the session
            mission: Video mission/topic
            platform: Target platform
            generation_config: Generation configuration
            
        Returns:
            Created video entity
            
        Raises:
            ValueError: If session not found or invalid parameters
        """
        # Validate session exists and is active
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if not session.can_add_videos():
            raise ValueError(f"Cannot add videos to session with status: {session.status}")
        
        # Create video entity
        video_id = f"video_{datetime.now().isoformat()}_{session_id}"
        
        # Extract metadata from config
        metadata = VideoMetadata(
            title=generation_config.get("title", f"Video for {mission}"),
            description=generation_config.get("description"),
            tags=generation_config.get("tags", []),
            duration_seconds=generation_config.get("duration_seconds", 30),
            resolution=generation_config.get("resolution", "1080p"),
            aspect_ratio=generation_config.get("aspect_ratio", "16:9"),
            frame_rate=generation_config.get("frame_rate", 30)
        )
        
        video = VideoEntity(
            id=video_id,
            session_id=session_id,
            mission=mission,
            platform=platform,
            metadata=metadata,
            generation_config=generation_config
        )
        
        # Save video entity
        await self.video_repository.save(video)
        
        # Update session
        session.add_video(video_id)
        await self.session_repository.save(session)
        
        logger.info(f"Created video generation request: {video_id}")
        return video
    
    async def start_video_generation(self, video_id: str) -> None:
        """
        Start the video generation process
        
        Args:
            video_id: ID of the video to generate
            
        Raises:
            ValueError: If video not found or cannot be started
        """
        # Get video entity
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        # Start generation process
        video.start_generation()
        await self.video_repository.save(video)
        
        logger.info(f"Started video generation: {video_id}")
        
        # Orchestrate the generation pipeline
        try:
            await self._orchestrate_generation_pipeline(video)
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            video.fail_generation(str(e))
            await self.video_repository.save(video)
            
            # Update session
            session = await self.session_repository.get_by_id(video.session_id)
            if session:
                session.mark_video_failed(video_id)
                await self.session_repository.save(session)
            
            raise
    
    async def _orchestrate_generation_pipeline(self, video: VideoEntity) -> None:
        """
        Orchestrate the complete video generation pipeline
        
        Args:
            video: Video entity to generate
        """
        # Phase 1: Script Generation
        await self._generate_script(video)
        
        # Phase 2: Audio Generation
        await self._generate_audio(video)
        
        # Phase 3: Video Generation
        await self._generate_video_content(video)
        
        # Phase 4: Final Composition
        await self._compose_final_video(video)
        
        # Mark as completed
        if video.final_video_path:
            video.complete_generation(video.final_video_path)
        else:
            raise ValueError("Final video path is required to complete generation")
        await self.video_repository.save(video)
        
        # Update session
        session = await self.session_repository.get_by_id(video.session_id)
        if session:
            session.mark_video_completed(video.id)
            await self.session_repository.save(session)
        
        logger.info(f"Video generation completed: {video.id}")
    
    async def _generate_script(self, video: VideoEntity) -> None:
        """Generate script content for the video"""
        video.update_progress(10.0, "script_generation")
        await self.video_repository.save(video)
        
        # Generate script using AI service
        script_content = await self.script_generation_service.generate_script(
            mission=video.mission,
            platform=video.platform,
            duration_seconds=video.metadata.duration_seconds,
            config=video.generation_config
        )
        
        video.set_script_content(script_content)
        video.update_progress(25.0, "script_completed")
        await self.video_repository.save(video)
        
        logger.info(f"Script generated for video: {video.id}")
    
    async def _generate_audio(self, video: VideoEntity) -> None:
        """Generate audio content for the video"""
        video.update_progress(30.0, "audio_generation")
        await self.video_repository.save(video)
        
        if not video.script_content:
            raise ValueError("Script content required for audio generation")
        
        # Generate audio using TTS service
        audio_files = await self.audio_generation_service.generate_audio(
            script_content=video.script_content,
            config=video.generation_config
        )
        
        for audio_file in audio_files:
            video.add_audio_file(audio_file)
        
        video.update_progress(50.0, "audio_completed")
        await self.video_repository.save(video)
        
        logger.info(f"Audio generated for video: {video.id}")
    
    async def _generate_video_content(self, video: VideoEntity) -> None:
        """Generate video content (clips and images)"""
        video.update_progress(55.0, "video_content_generation")
        await self.video_repository.save(video)
        
        if not video.script_content:
            raise ValueError("Script content required for video generation")
        
        # Generate video clips and images
        video_clips, image_files = await self.video_generation_service.generate_content(
            script_content=video.script_content,
            platform=video.platform,
            config=video.generation_config
        )
        
        for clip in video_clips:
            video.add_video_clip(clip)
        
        for image in image_files:
            video.add_image_file(image)
        
        video.update_progress(80.0, "video_content_completed")
        await self.video_repository.save(video)
        
        logger.info(f"Video content generated for video: {video.id}")
    
    async def _compose_final_video(self, video: VideoEntity) -> None:
        """Compose the final video from all components"""
        video.update_progress(85.0, "final_composition")
        await self.video_repository.save(video)
        
        # Compose final video
        final_video_path = await self.video_generation_service.compose_final_video(
            video_clips=video.video_clips,
            audio_files=video.audio_files,
            image_files=video.image_files,
            script_content=video.script_content,
            platform=video.platform,
            config=video.generation_config
        )
        
        video.final_video_path = final_video_path
        video.update_progress(100.0, "composition_completed")
        await self.video_repository.save(video)
        
        logger.info(f"Final video composed: {video.id}")
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get current status of video generation
        
        Args:
            video_id: ID of the video
            
        Returns:
            Video status information
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        return {
            "id": video.id,
            "status": video.status.value,
            "progress_percentage": video.progress_percentage,
            "current_stage": video.current_stage,
            "error_message": video.error_message,
            "created_at": video.created_at.isoformat(),
            "updated_at": video.updated_at.isoformat(),
            "completed_at": video.completed_at.isoformat() if video.completed_at else None
        }
    
    async def cancel_video_generation(self, video_id: str) -> None:
        """
        Cancel video generation
        
        Args:
            video_id: ID of the video to cancel
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        if not video.can_be_cancelled():
            raise ValueError(f"Cannot cancel video with status: {video.status}")
        
        video.cancel_generation()
        await self.video_repository.save(video)
        
        logger.info(f"Video generation cancelled: {video_id}")
    
    async def get_video_by_id(self, video_id: str) -> Optional[VideoEntity]:
        """
        Get video by ID
        
        Args:
            video_id: ID of the video
            
        Returns:
            Video entity or None if not found
        """
        return await self.video_repository.get_by_id(video_id)
    
    async def list_videos_by_session(self, session_id: str) -> list[VideoEntity]:
        """
        List all videos in a session
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of video entities
        """
        return await self.video_repository.list_by_session(session_id) 