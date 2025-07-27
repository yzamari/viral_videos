"""
Video Generator V2 - Uses AI Service Interfaces
This is a refactored version that uses dependency injection and interfaces
"""

import os
import time
import uuid
import re
import warnings
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import subprocess

# Suppress pkg_resources deprecation warnings
warnings.filterwarnings("ignore", category=UserWarning, module="imageio_ffmpeg")

from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from ..utils.logging_config import get_logger
from ..config.ai_model_config import DEFAULT_AI_MODEL
from ..config.tts_config import tts_config

# AI Service Interfaces
from ..ai.manager import AIServiceManager
from ..ai.interfaces.base import AIServiceType
from ..ai.interfaces.image_generation import ImageGenerationRequest
from ..ai.interfaces.speech_synthesis import SpeechSynthesisRequest
from ..ai.interfaces.video_generation import VideoGenerationRequest

# Other dependencies (unchanged)
from ..generators.enhanced_script_processor import EnhancedScriptProcessor
from ..generators.director import Director
from ..agents.voice_director_agent import VoiceDirectorAgent
from ..agents.overlay_positioning_agent import OverlayPositioningAgent
from ..agents.visual_style_agent import VisualStyleAgent
from ..generators.hashtag_generator import HashtagGenerator
from ..utils.session_context import SessionContext, create_session_context
from ..utils.duration_coordinator import DurationCoordinator
from ..utils.overlay_enhancement import OverlayEnhancer
from ..utils.audio_duration_manager import AudioDurationManager, AudioDurationAnalysis
from ..utils.duration_feedback_system import DurationFeedbackSystem
from ..utils.professional_text_renderer import (
    ProfessionalTextRenderer, 
    TextOverlay, 
    TextStyle, 
    TextLayout, 
    TextPosition, 
    TextAlignment
)
from ..config import video_config
from .png_overlay_handler import PNGOverlayHandler
from .video_generator import VideoGenerationResult  # Reuse the result class

logger = get_logger(__name__)


class VideoGeneratorV2:
    """Refactored video generator that uses AI service interfaces"""
    
    def __init__(self, 
                 service_manager: AIServiceManager,
                 api_key: str,
                 use_real_veo2: bool = True,
                 use_vertex_ai: bool = True,
                 vertex_project_id: Optional[str] = None,
                 vertex_location: Optional[str] = None,
                 vertex_gcs_bucket: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 prefer_veo3: bool = False):
        """
        Initialize video generator with AI service interfaces
        
        Args:
            service_manager: AI service manager for getting service interfaces
            api_key: Google AI API key (for legacy components)
            use_real_veo2: Whether to use VEO for video generation
            use_vertex_ai: Whether to use Vertex AI or Google AI Studio
            vertex_project_id: Vertex AI project ID
            vertex_location: Vertex AI location
            vertex_gcs_bucket: GCS bucket for Vertex AI results
            output_dir: Output directory for generated content
            prefer_veo3: Whether to prefer VEO-3 over VEO-2
        """
        self.service_manager = service_manager
        self.api_key = api_key
        self.use_real_veo2 = use_real_veo2
        self.use_vertex_ai = use_vertex_ai
        self.prefer_veo3 = prefer_veo3
        
        # Get AI services from manager
        self.image_service = service_manager.get_service(AIServiceType.IMAGE_GENERATION)
        self.speech_service = service_manager.get_service(AIServiceType.SPEECH_SYNTHESIS)
        self.video_service = service_manager.get_service(AIServiceType.VIDEO_GENERATION)
        self.text_service = service_manager.get_service(AIServiceType.TEXT_GENERATION)
        
        # Setup directories
        if output_dir:
            self.output_dir = output_dir
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = f"outputs/video_{timestamp}"
        
        # Create output directories
        self.clips_dir = os.path.join(self.output_dir, "clips")
        self.audio_dir = os.path.join(self.output_dir, "audio")
        self.images_dir = os.path.join(self.output_dir, "images")
        self.overlays_dir = os.path.join(self.output_dir, "overlays")
        
        for dir_path in [self.output_dir, self.clips_dir, self.audio_dir, 
                         self.images_dir, self.overlays_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Initialize other components (unchanged from original)
        self.text_renderer = ProfessionalTextRenderer(use_skia=True)
        self.hashtag_generator = HashtagGenerator(api_key)
        self.overlay_handler = PNGOverlayHandler(self.overlays_dir)
        
        # Initialize enhanced script processor
        self.script_processor = EnhancedScriptProcessor(api_key)
        
        # Initialize agents
        self.voice_director = VoiceDirectorAgent(api_key)
        self.overlay_agent = OverlayPositioningAgent(api_key)
        self.style_agent = VisualStyleAgent(api_key)
        
        # Initialize director
        self.director = Director()
        
        # Initialize duration coordinator
        self.duration_coordinator = DurationCoordinator()
        
        # Initialize overlay enhancer
        self.overlay_enhancer = OverlayEnhancer()
        
        # Initialize audio duration manager
        self.audio_duration_manager = AudioDurationManager()
        
        # Initialize duration feedback system
        self.duration_feedback = DurationFeedbackSystem(self.output_dir)
        
        logger.info(f"Initialized VideoGeneratorV2 with service interfaces")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Using VEO: {use_real_veo2}, Prefer VEO3: {prefer_veo3}")
    
    async def generate_image_for_scene(self, prompt: str, style: Optional[str] = None, 
                                     aspect_ratio: str = "16:9") -> Optional[str]:
        """Generate an image for a scene using the image service interface"""
        try:
            request = ImageGenerationRequest(
                prompt=prompt,
                style=style,
                aspect_ratio=aspect_ratio,
                num_images=1
            )
            
            response = await self.image_service.generate_image(request)
            
            if response.image_paths:
                return response.first_image
            else:
                logger.error(f"No image generated for prompt: {prompt}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None
    
    async def generate_speech(self, text: str, voice_id: Optional[str] = None,
                            language: str = "en") -> Optional[str]:
        """Generate speech audio using the speech service interface"""
        try:
            request = SpeechSynthesisRequest(
                text=text,
                voice_id=voice_id,
                language=language,
                speed=1.0,
                pitch=0.0
            )
            
            response = await self.speech_service.synthesize(request)
            
            if response.audio_path:
                return response.audio_path
            else:
                logger.error(f"No audio generated for text: {text[:50]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return None
    
    async def generate_video_clip(self, prompt: str, duration: float,
                                style: Optional[str] = None,
                                aspect_ratio: str = "16:9") -> Optional[str]:
        """Generate a video clip using the video service interface"""
        try:
            request = VideoGenerationRequest(
                prompt=prompt,
                duration=duration,
                style=style,
                aspect_ratio=aspect_ratio
            )
            
            response = await self.video_service.generate_video(request)
            
            if response.video_path:
                return response.video_path
            elif response.job_id:
                # Handle async generation
                logger.info(f"Video generation started with job ID: {response.job_id}")
                # Wait for completion
                final_status = await self.video_service.wait_for_completion(response.job_id)
                return final_status.video_path
            else:
                logger.error(f"No video generated for prompt: {prompt}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return None
    
    # Copy other methods from original VideoGenerator and update to use service interfaces
    # This is a starting point - the full implementation would require copying and updating
    # all methods from the original VideoGenerator class