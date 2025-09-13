"""
Authentication Controller handling user authentication and authorization.

This controller follows the Single Responsibility Principle by handling
only authentication-related endpoints and delegating business logic to services.
"""

import logging
from typing import Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, validator
from datetime import timedelta

from src.api.controllers.base_controller import BaseController
from src.services.interfaces import IAuthenticationService
from src.domain.entities.user import UserRole
from src.utils.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


# Request/Response models
class UserRegistrationRequest(BaseModel):
    """User registration request model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    organization: str = Field(None, max_length=200)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower()


class UserLoginRequest(BaseModel):
    """User login request model"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class PasswordChangeRequest(BaseModel):
    """Password change request model"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Dict[str, Any]


class UserProfileResponse(BaseModel):
    """User profile response model"""
    id: str
    username: str
    email: str
    organization: str = None
    role: str
    status: str
    created_at: str
    email_verified: bool
    usage_summary: Dict[str, Any]


class AuthController(BaseController):
    """
    Authentication controller implementing user authentication endpoints.
    
    This controller maintains thin controller logic by delegating all
    business operations to the authentication service.
    """
    
    def __init__(self, authentication_service: IAuthenticationService):
        """
        Initialize authentication controller.
        
        Args:
            authentication_service: Authentication service for business logic
        """
        super().__init__(authentication_service)
        self._auth_service = authentication_service
    
    async def register_user(self, request: UserRegistrationRequest) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            request: User registration request
            
        Returns:
            Registration response with token
            
        Raises:
            HTTPException: If registration fails
        """
        try:
            self.log_request("POST /auth/register", username=request.username)
            
            # Create user through service
            user = await self._auth_service.register_user(
                username=request.username,
                email=request.email,
                password=request.password,
                organization=request.organization
            )
            
            # Create access token
            access_token = await self._auth_service.create_access_token(user)
            
            # Prepare response
            response_data = {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 30 * 60,  # 30 minutes
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "organization": user.organization,
                    "role": user.role.value,
                    "status": user.status.value
                }
            }
            
            self.log_response("POST /auth/register", True)
            return self.create_success_response(
                data=response_data,
                message="User registered successfully"
            )
            
        except AuthenticationError as e:
            logger.warning(f"Registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected registration error: {e}")
            raise self.handle_service_exception(e)
    
    async def login_user(self, form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, Any]:
        """
        Authenticate user and return access token.
        
        Args:
            form_data: OAuth2 password form data
            
        Returns:
            Login response with token
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            self.log_request("POST /auth/login", username=form_data.username)
            
            # Authenticate user
            user = await self._auth_service.authenticate_user(
                username=form_data.username,
                password=form_data.password
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=30)
            access_token = await self._auth_service.create_access_token(
                user=user,
                expires_delta=access_token_expires
            )
            
            # Prepare response
            response_data = {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": int(access_token_expires.total_seconds()),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "organization": user.organization,
                    "role": user.role.value,
                    "status": user.status.value,
                    "last_login": user.last_login_at.isoformat() if user.last_login_at else None
                }
            }
            
            self.log_response("POST /auth/login", True)
            return self.create_success_response(
                data=response_data,
                message="Login successful"
            )
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise self.handle_service_exception(e)
    
    async def get_current_user_profile(self, token: str) -> Dict[str, Any]:
        """
        Get current user profile information.
        
        Args:
            token: JWT access token
            
        Returns:
            User profile information
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("GET /auth/me", user_id=user.id)
            
            # Prepare profile response
            profile_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "organization": user.organization,
                "role": user.role.value,
                "status": user.status.value,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "email_verified": user.is_email_verified(),
                "trial_info": {
                    "is_trial": user.is_trial_user(),
                    "trial_expires_at": user.trial_expires_at.isoformat() if user.trial_expires_at else None,
                    "remaining_days": user.get_remaining_trial_days() if user.is_trial_user() else None
                },
                "usage_summary": user.get_usage_summary()
            }
            
            self.log_response("GET /auth/me", True)
            return self.create_success_response(
                data=profile_data,
                message="Profile retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Profile retrieval error: {e}")
            raise self.handle_service_exception(e)
    
    async def change_password(self, token: str, request: PasswordChangeRequest) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            token: JWT access token
            request: Password change request
            
        Returns:
            Password change confirmation
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("POST /auth/change-password", user_id=user.id)
            
            # Change password through service
            success = await self._auth_service.change_password(
                user_id=user.id,
                old_password=request.old_password,
                new_password=request.new_password
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password change failed"
                )
            
            self.log_response("POST /auth/change-password", True)
            return self.create_success_response(
                message="Password changed successfully"
            )
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            raise self.handle_service_exception(e)
    
    async def refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Refresh user access token.
        
        Args:
            token: Current JWT access token
            
        Returns:
            New access token
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("POST /auth/refresh", user_id=user.id)
            
            # Generate new token
            new_token = await self._auth_service.refresh_access_token(user)
            
            response_data = {
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": 30 * 60  # 30 minutes
            }
            
            self.log_response("POST /auth/refresh", True)
            return self.create_success_response(
                data=response_data,
                message="Token refreshed successfully"
            )
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise self.handle_service_exception(e)
    
    async def verify_email(self, user_id: str, verification_token: str) -> Dict[str, Any]:
        """
        Verify user email address.
        
        Args:
            user_id: User ID
            verification_token: Email verification token
            
        Returns:
            Email verification confirmation
        """
        try:
            self.log_request("POST /auth/verify-email", user_id=user_id)
            
            # Verify email through service
            success = await self._auth_service.verify_email(user_id, verification_token)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email verification failed"
                )
            
            self.log_response("POST /auth/verify-email", True)
            return self.create_success_response(
                message="Email verified successfully"
            )
            
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            raise self.handle_service_exception(e)
    
    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset.
        
        Args:
            email: User email address
            
        Returns:
            Password reset request confirmation
        """
        try:
            self.log_request("POST /auth/reset-password", email=email)
            
            # Request password reset through service
            success = await self._auth_service.reset_password(email)
            
            # Always return success to prevent email enumeration
            self.log_response("POST /auth/reset-password", True)
            return self.create_success_response(
                message="If the email exists, a password reset link has been sent"
            )
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            # Don't expose internal errors for security
            return self.create_success_response(
                message="If the email exists, a password reset link has been sent"
            )