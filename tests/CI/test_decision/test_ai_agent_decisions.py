"""
Tests for AI Agent Decisions
Ensures collaborative decision making between agents works correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
from datetime import datetime

from src.decision_framework import DecisionFramework
from src.discussion.multi_agent_discussion import MultiAgentDiscussion
from src.core.entities import CoreDecisions, GeneratedVideoConfig


class TestAIAgentDecisions:
    """Test suite for AI agent collaborative decision making"""
    
    @pytest.fixture
    def decision_framework(self, mock_ai_client, mock_session_context):
        """Create DecisionFramework with AI agents enabled"""
        framework = DecisionFramework(mock_ai_client, mock_session_context)
        framework.enable_ai_agents = True
        return framework
    
    @pytest.fixture
    def multi_agent_system(self, mock_ai_client, mock_session_context):
        """Create multi-agent discussion system"""
        return MultiAgentDiscussion(
            ai_client=mock_ai_client,
            session_context=mock_session_context,
            mission="Create test video",
            mode="enhanced"
        )
    
    @pytest.mark.unit
    def test_agent_decision_contribution(self, decision_framework, mock_ai_client):
        """Test individual agent decision contributions"""
        # Mock agent decisions
        agent_decisions = {
            "DirectorAgent": {
                "decisions": {
                    "narrative_structure": "three-act",
                    "emotional_arc": "curiosity-understanding-inspiration",
                    "pacing": "moderate-build"
                },
                "confidence": 0.9,
                "rationale": "Best structure for educational content"
            },
            "VisualStyleAgent": {
                "decisions": {
                    "aesthetic": "modern-clean",
                    "color_scheme": "blue-white-accent",
                    "typography": "sans-serif-minimal"
                },
                "confidence": 0.85,
                "rationale": "Appeals to professional audience"
            },
            "ScriptWriterAgent": {
                "decisions": {
                    "tone": "conversational-authoritative",
                    "vocabulary_level": "intermediate",
                    "sentence_structure": "varied"
                },
                "confidence": 0.88,
                "rationale": "Balances accessibility with credibility"
            }
        }
        
        # Process agent decisions
        for agent_name, agent_decision in agent_decisions.items():
            mock_ai_client.generate_content.return_value = Mock(
                text=json.dumps(agent_decision)
            )
            
            result = decision_framework.process_agent_decision(agent_name)
            
            # Verify processing
            assert result["agent"] == agent_name
            assert "decisions" in result
            assert result["confidence"] == agent_decision["confidence"]
    
    @pytest.mark.unit
    def test_agent_consensus_building(self, decision_framework, mock_ai_client):
        """Test building consensus from multiple agent decisions"""
        # Mock multiple agent opinions on same topic
        topic = "video_duration"
        agent_opinions = [
            {
                "agent": "DirectorAgent",
                "opinion": 90,  # 90 seconds
                "reasoning": "Enough time for complete narrative"
            },
            {
                "agent": "EditorAgent", 
                "opinion": 60,  # 60 seconds
                "reasoning": "Optimal for attention retention"
            },
            {
                "agent": "TrendAnalystAgent",
                "opinion": 45,  # 45 seconds
                "reasoning": "Current platform trends favor shorter content"
            }
        ]
        
        # Mock consensus response
        consensus_response = {
            "consensus": {
                "topic": topic,
                "final_value": 60,
                "consensus_type": "weighted_average",
                "weights": {
                    "DirectorAgent": 0.4,
                    "EditorAgent": 0.35,
                    "TrendAnalystAgent": 0.25
                },
                "agreement_score": 0.75,
                "dissent": []
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(consensus_response)
        )
        
        # Build consensus
        consensus = decision_framework.build_agent_consensus(topic, agent_opinions)
        
        # Verify consensus
        assert consensus["consensus"]["final_value"] == 60
        assert consensus["consensus"]["agreement_score"] == 0.75
        assert len(consensus["consensus"]["dissent"]) == 0
    
    @pytest.mark.unit
    def test_agent_decision_conflicts(self, decision_framework, mock_ai_client):
        """Test handling of conflicting agent decisions"""
        # Create conflicting decisions
        conflicts = [
            {
                "topic": "music_style",
                "agent1": {"name": "DirectorAgent", "choice": "minimal_ambient"},
                "agent2": {"name": "SoundmanAgent", "choice": "epic_orchestral"},
                "severity": "high"
            },
            {
                "topic": "transition_style",
                "agent1": {"name": "EditorAgent", "choice": "quick_cuts"},
                "agent2": {"name": "DirectorAgent", "choice": "slow_fades"},
                "severity": "medium"
            }
        ]
        
        # Mock conflict resolution
        resolution_response = {
            "resolutions": [
                {
                    "topic": "music_style",
                    "resolution": "layered_approach",
                    "details": "Start minimal, build to orchestral for climax",
                    "satisfies_both": True
                },
                {
                    "topic": "transition_style", 
                    "resolution": "context_based",
                    "details": "Quick cuts for energy, slow fades for reflection",
                    "satisfies_both": True
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(resolution_response)
        )
        
        # Resolve conflicts
        resolutions = decision_framework.resolve_agent_conflicts(conflicts)
        
        # Verify resolutions
        assert len(resolutions["resolutions"]) == 2
        assert all(r["satisfies_both"] for r in resolutions["resolutions"])
    
    @pytest.mark.unit
    def test_agent_expertise_weighting(self, decision_framework):
        """Test weighting decisions based on agent expertise"""
        # Define agent expertise areas
        agent_expertise = {
            "DirectorAgent": ["narrative", "structure", "pacing", "emotion"],
            "VisualStyleAgent": ["colors", "typography", "layout", "aesthetics"],
            "SoundmanAgent": ["music", "sound_effects", "audio_mix"],
            "EditorAgent": ["cuts", "transitions", "timing", "flow"]
        }
        
        # Test expertise-based weighting
        decision_topic = "color_scheme"
        
        weights = decision_framework.calculate_agent_weights(
            decision_topic,
            agent_expertise
        )
        
        # VisualStyleAgent should have highest weight for color decisions
        assert weights["VisualStyleAgent"] > weights["DirectorAgent"]
        assert weights["VisualStyleAgent"] > weights["SoundmanAgent"]
        assert sum(weights.values()) == 1.0  # Weights sum to 1
    
    @pytest.mark.unit
    def test_multi_round_agent_discussion(self, multi_agent_system, mock_ai_client):
        """Test multi-round agent discussions for complex decisions"""
        # Mock multi-round discussion
        rounds = [
            {
                "round": 1,
                "topic": "Overall video concept",
                "participants": ["DirectorAgent", "ScriptWriterAgent"],
                "outcome": "Initial concept defined",
                "consensus": 0.7
            },
            {
                "round": 2,
                "topic": "Refine visual approach",
                "participants": ["DirectorAgent", "VisualStyleAgent", "EditorAgent"],
                "outcome": "Visual style agreed",
                "consensus": 0.85
            },
            {
                "round": 3,
                "topic": "Finalize all decisions",
                "participants": "all",
                "outcome": "Complete agreement",
                "consensus": 0.92
            }
        ]
        
        # Process each round
        for round_data in rounds:
            mock_ai_client.generate_content.return_value = Mock(
                text=json.dumps(round_data)
            )
            
            result = multi_agent_system.conduct_discussion_round(
                round_data["topic"],
                multi_agent_system.agents if round_data["participants"] == "all" else None
            )
            
            # Verify progression
            assert result["round"] == round_data["round"]
            assert result["consensus"] >= 0.7
            
        # Final consensus should be high
        assert rounds[-1]["consensus"] > 0.9
    
    @pytest.mark.unit
    def test_agent_decision_validation(self, decision_framework, mock_ai_client):
        """Test validation of agent decisions against constraints"""
        # Define validation rules
        validation_rules = {
            "duration": {"min": 30, "max": 300},
            "complexity": ["simple", "moderate", "complex"],
            "style_consistency": True,
            "platform_compliance": True
        }
        
        # Test valid agent decision
        valid_decision = {
            "agent": "DirectorAgent",
            "decisions": {
                "duration": 60,
                "complexity": "moderate",
                "style": "consistent_modern"
            }
        }
        
        validation_result = decision_framework.validate_agent_decision(
            valid_decision,
            validation_rules
        )
        
        assert validation_result["valid"] is True
        assert len(validation_result["issues"]) == 0
        
        # Test invalid agent decision
        invalid_decision = {
            "agent": "DirectorAgent",
            "decisions": {
                "duration": 400,  # Exceeds max
                "complexity": "extreme",  # Not in allowed values
                "style": "inconsistent"
            }
        }
        
        validation_result = decision_framework.validate_agent_decision(
            invalid_decision,
            validation_rules
        )
        
        assert validation_result["valid"] is False
        assert len(validation_result["issues"]) >= 2
    
    @pytest.mark.unit
    def test_agent_decision_priority(self, decision_framework):
        """Test prioritization of agent decisions"""
        # Define decision priority matrix
        priority_matrix = {
            "critical": ["platform", "duration", "language"],
            "high": ["visual_style", "narrative_structure", "voice_type"],
            "medium": ["transitions", "music_style", "color_scheme"],
            "low": ["effects", "filters", "metadata"]
        }
        
        # Agent decisions with different priorities
        agent_decisions = [
            {"agent": "A1", "topic": "effects", "value": "minimal"},  # Low
            {"agent": "A2", "topic": "platform", "value": "youtube"},  # Critical
            {"agent": "A3", "topic": "visual_style", "value": "modern"},  # High
        ]
        
        # Sort by priority
        sorted_decisions = decision_framework.prioritize_decisions(
            agent_decisions,
            priority_matrix
        )
        
        # Verify critical decisions come first
        assert sorted_decisions[0]["topic"] == "platform"
        assert sorted_decisions[1]["topic"] == "visual_style"
        assert sorted_decisions[2]["topic"] == "effects"
    
    @pytest.mark.unit
    def test_agent_learning_feedback(self, decision_framework, mock_ai_client):
        """Test agent learning from decision outcomes"""
        # Record decision and outcome
        decision_record = {
            "decision_id": "d123",
            "agent": "TrendAnalystAgent",
            "decision": "use_vertical_format",
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat()
        }
        
        outcome_record = {
            "decision_id": "d123",
            "outcome": "positive",
            "metrics": {
                "engagement_rate": 0.12,  # 12% - above average
                "completion_rate": 0.85,   # 85% - very good
                "feedback_sentiment": 0.9  # 90% positive
            },
            "lesson": "Vertical format performed well for this content type"
        }
        
        # Process feedback
        feedback_result = decision_framework.process_agent_feedback(
            decision_record,
            outcome_record
        )
        
        # Verify learning
        assert feedback_result["success"] is True
        assert feedback_result["confidence_adjustment"] > 0  # Should increase
        assert "lesson" in feedback_result
    
    @pytest.mark.unit
    def test_emergency_agent_override(self, decision_framework, mock_ai_client):
        """Test emergency override by senior agents"""
        # Normal decision
        normal_decision = {
            "topic": "content_safety",
            "value": "include_controversial_topic",
            "agent": "ScriptWriterAgent",
            "confidence": 0.7
        }
        
        # Emergency override by safety agent
        override_response = {
            "override": True,
            "overriding_agent": "CulturalSensitivityAgent",
            "reason": "Content may be culturally insensitive",
            "new_decision": "modify_or_remove_topic",
            "severity": "high",
            "authority_level": "veto"
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(override_response)
        )
        
        # Process override
        final_decision = decision_framework.check_for_override(normal_decision)
        
        # Verify override applied
        assert final_decision["value"] != normal_decision["value"]
        assert final_decision["overridden"] is True
        assert final_decision["override_reason"] is not None
    
    @pytest.mark.integration
    def test_complete_agent_decision_workflow(self, decision_framework, multi_agent_system, mock_ai_client):
        """Test complete agent decision workflow"""
        # Setup comprehensive decision scenario
        mission = "Create educational video about climate change"
        
        # Phase 1: Initial agent proposals
        initial_proposals = {
            "DirectorAgent": {"tone": "urgent_but_hopeful"},
            "ScriptWriterAgent": {"structure": "problem_solution_action"},
            "VisualStyleAgent": {"palette": "earth_tones_with_green"},
            "SoundmanAgent": {"music": "atmospheric_building"}
        }
        
        # Phase 2: Discussion and refinement
        discussion_rounds = 3
        consensus_scores = [0.7, 0.85, 0.95]
        
        for round in range(discussion_rounds):
            mock_ai_client.generate_content.return_value = Mock(
                text=json.dumps({
                    "round": round + 1,
                    "consensus": consensus_scores[round],
                    "refinements": "Adjustments made based on discussion"
                })
            )
            
            multi_agent_system.conduct_discussion_round(
                f"Refinement round {round + 1}",
                multi_agent_system.agents
            )
        
        # Phase 3: Final decision compilation
        final_decisions_response = {
            "compiled_decisions": {
                "tone": "urgent_but_hopeful",
                "structure": "problem_solution_action",
                "visual_style": "documentary_earth_tones",
                "music": "atmospheric_crescendo",
                "duration": 90,
                "platform_optimizations": {
                    "youtube": "16:9_with_chapters",
                    "instagram": "9:16_reels_version"
                }
            },
            "consensus_level": 0.95,
            "dissenting_opinions": [],
            "implementation_ready": True
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(final_decisions_response)
        )
        
        # Compile final decisions
        final = decision_framework.compile_agent_decisions()
        
        # Verify complete workflow
        assert final["consensus_level"] >= 0.9
        assert final["implementation_ready"] is True
        assert "platform_optimizations" in final["compiled_decisions"]
        assert len(final["dissenting_opinions"]) == 0