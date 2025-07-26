"""
Data models for the datasources system
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class DatasourceType(Enum):
    """Supported datasource types"""
    TEXT_FILE = "text_file"           # Single text file
    TEXT_LIST = "text_list"           # File with list of items
    FOLDER = "folder"                 # Directory of files
    JSON = "json"                     # Structured JSON data
    CSV = "csv"                       # Tabular data
    URL = "url"                       # Web content
    API = "api"                       # API endpoint


@dataclass
class ContentItem:
    """Individual content item from datasource"""
    content: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens: Optional[int] = None
    summary: Optional[str] = None
    topics: List[str] = field(default_factory=list)


@dataclass
class DatasourceConfig:
    """Configuration for datasource loading and processing"""
    source_type: DatasourceType
    source_path: str  # File path, folder path, or URL
    
    # Processing options
    item_selector: Optional[str] = None  # For selecting specific items
    content_filter: Optional[str] = None  # Filter criteria
    max_items: Optional[int] = None      # Limit number of items
    
    # Transformation options
    extract_topics: bool = True          # Extract main topics
    summarize: bool = False              # Summarize long content
    chunk_size: Optional[int] = None     # For chunking large content
    max_tokens: int = 50000              # Maximum tokens to process
    
    # Context options
    context_template: Optional[str] = None  # How to format for AI
    include_metadata: bool = True           # Include source metadata
    
    # Security options
    allowed_extensions: List[str] = field(default_factory=lambda: ['.txt', '.md', '.json', '.csv'])
    max_file_size_mb: int = 100          # Maximum file size in MB
    allow_urls: bool = False             # Whether to allow URL datasources


@dataclass
class DatasourceContent:
    """Processed datasource content ready for video generation"""
    items: List[ContentItem]
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    total_tokens: int = 0
    source_type: DatasourceType = DatasourceType.TEXT_FILE
    
    def get_formatted_content(self, max_items: Optional[int] = None) -> str:
        """Get formatted content for mission enhancement"""
        items_to_format = self.items[:max_items] if max_items else self.items
        
        formatted_items = []
        for i, item in enumerate(items_to_format, 1):
            formatted_items.append(f"{i}. {item.content}")
        
        return "\n".join(formatted_items)
    
    def get_topics_summary(self) -> str:
        """Get a summary of main topics"""
        if not self.topics:
            return "No specific topics identified"
        
        return f"Main topics: {', '.join(self.topics[:5])}"
    
    def to_context_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for AI agent context"""
        return {
            'items': [
                {
                    'content': item.content,
                    'type': item.type,
                    'metadata': item.metadata
                }
                for item in self.items
            ],
            'summary': self.summary,
            'topics': self.topics,
            'total_items': len(self.items),
            'source_type': self.source_type.value
        }