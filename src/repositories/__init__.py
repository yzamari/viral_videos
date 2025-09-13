"""
Repository package for data access abstraction.

This package implements the Repository pattern to abstract data access
and provide clean separation between domain logic and data persistence.
"""

from .interfaces import IRepository, IUserRepository, IVideoSessionRepository, ICampaignRepository
from .user_repository import UserRepository
from .video_session_repository import VideoSessionRepository  
from .campaign_repository import CampaignRepository

__all__ = [
    'IRepository', 'IUserRepository', 'IVideoSessionRepository', 'ICampaignRepository',
    'UserRepository', 'VideoSessionRepository', 'CampaignRepository'
]