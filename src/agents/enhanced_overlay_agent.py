"""
Enhanced Overlay Agent - Next-generation AI-driven overlay system
Uses FFmpeg for better performance and cooler effects
"""

import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OverlayEffect(Enum):
    """Advanced overlay effects"""
    FADE_IN = "fade_in"
    SLIDE_IN_LEFT = "slide_in_left" 
    SLIDE_IN_RIGHT = "slide_in_right"
    SLIDE_IN_UP = "slide_in_up"
    SLIDE_IN_DOWN = "slide_in_down"
    BOUNCE = "bounce"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ROTATE_IN = "rotate_in"
    SHAKE = "shake"
    PULSE = "pulse"
    GLOW = "glow"
    TYPEWRITER = "typewriter"
    NEON = "neon"
    GLITCH = "glitch"
    RAINBOW = "rainbow"
    FIRE = "fire"
    ELECTRIC = "electric"

class OverlayTrigger(Enum):
    """When overlays should appear"""
    TIME_BASED = "time_based"
    CONTENT_BASED = "content_based"
    EMOTION_PEAK = "emotion_peak"
    HOOK_MOMENT = "hook_moment"
    CTA_MOMENT = "cta_moment"
    TRANSITION = "transition"

@dataclass
class EnhancedOverlay:
    """Enhanced overlay with advanced styling and effects"""
    text: str
    start_time: float
    duration: float
    
    # Position & Layout
    x_position: str  # Can be formula like "(w-text_w)/2" or "w*0.1"
    y_position: str  # Can be formula like "h*0.8" or "100"
    anchor: str = "center"  # center, top-left, top-right, etc.
    
    # Typography
    font_family: str = "Arial"
    font_size: int = 32
    font_weight: str = "bold"  # normal, bold, black
    font_color: str = "#FFFFFF"
    
    # Background & Effects
    background_enabled: bool = True
    background_color: str = "#000000@0.7"
    border_width: int = 0
    border_color: str = "#FFFFFF"
    shadow_enabled: bool = True
    shadow_color: str = "#000000@0.8"
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    
    # Animation & Effects
    effect: OverlayEffect = OverlayEffect.FADE_IN
    trigger: OverlayTrigger = OverlayTrigger.TIME_BASED
    
    # Advanced Properties
    z_index: int = 1  # Layer ordering
    opacity: float = 1.0
    rotation: float = 0.0
    scale: float = 1.0
    
    # AI-Generated Properties
    purpose: str = ""  # Why this overlay exists
    emotion: str = "neutral"  # excited, urgent, calm, etc.
    importance: int = 5  # 1-10 priority
    
    def to_ffmpeg_drawtext(self) -> str:
        """Convert to FFmpeg drawtext filter"""
        
        # Build basic drawtext parameters
        params = [
            f"text='{self._escape_text(self.text)}'",
            f"fontfile='{self._get_font_path()}'",
            f"fontsize={self.font_size}",
            f"fontcolor={self.font_color}",
            f"x={self.x_position}",
            f"y={self.y_position}"
        ]
        
        # Add background box
        if self.background_enabled:
            params.extend([
                "box=1",
                f"boxcolor={self.background_color}",
                f"boxborderw={max(5, self.font_size // 8)}"
            ])
        
        # Add shadow
        if self.shadow_enabled:
            params.extend([
                f"shadowcolor={self.shadow_color}",
                f"shadowx={self.shadow_offset_x}",
                f"shadowy={self.shadow_offset_y}"
            ])
        
        # Add border
        if self.border_width > 0:
            params.extend([
                f"borderw={self.border_width}",
                f"bordercolor={self.border_color}"
            ])
        
        # Add timing
        if self.duration > 0:
            params.append(f"enable=between(t\\,{self.start_time}\\,{self.start_time + self.duration})")
        else:
            params.append(f"enable=gte(t\\,{self.start_time})")
        
        # Add animation effects
        if self.effect != OverlayEffect.FADE_IN:
            params.extend(self._get_animation_params())
        
        return "drawtext=" + ":".join(params)
    
    def _get_animation_params(self) -> List[str]:
        """Get animation parameters for FFmpeg"""
        t_start = self.start_time
        t_end = self.start_time + self.duration
        
        if self.effect == OverlayEffect.SLIDE_IN_LEFT:
            return [f"x=if(lt(t,{t_start}),-text_w,{self.x_position}+(text_w*(1-min(1,(t-{t_start})/0.5))))"]
        
        elif self.effect == OverlayEffect.SLIDE_IN_RIGHT:
            return [f"x=if(lt(t,{t_start}),w,{self.x_position}-(text_w*(1-min(1,(t-{t_start})/0.5))))"]
        
        elif self.effect == OverlayEffect.SLIDE_IN_UP:
            return [f"y=if(lt(t,{t_start}),-text_h,{self.y_position}+(text_h*(1-min(1,(t-{t_start})/0.5))))"]
        
        elif self.effect == OverlayEffect.SLIDE_IN_DOWN:
            return [f"y=if(lt(t,{t_start}),h,{self.y_position}-(text_h*(1-min(1,(t-{t_start})/0.5))))"]
        
        elif self.effect == OverlayEffect.BOUNCE:
            return [
                f"y={self.y_position}+abs(20*sin(8*PI*(t-{t_start})))*exp(-2*(t-{t_start}))"
            ]
        
        elif self.effect == OverlayEffect.PULSE:
            return [
                f"fontsize={self.font_size}*(1+0.2*sin(4*PI*(t-{t_start})))"
            ]
        
        elif self.effect == OverlayEffect.SHAKE:
            return [
                f"x={self.x_position}+5*sin(16*PI*(t-{t_start}))",
                f"y={self.y_position}+3*cos(20*PI*(t-{t_start}))"
            ]
        
        elif self.effect == OverlayEffect.ZOOM_IN:
            scale_factor = f"min(1,2*(t-{t_start})/0.5)"
            return [f"fontsize={self.font_size}*{scale_factor}"]
        
        elif self.effect == OverlayEffect.RAINBOW:
            # Cycle through colors
            return [
                f"fontcolor=hsv2rgb(360*fmod(t-{t_start},3)/3,1,1)"
            ]
        
        return []
    
    def _escape_text(self, text: str) -> str:
        """Escape text for FFmpeg"""
        text = text.replace("\\", "\\\\")
        text = text.replace("'", "\\'") 
        text = text.replace(":", "\\:")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace(",", "\\,")
        text = text.replace(";", "\\;")
        return text
    
    def _get_font_path(self) -> str:
        """Get system font path"""
        font_paths = {
            "Arial": "/System/Library/Fonts/Arial.ttf",
            "Helvetica": "/System/Library/Fonts/Helvetica.ttc",
            "Impact": "/System/Library/Fonts/Impact.ttc",
            "Comic Sans MS": "/System/Library/Fonts/Comic Sans MS.ttf",
            "Times": "/System/Library/Fonts/Times.ttc"
        }
        return font_paths.get(self.font_family, font_paths["Arial"])

class EnhancedOverlayAgent:
    """Next-generation AI overlay agent with advanced effects"""
    
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
        logger.info("🎨 Enhanced Overlay Agent initialized")
    
    async def generate_viral_overlays(self, mission: str, script: str, 
                                    duration: float, platform: str,
                                    style: str, segments: List[Dict]) -> List[EnhancedOverlay]:
        """Generate viral-worthy overlays using advanced AI analysis"""
        
        prompt = f"""
You are a viral video overlay expert. Create ATTENTION-GRABBING overlays that will make viewers stop scrolling.

CONTENT ANALYSIS:
Mission: {mission}
Platform: {platform} 
Duration: {duration}s
Style: {style}
Script: {script}

SEGMENTS WITH TIMING:
{json.dumps(segments, indent=2)}

Create 8-12 overlays that will:
1. 🎯 HOOK viewers in first 3 seconds
2. 📈 Highlight key moments that build engagement  
3. 🔥 Add viral elements (emojis, trending phrases)
4. 💡 Emphasize important information
5. 📣 Include strategic CTAs throughout (not just end)
6. ⚡ Use platform-specific viral tactics
7. 🎨 Mix different visual styles for variety

OVERLAY TYPES TO USE:
- Hook: Attention-grabbing opener ("🚨 THIS WILL BLOW YOUR MIND")
- Stat: Key statistics with impact ("📊 95% of people don't know this")  
- Quote: Memorable soundbites ("💬 Expert says...")
- Emoji: Reaction overlays ("🤯", "💯", "🔥")
- Question: Engagement drivers ("🤔 Can you guess why?")
- CTA: Action prompts ("👆 DOUBLE TAP if you agree")
- Countdown: Urgency creators ("⏰ Only 10 seconds left")
- Reveal: "Wait for it..." moments

For each overlay, provide:
{{
    "text": "Short punchy text (3-8 words max)",
    "start_time": 5.2,
    "duration": 2.5,
    "x_position": "(w-text_w)/2",  // Can use formulas
    "y_position": "h*0.2",         // Can use math expressions  
    "font_size": 36,
    "font_color": "#FF6B6B",       // Vibrant colors
    "background_color": "#000000@0.8",
    "effect": "bounce",            // bounce, slide_in_left, pulse, shake, zoom_in, rainbow
    "purpose": "Hook attention at video start",
    "emotion": "excited",          // excited, urgent, surprised, mysterious
    "importance": 8               // 1-10 priority
}}

PLATFORM OPTIMIZATION:
- {platform}: Use {self._get_platform_style(platform)}

Return JSON array of overlay objects. Make them VIRAL! 🚀
"""
        
        try:
            text_service = self.ai_manager.get_service("text_generation")
            
            # Create request object (import locally to avoid circular imports)
            try:
                from ..utils.ai_service_types import TextGenerationRequest
            except ImportError:
                # Fallback for simple request structure
                class TextGenerationRequest:
                    def __init__(self, prompt, max_tokens, temperature):
                        self.prompt = prompt
                        self.max_tokens = max_tokens
                        self.temperature = temperature
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=1200,
                temperature=0.8  # Higher creativity for viral content
            )
            
            response = await text_service.generate_text(request)
            overlay_data = json.loads(response.text)
            
            # Convert to EnhancedOverlay objects
            overlays = []
            for data in overlay_data:
                overlay = EnhancedOverlay(
                    text=data.get('text', '🔥 VIRAL MOMENT'),
                    start_time=float(data.get('start_time', 0)),
                    duration=float(data.get('duration', 3)),
                    x_position=data.get('x_position', '(w-text_w)/2'),
                    y_position=data.get('y_position', 'h*0.1'),
                    font_size=int(data.get('font_size', 32)),
                    font_color=data.get('font_color', '#FFFFFF'),
                    background_color=data.get('background_color', '#000000@0.7'),
                    effect=OverlayEffect(data.get('effect', 'fade_in')),
                    purpose=data.get('purpose', ''),
                    emotion=data.get('emotion', 'neutral'),
                    importance=int(data.get('importance', 5))
                )
                overlays.append(overlay)
            
            logger.info(f"🎨 Generated {len(overlays)} viral overlays")
            return overlays
            
        except Exception as e:
            logger.error(f"AI overlay generation failed: {e}")
            return self._get_fallback_viral_overlays(duration)
    
    def _get_platform_style(self, platform: str) -> str:
        """Get platform-specific viral overlay style"""
        styles = {
            "instagram": "Bright colors, emojis, story-style text, short punchy phrases",
            "tiktok": "Bold text, trending sounds callouts, challenge references, Gen-Z language", 
            "youtube": "Professional but engaging, longer text allowed, educational elements",
            "twitter": "News-style, breaking alerts, thread indicators, hashtag callouts"
        }
        return styles.get(platform.lower(), "Engaging and attention-grabbing")
    
    def _get_fallback_viral_overlays(self, duration: float) -> List[EnhancedOverlay]:
        """Fallback viral overlays if AI fails"""
        return [
            EnhancedOverlay(
                text="🚨 VIRAL ALERT",
                start_time=0.5,
                duration=2.0,
                x_position="(w-text_w)/2",
                y_position="h*0.1", 
                font_size=40,
                font_color="#FF0040",
                effect=OverlayEffect.BOUNCE,
                purpose="Hook attention",
                emotion="excited",
                importance=10
            ),
            EnhancedOverlay(
                text="💯 YOU WON'T BELIEVE",
                start_time=duration * 0.3,
                duration=2.5,
                x_position="w*0.05",
                y_position="h*0.3",
                font_size=32,
                font_color="#00FF80",
                effect=OverlayEffect.SLIDE_IN_LEFT,
                purpose="Build curiosity",
                emotion="mysterious", 
                importance=8
            ),
            EnhancedOverlay(
                text="👆 DOUBLE TAP NOW",
                start_time=duration - 4,
                duration=4.0,
                x_position="(w-text_w)/2",
                y_position="h*0.8",
                font_size=36,
                font_color="#FFD700",
                effect=OverlayEffect.PULSE,
                purpose="Drive engagement",
                emotion="urgent",
                importance=9
            )
        ]
        
    def convert_to_ffmpeg_filters(self, overlays: List[EnhancedOverlay]) -> str:
        """Convert overlays to FFmpeg filter chain"""
        if not overlays:
            return ""
        
        # Sort by z_index and start_time
        sorted_overlays = sorted(overlays, key=lambda x: (x.z_index, x.start_time))
        
        # Generate drawtext filters
        filters = []
        for overlay in sorted_overlays:
            filters.append(overlay.to_ffmpeg_drawtext())
        
        return ",".join(filters)