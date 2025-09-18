"""
Narrative Orchestrator for Multi-Scene Story Generation
Handles complex narratives with multiple characters and scenes
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime

from ..utils.logging_config import get_logger
from ..characters.character_database import get_character_database
from ..characters.character_model import Character
from ..agents.mission_planning_agent import MissionPlanningAgent
from ..core.decision_framework import DecisionFramework
from ..utils.session_context import SessionContext
from ..utils.parallel_processor import ParallelProcessor
from ..workflows.generate_viral_video import generate_viral_video

logger = get_logger(__name__)


class SceneType(Enum):
    """Types of scenes in a narrative"""
    ESTABLISHING = "establishing"      # Sets up the world/context
    CHARACTER_INTRO = "character_intro" # Introduces a character
    CONFLICT = "conflict"              # Shows problem/challenge
    DEVELOPMENT = "development"        # Develops story/character
    CLIMAX = "climax"                 # Peak of narrative tension
    RESOLUTION = "resolution"          # Resolves conflict
    EPILOGUE = "epilogue"             # Final thoughts/future


class NarrativeStructure(Enum):
    """Common narrative structures"""
    THREE_ACT = "three_act"           # Setup, Confrontation, Resolution
    FIVE_ACT = "five_act"             # Exposition, Rising, Climax, Falling, Resolution
    HEROS_JOURNEY = "heros_journey"   # Campbell's monomyth
    PARALLEL = "parallel"             # Multiple parallel stories
    CIRCULAR = "circular"             # Ends where it begins
    EDUCATIONAL = "educational"       # Problem, Examples, Solution
    DOCUMENTARY = "documentary"       # Real events chronologically


@dataclass
class CharacterArc:
    """Tracks a character's journey through the narrative"""
    character_id: str
    character_name: str
    starting_state: str
    ending_state: str
    key_moments: List[int] = field(default_factory=list)  # Scene indices
    emotional_journey: List[str] = field(default_factory=list)
    primary_challenge: str = ""
    resolution: str = ""


@dataclass
class Scene:
    """Individual scene in the narrative"""
    scene_number: int
    duration: float
    scene_type: SceneType
    title: str
    description: str
    characters: List[str]  # Character IDs
    location: str
    mood: str
    key_action: str
    visual_style: str
    transition_from_previous: str = "cut"
    narrative_purpose: str = ""
    generated_video_path: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class Narrative:
    """Complete narrative structure"""
    title: str
    total_duration: float
    structure: NarrativeStructure
    characters: List[CharacterArc]
    scenes: List[Scene]
    theme: str
    style: str
    visual_style: str
    platform: str = "youtube"
    aspect_ratio: str = "16:9"
    target_audience: str = "general"
    educational_goals: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class NarrativeOrchestrator:
    """
    Orchestrates complex multi-scene narratives with multiple characters
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize the narrative orchestrator"""
        self.session_id = session_id or f"narrative_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_context = SessionContext(self.session_id)
        self.character_db = get_character_database()
        self.mission_planner = MissionPlanningAgent()
        self.parallel_processor = ParallelProcessor()
        self.current_narrative: Optional[Narrative] = None
        
        logger.info(f"🎬 Narrative Orchestrator initialized for session: {self.session_id}")
    
    async def create_narrative(
        self,
        mission: str,
        duration: float,
        num_characters: Optional[int] = None,
        character_ids: Optional[List[str]] = None,
        structure: NarrativeStructure = NarrativeStructure.EDUCATIONAL,
        style: str = "cinematic",
        visual_style: str = "realistic",
        platform: str = "youtube",
        **kwargs
    ) -> Narrative:
        """
        Create a complete narrative from a mission description
        
        Args:
            mission: High-level description of the story
            duration: Total duration in seconds
            num_characters: Number of characters (if creating new)
            character_ids: Existing character IDs to use
            structure: Narrative structure to follow
            style: Overall style
            visual_style: Visual treatment
            platform: Target platform
            
        Returns:
            Complete Narrative object with all scenes planned
        """
        logger.info(f"📝 Creating narrative: {mission[:100]}...")
        
        # Step 1: Analyze the mission and extract narrative elements
        narrative_analysis = await self._analyze_narrative_requirements(
            mission, duration, structure
        )
        
        # Step 2: Create or load characters
        characters = await self._prepare_characters(
            narrative_analysis, num_characters, character_ids
        )
        
        # Step 3: Decompose into scenes
        scenes = await self._decompose_into_scenes(
            narrative_analysis, characters, duration, structure
        )
        
        # Step 4: Create character arcs
        character_arcs = await self._create_character_arcs(
            characters, scenes, narrative_analysis
        )
        
        # Step 5: Assemble narrative
        narrative = Narrative(
            title=narrative_analysis.get("title", "Untitled Narrative"),
            total_duration=duration,
            structure=structure,
            characters=character_arcs,
            scenes=scenes,
            theme=narrative_analysis.get("theme", ""),
            style=style,
            visual_style=visual_style,
            platform=platform,
            target_audience=kwargs.get("target_audience", "general"),
            educational_goals=narrative_analysis.get("educational_goals", []),
            metadata={
                "mission": mission,
                "created_at": datetime.now().isoformat(),
                "session_id": self.session_id,
                **kwargs
            }
        )
        
        self.current_narrative = narrative
        
        # Save narrative plan
        self._save_narrative_plan(narrative)
        
        logger.info(f"✅ Created narrative with {len(scenes)} scenes and {len(characters)} characters")
        return narrative
    
    async def _analyze_narrative_requirements(
        self, mission: str, duration: float, structure: NarrativeStructure
    ) -> Dict[str, Any]:
        """Analyze mission to extract narrative requirements"""
        
        # Use AI to analyze the narrative
        prompt = f"""
        Analyze this narrative mission and extract key elements:
        Mission: {mission}
        Duration: {duration} seconds
        Structure: {structure.value}
        
        Extract:
        1. Title (short, descriptive)
        2. Theme (core message)
        3. Key story beats (major plot points)
        4. Character requirements (types, roles)
        5. Emotional arc (journey)
        6. Educational goals (if any)
        7. Suggested number of scenes
        
        Return as JSON.
        """
        
        # TODO: Call AI service for analysis
        # For now, use heuristic analysis
        
        analysis = {
            "title": self._extract_title(mission),
            "theme": self._extract_theme(mission),
            "story_beats": self._extract_story_beats(mission, structure),
            "character_requirements": self._extract_character_requirements(mission),
            "emotional_arc": self._extract_emotional_arc(mission),
            "educational_goals": self._extract_educational_goals(mission),
            "suggested_scenes": self._calculate_scene_count(duration)
        }
        
        logger.info(f"📊 Narrative analysis complete: {analysis['suggested_scenes']} scenes suggested")
        return analysis
    
    def _extract_title(self, mission: str) -> str:
        """Extract or generate title from mission"""
        # Simple extraction - could use AI
        if ":" in mission:
            return mission.split(":")[0].strip()
        return mission[:50].strip() + "..."
    
    def _extract_theme(self, mission: str) -> str:
        """Extract theme from mission"""
        keywords = ["education", "awareness", "journey", "story", "experience"]
        for keyword in keywords:
            if keyword in mission.lower():
                return keyword.capitalize()
        return "Human Experience"
    
    def _extract_story_beats(self, mission: str, structure: NarrativeStructure) -> List[str]:
        """Extract major story beats based on structure"""
        if structure == NarrativeStructure.THREE_ACT:
            return ["Setup", "Confrontation", "Resolution"]
        elif structure == NarrativeStructure.EDUCATIONAL:
            return ["Problem Introduction", "Examples/Cases", "Analysis", "Solution/Hope"]
        elif structure == NarrativeStructure.PARALLEL:
            return ["Individual Struggles", "Convergence", "Shared Resolution"]
        else:
            return ["Beginning", "Middle", "End"]
    
    def _extract_character_requirements(self, mission: str) -> Dict[str, Any]:
        """Extract character requirements from mission"""
        # Look for character descriptions
        requirements = {
            "count": 1,
            "types": [],
            "relationships": []
        }
        
        # Check for multiple characters
        if "four" in mission.lower() or "4" in mission:
            requirements["count"] = 4
        elif "three" in mission.lower() or "3" in mission:
            requirements["count"] = 3
        elif "two" in mission.lower() or "2" in mission:
            requirements["count"] = 2
        
        # Check for character types
        if "soldier" in mission.lower():
            requirements["types"].append("soldier")
        if "veteran" in mission.lower():
            requirements["types"].append("veteran")
        if "doctor" in mission.lower() or "medic" in mission.lower():
            requirements["types"].append("medical")
            
        return requirements
    
    def _extract_emotional_arc(self, mission: str) -> List[str]:
        """Extract emotional journey from mission"""
        if "ptsd" in mission.lower():
            return ["trauma", "struggle", "recognition", "hope"]
        elif "journey" in mission.lower():
            return ["beginning", "challenge", "growth", "transformation"]
        else:
            return ["introduction", "development", "climax", "resolution"]
    
    def _extract_educational_goals(self, mission: str) -> List[str]:
        """Extract educational goals if present"""
        goals = []
        
        if "ptsd" in mission.lower():
            goals.append("PTSD symptom awareness")
            goals.append("Mental health understanding")
        if "education" in mission.lower() or "teach" in mission.lower():
            goals.append("Educational content")
        if "awareness" in mission.lower():
            goals.append("Raising awareness")
            
        return goals
    
    def _calculate_scene_count(self, duration: float) -> int:
        """Calculate optimal number of scenes based on duration"""
        # Rough heuristic: 10-20 seconds per scene
        if duration <= 30:
            return max(2, int(duration / 10))
        elif duration <= 60:
            return max(3, int(duration / 15))
        elif duration <= 120:
            return max(4, int(duration / 15))
        else:
            return max(6, int(duration / 20))
    
    async def _prepare_characters(
        self,
        narrative_analysis: Dict[str, Any],
        num_characters: Optional[int],
        character_ids: Optional[List[str]]
    ) -> List[Character]:
        """Prepare characters for the narrative"""
        characters = []
        
        if character_ids:
            # Load existing characters
            for char_id in character_ids:
                char = self.character_db.get_character(char_id)
                if char:
                    characters.append(char)
                    logger.info(f"✅ Loaded character: {char.display_name}")
                else:
                    logger.warning(f"⚠️ Character not found: {char_id}")
        
        elif num_characters:
            # Create new characters based on requirements
            char_requirements = narrative_analysis.get("character_requirements", {})
            char_types = char_requirements.get("types", [])
            
            for i in range(num_characters):
                # Generate character based on type
                char_type = char_types[i] if i < len(char_types) else "generic"
                character = await self._generate_character(char_type, i)
                characters.append(character)
                logger.info(f"✅ Generated character: {character.display_name}")
        
        else:
            # Create single protagonist
            character = await self._generate_character("protagonist", 0)
            characters.append(character)
            
        return characters
    
    async def _generate_character(self, char_type: str, index: int) -> Character:
        """Generate a new character based on type"""
        # This would normally use AI to generate unique character
        # For now, create a basic character
        
        character = Character(
            name=f"character_{char_type}_{index}",
            display_name=f"Character {index + 1}",
            age=30 + (index * 5),
            profession=char_type.capitalize(),
            personality="Complex",
            visual_description=f"Person {index + 1}, appropriate for {char_type} role",
            voice_style="Natural",
            speaking_style="Conversational",
            tags=[char_type, "generated"],
            expertise_areas=[char_type],
            catchphrases=[],
            energy_level="medium",
            language_preferences=["English"],
            voice_provider="google",
            voice_id=f"en-US-Neural2-{chr(ord('A') + index)}"
        )
        
        # Save to database
        self.character_db.create_character(character)
        return character
    
    async def _decompose_into_scenes(
        self,
        narrative_analysis: Dict[str, Any],
        characters: List[Character],
        duration: float,
        structure: NarrativeStructure
    ) -> List[Scene]:
        """Decompose narrative into individual scenes"""
        
        scene_count = narrative_analysis.get("suggested_scenes", 8)
        scene_duration = duration / scene_count
        story_beats = narrative_analysis.get("story_beats", [])
        
        scenes = []
        
        if structure == NarrativeStructure.EDUCATIONAL and len(characters) > 1:
            # Special handling for educational multi-character narratives
            scenes = self._create_educational_scenes(
                characters, scene_count, scene_duration, narrative_analysis
            )
        elif structure == NarrativeStructure.PARALLEL:
            # Parallel narratives
            scenes = self._create_parallel_scenes(
                characters, scene_count, scene_duration, narrative_analysis
            )
        else:
            # Standard narrative structure
            scenes = self._create_standard_scenes(
                characters, scene_count, scene_duration, story_beats
            )
        
        logger.info(f"📑 Created {len(scenes)} scenes")
        return scenes
    
    def _create_educational_scenes(
        self,
        characters: List[Character],
        scene_count: int,
        scene_duration: float,
        narrative_analysis: Dict[str, Any]
    ) -> List[Scene]:
        """Create scenes for educational narrative"""
        scenes = []
        
        # Example for PTSD education film structure
        if "ptsd" in str(narrative_analysis).lower():
            # Scene 1: Establishing trauma event
            scenes.append(Scene(
                scene_number=1,
                duration=scene_duration,
                scene_type=SceneType.ESTABLISHING,
                title="The Day",
                description="Initial trauma event with all characters",
                characters=[c.name for c in characters],
                location="Conflict zone",
                mood="tense",
                key_action="Combat situation",
                visual_style="Documentary realism",
                narrative_purpose="Establish shared trauma"
            ))
            
            # Individual character scenes
            for i, char in enumerate(characters):
                if i < scene_count - 2:  # Leave room for convergence and resolution
                    scenes.append(Scene(
                        scene_number=i + 2,
                        duration=scene_duration,
                        scene_type=SceneType.DEVELOPMENT,
                        title=f"{char.display_name}'s Struggle",
                        description=f"Individual PTSD symptoms of {char.display_name}",
                        characters=[char.name],
                        location="Civilian life",
                        mood="anxious",
                        key_action="PTSD symptom manifestation",
                        visual_style="Psychological realism",
                        narrative_purpose=f"Show {char.display_name}'s specific symptoms"
                    ))
            
            # Convergence scene
            scenes.append(Scene(
                scene_number=len(scenes) + 1,
                duration=scene_duration,
                scene_type=SceneType.CLIMAX,
                title="Recognition",
                description="Characters recognize shared struggle",
                characters=[c.name for c in characters],
                location="Therapy center entrance",
                mood="understanding",
                key_action="Silent acknowledgment",
                visual_style="Hopeful realism",
                narrative_purpose="Show they're not alone"
            ))
            
            # Resolution scene
            scenes.append(Scene(
                scene_number=len(scenes) + 1,
                duration=scene_duration,
                scene_type=SceneType.RESOLUTION,
                title="First Steps",
                description="Group therapy beginning",
                characters=[c.name for c in characters],
                location="Therapy room",
                mood="hopeful",
                key_action="Seeking help together",
                visual_style="Warm, supportive",
                narrative_purpose="Show path to healing"
            ))
        else:
            # Generic educational structure
            for i in range(scene_count):
                scene_type = self._determine_scene_type(i, scene_count)
                scenes.append(Scene(
                    scene_number=i + 1,
                    duration=scene_duration,
                    scene_type=scene_type,
                    title=f"Scene {i + 1}",
                    description=f"Educational content part {i + 1}",
                    characters=[c.name for c in characters[:max(1, len(characters) // (i + 1))]],
                    location="Educational setting",
                    mood="informative",
                    key_action="Teaching moment",
                    visual_style="Clear and engaging",
                    narrative_purpose=f"Educational beat {i + 1}"
                ))
        
        return scenes
    
    def _create_parallel_scenes(
        self,
        characters: List[Character],
        scene_count: int,
        scene_duration: float,
        narrative_analysis: Dict[str, Any]
    ) -> List[Scene]:
        """Create scenes for parallel narratives"""
        scenes = []
        
        # Divide scenes among characters
        scenes_per_character = scene_count // len(characters)
        
        for char_idx, character in enumerate(characters):
            for scene_idx in range(scenes_per_character):
                overall_scene_num = char_idx * scenes_per_character + scene_idx + 1
                scene_type = self._determine_scene_type(scene_idx, scenes_per_character)
                
                scenes.append(Scene(
                    scene_number=overall_scene_num,
                    duration=scene_duration,
                    scene_type=scene_type,
                    title=f"{character.display_name} - Part {scene_idx + 1}",
                    description=f"{character.display_name}'s journey segment",
                    characters=[character.name],
                    location=f"Location {scene_idx + 1}",
                    mood=self._determine_mood(scene_type),
                    key_action=f"Character development",
                    visual_style="Character-focused",
                    narrative_purpose=f"Develop {character.display_name}'s story"
                ))
        
        # Add convergence scene if room
        if scene_count > len(scenes):
            scenes.append(Scene(
                scene_number=len(scenes) + 1,
                duration=scene_duration,
                scene_type=SceneType.RESOLUTION,
                title="Convergence",
                description="All stories converge",
                characters=[c.name for c in characters],
                location="Shared space",
                mood="unified",
                key_action="Stories intersect",
                visual_style="Ensemble",
                narrative_purpose="Unite parallel narratives"
            ))
        
        return scenes
    
    def _create_standard_scenes(
        self,
        characters: List[Character],
        scene_count: int,
        scene_duration: float,
        story_beats: List[str]
    ) -> List[Scene]:
        """Create scenes for standard narrative structure"""
        scenes = []
        
        for i in range(scene_count):
            scene_type = self._determine_scene_type(i, scene_count)
            beat_index = min(i * len(story_beats) // scene_count, len(story_beats) - 1)
            
            scenes.append(Scene(
                scene_number=i + 1,
                duration=scene_duration,
                scene_type=scene_type,
                title=f"Scene {i + 1}: {story_beats[beat_index] if story_beats else 'Development'}",
                description=f"Narrative development - {scene_type.value}",
                characters=[c.name for c in characters[:max(1, (i % len(characters)) + 1)]],
                location=f"Setting {i + 1}",
                mood=self._determine_mood(scene_type),
                key_action=story_beats[beat_index] if story_beats else "Story progression",
                visual_style="Cinematic",
                narrative_purpose=scene_type.value
            ))
        
        return scenes
    
    def _determine_scene_type(self, index: int, total: int) -> SceneType:
        """Determine scene type based on position in narrative"""
        position = index / max(1, total - 1)
        
        if index == 0:
            return SceneType.ESTABLISHING
        elif position < 0.2:
            return SceneType.CHARACTER_INTRO
        elif position < 0.4:
            return SceneType.DEVELOPMENT
        elif position < 0.6:
            return SceneType.CONFLICT
        elif position < 0.8:
            return SceneType.CLIMAX
        elif index == total - 1:
            return SceneType.EPILOGUE
        else:
            return SceneType.RESOLUTION
    
    def _determine_mood(self, scene_type: SceneType) -> str:
        """Determine mood based on scene type"""
        mood_map = {
            SceneType.ESTABLISHING: "neutral",
            SceneType.CHARACTER_INTRO: "curious",
            SceneType.DEVELOPMENT: "building",
            SceneType.CONFLICT: "tense",
            SceneType.CLIMAX: "intense",
            SceneType.RESOLUTION: "relieved",
            SceneType.EPILOGUE: "reflective"
        }
        return mood_map.get(scene_type, "neutral")
    
    async def _create_character_arcs(
        self,
        characters: List[Character],
        scenes: List[Scene],
        narrative_analysis: Dict[str, Any]
    ) -> List[CharacterArc]:
        """Create character arcs tracking their journey"""
        arcs = []
        
        for character in characters:
            # Find scenes where character appears
            character_scenes = [
                i for i, scene in enumerate(scenes)
                if character.name in scene.characters
            ]
            
            # Determine emotional journey
            emotional_journey = []
            if character_scenes:
                for scene_idx in character_scenes:
                    scene = scenes[scene_idx]
                    emotional_journey.append(scene.mood)
            
            arc = CharacterArc(
                character_id=character.name,
                character_name=character.display_name,
                starting_state=self._determine_character_state(character, "start"),
                ending_state=self._determine_character_state(character, "end"),
                key_moments=character_scenes,
                emotional_journey=emotional_journey,
                primary_challenge=self._extract_character_challenge(character),
                resolution=self._determine_character_resolution(character)
            )
            
            arcs.append(arc)
            logger.info(f"📈 Created arc for {character.display_name}: {len(character_scenes)} scenes")
        
        return arcs
    
    def _determine_character_state(self, character: Character, phase: str) -> str:
        """Determine character's emotional/mental state"""
        if "ptsd" in character.tags:
            if phase == "start":
                return "traumatized"
            else:
                return "seeking help"
        elif "veteran" in character.profession.lower():
            if phase == "start":
                return "struggling"
            else:
                return "finding hope"
        else:
            if phase == "start":
                return "challenged"
            else:
                return "transformed"
    
    def _extract_character_challenge(self, character: Character) -> str:
        """Extract character's primary challenge"""
        if "hypervigilance" in character.tags:
            return "hypervigilance"
        elif "emotional_numbing" in character.tags:
            return "emotional numbness"
        elif "panic" in character.tags:
            return "panic attacks"
        elif "avoidance" in character.tags:
            return "avoidance behaviors"
        else:
            return "personal struggle"
    
    def _determine_character_resolution(self, character: Character) -> str:
        """Determine character's resolution"""
        return "beginning healing journey"
    
    async def generate_narrative(
        self,
        narrative: Optional[Narrative] = None,
        parallel: bool = True,
        **generation_kwargs
    ) -> Dict[str, Any]:
        """
        Generate all scenes for the narrative
        
        Args:
            narrative: Narrative to generate (uses current if None)
            parallel: Whether to generate scenes in parallel
            **generation_kwargs: Additional arguments for video generation
            
        Returns:
            Dictionary with generation results
        """
        if not narrative:
            narrative = self.current_narrative
            
        if not narrative:
            raise ValueError("No narrative to generate")
        
        logger.info(f"🎬 Generating {len(narrative.scenes)} scenes for: {narrative.title}")
        
        results = {
            "narrative_id": self.session_id,
            "title": narrative.title,
            "scenes": [],
            "success": True,
            "errors": []
        }
        
        if parallel:
            # Generate scenes in parallel
            scene_tasks = []
            for scene in narrative.scenes:
                task = self._generate_scene(scene, narrative, **generation_kwargs)
                scene_tasks.append(task)
            
            scene_results = await asyncio.gather(*scene_tasks, return_exceptions=True)
            
            for i, result in enumerate(scene_results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Scene {i + 1} failed: {result}")
                    results["errors"].append(f"Scene {i + 1}: {str(result)}")
                    results["success"] = False
                else:
                    results["scenes"].append(result)
                    narrative.scenes[i].generated_video_path = result.get("video_path")
        else:
            # Generate scenes sequentially
            for scene in narrative.scenes:
                try:
                    result = await self._generate_scene(scene, narrative, **generation_kwargs)
                    results["scenes"].append(result)
                    scene.generated_video_path = result.get("video_path")
                except Exception as e:
                    logger.error(f"❌ Scene {scene.scene_number} failed: {e}")
                    results["errors"].append(f"Scene {scene.scene_number}: {str(e)}")
                    results["success"] = False
        
        # Save generation results
        self._save_generation_results(narrative, results)
        
        # Combine scenes if all successful
        if results["success"] and generation_kwargs.get("auto_combine", True):
            combined_path = await self._combine_scenes(narrative)
            results["final_video"] = combined_path
        
        logger.info(f"✅ Narrative generation complete: {len(results['scenes'])} scenes generated")
        return results
    
    async def _generate_scene(
        self,
        scene: Scene,
        narrative: Narrative,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a single scene"""
        logger.info(f"🎬 Generating scene {scene.scene_number}: {scene.title}")
        
        # Build scene-specific mission
        mission = self._build_scene_mission(scene, narrative)
        
        # Get character references
        character_refs = ",".join(scene.characters) if scene.characters else None
        
        # Set scene-specific session ID
        scene_session_id = f"{self.session_id}_scene{scene.scene_number}"
        scene.session_id = scene_session_id
        
        # Call video generation
        result = await asyncio.to_thread(
            generate_viral_video,
            mission=mission,
            duration=scene.duration,
            platform=narrative.platform,
            style=f"{narrative.style} {scene.visual_style}",
            visual_style=scene.visual_style,
            character_refs=character_refs,
            session_id=scene_session_id,
            **kwargs
        )
        
        return {
            "scene_number": scene.scene_number,
            "title": scene.title,
            "video_path": result.get("video_path"),
            "session_id": scene_session_id,
            "success": result.get("success", False)
        }
    
    def _build_scene_mission(self, scene: Scene, narrative: Narrative) -> str:
        """Build mission description for a specific scene"""
        mission_parts = [
            f"{narrative.style} style:",
            scene.description,
            f"Location: {scene.location}.",
            f"Mood: {scene.mood}.",
            f"Key action: {scene.key_action}."
        ]
        
        if scene.characters:
            char_names = [
                self.character_db.get_character(cid).display_name 
                for cid in scene.characters 
                if self.character_db.get_character(cid)
            ]
            if char_names:
                mission_parts.append(f"Characters: {', '.join(char_names)}.")
        
        if scene.narrative_purpose:
            mission_parts.append(f"Purpose: {scene.narrative_purpose}.")
        
        return " ".join(mission_parts)
    
    async def _combine_scenes(self, narrative: Narrative) -> str:
        """Combine all generated scenes into final video"""
        logger.info("🎬 Combining scenes into final narrative...")
        
        # Get all video paths
        video_paths = []
        for scene in narrative.scenes:
            if scene.generated_video_path:
                video_paths.append(scene.generated_video_path)
            else:
                logger.warning(f"⚠️ Scene {scene.scene_number} missing video")
        
        if not video_paths:
            raise ValueError("No videos to combine")
        
        # Use FFmpeg to concatenate
        output_path = self.session_context.get_path("final_output") / "narrative_complete.mp4"
        
        # Create concat file
        concat_file = self.session_context.get_path("temp") / "concat.txt"
        with open(concat_file, "w") as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")
        
        # Run FFmpeg
        import subprocess
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        logger.info(f"✅ Combined narrative saved to: {output_path}")
        return str(output_path)
    
    def _save_narrative_plan(self, narrative: Narrative):
        """Save narrative plan to session"""
        plan_path = self.session_context.get_path("narrative") / "narrative_plan.json"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        
        plan_data = {
            "title": narrative.title,
            "duration": narrative.total_duration,
            "structure": narrative.structure.value,
            "theme": narrative.theme,
            "style": narrative.style,
            "visual_style": narrative.visual_style,
            "characters": [
                {
                    "id": arc.character_id,
                    "name": arc.character_name,
                    "journey": arc.emotional_journey,
                    "challenge": arc.primary_challenge,
                    "resolution": arc.resolution
                }
                for arc in narrative.characters
            ],
            "scenes": [
                {
                    "number": scene.scene_number,
                    "duration": scene.duration,
                    "type": scene.scene_type.value,
                    "title": scene.title,
                    "description": scene.description,
                    "characters": scene.characters,
                    "location": scene.location,
                    "mood": scene.mood
                }
                for scene in narrative.scenes
            ],
            "metadata": narrative.metadata
        }
        
        with open(plan_path, "w") as f:
            json.dump(plan_data, f, indent=2)
        
        logger.info(f"💾 Saved narrative plan to: {plan_path}")
    
    def _save_generation_results(self, narrative: Narrative, results: Dict[str, Any]):
        """Save generation results"""
        results_path = self.session_context.get_path("narrative") / "generation_results.json"
        
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"💾 Saved generation results to: {results_path}")
    
    def get_narrative_summary(self, narrative: Optional[Narrative] = None) -> str:
        """Get a summary of the narrative"""
        if not narrative:
            narrative = self.current_narrative
            
        if not narrative:
            return "No narrative available"
        
        summary_lines = [
            f"Title: {narrative.title}",
            f"Duration: {narrative.total_duration}s",
            f"Structure: {narrative.structure.value}",
            f"Characters: {len(narrative.characters)}",
            f"Scenes: {len(narrative.scenes)}",
            "",
            "Scene Breakdown:"
        ]
        
        for scene in narrative.scenes:
            char_names = [
                self.character_db.get_character(cid).display_name 
                for cid in scene.characters 
                if self.character_db.get_character(cid)
            ]
            summary_lines.append(
                f"  {scene.scene_number}. {scene.title} ({scene.duration}s) - "
                f"{', '.join(char_names) if char_names else 'No characters'}"
            )
        
        return "\n".join(summary_lines)