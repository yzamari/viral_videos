"""
Quick Mission Enhancement - Immediate improvements for better message delivery
Can be integrated into existing workflow without major refactoring
"""
import json
from typing import Dict, Any, List

class QuickMissionEnhancer:
    """Simple enhancements that can be added to existing pipeline"""
    
    @staticmethod
    def enhance_mission_prompt(mission: str, duration: int) -> str:
        """
        Enhance any AI prompt to focus on mission accomplishment
        Add this to existing prompts in script generation
        """
        return f"""
MISSION-CRITICAL FOCUS:
You are creating content to ACCOMPLISH: {mission}

Every element must:
1. Advance toward the desired outcome
2. Remove any content that doesn't serve the mission
3. Use persuasion techniques (logic, emotion, credibility)
4. Address likely objections
5. End with clear action steps

Duration: {duration} seconds - make every second count!
"""
    
    @staticmethod
    def validate_script_focus(script_segments: List[Dict[str, Any]], mission: str) -> Dict[str, Any]:
        """
        Quick validation of script focus - can be added after script generation
        """
        mission_words = set(mission.lower().split())
        focused_segments = []
        unfocused_segments = []
        
        for segment in script_segments:
            segment_text = segment.get('dialogue', '').lower()
            segment_words = set(segment_text.split())
            
            # Check if segment relates to mission
            if mission_words & segment_words:
                focused_segments.append(segment['segment_id'])
            else:
                unfocused_segments.append(segment['segment_id'])
        
        focus_score = len(focused_segments) / max(1, len(script_segments)) * 100
        
        return {
            "focus_score": focus_score,
            "focused_segments": focused_segments,
            "unfocused_segments": unfocused_segments,
            "recommendation": "Rewrite unfocused segments" if focus_score < 80 else "Good focus"
        }
    
    @staticmethod
    def add_mission_reinforcement(script_data: Dict[str, Any], mission: str) -> Dict[str, Any]:
        """
        Add reinforcement elements to existing script
        """
        # Extract key message
        key_words = mission.split()[:5]  # First 5 words as key message
        key_message = " ".join(key_words)
        
        # Add reinforcement metadata
        if 'reinforcements' not in script_data:
            script_data['reinforcements'] = {}
        
        script_data['reinforcements'] = {
            "visual_cues": [
                {"timing": "0-3s", "element": f"Bold text: '{key_message}'"},
                {"timing": "middle", "element": "Icon representing the mission"},
                {"timing": "end", "element": "CTA button with mission action"}
            ],
            "audio_emphasis": [
                {"timing": "hook", "technique": "Slower pace for key message"},
                {"timing": "climax", "technique": "Pause before main point"},
                {"timing": "cta", "technique": "Confident, clear delivery"}
            ],
            "repetition_pattern": {
                "key_phrase": key_message,
                "appearances": ["start", "middle", "end"],
                "variations": [
                    key_message,
                    f"Remember: {key_message}",
                    f"Take action on {key_message}"
                ]
            }
        }
        
        return script_data
    
    @staticmethod
    def create_mission_checklist(mission: str) -> List[str]:
        """
        Create a checklist for content creators to ensure mission focus
        """
        return [
            f"✓ Hook directly relates to: {mission}",
            f"✓ Every segment advances the mission goal",
            f"✓ Visual elements reinforce the message",
            f"✓ No tangential content or distractions",
            f"✓ Clear evidence/examples supporting the mission",
            f"✓ Addresses likely objections or doubts",
            f"✓ Emotional journey supports mission impact",
            f"✓ Strong, specific call-to-action",
            f"✓ Memorable key phrase repeated 3x",
            f"✓ Platform-optimized for maximum reach"
        ]

# Example usage in existing code:
# 
# 1. In script generation prompts:
# base_prompt = "Generate a script..."
# enhanced_prompt = base_prompt + QuickMissionEnhancer.enhance_mission_prompt(mission, duration)
#
# 2. After script generation:
# validation = QuickMissionEnhancer.validate_script_focus(script_segments, mission)
# if validation['focus_score'] < 80:
#     logger.warning(f"Low focus score: {validation['focus_score']}%")
#
# 3. Before final output:
# script_data = QuickMissionEnhancer.add_mission_reinforcement(script_data, mission)