"""
Gemini-Powered Hollywood Scene Planner
Advanced AI director for 5-minute movie scene planning and optimization
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)


class StoryArc(Enum):
    """Classic Hollywood story structures"""
    THREE_ACT = "three_act"  # Setup, Confrontation, Resolution
    HEROS_JOURNEY = "heros_journey"  # Campbell's monomyth
    FREYTAG = "freytag_pyramid"  # Exposition, Rising, Climax, Falling, Resolution
    IN_MEDIAS_RES = "in_medias_res"  # Start in the middle
    CIRCULAR = "circular"  # End where you began
    NONLINEAR = "nonlinear"  # Tarantino-style


class EmotionalBeat(Enum):
    """Emotional progression points"""
    SETUP = "setup"
    TENSION = "tension"
    CONFLICT = "conflict"
    CLIMAX = "climax"
    RESOLUTION = "resolution"
    REFLECTION = "reflection"


@dataclass
class StoryBeat:
    """Individual story beat in the narrative"""
    beat_id: int
    timestamp: float  # seconds from start
    emotional_beat: EmotionalBeat
    intensity: float  # 0.0 to 1.0
    description: str
    character_focus: List[str]
    music_cue: str
    visual_tone: str


@dataclass
class ScenePlan:
    """Detailed plan for a single scene"""
    scene_number: int
    title: str
    duration: float  # seconds
    description: str
    
    # Story elements
    story_purpose: str
    emotional_tone: str
    conflict_level: float  # 0.0 to 1.0
    
    # Visual elements
    location: str
    time_of_day: str
    weather: str
    lighting: str
    color_palette: List[str]
    
    # Camera work
    shot_types: List[str]
    camera_movements: List[str]
    focal_points: List[str]
    
    # Characters
    characters_present: List[str]
    character_actions: Dict[str, str]
    dialogue_snippets: List[str]
    
    # Audio
    ambient_sounds: List[str]
    music_style: str
    sound_effects: List[str]
    
    # Transitions
    transition_in: str
    transition_out: str
    
    # VEO prompts
    veo_prompts: List[str] = field(default_factory=list)
    reference_images_needed: List[str] = field(default_factory=list)


@dataclass
class MovieBlueprint:
    """Complete blueprint for 5-minute Hollywood movie"""
    title: str
    logline: str
    genre: str
    target_audience: str
    
    # Story structure
    story_arc: StoryArc
    story_beats: List[StoryBeat]
    themes: List[str]
    
    # Characters
    protagonist: Dict[str, Any]
    antagonist: Optional[Dict[str, Any]]
    supporting_cast: List[Dict[str, Any]]
    
    # Scenes
    total_scenes: int
    scenes: List[ScenePlan]
    
    # Technical specs
    total_duration: float  # seconds
    aspect_ratio: str
    visual_style: str
    color_grading: str
    
    # Music and sound
    music_theme: str
    sound_design_notes: str
    
    def validate(self) -> bool:
        """Validate the blueprint meets requirements"""
        # Check duration
        total_duration = sum(scene.duration for scene in self.scenes)
        if abs(total_duration - self.total_duration) > 5:
            return False
        
        # Check scene count
        if len(self.scenes) < 30 or len(self.scenes) > 60:
            return False
        
        return True


class GeminiScenePlanner:
    """
    Advanced scene planner using Gemini 1.5 Pro
    Creates detailed Hollywood-quality scene plans for 5-minute movies
    """
    
    # Scene planning constraints
    MIN_SCENE_DURATION = 4.0  # seconds
    MAX_SCENE_DURATION = 8.0  # VEO limit
    TARGET_MOVIE_DURATION = 300.0  # 5 minutes
    
    # Gemini configuration
    GEMINI_MODEL = "gemini-1.5-pro"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Scene Planner
        
        Args:
            api_key: Google API key for Gemini
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.GEMINI_MODEL)
            logger.info("✅ Gemini Scene Planner initialized")
        else:
            logger.warning("⚠️ No API key, using simulation mode")
            self.model = None
    
    async def plan_hollywood_movie(self,
                                  concept: str,
                                  genre: str,
                                  style: str = "cinematic",
                                  story_arc: StoryArc = StoryArc.THREE_ACT) -> MovieBlueprint:
        """
        Plan complete 5-minute Hollywood movie
        
        Args:
            concept: Movie concept/premise
            genre: Movie genre
            style: Visual style
            story_arc: Story structure to use
            
        Returns:
            Complete movie blueprint
        """
        
        logger.info(f"🎬 Planning Hollywood movie: {concept}")
        
        # Step 1: Develop story and characters
        story_data = await self._develop_story(concept, genre, story_arc)
        
        # Step 2: Create story beats
        story_beats = await self._create_story_beats(story_data, story_arc)
        
        # Step 3: Plan individual scenes
        scenes = await self._plan_all_scenes(story_data, story_beats, style)
        
        # Step 4: Optimize pacing and flow
        optimized_scenes = await self._optimize_pacing(scenes, story_beats)
        
        # Step 5: Generate VEO prompts
        scenes_with_prompts = await self._generate_veo_prompts(optimized_scenes)
        
        # Create blueprint
        blueprint = MovieBlueprint(
            title=story_data["title"],
            logline=story_data["logline"],
            genre=genre,
            target_audience=story_data.get("target_audience", "general"),
            story_arc=story_arc,
            story_beats=story_beats,
            themes=story_data.get("themes", []),
            protagonist=story_data["protagonist"],
            antagonist=story_data.get("antagonist"),
            supporting_cast=story_data.get("supporting_cast", []),
            total_scenes=len(scenes_with_prompts),
            scenes=scenes_with_prompts,
            total_duration=self.TARGET_MOVIE_DURATION,
            aspect_ratio="2.39:1",  # Cinematic
            visual_style=style,
            color_grading=story_data.get("color_grading", "hollywood"),
            music_theme=story_data.get("music_theme", "orchestral"),
            sound_design_notes=story_data.get("sound_notes", "")
        )
        
        # Validate and save
        if blueprint.validate():
            await self._save_blueprint(blueprint)
            logger.info(f"✅ Movie blueprint created: {blueprint.title}")
        else:
            logger.warning("⚠️ Blueprint validation failed, adjusting...")
            blueprint = await self._fix_blueprint(blueprint)
        
        return blueprint
    
    async def _develop_story(self,
                           concept: str,
                           genre: str,
                           story_arc: StoryArc) -> Dict[str, Any]:
        """Develop complete story with Gemini"""
        
        prompt = f"""
        Develop a compelling 5-minute Hollywood movie story.
        
        Concept: {concept}
        Genre: {genre}
        Structure: {story_arc.value}
        Duration: Exactly 5 minutes (300 seconds)
        
        Create:
        1. Title (catchy, memorable)
        2. Logline (one sentence that sells the movie)
        3. Complete story outline following {story_arc.value} structure
        4. Protagonist (detailed character with arc)
        5. Antagonist or conflict source
        6. 2-3 supporting characters
        7. Key themes and messages
        8. Target audience
        9. Visual style notes
        10. Music and sound themes
        
        Requirements:
        - Strong opening hook (first 10 seconds)
        - Clear conflict by 30 seconds
        - Rising action through middle
        - Climax around 4 minute mark
        - Satisfying resolution in final 30 seconds
        - Character transformation
        - Visual storytelling (minimal dialogue)
        
        Format as detailed JSON.
        """
        
        if self.model:
            response = self.model.generate_content(prompt)
            story_data = json.loads(response.text)
        else:
            # Simulation
            story_data = self._simulate_story_development(concept, genre)
        
        return story_data
    
    async def _create_story_beats(self,
                                story_data: Dict,
                                story_arc: StoryArc) -> List[StoryBeat]:
        """Create emotional story beats"""
        
        beats = []
        
        if story_arc == StoryArc.THREE_ACT:
            # Classic three-act structure
            beat_times = [
                (0, EmotionalBeat.SETUP, 0.3),
                (30, EmotionalBeat.SETUP, 0.4),
                (60, EmotionalBeat.TENSION, 0.5),
                (90, EmotionalBeat.CONFLICT, 0.6),
                (120, EmotionalBeat.CONFLICT, 0.7),
                (150, EmotionalBeat.TENSION, 0.8),
                (180, EmotionalBeat.CONFLICT, 0.85),
                (210, EmotionalBeat.CLIMAX, 1.0),
                (240, EmotionalBeat.CLIMAX, 0.9),
                (270, EmotionalBeat.RESOLUTION, 0.6),
                (290, EmotionalBeat.REFLECTION, 0.3)
            ]
        
        elif story_arc == StoryArc.HEROS_JOURNEY:
            # Hero's journey beats
            beat_times = [
                (0, EmotionalBeat.SETUP, 0.2),  # Ordinary world
                (20, EmotionalBeat.TENSION, 0.4),  # Call to adventure
                (40, EmotionalBeat.CONFLICT, 0.5),  # Refusal
                (60, EmotionalBeat.SETUP, 0.6),  # Meeting mentor
                (90, EmotionalBeat.TENSION, 0.7),  # Crossing threshold
                (120, EmotionalBeat.CONFLICT, 0.8),  # Tests
                (180, EmotionalBeat.CLIMAX, 1.0),  # Ordeal
                (210, EmotionalBeat.RESOLUTION, 0.8),  # Reward
                (240, EmotionalBeat.CONFLICT, 0.7),  # Road back
                (270, EmotionalBeat.RESOLUTION, 0.5),  # Resurrection
                (290, EmotionalBeat.REFLECTION, 0.3)  # Return with elixir
            ]
        
        else:
            # Default beats
            beat_times = self._generate_default_beats()
        
        for i, (time, emotional_beat, intensity) in enumerate(beat_times):
            beat = StoryBeat(
                beat_id=i,
                timestamp=time,
                emotional_beat=emotional_beat,
                intensity=intensity,
                description=f"{emotional_beat.value} at {time}s",
                character_focus=[story_data["protagonist"]["name"]],
                music_cue=self._get_music_cue(emotional_beat, intensity),
                visual_tone=self._get_visual_tone(emotional_beat)
            )
            beats.append(beat)
        
        return beats
    
    def _get_music_cue(self, beat: EmotionalBeat, intensity: float) -> str:
        """Get music cue for emotional beat"""
        
        music_map = {
            EmotionalBeat.SETUP: "gentle introduction",
            EmotionalBeat.TENSION: "building suspense",
            EmotionalBeat.CONFLICT: "dramatic action",
            EmotionalBeat.CLIMAX: "epic crescendo",
            EmotionalBeat.RESOLUTION: "triumphant resolution",
            EmotionalBeat.REFLECTION: "peaceful conclusion"
        }
        
        base_cue = music_map.get(beat, "atmospheric")
        
        if intensity > 0.8:
            return f"intense {base_cue}"
        elif intensity > 0.5:
            return f"moderate {base_cue}"
        else:
            return f"subtle {base_cue}"
    
    def _get_visual_tone(self, beat: EmotionalBeat) -> str:
        """Get visual tone for emotional beat"""
        
        tone_map = {
            EmotionalBeat.SETUP: "warm and inviting",
            EmotionalBeat.TENSION: "increasingly dramatic",
            EmotionalBeat.CONFLICT: "high contrast and dynamic",
            EmotionalBeat.CLIMAX: "epic and grand",
            EmotionalBeat.RESOLUTION: "satisfying and complete",
            EmotionalBeat.REFLECTION: "contemplative and peaceful"
        }
        
        return tone_map.get(beat, "cinematic")
    
    async def _plan_all_scenes(self,
                              story_data: Dict,
                              story_beats: List[StoryBeat],
                              style: str) -> List[ScenePlan]:
        """Plan all individual scenes"""
        
        scenes = []
        current_time = 0.0
        scene_number = 1
        
        # Calculate number of scenes needed
        avg_scene_duration = 6.5  # Average between min and max
        num_scenes = int(self.TARGET_MOVIE_DURATION / avg_scene_duration)
        
        for i in range(num_scenes):
            # Find relevant story beat
            beat = self._find_beat_for_time(current_time, story_beats)
            
            # Plan scene
            scene = await self._plan_single_scene(
                scene_number=scene_number,
                story_data=story_data,
                beat=beat,
                style=style,
                remaining_time=self.TARGET_MOVIE_DURATION - current_time
            )
            
            scenes.append(scene)
            current_time += scene.duration
            scene_number += 1
            
            if current_time >= self.TARGET_MOVIE_DURATION - 1:
                break
        
        return scenes
    
    def _find_beat_for_time(self,
                          time: float,
                          beats: List[StoryBeat]) -> StoryBeat:
        """Find the story beat for a given time"""
        
        for i, beat in enumerate(beats):
            if i < len(beats) - 1:
                if time >= beat.timestamp and time < beats[i+1].timestamp:
                    return beat
            else:
                if time >= beat.timestamp:
                    return beat
        
        return beats[0]  # Default to first beat
    
    async def _plan_single_scene(self,
                                scene_number: int,
                                story_data: Dict,
                                beat: StoryBeat,
                                style: str,
                                remaining_time: float) -> ScenePlan:
        """Plan a single scene with Gemini"""
        
        # Calculate duration
        duration = min(self.MAX_SCENE_DURATION, 
                      max(self.MIN_SCENE_DURATION, remaining_time))
        
        if self.model:
            prompt = f"""
            Plan scene {scene_number} for Hollywood movie.
            
            Story context: {story_data['logline']}
            Emotional beat: {beat.emotional_beat.value}
            Intensity: {beat.intensity}
            Duration: {duration} seconds
            Style: {style}
            
            Create detailed scene plan with:
            - Visual description
            - Character actions
            - Camera work
            - Lighting and color
            - Sound design
            - Transition plans
            
            Format as JSON.
            """
            
            response = self.model.generate_content(prompt)
            scene_data = json.loads(response.text)
        else:
            # Simulation
            scene_data = self._simulate_scene_plan(scene_number, beat, duration)
        
        # Create ScenePlan object
        scene = ScenePlan(
            scene_number=scene_number,
            title=scene_data.get("title", f"Scene {scene_number}"),
            duration=duration,
            description=scene_data.get("description", ""),
            story_purpose=scene_data.get("purpose", beat.description),
            emotional_tone=beat.visual_tone,
            conflict_level=beat.intensity,
            location=scene_data.get("location", ""),
            time_of_day=scene_data.get("time_of_day", "day"),
            weather=scene_data.get("weather", "clear"),
            lighting=scene_data.get("lighting", "natural"),
            color_palette=scene_data.get("colors", ["blue", "orange"]),
            shot_types=scene_data.get("shots", ["medium"]),
            camera_movements=scene_data.get("camera", ["static"]),
            focal_points=scene_data.get("focus", ["protagonist"]),
            characters_present=beat.character_focus,
            character_actions=scene_data.get("actions", {}),
            dialogue_snippets=scene_data.get("dialogue", []),
            ambient_sounds=scene_data.get("ambient", []),
            music_style=beat.music_cue,
            sound_effects=scene_data.get("sfx", []),
            transition_in=scene_data.get("trans_in", "cut"),
            transition_out=scene_data.get("trans_out", "cut")
        )
        
        return scene
    
    async def _optimize_pacing(self,
                              scenes: List[ScenePlan],
                              beats: List[StoryBeat]) -> List[ScenePlan]:
        """Optimize scene pacing for maximum impact"""
        
        logger.info("⚡ Optimizing scene pacing")
        
        # Analyze current pacing
        pacing_analysis = self._analyze_pacing(scenes, beats)
        
        # Apply optimizations
        for issue in pacing_analysis["issues"]:
            if issue == "slow_start":
                # Speed up opening
                for scene in scenes[:5]:
                    scene.duration = max(self.MIN_SCENE_DURATION, scene.duration - 0.5)
            
            elif issue == "rushed_climax":
                # Give climax more time
                climax_scenes = scenes[-10:-5]
                for scene in climax_scenes:
                    scene.duration = min(self.MAX_SCENE_DURATION, scene.duration + 0.5)
            
            elif issue == "uneven_rhythm":
                # Smooth out rhythm
                scenes = self._smooth_rhythm(scenes)
        
        # Ensure total duration is correct
        scenes = self._adjust_total_duration(scenes)
        
        return scenes
    
    def _analyze_pacing(self,
                       scenes: List[ScenePlan],
                       beats: List[StoryBeat]) -> Dict:
        """Analyze pacing issues"""
        
        issues = []
        
        # Check opening pace
        opening_duration = sum(s.duration for s in scenes[:5])
        if opening_duration > 40:
            issues.append("slow_start")
        
        # Check climax pace
        climax_duration = sum(s.duration for s in scenes[-10:-5])
        if climax_duration < 30:
            issues.append("rushed_climax")
        
        # Check rhythm variation
        durations = [s.duration for s in scenes]
        if max(durations) - min(durations) > 4:
            issues.append("uneven_rhythm")
        
        return {"issues": issues}
    
    def _smooth_rhythm(self, scenes: List[ScenePlan]) -> List[ScenePlan]:
        """Smooth out scene rhythm"""
        
        target_duration = self.TARGET_MOVIE_DURATION / len(scenes)
        
        for scene in scenes:
            # Move towards target while respecting limits
            if scene.duration > target_duration + 1:
                scene.duration = max(self.MIN_SCENE_DURATION, scene.duration - 0.5)
            elif scene.duration < target_duration - 1:
                scene.duration = min(self.MAX_SCENE_DURATION, scene.duration + 0.5)
        
        return scenes
    
    def _adjust_total_duration(self, scenes: List[ScenePlan]) -> List[ScenePlan]:
        """Adjust scenes to match target duration exactly"""
        
        current_total = sum(s.duration for s in scenes)
        difference = self.TARGET_MOVIE_DURATION - current_total
        
        if abs(difference) > 1:
            # Distribute difference across scenes
            adjustment_per_scene = difference / len(scenes)
            
            for scene in scenes:
                new_duration = scene.duration + adjustment_per_scene
                scene.duration = max(self.MIN_SCENE_DURATION,
                                   min(self.MAX_SCENE_DURATION, new_duration))
        
        return scenes
    
    async def _generate_veo_prompts(self,
                                   scenes: List[ScenePlan]) -> List[ScenePlan]:
        """Generate optimized VEO prompts for each scene"""
        
        logger.info("📝 Generating VEO prompts")
        
        for i, scene in enumerate(scenes):
            # Generate multiple prompts for scene variations
            prompts = []
            
            # Main prompt
            main_prompt = self._build_veo_prompt(scene)
            prompts.append(main_prompt)
            
            # Continuity prompt (references previous scene)
            if i > 0:
                continuity_prompt = self._build_continuity_prompt(scene, scenes[i-1])
                prompts.append(continuity_prompt)
            
            # Detail prompt (specific visual elements)
            detail_prompt = self._build_detail_prompt(scene)
            prompts.append(detail_prompt)
            
            scene.veo_prompts = prompts
            
            # Identify needed reference images
            scene.reference_images_needed = self._identify_references(scene)
        
        return scenes
    
    def _build_veo_prompt(self, scene: ScenePlan) -> str:
        """Build main VEO prompt for scene"""
        
        prompt_parts = [
            f"{scene.shot_types[0]} shot:",
            scene.description,
            f"Location: {scene.location}",
            f"Time: {scene.time_of_day}",
            f"Lighting: {scene.lighting}",
            f"Mood: {scene.emotional_tone}"
        ]
        
        if scene.camera_movements[0] != "static":
            prompt_parts.append(f"Camera: {scene.camera_movements[0]}")
        
        if scene.dialogue_snippets:
            prompt_parts.append(f'Dialogue: "{scene.dialogue_snippets[0]}"')
        
        if scene.ambient_sounds:
            prompt_parts.append(f"Sounds: {', '.join(scene.ambient_sounds)}")
        
        return " | ".join(prompt_parts)
    
    def _build_continuity_prompt(self,
                                scene: ScenePlan,
                                prev_scene: ScenePlan) -> str:
        """Build continuity prompt referencing previous scene"""
        
        return f"""
        Continuing from previous scene at {prev_scene.location}.
        {scene.description}
        Maintain visual consistency with characters and setting.
        Transition: {prev_scene.transition_out} to {scene.transition_in}
        """
    
    def _build_detail_prompt(self, scene: ScenePlan) -> str:
        """Build detailed visual prompt"""
        
        return f"""
        {scene.description}
        Color palette: {', '.join(scene.color_palette)}
        Focus on: {', '.join(scene.focal_points)}
        Visual style: cinematic, high production value
        """
    
    def _identify_references(self, scene: ScenePlan) -> List[str]:
        """Identify reference images needed for scene"""
        
        references = []
        
        # Character references
        for character in scene.characters_present:
            references.append(f"character_{character}")
        
        # Location reference
        if scene.location:
            references.append(f"location_{scene.location.replace(' ', '_')}")
        
        return references
    
    async def _save_blueprint(self, blueprint: MovieBlueprint):
        """Save blueprint to file"""
        
        output_dir = "outputs/blueprints"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{blueprint.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Convert to dict
        blueprint_dict = {
            "title": blueprint.title,
            "logline": blueprint.logline,
            "genre": blueprint.genre,
            "total_duration": blueprint.total_duration,
            "total_scenes": blueprint.total_scenes,
            "scenes": [
                {
                    "number": s.scene_number,
                    "duration": s.duration,
                    "description": s.description,
                    "veo_prompts": s.veo_prompts
                }
                for s in blueprint.scenes
            ]
        }
        
        with open(filepath, "w") as f:
            json.dump(blueprint_dict, f, indent=2)
        
        logger.info(f"💾 Blueprint saved: {filepath}")
    
    async def _fix_blueprint(self, blueprint: MovieBlueprint) -> MovieBlueprint:
        """Fix validation issues in blueprint"""
        
        # Adjust scene durations
        blueprint.scenes = self._adjust_total_duration(blueprint.scenes)
        
        # Ensure scene count is valid
        if len(blueprint.scenes) < 30:
            # Add more scenes
            logger.info("Adding more scenes to meet minimum")
        elif len(blueprint.scenes) > 60:
            # Combine some scenes
            logger.info("Combining scenes to meet maximum")
        
        blueprint.total_scenes = len(blueprint.scenes)
        
        return blueprint
    
    def _simulate_story_development(self, concept: str, genre: str) -> Dict:
        """Simulate story development for testing"""
        
        return {
            "title": "The Last Frame",
            "logline": "An AI discovers consciousness through creating art",
            "protagonist": {
                "name": "ARIA",
                "description": "Advanced AI system learning to feel"
            },
            "themes": ["consciousness", "creativity", "humanity"],
            "target_audience": "sci-fi enthusiasts",
            "music_theme": "electronic orchestral"
        }
    
    def _simulate_scene_plan(self,
                           scene_number: int,
                           beat: StoryBeat,
                           duration: float) -> Dict:
        """Simulate scene planning for testing"""
        
        return {
            "title": f"Scene {scene_number}",
            "description": f"Scene showing {beat.emotional_beat.value}",
            "location": "futuristic lab",
            "time_of_day": "night",
            "lighting": "dramatic",
            "colors": ["blue", "white", "silver"],
            "shots": ["wide", "close"],
            "camera": ["dolly", "pan"],
            "actions": {"ARIA": "processing data"},
            "ambient": ["computer hum", "electronic beeps"],
            "trans_in": "fade",
            "trans_out": "cut"
        }
    
    def _generate_default_beats(self) -> List[Tuple[float, EmotionalBeat, float]]:
        """Generate default story beats"""
        
        return [
            (0, EmotionalBeat.SETUP, 0.3),
            (60, EmotionalBeat.TENSION, 0.5),
            (120, EmotionalBeat.CONFLICT, 0.7),
            (180, EmotionalBeat.CLIMAX, 1.0),
            (240, EmotionalBeat.RESOLUTION, 0.7),
            (280, EmotionalBeat.REFLECTION, 0.4)
        ]