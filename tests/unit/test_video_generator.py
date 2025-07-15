"""
Comprehensive unit tests for VideoGenerator class
Tests all methods, edge cases, and error conditions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import tempfile
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.generators.video_generator import VideoGenerator, VideoGenerationResult
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory


class TestVideoGenerator(unittest.TestCase):
    """Comprehensive tests for VideoGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock all external dependencies
        self.mock_veo_factory = Mock()
        self.mock_voice_director = Mock()
        self.mock_positioning_agent = Mock()
        self.mock_style_agent = Mock()
        self.mock_script_processor = Mock()
        self.mock_image_client = Mock()
        self.mock_tts_client = Mock()
        
        # Create test config
        self.test_config = GeneratedVideoConfig(
            topic="Test video topic",
            duration_seconds=10,
            target_platform=Platform.TIKTOK,
            category=VideoCategory.COMEDY,
            session_id="test_session_123"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_init_success(self, mock_tts, mock_image, mock_script, mock_style, 
                         mock_positioning, mock_voice, mock_veo_factory):
        """Test successful initialization"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        
        # Create generator
        generator = VideoGenerator(
            api_key=self.api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            vertex_project_id="test_project",
            vertex_location="us-central1",
            output_dir=self.temp_dir
        )
        
        # Verify initialization
        self.assertEqual(generator.api_key, self.api_key)
        self.assertTrue(generator.use_real_veo2)
        self.assertTrue(generator.use_vertex_ai)
        self.assertEqual(generator.output_dir, self.temp_dir)
        
        # Verify all components are initialized
        mock_veo_factory.assert_called_once()
        mock_voice.assert_called_once_with(self.api_key)
        mock_positioning.assert_called_once_with(self.api_key)
        mock_style.assert_called_once_with(self.api_key)
        mock_script.assert_called_once_with(self.api_key)
        mock_image.assert_called_once_with(self.api_key, self.temp_dir)
        mock_tts.assert_called_once_with(self.api_key)
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_init_with_defaults(self, mock_tts, mock_image, mock_script, mock_style, 
                               mock_positioning, mock_voice, mock_veo_factory):
        """Test initialization with default parameters"""
        mock_veo_factory.return_value.get_available_models.return_value = []
        
        generator = VideoGenerator(api_key=self.api_key)
        
        self.assertEqual(generator.api_key, self.api_key)
        self.assertTrue(generator.use_real_veo2)
        self.assertTrue(generator.use_vertex_ai)
        self.assertEqual(generator.output_dir, "outputs")
        self.assertFalse(generator.prefer_veo3)
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    @patch('src.generators.video_generator.create_session_context')
    def test_generate_video_success(self, mock_session_context, mock_tts, mock_image, 
                                   mock_script, mock_style, mock_positioning, 
                                   mock_voice, mock_veo_factory):
        """Test successful video generation"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_session_context.return_value = Mock()
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        
        # Mock all internal methods
        generator._process_script_with_ai = Mock(return_value={'final_script': 'test script'})
        generator._get_visual_style_decision = Mock(return_value={'primary_style': 'cartoon'})
        generator._get_positioning_decision = Mock(return_value={'position': 'center'})
        generator._generate_video_clips = Mock(return_value=['clip1.mp4', 'clip2.mp4'])
        generator._generate_ai_optimized_audio = Mock(return_value=['audio1.wav'])
        generator._compose_final_video = Mock(return_value='final_video.mp4')
        generator._get_file_size_mb = Mock(return_value=5.2)
        
        # Test video generation
        result = generator.generate_video(self.test_config)
        
        # Verify result
        self.assertIsInstance(result, VideoGenerationResult)
        self.assertEqual(result.file_path, 'final_video.mp4')
        self.assertEqual(result.file_size_mb, 5.2)
        self.assertTrue(result.success)
        self.assertEqual(result.clips_generated, 2)
        self.assertEqual(result.audio_files, ['audio1.wav'])
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    @patch('src.generators.video_generator.create_session_context')
    def test_generate_video_failure(self, mock_session_context, mock_tts, mock_image, 
                                   mock_script, mock_style, mock_positioning, 
                                   mock_voice, mock_veo_factory):
        """Test video generation failure handling"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_session_context.return_value = Mock()
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        
        # Mock failure in script processing
        generator._process_script_with_ai = Mock(side_effect=Exception("Script processing failed"))
        
        # Test video generation
        result = generator.generate_video(self.test_config)
        
        # Verify failure handling
        self.assertIsInstance(result, VideoGenerationResult)
        self.assertFalse(result.success)
        self.assertIn("Script processing failed", result.error_message)
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_process_script_with_ai(self, mock_tts, mock_image, mock_script, mock_style, 
                                   mock_positioning, mock_voice, mock_veo_factory):
        """Test script processing with AI"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_script.return_value.process_script_for_tts.return_value = {
            'final_script': 'processed script',
            'segments': ['segment1', 'segment2']
        }
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        mock_session_context = Mock()
        
        # Test script processing
        result = generator._process_script_with_ai(self.test_config, mock_session_context)
        
        # Verify processing
        self.assertIn('final_script', result)
        self.assertEqual(result['final_script'], 'processed script')
        mock_script.return_value.process_script_for_tts.assert_called_once()
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_get_visual_style_decision(self, mock_tts, mock_image, mock_script, mock_style, 
                                      mock_positioning, mock_voice, mock_veo_factory):
        """Test visual style decision making"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_style.return_value.analyze_optimal_style.return_value = {
            'primary_style': 'cartoon',
            'color_palette': 'vibrant'
        }
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        
        # Test style decision
        result = generator._get_visual_style_decision(self.test_config)
        
        # Verify decision
        self.assertEqual(result['primary_style'], 'cartoon')
        self.assertEqual(result['color_palette'], 'vibrant')
        mock_style.return_value.analyze_optimal_style.assert_called_once()
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_get_positioning_decision(self, mock_tts, mock_image, mock_script, mock_style, 
                                     mock_positioning, mock_voice, mock_veo_factory):
        """Test positioning decision making"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_positioning.return_value.analyze_optimal_positioning.return_value = {
            'primary_subtitle_position': 'bottom_third',
            'strategy': 'static'
        }
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        style_decision = {'primary_style': 'cartoon'}
        
        # Test positioning decision
        result = generator._get_positioning_decision(self.test_config, style_decision)
        
        # Verify decision
        self.assertEqual(result['primary_subtitle_position'], 'bottom_third')
        self.assertEqual(result['strategy'], 'static')
        mock_positioning.return_value.analyze_optimal_positioning.assert_called_once()
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_get_ai_voice_config(self, mock_tts, mock_image, mock_script, mock_style, 
                                mock_positioning, mock_voice, mock_veo_factory):
        """Test AI voice configuration"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_voice.return_value.get_voice_config.return_value = {
            'voices': ['en-US-Neural2-C', 'en-US-Neural2-D'],
            'strategy': 'multiple'
        }
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        script_result = {'final_script': 'test script'}
        
        # Test voice config
        result = generator._get_ai_voice_config(self.test_config, script_result, 2)
        
        # Verify config
        self.assertEqual(len(result['voices']), 2)
        self.assertEqual(result['strategy'], 'multiple')
        mock_voice.return_value.get_voice_config.assert_called_once()
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_get_ai_voice_config_fallback(self, mock_tts, mock_image, mock_script, mock_style, 
                                         mock_positioning, mock_voice, mock_veo_factory):
        """Test AI voice configuration fallback"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        # Remove voice director to test fallback
        generator.voice_director = None
        script_result = {'final_script': 'test script'}
        
        # Test voice config fallback
        result = generator._get_ai_voice_config(self.test_config, script_result, 2)
        
        # Verify fallback
        self.assertEqual(len(result['voices']), 2)
        self.assertEqual(result['strategy'], 'single')
        self.assertEqual(result['primary_personality'], 'professional')
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    @patch('src.generators.video_generator.os.path.getsize')
    def test_get_file_size_mb(self, mock_getsize, mock_tts, mock_image, mock_script, 
                             mock_style, mock_positioning, mock_voice, mock_veo_factory):
        """Test file size calculation"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_getsize.return_value = 5242880  # 5MB in bytes
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        
        # Test file size calculation
        result = generator._get_file_size_mb("test_file.mp4")
        
        # Verify calculation
        self.assertEqual(result, 5.0)
        mock_getsize.assert_called_once_with("test_file.mp4")
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    @patch('src.generators.video_generator.os.path.getsize')
    def test_get_file_size_mb_error(self, mock_getsize, mock_tts, mock_image, mock_script, 
                                   mock_style, mock_positioning, mock_voice, mock_veo_factory):
        """Test file size calculation error handling"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        mock_getsize.side_effect = OSError("File not found")
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        
        # Test file size calculation with error
        result = generator._get_file_size_mb("nonexistent_file.mp4")
        
        # Verify error handling
        self.assertEqual(result, 0.0)
        mock_getsize.assert_called_once_with("nonexistent_file.mp4")
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_add_aligned_subtitle_overlays(self, mock_tts, mock_image, mock_script, mock_style, 
                                          mock_positioning, mock_voice, mock_veo_factory):
        """Test aligned subtitle overlays"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        generator._add_subtitle_overlays = Mock(return_value="video_with_subtitles.mp4")
        
        mock_session_context = Mock()
        
        # Test aligned subtitle overlays
        result = generator._add_aligned_subtitle_overlays(
            "input_video.mp4", self.test_config, mock_session_context
        )
        
        # Verify result
        self.assertEqual(result, "video_with_subtitles.mp4")
        generator._add_subtitle_overlays.assert_called_once_with(
            "input_video.mp4", self.test_config, mock_session_context
        )
    
    @patch('src.generators.video_generator.VeoClientFactory')
    @patch('src.generators.video_generator.VoiceDirectorAgent')
    @patch('src.generators.video_generator.OverlayPositioningAgent')
    @patch('src.generators.video_generator.VisualStyleAgent')
    @patch('src.generators.video_generator.EnhancedScriptProcessor')
    @patch('src.generators.video_generator.GeminiImageClient')
    @patch('src.generators.video_generator.EnhancedMultilingualTTS')
    def test_add_aligned_subtitle_overlays_error(self, mock_tts, mock_image, mock_script, 
                                                mock_style, mock_positioning, mock_voice, 
                                                mock_veo_factory):
        """Test aligned subtitle overlays error handling"""
        # Setup mocks
        mock_veo_factory.return_value.get_available_models.return_value = ['veo-2.0-generate-001']
        
        generator = VideoGenerator(api_key=self.api_key, output_dir=self.temp_dir)
        generator._add_subtitle_overlays = Mock(side_effect=Exception("Subtitle error"))
        
        mock_session_context = Mock()
        
        # Test aligned subtitle overlays with error
        result = generator._add_aligned_subtitle_overlays(
            "input_video.mp4", self.test_config, mock_session_context
        )
        
        # Verify error handling
        self.assertEqual(result, "input_video.mp4")


if __name__ == '__main__':
    unittest.main() 