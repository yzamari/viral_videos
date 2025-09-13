"""
Repository interfaces implementing the Repository pattern with proper abstraction.

These interfaces follow the Interface Segregation Principle by providing
specific contracts for each entity type while maintaining common patterns.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from src.domain.entities.user import User
from src.domain.entities.video_session import VideoSession
from src.domain.entities.campaign import Campaign

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Base repository interface following the Repository pattern.
    
    Provides common CRUD operations that all repositories should implement.
    Uses Generic typing to maintain type safety while allowing reuse.
    """
    
    @abstractmethod
    async def save(self, entity: T) -> None:
        """
        Save an entity to the repository.
        
        Args:
            entity: The entity to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            The entity if found, None otherwise
            
        Raises:
            RepositoryError: If retrieval operation fails
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            entity_id: Unique identifier for the entity to delete
            
        Returns:
            True if entity was deleted, False if not found
            
        Raises:
            RepositoryError: If delete operation fails
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """
        Check if an entity exists by its ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            True if entity exists, False otherwise
            
        Raises:
            RepositoryError: If check operation fails
        """
        pass
    
    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        List all entities with optional pagination.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of entities
            
        Raises:
            RepositoryError: If list operation fails
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Count total number of entities.
        
        Returns:
            Total count of entities
            
        Raises:
            RepositoryError: If count operation fails
        """
        pass


class IUserRepository(IRepository[User]):
    """
    User repository interface with user-specific operations.
    
    Extends the base repository with user domain-specific queries
    while maintaining the Liskov Substitution Principle.
    """
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_role(self, role: str, limit: Optional[int] = None) -> List[User]:
        """
        Find users by role.
        
        Args:
            role: User role to filter by
            limit: Maximum number of results
            
        Returns:
            List of users with the specified role
        """
        pass
    
    @abstractmethod
    async def find_trial_users_expiring(self, days: int = 7) -> List[User]:
        """
        Find trial users expiring within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of users with trials expiring soon
        """
        pass
    
    @abstractmethod
    async def find_inactive_users(self, days: int = 30) -> List[User]:
        """
        Find users who haven't logged in for specified days.
        
        Args:
            days: Number of days of inactivity
            
        Returns:
            List of inactive users
        """
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: str) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: ID of user to update
        """
        pass


class IVideoSessionRepository(IRepository[VideoSession]):
    """
    Video session repository interface with session-specific operations.
    
    Provides video session domain-specific queries while maintaining
    separation of concerns from the domain layer.
    """
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: Optional[int] = None) -> List[VideoSession]:
        """
        Get video sessions by user ID.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of user's video sessions
        """
        pass
    
    @abstractmethod
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[VideoSession]:
        """
        Get active video sessions.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of active sessions
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str, limit: Optional[int] = None) -> List[VideoSession]:
        """
        Get sessions by status.
        
        Args:
            status: Session status to filter by
            limit: Maximum number of results
            
        Returns:
            List of sessions with specified status
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def get_user_session_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's session statistics.
        
        Args:
            user_id: User ID to get stats for
            
        Returns:
            Dictionary with session statistics
        """
        pass


class ICampaignRepository(IRepository[Campaign]):
    """
    Campaign repository interface with campaign-specific operations.
    
    Provides campaign domain-specific queries while maintaining proper
    abstraction and separation of concerns.
    """
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: Optional[int] = None) -> List[Campaign]:
        """
        Get campaigns by user ID.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of user's campaigns
        """
        pass
    
    @abstractmethod
    async def get_active_campaigns(self, user_id: Optional[str] = None) -> List[Campaign]:
        """
        Get active campaigns.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of active campaigns
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str, limit: Optional[int] = None) -> List[Campaign]:
        """
        Get campaigns by status.
        
        Args:
            status: Campaign status to filter by
            limit: Maximum number of results
            
        Returns:
            List of campaigns with specified status
        """
        pass
    
    @abstractmethod
    async def find_by_tags(self, tags: List[str], user_id: Optional[str] = None) -> List[Campaign]:
        """
        Find campaigns by tags.
        
        Args:
            tags: List of tags to search for
            user_id: Optional user ID filter
            
        Returns:
            List of campaigns containing any of the specified tags
        """
        pass
    
    @abstractmethod
    async def get_campaigns_by_platform(self, platform: str, user_id: Optional[str] = None) -> List[Campaign]:
        """
        Get campaigns targeting specific platform.
        
        Args:
            platform: Platform to filter by
            user_id: Optional user ID filter
            
        Returns:
            List of campaigns targeting the platform
        """
        pass
    
    @abstractmethod
    async def get_campaign_performance_summary(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign performance summary.
        
        Args:
            campaign_id: Campaign ID to get summary for
            
        Returns:
            Dictionary with campaign performance metrics
        """
        pass