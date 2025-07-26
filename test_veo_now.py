#!/usr/bin/env python3
"""
Test VEO video generation RIGHT NOW
"""

import asyncio
import os
from src.generators.veo_client_factory import VeoClientFactory


async def test_veo_generation():
    """Test actual VEO video generation"""
    try:
        print("🚀 Starting VEO test...")
        
        # Create output directory
        output_dir = "outputs/veo_test_now"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create VEO factory
        factory = VeoClientFactory()
        
        # Get VEO client
        client = factory.get_best_available_client(output_dir)
        
        if not client:
            print("❌ No VEO client available!")
            return False
        
        print(f"✅ VEO client created: {client.get_model_name()}")
        
        # Generate a test video
        prompt = "A beautiful sunrise over mountains, cinematic style, high quality"
        duration = 3  # seconds
        
        print(f"🎬 Generating {duration}s video...")
        print(f"📝 Prompt: {prompt}")
        
        try:
            video_path = await client.generate_video(
                prompt=prompt,
                duration=duration,
                aspect_ratio="16:9"
            )
            
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                print(f"✅ Video generated successfully!")
                print(f"📁 Path: {video_path}")
                print(f"📊 Size: {file_size:.2f} MB")
                return True
            else:
                print(f"❌ Video generation failed - no file created")
                return False
                
        except Exception as e:
            print(f"❌ Video generation error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_veo_generation())
    exit(0 if success else 1)