"""Scraped Media Composer - Creates videos using ONLY scraped media, NO VEO generation"""

import os
import subprocess
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

from ...utils.logging_config import get_logger
from ...utils.session_manager import SessionManager
from ..processors.media_downloader import MediaDownloader
from ..models.content_models import ContentItem, MediaAsset, AssetType

logger = get_logger(__name__)


class ScrapedMediaComposer:
    """Creates videos using ONLY scraped media - NO AI generation"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        media_downloader: MediaDownloader,
        output_dir: str = "outputs/scraped_videos"
    ):
        self.session_manager = session_manager
        self.media_downloader = media_downloader
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    async def create_video_from_scraped_media(
        self,
        content_items: List[ContentItem],
        duration_seconds: int = 30,
        style: str = "fast-paced",
        output_filename: Optional[str] = None
    ) -> str:
        """Create video using ONLY scraped media files"""
        
        logger.info("🎬 Creating video from SCRAPED MEDIA ONLY (NO VEO)")
        
        # 1. Extract all media URLs
        all_media = []
        for item in content_items:
            for asset in item.media_assets:
                if asset.asset_type in [AssetType.VIDEO, AssetType.IMAGE]:
                    all_media.append({
                        "asset": asset,
                        "item": item,
                        "url": asset.source_url
                    })
        
        logger.info(f"📸 Found {len(all_media)} media assets to download")
        
        # 2. Download all media
        downloaded_files = await self._download_all_media(all_media)
        
        if not downloaded_files:
            raise ValueError("No media could be downloaded!")
        
        logger.info(f"✅ Downloaded {len(downloaded_files)} media files")
        
        # 3. Process media for video composition
        video_clips = await self._prepare_video_clips(
            downloaded_files,
            duration_seconds,
            style
        )
        
        # 4. Create final video with FFmpeg
        output_path = await self._compose_final_video(
            video_clips,
            duration_seconds,
            style,
            output_filename
        )
        
        logger.info(f"✅ Video created using SCRAPED MEDIA: {output_path}")
        return output_path
    
    async def _download_all_media(
        self,
        media_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Download all media files"""
        
        downloaded = []
        
        for media_info in media_list:
            try:
                # Download using media downloader
                result = await self.media_downloader.download_media(
                    media_info["url"],
                    metadata={
                        "title": media_info["item"].title,
                        "source": media_info["item"].source.name
                    }
                )
                
                if result and os.path.exists(result["local_path"]):
                    downloaded.append({
                        "path": result["local_path"],
                        "type": result["media_type"],
                        "duration": result.get("duration"),
                        "title": media_info["item"].title,
                        "metadata": result
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to download {media_info['url']}: {str(e)}")
        
        return downloaded
    
    async def _prepare_video_clips(
        self,
        downloaded_files: List[Dict[str, Any]],
        total_duration: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """Prepare video clips from downloaded media"""
        
        clips = []
        
        # Calculate time per clip
        num_clips = min(len(downloaded_files), max(4, total_duration // 5))
        time_per_clip = total_duration / num_clips
        
        # Process each media file
        for i, media in enumerate(downloaded_files[:num_clips]):
            if media["type"] == "video":
                # Trim video to desired length
                clip_path = await self._trim_video_clip(
                    media["path"],
                    time_per_clip,
                    style
                )
                clips.append({
                    "path": clip_path,
                    "duration": time_per_clip,
                    "title": media["title"],
                    "type": "video"
                })
                
            elif media["type"] == "image":
                # Convert image to video clip
                clip_path = await self._image_to_video(
                    media["path"],
                    time_per_clip,
                    style
                )
                clips.append({
                    "path": clip_path,
                    "duration": time_per_clip,
                    "title": media["title"],
                    "type": "image"
                })
        
        return clips
    
    async def _trim_video_clip(
        self,
        video_path: str,
        duration: float,
        style: str
    ) -> str:
        """Trim video to specific duration"""
        
        output_path = video_path.replace(".mp4", f"_trimmed_{duration}s.mp4")
        
        # FFmpeg command to trim video
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23"
        ]
        
        # Add style-specific filters
        if style == "fast-paced":
            # Speed up slightly and add energy
            cmd.extend([
                "-filter:v", "setpts=0.8*PTS,eq=contrast=1.2:brightness=0.05"
            ])
        
        cmd.append(output_path)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to trim video: {e.stderr}")
            return video_path  # Return original if trim fails
    
    async def _image_to_video(
        self,
        image_path: str,
        duration: float,
        style: str
    ) -> str:
        """Convert image to video clip with movement"""
        
        output_path = image_path.replace(".jpg", f"_video_{duration}s.mp4").replace(".png", f"_video_{duration}s.mp4")
        
        # FFmpeg command for image to video with Ken Burns effect
        if style == "fast-paced":
            # Zoom and pan effect
            filter_str = (
                f"scale=1920*2:1080*2,"
                f"zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={int(duration*25)}:s=1920x1080:fps=25"
            )
        else:
            # Simple pan
            filter_str = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-vf", filter_str,
            "-preset", "fast",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert image to video: {e.stderr}")
            # Create simple static video as fallback
            return await self._create_static_video(image_path, duration)
    
    async def _create_static_video(self, image_path: str, duration: float) -> str:
        """Create simple static video from image"""
        output_path = image_path.replace(".jpg", f"_static_{duration}s.mp4").replace(".png", f"_static_{duration}s.mp4")
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        return output_path
    
    async def _compose_final_video(
        self,
        video_clips: List[Dict[str, Any]],
        total_duration: int,
        style: str,
        output_filename: Optional[str] = None
    ) -> str:
        """Compose final video from clips using FFmpeg"""
        
        if not video_clips:
            raise ValueError("No video clips to compose!")
        
        # Create concat file
        concat_file = os.path.join(self.output_dir, "concat_list.txt")
        with open(concat_file, "w") as f:
            for clip in video_clips:
                f.write(f"file '{clip['path']}'\n")
        
        # Output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"scraped_media_video_{style}_{timestamp}.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # FFmpeg concat command
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p"
        ]
        
        # Add style-specific final touches
        if style == "fast-paced":
            cmd.extend([
                "-filter_complex",
                "[0:v]setpts=0.9*PTS,eq=contrast=1.1:saturation=1.2[v]",
                "-map", "[v]"
            ])
        
        cmd.append(output_path)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"✅ Final video composed: {output_path}")
            
            # Clean up temp files
            os.remove(concat_file)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to compose final video: {e.stderr}")
            raise


async def create_scraped_media_video(
    content_items: List[ContentItem],
    duration_seconds: int = 30,
    style: str = "fast-paced",
    output_filename: Optional[str] = None
) -> str:
    """Create video using only scraped media"""
    
    from ...utils.session_manager import SessionManager
    from ..processors.media_downloader import MediaDownloader
    
    session_manager = SessionManager()
    media_downloader = MediaDownloader()
    
    composer = ScrapedMediaComposer(session_manager, media_downloader)
    
    return await composer.create_video_from_scraped_media(
        content_items,
        duration_seconds,
        style,
        output_filename
    )