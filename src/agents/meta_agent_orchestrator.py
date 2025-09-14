"""
Meta-Agent Orchestrator - Autonomous Agent Management System
Manages the lifecycle of dynamic agents and orchestrates their creation
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

from src.utils.ai_service_manager import AIServiceManager
from src.config.ai_model_config import DEFAULT_AI_MODEL
from src.agents.dynamic_agent_factory import DynamicAgentFactory, AgentType, DynamicAgent
from src.agents.agent_discovery_system import AgentDiscoverySystem

logger = logging.getLogger(__name__)


class AgentNeed(Enum):
    """Priority levels for agent needs"""
    CRITICAL = "critical"      # Must have for task success
    HIGH = "high"              # Significantly improves outcome
    MEDIUM = "medium"          # Nice to have
    LOW = "low"               # Optional enhancement


@dataclass
class AgentRequest:
    """Request for a new dynamic agent"""
    need_level: AgentNeed
    agent_type: AgentType
    specialization: str
    context: Dict[str, Any]
    requester: str  # Which agent/system requested this
    timestamp: datetime
    auto_approve: bool = False


class MetaAgentOrchestrator:
    """
    Meta-Agent that autonomously manages the agent ecosystem
    - Monitors ongoing discussions
    - Identifies capability gaps
    - Spawns specialized agents
    - Manages agent lifecycle
    """
    
    def __init__(self, auto_spawn_threshold: float = 0.85):
        self.ai_service = AIServiceManager()
        self.agent_factory = DynamicAgentFactory()
        self.discovery_system = AgentDiscoverySystem()
        
        self.auto_spawn_threshold = auto_spawn_threshold
        self.active_agents: Dict[str, DynamicAgent] = {}
        self.agent_requests: List[AgentRequest] = []
        self.agent_performance: Dict[str, Dict] = {}
        self.spawn_history: List[Dict] = []
        
        logger.info(f"🧠 Meta-Agent Orchestrator initialized (auto-spawn: {auto_spawn_threshold})")
    
    async def monitor_discussion(
        self,
        discussion_topic: str,
        participants: List[str],
        discussion_content: str,
        context: Dict[str, Any]
    ) -> Optional[DynamicAgent]:
        """Monitor an ongoing discussion and spawn agents if needed"""
        
        # Analyze if the discussion needs additional expertise
        analysis = await self._analyze_discussion_gaps(
            discussion_topic,
            participants,
            discussion_content,
            context
        )
        
        if analysis.get("needs_specialist", False):
            confidence = analysis.get("confidence", 0.0)
            
            if confidence >= self.auto_spawn_threshold:
                # Auto-spawn the specialist
                return await self._spawn_specialist(
                    analysis["specialist_type"],
                    analysis["specialization"],
                    context,
                    f"Discussion gap in: {discussion_topic}"
                )
            else:
                # Queue for manual approval
                self._queue_agent_request(
                    AgentNeed.HIGH,
                    AgentType(analysis["specialist_type"]),
                    analysis["specialization"],
                    context,
                    "meta_agent_discussion_monitor"
                )
                logger.info(f"📋 Queued specialist request: {analysis['specialization']}")
        
        return None
    
    async def _analyze_discussion_gaps(
        self,
        topic: str,
        participants: List[str],
        content: str,
        context: Dict
    ) -> Dict[str, Any]:
        """Analyze a discussion for expertise gaps"""
        
        prompt = f"""
        Analyze this ongoing discussion to identify if specialized expertise is missing.
        
        Discussion Topic: {topic}
        Current Participants: {', '.join(participants)}
        
        Discussion Content (last 500 chars):
        {content[-500:] if len(content) > 500 else content}
        
        Context: {json.dumps(context, indent=2)}
        
        Available Agent Types: {', '.join([t.value for t in AgentType])}
        
        Determine if a specialist is needed:
        {{
            "needs_specialist": true/false,
            "confidence": <0.0-1.0>,
            "specialist_type": "<agent_type if needed>",
            "specialization": "<specific expertise area>",
            "gap_identified": "<what's missing from discussion>",
            "expected_value": "<what the specialist would add>",
            "urgency": "critical/high/medium/low"
        }}
        """
        
        analysis = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.5
        )
        
        return analysis
    
    async def _spawn_specialist(
        self,
        agent_type: str,
        specialization: str,
        context: Dict,
        reason: str
    ) -> DynamicAgent:
        """Spawn a specialized agent"""
        
        logger.info(f"🚀 Auto-spawning {specialization} specialist")
        logger.info(f"   Reason: {reason}")
        
        # Create the agent
        agent = await self.agent_factory.create_agent(
            agent_type=AgentType(agent_type),
            specialization=specialization,
            context=context
        )
        
        # Register the agent
        agent_id = f"{agent.spec.name}_{datetime.now().timestamp()}"
        self.active_agents[agent_id] = agent
        
        # Log the spawn
        self.spawn_history.append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "type": agent_type,
            "specialization": specialization,
            "reason": reason,
            "auto_spawned": True
        })
        
        return agent
    
    def _queue_agent_request(
        self,
        need_level: AgentNeed,
        agent_type: AgentType,
        specialization: str,
        context: Dict,
        requester: str
    ):
        """Queue an agent request for approval"""
        
        request = AgentRequest(
            need_level=need_level,
            agent_type=agent_type,
            specialization=specialization,
            context=context,
            requester=requester,
            timestamp=datetime.now(),
            auto_approve=(need_level == AgentNeed.CRITICAL)
        )
        
        self.agent_requests.append(request)
        
        if request.auto_approve:
            logger.warning(f"⚡ Critical agent request will be auto-approved: {specialization}")
    
    async def process_agent_requests(self) -> List[DynamicAgent]:
        """Process queued agent requests"""
        
        spawned_agents = []
        
        for request in self.agent_requests:
            if request.auto_approve or request.need_level == AgentNeed.CRITICAL:
                agent = await self._spawn_specialist(
                    request.agent_type.value,
                    request.specialization,
                    request.context,
                    f"Request from {request.requester}"
                )
                spawned_agents.append(agent)
        
        # Clear processed requests
        self.agent_requests = [
            r for r in self.agent_requests 
            if not (r.auto_approve or r.need_level == AgentNeed.CRITICAL)
        ]
        
        return spawned_agents
    
    async def optimize_agent_pool(
        self,
        current_task: str,
        performance_metrics: Dict
    ) -> Dict[str, Any]:
        """Optimize the current agent pool based on performance"""
        
        prompt = f"""
        Analyze and optimize our current agent pool.
        
        Current Task: {current_task}
        
        Active Agents:
        {json.dumps([{
            "name": agent.spec.name,
            "type": agent.spec.type.value,
            "specialization": agent.spec.specialization,
            "interactions": len(agent.interaction_history)
        } for agent in self.active_agents.values()], indent=2)}
        
        Performance Metrics:
        {json.dumps(performance_metrics, indent=2)}
        
        Provide optimization recommendations:
        {{
            "agents_to_retire": [
                {{"name": "agent_name", "reason": "why_retire"}}
            ],
            "agents_to_spawn": [
                {{
                    "type": "agent_type",
                    "specialization": "area",
                    "reason": "why_needed"
                }}
            ],
            "agents_to_modify": [
                {{
                    "name": "agent_name",
                    "modification": "what_to_change",
                    "reason": "why_modify"
                }}
            ],
            "overall_health": <0.0-1.0>,
            "optimization_priority": "high/medium/low"
        }}
        """
        
        optimization = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.5
        )
        
        # Apply high-priority optimizations automatically
        if optimization.get("optimization_priority") == "high":
            await self._apply_optimizations(optimization)
        
        return optimization
    
    async def _apply_optimizations(self, optimization: Dict):
        """Apply optimization recommendations"""
        
        # Retire underperforming agents
        for retirement in optimization.get("agents_to_retire", []):
            agent_name = retirement["name"]
            if agent_name in self.active_agents:
                logger.info(f"🔚 Retiring agent: {agent_name}")
                logger.info(f"   Reason: {retirement['reason']}")
                del self.active_agents[agent_name]
        
        # Spawn new agents
        for spawn_req in optimization.get("agents_to_spawn", []):
            await self._spawn_specialist(
                spawn_req["type"],
                spawn_req["specialization"],
                {},  # Context will be filled by factory
                spawn_req["reason"]
            )
    
    async def handle_complex_task(
        self,
        task_description: str,
        context: Dict
    ) -> List[DynamicAgent]:
        """Handle a complex task by assembling the right team of agents"""
        
        # Analyze task complexity
        recommendations = await self.discovery_system.recommend_dynamic_agents(
            task_description,
            context,
            threshold=0.6  # Lower threshold for complex tasks
        )
        
        # Spawn high-priority agents
        spawned_agents = []
        for rec in recommendations:
            if rec["priority"] == "high":
                agent = await self._spawn_specialist(
                    rec["agent_type"],
                    rec["specialization"],
                    context,
                    f"Complex task requirement: {task_description[:100]}"
                )
                spawned_agents.append(agent)
        
        logger.info(f"🎯 Assembled team of {len(spawned_agents)} specialists for complex task")
        
        return spawned_agents
    
    async def evaluate_agent_ecosystem(self) -> Dict[str, Any]:
        """Evaluate the overall health of the agent ecosystem"""
        
        total_agents = len(self.active_agents)
        total_interactions = sum(
            len(agent.interaction_history) 
            for agent in self.active_agents.values()
        )
        
        # Calculate agent diversity
        agent_types = {}
        for agent in self.active_agents.values():
            agent_type = agent.spec.type.value
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
        
        diversity_score = len(agent_types) / len(AgentType) if total_agents > 0 else 0
        
        # Calculate activity score
        activity_score = min(1.0, total_interactions / (total_agents * 10)) if total_agents > 0 else 0
        
        # Get insights from discovery system
        discovery_insights = self.discovery_system.get_discovery_insights()
        
        ecosystem_health = {
            "total_agents": total_agents,
            "active_agents": len([a for a in self.active_agents.values() 
                                 if len(a.interaction_history) > 0]),
            "total_interactions": total_interactions,
            "diversity_score": diversity_score,
            "activity_score": activity_score,
            "agent_distribution": agent_types,
            "pending_requests": len(self.agent_requests),
            "spawn_history_count": len(self.spawn_history),
            "discovery_insights": discovery_insights,
            "health_score": (diversity_score + activity_score) / 2,
            "recommendations": []
        }
        
        # Generate recommendations
        if ecosystem_health["health_score"] < 0.5:
            ecosystem_health["recommendations"].append(
                "Consider spawning more diverse agents to improve coverage"
            )
        
        if activity_score < 0.3:
            ecosystem_health["recommendations"].append(
                "Low activity detected - agents may be underutilized"
            )
        
        if len(self.agent_requests) > 5:
            ecosystem_health["recommendations"].append(
                f"Process {len(self.agent_requests)} pending agent requests"
            )
        
        return ecosystem_health
    
    async def coordinate_multi_agent_task(
        self,
        task: str,
        required_agents: List[str],
        context: Dict
    ) -> Dict[str, Any]:
        """Coordinate a task requiring multiple specialized agents"""
        
        logger.info(f"🎭 Coordinating multi-agent task: {task[:100]}")
        
        # Ensure all required agents exist
        missing_agents = []
        for agent_spec in required_agents:
            if not any(agent_spec in agent_id for agent_id in self.active_agents):
                missing_agents.append(agent_spec)
        
        # Spawn missing agents
        if missing_agents:
            logger.info(f"📦 Spawning {len(missing_agents)} missing agents")
            for agent_spec in missing_agents:
                # Parse agent specification (e.g., "language_specialist:hebrew")
                if ":" in agent_spec:
                    agent_type, specialization = agent_spec.split(":", 1)
                else:
                    agent_type = "content_specialist"
                    specialization = agent_spec
                
                await self._spawn_specialist(
                    agent_type,
                    specialization,
                    context,
                    f"Required for task: {task[:50]}"
                )
        
        # Coordinate the agents
        coordination_result = {
            "task": task,
            "agents_involved": required_agents,
            "timestamp": datetime.now().isoformat(),
            "status": "coordinated"
        }
        
        return coordination_result
    
    def get_agent_by_specialization(
        self, 
        specialization: str
    ) -> Optional[DynamicAgent]:
        """Get an active agent by specialization"""
        
        for agent in self.active_agents.values():
            if specialization.lower() in agent.spec.specialization.lower():
                return agent
        return None
    
    def get_status_report(self) -> str:
        """Generate a status report of the meta-agent system"""
        
        report = f"""
        🧠 Meta-Agent Orchestrator Status
        ================================
        Active Agents: {len(self.active_agents)}
        Pending Requests: {len(self.agent_requests)}
        Total Spawned: {len(self.spawn_history)}
        Auto-Spawn Threshold: {self.auto_spawn_threshold}
        
        Agent Types Distribution:
        """
        
        agent_types = {}
        for agent in self.active_agents.values():
            agent_type = agent.spec.type.value
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
        
        for agent_type, count in agent_types.items():
            report += f"  - {agent_type}: {count}\n"
        
        if self.agent_requests:
            report += f"\nPending Requests:\n"
            for req in self.agent_requests[:5]:  # Show first 5
                report += f"  - {req.specialization} ({req.need_level.value})\n"
        
        return report