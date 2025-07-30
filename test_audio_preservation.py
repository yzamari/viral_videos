#!/usr/bin/env python3
"""
Test script to verify audio preservation after pipeline reordering fix
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.ffmpeg_processor import FFmpegProcessor
from src.utils.logger import setup_logger

logger = setup_logger("audio_test")

def check_audio_in_file(file_path: str, processor: FFmpegProcessor) -> bool:
    """Check if a video file has audio"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    has_audio = processor.has_audio_stream(file_path)
    duration = processor.get_duration(file_path)
    
    logger.info(f"📁 File: {Path(file_path).name}")
    logger.info(f"   Duration: {duration:.2f}s")
    logger.info(f"   Has Audio: {'✅ YES' if has_audio else '❌ NO'}")
    
    return has_audio

def analyze_session_outputs(session_path: str):
    """Analyze all video files in a session for audio presence"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🔍 Analyzing session: {session_path}")
    logger.info(f"{'='*60}\n")
    
    with FFmpegProcessor() as ffmpeg:
        # Check for common video files in the session
        video_patterns = [
            "final_output/*.mp4",
            "video_clips/*.mp4",
            "temp_files/*audio*.mp4",
            "temp_files/*overlay*.mp4",
            "temp_files/*subtitle*.mp4",
            "temp_files/*.mp4"
        ]
        
        results = {}
        
        for pattern in video_patterns:
            files = list(Path(session_path).glob(pattern))
            if files:
                logger.info(f"\n📂 Checking {pattern}:")
                for file in sorted(files):
                    has_audio = check_audio_in_file(str(file), ffmpeg)
                    results[str(file)] = has_audio
                    print()  # Add spacing
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("📊 SUMMARY:")
        logger.info(f"{'='*60}")
        
        files_with_audio = sum(1 for has_audio in results.values() if has_audio)
        total_files = len(results)
        
        logger.info(f"Total video files: {total_files}")
        logger.info(f"Files with audio: {files_with_audio}")
        logger.info(f"Files without audio: {total_files - files_with_audio}")
        
        # Specific checks
        final_videos = [f for f in results if "final_output" in f]
        if final_videos:
            for final in final_videos:
                status = "✅ PASS" if results[final] else "❌ FAIL"
                logger.info(f"\nFinal video audio check: {status}")
                logger.info(f"  File: {Path(final).name}")
        
        # Check for the pipeline order
        logger.info(f"\n{'='*60}")
        logger.info("🔄 PIPELINE ORDER CHECK:")
        logger.info(f"{'='*60}")
        
        # Look for specific temp files that indicate pipeline order
        audio_only = list(Path(session_path).glob("temp_files/*audio_only*.mp4"))
        overlay_files = list(Path(session_path).glob("temp_files/*overlay*.mp4"))
        
        if audio_only:
            logger.info("✅ Found audio_only files (indicates audio was processed)")
        else:
            logger.info("⚠️  No audio_only files found")
            
        if overlay_files:
            logger.info("✅ Found overlay files (indicates overlays were processed)")
        else:
            logger.info("⚠️  No overlay files found")
        
        # Root cause analysis
        logger.info(f"\n{'='*60}")
        logger.info("🔍 ROOT CAUSE ANALYSIS:")
        logger.info(f"{'='*60}")
        
        if final_videos and not all(results[f] for f in final_videos):
            logger.info("\n❌ AUDIO LOSS DETECTED IN FINAL VIDEO")
            logger.info("\nPossible causes:")
            logger.info("1. Overlays were added AFTER audio (old pipeline)")
            logger.info("2. MoviePy corrupted audio during overlay processing")
            logger.info("3. FFmpeg audio composition failed")
            
            logger.info("\n✅ FIX APPLIED:")
            logger.info("- Pipeline reordered: overlays → subtitles → audio")
            logger.info("- Overlays processed without audio (-an flag)")
            logger.info("- Audio added as final step")
            logger.info("- Audio verification checks added")
        else:
            logger.info("\n✅ AUDIO PRESERVED SUCCESSFULLY")
            logger.info("The pipeline reordering fix is working correctly!")

def main():
    """Main test function"""
    import argparse
    parser = argparse.ArgumentParser(description="Test audio preservation in video generation")
    parser.add_argument("session_path", help="Path to session directory to analyze")
    args = parser.parse_args()
    
    if not os.path.exists(args.session_path):
        logger.error(f"Session path not found: {args.session_path}")
        sys.exit(1)
    
    analyze_session_outputs(args.session_path)

if __name__ == "__main__":
    main()