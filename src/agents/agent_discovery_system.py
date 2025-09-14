"""
Agent Discovery System - Intelligent Agent Need Detection
Analyzes tasks and context to identify when specialized agents are needed
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import json

from src.utils.ai_service_manager import AIServiceManager
from src.config.ai_model_config import DEFAULT_AI_MODEL
from src.agents.dynamic_agent_factory import (
    DynamicAgentFactory, 
    AgentType,
    DynamicAgent
)

logger = logging.getLogger(__name__)


@dataclass
class TaskAnalysis:
    """Analysis of a task's requirements"""
    complexity_score: float  # 0.0 to 1.0
    required_expertise: List[str]
    missing_capabilities: List[str]
    recommended_agents: List[Dict[str, Any]]
    confidence: float
    reasoning: str


@dataclass
class AgentGap:
    """Represents a gap in current agent capabilities"""
    capability_needed: str
    importance: float  # 0.0 to 1.0
    agent_type: AgentType
    specialization: str
    justification: str


class AgentDiscoverySystem:
    """System for discovering when new agents are needed"""
    
    def __init__(self):
        self.ai_service = AIServiceManager()
        self.agent_factory = DynamicAgentFactory()
        self.discovery_history: List[Dict] = []
        self.current_agents: Dict[str, Any] = {}
        self.capability_map: Dict[str, Set[str]] = self._initialize_capability_map()
        logger.info("🔍 Agent Discovery System initialized")
    
    def _initialize_capability_map(self) -> Dict[str, Set[str]]:
        """Initialize map of agent types to their typical capabilities"""
        return {
            "AudioMaster": {
                "audio_timing", "sound_design", "music_selection", 
                "voice_modulation", "audio_mixing"
            },
            "CutMaster": {
                "video_editing", "transition_design", "pacing_control",
                "scene_selection", "cut_timing"
            },
            "SyncMaster": {
                "synchronization", "coordination", "timing_alignment",
                "workflow_management", "quality_control"
            },
            "ScriptMaster": {
                "narrative_creation", "dialogue_writing", "story_structure",
                "content_adaptation", "tone_adjustment"
            },
            "VisionMaster": {
                "visual_composition", "cinematography", "color_theory",
                "scene_design", "visual_storytelling"
            },
            "DirectorOfPhotography": {
                "lighting_design", "camera_angles", "shot_composition",
                "visual_style", "technical_cinematography"
            },
            "Colorist": {
                "color_grading", "mood_creation", "visual_consistency",
                "color_correction", "atmosphere_design"
            }
        }
    
    async def analyze_task_requirements(
        self,
        task_description: str,
        context: Dict[str, Any],
        existing_agents: List[str]
    ) -> TaskAnalysis:
        """Analyze a task to determine agent requirements"""
        
        prompt = f"""
        Analyze this task to determine what expertise and agents are needed.
        
        Task: {task_description}
        Context: {json.dumps(context, indent=2)}
        Current Agents: {', '.join(existing_agents)}
        
        Known Agent Capabilities:
        {json.dumps({agent: list(caps) for agent, caps in self.capability_map.items()}, indent=2)}
        
        Provide a detailed analysis:
        {{
            "complexity_score": <0.0-1.0>,
            "required_expertise": ["expertise1", "expertise2", ...],
            "missing_capabilities": ["capability1", "capability2", ...],
            "recommended_agents": [
                {{
                    "type": "agent_type",
                    "specialization": "specific_area",
                    "priority": "high/medium/low",
                    "reason": "why_needed"
                }}
            ],
            "confidence": <0.0-1.0>,
            "reasoning": "detailed explanation"
        }}
        """
        
        analysis_data = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.5
        )
        
        analysis = TaskAnalysis(
            complexity_score=analysis_data.get("complexity_score", 0.5),
            required_expertise=analysis_data.get("required_expertise", []),
            missing_capabilities=analysis_data.get("missing_capabilities", []),
            recommended_agents=analysis_data.get("recommended_agents", []),
            confidence=analysis_data.get("confidence", 0.7),
            reasoning=analysis_data.get("reasoning", "")
        )
        
        # Log the discovery
        self.discovery_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": task_description,
            "analysis": analysis.__dict__
        })
        
        return analysis
    
    async def identify_agent_gaps(
        self,
        required_capabilities: List[str],
        existing_agents: Dict[str, List[str]]
    ) -> List[AgentGap]:
        """Identify gaps between required and existing agent capabilities"""
        
        # Collect all existing capabilities
        existing_capabilities = set()
        for agent_name, capabilities in existing_agents.items():
            existing_capabilities.update(capabilities)
        
        # Identify missing capabilities
        missing = set(required_capabilities) - existing_capabilities
        
        if not missing:
            return []
        
        # Analyze each missing capability
        gaps = []
        for capability in missing:
            gap = await self._analyze_capability_gap(
                capability,
                existing_capabilities
            )
            if gap:
                gaps.append(gap)
        
        # Sort by importance
        gaps.sort(key=lambda g: g.importance, reverse=True)
        
        return gaps
    
    async def _analyze_capability_gap(
        self,
        capability: str,
        existing_capabilities: Set[str]
    ) -> Optional[AgentGap]:
        """Analyze a specific capability gap"""
        
        prompt = f"""
        Analyze this missing capability and recommend an agent to provide it.
        
        Missing Capability: {capability}
        Existing Capabilities: {', '.join(existing_capabilities)}
        
        Agent Types Available:
        {', '.join([t.value for t in AgentType])}
        
        Provide recommendation:
        {{
            "importance": <0.0-1.0>,
            "agent_type": "<from available types>",
            "specialization": "<specific expertise area>",
            "justification": "<why this agent is needed>"
        }}
        """
        
        recommendation = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.5
        )
        
        if recommendation:
            return AgentGap(
                capability_needed=capability,
                importance=recommendation.get("importance", 0.5),
                agent_type=AgentType(recommendation.get("agent_type", "content_specialist")),
                specialization=recommendation.get("specialization", capability),
                justification=recommendation.get("justification", "")
            )
        
        return None
    
    async def recommend_dynamic_agents(
        self,
        task: str,
        context: Dict,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Recommend dynamic agents for a task"""
        
        # Get current agents
        existing_agents = list(self.current_agents.keys())
        
        # Analyze task requirements
        analysis = await self.analyze_task_requirements(
            task, 
            context, 
            existing_agents
        )
        
        # Filter recommendations by confidence threshold
        recommendations = []
        for agent_rec in analysis.recommended_agents:
            if analysis.confidence >= threshold:
                recommendations.append({
                    "agent_type": agent_rec.get("type"),
                    "specialization": agent_rec.get("specialization"),
                    "priority": agent_rec.get("priority"),
                    "reason": agent_rec.get("reason"),
                    "confidence": analysis.confidence
                })
        
        logger.info(f"📊 Task complexity: {analysis.complexity_score:.2f}")
        logger.info(f"🎯 Recommended {len(recommendations)} dynamic agents")
        
        return recommendations
    
    async def spawn_recommended_agents(
        self,
        recommendations: List[Dict[str, Any]],
        context: Dict,
        auto_spawn_threshold: float = 0.8
    ) -> List[DynamicAgent]:
        """Spawn recommended agents based on confidence threshold"""
        
        spawned_agents = []
        
        for rec in recommendations:
            # Auto-spawn high-confidence recommendations
            if rec["confidence"] >= auto_spawn_threshold:
                logger.info(f"🤖 Auto-spawning {rec['specialization']} agent")
                
                agent = await self.agent_factory.create_agent(
                    agent_type=AgentType[rec["agent_type"].upper()],
                    specialization=rec["specialization"],
                    context=context
                )
                
                spawned_agents.append(agent)
                
                # Update current agents
                self.current_agents[agent.spec.name] = agent.spec.capabilities
            
            else:
                logger.info(f"⚠️ Manual approval needed for {rec['specialization']} "
                          f"(confidence: {rec['confidence']:.2f})")
        
        return spawned_agents
    
    async def monitor_agent_effectiveness(
        self,
        agent: DynamicAgent,
        task_results: Dict
    ) -> Dict[str, Any]:
        """Monitor how effective a spawned agent was"""
        
        prompt = f"""
        Evaluate the effectiveness of this dynamically spawned agent.
        
        Agent: {agent.spec.name}
        Type: {agent.spec.type.value}
        Specialization: {agent.spec.specialization}
        Capabilities: {', '.join(agent.spec.capabilities)}
        
        Task Results:
        {json.dumps(task_results, indent=2)}
        
        Agent Interaction History:
        {json.dumps(agent.interaction_history[-5:], indent=2)}
        
        Evaluate:
        {{
            "effectiveness_score": <0.0-1.0>,
            "value_added": "<description of value provided>",
            "redundancy_score": <0.0-1.0>,
            "recommendation": "keep/adjust/remove",
            "learnings": ["learning1", "learning2"],
            "future_spawn_probability": <0.0-1.0>
        }}
        """
        
        evaluation = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.4
        )
        
        # Store learnings for future decisions
        self._update_learning_database(agent.spec, evaluation)
        
        return evaluation
    
    def _update_learning_database(
        self,
        agent_spec: Any,
        evaluation: Dict
    ):
        """Update learning database with agent effectiveness data"""
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": agent_spec.type.value,
            "specialization": agent_spec.specialization,
            "effectiveness": evaluation.get("effectiveness_score", 0),
            "learnings": evaluation.get("learnings", [])
        }
        
        # In production, this would persist to a database
        self.discovery_history.append({"type": "learning", "data": learning_entry})
    
    async def suggest_agent_evolution(
        self,
        current_agents: List[DynamicAgent],
        performance_data: Dict
    ) -> List[Dict[str, Any]]:
        """Suggest how agents should evolve based on performance"""
        
        prompt = f"""
        Based on performance data, suggest how our agent pool should evolve.
        
        Current Dynamic Agents:
        {json.dumps([{
            "name": agent.spec.name,
            "type": agent.spec.type.value,
            "specialization": agent.spec.specialization
        } for agent in current_agents], indent=2)}
        
        Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        Suggest evolution:
        {{
            "agents_to_add": [
                {{
                    "type": "agent_type",
                    "specialization": "area",
                    "reason": "why_needed"
                }}
            ],
            "agents_to_modify": [
                {{
                    "current_name": "name",
                    "suggested_changes": ["change1", "change2"],
                    "reason": "why_modify"
                }}
            ],
            "agents_to_remove": [
                {{
                    "name": "agent_name",
                    "reason": "why_remove"
                }}
            ],
            "overall_strategy": "strategic recommendation"
        }}
        """
        
        evolution_plan = await self.ai_service.generate_json(
            prompt=prompt,
            model=DEFAULT_AI_MODEL,
            temperature=0.6
        )
        
        return evolution_plan
    
    def get_discovery_insights(self) -> Dict[str, Any]:
        """Get insights from discovery history"""
        
        if not self.discovery_history:
            return {"status": "no_history"}
        
        # Analyze patterns in discovery history
        total_discoveries = len(self.discovery_history)
        
        # Count agent type recommendations
        agent_type_counts = {}
        for entry in self.discovery_history:
            if "analysis" in entry and "recommended_agents" in entry["analysis"]:
                for agent in entry["analysis"]["recommended_agents"]:
                    agent_type = agent.get("type", "unknown")
                    agent_type_counts[agent_type] = agent_type_counts.get(agent_type, 0) + 1
        
        # Find most common missing capabilities
        missing_capabilities = {}
        for entry in self.discovery_history:
            if "analysis" in entry and "missing_capabilities" in entry["analysis"]:
                for cap in entry["analysis"]["missing_capabilities"]:
                    missing_capabilities[cap] = missing_capabilities.get(cap, 0) + 1
        
        return {
            "total_discoveries": total_discoveries,
            "most_needed_agents": sorted(
                agent_type_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            "common_missing_capabilities": sorted(
                missing_capabilities.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "discovery_timeline": [
                {
                    "timestamp": entry.get("timestamp"),
                    "task": entry.get("task", "")[:100]
                }
                for entry in self.discovery_history[-10:]
            ]
        }