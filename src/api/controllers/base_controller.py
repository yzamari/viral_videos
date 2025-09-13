"""
Base Controller providing common functionality for all API controllers.

This base class implements common patterns and error handling while
following the Single Responsibility Principle.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from datetime import datetime

from src.domain.entities.user import User
from src.services.interfaces import IAuthenticationService
from src.utils.exceptions import AuthenticationError, RepositoryError, VideoGenerationError, CampaignError

logger = logging.getLogger(__name__)


class BaseController:
    """
    Base controller class providing common functionality.
    
    This class encapsulates common error handling, response formatting,
    and authentication patterns used across all controllers.
    """
    
    def __init__(self, authentication_service: IAuthenticationService):
        """
        Initialize base controller.
        
        Args:
            authentication_service: Authentication service for user verification
        """
        self._auth_service = authentication_service
    
    async def get_current_user_from_token(self, token: str) -> User:
        """
        Get current user from JWT token with proper error handling.
        
        Args:
            token: JWT access token
            
        Returns:
            User entity
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            user = await self._auth_service.verify_access_token(token)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            return user
        except AuthenticationError as e:
            logger.warning(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"Unexpected error in authentication: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    def handle_service_exception(self, e: Exception) -> HTTPException:
        """
        Convert service exceptions to appropriate HTTP exceptions.
        
        Args:
            e: Service exception
            
        Returns:
            HTTPException with appropriate status code and message
        """
        if isinstance(e, AuthenticationError):
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        elif isinstance(e, VideoGenerationError):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        elif isinstance(e, CampaignError):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        elif isinstance(e, RepositoryError):
            logger.error(f"Repository error: {e}")
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data access error"
            )
        elif isinstance(e, ValueError):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            logger.error(f"Unexpected service error: {e}")
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def create_success_response(self, 
                              data: Any = None, 
                              message: str = "Success") -> Dict[str, Any]:
        """
        Create standardized success response.
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Standardized response dictionary
        """
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if data is not None:
            response["data"] = data
            
        return response
    
    def create_error_response(self, 
                            message: str, 
                            error_code: Optional[str] = None,
                            details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create standardized error response.
        
        Args:
            message: Error message
            error_code: Optional error code
            details: Optional error details
            
        Returns:
            Standardized error response dictionary
        """
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if details:
            response["details"] = details
            
        return response
    
    def validate_pagination_params(self, 
                                 page: int = 1, 
                                 limit: int = 20) -> tuple[int, int]:
        """
        Validate and normalize pagination parameters.
        
        Args:
            page: Page number (1-based)
            limit: Items per page
            
        Returns:
            Tuple of (offset, limit) for repository queries
            
        Raises:
            ValueError: If parameters are invalid
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")
            
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        offset = (page - 1) * limit
        return offset, limit
    
    def create_paginated_response(self, 
                                items: list,
                                total_count: int,
                                page: int,
                                limit: int) -> Dict[str, Any]:
        """
        Create paginated response with metadata.
        
        Args:
            items: List of items for current page
            total_count: Total number of items
            page: Current page number
            limit: Items per page
            
        Returns:
            Paginated response with metadata
        """
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        return self.create_success_response(
            data={
                "items": items,
                "pagination": {
                    "current_page": page,
                    "items_per_page": limit,
                    "total_items": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                }
            }
        )
    
    def log_request(self, endpoint: str, user_id: Optional[str] = None, **kwargs):
        """
        Log API request for monitoring and debugging.
        
        Args:
            endpoint: API endpoint being called
            user_id: Optional user ID making the request
            **kwargs: Additional context to log
        """
        context = {
            "endpoint": endpoint,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        logger.info(f"API Request: {context}")
    
    def log_response(self, endpoint: str, success: bool, duration_ms: Optional[float] = None):
        """
        Log API response for monitoring.
        
        Args:
            endpoint: API endpoint
            success: Whether the request was successful
            duration_ms: Optional request duration in milliseconds
        """
        context = {
            "endpoint": endpoint,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if duration_ms is not None:
            context["duration_ms"] = duration_ms
            
        logger.info(f"API Response: {context}")
    
    async def verify_user_ownership(self, 
                                  user: User, 
                                  resource_user_id: str,
                                  resource_type: str = "resource") -> None:
        """
        Verify that user owns the requested resource.
        
        Args:
            user: Current user
            resource_user_id: User ID that owns the resource
            resource_type: Type of resource being accessed
            
        Raises:
            HTTPException: If user doesn't own the resource
        """
        if user.id != resource_user_id:
            logger.warning(
                f"Unauthorized access attempt: user {user.id} "
                f"trying to access {resource_type} owned by {resource_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: You don't own this {resource_type}"
            )