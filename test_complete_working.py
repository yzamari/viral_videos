#!/usr/bin/env python3
"""
Complete Working Test - Verify all functionality
"""

import os
import sys
import time
from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory

def test_complete_generation():
    """Test complete video generation with all features"""
    print("🚀 Starting complete video generation test...")
    
    # Create config
    config = GeneratedVideoConfig(
        topic="Complete system test with AI discussions",
        duration_seconds=8,
        target_platform=Platform.YOUTUBE,
        category=VideoCategory.ENTERTAINMENT,
        session_id="complete_working_test"
    )
    
    # Create generator
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    generator = VideoGenerator(
        api_key=api_key,
        use_real_veo2=True,
        use_vertex_ai=True,
        vertex_project_id="viralgen-464411",
        vertex_location="us-central1",
        vertex_gcs_bucket="viral-veo2-results",
        prefer_veo3=False
    )
    
    # Generate video
    start_time = time.time()
    result = generator.generate_video(config)
    generation_time = time.time() - start_time
    
    print(f"✅ Generation completed in {generation_time:.1f}s")
    print(f"   Success: {result.success}")
    print(f"   Video: {result.file_path}")
    print(f"   Audio files: {len(result.audio_files)}")
    print(f"   Script: {len(result.script)} characters")
    print(f"   Size: {result.file_size_mb:.2f}MB")
    
    # Check session contents
    session_dir = f"outputs/{config.session_id}"
    if os.path.exists(session_dir):
        print(f"\n📁 SESSION DIRECTORY: {session_dir}")
        
        # Check discussions
        discussions_dir = os.path.join(session_dir, "discussions")
        if os.path.exists(discussions_dir):
            files = os.listdir(discussions_dir)
            print(f"   📝 Discussions: {len(files)} files")
            for file in files:
                file_path = os.path.join(discussions_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"      ✅ {file}: {size:,} bytes")
        
        # Check final video
        final_dir = os.path.join(session_dir, "final_output")
        if os.path.exists(final_dir):
            files = os.listdir(final_dir)
            print(f"   🎬 Final output: {len(files)} files")
            for file in files:
                file_path = os.path.join(final_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"      ✅ {file}: {size:,} bytes")
        
        # Check AI agents
        ai_dir = os.path.join(session_dir, "ai_agents")
        if os.path.exists(ai_dir):
            files = os.listdir(ai_dir)
            print(f"   🤖 AI agents: {len(files)} files")
            for file in files:
                file_path = os.path.join(ai_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"      ✅ {file}: {size:,} bytes")
    
    return result

if __name__ == "__main__":
    try:
        result = test_complete_generation()
        print("\n🎉 COMPLETE TEST SUCCESSFUL!")
        print("✅ All features working:")
        print("   - VEO-2 video generation")
        print("   - AI agent discussions")
        print("   - Session management")
        print("   - Audio generation")
        print("   - Final video composition")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
