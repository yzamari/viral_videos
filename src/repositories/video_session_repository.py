"""
Video Session Repository implementation for persistent storage.

This implementation provides data access for VideoSession entities
with proper error handling and query optimization.
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.domain.entities.video_session import VideoSession, VideoSessionStatus
from src.repositories.interfaces import IVideoSessionRepository
from src.utils.exceptions import RepositoryError


class VideoSessionRepository(IVideoSessionRepository):
    """
    File-based VideoSession repository implementation.
    
    Provides persistent storage for VideoSession entities using JSON files
    with proper indexing for efficient queries.
    """
    
    def __init__(self, base_path: str = "data/video_sessions"):
        """
        Initialize repository with base storage path.
        
        Args:
            base_path: Base directory for session data storage
        """
        self.base_path = Path(base_path)
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self) -> None:
        """Ensure storage directory exists"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RepositoryError(f"Failed to create storage directory: {e}")
    
    def _get_session_file_path(self, session_id: str) -> Path:
        """Get file path for session data"""
        return self.base_path / f"{session_id}.json"
    
    def _get_user_index_path(self) -> Path:
        """Get path for user-based session index"""
        return self.base_path / "user_sessions_index.json"
    
    def _get_status_index_path(self) -> Path:
        """Get path for status-based session index"""
        return self.base_path / "status_index.json"
    
    async def _load_user_index(self) -> Dict[str, List[str]]:
        """
        Load user session index for efficient user-based queries.
        
        Returns:
            Dictionary mapping user IDs to list of session IDs
        """
        index_path = self._get_user_index_path()
        if not index_path.exists():
            return {}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RepositoryError(f"Failed to load user index: {e}")
    
    async def _save_user_index(self, index: Dict[str, List[str]]) -> None:
        """Save user session index"""
        index_path = self._get_user_index_path()
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RepositoryError(f"Failed to save user index: {e}")
    
    async def _load_status_index(self) -> Dict[str, List[str]]:
        """
        Load status session index for efficient status-based queries.
        
        Returns:
            Dictionary mapping status values to list of session IDs
        """
        index_path = self._get_status_index_path()
        if not index_path.exists():
            return {}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RepositoryError(f"Failed to load status index: {e}")
    
    async def _save_status_index(self, index: Dict[str, List[str]]) -> None:
        """Save status session index"""
        index_path = self._get_status_index_path()
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RepositoryError(f"Failed to save status index: {e}")
    
    async def _update_indexes_for_session(self, session: VideoSession) -> None:
        """Update indexes when session is saved"""
        # Update user index
        user_index = await self._load_user_index()
        if session.user_id not in user_index:
            user_index[session.user_id] = []
        if session.id not in user_index[session.user_id]:
            user_index[session.user_id].append(session.id)
        await self._save_user_index(user_index)
        
        # Update status index
        status_index = await self._load_status_index()
        status_value = session.status.value
        if status_value not in status_index:
            status_index[status_value] = []
        if session.id not in status_index[status_value]:
            status_index[status_value].append(session.id)
        await self._save_status_index(status_index)
    
    async def _remove_from_indexes(self, session: VideoSession) -> None:
        """Remove session from indexes when deleted"""
        # Remove from user index
        user_index = await self._load_user_index()
        if session.user_id in user_index:
            user_sessions = user_index[session.user_id]
            if session.id in user_sessions:
                user_sessions.remove(session.id)
            if not user_sessions:
                del user_index[session.user_id]
        await self._save_user_index(user_index)
        
        # Remove from status index
        status_index = await self._load_status_index()
        for status_sessions in status_index.values():
            if session.id in status_sessions:
                status_sessions.remove(session.id)
        # Clean empty status lists
        status_index = {k: v for k, v in status_index.items() if v}
        await self._save_status_index(status_index)
    
    async def save(self, session: VideoSession) -> None:
        """
        Save video session entity to storage.
        
        Args:
            session: VideoSession entity to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        if not isinstance(session, VideoSession):
            raise RepositoryError("Entity must be a VideoSession instance")
        
        try:
            file_path = self._get_session_file_path(session.id)
            session_data = session.to_dict(include_entity=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            # Update indexes for efficient queries
            await self._update_indexes_for_session(session)
            
        except Exception as e:
            raise RepositoryError(f"Failed to save video session {session.id}: {e}")
    
    async def get_by_id(self, session_id: str) -> Optional[VideoSession]:
        """
        Get video session by ID.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            VideoSession entity if found, None otherwise
        """
        if not session_id or not session_id.strip():
            return None
        
        try:
            file_path = self._get_session_file_path(session_id)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            return VideoSession.from_dict(session_data)
            
        except Exception as e:
            raise RepositoryError(f"Failed to get video session {session_id}: {e}")
    
    async def get_by_user_id(self, user_id: str, limit: Optional[int] = None) -> List[VideoSession]:
        """
        Get video sessions by user ID.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of user's video sessions
        """
        if not user_id or not user_id.strip():
            return []
        
        try:
            user_index = await self._load_user_index()
            session_ids = user_index.get(user_id, [])
            
            if limit is not None:
                session_ids = session_ids[:limit]
            
            sessions = []
            for session_id in session_ids:
                session = await self.get_by_id(session_id)
                if session:
                    sessions.append(session)
            
            # Sort by creation time (most recent first)
            sessions.sort(key=lambda s: s.created_at, reverse=True)
            
            return sessions
            
        except Exception as e:
            raise RepositoryError(f"Failed to get sessions for user {user_id}: {e}")
    
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[VideoSession]:
        """
        Get active video sessions.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of active sessions
        """
        try:
            active_statuses = [
                VideoSessionStatus.CREATED.value,
                VideoSessionStatus.QUEUED.value,
                VideoSessionStatus.GENERATING.value,
                VideoSessionStatus.POST_PROCESSING.value
            ]
            
            all_active = []
            for status in active_statuses:
                status_sessions = await self.get_by_status(status)
                all_active.extend(status_sessions)
            
            # Filter by user if specified
            if user_id:
                all_active = [s for s in all_active if s.user_id == user_id]
            
            # Sort by creation time
            all_active.sort(key=lambda s: s.created_at, reverse=True)
            
            return all_active
            
        except Exception as e:
            raise RepositoryError(f"Failed to get active sessions: {e}")
    
    async def get_by_status(self, status: str, limit: Optional[int] = None) -> List[VideoSession]:
        """
        Get sessions by status.
        
        Args:
            status: Session status to filter by
            limit: Maximum number of results
            
        Returns:
            List of sessions with specified status
        """
        try:
            status_index = await self._load_status_index()
            session_ids = status_index.get(status, [])
            
            if limit is not None:
                session_ids = session_ids[:limit]
            
            sessions = []
            for session_id in session_ids:
                session = await self.get_by_id(session_id)
                if session and session.status.value == status:  # Double-check status
                    sessions.append(session)
            
            # Sort by creation time
            sessions.sort(key=lambda s: s.created_at, reverse=True)
            
            return sessions
            
        except Exception as e:
            raise RepositoryError(f"Failed to get sessions by status {status}: {e}")
    
    async def get_sessions_by_date_range(self, 
                                       start_date: str, 
                                       end_date: str,
                                       user_id: Optional[str] = None) -> List[VideoSession]:
        """
        Get sessions within date range.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            user_id: Optional user ID filter
            
        Returns:
            List of sessions within date range
        """
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Get all sessions for user or all sessions
            if user_id:
                sessions = await self.get_by_user_id(user_id)
            else:
                sessions = await self.list_all()
            
            # Filter by date range
            filtered_sessions = [
                session for session in sessions
                if start_dt <= session.created_at <= end_dt
            ]
            
            return filtered_sessions
            
        except Exception as e:
            raise RepositoryError(f"Failed to get sessions by date range: {e}")
    
    async def get_user_session_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's session statistics.
        
        Args:
            user_id: User ID to get stats for
            
        Returns:
            Dictionary with session statistics
        """
        try:
            user_sessions = await self.get_by_user_id(user_id)
            
            stats = {
                "total_sessions": len(user_sessions),
                "active_sessions": 0,
                "completed_sessions": 0,
                "failed_sessions": 0,
                "total_compute_time": 0.0,
                "total_storage_used": 0.0,
                "total_ai_tokens": 0,
                "average_generation_time": 0.0,
                "success_rate": 0.0
            }
            
            if not user_sessions:
                return stats
            
            total_generation_time = 0.0
            completed_count = 0
            
            for session in user_sessions:
                # Count by status
                if session.is_active():
                    stats["active_sessions"] += 1
                elif session.is_completed():
                    stats["completed_sessions"] += 1
                elif session.is_failed():
                    stats["failed_sessions"] += 1
                
                # Aggregate resource usage
                stats["total_compute_time"] += session.compute_time_seconds
                stats["total_storage_used"] += session.storage_used_mb
                stats["total_ai_tokens"] += session.ai_tokens_used
                
                # Calculate average generation time for completed sessions
                if session.is_completed() and session.compute_time_seconds > 0:
                    total_generation_time += session.compute_time_seconds
                    completed_count += 1
            
            # Calculate derived metrics
            if completed_count > 0:
                stats["average_generation_time"] = total_generation_time / completed_count
            
            if stats["total_sessions"] > 0:
                stats["success_rate"] = (stats["completed_sessions"] / stats["total_sessions"]) * 100.0
            
            return stats
            
        except Exception as e:
            raise RepositoryError(f"Failed to get user session stats for {user_id}: {e}")
    
    async def delete(self, session_id: str) -> bool:
        """
        Delete video session by ID.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not session_id or not session_id.strip():
            return False
        
        try:
            # Get session first to update indexes
            session = await self.get_by_id(session_id)
            if not session:
                return False
            
            file_path = self._get_session_file_path(session_id)
            if file_path.exists():
                file_path.unlink()
                await self._remove_from_indexes(session)
                return True
            
            return False
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete video session {session_id}: {e}")
    
    async def exists(self, session_id: str) -> bool:
        """
        Check if video session exists.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            True if exists, False otherwise
        """
        if not session_id or not session_id.strip():
            return False
        
        try:
            file_path = self._get_session_file_path(session_id)
            return file_path.exists()
        except Exception as e:
            raise RepositoryError(f"Failed to check session existence {session_id}: {e}")
    
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[VideoSession]:
        """
        List all video sessions with pagination.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of video sessions
        """
        try:
            sessions = []
            session_files = list(self.base_path.glob("*.json"))
            
            # Exclude index files
            session_files = [f for f in session_files if not f.name.endswith("_index.json")]
            
            # Sort by modification time (most recent first)
            session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Apply pagination
            if offset > 0:
                session_files = session_files[offset:]
            if limit is not None:
                session_files = session_files[:limit]
            
            for file_path in session_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    session = VideoSession.from_dict(session_data)
                    sessions.append(session)
                except Exception as e:
                    # Log error but continue with other sessions
                    print(f"Warning: Failed to load session from {file_path}: {e}")
                    continue
            
            return sessions
            
        except Exception as e:
            raise RepositoryError(f"Failed to list video sessions: {e}")
    
    async def count(self) -> int:
        """
        Count total number of video sessions.
        
        Returns:
            Total session count
        """
        try:
            session_files = list(self.base_path.glob("*.json"))
            # Exclude index files
            session_files = [f for f in session_files if not f.name.endswith("_index.json")]
            return len(session_files)
        except Exception as e:
            raise RepositoryError(f"Failed to count video sessions: {e}")