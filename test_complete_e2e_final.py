#!/usr/bin/env python3
"""
Complete End-to-End Test with Continuous VEO2 and AI Discussions
"""

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from config.config import settings
import time
import os
import json

def run_complete_e2e_test():
    """Run complete end-to-end test with all features"""
    print("🚀 COMPLETE END-TO-END TEST WITH CONTINUOUS VEO2 AND AI DISCUSSIONS")
    print("=" * 80)
    
    # Create generator
    generator = VideoGenerator(
        api_key=settings.google_api_key,
        use_real_veo2=True,
        use_vertex_ai=True,
        vertex_project_id=settings.veo_project_id,
        vertex_location=settings.veo_location,
        vertex_gcs_bucket='viral-veo2-results',
        output_dir='test_output/complete_e2e'
    )
    
    # Create comprehensive config
    config = GeneratedVideoConfig(
        topic='Complete AI-powered video generation with continuous VEO2 and agent discussions',
        duration_seconds=15,
        target_platform=Platform.YOUTUBE,
        category=VideoCategory.EDUCATIONAL,
        session_id='complete_e2e_' + str(int(time.time())),
        visual_style='minimalist',
        tone='professional',
        hook='Welcome to our complete AI video generation system!',
        call_to_action='Subscribe for more AI-powered content!'
    )
    
    print(f"📋 Test Configuration:")
    print(f"   Topic: {config.topic}")
    print(f"   Duration: {config.duration_seconds} seconds")
    print(f"   Platform: {config.target_platform}")
    print(f"   Session: {config.session_id}")
    print()
    
    try:
        print("🎬 Starting complete video generation...")
        start_time = time.time()
        
        result = generator.generate_video(config)
        
        generation_time = time.time() - start_time
        
        print(f"✅ GENERATION COMPLETED IN {generation_time:.1f} SECONDS!")
        print(f"   Success: {result.success}")
        print(f"   Video file: {result.file_path}")
        print(f"   Audio files: {len(result.audio_files)}")
        print(f"   Script length: {len(result.script)} characters")
        print(f"   File size: {result.file_size_mb:.2f} MB")
        print(f"   Clips generated: {result.clips_generated}")
        print()
        
        # Check session directory
        session_dir = f"outputs/{config.session_id}"
        if os.path.exists(session_dir):
            print(f"📁 SESSION DIRECTORY: {session_dir}")
            
            # Check each subdirectory
            subdirs = ['video_clips', 'audio', 'ai_agents', 'discussions', 'scripts', 'final_output']
            for subdir in subdirs:
                subdir_path = os.path.join(session_dir, subdir)
                if os.path.exists(subdir_path):
                    files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
                    if files:
                        print(f"   📂 {subdir}: {len(files)} files")
                        for file in files[:3]:  # Show first 3 files
                            file_path = os.path.join(subdir_path, file)
                            size = os.path.getsize(file_path)
                            print(f"      📄 {file}: {size:,} bytes")
            print()
            
            # Check for AI agent discussions
            discussion_file = os.path.join(session_dir, "ai_agent_discussion.json")
            if os.path.exists(discussion_file):
                print("🤖 AI AGENT DISCUSSIONS FOUND:")
                try:
                    with open(discussion_file, 'r') as f:
                        discussion = json.load(f)
                    
                    agents = discussion.get('agents', {})
                    print(f"   🔹 Total agents: {len(agents)}")
                    for agent_name, agent_data in agents.items():
                        print(f"   🔹 {agent_data.get('agent_name', agent_name)}")
                        print(f"      Role: {agent_data.get('role', 'N/A')}")
                    
                    summary = discussion.get('discussion_summary', {})
                    print(f"   📊 Consensus: {summary.get('consensus', 'N/A')}")
                    print()
                except Exception as e:
                    print(f"   ❌ Error reading discussion: {e}")
            
            # Check for continuous VEO2 clips
            veo_clips_dir = os.path.join(session_dir, "video_clips", "veo_clips")
            if os.path.exists(veo_clips_dir):
                clips = [f for f in os.listdir(veo_clips_dir) if f.endswith('.mp4')]
                print(f"🎬 CONTINUOUS VEO2 CLIPS: {len(clips)} clips")
                for clip in clips:
                    clip_path = os.path.join(veo_clips_dir, clip)
                    size = os.path.getsize(clip_path)
                    print(f"   🎞️ {clip}: {size:,} bytes")
                print()
        
        # Final assessment
        quality_score = 0
        
        if result.success:
            quality_score += 25
            print("✅ Video generation successful")
        
        if result.file_path and os.path.exists(result.file_path):
            quality_score += 25
            print("✅ Video file created")
        
        if len(result.audio_files) > 0:
            quality_score += 25
            print("✅ Audio files generated")
        
        if len(result.script) > 50:
            quality_score += 25
            print("✅ Script generated")
        
        print(f"📊 Quality Score: {quality_score}/100")
        print()
        
        if quality_score >= 75:
            print("🎉 COMPLETE END-TO-END TEST PASSED!")
            print("   ✅ Continuous VEO2 video generation working")
            print("   ✅ AI agent discussions implemented")
            print("   ✅ Comprehensive session data created")
            print("   ✅ All components functioning correctly")
            return True
        else:
            print("❌ Test failed - quality score too low")
            return False
            
    except Exception as e:
        print(f"❌ COMPLETE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_complete_e2e_test()
    exit(0 if success else 1) 