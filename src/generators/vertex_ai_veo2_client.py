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

    def __init__(self,
            project_id: str,
            location: str,
            gcs_bucket: str,
            output_dir: str):
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
                      clip_id: str = "clip", image_path: Optional[str] = None, aspect_ratio: str = "9:16") -> str:
        """
        Generate video using Vertex AI VEO-2

        Args:
            prompt: Text prompt for video generation
            duration: Video duration in seconds
            clip_id: Unique identifier for the clip
            image_path: Optional image path for image-to-video generation
            aspect_ratio: Video aspect ratio (default: "9:16" for portrait)

        Returns:
            Path to generated video file
        """
        if not self.is_available:
            logger.warning("⚠️ FALLBACK WARNING: VEO-2 not available, using fallback video generation")
            print("⚠️ FALLBACK WARNING: VEO-2 service unavailable - generating fallback video with reduced quality")
            return self._create_fallback_clip(prompt, duration, clip_id)

        logger.info(f"🎬 Starting VEO-2 generation for clip: {clip_id}")

        try:
            # Enhance prompt with Gemini
            enhanced_prompt = self._enhance_prompt_with_gemini(prompt)

            # Submit generation request to Vertex AI VEO-2
            operation_name = self._submit_generation_request(
                enhanced_prompt,
                duration,
                clip_id,
                image_path,
                aspect_ratio)

            if operation_name:
                # Poll for completion
                operation_result = self._poll_operation(operation_name)
                if operation_result:
                    # Process the operation result to extract video path
                    video_path = self._process_operation_result(operation_result, clip_id)
                    
                    if video_path:
                        # Check if result is a local file path or GCS URI
                        if isinstance(video_path, str) and os.path.exists(video_path):
                            # Result is already a local file path (base64 video was processed)
                            logger.info(f"✅ VEO-2 generation completed: {video_path}")
                            return video_path
                        elif isinstance(video_path, str) and video_path.startswith("gs://"):
                            # Result is a GCS URI, download it
                            local_path = self._download_video_from_gcs(video_path, clip_id)
                            if local_path and os.path.exists(local_path):
                                logger.info(f"✅ VEO-2 generation completed: {local_path}")
                                return local_path
                            else:
                                logger.error("❌ Failed to download VEO-2 video from GCS")
                                return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
                        else:
                            logger.error(f"❌ Invalid result format: {video_path} (type: {type(video_path)})")
                            return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
                    else:
                        logger.error("❌ Failed to process VEO-2 operation result")
                        return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
                else:
                    logger.error("❌ Polling operation failed")
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
        enhanced_prompt += ". IMPORTANT: No text overlays, captions, subtitles, or " \
                          "written words should appear in the video. Pure visual content only"

        return enhanced_prompt

    def _submit_generation_request(
            self,
            prompt: str,
            duration: float,
            clip_id: str,
            image_path: Optional[str] = None,
            aspect_ratio: str = "9:16") -> Optional[str]:
        """Submit VEO-2 generation request to Vertex AI"""
        try:
            # CORRECT URL format for VEO-2 predictLongRunning endpoint
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.veo2_model}:predictLongRunning"
            headers = self._get_auth_headers()

            # Prepare request data with correct parameter structure
            request_data = {
                "instances": [{
                    "prompt": prompt,
                    "durationSeconds": duration
                }],
                "parameters": {
                    "outputGcsBucket": self.gcs_bucket,
                    "aspectRatio": aspect_ratio
                }
            }

            # Add image if provided
            if image_path and os.path.exists(image_path):
                try:
                    import mimetypes
                    
                    # Get mime type from file extension
                    mime_type, _ = mimetypes.guess_type(image_path)
                    if not mime_type:
                        # Default to JPEG if mime type cannot be determined
                        mime_type = "image/jpeg"
                    
                    with open(image_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                    
                    request_data["instances"][0]["image"] = {
                        "bytesBase64Encoded": image_data,
                        "mimeType": mime_type
                    }
                    
                    logger.info(f"🖼️ Added image to VEO-2 request: {os.path.basename(image_path)} ({mime_type})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process image {image_path}: {e}")
                    # Continue without image if processing fails

            response = requests.post(url, headers=headers, json=request_data, timeout=60)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ VEO-2 request successful: {result}")
                operation_name = result.get("name")
                if operation_name:
                    # Return operation name for polling
                    return operation_name
                else:
                    logger.error("❌ No operation name in response")
                    return None
            else:
                logger.error(f"❌ VEO-2 request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ VEO-2 request failed: {e}")
            return None

    def _poll_operation(self, operation_name: str, max_attempts: int = 60) -> Optional[Dict]:
        """Poll VEO-2 operation with network retry logic"""
        import time
        import requests
        from requests.exceptions import ConnectionError, Timeout
        
        operation_id = operation_name.split('/')[-1]
        logger.info(f"⏳ Polling VEO-2 operation using fetchPredictOperation: {operation_id}")
        
        for attempt in range(max_attempts):
            try:
                # Network retry logic with exponential backoff
                max_network_retries = 3
                base_delay = 2
                
                for network_retry in range(max_network_retries):
                    try:
                        # Use correct POST method and URL format for fetchPredictOperation
                        url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.veo2_model}:fetchPredictOperation"
                        
                        headers = {
                            "Authorization": f"Bearer {self.access_token}",
                            "Content-Type": "application/json"
                        }
                        
                        # Use POST method with operation name in request body
                        request_data = {
                            "operationName": operation_name
                        }
                        
                        response = requests.post(url, headers=headers, json=request_data, timeout=30)
                        break  # Success, exit retry loop
                        
                    except (ConnectionError, Timeout, requests.exceptions.RequestException) as network_error:
                        if network_retry < max_network_retries - 1:
                            retry_delay = base_delay * (2 ** network_retry)
                            logger.warning(f"🔄 Network error (attempt {network_retry + 1}/{max_network_retries}): {network_error}")
                            logger.info(f"⏳ Retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"❌ Network failure after {max_network_retries} attempts: {network_error}")
                            raise
                
                if response.status_code != 200:
                    logger.error(f"❌ Failed to poll VEO-2 operation: {response.status_code}")
                    if response.status_code == 503:
                        logger.error("Response: Service temporarily unavailable")
                    else:
                        logger.error(f"Response: {response.text}")
                    return None
                
                result = response.json()
                
                # Check if operation is complete
                if result.get('done', False):
                    logger.info("🔍 VEO-2 operation completed. Full response: ...")
                    return result
                
                # Operation still in progress
                logger.info(f"⏳ VEO-2 generation in progress... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(12)  # Wait 12 seconds between polls
                
            except Exception as e:
                logger.error(f"❌ Error polling VEO-2 operation: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(5)
                else:
                    return None
        
        logger.error(f"❌ VEO-2 operation timed out after {max_attempts} attempts")
        return None

    def _process_operation_result(self, result: Dict, clip_id: str) -> Optional[str]:
        """Process VEO-2 operation result to extract video path"""
        try:
            if not result or not isinstance(result, dict):
                logger.error("❌ Invalid operation result format")
                return None
            
            # Check if operation completed successfully
            if not result.get('done', False):
                logger.error("❌ Operation not completed")
                return None
            
            # Check for errors
            if 'error' in result:
                error_msg = result['error'].get('message', 'Unknown error')
                logger.error(f"❌ VEO-2 operation failed: {error_msg}")
                return None
            
            # Extract response from result
            response = result.get('response', {})
            if not response:
                logger.error("❌ No response in operation result")
                # Handle cases where response is directly in result
                if 'videos' in result:
                    response = result
                else:
                    return None
            
            # VEO-2 API returns a list of videos under the 'videos' key
            if 'videos' in response:
                videos = response.get('videos', [])
                if not videos:
                    logger.error("❌ No videos found in response")
                    return None
                
                # Get the first video's data
                video_info = videos[0]
                
                if 'videoBase64' in video_info:
                    video_data = video_info['videoBase64']
                    mime_type = video_info.get('mimeType', 'video/mp4')
                    return self._save_base64_video(video_data, clip_id, mime_type)
                elif 'bytesBase64Encoded' in video_info:
                    video_data = video_info['bytesBase64Encoded']
                    mime_type = video_info.get('mimeType', 'video/mp4')
                    return self._save_base64_video(video_data, clip_id, mime_type)
                elif 'gcsUri' in video_info:
                    return video_info['gcsUri']
            
            # Fallback to previous logic for other response structures
            predictions = response.get('predictions', [])
            if not predictions:
                logger.error("❌ No predictions in response")
                logger.error(f"🔍 Full response structure: {json.dumps(response, indent=2)}")
                logger.error(f"🔍 Response type: {type(response)}")
                logger.error(f"🔍 Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
                return None
            
            prediction = predictions[0]
            
            # Log prediction structure for debugging
            logger.debug(f"🔍 Prediction structure: {list(prediction.keys())}")
            
            # Check for base64 video data
            if 'videoBase64' in prediction:
                video_data = prediction['videoBase64']
                mime_type = prediction.get('mimeType', 'video/mp4')
                logger.info("✅ Found base64 video data")
                return self._save_base64_video(video_data, clip_id, mime_type)
            elif 'bytesBase64Encoded' in prediction:
                video_data = prediction['bytesBase64Encoded']
                mime_type = prediction.get('mimeType', 'video/mp4')
                logger.info("✅ Found base64 video data (bytesBase64Encoded)")
                return self._save_base64_video(video_data, clip_id, mime_type)
            
            # Check for GCS URI
            if 'gcsUri' in prediction:
                gcs_uri = prediction['gcsUri']
                logger.info(f"✅ Found GCS URI: {gcs_uri}")
                return gcs_uri
            
            # Check for direct URI
            if 'uri' in prediction:
                uri = prediction['uri']
                logger.info(f"✅ Found direct URI: {uri}")
                return uri
            
            # Check for videoUri (alternative field name)
            if 'videoUri' in prediction:
                video_uri = prediction['videoUri']
                logger.info(f"✅ Found video URI: {video_uri}")
                return video_uri
            
            logger.error(f"❌ No video data found in prediction. Available keys: {list(prediction.keys())}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to process operation result: {e}")
            return None

    def _save_base64_video(
            self,
        video_data: str,
        clip_id: str,
        mime_type: str = "video/mp4") -> Optional[str]:
        """Save base64 video data to a local file"""
        try:
            import base64

            # Determine file extension from mime type
            if "mp4" in mime_type:
                extension = "mp4"
            elif "webm" in mime_type:
                extension = "webm"
            elif "avi" in mime_type:
                extension = "avi"
            else:
                extension = "mp4"  # Default to mp4

            # Create output path
            output_path = os.path.join(
                self.output_dir,
                "veo_clips",
                f"{clip_id}.{extension}")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Decode and save base64 video data
            video_bytes = base64.b64decode(video_data)

            with open(output_path, 'wb') as f:
                f.write(video_bytes)

            logger.info(f"✅ VEO-2 video saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Failed to save base64 video: {e}")
            return None

    def _download_video_from_gcs(
            self,
            gcs_uri: str,
            clip_id: str) -> Optional[str]:
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
                "parameters": {"aspectRatio": "9:16", "durationSeconds": 5}
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
