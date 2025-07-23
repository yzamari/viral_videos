"""Theme Integration Service for applying themes to video generation."""

import logging
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..models.theme import Theme, LogoConfiguration, LowerThirdsStyle, CaptionStyle
from ..managers.theme_manager import ThemeManager
from ...utils.session_context import SessionContext

logger = logging.getLogger(__name__)


class ThemeIntegrationService:
    """Service for integrating themes into video generation pipeline."""
    
    def __init__(self, theme_manager: ThemeManager, session_context: SessionContext):
        """Initialize theme integration service.
        
        Args:
            theme_manager: Manager for theme operations
            session_context: Current session context
        """
        self.theme_manager = theme_manager
        self.session_context = session_context
        self._theme_cache: Dict[str, Theme] = {}
        
    def load_theme(self, theme_id: str) -> Optional[Theme]:
        """Load theme by ID with caching.
        
        Args:
            theme_id: Theme identifier
            
        Returns:
            Theme object or None if not found
        """
        if theme_id in self._theme_cache:
            return self._theme_cache[theme_id]
            
        theme = self.theme_manager.get_theme(theme_id)
        if theme:
            self._theme_cache[theme_id] = theme
            logger.info(f"Loaded theme: {theme.name} ({theme_id})")
        else:
            logger.warning(f"Theme not found: {theme_id}")
            
        return theme
        
    def apply_logo_overlay(
        self,
        frame: np.ndarray,
        theme: Theme,
        frame_number: int,
        total_frames: int
    ) -> np.ndarray:
        """Apply logo overlay to video frame.
        
        Args:
            frame: Video frame as numpy array
            theme: Theme containing logo configuration
            frame_number: Current frame number
            total_frames: Total number of frames
            
        Returns:
            Frame with logo overlay
        """
        if not theme.brand_kit or not theme.brand_kit.logo_path:
            return frame
            
        logo_config = theme.brand_kit.logo_config
        if not logo_config or not logo_config.enabled:
            return frame
            
        try:
            # Load logo image
            logo_path = Path(theme.brand_kit.logo_path)
            if not logo_path.exists():
                logger.warning(f"Logo file not found: {logo_path}")
                return frame
                
            logo = cv2.imread(str(logo_path), cv2.IMREAD_UNCHANGED)
            if logo is None:
                return frame
                
            # Resize logo
            h, w = frame.shape[:2]
            logo_h = int(h * logo_config.size)
            logo_w = int(logo_h * logo.shape[1] / logo.shape[0])
            logo = cv2.resize(logo, (logo_w, logo_h))
            
            # Calculate position
            x, y = self._calculate_position(
                frame_size=(w, h),
                element_size=(logo_w, logo_h),
                position=logo_config.position,
                margin=logo_config.margin
            )
            
            # Apply fade animation if configured
            opacity = logo_config.opacity
            if logo_config.fade_in_duration > 0:
                fade_frames = int(logo_config.fade_in_duration * 30)  # Assuming 30fps
                if frame_number < fade_frames:
                    opacity *= frame_number / fade_frames
                    
            if logo_config.fade_out_duration > 0:
                fade_frames = int(logo_config.fade_out_duration * 30)
                frames_from_end = total_frames - frame_number
                if frames_from_end < fade_frames:
                    opacity *= frames_from_end / fade_frames
            
            # Overlay logo with alpha blending
            frame = self._overlay_image(frame, logo, (x, y), opacity)
            
        except Exception as e:
            logger.error(f"Error applying logo overlay: {e}")
            
        return frame
        
    def apply_lower_thirds(
        self,
        frame: np.ndarray,
        theme: Theme,
        text_primary: str,
        text_secondary: Optional[str] = None,
        display_duration: float = 5.0,
        frame_number: int = 0,
        fps: float = 30.0
    ) -> np.ndarray:
        """Apply lower thirds graphics to frame.
        
        Args:
            frame: Video frame
            theme: Theme with lower thirds configuration
            text_primary: Main text to display
            text_secondary: Optional secondary text
            display_duration: How long to display (seconds)
            frame_number: Current frame number
            fps: Video framerate
            
        Returns:
            Frame with lower thirds
        """
        if not theme.lower_thirds_style or not theme.lower_thirds_style.enabled:
            return frame
            
        style = theme.lower_thirds_style
        h, w = frame.shape[:2]
        
        # Create lower thirds graphic
        lt_height = int(h * 0.15)  # 15% of frame height
        lt_width = int(w * 0.4)     # 40% of frame width
        
        # Create background with gradient
        overlay = np.zeros((lt_height, lt_width, 4), dtype=np.uint8)
        
        # Apply gradient background
        for i in range(lt_height):
            alpha = int(255 * style.background_opacity * (1 - i / lt_height * 0.3))
            color = self._hex_to_rgb(style.background_color)
            overlay[i, :] = (*color, alpha)
            
        # Add text
        pil_image = Image.fromarray(overlay)
        draw = ImageDraw.Draw(pil_image)
        
        # Load fonts (with fallback)
        try:
            font_primary = ImageFont.truetype(style.font_family, int(style.font_size * 1.2))
            font_secondary = ImageFont.truetype(style.font_family, int(style.font_size * 0.8))
        except:
            font_primary = ImageFont.load_default()
            font_secondary = ImageFont.load_default()
            
        # Draw primary text
        text_color = self._hex_to_rgb(style.text_color)
        draw.text(
            (20, 10),
            text_primary,
            font=font_primary,
            fill=(*text_color, 255)
        )
        
        # Draw secondary text if provided
        if text_secondary:
            draw.text(
                (20, int(lt_height * 0.6)),
                text_secondary,
                font=font_secondary,
                fill=(*text_color, 200)
            )
            
        overlay = np.array(pil_image)
        
        # Calculate position (lower third)
        x = int(w * 0.05)  # 5% from left
        y = int(h * 0.7)   # 70% from top
        
        # Apply animation
        if style.animation_type == "slide":
            # Slide in from left
            animation_frames = int(0.5 * fps)  # 0.5 second animation
            if frame_number < animation_frames:
                x -= int((1 - frame_number / animation_frames) * lt_width)
                
        # Overlay lower thirds
        frame = self._overlay_image(frame, overlay, (x, y), 1.0)
        
        return frame
        
    def apply_caption_style(
        self,
        frame: np.ndarray,
        theme: Theme,
        caption_text: str,
        position: str = "bottom"
    ) -> np.ndarray:
        """Apply styled captions to frame.
        
        Args:
            frame: Video frame
            theme: Theme with caption style
            caption_text: Caption text to display
            position: Caption position (top/bottom)
            
        Returns:
            Frame with styled captions
        """
        if not theme.caption_style or not caption_text:
            return frame
            
        style = theme.caption_style
        h, w = frame.shape[:2]
        
        # Create text overlay
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # Load font
        try:
            font = ImageFont.truetype(style.font_family, style.font_size)
        except:
            font = ImageFont.load_default()
            
        # Get text dimensions
        bbox = draw.textbbox((0, 0), caption_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        x = (w - text_width) // 2
        y = h - text_height - 50 if position == "bottom" else 50
        
        # Draw background if enabled
        if style.background_enabled:
            padding = 10
            bg_color = self._hex_to_rgb(style.background_color)
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(*bg_color, int(255 * style.background_opacity))
            )
            
        # Draw text with outline if enabled
        text_color = self._hex_to_rgb(style.text_color)
        if style.outline_width > 0:
            outline_color = self._hex_to_rgb(style.outline_color)
            # Draw outline
            for adj in range(-style.outline_width, style.outline_width + 1):
                for adj2 in range(-style.outline_width, style.outline_width + 1):
                    if adj != 0 or adj2 != 0:
                        draw.text((x + adj, y + adj2), caption_text, font=font, fill=outline_color)
                        
        # Draw main text
        draw.text((x, y), caption_text, font=font, fill=text_color)
        
        # Convert back to OpenCV format
        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return frame
        
    def apply_intro_outro(
        self,
        video_path: str,
        theme: Theme,
        output_path: str
    ) -> bool:
        """Apply intro and outro to video.
        
        Args:
            video_path: Path to main video
            theme: Theme with intro/outro templates
            output_path: Path for output video
            
        Returns:
            Success status
        """
        if not theme.video_template:
            # No intro/outro to apply
            return False
            
        try:
            clips = []
            
            # Add intro if exists
            if theme.video_template.intro_template_path:
                intro_path = Path(theme.video_template.intro_template_path)
                if intro_path.exists():
                    clips.append(str(intro_path))
                    
            # Add main video
            clips.append(video_path)
            
            # Add outro if exists
            if theme.video_template.outro_template_path:
                outro_path = Path(theme.video_template.outro_template_path)
                if outro_path.exists():
                    clips.append(str(outro_path))
                    
            if len(clips) == 1:
                # No intro/outro found
                return False
                
            # Concatenate videos using ffmpeg
            import subprocess
            
            # Create concat file
            concat_file = self.session_context.get_output_path("concat_list.txt")
            with open(concat_file, 'w') as f:
                for clip in clips:
                    f.write(f"file '{clip}'\n")
                    
            # Run ffmpeg concat
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg concat failed: {result.stderr}")
                return False
                
            logger.info(f"Applied intro/outro to video: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying intro/outro: {e}")
            return False
            
    def create_series_metadata(
        self,
        theme: Theme,
        series_name: str,
        episode_number: int,
        episode_title: str
    ) -> Dict[str, Any]:
        """Create metadata for series episode.
        
        Args:
            theme: Theme for the series
            series_name: Name of the series
            episode_number: Episode number
            episode_title: Episode title
            
        Returns:
            Series metadata dictionary
        """
        metadata = {
            "series": {
                "name": series_name,
                "theme_id": theme.id,
                "theme_name": theme.name,
                "brand": theme.brand_kit.brand_name if theme.brand_kit else None,
                "episode": {
                    "number": episode_number,
                    "title": episode_title,
                    "formatted_title": f"{series_name} - Episode {episode_number}: {episode_title}"
                }
            },
            "visual_identity": {
                "primary_color": theme.brand_kit.primary_color if theme.brand_kit else None,
                "secondary_color": theme.brand_kit.secondary_color if theme.brand_kit else None,
                "font_family": theme.brand_kit.font_family if theme.brand_kit else None,
                "logo_path": theme.brand_kit.logo_path if theme.brand_kit else None
            },
            "style_elements": {
                "lower_thirds_enabled": theme.lower_thirds_style.enabled if theme.lower_thirds_style else False,
                "caption_style": theme.caption_style.style_name if theme.caption_style else None,
                "transition_type": theme.transition_style.transition_type if theme.transition_style else None
            }
        }
        
        return metadata
        
    def _calculate_position(
        self,
        frame_size: Tuple[int, int],
        element_size: Tuple[int, int],
        position: str,
        margin: int
    ) -> Tuple[int, int]:
        """Calculate x, y position for element placement.
        
        Args:
            frame_size: (width, height) of frame
            element_size: (width, height) of element
            position: Position string (top-left, bottom-right, etc.)
            margin: Margin from edges
            
        Returns:
            (x, y) position
        """
        w, h = frame_size
        ew, eh = element_size
        
        # Parse position
        if "top" in position:
            y = margin
        elif "bottom" in position:
            y = h - eh - margin
        else:  # center
            y = (h - eh) // 2
            
        if "left" in position:
            x = margin
        elif "right" in position:
            x = w - ew - margin
        else:  # center
            x = (w - ew) // 2
            
        return x, y
        
    def _overlay_image(
        self,
        background: np.ndarray,
        overlay: np.ndarray,
        position: Tuple[int, int],
        opacity: float
    ) -> np.ndarray:
        """Overlay image with alpha blending.
        
        Args:
            background: Background image
            overlay: Overlay image with alpha channel
            position: (x, y) position for overlay
            opacity: Overall opacity (0-1)
            
        Returns:
            Composited image
        """
        x, y = position
        h, w = overlay.shape[:2]
        
        # Ensure overlay fits in frame
        if x < 0:
            overlay = overlay[:, -x:]
            w = overlay.shape[1]
            x = 0
        if y < 0:
            overlay = overlay[-y:, :]
            h = overlay.shape[0]
            y = 0
            
        if x + w > background.shape[1]:
            w = background.shape[1] - x
            overlay = overlay[:, :w]
        if y + h > background.shape[0]:
            h = background.shape[0] - y
            overlay = overlay[:h, :]
            
        if h <= 0 or w <= 0:
            return background
            
        # Extract alpha channel
        if overlay.shape[2] == 4:
            alpha = overlay[:, :, 3] / 255.0 * opacity
            overlay_rgb = overlay[:, :, :3]
        else:
            alpha = np.ones((h, w)) * opacity
            overlay_rgb = overlay
            
        # Blend images
        for c in range(3):
            background[y:y+h, x:x+w, c] = (
                alpha * overlay_rgb[:, :, c] +
                (1 - alpha) * background[y:y+h, x:x+w, c]
            )
            
        return background
        
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string (#RRGGBB)
            
        Returns:
            (R, G, B) tuple
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))