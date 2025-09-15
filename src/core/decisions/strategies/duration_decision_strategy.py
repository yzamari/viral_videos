"""
Duration Decision Strategy - Single Responsibility Principle Implementation

This strategy is responsible ONLY for making duration-related decisions,
demonstrating proper SRP application.
"""

import logging
from typing import Optional
from ..interfaces.decision_strategy import (
    IDecisionStrategy,
    DecisionContext,
    DecisionResult
)

logger = logging.getLogger(__name__)


class DurationDecisionStrategy(IDecisionStrategy):
    """
    Strategy for making duration decisions following Single Responsibility Principle.
    
    This class has ONE responsibility: determining the optimal duration
    for content based on platform, audience, and mission requirements.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize duration decision strategy."""
        self.config = config or {}
        self._platform_defaults = {
            'tiktok': {'min': 15, 'max': 60, 'optimal': 30},
            'youtube': {'min': 60, 'max': 600, 'optimal': 180},
            'instagram': {'min': 15, 'max': 90, 'optimal': 45},
            'twitter': {'min': 5, 'max': 140, 'optimal': 30}
        }
        self._segment_duration = 8  # Standard 8-second segments
    
    def decide(self, context: DecisionContext) -> DecisionResult:
        """
        Make duration decision based on platform and mission context.
        
        Args:
            context: Decision context with platform and mission data
            
        Returns:
            DecisionResult: Duration decision with reasoning
        """
        if not self.can_decide(context):
            raise ValueError(f"Cannot make duration decision with given context: missing {self._get_missing_fields(context)}")
        
        # Get platform constraints
        platform_config = self._platform_defaults.get(context.platform, self._platform_defaults['tiktok'])
        
        # Start with platform optimal duration
        base_duration = platform_config['optimal']
        
        # Adjust based on mission complexity
        mission_complexity = self._analyze_mission_complexity(context.mission)
        duration_adjustment = self._calculate_duration_adjustment(mission_complexity)
        
        # Calculate target duration
        target_duration = max(
            platform_config['min'],
            min(platform_config['max'], base_duration + duration_adjustment)
        )
        
        # Align to 8-second segments for video generation efficiency
        aligned_duration = self._align_to_segments(target_duration)
        
        # Calculate confidence based on context completeness
        confidence = self._calculate_confidence(context, aligned_duration, platform_config)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            context, aligned_duration, platform_config, mission_complexity
        )
        
        return DecisionResult(
            value=aligned_duration,
            confidence=confidence,
            source="duration_strategy",
            reasoning=reasoning,
            alternatives={
                'min_duration': platform_config['min'],
                'max_duration': platform_config['max'],
                'platform_optimal': platform_config['optimal'],
                'unaligned_duration': target_duration
            }
        )
    
    def can_decide(self, context: DecisionContext) -> bool:
        """
        Check if duration decision can be made with given context.
        
        Args:
            context: Decision context to evaluate
            
        Returns:
            bool: True if can make decision
        """
        required = self.required_context_fields
        return all(getattr(context, field, None) is not None for field in required)
    
    @property
    def decision_type(self) -> str:
        """Get decision type identifier."""
        return "duration"
    
    @property
    def required_context_fields(self) -> list[str]:
        """Get required context fields for duration decision."""
        return ["mission", "platform"]
    
    def _get_missing_fields(self, context: DecisionContext) -> list[str]:
        """Get list of missing required fields."""
        return [
            field for field in self.required_context_fields
            if getattr(context, field, None) is None
        ]
    
    def _analyze_mission_complexity(self, mission: str) -> float:
        """
        Analyze mission complexity to adjust duration.
        
        Args:
            mission: Mission description
            
        Returns:
            float: Complexity score (0.0 to 1.0)
        """
        complexity_indicators = [
            'research', 'analyze', 'comprehensive', 'detailed', 'multiple',
            'complex', 'various', 'extensive', 'thorough', 'in-depth'
        ]
        
        mission_lower = mission.lower()
        complexity_score = sum(
            1 for indicator in complexity_indicators
            if indicator in mission_lower
        ) / len(complexity_indicators)
        
        return min(1.0, complexity_score)
    
    def _calculate_duration_adjustment(self, complexity: float) -> int:
        """
        Calculate duration adjustment based on mission complexity.
        
        Args:
            complexity: Mission complexity score (0.0 to 1.0)
            
        Returns:
            int: Duration adjustment in seconds
        """
        # More complex missions need more time
        max_adjustment = 30  # Maximum 30 seconds adjustment
        return int(complexity * max_adjustment)
    
    def _align_to_segments(self, duration: int) -> int:
        """
        Align duration to 8-second segments for video generation efficiency.
        
        Args:
            duration: Target duration in seconds
            
        Returns:
            int: Aligned duration in seconds
        """
        segments = max(1, round(duration / self._segment_duration))
        return segments * self._segment_duration
    
    def _calculate_confidence(self, context: DecisionContext, duration: int, platform_config: dict) -> float:
        """
        Calculate confidence in duration decision.
        
        Args:
            context: Decision context
            duration: Calculated duration
            platform_config: Platform configuration
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.8
        
        # Higher confidence if duration is within optimal range
        optimal = platform_config['optimal']
        distance_from_optimal = abs(duration - optimal) / optimal
        optimal_bonus = max(0, 0.2 - distance_from_optimal)
        
        # Bonus for having target audience info
        audience_bonus = 0.1 if context.target_audience else 0
        
        return min(1.0, base_confidence + optimal_bonus + audience_bonus)
    
    def _generate_reasoning(self, context: DecisionContext, duration: int, 
                          platform_config: dict, complexity: float) -> str:
        """
        Generate human-readable reasoning for the duration decision.
        
        Args:
            context: Decision context
            duration: Final duration
            platform_config: Platform configuration
            complexity: Mission complexity score
            
        Returns:
            str: Reasoning explanation
        """
        segments = duration // self._segment_duration
        
        reasoning_parts = [
            f"Selected {duration}s duration for {context.platform} platform",
            f"({segments} segments of {self._segment_duration}s each)",
            f"Platform optimal: {platform_config['optimal']}s"
        ]
        
        if complexity > 0.5:
            reasoning_parts.append(f"Extended for mission complexity ({complexity:.1%})")
        
        if context.target_audience:
            reasoning_parts.append(f"Optimized for {context.target_audience}")
        
        return ". ".join(reasoning_parts) + "."

    def __str__(self) -> str:
        """String representation for debugging."""
        return f"DurationDecisionStrategy(platforms={list(self._platform_defaults.keys())})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"DurationDecisionStrategy(config={self.config}, segment_duration={self._segment_duration})"