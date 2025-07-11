"""
Agent orchestration use case for the AI Video Generator

This module contains the business logic for orchestrating AI agents
in the video generation process.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.agent_entity import AgentEntity, AgentType, AgentStatus
from ..entities.video_entity import VideoEntity
from ..entities.session_entity import SessionEntity
from ..interfaces.repositories import AgentRepository, VideoRepository, SessionRepository


class AgentOrchestrationUseCase:
    """
    Use case for orchestrating AI agents in video generation
    
    This class encapsulates all business logic related to agent coordination,
    assignment, and performance monitoring.
    """
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        video_repository: VideoRepository,
        session_repository: SessionRepository
    ):
        """
        Initialize agent orchestration use case
        
        Args:
            agent_repository: Repository for agent data
            video_repository: Repository for video data
            session_repository: Repository for session data
        """
        self.agent_repository = agent_repository
        self.video_repository = video_repository
        self.session_repository = session_repository
    
    async def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        expertise_level: float = 1.0,
        capabilities: Optional[List[str]] = None
    ) -> AgentEntity:
        """
        Create a new AI agent
        
        Args:
            name: Agent name
            agent_type: Type of agent
            expertise_level: Agent expertise level (0.0 to 1.0)
            capabilities: List of agent capabilities
            
        Returns:
            Created agent entity
        """
        # Generate agent ID
        agent_id = f"agent_{agent_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create agent entity
        agent = AgentEntity(
            id=agent_id,
            name=name,
            agent_type=agent_type,
            expertise_level=expertise_level,
            capabilities=capabilities or []
        )
        
        # Save agent
        await self.agent_repository.save(agent)
        
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[AgentEntity]:
        """
        Get agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent entity or None if not found
        """
        return await self.agent_repository.get_by_id(agent_id)
    
    async def get_available_agents(self) -> List[AgentEntity]:
        """
        Get all available agents
        
        Returns:
            List of available agent entities
        """
        return await self.agent_repository.list_available()
    
    async def assign_agent_to_video(
        self,
        agent_id: str,
        video_id: str,
        task_description: str
    ) -> AgentEntity:
        """
        Assign agent to a video generation task
        
        Args:
            agent_id: Agent ID
            video_id: Video ID
            task_description: Task description
            
        Returns:
            Updated agent entity
        """
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video not found: {video_id}")
        
        # Assign agent to video
        agent.assign_to_session(video.session_id, video_id)
        agent.start_task(task_description)
        
        # Save agent
        await self.agent_repository.save(agent)
        
        return agent
    
    async def get_best_agent_for_task(
        self,
        agent_type: AgentType,
        required_capabilities: Optional[List[str]] = None
    ) -> Optional[AgentEntity]:
        """
        Get the best available agent for a specific task
        
        Args:
            agent_type: Required agent type
            required_capabilities: Required capabilities
            
        Returns:
            Best available agent or None
        """
        available_agents = await self.get_available_agents()
        
        # Filter by agent type
        suitable_agents = [a for a in available_agents if a.agent_type == agent_type]
        
        # Filter by capabilities if specified
        if required_capabilities:
            suitable_agents = [
                a for a in suitable_agents
                if all(cap in a.capabilities for cap in required_capabilities)
            ]
        
        if not suitable_agents:
            return None
        
        # Sort by expertise level and success rate
        suitable_agents.sort(
            key=lambda a: (a.expertise_level, a.get_success_rate()),
            reverse=True
        )
        
        return suitable_agents[0]
    
    async def orchestrate_video_generation(
        self,
        video_id: str
    ) -> Dict[str, AgentEntity]:
        """
        Orchestrate agents for video generation
        
        Args:
            video_id: Video ID
            
        Returns:
            Dictionary mapping task names to assigned agents
        """
        video = await self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video not found: {video_id}")
        
        assigned_agents = {}
        
        # Define required agent types and tasks
        agent_tasks = [
            (AgentType.SCRIPT_WRITER, "Generate script content"),
            (AgentType.DIRECTOR, "Direct video production"),
            (AgentType.EDITOR, "Edit and compose final video"),
            (AgentType.SOUNDMAN, "Generate and manage audio")
        ]
        
        # Assign agents to tasks
        for agent_type, task_description in agent_tasks:
            agent = await self.get_best_agent_for_task(agent_type)
            
            if agent:
                assigned_agent = await self.assign_agent_to_video(
                    agent.id, video_id, task_description
                )
                assigned_agents[task_description] = assigned_agent
            else:
                # Create a new agent if none available
                agent = await self.create_agent(
                    name=f"Auto-{agent_type.value}",
                    agent_type=agent_type
                )
                assigned_agent = await self.assign_agent_to_video(
                    agent.id, video_id, task_description
                )
                assigned_agents[task_description] = assigned_agent
        
        return assigned_agents
    
    async def update_agent_progress(
        self,
        agent_id: str,
        progress: float,
        status_message: Optional[str] = None
    ) -> AgentEntity:
        """
        Update agent task progress
        
        Args:
            agent_id: Agent ID
            progress: Progress percentage (0.0 to 100.0)
            status_message: Optional status message
            
        Returns:
            Updated agent entity
        """
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent.update_task_progress(progress)
        if status_message:
            agent.current_task = status_message
        
        await self.agent_repository.save(agent)
        
        return agent
    
    async def complete_agent_task(
        self,
        agent_id: str,
        success: bool = True,
        result_data: Optional[Dict[str, Any]] = None
    ) -> AgentEntity:
        """
        Complete agent task
        
        Args:
            agent_id: Agent ID
            success: Whether task was successful
            result_data: Optional result data
            
        Returns:
            Updated agent entity
        """
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        if success:
            agent.complete_task()
        else:
            agent.fail_task("Task failed")
        
        # Record decision if result data provided
        if result_data:
            agent.make_decision(
                decision_type="task_completion",
                decision_data=result_data,
                confidence_score=1.0 if success else 0.0,
                reasoning=f"Task {'completed successfully' if success else 'failed'}"
            )
        
        await self.agent_repository.save(agent)
        
        return agent
    
    async def get_session_agents(self, session_id: str) -> List[AgentEntity]:
        """
        Get all agents assigned to a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of agent entities
        """
        return await self.agent_repository.list_by_session(session_id)
    
    async def get_agent_performance_stats(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Get agent performance statistics
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Performance statistics dictionary
        """
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "agent_type": agent.agent_type.value,
            "expertise_level": agent.expertise_level,
            "total_tasks": agent.total_tasks,
            "completed_tasks": agent.completed_tasks,
            "failed_tasks": agent.failed_tasks,
            "success_rate": agent.get_success_rate(),
            "total_decisions": agent.total_decisions,
            "successful_decisions": agent.successful_decisions,
            "decision_success_rate": agent.get_success_rate(),
            "average_confidence": agent.average_confidence_score,
            "current_status": agent.status.value,
            "current_task": agent.current_task,
            "current_progress": agent.current_task_progress,
            "created_at": agent.created_at.isoformat(),
            "last_active": agent.last_active.isoformat() if agent.last_active else None
        }
    
    async def release_agent(self, agent_id: str) -> AgentEntity:
        """
        Release agent from current assignment
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Updated agent entity
        """
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent.release()
        await self.agent_repository.save(agent)
        
        return agent
    
    async def get_orchestration_summary(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get orchestration summary for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Orchestration summary dictionary
        """
        agents = await self.get_session_agents(session_id)
        
        # Calculate summary statistics
        total_agents = len(agents)
        active_agents = sum(1 for a in agents if a.status == AgentStatus.WORKING)
        completed_agents = sum(1 for a in agents if a.status == AgentStatus.COMPLETED)
        failed_agents = sum(1 for a in agents if a.status == AgentStatus.FAILED)
        
        # Agent type distribution
        agent_types = {}
        for agent in agents:
            agent_type = agent.agent_type.value
            if agent_type not in agent_types:
                agent_types[agent_type] = 0
            agent_types[agent_type] += 1
        
        # Calculate average performance
        if agents:
            avg_expertise = sum(a.expertise_level for a in agents) / len(agents)
            avg_success_rate = sum(a.get_success_rate() for a in agents) / len(agents)
        else:
            avg_expertise = 0.0
            avg_success_rate = 0.0
        
        return {
            "session_id": session_id,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "completed_agents": completed_agents,
            "failed_agents": failed_agents,
            "idle_agents": total_agents - active_agents - completed_agents - failed_agents,
            "agent_type_distribution": agent_types,
            "average_expertise_level": avg_expertise,
            "average_success_rate": avg_success_rate,
            "orchestration_efficiency": (completed_agents / total_agents * 100) if total_agents > 0 else 0.0
        } 