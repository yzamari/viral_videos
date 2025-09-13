"""
Google Cloud Authentication Provider
"""
import subprocess
import time
from typing import Optional
from ...interfaces.auth import AuthProvider, AuthType, Credentials

class GoogleCloudAuthProvider(AuthProvider):
    """Google Cloud authentication using gcloud CLI or service account"""
    
    def __init__(self, 
                 project_id: Optional[str] = None,
                 service_account_path: Optional[str] = None,
                 use_application_default: bool = True):
        self.project_id = project_id
        self.service_account_path = service_account_path
        self.use_application_default = use_application_default
    
    async def get_credentials(self) -> Credentials:
        """Get Google Cloud credentials"""
        try:
            # Try application default credentials first
            if self.use_application_default:
                result = subprocess.run(
                    ["gcloud", "auth", "application-default", "print-access-token"],
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                # Use regular gcloud auth
                result = subprocess.run(
                    ["gcloud", "auth", "print-access-token"],
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            access_token = result.stdout.strip()
            
            # Token expires in 1 hour
            expires_at = time.time() + 3600
            
            return Credentials(
                auth_type=AuthType.GOOGLE_CLOUD,
                access_token=access_token,
                expires_at=expires_at,
                metadata={'project_id': self.project_id}
            )
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get Google Cloud credentials: {e}")
    
    async def refresh_credentials(self, credentials: Credentials) -> Credentials:
        """Refresh Google Cloud credentials"""
        # For gcloud, we just get new credentials
        return await self.get_credentials()
    
    def get_auth_type(self) -> AuthType:
        """Get authentication type"""
        return AuthType.GOOGLE_CLOUD