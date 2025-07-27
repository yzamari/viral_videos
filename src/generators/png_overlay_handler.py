"""
PNG Overlay Handler
Adds support for overlaying PNG images (flags, logos, etc.) on videos
"""

import os
import subprocess
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from ..utils.logging_config import get_logger
from ..config.video_config import video_config

logger = get_logger(__name__)


class PNGOverlayHandler:
    """Handles PNG image overlays on videos"""
    
    def __init__(self):
        """Initialize PNG overlay handler"""
        self.supported_positions = [
            'top-left', 'top-center', 'top-right',
            'center-left', 'center', 'center-right',
            'bottom-left', 'bottom-center', 'bottom-right'
        ]
        
        # Default overlay settings
        self.default_settings = {
            'opacity': 0.9,
            'scale': 0.1,  # 10% of video size by default
            'padding': 20,  # pixels from edge
            'fade_in': 0.5,  # seconds
            'fade_out': 0.5  # seconds
        }
        
        logger.info("✅ PNG Overlay Handler initialized")
    
    def create_text_logo(self, text: str, output_path: str, 
                        width: int = 400, height: int = 150,
                        bg_color: str = '#CC0000', text_color: str = '#FFFFFF') -> Optional[str]:
        """Create a text-based logo as PNG when logo file doesn't exist"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import os
            
            # Create image with background
            img = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw rounded rectangle background
            padding = 10
            draw.rounded_rectangle(
                [(padding, padding), (width-padding, height-padding)],
                radius=15,
                fill=bg_color
            )
            
            # Try to use a nice font, fallback to default
            try:
                # Try to use Arial or system font
                font_size = int(height * 0.3)
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                # Use default font
                font = ImageFont.load_default()
            
            # Draw text
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=text_color, font=font)
            
            # Save
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, 'PNG')
            
            logger.info(f"✅ Created text logo: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create text logo: {e}")
            return None
    
    def add_png_overlay(self, 
                       video_path: str, 
                       png_path: str, 
                       output_path: str,
                       position: str = 'top-left',
                       scale: Optional[float] = None,
                       opacity: Optional[float] = None,
                       padding: Optional[int] = None,
                       start_time: float = 0,
                       end_time: Optional[float] = None) -> Optional[str]:
        """
        Add PNG overlay to video
        
        Args:
            video_path: Path to input video
            png_path: Path to PNG image
            output_path: Path for output video
            position: Overlay position (e.g., 'top-left', 'bottom-right')
            scale: Scale factor (0.0-1.0) relative to video size
            opacity: Opacity (0.0-1.0)
            padding: Padding from edges in pixels
            start_time: When to start showing overlay
            end_time: When to stop showing overlay (None = entire video)
        
        Returns:
            Path to output video or None if failed
        """
        try:
            # Validate inputs
            if not os.path.exists(video_path):
                logger.error(f"❌ Video not found: {video_path}")
                return None
            
            if not os.path.exists(png_path):
                logger.error(f"❌ PNG not found: {png_path}")
                return None
            
            if position not in self.supported_positions:
                logger.warning(f"⚠️ Invalid position: {position}, using top-left")
                position = 'top-left'
            
            # Use defaults if not specified
            scale = scale or self.default_settings['scale']
            opacity = opacity or self.default_settings['opacity']
            padding = padding or self.default_settings['padding']
            
            logger.info(f"🖼️ Adding PNG overlay: {os.path.basename(png_path)}")
            logger.info(f"   Position: {position}")
            logger.info(f"   Scale: {scale * 100}%")
            logger.info(f"   Opacity: {opacity * 100}%")
            
            # Get video dimensions
            video_width, video_height = self._get_video_dimensions(video_path)
            if not video_width or not video_height:
                logger.error("❌ Could not get video dimensions")
                return None
            
            # Calculate overlay position
            x, y = self._calculate_position(position, video_width, video_height, scale, padding)
            
            # Build FFmpeg filter
            filters = []
            
            # Load and scale the PNG
            overlay_filter = f"[1:v]scale=iw*{scale}:ih*{scale}"
            
            # Add opacity
            if opacity < 1.0:
                overlay_filter += f",format=rgba,colorchannelmixer=aa={opacity}"
            
            overlay_filter += "[logo]"
            filters.append(overlay_filter)
            
            # Overlay on video with timing
            overlay_cmd = f"[0:v][logo]overlay={x}:{y}"
            
            # Add timing if specified
            if end_time:
                overlay_cmd += f":enable='between(t,{start_time},{end_time})'"
            elif start_time > 0:
                overlay_cmd += f":enable='gte(t,{start_time})'"
            
            filters.append(overlay_cmd)
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', png_path,
                '-filter_complex', ';'.join(filters),
                '-c:a', 'copy',  # Copy audio without re-encoding
                '-c:v', video_config.encoding.video_codec,
                '-preset', 'fast',
                '-y', output_path
            ]
            
            logger.info("🎬 Applying PNG overlay...")
            
            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ PNG overlay added successfully: {output_path} ({file_size:.1f}MB)")
                return output_path
            else:
                logger.error(f"❌ FFmpeg failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to add PNG overlay: {e}")
            return None
    
    def add_israeli_flag(self, video_path: str, output_path: str, 
                        position: str = 'top-left',
                        scale: float = 0.08) -> Optional[str]:
        """
        Add Israeli flag overlay to video
        
        Args:
            video_path: Path to input video
            output_path: Path for output video
            position: Flag position (default: top-left)
            scale: Scale factor (default: 8% of video size)
        
        Returns:
            Path to output video or None if failed
        """
        # Check if we have the Israeli flag PNG
        flag_path = self._get_flag_path('israel')
        
        if not flag_path:
            logger.warning("⚠️ Israeli flag PNG not found, creating one...")
            flag_path = self._create_israeli_flag_svg()
        
        if flag_path:
            return self.add_png_overlay(
                video_path=video_path,
                png_path=flag_path,
                output_path=output_path,
                position=position,
                scale=scale,
                opacity=0.9
            )
        
        return None
    
    def _get_video_dimensions(self, video_path: str) -> Tuple[Optional[int], Optional[int]]:
        """Get video dimensions using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'csv=s=x:p=0',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                dimensions = result.stdout.strip().split('x')
                if len(dimensions) == 2:
                    return int(dimensions[0]), int(dimensions[1])
            
            return None, None
            
        except Exception as e:
            logger.error(f"❌ Failed to get video dimensions: {e}")
            return None, None
    
    def _calculate_position(self, position: str, video_width: int, video_height: int, 
                           scale: float, padding: int) -> Tuple[str, str]:
        """Calculate FFmpeg overlay position based on position name"""
        
        # Calculate overlay size (approximate)
        overlay_width = int(video_width * scale)
        overlay_height = int(video_height * scale * 0.67)  # Assume 3:2 aspect ratio
        
        positions = {
            'top-left': (f"{padding}", f"{padding}"),
            'top-center': (f"(W-w)/2", f"{padding}"),
            'top-right': (f"W-w-{padding}", f"{padding}"),
            'center-left': (f"{padding}", f"(H-h)/2"),
            'center': ("(W-w)/2", "(H-h)/2"),
            'center-right': (f"W-w-{padding}", f"(H-h)/2"),
            'bottom-left': (f"{padding}", f"H-h-{padding}"),
            'bottom-center': (f"(W-w)/2", f"H-h-{padding}"),
            'bottom-right': (f"W-w-{padding}", f"H-h-{padding}")
        }
        
        return positions.get(position, positions['top-left'])
    
    def _get_flag_path(self, country: str) -> Optional[str]:
        """Get path to flag PNG file"""
        # Check common locations
        possible_paths = [
            f"assets/flags/{country}.png",
            f"resources/flags/{country}.png",
            f"data/flags/{country}.png",
            os.path.join(os.path.dirname(__file__), f"../../assets/flags/{country}.png")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _create_israeli_flag_svg(self) -> Optional[str]:
        """Create Israeli flag as SVG and convert to PNG"""
        try:
            import tempfile
            
            # Create SVG content for Israeli flag
            svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="660" height="480" viewBox="0 0 220 160">
  <rect width="220" height="160" fill="white"/>
  <rect width="220" height="25" fill="#0038b8" y="15"/>
  <rect width="220" height="25" fill="#0038b8" y="120"/>
  <path d="M 110,55 L 125,85 L 95,85 z" fill="none" stroke="#0038b8" stroke-width="5.5"/>
  <path d="M 110,105 L 95,75 L 125,75 z" fill="none" stroke="#0038b8" stroke-width="5.5"/>
</svg>"""
            
            # Save SVG to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
                f.write(svg_content)
                svg_path = f.name
            
            # Convert SVG to PNG using ImageMagick or rsvg
            png_path = svg_path.replace('.svg', '.png')
            
            # Try different conversion methods
            converters = [
                ['convert', '-background', 'none', svg_path, png_path],
                ['rsvg-convert', '-o', png_path, svg_path],
                ['inkscape', svg_path, '--export-png', png_path]
            ]
            
            for cmd in converters:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0 and os.path.exists(png_path):
                        logger.info(f"✅ Created Israeli flag PNG: {png_path}")
                        os.unlink(svg_path)  # Clean up SVG
                        return png_path
                except:
                    continue
            
            # If no converter worked, keep the SVG for manual conversion
            logger.warning(f"⚠️ Could not convert SVG to PNG. SVG saved at: {svg_path}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to create Israeli flag: {e}")
            return None