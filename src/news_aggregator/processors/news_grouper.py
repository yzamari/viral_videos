"""News Grouper - Groups related news items together"""

from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
import re
from datetime import datetime

from ...utils.logging_config import get_logger
from ...ai.manager import AIServiceManager
from ..models.content_models import ContentItem, ContentCollection

logger = get_logger(__name__)


class NewsGrouper:
    """Groups related news items into collections"""
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        
        # Similarity thresholds
        self.title_similarity_threshold = 0.6
        self.content_similarity_threshold = 0.5
        self.tag_overlap_threshold = 0.4
    
    async def group_content(
        self,
        content_items: List[ContentItem],
        edition_type: str
    ) -> List[ContentCollection]:
        """Group related content items into collections"""
        
        logger.info(f"Grouping {len(content_items)} items for {edition_type} edition")
        
        # First pass: Group by explicit similarities
        initial_groups = self._create_initial_groups(content_items)
        
        # Second pass: Merge similar groups
        merged_groups = await self._merge_similar_groups(initial_groups)
        
        # Create content collections
        collections = []
        for group_id, items in merged_groups.items():
            collection = await self._create_collection(items, edition_type)
            collections.append(collection)
        
        # Sort by relevance (sum of item scores)
        collections.sort(
            key=lambda c: sum(item.relevance_score for item in c.items),
            reverse=True
        )
        
        logger.info(f"Created {len(collections)} content groups")
        
        return collections
    
    def _create_initial_groups(
        self, 
        content_items: List[ContentItem]
    ) -> Dict[int, List[ContentItem]]:
        """Create initial groups based on obvious similarities"""
        
        groups = {}
        used_items = set()
        
        for i, item1 in enumerate(content_items):
            if i in used_items:
                continue
                
            # Start new group
            group = [item1]
            used_items.add(i)
            
            # Find similar items
            for j, item2 in enumerate(content_items[i+1:], start=i+1):
                if j in used_items:
                    continue
                    
                # Check if items are related
                if self._are_items_related(item1, item2):
                    group.append(item2)
                    used_items.add(j)
            
            groups[i] = group
        
        return groups
    
    def _are_items_related(
        self,
        item1: ContentItem,
        item2: ContentItem
    ) -> bool:
        """Check if two items are related"""
        
        # Check title similarity
        title_sim = self._calculate_title_similarity(item1.title, item2.title)
        if title_sim > self.title_similarity_threshold:
            return True
        
        # Check tag overlap
        if item1.tags and item2.tags:
            tag_overlap = len(set(item1.tags) & set(item2.tags)) / min(
                len(item1.tags), len(item2.tags)
            )
            if tag_overlap > self.tag_overlap_threshold:
                return True
        
        # Check for same entities
        entities1 = self._extract_entities(item1)
        entities2 = self._extract_entities(item2)
        
        if entities1 and entities2:
            entity_overlap = len(entities1 & entities2)
            if entity_overlap >= 2:  # At least 2 common entities
                return True
        
        # Check category overlap
        if item1.categories and item2.categories:
            if set(item1.categories) & set(item2.categories):
                # Additional content check for same category
                return self._check_content_similarity(item1, item2)
        
        return False
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""
        
        # Simple word overlap similarity
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was'}
        words1 -= stop_words
        words2 -= stop_words
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_entities(self, item: ContentItem) -> Set[str]:
        """Extract named entities from content"""
        entities = set()
        
        # Extract capitalized words (simple NER)
        text = f"{item.title} {item.content[:500]}"
        
        # Find capitalized phrases
        cap_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        for phrase in cap_words:
            # Filter out common words
            if len(phrase) > 2 and phrase not in ['The', 'This', 'That', 'These']:
                entities.add(phrase.lower())
        
        # Add tags as entities
        if item.tags:
            entities.update(tag.lower() for tag in item.tags)
        
        return entities
    
    def _check_content_similarity(
        self,
        item1: ContentItem,
        item2: ContentItem
    ) -> bool:
        """Check content similarity for items in same category"""
        
        # Get key phrases from content
        phrases1 = self._extract_key_phrases(item1.content)
        phrases2 = self._extract_key_phrases(item2.content)
        
        if not phrases1 or not phrases2:
            return False
        
        # Check phrase overlap
        overlap = len(phrases1 & phrases2)
        min_phrases = min(len(phrases1), len(phrases2))
        
        return (overlap / min_phrases) > self.content_similarity_threshold
    
    def _extract_key_phrases(self, content: str) -> Set[str]:
        """Extract key phrases from content"""
        phrases = set()
        
        # Get first 500 characters
        text = content[:500].lower()
        
        # Extract phrases between punctuation
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences[:3]:  # First 3 sentences
            # Extract 2-3 word phrases
            words = sentence.split()
            for i in range(len(words) - 1):
                phrase = ' '.join(words[i:i+2])
                if len(phrase) > 5:  # Minimum phrase length
                    phrases.add(phrase)
        
        return phrases
    
    async def _merge_similar_groups(
        self,
        groups: Dict[int, List[ContentItem]]
    ) -> Dict[int, List[ContentItem]]:
        """Merge groups that are similar"""
        
        merged = {}
        used_groups = set()
        
        group_ids = list(groups.keys())
        
        for i, group_id1 in enumerate(group_ids):
            if group_id1 in used_groups:
                continue
                
            merged_group = groups[group_id1].copy()
            used_groups.add(group_id1)
            
            # Check against other groups
            for group_id2 in group_ids[i+1:]:
                if group_id2 in used_groups:
                    continue
                
                # Check if groups should be merged
                if await self._should_merge_groups(
                    groups[group_id1], 
                    groups[group_id2]
                ):
                    merged_group.extend(groups[group_id2])
                    used_groups.add(group_id2)
            
            merged[group_id1] = merged_group
        
        return merged
    
    async def _should_merge_groups(
        self,
        group1: List[ContentItem],
        group2: List[ContentItem]
    ) -> bool:
        """Check if two groups should be merged"""
        
        # Get representative items (highest relevance)
        rep1 = max(group1, key=lambda x: x.relevance_score)
        rep2 = max(group2, key=lambda x: x.relevance_score)
        
        # Check if representatives are related
        return self._are_items_related(rep1, rep2)
    
    async def _create_collection(
        self,
        items: List[ContentItem],
        edition_type: str
    ) -> ContentCollection:
        """Create content collection from grouped items"""
        
        # Generate collection name
        collection_name = await self._generate_collection_name(items)
        
        # Generate description
        description = await self._generate_collection_description(
            items, 
            edition_type
        )
        
        # Extract common tags
        all_tags = []
        for item in items:
            all_tags.extend(item.tags)
        
        # Count tag frequency
        tag_counts = defaultdict(int)
        for tag in all_tags:
            tag_counts[tag] += 1
        
        # Get most common tags
        common_tags = sorted(
            tag_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        collection = ContentCollection(
            id=f"collection_{datetime.now().timestamp()}",
            name=collection_name,
            description=description,
            items=items,
            tags=[tag for tag, _ in common_tags],
            metadata={
                "edition_type": edition_type,
                "item_count": len(items),
                "avg_relevance": sum(
                    item.relevance_score for item in items
                ) / len(items)
            }
        )
        
        return collection
    
    async def _generate_collection_name(
        self,
        items: List[ContentItem]
    ) -> str:
        """Generate name for content collection"""
        
        if len(items) == 1:
            # Single item - use truncated title
            return items[0].title[:100]
        
        # Multiple items - find common theme
        # Get most common entities
        all_entities = []
        for item in items[:3]:  # Top 3 items
            entities = self._extract_entities(item)
            all_entities.extend(entities)
        
        # Count entity frequency
        entity_counts = defaultdict(int)
        for entity in all_entities:
            entity_counts[entity] += 1
        
        # Get most common entity
        if entity_counts:
            most_common = max(entity_counts.items(), key=lambda x: x[1])
            base_name = most_common[0].title()
            
            # Add context
            if len(items) == 2:
                return f"{base_name} - Developing Story"
            else:
                return f"{base_name} - {len(items)} Related Stories"
        
        # Fallback to generic name
        return f"Related News - {len(items)} Stories"
    
    async def _generate_collection_description(
        self,
        items: List[ContentItem],
        edition_type: str
    ) -> str:
        """Generate description for content collection"""
        
        # Sort by relevance
        sorted_items = sorted(
            items, 
            key=lambda x: x.relevance_score, 
            reverse=True
        )
        
        # Create description from top items
        summaries = []
        for item in sorted_items[:3]:
            if item.summary:
                summaries.append(item.summary)
            else:
                summaries.append(item.title)
        
        if len(summaries) == 1:
            return summaries[0]
        elif len(summaries) == 2:
            return f"{summaries[0]} Additionally, {summaries[1]}"
        else:
            prompt = f"""Create a cohesive description for these related {edition_type} news stories:
            1. {summaries[0]}
            2. {summaries[1]}
            3. {summaries[2]}
            
            Write a single paragraph that captures the overall theme."""
            
            try:
                response = await self.ai_manager.generate_text(
                    prompt, 
                    max_tokens=150
                )
                return response.strip()
            except:
                # Fallback
                return f"Multiple stories about: {summaries[0][:100]}..."