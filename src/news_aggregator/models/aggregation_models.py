"""Aggregation Models for Channel Configuration"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, time
from enum import Enum
import re


class ScheduleType(Enum):
    """Types of content scheduling"""
    CONTINUOUS = "continuous"  # Run continuously
    INTERVAL = "interval"  # Run at intervals (e.g., every hour)
    SCHEDULED = "scheduled"  # Run at specific times
    TRIGGERED = "triggered"  # Run on external trigger


class FilterOperator(Enum):
    """Filter operators for content"""
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    REGEX = "regex"


@dataclass
class ContentFilter:
    """Filter for content selection"""
    field: str  # e.g., "title", "content", "tags"
    operator: FilterOperator
    value: Any
    case_sensitive: bool = False
    
    def matches(self, content_item: Any) -> bool:
        """Check if content item matches filter"""
        try:
            field_value = getattr(content_item, self.field)
            
            if isinstance(field_value, str) and not self.case_sensitive:
                field_value = field_value.lower()
                compare_value = self.value.lower() if isinstance(self.value, str) else self.value
            else:
                compare_value = self.value
            
            if self.operator == FilterOperator.CONTAINS:
                return compare_value in field_value
            elif self.operator == FilterOperator.NOT_CONTAINS:
                return compare_value not in field_value
            elif self.operator == FilterOperator.EQUALS:
                return field_value == compare_value
            elif self.operator == FilterOperator.NOT_EQUALS:
                return field_value != compare_value
            elif self.operator == FilterOperator.GREATER_THAN:
                return field_value > compare_value
            elif self.operator == FilterOperator.LESS_THAN:
                return field_value < compare_value
            elif self.operator == FilterOperator.REGEX:
                return bool(re.search(compare_value, str(field_value)))
            
        except (AttributeError, TypeError):
            return False
        
        return False


@dataclass
class AggregationRule:
    """Rule for aggregating content"""
    name: str
    description: str
    
    # Content selection
    include_filters: List[ContentFilter] = field(default_factory=list)
    exclude_filters: List[ContentFilter] = field(default_factory=list)
    
    # Limits
    max_items: int = 10
    max_duration: float = 300.0  # seconds
    min_relevance_score: float = 0.5
    
    # Grouping
    group_by: Optional[str] = None  # e.g., "category", "source"
    sort_by: str = "relevance_score"  # relevance_score, published_date, etc.
    sort_descending: bool = True
    
    # Time window
    time_window_hours: Optional[int] = 24
    
    def apply(self, content_items: List[Any]) -> List[Any]:
        """Apply rule to filter and sort content items"""
        filtered = content_items
        
        # Apply include filters
        for filter_rule in self.include_filters:
            filtered = [item for item in filtered if filter_rule.matches(item)]
        
        # Apply exclude filters
        for filter_rule in self.exclude_filters:
            filtered = [item for item in filtered if not filter_rule.matches(item)]
        
        # Apply relevance threshold
        if hasattr(filtered[0] if filtered else None, 'relevance_score'):
            filtered = [item for item in filtered 
                       if item.relevance_score >= self.min_relevance_score]
        
        # Sort
        if self.sort_by and hasattr(filtered[0] if filtered else None, self.sort_by):
            filtered.sort(key=lambda x: getattr(x, self.sort_by), 
                         reverse=self.sort_descending)
        
        # Apply limit
        return filtered[:self.max_items]


@dataclass
class ScheduleConfig:
    """Configuration for content scheduling"""
    schedule_type: ScheduleType
    
    # For INTERVAL type
    interval_minutes: Optional[int] = None
    
    # For SCHEDULED type
    daily_times: List[time] = field(default_factory=list)  # Times to run each day
    days_of_week: List[int] = field(default_factory=lambda: list(range(7)))  # 0=Monday
    
    # For TRIGGERED type
    trigger_endpoint: Optional[str] = None
    
    # Common settings
    timezone: str = "UTC"
    retry_on_failure: bool = True
    max_retries: int = 3
    
    def get_next_run_time(self, from_time: datetime) -> Optional[datetime]:
        """Calculate next run time based on schedule"""
        if self.schedule_type == ScheduleType.CONTINUOUS:
            return from_time
        
        elif self.schedule_type == ScheduleType.INTERVAL:
            if not self.interval_minutes:
                return None
            from datetime import timedelta
            return from_time + timedelta(minutes=self.interval_minutes)
        
        elif self.schedule_type == ScheduleType.SCHEDULED:
            # Find next scheduled time
            for scheduled_time in sorted(self.daily_times):
                next_time = from_time.replace(
                    hour=scheduled_time.hour,
                    minute=scheduled_time.minute,
                    second=0,
                    microsecond=0
                )
                if next_time > from_time and from_time.weekday() in self.days_of_week:
                    return next_time
            
            # Try next day
            from datetime import timedelta
            return self.get_next_run_time(from_time + timedelta(days=1))
        
        return None


@dataclass
class OutputConfig:
    """Configuration for output generation"""
    # Video settings
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    video_codec: str = "h264"
    video_bitrate: str = "5M"
    
    # Audio settings
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"
    audio_sample_rate: int = 44100
    
    # Output format
    format: str = "mp4"
    
    # Quality settings
    quality_preset: str = "high"  # low, medium, high, ultra
    
    # File naming
    filename_template: str = "{channel_name}_{date}_{sequence}"
    
    # Distribution
    upload_platforms: List[str] = field(default_factory=list)  # youtube, tiktok, etc.
    local_copy: bool = True
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelConfig:
    """Configuration for an automated content channel"""
    id: str
    name: str
    description: str
    
    # Content sources
    sources: List['NewsSource'] = field(default_factory=list)
    
    # Aggregation rules
    aggregation_rules: List[AggregationRule] = field(default_factory=list)
    
    # Template and theme
    template_name: str = "professional_news"
    theme_name: str = "default"
    
    # Scheduling
    schedule_config: ScheduleConfig = field(default_factory=lambda: ScheduleConfig(ScheduleType.SCHEDULED))
    
    # Output
    output_config: OutputConfig = field(default_factory=OutputConfig)
    
    # Multi-language
    primary_language: str = "en"
    target_languages: List[str] = field(default_factory=list)
    
    # AI Configuration
    use_ai_presenter: bool = True
    presenter_style: str = "formal_news"
    
    # Content settings
    intro_text_template: str = "Welcome to {channel_name}. Here are today's top stories."
    outro_text_template: str = "Thanks for watching {channel_name}. See you next time!"
    
    # Hooks for customization
    pre_processing_hook: Optional[str] = None  # Script to run before processing
    post_processing_hook: Optional[str] = None  # Script to run after processing
    
    # Status
    is_active: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate channel configuration"""
        errors = []
        
        if not self.sources:
            errors.append("No content sources configured")
        
        if not self.aggregation_rules:
            errors.append("No aggregation rules configured")
        
        if self.schedule_config.schedule_type == ScheduleType.INTERVAL:
            if not self.schedule_config.interval_minutes:
                errors.append("Interval schedule requires interval_minutes")
        
        if self.schedule_config.schedule_type == ScheduleType.SCHEDULED:
            if not self.schedule_config.daily_times:
                errors.append("Scheduled type requires daily_times")
        
        return errors


@dataclass
class AggregationSession:
    """Tracks a single aggregation session"""
    id: str
    channel_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Content tracking
    total_items_scraped: int = 0
    items_after_filtering: int = 0
    items_used_in_video: int = 0
    
    # Source breakdown
    items_per_source: Dict[str, int] = field(default_factory=dict)
    
    # Performance metrics
    scraping_duration: float = 0.0  # seconds
    processing_duration: float = 0.0
    composition_duration: float = 0.0
    total_duration: float = 0.0
    
    # Output
    output_file: Optional[str] = None
    output_size: Optional[int] = None  # bytes
    output_duration: Optional[float] = None  # seconds
    
    # Status
    status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None
    
    # Detailed logs
    log_entries: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_log(self, level: str, message: str, data: Optional[Dict] = None):
        """Add a log entry"""
        self.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        })
    
    def complete(self, output_file: str, output_size: int, output_duration: float):
        """Mark session as completed"""
        self.end_time = datetime.now()
        self.status = "completed"
        self.output_file = output_file
        self.output_size = output_size
        self.output_duration = output_duration
        self.total_duration = (self.end_time - self.start_time).total_seconds()
    
    def fail(self, error_message: str):
        """Mark session as failed"""
        self.end_time = datetime.now()
        self.status = "failed"
        self.error_message = error_message
        self.total_duration = (self.end_time - self.start_time).total_seconds()