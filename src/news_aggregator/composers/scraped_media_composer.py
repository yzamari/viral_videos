"""Scraped Media Composer - Creates videos using ONLY scraped media, NO VEO generation"""

import os
import subprocess
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap

# RTL text support
try:
    from bidi.algorithm import get_display
    import arabic_reshaper
    RTL_SUPPORT = True
except ImportError:
    RTL_SUPPORT = False
    get_display = lambda x: x  # Fallback

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
        output_dir: str = "outputs/scraped_videos",
        visual_styles: Dict[str, Any] = None,
        logo_path: str = None,
        channel_name: str = "NEWS"
    ):
        self.session_manager = session_manager
        self.media_downloader = media_downloader
        self.output_dir = output_dir
        self.visual_styles = visual_styles or {}
        self.logo_path = logo_path
        self.channel_name = channel_name
        os.makedirs(output_dir, exist_ok=True)
        self.dimensions = (1920, 1080)  # Default dimensions
        self.platform = "youtube"  # Default platform
    
    async def create_video_from_scraped_media(
        self,
        content_items: List[ContentItem],
        duration_seconds: int = 30,
        style: str = "fast-paced",
        output_filename: Optional[str] = None,
        platform: str = "youtube"
    ) -> str:
        """Create video using ONLY scraped media files"""
        
        logger.info("🎬 Creating video from SCRAPED MEDIA ONLY (NO VEO)")
        
        # Set dimensions based on platform
        self.platform = platform
        if platform == "tiktok":
            self.dimensions = (1080, 1920)  # Portrait
        elif platform == "instagram":
            self.dimensions = (1080, 1080)  # Square
        else:
            self.dimensions = (1920, 1080)  # Landscape
        
        # 1. Extract all media URLs
        all_media = []
        for item in content_items:
            for asset in item.media_assets:
                if asset.asset_type in [AssetType.VIDEO, AssetType.IMAGE]:
                    # Check if this is a YouTube video that's already downloaded
                    if asset.source_url == 'youtube' and asset.local_path:
                        # YouTube video already downloaded, use directly
                        all_media.append({
                            "asset": asset,
                            "item": item,
                            "url": asset.local_path,  # Use local path instead of source_url
                            "already_downloaded": True
                        })
                    else:
                        # Regular media that needs downloading
                        all_media.append({
                            "asset": asset,
                            "item": item,
                            "url": asset.source_url,
                            "already_downloaded": False
                        })
        
        logger.info(f"📸 Found {len(all_media)} media assets to download")
        
        # 2. Download all media
        downloaded_files = await self._download_all_media(all_media)
        
        if not downloaded_files:
            logger.warning("No media could be downloaded, creating text-only video")
            # Create text-only segments for ALL content items
            for i, item in enumerate(content_items):
                # Include rephrasing information in text segments
                text_metadata = {
                    "content": item.content, 
                    "index": i + 1, 
                    "total": len(content_items),
                    "original_title": getattr(item, 'metadata', {}).get('original_title', ''),
                    "original_content": getattr(item, 'metadata', {}).get('original_content', ''),
                    "rephrased": getattr(item, 'metadata', {}).get('rephrased', False)
                }
                downloaded_files.append({
                    "path": None,
                    "type": "text", 
                    "title": item.title,
                    "original_title": getattr(item, 'metadata', {}).get('original_title', ''),
                    "original_content": getattr(item, 'metadata', {}).get('original_content', ''),
                    "rephrased": getattr(item, 'metadata', {}).get('rephrased', False),
                    "metadata": text_metadata
                })
        
        logger.info(f"✅ Downloaded {len(downloaded_files)} media files")
        
        # 3. Process media for video composition
        video_clips = await self._prepare_video_clips(
            downloaded_files,
            duration_seconds,
            style
        )
        
        # 4. Create final video with FFmpeg
        logger.info(f"📹 Composing final video from {len(video_clips)} clips")
        if not video_clips:
            logger.error("No video clips created! Cannot compose final video")
            # Create a simple fallback video
            fallback_path = await self._create_fallback_video(duration_seconds, style, output_filename)
            return fallback_path
            
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
                # Check if already downloaded (YouTube videos)
                if media_info.get("already_downloaded", False) and os.path.exists(media_info["url"]):
                    # YouTube video already downloaded
                    logger.info(f"📹 Using pre-downloaded YouTube video: {media_info['url']}")
                    downloaded.append({
                        "path": media_info["url"],
                        "type": "video",  # YouTube videos are always videos
                        "duration": None,  # Will be detected by FFmpeg
                        "title": media_info["item"].title,
                        "metadata": {"source": "youtube", "local_path": media_info["url"]}
                    })
                else:
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
        # Ensure we show all items, adjusting time per clip
        num_clips = len(downloaded_files)
        logger.info(f"📊 Processing {num_clips} downloaded files")
        if num_clips == 0:
            logger.error("No downloaded files to process!")
            return []
        
        # RESPECT USER'S REQUESTED DURATION - calculate time per clip exactly
        time_per_clip = total_duration / num_clips if num_clips > 0 else total_duration
        actual_duration = total_duration  # Always respect user's exact duration
        
        logger.info(f"📊 Creating {num_clips} clips, {time_per_clip:.1f}s each (total: {actual_duration:.1f}s)")
        
        # Process each media file
        for i, media in enumerate(downloaded_files[:num_clips]):
            logger.info(f"🎬 Processing clip {i+1}/{num_clips}: {media['type']} - {media.get('title', 'No title')[:50]}")
            
            if media["type"] == "text":
                # Create text video segment with rephrasing info
                segment_metadata = media.get("metadata", {})
                # Pass through rephrasing information
                segment_metadata.update({
                    "original_title": media.get("original_title", ""),
                    "original_content": media.get("original_content", ""),  
                    "rephrased": media.get("rephrased", False)
                })
                clip_path = await self._create_text_segment(
                    media["title"],
                    media.get("metadata", {}).get("content", ""),
                    time_per_clip,
                    style,
                    segment_metadata
                )
                
                # Verify the clip was created
                if os.path.exists(clip_path):
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=noprint_wrappers=1:nokey=1', clip_path]
                    duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    actual_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0
                    logger.info(f"  ✅ Created text clip: {actual_duration:.1f}s")
                else:
                    logger.error(f"  ❌ Failed to create text clip")
                    continue
                    
                clips.append({
                    "path": clip_path,
                    "duration": time_per_clip,
                    "title": media["title"],
                    "type": "text"
                })
            elif media["type"] == "video":
                # Trim video to desired length
                clip_path = await self._trim_video_clip(
                    media["path"],
                    time_per_clip,
                    style,
                    media["title"]
                )
                
                # Verify the clip was created
                if os.path.exists(clip_path):
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=noprint_wrappers=1:nokey=1', clip_path]
                    duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    actual_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0
                    logger.info(f"  ✅ Created video clip: {actual_duration:.1f}s")
                else:
                    logger.error(f"  ❌ Failed to create video clip")
                    continue
                    
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
                    style,
                    media["title"]
                )
                
                # Verify the clip was created
                if os.path.exists(clip_path):
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=noprint_wrappers=1:nokey=1', clip_path]
                    duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    actual_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0
                    logger.info(f"  ✅ Created image clip: {actual_duration:.1f}s")
                else:
                    logger.error(f"  ❌ Failed to create image clip")
                    continue
                    
                clips.append({
                    "path": clip_path,
                    "duration": time_per_clip,
                    "title": media["title"],
                    "type": "image"
                })
        
        logger.info(f"📊 Total clips created: {len(clips)}")
        return clips
    
    async def _trim_video_clip(
        self,
        video_path: str,
        duration: float,
        style: str,
        title: str = ""
    ) -> str:
        """Trim video to specific duration with overlay"""
        
        output_path = video_path.replace(".mp4", f"_trimmed_{duration}s.mp4")
        
        # Create overlay image for the video
        overlay_path = await self._create_video_overlay(title, style)
        
        # FFmpeg command to trim video and add overlay
        width, height = self.dimensions
        filter_complex = []
        
        # Always scale to target dimensions
        filter_complex.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1")
        
        # Base video processing
        if style == "fast-paced":
            filter_complex.append("setpts=0.8*PTS,eq=contrast=1.2:brightness=0.05")
        
        # Add overlay if created
        if overlay_path and os.path.exists(overlay_path):
            filter_str = ",".join(filter_complex) if filter_complex else ""
            if filter_str:
                filter_str = f"[0:v]{filter_str}[v1];[v1][1:v]overlay=0:0[v]"
            else:
                filter_str = "[0:v][1:v]overlay=0:0[v]"
            
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", overlay_path,
                "-t", str(duration),
                "-filter_complex", filter_str,
                "-map", "[v]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                output_path
            ]
        else:
            # Fallback without overlay
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-t", str(duration),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23"
            ]
            
            # Always apply filters (at minimum, scaling)
            cmd.extend(["-filter:v", ",".join(filter_complex)])
            
            cmd.append(output_path)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            # Clean up overlay
            if overlay_path and os.path.exists(overlay_path):
                os.remove(overlay_path)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to trim video: {e.stderr}")
            return video_path  # Return original if trim fails
    
    async def _image_to_video(
        self,
        image_path: str,
        duration: float,
        style: str,
        title: str = ""
    ) -> str:
        """Convert image to video clip with movement and overlay"""
        
        output_path = image_path.replace(".jpg", f"_video_{duration}s.mp4").replace(".png", f"_video_{duration}s.mp4")
        
        # Create overlay
        overlay_path = await self._create_video_overlay(title, style)
        
        # FFmpeg command for image to video with Ken Burns effect
        if style == "fast-paced":
            # Zoom and pan effect
            width, height = self.dimensions
            base_filter = (
                f"scale={width*2}:{height*2},"
                f"zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={int(duration*25)}:s={width}x{height}:fps=25"
            )
        else:
            # Simple pan
            width, height = self.dimensions
            base_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        
        # Build command with or without overlay
        if overlay_path and os.path.exists(overlay_path):
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", image_path,
                "-i", overlay_path,
                "-filter_complex",
                f"[0:v]{base_filter}[v];[v][1:v]overlay=0:0",
                "-c:v", "libx264",
                "-t", str(duration),
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                output_path
            ]
        else:
            # Check if it's a GIF file
            if image_path.lower().endswith('.gif'):
                # For GIFs, don't use loop parameter at all
                cmd = [
                    "ffmpeg", "-y",
                    "-i", image_path,
                    "-c:v", "libx264",
                    "-t", str(duration),
                    "-pix_fmt", "yuv420p",
                    "-vf", base_filter,
                    "-preset", "fast",
                    output_path
                ]
            else:
                # For static images
                cmd = [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", image_path,
                    "-c:v", "libx264",
                    "-t", str(duration),
                    "-pix_fmt", "yuv420p",
                    "-vf", base_filter,
                    "-preset", "fast",
                    output_path
                ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            # Clean up overlay
            if overlay_path and os.path.exists(overlay_path):
                os.remove(overlay_path)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert image to video: {e.stderr}")
            # Create simple static video as fallback
            return await self._create_static_video(image_path, duration)
    
    async def _create_text_segment(self, title: str, content: str, duration: float, style: str, metadata: dict = None, visual_styles: dict = None) -> str:
        """Create text-only video segment with modern design and proper Unicode support"""
        
        if metadata is None:
            metadata = {}
        
        # Use AI-selected visual styles or defaults
        if visual_styles is None:
            visual_styles = self.visual_styles or {}
        
        # Create gradient background with modern design
        width, height = self.dimensions
        img = Image.new('RGB', (width, height))
        draw_temp = ImageDraw.Draw(img)
        
        # Create more vibrant gradient based on style
        if style == 'dark_humor':
            # Dark humor/satirical: black to dark gray gradient
            for y in range(height):
                progress = y / height
                r = int(10 * (1 - progress) + 5)   # Very dark red
                g = int(10 * (1 - progress) + 5)   # Very dark green
                b = int(15 * (1 - progress) + 10)  # Slightly more blue for depth
                draw_temp.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
        elif "news" in style.lower() or "breaking" in style.lower():
            # News style: dark red to black gradient
            for y in range(height):
                progress = y / height
                r = int(80 * (1 - progress) + 20)
                g = int(20 * (1 - progress) + 10)
                b = int(30 * (1 - progress) + 15)
                draw_temp.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
        else:
            # Default: modern blue gradient
            for y in range(height):
                progress = y / height
                r = int(20 * (1 - progress) + 10)
                g = int(40 * (1 - progress) + 20)
                b = int(80 * (1 - progress) + 40)
                draw_temp.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
        
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts that support Hebrew/Arabic/Russian
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # macOS Unicode font
            "/System/Library/Fonts/Supplemental/Arial Hebrew.ttf",  # macOS Hebrew font
            "/System/Library/Fonts/Supplemental/Heiti TC.ttc",  # macOS CJK font
            "/Library/Fonts/Arial Unicode.ttf",  # Alternative macOS path
            "/System/Library/Fonts/Times.ttc",  # macOS Times
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux Unicode font
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "C:/Windows/Fonts/arialuni.ttf",  # Windows Unicode
            "/System/Library/Fonts/Helvetica.ttc"  # Fallback
        ]
        
        font_title = None
        font_content = None
        font_loaded = False
        
        # Get font sizes from AI-selected visual styles - but ensure they're reasonable
        title_font_size = visual_styles.get('HEADER_FONT', {}).get('size', 48)
        content_font_size = visual_styles.get('CONTENT_FONT', {}).get('size', 32)
        
        # Platform-specific adjustments - MASSIVE FONTS FOR READABILITY
        if self.platform == "tiktok":
            # Portrait mode - HUGE FONTS
            title_font_size = 100  # Big bold title
            content_font_size = 60  # Large readable content
        else:
            # Landscape mode - LARGE FONTS
            title_font_size = 110
            content_font_size = 65
        
        logger.info(f"📝 Using AI-selected font sizes - Title: {title_font_size}, Content: {content_font_size}")
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    logger.info(f"Testing font: {font_path}")
                    # Use AI-selected font sizes
                    font_title = ImageFont.truetype(font_path, title_font_size)
                    font_content = ImageFont.truetype(font_path, content_font_size)
                    # Test if font supports Hebrew
                    test_img = Image.new('RGB', (100, 100))
                    test_draw = ImageDraw.Draw(test_img)
                    test_draw.text((10, 10), "בדיקה", font=font_title)
                    font_loaded = True
                    logger.info(f"✅ Successfully loaded Unicode font: {font_path}")
                    break
            except Exception as e:
                logger.debug(f"Font {font_path} failed: {e}")
                continue
        
        if not font_loaded:
            logger.warning("⚠️  No Unicode font found, Hebrew text may not display correctly")
            font_title = ImageFont.load_default()
            font_content = ImageFont.load_default()
        
        # Detect if text is RTL (Hebrew/Arabic)
        is_rtl = any('\u0590' <= char <= '\u05FF' or '\u0600' <= char <= '\u06FF' for char in title)
        
        # USE FULL SCREEN for text display
        if self.platform == "tiktok":
            # Portrait layout - USE ENTIRE SCREEN
            title_y = int(height * 0.22)  # Move title down (was 0.15)
            content_y_start = title_y + 100  # Content closer to title
            overlay_width = int(width * 0.95)  # Use almost full width
            overlay_x = (width - overlay_width) // 2
        else:
            # Landscape layout - USE MORE SCREEN
            title_y = int(height * 0.30)  # Move title down (was 0.25)
            content_y_start = title_y + 90
            overlay_width = int(width * 0.90)  # Use 90% width
            overlay_x = (width - overlay_width) // 2
        
        # Draw title with proper alignment and text wrapping
        center_x = width // 2
        max_width = overlay_width - 60  # Leave good margins for readability
        
        # Better text wrapping that doesn't break mid-word (especially for Hebrew)
        def wrap_text_properly(text, font, max_width):
            """Wrap text without breaking words, show complete title"""
            lines = []
            current_line = ""
            
            # For Hebrew/RTL text, we need special handling
            is_hebrew = any('\u0590' <= c <= '\u05FF' for c in text)
            
            if is_hebrew:
                # For Hebrew, try to keep logical units together
                # Split on common Hebrew punctuation and spaces
                parts = text.replace(':', ' : ').replace('"', ' " ').replace(',', ' , ').split(' ')
            else:
                parts = text.split(' ')
            
            for part in parts:
                if not part:
                    continue
                    
                test_line = current_line + ' ' + part if current_line else part
                bbox = draw.textbbox((0, 0), test_line, font=font)
                
                if bbox[2] - bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = part
            
            if current_line:
                lines.append(current_line)
            
            # Make sure we show the complete title - no truncation
            return lines
        
        # Check if we have both original and rephrased versions for dual display
        has_original = metadata and (metadata.get('original_title') or 'original_title' in item for item in [metadata])
        if has_original:
            original_title = metadata.get('original_title', title)
            original_content = metadata.get('original_content', content)
            is_rephrased = metadata.get('rephrased', False)
            
            if is_rephrased and original_title != title:
                logger.info(f"📝 Dual text display: '{title[:30]}...' + original: '{original_title[:20]}...'")
        else:
            original_title = None
            is_rephrased = False
        
        # Wrap title - show complete title even if it needs multiple lines
        title_lines = wrap_text_properly(title, font_title, max_width)
        line_height = int(title_font_size * 1.3)  # Dynamic line height based on font size
        
        # Calculate space needed for dual display if applicable
        original_space = 0
        if original_title and is_rephrased and original_title != title:
            # Add space for original title in smaller font
            original_font_size = int(title_font_size * 0.7)  # 70% of main font size
            original_lines = wrap_text_properly(f"Original: {original_title}", font_content, max_width)
            original_space = len(original_lines) * int(original_font_size * 1.2) + 20
        
        # Calculate total height needed for title (including original if needed)
        total_title_height = len(title_lines) * line_height + original_space + 60  # Add padding
        
        # Create semi-transparent background that fits the entire title
        overlay_y = title_y - 30  # Start a bit above title
        overlay_height = max(200, total_title_height + 60)  # Ensure it covers all lines
        
        # Add semi-transparent background with rounded corners effect
        overlay = Image.new('RGBA', (overlay_width, overlay_height), (0, 0, 0, 200))  # More opaque
        img.paste(overlay, (overlay_x, overlay_y), overlay)
        
        # Add subtle border for better visibility
        border_overlay = Image.new('RGBA', (overlay_width, 3), (255, 255, 255, 80))
        img.paste(border_overlay, (overlay_x, overlay_y), border_overlay)
        img.paste(border_overlay, (overlay_x, overlay_y + overlay_height - 3), border_overlay)
        
        # Calculate starting y position - no overlay needed
        start_y = title_y  # Start directly at title position
        
        for i, line in enumerate(title_lines):
            line_y = start_y + i * line_height
            
            if is_rtl and RTL_SUPPORT:
                # Hebrew doesn't need reshaping, only bidi reordering
                if any('\u0590' <= char <= '\u05FF' for char in line):
                    # Hebrew text - PIL handles it correctly, no need for bidi
                    draw.text((center_x, line_y), line, fill=(255, 255, 255), font=font_title, anchor="ma")
                else:
                    # Arabic text - needs reshaping and bidi
                    reshaped_line = arabic_reshaper.reshape(line)
                    bidi_line = get_display(reshaped_line)
                    draw.text((center_x, line_y), bidi_line, fill=(255, 255, 255), font=font_title, anchor="ma")
            elif is_rtl:
                # Fallback for RTL without libraries
                draw.text((center_x, line_y), line[::-1], fill=(255, 255, 255), font=font_title, anchor="ma")
            else:
                draw.text((center_x, line_y), line, fill=(255, 255, 255), font=font_title, anchor="ma")
        
        # Add original title below main title if we have dual display
        if original_title and is_rephrased and original_title != title:
            original_font_size = int(title_font_size * 0.7)
            try:
                original_font = ImageFont.truetype(font_paths[0] if font_paths else '', original_font_size) if font_loaded else ImageFont.load_default()
            except:
                original_font = font_content
            
            # Just show the original title without "Original:" prefix
            original_text = original_title
            original_lines = wrap_text_properly(original_text, original_font, max_width)
            # Move original text up from bottom - to 70% of screen height
            original_start_y = int(height * 0.70)  # Move up (was 0.8)
            
            for i, orig_line in enumerate(original_lines):
                orig_y = original_start_y + i * int(original_font_size * 1.2)
                # Draw original in dimmer color to distinguish from main title
                # Draw original with shadow
                draw.text((center_x + 2, orig_y + 2), orig_line, fill=(0, 0, 0, 200), font=original_font, anchor="ma")
                draw.text((center_x, orig_y), orig_line, fill=(180, 180, 180), font=original_font, anchor="ma")
        
        # SIMPLIFIED DISPLAY - TITLE ONLY, NO LONG CONTENT
        # Removed content display to reduce text clutter in video
        
        # Add modern overlay elements
        # Top bar
        draw.rectangle([(0, 0), (width, 5)], fill=(255, 100, 0))
        # Bottom bar
        draw.rectangle([(0, height - 5), (width, height)], fill=(255, 100, 0))
        
        # Add item number indicator if available
        if metadata and metadata.get('index') and metadata.get('total'):
            index_text = f"{metadata['index']}/{metadata['total']}"
            # Position in top-right corner
            if self.platform == "tiktok":
                draw.text((width - 100, 50), index_text, fill=(255, 255, 255), font=font_content, anchor="ra")
            else:
                draw.text((width - 150, 50), index_text, fill=(255, 255, 255), font=font_content, anchor="ra")
        
        # Add timestamp
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        time_font = font_content if font_content else ImageFont.load_default()
        
        if self.platform == "tiktok":
            # Position for portrait
            draw.text((50, height - 40), time_str, fill=(200, 200, 200), font=time_font)
            # Platform indicator
            draw.text((width - 50, height - 40), "TIKTOK", fill=(200, 200, 200), font=time_font, anchor="ra")
        else:
            # Position for landscape
            draw.text((100, height - 40), time_str, fill=(200, 200, 200), font=time_font)
            # Add source/style indicator
            style_text = f"Style: {style.upper()}"
            draw.text((width - 100, height - 40), style_text, fill=(200, 200, 200), font=time_font, anchor="ra")
        
        # Save image with high quality
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        img_path = os.path.join(self.output_dir, f"text_segment_{timestamp}.jpg")
        img.save(img_path, quality=95)
        
        # Convert to video
        video_path = img_path.replace('.jpg', '.mp4')
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={width}:{height}",
            "-preset", "fast",
            video_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # Clean up image
        os.remove(img_path)
        
        return video_path
    
    async def _create_video_overlay(self, title: str, style: str) -> Optional[str]:
        """Create a modern overlay for video clips"""
        
        if not title:
            return None
        
        # Create transparent overlay image
        width, height = self.dimensions
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load better Hebrew fonts
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Hebrew.ttf",  # Better for Hebrew
            "/System/Library/Fonts/Supplemental/HebrewSupplement.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        
        font = None
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    # Larger font for better readability
                    font_size = 56 if self.platform == "tiktok" else 48
                    font = ImageFont.truetype(font_path, font_size)
                    break
            except:
                continue
        
        if not font:
            font = ImageFont.load_default()
        
        # Detect RTL
        is_rtl = any('\u0590' <= char <= '\u05FF' or '\u0600' <= char <= '\u06FF' for char in title)
        
        # Create lower third overlay - position higher for TikTok
        # Background gradient
        gradient_height = 180 if self.platform == "tiktok" else 120
        # Move subtitles much higher for TikTok (middle-bottom area)
        overlay_y = height - gradient_height - 400 if self.platform == "tiktok" else height // 2
        
        for y in range(gradient_height):
            alpha = int(200 * (1 - y / gradient_height))  # Fade out
            for x in range(width):
                if overlay_y + y < height:
                    img.putpixel((x, overlay_y + y), (0, 0, 0, alpha))
        
        # Add colored accent bar
        draw.rectangle([(0, overlay_y - 5), (width, overlay_y)], fill=(255, 100, 0, 255))
        
        # Draw title with multi-line support
        # Break long titles into multiple lines
        import textwrap
        max_chars = 30 if self.platform == "tiktok" else 40
        wrapped_title = title
        if len(title) > max_chars:
            wrapped_lines = textwrap.wrap(title, width=max_chars)
            wrapped_title = wrapped_lines[0] if len(wrapped_lines) == 1 else "\n".join(wrapped_lines[:2])
        
        text_y = overlay_y + gradient_height//2
        center_x = width // 2
        if is_rtl and RTL_SUPPORT:
            # Handle multi-line text with proper RTL support
            if "\n" in wrapped_title:
                lines = wrapped_title.split("\n")
                line_height = font.size + 10
                start_y = text_y - (len(lines) - 1) * line_height // 2
                for i, line in enumerate(lines):
                    if any('\u0590' <= char <= '\u05FF' for char in line):
                        # Hebrew text - PIL handles it correctly, no need for bidi
                        draw.text((center_x, start_y + i * line_height), line, fill=(255, 255, 255, 255), font=font, anchor="ma")
                    else:
                        # Arabic text - needs reshaping and bidi
                        reshaped_line = arabic_reshaper.reshape(line)
                        line_bidi = get_display(reshaped_line)
                        draw.text((center_x, start_y + i * line_height), line_bidi, fill=(255, 255, 255, 255), font=font, anchor="ma")
            else:
                # Single line text
                if any('\u0590' <= char <= '\u05FF' for char in wrapped_title):
                    # Hebrew text - PIL handles it correctly, no need for bidi
                    draw.text((center_x, text_y), wrapped_title, fill=(255, 255, 255, 255), font=font, anchor="ma")
                else:
                    # Arabic text - needs reshaping and bidi
                    reshaped_title = arabic_reshaper.reshape(wrapped_title)
                    bidi_title = get_display(reshaped_title)
                    draw.text((center_x, text_y), bidi_title, fill=(255, 255, 255, 255), font=font, anchor="ma")
        elif is_rtl:
            # Handle multi-line for fallback RTL
            if "\n" in wrapped_title:
                lines = wrapped_title.split("\n")
                line_height = font.size + 10
                start_y = text_y - (len(lines) - 1) * line_height // 2
                for i, line in enumerate(lines):
                    draw.text((center_x, start_y + i * line_height), line[::-1], fill=(255, 255, 255, 255), font=font, anchor="ma")
            else:
                draw.text((center_x, text_y), title[::-1], fill=(255, 255, 255, 255), font=font, anchor="ma")
        else:
            # Handle multi-line for English
            if "\n" in wrapped_title:
                lines = wrapped_title.split("\n")
                line_height = font.size + 10
                start_y = text_y - (len(lines) - 1) * line_height // 2
                for i, line in enumerate(lines):
                    draw.text((center_x, start_y + i * line_height), line, fill=(255, 255, 255, 255), font=font, anchor="ma")
            else:
                draw.text((center_x, text_y), wrapped_title, fill=(255, 255, 255, 255), font=font, anchor="ma")
        
        # Add platform-specific hooks with AI-selected styling
        hooks = self.visual_styles.get('HOOKS', ["NEWS"])
        hook_color = self.visual_styles.get('HOOK_COLOR', '#ff0000')
        hook_font_info = self.visual_styles.get('HOOK_FONT', {'size': 72})
        
        # Convert hex color to RGB
        hook_rgb = tuple(int(hook_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        import random
        hook_text = random.choice(hooks) if hooks else "BREAKING"
        
        # Platform-specific hook styling
        if self.platform in ["tiktok", "instagram"]:
            # Create eye-catching header
            header_height = 100
            # Gradient background with platform-specific color
            for y in range(header_height):
                alpha = int(220 - (y * 50 / header_height))
                for x in range(width):
                    img.putpixel((x, y), (*hook_rgb, alpha))
            
            # Add hook text
            hook_font_size = hook_font_info.get('size', 72)
            hook_font = ImageFont.truetype(font_paths[0], hook_font_size) if font_paths[0] and os.path.exists(font_paths[0]) else font
            draw.text((width // 2, 50), hook_text, fill=(255, 255, 255, 255), font=hook_font, anchor="ma")
            
            # Add channel name/logo area
            if self.logo_path and os.path.exists(self.logo_path):
                # Load and paste logo
                try:
                    logo = Image.open(self.logo_path).convert('RGBA')
                    logo_size = (80, 80)
                    logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
                    img.paste(logo, (width - 100, 20), logo)
                except:
                    pass
            else:
                # Show channel name with semi-transparent background
                channel_font_size = self.visual_styles.get('CHANNEL_FONT', {}).get('size', 36)
                channel_font = ImageFont.truetype(font_paths[0], channel_font_size) if font_paths[0] and os.path.exists(font_paths[0]) else font
                
                # Get text bounds for channel name
                bbox = draw.textbbox((0, 0), self.channel_name, font=channel_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Create semi-transparent background for channel name
                channel_bg_x = width - text_width - 70
                channel_bg_y = 30
                channel_bg = Image.new('RGBA', (text_width + 40, text_height + 20), (0, 0, 0, 180))
                img.paste(channel_bg, (channel_bg_x, channel_bg_y), channel_bg)
                
                # Draw channel name with AI-selected color
                channel_color = self.visual_styles.get('COLOR_SCHEME', {}).get('accent', '#ff6600')
                channel_rgb = tuple(int(channel_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                draw.text((width - 50, 50), self.channel_name, fill=(*channel_rgb, 255), font=channel_font, anchor="ra")
        else:
            logo_size = (300, 70)
            logo_pos = (50, 50)
            draw.rectangle([logo_pos, (logo_pos[0] + logo_size[0], logo_pos[1] + logo_size[1])], fill=(255, 100, 0, 180))
            logo_font = ImageFont.truetype(font_paths[0], 36) if font_paths[0] and os.path.exists(font_paths[0]) else font
            draw.text((logo_pos[0] + logo_size[0]//2, logo_pos[1] + logo_size[1]//2), self.channel_name, fill=(255, 255, 255, 255), font=logo_font, anchor="ma")
        
        # Save overlay
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        overlay_path = os.path.join(self.output_dir, f"overlay_{timestamp}.png")
        img.save(overlay_path)
        
        return overlay_path
    
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
    
    async def _create_fallback_video(self, duration: float, style: str, output_filename: str) -> str:
        """Create a simple fallback video when no clips are available"""
        logger.warning("Creating fallback video")
        
        # Create a simple text video
        text_path = await self._create_text_segment(
            "News Content",
            "Content being processed...",
            duration,
            style
        )
        
        if not output_filename:
            output_filename = f"fallback_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Copy the text video as output
        import shutil
        shutil.copy(text_path, output_path)
        
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
        logger.info(f"📝 Creating concat file with {len(video_clips)} clips at: {concat_file}")
        
        # Verify each clip exists and get its duration
        total_expected_duration = 0
        with open(concat_file, "w") as f:
            for i, clip in enumerate(video_clips):
                # Use absolute path for concat
                abs_path = os.path.abspath(clip['path'])
                
                # Verify clip exists and get actual duration
                if os.path.exists(abs_path):
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=noprint_wrappers=1:nokey=1', abs_path]
                    duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    actual_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0
                    total_expected_duration += actual_duration
                    logger.info(f"  Clip {i+1}: {actual_duration:.1f}s (expected: {clip.get('duration', 0)}s) - {os.path.basename(abs_path)}")
                    f.write(f"file '{abs_path}'\n")
                else:
                    logger.error(f"  Clip {i+1} NOT FOUND: {abs_path}")
        
        logger.info(f"📊 Total expected duration from clips: {total_expected_duration:.1f}s")
        
        # Output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"scraped_media_video_{style}_{timestamp}.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # FFmpeg concat command - use copy codec first to preserve duration
        width, height = self.dimensions
        
        # First try to concat with copy codec (fastest and preserves everything)
        cmd_copy = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_path
        ]
        
        # Try copy first
        logger.info("Attempting concat with copy codec...")
        result = subprocess.run(cmd_copy, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.info(f"Copy codec failed: {result.stderr[:200]}... Re-encoding...")
            # Fall back to re-encoding
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
            ]
            
            # Add style-specific final touches
            if style == "fast-paced" or "viral" in style.lower() or "breaking" in style.lower():
                # Modify the existing filter to include style effects
                # NOTE: Don't use setpts as it changes duration!
                cmd[-1] = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,eq=contrast=1.05:saturation=1.1"
            
            cmd.append(output_path)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        logger.info(f"✅ Concatenation completed")
        
        try:
            # Verify output duration
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                         '-of', 'default=noprint_wrappers=1:nokey=1', output_path]
            duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            output_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0
            logger.info(f"📹 Output video duration: {output_duration:.1f}s")
            
            # Clean up temp files
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to compose final video: {e}")
            if os.path.exists(concat_file):
                logger.error(f"Concat file preserved for debugging: {concat_file}")
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