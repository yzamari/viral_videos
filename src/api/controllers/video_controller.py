"""
Video Generation Controller handling video creation and management endpoints.

This controller manages video generation workflows while maintaining
proper separation of concerns and delegating business logic to services.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator
from datetime import datetime

from src.api.controllers.base_controller import BaseController
from src.services.interfaces import IAuthenticationService, IVideoGenerationService
from src.domain.entities.video_session import VideoGenerationConfig, VideoSessionStatus
from src.utils.exceptions import VideoGenerationError

logger = logging.getLogger(__name__)


# Request/Response models
class VideoGenerationRequest(BaseModel):
    """Video generation request model"""
    mission: str = Field(..., min_length=10, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    platform: str = Field("youtube", regex="^(youtube|tiktok|instagram|facebook|twitter)$")
    duration: int = Field(20, ge=5, le=300)
    image_only: bool = False
    fallback_only: bool = False
    force_generation: bool = False
    skip_auth_test: bool = False
    discussion_mode: str = Field("enhanced", regex="^(simple|enhanced|professional)$")
    show_discussion_logs: bool = True
    style: Optional[str] = Field(None, max_length=100)
    visual_style: Optional[str] = Field(None, max_length=100)
    language: str = Field("english", max_length=50)
    voice_preference: Optional[str] = Field(None, max_length=100)
    use_premium_models: bool = False
    enable_subtitles: bool = True
    background_music: bool = True


class SessionResponse(BaseModel):
    """Video session response model"""
    id: str
    status: str
    current_phase: str
    progress_percentage: float
    created_at: str
    updated_at: str
    estimated_completion_time: Optional[str]
    config: Dict[str, Any]


class ProgressResponse(BaseModel):
    """Generation progress response model"""
    session_id: str
    status: str
    current_phase: str
    progress_percentage: float
    estimated_time_remaining: Optional[int]
    created_at: str
    updated_at: str


class VideoController(BaseController):
    """
    Video generation controller implementing video creation endpoints.
    
    This controller maintains thin controller logic by delegating all
    video generation business operations to the video generation service.
    """
    
    def __init__(self, 
                 authentication_service: IAuthenticationService,
                 video_generation_service: IVideoGenerationService):
        """
        Initialize video controller.
        
        Args:
            authentication_service: Authentication service
            video_generation_service: Video generation service
        """
        super().__init__(authentication_service)
        self._video_service = video_generation_service
    
    async def create_video_session(self, 
                                 token: str, 
                                 request: VideoGenerationRequest) -> Dict[str, Any]:
        """
        Create a new video generation session.
        
        Args:
            token: JWT access token
            request: Video generation request
            
        Returns:
            Created session information
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("POST /video/sessions", user_id=user.id, mission=request.mission[:50])
            
            # Create video generation configuration
            config = VideoGenerationConfig(
                mission=request.mission,
                category=request.category,
                platform=request.platform,
                duration=request.duration,
                image_only=request.image_only,
                fallback_only=request.fallback_only,
                force_generation=request.force_generation,
                skip_auth_test=request.skip_auth_test,
                discussion_mode=request.discussion_mode,
                show_discussion_logs=request.show_discussion_logs,
                style=request.style,
                visual_style=request.visual_style,
                language=request.language,
                voice_preference=request.voice_preference,
                use_premium_models=request.use_premium_models,
                enable_subtitles=request.enable_subtitles,
                background_music=request.background_music
            )
            
            # Create session through service
            session = await self._video_service.create_video_session(user.id, config)
            
            # Prepare response
            session_data = {
                "id": session.id,
                "status": session.status.value,
                "current_phase": session.current_phase,
                "progress_percentage": session.progress_percentage,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "estimated_completion_time": session.estimated_completion_time.isoformat() if session.estimated_completion_time else None,
                "config": session.config.to_dict()
            }
            
            self.log_response("POST /video/sessions", True)
            return self.create_success_response(
                data=session_data,
                message="Video session created successfully"
            )
            
        except VideoGenerationError as e:
            logger.warning(f"Session creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected session creation error: {e}")
            raise self.handle_service_exception(e)
    
    async def start_video_generation(self, token: str, session_id: str) -> Dict[str, Any]:
        """
        Start video generation for a session.
        
        Args:
            token: JWT access token
            session_id: Session ID to start generation for
            
        Returns:
            Generation start confirmation
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("POST /video/sessions/{session_id}/start", user_id=user.id, session_id=session_id)
            
            # Start generation through service
            success = await self._video_service.start_video_generation(session_id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to start video generation"
                )
            
            self.log_response("POST /video/sessions/{session_id}/start", True)
            return self.create_success_response(
                message="Video generation started successfully"
            )
            
        except Exception as e:
            logger.error(f"Generation start error: {e}")
            raise self.handle_service_exception(e)
    
    async def get_generation_progress(self, token: str, session_id: str) -> Dict[str, Any]:
        """
        Get generation progress for a session.
        
        Args:
            token: JWT access token
            session_id: Session ID to get progress for
            
        Returns:
            Current generation progress
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("GET /video/sessions/{session_id}/progress", user_id=user.id, session_id=session_id)
            
            # Get progress through service
            progress = await self._video_service.get_generation_progress(session_id)
            
            if "error" in progress:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=progress["error"]
                )
            
            self.log_response("GET /video/sessions/{session_id}/progress", True)
            return self.create_success_response(
                data=progress,
                message="Progress retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Progress retrieval error: {e}")
            raise self.handle_service_exception(e)
    
    async def cancel_generation(self, token: str, session_id: str) -> Dict[str, Any]:
        """
        Cancel video generation for a session.
        
        Args:
            token: JWT access token
            session_id: Session ID to cancel
            
        Returns:
            Cancellation confirmation
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("POST /video/sessions/{session_id}/cancel", user_id=user.id, session_id=session_id)
            
            # Cancel generation through service
            success = await self._video_service.cancel_generation(session_id, user.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to cancel generation"
                )
            
            self.log_response("POST /video/sessions/{session_id}/cancel", True)
            return self.create_success_response(
                message="Video generation cancelled successfully"
            )
            
        except Exception as e:
            logger.error(f"Generation cancellation error: {e}")
            raise self.handle_service_exception(e)
    
    async def get_user_sessions(self, 
                              token: str,
                              page: int = 1,
                              limit: int = 20,
                              status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user's video sessions with pagination.
        
        Args:
            token: JWT access token
            page: Page number (1-based)
            limit: Items per page
            status: Optional status filter
            
        Returns:
            Paginated list of user sessions
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("GET /video/sessions", user_id=user.id, page=page, limit=limit)
            
            # Validate pagination parameters
            offset, validated_limit = self.validate_pagination_params(page, limit)
            
            # Get user sessions through service
            sessions = await self._video_service.get_user_sessions(user.id, validated_limit)
            
            # Filter by status if provided
            if status:
                sessions = [s for s in sessions if s.status.value == status]
            
            # Apply pagination
            paginated_sessions = sessions[offset:offset + validated_limit]
            
            # Convert to response format
            session_data = []
            for session in paginated_sessions:
                session_data.append({
                    "id": session.id,
                    "status": session.status.value,
                    "current_phase": session.current_phase,
                    "progress_percentage": session.progress_percentage,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "config": {
                        "mission": session.config.mission[:100] + "..." if len(session.config.mission) > 100 else session.config.mission,
                        "platform": session.config.platform,
                        "duration": session.config.duration,
                        "language": session.config.language
                    }
                })
            
            self.log_response("GET /video/sessions", True)
            return self.create_paginated_response(
                items=session_data,
                total_count=len(sessions),
                page=page,
                limit=validated_limit
            )
            
        except Exception as e:
            logger.error(f"Sessions retrieval error: {e}")
            raise self.handle_service_exception(e)
    
    async def get_session_details(self, token: str, session_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific session.
        
        Args:
            token: JWT access token
            session_id: Session ID to get details for
            
        Returns:
            Detailed session information
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("GET /video/sessions/{session_id}", user_id=user.id, session_id=session_id)
            
            # Get session through service (this will be a repository call in practice)
            sessions = await self._video_service.get_user_sessions(user.id)
            session = next((s for s in sessions if s.id == session_id), None)
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            
            # Verify user ownership
            await self.verify_user_ownership(user, session.user_id, "session")
            
            # Prepare detailed response
            session_data = {
                "id": session.id,
                "status": session.status.value,
                "current_phase": session.current_phase,
                "progress_percentage": session.progress_percentage,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "estimated_completion_time": session.estimated_completion_time.isoformat() if session.estimated_completion_time else None,
                "config": session.config.to_dict(),
                "resource_usage": {
                    "compute_time_seconds": session.compute_time_seconds,
                    "storage_used_mb": session.storage_used_mb,
                    "ai_tokens_used": session.ai_tokens_used
                },
                "quality_metrics": {
                    "quality_score": session.generation_quality_score,
                    "user_rating": session.user_satisfaction_rating
                },
                "output_files": {
                    "video_path": session.output_video_path,
                    "thumbnail_path": session.thumbnail_path,
                    "metadata_path": session.metadata_path
                }
            }
            
            self.log_response("GET /video/sessions/{session_id}", True)
            return self.create_success_response(
                data=session_data,
                message="Session details retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Session details error: {e}")
            raise self.handle_service_exception(e)
    
    async def validate_generation_config(self, 
                                       token: str,
                                       request: VideoGenerationRequest) -> Dict[str, Any]:
        """
        Validate video generation configuration without creating a session.
        
        Args:
            token: JWT access token
            request: Video generation request to validate
            
        Returns:
            Validation results
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("POST /video/validate", user_id=user.id)
            
            # Create configuration for validation
            config = VideoGenerationConfig(
                mission=request.mission,
                category=request.category,
                platform=request.platform,
                duration=request.duration,
                image_only=request.image_only,
                fallback_only=request.fallback_only,
                force_generation=request.force_generation,
                skip_auth_test=request.skip_auth_test,
                discussion_mode=request.discussion_mode,
                show_discussion_logs=request.show_discussion_logs,
                style=request.style,
                visual_style=request.visual_style,
                language=request.language,
                voice_preference=request.voice_preference,
                use_premium_models=request.use_premium_models,
                enable_subtitles=request.enable_subtitles,
                background_music=request.background_music
            )
            
            # Validate through service
            validation_result = await self._video_service.validate_generation_config(config, user)
            cost_estimate = await self._video_service.estimate_generation_cost(config)
            
            response_data = {
                "validation": validation_result,
                "cost_estimate": cost_estimate,
                "user_limits": {
                    "can_generate": user.can_generate_videos(),
                    "monthly_usage": user.monthly_videos_used,
                    "monthly_limit": user.role.get_max_monthly_videos(),
                    "active_sessions": len(user.active_sessions),
                    "session_limit": user.role.get_max_sessions()
                }
            }
            
            self.log_response("POST /video/validate", True)
            return self.create_success_response(
                data=response_data,
                message="Configuration validated successfully"
            )
            
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            raise self.handle_service_exception(e)
    
    async def get_generation_queue_status(self, token: str) -> Dict[str, Any]:
        """
        Get current video generation queue status.
        
        Args:
            token: JWT access token
            
        Returns:
            Queue status information
        """
        try:
            user = await self.get_current_user_from_token(token)
            self.log_request("GET /video/queue", user_id=user.id)
            
            # Get queue status through service
            queue_status = await self._video_service.get_generation_queue_status()
            
            self.log_response("GET /video/queue", True)
            return self.create_success_response(
                data=queue_status,
                message="Queue status retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Queue status error: {e}")
            raise self.handle_service_exception(e)