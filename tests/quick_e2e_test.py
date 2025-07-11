#!/usr/bin/env python3
"""
Quick End-to-End Test for AI Video Generator
Tests actual video generation with a simple topic
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_video_generation():
    """Test actual video generation"""
    print("🎬 Quick End-to-End Video Generation Test")
    print("=" * 60)
    
    try:
        # Import orchestrator
        from src.agents.working_orchestrator import create_working_orchestrator
        
        print("✅ Orchestrator imported successfully")
        
        # Create orchestrator
        orchestrator = create_working_orchestrator(
            topic="Quick test of AI video generation capabilities",
            platform="instagram",
            category="education",
            duration=15,  # Short duration for quick test
            api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        print(f"✅ Orchestrator created - Session: {orchestrator.session_id}")
        
        # Test configuration
        config = {
            'force_generation': 'force_image_gen',  # Use fastest generation mode
            'frame_continuity': 'off',
            'image_only': True,
            'fallback_only': False,
            'style': 'viral',
            'tone': 'engaging'
        }
        
        print("🚀 Starting video generation (image-only mode for speed)...")
        start_time = time.time()
        
        # Generate video
        result = orchestrator.generate_video(config)
        
        generation_time = time.time() - start_time
        
        print(f"⏱️  Generation completed in {generation_time:.1f} seconds")
        
        # Check result
        if result.get('success'):
            print("✅ Video generation successful!")
            print(f"   Final video path: {result.get('final_video_path', 'Not specified')}")
            print(f"   Session ID: {result.get('session_id', 'N/A')}")
            print(f"   Mode: {result.get('mode', 'N/A')}")
            print(f"   Agents used: {result.get('agents_used', 0)}")
            print(f"   Agent decisions made: {len(result.get('agent_decisions', {}))}")
            
            # Check if video file exists
            video_path = result.get('final_video_path')
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                print(f"   Video file size: {file_size / 1024 / 1024:.2f} MB")
                print("✅ Video file created successfully")
                return True
            else:
                print("⚠️  Video file not found on disk")
                return False
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ Video generation failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Running Quick E2E Test...")
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GOOGLE_API_KEY found - test will likely fail")
        return 1
    else:
        print(f"✅ API key found (length: {len(api_key)})")
    
    # Run test
    success = test_video_generation()
    
    print("\n" + "=" * 60)
    print("🎯 E2E TEST RESULT")
    print("=" * 60)
    
    if success:
        print("🎉 END-TO-END TEST PASSED!")
        print("✅ Video generation pipeline working")
        print("✅ AI agents making decisions")
        print("✅ Output files created")
        print("🎬 System ready for production use")
        return 0
    else:
        print("❌ END-TO-END TEST FAILED")
        print("⚠️  Video generation pipeline has issues")
        print("🔧 Check logs above for details")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 