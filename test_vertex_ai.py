#!/usr/bin/env python3
"""
Test Vertex AI VEO-2 Generation

This script tests the Vertex AI VEO-2 setup with a simple video generation.
"""

import os
import sys

def test_vertex_ai_generation():
    """Test Vertex AI VEO-2 generation"""
    print("🧪 Testing Vertex AI VEO-2 generation...")
    
    try:
        from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
        
        # Initialize client
        client = VertexAIVeo2Client(
            project_id='viralgen-464411',
            location='us-central1',
            gcs_bucket='viral-veo2-results',
            output_dir='outputs'
        )
        
        if not client.veo_available:
            print("❌ Vertex AI not available")
            return False
        
        # Test generation
        print("🎬 Generating test video...")
        result = client.generate_video_clip(
            prompt="A cute baby laughing and playing with toys",
            duration=5.0,
            clip_id="vertex_test",
            aspect_ratio="16:9"
        )
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / (1024 * 1024)
            print(f"✅ SUCCESS: {result} ({file_size:.1f}MB)")
            print("💰 Estimated cost: ~$0.15")
            print("🚀 No quota limits!")
            return True
        else:
            print("❌ Generation failed - no file created")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test routine"""
    print("🚀 Vertex AI VEO-2 Test")
    print("=" * 30)
    
    success = test_vertex_ai_generation()
    
    if success:
        print("\n🎉 Vertex AI is working perfectly!")
        print("   You now have unlimited VEO generation.")
    else:
        print("\n❌ Vertex AI test failed.")
        print("   Check your Google Cloud setup.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
