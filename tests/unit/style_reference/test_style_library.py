"""
Unit tests for Style Library Manager
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.style_reference.managers.style_library import StyleLibrary
from src.style_reference.models.style_reference import StyleReference
from src.style_reference.models.style_attributes import (
    ReferenceType, ColorPalette, Typography, Composition, MotionStyle
)


class TestStyleLibrary:
    """Test style library functionality"""
    
    @pytest.fixture
    def temp_library_path(self):
        """Create temporary library directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def library(self, temp_library_path):
        """Create library instance with temp path"""
        return StyleLibrary(temp_library_path)
    
    @pytest.fixture
    def sample_style(self):
        """Create sample style reference"""
        return StyleReference(
            reference_id="test_ref_001",
            name="Test Style",
            reference_type=ReferenceType.VIDEO,
            source_path="/path/to/video.mp4",
            template_id=None,
            color_palette=ColorPalette(
                primary_color="#FF0000",
                secondary_color="#00FF00",
                accent_color="#0000FF",
                background_colors=["#FFFFFF", "#000000"],
                text_colors=["#FFFFFF", "#000000"],
                saturation_level=0.8,
                brightness_level=0.6,
                contrast_ratio=0.7,
                mood="vibrant"
            ),
            typography=Typography(
                primary_font_family=None,
                secondary_font_family=None,
                title_size_ratio=0.1,
                body_size_ratio=0.05,
                font_weight="regular",
                letter_spacing=1.0,
                line_height=1.2,
                has_shadow=False,
                has_outline=False,
                text_animation_style=None
            ),
            composition=Composition(
                rule_of_thirds_adherence=0.8,
                symmetry_score=0.6,
                primary_layout="centered",
                text_placement_zones=["lower-third"],
                margin_ratio=0.1,
                padding_ratio=0.05,
                focal_point_strategy="center",
                depth_layers=3
            ),
            motion_style=MotionStyle(
                camera_movement="static",
                transition_style="cut",
                average_shot_duration=3.5,
                movement_intensity=0.3,
                text_animation_type=None,
                element_animation_style=None,
                pacing="medium",
                rhythm_pattern=None
            ),
            visual_effects=[],
            logo_placement=None,
            watermark=None,
            lower_thirds=None,
            aspect_ratio="16:9",
            resolution="1920x1080",
            frame_rate=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["test", "sample"],
            description="Test style for unit testing",
            confidence_scores={"overall": 0.85}
        )
    
    def test_library_initialization(self, library, temp_library_path):
        """Test library initialization"""
        assert library.library_path == Path(temp_library_path)
        assert library.templates_dir.exists()
        assert library.metadata_file.exists()
    
    def test_save_style(self, library, sample_style):
        """Test saving a style template"""
        template_id = library.save_style(
            sample_style,
            "My Test Template",
            tags=["test", "custom"],
            description="A test template"
        )
        
        assert template_id is not None
        assert template_id.startswith("template_")
        
        # Check template file exists
        template_file = library.templates_dir / f"{template_id}.json"
        assert template_file.exists()
        
        # Check metadata updated
        metadata = library._load_metadata()
        assert template_id in metadata["templates"]
        assert metadata["templates"][template_id]["name"] == "My Test Template"
    
    def test_load_style_by_id(self, library, sample_style):
        """Test loading style by template ID"""
        # Save first
        template_id = library.save_style(sample_style, "Test Template")
        
        # Load by ID
        loaded_style = library.load_style(template_id)
        
        assert loaded_style is not None
        assert loaded_style.name == "Test Template"
        assert loaded_style.template_id == template_id
        assert loaded_style.color_palette.primary_color == "#FF0000"
    
    def test_load_style_by_name(self, library, sample_style):
        """Test loading style by template name"""
        # Save first
        template_name = "Unique Template Name"
        library.save_style(sample_style, template_name)
        
        # Load by name
        loaded_style = library.load_style_by_name(template_name)
        
        assert loaded_style is not None
        assert loaded_style.name == template_name
    
    def test_search_styles(self, library, sample_style):
        """Test searching styles"""
        # Save multiple styles
        library.save_style(sample_style, "Red Style", tags=["red", "vibrant"])
        library.save_style(sample_style, "Blue Style", tags=["blue", "calm"])
        library.save_style(sample_style, "Green Style", tags=["green", "nature"])
        
        # Search by query
        results = library.search_styles(query="Blue")
        assert len(results) == 1
        assert results[0]["name"] == "Blue Style"
        
        # Search by tags
        results = library.search_styles(tags=["vibrant"])
        assert len(results) == 1
        assert results[0]["name"] == "Red Style"
    
    def test_list_all_styles(self, library, sample_style):
        """Test listing all styles"""
        # Save multiple styles
        library.save_style(sample_style, "Style 1")
        library.save_style(sample_style, "Style 2")
        library.save_style(sample_style, "Style 3")
        
        # List all
        results = library.list_styles()
        assert len(results) == 3
    
    def test_delete_style(self, library, sample_style):
        """Test deleting a style"""
        # Save first
        template_id = library.save_style(sample_style, "To Delete")
        
        # Verify it exists
        assert library.load_style(template_id) is not None
        
        # Delete
        success = library.delete_style(template_id)
        assert success is True
        
        # Verify it's gone
        assert library.load_style(template_id) is None
        
        # Try deleting non-existent
        assert library.delete_style("fake_id") is False
    
    def test_get_preset_styles(self, library):
        """Test getting preset styles"""
        presets = library.get_preset_styles()
        
        assert len(presets) > 0
        assert any(p["name"] == "News Broadcast" for p in presets)
        assert any(p["name"] == "Cinematic" for p in presets)
        
        # Check preset structure
        for preset in presets:
            assert "name" in preset
            assert "description" in preset
            assert "tags" in preset
            assert "template_id" in preset
    
    def test_style_similarity(self, sample_style):
        """Test style similarity calculation"""
        # Create similar style
        similar_style = sample_style
        score = sample_style.similarity_score(similar_style)
        assert score == pytest.approx(1.0, rel=0.1)  # Should be very similar
        
        # Create different style
        different_style = StyleReference(
            reference_id="different",
            name="Different",
            reference_type=ReferenceType.VIDEO,
            source_path=None,
            template_id=None,
            color_palette=ColorPalette(
                primary_color="#000000",
                secondary_color="#FFFFFF",
                accent_color="#808080",
                background_colors=[],
                text_colors=[],
                saturation_level=0.1,
                brightness_level=0.1,
                contrast_ratio=0.1,
                mood="dark"
            ),
            typography=sample_style.typography,
            composition=sample_style.composition,
            motion_style=MotionStyle(
                camera_movement="dynamic",
                transition_style="fade",
                average_shot_duration=1.0,
                movement_intensity=0.9,
                text_animation_type=None,
                element_animation_style=None,
                pacing="fast",
                rhythm_pattern=None
            ),
            visual_effects=[],
            logo_placement=None,
            watermark=None,
            lower_thirds=None,
            aspect_ratio="9:16",  # Different aspect ratio
            resolution="1080x1920",
            frame_rate=60,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=[],
            description=None,
            confidence_scores={}
        )
        
        different_score = sample_style.similarity_score(different_style)
        assert different_score < 0.7  # Should be less similar