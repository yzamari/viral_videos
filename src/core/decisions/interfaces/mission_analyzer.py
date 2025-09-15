"""
Mission Analyzer Interface - Interface Segregation Principle

This interface defines the contract for mission analysis,
following ISP by separating mission analysis from other concerns.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MissionType(Enum):
    """Mission types for classification"""
    INFORM = "inform"
    PERSUADE = "persuade"
    ENTERTAIN = "entertain"
    EDUCATE = "educate"
    PROMOTE = "promote"


@dataclass
class MissionAnalysisResult:
    """Result of mission analysis - Value Object"""
    mission_type: MissionType
    is_strategic: bool
    confidence: float
    target_outcome: str
    strategic_approach: str
    success_metrics: list[str]
    content_strategy: Dict[str, Any]
    recommended_clips: int
    reasoning: str
    risk_assessment: Optional[Dict[str, Any]] = None


@dataclass
class CredibilityAnalysis:
    """Content credibility analysis result"""
    score: float
    level: str  # EXCELLENT, GOOD, QUESTIONABLE, POOR
    factual_claims: int
    bias_level: str
    reasoning: str
    recommendations: list[str]


@dataclass
class AudienceIntelligence:
    """Audience intelligence analysis result"""
    confidence: float
    primary_age_group: str
    engagement_prediction: float
    platform_suitability: Dict[str, float]
    optimization_recommendations: list[str]
    demographic_insights: Dict[str, Any]


@dataclass
class EthicalAssessment:
    """Ethical optimization assessment result"""
    rating: str  # EXCELLENT, GOOD, NEEDS_IMPROVEMENT, POOR
    compliance_score: float
    transparency_score: float
    educational_value: float
    positive_engagement: float
    recommendations: list[str]
    risk_factors: list[str]


class IMissionAnalyzer(ABC):
    """
    Interface for mission analysis following Interface Segregation Principle.
    
    Separated from decision-making to allow independent testing and evolution.
    """
    
    @abstractmethod
    def analyze_mission_type(self, mission: str) -> MissionAnalysisResult:
        """
        Analyze mission to determine type and strategic approach.
        
        Args:
            mission: Mission description to analyze
            
        Returns:
            MissionAnalysisResult: Comprehensive mission analysis
        """
        pass
    
    @abstractmethod
    def assess_content_credibility(self, content: str) -> CredibilityAnalysis:
        """
        Assess the credibility of content.
        
        Args:
            content: Content to assess
            
        Returns:
            CredibilityAnalysis: Credibility assessment result
        """
        pass
    
    @abstractmethod
    def analyze_audience_intelligence(self, mission: str, platform: str) -> AudienceIntelligence:
        """
        Analyze audience intelligence for mission and platform.
        
        Args:
            mission: Mission description
            platform: Target platform
            
        Returns:
            AudienceIntelligence: Audience analysis result
        """
        pass
    
    @abstractmethod
    def perform_ethical_assessment(self, mission: str) -> EthicalAssessment:
        """
        Perform ethical optimization assessment.
        
        Args:
            mission: Mission description to assess
            
        Returns:
            EthicalAssessment: Ethical assessment result
        """
        pass