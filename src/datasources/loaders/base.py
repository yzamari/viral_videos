"""
Base loader class for datasources
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import os
from pathlib import Path

from ..models import ContentItem, DatasourceConfig
from ..exceptions import DatasourceNotFoundError, DatasourceSizeError, DatasourceSecurityError
from ...utils.logging_config import get_logger

logger = get_logger(__name__)


class BaseLoader(ABC):
    """Abstract base class for datasource loaders"""
    
    def __init__(self):
        self.logger = logger
    
    @abstractmethod
    async def load(self, config: DatasourceConfig) -> List[ContentItem]:
        """Load content from datasource"""
        pass
    
    def validate_file_path(self, file_path: str, config: DatasourceConfig) -> Path:
        """Validate file path for security and existence"""
        path = Path(file_path).resolve()
        
        # Check if file exists
        if not path.exists():
            raise DatasourceNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        if path.is_file():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > config.max_file_size_mb:
                raise DatasourceSizeError(
                    f"File size {size_mb:.1f}MB exceeds limit of {config.max_file_size_mb}MB"
                )
        
        # Check file extension
        if path.is_file() and config.allowed_extensions:
            if path.suffix.lower() not in config.allowed_extensions:
                raise DatasourceSecurityError(
                    f"File type {path.suffix} not allowed. "
                    f"Allowed types: {', '.join(config.allowed_extensions)}"
                )
        
        return path
    
    def extract_metadata(self, file_path: Path) -> dict:
        """Extract basic metadata from file"""
        stat = file_path.stat()
        return {
            'source': str(file_path),
            'size_bytes': stat.st_size,
            'modified': stat.st_mtime,
            'name': file_path.name,
            'extension': file_path.suffix
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4