"""
Smart Overlay Positioning Agent
AI agent that makes intelligent decisions about subtitle and text overlay positioning
"""

import google.generativeai as genai
from typing import Dict, List, Any
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class OverlayPositioningAgent:
    """AI agent for smart subtitle and overlay positioning decisions"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("🎯 OverlayPositioningAgent initialized")
    
    def analyze_optimal_positioning(self, topic: str, video_style: str, platform: str, 
                                  duration: float, subtitle_count: int) -> Dict[str, Any]:
        """Analyze and decide optimal positioning for subtitles and overlays"""
        
        logger.info(f"🎯 Analyzing optimal positioning for: {topic}")
        logger.info(f"📱 Platform: {platform}, Style: {video_style}, Duration: {duration}s")
        
        try:
            positioning_prompt = f"""
            You are an expert UI/UX designer specializing in video overlay positioning for social media.
            
            VIDEO DETAILS:
            - Topic: {topic}
            - Style: {video_style}
            - Platform: {platform}
            - Duration: {duration} seconds
            - Number of subtitle segments: {subtitle_count}
            
            TASK: Decide optimal positioning strategy for subtitles and text overlays.
            
            POSITIONING RULES:
            1. Subtitles should NEVER overlap with important visual content
            2. For face-focused content: position subtitles at bottom
            3. For action/movement: position subtitles at top or sides
            4. For object demonstrations: avoid center positioning
            5. Consider platform-specific safe zones
            6. Ensure readability on mobile devices
            
            PLATFORM CONSIDERATIONS:
            - TikTok: Bottom positioning preferred, avoid center
            - YouTube Shorts: Lower third is safe zone
            - Instagram Reels: Avoid bottom 20% (UI overlap)
            
            STYLE CONSIDERATIONS:
            - Realistic/Documentary: Professional lower third
            - Cartoon/Animated: More flexible positioning
            - Action/Sports: Dynamic side positioning
            - Educational: Traditional bottom positioning
            
            Return a JSON decision with this structure:
            {{
                "primary_subtitle_position": "bottom_third",
                "secondary_overlay_position": "top_right",
                "positioning_strategy": "static",
                "safe_zones": ["bottom_third", "top_third"],
                "avoid_zones": ["center"],
                "reasoning": "Explanation of positioning decisions",
                "mobile_optimized": true,
                "accessibility_compliant": true
            }}
            """
            
            response = self.model.generate_content(positioning_prompt)
            
            # Parse the response with improved error handling
            import json
            import re
            
            # Clean the response text to remove control characters and non-printable chars
            clean_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response.text)
            clean_text = re.sub(r'[^\x20-\x7E\s]', '', clean_text)  # Keep only printable ASCII
            
            json_match = re.search(r'\{[^{}]*\}', clean_text, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group()
                    # Additional cleaning for common JSON issues
                    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                    
                    positioning_decision = json.loads(json_str)
                    
                    # Validate required fields
                    required_fields = ['primary_subtitle_position', 'positioning_strategy']
                    if all(field in positioning_decision for field in required_fields):
                        logger.info(f"🎯 Positioning Decision: {positioning_decision.get('primary_subtitle_position')}")
                        logger.info(f"📋 Strategy: {positioning_decision.get('positioning_strategy')}")
                        logger.info(f"💭 Reasoning: {positioning_decision.get('reasoning', '')[:100]}...")
                        
                        return positioning_decision
                    else:
                        logger.warning("⚠️ Missing required fields in JSON response, using fallback")
                        return self._get_fallback_positioning(platform, video_style)
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ JSON parsing failed: {e}, using fallback")
                    return self._get_fallback_positioning(platform, video_style)
            else:
                logger.warning("⚠️ Could not find valid JSON in response, using fallback")
                return self._get_fallback_positioning(platform, video_style)
                
        except Exception as e:
            logger.error(f"❌ Positioning analysis failed: {e}")
            return self._get_fallback_positioning(platform, video_style)
    
    def _get_fallback_positioning(self, platform: str, video_style: str) -> Dict[str, Any]:
        """Fallback positioning strategy based on platform and style"""
        
        # Platform-specific defaults
        if platform.lower() in ['tiktok', 'youtube_shorts']:
            primary_position = "bottom_third"
            secondary_position = "top_right"
        elif platform.lower() in ['instagram', 'reels']:
            primary_position = "center_bottom"
            secondary_position = "top_left"
        else:
            primary_position = "bottom_third"
            secondary_position = "top_center"
        
        return {
            "primary_subtitle_position": primary_position,
            "secondary_overlay_position": secondary_position,
            "positioning_strategy": "static",
            "safe_zones": ["bottom_third", "top_third"],
            "avoid_zones": ["center"],
            "reasoning": f"Fallback positioning for {platform} with {video_style} style",
            "mobile_optimized": True,
            "accessibility_compliant": True
        }
    
    def calculate_precise_coordinates(self, position: str, video_width: int, video_height: int,
                                    text_width: int, text_height: int) -> tuple:
        """Calculate precise pixel coordinates for positioning"""
        
        # Define positioning zones as percentages
        position_map = {
            "top_third": (0.5, 0.15),          # Center horizontally, 15% from top
            "bottom_third": (0.5, 0.85),       # Center horizontally, 85% from top
            "center_safe": (0.5, 0.5),         # Dead center
            "left_side": (0.15, 0.5),          # 15% from left, center vertically
            "right_side": (0.85, 0.5),         # 85% from left, center vertically
            "top_left": (0.1, 0.1),            # Top left corner
            "top_right": (0.9, 0.1),           # Top right corner
            "bottom_left": (0.1, 0.9),         # Bottom left corner
            "bottom_right": (0.9, 0.9),        # Bottom right corner
            "center_top": (0.5, 0.25),         # Center horizontally, 25% from top
            "center_bottom": (0.5, 0.75),      # Center horizontally, 75% from top
        }
        
        if position in position_map:
            x_percent, y_percent = position_map[position]
            
            # Calculate pixel coordinates
            x = int((video_width * x_percent) - (text_width / 2))
            y = int((video_height * y_percent) - (text_height / 2))
            
            # Ensure coordinates are within bounds
            x = max(10, min(x, video_width - text_width - 10))
            y = max(10, min(y, video_height - text_height - 10))
            
            logger.info(f"📍 Position '{position}': ({x}, {y}) in {video_width}x{video_height}")
            return (x, y)
        else:
            # Default to center bottom
            x = int((video_width / 2) - (text_width / 2))
            y = int((video_height * 0.85) - (text_height / 2))
            logger.warning(f"⚠️ Unknown position '{position}', using center bottom: ({x}, {y})")
            return (x, y) 