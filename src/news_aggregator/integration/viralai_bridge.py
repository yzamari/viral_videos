"""Bridge to integrate with existing ViralAI components"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

# Add parent directory to path to import ViralAI components
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ...utils.logging_config import get_logger
from ...utils.session_manager import SessionManager
from ...ai.manager import AIServiceManager
from ...ai.interfaces.base import AIServiceType
from ...core.decision_framework import DecisionFramework, CoreDecisions, Decision, DecisionSource
from ...models.video_models import Platform, VideoCategory, Language
from ...generators.subtitle_generator import SubtitleGenerator
from ...infrastructure.services.existing_video_generation_service import ExistingVideoGenerationService
from ...infrastructure.services.existing_audio_generation_service import ExistingAudioGenerationService
from ...config.video_config import video_config

logger = get_logger(__name__)


class ViralAIBridge:
    """Bridge to use existing ViralAI components for news video generation"""
    
    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        ai_manager: Optional[AIServiceManager] = None,
        output_dir: str = "outputs/news_videos"
    ):
        # Initialize managers
        self.session_manager = session_manager or SessionManager(base_output_dir=output_dir)
        self.ai_manager = ai_manager or AIServiceManager()
        self.decision_framework = DecisionFramework()
        
        # Initialize services
        self.video_service = ExistingVideoGenerationService(
            ai_manager=self.ai_manager,
            decision_framework=self.decision_framework
        )
        self.audio_service = ExistingAudioGenerationService(
            ai_manager=self.ai_manager,
            decision_framework=self.decision_framework
        )
        self.subtitle_generator = SubtitleGenerator()
        
        logger.info("ViralAI Bridge initialized")
    
    async def create_news_session(
        self,
        channel_name: str,
        episode_title: str,
        language: str = "en"
    ) -> str:
        """Create a session for news video generation"""
        # Map language to ViralAI Language enum
        lang_map = {
            "en": Language.ENGLISH,
            "he": Language.HEBREW,
            "es": Language.SPANISH,
            "fr": Language.FRENCH
        }
        
        # Create session with news-specific parameters
        session_id = self.session_manager.create_session(
            mission=f"{channel_name}: {episode_title}",
            platform="youtube",  # Default to YouTube format
            duration=300,  # 5 minutes default
            category="news"
        )
        
        # Create core decisions for the session
        decisions = CoreDecisions(
            mission=f"{channel_name}: {episode_title}",
            platform=Platform.YOUTUBE,
            video_category=VideoCategory.NEWS,
            duration=300,
            language=lang_map.get(language, Language.ENGLISH),
            style="professional",
            ai_mode="enhanced",
            music_style="news_background",
            subtitle_style="news_ticker"
        )
        
        # Store decisions in framework
        self.decision_framework.decisions = decisions
        
        logger.info(f"Created news session: {session_id}")
        return session_id
    
    async def generate_audio_narration(
        self,
        text: str,
        language: str = "en",
        voice_style: str = "news_anchor",
        output_path: Optional[str] = None
    ) -> str:
        """Generate audio narration using existing TTS service"""
        try:
            # Prepare audio parameters
            audio_params = {
                "text": text,
                "language": language,
                "voice": self._get_voice_for_style(voice_style, language),
                "speaking_rate": 1.0 if voice_style == "news_anchor" else 1.1
            }
            
            # Generate audio
            audio_path = await self.audio_service.generate_audio(
                text=text,
                voice_params=audio_params,
                output_path=output_path
            )
            
            logger.info(f"Generated narration audio: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Failed to generate audio narration: {str(e)}")
            raise
    
    async def generate_video_segment(
        self,
        prompt: str,
        duration: float = 5.0,
        existing_media_path: Optional[str] = None,
        use_veo3_fast: bool = True
    ) -> str:
        """Generate or process video segment"""
        try:
            if existing_media_path and os.path.exists(existing_media_path):
                # Process existing media
                logger.info(f"Using existing media: {existing_media_path}")
                # TODO: Add video processing (crop, resize, effects)
                return existing_media_path
            
            # Generate new video using VEO-3
            if use_veo3_fast:
                # Use fast generation for news content
                video_path = await self.video_service.generate_video_veo3_fast(
                    prompt=prompt,
                    duration=duration
                )
            else:
                # Use standard generation
                video_path = await self.video_service.generate_video(
                    prompt=prompt,
                    duration=duration
                )
            
            logger.info(f"Generated video segment: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Failed to generate video segment: {str(e)}")
            raise
    
    async def generate_subtitles(
        self,
        audio_path: str,
        text: str,
        language: str = "en",
        style: str = "news_lower_third"
    ) -> str:
        """Generate subtitles using existing subtitle generator"""
        try:
            # Configure subtitle style for news
            subtitle_config = {
                "font_size": 32 if style == "news_lower_third" else 28,
                "font_color": "white",
                "background_color": "rgba(0,0,0,0.7)",
                "position": "bottom" if style == "news_lower_third" else "center",
                "margin": 50
            }
            
            # Generate subtitles
            subtitle_path = self.subtitle_generator.generate(
                audio_path=audio_path,
                text=text,
                language=language,
                config=subtitle_config
            )
            
            logger.info(f"Generated subtitles: {subtitle_path}")
            return subtitle_path
            
        except Exception as e:
            logger.error(f"Failed to generate subtitles: {str(e)}")
            raise
    
    async def summarize_content(
        self,
        content: str,
        max_length: int = 200,
        language: str = "en"
    ) -> str:
        """Summarize content using AI text service"""
        try:
            # Create summarization prompt
            prompt = f"""
            Summarize the following news content in {max_length} words or less.
            Make it suitable for news broadcast narration.
            Language: {language}
            
            Content:
            {content}
            
            Summary:
            """
            
            # Get text service
            text_service = self.ai_manager.get_text_service()
            
            # Generate summary
            summary = await text_service.generate(prompt)
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize content: {str(e)}")
            raise
    
    async def translate_content(
        self,
        content: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate content between languages"""
        try:
            # Skip if same language
            if source_lang == target_lang:
                return content
            
            # Create translation prompt
            lang_names = {
                "en": "English",
                "he": "Hebrew",
                "es": "Spanish",
                "fr": "French"
            }
            
            prompt = f"""
            Translate the following text from {lang_names.get(source_lang, source_lang)} 
            to {lang_names.get(target_lang, target_lang)}.
            Maintain the news reporting style and tone.
            
            Text:
            {content}
            
            Translation:
            """
            
            # Get text service
            text_service = self.ai_manager.get_text_service()
            
            # Generate translation
            translation = await text_service.generate(prompt)
            
            return translation.strip()
            
        except Exception as e:
            logger.error(f"Failed to translate content: {str(e)}")
            raise
    
    def _get_voice_for_style(self, style: str, language: str) -> str:
        """Get appropriate voice ID for style and language"""
        voice_map = {
            "en": {
                "news_anchor": "en-US-News-M",  # Professional male news voice
                "casual": "en-US-Standard-J",
                "female_anchor": "en-US-News-K"  # Professional female news voice
            },
            "he": {
                "news_anchor": "he-IL-Standard-A",  # Hebrew male voice
                "casual": "he-IL-Standard-B",
                "female_anchor": "he-IL-Standard-C"  # Hebrew female voice
            }
        }
        
        return voice_map.get(language, {}).get(style, "en-US-Standard-J")
    
    def get_video_config(self) -> Dict[str, Any]:
        """Get video configuration from existing config"""
        return {
            "resolution": (video_config.DEFAULT_WIDTH, video_config.DEFAULT_HEIGHT),
            "fps": video_config.DEFAULT_FPS,
            "bitrate": "5M",
            "codec": "libx264",
            "format": "mp4"
        }
    
    async def compose_final_video(
        self,
        segments: List[Dict[str, str]],
        audio_tracks: List[str],
        subtitles: List[str],
        output_path: str,
        theme_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Compose final video from segments"""
        try:
            # This would use existing video composition logic
            # For now, returning a placeholder
            logger.info(f"Composing final video with {len(segments)} segments")
            
            # TODO: Implement actual video composition using existing tools
            # - Merge video segments
            # - Add audio tracks
            # - Apply subtitles
            # - Add theme overlays
            # - Apply transitions
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to compose final video: {str(e)}")
            raise