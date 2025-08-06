"""
Intelligent Media Orchestrator
Combines multiple media sources and selects the best moments for engaging storytelling
"""

import logging
import asyncio
from typing import List, Dict, Optional, Any, Tuple
import cv2
import numpy as np
from datetime import datetime
import os
import subprocess
import json

logger = logging.getLogger(__name__)

class MediaOrchestrator:
    """
    Orchestrates media from multiple sources to create engaging news videos
    """
    
    def __init__(self, ai_manager=None):
        self.ai_manager = ai_manager
        self.scene_cache = {}
        
    async def create_story_timeline(
        self,
        news_item: Dict[str, Any],
        available_media: List[Dict[str, Any]],
        target_duration: float,
        style: str,
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Create an intelligent timeline combining multiple media sources
        
        Args:
            news_item: The news story content
            available_media: List of available media (images, videos, etc.)
            target_duration: Target duration for this story segment
            style: Visual style (e.g., "breaking news", "dark humor")
            platform: Target platform
            
        Returns:
            Timeline of media segments with transitions
        """
        
        # Analyze the news content to identify key moments
        key_moments = await self._identify_key_moments(news_item)
        
        # Create a narrative structure
        narrative_beats = self._create_narrative_structure(
            key_moments, 
            target_duration,
            style
        )
        
        timeline = []
        current_time = 0
        
        for beat in narrative_beats:
            # Find the best media for this narrative beat
            best_media = await self._select_best_media(
                beat,
                available_media,
                news_item
            )
            
            if best_media:
                # If it's a video, extract the relevant segment
                if best_media['type'] == 'video':
                    segment = await self._extract_video_highlight(
                        best_media,
                        beat,
                        news_item
                    )
                else:
                    segment = best_media
                
                # Add to timeline with timing and transitions
                timeline.append({
                    'start_time': current_time,
                    'duration': beat['duration'],
                    'media': segment,
                    'overlay_text': beat.get('text', ''),
                    'transition': beat.get('transition', 'cut'),
                    'effects': self._get_effects_for_beat(beat, style, platform)
                })
                
                current_time += beat['duration']
        
        return timeline
    
    async def _identify_key_moments(self, news_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use AI to identify key moments in the news story
        """
        if not self.ai_manager:
            # Fallback to simple keyword extraction
            return self._extract_keywords(news_item)
        
        prompt = f"""
        Analyze this news story and identify key visual moments:
        Title: {news_item.get('title', '')}
        Content: {news_item.get('content', '')}
        
        Return a JSON list of key moments with:
        - moment_type: (action, emotion, location, person, object)
        - keywords: List of search keywords for this moment
        - importance: 1-10 scale
        - ideal_duration: Suggested duration in seconds
        
        Example:
        [
            {{"moment_type": "action", "keywords": ["goal", "score", "celebration"], "importance": 10, "ideal_duration": 3}},
            {{"moment_type": "person", "keywords": ["Netanyahu", "prime minister"], "importance": 8, "ideal_duration": 2}}
        ]
        """
        
        try:
            response = await self.ai_manager.generate_content_async(prompt)
            # Parse JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
        
        return self._extract_keywords(news_item)
    
    def _extract_keywords(self, news_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simple keyword extraction fallback
        """
        keywords = []
        content = f"{news_item.get('title', '')} {news_item.get('content', '')}"
        
        # Look for action words
        action_words = ['goal', 'score', 'win', 'crash', 'explosion', 'attack', 'save', 'rescue']
        for word in action_words:
            if word in content.lower():
                keywords.append({
                    'moment_type': 'action',
                    'keywords': [word],
                    'importance': 8,
                    'ideal_duration': 3
                })
        
        # Look for emotions
        emotion_words = ['celebrate', 'cry', 'angry', 'happy', 'shock', 'surprise']
        for word in emotion_words:
            if word in content.lower():
                keywords.append({
                    'moment_type': 'emotion',
                    'keywords': [word],
                    'importance': 7,
                    'ideal_duration': 2
                })
        
        if not keywords:
            # Default moment
            keywords.append({
                'moment_type': 'general',
                'keywords': news_item.get('title', '').split()[:3],
                'importance': 5,
                'ideal_duration': 5
            })
        
        return keywords
    
    def _create_narrative_structure(
        self,
        key_moments: List[Dict[str, Any]],
        target_duration: float,
        style: str
    ) -> List[Dict[str, Any]]:
        """
        Create a narrative structure with proper pacing
        """
        # Sort by importance
        sorted_moments = sorted(key_moments, key=lambda x: x['importance'], reverse=True)
        
        narrative_beats = []
        remaining_duration = target_duration
        
        # For TikTok/viral style: Start with the most exciting moment
        if 'viral' in style.lower() or 'tiktok' in style.lower():
            # Hook - most important moment first
            if sorted_moments:
                hook = sorted_moments[0]
                hook_duration = min(3, remaining_duration)
                narrative_beats.append({
                    'type': 'hook',
                    'moment': hook,
                    'duration': hook_duration,
                    'text': '⚡ BREAKING',
                    'transition': 'zoom_in'
                })
                remaining_duration -= hook_duration
        
        # Build the story
        for moment in sorted_moments[1:]:
            if remaining_duration <= 0:
                break
            
            beat_duration = min(moment['ideal_duration'], remaining_duration)
            narrative_beats.append({
                'type': 'story',
                'moment': moment,
                'duration': beat_duration,
                'transition': 'cut'
            })
            remaining_duration -= beat_duration
        
        return narrative_beats
    
    async def _select_best_media(
        self,
        beat: Dict[str, Any],
        available_media: List[Dict[str, Any]],
        news_item: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best media for a narrative beat
        """
        moment = beat.get('moment', {})
        keywords = moment.get('keywords', [])
        
        best_score = 0
        best_media = None
        
        for media in available_media:
            score = 0
            
            # Check if media matches keywords
            media_text = f"{media.get('title', '')} {media.get('description', '')}"
            for keyword in keywords:
                if keyword.lower() in media_text.lower():
                    score += 10
            
            # Prefer video for action moments
            if moment['moment_type'] == 'action' and media['type'] == 'video':
                score += 5
            
            # Prefer images for emotion/person moments
            if moment['moment_type'] in ['emotion', 'person'] and media['type'] == 'image':
                score += 3
            
            if score > best_score:
                best_score = score
                best_media = media
        
        # If no good match, use any available media
        if not best_media and available_media:
            best_media = available_media[0]
        
        return best_media
    
    async def _extract_video_highlight(
        self,
        video: Dict[str, Any],
        beat: Dict[str, Any],
        news_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract the most relevant segment from a video
        """
        video_path = video.get('local_path', video.get('url', ''))
        if not video_path or not os.path.exists(video_path):
            return video
        
        moment = beat.get('moment', {})
        keywords = moment.get('keywords', [])
        
        # Analyze video to find best moments
        highlight_times = await self._find_highlight_moments(
            video_path,
            keywords,
            moment['moment_type']
        )
        
        if highlight_times:
            # Extract the best segment
            start_time, end_time = highlight_times[0]
            duration = min(end_time - start_time, beat['duration'])
            
            # Create clip
            output_path = f"{video_path}_highlight_{start_time}_{duration}.mp4"
            
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', video_path,
                '-t', str(duration),
                '-c', 'copy',
                output_path
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                
                return {
                    **video,
                    'local_path': output_path,
                    'start_time': start_time,
                    'duration': duration,
                    'is_highlight': True
                }
            except Exception as e:
                logger.error(f"Failed to extract highlight: {e}")
        
        return video
    
    async def _find_highlight_moments(
        self,
        video_path: str,
        keywords: List[str],
        moment_type: str
    ) -> List[Tuple[float, float]]:
        """
        Find highlight moments in a video using computer vision
        """
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            highlights = []
            
            # For action moments, look for fast motion
            if moment_type == 'action':
                prev_frame = None
                motion_scores = []
                
                for i in range(0, total_frames, int(fps)):  # Sample every second
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if prev_frame is not None:
                        # Calculate motion between frames
                        diff = cv2.absdiff(prev_frame, frame)
                        motion_score = np.mean(diff)
                        motion_scores.append((i / fps, motion_score))
                    
                    prev_frame = frame
                
                # Find peaks in motion
                if motion_scores:
                    motion_scores.sort(key=lambda x: x[1], reverse=True)
                    for time, score in motion_scores[:3]:  # Top 3 moments
                        highlights.append((time, time + 3))  # 3-second clips
            
            # For other moments, use the middle of the video as fallback
            if not highlights:
                middle = total_frames / fps / 2
                highlights.append((middle - 2, middle + 2))
            
            cap.release()
            return highlights
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return [(0, 5)]  # Default to first 5 seconds
    
    def _get_effects_for_beat(
        self,
        beat: Dict[str, Any],
        style: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Determine visual effects for a narrative beat
        """
        effects = {
            'zoom': 1.0,
            'speed': 1.0,
            'filter': None,
            'overlay_opacity': 0.8
        }
        
        # Hook gets special treatment
        if beat['type'] == 'hook':
            effects['zoom'] = 1.2  # Slight zoom
            effects['speed'] = 0.9  # Slight slow-mo for drama
            
        # Platform-specific effects
        if platform == 'tiktok':
            effects['filter'] = 'vibrant'  # More saturated colors
            
        # Style-specific effects
        if 'dark' in style.lower():
            effects['filter'] = 'dark'
            effects['overlay_opacity'] = 0.9
        elif 'urgent' in style.lower() or 'breaking' in style.lower():
            effects['speed'] = 1.1  # Slightly faster
            
        return effects