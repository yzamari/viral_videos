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
                    all_media.append({
                        "asset": asset,
                        "item": item,
                        "url": asset.source_url
                    })
        
        logger.info(f"📸 Found {len(all_media)} media assets to download")
        
        # 2. Download all media
        downloaded_files = await self._download_all_media(all_media)
        
        if not downloaded_files:
            logger.warning("No media could be downloaded, creating text-only video")
            # Create text-only segments for ALL content items
            for i, item in enumerate(content_items):
                downloaded_files.append({
                    "path": None,
                    "type": "text",
                    "title": item.title,
                    "metadata": {"content": item.content, "index": i + 1, "total": len(content_items)}
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
        
        # Dynamic pacing based on content and platform
        # Each story gets appropriate time based on its complexity
        if self.platform == "tiktok":
            # TikTok: Very quick cuts, multiple media per story
            min_time_per_clip = 5.0  # Base time, but we'll use multiple shots
            shots_per_story = 3  # Multiple quick shots per story
        else:
            min_time_per_clip = 8.0  # Standard pacing
            shots_per_story = 2  # Fewer cuts for other platforms
        
        ideal_time_per_clip = total_duration / num_clips
        time_per_clip = max(min_time_per_clip, ideal_time_per_clip)
        
        # If we need more time, extend total duration
        actual_duration = time_per_clip * num_clips
        
        logger.info(f"📊 Creating {num_clips} clips, {time_per_clip:.1f}s each (total: {actual_duration:.1f}s)")
        
        # Process each media file
        for i, media in enumerate(downloaded_files[:num_clips]):
            logger.info(f"🎬 Processing clip {i+1}/{num_clips}: {media['type']} - {media.get('title', 'No title')[:50]}")
            
            if media["type"] == "text":
                # Create text video segment
                clip_path = await self._create_text_segment(
                    media["title"],
                    media.get("metadata", {}).get("content", ""),
                    time_per_clip,
                    style,
                    media.get("metadata", {})
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
        if visual_styles is None:
            visual_styles = {}
        
        # Create gradient background with modern design
        width, height = self.dimensions
        img = Image.new('RGB', (width, height))
        draw_temp = ImageDraw.Draw(img)
        
        # Create more vibrant gradient based on style
        if "news" in style.lower() or "breaking" in style.lower():
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
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    logger.info(f"Testing font: {font_path}")
                    # Dynamic font sizes based on platform
                    if self.platform == "tiktok":
                        font_title = ImageFont.truetype(font_path, 60)
                        font_content = ImageFont.truetype(font_path, 32)
                    else:
                        font_title = ImageFont.truetype(font_path, 80)
                        font_content = ImageFont.truetype(font_path, 42)
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
        
        # Adjust layout for different platforms
        if self.platform == "tiktok":
            # Portrait layout - position text in viewable area
            title_y = 600  # Move title lower to middle area
            content_y_start = 750  # Content below title
            overlay_width = int(width * 0.95)  # Wider for better text display
            overlay_x = (width - overlay_width) // 2
        else:
            # Landscape layout
            title_y = 225
            content_y_start = 400
            overlay_width = 1600
            overlay_x = 160
        
        # Add overlay background for title
        overlay = Image.new('RGBA', (overlay_width, 150), (0, 0, 0, 180))
        img.paste(overlay, (overlay_x, 150), overlay)
        
        # Draw title with proper alignment
        center_x = width // 2
        if is_rtl and RTL_SUPPORT:
            # Hebrew doesn't need reshaping, only bidi reordering
            if any('\u0590' <= char <= '\u05FF' for char in title):
                # Hebrew text - PIL handles it correctly, no need for bidi
                draw.text((center_x, title_y), title, fill=(255, 255, 255), font=font_title, anchor="ma")
            else:
                # Arabic text - needs reshaping and bidi
                reshaped_title = arabic_reshaper.reshape(title)
                bidi_title = get_display(reshaped_title)
                draw.text((center_x, title_y), bidi_title, fill=(255, 255, 255), font=font_title, anchor="ma")
        elif is_rtl:
            # Fallback for RTL without libraries
            draw.text((center_x, title_y), title[::-1], fill=(255, 255, 255), font=font_title, anchor="ma")
        else:
            draw.text((center_x, title_y), title, fill=(255, 255, 255), font=font_title, anchor="ma")
        
        # Draw content with modern styling
        if content:
            # Add semi-transparent overlay for content area
            if self.platform == "tiktok":
                content_overlay_width = int(width * 0.9)  # Wider overlay
                content_overlay_height = 1000  # Taller overlay for more text
                content_overlay_x = (width - content_overlay_width) // 2
                content_overlay_y = 380  # Start higher to fit more content
            else:
                content_overlay_width = 1400
                content_overlay_height = 600
                content_overlay_x = 260
                content_overlay_y = 350
            
            content_overlay = Image.new('RGBA', (content_overlay_width, content_overlay_height), (0, 0, 0, 120))
            img.paste(content_overlay, (content_overlay_x, content_overlay_y), content_overlay)
            
            # Better text wrapping for different languages
            if is_rtl:
                # RTL languages need special handling - wider for more content
                lines = content.split('\n') if '\n' in content else textwrap.wrap(content, width=50)
            else:
                lines = textwrap.wrap(content, width=70)
            
            y_offset = content_y_start
            line_spacing = 45 if self.platform == "tiktok" else 55
            # Increase max lines to show more content
            max_lines = 16 if self.platform == "tiktok" else 14
            
            for line in lines[:max_lines]:
                if is_rtl and RTL_SUPPORT:
                    # Hebrew doesn't need reshaping, only bidi reordering
                    if any('\u0590' <= char <= '\u05FF' for char in line):
                        # Hebrew text - PIL handles it correctly, no need for bidi
                        draw.text((center_x, y_offset), line, fill=(240, 240, 240), font=font_content, anchor="ma")
                    else:
                        # Arabic text - needs reshaping and bidi
                        reshaped_line = arabic_reshaper.reshape(line)
                        bidi_line = get_display(reshaped_line)
                        draw.text((center_x, y_offset), bidi_line, fill=(240, 240, 240), font=font_content, anchor="ma")
                elif is_rtl:
                    draw.text((center_x, y_offset), line[::-1], fill=(240, 240, 240), font=font_content, anchor="ma")
                else:
                    draw.text((center_x, y_offset), line, fill=(240, 240, 240), font=font_content, anchor="ma")
                y_offset += line_spacing
        
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
                # Show channel name
                channel_font = ImageFont.truetype(font_paths[0], 36) if font_paths[0] and os.path.exists(font_paths[0]) else font
                draw.text((width - 50, 50), self.channel_name, fill=(255, 255, 255, 255), font=channel_font, anchor="ra")
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
            logger.info("Copy codec failed, re-encoding...")
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
                cmd[-1] = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,setpts=0.95*PTS,eq=contrast=1.05:saturation=1.1"
            
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