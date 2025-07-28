#!/usr/bin/env python3
"""
Unit tests for VEO3 client portrait video generation
Tests verify that VEO3 client generates portrait videos correctly
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.generators.vertex_veo3_client import VertexAIVeo3Client
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class TestVEO3ClientPortrait(unittest.TestCase):
    """Test VEO3 client portrait video generation"""

    def setUp(self):
        """Set up test environment"""
        self.project_id = 'viralgen-464411'
        self.location = 'us-central1'
        self.gcs_bucket = 'viral-veo2-results'
        self.output_dir = '/tmp/test_veo3_output'
        
        # Skip tests if no API key
        if not os.getenv('GOOGLE_API_KEY'):
            self.skipTest("No GOOGLE_API_KEY found")

    def test_portrait_aspect_ratio_parameter(self):
        """Test that VEO3 client accepts and uses portrait aspect ratio"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        # Test that generate_video method accepts aspect_ratio parameter
        prompt = "A simple test video of a person walking"
        
        # Mock the internal API call to test parameter passing
        with patch.object(client, '_submit_generation_request') as mock_submit:
            mock_submit.return_value = {
                'name': 'test-operation-id'
            }
            
            # Mock the polling and download
            with patch.object(client, '_poll_operation_status') as mock_poll:
                mock_poll.return_value = {
                    'done': True,
                    'response': {
                        'generatedVideo': {
                            'gcsUri': 'gs://test-bucket/test-video.mp4'
                        }
                    }
                }
                
                with patch.object(client, '_download_video') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    # Test portrait aspect ratio
                    result = client.generate_video(
                        prompt=prompt,
                        duration=8.0,
                        aspect_ratio="9:16"
                    )
                    
                    # Verify the API was called with correct aspect ratio
                    mock_submit.assert_called_once()
                    call_args = mock_submit.call_args[0][0]
                    
                    # Check that aspect ratio was passed correctly
                    self.assertEqual(call_args['instances'][0]['aspectRatio'], '9:16')
                    self.assertTrue(result.endswith('.mp4'))

    def test_default_portrait_aspect_ratio(self):
        """Test that VEO3 client defaults to portrait aspect ratio"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        prompt = "A simple test video of a person walking"
        
        # Mock the internal API call to test default parameter
        with patch.object(client, '_submit_generation_request') as mock_submit:
            mock_submit.return_value = {
                'name': 'test-operation-id'
            }
            
            # Mock the polling and download
            with patch.object(client, '_poll_operation_status') as mock_poll:
                mock_poll.return_value = {
                    'done': True,
                    'response': {
                        'generatedVideo': {
                            'gcsUri': 'gs://test-bucket/test-video.mp4'
                        }
                    }
                }
                
                with patch.object(client, '_download_video') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    # Test default aspect ratio (should be portrait)
                    result = client.generate_video(
                        prompt=prompt,
                        duration=8.0
                    )
                    
                    # Verify the API was called with default portrait aspect ratio
                    mock_submit.assert_called_once()
                    call_args = mock_submit.call_args[0][0]
                    
                    # Check that default aspect ratio is portrait
                    self.assertEqual(call_args['instances'][0]['aspectRatio'], '9:16')
                    self.assertTrue(result.endswith('.mp4'))

    def test_landscape_aspect_ratio_override(self):
        """Test that VEO3 client can be overridden to landscape"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        prompt = "A simple test video of a person walking"
        
        # Mock the internal API call to test landscape override
        with patch.object(client, '_submit_generation_request') as mock_submit:
            mock_submit.return_value = {
                'name': 'test-operation-id'
            }
            
            # Mock the polling and download
            with patch.object(client, '_poll_operation_status') as mock_poll:
                mock_poll.return_value = {
                    'done': True,
                    'response': {
                        'generatedVideo': {
                            'gcsUri': 'gs://test-bucket/test-video.mp4'
                        }
                    }
                }
                
                with patch.object(client, '_download_video') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    # Test landscape aspect ratio override
                    result = client.generate_video(
                        prompt=prompt,
                        duration=8.0,
                        aspect_ratio="16:9"
                    )
                    
                    # Verify the API was called with landscape aspect ratio
                    mock_submit.assert_called_once()
                    call_args = mock_submit.call_args[0][0]
                    
                    # Check that aspect ratio was overridden to landscape
                    self.assertEqual(call_args['instances'][0]['aspectRatio'], '16:9')
                    self.assertTrue(result.endswith('.mp4'))

    def test_audio_enabled_parameter(self):
        """Test that VEO3 client handles audio parameter correctly"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        prompt = "A simple test video of a person walking"
        
        # Mock the internal API call to test audio parameter
        with patch.object(client, '_submit_generation_request') as mock_submit:
            mock_submit.return_value = {
                'name': 'test-operation-id'
            }
            
            # Mock the polling and download
            with patch.object(client, '_poll_operation_status') as mock_poll:
                mock_poll.return_value = {
                    'done': True,
                    'response': {
                        'generatedVideo': {
                            'gcsUri': 'gs://test-bucket/test-video.mp4'
                        }
                    }
                }
                
                with patch.object(client, '_download_video') as mock_download:
                    mock_download.return_value = '/tmp/test_video.mp4'
                    
                    # Test with audio enabled
                    result = client.generate_video(
                        prompt=prompt,
                        duration=8.0,
                        aspect_ratio="9:16",
                        enable_audio=True
                    )
                    
                    # Verify the API was called with audio enabled
                    mock_submit.assert_called_once()
                    call_args = mock_submit.call_args[0][0]
                    
                    # Check that audio was enabled
                    self.assertTrue(call_args['instances'][0]['enableAudio'])
                    self.assertEqual(call_args['instances'][0]['aspectRatio'], '9:16')
                    self.assertTrue(result.endswith('.mp4'))

    def test_fallback_to_veo2(self):
        """Test that VEO3 client falls back to VEO2 on failure"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        prompt = "A simple test video of a person walking"
        
        # Mock VEO3 to fail
        with patch.object(client, '_submit_generation_request') as mock_submit:
            mock_submit.side_effect = Exception("VEO3 service unavailable")
            
            # Mock VEO2 client to succeed
            with patch.object(client, 'veo2_client') as mock_veo2:
                mock_veo2.generate_video.return_value = '/tmp/fallback_video.mp4'
                
                # Test fallback behavior
                result = client.generate_video(
                    prompt=prompt,
                    duration=8.0,
                    aspect_ratio="9:16"
                )
                
                # Verify VEO2 was called as fallback
                mock_veo2.generate_video.assert_called_once()
                fallback_call = mock_veo2.generate_video.call_args
                
                # Check that aspect ratio was preserved in fallback
                self.assertEqual(fallback_call[1]['aspect_ratio'], '9:16')
                self.assertTrue(result.endswith('.mp4'))

    @unittest.skipIf(os.getenv('SKIP_INTEGRATION_TESTS') == 'true', 
                     "Integration tests skipped")
    def test_real_veo3_fast_generation(self):
        """Integration test: Generate actual video using VEO-3-FAST"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        # Enable VEO-3-FAST mode
        client.is_veo3_fast = True
        
        prompt = "A simple 5-second video of a red car driving on a highway"
        
        try:
            # Generate video with VEO-3-FAST (no audio)
            result = client.generate_video(
                prompt=prompt,
                duration=5.0,
                aspect_ratio="9:16",
                enable_audio=False,  # VEO-3-FAST doesn't support audio
                clip_id="test_veo3_fast"
            )
            
            # Verify file was created
            self.assertTrue(os.path.exists(result))
            self.assertTrue(result.endswith('.mp4'))
            
            # Verify it's a valid video file
            file_size = os.path.getsize(result)
            self.assertGreater(file_size, 1000, "Video file should be larger than 1KB")
            
            logger.info(f"✅ Generated VEO-3-FAST video: {result} ({file_size} bytes)")
            
            # Clean up
            if os.path.exists(result):
                os.remove(result)
                
        except Exception as e:
            # If VEO-3-FAST is not available, this is expected
            if "VEO3 service unavailable" in str(e):
                logger.warning("VEO-3-FAST service unavailable, skipping integration test")
                self.skipTest("VEO-3-FAST service unavailable")
            else:
                self.fail(f"VEO-3-FAST generation failed: {e}")

    @unittest.skipIf(os.getenv('SKIP_INTEGRATION_TESTS') == 'true', 
                     "Integration tests skipped")
    def test_real_veo3_portrait_generation(self):
        """Integration test: Generate actual portrait video using VEO3"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        prompt = "A simple 5-second video of a blue bird flying"
        
        try:
            # Generate portrait video
            result = client.generate_video(
                prompt=prompt,
                duration=5.0,
                aspect_ratio="9:16",
                enable_audio=True,
                clip_id="test_portrait_veo3"
            )
            
            # Verify file was created
            self.assertTrue(os.path.exists(result))
            self.assertTrue(result.endswith('.mp4'))
            
            # Verify video dimensions using ffprobe (if available)
            try:
                import subprocess
                import json
                
                cmd = [
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_streams', result
                ]
                
                output = subprocess.check_output(cmd, text=True)
                video_info = json.loads(output)
                
                # Find video stream
                video_stream = None
                for stream in video_info['streams']:
                    if stream['codec_type'] == 'video':
                        video_stream = stream
                        break
                
                if video_stream:
                    width = int(video_stream['width'])
                    height = int(video_stream['height'])
                    
                    # Verify portrait orientation (height > width)
                    self.assertGreater(height, width, 
                                     f"Video should be portrait but got {width}x{height}")
                    
                    # Verify aspect ratio is close to 9:16
                    aspect_ratio = width / height
                    expected_ratio = 9 / 16
                    self.assertAlmostEqual(aspect_ratio, expected_ratio, delta=0.1,
                                         msg=f"Aspect ratio {aspect_ratio} should be close to {expected_ratio}")
                    
                    logger.info(f"✅ Generated portrait video: {width}x{height}")
                else:
                    logger.warning("Could not find video stream in ffprobe output")
                    
            except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
                logger.warning("ffprobe not available, skipping video dimension check")
                
            # Clean up
            if os.path.exists(result):
                os.remove(result)
                
        except Exception as e:
            # If VEO3 is not available, this is expected
            if "VEO3 service unavailable" in str(e):
                logger.warning("VEO3 service unavailable, skipping integration test")
                self.skipTest("VEO3 service unavailable")
            else:
                self.fail(f"VEO3 portrait generation failed: {e}")

    def test_error_handling(self):
        """Test error handling in VEO3 client"""
        client = VertexAIVeo3Client(
            project_id=self.project_id,
            location=self.location,
            gcs_bucket=self.gcs_bucket,
            output_dir=self.output_dir
        )
        
        # Test with invalid aspect ratio
        with self.assertRaises(ValueError):
            client.generate_video(
                prompt="Test video",
                duration=8.0,
                aspect_ratio="invalid:ratio"
            )
            
        # Test with invalid duration
        with self.assertRaises(ValueError):
            client.generate_video(
                prompt="Test video",
                duration=0.0,
                aspect_ratio="9:16"
            )

if __name__ == '__main__':
    unittest.main()