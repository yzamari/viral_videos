"""
Duration Feedback System - Coordinates duration management between components
Provides real-time feedback and quality gates for duration targets
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

from ..utils.logging_config import get_logger
from ..config import video_config

logger = get_logger(__name__)


@dataclass
class DurationCheckpoint:
    """Checkpoint for duration tracking at various stages"""
    stage: str
    timestamp: datetime
    target_duration: float
    actual_duration: float
    component: str
    is_within_tolerance: bool
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class DurationFeedback:
    """Feedback data for duration management"""
    current_stage: str
    target_duration: float
    checkpoints: List[DurationCheckpoint]
    quality_score: float
    can_proceed: bool
    must_regenerate: bool
    recommendations: List[str]
    adjustments_made: List[str]


class DurationFeedbackSystem:
    """Manages duration feedback between all components"""
    
    def __init__(self, session_context=None):
        """Initialize Duration Feedback System"""
        self.session_context = session_context
        self.checkpoints: List[DurationCheckpoint] = []
        self.target_duration: float = 0
        self.tolerance_percent = video_config.audio.duration_tolerance_percent
        self.quality_gates_enabled = video_config.audio.block_on_duration_failure
        
        logger.info("📊 Duration Feedback System initialized")
        logger.info(f"   Tolerance: ±{self.tolerance_percent}%")
        logger.info(f"   Quality gates: {'✅ ENABLED' if self.quality_gates_enabled else '❌ DISABLED'}")
    
    def set_target_duration(self, duration: float):
        """Set the target duration for the video"""
        self.target_duration = duration
        logger.info(f"🎯 Target duration set: {duration}s")
    
    def add_checkpoint(self, stage: str, actual_duration: float, component: str, 
                      details: Optional[Dict[str, Any]] = None) -> DurationCheckpoint:
        """Add a duration checkpoint from a component"""
        tolerance_range = self.target_duration * (self.tolerance_percent / 100)
        min_duration = self.target_duration - tolerance_range
        max_duration = self.target_duration + tolerance_range
        
        is_within_tolerance = min_duration <= actual_duration <= max_duration
        
        checkpoint = DurationCheckpoint(
            stage=stage,
            timestamp=datetime.now(),
            target_duration=self.target_duration,
            actual_duration=actual_duration,
            component=component,
            is_within_tolerance=is_within_tolerance,
            details=details or {}
        )
        
        # Add warnings/errors
        if not is_within_tolerance:
            diff = actual_duration - self.target_duration
            diff_percent = (diff / self.target_duration) * 100
            
            if actual_duration < min_duration:
                checkpoint.warnings.append(
                    f"Duration {actual_duration:.1f}s is {abs(diff):.1f}s too short ({diff_percent:.1f}%)"
                )
            else:
                checkpoint.warnings.append(
                    f"Duration {actual_duration:.1f}s is {diff:.1f}s too long ({diff_percent:.1f}%)"
                )
        
        self.checkpoints.append(checkpoint)
        
        logger.info(f"📍 Checkpoint: {stage} - {actual_duration:.1f}s "
                   f"({'✅ OK' if is_within_tolerance else '⚠️ OUT OF RANGE'})")
        
        # Save checkpoint to session if available
        if self.session_context:
            self._save_checkpoint_to_session(checkpoint)
        
        return checkpoint
    
    def get_feedback(self, current_stage: str) -> DurationFeedback:
        """Get comprehensive feedback for the current stage"""
        # Calculate quality score based on checkpoints
        if self.checkpoints:
            valid_checkpoints = sum(1 for cp in self.checkpoints if cp.is_within_tolerance)
            quality_score = valid_checkpoints / len(self.checkpoints)
        else:
            quality_score = 1.0
        
        # Determine if we can proceed
        critical_stages = ['audio_generation', 'video_generation', 'final_assembly']
        critical_failures = [
            cp for cp in self.checkpoints 
            if cp.stage in critical_stages and not cp.is_within_tolerance
        ]
        
        can_proceed = not (self.quality_gates_enabled and critical_failures)
        must_regenerate = len(critical_failures) > 0 and quality_score < 0.6
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Track adjustments made
        adjustments_made = self._get_adjustments_made()
        
        feedback = DurationFeedback(
            current_stage=current_stage,
            target_duration=self.target_duration,
            checkpoints=self.checkpoints,
            quality_score=quality_score,
            can_proceed=can_proceed,
            must_regenerate=must_regenerate,
            recommendations=recommendations,
            adjustments_made=adjustments_made
        )
        
        # Log feedback summary
        logger.info(f"📊 Duration Feedback Summary:")
        logger.info(f"   Stage: {current_stage}")
        logger.info(f"   Quality Score: {quality_score:.2f}")
        logger.info(f"   Can Proceed: {'✅' if can_proceed else '❌'}")
        logger.info(f"   Must Regenerate: {'❌ YES' if must_regenerate else '✅ NO'}")
        
        return feedback
    
    def apply_quality_gate(self, stage: str, actual_duration: float, 
                          component: str) -> Tuple[bool, str]:
        """Apply quality gate check for duration compliance"""
        checkpoint = self.add_checkpoint(stage, actual_duration, component)
        
        if not self.quality_gates_enabled:
            return True, "Quality gates disabled"
        
        if checkpoint.is_within_tolerance:
            return True, "Duration within tolerance"
        
        # Check if this is a critical stage
        critical_stages = ['audio_generation', 'final_assembly']
        if stage in critical_stages:
            diff = actual_duration - self.target_duration
            message = (f"QUALITY GATE FAILED: {stage} duration {actual_duration:.1f}s "
                      f"is {abs(diff):.1f}s {'short' if diff < 0 else 'long'} "
                      f"(target: {self.target_duration}s)")
            logger.error(f"🚫 {message}")
            return False, message
        
        # Non-critical stage - just warn
        logger.warning(f"⚠️ Quality gate warning for {stage} but proceeding")
        return True, "Non-critical stage - proceeding with warning"
    
    def suggest_adjustments(self, component: str) -> Dict[str, Any]:
        """Suggest adjustments based on current feedback"""
        suggestions = {
            'component': component,
            'adjustments': []
        }
        
        # Analyze recent checkpoints
        recent_checkpoints = self.checkpoints[-3:] if len(self.checkpoints) >= 3 else self.checkpoints
        
        for checkpoint in recent_checkpoints:
            if not checkpoint.is_within_tolerance:
                diff = checkpoint.actual_duration - checkpoint.target_duration
                diff_percent = abs(diff) / checkpoint.target_duration
                
                if checkpoint.component == 'script_processor':
                    if diff < 0:  # Too short
                        suggestions['adjustments'].append({
                            'type': 'expand_script',
                            'factor': 1 + diff_percent,
                            'description': f"Expand script by {diff_percent:.0%}"
                        })
                    else:  # Too long
                        suggestions['adjustments'].append({
                            'type': 'trim_script',
                            'factor': 1 - diff_percent,
                            'description': f"Trim script by {diff_percent:.0%}"
                        })
                
                elif checkpoint.component == 'audio_generator':
                    if diff < 0:  # Too short
                        suggestions['adjustments'].append({
                            'type': 'slow_speech_rate',
                            'factor': 0.9,
                            'description': "Reduce speech rate by 10%"
                        })
                    else:  # Too long
                        suggestions['adjustments'].append({
                            'type': 'increase_speech_rate',
                            'factor': 1.1,
                            'description': "Increase speech rate by 10%"
                        })
                
                elif checkpoint.component == 'video_generator':
                    suggestions['adjustments'].append({
                        'type': 'adjust_clip_durations',
                        'target': checkpoint.target_duration,
                        'description': f"Adjust clip durations to match {checkpoint.target_duration}s"
                    })
        
        return suggestions
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on checkpoints"""
        recommendations = []
        
        # Check for consistent patterns
        short_count = sum(1 for cp in self.checkpoints 
                         if cp.actual_duration < cp.target_duration - cp.target_duration * 0.05)
        long_count = sum(1 for cp in self.checkpoints 
                        if cp.actual_duration > cp.target_duration + cp.target_duration * 0.05)
        
        if short_count > long_count and short_count > 1:
            recommendations.append("Content is consistently too short - consider adding more detail or slowing speech")
        elif long_count > short_count and long_count > 1:
            recommendations.append("Content is consistently too long - consider trimming or increasing speech rate")
        
        # Component-specific recommendations
        audio_checkpoints = [cp for cp in self.checkpoints if 'audio' in cp.component.lower()]
        if audio_checkpoints and not audio_checkpoints[-1].is_within_tolerance:
            recommendations.append("Audio duration mismatch - regenerate with adjusted speech rate")
        
        return recommendations
    
    def _get_adjustments_made(self) -> List[str]:
        """Get list of adjustments made during generation"""
        adjustments = []
        
        for checkpoint in self.checkpoints:
            if 'adjustments' in checkpoint.details:
                for adj in checkpoint.details['adjustments']:
                    adjustments.append(f"{checkpoint.component}: {adj}")
        
        return adjustments
    
    def _save_checkpoint_to_session(self, checkpoint: DurationCheckpoint):
        """Save checkpoint to session for tracking"""
        try:
            if not self.session_context:
                return
            
            checkpoint_data = {
                'stage': checkpoint.stage,
                'timestamp': checkpoint.timestamp.isoformat(),
                'target_duration': checkpoint.target_duration,
                'actual_duration': checkpoint.actual_duration,
                'component': checkpoint.component,
                'is_within_tolerance': checkpoint.is_within_tolerance,
                'details': checkpoint.details,
                'warnings': checkpoint.warnings,
                'errors': checkpoint.errors
            }
            
            # Save to session
            feedback_dir = os.path.join(self.session_context.session_dir, 'duration_feedback')
            os.makedirs(feedback_dir, exist_ok=True)
            
            checkpoint_file = os.path.join(
                feedback_dir, 
                f"checkpoint_{checkpoint.stage}_{checkpoint.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint to session: {e}")
    
    def export_feedback_report(self) -> Dict[str, Any]:
        """Export comprehensive feedback report"""
        return {
            'target_duration': self.target_duration,
            'tolerance_percent': self.tolerance_percent,
            'quality_gates_enabled': self.quality_gates_enabled,
            'checkpoints': [
                {
                    'stage': cp.stage,
                    'timestamp': cp.timestamp.isoformat(),
                    'target': cp.target_duration,
                    'actual': cp.actual_duration,
                    'component': cp.component,
                    'within_tolerance': cp.is_within_tolerance,
                    'warnings': cp.warnings,
                    'errors': cp.errors
                }
                for cp in self.checkpoints
            ],
            'summary': {
                'total_checkpoints': len(self.checkpoints),
                'passed_checkpoints': sum(1 for cp in self.checkpoints if cp.is_within_tolerance),
                'quality_score': self.get_feedback('summary').quality_score,
                'recommendations': self._generate_recommendations()
            }
        }