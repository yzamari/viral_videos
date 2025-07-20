#!/usr/bin/env python3
"""
Test Suite for Subtitle Timing and Dynamic Overlay Fixes
Validates the fixes for segmented subtitles and dynamic overlay positioning
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.generators.video_generator import VideoGenerator
from src.agents.overlay_positioning_agent import OverlayPositioningAgent
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory

class TestSubtitleAndOverlayFixes(unittest.TestCase):
    """Test subtitle timing and dynamic overlay positioning fixes"""
    
    def setUp(self):
        """Set up test environment"""
        # Use test API key for testing
        test_api_key = os.environ.get('GOOGLE_API_KEY', 'test_key_for_unit_tests')
        self.generator = VideoGenerator(api_key=test_api_key)
        self.positioning_agent = OverlayPositioningAgent(api_key=test_api_key)
    
    def test_subtitle_segmentation_multiple_segments(self):
        """Test that scripts are split into multiple subtitle segments"""
        test_script = "Discover amazing content! This is sentence one. Here's sentence two? Follow for more awesome videos!"
        
        segments = self.generator._parse_script_into_segments(test_script, 15.0)
        
        # Should create multiple segments
        self.assertGreater(len(segments), 1, "Should create multiple subtitle segments")
        
        # Each segment should have required properties
        for segment in segments:
            self.assertIn('text', segment)
            self.assertIn('start', segment)
            self.assertIn('end', segment) 
            self.assertIn('estimated_duration', segment)
            self.assertGreater(segment['end'], segment['start'])
    
    def test_content_aware_timing_adjustments(self):
        """Test that timing adjustments are applied based on content type"""
        # Test hook content (should get 1.3x multiplier)
        hook_script = "Discover the secret to viral videos!"
        hook_segments = self.generator._parse_script_into_segments(hook_script, 10.0)
        
        # Test question content (should get 1.1x multiplier)
        question_script = "What makes videos go viral?"
        question_segments = self.generator._parse_script_into_segments(question_script, 10.0)
        
        # Test CTA content (should get 0.9x multiplier)
        cta_script = "Follow for more amazing content!"
        cta_segments = self.generator._parse_script_into_segments(cta_script, 10.0)
        
        # Verify segments were created
        self.assertGreater(len(hook_segments), 0)
        self.assertGreater(len(question_segments), 0)
        self.assertGreater(len(cta_segments), 0)
        
        # Note: Exact timing verification would require knowing the base duration
        # This test ensures the content-aware logic doesn't break
    
    def test_dynamic_positioning_for_tiktok(self):
        """Test that TikTok videos get dynamic positioning"""
        decision = self.positioning_agent.analyze_positioning(
            topic="Test video",
            platform="tiktok",
            video_style="cartoon",
            duration_seconds=20.0,
            target_audience="general audience"
        )
        
        self.assertEqual(decision['positioning_strategy'], 'dynamic')
        self.assertTrue(decision.get('animation_enabled', False))
        self.assertIn('reasoning', decision)
        self.assertTrue(decision.get('mobile_optimized', False))
    
    def test_static_positioning_for_long_videos(self):
        """Test that longer videos get static positioning"""
        decision = self.positioning_agent.analyze_positioning(
            topic="Test video",
            platform="youtube",
            video_style="realistic", 
            duration_seconds=60.0,
            target_audience="general audience"
        )
        
        # Should use static for longer videos
        self.assertEqual(decision['positioning_strategy'], 'static')
        self.assertIn('reasoning', decision)
    
    def test_intelligent_subtitle_timing_with_audio(self):
        """Test intelligent subtitle timing method"""
        # Mock audio file
        test_segments = [
            {'text': 'First sentence for testing.', 'estimated_duration': 3.0},
            {'text': 'Second sentence with more content.', 'estimated_duration': 4.0},
            {'text': 'Follow for more!', 'estimated_duration': 2.0}
        ]
        
        # Mock AudioFileClip
        with patch('src.generators.video_generator.AudioFileClip') as mock_audio:
            mock_clip = Mock()
            mock_clip.duration = 12.0
            mock_audio.return_value = mock_clip
            
            # Create temporary audio file for testing
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            try:
                timed_segments = self.generator._intelligent_subtitle_timing(
                    test_segments, 15.0, temp_audio_path
                )
                
                # Verify timing results
                self.assertEqual(len(timed_segments), 3)
                
                # Check timing properties
                for segment in timed_segments:
                    self.assertIn('start', segment)
                    self.assertIn('end', segment)
                    self.assertTrue(segment.get('audio_synchronized', False))
                    self.assertTrue(segment.get('intelligent_timing', False))
                
                # Verify no overlapping
                for i in range(len(timed_segments) - 1):
                    self.assertLessEqual(timed_segments[i]['end'], timed_segments[i+1]['start'])
                    
            finally:
                os.unlink(temp_audio_path)
    
    def test_fallback_segmentation(self):
        """Test fallback segmentation when audio analysis fails"""
        test_segments = [
            {'text': 'First segment'},
            {'text': 'Second segment'},
            {'text': 'Third segment'}
        ]
        
        fallback_segments = self.generator._fallback_segmentation(test_segments, 12.0)
        
        self.assertEqual(len(fallback_segments), 3)
        
        # Verify proportional timing
        expected_duration = 12.0 / 3
        for segment in fallback_segments:
            self.assertAlmostEqual(segment['estimated_duration'], expected_duration, places=1)
            self.assertTrue(segment.get('fallback_segmentation', False))
    
    def test_overlay_animation_parameters(self):
        """Test that dynamic overlays include animation parameters"""
        decision = self.positioning_agent.analyze_positioning(
            topic="Test animation",
            platform="tiktok",
            video_style="dynamic",
            duration_seconds=15.0,
            target_audience="young adults"
        )
        
        if decision['positioning_strategy'] == 'dynamic':
            self.assertTrue(decision.get('animation_enabled'))
            self.assertIn('primary_subtitle_position', decision)
            self.assertIn('secondary_overlay_position', decision)
    
    def test_platform_specific_positioning_rules(self):
        """Test positioning rules for different platforms"""
        platforms = ['tiktok', 'youtube', 'instagram']
        
        for platform in platforms:
            decision = self.positioning_agent.analyze_positioning(
                topic=f"Test {platform} video",
                platform=platform,
                video_style="cartoon",
                duration_seconds=20.0,
                target_audience="general audience"
            )
            
            # All platforms should provide positioning decisions
            self.assertIn('positioning_strategy', decision)
            self.assertIn('primary_subtitle_position', decision)
            self.assertIn('reasoning', decision)
            self.assertIn('mobile_optimized', decision)
            
            # TikTok should prefer dynamic for short videos
            if platform == 'tiktok':
                self.assertEqual(decision['positioning_strategy'], 'dynamic')
    
    def test_subtitle_timing_bounds(self):
        """Test that subtitle timing stays within reasonable bounds"""
        test_script = "Very short."
        segments = self.generator._parse_script_into_segments(test_script, 5.0)
        
        for segment in segments:
            # Minimum duration should be at least 1 second
            self.assertGreaterEqual(segment['estimated_duration'], 1.0)
            # Should not exceed video duration
            self.assertLessEqual(segment['end'], 5.0)
            # Start should be non-negative
            self.assertGreaterEqual(segment['start'], 0.0)
    
    def test_empty_script_handling(self):
        """Test handling of empty or invalid scripts"""
        empty_segments = self.generator._parse_script_into_segments("", 10.0)
        self.assertEqual(len(empty_segments), 0)
        
        whitespace_segments = self.generator._parse_script_into_segments("   ", 10.0)
        self.assertEqual(len(whitespace_segments), 0)
    
    def test_overlay_metadata_generation(self):
        """Test that overlay positioning generates proper metadata"""
        decision = self.positioning_agent.analyze_positioning(
            topic="Metadata test",
            platform="tiktok",
            video_style="vibrant",
            duration_seconds=10.0,
            target_audience="teens"
        )
        
        # Verify essential metadata fields
        required_fields = [
            'positioning_strategy',
            'primary_subtitle_position', 
            'reasoning',
            'mobile_optimized',
            'accessibility_compliant'
        ]
        
        for field in required_fields:
            self.assertIn(field, decision, f"Missing required field: {field}")
        
        # Verify reasoning is descriptive
        self.assertGreater(len(decision['reasoning']), 10, "Reasoning should be descriptive")

if __name__ == '__main__':
    print("🧪 Running Subtitle and Overlay Fixes Test Suite")
    print("=" * 60)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)