"""
Decision Strategy Interface - Single Responsibility Principle

This interface defines the contract for individual decision strategies,
following SRP by focusing only on making one type of decision.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class DecisionContext:
    """Context data for decision making - Value Object pattern"""
    mission: str
    platform: Optional[str] = None
    duration: Optional[int] = None
    target_audience: Optional[str] = None
    language: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    session_data: Optional[Dict[str, Any]] = None


@dataclass
class DecisionResult:
    """Result of a decision - Value Object pattern"""
    value: Any
    confidence: float
    source: str
    reasoning: Optional[str] = None
    alternatives: Optional[Dict[str, Any]] = None


class IDecisionStrategy(ABC):
    """
    Interface for decision strategies following Single Responsibility Principle.
    
    Each strategy is responsible for making ONE type of decision only.
    This follows SRP and enables easy testing and extension (OCP).
    """
    
    @abstractmethod
    def decide(self, context: DecisionContext) -> DecisionResult:
        """
        Make a specific decision based on the context.
        
        Args:
            context: Decision context with relevant data
            
        Returns:
            DecisionResult: The decision with confidence and reasoning
        """
        pass
    
    @abstractmethod
    def can_decide(self, context: DecisionContext) -> bool:
        """
        Check if this strategy can make a decision with the given context.
        
        Args:
            context: Decision context to evaluate
            
        Returns:
            bool: True if strategy can make decision, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def decision_type(self) -> str:
        """
        Get the type of decision this strategy handles.
        
        Returns:
            str: Decision type identifier (e.g., 'duration', 'platform', 'style')
        """
        pass
    
    @property
    @abstractmethod
    def required_context_fields(self) -> list[str]:
        """
        Get the required context fields for this decision.
        
        Returns:
            list[str]: List of required context field names
        """
        pass