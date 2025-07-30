"""
AI Agent for Building JSON Prompts
Converts missions and scripts into structured JSON prompts
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from ..generators.json_prompt_system import (
        VEOJsonPrompt, CameraConfig, LightingConfig, 
        SubjectConfig, SceneConfig, SegmentConfig,
        CameraMovement, ShotType, LightingStyle, VisualStyle
    )
    from ..models.video_models import Platform
    from ..utils.logging_config import get_logger
    from .gemini_helper import GeminiHelper
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from generators.json_prompt_system import (
        VEOJsonPrompt, CameraConfig, LightingConfig, 
        SubjectConfig, SceneConfig, SegmentConfig,
        CameraMovement, ShotType, LightingStyle, VisualStyle
    )
    from models.video_models import Platform
    from utils.logging_config import get_logger
    from agents.gemini_helper import GeminiHelper

logger = get_logger(__name__)


class JSONPromptBuilderAgent:
    """AI Agent that builds structured JSON prompts from missions"""
    
    def __init__(self, ai_model: str = "gemini-2.5-flash-lite"):
        self.gemini = GeminiHelper(model=ai_model)
        logger.info("🏗️ JSON Prompt Builder Agent initialized")
    
    async def build_json_prompt(self, 
                              mission: str,
                              script: str,
                              duration: float,
                              platform: Platform,
                              style: str = "viral",
                              segments: Optional[List[Dict]] = None) -> VEOJsonPrompt:
        """Build complete JSON prompt from mission and script"""
        
        logger.info(f"🏗️ Building JSON prompt for {platform.value} ({duration}s)")
        
        # Step 1: Analyze mission to extract key elements
        mission_analysis = await self._analyze_mission(mission)
        
        # Step 2: Generate camera and lighting decisions
        camera_config = await self._generate_camera_config(mission, script, style)
        lighting_config = await self._generate_lighting_config(mission, style, platform)
        
        # Step 3: Extract subject and scene if applicable
        subject_config = await self._extract_subject(mission, script)
        scene_config = await self._extract_scene(mission, script)
        
        # Step 4: Build segments if script has multiple parts
        json_segments = []
        if segments:
            json_segments = await self._build_segments(segments, mission, style)
        
        # Step 5: Determine visual style
        visual_style = await self._determine_visual_style(mission, style, platform)
        
        # Step 6: Generate keywords
        keywords = await self._generate_keywords(mission, platform, style)
        
        # Create the JSON prompt
        prompt = VEOJsonPrompt(
            description=mission_analysis.get('description', mission),
            style=visual_style,
            duration=duration,
            platform=platform,
            camera=camera_config,
            lighting=lighting_config,
            subject=subject_config,
            scene=scene_config,
            segments=json_segments,
            keywords=keywords,
            constraints=mission_analysis.get('constraints', [])
        )
        
        logger.info(f"✅ JSON prompt built: {len(json_segments)} segments, {len(keywords)} keywords")
        return prompt
    
    async def _analyze_mission(self, mission: str) -> Dict[str, Any]:
        """Analyze mission to extract key elements"""
        
        prompt = f"""Analyze this video mission and extract key elements:
Mission: {mission}

Extract:
1. A clear, visual description (1-2 sentences)
2. Any constraints mentioned (e.g., "no text", "family-friendly")
3. The main action or story
4. Target emotion or mood

Return as JSON:
{{
    "description": "clear visual description",
    "constraints": ["constraint1", "constraint2"],
    "main_action": "what happens",
    "mood": "emotional tone"
}}"""
        
        response = await self.gemini.generate_json(prompt)
        return response
    
    async def _generate_camera_config(self, mission: str, script: str, style: str) -> CameraConfig:
        """Generate camera configuration based on content"""
        
        prompt = f"""Based on this content, suggest camera settings:
Mission: {mission}
Style: {style}
Script preview: {script[:200]}...

Consider:
- Shot type (wide, medium, close, etc.)
- Camera movement (static, pan, dolly, etc.)
- Lens choice (24mm, 50mm, 85mm, etc.)
- Frame rate (24fps, 30fps, 60fps)

Return as JSON:
{{
    "shot_type": "medium_shot",
    "movement": "dolly_in",
    "lens": "50mm",
    "aperture": "f/2.8",
    "frame_rate": "24fps",
    "speed": "slow"
}}"""
        
        response = await self.gemini.generate_json(prompt)
        
        # Convert to enums
        try:
            shot_type = ShotType(response.get('shot_type', 'medium_shot'))
        except:
            shot_type = ShotType.MEDIUM
        
        try:
            movement = CameraMovement(response.get('movement', 'static'))
        except:
            movement = CameraMovement.STATIC
        
        return CameraConfig(
            shot_type=shot_type,
            movement=movement,
            lens=response.get('lens', '50mm'),
            aperture=response.get('aperture', 'f/2.8'),
            frame_rate=response.get('frame_rate', '24fps'),
            speed=response.get('speed')
        )
    
    async def _generate_lighting_config(self, mission: str, style: str, platform: Platform) -> LightingConfig:
        """Generate lighting configuration"""
        
        prompt = f"""Suggest lighting for this video:
Mission: {mission}
Style: {style}
Platform: {platform.value}

Consider platform preferences:
- Instagram: Bright, vibrant
- TikTok: Dynamic, trendy
- YouTube: Professional, cinematic

Return as JSON:
{{
    "style": "natural",
    "mood": "warm",
    "key_light": "window light from right",
    "color_temperature": "5600K"
}}"""
        
        response = await self.gemini.generate_json(prompt)
        
        try:
            lighting_style = LightingStyle(response.get('style', 'natural'))
        except:
            lighting_style = LightingStyle.NATURAL
        
        return LightingConfig(
            style=lighting_style,
            mood=response.get('mood', 'neutral'),
            key_light=response.get('key_light'),
            color_temperature=response.get('color_temperature')
        )
    
    async def _extract_subject(self, mission: str, script: str) -> Optional[SubjectConfig]:
        """Extract subject/character information if present"""
        
        prompt = f"""Extract character/subject details from this content:
Mission: {mission}
Script: {script[:300]}...

If there's a main character or subject, describe:
- Physical appearance
- Clothing/wardrobe
- Pose or expression
- Current action

Return as JSON (or null if no specific subject):
{{
    "description": "character description",
    "wardrobe": "what they're wearing",
    "pose": "body position",
    "expression": "facial expression",
    "action": "what they're doing"
}}"""
        
        response = await self.gemini.generate_json(prompt)
        
        if response and response.get('description'):
            return SubjectConfig(**response)
        return None
    
    async def _extract_scene(self, mission: str, script: str) -> Optional[SceneConfig]:
        """Extract scene/location information"""
        
        prompt = f"""Extract scene/location details:
Mission: {mission}
Script: {script[:300]}...

Describe:
- Location/setting
- Time of day
- Weather (if relevant)
- Important props or objects

Return as JSON:
{{
    "location": "where this takes place",
    "time_of_day": "morning/afternoon/evening/night",
    "weather": "if mentioned",
    "environment_details": "additional details",
    "props": ["prop1", "prop2"]
}}"""
        
        response = await self.gemini.generate_json(prompt)
        
        if response and response.get('location'):
            return SceneConfig(
                location=response['location'],
                time_of_day=response.get('time_of_day', 'day'),
                weather=response.get('weather'),
                environment_details=response.get('environment_details'),
                props=response.get('props', [])
            )
        return None
    
    async def _build_segments(self, segments: List[Dict], mission: str, style: str) -> List[SegmentConfig]:
        """Build segment configurations from script segments"""
        
        json_segments = []
        
        for i, segment in enumerate(segments):
            # Analyze each segment
            segment_text = segment.get('text', '')
            segment_duration = segment.get('duration', 5.0)
            
            prompt = f"""For this video segment, suggest visuals:
Segment {i+1}: {segment_text}
Duration: {segment_duration}s
Overall style: {style}

Suggest camera and scene for this specific moment.

Return as JSON:
{{
    "description": "what to show visually",
    "shot_type": "appropriate shot type",
    "camera_movement": "movement for this segment",
    "scene_detail": "specific location/action"
}}"""
            
            response = await self.gemini.generate_json(prompt)
            
            # Build segment config
            seg_config = SegmentConfig(
                duration=segment_duration,
                description=response.get('description', segment_text),
                camera=CameraConfig(
                    shot_type=ShotType(response.get('shot_type', 'medium_shot')) if response.get('shot_type') else ShotType.MEDIUM,
                    movement=CameraMovement(response.get('camera_movement', 'static')) if response.get('camera_movement') else CameraMovement.STATIC
                )
            )
            
            json_segments.append(seg_config)
        
        return json_segments
    
    async def _determine_visual_style(self, mission: str, style: str, platform: Platform) -> VisualStyle:
        """Determine the best visual style"""
        
        prompt = f"""Choose the best visual style:
Mission: {mission}
Requested style: {style}
Platform: {platform.value}

Options: realistic, cinematic, documentary, animation, cartoon, anime, retro, futuristic, minimalist, vintage, noir, vibrant, muted, dreamy

Choose ONE that best fits. Return just the style name."""
        
        response = await self.gemini.generate_text(prompt)
        
        try:
            return VisualStyle(response.strip().lower())
        except:
            # Default based on style
            if "educational" in style.lower():
                return VisualStyle.DOCUMENTARY
            elif "viral" in style.lower():
                return VisualStyle.VIBRANT
            else:
                return VisualStyle.CINEMATIC
    
    async def _generate_keywords(self, mission: str, platform: Platform, style: str) -> List[str]:
        """Generate relevant keywords"""
        
        prompt = f"""Generate 5-10 keywords for this video:
Mission: {mission}
Platform: {platform.value}
Style: {style}

Include:
- Platform-specific tags
- Style descriptors
- Content themes
- Technical terms

Return as JSON array: ["keyword1", "keyword2", ...]"""
        
        keywords = await self.gemini.generate_json(prompt)
        
        if isinstance(keywords, list):
            return keywords
        
        # Fallback
        return [platform.value, style, "viral", "hd", "professional"]
    
    def convert_to_veo_prompt(self, json_prompt: VEOJsonPrompt) -> str:
        """Convert JSON prompt to VEO-compatible string (fallback)"""
        
        # This is a fallback - ideally we send JSON directly
        parts = [json_prompt.description]
        
        if json_prompt.camera:
            parts.append(f"Shot with {json_prompt.camera.lens} lens, {json_prompt.camera.shot_type.value}")
            if json_prompt.camera.movement != CameraMovement.STATIC:
                parts.append(f"Camera movement: {json_prompt.camera.movement.value}")
        
        if json_prompt.lighting:
            parts.append(f"Lighting: {json_prompt.lighting.style.value}, {json_prompt.lighting.mood} mood")
        
        if json_prompt.style:
            parts.append(f"Visual style: {json_prompt.style.value if isinstance(json_prompt.style, VisualStyle) else json_prompt.style}")
        
        if json_prompt.keywords:
            parts.append(f"Keywords: {', '.join(json_prompt.keywords)}")
        
        return ". ".join(parts)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        builder = JSONPromptBuilderAgent()
        
        prompt = await builder.build_json_prompt(
            mission="Create a viral TikTok showing morning coffee routine",
            script="Wake up, stretch, make coffee, first sip reaction",
            duration=15.0,
            platform=Platform.TIKTOK,
            style="viral"
        )
        
        print(prompt.to_json())
    
    asyncio.run(test())