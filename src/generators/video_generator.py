"""
Video generator using AI and video editing libraries with REAL VEO-2 integration
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Union
import random
import time
import google.generativeai as genai
from moviepy.editor import *
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from gtts import gTTS
import tempfile
import uuid
import subprocess
import requests

# Import VEO client for real video generation
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from veo_client import VeoApiClient

try:
    from ..models.video_models import (
        VideoAnalysis, GeneratedVideoConfig, GeneratedVideo, 
        Platform, VideoCategory, VideoOrientation, ForceGenerationMode
    )
    from ..utils.logging_config import get_logger
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
        
        # Initialize session - use provided session_id or generate one
        self.session_id = session_id or str(uuid.uuid4())[:8]
        
        # UNIFIED OUTPUT STRUCTURE - All files go in session directory
        self.base_output_dir = "outputs"
        self.session_dir = os.path.join(self.base_output_dir, f"session_{self.session_id}")
        self.output_dir = self.session_dir  # Main output directory for this session
        
        # Create unified directory structure
        os.makedirs(self.session_dir, exist_ok=True)
        
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
            
            # Keep script as dict if it's a dict (for proper extraction later)
            if isinstance(script_data, dict):
                logger.info(f"📝 Script generated: {len(str(script_data))} characters")
                return script_data  # Return dict directly for proper extraction
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
            
            {' '.join(config.main_content)}
            
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
                from ..agents.enhanced_orchestrator_with_19_agents import EnhancedOrchestrator
                orchestrator = EnhancedOrchestrator(self.api_key)
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
            model = genai.GenerativeModel('gemini-2.5-flash')
            
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
    
    def _download_veo2_video(self, gcs_uri: str, clip_index: int) -> str:
        """Download VEO-2 generated video from GCS to local storage"""
        try:
            import subprocess
            
            # Create local path in session directory
            session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
            os.makedirs(session_dir, exist_ok=True)
            local_path = os.path.join(session_dir, f"veo2_clip_{clip_index}_{self.session_id}.mp4")
            
            # Use gsutil to download the file
            cmd = ["gsutil", "cp", gcs_uri, local_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Downloaded VEO-2 video: {gcs_uri} -> {local_path}")
                return local_path
            else:
                logger.error(f"❌ Failed to download VEO-2 video: {result.stderr}")
                raise Exception(f"Download failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Error downloading VEO-2 video: {e}")
            raise
    
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
                import subprocess
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
            session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
            os.makedirs(session_dir, exist_ok=True)
            final_video_path = os.path.join(session_dir, f"final_video_{self.session_id}.mp4")
            
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
            
            # Add text overlays and titles
            video_with_overlays = self._add_comprehensive_text_overlays(video, config)
            
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
            raise RenderingError("video_composition", f"Video composition failed: {str(e)}")
    
    def _add_comprehensive_text_overlays(self, video_clip, config: GeneratedVideoConfig):
        """Add comprehensive text overlays including titles, hooks, and subtitles with AI agent decision-making"""
        try:
            # Use AI agents to determine optimal text layout
            text_layout = self._get_ai_agent_text_layout(config, video_clip.duration)
            
            overlays = []
            
            # Create title overlay with intelligent line breaking
            title_text = self._create_video_title(config.topic)
            title_lines = self._split_text_intelligently(title_text, max_chars_per_line=25)
            
            # Create multi-line title if needed
            if len(title_lines) > 1:
                # Multi-line title
                title_clips = []
                for i, line in enumerate(title_lines):
                    line_clip = TextClip(line, 
                                       fontsize=text_layout['title']['fontsize'],
                                       color=text_layout['title']['color'],
                                       font=text_layout['title']['font'],
                                       stroke_color=text_layout['title']['stroke_color'],
                                       stroke_width=text_layout['title']['stroke_width'])
                    
                    # Position each line with proper spacing
                    y_offset = text_layout['title']['position'][1] + (i * text_layout['title']['line_spacing'])
                    line_clip = line_clip.set_position((text_layout['title']['position'][0], y_offset))
                    line_clip = line_clip.set_duration(text_layout['title']['duration']).set_start(text_layout['title']['start'])
                    title_clips.append(line_clip)
                
                overlays.extend(title_clips)
            else:
                # Single line title
                title = TextClip(title_text, 
                               fontsize=text_layout['title']['fontsize'],
                               color=text_layout['title']['color'],
                               font=text_layout['title']['font'],
                               stroke_color=text_layout['title']['stroke_color'],
                               stroke_width=text_layout['title']['stroke_width'])
                title = title.set_position(text_layout['title']['position']).set_duration(text_layout['title']['duration']).set_start(text_layout['title']['start'])
                overlays.append(title)
            
            # Create hook overlay with intelligent positioning
            hook_text = getattr(config, 'hook', 'Amazing content ahead!')
            hook_lines = self._split_text_intelligently(hook_text, max_chars_per_line=40)
            
            if len(hook_lines) > 1:
                # Multi-line hook
                hook_clips = []
                for i, line in enumerate(hook_lines):
                    line_clip = TextClip(line,
                                       fontsize=text_layout['hook']['fontsize'],
                                       color=text_layout['hook']['color'],
                                       font=text_layout['hook']['font'],
                                       stroke_color=text_layout['hook']['stroke_color'],
                                       stroke_width=text_layout['hook']['stroke_width'])
                    
                    y_offset = text_layout['hook']['position'][1] + (i * text_layout['hook']['line_spacing'])
                    line_clip = line_clip.set_position((text_layout['hook']['position'][0], y_offset))
                    line_clip = line_clip.set_duration(text_layout['hook']['duration']).set_start(text_layout['hook']['start'])
                    hook_clips.append(line_clip)
                
                overlays.extend(hook_clips)
            else:
                hook = TextClip(hook_text,
                              fontsize=text_layout['hook']['fontsize'],
                              color=text_layout['hook']['color'],
                              font=text_layout['hook']['font'],
                              stroke_color=text_layout['hook']['stroke_color'],
                              stroke_width=text_layout['hook']['stroke_width'])
                hook = hook.set_position(text_layout['hook']['position']).set_duration(text_layout['hook']['duration']).set_start(text_layout['hook']['start'])
                overlays.append(hook)
            
            # Create call-to-action overlay
            cta_text = getattr(config, 'call_to_action', 'Subscribe for more!')
            cta_lines = self._split_text_intelligently(cta_text, max_chars_per_line=30)
            
            if len(cta_lines) > 1:
                # Multi-line CTA
                cta_clips = []
                for i, line in enumerate(cta_lines):
                    line_clip = TextClip(line,
                                       fontsize=text_layout['cta']['fontsize'],
                                       color=text_layout['cta']['color'],
                                       font=text_layout['cta']['font'],
                                       stroke_color=text_layout['cta']['stroke_color'],
                                       stroke_width=text_layout['cta']['stroke_width'])
                    
                    y_offset = text_layout['cta']['position'][1] + (i * text_layout['cta']['line_spacing'])
                    line_clip = line_clip.set_position((text_layout['cta']['position'][0], y_offset))
                    line_clip = line_clip.set_duration(text_layout['cta']['duration']).set_start(text_layout['cta']['start'])
                    cta_clips.append(line_clip)
                
                overlays.extend(cta_clips)
            else:
                cta = TextClip(cta_text,
                             fontsize=text_layout['cta']['fontsize'],
                             color=text_layout['cta']['color'],
                             font=text_layout['cta']['font'],
                             stroke_color=text_layout['cta']['stroke_color'],
                             stroke_width=text_layout['cta']['stroke_width'])
                cta = cta.set_position(text_layout['cta']['position']).set_duration(text_layout['cta']['duration']).set_start(text_layout['cta']['start'])
                overlays.append(cta)
            
            # Create platform-specific overlay
            platform_text = f"#{config.target_platform.value.upper()}"
            platform = TextClip(platform_text,
                               fontsize=text_layout['platform']['fontsize'],
                               color=text_layout['platform']['color'],
                               font=text_layout['platform']['font'])
            platform = platform.set_position(text_layout['platform']['position']).set_duration(video_clip.duration)
            overlays.append(platform)
            
            # Combine all overlays
            if overlays:
                final_video = CompositeVideoClip([video_clip] + overlays)
                logger.info(f"✅ Added {len(overlays)} intelligent text overlays with AI agent positioning")
                return final_video
            else:
                return video_clip
            
        except Exception as e:
            logger.warning(f"⚠️ Intelligent text overlay creation failed: {e}, returning original video")
            return video_clip
    
    def _get_ai_agent_text_layout(self, config: GeneratedVideoConfig, duration: float) -> dict:
        """Use AI agents to determine optimal text positioning, colors, and fonts"""
        try:
            # Use AI to analyze content and determine optimal layout
            ai_prompt = f"""
            You are a team of AI agents specializing in video text overlay design. Analyze this video content and determine optimal text positioning:

            Video Details:
            - Topic: {config.topic}
            - Platform: {config.target_platform.value}
            - Category: {config.category}
            - Duration: {duration:.1f} seconds
            - Aspect Ratio: {"9:16" if config.target_platform.value == "tiktok" else "16:9"}

            Create a comprehensive text layout plan in this JSON format:
            {{
                "title": {{
                    "fontsize": 70,
                    "color": "white",
                    "font": "Arial-Bold",
                    "stroke_color": "black",
                    "stroke_width": 3,
                    "position": ["center", 100],
                    "duration": 3,
                    "start": 0,
                    "line_spacing": 80
                }},
                "hook": {{
                    "fontsize": 50,
                    "color": "yellow",
                    "font": "Arial-Bold",
                    "stroke_color": "red",
                    "stroke_width": 2,
                    "position": ["center", 200],
                    "duration": 3,
                    "start": 3,
                    "line_spacing": 60
                }},
                "cta": {{
                    "fontsize": 60,
                    "color": "lime",
                    "font": "Arial-Bold",
                    "stroke_color": "black",
                    "stroke_width": 2,
                    "position": ["center", 600],
                    "duration": 3,
                    "start": {duration - 3},
                    "line_spacing": 70
                }},
                "platform": {{
                    "fontsize": 40,
                    "color": "cyan",
                    "font": "Arial-Bold",
                    "position": [50, 50]
                }}
            }}

            Considerations:
            - TikTok videos need larger fonts and higher contrast
            - YouTube videos can use more varied positioning
            - Instagram needs aesthetic, clean layouts
            - Ensure text doesn't overlap with video content
            - Use colors that stand out based on the topic
            - Position text to avoid typical video content areas

            Return ONLY the JSON, no other text.
            """
            
            response = self.refinement_model.generate_content(ai_prompt)
            layout_data = self._extract_json_safely(response.text)
            
            if layout_data:
                logger.info("🎨 AI agents determined optimal text layout")
                return layout_data
            else:
                logger.warning("⚠️ AI layout generation failed, using platform defaults")
                
        except Exception as e:
            logger.error(f"❌ AI text layout generation failed: {e}")
        
        # Fallback to platform-specific defaults
        return self._get_platform_default_layout(config.target_platform.value, duration)
    
    def _get_platform_default_layout(self, platform: str, duration: float) -> dict:
        """Get platform-specific default text layouts"""
        if platform == "tiktok":
            return {
                "title": {
                    "fontsize": 80, "color": "white", "font": "Arial-Bold",
                    "stroke_color": "black", "stroke_width": 4,
                    "position": ["center", 80], "duration": 3, "start": 0, "line_spacing": 90
                },
                "hook": {
                    "fontsize": 60, "color": "yellow", "font": "Impact",
                    "stroke_color": "red", "stroke_width": 3,
                    "position": ["center", 300], "duration": 3, "start": 3, "line_spacing": 70
                },
                "cta": {
                    "fontsize": 70, "color": "lime", "font": "Arial-Bold",
                    "stroke_color": "black", "stroke_width": 3,
                    "position": ["center", 1600], "duration": 3, "start": max(0, duration - 3), "line_spacing": 80
                },
                "platform": {
                    "fontsize": 50, "color": "cyan", "font": "Arial-Bold",
                    "position": [50, 50]
                }
            }
        elif platform == "youtube":
            return {
                "title": {
                    "fontsize": 70, "color": "white", "font": "Arial-Bold",
                    "stroke_color": "black", "stroke_width": 3,
                    "position": ["center", 100], "duration": 3, "start": 0, "line_spacing": 80
                },
                "hook": {
                    "fontsize": 50, "color": "yellow", "font": "Arial-Bold",
                    "stroke_color": "red", "stroke_width": 2,
                    "position": ["center", 200], "duration": 3, "start": 3, "line_spacing": 60
                },
                "cta": {
                    "fontsize": 60, "color": "red", "font": "Arial-Bold",
                    "stroke_color": "white", "stroke_width": 2,
                    "position": ["center", 600], "duration": 3, "start": max(0, duration - 3), "line_spacing": 70
                },
                "platform": {
                    "fontsize": 40, "color": "red", "font": "Arial-Bold",
                    "position": [50, 50]
                }
            }
        else:  # Instagram
            return {
                "title": {
                    "fontsize": 65, "color": "white", "font": "Arial-Bold",
                    "stroke_color": "black", "stroke_width": 2,
                    "position": ["center", 100], "duration": 3, "start": 0, "line_spacing": 75
                },
                "hook": {
                    "fontsize": 45, "color": "magenta", "font": "Arial-Bold",
                    "stroke_color": "black", "stroke_width": 2,
                    "position": ["center", 200], "duration": 3, "start": 3, "line_spacing": 55
                },
                "cta": {
                    "fontsize": 55, "color": "white", "font": "Arial-Bold",
                    "stroke_color": "magenta", "stroke_width": 2,
                    "position": ["center", 600], "duration": 3, "start": max(0, duration - 3), "line_spacing": 65
                },
                "platform": {
                    "fontsize": 35, "color": "magenta", "font": "Arial-Bold",
                    "position": [50, 50]
                }
            }
    
    def _split_text_intelligently(self, text: str, max_chars_per_line: int = 30) -> List[str]:
        """Split text intelligently at word boundaries for multi-line display"""
        if len(text) <= max_chars_per_line:
            return [text]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Check if adding this word would exceed the limit
            if len(current_line + " " + word) <= max_chars_per_line:
                current_line += " " + word if current_line else word
            else:
                # Start a new line
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        # Add the last line if it exists
        if current_line:
            lines.append(current_line)
        
        # If we have more than 3 lines, truncate and add "..."
        if len(lines) > 3:
            lines = lines[:3]
            if len(lines[2]) > max_chars_per_line - 3:
                lines[2] = lines[2][:max_chars_per_line - 3] + "..."
            else:
                lines[2] += "..."
        
        return lines
    
    def _extract_json_safely(self, text: str) -> Optional[Dict]:
        """Extracts a JSON object from a string, safely handling errors."""
        try:
            import re
            # Try to extract JSON from the text using regex
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try to parse the entire text as JSON
                return json.loads(text)
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Could not decode JSON from AI response: {text[:100]}...")
            return None

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
        """Clean and optimize script for TTS generation ensuring complete sentences and proper duration"""
        import re
        import json
        
        logger.info(f"🎤 Cleaning script for TTS: target {target_duration}s")
        
        dialogue_lines = []
        
        # STEP 1: Extract dialogue content based on script format
        try:
            # Try to parse as JSON first
            if isinstance(script, str):
                script_data = json.loads(script)
            else:
                script_data = script
                
            # Extract dialogue from JSON structure
            if script_data and 'hook' in script_data and isinstance(script_data['hook'], dict):
                if 'text' in script_data['hook']:
                    hook_text = script_data['hook']['text']
                    if hook_text and not any(skip in hook_text for skip in ['Below it', 'Link in Bio', 'animates']):
                        dialogue_lines.append(hook_text)
            
            if script_data and 'segments' in script_data and isinstance(script_data['segments'], list):
                for segment in script_data['segments']:
                    if isinstance(segment, dict) and 'text' in segment:
                        seg_text = segment['text']
                        if seg_text and not any(skip in seg_text for skip in ['Below it', 'Link in Bio', 'animates']):
                            dialogue_lines.append(seg_text)
            
            if script_data and 'cta' in script_data and isinstance(script_data['cta'], dict):
                if 'text' in script_data['cta']:
                    cta_text = script_data['cta']['text']
                    # Skip generic CTAs
                    if cta_text and not any(skip in cta_text for skip in ['Subscribe', 'Follow', 'Like', 'Share', 'Save']):
                        dialogue_lines.append(cta_text)
            
            logger.info(f"📝 Extracted {len(dialogue_lines)} dialogue lines from JSON script")
            
        except (json.JSONDecodeError, TypeError):
            # Not JSON, parse as text
            script_str = str(script)
            for line in script_str.split('\n'):
                if '**VOICEOVER:**' in line:
                    content = line.replace('**VOICEOVER:**', '').strip()
                    if content and len(content) > 10:
                        dialogue_lines.append(content)
        
        if not dialogue_lines:
            # Fallback: extract any meaningful content that isn't technical
            script_str = str(script)
            sentences = script_str.split('.')
            for sentence in sentences:
                clean_sentence = sentence.strip()
                # Skip technical lines
                if not any(skip in clean_sentence.upper() for skip in [
                    'HOOK', 'TEXT', 'TYPE', 'SHOCK', 'VISUAL', 'SOUND', 'SFX', 
                    'MUSIC', 'CUT', 'FADE', 'ZOOM', 'TRANSITION', 'OVERLAY',
                    'DURATION', 'TIMING', 'POSITION', 'STYLE', 'FONT', 'COLOR',
                    'BELOW IT', 'ANIMATES IN', 'CALL TO ACTION', 'LINK IN BIO',
                    'FINGER TAP', 'ICON', 'APPEARS', 'FADES IN', 'SLIDES IN',
                    'BACKGROUND', 'FOREGROUND', 'CAMERA', 'SHOT', 'ANGLE'
                ]):
                    if len(clean_sentence) > 15:
                        dialogue_lines.append(clean_sentence)
        
        # STEP 2: Join and clean technical metadata
        full_dialogue = ' '.join(dialogue_lines)
        
        # Remove technical terms that shouldn't be spoken
        technical_patterns = [
            r'\b(hook|text|type|shock|visual|sound|sfx|music|cut|fade|zoom)\b',
            r'\b(transition|overlay|duration|timing|position|style|font|color)\b',
            r'\b(scene|clip|video|audio|track|layer|effect|filter)\b',
            r'\[(.*?)\]',  # Remove brackets
            r'\((.*?)\)',  # Remove parentheses  
            r'\{(.*?)\}',  # Remove curly braces
            r'<(.*?)>',    # Remove angle brackets
            r'\*\*(.*?)\*\*',  # Remove bold markers
            r'=+',         # Remove equal signs
            r'-{3,}',      # Remove long dashes
            r'\d+:\d+',    # Remove timestamps
            r'\btiming:\s*\w+\b',  # Remove timing specifications
            r'\bstyle:\s*\w+\b',   # Remove style specifications
        ]
        
        cleaned_text = full_dialogue
        for pattern in technical_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up whitespace and punctuation
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        cleaned_text = re.sub(r'^[:\-\s]+', '', cleaned_text)
        cleaned_text = re.sub(r'[.]+$', '.', cleaned_text)
        
        # STEP 3: Calculate optimal word count for natural speech timing
        # Use 2.2 words per second for more natural pacing (instead of 2.5)
        target_words = int(target_duration * 2.2)
        words = cleaned_text.split()
        
        # If still no good content, create a natural fallback based on topic
        if len(words) < 5 or any(tech in cleaned_text.upper() for tech in [
            'BELOW IT', 'ANIMATES', 'CALL TO ACTION', 'LINK IN BIO', 'FINGER TAP',
            'SPARKLES', 'VIRAL', 'UNDERSCORE', 'ELEMENTS', 'SUBSCRIBE FOR MORE'
        ]):
            logger.warning("⚠️ Script cleaning failed, creating natural speech fallback")
            
            # Create natural speech that matches the target duration
            fallback_script = self._create_natural_fallback_script(target_duration, target_words)
            logger.info(f"🔄 Using natural speech fallback: {fallback_script[:100]}...")
            return fallback_script
        
        # STEP 4: Trim to target length while preserving complete sentences
        if len(words) > target_words:
            # Find the best cutoff point that ends with complete sentences
            trimmed_words = words[:target_words]
            trimmed_text = ' '.join(trimmed_words)
            
            # Look for sentence endings within the last 20% of the text
            search_start = int(len(trimmed_text) * 0.8)
            search_text = trimmed_text[search_start:]
            
            # Find the last complete sentence
            sentence_endings = ['.', '!', '?']
            last_sentence_end = -1
            
            for ending in sentence_endings:
                pos = search_text.rfind(ending)
                if pos > last_sentence_end:
                    last_sentence_end = pos
            
            if last_sentence_end > 0:
                # Cut at the last complete sentence
                final_script = trimmed_text[:search_start + last_sentence_end + 1]
                logger.info(f"✂️ Trimmed to complete sentence ending")
            else:
                # No good sentence ending found, add proper ending
                final_script = trimmed_text.rstrip('.,!?') + '.'
                logger.info(f"✂️ Added proper ending to trimmed text")
        else:
            # Script is shorter than target, use as-is but ensure proper ending
            final_script = cleaned_text
            if not final_script.endswith(('.', '!', '?')):
                final_script += '.'
        
        # STEP 5: Validate the final script
        final_words = final_script.split()
        estimated_duration = len(final_words) / 2.2
        
        logger.info(f"✅ TTS script prepared:")
        logger.info(f"   Original: {len(words)} words")
        logger.info(f"   Final: {len(final_words)} words")
        logger.info(f"   Target duration: {target_duration}s")
        logger.info(f"   Estimated duration: {estimated_duration:.1f}s")
        logger.info(f"   Preview: {final_script[:100]}...")
        
        # Save to session for debugging
        try:
            script_file = os.path.join(self.session_dir, "tts_script.json")
            with open(script_file, 'w') as f:
                json.dump({
                    "final_script": final_script,
                    "original_length": len(words),
                    "cleaned_length": len(final_words),
                    "target_duration": target_duration,
                    "estimated_duration": estimated_duration,
                    "timestamp": str(datetime.now())
                }, f, indent=2)
            logger.info(f"📁 TTS script saved to: {script_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save TTS script: {e}")
        
        return final_script
    
    def _create_natural_fallback_script(self, target_duration: int, target_words: int) -> str:
        """Create a natural fallback script when cleaning fails"""
        # Create engaging content that matches the target duration
        fallback_templates = {
            15: "This is an amazing story that will blow your mind. Get ready for something incredible that you've never seen before.",
            30: "Welcome to the most incredible story you'll hear today. This amazing content will completely change how you think about everything. Pay attention because what happens next is absolutely mind-blowing and unforgettable.",
            45: "Get ready for the most incredible story you've ever heard. This amazing content is going to completely blow your mind and change everything you thought you knew. What you're about to discover is so incredible that you'll want to share it with everyone you know.",
            60: "Welcome to the most amazing story that will completely change your perspective on everything. This incredible content is so mind-blowing that you won't believe what you're about to discover. Get ready for an experience that will stay with you forever and make you question everything you thought you knew about the world."
        }
        
        # Find the closest template
        closest_duration = min(fallback_templates.keys(), key=lambda x: abs(x - target_duration))
        base_script = fallback_templates[closest_duration]
        
        # Adjust to target word count
        words = base_script.split()
        if len(words) > target_words:
            # Trim to target
            words = words[:target_words]
            final_script = ' '.join(words)
            # Ensure proper ending
            if not final_script.endswith(('.', '!', '?')):
                final_script = final_script.rstrip('.,!?') + '.'
        elif len(words) < target_words:
            # Extend naturally
            extensions = [
                "This is truly amazing.", "You won't believe this.", "This changes everything.",
                "Absolutely incredible.", "This is mind-blowing.", "You need to see this.",
                "This is extraordinary.", "Simply unbelievable.", "This is phenomenal."
            ]
            
            while len(words) < target_words:
                extension = extensions[len(words) % len(extensions)]
                words.extend(extension.split())
            
            # Trim to exact target
            words = words[:target_words]
            final_script = ' '.join(words)
            if not final_script.endswith(('.', '!', '?')):
                final_script = final_script.rstrip('.,!?') + '.'
        else:
            final_script = base_script
        
        return final_script
    
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
        """Add professional text overlays and headers to the video"""
        from moviepy.editor import TextClip, CompositeVideoClip
        
        logger.info(f"📝 Adding professional text overlays to {duration:.1f}s video")
        
        try:
            overlays = []
            
            # HEADER/TITLE - Always show at the beginning
            title_text = self._create_video_title(config.topic)
            title_clip = TextClip(
                title_text,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3
            ).set_position(('center', 0.1)).set_duration(4).set_start(0)
            overlays.append(title_clip)
            
            # PLATFORM-SPECIFIC OVERLAYS
            if config.target_platform.value.lower() == 'tiktok':
                # TikTok style overlays
                overlays.extend([
                    TextClip(
                        "🔥 VIRAL CONTENT",
                        fontsize=60,
                        color='orange',
                        font='Impact'
                    ).set_position(('center', 0.8)).set_duration(3).set_start(1),
                    
                    TextClip(
                        "👆 FOLLOW FOR MORE",
                        fontsize=55,
                        color='white',
                        font='Arial-Bold',
                        stroke_color='black',
                        stroke_width=2
                    ).set_position(('center', 0.85)).set_duration(3).set_start(duration-4)
                ])
                
            elif config.target_platform.value.lower() == 'youtube':
                # YouTube style overlays
                overlays.extend([
                    TextClip(
                        "🎬 MUST WATCH!",
                        fontsize=65,
                        color='red',
                        font='Arial-Bold'
                    ).set_position(('center', 0.15)).set_duration(3).set_start(2),
                    
                    TextClip(
                        "LIKE & SUBSCRIBE",
                        fontsize=50,
                        color='white',
                        font='Arial-Bold',
                        stroke_color='red',
                        stroke_width=2
                    ).set_position(('center', 0.9)).set_duration(4).set_start(duration-5)
                ])
                
            elif config.target_platform.value.lower() == 'instagram':
                # Instagram style overlays
                overlays.extend([
                    TextClip(
                        "✨ AMAZING!",
                        fontsize=60,
                        color='magenta',
                        font='Arial-Bold'
                    ).set_position(('center', 0.2)).set_duration(3).set_start(1.5),
                    
                    TextClip(
                        "💖 DOUBLE TAP",
                        fontsize=55,
                        color='white',
                        font='Arial-Bold',
                        stroke_color='magenta',
                        stroke_width=2
                    ).set_position(('center', 0.85)).set_duration(3).set_start(duration-4)
                ])
            
            # MIDDLE ENGAGEMENT OVERLAY
            if duration > 8:
                middle_text = self._get_engagement_text(config.category.value)
                middle_clip = TextClip(
                    middle_text,
                    fontsize=65,
                    color='cyan',
                    font='Impact'
                ).set_position('center').set_duration(2).set_start(duration/2)
                overlays.append(middle_clip)
            
            # CATEGORY-SPECIFIC OVERLAY
            category_overlay = self._get_category_overlay(config.category.value, duration)
            if category_overlay:
                overlays.append(category_overlay)
            
            # Combine video with all overlays
            if overlays:
                final_video = CompositeVideoClip([video_clip] + overlays)
                logger.info(f"✅ Added {len(overlays)} professional text overlays")
                return final_video
            else:
                logger.warning("⚠️ No overlays created, returning original video")
                return video_clip
                
        except Exception as e:
            logger.error(f"❌ Text overlay creation failed: {e}")
            logger.info("🔄 Returning video without overlays")
            return video_clip
    
    def _create_video_title(self, topic: str) -> str:
        """Create an engaging title for the video"""
        # Clean and format the topic
        clean_topic = topic.replace('_', ' ').title()
        
        # Add engaging elements based on content
        if any(word in topic.lower() for word in ['funny', 'comedy', 'laugh']):
            return f"😂 {clean_topic}"
        elif any(word in topic.lower() for word in ['amazing', 'incredible', 'mind']):
            return f"🤯 {clean_topic}"
        elif any(word in topic.lower() for word in ['secret', 'hidden', 'truth']):
            return f"🔥 {clean_topic}"
        elif any(word in topic.lower() for word in ['new', 'latest', 'breaking']):
            return f"🚨 {clean_topic}"
        else:
            return f"✨ {clean_topic}"
    
    def _get_engagement_text(self, category: str) -> str:
        """Get engagement text based on category"""
        engagement_texts = {
            'Comedy': '😂 SO FUNNY!',
            'Entertainment': '🎉 AMAZING!',
            'Education': '🧠 LEARN THIS!',
            'News': '📰 BREAKING!',
            'Sports': '⚽ INCREDIBLE!',
            'Music': '🎵 EPIC!',
            'Gaming': '🎮 LEGENDARY!',
            'Food': '🍕 DELICIOUS!',
            'Travel': '✈️ WANDERLUST!',
            'Fashion': '👗 STUNNING!'
        }
        return engagement_texts.get(category, '🔥 WOW!')
    
    def _get_category_overlay(self, category: str, duration: float):
        """Get category-specific overlay"""
        from moviepy.editor import TextClip
        
        try:
            category_configs = {
                'Comedy': {'text': '🎭 COMEDY', 'color': 'yellow', 'font': 'Comic Sans MS'},
                'Entertainment': {'text': '🎪 ENTERTAINMENT', 'color': 'purple', 'font': 'Arial-Bold'},
                'Education': {'text': '📚 EDUCATIONAL', 'color': 'blue', 'font': 'Times-Bold'},
                'News': {'text': '📺 NEWS', 'color': 'red', 'font': 'Arial-Bold'},
                'Sports': {'text': '🏆 SPORTS', 'color': 'green', 'font': 'Impact'},
                'Music': {'text': '🎼 MUSIC', 'color': 'gold', 'font': 'Arial-Bold'}
            }
            
            config = category_configs.get(category)
            if config:
                return TextClip(
                    config['text'],
                    fontsize=45,
                    color=config['color'],
                    font=config['font']
                ).set_position(('left', 'top')).set_duration(3).set_start(0.5)
            
        except Exception as e:
            logger.warning(f"Category overlay creation failed: {e}")
        
        return None

# NO MOCK CLIENTS - ONLY REAL VEO GENERATION ALLOWED!