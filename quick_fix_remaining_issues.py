#!/usr/bin/env python3
"""
Quick fix script for remaining video generation issues
"""

import os
import re

def fix_video_generator():
    """Fix all issues in video_generator.py"""
    
    file_path = "src/generators/video_generator.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Add Language import
    if "from src.models.video_models import" in content:
        content = content.replace(
            "from src.models.video_models import (GeneratedVideoConfig, Platform, VideoCategory,",
            "from src.models.video_models import (GeneratedVideoConfig, Platform, VideoCategory, Language,"
        )
    
    # Fix 2: Fix VEO client parameter name
    content = content.replace(
        "duration_seconds=int(clip_duration),",
        "duration=int(clip_duration),"
    )
    
    # Fix 3: Add fps to all write_videofile calls
    content = re.sub(
        r'write_videofile\(([^)]+)\)',
        lambda m: f'write_videofile({m.group(1)}, fps=24)' if 'fps=' not in m.group(1) else m.group(0),
        content
    )
    
    # Fix 4: Fix TTS method call
    old_tts_pattern = r'audio_path = self\.tts_client\.generate_tts\([^)]+\)'
    new_tts_call = """audio_files = self.tts_client.generate_intelligent_voice_audio(
                        script=segment.get('text', ''),
                        language=Language.EN_US,
                        topic=config.topic,
                        platform=config.target_platform,
                        category=config.category,
                        duration_seconds=int(segment.get('duration', 5)),
                        num_clips=len(segments),
                        clip_index=i
                    )
                    
                    # Use the first audio file if multiple are returned
                    if audio_files and len(audio_files) > 0:
                        audio_path = audio_files[0]
                    else:
                        audio_path = None"""
    
    content = re.sub(old_tts_pattern, new_tts_call, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed video_generator.py")

def fix_test_file():
    """Fix the E2E test file"""
    
    file_path = "test_complete_e2e_system.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix VideoGenerationResult access
    content = content.replace(
        "if result and result.get('success'):",
        "if result and result.success:"
    )
    
    content = content.replace(
        "result.get('video_path', 'N/A')",
        "result.file_path"
    )
    
    content = content.replace(
        "result.get('audio_path', 'N/A')",
        "', '.join(result.audio_files) if result.audio_files else 'N/A'"
    )
    
    content = content.replace(
        "result.get('script', 'N/A')[:100]",
        "result.script[:100]"
    )
    
    content = content.replace(
        "result.get('duration', 'N/A')",
        "result.generation_time_seconds"
    )
    
    content = content.replace(
        "result.get('error', 'Unknown error')",
        "result.error_message if result else 'Unknown error'"
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed test_complete_e2e_system.py")

if __name__ == '__main__':
    print("🔧 Applying quick fixes...")
    fix_video_generator()
    fix_test_file()
    print("🎉 All fixes applied!") 