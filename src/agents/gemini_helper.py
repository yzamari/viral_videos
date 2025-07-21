"""
Gemini Helper for Agents
Provides consistent Gemini model initialization for all agents
"""
import google.generativeai as genai
from typing import Optional
from ..ai.manager import AIServiceManager
from ..ai.config import AIConfiguration, AIProvider
from ..ai.factory import AIServiceType
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class GeminiModelHelper:
    """Helper class for consistent Gemini model initialization"""
    
    @staticmethod
    def get_configured_model(api_key: str, model_name: str = "gemini-2.5-flash") -> genai.GenerativeModel:
        """
        Get a configured Gemini model with proper API key handling
        
        Args:
            api_key: The API key to use
            model_name: The model name (default: gemini-2.5-flash)
            
        Returns:
            Configured GenerativeModel instance
        """
        if not api_key:
            raise ValueError("API key is required for Gemini model")
        
        # Configure genai with the API key
        genai.configure(api_key=api_key)
        
        # Create and return the model
        model = genai.GenerativeModel(model_name)
        logger.debug(f"✅ Gemini model {model_name} configured with API key")
        
        return model
    
    @staticmethod
    def get_ai_service_manager(api_key: str) -> AIServiceManager:
        """
        Get a properly configured AIServiceManager
        
        Args:
            api_key: The API key to use
            
        Returns:
            Configured AIServiceManager instance
        """
        if not api_key:
            raise ValueError("API key is required for AI Service Manager")
        
        # Create AI configuration with the provided API key
        config = AIConfiguration()
        config.api_keys[AIProvider.GEMINI] = api_key
        config.default_providers[AIServiceType.TEXT_GENERATION] = AIProvider.GEMINI
        
        # Create and return the manager
        ai_manager = AIServiceManager(config)
        logger.debug("✅ AI Service Manager configured with API key")
        
        return ai_manager


def ensure_api_key(api_key: Optional[str]) -> str:
    """
    Ensure API key is valid, loading from environment if needed
    
    Args:
        api_key: The API key or None
        
    Returns:
        Valid API key
        
    Raises:
        ValueError: If no API key is available
    """
    if api_key and api_key.strip():
        return api_key
    
    # Try to load from environment
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    env_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip():
        logger.debug("✅ API key loaded from environment")
        return env_key
    
    raise ValueError("No API key provided and none found in environment")