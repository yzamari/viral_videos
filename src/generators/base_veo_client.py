#!/usr/bin/env python3
"""
Base VEO Client - Abstract base class for all VEO clients
Provides clean interface and common functionality
"""

import os
import sys
import time
import subprocess
from abc  import ABC, abstractmethod
from typing import Dict, Optional, Any

# Add src to path for imports
if 'src' not in sys.path:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.utils.logging_config import get_logger
except ImportError:
    from utils.logging_config import get_logger

logger = get_logger(__name__)

class BaseVeoClient(ABC):
    """
    Abstract base class for VEO clients
    Provides common functionality and interface
    """

    def __init__(self, project_id: str, location: str, output_dir: str):
        """
        Initialize base VEO client

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location
            output_dir: Output directory for generated videos
        """
        self.project_id = project_id
        self.location = location
        self.output_dir = output_dir
        self.clips_dir = os.path.join(output_dir, "veo_clips")
        os.makedirs(self.clips_dir, exist_ok=True)

        # Authentication
        self.access_token = None
        self.token_expiry = 0

        # Availability status
        self._is_available = False
        self._last_check = 0

        # Initialize client
        self._initialize()

    def _initialize(self):
        """Initialize the client and check availability"""
        try:
            self._refresh_access_token()
            self._is_available = self._check_availability()
            if self._is_available:
                logger.info(f"✅ {self.__class__.__name__} initialized successfully")
            else:
                logger.warning(f"⚠️ {self.__class__.__name__} not available")
        except Exception as e:
            logger.error(f"❌ {self.__class__.__name__} initialization failed: {e}")
            self._is_available = False

    def _refresh_access_token(self):
        """Get fresh access token using gcloud CLI"""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True
            )
            self.access_token = result.stdout.strip()
            self.token_expiry = time.time() + 3600  # Token valid for 1 hour
            logger.debug("🔑 Access token refreshed")
        except Exception as e:
            raise Exception(f"Failed to get access token: {e}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers with fresh token"""
        # Refresh token if expired
        if not self.access_token or (self.token_expiry and
                time.time() >= self.token_expiry - 300):
            self._refresh_access_token()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    @property
    def is_available(self) -> bool:
        """Check if client is available"""
        # Re-check availability every 5 minutes
        if time.time() - self._last_check > 300:
            self._is_available = self._check_availability()
            self._last_check = time.time()
        return self._is_available

    @abstractmethod
    def _check_availability(self) -> bool:
        """Check if the VEO model is available"""
        pass

    @abstractmethod
    def generate_video(self, prompt: str, duration: float,
                      clip_id: str = "clip", image_path: Optional[str] = None) -> str:
        """
        Generate video using VEO model

        Args:
            prompt: Text description for video generation
            duration: Video duration in seconds
            clip_id: Unique identifier for the clip
            image_path: Optional image for image-to-video generation

        Returns:
            Path to generated video file
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get client status information"""
        return {
            "model_name": self.get_model_name(),
            "is_available": self.is_available,
            "project_id": self.project_id,
            "location": self.location,
            "output_dir": self.output_dir,
            "token_valid": self.access_token is not None and
                    time.time() < self.token_expiry
        }

    def _create_fallback_clip(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create fallback clip when VEO generation fails"""
        logger.info(f"🎨 Creating fallback for: {prompt[:50]}...")
        
        # First try image generation if content was filtered
        if hasattr(self, '_last_error') and 'filtered' in str(getattr(self, '_last_error', '')).lower():
            logger.info("🖼️ Content was filtered, attempting image generation fallback...")
            image_video = self._try_image_generation_fallback(prompt, duration, clip_id)
            if image_video:
                return image_video
        
        try:
            # Create a simple colored video as fallback using FFmpeg
            fallback_path = os.path.join(self.clips_dir, f"fallback_{clip_id}.mp4")
            
            # Ensure clips directory exists
            os.makedirs(self.clips_dir, exist_ok=True)
            
            # Create a colorful test pattern video with FFmpeg
            import subprocess
            import random
            
            # Generate random colors for variety
            colors = [
                "red", "green", "blue", "yellow", "magenta", "cyan", 
                "orange", "purple", "pink", "lime", "navy", "teal"
            ]
            color = random.choice(colors)
            
            # Create video with text overlay showing the prompt
            # Properly escape text for FFmpeg drawtext filter
            safe_text = prompt[:30].replace("'", "").replace('"', '').replace(':', '').replace('!', '').replace('?', '').replace(',', '')
            
            # Use portrait dimensions (9:16) to match VEO output
            video_dimensions = "720x1280"
            
            cmd = [
                'ffmpeg', '-f', 'lavfi', 
                '-i', f'color=c={color}:size={video_dimensions}:duration={duration}',
                '-vf', f'drawtext=text="{safe_text}":fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '24',
                '-y', fallback_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(fallback_path):
                file_size = os.path.getsize(fallback_path) / (1024 * 1024)
                logger.info(f"✅ Fallback video created: {fallback_path} ({file_size:.1f}MB)")
                return fallback_path
            else:
                logger.error(f"❌ FFmpeg fallback failed: {result.stderr}")
                return self._create_minimal_fallback(prompt, duration, clip_id)
                
        except Exception as e:
            logger.error(f"❌ Fallback creation failed: {e}")
            return self._create_minimal_fallback(prompt, duration, clip_id)
    
    def _create_minimal_fallback(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create minimal fallback using basic FFmpeg"""
        try:
            fallback_path = os.path.join(self.clips_dir, f"minimal_{clip_id}.mp4")
            
            # Create simple solid color video
            # Use portrait dimensions (9:16) to match VEO output
            video_dimensions = "720x1280"
            
            cmd = [
                'ffmpeg', '-f', 'lavfi', 
                '-i', f'color=c=blue:size={video_dimensions}:duration={duration}',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '24',
                '-y', fallback_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and os.path.exists(fallback_path):
                logger.info(f"✅ Minimal fallback created: {fallback_path}")
                return fallback_path
            else:
                logger.error(f"❌ Even minimal fallback failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Minimal fallback failed: {e}")
            return ""

    def _try_image_generation_fallback(self, prompt: str, duration: float, clip_id: str) -> Optional[str]:
        """Try to generate video using image generation as fallback"""
        try:
            logger.info("🖼️ Attempting image generation fallback...")
            
            # Try to import and use Gemini image client
            try:
                from .gemini_image_client import GeminiImageClient
                import os
                
                # Get API key from environment
                api_key = os.environ.get('GEMINI_API_KEY')
                if not api_key:
                    logger.warning("⚠️ No GEMINI_API_KEY found, skipping image generation")
                    return None
                
                # Initialize image client
                image_client = GeminiImageClient(api_key, self.output_dir)
                
                # Create prompts for image generation
                prompts = [{
                    'description': prompt,
                    'duration': duration,
                    'style': 'cinematic'
                }]
                
                # Generate config
                config = {
                    'duration_seconds': duration,
                    'platform': 'instagram',  # Default to Instagram for portrait videos
                    'is_fallback_generation': True
                }
                
                # Generate image-based clips
                clips = image_client.generate_image_based_clips(prompts, config, clip_id)
                
                if clips and len(clips) > 0 and 'path' in clips[0]:
                    video_path = clips[0]['path']
                    if os.path.exists(video_path):
                        logger.info(f"✅ Image generation fallback succeeded: {video_path}")
                        return video_path
                    
            except ImportError:
                logger.warning("⚠️ Gemini image client not available")
            except Exception as e:
                logger.warning(f"⚠️ Image generation fallback failed: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Image generation fallback error: {e}")
            return None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(" \
               f"model={self.get_model_name()}, " \
               f"available={self.is_available})"
