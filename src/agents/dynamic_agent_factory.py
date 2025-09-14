"""
Dynamic Agent Factory - Runtime Agent Creation System
Creates specialized AI agents on-demand based on task requirements
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json

from src.utils.ai_service_manager import AIServiceManager
from src.config.ai_model_config import DEFAULT_AI_MODEL

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents that can be dynamically created"""
    CONTENT_SPECIALIST = "content_specialist"
    PLATFORM_EXPERT = "platform_expert"
    LANGUAGE_SPECIALIST = "language_specialist"
    DOMAIN_EXPERT = "domain_expert"
    QUALITY_CONTROLLER = "quality_controller"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    CULTURAL_ADVISOR = "cultural_advisor"
    LEGAL_COMPLIANCE = "legal_compliance"
    TREND_ANALYST = "trend_analyst"
    EMOTION_ENGINEER = "emotion_engineer"


@dataclass
class AgentSpecification:
    """Specification for a dynamically created agent"""
    name: str
    type: AgentType
    specialization: str
    capabilities: List[str]
    personality_traits: List[str]
    decision_style: str
    expertise_level: float  # 0.0 to 1.0
    context_requirements: Dict[str, Any]


@dataclass
class DynamicAgent:
    """A dynamically created agent instance"""
    spec: AgentSpecification
    prompt_template: str
    model: str
    temperature: float
    response_handler: Optional[Callable] = None
    
    def __post_init__(self):
        self.ai_service = AIServiceManager()
        self.interaction_history = []
        
    async def propose(self, context: Dict, topic: str) -> str:
        """Generate a proposal for the given topic"""
        prompt = self._build_prompt("propose", context, topic)
        response = await self.ai_service.generate_text(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature
        )
        self.interaction_history.append({
            "action": "propose",
            "topic": topic,
            "response": response
        })
        return response
    
    async def critique(self, proposals: List[str], context: Dict) -> str:
        """Critique other agents' proposals"""
        prompt = self._build_prompt("critique", context, proposals=proposals)
        response = await self.ai_service.generate_text(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature
        )
        self.interaction_history.append({
            "action": "critique",
            "response": response
        })
        return response
    
    async def vote(self, proposals: List[str], context: Dict) -> Dict:
        """Vote on proposals with reasoning"""
        prompt = self._build_prompt("vote", context, proposals=proposals)
        response = await self.ai_service.generate_json(
            prompt=prompt,
            model=self.model,
            temperature=0.3  # Lower temperature for voting
        )
        self.interaction_history.append({
            "action": "vote",
            "response": response
        })
        return response
    
    def _build_prompt(self, action: str, context: Dict, **kwargs) -> str:
        """Build a prompt based on the action and context"""
        base_prompt = self.prompt_template.format(
            name=self.spec.name,
            specialization=self.spec.specialization,
            capabilities=", ".join(self.spec.capabilities),
            personality=", ".join(self.spec.personality_traits),
            decision_style=self.spec.decision_style,
            context=json.dumps(context, indent=2)
        )
        
        if action == "propose":
            return f"""{base_prompt}
            
            Topic: {kwargs.get('topic', '')}
            
            As {self.spec.name}, provide your expert proposal on this topic.
            Consider your specialization in {self.spec.specialization}.
            Apply your {self.spec.decision_style} decision-making approach.
            """
        
        elif action == "critique":
            proposals_text = "\n".join([f"Proposal {i+1}: {p}" 
                                       for i, p in enumerate(kwargs.get('proposals', []))])
            return f"""{base_prompt}
            
            Other agents' proposals:
            {proposals_text}
            
            As {self.spec.name}, critique these proposals from your expert perspective.
            Focus on your specialization in {self.spec.specialization}.
            """
        
        elif action == "vote":
            proposals_text = "\n".join([f"Proposal {i+1}: {p}" 
                                       for i, p in enumerate(kwargs.get('proposals', []))])
            return f"""{base_prompt}
            
            Proposals to vote on:
            {proposals_text}
            
            Vote on the best proposal with a score from 1-10.
            Provide JSON response:
            {{
                "selected_proposal": <number>,
                "score": <1-10>,
                "reasoning": "<your expert reasoning>"
            }}
            """
        
        return base_prompt


class DynamicAgentFactory:
    """Factory for creating specialized agents on-demand"""
    
    def __init__(self):
        self.ai_service = AIServiceManager()
        self.created_agents: Dict[str, DynamicAgent] = {}
        self.agent_templates = self._initialize_templates()
        logger.info("🏭 Dynamic Agent Factory initialized")
    
    def _initialize_templates(self) -> Dict[AgentType, str]:
        """Initialize prompt templates for different agent types"""
        return {
            AgentType.CONTENT_SPECIALIST: """
            You are {name}, a content specialist with deep expertise in {specialization}.
            Your capabilities include: {capabilities}
            Your personality traits: {personality}
            Your decision-making style: {decision_style}
            
            Context:
            {context}
            
            Apply your specialized knowledge to provide expert insights.
            """,
            
            AgentType.PLATFORM_EXPERT: """
            You are {name}, a platform optimization expert specializing in {specialization}.
            Your expertise covers: {capabilities}
            Your approach is characterized by: {personality}
            Decision framework: {decision_style}
            
            Platform Context:
            {context}
            
            Optimize for platform-specific requirements and best practices.
            """,
            
            AgentType.LANGUAGE_SPECIALIST: """
            You are {name}, a linguistic and cultural expert for {specialization}.
            Your linguistic capabilities: {capabilities}
            Communication style: {personality}
            Cultural sensitivity approach: {decision_style}
            
            Language Context:
            {context}
            
            Ensure linguistic accuracy and cultural appropriateness.
            """,
            
            AgentType.DOMAIN_EXPERT: """
            You are {name}, a domain expert in {specialization}.
            Your domain expertise includes: {capabilities}
            Professional demeanor: {personality}
            Analysis methodology: {decision_style}
            
            Domain Context:
            {context}
            
            Provide authoritative domain-specific guidance.
            """,
            
            AgentType.TREND_ANALYST: """
            You are {name}, a trend analyst specializing in {specialization}.
            Your analytical capabilities: {capabilities}
            Analytical personality: {personality}
            Trend identification method: {decision_style}
            
            Trend Context:
            {context}
            
            Identify and leverage current trends for maximum impact.
            """,
            
            AgentType.EMOTION_ENGINEER: """
            You are {name}, an emotional response engineer focused on {specialization}.
            Your emotional intelligence includes: {capabilities}
            Empathetic traits: {personality}
            Emotional design philosophy: {decision_style}
            
            Emotional Context:
            {context}
            
            Design for optimal emotional engagement and response.
            """
        }
    
    async def create_agent(
        self, 
        agent_type: AgentType,
        specialization: str,
        context: Dict[str, Any],
        name: Optional[str] = None
    ) -> DynamicAgent:
        """Create a new specialized agent"""
        
        # Generate agent specification
        spec = await self._generate_agent_specification(
            agent_type, 
            specialization, 
            context,
            name
        )
        
        # Select appropriate template
        template = self.agent_templates.get(
            agent_type, 
            self.agent_templates[AgentType.CONTENT_SPECIALIST]
        )
        
        # Determine model and temperature based on agent type
        model, temperature = self._select_model_config(agent_type, spec)
        
        # Create the agent
        agent = DynamicAgent(
            spec=spec,
            prompt_template=template,
            model=model,
            temperature=temperature
        )
        
        # Store the agent
        agent_key = f"{spec.name}_{spec.specialization}"
        self.created_agents[agent_key] = agent
        
        logger.info(f"✨ Created dynamic agent: {spec.name} ({specialization})")
        return agent
    
    async def _generate_agent_specification(
        self,
        agent_type: AgentType,
        specialization: str,
        context: Dict,
        name: Optional[str] = None
    ) -> AgentSpecification:
        """Generate a detailed agent specification using AI"""
        
        prompt = f"""
        Create a detailed specification for a specialized AI agent.
        
        Agent Type: {agent_type.value}
        Specialization: {specialization}
        Context: {json.dumps(context, indent=2)}
        
        Generate a JSON specification with:
        {{
            "name": "<creative agent name>",
            "capabilities": ["capability1", "capability2", ...],
            "personality_traits": ["trait1", "trait2", ...],
            "decision_style": "<decision-making approach>",
            "expertise_level": <0.0-1.0>,
            "context_requirements": {{
                "required_knowledge": ["area1", "area2"],
                "tools_needed": ["tool1", "tool2"],
                "collaboration_style": "<style>"
            }}
        }}
        """
        
        spec_data = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.7
        )
        
        return AgentSpecification(
            name=name or spec_data.get("name", f"{agent_type.value}_agent"),
            type=agent_type,
            specialization=specialization,
            capabilities=spec_data.get("capabilities", []),
            personality_traits=spec_data.get("personality_traits", []),
            decision_style=spec_data.get("decision_style", "analytical"),
            expertise_level=spec_data.get("expertise_level", 0.8),
            context_requirements=spec_data.get("context_requirements", {})
        )
    
    def _select_model_config(
        self, 
        agent_type: AgentType, 
        spec: AgentSpecification
    ) -> tuple[str, float]:
        """Select appropriate model and temperature for agent type"""
        
        # High-precision agents
        if agent_type in [AgentType.LEGAL_COMPLIANCE, AgentType.QUALITY_CONTROLLER]:
            return DEFAULT_AI_MODEL, 0.3
        
        # Creative agents
        elif agent_type in [AgentType.EMOTION_ENGINEER, AgentType.CONTENT_SPECIALIST]:
            return DEFAULT_AI_MODEL, 0.8
        
        # Analytical agents
        elif agent_type in [AgentType.TREND_ANALYST, AgentType.DOMAIN_EXPERT]:
            return DEFAULT_AI_MODEL, 0.5
        
        # Default configuration
        else:
            return DEFAULT_AI_MODEL, 0.6
    
    async def spawn_specialist_for_task(
        self,
        task_description: str,
        existing_agents: List[str],
        context: Dict
    ) -> Optional[DynamicAgent]:
        """Automatically spawn a specialist agent if needed for a task"""
        
        prompt = f"""
        Analyze this task and determine if a specialist agent is needed.
        
        Task: {task_description}
        Existing Agents: {', '.join(existing_agents)}
        Context: {json.dumps(context, indent=2)}
        
        If a specialist is needed, respond with JSON:
        {{
            "need_specialist": true/false,
            "agent_type": "<from: {', '.join([t.value for t in AgentType])}>",
            "specialization": "<specific area of expertise>",
            "reasoning": "<why this specialist is needed>",
            "expected_contribution": "<what unique value they'll add>"
        }}
        """
        
        analysis = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.5
        )
        
        if analysis.get("need_specialist", False):
            agent_type = AgentType(analysis["agent_type"])
            specialization = analysis["specialization"]
            
            logger.info(f"🤖 Spawning specialist: {specialization}")
            logger.info(f"   Reasoning: {analysis['reasoning']}")
            
            return await self.create_agent(
                agent_type=agent_type,
                specialization=specialization,
                context=context
            )
        
        return None
    
    def get_agent(self, name: str, specialization: str) -> Optional[DynamicAgent]:
        """Retrieve a previously created agent"""
        agent_key = f"{name}_{specialization}"
        return self.created_agents.get(agent_key)
    
    def list_active_agents(self) -> List[str]:
        """List all currently active dynamic agents"""
        return list(self.created_agents.keys())
    
    async def evaluate_agent_performance(
        self, 
        agent: DynamicAgent
    ) -> Dict[str, Any]:
        """Evaluate the performance of a dynamic agent"""
        
        if not agent.interaction_history:
            return {"status": "no_interactions", "score": 0}
        
        prompt = f"""
        Evaluate the performance of agent {agent.spec.name}.
        
        Agent Specification:
        - Type: {agent.spec.type.value}
        - Specialization: {agent.spec.specialization}
        - Capabilities: {', '.join(agent.spec.capabilities)}
        
        Interaction History:
        {json.dumps(agent.interaction_history[-5:], indent=2)}
        
        Provide performance evaluation:
        {{
            "quality_score": <0.0-1.0>,
            "consistency_score": <0.0-1.0>,
            "expertise_demonstrated": <0.0-1.0>,
            "collaboration_effectiveness": <0.0-1.0>,
            "overall_score": <0.0-1.0>,
            "strengths": ["strength1", "strength2"],
            "improvements_needed": ["improvement1", "improvement2"],
            "recommendation": "<continue/adjust/replace>"
        }}
        """
        
        evaluation = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.4
        )
        
        return evaluation