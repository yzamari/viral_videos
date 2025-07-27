"""
Tests for Multi-Agent Discussion System
Ensures agent collaboration framework works correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
import os
from pathlib import Path

from src.discussion.multi_agent_discussion import MultiAgentDiscussion
from src.agents.director_agent import DirectorAgent
from src.agents.script_writer_agent import ScriptWriterAgent


class TestMultiAgentDiscussion:
    """Test suite for multi-agent discussion system"""
    
    @pytest.fixture
    def discussion_system(self, mock_ai_client, mock_session_context):
        """Create MultiAgentDiscussion instance"""
        return MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Create test video",
            mode="enhanced"
        )
    
    @pytest.mark.unit
    def test_discussion_initialization(self, mock_ai_client, mock_session_context):
        """Test discussion system initialization"""
        # Test different modes
        modes = ["simple", "enhanced", "professional"]
        
        for mode in modes:
            discussion = MultiAgentDiscussion(
                ai_client=mock_ai_client,
                session_context=mock_session_context,
                mission="Test mission",
                mode=mode
            )
            
            assert discussion is not None
            assert discussion.mode == mode
            assert discussion.mission == "Test mission"
            
            # Verify agent count based on mode
            if mode == "simple":
                assert len(discussion.agents) <= 3
            elif mode == "enhanced":
                assert 5 <= len(discussion.agents) <= 10
            else:  # professional
                assert len(discussion.agents) >= 15
    
    @pytest.mark.unit
    def test_topic_selection(self, discussion_system, mock_ai_client):
        """Test discussion topic selection"""
        # Mock topic generation
        topics_response = {
            "discussion_topics": [
                {
                    "topic": "Visual Style and Aesthetics",
                    "priority": 1,
                    "participants": ["DirectorAgent", "VisualStyleAgent"]
                },
                {
                    "topic": "Narrative Structure",
                    "priority": 2,
                    "participants": ["DirectorAgent", "ScriptWriterAgent", "EditorAgent"]
                },
                {
                    "topic": "Audio Design",
                    "priority": 3,
                    "participants": ["SoundmanAgent", "VoiceDirectorAgent"]
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(topics_response)
        )
        
        topics = discussion_system.select_discussion_topics()
        
        assert len(topics["discussion_topics"]) == 3
        assert topics["discussion_topics"][0]["priority"] == 1
        assert "DirectorAgent" in topics["discussion_topics"][0]["participants"]
    
    @pytest.mark.unit
    def test_agent_discussion_round(self, discussion_system, mock_ai_client):
        """Test a single discussion round between agents"""
        topic = "Visual Style Selection"
        participating_agents = [
            Mock(name="DirectorAgent"),
            Mock(name="VisualStyleAgent")
        ]
        
        # Mock agent responses
        agent_responses = [
            {
                "agent": "DirectorAgent",
                "opinion": "We need a modern, clean aesthetic",
                "reasoning": "Appeals to tech-savvy audience",
                "suggestions": ["Minimalist design", "Blue color scheme"]
            },
            {
                "agent": "VisualStyleAgent",
                "opinion": "Agree with modern aesthetic, suggest gradients",
                "reasoning": "Gradients add depth while maintaining cleanliness",
                "suggestions": ["Gradient backgrounds", "Subtle animations"]
            }
        ]
        
        mock_ai_client.generate_content.side_effect = [
            Mock(text=json.dumps(resp)) for resp in agent_responses
        ]
        
        # Test discussion round
        round_result = discussion_system.conduct_discussion_round(
            topic,
            participating_agents
        )
        
        assert len(round_result) == 2
        assert round_result[0]["agent"] == "DirectorAgent"
        assert "suggestions" in round_result[1]
    
    @pytest.mark.unit
    def test_consensus_building(self, discussion_system, mock_ai_client):
        """Test consensus building from agent opinions"""
        agent_opinions = [
            {
                "agent": "DirectorAgent",
                "opinion": "Modern minimalist style",
                "suggestions": ["Clean lines", "Limited color palette"]
            },
            {
                "agent": "VisualStyleAgent",
                "opinion": "Agree with minimalist, add subtle animations",
                "suggestions": ["Micro-interactions", "Smooth transitions"]
            },
            {
                "agent": "EditorAgent",
                "opinion": "Support minimalist with dynamic cuts",
                "suggestions": ["Quick cuts for energy", "Clean transitions"]
            }
        ]
        
        # Mock consensus response
        consensus_response = {
            "consensus": {
                "agreement_level": 0.85,
                "final_decision": "Modern minimalist with subtle animations and dynamic editing",
                "key_elements": [
                    "Clean design language",
                    "Limited color palette",
                    "Subtle micro-animations",
                    "Dynamic but clean cuts"
                ],
                "dissenting_opinions": []
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(consensus_response)
        )
        
        consensus = discussion_system.build_consensus(agent_opinions)
        
        assert consensus["consensus"]["agreement_level"] == 0.85
        assert len(consensus["consensus"]["key_elements"]) == 4
        assert consensus["consensus"]["dissenting_opinions"] == []
    
    @pytest.mark.unit
    def test_conflict_resolution(self, discussion_system, mock_ai_client):
        """Test conflict resolution between agents"""
        conflicting_opinions = [
            {
                "agent": "DirectorAgent",
                "opinion": "Fast-paced editing",
                "reasoning": "Maintain viewer attention"
            },
            {
                "agent": "EditorAgent",
                "opinion": "Slow, contemplative pacing",
                "reasoning": "Allow message absorption"
            }
        ]
        
        # Mock resolution
        resolution_response = {
            "resolution": {
                "compromise": "Variable pacing - fast for hooks, slow for key messages",
                "rationale": "Combines benefits of both approaches",
                "implementation": [
                    "Fast-paced intro (0-10s)",
                    "Moderate pace for main content (10-50s)",
                    "Slow for key takeaways (50-60s)"
                ],
                "agent_agreement": {
                    "DirectorAgent": True,
                    "EditorAgent": True
                }
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(resolution_response)
        )
        
        resolution = discussion_system.resolve_conflict(conflicting_opinions)
        
        assert "compromise" in resolution["resolution"]
        assert resolution["resolution"]["agent_agreement"]["DirectorAgent"] is True
        assert resolution["resolution"]["agent_agreement"]["EditorAgent"] is True
    
    @pytest.mark.unit
    def test_discussion_documentation(self, discussion_system, mock_session_context, temp_dir):
        """Test discussion documentation and saving"""
        discussion_results = {
            "topics_discussed": ["Visual Style", "Narrative Structure"],
            "decisions_made": {
                "visual_style": "Modern minimalist",
                "narrative": "Problem-solution"
            },
            "agent_contributions": {
                "DirectorAgent": 5,
                "ScriptWriterAgent": 4,
                "VisualStyleAgent": 6
            }
        }
        
        # Setup mock session path
        mock_session_context.get_session_path.return_value = Path(temp_dir)
        
        # Test documentation
        discussion_system.document_discussion(discussion_results)
        
        # Verify file was saved
        expected_path = Path(temp_dir) / "discussions" / "multi_agent_discussion.json"
        mock_session_context.save_artifact.assert_called_once()
        
        # Verify content structure
        call_args = mock_session_context.save_artifact.call_args
        assert "multi_agent_discussion.json" in call_args[0][0]
        saved_data = json.loads(call_args[0][1])
        assert "topics_discussed" in saved_data
        assert "decisions_made" in saved_data
    
    @pytest.mark.unit
    def test_mode_based_agent_selection(self, mock_ai_client, mock_session_context):
        """Test agent selection based on mode"""
        # Test simple mode
        simple_discussion = MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Simple task",
            mode="simple"
        )
        
        simple_agents = {type(agent).__name__ for agent in simple_discussion.agents}
        assert "DirectorAgent" in simple_agents
        assert len(simple_agents) <= 5
        
        # Test enhanced mode
        enhanced_discussion = MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Enhanced task",
            mode="enhanced"
        )
        
        enhanced_agents = {type(agent).__name__ for agent in enhanced_discussion.agents}
        assert "DirectorAgent" in enhanced_agents
        assert "ScriptWriterAgent" in enhanced_agents
        assert 5 <= len(enhanced_agents) <= 10
        
        # Test professional mode
        professional_discussion = MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Professional task",
            mode="professional"
        )
        
        professional_agents = {type(agent).__name__ for agent in professional_discussion.agents}
        assert len(professional_agents) >= 15
        assert "TrendAnalystAgent" in professional_agents
        assert "FactCheckerAgent" in professional_agents
    
    @pytest.mark.unit
    def test_discussion_iteration(self, discussion_system, mock_ai_client):
        """Test iterative discussion rounds"""
        # Mock multiple rounds of discussion
        round_responses = [
            {
                "round": 1,
                "status": "in_progress",
                "agreements": ["Visual style"],
                "pending": ["Music choice", "Pacing"]
            },
            {
                "round": 2,
                "status": "in_progress",
                "agreements": ["Visual style", "Music choice"],
                "pending": ["Pacing"]
            },
            {
                "round": 3,
                "status": "complete",
                "agreements": ["Visual style", "Music choice", "Pacing"],
                "pending": []
            }
        ]
        
        mock_ai_client.generate_content.side_effect = [
            Mock(text=json.dumps(resp)) for resp in round_responses
        ]
        
        # Test iteration
        max_rounds = 3
        for i in range(max_rounds):
            result = discussion_system.iterate_discussion()
            
            if result["status"] == "complete":
                assert len(result["pending"]) == 0
                assert len(result["agreements"]) == 3
                break
        
        assert i == 2  # Should complete in 3 rounds
    
    @pytest.mark.unit
    def test_emergency_decision_making(self, discussion_system, mock_ai_client):
        """Test emergency decision when consensus cannot be reached"""
        # Mock failure to reach consensus
        deadlock_response = {
            "status": "deadlock",
            "conflicting_opinions": [
                {"agent": "Agent1", "position": "Option A"},
                {"agent": "Agent2", "position": "Option B"}
            ]
        }
        
        emergency_response = {
            "emergency_decision": {
                "decision": "Proceed with Option A with modifications",
                "rationale": "Option A aligns better with mission objectives",
                "risk_mitigation": [
                    "Monitor metrics closely",
                    "Prepare Option B as backup"
                ]
            }
        }
        
        mock_ai_client.generate_content.side_effect = [
            Mock(text=json.dumps(deadlock_response)),
            Mock(text=json.dumps(emergency_response))
        ]
        
        # Test emergency decision
        result = discussion_system.make_emergency_decision(deadlock_response)
        
        assert "emergency_decision" in result
        assert "risk_mitigation" in result["emergency_decision"]
        assert len(result["emergency_decision"]["risk_mitigation"]) == 2
    
    @pytest.mark.integration
    def test_full_discussion_workflow(self, mock_ai_client, mock_session_context):
        """Test complete discussion workflow"""
        discussion = MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Create engaging tech video",
            mode="enhanced"
        )
        
        # Mock complete workflow responses
        workflow_responses = [
            # Topic selection
            {"discussion_topics": [{"topic": "Visual Style", "priority": 1}]},
            # Discussion round
            {"agent": "DirectorAgent", "opinion": "Modern style"},
            {"agent": "VisualStyleAgent", "opinion": "Agree, with gradients"},
            # Consensus
            {"consensus": {"agreement_level": 0.9, "final_decision": "Modern with gradients"}},
            # Documentation
            {"status": "documented"}
        ]
        
        mock_ai_client.generate_content.side_effect = [
            Mock(text=json.dumps(resp)) for resp in workflow_responses
        ]
        
        # Execute workflow
        topics = discussion.select_discussion_topics()
        opinions = discussion.conduct_discussion_round(
            topics["discussion_topics"][0]["topic"],
            discussion.agents[:2]
        )
        consensus = discussion.build_consensus(opinions)
        
        # Verify workflow completion
        assert topics is not None
        assert len(opinions) >= 2
        assert consensus["consensus"]["agreement_level"] >= 0.8