"""
NewsAggregatorOrchestrator - Coordinates the entire news aggregation workflow.

This class acts as the main orchestrator, coordinating between content collection,
processing, and video composition while maintaining session management and reporting.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..interfaces.aggregator_interfaces import (
    IAggregatorOrchestrator, ISessionReporter, IContentConverter
)
from ..collectors.content_collector import NewsContentCollector
from ..processors.content_processor import NewsContentProcessor
from ..composers.video_composer import NewsVideoComposer
from ..models.content_models import ContentItem, MediaAsset, AssetType, NewsSource, SourceType
from ..utils.logging_config import get_logger
from ..utils.session_manager import SessionManager
from ..ai.manager import AIServiceManager
from ..core.decision_framework import DecisionFramework

logger = get_logger(__name__)


class NewsAggregatorOrchestrator(IAggregatorOrchestrator, ISessionReporter, IContentConverter):
    """
    Main orchestrator that coordinates all components of the news aggregation system.
    
    Responsibilities:
    - Workflow orchestration between all components
    - Session management and initialization
    - Component dependency injection
    - Session reporting and data export
    - Content format conversion utilities
    """
    
    def __init__(
        self,
        enable_discussions: bool = True,
        discussion_log: bool = False
    ):
        """
        Initialize the orchestrator with configuration options.
        
        Args:
            enable_discussions: Whether to enable AI discussions
            discussion_log: Whether to enable detailed discussion logging
        """
        self.enable_discussions = enable_discussions
        self.discussion_log = discussion_log
        
        # Core system components
        self.session_manager = SessionManager()
        self.ai_manager = AIServiceManager()
        
        # Components will be initialized after session creation
        self.decision_framework = None
        self.content_collector = None
        self.content_processor = None
        self.video_composer = None
    
    async def aggregate_news(
        self,
        sources: List[str],
        csv_file: Optional[str] = None,
        languages: List[str] = ['en'],
        style: str = "professional",
        tone: str = "informative",
        platform: str = "youtube",
        duration_seconds: int = 60,
        max_stories: int = 10,
        enable_ai_discussion: bool = True,
        discussion_log: bool = False,
        overlay_style: str = "modern",
        output_dir: str = "outputs/news",
        hours_back: int = 24,
        telegram_channels: List[str] = [],
        use_youtube_videos: bool = False,
        logo_path: str = None,
        channel_name: str = "NEWS",
        dynamic_transitions: bool = True
    ) -> Dict[str, str]:
        """
        Main aggregation method that orchestrates the entire workflow.
        
        Returns:
            Dict mapping language to output video path
        """
        logger.info("🎬 Enhanced News Aggregator Starting")
        logger.info(f"📰 Sources: {sources}")
        logger.info(f"🌐 Languages: {languages}")
        logger.info(f"🎨 Style: {style}, Tone: {tone}")
        logger.info(f"📱 Platform: {platform}")
        logger.info(f"📺 Channel Name: {channel_name}")
        
        # 1. Initialize session and components
        session_id = await self._initialize_session_and_components(
            sources, platform, duration_seconds, enable_ai_discussion
        )
        
        # 2. Collect all content from various sources
        all_content = await self._collect_all_content(
            sources, csv_file, hours_back, telegram_channels
        )
        
        if not all_content:
            raise ValueError("No content found from any source!")
        
        logger.info(f"📊 Collected {len(all_content)} total items")
        
        # 3. Process content (analyze, deduplicate, select)
        processed_content = await self._process_content(
            all_content, style, tone, platform, max_stories, 
            enable_ai_discussion, discussion_log
        )
        
        logger.info(f"✅ Selected {len(processed_content)} stories for final video")
        
        # 4. Download media assets
        media_enhanced_content = await self.video_composer.download_all_media(
            processed_content, use_youtube_videos
        )
        
        # 5. Create videos for each language
        output_videos = await self._create_videos_for_languages(
            media_enhanced_content, languages, style, tone, platform,
            duration_seconds, overlay_style, output_dir, use_youtube_videos,
            logo_path, channel_name, dynamic_transitions
        )
        
        # 6. Generate session reports and exports
        self._save_session_report(media_enhanced_content, output_videos, style, tone)
        self._export_to_csv(media_enhanced_content)
        
        return output_videos
    
    async def _initialize_session_and_components(
        self, 
        sources: List[str], 
        platform: str, 
        duration_seconds: int, 
        enable_ai_discussion: bool
    ) -> str:
        """Initialize session and dependency-inject components"""
        from ..utils.session_context import SessionContext
        
        # Create session
        session_id = self.session_manager.create_session(
            mission=f"News aggregation from {len(sources)} sources",
            platform=platform,
            duration=duration_seconds,
            category="news"
        )
        
        # Create session context
        session_context = SessionContext(
            session_id=session_id,
            session_manager_instance=self.session_manager
        )
        
        # Initialize decision framework
        self.decision_framework = DecisionFramework(session_context)
        
        # Initialize components with dependency injection
        self.content_collector = NewsContentCollector()
        
        self.content_processor = NewsContentProcessor(
            ai_manager=self.ai_manager,
            decision_framework=self.decision_framework,
            enable_ai_discussions=enable_ai_discussion
        )
        
        self.video_composer = NewsVideoComposer(
            session_manager=self.session_manager,
            ai_manager=self.ai_manager
        )
        
        return session_id
    
    async def _collect_all_content(
        self,
        sources: List[str],
        csv_file: Optional[str],
        hours_back: int,
        telegram_channels: List[str]
    ) -> List[Dict[str, Any]]:
        """Orchestrate content collection from all sources"""
        all_content = []
        
        # Collect from web sources
        web_content = await self.content_collector.collect_from_sources(sources, hours_back)
        all_content.extend(web_content)
        
        # Collect from CSV if provided
        if csv_file:
            csv_content = await self.content_collector.collect_from_csv(csv_file)
            all_content.extend(csv_content)
        
        # Collect from Telegram channels
        if telegram_channels:
            telegram_content = await self.content_collector.collect_from_telegram(
                telegram_channels, hours_back
            )
            all_content.extend(telegram_content)
        
        return all_content
    
    async def _process_content(
        self,
        all_content: List[Dict[str, Any]],
        style: str,
        tone: str,
        platform: str,
        max_stories: int,
        enable_ai_discussion: bool,
        discussion_log: bool
    ) -> List[Dict[str, Any]]:
        """Orchestrate content processing pipeline"""
        # 1. Analyze content for metadata and relevance
        analyzed_content = await self.content_processor.analyze_content(all_content)
        
        # 2. Detect and merge duplicates
        unique_content = await self.content_processor.detect_and_merge_duplicates(
            analyzed_content
        )
        logger.info(f"🔍 After duplicate detection: {len(unique_content)} unique stories")
        
        # 3. Select content using AI discussions or simple selection
        if enable_ai_discussion:
            selected_content = await self.content_processor.run_ai_discussions(
                unique_content, style, tone, platform, max_stories, discussion_log
            )
            
            # Save discussion log if enabled
            if discussion_log and hasattr(self.content_processor, 'orchestrator'):
                # This would require passing the discussion result, 
                # but we'll implement this in the processor itself
                pass
        else:
            selected_content = self.content_processor.select_content_simple(
                unique_content, max_stories
            )
        
        return selected_content
    
    async def _create_videos_for_languages(
        self,
        content: List[Dict[str, Any]],
        languages: List[str],
        style: str,
        tone: str,
        platform: str,
        duration_seconds: int,
        overlay_style: str,
        output_dir: str,
        use_youtube_videos: bool,
        logo_path: str,
        channel_name: str,
        dynamic_transitions: bool
    ) -> Dict[str, str]:
        """Create videos for all specified languages"""
        output_videos = {}
        
        # Get visual styles from AI if processor has orchestrator
        visual_styles = {}
        if (hasattr(self.content_processor, 'orchestrator') and 
            self.content_processor.orchestrator):
            try:
                visual_styles = await self.content_processor.orchestrator.select_visual_styles(
                    style, tone, platform, languages[0]
                )
                logger.info(f"🎨 AI selected visual styles: {visual_styles}")
            except Exception as e:
                logger.warning(f"Failed to get AI visual styles: {e}")
        
        # Create video for each language
        for language in languages:
            logger.info(f"🎥 Creating video for language: {language}")
            
            output_path = await self.video_composer.create_language_video(
                content=content,
                language=language,
                style=style,
                tone=tone,
                platform=platform,
                duration_seconds=duration_seconds,
                overlay_style=overlay_style,
                output_dir=output_dir,
                visual_styles=visual_styles,
                use_youtube_videos=use_youtube_videos,
                logo_path=logo_path,
                channel_name=channel_name,
                dynamic_transitions=dynamic_transitions
            )
            
            output_videos[language] = output_path
            logger.info(f"✅ Created {language} video: {output_path}")
        
        return output_videos
    
    def save_discussion_log(self, discussion_result: Dict[str, Any]) -> None:
        """Save AI discussion log to session directory"""
        session_dir = self.session_manager.session_data.get('session_dir', 'outputs')
        log_path = os.path.join(session_dir, 'ai_discussion_log.json')
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(discussion_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💬 AI discussion log saved: {log_path}")
        except Exception as e:
            logger.error(f"Failed to save discussion log: {e}")
    
    def save_session_report(
        self,
        content: List[Dict[str, Any]],
        output_videos: Dict[str, str],
        style: str,
        tone: str
    ) -> None:
        """Save comprehensive session report"""
        self._save_session_report(content, output_videos, style, tone)
    
    def export_to_csv(self, content: List[Dict[str, Any]]) -> None:
        """Export scraped articles to CSV format"""
        self._export_to_csv(content)
    
    def _save_session_report(
        self,
        content: List[Dict[str, Any]],
        output_videos: Dict[str, str],
        style: str,
        tone: str
    ) -> None:
        """Internal method to save session report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'style': style,
            'tone': tone,
            'total_stories': len(content),
            'output_videos': output_videos,
            'stories': []
        }
        
        # Compile story information
        for item in content:
            report['stories'].append({
                'title': item['title'],
                'sources': item.get('sources', [item['source']]),
                'has_image': bool(item.get('local_image')),
                'has_video': bool(item.get('local_video')),
                'has_youtube': bool(item.get('youtube_video')),
                'ai_reasoning': item.get('ai_reasoning', ''),
                'priority': item.get('priority', 0.5),
                'credibility_score': item.get('credibility_score', 0.0)
            })
        
        # Save report to session directory
        session_dir = self.session_manager.session_data.get('session_dir', 'outputs')
        report_path = os.path.join(session_dir, 'news_aggregation_report.json')
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Session report saved: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save session report: {e}")
    
    def _export_to_csv(self, content: List[Dict[str, Any]]) -> None:
        """Export scraped articles to CSV format"""
        import csv
        
        session_dir = self.session_manager.session_data.get('session_dir', 'outputs')
        csv_path = os.path.join(session_dir, 'scraped_articles.csv')
        
        # Prepare CSV data
        csv_data = []
        for item in content:
            # Collect all media URLs
            media_urls = []
            
            # Add images
            if item.get('article_images'):
                media_urls.extend(item['article_images'])
            elif item.get('image_url'):
                media_urls.append(item['image_url'])
                
            # Add videos  
            if item.get('article_videos'):
                media_urls.extend(item['article_videos'])
            elif item.get('video_url'):
                media_urls.append(item['video_url'])
            
            media_links = ','.join(media_urls) if media_urls else ''
            
            csv_data.append({
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'source': item.get('source', ''),
                'url': item.get('url', ''),
                'category': item.get('category', ''),
                'media_links': media_links,
                'priority': item.get('priority', 0.5),
                'credibility_score': item.get('credibility_score', 0.0),
                'ai_reasoning': item.get('ai_reasoning', '')
            })
        
        # Write CSV file
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'title', 'content', 'source', 'url', 'category', 
                    'media_links', 'priority', 'credibility_score', 'ai_reasoning'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(csv_data)
            
            logger.info(f"📊 Articles exported to CSV: {csv_path}")
            logger.info(f"📄 Exported {len(csv_data)} articles with media links")
            
        except Exception as e:
            logger.error(f"❌ Failed to export CSV: {e}")
    
    def content_item_to_dict(self, item: ContentItem) -> Dict[str, Any]:
        """Convert ContentItem to dict format"""
        return {
            'title': item.title,
            'content': item.content,
            'url': item.source.url if item.source else '',
            'source': item.source.name if item.source else 'Unknown',
            'image_url': next(
                (asset.source_url for asset in item.media_assets 
                 if asset.asset_type == AssetType.IMAGE), ''
            ),
            'video_url': next(
                (asset.source_url for asset in item.media_assets 
                 if asset.asset_type == AssetType.VIDEO), ''
            ),
            'categories': item.categories,
            'priority': item.relevance_score,
            'metadata': item.metadata
        }
    
    def dict_to_content_item(self, data: Dict[str, Any]) -> ContentItem:
        """Convert dict to ContentItem format - delegated to video composer"""
        return self.video_composer._dict_to_content_item(data)