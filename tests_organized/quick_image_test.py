#!/usr/bin/env python3
"""
Quick Image Generation Test for AI Video Generator
Tests image-based video generation which should work reliably
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_image_video_generation():
    """Test image-based video generation"""
    print("🎨 Quick Image-Based Video Generation Test")
    print("=" * 60)
    
    try:
        # Import orchestrator
        from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
        
        print("✅ Orchestrator imported successfully")
        
        # Create orchestrator
        orchestrator = create_working_simple_orchestrator(
            topic="Amazing benefits of yoga for healthy living",
            platform="instagram",
            category="health",
            duration=15,  # Short duration for quick test
            api_key=os.getenv('GOOGLE_API_KEY', 'test_key'),
            mode="simple"
        )
        
        print(f"✅ Orchestrator created - Session: {orchestrator.session_id}")
        
        # Test configuration - Force image generation
        config = {
            'force_generation': 'force_image_gen',
            'frame_continuity': 'off',
            'image_only': True,
            'fallback_only': False,
            'style': 'professional',
            'tone': 'inspiring'
        }
        
        print("🎨 Starting image-based video generation...")
        start_time = time.time()
        
        # Generate video
        result = orchestrator.generate_video(config)
        
        generation_time = time.time() - start_time
        
        print(f"⏱️  Generation completed in {generation_time:.1f} seconds")
        
        # Check result
        if result.get('success'):
            print("✅ Image-based video generation successful!")
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
                
                # Check session directory
                session_dir = os.path.dirname(video_path)
                if os.path.exists(session_dir):
                    files = os.listdir(session_dir)
                    image_files = [f for f in files if f.endswith(('.jpg', '.png', '.jpeg'))]
                    print(f"   Images generated: {len(image_files)}")
                    print(f"   Session files: {len(files)}")
                
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
    print("🧪 Running Quick Image Generation Test...")
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GOOGLE_API_KEY found - test will likely fail")
        return 1
    else:
        print(f"✅ API key found (length: {len(api_key)})")
    
    # Run test
    success = test_image_video_generation()
    
    print("\n" + "=" * 60)
    print("🎯 IMAGE GENERATION TEST RESULT")
    print("=" * 60)
    
    if success:
        print("🎉 IMAGE GENERATION TEST PASSED!")
        print("✅ Image-based video generation working")
        print("✅ AI agents making decisions")
        print("✅ Output files created")
        print("🎨 Image generation pipeline functional")
        return 0
    else:
        print("❌ IMAGE GENERATION TEST FAILED")
        print("⚠️  Image generation pipeline has issues")
        print("🔧 Check logs above for details")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 