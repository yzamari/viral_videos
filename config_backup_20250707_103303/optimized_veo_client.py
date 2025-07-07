"""
Optimized Veo Client with Quota Management and Veo-3 Support
Handles Google AI Studio rate limits: 2 videos/minute, 50 videos/day (Tier 1)
Now includes Gemini Image Generation fallback when VEO quota is exhausted
"""
import os
import time
import json
import uuid
import math
import subprocess
from typing import Dict, Optional, List, Tuple
from google import genai
from google.genai import types
import requests
from pathlib import Path
import random

from ..utils.logging_config import get_logger
from .gemini_image_client import GeminiImageClient
from ..utils.quota_verification import get_real_google_quota_usage

logger = get_logger(__name__)

class OptimizedVeoClient:
    """
    Quota-aware Veo client with Veo-2/3 support and 8-second optimization
    
    Features:
    - 8-second clips (maximum supported duration)
    - Veo-2 → Veo-3 → Gemini Images → Fallback chain
    - Smart quota management (2 videos/minute limit)
    - Retry mechanisms with backoff
    - Image-based video generation when VEO quota exhausted
    """
    
    def __init__(self, api_key: str, output_dir: str, disable_veo3: bool = True):
        """Initialize optimized Veo client with quota management and image fallback"""
        self.api_key = api_key
        self.output_dir = output_dir
        self.clips_dir = os.path.join(output_dir, "veo2_clips")
        os.makedirs(self.clips_dir, exist_ok=True)
        
        # Configuration flags
        self.disable_veo3 = disable_veo3  # Disable Veo-3 due to high cost
        self.veo_quota_exhausted = False  # Track if VEO quota is exhausted
        
        # Configure Google AI client
        os.environ['GOOGLE_API_KEY'] = api_key
        self.client = genai.Client()
        
        # Initialize Gemini Image Generation fallback
        try:
            self.gemini_image_client = GeminiImageClient(api_key, output_dir)
            self.gemini_images_available = self.gemini_image_client.is_available()
            logger.info(f"🎨 Gemini Image Generation: {'✅ AVAILABLE' if self.gemini_images_available else '❌ NOT AVAILABLE'}")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize Gemini Image Generation: {e}")
            self.gemini_image_client = None
            self.gemini_images_available = False
        
        # Quota management
        self.quota_tracker = QuotaTracker()
        
        # Detect available Veo models
        self.available_models = self._detect_veo_models()
        self.veo_available = len(self.available_models) > 0
        
        # Check initial quota status
        self._check_initial_quota_status()
        
        logger.info(f"🎬 Optimized Veo client initialized")
        logger.info(f"📊 Available models: {list(self.available_models.keys())}")
        if self.disable_veo3:
            logger.info("💰 Veo-3 DISABLED (cost optimization)")
        logger.info(f"⏰ Quota tracking: {self.quota_tracker.get_status()}")
        
        # Fallback chain summary
        fallback_chain = []
        if not self.veo_quota_exhausted:
            fallback_chain.append("VEO-2")
            if not self.disable_veo3 and 'veo3' in self.available_models:
                fallback_chain.insert(0, "VEO-3")
        if self.gemini_images_available:
            fallback_chain.append("Gemini Images")
        fallback_chain.append("Text Overlay")
        logger.info(f"🔄 Fallback chain: {' → '.join(fallback_chain)}")
        
        # Show quota exhaustion warning
        if self.veo_quota_exhausted:
            logger.warning("⚠️ VEO quota appears exhausted - will use image generation")
    
    def _check_initial_quota_status(self):
        """Check initial quota status to avoid unnecessary VEO attempts"""
        try:
            # Quick quota check using quota verification
            quota_info = get_real_google_quota_usage(self.api_key)
            
            if quota_info.get('status') == 'EXHAUSTED' or quota_info.get('quota_exhausted'):
                self.veo_quota_exhausted = True
                logger.warning("⚠️ Initial quota check: VEO quota exhausted")
            elif quota_info.get('status') == 'AVAILABLE':
                logger.info("✅ Initial quota check: VEO quota available")
            else:
                logger.info("ℹ️ Initial quota check: Status unclear, will attempt generation")
                
        except Exception as e:
            logger.info(f"ℹ️ Could not check initial quota status: {e}")
            # Don't set quota_exhausted if we can't check - let normal flow handle it
    
    def _detect_veo_models(self) -> Dict[str, str]:
        """Detect available Veo models in order of preference"""
        models = {}
        
        try:
            # Get actual list of available models from Google AI
            available_models = list(self.client.models.list())
            available_model_names = [model.name for model in available_models]
            
            logger.info(f"🔍 Detected {len(available_model_names)} total models")
            
            # Test for actual Veo models that exist
            test_models = [
                ("veo2", "veo-2.0-generate-001"),
                ("veo2_alt", "models/veo-2.0-generate-001"),
            ]
            
            # Add Veo-3 models only if not disabled
            if not self.disable_veo3:
                test_models.extend([
                    ("veo3", "veo-3.0-generate-preview"), 
                    ("veo3_alt", "models/veo-3.0-generate-preview"),
                ])
            
            for model_key, model_name in test_models:
                if model_name in available_model_names or model_name.replace("models/", "") in [m.replace("models/", "") for m in available_model_names]:
                    models[model_key] = model_name
                    logger.info(f"✅ {model_key.upper()} detected: {model_name}")
                else:
                    logger.info(f"❌ {model_key.upper()} not available: {model_name}")
                    
            # Check for any Veo models we might have missed
            for model_name in available_model_names:
                if "veo" in model_name.lower() and model_name not in models.values():
                    if "3" in model_name and not self.disable_veo3:
                        models["veo3"] = model_name
                        logger.info(f"✅ VEO3 found: {model_name}")
                    elif "2" in model_name and "veo2" not in models:
                        models["veo2"] = model_name
                        logger.info(f"✅ VEO2 found: {model_name}")
                    elif "3" in model_name and self.disable_veo3:
                        logger.info(f"💰 VEO3 skipped (disabled): {model_name}")
            
            if not models:
                logger.warning("⚠️ No Veo models detected - will use fallback generation")
                
        except Exception as e:
            logger.error(f"Error detecting Veo models: {e}")
            # Fallback to known working models
            models = {"veo2": "veo-2.0-generate-001"}
            logger.info("🔄 Using fallback model detection")
            
        return models
    
    def generate_optimized_clips(self, prompts: List[Dict], config: Dict, video_id: str) -> List[Dict]:
        """
        Generate optimized clips with quota management and optional frame continuity
        
        Key optimizations:
        - Use 8-second clips (fewer clips needed)
        - Smart quota spacing (30+ seconds between generations)
        - Veo-2 → Veo-3 → Gemini Images → Fallback chain
        - Frame continuity for seamless long videos
        """
        total_duration = config.get('duration_seconds', 30)
        frame_continuity = config.get('frame_continuity', False)
        
        # 🎯 OPTIMIZED GENERATION:
        logger.info("🎯 OPTIMIZED GENERATION:")
        logger.info(f"   Target duration: {total_duration}s")
        
        # CRITICAL: Use 8-second clips for maximum VEO-2 usage
        clip_duration = 8.0  # Fixed 8-second clips
        num_clips = max(1, int(total_duration / clip_duration))
        actual_duration = num_clips * clip_duration
        
        logger.info(f"   Clips: {num_clips} × {clip_duration}s = {actual_duration}s")
        logger.info(f"   Frame continuity: {'✅ ENABLED' if frame_continuity else '❌ DISABLED'}")
        logger.info(f"   Quota status: Daily: {self.quota_tracker.daily_count}/{self.quota_tracker.daily_limit}, Spacing: {self.quota_tracker.min_spacing}s")
        
        clips = []
        last_frame_image = None  # For frame continuity
        
        for i in range(num_clips):
            clip_id = f"{video_id}_scene_{i}"
            
            # Use prompt or create generic prompt for longer clips
            if i < len(prompts):
                prompt_data = prompts[i]
                prompt = prompt_data.get('veo2_prompt', prompt_data.get('description', 'cinematic video clip'))
            else:
                prompt = f"Cinematic video sequence part {i+1}, professional cinematography"
            
            # Retry logic for clip generation
            max_clip_retries = 3
            clip_generated = False
            
            for retry_attempt in range(max_clip_retries):
                try:
                    logger.info(f"🎬 Generating clip {i+1}/{num_clips} (attempt {retry_attempt + 1}/{max_clip_retries})")
                    
                    # Generate 8-second clip with quota management and frame continuity
                    clip_path = self._generate_quota_aware_clip(
                        prompt=prompt,
                        duration=clip_duration,
                        clip_id=clip_id,
                        frame_continuity=frame_continuity,
                        reference_image=last_frame_image
                    )
                    
                    # Verify clip was actually created
                    if not clip_path or not os.path.exists(clip_path):
                        raise Exception(f"Clip generation returned invalid path: {clip_path}")
                    
                    # Verify file size is reasonable
                    file_size = os.path.getsize(clip_path)
                    if file_size < 1024:  # Less than 1KB is probably corrupt
                        raise Exception(f"Generated clip is too small: {file_size} bytes")
                    
                    # Extract last frame for next clip if frame continuity is enabled
                    if frame_continuity:
                        try:
                            last_frame_image = self._extract_last_frame(clip_path, clip_id)
                            if last_frame_image:
                                logger.info(f"🖼️ Frame continuity: Extracted frame for next clip")
                        except Exception as frame_error:
                            logger.warning(f"Frame extraction failed (continuing without): {frame_error}")
                            last_frame_image = None
                    
                    clip_info = {
                        'clip_path': clip_path,
                        'description': f"Optimized 8s clip {i+1}/{num_clips}",
                        'veo2_prompt': prompt,
                        'duration': clip_duration,
                        'scene_index': i,
                        'generated_with': 'optimized_veo',
                        'file_size_mb': self._get_file_size_mb(clip_path),
                        'frame_continuity': frame_continuity,
                        'reference_image': last_frame_image if frame_continuity else None
                    }
                    
                    clips.append(clip_info)
                    logger.info(f"✅ Clip {i+1}/{num_clips} complete: {clip_info['file_size_mb']:.1f}MB" + 
                               (f" (with frame continuity)" if frame_continuity else ""))
                    
                    clip_generated = True
                    break  # Success - exit retry loop
                
                except Exception as e:
                    logger.error(f"❌ Clip {i+1} attempt {retry_attempt + 1} failed: {e}")
                    
                    if retry_attempt < max_clip_retries - 1:
                        wait_time = (retry_attempt + 1) * 30  # 30s, 60s, 90s waits
                        logger.info(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ All {max_clip_retries} attempts failed for clip {i+1}")
            
            if not clip_generated:
                logger.warning(f"⚠️ Skipping clip {i+1} after {max_clip_retries} failed attempts")
        
        logger.info(f"🎬 Optimized generation complete: {len(clips)}/{num_clips} clips successful")
        return clips
    
    def _generate_quota_aware_clip(self, prompt: str, duration: float, clip_id: str, 
                                  frame_continuity: bool = False, reference_image: Optional[str] = None) -> str:
        """Generate clip with 3 retry attempts, 1-minute waits, and optional frame continuity"""
        
        output_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
        
        # If VEO quota is exhausted, skip VEO attempts and go directly to image generation
        if self.veo_quota_exhausted:
            logger.info("⚠️ VEO quota exhausted - skipping VEO attempts, using image generation")
            return self._generate_image_fallback(prompt, duration, clip_id, output_path)
        
        # STEP 1: Check and wait for quota
        wait_time = self.quota_tracker.check_and_wait()
        if wait_time > 0:
            logger.info(f"⏰ Quota management: waiting {wait_time}s...")
            time.sleep(wait_time)
        
        # Enhanced retry mechanism: 3 attempts with 1-minute waits
        max_attempts = 3
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"🔄 Attempt {attempt}/{max_attempts} for video generation" + 
                       (f" (with frame continuity)" if frame_continuity else ""))
            
            # Try Veo-3 first (if available and not disabled)
            if 'veo3' in self.available_models and not self.disable_veo3:
                logger.info(f"🎬 Attempting Veo-3 generation (8s)...")
                result = self._try_veo_generation(
                    model_name=self.available_models['veo3'],
                    prompt=prompt,
                    duration=duration,
                    output_path=output_path,
                    model_type=f"Veo-3 (attempt {attempt})",
                    reference_image=reference_image if frame_continuity else None
                )
                if result:
                    self.quota_tracker.record_generation()
                    logger.info(f"✅ SUCCESS on attempt {attempt} with Veo-3!")
                    return result
            elif self.disable_veo3 and 'veo3' in self.available_models:
                logger.info("💰 Veo-3 available but disabled (cost optimization)")
            else:
                logger.info("ℹ️ Veo-3 not detected in your account - check API access")
            
            # Try Veo-2 as fallback
            if 'veo2' in self.available_models:
                logger.info(f"🎬 Attempting Veo-2 generation (8s)...")
                result = self._try_veo_generation(
                    model_name=self.available_models['veo2'],
                    prompt=prompt,
                    duration=duration,
                    output_path=output_path,
                    model_type=f"Veo-2 (attempt {attempt})",
                    reference_image=reference_image if frame_continuity else None
                )
                if result:
                    self.quota_tracker.record_generation()
                    logger.info(f"✅ SUCCESS on attempt {attempt} with Veo-2!")
                    return result
            
            # If this wasn't the last attempt, wait 1 minute before retrying
            if attempt < max_attempts:
                logger.info(f"⏳ Attempt {attempt} failed. Waiting 1 minute before attempt {attempt + 1}...")
                time.sleep(60)  # Wait 1 minute
            else:
                logger.warning(f"❌ All {max_attempts} attempts failed")
        
        # All VEO attempts failed - mark quota as exhausted for future attempts
        self.veo_quota_exhausted = True
        logger.warning("⚠️ All VEO attempts failed - marking quota as exhausted")
        
        # Try image generation fallback
        return self._generate_image_fallback(prompt, duration, clip_id, output_path)
    
    def _generate_image_fallback(self, prompt: str, duration: float, clip_id: str, output_path: str) -> str:
        """Generate video using image generation fallback"""
        # Try Gemini Image Generation fallback
        if self.gemini_images_available and self.gemini_image_client:
            logger.info("🎨 Using Gemini Image Generation fallback...")
            try:
                # Create a single prompt for image generation
                prompt_data = {
                    'veo2_prompt': prompt,
                    'description': prompt
                }
                
                # Generate image-based clip with 4-5 images per second
                image_config = {
                    'duration_seconds': duration,
                    'images_per_second': 4
                }
                
                image_clips = self.gemini_image_client.generate_image_based_clips(
                    prompts=[prompt_data],
                    config=image_config,
                    video_id=clip_id
                )
                
                if image_clips and len(image_clips) > 0:
                    # Move the generated clip to the expected location
                    source_path = image_clips[0]['clip_path']
                    if os.path.exists(source_path):
                        # Copy to expected output path
                        import shutil
                        shutil.copy2(source_path, output_path)
                        logger.info(f"✅ SUCCESS with Gemini Image Generation!")
                        return output_path
                        
            except Exception as e:
                logger.warning(f"⚠️ Gemini Image Generation fallback failed: {e}")
        
        # Final fallback - Create colorful engaging screen
        logger.warning("⚠️ All AI generation attempts failed - creating colorful fallback video...")
        return self._create_colorful_fallback(prompt, duration, clip_id)
    
    def _try_veo_generation(self, model_name: str, prompt: str, duration: float, 
                           output_path: str, model_type: str, reference_image: Optional[str] = None) -> Optional[str]:
        """Try generating with specific Veo model with optional frame continuity"""
        try:
            logger.info(f"📡 Calling {model_type} API..." + 
                       (f" (with reference image)" if reference_image else ""))
            
            # Enhanced prompt for 8-second clips
            enhanced_prompt = self._create_8s_optimized_prompt(prompt)
            
            # Prepare generation config
            generation_config = types.GenerateVideosConfig(
                    person_generation="allow_adult",
                    aspect_ratio="16:9",
                    duration_seconds=int(duration)  # Explicitly set 8 seconds
            )
            
            # Prepare generation parameters
            generation_params = {
                'model': model_name,
                'prompt': enhanced_prompt,
                'config': generation_config
            }
            
            # For frame continuity, use actual image-to-video generation
            # VEO-2 API supports image parameter for image-to-video generation
            if reference_image and os.path.exists(reference_image):
                logger.info(f"🖼️ Using frame continuity with image-to-video: {reference_image}")
                
                # Create image object for Google AI SDK
                try:
                    from google.genai import types as genai_types
                    
                    # Read image data
                    with open(reference_image, 'rb') as f:
                        image_data = f.read()
                    
                    # Create image object for the API
                    image_obj = genai_types.Image(
                        image_bytes=image_data,
                        mime_type='image/jpeg'
                    )
                    
                    # Use image-to-video generation for true frame continuity
                    generation_params['image'] = image_obj
                    
                    # Enhance prompt for continuity
                    enhanced_prompt = f"Continue seamlessly from this frame: {enhanced_prompt}"
                    generation_params['prompt'] = enhanced_prompt
                    
                except ImportError:
                    logger.warning("Google AI SDK types not available, using enhanced prompt only")
                    enhanced_prompt = f"Seamlessly continue the scene, maintaining visual consistency: {enhanced_prompt}"
                    generation_params['prompt'] = enhanced_prompt
            
            # Create generation operation
            operation = self.client.models.generate_videos(**generation_params)
            
            logger.info(f"⏳ Waiting for {model_type} generation (8s clip)...")
            
            # Poll for completion with timeout
            check_count = 0
            max_checks = 15  # ~5 minutes max wait
            
            while not operation.done and check_count < max_checks:
                check_count += 1
                logger.info(f"   Check {check_count}/{max_checks}: {model_type} in progress...")
                time.sleep(20)
                
                try:
                    operation = self.client.operations.get(operation)
                except Exception as e:
                    logger.warning(f"Error checking operation status: {e}")
                    break
            
            # Process results
            if operation.done and hasattr(operation, 'response'):
                if hasattr(operation.response, 'generated_videos'):
                    for generated_video in operation.response.generated_videos:
                        try:
                            self.client.files.download(file=generated_video.video)
                            generated_video.video.save(output_path)
                            
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                                file_size = os.path.getsize(output_path) / (1024 * 1024)
                                logger.info(f"🎉 {model_type} SUCCESS: {output_path} ({file_size:.1f}MB)")
                                return output_path
                        except Exception as save_error:
                            logger.error(f"Failed to save {model_type} video: {save_error}")
                            continue
            
            logger.warning(f"⚠️ {model_type} generation completed but no valid video found")
            return None
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                logger.warning(f"⏰ {model_type} quota exceeded: {e}")
                self.quota_tracker.record_quota_hit()
                # Return None to trigger fallback immediately
                return None
            elif "PERMISSION_DENIED" in error_msg:
                logger.error(f"🔒 {model_type} access denied - check API permissions: {e}")
                return None
            elif "INVALID_ARGUMENT" in error_msg:
                logger.error(f"❌ {model_type} invalid prompt or parameters: {e}")
                return None
            else:
                logger.error(f"❌ {model_type} generation failed: {e}")
            return None
    
    def _create_8s_optimized_prompt(self, prompt: str) -> str:
        """Optimize prompt for 8-second generation"""
        enhancements = [
            "8-second cinematic sequence",
            "smooth continuous motion",
            "professional cinematography",
            "seamless scene flow",
            "engaging visual storytelling"
        ]
        
        # Add 8-second specific optimization
        if "8" not in prompt and "second" not in prompt:
            prompt = f"8-second {prompt}"
        
        # Add cinematic quality
        if not any(term in prompt.lower() for term in ["cinematic", "professional", "quality"]):
            prompt += f", {enhancements[0]}"
        
        return prompt
    
    def _create_enhanced_fallback(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create high-quality 8-second fallback video that looks more realistic"""
        output_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
        
        try:
            import subprocess
            
            logger.info(f"🎨 Creating realistic 8-second fallback video...")
            
            # Create more realistic video based on content
            width, height = 1280, 720
            fps = 30
            
            # Analyze prompt to determine video style
            prompt_lower = prompt.lower()
            
            # Define realistic video patterns based on content
            if any(word in prompt_lower for word in ["baby", "child", "family"]):
                # Soft pastel animation
                filter_complex = [
                    f"color=c=0xFFE4E1:s={width}x{height}:d={duration}[bg]",
                    f"[bg]hue=s=sin(2*PI*t/{duration}):h=sin(2*PI*t/{duration})*360[hue]",
                    f"[hue]drawtext=text='Family Content':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=h-100:alpha='if(lt(t,2),t/2,if(lt(t,{duration}-2),1,(1-(t-({duration}-2))/2)))'[text]",
                    f"[text]fade=in:0:30,fade=out:{int(duration*fps-30)}:30"
                ]
            elif any(word in prompt_lower for word in ["nature", "landscape", "forest", "ocean"]):
                # Nature gradient animation
                filter_complex = [
                    f"gradients=size={width}x{height}:x0={width}/2:y0=0:x1={width}/2:y1={height}:c0=0x87CEEB:c1=0x228B22:duration={duration}[bg]",
                    f"[bg]curves=preset=increase_contrast[curves]",
                    f"[curves]vignette=PI/4[vig]",
                    f"[vig]drawtext=text='Nature Scene':fontcolor=white:fontsize=45:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.3:boxborderw=5[text]",
                    f"[text]fade=in:0:30,fade=out:{int(duration*fps-30)}:30"
                ]
            elif any(word in prompt_lower for word in ["news", "breaking", "viral", "trending"]):
                # News ticker style
                filter_complex = [
                    f"color=c=0x1E3A8A:s={width}x{height}:d={duration}[bg]",
                    f"[bg]noise=alls=20:allf=t+u[noise]",
                    f"[noise]drawbox=x=0:y={height}-120:w={width}:h=120:color=red@0.8:t=fill[box]",
                    f"[box]drawtext=text='BREAKING NEWS':fontcolor=white:fontsize=60:x=(w-text_w)/2:y={height}-90:box=1:boxcolor=red:boxborderw=0[breaking]",
                    f"[breaking]drawtext=text='AI Generated Content Preview':fontcolor=white:fontsize=30:x='if(gte(t,1),{width}-t*200,{width})':y={height}-40[ticker]",
                    f"[ticker]fade=in:0:30,fade=out:{int(duration*fps-30)}:30"
                ]
            else:
                # Dynamic modern animation (default)
                colors = ["0x2563EB", "0x7C3AED", "0xDB2777", "0xF59E0B"]
                base_color = random.choice(colors)
                filter_complex = [
                    f"color=c={base_color}:s={width}x{height}:d={duration}[bg]",
                    f"[bg]geq=r='r(X,Y)*abs(sin(2*PI*T/{duration}))':g='g(X,Y)*abs(cos(2*PI*T/{duration}))':b='b(X,Y)'[effect]",
                    f"[effect]boxblur=5:1[blur]",
                    f"[blur]drawtext=text='AI Video':fontcolor=white:fontsize=50:x='(w-text_w)/2+sin(t*2)*50':y='(h-text_h)/2':shadowx=2:shadowy=2[text]",
                    f"[text]fade=in:0:30,fade=out:{int(duration*fps-30)}:30"
                ]
            
            # Build FFmpeg command with complex filters
            filter_str = ";".join(filter_complex)
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'nullsrc=s={width}x{height}:d={duration}:r={fps}',
                '-filter_complex', filter_str,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                output_path
            ]
            
            logger.info(f"🎬 Generating realistic fallback with filters...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ Realistic fallback created: {output_path} ({file_size:.1f}MB)")
                
                # Add some motion blur for realism
                temp_output = output_path.replace('.mp4', '_temp.mp4')
                blur_cmd = [
                    'ffmpeg', '-y', '-i', output_path,
                    '-vf', 'minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    temp_output
                ]
                
                blur_result = subprocess.run(blur_cmd, capture_output=True)
                if blur_result.returncode == 0:
                    os.replace(temp_output, output_path)
                    logger.info("✨ Added motion interpolation for smoother playback")
                
                return output_path
            else:
                logger.warning(f"Realistic fallback failed: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Enhanced fallback failed: {e}")
            # Try simpler animated fallback
            return self._create_animated_fallback(prompt, duration, clip_id)
    
    def _create_animated_fallback(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create animated fallback with movement"""
        output_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
        
        try:
            import subprocess
            
            # Create video with animated patterns
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'testsrc2=size=1280x720:duration={duration}:rate=30',
                '-vf', 'format=yuv420p',
                '-c:v', 'libx264',
                '-preset', 'fast',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"✅ Animated fallback created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Animated fallback failed: {e}")
            return self._create_simple_fallback(clip_id, duration)
    
    def _create_simple_fallback(self, clip_id: str, duration: float) -> str:
        """Create simple fallback as last resort"""
        output_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
        
        try:
            import subprocess
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi', '-i', f'color=blue:size=1280x720:duration={duration}',
                '-c:v', 'libx264', '-preset', 'ultrafast',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"✅ Simple fallback created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"All fallback methods failed: {e}")
            # Create dummy file
            with open(output_path, 'w') as f:
                f.write("")
            return output_path
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except:
            return 0.0
    
    def _create_colorful_fallback(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create colorful engaging fallback when all AI generation fails"""
        output_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
        
        try:
            import subprocess
            
            logger.info("🎨 Creating colorful engaging fallback with enhanced visuals...")
            
            width, height = 1280, 720
            fps = 30
            
            # Extract key message from prompt
            text = "Viral Content Loading..."
            bg_color = "0x4A90E2"  # Nice blue default
            
            if "baby" in prompt.lower():
                text = "Baby Moments Coming Soon!"
                bg_color = "0xFFB6C1"  # Light pink
            elif "test" in prompt.lower():
                text = "Test Video Processing..."
                bg_color = "0x90EE90"  # Light green
            elif "amazing" in prompt.lower():
                text = "Amazing Content Ahead!"
                bg_color = "0xFFD700"  # Gold
            elif "iran" in prompt.lower() or "military" in prompt.lower():
                text = "Breaking News Content!"
                bg_color = "0xFF6B6B"  # Red
            elif "cat" in prompt.lower() or "animal" in prompt.lower():
                text = "Adorable Animals Loading!"
                bg_color = "0xFFA500"  # Orange
            else:
                text = "Viral Content Loading..."
                bg_color = "0x87CEEB"  # Sky blue
            
            # Create colorful animated background with text and effects
            filter_complex = [
                f"color=c={bg_color}:s={width}x{height}:d={duration}[bg]",
                f"[bg]drawtext=text='{text}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=(h-text_h)/2-50:box=1:boxcolor=black@0.7:boxborderw=8[text1]",
                f"[text1]drawtext=text='AI Generation Fallback':fontcolor=yellow:fontsize=30:x=(w-text_w)/2:y=(h-text_h)/2+50:box=1:boxcolor=black@0.5:boxborderw=5[text2]",
                f"[text2]fade=in:0:30,fade=out:{int(duration*fps-30)}:30"
            ]
            
            filter_str = ";".join(filter_complex)
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'nullsrc=s={width}x{height}:d={duration}:r={fps}',
                '-filter_complex', filter_str,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ Colorful fallback created: {output_path} ({file_size:.1f}MB)")
                return output_path
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Colorful fallback failed: {e}")
            # Ultimate fallback - create simple colored video
            return self._create_simple_colored_fallback(prompt, duration, clip_id)
    
    def _create_simple_colored_fallback(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create simple colored fallback as absolute last resort"""
        output_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
        
        try:
            import subprocess
            
            # Choose color based on prompt
            width, height = 1280, 720
            if "baby" in prompt.lower():
                color = "pink"
            elif "cat" in prompt.lower() or "animal" in prompt.lower():
                color = "orange"
            elif "news" in prompt.lower():
                color = "red"
            else:
                color = "blue"
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi', '-i', f'color={color}:size={width}x{height}:duration={duration}',
                '-c:v', 'libx264', '-preset', 'ultrafast',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"✅ Simple colored fallback created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"All fallback methods failed: {e}")
            # Create empty file as absolute last resort
            with open(output_path, 'wb') as f:
                f.write(b'')
            return output_path

    def _create_black_screen_fallback(self, prompt: str, duration: float, clip_id: str) -> str:
        """Create colorful engaging screen instead of black screen as final fallback"""
        output_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
        
        try:
            import subprocess
            
            logger.info("🎨 Creating colorful engaging screen with text overlay...")
            
            width, height = 1280, 720
            fps = 30
            
            # Extract key message from prompt
            text = "Content Loading..."
            bg_color = "0x4A90E2"  # Nice blue default
            
            if "baby" in prompt.lower():
                text = "Baby Moments Coming Soon!"
                bg_color = "0xFFB6C1"  # Light pink
            elif "test" in prompt.lower():
                text = "Test Video Processing..."
                bg_color = "0x90EE90"  # Light green
            elif "amazing" in prompt.lower():
                text = "Amazing Content Ahead!"
                bg_color = "0xFFD700"  # Gold
            elif "iran" in prompt.lower() or "military" in prompt.lower():
                text = "Breaking News Content!"
                bg_color = "0xFF6B6B"  # Red
            else:
                text = "Viral Content Loading..."
                bg_color = "0x87CEEB"  # Sky blue
            
            # Create colorful animated background with text
            filter_complex = [
                f"color=c={bg_color}:s={width}x{height}:d={duration}[bg]",
                f"[bg]drawtext=text='{text}':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.7:boxborderw=8[text]",
                f"[text]fade=in:0:30,fade=out:{int(duration*fps-30)}:30"
            ]
            
            filter_str = ";".join(filter_complex)
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'nullsrc=s={width}x{height}:d={duration}:r={fps}',
                '-filter_complex', filter_str,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ Black screen fallback created: {output_path} ({file_size:.1f}MB)")
                return output_path
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Black screen fallback failed: {e}")
            # Ultimate fallback - create empty file
            with open(output_path, 'wb') as f:
                f.write(b'')
            return output_path
    
    def _extract_last_frame(self, video_path: str, clip_id: str) -> Optional[str]:
        """Extract the last frame from a video for frame continuity"""
        try:
            frame_path = os.path.join(self.clips_dir, f"last_frame_{clip_id}.jpg")
            
            # Use ffmpeg to extract the last frame
            cmd = [
                'ffmpeg', '-y',
                '-sseof', '-1',
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '1',
                '-an',
                frame_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(frame_path):
                logger.info(f"🖼️ Extracted last frame for continuity: {frame_path}")
                return frame_path
            else:
                logger.warning(f"Failed to extract last frame: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting last frame: {e}")
            return None
    
    def _validate_content_matches_topic(self, prompt: str, topic: str) -> bool:
        """Validate that the VEO prompt actually matches the user's topic"""
        prompt_lower = prompt.lower()
        topic_keywords = topic.lower().split()
        
        # Check if prompt contains topic-related keywords
        topic_match_count = sum(1 for keyword in topic_keywords if keyword in prompt_lower)
        
        # Require at least 50% of topic keywords to be present
        required_matches = max(1, len(topic_keywords) // 2)
        
        # Also check for generic creator content that should be avoided
        generic_creator_terms = ['creator', 'influencer', 'content', 'screen', 'studio', 'computer', 'monitor', 'desk']
        generic_count = sum(1 for term in generic_creator_terms if term in prompt_lower)
        
        # If we have many generic terms and few topic matches, it's probably wrong
        if generic_count > 2 and topic_match_count < required_matches:
            logger.warning(f"⚠️ VEO prompt seems generic (creator content) rather than topic-specific")
            return False
        
        matches_topic = topic_match_count >= required_matches
        logger.info(f"🔍 Topic validation: {topic_match_count}/{len(topic_keywords)} keywords found, matches={matches_topic}")
        return matches_topic
    
    def _should_use_gemini_fallback(self, prompt: str, topic: str) -> bool:
        """Determine if we should use Gemini image generation instead of VEO"""
        # If the prompt doesn't match the topic, use Gemini images
        if not self._validate_content_matches_topic(prompt, topic):
            logger.info("🎨 Using Gemini image fallback due to topic mismatch")
            return True
        
        # If topic is specifically about visual content that VEO might not handle well
        topic_lower = topic.lower()
        visual_topics = ['cat', 'animal', 'pet', 'dog', 'bird', 'nature', 'garden', 'landscape']
        
        if any(visual_topic in topic_lower for visual_topic in visual_topics):
            # For visual topics, prefer Gemini images which can be more reliable
            logger.info("🎨 Using Gemini image fallback for visual content topic")
            return True
        
        return False


class QuotaTracker:
    """Smart quota tracking for Google AI Studio rate limits"""
    
    def __init__(self):
        self.last_generation_time = 0
        self.generation_count = 0
        self.daily_count = 0
        self.last_reset_day = time.strftime('%Y-%m-%d')
        self.consecutive_failures = 0
        self.last_quota_hit = 0
        
        # Tier 1 limits from Google AI documentation
        self.rpm_limit = 2  # 2 videos per minute
        self.daily_limit = 50  # 50 videos per day
        self.min_spacing = 30  # Minimum 30 seconds between generations
        
        # Exponential backoff parameters
        self.base_backoff = 60  # Start with 1 minute
        self.max_backoff = 300  # Maximum 5 minutes
        self.backoff_multiplier = 2
    
    def check_and_wait(self) -> int:
        """Check quota and return seconds to wait with exponential backoff"""
        current_time = time.time()
        current_day = time.strftime('%Y-%m-%d')
        
        # Reset daily counter
        if current_day != self.last_reset_day:
            self.daily_count = 0
            self.consecutive_failures = 0
            self.last_reset_day = current_day
            logger.info(f"📅 Daily quota reset: {self.daily_count}/{self.daily_limit}")
        
        # Check daily limit
        if self.daily_count >= self.daily_limit:
            logger.warning(f"🚫 Daily quota exceeded: {self.daily_count}/{self.daily_limit}")
            return 86400  # Wait 24 hours
        
        # Calculate time since last generation
        time_since_last = current_time - self.last_generation_time
        
        # If we've hit quota recently, use exponential backoff
        if self.consecutive_failures > 0:
            backoff_time = min(
                self.base_backoff * (self.backoff_multiplier ** (self.consecutive_failures - 1)),
                self.max_backoff
            )
            
            # Check if we've waited long enough since last quota hit
            time_since_quota_hit = current_time - self.last_quota_hit
            if time_since_quota_hit < backoff_time:
                wait_time = int(backoff_time - time_since_quota_hit) + 1
                logger.info(f"⏰ Exponential backoff: waiting {wait_time}s (failure #{self.consecutive_failures})")
                return wait_time
        
        # Enforce minimum spacing (quota management)
        if time_since_last < self.min_spacing:
            wait_time = int(self.min_spacing - time_since_last) + 1
            return wait_time
        
        return 0
    
    def record_generation(self):
        """Record successful generation"""
        self.last_generation_time = time.time()
        self.generation_count += 1
        self.daily_count += 1
        self.consecutive_failures = 0  # Reset failure counter on success
        logger.info(f"📊 Quota update: Daily {self.daily_count}/{self.daily_limit}")
    
    def record_quota_hit(self):
        """Record quota limit hit with exponential backoff"""
        self.consecutive_failures += 1
        self.last_quota_hit = time.time()
        
        # Increase minimum spacing more aggressively
        self.min_spacing = min(120, self.min_spacing + 30)  # Increase spacing more
        
        backoff_time = min(
            self.base_backoff * (self.backoff_multiplier ** (self.consecutive_failures - 1)),
            self.max_backoff
        )
        
        logger.warning(f"⏰ Quota limit hit #{self.consecutive_failures} - will backoff for {backoff_time}s")
        logger.warning(f"⏰ Minimum spacing increased to {self.min_spacing}s")
    
    def get_status(self) -> str:
        """Get current quota status"""
        status = f"Daily: {self.daily_count}/{self.daily_limit}, Spacing: {self.min_spacing}s"
        if self.consecutive_failures > 0:
            status += f", Failures: {self.consecutive_failures}"
        return status
    
    def is_quota_exhausted(self) -> bool:
        """Check if quota is exhausted"""
        return self.daily_count >= self.daily_limit or self.consecutive_failures >= 5
