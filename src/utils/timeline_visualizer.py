"""
Timeline Visualizer - Comprehensive timing analysis for audio-subtitle alignment
Shows exactly when each component starts and ends for manual debugging
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class TimelineEvent:
    """Represents a single event on the timeline"""
    type: str  # 'subtitle', 'audio', 'overlay', 'video_clip'
    index: int
    start_time: float
    end_time: float
    duration: float
    content: str
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TimelineVisualizer:
    """Creates comprehensive timeline visualizations for debugging audio-subtitle sync"""
    
    def __init__(self, session_context=None):
        self.session_context = session_context
        self.events: List[TimelineEvent] = []
        self.video_duration = 0.0
        
    def add_subtitle_event(self, index: int, start: float, end: float, text: str):
        """Add a subtitle timing event"""
        event = TimelineEvent(
            type='subtitle',
            index=index,
            start_time=start,
            end_time=end,
            duration=end - start,
            content=text[:50] + "..." if len(text) > 50 else text
        )
        self.events.append(event)
        logger.debug(f"Added subtitle {index}: {start:.3f}s - {end:.3f}s")
        
    def add_audio_event(self, index: int, start: float, duration: float, 
                       file_path: str, actual_duration: Optional[float] = None):
        """Add an audio segment timing event"""
        event = TimelineEvent(
            type='audio',
            index=index,
            start_time=start,
            end_time=start + duration,
            duration=duration,
            content=os.path.basename(file_path),
            file_path=file_path,
            metadata={'actual_duration': actual_duration} if actual_duration else None
        )
        self.events.append(event)
        logger.debug(f"Added audio {index}: {start:.3f}s - {start + duration:.3f}s")
        
    def add_overlay_event(self, index: int, start: float, end: float, 
                         text: str, position: Optional[str] = None):
        """Add an overlay timing event"""
        event = TimelineEvent(
            type='overlay',
            index=index,
            start_time=start,
            end_time=end,
            duration=end - start,
            content=text[:30] + "..." if len(text) > 30 else text,
            metadata={'position': position} if position else None
        )
        self.events.append(event)
        logger.debug(f"Added overlay {index}: {start:.3f}s - {end:.3f}s")
        
    def add_video_clip_event(self, index: int, start: float, duration: float, 
                            file_path: str):
        """Add a video clip timing event"""
        event = TimelineEvent(
            type='video_clip',
            index=index,
            start_time=start,
            end_time=start + duration,
            duration=duration,
            content=os.path.basename(file_path),
            file_path=file_path
        )
        self.events.append(event)
        logger.debug(f"Added video clip {index}: {start:.3f}s - {start + duration:.3f}s")
        
    def set_video_duration(self, duration: float):
        """Set the total video duration"""
        self.video_duration = duration
        
    def analyze_alignment(self) -> Dict[str, Any]:
        """Analyze timing alignment and detect issues"""
        issues = []
        warnings = []
        
        # Sort events by start time
        sorted_events = sorted(self.events, key=lambda e: e.start_time)
        
        # Group events by type
        subtitles = [e for e in sorted_events if e.type == 'subtitle']
        audio_segments = [e for e in sorted_events if e.type == 'audio']
        
        # Check subtitle-audio alignment
        for i, subtitle in enumerate(subtitles):
            # Find corresponding audio segment
            matching_audio = None
            for audio in audio_segments:
                if audio.index == subtitle.index:
                    matching_audio = audio
                    break
                    
            if matching_audio:
                # Check alignment
                start_diff = abs(subtitle.start_time - matching_audio.start_time)
                end_diff = abs(subtitle.end_time - matching_audio.end_time)
                
                if start_diff > 0.1:  # 100ms threshold
                    issues.append({
                        'type': 'start_misalignment',
                        'subtitle_index': subtitle.index,
                        'subtitle_start': subtitle.start_time,
                        'audio_start': matching_audio.start_time,
                        'difference': start_diff,
                        'message': f"Subtitle {subtitle.index} starts {start_diff:.3f}s off from audio"
                    })
                    
                if end_diff > 0.1:
                    issues.append({
                        'type': 'end_misalignment',
                        'subtitle_index': subtitle.index,
                        'subtitle_end': subtitle.end_time,
                        'audio_end': matching_audio.end_time,
                        'difference': end_diff,
                        'message': f"Subtitle {subtitle.index} ends {end_diff:.3f}s off from audio"
                    })
            else:
                warnings.append({
                    'type': 'missing_audio',
                    'subtitle_index': subtitle.index,
                    'message': f"Subtitle {subtitle.index} has no matching audio segment"
                })
                
        # Check for gaps in audio
        for i in range(len(audio_segments) - 1):
            current = audio_segments[i]
            next_seg = audio_segments[i + 1]
            gap = next_seg.start_time - current.end_time
            
            if gap > 0.5:  # 500ms gap
                warnings.append({
                    'type': 'audio_gap',
                    'between': [current.index, next_seg.index],
                    'gap_start': current.end_time,
                    'gap_end': next_seg.start_time,
                    'duration': gap,
                    'message': f"Audio gap of {gap:.3f}s between segments {current.index} and {next_seg.index}"
                })
                
        # Check if audio covers full video duration
        if audio_segments:
            last_audio_end = max(a.end_time for a in audio_segments)
            if last_audio_end < self.video_duration - 0.5:
                issues.append({
                    'type': 'missing_audio_at_end',
                    'audio_ends_at': last_audio_end,
                    'video_duration': self.video_duration,
                    'missing_duration': self.video_duration - last_audio_end,
                    'message': f"Audio ends at {last_audio_end:.1f}s but video is {self.video_duration:.1f}s ({self.video_duration - last_audio_end:.1f}s missing)"
                })
                
        return {
            'issues': issues,
            'warnings': warnings,
            'stats': {
                'total_subtitles': len(subtitles),
                'total_audio_segments': len(audio_segments),
                'total_overlays': len([e for e in sorted_events if e.type == 'overlay']),
                'video_duration': self.video_duration,
                'audio_coverage': last_audio_end / self.video_duration if audio_segments and self.video_duration > 0 else 0
            }
        }
        
    def generate_ascii_timeline(self, width: int = 120) -> str:
        """Generate ASCII timeline visualization"""
        if not self.events or self.video_duration <= 0:
            return "No timeline data available"
            
        lines = []
        lines.append("=" * width)
        lines.append(f"TIMELINE VISUALIZATION (Total Duration: {self.video_duration:.1f}s)")
        lines.append("=" * width)
        
        # Time markers
        time_line = self._generate_time_markers(width)
        lines.append(time_line)
        lines.append("-" * width)
        
        # Group events by type
        event_types = ['video_clip', 'audio', 'subtitle', 'overlay']
        
        for event_type in event_types:
            type_events = [e for e in self.events if e.type == event_type]
            if not type_events:
                continue
                
            # Type header
            lines.append(f"\n{event_type.upper()}S:")
            
            # Sort by index
            type_events.sort(key=lambda e: e.index)
            
            for event in type_events:
                # Create timeline bar
                start_pos = int((event.start_time / self.video_duration) * (width - 20))
                end_pos = int((event.end_time / self.video_duration) * (width - 20))
                duration_width = max(1, end_pos - start_pos)
                
                # Event line
                bar = " " * start_pos + "█" * duration_width
                bar = bar[:width - 20]  # Trim to fit
                
                # Label
                label = f"{event_type[0].upper()}{event.index}: {event.start_time:.2f}-{event.end_time:.2f}s"
                
                lines.append(f"{label:>18} |{bar}|")
                
                # Content preview (indented)
                content_preview = f"                   └─ {event.content}"
                lines.append(content_preview)
                
        lines.append("\n" + "=" * width)
        
        # Add legend
        lines.append("LEGEND: █ = Active period, | = Timeline boundaries")
        lines.append(f"Time scale: 0s " + "-" * (width - 30) + f" {self.video_duration:.1f}s")
        
        return "\n".join(lines)
        
    def _generate_time_markers(self, width: int) -> str:
        """Generate time marker line"""
        markers = []
        marker_count = 10  # Number of time markers
        
        for i in range(marker_count + 1):
            time = (i / marker_count) * self.video_duration
            position = int((i / marker_count) * (width - 20))
            markers.append((position, f"{time:.1f}s"))
            
        # Build marker line
        line = [" "] * (width - 20)
        for pos, label in markers:
            # Place marker
            if pos < len(line):
                for j, char in enumerate(label):
                    if pos + j < len(line):
                        line[pos + j] = char
                        
        return "Time:              " + "".join(line)
        
    def generate_detailed_report(self) -> str:
        """Generate detailed timing report"""
        lines = []
        lines.append("=" * 80)
        lines.append("DETAILED TIMING REPORT")
        lines.append("=" * 80)
        
        # Analysis results
        analysis = self.analyze_alignment()
        
        # Summary
        lines.append(f"\nSUMMARY:")
        lines.append(f"- Video Duration: {self.video_duration:.3f}s")
        lines.append(f"- Total Subtitles: {analysis['stats']['total_subtitles']}")
        lines.append(f"- Total Audio Segments: {analysis['stats']['total_audio_segments']}")
        lines.append(f"- Total Overlays: {analysis['stats']['total_overlays']}")
        lines.append(f"- Audio Coverage: {analysis['stats']['audio_coverage']*100:.1f}%")
        
        # Issues
        if analysis['issues']:
            lines.append(f"\n⚠️  CRITICAL ISSUES ({len(analysis['issues'])}):")
            for issue in analysis['issues']:
                lines.append(f"  - {issue['message']}")
                
        # Warnings
        if analysis['warnings']:
            lines.append(f"\n⚡ WARNINGS ({len(analysis['warnings'])}):")
            for warning in analysis['warnings']:
                lines.append(f"  - {warning['message']}")
                
        # Detailed timeline
        lines.append("\n" + "-" * 80)
        lines.append("DETAILED TIMELINE:")
        lines.append("-" * 80)
        
        # Sort all events by start time
        sorted_events = sorted(self.events, key=lambda e: e.start_time)
        
        for event in sorted_events:
            type_symbol = {
                'subtitle': '📝',
                'audio': '🔊',
                'overlay': '🎨',
                'video_clip': '🎬'
            }.get(event.type, '❓')
            
            lines.append(
                f"{event.start_time:7.3f}s - {event.end_time:7.3f}s "
                f"[{event.duration:6.3f}s] {type_symbol} {event.type.upper():>10} #{event.index:02d}: "
                f"{event.content}"
            )
            
            # Add metadata if available
            if event.metadata:
                for key, value in event.metadata.items():
                    lines.append(f"{'':>40} {key}: {value}")
                    
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)
        
    def save_timeline_data(self, output_dir: str):
        """Save timeline data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON data
        json_data = {
            'video_duration': self.video_duration,
            'events': [
                {
                    'type': e.type,
                    'index': e.index,
                    'start_time': e.start_time,
                    'end_time': e.end_time,
                    'duration': e.duration,
                    'content': e.content,
                    'file_path': e.file_path,
                    'metadata': e.metadata
                }
                for e in self.events
            ],
            'analysis': self.analyze_alignment()
        }
        
        json_path = os.path.join(output_dir, 'timeline_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
            
        # Save ASCII visualization
        ascii_path = os.path.join(output_dir, 'timeline_visual.txt')
        with open(ascii_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_ascii_timeline())
            f.write("\n\n")
            f.write(self.generate_detailed_report())
            
        # Save analysis report
        report_path = os.path.join(output_dir, 'timeline_analysis.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Timeline Analysis Report\n\n")
            f.write(self._generate_markdown_report())
            
        logger.info(f"✅ Timeline data saved to {output_dir}")
        
    def _generate_markdown_report(self) -> str:
        """Generate markdown formatted report"""
        analysis = self.analyze_alignment()
        lines = []
        
        lines.append("## Summary\n")
        lines.append(f"- **Video Duration**: {self.video_duration:.3f}s")
        lines.append(f"- **Audio Coverage**: {analysis['stats']['audio_coverage']*100:.1f}%")
        lines.append(f"- **Total Components**: {len(self.events)}")
        lines.append("")
        
        if analysis['issues']:
            lines.append("## 🚨 Critical Issues\n")
            for issue in analysis['issues']:
                lines.append(f"- **{issue['type']}**: {issue['message']}")
            lines.append("")
            
        if analysis['warnings']:
            lines.append("## ⚠️ Warnings\n")
            for warning in analysis['warnings']:
                lines.append(f"- **{warning['type']}**: {warning['message']}")
            lines.append("")
            
        lines.append("## Timeline Details\n")
        lines.append("```")
        lines.append(self.generate_ascii_timeline())
        lines.append("```")
        
        return "\n".join(lines)