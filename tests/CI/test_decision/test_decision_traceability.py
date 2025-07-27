"""
Tests for Decision Traceability
Ensures full audit trail of all decisions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
import uuid

from src.decision_framework import DecisionFramework
from src.core.entities import CoreDecisions, GeneratedVideoConfig


class TestDecisionTraceability:
    """Test suite for decision traceability and audit trail"""
    
    @pytest.fixture
    def decision_framework(self, mock_ai_client, mock_session_context):
        """Create DecisionFramework with traceability enabled"""
        framework = DecisionFramework(mock_ai_client, mock_session_context)
        framework.enable_traceability = True
        return framework
    
    @pytest.fixture
    def decision_trace(self):
        """Create a decision trace structure"""
        return {
            "trace_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "decisions": [],
            "sources": [],
            "rationales": []
        }
    
    @pytest.mark.unit
    def test_decision_trace_initialization(self, decision_framework):
        """Test initialization of decision tracing"""
        trace = decision_framework.initialize_trace()
        
        assert "trace_id" in trace
        assert "timestamp" in trace
        assert "decisions" in trace
        assert isinstance(trace["decisions"], list)
        assert len(trace["decisions"]) == 0  # Empty at start
    
    @pytest.mark.unit
    def test_record_decision_with_source(self, decision_framework, mock_ai_client):
        """Test recording a decision with its source"""
        # Make a decision
        decision = {
            "decision_type": "visual_style",
            "value": "modern minimalist",
            "source": "DirectorAgent",
            "reasoning": "Aligns with brand identity and target audience preferences",
            "confidence": 0.95,
            "alternatives_considered": ["vintage", "futuristic", "organic"]
        }
        
        # Record the decision
        trace_entry = decision_framework.record_decision(decision)
        
        # Verify trace entry
        assert trace_entry["decision_type"] == "visual_style"
        assert trace_entry["value"] == "modern minimalist"
        assert trace_entry["source"] == "DirectorAgent"
        assert trace_entry["reasoning"] is not None
        assert trace_entry["confidence"] == 0.95
        assert len(trace_entry["alternatives_considered"]) == 3
        assert "timestamp" in trace_entry
        assert "trace_id" in trace_entry
    
    @pytest.mark.unit
    def test_decision_chain_tracking(self, decision_framework):
        """Test tracking decision dependencies and chains"""
        # Create a chain of decisions
        decisions_chain = [
            {
                "id": "d1",
                "type": "content_type",
                "value": "educational",
                "dependencies": []
            },
            {
                "id": "d2",
                "type": "tone",
                "value": "professional",
                "dependencies": ["d1"]  # Depends on content_type
            },
            {
                "id": "d3",
                "type": "voice_style",
                "value": "authoritative_warm",
                "dependencies": ["d1", "d2"]  # Depends on both
            }
        ]
        
        # Track the chain
        for decision in decisions_chain:
            decision_framework.track_decision_chain(decision)
        
        # Verify chain integrity
        chain = decision_framework.get_decision_chain()
        assert len(chain) == 3
        
        # Verify dependencies are tracked
        d3 = next(d for d in chain if d["id"] == "d3")
        assert len(d3["dependencies"]) == 2
        assert "d1" in d3["dependencies"]
        assert "d2" in d3["dependencies"]
    
    @pytest.mark.unit
    def test_ai_reasoning_capture(self, decision_framework, mock_ai_client):
        """Test capturing AI reasoning for decisions"""
        # Mock AI reasoning response
        reasoning_response = {
            "decision": "use_blue_color_scheme",
            "reasoning_steps": [
                "Blue conveys trust and professionalism",
                "Target audience research shows preference for blue",
                "Competitor analysis reveals market gap for blue branding",
                "Blue provides good contrast for accessibility"
            ],
            "confidence_factors": {
                "market_research": 0.9,
                "brand_alignment": 0.95,
                "accessibility": 1.0,
                "aesthetic_appeal": 0.85
            },
            "final_confidence": 0.925
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(reasoning_response)
        )
        
        # Capture reasoning
        captured = decision_framework.capture_ai_reasoning("color_scheme", "blue")
        
        # Verify comprehensive capture
        assert captured["decision"] == "use_blue_color_scheme"
        assert len(captured["reasoning_steps"]) == 4
        assert captured["final_confidence"] == 0.925
        assert "market_research" in captured["confidence_factors"]
    
    @pytest.mark.unit
    def test_decision_audit_log(self, decision_framework, temp_dir, mock_session_context):
        """Test creation of decision audit log"""
        # Make several decisions
        decisions = [
            {"type": "platform", "value": "youtube", "source": "user_input"},
            {"type": "duration", "value": 60, "source": "user_input"},
            {"type": "style", "value": "modern", "source": "DirectorAgent"},
            {"type": "music", "value": "ambient", "source": "SoundmanAgent"}
        ]
        
        for decision in decisions:
            decision_framework.record_decision(decision)
        
        # Generate audit log
        mock_session_context.get_session_path.return_value = temp_dir
        audit_log = decision_framework.generate_audit_log()
        
        # Verify audit log structure
        assert "audit_metadata" in audit_log
        assert "total_decisions" in audit_log["audit_metadata"]
        assert audit_log["audit_metadata"]["total_decisions"] == 4
        
        assert "decisions_by_source" in audit_log
        assert "user_input" in audit_log["decisions_by_source"]
        assert audit_log["decisions_by_source"]["user_input"] == 2
        
        assert "decision_timeline" in audit_log
        assert len(audit_log["decision_timeline"]) == 4
    
    @pytest.mark.unit
    def test_decision_conflict_documentation(self, decision_framework, mock_ai_client):
        """Test documentation of decision conflicts and resolutions"""
        # Create a conflict
        conflict = {
            "conflict_id": "c1",
            "conflicting_decisions": [
                {"source": "TrendAnalyst", "suggestion": "vertical_video"},
                {"source": "Director", "suggestion": "horizontal_video"}
            ],
            "context": "Platform is YouTube but trend suggests vertical",
            "resolution": {
                "final_decision": "horizontal_video",
                "reasoning": "YouTube audience expects horizontal format",
                "compromise": "Add vertical clips for shorts",
                "resolver": "SuperMasterAgent"
            }
        }
        
        # Document the conflict
        decision_framework.document_conflict(conflict)
        
        # Verify conflict is tracked
        conflicts = decision_framework.get_conflicts()
        assert len(conflicts) == 1
        assert conflicts[0]["conflict_id"] == "c1"
        assert conflicts[0]["resolution"]["final_decision"] == "horizontal_video"
    
    @pytest.mark.unit
    def test_decision_versioning(self, decision_framework):
        """Test versioning of decisions when they change"""
        # Initial decision
        v1 = {
            "decision_id": "style_001",
            "type": "visual_style",
            "value": "minimalist",
            "version": 1,
            "timestamp": datetime.now().isoformat()
        }
        
        decision_framework.record_decision(v1)
        
        # Updated decision
        v2 = {
            "decision_id": "style_001",
            "type": "visual_style", 
            "value": "minimalist_with_accents",
            "version": 2,
            "timestamp": datetime.now().isoformat(),
            "change_reason": "Agent discussion suggested adding accent colors"
        }
        
        decision_framework.record_decision(v2)
        
        # Get decision history
        history = decision_framework.get_decision_history("style_001")
        
        assert len(history) == 2
        assert history[0]["version"] == 1
        assert history[1]["version"] == 2
        assert history[1]["change_reason"] is not None
    
    @pytest.mark.unit
    def test_decision_impact_tracking(self, decision_framework):
        """Test tracking the impact of decisions on final output"""
        # Record decision with expected impact
        decision_with_impact = {
            "type": "quality_preset",
            "value": "ultra_high",
            "expected_impacts": [
                {"component": "render_time", "effect": "increase", "magnitude": "3x"},
                {"component": "file_size", "effect": "increase", "magnitude": "5x"},
                {"component": "visual_quality", "effect": "increase", "magnitude": "2x"}
            ],
            "actual_impacts": None  # To be filled after generation
        }
        
        decision_framework.record_decision(decision_with_impact)
        
        # Simulate recording actual impacts
        actual_impacts = [
            {"component": "render_time", "effect": "increase", "magnitude": "2.8x"},
            {"component": "file_size", "effect": "increase", "magnitude": "4.2x"},
            {"component": "visual_quality", "effect": "increase", "magnitude": "2.1x"}
        ]
        
        decision_framework.record_actual_impacts("quality_preset", actual_impacts)
        
        # Verify impact tracking
        decision = decision_framework.get_decision("quality_preset")
        assert decision["actual_impacts"] is not None
        assert len(decision["actual_impacts"]) == 3
    
    @pytest.mark.unit
    def test_decision_export_formats(self, decision_framework):
        """Test exporting decision trace in various formats"""
        # Add some decisions
        for i in range(5):
            decision_framework.record_decision({
                "type": f"decision_{i}",
                "value": f"value_{i}",
                "source": f"agent_{i}"
            })
        
        # Export as JSON
        json_export = decision_framework.export_trace("json")
        assert isinstance(json_export, str)
        parsed = json.loads(json_export)
        assert "decisions" in parsed
        
        # Export as summary
        summary = decision_framework.export_trace("summary")
        assert "Total decisions:" in summary
        assert "Sources:" in summary
        
        # Export as timeline
        timeline = decision_framework.export_trace("timeline")
        assert isinstance(timeline, list)
        assert all("timestamp" in entry for entry in timeline)
    
    @pytest.mark.unit
    def test_decision_compliance_checking(self, decision_framework):
        """Test checking decisions against constraints"""
        # Define constraints
        constraints = {
            "duration": {"min": 15, "max": 300},
            "platform": ["youtube", "instagram", "tiktok"],
            "quality": ["low", "medium", "high", "ultra"],
            "language": ["en", "es", "fr", "de", "ja", "ar", "he"]
        }
        
        decision_framework.set_constraints(constraints)
        
        # Test compliant decisions
        compliant_decisions = [
            {"type": "duration", "value": 60},
            {"type": "platform", "value": "youtube"},
            {"type": "quality", "value": "high"}
        ]
        
        for decision in compliant_decisions:
            result = decision_framework.check_compliance(decision)
            assert result["compliant"] is True
        
        # Test non-compliant decisions
        non_compliant = {"type": "duration", "value": 400}  # Exceeds max
        result = decision_framework.check_compliance(non_compliant)
        assert result["compliant"] is False
        assert "reason" in result
    
    @pytest.mark.integration
    def test_full_decision_traceability_workflow(self, decision_framework, mock_ai_client, mock_session_context, temp_dir):
        """Test complete decision traceability workflow"""
        # Initialize trace
        trace = decision_framework.initialize_trace()
        
        # Make various decisions with full tracking
        decision_flow = [
            # User inputs
            {"type": "mission", "value": "Create AI education video", "source": "user"},
            {"type": "platform", "value": "youtube", "source": "user"},
            
            # AI decisions
            {"type": "content_structure", "value": "problem-solution", "source": "DirectorAgent"},
            {"type": "visual_style", "value": "tech-modern", "source": "VisualStyleAgent"},
            {"type": "voice_type", "value": "professional-female", "source": "VoiceDirectorAgent"},
            
            # Conflict resolution
            {
                "type": "music_style",
                "value": "subtle-electronic",
                "source": "conflict_resolution",
                "conflict_between": ["SoundmanAgent:epic-orchestral", "DirectorAgent:minimal-ambient"]
            }
        ]
        
        # Process each decision
        for decision in decision_flow:
            # Add reasoning
            decision["reasoning"] = f"Reasoning for {decision['type']}"
            decision["confidence"] = 0.8 + (0.15 if decision["source"] != "user" else 0.2)
            
            # Record decision
            decision_framework.record_decision(decision)
        
        # Generate comprehensive audit
        audit = decision_framework.generate_audit_log()
        
        # Save to session
        mock_session_context.get_session_path.return_value = Path(temp_dir)
        decision_framework.save_trace_to_session()
        
        # Verify comprehensive tracking
        assert len(decision_framework.get_all_decisions()) == 6
        assert audit["audit_metadata"]["total_decisions"] == 6
        assert audit["audit_metadata"]["sources"]["user"] == 2
        assert audit["audit_metadata"]["sources"]["DirectorAgent"] == 1
        
        # Verify conflict was tracked
        conflicts = decision_framework.get_conflicts()
        music_conflicts = [c for c in conflicts if "music_style" in str(c)]
        assert len(music_conflicts) > 0