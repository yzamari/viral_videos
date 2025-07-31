"""Core News Aggregator Components"""

from .aggregator import NewsAggregator
from .scraper_manager import ScraperManager
from .content_processor import ContentProcessor
from .composition_engine import CompositionEngine
from .channel_manager import ChannelManager

__all__ = [
    'NewsAggregator',
    'ScraperManager',
    'ContentProcessor',
    'CompositionEngine',
    'ChannelManager'
]