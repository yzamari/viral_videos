"""
Agent System Interfaces
Provider-agnostic agent system with dependency injection
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Dict, Any, List, Type
from enum import Enum
from ..ai.interfaces.text_generation import TextGenerationService
from ..ai.interfaces.base import AIProvider

T = TypeVar('T')  # Agent output type

class AgentRole(Enum):
    """Standard agent roles"""
    # Core Creative Team
    TREND_ANALYST = "trend_analyst"
    SCRIPT_WRITER = "script_writer"
    DIRECTOR = "director"
    VIDEO_GENERATOR = "video_generator"
    SOUNDMAN = "soundman"
    EDITOR = "editor"
    ORCHESTRATOR = "orchestrator"
    
    # Extended Team
    MARKETING_STRATEGIST = "marketing_strategist"
    SOCIAL_MEDIA_EXPERT = "social_media_expert"
    BRAND_SPECIALIST = "brand_specialist"
    ENGAGEMENT_OPTIMIZER = "engagement_optimizer"
    VISUAL_DESIGNER = "visual_designer"
    PLATFORM_OPTIMIZER = "platform_optimizer"
    VIRAL_SPECIALIST = "viral_specialist"
    NEUROSCIENTIST = "neuroscientist"
    
    # Additional Specialist Roles
    AUDIENCE_PSYCHOLOGIST = "audience_psychologist"
    PLATFORM_SPECIALIST = "platform_specialist"
    CREATIVE_STRATEGIST = "creative_strategist"
    BRAND_STRATEGIST = "brand_strategist"
    CONTENT_STRATEGIST = "content_strategist"
    MARKETING_SPECIALIST = "marketing_specialist"
    DESIGNER = "designer"
    COPYWRITER = "copywriter"
    DATA_ANALYST = "data_analyst"

@dataclass
class AgentContext:
    """Context passed to agents for execution"""
    mission: str
    session_id: str
    previous_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    target_platform: Optional[str] = None
    target_audience: Optional[str] = None
    style_preferences: Optional[Dict[str, Any]] = None

@dataclass
class AgentResponse(Generic[T]):
    """Standard agent response"""
    success: bool
    data: Optional[T] = None
    reasoning: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

class AgentInterface(ABC, Generic[T]):
    """Base interface for all agents"""
    
    def __init__(self, 
                 ai_service: TextGenerationService,
                 role: AgentRole,
                 name: Optional[str] = None):
        self.ai_service = ai_service
        self.role = role
        self.name = name or role.value.replace('_', ' ').title()
        self.context: Optional[AgentContext] = None
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResponse[T]:
        """Execute agent logic and return response"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        pass
    
    def get_role(self) -> AgentRole:
        """Get agent's role"""
        return self.role
    
    def get_name(self) -> str:
        """Get agent's name"""
        return self.name
    
    async def validate_context(self, context: AgentContext) -> bool:
        """Validate context before execution"""
        return context.mission and context.session_id
    
    async def prepare_prompt(self, context: AgentContext) -> str:
        """Prepare prompt for AI service"""
        return f"""
        You are {self.name}, a {self.role.value} agent.
        
        Mission: {context.mission}
        Context: {context.metadata}
        
        Please provide your analysis and recommendations.
        """

class CollaborativeAgent(AgentInterface[T]):
    """Agent that can collaborate with other agents"""
    
    def __init__(self,
                 ai_service: TextGenerationService,
                 role: AgentRole,
                 collaborators: Optional[List['CollaborativeAgent']] = None):
        super().__init__(ai_service, role)
        self.collaborators = collaborators or []
    
    async def consult_collaborators(self, 
                                   context: AgentContext,
                                   question: str) -> List[AgentResponse]:
        """Consult with collaborator agents"""
        responses = []
        for collaborator in self.collaborators:
            response = await collaborator.execute(context)
            responses.append(response)
        return responses
    
    async def reach_consensus(self,
                             responses: List[AgentResponse],
                             threshold: float = 0.7) -> Optional[Any]:
        """Reach consensus among responses"""
        if not responses:
            return None
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in responses) / len(responses)
        
        if avg_confidence >= threshold:
            # Return most confident response
            return max(responses, key=lambda r: r.confidence)
        
        return None

class AgentFactory:
    """Factory for creating agents with dependency injection"""
    
    def __init__(self, ai_manager):
        """Initialize factory with AI manager"""
        self.ai_manager = ai_manager
        self._registry: Dict[AgentRole, Type[AgentInterface]] = {}
    
    def register(self, role: AgentRole, agent_class: Type[AgentInterface]):
        """Register an agent implementation"""
        self._registry[role] = agent_class
    
    def create_agent(self,
                    role: AgentRole,
                    provider: Optional[AIProvider] = None,
                    **kwargs) -> AgentInterface:
        """Create agent with specified AI provider"""
        if role not in self._registry:
            raise ValueError(f"No agent registered for role: {role}")
        
        # Get AI service with specified provider
        ai_service = self.ai_manager.get_text_service(provider)
        
        # Get agent class
        agent_class = self._registry[role]
        
        # Create and return agent
        return agent_class(ai_service, role, **kwargs)
    
    def create_team(self,
                   roles: List[AgentRole],
                   provider: Optional[AIProvider] = None) -> Dict[AgentRole, AgentInterface]:
        """Create a team of agents"""
        team = {}
        for role in roles:
            team[role] = self.create_agent(role, provider)
        return team
    
    def get_available_roles(self) -> List[AgentRole]:
        """Get list of available agent roles"""
        return list(self._registry.keys())

class AgentOrchestrator:
    """Orchestrates multiple agents for complex tasks"""
    
    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self.agents: Dict[AgentRole, AgentInterface] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_agent(self, 
                 role: AgentRole,
                 provider: Optional[AIProvider] = None):
        """Add an agent to the orchestrator"""
        agent = self.factory.create_agent(role, provider)
        self.agents[role] = agent
    
    async def execute_sequential(self,
                                context: AgentContext,
                                roles: List[AgentRole]) -> List[AgentResponse]:
        """Execute agents sequentially"""
        responses = []
        
        for role in roles:
            if role not in self.agents:
                self.add_agent(role)
            
            agent = self.agents[role]
            
            # Update context with previous results
            if responses:
                context.previous_results[roles[len(responses)-1].value] = responses[-1].data
            
            response = await agent.execute(context)
            responses.append(response)
            
            # Record execution
            self.execution_history.append({
                'role': role,
                'response': response,
                'timestamp': self._get_timestamp()
            })
        
        return responses
    
    async def execute_parallel(self,
                             context: AgentContext,
                             roles: List[AgentRole]) -> List[AgentResponse]:
        """Execute agents in parallel"""
        import asyncio
        
        tasks = []
        for role in roles:
            if role not in self.agents:
                self.add_agent(role)
            
            agent = self.agents[role]
            tasks.append(agent.execute(context))
        
        responses = await asyncio.gather(*tasks)
        
        # Record execution
        for role, response in zip(roles, responses):
            self.execution_history.append({
                'role': role,
                'response': response,
                'timestamp': self._get_timestamp()
            })
        
        return responses
    
    async def execute_with_voting(self,
                                 context: AgentContext,
                                 roles: List[AgentRole],
                                 threshold: float = 0.6) -> AgentResponse:
        """Execute agents and return consensus result"""
        responses = await self.execute_parallel(context, roles)
        
        # Calculate consensus
        successful_responses = [r for r in responses if r.success]
        
        if len(successful_responses) / len(responses) >= threshold:
            # Return highest confidence response
            best_response = max(successful_responses, key=lambda r: r.confidence)
            return best_response
        
        # No consensus reached
        return AgentResponse(
            success=False,
            error="No consensus reached among agents"
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()