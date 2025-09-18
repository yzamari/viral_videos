"""
Prompt Optimization Service
Single Responsibility: Optimize and validate prompts for video generation
"""
import re
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

from .interfaces.base_interfaces import (
    IPromptOptimizer, 
    OptimizationRequest, 
    OptimizationResult,
    ICacheService,
    IMonitoringService,
    SystemEvent,
    EventType,
    IEventBus
)

try:
    from ..utils.logging_config import get_logger
except ImportError:
    from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class PromptOptimizationService(IPromptOptimizer):
    """
    Service responsible for prompt optimization
    Follows Single Responsibility Principle
    """
    
    def __init__(self, 
                 cache_service: ICacheService = None,
                 monitoring_service: IMonitoringService = None,
                 event_bus: IEventBus = None):
        """
        Initialize with injected dependencies
        
        Args:
            cache_service: Optional cache service
            monitoring_service: Optional monitoring service
            event_bus: Optional event bus
        """
        self.cache = cache_service
        self.monitoring = monitoring_service
        self.event_bus = event_bus
        
        # Configuration
        self.max_prompt_length = 500
        self.banned_terms = self._load_banned_terms()
        self.safe_keywords = ["cinematic", "professional", "4K", "artistic", "beautiful"]
        
        logger.info("✅ Prompt Optimization Service initialized")
    
    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        """
        Optimize a prompt according to request parameters
        
        Args:
            request: Optimization request
            
        Returns:
            Optimization result
        """
        start_time = datetime.now()
        
        # Check cache
        cache_key = self._generate_cache_key(request)
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self._record_metric("cache_hit", 1)
                return cached_result
        
        # Perform optimization
        optimized_prompt = self._apply_optimization(
            request.original_prompt,
            request.optimization_level
        )
        
        # Validate safety
        is_safe, issues = self.validate_safety(optimized_prompt)
        
        # Calculate success probability
        success_prob = self._calculate_success_probability(optimized_prompt, is_safe)
        
        # Create result
        result = OptimizationResult(
            optimized_prompt=optimized_prompt,
            modifications_applied=self._get_modifications(request.original_prompt, optimized_prompt),
            success_probability=success_prob
        )
        
        # Cache result
        if self.cache and is_safe:
            self.cache.set(cache_key, result, ttl=3600)
        
        # Record metrics
        self._record_metric("optimization_time", (datetime.now() - start_time).total_seconds())
        self._record_metric("optimization_success_prob", success_prob)
        
        # Publish event
        self._publish_event(EventType.OPTIMIZATION_APPLIED, {
            "original_length": len(str(request.original_prompt)),
            "optimized_length": len(optimized_prompt),
            "success_probability": success_prob,
            "is_safe": is_safe
        })
        
        return result
    
    def validate_safety(self, prompt: str) -> Tuple[bool, List[str]]:
        """
        Validate prompt safety
        
        Args:
            prompt: Prompt to validate
            
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        issues = []
        prompt_lower = prompt.lower()
        
        # Check for banned terms
        for term in self.banned_terms:
            if term in prompt_lower:
                issues.append(f"Contains banned term: {term}")
        
        # Check length
        if len(prompt) > self.max_prompt_length:
            issues.append(f"Too long: {len(prompt)} > {self.max_prompt_length}")
        
        # Check for suspicious patterns
        if re.search(r'\d{4}-\d{2}-\d{2}', prompt):
            issues.append("Contains date pattern")
        
        is_safe = len(issues) == 0
        
        # Record validation metrics
        self._record_metric("safety_validation", 1 if is_safe else 0)
        
        return is_safe, issues
    
    def _apply_optimization(self, prompt: Any, level: str) -> str:
        """Apply optimization based on level"""
        # Convert to string
        if isinstance(prompt, dict):
            prompt_str = self._dict_to_text(prompt)
        else:
            prompt_str = str(prompt)
        
        # Apply level-specific optimization
        if level == "minimal":
            return self._minimal_optimization(prompt_str)
        elif level == "moderate":
            return self._moderate_optimization(prompt_str)
        elif level == "aggressive":
            return self._aggressive_optimization(prompt_str)
        else:
            return self._extreme_optimization(prompt_str)
    
    def _minimal_optimization(self, text: str) -> str:
        """Minimal optimization - remove banned terms only"""
        for term in self.banned_terms:
            text = re.sub(r'\b' + re.escape(term) + r'\b', '', text, flags=re.IGNORECASE)
        return self._clean_text(text)
    
    def _moderate_optimization(self, text: str) -> str:
        """Moderate optimization - simplify and clean"""
        text = self._minimal_optimization(text)
        # Remove complex descriptions
        text = re.sub(r'\([^)]+\)', '', text)  # Remove parentheses
        text = re.sub(r'"[^"]+"', '', text)  # Remove quotes
        return self._truncate(text, 500)
    
    def _aggressive_optimization(self, text: str) -> str:
        """Aggressive optimization - keep essentials only"""
        text = self._moderate_optimization(text)
        # Keep only first 3 sentences
        sentences = text.split('.')[:3]
        text = '. '.join(sentences)
        return self._truncate(text, 300)
    
    def _extreme_optimization(self, text: str) -> str:
        """Extreme optimization - bare minimum"""
        # Extract key visual elements
        keywords = []
        if "scene" in text.lower():
            keywords.append("scenic view")
        if "person" in text.lower():
            keywords.append("person")
        keywords.extend(self.safe_keywords[:3])
        return " ".join(keywords)
    
    def _dict_to_text(self, prompt_dict: Dict[str, Any]) -> str:
        """Convert dictionary prompt to text"""
        parts = []
        for key in ['scene', 'subject', 'style']:
            if key in prompt_dict:
                value = prompt_dict[key]
                if isinstance(value, dict):
                    parts.append(value.get('description', ''))
                else:
                    parts.append(str(value))
        return ". ".join(filter(None, parts))
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = ' '.join(text.split())  # Normalize whitespace
        text = re.sub(r'[^\w\s.,!?-]', '', text)  # Remove special chars
        return text.strip()
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text
    
    def _calculate_success_probability(self, prompt: str, is_safe: bool) -> float:
        """Calculate probability of successful generation"""
        if not is_safe:
            return 0.1
        
        score = 0.9
        
        # Length penalty
        if len(prompt) > 400:
            score -= 0.2
        elif len(prompt) > 300:
            score -= 0.1
        
        # Bonus for safe keywords
        for keyword in self.safe_keywords:
            if keyword in prompt.lower():
                score += 0.02
        
        return min(1.0, max(0.1, score))
    
    def _get_modifications(self, original: Any, optimized: str) -> List[str]:
        """Get list of modifications applied"""
        modifications = []
        original_str = str(original)
        
        if len(optimized) < len(original_str) * 0.5:
            modifications.append("significant_reduction")
        
        if not any(term in optimized.lower() for term in self.banned_terms):
            modifications.append("banned_terms_removed")
        
        if len(optimized) <= self.max_prompt_length:
            modifications.append("length_optimized")
        
        return modifications
    
    def _generate_cache_key(self, request: OptimizationRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.original_prompt}_{request.optimization_level}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _load_banned_terms(self) -> List[str]:
        """Load list of banned terms"""
        return [
            "war", "soldier", "military", "weapon", "combat", "violence",
            "blood", "explosion", "terrorist", "ptsd", "trauma",
            "israel", "palestinian", "lebanon", "gaza", "october"
        ]
    
    def _record_metric(self, name: str, value: Any):
        """Record metric if monitoring service available"""
        if self.monitoring:
            self.monitoring.record_metric(f"prompt_optimization.{name}", value)
    
    def _publish_event(self, event_type: EventType, data: Dict[str, Any]):
        """Publish event if event bus available"""
        if self.event_bus:
            event = SystemEvent(
                event_type=event_type,
                timestamp=datetime.now().isoformat(),
                service="PromptOptimizationService",
                data=data
            )
            self.event_bus.publish(event)