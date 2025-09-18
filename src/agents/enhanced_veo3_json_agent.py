"""
Enhanced VEO3 JSON Prompt Generation Agent
Creates comprehensive, detailed JSON prompts based on user examples
Uses collaborative AI agents with weighted voting system
"""

import json
import asyncio
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
    """Specialized agent roles for VEO3 JSON generation"""
    CINEMATOGRAPHER = "cinematographer"        # Camera, shots, cinematography
    VISUAL_DESIGNER = "visual_designer"       # Style, colors, effects, lighting
    MOTION_DIRECTOR = "motion_director"       # Movement, physics, motion
    SCENE_ARCHITECT = "scene_architect"       # Environment, setting, props
    NARRATIVE_DIRECTOR = "narrative_director"  # Story, sequence, timing
    TECHNICAL_DIRECTOR = "technical_director"  # Specifications, format
    ORCHESTRATOR = "orchestrator"             # Final decisions, weighting


@dataclass
class VEO3JsonStructure:
    """Structure for comprehensive VEO3 JSON prompts"""
    description: str
    style: str
    camera: Optional[str] = None
    lighting: Optional[str] = None
    room: Optional[str] = None
    environment: Optional[str] = None
    elements: Optional[List[str]] = None
    motion: Optional[str] = None
    ending: Optional[str] = None
    text: str = "none"
    keywords: Optional[List[str]] = None
    sequence: Optional[List[Dict]] = None  # For complex sequences


class EnhancedVEO3JsonAgent:
    """Enhanced VEO3 JSON prompt generation with AI collaboration"""
    
    def __init__(self, session_context: SessionContext, api_key: Optional[str] = None):
        """Initialize the enhanced VEO3 JSON agent"""
        self.session_context = session_context
        self.api_key = ensure_api_key(api_key)
        
        # Agent expertise weights for voting
        self.agent_weights = {
            AgentSpecialty.CINEMATOGRAPHER: {
                'camera': 0.9, 'lighting': 0.7, 'style': 0.6
            },
            AgentSpecialty.VISUAL_DESIGNER: {
                'style': 0.9, 'lighting': 0.8, 'elements': 0.7
            },
            AgentSpecialty.MOTION_DIRECTOR: {
                'motion': 0.9, 'camera': 0.6, 'ending': 0.7
            },
            AgentSpecialty.SCENE_ARCHITECT: {
                'room': 0.9, 'environment': 0.9, 'elements': 0.8
            },
            AgentSpecialty.NARRATIVE_DIRECTOR: {
                'description': 0.8, 'sequence': 0.9, 'ending': 0.8
            },
            AgentSpecialty.TECHNICAL_DIRECTOR: {
                'keywords': 0.9, 'text': 0.8, 'style': 0.6
            }
        }
        
        logger.info("✅ Enhanced VEO3 JSON Agent initialized")
    
    async def generate_comprehensive_json_prompt(self, 
                                               mission: str,
                                               style: str,
                                               tone: str,
                                               duration: int,
                                               platform: Platform,
                                               additional_context: Dict[str, Any] = None) -> Tuple[Dict[str, Any], str]:
        """
        Generate comprehensive JSON prompt using collaborative AI agents
        
        Returns:
            Tuple of (json_dict, formatted_text_for_veo3)
        """
        
        logger.info("🎬 Starting Enhanced VEO3 JSON Generation...")
        
        # Step 1: Generate base structure with each agent
        agent_proposals = await self._gather_agent_proposals(
            mission, style, tone, duration, platform, additional_context
        )
        
        # Step 2: Weighted voting on each JSON field
        final_json = await self._weighted_voting_on_fields(agent_proposals)
        
        # Step 3: Orchestrator review and final polish
        polished_json = await self._orchestrator_polish(final_json, mission, style, duration)
        
        # Step 4: Convert to text format for VEO3
        formatted_text = self._convert_json_to_veo3_text(polished_json)
        
        # Save outputs
        await self._save_generation_artifacts(polished_json, formatted_text)
        
        logger.info("✅ Enhanced VEO3 JSON prompt generated")
        return polished_json, formatted_text
    
    async def _gather_agent_proposals(self, mission: str, style: str, tone: str, 
                                    duration: int, platform: Platform, 
                                    additional_context: Dict) -> Dict[AgentSpecialty, Dict]:
        """Gather proposals from each specialized agent"""
        
        context_prompt = f"""
        MISSION: {mission}
        STYLE: {style}
        TONE: {tone}
        DURATION: {duration} seconds
        PLATFORM: {platform.value}
        ADDITIONAL: {json.dumps(additional_context or {}, indent=2)}
        
        You are creating a VEO3 video generation prompt. Study these example JSON structures:
        
        EXAMPLE 1 (Nutella Commercial):
        {{
          "description": "Photorealistic cinematic shot of a sunlit kitchen nook. A sealed Nutella jar begins to vibrate gently, then bursts open—releasing a rich explosion of swirling chocolate, roasted hazelnuts, toast slices, strawberries, and golden syrup. The ingredients twirl mid-air in gravity-defying slow motion, assembling into a picture-perfect Nutella breakfast platter on a rustic wooden table.",
          "style": "photorealistic cinematic",
          "camera": "slow orbital shot from low angle upward, transitioning into an overhead top-down reveal",
          "lighting": "morning sunlight streaming through soft white curtains, gentle glow on chocolate and fruit highlights",
          "room": "cozy breakfast nook with wooden table, beige walls, ceramic mugs, and hanging plants",
          "elements": ["sealed Nutella jar (center of table)", "thick chocolate ribbons swirling through air", "flying toasted bread slices with golden crust"],
          "motion": "jar shakes, lid pops and spins off, chocolate erupts upward with roasted hazelnuts orbiting it",
          "ending": "a beautifully arranged Nutella breakfast board sits steaming on the table, chocolate glistening in the sunlight",
          "text": "none",
          "keywords": ["16:9", "Nutella explosion", "hazelnuts", "swirling chocolate", "realistic food", "breakfast aesthetic", "slow motion", "natural morning light", "high detail", "no text"]
        }}
        
        EXAMPLE 2 (Transformers Mecha):
        {{
          "description": "The scene opens on a smooth, metallic silver egg resting in the center of a vast, gritty industrial hangar. Suddenly, glowing seams etch across its surface, and the egg doesn't unfold-it fractures. With a surge of energy, armored plates unlock and pull back, revealing a complex mechanical skeleton within.",
          "style": "Hyper-detailed, industrial mecha CGI. The aesthetic is inspired by 'Transformers' and 'Pacific Rim,' focusing on complex, hard-surface mechanics",
          "camera": "A single, dynamic continuous shot. Starts as a close-up on the egg, then pulls back and orbits the transformation",
          "lighting": "Begins with stark, top-down industrial lighting on the egg. As the transformation begins, a glowing blue power core ignites within the chest",
          "setting": "A vast, dark, and gritty industrial hangar with a weathered concrete floor and visible support beams",
          "elements": ["smooth metallic silver egg", "glowing energy seams", "shifting armor plates", "exposed pistons, gears, and hydraulics"],
          "motion": "A violent, multi-layered mechanical reconfiguration. The motion is not fluid but clunky and purposeful",
          "ending": "The fully constructed robotic T-Rex stands in a low, predatory stance. It throws its head back",
          "text": "As the final transformation completes, steam erupts from vents on its neck and shoulders.",
          "keywords": ["mecha", "robot", "T-Rex", "transformer", "transformation", "mechanical", "industrial", "hard surface modeling", "CGI", "sci-fi"]
        }}
        
        Create a JSON in this detailed format for the given mission.
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
            {self._get_agent_focus_areas(specialty)}
            
            Generate a comprehensive JSON structure focusing on your expertise.
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
                logger.debug(f"✅ {specialty.value} proposal generated")
                
            except Exception as e:
                logger.warning(f"⚠️ {specialty.value} agent failed: {e}")
                agents[specialty] = {}
        
        return agents
    
    def _get_agent_focus_areas(self, specialty: AgentSpecialty) -> str:
        """Get focus areas description for each agent"""
        focus_map = {
            AgentSpecialty.CINEMATOGRAPHER: "Camera angles, shot types, movement, lens choice, cinematography",
            AgentSpecialty.VISUAL_DESIGNER: "Visual style, lighting, color palette, effects, atmosphere",
            AgentSpecialty.MOTION_DIRECTOR: "Movement, physics, action sequences, timing, dynamics",
            AgentSpecialty.SCENE_ARCHITECT: "Environment, setting, props, spatial design, location",
            AgentSpecialty.NARRATIVE_DIRECTOR: "Story flow, sequence, pacing, beginning/ending",
            AgentSpecialty.TECHNICAL_DIRECTOR: "Keywords, format specifications, technical constraints"
        }
        return focus_map.get(specialty, "General video production")
    
    async def _weighted_voting_on_fields(self, agent_proposals: Dict[AgentSpecialty, Dict]) -> Dict[str, Any]:
        """Use weighted voting to decide on each JSON field"""
        
        final_json = {}
        
        # List of all possible JSON fields from examples
        all_fields = ['description', 'style', 'camera', 'lighting', 'room', 'environment', 
                     'setting', 'elements', 'motion', 'ending', 'text', 'keywords', 'sequence']
        
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
    
    async def _orchestrator_polish(self, draft_json: Dict[str, Any], mission: str, 
                                 style: str, duration: int) -> Dict[str, Any]:
        """Orchestrator reviews and polishes the final JSON"""
        
        model = GeminiModelHelper.get_configured_model(self.api_key)
        
        orchestrator_prompt = f"""
        As the ORCHESTRATOR, review and polish this VEO3 JSON prompt:
        
        ORIGINAL MISSION: {mission}
        STYLE: {style}
        DURATION: {duration} seconds
        
        CURRENT JSON:
        {json.dumps(draft_json, indent=2)}
        
        Your tasks:
        1. Ensure all fields are coherent and work together
        2. Verify description is detailed and cinematic
        3. Check that motion and ending create a complete sequence
        4. Ensure keywords are comprehensive and include aspect ratio
        5. Make final improvements for maximum VEO3 effectiveness
        
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
            logger.info("✅ Orchestrator polish completed")
            return polished
            
        except Exception as e:
            logger.warning(f"⚠️ Orchestrator polish failed: {e}, using draft")
            return draft_json
    
    def _convert_json_to_veo3_text(self, json_prompt: Dict[str, Any]) -> str:
        """Convert JSON structure to formatted text for VEO3"""
        
        # VEO3 accepts JSON as formatted text
        return json.dumps(json_prompt, indent=2)
    
    async def _save_generation_artifacts(self, json_prompt: Dict[str, Any], formatted_text: str):
        """Save generation artifacts to session"""
        
        # Save JSON prompt
        json_path = self.session_context.get_output_path("prompts", "veo3_enhanced_prompt.json")
        with open(json_path, 'w') as f:
            json.dump(json_prompt, f, indent=2)
        
        # Save formatted text for VEO3
        text_path = self.session_context.get_output_path("prompts", "veo3_formatted_prompt.txt")
        with open(text_path, 'w') as f:
            f.write(formatted_text)
        
        logger.info(f"💾 Artifacts saved: {json_path}, {text_path}")


# Example usage and testing
if __name__ == "__main__":
    async def test_enhanced_agent():
        session = SessionContext("test_enhanced_veo3")
        agent = EnhancedVEO3JsonAgent(session)
        
        mission = """Self POV 'Waltz with Bashir' animation style, the self is Israeli soldier 
        holding M4 rifle going in olive trees area, hiding from young terrorists throwing 
        little stones on him"""
        
        json_prompt, formatted_text = await agent.generate_comprehensive_json_prompt(
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
        
        print("📝 Generated JSON:")
        print(json.dumps(json_prompt, indent=2))
        print("\n🎬 Formatted for VEO3:")
        print(formatted_text[:500] + "...")
    
    asyncio.run(test_enhanced_agent())