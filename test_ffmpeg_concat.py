#!/usr/bin/env python3
"""Direct test of FFmpeg concatenation"""

import os
import subprocess
import tempfile
import shutil

def create_test_clip(output_path, duration, text):
    """Create a simple test video clip with text"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=blue:s=1080x1920:d={duration}",
        "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path

def test_concat():
    """Test concatenation directly"""
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="concat_test_")
    print(f"Working in: {temp_dir}")
    
    try:
        # Create test clips
        clips = []
        total_expected = 0
        
        for i in range(5):
            clip_duration = 12  # 12 seconds each = 60 total
            clip_path = os.path.join(temp_dir, f"clip_{i}.mp4")
            create_test_clip(clip_path, clip_duration, f"Clip {i+1}")
            clips.append(clip_path)
            total_expected += clip_duration
            
            # Verify clip
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                         '-of', 'default=noprint_wrappers=1:nokey=1', clip_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            actual_duration = float(result.stdout.strip()) if result.returncode == 0 else 0
            print(f"  Clip {i+1}: {actual_duration:.1f}s")
        
        print(f"\nTotal expected duration: {total_expected}s")
        
        # Create concat file
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, "w") as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        print(f"\nConcat file contents:")
        with open(concat_file, "r") as f:
            print(f.read())
        
        # Concatenate
        output_path = os.path.join(temp_dir, "output.mp4")
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",  # Try copy first
            output_path
        ]
        
        print(f"\nRunning concat command...")
        result = subprocess.run(concat_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            
            # Try re-encoding instead
            print("\nTrying with re-encoding...")
            concat_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-preset", "fast",
                output_path
            ]
            subprocess.run(concat_cmd, check=True, capture_output=True)
        
        # Check output duration
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', output_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        output_duration = float(result.stdout.strip()) if result.returncode == 0 else 0
        
        print(f"\n✅ Output video duration: {output_duration:.1f}s")
        
        if abs(output_duration - total_expected) < 1.0:
            print("✅ Concatenation successful!")
        else:
            print(f"❌ Duration mismatch! Expected {total_expected}s, got {output_duration:.1f}s")
            
            # Debug: Check each clip again
            print("\nRechecking clips:")
            for i, clip in enumerate(clips):
                probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                             '-of', 'default=noprint_wrappers=1:nokey=1', clip]
                result = subprocess.run(probe_cmd, capture_output=True, text=True)
                dur = float(result.stdout.strip()) if result.returncode == 0 else 0
                print(f"  Clip {i+1}: {dur:.1f}s - {clip}")
        
        # Keep output for inspection
        final_path = "/tmp/test_concat_output.mp4"
        shutil.copy(output_path, final_path)
        print(f"\nOutput saved to: {final_path}")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_concat()