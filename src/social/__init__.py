"""
Social Media Integration Module
Provides autoposting functionality for various social media platforms
"""

from .instagram_autoposter import InstagramAutoPoster, InstagramCredentials, PostContent, PostingOptions
from .social_config import SocialConfigManager, SocialCredentials, PostingPreferences
from .cli_integration import add_social_commands, auto_post_if_enabled

__all__ = [
    'InstagramAutoPoster',
    'InstagramCredentials', 
    'PostContent',
    'PostingOptions',
    'SocialConfigManager',
    'SocialCredentials',
    'PostingPreferences',
    'add_social_commands',
    'auto_post_if_enabled'
]