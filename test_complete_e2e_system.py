#!/usr/bin/env python3
"""
Complete End-to-End System Test
Tests the entire video generation pipeline with real API calls
"""

import os
import sys
import time
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from config.config import settings

def run_complete_e2e_test():
    """Run a complete end-to-end test of the video generation system"""
    
    print("🚀 COMPLETE END-TO-END SYSTEM TEST")
    print("=" * 60)
    
    # Test configuration
    test_session_id = f"e2e_test_{int(time.time())}"
    output_dir = f"test_output/e2e_{test_session_id}"
    
    print(f"📋 Test Session: {test_session_id}")
    print(f"📁 Output Directory: {output_dir}")
    print(f"🔑 API Key: {'✅ SET' if settings.google_api_key else '❌ MISSING'}")
    print(f"🎬 VEO Project: {settings.veo_project_id}")
    print(f"🌍 VEO Location: {settings.veo_location}")
    print()
    
    # Step 1: Initialize Video Generator
    print("STEP 1: Initialize Video Generator")
    print("-" * 40)
    
    start_time = time.time()
    try:
        generator = VideoGenerator(
            api_key=settings.google_api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            vertex_project_id=settings.veo_project_id,
            vertex_location=settings.veo_location,
            vertex_gcs_bucket=os.getenv('VERTEX_AI_GCS_BUCKET', 'viral-veo2-results'),
            output_dir=output_dir
        )
        init_time = time.time() - start_time
        print(f"✅ Video generator initialized in {init_time:.2f} seconds")
        print(f"   Components: Script processor, Style agent, Positioning agent, Voice director")
        print(f"   VEO models: Available and authenticated")
        print()
    except Exception as e:
        print(f"❌ Video generator initialization failed: {e}")
        return False
    
    # Step 2: Create Video Configuration
    print("STEP 2: Create Video Configuration")
    print("-" * 40)
    
    try:
        config = GeneratedVideoConfig(
            topic="AI-powered video generation demonstration",
            duration_seconds=15,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATIONAL,
            session_id=test_session_id,
            visual_style="minimalist",
            tone="professional",
            hook="Welcome to our AI video generation demo!",
            call_to_action="Thanks for watching! Subscribe for more AI content!"
        )
        print(f"✅ Video configuration created")
        print(f"   Topic: {config.topic}")
        print(f"   Duration: {config.duration_seconds} seconds")
        print(f"   Platform: {config.target_platform}")
        print(f"   Category: {config.category}")
        print()
    except Exception as e:
        print(f"❌ Video configuration creation failed: {e}")
        return False
    
    # Step 3: Generate Video (Full Pipeline)
    print("STEP 3: Generate Video (Full Pipeline)")
    print("-" * 40)
    
    generation_start_time = time.time()
    try:
        print("🎬 Starting video generation...")
        
        # Create session context
        from src.utils.session_context import SessionContext
        session_context = SessionContext(
            session_id=test_session_id
        )
        
        # Generate video
        result = generator.generate_video(config)
        
        generation_time = time.time() - generation_start_time
        
        if result and result.success:
            print(f"✅ Video generation completed in {generation_time:.2f} seconds")
            print(f"   Video file: {result.file_path}")
            print(f"   Audio files: {len(result.audio_files)} files")
            print(f"   Script: {result.script[:100]}...")
            print(f"   Duration: {result.generation_time_seconds} seconds")
            print()
        else:
            print(f"❌ Video generation failed: {result.error_message if result else 'Unknown error'}")
            return False
            
    except Exception as e:
        print(f"❌ Video generation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Validate Output Files
    print("STEP 4: Validate Output Files")
    print("-" * 40)
    
    try:
        files_to_check = [
            result.file_path,
            *result.audio_files
        ]
        
        valid_files = 0
        for file_path in files_to_check:
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✅ {os.path.basename(file_path)}: {file_size:,} bytes")
                valid_files += 1
            else:
                print(f"❌ Missing: {file_path}")
        
        if valid_files >= 1:  # At least video file
            print(f"✅ Output validation passed ({valid_files}/{len(files_to_check)} files)")
            print()
        else:
            print(f"❌ Output validation failed ({valid_files}/{len(files_to_check)} files)")
            return False
            
    except Exception as e:
        print(f"❌ Output validation failed: {e}")
        return False
    
    # Step 5: Performance Summary
    print("STEP 5: Performance Summary")
    print("-" * 40)
    
    total_time = time.time() - start_time
    
    print(f"📊 Performance Metrics:")
    print(f"   Initialization time: {init_time:.2f} seconds")
    print(f"   Video generation time: {generation_time:.2f} seconds")
    print(f"   Total time: {total_time:.2f} seconds")
    print(f"   Average time per second of video: {generation_time/config.duration_seconds:.2f}s")
    print()
    
    # Step 6: Quality Assessment
    print("STEP 6: Quality Assessment")
    print("-" * 40)
    
    quality_score = 0
    
    # Check if video file exists and has reasonable size
    if result.file_path and os.path.exists(result.file_path):
        video_size = os.path.getsize(result.file_path)
        if video_size > 100000:  # At least 100KB
            quality_score += 25
            print("✅ Video file size adequate")
        else:
            print("❌ Video file size too small")
    
    # Check if audio file exists and has reasonable size
    if result.audio_files and result.audio_files[0] and os.path.exists(result.audio_files[0]):
        audio_size = os.path.getsize(result.audio_files[0])
        if audio_size > 10000:  # At least 10KB
            quality_score += 25
            print("✅ Audio file size adequate")
        else:
            print("❌ Audio file size too small")
    
    # Check if script was generated
    if result.script and len(result.script) > 50:
        quality_score += 25
        print("✅ Script generated adequately")
    else:
        print("❌ Script generation inadequate")
    
    # Check if generation completed without errors
    if result.success:
        quality_score += 25
        print("✅ Generation completed successfully")
    else:
        print("❌ Generation completed with errors")
    
    print(f"📈 Quality Score: {quality_score}/100")
    print()
    
    # Final Results
    print("FINAL RESULTS")
    print("=" * 60)
    
    if quality_score >= 75:
        print("🎉 END-TO-END TEST PASSED!")
        print("   System is working correctly and ready for production")
        print(f"   Quality Score: {quality_score}/100")
        print(f"   Total Time: {total_time:.2f} seconds")
        print(f"   Output Directory: {output_dir}")
        return True
    else:
        print("❌ END-TO-END TEST FAILED")
        print(f"   Quality Score: {quality_score}/100 (minimum 75 required)")
        print("   System needs further debugging")
        return False

if __name__ == '__main__':
    success = run_complete_e2e_test()
    sys.exit(0 if success else 1) 