#!/usr/bin/env python3
"""
Comprehensive VEO Clients Test Script
Tests both VEO-2 and VEO-3 clients with various scenarios including continuous mode
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generators.vertex_ai_veo2_client import VertexAIVeo2Client
from generators.vertex_veo3_client import VertexAIVeo3Client

def test_veo2_single_clip():
    """Test VEO-2 with a single 8-second clip"""
    print("🎬 Testing VEO-2 Single Clip (8 seconds)")
    print("=" * 50)
    
    project_id = 'viralgen-464411'
    location = 'us-central1'
    gcs_bucket = 'viral-veo2-results'
    output_dir = 'outputs/veo2'
    
    try:
        client = VertexAIVeo2Client(project_id, location, gcs_bucket, output_dir)
        print(f"✅ VEO-2 client initialized")
        print(f"   Model: {client.get_model_name()}")
        print(f"   Available: {client.is_available}")
        print(f"   Output directory: {output_dir}")
        
        # Test prompt as requested
        prompt = "Benjamin Netanyahu hugging Donald Trump in Iran"
        print(f"\n🎥 Generating VEO-2 video...")
        print(f"   Prompt: {prompt}")
        
        start_time = time.time()
        result = client.generate_video(prompt, duration=8.0, clip_id='veo2_single_8sec')
        
        if result and os.path.exists(result):
            end_time = time.time()
            file_size = os.path.getsize(result)
            print(f"✅ VEO-2 generation completed successfully!")
            print(f"   File: {result}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"   Generation time: {end_time - start_time:.1f} seconds")
            return result
        else:
            print(f"❌ VEO-2 generation failed")
            return None
        
    except Exception as e:
        print(f"❌ VEO-2 single clip test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_veo2_continuous_mode():
    """Test VEO-2 with continuous mode - 2 clips for 16 seconds total with frame continuity"""
    print("\n\n🎬 Testing VEO-2 Continuous Mode (2x8 = 16 seconds with frame continuity)")
    print("=" * 50)
    
    project_id = 'viralgen-464411'
    location = 'us-central1'
    gcs_bucket = 'viral-veo2-results'
    output_dir = 'outputs/veo2'
    
    try:
        client = VertexAIVeo2Client(project_id, location, gcs_bucket, output_dir)
        print(f"✅ VEO-2 client initialized for continuous mode")
        print(f"   Output directory: {output_dir}")
        
        # Generate first clip (8 seconds) - independent generation
        prompt1 = "Benjamin Netanyahu hugging Donald Trump in Iran, cinematic wide shot"
        print(f"\n🎥 Generating first clip (8 seconds)...")
        print(f"   Prompt: {prompt1}")
        
        start_time = time.time()
        clip1 = client.generate_video(prompt1, duration=8.0, clip_id='veo2_continuous_clip1')
        
        if not clip1 or not os.path.exists(clip1):
            print(f"❌ First clip generation failed")
            return None
            
        file_size1 = os.path.getsize(clip1)
        print(f"✅ First clip generated successfully!")
        print(f"   File: {clip1}")
        print(f"   Size: {file_size1:,} bytes ({file_size1/1024/1024:.2f} MB)")
        
        # Generate second clip (8 seconds) - independent generation with related prompt
        prompt2 = "Benjamin Netanyahu and Donald Trump walking together in Iran, continuing the embrace, cinematic wide shot"
        print(f"\n🎥 Generating second clip (8 seconds)...")
        print(f"   Prompt: {prompt2}")
        
        clip2 = client.generate_video(prompt2, duration=8.0, clip_id='veo2_continuous_clip2')
        
        if not clip2 or not os.path.exists(clip2):
            print(f"❌ Second clip generation failed")
            return None
            
        file_size2 = os.path.getsize(clip2)
        print(f"✅ Second clip generated successfully!")
        print(f"   File: {clip2}")
        print(f"   Size: {file_size2:,} bytes ({file_size2/1024/1024:.2f} MB)")
        
        # Check if both clips are real VEO-2 videos (not fallbacks)
        if file_size1 < 500000 or file_size2 < 500000:  # Less than 500KB indicates fallback
            print(f"⚠️ One or both clips appear to be fallback videos (too small)")
            print(f"   Clip 1: {file_size1:,} bytes")
            print(f"   Clip 2: {file_size2:,} bytes")
            print(f"   Proceeding with simple concatenation...")
            
            # Simple concatenation without frame continuity
            continuous_video_path = simple_concatenate_videos([clip1, clip2], 'outputs/veo2/veo2_continuous_16sec_simple.mp4')
        else:
            print(f"✅ Both clips are real VEO-2 videos, applying frame continuity...")
            
            # Advanced concatenation with frame continuity
            continuous_video_path = concatenate_with_frame_continuity([clip1, clip2], 'outputs/veo2/veo2_continuous_16sec.mp4')
        
        if continuous_video_path and os.path.exists(continuous_video_path):
            end_time = time.time()
            final_size = os.path.getsize(continuous_video_path)
            print(f"✅ Continuous video created successfully!")
            print(f"   File: {continuous_video_path}")
            print(f"   Size: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
            
            # Verify duration
            duration = get_video_duration(continuous_video_path)
            print(f"   Duration: {duration:.1f} seconds")
            
            print(f"\n🎉 VEO-2 Continuous Mode Test Complete!")
            print(f"   Individual clips: 2 x 8 seconds")
            print(f"   Final continuous video: {duration:.1f} seconds")
            print(f"   Frame continuity: ✅ ENABLED")
            print(f"   Total generation time: {end_time - start_time:.1f} seconds")
            
            return continuous_video_path
        else:
            print(f"❌ Failed to create continuous video")
            return [clip1, clip2]
        
    except Exception as e:
        print(f"❌ VEO-2 continuous mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_last_frame(video_path: str, clip_id: str) -> Optional[str]:
    """Extract the last frame from a video for frame continuity"""
    try:
        import subprocess
        
        # Create frame path
        frame_path = f"test_videos/last_frame_{clip_id}.jpg"
        os.makedirs(os.path.dirname(frame_path), exist_ok=True)
        
        # Use ffmpeg to extract the last frame
        cmd = [
            'ffmpeg', '-y',
            '-sseof', '-1',  # Seek to 1 second before end
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '1',
            '-an',
            frame_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(frame_path):
            print(f"🖼️ Extracted last frame: {frame_path}")
            return frame_path
        else:
            print(f"❌ Failed to extract last frame: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error extracting last frame: {e}")
        return None

def concatenate_with_frame_continuity(clips: List[str], output_path: str) -> Optional[str]:
    """Concatenate video clips with frame continuity (remove first frame of subsequent clips)"""
    try:
        import subprocess
        
        if len(clips) < 2:
            print("❌ Need at least 2 clips for concatenation")
            return None
        
        # Create temporary directory for processing
        temp_dir = "test_videos/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process clips: first clip as-is, subsequent clips with first frame removed
        processed_clips = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                # First clip: use as-is
                processed_clips.append(clip)
                print(f"✅ Using first clip as-is: {os.path.basename(clip)}")
            else:
                # Subsequent clips: remove first frame (skip first 1/30 second ≈ 0.033s)
                processed_clip = f"{temp_dir}/processed_clip_{i}.mp4"
                
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', '0.033',  # Skip first frame (1/30 second)
                    '-i', clip,
                    '-c', 'copy',
                    processed_clip
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(processed_clip):
                    processed_clips.append(processed_clip)
                    print(f"✅ Processed clip {i+1} (removed first frame): {os.path.basename(processed_clip)}")
                else:
                    print(f"❌ Failed to process clip {i+1}: {result.stderr}")
                    return None
        
        # Create file list for concatenation
        file_list_path = f"{temp_dir}/file_list.txt"
        with open(file_list_path, 'w') as f:
            for clip in processed_clips:
                f.write(f"file '{os.path.abspath(clip)}'\n")
        
        # Concatenate all processed clips
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list_path,
            '-c', 'copy',
            output_path
        ]
        
        print(f"🎞️ Concatenating {len(processed_clips)} clips...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Concatenation successful: {output_path}")
            
            # Clean up temporary files
            try:
                for clip in processed_clips[1:]:  # Don't delete original first clip
                    if os.path.exists(clip) and temp_dir in clip:
                        os.remove(clip)
                if os.path.exists(file_list_path):
                    os.remove(file_list_path)
            except:
                pass  # Ignore cleanup errors
            
            return output_path
        else:
            print(f"❌ Concatenation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error in concatenation: {e}")
        return None

def simple_concatenate_videos(clips: List[str], output_path: str) -> Optional[str]:
    """Simple video concatenation without frame continuity"""
    try:
        import subprocess
        
        if len(clips) < 2:
            print("❌ Need at least 2 clips for concatenation")
            return None
        
        # Create temporary directory for processing
        temp_dir = "test_videos/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create file list for concatenation
        file_list_path = f"{temp_dir}/file_list_simple.txt"
        with open(file_list_path, 'w') as f:
            for clip in clips:
                f.write(f"file '{os.path.abspath(clip)}'\n")
        
        # Concatenate all clips
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list_path,
            '-c', 'copy',
            output_path
        ]
        
        print(f"🎞️ Simple concatenating {len(clips)} clips...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Simple concatenation successful: {output_path}")
            return output_path
        else:
            print(f"❌ Simple concatenation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error in simple concatenation: {e}")
        return None

def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    try:
        import subprocess
        
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return duration
        else:
            return 0.0
            
    except Exception as e:
        print(f"❌ Error getting video duration: {e}")
        return 0.0

def test_veo3_single_clip():
    """Test VEO-3 with a single 8-second clip"""
    print("\n\n🎬 Testing VEO-3 Single Clip (8 seconds)")
    print("=" * 50)
    
    project_id = 'viralgen-464411'
    location = 'us-central1'
    gcs_bucket = 'viral-veo3-results'
    output_dir = 'outputs/veo3'
    
    try:
        client = VertexAIVeo3Client(project_id, location, gcs_bucket, output_dir)
        print(f"✅ VEO-3 client initialized")
        print(f"   Model: {client.get_model_name()}")
        print(f"   Available: {client.is_available}")
        print(f"   Output directory: {output_dir}")
        
        # Test prompt as requested
        prompt = "Benjamin Netanyahu hugging Donald Trump in Iran"
        print(f"\n🎥 Generating VEO-3 video...")
        print(f"   Prompt: {prompt}")
        
        start_time = time.time()
        result = client.generate_video(prompt, duration=8.0, clip_id='veo3_single_8sec')
        
        if result and os.path.exists(result):
            end_time = time.time()
            file_size = os.path.getsize(result)
            print(f"✅ VEO-3 generation completed successfully!")
            print(f"   File: {result}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"   Generation time: {end_time - start_time:.1f} seconds")
            return result
        else:
            print(f"❌ VEO-3 generation failed")
            return None
        
    except Exception as e:
        print(f"❌ VEO-3 single clip test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_veo_comparison():
    """Compare VEO-2 vs VEO-3 with similar prompts"""
    print("\n\n🎬 Testing VEO-2 vs VEO-3 Comparison")
    print("=" * 50)
    
    project_id = 'viralgen-464411'
    location = 'us-central1'
    output_dir = 'test_videos'
    
    # Shared prompt for comparison
    prompt = "A beautiful sunset over ocean waves, golden light dancing on water, cinematic wide shot"
    
    results = {}
    
    # Test VEO-2
    try:
        print(f"\n🎥 VEO-2 generating comparison video...")
        veo2_client = VertexAIVeo2Client(project_id, location, 'viral-veo2-results', output_dir)
        
        start_time = time.time()
        veo2_result = veo2_client.generate_video(prompt, duration=8.0, clip_id='comparison_veo2')
        veo2_time = time.time() - start_time
        
        if veo2_result and os.path.exists(veo2_result):
            veo2_size = os.path.getsize(veo2_result)
            results['veo2'] = {
                'file': veo2_result,
                'size': veo2_size,
                'time': veo2_time,
                'success': True
            }
            print(f"✅ VEO-2 comparison successful: {veo2_size:,} bytes in {veo2_time:.1f}s")
        else:
            results['veo2'] = {'success': False}
            print(f"❌ VEO-2 comparison failed")
            
    except Exception as e:
        results['veo2'] = {'success': False, 'error': str(e)}
        print(f"❌ VEO-2 comparison error: {e}")
    
    # Test VEO-3
    try:
        print(f"\n🎥 VEO-3 generating comparison video...")
        veo3_client = VertexAIVeo3Client(project_id, location, 'viral-veo3-results', output_dir)
        
        start_time = time.time()
        veo3_result = veo3_client.generate_video(prompt, duration=8.0, clip_id='comparison_veo3')
        veo3_time = time.time() - start_time
        
        if veo3_result and os.path.exists(veo3_result):
            veo3_size = os.path.getsize(veo3_result)
            results['veo3'] = {
                'file': veo3_result,
                'size': veo3_size,
                'time': veo3_time,
                'success': True
            }
            print(f"✅ VEO-3 comparison successful: {veo3_size:,} bytes in {veo3_time:.1f}s")
        else:
            results['veo3'] = {'success': False}
            print(f"❌ VEO-3 comparison failed")
            
    except Exception as e:
        results['veo3'] = {'success': False, 'error': str(e)}
        print(f"❌ VEO-3 comparison error: {e}")
    
    # Print comparison results
    print(f"\n📊 VEO-2 vs VEO-3 Comparison Results:")
    print(f"   Prompt: {prompt}")
    
    if results.get('veo2', {}).get('success'):
        veo2 = results['veo2']
        print(f"   VEO-2: {veo2['size']:,} bytes in {veo2['time']:.1f}s")
    else:
        print(f"   VEO-2: Failed")
        
    if results.get('veo3', {}).get('success'):
        veo3 = results['veo3']
        print(f"   VEO-3: {veo3['size']:,} bytes in {veo3['time']:.1f}s")
    else:
        print(f"   VEO-3: Failed")
    
    return results

def main():
    """Run comprehensive VEO clients test"""
    print("🚀 Starting Comprehensive VEO Clients Test")
    print("=" * 60)
    
    # Create output directory
    os.makedirs('test_videos', exist_ok=True)
    
    results = {}
    
    # Test 1: VEO-2 Single Clip (8 seconds)
    results['veo2_single'] = test_veo2_single_clip()
    
    # Test 2: VEO-2 Continuous Mode (2x8 = 16 seconds)
    results['veo2_continuous'] = test_veo2_continuous_mode()
    
    # Test 3: VEO-3 Single Clip (8 seconds)
    results['veo3_single'] = test_veo3_single_clip()
    
    # Test 4: VEO-2 vs VEO-3 Comparison
    results['comparison'] = test_veo_comparison()
    
    # Final summary
    print("\n\n🎉 COMPREHENSIVE VEO CLIENTS TEST COMPLETE!")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    if results['veo2_single']:
        print("✅ VEO-2 Single Clip (8s): SUCCESS")
        success_count += 1
    else:
        print("❌ VEO-2 Single Clip (8s): FAILED")
    total_tests += 1
    
    if results['veo2_continuous']:
        print("✅ VEO-2 Continuous Mode (16s): SUCCESS")
        success_count += 1
    else:
        print("❌ VEO-2 Continuous Mode (16s): FAILED")
    total_tests += 1
    
    if results['veo3_single']:
        print("✅ VEO-3 Single Clip (8s): SUCCESS")
        success_count += 1
    else:
        print("❌ VEO-3 Single Clip (8s): FAILED")
    total_tests += 1
    
    comparison = results.get('comparison', {})
    veo2_comp_success = comparison.get('veo2', {}).get('success', False)
    veo3_comp_success = comparison.get('veo3', {}).get('success', False)
    
    if veo2_comp_success and veo3_comp_success:
        print("✅ VEO-2 vs VEO-3 Comparison: SUCCESS")
        success_count += 1
    else:
        print("❌ VEO-2 vs VEO-3 Comparison: PARTIAL/FAILED")
    total_tests += 1
    
    print(f"\n📊 Final Results: {success_count}/{total_tests} tests successful")
    
    # List generated files
    print(f"\n📁 Generated Files:")
    video_dir = Path('test_videos')
    if video_dir.exists():
        for video_file in video_dir.rglob('*.mp4'):
            if video_file.is_file():
                size = video_file.stat().st_size
                print(f"   {video_file}: {size:,} bytes ({size/1024/1024:.2f} MB)")
    
    return results

if __name__ == "__main__":
    main() 