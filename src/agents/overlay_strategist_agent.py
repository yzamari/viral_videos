"""
Overlay Strategist Agent - Decides on dynamic overlays throughout the video
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .gemini_helper import GeminiModelHelper

logger = logging.getLogger(__name__)


class OverlayType(Enum):
    """Types of overlays"""
    FACT_BUBBLE = "fact_bubble"
    QUOTE = "quote"
    STATISTIC = "statistic"
    CALL_TO_ACTION = "call_to_action"
    EMOJI_REACTION = "emoji_reaction"
    HIGHLIGHT = "highlight"
    QUESTION = "question"
    TIP = "tip"
    WARNING = "warning"
    TRANSITION = "transition"
    BRAND = "brand"
    COUNTDOWN = "countdown"
    LOCATION = "location"
    TIME_MARKER = "time_marker"
    ACHIEVEMENT = "achievement"


@dataclass
class DynamicOverlay:
    """Dynamic overlay configuration"""
    overlay_type: OverlayType
    text: str
    start_time: float
    duration: float
    position: str  # top-left, top-center, top-right, etc.
    style: str  # bold, subtle, animated, etc.
    color_scheme: str  # vibrant, muted, branded, etc.
    animation: str  # fade, slide, bounce, zoom, etc.
    size: str  # small, medium, large
    priority: int  # 1-10, higher means more important
    reasoning: str


class OverlayStrategistAgent:
    """AI agent that analyzes scripts and decides on dynamic overlays"""
    
    def __init__(self, api_key: str):
        """Initialize the overlay strategist agent"""
        self.gemini = GeminiModelHelper.get_configured_model(api_key)
        logger.info("🎯 Overlay Strategist Agent initialized")
    
    def analyze_script_for_overlays(
        self,
        script: str,
        video_duration: float,
        platform: str,
        style: str,
        tone: str,
        mission: str,
        segments: List[Dict[str, Any]]
    ) -> List[DynamicOverlay]:
        """
        Analyze script and decide on dynamic overlays throughout the video
        
        Args:
            script: Full script text
            video_duration: Total video duration
            platform: Target platform (instagram, tiktok, etc.)
            style: Video style
            tone: Video tone
            mission: Original mission
            segments: Script segments with timing
            
        Returns:
            List of dynamic overlays to add
        """
        logger.info(f"🎯 Analyzing script for dynamic overlays (duration: {video_duration}s)")
        
        prompt = f"""
You are an expert overlay strategist for viral videos. Analyze this script and create engaging overlays throughout the video.

PLATFORM: {platform}
STYLE: {style}
TONE: {tone}
DURATION: {video_duration} seconds
MISSION: {mission}

SCRIPT:
{script}

SEGMENTS WITH TIMING:
{self._format_segments(segments)}

Create 5-10 dynamic overlays distributed throughout the video. Consider:

1. ENGAGEMENT HOOKS: Add overlays that grab attention and encourage interaction
2. KEY INFORMATION: Highlight important facts, statistics, or quotes
3. EMOTIONAL MOMENTS: Add reactions, emojis, or emphasis at peak moments
4. CALL-TO-ACTIONS: Strategic CTAs beyond just the end (like, share, comment)
5. VISUAL VARIETY: Mix different overlay types and positions
6. PLATFORM OPTIMIZATION: Match platform best practices
7. TIMING: Avoid cluttering, space overlays appropriately

For each overlay, provide:
- Type (fact_bubble, quote, statistic, call_to_action, emoji_reaction, highlight, question, tip, warning, transition, brand, countdown, location, time_marker, achievement)
- Text (keep it SHORT and punchy, max 5-7 words)
- Start time (in seconds)
- Duration (typically 2-4 seconds)
- Position (top-left, top-center, top-right, middle-left, center, middle-right, bottom-left, bottom-center, bottom-right)
- Style (bold, subtle, animated, minimal, dramatic)
- Color scheme (vibrant, muted, branded, contrast, gradient)
- Animation (fade, slide-left, slide-right, slide-up, slide-down, bounce, zoom, rotate, shake)
- Size (small, medium, large)
- Priority (1-10, where 10 is most important)
- Reasoning (why this overlay at this moment)

Return as a JSON array of overlay objects.
"""
        
        try:
            response = self.gemini.generate_content(prompt)
            import json
            response = json.loads(response.text)
            
            if not response or not isinstance(response, list):
                logger.warning("Invalid response from AI, using fallback overlays")
                return self._get_fallback_overlays(video_duration)
            
            # Parse and validate overlays
            overlays = []
            for overlay_data in response:
                try:
                    overlay = DynamicOverlay(
                        overlay_type=OverlayType(overlay_data.get('type', 'fact_bubble')),
                        text=overlay_data.get('text', ''),
                        start_time=float(overlay_data.get('start_time', 0)),
                        duration=float(overlay_data.get('duration', 3)),
                        position=overlay_data.get('position', 'top-center'),
                        style=overlay_data.get('style', 'animated'),
                        color_scheme=overlay_data.get('color_scheme', 'vibrant'),
                        animation=overlay_data.get('animation', 'fade'),
                        size=overlay_data.get('size', 'medium'),
                        priority=int(overlay_data.get('priority', 5)),
                        reasoning=overlay_data.get('reasoning', '')
                    )
                    
                    # Validate timing
                    if overlay.start_time < 0 or overlay.start_time >= video_duration:
                        continue
                    if overlay.start_time + overlay.duration > video_duration:
                        overlay.duration = video_duration - overlay.start_time
                    
                    overlays.append(overlay)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse overlay: {e}")
                    continue
            
            # Sort by start time
            overlays.sort(key=lambda x: x.start_time)
            
            logger.info(f"✅ Generated {len(overlays)} dynamic overlays")
            for i, overlay in enumerate(overlays):
                logger.info(f"   {i+1}. {overlay.overlay_type.value}: '{overlay.text}' at {overlay.start_time:.1f}s ({overlay.position})")
            
            return overlays
            
        except Exception as e:
            logger.error(f"Failed to generate dynamic overlays: {e}")
            return self._get_fallback_overlays(video_duration)
    
    def _format_segments(self, segments: List[Dict[str, Any]]) -> str:
        """Format segments for the prompt"""
        formatted = []
        current_time = 0
        
        for i, segment in enumerate(segments):
            duration = segment.get('duration', 8)
            formatted.append(f"Segment {i+1} ({current_time:.1f}s - {current_time + duration:.1f}s): {segment.get('text', '')[:100]}...")
            current_time += duration
        
        return "\n".join(formatted)
    
    def _get_fallback_overlays(self, video_duration: float) -> List[DynamicOverlay]:
        """Get fallback overlays if AI fails"""
        overlays = []
        
        # Add a mid-video engagement overlay
        if video_duration > 20:
            overlays.append(DynamicOverlay(
                overlay_type=OverlayType.CALL_TO_ACTION,
                text="Double tap if you agree! ❤️",
                start_time=video_duration / 2,
                duration=3,
                position="center",
                style="animated",
                color_scheme="vibrant",
                animation="bounce",
                size="medium",
                priority=7,
                reasoning="Mid-video engagement boost"
            ))
        
        # Add a fact bubble
        if video_duration > 15:
            overlays.append(DynamicOverlay(
                overlay_type=OverlayType.FACT_BUBBLE,
                text="Fun Fact! 🎯",
                start_time=video_duration * 0.3,
                duration=2.5,
                position="top-right",
                style="bold",
                color_scheme="gradient",
                animation="slide-left",
                size="small",
                priority=5,
                reasoning="Information highlight"
            ))
        
        return overlays