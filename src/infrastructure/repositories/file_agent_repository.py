"""
File-based agent repository implementation
"""

import json
from typing import Optional, List
from pathlib import Path

from ...core.interfaces.repositories import AgentRepository
from ...core.entities.agent_entity import AgentEntity, AgentStatus


class FileAgentRepository(AgentRepository):
    """
    File-based implementation of AgentRepository
    
    Stores agent entities as JSON files in a directory structure
    """
    
    def __init__(self, base_path: str = "data/agents"):
        """
        Initialize repository with base path
        
        Args:
            base_path: Base directory for storing agent files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save(self, agent: AgentEntity) -> None:
        """Save an agent entity to file"""
        agent_file = self.base_path / f"{agent.id}.json"
        
        # Convert entity to dictionary
        agent_data = agent.to_dict()
        
        # Save to file
        with open(agent_file, 'w', encoding='utf-8') as f:
            json.dump(agent_data, f, indent=2, ensure_ascii=False)
    
    async def get_by_id(self, agent_id: str) -> Optional[AgentEntity]:
        """Get agent by ID from file"""
        agent_file = self.base_path / f"{agent_id}.json"
        
        if not agent_file.exists():
            return None
        
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            
            return AgentEntity.from_dict(agent_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log error but don't raise - return None for invalid data
            print(f"Error loading agent {agent_id}: {e}")
            return None
    
    async def list_available(self) -> List[AgentEntity]:
        """List available agents"""
        agents = []
        
        # Iterate through all agent files
        for agent_file in self.base_path.glob("*.json"):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                # Check if agent is available
                if agent_data.get("status") == AgentStatus.IDLE.value:
                    agent = AgentEntity.from_dict(agent_data)
                    agents.append(agent)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by expertise level (highest first)
        agents.sort(key=lambda a: a.expertise_level, reverse=True)
        return agents
    
    async def list_by_session(self, session_id: str) -> List[AgentEntity]:
        """List agents by session ID"""
        agents = []
        
        # Iterate through all agent files
        for agent_file in self.base_path.glob("*.json"):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                # Check if agent belongs to session
                if agent_data.get("session_id") == session_id:
                    agent = AgentEntity.from_dict(agent_data)
                    agents.append(agent)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by agent type and name
        agents.sort(key=lambda a: (a.agent_type.value, a.name))
        return agents
    
    async def delete(self, agent_id: str) -> None:
        """Delete an agent file"""
        agent_file = self.base_path / f"{agent_id}.json"
        
        if agent_file.exists():
            agent_file.unlink()
    
    async def list_all(self) -> List[AgentEntity]:
        """List all agents"""
        agents = []
        
        # Iterate through all agent files
        for agent_file in self.base_path.glob("*.json"):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                agent = AgentEntity.from_dict(agent_data)
                agents.append(agent)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by agent type and name
        agents.sort(key=lambda a: (a.agent_type.value, a.name))
        return agents
    
    async def list_by_status(self, status: AgentStatus) -> List[AgentEntity]:
        """List agents by status (additional method)"""
        agents = []
        
        # Iterate through all agent files
        for agent_file in self.base_path.glob("*.json"):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                # Check if agent has the specified status
                if agent_data.get("status") == status.value:
                    agent = AgentEntity.from_dict(agent_data)
                    agents.append(agent)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue
        
        # Sort by agent type and name
        agents.sort(key=lambda a: (a.agent_type.value, a.name))
        return agents
    
    def get_storage_path(self) -> str:
        """Get the storage path for this repository"""
        return str(self.base_path)
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up old agent files
        
        Args:
            days: Number of days to keep files
            
        Returns:
            Number of files cleaned up
        """
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned_count = 0
        
        for agent_file in self.base_path.glob("*.json"):
            if agent_file.stat().st_mtime < cutoff_time:
                agent_file.unlink()
                cleaned_count += 1
        
        return cleaned_count 