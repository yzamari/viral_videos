"""
Third-party subtitle integration tool using FFmpeg
Handles RTL languages like Hebrew with proper formatting
"""
import os
import subprocess
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from ..models.video_models import Language

logger = logging.getLogger(__name__)

class SubtitleIntegrationTool:
    """Advanced subtitle integration using FFmpeg with RTL support"""
    
    def __init__(self):
        self.rtl_languages = {Language.HEBREW, Language.ARABIC, Language.PERSIAN}
        
        # Font configurations for different languages
        self.font_configs = {
            Language.HEBREW: {
                'font_family': 'Arial Hebrew',
                'fallback_fonts': ['Arial', 'DejaVu Sans', 'Noto Sans Hebrew', 'Helvetica'],
                'font_size': 38,  # Increased from 32 for better readability
                'outline': 3,  # Thicker outline for Hebrew
                'shadow': 2  # More prominent shadow
            },
            Language.ARABIC: {
                'font_family': 'Arial Arabic',
                'fallback_fonts': ['Arial', 'DejaVu Sans', 'Noto Sans Arabic'],
                'font_size': 36,  # Increased from 24 for better readability
                'outline': 3,     # Increased from 2 for better visibility
                'shadow': 2       # Increased from 1 for better contrast
            },
            'default': {
                'font_family': 'Arial',
                'fallback_fonts': ['DejaVu Sans', 'Liberation Sans'],
                'font_size': 36,  # Increased from 22 for better readability
                'outline': 3,     # Increased from 2 for better visibility
                'shadow': 2       # Increased from 1 for better contrast
            }
        }
    
    def integrate_subtitles_with_ffmpeg(self, 
                                      video_path: str, 
                                      subtitle_path: str, 
                                      output_path: str,
                                      language: Language = Language.ENGLISH_US,
                                      style_override: Optional[Dict[str, Any]] = None,
                                      video_width: Optional[int] = None,
                                      video_height: Optional[int] = None) -> bool:
        """
        Integrate subtitles using FFmpeg with language-specific formatting
        
        Args:
            video_path: Path to input video
            subtitle_path: Path to SRT subtitle file
            output_path: Path for output video with subtitles
            language: Language for subtitle formatting
            style_override: Override default style settings
            
        Returns:
            Success status
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return False
                
            if not os.path.exists(subtitle_path):
                logger.error(f"Subtitle file not found: {subtitle_path}")
                return False
            
            # Get video dimensions if not provided
            if not video_width or not video_height:
                video_width, video_height = self._get_video_dimensions(video_path)
                logger.info(f"📐 Video dimensions: {video_width}x{video_height}")
            
            # Get font configuration for language
            font_config = self.font_configs.get(language, self.font_configs['default'])
            if style_override:
                font_config.update(style_override)
            
            # Calculate dynamic font size based on video resolution
            from ..config import video_config
            calculated_font_size = video_config.get_font_size('subtitle', video_width)
            font_config['font_size'] = calculated_font_size
            
            # Scale outline and shadow based on font size
            font_config['outline'] = max(2, int(calculated_font_size * 0.08))  # 8% of font size
            font_config['shadow'] = max(1, int(calculated_font_size * 0.05))   # 5% of font size
            
            logger.info(f"📝 Dynamic subtitle styling: font_size={calculated_font_size}, outline={font_config['outline']}, shadow={font_config['shadow']}")
            
            # Find available font
            font_path = self._find_available_font(font_config)
            if not font_path:
                logger.warning(f"No suitable font found for {language.value}, using system default")
                font_path = None
            
            # Build FFmpeg filter for subtitles
            subtitle_filter = self._build_subtitle_filter(
                subtitle_path, language, font_config, font_path
            )
            
            # Construct FFmpeg command with high quality settings
            cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-i', video_path,
                '-vf', subtitle_filter,
                '-c:a', 'copy',  # Copy audio stream
                '-c:v', 'libx264',  # Re-encode video for subtitle burn-in
                '-preset', 'slow',  # Better quality
                '-crf', '18',  # Lower CRF = higher quality (18 is visually lossless)
                '-pix_fmt', 'yuv420p',  # Compatibility
                '-movflags', '+faststart',  # Web optimization
                output_path
            ]
            
            logger.info(f"🎬 Integrating {language.value} subtitles with FFmpeg...")
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            # Execute FFmpeg command
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    logger.info(f"✅ Subtitles integrated successfully: {output_path} ({file_size/1024/1024:.1f}MB)")
                    return True
                else:
                    logger.error("FFmpeg succeeded but output file not found")
                    return False
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg subtitle integration timed out")
            return False
        except Exception as e:
            logger.error(f"Subtitle integration failed: {e}")
            return False
    
    def _find_available_font(self, font_config: Dict[str, Any]) -> Optional[str]:
        """Find available font file on the system"""
        font_candidates = [font_config['font_family']] + font_config['fallback_fonts']
        
        # Common font paths by platform
        font_paths = [
            '/System/Library/Fonts',  # macOS
            '/Library/Fonts',  # macOS user fonts
            '/usr/share/fonts',  # Linux
            '/usr/local/share/fonts',  # Linux local
            'C:/Windows/Fonts',  # Windows
        ]
        
        for font_name in font_candidates:
            for base_path in font_paths:
                if not os.path.exists(base_path):
                    continue
                    
                # Try different font file patterns
                font_patterns = [
                    f"{font_name}.ttf",
                    f"{font_name}.otf",
                    f"{font_name.replace(' ', '')}.ttf",
                    f"{font_name.replace(' ', '-')}.ttf",
                    f"{font_name.lower()}.ttf",
                ]
                
                for pattern in font_patterns:
                    font_path = os.path.join(base_path, pattern)
                    if os.path.exists(font_path):
                        logger.debug(f"Found font: {font_path}")
                        return font_path
        
        return None
    
    def _get_video_dimensions(self, video_path: str) -> tuple:
        """Get video dimensions using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        width = stream.get('width', 1920)
                        height = stream.get('height', 1080)
                        return width, height
            
            logger.warning("Failed to get video dimensions, using defaults")
            return 1920, 1080  # Default HD dimensions
            
        except Exception as e:
            logger.warning(f"Error getting video dimensions: {e}, using defaults")
            return 1920, 1080
    
    def _build_subtitle_filter(self, 
                             subtitle_path: str, 
                             language: Language,
                             font_config: Dict[str, Any],
                             font_path: Optional[str]) -> str:
        """Build FFmpeg subtitle filter with language-specific settings"""
        
        # Build proper force_style string for subtitles filter
        style_parts = []
        
        # Font settings
        if font_config.get('font_family'):
            style_parts.append(f"FontName={font_config['font_family']}")
        
        style_parts.append(f"FontSize={font_config['font_size']}")
        
        # Colors - CRITICAL: Transparent background
        style_parts.append("PrimaryColour=&H00FFFFFF")  # White text
        style_parts.append("OutlineColour=&H00000000")  # Black outline
        style_parts.append("BackColour=&H80000000")  # Transparent background
        
        # Border and shadow
        style_parts.append(f"BorderStyle=1")  # Outline + drop shadow
        style_parts.append(f"Outline={font_config['outline']}")
        style_parts.append(f"Shadow={font_config['shadow']}")
        
        # Positioning
        style_parts.append("Alignment=2")  # Bottom center
        style_parts.append("MarginV=80")  # Distance from bottom - matches perfect video
        
        # Bold text for better readability
        style_parts.append("Bold=1")
        
        # RTL language specific settings
        if language in self.rtl_languages:
            style_parts.append("Alignment=2")  # Center alignment for RTL
            logger.info(f"Applied RTL settings for {language.value}")
        
        # Combine all style settings
        force_style = ",".join(style_parts)
        
        # Build final filter with proper escaping
        subtitle_filter = f"subtitles='{subtitle_path}':force_style='{force_style}'"
        
        logger.debug(f"Subtitle filter: {subtitle_filter}")
        
        return subtitle_filter
    
    def create_styled_srt(self, 
                         input_srt_path: str, 
                         output_srt_path: str,
                         language: Language = Language.ENGLISH_US) -> bool:
        """
        Create a styled SRT file with language-specific formatting
        
        Args:
            input_srt_path: Original SRT file
            output_srt_path: Styled SRT output
            language: Language for styling
            
        Returns:
            Success status
        """
        try:
            if not os.path.exists(input_srt_path):
                logger.error(f"Input SRT not found: {input_srt_path}")
                return False
            
            with open(input_srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # Apply RTL formatting if needed
            if language in self.rtl_languages:
                # Add RTL markers and proper formatting
                srt_content = self._apply_rtl_formatting(srt_content, language)
                logger.info(f"Applied RTL formatting for {language.value}")
            
            # Save styled SRT
            with open(output_srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            logger.info(f"✅ Created styled SRT: {output_srt_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create styled SRT: {e}")
            return False
    
    def _apply_rtl_formatting(self, srt_content: str, language: Language) -> str:
        """Apply RTL formatting to SRT content"""
        lines = srt_content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Skip sequence numbers and timestamps
            if line.strip().isdigit() or '-->' in line or not line.strip():
                formatted_lines.append(line)
                continue
            
            # Apply RTL formatting to text lines
            if language == Language.HEBREW:
                # Add Hebrew RTL marker and ensure proper direction
                formatted_line = f"‏{line.strip()}‏"  # RTL markers
                formatted_lines.append(formatted_line)
            elif language == Language.ARABIC:
                # Add Arabic RTL marker
                formatted_line = f"‏{line.strip()}‏"
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def validate_subtitle_sync(self, video_path: str, subtitle_path: str) -> Dict[str, Any]:
        """
        Validate subtitle synchronization with video
        
        Returns:
            Validation results including timing analysis
        """
        try:
            # Get video duration
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {'valid': False, 'error': 'Could not analyze video'}
            
            import json
            video_info = json.loads(result.stdout)
            video_duration = float(video_info['format']['duration'])
            
            # Parse SRT timing
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # Extract all timestamps
            import re
            timestamp_pattern = r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
            timestamps = re.findall(timestamp_pattern, srt_content)
            
            if not timestamps:
                return {'valid': False, 'error': 'No timestamps found in SRT'}
            
            # Convert last timestamp to seconds
            last_end = timestamps[-1][1]
            h, m, s_ms = last_end.split(':')
            s, ms = s_ms.split(',')
            last_subtitle_time = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
            
            # Check if subtitles fit within video duration
            valid = last_subtitle_time <= video_duration + 1.0  # 1 second tolerance
            
            return {
                'valid': valid,
                'video_duration': video_duration,
                'subtitle_duration': last_subtitle_time,
                'subtitle_count': len(timestamps),
                'timing_difference': video_duration - last_subtitle_time
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}