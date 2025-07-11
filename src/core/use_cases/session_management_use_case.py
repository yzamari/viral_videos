"""
Session management use case for the AI Video Generator

This module contains the business logic for managing video generation sessions.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.session_entity import SessionEntity, SessionStatus
from ..entities.video_entity import VideoEntity
from ..interfaces.repositories import SessionRepository, VideoRepository


class SessionManagementUseCase:
    """
    Use case for managing video generation sessions
    
    This class encapsulates all business logic related to session management,
    including creating sessions, tracking progress, and managing session lifecycle.
    """
    
    def __init__(
        self,
        session_repository: SessionRepository,
        video_repository: VideoRepository
    ):
        """
        Initialize session management use case
        
        Args:
            session_repository: Repository for session data
            video_repository: Repository for video data
        """
        self.session_repository = session_repository
        self.video_repository = video_repository
    
    async def create_session(
        self,
        name: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> SessionEntity:
        """
        Create a new video generation session
        
        Args:
            name: Session name
            description: Optional session description
            config: Optional session configuration
            
        Returns:
            Created session entity
        """
        # Generate session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create session entity
        session = SessionEntity(
            id=session_id,
            name=name
        )
        
        # Set configuration if provided
        if config:
            session.session_config = config
        
        # Store description in config if provided
        if description:
            session.session_config["description"] = description
        
        # Save session
        await self.session_repository.save(session)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[SessionEntity]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            Session entity or None if not found
        """
        return await self.session_repository.get_by_id(session_id)
    
    async def get_active_sessions(self) -> List[SessionEntity]:
        """
        Get all active sessions
        
        Returns:
            List of active session entities
        """
        return await self.session_repository.list_active()
    
    async def get_session_videos(self, session_id: str) -> List[VideoEntity]:
        """
        Get all videos for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of video entities
        """
        return await self.video_repository.list_by_session(session_id)
    
    async def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """
        Get session progress information
        
        Args:
            session_id: Session ID
            
        Returns:
            Progress information dictionary
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        videos = await self.get_session_videos(session_id)
        
        # Calculate progress statistics
        total_videos = len(videos)
        completed_videos = sum(1 for v in videos if v.status.value == "completed")
        failed_videos = sum(1 for v in videos if v.status.value == "failed")
        in_progress_videos = sum(1 for v in videos if v.status.value == "generating")
        
        # Calculate average progress
        if total_videos > 0:
            total_progress = sum(v.progress_percentage for v in videos)
            average_progress = total_progress / total_videos
        else:
            average_progress = 0.0
        
        return {
            "session_id": session_id,
            "session_name": session.name,
            "session_status": session.status.value,
            "total_videos": total_videos,
            "completed_videos": completed_videos,
            "failed_videos": failed_videos,
            "in_progress_videos": in_progress_videos,
            "pending_videos": total_videos - completed_videos - failed_videos - in_progress_videos,
            "completion_rate": (completed_videos / total_videos * 100) if total_videos > 0 else 0.0,
            "failure_rate": (failed_videos / total_videos * 100) if total_videos > 0 else 0.0,
            "average_progress": average_progress,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat() if session.updated_at else None
        }
    
    async def update_session_status(
        self,
        session_id: str,
        status: SessionStatus
    ) -> SessionEntity:
        """
        Update session status
        
        Args:
            session_id: Session ID
            status: New status
            
        Returns:
            Updated session entity
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.update_status(status)
        await self.session_repository.save(session)
        
        return session
    
    async def complete_session(self, session_id: str) -> SessionEntity:
        """
        Mark session as completed
        
        Args:
            session_id: Session ID
            
        Returns:
            Updated session entity
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.complete()
        await self.session_repository.save(session)
        
        return session
    
    async def pause_session(self, session_id: str) -> SessionEntity:
        """
        Pause session
        
        Args:
            session_id: Session ID
            
        Returns:
            Updated session entity
        """
        return await self.update_session_status(session_id, SessionStatus.PAUSED)
    
    async def resume_session(self, session_id: str) -> SessionEntity:
        """
        Resume session
        
        Args:
            session_id: Session ID
            
        Returns:
            Updated session entity
        """
        return await self.update_session_status(session_id, SessionStatus.ACTIVE)
    
    async def delete_session(self, session_id: str) -> None:
        """
        Delete session and all associated videos
        
        Args:
            session_id: Session ID
        """
        # Get all videos for the session
        videos = await self.get_session_videos(session_id)
        
        # Delete all videos
        for video in videos:
            await self.video_repository.delete(video.id)
        
        # Delete session
        await self.session_repository.delete(session_id)
    
    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed session statistics
        
        Args:
            session_id: Session ID
            
        Returns:
            Detailed statistics dictionary
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        videos = await self.get_session_videos(session_id)
        
        # Calculate detailed statistics
        platform_stats = {}
        status_stats = {}
        duration_stats = {"total": 0, "average": 0, "min": float('inf'), "max": 0}
        
        for video in videos:
            # Platform statistics
            platform = video.platform.value
            if platform not in platform_stats:
                platform_stats[platform] = 0
            platform_stats[platform] += 1
            
            # Status statistics
            status = video.status.value
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
            
            # Duration statistics
            if video.metadata and video.metadata.duration_seconds:
                duration = video.metadata.duration_seconds
                duration_stats["total"] += duration
                duration_stats["min"] = min(duration_stats["min"], duration)
                duration_stats["max"] = max(duration_stats["max"], duration)
        
        # Calculate averages
        if videos:
            duration_stats["average"] = duration_stats["total"] / len(videos)
            if duration_stats["min"] == float('inf'):
                duration_stats["min"] = 0
        else:
            duration_stats["min"] = 0
        
        return {
            "session_id": session_id,
            "session_name": session.name,
            "total_videos": len(videos),
            "platform_distribution": platform_stats,
            "status_distribution": status_stats,
            "duration_statistics": duration_stats,
            "session_duration": (
                datetime.now() - session.created_at
            ).total_seconds() if session.status == SessionStatus.ACTIVE else None,
            "completion_rate": session.get_completion_rate(),
            "failure_rate": session.get_failure_rate()
        } 