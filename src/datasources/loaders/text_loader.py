"""
Text file loaders for datasources
"""

from typing import List
import aiofiles
from pathlib import Path

from .base import BaseLoader
from ..models import ContentItem, DatasourceConfig
from ..exceptions import DatasourceProcessingError


class TextFileLoader(BaseLoader):
    """Loader for single text files"""
    
    async def load(self, config: DatasourceConfig) -> List[ContentItem]:
        """Load content from a single text file"""
        try:
            file_path = self.validate_file_path(config.source_path, config)
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Estimate tokens
            tokens = self.estimate_tokens(content)
            
            # Create single content item
            item = ContentItem(
                content=content.strip(),
                type="text_document",
                metadata=self.extract_metadata(file_path),
                tokens=tokens
            )
            
            self.logger.info(f"✅ Loaded text file: {file_path.name} ({tokens} tokens)")
            
            return [item]
            
        except Exception as e:
            raise DatasourceProcessingError(f"Failed to load text file: {e}")


class TextListLoader(BaseLoader):
    """Loader for text files containing lists of items (one per line)"""
    
    async def load(self, config: DatasourceConfig) -> List[ContentItem]:
        """Load content from a text file with list items"""
        try:
            file_path = self.validate_file_path(config.source_path, config)
            
            items = []
            total_tokens = 0
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()
            
            # Process each non-empty line as an item
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Apply item limit if specified
                if config.max_items and len(items) >= config.max_items:
                    break
                
                # Apply content filter if specified
                if config.content_filter and config.content_filter.lower() not in line.lower():
                    continue
                
                tokens = self.estimate_tokens(line)
                total_tokens += tokens
                
                # Check token limit
                if total_tokens > config.max_tokens:
                    self.logger.warning(f"⚠️ Reached token limit at item {i+1}")
                    break
                
                item = ContentItem(
                    content=line,
                    type="list_item",
                    metadata={
                        "source": str(file_path),
                        "line_number": i + 1,
                        "file_name": file_path.name
                    },
                    tokens=tokens
                )
                
                items.append(item)
            
            self.logger.info(
                f"✅ Loaded {len(items)} items from list file: {file_path.name} "
                f"({total_tokens} total tokens)"
            )
            
            return items
            
        except Exception as e:
            raise DatasourceProcessingError(f"Failed to load text list: {e}")