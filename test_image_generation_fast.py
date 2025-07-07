#!/usr/bin/env python3
"""
Fast Test for Image Generation Fallback
Forces immediate fallback to image generation
"""

import sys
import os
sys.path.append('.')

from src.generators.optimized_veo_client import OptimizedVeoClient

def test_image_generation_fast():
    print('🎬 Fast Image Generation Fallback Test...')
    print('=' * 50)

    # Create client with invalid API key
    client = OptimizedVeoClient('invalid_key', 'outputs/test_image_fast')
    
    # Force quota exhausted to skip VEO attempts
    client.veo_quota_exhausted = True
    
    print(f'🎨 Gemini Images Available: {client.gemini_images_available}')
    print(f'⚠️ VEO Quota Exhausted (forced): {client.veo_quota_exhausted}')
    print()

    # Test the image fallback method directly
    try:
        print('🚀 Testing image fallback directly...')
        
        prompt = "A cute orange cat playing with colorful toys in a bright room"
        duration = 5.0
        clip_id = "test_cat_clip"
        output_path = "outputs/test_image_fast/test_clip.mp4"
        
        print(f'📝 Prompt: {prompt}')
        print(f'⏱️ Duration: {duration}s')
        print()
        
        # Test the _generate_image_fallback method directly
        result_path = client._generate_image_fallback(prompt, duration, clip_id, output_path)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path) / (1024 * 1024)
            print(f'✅ Image fallback completed!')
            print(f'📁 File: {os.path.basename(result_path)}')
            print(f'📊 File size: {file_size:.1f}MB')
            
            # Analyze the result
            if file_size > 0.5:
                print(f'🎨 SUCCESS: Large file indicates image-based generation!')
            else:
                print(f'🎨 FALLBACK: Small file indicates colored fallback')
                
            # Check video properties
            print(f'\n📹 Checking video properties...')
            os.system(f'ffprobe -v quiet -print_format json -show_format "{result_path}" | grep duration')
            
            return True
        else:
            print(f'❌ Image fallback failed - no file created')
            return False
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_image_generation_fast()
    if success:
        print('\n🎉 Fast test completed successfully!')
    else:
        print('\n💥 Fast test failed!') 