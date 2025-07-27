"""
Tests for VEO-2 Integration
Ensures VEO-2 video generation works correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path

from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client


class TestVEO2Generation:
    """Test suite for VEO-2 video generation"""
    
    @pytest.fixture
    def mock_vertex_ai(self):
        """Mock Vertex AI dependencies"""
        with patch('src.generators.vertex_ai_veo2_client.aiplatform') as mock_ai:
            mock_ai.init = Mock()
            yield mock_ai
    
    @pytest.fixture
    def mock_image_generation(self):
        """Mock image generation client"""
        with patch('src.generators.vertex_ai_veo2_client.ImageGenerationClient') as mock_client:
            mock_instance = Mock()
            mock_instance.generate_images.return_value = Mock(
                images=[Mock(image=Mock(_image_bytes=b'fake_image_data'))]
            )
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def veo2_client(self, mock_vertex_ai, mock_image_generation):
        """Create VEO-2 client instance"""
        return VertexAIVeo2Client()
    
    @pytest.mark.unit
    def test_veo2_client_initialization(self, mock_vertex_ai):
        """Test VEO-2 client initializes correctly"""
        client = VertexAIVeo2Client()
        assert client is not None
        mock_vertex_ai.init.assert_called_once()
    
    @pytest.mark.unit
    def test_generate_video_success(self, veo2_client, temp_dir):
        """Test successful video generation"""
        # Setup
        prompt = "A futuristic city with flying cars"
        output_path = os.path.join(temp_dir, "test_video.mp4")
        
        # Mock the generate method
        with patch.object(veo2_client, '_generate_from_veo2') as mock_generate:
            mock_generate.return_value = b'fake_video_data'
            
            # Execute
            result = veo2_client.generate_video(
                prompt=prompt,
                output_path=output_path,
                duration=5
            )
            
            # Assert
            assert result == output_path
            assert os.path.exists(output_path)
            mock_generate.assert_called_once()
    
    @pytest.mark.unit
    def test_generate_video_with_reference_image(self, veo2_client, temp_dir):
        """Test video generation with reference image"""
        prompt = "Transform this scene into a futuristic version"
        output_path = os.path.join(temp_dir, "test_video.mp4")
        reference_image = os.path.join(temp_dir, "reference.jpg")
        
        # Create fake reference image
        Path(reference_image).write_bytes(b'fake_image_data')
        
        with patch.object(veo2_client, '_generate_from_veo2') as mock_generate:
            mock_generate.return_value = b'fake_video_data'
            
            result = veo2_client.generate_video(
                prompt=prompt,
                output_path=output_path,
                duration=5,
                reference_image_path=reference_image
            )
            
            assert result == output_path
            assert os.path.exists(output_path)
    
    @pytest.mark.unit
    def test_generate_video_fallback_to_image(self, veo2_client, mock_image_generation, temp_dir):
        """Test fallback to image generation when VEO-2 fails"""
        prompt = "A scene that will fail VEO-2"
        output_path = os.path.join(temp_dir, "test_video.mp4")
        
        # Mock VEO-2 failure
        with patch.object(veo2_client, '_generate_from_veo2') as mock_veo2:
            mock_veo2.side_effect = Exception("VEO-2 generation failed")
            
            # Mock image to video conversion
            with patch.object(veo2_client, '_convert_image_to_video') as mock_convert:
                mock_convert.return_value = None
                
                result = veo2_client.generate_video(
                    prompt=prompt,
                    output_path=output_path,
                    duration=5
                )
                
                # Should fallback to image generation
                assert result == output_path
                mock_image_generation.generate_images.assert_called_once()
                mock_convert.assert_called_once()
    
    @pytest.mark.unit
    def test_aspect_ratio_handling(self, veo2_client):
        """Test different aspect ratios are handled correctly"""
        aspect_ratios = ["16:9", "9:16", "1:1", "4:3"]
        
        for ratio in aspect_ratios:
            with patch.object(veo2_client, '_generate_from_veo2') as mock_generate:
                mock_generate.return_value = b'fake_video_data'
                
                result = veo2_client.generate_video(
                    prompt="Test prompt",
                    output_path=f"test_{ratio.replace(':', '_')}.mp4",
                    aspect_ratio=ratio,
                    duration=5
                )
                
                assert result is not None
    
    @pytest.mark.unit
    def test_error_handling_invalid_duration(self, veo2_client):
        """Test error handling for invalid duration"""
        with pytest.raises(ValueError):
            veo2_client.generate_video(
                prompt="Test prompt",
                output_path="test.mp4",
                duration=0  # Invalid duration
            )
    
    @pytest.mark.unit
    def test_error_handling_empty_prompt(self, veo2_client):
        """Test error handling for empty prompt"""
        with pytest.raises(ValueError):
            veo2_client.generate_video(
                prompt="",  # Empty prompt
                output_path="test.mp4",
                duration=5
            )
    
    @pytest.mark.unit
    @patch('src.generators.vertex_ai_veo2_client.os.environ')
    def test_project_id_configuration(self, mock_environ, mock_vertex_ai, mock_image_generation):
        """Test project ID is correctly configured"""
        mock_environ.get.return_value = "test-project-id"
        
        client = VertexAIVeo2Client()
        
        # Verify project ID was used
        mock_vertex_ai.init.assert_called_with(
            project="test-project-id",
            location="us-central1"
        )
    
    @pytest.mark.unit
    def test_retry_mechanism(self, veo2_client):
        """Test retry mechanism for transient failures"""
        prompt = "Test prompt"
        output_path = "test.mp4"
        
        # Mock to fail twice then succeed
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Transient error")
            return b'fake_video_data'
        
        with patch.object(veo2_client, '_generate_from_veo2', side_effect=side_effect):
            result = veo2_client.generate_video(
                prompt=prompt,
                output_path=output_path,
                duration=5
            )
            
            assert result == output_path
            assert call_count == 3  # Should retry twice before succeeding
    
    @pytest.mark.integration
    @pytest.mark.requires_api
    @pytest.mark.skipif(
        not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
        reason="Requires Google Cloud credentials"
    )
    def test_real_veo2_connection(self):
        """Test real connection to VEO-2 API (requires credentials)"""
        client = VertexAIVeo2Client()
        
        # Just test initialization succeeds with real credentials
        assert client is not None
        assert hasattr(client, 'generate_video')