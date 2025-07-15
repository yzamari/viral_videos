"""
Comprehensive unit tests for VoiceDirectorAgent class
Tests all methods, edge cases, and error conditions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.voice_director_agent import VoiceDirectorAgent, VoicePersonality, VoiceGender
from src.models.video_models import Language, Platform, VideoCategory


class TestVoiceDirectorAgent(unittest.TestCase):
    """Comprehensive tests for VoiceDirectorAgent class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.mock_model = Mock()
        
    @patch('src.agents.voice_director_agent.genai')
    def test_init_success(self, mock_genai):
        """Test successful initialization"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        self.assertEqual(agent.api_key, self.api_key)
        self.assertEqual(agent.model, self.mock_model)
        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.5-flash')
        
        # Verify voice database is initialized
        self.assertIn(Language.ENGLISH_US, agent.voice_database)
        self.assertIn(VoicePersonality.NARRATOR, agent.voice_database[Language.ENGLISH_US])
    
    @patch('src.agents.voice_director_agent.genai')
    def test_get_voice_config_success(self, mock_genai):
        """Test successful voice configuration"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Mock the analyze_content_and_select_voices method
        agent.analyze_content_and_select_voices = Mock(return_value={
            'voices': ['en-US-Neural2-C', 'en-US-Neural2-D'],
            'strategy': 'multiple',
            'primary_personality': 'storyteller'
        })
        
        # Test voice config
        result = agent.get_voice_config(
            content="Funny cat video",
            platform=Platform.TIKTOK,
            num_clips=2,
            style="humorous",
            tone="funny"
        )
        
        # Verify result
        self.assertEqual(result['voices'], ['en-US-Neural2-C', 'en-US-Neural2-D'])
        self.assertEqual(result['strategy'], 'multiple')
        self.assertEqual(result['primary_personality'], 'storyteller')
        
        # Verify method was called
        agent.analyze_content_and_select_voices.assert_called_once()
    
    @patch('src.agents.voice_director_agent.genai')
    def test_get_voice_config_fallback(self, mock_genai):
        """Test voice configuration fallback"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Mock the analyze_content_and_select_voices method to return no voices
        agent.analyze_content_and_select_voices = Mock(return_value={
            'strategy': 'single',
            'primary_personality': 'narrator'
        })
        
        # Mock the fallback method
        agent._create_fallback_voice_config = Mock(return_value={
            'voices': ['en-US-Neural2-C', 'en-US-Neural2-C'],
            'strategy': 'single',
            'primary_personality': 'professional'
        })
        
        # Test voice config fallback
        result = agent.get_voice_config(
            content="Test content",
            platform=Platform.TIKTOK,
            num_clips=2
        )
        
        # Verify fallback was used
        agent._create_fallback_voice_config.assert_called_once()
        self.assertEqual(result['strategy'], 'single')
        self.assertEqual(result['primary_personality'], 'professional')
    
    @patch('src.agents.voice_director_agent.genai')
    def test_get_voice_config_exception(self, mock_genai):
        """Test voice configuration exception handling"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Mock the analyze_content_and_select_voices method to raise exception
        agent.analyze_content_and_select_voices = Mock(side_effect=Exception("API Error"))
        
        # Mock the fallback method
        agent._create_fallback_voice_config = Mock(return_value={
            'voices': ['en-US-Neural2-C', 'en-US-Neural2-C'],
            'strategy': 'single',
            'primary_personality': 'professional'
        })
        
        # Test voice config with exception
        result = agent.get_voice_config(
            content="Test content",
            platform=Platform.TIKTOK,
            num_clips=2
        )
        
        # Verify fallback was used
        agent._create_fallback_voice_config.assert_called_once()
        self.assertEqual(result['strategy'], 'single')
    
    @patch('src.agents.voice_director_agent.genai')
    def test_analyze_content_and_select_voices_success(self, mock_genai):
        """Test successful content analysis and voice selection"""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = '''
        {
            "strategy": "multiple",
            "primary_personality": "storyteller",
            "primary_gender": "female",
            "use_multiple_voices": true,
            "voice_changes_per_clip": true,
            "reasoning": "Multiple voices will create more engaging content",
            "clip_voice_plan": [
                {
                    "clip_index": 0,
                    "personality": "storyteller",
                    "gender": "female",
                    "emotion": "warm",
                    "pitch_adjustment": 0.5,
                    "speed_adjustment": 1.0,
                    "energy_level": "medium",
                    "content_focus": "introduction",
                    "reasoning": "Opening needs warm storytelling"
                },
                {
                    "clip_index": 1,
                    "personality": "enthusiast",
                    "gender": "male",
                    "emotion": "excited",
                    "pitch_adjustment": 1.0,
                    "speed_adjustment": 1.1,
                    "energy_level": "high",
                    "content_focus": "main_hook",
                    "reasoning": "Climax needs high energy"
                }
            ],
            "confidence_score": 0.85,
            "target_audience_analysis": "Young adults who enjoy dynamic content"
        }
        '''
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test content analysis
        result = agent.analyze_content_and_select_voices(
            topic="Funny cat video",
            script="A cat does something funny",
            language=Language.ENGLISH_US,
            platform=Platform.TIKTOK,
            category=VideoCategory.COMEDY,
            duration_seconds=10,
            num_clips=2
        )
        
        # Verify result
        self.assertEqual(result['strategy'], 'multiple')
        self.assertEqual(result['primary_personality'], 'storyteller')
        self.assertIn('voices', result)
        self.assertEqual(len(result['voices']), 2)
        
        # Verify API call
        self.mock_model.generate_content.assert_called_once()
    
    @patch('src.agents.voice_director_agent.genai')
    def test_analyze_content_and_select_voices_invalid_json(self, mock_genai):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        
        mock_genai.GenerativeModel.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Mock fallback method
        agent._create_fallback_voice_config = Mock(return_value={
            'voices': ['en-US-Neural2-C'],
            'strategy': 'single',
            'primary_personality': 'professional'
        })
        
        # Test with invalid JSON
        result = agent.analyze_content_and_select_voices(
            topic="Test topic",
            script="Test script",
            language=Language.ENGLISH_US,
            platform=Platform.TIKTOK,
            category=VideoCategory.COMEDY,
            duration_seconds=10,
            num_clips=1
        )
        
        # Should use fallback
        agent._create_fallback_voice_config.assert_called_once()
        self.assertEqual(result['strategy'], 'single')
    
    @patch('src.agents.voice_director_agent.genai')
    def test_select_voice_for_clip_success(self, mock_genai):
        """Test successful voice selection for clip"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test voice selection
        voice = agent._select_voice_for_clip(
            language=Language.ENGLISH_US,
            personality="storyteller",
            gender="female",
            emotion="warm"
        )
        
        # Verify voice selection
        self.assertIsInstance(voice, str)
        self.assertIn("en-US", voice)
    
    @patch('src.agents.voice_director_agent.genai')
    def test_select_voice_for_clip_fallback(self, mock_genai):
        """Test voice selection fallback"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test with unknown personality
        voice = agent._select_voice_for_clip(
            language=Language.ENGLISH_US,
            personality="unknown_personality",
            gender="female",
            emotion="neutral"
        )
        
        # Should fallback to narrator
        self.assertIsInstance(voice, str)
        self.assertIn("en-US", voice)
    
    @patch('src.agents.voice_director_agent.genai')
    def test_get_speed_for_emotion(self, mock_genai):
        """Test speed calculation for emotions"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test different emotions
        self.assertEqual(agent._get_speed_for_emotion("excited"), 1.1)
        self.assertEqual(agent._get_speed_for_emotion("calm"), 0.9)
        self.assertEqual(agent._get_speed_for_emotion("urgent"), 1.2)
        self.assertEqual(agent._get_speed_for_emotion("unknown"), 1.0)
    
    @patch('src.agents.voice_director_agent.genai')
    def test_get_pitch_for_emotion(self, mock_genai):
        """Test pitch calculation for emotions"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test different emotions
        self.assertEqual(agent._get_pitch_for_emotion("excited"), 2.0)
        self.assertEqual(agent._get_pitch_for_emotion("sad"), -2.0)
        self.assertEqual(agent._get_pitch_for_emotion("angry"), 1.0)
        self.assertEqual(agent._get_pitch_for_emotion("unknown"), 0.0)
    
    @patch('src.agents.voice_director_agent.genai')
    def test_create_fallback_voice_config(self, mock_genai):
        """Test fallback voice configuration creation"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test fallback config
        result = agent._create_fallback_voice_config(
            topic="Test topic",
            language=Language.ENGLISH_US,
            num_clips=3
        )
        
        # Verify fallback
        self.assertEqual(result['strategy'], 'single')
        self.assertEqual(result['primary_personality'], 'professional')
        self.assertEqual(len(result['voices']), 3)
        self.assertIn('reasoning', result)
        self.assertIn('fallback', result['reasoning'].lower())
    
    @patch('src.agents.voice_director_agent.genai')
    def test_convert_analysis_to_voices(self, mock_genai):
        """Test conversion of analysis to voice configuration"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        analysis = {
            'strategy': 'multiple',
            'primary_personality': 'storyteller',
            'primary_gender': 'female',
            'use_multiple_voices': True,
            'clip_voice_plan': [
                {
                    'clip_index': 0,
                    'personality': 'storyteller',
                    'gender': 'female',
                    'emotion': 'warm'
                },
                {
                    'clip_index': 1,
                    'personality': 'enthusiast',
                    'gender': 'male',
                    'emotion': 'excited'
                }
            ]
        }
        
        # Test conversion
        result = agent._convert_analysis_to_voices(analysis, Language.ENGLISH_US, 2)
        
        # Verify conversion
        self.assertEqual(result['strategy'], 'multiple')
        self.assertEqual(len(result['clip_voices']), 2)
        self.assertEqual(result['voice_variety'], True)
    
    @patch('src.agents.voice_director_agent.genai')
    def test_create_clip_voice_plan(self, mock_genai):
        """Test clip voice plan creation"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        analysis = {
            'strategy': 'single',
            'primary_personality': 'storyteller',
            'primary_gender': 'female'
        }
        
        # Test voice plan creation
        result = agent._create_clip_voice_plan(analysis, 1)
        
        # Verify plan
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['clip_index'], 0)
        self.assertEqual(result[0]['personality'], 'storyteller')
        self.assertEqual(result[0]['gender'], 'female')
        self.assertEqual(result[0]['emotion'], 'neutral')
    
    @patch('src.agents.voice_director_agent.genai')
    def test_voice_personality_enum(self, mock_genai):
        """Test VoicePersonality enum values"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Test enum values
        self.assertEqual(VoicePersonality.NARRATOR.value, "narrator")
        self.assertEqual(VoicePersonality.STORYTELLER.value, "storyteller")
        self.assertEqual(VoicePersonality.EDUCATOR.value, "educator")
        self.assertEqual(VoicePersonality.COMEDIAN.value, "comedian")
        self.assertEqual(VoicePersonality.DRAMATIC.value, "dramatic")
        self.assertEqual(VoicePersonality.YOUNG_ADULT.value, "young_adult")
        self.assertEqual(VoicePersonality.WISE.value, "wise")
        self.assertEqual(VoicePersonality.ENTHUSIAST.value, "enthusiast")
    
    @patch('src.agents.voice_director_agent.genai')
    def test_voice_gender_enum(self, mock_genai):
        """Test VoiceGender enum values"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Test enum values
        self.assertEqual(VoiceGender.MALE.value, "male")
        self.assertEqual(VoiceGender.FEMALE.value, "female")
        self.assertEqual(VoiceGender.MIXED.value, "mixed")
        self.assertEqual(VoiceGender.AUTO.value, "auto")
    
    @patch('src.agents.voice_director_agent.genai')
    def test_voice_database_structure(self, mock_genai):
        """Test voice database structure"""
        mock_genai.GenerativeModel.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test database structure
        self.assertIn(Language.ENGLISH_US, agent.voice_database)
        
        english_voices = agent.voice_database[Language.ENGLISH_US]
        self.assertIn(VoicePersonality.NARRATOR, english_voices)
        self.assertIn(VoicePersonality.STORYTELLER, english_voices)
        
        narrator_voices = english_voices[VoicePersonality.NARRATOR]
        self.assertIn("male", narrator_voices)
        self.assertIn("female", narrator_voices)
        
        # Verify voice names are strings
        for voice in narrator_voices["male"]:
            self.assertIsInstance(voice, str)
            self.assertIn("en-US", voice)


if __name__ == '__main__':
    unittest.main() 