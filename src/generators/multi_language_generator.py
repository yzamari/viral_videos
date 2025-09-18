"""
Multi-language video generator - Generate same video in multiple languages with RTL support
"""
import os

from datetime import datetime
from typing import List, Dict, Optional
import uuid
import google.generativeai as genai
from gtts  import gTTS
from moviepy.editor import *

import time
import re # Added for Hebrew TTS

from ..models.video_models import (
    GeneratedVideoConfig, MultiLanguageVideo, LanguageVersion,
    Language, TTSVoice
)
from ..utils.logging_config import get_logger
from .video_generator import VideoGenerator
from ..config.ai_model_config import DEFAULT_AI_MODEL

logger = get_logger(__name__)

class MultiLanguageVideoGenerator:
    """Generate the same video content in multiple languages with RTL support"""

    def __init__(self, api_key: str, output_dir: str = "outputs"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.translation_model = genai.GenerativeModel(DEFAULT_AI_MODEL)
        genai.configure(api_key=api_key)

        # Enhanced language configuration with proper display names
        self.language_names = {
            # English variants
            Language.ENGLISH_US: "American English",
            Language.ENGLISH_UK: "British English",
            Language.ENGLISH_IN: "Indian English",

            # European languages
            Language.FRENCH: "French (Français)",
            Language.GERMAN: "German (Deutsch)",

            # Middle Eastern languages (RTL)
            Language.ARABIC: "Arabic (العربية)",
            Language.PERSIAN: "Persian (فارسی)",
            Language.HEBREW: "Hebrew (עברית)",

            # Asian languages
            Language.THAI: "Thai (ไทย)",

            # Additional languages
            Language.SPANISH: "Spanish (Español)",
            Language.ITALIAN: "Italian (Italiano)",
            Language.PORTUGUESE: "Portuguese (Português)",
            Language.RUSSIAN: "Russian (Русский)",
            Language.CHINESE: "Chinese (中文)",
            Language.JAPANESE: "Japanese (日本語)"
        }

        # RTL language detection
        self.rtl_languages = {
            Language.ARABIC, Language.PERSIAN, Language.HEBREW
        }

        # Enhanced TTS configuration with proper language codes
        self.tts_voice_config = {
            # English variants
            Language.ENGLISH_US: {'lang': 'en', 'tld': 'com', 'slow': False},
            Language.ENGLISH_UK: {'lang': 'en', 'tld': 'co.uk', 'slow': False},
            Language.ENGLISH_IN: {'lang': 'en', 'tld': 'co.in', 'slow': False},

            # European languages
            Language.FRENCH: {'lang': 'fr', 'tld': 'fr', 'slow': False},
            Language.GERMAN: {'lang': 'de', 'tld': 'de', 'slow': False},

            # Middle Eastern languages (RTL)
            Language.ARABIC: {'lang': 'ar', 'tld': 'com', 'slow': False},
            Language.PERSIAN: {'lang': 'fa', 'tld': 'com', 'slow': False},  # Persian/Farsi
            Language.HEBREW: {'lang': 'iw', 'tld': 'co.il', 'slow': False},

            # Asian languages
            Language.THAI: {'lang': 'th', 'tld': 'com', 'slow': False},

            # Additional languages
            Language.SPANISH: {'lang': 'es', 'tld': 'es', 'slow': False},
            Language.ITALIAN: {'lang': 'it', 'tld': 'it', 'slow': False},
            Language.PORTUGUESE: {'lang': 'pt', 'tld': 'com.br', 'slow': False},
            Language.RUSSIAN: {'lang': 'ru', 'tld': 'ru', 'slow': False},
            Language.CHINESE: {'lang': 'zh', 'tld': 'cn', 'slow': False},
            Language.JAPANESE: {'lang': 'ja', 'tld': 'jp', 'slow': False}
        }

        # Cultural context for better translations
        self.cultural_context = {
            Language.ENGLISH_US: "American culture, casual tone, American expressions",
            Language.ENGLISH_UK: "British culture, formal tone, British expressions",
            Language.ENGLISH_IN: "Indian culture, respectful tone, Indian English expressions",
            Language.FRENCH: "French culture, elegant tone, French expressions",
            Language.GERMAN: "German culture, direct tone, German expressions",
            Language.ARABIC: "Arabic culture, respectful tone, Middle Eastern context",
            Language.PERSIAN: "Persian culture, poetic tone, Iranian context",
            Language.HEBREW: "Hebrew culture, modern Israeli context",
            Language.THAI: "Thai culture, polite tone, Thai expressions",
            Language.SPANISH: "Spanish culture, warm tone, Spanish expressions",
            Language.ITALIAN: "Italian culture, expressive tone, Italian expressions",
            Language.PORTUGUESE: "Portuguese/Brazilian culture, friendly tone",
            Language.RUSSIAN: "Russian culture, formal tone, Russian expressions",
            Language.CHINESE: "Chinese culture, respectful tone, Chinese expressions",
            Language.JAPANESE: "Japanese culture, polite tone, Japanese expressions"
        }

        logger.info(f"🌍 Multi-language generator initialized with {len(self.language_names)} languages")
        logger.info(f"📜 RTL support enabled for: {', '.join([self.language_names[lang] for lang in self.rtl_languages])}")

    def generate_multilingual_video(self, config: GeneratedVideoConfig,
                                  selected_languages: List[Language]) -> MultiLanguageVideo:
        """Generate video in multiple selected languages with shared video clips"""
        start_time = time.time()

        # Validate selected languages
        valid_languages = []
        for lang in selected_languages:
            if lang in self.language_names:
                valid_languages.append(lang)
            else:
                logger.warning(f"⚠️ Language {lang} not supported, skipping...")

        if not valid_languages:
            raise ValueError("No valid languages selected for multi-language generation")

        # Set configuration for TTS generation
        self.use_realistic_audio = getattr(config, 'realistic_audio', False)
        self.current_feeling = getattr(config, 'feeling', 'neutral')
        self.current_narrative = getattr(config, 'narrative', 'neutral')

        logger.info(f"🌍 Generating multilingual video for {len(valid_languages)} languages:")
        logger.info(f"   Languages: {', '.join([self.language_names[lang] for lang in valid_languages])}")
        logger.info(f"🎤 Realistic audio: {'Yes' if self.use_realistic_audio else 'No'}")

        base_video_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(
            "outputs",
            f"multilang_{timestamp}_{base_video_id[:8]}")
        shared_clips_dir = os.path.join(session_dir, "shared_clips")

        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(shared_clips_dir, exist_ok=True)

        # Generate master script (in first selected language)
        primary_language = valid_languages[0]
        logger.info(f"📝 Generating master script in {self.language_names[primary_language]}")
        generator = VideoGenerator(api_key=self.api_key, use_real_veo=True)
        master_script = generator._generate_creative_script(config, base_video_id)

        # Generate sufficient video clips for the full duration
        logger.info("🎬 Generating shared video clips...")
        veo_prompts = generator._create_veo_prompts(config, master_script)

        # Ensure we have enough clips for the duration
        clips_needed = max(2, config.duration_seconds // 6)

        if len(veo_prompts) < clips_needed:
            logger.warning(
                f"Only {len(veo_prompts)} prompts for {config.duration_seconds}s, "
                "generating more...")
            additional_prompts = clips_needed - len(veo_prompts)

            for i in range(additional_prompts):
                fallback_prompt = {
                    'veo_prompt': f"Continuation of the story, scene {len(veo_prompts) + i + 1}",
                    'description': f"Additional scene {i + 1}",
                    'duration': min(8, config.duration_seconds / clips_needed),
                    'scene_type': 'continuation'
                }
                veo_prompts.append(fallback_prompt)

            logger.info(f"Added {additional_prompts} additional prompts for full duration")

        # Generate shared video clips that all language versions will use
        video_clip_paths = generator._generate_video_clips(config, master_script)

        # Convert file paths to clip dictionaries with metadata
        veo_clips = []
        for i, clip_path in enumerate(video_clip_paths):
            veo_clips.append({
                'clip_path': clip_path,
                'clip_id': f"shared_clip_{i}_{base_video_id}",
                'duration': min(8, config.duration_seconds / len(video_clip_paths)),
                'scene_index': i,
                'prompt': f"Scene {i+1}",
                'success': os.path.exists(clip_path) if clip_path else False
            })

        # Move clips to shared directory
        for clip in veo_clips:
            if clip['clip_path'] and os.path.exists(clip['clip_path']):
                new_path = os.path.join(shared_clips_dir, os.path.basename(clip['clip_path']))
                os.rename(clip['clip_path'], new_path)
                clip['clip_path'] = new_path

        # Generate versions for each selected language
        language_versions = {}

        for language in valid_languages:
            lang_version = self._generate_language_version(
                language, master_script, config, veo_clips,
                base_video_id, session_dir, shared_clips_dir
            )
            language_versions[language] = lang_version

        total_time = time.time() - start_time

        multilang_video = MultiLanguageVideo(
            base_video_id=base_video_id,
            master_config=config,
            shared_clips_dir=shared_clips_dir,
            veo_clips=veo_clips,
            language_versions=language_versions,
            total_generation_time=total_time,
            master_script=master_script,
            total_languages=len(language_versions),
            primary_language=primary_language,
            supported_languages=list(language_versions.keys())
        )

        self._save_multilingual_project_info(multilang_video, session_dir)
        logger.info(f"🎉 Multi-language generation complete: {len(language_versions)} languages in {total_time:.1f}s")

        return multilang_video

    def _generate_language_version(self, language: Language, master_script: str,
                                 config: GeneratedVideoConfig, veo_clips: List[Dict],
                                 base_video_id: str, session_dir: str,
                                 shared_clips_dir: str) -> LanguageVersion:
        """Generate a single language version of the video"""

        lang_name = self.language_names[language]
        logger.info(f"🔤 Generating {lang_name} version...")

        # Translate script
        translated_script = self._translate_script(master_script, language, config)

        # Generate TTS
        audio_path = self._generate_multilingual_tts(
            translated_script, language, config.duration_seconds,
            base_video_id, session_dir
        )

        # Compose video
        video_path = self._compose_multilingual_video(
            veo_clips, audio_path, language, base_video_id, session_dir
        )

        # Create version object
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        audio_clip.close()

        lang_version = LanguageVersion(
            language=language,
            language_name=lang_name,
            audio_path=audio_path,
            video_path=video_path,
            translated_script=translated_script,
            translated_overlays=[],
            tts_voice_used=self.tts_voice_config[language]['lang'],
            word_count=len(translated_script.split()),
            audio_duration=audio_duration
        )

        return lang_version

    def _translate_script(self, master_script: str, target_language: Language,
                         config: GeneratedVideoConfig) -> str:
        """Translate script maintaining timing and emotional impact with cultural context"""

        lang_name = self.language_names[target_language]
        target_words = int(config.duration_seconds * 2.5)
        is_rtl = target_language in self.rtl_languages
        cultural_context = self.cultural_context.get(target_language, "neutral tone")

        logger.info(f"📝 Translating to {lang_name} ({target_words} words)")
        if is_rtl:
            logger.info("📜 RTL language detected - applying right-to-left formatting")

        translation_prompt = """
        Translate this video script to {lang_name} maintaining exact timing and
                emotion.

        ORIGINAL SCRIPT:
        {master_script}

        REQUIREMENTS:
        - Target language: {lang_name}
        - Duration: {config.duration_seconds} seconds
        - Target words: {target_words} (for precise timing)
        - Cultural context: {cultural_context}
        - Keep natural speaking rhythm for {lang_name} speakers
        - Cultural sensitivity and appropriate expressions
        {"- RIGHT-TO-LEFT (RTL) language - ensure proper text direction" if is_rtl else ""}

        CULTURAL ADAPTATION:
        - Use culturally appropriate expressions and idioms
        - Adapt humor and references to local context
        - Maintain emotional impact while respecting cultural norms
        - Use natural speech patterns for {lang_name}

        Return ONLY the translated script with exactly {target_words} words.
        """

        try:
            response = self.translation_model.generate_content(translation_prompt)
            translated_script = response.text.strip()

            # Adjust word count for timing
            actual_words = len(translated_script.split())
            if actual_words > target_words * 1.2:
                words = translated_script.split()[:target_words]
                translated_script = ' '.join(words) + "."
            elif actual_words < target_words * 0.8:
                # Extend naturally with culturally appropriate phrases
                extensions = {
                    Language.ENGLISH_US: ["This is incredible!", "Amazing!", "Don't miss this!"],
                    Language.ENGLISH_UK: ["This is brilliant!", "Absolutely brilliant!", "Quite remarkable!"],
                    Language.ENGLISH_IN: ["This is fantastic!", "Very good!", "Most excellent!"],
                    Language.FRENCH: ["C'est incroyable!", "Magnifique!", "Ne ratez pas ça!"],
                    Language.GERMAN: ["Das ist unglaublich!", "Fantastisch!", "Verpassen Sie das nicht!"],
                    Language.ARABIC: ["هذا مذهل!", "رائع!", "لا تفوت هذا!"],
                    Language.PERSIAN: ["این عالی است!", "عالی!", "این را از دست ندهید!"],
                    Language.HEBREW: ["זה מדהים!", "מהמם!", "אל תפספסו!"],
                    Language.THAI: ["นี่น่าทึ่งมาก!", "ยอดเยี่ยม!", "อย่าพลาด!"],
                    Language.SPANISH: ["¡Esto es increíble!", "¡Asombroso!", "¡No te lo pierdas!"],
                    Language.ITALIAN: ["È incredibile!", "Fantastico!", "Non perdertelo!"],
                    Language.PORTUGUESE: ["Isso é incrível!", "Fantástico!", "Não perca!"],
                    Language.RUSSIAN: ["Это невероятно!", "Потрясающе!", "Не пропустите!"],
                    Language.CHINESE: ["这太不可思议了!", "太棒了!", "不要错过!"],
                    Language.JAPANESE: ["これは信じられない!", "素晴らしい!", "見逃すな!"]
                }

                ext_list = extensions.get(target_language, extensions[Language.ENGLISH_US])
                while len(translated_script.split()) < target_words:
                    translated_script += " " + \
                        ext_list[len(translated_script.split()) % len(ext_list)]

                words = translated_script.split()[:target_words]
                translated_script = ' '.join(words) + "."

            # Apply RTL formatting if needed
            if is_rtl:
                translated_script = self._apply_rtl_formatting(
                    translated_script,
                    target_language)

            logger.info(f"✅ {lang_name} translation: {len(translated_script.split())} words")
            if is_rtl:
                logger.info("📜 RTL formatting applied")

            return translated_script

        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            return master_script

    def _apply_rtl_formatting(self, text: str, language: Language) -> str:
        """Apply RTL formatting and ensure proper text direction"""

        # Add RTL marker at the beginning for proper text direction
        rtl_marker = "\u202E"  # Right-to-Left Override

        # Language-specific RTL handling
        if language == Language.ARABIC:
            # Ensure proper Arabic text formatting
            text = rtl_marker + text
        elif language == Language.HEBREW:
            # Ensure proper Hebrew text formatting
            text = rtl_marker + text
        elif language == Language.PERSIAN:
            # Ensure proper Persian text formatting
            text = rtl_marker + text

        return text

    def _generate_multilingual_tts(self, script: str, language: Language,
                                 duration: int, video_id: str, session_dir: str) -> str:
        """Generate realistic TTS audio in target language"""

        lang_name = self.language_names[language]
        logger.info(f"🎤 Generating realistic {lang_name} TTS...")

        try:
            # Enhanced TTS configuration with language-specific settings
            tts_config = self.tts_voice_config[language].copy()

            # Special handling for Hebrew to improve naturalness
            if language == Language.HEBREW:
                logger.info("🎤 Using enhanced Hebrew TTS settings...")
                # Use better Hebrew voice settings
                tts_config = {
                    'lang': 'iw',  # Hebrew language code
                    'tld': 'co.il',  # Israeli domain for better Hebrew pronunciation
                    'slow': False
                }

                # Add Hebrew-specific improvements
                # Remove punctuation that might confuse Hebrew TTS
                script = re.sub(r'[^\w\s\u0590-\u05FF]', ' ', script)  # Keep Hebrew characters
                script = re.sub(r'\s+', ' ', script).strip()

                # Add natural Hebrew speech patterns
                script = script.replace('.', ' ')  # Remove periods for better flow
                script = script.replace('!', ' ')  # Remove exclamation marks
                script = script.replace('?', ' ')  # Remove question marks

                logger.info(f"🎤 Hebrew script cleaned: {script[:50]}...")

            # Create natural TTS with emotion
            tts = gTTS(
                text=script,
                **tts_config
            )

            audio_filename = f"audio_{language.value}_{video_id}.mp3"
            audio_path = os.path.join(session_dir, audio_filename)

            # Multiple attempts for reliable generation
            for attempt in range(3):
                try:
                    logger.info(f"🎤 TTS attempt {attempt + 1}/3 for {lang_name}...")
                    tts.save(audio_path)

                    # Validate the generated audio
                    if os.path.exists(audio_path):
                        file_size = os.path.getsize(audio_path)
                        if file_size > 50000:  # At least 50KB for real audio
                            audio_clip = AudioFileClip(audio_path)
                            actual_duration = audio_clip.duration
                            audio_clip.close()

                            logger.info(f"✅ Enhanced {lang_name} TTS: {actual_duration:.1f}s ({file_size/1024:.0f}KB)")
                            return audio_path
                        else:
                            logger.warning(f"⚠️ Generated audio too small: {file_size} bytes")
                            if os.path.exists(audio_path):
                                os.remove(audio_path)

                except Exception as e:
                    logger.warning(f"⚠️ TTS attempt {attempt + 1} failed: {e}")
                    if attempt < 2:  # Wait before retry
                        time.sleep(2)
                    continue

            # If all attempts failed, create a fallback
            logger.error(f"❌ All TTS attempts failed for {lang_name}")
            raise Exception(f"TTS generation failed for {lang_name}")

        except Exception as e:
            logger.error(f"❌ TTS failed: {e}")
            raise

    def _compose_multilingual_video(self, veo_clips: List[Dict], audio_path: str,
                                   language: Language, video_id: str, session_dir: str) -> str:
        """Compose final video with shared clips, language-specific audio, and text overlays"""

        lang_name = self.language_names[language]
        logger.info(f"🎬 Composing {lang_name} video with text overlays...")

        try:
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration

            # Load shared video clips and filter out failed ones
            video_clips = []
            for clip_info in veo_clips:
                try:
                    clip_path = clip_info['clip_path']
                    if os.path.exists(clip_path):
                        file_size = os.path.getsize(clip_path)
                        if file_size > 100000:  # At least 100KB for real video
                            video_clip = VideoFileClip(clip_path)
                            video_clips.append(video_clip)
                            logger.info(f"✅ Loaded clip: {os.path.basename(clip_path)} ({file_size/1024/1024:.1f}MB)")
                        else:
                            logger.warning(f"⚠️ Skipping small clip: {os.path.basename(clip_path)} ({file_size} bytes)")
                    else:
                        logger.warning(f"⚠️ Clip not found: {clip_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load clip: {e}")

            if not video_clips:
                raise Exception("No valid video clips available")

            logger.info(f"🎬 Using {len(video_clips)} valid video clips")

            # Concatenate and sync to audio
            final_video = concatenate_videoclips(video_clips, method="compose")

            if final_video.duration > audio_duration:
                final_video = final_video.subclip(0, audio_duration)
            elif final_video.duration < audio_duration:
                padding = audio_duration - final_video.duration
                last_frame = final_video.to_ImageClip(t=final_video.duration - 0.1).set_duration(padding)
                final_video = concatenate_videoclips([final_video, last_frame])

            # Add text overlays for multi-language videos
            final_video_with_overlays = self._add_multilingual_text_overlays(
                final_video, language, audio_duration
            )

            # Add audio
            final_video_with_audio = final_video_with_overlays.set_audio(audio_clip)

            # Save to final_output directory (all languages in same folder)
            final_output_dir = os.path.join(session_dir, "final_output")
            os.makedirs(final_output_dir, exist_ok=True)
            video_filename = f"final_video_{language.value}_{video_id}.mp4"
            output_path = os.path.join(final_output_dir, video_filename)

            logger.info(f"🎬 Rendering {lang_name} video: {output_path}")
            final_video_with_audio.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )

            # Cleanup
            final_video_with_audio.close()
            audio_clip.close()
            for clip in video_clips:
                clip.close()

            # Verify output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ {lang_name} video generated: {output_path} ({file_size:.1f}MB)")
                return output_path
            else:
                raise Exception(f"Output video not created: {output_path}")

        except Exception as e:
            logger.error(f"❌ Video composition failed for {lang_name}: {e}")
            raise

    def _add_multilingual_text_overlays(
        self,
        video_clip,
        language: Language,
        duration: float):
        """Add text overlays appropriate for the target language"""
        from moviepy.editor import TextClip, CompositeVideoClip

        lang_name = self.language_names[language]
        is_rtl = language in self.rtl_languages

        logger.info(f"📝 Adding text overlays for {lang_name} (RTL: {is_rtl}")

        try:
            overlays = []
            video_width, video_height = video_clip.size

            # Language-specific text overlays with enhanced styling
            if language == Language.HEBREW:
                overlay_texts = [
                    {"text": "🔥 תוכן ויראלי", "start": 0, "end": 3, "position": "top", "color": "#FF6B6B", "font": "Helvetica-Bold"},
                    {"text": "💡 מידע חשוב", "start": 4, "end": 8, "position": "center", "color": "#4ECDC4", "font": "Arial-Bold"},
                    {"text": "👆 עקבו לעוד", "start": max(0, duration-4), "end": duration, "position": "bottom", "color": "#45B7D1", "font": "Impact"}
                ]
            elif language == Language.ARABIC:
                overlay_texts = [
                    {"text": "🔥 محتوى فيروسي", "start": 0, "end": 3, "position": "top", "color": "#96CEB4", "font": "Helvetica-Bold"},
                    {"text": "💡 معلومات مهمة", "start": 4, "end": 8, "position": "center", "color": "#54A0FF", "font": "Arial-Bold"},
                    {"text": "👆 تابعونا للمزيد", "start": max(0, duration-4), "end": duration, "position": "bottom", "color": "#5F27CD", "font": "Impact"}
                ]
            elif language == Language.PERSIAN:
                overlay_texts = [
                    {"text": "🔥 محتوای ویروسی", "start": 0, "end": 3, "position": "top", "color": "#00D2D3", "font": "Helvetica-Bold"},
                    {"text": "💡 اطلاعات مهم", "start": 4, "end": 8, "position": "center", "color": "#C44569", "font": "Arial-Bold"},
                    {"text": "👆 دنبال کنید", "start": max(0, duration-4), "end": duration, "position": "bottom", "color": "#2C3E50", "font": "Impact"}
                ]
            else:
                # English and other languages with enhanced colors
                overlay_texts = [
                    {"text": "🔥 Viral Content", "start": 0, "end": 3, "position": "top", "color": "#FF6B6B", "font": "Helvetica-Bold"},
                    {"text": "💡 Important Info", "start": 4, "end": 8, "position": "center", "color": "#4ECDC4", "font": "Arial-Bold"},
                    {"text": "👆 Follow for more", "start": max(0, duration-4), "end": duration, "position": "bottom", "color": "#45B7D1", "font": "Impact"}
                ]

            # Create text clips
            for overlay in overlay_texts:
                try:
                    text = overlay["text"]
                    start_time = overlay["start"]
                    end_time = min(overlay["end"], duration)
                    position = overlay["position"]

                    if end_time <= start_time:
                        continue

                    # Font size based on video dimensions
                    font_size = max(60, int(video_width * 0.08))

                    # Position calculation
                    if position == "top":
                        y_pos = video_height * 0.15
                    elif position == "center":
                        y_pos = video_height * 0.5
                    else:  # bottom
                        y_pos = video_height * 0.75

                    # Create text clip with enhanced styling
                    text_clip = TextClip(
                        text,
                        fontsize=font_size,
                        color=overlay.get("color", "white"),  # Use enhanced color
                        font=overlay.get("font", "Arial-Bold"),  # Use enhanced font
                        stroke_color='black',
                        stroke_width=3,
                        method='caption',
                        size=(int(video_width * 0.9), None),
                        align='center'
                    )

                    text_clip = text_clip.set_position(('center', y_pos)).set_start(start_time).set_duration(end_time - start_time)
                    overlays.append(text_clip)

                    logger.info(f"📝 Added {lang_name} overlay: '{text}' at {start_time}-{end_time}s")

                except Exception as e:
                    logger.warning(f"⚠️ Failed to create overlay: {e}")
                    continue

            # Composite video with overlays
            if overlays:
                final_video = CompositeVideoClip([video_clip] + overlays)
                logger.info(f"✅ Added {len(overlays)} text overlays to {lang_name} video")
                return final_video
            else:
                logger.warning(f"⚠️ No overlays added to {lang_name} video")
                return video_clip

        except Exception as e:
            logger.error(f"❌ Text overlay generation failed for {lang_name}: {e}")
            return video_clip

    def _save_multilingual_project_info(
        self,
        multilang_video: MultiLanguageVideo,
        session_dir: str):
        """Save project information"""
        try:
            report_path = os.path.join(session_dir, "multilingual_report.txt")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("🌍 MULTI-LANGUAGE VIDEO PROJECT\n")
                f.write("=" * 50 + "\n\n")

                f.write("📋 PROJECT OVERVIEW\n")
                f.write(f"Video ID: {multilang_video.base_video_id}\n")
                f.write(f"Languages: {multilang_video.total_languages}\n")
                f.write(f"Generation Time: {multilang_video.total_generation_time:.1f}s\n\n")

                f.write("🌍 LANGUAGE VERSIONS\n")
                for lang, version in multilang_video.language_versions.items():
                    f.write(f"{version.language_name}: {os.path.basename(version.video_path)}\n")
                    f.write(f"  Audio: {version.audio_duration:.1f}s\n")
                    f.write(f"  Words: {version.word_count}\n\n")

            logger.info(f"📊 Project report saved: {report_path}")

        except Exception as e:
            logger.error(f"Failed to save project info: {e}")
