"""
Video composers module for the News Aggregator system.

This module contains classes responsible for video composition and media handling
following the Single Responsibility Principle.
"""

from .video_composer import NewsVideoComposer
from .scraped_media_composer import ScrapedMediaComposer
from .multi_language_composer import MultiLanguageComposer

__all__ = [
    'NewsVideoComposer',
    'ScrapedMediaComposer',
    'MultiLanguageComposer'
]