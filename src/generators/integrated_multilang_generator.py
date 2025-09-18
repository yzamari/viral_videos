"""
Integrated Multilingual Video Generator
Combines AI voice selection, enhanced script processing, RTL validation, and
        video generation
"""
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..utils.logging_config import get_logger
from ..models.video_models import (
    GeneratedVideoConfig, Language, Platform, VideoCategory,
    LanguageVersion, MultiLanguageVideo
)
from ..agents.voice_director_agent import VoiceDirectorAgent
from ..generators.enhanced_script_processor import EnhancedScriptProcessor
from ..generators.rtl_validator import RTLValidator
from ..generators.enhanced_multilang_tts import EnhancedMultilingualTTS
from ..config.ai_model_config import DEFAULT_AI_MODEL

logger = get_logger(__name__)

@dataclass
class VoiceSelectionResult:
    """Result of AI voice selection process"""
    strategy: str
    clip_voices: List[Dict[str, Any]]
    voice_variety: bool
    ai_reasoning: str
    confidence_score: float

@dataclass
class ProcessedScript:
    """Result of script processing"""
    original_script: str
    enhanced_script: str
    final_script: str
    tts_ready: bool
    word_count: int
    sentence_count: int
    estimated_duration: float
    validation_notes: List[str]

class IntegratedMultilingualGenerator:
    """Integrated generator with AI voice selection and enhanced multilingual support"""

    def __init__(self, api_key: str, output_dir: str = "outputs"):
        self.api_key = api_key
        self.output_dir = output_dir

        # Initialize all AI components
        self.voice_director = VoiceDirectorAgent(api_key)
        self.script_processor = EnhancedScriptProcessor(api_key)
        self.rtl_validator = RTLValidator(api_key)
        self.multilang_tts = EnhancedMultilingualTTS(api_key)

        # Language capabilities
        self.supported_languages = [
            Language.ENGLISH_US, Language.ENGLISH_UK, Language.ENGLISH_IN,
            Language.HEBREW, Language.ARABIC, Language.PERSIAN,
            Language.FRENCH, Language.SPANISH, Language.GERMAN,
            Language.ITALIAN, Language.PORTUGUESE, Language.RUSSIAN,
            Language.CHINESE, Language.JAPANESE, Language.THAI
        ]

        logger.info(
            "✅ Integrated Multilingual Generator initialized with AI agents")

    def generate_multilingual_video_with_ai_voices(
            self,
            config: GeneratedVideoConfig,
            languages: List[Language],
            base_script: str) -> MultiLanguageVideo:
        """Generate multilingual video with AI-powered voice selection"""

        logger.info(
            f"🌍 Generating multilingual video in {
                len(languages)} languages")

        start_time = time.time()
        base_video_id = f"multilang_{int(time.time())}"

        # Step 1: Process and enhance the base script
        logger.info("📝 Step 1: Processing base script...")
        primary_language = languages[0] if languages else Language.ENGLISH_US

        processed_script = self._process_script_with_ai(
            script=base_script,
            language=primary_language,
            config=config
        )

        if not processed_script.tts_ready:
            logger.warning(
                "⚠️ Script processing had issues, proceeding with caution")

        # Step 2: Generate AI voice strategy for primary language
        logger.info("🎭 Step 2: AI voice strategy analysis...")
        _voice_strategy = self._get_ai_voice_strategy(
            script=processed_script.final_script,
            language=primary_language,
            config=config
        )

        # Step 3: Create shared video clips (visual content)
        logger.info("🎬 Step 3: Generating shared video clips...")
        # This would integrate with existing video generation
        shared_clips = self._generate_shared_video_clips(
            config, processed_script.final_script)

        # Step 4: Generate language-specific versions
        logger.info("🗣️ Step 4: Generating language-specific versions...")
        language_versions = {}

        for language in languages:
            logger.info(f"   Processing {language.value}...")

            # Translate and process script for this language
            lang_script = self._translate_and_process_script(
                script=processed_script.final_script,
                target_language=language,
                config=config
            )

            # Generate AI-optimized audio for this language
            audio_path = self._generate_ai_optimized_audio(
                script=lang_script.final_script,
                language=language,
                config=config,
                num_clips=len(shared_clips)
            )

            # Create language version
            language_versions[language] = LanguageVersion(
                language=language,
                language_name=self._get_language_name(language),
                audio_path=audio_path,
                video_path="",  # Will be set after video composition
                translated_script=lang_script.final_script,
                translated_overlays=[],
                tts_voice_used="AI-selected",
                word_count=lang_script.word_count,
                audio_duration=lang_script.estimated_duration
            )

        # Step 5: Create multilingual video object
        total_time = time.time() - start_time

        multilang_video = MultiLanguageVideo(
            base_video_id=base_video_id,
            master_config=config,
            shared_clips_dir=self.output_dir,
            veo_clips=shared_clips,
            language_versions=language_versions,
            total_generation_time=total_time,
            master_script=processed_script.final_script,
            total_languages=len(languages),
            primary_language=primary_language,
            supported_languages=languages
        )

        logger.info(f"✅ Multilingual video generated in {total_time:.1f}s")
        return multilang_video

    def _process_script_with_ai(
            self,
            script: str,
            language: Language,
            config: GeneratedVideoConfig) -> ProcessedScript:
        """Process script with AI enhancement and validation"""

        try:
            # Enhanced script processing
            result = self.script_processor.process_script_for_tts(
                script=script,
                language=language,
                target_duration=config.duration_seconds,
                platform=config.target_platform,
                category=config.category
            )

            # RTL validation if needed
            validation_notes = []
            final_script = result.get("final_script", script)

            if self.rtl_validator.is_rtl_language(language):
                logger.info(f"🔍 Validating RTL language: {language.value}")
                rtl_result = self.rtl_validator.validate_and_correct_rtl_text(
                    text=final_script,
                    language=language,
                    context=f"Video about: {config.mission}"
                )

                if rtl_result.get("corrections_made"):
                    final_script = rtl_result["corrected_text"]
                    validation_notes.append(
                        f"RTL corrections: {len(rtl_result['corrections_made'])}")
                    logger.info(
                        f"✅ RTL validation complete with {len(rtl_result['corrections_made'])} corrections")

            return ProcessedScript(
                original_script=script,
                enhanced_script=result.get("enhanced_script", script),
                final_script=final_script,
                tts_ready=result.get("tts_ready", True),
                word_count=result.get("word_count", len(script.split())),
                sentence_count=result.get("sentence_count", 1),
                estimated_duration=result.get("estimated_duration", config.duration_seconds),
                validation_notes=validation_notes
            )

        except Exception as e:
            logger.error(f"❌ Script processing failed: {e}")
            # Return basic processed version
            return ProcessedScript(
                original_script=script,
                enhanced_script=script,
                final_script=script,
                tts_ready=True,
                word_count=len(script.split()),
                sentence_count=1,
                estimated_duration=config.duration_seconds,
                validation_notes=["Processing failed, using original script"]
            )

    def _get_ai_voice_strategy(
            self,
            script: str,
            language: Language,
            config: GeneratedVideoConfig) -> VoiceSelectionResult:
        """Get AI-powered voice selection strategy"""

        try:
            # Calculate number of clips based on duration
            # Use conservative estimate: ~3-4 seconds per clip for better quality
            num_clips = max(2, min(5, config.duration_seconds // 3))
            logger.info(f"⏱️ Multilang Voice: Duration {config.duration_seconds}s → {num_clips} clips")

            result = self.voice_director.analyze_content_and_select_voices(
                mission=config.mission,
                script=script,
                language=language,
                platform=config.target_platform,
                category=config.category,
                duration_seconds=config.duration_seconds,
                num_clips=num_clips
            )

            if result["success"]:
                ai_analysis = result["ai_analysis"]
                voice_config = result["voice_config"]

                return VoiceSelectionResult(
                    strategy=ai_analysis["strategy"],
                    clip_voices=voice_config["clip_voices"],
                    voice_variety=voice_config["voice_variety"],
                    ai_reasoning=ai_analysis.get("reasoning", ""),
                    confidence_score=ai_analysis.get("confidence_score", 0.8)
                )
            else:
                logger.warning("⚠️ AI voice selection failed, using fallback")
                return self._create_fallback_voice_strategy(num_clips)

        except Exception as e:
            logger.error(f"❌ Voice strategy analysis failed: {e}")
            return self._create_fallback_voice_strategy(3)

    def _translate_and_process_script(
            self,
            script: str,
            target_language: Language,
            config: GeneratedVideoConfig) -> ProcessedScript:
        """Translate script to target language and process for TTS"""

        if target_language == Language.ENGLISH_US:
            # No translation needed
            return self._process_script_with_ai(
                script, target_language, config)

        try:
            # Simple translation using Gemini (could be enhanced)
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(DEFAULT_AI_MODEL)

            language_names = {
                Language.HEBREW: "Hebrew (עברית)",
                Language.ARABIC: "Arabic (العربية)",
                Language.FRENCH: "French (Français)",
                Language.SPANISH: "Spanish (Español)",
                Language.GERMAN: "German (Deutsch)"
            }

            target_lang_name = language_names.get(
                target_language, target_language.value)

            translation_prompt = """
            Translate this video script to {target_lang_name}.
            Keep it natural, engaging, and appropria
                te for {config.target_platform.value} content.

            Original script: {script}

            Requirements:
            - Natural, conversational tone
            - Culturally appropriate
            - Same meaning and energy
            - TTS-friendly (short sentences, clear punctuation)

            Return only the translated script.
            """

            response = model.generate_content(translation_prompt)
            translated_script = response.text.strip()

            # Process the translated script
            return self._process_script_with_ai(
                translated_script, target_language, config)

        except Exception as e:
            logger.error(
                f"❌ Translation failed for {
                    target_language.value}: {e}")
            # Return original script as fallback
            return ProcessedScript(
                original_script=script,
                enhanced_script=script,
                final_script=script,
                tts_ready=True,
                word_count=len(
                    script.split()),
                sentence_count=1,
                estimated_duration=config.duration_seconds,
                validation_notes=[
                    f"Translation failed for {
                        target_language.value}"])

    def _generate_ai_optimized_audio(
            self,
            script: str,
            language: Language,
            config: GeneratedVideoConfig,
            num_clips: int) -> str:
        """Generate AI-optimized audio with intelligent voice selection"""

        try:
            # Generate audio with AI voice selection
            audio_files = self.multilang_tts.generate_intelligent_voice_audio(
                script=script,
                language=language,
                mission=config.mission,
                platform=config.target_platform,
                category=config.category,
                duration_seconds=config.duration_seconds,
                num_clips=num_clips
            )

            if audio_files and len(audio_files) > 0:
                # For now, return the first audio file
                # In a full implementation, we'd combine multiple clip audios
                return audio_files[0]
            else:
                logger.warning("⚠️ AI audio generation failed, using fallback")
                return self._generate_fallback_audio(script, language)

        except Exception as e:
            logger.error(f"❌ AI audio generation failed: {e}")
            return self._generate_fallback_audio(script, language)

    def _generate_shared_video_clips(
            self, config: GeneratedVideoConfig, script: str) -> List[Dict[str, Any]]:
        """Generate shared video clips (placeholder - would integrate with existing video generation)"""

        # This is a placeholder - in the full integration, this would call
        # the existing video generation system
        num_clips = max(2, min(5, config.duration_seconds // 3))
        clip_duration = config.duration_seconds / num_clips
        
        logger.info(f"⏱️ Multilang Clips: Duration {config.duration_seconds}s → {num_clips} clips @ {clip_duration:.1f}s each")

        shared_clips = []
        for i in range(num_clips):
            shared_clips.append({
                "clip_id": f"shared_clip_{i}",
                "clip_path": f"placeholder_clip_{i}.mp4",
                "duration": clip_duration,
                "scene_index": i,
                "prompt": f"Scene {i + 1} of {config.mission}",
                "success": True
            })

        logger.info(f"📹 Generated {len(shared_clips)} shared video clips")
        return shared_clips

    def _generate_fallback_audio(self, script: str, language: Language) -> str:
        """Generate fallback audio when AI generation fails"""

        try:
            from gtts import gTTS
            import tempfile
            import uuid

            # Basic gTTS configuration
            lang_codes = {
                Language.ENGLISH_US: 'en',
                Language.HEBREW: 'iw',
                Language.ARABIC: 'ar',
                Language.FRENCH: 'fr',
                Language.SPANISH: 'es',
                Language.GERMAN: 'de'
            }

            lang_code = lang_codes.get(language, 'en')

            tts = gTTS(text=script, lang=lang_code, slow=False)
            audio_path = os.path.join(
                tempfile.gettempdir(),
                f"fallback_audio_{
                    uuid.uuid4()}.mp3")
            tts.save(audio_path)

            logger.info(f"✅ Fallback audio generated: {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"❌ Even fallback audio generation failed: {e}")
            raise

    def _create_fallback_voice_strategy(
            self, num_clips: int) -> VoiceSelectionResult:
        """Create fallback voice strategy when AI analysis fails"""

        clip_voices = []
        for i in range(num_clips):
            clip_voices.append({
                "clip_index": i,
                "voice_name": "fallback_voice",
                "personality": "narrator",
                "gender": "auto",
                "emotion": "neutral",
                "speed": 1.0,
                "pitch": 0.0
            })

        return VoiceSelectionResult(
            strategy="single",
            clip_voices=clip_voices,
            voice_variety=False,
            ai_reasoning="Fallback strategy due to AI analysis failure",
            confidence_score=0.5
        )

    def _get_language_name(self, language: Language) -> str:
        """Get human-readable language name"""

        language_names = {
            Language.ENGLISH_US: "English (US)",
            Language.ENGLISH_UK: "English (UK)",
            Language.ENGLISH_IN: "English (India)",
            Language.HEBREW: "Hebrew (עברית)",
            Language.ARABIC: "Arabic (العربية)",
            Language.PERSIAN: "Persian (فارسی)",
            Language.FRENCH: "French (Français)",
            Language.SPANISH: "Spanish (Español)",
            Language.GERMAN: "German (Deutsch)",
            Language.ITALIAN: "Italian (Italiano)",
            Language.PORTUGUESE: "Portuguese (Português)",
            Language.RUSSIAN: "Russian (Русский)",
            Language.CHINESE: "Chinese (中文)",
            Language.JAPANESE: "Japanese (日本語)",
            Language.THAI: "Thai (ไทย)"
        }

        return language_names.get(language, language.value)

    def get_voice_strategy_preview(self,
                                   config: GeneratedVideoConfig,
                                   script: str,
                                   language: Language) -> Dict[str,
                                                               Any]:
        """Get a preview of the voice strategy without generating audio"""

        try:
            voice_strategy = self._get_ai_voice_strategy(
                script, language, config)

            return {
                "strategy": voice_strategy.strategy,
                "voice_variety": voice_strategy.voice_variety,
                "num_unique_voices": len(set(v["voice_name"] for v in voice_strategy.clip_voices)),
                "ai_reasoning": voice_strategy.ai_reasoning,
                "confidence": voice_strategy.confidence_score,
                "clip_breakdown": [
                    {
                        "clip": i,
                        "voice": voice["voice_name"],
                        "personality": voice["personality"],
                        "emotion": voice["emotion"]
                    }
                    for i, voice in enumerate(voice_strategy.clip_voices)
                ]
            }

        except Exception as e:
            logger.error(f"❌ Voice strategy preview failed: {e}")
            return {"strategy": "fallback", "error": str(e)}
