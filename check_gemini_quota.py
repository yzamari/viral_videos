#!/usr/bin/env python3
"""
Check Gemini Model Quota Usage
Tests different models and shows their quota limits
"""
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_models():
    """Test different Gemini models and their quota limits"""
    
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY")
        return
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Models to test (using only gemini-2.5-flash for consistency)
        models_to_test = [
            ('gemini-2.5-flash', 'Primary model with excellent quota and performance'),
        ]
        
        print("🧪 Testing Gemini Models for Quota Limits")
        print("=" * 50)
        
        for model_name, description in models_to_test:
            print(f"\n🤖 Testing: {model_name}")
            print(f"📋 Description: {description}")
            
            try:
                model = genai.GenerativeModel(model_name)
                
                # Simple test request
                response = model.generate_content("Say 'Hello, this is a quota test'")
                
                if response and response.text:
                    print(f"✅ {model_name}: WORKING")
                    print(f"   Response: {response.text[:50]}...")
                else:
                    print(f"⚠️ {model_name}: Empty response")
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"🚫 {model_name}: QUOTA EXCEEDED")
                    print(f"   Error: {error_str[:100]}...")
                elif "not found" in error_str.lower():
                    print(f"❌ {model_name}: MODEL NOT AVAILABLE")
                else:
                    print(f"❌ {model_name}: ERROR - {error_str[:100]}...")
            
            # Small delay between tests
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print("💡 RECOMMENDATIONS:")
        print("1. Use gemini-2.5-flash for all tasks (primary model)")
        print("2. Set GEMINI_MODEL environment variable to gemini-2.5-flash")
        print("3. All agents now use gemini-2.5-flash for consistency")
        
    except ImportError:
        print("❌ google-generativeai not installed")
        print("Install with: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Error testing models: {e}")

if __name__ == "__main__":
    test_gemini_models() 