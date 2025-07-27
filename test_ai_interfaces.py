#!/usr/bin/env python3
"""Test script for the new AI service interfaces"""

import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ai.manager import AIServiceManager
from src.ai.config import AIConfiguration
from src.ai.interfaces.base import AIServiceType, AIProvider, AIServiceConfig
from src.ai.interfaces.image_generation import ImageGenerationRequest
from src.ai.interfaces.speech_synthesis import SpeechSynthesisRequest
from src.ai.interfaces.video_generation import VideoGenerationRequest

# Initialize providers after imports
from src.ai.factory import AIServiceFactory
AIServiceFactory.initialize_providers()


async def test_interfaces():
    """Test all AI service interfaces"""
    
    print("🧪 Testing AI Service Interfaces")
    print("=" * 50)
    
    # Create AI configuration
    config = AIConfiguration.create_default()
    
    # Create service manager
    manager = AIServiceManager(config)
    
    # Test 1: Image Generation
    print("\n1️⃣ Testing Image Generation Service")
    try:
        image_service = manager.get_service(AIServiceType.IMAGE_GENERATION)
        print(f"✅ Got image service: {image_service.get_provider_name()}")
        
        # Test image generation
        request = ImageGenerationRequest(
            prompt="A cute robot painting a picture",
            style="digital art",
            aspect_ratio="16:9"
        )
        
        print("📸 Generating test image...")
        response = await image_service.generate_image(request)
        
        if response.image_paths:
            print(f"✅ Image generated: {response.first_image}")
            print(f"   Provider: {response.provider_used}")
            print(f"   Time: {response.generation_time:.2f}s")
        else:
            print("❌ No image generated")
            
    except Exception as e:
        print(f"❌ Image service error: {str(e)}")
    
    # Test 2: Speech Synthesis
    print("\n2️⃣ Testing Speech Synthesis Service")
    try:
        speech_service = manager.get_service(AIServiceType.SPEECH_SYNTHESIS)
        print(f"✅ Got speech service: {speech_service.get_provider_name()}")
        
        # Test speech synthesis
        request = SpeechSynthesisRequest(
            text="Hello, this is a test of the AI service interfaces.",
            language="en",
            voice_id="male"
        )
        
        print("🎤 Generating test speech...")
        response = await speech_service.synthesize(request)
        
        if response.audio_path:
            print(f"✅ Speech generated: {response.audio_path}")
            print(f"   Provider: {response.provider_used}")
            print(f"   Duration: {response.duration:.2f}s")
        else:
            print("❌ No speech generated")
            
    except Exception as e:
        print(f"❌ Speech service error: {str(e)}")
    
    # Test 3: Video Generation
    print("\n3️⃣ Testing Video Generation Service")
    try:
        video_service = manager.get_service(AIServiceType.VIDEO_GENERATION)
        print(f"✅ Got video service: {video_service.get_provider_name()}")
        
        # Test video generation (with a short test video)
        request = VideoGenerationRequest(
            prompt="A robot dancing happily",
            duration=2.0,  # Short test video
            style="cartoon",
            aspect_ratio="16:9"
        )
        
        print("🎬 Generating test video...")
        response = await video_service.generate_video(request)
        
        if response.video_path:
            print(f"✅ Video generated: {response.video_path}")
            print(f"   Provider: {response.provider_used}")
            print(f"   Time: {response.generation_time:.2f}s")
        else:
            print(f"⏳ Video job started: {response.job_id}")
            print(f"   Status: {response.status.value}")
            
    except Exception as e:
        print(f"❌ Video service error: {str(e)}")
    
    # Test 4: Provider Fallback
    print("\n4️⃣ Testing Provider Fallback")
    try:
        # Set fallback chain for image generation
        manager.set_fallback_chain(
            AIServiceType.IMAGE_GENERATION,
            [AIProvider.GEMINI, AIProvider.VERTEX]
        )
        
        print("📸 Testing image generation with fallback...")
        result = await manager.execute_with_fallback(
            AIServiceType.IMAGE_GENERATION,
            'generate_image',
            ImageGenerationRequest(
                prompt="A beautiful sunset over mountains",
                aspect_ratio="16:9"
            )
        )
        
        if result.image_paths:
            print(f"✅ Fallback worked: {result.provider_used}")
        
    except Exception as e:
        print(f"❌ Fallback error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Interface testing complete!")


if __name__ == "__main__":
    # Set up environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # Run async test
    asyncio.run(test_interfaces())