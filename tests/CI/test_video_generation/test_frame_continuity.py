"""
Tests for Frame Continuity
Ensures seamless transitions between video clips
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path
import json

from src.agents.continuity_decision_agent import ContinuityDecisionAgent
from src.core.entities import CoreDecisions, GeneratedVideoConfig


class TestFrameContinuity:
    """Test suite for frame continuity between clips"""
    
    @pytest.fixture
    def continuity_agent(self, mock_ai_client):
        """Create ContinuityDecisionAgent instance"""
        return ContinuityDecisionAgent(mock_ai_client)
    
    @pytest.fixture
    def sample_segments(self):
        """Sample video segments for testing continuity"""
        return [
            {
                "segment_number": 1,
                "visual_description": "Wide shot of a modern city skyline at dawn",
                "narrator_text": "Our story begins in the heart of the city",
                "duration": 5.0
            },
            {
                "segment_number": 2,
                "visual_description": "Close-up of a person walking through busy streets",
                "narrator_text": "Where thousands of people start their day",
                "duration": 5.0
            },
            {
                "segment_number": 3,
                "visual_description": "Interior of a coffee shop with morning customers",
                "narrator_text": "Each with their own story to tell",
                "duration": 5.0
            }
        ]
    
    @pytest.mark.unit
    def test_continuity_analysis(self, continuity_agent, sample_segments, mock_ai_client):
        """Test continuity analysis between segments"""
        # Mock AI response
        continuity_response = {
            "continuity_decisions": [
                {
                    "segment_pair": "1-2",
                    "transition_type": "cut",
                    "visual_continuity": "maintain_location",
                    "color_continuity": "consistent_palette",
                    "motion_continuity": "smooth_flow"
                },
                {
                    "segment_pair": "2-3",
                    "transition_type": "fade",
                    "visual_continuity": "scene_change",
                    "color_continuity": "gradual_shift",
                    "motion_continuity": "reset"
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(continuity_response)
        )
        
        # Test
        decisions = continuity_agent.analyze_continuity(sample_segments)
        
        # Assert
        assert len(decisions["continuity_decisions"]) == 2
        assert decisions["continuity_decisions"][0]["transition_type"] == "cut"
        assert decisions["continuity_decisions"][1]["transition_type"] == "fade"
    
    @pytest.mark.unit
    def test_continuity_flags_generation(self, continuity_agent, mock_ai_client):
        """Test generation of continuity flags for video generation"""
        segments = [
            {"segment_number": 1, "visual_description": "Person entering building"},
            {"segment_number": 2, "visual_description": "Same person in elevator"}
        ]
        
        # Mock response with continuity requirements
        mock_response = {
            "continuity_flags": {
                "character_consistency": True,
                "location_consistency": True,
                "time_progression": "continuous",
                "lighting_consistency": "indoor_fluorescent",
                "camera_angle_suggestion": "maintain_eye_level"
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(mock_response)
        )
        
        flags = continuity_agent.generate_continuity_flags(segments[0], segments[1])
        
        assert flags["character_consistency"] is True
        assert flags["location_consistency"] is True
        assert flags["time_progression"] == "continuous"
    
    @pytest.mark.unit
    def test_scene_transition_recommendations(self, continuity_agent, mock_ai_client):
        """Test scene transition recommendations"""
        scene_pairs = [
            ("Day exterior", "Night exterior"),
            ("Indoor office", "Indoor office"),
            ("Action scene", "Calm scene")
        ]
        
        for scene1, scene2 in scene_pairs:
            mock_response = {
                "transition": {
                    "type": "dissolve" if "Day" in scene1 else "cut",
                    "duration": 1.0 if "Day" in scene1 else 0.1,
                    "effect": "fade_to_black" if "Day" in scene1 else "none"
                }
            }
            
            mock_ai_client.generate_content.return_value = Mock(
                text=json.dumps(mock_response)
            )
            
            transition = continuity_agent.recommend_transition(scene1, scene2)
            
            assert "type" in transition
            assert "duration" in transition
    
    @pytest.mark.unit
    def test_visual_consistency_scoring(self, continuity_agent):
        """Test visual consistency scoring between frames"""
        # Test similar scenes
        similar_score = continuity_agent.calculate_visual_similarity(
            "Modern office with white walls and glass windows",
            "Modern office meeting room with glass walls"
        )
        
        # Test different scenes
        different_score = continuity_agent.calculate_visual_similarity(
            "Sunny beach with palm trees",
            "Snowy mountain peak at night"
        )
        
        assert similar_score > different_score
        assert 0 <= similar_score <= 1
        assert 0 <= different_score <= 1
    
    @pytest.mark.unit
    def test_continuity_with_characters(self, continuity_agent, mock_ai_client):
        """Test continuity when specific characters are involved"""
        segments_with_character = [
            {
                "segment_number": 1,
                "visual_description": "Sarah Chen giving presentation in boardroom",
                "character": "sarah_chen"
            },
            {
                "segment_number": 2,
                "visual_description": "Sarah Chen walking through office corridor",
                "character": "sarah_chen"
            }
        ]
        
        mock_response = {
            "character_continuity": {
                "appearance_consistent": True,
                "clothing_notes": "Maintain business suit",
                "expression_progression": "confident to thoughtful",
                "position_continuity": "screen_right to center"
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(mock_response)
        )
        
        continuity = continuity_agent.ensure_character_continuity(segments_with_character)
        
        assert continuity["character_continuity"]["appearance_consistent"] is True
        assert "clothing_notes" in continuity["character_continuity"]
    
    @pytest.mark.unit
    def test_motion_vector_analysis(self, continuity_agent):
        """Test motion vector analysis for smooth transitions"""
        motion_pairs = [
            {
                "prev": "Camera panning left across cityscape",
                "next": "Continuing pan left to reveal monument",
                "expected": "continuous"
            },
            {
                "prev": "Static shot of doorway",
                "next": "Person walking through doorway",
                "expected": "entry"
            },
            {
                "prev": "Car driving right to left",
                "next": "Same car driving left to right",
                "expected": "reverse"
            }
        ]
        
        for pair in motion_pairs:
            motion_type = continuity_agent.analyze_motion_continuity(
                pair["prev"], 
                pair["next"]
            )
            
            assert motion_type == pair["expected"]
    
    @pytest.mark.unit
    def test_color_palette_continuity(self, continuity_agent, mock_ai_client):
        """Test color palette continuity between scenes"""
        scenes = [
            {"description": "Warm sunset with orange and red hues"},
            {"description": "Golden hour cityscape"},
            {"description": "Blue night scene with neon lights"}
        ]
        
        # Test warm to warm transition
        mock_ai_client.generate_content.return_value = Mock(
            text='{"palette_match": "compatible", "transition": "smooth"}'
        )
        
        result = continuity_agent.check_color_continuity(scenes[0], scenes[1])
        assert result["palette_match"] == "compatible"
        
        # Test warm to cool transition
        mock_ai_client.generate_content.return_value = Mock(
            text='{"palette_match": "contrasting", "transition": "requires_fade"}'
        )
        
        result = continuity_agent.check_color_continuity(scenes[0], scenes[2])
        assert result["palette_match"] == "contrasting"
    
    @pytest.mark.unit
    def test_temporal_continuity(self, continuity_agent):
        """Test temporal continuity in video sequences"""
        time_sequences = [
            {
                "segments": [
                    {"time": "morning", "description": "Sunrise over city"},
                    {"time": "noon", "description": "Busy lunch hour"},
                    {"time": "evening", "description": "Sunset and city lights"}
                ],
                "expected": "natural_progression"
            },
            {
                "segments": [
                    {"time": "night", "description": "Dark street"},
                    {"time": "day", "description": "Bright sunshine"},
                    {"time": "night", "description": "Dark again"}
                ],
                "expected": "flashback_or_error"
            }
        ]
        
        for sequence in time_sequences:
            result = continuity_agent.analyze_temporal_flow(sequence["segments"])
            assert result == sequence["expected"]
    
    @pytest.mark.unit
    def test_continuity_metadata_generation(self, continuity_agent, sample_segments):
        """Test generation of continuity metadata for video assembly"""
        metadata = continuity_agent.generate_continuity_metadata(sample_segments)
        
        assert "total_segments" in metadata
        assert "continuity_score" in metadata
        assert "transition_points" in metadata
        assert len(metadata["transition_points"]) == len(sample_segments) - 1
        
        # Each transition should have required fields
        for transition in metadata["transition_points"]:
            assert "from_segment" in transition
            assert "to_segment" in transition
            assert "transition_type" in transition
            assert "duration" in transition
    
    @pytest.mark.integration
    def test_continuity_with_video_generator(self, mock_ai_client, mock_session_context):
        """Test continuity integration with video generator"""
        from src.generators.video_generator import VideoGenerator
        
        # Create decisions with continuity enabled
        config = GeneratedVideoConfig(
            topic="Continuous story",
            duration=15,
            platform="youtube",
            language="en"
        )
        
        decisions = CoreDecisions(
            video_config=config,
            mission="Tell continuous story",
            target_platform="youtube",
            language="en",
            duration=15
        )
        decisions.enable_continuity = True
        decisions.visual_style = "cinematic"
        
        # Mock continuity agent in video generator
        with patch('src.generators.video_generator.ContinuityDecisionAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.analyze_continuity.return_value = {
                "continuity_decisions": [
                    {"transition_type": "cut", "duration": 0.1}
                ]
            }
            mock_agent_class.return_value = mock_agent
            
            # Create video generator
            generator = VideoGenerator(decisions, mock_session_context)
            
            # Verify continuity agent is initialized when enabled
            assert hasattr(generator, 'continuity_agent')
            mock_agent_class.assert_called_once()