"""
CSV file loader for datasources
"""

import csv
import aiofiles
from typing import List
from pathlib import Path
import io

from .base import BaseLoader
from ..models import ContentItem, DatasourceConfig
from ..exceptions import DatasourceFormatError, DatasourceProcessingError


class CsvLoader(BaseLoader):
    """Loader for CSV files"""
    
    async def load(self, config: DatasourceConfig) -> List[ContentItem]:
        """Load content from CSV file"""
        try:
            file_path = self.validate_file_path(config.source_path, config)
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(content))
            
            items = []
            total_tokens = 0
            
            for i, row in enumerate(csv_reader):
                # Apply item limit
                if config.max_items and len(items) >= config.max_items:
                    break
                
                # Convert row to formatted content
                content_parts = []
                for key, value in row.items():
                    if value:  # Skip empty values
                        content_parts.append(f"{key}: {value}")
                
                content_str = "\n".join(content_parts)
                
                # Apply content filter
                if config.content_filter and config.content_filter.lower() not in content_str.lower():
                    continue
                
                tokens = self.estimate_tokens(content_str)
                total_tokens += tokens
                
                # Check token limit
                if total_tokens > config.max_tokens:
                    self.logger.warning(f"⚠️ Reached token limit at row {i+1}")
                    break
                
                # Create metadata from row data
                metadata = {
                    "source": str(file_path),
                    "row_number": i + 1,
                    "file_name": file_path.name,
                    **{k: v for k, v in row.items() if len(str(v)) < 100}  # Add short values to metadata
                }
                
                item = ContentItem(
                    content=content_str,
                    type="csv_row",
                    metadata=metadata,
                    tokens=tokens
                )
                
                items.append(item)
            
            if not items and csv_reader.fieldnames:
                # If no data rows, at least show the headers
                headers = f"CSV Headers: {', '.join(csv_reader.fieldnames)}"
                items.append(ContentItem(
                    content=headers,
                    type="csv_headers",
                    metadata={"source": str(file_path)},
                    tokens=self.estimate_tokens(headers)
                ))
            
            self.logger.info(
                f"✅ Loaded {len(items)} rows from CSV file: {file_path.name} "
                f"({total_tokens} total tokens)"
            )
            
            return items
            
        except csv.Error as e:
            raise DatasourceFormatError(f"Invalid CSV format: {e}")
        except Exception as e:
            raise DatasourceProcessingError(f"Failed to load CSV file: {e}")