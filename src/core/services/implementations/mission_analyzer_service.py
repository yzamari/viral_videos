"""
Mission Analyzer Service - Single Responsibility + Dependency Injection

This service implements the IMissionAnalyzer interface following SOLID principles.
It demonstrates proper separation of concerns and dependency injection.
"""

import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..interfaces.mission_analyzer import (
    IMissionAnalyzer,
    MissionAnalysisResult,
    MissionType,
    CredibilityAnalysis,
    AudienceIntelligence,
    EthicalAssessment
)
from ...frameworks.content_credibility_system import ContentCredibilitySystem
from ...frameworks.audience_intelligence_system import AudienceIntelligenceSystem
from ...frameworks.ethical_optimization_system import EthicalOptimizationSystem

logger = logging.getLogger(__name__)


class MissionAnalyzerService(IMissionAnalyzer):
    """
    Mission analyzer service following SOLID principles.
    
    Demonstrates:
    - SRP: Only responsible for mission analysis coordination
    - DIP: Depends on injected analysis systems, not concrete implementations
    - ISP: Uses focused interfaces for each analysis type
    - OCP: New analysis types can be added without modification
    """
    
    def __init__(self, 
                 api_key: str,
                 credibility_system: Optional[ContentCredibilitySystem] = None,
                 audience_system: Optional[AudienceIntelligenceSystem] = None,
                 ethical_system: Optional[EthicalOptimizationSystem] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize mission analyzer with dependency injection.
        
        Args:
            api_key: API key for AI services
            credibility_system: Content credibility analysis system (injected)
            audience_system: Audience intelligence system (injected)
            ethical_system: Ethical optimization system (injected)
            config: Configuration options
        """
        self.api_key = api_key
        self.config = config or {}
        
        # Dependency injection - systems can be mocked for testing
        self._credibility_system = credibility_system or ContentCredibilitySystem(api_key)
        self._audience_system = audience_system or AudienceIntelligenceSystem(api_key)
        self._ethical_system = ethical_system or EthicalOptimizationSystem(
            api_key, 
            timeout=self.config.get('ethical_timeout', 30)
        )
        
        # Performance optimization settings
        self._parallel_analysis = self.config.get('parallel_analysis', True)
        self._max_workers = self.config.get('max_workers', 3)
        
        logger.info("🎯 Mission Analyzer Service initialized (SOLID-compliant)")
    
    def analyze_mission_type(self, mission: str) -> MissionAnalysisResult:
        """
        Analyze mission to determine type and strategic approach.
        
        This method demonstrates SRP by focusing only on mission type analysis.
        
        Args:
            mission: Mission description to analyze
            
        Returns:
            MissionAnalysisResult: Comprehensive mission analysis
        """
        logger.info(f"🎯 Analyzing mission type: {mission[:50]}...")
        
        try:
            # Use the existing mission planning logic but in a focused way
            mission_type = self._classify_mission_type(mission)
            is_strategic = self._is_strategic_mission(mission, mission_type)
            
            # Generate strategic recommendations
            target_outcome = self._generate_target_outcome(mission, mission_type)
            strategic_approach = self._generate_strategic_approach(mission, mission_type)
            success_metrics = self._generate_success_metrics(mission_type)
            content_strategy = self._generate_content_strategy(mission, mission_type)
            
            # Calculate recommended clips based on mission complexity
            recommended_clips = self._calculate_recommended_clips(mission, mission_type)
            
            # Generate reasoning
            reasoning = self._generate_mission_reasoning(
                mission, mission_type, is_strategic
            )
            
            # Calculate confidence based on mission clarity
            confidence = self._calculate_mission_confidence(mission)
            
            result = MissionAnalysisResult(
                mission_type=mission_type,
                is_strategic=is_strategic,
                confidence=confidence,
                target_outcome=target_outcome,
                strategic_approach=strategic_approach,
                success_metrics=success_metrics,
                content_strategy=content_strategy,
                recommended_clips=recommended_clips,
                reasoning=reasoning
            )
            
            logger.info(
                f"✅ Mission analysis complete: {mission_type.value} "
                f"(strategic: {is_strategic}, confidence: {confidence:.2f})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Mission analysis failed: {e}")
            # Return default analysis rather than failing
            return self._create_default_mission_analysis(mission)
    
    def assess_content_credibility(self, content: str) -> CredibilityAnalysis:
        """
        Assess the credibility of content using injected credibility system.
        
        Args:
            content: Content to assess
            
        Returns:
            CredibilityAnalysis: Credibility assessment result
        """
        logger.info("🔍 Assessing content credibility...")
        
        try:
            # Use the injected credibility system
            result = self._credibility_system.evaluate_credibility(content)
            
            # Map to our standardized format
            credibility_analysis = CredibilityAnalysis(
                score=result.get('score', 0.0),
                level=result.get('level', 'UNKNOWN'),
                factual_claims=result.get('factual_claims', 0),
                bias_level=result.get('bias_level', 'UNKNOWN'),
                reasoning=result.get('reasoning', 'No analysis available'),
                recommendations=result.get('recommendations', [])
            )
            
            logger.info(
                f"✅ Credibility assessment complete: {credibility_analysis.score:.1f}/10 "
                f"({credibility_analysis.level})"
            )
            
            return credibility_analysis
            
        except Exception as e:
            logger.error(f"❌ Credibility assessment failed: {e}")
            return self._create_default_credibility_analysis()
    
    def analyze_audience_intelligence(self, mission: str, platform: str) -> AudienceIntelligence:
        """
        Analyze audience intelligence using injected audience system.
        
        Args:
            mission: Mission description
            platform: Target platform
            
        Returns:
            AudienceIntelligence: Audience analysis result
        """
        logger.info(f"🧠 Analyzing audience for {platform}...")
        
        try:
            # Use the injected audience system
            result = self._audience_system.analyze_audience(mission, platform)
            
            # Map to our standardized format
            audience_intelligence = AudienceIntelligence(
                confidence=result.get('confidence', 0.0),
                primary_age_group=result.get('primary_age_group', 'unknown'),
                engagement_prediction=result.get('engagement_prediction', 0.0),
                platform_suitability={platform: result.get('suitability_score', 0.5)},
                optimization_recommendations=result.get('recommendations', []),
                demographic_insights=result.get('demographic_data', {})
            )
            
            logger.info(
                f"✅ Audience analysis complete: {audience_intelligence.primary_age_group} "
                f"(confidence: {audience_intelligence.confidence:.2f})"
            )
            
            return audience_intelligence
            
        except Exception as e:
            logger.error(f"❌ Audience analysis failed: {e}")
            return self._create_default_audience_intelligence(platform)
    
    def perform_ethical_assessment(self, mission: str) -> EthicalAssessment:
        """
        Perform ethical optimization assessment using injected ethical system.
        
        Args:
            mission: Mission description to assess
            
        Returns:
            EthicalAssessment: Ethical assessment result
        """
        logger.info("🎯 Performing ethical assessment...")
        
        try:
            # Use the injected ethical system with timeout handling
            result = self._ethical_system.optimize_for_ethics(mission)
            
            # Map to our standardized format
            ethical_assessment = EthicalAssessment(
                rating=result.get('rating', 'UNKNOWN'),
                compliance_score=result.get('compliance_score', 0.0),
                transparency_score=result.get('transparency', 0.0),
                educational_value=result.get('educational_value', 0.0),
                positive_engagement=result.get('positive_engagement', 0.0),
                recommendations=result.get('recommendations', []),
                risk_factors=result.get('risk_factors', [])
            )
            
            logger.info(
                f"✅ Ethical assessment complete: {ethical_assessment.rating} "
                f"(score: {ethical_assessment.compliance_score:.1f}/10)"
            )
            
            return ethical_assessment
            
        except Exception as e:
            logger.error(f"❌ Ethical assessment failed: {e}")
            return self._create_default_ethical_assessment()
    
    def analyze_mission_comprehensive(self, mission: str, platform: str = 'tiktok') -> Dict[str, Any]:
        """
        Perform comprehensive mission analysis using all systems.
        
        This demonstrates how to coordinate multiple analysis systems
        while maintaining separation of concerns.
        
        Args:
            mission: Mission description
            platform: Target platform
            
        Returns:
            Dict[str, Any]: Comprehensive analysis results
        """
        logger.info(f"🚀 Starting comprehensive mission analysis...")
        
        if self._parallel_analysis:
            return self._analyze_parallel(mission, platform)
        else:
            return self._analyze_sequential(mission, platform)
    
    def _analyze_parallel(self, mission: str, platform: str) -> Dict[str, Any]:
        """Perform parallel analysis for better performance."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            # Submit all analysis tasks
            futures = {
                'mission_type': executor.submit(self.analyze_mission_type, mission),
                'credibility': executor.submit(self.assess_content_credibility, mission),
                'audience': executor.submit(self.analyze_audience_intelligence, mission, platform),
                'ethical': executor.submit(self.perform_ethical_assessment, mission)
            }
            
            # Collect results as they complete
            for future in as_completed(futures.values()):
                for analysis_type, task_future in futures.items():
                    if task_future == future:
                        try:
                            results[analysis_type] = future.result()
                        except Exception as e:
                            logger.error(f"Parallel analysis {analysis_type} failed: {e}")
                            results[analysis_type] = None
                        break
        
        return results
    
    def _analyze_sequential(self, mission: str, platform: str) -> Dict[str, Any]:
        """Perform sequential analysis."""
        return {
            'mission_type': self.analyze_mission_type(mission),
            'credibility': self.assess_content_credibility(mission),
            'audience': self.analyze_audience_intelligence(mission, platform),
            'ethical': self.perform_ethical_assessment(mission)
        }
    
    # Helper methods for mission type analysis
    def _classify_mission_type(self, mission: str) -> MissionType:
        """Classify mission type based on content analysis."""
        mission_lower = mission.lower()
        
        persuade_indicators = ['perspective', 'convince', 'persuade', 'support', 'advocate']
        inform_indicators = ['research', 'facts', 'information', 'explain', 'analyze']
        entertain_indicators = ['fun', 'entertaining', 'viral', 'engaging', 'humor']
        educate_indicators = ['learn', 'teach', 'educational', 'understand', 'knowledge']
        promote_indicators = ['promote', 'marketing', 'brand', 'product', 'service']
        
        # Count indicators for each type
        scores = {
            MissionType.PERSUADE: sum(1 for indicator in persuade_indicators if indicator in mission_lower),
            MissionType.INFORM: sum(1 for indicator in inform_indicators if indicator in mission_lower),
            MissionType.ENTERTAIN: sum(1 for indicator in entertain_indicators if indicator in mission_lower),
            MissionType.EDUCATE: sum(1 for indicator in educate_indicators if indicator in mission_lower),
            MissionType.PROMOTE: sum(1 for indicator in promote_indicators if indicator in mission_lower)
        }
        
        # Return type with highest score, default to INFORM
        return max(scores.keys(), key=lambda k: scores[k]) if max(scores.values()) > 0 else MissionType.INFORM
    
    def _is_strategic_mission(self, mission: str, mission_type: MissionType) -> bool:
        """Determine if mission is strategic based on content and type."""
        strategic_indicators = [
            'strategy', 'strategic', 'campaign', 'influence', 'impact',
            'viral', 'distribution', 'perspective', 'opinion'
        ]
        
        mission_lower = mission.lower()
        strategic_score = sum(1 for indicator in strategic_indicators if indicator in mission_lower)
        
        # PERSUADE missions are generally strategic
        return mission_type == MissionType.PERSUADE or strategic_score >= 2
    
    # Default/fallback creation methods
    def _create_default_mission_analysis(self, mission: str) -> MissionAnalysisResult:
        """Create default mission analysis when analysis fails."""
        return MissionAnalysisResult(
            mission_type=MissionType.INFORM,
            is_strategic=False,
            confidence=0.5,
            target_outcome="Create engaging content",
            strategic_approach="Standard content creation approach",
            success_metrics=["Views", "Engagement"],
            content_strategy={"approach": "general"},
            recommended_clips=2,
            reasoning="Default analysis due to processing error"
        )
    
    def _create_default_credibility_analysis(self) -> CredibilityAnalysis:
        """Create default credibility analysis when assessment fails."""
        return CredibilityAnalysis(
            score=5.0,
            level="UNKNOWN",
            factual_claims=0,
            bias_level="UNKNOWN",
            reasoning="Analysis unavailable due to processing error",
            recommendations=["Manual review recommended"]
        )
    
    def _create_default_audience_intelligence(self, platform: str) -> AudienceIntelligence:
        """Create default audience intelligence when analysis fails."""
        return AudienceIntelligence(
            confidence=0.5,
            primary_age_group="general",
            engagement_prediction=0.5,
            platform_suitability={platform: 0.5},
            optimization_recommendations=["Standard optimization"],
            demographic_insights={}
        )
    
    def _create_default_ethical_assessment(self) -> EthicalAssessment:
        """Create default ethical assessment when analysis fails."""
        return EthicalAssessment(
            rating="NEEDS_REVIEW",
            compliance_score=5.0,
            transparency_score=5.0,
            educational_value=5.0,
            positive_engagement=5.0,
            recommendations=["Manual ethical review recommended"],
            risk_factors=["Analysis unavailable"]
        )
    
    # Additional helper methods would go here...
    def _generate_target_outcome(self, mission: str, mission_type: MissionType) -> str:
        """Generate target outcome based on mission and type."""
        if mission_type == MissionType.PERSUADE:
            return "Achieve high engagement with positive sentiment toward the presented perspective"
        elif mission_type == MissionType.INFORM:
            return "Deliver clear, accurate information to target audience"
        elif mission_type == MissionType.ENTERTAIN:
            return "Maximize entertainment value and viral potential"
        elif mission_type == MissionType.EDUCATE:
            return "Enhance audience knowledge and understanding"
        else:
            return "Achieve platform-specific engagement goals"
    
    def _generate_strategic_approach(self, mission: str, mission_type: MissionType) -> str:
        """Generate strategic approach based on mission analysis."""
        base_approaches = {
            MissionType.PERSUADE: "Emotional storytelling with clear perspective",
            MissionType.INFORM: "Fact-based presentation with clear structure",
            MissionType.ENTERTAIN: "High-energy content with viral elements",
            MissionType.EDUCATE: "Step-by-step explanatory content",
            MissionType.PROMOTE: "Value-focused promotional messaging"
        }
        return base_approaches.get(mission_type, "Balanced content approach")
    
    def _generate_success_metrics(self, mission_type: MissionType) -> list[str]:
        """Generate success metrics based on mission type."""
        base_metrics = ["Views", "Engagement Rate", "Share Rate"]
        
        type_specific_metrics = {
            MissionType.PERSUADE: ["Sentiment Analysis", "Comment Sentiment"],
            MissionType.INFORM: ["Information Retention", "Fact Checking"],
            MissionType.ENTERTAIN: ["Viral Coefficient", "Repeat Views"],
            MissionType.EDUCATE: ["Knowledge Transfer", "Educational Impact"],
            MissionType.PROMOTE: ["Conversion Rate", "Brand Awareness"]
        }
        
        return base_metrics + type_specific_metrics.get(mission_type, [])
    
    def _generate_content_strategy(self, mission: str, mission_type: MissionType) -> Dict[str, Any]:
        """Generate content strategy based on mission analysis."""
        return {
            "main_approach": self._generate_strategic_approach(mission, mission_type),
            "content_type": mission_type.value,
            "tone": "engaging" if mission_type == MissionType.ENTERTAIN else "professional",
            "structure": "narrative" if mission_type == MissionType.PERSUADE else "informational"
        }
    
    def _calculate_recommended_clips(self, mission: str, mission_type: MissionType) -> int:
        """Calculate recommended number of clips based on mission complexity."""
        # Base clips by mission type
        base_clips = {
            MissionType.PERSUADE: 2,  # Setup + resolution
            MissionType.INFORM: 3,    # Intro + content + conclusion
            MissionType.ENTERTAIN: 2, # Hook + payoff
            MissionType.EDUCATE: 3,   # Intro + explanation + summary
            MissionType.PROMOTE: 2    # Problem + solution
        }
        
        # Adjust based on mission length/complexity
        mission_length = len(mission.split())
        complexity_bonus = 1 if mission_length > 20 else 0
        
        return base_clips.get(mission_type, 2) + complexity_bonus
    
    def _generate_mission_reasoning(self, mission: str, mission_type: MissionType, is_strategic: bool) -> str:
        """Generate human-readable reasoning for mission classification."""
        reasoning_parts = [
            f"Classified as {mission_type.value} mission",
            f"Strategic mission: {is_strategic}"
        ]
        
        if mission_type == MissionType.PERSUADE:
            reasoning_parts.append("Detected persuasive intent and perspective elements")
        
        if is_strategic:
            reasoning_parts.append("Contains strategic indicators for influence/impact")
        
        return ". ".join(reasoning_parts) + "."
    
    def _calculate_mission_confidence(self, mission: str) -> float:
        """Calculate confidence in mission analysis based on clarity."""
        # Base confidence
        confidence = 0.7
        
        # Bonus for clear mission structure
        if len(mission.split()) > 10:
            confidence += 0.1
        
        # Bonus for specific keywords
        specific_keywords = ['create', 'generate', 'make', 'produce', 'develop']
        if any(keyword in mission.lower() for keyword in specific_keywords):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"MissionAnalyzerService(parallel={self._parallel_analysis})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"MissionAnalyzerService(api_key='***', parallel={self._parallel_analysis}, config={self.config})"