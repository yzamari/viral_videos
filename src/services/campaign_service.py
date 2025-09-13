"""
Campaign Service implementation for managing marketing campaigns.

This service orchestrates campaign lifecycle management while coordinating
with video generation services and maintaining proper business logic separation.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List

from src.domain.entities.user import User
from src.domain.entities.campaign import Campaign, CampaignStatus, CampaignPriority
from src.domain.entities.video_session import VideoSession
from src.repositories.interfaces import IUserRepository, ICampaignRepository, IVideoSessionRepository
from src.services.interfaces import ICampaignService
from src.utils.exceptions import CampaignError, RepositoryError

logger = logging.getLogger(__name__)


class CampaignService(ICampaignService):
    """
    Campaign service implementing campaign lifecycle management.
    
    This service encapsulates campaign business logic while maintaining
    proper separation of concerns and coordinating with video generation.
    """
    
    def __init__(self, 
                 user_repository: IUserRepository,
                 campaign_repository: ICampaignRepository,
                 video_session_repository: IVideoSessionRepository):
        """
        Initialize campaign service.
        
        Args:
            user_repository: User repository for user data access
            campaign_repository: Campaign repository for campaign data
            video_session_repository: Video session repository for session data
        """
        self._user_repository = user_repository
        self._campaign_repository = campaign_repository
        self._video_session_repository = video_session_repository
    
    async def create_campaign(self, 
                            user_id: str,
                            name: str,
                            description: str,
                            target_platforms: List[str]) -> Campaign:
        """
        Create a new marketing campaign with validation.
        
        Args:
            user_id: User ID creating the campaign
            name: Campaign name
            description: Campaign description
            target_platforms: List of target platforms
            
        Returns:
            Created campaign entity
            
        Raises:
            CampaignError: If campaign creation fails
        """
        try:
            # Load and validate user
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                raise CampaignError("User not found")
            
            if not user.is_active():
                raise CampaignError("User account is not active")
            
            # Validate input parameters
            self._validate_campaign_input(name, description, target_platforms)
            
            # Check user's campaign limits based on role
            await self._validate_campaign_limits(user)
            
            # Create campaign entity
            campaign_id = str(uuid.uuid4())
            campaign = Campaign.create_new_campaign(
                campaign_id=campaign_id,
                name=name,
                description=description,
                user_id=user_id,
                target_platforms=target_platforms,
                priority=CampaignPriority.MEDIUM
            )
            
            # Save campaign to repository
            await self._campaign_repository.save(campaign)
            
            logger.info(f"Campaign created: {campaign_id} for user {user_id}")
            return campaign
            
        except RepositoryError as e:
            logger.error(f"Repository error creating campaign: {e}")
            raise CampaignError(f"Campaign creation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating campaign: {e}")
            raise CampaignError(f"Campaign creation failed: {e}")
    
    def _validate_campaign_input(self, name: str, description: str, target_platforms: List[str]) -> None:
        """Validate campaign input parameters"""
        if not name or len(name.strip()) < 3:
            raise CampaignError("Campaign name must be at least 3 characters long")
        
        if not description or len(description.strip()) < 10:
            raise CampaignError("Campaign description must be at least 10 characters long")
        
        if not target_platforms or len(target_platforms) == 0:
            raise CampaignError("At least one target platform is required")
        
        valid_platforms = ['youtube', 'tiktok', 'instagram', 'facebook', 'twitter']
        invalid_platforms = [p for p in target_platforms if p not in valid_platforms]
        if invalid_platforms:
            raise CampaignError(f"Invalid platforms: {', '.join(invalid_platforms)}")
    
    async def _validate_campaign_limits(self, user: User) -> None:
        """Validate user hasn't exceeded campaign limits"""
        user_campaigns = await self._campaign_repository.get_by_user_id(user.id)
        active_campaigns = [c for c in user_campaigns if c.is_active()]
        
        # Define limits based on user role
        role_limits = {
            'trial': {'max_campaigns': 1, 'max_active': 1},
            'basic': {'max_campaigns': 5, 'max_active': 2},
            'premium': {'max_campaigns': 20, 'max_active': 5},
            'admin': {'max_campaigns': -1, 'max_active': -1}  # Unlimited
        }
        
        limits = role_limits.get(user.role.value, role_limits['trial'])
        
        # Check total campaign limit
        if limits['max_campaigns'] > 0 and len(user_campaigns) >= limits['max_campaigns']:
            raise CampaignError(f"Maximum campaign limit reached ({limits['max_campaigns']})")
        
        # Check active campaign limit
        if limits['max_active'] > 0 and len(active_campaigns) >= limits['max_active']:
            raise CampaignError(f"Maximum active campaign limit reached ({limits['max_active']})")
    
    async def add_video_to_campaign(self, 
                                  campaign_id: str, 
                                  video_session_id: str,
                                  user_id: str) -> bool:
        """
        Add a video session to a campaign.
        
        Args:
            campaign_id: Campaign ID
            video_session_id: Video session ID to add
            user_id: User ID making the request
            
        Returns:
            True if video added successfully
        """
        try:
            # Load and validate campaign
            campaign = await self._campaign_repository.get_by_id(campaign_id)
            if not campaign:
                raise CampaignError("Campaign not found")
            
            # Verify user owns the campaign
            if campaign.user_id != user_id:
                raise CampaignError("Unauthorized: User does not own this campaign")
            
            # Check if campaign can accept new videos
            if not campaign.can_add_videos():
                raise CampaignError(f"Cannot add videos to campaign in {campaign.status.value} status")
            
            # Load and validate video session
            video_session = await self._video_session_repository.get_by_id(video_session_id)
            if not video_session:
                raise CampaignError("Video session not found")
            
            # Verify user owns the video session
            if video_session.user_id != user_id:
                raise CampaignError("Unauthorized: User does not own this video session")
            
            # Add video to campaign
            campaign.add_video_session(video_session_id)
            await self._campaign_repository.save(campaign)
            
            logger.info(f"Video {video_session_id} added to campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding video to campaign: {e}")
            raise CampaignError(str(e)) if isinstance(e, CampaignError) else CampaignError("Failed to add video to campaign")
    
    async def activate_campaign(self, campaign_id: str, user_id: str) -> bool:
        """
        Activate a campaign for execution.
        
        Args:
            campaign_id: Campaign ID to activate
            user_id: User ID making the request
            
        Returns:
            True if campaign activated successfully
        """
        try:
            # Load and validate campaign
            campaign = await self._campaign_repository.get_by_id(campaign_id)
            if not campaign:
                raise CampaignError("Campaign not found")
            
            # Verify user owns the campaign
            if campaign.user_id != user_id:
                raise CampaignError("Unauthorized: User does not own this campaign")
            
            # Validate campaign can be activated
            if campaign.total_planned_videos == 0:
                raise CampaignError("Cannot activate campaign with no videos")
            
            # Activate the campaign
            campaign.activate_campaign()
            await self._campaign_repository.save(campaign)
            
            logger.info(f"Campaign activated: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating campaign: {e}")
            raise CampaignError(str(e)) if isinstance(e, CampaignError) else CampaignError("Failed to activate campaign")
    
    async def get_campaign_performance(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get campaign performance metrics.
        
        Args:
            campaign_id: Campaign ID
            user_id: User ID making the request
            
        Returns:
            Campaign performance data
        """
        try:
            # Load and validate campaign
            campaign = await self._campaign_repository.get_by_id(campaign_id)
            if not campaign:
                raise CampaignError("Campaign not found")
            
            # Verify user owns the campaign
            if campaign.user_id != user_id:
                raise CampaignError("Unauthorized: User does not own this campaign")
            
            # Get basic campaign summary
            performance = campaign.get_campaign_summary()
            
            # Enhance with video session details
            video_sessions = []
            for session_id in campaign.video_session_ids:
                session = await self._video_session_repository.get_by_id(session_id)
                if session:
                    video_sessions.append({
                        "id": session.id,
                        "status": session.status.value,
                        "progress": session.progress_percentage,
                        "created_at": session.created_at.isoformat(),
                        "config": session.config.to_dict()
                    })
            
            performance["video_sessions"] = video_sessions
            performance["session_details"] = {
                "total_compute_time": sum(s.compute_time_seconds for s in [
                    await self._video_session_repository.get_by_id(sid) 
                    for sid in campaign.video_session_ids
                ] if s),
                "total_storage_used": sum(s.storage_used_mb for s in [
                    await self._video_session_repository.get_by_id(sid) 
                    for sid in campaign.video_session_ids
                ] if s),
                "average_quality_score": campaign.performance_metrics.get("average_quality_score", 0.0)
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting campaign performance: {e}")
            raise CampaignError(str(e)) if isinstance(e, CampaignError) else CampaignError("Failed to get campaign performance")
    
    async def get_user_campaigns(self, 
                               user_id: str,
                               status: Optional[str] = None) -> List[Campaign]:
        """
        Get campaigns for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
            
        Returns:
            List of user's campaigns
        """
        try:
            if status:
                # Get campaigns by status
                all_campaigns = await self._campaign_repository.get_by_status(status)
                return [c for c in all_campaigns if c.user_id == user_id]
            else:
                # Get all user campaigns
                return await self._campaign_repository.get_by_user_id(user_id)
                
        except Exception as e:
            logger.error(f"Error getting user campaigns: {e}")
            return []
    
    async def update_campaign_progress(self, 
                                     campaign_id: str,
                                     session_id: str,
                                     progress_data: Dict[str, Any]) -> bool:
        """
        Update campaign progress when video sessions complete.
        
        Args:
            campaign_id: Campaign ID
            session_id: Video session ID
            progress_data: Progress update data
            
        Returns:
            True if update successful
        """
        try:
            # Load campaign
            campaign = await self._campaign_repository.get_by_id(campaign_id)
            if not campaign:
                logger.warning(f"Campaign not found for progress update: {campaign_id}")
                return False
            
            # Verify session belongs to campaign
            if session_id not in campaign.video_session_ids:
                logger.warning(f"Session {session_id} not in campaign {campaign_id}")
                return False
            
            # Load session to get latest status
            session = await self._video_session_repository.get_by_id(session_id)
            if not session:
                logger.warning(f"Session not found for progress update: {session_id}")
                return False
            
            # Update campaign based on session status
            if session.is_completed():
                quality_score = progress_data.get("quality_score")
                campaign.mark_video_completed(session_id, quality_score)
                
                # Update cost tracking
                cost = progress_data.get("cost", 0.0)
                if cost > 0:
                    campaign.add_cost(cost, f"Video generation: {session_id}")
                    
            elif session.is_failed():
                campaign.mark_video_failed(session_id)
            
            # Update performance metrics
            if "performance_metrics" in progress_data:
                campaign.update_performance_metrics(progress_data["performance_metrics"])
            
            # Save updated campaign
            await self._campaign_repository.save(campaign)
            
            logger.info(f"Campaign progress updated: {campaign_id} for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating campaign progress: {e}")
            return False
    
    async def pause_campaign(self, campaign_id: str, user_id: str) -> bool:
        """
        Pause an active campaign.
        
        Args:
            campaign_id: Campaign ID to pause
            user_id: User ID making the request
            
        Returns:
            True if campaign paused successfully
        """
        try:
            campaign = await self._campaign_repository.get_by_id(campaign_id)
            if not campaign:
                raise CampaignError("Campaign not found")
            
            if campaign.user_id != user_id:
                raise CampaignError("Unauthorized: User does not own this campaign")
            
            campaign.pause_campaign()
            await self._campaign_repository.save(campaign)
            
            logger.info(f"Campaign paused: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {e}")
            return False
    
    async def resume_campaign(self, campaign_id: str, user_id: str) -> bool:
        """
        Resume a paused campaign.
        
        Args:
            campaign_id: Campaign ID to resume
            user_id: User ID making the request
            
        Returns:
            True if campaign resumed successfully
        """
        try:
            campaign = await self._campaign_repository.get_by_id(campaign_id)
            if not campaign:
                raise CampaignError("Campaign not found")
            
            if campaign.user_id != user_id:
                raise CampaignError("Unauthorized: User does not own this campaign")
            
            campaign.resume_campaign()
            await self._campaign_repository.save(campaign)
            
            logger.info(f"Campaign resumed: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {e}")
            return False
    
    async def delete_campaign(self, campaign_id: str, user_id: str) -> bool:
        """
        Delete a campaign (only if in draft status).
        
        Args:
            campaign_id: Campaign ID to delete
            user_id: User ID making the request
            
        Returns:
            True if campaign deleted successfully
        """
        try:
            campaign = await self._campaign_repository.get_by_id(campaign_id)
            if not campaign:
                return False
            
            if campaign.user_id != user_id:
                raise CampaignError("Unauthorized: User does not own this campaign")
            
            if campaign.status != CampaignStatus.DRAFT:
                raise CampaignError("Can only delete campaigns in draft status")
            
            success = await self._campaign_repository.delete(campaign_id)
            if success:
                logger.info(f"Campaign deleted: {campaign_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting campaign: {e}")
            return False
    
    async def get_campaign_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get campaign analytics for a user.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Analytics data
        """
        try:
            user_campaigns = await self._campaign_repository.get_by_user_id(user_id)
            
            # Calculate analytics
            total_campaigns = len(user_campaigns)
            active_campaigns = len([c for c in user_campaigns if c.is_active()])
            completed_campaigns = len([c for c in user_campaigns if c.is_completed()])
            
            total_videos = sum(c.total_planned_videos for c in user_campaigns)
            completed_videos = sum(c.completed_videos for c in user_campaigns)
            
            total_cost = sum(c.actual_cost for c in user_campaigns)
            average_campaign_cost = total_cost / total_campaigns if total_campaigns > 0 else 0
            
            return {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "completed_campaigns": completed_campaigns,
                "total_videos": total_videos,
                "completed_videos": completed_videos,
                "success_rate": (completed_videos / total_videos * 100) if total_videos > 0 else 0,
                "total_cost": total_cost,
                "average_campaign_cost": average_campaign_cost,
                "cost_per_video": (total_cost / completed_videos) if completed_videos > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign analytics: {e}")
            return {"error": str(e)}