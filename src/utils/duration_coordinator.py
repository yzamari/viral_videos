"""Duration Coordinator - Manages flexible duration across all components."""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os
import subprocess
import json

logger = logging.getLogger(__name__)


@dataclass
class DurationInfo:
    """Duration information from a component."""
    component: str  # script, audio, video
    requested_duration: float
    actual_duration: float
    confidence: float = 1.0  # How confident the component is in its duration
    

class DurationCoordinator:
    """Coordinates duration across script, audio, and video components with 5% flexibility."""
    
    TOLERANCE_PERCENT = 0.05  # 5% tolerance
    
    def __init__(self, target_duration: float):
        """Initialize with target duration.
        
        Args:
            target_duration: The originally requested duration in seconds
        """
        self.target_duration = target_duration
        self.min_duration = target_duration * (1 - self.TOLERANCE_PERCENT)
        self.max_duration = target_duration * (1 + self.TOLERANCE_PERCENT)
        self.duration_info: List[DurationInfo] = []
        
        logger.info(f"🎯 Duration Coordinator initialized:")
        logger.info(f"   Target: {target_duration}s")
        logger.info(f"   Acceptable range: {self.min_duration:.1f}s - {self.max_duration:.1f}s")
        
    def add_component_duration(self, component: str, requested: float, actual: float, confidence: float = 1.0):
        """Add duration information from a component.
        
        Args:
            component: Component name (script, audio, video)
            requested: What the component requested
            actual: What the component actually produced
            confidence: How confident the component is (0-1)
        """
        info = DurationInfo(component, requested, actual, confidence)
        self.duration_info.append(info)
        
        logger.info(f"📊 {component} duration: requested={requested:.1f}s, actual={actual:.1f}s, confidence={confidence:.1f}")
        
    def get_optimal_duration(self) -> float:
        """Calculate the optimal final duration based on all components.
        
        Returns:
            The optimal duration to use for the final video
        """
        if not self.duration_info:
            return self.target_duration
            
        # Get all actual durations
        durations = [info.actual_duration for info in self.duration_info]
        
        # Use the maximum duration from all components
        max_duration = max(durations)
        
        # Check if it's within tolerance
        if max_duration <= self.max_duration:
            logger.info(f"✅ Using maximum component duration: {max_duration:.1f}s (within tolerance)")
            return max_duration
        else:
            # Cap at max tolerance
            logger.warning(f"⚠️ Maximum duration {max_duration:.1f}s exceeds tolerance, capping at {self.max_duration:.1f}s")
            return self.max_duration
            
    def analyze_audio_files(self, audio_files: List[str]) -> float:
        """Analyze audio files to get total duration.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Total audio duration in seconds
        """
        total_duration = 0.0
        
        for audio_file in audio_files:
            duration = self._get_audio_duration(audio_file)
            if duration:
                total_duration += duration
                
        if total_duration > 0:
            self.add_component_duration("audio", self.target_duration, total_duration, confidence=1.0)
            
        return total_duration
        
    def analyze_video_clips(self, video_clips: List[str]) -> float:
        """Analyze video clips to get total duration.
        
        Args:
            video_clips: List of video clip paths
            
        Returns:
            Total video duration in seconds
        """
        total_duration = 0.0
        
        for clip in video_clips:
            duration = self._get_video_duration(clip)
            if duration:
                total_duration += duration
                
        if total_duration > 0:
            self.add_component_duration("video_clips", self.target_duration, total_duration, confidence=0.9)
            
        return total_duration
        
    def analyze_script_duration(self, script: str, segments: List[Dict]) -> float:
        """Analyze script to estimate duration.
        
        Args:
            script: Full script text
            segments: Script segments with timing
            
        Returns:
            Estimated script duration in seconds
        """
        # Method 1: Word count estimation (2.5 words per second)
        word_count = len(script.split())
        word_based_duration = word_count / 2.5
        
        # Method 2: Segment timing sum
        segment_duration = sum(seg.get('duration', 0) for seg in segments)
        
        # Use the maximum of both methods
        estimated_duration = max(word_based_duration, segment_duration)
        
        if estimated_duration > 0:
            self.add_component_duration("script", self.target_duration, estimated_duration, confidence=0.8)
            
        return estimated_duration
        
    def extend_video_to_duration(self, video_path: str, target_duration: float, output_path: str) -> bool:
        """Extend video to target duration by freezing last frame.
        
        Args:
            video_path: Input video path
            target_duration: Target duration in seconds
            output_path: Output video path
            
        Returns:
            Success status
        """
        try:
            current_duration = self._get_video_duration(video_path)
            if not current_duration:
                logger.error("Could not get video duration")
                return False
                
            if current_duration >= target_duration:
                logger.info(f"Video already {current_duration:.1f}s, no extension needed")
                return False
                
            freeze_duration = target_duration - current_duration
            logger.info(f"🎬 Extending video from {current_duration:.1f}s to {target_duration:.1f}s (freeze last frame for {freeze_duration:.1f}s)")
            
            # Extract last frame
            last_frame_path = output_path.replace('.mp4', '_last_frame.png')
            extract_cmd = [
                'ffmpeg', '-y',
                '-sseof', '-0.1',  # 0.1 seconds from end
                '-i', video_path,
                '-frames:v', '1',
                last_frame_path
            ]
            
            result = subprocess.run(extract_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to extract last frame: {result.stderr}")
                return False
                
            # Create freeze frame video
            freeze_video = output_path.replace('.mp4', '_freeze.mp4')
            freeze_cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', last_frame_path,
                '-c:v', 'libx264',
                '-t', str(freeze_duration),
                '-pix_fmt', 'yuv420p',
                freeze_video
            ]
            
            result = subprocess.run(freeze_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to create freeze frame video: {result.stderr}")
                return False
                
            # Concatenate original video with freeze frame
            concat_file = output_path.replace('.mp4', '_concat.txt')
            with open(concat_file, 'w') as f:
                f.write(f"file '{os.path.abspath(video_path)}'\n")
                f.write(f"file '{os.path.abspath(freeze_video)}'\n")
                
            concat_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                output_path
            ]
            
            result = subprocess.run(concat_cmd, capture_output=True, text=True)
            
            # Clean up temporary files
            for temp_file in [last_frame_path, freeze_video, concat_file]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
            if result.returncode == 0:
                logger.info(f"✅ Successfully extended video to {target_duration:.1f}s")
                return True
            else:
                logger.error(f"Failed to concatenate videos: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error extending video: {e}")
            return False
            
    def get_duration_report(self) -> Dict[str, any]:
        """Get a detailed report of duration analysis.
        
        Returns:
            Dictionary with duration analysis details
        """
        report = {
            "target_duration": self.target_duration,
            "tolerance_range": {
                "min": self.min_duration,
                "max": self.max_duration,
                "tolerance_percent": self.TOLERANCE_PERCENT * 100
            },
            "components": {},
            "optimal_duration": self.get_optimal_duration()
        }
        
        for info in self.duration_info:
            report["components"][info.component] = {
                "requested": info.requested_duration,
                "actual": info.actual_duration,
                "confidence": info.confidence,
                "within_tolerance": self.min_duration <= info.actual_duration <= self.max_duration
            }
            
        return report
        
    def _get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Get duration of an audio file."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None
                
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    return float(stream.get('duration', 0))
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return None
            
    def _get_video_duration(self, video_path: str) -> Optional[float]:
        """Get duration of a video file."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None
                
            data = json.loads(result.stdout)
            return float(data.get('format', {}).get('duration', 0))
            
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return None