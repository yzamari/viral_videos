"""
Repository interfaces for data access abstraction
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.video_entity import VideoEntity
from ..entities.session_entity import SessionEntity
from ..entities.agent_entity import AgentEntity


class VideoRepository(ABC):
    """Abstract repository for video entities"""
    
    @abstractmethod
    async def save(self, video: VideoEntity) -> None:
        """Save a video entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, video_id: str) -> Optional[VideoEntity]:
        """Get video by ID"""
        pass
    
    @abstractmethod
    async def list_by_session(self, session_id: str) -> List[VideoEntity]:
        """List videos by session ID"""
        pass
    
    @abstractmethod
    async def delete(self, video_id: str) -> None:
        """Delete a video"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[VideoEntity]:
        """List all videos"""
        pass


class SessionRepository(ABC):
    """Abstract repository for session entities"""
    
    @abstractmethod
    async def save(self, session: SessionEntity) -> None:
        """Save a session entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[SessionEntity]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    async def list_active(self) -> List[SessionEntity]:
        """List active sessions"""
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """Delete a session"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[SessionEntity]:
        """List all sessions"""
        pass


class AgentRepository(ABC):
    """Abstract repository for agent entities"""
    
    @abstractmethod
    async def save(self, agent: AgentEntity) -> None:
        """Save an agent entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, agent_id: str) -> Optional[AgentEntity]:
        """Get agent by ID"""
        pass
    
    @abstractmethod
    async def list_available(self) -> List[AgentEntity]:
        """List available agents"""
        pass
    
    @abstractmethod
    async def list_by_session(self, session_id: str) -> List[AgentEntity]:
        """List agents by session ID"""
        pass
    
    @abstractmethod
    async def delete(self, agent_id: str) -> None:
        """Delete an agent"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[AgentEntity]:
        """List all agents"""
        pass 