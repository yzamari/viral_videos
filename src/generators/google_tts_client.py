"""
Google Cloud Text-to-Speech Client
Advanced neural voices with emotion and SSML support
"""
import os
import tempfile
import uuid
from typing import Optional, Dict, Any
from enum import Enum

from google.cloud import texttospeech
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class GoogleVoiceType(str, Enum):
    """Google Cloud TTS voice types"""
    # Journey Voices (Most Advanced and Natural)
    EN_US_JOURNEY_D = "en-US-Journey-D"  # Male, conversational
    EN_US_JOURNEY_F = "en-US-Journey-F"  # Female, conversational
    EN_US_JOURNEY_O = "en-US-Journey-O"  # Female, warm

    # Neural2 Voices (High Quality)
    EN_US_NEURAL2_A = "en-US-Neural2-A"  # Female, warm
    EN_US_NEURAL2_C = "en-US-Neural2-C"  # Female, young
    EN_US_NEURAL2_D = "en-US-Neural2-D"  # Male, deep
    EN_US_NEURAL2_F = "en-US-Neural2-F"  # Female, mature
    EN_US_NEURAL2_G = "en-US-Neural2-G"  # Female, young
    EN_US_NEURAL2_H = "en-US-Neural2-H"  # Female, confident
    EN_US_NEURAL2_I = "en-US-Neural2-I"  # Male, young
    EN_US_NEURAL2_J = "en-US-Neural2-J"  # Male, mature

    # Studio Voices (Premium)
    EN_US_STUDIO_O = "en-US-Studio-O"    # Female, narrator
    EN_US_STUDIO_Q = "en-US-Studio-Q"    # Male, narrator

class GoogleTTSClient:
    """Advanced Google Cloud Text-to-Speech Client"""

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Google TTS client"""
        try:
            if credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

            self.client = texttospeech.TextToSpeechClient()

            # Voice gender mapping
            self.voice_gender_map = {
                GoogleVoiceType.EN_US_JOURNEY_D: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_JOURNEY_F: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_JOURNEY_O: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_A: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_C: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_D: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_NEURAL2_F: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_G: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_H: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_I: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_NEURAL2_J: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_STUDIO_O: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_STUDIO_Q: texttospeech.SsmlVoiceGender.MALE,
            }

            # Enhanced voice mapping for different emotions/feelings with natural settings
            self.emotion_voice_mapping = {
                "funny": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_F,  # Journey voice for naturalness
                    "pitch": 0.0,   # Natural pitch
                    "speed": 1.0,   # Natural speed
                    "volume": 0.0   # Natural volume
                },
                "excited": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_F,
                    "pitch": 2.0,   # Slightly higher pitch for excitement
                    "speed": 1.1,   # Slightly faster for energy
                    "volume": 2.0   # Slightly louder
                },
                "serious": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_D,  # Male voice for authority
                    "pitch": -2.0,  # Slightly lower pitch
                    "speed": 0.9,   # Slower for gravitas
                    "volume": 0.0   # Natural volume
                },
                "dramatic": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_D,
                    "pitch": -1.0,  # Lower pitch for drama
                    "speed": 0.85,  # Slower for dramatic effect
                    "volume": 1.0   # Slightly louder
                },
                "neutral": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_F,
                    "pitch": 0.0,   # Natural pitch
                    "speed": 1.0,   # Natural speed
                    "volume": 0.0   # Natural volume
                },
                "educational": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_O,  # Warm female voice
                    "pitch": 0.0,   # Natural pitch
                    "speed": 0.95,  # Slightly slower for clarity
                    "volume": 0.0   # Natural volume
                },
                "energetic": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_F,
                    "pitch": 1.0,   # Slightly higher pitch
                    "speed": 1.05,  # Slightly faster
                    "volume": 1.0   # Slightly louder
                }
            }

            logger.info("✅ Google Cloud TTS client initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Google TTS client: {e}")
            raise

    def generate_speech(self, text: str, feeling: str = "neutral",
                       narrative: str = "neutral", duration_target: float = 30,
                       use_ssml: bool = False, voice_override: Optional[str] = None) -> str:
        """Generate high-quality speech with Google Cloud TTS"""
        try:
            logger.info(f"🎤 Generating Google Cloud TTS voice ({feeling} emotion)")

            # Get voice configuration for emotion
            voice_config = self.emotion_voice_mapping.get(feeling.lower(), self.emotion_voice_mapping["neutral"])

            # Allow voice override from environment or parameter
            selected_voice = voice_override or os.getenv("GOOGLE_TTS_VOICE_TYPE", voice_config["voice"])

            # Get appropriate gender for the voice
            try:
                voice_gender = self.voice_gender_map.get(GoogleVoiceType(selected_voice), texttospeech.SsmlVoiceGender.FEMALE)
            except ValueError:
                # If voice not in enum, default to Journey F
                selected_voice = GoogleVoiceType.EN_US_JOURNEY_F
                voice_gender = texttospeech.SsmlVoiceGender.FEMALE

            # Enhance text with natural speech patterns
            enhanced_text = self._enhance_text_for_naturalness(text, feeling)

            # Use text input for Journey voices (they don't support SSML pitch/speed)
            if "Journey" in selected_voice:
                synthesis_input = texttospeech.SynthesisInput(text=enhanced_text)

                # Build the voice request with Journey voice
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name=selected_voice,
                    ssml_gender=voice_gender
                )

                # Configure audio with optimal settings for Journey voices
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=voice_config["speed"],
                    # No pitch control for Journey voices - they're naturally expressive
                    sample_rate_hertz=24000,
                    effects_profile_id=["headphone-class-device"],
                    volume_gain_db=voice_config["volume"]
                )
            else:
                # Use SSML for Neural2/Studio voices that support it
                ssml_text = f"""
                <speak>
                    <prosody rate="{voice_config['speed']}" pitch="{voice_config['pitch']}st" volume="{voice_config['volume']}dB">
                        {enhanced_text}
                    </prosody>
                </speak>
                """

                synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

                # Build the voice request with Neural2/Studio voice
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name=selected_voice,
                    ssml_gender=voice_gender
                )

                # Configure audio with optimal settings
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    sample_rate_hertz=24000,
                    effects_profile_id=["headphone-class-device"]
                )

            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # Save the audio to a file
            audio_path = os.path.join(tempfile.gettempdir(), f"google_neural_voice_{uuid.uuid4()}.mp3")

            with open(audio_path, "wb") as out:
                out.write(response.audio_content)

            # Validate file
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                file_size = os.path.getsize(audio_path) / (1024 * 1024)
                logger.info(f"✅ Google Cloud TTS generated: {audio_path} ({file_size:.2f}MB)")
                logger.info(f"   Voice: {selected_voice}, Speed: {voice_config['speed']}x, Pitch: {voice_config['pitch']}st")
                return audio_path
            else:
                raise Exception("Generated audio file is empty or missing")

        except Exception as e:
            logger.error(f"❌ Google Cloud TTS generation failed: {e}")
            # Fallback to basic gTTS if Cloud TTS fails
            return self._fallback_to_gtts(text, feeling)

    def _enhance_text_for_naturalness(self, text: str, feeling: str) -> str:
        """Enhance text with natural speech patterns and pauses"""
        enhanced_text = text

        # Add natural pauses and emphasis based on feeling
        if feeling == "excited":
            # Add emphasis and shorter pauses for excitement
            enhanced_text = enhanced_text.replace("!", "! ")
            enhanced_text = enhanced_text.replace("?", "? ")
            enhanced_text = enhanced_text.replace(".", ". ")
        elif feeling == "serious":
            # Add longer pauses for gravitas
            enhanced_text = enhanced_text.replace(".", "... ")
            enhanced_text = enhanced_text.replace("!", "! ")
        elif feeling == "dramatic":
            # Add dramatic pauses
            enhanced_text = enhanced_text.replace(",", "... ")
            enhanced_text = enhanced_text.replace(".", "... ")
        else:
            # Natural pauses
            enhanced_text = enhanced_text.replace(".", ". ")
            enhanced_text = enhanced_text.replace(",", ", ")
            enhanced_text = enhanced_text.replace("!", "! ")
            enhanced_text = enhanced_text.replace("?", "? ")

        # Clean up multiple spaces
        import re
        enhanced_text = re.sub(r'\s+', ' ', enhanced_text).strip()

        return enhanced_text

    def _fallback_to_gtts(self, text: str, feeling: str) -> str:
        """Fallback to basic gTTS if Cloud TTS fails"""
        try:
            from gtts import gTTS

            logger.warning("🔄 Falling back to enhanced gTTS...")

            # Enhanced gTTS configuration based on feeling
            tts_config = {
                'lang': 'en',
                'slow': False,
                'tld': 'com'
            }

            # Adjust TLD for different voices
            if feeling in ['funny', 'excited']:
                tts_config['tld'] = 'co.uk'  # British accent for variety
            elif feeling in ['serious', 'dramatic']:
                tts_config['tld'] = 'com.au'  # Australian for deeper tone
            elif feeling == 'educational':
                tts_config['tld'] = 'ca'  # Canadian for clarity

            # Enhance text for better gTTS output
            enhanced_text = self._enhance_text_for_naturalness(text, feeling)

            tts = gTTS(text=enhanced_text, **tts_config)
            audio_path = os.path.join(tempfile.gettempdir(), f"gtts_enhanced_{uuid.uuid4()}.mp3")
            tts.save(audio_path)

            logger.info(f"✅ Enhanced gTTS fallback generated: {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"❌ Even enhanced gTTS fallback failed: {e}")
            raise

    def get_available_voices(self) -> Dict[str, Any]:
        """Get available Google Cloud TTS voices"""
        try:
            voices = self.client.list_voices()

            available_voices = {}
            for voice in voices.voices:
                if voice.language_codes[0] == "en-US":
                    available_voices[voice.name] = {
                        "gender": voice.ssml_gender.name,
                        "language": voice.language_codes[0],
                        "natural_sample_rate": voice.natural_sample_rate_hertz
                    }

            return available_voices

        except Exception as e:
            logger.error(f"❌ Failed to get available voices: {e}")
            return {}

