"""
Simplified Audio Processor
Eliminates audio stuttering by using simple, reliable audio operations.
Replaces complex filter chains that cause artifacts.
"""

import os
import logging
import subprocess
import tempfile
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SimplifiedAudioProcessor:
    """
    Simplified audio processor that eliminates stuttering and artifacts.
    
    PROBLEMS WITH OLD APPROACH:
    - Complex filter chains with adelay, crossfade, normalization
    - Multiple processing steps that introduce artifacts  
    - Crossfade on segments shorter than fade duration
    - Audio normalization during concatenation
    
    NEW APPROACH:
    - Simple file-based concatenation
    - Pre-process normalization individually  
    - No crossfade (eliminates stuttering)
    - Verify audio specs before processing
    """
    
    def __init__(self):
        """Initialize simplified audio processor"""
        self.temp_files = []
        logger.info("🔧 Simplified Audio Processor initialized")
        logger.info("   Strategy: Simple operations, no complex filters")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"🗑️ Cleaned up: {os.path.basename(temp_file)}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup {temp_file}: {e}")
        self.temp_files.clear()
        
    def get_audio_info(self, audio_file: str) -> Dict[str, Any]:
        """
        Get detailed audio file information
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            # Extract relevant stream info
            audio_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
                    
            if not audio_stream:
                raise ValueError(f"No audio stream found in {audio_file}")
                
            return {
                'duration': float(info['format']['duration']),
                'sample_rate': int(audio_stream.get('sample_rate', 44100)),
                'channels': int(audio_stream.get('channels', 2)),
                'codec': audio_stream.get('codec_name', 'unknown'),
                'bit_rate': int(audio_stream.get('bit_rate', 128000)),
                'file': audio_file
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"❌ Failed to get audio info for {audio_file}: {e}")
            return {}
            
    def get_audio_duration(self, audio_file: str) -> float:
        """Get audio duration in seconds"""
        info = self.get_audio_info(audio_file)
        return info.get('duration', 0.0)
        
    def normalize_audio_specs(self, audio_files: List[str]) -> List[str]:
        """
        Normalize all audio files to have the same specs for clean concatenation
        
        This prevents audio artifacts by ensuring consistent:
        - Sample rate (44100 Hz)
        - Channels (2 - stereo)
        - Format (AAC)
        - Bit rate (128k)
        
        Args:
            audio_files: List of input audio files
            
        Returns:
            List of normalized audio files
        """
        logger.info(f"🎚️ Normalizing {len(audio_files)} audio files to consistent specs")
        
        normalized_files = []
        target_sample_rate = 44100
        target_channels = 2
        target_bitrate = "128k"
        
        for i, audio_file in enumerate(audio_files):
            if not os.path.exists(audio_file):
                logger.warning(f"⚠️ Audio file not found: {audio_file}")
                continue
                
            # Check current specs
            info = self.get_audio_info(audio_file)
            if not info:
                logger.warning(f"⚠️ Skipping invalid audio file: {audio_file}")
                continue
            
            current_rate = info.get('sample_rate', 0)
            current_channels = info.get('channels', 0)
            current_duration = info.get('duration', 0)
            
            # Skip zero-duration files
            if current_duration <= 0:
                logger.warning(f"⚠️ Skipping zero-duration file: {audio_file}")
                continue
                
            # Create normalized version
            normalized_file = self._create_temp_file(f"normalized_{i}.aac")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', audio_file,
                '-ar', str(target_sample_rate),  # Sample rate
                '-ac', str(target_channels),     # Channels  
                '-c:a', 'aac',                   # Codec
                '-b:a', target_bitrate,          # Bit rate
                '-avoid_negative_ts', 'make_zero',  # Fix timing issues
                normalized_file
            ]
            
            try:
                self._run_command(cmd, f"Normalizing audio {i+1}/{len(audio_files)}")
                
                # Verify the normalized file
                new_info = self.get_audio_info(normalized_file)
                if new_info and new_info.get('duration', 0) > 0:
                    normalized_files.append(normalized_file)
                    logger.info(f"   ✅ {os.path.basename(audio_file)}: "
                               f"{current_rate}Hz→{target_sample_rate}Hz, "
                               f"{current_channels}ch→{target_channels}ch, "
                               f"{current_duration:.1f}s")
                else:
                    logger.error(f"❌ Normalization failed for {audio_file}")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to normalize {audio_file}: {e}")
                
        logger.info(f"✅ Successfully normalized {len(normalized_files)}/{len(audio_files)} files")
        return normalized_files
        
    def concatenate_audio_simple(self, audio_files: List[str], output_path: str) -> str:
        """
        Simple audio concatenation without complex filters
        
        This eliminates stuttering by:
        1. Normalizing all files to same specs first
        2. Using simple file-based concat (no complex filters)
        3. No crossfade (major cause of stuttering)
        4. No real-time normalization
        
        Args:
            audio_files: List of audio file paths
            output_path: Output file path
            
        Returns:
            Path to concatenated audio file
        """
        logger.info(f"🔗 Simple audio concatenation: {len(audio_files)} files → {output_path}")
        
        if not audio_files:
            raise ValueError("No audio files provided for concatenation")
            
        # Step 1: Normalize all audio files to consistent specs
        normalized_files = self.normalize_audio_specs(audio_files)
        
        if not normalized_files:
            raise ValueError("No valid audio files after normalization")
            
        if len(normalized_files) == 1:
            # Single file - just copy
            logger.info("📄 Single file - copying directly")
            cmd = ['ffmpeg', '-y', '-i', normalized_files[0], '-c', 'copy', output_path]
            self._run_command(cmd, "Copying single audio file")
            return output_path
            
        # Step 2: Create concat demuxer file
        concat_file = self._create_temp_file("concat_list.txt")
        
        with open(concat_file, 'w') as f:
            for audio_file in normalized_files:
                # Use absolute paths to avoid issues
                abs_path = os.path.abspath(audio_file)
                f.write(f"file '{abs_path}'\n")
                
        # Step 3: Simple concatenation using concat demuxer
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',  # Copy streams without re-encoding (prevents artifacts)
            output_path
        ]
        
        self._run_command(cmd, "Simple audio concatenation")
        
        # Step 4: Verify output
        output_info = self.get_audio_info(output_path)
        if output_info:
            output_duration = output_info.get('duration', 0)
            expected_duration = sum(self.get_audio_duration(f) for f in normalized_files)
            logger.info(f"✅ Concatenation complete: {output_duration:.1f}s "
                       f"(expected: {expected_duration:.1f}s)")
        else:
            logger.error("❌ Failed to verify concatenated audio")
            
        return output_path
        
    def add_audio_to_video_simple(self, video_path: str, audio_path: str, output_path: str) -> str:
        """
        Add audio to video with simple mapping
        
        Args:
            video_path: Input video file
            audio_path: Input audio file  
            output_path: Output video file
            
        Returns:
            Path to output video
        """
        logger.info(f"🎬 Adding audio to video: {os.path.basename(video_path)}")
        
        # Get durations
        video_info = self._get_video_info(video_path)
        audio_info = self.get_audio_info(audio_path)
        
        if not video_info or not audio_info:
            raise ValueError("Cannot get video or audio information")
            
        video_duration = video_info.get('duration', 0)
        audio_duration = audio_info.get('duration', 0)
        
        logger.info(f"   Video duration: {video_duration:.1f}s")
        logger.info(f"   Audio duration: {audio_duration:.1f}s")
        
        # Use shortest duration to prevent sync issues
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',        # Copy video stream
            '-c:a', 'aac',         # Re-encode audio for compatibility
            '-b:a', '128k',        # Consistent audio bitrate
            '-map', '0:v:0',       # Map first video stream
            '-map', '1:a:0',       # Map first audio stream
            '-shortest',           # Use shortest stream duration
            output_path
        ]
        
        self._run_command(cmd, "Adding audio to video")
        
        # Verify output
        final_info = self._get_video_info(output_path)
        if final_info:
            final_duration = final_info.get('duration', 0)
            logger.info(f"✅ Final video: {final_duration:.1f}s with audio")
        
        return output_path
        
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video file information"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            return {
                'duration': float(info['format']['duration']),
                'file': video_path
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get video info for {video_path}: {e}")
            return {}
            
    def _create_temp_file(self, suffix: str) -> str:
        """Create a temporary file and track it for cleanup"""
        temp_file = os.path.join(tempfile.gettempdir(), f"simplified_audio_{suffix}")
        self.temp_files.append(temp_file)
        return temp_file
        
    def _run_command(self, cmd: List[str], description: str = "Audio operation"):
        """Run FFmpeg command with error handling"""
        logger.info(f"🔧 {description}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.stderr:
                # FFmpeg writes normal output to stderr, only log if it looks like an error
                if "error" in result.stderr.lower() or "failed" in result.stderr.lower():
                    logger.warning(f"⚠️ FFmpeg stderr: {result.stderr}")
                else:
                    logger.debug(f"FFmpeg output: {result.stderr}")
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Command failed: {e}")
            logger.error(f"Command: {' '.join(cmd)}")
            if e.stderr:
                logger.error(f"Stderr: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timed out: {' '.join(cmd)}")
            raise
            
    def validate_audio_files(self, audio_files: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate audio files and return valid/invalid lists
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Tuple of (valid_files, invalid_files)
        """
        valid_files = []
        invalid_files = []
        
        for audio_file in audio_files:
            if not os.path.exists(audio_file):
                invalid_files.append(f"{audio_file} (not found)")
                continue
                
            if os.path.getsize(audio_file) == 0:
                invalid_files.append(f"{audio_file} (empty file)")
                continue
                
            info = self.get_audio_info(audio_file)
            if not info or info.get('duration', 0) <= 0:
                invalid_files.append(f"{audio_file} (invalid/zero duration)")
                continue
                
            valid_files.append(audio_file)
            
        logger.info(f"📊 Audio validation: {len(valid_files)} valid, {len(invalid_files)} invalid")
        
        if invalid_files:
            logger.warning("⚠️ Invalid audio files:")
            for invalid in invalid_files:
                logger.warning(f"   {invalid}")
                
        return valid_files, invalid_files