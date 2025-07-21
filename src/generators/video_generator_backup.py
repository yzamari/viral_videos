"""Video Generator - Main video generation orchestrator
Coordinates video generation using VEO2/VEO3, Gemini images, and TTS"""

import os
import json
import tempfile
import shutil
from typing import Dict, Any, Optional, List
import subprocess

from ..models.video_models import GeneratedVideoConfig
from ..utils.logging_config import get_logger
from ..generators.veo_client_factory import VeoClientFactory
from ..agents.voice_director_agent import VoiceDirectorAgent
from ..agents.overlay_positioning_agent import OverlayPositioningAgent
from ..utils.session_context import SessionContext
from ..utils.exceptionsimport (VideoGenerationError,
    AudioGenerationError,
    SubtitleGenerationError
)
from ..generators.director import Director

logger = get_logger(__name__)

class VideoGenerator:
    """Enhanced video generator with AI-powered features"""def __init(self, api_key: str, credentials_path: Optional[str] = None): """Initialize the video generator with API credentials"""self.api_key = api_key
        self.credentials_path = credentials_path

        # Initialize VEO client factory with proper project credentials
        self.veo_factory = VeoClientFactory()

        # Initialize AI agents
        self.director = Director(api_key=self.api_key)
        self.voice_director = VoiceDirectorAgent(api_key)
        self.overlay_positioning = OverlayPositioningAgent(api_key)

    def generate_viral_video(self,
        config: GeneratedVideoConfig,
        script_result: Dict[str, Any],
        session_context: SessionContext
    ) -> str:
        """Main method to generate a complete viral video.

        Orchestrates audio generation, video clip creation,
        and final composition with subtitles.
        """
        logger.info("🎬 Starting AI-optimized video generation")
        logger.info(f"📊 Config: {config.topic[:50]}...")
        logger.info(f"🎯 Target: {config.target_platform.value}")
        logger.info(f"⏱️ Duration: {config.duration_seconds}s")

        try:
            # 1. Generate audio clips
            audio_files = self._generate_ai_optimized_audio(config, script_result, session_context
            )

            # 2. Generate video clips
            video_clips = self._generate_video_clips(config, script_result, session_context
            )

            # If no video clips were generated, create a fallback
            if not video_clips: logger.warning("⚠️ No video clips generated, creating fallback from audio.")
                return self._create_fallback_video_from_audio(audio_files, config, session_context
                )

            # 3. Add professional subtitles
            final_video_path = self._add_professional_subtitles(video_clips,
                    audio_files, script_result, config, session_context
            )

            if not final_video_path or not os.path.exists(final_video_path): raise VideoGenerationError("Final video path not found or invalid.")
 logger.info(f"✅ Video generation successful: {final_video_path}")
            return final_video_path

        except (VideoGenerationError,
            AudioGenerationError,
            SubtitleGenerationError) as e: logger.error(f"❌ Video generation failed: {e}")
            raise
        except Exception as e: logger.error(f"❌ An unexpected error occurred: {e}", exc_info=True) raise VideoGenerationError(f"An unexpected error occurred: {e}")

    def _generate_ai_optimized_audio(self,
        config: GeneratedVideoConfig,
        script_result: Dict[str, Any],
        session_context: SessionContext
    ) -> List[str]: """Generate multiple audio clips with AI-selected voices"""logger.info("🎤 Generating AI-optimized audio")

        # Get AI voice strategy
        voice_strategy_result = self.voice_director.decide_voice_strategy(topic=config.topic,
            platform=config.target_platform.value,
            duration=config.duration_seconds,
            num_clips=4
        )
        voice_strategy = voice_strategy_result.get('voices', []) logger.info(f"🎯 Voice strategy: {len(voice_strategy)} voices selected")

        # Segment script for audio generation
        script_segments = self._segment_script_for_audio(script_result)

        # Initialize TTS client
        try:
            from ..generators.enhanced_multilang_tts import EnhancedMultilingualTTSClient
            tts_client = EnhancedMultilingualTTSClient(self.api_key)
        except ImportError: logger.error("❌ Failed to import EnhancedMultilingualTTSClient") raise AudioGenerationError("TTS client could not be initialized.")

        audio_files = []
        for i, segment in enumerate(script_segments):
            if i >= len(voice_strategy):
                logger.warning( f"⚠️ Not enough voices for segment {i + 1},reusing last voice.")
                voice_config = voice_strategy[-1]
            else:
                voice_config = voice_strategy[i]
 # CRITICAL FIX: Do not send pitch for Studio voices if "studio" in voice_config.get('voice_name', '').lower(): if 'pitch' in voice_config: del voice_config['pitch']
                    logger.info( f"🎤 Removed pitch for Studio voice: { voice_config.get('voice_name')}") logger.info(f"🎵 Generating audio segment {i + 1}/{len(script_segments)}") logger.info(f"🎤 Voice: {voice_config.get('voice_name')}")

            try:
                audio_path = tts_client.generate_intelligent_voice(text=segment, language_code="en-US", output_dir=session_context.get_output_path("audio"), clip_id=f"audio_segment_{i}", voice_name=voice_config.get('voice_name'), speaking_rate=voice_config.get('speed'), pitch=voice_config.get('pitch', 0),  # Use default if missing emotion=voice_config.get('emotion')
                )
                if audio_path and os.path.exists(audio_path): audio_files.append(audio_path) logger.info(f"✅ Generated audio for clip {i}: {voice_config.get('voice_name')}")
                else: logger.warning(f"⚠️ Failed to generate audio for clip {i}")

            except Exception as e: logger.error(f"❌ Error generating audio for clip {i}: {e}")
                continue

        if not audio_files: raise AudioGenerationError("No audio segments were successfully generated.")
 logger.info(f"🎵 Audio generation complete: {len(audio_files)} segments created")

        # Save audio generation metadata
        audio_metadata = { "total_segments": len(script_segments), "successful_segments": len(audio_files), "voice_strategy": voice_strategy, "script_segments": script_segments
        }

        metadata_path = os.path.join( session_context.get_output_path("metadata"), "audio_generation.json")
        try: with open(metadata_path, 'w') as f:
                json.dump(audio_metadata, f, indent=2)
        except Exception as e: logger.warning(f"Could not save audio metadata: {e}")

        return audio_files

    def _generate_video_clips(self, config: GeneratedVideoConfig,
                              script_result: Dict[str, Any],
                              session_context: SessionContext) -> List[str]: """Generate video clips using VEO clients with optional frame continuity"""logger.info("🎥 Generating video clips")

        # Get best VEO client
        veo_client = self.veo_factory.get_best_available_client( output_dir=session_context.get_output_path("video_clips")
        )

        if not veo_client: logger.error("❌ No VEO client available")
            return []
 logger.info(f"🤖 Using VEO client: {veo_client.__class__.__name__}")

        # Check if Director decided to use frame continuity
        from ..generators.director import Director

        director = Director(api_key=self.api_key)
        continuity_decision = director.decide_frame_continuity(topic=config.topic,
            style=config.visual_style,
            category=config.category,
            duration=config.duration_seconds,
            platform=config.target_platform
        )
 use_continuity = continuity_decision.get('use_frame_continuity', False) logger.info(f"🎬 Frame continuity decision: {use_continuity}")

        if use_continuity:
            # Use continuous video generation for seamless flow
            return self._generate_continuous_video_clips(veo_client,
                    config, script_result, session_context, continuity_decision
            )
        else:
            # Use standard individual clip generation
            return self._generate_individual_video_clips(veo_client, config, script_result, session_context
            )

    def _generate_continuous_video_clips(self,
        veo_client, config: GeneratedVideoConfig,
                                         script_result: Dict[str, Any],
                                         session_context: SessionContext,
                                         continuity_decision: Dict[str, Any]) -> List[str]: """Generate continuous video clips with frame continuity"""logger.info("🎬 Generating continuous video with frame continuity")

        # Get script text for continuous generation
        if isinstance(script_result, dict): script_text = script_result.get('final_script', '')
            if not script_text: script_text = script_result.get('script', '')
        else:
            script_text = str(script_result)

        if not script_text: logger.error("❌ No script text available for continuous generation")
            return []

        # Use recommended clip count from Director num_clips = continuity_decision.get('recommended_clip_count', 4)
        clip_duration = config.duration_seconds / num_clips

        # Generate continuous video using VEO client if hasattr(veo_client, 'generate_continuous_video'):
            continuous_video_path = veo_client.generate_continuous_video(base_prompt=script_text,
                num_clips=num_clips,
                clip_duration=clip_duration, base_clip_id="continuous_main")

            if continuous_video_path and os.path.exists(continuous_video_path): logger.info(f"✅ Generated continuous video: {continuous_video_path}")
                return [continuous_video_path]  # Return as single continuous clip
            else:
                logger.warning( "⚠️ Continuous generation failed,"
                    falling back to individual clips")"
                return self._generate_individual_video_clips(veo_client, config, script_result, session_context
                )
        else: logger.warning( "⚠️ VEO client doesn't support continuous generation,"'
                    using individual clips")"
            return self._generate_individual_video_clips(veo_client, config, script_result, session_context
            )

    def _generate_individual_video_clips(self,
        veo_client, config: GeneratedVideoConfig,
                                         script_result: Dict[str, Any],
                                         session_context: SessionContext) -> List[str]: """Generate individual video clips (standard mode)"""logger.info("🎥 Generating individual video clips")

        # Prepare script segments
        script_segments = self._segment_script_for_video(script_result, config.duration_seconds
        )

        if not script_segments: logger.error("❌ No script segments available for video generation")
            return []

        video_clips = []
        for i, segment in enumerate(script_segments): logger.info(f"🎬 Generating video clip {i + 1}/{len(script_segments)}")

            try:
                # Generate video clip
                clip_path = veo_client.generate_video(prompt=segment,
                    duration=config.duration_seconds // len(script_segments), clip_id=f"clip_{i}")

                if clip_path and os.path.exists(clip_path):
                    video_clips.append(clip_path) logger.info(f"✅ Generated clip {i}: {clip_path}")
                else: logger.warning(f"⚠️ Failed to generate clip {i}")

            except Exception as e: logger.error(f"❌ Error generating clip {i}: {str(e)}")
                continue

        return video_clips

    def _segment_script_for_video(self, script_result: Dict[str, Any],
                                  duration: float) -> List[str]: """Segment script for video generation"""if isinstance(script_result, dict):
            script_text = script_result.get('final_script', '')
            if not script_text: script_text = script_result.get('script', '')
        else:
            script_text = str(script_result)

        # Split into sentences sentences = [s.strip() for s in script_text.split('.') if s.strip()]

        # Group sentences into segments
        segments = []
        current_segment = []
        target_segments = max(3, min(6, int(duration / 5)))  # 3-6 segments

        sentences_per_segment = len(sentences) // target_segments
        for i, sentence in enumerate(sentences):
            current_segment.append(sentence)

            if len(current_segment) >= sentences_per_segment or i == len(sentences) - 1: segments.append('. '.join(current_segment) + '.')
                _current_segment = []

        return segments if segments else [script_text]

    def _segment_script_for_audio(self,
        script_result: Dict[str,
        Any]) -> List[str]: """Segment script text into equal parts for audio generation"""if isinstance(script_result, dict): script_text = script_result.get('final_script', '')
            if not script_text: script_text = script_result.get('script', '')
        else:
            script_text = str(script_result)

        # Split into words
        words = script_text.strip().split()
        if len(words) < 4:
            # If too few words, duplicate content
            return [script_text] * 4

        # Calculate words per segment
        words_per_segment = len(words) // 4
        segments = []

        for i in range(4):
            start_idx = i * words_per_segment
            if i == 3:  # Last segment gets remaining words
                end_idx = len(words)
            else:
                end_idx = (i + 1) * words_per_segment

            segment_words = words[start_idx:end_idx] segments.append(' '.join(segment_words))

        return segments

    def _ensure_perfect_duration_sync(self, clips: List[str], audio_files: List[str],
                                      target_duration: float) -> Dict[str, Any]: """ENHANCED: Ensure perfect synchronization between video clips,"
        audio segments, and target duration """logger.info(f"🔄 Ensuring perfect duration sync for {len(clips)} clips "f"and {len(audio_files)} audio files")"

        sync_result = { "clips_adjusted": 0, "audio_adjusted": 0, "total_video_duration": 0.0, "total_audio_duration": 0.0, "sync_success": False, "adjustments_made": []
        }

        try:
            # Calculate total video duration
            total_video_duration = 0.0
            for clip in clips:
                if os.path.exists(clip):
                    result = subprocess.run([ 'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', clip
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        info = json.loads(result.stdout) duration = float(info['format']['duration'])
                        total_video_duration += duration

            # Calculate total audio duration
            total_audio_duration = 0.0
            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    result = subprocess.run([ 'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_file
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        info = json.loads(result.stdout) duration = float(info['format']['duration'])
                        total_audio_duration += duration

            sync_result.update( "total_video_duration": total_video_duration, "total_audio_duration": total_audio_duration, "sync_success": abs(total_video_duration - total_audio_duration) < 1.0
            ) logger.info(f"📊 Video duration: {total_video_duration:.2f}s") logger.info(f"📊 Audio duration: {total_audio_duration:.2f}s") logger.info(f"✅ Sync success: {sync_result['sync_success']}")

        except Exception: logger.warning("⚠️ Could not calculate duration sync")

        return sync_result

    def _add_professional_subtitles(self, video_clips: List[str], audio_files: List[str],
                                    script_result: Dict[str, Any],
                                    config: GeneratedVideoConfig,
                                    session_context: SessionContext) -> str: """Add professional subtitles with perfect timing"""logger.info("📝 Adding subtitle overlays to final video")

        # Handle case when no video clips were generated
        if not video_clips: logger.warning("⚠️ No video clips available for subtitle overlay")
            # Create a fallback video from audio
            return self._create_fallback_video_from_audio(audio_files,
                config,
                session_context)

        # Get AI positioning decision logger.info("🎯 Getting AI positioning decision")
        self.overlay_positioning.analyze_optimal_positioning(topic=config.topic,
            video_style=config.visual_style,
            platform=config.target_platform.value,
            duration=config.duration_seconds,
            subtitle_count=len(video_clips)
        )

        # Create subtitle segments
        subtitle_segments = self._create_subtitle_segments(script_result, len(video_clips), config.duration_seconds
        )

        # Synchronize with audio
        synchronized_segments = self._synchronize_with_audio_segments(subtitle_segments, config.duration_seconds, session_context
        )

        # Concatenate video clips first
        temp_video = self._concatenate_video_clips(video_clips)

        # Add subtitle overlays
        final_video = self._apply_subtitle_overlays(temp_video, synchronized_segments, config, session_context
        )

        return final_video

    def _create_subtitle_segments(self, script_result: Dict[str, Any],
                                  num_segments: int, duration: float) -> List[Dict[str, Any]]: """Create subtitle segments from script"""if num_segments <= 0: logger.warning("⚠️ No segments provided for subtitle creation")
            return []

        if isinstance(script_result, dict): script_text = script_result.get('final_script', '')
            if not script_text: script_text = script_result.get('script', '')
        else:
            script_text = str(script_result)

        if not script_text: logger.warning("⚠️ No script text available for subtitle creation")
            return []

        # Split into words for better timing
        words = script_text.split()
        if not words: logger.warning("⚠️ No words found in script for subtitle creation")
            return []

        segment_duration = duration / num_segments
        words_per_segment = max(1, len(words) // num_segments)

        segments = []
        for i in range(num_segments):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration

            start_word = i * words_per_segment
            end_word = (i + 1) * words_per_segment if i < num_segments - 1 else len(words)
 segment_text = ' '.join(words[start_word:end_word])

            if segment_text:  # Only add non-empty segments
                segments.append( 'text': segment_text, 'start_time': start_time, 'end_time': end_time, 'duration': segment_duration
                )

        return segments

    def _synchronize_with_audio_segments(self, segments: List[Dict[str, Any]],
                                         video_duration: float,
                                         session_context: SessionContext) -> List[Dict[str, Any]]: """ENHANCED: Synchronize subtitle segments with audio files for perfect timing """logger.info(f"🎵 Synchronizing {len(segments)} subtitle segments with audio")

        try:
            # Get audio files from session context audio_dir = session_context.get_output_path("audio")
            audio_files = []

            if os.path.exists(audio_dir):
                audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3') and 'segment' in f]
                audio_files.sort()

            if not audio_files: logger.warning("⚠️ No audio files found for synchronization")
                return segments

            # Calculate precise timing based on audio files
            current_time = 0.0
            synchronized_segments = []

            for i, (segment, audio_file) in enumerate(zip(segments, audio_files)):
                audio_path = os.path.join(audio_dir, audio_file)

                try:
                    # Get actual audio duration
                    result = subprocess.run([ 'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_path
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        info = json.loads(result.stdout) actual_duration = float(info['format']['duration'])

                        synchronized_segment = { 'text': segment['text'], 'start_time': current_time, 'end_time': current_time + actual_duration, 'duration': actual_duration, 'audio_file': audio_file
                        }

                        synchronized_segments.append(synchronized_segment)
                        current_time += actual_duration
 logger.info(f"📝 Synchronized segment {i}: "f"{current_time - actual_duration:.1f}-{current_time:.1f}s")

                except Exception:
                    # Fallback to original timing
                    synchronized_segments.append(segment)

            return synchronized_segments

        except Exception as e: logger.error(f"❌ Synchronization failed: {str(e)}")
            return segments

    def _concatenate_video_clips(self, video_clips: List[str]) -> str: """Concatenate video clips into single video"""if not video_clips: raise VideoGenerationError("No video clips to concatenate")

        if len(video_clips) == 1:
            return video_clips[0]

        # Create temporary file for concatenation temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_video.close()

        try:
            # Create file list for ffmpeg file_list = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) for clip in video_clips: file_list.write(f"file '{clip}'\n")
            file_list.close()

            # Concatenate with ffmpeg
            cmd = [ 'ffmpeg', '-', 'concat', '-safe', '0', '-i', file_list.name, '-c', 'copy', '-y', temp_video.name
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0: logger.info("✅ Video clips concatenated successfully")
                return temp_video.name
            else: logger.error(f"❌ Concatenation failed: {result.stderr}") raise VideoGenerationError(f"Video concatenation failed: {result.stderr}")

        finally:
            # Clean up file list
            if os.path.exists(file_list.name):
                os.unlink(file_list.name)

    def _apply_subtitle_overlays(self, video_path: str, segments: List[Dict[str, Any]],
                                 config: GeneratedVideoConfig,
                                 session_context: SessionContext) -> str: """Apply subtitle overlays to video"""logger.info(f"🎬 Compositing video with {len(segments)} subtitle overlays")

        # Create output path
        output_path = os.path.join( session_context.get_output_path("final_output"), f"final_video_{session_context.session_id}.mp4")

        try:
            # Build subtitle filter
            subtitle_filters = []
            for i, segment in enumerate(segments): # Escape text for ffmpeg text = segment['text'].replace("'", "\\'").replace('"', '\\"') start_time = segment['start_time'] end_time = segment['end_time']

                # Create subtitle filter with professional styling subtitle_filter = ( f"drawtext=text='{text}'"":fontfile=/System/Library/Fonts/Arial.tt"":fontsize=24:fontcolor=white"":x=(w-text_w)/2:y=h-100"f":enable='between(t,{start_time},{end_time)'"":box=1:boxcolor=black@0.5:boxborderw=5")
                subtitle_filters.append(subtitle_filter) logger.info(f"📝 Added subtitle: '{text[:30]}...' at "f"{start_time:.1f}-{end_time:.1f}s")

            # Combine all subtitle filters
            if subtitle_filters: filter_complex = ','.join(subtitle_filters)
            else: filter_complex = "null"# Apply subtitles with ffmpeg
            cmd = [ 'ffmpeg', '-i', video_path, '-v', filter_complex, '-c:a', 'copy', '-y', str(output_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0: logger.info(f"✅ Subtitles applied successfully: {output_path}")
                return str(output_path)
            else: logger.error(f"❌ Subtitle application failed: {result.stderr}")
                # Return original video if subtitle application fails
                shutil.copy2(video_path, output_path)
                return str(output_path)

        except Exception: logger.error("❌ Subtitle overlay failed")
            # Return original video if overlay fails
            shutil.copy2(video_path, output_path)
            return str(output_path)

    def _get_video_info(self, video_path: str) -> Dict[str, Any]: """Get video information using ffprobe"""try:
            result = subprocess.run([ 'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path
            ], capture_output=True, text=True)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {}

        except Exception:
            return {}

    def _create_fallback_video_from_audio(self,
            audio_files: List[str],
            config: GeneratedVideoConfig,
            session_context: SessionContext) -> str: """Create a fallback video from audio files when no video clips are available"""logger.info("🎨 Creating fallback video from audio files")

        if not audio_files: logger.error("❌ No audio files available for fallback video") return ""try:
            # Create a simple colored video with audio
            output_path = os.path.join( session_context.get_output_path("final_output"), f"fallback_video_{session_context.session_id}.mp4")

            # Concatenate audio files
            audio_concat_path = os.path.join( session_context.get_output_path("audio"), "concatenated_audio.mp3")

            # Create audio concatenation file list
            audio_list_path = os.path.join( session_context.get_output_path("audio"), "audio_list.txt")
 with open(audio_list_path, 'w') as f: for audio_file in audio_files: f.write(f"file '{audio_file}'\n")

            # Concatenate audio files
            concat_cmd = [ 'ffmpeg', '-y', '-', 'concat', '-safe', '0', '-i', audio_list_path, '-c', 'copy',
                audio_concat_path
            ]

            subprocess.run(concat_cmd, capture_output=True, text=True, check=True)

            # Get audio duration
            duration_cmd = [ 'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-o', 'csv=p=0', audio_concat_path
            ]

            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            audio_duration = float(duration_result.stdout.strip())
 # Create video with audio aspect_ratio = "9:16" if config.target_platform.value.lower() in [ 'instagram', 'tiktok'] else "16:9"size = "1080x1920" if aspect_ratio == "9:16" else "1920x1080"video_cmd = [ 'ffmpeg', '-y', '-', 'lavfi', '-i', f'color=c=black:size={size}:duration={audio_duration}:rate=30', '-i', audio_concat_path, '-c:v', 'libx264', '-preset', 'fast', '-cr', '23', '-c:a', 'aac', '-b:a', '128k', '-pix_fmt', 'yuv420p', '-shortest',
                output_path
            ]

            subprocess.run(video_cmd, capture_output=True, text=True, check=True)

            if os.path.exists(output_path): logger.info(f"✅ Fallback video created: {output_path}")
                return output_path
            else: logger.error("❌ Failed to create fallback video") return ""except Exception as e: logger.error(f"❌ Error creating fallback video: {e}") return ""
