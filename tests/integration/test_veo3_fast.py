#!/usr/bin/env python3
"""
Test VEO-3 Fast Integration
"""
import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.veo_client_factory import VeoClientFactory, VeoModel
from src.utils.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)

def test_veo3_fast():
    """Test VEO-3 Fast video generation"""
    print("\n🚀 Testing VEO-3 Fast Integration\n")
    
    # Create output directory
    output_dir = "test_veo3_fast_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize VEO client factory
    factory = VeoClientFactory()
    
    # Create VEO-3 Fast client
    try:
        print("📦 Creating VEO-3 Fast client...")
        client = factory.create_client(VeoModel.VEO3_FAST, output_dir)
        
        if not client:
            print("❌ Failed to create VEO-3 Fast client")
            return False
            
        print(f"✅ Created client: {client.get_model_name()}")
        
        # Test video generation
        test_prompt = (
            "A serene sunrise over mountain peaks with golden light "
            "spreading across the landscape, birds flying in the distance, "
            "cinematic quality, 4K resolution"
        )
        
        print(f"\n🎬 Generating test video...")
        print(f"   Prompt: {test_prompt[:50]}...")
        print(f"   Duration: 5 seconds")
        print(f"   Aspect Ratio: 16:9")
        
        video_path = client.generate_video(
            prompt=test_prompt,
            duration=5.0,
            clip_id="test_veo3_fast",
            aspect_ratio="16:9",
            enable_audio=False  # VEO-3 Fast doesn't support audio
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"\n✅ VEO-3 Fast test successful!")
            print(f"   Video path: {video_path}")
            print(f"   File size: {file_size:.2f} MB")
            
            # Test with best available client to confirm VEO-3 Fast is selected
            print(f"\n🔍 Testing best available client selection...")
            best_client = factory.get_best_available_client(output_dir)
            if best_client:
                model_name = best_client.get_model_name()
                print(f"✅ Best available model: {model_name}")
                if "fast" in model_name.lower():
                    print(f"✅ VEO-3 Fast is correctly selected as best model!")
                    return True
            
            return True
        else:
            print(f"\n❌ VEO-3 Fast test failed - no video generated")
            return False
            
    except Exception as e:
        print(f"\n❌ VEO-3 Fast test failed with error: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run the test
    success = test_veo3_fast()
    
    if success:
        print("\n🎉 VEO-3 Fast integration successful! Ready to use as default.")
        sys.exit(0)
    else:
        print("\n⚠️  VEO-3 Fast integration needs debugging.")
        sys.exit(1)