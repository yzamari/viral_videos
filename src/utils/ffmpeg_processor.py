"""
FFmpeg Video Processor - Python wrapper for FFmpeg operations
Replaces MoviePy with direct FFmpeg commands for better performance and precision
"""

import os
import subprocess
import json
import tempfile
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FFmpegProcessor:
    """Encapsulated FFmpeg processor for video operations"""
    
    def __init__(self):
        self.temp_files = []
    
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
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        self.temp_files.clear()
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get video info: {e}")
            return {}
    
    def get_duration(self, media_path: str) -> float:
        """Get media duration in seconds"""
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'csv=p=0', media_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.error(f"Failed to get duration: {e}")
            return 0.0
    
    def concatenate_videos(self, video_paths: List[str], output_path: str, 
                          method: str = "concat") -> str:
        """Concatenate multiple videos using FFmpeg"""
        if not video_paths:
            raise ValueError("No videos to concatenate")
        
        if method == "concat":
            # Create concat file
            concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            self.temp_files.append(concat_file.name)
            
            for video_path in video_paths:
                concat_file.write(f"file '{os.path.abspath(video_path)}'\n")
            concat_file.close()
            
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', concat_file.name, '-c', 'copy', output_path
            ]
        else:
            # Use filter_complex for advanced concatenation
            inputs = []
            for video_path in video_paths:
                inputs.extend(['-i', video_path])
            
            filter_complex = ''.join([f'[{i}:v][{i}:a]' for i in range(len(video_paths))])
            filter_complex += f'concat=n={len(video_paths)}:v=1:a=1[outv][outa]'
            
            cmd = ['ffmpeg', '-y'] + inputs + [
                '-filter_complex', filter_complex,
                '-map', '[outv]', '-map', '[outa]', output_path
            ]
        
        self._run_command(cmd, f"Concatenating {len(video_paths)} videos")
        return output_path
    
    def concatenate_audio(self, audio_paths: List[str], output_path: str,
                         crossfade: bool = True, fade_duration: float = 0.1) -> str:
        """Concatenate audio files with optional crossfade"""
        if not audio_paths:
            raise ValueError("No audio files to concatenate")
        
        # Filter out empty or invalid audio files
        valid_audio_paths = []
        for audio_path in audio_paths:
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                try:
                    duration = self.get_duration(audio_path)
                    if duration > 0:
                        valid_audio_paths.append(audio_path)
                    else:
                        logger.warning(f"Skipping zero-duration audio: {audio_path}")
                except Exception as e:
                    logger.warning(f"Skipping invalid audio file {audio_path}: {e}")
            else:
                logger.warning(f"Skipping non-existent or empty audio: {audio_path}")
        
        if not valid_audio_paths:
            raise ValueError("No valid audio files to concatenate")
        
        audio_paths = valid_audio_paths
        
        if len(audio_paths) == 1:
            # Single file, just copy
            cmd = ['ffmpeg', '-y', '-i', audio_paths[0], '-c', 'copy', output_path]
        elif crossfade and len(audio_paths) > 1:
            # Advanced concatenation with crossfade
            inputs = []
            for audio_path in audio_paths:
                inputs.extend(['-i', audio_path])
            
            filter_parts = []
            current_input = '[0:a]'
            
            for i in range(1, len(audio_paths)):
                next_input = f'[{i}:a]'
                output_label = f'[a{i}]' if i < len(audio_paths) - 1 else '[outa]'
                
                filter_parts.append(
                    f'{current_input}{next_input}acrossfade=d={fade_duration}:c1=tri:c2=tri{output_label}'
                )
                current_input = f'[a{i}]'
            
            filter_complex = ';'.join(filter_parts)
            
            # Check output format
            if output_path.endswith('.mp3'):
                audio_codec = ['-c:a', 'libmp3lame', '-b:a', '128k']
            else:
                audio_codec = ['-c:a', 'aac', '-b:a', '128k']
            
            cmd = ['ffmpeg', '-y'] + inputs + [
                '-filter_complex', filter_complex,
                '-map', '[outa]'] + audio_codec + [output_path]
        else:
            # Simple concatenation
            concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            self.temp_files.append(concat_file.name)
            
            for audio_path in audio_paths:
                concat_file.write(f"file '{os.path.abspath(audio_path)}'\n")
            concat_file.close()
            
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', concat_file.name, '-c', 'copy', output_path
            ]
        
        self._run_command(cmd, f"Concatenating {len(audio_paths)} audio files")
        return output_path
    
    def add_audio_to_video(self, video_path: str, audio_path: str, 
                          output_path: str, sync_method: str = "exact") -> str:
        """Add audio to video with precise synchronization"""
        
        if sync_method == "exact":
            # Map video and audio exactly, shortest duration wins
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_path
            ]
        elif sync_method == "stretch":
            # Stretch audio to match video duration
            video_duration = self.get_duration(video_path)
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-af', f'atempo={self.get_duration(audio_path)/video_duration}',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_path
            ]
        else:  # "pad"
            # Pad audio with silence to match video
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-af', 'apad',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-shortest',
                output_path
            ]
        
        self._run_command(cmd, f"Adding audio to video ({sync_method})")
        return output_path
    
    def create_subtitle_aligned_video(self, video_clips: List[str], 
                                    audio_segments: List[str],
                                    subtitle_segments: List[Dict],
                                    output_path: str) -> str:
        """Create video with perfect subtitle-audio alignment"""
        
        # Build complex filter for precise timing
        inputs = []
        for clip in video_clips:
            inputs.extend(['-i', clip])
        for audio in audio_segments:
            inputs.extend(['-i', audio])
        
        # Create filter_complex for precise timing
        video_count = len(video_clips)
        audio_count = len(audio_segments)
        
        filter_parts = []
        
        # Video concatenation
        if video_count > 1:
            video_concat = ''.join([f'[{i}:v]' for i in range(video_count)])
            video_concat += f'concat=n={video_count}:v=1:a=0[video_out]'
            filter_parts.append(video_concat)
        else:
            filter_parts.append('[0:v]copy[video_out]')
        
        # Audio with precise timing based on subtitles
        audio_timeline = []
        for i, (segment, audio_idx) in enumerate(zip(subtitle_segments, 
                                                   range(video_count, video_count + audio_count))):
            start_time = segment['start']
            duration = segment['end'] - segment['start']
            
            # Pad audio to exact subtitle timing
            audio_timeline.append(
                f'[{audio_idx}:a]adelay={int(start_time * 1000)}|{int(start_time * 1000)}[a{i}]'
            )
        
        if audio_timeline:
            filter_parts.extend(audio_timeline)
            
            # Mix all audio streams
            audio_mix = ''.join([f'[a{i}]' for i in range(len(audio_timeline))])
            audio_mix += f'amix=inputs={len(audio_timeline)}:duration=longest[audio_out]'
            filter_parts.append(audio_mix)
        
        filter_complex = ';'.join(filter_parts)
        
        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', filter_complex,
            '-map', '[video_out]',
            '-map', '[audio_out]' if audio_timeline else '[0:a]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_path
        ]
        
        self._run_command(cmd, "Creating subtitle-aligned video")
        return output_path
    
    def add_text_overlay(self, video_path: str, output_path: str,
                        text_overlays: List[Dict[str, Any]]) -> str:
        """Add multiple text overlays with AI-driven styling"""
        
        if not text_overlays:
            # No overlays, just copy
            cmd = ['ffmpeg', '-y', '-i', video_path, '-c', 'copy', output_path]
            self._run_command(cmd, "Copying video (no overlays)")
            return output_path
        
        # Build drawtext filters
        drawtext_filters = []
        
        for overlay in text_overlays:
            text = self._escape_text(overlay['text'])
            
            # AI-generated styling
            font_file = overlay.get('font_file', '/System/Library/Fonts/Arial.ttf')
            font_size = overlay.get('font_size', 24)
            font_color = overlay.get('font_color', 'white')
            
            # Position (can be animated)
            x = overlay.get('x', '(w-text_w)/2')
            y = overlay.get('y', '(h-text_h)/2')
            
            # Timing
            start_time = overlay.get('start_time', 0)
            end_time = overlay.get('end_time', None)
            
            # Effects
            box = overlay.get('box', True)
            box_color = overlay.get('box_color', 'black@0.5')
            box_border = overlay.get('box_border', 5)
            
            # Shadow/outline
            shadow = overlay.get('shadow', True)
            
            # Build drawtext filter
            drawtext_parts = [
                f"text='{text}'",
                f"fontfile='{font_file}'",
                f"fontsize={font_size}",
                f"fontcolor={font_color}",
                f"x={x}",
                f"y={y}"
            ]
            
            if box:
                drawtext_parts.extend([
                    f"box=1",
                    f"boxcolor={box_color}",
                    f"boxborderw={box_border}"
                ])
            
            if shadow:
                drawtext_parts.extend([
                    f"shadowcolor=black@0.8",
                    f"shadowx=2",
                    f"shadowy=2"
                ])
            
            # Timing
            if end_time:
                drawtext_parts.append(f"enable=between(t\\,{start_time}\\,{end_time})")
            elif start_time > 0:
                drawtext_parts.append(f"enable=gte(t\\,{start_time})")
            
            drawtext_filter = "drawtext=" + ":".join(drawtext_parts)
            drawtext_filters.append(drawtext_filter)
        
        # Combine all filters
        video_filter = ",".join(drawtext_filters)
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', video_filter,
            '-c:a', 'copy',
            output_path
        ]
        
        self._run_command(cmd, f"Adding {len(text_overlays)} text overlays")
        return output_path
    
    def extend_video_with_fadeout(self, video_path: str, audio_path: str, 
                                  output_path: str, fade_duration: float = 2.0) -> str:
        """Extend video to match audio duration with fade-out effect
        
        Args:
            video_path: Input video file
            audio_path: Audio file to match duration
            output_path: Output video file
            fade_duration: Duration of fade-out in seconds
        """
        video_duration = self.get_duration(video_path)
        audio_duration = self.get_duration(audio_path)
        
        if audio_duration <= video_duration:
            # No need to extend, just copy
            cmd = ['ffmpeg', '-y', '-i', video_path, '-i', audio_path, 
                   '-c:v', 'copy', '-c:a', 'copy', '-shortest', output_path]
        else:
            # Calculate how much to extend
            extension_duration = audio_duration - video_duration
            
            # Create filter for extending video with last frame + fade
            # 1. Loop last frame for extension duration
            # 2. Apply fade-out starting before video ends
            fade_start = video_duration - fade_duration
            
            filter_complex = (
                f"[0:v]tpad=stop_mode=clone:stop_duration={extension_duration},"
                f"fade=t=out:st={fade_start}:d={fade_duration + extension_duration}[v]"
            )
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'copy',
                '-t', str(audio_duration),
                output_path
            ]
        
        self._run_command(cmd, f"Extending video to {audio_duration:.1f}s with fade-out")
        return output_path
    
    def add_subtitles(self, video_path: str, subtitle_path: str, 
                     output_path: str, style: Dict[str, Any] = None) -> str:
        """Add subtitles with custom styling"""
        
        if style is None:
            style = {
                'font_size': 24,
                'font_color': 'white',
                'box_color': 'black@0.7',
                'position': 'bottom'
            }
        
        # Use subtitles filter for SRT files
        subtitle_filter = f"subtitles={subtitle_path}"
        
        # Add custom styling if provided
        if style.get('font_size'):
            subtitle_filter += f":force_style='FontSize={style['font_size']}'"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', subtitle_filter,
            '-c:a', 'copy',
            output_path
        ]
        
        self._run_command(cmd, "Adding subtitles")
        return output_path
    
    def _escape_text(self, text: str) -> str:
        """Escape text for FFmpeg drawtext filter"""
        # Escape special characters for FFmpeg
        text = text.replace("\\", "\\\\")
        text = text.replace("'", "\\'")
        text = text.replace(":", "\\:")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace(",", "\\,")
        text = text.replace(";", "\\;")
        return text
    
    def _run_command(self, cmd: List[str], description: str = "FFmpeg operation"):
        """Run FFmpeg command with error handling"""
        logger.info(f"πŸŽ¬ {description}")
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
                logger.debug(f"FFmpeg stderr: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ FFmpeg command failed: {e}")
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Stderr: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            logger.error(f"❌ FFmpeg command timed out: {' '.join(cmd)}")
            raise


class AdvancedOverlayGenerator:
    """AI-driven overlay generator for dynamic text effects"""
    
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
    
    async def generate_overlay_strategy(self, mission: str, platform: str, 
                                      duration: float, style: str) -> Dict[str, Any]:
        """Use AI to determine overlay strategy"""
        
        prompt = f"""
Create a dynamic overlay strategy for a {duration}s video on {platform}.

Mission: {mission}
Style: {style}

Design overlays that are:
1. Platform-optimized ({platform} best practices)  
2. Attention-grabbing and viral-worthy
3. Complement the content without overwhelming it
4. Use modern design trends

Consider:
- Hook overlays (first 3 seconds)
- Key point highlights (middle segments)
- Call-to-action overlays (final 5 seconds)
- Animated text effects
- Color psychology
- Font psychology
- Timing for maximum retention

Return JSON:
{{
    "overlay_count": 3-7,
    "hook_overlay": {{
        "text": "attention-grabbing opener",
        "font_style": "bold/modern/playful",
        "font_size": 32-48,
        "color": "#hex",
        "position": "center/top/bottom",
        "animation": "fade/slide/bounce/type",
        "duration": 2.5,
        "start_time": 0.0
    }},
    "content_overlays": [
        {{
            "text": "key point highlight",
            "font_style": "clean/bold",
            "font_size": 24-36,
            "color": "#hex",
            "position": "bottom/side",
            "animation": "fade/slide",
            "start_time": 5.0,
            "duration": 3.0
        }}
    ],
    "cta_overlay": {{
        "text": "call to action",
        "font_style": "bold/urgent",
        "font_size": 28-40,
        "color": "#hex",
        "position": "center/bottom",
        "animation": "pulse/glow",
        "start_time": {duration - 5},
        "duration": 5.0
    }}
}}
"""
        
        try:
            text_service = self.ai_manager.get_service("text_generation")
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7
            )
            
            response = await text_service.generate_text(request)
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"AI overlay generation failed: {e}")
            return self._get_fallback_overlay_strategy(platform, duration)
    
    def _get_fallback_overlay_strategy(self, platform: str, duration: float) -> Dict[str, Any]:
        """Fallback overlay strategy if AI fails"""
        return {
            "overlay_count": 3,
            "hook_overlay": {
                "text": "🔥 VIRAL CONTENT ALERT",
                "font_style": "bold",
                "font_size": 36,
                "color": "#FF6B6B",
                "position": "center",
                "animation": "bounce",
                "duration": 2.5,
                "start_time": 0.0
            },
            "content_overlays": [
                {
                    "text": "📈 TRENDING NOW",
                    "font_style": "modern",
                    "font_size": 28,
                    "color": "#4ECDC4",
                    "position": "bottom",
                    "animation": "slide",
                    "start_time": duration * 0.3,
                    "duration": 3.0
                }
            ],
            "cta_overlay": {
                "text": "👆 FOLLOW FOR MORE",
                "font_style": "bold",
                "font_size": 32,
                "color": "#FFE66D",
                "position": "center",
                "animation": "pulse",
                "start_time": duration - 5,
                "duration": 5.0
            }
        }