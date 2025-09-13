"""
API Key Authentication Provider
"""
from typing import Optional, Dict
from ...interfaces.auth import AuthProvider, AuthType, Credentials

class APIKeyAuthProvider(AuthProvider):
    """Simple API key authentication"""
    
    def __init__(self, 
                 api_key: str,
                 header_name: str = "X-API-Key",
                 prefix: Optional[str] = None):
        self.api_key = api_key
        self.header_name = header_name
        self.prefix = prefix
    
    async def get_credentials(self) -> Credentials:
        """Get API key credentials"""
        formatted_key = f"{self.prefix} {self.api_key}" if self.prefix else self.api_key
        
        return Credentials(
            auth_type=AuthType.API_KEY,
            api_key=formatted_key,
            metadata={'header_name': self.header_name}
        )
    
    async def refresh_credentials(self, credentials: Credentials) -> Credentials:
        """API keys don't need refreshing"""
        return credentials
    
    def get_auth_type(self) -> AuthType:
        """Get authentication type"""
        return AuthType.API_KEY
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for authentication"""
        formatted_key = f"{self.prefix} {self.api_key}" if self.prefix else self.api_key
        return {self.header_name: formatted_key}