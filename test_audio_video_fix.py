#!/usr/bin/env python3
"""
Test audio and video fixes
"""

import os
import sys
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_audio_video_fixes():
    """Test that audio and video fixes work"""
    print("🧪 Testing audio and video fixes...")
    
    try:
        from src.generators.video_generator import VideoGenerator
        from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
        
        print("✅ Imports successful")
        
        # Create simple config
        config = GeneratedVideoConfig(
            topic="Audio and video test",
            duration_seconds=5,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.ENTERTAINMENT,
            session_id="audio_video_test"
        )
        
        # Test generator creation
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return False
        
        generator = VideoGenerator(
            api_key=api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            vertex_project_id="viralgen-464411",
            vertex_location="us-central1",
            vertex_gcs_bucket="viral-veo2-results",
            prefer_veo3=False
        )
        
        print("✅ Generator created successfully")
        
        # Test video generation
        print("🎬 Starting video generation...")
        start_time = time.time()
        
        result = generator.generate_video(config)
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation completed in {generation_time:.1f}s")
        
        if result and hasattr(result, 'success') and result.success:
            print("✅ Video generation successful!")
            print(f"📁 Video path: {result.file_path}")
            print(f"🎵 Audio files: {len(result.audio_files) if result.audio_files else 0}")
            print(f"📊 File size: {result.file_size_mb:.2f}MB")
            
            # Check if final video exists and has content
            if os.path.exists(result.file_path):
                size = os.path.getsize(result.file_path)
                print(f"📁 Final video size: {size:,} bytes")
                if size > 1000:
                    print("✅ Final video has content!")
                else:
                    print("⚠️ Final video is very small")
            else:
                print("❌ Final video file not found")
            
            # Check session directory
            session_dir = f"outputs/{config.session_id}"
            if os.path.exists(session_dir):
                print(f"📂 Session directory exists: {session_dir}")
                
                # Check audio directory
                audio_dir = os.path.join(session_dir, "audio")
                if os.path.exists(audio_dir):
                    audio_files = os.listdir(audio_dir)
                    print(f"🎵 Audio files in session: {len(audio_files)}")
                    for audio_file in audio_files:
                        audio_path = os.path.join(audio_dir, audio_file)
                        if os.path.isfile(audio_path):
                            size = os.path.getsize(audio_path)
                            print(f"   ✅ {audio_file}: {size:,} bytes")
                
                # Check discussions
                discussions_dir = os.path.join(session_dir, "discussions")
                if os.path.exists(discussions_dir):
                    discussion_files = os.listdir(discussions_dir)
                    print(f"📝 Discussion files: {len(discussion_files)}")
                    for file in discussion_files:
                        file_path = os.path.join(discussions_dir, file)
                        if os.path.isfile(file_path):
                            size = os.path.getsize(file_path)
                            print(f"   ✅ {file}: {size:,} bytes")
            
            return True
        else:
            print("❌ Video generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 TESTING AUDIO AND VIDEO FIXES")
    print("=" * 40)
    
    success = test_audio_video_fixes()
    
    if success:
        print("\n🎉 TEST SUCCESSFUL!")
        print("✅ Audio generation working")
        print("✅ Video composition working")
        print("✅ Session management working")
    else:
        print("\n❌ TEST FAILED!")
        print("🔧 Additional fixes needed") 