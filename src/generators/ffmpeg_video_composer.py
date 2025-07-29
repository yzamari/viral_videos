"""
FFmpeg Video Composer - Replaces MoviePy with high-performance FFmpeg operations
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.ffmpeg_processor import FFmpegProcessor
from ..agents.enhanced_overlay_agent import EnhancedOverlayAgent

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
        """Compose final video with perfect sync and cool overlays"""
        
        logger.info(f"🎬 Composing final video with {len(video_clips)} clips and {len(audio_segments)} audio segments")
        
        with FFmpegProcessor() as ffmpeg:
            try:
                # Step 1: Create base video from clips
                if len(video_clips) > 1:
                    base_video = self._create_temp_path("base_video.mp4")
                    ffmpeg.concatenate_videos(video_clips, base_video)
                else:
                    base_video = video_clips[0]
                
                # Step 2: Create synchronized audio
                if len(audio_segments) > 1:
                    synced_audio = self._create_temp_path("synced_audio.mp3")
                    synced_audio = await self._create_subtitle_synced_audio(
                        ffmpeg, audio_segments, subtitle_segments, synced_audio
                    )
                else:
                    synced_audio = audio_segments[0] if audio_segments else None
                
                # Step 3: Combine video and audio with perfect sync
                if synced_audio:
                    video_with_audio = self._create_temp_path("video_with_audio.mp4")
                    ffmpeg.add_audio_to_video(base_video, synced_audio, video_with_audio, "exact")
                else:
                    video_with_audio = base_video
                
                # Step 4: Generate AI-powered viral overlays
                overlays = await self.overlay_agent.generate_viral_overlays(
                    mission=config.get('mission', ''),
                    script=config.get('script', ''),
                    duration=ffmpeg.get_duration(video_with_audio),
                    platform=config.get('platform', 'instagram'),
                    style=config.get('style', 'viral'),
                    segments=config.get('segments', [])
                )
                
                # Step 5: Add cool overlays
                if overlays:
                    logger.info(f"🎨 Adding {len(overlays)} viral overlays")
                    overlay_filters = self.overlay_agent.convert_to_ffmpeg_filters(overlays)
                    
                    video_with_overlays = self._create_temp_path("video_with_overlays.mp4")
                    ffmpeg._run_command([
                        'ffmpeg', '-y',
                        '-i', video_with_audio,
                        '-vf', overlay_filters,
                        '-c:a', 'copy',
                        video_with_overlays
                    ], "Adding viral overlays")
                    
                    video_with_audio = video_with_overlays
                
                # Step 6: Add subtitles if provided
                if subtitle_segments:
                    subtitle_file = self._create_subtitle_file(subtitle_segments)
                    if subtitle_file:
                        final_video = self._create_temp_path("final_with_subs.mp4")
                        ffmpeg.add_subtitles(video_with_audio, subtitle_file, final_video)
                        video_with_audio = final_video
                
                # Step 7: Final optimization and copy to output
                self._optimize_final_video(ffmpeg, video_with_audio, output_path, config)
                
                logger.info(f"✅ Video composition complete: {output_path}")
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
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
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
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
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