"""
Tests for DirectorAgent
Ensures the DirectorAgent properly directs video creation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.agents.director_agent import DirectorAgent


class TestDirectorAgent:
    """Test suite for DirectorAgent"""
    
    @pytest.fixture
    def director_agent(self, mock_ai_client):
        """Create DirectorAgent instance"""
        return DirectorAgent(mock_ai_client)
    
    @pytest.mark.unit
    def test_director_initialization(self, mock_ai_client):
        """Test DirectorAgent initializes correctly"""
        agent = DirectorAgent(mock_ai_client)
        assert agent is not None
        assert agent.ai_client == mock_ai_client
        assert agent.name == "DirectorAgent"
    
    @pytest.mark.unit
    def test_analyze_mission(self, director_agent, mock_ai_client):
        """Test mission analysis and interpretation"""
        mission = "Create an engaging video about climate change impacts on oceans"
        
        # Mock AI response
        analysis_response = {
            "mission_analysis": {
                "primary_topic": "climate change impacts on oceans",
                "target_audience": "general public",
                "tone": "educational yet engaging",
                "key_messages": [
                    "Ocean warming effects",
                    "Sea level rise",
                    "Marine ecosystem impacts"
                ],
                "narrative_approach": "documentary style with emotional appeal"
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(analysis_response)
        )
        
        # Test
        analysis = director_agent.analyze_mission(mission)
        
        # Assert
        assert analysis["mission_analysis"]["primary_topic"] == "climate change impacts on oceans"
        assert "target_audience" in analysis["mission_analysis"]
        assert len(analysis["mission_analysis"]["key_messages"]) == 3
    
    @pytest.mark.unit
    def test_create_creative_direction(self, director_agent, mock_ai_client):
        """Test creative direction generation"""
        mission_analysis = {
            "primary_topic": "artificial intelligence",
            "tone": "futuristic and optimistic"
        }
        
        # Mock response
        direction_response = {
            "creative_direction": {
                "visual_style": "modern, clean, tech-focused",
                "color_palette": ["blue", "white", "silver"],
                "pacing": "dynamic with moments of reflection",
                "music_style": "electronic ambient",
                "narrative_structure": "problem-solution-future",
                "key_visual_elements": [
                    "Neural networks visualization",
                    "Real-world AI applications",
                    "Human-AI interaction"
                ]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(direction_response)
        )
        
        # Test
        direction = director_agent.create_creative_direction(mission_analysis)
        
        # Assert
        assert direction["creative_direction"]["visual_style"] == "modern, clean, tech-focused"
        assert "blue" in direction["creative_direction"]["color_palette"]
        assert len(direction["creative_direction"]["key_visual_elements"]) == 3
    
    @pytest.mark.unit
    def test_segment_planning(self, director_agent, mock_ai_client):
        """Test video segment planning"""
        creative_direction = {
            "narrative_structure": "three-act",
            "pacing": "gradual build"
        }
        duration = 60  # seconds
        
        # Mock response
        segment_response = {
            "segments": [
                {
                    "segment_number": 1,
                    "purpose": "introduction",
                    "duration": 15,
                    "content_focus": "Set the stage",
                    "visual_tone": "mysterious"
                },
                {
                    "segment_number": 2,
                    "purpose": "main content",
                    "duration": 30,
                    "content_focus": "Core information",
                    "visual_tone": "informative"
                },
                {
                    "segment_number": 3,
                    "purpose": "conclusion",
                    "duration": 15,
                    "content_focus": "Call to action",
                    "visual_tone": "inspiring"
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(segment_response)
        )
        
        # Test
        segments = director_agent.plan_segments(creative_direction, duration)
        
        # Assert
        assert len(segments["segments"]) == 3
        total_duration = sum(s["duration"] for s in segments["segments"])
        assert total_duration == duration
        assert segments["segments"][1]["purpose"] == "main content"
    
    @pytest.mark.unit
    def test_style_consistency_guidelines(self, director_agent, mock_ai_client):
        """Test generation of style consistency guidelines"""
        creative_direction = {
            "visual_style": "cinematic documentary",
            "color_palette": ["earth tones", "natural greens"]
        }
        
        # Mock response
        guidelines_response = {
            "style_guidelines": {
                "camera_work": "steady, slow movements",
                "transitions": "dissolves and fades",
                "text_style": "minimal, sans-serif",
                "visual_consistency_rules": [
                    "Maintain earth tone palette throughout",
                    "Use natural lighting aesthetics",
                    "Keep text overlays in lower third"
                ]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(guidelines_response)
        )
        
        # Test
        guidelines = director_agent.create_style_guidelines(creative_direction)
        
        # Assert
        assert guidelines["style_guidelines"]["camera_work"] == "steady, slow movements"
        assert len(guidelines["style_guidelines"]["visual_consistency_rules"]) == 3
    
    @pytest.mark.unit
    def test_emotional_arc_planning(self, director_agent, mock_ai_client):
        """Test emotional arc planning for video"""
        mission = "Inspire people to take action on environmental issues"
        
        # Mock response
        arc_response = {
            "emotional_arc": [
                {"time": "0-20%", "emotion": "concern", "intensity": 3},
                {"time": "20-40%", "emotion": "understanding", "intensity": 5},
                {"time": "40-60%", "emotion": "urgency", "intensity": 7},
                {"time": "60-80%", "emotion": "hope", "intensity": 8},
                {"time": "80-100%", "emotion": "empowerment", "intensity": 9}
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(arc_response)
        )
        
        # Test
        arc = director_agent.plan_emotional_arc(mission)
        
        # Assert
        assert len(arc["emotional_arc"]) == 5
        assert arc["emotional_arc"][0]["emotion"] == "concern"
        assert arc["emotional_arc"][-1]["emotion"] == "empowerment"
        # Verify intensity increases
        assert arc["emotional_arc"][-1]["intensity"] > arc["emotional_arc"][0]["intensity"]
    
    @pytest.mark.unit
    def test_platform_specific_direction(self, director_agent, mock_ai_client):
        """Test platform-specific creative direction"""
        platforms = ["youtube", "instagram", "tiktok"]
        
        for platform in platforms:
            # Mock platform-specific response
            platform_response = {
                "platform_direction": {
                    "youtube": {
                        "opening": "Strong hook in first 5 seconds",
                        "structure": "Long-form storytelling",
                        "cta": "Subscribe and notification bell"
                    },
                    "instagram": {
                        "opening": "Visual impact immediately",
                        "structure": "Quick, punchy segments",
                        "cta": "Swipe up or link in bio"
                    },
                    "tiktok": {
                        "opening": "Trend-based hook",
                        "structure": "Fast-paced, loop-friendly",
                        "cta": "Follow for more"
                    }
                }
            }
            
            mock_ai_client.generate_content.return_value = Mock(
                text=json.dumps(platform_response["platform_direction"][platform])
            )
            
            # Test
            direction = director_agent.get_platform_direction(platform)
            
            # Assert
            assert "opening" in direction
            assert "structure" in direction
            assert "cta" in direction
    
    @pytest.mark.unit
    def test_collaboration_with_other_agents(self, director_agent, mock_ai_client):
        """Test DirectorAgent's guidance for other agents"""
        # Mock guidance generation
        guidance_response = {
            "agent_guidance": {
                "ScriptWriterAgent": {
                    "tone": "conversational yet informative",
                    "vocabulary_level": "accessible",
                    "key_points_emphasis": ["innovation", "accessibility", "future"]
                },
                "VisualStyleAgent": {
                    "aesthetic": "modern minimalist",
                    "color_emphasis": "cool tones",
                    "visual_metaphors": ["network connections", "data flow"]
                },
                "VoiceDirectorAgent": {
                    "voice_character": "warm, trustworthy",
                    "pacing": "measured, clear",
                    "emphasis_patterns": "key statistics and calls to action"
                }
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(guidance_response)
        )
        
        # Test
        guidance = director_agent.generate_agent_guidance()
        
        # Assert
        assert "ScriptWriterAgent" in guidance["agent_guidance"]
        assert "VisualStyleAgent" in guidance["agent_guidance"]
        assert "VoiceDirectorAgent" in guidance["agent_guidance"]
        assert guidance["agent_guidance"]["ScriptWriterAgent"]["tone"] == "conversational yet informative"
    
    @pytest.mark.unit
    def test_quality_criteria_definition(self, director_agent, mock_ai_client):
        """Test quality criteria definition for video"""
        # Mock response
        criteria_response = {
            "quality_criteria": {
                "visual_quality": {
                    "resolution": "1080p minimum",
                    "consistency": "No jarring style changes",
                    "clarity": "Clear focus on key elements"
                },
                "narrative_quality": {
                    "coherence": "Logical flow throughout",
                    "engagement": "Hook within 3 seconds",
                    "clarity": "Message easily understood"
                },
                "technical_quality": {
                    "audio_levels": "Consistent, no clipping",
                    "transitions": "Smooth, purposeful",
                    "timing": "Perfect sync with narration"
                }
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(criteria_response)
        )
        
        # Test
        criteria = director_agent.define_quality_criteria()
        
        # Assert
        assert "visual_quality" in criteria["quality_criteria"]
        assert "narrative_quality" in criteria["quality_criteria"]
        assert "technical_quality" in criteria["quality_criteria"]
    
    @pytest.mark.integration
    def test_director_full_workflow(self, director_agent, mock_ai_client):
        """Test complete director workflow"""
        mission = "Create an inspiring video about space exploration"
        
        # Setup mock responses for full workflow
        responses = [
            {"mission_analysis": {"primary_topic": "space exploration"}},
            {"creative_direction": {"visual_style": "epic cinematic"}},
            {"segments": [{"segment_number": 1, "duration": 30}]},
            {"style_guidelines": {"transitions": "smooth fades"}},
            {"emotional_arc": [{"emotion": "wonder", "intensity": 8}]}
        ]
        
        mock_ai_client.generate_content.side_effect = [
            Mock(text=json.dumps(resp)) for resp in responses
        ]
        
        # Execute full workflow
        analysis = director_agent.analyze_mission(mission)
        direction = director_agent.create_creative_direction(analysis["mission_analysis"])
        segments = director_agent.plan_segments(direction["creative_direction"], 60)
        guidelines = director_agent.create_style_guidelines(direction["creative_direction"])
        arc = director_agent.plan_emotional_arc(mission)
        
        # Verify complete direction package
        assert analysis is not None
        assert direction is not None
        assert segments is not None
        assert guidelines is not None
        assert arc is not None
        
        # Verify AI was called correct number of times
        assert mock_ai_client.generate_content.call_count == 5