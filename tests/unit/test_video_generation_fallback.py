"""
Unit tests for Video Generation Fallback System
Tests the robust fallback chain for video generation
"""

import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from moviepy.editor import ColorClip

from src.generators.video_generation_fallback import (
    VideoGenerationFallback, FallbackResult
)
from src.models.video_models import GeneratedVideoConfig, Platform


class TestVideoGenerationFallback:
    """Test suite for VideoGenerationFallback"""
    
    @pytest.fixture
    def mock_veo_client(self):
        """Create mock VEO client"""
        client = Mock()
        client.generate_video = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_image_client(self):
        """Create mock image client"""
        client = Mock()
        client.generate_image = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_config(self):
        """Create mock video generation config"""
        config = Mock(spec=GeneratedVideoConfig)
        config.target_platform = Platform.YOUTUBE
        config.duration_seconds = 10
        config.visual_style = "dynamic"
        config.fallback_only = False
        return config
    
    @pytest.fixture
    def fallback_system(self, mock_veo_client, mock_image_client):
        """Create VideoGenerationFallback instance"""
        return VideoGenerationFallback(
            veo_client=mock_veo_client,
            image_client=mock_image_client,
            api_key="test_key"
        )
    
    @pytest.mark.asyncio
    async def test_successful_veo_generation(self, fallback_system, mock_config):
        """Test successful VEO generation on first attempt"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            temp_path = tmp.name
        
        # Mock successful VEO generation
        fallback_system.veo_client.generate_video.return_value = temp_path
        
        # Create output path
        output_path = "/tmp/test_output.mp4"
        
        with patch('os.path.exists', return_value=True):
            with patch('os.rename'):
                result = await fallback_system.generate_with_fallback(
                    prompt="Test prompt",
                    duration=10.0,
                    config=mock_config,
                    output_path=output_path
                )
        
        assert result.success is True
        assert result.method_used == "veo"
        assert result.attempts == 1
        
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass
    
    @pytest.mark.asyncio
    async def test_veo_fails_image_succeeds(self, fallback_system, mock_config):
        """Test fallback to image generation when VEO fails"""
        # Mock VEO failure
        fallback_system.veo_client.generate_video.side_effect = Exception("VEO failed")
        
        # Mock successful image generation
        fallback_system.image_client.generate_image.return_value = {
            'path': '/tmp/test_image.png'
        }
        
        output_path = "/tmp/test_output.mp4"
        
        with patch('os.path.exists', return_value=True):
            with patch.object(fallback_system, '_create_video_from_images', 
                            return_value=True):
                result = await fallback_system.generate_with_fallback(
                    prompt="Test prompt",
                    duration=5.0,
                    config=mock_config,
                    output_path=output_path
                )
        
        assert result.success is True
        assert result.method_used == "image_sequence"
        assert result.attempts == 3  # 2 VEO attempts + 1 image attempt
    
    @pytest.mark.asyncio
    async def test_all_fail_color_fallback(self, fallback_system, mock_config):
        """Test color fallback when all other methods fail"""
        # Mock all failures
        fallback_system.veo_client.generate_video.side_effect = Exception("VEO failed")
        fallback_system.image_client.generate_image.side_effect = Exception("Image failed")
        
        output_path = "/tmp/test_output.mp4"
        
        with patch.object(fallback_system, '_generate_color_fallback', 
                         return_value=True) as mock_color:
            result = await fallback_system.generate_with_fallback(
                prompt="Test prompt",
                duration=5.0,
                config=mock_config,
                output_path=output_path
            )
        
        assert result.success is True
        assert result.method_used == "color_fallback"
        assert result.attempts == 5
        mock_color.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fallback_only_mode(self, fallback_system, mock_config):
        """Test that VEO is skipped when fallback_only is True"""
        mock_config.fallback_only = True
        
        # Mock successful image generation
        fallback_system.image_client.generate_image.return_value = {
            'path': '/tmp/test_image.png'
        }
        
        output_path = "/tmp/test_output.mp4"
        
        with patch('os.path.exists', return_value=True):
            with patch.object(fallback_system, '_create_video_from_images', 
                            return_value=True):
                result = await fallback_system.generate_with_fallback(
                    prompt="Test prompt",
                    duration=5.0,
                    config=mock_config,
                    output_path=output_path
                )
        
        # VEO should not have been called
        fallback_system.veo_client.generate_video.assert_not_called()
        assert result.method_used == "image_sequence"
    
    def test_aspect_ratio_detection(self, fallback_system, mock_config):
        """Test correct aspect ratio detection for platforms"""
        # YouTube should be 16:9
        mock_config.target_platform = Platform.YOUTUBE
        assert fallback_system._get_aspect_ratio(mock_config) == "16:9"
        
        # TikTok should be 9:16
        mock_config.target_platform = Platform.TIKTOK
        assert fallback_system._get_aspect_ratio(mock_config) == "9:16"
    
    def test_dimensions_for_platforms(self, fallback_system, mock_config):
        """Test correct dimensions for different platforms"""
        # YouTube dimensions
        mock_config.target_platform = Platform.YOUTUBE
        assert fallback_system._get_width(mock_config) == 1920
        assert fallback_system._get_height(mock_config) == 1080
        
        # TikTok dimensions
        mock_config.target_platform = Platform.TIKTOK
        assert fallback_system._get_width(mock_config) == 1080
        assert fallback_system._get_height(mock_config) == 1920
    
    def test_color_extraction_from_prompt(self, fallback_system, mock_config):
        """Test color extraction based on content type"""
        # News content
        colors = fallback_system._extract_colors_from_prompt(
            "Breaking news report", mock_config
        )
        assert len(colors) == 3
        assert colors[0] == (200, 0, 0)  # Red
        
        # Comedy content
        colors = fallback_system._extract_colors_from_prompt(
            "Family Guy comedy sketch", mock_config
        )
        assert len(colors) == 3
        assert colors[0] == (255, 200, 0)  # Yellow
        
        # Educational content
        colors = fallback_system._extract_colors_from_prompt(
            "Educational tutorial", mock_config
        )
        assert len(colors) == 3
        assert colors[0] == (0, 150, 0)  # Green
    
    def test_create_image_prompt_with_scene_data(self, fallback_system):
        """Test image prompt creation with scene data"""
        base_prompt = "News report"
        scene_data = {
            'visual_sequence': [
                {
                    'description': 'Anchor at desk',
                    'camera_angle': 'medium shot',
                    'key_elements': ['news desk', 'graphics']
                },
                {
                    'description': 'Field reporter',
                    'camera_angle': 'wide shot',
                    'key_elements': ['location', 'crowd']
                }
            ]
        }
        
        # First image should use first scene
        prompt1 = fallback_system._create_image_prompt(
            base_prompt, 0, 10, scene_data
        )
        assert "Anchor at desk" in prompt1
        assert "medium shot" in prompt1
        
        # Last image should use last scene
        prompt2 = fallback_system._create_image_prompt(
            base_prompt, 9, 10, scene_data
        )
        assert "Field reporter" in prompt2
        assert "wide shot" in prompt2
    
    @pytest.mark.asyncio
    async def test_image_sequence_generation_details(self, fallback_system, mock_config):
        """Test detailed image sequence generation"""
        mock_config.duration_seconds = 10
        
        # Calculate expected number of images
        expected_images = int(10 * 4.5)  # 4.5 images per second
        
        # Mock image generation
        fallback_system.image_client.generate_image.return_value = {
            'path': '/tmp/test_image.png'
        }
        
        # Track calls
        with patch('os.path.exists', return_value=True):
            with patch.object(fallback_system, '_create_video_from_images', 
                            return_value=True):
                await fallback_system._try_image_sequence_generation(
                    prompt="Test",
                    duration=10.0,
                    output_path="/tmp/out.mp4",
                    config=mock_config,
                    scene_data=None
                )
        
        # Should have generated correct number of images
        assert fallback_system.image_client.generate_image.call_count == expected_images
    
    def test_placeholder_image_creation(self, fallback_system, mock_config):
        """Test placeholder image creation when generation fails"""
        with patch('moviepy.editor.ColorClip') as mock_color:
            with patch('moviepy.editor.TextClip') as mock_text:
                with patch('moviepy.editor.CompositeVideoClip') as mock_composite:
                    # Mock the save_frame method
                    mock_instance = MagicMock()
                    mock_composite.return_value = mock_instance
                    
                    path = fallback_system._create_placeholder_image(
                        "Test Scene", mock_config
                    )
                    
                    assert path.startswith("/tmp/placeholder_")
                    assert path.endswith(".png")
                    mock_instance.save_frame.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complete_failure_scenario(self, fallback_system, mock_config):
        """Test when all generation methods fail"""
        # Mock all failures
        fallback_system.veo_client.generate_video.side_effect = Exception("VEO failed")
        fallback_system.image_client.generate_image.side_effect = Exception("Image failed")
        
        with patch.object(fallback_system, '_generate_color_fallback', 
                         side_effect=Exception("Color failed")):
            result = await fallback_system.generate_with_fallback(
                prompt="Test prompt",
                duration=5.0,
                config=mock_config,
                output_path="/tmp/out.mp4"
            )
        
        assert result.success is False
        assert result.method_used == "none"
        assert result.attempts == 5
        assert result.error_message == "All generation methods failed"


class TestVideoFromImages:
    """Test video creation from images"""
    
    def test_create_video_from_images(self):
        """Test creating video from image sequence"""
        fallback = VideoGenerationFallback(None, None, "test_key")
        
        # Create test images using matplotlib
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        
        images = []
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test images
            for i in range(3):
                fig, ax = plt.subplots(figsize=(10, 10))
                ax.text(0.5, 0.5, f"Frame {i+1}", 
                       fontsize=50, ha='center', va='center')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                
                img_path = os.path.join(tmpdir, f"frame_{i}.png")
                plt.savefig(img_path)
                plt.close()
                images.append(img_path)
            
            output_path = os.path.join(tmpdir, "output.mp4")
            
            # Test video creation
            with patch('moviepy.editor.ImageClip') as mock_clip:
                with patch('moviepy.editor.concatenate_videoclips') as mock_concat:
                    mock_video = MagicMock()
                    mock_concat.return_value = mock_video
                    mock_video.set_fps.return_value = mock_video
                    
                    # Mock the transition method
                    mock_video.crossfadein.return_value = mock_video
                    mock_video.crossfadeout.return_value = mock_video
                    
                    with patch('os.path.exists', return_value=True):
                        result = fallback._create_video_from_images(
                            images, output_path, 3.0, 24
                        )
                    
                    assert result is True
                    mock_video.write_videofile.assert_called_once()


class TestColorFallback:
    """Test color-based fallback generation"""
    
    @pytest.mark.asyncio
    async def test_color_fallback_generation(self):
        """Test color fallback video generation"""
        fallback = VideoGenerationFallback(None, None, "test_key")
        
        config = Mock()
        config.target_platform = Platform.YOUTUBE
        
        scene_data = {
            'script_content': 'This is a test script with multiple words'
        }
        
        with patch('moviepy.editor.ColorClip') as mock_color:
            with patch('moviepy.editor.TextClip') as mock_text:
                with patch('moviepy.editor.CompositeVideoClip') as mock_composite:
                    with patch('moviepy.editor.concatenate_videoclips') as mock_concat:
                        mock_video = MagicMock()
                        mock_concat.return_value = mock_video
                        mock_video.set_fps.return_value = mock_video
                        
                        with patch('os.path.exists', return_value=True):
                            result = await fallback._generate_color_fallback(
                                prompt="Test prompt",
                                duration=6.0,
                                output_path="/tmp/out.mp4",
                                config=config,
                                scene_data=scene_data
                            )
                        
                        assert result is True
                        mock_video.write_videofile.assert_called_once()