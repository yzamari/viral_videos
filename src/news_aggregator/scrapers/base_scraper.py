"""Base scraper interface"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.content_models import ContentItem, NewsSource


class BaseScraper(ABC):
    """Base class for all content scrapers"""
    
    @abstractmethod
    async def scrape(self, source: NewsSource) -> List[ContentItem]:
        """Scrape content from source"""
        pass
    
    @abstractmethod
    async def validate_source(self, source: NewsSource) -> bool:
        """Validate if source is accessible"""
        pass
    
    def extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common metadata from raw data"""
        return {
            "scraper_type": self.__class__.__name__,
            "scrape_timestamp": datetime.now().isoformat()
        }