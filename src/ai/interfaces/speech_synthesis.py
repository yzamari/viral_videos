"""Speech synthesis service interface."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from src.ai.interfaces.base import AIService


@dataclass
class Voice:
    """Voice information."""
    id: str
    name: str
    language: str
    gender: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None


@dataclass
class SpeechSynthesisRequest:
    """Request for speech synthesis."""
    text: str
    voice_id: Optional[str] = None
    language: str = "en"
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    output_format: str = "mp3"
    session_context: Optional[Any] = None  # SessionContext
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            'text': self.text,
            'voice_id': self.voice_id,
            'language': self.language,
            'speed': self.speed,
            'pitch': self.pitch,
            'volume': self.volume,
            'output_format': self.output_format
        }


@dataclass
class MultilingualSpeechRequest:
    """Request for multilingual speech synthesis."""
    segments: List[Dict[str, str]]  # [{'text': '...', 'language': 'en'}, ...]
    voice_id: Optional[str] = None
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    output_format: str = "mp3"
    session_context: Optional[Any] = None
    transition_duration: float = 0.5


@dataclass
class SpeechSynthesisResponse:
    """Response from speech synthesis."""
    audio_path: str
    duration: float
    metadata: Dict[str, Any]
    provider_used: str
    sample_rate: Optional[int] = None
    channels: Optional[int] = None


class SpeechSynthesisService(AIService):
    """Abstract interface for speech synthesis services."""
    
    @abstractmethod
    async def synthesize(self, request: SpeechSynthesisRequest) -> SpeechSynthesisResponse:
        """Synthesize speech from text.
        
        Args:
            request: Speech synthesis request
            
        Returns:
            Speech synthesis response with audio path and metadata
        """
        pass
    
    @abstractmethod
    async def get_voices(self, language: Optional[str] = None) -> List[Voice]:
        """Get available voices.
        
        Args:
            language: Optional language filter
            
        Returns:
            List of available voices
        """
        pass
    
    async def synthesize_multilingual(self, request: MultilingualSpeechRequest) -> SpeechSynthesisResponse:
        """Synthesize multilingual speech.
        
        Default implementation synthesizes each segment separately and concatenates.
        Providers can override for better multilingual support.
        
        Args:
            request: Multilingual speech synthesis request
            
        Returns:
            Speech synthesis response with concatenated audio
        """
        # Default implementation - providers can override
        raise NotImplementedError("Multilingual synthesis not implemented for this provider")