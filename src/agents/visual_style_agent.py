"""
Visual Style Agent - AI-powered visual style analysis and optimization
"""

import json
import re
from typing import Dict, Any, Optional
from ..utils.logging_config import get_logger
from .gemini_helper import GeminiModelHelper, ensure_api_key

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = get_logger(__name__)

class VisualStyleAgent:
    """AI agent for visual style analysis and optimization"""
    
    def __init__(self, api_key: str):
        """Initialize Visual Style Agent"""
        self.api_key = ensure_api_key(api_key)
        
        if genai:
            self.model = GeminiModelHelper.get_configured_model(self.api_key, 'gemini-2.5-flash')
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
        """Fallback style decision based on topic and audience with improved typography and colors"""

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

        # Topic-based adjustments with priority for serious content
        serious_keywords = ['veteran', 'ptsd', 'military', 'health', 'mental', 'trauma', 'medical', 'war', 
                           'soldier', 'depression', 'anxiety', 'therapy', 'serious', 'important', 'awareness']
        educational_keywords = ['education', 'tutorial', 'how to', 'learn', 'fact', 'knowledge', 'science']
        humor_keywords = ['funny', 'comedy', 'humor', 'meme', 'joke', 'laugh']
        
        if any(word in topic_lower for word in serious_keywords):
            primary_style = 'realistic'
            color_palette = 'muted'
            engagement_prediction = 'medium'
        elif any(word in topic_lower for word in educational_keywords):
            primary_style = 'realistic'
            color_palette = 'natural'
            engagement_prediction = 'medium'
        elif any(word in topic_lower for word in humor_keywords):
            primary_style = 'cartoon'
            color_palette = 'vibrant'
            engagement_prediction = 'high'

        # Enhanced typography selection
        enhanced_fonts = {
            'professional': ['Helvetica-Bold', 'Arial-Bold', 'Georgia-Bold'],
            'casual': ['Arial-Bold', 'Verdana-Bold', 'Trebuchet-Bold'],
            'impact': ['Impact', 'Helvetica-Bold', 'Arial-Bold'],
            'elegant': ['Georgia-Bold', 'Helvetica-Bold', 'Arial-Bold']
        }

        # Enhanced color palette - avoiding redundant orange
        enhanced_colors = {
            'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#54A0FF', '#5F27CD', '#00D2D3', '#C44569'],
            'muted': ['#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7', '#ECF0F1'],
            'natural': ['#27AE60', '#2ECC71', '#3498DB', '#9B59B6', '#E67E22', '#E74C3C'],
            'professional': ['#2C3E50', '#34495E', '#E74C3C', '#3498DB', '#27AE60', '#F39C12']
        }

        # Select appropriate fonts and colors
        font_style = 'professional' if 'professional' in primary_style else 'casual'
        selected_fonts = enhanced_fonts[font_style]
        selected_colors = enhanced_colors[color_palette]

        return {
            'primary_style': primary_style,
            'color_palette': color_palette,
            'engagement_prediction': engagement_prediction,
            'typography': {
                'primary_font': selected_fonts[0],
                'secondary_font': selected_fonts[1],
                'accent_font': selected_fonts[2],
                'font_weights': ['normal', 'bold', 'extra-bold']
            },
            'colors': {
                'primary': selected_colors[0],
                'secondary': selected_colors[1],
                'accent': selected_colors[2],
                'text': '#FFFFFF' if color_palette in ['vibrant', 'natural'] else '#000000',
                'background': '#000000' if color_palette in ['vibrant', 'natural'] else '#FFFFFF'
            },
            'reasoning': f'Enhanced fallback style: {primary_style} with {color_palette} palette, avoiding redundant orange colors'
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
            # Comprehensive Style Mapping - 100+ Visual Styles
            style_mappings = {
                # Photographic & Realistic Styles
                'realistic': 'photorealistic, high quality, detailed, lifelike',
                'photorealistic': 'ultra-realistic, professional photography, crisp details',
                'cinematic': 'cinematic lighting, dramatic composition, film-like quality',
                'documentary': 'documentary style, authentic, real-world settings',
                'portrait': 'portrait photography, focused composition, professional lighting',
                'landscape': 'landscape photography, wide vistas, natural beauty',
                'street': 'street photography, candid moments, urban environments',
                'macro': 'macro photography, extreme close-ups, fine details',
                'black_and_white': 'monochrome, black and white, classic photography',
                'sepia': 'sepia tone, vintage photography, warm brown tints',
                'high_contrast': 'high contrast, dramatic shadows and highlights',
                'low_key': 'low key lighting, dramatic shadows, moody atmosphere',
                'high_key': 'high key lighting, bright, airy, optimistic feel',
                'golden_hour': 'golden hour lighting, warm sunset glow',
                'blue_hour': 'blue hour lighting, twilight atmosphere',
                'neon': 'neon lighting, vibrant colors, urban nightlife',
                'natural_light': 'natural lighting, soft shadows, organic feel',
                'studio': 'studio lighting, controlled environment, clean backgrounds',
                'candid': 'candid photography, natural moments, unposed',
                'dynamic': 'dynamic composition, movement, energy, action-packed',
                
                # Animation & Cartoon Styles
                'cartoon': 'animated, colorful, playful cartoon style',
                'disney': 'Disney animation style, magical, family-friendly',
                'pixar': 'Pixar 3D animation style, vibrant, heartwarming',
                'anime': 'anime style, expressive, dramatic, Japanese animation',
                'manga': 'manga style, black and white, detailed linework',
                'comic': 'comic book style, bold colors, action-oriented',
                'comic_book': 'comic book illustration, speech bubbles, dynamic panels',
                'graphic_novel': 'graphic novel style, sophisticated storytelling',
                'webcomic': 'webcomic style, digital art, modern humor',
                'superhero': 'superhero comic style, bold, powerful, heroic',
                'chibi': 'chibi style, cute, small proportions, adorable',
                'kawaii': 'kawaii style, cute, pastel colors, Japanese cute culture',
                'cel_shading': 'cel shading, flat colors, anime-inspired',
                'toon_shading': 'toon shading, stylized lighting, cartoon-like',
                'flash_animation': 'Flash animation style, vector graphics, smooth motion',
                'stop_motion': 'stop motion animation, tactile, handcrafted feel',
                'claymation': 'claymation style, clay figures, quirky texture',
                'clay': 'clay animation, moldable characters, playful texture',
                'puppet': 'puppet animation, string puppets, theatrical',
                'paper_cutout': 'paper cutout animation, flat layers, handmade',
                'silhouette': 'silhouette animation, shadow play, dramatic',
                
                # Artistic & Painting Styles
                'watercolor': 'watercolor painting style, soft, artistic, flowing',
                'oil_painting': 'oil painting style, rich textures, classical art',
                'acrylic': 'acrylic painting style, vibrant colors, modern art',
                'gouache': 'gouache painting style, opaque watercolor, illustration',
                'tempera': 'tempera painting style, traditional medium, smooth finish',
                'fresco': 'fresco painting style, wall painting, renaissance',
                'impressionist': 'impressionist style, light and color, loose brushstrokes',
                'expressionist': 'expressionist style, emotional, distorted reality',
                'cubist': 'cubist style, geometric shapes, multiple perspectives',
                'surrealist': 'surrealist style, dreamlike, impossible scenarios',
                'abstract': 'abstract art style, non-representational, conceptual',
                'pointillism': 'pointillism style, dots of color, neo-impressionist',
                'pop_art': 'pop art style, bold colors, commercial imagery',
                'art_nouveau': 'art nouveau style, flowing lines, natural forms',
                'art_deco': 'art deco style, geometric patterns, luxury aesthetics',
                'baroque': 'baroque style, ornate, dramatic, religious themes',
                'renaissance': 'renaissance style, classical beauty, realistic proportions',
                'medieval': 'medieval art style, illuminated manuscripts, religious',
                'byzantine': 'byzantine art style, golden backgrounds, religious icons',
                'japanese_ink': 'Japanese ink painting, minimalist, zen-like',
                'chinese_brush': 'Chinese brush painting, traditional, flowing strokes',
                'calligraphy': 'calligraphic style, elegant lettering, artistic writing',
                
                # Design & Illustration Styles
                'minimalist': 'clean, simple, modern, minimalist design',
                'maximalist': 'maximalist design, busy, ornate, decorative',
                'flat_design': 'flat design, simple shapes, no gradients',
                'material_design': 'material design, Google style, cards and shadows',
                'skeuomorphic': 'skeuomorphic design, realistic textures, dimensional',
                'isometric': 'isometric design, 3D perspective, technical illustration',
                'vector': 'vector illustration, scalable graphics, clean lines',
                'line_art': 'line art illustration, simple lines, minimal color',
                'geometric': 'geometric design, shapes and patterns, mathematical',
                'organic': 'organic design, natural forms, flowing curves',
                'technical': 'technical illustration, precise, instructional',
                'infographic': 'infographic style, data visualization, informative',
                'logo_design': 'logo design style, brand identity, memorable',
                'typography': 'typography-focused, text as art, letterforms',
                'monoline': 'monoline illustration, single line weight, modern',
                'duotone': 'duotone style, two-color palette, high contrast',
                'gradient': 'gradient design, color transitions, modern',
                'neon_gradient': 'neon gradient, vibrant transitions, futuristic',
                
                # Genre & Thematic Styles
                'cyberpunk': 'futuristic, neon, high-tech, cyberpunk style',
                'steampunk': 'steampunk style, Victorian era, brass and gears',
                'dieselpunk': 'dieselpunk style, 1940s aesthetic, industrial',
                'biopunk': 'biopunk style, organic technology, biotechnology',
                'space_opera': 'space opera style, grand scale, futuristic',
                'fantasy': 'fantasy style, magical, mythical creatures',
                'medieval_fantasy': 'medieval fantasy, castles, dragons, knights',
                'urban_fantasy': 'urban fantasy, modern world with magic',
                'horror': 'horror style, dark, scary, unsettling',
                'gothic': 'gothic style, dark, mysterious, ornate',
                'noir': 'film noir style, high contrast, shadows, mystery',
                'western': 'western style, cowboys, desert landscapes',
                'post_apocalyptic': 'post-apocalyptic, destroyed world, survival',
                'utopian': 'utopian style, perfect world, optimistic future',
                'dystopian': 'dystopian style, oppressive society, dark future',
                'vintage': 'vintage style, nostalgic, aged appearance',
                'retro': 'retro aesthetic, past decades, nostalgic',
                'retro_futurism': 'retro-futurism, 1950s vision of future',
                'vaporwave': 'vaporwave aesthetic, 80s nostalgia, neon pastels',
                'synthwave': 'synthwave style, 80s neon, outrun aesthetic',
                'cottagecore': 'cottagecore aesthetic, rural, cozy, natural',
                'dark_academia': 'dark academia, scholarly, gothic architecture',
                'light_academia': 'light academia, bright, intellectual, classical',
                
                # Cultural & Historical Styles
                'japanese': 'Japanese art style, traditional aesthetics',
                'chinese': 'Chinese art style, traditional culture',
                'indian': 'Indian art style, rich colors, intricate patterns',
                'african': 'African art style, tribal patterns, earth tones',
                'aztec': 'Aztec art style, geometric patterns, ancient civilization',
                'egyptian': 'Egyptian art style, hieroglyphs, ancient symbols',
                'greek': 'Greek art style, classical proportions, marble',
                'roman': 'Roman art style, imperial grandeur, classical',
                'viking': 'Viking art style, Norse mythology, runic symbols',
                'celtic': 'Celtic art style, intricate knots, mystical',
                'native_american': 'Native American art style, spiritual, nature-based',
                'persian': 'Persian art style, intricate carpets, miniatures',
                'islamic': 'Islamic art style, geometric patterns, calligraphy',
                'tibetan': 'Tibetan art style, Buddhist themes, spiritual',
                'mayan': 'Mayan art style, complex calendars, jungle themes',
                
                # Texture & Material Styles
                'wood': 'wood texture, natural grain, organic material',
                'metal': 'metal texture, industrial, reflective surfaces',
                'glass': 'glass texture, transparent, reflective',
                'fabric': 'fabric texture, soft, textile patterns',
                'paper': 'paper texture, handmade, organic feel',
                'stone': 'stone texture, rough, natural materials',
                'marble': 'marble texture, luxury, classical architecture',
                'concrete': 'concrete texture, industrial, modern architecture',
                'brick': 'brick texture, urban, architectural',
                'leather': 'leather texture, luxury, crafted materials',
                'fur': 'fur texture, soft, natural animal textures',
                'water': 'water effects, flowing, reflective surfaces',
                'fire': 'fire effects, dynamic, warm energy',
                'smoke': 'smoke effects, ethereal, atmospheric',
                'crystal': 'crystal texture, geometric, magical',
                'holographic': 'holographic effects, rainbow, futuristic',
                'glitch': 'glitch effects, digital corruption, cyberpunk',
                'pixelated': 'pixelated style, retro gaming, 8-bit aesthetic',
                'low_poly': 'low poly style, geometric, minimalist 3D',
                'high_poly': 'high poly style, detailed 3D, smooth surfaces',
                'wireframe': 'wireframe style, technical, blueprint-like',
                'x_ray': 'x-ray style, transparent, medical imaging',
                'thermal': 'thermal imaging style, heat signatures, scientific',
                'microscopic': 'microscopic style, cellular, scientific detail',
                'astronomical': 'astronomical style, cosmic, space imagery',
                'underwater': 'underwater style, aquatic, marine life',
                'aerial': 'aerial view style, bird\'s eye perspective',
                'cross_section': 'cross-section style, technical, educational',
                'blueprint': 'blueprint style, technical drawings, architectural',
                'schematic': 'schematic style, technical diagrams, instructional'
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
