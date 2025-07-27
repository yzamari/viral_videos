"""
Tests for Video Fallback System
Ensures hierarchical fallback (VEO → Image → Color) works correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import os
from pathlib import Path
import tempfile
import shutil

from src.generators.video_generator import VideoGenerator
from src.core.entities import CoreDecisions, GeneratedVideoConfig


class TestVideoFallbackSystem:
    """Test suite for video generation fallback mechanism"""
    
    @pytest.fixture
    def mock_decisions(self):
        """Create mock CoreDecisions"""
        config = GeneratedVideoConfig(
            topic="Test video",
            duration=10,
            platform="youtube",
            language="en"
        )
        
        decisions = CoreDecisions(
            video_config=config,
            mission="Create test video",
            target_platform="youtube",
            language="en",
            duration=10
        )
        
        # Add required attributes
        decisions.visual_style = "modern"
        decisions.cheap_mode_level = None  # Not in cheap mode
        
        return decisions
    
    @pytest.fixture
    def mock_veo_factory(self):
        """Mock VEO client factory"""
        with patch('src.generators.video_generator.VeoClientFactory') as mock_factory:
            yield mock_factory
    
    @pytest.fixture
    def mock_gemini_client(self):
        """Mock Gemini image client"""
        with patch('src.generators.video_generator.GeminiImageClient') as mock_client:
            instance = Mock()
            mock_client.return_value = instance
            yield instance
    
    @pytest.fixture
    def video_generator(self, mock_decisions, mock_session_context, mock_veo_factory, mock_gemini_client):
        """Create VideoGenerator instance"""
        return VideoGenerator(mock_decisions, mock_session_context)
    
    @pytest.mark.unit
    def test_veo_success_no_fallback(self, video_generator, mock_veo_factory, temp_dir):
        """Test successful VEO generation without needing fallback"""
        # Setup mock VEO client
        mock_veo_client = Mock()
        mock_veo_client.generate_video.return_value = os.path.join(temp_dir, "veo_video.mp4")
        mock_veo_factory.get_client.return_value = mock_veo_client
        
        # Create fake video file
        video_path = os.path.join(temp_dir, "veo_video.mp4")
        Path(video_path).touch()
        
        # Test
        prompt = "A beautiful landscape"
        result = video_generator._generate_single_clip(prompt, "test_clip.mp4", 5)
        
        # Assert VEO was used and no fallback
        assert result == video_path
        mock_veo_client.generate_video.assert_called_once()
        # Gemini should not be called
        assert video_generator.gemini_client.generate_image.call_count == 0
    
    @pytest.mark.unit
    def test_veo_fails_fallback_to_image(self, video_generator, mock_veo_factory, mock_gemini_client, temp_dir):
        """Test fallback to image generation when VEO fails"""
        # Setup VEO to fail
        mock_veo_client = Mock()
        mock_veo_client.generate_video.side_effect = Exception("VEO generation failed")
        mock_veo_factory.get_client.return_value = mock_veo_client
        
        # Setup Gemini to succeed
        mock_gemini_client.generate_image.return_value = b'fake_image_data'
        
        # Mock image to video conversion
        with patch.object(video_generator, '_convert_image_to_video') as mock_convert:
            output_path = os.path.join(temp_dir, "fallback_video.mp4")
            Path(output_path).touch()
            mock_convert.return_value = output_path
            
            # Test
            prompt = "A scene that fails VEO"
            result = video_generator._generate_single_clip(prompt, "test_clip.mp4", 5)
            
            # Assert fallback occurred
            assert result == output_path
            mock_veo_client.generate_video.assert_called_once()
            mock_gemini_client.generate_image.assert_called_once_with(prompt)
            mock_convert.assert_called_once()
    
    @pytest.mark.unit
    def test_both_fail_fallback_to_color(self, video_generator, mock_veo_factory, mock_gemini_client, temp_dir):
        """Test fallback to solid color when both VEO and image generation fail"""
        # Setup both to fail
        mock_veo_client = Mock()
        mock_veo_client.generate_video.side_effect = Exception("VEO failed")
        mock_veo_factory.get_client.return_value = mock_veo_client
        
        mock_gemini_client.generate_image.side_effect = Exception("Gemini failed")
        
        # Mock color video generation
        with patch.object(video_generator, '_generate_color_video') as mock_color:
            output_path = os.path.join(temp_dir, "color_video.mp4")
            Path(output_path).touch()
            mock_color.return_value = output_path
            
            # Test
            prompt = "A scene that fails everything"
            result = video_generator._generate_single_clip(prompt, "test_clip.mp4", 5)
            
            # Assert double fallback occurred
            assert result == output_path
            mock_veo_client.generate_video.assert_called_once()
            mock_gemini_client.generate_image.assert_called_once()
            mock_color.assert_called_once()
    
    @pytest.mark.unit
    def test_fallback_chain_logging(self, video_generator, mock_veo_factory, mock_gemini_client, capture_logs):
        """Test that fallback chain is properly logged"""
        # Setup cascading failures
        mock_veo_client = Mock()
        mock_veo_client.generate_video.side_effect = Exception("VEO error")
        mock_veo_factory.get_client.return_value = mock_veo_client
        
        mock_gemini_client.generate_image.side_effect = Exception("Gemini error")
        
        with patch.object(video_generator, '_generate_color_video', return_value="color.mp4"):
            video_generator._generate_single_clip("test", "out.mp4", 5)
            
            # Check logs
            logs = capture_logs.getvalue()
            assert "VEO generation failed" in logs
            assert "Falling back to image generation" in logs
            assert "Image generation failed" in logs
            assert "Falling back to color video" in logs
    
    @pytest.mark.unit
    def test_cheap_mode_skips_veo(self, video_generator, mock_veo_factory, mock_gemini_client):
        """Test that cheap mode skips VEO and goes directly to image generation"""
        # Enable cheap mode
        video_generator.decisions.cheap_mode_level = "full"
        
        # Setup Gemini
        mock_gemini_client.generate_image.return_value = b'fake_image'
        
        with patch.object(video_generator, '_convert_image_to_video', return_value="image_video.mp4"):
            result = video_generator._generate_single_clip("test", "out.mp4", 5)
            
            # VEO should not be called in cheap mode
            mock_veo_factory.get_client.assert_not_called()
            # Should go directly to image generation
            mock_gemini_client.generate_image.assert_called_once()
    
    @pytest.mark.unit
    def test_platform_specific_fallback(self, video_generator, mock_veo_factory):
        """Test platform-specific fallback behavior"""
        platforms = ["youtube", "instagram", "tiktok"]
        
        for platform in platforms:
            video_generator.decisions.target_platform = platform
            
            # Mock VEO client with platform-specific settings
            mock_veo_client = Mock()
            mock_veo_factory.get_client.return_value = mock_veo_client
            
            # Test aspect ratio is set correctly based on platform
            video_generator._generate_single_clip("test", "out.mp4", 5)
            
            # Verify platform-specific parameters were used
            call_args = mock_veo_client.generate_video.call_args
            if platform in ["instagram", "tiktok"]:
                assert call_args[1].get('aspect_ratio') == "9:16"  # Vertical
            else:
                assert call_args[1].get('aspect_ratio') == "16:9"  # Horizontal
    
    @pytest.mark.unit
    def test_fallback_preserves_duration(self, video_generator, mock_veo_factory, mock_gemini_client):
        """Test that video duration is preserved through fallback chain"""
        target_duration = 7.5
        
        # Setup VEO to fail
        mock_veo_client = Mock()
        mock_veo_client.generate_video.side_effect = Exception("VEO failed")
        mock_veo_factory.get_client.return_value = mock_veo_client
        
        # Mock image to video conversion
        with patch.object(video_generator, '_convert_image_to_video') as mock_convert:
            mock_convert.return_value = "fallback.mp4"
            mock_gemini_client.generate_image.return_value = b'image'
            
            video_generator._generate_single_clip("test", "out.mp4", target_duration)
            
            # Verify duration was passed correctly
            mock_convert.assert_called_once()
            assert mock_convert.call_args[0][2] == target_duration  # duration parameter
    
    @pytest.mark.unit
    def test_fallback_with_reference_image(self, video_generator, mock_veo_factory):
        """Test fallback behavior when reference image is provided"""
        reference_image = "reference.jpg"
        
        mock_veo_client = Mock()
        mock_veo_client.generate_video.return_value = "video.mp4"
        mock_veo_factory.get_client.return_value = mock_veo_client
        
        # Test with reference image
        video_generator._generate_single_clip(
            "test prompt", 
            "out.mp4", 
            5,
            reference_image=reference_image
        )
        
        # Verify reference image was passed to VEO
        call_args = mock_veo_client.generate_video.call_args
        assert call_args[1].get('reference_image_path') == reference_image
    
    @pytest.mark.unit
    def test_error_recovery_in_batch(self, video_generator, mock_veo_factory, mock_gemini_client):
        """Test error recovery when generating multiple clips"""
        clips_data = [
            {"prompt": "Clip 1", "duration": 5},
            {"prompt": "Clip 2", "duration": 5},  # This will fail
            {"prompt": "Clip 3", "duration": 5}
        ]
        
        # Setup mixed success/failure
        mock_veo_client = Mock()
        mock_veo_client.generate_video.side_effect = [
            "clip1.mp4",
            Exception("VEO failed for clip 2"),
            "clip3.mp4"
        ]
        mock_veo_factory.get_client.return_value = mock_veo_client
        
        # Setup image fallback for failed clip
        mock_gemini_client.generate_image.return_value = b'fallback_image'
        
        with patch.object(video_generator, '_convert_image_to_video', return_value="clip2_fallback.mp4"):
            results = []
            for i, clip in enumerate(clips_data):
                result = video_generator._generate_single_clip(
                    clip["prompt"], 
                    f"clip_{i}.mp4", 
                    clip["duration"]
                )
                results.append(result)
            
            # Verify mixed results
            assert results[0] == "clip1.mp4"  # VEO success
            assert results[1] == "clip2_fallback.mp4"  # Fallback success
            assert results[2] == "clip3.mp4"  # VEO success
    
    @pytest.mark.integration
    def test_full_fallback_integration(self, temp_dir):
        """Integration test of complete fallback system"""
        # Create real instances with mocked external dependencies
        config = GeneratedVideoConfig(
            topic="Integration test",
            duration=5,
            platform="youtube",
            language="en"
        )
        
        decisions = CoreDecisions(
            video_config=config,
            mission="Test fallback",
            target_platform="youtube",
            language="en",
            duration=5
        )
        decisions.visual_style = "test"
        decisions.cheap_mode_level = None
        
        # Create session context
        session_context = Mock()
        session_context.get_session_path.return_value = Path(temp_dir)
        
        # Test with all mocked external services
        with patch('src.generators.video_generator.VeoClientFactory') as mock_factory:
            with patch('src.generators.video_generator.GeminiImageClient') as mock_gemini:
                # Setup complete failure chain
                mock_veo = Mock()
                mock_veo.generate_video.side_effect = Exception("VEO failed")
                mock_factory.get_client.return_value = mock_veo
                
                mock_gemini_instance = Mock()
                mock_gemini_instance.generate_image.side_effect = Exception("Gemini failed")
                mock_gemini.return_value = mock_gemini_instance
                
                # Create generator
                generator = VideoGenerator(decisions, session_context)
                
                # Should fallback to color video
                with patch('subprocess.run') as mock_subprocess:
                    mock_subprocess.return_value = Mock(returncode=0)
                    
                    result = generator._generate_single_clip("test", "final.mp4", 5)
                    
                    # Verify ffmpeg was called for color video
                    assert mock_subprocess.called
                    ffmpeg_args = mock_subprocess.call_args[0][0]
                    assert "ffmpeg" in ffmpeg_args[0]
                    assert "color=c=blue" in " ".join(ffmpeg_args)  # Color filter