#!/usr/bin/env python3
"""
Test script to verify gemini-2.5-flash-lite model works
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import google.generativeai as genai
from src.config.ai_model_config import DEFAULT_AI_MODEL
from src.agents.gemini_helper import GeminiModelHelper

# Load environment variables
load_dotenv()

def test_basic_generation():
    """Test basic text generation with gemini-2.5-flash-lite"""
    print(f"🧪 Testing {DEFAULT_AI_MODEL}...")
    
    # Get API key
    api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found in environment")
        return False
    
    try:
        # Test 1: Direct genai usage
        print("\n📝 Test 1: Direct genai usage")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(DEFAULT_AI_MODEL)
        response = model.generate_content("Say hello in 5 words or less")
        print(f"✅ Response: {response.text.strip()}")
        
        # Test 2: Using GeminiModelHelper
        print("\n📝 Test 2: Using GeminiModelHelper")
        helper_model = GeminiModelHelper.get_configured_model(api_key)
        response2 = helper_model.generate_content("Count from 1 to 5")
        print(f"✅ Response: {response2.text.strip()}")
        
        # Test 3: Complex prompt
        print("\n📝 Test 3: Complex prompt with JSON")
        complex_prompt = """
        Create a simple JSON object with these fields:
        - name: "Test"
        - value: 42
        - active: true
        
        Return ONLY the JSON, no explanations.
        """
        response3 = model.generate_content(complex_prompt)
        print(f"✅ Response: {response3.text.strip()}")
        
        print(f"\n✅ All tests passed! {DEFAULT_AI_MODEL} is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing {DEFAULT_AI_MODEL}: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_agent_integration():
    """Test agent integration with the new model"""
    print(f"\n🧪 Testing agent integration with {DEFAULT_AI_MODEL}...")
    
    api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    try:
        # Test with VoiceDirectorAgent
        from src.agents.voice_director_agent import VoiceDirectorAgent
        print("\n📝 Testing VoiceDirectorAgent...")
        voice_agent = VoiceDirectorAgent(api_key)
        print("✅ VoiceDirectorAgent initialized successfully")
        
        # Test with VisualStyleAgent
        from src.agents.visual_style_agent import VisualStyleAgent
        print("\n📝 Testing VisualStyleAgent...")
        style_agent = VisualStyleAgent(api_key)
        print("✅ VisualStyleAgent initialized successfully")
        
        # Test with Director
        from src.generators.director import Director
        print("\n📝 Testing Director...")
        director = Director(api_key)
        print(f"✅ Director initialized with model: {director.model_name}")
        
        print(f"\n✅ All agent integrations passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in agent integration: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def main():
    """Main test function"""
    print(f"🚀 Testing Gemini Model: {DEFAULT_AI_MODEL}")
    print("=" * 60)
    
    # Run basic tests
    basic_ok = test_basic_generation()
    
    # Run agent integration tests
    agent_ok = test_agent_integration()
    
    # Summary
    print("\n" + "=" * 60)
    if basic_ok and agent_ok:
        print("✅ ALL TESTS PASSED! gemini-2.5-flash-lite is ready to use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    return basic_ok and agent_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)