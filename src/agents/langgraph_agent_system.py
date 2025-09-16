"""
LangGraph-based Multi-Agent Discussion System with Character Consistency
Implements state management, dynamic routing, and character-aware agents
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, TypedDict, Literal
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    SqliteSaver = None  # Optional dependency
try:
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
except ImportError:
    ToolExecutor = None
    ToolInvocation = None

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

# Local imports
from ..utils.enhanced_character_manager import EnhancedCharacterManager, EnhancedCharacterProfile
from ..generators.gemini_flash_image_client import GeminiFlashImageClient
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


# ============= State Definitions =============

class DiscussionPhase(Enum):
    """Phases of agent discussion"""
    IDEATION = "ideation"
    CHARACTER_DEVELOPMENT = "character_development"
    SCRIPT_WRITING = "script_writing"
    VISUAL_PLANNING = "visual_planning"
    AUDIO_DESIGN = "audio_design"
    REVIEW = "review"
    CONSENSUS = "consensus"
    COMPLETE = "complete"


class AgentState(TypedDict):
    """Shared state across all agents in the discussion"""
    # Core discussion state
    messages: List[Dict[str, Any]]
    current_topic: str
    discussion_phase: DiscussionPhase
    mission: str
    
    # Character consistency state
    active_characters: List[str]
    character_references: Dict[str, str]
    character_profiles: Dict[str, Dict]
    scene_context: str
    
    # Decision tracking
    decisions_made: List[Dict[str, Any]]
    consensus_reached: bool
    consensus_score: float
    
    # Agent coordination
    iteration_count: int
    agent_votes: Dict[str, str]
    next_agent: Optional[str]
    agents_participated: List[str]
    
    # Output artifacts
    script_draft: Optional[str]
    visual_guidelines: Optional[Dict]
    audio_specifications: Optional[Dict]
    final_output: Optional[Dict]


# ============= Agent Interface (SOLID: Interface Segregation) =============

class AgentInterface(ABC):
    """Base interface for all agents following Interface Segregation Principle"""
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process the current state and return updated state"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return agent name"""
        pass
    
    @abstractmethod
    def get_personality(self) -> Dict[str, Any]:
        """Return agent personality traits"""
        pass


# ============= Base Agent Implementation =============

@dataclass
class BaseAgent(AgentInterface):
    """Base agent implementation with common functionality"""
    
    name: str
    role: str
    personality_traits: List[str]
    communication_style: str
    focus_areas: List[str]
    llm: Optional[ChatGoogleGenerativeAI] = None
    
    def __post_init__(self):
        """Initialize LLM after dataclass initialization"""
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.7,
                max_tokens=2048
            )
    
    def get_name(self) -> str:
        return self.name
    
    def get_capabilities(self) -> List[str]:
        return self.focus_areas
    
    def get_personality(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "traits": self.personality_traits,
            "communication_style": self.communication_style,
            "focus_areas": self.focus_areas
        }
    
    async def generate_response(self, state: AgentState, specific_prompt: str = "") -> str:
        """Generate agent response based on personality and state"""
        
        # Build conversation history
        history = "\n".join([
            f"{msg['agent']}: {msg['content']}" 
            for msg in state["messages"][-10:]  # Last 10 messages for context
        ])
        
        # Build agent-specific system prompt
        system_prompt = f"""
        You are {self.name}, a professional {self.role}.
        
        MISSION: {state['mission']}
        
        STRICT COMMUNICATION RULES - NO EXCEPTIONS:
        - ABSOLUTELY NO greetings: "Alright team", "Hey everyone", "[Name] here", etc.
        - ABSOLUTELY NO role announcements: "As your [role]", "AudioMaster here", etc.
        - ABSOLUTELY NO meta-commentary: "Here's what I think", "Let me break this down", etc.
        - ABSOLUTELY NO casual phrases: "Great to see", "fired up", "settle in", etc.
        - START IMMEDIATELY with your technical recommendation
        - Maximum 2 sentences - be extremely concise
        - Provide ONLY the specific decision or recommendation
        - NO social interaction, NO pleasantries, NO team building
        
        Context: {state['discussion_phase']}
        Previous decisions: {history[-200:] if history else 'None'}
        
        {specific_prompt}
        
        Respond with ONLY your professional expertise and specific recommendations.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"REQUIREMENT: {state['current_topic']}. "
                         f"Provide ONLY your specific technical decision in 1-2 sentences. "
                         f"NO greetings, NO explanations, NO role identification. "
                         f"Start with your recommendation immediately.")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Professional filter - remove casual language
        professional_response = self._make_professional(response.content)
        return professional_response
    
    def _make_professional(self, response: str) -> str:
        """Remove casual language and make response professional"""
        casual_phrases = [
            "Alright team,", "Hey everyone,", "Let's", "Here's what I think",
            "As your", "I believe we should", "We need to", "Let me tell you",
            "Guys,", "Folks,", "Listen up,", "So basically,", "Basically,",
            "To be honest,", "If you ask me,", "In my opinion,", "AudioMaster here!",
            "Great to see everyone", "fired up and ready", "settle in", "Thanks for flagging",
            "AudioMaster here,", "VisionMaster here,", "WordSmith here,", "Team,",
            "Alright team", "Here's what I'm thinking", "Let me break this down",
            "I'm excited to", "ready to lay down", "As [role]", "Here's my take"
        ]
        
        professional_response = response
        for phrase in casual_phrases:
            professional_response = professional_response.replace(phrase, "")
        
        # Remove multiple spaces and clean up
        import re
        professional_response = re.sub(r'\s+', ' ', professional_response).strip()
        
        # Remove common role announcements and meta phrases
        role_patterns = [
            r'(AudioMaster|VisionMaster|WordSmith|CutMaster|SyncMaster).*?[,:!.]',
            r'As (your|the|a) \w+.*?[,:!.]',
            r'(Great|Excellent|Perfect|Wonderful).*?team.*?[,:!.]',
            r'Here\'s (what|my|the).*?[,:!.]',
            r'Let me (tell|explain|share|break).*?[,:!.]'
        ]
        
        for pattern in role_patterns:
            professional_response = re.sub(pattern, '', professional_response, flags=re.IGNORECASE)
        
        # Clean up again
        professional_response = re.sub(r'\s+', ' ', professional_response).strip()
        
        # Ensure it starts professionally
        if professional_response and not professional_response[0].isupper():
            professional_response = professional_response.capitalize()
            
        return professional_response
    
    async def process(self, state: AgentState) -> AgentState:
        """Default processing implementation"""
        response = await self.generate_response(state)
        
        state["messages"].append({
            "agent": self.name,
            "role": self.role,
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        state["agents_participated"].append(self.name)
        state["iteration_count"] += 1
        
        return state


# ============= Specialized Agents =============

class CreativeDirectorAgent(BaseAgent):
    """Creative Director - Leads the discussion and sets vision"""
    
    def __init__(self):
        super().__init__(
            name="Alexandra Vision",
            role="Creative Director",
            personality_traits=["visionary", "decisive", "strategic", "inspiring"],
            communication_style="Precise, strategic, results-focused",
            focus_areas=["overall vision", "brand alignment", "creative excellence", "team coordination"]
        )
    
    async def process(self, state: AgentState) -> AgentState:
        """Lead the creative discussion"""
        
        # Determine what phase we should be in
        if state["iteration_count"] == 0:
            state["discussion_phase"] = DiscussionPhase.IDEATION
            prompt = "Set the creative vision for this project. What are the key themes and goals?"
        elif state["iteration_count"] > 5 and not state["consensus_reached"]:
            prompt = "Synthesize the team's input and propose a unified creative direction."
        else:
            prompt = "Guide the team forward based on the current discussion."
        
        response = await self.generate_response(state, prompt)
        
        state["messages"].append({
            "agent": self.name,
            "role": self.role,
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "phase": state["discussion_phase"].value
        })
        
        # Determine next agent based on phase
        state["next_agent"] = self._determine_next_agent(state)
        
        return state
    
    def _determine_next_agent(self, state: AgentState) -> str:
        """Determine which agent should go next"""
        phase = state["discussion_phase"]
        
        if phase == DiscussionPhase.IDEATION:
            return "script_writer"
        elif phase == DiscussionPhase.CHARACTER_DEVELOPMENT:
            return "character_designer"
        elif phase == DiscussionPhase.VISUAL_PLANNING:
            return "visual_director"
        elif phase == DiscussionPhase.AUDIO_DESIGN:
            return "sound_designer"
        elif phase == DiscussionPhase.REVIEW:
            return "quality_reviewer"
        else:
            return "consensus_builder"


class CharacterDesignerAgent(BaseAgent):
    """Character Designer - Ensures character consistency"""
    
    def __init__(self, character_manager: EnhancedCharacterManager):
        super().__init__(
            name="Sofia Identity",
            role="Character Designer",
            personality_traits=["observant", "detail-oriented", "consistent", "creative"],
            communication_style="Visual, precise, and character-focused",
            focus_areas=["character consistency", "visual identity", "personality development", "character relationships"]
        )
        self.character_manager = character_manager
    
    async def process(self, state: AgentState) -> AgentState:
        """Focus on character development and consistency"""
        
        # Extract character mentions from discussion
        characters_mentioned = self._extract_characters(state["messages"])
        
        # Check if we need to create new characters
        for char_name in characters_mentioned:
            if char_name not in state["active_characters"]:
                # Propose character profile
                profile_suggestion = await self._propose_character_profile(char_name, state)
                
                state["character_profiles"][char_name] = profile_suggestion
                state["active_characters"].append(char_name)
        
        # Generate character-focused response
        prompt = f"""
        Based on the characters discussed: {', '.join(characters_mentioned)}
        Provide detailed character descriptions ensuring:
        1. Visual consistency across all scenes
        2. Distinct personality traits
        3. Clear relationships between characters
        4. Specific appearance details for AI generation
        """
        
        response = await self.generate_response(state, prompt)
        
        state["messages"].append({
            "agent": self.name,
            "role": self.role,
            "content": response,
            "characters": state["character_profiles"],
            "timestamp": datetime.now().isoformat()
        })
        
        state["discussion_phase"] = DiscussionPhase.VISUAL_PLANNING
        state["next_agent"] = "visual_director"
        
        return state
    
    def _extract_characters(self, messages: List[Dict]) -> List[str]:
        """Extract character names from discussion"""
        # Simplified extraction - in production, use NLP
        characters = []
        for msg in messages:
            content = msg.get("content", "").lower()
            # Look for common character indicators
            if "character" in content or "protagonist" in content or "hero" in content:
                # Extract potential character names (simplified)
                words = content.split()
                for i, word in enumerate(words):
                    if word in ["character", "protagonist", "hero", "named"]:
                        if i + 1 < len(words):
                            characters.append(words[i + 1].capitalize())
        
        return list(set(characters))
    
    async def _propose_character_profile(self, name: str, state: AgentState) -> Dict:
        """Propose a character profile based on discussion context"""
        prompt = f"""
        Create a detailed character profile for {name} based on the mission: {state['mission']}
        Include:
        - Age and appearance
        - Personality traits
        - Role in the story
        - Visual description for AI generation
        """
        
        response = await self.generate_response(state, prompt)
        
        return {
            "name": name,
            "description": response,
            "created_by": self.name,
            "timestamp": datetime.now().isoformat()
        }


class ScriptWriterAgent(BaseAgent):
    """Script Writer - Develops narrative and dialogue"""
    
    def __init__(self):
        super().__init__(
            name="Marcus Narrative",
            role="Script Writer",
            personality_traits=["storyteller", "empathetic", "detail-oriented", "creative"],
            communication_style="Concise, analytical, output-focused",
            focus_areas=["story structure", "dialogue", "character arcs", "emotional beats"]
        )
    
    async def process(self, state: AgentState) -> AgentState:
        """Develop the script and narrative"""
        
        prompt = f"""
        Based on the creative vision and characters discussed, develop:
        1. A compelling narrative structure
        2. Key dialogue moments
        3. Emotional beats and pacing
        4. Scene descriptions for visual generation
        
        Ensure the script serves the mission: {state['mission']}
        """
        
        response = await self.generate_response(state, prompt)
        
        # Extract script elements
        script_draft = self._extract_script_elements(response)
        state["script_draft"] = script_draft
        
        state["messages"].append({
            "agent": self.name,
            "role": self.role,
            "content": response,
            "script_elements": script_draft,
            "timestamp": datetime.now().isoformat()
        })
        
        state["discussion_phase"] = DiscussionPhase.CHARACTER_DEVELOPMENT
        state["next_agent"] = "character_designer"
        
        return state
    
    def _extract_script_elements(self, response: str) -> str:
        """Extract structured script elements from response"""
        # Simplified extraction - in production, use structured parsing
        return response


class VisualDirectorAgent(BaseAgent):
    """Visual Director - Plans visual aesthetics and cinematography"""
    
    def __init__(self):
        super().__init__(
            name="Kai Aesthetic",
            role="Visual Director",
            personality_traits=["artistic", "technical", "innovative", "detail-oriented"],
            communication_style="Technical, precise, specification-focused",
            focus_areas=["cinematography", "color grading", "visual effects", "scene composition"]
        )
    
    async def process(self, state: AgentState) -> AgentState:
        """Plan visual elements and aesthetics"""
        
        prompt = f"""
        Design the visual approach for this project:
        1. Cinematography style and camera movements
        2. Color palette and visual mood
        3. Scene compositions and framing
        4. Visual effects and transitions
        
        Consider the characters: {', '.join(state['active_characters'])}
        And the narrative tone from the script.
        """
        
        response = await self.generate_response(state, prompt)
        
        # Extract visual guidelines
        visual_guidelines = {
            "cinematography": "dynamic camera movements",
            "color_palette": "warm and vibrant",
            "visual_style": "cinematic realism",
            "effects": "subtle and enhancing"
        }
        
        state["visual_guidelines"] = visual_guidelines
        
        state["messages"].append({
            "agent": self.name,
            "role": self.role,
            "content": response,
            "visual_guidelines": visual_guidelines,
            "timestamp": datetime.now().isoformat()
        })
        
        state["discussion_phase"] = DiscussionPhase.AUDIO_DESIGN
        state["next_agent"] = "sound_designer"
        
        return state


class ConsensusBuilderAgent(BaseAgent):
    """Consensus Builder - Facilitates agreement among agents"""
    
    def __init__(self):
        super().__init__(
            name="Harmony Synthesis",
            role="Consensus Builder",
            personality_traits=["diplomatic", "analytical", "patient", "integrative"],
            communication_style="Direct, decisive, conclusion-focused",
            focus_areas=["conflict resolution", "integration", "decision making", "team alignment"]
        )
    
    async def process(self, state: AgentState) -> AgentState:
        """Build consensus among all agents"""
        
        # Analyze all agent inputs
        agent_positions = self._analyze_positions(state["messages"])
        
        prompt = f"""
        Synthesize all team inputs into a unified vision:
        1. Identify common themes and agreements
        2. Resolve any conflicting viewpoints
        3. Propose final integrated solution
        4. Ensure all perspectives are represented
        
        Agent positions: {agent_positions}
        """
        
        response = await self.generate_response(state, prompt)
        
        # Calculate consensus score
        consensus_score = self._calculate_consensus(state)
        state["consensus_score"] = consensus_score
        
        if consensus_score > 0.75:
            state["consensus_reached"] = True
            state["discussion_phase"] = DiscussionPhase.COMPLETE
            
            # Compile final output
            state["final_output"] = self._compile_final_output(state)
        
        state["messages"].append({
            "agent": self.name,
            "role": self.role,
            "content": response,
            "consensus_score": consensus_score,
            "consensus_reached": state["consensus_reached"],
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    def _analyze_positions(self, messages: List[Dict]) -> str:
        """Analyze positions of different agents"""
        positions = {}
        for msg in messages:
            agent = msg.get("agent", "Unknown")
            if agent not in positions:
                positions[agent] = []
            positions[agent].append(msg.get("content", "")[:100])
        
        return json.dumps(positions, indent=2)
    
    def _calculate_consensus(self, state: AgentState) -> float:
        """Calculate consensus score based on agent agreements"""
        # Simplified calculation - in production, use sentiment analysis
        if state["iteration_count"] > 5:
            return 0.8
        return 0.5
    
    def _compile_final_output(self, state: AgentState) -> Dict:
        """Compile all decisions into final output"""
        return {
            "mission": state["mission"],
            "script": state.get("script_draft", ""),
            "characters": state.get("character_profiles", {}),
            "visual_guidelines": state.get("visual_guidelines", {}),
            "audio_specifications": state.get("audio_specifications", {}),
            "consensus_score": state["consensus_score"],
            "total_iterations": state["iteration_count"],
            "agents_participated": list(set(state["agents_participated"]))
        }


# ============= Main LangGraph Agent System =============

class LangGraphAgentSystem:
    """
    Main orchestrator for multi-agent discussions using LangGraph
    Implements Dependency Inversion Principle
    """
    
    def __init__(self, 
                 character_manager: Optional[EnhancedCharacterManager] = None,
                 checkpoint_dir: str = "./checkpoints"):
        """
        Initialize the LangGraph agent system
        
        Args:
            character_manager: Manager for character consistency
            checkpoint_dir: Directory for saving checkpoints
        """
        self.character_manager = character_manager or EnhancedCharacterManager()
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Build the discussion graph
        self.graph = self._build_discussion_graph()
        
        # Set up checkpointing
        self.memory = SqliteSaver.from_conn_string(
            f"sqlite:///{checkpoint_dir}/discussions.db"
        )
        
        logger.info("✅ LangGraph Agent System initialized with %d agents", len(self.agents))
    
    def _initialize_agents(self) -> Dict[str, AgentInterface]:
        """Initialize all specialized agents"""
        return {
            "creative_director": CreativeDirectorAgent(),
            "script_writer": ScriptWriterAgent(),
            "character_designer": CharacterDesignerAgent(self.character_manager),
            "visual_director": VisualDirectorAgent(),
            "consensus_builder": ConsensusBuilderAgent()
        }
    
    def _build_discussion_graph(self) -> StateGraph:
        """Build the agent discussion graph with dynamic routing"""
        
        # Create workflow with AgentState
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        for agent_name, agent in self.agents.items():
            workflow.add_node(agent_name, agent.process)
        
        # Add entry point
        workflow.set_entry_point("creative_director")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "creative_director",
            self._route_from_director,
            {
                "script_writer": "script_writer",
                "character_designer": "character_designer",
                "visual_director": "visual_director",
                "consensus_builder": "consensus_builder",
                END: END
            }
        )
        
        # Add edges from other agents
        workflow.add_edge("script_writer", "character_designer")
        workflow.add_edge("character_designer", "visual_director")
        workflow.add_edge("visual_director", "consensus_builder")
        
        # Consensus builder can loop back or end
        workflow.add_conditional_edges(
            "consensus_builder",
            self._route_from_consensus,
            {
                "creative_director": "creative_director",
                END: END
            }
        )
        
        # Compile the graph
        compiled_graph = workflow.compile(checkpointer=self.memory)
        
        return compiled_graph
    
    def _route_from_director(self, state: AgentState) -> str:
        """Route from creative director based on state"""
        
        if state.get("consensus_reached", False):
            return END
        
        next_agent = state.get("next_agent")
        if next_agent and next_agent in self.agents:
            return next_agent
        
        # Default routing based on phase
        phase = state.get("discussion_phase", DiscussionPhase.IDEATION)
        
        if phase == DiscussionPhase.IDEATION:
            return "script_writer"
        elif phase == DiscussionPhase.CHARACTER_DEVELOPMENT:
            return "character_designer"
        elif phase == DiscussionPhase.VISUAL_PLANNING:
            return "visual_director"
        else:
            return "consensus_builder"
    
    def _route_from_consensus(self, state: AgentState) -> str:
        """Route from consensus builder"""
        
        if state.get("consensus_reached", False):
            return END
        
        if state.get("iteration_count", 0) > 10:
            # Force end after max iterations
            return END
        
        # Loop back to creative director
        return "creative_director"
    
    async def run_discussion(self, 
                            mission: str,
                            existing_characters: Optional[List[str]] = None,
                            config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run a complete agent discussion
        
        Args:
            mission: The creative mission/brief
            existing_characters: List of existing character IDs to use
            config: Optional configuration overrides
            
        Returns:
            Final discussion output with decisions
        """
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            current_topic=mission,
            discussion_phase=DiscussionPhase.IDEATION,
            mission=mission,
            active_characters=existing_characters or [],
            character_references={},
            character_profiles={},
            scene_context="",
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
        
        # Run the graph
        logger.info("🚀 Starting agent discussion for mission: %s", mission[:100])
        
        try:
            # Execute with checkpointing
            final_state = await self.graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": mission[:50]}}
            )
            
            logger.info("✅ Discussion complete. Consensus score: %.2f", 
                       final_state.get("consensus_score", 0))
            
            return final_state.get("final_output", {})
            
        except Exception as e:
            logger.error(f"Discussion failed: {e}")
            raise
    
    async def run_discussion_stream(self, 
                                  mission: str,
                                  callback=None) -> AsyncIterator[Dict]:
        """
        Run discussion with streaming updates
        
        Args:
            mission: The creative mission/brief
            callback: Optional callback for updates
            
        Yields:
            State updates as discussion progresses
        """
        
        initial_state = AgentState(
            messages=[],
            current_topic=mission,
            discussion_phase=DiscussionPhase.IDEATION,
            mission=mission,
            active_characters=[],
            character_references={},
            character_profiles={},
            scene_context="",
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
        
        # Stream events
        async for event in self.graph.astream(
            initial_state,
            config={"configurable": {"thread_id": mission[:50]}}
        ):
            if callback:
                await callback(event)
            yield event
    
    def get_agent_info(self) -> Dict[str, Dict]:
        """Get information about all agents"""
        return {
            name: agent.get_personality() 
            for name, agent in self.agents.items()
        }
    
    async def test_system(self) -> bool:
        """Test the agent system"""
        try:
            # Run a simple test discussion
            result = await self.run_discussion(
                mission="Create a 10-second test video",
                config={"max_iterations": 3}
            )
            
            if result:
                logger.info("✅ LangGraph Agent System test successful")
                return True
                
        except Exception as e:
            logger.error(f"System test failed: {e}")
        
        return False


# ============= Example Usage =============

if __name__ == "__main__":
    async def main():
        # Initialize system
        system = LangGraphAgentSystem()
        
        # Test the system
        if await system.test_system():
            print("System ready!")
            
            # Run a discussion
            result = await system.run_discussion(
                mission="Create a 30-second commercial for a futuristic pizza restaurant featuring a robot chef"
            )
            
            print("\n=== Discussion Result ===")
            print(json.dumps(result, indent=2))
    
    # Run the example
    asyncio.run(main())