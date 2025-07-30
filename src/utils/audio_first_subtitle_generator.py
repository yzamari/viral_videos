"""
Audio-First Subtitle Generator
Creates subtitles based on ACTUAL audio durations instead of estimates.
This eliminates audio-subtitle sync issues by measuring real audio files.
"""

import os
import logging
import subprocess
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AudioSegmentInfo:
    """Information about an audio segment"""
    file_path: str
    duration: float
    start_time: float
    end_time: float
    text: str
    confidence: float = 1.0


@dataclass
class SubtitleSegment:
    """A subtitle segment with precise timing"""
    start: float
    end: float
    text: str
    audio_file: str
    index: int
    method: str = "audio_duration_based"


class AudioFirstSubtitleGenerator:
    """
    Generates subtitles based on actual audio file durations.
    
    This replaces the estimation-based approach that caused sync issues.
    
    OLD APPROACH (caused sync issues):
    Script → Estimate durations → Create subtitles → Generate audio
    
    NEW APPROACH (eliminates sync issues):  
    Script → Generate audio → Measure actual durations → Create subtitles
    """
    
    def __init__(self, padding_between_segments: float = 0.0):
        """
        Initialize the audio-first subtitle generator
        
        Args:
            padding_between_segments: Gap between audio segments in seconds
        """
        self.padding_between_segments = padding_between_segments
        logger.info("🎵 Audio-First Subtitle Generator initialized")
        logger.info(f"   Padding between segments: {padding_between_segments}s")
        
    def get_audio_duration(self, audio_file: str) -> float:
        """
        Get precise audio duration using FFprobe
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Duration in seconds, or 0.0 if file doesn't exist/error
        """
        if not os.path.exists(audio_file):
            logger.warning(f"⚠️ Audio file not found: {audio_file}")
            return 0.0
            
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            
            logger.debug(f"📏 {os.path.basename(audio_file)}: {duration:.3f}s")
            return duration
            
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
            logger.error(f"❌ Failed to get duration for {audio_file}: {e}")
            return 0.0
            
    def analyze_audio_segments(self, 
                             audio_files: List[str], 
                             script_segments: List[Dict[str, Any]]) -> List[AudioSegmentInfo]:
        """
        Analyze audio files and create segment information
        
        Args:
            audio_files: List of audio file paths
            script_segments: Script segments with text content
            
        Returns:
            List of AudioSegmentInfo with actual durations
        """
        logger.info(f"🔍 Analyzing {len(audio_files)} audio segments")
        
        audio_segments = []
        current_time = 0.0
        
        for i, (audio_file, script_segment) in enumerate(zip(audio_files, script_segments)):
            # Get ACTUAL duration from audio file
            actual_duration = self.get_audio_duration(audio_file)
            
            if actual_duration == 0.0:
                logger.warning(f"⚠️ Skipping segment {i+1} due to invalid audio file")
                continue
                
            segment_info = AudioSegmentInfo(
                file_path=audio_file,
                duration=actual_duration,
                start_time=current_time,
                end_time=current_time + actual_duration,
                text=script_segment.get('text', ''),
                confidence=1.0  # High confidence since we measured actual file
            )
            
            audio_segments.append(segment_info)
            
            # Move timeline forward
            current_time += actual_duration + self.padding_between_segments
            
            logger.info(f"   Segment {i+1}: {actual_duration:.3f}s "
                       f"({segment_info.start_time:.3f}s - {segment_info.end_time:.3f}s)")
                       
        total_duration = current_time - self.padding_between_segments  # Remove last padding
        logger.info(f"✅ Total analyzed duration: {total_duration:.3f}s")
        
        return audio_segments
        
    def create_subtitle_segments(self, 
                               audio_segments: List[AudioSegmentInfo],
                               max_subtitle_duration: float = 5.0) -> List[SubtitleSegment]:
        """
        Create subtitle segments from audio segments
        
        For long audio segments, split into multiple subtitle segments for readability
        
        Args:
            audio_segments: Audio segment information
            max_subtitle_duration: Maximum duration for a single subtitle
            
        Returns:
            List of SubtitleSegment objects
        """
        logger.info(f"📝 Creating subtitle segments (max duration: {max_subtitle_duration}s)")
        
        subtitle_segments = []
        subtitle_index = 0
        
        for audio_segment in audio_segments:
            text = audio_segment.text.strip()
            if not text:
                logger.warning(f"⚠️ Empty text for audio segment: {audio_segment.file_path}")
                continue
                
            # If audio segment is short enough, create single subtitle
            if audio_segment.duration <= max_subtitle_duration:
                subtitle = SubtitleSegment(
                    start=audio_segment.start_time,
                    end=audio_segment.end_time,
                    text=text,
                    audio_file=audio_segment.file_path,
                    index=subtitle_index,
                    method="single_segment"
                )
                subtitle_segments.append(subtitle)
                subtitle_index += 1
                
                logger.debug(f"   Single subtitle: {subtitle.start:.3f}s-{subtitle.end:.3f}s")
                
            else:
                # Split long audio segment into multiple subtitles
                words = text.split()
                total_words = len(words)
                
                # Calculate how many subtitle segments we need
                num_subtitles = max(1, int(audio_segment.duration / max_subtitle_duration))
                words_per_subtitle = max(1, total_words // num_subtitles)
                
                # Calculate time per subtitle
                time_per_subtitle = audio_segment.duration / num_subtitles
                
                for sub_idx in range(num_subtitles):
                    start_word = sub_idx * words_per_subtitle
                    end_word = min(start_word + words_per_subtitle, total_words)
                    
                    # Handle last subtitle - include remaining words
                    if sub_idx == num_subtitles - 1:
                        end_word = total_words
                        
                    subtitle_text = ' '.join(words[start_word:end_word])
                    
                    start_time = audio_segment.start_time + (sub_idx * time_per_subtitle)
                    end_time = audio_segment.start_time + ((sub_idx + 1) * time_per_subtitle)
                    
                    # Adjust last subtitle end time to match audio exactly
                    if sub_idx == num_subtitles - 1:
                        end_time = audio_segment.end_time
                        
                    subtitle = SubtitleSegment(
                        start=start_time,
                        end=end_time,
                        text=subtitle_text,
                        audio_file=audio_segment.file_path,
                        index=subtitle_index,
                        method="split_segment"
                    )
                    subtitle_segments.append(subtitle)
                    subtitle_index += 1
                    
                    logger.debug(f"   Split subtitle {sub_idx+1}/{num_subtitles}: "
                               f"{start_time:.3f}s-{end_time:.3f}s")
                               
        logger.info(f"✅ Created {len(subtitle_segments)} subtitle segments from "
                   f"{len(audio_segments)} audio segments")
        
        return subtitle_segments
        
    def format_subtitle_text(self, text: str, max_chars_per_line: int = 42, max_lines: int = 2) -> str:
        """
        Format subtitle text for optimal readability
        
        Args:
            text: Raw subtitle text
            max_chars_per_line: Maximum characters per line
            max_lines: Maximum number of lines
            
        Returns:
            Formatted text with line breaks
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            # Check if adding this word would exceed line length
            if current_length + word_length + len(current_line) > max_chars_per_line:
                if current_line:  # If we have words in current line
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:  # Single word is too long
                    lines.append(word)
                    current_line = []
                    current_length = 0
            else:
                current_line.append(word)
                current_length += word_length
                
            # Stop if we've reached max lines
            if len(lines) >= max_lines:
                break
                
        # Add remaining words to last line
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
            
        # Truncate if too many lines
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            
        return '\n'.join(lines)
        
    def create_srt_file(self, subtitle_segments: List[SubtitleSegment], output_path: str) -> str:
        """
        Create SRT subtitle file
        
        Args:
            subtitle_segments: List of subtitle segments
            output_path: Path for output SRT file
            
        Returns:
            Path to created SRT file
        """
        logger.info(f"📄 Creating SRT file: {output_path}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(subtitle_segments, 1):
                # Format timestamps
                start_time = self._seconds_to_srt_time(segment.start)
                end_time = self._seconds_to_srt_time(segment.end)
                
                # Format text
                formatted_text = self.format_subtitle_text(segment.text)
                
                # Write SRT entry
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{formatted_text}\n\n")
                
        logger.info(f"✅ SRT file created with {len(subtitle_segments)} entries")
        return output_path
        
    def create_vtt_file(self, subtitle_segments: List[SubtitleSegment], output_path: str) -> str:
        """
        Create VTT subtitle file
        
        Args:
            subtitle_segments: List of subtitle segments
            output_path: Path for output VTT file
            
        Returns:
            Path to created VTT file
        """
        logger.info(f"📄 Creating VTT file: {output_path}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for segment in subtitle_segments:
                # Format timestamps
                start_time = self._seconds_to_vtt_time(segment.start)
                end_time = self._seconds_to_vtt_time(segment.end)
                
                # Format text
                formatted_text = self.format_subtitle_text(segment.text)
                
                # Write VTT entry
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{formatted_text}\n\n")
                
        logger.info(f"✅ VTT file created with {len(subtitle_segments)} entries")
        return output_path
        
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
        
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to VTT time format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
        
    def generate_subtitles(self,
                         audio_files: List[str],
                         script_segments: List[Dict[str, Any]],
                         output_dir: str,
                         base_filename: str = "subtitles") -> Tuple[str, str, List[SubtitleSegment]]:
        """
        Complete subtitle generation pipeline
        
        Args:
            audio_files: List of audio file paths
            script_segments: Script segments with text
            output_dir: Directory for subtitle files
            base_filename: Base filename for subtitle files
            
        Returns:
            Tuple of (srt_path, vtt_path, subtitle_segments)
        """
        logger.info("🚀 Starting audio-first subtitle generation")
        
        # Step 1: Analyze audio files for actual durations
        audio_segments = self.analyze_audio_segments(audio_files, script_segments)
        
        if not audio_segments:
            raise ValueError("No valid audio segments found")
            
        # Step 2: Create subtitle segments
        subtitle_segments = self.create_subtitle_segments(audio_segments)
        
        # Step 3: Create subtitle files
        srt_path = os.path.join(output_dir, f"{base_filename}.srt")
        vtt_path = os.path.join(output_dir, f"{base_filename}.vtt")
        
        self.create_srt_file(subtitle_segments, srt_path)
        self.create_vtt_file(subtitle_segments, vtt_path)
        
        # Log summary
        total_duration = subtitle_segments[-1].end if subtitle_segments else 0.0
        logger.info(f"🎯 Subtitle generation complete:")
        logger.info(f"   Total duration: {total_duration:.3f}s")
        logger.info(f"   Subtitle segments: {len(subtitle_segments)}")
        logger.info(f"   Audio segments: {len(audio_segments)}")
        logger.info(f"   SRT file: {srt_path}")
        logger.info(f"   VTT file: {vtt_path}")
        
        return srt_path, vtt_path, subtitle_segments