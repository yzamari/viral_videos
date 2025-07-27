"""Google Cloud Text-to-Speech service implementation."""
import os
import time
from typing import List, Optional, Dict, Any

from src.ai.interfaces.base import AIServiceConfig, AIProvider
from src.ai.interfaces.speech_synthesis import (
    SpeechSynthesisService,
    SpeechSynthesisRequest,
    SpeechSynthesisResponse,
    MultilingualSpeechRequest,
    Voice
)
from src.generators.google_tts_client import GoogleTTSClient, GoogleVoiceType
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class GoogleTTSService(SpeechSynthesisService):
    """Google Cloud TTS implementation of speech synthesis service."""
    
    def __init__(self, config: AIServiceConfig):
        """Initialize Google TTS service.
        
        Args:
            config: Service configuration
        """
        super().__init__(config)
        
        # Get credentials path from config
        credentials_path = config.custom_config.get('credentials_path') or \
                          os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        # Initialize the underlying Google TTS client
        self.client = GoogleTTSClient(credentials_path=credentials_path)
        logger.info("Initialized Google Cloud TTS service")
        
        # Default voice mapping
        self.default_voice = config.custom_config.get('default_voice', GoogleVoiceType.EN_US_NEURAL2_J)
    
    async def synthesize(self, request: SpeechSynthesisRequest) -> SpeechSynthesisResponse:
        """Synthesize speech using Google Cloud TTS.
        
        Args:
            request: Speech synthesis request
            
        Returns:
            Speech synthesis response
        """
        start_time = time.time()
        
        try:
            # Map voice_id to GoogleVoiceType if needed
            voice = request.voice_id or self.default_voice
            if isinstance(voice, str) and not voice.startswith('en-'):
                # Try to find a matching voice type
                voice = self._map_voice_id(voice)
            
            # Generate audio using the client
            audio_path, duration = self.client.synthesize_speech(
                text=request.text,
                voice_name=voice,
                speaking_rate=request.speed,
                pitch=request.pitch,
                volume_gain_db=self._volume_to_db(request.volume),
                language_code=request.language
            )
            
            generation_time = time.time() - start_time
            
            return SpeechSynthesisResponse(
                audio_path=audio_path,
                duration=duration,
                metadata={
                    'voice': voice,
                    'language': request.language,
                    'speed': request.speed,
                    'pitch': request.pitch,
                    'provider': 'google_tts'
                },
                provider_used='google_tts',
                sample_rate=24000,  # Google TTS default
                channels=1  # Mono by default
            )
            
        except Exception as e:
            logger.error(f"Error synthesizing speech with Google TTS: {str(e)}")
            raise
    
    async def get_voices(self, language: Optional[str] = None) -> List[Voice]:
        """Get available voices from Google Cloud TTS.
        
        Args:
            language: Optional language filter (e.g., 'en', 'es')
            
        Returns:
            List of available voices
        """
        voices = []
        
        # Map GoogleVoiceType enum to Voice objects
        for voice_type in GoogleVoiceType:
            voice_name = voice_type.value
            
            # Extract language from voice name (e.g., 'en-US' from 'en-US-Neural2-J')
            voice_language = '-'.join(voice_name.split('-')[:2])
            
            # Filter by language if specified
            if language and not voice_language.startswith(language):
                continue
            
            # Determine gender from voice name
            gender = self._determine_gender(voice_name)
            
            voices.append(Voice(
                id=voice_name,
                name=voice_name,
                language=voice_language,
                gender=gender,
                description=f"Google {voice_name}",
                provider='google_tts'
            ))
        
        return voices
    
    async def synthesize_multilingual(self, request: MultilingualSpeechRequest) -> SpeechSynthesisResponse:
        """Synthesize multilingual speech.
        
        Google TTS can handle multiple languages by switching voices.
        
        Args:
            request: Multilingual speech synthesis request
            
        Returns:
            Speech synthesis response with concatenated audio
        """
        if hasattr(self.client, 'synthesize_multilingual'):
            # Use client's multilingual support if available
            audio_path, duration = self.client.synthesize_multilingual(
                segments=request.segments,
                transition_duration=request.transition_duration
            )
            
            return SpeechSynthesisResponse(
                audio_path=audio_path,
                duration=duration,
                metadata={
                    'segments': len(request.segments),
                    'languages': list(set(s['language'] for s in request.segments)),
                    'provider': 'google_tts'
                },
                provider_used='google_tts'
            )
        else:
            # Fallback to base implementation
            return await super().synthesize_multilingual(request)
    
    def _map_voice_id(self, voice_id: str) -> str:
        """Map generic voice IDs to Google voice names.
        
        Args:
            voice_id: Generic voice ID
            
        Returns:
            Google voice name
        """
        mapping = {
            'male': GoogleVoiceType.EN_US_NEURAL2_J,
            'female': GoogleVoiceType.EN_US_NEURAL2_F,
            'narrator': GoogleVoiceType.EN_US_STUDIO_Q,
            'conversational': GoogleVoiceType.EN_US_JOURNEY_D,
            'young_male': GoogleVoiceType.EN_US_NEURAL2_I,
            'young_female': GoogleVoiceType.EN_US_NEURAL2_C
        }
        
        return mapping.get(voice_id.lower(), self.default_voice)
    
    def _volume_to_db(self, volume: float) -> float:
        """Convert volume (0-2) to decibels.
        
        Args:
            volume: Volume level (0-2)
            
        Returns:
            Volume in decibels
        """
        # Map 0-2 to -20 to +20 dB
        return (volume - 1.0) * 20.0
    
    def _determine_gender(self, voice_name: str) -> str:
        """Determine gender from voice name.
        
        Args:
            voice_name: Google voice name
            
        Returns:
            'male', 'female', or 'neutral'
        """
        # Based on Google's voice naming convention
        if any(letter in voice_name for letter in ['D', 'I', 'J', 'Q']):
            return 'male'
        elif any(letter in voice_name for letter in ['A', 'C', 'F', 'G', 'H', 'O']):
            return 'female'
        return 'neutral'
    
    def validate_config(self) -> None:
        """Validate service configuration."""
        # Google TTS will use ADC if no explicit credentials
        pass
    
    async def estimate_cost(self, request: Any) -> float:
        """Estimate cost for speech synthesis.
        
        Google Cloud TTS pricing (as of 2025):
        - Neural2/Journey voices: $16 per 1 million characters
        - Studio voices: $160 per 1 million characters
        
        Args:
            request: Speech synthesis request
            
        Returns:
            Estimated cost in USD
        """
        if isinstance(request, SpeechSynthesisRequest):
            char_count = len(request.text)
            
            # Check if using Studio voice
            if request.voice_id and 'Studio' in request.voice_id:
                # Studio voices: $160 per 1M chars
                return (char_count / 1_000_000) * 160
            else:
                # Neural2/Journey voices: $16 per 1M chars
                return (char_count / 1_000_000) * 16
        
        return 0.0