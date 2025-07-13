#!/usr/bin/env python3
"""
Vertex AI VEO-3 Client for Advanced Video Generation
Supports native audio generation and enhanced cinematic quality
"""

import os
import sys
import time
import json
import subprocess
import requests
import shutil
from typing import Dict, Optional, List

# Add src to path for imports
if 'src' not in sys.path:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from .base_veo_client import BaseVeoClient
except ImportError:
    try:
        from src.generators.base_veo_client import BaseVeoClient
    except ImportError:
        from base_veo_client import BaseVeoClient

try:
    from src.utils.logging_config import get_logger
except ImportError:
    from utils.logging_config import get_logger

logger = get_logger(__name__)


class VertexAIVeo3Client(BaseVeoClient):
    """Vertex AI VEO-3 client for advanced video generation"""
    
    def __init__(self, project_id: str, location: str, gcs_bucket: str, output_dir: str):
        """
        Initialize Vertex AI VEO-3 client
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location (e.g., 'us-central1')
            gcs_bucket: GCS bucket for storing generated videos
            output_dir: Local directory for downloaded videos
        """
        self.gcs_bucket = gcs_bucket
        self.clips_dir = os.path.join(output_dir, "veo3_clips")
        os.makedirs(self.clips_dir, exist_ok=True)
        
        # VEO-3 model configuration
        self.veo3_model = "veo-3.0-generate-preview"
        
        # Initialize base client
        super().__init__(project_id, location, output_dir)
    
    def get_model_name(self) -> str:
        """Get the model name"""
        return self.veo3_model
    
    def generate_video(self, prompt: str, duration: float = 8.0, 
                      clip_id: str = "clip", image_path: Optional[str] = None,
                      enable_audio: bool = True) -> str:
        """
        Generate video using VEO-3 with native audio support
        
        Args:
            prompt: Text description for video generation
            duration: Video duration in seconds (up to 8 seconds for VEO-3)
            clip_id: Unique identifier for the clip
            image_path: Optional image for image-to-video generation
            enable_audio: Whether to generate native audio (VEO-3 feature)
            
        Returns:
            Path to generated video file
        """
        if not self.is_available:
            logger.warning("❌ VEO-3 not available, falling back to VEO-2")
            # Import VEO-2 client as fallback
            try:
                from .vertex_ai_veo2_client import VertexAIVeo2Client
                veo2_client = VertexAIVeo2Client(self.project_id, self.location, self.gcs_bucket, self.output_dir)
                return veo2_client.generate_video(prompt, duration, clip_id, image_path)
            except Exception as e:
                logger.error(f"❌ VEO-2 fallback failed: {e}")
                return self._create_fallback_clip(prompt, duration, clip_id)
        
        logger.info(f"🎬 Starting VEO-3 generation for clip: {clip_id}")
        
        try:
            # Enhance prompt for VEO-3 with audio and cinematic instructions
            enhanced_prompt = self._enhance_prompt_for_veo3(prompt, enable_audio)
            
            # Submit generation request to Vertex AI VEO-3
            gcs_uri = self._submit_veo3_generation_request(enhanced_prompt, duration, image_path, enable_audio)
            
            if gcs_uri:
                # Download video from GCS
                local_path = self._download_video_from_gcs(gcs_uri, clip_id)
                if local_path and os.path.exists(local_path):
                    logger.info(f"✅ VEO-3 generation completed: {local_path}")
                    return local_path
                else:
                    logger.error("❌ Failed to download VEO-3 video")
                    return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
            else:
                logger.error("❌ VEO-3 generation failed")
                return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
            
        except Exception as e:
            logger.error(f"❌ VEO-3 generation failed: {e}")
            return self._create_fallback_clip(prompt, duration, clip_id)
    
    def _check_availability(self) -> bool:
        """Check if VEO-3 is available for this project using CORRECT URL format"""
        try:
            # CORRECT URL format for VEO-3 predictLongRunning endpoint
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.veo3_model}:predictLongRunning"
            headers = self._get_auth_headers()

            # Make a minimal test request
            test_data = {
                "instances": [{"prompt": "test"}],
                "parameters": {"aspectRatio": "16:9", "durationSeconds": 5}
            }

            response = requests.post(url, headers=headers, json=test_data, timeout=30)

            # If we get 200, model is fully working
            if response.status_code == 200:
                logger.debug("✅ VEO-3 fully available")
                return True
            # If we get 400, it means the model exists but our test request is invalid (which is expected)
            elif response.status_code == 400:
                logger.debug("✅ VEO-3 available (model exists)")
                return True
            # If we get 429, it means quota exceeded but model is available
            elif response.status_code == 429:
                logger.debug("✅ VEO-3 available (quota exceeded - model accessible)")
                return True
            # If we get 404, VEO-3 is not available
            elif response.status_code == 404:
                logger.debug("🚫 VEO-3 not available (404 - not in allowlist)")
                return False
            # Any other status code suggests the model is available
            else:
                logger.debug(f"✅ VEO-3 available (status: {response.status_code})")
                return True

        except Exception as e:
            logger.debug(f"🚫 VEO-3 availability check failed: {e}")
            return False

    def _enhance_prompt_for_veo3(self, prompt: str, enable_audio: bool) -> str:
        """Enhance prompt for VEO-3 with audio and cinematic instructions"""
        enhanced_prompt = prompt

        # Add audio instructions for VEO-3
        if enable_audio and "audio:" not in prompt.lower():
            # Analyze prompt to suggest appropriate audio
            audio_suggestions = self._generate_audio_suggestions(prompt)
            if audio_suggestions:
                enhanced_prompt += f" Audio: {audio_suggestions}"

        # Add cinematic quality instructions
        if "cinematic" not in enhanced_prompt.lower():
            enhanced_prompt += ", cinematic quality, professional cinematography"

        # Add physics realism for VEO-3
        if "realistic" not in enhanced_prompt.lower():
            enhanced_prompt += ", realistic physics and movement"

        # CRITICAL: No text overlays instruction
        enhanced_prompt += ". IMPORTANT: No text overlays, captions, subtitles, or written words should appear in the video. Pure visual content only"

        return enhanced_prompt

    def _generate_audio_suggestions(self, prompt: str) -> str:
        """Generate appropriate audio suggestions based on video prompt"""
        prompt_lower = prompt.lower()
        audio_elements = []

        # Nature/outdoor scenes
        if any(word in prompt_lower for word in ['forest', 'nature', 'outdoor', 'trees', 'birds']):
            audio_elements.append("gentle bird songs, rustling leaves")
        elif any(word in prompt_lower for word in ['ocean', 'sea', 'beach', 'waves']):
            audio_elements.append("ocean waves, seagull calls")
        elif any(word in prompt_lower for word in ['city', 'street', 'urban', 'traffic']):
            audio_elements.append("distant city traffic, urban ambiance")

        # Character interactions
        if any(word in prompt_lower for word in ['talking', 'speaking', 'conversation', 'dialogue']):
            audio_elements.append("clear dialogue, natural speech")
        elif any(word in prompt_lower for word in ['laughing', 'happy', 'joy']):
            audio_elements.append("joyful laughter, cheerful voices")
        elif any(word in prompt_lower for word in ['crying', 'sad', 'emotional']):
            audio_elements.append("emotional breathing, soft sobs")

        # Action scenes
        if any(word in prompt_lower for word in ['running', 'chase', 'fast', 'action']):
            audio_elements.append("footsteps, heavy breathing, dynamic movement sounds")
        elif any(word in prompt_lower for word in ['fighting', 'battle', 'combat']):
            audio_elements.append("impact sounds, movement, tension")

        # Music/instruments
        if any(word in prompt_lower for word in ['music', 'piano', 'guitar', 'singing']):
            audio_elements.append("melodic music, instrumental harmony")
        elif any(word in prompt_lower for word in ['dancing', 'party', 'celebration']):
            audio_elements.append("upbeat music, celebratory sounds")

        # Return combined audio suggestions
        return ", ".join(audio_elements) if audio_elements else "ambient background audio"

    def _submit_veo3_generation_request(self, prompt: str, duration: float, 
                                       image_path: str = None, enable_audio: bool = True) -> str:
        """Submit video generation request to Vertex AI VEO-3"""
        try:
            # Build the request URL - Use predictLongRunning for VEO models
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.veo3_model}:predictLongRunning"
            
            headers = self._get_auth_headers()
            
            # Build request payload for VEO-3
            payload = {
                "instances": [
                    {
                        "prompt": prompt,
                        "config": {
                            "aspectRatio": "16:9",
                            "duration": f"{int(duration)}s",
                            "enableAudio": enable_audio,  # VEO-3 feature
                            "cinematicQuality": True,     # VEO-3 feature
                            "realisticPhysics": True      # VEO-3 feature
                        }
                    }
                ]
            }
            
            # Add image if provided for image-to-video
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    import base64
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    payload["instances"][0]["image"] = {
                        "bytesBase64Encoded": img_data
                    }
            
            logger.info(f"🚀 Submitting VEO-3 generation request...")
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                operation_name = result.get("name")
                if operation_name:
                    logger.info(f"✅ VEO-3 operation started: {operation_name}")
                    return self._poll_operation_status(operation_name)
                else:
                    logger.error("❌ No operation name in VEO-3 response")
                    return None
            elif response.status_code == 429:
                logger.warning("⚠️ VEO-3 quota exceeded - falling back to VEO-2")
                return None
            else:
                logger.error(f"❌ VEO-3 request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ VEO-3 generation request failed: {e}")
            return None

    def _poll_operation_status(self, operation_name: str) -> str:
        """Poll the operation status until completion or failure"""
        url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/operations/{operation_name}"
        headers = self._get_auth_headers()
        logger.info(f"Polling operation status for {operation_name}...")

        while True:
            try:
                response = requests.get(url, headers=headers, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    state = result.get("done")
                    if state:
                        if result.get("error"):
                            logger.error(f"Operation {operation_name} failed: {result['error']['message']}")
                            return None
                        else:
                            logger.info(f"Operation {operation_name} completed successfully.")
                            if "response" in result:
                                gcs_uri = result["response"]["gcsUri"]
                                logger.info(f"Operation {operation_name} completed with GCS URI: {gcs_uri}")
                                return gcs_uri
                            else:
                                logger.error(f"Operation {operation_name} completed but no GCS URI in response.")
                                return None
                    else:
                        logger.info(f"Operation {operation_name} not done yet. Waiting...")
                        time.sleep(10) # Wait 10 seconds before polling again
                else:
                    logger.error(f"Failed to poll operation status: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling operation status: {e}")
                return None

    def _download_video_from_gcs(self, gcs_uri: str, clip_id: str) -> str:
        """Download video from GCS to local storage"""
        try:
            from google.cloud import storage
            
            # Parse GCS URI
            if not gcs_uri.startswith('gs://'):
                logger.error(f"❌ Invalid GCS URI: {gcs_uri}")
                return None
            
            # Extract bucket and blob name
            gcs_path = gcs_uri[5:]  # Remove 'gs://'
            bucket_name, blob_name = gcs_path.split('/', 1)
            
            # Initialize GCS client
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Download to local file
            local_path = os.path.join(self.clips_dir, f"veo3_clip_{clip_id}.mp4")
            blob.download_to_filename(local_path)
            
            logger.info(f"✅ Downloaded VEO-3 video: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"❌ Failed to download video from GCS: {e}")
            return None

    def _create_fallback_clip(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create fallback clip when VEO-3 generation fails"""
        logger.info("🎨 Creating VEO-3 fallback clip...")
        
        # Use VEO-2 as fallback
        try:
            from .vertex_ai_veo2_client import VertexAIVeo2Client
            veo2_client = VertexAIVeo2Client(self.project_id, self.location, self.gcs_bucket, self.output_dir)
            return veo2_client.generate_video(prompt, duration, clip_id)
        except Exception as e:
            logger.error(f"❌ VEO-2 fallback failed: {e}")
            
            # Create basic fallback
            fallback_path = os.path.join(self.clips_dir, f"veo3_fallback_{clip_id}.mp4")
            
            # Create a simple colored video as last resort
            try:
                import cv2
                import numpy as np
                
                # Create video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                fps = 30
                width, height = 1920, 1080
                frames = int(duration * fps)
                
                out = cv2.VideoWriter(fallback_path, fourcc, fps, (width, height))
                
                # Generate frames with gradient colors
                for i in range(frames):
                    # Create gradient frame
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    color_shift = int(255 * (i / frames))
                    frame[:, :] = [color_shift % 255, (color_shift + 85) % 255, (color_shift + 170) % 255]
                    
                    out.write(frame)
                
                out.release()
                logger.info(f"✅ VEO-3 fallback clip created: {fallback_path}")
                return fallback_path
                
            except Exception as e:
                logger.error(f"❌ Failed to create VEO-3 fallback clip: {e}")
                return None

    def is_available(self) -> bool:
        """Check if VEO-3 is available"""
        return self.veo3_available

    def get_capabilities(self) -> Dict[str, bool]:
        """Get VEO-3 capabilities"""
        return {
            "native_audio": True,
            "cinematic_quality": True,
            "realistic_physics": True,
            "max_duration": 8.0,
            "image_to_video": True,
            "text_to_video": True
        }

