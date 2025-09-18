"""
Base Interfaces for SOLID Service Architecture
Following Interface Segregation and Dependency Inversion Principles
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# ============= Core Domain Models =============

@dataclass
class GenerationRequest:
    """Immutable generation request"""
    clip_id: str
    prompt: Any
    duration: float
    platform: str
    style: str
    metadata: Dict[str, Any]


@dataclass
class GenerationResult:
    """Immutable generation result"""
    success: bool
    output_path: Optional[str]
    metadata: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class OptimizationRequest:
    """Request for prompt optimization"""
    original_prompt: Any
    optimization_level: str
    context: Dict[str, Any]


@dataclass
class OptimizationResult:
    """Result of prompt optimization"""
    optimized_prompt: str
    modifications_applied: List[str]
    success_probability: float


# ============= Service Interfaces =============

class IPromptOptimizer(ABC):
    """Interface for prompt optimization service"""
    
    @abstractmethod
    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        """Optimize a prompt"""
        pass
    
    @abstractmethod
    def validate_safety(self, prompt: str) -> Tuple[bool, List[str]]:
        """Validate prompt safety"""
        pass


class IRetryStrategy(ABC):
    """Interface for retry strategies"""
    
    @abstractmethod
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if should retry"""
        pass
    
    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Get delay before next retry"""
        pass


class IVideoGenerator(ABC):
    """Interface for video generation"""
    
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate video from request"""
        pass
    
    @abstractmethod
    def validate_request(self, request: GenerationRequest) -> Tuple[bool, Optional[str]]:
        """Validate generation request"""
        pass


class IScriptGenerator(ABC):
    """Interface for script generation"""
    
    @abstractmethod
    def generate_script(self, mission: str, duration: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script from mission"""
        pass
    
    @abstractmethod
    def validate_script(self, script: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate generated script"""
        pass


class IAudioGenerator(ABC):
    """Interface for audio generation"""
    
    @abstractmethod
    def generate_audio(self, text: str, voice_config: Dict[str, Any]) -> str:
        """Generate audio from text"""
        pass
    
    @abstractmethod
    def analyze_duration(self, audio_files: List[str], target_duration: float) -> Dict[str, Any]:
        """Analyze audio duration"""
        pass


class IStoryboardGenerator(ABC):
    """Interface for storyboard generation"""
    
    @abstractmethod
    def generate_storyboard(self, script: Dict[str, Any], style: str) -> Dict[str, Any]:
        """Generate storyboard from script"""
        pass
    
    @abstractmethod
    def update_scene(self, scene_id: str, updates: Dict[str, Any]) -> bool:
        """Update a storyboard scene"""
        pass


class IMonitoringService(ABC):
    """Interface for monitoring and metrics"""
    
    @abstractmethod
    def record_metric(self, metric_name: str, value: Any, tags: Dict[str, str] = None):
        """Record a metric"""
        pass
    
    @abstractmethod
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """Record an event"""
        pass
    
    @abstractmethod
    def get_metrics(self, metric_name: str = None) -> Dict[str, Any]:
        """Get metrics"""
        pass


class ICacheService(ABC):
    """Interface for caching service"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None):
        """Set in cache"""
        pass
    
    @abstractmethod
    def invalidate(self, key: str):
        """Invalidate cache entry"""
        pass


class IOrchestrator(ABC):
    """Interface for service orchestration"""
    
    @abstractmethod
    def process_request(self, request: GenerationRequest) -> GenerationResult:
        """Process end-to-end generation request"""
        pass
    
    @abstractmethod
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        pass


# ============= Event System =============

class EventType(Enum):
    """Types of system events"""
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    GENERATION_FAILED = "generation_failed"
    OPTIMIZATION_APPLIED = "optimization_applied"
    RETRY_ATTEMPTED = "retry_attempted"
    SERVICE_ERROR = "service_error"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"


@dataclass
class SystemEvent:
    """System event for pub/sub"""
    event_type: EventType
    timestamp: str
    service: str
    data: Dict[str, Any]


class IEventBus(ABC):
    """Interface for event bus"""
    
    @abstractmethod
    def publish(self, event: SystemEvent):
        """Publish an event"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: EventType, handler: callable):
        """Subscribe to event type"""
        pass


# ============= Factory Interfaces =============

class IServiceFactory(ABC):
    """Abstract factory for creating services"""
    
    @abstractmethod
    def create_video_generator(self) -> IVideoGenerator:
        """Create video generator"""
        pass
    
    @abstractmethod
    def create_script_generator(self) -> IScriptGenerator:
        """Create script generator"""
        pass
    
    @abstractmethod
    def create_audio_generator(self) -> IAudioGenerator:
        """Create audio generator"""
        pass
    
    @abstractmethod
    def create_prompt_optimizer(self) -> IPromptOptimizer:
        """Create prompt optimizer"""
        pass
    
    @abstractmethod
    def create_monitoring_service(self) -> IMonitoringService:
        """Create monitoring service"""
        pass