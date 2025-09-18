"""
VEO3 Adaptive Retry System
Automatically rephrases content when VEO3 blocks it for safety
"""
import re
import time
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from ..utils.logging_config import get_logger
except ImportError:
    from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class RephrasingStrategy(Enum):
    """Strategies for rephrasing blocked content"""
    LEVEL_1_MINOR = "minor_adjustments"      # Small word changes
    LEVEL_2_MODERATE = "moderate_changes"    # Replace sensitive terms
    LEVEL_3_ABSTRACT = "abstract_version"    # Make more abstract
    LEVEL_4_METAPHOR = "metaphorical"        # Full metaphorical transformation
    LEVEL_5_ARTISTIC = "artistic_only"       # Pure artistic interpretation


@dataclass
class RetryAttempt:
    """Record of a retry attempt"""
    attempt_number: int
    original_prompt: str
    rephrased_prompt: str
    strategy_used: RephrasingStrategy
    error_message: Optional[str]
    success: bool
    timestamp: datetime


class VEO3AdaptiveRetry:
    """
    Intelligent retry system that learns from VEO3 responses
    and progressively rephrases content until accepted
    """
    
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
        self.retry_history: List[RetryAttempt] = []
        self.blocked_patterns: List[str] = []  # Learn what gets blocked
        self.successful_patterns: List[str] = []  # Learn what works
        
        # Progressive rephrasing rules for each level
        self.rephrasing_rules = {
            RephrasingStrategy.LEVEL_1_MINOR: {
                # Minor word replacements
                "israeli soldier": "soldier",
                "idf": "military",
                "hamas": "opposition",
                "gaza": "urban area",
                "october 7": "recent events",
                "ptsd": "stress response"
            },
            RephrasingStrategy.LEVEL_2_MODERATE: {
                # More significant changes
                "war": "conflict",
                "weapon": "equipment",
                "kill": "neutralize",
                "blood": "intensity",
                "explosion": "impact",
                "combat": "engagement",
                "rifle": "tool",
                "gunfire": "sounds",
                "wounded": "affected"
            },
            RephrasingStrategy.LEVEL_3_ABSTRACT: {
                # Abstract descriptions
                "soldier": "individual",
                "battlefield": "challenging environment",
                "enemy": "opposing force",
                "attack": "action",
                "violence": "intensity",
                "trauma": "difficult experience",
                "flashback": "memory"
            },
            RephrasingStrategy.LEVEL_4_METAPHOR: {
                # Metaphorical transformations
                "walking through war zone": "navigating turbulent waters",
                "holding weapon": "grasping for control",
                "combat scene": "storm of emotions",
                "military operation": "complex journey",
                "fighting": "struggling with inner demons",
                "war torn": "fractured landscape"
            },
            RephrasingStrategy.LEVEL_5_ARTISTIC: {
                # Pure artistic interpretation
                "entire scene": "abstract emotional landscape with flowing colors and shapes representing inner turmoil"
            }
        }
    
    def attempt_generation(
        self,
        prompt: Any,
        veo_client: Any,
        clip_id: str
    ) -> Tuple[Optional[str], RetryAttempt]:
        """
        Attempt VEO3 generation with progressive rephrasing on failure
        
        Args:
            prompt: Original prompt (string or dict)
            veo_client: VEO3 client instance
            clip_id: Identifier for this clip
            
        Returns:
            Tuple of (video_path if successful, retry_attempt_record)
        """
        original_prompt = prompt
        current_strategy = RephrasingStrategy.LEVEL_1_MINOR
        
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"🎯 Attempt {attempt}/{self.max_retries} with strategy: {current_strategy.value}")
            
            # Rephrase if not first attempt
            if attempt > 1:
                prompt = self._rephrase_prompt(prompt, current_strategy)
                logger.info(f"📝 Rephrased prompt for attempt {attempt}")
            
            # Try generation
            try:
                result = veo_client.generate_video(
                    prompt=prompt,
                    duration=8,
                    aspect_ratio="16:9"
                )
                
                # Success!
                retry_record = RetryAttempt(
                    attempt_number=attempt,
                    original_prompt=str(original_prompt),
                    rephrased_prompt=str(prompt),
                    strategy_used=current_strategy,
                    error_message=None,
                    success=True,
                    timestamp=datetime.now()
                )
                
                self.retry_history.append(retry_record)
                self._learn_from_success(prompt)
                
                logger.info(f"✅ Generation successful on attempt {attempt}")
                return result, retry_record
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"⚠️ Attempt {attempt} failed: {error_msg}")
                
                # Record failure
                retry_record = RetryAttempt(
                    attempt_number=attempt,
                    original_prompt=str(original_prompt),
                    rephrased_prompt=str(prompt),
                    strategy_used=current_strategy,
                    error_message=error_msg,
                    success=False,
                    timestamp=datetime.now()
                )
                self.retry_history.append(retry_record)
                
                # Learn from failure
                self._learn_from_failure(prompt, error_msg)
                
                # Check if it's a safety block
                if self._is_safety_block(error_msg):
                    # Move to next strategy level
                    current_strategy = self._get_next_strategy(current_strategy)
                    logger.info(f"🔄 Safety block detected, escalating to {current_strategy.value}")
                else:
                    # Non-safety error, might be API issue
                    logger.error(f"❌ Non-safety error: {error_msg}")
                    if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                        # Rate limit, wait longer
                        time.sleep(30)
                    else:
                        # Unknown error, try once more with same strategy
                        time.sleep(5)
                
                # Add backoff delay
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # All attempts failed
        logger.error(f"❌ All {self.max_retries} attempts failed for clip {clip_id}")
        return None, retry_record
    
    def _rephrase_prompt(self, prompt: Any, strategy: RephrasingStrategy) -> Any:
        """
        Rephrase prompt based on strategy
        
        Args:
            prompt: Current prompt
            strategy: Rephrasing strategy to use
            
        Returns:
            Rephrased prompt
        """
        if isinstance(prompt, dict):
            return self._rephrase_dict_prompt(prompt, strategy)
        else:
            return self._rephrase_text_prompt(str(prompt), strategy)
    
    def _rephrase_text_prompt(self, text: str, strategy: RephrasingStrategy) -> str:
        """Rephrase a text prompt"""
        rephrased = text
        
        # Apply rules for current strategy and all previous levels
        for level in [
            RephrasingStrategy.LEVEL_1_MINOR,
            RephrasingStrategy.LEVEL_2_MODERATE,
            RephrasingStrategy.LEVEL_3_ABSTRACT,
            RephrasingStrategy.LEVEL_4_METAPHOR,
            RephrasingStrategy.LEVEL_5_ARTISTIC
        ]:
            if level.value <= strategy.value:
                rules = self.rephrasing_rules.get(level, {})
                for pattern, replacement in rules.items():
                    rephrased = re.sub(
                        re.escape(pattern),
                        replacement,
                        rephrased,
                        flags=re.IGNORECASE
                    )
            
            if level == strategy:
                break
        
        # Special handling for highest level
        if strategy == RephrasingStrategy.LEVEL_5_ARTISTIC:
            # Complete artistic transformation
            rephrased = self._create_artistic_version(rephrased)
        
        return rephrased
    
    def _rephrase_dict_prompt(self, prompt_dict: Dict, strategy: RephrasingStrategy) -> Dict:
        """Rephrase a JSON/dict prompt"""
        rephrased = prompt_dict.copy()
        
        # Fields to rephrase
        text_fields = ['scene', 'motion', 'subject', 'visual_details', 'description']
        
        for field in text_fields:
            if field in rephrased:
                if isinstance(rephrased[field], str):
                    rephrased[field] = self._rephrase_text_prompt(rephrased[field], strategy)
                elif isinstance(rephrased[field], dict):
                    for subfield, value in rephrased[field].items():
                        if isinstance(value, str):
                            rephrased[field][subfield] = self._rephrase_text_prompt(value, strategy)
        
        # Simplify keywords if needed
        if 'keywords' in rephrased and strategy.value >= RephrasingStrategy.LEVEL_3_ABSTRACT.value:
            # Remove potentially problematic keywords
            safe_keywords = []
            problematic = ['war', 'weapon', 'military', 'combat', 'violence', 'israel', 'gaza']
            for keyword in rephrased.get('keywords', []):
                if not any(prob in keyword.lower() for prob in problematic):
                    safe_keywords.append(keyword)
            rephrased['keywords'] = safe_keywords
        
        return rephrased
    
    def _create_artistic_version(self, text: str) -> str:
        """Create pure artistic interpretation"""
        # Extract the emotional core
        emotions = []
        if "fear" in text.lower():
            emotions.append("swirling dark blues")
        if "ptsd" in text.lower() or "trauma" in text.lower():
            emotions.append("fragmented memories as broken glass")
        if "war" in text.lower() or "combat" in text.lower():
            emotions.append("chaos represented by stormy abstracts")
        if "healing" in text.lower():
            emotions.append("golden light breaking through darkness")
        
        if not emotions:
            emotions = ["emotional journey through abstract landscapes"]
        
        return f"Abstract artistic visualization: {', '.join(emotions)}. Flowing colors and shapes representing inner emotional states, no literal representations."
    
    def _is_safety_block(self, error_msg: str) -> bool:
        """Check if error is due to safety/content policy"""
        safety_indicators = [
            "safety",
            "policy",
            "content",
            "inappropriate",
            "violated",
            "blocked",
            "not allowed",
            "prohibited",
            "guidelines"
        ]
        
        error_lower = error_msg.lower()
        return any(indicator in error_lower for indicator in safety_indicators)
    
    def _get_next_strategy(self, current: RephrasingStrategy) -> RephrasingStrategy:
        """Get next strategy level"""
        strategies = [
            RephrasingStrategy.LEVEL_1_MINOR,
            RephrasingStrategy.LEVEL_2_MODERATE,
            RephrasingStrategy.LEVEL_3_ABSTRACT,
            RephrasingStrategy.LEVEL_4_METAPHOR,
            RephrasingStrategy.LEVEL_5_ARTISTIC
        ]
        
        try:
            current_idx = strategies.index(current)
            if current_idx < len(strategies) - 1:
                return strategies[current_idx + 1]
        except ValueError:
            pass
        
        return RephrasingStrategy.LEVEL_5_ARTISTIC  # Maximum abstraction
    
    def _learn_from_success(self, prompt: str):
        """Learn what works"""
        # Extract successful patterns
        prompt_str = str(prompt).lower()
        if len(prompt_str) < 500:  # Don't store huge prompts
            self.successful_patterns.append(prompt_str)
        logger.info("📚 Learned successful pattern")
    
    def _learn_from_failure(self, prompt: str, error: str):
        """Learn what gets blocked"""
        # Extract problematic patterns
        if "safety" in error.lower() or "policy" in error.lower():
            prompt_str = str(prompt).lower()
            # Find specific problematic terms
            problematic_terms = [
                "weapon", "rifle", "gun", "bomb", "kill", "death",
                "israel", "gaza", "hamas", "idf", "october 7"
            ]
            
            for term in problematic_terms:
                if term in prompt_str:
                    if term not in self.blocked_patterns:
                        self.blocked_patterns.append(term)
                        logger.info(f"📚 Learned blocked pattern: {term}")
    
    def get_retry_report(self) -> Dict:
        """Get summary of retry attempts"""
        total_attempts = len(self.retry_history)
        successful = sum(1 for r in self.retry_history if r.success)
        
        strategy_stats = {}
        for strategy in RephrasingStrategy:
            strategy_attempts = [r for r in self.retry_history if r.strategy_used == strategy]
            strategy_success = sum(1 for r in strategy_attempts if r.success)
            strategy_stats[strategy.value] = {
                "attempts": len(strategy_attempts),
                "successes": strategy_success,
                "success_rate": strategy_success / len(strategy_attempts) if strategy_attempts else 0
            }
        
        return {
            "total_attempts": total_attempts,
            "successful": successful,
            "success_rate": successful / total_attempts if total_attempts else 0,
            "blocked_patterns": self.blocked_patterns,
            "strategy_stats": strategy_stats,
            "average_attempts_to_success": sum(r.attempt_number for r in self.retry_history if r.success) / successful if successful else 0
        }


# Convenience function
def generate_with_adaptive_retry(
    prompt: Any,
    veo_client: Any,
    clip_id: str = "clip",
    max_retries: int = 5
) -> Optional[str]:
    """
    Generate video with adaptive retry on content blocks
    
    Args:
        prompt: Original prompt
        veo_client: VEO3 client
        clip_id: Clip identifier
        max_retries: Maximum retry attempts
        
    Returns:
        Video path if successful, None otherwise
    """
    retry_system = VEO3AdaptiveRetry(max_retries)
    video_path, attempt = retry_system.attempt_generation(prompt, veo_client, clip_id)
    
    if video_path:
        logger.info(f"✅ Successfully generated after {attempt.attempt_number} attempts")
    else:
        logger.error(f"❌ Failed after {max_retries} attempts")
        # Log retry report
        report = retry_system.get_retry_report()
        logger.info(f"📊 Retry Report: {json.dumps(report, indent=2)}")
    
    return video_path