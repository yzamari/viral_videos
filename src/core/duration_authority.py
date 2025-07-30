"""
Duration Authority - Single source of truth for duration management
Replaces distributed duration decisions with centralized control
"""

import logging
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of components that report duration"""
    SCRIPT = "script"
    AUDIO = "audio"
    VIDEO = "video"
    SUBTITLES = "subtitles"


@dataclass
class DurationReport:
    """Duration report from a component"""
    component: ComponentType
    target_duration: float
    actual_duration: float
    confidence: float
    metadata: Dict[str, any]
    timestamp: float


class DurationAuthority:
    """
    Single source of truth for all duration decisions and validation.
    
    Replaces the distributed duration management across multiple classes:
    - DecisionFramework
    - DurationCoordinator  
    - AudioDurationManager
    - Enhanced Script Processor duration logic
    """
    
    def __init__(self, target_duration: float, tolerance_percent: float = 0.05):
        """
        Initialize Duration Authority
        
        Args:
            target_duration: Target video duration in seconds
            tolerance_percent: Allowable deviation (0.05 = 5%)
        """
        self.target_duration = target_duration
        self.tolerance_percent = tolerance_percent
        self.min_allowed = target_duration * (1 - tolerance_percent)
        self.max_allowed = target_duration * (1 + tolerance_percent)
        
        # Track component durations
        self.component_reports: List[DurationReport] = []
        self.component_durations: Dict[ComponentType, float] = {}
        
        # Duration calculation constants
        self.WORDS_PER_SECOND = 2.3  # Conservative estimate for TTS
        self.MIN_SEGMENT_DURATION = 2.0  # Minimum audio segment
        self.MAX_SEGMENT_DURATION = 8.0  # Maximum to prevent long segments
        self.PADDING_BETWEEN_SEGMENTS = 0.3  # FFmpeg concat padding
        
        logger.info(f"🎯 Duration Authority initialized:")
        logger.info(f"   Target: {target_duration}s")
        logger.info(f"   Acceptable range: {self.min_allowed:.1f}s - {self.max_allowed:.1f}s")
        logger.info(f"   Tolerance: ±{tolerance_percent * 100:.1f}%")
        
    def get_target_duration(self) -> float:
        """Get the authoritative target duration"""
        return self.target_duration
        
    def get_max_allowed_duration(self) -> float:
        """Get maximum allowed duration with tolerance"""
        return self.max_allowed
        
    def get_min_allowed_duration(self) -> float:
        """Get minimum allowed duration with tolerance"""
        return self.min_allowed
        
    def calculate_max_words(self) -> int:
        """Calculate maximum words for target duration"""
        # Use conservative estimate to prevent overruns
        max_words = int(self.target_duration * self.WORDS_PER_SECOND * 0.85)
        logger.info(f"📝 Max words for {self.target_duration}s: {max_words}")
        return max_words
        
    def calculate_max_segments(self) -> int:
        """Calculate maximum segments for target duration"""
        max_segments = int(self.target_duration / self.MIN_SEGMENT_DURATION)
        logger.info(f"🎵 Max segments for {self.target_duration}s: {max_segments}")
        return max_segments
        
    def calculate_max_clips(self) -> int:
        """Calculate maximum video clips for target duration"""
        max_clips = int(self.target_duration / self.MAX_SEGMENT_DURATION) + 1
        logger.info(f"🎬 Max clips for {self.target_duration}s: {max_clips}")
        return max_clips
        
    def register_component_duration(self, 
                                  component: ComponentType,
                                  actual_duration: float,
                                  confidence: float = 1.0,
                                  metadata: Optional[Dict] = None,
                                  timestamp: Optional[float] = None) -> bool:
        """
        Register actual duration from a component
        
        Args:
            component: Which component is reporting
            actual_duration: Measured duration in seconds
            confidence: How confident this measurement is (0-1)
            metadata: Additional information about the measurement
            timestamp: When the measurement was taken
            
        Returns:
            True if within tolerance, False if exceeds limits
        """
        import time
        
        if metadata is None:
            metadata = {}
        if timestamp is None:
            timestamp = time.time()
            
        report = DurationReport(
            component=component,
            target_duration=self.target_duration,
            actual_duration=actual_duration,
            confidence=confidence,
            metadata=metadata,
            timestamp=timestamp
        )
        
        self.component_reports.append(report)
        self.component_durations[component] = actual_duration
        
        is_within_tolerance = self.is_within_tolerance(actual_duration)
        status = "✅" if is_within_tolerance else "❌"
        
        logger.info(f"{status} {component.value} duration: {actual_duration:.1f}s "
                   f"(target: {self.target_duration:.1f}s, confidence: {confidence:.1f})")
        
        if not is_within_tolerance:
            difference = actual_duration - self.target_duration
            logger.warning(f"⚠️ {component.value} duration exceeds tolerance by {difference:.1f}s")
            
        return is_within_tolerance
        
    def is_within_tolerance(self, duration: float) -> bool:
        """Check if duration is within acceptable tolerance"""
        return self.min_allowed <= duration <= self.max_allowed
        
    def get_final_duration_recommendation(self) -> float:
        """
        Get recommended final duration based on all component reports
        
        Strategy:
        1. If all components within tolerance, use maximum
        2. If any exceed tolerance, cap at max allowed
        3. Prioritize audio duration (most accurate)
        """
        if not self.component_durations:
            logger.warning("⚠️ No component durations registered, using target")
            return self.target_duration
            
        # Prioritize audio duration if available (most accurate)
        if ComponentType.AUDIO in self.component_durations:
            audio_duration = self.component_durations[ComponentType.AUDIO]
            if self.is_within_tolerance(audio_duration):
                logger.info(f"🎵 Using audio duration as final: {audio_duration:.1f}s")
                return audio_duration
            else:
                logger.warning(f"⚠️ Audio duration {audio_duration:.1f}s exceeds tolerance")
                
        # Use maximum of all components within tolerance
        valid_durations = [
            duration for duration in self.component_durations.values()
            if self.is_within_tolerance(duration)
        ]
        
        if valid_durations:
            recommended = max(valid_durations)
            logger.info(f"✅ Recommended final duration: {recommended:.1f}s")
            return recommended
        else:
            # All components exceed tolerance, cap at maximum
            logger.warning(f"⚠️ All components exceed tolerance, capping at {self.max_allowed:.1f}s")
            return self.max_allowed
            
    def validate_final_result(self) -> Tuple[bool, List[str]]:
        """
        Validate the final video generation result
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if not self.component_durations:
            issues.append("No component durations were registered")
            return False, issues
            
        # Check each component
        for component, duration in self.component_durations.items():
            if not self.is_within_tolerance(duration):
                difference = duration - self.target_duration
                issues.append(f"{component.value} duration {duration:.1f}s exceeds tolerance by {difference:.1f}s")
                
        # Check for sync issues between components
        if ComponentType.AUDIO in self.component_durations and ComponentType.SUBTITLES in self.component_durations:
            audio_dur = self.component_durations[ComponentType.AUDIO]
            subtitle_dur = self.component_durations[ComponentType.SUBTITLES]
            sync_diff = abs(audio_dur - subtitle_dur)
            
            if sync_diff > 0.5:  # More than 500ms difference
                issues.append(f"Audio-subtitle sync issue: {sync_diff:.1f}s difference")
                
        is_valid = len(issues) == 0
        status = "✅" if is_valid else "❌"
        logger.info(f"{status} Final validation: {is_valid} ({len(issues)} issues)")
        
        return is_valid, issues
        
    def get_generation_constraints(self) -> Dict[str, any]:
        """
        Get constraints for content generation based on target duration
        
        Returns dictionary of constraints for all components
        """
        return {
            "target_duration": self.target_duration,
            "max_allowed_duration": self.max_allowed,
            "min_allowed_duration": self.min_allowed,
            "max_words": self.calculate_max_words(),
            "max_segments": self.calculate_max_segments(),  
            "max_clips": self.calculate_max_clips(),
            "words_per_second": self.WORDS_PER_SECOND,
            "min_segment_duration": self.MIN_SEGMENT_DURATION,
            "max_segment_duration": self.MAX_SEGMENT_DURATION,
            "padding_between_segments": self.PADDING_BETWEEN_SEGMENTS,
            "tolerance_percent": self.tolerance_percent
        }
        
    def create_duration_contract(self) -> 'DurationContract':
        """Create a duration contract for enforcement"""
        return DurationContract(
            authority=self,
            max_duration=self.max_allowed,
            tolerance=self.tolerance_percent
        )


class DurationContract:
    """
    Contract for enforcing duration constraints on generated content
    Used by generators to validate and enforce duration limits
    """
    
    def __init__(self, authority: DurationAuthority, max_duration: float, tolerance: float = 0.05):
        self.authority = authority
        self.max_duration = max_duration
        self.tolerance = tolerance
        
    def validate_duration(self, actual_duration: float) -> bool:
        """Validate if duration meets contract"""
        return actual_duration <= self.max_duration
        
    def enforce_on_script(self, script_content: str, estimated_duration: float) -> str:
        """Enforce duration constraint on script content"""
        if estimated_duration <= self.max_duration:
            return script_content
            
        # Calculate how much to trim
        target_ratio = self.max_duration / estimated_duration
        words = script_content.split()
        target_words = int(len(words) * target_ratio)
        
        # Find sentence boundary near target
        sentences = script_content.split('.')
        trimmed_sentences = []
        word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= target_words:
                trimmed_sentences.append(sentence)
                word_count += sentence_words
            else:
                break
                
        trimmed_script = '. '.join(trimmed_sentences)
        if trimmed_script and not trimmed_script.endswith('.'):
            trimmed_script += '.'
            
        logger.info(f"✂️ Script trimmed: {len(words)} → {len(trimmed_script.split())} words")
        return trimmed_script
        
    def get_max_duration(self) -> float:
        """Get maximum allowed duration"""
        return self.max_duration