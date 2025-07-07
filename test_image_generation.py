#!/usr/bin/env python3
"""
Test Image Generation Fallback
Tests the image generation fallback when VEO-2 quota is exhausted
"""

import sys
import os
sys.path.append('.')

from src.generators.optimized_veo_client import OptimizedVeoClient

def test_image_generation_fallback():
    print('🎬 Testing Image Generation Fallback...')
    print('=' * 50)

    # Create client with invalid API key to force fallback
    client = OptimizedVeoClient('invalid_key_to_force_fallback', 'outputs/test_image_gen')

    # Create simple test prompt
    test_prompts = [
        {
            'veo2_prompt': 'A cute orange cat playing with colorful toys in a bright room',
            'description': 'Cute cat playing with toys',
            'scene_index': 0
        }
    ]

    config = {
        'duration_seconds': 5,
        'target_platform': 'youtube'
    }

    print(f'🎯 Prompt: {test_prompts[0]["description"]}')
    print(f'⏱️ Duration: {config["duration_seconds"]}s')
    print(f'🎨 Gemini Images Available: {client.gemini_images_available}')
    print(f'⚠️ VEO Quota Exhausted: {client.veo_quota_exhausted}')
    print()

    try:
        print('🚀 Starting generation (should trigger fallback chain)...')
        clips = client.generate_optimized_clips(test_prompts, config, 'test_cat_video')
        
        if clips:
            print(f'✅ Generation completed!')
            print(f'🎬 Clips generated: {len(clips)}')
            print()
            
            for i, clip in enumerate(clips):
                print(f'📹 Clip {i+1}:')
                print(f'   Generated with: {clip.get("generated_with", "unknown")}')
                print(f'   File size: {clip.get("file_size_mb", 0):.1f}MB')
                print(f'   Duration: {clip.get("duration", 0)}s')
                
                clip_path = clip.get('clip_path')
                if clip_path and os.path.exists(clip_path):
                    actual_size = os.path.getsize(clip_path) / (1024 * 1024)
                    print(f'   Actual file size: {actual_size:.1f}MB')
                    print(f'   ✅ File exists: {os.path.basename(clip_path)}')
                    
                    # Check what type of fallback was used
                    if actual_size > 0.5:  # If larger than 0.5MB, likely image-based
                        print(f'   🎨 Likely image-based fallback (larger file)')
                    else:
                        print(f'   🎨 Likely colored fallback (smaller file)')
                else:
                    print(f'   ❌ File not found')
                print()
                
            return True
        else:
            print('❌ No clips generated')
            return False
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_image_generation_fallback()
    if success:
        print('🎉 Test completed successfully!')
    else:
        print('💥 Test failed!') 