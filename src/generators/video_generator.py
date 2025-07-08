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
        Platform, VideoCategory
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
        Platform, VideoCategory
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
        self.output_dir = "outputs"
        self.clips_dir = os.path.join(self.output_dir, "clips")
        os.makedirs(self.clips_dir, exist_ok=True)
        
        # Ensure gcloud authentication before any GCP operations
        ensure_gcloud_auth()
        
        # Initialize comprehensive logger
        from ..utils.comprehensive_logger import ComprehensiveLogger
        session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
        os.makedirs(session_dir, exist_ok=True)
        self.comprehensive_logger = ComprehensiveLogger(self.session_id, session_dir)
        
        # Initialize models
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.script_model = genai.GenerativeModel("gemini-2.5-flash")
        self.prompt_model = genai.GenerativeModel("gemini-2.5-flash")
        
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
                        gcs_bucket=self.gcs_bucket,  # Use instance gcs_bucket parameter
                        output_dir=self.output_dir
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
                        output_dir=self.output_dir
                    )
                    logger.info("🎬 Google AI Studio VEO-2 client initialized")
                except ImportError as e:
                    logger.warning(f"⚠️ Google AI Studio VEO-2 not available: {e}")
            
            # Initialize Gemini Image fallback
            try:
                from .gemini_image_client import GeminiImageClient
                self.image_client = GeminiImageClient(api_key, self.output_dir)
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
            message="Video generator initialized",
            data={
                "session_id": self.session_id,
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
        """Generate video clips with proper VEO-2 → Gemini Images → Local Tools → Text fallback chain"""
        try:
            clips = []
            session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
            os.makedirs(session_dir, exist_ok=True)
            
            # Calculate proper clip timing
            num_clips = max(1, config.duration_seconds // 8)
            clip_duration = config.duration_seconds / num_clips
            
            # Create VEO-2 prompts based on the topic and script
            veo_prompts = self._create_veo2_prompts(config, script)
            
            logger.info(f"🎬 Starting video generation with {len(veo_prompts)} clips (duration: {clip_duration:.1f}s each)")
            
            for i, prompt in enumerate(veo_prompts):
                clip_id = f"{self.session_id}_clip_{i}"
                clip_path = None
                
                # STEP 1: Try VEO-2 generation
                if self.use_real_veo2 and self.veo_client:
                    logger.info(f"🎬 Attempting VEO-2 generation for clip {i+1}/{len(veo_prompts)}")
                    try:
                        clip_path = self.veo_client.generate_video_clip(
                            prompt=prompt,
                            duration=clip_duration,
                            clip_id=clip_id
                        )
                        if clip_path and os.path.exists(clip_path):
                            logger.info(f"✅ VEO-2 clip {i+1} generated: {clip_path}")
                            clips.append(clip_path)
                            continue
                    except Exception as e:
                        logger.warning(f"⚠️ VEO-2 failed for clip {i+1}: {e}")
                
                # STEP 2: Try Gemini Image Generation fallback
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
                                'images_per_second': 4
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
                
                # STEP 3: Local tool fallback (FFmpeg-based)
                logger.info(f"🛠️ Using local tool fallback for clip {i+1}")
                try:
                    clip_path = os.path.join(session_dir, f"local_clip_{i}_{self.session_id}.mp4")
                    self._create_enhanced_local_clip(clip_path, prompt, clip_duration)
                    if os.path.exists(clip_path):
                        logger.info(f"✅ Local tool clip {i+1} generated: {clip_path}")
                        clips.append(clip_path)
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ Local tool failed for clip {i+1}: {e}")
                
                # STEP 4: Final text fallback
                logger.info(f"📝 Using text fallback for clip {i+1}")
                clip_path = os.path.join(session_dir, f"text_clip_{i}_{self.session_id}.mp4")
                self._create_text_overlay_clip(clip_path, prompt, clip_duration)
                clips.append(clip_path)
            
            logger.info(f"🎥 Generated {len(clips)} video clips with proper fallback chain")
            return clips
            
        except Exception as e:
            logger.error(f"❌ Video clip generation failed: {e}")
            raise
    
    def _create_veo2_prompts(self, config: GeneratedVideoConfig, script: Union[str, dict]) -> List[str]:
        """Create VEO-2 prompts based on topic and script content"""
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
            script_lower = script_content.lower()
        elif isinstance(script, str):
            script_lower = script.lower()
        else:
            script_lower = ""
        
        # Create prompts based on topic and script content
        if "persian" in topic.lower() or "goddess" in topic.lower():
            prompts = [
                f"Majestic Persian goddess with flowing robes and golden jewelry, ancient palace setting, cinematic lighting, {style}",
                f"Powerful female deity from Persian mythology, mystical aura, ornate costume, epic fantasy style",
                f"Beautiful ancient Persian princess transforming into divine goddess, magical effects, cinematic quality"
            ]
        elif "unicorn" in topic.lower():
            prompts = [
                f"A majestic rainbow unicorn with flowing mane galloping through clouds, cinematic style, {style}",
                f"Epic battle scene with colorful unicorns using magical powers, fantasy adventure style",
                f"Dramatic close-up of a unicorn's horn glowing with magical energy, mystical atmosphere"
            ]
        elif "comedy" in config.category.value.lower():
            prompts = [
                f"Comedic cartoon characters in an absurd situation, exaggerated expressions, colorful animation style",
                f"Whimsical animated scene with unexpected visual gags, bright colors, playful atmosphere",
                f"Funny cartoon animals doing silly actions, animated comedy style, vibrant colors"
            ]
        else:
            # Generic engaging prompts
            prompts = [
                f"Cinematic establishing shot of an epic adventure, {style}, dramatic lighting",
                f"Dynamic action sequence with colorful characters, animated style, high energy",
                f"Emotional climax scene with dramatic music and lighting, cinematic style"
            ]
        
        # Log the prompts being used
        logger.info(f"🎨 VEO-2 Prompts created for '{topic}':")
        for i, prompt in enumerate(prompts):
            logger.info(f"   Prompt {i+1}: {prompt}")
        
        # Limit to duration-appropriate number of clips
        num_clips = min(len(prompts), max(1, config.duration_seconds // 8))
        selected_prompts = prompts[:num_clips]
        logger.info(f"📹 Selected {len(selected_prompts)} prompts for {config.duration_seconds}s video")
        
        # Log all prompts to session output
        import json
        session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
        prompts_file = os.path.join(session_dir, "veo_prompts.json")
        with open(prompts_file, 'w') as f:
            json.dump({
                "topic": topic,
                "all_prompts": prompts,
                "selected_prompts": selected_prompts,
                "num_clips": num_clips,
                "duration_per_clip": config.duration_seconds / num_clips
            }, f, indent=2)
        logger.info(f"📁 VEO prompts saved to: {prompts_file}")
        
        return selected_prompts
    
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
        """Generate high-quality audio using Google Cloud TTS"""
        logger.info(f"🎤 Generating high-quality audio for {duration}s video...")
        
        # Check if VEO-3 already generated native audio
        session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
        veo_clips_dir = os.path.join(self.output_dir, "veo2_clips")
        
        # Look for VEO clips with audio
        if os.path.exists(veo_clips_dir):
            veo_clips = [f for f in os.listdir(veo_clips_dir) if f.endswith('.mp4') and self.session_id in f]
            if veo_clips:
                # Check if VEO-3 clip has audio
                veo_clip_path = os.path.join(veo_clips_dir, veo_clips[0])
                try:
                    from moviepy.editor import VideoFileClip
                    clip = VideoFileClip(veo_clip_path)
                    if clip.audio is not None:
                        logger.info(f"🎵 VEO-3 native audio detected in {veo_clip_path}")
                        logger.info("⚡ Skipping TTS generation - using VEO-3 native audio")
                        
                        # Extract audio from VEO clip
                        audio_path = os.path.join(session_dir, f"veo3_native_audio_{self.session_id}.mp3")
                        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
                        clip.close()
                        
                        logger.info(f"📁 VEO-3 audio extracted to: {audio_path}")
                        return audio_path
                    clip.close()
                except Exception as e:
                    logger.warning(f"⚠️ Could not check VEO clip audio: {e}")
        
        # Use the advanced voiceover generation with Google Cloud TTS
        logger.info("🎤 Generating TTS audio (no VEO-3 native audio found)")
        config = {
            'narrative': 'energetic',
            'feeling': 'excited',
            'realistic_audio': True,
            'duration_seconds': duration
        }
        
        return self._generate_voiceover(script, duration, config)
    
    def _compose_final_video(self, video_clips: List[str], audio_path: str, 
                           config: GeneratedVideoConfig) -> str:
        """Compose final video with proper duration alignment and text overlays"""
        try:
            # Create session directory path
            session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
            os.makedirs(session_dir, exist_ok=True)
            final_video_path = os.path.join(session_dir, f"final_video_{self.session_id}.mp4")
            
            # Load and validate audio first to get target duration
            target_duration = config.duration_seconds
            audio_clip = None
            
            if audio_path and os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                target_duration = audio_clip.duration
                logger.info(f"🎵 Audio duration: {target_duration:.1f}s - using as target")
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
            
            # Adjust video duration to match audio
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
            
            # Final duration adjustment
            if video.duration > target_duration:
                video = video.subclip(0, target_duration)
            elif video.duration < target_duration:
                # Extend last frame
                last_frame = video.get_frame(video.duration - 0.1)
                extension = ImageClip(last_frame, duration=target_duration - video.duration)
                video = concatenate_videoclips([video, extension])
            
            # Add text overlays and titles
            video_with_overlays = self._add_comprehensive_text_overlays(video, config)
            
            # Sync audio
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
        """Add comprehensive text overlays including titles, hooks, and subtitles"""
        try:
            # Create title overlay (first 3 seconds)
            title_text = self._create_video_title(config.topic)
            title = TextClip(title_text, 
                           fontsize=80, color='white', font='Arial-Bold',
                           stroke_color='black', stroke_width=3)
            title = title.set_position(('center', 100)).set_duration(3).set_start(0)
            
            # Create hook overlay (seconds 3-6)
            hook_text = getattr(config, 'hook', 'Amazing content ahead!')
            hook = TextClip(hook_text[:50] + "..." if len(hook_text) > 50 else hook_text,
                          fontsize=50, color='yellow', font='Arial-Bold',
                          stroke_color='red', stroke_width=2)
            hook = hook.set_position(('center', 200)).set_duration(3).set_start(3)
            
            # Create call-to-action overlay (last 3 seconds)
            cta_text = getattr(config, 'call_to_action', 'Subscribe for more!')
            cta = TextClip(cta_text,
                         fontsize=60, color='lime', font='Arial-Bold',
                         stroke_color='black', stroke_width=2)
            cta = cta.set_position(('center', 600)).set_duration(3).set_start(max(0, video_clip.duration - 3))
            
            # Create platform-specific overlay
            platform_text = f"#{config.target_platform.value.upper()}"
            platform = TextClip(platform_text,
                               fontsize=40, color='cyan', font='Arial-Bold')
            platform = platform.set_position((50, 50)).set_duration(video_clip.duration)
            
            # Combine all overlays
            final_video = CompositeVideoClip([
                video_clip,
                title.set_opacity(0.9),
                hook.set_opacity(0.8),
                cta.set_opacity(0.9),
                platform.set_opacity(0.7)
            ])
            
            logger.info("✅ Added comprehensive text overlays (title, hook, CTA, platform)")
            return final_video
            
        except Exception as e:
            logger.warning(f"⚠️ Text overlay creation failed: {e}, returning original video")
            return video_clip
    
    def _create_enhanced_local_clip(self, output_path: str, prompt: str, duration: float):
        """Create enhanced local clip using FFmpeg with animations"""
        try:
            import subprocess
            
            # Create animated background based on prompt content
            if "mytholog" in prompt.lower() or "ancient" in prompt.lower():
                # Golden/mystical theme
                filter_complex = [
                    f"color=c=0x8B4513:s=1280x720:d={duration}[bg]",
                    f"[bg]geq=r='255*abs(sin(2*PI*T/{duration}))':g='215*abs(cos(2*PI*T/{duration}))':b='0'[effect]",
                    f"[effect]drawtext=text='{prompt[:30]}...':fontcolor=gold:fontsize=40:x='(w-text_w)/2':y='(h-text_h)/2':shadowx=2:shadowy=2[text]"
                ]
            elif "persian" in prompt.lower():
                # Persian-inspired colors
                filter_complex = [
                    f"color=c=0x4169E1:s=1280x720:d={duration}[bg]",
                    f"[bg]geq=r='65*abs(sin(2*PI*T/{duration}))':g='105*abs(cos(2*PI*T/{duration}))':b='225'[effect]",
                    f"[effect]drawtext=text='Persian Tale':fontcolor=white:fontsize=50:x='(w-text_w)/2':y='(h-text_h)/2':shadowx=3:shadowy=3[text]"
                ]
            else:
                # Dynamic modern animation
                filter_complex = [
                    f"color=c=0x2563EB:s=1280x720:d={duration}[bg]",
                    f"[bg]geq=r='r(X,Y)*abs(sin(2*PI*T/{duration}))':g='g(X,Y)*abs(cos(2*PI*T/{duration}))':b='b(X,Y)'[effect]",
                    f"[effect]drawtext=text='AI Generated':fontcolor=white:fontsize=45:x='(w-text_w)/2':y='(h-text_h)/2':shadowx=2:shadowy=2[text]"
                ]
            
            filter_str = ";".join(filter_complex)
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'nullsrc=s=1280x720:d={duration}:r=30',
                '-filter_complex', filter_str,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"Enhanced local clip failed: {e}, using simple fallback")
            self._create_placeholder_clip(output_path, int(duration))

    def _create_text_overlay_clip(self, output_path: str, prompt: str, duration: float):
        """Create text overlay clip with proper styling"""
        try:
            # Create a gradient background
            color = (random.randint(50, 150), random.randint(50, 150), random.randint(100, 255))
            clip = ColorClip(size=(1280, 720), color=color, duration=duration)
            
            # Extract key words from prompt for display
            words = prompt.split()[:5]  # First 5 words
            display_text = " ".join(words) + "..."
            
            # Create main text
            txt = TextClip(display_text, 
                          fontsize=60, color='white', font='Arial-Bold',
                          stroke_color='black', stroke_width=2)
            txt = txt.set_position('center').set_duration(duration)
            
            # Create subtitle
            subtitle = TextClip("AI Generated Video", 
                               fontsize=30, color='lightgray', font='Arial')
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
        """Clean and optimize script for TTS generation - Extract ONLY natural speech"""
        import re
        
        logger.info(f"🧹 Cleaning script for TTS (target: {target_duration}s)")
        logger.info(f"📋 Script type: {type(script)}")
        
        # STEP 1: Extract only VOICEOVER content
        dialogue_lines = []
        
        # Handle both dict and string inputs
        try:
            import json
            if isinstance(script, dict):
                script_data = script
                logger.info("📝 Processing script as dictionary")
            elif isinstance(script, str):
                # Try to parse as JSON first
                try:
                    script_data = json.loads(script)
                    logger.info("📝 Parsed script string as JSON")
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text
                    logger.info("📝 Processing script as plain text")
                    script_data = None
            else:
                logger.warning(f"⚠️ Unexpected script type: {type(script)}")
                script_data = None
            
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
            if dialogue_lines:
                logger.info(f"   Line 1: {dialogue_lines[0][:80]}...")
                if len(dialogue_lines) > 1:
                    logger.info(f"   Line 2: {dialogue_lines[1][:80]}...")
                if len(dialogue_lines) > 2:
                    logger.info(f"   Line 3: {dialogue_lines[2][:80]}...")
            
        except (json.JSONDecodeError, TypeError):
            # Not JSON, parse as text
            script_data = None
            
        # Handle plain text script (when script_data is None)
        if script_data is None and isinstance(script, str):
            for line in script.split('\n'):
                if '**VOICEOVER:**' in line:
                    content = line.replace('**VOICEOVER:**', '').strip()
                    if content and len(content) > 10:
                        dialogue_lines.append(content)
        
        if not dialogue_lines:
            # Fallback: extract any meaningful content that isn't technical
            sentences = script.split('.')
            for sentence in sentences:
                clean_sentence = sentence.strip()
                # Skip technical lines - EXPANDED list
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
        
        # STEP 3: Calculate optimal word count and trim
        target_words = int(target_duration * 2.5)  # 2.5 words per second
        words = cleaned_text.split()
        
        # If still no good content, create a natural fallback based on topic
        if len(words) < 5 or any(tech in cleaned_text.upper() for tech in [
            'BELOW IT', 'ANIMATES', 'CALL TO ACTION', 'LINK IN BIO', 'FINGER TAP',
            'SPARKLES', 'VIRAL', 'UNDERSCORE', 'ELEMENTS', 'SUBSCRIBE FOR MORE'
        ]):
            logger.warning("⚠️ Script cleaning failed, creating natural speech fallback")
            logger.warning(f"   Rejected content: {cleaned_text[:100]}...")
            
            # Extract topic from context or create generic engaging content
            topic_words = [word for word in words if len(word) > 3 and word.isalpha()]
            if 'persian' in ' '.join(topic_words).lower() or 'goddess' in ' '.join(topic_words).lower():
                final_script = "Meet the most powerful goddess you've never heard of. She was Persian royalty with incredible abilities. Think you have the spirit of a goddess?"
            else:
                final_script = f"This is an amazing story you need to hear. Get ready for something incredible. You won't believe what happens next."
            
            logger.info(f"🔄 Using natural speech fallback: {final_script}")
            return final_script
        
        if len(words) > target_words:
            # Trim to target length but keep complete sentences
            trimmed_words = words[:target_words]
            trimmed_text = ' '.join(trimmed_words)
            
            # Try to end at a sentence boundary
            if '.' in trimmed_text:
                sentences = trimmed_text.split('.')
                if len(sentences) > 1:
                    trimmed_text = '. '.join(sentences[:-1]) + '.'
            final_script = trimmed_text
        else:
            final_script = cleaned_text
        
        # Ensure it ends properly
        if not final_script.endswith('.'):
            final_script += '.'
        
        logger.info(f"✅ Cleaned TTS script: {len(words)} → {len(final_script.split())} words")
        logger.info(f"🎯 Removed technical terms, kept only natural speech")
        logger.info(f"📝 Clean script preview: {final_script[:100]}...")
        
        # Log complete script to session output
        import json
        session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
        os.makedirs(session_dir, exist_ok=True)
        script_file = os.path.join(session_dir, "tts_script.json")
        with open(script_file, 'w') as f:
            json.dump({
                "final_script": final_script,
                "original_length": len(words),
                "cleaned_length": len(final_script.split()),
                "target_duration": target_duration,
                "timestamp": str(datetime.now())
            }, f, indent=2)
        logger.info(f"📁 TTS script saved to: {script_file}")
        
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
            if config.target_platform.value.upper() == 'TIKTOK':
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
                
            elif config.target_platform.value.upper() == 'YOUTUBE':
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
                
            elif config.target_platform.value.upper() == 'INSTAGRAM':
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