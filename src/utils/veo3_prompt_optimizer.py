"""
VEO3 Prompt Optimizer
Aggressively simplifies prompts to maximize generation success
"""
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from ..utils.logging_config import get_logger
except ImportError:
    from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class OptimizationLevel(Enum):
    """Levels of prompt optimization"""
    MINIMAL = "minimal"      # Light touch, preserve most content
    MODERATE = "moderate"    # Balance between detail and safety
    AGGRESSIVE = "aggressive"  # Maximum simplification for safety
    EXTREME = "extreme"      # Bare minimum for generation


@dataclass 
class OptimizationResult:
    """Result of prompt optimization"""
    original_prompt: Any
    optimized_prompt: str
    optimization_level: OptimizationLevel
    original_length: int
    optimized_length: int
    removed_elements: List[str]
    success_probability: float


class VEO3PromptOptimizer:
    """Optimizes prompts for maximum VEO3 success rate"""
    
    # Maximum lengths per optimization level
    MAX_LENGTHS = {
        OptimizationLevel.MINIMAL: 800,
        OptimizationLevel.MODERATE: 500,
        OptimizationLevel.AGGRESSIVE: 300,
        OptimizationLevel.EXTREME: 150
    }
    
    # Essential keywords only (avoid triggering safety)
    SAFE_KEYWORDS = [
        "cinematic", "professional", "4K", "smooth", "artistic",
        "beautiful", "elegant", "modern", "creative", "dynamic"
    ]
    
    # Words to always remove (high risk of safety blocks)
    BANNED_WORDS = [
        # Violence/conflict
        "war", "soldier", "military", "weapon", "gun", "rifle", "combat",
        "fight", "battle", "attack", "conflict", "violence", "blood",
        "explosion", "bomb", "terrorist", "enemy", "kill", "death",
        
        # Specific conflicts/politics
        "israel", "palestinian", "lebanon", "gaza", "hamas", "hezbollah",
        "idf", "october", "iran", "syria", "ukraine", "russia",
        
        # Mental health (when combined with violence)
        "ptsd", "trauma", "suicide", "depression", "anxiety",
        
        # Other sensitive
        "political", "religious", "controversial", "sensitive"
    ]
    
    def __init__(self):
        """Initialize the optimizer"""
        logger.info("🚀 VEO3 Prompt Optimizer initialized")
        self.optimization_cache = {}
    
    def optimize_prompt(self, 
                       prompt: Any,
                       target_level: OptimizationLevel = OptimizationLevel.MODERATE,
                       max_retries: int = 3) -> OptimizationResult:
        """
        Optimize a prompt for VEO3 generation
        
        Args:
            prompt: Original prompt (string or dict)
            target_level: Target optimization level
            max_retries: Max attempts if prompt still too complex
            
        Returns:
            OptimizationResult with simplified prompt
        """
        # Convert to string if needed
        if isinstance(prompt, dict):
            prompt_str = self._dict_to_simple_text(prompt)
        else:
            prompt_str = str(prompt)
        
        original_length = len(prompt_str)
        
        # Check cache
        cache_key = f"{prompt_str[:50]}_{target_level.value}"
        if cache_key in self.optimization_cache:
            logger.info("📦 Using cached optimization")
            return self.optimization_cache[cache_key]
        
        # Progressive optimization
        optimized = prompt_str
        removed_elements = []
        current_level = OptimizationLevel.MINIMAL
        
        while len(optimized) > self.MAX_LENGTHS[target_level] and max_retries > 0:
            optimized, removed = self._apply_optimization_level(optimized, current_level)
            removed_elements.extend(removed)
            
            # Escalate if still too long
            if len(optimized) > self.MAX_LENGTHS[target_level]:
                levels = list(OptimizationLevel)
                current_idx = levels.index(current_level)
                if current_idx < len(levels) - 1:
                    current_level = levels[current_idx + 1]
                    logger.info(f"📈 Escalating to {current_level.value} optimization")
            
            max_retries -= 1
        
        # Final safety pass
        optimized = self._final_safety_pass(optimized)
        
        # Calculate success probability
        success_prob = self._estimate_success_probability(optimized)
        
        result = OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=optimized,
            optimization_level=current_level,
            original_length=original_length,
            optimized_length=len(optimized),
            removed_elements=removed_elements,
            success_probability=success_prob
        )
        
        # Cache result
        self.optimization_cache[cache_key] = result
        
        logger.info(f"✅ Optimized: {original_length} → {len(optimized)} chars")
        logger.info(f"📊 Success probability: {success_prob:.1%}")
        
        return result
    
    def _dict_to_simple_text(self, prompt_dict: Dict[str, Any]) -> str:
        """Convert dict prompt to simple text"""
        parts = []
        
        # Extract only essential elements
        if 'scene' in prompt_dict:
            if isinstance(prompt_dict['scene'], dict):
                parts.append(prompt_dict['scene'].get('description', ''))
            else:
                parts.append(str(prompt_dict['scene']))
        
        if 'subject' in prompt_dict:
            if isinstance(prompt_dict['subject'], dict):
                parts.append(prompt_dict['subject'].get('description', ''))
            else:
                parts.append(str(prompt_dict['subject']))
        
        if 'style' in prompt_dict:
            if isinstance(prompt_dict['style'], dict):
                parts.append(prompt_dict['style'].get('visual_aesthetic', ''))
            else:
                parts.append(str(prompt_dict['style']))
        
        # Add safe keywords
        if 'keywords' in prompt_dict and isinstance(prompt_dict['keywords'], list):
            safe_kw = [k for k in prompt_dict['keywords'][:5] 
                      if not any(b in k.lower() for b in self.BANNED_WORDS)]
            parts.extend(safe_kw)
        
        return ". ".join(filter(None, parts))
    
    def _apply_optimization_level(self, 
                                 text: str,
                                 level: OptimizationLevel) -> Tuple[str, List[str]]:
        """Apply specific optimization level"""
        removed = []
        
        if level == OptimizationLevel.MINIMAL:
            # Remove banned words only
            for word in self.BANNED_WORDS:
                pattern = r'\b' + re.escape(word) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                    removed.append(f"banned:{word}")
        
        elif level == OptimizationLevel.MODERATE:
            # Remove banned words and simplify descriptions
            text = self._remove_banned_words(text)
            text = self._simplify_descriptions(text)
            removed.append("complex_descriptions")
        
        elif level == OptimizationLevel.AGGRESSIVE:
            # Keep only essential elements
            text = self._extract_essential_only(text)
            removed.append("non_essential_details")
        
        elif level == OptimizationLevel.EXTREME:
            # Bare minimum
            text = self._create_minimal_prompt(text)
            removed.append("all_details")
        
        # Clean up extra spaces
        text = ' '.join(text.split())
        
        return text, removed
    
    def _remove_banned_words(self, text: str) -> str:
        """Remove all banned words"""
        for word in self.BANNED_WORDS:
            pattern = r'\b' + re.escape(word) + r's?\b'  # Handle plurals
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def _simplify_descriptions(self, text: str) -> str:
        """Simplify complex descriptions"""
        # Remove parenthetical explanations
        text = re.sub(r'\([^)]+\)', '', text)
        
        # Remove quoted text
        text = re.sub(r'"[^"]+"', '', text)
        text = re.sub(r"'[^']+'", '', text)
        
        # Simplify punctuation
        text = re.sub(r'[;:]', '.', text)
        text = re.sub(r'\.+', '.', text)
        
        # Remove very long words (likely technical terms)
        words = text.split()
        words = [w for w in words if len(w) <= 15]
        text = ' '.join(words)
        
        return text
    
    def _extract_essential_only(self, text: str) -> str:
        """Extract only essential elements"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Keep only short, simple sentences
        essential = []
        for sent in sentences[:3]:  # Max 3 sentences
            if len(sent) < 100:
                # Clean the sentence
                sent = self._remove_banned_words(sent)
                if sent.strip():
                    essential.append(sent.strip())
        
        return '. '.join(essential)
    
    def _create_minimal_prompt(self, text: str) -> str:
        """Create minimal viable prompt"""
        # Extract key visual elements
        visuals = []
        
        # Look for scene/setting
        if "scene" in text.lower() or "setting" in text.lower():
            visuals.append("scenic view")
        
        # Look for character/person
        if any(word in text.lower() for word in ["person", "character", "people"]):
            visuals.append("person walking")
        
        # Look for style
        if "cinematic" in text.lower():
            visuals.append("cinematic style")
        elif "animation" in text.lower():
            visuals.append("animated style")
        else:
            visuals.append("professional video")
        
        # Add safe keywords
        visuals.extend(self.SAFE_KEYWORDS[:3])
        
        return " ".join(visuals)
    
    def _final_safety_pass(self, text: str) -> str:
        """Final safety cleanup"""
        # Remove any remaining sensitive patterns
        text = re.sub(r'\d{4}-\d{2}-\d{2}', 'recent', text)  # Dates
        text = re.sub(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+', 'recently', text)
        text = re.sub(r'\b\d{4}\b', 'recent year', text)  # Years
        
        # Ensure no double spaces or weird characters
        text = ' '.join(text.split())
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Truncate if still too long
        max_len = 500
        if len(text) > max_len:
            text = text[:max_len-3] + "..."
        
        return text.strip()
    
    def _estimate_success_probability(self, text: str) -> float:
        """Estimate probability of successful generation"""
        score = 1.0
        
        # Length penalty
        if len(text) > 500:
            score -= 0.3
        elif len(text) > 300:
            score -= 0.1
        
        # Check for remaining banned words
        text_lower = text.lower()
        for word in self.BANNED_WORDS:
            if word in text_lower:
                score -= 0.2
        
        # Bonus for safe keywords
        for keyword in self.SAFE_KEYWORDS:
            if keyword in text_lower:
                score += 0.05
        
        # Ensure valid range
        return max(0.1, min(1.0, score))
    
    def create_safe_prompt(self, 
                          scene_description: str,
                          style: str = "cinematic",
                          duration: int = 8) -> str:
        """
        Create a safe, minimal prompt from scratch
        
        Args:
            scene_description: What to show
            style: Visual style
            duration: Duration in seconds
            
        Returns:
            Safe prompt string
        """
        # Clean the description
        clean_desc = self._remove_banned_words(scene_description)
        clean_desc = self._simplify_descriptions(clean_desc)
        
        # Build safe prompt
        parts = [
            clean_desc[:100],  # Limit description
            f"{style} style",
            "professional quality",
            "4K resolution"
        ]
        
        # Add a few safe keywords
        parts.extend(self.SAFE_KEYWORDS[:3])
        
        prompt = ". ".join(parts)
        
        # Final safety
        prompt = self._final_safety_pass(prompt)
        
        logger.info(f"✅ Created safe prompt: {len(prompt)} chars")
        return prompt


class ProgressiveSimplifier:
    """Progressively simplifies prompts after failures"""
    
    def __init__(self):
        self.optimizer = VEO3PromptOptimizer()
        self.failure_count = {}
    
    def get_simplified_prompt(self, 
                            original_prompt: Any,
                            clip_id: str) -> str:
        """
        Get progressively simpler prompt based on failure count
        
        Args:
            original_prompt: Original prompt
            clip_id: Clip identifier for tracking failures
            
        Returns:
            Simplified prompt string
        """
        # Track failures
        failures = self.failure_count.get(clip_id, 0)
        
        # Determine optimization level based on failures
        if failures == 0:
            level = OptimizationLevel.MINIMAL
        elif failures == 1:
            level = OptimizationLevel.MODERATE
        elif failures == 2:
            level = OptimizationLevel.AGGRESSIVE
        else:
            level = OptimizationLevel.EXTREME
        
        logger.info(f"🔄 Attempt {failures + 1} for {clip_id}, using {level.value} optimization")
        
        # Optimize
        result = self.optimizer.optimize_prompt(original_prompt, level)
        
        # Track this attempt
        self.failure_count[clip_id] = failures + 1
        
        return result.optimized_prompt
    
    def reset_clip(self, clip_id: str):
        """Reset failure count for a clip"""
        self.failure_count.pop(clip_id, None)


# Global instance for easy access
prompt_optimizer = VEO3PromptOptimizer()
progressive_simplifier = ProgressiveSimplifier()