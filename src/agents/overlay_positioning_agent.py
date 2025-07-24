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
            1. Create 6-10 text hooks that appear at different times throughout the video
            2. Use sophisticated colors that grab attention (avoid redundant orange - use #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #54A0FF, #5F27CD, #00D2D3, #C44569, #2C3E50, #E74C3C)
            3. Choose professional fonts that match the content style (Helvetica-Bold, Arial-Bold, Impact, Georgia-Bold, Verdana-Bold, Trebuchet-Bold)
            4. Position hooks strategically for maximum impact
            5. Include emojis and visual elements
            6. Make hooks short and punchy (max 20 characters)
            7. Ensure hooks appear every 3-5 seconds for maximum engagement
            8. AVOID redundant orange colors - use diverse, sophisticated color palette
            
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
        
        # Generate more frequent hooks based on video duration
        num_hooks = max(6, min(12, int(video_duration / 3)))  # One hook every 3-5 seconds
        
        # Enhanced hook templates with better colors and fonts
        hook_templates = [
            {"text": f"🔥 {main_word.upper()}!", "color": "#FF6B6B", "font": "Helvetica-Bold", "position": "top_center", "animation": "bounce"},
            {"text": "💡 WATCH THIS!", "color": "#4ECDC4", "font": "Arial-Bold", "position": "center_right", "animation": "fade"},
            {"text": "😱 MIND BLOWN!", "color": "#45B7D1", "font": "Impact", "position": "top_right", "animation": "pulse"},
            {"text": "🚀 VIRAL CONTENT", "color": "#96CEB4", "font": "Helvetica-Bold", "position": "center_left", "animation": "bounce"},
            {"text": "⚡ AMAZING FACT!", "color": "#FECA57", "font": "Arial-Bold", "position": "top_left", "animation": "fade"},
            {"text": "🎯 MUST KNOW!", "color": "#FF9FF3", "font": "Impact", "position": "bottom_left", "animation": "pulse"},
            {"text": "🌟 INCREDIBLE!", "color": "#54A0FF", "font": "Helvetica-Bold", "position": "center_right", "animation": "bounce"},
            {"text": "🔥 SO TRUE!", "color": "#5F27CD", "font": "Arial-Bold", "position": "top_center", "animation": "fade"},
            {"text": "💯 FACTS ONLY!", "color": "#00D2D3", "font": "Impact", "position": "bottom_right", "animation": "pulse"},
            {"text": "👀 LOOK AT THIS!", "color": "#FF9F43", "font": "Helvetica-Bold", "position": "center_left", "animation": "bounce"},
            {"text": "🎉 AWESOME!", "color": "#C44569", "font": "Arial-Bold", "position": "top_right", "animation": "fade"},
            {"text": "👍 LIKE & FOLLOW!", "color": "#FECA57", "font": "Impact", "position": "bottom_right", "animation": "pulse"}
        ]
        
        # Enhanced color palette - removing redundant orange and using more sophisticated colors
        enhanced_colors = [
            "#FF6B6B",  # Coral Red
            "#4ECDC4",  # Turquoise
            "#45B7D1",  # Sky Blue
            "#96CEB4",  # Mint Green
            "#FECA57",  # Golden Yellow
            "#FF9FF3",  # Pink
            "#54A0FF",  # Blue
            "#5F27CD",  # Purple
            "#00D2D3",  # Cyan
            "#C44569",  # Rose
            "#2C3E50",  # Dark Blue
            "#E74C3C"   # Red
        ]
        
        # Enhanced font selection with better typography
        enhanced_fonts = [
            "Helvetica-Bold",
            "Arial-Bold", 
            "Impact",
            "Georgia-Bold",
            "Verdana-Bold",
            "Trebuchet-Bold"
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
                "font_size": 52 if i % 3 == 0 else 46,  # Larger fonts for better visibility
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
        # Default to dynamic for TikTok (most TikTok videos are short)
        strategy = "dynamic" if platform.lower() == "tiktok" else "static"
        
        return {
            "primary_overlay_position": primary_position,  # Changed from primary_subtitle_position for consistency
            "primary_subtitle_position": primary_position,  # Keep both for backward compatibility
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
            "bottom_third": (0.5, 0.65),       # Center horizontally, 65% from top (raised from 85%)
            "center_safe": (0.5, 0.5),         # Dead center
            "center": (0.5, 0.5),              # Dead center (alias)
            "top_center": (0.5, 0.1),          # Top center
            "bottom_center": (0.5, 0.75),       # Bottom center (raised from 90% to 75%)
            "center_bottom": (0.5, 0.65),      # Center horizontally, 65% from top (raised from 75%)
            "left_side": (0.15, 0.5),          # 15% from left, center vertically
            "right_side": (0.85, 0.5),         # 85% from left, center vertically
            "top_left": (0.1, 0.1),            # Top left corner
            "top_right": (0.9, 0.1),           # Top right corner
            "bottom_left": (0.1, 0.75),         # Bottom left corner (raised from 90%)
            "bottom_right": (0.9, 0.75),        # Bottom right corner (raised from 90%)
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
