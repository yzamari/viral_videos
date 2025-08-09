"""
NewsContentProcessor - Responsible for processing and analyzing content.

This class follows the Single Responsibility Principle by focusing solely on
content processing, including duplicate detection, AI analysis, and content selection.
"""

from typing import List, Dict, Any
from ..interfaces.aggregator_interfaces import IContentProcessor
from ..processors.content_analyzer import ContentAnalyzer
from ..processors.duplicate_detector import DuplicateDetector
from ..agents.news_orchestrator import NewsOrchestrator
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class NewsContentProcessor(IContentProcessor):
    """
    Processes and analyzes collected content.
    
    Responsibilities:
    - Content analysis for metadata and relevance
    - Duplicate detection and merging from multiple sources
    - AI agent discussions for intelligent content selection
    - Simple rule-based content selection
    """
    
    def __init__(
        self, 
        ai_manager,
        decision_framework=None,
        enable_ai_discussions: bool = True
    ):
        """
        Initialize the content processor with required dependencies.
        
        Args:
            ai_manager: AI service manager for content analysis
            decision_framework: Framework for decision making
            enable_ai_discussions: Whether to enable AI discussions
        """
        self.ai_manager = ai_manager
        self.decision_framework = decision_framework
        self.enable_ai_discussions = enable_ai_discussions
        
        # Initialize content analysis components
        self.content_analyzer = ContentAnalyzer(ai_manager)
        self.duplicate_detector = DuplicateDetector(ai_manager)
        
        # Initialize AI orchestrator if enabled
        self.orchestrator = None
        if enable_ai_discussions and decision_framework:
            self.orchestrator = NewsOrchestrator(ai_manager, decision_framework)
    
    async def analyze_content(
        self, 
        content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze content for relevance, metadata, and quality scores.
        
        Args:
            content: List of content items to analyze
            
        Returns:
            Content items with additional analysis metadata
        """
        logger.info(f"📊 Analyzing {len(content)} content items...")
        
        analyzed_content = []
        for item in content:
            try:
                # Analyze individual content item
                analysis_result = await self.content_analyzer.analyze_content_item(item)
                
                # Merge analysis results into the item
                analyzed_item = {**item, **analysis_result}
                analyzed_content.append(analyzed_item)
                
            except Exception as e:
                logger.warning(f"Failed to analyze item '{item.get('title', 'Unknown')}': {e}")
                # Keep original item if analysis fails
                analyzed_content.append(item)
        
        logger.info(f"✅ Content analysis completed for {len(analyzed_content)} items")
        return analyzed_content
    
    async def detect_and_merge_duplicates(
        self, 
        content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect and merge duplicate stories from different sources.
        
        Args:
            content: List of content items to deduplicate
            
        Returns:
            List of unique content items with duplicates merged
        """
        logger.info(f"🔍 Detecting duplicates in {len(content)} items...")
        
        # Group by similarity
        groups = await self.duplicate_detector.group_similar_content(content)
        
        merged_content = []
        for group in groups:
            if len(group) > 1:
                # Merge duplicates
                merged = await self._merge_duplicate_group(group)
                merged_content.append(merged)
            else:
                # Single item, no duplicates
                merged_content.append(group[0])
        
        logger.info(f"✅ Duplicate detection complete: {len(merged_content)} unique items")
        return merged_content
    
    async def run_ai_discussions(
        self,
        content: List[Dict[str, Any]],
        style: str,
        tone: str,
        platform: str,
        max_stories: int,
        discussion_log: bool
    ) -> List[Dict[str, Any]]:
        """
        Run AI agent discussions for intelligent content selection and ordering.
        
        Args:
            content: Content items to select from
            style: Style description for content selection
            tone: Tone description for content selection
            platform: Target platform for optimization
            max_stories: Maximum number of stories to select
            discussion_log: Whether to enable detailed logging
            
        Returns:
            Selected and ordered content items with AI insights
        """
        if not self.orchestrator:
            logger.warning("AI discussions not available - orchestrator not initialized")
            return self.select_content_simple(content, max_stories)
        
        logger.info("🤖 Starting AI agent discussions for content selection...")
        
        # Create discussion context
        context = {
            'content': content,
            'style': style,
            'tone': tone,
            'platform': platform,
            'max_stories': max_stories,
            'criteria': {
                'relevance': 'How newsworthy and current is this story?',
                'engagement': f'How engaging will this be for {platform} audience?',
                'visual_appeal': 'Does this have good visual media available?',
                'diversity': 'Does this add variety to our news selection?',
                'multi_source': 'Is this confirmed by multiple sources?'
            }
        }
        
        # Run orchestrated discussion
        discussion_result = await self.orchestrator.run_news_selection_discussion(
            context,
            enable_logging=discussion_log
        )
        
        # Extract selected content
        selected_indices = discussion_result.get('selected_indices', [])
        selected_content = [content[i] for i in selected_indices if i < len(content)]
        
        # Add AI insights to each item
        insights = discussion_result.get('insights', {})
        for i, item in enumerate(selected_content):
            item['ai_insights'] = insights.get(str(i), {})
            item['ai_reasoning'] = discussion_result.get('reasoning', {}).get(str(i), '')
        
        # Get visual style recommendations
        if self.orchestrator:
            visual_styles = await self.orchestrator.select_visual_styles(
                style, tone, platform, 'en'  # Default to English for style selection
            )
            logger.info(f"🎨 AI selected visual styles: {visual_styles}")
            
            # Run content rephrasing if needed
            selected_content = await self.orchestrator.rephrase_content_with_tone(
                selected_content, style, tone, 'en'  # Default language
            )
        
        logger.info(f"✅ AI discussion completed: selected {len(selected_content)} stories")
        return selected_content
    
    def select_content_simple(
        self,
        content: List[Dict[str, Any]],
        max_stories: int
    ) -> List[Dict[str, Any]]:
        """
        Simple content selection based on priority and media availability.
        
        Args:
            content: Content items to select from
            max_stories: Maximum number of stories to select
            
        Returns:
            Selected content items ordered by priority
        """
        logger.info(f"📋 Simple content selection from {len(content)} items...")
        
        # Sort by priority, duplicate count, and content length
        sorted_content = sorted(
            content,
            key=lambda x: (
                x.get('priority', 0.5),
                x.get('duplicate_count', 1),
                len(x.get('content', ''))
            ),
            reverse=True
        )
        
        # Prefer items with media, but allow text-only if no media available
        with_media = [
            item for item in sorted_content
            if item.get('image_url') or item.get('video_url')
        ]
        
        if not with_media:
            logger.warning("No items with media found, using text-only content")
            selected = sorted_content[:max_stories]
        else:
            selected = with_media[:max_stories]
        
        logger.info(f"✅ Simple selection complete: selected {len(selected)} stories")
        return selected
    
    async def _merge_duplicate_group(
        self,
        group: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge a group of duplicate stories into a single enhanced story.
        
        Args:
            group: List of duplicate content items
            
        Returns:
            Merged content item with combined information
        """
        # Use the most complete version as base (highest content length)
        base = max(group, key=lambda x: len(x.get('content', '')))
        
        # Create merged item
        merged = base.copy()
        merged['sources'] = list(set([item['source'] for item in group]))
        merged['source'] = ' + '.join(merged['sources'])
        
        # Collect all media URLs
        all_images = []
        all_videos = []
        for item in group:
            if item.get('image_url'):
                all_images.append(item['image_url'])
            if item.get('video_url'):
                all_videos.append(item['video_url'])
        
        # Use best quality media (first one for now - could be enhanced with quality detection)
        if all_images:
            merged['image_url'] = all_images[0]
            merged['all_images'] = all_images
        if all_videos:
            merged['video_url'] = all_videos[0]
            merged['all_videos'] = all_videos
        
        # Boost priority for multi-source stories (indicates higher credibility)
        merged['priority'] = min(1.0, max(item.get('priority', 0.5) for item in group) + 0.2)
        merged['duplicate_count'] = len(group)
        merged['credibility_score'] = len(group) / 5.0  # More sources = higher credibility
        
        logger.info(f"🔀 Merged {len(group)} duplicate stories: {merged['title'][:50]}...")
        
        return merged