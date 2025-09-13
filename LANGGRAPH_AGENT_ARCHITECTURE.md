# LangGraph-Based Agent Architecture with Character Consistency

## Overview
This document outlines the integration of LangGraph for our multi-agent discussion system, combined with character consistency features, following OOP, SOLID, and microservices principles.

## Why LangGraph?

### Current Issues with Our Agent System:
1. **No State Management**: Agents lose context between interactions
2. **Linear Flow**: Can't handle complex branching discussions
3. **Poor Orchestration**: Difficult to coordinate multiple agents
4. **No Checkpointing**: Can't resume interrupted discussions

### LangGraph Benefits:
1. **State Graphs**: Maintain conversation state across agent interactions
2. **Conditional Routing**: Dynamic agent selection based on context
3. **Parallel Execution**: Run multiple agents concurrently
4. **Checkpointing**: Save and resume complex workflows
5. **Stream Events**: Real-time monitoring of agent discussions

## Architecture Design

### 1. Core Components (Following SOLID Principles)

```python
# Single Responsibility Principle
class AgentInterface(ABC):
    """Interface for all agents (Interface Segregation)"""
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass

class CharacterAgent(AgentInterface):
    """Agent with character personality (Single Responsibility)"""
    def __init__(self, character_profile: EnhancedCharacterProfile):
        self.character = character_profile
        self.llm = self._setup_llm()
    
    async def process(self, state: AgentState) -> AgentState:
        # Process with character personality
        pass

class DiscussionOrchestrator:
    """Orchestrates multi-agent discussions (Open/Closed Principle)"""
    def __init__(self, graph: StateGraph):
        self.graph = graph
        self.agents = {}
    
    def add_agent(self, agent: AgentInterface):
        # Open for extension, closed for modification
        pass
```

### 2. LangGraph State Management

```python
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

class AgentState(TypedDict):
    """Shared state across all agents"""
    # Core discussion state
    messages: List[Dict[str, str]]
    current_topic: str
    discussion_phase: str
    
    # Character consistency state
    active_characters: List[str]
    character_references: Dict[str, str]
    scene_context: str
    
    # Decision tracking
    decisions_made: List[Dict[str, str]]
    consensus_reached: bool
    
    # Metadata
    iteration_count: int
    agent_votes: Dict[str, str]
    next_agent: Optional[str]
```

### 3. Enhanced Agent System with LangGraph

```python
class LangGraphAgentSystem:
    """
    Main orchestrator for multi-agent discussions using LangGraph
    Follows Dependency Inversion Principle
    """
    
    def __init__(self, 
                 character_manager: EnhancedCharacterManager,
                 ai_service_manager: AIServiceManager):
        self.character_manager = character_manager
        self.ai_service = ai_service_manager
        self.graph = self._build_discussion_graph()
        self.memory = SqliteSaver.from_conn_string(":memory:")
    
    def _build_discussion_graph(self) -> StateGraph:
        """Build the agent discussion graph"""
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("creative_director", self.creative_director_agent)
        workflow.add_node("script_writer", self.script_writer_agent)
        workflow.add_node("character_designer", self.character_designer_agent)
        workflow.add_node("visual_director", self.visual_director_agent)
        workflow.add_node("sound_designer", self.sound_designer_agent)
        workflow.add_node("quality_reviewer", self.quality_reviewer_agent)
        workflow.add_node("consensus_builder", self.consensus_builder_agent)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "creative_director",
            self._route_discussion,
            {
                "script": "script_writer",
                "character": "character_designer",
                "visual": "visual_director",
                "audio": "sound_designer",
                "review": "quality_reviewer",
                "consensus": "consensus_builder",
                END: END
            }
        )
        
        # Set entry point
        workflow.set_entry_point("creative_director")
        
        return workflow.compile(checkpointer=self.memory)
    
    def _route_discussion(self, state: AgentState) -> str:
        """Dynamic routing based on discussion state"""
        if state["consensus_reached"]:
            return END
        
        # Intelligent routing based on discussion phase
        phase = state["discussion_phase"]
        if phase == "ideation":
            return "script_writer"
        elif phase == "character_development":
            return "character_designer"
        elif phase == "visual_planning":
            return "visual_director"
        elif phase == "review":
            return "quality_reviewer"
        elif state["iteration_count"] > 3:
            return "consensus_builder"
        
        # Default to next in sequence
        return state.get("next_agent", "creative_director")
```

### 4. Character-Aware Agents

```python
class CharacterDesignerAgent:
    """
    Agent responsible for character consistency in discussions
    Implements Single Responsibility Principle
    """
    
    def __init__(self, 
                 character_manager: EnhancedCharacterManager,
                 gemini_client: GeminiFlashImageClient):
        self.character_manager = character_manager
        self.gemini_client = gemini_client
        self.role = "Character Designer"
        self.personality = self._load_personality()
    
    async def process(self, state: AgentState) -> AgentState:
        """Process state with focus on character consistency"""
        
        # Extract character requirements from discussion
        character_needs = self._analyze_character_needs(state["messages"])
        
        # Check existing characters
        existing_chars = state.get("active_characters", [])
        
        # Generate or retrieve character references
        for char_name in character_needs:
            if char_name not in existing_chars:
                # Create new character with Gemini 2.5 Flash
                char_id = await self._create_character(char_name, state)
                state["active_characters"].append(char_id)
                
                # Generate reference image
                ref_image = await self._generate_reference(char_id, state)
                state["character_references"][char_id] = ref_image
        
        # Add character consistency recommendations
        response = await self._generate_response(state)
        state["messages"].append({
            "agent": self.role,
            "content": response,
            "character_refs": state["character_references"]
        })
        
        # Update routing
        state["next_agent"] = self._determine_next_agent(state)
        
        return state
    
    async def _create_character(self, name: str, state: AgentState) -> str:
        """Create a new character based on discussion context"""
        # Extract character description from discussion
        description = self._extract_character_description(name, state["messages"])
        
        # Use character manager to create profile
        appearance = self._parse_appearance(description)
        personality = self._parse_personality(description)
        
        char_id = self.character_manager.create_character(
            name=name,
            description=description,
            appearance=appearance,
            personality=personality
        )
        
        return char_id
```

### 5. Microservices Architecture

```python
# Each component as a separate service

class CharacterService:
    """Microservice for character management"""
    
    def __init__(self, port: int = 8001):
        self.app = FastAPI()
        self.character_manager = EnhancedCharacterManager()
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.post("/characters/create")
        async def create_character(request: CharacterRequest):
            # Handle character creation
            pass
        
        @self.app.get("/characters/{character_id}/reference")
        async def get_reference(character_id: str):
            # Return character reference images
            pass

class AgentService:
    """Microservice for agent discussions"""
    
    def __init__(self, port: int = 8002):
        self.app = FastAPI()
        self.agent_system = LangGraphAgentSystem()
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.post("/discussions/start")
        async def start_discussion(request: DiscussionRequest):
            # Start new discussion
            pass
        
        @self.app.get("/discussions/{discussion_id}/state")
        async def get_state(discussion_id: str):
            # Return current discussion state
            pass

class VideoGenerationService:
    """Microservice for video generation"""
    
    def __init__(self, port: int = 8003):
        self.app = FastAPI()
        self.veo_client = EnhancedVeo3Client()
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.post("/videos/generate")
        async def generate_video(request: VideoRequest):
            # Generate video with character references
            pass
```

### 6. Implementation Pipeline

```python
class CharacterConsistentVideoWorkflow:
    """
    Complete workflow combining LangGraph agents with character consistency
    """
    
    def __init__(self):
        self.graph = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(VideoProductionState)
        
        # Phase 1: Ideation with agents
        workflow.add_node("agent_discussion", self.run_agent_discussion)
        
        # Phase 2: Character creation
        workflow.add_node("character_creation", self.create_characters)
        
        # Phase 3: Scene generation
        workflow.add_node("scene_generation", self.generate_scenes)
        
        # Phase 4: Video production
        workflow.add_node("video_production", self.produce_videos)
        
        # Phase 5: Quality review
        workflow.add_node("quality_review", self.review_output)
        
        # Add edges
        workflow.add_edge("agent_discussion", "character_creation")
        workflow.add_edge("character_creation", "scene_generation")
        workflow.add_edge("scene_generation", "video_production")
        workflow.add_edge("video_production", "quality_review")
        
        # Conditional edge for iteration
        workflow.add_conditional_edges(
            "quality_review",
            lambda x: "end" if x["quality_passed"] else "agent_discussion",
            {
                "agent_discussion": "agent_discussion",
                "end": END
            }
        )
        
        workflow.set_entry_point("agent_discussion")
        
        return workflow.compile()
    
    async def run_workflow(self, mission: str) -> Dict:
        """Execute the complete workflow"""
        initial_state = {
            "mission": mission,
            "messages": [],
            "characters": {},
            "scenes": [],
            "videos": [],
            "quality_passed": False
        }
        
        # Run with streaming for real-time updates
        async for event in self.graph.astream(initial_state):
            logger.info(f"Workflow event: {event}")
            yield event
```

## Agent Personality Templates

```python
AGENT_PERSONALITIES = {
    "creative_director": {
        "name": "Alexandra Vision",
        "traits": ["visionary", "decisive", "strategic"],
        "communication_style": "Direct and inspiring",
        "focus_areas": ["overall vision", "brand alignment", "creative excellence"]
    },
    "script_writer": {
        "name": "Marcus Narrative",
        "traits": ["storyteller", "detail-oriented", "empathetic"],
        "communication_style": "Descriptive and engaging",
        "focus_areas": ["story structure", "dialogue", "character development"]
    },
    "character_designer": {
        "name": "Sofia Identity", 
        "traits": ["observant", "consistent", "creative"],
        "communication_style": "Visual and precise",
        "focus_areas": ["character consistency", "visual identity", "personality traits"]
    },
    "visual_director": {
        "name": "Kai Aesthetic",
        "traits": ["artistic", "technical", "innovative"],
        "communication_style": "Visual metaphors and technical precision",
        "focus_areas": ["cinematography", "color grading", "visual effects"]
    },
    "sound_designer": {
        "name": "Rhythm Echo",
        "traits": ["musical", "atmospheric", "technical"],
        "communication_style": "Descriptive audio terminology",
        "focus_areas": ["music", "sound effects", "audio synchronization"]
    }
}
```

## Benefits of This Architecture

### 1. **State Management**
- Persistent state across agent interactions
- Checkpointing for long discussions
- Resume interrupted workflows

### 2. **Better Orchestration**
- Dynamic agent routing based on context
- Parallel agent execution when needed
- Conditional branching in discussions

### 3. **Character Consistency**
- Integrated character management in agent discussions
- Automatic reference generation
- Consistency validation at each step

### 4. **SOLID Compliance**
- **S**: Each agent has single responsibility
- **O**: Open for extension via new agents
- **L**: AgentInterface ensures substitutability
- **I**: Specific interfaces for different agent types
- **D**: Dependency injection throughout

### 5. **Microservices Benefits**
- Independent scaling of services
- Technology agnostic (can use different languages)
- Fault isolation
- Easy deployment and updates

## Implementation Steps

1. **Install Dependencies**:
```bash
pip install langgraph langchain langchain-google-genai fastapi uvicorn
```

2. **Set up Configuration**:
```python
# config/langgraph_config.py
LANGGRAPH_CONFIG = {
    "checkpoint_storage": "sqlite:///agent_discussions.db",
    "max_iterations": 10,
    "parallel_agents": True,
    "streaming": True,
    "agent_timeout": 30,
    "consensus_threshold": 0.7
}
```

3. **Environment Variables**:
```bash
export LANGGRAPH_API_KEY="your-key"
export GOOGLE_AI_API_KEY="your-gemini-key"
export VERTEX_AI_PROJECT="viralgen-464411"
```

## Testing Strategy

```python
import pytest
from langgraph.testing import GraphTester

class TestLangGraphAgents:
    @pytest.fixture
    def agent_system(self):
        return LangGraphAgentSystem()
    
    async def test_discussion_flow(self, agent_system):
        """Test complete discussion flow"""
        result = await agent_system.run_discussion(
            mission="Create a 30-second ad for a pizza restaurant"
        )
        
        assert result["consensus_reached"] == True
        assert len(result["characters"]) > 0
        assert result["quality_score"] > 0.8
    
    async def test_character_consistency(self, agent_system):
        """Test character consistency across discussions"""
        char_id = await agent_system.create_character("Pizza Chef Mario")
        
        # Run multiple discussions with same character
        results = []
        for i in range(3):
            result = await agent_system.run_discussion(
                mission=f"Scene {i} with Chef Mario",
                existing_characters=[char_id]
            )
            results.append(result)
        
        # Verify consistency
        for result in results:
            assert result["character_consistency_score"] > 0.95
```

## Monitoring and Observability

```python
from langgraph.callbacks import LangGraphCallbackHandler
import wandb

class MonitoringCallback(LangGraphCallbackHandler):
    def on_agent_start(self, agent_name: str, state: AgentState):
        wandb.log({
            "agent_started": agent_name,
            "iteration": state["iteration_count"]
        })
    
    def on_agent_end(self, agent_name: str, state: AgentState):
        wandb.log({
            "agent_completed": agent_name,
            "messages_count": len(state["messages"])
        })
```

## Conclusion

Integrating LangGraph with our character consistency system provides:
1. **Robust state management** for complex agent discussions
2. **Dynamic routing** based on discussion context
3. **Character consistency** throughout the creative process
4. **SOLID principles** for maintainable code
5. **Microservices architecture** for scalability

This architecture significantly improves our AI agent discussions while maintaining the ability to create consistent characters across entire movies and video series.