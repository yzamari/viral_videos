"""
Detailed VEO3 JSON Prompt Generation Agent
Creates comprehensive, nested JSON prompts matching the most detailed professional examples
Supports both flat structure (Tesla/Pepsi) and nested structure (advanced examples)
"""

import json
import asyncio
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from .gemini_helper import GeminiModelHelper, ensure_api_key
    from ..utils.logging_config import get_logger
    from ..models.video_models import Platform
    from ..utils.session_context import SessionContext
    from ..utils.ai_timeout_wrapper import with_timeout, ai_wrapper
except ImportError:
    from src.agents.gemini_helper import GeminiModelHelper, ensure_api_key
    from src.utils.logging_config import get_logger
    from src.models.video_models import Platform
    from src.utils.session_context import SessionContext
    from src.utils.ai_timeout_wrapper import with_timeout, ai_wrapper

logger = get_logger(__name__)


class AgentSpecialty(Enum):
    """Specialized agent roles for detailed VEO3 JSON generation"""
    CINEMATOGRAPHER = "cinematographer"        # shot, camera_motion, frame_rate, film_grain
    VISUAL_DESIGNER = "visual_designer"       # style, visual_details, cinematography
    SCENE_ARCHITECT = "scene_architect"       # scene, location, environment
    CHARACTER_DIRECTOR = "character_director"  # subject, character details
    AUDIO_DIRECTOR = "audio_director"         # audio, dialogue, sounds
    MOTION_SPECIALIST = "motion_specialist"   # motion, physics, action
    TECHNICAL_DIRECTOR = "technical_director"  # keywords, technical specs
    ORCHESTRATOR = "orchestrator"             # Final decisions, structure


class DetailedVEO3JsonAgent:
    """Detailed VEO3 JSON prompt generation with nested professional structure"""
    
    def __init__(self, session_context: SessionContext, api_key: Optional[str] = None):
        """Initialize the detailed VEO3 JSON agent"""
        self.session_context = session_context
        self.api_key = ensure_api_key(api_key)
        
        # Agent expertise weights for nested structure
        self.agent_weights = {
            AgentSpecialty.CINEMATOGRAPHER: {
                'shot': 0.9, 'camera': 0.9, 'camera_motion': 0.9, 'frame_rate': 0.9, 'film_grain': 0.8
            },
            AgentSpecialty.VISUAL_DESIGNER: {
                'style': 0.9, 'visual_details': 0.9, 'cinematography': 0.9, 'lighting': 0.8
            },
            AgentSpecialty.SCENE_ARCHITECT: {
                'scene': 0.9, 'location': 0.9, 'environment': 0.9, 'setting': 0.8, 'room': 0.8
            },
            AgentSpecialty.CHARACTER_DIRECTOR: {
                'subject': 0.9, 'character_consistency': 0.9, 'wardrobe': 0.8, 'elements': 0.6
            },
            AgentSpecialty.AUDIO_DIRECTOR: {
                'audio': 0.9, 'dialogue': 0.9, 'primary_sounds': 0.9, 'music': 0.8, 
                'ambient': 0.8, 'environmental_details': 0.8, 'technical_effects': 0.7
            },
            AgentSpecialty.MOTION_SPECIALIST: {
                'motion': 0.9, 'physics': 0.9, 'action': 0.9, 'ending': 0.7
            },
            AgentSpecialty.TECHNICAL_DIRECTOR: {
                'keywords': 0.9, 'text': 0.9, 'quality': 0.8, 'aspect_ratio': 0.9
            }
        }
        
        logger.info("✅ Detailed VEO3 JSON Agent initialized")
    
    async def generate_detailed_json_prompt(self, 
                                           mission: str,
                                           style: str,
                                           tone: str,
                                           duration: int,
                                           platform: Platform,
                                           additional_context: Dict[str, Any] = None) -> Tuple[Dict[str, Any], str]:
        """
        Generate detailed nested JSON prompt using collaborative AI agents
        
        Returns:
            Tuple of (detailed_json_dict, formatted_text_for_veo3)
        """
        
        logger.info("🎬 Starting Detailed VEO3 JSON Generation...")
        
        # Step 1: Generate detailed structure with each agent
        agent_proposals = await self._gather_detailed_agent_proposals(
            mission, style, tone, duration, platform, additional_context
        )
        
        # Step 2: Weighted voting on each nested JSON field
        final_json = await self._detailed_weighted_voting(agent_proposals)
        
        # Step 3: Orchestrator review and final structure polish
        polished_json = await self._orchestrator_detailed_polish(final_json, mission, style, duration)
        
        # Step 4: Convert to text format for VEO3
        formatted_text = self._convert_detailed_json_to_veo3_text(polished_json)
        
        # Step 5: Save detailed outputs with comprehensive logging
        await self._save_detailed_artifacts(polished_json, formatted_text, mission, duration)
        
        logger.info("✅ Detailed VEO3 JSON prompt generated")
        return polished_json, formatted_text
    
    async def _gather_detailed_agent_proposals(self, mission: str, style: str, tone: str, 
                                             duration: int, platform: Platform, 
                                             additional_context: Dict) -> Dict[AgentSpecialty, Dict]:
        """Gather detailed proposals from each specialized agent"""
        
        detailed_examples = self._get_detailed_professional_examples()
        
        context_prompt = f"""
        MISSION: {mission}
        STYLE: {style}
        TONE: {tone}
        DURATION: {duration}s
        
        Create a VEO3 JSON with these sections: shot, subject, scene, visual_details, cinematography, audio, style.
        Example: {detailed_examples}
        
        Return ONLY valid JSON.
        """
        
        agents = {}
        model = GeminiModelHelper.get_configured_model(self.api_key)
        
        # Gather proposals from each agent
        for specialty in AgentSpecialty:
            if specialty == AgentSpecialty.ORCHESTRATOR:
                continue  # Orchestrator comes later
                
            agent_prompt = f"""
            {context_prompt}
            
            As {specialty.value}: Focus on {self._get_detailed_agent_focus(specialty)}
            Return JSON only.
            """
            
            try:
                # Apply timeout to AI call - increased to 90 seconds for complex prompts
                response = ai_wrapper.safe_ai_call(
                    model.generate_content,
                    agent_prompt,
                    timeout=90,
                    fallback_value=None
                )
                
                if response:
                    json_text = response.text.strip()
                    
                    # Clean up JSON
                    if json_text.startswith('```json'):
                        json_text = json_text[7:-3]
                    elif json_text.startswith('```'):
                        json_text = json_text[3:-3]
                    
                    try:
                        agents[specialty] = json.loads(json_text)
                        logger.debug(f"✅ {specialty.value} detailed proposal generated")
                    except json.JSONDecodeError as je:
                        logger.warning(f"⚠️ {specialty.value} returned invalid JSON: {je}")
                        agents[specialty] = self._get_agent_fallback(specialty)
                else:
                    logger.warning(f"⏱️ {specialty.value} agent timed out after 90s")
                    agents[specialty] = self._get_agent_fallback(specialty)
                
            except Exception as e:
                logger.warning(f"⚠️ {specialty.value} agent failed: {e}")
                agents[specialty] = self._get_agent_fallback(specialty)
        
        return agents
    
    def _get_detailed_professional_examples(self) -> str:
        """Get simplified examples to prevent timeouts - OPTIMIZED FOR SPEED"""
        return '''
        SIMPLIFIED EXAMPLE:
        {
          "shot": {"composition": "medium shot", "camera_motion": "static", "frame_rate": "24fps"},
          "subject": {"description": "person in modern setting", "wardrobe": "casual clothing"},
          "scene": {"location": "indoor space", "time_of_day": "day", "environment": "clean modern"},
          "visual_details": {"action": "standing and speaking", "props": ["furniture"], "physics": "realistic"},
          "cinematography": {"lighting": "natural daylight", "tone": "professional", "color_palette": "neutral"},
          "audio": {"dialogue": null, "primary_sounds": "ambient room tone", "ambient": "quiet indoor"},
          "style": {"visual_aesthetic": "cinematic", "aspect_ratio": "16:9", "quality": "HD"},
          "motion": "minimal movement",
          "ending": "scene concludes naturally",
          "text": "none",
          "keywords": ["16:9", "cinematic", "professional", "HD", "modern"]
        }
        '''
    
    def _get_detailed_agent_focus(self, specialty: AgentSpecialty) -> str:
        """Get detailed focus areas for each agent based on nested examples"""
        focus_map = {
            AgentSpecialty.CINEMATOGRAPHER: "Shot composition, camera motion, frame rate, film grain. Create 'shot' object with detailed technical specs",
            AgentSpecialty.VISUAL_DESIGNER: "Visual style, cinematography, lighting. Create 'cinematography' and 'style' objects with detailed aesthetics",
            AgentSpecialty.SCENE_ARCHITECT: "Scene location, environment, setting. Create 'scene' object with location, time_of_day, environment",
            AgentSpecialty.CHARACTER_DIRECTOR: "Subject details, character consistency. Create 'subject' object with description, wardrobe, character_consistency",
            AgentSpecialty.AUDIO_DIRECTOR: "Audio design, dialogue, sounds. Create 'audio' object with dialogue, primary_sounds, ambient, music",
            AgentSpecialty.MOTION_SPECIALIST: "Visual details, motion, physics. Create 'visual_details' object with action, props, physics. Also main 'motion' field",
            AgentSpecialty.TECHNICAL_DIRECTOR: "Keywords, technical specs. Create comprehensive keywords array and technical fields"
        }
        return focus_map.get(specialty, "General detailed video production")
    
    async def _detailed_weighted_voting(self, agent_proposals: Dict[AgentSpecialty, Dict]) -> Dict[str, Any]:
        """Use weighted voting for detailed nested structure"""
        
        final_json = {}
        
        # All possible fields from detailed examples
        all_fields = [
            # Flat fields
            'description', 'motion', 'ending', 'text', 'keywords',
            # Nested objects
            'shot', 'subject', 'scene', 'visual_details', 'cinematography', 'audio', 'style',
            # Legacy flat fields
            'camera', 'lighting', 'room', 'environment', 'location', 'setting', 'elements'
        ]
        
        for field in all_fields:
            field_proposals = []
            
            # Collect proposals for this field from all agents
            for specialty, proposal in agent_proposals.items():
                if field in proposal:
                    weight = self.agent_weights.get(specialty, {}).get(field, 0.3)
                    field_proposals.append({
                        'value': proposal[field],
                        'weight': weight,
                        'agent': specialty.value
                    })
            
            if field_proposals:
                # Select best proposal based on weight
                best_proposal = max(field_proposals, key=lambda x: x['weight'])
                final_json[field] = best_proposal['value']
                logger.debug(f"🗳️ {field}: selected from {best_proposal['agent']} (weight: {best_proposal['weight']})")
        
        return final_json
    
    async def _orchestrator_detailed_polish(self, draft_json: Dict[str, Any], mission: str, 
                                          style: str, duration: int) -> Dict[str, Any]:
        """Orchestrator reviews and polishes detailed nested structure"""
        
        model = GeminiModelHelper.get_configured_model(self.api_key)
        
        orchestrator_prompt = f"""
        Polish this VEO3 JSON for: {mission} ({style}, {duration}s)
        
        Current: {json.dumps(draft_json, indent=2)}
        
        Return improved JSON only.
        """
        
        try:
            # Apply timeout to orchestrator AI call - increased to 90 seconds
            response = ai_wrapper.safe_ai_call(
                model.generate_content,
                orchestrator_prompt,
                timeout=90,
                fallback_value=None
            )
            
            if response:
                json_text = response.text.strip()
                
                # Clean up JSON
                if json_text.startswith('```json'):
                    json_text = json_text[7:-3]
                elif json_text.startswith('```'):
                    json_text = json_text[3:-3]
                
                polished = json.loads(json_text)
                logger.info("✅ Detailed orchestrator polish completed")
            else:
                logger.warning("⏱️ Orchestrator timed out after 30s, using unpolished version")
                polished = final_json
            return polished
            
        except Exception as e:
            logger.warning(f"⚠️ Orchestrator polish failed: {e}, using draft")
            return draft_json
    
    def _convert_detailed_json_to_veo3_text(self, json_prompt: Dict[str, Any]) -> str:
        """Convert detailed JSON structure to formatted text for VEO3"""
        
        # VEO3 accepts detailed JSON as formatted text
        return json.dumps(json_prompt, indent=2)
    
    async def _save_detailed_artifacts(self, json_prompt: Dict[str, Any], formatted_text: str, 
                                     mission: str, duration: int):
        """Save detailed generation artifacts with comprehensive logging"""
        
        # Create prompts directory
        prompts_dir = os.path.dirname(self.session_context.get_output_path("prompts", ""))
        os.makedirs(prompts_dir, exist_ok=True)
        
        # Save detailed JSON prompt
        safe_mission = "".join(c for c in mission[:30] if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        json_path = self.session_context.get_output_path("prompts", f"detailed_veo3_prompt_{safe_mission}_{duration}s.json")
        with open(json_path, 'w') as f:
            json.dump(json_prompt, f, indent=2)
        
        # Save formatted text for VEO3
        text_path = self.session_context.get_output_path("prompts", f"detailed_veo3_formatted_{safe_mission}_{duration}s.txt")
        with open(text_path, 'w') as f:
            f.write(formatted_text)
        
        # COMPREHENSIVE JSON LOGGING as requested
        logger.info(f"🎯 DETAILED PROFESSIONAL JSON PROMPT GENERATED:")
        logger.info(f"📝 Full JSON Structure:\n{json.dumps(json_prompt, indent=2)}")
        
        # Log each major section
        for section, content in json_prompt.items():
            if isinstance(content, dict):
                logger.info(f"📋 {section.upper()} Section: {len(content)} fields")
                for field, value in content.items():
                    logger.info(f"   - {field}: {str(value)[:100]}")
            elif isinstance(content, list):
                logger.info(f"📋 {section.upper()} Array: {len(content)} items")
            else:
                logger.info(f"📋 {section.upper()}: {str(content)[:100]}")
        
        logger.info(f"💾 Detailed artifacts saved: {json_path}, {text_path}")
    
    def _get_agent_fallback(self, agent: AgentSpecialty) -> Dict[str, Any]:
        """Get fallback structure for failed agent"""
        fallbacks = {
            AgentSpecialty.CINEMATOGRAPHER: {
                "shot": {"composition": "medium shot"},
                "camera_motion": "static",
                "frame_rate": "24fps"
            },
            AgentSpecialty.VISUAL_DESIGNER: {
                "style": {"visual_aesthetic": "cinematic"},
                "cinematography": {"lighting": "natural", "tone": "neutral"}
            },
            AgentSpecialty.SCENE_ARCHITECT: {
                "scene": {"location": "generic setting", "time_of_day": "day"}
            },
            AgentSpecialty.CHARACTER_DIRECTOR: {
                "subject": {"description": "main character"}
            },
            AgentSpecialty.AUDIO_DIRECTOR: {
                "audio": {"ambient": "natural sounds"}
            },
            AgentSpecialty.MOTION_SPECIALIST: {
                "motion": "natural movement",
                "physics": "realistic"
            },
            AgentSpecialty.TECHNICAL_DIRECTOR: {
                "keywords": ["professional", "high quality"],
                "quality": "4K"
            },
            AgentSpecialty.ORCHESTRATOR: {}
        }
        return fallbacks.get(agent, {})


# Test function
async def test_detailed_waltz_bashir():
    """Test detailed VEO3 JSON generation for Waltz with Bashir"""
    
    logger.info("🚀 Testing Detailed VEO3 JSON Generation - Waltz with Bashir")
    logger.info("=" * 70)
    
    session = SessionContext("detailed_waltz_bashir_test")
    agent = DetailedVEO3JsonAgent(session)
    
    mission = """Self POV 'Waltz with Bashir' animation style, the self is Israeli soldier 
    holding M4 rifle going in olive trees area, hiding from young terrorists throwing 
    little stones on him"""
    
    json_prompt, formatted_text = await agent.generate_detailed_json_prompt(
        mission=mission,
        style="Waltz with Bashir rotoscoped animation",
        tone="tense, defensive, survival",
        duration=10,
        platform=Platform.YOUTUBE,
        additional_context={
            "perspective": "first-person POV",
            "character": "Israeli soldier with PTSD",
            "equipment": "M4 rifle visible in frame",
            "environment": "olive grove, Mediterranean terrain",
            "threat": "stone-throwing youth",
            "animation_style": "rotoscoped, high contrast, surreal"
        }
    )
    
    logger.info("✅ Detailed JSON Test Completed")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_detailed_waltz_bashir())