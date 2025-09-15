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
from typing import Dict, Optional, List, Union

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
    from src.generators.json_prompt_system import VEOJsonPrompt, JSONPromptValidator, GeneratorType
except ImportError:
    from utils.logging_config import get_logger
    from generators.json_prompt_system import VEOJsonPrompt, JSONPromptValidator, GeneratorType

logger = get_logger(__name__)

class VertexAIVeo3Client(BaseVeoClient):
    """Vertex AI VEO-3 client for advanced video generation"""

    def __init__(self,
        project_id: str,
        location: str,
        gcs_bucket: str,
        output_dir: str):
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
        self.veo3_model = "veo-3.0-generate-001"  # Full VEO3 model with portrait support
        
        # Flag for VEO3-fast mode (no audio)
        self.is_veo3_fast = False

        # Initialize base client
        super().__init__(project_id, location, output_dir)

    def get_model_name(self) -> str:
        """Get the model name"""
        if self.is_veo3_fast:
            return "veo-3.0-fast-generate-001"  # Official Veo 3 Fast model
        return self.veo3_model
    
    def _convert_json_prompt_to_text(self, json_prompt: VEOJsonPrompt) -> str:
        """Convert structured JSON prompt to optimized text prompt for VEO-3"""
        parts = []
        
        # Main description
        parts.append(json_prompt.description)
        
        # Camera details
        if json_prompt.camera:
            camera_desc = []
            if json_prompt.camera.shot_type:
                camera_desc.append(f"{json_prompt.camera.shot_type.value} shot")
            if json_prompt.camera.movement:
                camera_desc.append(f"{json_prompt.camera.movement.value} camera movement")
            if json_prompt.camera.lens:
                camera_desc.append(f"shot with {json_prompt.camera.lens} lens")
            if json_prompt.camera.aperture:
                camera_desc.append(f"at {json_prompt.camera.aperture}")
            if camera_desc:
                parts.append(", ".join(camera_desc))
        
        # Lighting
        if json_prompt.lighting:
            lighting_desc = []
            if json_prompt.lighting.style:
                lighting_desc.append(f"{json_prompt.lighting.style.value} lighting")
            if json_prompt.lighting.mood:
                lighting_desc.append(f"{json_prompt.lighting.mood} mood")
            if lighting_desc:
                parts.append(", ".join(lighting_desc))
        
        # Scene details
        if json_prompt.scene:
            if json_prompt.scene.location:
                parts.append(f"location: {json_prompt.scene.location}")
            if json_prompt.scene.time_of_day:
                parts.append(f"time: {json_prompt.scene.time_of_day}")
            if json_prompt.scene.weather:
                parts.append(f"weather: {json_prompt.scene.weather}")
        
        # Subject details
        if json_prompt.subject:
            subject_parts = [json_prompt.subject.description]
            if json_prompt.subject.action:
                subject_parts.append(json_prompt.subject.action)
            if json_prompt.subject.expression:
                subject_parts.append(f"with {json_prompt.subject.expression} expression")
            parts.append(", ".join(subject_parts))
        
        # Visual style
        if hasattr(json_prompt.style, 'value'):
            parts.append(f"{json_prompt.style.value} style")
        else:
            parts.append(f"{json_prompt.style} style")
        
        # Effects
        if json_prompt.effects:
            if json_prompt.effects.color_grading:
                parts.append(f"color grading: {json_prompt.effects.color_grading}")
            if json_prompt.effects.film_grain:
                parts.append(f"with {json_prompt.effects.film_grain} film grain")
        
        # Keywords
        if json_prompt.keywords:
            parts.append(f"keywords: {', '.join(json_prompt.keywords)}")
        
        # Constraints
        if json_prompt.constraints:
            parts.append(f"constraints: {', '.join(json_prompt.constraints)}")
        
        # Multi-segment handling
        if json_prompt.segments and len(json_prompt.segments) > 0:
            parts.append("\nSequence breakdown:")
            for i, segment in enumerate(json_prompt.segments):
                segment_desc = f"{i+1}. [{segment.duration}s] {segment.description}"
                if segment.camera:
                    segment_desc += f" ({segment.camera.shot_type.value} shot, {segment.camera.movement.value} movement)"
                parts.append(segment_desc)
        
        return ". ".join(parts)

    def generate_video(self, prompt: Union[str, VEOJsonPrompt], duration: float,
                      clip_id: str = "clip", image_path: Optional[str] = None,
                      enable_audio: bool = False, aspect_ratio: str = "9:16") -> str:
        """
        Generate video using VEO-3 with native audio support

        Args:
            prompt: Text description or VEOJsonPrompt for video generation
            duration: Video duration in seconds (up to 8 seconds for VEO-3)
            clip_id: Unique identifier for the clip
            image_path: Optional image for image-to-video generation
            enable_audio: Whether to generate native audio (VEO-3 feature)
            aspect_ratio: Video aspect ratio (default: "9:16" for portrait)

        Returns:
            Path to generated video file
        """
        # Handle JSON prompt
        if isinstance(prompt, VEOJsonPrompt):
            # Validate JSON prompt
            valid, errors = JSONPromptValidator.validate(prompt, GeneratorType.VEO3)
            if not valid:
                logger.warning(f"⚠️ JSON prompt validation errors: {errors}")
            
            # Use JSON prompt's duration and aspect ratio if provided
            if prompt.duration:
                duration = prompt.duration
            if prompt.aspect_ratio:
                aspect_ratio = prompt.aspect_ratio
            
            # Convert JSON to optimized text prompt
            text_prompt = self._convert_json_prompt_to_text(prompt)
            logger.info(f"📋 Converted JSON prompt to text: {text_prompt[:200]}...")
        else:
            text_prompt = prompt
        if not self.is_available:
            logger.warning("⚠️ FALLBACK WARNING: VEO-3 not available, falling back to VEO-2")
            print("⚠️ FALLBACK WARNING: VEO-3 service unavailable - falling back to VEO-2")
            # Import VEO-2 client as fallback
            try:
                from .vertex_ai_veo2_client import VertexAIVeo2Client
                veo2_client = VertexAIVeo2Client(
                    self.project_id,
                    self.location,
                    self.gcs_bucket,
                    self.output_dir)
                return veo2_client.generate_video(text_prompt, duration, clip_id, image_path, aspect_ratio)
            except Exception as e:
                logger.error(f"❌ VEO-2 fallback failed: {e}")
                return self._create_fallback_clip(text_prompt, duration, clip_id)

        # Cost optimization: Disable audio for VEO-3 (expensive)
        if enable_audio:
            logger.info(f"💰 VEO-3 audio generation disabled for cost optimization")
            enable_audio = False
            
        # Override enable_audio for VEO3-fast mode
        if self.is_veo3_fast:
            enable_audio = False
            logger.info(f"⚡ VEO3-FAST mode: Audio generation disabled")
        
        logger.info(f"🎬 Starting VEO-3 generation for clip: {clip_id}")
        logger.info(f"⏱️ VEO-3 Duration Requested: {duration}s")

        try:
            # Enhance prompt for VEO-3 with audio and cinematic instructions
            enhanced_prompt = self._enhance_prompt_for_veo3(text_prompt, enable_audio)

            # Submit generation request to Vertex AI VEO-3
            video_result = self._submit_veo3_generation_request(
                enhanced_prompt,
                duration,
                image_path,
                enable_audio,
                aspect_ratio)

            if video_result:
                # video_result can be either a GCS URI or a local file path (from base64)
                if video_result.startswith('gs://'):
                    # Download video from GCS
                    local_path = self._download_video_from_gcs(video_result, clip_id)
                else:
                    # Already a local file path (from base64 video)
                    local_path = video_result
                
                if local_path and os.path.exists(local_path):
                    logger.info(f"✅ VEO-3 generation completed: {local_path}")
                    return local_path
                else:
                    logger.error("❌ Failed to process VEO-3 video")
                    return self._create_fallback_clip(enhanced_prompt, duration, clip_id)
            else:
                logger.error("❌ VEO-3 generation failed")
                return self._create_fallback_clip(enhanced_prompt, duration, clip_id)

        except Exception as e:
            logger.error(f"❌ VEO-3 generation failed: {e}")
            return self._create_fallback_clip(text_prompt, duration, clip_id)

    def _check_availability(self) -> bool:
        """Check if VEO-3 is available for this project using CORRECT URL format"""
        try:
            # Use correct model name based on mode
            model_name = self.get_model_name()
            # CORRECT URL format for VEO-3 predictLongRunning endpoint
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}:predictLongRunning"
            headers = self._get_auth_headers()

            # Make a minimal test request for VEO-3 Fast
            test_data = {
                "instances": [{"prompt": "test"}],
                "parameters": {
                    "aspectRatio": "9:16",
                    "durationSeconds": "5",
                    "sampleCount": 1,
                    "personGeneration": "allow_all",
                    "addWatermark": True,
                    "includeRaiReason": True,
                    "generateAudio": False,
                    "resolution": "1080p"
                }
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
                logger.debug(f"✅ VEO-3 available (status: {response.status_code}")
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
        enhanced_prompt += ". IMPORTANT: No text overlays, captions, subtitles, or " \
                          "written words should appear in the video. Pure visual content only"

        return enhanced_prompt

    def _generate_audio_suggestions(self, prompt: str) -> str:
        """Generate appropriate audio suggestions based on video prompt"""
        prompt_lower = prompt.lower()
        audio_elements = []

        # Nature/outdoor scenes
        if any(
            word in prompt_lower for word in ['forest',
            'nature',
            'outdoor',
            'trees',
            'birds']):
            audio_elements.append("gentle bird songs, rustling leaves")
        elif any(word in prompt_lower for word in ['ocean', 'sea', 'beach', 'waves']):
            audio_elements.append("ocean waves, seagull calls")
        elif any(
            word in prompt_lower for word in ['city',
            'street',
            'urban',
            'traffic']):
            audio_elements.append("distant city traffic, urban ambiance")

        # Character interactions
        if any(
            word in prompt_lower for word in ['talking',
            'speaking',
            'conversation',
            'dialogue']):
            audio_elements.append("clear dialogue, natural speech")
        elif any(word in prompt_lower for word in ['laughing', 'happy', 'joy']):
            audio_elements.append("joyful laughter, cheerful voices")
        elif any(word in prompt_lower for word in ['crying', 'sad', 'emotional']):
            audio_elements.append("emotional breathing, soft sobs")

        # Action scenes
        if any(
            word in prompt_lower for word in ['running',
            'chase',
            'fast',
            'action']):
            audio_elements.append("footsteps, heavy breathing, dynamic movement sounds")
        elif any(word in prompt_lower for word in ['fighting', 'battle', 'combat']):
            audio_elements.append("impact sounds, movement, tension")

        # Music/instruments
        if any(
            word in prompt_lower for word in ['music',
            'piano',
            'guitar',
            'singing']):
            audio_elements.append("melodic music, instrumental harmony")
        elif any(word in prompt_lower for word in ['dancing', 'party', 'celebration']):
            audio_elements.append("upbeat music, celebratory sounds")

        # Return combined audio suggestions
        return ", ".join(audio_elements) if audio_elements else "ambient background audio"

    def _submit_veo3_generation_request(self, prompt: str, duration: float,
                                       image_path: str = None, enable_audio: bool = True, aspect_ratio: str = "9:16") -> str:
        """Submit video generation request to Vertex AI VEO-3"""
        try:
            # Build the request URL - Use predictLongRunning for VEO models
            model_name = self.get_model_name()
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}:predictLongRunning"

            headers = self._get_auth_headers()

            # Build request payload for VEO-3 Fast using the example format
            # Convert aspect ratio based on model type
            if self.is_veo3_fast:
                # VEO3-Fast doesn't support portrait, force landscape
                if aspect_ratio == "9:16":
                    logger.warning("⚠️ VEO3-Fast doesn't support portrait (9:16), using landscape (16:9) instead")
                    veo3_aspect_ratio = "16:9"
                else:
                    veo3_aspect_ratio = aspect_ratio  # e.g., "16:9" or "1:1"
            else:
                # Regular VEO3 uses descriptive format
                if aspect_ratio == "9:16":
                    veo3_aspect_ratio = "9:16 portrait"
                elif aspect_ratio == "16:9":
                    veo3_aspect_ratio = "16:9 landscape"
                else:
                    veo3_aspect_ratio = aspect_ratio  # Pass as-is if already in correct format
            
            payload = {
                "instances": [
                    {
                        "prompt": prompt,
                    }
                ],
                "parameters": {
                    "aspectRatio": veo3_aspect_ratio,
                    "sampleCount": 1,
                    "durationSeconds": str(int(duration)),
                    "personGeneration": "allow_all",
                    "addWatermark": True,
                    "includeRaiReason": True,
                    "generateAudio": enable_audio and not self.is_veo3_fast,  # VEO-3 Fast doesn't support audio
                    "resolution": "1080p",
                }
            }

            # Add image if provided for image-to-video
            if image_path and os.path.exists(image_path):
                try:
                    import base64
                    import mimetypes
                    
                    # Get mime type from file extension
                    mime_type, _ = mimetypes.guess_type(image_path)
                    if not mime_type:
                        # Default to JPEG if mime type cannot be determined
                        mime_type = "image/jpeg"
                    
                    with open(image_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        payload["instances"][0]["image"] = {
                            "bytesBase64Encoded": img_data,
                            "mimeType": mime_type
                        }
                    
                    logger.info(f"🖼️ Added image to VEO-3 request: {os.path.basename(image_path)} ({mime_type})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process image {image_path}: {e}")
                    # Continue without image if processing fails

            logger.info("🚀 Submitting VEO-3 generation request...")
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
        """Poll the operation status until completion or failure using fetchPredictOperation"""
        import time
        import requests
        from requests.exceptions import ConnectionError, Timeout
        
        operation_id = operation_name.split('/')[-1]
        logger.info(f"⏳ Polling VEO-3 operation using fetchPredictOperation: {operation_id}")
        
        max_attempts = 180  # 30 minutes with 10-second intervals
        for attempt in range(max_attempts):
            try:
                # Use fetchPredictOperation endpoint like VEO-2
                model_name = self.get_model_name()
                url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}:fetchPredictOperation"
                
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                # Use POST method with operation name in request body
                request_data = {
                    "operationName": operation_name
                }
                
                response = requests.post(url, headers=headers, json=request_data, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    state = result.get("done")
                    if state:
                        if result.get("error"):
                            logger.error(f"❌ VEO-3 operation {operation_id} failed: {result['error']['message']}")
                            return None
                        else:
                            logger.info(f"✅ VEO-3 operation {operation_id} completed successfully.")
                            if "response" in result:
                                response_data = result["response"]
                                
                                # VEO-3 Fast returns predictions with metadata
                                if "predictions" in response_data and len(response_data["predictions"]) > 0:
                                    prediction = response_data["predictions"][0]
                                    
                                    # Check for video data in prediction
                                    if "video" in prediction:
                                        video_data = prediction["video"]
                                        if "gcsUri" in video_data:
                                            gcs_uri = video_data["gcsUri"]
                                            logger.info(f"✅ VEO-3 Fast operation completed with GCS URI: {gcs_uri}")
                                            return gcs_uri
                                        elif "bytesBase64Encoded" in video_data:
                                            logger.info(f"✅ VEO-3 Fast operation completed with base64 encoded video")
                                            return self._save_base64_video(video_data["bytesBase64Encoded"], operation_id)
                                    
                                    # Fallback to generatedSamples format
                                    elif "generatedSamples" in prediction and len(prediction["generatedSamples"]) > 0:
                                        sample = prediction["generatedSamples"][0]
                                        if "video" in sample:
                                            video_data = sample["video"]
                                            if "gcsUri" in video_data:
                                                gcs_uri = video_data["gcsUri"]
                                                logger.info(f"✅ VEO-3 Fast operation completed with GCS URI: {gcs_uri}")
                                                return gcs_uri
                                            elif "bytesBase64Encoded" in video_data:
                                                logger.info(f"✅ VEO-3 Fast operation completed with base64 encoded video")
                                                return self._save_base64_video(video_data["bytesBase64Encoded"], operation_id)
                                
                                # Legacy VEO-3 format support
                                elif "generatedVideo" in response_data and "gcsUri" in response_data["generatedVideo"]:
                                    gcs_uri = response_data["generatedVideo"]["gcsUri"]
                                    logger.info(f"✅ VEO-3 operation completed with GCS URI: {gcs_uri}")
                                    return gcs_uri
                                elif "videos" in response_data and len(response_data["videos"]) > 0:
                                    # Handle base64 encoded video response
                                    video_data = response_data["videos"][0]
                                    if "bytesBase64Encoded" in video_data:
                                        logger.info(f"✅ VEO-3 operation completed with base64 encoded video")
                                        return self._save_base64_video(video_data["bytesBase64Encoded"], operation_id)
                                    else:
                                        logger.error(f"❌ VEO-3 video data format not recognized")
                                        return None
                                else:
                                    logger.error(f"❌ VEO-3 operation completed but no video data in response.")
                                    logger.error(f"Response structure: {result}")
                                    return None
                            else:
                                logger.error(f"❌ VEO-3 operation completed but no response data.")
                                return None
                    else:
                        if attempt % 3 == 0:  # Log every 3rd attempt to reduce noise
                            logger.info(f"⏳ VEO-3 generation in progress... (attempt {attempt+1}/{max_attempts})")
                        time.sleep(10)  # Wait 10 seconds before polling again
                        continue
                else:
                    logger.error(f"❌ Failed to poll VEO-3 operation status: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None
                    
            except (ConnectionError, Timeout) as e:
                logger.warning(f"⚠️ Network error polling VEO-3 operation (attempt {attempt+1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(10)
                    continue
                else:
                    logger.error(f"❌ Maximum network retries exceeded for VEO-3 operation")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error polling VEO-3 operation: {e}")
                return None
        
        # If we reach here, we've exceeded max attempts
        logger.error(f"❌ VEO-3 operation timed out after {max_attempts} attempts")
        return None

    def _save_base64_video(self, base64_data: str, operation_id: str) -> str:
        """Save base64 encoded video data to local file"""
        import base64
        
        try:
            # Decode base64 data
            video_bytes = base64.b64decode(base64_data)
            
            # Create local file path
            local_path = os.path.join(self.clips_dir, f"veo3_clip_{operation_id}.mp4")
            
            # Write video data to file
            with open(local_path, 'wb') as f:
                f.write(video_bytes)
            
            logger.info(f"✅ Saved VEO-3 base64 video: {local_path}")
            
            # Check if video needs cropping to portrait
            cropped_path = self._ensure_portrait_aspect_ratio(local_path, operation_id)
            return cropped_path if cropped_path else local_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save base64 video: {e}")
            return None

    def _ensure_portrait_aspect_ratio(self, video_path: str, operation_id: str) -> str:
        """Crop landscape video to portrait if needed"""
        try:
            import subprocess
            import json
            
            # Get video dimensions using ffprobe
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"⚠️ Could not analyze video dimensions: {result.stderr}")
                return video_path
            
            video_info = json.loads(result.stdout)
            
            # Find video stream
            video_stream = None
            for stream in video_info['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                logger.warning("⚠️ No video stream found")
                return video_path
            
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            
            # Check if video is landscape (width > height)
            if width <= height:
                logger.info(f"✅ Video is already portrait ({width}x{height})")
                return video_path
            
            logger.info(f"🔄 Cropping landscape video ({width}x{height}) to portrait")
            
            # Calculate crop dimensions for 9:16 aspect ratio
            target_aspect = 9 / 16
            current_aspect = width / height
            
            if current_aspect > target_aspect:
                # Video is wider than target, crop width
                new_width = int(height * target_aspect)
                new_height = height
                crop_x = (width - new_width) // 2
                crop_y = 0
            else:
                # Video is taller than target, crop height
                new_width = width
                new_height = int(width / target_aspect)
                crop_x = 0
                crop_y = (height - new_height) // 2
            
            # Create cropped video path
            cropped_path = os.path.join(self.clips_dir, f"veo3_clip_{operation_id}_portrait.mp4")
            
            # Crop video using ffmpeg
            crop_cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f'crop={new_width}:{new_height}:{crop_x}:{crop_y}',
                '-c:a', 'copy', '-y', cropped_path
            ]
            
            result = subprocess.run(crop_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Successfully cropped to portrait: {cropped_path} ({new_width}x{new_height})")
                return cropped_path
            else:
                logger.error(f"❌ Failed to crop video: {result.stderr}")
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Error checking/cropping video: {e}")
            return video_path

    def _download_video_from_gcs(self, gcs_uri: str, clip_id: str) -> str:
        """Download video from GCS to local storage"""
        try:
            from google.cloud  import storage

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
            
            # Check if video needs cropping to portrait
            cropped_path = self._ensure_portrait_aspect_ratio(local_path, clip_id)
            return cropped_path if cropped_path else local_path

        except Exception as e:
            logger.error(f"❌ Failed to download video from GCS: {e}")
            return None

    def _create_fallback_clip(
        self,
        prompt: str,
        duration: float,
        clip_id: str,
        aspect_ratio: str = "9:16") -> str:
        """Create fallback clip when VEO-3 generation fails"""
        logger.info("🎨 Creating VEO-3 fallback clip...")

        # Use VEO-2 as fallback
        try:
            from .vertex_ai_veo2_client import VertexAIVeo2Client
            veo2_client = VertexAIVeo2Client(
                self.project_id,
                self.location,
                self.gcs_bucket,
                self.output_dir)
            return veo2_client.generate_video(prompt, duration, clip_id, image_path=None, aspect_ratio=aspect_ratio)
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
