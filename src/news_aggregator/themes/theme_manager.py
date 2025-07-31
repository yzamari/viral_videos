"""Theme Manager for News Videos"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

from ...utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ThemePosition:
    """Position configuration for theme elements"""
    x: int
    y: int
    anchor: str = "top-left"  # top-left, center, bottom-right, etc.
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemePosition':
        return cls(**data)


@dataclass
class FontConfig:
    """Font configuration"""
    family: str
    size: int
    weight: str = "normal"  # normal, bold
    color: str = "#FFFFFF"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FontConfig':
        return cls(**data)


@dataclass
class NewsTheme:
    """Complete theme configuration for news videos"""
    name: str
    style: Dict[str, Any]
    layout: Dict[str, Any]
    audio: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def primary_color(self) -> str:
        return self.style.get("colors", {}).get("primary", "#1E3A8A")
    
    @property
    def secondary_color(self) -> str:
        return self.style.get("colors", {}).get("secondary", "#3B82F6")
    
    @property
    def headline_font(self) -> FontConfig:
        font_data = self.style.get("fonts", {}).get("headline", {})
        return FontConfig.from_dict(font_data)
    
    @property
    def subtitle_font(self) -> FontConfig:
        font_data = self.style.get("fonts", {}).get("subtitle", {})
        return FontConfig.from_dict(font_data)
    
    def get_overlay_path(self, overlay_type: str) -> Optional[str]:
        """Get path for specific overlay graphic"""
        return self.style.get("overlays", {}).get(overlay_type)
    
    def get_position(self, element: str) -> ThemePosition:
        """Get position for specific element"""
        pos_data = self.layout.get(f"{element}_position", {"x": 0, "y": 0})
        return ThemePosition.from_dict(pos_data)


class ThemeManager:
    """Manages loading and applying themes"""
    
    def __init__(self, themes_dir: str = "src/news_aggregator/themes/templates"):
        self.themes_dir = themes_dir
        self.loaded_themes: Dict[str, NewsTheme] = {}
        
        # Create default themes if directory doesn't exist
        os.makedirs(themes_dir, exist_ok=True)
        self._create_default_themes()
    
    def load_theme(self, theme_path: str) -> NewsTheme:
        """Load theme from JSON file"""
        if theme_path in self.loaded_themes:
            return self.loaded_themes[theme_path]
        
        try:
            # Check if it's a theme name or full path
            if not theme_path.endswith('.json'):
                theme_path = os.path.join(self.themes_dir, f"{theme_path}.json")
            
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme = NewsTheme(**theme_data)
            self.loaded_themes[theme_path] = theme
            
            logger.info(f"Loaded theme: {theme.name}")
            return theme
            
        except Exception as e:
            logger.error(f"Failed to load theme {theme_path}: {str(e)}")
            raise
    
    def save_theme(self, theme: NewsTheme, filename: str):
        """Save theme to JSON file"""
        theme_path = os.path.join(self.themes_dir, filename)
        
        theme_data = {
            "name": theme.name,
            "style": theme.style,
            "layout": theme.layout,
            "audio": theme.audio,
            "metadata": theme.metadata
        }
        
        with open(theme_path, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved theme: {theme.name} to {theme_path}")
    
    def list_themes(self) -> List[str]:
        """List all available themes"""
        themes = []
        for file in os.listdir(self.themes_dir):
            if file.endswith('.json'):
                themes.append(file[:-5])  # Remove .json extension
        return themes
    
    def _create_default_themes(self):
        """Create default theme templates"""
        
        # Professional News Theme
        professional_news = {
            "name": "Professional News",
            "style": {
                "colors": {
                    "primary": "#1E3A8A",
                    "secondary": "#3B82F6",
                    "accent": "#EF4444",
                    "text": "#FFFFFF",
                    "background": "#000000",
                    "ticker_bg": "#1E3A8A",
                    "ticker_text": "#FFFFFF"
                },
                "fonts": {
                    "headline": {
                        "family": "Arial",
                        "size": 56,
                        "weight": "bold",
                        "color": "#FFFFFF"
                    },
                    "subtitle": {
                        "family": "Arial",
                        "size": 32,
                        "weight": "normal",
                        "color": "#FFFFFF"
                    },
                    "ticker": {
                        "family": "Arial",
                        "size": 24,
                        "weight": "normal",
                        "color": "#FFFFFF"
                    },
                    "timestamp": {
                        "family": "Arial",
                        "size": 20,
                        "weight": "normal",
                        "color": "#CCCCCC"
                    }
                },
                "overlays": {
                    "lower_third": "themes/assets/professional_lower_third.png",
                    "breaking_news": "themes/assets/breaking_news_banner.png",
                    "logo": "themes/assets/news_logo.png",
                    "ticker_bg": "themes/assets/ticker_background.png"
                }
            },
            "layout": {
                "headline_position": {"x": 100, "y": 100, "anchor": "top-left"},
                "subtitle_position": {"x": 960, "y": 920, "anchor": "center"},
                "ticker_position": {"x": 0, "y": 1000, "anchor": "bottom-left"},
                "logo_position": {"x": 1820, "y": 100, "anchor": "top-right"},
                "timestamp_position": {"x": 100, "y": 980, "anchor": "bottom-left"},
                "ticker_enabled": True,
                "ticker_height": 80,
                "presenter_enabled": True,
                "presenter_position": {"x": 1520, "y": 780, "anchor": "bottom-right"},
                "presenter_size": {"width": 400, "height": 400}
            },
            "audio": {
                "background_music": "themes/audio/professional_news_theme.mp3",
                "music_volume": 0.3,
                "transition_sound": "themes/audio/swoosh.mp3",
                "breaking_news_sound": "themes/audio/breaking_news.mp3"
            },
            "metadata": {
                "author": "ViralAI",
                "version": "1.0",
                "description": "Professional news channel theme with blue color scheme"
            }
        }
        
        # Modern Tech News Theme
        modern_tech = {
            "name": "Modern Tech News",
            "style": {
                "colors": {
                    "primary": "#10B981",
                    "secondary": "#34D399",
                    "accent": "#8B5CF6",
                    "text": "#FFFFFF",
                    "background": "#111827",
                    "ticker_bg": "#1F2937",
                    "ticker_text": "#10B981"
                },
                "fonts": {
                    "headline": {
                        "family": "Roboto",
                        "size": 48,
                        "weight": "bold",
                        "color": "#10B981"
                    },
                    "subtitle": {
                        "family": "Roboto",
                        "size": 28,
                        "weight": "normal",
                        "color": "#FFFFFF"
                    },
                    "ticker": {
                        "family": "Roboto Mono",
                        "size": 22,
                        "weight": "normal",
                        "color": "#34D399"
                    }
                },
                "overlays": {
                    "lower_third": "themes/assets/tech_lower_third.png",
                    "logo": "themes/assets/tech_logo.png"
                }
            },
            "layout": {
                "headline_position": {"x": 80, "y": 80, "anchor": "top-left"},
                "subtitle_position": {"x": 80, "y": 900, "anchor": "bottom-left"},
                "logo_position": {"x": 1840, "y": 80, "anchor": "top-right"},
                "ticker_enabled": False,
                "presenter_enabled": True,
                "presenter_position": {"x": 200, "y": 540, "anchor": "center-left"},
                "presenter_size": {"width": 300, "height": 300}
            },
            "audio": {
                "background_music": "themes/audio/tech_ambient.mp3",
                "music_volume": 0.2
            },
            "metadata": {
                "author": "ViralAI",
                "version": "1.0",
                "description": "Modern tech news theme with green accent colors"
            }
        }
        
        # Hebrew News Theme
        hebrew_news = {
            "name": "Hebrew News Channel",
            "style": {
                "colors": {
                    "primary": "#0038A8",
                    "secondary": "#FFFFFF",
                    "accent": "#D4AF37",
                    "text": "#FFFFFF",
                    "background": "#000033"
                },
                "fonts": {
                    "headline": {
                        "family": "Arial Hebrew",
                        "size": 52,
                        "weight": "bold",
                        "color": "#FFFFFF"
                    },
                    "subtitle": {
                        "family": "Arial Hebrew",
                        "size": 30,
                        "weight": "normal",
                        "color": "#D4AF37"
                    }
                },
                "overlays": {
                    "lower_third": "themes/assets/hebrew_lower_third.png",
                    "logo": "themes/assets/hebrew_news_logo.png"
                }
            },
            "layout": {
                "headline_position": {"x": 1820, "y": 100, "anchor": "top-right"},
                "subtitle_position": {"x": 1820, "y": 920, "anchor": "bottom-right"},
                "logo_position": {"x": 100, "y": 100, "anchor": "top-left"},
                "ticker_enabled": True,
                "ticker_position": {"x": 1920, "y": 1000, "anchor": "bottom-right"},
                "ticker_rtl": True,
                "presenter_enabled": True,
                "presenter_position": {"x": 400, "y": 780, "anchor": "bottom-left"}
            },
            "audio": {
                "background_music": "themes/audio/hebrew_news_theme.mp3",
                "music_volume": 0.25
            },
            "metadata": {
                "author": "ViralAI",
                "version": "1.0",
                "description": "Hebrew news theme with RTL support",
                "rtl": True
            }
        }
        
        # Save default themes if they don't exist
        themes = [
            ("professional_news.json", professional_news),
            ("modern_tech.json", modern_tech),
            ("hebrew_news.json", hebrew_news)
        ]
        
        for filename, theme_data in themes:
            theme_path = os.path.join(self.themes_dir, filename)
            if not os.path.exists(theme_path):
                with open(theme_path, 'w', encoding='utf-8') as f:
                    json.dump(theme_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Created default theme: {filename}")
    
    def apply_theme_to_video(self, theme: NewsTheme, video_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply theme settings to video configuration"""
        # Apply colors
        video_config["colors"] = theme.style.get("colors", {})
        
        # Apply fonts
        video_config["fonts"] = theme.style.get("fonts", {})
        
        # Apply layout
        video_config["layout"] = theme.layout
        
        # Apply audio settings
        video_config["audio"] = theme.audio
        
        # Apply RTL if needed
        if theme.metadata.get("rtl", False):
            video_config["text_direction"] = "rtl"
        
        return video_config