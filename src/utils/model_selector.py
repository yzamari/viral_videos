"""
Intelligent Gemini Model Selection with Quota-Aware Fallbacks
Automatically selects the best available model based on quota limits
"""
import os
import time
from typing import Optional, List, Dict, Any
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class ModelSelector:
    """
    Smart model selector that handles quota limits and fallbacks
    """

    # Model hierarchy: gemini-2.5-flash as primary
    MODELS = [
        'gemini-2.5-flash',           # Primary model - latest with excellent performance
    ]

    # Quota limits per model (requests per minute)
    QUOTA_LIMITS = {
        'gemini-2.5-flash': 100,     # Primary model quota
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.usage_tracker = {}
        self.last_reset = time.time()

    def get_best_model(self, task_type: str = 'general') -> str:
        """
        Get the best available model for the task type

        Args:
            task_type: Type of task ('prompt_generation', 'text_processing', 'general')

        Returns:
            Model name to use
        """
        current_time = time.time()

        # Reset usage tracker every minute
        if current_time - self.last_reset > 60:
            self.usage_tracker = {}
            self.last_reset = current_time

        # Check each model in order of preference
        for model in self.MODELS:
            usage = self.usage_tracker.get(model, 0)
            limit = self.QUOTA_LIMITS.get(model, 10)

            if usage < limit * 0.8:  # Use 80% of quota as safety margin
                logger.info(
                    f"🤖 Selected model: {model} (usage: {usage}/{limit})")
                return model

        # If all models are at limit, use the highest quota model anyway
        fallback_model = self.MODELS[0]
        logger.warning(
            f"⚠️ All models at quota limit, using fallback: {fallback_model}")
        return fallback_model

    def record_usage(self, model: str):
        """Record usage of a model"""
        self.usage_tracker[model] = self.usage_tracker.get(model, 0) + 1

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        stats = {}
        for model in self.MODELS:
            usage = self.usage_tracker.get(model, 0)
            limit = self.QUOTA_LIMITS.get(model, 10)
            stats[model] = {
                'usage': usage,
                'limit': limit,
                'percentage': (usage / limit) * 100 if limit > 0 else 0
            }
        return stats

    def get_fallback_model(self) -> str:
        """Get safe fallback model when quota is exhausted"""
        return 'gemini-2.5-flash'  # Use primary model

# Global model selector instance
_model_selector = None

def get_model_selector() -> ModelSelector:
    """Get or create global model selector"""
    global _model_selector
    if _model_selector is None:
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("No API key found for model selector")
        _model_selector = ModelSelector(api_key)
    return _model_selector

def get_best_gemini_model(task_type: str = 'general') -> str:
    """
    Convenience function to get the best available Gemini model

    Args:
        task_type: Type of task ('prompt_generation', 'text_processing', 'general')

    Returns:
        Model name to use
    """
    try:
        selector = get_model_selector()
        model = selector.get_best_model(task_type)
        selector.record_usage(model)
        return model
    except Exception as e:
        logger.error(f"❌ Model selection failed: {e}")
        return 'gemini-2.5-flash'  # Safe fallback

def log_quota_usage():
    """Log current quota usage across all models"""
    try:
        selector = get_model_selector()
        stats = selector.get_usage_stats()

        logger.info("📊 Current Gemini Model Usage:")
        for model, data in stats.items():
            percentage = data['percentage']
            emoji = "🟢" if percentage < 50 else "🟡" if percentage < 80 else "🔴"
            logger.info(
                f"   {emoji} {model}: {data['usage']}/{data['limit']} ({percentage:.1f}%)")

    except Exception as e:
        logger.error(f"❌ Failed to log quota usage: {e}")
