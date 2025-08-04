"""Visual Composer - Handles video composition and overlays"""

import os
import shutil
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ...utils.logging_config import get_logger
from ...utils.session_manager import SessionManager
from ..models.composition_models import (
    CompositionProject, VideoSegment, VideoLayer,
    LayerType, Position, ThemeConfig
)

logger = get_logger(__name__)


class VisualComposer:
    """Handles final video composition with overlays and effects"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.output_dir = os.path.join(
            session_manager.base_output_dir,
            "composed_videos"
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def apply_final_composition(
        self,
        video_path: str,
        composition: CompositionProject,
        output_filename: Optional[str] = None
    ) -> str:
        """Apply final composition with overlays and effects"""
        
        logger.info("Applying final video composition...")
        
        # Determine output path
        if output_filename:
            final_path = os.path.join(self.output_dir, output_filename)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = os.path.join(
                self.output_dir,
                f"{composition.name.replace(' ', '_')}_{timestamp}.mp4"
            )
        
        # Build FFmpeg filter complex
        filter_complex = self._build_filter_complex(composition)
        
        # Build FFmpeg command
        cmd = self._build_ffmpeg_command(
            video_path,
            composition,
            filter_complex,
            final_path
        )
        
        # Execute FFmpeg
        try:
            logger.info(f"Executing FFmpeg command: {' '.join(cmd[:10])}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("FFmpeg composition completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr}")
            # Fallback to simple copy
            logger.warning("Falling back to simple copy")
            shutil.copy2(video_path, final_path)
        
        return final_path
    
    def _build_filter_complex(
        self, 
        composition: CompositionProject
    ) -> str:
        """Build FFmpeg filter complex for overlays"""
        
        filters = []
        theme = composition.template.theme_config
        
        # Add logo overlay if specified
        if theme.logo_path and os.path.exists(theme.logo_path):
            filters.append(self._create_logo_filter(theme))
        
        # Add news ticker if enabled
        if composition.template.ticker_position:
            filters.append(self._create_ticker_filter(composition))
        
        # Add lower thirds for headlines
        filters.append(self._create_lower_third_filter(composition))
        
        # Add watermark if specified
        if theme.watermark_path and os.path.exists(theme.watermark_path):
            filters.append(self._create_watermark_filter(theme))
        
        # Combine filters
        if filters:
            return ";".join(filters)
        else:
            return "null"  # No filters
    
    def _build_ffmpeg_command(
        self,
        input_video: str,
        composition: CompositionProject,
        filter_complex: str,
        output_path: str
    ) -> List[str]:
        """Build complete FFmpeg command"""
        
        cmd = ["ffmpeg", "-y", "-i", input_video]
        
        # Add overlay inputs if needed
        theme = composition.template.theme_config
        
        if theme.logo_path and os.path.exists(theme.logo_path):
            cmd.extend(["-i", theme.logo_path])
        
        if theme.watermark_path and os.path.exists(theme.watermark_path):
            cmd.extend(["-i", theme.watermark_path])
        
        # Add filter complex if not null
        if filter_complex != "null":
            cmd.extend(["-filter_complex", filter_complex])
        
        # Output settings
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "copy",
            "-movflags", "+faststart",
            output_path
        ])
        
        return cmd
    
    def _create_logo_filter(self, theme: ThemeConfig) -> str:
        """Create logo overlay filter"""
        
        # Default logo position (top-left)
        logo_filter = (
            "[1:v]scale=200:-1[logo];"
            "[0:v][logo]overlay=50:50"
        )
        
        return logo_filter
    
    def _create_ticker_filter(
        self, 
        composition: CompositionProject
    ) -> str:
        """Create news ticker filter"""
        
        # Create scrolling text
        ticker_text = self._generate_ticker_text(composition)
        
        # Ticker at bottom of screen
        ticker_filter = (
            f"drawtext=text='{ticker_text}':"
            f"fontfile=/System/Library/Fonts/Helvetica.ttc:"
            f"fontsize=24:"
            f"fontcolor=white:"
            f"box=1:"
            f"boxcolor=red@0.8:"
            f"boxborderw=5:"
            f"x=w-mod(2*n\\,w+tw):"
            f"y=h-50"
        )
        
        return ticker_filter
    
    def _create_lower_third_filter(
        self,
        composition: CompositionProject
    ) -> str:
        """Create lower third graphics filter"""
        
        # Simple lower third with headline
        # This would be more complex with actual graphics
        headline = composition.segments[0].subtitle_text if composition.segments else ""
        
        lower_third_filter = (
            f"drawbox=x=0:y=h-200:w=w:h=100:"
            f"color=black@0.7:t=fill,"
            f"drawtext=text='{self._escape_text(headline)}':"
            f"fontfile=/System/Library/Fonts/Helvetica.ttc:"
            f"fontsize=36:"
            f"fontcolor=white:"
            f"x=(w-text_w)/2:"
            f"y=h-150"
        )
        
        return lower_third_filter
    
    def _create_watermark_filter(self, theme: ThemeConfig) -> str:
        """Create watermark overlay filter"""
        
        # Semi-transparent watermark in corner
        watermark_filter = (
            "[2:v]scale=100:-1,format=rgba,colorchannelmixer=aa=0.5[wm];"
            "[0:v][wm]overlay=W-w-20:H-h-20"
        )
        
        return watermark_filter
    
    def _generate_ticker_text(
        self,
        composition: CompositionProject
    ) -> str:
        """Generate text for news ticker"""
        
        ticker_items = []
        
        # Add headlines from segments
        for segment in composition.segments[:5]:
            if segment.subtitle_text:
                ticker_items.append(segment.subtitle_text)
        
        # Add metadata info
        ticker_items.append(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        )
        
        # Join with separator
        ticker_text = " • ".join(ticker_items)
        
        # Escape for FFmpeg
        return self._escape_text(ticker_text)
    
    def _escape_text(self, text: str) -> str:
        """Escape text for FFmpeg filters"""
        # Escape special characters
        text = text.replace("'", "\\'")
        text = text.replace(":", "\\:")
        text = text.replace(",", "\\,")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        return text
    
    async def create_intro_animation(
        self,
        composition: CompositionProject,
        duration: float = 5.0
    ) -> Optional[str]:
        """Create animated intro for news video"""
        
        # This would create a professional intro animation
        # For now, return None to use default
        return None
    
    async def create_outro_animation(
        self,
        composition: CompositionProject,
        duration: float = 5.0
    ) -> Optional[str]:
        """Create animated outro for news video"""
        
        # This would create a professional outro animation
        # For now, return None to use default
        return None
    
    def apply_color_grading(
        self,
        video_path: str,
        style: str
    ) -> str:
        """Apply color grading based on style"""
        
        # Define color grading presets
        presets = {
            "professional": "eq=contrast=1.1:brightness=0.05:saturation=0.9",
            "dramatic": "eq=contrast=1.3:brightness=-0.05:saturation=1.2",
            "modern": "eq=contrast=1.0:brightness=0.1:saturation=1.1",
            "vintage": "eq=contrast=0.9:brightness=0.0:saturation=0.7"
        }
        
        filter_string = presets.get(style, presets["professional"])
        
        # Apply color grading
        output_path = video_path.replace(".mp4", "_graded.mp4")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", filter_string,
            "-c:a", "copy",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except:
            # Return original if grading fails
            return video_path
    
    def add_background_music(
        self,
        video_path: str,
        music_path: str,
        volume: float = 0.3
    ) -> str:
        """Add background music to video"""
        
        if not os.path.exists(music_path):
            return video_path
        
        output_path = video_path.replace(".mp4", "_music.mp4")
        
        # Mix audio tracks
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={volume}[music];"
            f"[0:a][music]amix=inputs=2:duration=first",
            "-c:v", "copy",
            "-shortest",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except:
            return video_path