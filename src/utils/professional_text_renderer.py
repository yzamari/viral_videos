"""
Professional Text Renderer for Video Overlays
Uses OpenCV + Pillow/Skia-Python for high-quality text rendering
Replaces FFmpeg drawtext with professional typography
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import os
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL.ImageColor import getrgb
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import skia
    SKIA_AVAILABLE = True
except ImportError:
    SKIA_AVAILABLE = False

logger = logging.getLogger(__name__)


class TextAlignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class TextPosition(Enum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"
    CUSTOM = "custom"


@dataclass
class TextStyle:
    """Comprehensive text styling options"""
    font_family: str = "Arial"
    font_size: int = 48
    font_weight: str = "normal"  # normal, bold, light
    font_style: str = "normal"   # normal, italic
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)  # RGBA
    stroke_color: Tuple[int, int, int, int] = (0, 0, 0, 255)  # RGBA
    stroke_width: int = 2
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128)  # RGBA
    shadow_offset: Tuple[int, int] = (2, 2)
    shadow_blur: int = 4
    background_color: Optional[Tuple[int, int, int, int]] = None  # None or RGBA
    background_padding: Tuple[int, int, int, int] = (10, 5, 10, 5)  # left, top, right, bottom
    line_spacing: float = 1.2
    letter_spacing: int = 0
    text_decoration: str = "none"  # none, underline, strikethrough
    gradient: Optional[Dict[str, Any]] = None  # For gradient text effects


@dataclass
class TextLayout:
    """Text layout and positioning"""
    position: TextPosition = TextPosition.BOTTOM_CENTER
    custom_position: Optional[Tuple[int, int]] = None  # (x, y) for CUSTOM position
    alignment: TextAlignment = TextAlignment.CENTER
    max_width: Optional[int] = None  # Maximum width in pixels
    max_height: Optional[int] = None  # Maximum height in pixels
    margin: Tuple[int, int, int, int] = (20, 20, 20, 20)  # left, top, right, bottom
    z_index: int = 0  # For layering multiple text elements


@dataclass
class AnimationEffect:
    """Text animation effects"""
    effect_type: str = "none"  # none, fade_in, slide_in, typewriter, bounce
    duration: float = 0.5  # Animation duration in seconds
    delay: float = 0.0     # Animation delay in seconds
    easing: str = "ease_out"  # linear, ease_in, ease_out, ease_in_out


@dataclass
class TextOverlay:
    """Complete text overlay definition"""
    text: str
    style: TextStyle
    layout: TextLayout
    animation: Optional[AnimationEffect] = None
    start_time: float = 0.0
    end_time: float = 10.0
    fade_in_duration: float = 0.2
    fade_out_duration: float = 0.2


class ProfessionalTextRenderer:
    """High-quality text renderer for video overlays"""
    
    def __init__(self, use_skia: bool = True):
        self.use_skia = use_skia and SKIA_AVAILABLE
        self.use_pil = PIL_AVAILABLE
        
        if not self.use_skia and not self.use_pil:
            logger.warning("⚠️ Neither Skia-Python nor PIL available. Install with: "
                          "pip install skia-python pillow")
        
        # Font cache
        self.font_cache = {}
        
        # Default fonts by priority
        self.default_fonts = [
            "Arial", "Helvetica", "DejaVu Sans", "Liberation Sans",
            "Roboto", "Open Sans", "Lato", "Montserrat"
        ]
        
        logger.info(f"🎨 Professional text renderer initialized (Skia: {self.use_skia}, PIL: {self.use_pil})")
    
    def render_text_overlay(self, frame: np.ndarray, overlay: TextOverlay, 
                           current_time: float) -> np.ndarray:
        """Render a single text overlay on a video frame"""
        try:
            # Check if overlay should be visible at current time
            if not (overlay.start_time <= current_time <= overlay.end_time):
                return frame
            
            frame_height, frame_width = frame.shape[:2]
            
            # Calculate opacity based on fade in/out
            opacity = self._calculate_opacity(overlay, current_time)
            if opacity <= 0:
                return frame
            
            # Choose rendering method
            if self.use_skia:
                text_surface = self._render_with_skia(overlay, frame_width, frame_height)
            elif self.use_pil:
                text_surface = self._render_with_pil(overlay, frame_width, frame_height)
            else:
                text_surface = self._render_with_opencv(overlay, frame_width, frame_height)
            
            if text_surface is None:
                logger.warning("⚠️ Text rendering failed, using OpenCV fallback")
                text_surface = self._render_with_opencv(overlay, frame_width, frame_height)
            
            # Apply animation effects
            if overlay.animation and overlay.animation.effect_type != "none":
                text_surface = self._apply_animation_effect(text_surface, overlay, current_time)
            
            # Composite text onto frame with opacity
            result_frame = self._composite_with_opacity(frame, text_surface, opacity)
            
            return result_frame
            
        except Exception as e:
            logger.error(f"❌ Text overlay rendering failed: {e}")
            return frame
    
    def _calculate_opacity(self, overlay: TextOverlay, current_time: float) -> float:
        """Calculate opacity based on fade in/out timing"""
        # Time within the overlay duration
        overlay_time = current_time - overlay.start_time
        overlay_duration = overlay.end_time - overlay.start_time
        
        opacity = 1.0
        
        # Fade in
        if overlay_time < overlay.fade_in_duration:
            opacity = overlay_time / overlay.fade_in_duration
        
        # Fade out
        time_until_end = overlay_duration - overlay_time
        if time_until_end < overlay.fade_out_duration:
            fade_opacity = time_until_end / overlay.fade_out_duration
            opacity = min(opacity, fade_opacity)
        
        return max(0.0, min(1.0, opacity))
    
    def _render_with_skia(self, overlay: TextOverlay, frame_width: int, frame_height: int) -> Optional[np.ndarray]:
        """Render text using Skia-Python for highest quality"""
        try:
            if not SKIA_AVAILABLE:
                return None
            
            # Create Skia surface
            surface = skia.Surface(frame_width, frame_height)
            canvas = surface.getCanvas()
            canvas.clear(skia.Color4f(0, 0, 0, 0))  # Transparent background
            
            # Setup paint for text
            paint = skia.Paint()
            paint.setAntiAlias(True)
            paint.setColor4f(skia.Color4f(
                overlay.style.color[0] / 255.0,
                overlay.style.color[1] / 255.0,
                overlay.style.color[2] / 255.0,
                overlay.style.color[3] / 255.0
            ))
            
            # Setup font
            typeface = skia.Typeface(overlay.style.font_family, skia.FontStyle())
            font = skia.Font(typeface, overlay.style.font_size)
            
            # Setup stroke if needed
            if overlay.style.stroke_width > 0:
                stroke_paint = skia.Paint()
                stroke_paint.setAntiAlias(True)
                stroke_paint.setStyle(skia.Paint.kStroke_Style)
                stroke_paint.setStrokeWidth(overlay.style.stroke_width)
                stroke_paint.setColor4f(skia.Color4f(
                    overlay.style.stroke_color[0] / 255.0,
                    overlay.style.stroke_color[1] / 255.0,
                    overlay.style.stroke_color[2] / 255.0,
                    overlay.style.stroke_color[3] / 255.0
                ))
            
            # Calculate text position and layout
            lines = self._wrap_text_to_width(overlay.text, font, overlay.layout.max_width or frame_width - 40)
            total_height = len(lines) * overlay.style.font_size * overlay.style.line_spacing
            
            x, y = self._calculate_text_position(overlay.layout, frame_width, frame_height, 
                                               overlay.layout.max_width or frame_width, total_height)
            
            # Render background if specified
            if overlay.style.background_color:
                # Calculate background bounds
                max_line_width = max(font.measureText(line) for line in lines)
                bg_rect = skia.Rect.MakeXYWH(
                    x - overlay.style.background_padding[0],
                    y - overlay.style.background_padding[1],
                    max_line_width + overlay.style.background_padding[0] + overlay.style.background_padding[2],
                    total_height + overlay.style.background_padding[1] + overlay.style.background_padding[3]
                )
                
                bg_paint = skia.Paint()
                bg_paint.setColor4f(skia.Color4f(
                    overlay.style.background_color[0] / 255.0,
                    overlay.style.background_color[1] / 255.0,
                    overlay.style.background_color[2] / 255.0,
                    overlay.style.background_color[3] / 255.0
                ))
                canvas.drawRect(bg_rect, bg_paint)
            
            # Render shadow if specified
            if overlay.style.shadow_color[3] > 0:
                shadow_paint = skia.Paint(paint)
                shadow_paint.setColor4f(skia.Color4f(
                    overlay.style.shadow_color[0] / 255.0,
                    overlay.style.shadow_color[1] / 255.0,
                    overlay.style.shadow_color[2] / 255.0,
                    overlay.style.shadow_color[3] / 255.0
                ))
                
                for i, line in enumerate(lines):
                    line_y = y + i * overlay.style.font_size * overlay.style.line_spacing
                    shadow_x = x + overlay.style.shadow_offset[0]
                    shadow_y = line_y + overlay.style.shadow_offset[1]
                    canvas.drawSimpleText(line, shadow_x, shadow_y, font, shadow_paint)
            
            # Render stroke if specified
            if overlay.style.stroke_width > 0:
                for i, line in enumerate(lines):
                    line_y = y + i * overlay.style.font_size * overlay.style.line_spacing
                    canvas.drawSimpleText(line, x, line_y, font, stroke_paint)
            
            # Render main text
            for i, line in enumerate(lines):
                line_y = y + i * overlay.style.font_size * overlay.style.line_spacing
                canvas.drawSimpleText(line, x, line_y, font, paint)
            
            # Convert Skia surface to numpy array
            image = surface.makeImageSnapshot()
            array = image.toarray()
            
            # Convert RGBA to BGRA for OpenCV
            if array.shape[2] == 4:
                array = array[:, :, [2, 1, 0, 3]]  # RGBA to BGRA
            
            return array
            
        except Exception as e:
            logger.warning(f"⚠️ Skia rendering failed: {e}")
            return None
    
    def _render_with_pil(self, overlay: TextOverlay, frame_width: int, frame_height: int) -> Optional[np.ndarray]:
        """Render text using PIL for good quality"""
        try:
            if not PIL_AVAILABLE:
                return None
            
            # Create PIL image with transparency
            img = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Load font
            font = self._get_pil_font(overlay.style.font_family, overlay.style.font_size)
            
            # Wrap text to fit width
            lines = self._wrap_text_pil(overlay.text, font, overlay.layout.max_width or frame_width - 40)
            
            # Calculate total text dimensions
            line_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in lines]
            max_line_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)
            total_height = sum(line_heights) + (len(lines) - 1) * int(overlay.style.font_size * (overlay.style.line_spacing - 1))
            
            # Calculate position
            x, y = self._calculate_text_position(overlay.layout, frame_width, frame_height, 
                                               max_line_width, total_height)
            
            # Render background if specified
            if overlay.style.background_color:
                bg_x1 = x - overlay.style.background_padding[0]
                bg_y1 = y - overlay.style.background_padding[1]
                bg_x2 = x + max_line_width + overlay.style.background_padding[2]
                bg_y2 = y + total_height + overlay.style.background_padding[3]
                
                draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], 
                             fill=overlay.style.background_color)
            
            # Render each line
            current_y = y
            for line in lines:
                # Calculate x position for alignment
                line_width = draw.textbbox((0, 0), line, font=font)[2]
                if overlay.layout.alignment == TextAlignment.CENTER:
                    line_x = x + (max_line_width - line_width) // 2
                elif overlay.layout.alignment == TextAlignment.RIGHT:
                    line_x = x + max_line_width - line_width
                else:  # LEFT
                    line_x = x
                
                # Render shadow
                if overlay.style.shadow_color[3] > 0:
                    shadow_x = line_x + overlay.style.shadow_offset[0]
                    shadow_y = current_y + overlay.style.shadow_offset[1]
                    draw.text((shadow_x, shadow_y), line, font=font, fill=overlay.style.shadow_color)
                
                # Render stroke
                if overlay.style.stroke_width > 0:
                    for dx in range(-overlay.style.stroke_width, overlay.style.stroke_width + 1):
                        for dy in range(-overlay.style.stroke_width, overlay.style.stroke_width + 1):
                            if dx != 0 or dy != 0:
                                draw.text((line_x + dx, current_y + dy), line, font=font, 
                                        fill=overlay.style.stroke_color)
                
                # Render main text
                draw.text((line_x, current_y), line, font=font, fill=overlay.style.color)
                
                current_y += line_heights[lines.index(line)] + int(overlay.style.font_size * (overlay.style.line_spacing - 1))
            
            # Convert PIL image to numpy array
            array = np.array(img)
            
            # Convert RGBA to BGRA for OpenCV
            if array.shape[2] == 4:
                array = array[:, :, [2, 1, 0, 3]]  # RGBA to BGRA
            
            return array
            
        except Exception as e:
            logger.warning(f"⚠️ PIL rendering failed: {e}")
            return None
    
    def _render_with_opencv(self, overlay: TextOverlay, frame_width: int, frame_height: int) -> np.ndarray:
        """Fallback rendering using OpenCV (basic quality)"""
        try:
            # Create transparent overlay
            overlay_img = np.zeros((frame_height, frame_width, 4), dtype=np.uint8)
            
            # OpenCV font mapping
            cv2_font = cv2.FONT_HERSHEY_SIMPLEX
            if "bold" in overlay.style.font_weight.lower():
                cv2_font = cv2.FONT_HERSHEY_SIMPLEX
            
            # Calculate font scale
            font_scale = overlay.style.font_size / 30.0  # Rough scaling
            thickness = max(1, overlay.style.stroke_width)
            
            # Split text into lines
            lines = overlay.text.split('\n')
            if overlay.layout.max_width:
                lines = self._wrap_text_opencv(overlay.text, cv2_font, font_scale, overlay.layout.max_width)
            
            # Calculate text dimensions
            line_heights = []
            max_width = 0
            for line in lines:
                (w, h), baseline = cv2.getTextSize(line, cv2_font, font_scale, thickness)
                line_heights.append(h + baseline)
                max_width = max(max_width, w)
            
            total_height = sum(line_heights) + len(lines) * 5  # Add spacing
            
            # Calculate position
            x, y = self._calculate_text_position(overlay.layout, frame_width, frame_height, 
                                               max_width, total_height)
            
            # Render each line
            current_y = y
            for i, line in enumerate(lines):
                line_width = cv2.getTextSize(line, cv2_font, font_scale, thickness)[0][0]
                
                # Calculate x position for alignment
                if overlay.layout.alignment == TextAlignment.CENTER:
                    line_x = x + (max_width - line_width) // 2
                elif overlay.layout.alignment == TextAlignment.RIGHT:
                    line_x = x + max_width - line_width
                else:  # LEFT
                    line_x = x
                
                line_y = current_y + line_heights[i]
                
                # Render stroke/outline
                if overlay.style.stroke_width > 0:
                    cv2.putText(overlay_img, line, (line_x, line_y), cv2_font, font_scale,
                              overlay.style.stroke_color, thickness + 2, cv2.LINE_AA)
                
                # Render main text
                cv2.putText(overlay_img, line, (line_x, line_y), cv2_font, font_scale,
                          overlay.style.color, thickness, cv2.LINE_AA)
                
                current_y += line_heights[i] + 5
            
            return overlay_img
            
        except Exception as e:
            logger.error(f"❌ OpenCV text rendering failed: {e}")
            # Return empty overlay
            return np.zeros((frame_height, frame_width, 4), dtype=np.uint8)
    
    def _get_pil_font(self, font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
        """Get PIL font with caching"""
        cache_key = f"{font_family}_{font_size}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Try to load the specified font
        font_paths = [
            f"/System/Library/Fonts/{font_family}.ttf",  # macOS
            f"/System/Library/Fonts/{font_family}.ttc",  # macOS TrueType Collection
            f"/usr/share/fonts/truetype/{font_family.lower()}/{font_family}.ttf",  # Linux
            f"C:\\Windows\\Fonts\\{font_family}.ttf",  # Windows
            # Add emoji fonts for better emoji support
            "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS emoji font
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # macOS Unicode
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux emoji font
            "C:\\Windows\\Fonts\\seguiemj.ttf",  # Windows emoji font
        ]
        
        font = None
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break
            except:
                continue
        
        # Fallback to default font
        if font is None:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        self.font_cache[cache_key] = font
        return font
    
    def _wrap_text_to_width(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within specified width (Skia)"""
        if not text:
            return []
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.measureText(test_line) <= max_width or not current_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines or [text]
    
    def _wrap_text_pil(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within specified width (PIL)"""
        if not text:
            return []
        
        words = text.split()
        lines = []
        current_line = []
        
        # Create a temporary draw object for measurements
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if draw.textbbox((0, 0), test_line, font=font)[2] <= max_width or not current_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines or [text]
    
    def _wrap_text_opencv(self, text: str, font, font_scale: float, max_width: int) -> List[str]:
        """Wrap text to fit within specified width (OpenCV)"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            (w, h), _ = cv2.getTextSize(test_line, font, font_scale, 1)
            
            if w <= max_width or not current_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines or [text]
    
    def _calculate_text_position(self, layout: TextLayout, frame_width: int, frame_height: int,
                               text_width: int, text_height: int) -> Tuple[int, int]:
        """Calculate text position based on layout settings"""
        if layout.position == TextPosition.CUSTOM and layout.custom_position:
            return layout.custom_position
        
        # Apply margins
        available_width = frame_width - layout.margin[0] - layout.margin[2]
        available_height = frame_height - layout.margin[1] - layout.margin[3]
        
        # Calculate base position
        if layout.position in [TextPosition.TOP_LEFT, TextPosition.CENTER_LEFT, TextPosition.BOTTOM_LEFT]:
            x = layout.margin[0]
        elif layout.position in [TextPosition.TOP_CENTER, TextPosition.CENTER, TextPosition.BOTTOM_CENTER]:
            x = layout.margin[0] + (available_width - text_width) // 2
        else:  # RIGHT positions
            x = layout.margin[0] + available_width - text_width
        
        if layout.position in [TextPosition.TOP_LEFT, TextPosition.TOP_CENTER, TextPosition.TOP_RIGHT]:
            y = layout.margin[1]
        elif layout.position in [TextPosition.CENTER_LEFT, TextPosition.CENTER, TextPosition.CENTER_RIGHT]:
            y = layout.margin[1] + (available_height - text_height) // 2
        else:  # BOTTOM positions
            y = layout.margin[1] + available_height - text_height
        
        return max(0, x), max(0, y)
    
    def _apply_animation_effect(self, text_surface: np.ndarray, overlay: TextOverlay, 
                              current_time: float) -> np.ndarray:
        """Apply animation effects to text surface"""
        if not overlay.animation or overlay.animation.effect_type == "none":
            return text_surface
        
        # Calculate animation progress (0-1)
        animation_start = overlay.start_time + overlay.animation.delay
        animation_end = animation_start + overlay.animation.duration
        
        if current_time < animation_start:
            # Animation hasn't started yet
            if overlay.animation.effect_type in ["fade_in", "slide_in"]:
                return np.zeros_like(text_surface)  # Invisible
            return text_surface
        
        if current_time > animation_end:
            return text_surface  # Animation complete
        
        # Calculate progress with easing
        raw_progress = (current_time - animation_start) / overlay.animation.duration
        progress = self._apply_easing(raw_progress, overlay.animation.easing)
        
        # Apply specific animation effects
        if overlay.animation.effect_type == "fade_in":
            alpha_multiplier = progress
            if text_surface.shape[2] == 4:  # Has alpha channel
                text_surface[:, :, 3] = (text_surface[:, :, 3] * alpha_multiplier).astype(np.uint8)
        
        elif overlay.animation.effect_type == "slide_in":
            # Slide from bottom
            slide_offset = int((1 - progress) * text_surface.shape[0] * 0.5)
            if slide_offset > 0:
                # Create new surface with offset
                new_surface = np.zeros_like(text_surface)
                if slide_offset < text_surface.shape[0]:
                    new_surface[slide_offset:, :] = text_surface[:-slide_offset, :]
                text_surface = new_surface
        
        return text_surface
    
    def _apply_easing(self, t: float, easing: str) -> float:
        """Apply easing function to animation progress"""
        t = max(0, min(1, t))  # Clamp to [0, 1]
        
        if easing == "ease_in":
            return t * t
        elif easing == "ease_out":
            return 1 - (1 - t) * (1 - t)
        elif easing == "ease_in_out":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:  # linear
            return t
    
    def _composite_with_opacity(self, background: np.ndarray, overlay: np.ndarray, 
                              opacity: float) -> np.ndarray:
        """Composite overlay onto background with specified opacity"""
        if overlay.shape[2] != 4:  # No alpha channel
            return background
        
        # Extract alpha channel and apply global opacity
        alpha = overlay[:, :, 3:4] / 255.0 * opacity
        
        # Blend colors
        overlay_bgr = overlay[:, :, :3]
        blended = background * (1 - alpha) + overlay_bgr * alpha
        
        return blended.astype(np.uint8)
    
    def _is_rtl_text(self, text: str) -> bool:
        """Detect if text contains RTL characters (Hebrew, Arabic, etc.)"""
        rtl_ranges = [
            (0x0590, 0x05FF),  # Hebrew
            (0x0600, 0x06FF),  # Arabic
            (0x0700, 0x074F),  # Syriac
            (0x0750, 0x077F),  # Arabic Supplement
            (0x08A0, 0x08FF),  # Arabic Extended-A
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        ]
        
        for char in text:
            code = ord(char)
            for start, end in rtl_ranges:
                if start <= code <= end:
                    return True
        return False
    
    def create_subtitle_overlay(self, text: str, frame_width: int, frame_height: int,
                              style_preset: str = "default") -> TextOverlay:
        """Create a subtitle overlay with predefined styling"""
        # Detect if RTL text
        is_rtl = self._is_rtl_text(text)
        
        # Predefined subtitle styles
        styles = {
            "default": TextStyle(
                font_family="Arial",
                font_size=max(32, int(frame_width * 0.04)),
                font_weight="bold",
                color=(255, 255, 255, 255),
                stroke_color=(0, 0, 0, 255),
                stroke_width=2,
                background_color=(0, 0, 0, 128),
                background_padding=(10, 5, 10, 5),
                line_spacing=1.2
            ),
            "rtl": TextStyle(
                font_family="Arial",
                font_size=max(40, int(frame_width * 0.05)),  # Larger for RTL
                font_weight="bold",
                color=(255, 255, 255, 255),
                stroke_color=(0, 0, 0, 255),
                stroke_width=3,  # Thicker outline for RTL
                background_color=(0, 0, 0, 160),  # Darker background
                background_padding=(15, 8, 15, 8),  # More padding
                line_spacing=1.3
            ),
            "modern": TextStyle(
                font_family="Roboto",
                font_size=max(36, int(frame_width * 0.045)),
                font_weight="normal",
                color=(255, 255, 255, 255),
                stroke_color=(0, 0, 0, 0),
                stroke_width=0,
                background_color=(0, 0, 0, 180),
                background_padding=(15, 8, 15, 8),
                line_spacing=1.3
            ),
            "bold": TextStyle(
                font_family="Impact",
                font_size=max(40, int(frame_width * 0.05)),
                font_weight="bold",
                color=(255, 255, 255, 255),
                stroke_color=(0, 0, 0, 255),
                stroke_width=3,
                shadow_color=(0, 0, 0, 200),
                shadow_offset=(3, 3),
                shadow_blur=6,
                line_spacing=1.1
            )
        }
        
        # Use RTL style if RTL text detected
        if is_rtl and style_preset == "default":
            style = styles["rtl"]
        else:
            style = styles.get(style_preset, styles["default"])
        
        layout = TextLayout(
            position=TextPosition.BOTTOM_CENTER,
            alignment=TextAlignment.CENTER,
            max_width=int(frame_width * 0.9),
            margin=(20, 20, 20, 60)  # Extra bottom margin for subtitles
        )
        
        return TextOverlay(
            text=text,
            style=style,
            layout=layout,
            fade_in_duration=0.1,
            fade_out_duration=0.1
        )