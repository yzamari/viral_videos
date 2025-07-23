"""
Unit tests for Theme Manager
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.themes.managers.theme_manager import ThemeManager
from src.themes.models.theme import Theme, ThemeCategory, TransitionStyle
from src.themes.presets.news_edition import NewsEditionTheme


class TestThemeManager:
    """Test theme manager functionality"""
    
    @pytest.fixture
    def temp_themes_dir(self):
        """Create temporary themes directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def theme_manager(self, temp_themes_dir):
        """Create theme manager with temp directory"""
        return ThemeManager(temp_themes_dir)
    
    @pytest.fixture
    def sample_theme(self):
        """Create sample theme for testing"""
        return Theme(
            theme_id="test_theme_001",
            name="Test Theme",
            category=ThemeCategory.CUSTOM,
            version="1.0.0",
            description="A test theme",
            tags=["test", "sample"],
            content_tone="professional",
            content_style="informative",
            default_duration=60
        )
    
    def test_initialization(self, theme_manager, temp_themes_dir):
        """Test theme manager initialization"""
        assert theme_manager.themes_dir == Path(temp_themes_dir)
        assert theme_manager.custom_themes_dir.exists()
        assert theme_manager.metadata_file.exists()
        
        # Check metadata structure
        with open(theme_manager.metadata_file, 'r') as f:
            metadata = json.load(f)
        
        assert "version" in metadata
        assert "themes" in metadata
        assert "categories" in metadata
        assert all(cat.value in metadata["categories"] for cat in ThemeCategory)
    
    def test_preset_themes_loaded(self, theme_manager):
        """Test that preset themes are loaded"""
        assert len(theme_manager.preset_themes) == 4
        assert "preset_news_edition" in theme_manager.preset_themes
        assert "preset_sports" in theme_manager.preset_themes
        assert "preset_tech" in theme_manager.preset_themes
        assert "preset_entertainment" in theme_manager.preset_themes
        
        # Check preset theme properties
        news_theme = theme_manager.preset_themes["preset_news_edition"]
        assert isinstance(news_theme, NewsEditionTheme)
        assert news_theme.category == ThemeCategory.NEWS
    
    def test_save_theme(self, theme_manager, sample_theme):
        """Test saving a custom theme"""
        theme_id = theme_manager.save_theme(sample_theme)
        
        assert theme_id == "test_theme_001"
        
        # Check theme file exists
        theme_file = theme_manager.custom_themes_dir / f"{theme_id}.json"
        assert theme_file.exists()
        
        # Check metadata updated
        metadata = theme_manager._load_metadata()
        assert theme_id in metadata["themes"]
        assert metadata["themes"][theme_id]["name"] == "Test Theme"
        assert theme_id in metadata["categories"][ThemeCategory.CUSTOM.value]
    
    def test_save_theme_overwrite(self, theme_manager, sample_theme):
        """Test overwriting existing theme"""
        # Save once
        theme_manager.save_theme(sample_theme)
        
        # Try to save again without overwrite
        with pytest.raises(ValueError, match="already exists"):
            theme_manager.save_theme(sample_theme, overwrite=False)
        
        # Save with overwrite
        sample_theme.description = "Updated description"
        theme_id = theme_manager.save_theme(sample_theme, overwrite=True)
        
        # Verify update
        loaded = theme_manager.load_theme(theme_id)
        assert loaded is not None
    
    def test_load_preset_theme(self, theme_manager):
        """Test loading preset theme"""
        theme = theme_manager.load_theme("preset_news_edition")
        
        assert theme is not None
        assert theme.name == "News Edition"
        assert theme.category == ThemeCategory.NEWS
        assert theme.style_reference is not None
    
    def test_load_custom_theme(self, theme_manager, sample_theme):
        """Test loading custom theme"""
        # Save first
        theme_id = theme_manager.save_theme(sample_theme)
        
        # Load back
        loaded = theme_manager.load_theme(theme_id)
        
        assert loaded is not None
        assert loaded.name == sample_theme.name
        assert loaded.theme_id == theme_id
    
    def test_load_nonexistent_theme(self, theme_manager):
        """Test loading non-existent theme"""
        theme = theme_manager.load_theme("fake_theme_id")
        assert theme is None
    
    def test_load_theme_by_name(self, theme_manager, sample_theme):
        """Test loading theme by name"""
        # Test preset
        theme = theme_manager.load_theme_by_name("News Edition")
        assert theme is not None
        assert theme.theme_id == "preset_news_edition"
        
        # Test custom
        theme_manager.save_theme(sample_theme)
        loaded = theme_manager.load_theme_by_name("Test Theme")
        assert loaded is not None
        assert loaded.theme_id == sample_theme.theme_id
        
        # Test case insensitive
        loaded = theme_manager.load_theme_by_name("test theme")
        assert loaded is not None
    
    def test_list_themes(self, theme_manager, sample_theme):
        """Test listing themes"""
        # List all themes (should include presets)
        all_themes = theme_manager.list_themes()
        assert len(all_themes) >= 4  # At least 4 presets
        
        # Save custom theme
        theme_manager.save_theme(sample_theme)
        
        # List again
        all_themes = theme_manager.list_themes()
        assert len(all_themes) >= 5
        
        # Check structure
        for theme_info in all_themes:
            assert "theme_id" in theme_info
            assert "name" in theme_info
            assert "category" in theme_info
            assert "is_preset" in theme_info
    
    def test_list_themes_by_category(self, theme_manager):
        """Test filtering themes by category"""
        news_themes = theme_manager.list_themes(category=ThemeCategory.NEWS)
        assert len(news_themes) >= 1
        assert all(t["category"] == "news" for t in news_themes)
        
        sports_themes = theme_manager.list_themes(category=ThemeCategory.SPORTS)
        assert len(sports_themes) >= 1
        assert all(t["category"] == "sports" for t in sports_themes)
    
    def test_search_themes(self, theme_manager, sample_theme):
        """Test searching themes"""
        # Search in presets
        results = theme_manager.search_themes("news")
        assert len(results) >= 1
        assert any("news" in r["name"].lower() for r in results)
        
        # Save custom theme with specific tags
        sample_theme.tags = ["vintage", "retro", "classic"]
        sample_theme.description = "A vintage style theme"
        theme_manager.save_theme(sample_theme)
        
        # Search by tag
        results = theme_manager.search_themes("vintage")
        assert len(results) >= 1
        assert sample_theme.theme_id in [r["theme_id"] for r in results]
        
        # Search by description
        results = theme_manager.search_themes("style")
        assert len(results) >= 1
    
    def test_delete_theme(self, theme_manager, sample_theme):
        """Test deleting theme"""
        # Save theme
        theme_id = theme_manager.save_theme(sample_theme)
        
        # Verify it exists
        assert theme_manager.load_theme(theme_id) is not None
        
        # Delete
        success = theme_manager.delete_theme(theme_id)
        assert success is True
        
        # Verify it's gone
        assert theme_manager.load_theme(theme_id) is None
        
        # Check metadata updated
        metadata = theme_manager._load_metadata()
        assert theme_id not in metadata["themes"]
        assert theme_id not in metadata["categories"][ThemeCategory.CUSTOM.value]
    
    def test_cannot_delete_preset(self, theme_manager):
        """Test that preset themes cannot be deleted"""
        success = theme_manager.delete_theme("preset_news_edition")
        assert success is False
        
        # Verify preset still exists
        assert theme_manager.load_theme("preset_news_edition") is not None
    
    def test_duplicate_theme(self, theme_manager):
        """Test duplicating theme"""
        # Duplicate preset
        new_id = theme_manager.duplicate_theme("preset_news_edition", "My News Theme")
        
        assert new_id is not None
        assert new_id != "preset_news_edition"
        
        # Load duplicated theme
        new_theme = theme_manager.load_theme(new_id)
        assert new_theme is not None
        assert new_theme.name == "My News Theme"
        assert new_theme.parent_theme_id == "preset_news_edition"
        assert "duplicated" in new_theme.tags
    
    def test_export_import_theme(self, theme_manager, sample_theme, tmp_path):
        """Test exporting and importing themes"""
        # Save theme first
        theme_id = theme_manager.save_theme(sample_theme)
        
        # Export
        export_path = tmp_path / "exported_theme.json"
        success = theme_manager.export_theme(theme_id, str(export_path))
        assert success is True
        assert export_path.exists()
        
        # Check export structure
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert "version" in export_data
        assert "exported_at" in export_data
        assert "theme" in export_data
        
        # Import with new name
        imported_id = theme_manager.import_theme(
            str(export_path),
            new_name="Imported Theme"
        )
        
        assert imported_id is not None
        assert imported_id != theme_id  # Should have new ID
        
        # Verify imported theme
        imported = theme_manager.load_theme(imported_id)
        assert imported is not None
        assert imported.name == "Imported Theme"