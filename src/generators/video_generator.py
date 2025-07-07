"""
Video generator using AI and video editing libraries with REAL VEO-2 integration
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
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

class VideoGenerator:
    """
    Main video generator class with REAL VEO-2 video generation
    """
    
    def __init__(self, api_key: str, use_vertex_ai: bool = True, project_id: Optional[str] = None, 
                 location: Optional[str] = None, use_real_veo2: bool = True, session_id: Optional[str] = None):
        self.api_key = api_key
        self.use_vertex_ai = use_vertex_ai
        self.project_id = project_id or "viralgen-464411"
        self.location = location or "us-central1"
        self.use_real_veo2 = use_real_veo2
        
        # Initialize session - use provided session_id or generate one
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.output_dir = "outputs"
        self.clips_dir = os.path.join(self.output_dir, "clips")
        os.makedirs(self.clips_dir, exist_ok=True)
        
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
        if use_real_veo2 and use_vertex_ai:
            try:
                from .veo_client import VeoApiClient
                self.veo_client = VeoApiClient(
                    project_id=self.project_id,
                    location=self.location
                )
                logger.info(f"🎬 VEO-2 Client initialized for project: {self.project_id}")
            except Exception as e:
                logger.warning(f"VEO-2 client initialization failed: {e}")
                self.veo_client = None
        else:
            self.veo_client = None
        
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
            
            # Extract text from script data
            if isinstance(script_data, dict):
                script = script_data.get('text', str(script_data))
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
        """Generate REAL VEO-2 video clips based on the script and configuration"""
        try:
            clips = []
            
            if self.use_real_veo2 and self.veo_client:
                logger.info("🎬 Generating REAL VEO-2 video clips")
                
                # Create VEO-2 prompts based on the topic and script
                veo_prompts = self._create_veo2_prompts(config, script)
                
                for i, prompt in enumerate(veo_prompts):
                    logger.info(f"🎬 Generating VEO-2 clip {i+1}/{len(veo_prompts)}: {prompt[:100]}...")
                    
                    try:
                        # Generate video with VEO-2
                        video_uri = self.veo_client.generate_video(
                            prompt=prompt,
                            output_folder=f"session_{self.session_id}"
                        )
                        
                        if video_uri:
                            # Download the video from GCS
                            local_path = self._download_veo2_video(video_uri, i)
                            clips.append(local_path)
                            logger.info(f"✅ VEO-2 clip {i+1} generated: {local_path}")
                        else:
                            logger.warning(f"❌ VEO-2 clip {i+1} failed, using fallback")
                            # Create fallback clip in session directory
                            session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
                            os.makedirs(session_dir, exist_ok=True)
                            fallback_path = os.path.join(session_dir, f"fallback_clip_{i}_{self.session_id}.mp4")
                            self._create_placeholder_clip(fallback_path, 8)
                            clips.append(fallback_path)
                            
                    except Exception as e:
                        logger.error(f"❌ VEO-2 generation failed for clip {i+1}: {e}")
                        # Create fallback clip in session directory
                        session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
                        os.makedirs(session_dir, exist_ok=True)
                        fallback_path = os.path.join(session_dir, f"fallback_clip_{i}_{self.session_id}.mp4")
                        self._create_placeholder_clip(fallback_path, 8)
                        clips.append(fallback_path)
            else:
                logger.info("🎬 Generating placeholder clips (VEO-2 disabled)")
                # Fallback to placeholder clips in session directory
                session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
                os.makedirs(session_dir, exist_ok=True)
                num_clips = max(1, config.duration_seconds // 8)
                
                for i in range(num_clips):
                    clip_path = os.path.join(session_dir, f"clip_{i}_{self.session_id}.mp4")
                    self._create_placeholder_clip(clip_path, 8)
                    clips.append(clip_path)
            
            logger.info(f"🎥 Generated {len(clips)} video clips")
            return clips
            
        except Exception as e:
            logger.error(f"❌ Video clip generation failed: {e}")
            raise
    
    def _create_veo2_prompts(self, config: GeneratedVideoConfig, script: str) -> List[str]:
        """Create VEO-2 prompts based on the video configuration and script"""
        topic = config.topic
        style = config.visual_style
        
        # Create prompts that avoid content policy issues while being engaging
        if "unicorn" in topic.lower():
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
        
        # Limit to duration-appropriate number of clips
        num_clips = min(len(prompts), max(1, config.duration_seconds // 8))
        return prompts[:num_clips]
    
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
        
        # Use the advanced voiceover generation with Google Cloud TTS
        config = {
            'narrative': 'energetic',
            'feeling': 'excited',
            'realistic_audio': True,
            'duration_seconds': duration
        }
        
        return self._generate_voiceover(script, duration, config)
    
    def _compose_final_video(self, video_clips: List[str], audio_path: str, 
                           config: GeneratedVideoConfig) -> str:
        """Compose final video from clips and audio"""
        try:
            # Create session directory path
            session_dir = os.path.join(self.output_dir, f"session_{self.session_id}")
            os.makedirs(session_dir, exist_ok=True)
            final_video_path = os.path.join(session_dir, f"final_video_{self.session_id}.mp4")
            
            # Load video clips
            clips = []
            for clip_path in video_clips:
                if os.path.exists(clip_path):
                    clip = VideoFileClip(clip_path)
                    clips.append(clip)
            
            if not clips:
                raise RenderingError("No valid video clips found")
            
            # Concatenate video clips
            video = concatenate_videoclips(clips)
            
            # Load and sync audio
            if os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                # Trim or loop audio to match video duration
                if audio.duration > video.duration:
                    audio = audio.subclip(0, video.duration)
                elif audio.duration < video.duration:
                    # Loop audio if needed
                    loops = int(video.duration / audio.duration) + 1
                    audio = concatenate_audioclips([audio] * loops).subclip(0, video.duration)
                
                video = video.set_audio(audio)
            
            # Write final video
            video.write_videofile(
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
            if 'audio' in locals():
                audio.close()
            video.close()
            
            logger.info(f"🎬 Final video composed: {final_video_path}")
            return final_video_path
            
        except Exception as e:
            logger.error(f"❌ Video composition failed: {e}")
            raise RenderingError("video_composition", f"Video composition failed: {str(e)}")
    
    def _create_placeholder_clip(self, output_path: str, duration: int):
        """Create a placeholder video clip"""
        try:
            # Create a simple colored clip
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            clip = ColorClip(size=(1080, 1920), color=color, duration=duration)
            
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

    def _clean_script_for_tts(self, script: str, target_duration: int) -> str:
        """Clean and optimize script for TTS generation - Remove ALL technical terms"""
        import re
        
        logger.info(f"🧹 Cleaning script for TTS (target: {target_duration}s)")
        
        # STEP 1: Extract only VOICEOVER content
        dialogue_lines = []
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
                # Skip technical lines
                if not any(skip in clean_sentence.upper() for skip in [
                    'HOOK', 'TEXT', 'TYPE', 'SHOCK', 'VISUAL', 'SOUND', 'SFX', 
                    'MUSIC', 'CUT', 'FADE', 'ZOOM', 'TRANSITION', 'OVERLAY',
                    'DURATION', 'TIMING', 'POSITION', 'STYLE', 'FONT', 'COLOR'
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