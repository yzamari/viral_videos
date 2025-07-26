"""
Mission Analyzer - Comprehensive mission analysis using Gemini Pro
Replaces the complex parsing system with intelligent analysis
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re

from ..utils.logging_config import get_logger
from ..models.video_models import Platform, VideoCategory

logger = get_logger(__name__)


@dataclass
class AnalyzedMission:
    """Complete mission analysis with all components"""
    # Core content
    script_content: str  # Only spoken dialogue
    visual_sequence: List[Dict[str, Any]]  # Scene-by-scene visuals
    
    # Production details
    character_details: Dict[str, Any]  # Character appearances, emotions
    scene_descriptions: List[str]  # Detailed scene info
    technical_requirements: Dict[str, Any]  # Effects, transitions, overlays
    timing_breakdown: List[Dict[str, Any]]  # How to fit in duration
    
    # Metadata
    content_type: str  # news, comedy, educational, etc.
    emotional_arc: str  # How emotion progresses
    key_moments: List[str]  # Critical moments to emphasize
    platform_optimizations: Dict[str, Any]  # Platform-specific tips
    
    # Quality metrics
    confidence_score: float
    complexity_level: str  # simple, moderate, complex
    production_notes: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class MissionAnalyzer:
    """
    Analyzes video generation missions using Gemini Pro
    Considers ALL context: mission, flags, platform, style, etc.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro"):
        """Initialize Mission Analyzer with Gemini Pro"""
        self.api_key = api_key
        self.model_name = model_name
        
        # Initialize Gemini
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(model_name)
            logger.info(f"✅ Mission Analyzer initialized with {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.gemini_model = None
    
    async def analyze_mission(self, 
                            config: Any,
                            use_multishot: bool = True) -> AnalyzedMission:
        """
        Analyze mission with full context
        
        Args:
            config: VideoGenerationConfig with all parameters
            use_multishot: Whether to use multi-shot examples
            
        Returns:
            AnalyzedMission with complete breakdown
        """
        try:
            logger.info(f"🎯 Analyzing mission: {config.mission[:100]}...")
            
            # Build comprehensive prompt
            prompt = self._build_analysis_prompt(config, use_multishot)
            
            # Get analysis from Gemini
            response_text = await self._get_gemini_analysis(prompt)
            
            if response_text:
                # Parse the response
                analyzed = self._parse_analysis(response_text, config)
                if analyzed:
                    logger.info(f"✅ Mission analysis complete:")
                    logger.info(f"   Script length: {len(analyzed.script_content)} chars")
                    logger.info(f"   Visual scenes: {len(analyzed.visual_sequence)}")
                    logger.info(f"   Complexity: {analyzed.complexity_level}")
                    logger.info(f"   Confidence: {analyzed.confidence_score:.2f}")
                    return analyzed
            
            # Fallback to simple analysis
            logger.warning("⚠️ Advanced analysis failed, using simple analysis")
            return self._simple_analysis(config)
            
        except Exception as e:
            logger.error(f"❌ Mission analysis failed: {e}")
            return self._simple_analysis(config)
    
    def _build_analysis_prompt(self, config: Any, use_multishot: bool) -> str:
        """Build comprehensive analysis prompt with all context"""
        
        # Multi-shot examples for better results
        examples = ""
        if use_multishot:
            examples = self._get_multishot_examples()
        
        prompt = f"""You are an expert video production analyzer. Analyze this video request comprehensively.

{examples}

CURRENT REQUEST TO ANALYZE:

MISSION: {config.mission}
PLATFORM: {config.target_platform.value if hasattr(config.target_platform, 'value') else config.target_platform}
DURATION: {config.duration_seconds} seconds
VISUAL STYLE: {getattr(config, 'visual_style', 'dynamic')}
TONE: {getattr(config, 'tone', 'engaging')}
AUDIENCE: {getattr(config, 'target_audience', 'general')}
CHARACTER: {getattr(config, 'character', 'No specific character')}
SCENE: {getattr(config, 'scene', 'No specific scene')}
THEME: {getattr(config, 'theme', 'No specific theme')}
STYLE TEMPLATE: {getattr(config, 'style_template', 'default')}
VOICE: {getattr(config, 'voice', 'default')}
MODE: {getattr(config, 'mode', 'enhanced')}
LANGUAGE: {getattr(config, 'language', 'en-US')}

CRITICAL REQUIREMENTS:
1. SCRIPT must contain ONLY spoken dialogue/narration (no visual descriptions, no stage directions)
2. Remove character names from dialogue (e.g., "John: Hello" becomes just "Hello")
3. Visual descriptions go in VISUAL_SEQUENCE only
4. Consider platform requirements (TikTok = fast-paced, YouTube = can be longer)
5. Ensure everything fits within {config.duration_seconds} seconds

Provide a JSON response with this EXACT structure:
{{
    "script_content": "Complete spoken dialogue only, no visual descriptions",
    "visual_sequence": [
        {{
            "scene_number": 1,
            "duration_seconds": 5,
            "description": "What happens visually",
            "camera_angle": "close-up/wide/etc",
            "characters_present": ["list of characters"],
            "key_elements": ["important visual elements"],
            "transitions": "how it transitions to next scene"
        }}
    ],
    "character_details": {{
        "character_name": {{
            "appearance": "physical description",
            "emotions": ["emotional states throughout"],
            "costume_changes": ["if any"],
            "key_actions": ["main actions performed"]
        }}
    }},
    "scene_descriptions": [
        "Detailed description of each location/setting"
    ],
    "technical_requirements": {{
        "effects": ["special effects needed"],
        "transitions": ["transition types"],
        "overlays": ["text overlays, graphics"],
        "audio_cues": ["sound effects, music cues"],
        "color_grading": "overall visual tone"
    }},
    "timing_breakdown": [
        {{
            "segment": "Introduction",
            "start_time": 0,
            "end_time": 5,
            "script_portion": "What is said",
            "visual_portion": "What is shown"
        }}
    ],
    "content_type": "news/comedy/educational/promotional/etc",
    "emotional_arc": "how emotions progress through video",
    "key_moments": ["memorable moments to emphasize"],
    "platform_optimizations": {{
        "hook_strategy": "how to grab attention in first 3 seconds",
        "engagement_tactics": ["ways to maintain interest"],
        "cta_placement": "where to place call-to-action"
    }},
    "confidence_score": 0.95,
    "complexity_level": "simple/moderate/complex",
    "production_notes": "any special considerations for production"
}}

IMPORTANT: Return ONLY the JSON, no markdown formatting, no explanation."""
        
        return prompt
    
    def _get_multishot_examples(self) -> str:
        """Get multi-shot examples for better analysis"""
        return """
EXAMPLE 1 - News Parody:
Mission: "Family Guy style news. Anchor says: 'Breaking news!' Show explosion. Reporter: 'Chaos everywhere!' Cut to chicken fight."
Analysis:
{
    "script_content": "Breaking news! Chaos everywhere!",
    "visual_sequence": [
        {
            "scene_number": 1,
            "duration_seconds": 3,
            "description": "News anchor at desk delivers breaking news",
            "camera_angle": "medium shot",
            "characters_present": ["News Anchor"],
            "key_elements": ["news desk", "breaking news graphic"],
            "transitions": "quick cut"
        },
        {
            "scene_number": 2,
            "duration_seconds": 2,
            "description": "Explosion effect fills screen",
            "camera_angle": "wide shot",
            "characters_present": [],
            "key_elements": ["explosion", "debris"],
            "transitions": "explosive transition"
        }
    ]
}

EXAMPLE 2 - Educational Content:
Mission: "Teacher explains: 'Photosynthesis converts light to energy.' Show animated plant growing. Students ask: 'How does it work?' Display diagram."
Analysis:
{
    "script_content": "Photosynthesis converts light to energy. How does it work?",
    "visual_sequence": [
        {
            "scene_number": 1,
            "duration_seconds": 4,
            "description": "Teacher at whiteboard explaining concept",
            "camera_angle": "medium shot",
            "characters_present": ["Teacher"],
            "key_elements": ["whiteboard", "simple drawings"],
            "transitions": "smooth fade"
        }
    ]
}
"""
    
    async def _get_gemini_analysis(self, prompt: str) -> Optional[str]:
        """Get analysis from Gemini Pro"""
        if not self.gemini_model:
            return None
            
        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.3,  # Low for consistency
                    "max_output_tokens": 4000,
                    "top_p": 0.9,
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"❌ Gemini analysis failed: {e}")
            return None
    
    def _parse_analysis(self, response_text: str, config: Any) -> Optional[AnalyzedMission]:
        """Parse Gemini response into AnalyzedMission"""
        try:
            # Clean response
            text = response_text.strip()
            
            # Remove any markdown formatting
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            
            # Parse JSON
            data = json.loads(text)
            
            # Create AnalyzedMission object
            return AnalyzedMission(
                script_content=data.get('script_content', ''),
                visual_sequence=data.get('visual_sequence', []),
                character_details=data.get('character_details', {}),
                scene_descriptions=data.get('scene_descriptions', []),
                technical_requirements=data.get('technical_requirements', {}),
                timing_breakdown=data.get('timing_breakdown', []),
                content_type=data.get('content_type', 'general'),
                emotional_arc=data.get('emotional_arc', 'steady'),
                key_moments=data.get('key_moments', []),
                platform_optimizations=data.get('platform_optimizations', {}),
                confidence_score=float(data.get('confidence_score', 0.8)),
                complexity_level=data.get('complexity_level', 'moderate'),
                production_notes=data.get('production_notes', '')
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to parse analysis: {e}")
            logger.debug(f"Response was: {response_text[:500]}...")
            return None
    
    def _simple_analysis(self, config: Any) -> AnalyzedMission:
        """Simple fallback analysis without AI"""
        logger.info("📝 Using simple analysis fallback")
        
        # Extract dialogue using basic patterns
        mission = config.mission
        script_parts = []
        
        # Find quoted text (likely dialogue)
        quotes = re.findall(r'["\']([^"\']+)["\']', mission)
        script_parts.extend(quotes)
        
        # Remove character names
        cleaned_parts = []
        for part in script_parts:
            cleaned = re.sub(r'^[A-Z][a-zA-Z\s]*:\s*', '', part)
            if cleaned:
                cleaned_parts.append(cleaned)
        
        script = '. '.join(cleaned_parts) if cleaned_parts else mission[:200]
        
        # Simple visual sequence
        duration = config.duration_seconds
        num_scenes = max(3, min(8, duration // 5))
        scene_duration = duration / num_scenes
        
        visual_sequence = []
        for i in range(num_scenes):
            visual_sequence.append({
                "scene_number": i + 1,
                "duration_seconds": scene_duration,
                "description": f"Scene {i + 1} of the video",
                "camera_angle": "medium shot",
                "characters_present": [],
                "key_elements": [],
                "transitions": "cut"
            })
        
        return AnalyzedMission(
            script_content=script,
            visual_sequence=visual_sequence,
            character_details={},
            scene_descriptions=["Fallback scene description"],
            technical_requirements={
                "effects": [],
                "transitions": ["simple cuts"],
                "overlays": [],
                "audio_cues": [],
                "color_grading": "standard"
            },
            timing_breakdown=[{
                "segment": "Full video",
                "start_time": 0,
                "end_time": duration,
                "script_portion": script,
                "visual_portion": "Visual content"
            }],
            content_type="general",
            emotional_arc="steady",
            key_moments=[],
            platform_optimizations={},
            confidence_score=0.5,
            complexity_level="simple",
            production_notes="Simple fallback analysis used"
        )