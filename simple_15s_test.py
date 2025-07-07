#!/usr/bin/env python3
"""
Simple 15-second video generator without ImageMagick dependencies
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from moviepy.editor import ColorClip, concatenate_videoclips, AudioFileClip, VideoFileClip
from gtts import gTTS
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_simple_15s_video():
    """Create a simple 15-second video with proper audio"""
    
    logger.info("🎬 Creating simple 15-second video...")
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"outputs/simple_test_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Create exactly 15 seconds of TTS audio
    # Using fewer words for better timing (2 words/second = 30 words for 15s)
    script = "Hey everyone! Check out this amazing test video. The quality is perfect now, with smooth visuals and clear natural audio. This is exactly fifteen seconds long. Enjoy watching!"
    
    word_count = len(script.split())
    logger.info(f"📝 Script: {word_count} words")
    
    # Generate audio with gTTS
    audio_path = os.path.join(output_dir, "audio.mp3")
    tts = gTTS(text=script, lang='en', slow=False)
    tts.save(audio_path)
    
    # Check audio duration
    from mutagen.mp3 import MP3
    audio_info = MP3(audio_path)
    audio_duration = audio_info.info.length
    logger.info(f"🎤 Audio duration: {audio_duration:.1f}s")
    
    # Step 2: Create video scenes (5 seconds each, 3 scenes = 15 seconds)
    scenes = []
    colors = [(0, 0, 255), (0, 255, 0), (128, 0, 128)]  # Blue, Green, Purple in RGB
    
    for i, color in enumerate(colors):
        logger.info(f"🎨 Creating scene {i+1}: RGB{color}")
        scene = ColorClip(size=(1280, 720), color=color, duration=5.0)
        scenes.append(scene)
    
    # Concatenate scenes
    video = concatenate_videoclips(scenes)
    logger.info(f"📹 Video duration: {video.duration}s")
    
    # Step 3: Add audio to video
    video = video.set_audio(AudioFileClip(audio_path))
    
    # Step 4: Ensure exactly 15 seconds
    target_duration = 15.0
    if video.duration != target_duration:
        if video.duration > target_duration:
            video = video.subclip(0, target_duration)
        else:
            # Extend with last frame
            extension_duration = target_duration - video.duration
            last_frame = video.to_ImageClip(t=video.duration-0.1).set_duration(extension_duration)
            video = concatenate_videoclips([video, last_frame])
    
    # Step 5: Export final video
    output_path = os.path.join(output_dir, "final_15s_video.mp4")
    logger.info("💾 Rendering final video...")
    
    video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        threads=4,
        logger=None,  # Suppress MoviePy output
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    # Cleanup
    video.close()
    
    # Verify final duration
    final_video = VideoFileClip(output_path)
    final_duration = final_video.duration
    final_video.close()
    
    logger.info(f"✅ Video created successfully!")
    logger.info(f"📁 Location: {output_path}")
    logger.info(f"⏱️  Duration: {final_duration:.1f}s")
    
    return output_path, final_duration

if __name__ == "__main__":
    print("\n🎬 Simple 15-Second Video Generator")
    print("=" * 50)
    print("✅ No ImageMagick required")
    print("✅ Natural audio with gTTS")
    print("✅ Exactly 15 seconds duration")
    print("=" * 50)
    
    try:
        video_path, duration = create_simple_15s_video()
        print(f"\n✅ SUCCESS!")
        print(f"📁 Video saved to: {video_path}")
        print(f"⏱️  Final duration: {duration:.1f} seconds")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 