"""
Video Generation Use Case - Orchestrates video generation business logic
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..entities.video_entity import (
    VideoEntity,
    VideoStatus,
    Platform,
    VideoMetadata
)
from ..entities.session_entity import SessionEntity
from ..entities.agent_entity import AgentEntity, AgentType
from ..interfaces.repositories import (
    VideoRepository,
    SessionRepository,
    AgentRepository
)
from ..interfaces.services import (
    VideoGenerationService,
    ScriptGenerationService,
    AudioGenerationService
)

logger = logging.getLogger(__name__)

class VideoGenerationUseCase:
    """
    Use case for video generation orchestration

    This class encapsulates the business logic for generating videos,
    coordinating between entities and external services.
    """

    def __init__(self,
        video_repository: VideoRepository,
        session_repository: SessionRepository,
        agent_repository: AgentRepository,
        video_generation_service: VideoGenerationService,
        script_generation_service: ScriptGenerationService,
        audio_generation_service: AudioGenerationService):
        """Initialize use case with required dependencies"""
        self.video_repository = video_repository
        self.session_repository = session_repository
        self.agent_repository = agent_repository
        self.video_generation_service = video_generation_service
        self.script_generation_service = script_generation_service
        self.audio_generation_service = audio_generation_service

    async def create_video_generation_request(self,
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
            status=VideoStatus.PENDING,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to repository
        saved_video = await self.video_repository.save(video)
        logger.info(f"Created video generation request: {video_id}")

        return saved_video

    async def start_video_generation(self, video_id: str) -> None:
        """
        Start the video generation process

        Args:
            video_id: ID of the video to generate

        Raises:
            ValueError: If video not found
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        if video.status != VideoStatus.PENDING:
            raise ValueError(f"Video {video_id} is not in pending status")

        # Update status to generating
        video.status = VideoStatus.GENERATING
        video.updated_at = datetime.now()
        await self.video_repository.save(video)

        try:
            # Start generation pipeline
            await self._orchestrate_generation_pipeline(video)
            
            # Update status to completed
            video.status = VideoStatus.COMPLETED
            video.updated_at = datetime.now()
            await self.video_repository.save(video)
            
            logger.info(f"Video generation completed: {video_id}")
            
        except Exception as e:
            # Update status to failed
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            video.updated_at = datetime.now()
            await self.video_repository.save(video)
            
            logger.error(f"Video generation failed: {video_id} - {e}")
            raise

    async def _orchestrate_generation_pipeline(self, video: VideoEntity) -> None:
        """
        Orchestrate the complete video generation pipeline

        Args:
            video: Video entity
        """
        logger.info(f"Starting generation pipeline for video: {video.id}")
        
        # Generate script
        await self._generate_script(video)
        
        # Generate audio
        await self._generate_audio(video)
        
        # Generate video content
        await self._generate_video_content(video)
        
        # Compose final video
        await self._compose_final_video(video)

    async def _generate_script(self, video: VideoEntity) -> None:
        """
        Generate script content

        Args:
            video: Video entity
        """
        logger.info(f"Generating script for video: {video.id}")

        script_content = await self.script_generation_service.generate_script(
            mission=video.mission,
            platform=video.platform,
            duration_seconds=video.metadata.duration_seconds,
            config=video.generation_config
        )

        video.script_content = script_content
        await self.video_repository.save(video)

    async def _generate_audio(self, video: VideoEntity) -> None:
        """
        Generate audio for the video

        Args:
            video: Video entity
        """
        logger.info(f"Generating audio for video: {video.id}")

        # Use script_content if available, otherwise use empty dict
        script_data = video.script_content or {"script": "Default script"}
        
        audio_files = await self.audio_generation_service.generate_audio(
            script_content=script_data,
            config=video.generation_config
        )

        if audio_files:
            video.audio_files.extend(audio_files)
        await self.video_repository.save(video)

    async def _generate_video_content(self, video: VideoEntity) -> None:
        """
        Generate video content

        Args:
            video: Video entity
        """
        logger.info(f"Generating video content for video: {video.id}")

        # Use script_content if available
        script_data = video.script_content or {"script": "Default script"}
        
        video_clips, image_files = await self.video_generation_service.generate_content(
            script_content=script_data,
            platform=video.platform,
            config=video.generation_config
        )

        if video_clips:
            video.video_clips.extend(video_clips)
        if image_files:
            video.image_files.extend(image_files)
        await self.video_repository.save(video)

    async def _compose_final_video(self, video: VideoEntity) -> None:
        """
        Compose final video from components

        Args:
            video: Video entity
        """
        logger.info(f"Composing final video for video: {video.id}")

        script_data = video.script_content or {"script": "Default script"}
        
        final_path = await self.video_generation_service.compose_final_video(
            video_clips=video.video_clips,
            audio_files=video.audio_files,
            image_files=video.image_files,
            script_content=script_data,
            platform=video.platform,
            config=video.generation_config
        )

        video.final_video_path = final_path
        await self.video_repository.save(video)

    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a video generation

        Args:
            video_id: ID of the video

        Returns:
            Status information

        Raises:
            ValueError: If video not found
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        return {
            "id": video.id,
            "status": video.status.value,
            "created_at": video.created_at.isoformat(),
            "updated_at": video.updated_at.isoformat(),
            "error_message": video.error_message,
            "progress": video.progress_percentage or 0
        }

    async def cancel_video_generation(self, video_id: str) -> None:
        """
        Cancel a video generation

        Args:
            video_id: ID of the video to cancel

        Raises:
            ValueError: If video not found or cannot be cancelled
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        if video.status not in [VideoStatus.PENDING, VideoStatus.PROCESSING]:
            raise ValueError(f"Cannot cancel video with status: {video.status}")

        video.status = VideoStatus.CANCELLED
        video.updated_at = datetime.now()
        await self.video_repository.save(video)

        logger.info(f"Video generation cancelled: {video_id}")

    async def get_video_by_id(self, video_id: str) -> Optional[VideoEntity]:
        """
        Get a video by its ID

        Args:
            video_id: ID of the video

        Returns:
            Video entity if found, None otherwise
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
        return await self.video_repository.get_by_session_id(session_id)

    async def get_videos_by_session(self, session_id: str) -> list[VideoEntity]:
        """
        Get all videos in a session (alias for list_videos_by_session)

        Args:
            session_id: ID of the session

        Returns:
            List of video entities
        """
        return await self.list_videos_by_session(session_id)

    async def delete_video(self, video_id: str) -> bool:
        """
        Delete a video

        Args:
            video_id: ID of the video to delete

        Returns:
            True if successful

        Raises:
            ValueError: If video not found
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video not found: {video_id}")
        
        await self.video_repository.delete(video_id)
        return True

    async def generate_video(self, video_id: str) -> VideoEntity:
        """
        Generate a video (alias for start_video_generation)

        Args:
            video_id: ID of the video to generate

        Returns:
            Video entity with updated status
        """
        try:
            await self.start_video_generation(video_id)
        except Exception:
            # Exception already handled in start_video_generation
            pass
        
        # Return the video entity
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video not found: {video_id}")
        return video

    async def update_video_status(self, video_id: str, status: VideoStatus) -> VideoEntity:
        """
        Update video status

        Args:
            video_id: ID of the video
            status: New status

        Returns:
            Updated video entity
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video not found: {video_id}")
        
        video.status = status
        await self.video_repository.save(video)
        return video

    def _validate_video_parameters(self, mission: str, platform: Platform = Platform.YOUTUBE, generation_config: Dict[str, Any] = None) -> bool:
        """
        Validate video parameters

        Args:
            mission: Video mission/topic
            platform: Target platform
            generation_config: Generation configuration

        Returns:
            True if valid

        Raises:
            ValueError: If parameters are invalid
        """
        if not mission or not mission.strip():
            raise ValueError("Mission cannot be empty")
        
        if generation_config and "duration_seconds" in generation_config:
            duration = generation_config["duration_seconds"]
            if duration <= 0:
                raise ValueError("Duration must be positive")
            
            if duration > 300:  # 5 minutes
                raise ValueError("Duration cannot exceed 300 seconds")
        
        return True
