"""
Unit tests for MissionAnalyzer
Tests comprehensive mission analysis with various complexity levels
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import asdict

from src.agents.mission_analyzer import MissionAnalyzer, AnalyzedMission
from src.models.video_models import GeneratedVideoConfig, Platform


class TestMissionAnalyzer:
    """Test suite for MissionAnalyzer"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock video generation config"""
        config = Mock(spec=GeneratedVideoConfig)
        config.mission = "Test mission"
        config.target_platform = Platform.YOUTUBE
        config.duration_seconds = 60
        config.visual_style = "dynamic"
        config.tone = "engaging"
        config.target_audience = "general"
        config.character = "Test character"
        config.scene = "Test scene"
        config.theme = "Test theme"
        config.style_template = "default"
        config.voice = "default"
        config.mode = "enhanced"
        config.language = "en-US"
        return config
    
    @pytest.fixture
    def analyzer(self):
        """Create MissionAnalyzer instance"""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                return MissionAnalyzer(api_key="test_key")
    
    @pytest.mark.asyncio
    async def test_simple_mission_analysis(self, analyzer, mock_config):
        """Test analysis of simple mission"""
        mock_config.mission = "News anchor says: 'Breaking news about weather.' Show storm clouds."
        
        # Mock Gemini response
        mock_response = {
            "script_content": "Breaking news about weather.",
            "visual_sequence": [{
                "scene_number": 1,
                "duration_seconds": 30,
                "description": "News anchor speaking",
                "camera_angle": "medium shot",
                "characters_present": ["News Anchor"],
                "key_elements": ["news desk"],
                "transitions": "cut"
            }],
            "character_details": {},
            "scene_descriptions": ["News studio"],
            "technical_requirements": {"effects": [], "transitions": ["cuts"]},
            "timing_breakdown": [],
            "content_type": "news",
            "emotional_arc": "steady",
            "key_moments": [],
            "platform_optimizations": {},
            "confidence_score": 0.95,
            "complexity_level": "simple",
            "production_notes": ""
        }
        
        with patch.object(analyzer, '_get_gemini_analysis', 
                         return_value=str(mock_response).replace("'", '"')):
            result = await analyzer.analyze_mission(mock_config)
            
            assert result.script_content == "Breaking news about weather."
            assert len(result.visual_sequence) == 1
            assert result.content_type == "news"
            assert result.complexity_level == "simple"
            assert result.confidence_score == 0.95
    
    @pytest.mark.asyncio
    async def test_complex_mission_analysis(self, analyzer, mock_config):
        """Test analysis of complex mission"""
        mock_config.mission = """
        Family Guy style animated news. Maryam says: 'Breaking news!' 
        Cut to explosion. Peter: 'Oh no!' Show chaos. 
        Brian explains: 'This is serious.' Chicken fight ensues.
        """
        
        # Test fallback when Gemini fails
        with patch.object(analyzer, '_get_gemini_analysis', return_value=None):
            result = await analyzer.analyze_mission(mock_config)
            
            # Should use simple analysis
            assert "Breaking news!" in result.script_content
            assert "Oh no!" in result.script_content
            assert "This is serious." in result.script_content
            assert result.confidence_score == 0.5
            assert result.complexity_level == "simple"
    
    @pytest.mark.asyncio
    async def test_multishot_examples(self, analyzer, mock_config):
        """Test that multishot examples are included"""
        prompt = analyzer._build_analysis_prompt(mock_config, use_multishot=True)
        
        assert "EXAMPLE 1" in prompt
        assert "News Parody" in prompt
        assert "EXAMPLE 2" in prompt
        assert "Educational Content" in prompt
    
    @pytest.mark.asyncio
    async def test_character_name_removal(self, analyzer, mock_config):
        """Test that character names are removed from dialogue"""
        mock_config.mission = "John: 'Hello world!' Mary: 'How are you?'"
        
        with patch.object(analyzer, '_get_gemini_analysis', return_value=None):
            result = await analyzer.analyze_mission(mock_config)
            
            # Simple analysis should remove character names
            assert "John:" not in result.script_content
            assert "Mary:" not in result.script_content
            assert "Hello world!" in result.script_content
            assert "How are you?" in result.script_content
    
    @pytest.mark.asyncio
    async def test_platform_specific_analysis(self, analyzer, mock_config):
        """Test platform-specific optimizations"""
        mock_config.target_platform = Platform.TIKTOK
        mock_config.duration_seconds = 30
        
        prompt = analyzer._build_analysis_prompt(mock_config, use_multishot=False)
        
        assert "PLATFORM: tiktok" in prompt
        assert "DURATION: 30 seconds" in prompt
        assert "fast-paced" in prompt
    
    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer, mock_config):
        """Test error handling in analysis"""
        # Test with Gemini initialization failure
        with patch('google.generativeai.GenerativeModel', side_effect=Exception("API Error")):
            analyzer = MissionAnalyzer(api_key="test_key")
            
        result = await analyzer.analyze_mission(mock_config)
        
        # Should still return a result using simple analysis
        assert result is not None
        assert result.confidence_score == 0.5
        assert "Simple fallback analysis" in result.production_notes
    
    def test_parse_analysis_with_malformed_json(self, analyzer, mock_config):
        """Test parsing malformed JSON response"""
        malformed_response = '{"script_content": "Test", invalid json}'
        
        result = analyzer._parse_analysis(malformed_response, mock_config)
        
        assert result is None
    
    def test_simple_analysis_fallback(self, analyzer, mock_config):
        """Test simple analysis fallback logic"""
        mock_config.mission = "Complex mission with 'quoted text' and *actions*"
        mock_config.duration_seconds = 45
        
        result = analyzer._simple_analysis(mock_config)
        
        assert result is not None
        assert "quoted text" in result.script_content
        assert len(result.visual_sequence) > 0
        assert result.confidence_score == 0.5
        
        # Check scene calculation
        expected_scenes = max(3, min(8, 45 // 5))  # Should be 8
        assert len(result.visual_sequence) == expected_scenes
    
    @pytest.mark.asyncio
    async def test_all_context_included(self, analyzer, mock_config):
        """Test that all context from config is included in analysis"""
        mock_config.visual_style = "Family Guy animation"
        mock_config.tone = "satirical"
        mock_config.character = "Maryam: News anchor with hijab"
        mock_config.theme = "nuclear-news"
        
        prompt = analyzer._build_analysis_prompt(mock_config, use_multishot=False)
        
        assert "VISUAL STYLE: Family Guy animation" in prompt
        assert "TONE: satirical" in prompt
        assert "CHARACTER: Maryam: News anchor with hijab" in prompt
        assert "THEME: nuclear-news" in prompt
    
    def test_analyzed_mission_serialization(self):
        """Test AnalyzedMission to_dict method"""
        mission = AnalyzedMission(
            script_content="Test script",
            visual_sequence=[{"scene": 1}],
            character_details={"char1": {"appearance": "test"}},
            scene_descriptions=["Scene 1"],
            technical_requirements={"effects": ["explosion"]},
            timing_breakdown=[{"segment": "intro"}],
            content_type="comedy",
            emotional_arc="rising",
            key_moments=["climax"],
            platform_optimizations={"hook": "strong"},
            confidence_score=0.9,
            complexity_level="moderate",
            production_notes="Test notes"
        )
        
        data = mission.to_dict()
        
        assert data['script_content'] == "Test script"
        assert data['confidence_score'] == 0.9
        assert data['complexity_level'] == "moderate"
        assert len(data['visual_sequence']) == 1


class TestMissionAnalyzerIntegration:
    """Integration tests for MissionAnalyzer"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_gemini_analysis(self):
        """Test with real Gemini API (requires API key)"""
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            pytest.skip("No API key available for integration test")
        
        analyzer = MissionAnalyzer(api_key=api_key)
        
        config = Mock()
        config.mission = "News anchor reports: 'Breaking news!' Show explosion."
        config.target_platform = Platform.YOUTUBE
        config.duration_seconds = 30
        config.visual_style = "realistic"
        config.tone = "serious"
        config.target_audience = "general"
        
        result = await analyzer.analyze_mission(config)
        
        assert result is not None
        assert len(result.script_content) > 0
        assert result.confidence_score > 0.5
        assert result.content_type in ["news", "news_report", "breaking_news"]