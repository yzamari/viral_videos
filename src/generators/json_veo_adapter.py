"""
JSON VEO Adapter - Integrates JSON prompt system with VEO clients
"""

import json
from typing import Dict, Any, Optional, Union, List

try:
    from ..generators.json_prompt_system import VEOJsonPrompt, JSONPromptValidator, GeneratorType
    from ..generators.veo_client_factory import VeoClientFactory, VeoModel
    from ..utils.logging_config import get_logger
    from ..utils.session_context import SessionContext
    from ..models.video_models import Platform
except ImportError:
    from generators.json_prompt_system import VEOJsonPrompt, JSONPromptValidator, GeneratorType
    from generators.veo_client_factory import VeoClientFactory, VeoModel
    from utils.logging_config import get_logger
    from utils.session_context import SessionContext
    from models.video_models import Platform

logger = get_logger(__name__)


class JSONVEOAdapter:
    """Adapter to use JSON prompts with VEO generation"""
    
    def __init__(self):
        self.veo_factory = VeoClientFactory()
        self.validator = JSONPromptValidator()
        logger.info("🔄 JSON VEO Adapter initialized")
    
    def generate_video_from_json(self,
                                json_prompt: Union[VEOJsonPrompt, Dict[str, Any], str],
                                session_context: SessionContext,
                                veo_model: VeoModel = VeoModel.VEO3_FAST,  # Default to VEO-3 fast for cost savings
                                clip_id: str = "json-clip") -> str:
        """
        Generate video using JSON prompt
        
        Args:
            json_prompt: Can be VEOJsonPrompt object, dict, or JSON string
            session_context: Session context for output
            veo_model: Which VEO model to use
            clip_id: Unique clip identifier
            
        Returns:
            Path to generated video
        """
        
        # Convert input to VEOJsonPrompt if needed
        if isinstance(json_prompt, str):
            try:
                json_data = json.loads(json_prompt)
                json_prompt = VEOJsonPrompt.from_dict(json_data)
                logger.info("📄 Parsed JSON string to VEOJsonPrompt")
            except json.JSONDecodeError:
                # Maybe it's not JSON but a regular prompt
                logger.warning("⚠️ Failed to parse as JSON, treating as text prompt")
                return self._generate_from_text(json_prompt, session_context, veo_model, clip_id)
        elif isinstance(json_prompt, dict):
            json_prompt = VEOJsonPrompt.from_dict(json_prompt)
            logger.info("📄 Converted dict to VEOJsonPrompt")
        
        # Validate prompt
        generator_type = GeneratorType.VEO2 if veo_model == VeoModel.VEO2 else GeneratorType.VEO3
        valid, errors = self.validator.validate(json_prompt, generator_type)
        
        if not valid:
            logger.error(f"❌ Invalid JSON prompt: {errors}")
            raise ValueError(f"Invalid JSON prompt: {', '.join(errors)}")
        
        # Enhance with platform defaults
        json_prompt = self.validator.enhance(json_prompt, json_prompt.platform)
        
        logger.info(f"🎬 Generating video from JSON prompt:")
        logger.info(f"   Model: {veo_model.value}")
        logger.info(f"   Duration: {json_prompt.duration}s")
        logger.info(f"   Style: {json_prompt.style}")
        logger.info(f"   Platform: {json_prompt.platform.value}")
        
        # Get VEO client with aspect ratio awareness
        output_dir = session_context.get_output_path("video_clips", "veo_clips")
        aspect_ratio = json_prompt.aspect_ratio if json_prompt.aspect_ratio else "16:9"
        
        veo_client = self.veo_factory.get_aspect_ratio_aware_client(
            output_dir=output_dir,
            aspect_ratio=aspect_ratio
        )
        
        # Convert to JSON string for VEO
        json_string = json_prompt.to_json(pretty=True)
        
        logger.info("📤 Sending JSON to VEO:")
        logger.info(json_string[:500] + "..." if len(json_string) > 500 else json_string)
        
        # Generate video with JSON
        try:
            video_path = veo_client.generate_video(
                prompt=json_string,  # Send raw JSON
                duration=json_prompt.duration,
                clip_id=clip_id,
                aspect_ratio=json_prompt.aspect_ratio
            )
            
            logger.info(f"✅ Video generated from JSON: {video_path}")
            
            # Save JSON prompt for reference
            json_path = session_context.get_output_path("metadata", f"{clip_id}_prompt.json")
            with open(json_path, 'w') as f:
                f.write(json_string)
            logger.info(f"💾 JSON prompt saved: {json_path}")
            
            return video_path
            
        except Exception as e:
            logger.error(f"❌ VEO generation failed: {e}")
            
            # Fallback: Try converting to text prompt
            logger.info("🔄 Attempting fallback to text prompt")
            text_prompt = self._json_to_text_fallback(json_prompt)
            return self._generate_from_text(text_prompt, session_context, veo_model, clip_id)
    
    def _generate_from_text(self, text_prompt: str, session_context: SessionContext,
                          veo_model: VeoModel, clip_id: str) -> str:
        """Generate video from text prompt (fallback)"""
        
        output_dir = session_context.get_output_path("video_clips", "veo_clips")
        # Default to 16:9 for text prompts (no aspect ratio specified)
        veo_client = self.veo_factory.get_aspect_ratio_aware_client(
            output_dir=output_dir,
            aspect_ratio="16:9"  # Default for text prompts
        )
        
        return veo_client.generate_video(
            prompt=text_prompt,
            duration=8.0,  # Default duration
            clip_id=clip_id
        )
    
    def _json_to_text_fallback(self, json_prompt: VEOJsonPrompt) -> str:
        """Convert JSON prompt to text as fallback"""
        
        parts = [json_prompt.description]
        
        # Add style
        if json_prompt.style:
            style_str = json_prompt.style.value if hasattr(json_prompt.style, 'value') else str(json_prompt.style)
            parts.append(f"in {style_str} style")
        
        # Add camera info
        if json_prompt.camera:
            cam = json_prompt.camera
            parts.append(f"Shot with {cam.lens} lens")
            if cam.movement and hasattr(cam.movement, 'value'):
                parts.append(f"{cam.movement.value} camera movement")
            if cam.shot_type and hasattr(cam.shot_type, 'value'):
                parts.append(f"{cam.shot_type.value}")
        
        # Add lighting
        if json_prompt.lighting:
            light = json_prompt.lighting
            if light.style and hasattr(light.style, 'value'):
                parts.append(f"{light.style.value} lighting")
            if light.mood:
                parts.append(f"{light.mood} mood")
        
        # Add subject
        if json_prompt.subject:
            if json_prompt.subject.description:
                parts.append(f"featuring {json_prompt.subject.description}")
            if json_prompt.subject.wardrobe:
                parts.append(f"wearing {json_prompt.subject.wardrobe}")
        
        # Add scene
        if json_prompt.scene:
            if json_prompt.scene.location:
                parts.append(f"in {json_prompt.scene.location}")
            if json_prompt.scene.time_of_day:
                parts.append(f"during {json_prompt.scene.time_of_day}")
        
        # Add constraints
        if json_prompt.constraints:
            for constraint in json_prompt.constraints:
                parts.append(constraint)
        
        # Add keywords
        if json_prompt.keywords:
            parts.append(f"Keywords: {', '.join(json_prompt.keywords)}")
        
        return ". ".join(parts)
    
    def generate_multi_segment_video(self,
                                   json_prompt: VEOJsonPrompt,
                                   session_context: SessionContext,
                                   veo_model: VeoModel = VeoModel.VEO3_FAST) -> Dict[str, Any]:  # Default to VEO-3 fast
        """Generate video with multiple segments"""
        
        if not json_prompt.segments:
            # Single segment video
            video_path = self.generate_video_from_json(json_prompt, session_context, veo_model)
            return {
                "final_video": video_path,
                "segments": [video_path]
            }
        
        logger.info(f"🎬 Generating multi-segment video: {len(json_prompt.segments)} segments")
        
        segment_videos = []
        
        for i, segment in enumerate(json_prompt.segments):
            # Create individual prompt for each segment
            segment_prompt = VEOJsonPrompt(
                description=segment.description,
                style=json_prompt.style,
                duration=segment.duration,
                platform=json_prompt.platform,
                aspect_ratio=json_prompt.aspect_ratio,
                camera=segment.camera or json_prompt.camera,
                lighting=json_prompt.lighting,
                subject=segment.subject or json_prompt.subject,
                scene=segment.scene or json_prompt.scene,
                effects=json_prompt.effects,
                keywords=json_prompt.keywords
            )
            
            # Generate segment video
            clip_id = f"segment_{i+1}"
            video_path = self.generate_video_from_json(
                segment_prompt, 
                session_context,
                veo_model,
                clip_id
            )
            
            segment_videos.append(video_path)
            logger.info(f"✅ Generated segment {i+1}/{len(json_prompt.segments)}")
        
        # TODO: Concatenate segments into final video
        # For now, return the segments
        return {
            "final_video": None,  # Would concatenate here
            "segments": segment_videos
        }


# Integration helper
class VEOJSONIntegration:
    """Helper to integrate JSON prompts into existing workflow"""
    
    @staticmethod
    def should_use_json(mission: str, platform: Platform) -> bool:
        """Determine if JSON prompts should be used"""
        
        # Use JSON for complex missions or specific platforms
        complex_indicators = [
            "multiple scenes",
            "specific camera",
            "cinematic",
            "professional",
            "technical",
            "precise timing",
            "synchronized"
        ]
        
        mission_lower = mission.lower()
        
        # Check for complexity indicators
        for indicator in complex_indicators:
            if indicator in mission_lower:
                return True
        
        # Platform preferences
        if platform == Platform.YOUTUBE:
            return True  # YouTube benefits from precise control
        
        return False
    
    @staticmethod
    async def create_json_prompt_from_decisions(decisions: Dict[str, Any],
                                              script: str,
                                              segments: Optional[List[Dict]] = None) -> VEOJsonPrompt:
        """Create JSON prompt from existing decision framework"""
        
        from ..agents.json_prompt_builder_agent import JSONPromptBuilderAgent
        
        builder = JSONPromptBuilderAgent()
        
        json_prompt = await builder.build_json_prompt(
            mission=decisions.get('mission', ''),
            script=script,
            duration=decisions.get('duration_seconds', 30),
            platform=Platform(decisions.get('platform', 'instagram')),
            style=decisions.get('style', 'viral'),
            segments=segments
        )
        
        return json_prompt