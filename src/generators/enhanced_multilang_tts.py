"""
Enhanced Multilingual TTS Client
Works with Voice Director Agent for intelligent voice selection across languages
"""
import os
import tempfile
import uuid
from typing import Optional, Dict, Any, List
from enum import Enum

from google.cloud import texttospeech
from gtts import gTTS
from ..utils.logging_config import get_logger
from ..models.video_models import Language
from ..agents.voice_director_agent import VoiceDirectorAgent

logger = get_logger(__name__)

class EnhancedMultilingualTTS:
    """Enhanced TTS client with AI voice selection and multi-language support"""

    def __init__(self, api_key: str, credentials_path: Optional[str] = None):
        """Initialize enhanced multilingual TTS client"""
        try:
            if credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

            # Initialize Google Cloud TTS
            self.client = texttospeech.TextToSpeechClient()

            # Initialize Voice Director Agent
            self.voice_director = VoiceDirectorAgent(api_key)

            # Language code mapping for Google Cloud TTS
            self.language_codes = {
                Language.ENGLISH_US: "en-US",
                Language.ENGLISH_UK: "en-GB",
                Language.ENGLISH_IN: "en-IN",
                Language.HEBREW: "he-IL",
                Language.ARABIC: "ar-XA",
                Language.FRENCH: "fr-FR",
                Language.SPANISH: "es-ES",
                Language.GERMAN: "de-DE",
                Language.ITALIAN: "it-IT",
                Language.PORTUGUESE: "pt-BR",
                Language.RUSSIAN: "ru-RU",
                Language.CHINESE: "zh-CN",
                Language.JAPANESE: "ja-JP",
                Language.PERSIAN: "fa-IR",
                Language.THAI: "th-TH"
            }

            # Fallback gTTS configuration for unsupported voices
            self.gtts_fallback_config = {
                Language.ENGLISH_US: {'lang': 'en', 'tld': 'com'},
                Language.ENGLISH_UK: {'lang': 'en', 'tld': 'co.uk'},
                Language.ENGLISH_IN: {'lang': 'en', 'tld': 'co.in'},
                Language.HEBREW: {'lang': 'iw', 'tld': 'co.il'},
                Language.ARABIC: {'lang': 'ar', 'tld': 'com'},
                Language.FRENCH: {'lang': 'fr', 'tld': 'fr'},
                Language.SPANISH: {'lang': 'es', 'tld': 'es'},
                Language.GERMAN: {'lang': 'de', 'tld': 'de'},
                Language.ITALIAN: {'lang': 'it', 'tld': 'it'},
                Language.PORTUGUESE: {'lang': 'pt', 'tld': 'com.br'},
                Language.RUSSIAN: {'lang': 'ru', 'tld': 'ru'},
                Language.CHINESE: {'lang': 'zh', 'tld': 'cn'},
                Language.JAPANESE: {'lang': 'ja', 'tld': 'jp'},
                Language.PERSIAN: {'lang': 'fa', 'tld': 'com'},
                Language.THAI: {'lang': 'th', 'tld': 'com'}
            }

            logger.info("✅ Enhanced Multilingual TTS client initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Multilingual TTS: {e}")
            raise

    def generate_intelligent_voice_audio(self,
                                       script: str,
                                       language: Language,
                                       topic: str,
                                       platform: Any,
                                       category: Any,
                                       duration_seconds: int,
                                       num_clips: int,
                                       clip_index: Optional[int] = None) -> List[str]:
        """Generate audio with AI-selected voices for optimal content delivery"""

        logger.info(f"🎤 Generating intelligent voice audio for {language.value}")

        try:
            # Get AI voice selection strategy
            voice_strategy = self.voice_director.analyze_content_and_select_voices(
                topic=topic,
                script=script,
                language=language,
                platform=platform,
                category=category,
                duration_seconds=duration_seconds,
                num_clips=num_clips
            )

            if not voice_strategy["success"]:
                logger.warning("⚠️ AI voice selection failed, using single voice fallback")

            voice_config = voice_strategy["voice_config"]

            # Generate audio for each clip
            audio_files = []

            if clip_index is not None:
                # Generate for specific clip
                clip_voices = [voice_config["clip_voices"][clip_index]]
            else:
                # Generate for all clips
                clip_voices = voice_config["clip_voices"]

            for clip_voice in clip_voices:
                audio_path = self._generate_clip_audio(
                    script=script,
                    language=language,
                    voice_config=clip_voice
                )

                if audio_path:
                    audio_files.append(audio_path)
                    logger.info(f"✅ Generated audio for clip {clip_voice['clip_index']}: {clip_voice['voice_name']}")
                else:
                    logger.error(f"❌ Failed to generate audio for clip {clip_voice['clip_index']}")

            return audio_files

        except Exception as e:
            logger.error(f"❌ Intelligent voice generation failed: {e}")
            # Fallback to simple generation
            return [self._generate_fallback_audio(script, language)]

    def _generate_clip_audio(self, script: str, language: Language, voice_config: Dict) -> Optional[str]:
        """Generate audio for a specific clip with given voice configuration"""

        try:
            voice_name = voice_config["voice_name"]
            speed = voice_config.get("speed", 1.0)
            pitch = voice_config.get("pitch", 0.0)
            emotion = voice_config.get("emotion", "neutral")

            logger.info(f"🎤 Generating clip audio: {voice_name} (speed: {speed}, pitch: {pitch}, emotion: {emotion})")

            # Try Google Cloud TTS first
            if self._is_google_cloud_voice(voice_name):
                return self._generate_google_cloud_audio(script, language, voice_name, speed, pitch)
            else:
                # Fallback to enhanced gTTS
                return self._generate_enhanced_gtts_audio(script, language, emotion)

        except Exception as e:
            logger.error(f"❌ Clip audio generation failed: {e}")
            return None

    def _is_google_cloud_voice(self, voice_name: str) -> bool:
        """Check if voice is available in Google Cloud TTS"""
        google_voice_patterns = [
            "Journey", "Neural2", "Wavenet", "Standard", "Studio"
        ]
        return any(pattern in voice_name for pattern in google_voice_patterns)

    def _generate_google_cloud_audio(self, script: str, language: Language, voice_name: str, speed: float, pitch: float) -> Optional[str]:
        """Generate audio using Google Cloud TTS"""

        try:
            language_code = self.language_codes.get(language, "en-US")

            # Enhance text for better speech
            enhanced_script = self._enhance_text_for_language(script, language)

            # Determine if voice supports SSML
            if "Journey" in voice_name:
                # Journey voices - use text input only
                synthesis_input = texttospeech.SynthesisInput(text=enhanced_script)

                # Configure audio for Journey voices
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speed,
                    sample_rate_hertz=24000,
                    effects_profile_id=["headphone-class-device"]
                )
            else:
                # Neural2/Wavenet/Standard voices - use SSML
                ssml_text = f"""
                <speak>
                    <prosody rate="{speed}" pitch="{pitch}st">
                        {enhanced_script}
                    </prosody>
                </speak>
                """

                synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

                # Configure audio with SSML support
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    sample_rate_hertz=24000,
                    effects_profile_id=["headphone-class-device"]
                )

            # Set up voice selection
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name
            )

            # Generate speech
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # Save audio file
            audio_path = os.path.join(tempfile.gettempdir(), f"multilang_tts_{uuid.uuid4()}.mp3")

            with open(audio_path, "wb") as out:
                out.write(response.audio_content)

            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                file_size = os.path.getsize(audio_path) / (1024 * 1024)
                logger.info(f"✅ Google Cloud TTS generated: {file_size:.2f}MB")
                return audio_path
            else:
                raise Exception("Generated audio file is empty")

        except Exception as e:
            logger.error(f"❌ Google Cloud TTS failed: {e}")
            return None

    def _generate_enhanced_gtts_audio(self, script: str, language: Language, emotion: str) -> Optional[str]:
        """Generate audio using enhanced gTTS with emotion-based configuration"""

        try:
            # Get gTTS configuration for language
            gtts_config = self.gtts_fallback_config.get(language, {'lang': 'en', 'tld': 'com'})

            # Enhance text for language
            enhanced_script = self._enhance_text_for_language(script, language)

            # Adjust TLD based on emotion for variety
            if emotion in ['excited', 'enthusiastic']:
                if gtts_config['lang'] == 'en':
                    gtts_config['tld'] = 'co.uk'  # British accent for excitement
            elif emotion in ['dramatic', 'authoritative']:
                if gtts_config['lang'] == 'en':
                    gtts_config['tld'] = 'com.au'  # Australian for authority

            # Generate with gTTS
            tts = gTTS(text=enhanced_script, **gtts_config, slow=False)

            audio_path = os.path.join(tempfile.gettempdir(), f"enhanced_gtts_{uuid.uuid4()}.mp3")
            tts.save(audio_path)

            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                file_size = os.path.getsize(audio_path) / (1024 * 1024)
                logger.info(f"✅ Enhanced gTTS generated: {file_size:.2f}MB")
                return audio_path
            else:
                raise Exception("Generated audio file is empty")

        except Exception as e:
            logger.error(f"❌ Enhanced gTTS failed: {e}")
            return None

    def _enhance_text_for_language(self, text: str, language: Language) -> str:
        """Enhance text with language-specific improvements"""

        enhanced_text = text

        # RTL languages need special handling
        if language in [Language.HEBREW, Language.ARABIC, Language.PERSIAN]:
            # Remove problematic punctuation for RTL TTS
            enhanced_text = enhanced_text.replace('!', ' ')
            enhanced_text = enhanced_text.replace('?', ' ')
            enhanced_text = enhanced_text.replace('.', ' ')
            enhanced_text = enhanced_text.replace(',', ' ')

            # Add natural pauses with spaces
            enhanced_text = enhanced_text.replace('  ', ' ')  # Clean double spaces

        else:
            # LTR languages - add natural pauses
            enhanced_text = enhanced_text.replace('.', '. ')
            enhanced_text = enhanced_text.replace(',', ', ')
            enhanced_text = enhanced_text.replace('!', '! ')
            enhanced_text = enhanced_text.replace('?', '? ')

        # Clean up multiple spaces
        import re
        enhanced_text = re.sub(r'\s+', ' ', enhanced_text).strip()

        return enhanced_text

    def _generate_fallback_audio(self, script: str, language: Language) -> str:
        """Generate fallback audio when all else fails"""

        logger.warning("🔄 Using basic fallback audio generation")

        try:
            gtts_config = self.gtts_fallback_config.get(language, {'lang': 'en', 'tld': 'com'})
            enhanced_script = self._enhance_text_for_language(script, language)

            tts = gTTS(text=enhanced_script, **gtts_config, slow=False)
            audio_path = os.path.join(tempfile.gettempdir(), f"fallback_tts_{uuid.uuid4()}.mp3")
            tts.save(audio_path)

            logger.info(f"✅ Fallback audio generated: {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"❌ Even fallback audio generation failed: {e}")
            raise

    def get_voice_strategy_summary(self,
                                 topic: str,
                                 language: Language,
                                 platform: Any,
                                 category: Any,
                                 duration_seconds: int,
                                 num_clips: int) -> Dict[str, Any]:
        """Get voice strategy summary without generating audio"""

        try:
            voice_strategy = self.voice_director.analyze_content_and_select_voices(
                topic=topic,
                script="Sample script for analysis",
                language=language,
                platform=platform,
                category=category,
                duration_seconds=duration_seconds,
                num_clips=num_clips
            )

            return {
                "strategy": voice_strategy["voice_config"]["strategy"],
                "num_voices": len(set(v["voice_name"] for v in voice_strategy["voice_config"]["clip_voices"])),
                "voice_variety": voice_strategy["voice_config"]["voice_variety"],
                "ai_reasoning": voice_strategy["ai_analysis"].get("reasoning", ""),
                "voices_used": [v["voice_name"] for v in voice_strategy["voice_config"]["clip_voices"]]
            }

        except Exception as e:
            logger.error(f"❌ Voice strategy summary failed: {e}")
            return {"strategy": "fallback", "num_voices": 1, "voice_variety": False}

