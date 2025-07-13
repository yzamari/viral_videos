#!/usr/bin/env python3
"""
Vertex AI VEO-2 Client for Google Cloud Tier 1 customers
Based on official Vertex AI documentation and API reference
"""
import os
import sys
import time
import json
import base64
import subprocess
import requests
from datetime import datetime
from typing import Dict, Optional, List
import shutil

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


class VertexAIVeo2Client(BaseVeoClient):
    """
    Vertex AI VEO-2 client for Google Cloud Tier 1 customers
    Uses the official Vertex AI REST API for video generation
    """

    def __init__(self, project_id: str, location: str, gcs_bucket: str, output_dir: str):
        """
        Initialize Vertex AI VEO-2 client
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location (e.g., 'us-central1')
            gcs_bucket: GCS bucket for storing generated videos
            output_dir: Local output directory
        """
        # Set up model name before parent initialization
        self.gcs_bucket = gcs_bucket
        self.veo2_model = "veo-2.0-generate-001"
        
        # Initialize parent class
        super().__init__(project_id, location, output_dir)
        
        # Verify VEO-2 availability
        if self._check_availability():
            logger.info("✅ VertexAIVeo2Client initialized successfully")
        else:
            logger.warning("⚠️ VEO-2 not available - will use fallback")

    def get_model_name(self) -> str:
        """Get the VEO-2 model name"""
        return self.veo2_model

    def generate_video(self, prompt: str, duration: float = 5.0, 
                      clip_id: str = "clip", image_path: Optional[str] = None) -> str:
        """
        Generate video using Vertex AI VEO-2
        
        Args:
            prompt: Text prompt for video generation
            duration: Video duration in seconds
            clip_id: Unique identifier for the clip
            image_path: Optional image path for image-to-video generation
            
        Returns:
            Path to generated video file
        """
        if not self.is_available:
            logger.warning("❌ VEO-2 not available, using fallback")
            return self._create_fallback_clip(prompt, duration, clip_id)
        
        logger.info(f"🎬 Starting VEO-2 generation for clip: {clip_id}")
        
        try:
            # Enhance prompt with Gemini
            enhanced_prompt = self._enhance_prompt_with_gemini(prompt)
            
            # Submit generation request to Vertex AI VEO-2
            gcs_uri = self._submit_generation_request(enhanced_prompt, duration, image_path)
            
            if gcs_uri:
                # Download video from GCS
                local_path = self._download_video_from_gcs(gcs_uri, clip_id)
                if local_path and os.path.exists(local_path):
                    logger.info(f"✅ VEO-2 generation completed: {local_path}")
                    return local_path
                else:
                    logger.error("❌ Failed to download VEO-2 video")
                    return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
            else:
                logger.error("❌ VEO-2 generation failed")
                return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
            
        except Exception as e:
            logger.error(f"❌ VEO-2 generation failed: {e}")
            return self._create_fallback_clip(prompt, duration, clip_id)

    def _enhance_prompt_with_gemini(self, prompt: str) -> str:
        """Enhance prompt for VEO-2 with cinematic instructions"""
        enhanced_prompt = prompt

        # Add cinematic quality instructions
        if "cinematic" not in enhanced_prompt.lower():
            enhanced_prompt += ", cinematic quality, professional cinematography"

        # Add visual enhancement for VEO-2
        if "realistic" not in enhanced_prompt.lower():
            enhanced_prompt += ", realistic movement and physics"

        # CRITICAL: No text overlays instruction
        enhanced_prompt += ". IMPORTANT: No text overlays, captions, subtitles, or written words should appear in the video. Pure visual content only"

        return enhanced_prompt

    def _submit_generation_request(self, prompt: str, duration: float, image_path: Optional[str] = None) -> Optional[str]:
        """Submit VEO-2 generation request to Vertex AI"""
        try:
            # CORRECT URL format for VEO-2 predictLongRunning endpoint
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.veo2_model}:predictLongRunning"
            headers = self._get_auth_headers()

            # Prepare request data
            request_data = {
                "instances": [{
                    "prompt": prompt,
                    "aspectRatio": "16:9",
                    "durationSeconds": duration
                }],
                "parameters": {
                    "outputGcsBucket": self.gcs_bucket
                }
            }

            # Add image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                request_data["instances"][0]["image"] = {
                    "bytesBase64Encoded": image_data
                }

            response = requests.post(url, headers=headers, json=request_data, timeout=60)

            if response.status_code == 200:
                result = response.json()
                operation_name = result.get("name")
                if operation_name:
                    # Poll for completion
                    return self._poll_operation_status(operation_name)
                else:
                    logger.error("❌ No operation name in response")
                    return None
            else:
                logger.error(f"❌ VEO-2 request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ VEO-2 request failed: {e}")
            return None

    def _poll_operation_status(self, operation_name: str) -> Optional[str]:
        """Poll operation status until completion"""
        try:
            # Extract operation ID from full operation name if needed
            # Format: projects/{project}/locations/{location}/operations/{operation_id}
            if "operations/" in operation_name:
                operation_id = operation_name.split("operations/")[-1]
            else:
                operation_id = operation_name
            
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/operations/{operation_id}"
            headers = self._get_auth_headers()

            max_attempts = 60  # 10 minutes max
            for attempt in range(max_attempts):
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("done"):
                        if "error" in result:
                            logger.error(f"❌ VEO-2 operation failed: {result['error']}")
                            return None
                        
                        # Extract GCS URI from response
                        response_data = result.get("response", {})
                        predictions = response_data.get("predictions", [])
                        if predictions and len(predictions) > 0:
                            gcs_uri = predictions[0].get("generatedVideo", {}).get("gcsUri")
                            if gcs_uri:
                                logger.info(f"✅ VEO-2 generation completed: {gcs_uri}")
                                return gcs_uri
                        
                        logger.error("❌ No GCS URI in response")
                        return None
                    else:
                        logger.info(f"⏳ VEO-2 generation in progress... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(10)
                else:
                    logger.error(f"❌ Failed to poll operation: {response.status_code}")
                    return None

            logger.error("❌ VEO-2 generation timed out")
            return None

        except Exception as e:
            logger.error(f"❌ Failed to poll operation: {e}")
            return None

    def _download_video_from_gcs(self, gcs_uri: str, clip_id: str) -> Optional[str]:
        """Download video from GCS to local file"""
        try:
            # Extract bucket and object path from GCS URI
            # Format: gs://bucket-name/path/to/file.mp4
            if not gcs_uri.startswith("gs://"):
                logger.error(f"❌ Invalid GCS URI format: {gcs_uri}")
                return None

            gcs_path = gcs_uri[5:]  # Remove 'gs://'
            bucket_name, object_path = gcs_path.split('/', 1)

            # Create local file path
            local_path = os.path.join(self.clips_dir, f"{clip_id}.mp4")

            # Use gsutil to download
            cmd = ["gsutil", "cp", gcs_uri, local_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                    logger.info(f"✅ Downloaded VEO-2 video: {local_path}")
                    return local_path
                else:
                    logger.error("❌ Downloaded file is empty or missing")
                    return None
            else:
                logger.error(f"❌ gsutil download failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to download from GCS: {e}")
            return None
    
    def _check_availability(self) -> bool:
        """Check if VEO-2 is available for this project using CORRECT URL format"""
        try:
            # CORRECT URL format for VEO-2 predictLongRunning endpoint
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.veo2_model}:predictLongRunning"
            headers = self._get_auth_headers()

            # Make a minimal test request
            test_data = {
                "instances": [{"prompt": "test"}],
                "parameters": {"aspectRatio": "16:9", "durationSeconds": 5}
            }

            response = requests.post(url, headers=headers, json=test_data, timeout=30)

            # If we get 200, model is fully working
            if response.status_code == 200:
                logger.debug("✅ VEO-2 fully available")
                return True
            # If we get 400, it means the model exists but our test request is invalid (which is expected)
            elif response.status_code == 400:
                logger.debug("✅ VEO-2 available (model exists)")
                return True
            # If we get 429, it means quota exceeded but model is available
            elif response.status_code == 429:
                logger.debug("✅ VEO-2 available (quota exceeded - model accessible)")
                return True
            # If we get 404, VEO-2 is not available
            elif response.status_code == 404:
                logger.debug("🚫 VEO-2 not available (404 - not in allowlist)")
                return False
            # Any other status code suggests the model is available
            else:
                logger.debug(f"✅ VEO-2 available (status: {response.status_code})")
                return True

        except Exception as e:
            logger.debug(f"🚫 VEO-2 availability check failed: {e}")
            return False
