"""
Service Factory - Factory Pattern + Dependency Injection

This factory demonstrates proper SOLID principles in service creation:
- SRP: Only responsible for service instantiation
- DIP: Uses dependency injection for configuration
- OCP: New services can be added without modification
"""

import logging
from typing import Dict, Any, Optional, Type
from .interfaces.mission_analyzer import IMissionAnalyzer
from .implementations.mission_analyzer_service import MissionAnalyzerService
from ..decisions.orchestrator import DecisionOrchestrator
from ..decisions.strategies.duration_decision_strategy import DurationDecisionStrategy
from ...frameworks.content_credibility_system import ContentCredibilitySystem
from ...frameworks.audience_intelligence_system import AudienceIntelligenceSystem
from ...frameworks.ethical_optimization_system import EthicalOptimizationSystem

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating services with proper dependency injection.
    
    This demonstrates:
    - Factory Pattern for service creation
    - Dependency Injection for configuration
    - SOLID principles in service architecture
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize service factory with configuration."""
        self.config = config or {}
        self._service_cache: Dict[str, Any] = {}
        self._enable_caching = self.config.get('enable_service_caching', True)
        
        logger.info("🏭 Service Factory initialized (SOLID-compliant)")
    
    def create_mission_analyzer(self, api_key: str, 
                               service_config: Optional[Dict[str, Any]] = None) -> IMissionAnalyzer:
        """
        Create mission analyzer service with proper dependency injection.
        
        Args:
            api_key: API key for AI services
            service_config: Service-specific configuration
            
        Returns:
            IMissionAnalyzer: Mission analyzer service instance
        """
        cache_key = f"mission_analyzer_{hash(api_key)}"
        
        if self._enable_caching and cache_key in self._service_cache:
            logger.debug("📦 Returning cached mission analyzer service")
            return self._service_cache[cache_key]
        
        config = dict(self.config)
        if service_config:
            config.update(service_config)
        
        # Create dependency services with proper configuration
        credibility_system = self._create_credibility_system(api_key, config)
        audience_system = self._create_audience_system(api_key, config)
        ethical_system = self._create_ethical_system(api_key, config)
        
        # Create mission analyzer with injected dependencies
        mission_analyzer = MissionAnalyzerService(
            api_key=api_key,
            credibility_system=credibility_system,
            audience_system=audience_system,
            ethical_system=ethical_system,
            config=config
        )
        
        if self._enable_caching:
            self._service_cache[cache_key] = mission_analyzer
        
        logger.info("✅ Created mission analyzer service with dependency injection")
        return mission_analyzer
    
    def create_decision_orchestrator(self, 
                                   service_config: Optional[Dict[str, Any]] = None) -> DecisionOrchestrator:
        """
        Create decision orchestrator with registered strategies.
        
        Args:
            service_config: Service-specific configuration
            
        Returns:
            DecisionOrchestrator: Configured decision orchestrator
        """
        cache_key = "decision_orchestrator"
        
        if self._enable_caching and cache_key in self._service_cache:
            logger.debug("📦 Returning cached decision orchestrator")
            return self._service_cache[cache_key]
        
        config = dict(self.config)
        if service_config:
            config.update(service_config)
        
        # Create orchestrator
        orchestrator = DecisionOrchestrator(config)
        
        # Register standard strategies
        self._register_standard_strategies(orchestrator, config)
        
        if self._enable_caching:
            self._service_cache[cache_key] = orchestrator
        
        logger.info("✅ Created decision orchestrator with registered strategies")
        return orchestrator
    
    def create_integrated_framework(self, api_key: str, 
                                  framework_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create integrated framework with all services properly wired.
        
        This demonstrates how to compose complex systems using SOLID principles.
        
        Args:
            api_key: API key for AI services
            framework_config: Framework-specific configuration
            
        Returns:
            Dict[str, Any]: Integrated framework components
        """
        config = dict(self.config)
        if framework_config:
            config.update(framework_config)
        
        logger.info("🚀 Creating integrated SOLID-compliant framework...")
        
        # Create core services
        mission_analyzer = self.create_mission_analyzer(api_key, config.get('mission_analyzer'))
        decision_orchestrator = self.create_decision_orchestrator(config.get('decision_orchestrator'))
        
        # Create supporting services
        credibility_system = self._create_credibility_system(api_key, config)
        audience_system = self._create_audience_system(api_key, config)
        ethical_system = self._create_ethical_system(api_key, config)
        
        framework = {
            'mission_analyzer': mission_analyzer,
            'decision_orchestrator': decision_orchestrator,
            'credibility_system': credibility_system,
            'audience_system': audience_system,
            'ethical_system': ethical_system,
            'config': config
        }
        
        logger.info("✅ Integrated framework created successfully")
        return framework
    
    def _create_credibility_system(self, api_key: str, config: Dict[str, Any]) -> ContentCredibilitySystem:
        """Create content credibility system with configuration."""
        return ContentCredibilitySystem(api_key)
    
    def _create_audience_system(self, api_key: str, config: Dict[str, Any]) -> AudienceIntelligenceSystem:
        """Create audience intelligence system with configuration."""
        return AudienceIntelligenceSystem(api_key)
    
    def _create_ethical_system(self, api_key: str, config: Dict[str, Any]) -> EthicalOptimizationSystem:
        """Create ethical optimization system with timeout configuration."""
        timeout = config.get('ethical_timeout', 30)
        return EthicalOptimizationSystem(api_key, timeout=timeout)
    
    def _register_standard_strategies(self, orchestrator: DecisionOrchestrator, 
                                    config: Dict[str, Any]) -> None:
        """
        Register standard decision strategies with the orchestrator.
        
        Args:
            orchestrator: Decision orchestrator to configure
            config: Configuration for strategies
        """
        # Register duration strategy
        duration_strategy = DurationDecisionStrategy(config.get('duration_strategy'))
        orchestrator.register_strategy(duration_strategy)
        
        # Additional strategies would be registered here
        # This demonstrates OCP - new strategies can be added without modification
        
        logger.info(f"✅ Registered {len(orchestrator.registered_strategies)} decision strategies")
    
    def clear_cache(self) -> None:
        """Clear service cache for testing or memory management."""
        self._service_cache.clear()
        logger.info("🧹 Service cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached services."""
        return {
            'enabled': self._enable_caching,
            'cached_services': list(self._service_cache.keys()),
            'cache_size': len(self._service_cache)
        }
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"ServiceFactory(caching={self._enable_caching}, services={len(self._service_cache)})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"ServiceFactory(config={self.config}, cache={self.get_cache_info()})"