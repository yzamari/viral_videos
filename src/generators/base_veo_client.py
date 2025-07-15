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
    def generate_video(self, prompt: str, duration: float = 5.0,
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
        
        try:
            # Create a simple colored video as fallback
            import cv2
            import numpy as np
            
            fallback_path = os.path.join(self.clips_dir, f"fallback_{clip_id}.mp4")
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 24
            width, height = 1920, 1080
            frames = int(duration * fps)
            
            # Ensure we have at least 1 frame
            if frames < 1:
                frames = 1
            
            out = cv2.VideoWriter(fallback_path, fourcc, fps, (width, height))
            
            # Generate frames with gradient colors based on prompt
            color_base = hash(prompt) % 256
            
            for i in range(frames):
                # Create gradient frame
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                color_shift = int(255 * (i / max(frames, 1)))
                
                # Use prompt-based colors
                frame[:, :] = [
                    (color_base + color_shift) % 255,
                    (color_base + color_shift + 85) % 255,
                    (color_base + color_shift + 170) % 255
                ]
                
                out.write(frame)
            
            out.release()
            
            # Verify the fallback was created
            if os.path.exists(fallback_path) and os.path.getsize(fallback_path) > 1000:
                logger.info(f"✅ Fallback video created: {fallback_path}")
                return fallback_path
            else:
                logger.error(f"❌ Fallback video creation failed or too small")
                return self._create_minimal_fallback(clip_id, duration)
                
        except Exception as e:
            logger.error(f"❌ Error creating fallback clip: {e}")
            return self._create_minimal_fallback(clip_id, duration)
    
    def _create_minimal_fallback(self, clip_id: str, duration: float) -> str:
        """Create minimal fallback when even the colored video fails"""
        try:
            import subprocess
            
            minimal_path = os.path.join(self.clips_dir, f"minimal_{clip_id}.mp4")
            
            # Create minimal black video using FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=black:size=1920x1080:duration={duration}',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '30',
                minimal_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(minimal_path):
                logger.info(f"✅ Minimal fallback created: {minimal_path}")
                return minimal_path
            else:
                logger.error(f"❌ Minimal fallback failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Minimal fallback creation failed: {e}")
            return ""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(" \
               f"model={self.get_model_name()}, " \
               f"available={self.is_available})"
