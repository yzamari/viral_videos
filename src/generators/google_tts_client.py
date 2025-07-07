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
    # English Neural Voices (High Quality)
    EN_US_NEURAL2_A = "en-US-Neural2-A"  # Female, warm
    EN_US_NEURAL2_C = "en-US-Neural2-C"  # Female, young
    EN_US_NEURAL2_D = "en-US-Neural2-D"  # Male, deep
    EN_US_NEURAL2_F = "en-US-Neural2-F"  # Female, mature
    EN_US_NEURAL2_G = "en-US-Neural2-G"  # Female, young
    EN_US_NEURAL2_H = "en-US-Neural2-H"  # Female, confident
    EN_US_NEURAL2_I = "en-US-Neural2-I"  # Male, young
    EN_US_NEURAL2_J = "en-US-Neural2-J"  # Male, mature
    
    # Journey Voices (Most Advanced)
    EN_US_JOURNEY_D = "en-US-Journey-D"  # Male, conversational
    EN_US_JOURNEY_F = "en-US-Journey-F"  # Female, conversational
    
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
                GoogleVoiceType.EN_US_NEURAL2_A: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_C: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_D: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_NEURAL2_F: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_G: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_H: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_NEURAL2_I: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_NEURAL2_J: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_JOURNEY_D: texttospeech.SsmlVoiceGender.MALE,
                GoogleVoiceType.EN_US_JOURNEY_F: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_STUDIO_O: texttospeech.SsmlVoiceGender.FEMALE,
                GoogleVoiceType.EN_US_STUDIO_Q: texttospeech.SsmlVoiceGender.MALE,
            }
            
            # Voice mapping for different emotions/feelings
            self.emotion_voice_mapping = {
                "funny": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_F,  # Use Journey voice for more natural sound
                    "pitch": 0.5,  # Much lower pitch
                    "speed": 0.85   # Slower speed
                },
                "excited": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_F,
                    "pitch": 1.0,   # Lower pitch
                    "speed": 0.9    # Slower speed
                },
                "serious": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_D,
                    "pitch": -0.5,  # Slightly lower
                    "speed": 0.8    # Much slower for serious tone
                },
                "dramatic": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_D,
                    "pitch": -0.5,  # Lower pitch
                    "speed": 0.75   # Slower for dramatic effect
                },
                "neutral": {
                    "voice": GoogleVoiceType.EN_US_JOURNEY_F,
                    "pitch": 0.0,   # Natural pitch
                    "speed": 0.85   # Slightly slower than default
                }
            }
            
            logger.info("✅ Google Cloud TTS client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google TTS client: {e}")
            raise
    
    def _enhance_with_ssml(self, text: str, feeling: str, voice_config: dict) -> str:
        """Enhance text with SSML markup for better emotional expression"""
        
        # Clean text first
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        if feeling == "dramatic":
            # Add dramatic pauses and emphasis (no pitch for Studio voices)
            ssml = f"""<speak>
                <prosody rate="slow">
                    <emphasis level="strong">{text}</emphasis>
                </prosody>
            </speak>"""
            
        elif feeling == "excited":
            # Fast pace with high pitch
            ssml = f"""<speak>
                <prosody rate="fast" pitch="+3st">
                    {text}
                </prosody>
            </speak>"""
            
        elif feeling == "funny":
            # Variable pace and pitch for comedic effect
            sentences = text.split('. ')
            ssml_parts = []
            for i, sentence in enumerate(sentences):
                if i % 2 == 0:
                    ssml_parts.append(f'<prosody rate="fast" pitch="+2st">{sentence}</prosody>')
                else:
                    ssml_parts.append(f'<prosody rate="medium">{sentence}</prosody>')
                if i < len(sentences) - 1:
                    ssml_parts.append('<break time="300ms"/>')
            
            ssml = f"<speak>{' '.join(ssml_parts)}</speak>"
            
        else:
            # Default SSML with natural pauses
            ssml = f"""<speak>
                <prosody rate="{voice_config['speed']}" pitch="{voice_config['pitch']}st">
                    {text}
                </prosody>
            </speak>"""
        
        return ssml
    
    def generate_speech(self, text: str, feeling: str = "neutral", 
                       narrative: str = "neutral", duration_target: float = 30,
                       use_ssml: bool = False, voice_override: Optional[str] = None) -> str:
        """Generate high-quality speech with Google Cloud TTS"""
        try:
            logger.info(f"🎤 Generating Google neural voice ({feeling} emotion)")
            
            # Get voice configuration for emotion
            voice_config = self.emotion_voice_mapping.get(feeling.lower(), self.emotion_voice_mapping["neutral"])
            
            # Allow voice override from environment or parameter
            selected_voice = voice_override or os.getenv("GOOGLE_TTS_VOICE_TYPE", voice_config["voice"])
            
            # Get appropriate gender for the voice
            try:
                voice_gender = self.voice_gender_map.get(GoogleVoiceType(selected_voice), texttospeech.SsmlVoiceGender.FEMALE)
            except ValueError:
                # If voice not in enum, default to female
                voice_gender = texttospeech.SsmlVoiceGender.FEMALE
            
            # Use text input only - Journey/Neural2 voices don't support SSML
            # We'll control emotion through voice selection and audio config instead
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request with neural voice
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=selected_voice,
                ssml_gender=voice_gender
            )
            
            # Configure audio with optimal settings (no pitch for Journey/Neural2 voices)
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=voice_config["speed"],
                # pitch=voice_config["pitch"],  # Journey voices don't support pitch
                sample_rate_hertz=24000,
                effects_profile_id=["headphone-class-device"]  # Optimize for headphones
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
                logger.info(f"✅ Google neural voice generated: {audio_path} ({file_size:.2f}MB)")
                logger.info(f"   Voice: {selected_voice}, Speed: {voice_config['speed']}x, Pitch: {voice_config['pitch']}")
                return audio_path
            else:
                raise Exception("Generated audio file is empty or missing")
                
        except Exception as e:
            logger.error(f"❌ Google TTS generation failed: {e}")
            # Fallback to basic gTTS if Cloud TTS fails
            return self._fallback_to_gtts(text, feeling)
    
    def _fallback_to_gtts(self, text: str, feeling: str) -> str:
        """Fallback to basic gTTS if Cloud TTS fails"""
        try:
            from gtts import gTTS
            
            logger.warning("🔄 Falling back to basic gTTS...")
            
            tld_mapping = {
                "funny": "co.uk",
                "excited": "co.uk", 
                "serious": "com",
                "dramatic": "com",
                "neutral": "com"
            }
            
            tld = tld_mapping.get(feeling, "com")
            
            tts = gTTS(text=text, lang='en', tld=tld, slow=False)
            audio_path = os.path.join(tempfile.gettempdir(), f"gtts_fallback_{uuid.uuid4()}.mp3")
            tts.save(audio_path)
            
            logger.info(f"✅ gTTS fallback generated: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ Even gTTS fallback failed: {e}")
            raise
