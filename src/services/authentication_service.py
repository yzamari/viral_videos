"""
Authentication Service implementation providing user authentication and authorization.

This service follows the Single Responsibility Principle by handling only
authentication-related business logic.
"""

import uuid
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from src.domain.entities.user import User, UserRole, UserStatus
from src.repositories.interfaces import IUserRepository
from src.services.interfaces import IAuthenticationService
from src.utils.exceptions import AuthenticationError, RepositoryError

logger = logging.getLogger(__name__)


class AuthenticationService(IAuthenticationService):
    """
    Authentication service implementation with JWT token management.
    
    Provides secure user authentication, registration, and token management
    while maintaining proper separation from infrastructure concerns.
    """
    
    def __init__(self, 
                 user_repository: IUserRepository,
                 secret_key: str = "your-secret-key-change-in-production",
                 algorithm: str = "HS256",
                 access_token_expire_minutes: int = 30):
        """
        Initialize authentication service.
        
        Args:
            user_repository: User repository for data access
            secret_key: JWT signing secret key
            algorithm: JWT algorithm to use
            access_token_expire_minutes: Token expiration time in minutes
        """
        self._user_repository = user_repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
    
    async def register_user(self, 
                          username: str, 
                          email: str, 
                          password: str,
                          organization: Optional[str] = None) -> User:
        """
        Register a new user with validation and duplicate checking.
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password
            organization: Optional organization name
            
        Returns:
            Created user entity
            
        Raises:
            AuthenticationError: If registration fails
        """
        try:
            # Validate input parameters
            self._validate_registration_input(username, email, password)
            
            # Check for duplicate username
            existing_user = await self._user_repository.get_by_username(username)
            if existing_user:
                raise AuthenticationError("Username already exists")
            
            # Check for duplicate email
            existing_email = await self._user_repository.get_by_email(email)
            if existing_email:
                raise AuthenticationError("Email already registered")
            
            # Create new user entity
            user_id = str(uuid.uuid4())
            user = User.create_new_user(
                user_id=user_id,
                username=username,
                email=email,
                password=password,
                organization=organization,
                role=UserRole.TRIAL  # New users start with trial
            )
            
            # Save user to repository
            await self._user_repository.save(user)
            
            logger.info(f"User registered successfully: {username} ({email})")
            return user
            
        except RepositoryError as e:
            logger.error(f"Repository error during user registration: {e}")
            raise AuthenticationError(f"Registration failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during user registration: {e}")
            raise AuthenticationError(f"Registration failed: {e}")
    
    def _validate_registration_input(self, username: str, email: str, password: str) -> None:
        """Validate registration input parameters"""
        if not username or len(username.strip()) < 3:
            raise AuthenticationError("Username must be at least 3 characters long")
            
        if not email or '@' not in email:
            raise AuthenticationError("Valid email address is required")
            
        if not password or len(password) < 8:
            raise AuthenticationError("Password must be at least 8 characters long")
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/password.
        
        Supports authentication with either username or email address.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User entity if authentication succeeds, None otherwise
        """
        try:
            if not username or not password:
                return None
            
            # Try to find user by username first
            user = await self._user_repository.get_by_username(username)
            
            # If not found, try by email
            if not user:
                user = await self._user_repository.get_by_email(username)
            
            if not user:
                logger.warning(f"Authentication attempt for non-existent user: {username}")
                return None
            
            # Verify password
            if not user.verify_password(password):
                logger.warning(f"Failed password verification for user: {username}")
                return None
            
            # Check if user account is active
            if not user.is_active():
                logger.warning(f"Authentication attempt for inactive user: {username}")
                return None
            
            # Check if trial has expired
            if user.is_trial_expired():
                # Update user status to trial expired
                user.status = UserStatus.TRIAL_EXPIRED
                await self._user_repository.save(user)
                logger.warning(f"Authentication attempt for expired trial user: {username}")
                return None
            
            # Update last login timestamp
            await self._user_repository.update_last_login(user.id)
            
            logger.info(f"User authenticated successfully: {username}")
            return user
            
        except RepositoryError as e:
            logger.error(f"Repository error during authentication: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return None
    
    async def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token for user.
        
        Args:
            user: User entity to create token for
            expires_delta: Optional expiration time delta
            
        Returns:
            JWT access token string
        """
        try:
            # Calculate expiration time
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self._access_token_expire_minutes)
            
            # Create token payload
            payload = {
                "sub": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access_token"
            }
            
            # Encode and return JWT token
            token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
            
            logger.debug(f"Access token created for user: {user.username}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise AuthenticationError(f"Token creation failed: {e}")
    
    async def verify_access_token(self, token: str) -> Optional[User]:
        """
        Verify JWT access token and return user.
        
        Args:
            token: JWT access token
            
        Returns:
            User entity if token is valid, None otherwise
        """
        try:
            if not token:
                return None
            
            # Decode and verify token
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            
            # Extract user ID from token
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Token missing user ID")
                return None
            
            # Verify token type
            token_type = payload.get("type")
            if token_type != "access_token":
                logger.warning(f"Invalid token type: {token_type}")
                return None
            
            # Load user from repository
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"Token verification failed - user not found: {user_id}")
                return None
            
            # Verify user is still active
            if not user.is_active():
                logger.warning(f"Token verification failed - user not active: {user_id}")
                return None
            
            return user
            
        except jwt.ExpiredSignatureError:
            logger.debug("Token verification failed - token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed - invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return None
    
    async def refresh_access_token(self, user: User) -> str:
        """
        Refresh access token for user.
        
        Args:
            user: User entity to refresh token for
            
        Returns:
            New JWT access token
        """
        try:
            # Verify user is still active and valid
            current_user = await self._user_repository.get_by_id(user.id)
            if not current_user or not current_user.is_active():
                raise AuthenticationError("User not active - cannot refresh token")
            
            # Create new token
            return await self.create_access_token(current_user)
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise AuthenticationError(f"Token refresh failed: {e}")
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password with validation.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        try:
            # Load user
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                raise AuthenticationError("User not found")
            
            # Change password (includes validation)
            user.change_password(old_password, new_password)
            
            # Save updated user
            await self._user_repository.save(user)
            
            logger.info(f"Password changed successfully for user: {user.username}")
            return True
            
        except ValueError as e:
            logger.warning(f"Password change validation error: {e}")
            raise AuthenticationError(str(e))
        except RepositoryError as e:
            logger.error(f"Repository error during password change: {e}")
            raise AuthenticationError("Password change failed")
        except Exception as e:
            logger.error(f"Unexpected error during password change: {e}")
            raise AuthenticationError("Password change failed")
    
    async def verify_email(self, user_id: str, verification_token: str) -> bool:
        """
        Verify user email address.
        
        Args:
            user_id: User ID
            verification_token: Email verification token
            
        Returns:
            True if email verified successfully
        """
        try:
            # Load user
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                return False
            
            # In a real implementation, you would validate the verification token
            # For now, just mark email as verified
            user.verify_email()
            
            # Save updated user
            await self._user_repository.save(user)
            
            logger.info(f"Email verified successfully for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False
    
    async def reset_password(self, email: str) -> bool:
        """
        Initiate password reset process.
        
        Args:
            email: User email address
            
        Returns:
            True if reset initiated successfully
        """
        try:
            # Find user by email
            user = await self._user_repository.get_by_email(email)
            if not user:
                # Don't reveal whether email exists or not
                logger.warning(f"Password reset attempt for non-existent email: {email}")
                return True  # Return true to avoid email enumeration
            
            # In a real implementation, you would:
            # 1. Generate a password reset token
            # 2. Store it with expiration time
            # 3. Send password reset email
            
            logger.info(f"Password reset initiated for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error initiating password reset: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID (helper method for other services).
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            User entity if found, None otherwise
        """
        try:
            return await self._user_repository.get_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None