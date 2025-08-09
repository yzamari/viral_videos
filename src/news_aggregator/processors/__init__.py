"""
Content processors module for the News Aggregator system.

This module contains classes responsible for processing, analyzing, and transforming content
following the Single Responsibility Principle.
"""

from .content_processor import NewsContentProcessor
from .content_analyzer import ContentAnalyzer
from .duplicate_detector import DuplicateDetector
from .media_downloader import MediaDownloader

__all__ = [
    'NewsContentProcessor',
    'ContentAnalyzer',
    'DuplicateDetector',
    'MediaDownloader'
]