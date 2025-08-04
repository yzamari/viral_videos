"""Unit tests for theme manager"""

import pytest
import json
import os
from tempfile import TemporaryDirectory

from src.news_aggregator.themes.theme_manager import ThemeManager, NewsTheme, ThemePosition, FontConfig


class TestThemeManager:
    """Test theme management functionality"""
    
    @pytest.fixture
    def temp_themes_dir(self):
        """Create temporary themes directory"""
        with TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def theme_manager(self, temp_themes_dir):
        """Create theme manager with temp directory"""
        return ThemeManager(themes_dir=temp_themes_dir)
    
    def test_create_default_themes(self, theme_manager, temp_themes_dir):
        """Test default themes are created"""
        expected_themes = ["professional_news.json", "modern_tech.json", "hebrew_news.json"]
        
        for theme_file in expected_themes:
            assert os.path.exists(os.path.join(temp_themes_dir, theme_file))
    
    def test_load_theme(self, theme_manager, temp_themes_dir):
        """Test loading a theme"""
        # Create test theme
        test_theme = {
            "name": "Test Theme",
            "style": {
                "colors": {
                    "primary": "#FF0000",
                    "secondary": "#00FF00"
                },
                "fonts": {
                    "headline": {
                        "family": "Arial",
                        "size": 48,
                        "weight": "bold",
                        "color": "#FFFFFF"
                    }
                }
            },
            "layout": {
                "headline_position": {"x": 100, "y": 100, "anchor": "top-left"}
            },
            "audio": {
                "background_music": "test.mp3",
                "music_volume": 0.5
            }
        }
        
        theme_path = os.path.join(temp_themes_dir, "test_theme.json")
        with open(theme_path, 'w') as f:
            json.dump(test_theme, f)
        
        # Load theme
        loaded_theme = theme_manager.load_theme("test_theme")
        
        assert loaded_theme.name == "Test Theme"
        assert loaded_theme.primary_color == "#FF0000"
        assert loaded_theme.headline_font.family == "Arial"
        assert loaded_theme.headline_font.size == 48
    
    def test_hebrew_theme_rtl(self, theme_manager):
        """Test Hebrew theme has RTL support"""
        hebrew_theme = theme_manager.load_theme("hebrew_news")
        
        assert hebrew_theme.metadata.get("rtl", False) == True
        assert hebrew_theme.layout.get("ticker_rtl", False) == True
    
    def test_apply_theme_to_video(self, theme_manager):
        """Test applying theme to video config"""
        theme = theme_manager.load_theme("professional_news")
        video_config = {}
        
        updated_config = theme_manager.apply_theme_to_video(theme, video_config)
        
        assert "colors" in updated_config
        assert "fonts" in updated_config
        assert "layout" in updated_config
        assert "audio" in updated_config
    
    def test_position_from_dict(self):
        """Test creating position from dictionary"""
        pos_data = {"x": 100, "y": 200, "anchor": "center"}
        position = ThemePosition.from_dict(pos_data)
        
        assert position.x == 100
        assert position.y == 200
        assert position.anchor == "center"


class TestYnetTheme:
    """Test Ynet-specific theme configuration"""
    
    @pytest.fixture
    def ynet_theme_data(self):
        """Create Ynet-style theme data"""
        return {
            "name": "Ynet News Style",
            "style": {
                "colors": {
                    "primary": "#D40000",  # Ynet red
                    "secondary": "#FFFFFF",
                    "accent": "#000000",
                    "text": "#FFFFFF",
                    "background": "#F5F5F5",
                    "ticker_bg": "#D40000",
                    "ticker_text": "#FFFFFF"
                },
                "fonts": {
                    "headline": {
                        "family": "Arial Hebrew",
                        "size": 52,
                        "weight": "bold",
                        "color": "#000000"
                    },
                    "subtitle": {
                        "family": "Arial Hebrew",
                        "size": 28,
                        "weight": "normal",
                        "color": "#666666"
                    }
                },
                "overlays": {
                    "logo": "themes/assets/ynet_logo.png",
                    "lower_third": "themes/assets/ynet_lower_third.png",
                    "breaking": "themes/assets/ynet_breaking.png"
                }
            },
            "layout": {
                "headline_position": {"x": 50, "y": 850, "anchor": "bottom-left"},
                "logo_position": {"x": 50, "y": 50, "anchor": "top-left"},
                "alien_position": {"x": 1720, "y": 880, "anchor": "bottom-right"},
                "alien_size": {"width": 200, "height": 200}
            },
            "audio": {
                "background_music": "themes/audio/ynet_theme.mp3",
                "music_volume": 0.2
            },
            "metadata": {
                "rtl": True,
                "style": "news_website"
            }
        }
    
    def test_ynet_theme_colors(self, ynet_theme_data):
        """Test Ynet theme has correct brand colors"""
        theme = NewsTheme(**ynet_theme_data)
        assert theme.primary_color == "#D40000"  # Ynet red
        assert theme.style["colors"]["background"] == "#F5F5F5"