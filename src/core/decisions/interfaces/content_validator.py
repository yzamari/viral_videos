"""
Content Validator Interface - Open/Closed Principle

This interface defines the contract for content validation,
following OCP by allowing extension without modification.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Individual validation issue - Value Object"""
    severity: ValidationSeverity
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Content validation result - Value Object"""
    is_valid: bool
    score: float  # 0.0 to 1.0
    issues: List[ValidationIssue]
    summary: str
    recommendations: List[str]
    metadata: Optional[Dict[str, Any]] = None


class IContentValidator(ABC):
    """
    Interface for content validation following Open/Closed Principle.
    
    New validation rules can be added without modifying existing validators.
    """
    
    @abstractmethod
    def validate(self, content: Dict[str, Any]) -> ValidationResult:
        """
        Validate content according to specific rules.
        
        Args:
            content: Content to validate
            
        Returns:
            ValidationResult: Validation result with issues and recommendations
        """
        pass
    
    @abstractmethod
    def can_validate(self, content_type: str) -> bool:
        """
        Check if this validator can validate the given content type.
        
        Args:
            content_type: Type of content to validate
            
        Returns:
            bool: True if validator can handle this content type
        """
        pass
    
    @property
    @abstractmethod
    def supported_content_types(self) -> List[str]:
        """
        Get list of supported content types.
        
        Returns:
            List[str]: Supported content types
        """
        pass
    
    @property
    @abstractmethod
    def validator_name(self) -> str:
        """
        Get the name of this validator.
        
        Returns:
            str: Validator name
        """
        pass