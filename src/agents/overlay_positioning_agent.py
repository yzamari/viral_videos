"""
Smart Overlay Positioning Agent
AI agent that makes intelligent decisions about subtitle and
        text overlay positioning with colorful hooks and fonts
"""

import google.generativeai as genai
from typing import Dict, List, Any, Optional
from ..utils.logging_config import get_logger
import json
import re

logger = get_logger(__name__)

class OverlayPositioningAgent:
    """AI agent for smart subtitle and overlay positioning decisions with colorful hooks"""

    def __init__(self, api_key: str):
        """Initialize the positioning agent"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        logger.info("🎯 OverlayPositioningAgent initialized with colorful hooks support")

    def analyze_optimal_positioning(self, topic: str, video_style: str, platform: str,
                                  duration: float, subtitle_count: int) -> Dict[str, Any]:
        """Analyze optimal positioning for subtitles and colorful text overlays"""

        logger.info(f"🎯 Analyzing optimal positioning for: {topic}")
        logger.info(
            f"📱 Platform: {platform}, "
            f"Style: {video_style}, "
            f"Duration: {duration}s")

        try:
            # Optimized concise prompt for faster processing
            positioning_prompt = f"""
Overlay positioning for: "{topic}"
Platform: {platform}, Style: {video_style}, Duration: {duration}s

Rules:
- TikTok: Bottom positioning, avoid center
- YouTube: Lower third safe zone
- Instagram: Avoid bottom 20%

Choose position: bottom_center, bottom_left, bottom_right, top_center, top_left, top_right, center_left, center_right

Return JSON:
{{
    "primary_overlay_position": "position_name",
    "positioning_strategy": "static|dynamic",
    "reasoning": "Brief explanation",
    "mobile_optimized": true
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
                    required_fields = ['primary_overlay_position', 'positioning_strategy']
                    if all(field in positioning_decision for field in required_fields):
                        logger.info(f"🎯 Positioning Decision: {positioning_decision.get('primary_overlay_position')}")
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

    def create_colorful_text_hooks(self, topic: str, platform: str, video_duration: float,
                                  script_content: str) -> List[Dict[str, Any]]:
        """Create colorful text hooks and overlays using AI"""
        
        logger.info(f"🎨 Creating colorful text hooks for: {topic}")
        
        try:
            hooks_prompt = f"""
            You are a creative designer specializing in viral social media content.
            
            CONTENT DETAILS:
            - Topic: {topic}
            - Platform: {platform}
            - Duration: {video_duration} seconds
            - Script: {script_content[:300]}...
            
            TASK: Create engaging colorful text hooks and overlays that will make the video viral.
            
            REQUIREMENTS:
            1. Create 3-5 text hooks that appear at different times
            2. Use vibrant colors that grab attention
            3. Choose fonts that match the content style
            4. Position hooks strategically for maximum impact
            5. Include emojis and visual elements
            6. Make hooks short and punchy (max 15 characters)
            
            PLATFORM OPTIMIZATION:
            - TikTok: Bold, colorful, trending phrases
            - YouTube: Professional but engaging
            - Instagram: Aesthetic, hashtag-friendly
            
            Return JSON array of text hooks:
            [
                {{
                    "text": "🔥 VIRAL FACT!",
                    "start_time": 0.5,
                    "end_time": 3.0,
                    "position": "top_center",
                    "font_family": "Arial-Bold",
                    "font_size": 48,
                    "color": "#FF6B6B",
                    "background_color": "#FFFFFF",
                    "stroke_color": "#000000",
                    "stroke_width": 2,
                    "animation": "bounce",
                    "opacity": 0.9,
                    "reasoning": "Hook to grab attention early"
                }}
            ]
            """
            
            response = self.model.generate_content(hooks_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                try:
                    hooks_data = json.loads(json_match.group())
                    
                    # Validate and enhance hooks
                    validated_hooks = []
                    for hook in hooks_data:
                        if self._validate_hook(hook):
                            validated_hooks.append(hook)
                    
                    logger.info(f"🎨 Created {len(validated_hooks)} colorful text hooks")
                    return validated_hooks
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Failed to parse hooks JSON: {e}")
                    return self._get_fallback_hooks(topic, platform, video_duration)
            else:
                logger.warning("⚠️ No valid JSON found in hooks response")
                return self._get_fallback_hooks(topic, platform, video_duration)
                
        except Exception as e:
            logger.error(f"❌ Text hooks creation failed: {e}")
            return self._get_fallback_hooks(topic, platform, video_duration)

    def _validate_hook(self, hook: Dict[str, Any]) -> bool:
        """Validate a text hook has required fields"""
        required_fields = ['text', 'start_time', 'end_time', 'position', 'color']
        return all(field in hook for field in required_fields)

    def _get_fallback_hooks(self, topic: str, platform: str, video_duration: float) -> List[Dict[str, Any]]:
        """Create fallback text hooks when AI generation fails"""
        
        logger.info("🎨 Creating fallback colorful text hooks")
        
        # Create topic-specific hooks
        topic_words = topic.split()
        main_word = topic_words[0] if topic_words else "Content"
        
        fallback_hooks = [
            {
                "text": f"🔥 {main_word.upper()}!",
                "start_time": 0.5,
                "end_time": 3.0,
                "position": "top_center",
                "font_family": "Arial-Bold",
                "font_size": 48,
                "color": "#FF6B6B",
                "background_color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 2,
                "animation": "bounce",
                "opacity": 0.9,
                "reasoning": "Opening hook"
            },
            {
                "text": "💡 LEARN MORE",
                "start_time": video_duration * 0.4,
                "end_time": video_duration * 0.6,
                "position": "center",
                "font_family": "Arial-Bold",
                "font_size": 36,
                "color": "#4ECDC4",
                "background_color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 2,
                "animation": "fade",
                "opacity": 0.85,
                "reasoning": "Mid-content engagement"
            },
            {
                "text": "👆 FOLLOW!",
                "start_time": video_duration * 0.8,
                "end_time": video_duration,
                "position": "bottom_right",
                "font_family": "Arial-Bold",
                "font_size": 32,
                "color": "#45B7D1",
                "background_color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 2,
                "animation": "pulse",
                "opacity": 0.9,
                "reasoning": "Call to action"
            }
        ]
        
        # Filter hooks that fit within video duration
        valid_hooks = [hook for hook in fallback_hooks if hook['end_time'] <= video_duration]
        
        logger.info(f"🎨 Created {len(valid_hooks)} fallback text hooks")
        return valid_hooks

    def _get_fallback_positioning(self,
        platform: str,
        video_style: str) -> Dict[str, Any]:
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

        # CRITICAL FIX: Use dynamic positioning for TikTok viral content
        strategy = "dynamic" if platform == "tiktok" and duration_seconds <= 30 else "static"
        
        return {
            "primary_subtitle_position": primary_position,
            "secondary_overlay_position": secondary_position,
            "positioning_strategy": strategy,
            "safe_zones": ["bottom_third", "top_third"],
            "avoid_zones": ["center"],
            "reasoning": f"FIXED: Using {strategy} positioning for {platform} with {video_style} style - TikTok videos benefit from dynamic overlays",
            "mobile_optimized": True,
            "accessibility_compliant": True,
            "animation_enabled": strategy == "dynamic"
        }

    def calculate_precise_coordinates(self, position: str, video_width: int, video_height: int,
                                    text_width: int, text_height: int) -> tuple:
        """Calculate precise pixel coordinates for positioning"""

        # Define positioning zones as percentages
        position_map = {
            "top_third": (0.5, 0.15),          # Center horizontally, 15% from top
            "bottom_third": (0.5, 0.85),       # Center horizontally, 85% from top
            "center_safe": (0.5, 0.5),         # Dead center
            "center": (0.5, 0.5),              # Dead center (alias)
            "top_center": (0.5, 0.1),          # Top center
            "bottom_center": (0.5, 0.9),       # Bottom center
            "center_bottom": (0.5, 0.75),      # Center horizontally, 75% from top
            "left_side": (0.15, 0.5),          # 15% from left, center vertically
            "right_side": (0.85, 0.5),         # 85% from left, center vertically
            "top_left": (0.1, 0.1),            # Top left corner
            "top_right": (0.9, 0.1),           # Top right corner
            "bottom_left": (0.1, 0.9),         # Bottom left corner
            "bottom_right": (0.9, 0.9),        # Bottom right corner
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
            logger.warning(
                f"⚠️ Unknown position '{position}', "
                f"using center bottom: ({x}, {y})")
            return (x, y)
