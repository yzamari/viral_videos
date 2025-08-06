"""News Scrapers"""

from .web_scraper import WebNewsScraper
from .base_scraper import BaseScraper
from .universal_scraper import UniversalNewsScraper
from .test_universal_scraper import TestUniversalNewsScraper, TelegramChannelScraper

__all__ = ['WebNewsScraper', 'BaseScraper', 'UniversalNewsScraper', 'TestUniversalNewsScraper', 'TelegramChannelScraper']