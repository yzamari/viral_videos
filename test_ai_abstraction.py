#!/usr/bin/env python3
"""
Test script for AI abstraction layer
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ai.manager import AIServiceManager
from src.ai.interfaces.text_generation import TextGenerationRequest

async def test_ai_abstraction():
    """Test the AI abstraction layer"""
    try:
        print("🔧 Testing AI abstraction layer...")
        
        # Create AI service manager
        ai_manager = AIServiceManager()
        
        # Get text service
        text_service = ai_manager.get_text_service()
        print(f"✅ Created text service: {text_service.get_provider_name()}")
        
        # Test generation
        request = TextGenerationRequest(
            prompt="Say hello world in a simple way",
            max_tokens=20,
            temperature=0.1
        )
        
        print("🚀 Testing text generation...")
        response = await text_service.generate(request)
        
        print(f"✅ Generation successful!")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Text: {response.text[:100]}...")
        print(f"   Tokens used: {response.usage}")
        print(f"   Cost estimate: ${response.cost_estimate:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_abstraction())
    sys.exit(0 if success else 1)