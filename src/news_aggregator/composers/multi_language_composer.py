"""Multi-Language News Video Composer"""

import os
import subprocess
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...utils.logging_config import get_logger
from ...utils.session_manager import SessionManager
from ...ai.manager import AIServiceManager
from ..models.content_models import ContentItem
from .scraped_media_composer import ScrapedMediaComposer

logger = get_logger(__name__)


class MultiLanguageComposer:
    """Creates news videos in multiple languages with platform-specific formatting"""
    
    # Platform specifications
    PLATFORM_SPECS = {
        'youtube': {
            'resolution': '1920x1080',
            'aspect_ratio': '16:9',
            'max_duration': 600,  # 10 minutes
            'fps': 30,
            'bitrate': '8M'
        },
        'tiktok': {
            'resolution': '1080x1920',
            'aspect_ratio': '9:16',
            'max_duration': 60,
            'fps': 30,
            'bitrate': '6M'
        },
        'instagram': {
            'resolution': '1080x1080',
            'aspect_ratio': '1:1',
            'max_duration': 60,
            'fps': 30,
            'bitrate': '6M'
        },
        'twitter': {
            'resolution': '1280x720',
            'aspect_ratio': '16:9',
            'max_duration': 140,
            'fps': 30,
            'bitrate': '5M'
        }
    }
    
    def __init__(
        self,
        session_manager: SessionManager,
        ai_manager: AIServiceManager,
        scraped_media_composer: ScrapedMediaComposer
    ):
        self.session_manager = session_manager
        self.ai_manager = ai_manager
        self.scraped_media_composer = scraped_media_composer
    
    async def create_news_video(
        self,
        content_items: List[ContentItem],
        language: str,
        style: str,
        tone: str,
        platform: str,
        duration_seconds: int,
        overlay_style: str,
        output_filename: Optional[str] = None,
        visual_styles: Dict[str, Any] = None,
        use_youtube_videos: bool = False,
        logo_path: str = None,
        channel_name: str = "NEWS",
        dynamic_transitions: bool = True
    ) -> str:
        """Create news video for specific language and platform"""
        
        logger.info(f"🎬 Creating {language} news video for {platform}")
        
        # Get platform specs
        specs = self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS['youtube'])
        
        # Adjust duration for platform limits
        actual_duration = min(duration_seconds, specs['max_duration'])
        
        # Translate content if needed
        # Check the actual language of the content first
        if content_items and content_items[0].title:
            has_hebrew = any('\u0590' <= char <= '\u05FF' for char in content_items[0].title)
            content_language = 'he' if has_hebrew else 'en'
            
            if language == content_language:
                logger.info(f"✅ Content already in {language}, skipping translation")
            elif language == 'en' and has_hebrew:
                logger.info(f"🌐 Translating Hebrew content to English")
                content_items = await self._translate_content(content_items, 'en')
            elif language != 'en' and not has_hebrew:
                logger.info(f"🌐 Translating English content to {language}")
                content_items = await self._translate_content(content_items, language)
            else:
                logger.info(f"✅ No translation needed")
        
        # Note: Dark humor tone is now applied directly in AI agent prompts, not as separate transformation
        
        # Update scraped_media_composer with new parameters
        logger.info(f"🎬 Setting channel name: {channel_name}")
        logger.info(f"🎨 Visual styles: {visual_styles}")
        self.scraped_media_composer.visual_styles = visual_styles
        self.scraped_media_composer.logo_path = logo_path
        self.scraped_media_composer.channel_name = channel_name
        self.scraped_media_composer.dynamic_transitions = dynamic_transitions
        
        # Create base video with scraped media
        base_video = await self.scraped_media_composer.create_video_from_scraped_media(
            content_items=content_items,
            duration_seconds=actual_duration,
            style=self._map_style_to_video_style(style, tone),
            output_filename=f"temp_base_{language}.mp4",
            platform=platform
        )
        
        # Check base video duration
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                     '-of', 'default=noprint_wrappers=1:nokey=1', base_video]
        duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        base_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0
        logger.info(f"📹 Base video duration: {base_duration:.1f}s (expected: {actual_duration}s)")
        
        # Apply platform-specific formatting
        formatted_video = await self._apply_platform_formatting(
            base_video,
            platform,
            specs
        )
        
        # Add language-specific overlays
        final_video = await self._add_language_overlays(
            formatted_video,
            content_items,
            language,
            overlay_style,
            platform,
            channel_name
        )
        
        # Final output
        if not output_filename:
            output_filename = f"news_{language}_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        # Get session directory
        session_dir = self.session_manager.session_data.get('session_dir', 'outputs')
        output_path = os.path.join(session_dir, output_filename)
        
        # Move final video to output path
        subprocess.run([
            'ffmpeg', '-y', '-i', final_video,
            '-c', 'copy', output_path
        ], capture_output=True)
        
        # Cleanup temp files
        for temp_file in [base_video, formatted_video, final_video]:
            if os.path.exists(temp_file) and temp_file != output_path:
                os.remove(temp_file)
        
        logger.info(f"✅ Created {language} video for {platform}: {output_path}")
        
        return output_path
    
    async def _translate_content(
        self,
        content_items: List[ContentItem],
        target_language: str
    ) -> List[ContentItem]:
        """Translate content items to target language"""
        
        # Don't skip - always translate when this method is called
        # The decision to translate is made in create_video method
        
        logger.info(f"🌐 Translating content to {target_language}")
        
        language_map = {
            'he': 'Hebrew',
            'ru': 'Russian',
            'ar': 'Arabic',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese'
        }
        
        translated_items = []
        
        for item in content_items:
            # Create translation prompt
            prompt = f"""Translate the following news content to {language_map.get(target_language, target_language)}.
Keep the translation natural and appropriate for news broadcasting.

Title: {item.title}
Content: {item.content[:500]}

Provide the translation in this format:
TITLE: [translated title]
CONTENT: [translated content]"""
            
            try:
                # Use the AI manager's proper method
                response = await self.ai_manager.generate_content_async(
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                # Parse response
                lines = response.split('\n')
                translated_title = item.title  # fallback
                translated_content = item.content  # fallback
                
                for line in lines:
                    if line.startswith('TITLE:'):
                        translated_title = line.replace('TITLE:', '').strip()
                    elif line.startswith('CONTENT:'):
                        translated_content = line.replace('CONTENT:', '').strip()
                
                # Create translated item
                translated_item = ContentItem(
                    id=item.id,
                    source=item.source,
                    title=translated_title,
                    content=translated_content,
                    categories=item.categories,
                    media_assets=item.media_assets,
                    relevance_score=item.relevance_score,
                    metadata={**item.metadata, 'original_language': 'en', 'translated_to': target_language}
                )
                
                translated_items.append(translated_item)
                
            except Exception as e:
                logger.warning(f"Translation failed for item: {e}")
                translated_items.append(item)  # Use original
        
        return translated_items
    
    async def _apply_platform_formatting(
        self,
        input_video: str,
        platform: str,
        specs: Dict[str, Any]
    ) -> str:
        """Apply platform-specific video formatting"""
        
        output_video = input_video.replace('.mp4', f'_{platform}.mp4')
        
        # Get input video duration to preserve it
        import subprocess
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                     '-of', 'default=noprint_wrappers=1:nokey=1', input_video]
        duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        video_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else None
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y', '-i', input_video]
        
        # Platform-specific filters
        if platform == 'tiktok':
            # Vertical format with padding
            cmd.extend([
                '-vf', f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
                '-r', str(specs['fps'])
            ])
        elif platform == 'instagram':
            # Square format with padding
            cmd.extend([
                '-vf', f"scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
                '-r', str(specs['fps'])
            ])
        else:
            # Standard horizontal format
            cmd.extend([
                '-vf', f"scale={specs['resolution']}:force_original_aspect_ratio=decrease,pad={specs['resolution'].replace('x', ':')}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                '-r', str(specs['fps'])
            ])
        
        # Output settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-b:v', specs['bitrate'],
            '-c:a', 'aac',
            '-b:a', '128k'
        ])
        
        # Preserve duration if we know it
        if video_duration:
            cmd.extend(['-t', str(video_duration)])
            
        cmd.append(output_video)
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return output_video
    
    async def _add_language_overlays(
        self,
        input_video: str,
        content_items: List[ContentItem],
        language: str,
        overlay_style: str,
        platform: str,
        channel_name: str = None
    ) -> str:
        """Add language-specific overlays and text"""
        
        # Add news channel overlay if channel name is set
        if channel_name and "news" in overlay_style.lower():
            return await self._add_news_channel_overlay(
                input_video, 
                channel_name,
                language,
                platform
            )
        
        return input_video
    
    async def _add_news_channel_overlay(
        self,
        input_video: str,
        channel_name: str,
        language: str,
        platform: str
    ) -> str:
        """Add professional news channel overlay with logo and ticker"""
        
        import tempfile
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create output path
        output_video = input_video.replace('.mp4', '_with_overlay.mp4')
        
        # Get video dimensions
        probe_cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            input_video
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        width, height = map(int, result.stdout.strip().split('x'))
        
        # Create news overlay image
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Top banner for channel name (semi-transparent)
        banner_height = int(height * 0.08)
        draw.rectangle(
            [(0, 0), (width, banner_height)],
            fill=(10, 10, 10, 220)  # Dark semi-transparent
        )
        
        # Add gradient effect
        for i in range(10):
            alpha = int(220 - i * 15)
            if alpha > 0 and banner_height - i - 1 >= 0:
                draw.rectangle(
                    [(0, banner_height - i - 1), (width, banner_height - i)],
                    fill=(10, 10, 10, alpha)
                )
        
        # Bottom ticker area
        ticker_height = int(height * 0.12)
        ticker_y = height - ticker_height
        
        # Ticker background with gradient
        for i in range(20):
            alpha = int(i * 11)
            draw.rectangle(
                [(0, ticker_y + i), (width, ticker_y + i + 1)],
                fill=(10, 10, 10, alpha)
            )
        draw.rectangle(
            [(0, ticker_y + 20), (width, height)],
            fill=(10, 10, 10, 220)
        )
        
        # Add red accent line
        draw.rectangle(
            [(0, ticker_y), (width, ticker_y + 3)],
            fill=(200, 30, 30, 255)  # Red accent
        )
        
        # Try to use a good font
        font_size = int(banner_height * 0.6)
        ticker_font_size = int(ticker_height * 0.3)
        
        try:
            # Try system fonts
            if language == 'he':
                font_path = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
            else:
                font_path = '/System/Library/Fonts/Helvetica.ttc'
            
            font = ImageFont.truetype(font_path, font_size)
            ticker_font = ImageFont.truetype(font_path, ticker_font_size)
        except:
            font = ImageFont.load_default()
            ticker_font = ImageFont.load_default()
        
        # Add channel name
        text_bbox = draw.textbbox((0, 0), channel_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        text_y = (banner_height - font_size) // 2
        
        # Add text with shadow effect
        draw.text((text_x + 2, text_y + 2), channel_name, fill=(0, 0, 0, 180), font=font)
        draw.text((text_x, text_y), channel_name, fill=(255, 255, 255, 255), font=font)
        
        # Add "BREAKING NEWS" or similar text in ticker
        if language == 'he':
            ticker_text = "חדשות דחופות • מהדורה מיוחדת"
        else:
            ticker_text = "BREAKING NEWS • SPECIAL EDITION"
        
        draw.text((20, ticker_y + 25), ticker_text, fill=(255, 255, 255, 255), font=ticker_font)
        
        # Add live indicator
        live_text = "● LIVE" if language != 'he' else "● שידור חי"
        draw.text((width - 150, 15), live_text, fill=(255, 50, 50, 255), font=ticker_font)
        
        # Save overlay image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            overlay.save(tmp.name, 'PNG')
            overlay_path = tmp.name
        
        # Apply overlay using FFmpeg
        cmd = [
            'ffmpeg', '-y',
            '-i', input_video,
            '-i', overlay_path,
            '-filter_complex', '[0:v][1:v]overlay=0:0',
            '-c:a', 'copy',
            '-c:v', 'libx264',
            '-preset', 'fast',
            output_video
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        # Clean up temp file
        os.unlink(overlay_path)
        
        logger.info(f"✅ Added news channel overlay: {channel_name}")
        return output_video
    
    def _map_style_to_video_style(self, style: str, tone: str) -> str:
        """Map free-form style/tone to video style"""
        
        # AI could help here, but for now use keywords
        combined = f"{style} {tone}".lower()
        
        if any(word in combined for word in ['dark', 'comedy', 'satirical', 'satire', 'humor', 'humorous', 'onion']):
            return 'dark_humor'
        elif any(word in combined for word in ['fast', 'energetic', 'viral', 'trending']):
            return 'fast-paced'
        elif any(word in combined for word in ['dramatic', 'serious', 'breaking']):
            return 'dramatic'
        else:
            return 'normal'