"""
Service interfaces defining business logic contracts.

These interfaces follow the Dependency Inversion Principle by providing
abstract contracts that can be implemented by concrete service classes.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from src.domain.entities.user import User, UserRole
from src.domain.entities.video_session import VideoSession, VideoGenerationConfig
from src.domain.entities.campaign import Campaign


class IAuthenticationService(ABC):
    """
    Authentication service interface defining user authentication contracts.
    
    Follows Single Responsibility Principle by handling only authentication
    and authorization logic.
    """
    
    @abstractmethod
    async def register_user(self, 
                          username: str, 
                          email: str, 
                          password: str,
                          organization: Optional[str] = None) -> User:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            organization: Optional organization name
            
        Returns:
            Created user entity
            
        Raises:
            AuthenticationError: If registration fails
        """
        pass
    
    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/password.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User entity if authentication succeeds, None otherwise
        """
        pass
    
    @abstractmethod
    async def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token for user.
        
        Args:
            user: User entity to create token for
            expires_delta: Optional expiration time delta
            
        Returns:
            JWT access token string
        """
        pass
    
    @abstractmethod
    async def verify_access_token(self, token: str) -> Optional[User]:
        """
        Verify JWT access token and return user.
        
        Args:
            token: JWT access token
            
        Returns:
            User entity if token is valid, None otherwise
        """
        pass
    
    @abstractmethod
    async def refresh_access_token(self, user: User) -> str:
        """
        Refresh access token for user.
        
        Args:
            user: User entity to refresh token for
            
        Returns:
            New JWT access token
        """
        pass
    
    @abstractmethod
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        pass
    
    @abstractmethod
    async def verify_email(self, user_id: str, verification_token: str) -> bool:
        """
        Verify user email address.
        
        Args:
            user_id: User ID
            verification_token: Email verification token
            
        Returns:
            True if email verified successfully
        """
        pass
    
    @abstractmethod
    async def reset_password(self, email: str) -> bool:
        """
        Initiate password reset process.
        
        Args:
            email: User email address
            
        Returns:
            True if reset initiated successfully
        """
        pass


class IVideoGenerationService(ABC):
    """
    Video generation service interface for managing video creation workflow.
    
    Orchestrates video generation processes while maintaining separation
    of concerns from domain entities.
    """
    
    @abstractmethod
    async def create_video_session(self, 
                                 user_id: str, 
                                 config: VideoGenerationConfig) -> VideoSession:
        """
        Create a new video generation session.
        
        Args:
            user_id: User ID creating the session
            config: Video generation configuration
            
        Returns:
            Created video session entity
            
        Raises:
            VideoGenerationError: If session creation fails
        """
        pass
    
    @abstractmethod
    async def start_video_generation(self, session_id: str) -> bool:
        """
        Start video generation process for a session.
        
        Args:
            session_id: Session ID to start generation for
            
        Returns:
            True if generation started successfully
        """
        pass
    
    @abstractmethod
    async def get_generation_progress(self, session_id: str) -> Dict[str, Any]:
        """
        Get current generation progress for a session.
        
        Args:
            session_id: Session ID to get progress for
            
        Returns:
            Progress information dictionary
        """
        pass
    
    @abstractmethod
    async def cancel_generation(self, session_id: str, user_id: str) -> bool:
        """
        Cancel video generation for a session.
        
        Args:
            session_id: Session ID to cancel
            user_id: User ID requesting cancellation
            
        Returns:
            True if cancellation successful
        """
        pass
    
    @abstractmethod
    async def get_user_sessions(self, 
                              user_id: str, 
                              limit: Optional[int] = None) -> List[VideoSession]:
        """
        Get video sessions for a user.
        
        Args:
            user_id: User ID to get sessions for
            limit: Optional limit on results
            
        Returns:
            List of user's video sessions
        """
        pass
    
    @abstractmethod
    async def validate_generation_config(self, 
                                       config: VideoGenerationConfig,
                                       user: User) -> Dict[str, Any]:
        """
        Validate video generation configuration against user limits.
        
        Args:
            config: Video generation configuration
            user: User entity
            
        Returns:
            Validation result with any errors or warnings
        """
        pass
    
    @abstractmethod
    async def estimate_generation_cost(self, config: VideoGenerationConfig) -> Dict[str, Any]:
        """
        Estimate cost and resource usage for generation.
        
        Args:
            config: Video generation configuration
            
        Returns:
            Cost estimation details
        """
        pass
    
    @abstractmethod
    async def get_generation_queue_status(self) -> Dict[str, Any]:
        """
        Get current status of the generation queue.
        
        Returns:
            Queue status information
        """
        pass


class ICampaignService(ABC):
    """
    Campaign service interface for managing marketing campaigns.
    
    Orchestrates campaign lifecycle and coordinates with video generation
    while maintaining proper separation of concerns.
    """
    
    @abstractmethod
    async def create_campaign(self, 
                            user_id: str,
                            name: str,
                            description: str,
                            target_platforms: List[str]) -> Campaign:
        """
        Create a new marketing campaign.
        
        Args:
            user_id: User ID creating the campaign
            name: Campaign name
            description: Campaign description
            target_platforms: List of target platforms
            
        Returns:
            Created campaign entity
        """
        pass
    
    @abstractmethod
    async def add_video_to_campaign(self, 
                                  campaign_id: str, 
                                  video_session_id: str,
                                  user_id: str) -> bool:
        """
        Add a video session to a campaign.
        
        Args:
            campaign_id: Campaign ID
            video_session_id: Video session ID to add
            user_id: User ID making the request
            
        Returns:
            True if video added successfully
        """
        pass
    
    @abstractmethod
    async def activate_campaign(self, campaign_id: str, user_id: str) -> bool:
        """
        Activate a campaign for execution.
        
        Args:
            campaign_id: Campaign ID to activate
            user_id: User ID making the request
            
        Returns:
            True if campaign activated successfully
        """
        pass
    
    @abstractmethod
    async def get_campaign_performance(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get campaign performance metrics.
        
        Args:
            campaign_id: Campaign ID
            user_id: User ID making the request
            
        Returns:
            Campaign performance data
        """
        pass
    
    @abstractmethod
    async def get_user_campaigns(self, 
                               user_id: str,
                               status: Optional[str] = None) -> List[Campaign]:
        """
        Get campaigns for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
            
        Returns:
            List of user's campaigns
        """
        pass
    
    @abstractmethod
    async def update_campaign_progress(self, 
                                     campaign_id: str,
                                     session_id: str,
                                     progress_data: Dict[str, Any]) -> bool:
        """
        Update campaign progress when video sessions complete.
        
        Args:
            campaign_id: Campaign ID
            session_id: Video session ID
            progress_data: Progress update data
            
        Returns:
            True if update successful
        """
        pass