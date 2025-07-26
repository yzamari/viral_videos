"""
Folder loader for processing multiple files
"""

import asyncio
from typing import List
from pathlib import Path

from .base import BaseLoader
from .text_loader import TextFileLoader
from .json_loader import JsonLoader
from .csv_loader import CsvLoader
from ..models import ContentItem, DatasourceConfig, DatasourceType
from ..exceptions import DatasourceNotFoundError, DatasourceProcessingError


class FolderLoader(BaseLoader):
    """Loader for folders containing multiple files"""
    
    def __init__(self):
        super().__init__()
        self.loaders = {
            '.txt': TextFileLoader(),
            '.md': TextFileLoader(),
            '.json': JsonLoader(),
            '.csv': CsvLoader(),
        }
    
    async def load(self, config: DatasourceConfig) -> List[ContentItem]:
        """Load content from all files in a folder"""
        try:
            folder_path = Path(config.source_path).resolve()
            
            if not folder_path.exists():
                raise DatasourceNotFoundError(f"Folder not found: {folder_path}")
            
            if not folder_path.is_dir():
                raise DatasourceProcessingError(f"Path is not a folder: {folder_path}")
            
            items = []
            total_tokens = 0
            processed_files = 0
            
            # Get all files with allowed extensions
            files = []
            for ext in config.allowed_extensions:
                files.extend(folder_path.glob(f"*{ext}"))
            
            # Sort files for consistent ordering
            files.sort()
            
            self.logger.info(f"📁 Found {len(files)} files to process in {folder_path.name}")
            
            for file_path in files:
                # Check if we've reached limits
                if config.max_items and len(items) >= config.max_items:
                    self.logger.info(f"📊 Reached item limit ({config.max_items})")
                    break
                
                if total_tokens >= config.max_tokens:
                    self.logger.info(f"📊 Reached token limit ({config.max_tokens})")
                    break
                
                # Get appropriate loader
                loader = self.loaders.get(file_path.suffix.lower())
                if not loader:
                    self.logger.warning(f"⚠️ No loader for file type: {file_path.suffix}")
                    continue
                
                try:
                    # Create a sub-config for the individual file
                    file_config = DatasourceConfig(
                        source_type=DatasourceType.TEXT_FILE,
                        source_path=str(file_path),
                        item_selector=config.item_selector,
                        content_filter=config.content_filter,
                        max_items=None,  # Let folder loader control limits
                        extract_topics=config.extract_topics,
                        summarize=config.summarize,
                        chunk_size=config.chunk_size,
                        max_tokens=config.max_tokens - total_tokens,  # Remaining tokens
                        context_template=config.context_template,
                        include_metadata=config.include_metadata,
                        allowed_extensions=config.allowed_extensions,
                        max_file_size_mb=config.max_file_size_mb,
                        allow_urls=config.allow_urls
                    )
                    
                    # Load file content
                    file_items = await loader.load(file_config)
                    
                    # Add folder context to metadata
                    for item in file_items:
                        item.metadata['folder'] = folder_path.name
                        item.metadata['folder_path'] = str(folder_path)
                    
                    items.extend(file_items)
                    total_tokens += sum(item.tokens or 0 for item in file_items)
                    processed_files += 1
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to load {file_path.name}: {e}")
                    continue
            
            self.logger.info(
                f"✅ Loaded {len(items)} items from {processed_files} files "
                f"in folder: {folder_path.name} ({total_tokens} total tokens)"
            )
            
            return items
            
        except Exception as e:
            raise DatasourceProcessingError(f"Failed to load folder: {e}")