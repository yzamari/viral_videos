"""
FFmpeg Video Composer - Replaces MoviePy with high-performance FFmpeg operations
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from ..utils.ffmpeg_processor import FFmpegProcessor
    from ..agents.enhanced_overlay_agent import EnhancedOverlayAgent
except ImportError:
    from src.utils.ffmpeg_processor import FFmpegProcessor
    from src.agents.enhanced_overlay_agent import EnhancedOverlayAgent

logger = logging.getLogger(__name__)

class FFmpegVideoComposer:
    """High-performance video composer using FFmpeg instead of MoviePy"""
    
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
        self.overlay_agent = EnhancedOverlayAgent(ai_manager)
        logger.info("🎬 FFmpeg Video Composer initialized")
    
    async def compose_final_video(self, video_clips: List[str], audio_segments: List[str],
                                subtitle_segments: List[Dict], config: Dict[str, Any],
                                output_path: str) -> str:
        """Compose final video with perfect sync and cool overlays
        
        CRITICAL: Pipeline reordered to prevent audio loss:
        1. Create base video
        2. Add overlays (while no audio)
        3. Add subtitles (while no audio)
        4. Create synchronized audio
        5. Add audio as final step
        """
        
        logger.info(f"🎬 Composing final video with {len(video_clips)} clips and {len(audio_segments)} audio segments")
        logger.info("🔄 Using audio-safe pipeline: overlays → subtitles → audio")
        
        with FFmpegProcessor() as ffmpeg:
            try:
                # Step 1: Create base video from clips (NO AUDIO YET)
                if len(video_clips) > 1:
                    base_video = self._create_temp_path("base_video.mp4")
                    ffmpeg.concatenate_videos(video_clips, base_video)
                else:
                    base_video = video_clips[0]
                
                # Get base video duration for overlay generation
                base_duration = ffmpeg.get_duration(base_video)
                logger.info(f"📏 Base video duration: {base_duration:.2f}s")
                
                # Step 2: Generate AI-powered viral overlays
                overlays = await self.overlay_agent.generate_viral_overlays(
                    mission=config.get('mission', ''),
                    script=config.get('script', ''),
                    duration=base_duration,
                    platform=config.get('platform', 'instagram'),
                    style=config.get('style', 'viral'),
                    segments=config.get('segments', [])
                )
                
                # Step 3: Add cool overlays to video (NO AUDIO YET)
                current_video = base_video
                if overlays:
                    logger.info(f"🎨 Adding {len(overlays)} viral overlays to video (before audio)")
                    overlay_filters = self.overlay_agent.convert_to_ffmpeg_filters(overlays)
                    
                    video_with_overlays = self._create_temp_path("video_with_overlays.mp4")
                    ffmpeg._run_command([
                        'ffmpeg', '-y',
                        '-i', current_video,
                        '-vf', overlay_filters,
                        '-c:v', 'libx264',
                        '-preset', 'slow',    # QUALITY FIX: slow preset for better quality
                        '-crf', '18',         # QUALITY FIX: High quality CRF (lower = better)
                        '-an',  # CRITICAL: Discard any audio during overlay processing
                        video_with_overlays
                    ], "Adding viral overlays (high quality, no audio)")
                    
                    current_video = video_with_overlays
                
                # Step 4: Skip subtitles here - MoviePy will handle them later
                # This prevents duplicate subtitles and allows better styling
                logger.info("📝 Skipping subtitles in FFmpeg - MoviePy will add them with better styling")
                
                # Step 5: Create synchronized audio
                synced_audio = None
                if audio_segments:
                    if len(audio_segments) > 1:
                        synced_audio = self._create_temp_path("synced_audio.m4a")
                        synced_audio = await self._create_subtitle_synced_audio(
                            ffmpeg, audio_segments, subtitle_segments, synced_audio
                        )
                    else:
                        synced_audio = audio_segments[0]
                    
                    logger.info(f"🎵 Audio prepared: {synced_audio}")
                
                # Step 6: Add audio to fully processed video as FINAL step
                if synced_audio:
                    logger.info("🎼 Adding audio to fully processed video (final step)")
                    video_with_audio = self._create_temp_path("final_with_audio.mp4")
                    ffmpeg.add_audio_to_video(current_video, synced_audio, video_with_audio, "exact")
                    current_video = video_with_audio
                    
                    # Verify audio is present
                    if ffmpeg.has_audio_stream(current_video):
                        logger.info("✅ Audio successfully added to final video")
                    else:
                        logger.error("❌ WARNING: Audio was not properly added!")
                else:
                    logger.warning("⚠️ No audio segments provided")
                
                # Step 7: Final optimization and copy to output
                self._optimize_final_video(ffmpeg, current_video, output_path, config)
                
                # Final audio check
                if ffmpeg.has_audio_stream(output_path):
                    logger.info(f"✅ Video composition complete with audio: {output_path}")
                else:
                    logger.error(f"❌ WARNING: Final video missing audio: {output_path}")
                
                return output_path
                
            except Exception as e:
                logger.error(f"❌ Video composition failed: {e}")
                raise
    
    async def _create_subtitle_synced_audio(self, ffmpeg: FFmpegProcessor, 
                                          audio_segments: List[str],
                                          subtitle_segments: List[Dict],
                                          output_path: str) -> str:
        """Create audio perfectly synced to subtitle timing"""
        
        if not subtitle_segments:
            # Fallback to simple concatenation
            return ffmpeg.concatenate_audio(audio_segments, output_path, crossfade=True)
        
        # Build complex audio filter for precise timing
        inputs = []
        for audio_file in audio_segments:
            inputs.extend(['-i', audio_file])
        
        # Create audio timeline based on subtitle timing
        filter_parts = []
        audio_streams = []
        
        for i, (segment, audio_idx) in enumerate(zip(subtitle_segments, range(len(audio_segments)))):
            start_time = segment.get('start', 0)
            duration = segment.get('end', start_time + 3) - start_time
            
            # Delay audio to match subtitle timing exactly
            delay_ms = int(start_time * 1000)
            
            if delay_ms > 0:
                filter_parts.append(f'[{audio_idx}:a]adelay={delay_ms}|{delay_ms}[delayed{i}]')
                audio_streams.append(f'[delayed{i}]')
            else:
                audio_streams.append(f'[{audio_idx}:a]')
        
        # Mix all delayed audio streams
        if len(audio_streams) > 1:
            mix_filter = ''.join(audio_streams) + f'amix=inputs={len(audio_streams)}:duration=longest[outa]'
            filter_parts.append(mix_filter)
            filter_complex = ';'.join(filter_parts)
        else:
            filter_complex = filter_parts[0] if filter_parts else '[0:a]copy[outa]'
        
        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', filter_complex,
            '-map', '[outa]',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_path
        ]
        
        ffmpeg._run_command(cmd, "Creating subtitle-synced audio")
        return output_path
    
    def _create_subtitle_file(self, subtitle_segments: List[Dict]) -> Optional[str]:
        """Create SRT subtitle file"""
        try:
            subtitle_path = self._create_temp_path("subtitles.srt")
            
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(subtitle_segments, 1):
                    start = segment.get('start', 0)
                    end = segment.get('end', start + 3)
                    text = segment.get('text', '')
                    
                    # Convert to SRT time format
                    start_time = self._seconds_to_srt_time(start)
                    end_time = self._seconds_to_srt_time(end)
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n") 
                    f.write(f"{text}\n\n")
            
            return subtitle_path
            
        except Exception as e:
            logger.error(f"Failed to create subtitle file: {e}")
            return None
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _optimize_final_video(self, ffmpeg: FFmpegProcessor, input_path: str, 
                            output_path: str, config: Dict[str, Any]):
        """Apply final optimizations for platform"""
        
        platform = config.get('platform', 'instagram').lower()
        
        # Platform-specific optimization
        if platform == 'instagram':
            # Instagram Reels optimization
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',  # Enable fast start for web
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease:flags=bilinear,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
                output_path
            ]
        elif platform == 'tiktok':
            # TikTok optimization
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'fast', 
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-r', '30',  # 30fps for TikTok
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease:flags=bilinear,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
                output_path
            ]
        elif platform == 'youtube':
            # YouTube optimization
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'slow',  # Better quality for YouTube
                '-crf', '21',
                '-c:a', 'aac',
                '-b:a', '192k',  # Higher audio quality
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
        else:
            # General optimization
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
        
        ffmpeg._run_command(cmd, f"Optimizing for {platform}")
    
    def _create_temp_path(self, filename: str) -> str:
        """Create temporary file path"""
        import tempfile
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, f"ffmpeg_compose_{filename}")
    
    async def create_audio_only_version(self, video_path: str, output_path: str) -> str:
        """Create audio-only version for comparison/debugging"""
        
        with FFmpegProcessor() as ffmpeg:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-c:v', 'copy',
                '-an',  # Remove audio for debugging
                output_path
            ]
            
            ffmpeg._run_command(cmd, "Creating audio-only version")
            return output_path
            
    def get_composition_stats(self, video_path: str) -> Dict[str, Any]:
        """Get detailed stats about composed video"""
        
        with FFmpegProcessor() as ffmpeg:
            info = ffmpeg.get_video_info(video_path)
            duration = ffmpeg.get_duration(video_path)
            
            return {
                "duration": duration,
                "file_size_mb": os.path.getsize(video_path) / (1024 * 1024),
                "video_info": info,
                "composition_method": "ffmpeg_native"
            }