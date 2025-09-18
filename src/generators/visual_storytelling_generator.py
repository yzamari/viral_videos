"""
Visual Storytelling Script Generator
Generates scripts optimized for visual medium with clear, concrete scenes
"""
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from ..utils.logging_config import get_logger
    from ..models.video_models import Platform
    from ..utils.session_context import SessionContext
    from ..agents.gemini_helper import GeminiModelHelper, ensure_api_key
except ImportError:
    from src.utils.logging_config import get_logger
    from src.models.video_models import Platform
    from src.utils.session_context import SessionContext
    from src.agents.gemini_helper import GeminiModelHelper, ensure_api_key

logger = get_logger(__name__)


class SceneType(Enum):
    """Types of scenes for visual storytelling"""
    ESTABLISHING = "establishing"  # Sets location/context
    ACTION = "action"  # Shows activity/movement
    EMOTION = "emotion"  # Focus on feelings/reactions
    TRANSITION = "transition"  # Bridges between scenes
    CLIMAX = "climax"  # Peak moment
    RESOLUTION = "resolution"  # Conclusion/outcome


@dataclass
class VisualScene:
    """Represents a single visual scene"""
    scene_number: int
    duration: float
    scene_type: SceneType
    visual_description: str  # What we see
    action: str  # What happens
    dialogue: str  # What is said
    camera_direction: str  # How to shoot it
    emotion: str  # Emotional tone
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'scene_number': self.scene_number,
            'duration': self.duration,
            'scene_type': self.scene_type.value,
            'visual_description': self.visual_description,
            'action': self.action,
            'dialogue': self.dialogue,
            'camera_direction': self.camera_direction,
            'emotion': self.emotion
        }


class VisualStorytellingGenerator:
    """Generates scripts with strong visual storytelling"""
    
    def __init__(self, session_context: Optional[SessionContext] = None):
        """Initialize the visual storytelling generator"""
        self.session_context = session_context
        self.api_key = ensure_api_key()
        logger.info("🎬 Visual Storytelling Generator initialized")
    
    def generate_visual_script(self, 
                              mission: str,
                              duration: int,
                              platform: Platform = Platform.YOUTUBE,
                              style: str = "cinematic",
                              tone: str = "engaging") -> Dict[str, Any]:
        """
        Generate a script optimized for visual storytelling
        
        Args:
            mission: The story/message to convey
            duration: Total duration in seconds
            platform: Target platform
            style: Visual style
            tone: Emotional tone
            
        Returns:
            Script with visual scenes
        """
        logger.info(f"🎨 Generating visual script for: {mission[:100]}...")
        
        # Calculate scene structure
        num_scenes = self._calculate_scene_count(duration)
        scenes = self._generate_scenes(mission, num_scenes, duration, style, tone)
        
        # Create script structure
        script = self._assemble_script(scenes, mission, platform)
        
        # Validate and optimize
        script = self._validate_visual_coherence(script)
        
        logger.info(f"✅ Visual script generated with {len(scenes)} scenes")
        return script
    
    def _calculate_scene_count(self, duration: int) -> int:
        """Calculate optimal number of scenes based on duration"""
        # Optimal scene length is 5-8 seconds for engagement
        if duration <= 30:
            return max(3, duration // 7)  # 3-4 scenes for short videos
        elif duration <= 60:
            return duration // 8  # 7-8 second scenes
        else:
            return duration // 10  # Longer scenes for longer videos
    
    def _generate_scenes(self, 
                        mission: str,
                        num_scenes: int,
                        duration: int,
                        style: str,
                        tone: str) -> List[VisualScene]:
        """Generate individual visual scenes"""
        model = GeminiModelHelper(api_key=self.api_key)
        
        # Create scene generation prompt
        prompt = f"""
Create {num_scenes} visual scenes for this story:
MISSION: {mission}
DURATION: {duration} seconds total
STYLE: {style}
TONE: {tone}

CRITICAL REQUIREMENTS:
1. Each scene must be VISUALLY CONCRETE - describe what we SEE, not abstract concepts
2. Use SHOW DON'T TELL - convey information through visuals and action
3. Each scene should have clear visual elements:
   - Setting/location
   - Subjects/characters
   - Specific actions
   - Visual details
4. Dialogue should be minimal and natural (1-2 short sentences max per scene)
5. Focus on VISUAL STORYTELLING over narration

Create exactly {num_scenes} scenes:

For each scene provide:
- Scene Type: establishing/action/emotion/transition/climax/resolution
- Visual Description: What we see (be specific: colors, objects, environment)
- Action: What happens (movement, gestures, changes)
- Dialogue: What is said (if anything, keep brief)
- Camera Direction: How to film it (close-up, wide shot, pan, etc.)
- Emotion: The feeling conveyed

Return as JSON:
{{
    "scenes": [
        {{
            "scene_number": 1,
            "duration": X,
            "scene_type": "establishing",
            "visual_description": "Detailed visual description",
            "action": "What happens",
            "dialogue": "Brief spoken text",
            "camera_direction": "Camera movement/angle",
            "emotion": "Emotional tone"
        }}
    ]
}}
"""
        
        try:
            response = model.generate_content(prompt)
            scenes_data = self._parse_scenes_response(response.text)
            
            # Convert to VisualScene objects
            scenes = []
            for scene_data in scenes_data.get('scenes', []):
                scene = VisualScene(
                    scene_number=scene_data.get('scene_number', len(scenes) + 1),
                    duration=scene_data.get('duration', duration / num_scenes),
                    scene_type=SceneType(scene_data.get('scene_type', 'action')),
                    visual_description=scene_data.get('visual_description', ''),
                    action=scene_data.get('action', ''),
                    dialogue=scene_data.get('dialogue', ''),
                    camera_direction=scene_data.get('camera_direction', 'medium shot'),
                    emotion=scene_data.get('emotion', tone)
                )
                scenes.append(scene)
            
            return scenes
            
        except Exception as e:
            logger.error(f"❌ Scene generation failed: {e}")
            return self._get_fallback_scenes(mission, num_scenes, duration)
    
    def _parse_scenes_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response to extract scenes"""
        try:
            # Clean response
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse JSON, using regex extraction")
            # Fallback: extract key information
            scenes = []
            scene_blocks = re.findall(r'"scene_number":\s*(\d+).*?"emotion":\s*"([^"]+)"', 
                                     response_text, re.DOTALL)
            for i, block in enumerate(scene_blocks):
                scenes.append({
                    'scene_number': i + 1,
                    'duration': 8,
                    'scene_type': 'action',
                    'visual_description': 'Scene description',
                    'action': 'Action happening',
                    'dialogue': '',
                    'camera_direction': 'medium shot',
                    'emotion': 'neutral'
                })
            return {'scenes': scenes}
    
    def _assemble_script(self, 
                        scenes: List[VisualScene],
                        mission: str,
                        platform: Platform) -> Dict[str, Any]:
        """Assemble scenes into complete script"""
        
        # Create narrative text from scenes
        narrative_segments = []
        for scene in scenes:
            segment_text = scene.dialogue if scene.dialogue else f"[{scene.action}]"
            narrative_segments.append(segment_text)
        
        script = {
            'mission': mission,
            'platform': platform.value,
            'scenes': [scene.to_dict() for scene in scenes],
            'narrative': ' '.join(narrative_segments),
            'total_duration': sum(scene.duration for scene in scenes),
            'scene_count': len(scenes),
            'visual_flow': self._analyze_visual_flow(scenes),
            'storyboard_ready': True
        }
        
        return script
    
    def _analyze_visual_flow(self, scenes: List[VisualScene]) -> Dict[str, Any]:
        """Analyze the visual flow and pacing"""
        flow_analysis = {
            'opening_type': scenes[0].scene_type.value if scenes else None,
            'closing_type': scenes[-1].scene_type.value if scenes else None,
            'scene_types': [s.scene_type.value for s in scenes],
            'emotional_arc': [s.emotion for s in scenes],
            'has_climax': any(s.scene_type == SceneType.CLIMAX for s in scenes),
            'has_resolution': any(s.scene_type == SceneType.RESOLUTION for s in scenes),
            'average_scene_duration': sum(s.duration for s in scenes) / len(scenes) if scenes else 0
        }
        return flow_analysis
    
    def _validate_visual_coherence(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the script has visual coherence"""
        issues = []
        
        # Check for abstract descriptions
        for scene in script['scenes']:
            if any(word in scene['visual_description'].lower() 
                   for word in ['concept', 'idea', 'feeling', 'thought']):
                issues.append(f"Scene {scene['scene_number']}: Too abstract")
        
        # Check for visual variety
        camera_directions = [s['camera_direction'] for s in script['scenes']]
        if len(set(camera_directions)) < len(camera_directions) * 0.5:
            issues.append("Lacks camera variety")
        
        # Check dialogue balance
        total_dialogue = sum(len(s['dialogue']) for s in script['scenes'])
        if total_dialogue > 200:  # Too much talking
            issues.append("Too dialogue-heavy for visual medium")
        
        script['validation'] = {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'visual_score': max(0, 100 - len(issues) * 20)
        }
        
        return script
    
    def _get_fallback_scenes(self, mission: str, num_scenes: int, duration: int) -> List[VisualScene]:
        """Create fallback scenes if generation fails"""
        scenes = []
        scene_duration = duration / num_scenes
        
        # Basic three-act structure
        scene_types = [SceneType.ESTABLISHING, SceneType.ACTION, SceneType.RESOLUTION]
        if num_scenes > 3:
            scene_types = [SceneType.ESTABLISHING] + \
                         [SceneType.ACTION] * (num_scenes - 2) + \
                         [SceneType.RESOLUTION]
        
        for i in range(num_scenes):
            scene = VisualScene(
                scene_number=i + 1,
                duration=scene_duration,
                scene_type=scene_types[min(i, len(scene_types) - 1)],
                visual_description=f"Visual scene {i+1} showing the story",
                action=f"Action unfolds in scene {i+1}",
                dialogue="",
                camera_direction="medium shot" if i % 2 == 0 else "close-up",
                emotion="neutral"
            )
            scenes.append(scene)
        
        return scenes


def create_visual_script(mission: str, duration: int, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to create a visual script
    
    Args:
        mission: The story to tell
        duration: Duration in seconds
        **kwargs: Additional parameters
        
    Returns:
        Visual script dictionary
    """
    generator = VisualStorytellingGenerator()
    return generator.generate_visual_script(mission, duration, **kwargs)