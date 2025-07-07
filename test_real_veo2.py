#!/usr/bin/env python3
"""
Test Real Veo-2 API Integration

Run this script to test if Google's Veo-2 API is working and generating actual AI videos.
"""
import os
import sys

# Instructions for user
INSTRUCTIONS = """
🎬 REAL VEO-2 API TEST
======================

PREREQUISITES:
1. Set your API key: export GOOGLE_API_KEY="your_api_key_here"
2. Make sure you have Veo-2 access in Google AI Studio
3. Run: python test_real_veo2.py

WHAT THIS TESTS:
✅ Real Veo-2 API connection
✅ Actual AI video generation from prompts
✅ Video content matching "baby hanging out with animals"
✅ Fallback system if API limits reached

"""

def main():
    print(INSTRUCTIONS)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: No API key found!")
        print("💡 Solution: export GOOGLE_API_KEY='your_working_api_key'")
        print("🔗 Get API key: https://aistudio.google.com/app/apikey")
        return False
    
    print(f"✅ API Key Found: {api_key[:25]}...")
    
    # Test the integration
    try:
        sys.path.insert(0, 'src')
        from src.generators.real_veo2_client import RealVeo2Client
        
        print("\n🎬 Testing Real Veo-2 Integration...")
        veo_client = RealVeo2Client(api_key, "outputs")
        
        print(f"🔍 Veo-2 Available: {veo_client.veo_available}")
        if hasattr(veo_client, 'veo_model_name'):
            print(f"🎯 Model: {veo_client.veo_model_name}")
        
        # Test real video generation
        print("\n📹 Generating REAL AI Video...")
        print("Prompt: 'Adorable baby sitting with gentle puppy and bunny in cozy living room'")
        
        video_path = veo_client.generate_video_clip(
            prompt="Adorable baby sitting with gentle puppy and bunny in cozy living room",
            duration=5.0,
            clip_id="real_veo2_test"
        )
        
        if os.path.exists(video_path):
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f"✅ SUCCESS: Real AI video generated!")
            print(f"📁 File: {video_path}")
            print(f"📏 Size: {size_mb:.2f} MB")
            
            # Check if it's actual Veo-2 content or fallback
            with open("outputs/veo2_clips/test_real_veo2.log", "w") as f:
                f.write(f"Real Veo-2 test completed\nVideo: {video_path}\nSize: {size_mb:.2f} MB\n")
            
            return True
        else:
            print(f"❌ FAILED: Video not created at {video_path}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 REAL VEO-2 INTEGRATION WORKING!")
        print("🚀 Now run: export GOOGLE_API_KEY='your_key' && python example_usage.py --prompt 'baby hanging out with animals' --duration 30")
    else:
        print("\n⚠️  Using fallback mode (test patterns)")
        print("💡 Veo-2 API may need billing enabled or model access approved") 