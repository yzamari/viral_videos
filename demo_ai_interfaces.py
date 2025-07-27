#!/usr/bin/env python3
"""
Demo: How to Use the Universal AI Provider Interface System

This demonstrates the proper way to use AI services through interfaces.
"""

import asyncio
import os
from src.ai.manager import AIServiceManager
from src.ai.config import AIConfiguration
from src.ai.interfaces.base import AIServiceType, AIProvider
from src.ai.interfaces.image_generation import ImageGenerationRequest
from src.ai.interfaces.speech_synthesis import SpeechSynthesisRequest
from src.ai.interfaces.text_generation import TextGenerationRequest

# Initialize providers after imports
from src.ai.factory import AIServiceFactory
AIServiceFactory.initialize_providers()


async def main():
    """Demonstrate proper AI service usage through interfaces"""
    
    print("🚀 Universal AI Provider Interface Demo")
    print("=" * 50)
    
    # 1. Create configuration (loads from environment)
    config = AIConfiguration.create_default()
    
    # 2. Create service manager
    manager = AIServiceManager(config)
    
    # Example 1: Text Generation (already working)
    print("\n📝 Text Generation Example:")
    text_service = manager.get_service(AIServiceType.TEXT_GENERATION)
    
    text_request = TextGenerationRequest(
        prompt="Write a haiku about robots",
        max_tokens=100,
        temperature=0.7
    )
    
    text_response = await text_service.generate(text_request)
    print(f"Generated text:\n{text_response.text}")
    
    # Example 2: Image Generation
    print("\n🎨 Image Generation Example:")
    image_service = manager.get_service(AIServiceType.IMAGE_GENERATION)
    
    image_request = ImageGenerationRequest(
        prompt="A happy robot painting a sunset",
        style="oil painting",
        aspect_ratio="16:9"
    )
    
    image_response = await image_service.generate_image(image_request)
    if image_response.image_paths:
        print(f"Image saved to: {image_response.first_image}")
    
    # Example 3: Using with VideoGenerator
    print("\n🎬 VideoGenerator Integration Example:")
    print("To use with VideoGenerator, inject services via constructor:")
    print("""
    # Instead of:
    video_gen = VideoGenerator(api_key=key)  # ❌ Creates clients directly
    
    # Do this:
    manager = AIServiceManager(config)
    video_gen = VideoGeneratorV2(
        service_manager=manager,  # ✅ Uses interfaces
        api_key=key,  # For legacy components
        ...
    )
    """)
    
    # Example 4: Provider Switching
    print("\n🔄 Provider Switching Example:")
    print("Switch providers through configuration without code changes:")
    print("""
    # config/ai_config.yaml
    ai_services:
      image_generation:
        default_provider: VERTEX  # Switch from GEMINI to VERTEX
    """)
    
    # Example 5: Fallback Chains
    print("\n🔗 Fallback Chain Example:")
    manager.set_fallback_chain(
        AIServiceType.IMAGE_GENERATION,
        [AIProvider.GEMINI, AIProvider.VERTEX]
    )
    print("If GEMINI fails, automatically tries VERTEX")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete! Use interfaces for all AI operations.")


if __name__ == "__main__":
    # Ensure API keys are set
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Please set GOOGLE_API_KEY environment variable")
        exit(1)
    
    asyncio.run(main())