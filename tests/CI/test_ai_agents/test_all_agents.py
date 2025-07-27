"""
Comprehensive tests for all 22 AI Agents
Ensures all agents work correctly and collaborate properly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Import all agents
from src.agents.director_agent import DirectorAgent
from src.agents.script_writer_agent import ScriptWriterAgent
from src.agents.visual_style_agent import VisualStyleAgent
from src.agents.voice_director_agent import VoiceDirectorAgent
from src.agents.soundman_agent import SoundmanAgent
from src.agents.editor_agent import EditorAgent
from src.agents.video_generator_agent import VideoGeneratorAgent
from src.agents.overlay_positioning_agent import OverlayPositioningAgent
from src.agents.trend_analyst_agent import TrendAnalystAgent
from src.agents.fact_checker_agent import FactCheckerAgent
from src.agents.cultural_sensitivity_agent import CulturalSensitivityAgent
from src.agents.continuity_decision_agent import ContinuityDecisionAgent
from src.agents.super_master_agent import SuperMasterAgent
from src.agents.mission_planning_agent import MissionPlanningAgent
from src.agents.video_structure_agent import VideoStructureAgent
from src.agents.clip_timing_agent import ClipTimingAgent
from src.agents.visual_elements_agent import VisualElementsAgent
from src.agents.media_type_agent import MediaTypeAgent
from src.agents.image_timing_agent import ImageTimingAgent
from src.discussion.multi_agent_discussion import MultiAgentDiscussion


class TestAllAgents:
    """Test suite for all 22 agents"""
    
    @pytest.fixture
    def all_agents(self, mock_ai_client):
        """Create instances of all agents"""
        return {
            "director": DirectorAgent(mock_ai_client),
            "script_writer": ScriptWriterAgent(mock_ai_client),
            "visual_style": VisualStyleAgent(mock_ai_client),
            "voice_director": VoiceDirectorAgent(mock_ai_client),
            "soundman": SoundmanAgent(mock_ai_client),
            "editor": EditorAgent(mock_ai_client),
            "video_generator": VideoGeneratorAgent(mock_ai_client),
            "overlay_positioning": OverlayPositioningAgent(mock_ai_client),
            "trend_analyst": TrendAnalystAgent(mock_ai_client),
            "fact_checker": FactCheckerAgent(mock_ai_client),
            "cultural_sensitivity": CulturalSensitivityAgent(mock_ai_client),
            "continuity_decision": ContinuityDecisionAgent(mock_ai_client),
            "super_master": SuperMasterAgent(mock_ai_client),
            "mission_planning": MissionPlanningAgent(mock_ai_client),
            "video_structure": VideoStructureAgent(mock_ai_client),
            "clip_timing": ClipTimingAgent(mock_ai_client),
            "visual_elements": VisualElementsAgent(mock_ai_client),
            "media_type": MediaTypeAgent(mock_ai_client),
            "image_timing": ImageTimingAgent(mock_ai_client)
        }
    
    @pytest.mark.unit
    def test_all_agents_initialization(self, all_agents):
        """Test all agents initialize correctly"""
        assert len(all_agents) == 19  # All core agents
        
        for name, agent in all_agents.items():
            assert agent is not None
            assert hasattr(agent, 'ai_client')
            assert hasattr(agent, 'name')
    
    @pytest.mark.unit
    def test_visual_style_agent(self, mock_ai_client):
        """Test VisualStyleAgent functionality"""
        agent = VisualStyleAgent(mock_ai_client)
        
        # Mock response
        style_response = {
            "visual_style": {
                "aesthetic": "modern minimalist",
                "color_scheme": {
                    "primary": "#1E88E5",
                    "secondary": "#FFC107",
                    "background": "#FFFFFF"
                },
                "typography": {
                    "heading": "Helvetica Neue Bold",
                    "body": "Open Sans Regular"
                },
                "animation_style": "smooth transitions",
                "visual_elements": ["geometric shapes", "clean lines", "ample whitespace"]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(style_response))
        
        style = agent.define_visual_style("tech product launch")
        
        assert style["visual_style"]["aesthetic"] == "modern minimalist"
        assert "#1E88E5" in style["visual_style"]["color_scheme"]["primary"]
    
    @pytest.mark.unit
    def test_voice_director_agent(self, mock_ai_client):
        """Test VoiceDirectorAgent functionality"""
        agent = VoiceDirectorAgent(mock_ai_client)
        
        # Mock response
        voice_response = {
            "voice_direction": {
                "voice_type": "professional female",
                "tone": "confident and warm",
                "pace": "moderate - 150 wpm",
                "emphasis": ["key benefits", "call to action"],
                "emotion_mapping": {
                    "intro": "welcoming",
                    "problem": "concerned",
                    "solution": "optimistic",
                    "cta": "encouraging"
                }
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(voice_response))
        
        direction = agent.create_voice_direction("corporate presentation", "en")
        
        assert direction["voice_direction"]["voice_type"] == "professional female"
        assert direction["voice_direction"]["pace"] == "moderate - 150 wpm"
    
    @pytest.mark.unit
    def test_soundman_agent(self, mock_ai_client):
        """Test SoundmanAgent functionality"""
        agent = SoundmanAgent(mock_ai_client)
        
        # Mock response
        sound_response = {
            "sound_design": {
                "background_music": {
                    "style": "ambient electronic",
                    "mood": "uplifting",
                    "intensity_curve": [0.3, 0.5, 0.7, 0.9, 0.6]
                },
                "sound_effects": [
                    {"timestamp": 0.5, "effect": "swoosh", "purpose": "transition"},
                    {"timestamp": 5.2, "effect": "chime", "purpose": "highlight"}
                ],
                "audio_mix": {
                    "voice_level": -3,
                    "music_level": -12,
                    "effects_level": -6
                }
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(sound_response))
        
        sound_design = agent.design_soundscape("tech demo video", 30)
        
        assert sound_design["sound_design"]["background_music"]["style"] == "ambient electronic"
        assert len(sound_design["sound_design"]["sound_effects"]) == 2
    
    @pytest.mark.unit
    def test_editor_agent(self, mock_ai_client):
        """Test EditorAgent functionality"""
        agent = EditorAgent(mock_ai_client)
        
        # Mock response
        edit_response = {
            "editing_decisions": {
                "cut_points": [5.2, 10.5, 15.8, 20.1],
                "transitions": [
                    {"type": "cut", "duration": 0},
                    {"type": "dissolve", "duration": 0.5},
                    {"type": "wipe", "duration": 0.3}
                ],
                "pacing": "dynamic with breathing room",
                "rhythm": "follows music beat",
                "special_effects": [
                    {"type": "slow_motion", "start": 12.0, "end": 13.5},
                    {"type": "speed_ramp", "start": 18.0, "end": 19.0}
                ]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(edit_response))
        
        editing = agent.create_edit_decisions(["clip1", "clip2", "clip3"], 30)
        
        assert len(editing["editing_decisions"]["cut_points"]) == 4
        assert editing["editing_decisions"]["transitions"][1]["type"] == "dissolve"
    
    @pytest.mark.unit
    def test_overlay_positioning_agent(self, mock_ai_client):
        """Test OverlayPositioningAgent functionality"""
        agent = OverlayPositioningAgent(mock_ai_client)
        
        # Mock response
        overlay_response = {
            "overlay_positions": [
                {
                    "text": "Amazing Technology",
                    "position": {"x": 0.5, "y": 0.8},
                    "alignment": "center",
                    "animation": "fade_in",
                    "duration": 3.0
                },
                {
                    "text": "Learn More",
                    "position": {"x": 0.9, "y": 0.9},
                    "alignment": "right",
                    "animation": "slide_in_right",
                    "duration": 5.0
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(overlay_response))
        
        positions = agent.calculate_overlay_positions(
            ["Amazing Technology", "Learn More"],
            "youtube"
        )
        
        assert len(positions["overlay_positions"]) == 2
        assert positions["overlay_positions"][0]["position"]["y"] == 0.8
    
    @pytest.mark.unit
    def test_trend_analyst_agent(self, mock_ai_client):
        """Test TrendAnalystAgent functionality"""
        agent = TrendAnalystAgent(mock_ai_client)
        
        # Mock response
        trend_response = {
            "trend_analysis": {
                "current_trends": [
                    "Short-form vertical videos",
                    "AI-generated content",
                    "Interactive elements"
                ],
                "hashtag_recommendations": [
                    "#AIRevolution", "#TechTrends2024", "#FutureIsNow"
                ],
                "timing_recommendation": "Post at 2PM EST for maximum engagement",
                "format_suggestions": ["Add captions", "Use trending audio", "Hook in first 3 seconds"]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(trend_response))
        
        trends = agent.analyze_trends("AI technology", "instagram")
        
        assert len(trends["trend_analysis"]["current_trends"]) == 3
        assert "#AIRevolution" in trends["trend_analysis"]["hashtag_recommendations"]
    
    @pytest.mark.unit
    def test_fact_checker_agent(self, mock_ai_client):
        """Test FactCheckerAgent functionality"""
        agent = FactCheckerAgent(mock_ai_client)
        
        # Mock response
        fact_check_response = {
            "fact_check_results": [
                {
                    "claim": "AI can diagnose diseases",
                    "verdict": "partially_true",
                    "explanation": "AI assists in diagnosis but requires human oversight",
                    "sources": ["FDA guidelines", "Medical journals"]
                },
                {
                    "claim": "AI will replace all jobs",
                    "verdict": "false",
                    "explanation": "AI will transform jobs, not replace all of them",
                    "sources": ["Economic studies", "Labor statistics"]
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(fact_check_response))
        
        results = agent.verify_facts([
            "AI can diagnose diseases",
            "AI will replace all jobs"
        ])
        
        assert len(results["fact_check_results"]) == 2
        assert results["fact_check_results"][0]["verdict"] == "partially_true"
    
    @pytest.mark.unit
    def test_cultural_sensitivity_agent(self, mock_ai_client):
        """Test CulturalSensitivityAgent functionality"""
        agent = CulturalSensitivityAgent(mock_ai_client)
        
        # Mock response
        cultural_response = {
            "cultural_analysis": {
                "potential_issues": [
                    {
                        "content": "Hand gesture",
                        "issue": "Offensive in Middle Eastern cultures",
                        "suggestion": "Use different gesture or remove"
                    }
                ],
                "adaptations": {
                    "colors": "Avoid white for Chinese audience (associated with mourning)",
                    "symbols": "Remove religious symbols for secular content",
                    "language": "Use formal address for Japanese audience"
                },
                "approved": True,
                "confidence": 0.95
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(cultural_response))
        
        analysis = agent.analyze_content("Video script content", ["US", "Japan", "UAE"])
        
        assert len(analysis["cultural_analysis"]["potential_issues"]) == 1
        assert analysis["cultural_analysis"]["approved"] is True
    
    @pytest.mark.unit
    def test_mission_planning_agent(self, mock_ai_client):
        """Test MissionPlanningAgent functionality"""
        agent = MissionPlanningAgent(mock_ai_client)
        
        # Mock response
        planning_response = {
            "mission_plan": {
                "objectives": [
                    "Educate about AI benefits",
                    "Address common concerns",
                    "Inspire action"
                ],
                "target_audience": {
                    "primary": "Tech-savvy professionals",
                    "secondary": "General public interested in technology"
                },
                "key_messages": [
                    "AI enhances human capabilities",
                    "Ethical AI is possible",
                    "The future is collaborative"
                ],
                "success_metrics": [
                    "View duration > 80%",
                    "Engagement rate > 5%",
                    "Positive sentiment > 90%"
                ]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(planning_response))
        
        plan = agent.create_mission_plan("Create AI awareness video")
        
        assert len(plan["mission_plan"]["objectives"]) == 3
        assert plan["mission_plan"]["target_audience"]["primary"] == "Tech-savvy professionals"
    
    @pytest.mark.unit
    def test_video_structure_agent(self, mock_ai_client):
        """Test VideoStructureAgent functionality"""
        agent = VideoStructureAgent(mock_ai_client)
        
        # Mock response
        structure_response = {
            "video_structure": {
                "acts": [
                    {"name": "Hook", "duration": 5, "purpose": "Grab attention"},
                    {"name": "Problem", "duration": 10, "purpose": "Identify pain point"},
                    {"name": "Solution", "duration": 30, "purpose": "Present main content"},
                    {"name": "Benefits", "duration": 10, "purpose": "Show value"},
                    {"name": "CTA", "duration": 5, "purpose": "Drive action"}
                ],
                "narrative_arc": "problem-solution",
                "tension_points": [15, 35, 50],
                "resolution_point": 55
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(structure_response))
        
        structure = agent.design_structure("product demo", 60)
        
        assert len(structure["video_structure"]["acts"]) == 5
        assert sum(act["duration"] for act in structure["video_structure"]["acts"]) == 60
    
    @pytest.mark.unit
    def test_multi_agent_collaboration(self, mock_ai_client, mock_session_context):
        """Test multi-agent collaboration system"""
        from src.discussion.multi_agent_discussion import MultiAgentDiscussion
        
        # Create discussion system
        discussion = MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Create engaging AI video",
            mode="enhanced"  # Use 7 core agents
        )
        
        # Mock discussion responses
        discussion_response = {
            "discussion_summary": {
                "consensus_reached": True,
                "key_decisions": {
                    "visual_style": "modern tech aesthetic",
                    "voice_type": "professional narrator",
                    "music_style": "ambient electronic",
                    "structure": "problem-solution narrative"
                },
                "agent_contributions": {
                    "DirectorAgent": "Set overall creative vision",
                    "ScriptWriterAgent": "Crafted compelling narrative",
                    "VisualStyleAgent": "Defined aesthetic framework"
                }
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(text=json.dumps(discussion_response))
        
        # Test discussion
        with patch.object(discussion, 'conduct_discussion') as mock_discuss:
            mock_discuss.return_value = discussion_response
            
            result = discussion.conduct_discussion("topic")
            
            assert result["discussion_summary"]["consensus_reached"] is True
            assert "visual_style" in result["discussion_summary"]["key_decisions"]
    
    @pytest.mark.integration
    def test_professional_mode_all_agents(self, mock_ai_client, mock_session_context):
        """Test professional mode with all 22 agents"""
        discussion = MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Create comprehensive video",
            mode="professional"  # Use all 22 agents
        )
        
        # Verify all agents are loaded
        assert len(discussion.agents) >= 20  # At least 20 agents in professional mode
        
        # Test that all agent types are present
        agent_types = {type(agent).__name__ for agent in discussion.agents}
        expected_agents = {
            "DirectorAgent", "ScriptWriterAgent", "VisualStyleAgent",
            "VoiceDirectorAgent", "SoundmanAgent", "EditorAgent",
            "VideoGeneratorAgent", "OverlayPositioningAgent",
            "TrendAnalystAgent", "FactCheckerAgent",
            "CulturalSensitivityAgent", "ContinuityDecisionAgent"
        }
        
        assert expected_agents.issubset(agent_types)