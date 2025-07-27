"""
Tests for Multiple Output Formats
Ensures MP4, WebM support with platform-specific encoding
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import os
from pathlib import Path
import subprocess
import json

from src.generators.video_generator import VideoGenerator
from src.core.entities import CoreDecisions, GeneratedVideoConfig
from src.config.video_config import video_config


class TestOutputFormats:
    """Test suite for video output format support"""
    
    @pytest.fixture
    def video_generator(self, mock_core_decisions, mock_session_context):
        """Create VideoGenerator instance"""
        return VideoGenerator(mock_core_decisions, mock_session_context)
    
    @pytest.mark.unit
    def test_mp4_output_generation(self, video_generator, temp_dir):
        """Test MP4 format generation with H.264 codec"""
        output_path = os.path.join(temp_dir, "test_video.mp4")
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            # Generate MP4
            video_generator._encode_video("input.mov", output_path, format="mp4")
            
            # Verify ffmpeg was called with correct parameters
            mock_subprocess.assert_called_once()
            ffmpeg_args = mock_subprocess.call_args[0][0]
            
            assert "-c:v" in ffmpeg_args
            assert "libx264" in ffmpeg_args  # H.264 codec
            assert "-c:a" in ffmpeg_args
            assert "aac" in ffmpeg_args  # AAC audio
            assert output_path in ffmpeg_args
    
    @pytest.mark.unit
    def test_webm_output_generation(self, video_generator, temp_dir):
        """Test WebM format generation with VP9 codec"""
        output_path = os.path.join(temp_dir, "test_video.webm")
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            # Generate WebM
            video_generator._encode_video("input.mov", output_path, format="webm")
            
            # Verify ffmpeg was called with correct parameters
            mock_subprocess.assert_called_once()
            ffmpeg_args = mock_subprocess.call_args[0][0]
            
            assert "-c:v" in ffmpeg_args
            assert "libvpx-vp9" in ffmpeg_args  # VP9 codec
            assert "-c:a" in ffmpeg_args
            assert "libopus" in ffmpeg_args  # Opus audio
            assert output_path in ffmpeg_args
    
    @pytest.mark.unit
    def test_platform_specific_encoding(self, video_generator):
        """Test platform-specific encoding settings"""
        platforms = {
            "youtube": {
                "resolution": "1920x1080",
                "fps": 30,
                "bitrate": "8M",
                "format": "mp4"
            },
            "instagram": {
                "resolution": "1080x1920",  # Vertical
                "fps": 30,
                "bitrate": "5M",
                "format": "mp4"
            },
            "tiktok": {
                "resolution": "1080x1920",  # Vertical
                "fps": 30,
                "bitrate": "4M",
                "format": "mp4"
            },
            "twitter": {
                "resolution": "1280x720",
                "fps": 30,
                "bitrate": "6M",
                "format": "mp4"
            }
        }
        
        for platform, expected in platforms.items():
            video_generator.decisions.target_platform = platform
            
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value = Mock(returncode=0)
                
                video_generator._encode_video("input.mov", f"{platform}.mp4")
                
                ffmpeg_args = " ".join(mock_subprocess.call_args[0][0])
                
                # Verify platform-specific settings
                assert f"-s {expected['resolution']}" in ffmpeg_args
                assert f"-r {expected['fps']}" in ffmpeg_args
                assert f"-b:v {expected['bitrate']}" in ffmpeg_args
    
    @pytest.mark.unit
    def test_encoding_quality_presets(self, video_generator):
        """Test different quality preset encodings"""
        quality_presets = {
            "low": {"crf": 28, "preset": "faster"},
            "medium": {"crf": 23, "preset": "medium"},
            "high": {"crf": 18, "preset": "slow"},
            "ultra": {"crf": 15, "preset": "slower"}
        }
        
        for quality, settings in quality_presets.items():
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value = Mock(returncode=0)
                
                video_generator._encode_video(
                    "input.mov", 
                    f"output_{quality}.mp4",
                    quality=quality
                )
                
                ffmpeg_args = " ".join(mock_subprocess.call_args[0][0])
                
                assert f"-crf {settings['crf']}" in ffmpeg_args
                assert f"-preset {settings['preset']}" in ffmpeg_args
    
    @pytest.mark.unit
    def test_audio_codec_selection(self, video_generator):
        """Test audio codec selection based on format"""
        format_audio_codecs = {
            "mp4": "aac",
            "webm": "libopus",
            "mov": "pcm_s16le",
            "avi": "mp3"
        }
        
        for format, expected_codec in format_audio_codecs.items():
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value = Mock(returncode=0)
                
                video_generator._encode_video(
                    "input.mov",
                    f"output.{format}",
                    format=format
                )
                
                ffmpeg_args = mock_subprocess.call_args[0][0]
                audio_codec_idx = ffmpeg_args.index("-c:a") + 1
                assert ffmpeg_args[audio_codec_idx] == expected_codec
    
    @pytest.mark.unit
    def test_aspect_ratio_handling(self, video_generator):
        """Test aspect ratio handling for different formats"""
        aspect_ratios = ["16:9", "9:16", "1:1", "4:3", "21:9"]
        
        for ratio in aspect_ratios:
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value = Mock(returncode=0)
                
                video_generator._encode_video(
                    "input.mov",
                    "output.mp4",
                    aspect_ratio=ratio
                )
                
                ffmpeg_args = " ".join(mock_subprocess.call_args[0][0])
                
                # Verify aspect ratio filter is applied
                assert f"setdar={ratio}" in ffmpeg_args
    
    @pytest.mark.unit
    def test_subtitle_embedding(self, video_generator, temp_dir):
        """Test embedding subtitles in different formats"""
        subtitle_file = os.path.join(temp_dir, "subtitles.srt")
        Path(subtitle_file).write_text("1\n00:00:00,000 --> 00:00:05,000\nTest subtitle")
        
        formats = ["mp4", "webm", "mov"]
        
        for format in formats:
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value = Mock(returncode=0)
                
                video_generator._encode_video(
                    "input.mov",
                    f"output.{format}",
                    format=format,
                    subtitle_file=subtitle_file
                )
                
                ffmpeg_args = mock_subprocess.call_args[0][0]
                
                # Verify subtitle embedding
                assert "-i" in ffmpeg_args
                assert subtitle_file in ffmpeg_args
                
                if format == "mp4":
                    assert "-c:s" in ffmpeg_args
                    assert "mov_text" in ffmpeg_args  # MP4 subtitle codec
    
    @pytest.mark.unit
    def test_multi_audio_track_support(self, video_generator):
        """Test multiple audio track support for different languages"""
        audio_tracks = [
            {"file": "audio_en.mp3", "language": "eng", "title": "English"},
            {"file": "audio_es.mp3", "language": "spa", "title": "Spanish"},
            {"file": "audio_fr.mp3", "language": "fra", "title": "French"}
        ]
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            video_generator._encode_video_with_multi_audio(
                "input.mov",
                "output.mp4",
                audio_tracks=audio_tracks
            )
            
            ffmpeg_args = mock_subprocess.call_args[0][0]
            
            # Verify all audio tracks are included
            for track in audio_tracks:
                assert track["file"] in ffmpeg_args
                
            # Verify metadata for tracks
            assert "-metadata:s:a:0" in ffmpeg_args
            assert "language=eng" in ffmpeg_args
    
    @pytest.mark.unit
    def test_hdr_support(self, video_generator):
        """Test HDR video encoding support"""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            video_generator._encode_video(
                "input.mov",
                "output.mp4",
                hdr=True
            )
            
            ffmpeg_args = " ".join(mock_subprocess.call_args[0][0])
            
            # Verify HDR metadata preservation
            assert "-c:v libx265" in ffmpeg_args  # H.265 for HDR
            assert "-x265-params" in ffmpeg_args
            assert "hdr10=1" in ffmpeg_args
    
    @pytest.mark.unit
    def test_format_compatibility_check(self, video_generator):
        """Test format compatibility checking"""
        # Test valid combinations
        valid_combinations = [
            ("mp4", "h264", "aac"),
            ("webm", "vp9", "opus"),
            ("mov", "prores", "pcm")
        ]
        
        for container, video_codec, audio_codec in valid_combinations:
            assert video_generator._check_format_compatibility(
                container, video_codec, audio_codec
            ) is True
        
        # Test invalid combinations
        invalid_combinations = [
            ("mp4", "vp9", "opus"),  # WebM codecs in MP4
            ("webm", "h264", "aac"),  # MP4 codecs in WebM
        ]
        
        for container, video_codec, audio_codec in invalid_combinations:
            assert video_generator._check_format_compatibility(
                container, video_codec, audio_codec
            ) is False
    
    @pytest.mark.unit
    def test_output_file_size_optimization(self, video_generator):
        """Test file size optimization for different platforms"""
        platform_limits = {
            "twitter": 512 * 1024 * 1024,  # 512MB
            "instagram": 4 * 1024 * 1024 * 1024,  # 4GB
            "tiktok": 287 * 1024 * 1024,  # 287MB
        }
        
        for platform, max_size in platform_limits.items():
            video_generator.decisions.target_platform = platform
            
            # Calculate appropriate bitrate
            bitrate = video_generator._calculate_optimal_bitrate(
                duration=60,  # 1 minute
                max_size=max_size
            )
            
            # Verify bitrate will produce file under limit
            estimated_size = (bitrate / 8) * 60  # bytes
            assert estimated_size < max_size * 0.95  # 95% to leave margin
    
    @pytest.mark.integration
    @pytest.mark.requires_ffmpeg
    def test_real_format_conversion(self, video_generator, temp_dir):
        """Test real format conversion with ffmpeg (requires ffmpeg)"""
        # Create a simple test video
        input_file = os.path.join(temp_dir, "test_input.mp4")
        
        # Generate test video with ffmpeg
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", input_file
        ], check=True)
        
        # Test conversion to different formats
        formats = ["mp4", "webm", "mov"]
        
        for format in formats:
            output_file = os.path.join(temp_dir, f"test_output.{format}")
            
            video_generator._encode_video(
                input_file,
                output_file,
                format=format
            )
            
            # Verify output exists and is valid
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
            
            # Verify format with ffprobe
            result = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=codec_name", "-of", "json", output_file
            ], capture_output=True, text=True)
            
            probe_data = json.loads(result.stdout)
            assert len(probe_data["streams"]) > 0