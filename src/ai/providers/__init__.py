"""AI Provider implementations and registration."""

# Import all provider implementations
from .gemini_image_generation import GeminiImageGenerationService
from .vertex_imagen_generation import VertexImagenGenerationService
from .google_tts_service import GoogleTTSService
from .veo_video_generation import VEOVideoGenerationService

# Import existing text generation provider
from .gemini.text_generation import GeminiTextService


def register_all_providers():
    """Register all available AI providers with the factory.
    
    This should be called after the factory is fully initialized to avoid circular imports.
    """
    from src.ai.factory import AIServiceFactory, AIServiceType
    from src.ai.interfaces.base import AIProvider
    
    # Text Generation Providers (already registered in factory.py)
    # Skipping to avoid duplicate registration
    
    # Image Generation Providers
    AIServiceFactory.register(AIServiceType.IMAGE_GENERATION, AIProvider.GEMINI, GeminiImageGenerationService)
    AIServiceFactory.register(AIServiceType.IMAGE_GENERATION, AIProvider.VERTEX, VertexImagenGenerationService)
    
    # Speech Synthesis Providers
    AIServiceFactory.register(AIServiceType.SPEECH_SYNTHESIS, AIProvider.GOOGLE, GoogleTTSService)
    
    # Video Generation Providers
    AIServiceFactory.register(AIServiceType.VIDEO_GENERATION, AIProvider.GEMINI, VEOVideoGenerationService)  # VEO is under Google/Gemini