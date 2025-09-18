"""
Professional VEO3 JSON Prompt Generation Agent
Creates comprehensive, detailed JSON prompts matching professional examples from Tesla, Pepsi, Apple, etc.
Uses collaborative AI agents with weighted voting system and proper field structure
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
except ImportError:
    from src.agents.gemini_helper import GeminiModelHelper, ensure_api_key
    from src.utils.logging_config import get_logger
    from src.models.video_models import Platform
    from src.utils.session_context import SessionContext

logger = get_logger(__name__)


class AgentSpecialty(Enum):
    """Specialized agent roles for VEO3 JSON generation based on professional examples"""
    CINEMATOGRAPHER = "cinematographer"        # Camera, shots, cinematography
    VISUAL_DESIGNER = "visual_designer"       # Style, lighting, visual aesthetics
    MOTION_DIRECTOR = "motion_director"       # Movement, physics, action sequences
    SCENE_ARCHITECT = "scene_architect"       # Environment, room, setting, location
    NARRATIVE_DIRECTOR = "narrative_director"  # Description, story, sequence, ending
    TECHNICAL_DIRECTOR = "technical_director"  # Keywords, text, technical specs
    ORCHESTRATOR = "orchestrator"             # Final decisions, weighting


class ProfessionalVEO3JsonAgent:
    """Professional VEO3 JSON prompt generation matching industry examples"""
    
    def __init__(self, session_context: SessionContext, api_key: Optional[str] = None):
        """Initialize the professional VEO3 JSON agent"""
        self.session_context = session_context
        self.api_key = ensure_api_key(api_key)
        
        # Agent expertise weights for voting
        self.agent_weights = {
            AgentSpecialty.CINEMATOGRAPHER: {
                'camera': 0.9, 'lighting': 0.6, 'style': 0.5
            },
            AgentSpecialty.VISUAL_DESIGNER: {
                'style': 0.9, 'lighting': 0.9, 'elements': 0.7
            },
            AgentSpecialty.MOTION_DIRECTOR: {
                'motion': 0.9, 'ending': 0.7, 'sequence': 0.8
            },
            AgentSpecialty.SCENE_ARCHITECT: {
                'room': 0.9, 'environment': 0.9, 'location': 0.9, 'setting': 0.9, 'elements': 0.8
            },
            AgentSpecialty.NARRATIVE_DIRECTOR: {
                'description': 0.9, 'sequence': 0.9, 'ending': 0.8, 'scene': 0.7
            },
            AgentSpecialty.TECHNICAL_DIRECTOR: {
                'keywords': 0.9, 'text': 0.9, 'audio': 0.8
            }
        }
        
        logger.info("✅ Professional VEO3 JSON Agent initialized")
    
    async def generate_professional_json_prompt(self, 
                                               mission: str,
                                               style: str,
                                               tone: str,
                                               duration: int,
                                               platform: Platform,
                                               additional_context: Dict[str, Any] = None) -> Tuple[Dict[str, Any], str]:
        """
        Generate professional JSON prompt using collaborative AI agents
        
        Returns:
            Tuple of (json_dict, formatted_text_for_veo3)
        """
        
        logger.info("🎬 Starting Professional VEO3 JSON Generation...")
        
        # Step 1: Generate base structure with each agent using professional examples
        agent_proposals = await self._gather_professional_agent_proposals(
            mission, style, tone, duration, platform, additional_context
        )
        
        # Step 2: Weighted voting on each JSON field
        final_json = await self._professional_weighted_voting(agent_proposals)
        
        # Step 3: Orchestrator review and final polish
        polished_json = await self._orchestrator_professional_polish(final_json, mission, style, duration)
        
        # Step 4: Convert to text format for VEO3
        formatted_text = self._convert_json_to_veo3_text(polished_json)
        
        # Step 5: Save outputs with proper logging
        await self._save_professional_artifacts(polished_json, formatted_text, mission, duration)
        
        logger.info("✅ Professional VEO3 JSON prompt generated")
        return polished_json, formatted_text
    
    async def _gather_professional_agent_proposals(self, mission: str, style: str, tone: str, 
                                                 duration: int, platform: Platform, 
                                                 additional_context: Dict) -> Dict[AgentSpecialty, Dict]:
        """Gather proposals from each specialized agent using professional examples"""
        
        professional_examples = self._get_professional_examples()
        
        context_prompt = f"""
        MISSION: {mission}
        STYLE: {style}
        TONE: {tone}
        DURATION: {duration} seconds
        PLATFORM: {platform.value}
        ADDITIONAL: {json.dumps(additional_context or {}, indent=2)}
        
        You are creating a VEO3 video generation prompt. Study these PROFESSIONAL EXAMPLES from major brands:
        
        {professional_examples}
        
        CRITICAL REQUIREMENTS:
        1. Use EXACTLY the same field structure as the examples
        2. Include ALL required fields: description, style, camera, lighting, room/environment/location/setting, elements, motion, ending, text, keywords
        3. Make keywords comprehensive with aspect ratio (16:9) and specific descriptors
        4. Write detailed, cinematic descriptions like the professional examples
        5. Ensure "text" field is "none" unless text is specifically needed
        6. Make elements array detailed and specific
        7. Camera should describe specific shots and movements
        8. Motion should describe physics and timing
        9. Ending should describe the final frame/moment
        
        Create a JSON in this exact professional format for the given mission.
        """
        
        agents = {}
        model = GeminiModelHelper.get_configured_model(self.api_key)
        
        # Gather proposals from each agent
        for specialty in AgentSpecialty:
            if specialty == AgentSpecialty.ORCHESTRATOR:
                continue  # Orchestrator comes later
                
            agent_prompt = f"""
            {context_prompt}
            
            As a {specialty.value.replace('_', ' ').title()}, focus on your specialty areas:
            {self._get_professional_agent_focus(specialty)}
            
            Generate a comprehensive JSON structure focusing on your expertise.
            Use the EXACT field names from the professional examples.
            Return ONLY valid JSON, no explanations.
            """
            
            try:
                response = model.generate_content(agent_prompt)
                json_text = response.text.strip()
                
                # Clean up JSON
                if json_text.startswith('```json'):
                    json_text = json_text[7:-3]
                elif json_text.startswith('```'):
                    json_text = json_text[3:-3]
                
                agents[specialty] = json.loads(json_text)
                logger.debug(f"✅ {specialty.value} professional proposal generated")
                
            except Exception as e:
                logger.warning(f"⚠️ {specialty.value} agent failed: {e}")
                agents[specialty] = {}
        
        return agents
    
    def _get_professional_examples(self) -> str:
        """Get professional examples for AI agents to study"""
        return '''
        TESLA EXAMPLE:
        {
          "description": "Cinematic shot of a minimalist Tesla-branded crate magically opening to reveal a fully formed Tesla vehicle and an instantly assembled, sleek Tesla-themed showroom around it. No text.",
          "style": "cinematic",
          "camera": "fixed wide angle, with subtle zooms on key transformations",
          "lighting": "controlled, high-tech, transitioning from dim to bright and clean",
          "room": "empty futuristic space transforming into a minimalist Tesla showroom",
          "elements": [
            "Tesla-branded crate (glowing seams)",
            "Tesla vehicle (e.g., Model 3/Y/Cybertruck)",
            "charging station",
            "minimalist display panels",
            "sleek showroom furniture",
            "ambient lighting elements"
          ],
          "motion": "crate panels retract smoothly and silently, car revealed, showroom elements rise/unfold precisely and rapidly",
          "ending": "pristine, inviting Tesla showroom with car as centerpiece",
          "text": "none",
          "keywords": [
            "16:9",
            "Tesla",
            "magic assembly",
            "showroom",
            "innovation",
            "futuristic",
            "no text",
            "clean design",
            "reveal"
          ]
        }
        
        PEPSI EXAMPLE:
        {
          "description": "Cinematic ultra-close-up of a cold, frosty Pepsi can resting on a sleek futuristic pedestal in a minimal, high-tech urban plaza. The Pepsi logo subtly pulses with energy. Suddenly-the tab *clicks* open in slow motion. From the opening, streams of liquid light spiral out, transforming the environment. Skyscrapers animate with giant LED screens showing vibrant Pepsi visuals.",
          "style": "cinematic, dynamic, magical futurism",
          "camera": "starts ultra close on condensation dripping from the Pepsi can, zooms out and orbits as the cityscape transforms around it in real-time",
          "lighting": "daylight fading into vibrant neon blues, reds, and purples-cyberpunk festival glow",
          "environment": "quiet futuristic plaza transforms into a high-energy city-scale holographic party",
          "elements": [
            "Pepsi can (logo illuminated, condensation detailed)",
            "slow-motion can tab opening with light burst",
            "liquid light spirals triggering environment change",
            "LED skyscrapers animating Pepsi visuals",
            "holographic concert stage assembling mid-air"
          ],
          "motion": "continuous chain reaction from the can opening-liquid energy flows, triggers rapid city transformation in dynamic, seamless time-lapse",
          "ending": "Pepsi can in foreground, the whole futuristic city in full festival mode behind it, pulsing with light and music",
          "text": "none",
          "keywords": [
            "Pepsi",
            "urban festival",
            "futuristic party",
            "city transforms",
            "dynamic animation",
            "holographic concert",
            "hyper-realistic",
            "cinematic",
            "no text"
          ]
        }
        
        TRANSFORMERS MECHA EXAMPLE:
        {
          "description": "The scene opens on a smooth, metallic silver egg resting in the center of a vast, gritty industrial hangar. Suddenly, glowing seams etch across its surface, and the egg doesn't unfold-it fractures. With a surge of energy, armored plates unlock and pull back, revealing a complex mechanical skeleton within.",
          "style": "Hyper-detailed, industrial mecha CGI. The aesthetic is inspired by 'Transformers' and 'Pacific Rim,' focusing on complex, hard-surface mechanics",
          "camera": "A single, dynamic continuous shot. Starts as a close-up on the egg, then pulls back and orbits the transformation",
          "lighting": "Begins with stark, top-down industrial lighting on the egg. As the transformation begins, a glowing blue power core ignites within the chest",
          "setting": "A vast, dark, and gritty industrial hangar with a weathered concrete floor and visible support beams",
          "elements": [
            "smooth metallic silver egg",
            "glowing energy seams",
            "shifting armor plates",
            "exposed pistons, gears, and hydraulics",
            "a glowing internal power core"
          ],
          "motion": "A violent, multi-layered mechanical reconfiguration. The motion is not fluid but clunky and purposeful",
          "ending": "The fully constructed robotic T-Rex stands in a low, predatory stance. It throws its head back",
          "text": "As the final transformation completes, steam erupts from vents on its neck and shoulders.",
          "keywords": [
            "mecha",
            "robot",
            "T-Rex",
            "transformer",
            "transformation",
            "mechanical",
            "industrial",
            "CGI",
            "sci-fi"
          ]
        }
        '''
    
    def _get_professional_agent_focus(self, specialty: AgentSpecialty) -> str:
        """Get focus areas description for each agent based on professional examples"""
        focus_map = {
            AgentSpecialty.CINEMATOGRAPHER: "Camera work: shots, angles, movement, lens choice. Study Tesla's 'fixed wide angle with subtle zooms' and Pepsi's 'ultra close then orbits'",
            AgentSpecialty.VISUAL_DESIGNER: "Visual style and lighting: aesthetic, mood, color. Study Tesla's 'high-tech transitioning' and Pepsi's 'cyberpunk festival glow'",
            AgentSpecialty.MOTION_DIRECTOR: "Movement and physics: how things move, timing, dynamics. Study Tesla's 'panels retract smoothly' and Transformers' 'clunky purposeful motion'",
            AgentSpecialty.SCENE_ARCHITECT: "Environment and setting: room, location, space. Study Tesla's 'futuristic showroom' and Pepsi's 'urban plaza transforms'",
            AgentSpecialty.NARRATIVE_DIRECTOR: "Description and story flow: main description, sequence, ending. Study professional examples' detailed descriptions",
            AgentSpecialty.TECHNICAL_DIRECTOR: "Keywords and technical specs: comprehensive keyword arrays, text field, technical requirements"
        }
        return focus_map.get(specialty, "General video production")
    
    async def _professional_weighted_voting(self, agent_proposals: Dict[AgentSpecialty, Dict]) -> Dict[str, Any]:
        """Use weighted voting to decide on each JSON field using professional standards"""
        
        final_json = {}
        
        # Professional fields from examples
        professional_fields = ['description', 'style', 'camera', 'lighting', 'room', 'environment', 
                              'location', 'setting', 'elements', 'motion', 'ending', 'text', 'keywords', 
                              'sequence', 'audio', 'scene']
        
        for field in professional_fields:
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
    
    async def _orchestrator_professional_polish(self, draft_json: Dict[str, Any], mission: str, 
                                              style: str, duration: int) -> Dict[str, Any]:
        """Orchestrator reviews and polishes using professional standards"""
        
        model = GeminiModelHelper.get_configured_model(self.api_key)
        
        orchestrator_prompt = f"""
        As the ORCHESTRATOR, review and polish this VEO3 JSON prompt to match PROFESSIONAL STANDARDS:
        
        ORIGINAL MISSION: {mission}
        STYLE: {style}
        DURATION: {duration} seconds
        
        CURRENT JSON:
        {json.dumps(draft_json, indent=2)}
        
        PROFESSIONAL STANDARDS TO ENFORCE:
        1. Description: Must be detailed and cinematic like Tesla/Pepsi examples
        2. Keywords: Must include "16:9" and be comprehensive (8+ keywords)
        3. Elements: Must be detailed array with specific descriptions
        4. Camera: Must describe specific shots and movements
        5. Motion: Must describe physics and timing details
        6. Ending: Must describe the final frame/moment
        7. Text: Should be "none" unless text is specifically needed
        8. Style: Should be concise but descriptive
        9. Lighting: Should describe mood and technical aspects
        10. Room/Environment/Setting: Choose the most appropriate field name
        
        Return the polished JSON. Return ONLY valid JSON, no explanations.
        """
        
        try:
            response = model.generate_content(orchestrator_prompt)
            json_text = response.text.strip()
            
            # Clean up JSON
            if json_text.startswith('```json'):
                json_text = json_text[7:-3]
            elif json_text.startswith('```'):
                json_text = json_text[3:-3]
            
            polished = json.loads(json_text)
            logger.info("✅ Professional orchestrator polish completed")
            return polished
            
        except Exception as e:
            logger.warning(f"⚠️ Orchestrator polish failed: {e}, using draft")
            return draft_json
    
    def _convert_json_to_veo3_text(self, json_prompt: Dict[str, Any]) -> str:
        """Convert JSON structure to formatted text for VEO3"""
        
        # VEO3 accepts JSON as formatted text
        return json.dumps(json_prompt, indent=2)
    
    async def _save_professional_artifacts(self, json_prompt: Dict[str, Any], formatted_text: str, 
                                         mission: str, duration: int):
        """Save generation artifacts to session with proper logging"""
        
        # Create prompts directory
        prompts_dir = os.path.dirname(self.session_context.get_output_path("prompts", ""))
        os.makedirs(prompts_dir, exist_ok=True)
        
        # Save JSON prompt with mission in filename
        safe_mission = "".join(c for c in mission[:30] if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        json_path = self.session_context.get_output_path("prompts", f"professional_veo3_prompt_{safe_mission}_{duration}s.json")
        with open(json_path, 'w') as f:
            json.dump(json_prompt, f, indent=2)
        
        # Save formatted text for VEO3
        text_path = self.session_context.get_output_path("prompts", f"professional_veo3_formatted_{safe_mission}_{duration}s.txt")
        with open(text_path, 'w') as f:
            f.write(formatted_text)
        
        # Log the JSON in the output for debugging
        logger.info(f"🎯 PROFESSIONAL JSON PROMPT GENERATED:")
        logger.info(f"📝 JSON Content:\n{json.dumps(json_prompt, indent=2)}")
        
        logger.info(f"💾 Professional artifacts saved: {json_path}, {text_path}")


# Example usage and testing
if __name__ == "__main__":
    async def test_professional_agent():
        session = SessionContext("test_professional_veo3")
        agent = ProfessionalVEO3JsonAgent(session)
        
        mission = """Self POV 'Waltz with Bashir' animation style, the self is Israeli soldier 
        holding M4 rifle going in olive trees area, hiding from young terrorists throwing 
        little stones on him"""
        
        json_prompt, formatted_text = await agent.generate_professional_json_prompt(
            mission=mission,
            style="Waltz with Bashir rotoscoped animation",
            tone="tense, defensive, survival",
            duration=10,
            platform=Platform.YOUTUBE,
            additional_context={
                "perspective": "first-person POV",
                "character": "Israeli soldier",
                "equipment": "M4 rifle visible in frame",
                "environment": "olive grove, Mediterranean terrain",
                "threat": "stone-throwing youth",
                "animation_style": "rotoscoped, high contrast, surreal"
            }
        )
        
        print("📝 Generated Professional JSON:")
        print(json.dumps(json_prompt, indent=2))
        print("\n🎬 Formatted for VEO3:")
        print(formatted_text[:500] + "...")
    
    asyncio.run(test_professional_agent())