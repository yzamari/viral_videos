"""
Smart Overlay Positioning Agent
AI agent that makes intelligent decisions about subtitle and
        text overlay positioning with colorful hooks and fonts
"""

import google.generativeai as genai
from typing import Dict, List, Any, Optional
from ..utils.logging_config import get_logger
from .gemini_helper import GeminiModelHelper, ensure_api_key
import json
import re

from ..config.ai_model_config import DEFAULT_AI_MODEL
logger = get_logger(__name__)

class OverlayPositioningAgent:
    """AI agent for smart subtitle and overlay positioning decisions with colorful hooks"""

    def __init__(self, api_key: str):
        """Initialize the positioning agent"""
        self.api_key = ensure_api_key(api_key)
        self.model = GeminiModelHelper.get_configured_model(self.api_key)

        logger.info("🎯 OverlayPositioningAgent initialized with colorful hooks support")

    def analyze_optimal_positioning(self, mission: str, video_style: str, platform: str,
                                  duration: float, subtitle_count: int) -> Dict[str, Any]:
        """Analyze optimal positioning for subtitles and colorful text overlays"""

        logger.info(f"🎯 Analyzing optimal positioning for: {mission}")
        logger.info(
            f"📱 Platform: {platform}, "
            f"Style: {video_style}, "
            f"Duration: {duration}s")

        try:
            # Optimized concise prompt for faster processing
            positioning_prompt = f"""
Overlay positioning for: "{mission}"
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
            1. Create 10-15 text hooks that appear at different times throughout the video
            2. Use ULTRA VIBRANT neon colors that pop on screen:
               - Neon Pink: #FF10F0
               - Electric Blue: #00F5FF
               - Lime Green: #39FF14
               - Hot Magenta: #FF00FF
               - Cyber Yellow: #FFD700
               - Neon Purple: #9D00FF
               - Electric Red: #FF073A
               - Neon Orange: #FF6700
               - Bright Cyan: #00FFFF
               - Hot Pink: #FF69B4
            3. Use BOLD, TRENDY fonts: Impact, Bebas-Neue, Anton-Regular, Oswald-Bold, Montserrat-Black
            4. Add ANIMATED effects: bounce, glow, pulse, slide, zoom, shake, rotate
            5. Include LOTS of emojis and visual elements 🔥✨💥🚀⚡️💎🎯🌟
            6. Make hooks SUPER short and catchy (max 15 characters)
            7. Ensure hooks appear every 2-4 seconds for MAXIMUM engagement
            8. Use gradient backgrounds, neon glows, and shadow effects for depth
            9. Mix uppercase and lowercase for visual interest
            10. Add motion keywords: SWIPE!, TAP!, WATCH!, WAIT!, OMG!, WOW!
            
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
                    "font_family": "Helvetica-Bold",
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
        """Create fallback text hooks when AI generation fails with improved styling"""
        
        logger.info("🎨 Creating enhanced fallback text hooks with better fonts and colors")
        
        # Create topic-specific hooks
        topic_words = topic.split()
        main_word = topic_words[0] if topic_words else "Content"
        
        # Generate MANY MORE frequent hooks based on video duration
        num_hooks = max(10, min(20, int(video_duration / 2)))  # One hook every 2-3 seconds for MAXIMUM engagement
        
        # ULTRA VIBRANT hook templates with NEON colors and trendy fonts
        hook_templates = [
            {"text": f"🔥 {main_word.upper()}!", "color": "#FF10F0", "font": "Impact", "position": "top_center", "animation": "bounce"},
            {"text": "💥 WAIT FOR IT!", "color": "#00F5FF", "font": "Impact", "position": "center_right", "animation": "shake"},
            {"text": "😱 OMG!", "color": "#39FF14", "font": "Impact", "position": "top_right", "animation": "zoom"},
            {"text": "🚀 SWIPE UP!", "color": "#FF00FF", "font": "Impact", "position": "center_left", "animation": "pulse"},
            {"text": "⚡ WOW!", "color": "#FFD700", "font": "Impact", "position": "top_left", "animation": "glow"},
            {"text": "🎯 TAP HERE!", "color": "#9D00FF", "font": "Impact", "position": "top_center", "animation": "rotate"},
            {"text": "🌟 INSANE!", "color": "#FF073A", "font": "Impact", "position": "center_right", "animation": "bounce"},
            {"text": "💎 NO WAY!", "color": "#FF6700", "font": "Impact", "position": "top_center", "animation": "slide"},
            {"text": "💯 FACTS!", "color": "#00FFFF", "font": "Impact", "position": "top_right", "animation": "shake"},
            {"text": "👀 LOOK!", "color": "#FF69B4", "font": "Impact", "position": "center_left", "animation": "zoom"},
            {"text": "✨ VIRAL!", "color": "#FF10F0", "font": "Impact", "position": "top_right", "animation": "glow"},
            {"text": "🎉 LET'S GO!", "color": "#00F5FF", "font": "Impact", "position": "center_right", "animation": "pulse"},
            {"text": "🔥 SO LIT!", "color": "#39FF14", "font": "Impact", "position": "top_left", "animation": "rotate"},
            {"text": "💥 BOOM!", "color": "#FF00FF", "font": "Impact", "position": "center_left", "animation": "bounce"},
            {"text": "⚡ WATCH!", "color": "#FFD700", "font": "Impact", "position": "top_center", "animation": "slide"}
        ]
        
        # ULTRA VIBRANT NEON color palette for maximum visual impact
        enhanced_colors = [
            "#FF10F0",  # Neon Pink
            "#00F5FF",  # Electric Blue
            "#39FF14",  # Lime Green
            "#FF00FF",  # Hot Magenta
            "#FFD700",  # Cyber Yellow
            "#9D00FF",  # Neon Purple
            "#FF073A",  # Electric Red
            "#FF6700",  # Neon Orange
            "#00FFFF",  # Bright Cyan
            "#FF69B4",  # Hot Pink
            "#FFFF00",  # Pure Yellow
            "#00FF00"   # Pure Green
        ]
        
        # BOLD TRENDY fonts for maximum impact
        enhanced_fonts = [
            "Impact",
            "Impact",  # Use Impact more often - it's the most viral
            "Arial-Black", 
            "Impact",
            "Helvetica-Bold",
            "Impact"
        ]
        
        fallback_hooks = []
        # Calculate hook duration as a percentage of video duration (8-10% of total, max 3 seconds)
        hook_duration = min(3.0, max(1.5, video_duration * 0.08))
        time_per_hook = video_duration / num_hooks
        
        for i in range(num_hooks):
            template = hook_templates[i % len(hook_templates)]
            start_time = i * time_per_hook + 0.5
            end_time = min(start_time + hook_duration, video_duration - 0.5)
            
            # Skip if would go beyond video duration
            if start_time >= video_duration - 1:
                break
            
            # Choose enhanced color and font
            color = enhanced_colors[i % len(enhanced_colors)]
            font = enhanced_fonts[i % len(enhanced_fonts)]
            
            # Remove redundant orange colors - replace with better alternatives
            if color in ["#FF9F43", "#FECA57"]:  # Orange variants
                color = enhanced_colors[(i + 3) % len(enhanced_colors)]  # Skip to next color
                
            fallback_hooks.append({
                "text": template["text"],
                "start_time": start_time,
                "end_time": end_time,
                "position": template["position"],
                "font_family": font,
                "font_size": 64 if i % 3 == 0 else 58,  # MUCH LARGER fonts for viral impact
                "color": color,
                "background_color": "#000000" if i % 2 == 0 else "#FFFFFF",
                "stroke_color": "#FFFFFF" if i % 2 == 0 else "#000000",
                "stroke_width": 3,
                "animation": template["animation"],
                "opacity": 0.95,
                "reasoning": f"Enhanced hook {i+1} with better typography and color selection"
            })
        
        # Filter hooks that fit within video duration
        valid_hooks = [hook for hook in fallback_hooks if hook['end_time'] <= video_duration]
        
        logger.info(f"🎨 Created {len(valid_hooks)} enhanced fallback text hooks with improved styling")
        return valid_hooks

    def _get_fallback_positioning(self,
        platform: str,
        video_style: str) -> Dict[str, Any]:
        """Fallback positioning strategy based on platform and style"""

        # CRITICAL FIX: Separate overlay and subtitle positioning to avoid conflicts
        # Subtitles typically appear in bottom third, so overlays should go elsewhere
        
        # Platform-specific defaults with subtitle conflict avoidance
        if platform.lower() in ['tiktok', 'youtube_shorts']:
            # Overlays in top area to avoid subtitle conflicts
            primary_position = "top_center"
            secondary_position = "top_right"
            subtitle_position = "bottom_center"  # Subtitles stay at bottom
        elif platform.lower() in ['instagram', 'reels']:
            # Overlays in middle to top area
            primary_position = "center_top"
            secondary_position = "top_left"
            subtitle_position = "bottom_center"
        else:
            # YouTube - use upper area for overlays, lower for subtitles
            primary_position = "top_center"
            secondary_position = "center_right"
            subtitle_position = "bottom_center"

        # CRITICAL FIX: Use dynamic positioning for TikTok viral content
        # Default to dynamic for TikTok (most TikTok videos are short)
        strategy = "dynamic" if platform.lower() == "tiktok" else "static"
        
        return {
            "primary_overlay_position": primary_position,  # Overlays positioned to avoid subtitles
            "primary_subtitle_position": subtitle_position,  # Subtitles in dedicated area
            "secondary_overlay_position": secondary_position,
            "positioning_strategy": strategy,
            "safe_zones": ["top_third", "center"],  # Safe zones for overlays
            "subtitle_safe_zone": "bottom_third",    # Reserved area for subtitles
            "avoid_zones": ["bottom_third"],         # Overlays avoid subtitle area
            "reasoning": f"FIXED: Using {strategy} positioning for {platform} with {video_style} style - overlays positioned in top/center to avoid subtitle conflicts in bottom third",
            "mobile_optimized": True,
            "accessibility_compliant": True,
            "animation_enabled": strategy == "dynamic",
            "overlay_subtitle_separation": True  # Flag indicating separation strategy
        }

    def calculate_precise_coordinates(self, position: str, video_width: int, video_height: int,
                                    text_width: int, text_height: int) -> tuple:
        """Calculate precise pixel coordinates for positioning"""

        # Define positioning zones as percentages with clear overlay/subtitle separation
        position_map = {
            # OVERLAY ZONES (Upper 2/3 of screen to avoid subtitle conflicts)
            "top_third": (0.5, 0.15),          # Center horizontally, 15% from top
            "center_safe": (0.5, 0.4),         # Upper center area - safe from subtitles
            "center": (0.5, 0.4),              # Upper center area (moved up from 50%)
            "top_center": (0.5, 0.08),         # Top center - well above subtitles
            "center_top": (0.5, 0.25),         # Center-top area for overlays
            "left_side": (0.15, 0.35),         # 15% from left, upper center
            "right_side": (0.85, 0.35),        # 85% from left, upper center
            "center_left": (0.25, 0.35),       # Center-left, upper area
            "center_right": (0.75, 0.35),      # Center-right, upper area
            "top_left": (0.1, 0.1),            # Top left corner
            "top_right": (0.9, 0.1),           # Top right corner
            
            # SUBTITLE ZONES (Lower 1/3 of screen reserved for subtitles)
            "bottom_third": (0.5, 0.85),       # Subtitle area - bottom third
            "bottom_center": (0.5, 0.85),      # Bottom center for subtitles
            "center_bottom": (0.5, 0.85),      # Same as bottom_center for subtitles
            "bottom_left": (0.1, 0.85),        # Bottom left for subtitles
            "bottom_right": (0.9, 0.85),       # Bottom right for subtitles
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
            y = int((video_height * 0.75) - (text_height / 2))
            logger.warning(
                f"⚠️ Unknown position '{position}', "
                f"using center bottom: ({x}, {y})")
            return (x, y)
