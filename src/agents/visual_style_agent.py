"""
Visual Style Agent - AI-powered visual style analysis and optimization
"""

import json
import re
from typing import Dict, Any, Optional
from ..utils.logging_config import get_logger

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = get_logger(__name__)

class VisualStyleAgent:
    """AI agent for visual style analysis and optimization"""
    
    def __init__(self, api_key: str):
        """Initialize Visual Style Agent"""
        self.api_key = api_key
        
        if genai:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        logger.info("🎨 VisualStyleAgent initialized")
    
    def analyze_optimal_style(self, topic: str, target_audience: str, platform: str, 
                            content_type: str = "general", humor_level: str = "medium") -> Dict[str, Any]:
        """
        Analyze and determine optimal visual style for content
        
        Args:
            topic: Content topic/subject
            target_audience: Target audience description
            platform: Target platform (tiktok, youtube, instagram, etc.)
            content_type: Type of content (educational, entertainment, etc.)
            humor_level: Level of humor (low, medium, high)
            
        Returns:
            Dictionary with style decision and reasoning
        """
        try:
            logger.info(f"🎨 Analyzing optimal visual style for: {topic}")
            logger.info(f"👥 Audience: {target_audience}, Platform: {platform}")
            
            # Optimized concise prompt for faster processing
            style_prompt = f"""
Analyze visual style for: "{topic}"
Platform: {platform}
Audience: {target_audience}

Choose optimal style from: realistic, cartoon, disney, anime, comic, minimalist, retro, cyberpunk, watercolor, clay

Platform preferences:
- TikTok/Instagram: Creative, animated styles
- YouTube: Mix of realistic and animated
- LinkedIn: Professional, realistic

Return JSON:
{{
    "primary_style": "style_name",
    "color_palette": "vibrant|muted|pastel|natural",
    "reasoning": "Brief explanation",
    "engagement_prediction": "high|medium|low"
}}
"""

            response = self.model.generate_content(style_prompt)

            # Check if response is valid
            if not response or not response.text:
                logger.warning("⚠️ Empty response from Visual Style API")
                return self._get_fallback_style(topic, target_audience, platform)

            # Parse the response
            try:
                response_text = response.text.strip()
                
                # Check if response is empty
                if not response_text:
                    logger.warning("⚠️ Empty response text from Visual Style API")
                    return self._get_fallback_style(topic, target_audience, platform)

                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    style_decision = json.loads(json_match.group())

                    logger.info(f"🎨 Style Decision: {style_decision.get('primary_style')}")
                    logger.info(f"🎨 Color Palette: {style_decision.get('color_palette')}")
                    logger.info(f"📊 Engagement Prediction: {style_decision.get('engagement_prediction')}")
                    logger.info(f"💭 Reasoning: {style_decision.get('reasoning', '')[:100]}...")

                    return style_decision
                else:
                    logger.warning("⚠️ No JSON found in Visual Style response")
                    return self._get_fallback_style(topic, target_audience, platform)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Could not parse style decision: {e}")
                return self._get_fallback_style(topic, target_audience, platform)
            except Exception as e:
                logger.error(f"❌ Style analysis failed: {e}")
                return self._get_fallback_style(topic, target_audience, platform)
                
        except Exception as e:
            logger.error(f"❌ Visual style analysis failed: {e}")
            return self._get_fallback_style(topic, target_audience, platform)

    def _get_fallback_style(self, topic: str, target_audience: str, platform: str) -> Dict[str, Any]:
        """Fallback style decision based on topic and audience"""

        topic_lower = topic.lower()
        platform_lower = platform.lower()
        audience_lower = target_audience.lower()

        # Platform-based defaults
        if 'tiktok' in platform_lower:
            if any(word in audience_lower for word in ['young', 'teen', 'gen z', 'student']):
                primary_style = 'cartoon'
                color_palette = 'vibrant'
                engagement_prediction = 'high'
            else:
                primary_style = 'comic'
                color_palette = 'vibrant'
                engagement_prediction = 'high'
        elif 'linkedin' in platform_lower:
            primary_style = 'realistic'
            color_palette = 'muted'
            engagement_prediction = 'medium'
        elif 'youtube' in platform_lower:
            primary_style = 'realistic'
            color_palette = 'natural'
            engagement_prediction = 'medium'
        else:
            # Default for unknown platforms
            primary_style = 'realistic'
            color_palette = 'natural'
            engagement_prediction = 'medium'

        # Topic-based adjustments
        if any(word in topic_lower for word in ['education', 'tutorial', 'how to', 'learn']):
            primary_style = 'realistic'
            color_palette = 'natural'
        elif any(word in topic_lower for word in ['funny', 'comedy', 'humor', 'meme']):
            primary_style = 'cartoon'
            color_palette = 'vibrant'
            engagement_prediction = 'high'

        return {
            'primary_style': primary_style,
            'secondary_style': None,
            'style_intensity': 'medium',
            'color_palette': color_palette,
            'visual_effects': [],
            'reasoning': f'Fallback style decision based on platform ({platform}) and topic analysis. This is a safe default that should work well for most content.',
            'engagement_prediction': engagement_prediction,
            'appropriateness_score': 0.8
        }

    def generate_style_prompt_enhancement(self, base_prompt: str, style_decision: Dict[str, Any]) -> str:
        """
        Enhance a base prompt with style-specific instructions
        
        Args:
            base_prompt: Original video generation prompt
            style_decision: Style decision from analyze_optimal_style
            
        Returns:
            Enhanced prompt with style instructions
        """
        try:
            primary_style = style_decision.get('primary_style', 'realistic')
            color_palette = style_decision.get('color_palette', 'natural')
            visual_effects = style_decision.get('visual_effects', [])
            
            # Build style enhancement
            style_enhancements = []
            
            # Add primary style
            style_enhancements.append(f"in {primary_style} style")
            
            # Add color palette
            if color_palette:
                style_enhancements.append(f"with {color_palette} colors")
            
            # Add visual effects
            if visual_effects:
                effects_str = ", ".join(visual_effects)
                style_enhancements.append(f"featuring {effects_str}")
            
            # Combine enhancements
            enhancement_text = ", ".join(style_enhancements)
            
            # Create enhanced prompt
            enhanced_prompt = f"{base_prompt}, {enhancement_text}"
            
            logger.info(f"🎨 Enhanced prompt with {primary_style} style")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"❌ Prompt enhancement failed: {e}")
            return base_prompt

    def enhance_prompt_with_style(self, base_prompt: str, style: str) -> str:
        """
        Simple prompt enhancement with a specific style
        
        Args:
            base_prompt: Original prompt
            style: Style to apply
            
        Returns:
            Enhanced prompt
        """
        try:
            # Style mapping
            style_mappings = {
                'realistic': 'photorealistic, high quality, detailed',
                'cartoon': 'animated, colorful, playful cartoon style',
                'disney': 'Disney animation style, magical, family-friendly',
                'anime': 'anime style, expressive, dramatic',
                'comic': 'comic book style, bold colors, action-oriented',
                'minimalist': 'clean, simple, modern, minimalist design',
                'retro': 'vintage, nostalgic, retro aesthetic',
                'cyberpunk': 'futuristic, neon, high-tech, cyberpunk style',
                'watercolor': 'watercolor painting style, soft, artistic',
                'clay': 'claymation style, tactile, quirky'
            }
            
            style_description = style_mappings.get(style.lower())
            if style_description:
                return f"{base_prompt}, {style_description}"
            else:
                logger.warning(f"⚠️ Unknown style: {style}")
                return base_prompt
                
        except Exception as e:
            logger.error(f"❌ Simple style enhancement failed: {e}")
            return base_prompt
