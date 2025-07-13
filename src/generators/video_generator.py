"""
Video Generator - Main video generation orchestrator
Coordinates video generation using VEO2/VEO3, Gemini images, and TTS
"""

import os
import time
import tempfile
import uuid
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json

from ..models.video_models import GeneratedVideoConfig, GeneratedVideo, Platform, VideoCategory
from ..utils.logging_config import get_logger
from ..generators.veo_client_factory import VeoClientFactory, VeoModel, get_best_veo_client
from ..generators.gemini_image_client import GeminiImageClient
from ..generators.enhanced_multilang_tts import EnhancedMultilingualTTS
from ..generators.enhanced_script_processor import EnhancedScriptProcessor
from ..agents.voice_director_agent import VoiceDirectorAgent
from ..agents.overlay_positioning_agent import OverlayPositioningAgent
from ..agents.visual_style_agent import VisualStyleAgent
from ..utils.session_manager import session_manager
from ..utils.session_context import SessionContext, create_session_context

logger = get_logger(__name__)


@dataclass
class VideoGenerationResult:
    """Result of video generation process"""
    file_path: str
    file_size_mb: float
    generation_time_seconds: float
    script: str
    clips_generated: int
    audio_files: List[str]
    success: bool
    error_message: Optional[str] = None


class VideoGenerator:
    """Main video generator that orchestrates all AI agents and generation components"""
    
    def __init__(self, api_key: str, use_real_veo2: bool = True, use_vertex_ai: bool = True,
                 vertex_project_id: Optional[str] = None, vertex_location: Optional[str] = None, 
                 vertex_gcs_bucket: Optional[str] = None, output_dir: Optional[str] = None,
                 prefer_veo3: bool = False):
        """
        Initialize video generator with all AI components
        
        Args:
            api_key: Google AI API key
            use_real_veo2: Whether to use VEO for video generation
            use_vertex_ai: Whether to use Vertex AI or Google AI Studio
            vertex_project_id: Vertex AI project ID
            vertex_location: Vertex AI location
            vertex_gcs_bucket: GCS bucket for Vertex AI results
            output_dir: Output directory for generated content
            prefer_veo3: Whether to prefer VEO-3 over VEO-2
        """
        self.api_key = api_key
        self.use_real_veo2 = use_real_veo2
        self.use_vertex_ai = use_vertex_ai
        self.prefer_veo3 = prefer_veo3
        
        # Set output directory (fallback only)
        self.output_dir = output_dir or "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize VEO client factory
        self.veo_factory = VeoClientFactory(
            project_id=vertex_project_id,
            location=vertex_location,
            gcs_bucket=vertex_gcs_bucket
        )
        
        # Initialize AI agents
        self.voice_director = VoiceDirectorAgent(api_key)
        self.positioning_agent = OverlayPositioningAgent(api_key)
        self.style_agent = VisualStyleAgent(api_key)
        self.script_processor = EnhancedScriptProcessor(api_key)
        
        # Initialize other clients
        self.image_client = GeminiImageClient(api_key, self.output_dir)
        self.tts_client = EnhancedMultilingualTTS(api_key)
        
        # Check available VEO models
        available_models = self.veo_factory.get_available_models()
        
        logger.info(f"🎬 VideoGenerator initialized with clean OOP architecture")
        logger.info(f"   VEO Models: {[m.value for m in available_models]}")
        logger.info(f"   Prefer VEO-3: {'✅' if prefer_veo3 else '❌'}")
        logger.info(f"   Vertex AI: {'✅' if use_vertex_ai else '❌'}")
        logger.info(f"   AI Agents: ✅ (Voice, Positioning, Style, Script)")
        logger.info(f"   Session-aware: ✅ (Files will be organized in session directories)")
        
        # Log authentication status
        if available_models:
            logger.info(f"🔐 Authentication: ✅ SUCCESS")
        else:
            logger.warning(f"🔐 Authentication: ⚠️ No VEO models available")
    
    def generate_video(self, config: GeneratedVideoConfig) -> Union[str, VideoGenerationResult]:
        """
        Generate video using AI agents and generation clients
        
        Args:
            config: Video generation configuration
            
        Returns:
            Video file path or VideoGenerationResult object
        """
        start_time = time.time()
        
        from ..utils.session_manager import session_manager
        
        # Create session for this generation
        session_id = session_manager.create_session(
            topic=config.topic,
            platform=config.target_platform.value,
            duration=config.duration_seconds,
            category=config.category.value
        )
        
        # Create session context for this generation
        session_context = create_session_context(session_id)
        
        logger.info(f"🎬 Starting video generation for: {config.topic}")
        logger.info(f"   Duration: {config.duration_seconds}s")
        logger.info(f"   Platform: {config.target_platform.value}")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Session Directory: {session_context.get_output_path('')}")
        
        session_manager.log_generation_step("video_generation_started", "in_progress", {
            "topic": config.topic,
            "platform": config.target_platform.value,
            "duration": config.duration_seconds
        })
        
        try:
            # Initialize VEO client with session context
            if self.use_real_veo2 and self.use_vertex_ai:
                self.veo_client = self.veo_factory.get_veo_client(
                    model=VeoModel.VEO2 if not self.prefer_veo3 else VeoModel.VEO3,
                    output_dir=session_context.get_output_path("video_clips")
                )
            
            # Step 1: Process script with AI
            script_result = self._process_script_with_ai(config, session_context)
            
            # Store script result for subtitle generation
            self._last_script_result = script_result
            
            # Step 2: Get AI decisions for visual style and positioning
            style_decision = self._get_visual_style_decision(config)
            positioning_decision = self._get_positioning_decision(config, style_decision)
            
            # Step 3: Generate video clips
            clips = self._generate_video_clips(config, script_result, style_decision, session_context)
            
            # Step 4: Generate audio with AI voice selection
            audio_files = self._generate_ai_optimized_audio(config, script_result, session_context)
            
            # Step 5: Compose final video using session context
            final_video_path = self._compose_final_video(clips, audio_files, config, session_context)
            
            generation_time = time.time() - start_time
            
            logger.info(f"✅ Video generation completed in {generation_time:.1f}s")
            logger.info(f"📁 Output: {final_video_path}")
            
            # Log session summary
            summary = session_context.get_session_summary()
            logger.info(f"📊 Session Summary: {summary['file_counts']}")
            
            # Return VideoGenerationResult for compatibility
            result = VideoGenerationResult(
                file_path=final_video_path,
                file_size_mb=self._get_file_size_mb(final_video_path),
                generation_time_seconds=generation_time,
                script=script_result.get('final_script', config.topic),
                clips_generated=len(clips),
                audio_files=audio_files,
                success=True
            )
            
            # For backward compatibility, some callers expect just the path
            return final_video_path
            
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"❌ Video generation failed after {generation_time:.1f}s: {e}")
            
            # Return error result
            result = VideoGenerationResult(
                file_path="",
                file_size_mb=0.0,
                generation_time_seconds=generation_time,
                script="",
                clips_generated=0,
                audio_files=[],
                success=False,
                error_message=str(e)
            )
            
            # For backward compatibility, raise exception
            raise Exception(f"Video generation failed: {e}")
    
    def generate_video_config(self, analyses: List[Any], platform: Platform, 
                            category: VideoCategory, topic: Optional[str] = None,
                            user_config: Optional[Dict[str, Any]] = None) -> GeneratedVideoConfig:
        """
        Generate video configuration from trending analyses
        
        Args:
            analyses: List of video analyses
            platform: Target platform
            category: Video category
            topic: Optional topic override
            
        Returns:
            Generated video configuration
        """
        logger.info("📋 Generating video config from trending analyses")
        
        # Extract insights from analyses
        themes = []
        hooks = []
        success_factors = []
        
        for analysis in analyses:
            if hasattr(analysis, 'content_themes'):
                themes.extend(analysis.content_themes[:2])
            if hasattr(analysis, 'viral_hooks'):
                hooks.extend(analysis.viral_hooks[:1])
            if hasattr(analysis, 'success_factors'):
                success_factors.extend(analysis.success_factors[:2])
        
        # Generate topic if not provided
        if not topic:
            topic = f"Trending: {themes[0] if themes else 'Viral Content'}"
        
        # Create hook from trending insights
        hook = hooks[0] if hooks else f"You won't believe what's trending with {topic}!"
        
        # Generate main content
        main_content = [
            f"Opening: {topic} is taking over social media",
            f"Main: Here's why {topic} is so popular",
            f"Conclusion: This is just the beginning of {topic}"
        ]
        
        config = GeneratedVideoConfig(
            target_platform=platform,
            category=category,
            duration_seconds=15,  # Default short form
            topic=topic,
            style="viral",
            tone="engaging",
            target_audience=(user_config or {}).get('target_audience', 'general audience'),
            hook=hook,
            main_content=main_content,
            call_to_action="Follow for more trending content!",
            visual_style="dynamic",
            color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
            text_overlays=[],
            transitions=["fade", "zoom"],
            background_music_style="upbeat",
            voiceover_style="energetic",
            sound_effects=[],
            inspired_by_videos=[],
            predicted_viral_score=0.8
        )
        
        logger.info(f"✅ Generated config for: {topic}")
        return config
    
    def _process_script_with_ai(self, config: GeneratedVideoConfig, session_context: SessionContext) -> Dict[str, Any]:
        """Process script using AI script processor"""
        logger.info("📝 Processing script with AI")
        
        # Create script from config
        main_content = config.main_content or []
        script_parts = [config.hook] + main_content + [config.call_to_action]
        script = " ".join(script_parts)
        
        # Process with AI
        from ..models.video_models import Language
        result = self.script_processor.process_script_for_tts(
            script=script,
            language=Language.ENGLISH_US,
            target_duration=config.duration_seconds,
            platform=config.target_platform,
            category=config.category
        )
        
        # ENHANCED: Save ALL script variations to session
        from ..utils.session_manager import session_manager
        
        # Save original script
        session_manager.save_script(script, "original")
        
        # Save processed script
        if result.get('final_script'):
            script_path = session_context.get_output_path("scripts", "processed_script.txt")
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            with open(script_path, 'w') as f:
                f.write(result['final_script'])
            
            # Track with session manager
            session_manager.track_file(script_path, "script", "EnhancedScriptProcessor")
            session_manager.save_script(result['final_script'], "processed")
            
            logger.info(f"💾 Saved processed script to session")
        
        # Save TTS-ready script if different
        if result.get('tts_ready_script') and result['tts_ready_script'] != result.get('final_script'):
            session_manager.save_script(result['tts_ready_script'], "tts_ready")
        
        # Save full processing result
        session_manager.save_script(result, "processing_result")
        
        logger.info(f"✅ Script processed: {result.get('word_count', 0)} words")
        return result
    
    def _get_visual_style_decision(self, config: GeneratedVideoConfig) -> Dict[str, Any]:
        """Get AI decision for visual style"""
        logger.info("🎨 Getting AI visual style decision")
        
        style_decision = self.style_agent.analyze_optimal_style(
            topic=config.topic,
            target_audience=config.target_audience,
            platform=config.target_platform.value,
            content_type=config.category.value.lower(),
            humor_level="medium"
        )
        
        logger.info(f"✅ Style decision: {style_decision.get('primary_style', 'dynamic')}")
        return style_decision
    
    def _get_positioning_decision(self, config: GeneratedVideoConfig, 
                                style_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI decision for subtitle positioning"""
        logger.info("🎯 Getting AI positioning decision")
        
        positioning_decision = self.positioning_agent.analyze_optimal_positioning(
            topic=config.topic,
            video_style=style_decision.get('primary_style', 'dynamic'),
            platform=config.target_platform.value,
            duration=float(config.duration_seconds),
            subtitle_count=4
        )
        
        logger.info(f"✅ Positioning decision: {positioning_decision.get('primary_subtitle_position', 'bottom_third')}")
        return positioning_decision
    
    def _generate_video_clips(self, config: GeneratedVideoConfig, 
                            script_result: Dict[str, Any],
                            style_decision: Dict[str, Any],
                            session_context: SessionContext) -> List[str]:
        """Generate video clips using VEO factory with clean OOP architecture"""
        logger.info("🎬 Generating video clips with VEO factory")
        
        # Check if frame continuity is enabled
        use_frame_continuity = config.frame_continuity
        logger.info(f"🎬 Frame continuity: {'✅ ENABLED' if use_frame_continuity else '❌ DISABLED'}")
        
        clips = []
        num_clips = max(3, config.duration_seconds // 5)
        last_frame_image = None
        
        # Get the best available VEO client using factory
        veo_client = None
        if self.use_real_veo2:
            veo_client = self.veo_factory.get_best_available_client(
                output_dir=session_context.get_output_path("video_clips"),
                prefer_veo3=self.prefer_veo3 and not use_frame_continuity  # Use VEO-2 for frame continuity
            )
            
            if veo_client:
                logger.info(f"🚀 Using {veo_client.get_model_name()} for video generation")
            else:
                logger.warning("⚠️ No VEO clients available, falling back to image generation")
        
        for i in range(num_clips):
            try:
                # Create prompt for this clip
                prompt = f"{config.topic}, {style_decision.get('primary_style', 'dynamic')} style, scene {i+1}"
                
                # Enhance prompt with style
                enhanced_prompt = self.style_agent.enhance_prompt_with_style(
                    base_prompt=prompt,
                    style=style_decision.get('primary_style', 'dynamic')
                )
                
                if veo_client:
                    # Generate with VEO using factory pattern
                    if use_frame_continuity and last_frame_image:
                        clip_path = veo_client.generate_video(
                            prompt=enhanced_prompt,
                            duration=5.0,
                            clip_id=f"clip_{i}",
                            image_path=last_frame_image
                        )
                    else:
                        clip_path = veo_client.generate_video(
                            prompt=enhanced_prompt,
                            duration=5.0,
                            clip_id=f"clip_{i}"
                        )
                    
                    # Track with session manager
                    if clip_path:
                        from ..utils.session_manager import session_manager
                        clip_path = session_manager.track_file(clip_path, "video_clip", veo_client.get_model_name())
                    
                    # Extract last frame for next clip if frame continuity is enabled
                    if use_frame_continuity and clip_path and os.path.exists(clip_path):
                        try:
                            last_frame_image = self._extract_last_frame(clip_path, f"clip_{i}")
                            if last_frame_image:
                                # Track the extracted frame
                                session_manager.track_file(last_frame_image, "image", "FrameContinuity")
                                logger.info(f"🖼️ Frame continuity: Extracted frame for next clip")
                        except Exception as frame_error:
                            logger.warning(f"Frame extraction failed (continuing without): {frame_error}")
                            last_frame_image = None
                else:
                    # Generate with Gemini images (fallback)
                    temp_path = f"{tempfile.gettempdir()}/clip_{i}_{uuid.uuid4().hex[:8]}.jpg"
                    clip_path = self.image_client.generate_image(
                        prompt=enhanced_prompt,
                        style=style_decision.get('primary_style', 'dynamic'),
                        output_path=temp_path
                    )
                    
                    # Save to session directory and track
                    if clip_path:
                        from ..utils.session_manager import session_manager
                        clip_path = session_context.save_image(clip_path, f"clip_{i}")
                        clip_path = session_manager.track_file(clip_path, "image", "GeminiImages")
                
                if clip_path:
                    clips.append(clip_path)
                    logger.info(f"✅ Generated clip {i+1}/{num_clips}")
                else:
                    logger.warning(f"⚠️ Failed to generate clip {i+1}")
                    
            except Exception as e:
                logger.error(f"❌ Error generating clip {i+1}: {e}")
                # Continue with other clips
                continue
        
        logger.info(f"🎬 Generated {len(clips)} video clips")
        return clips

    def _extract_last_frame(self, video_path: str, clip_id: str) -> Optional[str]:
        """Extract the last frame from a video for frame continuity"""
        try:
            import subprocess
            
            # Create frame path in session directory
            from ..utils.session_manager import session_manager
            session_dir = session_manager.get_session_path("images")
            frame_path = os.path.join(session_dir, f"last_frame_{clip_id}.jpg")
            
            # Use ffmpeg to extract the last frame
            cmd = [
                'ffmpeg', '-y',
                '-sseof', '-1',  # Seek to 1 second before end
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
    
    def _generate_ai_optimized_audio(self, config: GeneratedVideoConfig,
                                   script_result: Dict[str, Any],
                                   session_context: SessionContext) -> List[str]:
        """Generate audio using AI voice selection"""
        logger.info("🎤 Generating AI-optimized audio")
        
        try:
            from ..models.video_models import Language
            
            audio_files = self.tts_client.generate_intelligent_voice_audio(
                script=script_result.get('final_script', config.topic),
                language=Language.ENGLISH_US,
                topic=config.topic,
                platform=config.target_platform,
                category=config.category,
                duration_seconds=config.duration_seconds,
                num_clips=4
            )
            
            # ENHANCED: Save ALL audio files to session directory with comprehensive tracking
            from ..utils.session_manager import session_manager
            session_audio_files = []
            
            for i, audio_file in enumerate(audio_files):
                if os.path.exists(audio_file):
                    # Save to session context
                    session_audio_path = session_context.save_audio_file(audio_file, f"segment_{i}")
                    
                    # Track with session manager
                    session_audio_path = session_manager.track_file(session_audio_path, "audio", "TTS")
                    
                    session_audio_files.append(session_audio_path)
                    logger.info(f"💾 Saved and tracked audio segment {i}")
                else:
                    session_audio_files.append(audio_file)
                    logger.warning(f"⚠️ Audio file {i} not found: {audio_file}")
            
            # Save audio generation metadata
            audio_metadata = {
                "total_segments": len(audio_files),
                "successful_segments": len([f for f in session_audio_files if os.path.exists(f)]),
                "script_used": script_result.get('final_script', config.topic)[:200] + "...",
                "generation_timestamp": datetime.now().isoformat(),
                "platform": config.target_platform.value,
                "category": config.category.value
            }
            
            metadata_file = session_context.get_output_path("metadata", "audio_generation.json")
            with open(metadata_file, 'w') as f:
                json.dump(audio_metadata, f, indent=2)
            
            session_manager.track_file(metadata_file, "metadata", "AudioGeneration")
            
            logger.info(f"✅ Generated {len(session_audio_files)} audio files")
            return session_audio_files
            
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            return []
    
    def _compose_final_video(self, clips: List[str], audio_files: List[str], 
                           config: GeneratedVideoConfig, session_context: SessionContext) -> str:
        """Compose final video with proper frame continuity handling"""
        logger.info("🎞️ Composing final video")
        
        try:
            import subprocess
            import tempfile
            
            # Create temporary video path
            temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_video_path = temp_video.name
            temp_video.close()
            
            # Check if frame continuity is enabled
            use_frame_continuity = config.frame_continuity
            
            if use_frame_continuity:
                logger.info("🎬 Composing with frame continuity (removing overlapping frames)")
                base_video_path = self._compose_with_frame_continuity(
                    clips, audio_files, temp_video_path, session_context
                )
            else:
                logger.info("🎬 Composing with standard cuts")
                base_video_path = self._compose_with_standard_cuts(
                    clips, audio_files, temp_video_path, session_context
                )
            
            # Add subtitle overlays if enabled
            if config.use_subtitle_overlays and base_video_path:
                logger.info("📝 Adding subtitle overlays to final video")
                base_video_path = self._add_subtitle_overlays(
                    base_video_path, config, session_context
                )
            
            # Save to session directory
            saved_path = session_context.save_final_video(base_video_path)
            
            return saved_path
            
        except Exception as e:
            logger.error(f"❌ Video composition failed: {e}")
            return ""

    def _add_subtitle_overlays(self, video_path: str, config: GeneratedVideoConfig, 
                             session_context: SessionContext) -> str:
        """Add subtitle overlays to the video using MoviePy"""
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            import tempfile
            
            logger.info("📝 Adding subtitle overlays using MoviePy")
            
            # Load the video
            video = VideoFileClip(video_path)
            video_duration = video.duration
            video_width, video_height = video.size
            
            # Create subtitle content based on the actual processed script
            subtitle_segments = self._create_subtitle_segments(
                config, video_duration, 
                script_result=getattr(self, '_last_script_result', None),
                session_context=session_context
            )
            
            # Get positioning decision
            positioning_decision = self._get_positioning_decision(config, {'primary_style': 'dynamic'})
            primary_position = positioning_decision.get('primary_subtitle_position', 'bottom_third')
            
            # Create text clips for subtitles
            text_clips = []
            for i, segment in enumerate(subtitle_segments):
                try:
                    text = segment['text']
                    start_time = segment['start']
                    end_time = segment['end']
                    
                    if end_time <= start_time:
                        continue
                    
                    # Calculate position based on AI decision
                    if primary_position == 'top_third':
                        y_pos = video_height * 0.15
                    elif primary_position == 'center':
                        y_pos = video_height * 0.5
                    else:  # bottom_third (default)
                        y_pos = video_height * 0.85
                    
                    # Font size based on video dimensions
                    font_size = max(40, int(video_width * 0.05))
                    
                    # Create text clip with modern styling
                    text_clip = TextClip(
                        text,
                        fontsize=font_size,
                        color='white',
                        font='Arial-Bold',
                        stroke_color='black',
                        stroke_width=2,
                        method='caption',
                        size=(int(video_width * 0.9), None),
                        align='center'
                    )
                    
                    # Position and time the text clip
                    text_clip = text_clip.set_position(('center', y_pos)).set_start(start_time).set_duration(end_time - start_time)
                    text_clips.append(text_clip)
                    
                    logger.info(f"📝 Added subtitle: '{text[:30]}...' at {start_time:.1f}-{end_time:.1f}s")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create subtitle clip {i}: {e}")
                    continue
            
            # Composite video with subtitle overlays
            if text_clips:
                logger.info(f"🎬 Compositing video with {len(text_clips)} subtitle overlays")
                final_video = CompositeVideoClip([video] + text_clips)
                
                # Create output path
                temp_output = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                output_path = temp_output.name
                temp_output.close()
                
                # Render the video with subtitles
                final_video.write_videofile(
                    output_path,
                    fps=30,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                
                # Clean up
                final_video.close()
                video.close()
                for clip in text_clips:
                    clip.close()
                
                # Verify output
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    logger.info(f"✅ Subtitle overlays added: {output_path} ({file_size:.1f}MB)")
                    
                    # Clean up original video
                    try:
                        os.remove(video_path)
                    except:
                        pass
                    
                    return output_path
                else:
                    logger.error("❌ Failed to create video with subtitles")
                    return video_path
            else:
                logger.warning("⚠️ No subtitle overlays created")
                video.close()
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Subtitle overlay creation failed: {e}")
            return video_path
    
    def _create_subtitle_segments(self, config: GeneratedVideoConfig, video_duration: float, 
                                 script_result: Dict[str, Any] = None, 
                                 session_context: SessionContext = None) -> List[Dict[str, Any]]:
        """Create subtitle segments from the actual processed script content with proper audio synchronization"""
        try:
            # CRITICAL FIX: Use actual processed script content instead of config content
            actual_script = ""
            
            # Priority 1: Use final processed script from script_result
            if script_result and script_result.get('final_script'):
                actual_script = script_result['final_script']
                logger.info("📝 Using processed script for subtitles")
            
            # Priority 2: Try to load from session context
            elif session_context:
                try:
                    script_path = session_context.get_output_path("scripts", "processed_script.txt")
                    if os.path.exists(script_path):
                        with open(script_path, 'r') as f:
                            actual_script = f.read().strip()
                        logger.info("📝 Loaded script from session for subtitles")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load script from session: {e}")
            
            # Priority 3: Fallback to config content (old behavior)
            if not actual_script:
                main_content = config.main_content or [config.topic]
                hook = config.hook or "Amazing content!"
                cta = config.call_to_action or "Follow for more!"
                actual_script = f"{hook} {' '.join(main_content)} {cta}"
                logger.warning("⚠️ Using fallback config content for subtitles")
            
            # Parse the actual script into meaningful segments
            segments = self._parse_script_into_segments(actual_script, video_duration)
            
            # Analyze audio files for better synchronization if available
            if session_context:
                segments = self._synchronize_with_audio_segments(segments, video_duration, session_context)
            
            logger.info(f"📝 Created {len(segments)} subtitle segments from actual script")
            for i, segment in enumerate(segments[:3]):  # Log first 3 segments
                logger.info(f"   Segment {i+1}: '{segment['text'][:50]}...' ({segment['start']:.1f}-{segment['end']:.1f}s)")
            
            return segments
            
        except Exception as e:
            logger.error(f"❌ Failed to create subtitle segments: {e}")
            return []
    
    def _parse_script_into_segments(self, script: str, video_duration: float) -> List[Dict[str, Any]]:
        """Parse script into natural segments based on sentences and timing"""
        try:
            # Split script into sentences
            import re
            sentences = re.split(r'[.!?]+', script)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return []
            
            # Calculate timing based on sentence complexity and length
            segments = []
            total_words = sum(len(sentence.split()) for sentence in sentences)
            
            # Estimate words per second (typical speech rate: 2-3 words/second)
            words_per_second = max(2.0, min(3.0, total_words / video_duration))
            
            current_time = 0.0
            
            for i, sentence in enumerate(sentences):
                words = len(sentence.split())
                
                # Calculate duration based on word count and complexity
                base_duration = words / words_per_second
                
                # Add padding for complex sentences or important content
                if any(keyword in sentence.lower() for keyword in ['meet', 'how', 'what', 'why', 'when', 'where']):
                    base_duration *= 1.2  # 20% longer for questions/introductions
                
                # Ensure minimum and maximum duration per segment
                duration = max(1.5, min(6.0, base_duration))
                
                # Adjust if we're running out of time
                remaining_time = video_duration - current_time
                if i == len(sentences) - 1:  # Last segment
                    duration = min(duration, remaining_time)
                elif current_time + duration > video_duration:
                    duration = remaining_time * 0.8  # Leave some buffer
                
                segments.append({
                    'text': sentence.strip(),
                    'start': current_time,
                    'end': current_time + duration,
                    'word_count': words,
                    'estimated_duration': duration
                })
                
                current_time += duration
                
                # Stop if we've reached the video duration
                if current_time >= video_duration:
                    break
            
            return segments
            
        except Exception as e:
            logger.error(f"❌ Failed to parse script into segments: {e}")
            return []
    
    def _synchronize_with_audio_segments(self, segments: List[Dict[str, Any]], 
                                       video_duration: float, 
                                       session_context: SessionContext) -> List[Dict[str, Any]]:
        """Synchronize subtitle segments with actual audio file durations"""
        try:
            # Get audio files from session
            audio_dir = session_context.get_output_path("audio")
            if not os.path.exists(audio_dir):
                logger.warning("⚠️ No audio directory found, skipping audio synchronization")
                return segments
            
            # Find audio files
            audio_files = []
            for filename in os.listdir(audio_dir):
                if filename.endswith('.mp3') or filename.endswith('.wav'):
                    audio_files.append(os.path.join(audio_dir, filename))
            
            if not audio_files:
                logger.warning("⚠️ No audio files found, skipping audio synchronization")
                return segments
            
            # Sort audio files by segment number
            audio_files.sort(key=lambda x: int(re.search(r'segment_(\d+)', x).group(1)) if re.search(r'segment_(\d+)', x) else 0)
            
            logger.info(f"🎵 Found {len(audio_files)} audio files for synchronization")
            
            # Analyze audio file durations
            try:
                from moviepy.editor import AudioFileClip
                
                audio_durations = []
                for audio_file in audio_files:
                    try:
                        audio_clip = AudioFileClip(audio_file)
                        duration = audio_clip.duration
                        audio_durations.append(duration)
                        audio_clip.close()
                        logger.info(f"🎵 Audio segment: {os.path.basename(audio_file)} - {duration:.2f}s")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to analyze audio file {audio_file}: {e}")
                        continue
                
                # Synchronize segments with audio durations
                if audio_durations and len(segments) > 0:
                    synchronized_segments = []
                    current_time = 0.0
                    
                    # Match segments with audio durations
                    for i, segment in enumerate(segments):
                        if i < len(audio_durations):
                            # Use actual audio duration
                            audio_duration = audio_durations[i]
                            
                            synchronized_segments.append({
                                'text': segment['text'],
                                'start': current_time,
                                'end': current_time + audio_duration,
                                'word_count': segment.get('word_count', 0),
                                'estimated_duration': audio_duration,
                                'audio_synchronized': True
                            })
                            
                            current_time += audio_duration
                        else:
                            # No corresponding audio file, use estimated timing
                            duration = min(segment['estimated_duration'], video_duration - current_time)
                            synchronized_segments.append({
                                'text': segment['text'],
                                'start': current_time,
                                'end': current_time + duration,
                                'word_count': segment.get('word_count', 0),
                                'estimated_duration': duration,
                                'audio_synchronized': False
                            })
                            current_time += duration
                        
                        # Stop if we exceed video duration
                        if current_time >= video_duration:
                            break
                    
                    logger.info(f"✅ Successfully synchronized {len(synchronized_segments)} segments with audio")
                    return synchronized_segments
                
            except ImportError:
                logger.warning("⚠️ MoviePy not available for audio analysis, using estimated timing")
            except Exception as e:
                logger.warning(f"⚠️ Audio synchronization failed: {e}")
            
            return segments
            
        except Exception as e:
            logger.error(f"❌ Audio synchronization error: {e}")
            return segments
    
    def _compose_with_frame_continuity(self, clips: List[str], audio_files: List[str], 
                                     output_path: str, session_context: SessionContext) -> str:
        """Compose video with frame continuity - remove first frame of each clip (except first)"""
        try:
            import subprocess
            
            # Create filter complex for frame continuity
            filter_parts = []
            input_parts = []
            
            # Add all video inputs
            for i, clip in enumerate(clips):
                input_parts.extend(['-i', clip])
            
            # Add all audio inputs
            for i, audio in enumerate(audio_files):
                input_parts.extend(['-i', audio])
            
            # Create video filter for frame continuity
            # For clips after the first, skip the first frame to avoid duplication
            video_filters = []
            
            for i, clip in enumerate(clips):
                if i == 0:
                    # First clip: use as-is
                    video_filters.append(f"[{i}:v]")
                else:
                    # Subsequent clips: remove first frame (skip first 1/30 second)
                    video_filters.append(f"[{i}:v]trim=start=0.033[v{i}]")
            
            # Concatenate all video streams
            if len(video_filters) > 1:
                concat_inputs = "".join([f"[v{i}]" if i > 0 else f"[{i}:v]" for i in range(len(clips))])
                video_filter = f"{';'.join([f for f in video_filters if 'trim' in f])};{concat_inputs}concat=n={len(clips)}:v=1:a=0[outv]"
            else:
                video_filter = f"[0:v]copy[outv]"
            
            # Create audio filter (concatenate all audio)
            audio_inputs = "".join([f"[{len(clips)+i}:a]" for i in range(len(audio_files))])
            audio_filter = f"{audio_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]"
            
            # Combine filters
            filter_complex = f"{video_filter};{audio_filter}"
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg', '-y'
            ] + input_parts + [
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
            
            logger.info("🎬 Running frame continuity composition...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Frame continuity composition completed")
                return output_path
            else:
                logger.error(f"❌ Frame continuity composition failed: {result.stderr}")
                # Fallback to standard composition
                return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context)
                
        except Exception as e:
            logger.error(f"❌ Frame continuity composition error: {e}")
            # Fallback to standard composition
            return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context)

    def _compose_with_standard_cuts(self, clips: List[str], audio_files: List[str], 
                                  output_path: str, session_context: SessionContext) -> str:
        """Compose video with standard cuts (no frame continuity)"""
        try:
            import subprocess
            
            # Create simple concatenation
            input_parts = []
            
            # Add all video inputs
            for clip in clips:
                input_parts.extend(['-i', clip])
            
            # Add all audio inputs
            for audio in audio_files:
                input_parts.extend(['-i', audio])
            
            # Create filter for standard concatenation
            video_inputs = "".join([f"[{i}:v]" for i in range(len(clips))])
            audio_inputs = "".join([f"[{len(clips)+i}:a]" for i in range(len(audio_files))])
            
            filter_complex = f"{video_inputs}concat=n={len(clips)}:v=1:a=0[outv];{audio_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]"
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg', '-y'
            ] + input_parts + [
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
            
            logger.info("🎬 Running standard composition...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Standard composition completed")
                return output_path
            else:
                logger.error(f"❌ Standard composition failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Standard composition error: {e}")
            return ""
    
    def _create_video_placeholder(self, config: GeneratedVideoConfig, 
                                clips: List[str], audio_files: List[str]) -> str:
        """Create comprehensive video placeholder content"""
        content = f"""# AI Video Generator - Video Placeholder

## Video Information
- Topic: {config.topic}
- Duration: {config.duration_seconds} seconds
- Platform: {config.target_platform.value}
- Category: {config.category.value}
- Style: {config.style}
- Tone: {config.tone}
- Target Audience: {config.target_audience}

## Generation Details
- Generated: {datetime.now().isoformat()}
- Clips Generated: {len(clips)}
- Audio Files: {len(audio_files)}

## Content Structure
- Hook: {config.hook}
- Main Content: {config.main_content}
- Call to Action: {config.call_to_action}

## Generated Assets
### Video Clips:
{chr(10).join(f"- {clip}" for clip in clips)}

### Audio Files:
{chr(10).join(f"- {audio}" for audio in audio_files)}

## Visual Style
- Visual Style: {config.visual_style}
- Color Scheme: {config.color_scheme}
- Transitions: {config.transitions}

## Audio Style
- Background Music: {config.background_music_style}
- Voiceover Style: {config.voiceover_style}
- Sound Effects: {config.sound_effects}

---
This is a placeholder file. In a full implementation, this would be a complete MP4 video file.
"""
        return content
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                return size_bytes / (1024 * 1024)
            return 0.0
        except:
            return 0.0
    
    def _ensure_perfect_duration_sync(self, clips: List[str], audio_files: List[str],
                                    target_duration: float) -> Dict[str, Any]:
        """Ensure perfect duration synchronization between video and audio"""
        logger.info(f"⏱️ Ensuring perfect duration sync for {target_duration}s")
        
        # This is a placeholder for the duration sync logic
        # In a full implementation, this would:
        # 1. Analyze actual clip and audio durations
        # 2. Trim or extend clips to match target duration
        # 3. Ensure audio matches video length exactly
        
        return {
            'video_duration': target_duration,
            'audio_duration': target_duration,
            'sync_accuracy': 1.0,
            'adjustments_made': []
        }



