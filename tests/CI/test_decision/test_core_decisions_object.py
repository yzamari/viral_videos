"""
Tests for CoreDecisions Object
Ensures CoreDecisions object is properly created and propagated
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from dataclasses import fields, is_dataclass

from src.core.entities import CoreDecisions, GeneratedVideoConfig


class TestCoreDecisionsObject:
    """Test suite for CoreDecisions object"""
    
    @pytest.fixture
    def sample_video_config(self):
        """Create sample video configuration"""
        return GeneratedVideoConfig(
            topic="Artificial Intelligence",
            duration=60,
            platform="youtube",
            language="en"
        )
    
    @pytest.fixture
    def core_decisions(self, sample_video_config):
        """Create CoreDecisions instance"""
        return CoreDecisions(
            video_config=sample_video_config,
            mission="Explain AI benefits",
            target_platform="youtube",
            language="en",
            duration=60
        )
    
    @pytest.mark.unit
    def test_core_decisions_creation(self, sample_video_config):
        """Test CoreDecisions object creation"""
        decisions = CoreDecisions(
            video_config=sample_video_config,
            mission="Test mission",
            target_platform="youtube",
            language="en",
            duration=60
        )
        
        assert decisions is not None
        assert decisions.video_config == sample_video_config
        assert decisions.mission == "Test mission"
        assert decisions.target_platform == "youtube"
        assert decisions.language == "en"
        assert decisions.duration == 60
    
    @pytest.mark.unit
    def test_core_decisions_dataclass(self):
        """Test that CoreDecisions is a proper dataclass"""
        assert is_dataclass(CoreDecisions)
        
        # Check required fields
        field_names = {f.name for f in fields(CoreDecisions)}
        required_fields = {
            'video_config', 'mission', 'target_platform', 
            'language', 'duration'
        }
        
        assert required_fields.issubset(field_names)
    
    @pytest.mark.unit
    def test_core_decisions_additional_attributes(self, core_decisions):
        """Test adding additional decision attributes"""
        # Add style decisions
        core_decisions.visual_style = "modern minimalist"
        core_decisions.color_palette = ["blue", "white", "gray"]
        core_decisions.font_family = "Helvetica"
        
        # Add audio decisions
        core_decisions.voice_type = "professional_female"
        core_decisions.background_music = "ambient_tech"
        core_decisions.sound_effects_enabled = True
        
        # Add content decisions
        core_decisions.content_strategy = "educational"
        core_decisions.emotional_arc = ["curiosity", "understanding", "inspiration"]
        core_decisions.key_messages = ["AI is accessible", "AI enhances human capability"]
        
        # Verify all attributes are stored
        assert core_decisions.visual_style == "modern minimalist"
        assert len(core_decisions.color_palette) == 3
        assert core_decisions.voice_type == "professional_female"
        assert core_decisions.content_strategy == "educational"
    
    @pytest.mark.unit
    def test_core_decisions_serialization(self, core_decisions):
        """Test CoreDecisions serialization for storage"""
        # Add various decision types
        core_decisions.visual_style = "cinematic"
        core_decisions.transitions = ["fade", "cut", "dissolve"]
        core_decisions.aspect_ratio = "16:9"
        core_decisions.quality_preset = "high"
        
        # Convert to dict
        decisions_dict = {
            "video_config": {
                "topic": core_decisions.video_config.topic,
                "duration": core_decisions.video_config.duration,
                "platform": core_decisions.video_config.platform,
                "language": core_decisions.video_config.language
            },
            "mission": core_decisions.mission,
            "target_platform": core_decisions.target_platform,
            "language": core_decisions.language,
            "duration": core_decisions.duration,
            "visual_style": core_decisions.visual_style,
            "transitions": core_decisions.transitions,
            "aspect_ratio": core_decisions.aspect_ratio,
            "quality_preset": core_decisions.quality_preset
        }
        
        # Should be JSON serializable
        json_str = json.dumps(decisions_dict)
        assert json_str is not None
        
        # Deserialize and verify
        loaded = json.loads(json_str)
        assert loaded["mission"] == core_decisions.mission
        assert loaded["visual_style"] == "cinematic"
        assert len(loaded["transitions"]) == 3
    
    @pytest.mark.unit
    def test_core_decisions_validation(self, sample_video_config):
        """Test CoreDecisions validation"""
        # Test with invalid duration
        with pytest.raises(ValueError):
            CoreDecisions(
                video_config=sample_video_config,
                mission="Test",
                target_platform="youtube",
                language="en",
                duration=-10  # Invalid
            )
        
        # Test with empty mission
        with pytest.raises(ValueError):
            CoreDecisions(
                video_config=sample_video_config,
                mission="",  # Invalid
                target_platform="youtube",
                language="en",
                duration=60
            )
        
        # Test with invalid platform
        with pytest.raises(ValueError):
            CoreDecisions(
                video_config=sample_video_config,
                mission="Test",
                target_platform="invalid_platform",  # Invalid
                language="en",
                duration=60
            )
    
    @pytest.mark.unit
    def test_core_decisions_propagation_tracking(self, core_decisions):
        """Test tracking of decision propagation to components"""
        # Add propagation tracking
        core_decisions._propagated_to = []
        
        # Simulate propagation to components
        components = [
            "VideoGenerator",
            "AudioGenerator",
            "ScriptWriter",
            "OverlayGenerator",
            "SubtitleGenerator"
        ]
        
        for component in components:
            # Component receives decisions
            core_decisions._propagated_to.append({
                "component": component,
                "timestamp": "2024-01-20T10:00:00",
                "success": True
            })
        
        # Verify all components received decisions
        assert len(core_decisions._propagated_to) == len(components)
        propagated_components = {p["component"] for p in core_decisions._propagated_to}
        assert propagated_components == set(components)
    
    @pytest.mark.unit
    def test_core_decisions_platform_specific(self):
        """Test platform-specific decision attributes"""
        platforms = {
            "youtube": {
                "aspect_ratio": "16:9",
                "max_duration": 600,
                "features": ["chapters", "cards", "end_screen"]
            },
            "instagram": {
                "aspect_ratio": "9:16",
                "max_duration": 60,
                "features": ["stories", "reels", "igtv"]
            },
            "tiktok": {
                "aspect_ratio": "9:16",
                "max_duration": 180,
                "features": ["effects", "sounds", "duet"]
            }
        }
        
        for platform, expected in platforms.items():
            config = GeneratedVideoConfig(
                topic="Test",
                duration=30,
                platform=platform,
                language="en"
            )
            
            decisions = CoreDecisions(
                video_config=config,
                mission="Test",
                target_platform=platform,
                language="en",
                duration=30
            )
            
            # Add platform-specific attributes
            decisions.aspect_ratio = expected["aspect_ratio"]
            decisions.max_duration = expected["max_duration"]
            decisions.platform_features = expected["features"]
            
            # Verify
            assert decisions.aspect_ratio == expected["aspect_ratio"]
            assert decisions.max_duration == expected["max_duration"]
            assert decisions.platform_features == expected["features"]
    
    @pytest.mark.unit
    def test_core_decisions_cheap_mode_attributes(self, sample_video_config):
        """Test cheap mode specific attributes"""
        # Normal mode
        normal_decisions = CoreDecisions(
            video_config=sample_video_config,
            mission="Test",
            target_platform="youtube",
            language="en",
            duration=60
        )
        normal_decisions.cheap_mode_level = None
        normal_decisions.use_veo = True
        normal_decisions.use_premium_voices = True
        
        # Cheap mode
        cheap_decisions = CoreDecisions(
            video_config=sample_video_config,
            mission="Test",
            target_platform="youtube",
            language="en",
            duration=60
        )
        cheap_decisions.cheap_mode_level = "full"
        cheap_decisions.use_veo = False
        cheap_decisions.use_premium_voices = False
        cheap_decisions.use_simple_effects = True
        
        # Verify differences
        assert normal_decisions.use_veo is True
        assert cheap_decisions.use_veo is False
        assert normal_decisions.use_premium_voices is True
        assert cheap_decisions.use_premium_voices is False
    
    @pytest.mark.unit
    def test_core_decisions_multilingual_attributes(self, sample_video_config):
        """Test multilingual-specific decision attributes"""
        languages = ["en", "es", "fr", "ar", "he", "ja"]
        
        for language in languages:
            config = GeneratedVideoConfig(
                topic="Test",
                duration=60,
                platform="youtube",
                language=language
            )
            
            decisions = CoreDecisions(
                video_config=config,
                mission="Test",
                target_platform="youtube",
                language=language,
                duration=60
            )
            
            # Add language-specific attributes
            decisions.text_direction = "rtl" if language in ["ar", "he"] else "ltr"
            decisions.subtitle_position = "top" if language in ["ja", "zh"] else "bottom"
            decisions.voice_gender_preference = "female" if language in ["fr", "es"] else "neutral"
            
            # Verify
            if language in ["ar", "he"]:
                assert decisions.text_direction == "rtl"
            else:
                assert decisions.text_direction == "ltr"
    
    @pytest.mark.unit
    def test_core_decisions_immutability_recommendation(self, core_decisions):
        """Test that CoreDecisions recommends immutability patterns"""
        # Original values
        original_mission = core_decisions.mission
        original_duration = core_decisions.duration
        
        # These should not change during execution
        # Components should read but not modify
        assert core_decisions.mission == original_mission
        assert core_decisions.duration == original_duration
        
        # Best practice: Create new decisions rather than modify
        modified_config = GeneratedVideoConfig(
            topic=core_decisions.video_config.topic,
            duration=90,  # Changed
            platform=core_decisions.video_config.platform,
            language=core_decisions.video_config.language
        )
        
        new_decisions = CoreDecisions(
            video_config=modified_config,
            mission=core_decisions.mission,
            target_platform=core_decisions.target_platform,
            language=core_decisions.language,
            duration=90  # Changed
        )
        
        # Original unchanged
        assert core_decisions.duration == original_duration
        # New has changes
        assert new_decisions.duration == 90
    
    @pytest.mark.integration
    def test_core_decisions_with_all_components(self, core_decisions, mock_session_context):
        """Test CoreDecisions integration with all system components"""
        # Add comprehensive decisions
        core_decisions.visual_style = "modern"
        core_decisions.audio_style = "professional"
        core_decisions.content_strategy = "educational"
        core_decisions.quality_level = "high"
        core_decisions.enable_captions = True
        core_decisions.enable_music = True
        core_decisions.enable_effects = True
        
        # Mock all components
        components = {
            "video_generator": Mock(),
            "audio_generator": Mock(),
            "script_writer": Mock(),
            "overlay_generator": Mock(),
            "subtitle_generator": Mock(),
            "effect_processor": Mock(),
            "quality_controller": Mock()
        }
        
        # Pass decisions to all components
        for name, component in components.items():
            component.process(core_decisions)
            
            # Verify component received complete decisions
            component.process.assert_called_once_with(core_decisions)
            
            # Component should have access to all decision attributes
            call_args = component.process.call_args[0][0]
            assert hasattr(call_args, 'visual_style')
            assert hasattr(call_args, 'audio_style')
            assert hasattr(call_args, 'content_strategy')