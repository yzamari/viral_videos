"""
Decision Orchestrator Interface - Dependency Inversion Principle

This interface defines the contract for orchestrating multiple decision strategies,
following DIP by depending on abstractions rather than concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .decision_strategy import IDecisionStrategy, DecisionContext, DecisionResult


class IDecisionOrchestrator(ABC):
    """
    Interface for orchestrating decision-making processes.
    
    This follows the Dependency Inversion Principle by depending on
    IDecisionStrategy abstractions rather than concrete implementations.
    """
    
    @abstractmethod
    def register_strategy(self, strategy: IDecisionStrategy) -> None:
        """
        Register a decision strategy.
        
        Args:
            strategy: Decision strategy to register
        """
        pass
    
    @abstractmethod
    def make_decisions(self, context: DecisionContext) -> Dict[str, DecisionResult]:
        """
        Make all applicable decisions based on context.
        
        Args:
            context: Decision context with relevant data
            
        Returns:
            Dict[str, DecisionResult]: Map of decision type to result
        """
        pass
    
    @abstractmethod
    def make_decision(self, decision_type: str, context: DecisionContext) -> Optional[DecisionResult]:
        """
        Make a specific decision by type.
        
        Args:
            decision_type: Type of decision to make
            context: Decision context with relevant data
            
        Returns:
            Optional[DecisionResult]: Decision result or None if not available
        """
        pass
    
    @abstractmethod
    def get_available_decisions(self, context: DecisionContext) -> List[str]:
        """
        Get list of decisions that can be made with the given context.
        
        Args:
            context: Decision context to evaluate
            
        Returns:
            List[str]: List of available decision types
        """
        pass
    
    @abstractmethod
    def validate_context(self, context: DecisionContext) -> Dict[str, bool]:
        """
        Validate if context has required fields for each decision type.
        
        Args:
            context: Decision context to validate
            
        Returns:
            Dict[str, bool]: Map of decision type to validation result
        """
        pass