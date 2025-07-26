"""
Theme Overlay Renderer - Renders theme-specific overlays like news tickers, banners, etc.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ThemeOverlayRenderer:
    """Renders theme-specific overlays (news tickers, banners, logos, etc.)"""
    
    def __init__(self):
        self.temp_dir = Path("temp_overlays")
        self.temp_dir.mkdir(exist_ok=True)
        
    def apply_theme_overlays(self, video_path: str, theme: Any, output_path: str, 
                           video_duration: float = None) -> str:
        """
        Apply theme-specific overlays to video
        
        Args:
            video_path: Path to input video
            theme: Theme object with overlay configurations
            output_path: Path for output video
            video_duration: Video duration in seconds
            
        Returns:
            Path to video with overlays applied
        """
        try:
            if not theme:
                logger.info("No theme provided, skipping theme overlays")
                return video_path
                
            logger.info(f"🎨 Applying theme overlays for: {theme.name if hasattr(theme, 'name') else 'Unknown'}")
            
            # Get video info
            width, height, duration = self._get_video_info(video_path)
            if video_duration:
                duration = video_duration
                
            # Build complex filter for all overlays
            filter_parts = []
            filter_inputs = [video_path]
            input_count = 1
            
            # 1. Apply ticker if enabled
            if hasattr(theme, 'ticker_config') and theme.ticker_config.get('enabled'):
                ticker_filter = self._create_ticker_filter(
                    theme.ticker_config, width, height, duration, input_count
                )
                if ticker_filter:
                    filter_parts.append(ticker_filter)
                    
            # 2. Apply breaking news banner if enabled
            if hasattr(theme, 'breaking_news_banner') and theme.breaking_news_banner.get('enabled'):
                banner_filter = self._create_banner_filter(
                    theme.breaking_news_banner, width, height, duration, input_count
                )
                if banner_filter:
                    filter_parts.append(banner_filter)
                    
            # 3. Apply news desk overlay if enabled
            if hasattr(theme, 'news_desk_overlay') and theme.news_desk_overlay.get('enabled'):
                desk_filter = self._create_news_desk_filter(
                    theme.news_desk_overlay, width, height, duration, input_count
                )
                if desk_filter:
                    filter_parts.append(desk_filter)
                    
            # 4. Apply logo if configured
            if hasattr(theme, 'logo_config') and theme.logo_config.always_visible:
                logo_filter = self._create_logo_filter(
                    theme.logo_config, width, height, duration, input_count
                )
                if logo_filter:
                    filter_parts.append(logo_filter)
                    
            # If no overlays to apply, return original
            if not filter_parts:
                logger.info("No theme overlays to apply")
                return video_path
                
            # Combine all filters
            filter_complex = self._combine_filters(filter_parts)
            
            # Apply overlays using FFmpeg
            cmd = [
                'ffmpeg', '-i', video_path,
                '-filter_complex', filter_complex,
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
                '-c:a', 'copy',
                '-y', output_path
            ]
            
            logger.info(f"🎬 Applying theme overlays with FFmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Theme overlays applied successfully: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Failed to apply theme overlays: {result.stderr}")
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Error applying theme overlays: {e}")
            return video_path
            
    def _get_video_info(self, video_path: str) -> Tuple[int, int, float]:
        """Get video dimensions and duration"""
        try:
            cmd = [
                'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,duration',
                '-of', 'json', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                stream = data['streams'][0]
                width = int(stream.get('width', 1280))
                height = int(stream.get('height', 720))
                duration = float(stream.get('duration', 60))
                return width, height, duration
        except:
            pass
            
        return 1280, 720, 60.0
        
    def _create_ticker_filter(self, ticker_config: Dict, width: int, height: int, 
                            duration: float, input_idx: int) -> str:
        """Create ticker overlay filter"""
        try:
            # Ticker parameters
            ticker_height = int(height * ticker_config.get('height_percentage', 6) / 100)
            ticker_y = height - ticker_height
            bg_color = ticker_config.get('background_color', '#000000')
            text_color = ticker_config.get('text_color', '#FFFFFF')
            font_size = int(height * ticker_config.get('font_size_ratio', 0.035))
            
            # Combine ticker content
            ticker_text = " • ".join(ticker_config.get('content', ['BREAKING NEWS']))
            ticker_text = ticker_text * 3  # Repeat for continuous scroll
            
            # Create ticker filter
            filter_str = (
                f"[{input_idx}:v]"
                f"drawbox=x=0:y={ticker_y}:w={width}:h={ticker_height}:"
                f"color={bg_color}:t=fill,"
                f"drawtext=text='{ticker_text}':"
                f"fontcolor={text_color}:fontsize={font_size}:"
                f"x=w-mod(t*100\\,w+tw)-tw:y={ticker_y + ticker_height//4}"
            )
            
            return filter_str
            
        except Exception as e:
            logger.error(f"❌ Error creating ticker filter: {e}")
            return ""
            
    def _create_banner_filter(self, banner_config: Dict, width: int, height: int,
                            duration: float, input_idx: int) -> str:
        """Create breaking news banner filter"""
        try:
            # Banner parameters
            banner_height = int(height * banner_config.get('height_percentage', 10) / 100)
            bg_color = banner_config.get('background_color', '#FF0000')
            text_color = banner_config.get('text_color', '#FFFFFF')
            banner_text = banner_config.get('text', 'BREAKING NEWS')
            font_family = banner_config.get('font_family', 'Impact')
            font_size = int(banner_height * 0.7)
            
            # Create banner filter with pulsing animation
            filter_str = (
                f"drawbox=x=0:y=0:w={width}:h={banner_height}:"
                f"color={bg_color}@0.9:t=fill,"
                f"drawtext=text='{banner_text}':"
                f"fontcolor={text_color}:fontsize={font_size}:"
                f"fontfile=/System/Library/Fonts/Helvetica.ttc:"  # Use system font
                f"x=(w-text_w)/2:y=(0+{banner_height}-text_h)/2:"
                f"alpha='if(eq(mod(t,1),0),1,0.8)'"  # Pulsing effect
            )
            
            return filter_str
            
        except Exception as e:
            logger.error(f"❌ Error creating banner filter: {e}")
            return ""
            
    def _create_news_desk_filter(self, desk_config: Dict, width: int, height: int,
                                duration: float, input_idx: int) -> str:
        """Create news desk overlay filter"""
        try:
            # Desk parameters
            desk_height = int(height * desk_config.get('desk_height_percentage', 25) / 100)
            desk_y = height - desk_height
            desk_color = desk_config.get('desk_color', '#000080')
            
            # Create desk filter with gradient effect
            filter_str = (
                f"drawbox=x=0:y={desk_y}:w={width}:h={desk_height}:"
                f"color={desk_color}@0.8:t=fill"
            )
            
            return filter_str
            
        except Exception as e:
            logger.error(f"❌ Error creating news desk filter: {e}")
            return ""
            
    def _create_logo_filter(self, logo_config: Any, width: int, height: int,
                          duration: float, input_idx: int) -> str:
        """Create logo overlay filter"""
        try:
            # For now, create a text-based logo placeholder
            # In production, this would overlay an actual logo image
            size_percentage = getattr(logo_config, 'size_percentage', 12.0)
            position = getattr(logo_config, 'position', 'top-right')
            margin = int(width * getattr(logo_config, 'margin_percentage', 2.0) / 100)
            
            # Calculate position
            logo_size = int(height * size_percentage / 100)
            if position == 'top-right':
                x = width - logo_size - margin
                y = margin
            elif position == 'top-left':
                x = margin
                y = margin
            else:
                x = width - logo_size - margin
                y = margin
                
            # For now, draw a placeholder box for logo
            filter_str = (
                f"drawbox=x={x}:y={y}:w={logo_size}:h={logo_size}:"
                f"color=red@0.3:t=fill"
            )
            
            return filter_str
            
        except Exception as e:
            logger.error(f"❌ Error creating logo filter: {e}")
            return ""
            
    def _combine_filters(self, filter_parts: List[str]) -> str:
        """Combine multiple filter parts into a single filter complex"""
        # Remove empty filters
        filters = [f for f in filter_parts if f]
        
        if not filters:
            return ""
            
        # Chain filters together
        if len(filters) == 1:
            return filters[0]
        else:
            # Apply filters sequentially
            combined = "[0:v]"
            for i, filter_part in enumerate(filters):
                # Remove input specifier from filter part
                if filter_part.startswith("["):
                    filter_part = filter_part.split("]", 1)[1]
                combined += filter_part
                if i < len(filters) - 1:
                    combined += ","
            return combined