"""
Theme System
Provides consistent visual themes for video generation
"""

from .models.theme import (
    Theme,
    ThemeCategory,
    TransitionStyle,
    VideoTemplate,
    LogoConfiguration,
    LowerThirdsStyle,
    CaptionStyle,
    BrandKit
)

from .managers.theme_manager import ThemeManager
from .managers.themed_session_manager import ThemedSessionManager

from .presets.news_edition import NewsEditionTheme
from .presets.sports_theme import SportsTheme
from .presets.tech_theme import TechTheme
from .presets.entertainment_theme import EntertainmentTheme

__all__ = [
    # Models
    "Theme",
    "ThemeCategory",
    "TransitionStyle",
    "VideoTemplate",
    "LogoConfiguration",
    "LowerThirdsStyle",
    "CaptionStyle",
    "BrandKit",
    
    # Managers
    "ThemeManager",
    "ThemedSessionManager",
    
    # Presets
    "NewsEditionTheme",
    "SportsTheme",
    "TechTheme",
    "EntertainmentTheme"
]