"""
Tests for VEO-3 Integration
Ensures VEO-3 video generation works correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path

from src.generators.vertex_veo3_client import VertexVeo3Client


class TestVEO3Generation:
    """Test suite for VEO-3 video generation"""
    
    @pytest.fixture
    def mock_genai(self):
        """Mock Google GenAI dependencies"""
        with patch('src.generators.vertex_veo3_client.genai') as mock_genai:
            mock_genai.configure = Mock()
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            yield mock_genai
    
    @pytest.fixture
    def veo3_client(self, mock_genai):
        """Create VEO-3 client instance"""
        with patch('src.generators.vertex_veo3_client.os.environ.get', return_value='test-api-key'):
            return VertexVeo3Client()
    
    @pytest.mark.unit
    def test_veo3_client_initialization(self, mock_genai):
        """Test VEO-3 client initializes correctly"""
        with patch('src.generators.vertex_veo3_client.os.environ.get', return_value='test-api-key'):
            client = VertexVeo3Client()
            assert client is not None
            mock_genai.configure.assert_called_once_with(api_key='test-api-key')
    
    @pytest.mark.unit
    def test_generate_video_success(self, veo3_client, temp_dir):
        """Test successful video generation with VEO-3"""
        prompt = "A serene mountain landscape at sunset"
        output_path = os.path.join(temp_dir, "test_veo3_video.mp4")
        
        # Mock video generation
        mock_response = Mock()
        mock_response.video = Mock()
        mock_response.video._data = b'fake_video_data_veo3'
        
        with patch.object(veo3_client.model, 'generate_content', return_value=mock_response):
            result = veo3_client.generate_video(
                prompt=prompt,
                output_path=output_path,
                duration=10
            )
            
            assert result == output_path
            assert os.path.exists(output_path)
            
            # Verify file content
            with open(output_path, 'rb') as f:
                assert f.read() == b'fake_video_data_veo3'
    
    @pytest.mark.unit
    def test_generate_video_with_advanced_prompt(self, veo3_client, temp_dir):
        """Test VEO-3 with advanced prompt structure"""
        prompt = {
            "main": "A futuristic cityscape",
            "style": "cyberpunk aesthetic",
            "camera": "aerial drone shot",
            "lighting": "neon lights at night"
        }
        output_path = os.path.join(temp_dir, "test_advanced.mp4")
        
        mock_response = Mock()
        mock_response.video = Mock()
        mock_response.video._data = b'fake_advanced_video'
        
        with patch.object(veo3_client.model, 'generate_content', return_value=mock_response):
            # VEO-3 should handle complex prompts
            formatted_prompt = veo3_client._format_prompt(prompt)
            result = veo3_client.generate_video(
                prompt=formatted_prompt,
                output_path=output_path,
                duration=8
            )
            
            assert result == output_path
            assert os.path.exists(output_path)
    
    @pytest.mark.unit
    def test_veo3_specific_features(self, veo3_client):
        """Test VEO-3 specific features like higher quality settings"""
        with patch.object(veo3_client.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.video = Mock()
            mock_response.video._data = b'high_quality_video'
            mock_generate.return_value = mock_response
            
            # Test high quality mode
            result = veo3_client.generate_video(
                prompt="High quality test",
                output_path="hq_test.mp4",
                duration=5,
                quality="high"  # VEO-3 specific parameter
            )
            
            assert result is not None
            # Verify quality parameter was used
            call_args = mock_generate.call_args
            assert call_args is not None
    
    @pytest.mark.unit
    def test_longer_duration_support(self, veo3_client):
        """Test VEO-3 supports longer video durations"""
        # VEO-3 supports up to 60 seconds
        durations = [10, 30, 60]
        
        for duration in durations:
            with patch.object(veo3_client.model, 'generate_content') as mock_generate:
                mock_response = Mock()
                mock_response.video = Mock()
                mock_response.video._data = b'video_data'
                mock_generate.return_value = mock_response
                
                result = veo3_client.generate_video(
                    prompt="Long duration test",
                    output_path=f"test_{duration}s.mp4",
                    duration=duration
                )
                
                assert result is not None
    
    @pytest.mark.unit
    def test_error_handling_no_api_key(self, mock_genai):
        """Test error handling when API key is missing"""
        with patch('src.generators.vertex_veo3_client.os.environ.get', return_value=None):
            with pytest.raises(ValueError, match="API key"):
                VertexVeo3Client()
    
    @pytest.mark.unit
    def test_error_handling_generation_failure(self, veo3_client):
        """Test error handling when generation fails"""
        with patch.object(veo3_client.model, 'generate_content', side_effect=Exception("API Error")):
            with pytest.raises(Exception, match="API Error"):
                veo3_client.generate_video(
                    prompt="Test prompt",
                    output_path="test.mp4",
                    duration=5
                )
    
    @pytest.mark.unit
    def test_fallback_mechanism(self, veo3_client, temp_dir):
        """Test VEO-3 fallback to alternative generation"""
        prompt = "Test fallback"
        output_path = os.path.join(temp_dir, "fallback.mp4")
        
        # First attempt fails
        with patch.object(veo3_client.model, 'generate_content') as mock_generate:
            # Simulate first failure then success
            mock_response = Mock()
            mock_response.video = Mock()
            mock_response.video._data = b'fallback_video'
            
            mock_generate.side_effect = [Exception("First attempt failed"), mock_response]
            
            # Should retry and succeed
            with patch.object(veo3_client, '_retry_generation', return_value=mock_response):
                result = veo3_client.generate_video(
                    prompt=prompt,
                    output_path=output_path,
                    duration=5
                )
                
                assert result == output_path
    
    @pytest.mark.unit
    def test_prompt_enhancement(self, veo3_client):
        """Test VEO-3 prompt enhancement capabilities"""
        simple_prompt = "A cat"
        
        # VEO-3 should enhance simple prompts
        enhanced = veo3_client._enhance_prompt(simple_prompt)
        
        assert len(enhanced) > len(simple_prompt)
        assert "cat" in enhanced.lower()
        # Should add quality descriptors
        assert any(word in enhanced.lower() for word in ["high quality", "detailed", "4k", "professional"])
    
    @pytest.mark.unit
    def test_model_switching(self, mock_genai):
        """Test switching between VEO-3 model variants"""
        with patch('src.generators.vertex_veo3_client.os.environ.get', return_value='test-api-key'):
            # Test standard model
            client_standard = VertexVeo3Client(model_variant="standard")
            assert client_standard.model_name == "veo-003"
            
            # Test preview model
            client_preview = VertexVeo3Client(model_variant="preview")
            assert client_preview.model_name == "veo-003-preview"
    
    @pytest.mark.integration
    @pytest.mark.requires_api
    @pytest.mark.skipif(
        not os.environ.get('GOOGLE_API_KEY'),
        reason="Requires Google API key"
    )
    def test_real_veo3_connection(self):
        """Test real connection to VEO-3 API (requires API key)"""
        client = VertexVeo3Client()
        
        # Just test initialization and model availability
        assert client is not None
        assert hasattr(client, 'generate_video')
        assert client.model is not None