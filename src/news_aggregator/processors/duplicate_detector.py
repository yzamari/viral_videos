"""Duplicate Detection for News Articles"""

import re
import hashlib
from typing import List, Dict, Any, Set, Tuple
from difflib import SequenceMatcher
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None

from ...utils.logging_config import get_logger
from ...ai.manager import AIServiceManager

logger = get_logger(__name__)


class DuplicateDetector:
    """Detects and groups duplicate news stories from multiple sources"""
    
    def __init__(self, ai_manager: AIServiceManager, similarity_threshold: float = 0.7):
        self.ai_manager = ai_manager
        self.similarity_threshold = similarity_threshold
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
        else:
            self.tfidf_vectorizer = None
    
    async def group_similar_content(
        self,
        content_list: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group similar/duplicate content together"""
        
        if not content_list:
            return []
        
        # 1. Quick hash-based exact duplicate detection
        exact_groups = self._group_exact_duplicates(content_list)
        
        # 2. Similarity-based grouping for near-duplicates
        final_groups = []
        
        for group in exact_groups:
            if len(group) == 1:
                # Check for similar stories
                similar_groups = await self._find_similar_stories(group[0], content_list)
                if similar_groups:
                    final_groups.append(similar_groups)
                else:
                    final_groups.append(group)
            else:
                # Already grouped by exact match
                final_groups.append(group)
        
        # Remove duplicates from groups
        final_groups = self._deduplicate_groups(final_groups)
        
        logger.info(f"🔍 Grouped {len(content_list)} items into {len(final_groups)} unique stories")
        
        return final_groups
    
    def _group_exact_duplicates(
        self,
        content_list: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group exact duplicates by title hash"""
        
        hash_groups = {}
        
        for item in content_list:
            # Create hash from normalized title
            title_hash = self._create_title_hash(item['title'])
            
            if title_hash not in hash_groups:
                hash_groups[title_hash] = []
            hash_groups[title_hash].append(item)
        
        return list(hash_groups.values())
    
    def _create_title_hash(self, title: str) -> str:
        """Create normalized hash from title"""
        # Normalize: lowercase, remove punctuation, extra spaces
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        normalized = ' '.join(normalized.split())
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def _find_similar_stories(
        self,
        target_item: Dict[str, Any],
        all_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find stories similar to target item"""
        
        similar_items = [target_item]
        target_text = f"{target_item['title']} {target_item.get('content', '')}"
        
        for item in all_items:
            if item == target_item:
                continue
            
            # Calculate similarity
            item_text = f"{item['title']} {item.get('content', '')}"
            similarity = self._calculate_similarity(target_text, item_text)
            
            if similarity >= self.similarity_threshold:
                similar_items.append(item)
        
        # If we have multiple similar items, use AI to confirm they're about the same event
        if len(similar_items) > 1:
            confirmed = await self._ai_confirm_duplicates(similar_items)
            if confirmed:
                return similar_items
        
        return [target_item]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using multiple methods"""
        
        # 1. Quick length check
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
        if len_ratio < 0.5:
            return 0.0
        
        # 2. Title similarity (weighted higher)
        title1 = text1.split('.')[0] if '.' in text1 else text1[:100]
        title2 = text2.split('.')[0] if '.' in text2 else text2[:100]
        title_sim = SequenceMatcher(None, title1, title2).ratio()
        
        # 3. Full text similarity
        text_sim = SequenceMatcher(None, text1, text2).ratio()
        
        # 4. TF-IDF similarity for longer texts
        tfidf_sim = 0.0
        if SKLEARN_AVAILABLE and self.tfidf_vectorizer and len(text1) > 200 and len(text2) > 200:
            try:
                vectors = self.tfidf_vectorizer.fit_transform([text1, text2])
                tfidf_sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            except:
                pass
        
        # Weighted average
        return (title_sim * 0.5) + (text_sim * 0.3) + (tfidf_sim * 0.2)
    
    async def _ai_confirm_duplicates(
        self,
        items: List[Dict[str, Any]]
    ) -> bool:
        """Use AI to confirm if items are about the same news event"""
        
        if len(items) < 2:
            return False
        
        # Prepare prompt
        prompt = "Are these news items about the same event? Reply with just YES or NO.\n\n"
        
        for i, item in enumerate(items[:3]):  # Check first 3 items
            prompt += f"Item {i+1} ({item['source']}): {item['title']}\n"
            if item.get('content'):
                prompt += f"Content: {item['content'][:200]}...\n"
            prompt += "\n"
        
        try:
            response = await self.ai_manager.generate_content_async(
                prompt=prompt,
                max_tokens=10,
                temperature=0.1
            )
            
            return 'yes' in response.lower()
            
        except Exception as e:
            logger.warning(f"AI confirmation failed: {e}")
            # Fallback to similarity threshold
            return True
    
    def _deduplicate_groups(
        self,
        groups: List[List[Dict[str, Any]]]
    ) -> List[List[Dict[str, Any]]]:
        """Remove items that appear in multiple groups"""
        
        seen_ids = set()
        final_groups = []
        
        for group in groups:
            unique_group = []
            for item in group:
                # Create unique ID for item
                item_id = f"{item['source']}_{item['title'][:50]}"
                
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    unique_group.append(item)
            
            if unique_group:
                final_groups.append(unique_group)
        
        return final_groups
    
    def calculate_group_importance(self, group: List[Dict[str, Any]]) -> float:
        """Calculate importance score for a group of duplicate stories"""
        
        # More sources = more important
        source_count = len(set(item['source'] for item in group))
        
        # Average priority
        avg_priority = sum(item.get('priority', 0.5) for item in group) / len(group)
        
        # Has media
        has_media = any(item.get('image_url') or item.get('video_url') for item in group)
        
        # Calculate final score
        importance = (
            (source_count / 5.0) * 0.4 +  # Normalize source count
            avg_priority * 0.4 +
            (0.2 if has_media else 0.0)
        )
        
        return min(1.0, importance)