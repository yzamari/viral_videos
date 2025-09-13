"""
Campaign Entity - Domain entity for managing video campaigns.

This entity encapsulates campaign-level business logic and orchestrates
multiple video sessions for complex marketing campaigns.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum


class CampaignStatus(Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class CampaignPriority(Enum):
    """Campaign priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Campaign:
    """
    Campaign domain entity for managing video marketing campaigns.
    
    Follows SOLID principles by encapsulating campaign-specific business logic
    and maintaining clear separation from individual video sessions.
    """
    
    # Core identity
    id: str
    name: str
    description: str
    user_id: str
    
    # Campaign lifecycle
    status: CampaignStatus = CampaignStatus.DRAFT
    priority: CampaignPriority = CampaignPriority.MEDIUM
    
    # Scheduling
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Content organization
    video_session_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    target_platforms: List[str] = field(default_factory=list)
    
    # Campaign metrics
    total_planned_videos: int = 0
    completed_videos: int = 0
    failed_videos: int = 0
    
    # Budget and resource tracking
    estimated_budget: Optional[float] = None
    actual_cost: float = 0.0
    estimated_duration_days: Optional[int] = None
    
    # Campaign settings
    auto_publish: bool = False
    quality_threshold: float = 0.7  # Minimum quality score for auto-approval
    
    # Metadata
    campaign_config: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""
        self._validate_core_fields()
        self._initialize_defaults()
    
    def _validate_core_fields(self) -> None:
        """Validate core campaign fields"""
        if not self.id or not self.id.strip():
            raise ValueError("Campaign ID cannot be empty")
            
        if not self.name or not self.name.strip():
            raise ValueError("Campaign name cannot be empty")
            
        if len(self.name) < 3 or len(self.name) > 200:
            raise ValueError("Campaign name must be between 3 and 200 characters")
            
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
            
        if self.description and len(self.description) > 2000:
            raise ValueError("Campaign description cannot exceed 2000 characters")
    
    def _initialize_defaults(self) -> None:
        """Initialize default values and configurations"""
        if not self.performance_metrics:
            self.performance_metrics = {
                "total_views": 0,
                "total_engagements": 0,
                "average_completion_rate": 0.0,
                "roi": 0.0,
                "last_updated": datetime.now().isoformat()
            }
    
    @classmethod
    def create_new_campaign(cls,
                          campaign_id: str,
                          name: str,
                          description: str,
                          user_id: str,
                          target_platforms: Optional[List[str]] = None,
                          priority: CampaignPriority = CampaignPriority.MEDIUM) -> "Campaign":
        """
        Factory method to create a new campaign with proper validation.
        
        Encapsulates campaign creation logic and ensures proper initialization.
        """
        if not target_platforms:
            target_platforms = ["youtube"]  # Default platform
            
        return cls(
            id=campaign_id,
            name=name,
            description=description,
            user_id=user_id,
            target_platforms=target_platforms,
            priority=priority
        )
    
    def activate_campaign(self, start_date: Optional[date] = None) -> None:
        """Activate campaign for execution"""
        if self.status != CampaignStatus.DRAFT:
            raise ValueError(f"Cannot activate campaign from status: {self.status.value}")
            
        if self.total_planned_videos == 0:
            raise ValueError("Cannot activate campaign with no planned videos")
            
        self.status = CampaignStatus.ACTIVE
        self.start_date = start_date or date.today()
        self.updated_at = datetime.now()
    
    def pause_campaign(self) -> None:
        """Pause active campaign"""
        if self.status != CampaignStatus.ACTIVE:
            raise ValueError(f"Cannot pause campaign from status: {self.status.value}")
            
        self.status = CampaignStatus.PAUSED
        self.updated_at = datetime.now()
    
    def resume_campaign(self) -> None:
        """Resume paused campaign"""
        if self.status != CampaignStatus.PAUSED:
            raise ValueError("Can only resume paused campaigns")
            
        self.status = CampaignStatus.ACTIVE
        self.updated_at = datetime.now()
    
    def complete_campaign(self) -> None:
        """Mark campaign as completed"""
        if self.status not in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]:
            raise ValueError(f"Cannot complete campaign from status: {self.status.value}")
            
        self.status = CampaignStatus.COMPLETED
        self.end_date = date.today()
        self.updated_at = datetime.now()
    
    def cancel_campaign(self, reason: Optional[str] = None) -> None:
        """Cancel campaign execution"""
        if self.status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel campaign from status: {self.status.value}")
            
        self.status = CampaignStatus.CANCELLED
        if reason:
            self.campaign_config["cancellation_reason"] = reason
        self.updated_at = datetime.now()
    
    def archive_campaign(self) -> None:
        """Archive completed or cancelled campaign"""
        if self.status not in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            raise ValueError("Can only archive completed or cancelled campaigns")
            
        self.status = CampaignStatus.ARCHIVED
        self.updated_at = datetime.now()
    
    def add_video_session(self, session_id: str) -> None:
        """Add a video session to the campaign"""
        if not session_id or not session_id.strip():
            raise ValueError("Session ID cannot be empty")
            
        if session_id not in self.video_session_ids:
            self.video_session_ids.append(session_id)
            self.total_planned_videos += 1
            self.updated_at = datetime.now()
    
    def remove_video_session(self, session_id: str) -> None:
        """Remove a video session from the campaign"""
        if session_id in self.video_session_ids:
            self.video_session_ids.remove(session_id)
            self.total_planned_videos -= 1
            self.updated_at = datetime.now()
    
    def mark_video_completed(self, session_id: str, quality_score: Optional[float] = None) -> None:
        """Mark a video session as completed"""
        if session_id not in self.video_session_ids:
            raise ValueError(f"Session {session_id} not found in campaign")
            
        self.completed_videos += 1
        
        # Check if campaign should auto-complete
        if self.completed_videos >= self.total_planned_videos and self.is_active():
            self.complete_campaign()
            
        # Record quality metrics
        if quality_score is not None:
            self._update_quality_metrics(quality_score)
            
        self.updated_at = datetime.now()
    
    def mark_video_failed(self, session_id: str) -> None:
        """Mark a video session as failed"""
        if session_id not in self.video_session_ids:
            raise ValueError(f"Session {session_id} not found in campaign")
            
        self.failed_videos += 1
        self.updated_at = datetime.now()
    
    def _update_quality_metrics(self, quality_score: float) -> None:
        """Update campaign quality metrics"""
        current_scores = self.campaign_config.get("quality_scores", [])
        current_scores.append(quality_score)
        self.campaign_config["quality_scores"] = current_scores
        
        # Calculate average quality
        avg_quality = sum(current_scores) / len(current_scores)
        self.performance_metrics["average_quality_score"] = avg_quality
    
    def add_tags(self, tags: List[str]) -> None:
        """Add tags to campaign"""
        for tag in tags:
            if tag and tag.strip() and tag not in self.tags:
                self.tags.append(tag.strip().lower())
        self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from campaign"""
        tag_lower = tag.strip().lower()
        if tag_lower in self.tags:
            self.tags.remove(tag_lower)
            self.updated_at = datetime.now()
    
    def set_budget(self, estimated_budget: float) -> None:
        """Set campaign budget"""
        if estimated_budget < 0:
            raise ValueError("Budget cannot be negative")
            
        self.estimated_budget = estimated_budget
        self.updated_at = datetime.now()
    
    def add_cost(self, cost: float, description: Optional[str] = None) -> None:
        """Add cost to campaign tracking"""
        if cost < 0:
            raise ValueError("Cost cannot be negative")
            
        self.actual_cost += cost
        
        # Track cost breakdown
        cost_log = self.campaign_config.get("cost_log", [])
        cost_log.append({
            "amount": cost,
            "description": description or "Campaign cost",
            "timestamp": datetime.now().isoformat()
        })
        self.campaign_config["cost_log"] = cost_log
        
        self.updated_at = datetime.now()
    
    def update_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update campaign performance metrics"""
        self.performance_metrics.update(metrics)
        self.performance_metrics["last_updated"] = datetime.now().isoformat()
        self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """Check if campaign is active"""
        return self.status == CampaignStatus.ACTIVE
    
    def is_completed(self) -> bool:
        """Check if campaign is completed"""
        return self.status == CampaignStatus.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if campaign is cancelled"""
        return self.status == CampaignStatus.CANCELLED
    
    def can_add_videos(self) -> bool:
        """Check if videos can be added to campaign"""
        return self.status in [CampaignStatus.DRAFT, CampaignStatus.ACTIVE, CampaignStatus.PAUSED]
    
    def get_completion_rate(self) -> float:
        """Get campaign completion rate as percentage"""
        if self.total_planned_videos == 0:
            return 0.0
        return (self.completed_videos / self.total_planned_videos) * 100.0
    
    def get_failure_rate(self) -> float:
        """Get campaign failure rate as percentage"""
        if self.total_planned_videos == 0:
            return 0.0
        return (self.failed_videos / self.total_planned_videos) * 100.0
    
    def get_budget_utilization(self) -> float:
        """Get budget utilization as percentage"""
        if not self.estimated_budget or self.estimated_budget == 0:
            return 0.0
        return min(100.0, (self.actual_cost / self.estimated_budget) * 100.0)
    
    def get_duration_days(self) -> int:
        """Get campaign duration in days"""
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days
        elif self.start_date:
            return (date.today() - self.start_date).days
        return 0
    
    def get_roi_estimate(self) -> Optional[float]:
        """Get estimated ROI if metrics available"""
        if not self.actual_cost or self.actual_cost == 0:
            return None
            
        revenue = self.performance_metrics.get("estimated_revenue", 0)
        if revenue > 0:
            return ((revenue - self.actual_cost) / self.actual_cost) * 100.0
        return None
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get comprehensive campaign summary"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority.value,
            "completion_rate": self.get_completion_rate(),
            "failure_rate": self.get_failure_rate(),
            "budget_utilization": self.get_budget_utilization(),
            "duration_days": self.get_duration_days(),
            "roi_estimate": self.get_roi_estimate(),
            "total_videos": self.total_planned_videos,
            "completed_videos": self.completed_videos,
            "failed_videos": self.failed_videos,
            "target_platforms": self.target_platforms,
            "tags": self.tags
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "video_session_ids": self.video_session_ids.copy(),
            "tags": self.tags.copy(),
            "target_platforms": self.target_platforms.copy(),
            "total_planned_videos": self.total_planned_videos,
            "completed_videos": self.completed_videos,
            "failed_videos": self.failed_videos,
            "estimated_budget": self.estimated_budget,
            "actual_cost": self.actual_cost,
            "estimated_duration_days": self.estimated_duration_days,
            "auto_publish": self.auto_publish,
            "quality_threshold": self.quality_threshold,
            "campaign_config": self.campaign_config.copy(),
            "performance_metrics": self.performance_metrics.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        """Create campaign from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            user_id=data["user_id"],
            status=CampaignStatus(data["status"]),
            priority=CampaignPriority(data.get("priority", "medium")),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            video_session_ids=data.get("video_session_ids", []),
            tags=data.get("tags", []),
            target_platforms=data.get("target_platforms", ["youtube"]),
            total_planned_videos=data.get("total_planned_videos", 0),
            completed_videos=data.get("completed_videos", 0),
            failed_videos=data.get("failed_videos", 0),
            estimated_budget=data.get("estimated_budget"),
            actual_cost=data.get("actual_cost", 0.0),
            estimated_duration_days=data.get("estimated_duration_days"),
            auto_publish=data.get("auto_publish", False),
            quality_threshold=data.get("quality_threshold", 0.7),
            campaign_config=data.get("campaign_config", {}),
            performance_metrics=data.get("performance_metrics", {})
        )