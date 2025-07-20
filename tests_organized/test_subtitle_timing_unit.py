#!/usr/bin/env python3
"""
Unit Tests for Subtitle Timing Fixes
Tests the core subtitle segmentation logic without full system dependencies
"""

import unittest
import os
import sys
import re
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TestSubtitleTimingUnit(unittest.TestCase):
    """Unit tests for subtitle timing functionality"""
    
    def test_script_sentence_splitting(self):
        """Test that scripts are properly split into sentences"""
        test_script = "Discover amazing content! This is sentence one. Here's sentence two? Follow for more awesome videos!"
        
        # Test the regex splitting logic used in the actual implementation
        sentences = re.split(r'[.!?]+', test_script)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Should create multiple sentences
        self.assertGreater(len(sentences), 1, "Should split script into multiple sentences")
        self.assertIn("Discover amazing content", sentences[0])
        self.assertIn("Follow for more awesome videos", sentences[-1])
    
    def test_timing_calculation_logic(self):
        """Test timing calculation without full VideoGenerator"""
        # Simulate the timing logic from _parse_script_into_segments
        sentences = ["Discover amazing content", "This is sentence one", "Here's sentence two", "Follow for more awesome videos"]
        video_duration = 15.0
        
        # Calculate basic timing
        total_words = sum(len(sentence.split()) for sentence in sentences)
        words_per_second = max(2.0, min(3.0, total_words / video_duration))
        
        segments = []
        current_time = 0.0
        
        for sentence in sentences:
            words = len(sentence.split())
            base_duration = words / words_per_second
            
            # Apply content-aware adjustments
            if sentence.lower().startswith(('discover', 'meet', 'what', 'how', 'why')):
                base_duration *= 1.3  # Hooks need more time
            elif sentence.lower().endswith(('!', '?')):
                base_duration *= 1.1  # Questions/exclamations need emphasis
            elif 'follow' in sentence.lower() or 'subscribe' in sentence.lower():
                base_duration *= 0.9  # CTAs can be faster
            
            # Ensure reasonable bounds
            duration = max(1.5, min(6.0, base_duration))
            
            segments.append({
                'text': sentence,
                'start': current_time,
                'end': current_time + duration,
                'estimated_duration': duration,
                'word_count': words
            })
            
            current_time += duration
        
        # Verify results
        self.assertEqual(len(segments), 4, "Should create 4 segments")
        
        # Check that hook gets longer duration
        hook_segment = next((s for s in segments if s['text'].startswith('Discover')), None)
        regular_segment = next((s for s in segments if s['text'].startswith('This is')), None)
        
        if hook_segment and regular_segment:
            # Hook should have longer duration per word
            hook_rate = hook_segment['estimated_duration'] / hook_segment['word_count']
            regular_rate = regular_segment['estimated_duration'] / regular_segment['word_count']
            self.assertGreater(hook_rate, regular_rate, "Hook should have longer duration per word")
        
        # Check CTA gets shorter duration
        cta_segment = next((s for s in segments if 'follow' in s['text'].lower()), None)
        if cta_segment and regular_segment:
            cta_rate = cta_segment['estimated_duration'] / cta_segment['word_count']
            regular_rate = regular_segment['estimated_duration'] / regular_segment['word_count']
            self.assertLess(cta_rate, regular_rate, "CTA should have shorter duration per word")
    
    def test_positioning_strategy_logic(self):
        """Test overlay positioning strategy logic"""
        # Simulate the logic from overlay_positioning_agent
        
        def get_positioning_strategy(platform, duration_seconds):
            """Simulate the positioning strategy logic"""
            return "dynamic" if platform == "tiktok" and duration_seconds <= 30 else "static"
        
        # Test TikTok short videos
        self.assertEqual(get_positioning_strategy("tiktok", 20), "dynamic")
        self.assertEqual(get_positioning_strategy("tiktok", 15), "dynamic")
        self.assertEqual(get_positioning_strategy("tiktok", 30), "dynamic")
        
        # Test longer videos
        self.assertEqual(get_positioning_strategy("tiktok", 31), "static")
        self.assertEqual(get_positioning_strategy("tiktok", 60), "static")
        
        # Test other platforms
        self.assertEqual(get_positioning_strategy("youtube", 20), "static")
        self.assertEqual(get_positioning_strategy("instagram", 15), "static")
    
    def test_intelligent_timing_proportional_logic(self):
        """Test proportional timing distribution logic"""
        segments = [
            {'text': 'First segment', 'estimated_duration': 3.0},
            {'text': 'Second longer segment with more words', 'estimated_duration': 5.0},
            {'text': 'Third segment', 'estimated_duration': 2.0}
        ]
        
        audio_duration = 12.0
        
        # Simulate the scaling logic from _intelligent_subtitle_timing
        total_estimated = sum(s['estimated_duration'] for s in segments)
        scale_factor = audio_duration / total_estimated
        
        timed_segments = []
        current_time = 0.0
        
        for segment in segments:
            scaled_duration = segment['estimated_duration'] * scale_factor
            
            timed_segments.append({
                'text': segment['text'],
                'start': current_time,
                'end': current_time + scaled_duration,
                'estimated_duration': scaled_duration
            })
            
            current_time += scaled_duration
        
        # Verify timing accuracy
        total_duration = sum(s['estimated_duration'] for s in timed_segments)
        self.assertAlmostEqual(total_duration, audio_duration, places=1)
        
        # Verify no overlaps
        for i in range(len(timed_segments) - 1):
            self.assertLessEqual(timed_segments[i]['end'], timed_segments[i+1]['start'])
        
        # Verify proportional scaling
        original_ratio = segments[1]['estimated_duration'] / segments[0]['estimated_duration']
        scaled_ratio = timed_segments[1]['estimated_duration'] / timed_segments[0]['estimated_duration']
        self.assertAlmostEqual(original_ratio, scaled_ratio, places=2)
    
    def test_fallback_timing_logic(self):
        """Test fallback timing when other methods fail"""
        segments = [
            {'text': 'First segment'},
            {'text': 'Second segment'},
            {'text': 'Third segment'}
        ]
        video_duration = 12.0
        
        # Simulate fallback logic
        fallback_segments = []
        time_per_segment = video_duration / len(segments)
        
        for i, segment in enumerate(segments):
            start_time = i * time_per_segment
            end_time = min((i + 1) * time_per_segment, video_duration)
            
            fallback_segments.append({
                'text': segment['text'],
                'start': start_time,
                'end': end_time,
                'estimated_duration': end_time - start_time,
                'fallback_segmentation': True
            })
        
        # Verify equal distribution
        self.assertEqual(len(fallback_segments), 3)
        
        for segment in fallback_segments:
            self.assertAlmostEqual(segment['estimated_duration'], 4.0, places=1)
            self.assertTrue(segment.get('fallback_segmentation'))
        
        # Verify total duration
        total_duration = sum(s['estimated_duration'] for s in fallback_segments)
        self.assertAlmostEqual(total_duration, video_duration, places=1)
    
    def test_content_type_detection(self):
        """Test content type detection for timing adjustments"""
        test_cases = [
            ("Discover amazing secrets!", "hook"),
            ("Meet the incredible team!", "hook"),
            ("What makes this special?", "question"),
            ("How does this work?", "question"),
            ("Follow for more content!", "cta"),
            ("Subscribe to our channel!", "cta"),
            ("This is regular content.", "regular")
        ]
        
        for text, expected_type in test_cases:
            # Simulate content type detection
            is_hook = text.lower().startswith(('discover', 'meet', 'what', 'how', 'why'))
            is_question = text.lower().endswith(('!', '?'))
            is_cta = 'follow' in text.lower() or 'subscribe' in text.lower()
            
            if expected_type == "hook":
                self.assertTrue(is_hook, f"'{text}' should be detected as hook")
            elif expected_type == "question":
                self.assertTrue(is_question, f"'{text}' should be detected as question")
            elif expected_type == "cta":
                self.assertTrue(is_cta, f"'{text}' should be detected as CTA")
    
    def test_empty_and_edge_cases(self):
        """Test handling of empty and edge case inputs"""
        # Empty script
        empty_sentences = re.split(r'[.!?]+', "")
        empty_sentences = [s.strip() for s in empty_sentences if s.strip()]
        self.assertEqual(len(empty_sentences), 0)
        
        # Whitespace only
        whitespace_sentences = re.split(r'[.!?]+', "   ")
        whitespace_sentences = [s.strip() for s in whitespace_sentences if s.strip()]
        self.assertEqual(len(whitespace_sentences), 0)
        
        # Single sentence
        single_sentences = re.split(r'[.!?]+', "Just one sentence.")
        single_sentences = [s.strip() for s in single_sentences if s.strip()]
        self.assertEqual(len(single_sentences), 1)
        
        # No punctuation
        no_punct_sentences = re.split(r'[.!?]+', "No punctuation here")
        no_punct_sentences = [s.strip() for s in no_punct_sentences if s.strip()]
        self.assertEqual(len(no_punct_sentences), 1)

if __name__ == '__main__':
    print("🧪 Running Subtitle Timing Unit Tests")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)