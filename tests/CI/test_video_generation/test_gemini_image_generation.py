"""
Tests for Gemini Image Generation
Ensures Gemini image fallback system works correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path
from PIL import Image
import io

from src.generators.gemini_image_client import GeminiImageClient


class TestGeminiImageGeneration:
    """Test suite for Gemini image generation"""
    
    @pytest.fixture
    def mock_genai(self):
        """Mock Google GenAI for Gemini"""
        with patch('src.generators.gemini_image_client.genai') as mock_genai:
            mock_genai.configure = Mock()
            
            # Mock image generation model
            mock_imagen = Mock()
            mock_genai.ImageGenerationModel.return_value = mock_imagen
            
            # Mock text model for prompt enhancement
            mock_text_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_text_model
            
            yield mock_genai
    
    @pytest.fixture
    def gemini_client(self, mock_genai):
        """Create Gemini client instance"""
        with patch('src.generators.gemini_image_client.os.environ.get', return_value='test-api-key'):
            return GeminiImageClient()
    
    @pytest.mark.unit
    def test_gemini_client_initialization(self, mock_genai):
        """Test Gemini client initializes correctly"""
        with patch('src.generators.gemini_image_client.os.environ.get', return_value='test-api-key'):
            client = GeminiImageClient()
            assert client is not None
            mock_genai.configure.assert_called_once_with(api_key='test-api-key')
    
    @pytest.mark.unit
    def test_generate_single_image(self, gemini_client, temp_dir):
        """Test generating a single image"""
        prompt = "A beautiful sunset over mountains"
        
        # Create fake image data
        fake_image = Image.new('RGB', (1024, 1024), color='red')
        img_bytes = io.BytesIO()
        fake_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Mock the response
        mock_response = Mock()
        mock_response.images = [Mock(_pil_image=fake_image)]
        
        with patch.object(gemini_client.imagen_model, 'generate_images', return_value=mock_response):
            result = gemini_client.generate_image(prompt)
            
            assert result is not None
            assert isinstance(result, bytes)
    
    @pytest.mark.unit
    def test_generate_multiple_images(self, gemini_client, temp_dir):
        """Test generating multiple image variations"""
        prompt = "A futuristic robot"
        num_images = 4
        
        # Create multiple fake images
        fake_images = []
        for i in range(num_images):
            img = Image.new('RGB', (1024, 1024), color=(i*50, i*50, i*50))
            fake_images.append(Mock(_pil_image=img))
        
        mock_response = Mock()
        mock_response.images = fake_images
        
        with patch.object(gemini_client.imagen_model, 'generate_images', return_value=mock_response):
            results = gemini_client.generate_images(prompt, count=num_images)
            
            assert len(results) == num_images
            assert all(isinstance(img, bytes) for img in results)
    
    @pytest.mark.unit
    def test_aspect_ratio_handling(self, gemini_client):
        """Test different aspect ratios for image generation"""
        aspect_ratios = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1": (1024, 1024),
            "4:3": (1024, 768)
        }
        
        for ratio, expected_size in aspect_ratios.items():
            fake_image = Image.new('RGB', expected_size, color='blue')
            mock_response = Mock()
            mock_response.images = [Mock(_pil_image=fake_image)]
            
            with patch.object(gemini_client.imagen_model, 'generate_images', return_value=mock_response):
                result = gemini_client.generate_image(
                    prompt="Test image",
                    aspect_ratio=ratio
                )
                
                assert result is not None
                
                # Verify image dimensions
                img = Image.open(io.BytesIO(result))
                assert img.size == expected_size
    
    @pytest.mark.unit
    def test_style_application(self, gemini_client):
        """Test applying different styles to generated images"""
        styles = ["photorealistic", "artistic", "cartoon", "oil painting", "watercolor"]
        
        for style in styles:
            fake_image = Image.new('RGB', (1024, 1024), color='green')
            mock_response = Mock()
            mock_response.images = [Mock(_pil_image=fake_image)]
            
            with patch.object(gemini_client.imagen_model, 'generate_images', return_value=mock_response):
                # Verify style is included in prompt
                with patch.object(gemini_client, '_enhance_prompt_with_style') as mock_enhance:
                    mock_enhance.return_value = f"Test prompt in {style} style"
                    
                    result = gemini_client.generate_image(
                        prompt="A landscape",
                        style=style
                    )
                    
                    assert result is not None
                    mock_enhance.assert_called_once_with("A landscape", style)
    
    @pytest.mark.unit
    def test_prompt_enhancement(self, gemini_client):
        """Test automatic prompt enhancement for better results"""
        simple_prompt = "A cat"
        
        # Mock text model response for enhancement
        enhanced_response = Mock()
        enhanced_response.text = "A majestic cat with detailed fur, sitting gracefully, professional photography, high resolution"
        
        with patch.object(gemini_client.text_model, 'generate_content', return_value=enhanced_response):
            enhanced = gemini_client.enhance_prompt(simple_prompt)
            
            assert len(enhanced) > len(simple_prompt)
            assert "cat" in enhanced.lower()
            assert any(quality_word in enhanced.lower() for quality_word in ["detailed", "high", "professional"])
    
    @pytest.mark.unit
    def test_error_handling_no_api_key(self, mock_genai):
        """Test error handling when API key is missing"""
        with patch('src.generators.gemini_image_client.os.environ.get', return_value=None):
            with pytest.raises(ValueError, match="API key"):
                GeminiImageClient()
    
    @pytest.mark.unit
    def test_error_handling_generation_failure(self, gemini_client):
        """Test error handling when image generation fails"""
        with patch.object(gemini_client.imagen_model, 'generate_images', side_effect=Exception("API Error")):
            with pytest.raises(Exception, match="API Error"):
                gemini_client.generate_image("Test prompt")
    
    @pytest.mark.unit
    def test_retry_mechanism(self, gemini_client):
        """Test retry mechanism for transient failures"""
        fake_image = Image.new('RGB', (1024, 1024), color='yellow')
        mock_response = Mock()
        mock_response.images = [Mock(_pil_image=fake_image)]
        
        # Fail twice, then succeed
        with patch.object(gemini_client.imagen_model, 'generate_images', 
                         side_effect=[Exception("Transient error"), 
                                    Exception("Another transient error"), 
                                    mock_response]):
            
            result = gemini_client.generate_image("Test prompt", max_retries=3)
            assert result is not None
    
    @pytest.mark.unit
    def test_save_image_to_file(self, gemini_client, temp_dir):
        """Test saving generated image to file"""
        output_path = os.path.join(temp_dir, "test_image.png")
        
        fake_image = Image.new('RGB', (1024, 1024), color='purple')
        mock_response = Mock()
        mock_response.images = [Mock(_pil_image=fake_image)]
        
        with patch.object(gemini_client.imagen_model, 'generate_images', return_value=mock_response):
            result_path = gemini_client.generate_and_save_image(
                prompt="Test image",
                output_path=output_path
            )
            
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            # Verify it's a valid image
            img = Image.open(output_path)
            assert img.size == (1024, 1024)
    
    @pytest.mark.unit
    def test_batch_generation(self, gemini_client, temp_dir):
        """Test batch generation of images for video frames"""
        prompts = [
            "Frame 1: Sunrise",
            "Frame 2: Midday",
            "Frame 3: Sunset",
            "Frame 4: Night"
        ]
        
        # Mock responses for each prompt
        for i, prompt in enumerate(prompts):
            fake_image = Image.new('RGB', (1024, 1024), color=(i*60, i*60, i*60))
            mock_response = Mock()
            mock_response.images = [Mock(_pil_image=fake_image)]
            
            with patch.object(gemini_client.imagen_model, 'generate_images', return_value=mock_response):
                output_path = os.path.join(temp_dir, f"frame_{i}.png")
                result = gemini_client.generate_and_save_image(prompt, output_path)
                
                assert os.path.exists(result)
    
    @pytest.mark.unit
    def test_content_filtering(self, gemini_client):
        """Test content filtering for inappropriate prompts"""
        inappropriate_prompt = "Generate inappropriate content"
        
        # Mock content filter rejection
        with patch.object(gemini_client.imagen_model, 'generate_images', 
                         side_effect=Exception("Content filtered")):
            
            with pytest.raises(Exception, match="Content filtered"):
                gemini_client.generate_image(inappropriate_prompt)
    
    @pytest.mark.integration
    @pytest.mark.requires_api
    @pytest.mark.skipif(
        not os.environ.get('GOOGLE_API_KEY'),
        reason="Requires Google API key"
    )
    def test_real_gemini_connection(self):
        """Test real connection to Gemini API (requires API key)"""
        client = GeminiImageClient()
        
        # Just test initialization succeeds
        assert client is not None
        assert hasattr(client, 'generate_image')
        assert client.imagen_model is not None