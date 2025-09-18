"""
VEO3 Retry System with Exponential Backoff
Handles VEO3 failures gracefully with smart retries
"""
import time
import random
from typing import Any, Callable, Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

try:
    from ..utils.logging_config import get_logger
    from .veo3_prompt_optimizer import progressive_simplifier
except ImportError:
    from src.utils.logging_config import get_logger
    from src.utils.veo3_prompt_optimizer import progressive_simplifier

logger = get_logger(__name__)


class FailureType(Enum):
    """Types of VEO3 failures"""
    SAFETY_BLOCK = "safety_block"
    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    INVALID_PROMPT = "invalid_prompt"
    UNKNOWN = "unknown"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 2.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    progressive_simplification: bool = True


@dataclass
class RetryResult:
    """Result of retry operation"""
    success: bool
    result: Any
    attempts: int
    total_time: float
    failure_types: list
    final_prompt: str


class VEO3RetrySystem:
    """Smart retry system for VEO3 generation"""
    
    def __init__(self, config: RetryConfig = None):
        """Initialize retry system"""
        self.config = config or RetryConfig()
        self.failure_history = {}
        self.success_cache = {}
        
        logger.info(f"🔄 VEO3 Retry System initialized")
        logger.info(f"   Max attempts: {self.config.max_attempts}")
        logger.info(f"   Progressive simplification: {self.config.progressive_simplification}")
    
    def retry_with_backoff(self,
                          func: Callable,
                          clip_id: str,
                          original_prompt: Any,
                          *args,
                          **kwargs) -> RetryResult:
        """
        Retry VEO3 generation with exponential backoff
        
        Args:
            func: VEO3 generation function to retry
            clip_id: Clip identifier
            original_prompt: Original prompt
            *args: Additional args for func
            **kwargs: Additional kwargs for func
            
        Returns:
            RetryResult with outcome
        """
        start_time = time.time()
        attempts = 0
        failure_types = []
        current_prompt = original_prompt
        
        # Check success cache
        cache_key = f"{clip_id}_{str(original_prompt)[:50]}"
        if cache_key in self.success_cache:
            logger.info(f"✅ Using cached successful prompt for {clip_id}")
            cached = self.success_cache[cache_key]
            return RetryResult(
                success=True,
                result=cached['result'],
                attempts=0,
                total_time=0,
                failure_types=[],
                final_prompt=cached['prompt']
            )
        
        while attempts < self.config.max_attempts:
            attempts += 1
            logger.info(f"🎯 Attempt {attempts}/{self.config.max_attempts} for {clip_id}")
            
            try:
                # Progressive simplification if enabled
                if self.config.progressive_simplification and attempts > 1:
                    current_prompt = progressive_simplifier.get_simplified_prompt(
                        original_prompt, clip_id
                    )
                    logger.info(f"📝 Using simplified prompt for attempt {attempts}")
                
                # Update kwargs with current prompt
                kwargs['prompt'] = current_prompt
                
                # Try generation
                result = func(*args, **kwargs)
                
                if result:
                    # Success! Cache it
                    self.success_cache[cache_key] = {
                        'result': result,
                        'prompt': current_prompt
                    }
                    
                    # Reset failure tracking
                    progressive_simplifier.reset_clip(clip_id)
                    
                    logger.info(f"✅ Success on attempt {attempts} for {clip_id}")
                    return RetryResult(
                        success=True,
                        result=result,
                        attempts=attempts,
                        total_time=time.time() - start_time,
                        failure_types=failure_types,
                        final_prompt=current_prompt
                    )
                else:
                    failure_type = FailureType.UNKNOWN
                    failure_types.append(failure_type)
                    logger.warning(f"⚠️ Attempt {attempts} returned None")
                    
            except Exception as e:
                # Classify failure
                failure_type = self._classify_failure(str(e))
                failure_types.append(failure_type)
                
                logger.warning(f"❌ Attempt {attempts} failed: {failure_type.value}")
                logger.debug(f"   Error: {str(e)}")
                
                # Check if we should retry this type of failure
                if not self._should_retry(failure_type, attempts):
                    logger.error(f"🛑 Not retrying {failure_type.value} failures")
                    break
            
            # Calculate backoff delay
            if attempts < self.config.max_attempts:
                delay = self._calculate_backoff(attempts)
                logger.info(f"⏰ Waiting {delay:.1f}s before retry...")
                time.sleep(delay)
        
        # All attempts failed
        logger.error(f"❌ All {attempts} attempts failed for {clip_id}")
        return RetryResult(
            success=False,
            result=None,
            attempts=attempts,
            total_time=time.time() - start_time,
            failure_types=failure_types,
            final_prompt=current_prompt
        )
    
    def _classify_failure(self, error_message: str) -> FailureType:
        """Classify the type of failure"""
        error_lower = error_message.lower()
        
        if any(word in error_lower for word in ['safety', 'guidelines', 'violated', 'blocked']):
            return FailureType.SAFETY_BLOCK
        elif 'timeout' in error_lower or 'timed out' in error_lower:
            return FailureType.TIMEOUT
        elif 'quota' in error_lower or 'limit' in error_lower:
            return FailureType.QUOTA_EXCEEDED
        elif 'invalid' in error_lower or 'malformed' in error_lower:
            return FailureType.INVALID_PROMPT
        elif 'api' in error_lower or 'connection' in error_lower:
            return FailureType.API_ERROR
        else:
            return FailureType.UNKNOWN
    
    def _should_retry(self, failure_type: FailureType, attempt: int) -> bool:
        """Determine if we should retry based on failure type"""
        # Always retry safety blocks with simplification
        if failure_type == FailureType.SAFETY_BLOCK:
            return self.config.progressive_simplification
        
        # Don't retry quota exceeded
        if failure_type == FailureType.QUOTA_EXCEEDED:
            return False
        
        # Retry timeouts up to 2 times
        if failure_type == FailureType.TIMEOUT:
            return attempt <= 2
        
        # Retry API errors
        if failure_type == FailureType.API_ERROR:
            return True
        
        # Default: retry
        return True
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        # Exponential backoff
        delay = min(
            self.config.initial_delay * (self.config.exponential_base ** (attempt - 1)),
            self.config.max_delay
        )
        
        # Add jitter if enabled
        if self.config.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay
    
    def get_failure_stats(self, clip_id: str = None) -> Dict[str, Any]:
        """Get failure statistics"""
        if clip_id:
            return self.failure_history.get(clip_id, {})
        
        # Overall stats
        total_clips = len(self.failure_history)
        total_failures = sum(len(h.get('failures', [])) for h in self.failure_history.values())
        
        failure_by_type = {}
        for history in self.failure_history.values():
            for failure in history.get('failures', []):
                failure_type = failure.get('type', 'unknown')
                failure_by_type[failure_type] = failure_by_type.get(failure_type, 0) + 1
        
        return {
            'total_clips_with_failures': total_clips,
            'total_failures': total_failures,
            'failure_by_type': failure_by_type,
            'cache_size': len(self.success_cache)
        }


class SmartVEO3Manager:
    """Smart manager combining retry and optimization"""
    
    def __init__(self):
        self.retry_system = VEO3RetrySystem()
        self.generation_history = []
    
    def generate_with_fallback(self,
                              veo3_client: Any,
                              prompt: Any,
                              clip_id: str,
                              duration: float = 8,
                              **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate video with smart fallback
        
        Args:
            veo3_client: VEO3 client instance
            prompt: Original prompt
            clip_id: Clip identifier  
            duration: Video duration
            **kwargs: Additional generation parameters
            
        Returns:
            Tuple of (video_path, metadata)
        """
        logger.info(f"🎬 Smart VEO3 generation for {clip_id}")
        
        # Try with retry system
        result = self.retry_system.retry_with_backoff(
            veo3_client.generate_video,
            clip_id,
            prompt,
            prompt=prompt,
            duration=duration,
            clip_id=clip_id,
            **kwargs
        )
        
        # Track in history
        self.generation_history.append({
            'clip_id': clip_id,
            'timestamp': datetime.now(),
            'success': result.success,
            'attempts': result.attempts,
            'time': result.total_time,
            'final_prompt': result.final_prompt[:100] if result.final_prompt else None
        })
        
        if result.success:
            metadata = {
                'attempts': result.attempts,
                'generation_time': result.total_time,
                'prompt_modified': result.final_prompt != prompt,
                'optimization_applied': result.attempts > 1
            }
            return result.result, metadata
        else:
            # Ultimate fallback
            logger.warning(f"⚠️ Using fallback video for {clip_id}")
            fallback_path = self._create_fallback_video(clip_id, duration)
            metadata = {
                'is_fallback': True,
                'attempts': result.attempts,
                'failure_types': [f.value for f in result.failure_types]
            }
            return fallback_path, metadata
    
    def _create_fallback_video(self, clip_id: str, duration: float) -> str:
        """Create a fallback video when all else fails"""
        # This would create a simple placeholder video
        logger.info(f"🎨 Creating fallback video for {clip_id}")
        # In production, this would generate a simple video
        return f"fallback_{clip_id}.mp4"
    
    def get_generation_report(self) -> Dict[str, Any]:
        """Get generation statistics report"""
        if not self.generation_history:
            return {'message': 'No generations yet'}
        
        total = len(self.generation_history)
        successful = sum(1 for g in self.generation_history if g['success'])
        
        avg_attempts = sum(g['attempts'] for g in self.generation_history) / total
        avg_time = sum(g['time'] for g in self.generation_history) / total
        
        return {
            'total_generations': total,
            'successful': successful,
            'success_rate': successful / total,
            'average_attempts': avg_attempts,
            'average_time': avg_time,
            'retry_stats': self.retry_system.get_failure_stats()
        }


# Global instance
smart_veo3_manager = SmartVEO3Manager()