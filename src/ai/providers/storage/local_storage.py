"""
Local Filesystem Storage Provider
"""
import os
import shutil
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncIterator
from ...interfaces.storage import StorageProvider, StorageConfig, StorageObject, StorageType

class LocalStorageProvider(StorageProvider):
    """Local filesystem storage implementation"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.base_path = Path(config.base_path or "./storage")
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, key: str) -> Path:
        """Get full filesystem path for key"""
        # Sanitize key to prevent directory traversal
        safe_key = key.replace("..", "").lstrip("/")
        return self.base_path / safe_key
    
    async def save(self, key: str, data: bytes,
                  content_type: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> StorageObject:
        """Save data to local filesystem"""
        file_path = self._get_full_path(key)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write data
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(data)
        
        # Save metadata if provided
        if metadata:
            metadata_path = file_path.with_suffix('.metadata.json')
            import json
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata))
        
        # Get file stats
        stat = file_path.stat()
        
        return StorageObject(
            key=key,
            size=len(data),
            content_type=content_type,
            metadata=metadata,
            last_modified=stat.st_mtime,
            url=str(file_path)
        )
    
    async def load(self, key: str) -> bytes:
        """Load data from local filesystem"""
        file_path = self._get_full_path(key)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Object not found: {key}")
        
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()
    
    async def stream(self, key: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        """Stream data from local filesystem"""
        file_path = self._get_full_path(key)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Object not found: {key}")
        
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    async def exists(self, key: str) -> bool:
        """Check if object exists"""
        file_path = self._get_full_path(key)
        return file_path.exists()
    
    async def delete(self, key: str) -> bool:
        """Delete object from filesystem"""
        file_path = self._get_full_path(key)
        
        if not file_path.exists():
            return False
        
        file_path.unlink()
        
        # Delete metadata if exists
        metadata_path = file_path.with_suffix('.metadata.json')
        if metadata_path.exists():
            metadata_path.unlink()
        
        return True
    
    async def list(self, prefix: Optional[str] = None,
                  limit: Optional[int] = None) -> List[StorageObject]:
        """List objects in storage"""
        objects = []
        
        if prefix:
            search_path = self._get_full_path(prefix)
        else:
            search_path = self.base_path
        
        # Walk directory tree
        count = 0
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith('.metadata.json'):
                    continue
                
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.base_path)
                key = str(relative_path)
                
                stat = file_path.stat()
                
                objects.append(StorageObject(
                    key=key,
                    size=stat.st_size,
                    last_modified=stat.st_mtime,
                    url=str(file_path)
                ))
                
                count += 1
                if limit and count >= limit:
                    return objects
        
        return objects
    
    async def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get file URL (local path)"""
        file_path = self._get_full_path(key)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Object not found: {key}")
        
        # For local storage, just return the file path
        return f"file://{file_path.absolute()}"
    
    async def copy(self, source_key: str, dest_key: str) -> StorageObject:
        """Copy object within storage"""
        source_path = self._get_full_path(source_key)
        dest_path = self._get_full_path(dest_key)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source object not found: {source_key}")
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)
        
        # Copy metadata if exists
        source_metadata = source_path.with_suffix('.metadata.json')
        if source_metadata.exists():
            dest_metadata = dest_path.with_suffix('.metadata.json')
            shutil.copy2(source_metadata, dest_metadata)
        
        stat = dest_path.stat()
        
        return StorageObject(
            key=dest_key,
            size=stat.st_size,
            last_modified=stat.st_mtime,
            url=str(dest_path)
        )
    
    async def move(self, source_key: str, dest_key: str) -> StorageObject:
        """Move object within storage"""
        source_path = self._get_full_path(source_key)
        dest_path = self._get_full_path(dest_key)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source object not found: {source_key}")
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(dest_path))
        
        # Move metadata if exists
        source_metadata = source_path.with_suffix('.metadata.json')
        if source_metadata.exists():
            dest_metadata = dest_path.with_suffix('.metadata.json')
            shutil.move(str(source_metadata), str(dest_metadata))
        
        stat = dest_path.stat()
        
        return StorageObject(
            key=dest_key,
            size=stat.st_size,
            last_modified=stat.st_mtime,
            url=str(dest_path)
        )