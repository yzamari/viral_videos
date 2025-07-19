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
        
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_init_success(self, mock_genai_model):
        """Test successful initialization"""
        mock_genai_model.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        self.assertEqual(agent.api_key, self.api_key)
        self.assertEqual(agent.model, self.mock_model)
        mock_genai_model.assert_called_once_with('gemini-2.5-flash')
        
        # Verify voice database is initialized
        self.assertIn(Language.ENGLISH_US, agent.voice_database)
        self.assertIn(VoicePersonality.NARRATOR, agent.voice_database[Language.ENGLISH_US])
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_get_voice_config_success(self, mock_genai_model):
        """Test successful voice configuration"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_get_voice_config_fallback(self, mock_genai_model):
        """Test voice configuration fallback"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_get_voice_config_exception(self, mock_genai_model):
        """Test voice configuration exception handling"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_analyze_content_and_select_voices_success(self, mock_genai_model):
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
        
        mock_genai_model.return_value = self.mock_model
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_analyze_content_and_select_voices_invalid_json(self, mock_genai_model):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        
        mock_genai_model.return_value = self.mock_model
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_select_voice_for_clip_success(self, mock_genai_model):
        """Test successful voice selection for clip"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_select_voice_for_clip_fallback(self, mock_genai_model):
        """Test voice selection fallback"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_get_speed_for_emotion(self, mock_genai_model):
        """Test speed calculation for emotions"""
        mock_genai_model.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test different emotions
        self.assertEqual(agent._get_speed_for_emotion("excited"), 1.1)
        self.assertEqual(agent._get_speed_for_emotion("calm"), 0.9)
        self.assertEqual(agent._get_speed_for_emotion("urgent"), 1.2)
        self.assertEqual(agent._get_speed_for_emotion("unknown"), 1.0)
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_get_pitch_for_emotion(self, mock_genai_model):
        """Test pitch calculation for emotions"""
        mock_genai_model.return_value = self.mock_model
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test different emotions
        self.assertEqual(agent._get_pitch_for_emotion("excited"), 2.0)
        self.assertEqual(agent._get_pitch_for_emotion("sad"), -2.0)
        self.assertEqual(agent._get_pitch_for_emotion("angry"), 1.0)
        self.assertEqual(agent._get_pitch_for_emotion("unknown"), 0.0)
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_create_fallback_voice_config(self, mock_genai_model):
        """Test fallback voice configuration creation"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_convert_analysis_to_voices(self, mock_genai_model):
        """Test conversion of analysis to voice configuration"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_create_clip_voice_plan(self, mock_genai_model):
        """Test clip voice plan creation"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_voice_personality_enum(self, mock_genai_model):
        """Test VoicePersonality enum values"""
        mock_genai_model.return_value = self.mock_model
        
        # Test enum values
        self.assertEqual(VoicePersonality.NARRATOR.value, "narrator")
        self.assertEqual(VoicePersonality.STORYTELLER.value, "storyteller")
        self.assertEqual(VoicePersonality.EDUCATOR.value, "educator")
        self.assertEqual(VoicePersonality.COMEDIAN.value, "comedian")
        self.assertEqual(VoicePersonality.DRAMATIC.value, "dramatic")
        self.assertEqual(VoicePersonality.YOUNG_ADULT.value, "young_adult")
        self.assertEqual(VoicePersonality.WISE.value, "wise")
        self.assertEqual(VoicePersonality.ENTHUSIAST.value, "enthusiast")
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_voice_gender_enum(self, mock_genai_model):
        """Test VoiceGender enum values"""
        mock_genai_model.return_value = self.mock_model
        
        # Test enum values
        self.assertEqual(VoiceGender.MALE.value, "male")
        self.assertEqual(VoiceGender.FEMALE.value, "female")
        self.assertEqual(VoiceGender.MIXED.value, "mixed")
        self.assertEqual(VoiceGender.AUTO.value, "auto")
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_voice_database_structure(self, mock_genai_model):
        """Test voice database structure"""
        mock_genai_model.return_value = self.mock_model
        
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
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_single_voice_preference(self, mock_genai_model):
        """Test single voice preference for professional content"""
        mock_response = Mock()
        mock_response.text = '''
        {
            "strategy": "single",
            "has_distinct_speakers": false,
            "speaker_count": 1,
            "primary_personality": "narrator",
            "primary_gender": "female",
            "use_multiple_voices": false,
            "voice_changes_per_clip": false,
            "reasoning": "Single voice preferred for professional content consistency",
            "clip_voice_plan": [
                {
                    "clip_index": 0,
                    "personality": "narrator",
                    "gender": "female",
                    "emotion": "neutral",
                    "speaker_id": "main"
                },
                {
                    "clip_index": 1,
                    "personality": "narrator",
                    "gender": "female",
                    "emotion": "neutral",
                    "speaker_id": "main"
                }
            ]
        }
        '''
        
        mock_genai_model.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test single voice preference
        result = agent.analyze_content_and_select_voices(
            topic="Professional business presentation",
            script="Welcome to our quarterly review. Today we'll discuss achievements and future plans.",
            language=Language.ENGLISH_US,
            platform=Platform.INSTAGRAM,
            category=VideoCategory.BUSINESS,
            duration_seconds=30,
            num_clips=2
        )
        
        # Verify single voice strategy
        self.assertEqual(result['strategy'], 'single')
        self.assertFalse(result['voice_variety'])
        
        # Verify all clips use the same voice
        clip_voices = result['clip_voices']
        self.assertEqual(len(clip_voices), 2)
        
        # All clips should use the same voice name
        voice_names = [voice['voice_name'] for voice in clip_voices]
        self.assertEqual(len(set(voice_names)), 1)  # Only one unique voice
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_multiple_speakers_detection(self, mock_genai_model):
        """Test detection of multiple speakers for dialogue content"""
        mock_response = Mock()
        mock_response.text = '''
        {
            "strategy": "multiple_speakers",
            "has_distinct_speakers": true,
            "speaker_count": 2,
            "primary_personality": "narrator",
            "primary_gender": "mixed",
            "use_multiple_voices": true,
            "voice_changes_per_clip": false,
            "reasoning": "Content contains distinct speakers in dialogue format",
            "clip_voice_plan": [
                {
                    "clip_index": 0,
                    "personality": "narrator",
                    "gender": "male",
                    "emotion": "conversational",
                    "speaker_id": "speaker_0"
                },
                {
                    "clip_index": 1,
                    "personality": "narrator",
                    "gender": "female",
                    "emotion": "conversational",
                    "speaker_id": "speaker_1"
                }
            ]
        }
        '''
        
        mock_genai_model.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test multiple speakers detection
        result = agent.analyze_content_and_select_voices(
            topic="Doctor patient consultation",
            script="Dr. Smith: How are you feeling today? Patient: I've been experiencing some discomfort.",
            language=Language.ENGLISH_US,
            platform=Platform.INSTAGRAM,
            category=VideoCategory.HEALTH,
            duration_seconds=20,
            num_clips=2
        )
        
        # Verify multiple speakers strategy
        self.assertEqual(result['strategy'], 'multiple_speakers')
        self.assertTrue(result['voice_variety'])
        
        # Verify different voices for different speakers
        clip_voices = result['clip_voices']
        self.assertEqual(len(clip_voices), 2)
        
        # Should have different voice names for different speakers
        voice_names = [voice['voice_name'] for voice in clip_voices]
        self.assertEqual(len(set(voice_names)), 2)  # Two unique voices
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_voice_boundary_protection(self, mock_genai_model):
        """Test that voice changes only happen at appropriate boundaries"""
        mock_response = Mock()
        mock_response.text = '''
        {
            "strategy": "single",
            "has_distinct_speakers": false,
            "speaker_count": 1,
            "primary_personality": "narrator",
            "primary_gender": "female",
            "use_multiple_voices": false,
            "voice_changes_per_clip": false,
            "reasoning": "Single voice ensures no mid-sentence voice changes",
            "clip_voice_plan": [
                {
                    "clip_index": 0,
                    "personality": "narrator",
                    "gender": "female",
                    "emotion": "neutral",
                    "speaker_id": "main"
                }
            ]
        }
        '''
        
        mock_genai_model.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test voice boundary protection
        result = agent.analyze_content_and_select_voices(
            topic="Continuous narrative",
            script="This is a continuous story that should maintain the same voice throughout to avoid jarring transitions.",
            language=Language.ENGLISH_US,
            platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATION,
            duration_seconds=15,
            num_clips=1
        )
        
        # Verify no voice changes per clip
        self.assertFalse(result.get('voice_changes_per_clip', True))
        
        # Verify reasoning mentions boundary protection
        reasoning = result.get('reasoning', '').lower()
        self.assertIn('single', reasoning)
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_context_aware_voice_selection(self, mock_genai_model):
        """Test that voice selection is context-aware for content type"""
        mock_response = Mock()
        mock_response.text = '''
        {
            "strategy": "single",
            "has_distinct_speakers": false,
            "speaker_count": 1,
            "primary_personality": "educator",
            "primary_gender": "female",
            "use_multiple_voices": false,
            "voice_changes_per_clip": false,
            "reasoning": "Educational content requires clear, authoritative voice",
            "clip_voice_plan": [
                {
                    "clip_index": 0,
                    "personality": "educator",
                    "gender": "female",
                    "emotion": "neutral",
                    "speaker_id": "main"
                }
            ]
        }
        '''
        
        mock_genai_model.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test context-aware selection for educational content
        result = agent.analyze_content_and_select_voices(
            topic="Science education",
            script="Today we'll learn about photosynthesis and how plants convert sunlight into energy.",
            language=Language.ENGLISH_US,
            platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATION,
            duration_seconds=45,
            num_clips=1
        )
        
        # Verify appropriate personality selection
        clip_voices = result['clip_voices']
        self.assertEqual(clip_voices[0]['personality'], 'educator')
        
        # Verify reasoning mentions educational context
        reasoning = result.get('reasoning', '').lower()
        self.assertIn('educational', reasoning)
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_fallback_to_single_voice(self, mock_genai_model):
        """Test fallback to single voice when analysis fails"""
        mock_genai_model.return_value = self.mock_model
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test fallback behavior
        result = agent.analyze_content_and_select_voices(
            topic="Fallback test",
            script="This should fallback to single voice when API fails",
            language=Language.ENGLISH_US,
            platform=Platform.INSTAGRAM,
            category=VideoCategory.ENTERTAINMENT,
            duration_seconds=20,
            num_clips=2
        )
        
        # Verify fallback to single voice
        self.assertEqual(result['strategy'], 'single')
        self.assertFalse(result['voice_variety'])
        
        # Verify reasoning mentions fallback
        reasoning = result.get('reasoning', '').lower()
        self.assertIn('fallback', reasoning)
    
    @patch('src.agents.voice_director_agent.genai_available', True)
    @patch('src.agents.voice_director_agent.GenerativeModel')
    def test_speaker_id_consistency(self, mock_genai_model):
        """Test that speaker IDs are consistent for same speakers"""
        mock_response = Mock()
        mock_response.text = '''
        {
            "strategy": "multiple_speakers",
            "has_distinct_speakers": true,
            "speaker_count": 2,
            "primary_personality": "narrator",
            "primary_gender": "mixed",
            "use_multiple_voices": true,
            "voice_changes_per_clip": false,
            "reasoning": "Two distinct speakers require different voices",
            "clip_voice_plan": [
                {
                    "clip_index": 0,
                    "personality": "narrator",
                    "gender": "male",
                    "emotion": "conversational",
                    "speaker_id": "speaker_0"
                },
                {
                    "clip_index": 1,
                    "personality": "narrator",
                    "gender": "female",
                    "emotion": "conversational",
                    "speaker_id": "speaker_1"
                },
                {
                    "clip_index": 2,
                    "personality": "narrator",
                    "gender": "male",
                    "emotion": "conversational",
                    "speaker_id": "speaker_0"
                }
            ]
        }
        '''
        
        mock_genai_model.return_value = self.mock_model
        self.mock_model.generate_content.return_value = mock_response
        
        agent = VoiceDirectorAgent(self.api_key)
        
        # Test speaker consistency
        result = agent.analyze_content_and_select_voices(
            topic="Multi-speaker conversation",
            script="A: Hello. B: Hi there. A: How are you?",
            language=Language.ENGLISH_US,
            platform=Platform.INSTAGRAM,
            category=VideoCategory.ENTERTAINMENT,
            duration_seconds=15,
            num_clips=3
        )
        
        # Verify speaker consistency
        clip_voices = result['clip_voices']
        self.assertEqual(len(clip_voices), 3)
        
        # Clips 0 and 2 should have the same voice (same speaker)
        self.assertEqual(clip_voices[0]['voice_name'], clip_voices[2]['voice_name'])
        
        # Clip 1 should have a different voice
        self.assertNotEqual(clip_voices[0]['voice_name'], clip_voices[1]['voice_name'])


if __name__ == '__main__':
    unittest.main()