#!/usr/bin/env python3
"""
Unit tests for FFmpeg text escaping functionality
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.generators.video_generator import VideoGenerator


class TestFFmpegEscaping(unittest.TestCase):
    """Test FFmpeg text escaping functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a VideoGenerator instance for testing (with dummy API key)
        self.video_gen = VideoGenerator(api_key="test_key", use_real_veo2=False)
    
    def test_apostrophe_escaping(self):
        """Test that apostrophes are properly escaped"""
        # Test regular apostrophe
        text = "Here's what you need"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Debug output
        print(f"Input: {repr(text)}")
        print(f"Output: {repr(escaped)}")
        
        # Should escape apostrophe but preserve the text
        self.assertNotIn("'", escaped)
        self.assertIn("Here", escaped)
        self.assertIn("what", escaped)
        self.assertIn("need", escaped)
    
    def test_unicode_apostrophes(self):
        """Test that Unicode apostrophes are handled"""
        # Test Unicode apostrophes
        text = "Here's what you'll need"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should not contain any apostrophes
        self.assertNotIn("'", escaped)
        self.assertNotIn("'", escaped)
        self.assertIn("Here", escaped)
        self.assertIn("what", escaped)
        self.assertIn("need", escaped)
    
    def test_colon_escaping(self):
        """Test that colons are properly escaped"""
        text = "Time: 5:30 PM"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should escape colons
        self.assertIn("\\:", escaped)
        self.assertIn("Time", escaped)
    
    def test_equals_escaping(self):
        """Test that equals signs are properly escaped"""
        text = "Score = 100"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should escape equals
        self.assertIn("\\=", escaped)
        self.assertIn("Score", escaped)
        self.assertIn("100", escaped)
    
    def test_comma_escaping(self):
        """Test that commas are properly escaped"""
        text = "Hello, world!"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should escape commas
        self.assertIn("\\,", escaped)
        self.assertIn("Hello", escaped)
        self.assertIn("world", escaped)
    
    def test_mixed_special_characters(self):
        """Test multiple special characters together"""
        text = "Here's the answer: Yes, it's correct!"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should not contain unescaped special chars
        self.assertNotIn("'", escaped)
        self.assertNotIn(":", escaped)
        self.assertNotIn(",", escaped)
        self.assertNotIn("!", escaped)
        
        # Should still contain the main words
        self.assertIn("Here", escaped)
        self.assertIn("answer", escaped)
        self.assertIn("Yes", escaped)
        self.assertIn("correct", escaped)
    
    def test_empty_text_handling(self):
        """Test that empty text is handled gracefully"""
        text = ""
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should return fallback text
        self.assertEqual(escaped, "Text")
    
    def test_whitespace_only_text(self):
        """Test that whitespace-only text is handled"""
        text = "   \n\t  "
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should return fallback text
        self.assertEqual(escaped, "Text")
    
    def test_realistic_hook_text(self):
        """Test with realistic hook text like from the error"""
        text = "HERE'S WHAT YOU NEED TO KNOW A"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should not contain apostrophe
        self.assertNotIn("'", escaped)
        # Should still contain the main message
        self.assertIn("HERE", escaped)
        self.assertIn("WHAT", escaped)
        self.assertIn("YOU", escaped)
        self.assertIn("NEED", escaped)
        self.assertIn("KNOW", escaped)
    
    def test_square_brackets_escaping(self):
        """Test that square brackets are properly escaped"""
        text = "Array[0] = value"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should escape square brackets
        self.assertIn("\\[", escaped)
        self.assertIn("\\]", escaped)
        self.assertIn("Array", escaped)
        self.assertIn("value", escaped)
    
    def test_newlines_converted_to_spaces(self):
        """Test that newlines are converted to spaces"""
        text = "Line 1\nLine 2\rLine 3\tTabbed"
        escaped = self.video_gen._escape_text_for_ffmpeg(text)
        
        # Should not contain newlines or tabs
        self.assertNotIn("\n", escaped)
        self.assertNotIn("\r", escaped) 
        self.assertNotIn("\t", escaped)
        
        # Should contain spaces instead
        self.assertIn("Line 1 Line 2", escaped)
        self.assertIn("Line 3 Tabbed", escaped)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)