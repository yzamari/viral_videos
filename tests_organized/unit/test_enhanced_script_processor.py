"""
Comprehensive unit tests for EnhancedScriptProcessor class
Tests all methods, duration alignment, and error conditions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from src.generators.enhanced_script_processor import EnhancedScriptProcessor
from src.models.video_models import Language

class TestEnhancedScriptProcessor(unittest.TestCase):
    """Comprehensive tests for EnhancedScriptProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.mock_model = Mock()
        
    @patch('src.generators.enhanced_script_processor.genai')
    def test_init_success(self, mock_genai):
        """Test successful initialization"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        
        self.assertEqual(processor.api_key, self.api_key)
        self.assertEqual(processor.model, self.mock_model)
        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.5-flash')

    @patch('src.generators.enhanced_script_processor.genai')
    def test_process_script_for_tts_success(self, mock_genai):
        """Test successful script processing"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Mock AI response
        mock_response = Mock()
        mock_response.text = '''
        {
            "optimized_script": "This is an optimized script for TTS.",
            "segments": [
                {
                    "text": "This is an optimized script for TTS.",
                    "duration": 3.0,
                    "word_count": 7,
                    "voice_suggestion": "storyteller"
                }
            ],
            "total_estimated_duration": 3.0,
            "total_word_count": 7,
            "optimization_notes": "Script optimized for TTS delivery",
            "duration_match": "perfect",
            "tts_optimizations": ["Clear pronunciation", "Proper pacing"]
        }
        '''
        self.mock_model.generate_content.return_value = mock_response
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        result = processor.process_script_for_tts(
            script_content="Test script",
            language=Language.ENGLISH_US,
            target_duration=5.0
        )
        
        # Verify result structure - using optimized_script not final_script
        self.assertIn('optimized_script', result)
        self.assertIn('segments', result)
        self.assertIn('total_estimated_duration', result)
        self.assertIn('total_word_count', result)
        self.assertIn('optimization_notes', result)
        self.assertIn('duration_match', result)
        self.assertIn('tts_optimizations', result)
        self.assertIn('language', result)
        self.assertIn('processing_timestamp', result)
        self.assertIn('target_duration', result)
        
        # Verify content
        self.assertEqual(result['optimized_script'], "This is an optimized script for TTS.")
        self.assertEqual(result['language'], Language.ENGLISH_US.value)
        self.assertEqual(result['target_duration'], 5.0)
        self.assertEqual(len(result['segments']), 1)

    @patch('src.generators.enhanced_script_processor.genai')
    def test_process_script_for_tts_invalid_json(self, mock_genai):
        """Test processing with invalid JSON response"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        self.mock_model.generate_content.return_value = mock_response
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        result = processor.process_script_for_tts(
            script_content="Test script",
            language=Language.ENGLISH_US,
            target_duration=5.0
        )
        
        # Should return fallback result
        self.assertIn('optimized_script', result)
        self.assertEqual(result['duration_match'], 'fallback')
        self.assertEqual(result['optimization_notes'], 'Fallback processing applied')

    @patch('src.generators.enhanced_script_processor.genai')
    def test_process_script_for_tts_no_response(self, mock_genai):
        """Test processing when model returns no response"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Mock no response
        self.mock_model.generate_content.return_value = None
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        result = processor.process_script_for_tts(
            script_content="Test script",
            language=Language.ENGLISH_US,
            target_duration=5.0
        )
        
        # Should return fallback result
        self.assertIn('optimized_script', result)
        self.assertEqual(result['duration_match'], 'fallback')

    @patch('src.generators.enhanced_script_processor.genai')
    def test_process_script_for_tts_empty_response(self, mock_genai):
        """Test processing with empty response"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Mock empty response
        mock_response = Mock()
        mock_response.text = ""
        self.mock_model.generate_content.return_value = mock_response
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        result = processor.process_script_for_tts(
            script_content="Test script",
            language=Language.ENGLISH_US,
            target_duration=5.0
        )
        
        # Should return fallback result
        self.assertIn('optimized_script', result)
        self.assertEqual(result['duration_match'], 'fallback')

    @patch('src.generators.enhanced_script_processor.genai')
    def test_process_script_for_tts_api_exception(self, mock_genai):
        """Test processing when API throws exception"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Mock API exception
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        result = processor.process_script_for_tts(
            script_content="Test script",
            language=Language.ENGLISH_US,
            target_duration=5.0
        )
        
        # Should return fallback result
        self.assertIn('optimized_script', result)
        self.assertEqual(result['duration_match'], 'fallback')
        self.assertEqual(result['optimization_notes'], 'Fallback processing applied')

    @patch('src.generators.enhanced_script_processor.genai')
    def test_process_script_for_tts_different_languages(self, mock_genai):
        """Test processing with different languages"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Mock response
        mock_response = Mock()
        mock_response.text = '''
        {
            "optimized_script": "Script optimizado",
            "segments": [{"text": "Script optimizado", "duration": 2.0, "word_count": 2, "voice_suggestion": "storyteller"}],
            "total_estimated_duration": 2.0,
            "total_word_count": 2,
            "optimization_notes": "Optimizado para TTS",
            "duration_match": "perfect",
            "tts_optimizations": ["Pronunciación clara"]
        }
        '''
        self.mock_model.generate_content.return_value = mock_response
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        
        # Test different languages - using correct enum values
        languages = [Language.ENGLISH_US, Language.SPANISH, Language.FRENCH]
        
        for language in languages:
            result = processor.process_script_for_tts(
                script_content="Test script",
                language=language,
                target_duration=5.0
            )
            
            self.assertIn('optimized_script', result)
            self.assertEqual(result['language'], language.value)

    @patch('src.generators.enhanced_script_processor.genai')
    def test_process_script_for_tts_different_durations(self, mock_genai):
        """Test processing with different target durations"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Mock response for first call
        mock_response_1 = Mock()
        mock_response_1.text = '''
        {
            "optimized_script": "Short script",
            "segments": [{"text": "Short script", "duration": 1.0, "word_count": 2, "voice_suggestion": "storyteller"}],
            "total_estimated_duration": 1.0,
            "total_word_count": 2,
            "optimization_notes": "Short duration optimization",
            "duration_match": "perfect",
            "tts_optimizations": ["Concise delivery"]
        }
        '''
        
        # Mock response for second call (longer duration)
        mock_response_2 = Mock()
        mock_response_2.text = '''
        {
            "optimized_script": "Longer script with more content",
            "segments": [{"text": "Longer script with more content", "duration": 2.0, "word_count": 6, "voice_suggestion": "storyteller"}],
            "total_estimated_duration": 2.0,
            "total_word_count": 6,
            "optimization_notes": "Extended for longer duration",
            "duration_match": "perfect",
            "tts_optimizations": ["Extended content"]
        }
        '''
        
        self.mock_model.generate_content.side_effect = [mock_response_1, mock_response_2]
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        
        # Test short duration
        result_short = processor.process_script_for_tts(
            script_content="Test script",
            language=Language.ENGLISH_US,
            target_duration=5.0
        )
        
        self.assertIn('optimized_script', result_short)
        self.assertEqual(result_short['target_duration'], 5.0)
        
        # Test longer duration
        result_long = processor.process_script_for_tts(
            script_content="Test script",
            language=Language.ENGLISH_US,
            target_duration=10.0
        )
        
        self.assertIn('optimized_script', result_long)
        self.assertEqual(result_long['target_duration'], 10.0)

    @patch('src.generators.enhanced_script_processor.genai')
    def test_create_fallback_result(self, mock_genai):
        """Test fallback result creation"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        processor = EnhancedScriptProcessor(api_key=self.api_key)
        
        # Test fallback result creation - with correct signature
        result = processor._create_fallback_result(
            script_content="Test script content",
            language=Language.ENGLISH_US,
            target_duration=5.0
        )
        
        self.assertIn('optimized_script', result)
        self.assertIn('segments', result)
        self.assertEqual(result['duration_match'], 'fallback')
        self.assertEqual(result['optimization_notes'], 'Fallback processing applied')
        self.assertEqual(result['language'], Language.ENGLISH_US.value)
        self.assertEqual(result['target_duration'], 5.0)

if __name__ == '__main__':
    unittest.main() 