"""
Audio Duration Manager - Validates and manages audio durations
Ensures audio duration matches target video duration with quality gates
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from moviepy.editor import AudioFileClip
import numpy as np

from ..utils.logging_config import get_logger
from ..config import video_config

logger = get_logger(__name__)


@dataclass
class AudioDurationAnalysis:
    """Analysis result for audio duration validation"""
    total_duration: float
    target_duration: float
    segment_durations: List[float]
    is_within_tolerance: bool
    tolerance_percent: float
    duration_difference: float
    duration_ratio: float
    recommendation: str
    segments_info: List[Dict[str, Any]]
    quality_score: float
    must_regenerate: bool


class AudioDurationManager:
    """Manages audio duration validation and adjustment"""
    
    def __init__(self):
        """Initialize Audio Duration Manager"""
        # Get tolerance from config
        self.tolerance_percent = video_config.audio.duration_tolerance_percent
        self.min_segment_duration = video_config.audio.min_segment_duration
        self.max_segment_duration = video_config.audio.max_segment_duration
        self.padding_between_segments = video_config.audio.padding_between_segments
        
        logger.info(f"✅ Audio Duration Manager initialized")
        logger.info(f"   Tolerance: ±{self.tolerance_percent}%")
        logger.info(f"   Min segment duration: {self.min_segment_duration}s")
        logger.info(f"   Max segment duration: {self.max_segment_duration}s")
        logger.info(f"   Padding between segments: {self.padding_between_segments}s")
    
    def analyze_audio_files(self, audio_files: List[str], target_duration: float) -> AudioDurationAnalysis:
        """
        Analyze audio files and validate against target duration
        
        Args:
            audio_files: List of audio file paths
            target_duration: Target video duration in seconds
            
        Returns:
            AudioDurationAnalysis with validation results
        """
        logger.info(f"🔍 Analyzing {len(audio_files)} audio files against target duration {target_duration}s")
        
        # Analyze each audio file
        segments_info = []
        segment_durations = []
        total_duration = 0.0
        
        for i, audio_file in enumerate(audio_files):
            if not os.path.exists(audio_file):
                logger.warning(f"⚠️ Audio file not found: {audio_file}")
                continue
                
            try:
                # Get audio duration
                with AudioFileClip(audio_file) as audio:
                    duration = audio.duration
                    
                segment_info = {
                    'index': i,
                    'file': os.path.basename(audio_file),
                    'duration': duration,
                    'is_too_short': duration < self.min_segment_duration,
                    'is_too_long': duration > self.max_segment_duration,
                    'quality_issues': []
                }
                
                # Check for quality issues
                if segment_info['is_too_short']:
                    segment_info['quality_issues'].append(
                        f"Too short ({duration:.1f}s < {self.min_segment_duration}s)"
                    )
                if segment_info['is_too_long']:
                    segment_info['quality_issues'].append(
                        f"Too long ({duration:.1f}s > {self.max_segment_duration}s)"
                    )
                
                segments_info.append(segment_info)
                segment_durations.append(duration)
                total_duration += duration
                
            except Exception as e:
                logger.error(f"❌ Error analyzing audio file {audio_file}: {e}")
        
        # Add padding duration if multiple segments
        if len(segment_durations) > 1:
            padding_total = self.padding_between_segments * (len(segment_durations) - 1)
            total_duration += padding_total
            logger.info(f"   Added {padding_total:.2f}s padding for {len(segment_durations)-1} gaps")
        
        # Calculate tolerance range
        tolerance_range = target_duration * (self.tolerance_percent / 100)
        min_duration = target_duration - tolerance_range
        max_duration = target_duration + tolerance_range
        
        # Check if within tolerance
        is_within_tolerance = min_duration <= total_duration <= max_duration
        duration_difference = total_duration - target_duration
        duration_ratio = total_duration / target_duration if target_duration > 0 else 0
        
        # Calculate quality score (0-1)
        quality_issues_count = sum(len(s['quality_issues']) for s in segments_info)
        duration_penalty = abs(duration_difference) / target_duration
        quality_score = max(0, 1 - (quality_issues_count * 0.1 + duration_penalty))
        
        # Determine if must regenerate
        must_regenerate = (
            not is_within_tolerance or
            duration_ratio < 0.8 or  # Less than 80% of target
            duration_ratio > 1.2 or  # More than 120% of target
            quality_score < 0.6      # Poor quality
        )
        
        # Generate recommendation
        if is_within_tolerance and quality_score >= 0.8:
            recommendation = "Audio duration is optimal - proceed with video generation"
        elif must_regenerate:
            if total_duration < min_duration:
                recommendation = f"Audio is {abs(duration_difference):.1f}s too short - MUST regenerate with slower speech or more content"
            elif total_duration > max_duration:
                recommendation = f"Audio is {abs(duration_difference):.1f}s too long - MUST regenerate with faster speech or less content"
            else:
                recommendation = f"Audio has quality issues (score: {quality_score:.2f}) - MUST regenerate"
        else:
            recommendation = f"Audio duration acceptable but could be improved (diff: {duration_difference:+.1f}s)"
        
        # Log analysis results
        logger.info(f"📊 Audio Duration Analysis:")
        logger.info(f"   Total duration: {total_duration:.1f}s (target: {target_duration}s)")
        logger.info(f"   Difference: {duration_difference:+.1f}s ({duration_ratio:.1%} of target)")
        logger.info(f"   Within tolerance: {'✅ YES' if is_within_tolerance else '❌ NO'}")
        logger.info(f"   Quality score: {quality_score:.2f}/1.0")
        logger.info(f"   Must regenerate: {'❌ YES' if must_regenerate else '✅ NO'}")
        logger.info(f"   Recommendation: {recommendation}")
        
        # Log segment details
        if segments_info:
            logger.info("📝 Segment details:")
            for seg in segments_info:
                issues = f" - Issues: {', '.join(seg['quality_issues'])}" if seg['quality_issues'] else ""
                logger.info(f"   Segment {seg['index']}: {seg['duration']:.1f}s{issues}")
        
        return AudioDurationAnalysis(
            total_duration=total_duration,
            target_duration=target_duration,
            segment_durations=segment_durations,
            is_within_tolerance=is_within_tolerance,
            tolerance_percent=self.tolerance_percent,
            duration_difference=duration_difference,
            duration_ratio=duration_ratio,
            recommendation=recommendation,
            segments_info=segments_info,
            quality_score=quality_score,
            must_regenerate=must_regenerate
        )
    
    def calculate_dynamic_clip_durations(self, audio_analysis: AudioDurationAnalysis, 
                                       num_clips: int) -> List[float]:
        """
        Calculate dynamic clip durations based on actual audio duration
        
        Args:
            audio_analysis: Audio duration analysis results
            num_clips: Number of video clips to generate
            
        Returns:
            List of clip durations that match audio duration
        """
        logger.info(f"🎬 Calculating dynamic clip durations for {num_clips} clips")
        
        # Use actual audio duration for calculations
        total_duration = audio_analysis.total_duration
        
        # If we have segment durations that match clip count, use them
        if len(audio_analysis.segment_durations) == num_clips:
            logger.info("✅ Using exact audio segment durations for video clips")
            return audio_analysis.segment_durations
        
        # Otherwise, distribute duration evenly with some variation
        base_duration = total_duration / num_clips
        clip_durations = []
        
        # Add slight variation to make it more natural
        for i in range(num_clips):
            # Vary by up to ±10% for natural pacing
            variation = np.random.uniform(0.9, 1.1)
            duration = base_duration * variation
            
            # Ensure within min/max bounds
            duration = max(self.min_segment_duration, 
                         min(duration, self.max_segment_duration))
            
            clip_durations.append(duration)
        
        # Adjust last clip to ensure exact match
        duration_sum = sum(clip_durations[:-1])
        clip_durations[-1] = total_duration - duration_sum
        
        # Ensure last clip is also within bounds
        if clip_durations[-1] < self.min_segment_duration:
            # Redistribute if last clip is too short
            shortage = self.min_segment_duration - clip_durations[-1]
            for i in range(len(clip_durations) - 1):
                clip_durations[i] -= shortage / (len(clip_durations) - 1)
            clip_durations[-1] = self.min_segment_duration
        
        logger.info(f"📏 Dynamic clip durations: {[f'{d:.1f}s' for d in clip_durations]}")
        logger.info(f"   Total: {sum(clip_durations):.1f}s (matches audio: {total_duration:.1f}s)")
        
        return clip_durations
    
    def add_padding_between_segments(self, audio_files: List[str], output_dir: str) -> List[str]:
        """
        Add padding/silence between audio segments for better pacing
        
        Args:
            audio_files: List of audio file paths
            output_dir: Directory to save padded audio files
            
        Returns:
            List of padded audio file paths
        """
        if len(audio_files) <= 1 or self.padding_between_segments <= 0:
            return audio_files
            
        logger.info(f"🔇 Adding {self.padding_between_segments}s padding between {len(audio_files)} segments")
        
        padded_files = []
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            from moviepy.editor import AudioFileClip, concatenate_audioclips
            from moviepy.audio.AudioClip import AudioClip
            
            # Create silence clip
            silence = AudioClip(
                lambda t: 0,
                duration=self.padding_between_segments,
                fps=44100
            )
            
            # Process each audio file
            for i, audio_file in enumerate(audio_files):
                # Copy original audio
                padded_path = os.path.join(output_dir, f"padded_{os.path.basename(audio_file)}")
                
                with AudioFileClip(audio_file) as audio:
                    # Add silence after each segment except the last
                    if i < len(audio_files) - 1:
                        padded_audio = concatenate_audioclips([audio, silence])
                        padded_audio.write_audiofile(padded_path, logger=None)
                        padded_audio.close()
                    else:
                        # Last segment - no padding
                        audio.write_audiofile(padded_path, logger=None)
                
                padded_files.append(padded_path)
                logger.info(f"✅ Padded audio segment {i+1}/{len(audio_files)}")
            
            return padded_files
            
        except Exception as e:
            logger.error(f"❌ Error adding padding: {e}")
            return audio_files  # Return original files on error
    
    def validate_before_video_generation(self, audio_files: List[str], 
                                       target_duration: float,
                                       block_on_failure: bool = True) -> Tuple[bool, AudioDurationAnalysis]:
        """
        Validate audio duration before proceeding to video generation
        
        Args:
            audio_files: List of audio file paths
            target_duration: Target video duration
            block_on_failure: Whether to block generation on validation failure
            
        Returns:
            Tuple of (can_proceed, analysis)
        """
        logger.info("🚦 Validating audio duration before video generation")
        
        # Analyze audio files
        analysis = self.analyze_audio_files(audio_files, target_duration)
        
        # Determine if we can proceed
        can_proceed = not analysis.must_regenerate or not block_on_failure
        
        if not can_proceed:
            logger.error("❌ BLOCKING: Audio duration validation failed")
            logger.error(f"   {analysis.recommendation}")
            logger.error("   Video generation cannot proceed until audio is regenerated")
        elif analysis.must_regenerate:
            logger.warning("⚠️ Audio duration issues detected but proceeding anyway")
            logger.warning(f"   {analysis.recommendation}")
        else:
            logger.info("✅ Audio duration validation passed - proceeding to video generation")
        
        return can_proceed, analysis