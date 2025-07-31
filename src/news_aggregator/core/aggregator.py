"""Main News Aggregator Engine"""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import uuid

from ...utils.logging_config import get_logger
from ...utils.session_manager import SessionManager
from ...ai.manager import AIServiceManager
from ...core.decision_framework import DecisionFramework, DecisionSource

from ..models.content_models import (
    ContentItem, ContentCollection, NewsSource, ContentStatus
)
from ..models.aggregation_models import (
    ChannelConfig, AggregationSession, AggregationRule
)
from ..models.composition_models import CompositionProject

from .scraper_manager import ScraperManager
from .content_processor import ContentProcessor
from .composition_engine import CompositionEngine

logger = get_logger(__name__)


class NewsAggregator:
    """Main news aggregation and video creation engine"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        ai_manager: AIServiceManager,
        decision_framework: DecisionFramework
    ):
        self.session_manager = session_manager
        self.ai_manager = ai_manager
        self.decision_framework = decision_framework
        
        # Initialize components
        self.scraper_manager = ScraperManager()
        self.content_processor = ContentProcessor(ai_manager)
        self.composition_engine = CompositionEngine(
            session_manager,
            ai_manager,
            decision_framework
        )
        
        # Active sessions
        self.active_sessions: Dict[str, AggregationSession] = {}
    
    async def run_channel(self, channel_config: ChannelConfig) -> AggregationSession:
        """Run aggregation for a channel"""
        # Create session
        session = AggregationSession(
            id=str(uuid.uuid4()),
            channel_id=channel_config.id
        )
        self.active_sessions[session.id] = session
        
        try:
            session.add_log("info", f"Starting aggregation for channel: {channel_config.name}")
            
            # Phase 1: Content Scraping
            content_items = await self._scrape_content(channel_config, session)
            session.total_items_scraped = len(content_items)
            
            # Phase 2: Content Processing & Filtering
            processed_items = await self._process_content(
                content_items, 
                channel_config, 
                session
            )
            session.items_after_filtering = len(processed_items)
            
            # Phase 3: Content Selection & Organization
            selected_items = self._select_content(
                processed_items,
                channel_config.aggregation_rules,
                session
            )
            session.items_used_in_video = len(selected_items)
            
            # Phase 4: Video Composition
            output_path = await self._compose_video(
                selected_items,
                channel_config,
                session
            )
            
            # Calculate output stats
            import os
            if output_path and os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                # TODO: Get actual video duration
                output_duration = 180.0  # placeholder
                
                session.complete(output_path, output_size, output_duration)
                session.add_log("info", "Channel run completed successfully")
            else:
                raise Exception("Output file not created")
            
        except Exception as e:
            logger.error(f"Channel run failed: {str(e)}")
            session.fail(str(e))
            session.add_log("error", f"Channel run failed: {str(e)}")
            raise
        
        finally:
            # Update channel last run time
            channel_config.last_run = datetime.now()
            channel_config.next_run = channel_config.schedule_config.get_next_run_time(
                datetime.now()
            )
            
            # Remove from active sessions
            self.active_sessions.pop(session.id, None)
        
        return session
    
    async def _scrape_content(
        self,
        channel_config: ChannelConfig,
        session: AggregationSession
    ) -> List[ContentItem]:
        """Scrape content from all sources"""
        session.add_log("info", "Starting content scraping phase")
        start_time = datetime.now()
        
        all_items = []
        
        for source in channel_config.sources:
            try:
                session.add_log("info", f"Scraping source: {source.name}")
                
                # Get scraper for source type
                scraper = self.scraper_manager.get_scraper(source.source_type)
                
                # Scrape content
                items = await scraper.scrape(source)
                
                # Track items per source
                session.items_per_source[source.id] = len(items)
                all_items.extend(items)
                
                session.add_log("info", 
                    f"Scraped {len(items)} items from {source.name}")
                
            except Exception as e:
                logger.error(f"Failed to scrape {source.name}: {str(e)}")
                session.add_log("error", 
                    f"Failed to scrape {source.name}: {str(e)}")
        
        session.scraping_duration = (datetime.now() - start_time).total_seconds()
        session.add_log("info", 
            f"Scraping completed. Total items: {len(all_items)}")
        
        return all_items
    
    async def _process_content(
        self,
        content_items: List[ContentItem],
        channel_config: ChannelConfig,
        session: AggregationSession
    ) -> List[ContentItem]:
        """Process and enrich content items"""
        session.add_log("info", "Starting content processing phase")
        start_time = datetime.now()
        
        processed_items = []
        
        for item in content_items:
            try:
                # Process item (summarize, analyze sentiment, extract media, etc.)
                processed = await self.content_processor.process(
                    item,
                    target_languages=channel_config.target_languages
                )
                
                if processed.status != ContentStatus.FAILED:
                    processed_items.append(processed)
                
            except Exception as e:
                logger.error(f"Failed to process item {item.id}: {str(e)}")
                session.add_log("warning", 
                    f"Failed to process item: {item.title[:50]}...")
        
        session.processing_duration = (datetime.now() - start_time).total_seconds()
        session.add_log("info", 
            f"Processing completed. Processed items: {len(processed_items)}")
        
        return processed_items
    
    def _select_content(
        self,
        content_items: List[ContentItem],
        rules: List[AggregationRule],
        session: AggregationSession
    ) -> List[ContentItem]:
        """Select content based on aggregation rules"""
        session.add_log("info", "Selecting content based on rules")
        
        selected_items = content_items
        
        # Apply each rule in sequence
        for rule in rules:
            selected_items = rule.apply(selected_items)
            session.add_log("debug", 
                f"Applied rule '{rule.name}': {len(selected_items)} items remain")
        
        session.add_log("info", 
            f"Content selection completed. Selected {len(selected_items)} items")
        
        return selected_items
    
    async def _compose_video(
        self,
        content_items: List[ContentItem],
        channel_config: ChannelConfig,
        session: AggregationSession
    ) -> str:
        """Compose video from selected content"""
        session.add_log("info", "Starting video composition phase")
        start_time = datetime.now()
        
        # Create content collection
        collection = ContentCollection(
            id=session.id,
            name=f"{channel_config.name} - {datetime.now().strftime('%Y-%m-%d')}",
            description=f"Automated content for {channel_config.name}",
            items=content_items
        )
        
        # Create composition project
        project = CompositionProject(
            id=session.id,
            name=collection.name,
            template=self.composition_engine.get_template(channel_config.template_name),
            content_collection_id=collection.id,
            primary_language=channel_config.primary_language,
            additional_languages=channel_config.target_languages
        )
        
        # Configure output
        project.output_resolution = channel_config.output_config.resolution
        project.output_fps = channel_config.output_config.fps
        project.output_format = channel_config.output_config.format
        
        # Compose video
        output_path = await self.composition_engine.compose(
            project,
            collection,
            channel_config
        )
        
        session.composition_duration = (datetime.now() - start_time).total_seconds()
        session.add_log("info", f"Video composition completed: {output_path}")
        
        return output_path
    
    def get_active_sessions(self) -> List[AggregationSession]:
        """Get all active aggregation sessions"""
        return list(self.active_sessions.values())
    
    def get_session(self, session_id: str) -> Optional[AggregationSession]:
        """Get specific session by ID"""
        return self.active_sessions.get(session_id)