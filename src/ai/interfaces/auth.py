"""
Authentication Provider Interface
Provides abstraction for different authentication methods
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class AuthType(Enum):
    """Types of authentication"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    SERVICE_ACCOUNT = "service_account"
    GOOGLE_CLOUD = "google_cloud"
    AWS_IAM = "aws_iam"
    AZURE_AD = "azure_ad"

@dataclass
class Credentials:
    """Authentication credentials"""
    auth_type: AuthType
    access_token: Optional[str] = None
    api_key: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def is_expired(self) -> bool:
        """Check if credentials are expired"""
        if self.expires_at is None:
            return False
        import time
        return time.time() > self.expires_at
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for authentication"""
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

class AuthProvider(ABC):
    """Abstract authentication provider interface"""
    
    @abstractmethod
    async def get_credentials(self) -> Credentials:
        """Get authentication credentials"""
        pass
    
    @abstractmethod
    async def refresh_credentials(self, credentials: Credentials) -> Credentials:
        """Refresh expired credentials"""
        pass
    
    @abstractmethod
    def get_auth_type(self) -> AuthType:
        """Get the authentication type"""
        pass
    
    async def ensure_valid_credentials(self, credentials: Optional[Credentials] = None) -> Credentials:
        """Ensure credentials are valid, refreshing if needed"""
        if credentials is None or credentials.is_expired():
            return await self.get_credentials()
        return credentials