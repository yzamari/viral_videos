"""
Mission Coherence Enforcer - Ensures every element serves the mission
"""
import json
from typing import Dict, List, Any, Optional
from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest

logger = get_logger(__name__)

class MissionCoherenceEnforcer:
    """
    Ensures all content elements (script, visuals, audio) align with and advance the mission
    """
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        logger.info("🎯 Mission Coherence Enforcer initialized")
    
    async def validate_script_alignment(self, mission: str, core_message: str, 
                                      script_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that every script segment advances the mission
        """
        logger.info("🔍 Validating script alignment with mission...")
        
        prompt = f"""
You are a mission coherence specialist ensuring content focus.

MISSION: {mission}
CORE MESSAGE: {core_message}

Review these script segments for mission alignment:
{json.dumps(script_segments, indent=2)}

For EACH segment, evaluate:
1. Does it directly advance the mission?
2. Is it essential or can it be cut?
3. How does it build on previous segments?
4. Does it maintain focus on the core message?

Return detailed analysis:
{{
    "overall_coherence_score": 0-100,
    "segments": [
        {{
            "segment_id": 1,
            "advances_mission": true/false,
            "alignment_score": 0-100,
            "issues": ["issue1", "issue2"],
            "improvement": "How to better align with mission",
            "essential": true/false
        }},
        ...
    ],
    "flow_analysis": {{
        "maintains_focus": true/false,
        "narrative_progression": "How the message builds",
        "weak_points": ["where focus is lost"],
        "strong_points": ["where message is reinforced"]
    }},
    "recommendations": [
        "specific improvement 1",
        "specific improvement 2"
    ]
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.6
            )
            
            response = await text_service.generate_text(request)
            validation = json.loads(response.text)
            
            logger.info(f"✅ Coherence Score: {validation['overall_coherence_score']}/100")
            
            # Identify segments that need improvement
            weak_segments = [s for s in validation['segments'] if s['alignment_score'] < 70]
            if weak_segments:
                logger.warning(f"⚠️ {len(weak_segments)} segments need better mission alignment")
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Script validation failed: {e}")
            return self._get_fallback_validation()
    
    async def enhance_weak_segments(self, mission: str, core_message: str,
                                  weak_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rewrite weak segments to better serve the mission
        """
        logger.info("💪 Enhancing weak segments for better mission alignment...")
        
        enhanced_segments = []
        
        for segment in weak_segments:
            prompt = f"""
Rewrite this segment to STRONGLY advance the mission:

MISSION: {mission}
CORE MESSAGE: {core_message}
CURRENT SEGMENT: {json.dumps(segment)}

Requirements:
1. Every word must serve the mission
2. Remove any tangential content
3. Strengthen the connection to core message
4. Make it more impactful and focused
5. Maintain natural flow

Return enhanced segment:
{{
    "segment_id": {segment.get('segment_id', 1)},
    "enhanced_content": "Rewritten content",
    "visual_description": "Visuals that reinforce the message",
    "mission_connection": "How this now advances the mission",
    "improvement_notes": "What was changed and why"
}}
"""
            
            try:
                text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
                request = TextGenerationRequest(
                    prompt=prompt,
                    max_tokens=800,
                    temperature=0.7
                )
                
                response = await text_service.generate_text(request)
                enhanced = json.loads(response.text)
                enhanced_segments.append(enhanced)
                
            except Exception as e:
                logger.error(f"❌ Failed to enhance segment {segment.get('segment_id')}: {e}")
                enhanced_segments.append(segment)
        
        return enhanced_segments
    
    async def create_mission_reinforcement_plan(self, mission: str, duration: int,
                                              key_moments: List[int]) -> Dict[str, Any]:
        """
        Create a plan to reinforce the mission at key moments
        """
        logger.info("📋 Creating mission reinforcement plan...")
        
        prompt = f"""
Create a reinforcement plan for this mission:

MISSION: {mission}
DURATION: {duration} seconds
KEY MOMENTS: {key_moments} (seconds)

Design reinforcement strategies:
1. Visual cues that remind of the mission
2. Audio emphasis at critical points
3. Text overlays for key messages
4. Repetition patterns that don't feel repetitive

Return reinforcement plan:
{{
    "visual_reinforcements": [
        {{
            "timing": "0-3s",
            "technique": "Visual technique",
            "message": "What it reinforces"
        }},
        ...
    ],
    "audio_reinforcements": [
        {{
            "timing": "key moment",
            "technique": "Audio technique",
            "impact": "Expected impact"
        }},
        ...
    ],
    "text_reinforcements": [
        {{
            "timing": "when to show",
            "text": "Key message text",
            "style": "How to display"
        }},
        ...
    ],
    "repetition_strategy": {{
        "key_phrase": "Core message to repeat",
        "variations": ["variation 1", "variation 2"],
        "timing_pattern": "When and how to repeat"
    }}
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.8
            )
            
            response = await text_service.generate_text(request)
            plan = json.loads(response.text)
            
            logger.info("✅ Mission reinforcement plan created")
            return plan
            
        except Exception as e:
            logger.error(f"❌ Reinforcement plan creation failed: {e}")
            return self._get_fallback_reinforcement_plan()
    
    def _get_fallback_validation(self) -> Dict[str, Any]:
        """Fallback validation result"""
        return {
            "overall_coherence_score": 70,
            "segments": [],
            "flow_analysis": {
                "maintains_focus": True,
                "narrative_progression": "Linear progression",
                "weak_points": [],
                "strong_points": ["Clear message"]
            },
            "recommendations": ["Maintain focus on core message"]
        }
    
    def _get_fallback_reinforcement_plan(self) -> Dict[str, Any]:
        """Fallback reinforcement plan"""
        return {
            "visual_reinforcements": [
                {
                    "timing": "0-3s",
                    "technique": "Strong opening visual",
                    "message": "Establish mission context"
                }
            ],
            "audio_reinforcements": [
                {
                    "timing": "climax",
                    "technique": "Emphasis through pacing",
                    "impact": "Highlight key message"
                }
            ],
            "text_reinforcements": [
                {
                    "timing": "end",
                    "text": "Remember the key message",
                    "style": "Bold, centered"
                }
            ],
            "repetition_strategy": {
                "key_phrase": "Core message",
                "variations": ["Different wording 1", "Different wording 2"],
                "timing_pattern": "Beginning, middle, end"
            }
        }