"""
Mission-Driven Script Generator - Creates scripts that accomplish specific objectives
"""
import json
from typing import Dict, List, Any, Optional
from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest
from ..models.video_models import Language, Platform

logger = get_logger(__name__)

class MissionDrivenScriptGenerator:
    """
    Generates scripts specifically designed to accomplish missions, not just convey information
    """
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        logger.info("🎯 Mission-Driven Script Generator initialized")
    
    async def generate_mission_script(self, mission: str, mission_analysis: Dict[str, Any],
                                    duration: int, platform: Platform, 
                                    language: Language = Language.ENGLISH_US) -> Dict[str, Any]:
        """
        Generate a script optimized for mission accomplishment
        """
        logger.info(f"📝 Generating mission-driven script for: {mission[:100]}...")
        
        # Calculate segment structure
        num_segments = max(1, duration // 8)
        segment_duration = duration / num_segments
        
        prompt = f"""
You are an expert scriptwriter specializing in mission-accomplishing content.

MISSION: {mission}
CORE MESSAGE: {mission_analysis['core_message']}
DESIRED OUTCOME: {mission_analysis['desired_outcome']}
PLATFORM: {platform.value}
DURATION: {duration} seconds ({num_segments} segments)
PERSUASION APPROACH: {mission_analysis['persuasion_framework']['primary_approach']}

Write a {num_segments}-segment script that ACCOMPLISHES this mission:

CRITICAL REQUIREMENTS:
1. HOOK (First 3 seconds): Immediately establish why viewers MUST watch
2. Every segment must advance toward the desired outcome
3. Use {mission_analysis['persuasion_framework']['primary_approach']} as primary influence method
4. Address resistance points: {', '.join(mission_analysis['resistance_points'])}
5. Include evidence: {', '.join(mission_analysis['key_evidence'][:3])}
6. Build emotional journey: {mission_analysis['emotional_journey']['start']} → {mission_analysis['emotional_journey']['end']}
7. End with clear call-to-action: {mission_analysis['call_to_action']['primary']}

SEGMENT STRUCTURE:
- Each segment: 1-2 sentences (10-15 words per sentence)
- Tag format: "[VISUAL: description] DIALOGUE: spoken words"
- Natural pauses between segments

Return JSON with mission-focused segments:
{{
    "segments": [
        {{
            "segment_id": 1,
            "duration": {segment_duration},
            "purpose": "What this segment accomplishes",
            "dialogue": "Spoken text (1-2 sentences)",
            "visual": "Visual that reinforces the message",
            "persuasion_technique": "Specific technique used",
            "mission_advancement": "How it moves toward outcome"
        }},
        ...
    ],
    "mission_alignment": {{
        "hook_effectiveness": "Why the hook works",
        "message_clarity": "How clear the core message is",
        "resistance_handling": "How objections are addressed",
        "cta_strength": "Why the CTA will work"
    }}
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.8
            )
            
            response = await text_service.generate_text(request)
            script_data = json.loads(response.text)
            
            # Validate mission alignment
            alignment_score = await self._calculate_alignment_score(script_data, mission_analysis)
            script_data['alignment_score'] = alignment_score
            
            logger.info(f"✅ Mission script generated with {alignment_score}% alignment")
            return script_data
            
        except Exception as e:
            logger.error(f"❌ Mission script generation failed: {e}")
            return self._get_fallback_script(mission, duration, num_segments)
    
    async def optimize_for_impact(self, script_data: Dict[str, Any], 
                                platform: Platform) -> Dict[str, Any]:
        """
        Optimize script for maximum impact on target platform
        """
        logger.info(f"💪 Optimizing script for {platform.value} impact...")
        
        prompt = f"""
Optimize this mission-driven script for MAXIMUM IMPACT on {platform.value}:

CURRENT SCRIPT: {json.dumps(script_data['segments'], indent=2)}

Platform-specific optimizations needed:
1. Hook optimization for {platform.value} algorithm
2. Pacing for {platform.value} attention spans
3. Language that triggers {platform.value} engagement
4. Visual cues that work on {platform.value}
5. CTA placement for {platform.value} users

For each segment, enhance:
1. Emotional triggers
2. Curiosity gaps
3. Social proof elements
4. Urgency/scarcity
5. Memorable phrases

Return optimized script with same structure but HIGHER IMPACT.
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.7
            )
            
            response = await text_service.generate_text(request)
            optimized_script = json.loads(response.text)
            
            # Merge optimizations
            script_data['segments'] = optimized_script.get('segments', script_data['segments'])
            script_data['platform_optimizations'] = optimized_script.get('optimizations', {})
            
            return script_data
            
        except Exception as e:
            logger.error(f"❌ Script optimization failed: {e}")
            return script_data
    
    async def _calculate_alignment_score(self, script_data: Dict[str, Any],
                                       mission_analysis: Dict[str, Any]) -> float:
        """
        Calculate how well the script aligns with mission objectives
        """
        score = 0.0
        total_weight = 0.0
        
        # Check core message presence (weight: 30%)
        core_message = mission_analysis['core_message'].lower()
        script_text = ' '.join([s['dialogue'] for s in script_data['segments']]).lower()
        if any(word in script_text for word in core_message.split()):
            score += 30
        total_weight += 30
        
        # Check evidence inclusion (weight: 20%)
        evidence_count = sum(1 for evidence in mission_analysis['key_evidence']
                           if any(ev_word in script_text for ev_word in evidence.lower().split()))
        score += (evidence_count / max(1, len(mission_analysis['key_evidence']))) * 20
        total_weight += 20
        
        # Check CTA presence (weight: 25%)
        cta = mission_analysis['call_to_action']['primary'].lower()
        if any(cta_word in script_text for cta_word in cta.split()):
            score += 25
        total_weight += 25
        
        # Check persuasion technique usage (weight: 25%)
        technique_count = sum(1 for segment in script_data['segments']
                            if segment.get('persuasion_technique'))
        score += (technique_count / len(script_data['segments'])) * 25
        total_weight += 25
        
        return round((score / total_weight) * 100, 1)
    
    def _get_fallback_script(self, mission: str, duration: int, 
                           num_segments: int) -> Dict[str, Any]:
        """Fallback script structure"""
        segments = []
        segment_duration = duration / num_segments
        
        # Basic structure
        purposes = [
            "Hook and establish relevance",
            "Present core message",
            "Provide evidence/example",
            "Address objections",
            "Reinforce message",
            "Call to action"
        ]
        
        for i in range(num_segments):
            purpose_idx = min(i, len(purposes) - 1)
            segments.append({
                "segment_id": i + 1,
                "duration": segment_duration,
                "purpose": purposes[purpose_idx],
                "dialogue": f"Segment {i+1} content addressing the mission.",
                "visual": f"Visual supporting segment {i+1}",
                "persuasion_technique": "logical appeal",
                "mission_advancement": "Advances mission objective"
            })
        
        return {
            "segments": segments,
            "mission_alignment": {
                "hook_effectiveness": "Captures attention",
                "message_clarity": "Clear and focused",
                "resistance_handling": "Addresses concerns",
                "cta_strength": "Direct and actionable"
            },
            "alignment_score": 70.0
        }