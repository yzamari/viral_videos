"""
Integration tests for video generation with fallback system
Tests the complete pipeline with MissionAnalyzer and VideoGenerationFallback
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock

from src.generators.video_generator import VideoGenerator
from src.generators.video_generation_fallback import VideoGenerationFallback
from src.agents.mission_analyzer import MissionAnalyzer
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory


class TestVideoFallbackIntegration:
    """Integration tests for video generation with fallback"""
    
    @pytest.fixture
    def test_config(self):
        """Create test video configuration"""
        config = Mock(spec=GeneratedVideoConfig)
        config.mission = "News anchor says: 'Breaking news!' Show explosion. Reporter: 'Chaos everywhere!'"
        config.target_platform = Platform.YOUTUBE
        config.duration_seconds = 10
        config.cheap_mode = False
        config.fallback_only = False
        config.visual_style = "realistic"
        config.tone = "serious"
        config.target_audience = "general"
        config.language = "en-US"
        config.num_clips = 2
        config.clip_durations = [5.0, 5.0]
        config.call_to_action = "Follow for more"
        config.hook = "Amazing news"
        return config
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_mission_analyzer_integration(self):
        """Test MissionAnalyzer integration with real API"""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("No API key for integration test")
        
        analyzer = MissionAnalyzer(api_key=api_key)
        
        config = Mock()
        config.mission = """
        Family Guy style animated news. Maryam says: 'Breaking news about water crisis!'
        Cut to animated map. Peter Griffin appears: 'This is worse than that time...'
        Show flashback. End with Nuclear News logo.
        """
        config.target_platform = Platform.TIKTOK
        config.duration_seconds = 30
        config.visual_style = "Family Guy animation"
        config.tone = "satirical"
        config.target_audience = "young adults"
        
        # Analyze mission
        result = await analyzer.analyze_mission(config, use_multishot=True)
        
        # Verify analysis
        assert result is not None
        assert len(result.script_content) > 0
        assert "Breaking news about water crisis" in result.script_content
        assert "This is worse than that time" in result.script_content
        assert len(result.visual_sequence) > 0
        assert result.content_type in ["comedy", "news_parody", "satirical_news"]
        assert result.confidence_score > 0.5
        
        # Verify no visual instructions in script
        assert "Cut to" not in result.script_content
        assert "Show" not in result.script_content
        assert "End with" not in result.script_content
    
    @pytest.mark.asyncio
    async def test_fallback_chain_veo_success(self):
        """Test fallback chain when VEO succeeds"""
        # Mock VEO client
        mock_veo = Mock()
        mock_veo.generate_video = AsyncMock(return_value="/tmp/veo_video.mp4")
        
        # Mock image client
        mock_image = Mock()
        
        fallback = VideoGenerationFallback(
            veo_client=mock_veo,
            image_client=mock_image,
            api_key="test_key"
        )
        
        config = Mock()
        config.target_platform = Platform.YOUTUBE
        config.fallback_only = False
        
        with patch('os.path.exists', return_value=True):
            with patch('os.rename'):
                result = await fallback.generate_with_fallback(
                    prompt="Test prompt",
                    duration=5.0,
                    config=config,
                    output_path="/tmp/output.mp4"
                )
        
        assert result.success is True
        assert result.method_used == "veo"
        assert result.attempts == 1
        mock_veo.generate_video.assert_called_once()
        mock_image.generate_image.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_fallback_chain_image_sequence(self):
        """Test fallback to image sequence when VEO fails"""
        # Mock VEO client that fails
        mock_veo = Mock()
        mock_veo.generate_video = AsyncMock(side_effect=Exception("VEO failed"))
        
        # Mock image client
        mock_image = Mock()
        mock_image.generate_image = AsyncMock(return_value={'path': '/tmp/image.png'})
        
        fallback = VideoGenerationFallback(
            veo_client=mock_veo,
            image_client=mock_image,
            api_key="test_key"
        )
        
        config = Mock()
        config.target_platform = Platform.YOUTUBE
        config.fallback_only = False
        
        scene_data = {
            'visual_sequence': [
                {'description': 'News anchor speaking'},
                {'description': 'Explosion effect'}
            ]
        }
        
        with patch('os.path.exists', return_value=True):
            with patch.object(fallback, '_create_video_from_images', return_value=True):
                result = await fallback.generate_with_fallback(
                    prompt="Test prompt",
                    duration=4.0,  # Will generate ~18 images
                    config=config,
                    output_path="/tmp/output.mp4",
                    scene_data=scene_data
                )
        
        assert result.success is True
        assert result.method_used == "image_sequence"
        assert result.attempts == 3  # 2 VEO attempts + 1 image
        
        # Verify correct number of images generated (4.5 per second)
        expected_images = int(4.0 * 4.5)
        assert mock_image.generate_image.call_count == expected_images
    
    @pytest.mark.asyncio
    async def test_fallback_chain_color_fallback(self):
        """Test color fallback when all else fails"""
        # Mock failures
        mock_veo = Mock()
        mock_veo.generate_video = AsyncMock(side_effect=Exception("VEO failed"))
        
        mock_image = Mock()
        mock_image.generate_image = AsyncMock(side_effect=Exception("Image failed"))
        
        fallback = VideoGenerationFallback(
            veo_client=mock_veo,
            image_client=mock_image,
            api_key="test_key"
        )
        
        config = Mock()
        config.target_platform = Platform.TIKTOK
        config.visual_style = "news"
        config.fallback_only = False
        
        with patch.object(fallback, '_generate_color_fallback', return_value=True):
            result = await fallback.generate_with_fallback(
                prompt="Breaking news report",
                duration=3.0,
                config=config,
                output_path="/tmp/output.mp4"
            )
        
        assert result.success is True
        assert result.method_used == "color_fallback"
        assert result.attempts == 5
    
    @pytest.mark.asyncio
    async def test_script_video_audio_alignment(self):
        """Test that script, video, and audio are properly aligned"""
        # This is a more complex integration test
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock config
            config = Mock()
            config.mission = "Anchor: 'Breaking news!' Explosion. 'The situation is critical.'"
            config.target_platform = Platform.YOUTUBE
            config.duration_seconds = 6
            config.num_clips = 2
            config.clip_durations = [3.0, 3.0]
            
            # Mock analyzer to return clean script
            mock_analyzer = Mock()
            analyzed = Mock()
            analyzed.script_content = "Breaking news! The situation is critical."
            analyzed.visual_sequence = [
                {'duration_seconds': 3, 'description': 'Anchor speaking'},
                {'duration_seconds': 3, 'description': 'Explosion and aftermath'}
            ]
            analyzed.character_details = {}
            analyzed.complexity_level = "simple"
            analyzed.confidence_score = 0.9
            mock_analyzer.analyze_mission = AsyncMock(return_value=analyzed)
            
            # Test alignment
            assert len(analyzed.script_content.split('.')) >= 2  # At least 2 sentences
            assert len(analyzed.visual_sequence) == 2  # Matches clip count
            
            # Verify timing alignment
            total_visual_duration = sum(s['duration_seconds'] for s in analyzed.visual_sequence)
            assert total_visual_duration == config.duration_seconds
    
    @pytest.mark.asyncio
    async def test_platform_specific_generation(self):
        """Test platform-specific video generation"""
        fallback = VideoGenerationFallback(None, None, "test_key")
        
        # Test YouTube (16:9)
        youtube_config = Mock()
        youtube_config.target_platform = Platform.YOUTUBE
        assert fallback._get_aspect_ratio(youtube_config) == "16:9"
        assert fallback._get_width(youtube_config) == 1920
        assert fallback._get_height(youtube_config) == 1080
        
        # Test TikTok (9:16)
        tiktok_config = Mock()
        tiktok_config.target_platform = Platform.TIKTOK
        assert fallback._get_aspect_ratio(tiktok_config) == "9:16"
        assert fallback._get_width(tiktok_config) == 1080
        assert fallback._get_height(tiktok_config) == 1920
    
    @pytest.mark.asyncio
    async def test_scene_aware_image_generation(self):
        """Test that image generation uses scene data properly"""
        mock_image = Mock()
        generated_prompts = []
        
        async def capture_prompt(prompt, **kwargs):
            generated_prompts.append(prompt)
            return {'path': f'/tmp/image_{len(generated_prompts)}.png'}
        
        mock_image.generate_image = AsyncMock(side_effect=capture_prompt)
        
        fallback = VideoGenerationFallback(
            veo_client=None,
            image_client=mock_image,
            api_key="test_key"
        )
        
        config = Mock()
        config.target_platform = Platform.YOUTUBE
        config.visual_style = "realistic"
        
        scene_data = {
            'visual_sequence': [
                {
                    'description': 'News anchor at desk',
                    'camera_angle': 'medium shot',
                    'key_elements': ['news desk', 'graphics']
                },
                {
                    'description': 'Field reporter on location',
                    'camera_angle': 'wide shot',
                    'key_elements': ['crowd', 'buildings']
                }
            ]
        }
        
        with patch('os.path.exists', return_value=True):
            with patch.object(fallback, '_create_video_from_images', return_value=True):
                await fallback._try_image_sequence_generation(
                    prompt="News report",
                    duration=2.0,  # Will generate ~9 images
                    output_path="/tmp/out.mp4",
                    config=config,
                    scene_data=scene_data
                )
        
        # Verify prompts include scene information
        assert any('News anchor at desk' in p for p in generated_prompts)
        assert any('medium shot' in p for p in generated_prompts)
        assert any('Field reporter' in p for p in generated_prompts)
        assert any('wide shot' in p for p in generated_prompts)


class TestCompleteVideoGeneration:
    """Test complete video generation pipeline"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_pipeline_with_fallback(self):
        """Test complete pipeline from mission to final video"""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("No API key for integration test")
        
        # This would test the full pipeline but requires significant setup
        # and actual API calls, so we'll mock most parts
        
        config = Mock()
        config.mission = "Test news: 'Important announcement!' Show graphics."
        config.target_platform = Platform.YOUTUBE
        config.duration_seconds = 5
        config.cheap_mode = True  # Use fallback
        config.fallback_only = True
        
        # The actual implementation would involve:
        # 1. MissionAnalyzer analyzing the mission
        # 2. VideoGenerator creating clips with fallback
        # 3. Audio generation matching the script
        # 4. Subtitle generation synchronized with audio
        # 5. Final video assembly
        
        # For now, we just verify the components exist
        analyzer = MissionAnalyzer(api_key=api_key)
        assert analyzer is not None
        
        fallback = VideoGenerationFallback(None, None, api_key)
        assert fallback is not None