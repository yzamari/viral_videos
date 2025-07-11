"""
Service interfaces for external service abstraction
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from ..entities.video_entity import Platform


class VideoGenerationService(ABC):
    """Abstract service for video generation"""
    
    @abstractmethod
    async def generate_content(
        self,
        script_content: Dict[str, Any],
        platform: Platform,
        config: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """
        Generate video content (clips and images)
        
        Returns:
            Tuple of (video_clips, image_files)
        """
        pass
    
    @abstractmethod
    async def compose_final_video(
        self,
        video_clips: List[str],
        audio_files: List[str],
        image_files: List[str],
        script_content: Dict[str, Any],
        platform: Platform,
        config: Dict[str, Any]
    ) -> str:
        """
        Compose final video from components
        
        Returns:
            Path to final video file
        """
        pass


class ScriptGenerationService(ABC):
    """Abstract service for script generation"""
    
    @abstractmethod
    async def generate_script(
        self,
        mission: str,
        platform: Platform,
        duration_seconds: int,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate script content
        
        Returns:
            Script content dictionary
        """
        pass


class AudioGenerationService(ABC):
    """Abstract service for audio generation"""
    
    @abstractmethod
    async def generate_audio(
        self,
        script_content: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Generate audio files from script
        
        Returns:
            List of audio file paths
        """
        pass 