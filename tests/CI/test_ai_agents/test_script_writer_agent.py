"""
Tests for ScriptWriterAgent
Ensures the ScriptWriterAgent properly generates and optimizes scripts
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.agents.script_writer_agent import ScriptWriterAgent
from src.core.entities import CoreDecisions, GeneratedVideoConfig


class TestScriptWriterAgent:
    """Test suite for ScriptWriterAgent"""
    
    @pytest.fixture
    def script_writer(self, mock_ai_client):
        """Create ScriptWriterAgent instance"""
        return ScriptWriterAgent(mock_ai_client)
    
    @pytest.fixture
    def sample_decisions(self):
        """Create sample decisions for testing"""
        config = GeneratedVideoConfig(
            topic="Artificial Intelligence",
            duration=60,
            platform="youtube",
            language="en"
        )
        
        decisions = CoreDecisions(
            video_config=config,
            mission="Explain AI benefits",
            target_platform="youtube",
            language="en",
            duration=60
        )
        
        return decisions
    
    @pytest.mark.unit
    def test_script_writer_initialization(self, mock_ai_client):
        """Test ScriptWriterAgent initializes correctly"""
        agent = ScriptWriterAgent(mock_ai_client)
        assert agent is not None
        assert agent.ai_client == mock_ai_client
        assert agent.name == "ScriptWriterAgent"
    
    @pytest.mark.unit
    def test_generate_script_segments(self, script_writer, mock_ai_client, sample_decisions):
        """Test script segment generation"""
        # Mock AI response
        script_response = {
            "script_segments": [
                {
                    "segment_number": 1,
                    "narrator_text": "Artificial Intelligence is transforming our world in unprecedented ways.",
                    "visual_description": "Montage of AI applications in various industries",
                    "duration": 5.0,
                    "emotional_tone": "intriguing"
                },
                {
                    "segment_number": 2,
                    "narrator_text": "From healthcare to transportation, AI is making life better.",
                    "visual_description": "Split screen showing medical diagnosis AI and self-driving cars",
                    "duration": 5.0,
                    "emotional_tone": "optimistic"
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(script_response)
        )
        
        # Test
        segments = script_writer.generate_script(sample_decisions)
        
        # Assert
        assert len(segments["script_segments"]) == 2
        assert segments["script_segments"][0]["narrator_text"] is not None
        assert segments["script_segments"][0]["visual_description"] is not None
        assert segments["script_segments"][0]["duration"] == 5.0
    
    @pytest.mark.unit
    def test_word_timing_calculation(self, script_writer):
        """Test accurate word timing calculation"""
        test_cases = [
            {
                "text": "Hello world",
                "expected_duration": 1.0,  # ~2 words at 120 wpm
                "language": "en"
            },
            {
                "text": "This is a longer sentence with more words to speak",
                "expected_duration": 4.5,  # ~10 words
                "language": "en"
            },
            {
                "text": "Bonjour le monde",  # French
                "expected_duration": 1.5,  # Slightly slower for French
                "language": "fr"
            }
        ]
        
        for case in test_cases:
            duration = script_writer.calculate_speech_duration(
                case["text"],
                case["language"]
            )
            
            # Allow 20% variance
            assert abs(duration - case["expected_duration"]) < case["expected_duration"] * 0.2
    
    @pytest.mark.unit
    def test_script_pacing_adjustment(self, script_writer, mock_ai_client):
        """Test script pacing adjustment for target duration"""
        target_duration = 30
        initial_segments = [
            {"narrator_text": "Segment 1 text", "duration": 5},
            {"narrator_text": "Segment 2 text", "duration": 5},
            {"narrator_text": "Segment 3 text", "duration": 5}
        ]
        
        # Total duration is 15s, need to expand to 30s
        adjusted_response = {
            "adjusted_segments": [
                {"narrator_text": "Expanded segment 1 with more detailed explanation", "duration": 10},
                {"narrator_text": "Expanded segment 2 with additional context and examples", "duration": 10},
                {"narrator_text": "Expanded segment 3 with comprehensive conclusion", "duration": 10}
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(adjusted_response)
        )
        
        # Test
        adjusted = script_writer.adjust_pacing(initial_segments, target_duration)
        
        # Assert
        total_duration = sum(s["duration"] for s in adjusted["adjusted_segments"])
        assert total_duration == target_duration
    
    @pytest.mark.unit
    def test_platform_specific_scripting(self, script_writer, mock_ai_client):
        """Test platform-specific script adaptations"""
        platforms = {
            "youtube": {
                "hook_style": "Question or surprising fact",
                "cta_style": "Subscribe and hit the bell",
                "max_segment_length": 300  # words
            },
            "instagram": {
                "hook_style": "Visual hook with text overlay",
                "cta_style": "Link in bio",
                "max_segment_length": 50  # words
            },
            "tiktok": {
                "hook_style": "Immediate action or trend reference",
                "cta_style": "Follow for part 2",
                "max_segment_length": 30  # words
            }
        }
        
        for platform, expectations in platforms.items():
            platform_response = {
                "platform_script": {
                    "hook": f"Platform-specific hook for {platform}",
                    "segments": [{"text": f"Optimized for {platform}"}],
                    "cta": expectations["cta_style"]
                }
            }
            
            mock_ai_client.generate_content.return_value = Mock(
                text=json.dumps(platform_response)
            )
            
            # Test
            script = script_writer.adapt_for_platform(
                "Generic script",
                platform
            )
            
            # Assert
            assert expectations["cta_style"] in script["platform_script"]["cta"]
    
    @pytest.mark.unit
    def test_multilingual_script_generation(self, script_writer, mock_ai_client):
        """Test script generation in multiple languages"""
        languages = ["en", "es", "fr", "de", "ja", "ar", "he"]
        
        for language in languages:
            # Mock language-specific response
            lang_response = {
                "script": {
                    "language": language,
                    "segments": [{
                        "text": f"Script content in {language}",
                        "cultural_adaptations": ["localized references"]
                    }]
                }
            }
            
            mock_ai_client.generate_content.return_value = Mock(
                text=json.dumps(lang_response)
            )
            
            # Test
            script = script_writer.generate_multilingual_script(
                "Test topic",
                language
            )
            
            # Assert
            assert script["script"]["language"] == language
            assert "cultural_adaptations" in script["script"]["segments"][0]
    
    @pytest.mark.unit
    def test_emotional_tone_integration(self, script_writer, mock_ai_client):
        """Test integration of emotional tones in script"""
        emotional_arc = [
            {"segment": 1, "emotion": "curiosity", "intensity": 5},
            {"segment": 2, "emotion": "concern", "intensity": 7},
            {"segment": 3, "emotion": "hope", "intensity": 8},
            {"segment": 4, "emotion": "inspiration", "intensity": 9}
        ]
        
        # Mock response with emotional language
        emotional_response = {
            "emotional_script": [
                {
                    "segment_number": 1,
                    "text": "Have you ever wondered...?",
                    "emotion": "curiosity",
                    "word_choices": ["wondered", "imagine", "discover"]
                },
                {
                    "segment_number": 2,
                    "text": "The challenges we face are real and urgent.",
                    "emotion": "concern",
                    "word_choices": ["challenges", "urgent", "critical"]
                }
            ]
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(emotional_response)
        )
        
        # Test
        script = script_writer.apply_emotional_arc(emotional_arc)
        
        # Assert
        assert script["emotional_script"][0]["emotion"] == "curiosity"
        assert "wondered" in script["emotional_script"][0]["word_choices"]
    
    @pytest.mark.unit
    def test_keyword_integration(self, script_writer, mock_ai_client):
        """Test SEO keyword integration in script"""
        keywords = ["artificial intelligence", "machine learning", "future technology"]
        base_script = "A script about technology"
        
        # Mock response with keywords integrated
        keyword_response = {
            "optimized_script": {
                "segments": [
                    {
                        "text": "Artificial intelligence and machine learning are shaping our future technology landscape.",
                        "keyword_density": 0.3,
                        "keywords_used": ["artificial intelligence", "machine learning", "future technology"]
                    }
                ]
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(keyword_response)
        )
        
        # Test
        optimized = script_writer.integrate_keywords(base_script, keywords)
        
        # Assert
        assert all(kw in optimized["optimized_script"]["segments"][0]["keywords_used"] for kw in keywords)
        assert optimized["optimized_script"]["segments"][0]["keyword_density"] <= 0.5  # Not over-optimized
    
    @pytest.mark.unit
    def test_script_validation(self, script_writer):
        """Test script validation for quality and consistency"""
        valid_script = {
            "segments": [
                {
                    "segment_number": 1,
                    "narrator_text": "This is valid text.",
                    "visual_description": "A valid visual description",
                    "duration": 5.0
                }
            ]
        }
        
        invalid_scripts = [
            {"segments": []},  # Empty
            {"segments": [{"narrator_text": ""}]},  # Empty text
            {"segments": [{"segment_number": 1}]},  # Missing required fields
            {"segments": [{"narrator_text": "Text", "duration": -5}]}  # Invalid duration
        ]
        
        # Test valid script
        assert script_writer.validate_script(valid_script) is True
        
        # Test invalid scripts
        for invalid in invalid_scripts:
            assert script_writer.validate_script(invalid) is False
    
    @pytest.mark.unit
    def test_script_coherence_check(self, script_writer, mock_ai_client):
        """Test script coherence and flow checking"""
        script_segments = [
            {"text": "AI is transforming healthcare."},
            {"text": "Doctors use AI for diagnosis."},
            {"text": "Suddenly, let's talk about cooking."},  # Incoherent
            {"text": "AI helps predict treatment outcomes."}
        ]
        
        # Mock coherence analysis
        coherence_response = {
            "coherence_analysis": {
                "overall_score": 0.7,
                "issues": [
                    {
                        "segment": 3,
                        "issue": "Topic shift without transition",
                        "suggestion": "Add transition or remove off-topic content"
                    }
                ],
                "flow_quality": "needs_improvement"
            }
        }
        
        mock_ai_client.generate_content.return_value = Mock(
            text=json.dumps(coherence_response)
        )
        
        # Test
        analysis = script_writer.check_coherence(script_segments)
        
        # Assert
        assert analysis["coherence_analysis"]["overall_score"] == 0.7
        assert len(analysis["coherence_analysis"]["issues"]) == 1
        assert analysis["coherence_analysis"]["issues"][0]["segment"] == 3
    
    @pytest.mark.integration
    def test_complete_script_generation_workflow(self, script_writer, mock_ai_client, sample_decisions):
        """Test complete script generation workflow"""
        # Setup mock responses for full workflow
        responses = [
            # Initial generation
            {
                "script_segments": [
                    {"segment_number": 1, "narrator_text": "Intro text", "duration": 5},
                    {"segment_number": 2, "narrator_text": "Main content", "duration": 10}
                ]
            },
            # Pacing adjustment
            {"adjusted_segments": [{"duration": 30}, {"duration": 30}]},
            # Platform optimization
            {"platform_script": {"hook": "YouTube hook", "cta": "Subscribe"}},
            # Coherence check
            {"coherence_analysis": {"overall_score": 0.9, "issues": []}}
        ]
        
        mock_ai_client.generate_content.side_effect = [
            Mock(text=json.dumps(resp)) for resp in responses
        ]
        
        # Execute workflow
        script = script_writer.generate_script(sample_decisions)
        adjusted = script_writer.adjust_pacing(script["script_segments"], 60)
        platform_script = script_writer.adapt_for_platform(adjusted, "youtube")
        coherence = script_writer.check_coherence(platform_script["platform_script"])
        
        # Verify complete workflow
        assert script is not None
        assert adjusted is not None
        assert platform_script is not None
        assert coherence["coherence_analysis"]["overall_score"] >= 0.8