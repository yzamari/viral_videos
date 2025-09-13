"""
Storage Provider Interface
Provides abstraction for different storage backends
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, AsyncIterator
from enum import Enum
import io

class StorageType(Enum):
    """Types of storage backends"""
    LOCAL = "local"
    GOOGLE_CLOUD_STORAGE = "gcs"
    AWS_S3 = "s3"
    AZURE_BLOB = "azure_blob"
    FTP = "ftp"
    MEMORY = "memory"  # For testing

@dataclass
class StorageObject:
    """Represents a stored object"""
    key: str
    size: int
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = None
    last_modified: Optional[float] = None
    etag: Optional[str] = None
    url: Optional[str] = None

@dataclass
class StorageConfig:
    """Storage configuration"""
    storage_type: StorageType
    bucket_name: Optional[str] = None
    base_path: Optional[str] = None
    credentials: Optional[Any] = None
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    public_read: bool = False

class StorageProvider(ABC):
    """Abstract storage provider interface"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
    
    @abstractmethod
    async def save(self, key: str, data: bytes, 
                  content_type: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> StorageObject:
        """Save data to storage"""
        pass
    
    @abstractmethod
    async def load(self, key: str) -> bytes:
        """Load data from storage"""
        pass
    
    @abstractmethod
    async def stream(self, key: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        """Stream data from storage in chunks"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if object exists"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete object from storage"""
        pass
    
    @abstractmethod
    async def list(self, prefix: Optional[str] = None, 
                  limit: Optional[int] = None) -> List[StorageObject]:
        """List objects in storage"""
        pass
    
    @abstractmethod
    async def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get URL for object (signed if needed)"""
        pass
    
    @abstractmethod
    async def copy(self, source_key: str, dest_key: str) -> StorageObject:
        """Copy object within storage"""
        pass
    
    @abstractmethod
    async def move(self, source_key: str, dest_key: str) -> StorageObject:
        """Move object within storage"""
        pass
    
    async def save_file(self, key: str, file_path: str, 
                       content_type: Optional[str] = None) -> StorageObject:
        """Save file to storage"""
        with open(file_path, 'rb') as f:
            data = f.read()
        return await self.save(key, data, content_type)
    
    async def load_file(self, key: str, file_path: str) -> None:
        """Load object to file"""
        data = await self.load(key)
        with open(file_path, 'wb') as f:
            f.write(data)
    
    async def save_stream(self, key: str, stream: io.BytesIO,
                         content_type: Optional[str] = None) -> StorageObject:
        """Save stream to storage"""
        data = stream.read()
        return await self.save(key, data, content_type)