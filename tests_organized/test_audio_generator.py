#!/usr/bin/env python3
"""
Unit tests for audio generator components
Tests verify that TTS and audio generation work correctly
"""

import unittest
import os
import sys
import tempfile
import wave
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.generators.enhanced_multilang_tts import EnhancedMultilingualTTS
from src.generators.google_tts_client import GoogleTTSClient
from src.models.video_models import Language
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class TestAudioGenerator(unittest.TestCase):
    """Test audio generation components"""

    def setUp(self):
        """Set up test environment"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        # Skip tests if no API key
        if not self.api_key:
            self.skipTest("No GOOGLE_API_KEY found")

    def test_enhanced_multilang_tts_initialization(self):
        """Test EnhancedMultiLangTTS initialization"""
        tts = EnhancedMultilingualTTS(api_key=self.api_key)
        
        # Verify initialization
        self.assertIsNotNone(tts.tts_client)
        self.assertIsNotNone(tts.voice_director)

    def test_google_tts_client_initialization(self):
        """Test GoogleTTSClient initialization"""
        client = GoogleTTSClient(api_key=self.api_key)
        
        # Verify initialization
        self.assertIsNotNone(client.client)
        self.assertEqual(client.api_key, self.api_key)

    def test_voice_selection_for_english(self):
        """Test voice selection for English language"""
        tts = EnhancedMultilingualTTS(api_key=self.api_key)
        
        text = "Hello, this is a test."
        voice_config = {
            'voice_name': 'en-US-Journey-F',
            'emotion': 'neutral',
            'speed': 1.0,
            'pitch': 0.0
        }
        
        # Mock the audio generation
        with patch.object(tts.tts_client, 'generate_audio') as mock_generate:
            mock_generate.return_value = '/tmp/test_audio.wav'
            
            result = tts.generate_audio(
                text=text,
                language=Language.ENGLISH_US,
                voice_config=voice_config
            )
            
            # Verify audio was generated
            mock_generate.assert_called_once()
            self.assertEqual(result, '/tmp/test_audio.wav')

    def test_voice_selection_for_hebrew(self):
        """Test voice selection for Hebrew language"""
        tts = EnhancedMultilingualTTS(api_key=self.api_key)
        
        text = "שלום, זה מבחן."
        voice_config = {
            'voice_name': 'he-IL-Wavenet-A',
            'emotion': 'neutral',
            'speed': 1.0,
            'pitch': 0.0
        }
        
        # Mock the audio generation
        with patch.object(tts.tts_client, 'generate_audio') as mock_generate:
            mock_generate.return_value = '/tmp/test_audio_hebrew.wav'
            
            result = tts.generate_audio(
                text=text,
                language=Language.HEBREW,
                voice_config=voice_config
            )
            
            # Verify audio was generated
            mock_generate.assert_called_once()
            self.assertEqual(result, '/tmp/test_audio_hebrew.wav')

    def test_voice_config_parameters(self):
        """Test that voice configuration parameters are applied correctly"""
        client = GoogleTTSClient(api_key=self.api_key)
        
        # Mock Google TTS client
        with patch('google.cloud.texttospeech.TextToSpeechClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Mock the synthesis response
            mock_response = MagicMock()
            mock_response.audio_content = b'fake_audio_data'
            mock_client.synthesize_speech.return_value = mock_response
            
            # Test with specific voice parameters
            result = client.generate_audio(
                text="Test text",
                voice_name="en-US-Journey-F",
                speaking_rate=1.2,
                pitch=0.5,
                volume_gain_db=2.0,
                output_file="/tmp/test_voice_params.wav"
            )
            
            # Verify the API was called with correct parameters
            mock_client.synthesize_speech.assert_called_once()
            call_args = mock_client.synthesize_speech.call_args[1]
            
            # Check voice parameters
            self.assertEqual(call_args['voice'].name, "en-US-Journey-F")
            self.assertEqual(call_args['audio_config'].speaking_rate, 1.2)
            self.assertEqual(call_args['audio_config'].pitch, 0.5)
            self.assertEqual(call_args['audio_config'].volume_gain_db, 2.0)
            
            # Verify file was created
            self.assertTrue(result.endswith('.wav'))

    def test_audio_file_format(self):
        """Test that generated audio is in correct format"""
        client = GoogleTTSClient(api_key=self.api_key)
        
        # Mock Google TTS client
        with patch('google.cloud.texttospeech.TextToSpeechClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Create mock audio content (minimal WAV header)
            wav_header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
            
            mock_response = MagicMock()
            mock_response.audio_content = wav_header
            mock_client.synthesize_speech.return_value = mock_response
            
            # Test audio generation
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                result = client.generate_audio(
                    text="Test audio format",
                    voice_name="en-US-Journey-F",
                    output_file=tmp_file.name
                )
                
                # Verify file exists and has content
                self.assertTrue(os.path.exists(result))
                self.assertGreater(os.path.getsize(result), 0)
                
                # Clean up
                os.unlink(result)

    def test_multilingual_support(self):
        """Test multilingual TTS support"""
        tts = EnhancedMultilingualTTS(api_key=self.api_key)
        
        test_cases = [
            (Language.ENGLISH_US, "Hello world", "en-US-Journey-F"),
            (Language.HEBREW, "שלום עולם", "he-IL-Wavenet-A"),
            (Language.ARABIC, "مرحبا بالعالم", "ar-XA-Wavenet-A"),
            (Language.FRENCH, "Bonjour le monde", "fr-FR-Wavenet-A"),
            (Language.SPANISH, "Hola mundo", "es-ES-Standard-A")
        ]
        
        for language, text, expected_voice in test_cases:
            with self.subTest(language=language):
                voice_config = {
                    'voice_name': expected_voice,
                    'emotion': 'neutral',
                    'speed': 1.0,
                    'pitch': 0.0
                }
                
                # Mock the audio generation
                with patch.object(tts.tts_client, 'generate_audio') as mock_generate:
                    mock_generate.return_value = f'/tmp/test_{language.value}.wav'
                    
                    result = tts.generate_audio(
                        text=text,
                        language=language,
                        voice_config=voice_config
                    )
                    
                    # Verify audio was generated
                    mock_generate.assert_called_once()
                    self.assertTrue(result.endswith('.wav'))

    def test_emotion_and_speed_modulation(self):
        """Test emotion and speed modulation in voice generation"""
        tts = EnhancedMultilingualTTS(api_key=self.api_key)
        
        text = "This is a test with emotions"
        
        emotion_configs = [
            {'emotion': 'excited', 'speed': 1.1, 'pitch': 2.0},
            {'emotion': 'calm', 'speed': 0.9, 'pitch': -0.5},
            {'emotion': 'neutral', 'speed': 1.0, 'pitch': 0.0}
        ]
        
        for config in emotion_configs:
            with self.subTest(emotion=config['emotion']):
                voice_config = {
                    'voice_name': 'en-US-Journey-F',
                    'emotion': config['emotion'],
                    'speed': config['speed'],
                    'pitch': config['pitch']
                }
                
                # Mock the audio generation
                with patch.object(tts.tts_client, 'generate_audio') as mock_generate:
                    mock_generate.return_value = f'/tmp/test_{config["emotion"]}.wav'
                    
                    result = tts.generate_audio(
                        text=text,
                        language=Language.ENGLISH_US,
                        voice_config=voice_config
                    )
                    
                    # Verify audio was generated with correct config
                    mock_generate.assert_called_once()
                    call_args = mock_generate.call_args[1]
                    
                    # Check that speed and pitch were applied
                    self.assertEqual(call_args['speaking_rate'], config['speed'])
                    self.assertEqual(call_args['pitch'], config['pitch'])

    @unittest.skipIf(os.getenv('SKIP_INTEGRATION_TESTS') == 'true', 
                     "Integration tests skipped")
    def test_real_audio_generation(self):
        """Integration test: Generate actual audio"""
        client = GoogleTTSClient(api_key=self.api_key)
        
        text = "This is a test of the audio generation system."
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                result = client.generate_audio(
                    text=text,
                    voice_name="en-US-Journey-F",
                    speaking_rate=1.0,
                    pitch=0.0,
                    output_file=tmp_file.name
                )
                
                # Verify file was created
                self.assertTrue(os.path.exists(result))
                self.assertGreater(os.path.getsize(result), 0)
                
                # Try to open as WAV file to verify format
                try:
                    with wave.open(result, 'rb') as wav_file:
                        # Basic WAV file checks
                        self.assertGreater(wav_file.getnframes(), 0)
                        self.assertGreater(wav_file.getframerate(), 0)
                        self.assertIn(wav_file.getnchannels(), [1, 2])
                        
                        logger.info(f"✅ Generated audio: {wav_file.getnframes()} frames, {wav_file.getframerate()} Hz")
                        
                except wave.Error:
                    logger.warning("Generated file is not a valid WAV file")
                    
                # Clean up
                os.unlink(result)
                
        except Exception as e:
            self.fail(f"Audio generation failed: {e}")

    def test_error_handling(self):
        """Test error handling in audio generation"""
        client = GoogleTTSClient(api_key=self.api_key)
        
        # Test with invalid voice name
        with self.assertRaises(Exception):
            client.generate_audio(
                text="Test text",
                voice_name="invalid-voice-name",
                output_file="/tmp/test_error.wav"
            )
            
        # Test with empty text
        with self.assertRaises(ValueError):
            client.generate_audio(
                text="",
                voice_name="en-US-Journey-F",
                output_file="/tmp/test_empty.wav"
            )

if __name__ == '__main__':
    unittest.main()