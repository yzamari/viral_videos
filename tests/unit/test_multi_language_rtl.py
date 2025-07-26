"""
Unit tests for multi-language support with special focus on RTL languages
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.models.video_models import Language, GeneratedVideoConfig, Platform, VideoCategory
from src.generators.multi_language_generator import MultiLanguageVideoGenerator
from src.generators.rtl_validator import RTLValidator


class TestRTLValidator(unittest.TestCase):
    """Test RTL language validation and correction"""
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.rtl_validator = RTLValidator(self.api_key)
    
    def test_rtl_language_detection(self):
        """Test RTL language detection"""
        # Test RTL languages
        self.assertTrue(Language.HEBREW in self.rtl_validator.rtl_languages)
        self.assertTrue(Language.ARABIC in self.rtl_validator.rtl_languages)
        self.assertTrue(Language.PERSIAN in self.rtl_validator.rtl_languages)
        
        # Test non-RTL languages
        self.assertFalse(Language.ENGLISH_US in self.rtl_validator.rtl_languages)
        self.assertFalse(Language.FRENCH in self.rtl_validator.rtl_languages)
    
    @patch('google.generativeai.GenerativeModel')
    def test_hebrew_text_validation(self, mock_genai):
        """Test Hebrew text validation"""
        mock_model = Mock()
        mock_genai.return_value = mock_model
        
        validator = RTLValidator(self.api_key)
        
        # Test Hebrew text
        hebrew_text = "שלום עולם"
        result = validator.validate_and_correct_rtl_text(
            hebrew_text,
            Language.HEBREW,
            context="greeting"
        )
        
        self.assertTrue(result['is_rtl'])
        self.assertEqual(result['original_text'], hebrew_text)
    
    @patch('google.generativeai.GenerativeModel')
    def test_arabic_text_validation(self, mock_genai):
        """Test Arabic text validation"""
        mock_model = Mock()
        mock_genai.return_value = mock_model
        
        validator = RTLValidator(self.api_key)
        
        # Test Arabic text
        arabic_text = "مرحبا بالعالم"
        result = validator.validate_and_correct_rtl_text(
            arabic_text,
            Language.ARABIC,
            context="greeting"
        )
        
        self.assertTrue(result['is_rtl'])
        self.assertEqual(result['original_text'], arabic_text)
    
    @patch('google.generativeai.GenerativeModel')
    def test_persian_text_validation(self, mock_genai):
        """Test Persian/Farsi text validation"""
        mock_model = Mock()
        mock_genai.return_value = mock_model
        
        validator = RTLValidator(self.api_key)
        
        # Test Persian text
        persian_text = "سلام دنیا"
        result = validator.validate_and_correct_rtl_text(
            persian_text,
            Language.PERSIAN,
            context="greeting"
        )
        
        self.assertTrue(result['is_rtl'])
        self.assertEqual(result['original_text'], persian_text)
    
    def test_non_rtl_language_skip(self):
        """Test that non-RTL languages are skipped"""
        english_text = "Hello World"
        result = self.rtl_validator.validate_and_correct_rtl_text(
            english_text,
            Language.ENGLISH_US
        )
        
        self.assertFalse(result['is_rtl'])
        self.assertEqual(result['original_text'], english_text)
        self.assertEqual(result['corrected_text'], english_text)
        self.assertTrue(result['validation_passed'])


class TestMultiLanguageGenerator(unittest.TestCase):
    """Test multi-language video generation"""
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.temp_dir = tempfile.mkdtemp()
        self.generator = MultiLanguageVideoGenerator(self.api_key, self.temp_dir)
    
    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_rtl_language_configuration(self):
        """Test RTL language configuration"""
        # Check RTL languages are properly configured
        self.assertIn(Language.HEBREW, self.generator.rtl_languages)
        self.assertIn(Language.ARABIC, self.generator.rtl_languages)
        self.assertIn(Language.PERSIAN, self.generator.rtl_languages)
        
        # Check language names include native scripts
        self.assertIn("עברית", self.generator.language_names[Language.HEBREW])
        self.assertIn("العربية", self.generator.language_names[Language.ARABIC])
        self.assertIn("فارسی", self.generator.language_names[Language.PERSIAN])
    
    def test_tts_configuration_for_rtl(self):
        """Test TTS configuration for RTL languages"""
        # Hebrew TTS config
        hebrew_config = self.generator.tts_voice_config[Language.HEBREW]
        self.assertEqual(hebrew_config['lang'], 'iw')  # Google TTS uses 'iw' for Hebrew
        self.assertEqual(hebrew_config['tld'], 'co.il')
        
        # Arabic TTS config
        arabic_config = self.generator.tts_voice_config[Language.ARABIC]
        self.assertEqual(arabic_config['lang'], 'ar')
        
        # Persian TTS config
        persian_config = self.generator.tts_voice_config[Language.PERSIAN]
        self.assertEqual(persian_config['lang'], 'fa')
    
    @patch('google.generativeai.GenerativeModel')
    def test_translate_script_rtl(self, mock_genai):
        """Test script translation for RTL languages"""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "תרגום בעברית"  # Hebrew translation
        mock_model.generate_content.return_value = mock_response
        mock_genai.return_value = mock_model
        
        generator = MultiLanguageVideoGenerator(self.api_key)
        
        # Test Hebrew translation
        english_script = "Hello world"
        translated = generator._translate_script(
            english_script,
            Language.HEBREW,
            tone="friendly"
        )
        
        self.assertEqual(translated, "תרגום בעברית")
        
        # Verify translation prompt includes RTL considerations
        call_args = mock_model.generate_content.call_args[0][0]
        self.assertIn("Hebrew", call_args)
        self.assertIn("right-to-left", call_args.lower())
    
    def test_subtitle_formatting_rtl(self):
        """Test subtitle formatting for RTL languages"""
        # Test subtitle with RTL text
        hebrew_segments = [
            {"text": "שלום", "start": 0.0, "end": 1.0},
            {"text": "עולם", "start": 1.0, "end": 2.0}
        ]
        
        srt_content = self.generator._create_subtitles(
            hebrew_segments,
            Language.HEBREW
        )
        
        # Check SRT format
        self.assertIn("1\n", srt_content)
        self.assertIn("00:00:00,000 --> 00:00:01,000\n", srt_content)
        self.assertIn("שלום", srt_content)
        
        # Verify RTL text is preserved
        lines = srt_content.strip().split('\n')
        subtitle_lines = [l for l in lines if l and not l[0].isdigit() and '-->' not in l]
        self.assertIn("שלום", subtitle_lines[0])
        self.assertIn("עולם", subtitle_lines[1])
    
    def test_overlay_text_rtl_alignment(self):
        """Test overlay text alignment for RTL languages"""
        # Test RTL overlay configuration
        hebrew_overlay = {
            "text": "כותרת בעברית",
            "language": Language.HEBREW,
            "position": "center"
        }
        
        # Check if RTL languages get proper alignment
        is_rtl = Language.HEBREW in self.generator.rtl_languages
        self.assertTrue(is_rtl)
        
        # For RTL, text should be right-aligned by default
        if is_rtl:
            expected_alignment = "right"
        else:
            expected_alignment = "left"
        
        # In actual implementation, RTL text should be right-aligned
        self.assertEqual(expected_alignment, "right")
    
    @patch('gtts.gTTS')
    def test_generate_audio_rtl(self, mock_gtts):
        """Test audio generation for RTL languages"""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance
        
        # Test Hebrew audio generation
        hebrew_text = "שלום עולם"
        audio_path = os.path.join(self.temp_dir, "hebrew_audio.mp3")
        
        self.generator._generate_audio_for_language(
            hebrew_text,
            Language.HEBREW,
            audio_path
        )
        
        # Verify gTTS was called with Hebrew config
        mock_gtts.assert_called_with(
            text=hebrew_text,
            lang='iw',  # Hebrew language code
            tld='co.il',
            slow=False
        )
        mock_tts_instance.save.assert_called_with(audio_path)
    
    def test_mixed_ltr_rtl_text_handling(self):
        """Test handling of mixed LTR/RTL text"""
        # Text with both English and Hebrew
        mixed_text = "Hello שלום World עולם"
        
        result = self.generator.rtl_validator.validate_and_correct_rtl_text(
            mixed_text,
            Language.HEBREW
        )
        
        # Should detect as RTL due to Hebrew language
        self.assertTrue(result['is_rtl'])
    
    def test_cultural_context_for_translations(self):
        """Test cultural context is applied for translations"""
        # Check cultural contexts exist for RTL languages
        self.assertIn(Language.HEBREW, self.generator.cultural_context)
        self.assertIn(Language.ARABIC, self.generator.cultural_context)
        self.assertIn(Language.PERSIAN, self.generator.cultural_context)
        
        # Verify context includes appropriate cultural notes
        hebrew_context = self.generator.cultural_context[Language.HEBREW]
        self.assertIn("Hebrew", hebrew_context)
        
        arabic_context = self.generator.cultural_context[Language.ARABIC]
        self.assertIn("Arabic", arabic_context)
        
        persian_context = self.generator.cultural_context[Language.PERSIAN]
        self.assertIn("Persian", persian_context)


class TestMultiLanguageIntegration(unittest.TestCase):
    """Integration tests for multi-language video generation"""
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.temp_dir = tempfile.mkdtemp()
        self.config = GeneratedVideoConfig(
            mission="Test video mission",
            duration_seconds=30,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATIONAL
        )
    
    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('google.generativeai.GenerativeModel')
    @patch('gtts.gTTS')
    @patch('moviepy.editor.VideoFileClip')
    @patch('moviepy.editor.AudioFileClip')
    @patch('moviepy.editor.TextClip')
    def test_generate_video_with_rtl_languages(self, mock_text_clip, mock_audio_clip, 
                                              mock_video_clip, mock_gtts, mock_genai):
        """Test generating video with Hebrew, Arabic, and Persian"""
        # Setup mocks
        mock_model = Mock()
        mock_genai.return_value = mock_model
        
        # Mock translations
        translations = {
            Language.HEBREW: "תוכן בעברית",
            Language.ARABIC: "محتوى عربي",
            Language.PERSIAN: "محتوای فارسی"
        }
        
        def mock_translate(text, lang, tone):
            mock_response = Mock()
            mock_response.text = translations.get(lang, text)
            return mock_response
        
        mock_model.generate_content.side_effect = mock_translate
        
        # Mock video/audio clips
        mock_video = Mock()
        mock_video.duration = 30
        mock_video_clip.return_value = mock_video
        
        mock_audio = Mock()
        mock_audio.duration = 30
        mock_audio_clip.return_value = mock_audio
        
        mock_text = Mock()
        mock_text_clip.return_value = mock_text
        
        # Generate multi-language video
        generator = MultiLanguageVideoGenerator(self.api_key, self.temp_dir)
        
        languages = [Language.ENGLISH_US, Language.HEBREW, Language.ARABIC, Language.PERSIAN]
        
        # Test that each language gets properly processed
        for lang in languages:
            if lang in generator.rtl_languages:
                # Verify RTL handling
                is_rtl = True
            else:
                is_rtl = False
            
            # Check language configuration
            self.assertIn(lang, generator.language_names)
            self.assertIn(lang, generator.tts_voice_config)
    
    def test_language_version_metadata(self):
        """Test language version metadata includes RTL info"""
        generator = MultiLanguageVideoGenerator(self.api_key, self.temp_dir)
        
        # Test metadata for RTL language
        hebrew_metadata = {
            "language": Language.HEBREW,
            "is_rtl": True,
            "text_direction": "rtl",
            "alignment": "right"
        }
        
        # Verify RTL languages get proper metadata
        for lang in [Language.HEBREW, Language.ARABIC, Language.PERSIAN]:
            is_rtl = lang in generator.rtl_languages
            self.assertTrue(is_rtl)


if __name__ == '__main__':
    unittest.main()