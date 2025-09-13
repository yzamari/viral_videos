"""
Video Generation Service implementation orchestrating video creation workflow.

This service coordinates video generation processes while maintaining proper
separation of concerns and business logic encapsulation.
"""

import uuid
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from src.domain.entities.user import User
from src.domain.entities.video_session import VideoSession, VideoGenerationConfig, VideoSessionStatus
from src.repositories.interfaces import IUserRepository, IVideoSessionRepository
from src.services.interfaces import IVideoGenerationService
from src.utils.exceptions import VideoGenerationError, RepositoryError

logger = logging.getLogger(__name__)


class VideoGenerationService(IVideoGenerationService):
    """
    Video generation service orchestrating the complete video creation workflow.
    
    This service encapsulates business logic for video generation while
    maintaining clean separation from infrastructure and presentation layers.
    """
    
    def __init__(self, 
                 user_repository: IUserRepository,
                 video_session_repository: IVideoSessionRepository,
                 max_concurrent_generations: int = 5):
        """
        Initialize video generation service.
        
        Args:
            user_repository: User repository for user data access
            video_session_repository: Video session repository for session data
            max_concurrent_generations: Maximum concurrent generation processes
        """
        self._user_repository = user_repository
        self._video_session_repository = video_session_repository
        self._max_concurrent_generations = max_concurrent_generations
        self._active_generations: Dict[str, asyncio.Task] = {}
    
    async def create_video_session(self, 
                                 user_id: str, 
                                 config: VideoGenerationConfig) -> VideoSession:
        """
        Create a new video generation session with validation.
        
        Args:
            user_id: User ID creating the session
            config: Video generation configuration
            
        Returns:
            Created video session entity
            
        Raises:
            VideoGenerationError: If session creation fails
        """
        try:
            # Load and validate user
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                raise VideoGenerationError("User not found")
            
            # Validate user can generate videos
            if not user.can_generate_videos():
                reasons = self._get_generation_restriction_reasons(user)
                raise VideoGenerationError(f"Cannot generate videos: {', '.join(reasons)}")
            
            # Validate user can create new session
            if not user.can_create_new_session():
                max_sessions = user.role.get_max_sessions()
                active_count = len(user.active_sessions)
                raise VideoGenerationError(
                    f"Maximum sessions reached ({active_count}/{max_sessions})"
                )
            
            # Validate generation configuration
            validation_result = await self.validate_generation_config(config, user)
            if not validation_result["valid"]:
                errors = validation_result.get("errors", [])
                raise VideoGenerationError(f"Invalid configuration: {', '.join(errors)}")
            
            # Create session entity
            session_id = str(uuid.uuid4())
            session = VideoSession.create_new_session(
                session_id=session_id,
                user_id=user_id,
                config=config
            )
            
            # Save session to repository
            await self._video_session_repository.save(session)
            
            # Update user's active sessions
            user.add_session(session_id)
            await self._user_repository.save(user)
            
            logger.info(f"Video session created: {session_id} for user {user_id}")
            return session
            
        except RepositoryError as e:
            logger.error(f"Repository error creating session: {e}")
            raise VideoGenerationError(f"Session creation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating session: {e}")
            raise VideoGenerationError(f"Session creation failed: {e}")
    
    def _get_generation_restriction_reasons(self, user: User) -> List[str]:
        """Get reasons why user cannot generate videos"""
        reasons = []
        
        if not user.is_active():
            reasons.append("account not active")
        
        if user.is_trial_expired():
            reasons.append("trial period expired")
        
        if user.has_exceeded_monthly_limit():
            max_videos = user.role.get_max_monthly_videos()
            reasons.append(f"monthly limit exceeded ({user.monthly_videos_used}/{max_videos})")
        
        return reasons
    
    async def start_video_generation(self, session_id: str) -> bool:
        """
        Start video generation process for a session.
        
        Args:
            session_id: Session ID to start generation for
            
        Returns:
            True if generation started successfully
        """
        try:
            # Load session
            session = await self._video_session_repository.get_by_id(session_id)
            if not session:
                raise VideoGenerationError("Session not found")
            
            # Validate session can be started
            if session.status != VideoSessionStatus.CREATED:
                raise VideoGenerationError(f"Cannot start generation from status: {session.status.value}")
            
            # Check generation queue capacity
            if len(self._active_generations) >= self._max_concurrent_generations:
                # Queue the session instead of starting immediately
                session.status = VideoSessionStatus.QUEUED
                await self._video_session_repository.save(session)
                logger.info(f"Session {session_id} queued - generation capacity full")
                return True
            
            # Start generation process
            session.start_generation()
            await self._video_session_repository.save(session)
            
            # Create background task for generation
            task = asyncio.create_task(self._run_video_generation(session_id))
            self._active_generations[session_id] = task
            
            logger.info(f"Video generation started for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting video generation: {e}")
            # Mark session as failed
            try:
                session = await self._video_session_repository.get_by_id(session_id)
                if session:
                    session.fail_with_error(str(e))
                    await self._video_session_repository.save(session)
            except:
                pass
            return False
    
    async def _run_video_generation(self, session_id: str) -> None:
        """
        Internal method to run the actual video generation process.
        
        Args:
            session_id: Session ID to generate video for
        """
        try:
            session = await self._video_session_repository.get_by_id(session_id)
            if not session:
                logger.error(f"Session not found for generation: {session_id}")
                return
            
            # Begin processing
            session.begin_processing()
            await self._video_session_repository.save(session)
            
            # Phase 1: AI Discussion & Planning (10-30%)
            await self._update_progress(session, "AI Discussion & Planning", 10.0)
            await asyncio.sleep(2)  # Simulate discussion time
            await self._update_progress(session, "AI Discussion & Planning", 30.0)
            
            # Phase 2: Script Generation (30-50%)
            await self._update_progress(session, "Script Generation", 30.0)
            await asyncio.sleep(1)  # Simulate script generation
            await self._update_progress(session, "Script Generation", 50.0)
            
            # Phase 3: Video Generation (50-80%)
            await self._update_progress(session, "Video Generation", 50.0)
            await asyncio.sleep(3)  # Simulate video generation
            await self._update_progress(session, "Video Generation", 80.0)
            
            # Phase 4: Audio Processing (80-95%)
            await self._update_progress(session, "Audio Processing", 80.0)
            await asyncio.sleep(1)  # Simulate audio processing
            await self._update_progress(session, "Audio Processing", 95.0)
            
            # Phase 5: Final Assembly (95-100%)
            await self._update_progress(session, "Final Assembly", 95.0)
            await asyncio.sleep(1)  # Simulate final assembly
            
            # Complete generation
            output_path = f"outputs/{session_id}/final_video.mp4"
            session.complete_successfully(
                output_video_path=output_path,
                thumbnail_path=f"outputs/{session_id}/thumbnail.jpg",
                metadata_path=f"outputs/{session_id}/metadata.json"
            )
            await self._video_session_repository.save(session)
            
            # Update user statistics
            await self._update_user_statistics(session)
            
            logger.info(f"Video generation completed successfully: {session_id}")
            
        except Exception as e:
            logger.error(f"Video generation failed for session {session_id}: {e}")
            try:
                session = await self._video_session_repository.get_by_id(session_id)
                if session:
                    session.fail_with_error(str(e))
                    await self._video_session_repository.save(session)
            except:
                pass
        finally:
            # Remove from active generations
            self._active_generations.pop(session_id, None)
            
            # Process queued sessions
            await self._process_queued_sessions()
    
    async def _update_progress(self, session: VideoSession, phase: str, percentage: float) -> None:
        """Update session progress"""
        session.update_progress(phase, percentage)
        await self._video_session_repository.save(session)
    
    async def _update_user_statistics(self, session: VideoSession) -> None:
        """Update user statistics after successful generation"""
        try:
            user = await self._user_repository.get_by_id(session.user_id)
            if user:
                user.increment_monthly_usage()
                user.remove_session(session.id)
                await self._user_repository.save(user)
        except Exception as e:
            logger.error(f"Error updating user statistics: {e}")
    
    async def _process_queued_sessions(self) -> None:
        """Process queued sessions when capacity becomes available"""
        try:
            if len(self._active_generations) >= self._max_concurrent_generations:
                return
            
            # Find queued sessions
            queued_sessions = await self._video_session_repository.get_by_status(
                VideoSessionStatus.QUEUED.value, 
                limit=1
            )
            
            if queued_sessions:
                session = queued_sessions[0]
                logger.info(f"Starting queued session: {session.id}")
                await self.start_video_generation(session.id)
                
        except Exception as e:
            logger.error(f"Error processing queued sessions: {e}")
    
    async def get_generation_progress(self, session_id: str) -> Dict[str, Any]:
        """
        Get current generation progress for a session.
        
        Args:
            session_id: Session ID to get progress for
            
        Returns:
            Progress information dictionary
        """
        try:
            session = await self._video_session_repository.get_by_id(session_id)
            if not session:
                return {"error": "Session not found"}
            
            return {
                "session_id": session.id,
                "status": session.status.value,
                "current_phase": session.current_phase,
                "progress_percentage": session.progress_percentage,
                "estimated_time_remaining": session.get_estimated_time_remaining(),
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting generation progress: {e}")
            return {"error": str(e)}
    
    async def cancel_generation(self, session_id: str, user_id: str) -> bool:
        """
        Cancel video generation for a session.
        
        Args:
            session_id: Session ID to cancel
            user_id: User ID requesting cancellation
            
        Returns:
            True if cancellation successful
        """
        try:
            # Load and validate session
            session = await self._video_session_repository.get_by_id(session_id)
            if not session:
                return False
            
            # Verify user owns the session
            if session.user_id != user_id:
                logger.warning(f"Unauthorized cancellation attempt: user {user_id} for session {session_id}")
                return False
            
            # Check if session can be cancelled
            if not session.can_be_cancelled():
                logger.warning(f"Cannot cancel session in status: {session.status.value}")
                return False
            
            # Cancel the session
            session.cancel_session()
            await self._video_session_repository.save(session)
            
            # Cancel background task if running
            if session_id in self._active_generations:
                task = self._active_generations.pop(session_id)
                task.cancel()
            
            # Update user's active sessions
            user = await self._user_repository.get_by_id(user_id)
            if user:
                user.remove_session(session_id)
                await self._user_repository.save(user)
            
            logger.info(f"Video generation cancelled: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling generation: {e}")
            return False
    
    async def get_user_sessions(self, 
                              user_id: str, 
                              limit: Optional[int] = None) -> List[VideoSession]:
        """
        Get video sessions for a user.
        
        Args:
            user_id: User ID to get sessions for
            limit: Optional limit on results
            
        Returns:
            List of user's video sessions
        """
        try:
            return await self._video_session_repository.get_by_user_id(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    async def validate_generation_config(self, 
                                       config: VideoGenerationConfig,
                                       user: User) -> Dict[str, Any]:
        """
        Validate video generation configuration against user limits.
        
        Args:
            config: Video generation configuration
            user: User entity
            
        Returns:
            Validation result with any errors or warnings
        """
        try:
            errors = []
            warnings = []
            
            # Validate basic configuration
            if not config.mission or len(config.mission.strip()) < 10:
                errors.append("Mission must be at least 10 characters long")
            
            if config.duration < 5 or config.duration > 300:
                errors.append("Duration must be between 5 and 300 seconds")
            
            # Validate against user role limits
            if config.use_premium_models and not user.role.can_access_premium_features():
                errors.append("Premium models require premium subscription")
            
            # Check if user is close to monthly limit
            monthly_limit = user.role.get_max_monthly_videos()
            if monthly_limit > 0:  # Not unlimited
                remaining = monthly_limit - user.monthly_videos_used
                if remaining <= 0:
                    errors.append("Monthly video generation limit exceeded")
                elif remaining <= 5:
                    warnings.append(f"Only {remaining} videos remaining this month")
            
            # Platform-specific validations
            platform_limits = {
                'tiktok': {'max_duration': 60},
                'instagram': {'max_duration': 90},
                'youtube': {'max_duration': 300}
            }
            
            platform_limit = platform_limits.get(config.platform, {})
            max_duration = platform_limit.get('max_duration')
            if max_duration and config.duration > max_duration:
                warnings.append(f"Duration adjusted to {max_duration}s for {config.platform}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Error validating generation config: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {e}"],
                "warnings": []
            }
    
    async def estimate_generation_cost(self, config: VideoGenerationConfig) -> Dict[str, Any]:
        """
        Estimate cost and resource usage for generation.
        
        Args:
            config: Video generation configuration
            
        Returns:
            Cost estimation details
        """
        try:
            # Base costs (in credits or currency units)
            base_cost = 10.0
            duration_multiplier = config.duration / 20.0  # Normalized to 20 seconds
            
            # Mode cost multipliers
            mode_costs = {
                'simple': 1.0,
                'enhanced': 1.5,
                'professional': 2.0
            }
            mode_multiplier = mode_costs.get(config.discussion_mode, 1.0)
            
            # Feature costs
            premium_multiplier = 1.5 if config.use_premium_models else 1.0
            subtitle_cost = 2.0 if config.enable_subtitles else 0.0
            
            total_cost = (base_cost * duration_multiplier * mode_multiplier * premium_multiplier) + subtitle_cost
            
            return {
                "estimated_cost": round(total_cost, 2),
                "base_cost": base_cost,
                "duration_factor": duration_multiplier,
                "mode_factor": mode_multiplier,
                "premium_factor": premium_multiplier,
                "additional_features": subtitle_cost,
                "estimated_time_seconds": config.get_estimated_generation_time(),
                "currency": "credits"
            }
            
        except Exception as e:
            logger.error(f"Error estimating generation cost: {e}")
            return {"error": str(e)}
    
    async def get_generation_queue_status(self) -> Dict[str, Any]:
        """
        Get current status of the generation queue.
        
        Returns:
            Queue status information
        """
        try:
            # Get active and queued sessions
            active_sessions = list(self._active_generations.keys())
            queued_sessions = await self._video_session_repository.get_by_status(
                VideoSessionStatus.QUEUED.value
            )
            
            return {
                "active_generations": len(active_sessions),
                "max_concurrent": self._max_concurrent_generations,
                "queued_sessions": len(queued_sessions),
                "available_slots": max(0, self._max_concurrent_generations - len(active_sessions)),
                "active_session_ids": active_sessions,
                "queued_session_ids": [s.id for s in queued_sessions]
            }
            
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {"error": str(e)}