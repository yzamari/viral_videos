#!/usr/bin/env python3
"""
Base VEO Client - Abstract base class for all VEO clients
Provides clean interface and common functionality
"""

import os
import sys
import time
import subprocess
from abc import ABC, abstractmethod
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
        if not self.access_token or (self.token_expiry and time.time() >= self.token_expiry - 300):
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
            "token_valid": self.access_token is not None and time.time() < self.token_expiry
        }
    
    def _create_fallback_clip(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create fallback video when VEO is not available"""
        output_path = os.path.join(self.clips_dir, f"{clip_id}.mp4")
        
        try:
            logger.info(f"🎨 Creating fallback for: {prompt[:50]}...")
            
            # Create simple animated video with FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'testsrc=duration={duration}:size=1080x1920:rate=30',
                '-vf', f'drawtext=text=Processing...:fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-pix_fmt', 'yuv420p', '-t', str(duration),
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Fallback video created: {output_path}")
                return output_path
            else:
                logger.error(f"❌ FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Fallback creation failed: {e}")
        
        return output_path
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(model={self.get_model_name()}, available={self.is_available})" 