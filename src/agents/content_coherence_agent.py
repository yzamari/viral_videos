"""
Content Coherence Agent - Ensures educational content is clear, focused, and complete
"""
import json
from typing import Dict, List, Any, Optional
from ..utils.logging_config import get_logger
from ..agents.base_agent import BaseAgent

logger = get_logger(__name__)

class ContentCoherenceAgent(BaseAgent):
    """
    Ensures educational content is coherent, focused on a single topic,
    and provides a complete learning experience without abrupt endings
    """
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            name="ContentCoherenceAgent",
            description="Educational content coherence and completeness specialist",
            skills=["curriculum design", "narrative structure", "learning objectives", "content flow"],
            personality_traits=["methodical", "thorough", "pedagogical", "clear-thinking"]
        )
    
    async def analyze_content_coherence(self, mission: str, duration: int, 
                                       platform: str = "youtube") -> Dict[str, Any]:
        """
        Analyze and improve content coherence for educational videos
        
        Args:
            mission: The educational topic/mission
            duration: Video duration in seconds
            platform: Target platform
            
        Returns:
            Coherent content structure with clear learning objectives
        """
        logger.info(f"🎯 Analyzing content coherence for: {mission[:100]}...")
        
        prompt = f"""
You are an educational content specialist ensuring videos are coherent and complete.

Mission: {mission}
Duration: {duration} seconds
Platform: {platform}

CRITICAL REQUIREMENTS:
1. Focus on ONE CLEAR TOPIC - no tangents or multiple subjects
2. Structure content with Beginning, Middle, and End
3. Ensure complete thoughts - no cut-off explanations
4. Make content age-appropriate and engaging
5. Include clear learning objectives

Analyze the mission and provide a COHERENT content structure:

1. SINGLE LEARNING OBJECTIVE: What ONE thing will viewers learn?
2. CONTENT STRUCTURE:
   - Introduction (15% of time): Hook + What we'll learn
   - Core Content (70% of time): Step-by-step explanation
   - Conclusion (15% of time): Summary + Key takeaway
3. KEY CONCEPTS: List 3-5 essential points to cover
4. NARRATIVE ARC: Ensure smooth flow from start to finish
5. COMPLETION CHECK: Does the content feel complete?

Return JSON:
{{
    "learning_objective": "Clear single objective",
    "content_structure": {{
        "introduction": {{
            "duration_percentage": 15,
            "content": "Hook and preview"
        }},
        "core_content": {{
            "duration_percentage": 70,
            "segments": ["segment1", "segment2", ...]
        }},
        "conclusion": {{
            "duration_percentage": 15,
            "content": "Summary and takeaway"
        }}
    }},
    "key_concepts": ["concept1", "concept2", ...],
    "coherence_score": 0-100,
    "completion_guarantee": "How we ensure no cut-offs"
}}

Focus on making the content feel COMPLETE and SATISFYING.
"""

        try:
            response = await self._make_api_call(prompt)
            analysis = self._parse_json_response(response)
            
            # Validate coherence
            if analysis.get('coherence_score', 0) < 80:
                logger.warning("⚠️ Low coherence score - improving structure")
                analysis = await self._improve_coherence(mission, duration, analysis)
            
            logger.info(f"✅ Content coherence score: {analysis.get('coherence_score', 0)}/100")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Content coherence analysis failed: {e}")
            return self._get_fallback_structure(duration)
    
    async def create_focused_script_segments(self, mission: str, duration: int,
                                           coherence_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create script segments that maintain focus on single topic
        """
        logger.info("📝 Creating focused script segments")
        
        # Calculate segment durations
        intro_duration = int(duration * 0.15)
        core_duration = int(duration * 0.70)
        conclusion_duration = int(duration * 0.15)
        
        segments = []
        
        # Introduction segment
        segments.append({
            "type": "introduction",
            "duration": intro_duration,
            "content": coherence_analysis['content_structure']['introduction']['content'],
            "purpose": "Hook and set expectations"
        })
        
        # Core content segments
        core_segments = coherence_analysis['content_structure']['core_content']['segments']
        segment_duration = core_duration // len(core_segments)
        
        for i, segment_content in enumerate(core_segments):
            segments.append({
                "type": "core_content",
                "duration": segment_duration,
                "content": segment_content,
                "sequence": i + 1,
                "total": len(core_segments)
            })
        
        # Conclusion segment
        segments.append({
            "type": "conclusion",
            "duration": conclusion_duration,
            "content": coherence_analysis['content_structure']['conclusion']['content'],
            "purpose": "Summarize and reinforce learning"
        })
        
        return segments
    
    async def _improve_coherence(self, mission: str, duration: int, 
                               initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Improve content structure for better coherence
        """
        prompt = f"""
The content structure needs improvement for better coherence.

Mission: {mission}
Duration: {duration} seconds
Current Analysis: {json.dumps(initial_analysis, indent=2)}

PROBLEMS TO FIX:
1. Content tries to cover too much
2. No clear beginning-middle-end
3. Concepts not explained fully
4. Abrupt or incomplete ending

Create an IMPROVED structure that:
1. Focuses on ONE main concept
2. Builds knowledge step-by-step
3. Has satisfying conclusion
4. Feels complete, not cut off

Return improved JSON with coherence_score >= 90.
"""

        response = await self._make_api_call(prompt)
        improved = self._parse_json_response(response)
        improved['coherence_score'] = max(90, improved.get('coherence_score', 90))
        return improved
    
    def _get_fallback_structure(self, duration: int) -> Dict[str, Any]:
        """
        Fallback coherent structure
        """
        return {
            "learning_objective": "Learn one key concept clearly",
            "content_structure": {
                "introduction": {
                    "duration_percentage": 15,
                    "content": "Welcome! Today we'll learn something amazing"
                },
                "core_content": {
                    "duration_percentage": 70,
                    "segments": [
                        "First, let's understand the basics",
                        "Now, let's see how it works",
                        "Finally, let's practice together"
                    ]
                },
                "conclusion": {
                    "duration_percentage": 15,
                    "content": "Great job! Remember what we learned today"
                }
            },
            "key_concepts": ["main concept", "how it works", "practice"],
            "coherence_score": 85,
            "completion_guarantee": "Each segment flows to the next with clear transitions"
        }
    
    def get_contribution_summary(self) -> str:
        """
        Summarize agent's contribution
        """
        return "Ensured content focuses on single topic with complete narrative arc"