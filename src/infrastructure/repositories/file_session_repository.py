"""
File-based session repository implementation
"""

import json
from typing import Optional, List
from pathlib import Path

from ...core.interfaces.repositories import SessionRepository
from ...core.entities.session_entity import SessionEntity, SessionStatus


class FileSessionRepository(SessionRepository):
    """
    File-based implementation of SessionRepository
    
    Stores session entities as JSON files in a directory structure
    """
    
    def __init__(self, base_path: str = "data/sessions"):
        """
        Initialize repository with base path
        
        Args:
            base_path: Base directory for storing session files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save(self, session: SessionEntity) -> None:
        """Save a session entity to file"""
        session_file = self.base_path / f"{session.id}.json"
        
        # Convert entity to dictionary
        session_data = session.to_dict()
        
        # Save to file
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    async def get_by_id(self, session_id: str) -> Optional[SessionEntity]:
        """Get session by ID from file"""
        session_file = self.base_path / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            return SessionEntity.from_dict(session_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log error but don't raise - return None for invalid data
            print(f"Error loading session {session_id}: {e}")
            return None
    
    async def list_active(self) -> List[SessionEntity]:
        """List active sessions"""
        sessions = []
        
        # Iterate through all session files
        for session_file in self.base_path.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Check if session is active
                if session_data.get("status") == SessionStatus.ACTIVE.value:
                    session = SessionEntity.from_dict(session_data)
                    sessions.append(session)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by creation date
        sessions.sort(key=lambda s: s.created_at)
        return sessions
    
    async def delete(self, session_id: str) -> None:
        """Delete a session file"""
        session_file = self.base_path / f"{session_id}.json"
        
        if session_file.exists():
            session_file.unlink()
    
    async def list_all(self) -> List[SessionEntity]:
        """List all sessions"""
        sessions = []
        
        # Iterate through all session files
        for session_file in self.base_path.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                session = SessionEntity.from_dict(session_data)
                sessions.append(session)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by creation date
        sessions.sort(key=lambda s: s.created_at)
        return sessions
    
    async def list_by_status(self, status: SessionStatus) -> List[SessionEntity]:
        """List sessions by status (additional method)"""
        sessions = []
        
        # Iterate through all session files
        for session_file in self.base_path.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Check if session has the specified status
                if session_data.get("status") == status.value:
                    session = SessionEntity.from_dict(session_data)
                    sessions.append(session)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by creation date
        sessions.sort(key=lambda s: s.created_at)
        return sessions
    
    def get_storage_path(self) -> str:
        """Get the storage path for this repository"""
        return str(self.base_path)
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up old session files
        
        Args:
            days: Number of days to keep files
            
        Returns:
            Number of files cleaned up
        """
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned_count = 0
        
        for session_file in self.base_path.glob("*.json"):
            if session_file.stat().st_mtime < cutoff_time:
                session_file.unlink()
                cleaned_count += 1
        
        return cleaned_count 