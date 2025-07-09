"""
Video generator using AI and video editing libraries
"""
import os
import json
import subprocess
import time
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from gtts import gTTS
import tempfile
import requests
import random

# MoviePy imports
from moviepy.editor import *
try:
    from moviepy.video.fx.fadein import fadein
    from moviepy.video.fx.fadeout import fadeout
    from moviepy.audio.fx.audio_fadein import audio_fadein
    from moviepy.audio.fx.audio_fadeout import audio_fadeout
except ImportError:
    # Fallback for different moviepy versions
    fadein = None
    fadeout = None
    audio_fadein = None
    audio_fadeout = None

# Google AI imports
import google.generativeai as genai

# Add project root to path for fallback imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from veo_client import VeoApiClient

try:
    from ..models.video_models import (
        VideoAnalysis, GeneratedVideoConfig, GeneratedVideo, 
        Platform, VideoCategory, VideoOrientation, ForceGenerationMode
    )
    from ..utils.logging_config import get_logger
    from ..utils.session_manager import SessionManager
    from ..utils.exceptions import (
        GenerationFailedError, RenderingError, 
        StorageError, ContentPolicyViolation
    )
    from .director import Director
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from models.video_models import (
        VideoAnalysis, GeneratedVideoConfig, GeneratedVideo, 
        Platform, VideoCategory, VideoOrientation, ForceGenerationMode
    )
    from utils.logging_config import get_logger
    from utils.session_manager import SessionManager
    from utils.exceptions import (
        GenerationFailedError, RenderingError, 
        StorageError, ContentPolicyViolation
    )
    from generators.director import Director

logger = get_logger(__name__)

def ensure_gcloud_auth():
    """Ensure gcloud is authenticated automatically without browser interaction"""
    try:
        # Check if already authenticated
        result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            logger.info("✅ gcloud already authenticated")
            
            # Check if application default credentials are set
            try:
                result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("✅ Application default credentials available")
                    
                    # Verify ADC file exists
                    import os
                    adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
                    if os.path.exists(adc_path):
                        logger.info("✅ ADC file confirmed")
                        return True
                    else:
                        logger.warning("⚠️ ADC file missing, may need re-authentication")
            except:
                pass
        
        logger.info("🔐 Setting up gcloud authentication...")
        
        # Set up application default credentials without browser
        try:
            result = subprocess.run([
                'gcloud', 'auth', 'application-default', 'login', 
                '--no-browser', '--quiet'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ Application default credentials configured")
                return True
            else:
                logger.warning(f"⚠️ Application default login failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Application default login timed out")
        except Exception as e:
            logger.warning(f"⚠️ Application default login error: {e}")
        
        # Alternative: Try to activate service account if available
        try:
            import os
            # Check if service account key exists
            service_account_paths = [
                os.path.expanduser("~/.config/gcloud/application_default_credentials.json"),
                os.path.join(os.getcwd(), "service-account-key.json"),
                os.path.join(os.getcwd(), "credentials.json")
            ]
            
            for key_path in service_account_paths:
                if os.path.exists(key_path):
                    logger.info(f"🔑 Found service account key: {key_path}")
                    result = subprocess.run([
                        'gcloud', 'auth', 'activate-service-account', 
                        '--key-file', key_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        logger.info("✅ Service account activated")
                        return True
        except Exception as e:
            logger.warning(f"⚠️ Service account activation failed: {e}")
        
        # Final fallback: Try to use existing credentials
        try:
            result = subprocess.run(['gcloud', 'config', 'set', 'auth/disable_credentials', 'false'], 
                                  capture_output=True, text=True)
            result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Using existing gcloud credentials")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Existing credentials check failed: {e}")
        
        logger.warning("⚠️ Could not set up automatic authentication, will use fallback methods")
        return False
        
    except Exception as e:
        logger.error(f"❌ Authentication setup failed: {e}")
        return False

class VideoGenerator:
    """
    Main video generator class with REAL VEO-2 video generation
    """
    
    def __init__(self, api_key: str, use_vertex_ai: bool = True, project_id: Optional[str] = None, 
                 location: Optional[str] = None, gcs_bucket: Optional[str] = None, 
                 use_real_veo2: bool = True, session_id: Optional[str] = None):
        self.api_key = api_key
        self.use_vertex_ai = use_vertex_ai
        self.project_id = project_id or "viralgen-464411"
        self.location = location or "us-central1"
        self.gcs_bucket = gcs_bucket or "viral-veo2-results"
        self.use_real_veo2 = use_real_veo2
        
        # Initialize session using centralized SessionManager
        if session_id:
            self.session_id = session_id
            self.session_dir = SessionManager.get_session_path(session_id)
            os.makedirs(self.session_dir, exist_ok=True)
        else:
            self.session_id = SessionManager.create_session_id()
            self.session_dir = SessionManager.create_session_folder(self.session_id)
        
        # UNIFIED OUTPUT STRUCTURE - All files go in session directory
        self.base_output_dir = "outputs"
        self.output_dir = self.session_dir  # Main output directory for this session
        
        # Subdirectories within session
        self.clips_dir = os.path.join(self.session_dir, "clips")
        self.images_dir = os.path.join(self.session_dir, "images")
        self.audio_dir = os.path.join(self.session_dir, "audio")
        self.logs_dir = os.path.join(self.session_dir, "logs")
        self.analysis_dir = os.path.join(self.session_dir, "analysis")
        
        # Create all subdirectories
        for directory in [self.clips_dir, self.images_dir, self.audio_dir, self.logs_dir, self.analysis_dir]:
            os.makedirs(directory, exist_ok=True)
        
        logger.info(f"📁 Unified session directory created: {self.session_dir}")
        logger.info(f"📁 Subdirectories: clips, images, audio, logs, analysis")
        
        # Ensure gcloud authentication before any GCP operations
        ensure_gcloud_auth()
        
        # Initialize comprehensive logger with session directory
        from ..utils.comprehensive_logger import ComprehensiveLogger
        self.comprehensive_logger = ComprehensiveLogger(self.session_id, self.session_dir)
        
        # Initialize models
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.script_model = genai.GenerativeModel("gemini-2.5-flash")
        self.refinement_model = genai.GenerativeModel("gemini-2.5-pro")
        
        # Initialize VEO-2 client if enabled
        if use_real_veo2:
            # Try to initialize VEO clients in fallback order
            self.veo_client = None
            
            if use_vertex_ai:
                try:
                    from .vertex_ai_veo2_client import VertexAIVeo2Client
                    self.veo_client = VertexAIVeo2Client(
                        project_id=self.project_id,
                        location=self.location,
                        gcs_bucket=self.gcs_bucket,
                        output_dir=self.session_dir  # Use session directory
                    )
                    logger.info("🎬 Vertex AI VEO-2 client initialized")
                except ImportError as e:
                    logger.warning(f"⚠️ Vertex AI VEO-2 not available: {e}")
            
            # Fallback to Google AI Studio VEO-2
            if not self.veo_client:
                try:
                    from .optimized_veo_client import OptimizedVeoClient
                    self.veo_client = OptimizedVeoClient(
                        api_key=api_key,
                        output_dir=self.session_dir  # Use session directory
                    )
                    logger.info("🎬 Google AI Studio VEO-2 client initialized")
                except ImportError as e:
                    logger.warning(f"⚠️ Google AI Studio VEO-2 not available: {e}")
            
            # Initialize Gemini Image fallback
            try:
                from .gemini_image_client import GeminiImageClient
                self.image_client = GeminiImageClient(api_key, self.session_dir)  # Use session directory
                logger.info("🎨 Gemini Image fallback client initialized")
            except ImportError as e:
                logger.warning(f"⚠️ Gemini Image fallback not available: {e}")
                self.image_client = None
        else:
            self.veo_client = None
            self.image_client = None
        
        logger.info(f"🎬 VideoGenerator initialized with session {self.session_id}, use_real_veo2={use_real_veo2}, use_vertex_ai={use_vertex_ai}")
        
        # Log initialization
        self.comprehensive_logger.log_debug_info(
            component="VideoGenerator",
            level="INFO",
            message="Video generator initialized with unified output structure",
            data={
                "session_id": self.session_id,
                "session_dir": self.session_dir,
                "use_real_veo2": use_real_veo2,
                "use_vertex_ai": use_vertex_ai,
                "project_id": self.project_id,
                "location": self.location
            }
        )
    
    def generate_video(self, config: GeneratedVideoConfig) -> str:
        """Generate a complete video with comprehensive logging"""
        start_time = time.time()
        
        # Initialize metrics
        self.comprehensive_logger.update_metrics(
            topic=config.topic,
            platform=config.target_platform.value,
            category=config.category.value,
            target_duration=config.duration_seconds
        )
        
        try:
            logger.info(f"🎬 Starting video generation for topic: {config.topic}")
            
            # Step 1: Generate Script
            script_start = time.time()
            script = self._generate_script(config)
            script_time = time.time() - script_start
            
            # Log script generation
            self.comprehensive_logger.log_script_generation(
                script_type="original",
                content=script,
                model_used="gemini-2.5-flash",
                generation_time=script_time,
                topic=config.topic,
                platform=config.target_platform.value,
                category=config.category.value
            )
            
            logger.info(f"📝 Script generated: {len(script)} characters")
            
            # Step 2: Clean script for TTS
            clean_script = self._clean_script_for_tts(script, config.duration_seconds)
            
            # Log cleaned script
            self.comprehensive_logger.log_script_generation(
                script_type="cleaned",
                content=clean_script,
                model_used="text_processing",
                generation_time=0.1,
                topic=config.topic,
                platform=config.target_platform.value,
                category=config.category.value
            )
            
            # Step 3: Generate Video Clips
            video_start = time.time()
            video_clips = self._generate_video_clips(config, script)
            video_time = time.time() - video_start
            
            logger.info(f"🎥 Generated {len(video_clips)} video clips")
            
            # Step 4: Generate Audio
            audio_start = time.time()
            audio_path = self._generate_audio(clean_script, config.duration_seconds)
            audio_time = time.time() - audio_start
            
            # Log audio generation
            if audio_path and os.path.exists(audio_path):
                file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                self.comprehensive_logger.log_audio_generation(
                    audio_type="enhanced_gtts",
                    file_path=audio_path,
                    file_size_mb=file_size_mb,
                    duration=config.duration_seconds,
                    voice_settings={"lang": "en", "slow": False},
                    script_used=clean_script,
                    generation_time=audio_time,
                    success=True
                )
            else:
                self.comprehensive_logger.log_audio_generation(
                    audio_type="enhanced_gtts",
                    file_path=audio_path or "failed",
                    file_size_mb=0.0,
                    duration=0.0,
                    voice_settings={},
                    script_used=clean_script,
                    generation_time=audio_time,
                    success=False,
                    error_message="Audio generation failed"
                )
            
            # Step 5: Compose Final Video
            final_video_path = self._compose_final_video(video_clips, audio_path, config)
            
            # Calculate final metrics
            total_time = time.time() - start_time
            final_video_size = 0.0
            if os.path.exists(final_video_path):
                final_video_size = os.path.getsize(final_video_path) / (1024 * 1024)
            
            # Update comprehensive metrics
            self.comprehensive_logger.update_metrics(
                script_generation_time=script_time,
                audio_generation_time=audio_time,
                video_generation_time=video_time,
                total_clips_generated=len(video_clips),
                successful_veo_clips=len([c for c in video_clips if not c.endswith('placeholder')]),
                fallback_clips=len([c for c in video_clips if c.endswith('placeholder')]),
                final_video_size_mb=final_video_size,
                actual_duration=config.duration_seconds
            )
            
            # Finalize session
            self.comprehensive_logger.finalize_session(success=True)
            
            logger.info(f"✅ Video generation complete: {final_video_path}")
            logger.info(f"⏱️ Total time: {total_time:.2f}s")
            logger.info(f"📊 Final video size: {final_video_size:.1f}MB")
            
            return final_video_path
            
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            
            # Log failure
            self.comprehensive_logger.finalize_session(success=False, error_message=str(e))
            
            raise
    
    def _generate_script(self, config: GeneratedVideoConfig) -> str:
        """Generate script for the video"""
        try:
            director = Director(self.api_key)
            
            # Use the correct method from Director class
            script_data = director.write_script(
                topic=config.topic,
                style=config.style,
                duration=config.duration_seconds,
                platform=config.target_platform,
                category=config.category,
                patterns={
                    'hooks': [],
                    'themes': [config.tone],
                    'success_factors': ['engaging', 'viral']
                },
                incorporate_news=False  # Simplify for now
            )
            
            # Always return string for TTS processing
            if isinstance(script_data, dict):
                # Extract text from dict structure
                script_text = ""
                if 'hook' in script_data:
                    script_text += str(script_data['hook']) + " "
                if 'segments' in script_data:
                    for segment in script_data['segments']:
                        script_text += str(segment) + " "
                if 'call_to_action' in script_data:
                    script_text += str(script_data['call_to_action'])
                script = script_text.strip() or str(script_data)
            else:
                script = str(script_data)
            
            logger.info(f"📝 Script generated: {len(script)} characters")
            return script
            
        except Exception as e:
            logger.error(f"❌ Script generation failed: {e}")
            # Create a simple fallback script
            fallback_script = f"""
            Welcome to an amazing {config.duration_seconds}-second video about {config.topic}!
            
            {config.hook}
            
            {' '.join(config.main_content or [])}
            
            {config.call_to_action}
            
            Thanks for watching!
            """
            logger.info("📝 Using fallback script")
            return fallback_script.strip()
    
    def _generate_video_clips(self, config: GeneratedVideoConfig, script: str) -> List[str]:
        """Generate video clips with force generation modes and proper orientation"""
        try:
            clips = []
            
            # Apply AI agents orientation decision if enabled
            if config.ai_decide_orientation and config.video_orientation == VideoOrientation.AUTO:
                from ..agents.enhanced_orchestrator_with_19_agents import EnhancedOrchestratorWith19Agents
                orchestrator = EnhancedOrchestratorWith19Agents(
                    api_key=self.api_key,
                    session_id=getattr(self, 'session_id', 'temp_session'),
                    use_vertex_ai=getattr(self, 'use_vertex_ai', True),
                    vertex_project_id=getattr(self, 'project_id', 'viralgen-464411'),
                    vertex_location=getattr(self, 'location', 'us-central1'),
                    vertex_gcs_bucket=getattr(self, 'gcs_bucket', 'viral-veo2-results')
                )
                optimal_orientation = orchestrator._ai_agents_decide_video_orientation(config)
                config = orchestrator._apply_orientation_to_config(config, optimal_orientation)
            
            # Get proper resolution based on orientation
            width, height = config.get_resolution()
            aspect_ratio = config.get_aspect_ratio()
            
            logger.info(f"🎬 Video generation with orientation: {config.video_orientation.value}")
            logger.info(f"📏 Resolution: {width}x{height} ({aspect_ratio})")
            logger.info(f"🎛️ Force generation mode: {config.force_generation_mode.value}")
            
            # Calculate proper clip timing
            num_clips = max(1, config.duration_seconds // 8)
            clip_duration = config.duration_seconds / num_clips
            
            # Create VEO-2 prompts based on the topic and script
            veo_prompts = self._create_veo2_prompts(config, script)
            
            logger.info(f"🎬 Starting video generation with {len(veo_prompts)} clips (duration: {clip_duration:.1f}s each)")
            
            # Handle different force generation modes
            if config.force_generation_mode == ForceGenerationMode.FORCE_VEO3:
                clips = self._force_veo3_generation(veo_prompts, config, clip_duration, aspect_ratio)
            elif config.force_generation_mode == ForceGenerationMode.FORCE_VEO2:
                clips = self._force_veo2_generation(veo_prompts, config, clip_duration, aspect_ratio)
            elif config.force_generation_mode == ForceGenerationMode.FORCE_IMAGE_GEN:
                clips = self._force_image_generation(veo_prompts, config, clip_duration, aspect_ratio)
            elif config.force_generation_mode == ForceGenerationMode.FORCE_CONTINUOUS:
                clips = self._force_continuous_generation(veo_prompts, config, clip_duration, aspect_ratio)
            else:
                # Normal fallback chain
                clips = self._generate_with_fallback_chain(veo_prompts, config, clip_duration, aspect_ratio)
            
            logger.info(f"🎥 Generated {len(clips)} video clips with force mode: {config.force_generation_mode.value}")
            return clips
            
        except Exception as e:
            logger.error(f"❌ Video clip generation failed: {e}")
            raise
    
    def _force_veo3_generation(self, veo_prompts: List[str], config: GeneratedVideoConfig, 
                              clip_duration: float, aspect_ratio: str) -> List[str]:
        """Force VEO-3 generation only"""
        logger.info("🎬 FORCE VEO-3 MODE: Using VEO-3 exclusively")
        
        clips = []
        for i, prompt in enumerate(veo_prompts):
            clip_id = f"{self.session_id}_veo3_clip_{i}"
            
            try:
                if self.use_real_veo2 and self.veo_client:
                    # Force VEO-3 with prefer_veo3=True and no fallback
                    if hasattr(self.veo_client, 'generate_video_clip'):
                        clip_path = self.veo_client.generate_video_clip(
                            prompt=prompt,
                            duration=clip_duration,
                            clip_id=clip_id,
                            aspect_ratio=aspect_ratio,
                            prefer_veo3=True,
                            enable_audio=True
                        )
                        
                        if clip_path and os.path.exists(clip_path):
                            logger.info(f"✅ VEO-3 clip {i+1} generated: {clip_path}")
                            clips.append(clip_path)
                            continue
                
                # If VEO-3 fails, create error clip
                logger.error(f"❌ VEO-3 generation failed for clip {i+1}")
                error_clip_path = os.path.join(self.session_dir, f"veo3_error_{i}_{self.session_id}.mp4")
                self._create_error_clip(error_clip_path, "VEO-3 Generation Failed", clip_duration, aspect_ratio)
                clips.append(error_clip_path)
                
            except Exception as e:
                logger.error(f"❌ VEO-3 clip {i+1} failed: {e}")
                error_clip_path = os.path.join(self.session_dir, f"veo3_error_{i}_{self.session_id}.mp4")
                self._create_error_clip(error_clip_path, f"VEO-3 Error: {str(e)}", clip_duration, aspect_ratio)
                clips.append(error_clip_path)
        
        return clips
    
    def _force_veo2_generation(self, veo_prompts: List[str], config: GeneratedVideoConfig, 
                              clip_duration: float, aspect_ratio: str) -> List[str]:
        """Force VEO-2 generation only"""
        logger.info("🎥 FORCE VEO-2 MODE: Using VEO-2 exclusively")
        
        clips = []
        for i, prompt in enumerate(veo_prompts):
            clip_id = f"{self.session_id}_veo2_clip_{i}"
            
            try:
                if self.use_real_veo2 and self.veo_client:
                    # Force VEO-2 with prefer_veo3=False
                    if hasattr(self.veo_client, 'generate_video_clip'):
                        clip_path = self.veo_client.generate_video_clip(
                            prompt=prompt,
                            duration=clip_duration,
                            clip_id=clip_id,
                            aspect_ratio=aspect_ratio,
                            prefer_veo3=False,
                            enable_audio=False
                        )
                        
                        if clip_path and os.path.exists(clip_path):
                            logger.info(f"✅ VEO-2 clip {i+1} generated: {clip_path}")
                            clips.append(clip_path)
                            continue
                
                # If VEO-2 fails, create error clip
                logger.error(f"❌ VEO-2 generation failed for clip {i+1}")
                error_clip_path = os.path.join(self.session_dir, f"veo2_error_{i}_{self.session_id}.mp4")
                self._create_error_clip(error_clip_path, "VEO-2 Generation Failed", clip_duration, aspect_ratio)
                clips.append(error_clip_path)
                
            except Exception as e:
                logger.error(f"❌ VEO-2 clip {i+1} failed: {e}")
                error_clip_path = os.path.join(self.session_dir, f"veo2_error_{i}_{self.session_id}.mp4")
                self._create_error_clip(error_clip_path, f"VEO-2 Error: {str(e)}", clip_duration, aspect_ratio)
                clips.append(error_clip_path)
        
        return clips
    
    def _force_image_generation(self, veo_prompts: List[str], config: GeneratedVideoConfig, 
                               clip_duration: float, aspect_ratio: str) -> List[str]:
        """Force image generation only"""
        logger.info("🎨 FORCE IMAGE GENERATION MODE: Using AI image generation exclusively")
        
        clips = []
        for i, prompt in enumerate(veo_prompts):
            clip_id = f"{self.session_id}_image_clip_{i}"
            
            try:
                if self.image_client:
                    image_clips = self.image_client.generate_image_based_clips(
                        prompts=[{
                            'veo2_prompt': prompt,
                            'description': f"Scene {i+1}: {prompt[:100]}"
                        }],
                        config={
                            'duration_seconds': clip_duration,
                            'images_per_second': 4,
                            'aspect_ratio': aspect_ratio
                        },
                        video_id=clip_id
                    )
                    
                    if image_clips and len(image_clips) > 0:
                        clip_path = image_clips[0]['clip_path']
                        if os.path.exists(clip_path):
                            logger.info(f"✅ Image generation clip {i+1} generated: {clip_path}")
                            clips.append(clip_path)
                            continue
                
                # If image generation fails, create error clip
                logger.error(f"❌ Image generation failed for clip {i+1}")
                error_clip_path = os.path.join(self.session_dir, f"image_error_{i}_{self.session_id}.mp4")
                self._create_error_clip(error_clip_path, "Image Generation Failed", clip_duration, aspect_ratio)
                clips.append(error_clip_path)
                
            except Exception as e:
                logger.error(f"❌ Image generation clip {i+1} failed: {e}")
                error_clip_path = os.path.join(self.session_dir, f"image_error_{i}_{self.session_id}.mp4")
                self._create_error_clip(error_clip_path, f"Image Error: {str(e)}", clip_duration, aspect_ratio)
                clips.append(error_clip_path)
        
        return clips
    
    def _force_continuous_generation(self, veo_prompts: List[str], config: GeneratedVideoConfig, 
                                    clip_duration: float, aspect_ratio: str) -> List[str]:
        """Force continuous generation - keep trying until success"""
        logger.info("🔄 FORCE CONTINUOUS MODE: Will keep trying until successful generation")
        
        clips = []
        max_attempts_per_clip = 10  # Maximum attempts per clip
        
        for i, prompt in enumerate(veo_prompts):
            clip_id = f"{self.session_id}_continuous_clip_{i}"
            clip_generated = False
            
            for attempt in range(max_attempts_per_clip):
                logger.info(f"🔄 Continuous generation attempt {attempt + 1}/{max_attempts_per_clip} for clip {i+1}")
                
                try:
                    # Try VEO-3 first
                    if self.use_real_veo2 and self.veo_client and hasattr(self.veo_client, 'generate_video_clip'):
                        clip_path = self.veo_client.generate_video_clip(
                            prompt=prompt,
                            duration=clip_duration,
                            clip_id=f"{clip_id}_attempt_{attempt}",
                            aspect_ratio=aspect_ratio,
                            prefer_veo3=True,
                            enable_audio=True
                        )
                        
                        if clip_path and os.path.exists(clip_path):
                            logger.info(f"✅ Continuous VEO-3 clip {i+1} generated on attempt {attempt + 1}")
                            clips.append(clip_path)
                            clip_generated = True
                            break
                    
                    # Try VEO-2 if VEO-3 fails
                    if self.use_real_veo2 and self.veo_client and hasattr(self.veo_client, 'generate_video_clip'):
                        clip_path = self.veo_client.generate_video_clip(
                            prompt=prompt,
                            duration=clip_duration,
                            clip_id=f"{clip_id}_veo2_attempt_{attempt}",
                            aspect_ratio=aspect_ratio,
                            prefer_veo3=False,
                            enable_audio=False
                        )
                        
                        if clip_path and os.path.exists(clip_path):
                            logger.info(f"✅ Continuous VEO-2 clip {i+1} generated on attempt {attempt + 1}")
                            clips.append(clip_path)
                            clip_generated = True
                            break
                    
                    # Try image generation
                    if self.image_client:
                        image_clips = self.image_client.generate_image_based_clips(
                            prompts=[{
                                'veo2_prompt': prompt,
                                'description': f"Scene {i+1}: {prompt[:100]}"
                            }],
                            config={
                                'duration_seconds': clip_duration,
                                'images_per_second': 4,
                                'aspect_ratio': aspect_ratio
                            },
                            video_id=f"{clip_id}_image_attempt_{attempt}"
                        )
                        
                        if image_clips and len(image_clips) > 0:
                            clip_path = image_clips[0]['clip_path']
                            if os.path.exists(clip_path):
                                logger.info(f"✅ Continuous image clip {i+1} generated on attempt {attempt + 1}")
                                clips.append(clip_path)
                                clip_generated = True
                                break
                    
                    # Wait before next attempt
                    if attempt < max_attempts_per_clip - 1:
                        wait_time = min(30, (attempt + 1) * 5)  # Progressive wait: 5s, 10s, 15s, etc.
                        logger.info(f"⏳ Waiting {wait_time}s before next attempt...")
                        time.sleep(wait_time)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Continuous generation attempt {attempt + 1} failed: {e}")
                    continue
            
            # If all attempts failed, create error clip
            if not clip_generated:
                logger.error(f"❌ All {max_attempts_per_clip} continuous attempts failed for clip {i+1}")
                error_clip_path = os.path.join(self.session_dir, f"continuous_error_{i}_{self.session_id}.mp4")
                self._create_error_clip(error_clip_path, f"Continuous Generation Failed ({max_attempts_per_clip} attempts)", clip_duration, aspect_ratio)
                clips.append(error_clip_path)
        
        return clips
    
    def _generate_with_fallback_chain(self, veo_prompts: List[str], config: GeneratedVideoConfig, 
                                     clip_duration: float, aspect_ratio: str) -> List[str]:
        """Generate with normal fallback chain: VEO-3 → VEO-2 → Image → Local → Text"""
        logger.info("🔄 NORMAL FALLBACK CHAIN: VEO-3 → VEO-2 → Image → Local → Text")
        
        clips = []
        for i, prompt in enumerate(veo_prompts):
            clip_id = f"{self.session_id}_clip_{i}"
            clip_path = None
            
            # STEP 1: Try VEO-3 generation
            if self.use_real_veo2 and self.veo_client and hasattr(self.veo_client, 'generate_video_clip'):
                logger.info(f"🎬 Attempting VEO-3 generation for clip {i+1}/{len(veo_prompts)}")
                try:
                    clip_path = self.veo_client.generate_video_clip(
                        prompt=prompt,
                        duration=clip_duration,
                        clip_id=clip_id,
                        aspect_ratio=aspect_ratio,
                        prefer_veo3=True,
                        enable_audio=True
                    )
                    if clip_path and os.path.exists(clip_path):
                        logger.info(f"✅ VEO-3 clip {i+1} generated: {clip_path}")
                        clips.append(clip_path)
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ VEO-3 failed for clip {i+1}: {e}")
            
            # STEP 2: Try VEO-2 generation
            if self.use_real_veo2 and self.veo_client and hasattr(self.veo_client, 'generate_video_clip'):
                logger.info(f"🎥 Attempting VEO-2 generation for clip {i+1}/{len(veo_prompts)}")
                try:
                    clip_path = self.veo_client.generate_video_clip(
                        prompt=prompt,
                        duration=clip_duration,
                        clip_id=clip_id,
                        aspect_ratio=aspect_ratio,
                        prefer_veo3=False,
                        enable_audio=False
                    )
                    if clip_path and os.path.exists(clip_path):
                        logger.info(f"✅ VEO-2 clip {i+1} generated: {clip_path}")
                        clips.append(clip_path)
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ VEO-2 failed for clip {i+1}: {e}")
            
            # STEP 3: Try Gemini Image Generation fallback
            if self.image_client:
                logger.info(f"🎨 Attempting Gemini Image fallback for clip {i+1}")
                try:
                    image_clips = self.image_client.generate_image_based_clips(
                        prompts=[{
                            'veo2_prompt': prompt,
                            'description': f"Scene {i+1}: {prompt[:100]}"
                        }],
                        config={
                            'duration_seconds': clip_duration,
                            'images_per_second': 4,
                            'aspect_ratio': aspect_ratio
                        },
                        video_id=clip_id
                    )
                    if image_clips and len(image_clips) > 0:
                        clip_path = image_clips[0]['clip_path']
                        if os.path.exists(clip_path):
                            logger.info(f"✅ Gemini Image clip {i+1} generated: {clip_path}")
                            clips.append(clip_path)
                            continue
                except Exception as e:
                    logger.warning(f"⚠️ Gemini Image failed for clip {i+1}: {e}")
            
            # STEP 4: Local tool fallback (FFmpeg-based)
            logger.info(f"🛠️ Using local tool fallback for clip {i+1}")
            try:
                clip_path = os.path.join(self.session_dir, f"local_clip_{i}_{self.session_id}.mp4")
                self._create_enhanced_local_clip(clip_path, prompt, clip_duration, aspect_ratio)
                if os.path.exists(clip_path):
                    logger.info(f"✅ Local tool clip {i+1} generated: {clip_path}")
                    clips.append(clip_path)
                    continue
            except Exception as e:
                logger.warning(f"⚠️ Local tool failed for clip {i+1}: {e}")
            
            # STEP 5: Final text fallback
            logger.info(f"📝 Using text fallback for clip {i+1}")
            clip_path = os.path.join(self.session_dir, f"text_clip_{i}_{self.session_id}.mp4")
            self._create_text_overlay_clip(clip_path, prompt, clip_duration, aspect_ratio)
            clips.append(clip_path)
        
        return clips
    
    def _create_error_clip(self, output_path: str, error_message: str, duration: float, aspect_ratio: str):
        """Create an error clip for failed generation"""
        try:
            import subprocess
            
            # Parse aspect ratio to get dimensions
            if aspect_ratio == "9:16":
                width, height = 1080, 1920
            elif aspect_ratio == "16:9":
                width, height = 1920, 1080
            elif aspect_ratio == "1:1":
                width, height = 1080, 1080
            else:
                width, height = 1920, 1080
            
            # Create error video with FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c=red:s={width}x{height}:d={duration}:r=30',
                '-vf', f'drawtext=text=\'{error_message}\':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Error clip created: {output_path}")
            else:
                logger.error(f"❌ Error clip creation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Error clip creation failed: {e}")
    
    def _create_enhanced_local_clip(self, output_path: str, prompt: str, duration: float, aspect_ratio: str = "16:9"):
        """Create enhanced local clip with proper aspect ratio"""
        try:
            import subprocess
            
            # Parse aspect ratio to get dimensions
            if aspect_ratio == "9:16":
                width, height = 1080, 1920
            elif aspect_ratio == "16:9":
                width, height = 1920, 1080
            elif aspect_ratio == "1:1":
                width, height = 1080, 1080
            else:
                width, height = 1920, 1080
            
            # Create animated background based on prompt content
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ['baby', 'child', 'cute', 'adorable']):
                colors = ["0xFFB6C1", "0xFFC0CB", "0xFFE4E1"]
                main_text = "👶 Adorable Baby Content"
                bg_animation = "geq=r='255*abs(sin(2*PI*T/5))':g='182*abs(cos(2*PI*T/5))':b='193'"
            elif any(word in prompt_lower for word in ['animal', 'pet', 'dog', 'cat', 'wildlife']):
                colors = ["0x228B22", "0x32CD32", "0x90EE90"]
                main_text = "🐾 Amazing Animal Content"
                bg_animation = "geq=r='34*abs(sin(2*PI*T/4))':g='139*abs(cos(2*PI*T/4))':b='34'"
            else:
                colors = ["0x2563EB", "0x7C3AED", "0xDB2777"]
                main_text = "✨ Amazing Content"
                bg_animation = "geq=r='37*abs(sin(2*PI*T/5))':g='99*abs(cos(2*PI*T/5))':b='235'"
            
            # Create subtitle text from prompt
            prompt_words = prompt.split()[:4]
            subtitle_text = " ".join(prompt_words) + "..."
            
            # Build FFmpeg command with proper aspect ratio
            base_color = random.choice(colors)
            
            filter_complex = [
                f"color=c={base_color}:s={width}x{height}:d={duration}[bg]",
                f"[bg]{bg_animation}[animated]",
                f"[animated]boxblur=3:1[blur]",
                f"[blur]drawtext=text='{main_text}':fontcolor=white:fontsize=60:x='(w-text_w)/2+sin(t)*20':y='(h-text_h)/2-100':shadowx=3:shadowy=3[title]",
                f"[title]drawtext=text='{subtitle_text}':fontcolor=yellow:fontsize=40:x='(w-text_w)/2':y='(h-text_h)/2+50':shadowx=2:shadowy=2[subtitle]",
                f"[subtitle]drawtext=text='Professional AI Content':fontcolor=white:fontsize=30:x='(w-text_w)/2':y='h-80':shadowx=2:shadowy=2[final]",
                f"[final]fade=in:0:30,fade=out:{int(duration*30-30)}:30"
            ]
            
            filter_str = ";".join(filter_complex)
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'nullsrc=s={width}x{height}:d={duration}:r=30',
                '-filter_complex', filter_str,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Enhanced local clip created: {output_path}")
            else:
                logger.error(f"❌ Enhanced local clip failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Enhanced local clip creation failed: {e}")
    
    def _create_text_overlay_clip(self, output_path: str, prompt: str, duration: float, aspect_ratio: str = "16:9"):
        """Create text overlay clip with proper aspect ratio"""
        try:
            # Parse aspect ratio to get dimensions
            if aspect_ratio == "9:16":
                width, height = 1080, 1920
            elif aspect_ratio == "16:9":
                width, height = 1920, 1080
            elif aspect_ratio == "1:1":
                width, height = 1080, 1080
            else:
                width, height = 1920, 1080
            
            # Create a gradient background
            color = (random.randint(50, 150), random.randint(50, 150), random.randint(100, 255))
            clip = ColorClip(size=(width, height), color=color, duration=duration)
            
            # Extract key words from prompt for display
            words = prompt.split()[:5]
            display_text = " ".join(words) + "..."
            
            # Create main text with proper sizing for aspect ratio
            font_size = 80 if aspect_ratio == "16:9" else 60
            txt = TextClip(display_text, 
                          fontsize=font_size, color='white', font='Arial-Bold',
                          stroke_color='black', stroke_width=2)
            txt = txt.set_position('center').set_duration(duration)
            
            # Create subtitle
            subtitle = TextClip("AI Generated Video", 
                               fontsize=font_size//2, color='lightgray', font='Arial')
            subtitle = subtitle.set_position(('center', 'bottom')).set_duration(duration)
            
            final_clip = CompositeVideoClip([clip, txt, subtitle])
            final_clip.write_videofile(output_path, fps=30, verbose=False, logger=None)
            final_clip.close()
            
        except Exception as e:
            logger.error(f"❌ Text overlay clip creation failed: {e}")
            self._create_placeholder_clip(output_path, int(duration))
    
    def _create_placeholder_clip(self, output_path: str, duration: int):
        """Create a placeholder video clip"""
        try:
            # Create a simple colored clip
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            clip = ColorClip(size=(1280, 720), color=color, duration=duration)
            
            # Add some text
            txt = TextClip(f"Generated Clip\nSession: {self.session_id}", 
                          fontsize=50, color='white', font='Arial-Bold')
            txt = txt.set_position('center').set_duration(duration)
            
            final_clip = CompositeVideoClip([clip, txt])
            final_clip.write_videofile(output_path, fps=30, verbose=False, logger=None)
            final_clip.close()
            
        except Exception as e:
            logger.error(f"❌ Placeholder clip creation failed: {e}")
            raise

    def _clean_script_for_tts(self, script, target_duration: int) -> str:
        """Clean and optimize script for TTS generation ensuring ONLY spoken dialogue with proper UTF-8 handling"""
        import re
        import json
        
        logger.info(f"🎤 Cleaning script for TTS: target {target_duration}s")
        
        dialogue_lines = []
        
        # STEP 1: Extract ONLY actual dialogue content - NO visual descriptions
        try:
            # Handle both string and dict input
            if isinstance(script, str):
                try:
                    script_data = json.loads(script)
                except json.JSONDecodeError:
                    script_data = None
            else:
                script_data = script
                
            # Extract dialogue from JSON/dict structure
            if script_data and isinstance(script_data, dict):
                # Check if it's a direct text response
                if 'text' in script_data:
                    text_content = script_data['text']
                    # Extract only the actual spoken text, not visual descriptions
                    clean_text = self._extract_spoken_dialogue(text_content)
                    if clean_text and len(clean_text.strip()) > 10:
                        dialogue_lines.append(clean_text)
                
                # Extract from hook
                elif 'hook' in script_data and isinstance(script_data['hook'], dict):
                    if 'text' in script_data['hook']:
                        hook_text = script_data['hook']['text']
                        # Extract only spoken content, not visual cues
                        clean_hook = self._extract_spoken_dialogue(hook_text)
                        if clean_hook and len(clean_hook.strip()) > 5:
                            dialogue_lines.append(clean_hook)
                
                # Extract from segments
                if 'segments' in script_data and isinstance(script_data['segments'], list):
                    for segment in script_data['segments']:
                        if isinstance(segment, dict) and 'text' in segment:
                            seg_text = segment['text']
                            # Extract only spoken content
                            clean_seg = self._extract_spoken_dialogue(seg_text)
                            if clean_seg and len(clean_seg.strip()) > 5:
                                dialogue_lines.append(clean_seg)
                
                # Extract from CTA (but skip generic ones)
                if 'cta' in script_data and isinstance(script_data['cta'], dict):
                    if 'text' in script_data['cta']:
                        cta_text = script_data['cta']['text']
                        # Skip generic CTAs
                        if cta_text and not any(skip in cta_text.lower() for skip in ['subscribe', 'follow', 'like', 'share', 'save', 'comment']):
                            clean_cta = self._extract_spoken_dialogue(cta_text)
                            if clean_cta and len(clean_cta.strip()) > 5:
                                dialogue_lines.append(clean_cta)
                
                logger.info(f"📝 Extracted {len(dialogue_lines)} dialogue lines from structured script")
                
        except Exception as e:
            logger.warning(f"Structured parsing failed: {e}")
            script_data = None
        
        # STEP 2: If structured parsing failed, parse as raw text
        if not dialogue_lines:
            script_str = str(script)
            logger.info(f"🔍 Parsing raw script text: {script_str[:200]}...")
            
            # First, try to extract quoted dialogue (most reliable)
            quoted_matches = re.findall(r'"([^"]+)"', script_str)
            for quote in quoted_matches:
                clean_line = self._extract_spoken_dialogue(quote)
                if clean_line and len(clean_line.strip()) > 10:
                    dialogue_lines.append(clean_line)
            
            # If no quotes, create natural dialogue based on topic
            if not dialogue_lines:
                logger.info("🎯 No quotes found, creating natural dialogue from topic")
                # Extract topic-based dialogue
                topic_dialogue = self._create_natural_dialogue_from_topic(script_str, target_duration)
                if topic_dialogue:
                    dialogue_lines.append(topic_dialogue)
        
        # STEP 3: Create final script with proper UTF-8 handling
        if dialogue_lines:
            # Join all dialogue lines
            full_dialogue = ' '.join(dialogue_lines)
        else:
            # Create fallback based on topic
            logger.warning("⚠️ No dialogue found, creating topic-based fallback")
            full_dialogue = self._create_engaging_fallback_script(target_duration)
        
        # STEP 4: Ensure proper UTF-8 encoding
        try:
            # Normalize Unicode characters
            import unicodedata
            full_dialogue = unicodedata.normalize('NFKC', full_dialogue)
        except Exception as e:
            logger.warning(f"Unicode normalization failed: {e}")
        
        # STEP 5: Calculate optimal word count and trim if needed
        target_words = int(target_duration * 2.2)  # 2.2 words per second for natural pacing
        words = full_dialogue.split()
        
        if len(words) > target_words:
            # Find the best cutoff point that ends with complete sentences
            trimmed_words = words[:target_words]
            trimmed_text = ' '.join(trimmed_words)
            
            # Look for sentence endings within the last 20% of the text
            search_start = int(len(trimmed_text) * 0.8)
            search_text = trimmed_text[search_start:]
            
            # Find the last complete sentence
            sentence_endings = ['.', '!', '?', '؟', '۔']  # Include Persian punctuation
            last_sentence_end = -1
            
            for ending in sentence_endings:
                pos = search_text.rfind(ending)
                if pos > last_sentence_end:
                    last_sentence_end = pos
            
            if last_sentence_end > 0:
                # Cut at the last complete sentence
                final_script = trimmed_text[:search_start + last_sentence_end + 1]
            else:
                # No good sentence ending found, add proper ending
                final_script = trimmed_text.rstrip('.,!?؟۔') + '.'
        else:
            # Script is shorter than target, use as-is but ensure proper ending
            final_script = full_dialogue
            if not final_script.endswith(('.', '!', '?', '؟', '۔')):
                final_script += '.'
        
        # STEP 6: Final cleanup and validation
        final_script = re.sub(r'\s+', ' ', final_script).strip()
        final_words = final_script.split()
        estimated_duration = len(final_words) / 2.2
        
        logger.info(f"✅ TTS script prepared:")
        logger.info(f"   Original: {len(words)} words")
        logger.info(f"   Final: {len(final_words)} words")
        logger.info(f"   Target duration: {target_duration}s")
        logger.info(f"   Estimated duration: {estimated_duration:.1f}s")
        logger.info(f"   Preview: {final_script[:100]}...")
        
        # Save to session for debugging with proper UTF-8 encoding
        try:
            script_file = os.path.join(self.session_dir, "tts_script.json")
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "final_script": final_script,
                    "original_length": len(words),
                    "cleaned_length": len(final_words),
                    "target_duration": target_duration,
                    "estimated_duration": estimated_duration,
                    "timestamp": str(datetime.now())
                }, f, indent=2, ensure_ascii=False)  # ensure_ascii=False for proper UTF-8
            logger.info(f"📁 TTS script saved to: {script_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save TTS script: {e}")
        
        return final_script
    
    def _create_natural_dialogue_from_topic(self, script_text: str, target_duration: int) -> str:
        """Create natural dialogue from topic information"""
        # Extract topic keywords
        topic_keywords = []
        if hasattr(self, 'config') and self.config:
            topic = getattr(self.config, 'topic', '')
            if topic:
                topic_keywords = topic.lower().split()
        
        # Create engaging dialogue based on topic
        if any(word in script_text.lower() for word in ['persian', 'mythology', 'coke', 'pepsi']):
            return self._create_persian_mythology_dialogue(target_duration)
        elif any(word in script_text.lower() for word in ['comedy', 'funny', 'humor']):
            return self._create_comedy_dialogue(target_duration)
        else:
            return self._create_generic_engaging_dialogue(target_duration)
    
    def _create_persian_mythology_dialogue(self, target_duration: int) -> str:
        """Create Persian mythology themed dialogue"""
        base_dialogue = (
            "In ancient Persian mythology, two powerful deities engaged in an epic battle for supremacy. "
            "Ahura Mazda, the wise lord of light, championed the sacred cola of wisdom and truth. "
            "Meanwhile, Angra Mainyu, the destructive spirit, promoted his own dark beverage of chaos. "
            "The people of ancient Persia watched in amazement as these divine forces clashed. "
            "Each deity claimed their drink possessed magical properties that would grant eternal happiness. "
            "The battle raged for centuries, with mortals choosing sides in this cosmic cola war. "
            "Some say this mythological conflict continues to this day, manifesting in modern brand loyalty. "
            "Which divine beverage would you choose in this eternal struggle between light and darkness?"
        )
        
        # Adjust length based on target duration
        words = base_dialogue.split()
        target_words = int(target_duration * 2.2)
        
        if len(words) > target_words:
            # Trim to target length
            return ' '.join(words[:target_words]) + '.'
        elif len(words) < target_words * 0.7:
            # Extend if too short
            extension = (
                " Legend tells of brave warriors who would drink their chosen beverage before battle. "
                "The taste would reveal their destiny and guide them to victory or defeat. "
                "Even today, some believe you can taste the ancient magic in every sip."
            )
            return base_dialogue + extension
        else:
            return base_dialogue
    
    def _create_comedy_dialogue(self, target_duration: int) -> str:
        """Create comedy themed dialogue"""
        base_dialogue = (
            "Have you ever wondered what would happen if ancient gods had to choose between cola brands? "
            "Picture this: Zeus sitting on Mount Olympus, holding two cans and looking completely confused. "
            "Meanwhile, Thor is arguing with Loki about which drink gives better lightning powers. "
            "The Egyptian gods are having a heated debate in their pyramid boardroom. "
            "Even the Buddha is scratching his head, trying to find the middle way between two sodas. "
            "It's the ultimate divine dilemma that has puzzled deities for millennia. "
            "Who knew that choosing a beverage could cause such cosmic chaos?"
        )
        
        # Adjust length based on target duration
        words = base_dialogue.split()
        target_words = int(target_duration * 2.2)
        
        if len(words) > target_words:
            return ' '.join(words[:target_words]) + '.'
        elif len(words) < target_words * 0.7:
            extension = (
                " The funniest part? They all end up drinking water anyway because immortals have to stay hydrated. "
                "But don't tell the marketing departments that!"
            )
            return base_dialogue + extension
        else:
            return base_dialogue
    
    def _create_generic_engaging_dialogue(self, target_duration: int) -> str:
        """Create generic engaging dialogue"""
        base_dialogue = (
            "Welcome to an incredible journey that will change how you see the world around you. "
            "Today we're exploring fascinating stories that have shaped human culture for generations. "
            "These tales reveal surprising connections between ancient wisdom and modern life. "
            "You'll discover hidden meanings that most people never notice. "
            "Every detail has been carefully chosen to create an unforgettable experience. "
            "By the end of this journey, you'll have a completely new perspective. "
            "Are you ready to dive into this amazing adventure?"
        )
        
        # Adjust length based on target duration
        words = base_dialogue.split()
        target_words = int(target_duration * 2.2)
        
        if len(words) > target_words:
            return ' '.join(words[:target_words]) + '.'
        elif len(words) < target_words * 0.7:
            extension = (
                " This is just the beginning of what promises to be an extraordinary exploration. "
                "Stay with us as we uncover more incredible insights together."
            )
            return base_dialogue + extension
        else:
            return base_dialogue
    
    def _create_engaging_fallback_script(self, target_duration: int) -> str:
        """Create engaging fallback script when all else fails"""
        return self._create_generic_engaging_dialogue(target_duration)
    
    def _extract_spoken_dialogue(self, text: str) -> str:
        """Extract only spoken dialogue from text, removing visual descriptions and stage directions"""
        import re
        
        if not text:
            return ""
        
        # Remove visual cues and stage directions
        text = re.sub(r'\([^)]*\)', '', text)  # Remove parentheses
        text = re.sub(r'\[[^\]]*\]', '', text)  # Remove brackets
        text = re.sub(r'\{[^}]*\}', '', text)  # Remove curly braces
        text = re.sub(r'<[^>]*>', '', text)   # Remove angle brackets
        
        # Remove visual description patterns - ENHANCED
        text = re.sub(r'Starts with.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Opens with.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Cuts (abruptly )?to.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Shows.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Zoom.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Camera.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Shot of.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Visual.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Scene.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Montage.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Fade.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Transition.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Background.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'As the.*?asked,', '', text, flags=re.IGNORECASE)
        text = re.sub(r'quickly cuts.*?\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'then back to.*?\.', '', text, flags=re.IGNORECASE)
        
        # Remove more visual patterns that got through
        text = re.sub(r'(Starts|Opens|Cuts|Shows|Begins|Ends)\s+(with|to|at|in)\s+.*?[.!?]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(a|an|the)\s+(rapid|quick|slow|gradual|sudden)\s+(cut|transition|fade|zoom)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(majestic|ancient|mythological)\s+(Persian|setting|backdrop|scene)', '', text, flags=re.IGNORECASE)
        
        # Remove technical directions
        text = re.sub(r'(Then,?\s*as\s+the\s+punchline|as\s+the\s+punchline)[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'lands,?\s*the\s+speaker[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'breaks\s+into[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'raises\s+an\s+eyebrow[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'->\s*A\s+single[^.]*\.', '', text, flags=re.IGNORECASE)
        
        # Remove timing and technical cues
        text = re.sub(r'\d+:\d+', '', text)
        text = re.sub(r'SFX:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'VISUAL:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'SOUND:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'MUSIC:', '', text, flags=re.IGNORECASE)
        
        # Remove incomplete sentences that start with visual words
        sentences = re.split(r'[.!?]+', text)
        clean_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Skip sentences that start with visual description words
                visual_starters = [
                    'starts', 'opens', 'cuts', 'shows', 'begins', 'ends',
                    'camera', 'shot', 'scene', 'visual', 'montage', 'fade',
                    'transition', 'background', 'zoom', 'focus', 'pan'
                ]
                
                first_word = sentence.split()[0].lower() if sentence.split() else ''
                if first_word not in visual_starters:
                    # Also check if it's a fragment starting with "a rapid", "an ancient", etc.
                    if not re.match(r'^(a|an|the)\s+(rapid|quick|slow|gradual|sudden|majestic|ancient)', sentence, re.IGNORECASE):
                        clean_sentences.append(sentence)
        
        text = '. '.join(clean_sentences)
        
        # Clean up whitespace and punctuation
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^[:\-\s,]+', '', text)
        text = re.sub(r'[,\s]+$', '', text)
        text = re.sub(r'[.]+$', '.', text)
        
        return text
    
    def _extract_dialogue_only(self, text: str) -> str:
        """Extract only actual dialogue from text, removing visual descriptions"""
        import re
        
        if not text:
            return ""
        
        # Remove visual descriptions and stage directions
        text = re.sub(r'Opens with[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'As the question is asked[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'quickly cuts to[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'then back to[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'with a thought bubble[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'showing[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Zoom to[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Cut to[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Images of[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Visual[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Shot of[^.]*\.', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Camera[^.]*\.', '', text, flags=re.IGNORECASE)
        
        # Remove stage directions in parentheses and brackets
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'\[[^\]]*\]', '', text)
        text = re.sub(r'\{[^}]*\}', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        
        # Remove technical directions
        text = re.sub(r'(Then,?\s*as\s+the\s+punchline|as\s+the\s+punchline)[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'lands,?\s*the\s+speaker[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'breaks\s+into[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'raises\s+an\s+eyebrow[^,]*,?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'->\s*A\s+single[^.]*\.', '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace and punctuation
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^[:\-\s,]+', '', text)
        text = re.sub(r'[,\s]+$', '', text)
        text = re.sub(r'[.]+$', '.', text)
        
        return text
    
    def _extract_dialogue_from_raw_text(self, text: str) -> List[str]:
        """Extract dialogue from raw text content"""
        import re
        
        dialogue_lines = []
        
        # Look for quoted dialogue
        quoted_matches = re.findall(r'"([^"]+)"', text)
        for quote in quoted_matches:
            clean_quote = self._extract_dialogue_only(quote)
            if clean_quote and len(clean_quote.strip()) > 10:
                dialogue_lines.append(clean_quote)
        
        # Look for dialogue patterns
        dialogue_patterns = [
            r'آیا می‌دانستید[^.]*؟',  # Persian question pattern
            r'در آغاز[^.]*\.', 
            r'اهورامزدا[^.]*\.', 
            r'اما اهریمن[^.]*\.', 
            r'و نبرد آغاز شد[^.]*\.', 
            r'از معبد[^.]*\.', 
            r'امروز هم[^.]*\.', 
        ]
        
        for pattern in dialogue_patterns:
            matches = re.findall(pattern, text, re.UNICODE)
            for match in matches:
                clean_match = self._extract_dialogue_only(match)
                if clean_match and len(clean_match.strip()) > 5:
                    dialogue_lines.append(clean_match)
        
        return dialogue_lines
    
    def _generate_voiceover(self, script: str, duration: int = 30, config: Dict = None) -> str:
        """Generate high-quality AI voice-over using Google Cloud TTS"""
        logger.info(f"🎤 Generating high-quality voice-over for {duration}s video...")
        
        if not config:
            config = {}
        
        # Extract context for voice selection
        narrative_context = config.get('narrative', 'neutral')
        feeling_context = config.get('feeling', 'neutral')
        
        try:
            # STEP 1: Clean script thoroughly for TTS
            clean_script = self._clean_script_for_tts(script, duration)
            
            if not clean_script or len(clean_script.strip()) < 10:
                logger.warning("⚠️ Script too short after cleaning, using fallback")
                clean_script = f"Welcome to this amazing video about {config.get('topic', 'our topic')}. This content will definitely interest you. Thanks for watching!"
            
            # STEP 2: Try Google Cloud TTS first for natural voice
            try:
                from .google_tts_client import GoogleTTSClient
                
                logger.info("🎤 Using Google Cloud TTS for natural voice...")
                google_tts = GoogleTTSClient()
                
                audio_path = google_tts.generate_speech(
                    text=clean_script,
                    feeling=feeling_context,
                    narrative=narrative_context,
                    duration_target=duration,
                    use_ssml=False  # Keep it simple for reliability
                )
                
                if audio_path and os.path.exists(audio_path):
                    # Move to session directory
                    session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
                    os.makedirs(session_dir, exist_ok=True)
                    final_path = os.path.join(session_dir, f"google_tts_voice_{uuid.uuid4()}.mp3")
                    import shutil
                    shutil.move(audio_path, final_path)
                    
                    logger.info(f"✅ Google Cloud TTS SUCCESS: Natural voice generated")
                    logger.info(f"📁 Audio file: {final_path}")
                    return final_path
                    
            except Exception as e:
                logger.warning(f"⚠️ Google Cloud TTS failed: {e}")
                logger.info("🔄 Falling back to enhanced gTTS...")
            
            # STEP 3: Enhanced gTTS fallback with better settings
            try:
                from gtts import gTTS
                
                # Enhanced TTS settings based on feeling
                tts_config = {
                    'lang': 'en',
                    'slow': False,
                    'tld': 'com'  # Use .com for most natural voice
                }
                
                # Adjust for feeling
                if feeling_context in ['funny', 'excited']:
                    tts_config['tld'] = 'co.uk'  # British accent for variety
                elif feeling_context in ['serious', 'dramatic']:
                    tts_config['tld'] = 'com.au'  # Australian for deeper tone
                
                # Add natural speech patterns
                enhanced_script = self._add_natural_speech_patterns(clean_script, feeling_context)
                
                tts = gTTS(text=enhanced_script, **tts_config)
                session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
                os.makedirs(session_dir, exist_ok=True)
                audio_path = os.path.join(session_dir, f"enhanced_voice_{uuid.uuid4()}.mp3")
                tts.save(audio_path)
                
                logger.info(f"✅ Enhanced gTTS generated: {audio_path}")
                return audio_path
                
            except Exception as gtts_error:
                logger.error(f"❌ Enhanced gTTS failed: {gtts_error}")
                
                # STEP 4: Simple fallback
                try:
                    simple_tts = gTTS(text=clean_script, lang='en', slow=False)
                    session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
                    os.makedirs(session_dir, exist_ok=True)
                    audio_path = os.path.join(session_dir, f"simple_voice_{uuid.uuid4()}.mp3")
                    simple_tts.save(audio_path)
                    logger.info(f"✅ Simple TTS fallback: {audio_path}")
                    return audio_path
                except Exception as simple_error:
                    logger.error(f"❌ All TTS methods failed: {simple_error}")
                    return None
        
        except Exception as e:
            logger.error(f"❌ Voice generation completely failed: {e}")
            return None
    
    def _add_natural_speech_patterns(self, text: str, feeling: str) -> str:
        """Add natural speech patterns to make TTS sound more human"""
        
        # Add natural pauses and emphasis
        if feeling == "excited":
            text = text.replace('.', '! ')
            text = text.replace(',', ', ')
            
        elif feeling == "dramatic":
            text = text.replace('.', '... ')
            text = text.replace('!', '! ')
            
        elif feeling == "funny":
            text = text.replace('.', '. ')
            # Add slight emphasis
            text = text.replace(' and ', ' and, ')
            
        # Add natural breathing pauses
        sentences = text.split('. ')
        if len(sentences) > 2:
            # Add pause after every other sentence
            for i in range(1, len(sentences), 2):
                if i < len(sentences):
                    sentences[i] = sentences[i] + ' '
        
        return '. '.join(sentences)
    
    def _add_text_overlays(self, video_clip, config: GeneratedVideoConfig, duration: float):
        """Add professional text overlays with larger, more readable text and better positioning"""
        from moviepy.editor import TextClip, CompositeVideoClip
        
        logger.info(f"📝 Adding enhanced text overlays to {duration:.1f}s video")
        
        try:
            overlays = []
            
            # Get video dimensions
            video_width, video_height = video_clip.size
            
            # Calculate much larger font sizes for better readability
            # For 1080px width: title=120px, subtitle=80px, overlay=100px
            title_fontsize = max(80, int(video_width * 0.11))  # 11% of video width
            subtitle_fontsize = max(60, int(video_width * 0.08))  # 8% of video width
            overlay_fontsize = max(70, int(video_width * 0.09))  # 9% of video width
            
            # Calculate safe text areas with more generous margins
            safe_width = int(video_width * 0.9)  # 90% of video width
            
            # Generate intelligent text overlays based on content
            intelligent_overlays = self._generate_intelligent_text_overlays(config, duration)
            
            # Add overlays with proper timing and positioning
            for i, overlay_data in enumerate(intelligent_overlays):
                try:
                    text = overlay_data['text']
                    start_time = overlay_data['start_time']
                    end_time = overlay_data['end_time']
                    position = overlay_data['position']
                    style = overlay_data.get('style', 'normal')
                    
                    # Use AI agent decisions for font, color, and styling
                    ai_font = overlay_data.get('font', 'Arial-Bold')
                    ai_color = overlay_data.get('color', 'white')
                    
                    # Determine font size based on style
                    if style == 'title':
                        fontsize = title_fontsize
                        color = ai_color
                        font = ai_font
                        stroke_width = 4
                    elif style == 'subtitle':
                        fontsize = subtitle_fontsize
                        color = ai_color
                        font = ai_font
                        stroke_width = 3
                    elif style == 'highlight':
                        fontsize = overlay_fontsize
                        color = ai_color
                        font = ai_font
                        stroke_width = 3
                    else:
                        fontsize = subtitle_fontsize
                        color = ai_color
                        font = ai_font
                        stroke_width = 2
                    
                    # Create text clip with better readability
                    text_clip = TextClip(
                        text,
                        fontsize=fontsize,
                        color=color,
                        font=font,
                        stroke_color='black',
                        stroke_width=stroke_width,
                        method='caption',
                        size=(safe_width, None),  # Allow height to auto-adjust
                        align='center'
                    )
                    
                    # Position text based on specified position
                    if position == 'top':
                        text_position = ('center', video_height * 0.1)
                    elif position == 'center':
                        text_position = 'center'
                    elif position == 'bottom':
                        text_position = ('center', video_height * 0.8)
                    elif position == 'upper_center':
                        text_position = ('center', video_height * 0.3)
                    elif position == 'lower_center':
                        text_position = ('center', video_height * 0.7)
                    else:
                        text_position = 'center'
                    
                    # Set timing and position
                    text_clip = text_clip.set_position(text_position).set_start(start_time).set_duration(end_time - start_time)
                    
                    overlays.append(text_clip)
                    logger.info(f"✅ Added text overlay: '{text[:30]}...' ({fontsize}px) at {start_time:.1f}s-{end_time:.1f}s")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create text overlay {i}: {e}")
                    continue
            
            # Combine video with all overlays
            if overlays:
                final_video = CompositeVideoClip([video_clip] + overlays)
                logger.info(f"✅ Added {len(overlays)} enhanced text overlays")
                return final_video
            else:
                logger.warning("⚠️ No overlays created, returning original video")
                return video_clip
                
        except Exception as e:
            logger.error(f"❌ Enhanced text overlay creation failed: {e}")
            logger.info("🔄 Returning video without overlays")
            return video_clip
    
    def _generate_intelligent_text_overlays(self, config: GeneratedVideoConfig, duration: float) -> List[Dict]:
        """Generate intelligent, content-specific text overlays with AI agents making decisions about content, font, colors, position, and style"""
        overlays = []
        
        try:
            # Use AI agents to analyze the mission and make overlay decisions
            topic = config.topic
            category = config.category.value
            platform = config.target_platform.value
            
            logger.info(f"🤖 AI AGENTS: Analyzing mission for intelligent text overlay decisions")
            logger.info(f"🎯 Mission: {topic}")
            logger.info(f"📱 Platform: {platform} | Category: {category} | Duration: {duration:.0f}s")
            
            # AI Agent-powered overlay generation with comprehensive decision making
            ai_prompt = f"""
            You are a team of AI agents specializing in viral video text overlays. Analyze this mission and make intelligent decisions:
            
            MISSION: {topic}
            PLATFORM: {platform}
            CATEGORY: {category}
            DURATION: {duration:.0f}s
            
            AI AGENTS TEAM:
            1. CONTENT STRATEGIST: Decides overlay text content based on mission psychology
            2. VISUAL DESIGNER: Chooses fonts, colors, and visual hierarchy
            3. PLATFORM EXPERT: Optimizes for platform-specific engagement patterns
            4. TIMING SPECIALIST: Determines optimal positioning and timing
            5. PSYCHOLOGY EXPERT: Ensures emotional impact and persuasion
            
            AGENT DECISIONS REQUIRED:
            - Content: What specific text will accomplish the mission?
            - Font: Which font style creates the desired psychological impact?
            - Color: What colors will maximize engagement and readability?
            - Position: Where should text be placed for maximum impact?
            - Style: What visual treatment enhances the message?
            - Timing: When should each overlay appear for optimal effect?
            
            Generate 6-8 text overlays with AI agent reasoning for each decision:
            
            [
                {{
                    "text": "🔥 Specific mission-focused text",
                    "start_time": 0.0,
                    "end_time": 4.0,
                    "position": "top",
                    "style": "title",
                    "font": "Impact",
                    "color": "red",
                    "reasoning": {{
                        "content_strategy": "Opens with shock value to grab attention",
                        "visual_design": "Bold red color creates urgency and importance",
                        "platform_optimization": "Top placement works well on mobile vertical scroll",
                        "timing_logic": "First 4 seconds are critical for hook retention",
                        "psychology": "Red color triggers fight-or-flight response, increasing engagement"
                    }}
                }},
                {{
                    "text": "🤯 Another strategic overlay",
                    "start_time": 5.0,
                    "end_time": 9.0,
                    "position": "center",
                    "style": "highlight",
                    "font": "Arial-Bold",
                    "color": "yellow",
                    "reasoning": {{
                        "content_strategy": "Builds on initial hook with emotional amplification",
                        "visual_design": "Yellow stands out against most backgrounds",
                        "platform_optimization": "Center position captures focus on mobile",
                        "timing_logic": "Mid-video placement maintains engagement",
                        "psychology": "Mind-blown emoji creates curiosity and shareability"
                    }}
                }}
            ]
            
            REQUIREMENTS:
            1. Text must be SPECIFIC to the mission "{topic}" - no generic content
            2. Each overlay needs complete AI agent reasoning
            3. Colors: red, yellow, white, cyan, orange, green, magenta, blue
            4. Fonts: Impact, Arial-Bold, Comic Sans MS, Times-Bold, Helvetica-Bold
            5. Positions: top, center, bottom, upper_center, lower_center
            6. Styles: title, subtitle, highlight, normal
            7. Timing must fit within {duration:.0f} seconds
            8. Focus on MISSION ACCOMPLISHMENT, not just engagement
            
            Return ONLY the JSON array, no other text.
            """
            
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                response = model.generate_content(ai_prompt)
                
                # Extract JSON from response
                import json
                import re
                
                # Find JSON array in response
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    overlay_data = json.loads(json_match.group())
                    
                    # Process AI agent decisions
                    for i, overlay in enumerate(overlay_data):
                        if isinstance(overlay, dict) and 'text' in overlay:
                            # Ensure timing is within video duration
                            start_time = min(float(overlay.get('start_time', 0)), duration - 2)
                            end_time = min(float(overlay.get('end_time', start_time + 3)), duration)
                            
                            if end_time > start_time:
                                # Log AI agent reasoning
                                reasoning = overlay.get('reasoning', {})
                                logger.info(f"🤖 AI AGENT OVERLAY {i+1}: {overlay['text'][:30]}...")
                                logger.info(f"   📝 Content Strategy: {reasoning.get('content_strategy', 'N/A')}")
                                logger.info(f"   🎨 Visual Design: {reasoning.get('visual_design', 'N/A')}")
                                logger.info(f"   📱 Platform Optimization: {reasoning.get('platform_optimization', 'N/A')}")
                                logger.info(f"   ⏰ Timing Logic: {reasoning.get('timing_logic', 'N/A')}")
                                logger.info(f"   🧠 Psychology: {reasoning.get('psychology', 'N/A')}")
                                
                                overlays.append({
                                    'text': overlay['text'],
                                    'start_time': start_time,
                                    'end_time': end_time,
                                    'position': overlay.get('position', 'center'),
                                    'style': overlay.get('style', 'normal'),
                                    'font': overlay.get('font', 'Arial-Bold'),
                                    'color': overlay.get('color', 'white'),
                                    'reasoning': reasoning
                                })
                    
                    logger.info(f"🤖 AI AGENTS generated {len(overlays)} intelligent text overlays with complete reasoning")
                    
            except Exception as e:
                logger.warning(f"⚠️ AI agent text generation failed: {e}")
                overlays = []
            
            # Fallback: Create mission-specific overlays if AI fails
            if not overlays:
                logger.info("🔄 AI agents failed, using mission-specific fallback")
                overlays = self._create_mission_specific_overlays(config, duration)
            
            return overlays
            
        except Exception as e:
            logger.error(f"❌ AI agent text overlay generation failed: {e}")
            return self._create_mission_specific_overlays(config, duration)
    
    def _create_mission_specific_overlays(self, config: GeneratedVideoConfig, duration: float) -> List[Dict]:
        """Create topic-specific text overlays as fallback"""
        overlays = []
        topic = config.topic.lower()
        
        try:
            # Persian mythology specific overlays
            if 'persian' in topic and 'mythology' in topic:
                overlays = [
                    {
                        'text': '🏺 Ancient Persian Mythology',
                        'start_time': 0.0,
                        'end_time': 4.0,
                        'position': 'top',
                        'style': 'title',
                        'color': 'white'
                    },
                    {
                        'text': '⚔️ Epic Battle of Deities',
                        'start_time': 5.0,
                        'end_time': 9.0,
                        'position': 'center',
                        'style': 'highlight',
                        'color': 'yellow'
                    },
                    {
                        'text': '🌟 Ahura Mazda vs Angra Mainyu',
                        'start_time': 10.0,
                        'end_time': 14.0,
                        'position': 'upper_center',
                        'style': 'subtitle',
                        'color': 'cyan'
                    },
                    {
                        'text': '🥤 The Sacred Cola Wars',
                        'start_time': 15.0,
                        'end_time': 19.0,
                        'position': 'center',
                        'style': 'highlight',
                        'color': 'orange'
                    },
                    {
                        'text': '✨ Choose Your Divine Drink',
                        'start_time': 20.0,
                        'end_time': 24.0,
                        'position': 'lower_center',
                        'style': 'subtitle',
                        'color': 'magenta'
                    },
                    {
                        'text': '🔥 Ancient Wisdom Revealed',
                        'start_time': 25.0,
                        'end_time': 29.0,
                        'position': 'center',
                        'style': 'highlight',
                        'color': 'red'
                    },
                    {
                        'text': '👆 Follow for More Mythology',
                        'start_time': max(0, duration - 8),
                        'end_time': duration,
                        'position': 'bottom',
                        'style': 'normal',
                        'color': 'white'
                    }
                ]
            
            # Comedy specific overlays
            elif 'comedy' in topic or 'funny' in topic:
                overlays = [
                    {
                        'text': '😂 Prepare to Laugh!',
                        'start_time': 0.0,
                        'end_time': 4.0,
                        'position': 'top',
                        'style': 'title',
                        'color': 'yellow'
                    },
                    {
                        'text': '🤣 This is Hilarious!',
                        'start_time': 8.0,
                        'end_time': 12.0,
                        'position': 'center',
                        'style': 'highlight',
                        'color': 'cyan'
                    },
                    {
                        'text': '💀 I Can\'t Even...',
                        'start_time': 16.0,
                        'end_time': 20.0,
                        'position': 'upper_center',
                        'style': 'subtitle',
                        'color': 'orange'
                    },
                    {
                        'text': '🔥 Comedy Gold!',
                        'start_time': 24.0,
                        'end_time': 28.0,
                        'position': 'center',
                        'style': 'highlight',
                        'color': 'red'
                    },
                    {
                        'text': '👆 Follow for More Laughs',
                        'start_time': max(0, duration - 6),
                        'end_time': duration,
                        'position': 'bottom',
                        'style': 'normal',
                        'color': 'white'
                    }
                ]
            
            # Generic engaging overlays
            else:
                clean_topic = config.topic.replace('_', ' ').title()
                overlays = [
                    {
                        'text': f'✨ {clean_topic}',
                        'start_time': 0.0,
                        'end_time': 4.0,
                        'position': 'top',
                        'style': 'title',
                        'color': 'white'
                    },
                    {
                        'text': '🤯 Mind-Blowing!',
                        'start_time': 6.0,
                        'end_time': 10.0,
                        'position': 'center',
                        'style': 'highlight',
                        'color': 'cyan'
                    },
                    {
                        'text': '🔥 This is Amazing!',
                        'start_time': 12.0,
                        'end_time': 16.0,
                        'position': 'upper_center',
                        'style': 'subtitle',
                        'color': 'orange'
                    },
                    {
                        'text': '⚡ Incredible Content!',
                        'start_time': 18.0,
                        'end_time': 22.0,
                        'position': 'center',
                        'style': 'highlight',
                        'color': 'yellow'
                    },
                    {
                        'text': '💫 Don\'t Miss This!',
                        'start_time': 24.0,
                        'end_time': 28.0,
                        'position': 'lower_center',
                        'style': 'subtitle',
                        'color': 'magenta'
                    },
                    {
                        'text': '👆 Follow for More',
                        'start_time': max(0, duration - 6),
                        'end_time': duration,
                        'position': 'bottom',
                        'style': 'normal',
                        'color': 'white'
                    }
                ]
            
            # Adjust timing for shorter videos
            if duration < 30:
                # Remove some overlays and adjust timing
                overlays = overlays[:4]  # Keep only first 4 overlays
                for i, overlay in enumerate(overlays):
                    # Distribute overlays evenly
                    overlay['start_time'] = (duration / len(overlays)) * i
                    overlay['end_time'] = min(overlay['start_time'] + 4, duration)
            
            logger.info(f"📝 Created {len(overlays)} topic-specific text overlays")
            return overlays
            
        except Exception as e:
            logger.error(f"❌ Topic-specific overlay creation failed: {e}")
            return []

    def _generate_audio(self, script: str, duration: int) -> str:
        """Generate audio from script using Google TTS with enhanced naturalness"""
        try:
            # Clean the script for TTS
            clean_script = self._clean_script_for_tts(script, duration)
            
            # Create unique filename in the audio directory
            audio_filename = f"google_tts_voice_{uuid.uuid4()}.mp3"
            audio_path = os.path.join(self.audio_dir, audio_filename)
            
            # Generate speech using Google TTS
            tts = gTTS(text=clean_script, lang='en', slow=False)
            tts.save(audio_path)
            
            # Verify the audio file was created
            if not os.path.exists(audio_path):
                raise Exception("Audio file was not created")
            
            # Get actual duration
            try:
                audio_clip = AudioFileClip(audio_path)
                actual_duration = audio_clip.duration
                audio_clip.close()
                
                logger.info(f"🎵 Audio generated: {audio_path}")
                logger.info(f"🎵 Duration: {actual_duration:.1f}s (target: {duration}s)")
                
                return audio_path
            except Exception as e:
                logger.warning(f"⚠️ Could not get audio duration: {e}")
                return audio_path
                
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            
            # Create a fallback silent audio file
            try:
                fallback_audio = os.path.join(self.audio_dir, f"fallback_audio_{uuid.uuid4()}.mp3")
                
                # Create silent audio using FFmpeg
                cmd = [
                    'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo:d={duration}',
                    '-acodec', 'mp3', '-y', fallback_audio
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"🔇 Created fallback silent audio: {fallback_audio}")
                    return fallback_audio
                else:
                    logger.error(f"❌ Fallback audio creation failed: {result.stderr}")
                    raise Exception("Both audio generation and fallback failed")
                    
            except Exception as fallback_error:
                logger.error(f"❌ Fallback audio creation failed: {fallback_error}")
                raise Exception("All audio generation methods failed")

    def _compose_final_video(self, video_clips: List[str], audio_path: str, 
                           config: GeneratedVideoConfig) -> str:
        """Compose final video with proper duration alignment and text overlays"""
        try:
            # Create session directory path
            final_video_path = os.path.join(self.session_dir, f"final_video_{self.session_id}.mp4")
            
            # Use the requested duration from config, not audio duration
            target_duration = config.duration_seconds
            logger.info(f"🎯 Target duration from config: {target_duration}s")
            
            # Load and validate audio
            audio_clip = None
            
            if audio_path and os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                logger.info(f"🎵 Audio duration: {audio_clip.duration:.1f}s")
                
                # Adjust audio to match target duration
                if audio_clip.duration > target_duration:
                    audio_clip = audio_clip.subclip(0, target_duration)
                    logger.info(f"🎵 Audio trimmed to {target_duration}s")
                elif audio_clip.duration < target_duration:
                    # Extend audio with silence or loop
                    from moviepy.audio.AudioClip import AudioClip
                    silence_duration = target_duration - audio_clip.duration
                    silence = AudioClip(lambda t: [0, 0], duration=silence_duration)
                    audio_clip = concatenate_audioclips([audio_clip, silence])
                    logger.info(f"🎵 Audio extended to {target_duration}s with silence")
            else:
                logger.warning("⚠️ No audio file found, using config duration")
            
            # Load video clips and ensure they match target duration
            clips = []
            total_video_duration = 0
            
            for clip_path in video_clips:
                if os.path.exists(clip_path):
                    clip = VideoFileClip(clip_path)
                    clips.append(clip)
                    total_video_duration += clip.duration
            
            if not clips:
                raise RenderingError("No valid video clips found")
            
            logger.info(f"🎬 Video clips total duration: {total_video_duration:.1f}s")
            logger.info(f"🎯 Adjusting video to match requested duration: {target_duration}s")
            
            # Adjust video duration to match target (not audio)
            if abs(total_video_duration - target_duration) > 0.5:
                logger.info(f"⚖️ Adjusting video duration from {total_video_duration:.1f}s to {target_duration:.1f}s")
                
                # Calculate speed factor
                speed_factor = total_video_duration / target_duration
                
                if speed_factor > 1.1:  # Video too long, speed up
                    from moviepy.video.fx.speedx import speedx
                    clips = [clip.fx(speedx, speed_factor) for clip in clips]
                    logger.info(f"⚡ Speeding up video by {speed_factor:.2f}x")
                elif speed_factor < 0.9:  # Video too short, slow down or loop
                    if speed_factor > 0.7:
                        from moviepy.video.fx.speedx import speedx
                        clips = [clip.fx(speedx, speed_factor) for clip in clips]
                        logger.info(f"🐌 Slowing down video by {speed_factor:.2f}x")
                    else:
                        # Loop clips to reach target duration
                        loops_needed = int(target_duration / total_video_duration) + 1
                        clips = clips * loops_needed
                        logger.info(f"🔄 Looping clips {loops_needed} times")
            
            # Concatenate video clips
            video = concatenate_videoclips(clips)
            
            # Final duration adjustment to exact target
            if video.duration > target_duration:
                video = video.subclip(0, target_duration)
            elif video.duration < target_duration:
                # Extend last frame
                last_frame = video.get_frame(video.duration - 0.1)
                extension = ImageClip(last_frame, duration=target_duration - video.duration)
                video = concatenate_videoclips([video, extension])
            
            # Add text overlays
            video_with_overlays = self._add_text_overlays(video, config, video.duration)
            
            # Add fade-out effect (1-2 seconds)
            fade_duration = min(2.0, video_with_overlays.duration * 0.1)  # 1-2 seconds or 10% of video, whichever is smaller
            if fade_duration > 0.5:  # Only apply if video is long enough
                if fadeout:
                    video_with_overlays = video_with_overlays.fx(fadeout, fade_duration)
                    logger.info(f"🌅 Added {fade_duration:.1f}s fade-out effect")
            
            # Sync audio to match video duration exactly
            if audio_clip:
                # Ensure audio matches video duration exactly
                if audio_clip.duration > video_with_overlays.duration:
                    audio_clip = audio_clip.subclip(0, video_with_overlays.duration)
                elif audio_clip.duration < video_with_overlays.duration:
                    # Extend audio with silence
                    from moviepy.audio.AudioClip import AudioClip
                    silence_duration = video_with_overlays.duration - audio_clip.duration
                    silence = AudioClip(lambda t: [0, 0], duration=silence_duration)
                    audio_clip = concatenate_audioclips([audio_clip, silence])
                
                # Apply fade-out to audio as well to match video
                if fade_duration > 0.5 and audio_fadeout:
                    audio_clip = audio_clip.fx(audio_fadeout, fade_duration)
                    logger.info(f"🔊 Added {fade_duration:.1f}s audio fade-out effect")
                
                video_with_overlays = video_with_overlays.set_audio(audio_clip)
                logger.info(f"🎵 Audio synced: {audio_clip.duration:.1f}s")
            
            # Write final video
            video_with_overlays.write_videofile(
                final_video_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                verbose=False,
                logger=None
            )
            
            # Clean up
            for clip in clips:
                clip.close()
            if audio_clip:
                audio_clip.close()
            video.close()
            video_with_overlays.close()
            
            # Verify final video duration
            final_clip = VideoFileClip(final_video_path)
            final_duration = final_clip.duration
            final_clip.close()
            
            logger.info(f"🎬 Final video composed: {final_video_path}")
            logger.info(f"✅ Final duration: {final_duration:.1f}s (target: {target_duration:.1f}s)")
            
            return final_video_path
            
        except Exception as e:
            logger.error(f"❌ Video composition failed: {e}")
            raise RenderingError(f"Video composition failed: {str(e)}")

    def _create_veo2_prompts(self, config: GeneratedVideoConfig, script: Union[str, dict]) -> List[str]:
        """Create VEO-2 prompts based on AI agent decisions and script content"""
        topic = config.topic
        style = config.visual_style
        
        # Extract actual content from script if available
        script_content = ""
        if isinstance(script, dict):
            # Extract text content from dictionary script
            if 'hook' in script and isinstance(script['hook'], dict) and 'text' in script['hook']:
                script_content += script['hook']['text'] + " "
            if 'segments' in script and isinstance(script['segments'], list):
                for segment in script['segments']:
                    if isinstance(segment, dict) and 'text' in segment:
                        script_content += segment['text'] + " "
        else:
            script_content = str(script)
        
        # Let AI agents decide on prompts based on mission and script
        logger.info(f"🤖 AI agents analyzing mission: {topic}")
        logger.info(f"🎬 Script content: {script_content[:200]}...")
        
        try:
            # Use Gemini to generate appropriate prompts based on the mission
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt_generation_request = f"""
            MISSION: {topic}
            SCRIPT CONTENT: {script_content}
            VISUAL STYLE: {style}
            PLATFORM: {config.target_platform.value}
            CATEGORY: {config.category.value}
            
            As a professional video director, create 3 distinct visual prompts for this mission.
            Each prompt should be specific, actionable, and designed to accomplish the mission.
            
            Requirements:
            - Each prompt should be 1-2 sentences maximum
            - Focus on visual elements that support the mission
            - Consider the target platform and category
            - Make prompts diverse but cohesive
            - No generic templates - be specific to this mission
            
            Return only the 3 prompts, one per line, no numbering or formatting.
            """
            
            response = model.generate_content(prompt_generation_request)
            ai_prompts = response.text.strip().split('\n')
            
            # Clean and validate prompts
            cleaned_prompts = []
            for prompt in ai_prompts:
                clean_prompt = prompt.strip()
                if clean_prompt and len(clean_prompt) > 10:
                    # Add style suffix if not already present
                    if style not in clean_prompt.lower():
                        clean_prompt += f", {style}"
                    cleaned_prompts.append(clean_prompt)
            
            # Ensure we have at least 3 prompts
            while len(cleaned_prompts) < 3:
                cleaned_prompts.append(f"Professional visual content supporting: {topic}, {style}")
            
            logger.info(f"🎨 AI-generated prompts for '{topic}':")
            for i, prompt in enumerate(cleaned_prompts[:3], 1):
                logger.info(f"   Prompt {i}: {prompt}")
            
            return cleaned_prompts[:3]
            
        except Exception as e:
            logger.error(f"❌ AI prompt generation failed: {e}")
            # Fallback: Create generic prompts based on mission analysis
            fallback_prompts = [
                f"Professional visual content that supports: {topic}, {style}",
                f"Engaging scene designed to accomplish: {topic}, {style}",
                f"Compelling visual narrative for: {topic}, {style}"
            ]
            logger.info(f"🔄 Using fallback prompts for '{topic}'")
            return fallback_prompts

# NO MOCK CLIENTS - ONLY REAL VEO GENERATION ALLOWED!