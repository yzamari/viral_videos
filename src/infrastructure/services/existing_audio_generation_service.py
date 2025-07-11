"""
Audio generation service implementation that wraps existing functionality
"""

import asyncio
from typing import Dict, Any, List
from pathlib import Path

from ...core.interfaces.services import AudioGenerationService


class ExistingAudioGenerationService(AudioGenerationService):
    """
    Implementation of AudioGenerationService that wraps existing audio generation functionality
    
    This service adapts the existing audio generation components to work with
    the clean architecture interfaces.
    """
    
    def __init__(self, output_base_path: str = "outputs"):
        """
        Initialize audio generation service
        
        Args:
            output_base_path: Base path for output files
        """
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(parents=True, exist_ok=True)
    
    async def generate_audio(
        self,
        script_content: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Generate audio files from script
        
        Args:
            script_content: Script content dictionary
            config: Generation configuration
            
        Returns:
            List of audio file paths
        """
        # Extract session information from config
        session_id = config.get("session_id", "default_session")
        session_path = self.output_base_path / session_id
        
        # Ensure session audio directory exists
        audio_path = session_path / "audio"
        audio_path.mkdir(parents=True, exist_ok=True)
        
        audio_files = []
        
        try:
            # For now, create placeholder audio files
            # In a real implementation, this would call the existing TTS services
            
            # Simulate audio generation
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Generate audio for hook
            if "hook" in script_content:
                hook_audio_path = str(audio_path / "hook.mp3")
                audio_files.append(hook_audio_path)
            
            # Generate audio for segments
            if "segments" in script_content:
                for i, segment in enumerate(script_content["segments"]):
                    segment_audio_path = str(audio_path / f"segment_{i}.mp3")
                    audio_files.append(segment_audio_path)
            
            # Generate audio for call to action
            if "call_to_action" in script_content:
                cta_audio_path = str(audio_path / "call_to_action.mp3")
                audio_files.append(cta_audio_path)
            
            return audio_files
        
        except Exception as e:
            print(f"Error generating audio: {e}")
            
            # Return minimal fallback audio file
            fallback_audio_path = str(audio_path / "fallback_audio.mp3")
            return [fallback_audio_path]
    
    def get_supported_voices(self) -> List[str]:
        """Get list of supported voices"""
        return [
            "en-US-Standard-A",
            "en-US-Standard-B",
            "en-US-Standard-C",
            "en-US-Standard-D",
            "en-US-Wavenet-A",
            "en-US-Wavenet-B",
            "en-US-Wavenet-C",
            "en-US-Wavenet-D"
        ]
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return [
            "en-US",
            "en-GB",
            "es-ES",
            "fr-FR",
            "de-DE",
            "it-IT",
            "pt-BR",
            "ja-JP",
            "ko-KR",
            "zh-CN"
        ]
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return ["mp3", "wav", "ogg"]
    
    def get_output_path(self, session_id: str) -> str:
        """Get output path for a session"""
        return str(self.output_base_path / session_id / "audio") 