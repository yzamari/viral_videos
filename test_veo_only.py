#!/usr/bin/env python3
"""
Test script to verify VEO-only generation without fallbacks
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generators.vertex_ai_veo2_client import VertexAIVeo2Client
from generators.optimized_veo_client import OptimizedVeoClient
from utils.logging_config import get_logger

logger = get_logger(__name__)

def test_veo_only_generation():
    """Test VEO-only generation without fallbacks"""
    
    print("🎬 Testing VEO-Only Generation (No Fallbacks)")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY")
        return False
    
    # Test with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temp directory: {temp_dir}")
        
        # Test 1: Google AI Studio VEO
        print("\n🔍 Test 1: Google AI Studio VEO")
        try:
            veo_client = OptimizedVeoClient(
                api_key=api_key,
                output_dir=temp_dir,
                disable_veo3=True
            )
            
            # Force VEO-only mode
            veo_client.veo_quota_exhausted = False
            veo_client.gemini_images_available = False  # Disable image fallback
            
            video_path = veo_client.generate_video(
                prompt="Simple colorful shapes moving",
                duration=5.0,
                clip_id="test_clip"
            )
            
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                print(f"✅ Google AI Studio VEO: SUCCESS ({file_size:.1f}MB)")
                print(f"   Video: {video_path}")
                return True
            else:
                print("❌ Google AI Studio VEO: FAILED - No video generated")
                return False
                
        except Exception as e:
            print(f"❌ Google AI Studio VEO: FAILED - {e}")
            
            # Check if it's a quota issue
            if "429" in str(e) or "quota" in str(e).lower():
                print("⚠️ Quota exhausted on Google AI Studio VEO")
                
                # Test 2: Vertex AI VEO
                print("\n🔍 Test 2: Vertex AI VEO")
                try:
                    vertex_client = VertexAIVeo2Client(
                        project_id="viralgen-464411",
                        location="us-central1",
                        gcs_bucket="viral-veo2-results-1752230855",
                        output_dir=temp_dir
                    )
                    
                    video_path = vertex_client.generate_video(
                        prompt="Simple colorful shapes moving",
                        duration=5.0,
                        clip_id="test_clip"
                    )
                    
                    if video_path and os.path.exists(video_path):
                        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                        print(f"✅ Vertex AI VEO: SUCCESS ({file_size:.1f}MB)")
                        print(f"   Video: {video_path}")
                        return True
                    else:
                        print("❌ Vertex AI VEO: FAILED - No video generated")
                        return False
                        
                except Exception as ve:
                    print(f"❌ Vertex AI VEO: FAILED - {ve}")
                    return False
            else:
                return False

def main():
    """Main test function"""
    success = test_veo_only_generation()
    
    if success:
        print("\n🎉 VEO-Only Generation Test: PASSED")
        print("✅ System can generate videos using VEO without fallbacks")
    else:
        print("\n❌ VEO-Only Generation Test: FAILED")
        print("⚠️ System may need quota increases or configuration changes")
        
        print("\n🔧 Recommended Actions:")
        print("1. Request Vertex AI quota increase:")
        print("   https://console.cloud.google.com/iam-admin/quotas")
        print("2. Check Google AI Studio quota:")
        print("   https://aistudio.google.com/")
        print("3. Verify API keys and project configuration")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 