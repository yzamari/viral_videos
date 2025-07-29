"""
Enhanced Mission Analyzer - Deep understanding of mission intent and impact
"""
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest

logger = get_logger(__name__)

class MissionImpact(Enum):
    """Impact levels for mission accomplishment"""
    BEHAVIORAL_CHANGE = "behavioral_change"
    MINDSET_SHIFT = "mindset_shift"
    KNOWLEDGE_TRANSFER = "knowledge_transfer"
    EMOTIONAL_RESONANCE = "emotional_resonance"
    ACTION_INSPIRATION = "action_inspiration"
    AWARENESS_BUILDING = "awareness_building"

class EnhancedMissionAnalyzer:
    """
    Analyzes missions to extract deep intent, target outcomes, and impact strategies
    """
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        logger.info("🎯 Enhanced Mission Analyzer initialized")
    
    async def analyze_mission_depth(self, mission: str, duration: int, 
                                   target_audience: str, platform: str) -> Dict[str, Any]:
        """
        Deeply analyze mission to understand true intent and desired impact
        """
        logger.info(f"🔍 Analyzing mission depth: {mission[:100]}...")
        
        prompt = f"""
You are a strategic content analyst specializing in mission-driven video creation.

MISSION: {mission}
DURATION: {duration} seconds
AUDIENCE: {target_audience}
PLATFORM: {platform}

Analyze this mission to extract:

1. CORE MESSAGE: What is the ONE fundamental message to convey?
2. DESIRED OUTCOME: What specific change/action do we want from viewers?
3. IMPACT TYPE: Primary impact (behavioral_change, mindset_shift, knowledge_transfer, emotional_resonance, action_inspiration, awareness_building)
4. PSYCHOLOGICAL DRIVERS: What motivates the audience to care?
5. RESISTANCE POINTS: What objections/barriers might prevent mission success?
6. PERSUASION FRAMEWORK: Best approach (logic, emotion, credibility, urgency)
7. SUCCESS METRICS: How do we measure if the mission was accomplished?
8. KEY EVIDENCE: What proof/examples will make the message believable?
9. EMOTIONAL JOURNEY: Beginning emotion → End emotion
10. CALL TO ACTION: Specific next step for viewers

Return comprehensive JSON analysis:
{{
    "core_message": "Single sentence capturing the essence",
    "desired_outcome": "Specific measurable outcome",
    "impact_type": "primary impact category",
    "psychological_drivers": ["driver1", "driver2", ...],
    "resistance_points": ["objection1", "objection2", ...],
    "persuasion_framework": {{
        "primary_approach": "logic/emotion/credibility/urgency",
        "supporting_approaches": ["approach1", "approach2"],
        "ratio": {{
            "logic": 30,
            "emotion": 40,
            "credibility": 20,
            "urgency": 10
        }}
    }},
    "success_metrics": ["metric1", "metric2", ...],
    "key_evidence": ["evidence1", "evidence2", ...],
    "emotional_journey": {{
        "start": "initial emotional state",
        "middle": "transformation point",
        "end": "desired emotional state"
    }},
    "call_to_action": {{
        "primary": "main action",
        "supporting": ["secondary action1", "secondary action2"]
    }},
    "content_strategy": {{
        "hook_approach": "how to grab attention in first 3 seconds",
        "narrative_arc": "story structure approach",
        "climax_moment": "peak impact moment",
        "resolution": "how to close with impact"
    }}
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            response = await text_service.generate_text(request)
            analysis = json.loads(response.text)
            
            logger.info(f"✅ Mission analysis complete:")
            logger.info(f"   Core Message: {analysis['core_message']}")
            logger.info(f"   Impact Type: {analysis['impact_type']}")
            logger.info(f"   Primary Approach: {analysis['persuasion_framework']['primary_approach']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Mission depth analysis failed: {e}")
            return self._get_fallback_analysis(mission)
    
    async def generate_impact_strategies(self, mission_analysis: Dict[str, Any], 
                                       platform: str) -> List[Dict[str, Any]]:
        """
        Generate specific strategies to maximize mission impact
        """
        logger.info("💡 Generating impact strategies...")
        
        prompt = f"""
Based on this mission analysis, create specific impact strategies:

CORE MESSAGE: {mission_analysis['core_message']}
IMPACT TYPE: {mission_analysis['impact_type']}
RESISTANCE POINTS: {', '.join(mission_analysis['resistance_points'])}
PLATFORM: {platform}

Generate 5 high-impact content strategies:

For each strategy provide:
1. Tactic name
2. Implementation approach
3. Why it works for this mission
4. Expected impact level (1-10)
5. Specific examples

Return JSON array:
[
    {{
        "tactic": "Tactic name",
        "approach": "How to implement",
        "rationale": "Why this works",
        "impact_score": 8,
        "examples": ["example1", "example2"]
    }},
    ...
]
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.8
            )
            
            response = await text_service.generate_text(request)
            strategies = json.loads(response.text)
            
            logger.info(f"✅ Generated {len(strategies)} impact strategies")
            return strategies
            
        except Exception as e:
            logger.error(f"❌ Strategy generation failed: {e}")
            return []
    
    def _get_fallback_analysis(self, mission: str) -> Dict[str, Any]:
        """Fallback analysis for error cases"""
        return {
            "core_message": mission[:100],
            "desired_outcome": "Viewer understanding and engagement",
            "impact_type": "awareness_building",
            "psychological_drivers": ["curiosity", "relevance"],
            "resistance_points": ["attention span", "skepticism"],
            "persuasion_framework": {
                "primary_approach": "emotion",
                "supporting_approaches": ["logic", "credibility"],
                "ratio": {"logic": 25, "emotion": 50, "credibility": 25, "urgency": 0}
            },
            "success_metrics": ["view completion", "engagement"],
            "key_evidence": ["examples", "testimonials"],
            "emotional_journey": {
                "start": "curious",
                "middle": "engaged",
                "end": "inspired"
            },
            "call_to_action": {
                "primary": "Learn more",
                "supporting": ["Share", "Comment"]
            },
            "content_strategy": {
                "hook_approach": "Question or surprising fact",
                "narrative_arc": "Problem-solution",
                "climax_moment": "Key revelation",
                "resolution": "Clear next steps"
            }
        }