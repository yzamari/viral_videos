"""
Advanced AI Voice Generation Module
Supports multiple state-of-the-art AI voice providers
"""
import os
import requests
import tempfile
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum
import uuid

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class VoiceProvider(str, Enum):
    """Supported AI voice providers"""
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    AZURE = "azure"
    AWS_POLLY = "aws_polly"
    GOOGLE_NEURAL = "google_neural"
    GTTS_FALLBACK = "gtts_fallback"  # Keep as emergency fallback

class VoiceEmotion(str, Enum):
    """Voice emotions and styles"""
    NEUTRAL = "neutral"
    EXCITED = "excited"
    SERIOUS = "serious"
    FUNNY = "funny"
    DRAMATIC = "dramatic"
    INSPIRATIONAL = "inspirational"
    CYNICAL = "cynical"
    CALM = "calm"

class AIVoiceProvider(ABC):
    """Abstract base class for AI voice providers"""
    
    @abstractmethod
    def generate_speech(self, text: str, emotion: VoiceEmotion, duration_target: float) -> str:
        """Generate speech audio file"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices"""
        pass

class ElevenLabsProvider(AIVoiceProvider):
    """ElevenLabs AI Voice Generation - Industry Leader"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # High-quality voices for different emotions
        self.voice_mapping = {
            VoiceEmotion.EXCITED: "EXAVITQu4vr4xnSDxMaL",  # Bella - energetic
            VoiceEmotion.SERIOUS: "21m00Tcm4TlvDq8ikWAM",   # Rachel - professional
            VoiceEmotion.FUNNY: "AZnzlk1XvdvUeBnXmlld",     # Domi - playful
            VoiceEmotion.DRAMATIC: "CYw3kZ02Hs0563khs1Fj",  # Dave - dramatic
            VoiceEmotion.INSPIRATIONAL: "EXAVITQu4vr4xnSDxMaL", # Bella - uplifting
            VoiceEmotion.CYNICAL: "onwK4e9ZLuTAKqWW03F9",   # Daniel - sardonic
            VoiceEmotion.CALM: "ThT5KcBeYPX3keUQqHPh",      # Dorothy - soothing
            VoiceEmotion.NEUTRAL: "21m00Tcm4TlvDq8ikWAM"    # Rachel - default
        }
    
    def generate_speech(self, text: str, emotion: VoiceEmotion, duration_target: float) -> str:
        """Generate ultra-realistic AI speech with ElevenLabs"""
        try:
            voice_id = self.voice_mapping.get(emotion, self.voice_mapping[VoiceEmotion.NEUTRAL])
            
            # Advanced ElevenLabs settings for realistic speech
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Highest quality model
                "voice_settings": {
                    "stability": 0.5,  # Balanced for natural variation
                    "similarity_boost": 0.75,  # High similarity to voice
                    "style": 0.5,  # Natural style
                    "use_speaker_boost": True  # Enhanced clarity
                }
            }
            
            # Add emotion-specific adjustments
            if emotion == VoiceEmotion.EXCITED:
                data["voice_settings"]["stability"] = 0.3  # More variation
                data["voice_settings"]["style"] = 0.8      # More expressive
            elif emotion == VoiceEmotion.SERIOUS:
                data["voice_settings"]["stability"] = 0.8  # More stable
                data["voice_settings"]["style"] = 0.2      # Less expressive
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            logger.info(f"🎤 Generating {emotion} voice with ElevenLabs...")
            
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                # Save to temporary file
                audio_path = os.path.join(tempfile.gettempdir(), f"elevenlabs_voice_{uuid.uuid4()}.mp3")
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = os.path.getsize(audio_path) / (1024 * 1024)
                logger.info(f"✅ ElevenLabs voice generated: {audio_path} ({file_size:.1f}MB)")
                return audio_path
            else:
                raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ ElevenLabs generation failed: {e}")
            raise
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get ElevenLabs available voices"""
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            return response.json() if response.status_code == 200 else {}
        except:
            return {}

class OpenAIVoiceProvider(AIVoiceProvider):
    """OpenAI Voice Generation - ChatGPT Quality"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # OpenAI voices mapped to emotions
        self.voice_mapping = {
            VoiceEmotion.EXCITED: "nova",     # Energetic and bright
            VoiceEmotion.SERIOUS: "echo",     # Professional and clear
            VoiceEmotion.FUNNY: "fable",      # Warm and playful
            VoiceEmotion.DRAMATIC: "onyx",    # Deep and dramatic
            VoiceEmotion.INSPIRATIONAL: "shimmer", # Uplifting
            VoiceEmotion.CYNICAL: "alloy",    # Neutral with edge
            VoiceEmotion.CALM: "nova",        # Gentle
            VoiceEmotion.NEUTRAL: "alloy"     # Balanced default
        }
    
    def generate_speech(self, text: str, emotion: VoiceEmotion, duration_target: float) -> str:
        """Generate speech with OpenAI's advanced TTS"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            voice = self.voice_mapping.get(emotion, "alloy")
            
            logger.info(f"🎤 Generating {emotion} voice with OpenAI ({voice})...")
            
            response = client.audio.speech.create(
                model="tts-1-hd",  # High definition model
                voice=voice,
                input=text,
                speed=1.0
            )
            
            # Save to file
            audio_path = os.path.join(tempfile.gettempdir(), f"openai_voice_{uuid.uuid4()}.mp3")
            response.stream_to_file(audio_path)
            
            file_size = os.path.getsize(audio_path) / (1024 * 1024)
            logger.info(f"✅ OpenAI voice generated: {audio_path} ({file_size:.1f}MB)")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ OpenAI voice generation failed: {e}")
            raise
    
    def get_available_voices(self) -> Dict[str, Any]:
        """OpenAI has fixed set of voices"""
        return {
            "alloy": "Balanced, neutral",
            "echo": "Professional, clear", 
            "fable": "Warm, playful",
            "onyx": "Deep, dramatic",
            "nova": "Energetic, bright",
            "shimmer": "Uplifting, inspiring"
        }

class GTTSFallbackProvider(AIVoiceProvider):
    """Fallback to basic gTTS if advanced providers fail"""
    
    def generate_speech(self, text: str, emotion: VoiceEmotion, duration_target: float) -> str:
        """Basic gTTS fallback"""
        try:
            from gtts import gTTS
            
            logger.warning("🔄 Using basic gTTS fallback...")
            
            tts_config = {
                'lang': 'en',
                'slow': False,
                'tld': 'co.uk' if emotion in [VoiceEmotion.FUNNY, VoiceEmotion.EXCITED] else 'com'
            }
            
            tts = gTTS(text=text, **tts_config)
            audio_path = os.path.join(tempfile.gettempdir(), f"gtts_fallback_{uuid.uuid4()}.mp3")
            tts.save(audio_path)
            
            logger.info(f"✅ Basic TTS fallback generated: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ Even gTTS fallback failed: {e}")
            raise
    
    def get_available_voices(self) -> Dict[str, Any]:
        return {"basic": "Basic Google TTS"}

class SmartAIVoiceGenerator:
    """Smart AI Voice Generator with multiple provider support"""
    
    def __init__(self, primary_provider: VoiceProvider, api_keys: Dict[str, str]):
        self.primary_provider = primary_provider
        self.api_keys = api_keys
        self.providers = {}
        
        # Initialize available providers
        self._init_providers()
    
    def _init_providers(self):
        """Initialize AI voice providers based on available API keys"""
        
        if "elevenlabs" in self.api_keys:
            self.providers[VoiceProvider.ELEVENLABS] = ElevenLabsProvider(self.api_keys["elevenlabs"])
            logger.info("🎤 ElevenLabs provider initialized")
        
        if "openai" in self.api_keys:
            self.providers[VoiceProvider.OPENAI] = OpenAIVoiceProvider(self.api_keys["openai"])
            logger.info("🎤 OpenAI voice provider initialized")
        
        # Always have fallback
        self.providers[VoiceProvider.GTTS_FALLBACK] = GTTSFallbackProvider()
        logger.info("🔄 gTTS fallback provider initialized")
    
    def generate_emotional_voice(self, text: str, emotion: VoiceEmotion, 
                                duration_target: float, narrative: str = "neutral") -> str:
        """Generate AI voice with emotion and fallback support"""
        
        # Try primary provider first
        try:
            if self.primary_provider in self.providers:
                provider = self.providers[self.primary_provider]
                logger.info(f"🎤 Using {self.primary_provider} for {emotion} voice generation")
                return provider.generate_speech(text, emotion, duration_target)
        except Exception as e:
            logger.warning(f"⚠️ Primary provider {self.primary_provider} failed: {e}")
        
        # Try other advanced providers
        for provider_name in [VoiceProvider.ELEVENLABS, VoiceProvider.OPENAI]:
            if provider_name in self.providers and provider_name != self.primary_provider:
                try:
                    logger.info(f"🔄 Falling back to {provider_name}")
                    provider = self.providers[provider_name]
                    return provider.generate_speech(text, emotion, duration_target)
                except Exception as e:
                    logger.warning(f"⚠️ {provider_name} also failed: {e}")
        
        # Final fallback to gTTS
        try:
            logger.warning("🔄 Using final gTTS fallback")
            provider = self.providers[VoiceProvider.GTTS_FALLBACK]
            return provider.generate_speech(text, emotion, duration_target)
        except Exception as e:
            logger.error(f"❌ All voice providers failed: {e}")
            raise Exception("All AI voice generation providers failed")
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Check which providers are available"""
        status = {}
        for provider_name, provider in self.providers.items():
            try:
                # Simple test to check if provider is working
                voices = provider.get_available_voices()
                status[provider_name] = len(voices) > 0
            except:
                status[provider_name] = False
        
        return status 