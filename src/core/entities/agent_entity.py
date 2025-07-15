"""
Agent Entity - Core domain entity for AI agent management
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class AgentType(Enum):
    """AI Agent types"""
    DIRECTOR = "director"
    VOICE_DIRECTOR = "voice_director"
    CONTINUITY_DECISION = "continuity_decision"
    SCRIPT_WRITER = "script_writer"
    EDITOR = "editor"
    SOUNDMAN = "soundman"
    TREND_ANALYST = "trend_analyst"
    VISUAL_STYLE = "visual_style"
    OVERLAY_POSITIONING = "overlay_positioning"
    SUPER_MASTER = "super_master"

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class AgentDecision:
    """Represents a decision made by an agent"""
    decision_id: str
    decision_type: str
    decision_data: Dict[str, Any]
    confidence_score: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AgentEntity:
    """
    Core agent entity representing an AI agent

    This entity encapsulates all the business logic and rules
    related to AI agent management and decision tracking.
    """

    # Identity
    id: str
    name: str
    agent_type: AgentType

    # Core attributes
    status: AgentStatus = AgentStatus.IDLE
    session_id: Optional[str] = None
    video_id: Optional[str] = None

    # Agent capabilities
    capabilities: List[str] = field(default_factory=list)
    specialization: str = ""
    expertise_level: float = 1.0  # 0.0 to 1.0

    # Decision tracking
    decisions: List[AgentDecision] = field(default_factory=list)
    total_decisions: int = 0
    successful_decisions: int = 0
    failed_decisions: int = 0

    # Performance metrics
    average_decision_time: float = 0.0
    average_confidence_score: float = 0.0
    total_processing_time: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_active_at: Optional[datetime] = None

    # Configuration
    agent_config: Dict[str, Any] = field(default_factory=dict)

    # Current task
    current_task: Optional[str] = None
    current_task_progress: float = 0.0

    def __post_init__(self):
        """Post-initialization validation"""
        if not self.id.strip():
            raise ValueError("Agent ID cannot be empty")

        if not self.name.strip():
            raise ValueError("Agent name cannot be empty")

        if not 0.0 <= self.expertise_level <= 1.0:
            raise ValueError("Expertise level must be between 0.0 and 1.0")

    def assign_to_session(
        self,
        session_id: str,
        video_id: Optional[str] = None) -> None:
        """Assign agent to a session"""
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        if self.status != AgentStatus.IDLE:
            raise ValueError(f"Cannot assign agent from status: {self.status}")

        self.session_id = session_id
        self.video_id = video_id
        self.status = AgentStatus.WORKING
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def start_task(self, task_description: str) -> None:
        """Start a new task"""
        if not task_description.strip():
            raise ValueError("Task description cannot be empty")

        if self.status != AgentStatus.WORKING:
            raise ValueError(f"Cannot start task from status: {self.status}")

        self.current_task = task_description
        self.current_task_progress = 0.0
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def update_task_progress(self, progress: float) -> None:
        """Update current task progress"""
        if not 0.0 <= progress <= 100.0:
            raise ValueError("Progress must be between 0.0 and 100.0")

        if self.status != AgentStatus.WORKING:
            raise ValueError(f"Cannot update progress from status: {self.status}")

        self.current_task_progress = progress
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def complete_task(self) -> None:
        """Complete the current task"""
        if self.status != AgentStatus.WORKING:
            raise ValueError(f"Cannot complete task from status: {self.status}")

        self.current_task = None
        self.current_task_progress = 0.0
        self.status = AgentStatus.COMPLETED
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def fail_task(self, error_message: str) -> None:
        """Fail the current task"""
        if self.status != AgentStatus.WORKING:
            raise ValueError(f"Cannot fail task from status: {self.status}")

        self.current_task = None
        self.current_task_progress = 0.0
        self.status = AgentStatus.FAILED
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def pause_task(self) -> None:
        """Pause the current task"""
        if self.status != AgentStatus.WORKING:
            raise ValueError(f"Cannot pause task from status: {self.status}")

        self.status = AgentStatus.PAUSED
        self.updated_at = datetime.now()

    def resume_task(self) -> None:
        """Resume the paused task"""
        if self.status != AgentStatus.PAUSED:
            raise ValueError(f"Cannot resume task from status: {self.status}")

        self.status = AgentStatus.WORKING
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def reset_to_idle(self) -> None:
        """Reset agent to idle status"""
        self.status = AgentStatus.IDLE
        self.session_id = None
        self.video_id = None
        self.current_task = None
        self.current_task_progress = 0.0
        self.updated_at = datetime.now()

    def make_decision(self, decision_type: str, decision_data: Dict[str, Any],
                     confidence_score: float, reasoning: str) -> str:
        """Make a decision and record it"""
        if not decision_type.strip():
            raise ValueError("Decision type cannot be empty")

        if not 0.0 <= confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")

        decision_id = f"{self.id}_{decision_type}_{datetime.now().isoformat()}"

        decision = AgentDecision(
            decision_id=decision_id,
            decision_type=decision_type,
            decision_data=decision_data,
            confidence_score=confidence_score,
            reasoning=reasoning
        )

        self.decisions.append(decision)
        self.total_decisions += 1

        # Update performance metrics
        self._update_performance_metrics()

        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

        return decision_id

    def mark_decision_successful(self, decision_id: str) -> None:
        """Mark a decision as successful"""
        decision = self._find_decision(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        self.successful_decisions += 1
        self._update_performance_metrics()
        self.updated_at = datetime.now()

    def mark_decision_failed(self, decision_id: str) -> None:
        """Mark a decision as failed"""
        decision = self._find_decision(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        self.failed_decisions += 1
        self._update_performance_metrics()
        self.updated_at = datetime.now()

    def _find_decision(self, decision_id: str) -> Optional[AgentDecision]:
        """Find a decision by ID"""
        for decision in self.decisions:
            if decision.decision_id == decision_id:
                return decision
        return None

    def _update_performance_metrics(self) -> None:
        """Update performance metrics based on decisions"""
        if self.total_decisions > 0:
            total_confidence = sum(d.confidence_score for d in self.decisions)
            self.average_confidence_score = total_confidence / self.total_decisions

    def add_capability(self, capability: str) -> None:
        """Add a capability to the agent"""
        if not capability.strip():
            raise ValueError("Capability cannot be empty")

        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = datetime.now()

    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the agent"""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.updated_at = datetime.now()

    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def get_success_rate(self) -> float:
        """Get decision success rate as percentage"""
        if self.total_decisions == 0:
            return 0.0

        return (self.successful_decisions / self.total_decisions) * 100.0

    def get_failure_rate(self) -> float:
        """Get decision failure rate as percentage"""
        if self.total_decisions == 0:
            return 0.0

        return (self.failed_decisions / self.total_decisions) * 100.0

    def is_available(self) -> bool:
        """Check if agent is available for assignment"""
        return self.status == AgentStatus.IDLE

    def is_working(self) -> bool:
        """Check if agent is currently working"""
        return self.status == AgentStatus.WORKING

    def is_completed(self) -> bool:
        """Check if agent has completed its task"""
        return self.status == AgentStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if agent has failed its task"""
        return self.status == AgentStatus.FAILED

    def is_paused(self) -> bool:
        """Check if agent is paused"""
        return self.status == AgentStatus.PAUSED

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "capabilities": self.capabilities,
            "specialization": self.specialization,
            "expertise_level": self.expertise_level,
            "decisions": [
                {
                    "decision_id": d.decision_id,
                    "decision_type": d.decision_type,
                    "decision_data": d.decision_data,
                    "confidence_score": d.confidence_score,
                    "reasoning": d.reasoning,
                    "timestamp": d.timestamp.isoformat()
                }
                for d in self.decisions
            ],
            "total_decisions": self.total_decisions,
            "successful_decisions": self.successful_decisions,
            "failed_decisions": self.failed_decisions,
            "average_decision_time": self.average_decision_time,
            "average_confidence_score": self.average_confidence_score,
            "total_processing_time": self.total_processing_time,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "agent_config": self.agent_config,
            "current_task": self.current_task,
            "current_task_progress": self.current_task_progress
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentEntity":
        """Create entity from dictionary"""
        decisions = []
        for d_data in data.get("decisions", []):
            decision = AgentDecision(
                decision_id=d_data["decision_id"],
                decision_type=d_data["decision_type"],
                decision_data=d_data["decision_data"],
                confidence_score=d_data["confidence_score"],
                reasoning=d_data["reasoning"],
                timestamp=datetime.fromisoformat(d_data["timestamp"])
            )
            decisions.append(decision)

        return cls(
            id=data["id"],
            name=data["name"],
            agent_type=AgentType(data["agent_type"]),
            status=AgentStatus(data["status"]),
            session_id=data.get("session_id"),
            video_id=data.get("video_id"),
            capabilities=data.get("capabilities", []),
            specialization=data.get("specialization", ""),
            expertise_level=data.get("expertise_level", 1.0),
            decisions=decisions,
            total_decisions=data.get("total_decisions", 0),
            successful_decisions=data.get("successful_decisions", 0),
            failed_decisions=data.get("failed_decisions", 0),
            average_decision_time=data.get("average_decision_time", 0.0),
            average_confidence_score=data.get("average_confidence_score", 0.0),
            total_processing_time=data.get("total_processing_time", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_active_at=datetime.fromisoformat(data["last_active_at"]) if data.get("last_active_at") else None,
            agent_config=data.get("agent_config", {}),
            current_task=data.get("current_task"),
            current_task_progress=data.get("current_task_progress", 0.0)
        )
