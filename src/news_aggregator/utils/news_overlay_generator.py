#!/usr/bin/env python3
"""
News Channel Overlay Generator
Creates professional news channel-style overlays dynamically
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class NewsOverlayGenerator:
    """Generate professional news channel overlays"""
    
    def __init__(self, platform: str = "youtube"):
        self.platform = platform
        self.dimensions = self._get_dimensions()
        
    def _get_dimensions(self) -> Tuple[int, int]:
        """Get dimensions based on platform"""
        if self.platform == "tiktok":
            return (1080, 1920)
        elif self.platform == "instagram":
            return (1080, 1080)
        else:  # youtube, twitter
            return (1920, 1080)
    
    def create_news_overlay(
        self,
        channel_name: str = "NEWS",
        style: str = "modern",
        output_path: str = None
    ) -> str:
        """Create a news channel overlay with ticker, logo area, and branding"""
        
        width, height = self.dimensions
        
        # Create transparent overlay
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Define colors based on style
        if "dark" in style.lower() or "satir" in style.lower():
            primary_color = (220, 20, 60, 230)  # Crimson red for satire
            secondary_color = (40, 40, 40, 200)  # Dark gray
            accent_color = (255, 215, 0, 255)  # Gold
        else:
            primary_color = (200, 0, 0, 230)  # News red
            secondary_color = (0, 0, 0, 200)  # Black
            accent_color = (255, 255, 255, 255)  # White
        
        # Platform-specific layout
        if self.platform == "tiktok":
            # Portrait mode layout
            self._create_portrait_overlay(draw, width, height, channel_name, 
                                         primary_color, secondary_color, accent_color)
        else:
            # Landscape mode layout
            self._create_landscape_overlay(draw, width, height, channel_name,
                                          primary_color, secondary_color, accent_color)
        
        # Save overlay
        if not output_path:
            output_path = f"news_overlay_{self.platform}.png"
        
        overlay.save(output_path, 'PNG')
        logger.info(f"✅ Created news overlay: {output_path}")
        return output_path
    
    def _create_portrait_overlay(self, draw, width, height, channel_name,
                                primary_color, secondary_color, accent_color):
        """Create portrait mode news overlay for TikTok"""
        
        # Top header bar
        header_height = 120
        draw.rectangle([(0, 0), (width, header_height)], fill=primary_color)
        
        # Channel name in header
        try:
            # Try to use a bold font
            font_size = 60
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        # Add "LIVE" indicator
        live_box_width = 120
        draw.rectangle([(20, 20), (20 + live_box_width, 80)], fill=(255, 0, 0, 255))
        try:
            live_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            live_font = font
        draw.text((40, 35), "LIVE", font=live_font, fill=(255, 255, 255, 255))
        
        # Channel name
        text_x = 160
        draw.text((text_x, 30), channel_name, font=font, fill=accent_color)
        
        # Bottom ticker area
        ticker_height = 150
        ticker_y = height - ticker_height
        
        # Main ticker background
        draw.rectangle([(0, ticker_y), (width, height)], fill=secondary_color)
        
        # Red accent bar on ticker
        draw.rectangle([(0, ticker_y), (width, ticker_y + 8)], fill=primary_color)
        
        # "BREAKING NEWS" or style-appropriate label
        if "satir" in channel_name.lower() or "סאטיר" in channel_name:
            breaking_text = "סאטירה"
        else:
            breaking_text = "מבזק"
        
        breaking_box_width = 200
        draw.rectangle([(30, ticker_y + 20), (30 + breaking_box_width, ticker_y + 70)], 
                      fill=primary_color)
        try:
            breaking_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        except:
            breaking_font = font
        draw.text((60, ticker_y + 30), breaking_text, font=breaking_font, fill=(255, 255, 255, 255))
        
        # Time display (top right)
        time_text = "14:30"
        draw.text((width - 150, 35), time_text, font=breaking_font, fill=accent_color)
    
    def _create_landscape_overlay(self, draw, width, height, channel_name,
                                 primary_color, secondary_color, accent_color):
        """Create landscape mode news overlay for YouTube/Twitter"""
        
        # Top header bar (thinner for landscape)
        header_height = 80
        draw.rectangle([(0, 0), (width, header_height)], fill=primary_color)
        
        try:
            font_size = 48
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        # LIVE indicator
        draw.rectangle([(30, 15), (130, 65)], fill=(255, 0, 0, 255))
        try:
            live_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        except:
            live_font = font
        draw.text((50, 25), "LIVE", font=live_font, fill=(255, 255, 255, 255))
        
        # Channel name
        draw.text((160, 20), channel_name, font=font, fill=accent_color)
        
        # Bottom ticker
        ticker_height = 120
        ticker_y = height - ticker_height
        
        draw.rectangle([(0, ticker_y), (width, height)], fill=secondary_color)
        draw.rectangle([(0, ticker_y), (width, ticker_y + 6)], fill=primary_color)
        
        # Breaking news box
        if "satir" in channel_name.lower() or "סאטיר" in channel_name:
            breaking_text = "SATIRE"
        else:
            breaking_text = "BREAKING"
        
        draw.rectangle([(40, ticker_y + 15), (240, ticker_y + 65)], fill=primary_color)
        try:
            breaking_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        except:
            breaking_font = font
        draw.text((70, ticker_y + 25), breaking_text, font=breaking_font, fill=(255, 255, 255, 255))
        
        # Time display
        draw.text((width - 120, 25), "14:30", font=breaking_font, fill=accent_color)
    
    def create_lower_third(
        self,
        title: str,
        subtitle: str = "",
        style: str = "modern",
        output_path: str = None
    ) -> str:
        """Create a lower third graphic for news"""
        
        width, height = self.dimensions
        
        # Create transparent image
        lower_third = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(lower_third)
        
        # Position at lower third
        if self.platform == "tiktok":
            y_position = int(height * 0.65)
            box_height = 180
            margin = 50
        else:
            y_position = int(height * 0.7)
            box_height = 150
            margin = 80
        
        # Background box
        draw.rectangle(
            [(margin, y_position), (width - margin, y_position + box_height)],
            fill=(0, 0, 0, 200)
        )
        
        # Red accent bar
        draw.rectangle(
            [(margin, y_position), (margin + 8, y_position + box_height)],
            fill=(220, 20, 60, 255)
        )
        
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title
        draw.text((margin + 30, y_position + 20), title, font=title_font, fill=(255, 255, 255, 255))
        
        # Draw subtitle if provided
        if subtitle:
            draw.text((margin + 30, y_position + 80), subtitle, font=subtitle_font, fill=(200, 200, 200, 255))
        
        if not output_path:
            output_path = f"lower_third_{self.platform}.png"
        
        lower_third.save(output_path, 'PNG')
        return output_path