"""
Visual Style Agent
AI agent that decides the optimal visual style for video generation
"""

import google.generativeai as genai
from typing import Dict, List, Any
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class VisualStyleAgent:
    """AI agent for determining optimal visual style for video content"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        logger.info("🎨 VisualStyleAgent initialized")
    
    def analyze_optimal_style(self, topic: str, target_audience: str, platform: str, 
                            content_type: str, humor_level: str = "medium") -> Dict[str, Any]:
        """Analyze and decide optimal visual style for the content"""
        
        logger.info(f"🎨 Analyzing optimal visual style for: {topic}")
        logger.info(f"👥 Audience: {target_audience}, Platform: {platform}")
        
        try:
            style_prompt = f"""
            You are an expert creative director specializing in video content styles for social media.
            
            CONTENT DETAILS:
            - Topic: {topic}
            - Target Audience: {target_audience}
            - Platform: {platform}
            - Content Type: {content_type}
            - Humor Level: {humor_level}
            
            TASK: Decide the optimal visual style that will maximize engagement and appropriateness.
            
            AVAILABLE VISUAL STYLES:
            1. "realistic" - Photorealistic, documentary-style, professional
            2. "cartoon" - Animated, colorful, playful, stylized
            3. "disney" - Disney-style animation, magical, family-friendly
            4. "anime" - Japanese animation style, expressive, dramatic
            5. "comic" - Comic book style, bold colors, action-oriented
            6. "minimalist" - Clean, simple, modern, abstract
            7. "retro" - Vintage, nostalgic, classic aesthetics
            8. "cyberpunk" - Futuristic, neon, high-tech, edgy
            9. "watercolor" - Artistic, soft, painterly, elegant
            10. "clay" - Claymation style, tactile, quirky, charming
            
            DECISION FACTORS:
            - Topic appropriateness (educational topics may prefer realistic)
            - Audience preferences (young people often prefer animated styles)
            - Platform culture (TikTok loves creative styles, LinkedIn prefers professional)
            - Humor integration (cartoon styles work better for comedy)
            - Content complexity (simple topics can use more stylized approaches)
            
            PLATFORM CONSIDERATIONS:
            - TikTok: Creative, animated, eye-catching styles preferred
            - YouTube Shorts: Mix of realistic and animated works well
            - Instagram Reels: Aesthetic, visually appealing styles
            - LinkedIn: Professional, realistic styles preferred
            
            AUDIENCE CONSIDERATIONS:
            - Young people (13-25): Prefer animated, cartoon, anime styles
            - Adults (26-45): Mix of realistic and stylized content
            - Professionals: Realistic, minimalist, clean styles
            - Students: Educational content with engaging visuals
            
            Return a JSON decision with this structure:
            {{
                "primary_style": "realistic|cartoon|disney|anime|comic|minimalist|retro|cyberpunk|watercolor|clay",
                "secondary_style": "optional_secondary_style_for_variety",
                "style_intensity": "low|medium|high",
                "color_palette": "vibrant|muted|monochrome|pastel|neon|natural",
                "visual_effects": ["effect1", "effect2"],
                "reasoning": "Detailed explanation of style choice",
                "engagement_prediction": "high|medium|low",
                "appropriateness_score": 0.95
            }}
            """
            
            response = self.model.generate_content(style_prompt)
            
            # Parse the response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                style_decision = json.loads(json_match.group())
                
                logger.info(f"🎨 Style Decision: {style_decision.get('primary_style')}")
                logger.info(f"🎨 Color Palette: {style_decision.get('color_palette')}")
                logger.info(f"📊 Engagement Prediction: {style_decision.get('engagement_prediction')}")
                logger.info(f"💭 Reasoning: {style_decision.get('reasoning', '')[:100]}...")
                
                return style_decision
            else:
                logger.warning("⚠️ Could not parse style decision, using fallback")
                return self._get_fallback_style(topic, target_audience, platform)
                
        except Exception as e:
            logger.error(f"❌ Style analysis failed: {e}")
            return self._get_fallback_style(topic, target_audience, platform)
    
    def _get_fallback_style(self, topic: str, target_audience: str, platform: str) -> Dict[str, Any]:
        """Fallback style decision based on topic and audience"""
        
        topic_lower = topic.lower()
        audience_lower = target_audience.lower()
        platform_lower = platform.lower()
        
        # Topic-based style decisions
        if any(word in topic_lower for word in ['quantum', 'physics', 'math', 'science', 'theorem']):
            primary_style = "minimalist"
            color_palette = "muted"
        elif any(word in topic_lower for word in ['cartoon', 'funny', 'comedy', 'humor', 'chimpanzee']):
            primary_style = "cartoon"
            color_palette = "vibrant"
        elif any(word in topic_lower for word in ['war', 'military', 'nato', 'conflict']):
            primary_style = "realistic"
            color_palette = "muted"
        elif any(word in topic_lower for word in ['disney', 'magical', 'fantasy']):
            primary_style = "disney"
            color_palette = "pastel"
        else:
            # Default based on audience and platform
            if 'young' in audience_lower or platform_lower in ['tiktok', 'youtube_shorts']:
                primary_style = "cartoon"
                color_palette = "vibrant"
            else:
                primary_style = "realistic"
                color_palette = "natural"
        
        return {
            "primary_style": primary_style,
            "secondary_style": None,
            "style_intensity": "medium",
            "color_palette": color_palette,
            "visual_effects": ["smooth_transitions"],
            "reasoning": f"Fallback style selection for {topic} targeting {target_audience}",
            "engagement_prediction": "medium",
            "appropriateness_score": 0.8
        }
    
    def generate_style_prompt_enhancement(self, base_prompt: str, style_decision: Dict[str, Any]) -> str:
        """Enhance a base prompt with style-specific instructions"""
        
        primary_style = style_decision.get('primary_style', 'realistic')
        color_palette = style_decision.get('color_palette', 'natural')
        style_intensity = style_decision.get('style_intensity', 'medium')
        
        # Style-specific prompt enhancements
        style_enhancements = {
            'realistic': f"photorealistic, high quality, professional cinematography, natural lighting",
            'cartoon': f"cartoon style, animated, colorful, playful, stylized characters",
            'disney': f"Disney animation style, magical, enchanting, family-friendly, beautiful characters",
            'anime': f"anime style, Japanese animation, expressive characters, dramatic lighting",
            'comic': f"comic book style, bold outlines, vibrant colors, action-oriented",
            'minimalist': f"minimalist design, clean lines, simple shapes, modern aesthetic",
            'retro': f"retro style, vintage aesthetics, nostalgic feel, classic design",
            'cyberpunk': f"cyberpunk style, futuristic, neon lights, high-tech, edgy atmosphere",
            'watercolor': f"watercolor painting style, soft edges, artistic, painterly texture",
            'clay': f"claymation style, clay figures, tactile texture, stop-motion feel"
        }
        
        # Color palette enhancements
        color_enhancements = {
            'vibrant': "bright vibrant colors, high saturation, energetic palette",
            'muted': "muted colors, soft tones, subtle palette, professional look",
            'monochrome': "black and white, grayscale, classic monochrome aesthetic",
            'pastel': "pastel colors, soft hues, gentle palette, dreamy atmosphere",
            'neon': "neon colors, glowing effects, electric palette, futuristic feel",
            'natural': "natural colors, earth tones, realistic palette, organic feel"
        }
        
        # Intensity modifiers
        intensity_modifiers = {
            'low': "subtle, understated, gentle",
            'medium': "balanced, moderate, well-defined",
            'high': "bold, dramatic, intense, striking"
        }
        
        # Build enhanced prompt
        style_enhancement = style_enhancements.get(primary_style, style_enhancements['realistic'])
        color_enhancement = color_enhancements.get(color_palette, color_enhancements['natural'])
        intensity_modifier = intensity_modifiers.get(style_intensity, intensity_modifiers['medium'])
        
        enhanced_prompt = f"{base_prompt}, {style_enhancement}, {color_enhancement}, {intensity_modifier} style"
        
        logger.info(f"🎨 Enhanced prompt with {primary_style} style")
        return enhanced_prompt
    
    def enhance_prompt_with_style(self, base_prompt: str, style: str) -> str:
        """Enhance a base prompt with the specified style - compatibility method"""
        
        # Create a style decision dict for the given style
        style_decision = {
            'primary_style': style,
            'color_palette': 'vibrant' if style in ['cartoon', 'anime', 'comic'] else 'natural',
            'style_intensity': 'medium'
        }
        
        return self.generate_style_prompt_enhancement(base_prompt, style_decision) 