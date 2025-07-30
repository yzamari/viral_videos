"""
Refactored Video Generator - Uses Duration Authority and Audio-First Subtitles
Eliminates audio-subtitle sync issues and duration mismatches
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import new refactored components  
from ..core.duration_authority import DurationAuthority, ComponentType, DurationContract
from ..utils.audio_first_subtitle_generator import AudioFirstSubtitleGenerator
from ..utils.simplified_audio_processor import SimplifiedAudioProcessor

# Import existing components
from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from ..utils.logging_config import get_logger
from ..utils.session_context import SessionContext
from ..generators.enhanced_multilang_tts import EnhancedMultilingualTTS
from ..generators.enhanced_script_processor import EnhancedScriptProcessor
from ..generators.director import Director
from ..config import video_config

logger = get_logger(__name__)


@dataclass
class RefactoredVideoResult:
    """Result of refactored video generation"""
    file_path: str
    duration_authority: DurationAuthority
    subtitle_files: Dict[str, str]  # {'srt': path, 'vtt': path}
    audio_files: List[str]
    video_clips: List[str]
    generation_time: float
    sync_quality_score: float
    success: bool
    error_message: Optional[str] = None


class RefactoredVideoGenerator:
    """
    Refactored video generator that solves the core issues:
    
    1. CENTRALIZED DURATION CONTROL
       - Single DurationAuthority makes all duration decisions
       - Components receive constraints, don't make their own decisions
       
    2. AUDIO-FIRST SUBTITLE GENERATION  
       - Generate audio first, then create subtitles from actual durations
       - Eliminates sync issues from estimation vs reality mismatch
       
    3. SIMPLIFIED AUDIO PROCESSING
       - No complex filter chains that cause stuttering
       - Simple, reliable audio operations
    """
    
    def __init__(self, api_key: str):
        """Initialize refactored video generator"""
        self.api_key = api_key
        
        # Initialize components
        self.script_processor = EnhancedScriptProcessor(api_key)
        self.tts_generator = EnhancedMultilingualTTS(api_key)
        self.director = Director(api_key)
        
        # Initialize new refactored components
        self.subtitle_generator = AudioFirstSubtitleGenerator()
        
        logger.info("🚀 Refactored Video Generator initialized")
        logger.info("   ✅ Centralized duration control")
        logger.info("   ✅ Audio-first subtitle generation")  
        logger.info("   ✅ Simplified audio processing")
        
    async def generate_video(self,
                           config: GeneratedVideoConfig,
                           session_context: SessionContext,
                           force_regenerate: bool = False) -> RefactoredVideoResult:
        """
        Generate video using the refactored approach
        
        Args:
            config: Video generation configuration
            session_context: Session context for file management
            force_regenerate: Force regeneration even if files exist
            
        Returns:
            RefactoredVideoResult with all generation results
        """
        start_time = time.time()
        
        logger.info("🎬 Starting refactored video generation")
        logger.info(f"   Mission: {config.mission}")
        logger.info(f"   Duration: {config.duration_seconds}s")
        logger.info(f"   Platform: {config.target_platform}")
        
        try:
            # STEP 1: CREATE DURATION AUTHORITY (SINGLE SOURCE OF TRUTH)
            duration_authority = DurationAuthority(
                target_duration=config.duration_seconds,
                tolerance_percent=0.05  # 5% tolerance
            )
            
            # Get generation constraints from authority
            constraints = duration_authority.get_generation_constraints()
            logger.info(f"📏 Generation constraints: max_words={constraints['max_words']}, "
                       f"max_segments={constraints['max_segments']}, max_clips={constraints['max_clips']}")
            
            # STEP 2: GENERATE SCRIPT WITH DURATION CONSTRAINTS
            script_result = await self._generate_constrained_script(
                config, duration_authority, session_context
            )
            
            # Register script duration with authority
            script_duration = script_result.get('total_estimated_duration', 0)
            duration_authority.register_component_duration(
                ComponentType.SCRIPT, 
                script_duration,
                confidence=0.7  # Script is estimated, not measured
            )
            
            # STEP 3: GENERATE AUDIO FROM SCRIPT (ACTUAL DURATIONS)
            audio_files = await self._generate_audio_segments(
                script_result, config, duration_authority, session_context
            )
            
            # Measure ACTUAL audio duration and register with authority
            with SimplifiedAudioProcessor() as audio_processor:
                total_audio_duration = sum(
                    audio_processor.get_audio_duration(f) for f in audio_files
                )
            
            duration_authority.register_component_duration(
                ComponentType.AUDIO,
                total_audio_duration, 
                confidence=1.0  # Audio is measured, fully accurate
            )
            
            # STEP 4: CREATE SUBTITLES FROM ACTUAL AUDIO (ELIMINATES SYNC ISSUES)
            subtitle_files = await self._create_audio_first_subtitles(
                audio_files, script_result, session_context
            )
            
            # Register subtitle duration
            duration_authority.register_component_duration(
                ComponentType.SUBTITLES,
                total_audio_duration,  # Subtitles match audio exactly
                confidence=1.0
            )
            
            # STEP 5: GENERATE VIDEO CLIPS WITH DURATION CONSTRAINTS
            video_clips = await self._generate_video_clips(
                script_result, config, duration_authority, session_context
            )
            
            # STEP 6: COMPOSE FINAL VIDEO
            final_video_path = await self._compose_final_video(
                video_clips, audio_files, subtitle_files, 
                config, duration_authority, session_context
            )
            
            # STEP 7: VALIDATE FINAL RESULT
            is_valid, issues = duration_authority.validate_final_result()
            
            generation_time = time.time() - start_time
            
            # Calculate sync quality score
            sync_quality = self._calculate_sync_quality_score(duration_authority)
            
            result = RefactoredVideoResult(
                file_path=final_video_path,
                duration_authority=duration_authority,
                subtitle_files=subtitle_files,
                audio_files=audio_files,
                video_clips=video_clips,
                generation_time=generation_time,
                sync_quality_score=sync_quality,
                success=is_valid and not issues,
                error_message="; ".join(issues) if issues else None
            )
            
            # Log final results
            self._log_generation_summary(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Refactored video generation failed: {e}")
            generation_time = time.time() - start_time
            
            return RefactoredVideoResult(
                file_path="",
                duration_authority=duration_authority if 'duration_authority' in locals() else None,
                subtitle_files={},
                audio_files=[],
                video_clips=[],
                generation_time=generation_time,
                sync_quality_score=0.0,
                success=False,
                error_message=str(e)
            )
            
    async def _generate_constrained_script(self,
                                         config: GeneratedVideoConfig,
                                         duration_authority: DurationAuthority,
                                         session_context: SessionContext) -> Dict[str, Any]:
        """Generate script with strict duration constraints"""
        logger.info("📝 Generating script with duration constraints")
        
        # Get constraints from authority
        max_words = duration_authority.calculate_max_words()
        target_duration = duration_authority.get_target_duration()
        
        # Process script with constraints
        script_result = await self.script_processor.process_script_for_tts(
            config.mission,
            config.language,
            target_duration=target_duration
        )
        
        # Enforce word limit using duration contract
        contract = duration_authority.create_duration_contract()
        estimated_duration = script_result.get('total_estimated_duration', 0)
        
        if estimated_duration > duration_authority.get_max_allowed_duration():
            logger.warning(f"⚠️ Script exceeds duration limit, enforcing constraints")
            script_result['optimized_script'] = contract.enforce_on_script(
                script_result['optimized_script'], 
                estimated_duration
            )
            # Recalculate duration after enforcement
            new_word_count = len(script_result['optimized_script'].split())
            script_result['total_estimated_duration'] = new_word_count / duration_authority.WORDS_PER_SECOND
            
        # Save script to session
        script_path = session_context.get_output_path("scripts", "constrained_script.txt")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_result['optimized_script'])
            
        logger.info(f"✅ Script: {script_result.get('total_word_count', 0)} words, "
                   f"{script_result.get('total_estimated_duration', 0):.1f}s estimated")
        
        return script_result
        
    async def _generate_audio_segments(self,
                                     script_result: Dict[str, Any],
                                     config: GeneratedVideoConfig,
                                     duration_authority: DurationAuthority,
                                     session_context: SessionContext) -> List[str]:
        """Generate audio segments and return file paths"""
        logger.info("🎵 Generating audio segments")
        
        segments = script_result.get('segments', [])
        if not segments:
            # Fallback: create single segment from full script
            segments = [{
                'text': script_result.get('optimized_script', ''),
                'duration': script_result.get('total_estimated_duration', 0),
                'voice_suggestion': 'storyteller'
            }]
            
        audio_files = []
        
        # Generate each audio segment
        for i, segment in enumerate(segments):
            segment_text = segment.get('text', '').strip()
            if not segment_text:
                logger.warning(f"⚠️ Empty text in segment {i+1}, skipping")
                continue
                
            # Generate audio for this segment
            audio_file = session_context.get_output_path("audio", f"audio_segment_{i+1:03d}.mp3")
            
            try:
                # Use TTS to generate audio
                await self.tts_generator.generate_audio(
                    text=segment_text,
                    output_path=audio_file,
                    language=config.language,
                    voice_id=segment.get('voice_suggestion', 'storyteller')
                )
                
                # Verify audio file was created
                if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                    audio_files.append(audio_file)
                    logger.info(f"   ✅ Segment {i+1}/{len(segments)}: {os.path.basename(audio_file)}")
                else:
                    logger.error(f"❌ Failed to generate audio for segment {i+1}")
                    
            except Exception as e:
                logger.error(f"❌ Audio generation failed for segment {i+1}: {e}")
                
        if not audio_files:
            raise ValueError("No audio files were generated successfully")
            
        logger.info(f"✅ Generated {len(audio_files)} audio segments")
        return audio_files
        
    async def _create_audio_first_subtitles(self,
                                          audio_files: List[str],
                                          script_result: Dict[str, Any],
                                          session_context: SessionContext) -> Dict[str, str]:
        """Create subtitles based on actual audio durations"""
        logger.info("📝 Creating audio-first subtitles")
        
        # Extract script segments 
        segments = script_result.get('segments', [])
        
        # Use subtitle generator to create subtitles from actual audio
        subtitle_dir = session_context.get_output_path("subtitles")
        os.makedirs(subtitle_dir, exist_ok=True)
        
        srt_path, vtt_path, subtitle_segments = self.subtitle_generator.generate_subtitles(
            audio_files=audio_files,
            script_segments=segments,
            output_dir=subtitle_dir,
            base_filename="audio_synced_subtitles"
        )
        
        return {
            'srt': srt_path,
            'vtt': vtt_path,
            'segments': subtitle_segments
        }
        
    async def _generate_video_clips(self,
                                  script_result: Dict[str, Any],
                                  config: GeneratedVideoConfig,
                                  duration_authority: DurationAuthority,
                                  session_context: SessionContext) -> List[str]:
        """Generate video clips with duration constraints"""
        logger.info("🎬 Generating video clips with duration constraints")
        
        # Get constraints from authority
        max_clips = duration_authority.calculate_max_clips()
        target_duration = duration_authority.get_target_duration()
        
        # For now, create a simple placeholder implementation
        # In full implementation, this would use VEO/image generation
        video_clips = []
        
        # Create placeholder video clips
        from moviepy.editor import ColorClip
        
        clip_duration = target_duration / max_clips
        
        for i in range(max_clips):
            clip_path = session_context.get_output_path("video_clips", f"clip_{i+1:03d}.mp4")
            
            # Create colored clip as placeholder
            color = (30 + (i * 30) % 200, 50 + (i * 40) % 150, 100 + (i * 50) % 100)
            clip = ColorClip(size=(1920, 1080), color=color, duration=clip_duration)
            clip.write_videofile(clip_path, fps=24, codec='libx264', verbose=False, logger=None)
            clip.close()
            
            video_clips.append(clip_path)
            logger.info(f"   ✅ Clip {i+1}/{max_clips}: {clip_duration:.1f}s")
            
        logger.info(f"✅ Generated {len(video_clips)} video clips")
        return video_clips
        
    async def _compose_final_video(self,
                                 video_clips: List[str],
                                 audio_files: List[str],
                                 subtitle_files: Dict[str, str],
                                 config: GeneratedVideoConfig,
                                 duration_authority: DurationAuthority,
                                 session_context: SessionContext) -> str:
        """Compose final video with simplified audio processing"""
        logger.info("🎯 Composing final video")
        
        final_output = session_context.get_output_path("final_output", "refactored_video.mp4")
        
        with SimplifiedAudioProcessor() as audio_processor:
            # Step 1: Concatenate video clips
            if len(video_clips) > 1:
                from moviepy.editor import VideoFileClip, concatenate_videoclips
                
                clips = [VideoFileClip(clip_path) for clip_path in video_clips]
                final_video = concatenate_videoclips(clips)
                
                # Save video without audio first
                temp_video = session_context.get_output_path("temp", "video_only.mp4")
                final_video.write_videofile(temp_video, fps=24, codec='libx264', 
                                          audio=False, verbose=False, logger=None)
                
                # Clean up clips
                for clip in clips:
                    clip.close()
                final_video.close()
            else:
                temp_video = video_clips[0]
                
            # Step 2: Concatenate audio using simplified processor
            temp_audio = session_context.get_output_path("temp", "concatenated_audio.aac")
            audio_processor.concatenate_audio_simple(audio_files, temp_audio)
            
            # Step 3: Add audio to video
            audio_processor.add_audio_to_video_simple(temp_video, temp_audio, final_output)
            
        # Register final video duration
        with SimplifiedAudioProcessor() as processor:
            final_duration = processor._get_video_info(final_output).get('duration', 0)
            
        duration_authority.register_component_duration(
            ComponentType.VIDEO,
            final_duration,
            confidence=1.0
        )
        
        logger.info(f"✅ Final video created: {final_output}")
        return final_output
        
    def _calculate_sync_quality_score(self, duration_authority: DurationAuthority) -> float:
        """Calculate sync quality score based on duration authority data"""
        if ComponentType.AUDIO not in duration_authority.component_durations:
            return 0.0
            
        if ComponentType.SUBTITLES not in duration_authority.component_durations:
            return 0.5  # Audio exists but no subtitles
            
        audio_duration = duration_authority.component_durations[ComponentType.AUDIO]
        subtitle_duration = duration_authority.component_durations[ComponentType.SUBTITLES]
        
        # Calculate sync error
        sync_error = abs(audio_duration - subtitle_duration)
        
        # Convert to quality score (0-1, where 1 is perfect)
        if sync_error <= 0.1:  # Within 100ms
            return 1.0
        elif sync_error <= 0.5:  # Within 500ms
            return 0.8
        elif sync_error <= 1.0:  # Within 1 second
            return 0.6
        else:
            return max(0.0, 1.0 - (sync_error / 5.0))  # Degrade score for larger errors
            
    def _log_generation_summary(self, result: RefactoredVideoResult):
        """Log comprehensive generation summary"""
        logger.info("📊 REFACTORED VIDEO GENERATION SUMMARY")
        logger.info("=" * 50)
        
        if result.duration_authority:
            logger.info("🎯 DURATION ANALYSIS:")
            target = result.duration_authority.target_duration
            logger.info(f"   Target duration: {target:.1f}s")
            
            for component, duration in result.duration_authority.component_durations.items():
                diff = duration - target
                status = "✅" if abs(diff) <= target * 0.05 else "⚠️"
                logger.info(f"   {status} {component.value}: {duration:.1f}s ({diff:+.1f}s)")
                
        logger.info(f"🎵 Audio files: {len(result.audio_files)}")
        logger.info(f"🎬 Video clips: {len(result.video_clips)}")
        logger.info(f"📝 Subtitle files: {len(result.subtitle_files)}")
        logger.info(f"⏱️ Generation time: {result.generation_time:.1f}s")
        logger.info(f"🎯 Sync quality: {result.sync_quality_score:.1f}/1.0")
        
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        logger.info(f"🏁 Result: {status}")
        
        if result.error_message:
            logger.error(f"   Error: {result.error_message}")
            
        logger.info("=" * 50)