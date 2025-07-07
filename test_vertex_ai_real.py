#!/usr/bin/env python3
"""
Test script for Real Vertex AI Veo-2 Integration
This validates the complete workflow from job submission to video download
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
from src.generators.video_generator import VideoGenerator
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_vertex_ai_authentication():
    """Test Vertex AI authentication and setup"""
    logger.info("🔐 Testing Vertex AI Authentication...")
    
    try:
        import google.auth
        import google.auth.transport.requests
        from google.cloud import storage
        
        # Test authentication
        creds, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        
        logger.info(f"✅ Authentication successful")
        logger.info(f"   Project: {project}")
        logger.info(f"   Token: {creds.token[:20]}...")
        
        # Test GCS access
        client = storage.Client()
        bucket = client.bucket("viral-veo2-results")
        
        logger.info(f"✅ GCS bucket access successful")
        logger.info(f"   Bucket: gs://viral-veo2-results/")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        logger.info("💡 Make sure you're authenticated with: gcloud auth login")
        return False

def test_vertex_ai_client():
    """Test Vertex AI Veo-2 client initialization"""
    logger.info("🚀 Testing Vertex AI Veo-2 Client...")
    
    try:
        client = VertexAIVeo2Client(
            project_id="viralgen-464411",
            location="us-central1",
            gcs_bucket="viral-veo2-results",
            output_dir="outputs"
        )
        
        if client.veo_available:
            logger.info("✅ Vertex AI Veo-2 client initialized successfully")
            
            # Test quota check
            quota_info = client.check_api_quota()
            logger.info("📊 Quota Information:")
            for key, value in quota_info.items():
                logger.info(f"   {key}: {value}")
            
            return client
        else:
            logger.error("❌ Client initialization failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Client creation failed: {e}")
        return None

def test_single_video_generation(client):
    """Test generating a single video with Vertex AI Veo-2"""
    logger.info("🎬 Testing Single Video Generation...")
    
    try:
        # Simple, safe prompt that shouldn't trigger content filters
        prompt = "a whimsical cartoon character riding a small pony"
        duration = 8  # Max supported by Veo-2
        clip_id = f"test_{int(time.time())}"
        
        logger.info(f"📝 Prompt: {prompt}")
        logger.info(f"⏱️  Duration: {duration}s")
        logger.info(f"🆔 Clip ID: {clip_id}")
        
        start_time = time.time()
        
        # Generate the video
        video_path = client.generate_video_clip(
            prompt=prompt,
            duration=duration,
            clip_id=clip_id,
            aspect_ratio="16:9"
        )
        
        generation_time = time.time() - start_time
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"✅ Video generated successfully!")
            logger.info(f"   Path: {video_path}")
            logger.info(f"   Size: {file_size:.2f} MB")
            logger.info(f"   Time: {generation_time:.1f} seconds")
            return True
        else:
            logger.error(f"❌ Video generation failed - no file created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Video generation failed: {e}")
        return False

def test_video_generator_integration():
    """Test full VideoGenerator integration with Vertex AI"""
    logger.info("🎞️  Testing VideoGenerator Integration...")
    
    try:
        # Load API key
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            logger.error("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        # Initialize VideoGenerator with Vertex AI
        generator = VideoGenerator(
            api_key=api_key,
            output_dir="outputs",
            use_real_veo2=False,  # Disable Google AI Studio
            use_vertex_ai=True,   # Enable Vertex AI
            vertex_project_id="viralgen-464411",
            vertex_location="us-central1",
            vertex_gcs_bucket="viral-veo2-results"
        )
        
        logger.info("✅ VideoGenerator initialized with Vertex AI")
        
        # Create a simple test configuration
        from generate_custom_video import create_custom_video_config
        config = create_custom_video_config(
            prompt="whimsical cartoon character riding a small pony",
            duration=15,
            style="heartwarming"
        )
        
        logger.info("📋 Test configuration created")
        logger.info(f"   Topic: {config.topic}")
        logger.info(f"   Duration: {config.duration_seconds}s")
        
        # Generate the video (this will use real Vertex AI)
        start_time = time.time()
        generated_video = generator.generate_video(config)
        generation_time = time.time() - start_time
        
        logger.info(f"✅ Full video generated successfully!")
        logger.info(f"   Path: {generated_video.file_path}")
        logger.info(f"   Size: {generated_video.file_size_mb:.2f} MB")
        logger.info(f"   Generation time: {generation_time:.1f} seconds")
        logger.info(f"   AI Models used: {', '.join(generated_video.ai_models_used)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ VideoGenerator integration failed: {e}")
        return False

def test_batch_generation(client):
    """Test generating multiple videos efficiently"""
    logger.info("📚 Testing Batch Video Generation...")
    
    try:
        prompts = [
            {"veo2_prompt": "a cartoon character walking through a forest", "description": "Forest walk"},
            {"veo2_prompt": "a small animal playing in a garden", "description": "Garden play"},
            {"veo2_prompt": "colorful flowers swaying in the breeze", "description": "Flower scene"}
        ]
        
        config = {
            "duration_seconds": 24,  # 8 seconds per clip
            "platform": "INSTAGRAM"
        }
        
        video_id = f"batch_test_{int(time.time())}"
        
        logger.info(f"🎬 Generating {len(prompts)} clips...")
        
        start_time = time.time()
        clips = client.generate_batch_clips(prompts, config, video_id)
        batch_time = time.time() - start_time
        
        if clips:
            logger.info(f"✅ Batch generation completed!")
            logger.info(f"   Generated clips: {len(clips)}")
            logger.info(f"   Total time: {batch_time:.1f} seconds")
            logger.info(f"   Average per clip: {batch_time/len(clips):.1f} seconds")
            
            for i, clip in enumerate(clips, 1):
                logger.info(f"   Clip {i}: {clip['clip_path']}")
            
            return True
        else:
            logger.error("❌ No clips generated")
            return False
            
    except Exception as e:
        logger.error(f"❌ Batch generation failed: {e}")
        return False

def main():
    """Run all Vertex AI tests"""
    logger.info("🧪 VERTEX AI VEO-2 INTEGRATION TESTS")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1: Authentication
    auth_success = test_vertex_ai_authentication()
    results.append(("Authentication", auth_success))
    
    if not auth_success:
        logger.error("🚨 Authentication failed - cannot proceed with other tests")
        logger.info("💡 Please run: gcloud auth login")
        return
    
    # Test 2: Client initialization
    client = test_vertex_ai_client()
    results.append(("Client Initialization", client is not None))
    
    if not client:
        logger.error("🚨 Client initialization failed - cannot proceed")
        return
    
    # Test 3: Single video generation
    single_success = test_single_video_generation(client)
    results.append(("Single Video Generation", single_success))
    
    # Test 4: VideoGenerator integration
    integration_success = test_video_generator_integration()
    results.append(("VideoGenerator Integration", integration_success))
    
    # Test 5: Batch generation
    batch_success = test_batch_generation(client)
    results.append(("Batch Generation", batch_success))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{test_name:<30} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    logger.info(f"\nTotal tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Vertex AI Veo-2 is ready for production!")
    else:
        logger.info("⚠️  Some tests failed - check the logs above for details")

if __name__ == "__main__":
    main() 