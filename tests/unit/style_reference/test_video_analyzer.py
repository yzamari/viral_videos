"""
Unit tests for Video Style Analyzer
"""
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import asyncio

from src.style_reference.analyzers.video_style_analyzer import VideoStyleAnalyzer
from src.style_reference.models.style_attributes import ReferenceType


class TestVideoStyleAnalyzer:
    """Test video style analyzer functionality"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return VideoStyleAnalyzer()
    
    @pytest.fixture
    def sample_frames(self):
        """Create sample video frames"""
        # Create 5 sample frames (100x100 RGB)
        frames = []
        for i in range(5):
            # Create frames with different colors
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            if i == 0:
                frame[:, :] = [255, 0, 0]  # Red
            elif i == 1:
                frame[:, :] = [0, 255, 0]  # Green
            elif i == 2:
                frame[:, :] = [0, 0, 255]  # Blue
            elif i == 3:
                frame[:, :] = [255, 255, 0]  # Yellow
            else:
                frame[:, :] = [128, 128, 128]  # Gray
            frames.append(frame)
        return frames
    
    def test_color_palette_extraction(self, analyzer, sample_frames):
        """Test color palette extraction from frames"""
        palette = analyzer._analyze_color_palette(sample_frames)
        
        assert palette is not None
        assert palette.primary_color is not None
        assert palette.secondary_color is not None
        assert palette.mood is not None
        assert 0 <= palette.brightness_level <= 1
        assert 0 <= palette.saturation_level <= 1
    
    def test_brightness_calculation(self, analyzer):
        """Test brightness calculation"""
        # Test with different colors
        white = np.array([255, 255, 255])
        black = np.array([0, 0, 0])
        gray = np.array([128, 128, 128])
        
        assert analyzer._get_brightness(white) == pytest.approx(1.0)
        assert analyzer._get_brightness(black) == pytest.approx(0.0)
        assert analyzer._get_brightness(gray) == pytest.approx(0.5, rel=0.1)
    
    def test_color_mood_determination(self, analyzer):
        """Test color mood determination"""
        # Test bright colors
        bright_colors = [np.array([255, 255, 255])]
        mood = analyzer._determine_color_mood(bright_colors, 0.9, 0.1)
        assert mood == "bright"
        
        # Test dark colors
        dark_colors = [np.array([50, 50, 50])]
        mood = analyzer._determine_color_mood(dark_colors, 0.2, 0.5)
        assert mood == "dark"
        
        # Test vibrant colors
        vibrant_colors = [np.array([255, 0, 0])]
        mood = analyzer._determine_color_mood(vibrant_colors, 0.8, 0.8)
        assert mood == "vibrant"
    
    def test_motion_intensity_calculation(self, analyzer, sample_frames):
        """Test motion intensity calculation"""
        # Create frames with motion
        moving_frames = []
        for i in range(3):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            # Create moving object
            frame[i*10:(i+1)*10, i*10:(i+1)*10] = [255, 255, 255]
            moving_frames.append(frame)
        
        intensity = analyzer._calculate_motion_intensity(moving_frames)
        assert 0 <= intensity <= 1
    
    def test_scene_change_detection(self, analyzer):
        """Test scene change detection"""
        # Create frames with scene change
        frames = []
        # Scene 1: Red frames
        for _ in range(3):
            frame = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
            frames.append(frame)
        # Scene 2: Blue frames (scene change)
        for _ in range(3):
            frame = np.full((100, 100, 3), [0, 0, 255], dtype=np.uint8)
            frames.append(frame)
        
        scene_changes = analyzer._detect_scene_changes(frames)
        assert len(scene_changes) >= 1  # At least one scene change detected
    
    @patch('cv2.VideoCapture')
    def test_video_specs_extraction(self, mock_capture, analyzer):
        """Test video technical specs extraction"""
        # Mock video capture
        mock_cap = MagicMock()
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30,
            cv2.CAP_PROP_FRAME_COUNT: 900
        }.get(prop, 0)
        mock_capture.return_value = mock_cap
        
        specs = analyzer._get_video_specs("dummy_path.mp4")
        
        assert specs['width'] == 1920
        assert specs['height'] == 1080
        assert specs['resolution'] == "1920x1080"
        assert specs['aspect_ratio'] == "16:9"
        assert specs['fps'] == 30
        assert specs['duration'] == 30.0
    
    def test_blur_detection(self, analyzer):
        """Test blur detection in frames"""
        # Create sharp frame
        sharp_frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Create blurred frame
        blurred_frame = cv2.GaussianBlur(sharp_frame, (15, 15), 10)
        
        sharp_score = analyzer._detect_blur([sharp_frame])
        blur_score = analyzer._detect_blur([blurred_frame])
        
        # Blurred frame should have higher blur score
        assert blur_score > sharp_score
    
    @pytest.mark.asyncio
    @patch('cv2.VideoCapture')
    @patch.object(VideoStyleAnalyzer, '_extract_sample_frames')
    async def test_analyze_video_complete(self, mock_extract, mock_capture, analyzer, sample_frames):
        """Test complete video analysis"""
        # Mock video capture
        mock_cap = MagicMock()
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30,
            cv2.CAP_PROP_FRAME_COUNT: 900
        }.get(prop, 0)
        mock_capture.return_value = mock_cap
        
        # Mock frame extraction
        mock_extract.return_value = sample_frames
        
        # Analyze video
        style_ref = await analyzer.analyze_video("test_video.mp4", "Test Style")
        
        assert style_ref is not None
        assert style_ref.name == "Test Style"
        assert style_ref.reference_type == ReferenceType.VIDEO
        assert style_ref.color_palette is not None
        assert style_ref.motion_style is not None
        assert style_ref.aspect_ratio == "16:9"
        assert style_ref.frame_rate == 30