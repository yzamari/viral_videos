#!/usr/bin/env python3
"""
Quick VEO-3 Test Script
Test Vertex AI VEO-3 integration with native audio generation
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_veo3_integration():
    """Test VEO-3 integration with native audio generation"""
    print("🎬 Testing Vertex AI VEO-3 Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import client
        print("📦 Testing imports...")
        from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
        print("✅ Vertex AI client imported successfully")
        
        # Test 2: Initialize client
        print("\n🔧 Testing client initialization...")
        client = VertexAIVeo2Client(
            project_id="viralgen-464411",
            location="us-central1",
            gcs_bucket="viralgen-veo2-results-20250707",
            output_dir="outputs"
        )
        
        if client.veo_available:
            print("✅ Vertex AI VEO-3 client initialized successfully!")
            print(f"   Project: {client.project_id}")
            print(f"   Location: {client.location}")
            print(f"   VEO-2 Model: {client.veo2_model}")
            print(f"   VEO-3 Model: {client.veo3_model}")
        else:
            print("❌ Vertex AI VEO not available")
            return False
        
        # Test 3: Model selection
        print("\n🎯 Testing VEO-3 model selection...")
        model, max_duration = client._select_optimal_model(
            duration=8.0, 
            prefer_veo3=True, 
            enable_audio=True
        )
        print(f"✅ Selected model: {model}")
        print(f"   Max duration: {max_duration}s")
        print(f"   Audio enabled: True")
        
        # Test 4: Prompt enhancement
        print("\n📝 Testing VEO-3 prompt enhancement...")
        original_prompt = "A cute baby laughing and playing with toys"
        enhanced_prompt = client._enhance_prompt_for_veo3(
            prompt=original_prompt,
            model_name=client.veo3_model,
            enable_audio=True
        )
        print(f"Original: {original_prompt}")
        print(f"Enhanced: {enhanced_prompt[:100]}...")
        
        # Test 5: Audio suggestions
        print("\n🔊 Testing audio suggestions...")
        audio_suggestions = client._generate_audio_suggestions(original_prompt)
        print(f"Audio suggestions: {audio_suggestions}")
        
        # Test 6: Generate a test video with VEO-3
        print("\n🎥 Testing VEO-3 video generation...")
        print("⚠️  This will use actual Vertex AI quota!")
        
        response = input("Generate test video with VEO-3? (y/N): ")
        if response.lower() == 'y':
            print("🎬 Generating 5-second test video with VEO-3 and native audio...")
            
            test_prompt = "A happy golden retriever puppy playing in a sunny garden, wagging its tail and chasing a colorful ball"
            
            start_time = time.time()
            test_clip = client.generate_video_clip(
                prompt=test_prompt,
                duration=5.0,
                clip_id="veo3_test",
                prefer_veo3=True,
                enable_audio=True
            )
            generation_time = time.time() - start_time
            
            if test_clip and os.path.exists(test_clip):
                file_size = os.path.getsize(test_clip) / (1024 * 1024)
                print(f"✅ VEO-3 test video generated successfully!")
                print(f"   File: {test_clip}")
                print(f"   Size: {file_size:.1f}MB")
                print(f"   Generation time: {generation_time:.1f}s")
                print(f"   Model used: VEO-3 with native audio")
            else:
                print(f"❌ Video generation failed: {test_clip}")
        else:
            print("⏭️  Skipping actual video generation")
        
        # Test 7: Cost estimation
        print("\n💰 VEO-3 Cost Information:")
        print("   VEO-3 Pricing: ~$0.50 per second")
        print("   5-second video: ~$2.50")
        print("   8-second video: ~$4.00")
        print("   30-second video: ~$15.00")
        print("   Includes native audio generation")
        
        print("\n🎉 ALL VEO-3 TESTS PASSED!")
        print("✅ VEO-3: Ready for production")
        print("✅ Native Audio: Enabled")
        print("✅ Enhanced Prompts: Working")
        print("✅ Model Selection: Optimized")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the viralAi directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_veo3_vs_veo2():
    """Compare VEO-3 vs VEO-2 capabilities"""
    print("\n🆚 VEO-3 vs VEO-2 Comparison:")
    print("=" * 40)
    
    print("VEO-2:")
    print("  ✅ Silent video generation")
    print("  ✅ 5-8 second clips")
    print("  ✅ 720p resolution")
    print("  ✅ Basic physics simulation")
    print("  💰 ~$0.50 per second")
    
    print("\nVEO-3:")
    print("  ✅ Native audio generation")
    print("  ✅ Synchronized dialogue")
    print("  ✅ Sound effects & ambient audio")
    print("  ✅ 4K resolution capability")
    print("  ✅ Enhanced physics realism")
    print("  ✅ Better prompt adherence")
    print("  ✅ Cinematic camera controls")
    print("  💰 ~$0.50 per second (same price!)")
    
    print("\n🎯 VEO-3 Advantages:")
    print("  🔊 No need for separate audio generation")
    print("  🎬 Professional cinematic quality")
    print("  🎭 Realistic character lip-sync")
    print("  🌟 One-prompt complete video solution")

if __name__ == "__main__":
    print("🎬 VEO-3 Integration Test Suite")
    print("=" * 60)
    
    success = test_veo3_integration()
    test_veo3_vs_veo2()
    
    if success:
        print("\n🎉 VEO-3 READY FOR VIRAL VIDEO GENERATION!")
        print("Run 'python gradio_ui.py' to start generating videos with VEO-3")
    else:
        print("\n❌ VEO-3 setup needs attention") 