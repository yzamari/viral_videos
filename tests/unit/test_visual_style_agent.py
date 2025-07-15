"""
Comprehensive unit tests for VisualStyleAgent class
Tests all methods, edge cases, and error conditions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.visual_style_agent import VisualStyleAgent


class TestVisualStyleAgent(unittest.TestCase):
    """Comprehensive tests for VisualStyleAgent class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.mock_model = Mock()
        
    @patch('src.agents.visual_style_agent.genai')
    def test_init_success(self, mock_genai):
        """Test successful initialization"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VisualStyleAgent(self.api_key)
        
        self.assertEqual(agent.api_key, self.api_key)
        self.assertEqual(agent.model, self.mock_model)
        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.5-flash')
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_success(self, mock_genai):
        """Test successful style analysis"""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = '''
        {
            "primary_style": "cartoon",
            "secondary_style": "comic",
            "style_intensity": "high",
            "color_palette": "vibrant",
            "visual_effects": ["glow", "sparkle"],
            "reasoning": "Cartoon style works best for comedy content",
            "engagement_prediction": "high",
            "appropriateness_score": 0.95
        }
        '''
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test style analysis
        result = agent.analyze_optimal_style(
            topic="Funny cat video",
            target_audience="young adults",
            platform="tiktok",
            content_type="comedy",
            humor_level="high"
        )
        
        # Verify result
        self.assertEqual(result['primary_style'], 'cartoon')
        self.assertEqual(result['secondary_style'], 'comic')
        self.assertEqual(result['style_intensity'], 'high')
        self.assertEqual(result['color_palette'], 'vibrant')
        self.assertEqual(result['visual_effects'], ['glow', 'sparkle'])
        self.assertEqual(result['reasoning'], 'Cartoon style works best for comedy content')
        self.assertEqual(result['engagement_prediction'], 'high')
        self.assertEqual(result['appropriateness_score'], 0.95)
        
        # Verify API call
        self.mock_model.generate_content.assert_called_once()
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_empty_response(self, mock_genai):
        """Test handling of empty response"""
        mock_response = Mock()
        mock_response.text = ""
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test with empty response
        result = agent.analyze_optimal_style(
            topic="Test topic",
            target_audience="general",
            platform="tiktok",
            content_type="educational"
        )
        
        # Should return fallback
        self.assertIn('primary_style', result)
        self.assertIn('fallback', result.get('reasoning', '').lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_no_response(self, mock_genai):
        """Test handling of no response"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = None
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test with no response
        result = agent.analyze_optimal_style(
            topic="Test topic",
            target_audience="general",
            platform="tiktok",
            content_type="educational"
        )
        
        # Should return fallback
        self.assertIn('primary_style', result)
        self.assertIn('fallback', result.get('reasoning', '').lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_invalid_json(self, mock_genai):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.text = "This is not valid JSON"
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test with invalid JSON
        result = agent.analyze_optimal_style(
            topic="Test topic",
            target_audience="general",
            platform="tiktok",
            content_type="educational"
        )
        
        # Should return fallback
        self.assertIn('primary_style', result)
        self.assertIn('fallback', result.get('reasoning', '').lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_malformed_json(self, mock_genai):
        """Test handling of malformed JSON response"""
        mock_response = Mock()
        mock_response.text = '{"primary_style": "cartoon", "incomplete": '
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test with malformed JSON
        result = agent.analyze_optimal_style(
            topic="Test topic",
            target_audience="general",
            platform="tiktok",
            content_type="educational"
        )
        
        # Should return fallback
        self.assertIn('primary_style', result)
        self.assertIn('fallback', result.get('reasoning', '').lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_api_exception(self, mock_genai):
        """Test handling of API exception"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test with API exception
        result = agent.analyze_optimal_style(
            topic="Test topic",
            target_audience="general",
            platform="tiktok",
            content_type="educational"
        )
        
        # Should return fallback
        self.assertIn('primary_style', result)
        self.assertIn('fallback', result.get('reasoning', '').lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_get_fallback_style_tiktok_young(self, mock_genai):
        """Test fallback style for TikTok young audience"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test fallback for TikTok young audience
        result = agent._get_fallback_style(
            topic="Dance challenge",
            target_audience="teenagers",
            platform="tiktok"
        )
        
        # Should prefer animated styles for young TikTok audience
        self.assertIn(result['primary_style'], ['cartoon', 'anime', 'comic'])
        self.assertEqual(result['color_palette'], 'vibrant')
        self.assertEqual(result['engagement_prediction'], 'high')
        self.assertIn('fallback', result['reasoning'].lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_get_fallback_style_linkedin_professional(self, mock_genai):
        """Test fallback style for LinkedIn professional audience"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test fallback for LinkedIn professional audience
        result = agent._get_fallback_style(
            topic="Business strategy",
            target_audience="professionals",
            platform="linkedin"
        )
        
        # Should prefer professional styles for LinkedIn
        self.assertIn(result['primary_style'], ['realistic', 'minimalist'])
        self.assertEqual(result['color_palette'], 'muted')
        self.assertEqual(result['engagement_prediction'], 'medium')
        self.assertIn('fallback', result['reasoning'].lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_get_fallback_style_educational_content(self, mock_genai):
        """Test fallback style for educational content"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test fallback for educational content
        result = agent._get_fallback_style(
            topic="Science explanation",
            target_audience="students",
            platform="youtube"
        )
        
        # Should prefer clear, educational styles
        self.assertIn(result['primary_style'], ['realistic', 'minimalist'])
        self.assertEqual(result['engagement_prediction'], 'medium')
        self.assertIn('fallback', result['reasoning'].lower())
    
    @patch('src.agents.visual_style_agent.genai')
    def test_generate_style_prompt_enhancement(self, mock_genai):
        """Test style prompt enhancement"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VisualStyleAgent(self.api_key)
        
        base_prompt = "Create a video about cats"
        style_decision = {
            'primary_style': 'cartoon',
            'color_palette': 'vibrant',
            'visual_effects': ['glow', 'sparkle']
        }
        
        # Test prompt enhancement
        enhanced_prompt = agent.generate_style_prompt_enhancement(base_prompt, style_decision)
        
        # Verify enhancement
        self.assertIn('cartoon', enhanced_prompt.lower())
        self.assertIn('vibrant', enhanced_prompt.lower())
        self.assertIn('glow', enhanced_prompt.lower())
        self.assertIn('sparkle', enhanced_prompt.lower())
        self.assertIn(base_prompt, enhanced_prompt)
    
    @patch('src.agents.visual_style_agent.genai')
    def test_enhance_prompt_with_style(self, mock_genai):
        """Test simple prompt enhancement with style"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VisualStyleAgent(self.api_key)
        
        base_prompt = "A cat playing"
        style = "cartoon"
        
        # Test simple enhancement
        enhanced_prompt = agent.enhance_prompt_with_style(base_prompt, style)
        
        # Verify enhancement
        self.assertIn('cartoon', enhanced_prompt.lower())
        self.assertIn(base_prompt, enhanced_prompt)
    
    @patch('src.agents.visual_style_agent.genai')
    def test_enhance_prompt_with_style_unknown(self, mock_genai):
        """Test prompt enhancement with unknown style"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VisualStyleAgent(self.api_key)
        
        base_prompt = "A cat playing"
        style = "unknown_style"
        
        # Test enhancement with unknown style
        enhanced_prompt = agent.enhance_prompt_with_style(base_prompt, style)
        
        # Should return original prompt
        self.assertEqual(enhanced_prompt, base_prompt)
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_with_json_in_markdown(self, mock_genai):
        """Test handling of JSON wrapped in markdown code blocks"""
        mock_response = Mock()
        mock_response.text = '''
        Here's the analysis:
        ```json
        {
            "primary_style": "realistic",
            "color_palette": "natural",
            "reasoning": "Realistic style for documentary content"
        }
        ```
        '''
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test with JSON in markdown
        result = agent.analyze_optimal_style(
            topic="Documentary",
            target_audience="adults",
            platform="youtube",
            content_type="educational"
        )
        
        # Should extract JSON correctly
        self.assertEqual(result['primary_style'], 'realistic')
        self.assertEqual(result['color_palette'], 'natural')
        self.assertEqual(result['reasoning'], 'Realistic style for documentary content')
    
    @patch('src.agents.visual_style_agent.genai')
    def test_analyze_optimal_style_platform_specific(self, mock_genai):
        """Test platform-specific style analysis"""
        mock_response = Mock()
        mock_response.text = '''
        {
            "primary_style": "cartoon",
            "platform_optimization": "TikTok prefers dynamic, colorful content"
        }
        '''
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VisualStyleAgent(self.api_key)
        
        # Test TikTok-specific analysis
        result = agent.analyze_optimal_style(
            topic="Dance video",
            target_audience="gen_z",
            platform="tiktok",
            content_type="entertainment"
        )
        
        # Verify platform consideration
        self.assertEqual(result['primary_style'], 'cartoon')
        self.assertIn('TikTok', result.get('platform_optimization', ''))


if __name__ == '__main__':
    unittest.main() 