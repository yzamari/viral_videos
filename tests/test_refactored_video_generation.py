"""
Test Suite for Refactored Video Generation
Validates the fixes for audio-subtitle sync, stuttering, and duration mismatches
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

# Import refactored components
from src.core.duration_authority import DurationAuthority, ComponentType, DurationContract
from src.utils.audio_first_subtitle_generator import AudioFirstSubtitleGenerator
from src.utils.simplified_audio_processor import SimplifiedAudioProcessor
from src.generators.refactored_video_generator import RefactoredVideoGenerator

# Import existing models
from src.models.video_models import GeneratedVideoConfig, Platform, Language
from src.utils.session_context import SessionContext


class TestDurationAuthority:
    """Test the centralized duration authority"""
    
    def test_duration_authority_initialization(self):
        """Test Duration Authority initializes correctly"""
        target_duration = 30.0
        authority = DurationAuthority(target_duration, tolerance_percent=0.1)
        
        assert authority.target_duration == 30.0
        assert authority.min_allowed == 27.0  # 30 * 0.9
        assert authority.max_allowed == 33.0  # 30 * 1.1
        assert authority.tolerance_percent == 0.1
        
    def test_generation_constraints(self):
        """Test generation constraints calculation"""
        authority = DurationAuthority(30.0)
        constraints = authority.get_generation_constraints()
        
        # Should calculate reasonable constraints
        assert constraints['target_duration'] == 30.0
        assert constraints['max_words'] > 0
        assert constraints['max_segments'] > 0
        assert constraints['max_clips'] > 0
        assert constraints['words_per_second'] == 2.3
        
    def test_component_duration_registration(self):
        """Test registering component durations"""
        authority = DurationAuthority(30.0)
        
        # Register within tolerance
        is_valid = authority.register_component_duration(
            ComponentType.SCRIPT, 29.5, confidence=0.8
        )
        assert is_valid is True
        assert ComponentType.SCRIPT in authority.component_durations
        assert authority.component_durations[ComponentType.SCRIPT] == 29.5
        
        # Register exceeding tolerance
        is_valid = authority.register_component_duration(
            ComponentType.AUDIO, 35.0, confidence=1.0
        )
        assert is_valid is False
        
    def test_final_duration_recommendation(self):
        """Test final duration recommendation logic"""
        authority = DurationAuthority(30.0, tolerance_percent=0.1)
        
        # Register audio (highest priority)
        authority.register_component_duration(ComponentType.AUDIO, 29.0, confidence=1.0)
        authority.register_component_duration(ComponentType.SCRIPT, 31.0, confidence=0.7)
        
        # Should prioritize audio duration
        recommended = authority.get_final_duration_recommendation()
        assert recommended == 29.0
        
    def test_validation(self):
        """Test final result validation"""
        authority = DurationAuthority(30.0, tolerance_percent=0.05)
        
        # Register valid durations
        authority.register_component_duration(ComponentType.AUDIO, 29.8, confidence=1.0)
        authority.register_component_duration(ComponentType.SUBTITLES, 29.8, confidence=1.0)
        
        is_valid, issues = authority.validate_final_result()
        assert is_valid is True
        assert len(issues) == 0
        
    def test_duration_contract(self):
        """Test duration contract enforcement"""
        authority = DurationAuthority(30.0)
        contract = authority.create_duration_contract()
        
        # Test script enforcement
        long_script = "This is a very long script " * 100
        estimated_duration = 45.0  # Exceeds 30s target
        
        trimmed_script = contract.enforce_on_script(long_script, estimated_duration)
        assert len(trimmed_script) < len(long_script)
        

class TestAudioFirstSubtitleGenerator:
    """Test audio-first subtitle generation"""
    
    @pytest.fixture
    def subtitle_generator(self):
        return AudioFirstSubtitleGenerator(padding_between_segments=0.3)
        
    @pytest.fixture
    def mock_audio_files(self, tmp_path):
        """Create mock audio files for testing"""
        audio_files = []
        for i in range(3):
            audio_file = tmp_path / f"audio_{i}.mp3"
            # Create empty file (in real test would be actual audio)
            audio_file.write_bytes(b"fake_audio_content")
            audio_files.append(str(audio_file))
        return audio_files
        
    def test_subtitle_generator_initialization(self, subtitle_generator):
        """Test subtitle generator initializes correctly"""
        assert subtitle_generator.padding_between_segments == 0.3
        
    @patch('subprocess.run')
    def test_get_audio_duration(self, mock_subprocess, subtitle_generator, tmp_path):
        """Test getting audio duration from file"""
        # Mock ffprobe output
        mock_subprocess.return_value.stdout = "3.456"
        mock_subprocess.return_value.returncode = 0
        
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake_audio")
        
        duration = subtitle_generator.get_audio_duration(str(audio_file))
        assert duration == 3.456
        
    @patch.object(AudioFirstSubtitleGenerator, 'get_audio_duration')
    def test_analyze_audio_segments(self, mock_duration, subtitle_generator):
        """Test analyzing audio segments"""
        # Mock durations for 3 audio files
        mock_duration.side_effect = [2.5, 3.2, 1.8]
        
        audio_files = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]
        script_segments = [
            {"text": "First segment"},
            {"text": "Second segment"},
            {"text": "Third segment"}
        ]
        
        segments = subtitle_generator.analyze_audio_segments(audio_files, script_segments)
        
        assert len(segments) == 3
        assert segments[0].duration == 2.5
        assert segments[0].start_time == 0.0
        assert segments[0].end_time == 2.5
        
        # Second segment should start after first + padding
        assert segments[1].start_time == 2.5 + 0.3  # 2.8
        assert segments[1].end_time == 2.8 + 3.2    # 6.0
        
    def test_format_subtitle_text(self, subtitle_generator):
        """Test subtitle text formatting"""
        long_text = "This is a very long subtitle text that should be split into multiple lines"
        formatted = subtitle_generator.format_subtitle_text(long_text, max_chars_per_line=20)
        
        lines = formatted.split('\n')
        assert len(lines) <= 2  # Max lines
        for line in lines:
            assert len(line) <= 20  # Max chars per line
            

class TestSimplifiedAudioProcessor:
    """Test simplified audio processing"""
    
    @pytest.fixture
    def audio_processor(self):
        return SimplifiedAudioProcessor()
        
    @patch('subprocess.run')
    def test_get_audio_info(self, mock_subprocess, audio_processor, tmp_path):
        """Test getting audio file information"""
        # Mock ffprobe JSON output
        mock_output = {
            "format": {"duration": "3.456"},
            "streams": [{
                "codec_type": "audio",
                "sample_rate": "44100",
                "channels": 2,
                "codec_name": "aac",
                "bit_rate": "128000"
            }]
        }
        
        import json
        mock_subprocess.return_value.stdout = json.dumps(mock_output)
        mock_subprocess.return_value.returncode = 0
        
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake_audio")
        
        info = audio_processor.get_audio_info(str(audio_file))
        
        assert info['duration'] == 3.456
        assert info['sample_rate'] == 44100
        assert info['channels'] == 2
        assert info['codec'] == 'aac'
        
    def test_validate_audio_files(self, audio_processor, tmp_path):
        """Test audio file validation"""
        # Create valid file
        valid_file = tmp_path / "valid.mp3"
        valid_file.write_bytes(b"fake_audio_content")
        
        # Create empty file
        empty_file = tmp_path / "empty.mp3"
        empty_file.write_bytes(b"")
        
        # Non-existent file
        missing_file = str(tmp_path / "missing.mp3")
        
        with patch.object(audio_processor, 'get_audio_info') as mock_info:
            # Mock valid file info
            mock_info.return_value = {'duration': 3.0}
            
            audio_files = [str(valid_file), str(empty_file), missing_file]
            valid, invalid = audio_processor.validate_audio_files(audio_files)
            
            assert len(valid) == 1
            assert str(valid_file) in valid
            assert len(invalid) == 2
            

class TestIntegration:
    """Integration tests for the complete refactored system"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock video configuration"""
        config = Mock(spec=GeneratedVideoConfig)
        config.mission = "Test video generation"
        config.duration_seconds = 15.0
        config.target_platform = Platform.INSTAGRAM
        config.language = Language.ENGLISH_US
        return config
        
    @pytest.fixture
    def mock_session_context(self, tmp_path):
        """Create mock session context"""
        session = Mock(spec=SessionContext)
        session.get_output_path = lambda *args: str(tmp_path / "_".join(args))
        return session
        
    @pytest.mark.asyncio
    async def test_duration_constraint_flow(self, mock_config, mock_session_context):
        """Test that duration constraints flow through the system"""
        # This would be a full integration test
        # For now, just test the constraint calculation
        
        authority = DurationAuthority(mock_config.duration_seconds)
        constraints = authority.get_generation_constraints()
        
        # Verify constraints are reasonable for 15s video
        assert constraints['target_duration'] == 15.0
        assert constraints['max_words'] <= 35  # Conservative for 15s
        assert constraints['max_segments'] >= 3   # At least 3 segments
        assert constraints['max_clips'] >= 2      # At least 2 clips
        
    @pytest.mark.asyncio  
    async def test_audio_first_subtitle_pipeline(self):
        """Test the audio-first subtitle generation pipeline"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            generator = AudioFirstSubtitleGenerator()
            
            # Mock audio files and script segments
            audio_files = []
            script_segments = []
            
            for i in range(2):
                # Create mock audio file
                audio_file = os.path.join(tmp_dir, f"segment_{i}.mp3")
                with open(audio_file, 'wb') as f:
                    f.write(b"fake_audio_content")
                audio_files.append(audio_file)
                
                # Create script segment
                script_segments.append({
                    'text': f"This is test segment number {i+1}",
                    'duration': 2.5  # This will be ignored - actual audio duration used
                })
            
            # Mock the duration getter to return known values
            with patch.object(generator, 'get_audio_duration') as mock_duration:
                mock_duration.side_effect = [2.3, 3.1]  # Different from script estimates
                
                # Generate subtitles
                srt_path, vtt_path, segments = generator.generate_subtitles(
                    audio_files, script_segments, tmp_dir, "test_subtitles"
                )
                
                # Verify files were created
                assert os.path.exists(srt_path)
                assert os.path.exists(vtt_path)
                
                # Verify timing uses actual audio durations, not estimates
                assert len(segments) == 2
                assert segments[0].start == 0.0
                assert segments[0].end == 2.3  # Uses actual, not estimated 2.5
                assert segments[1].start == 2.3  # Starts after first segment
                assert segments[1].end == 5.4   # 2.3 + 3.1
                

def test_sync_quality_calculation():
    """Test sync quality score calculation"""
    authority = DurationAuthority(30.0)
    
    # Perfect sync - audio and subtitles match exactly
    authority.register_component_duration(ComponentType.AUDIO, 29.5, confidence=1.0)
    authority.register_component_duration(ComponentType.SUBTITLES, 29.5, confidence=1.0)
    
    # Create a generator to test the sync calculation method
    generator = RefactoredVideoGenerator("fake_api_key")
    sync_score = generator._calculate_sync_quality_score(authority)
    
    assert sync_score == 1.0  # Perfect sync
    
    # Test with slight mismatch
    authority.component_durations[ComponentType.SUBTITLES] = 29.7  # 0.2s difference
    sync_score = generator._calculate_sync_quality_score(authority)
    
    assert sync_score >= 0.8  # Still good sync within 500ms


if __name__ == "__main__":
    # Run specific tests
    pytest.main([__file__, "-v"])