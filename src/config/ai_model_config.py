"""
AI Model Configuration
Centralized configuration for AI model names used across the system
"""

# Default AI model for all agents and components
# Using gemini-2.5-flash for fast performance with JSON mode support
DEFAULT_AI_MODEL = "gemini-2.5-flash"

# Legacy models (kept for reference)
LEGACY_MODELS = {
    "standard": "gemini-2.5-flash",
    "pro": "gemini-2.5-pro", 
    "fast": "gemini-1.5-flash",
    "image": "gemini-2.0-flash-preview-image-generation"
}

# Model-specific configurations
MODEL_CONFIGS = {
    "gemini-2.5-flash-lite": {
        "max_tokens": 8192,
        "temperature": 0.7,
        "description": "Ultra-fast lightweight model for rapid AI agent responses"
    },
    "gemini-2.5-flash": {
        "max_tokens": 32768,
        "temperature": 0.7,
        "description": "Standard fast model with good balance of speed and quality"
    },
    "gemini-2.5-pro": {
        "max_tokens": 32768,
        "temperature": 0.7,
        "description": "High-quality model for complex tasks"
    }
}