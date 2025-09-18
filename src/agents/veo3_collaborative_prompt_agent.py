"""
VEO3 Collaborative JSON Prompt Generation System
AI agents collaborate to create comprehensive JSON prompts with weighted voting
Based on Meta Prompt Framework and Veo 3 best practices
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import AI service and helpers
try:
    from .gemini_helper import GeminiModelHelper
    from ..utils.logging_config import get_logger
    from ..models.video_models import Platform
    from ..utils.session_context import SessionContext
except ImportError:
    from src.agents.gemini_helper import GeminiModelHelper
    from src.utils.logging_config import get_logger
    from src.models.video_models import Platform
    from src.utils.session_context import SessionContext

logger = get_logger(__name__)


class AgentRole(Enum):
    """Specialized AI agent roles for VEO3 prompt generation"""
    DIRECTOR = "director"  # Camera, shots, cinematography
    VISUAL_ARTIST = "visual_artist"  # Style, colors, effects
    SOUND_DESIGNER = "sound_designer"  # Audio, music, dialogue
    CHARACTER_DESIGNER = "character_designer"  # Subject, wardrobe, appearance
    ENVIRONMENT_ARTIST = "environment_artist"  # Scene, location, props
    MOTION_SPECIALIST = "motion_specialist"  # Movement, physics, actions
    NARRATIVE_DIRECTOR = "narrative_director"  # Story, pacing, emotion
    TECHNICAL_DIRECTOR = "technical_director"  # Technical specs, constraints
    ORCHESTRATOR = "orchestrator"  # Final decisions, weight management


@dataclass
class AgentExpertise:
    """Define agent expertise areas and voting weights"""
    role: AgentRole
    primary_domains: List[str]
    secondary_domains: List[str]
    weight_multiplier: float = 1.0
    
    def get_weight_for_parameter(self, parameter: str) -> float:
        """Get voting weight for specific parameter"""
        if parameter in self.primary_domains:
            return 2.0 * self.weight_multiplier
        elif parameter in self.secondary_domains:
            return 1.0 * self.weight_multiplier
        else:
            return 0.5 * self.weight_multiplier


@dataclass
class VEO3JsonPrompt:
    """Comprehensive VEO3 JSON prompt structure based on Meta Framework"""
    
    # Shot Configuration
    shot: Dict[str, Any] = field(default_factory=lambda: {
        "composition": "rule of thirds",
        "shot_type": "medium_shot",
        "camera_movement": "static",
        "camera_angle": "eye_level",
        "lens": "50mm",
        "aperture": "f/2.8",
        "frame_rate": "24fps",
        "film_grain": "none",
        "aspect_ratio": "16:9"
    })
    
    # Subject/Character
    subject: Dict[str, Any] = field(default_factory=lambda: {
        "description": "",
        "wardrobe": "",
        "expression": "",
        "pose": "",
        "action": "",
        "age": "",
        "ethnicity": "",
        "build": "",
        "hair": "",
        "eyes": ""
    })
    
    # Scene/Environment
    scene: Dict[str, Any] = field(default_factory=lambda: {
        "location": "",
        "time_of_day": "day",
        "weather": "clear",
        "environment": "",
        "atmosphere": "",
        "props": [],
        "background_elements": []
    })
    
    # Visual Style
    visual_details: Dict[str, Any] = field(default_factory=lambda: {
        "style": "realistic",
        "color_palette": "natural",
        "texture": "smooth",
        "mood": "neutral",
        "rendering": "photorealistic",
        "lighting_style": "natural",
        "visual_effects": []
    })
    
    # Cinematography
    cinematography: Dict[str, Any] = field(default_factory=lambda: {
        "lighting_style": "natural",
        "key_light": "soft",
        "shadows": "medium",
        "color_temperature": "5600K",
        "visual_tone": "cinematic",
        "depth_of_field": "medium",
        "focus": "subject"
    })
    
    # Audio
    audio: Dict[str, Any] = field(default_factory=lambda: {
        "ambient": "",
        "voice": "",
        "music_style": "none",
        "sound_effects": [],
        "volume_levels": "balanced",
        "audio_quality": "professional"
    })
    
    # Effects
    effects: Dict[str, Any] = field(default_factory=lambda: {
        "motion_blur": "none",
        "depth_of_field": "medium",
        "vignette": False,
        "chromatic_aberration": "none",
        "lens_flare": False,
        "particles": []
    })
    
    # Narrative
    narrative: Dict[str, Any] = field(default_factory=lambda: {
        "story_beat": "",
        "emotional_tone": "",
        "pacing": "normal",
        "tension_level": "medium",
        "narrative_arc": ""
    })
    
    # Dialogue
    dialogue: Dict[str, Any] = field(default_factory=lambda: {
        "text": "",
        "character_name": "",
        "tone": "",
        "delivery_style": "",
        "volume": "normal",
        "accent": "neutral"
    })
    
    # Technical
    technical: Dict[str, Any] = field(default_factory=lambda: {
        "duration": 8,
        "resolution": "1080p",
        "fps": 24,
        "seed": None,
        "generate_audio": True,
        "model": "veo-3.0-generate-001"
    })
    
    # Constraints (Negative Prompts)
    constraints: Dict[str, Any] = field(default_factory=lambda: {
        "avoid": ["text overlays", "logos", "watermarks", "subtitles", "captions"],
        "ensure": ["character consistency", "style coherence", "realistic physics"],
        "quality_negatives": ["blurry", "distorted", "amateur", "low quality"]
    })


class VEO3CollaborativePromptAgent:
    """Orchestrates multiple AI agents to collaboratively create VEO3 prompts"""
    
    def __init__(self, session_context: Optional[SessionContext] = None):
        self.gemini = GeminiModelHelper()
        self.session = session_context
        self.agents = self._initialize_agents()
        self.logger = get_logger(__name__)
        
    def _initialize_agents(self) -> Dict[AgentRole, AgentExpertise]:
        """Initialize agent expertise and voting weights"""
        return {
            AgentRole.DIRECTOR: AgentExpertise(
                role=AgentRole.DIRECTOR,
                primary_domains=["shot", "camera_movement", "camera_angle", "lens", "composition"],
                secondary_domains=["cinematography", "visual_tone", "pacing"],
                weight_multiplier=1.2
            ),
            AgentRole.VISUAL_ARTIST: AgentExpertise(
                role=AgentRole.VISUAL_ARTIST,
                primary_domains=["visual_details", "style", "color_palette", "texture", "rendering"],
                secondary_domains=["effects", "mood", "atmosphere"],
                weight_multiplier=1.1
            ),
            AgentRole.SOUND_DESIGNER: AgentExpertise(
                role=AgentRole.SOUND_DESIGNER,
                primary_domains=["audio", "ambient", "music_style", "sound_effects", "dialogue"],
                secondary_domains=["voice", "volume_levels", "audio_quality"],
                weight_multiplier=1.0
            ),
            AgentRole.CHARACTER_DESIGNER: AgentExpertise(
                role=AgentRole.CHARACTER_DESIGNER,
                primary_domains=["subject", "wardrobe", "expression", "pose", "description"],
                secondary_domains=["action", "age", "ethnicity", "build"],
                weight_multiplier=1.2
            ),
            AgentRole.ENVIRONMENT_ARTIST: AgentExpertise(
                role=AgentRole.ENVIRONMENT_ARTIST,
                primary_domains=["scene", "location", "environment", "props", "background_elements"],
                secondary_domains=["time_of_day", "weather", "atmosphere"],
                weight_multiplier=1.0
            ),
            AgentRole.MOTION_SPECIALIST: AgentExpertise(
                role=AgentRole.MOTION_SPECIALIST,
                primary_domains=["action", "camera_movement", "motion_blur", "physics"],
                secondary_domains=["pacing", "frame_rate", "effects"],
                weight_multiplier=1.1
            ),
            AgentRole.NARRATIVE_DIRECTOR: AgentExpertise(
                role=AgentRole.NARRATIVE_DIRECTOR,
                primary_domains=["narrative", "story_beat", "emotional_tone", "pacing"],
                secondary_domains=["dialogue", "tension_level", "narrative_arc"],
                weight_multiplier=1.0
            ),
            AgentRole.TECHNICAL_DIRECTOR: AgentExpertise(
                role=AgentRole.TECHNICAL_DIRECTOR,
                primary_domains=["technical", "constraints", "resolution", "fps", "quality_negatives"],
                secondary_domains=["aspect_ratio", "generate_audio", "model"],
                weight_multiplier=1.3
            )
        }
    
    async def generate_collaborative_prompt(
        self,
        mission: str,
        style: str,
        tone: str,
        duration: float = 8.0,
        platform: Platform = Platform.YOUTUBE,
        additional_context: Optional[Dict] = None
    ) -> Tuple[VEO3JsonPrompt, str]:
        """Generate VEO3 prompt through collaborative agent discussion"""
        
        logger.info("🎬 Starting VEO3 Collaborative Prompt Generation")
        logger.info(f"   Mission: {mission[:100]}...")
        logger.info(f"   Style: {style}")
        logger.info(f"   Tone: {tone}")
        
        # Initialize base prompt
        prompt = VEO3JsonPrompt()
        prompt.technical["duration"] = duration
        
        # Phase 1: Initial proposal generation by each agent
        proposals = await self._gather_agent_proposals(mission, style, tone, platform)
        
        # Phase 2: Cross-agent discussion and feedback
        discussed_proposals = await self._conduct_agent_discussion(proposals, mission)
        
        # Phase 3: Weighted voting on each parameter
        final_parameters = await self._conduct_weighted_voting(discussed_proposals)
        
        # Phase 4: Apply final parameters to prompt
        prompt = self._apply_final_parameters(prompt, final_parameters)
        
        # Phase 5: Convert to formatted text for VEO3
        formatted_text = self._convert_json_to_formatted_text(prompt)
        
        # Save to session if available
        if self.session:
            self._save_to_session(prompt, formatted_text)
        
        logger.info("✅ Collaborative prompt generation completed")
        return prompt, formatted_text
    
    async def _gather_agent_proposals(
        self,
        mission: str,
        style: str,
        tone: str,
        platform: Platform
    ) -> Dict[AgentRole, Dict[str, Any]]:
        """Each agent generates initial proposals for their domain"""
        
        proposals = {}
        tasks = []
        
        async def get_agent_proposal(agent_role: AgentRole, expertise: AgentExpertise):
            prompt = f"""
            As a {agent_role.value} expert for VEO3 video generation, analyze this mission and provide specific parameters for your domain.
            
            Mission: {mission}
            Style: {style}
            Tone: {tone}
            Platform: {platform.value}
            
            Your expertise areas: {', '.join(expertise.primary_domains)}
            Secondary areas: {', '.join(expertise.secondary_domains)}
            
            Based on the Meta Prompt Framework and VEO3 best practices, provide detailed specifications for your domain.
            Include specific technical details, creative choices, and rationale.
            
            Return as JSON with your recommended parameters.
            """
            
            try:
                response = await asyncio.to_thread(
                    self.gemini.generate_content,
                    prompt
                )
                
                # Parse JSON from response
                json_str = self._extract_json(response)
                proposal = json.loads(json_str) if json_str else {}
                
                return agent_role, proposal
            except Exception as e:
                logger.error(f"Error getting proposal from {agent_role}: {e}")
                return agent_role, {}
        
        # Gather proposals in parallel
        for agent_role, expertise in self.agents.items():
            if agent_role != AgentRole.ORCHESTRATOR:
                tasks.append(get_agent_proposal(agent_role, expertise))
        
        results = await asyncio.gather(*tasks)
        
        for agent_role, proposal in results:
            proposals[agent_role] = proposal
            logger.debug(f"📝 {agent_role.value} proposal received")
        
        return proposals
    
    async def _conduct_agent_discussion(
        self,
        proposals: Dict[AgentRole, Dict[str, Any]],
        mission: str
    ) -> Dict[AgentRole, Dict[str, Any]]:
        """Agents discuss and provide feedback on each other's proposals"""
        
        discussed_proposals = {}
        
        for agent_role, proposal in proposals.items():
            # Get feedback from other agents
            feedback_prompt = f"""
            As a collaborative team working on VEO3 prompt generation for: {mission}
            
            Review the {agent_role.value}'s proposal:
            {json.dumps(proposal, indent=2)}
            
            Other agents' proposals for context:
            {json.dumps({k.value: v for k, v in proposals.items() if k != agent_role}, indent=2)}
            
            Provide constructive feedback and suggestions to improve alignment and coherence.
            Consider:
            1. Technical feasibility in VEO3
            2. Consistency with other parameters
            3. Alignment with mission and style
            4. Meta Prompt Framework best practices
            
            Return refined parameters as JSON.
            """
            
            try:
                response = await asyncio.to_thread(
                    self.gemini.generate_content,
                    feedback_prompt
                )
                
                json_str = self._extract_json(response)
                refined_proposal = json.loads(json_str) if json_str else proposal
                discussed_proposals[agent_role] = refined_proposal
                
            except Exception as e:
                logger.error(f"Error in discussion for {agent_role}: {e}")
                discussed_proposals[agent_role] = proposal
        
        return discussed_proposals
    
    async def _conduct_weighted_voting(
        self,
        proposals: Dict[AgentRole, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Conduct weighted voting on each parameter"""
        
        final_parameters = {}
        all_parameters = set()
        
        # Collect all parameters
        for proposal in proposals.values():
            all_parameters.update(self._flatten_dict_keys(proposal))
        
        # Vote on each parameter
        for param_path in all_parameters:
            votes = []
            
            for agent_role, proposal in proposals.items():
                value = self._get_nested_value(proposal, param_path)
                if value is not None:
                    expertise = self.agents[agent_role]
                    weight = expertise.get_weight_for_parameter(param_path.split('.')[0])
                    votes.append((value, weight, agent_role))
            
            if votes:
                # Orchestrator makes final decision based on weighted votes
                final_value = await self._orchestrator_decision(param_path, votes)
                self._set_nested_value(final_parameters, param_path, final_value)
        
        return final_parameters
    
    async def _orchestrator_decision(
        self,
        parameter: str,
        votes: List[Tuple[Any, float, AgentRole]]
    ) -> Any:
        """Orchestrator makes final decision based on weighted votes"""
        
        # For consistent values, use highest weighted
        value_weights = {}
        for value, weight, role in votes:
            value_key = str(value)
            if value_key not in value_weights:
                value_weights[value_key] = 0
            value_weights[value_key] += weight
        
        # Return value with highest total weight
        if value_weights:
            best_value = max(value_weights.items(), key=lambda x: x[1])
            
            # Convert back to original type
            for value, _, _ in votes:
                if str(value) == best_value[0]:
                    logger.debug(f"🗳️ {parameter}: {value} (weight: {best_value[1]:.2f})")
                    return value
        
        return votes[0][0] if votes else None
    
    def _apply_final_parameters(
        self,
        prompt: VEO3JsonPrompt,
        parameters: Dict[str, Any]
    ) -> VEO3JsonPrompt:
        """Apply final parameters to prompt object"""
        
        for param_path, value in self._flatten_dict(parameters).items():
            self._set_prompt_value(prompt, param_path, value)
        
        return prompt
    
    def _convert_json_to_formatted_text(self, prompt: VEO3JsonPrompt) -> str:
        """Convert JSON prompt to formatted text for VEO3 API"""
        
        # Convert to professional VEO3 format based on Meta Framework
        formatted_parts = []
        
        # 1. Subject/Character (with comprehensive details)
        if prompt.subject["description"]:
            subject_text = f"Subject: {prompt.subject['description']}"
            if prompt.subject["age"]:
                subject_text += f", {prompt.subject['age']} years old"
            if prompt.subject["ethnicity"]:
                subject_text += f", {prompt.subject['ethnicity']}"
            if prompt.subject["build"]:
                subject_text += f", {prompt.subject['build']} build"
            if prompt.subject["hair"]:
                subject_text += f", {prompt.subject['hair']} hair"
            if prompt.subject["eyes"]:
                subject_text += f", {prompt.subject['eyes']} eyes"
            if prompt.subject["wardrobe"]:
                subject_text += f", wearing {prompt.subject['wardrobe']}"
            if prompt.subject["expression"]:
                subject_text += f", {prompt.subject['expression']} expression"
            formatted_parts.append(subject_text)
        
        # 2. Action
        if prompt.subject["action"]:
            formatted_parts.append(f"Action: {prompt.subject['action']}")
        
        # 3. Scene/Environment
        if prompt.scene["location"]:
            scene_text = f"Scene: {prompt.scene['location']}"
            if prompt.scene["time_of_day"]:
                scene_text += f", {prompt.scene['time_of_day']}"
            if prompt.scene["weather"]:
                scene_text += f", {prompt.scene['weather']} weather"
            if prompt.scene["atmosphere"]:
                scene_text += f", {prompt.scene['atmosphere']} atmosphere"
            if prompt.scene["props"]:
                scene_text += f", with {', '.join(prompt.scene['props'])}"
            formatted_parts.append(scene_text)
        
        # 4. Style and Cinematography
        style_text = f"Style: {prompt.shot['shot_type']} shot"
        if prompt.shot["camera_angle"]:
            style_text += f", {prompt.shot['camera_angle']} angle"
        if prompt.shot["camera_movement"] != "static":
            style_text += f", {prompt.shot['camera_movement']} camera movement"
        style_text += f" (thats where the camera is)"  # Critical for VEO3
        
        if prompt.visual_details["style"]:
            style_text += f", {prompt.visual_details['style']} visual style"
        if prompt.cinematography["lighting_style"]:
            style_text += f", {prompt.cinematography['lighting_style']} lighting"
        formatted_parts.append(style_text)
        
        # 5. Dialogue (using colon format to prevent subtitles)
        if prompt.dialogue["text"]:
            dialogue_text = f"Dialogue: {prompt.dialogue['character_name'] or 'Character'} says: "
            dialogue_text += f'"{prompt.dialogue["text"]}"'
            if prompt.dialogue["tone"]:
                dialogue_text += f" (Tone: {prompt.dialogue['tone']})"
            formatted_parts.append(dialogue_text)
        
        # 6. Audio
        if prompt.audio["ambient"] or prompt.audio["sound_effects"]:
            audio_text = "Audio: "
            audio_parts = []
            if prompt.audio["ambient"]:
                audio_parts.append(prompt.audio["ambient"])
            if prompt.audio["sound_effects"]:
                audio_parts.extend(prompt.audio["sound_effects"])
            audio_text += ", ".join(audio_parts)
            formatted_parts.append(audio_text)
        
        # 7. Technical and Quality (Negative Prompt)
        negative_parts = ["Technical: No " + ", no ".join(prompt.constraints["avoid"])]
        if prompt.constraints["quality_negatives"]:
            negative_parts.append("avoid " + ", ".join(prompt.constraints["quality_negatives"]))
        formatted_parts.append(". ".join(negative_parts))
        
        # Additional technical specs
        formatted_parts.append(f"Duration: {prompt.technical['duration']} seconds")
        formatted_parts.append(f"Resolution: {prompt.technical['resolution']}, {prompt.technical['fps']}fps")
        
        # Ensure requirements
        if prompt.constraints["ensure"]:
            formatted_parts.append(f"Ensure: {', '.join(prompt.constraints['ensure'])}")
        
        # Join all parts
        formatted_text = "\n\n".join(formatted_parts)
        
        # Also append the raw JSON for advanced users
        formatted_text += "\n\n[VEO3_JSON_STRUCTURE]\n"
        formatted_text += json.dumps(asdict(prompt), indent=2)
        
        return formatted_text
    
    def _flatten_dict_keys(self, d: Dict, parent_key: str = '') -> set:
        """Get all nested dictionary keys as paths"""
        keys = set()
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            keys.add(new_key)
            if isinstance(v, dict):
                keys.update(self._flatten_dict_keys(v, new_key))
        return keys
    
    def _flatten_dict(self, d: Dict, parent_key: str = '') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _get_nested_value(self, d: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = path.split('.')
        value = d
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def _set_nested_value(self, d: Dict, path: str, value: Any):
        """Set value in nested dictionary using dot notation"""
        keys = path.split('.')
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
    
    def _set_prompt_value(self, prompt: VEO3JsonPrompt, path: str, value: Any):
        """Set value in prompt object"""
        keys = path.split('.')
        obj = prompt
        for key in keys[:-1]:
            obj = getattr(obj, key)
        
        if isinstance(obj, dict):
            obj[keys[-1]] = value
        else:
            setattr(obj, keys[-1], value)
    
    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from AI response"""
        try:
            # Try to find JSON block
            if '{' in text and '}' in text:
                start = text.index('{')
                end = text.rindex('}') + 1
                return text[start:end]
        except:
            pass
        return None
    
    def _save_to_session(self, prompt: VEO3JsonPrompt, formatted_text: str):
        """Save prompt to session"""
        if self.session:
            try:
                # Save JSON structure
                json_path = self.session.get_path('prompts/veo3_collaborative_prompt.json')
                with open(json_path, 'w') as f:
                    json.dump(asdict(prompt), f, indent=2)
                
                # Save formatted text
                text_path = self.session.get_path('prompts/veo3_formatted_prompt.txt')
                with open(text_path, 'w') as f:
                    f.write(formatted_text)
                
                logger.info(f"💾 Saved collaborative prompt to session")
            except Exception as e:
                logger.error(f"Error saving to session: {e}")


# Example usage
async def main():
    """Example of collaborative prompt generation"""
    
    agent = VEO3CollaborativePromptAgent()
    
    prompt, formatted_text = await agent.generate_collaborative_prompt(
        mission="First-person POV of Israeli soldier with PTSD in war-torn Gaza streets",
        style="Waltz with Bashir animation",
        tone="introspective, haunting",
        duration=8.0,
        platform=Platform.YOUTUBE
    )
    
    print("Generated VEO3 Prompt:")
    print(formatted_text)
    
    return prompt, formatted_text


if __name__ == "__main__":
    asyncio.run(main())