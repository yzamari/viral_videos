"""
JSON file loader for datasources
"""

import json
import aiofiles
from typing import List, Any, Dict
from pathlib import Path

from .base import BaseLoader
from ..models import ContentItem, DatasourceConfig
from ..exceptions import DatasourceFormatError, DatasourceProcessingError


class JsonLoader(BaseLoader):
    """Loader for JSON files"""
    
    async def load(self, config: DatasourceConfig) -> List[ContentItem]:
        """Load content from JSON file"""
        try:
            file_path = self.validate_file_path(config.source_path, config)
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            # Extract items based on item_selector or structure
            if config.item_selector:
                items_data = self._extract_with_selector(data, config.item_selector)
            elif isinstance(data, list):
                items_data = data
            elif isinstance(data, dict):
                # Try common patterns
                items_data = data.get('items', data.get('data', data.get('results', [data])))
                if not isinstance(items_data, list):
                    items_data = [items_data]
            else:
                items_data = [data]
            
            # Convert to ContentItems
            items = []
            total_tokens = 0
            
            for i, item_data in enumerate(items_data):
                # Apply item limit
                if config.max_items and len(items) >= config.max_items:
                    break
                
                # Convert item to string content
                if isinstance(item_data, str):
                    content_str = item_data
                else:
                    content_str = json.dumps(item_data, indent=2, ensure_ascii=False)
                
                # Apply content filter
                if config.content_filter and config.content_filter.lower() not in content_str.lower():
                    continue
                
                tokens = self.estimate_tokens(content_str)
                total_tokens += tokens
                
                # Check token limit
                if total_tokens > config.max_tokens:
                    self.logger.warning(f"⚠️ Reached token limit at item {i+1}")
                    break
                
                # Extract metadata if item is a dict
                metadata = {
                    "source": str(file_path),
                    "index": i,
                    "file_name": file_path.name
                }
                
                if isinstance(item_data, dict):
                    # Add common fields to metadata
                    for key in ['id', 'name', 'title', 'type', 'category']:
                        if key in item_data:
                            metadata[key] = item_data[key]
                
                item = ContentItem(
                    content=content_str,
                    type="json_item",
                    metadata=metadata,
                    tokens=tokens
                )
                
                items.append(item)
            
            self.logger.info(
                f"✅ Loaded {len(items)} items from JSON file: {file_path.name} "
                f"({total_tokens} total tokens)"
            )
            
            return items
            
        except json.JSONDecodeError as e:
            raise DatasourceFormatError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise DatasourceProcessingError(f"Failed to load JSON file: {e}")
    
    def _extract_with_selector(self, data: Any, selector: str) -> List[Any]:
        """Extract items using a simple selector syntax (e.g., 'data.items')"""
        try:
            parts = selector.split('.')
            current = data
            
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part, [])
                elif isinstance(current, list) and part.isdigit():
                    idx = int(part)
                    current = current[idx] if idx < len(current) else []
                else:
                    return []
            
            # Ensure result is a list
            if not isinstance(current, list):
                current = [current] if current else []
            
            return current
            
        except Exception as e:
            self.logger.warning(f"⚠️ Selector '{selector}' failed: {e}")
            return []