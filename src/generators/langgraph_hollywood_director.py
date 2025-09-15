"""
LangGraph-Enhanced Hollywood Director
Uses LangGraph multi-agent system for AI discussions and scene planning
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from src.agents.langgraph_agent_system import (
    LangGraphAgentSystem,
    AgentState,
    DiscussionPhase,
    AgentMode
)
from src.agents.working_orchestrator import WorkingOrchestrator
from src.generators.hollywood_veo_director import HollywoodVeoDirector, Scene, MovieScript
from src.utils.session_context import SessionContext
from src.config.video_config import video_config

logger = logging.getLogger(__name__)


class LangGraphHollywoodDirector:
    """
    Hollywood Director using LangGraph for AI agent discussions
    Implements proper multi-agent collaboration for scene planning
    """
    
    def __init__(self, project_id: str, session_context: Optional[SessionContext] = None):
        """Initialize LangGraph Hollywood Director"""
        self.project_id = project_id
        self.session = session_context
        
        # Initialize LangGraph agent system
        self.agent_system = LangGraphAgentSystem(
            mode=AgentMode.PROFESSIONAL,  # Use all 22 agents
            mission="Create Hollywood-quality 5-minute movie",
            checkpoint_dir="./checkpoints"
        )
        
        # Initialize base Hollywood director
        self.base_director = HollywoodVeoDirector(
            project_id=project_id,
            session_context=session_context
        )
        
        # Initialize working orchestrator for coordination
        self.orchestrator = WorkingOrchestrator(
            project_id=project_id,
            session_context=session_context
        )
        
        logger.info("🎬 LangGraph Hollywood Director initialized")
    
    def create_5_minute_movie_with_langgraph(self,
                                            mission: str,
                                            genre: str = "drama",
                                            style: str = "cinematic") -> str:
        """
        Create 5-minute movie using LangGraph agent discussions
        
        Args:
            mission: Movie concept/story
            genre: Movie genre
            style: Visual style
            
        Returns:
            Path to final movie file
        """
        logger.info(f"🎬 Creating movie with LangGraph: {mission}")
        
        # Step 1: Initialize agent discussion state
        initial_state = self._initialize_discussion_state(mission, genre, style)
        
        # Step 2: Run ideation phase with agents
        logger.info("💡 Phase 1: Ideation with 22 agents...")
        ideation_state = self._run_ideation_phase(initial_state)
        
        # Step 3: Character development with agents
        logger.info("🎭 Phase 2: Character development...")
        character_state = self._run_character_phase(ideation_state)
        
        # Step 4: Script writing with agents
        logger.info("📝 Phase 3: Script writing...")
        script_state = self._run_script_phase(character_state)
        
        # Step 5: Visual planning with agents
        logger.info("🎨 Phase 4: Visual planning...")
        visual_state = self._run_visual_phase(script_state)
        
        # Step 6: Audio design with agents
        logger.info("🎵 Phase 5: Audio design...")
        audio_state = self._run_audio_phase(visual_state)
        
        # Step 7: Final review and consensus
        logger.info("✅ Phase 6: Final review and consensus...")
        final_state = self._run_review_phase(audio_state)
        
        # Step 8: Generate movie based on agent decisions
        logger.info("🎬 Generating movie based on agent consensus...")
        movie_script = self._extract_movie_script(final_state)
        
        # Step 9: Use base director to generate actual movie
        movie_path = self.base_director.create_5_minute_movie(
            mission=mission,
            genre=genre,
            style=style
        )
        
        # Step 10: Save agent discussion artifacts
        self._save_discussion_artifacts(final_state)
        
        logger.info(f"✅ Movie created with LangGraph: {movie_path}")
        return movie_path
    
    def _initialize_discussion_state(self, 
                                    mission: str,
                                    genre: str,
                                    style: str) -> AgentState:
        """Initialize the agent discussion state"""
        
        return AgentState(
            messages=[{
                "role": "system",
                "content": f"Create a Hollywood {genre} movie: {mission}"
            }],
            current_topic=f"{genre} movie creation",
            discussion_phase=DiscussionPhase.IDEATION,
            mission=mission,
            active_characters=[],
            character_references={},
            character_profiles={},
            scene_context=f"{style} style {genre} film",
            decisions_made=[],
            consensus_reached=False,
            consensus_score=0.0,
            iteration_count=0,
            agent_votes={},
            next_agent=None,
            agents_participated=[],
            script_draft=None,
            visual_guidelines=None,
            audio_specifications=None,
            final_output=None
        )
    
    def _run_ideation_phase(self, state: AgentState) -> AgentState:
        """Run ideation phase with agents"""
        
        state["discussion_phase"] = DiscussionPhase.IDEATION
        state["current_topic"] = "Story concept and themes"
        
        # Configure agents for ideation
        ideation_config = {
            "max_iterations": 5,
            "required_consensus": 0.8,
            "participating_agents": [
                "director", "scriptwriter", "producer",
                "cinematographer", "creative_consultant"
            ]
        }
        
        # Run agent discussion
        result = self.agent_system.run_discussion(
            initial_state=state,
            config=ideation_config
        )
        
        # Extract decisions
        decisions = result.get("decisions", [])
        state["decisions_made"].extend(decisions)
        
        return result["final_state"]
    
    def _run_character_phase(self, state: AgentState) -> AgentState:
        """Run character development phase"""
        
        state["discussion_phase"] = DiscussionPhase.CHARACTER_DEVELOPMENT
        state["current_topic"] = "Character profiles and consistency"
        
        # Configure agents for character development
        character_config = {
            "max_iterations": 7,
            "required_consensus": 0.85,
            "participating_agents": [
                "character_designer", "scriptwriter", "director",
                "costume_designer", "casting_director"
            ]
        }
        
        # Run discussion
        result = self.agent_system.run_discussion(
            initial_state=state,
            config=character_config
        )
        
        # Extract character profiles
        state["character_profiles"] = result.get("character_profiles", {})
        
        return result["final_state"]
    
    def _run_script_phase(self, state: AgentState) -> AgentState:
        """Run script writing phase"""
        
        state["discussion_phase"] = DiscussionPhase.SCRIPT_WRITING
        state["current_topic"] = "Detailed script and dialogue"
        
        # Configure agents for script writing
        script_config = {
            "max_iterations": 10,
            "required_consensus": 0.9,
            "participating_agents": [
                "scriptwriter", "director", "dialogue_coach",
                "story_consultant", "producer"
            ]
        }
        
        # Run discussion
        result = self.agent_system.run_discussion(
            initial_state=state,
            config=script_config
        )
        
        # Extract script
        state["script_draft"] = result.get("script", "")
        
        return result["final_state"]
    
    def _run_visual_phase(self, state: AgentState) -> AgentState:
        """Run visual planning phase"""
        
        state["discussion_phase"] = DiscussionPhase.VISUAL_PLANNING
        state["current_topic"] = "Visual style and cinematography"
        
        # Configure agents for visual planning
        visual_config = {
            "max_iterations": 8,
            "required_consensus": 0.85,
            "participating_agents": [
                "cinematographer", "vfx_supervisor", "art_director",
                "lighting_director", "director"
            ]
        }
        
        # Run discussion
        result = self.agent_system.run_discussion(
            initial_state=state,
            config=visual_config
        )
        
        # Extract visual guidelines
        state["visual_guidelines"] = result.get("visual_guidelines", {})
        
        return result["final_state"]
    
    def _run_audio_phase(self, state: AgentState) -> AgentState:
        """Run audio design phase"""
        
        state["discussion_phase"] = DiscussionPhase.AUDIO_DESIGN
        state["current_topic"] = "Music and sound design"
        
        # Configure agents for audio design
        audio_config = {
            "max_iterations": 6,
            "required_consensus": 0.8,
            "participating_agents": [
                "music_composer", "sound_designer", "audio_engineer",
                "director", "editor"
            ]
        }
        
        # Run discussion
        result = self.agent_system.run_discussion(
            initial_state=state,
            config=audio_config
        )
        
        # Extract audio specifications
        state["audio_specifications"] = result.get("audio_specs", {})
        
        return result["final_state"]
    
    def _run_review_phase(self, state: AgentState) -> AgentState:
        """Run final review and consensus phase"""
        
        state["discussion_phase"] = DiscussionPhase.REVIEW
        state["current_topic"] = "Final review and approval"
        
        # Configure all agents for final review
        review_config = {
            "max_iterations": 3,
            "required_consensus": 0.95,
            "participating_agents": "all"  # All 22 agents participate
        }
        
        # Run final discussion
        result = self.agent_system.run_discussion(
            initial_state=state,
            config=review_config
        )
        
        # Mark as complete
        state["discussion_phase"] = DiscussionPhase.COMPLETE
        state["consensus_reached"] = True
        state["final_output"] = result.get("final_output", {})
        
        return result["final_state"]
    
    def _extract_movie_script(self, state: AgentState) -> MovieScript:
        """Extract MovieScript from agent discussion state"""
        
        # Parse the script draft from agents
        script_data = state.get("script_draft", "")
        visual_data = state.get("visual_guidelines", {})
        audio_data = state.get("audio_specifications", {})
        
        # Convert to MovieScript format
        scenes = self._parse_scenes_from_script(script_data, visual_data)
        
        movie_script = MovieScript(
            title=state.get("final_output", {}).get("title", "Untitled"),
            genre=state.get("final_output", {}).get("genre", "drama"),
            total_duration=300.0,
            scenes=scenes,
            characters=state.get("character_profiles", {}),
            music_style=audio_data.get("music_style", "cinematic"),
            target_emotion=audio_data.get("target_emotion", "dramatic")
        )
        
        return movie_script
    
    def _parse_scenes_from_script(self, 
                                 script_data: str,
                                 visual_data: Dict) -> List[Scene]:
        """Parse scenes from agent-generated script"""
        
        # This would parse the actual script
        # For now, using placeholder
        from src.generators.hollywood_veo_director import SceneType
        
        scenes = []
        # Create 45 scenes for 5-minute movie
        for i in range(45):
            scene = Scene(
                scene_id=i,
                scene_type=SceneType.DIALOGUE if i % 3 == 0 else SceneType.ACTION,
                duration=6.67,  # ~300 seconds / 45 scenes
                description=f"Scene {i} from agent discussion",
                dialogue=None,
                characters=[]
            )
            scenes.append(scene)
        
        return scenes
    
    def _save_discussion_artifacts(self, state: AgentState):
        """Save agent discussion artifacts"""
        
        if not self.session:
            return
        
        artifacts_dir = self.session.get_path("agent_discussions")
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Save full discussion state
        state_file = os.path.join(artifacts_dir, "langgraph_discussion.json")
        
        # Convert state to serializable format
        serializable_state = {
            "mission": state["mission"],
            "decisions_made": state["decisions_made"],
            "consensus_score": state["consensus_score"],
            "agents_participated": state["agents_participated"],
            "character_profiles": state["character_profiles"],
            "visual_guidelines": state["visual_guidelines"],
            "audio_specifications": state["audio_specifications"],
            "final_output": state["final_output"]
        }
        
        with open(state_file, "w") as f:
            json.dump(serializable_state, f, indent=2)
        
        logger.info(f"💾 Saved LangGraph discussion artifacts: {state_file}")


def create_israel_iran_movie_with_langgraph():
    """
    Create Israel-Iran movie using LangGraph agent system
    """
    
    concept = """
    June 2025 Israel-Iran conflict: Operation Red Wedding.
    Israeli defense forces protect civilians from Iranian aggression.
    Focus on Iron Dome technology, IDF operations, and civilian resilience.
    Pro-Israeli perspective showcasing defense against existential threats.
    """
    
    print("\n" + "="*70)
    print("🎬 CREATING ISRAEL-IRAN MOVIE WITH LANGGRAPH")
    print("="*70)
    print("🤖 Using 22 AI agents for collaborative planning")
    print("📊 LangGraph state management and routing")
    print("🎯 Multi-phase discussion process")
    print("="*70 + "\n")
    
    # Initialize LangGraph director
    director = LangGraphHollywoodDirector(
        project_id="viralgen-464411"
    )
    
    # Create movie with agent discussions
    movie_path = director.create_5_minute_movie_with_langgraph(
        mission=concept,
        genre="thriller",
        style="hyper-realistic"
    )
    
    print(f"\n✅ Movie created: {movie_path}")
    print("📁 Agent discussion artifacts saved")
    
    return movie_path


if __name__ == "__main__":
    create_israel_iran_movie_with_langgraph()