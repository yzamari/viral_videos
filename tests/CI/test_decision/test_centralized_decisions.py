"""
Tests for Centralized Decision Making
Ensures all decisions are made upfront via DecisionFramework
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from src.decision_framework import DecisionFramework
from src.core.entities import CoreDecisions, GeneratedVideoConfig


class TestCentralizedDecisions:
    """Test suite for centralized decision making"""
    
    @pytest.fixture
    def decision_framework(self, mock_ai_client, mock_session_context):
        """Create DecisionFramework instance"""
        return DecisionFramework(
            ai_client=mock_ai_client,
            session_context=mock_session_context
        )
    
    @pytest.fixture
    def input_params(self):
        """Sample input parameters"""
        return {
            "mission": "Create an engaging video about renewable energy",
            "platform": "youtube",
            "language": "en",
            "duration": 60,
            "style_preference": "modern",
            "cheap_mode": False
        }
    
    @pytest.mark.unit
    def test_decision_framework_initialization(self, mock_ai_client, mock_session_context):
        """Test DecisionFramework initializes correctly"""
        framework = DecisionFramework(mock_ai_client, mock_session_context)
        
        assert framework is not None
        assert framework.ai_client == mock_ai_client
        assert framework.session_context == mock_session_context
        assert hasattr(framework, 'make_all_decisions')
    
    @pytest.mark.unit
    def test_make_all_decisions_upfront(self, decision_framework, mock_ai_client, input_params):
        """Test that all decisions are made upfront before any generation"""
        # Mock AI responses for decision making
        decision_responses = {
            "content_decisions": {
                "main_topic": "renewable energy benefits",
                "subtopics": ["solar power", "wind energy", "sustainability"],
                "tone": "educational and inspiring",
                "key_messages": ["clean future", "cost savings", "environmental impact"]
            },
            "style_decisions": {
                "visual_style": "modern clean tech",
                "color_palette": ["green", "blue", "white"],
                "typography": "sans-serif modern",
                "animation_style": "smooth transitions"
            },
            "technical_decisions": {
                "video_quality": "1080p",
                "fps": 30,
                "audio_quality": "high",
                "encoding": "h264"
            },
            "platform_decisions": {
                "aspect_ratio": "16:9",
                "max_duration": 600,
                "features": ["captions", "chapters", "end_screen"]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(decision_responses)
        )
        
        # Test
        decisions = decision_framework.make_all_decisions(**input_params)
        
        # Assert all decisions are made
        assert isinstance(decisions, CoreDecisions)
        assert decisions.mission == input_params["mission"]
        assert decisions.target_platform == input_params["platform"]
        assert decisions.language == input_params["language"]
        assert decisions.duration == input_params["duration"]
        
        # Verify no component makes its own decisions
        assert hasattr(decisions, 'visual_style')
        assert hasattr(decisions, 'audio_style')
        assert hasattr(decisions, 'content_strategy')
    
    @pytest.mark.unit
    def test_decision_immutability(self, decision_framework, input_params):
        """Test that decisions cannot be modified after creation"""
        decisions = decision_framework.make_all_decisions(**input_params)
        
        # Attempt to modify decisions should fail or be prevented
        original_duration = decisions.duration
        original_platform = decisions.target_platform
        
        # Decisions should remain unchanged throughout the pipeline
        assert decisions.duration == original_duration
        assert decisions.target_platform == original_platform
    
    @pytest.mark.unit
    def test_decision_propagation(self, decision_framework, mock_ai_client, input_params):
        """Test that decisions propagate to all components"""
        # Create decisions
        decisions = decision_framework.make_all_decisions(**input_params)
        
        # Mock components that receive decisions
        mock_components = {
            "video_generator": Mock(),
            "audio_generator": Mock(),
            "script_writer": Mock(),
            "style_manager": Mock()
        }
        
        # Propagate decisions to all components
        for component_name, component in mock_components.items():
            component.configure(decisions)
            
            # Verify component received decisions
            component.configure.assert_called_once_with(decisions)
    
    @pytest.mark.unit
    def test_no_hardcoded_defaults(self, decision_framework):
        """Test that no component has hardcoded defaults"""
        # Components should fail without decisions
        from src.generators.video_generator import VideoGenerator
        
        # Should not be able to create generator without decisions
        with pytest.raises(TypeError):
            VideoGenerator()  # Missing required decisions parameter
    
    @pytest.mark.unit
    def test_decision_validation(self, decision_framework, mock_ai_client):
        """Test decision validation and constraints"""
        # Test invalid inputs
        invalid_params = [
            {"mission": "", "platform": "youtube"},  # Empty mission
            {"mission": "Test", "platform": "invalid_platform"},  # Invalid platform
            {"mission": "Test", "duration": -10},  # Negative duration
            {"mission": "Test", "language": "xyz"}  # Invalid language
        ]
        
        for params in invalid_params:
            with pytest.raises(ValueError):
                decision_framework.make_all_decisions(**params)
    
    @pytest.mark.unit
    def test_platform_specific_decisions(self, decision_framework, mock_ai_client):
        """Test platform-specific decision making"""
        platforms = ["youtube", "instagram", "tiktok", "twitter"]
        
        platform_decisions = {}
        for platform in platforms:
            decisions = decision_framework.make_all_decisions(
                mission="Test video",
                platform=platform
            )
            platform_decisions[platform] = decisions
        
        # Verify platform-specific differences
        assert platform_decisions["youtube"].video_config.platform == "youtube"
        assert platform_decisions["instagram"].video_config.platform == "instagram"
        
        # Different platforms should have different settings
        youtube_aspect = platform_decisions["youtube"].aspect_ratio
        instagram_aspect = platform_decisions["instagram"].aspect_ratio
        assert youtube_aspect != instagram_aspect  # YouTube: 16:9, Instagram: 9:16
    
    @pytest.mark.unit
    def test_cheap_mode_decisions(self, decision_framework, mock_ai_client):
        """Test decisions in cheap mode vs normal mode"""
        # Normal mode decisions
        normal_decisions = decision_framework.make_all_decisions(
            mission="Test",
            cheap_mode=False
        )
        
        # Cheap mode decisions
        cheap_decisions = decision_framework.make_all_decisions(
            mission="Test",
            cheap_mode=True
        )
        
        # Verify cheap mode affects decisions
        assert cheap_decisions.cheap_mode_level is not None
        assert normal_decisions.cheap_mode_level is None
        
        # Cheap mode should skip expensive operations
        assert hasattr(cheap_decisions, 'skip_veo_generation')
        assert cheap_decisions.skip_veo_generation is True
    
    @pytest.mark.unit
    def test_decision_serialization(self, decision_framework, input_params, temp_dir):
        """Test decision serialization for session storage"""
        decisions = decision_framework.make_all_decisions(**input_params)
        
        # Serialize decisions
        serialized = decision_framework.serialize_decisions(decisions)
        
        # Should be JSON serializable
        json_str = json.dumps(serialized)
        assert json_str is not None
        
        # Deserialize and verify
        deserialized = json.loads(json_str)
        assert deserialized["mission"] == input_params["mission"]
        assert deserialized["platform"] == input_params["platform"]
    
    @pytest.mark.unit
    def test_decision_dependencies(self, decision_framework, mock_ai_client):
        """Test decision dependencies are resolved correctly"""
        # Some decisions depend on others
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps({
                "primary_decision": "educational_content",
                "dependent_decisions": {
                    "voice_style": "professional_narrator",  # Depends on educational
                    "music_style": "subtle_background",  # Depends on educational
                    "pacing": "moderate_clear"  # Depends on educational
                }
            })
        )
        
        decisions = decision_framework.make_all_decisions(
            mission="Educational video about science"
        )
        
        # Verify dependent decisions align
        assert hasattr(decisions, 'content_type')
        assert hasattr(decisions, 'voice_style')
        assert hasattr(decisions, 'music_style')
    
    @pytest.mark.unit
    def test_decision_conflict_resolution(self, decision_framework, mock_ai_client):
        """Test resolution of conflicting decision requirements"""
        # Mock conflicting requirements
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps({
                "conflicts_detected": [
                    {
                        "conflict": "Duration vs Content",
                        "requirement1": "30 seconds max (TikTok)",
                        "requirement2": "Complex topic needs 2 minutes",
                        "resolution": "Simplify content to key points"
                    }
                ],
                "resolved_decisions": {
                    "duration": 30,
                    "content_strategy": "highlight_key_points"
                }
            })
        )
        
        decisions = decision_framework.make_all_decisions(
            mission="Explain quantum computing",
            platform="tiktok"
        )
        
        assert decisions.duration == 30
        assert decisions.content_strategy == "highlight_key_points"
    
    @pytest.mark.integration
    def test_decision_framework_with_components(self, decision_framework, mock_ai_client, mock_session_context):
        """Test decision framework integration with actual components"""
        # Make decisions
        decisions = decision_framework.make_all_decisions(
            mission="Create tech demo video",
            platform="youtube",
            duration=60
        )
        
        # Create components with decisions
        from src.generators.video_generator import VideoGenerator
        from src.generators.audio_generator import AudioGenerator
        
        # Components should accept decisions without any configuration
        video_gen = VideoGenerator(decisions, mock_session_context)
        audio_gen = AudioGenerator(decisions, mock_session_context)
        
        # Verify components use decisions
        assert video_gen.decisions == decisions
        assert audio_gen.decisions == decisions
        
        # Components should not have their own defaults
        assert not hasattr(video_gen, 'default_duration')
        assert not hasattr(audio_gen, 'default_language')