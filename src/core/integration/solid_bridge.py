"""
SOLID Architecture Bridge - Migration Pattern

This bridge demonstrates how to integrate SOLID-compliant architecture
with existing legacy code during a gradual migration.
"""

import logging
from typing import Dict, Any, Optional
from ..decisions.interfaces.decision_strategy import DecisionContext, DecisionResult
from ..decisions.orchestrator import DecisionOrchestrator
from ..services.interfaces.mission_analyzer import IMissionAnalyzer
from ..services.service_factory import ServiceFactory
from ...utils.session_context import SessionContext

logger = logging.getLogger(__name__)


class SOLIDBridge:
    """
    Bridge between SOLID-compliant architecture and legacy DecisionFramework.
    
    This class demonstrates:
    - Bridge Pattern for legacy integration
    - Adapter Pattern for interface compatibility
    - Strategy Pattern for gradual migration
    - Facade Pattern for simplified access
    """
    
    def __init__(self, api_key: str, session_context: SessionContext, 
                 config: Optional[Dict[str, Any]] = None):
        """Initialize SOLID bridge with legacy compatibility."""
        self.api_key = api_key
        self.session_context = session_context
        self.config = config or {}
        
        # Initialize SOLID services
        self._service_factory = ServiceFactory(self.config.get('service_factory', {}))
        self._mission_analyzer = self._service_factory.create_mission_analyzer(
            api_key, self.config.get('mission_analyzer', {})
        )
        self._decision_orchestrator = self._service_factory.create_decision_orchestrator(
            self.config.get('decision_orchestrator', {})
        )
        
        # Migration flags
        self._use_solid_decisions = self.config.get('use_solid_decisions', True)
        self._use_solid_mission_analysis = self.config.get('use_solid_mission_analysis', True)
        self._fallback_to_legacy = self.config.get('fallback_to_legacy', True)
        
        logger.info("🌉 SOLID Bridge initialized (hybrid architecture)")
        logger.info(f"   SOLID decisions: {self._use_solid_decisions}")
        logger.info(f"   SOLID mission analysis: {self._use_solid_mission_analysis}")
        logger.info(f"   Legacy fallback: {self._fallback_to_legacy}")
    
    def make_core_decisions(self, mission: str, platform: str = 'tiktok', 
                           duration: Optional[int] = None, 
                           **kwargs) -> Dict[str, Any]:
        """
        Make core decisions using SOLID architecture with legacy fallback.
        
        Args:
            mission: Mission description
            platform: Target platform
            duration: Requested duration
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Decision results
        """
        logger.info("🎯 Making core decisions using SOLID architecture...")
        
        try:
            if self._use_solid_decisions:
                return self._make_solid_decisions(mission, platform, duration, **kwargs)
            else:
                return self._make_legacy_decisions(mission, platform, duration, **kwargs)
                
        except Exception as e:
            logger.error(f"❌ SOLID decision making failed: {e}")
            
            if self._fallback_to_legacy:
                logger.info("🔄 Falling back to legacy decision framework...")
                return self._make_legacy_decisions(mission, platform, duration, **kwargs)
            else:
                raise
    
    def analyze_mission_comprehensive(self, mission: str, platform: str = 'tiktok') -> Dict[str, Any]:
        """
        Perform comprehensive mission analysis using SOLID architecture.
        
        Args:
            mission: Mission description
            platform: Target platform
            
        Returns:
            Dict[str, Any]: Mission analysis results
        """
        logger.info("🔍 Performing comprehensive mission analysis...")
        
        try:
            if self._use_solid_mission_analysis:
                return self._analyze_mission_solid(mission, platform)
            else:
                return self._analyze_mission_legacy(mission, platform)
                
        except Exception as e:
            logger.error(f"❌ SOLID mission analysis failed: {e}")
            
            if self._fallback_to_legacy:
                logger.info("🔄 Falling back to legacy mission analysis...")
                return self._analyze_mission_legacy(mission, platform)
            else:
                raise
    
    def create_decision_context(self, mission: str, platform: str = 'tiktok',
                              duration: Optional[int] = None, 
                              target_audience: Optional[str] = None,
                              language: Optional[str] = None,
                              **kwargs) -> DecisionContext:
        """
        Create decision context for SOLID decision making.
        
        Args:
            mission: Mission description
            platform: Target platform
            duration: Requested duration
            target_audience: Target audience
            language: Content language
            **kwargs: Additional context data
            
        Returns:
            DecisionContext: Context for decision making
        """
        # Merge configuration
        context_config = dict(self.config)
        context_config.update(kwargs.get('config', {}))
        
        # Create session data
        session_data = {
            'session_id': self.session_context.session_id,
            'session_dir': str(self.session_context.session_dir),
            'timestamp': str(self.session_context.session_dir.name)
        }
        session_data.update(kwargs.get('session_data', {}))
        
        return DecisionContext(
            mission=mission,
            platform=platform,
            duration=duration,
            target_audience=target_audience,
            language=language,
            config=context_config,
            session_data=session_data
        )
    
    def _make_solid_decisions(self, mission: str, platform: str, 
                            duration: Optional[int], **kwargs) -> Dict[str, Any]:
        """Make decisions using SOLID architecture."""
        # Create decision context
        context = self.create_decision_context(
            mission, platform, duration, 
            kwargs.get('target_audience'),
            kwargs.get('language'),
            **kwargs
        )
        
        # Make decisions using orchestrator
        decision_results = self._decision_orchestrator.make_decisions(context)
        
        # Convert to legacy format for compatibility
        legacy_format = self._convert_decisions_to_legacy_format(decision_results, context)
        
        # Add SOLID metadata
        legacy_format['solid_metadata'] = {
            'architecture': 'SOLID-compliant',
            'decision_count': len(decision_results),
            'available_decisions': self._decision_orchestrator.get_available_decisions(context),
            'strategy_info': self._decision_orchestrator.get_strategy_info()
        }
        
        return legacy_format
    
    def _analyze_mission_solid(self, mission: str, platform: str) -> Dict[str, Any]:
        """Analyze mission using SOLID architecture."""
        # Perform comprehensive analysis
        analysis_results = self._mission_analyzer.analyze_mission_comprehensive(mission, platform)
        
        # Convert to legacy format for compatibility
        legacy_format = self._convert_analysis_to_legacy_format(analysis_results)
        
        # Add SOLID metadata
        legacy_format['solid_metadata'] = {
            'architecture': 'SOLID-compliant',
            'analysis_types': list(analysis_results.keys()),
            'service_type': type(self._mission_analyzer).__name__
        }
        
        return legacy_format
    
    def _make_legacy_decisions(self, mission: str, platform: str, 
                             duration: Optional[int], **kwargs) -> Dict[str, Any]:
        """Make decisions using legacy DecisionFramework."""
        # Import legacy framework
        from ...decision_framework import DecisionFramework
        
        # Create legacy framework
        legacy_framework = DecisionFramework(
            session_context=self.session_context,
            config=self.config.get('legacy_framework', {})
        )
        
        # Make legacy decisions
        legacy_decisions = legacy_framework.make_all_core_decisions(
            mission=mission,
            platform=platform,
            duration_seconds=duration,
            **kwargs
        )
        
        # Add legacy metadata
        legacy_decisions['legacy_metadata'] = {
            'architecture': 'Legacy',
            'framework_type': 'DecisionFramework'
        }
        
        return legacy_decisions
    
    def _analyze_mission_legacy(self, mission: str, platform: str) -> Dict[str, Any]:
        """Analyze mission using legacy mission planning agent."""
        # Import legacy components
        from ...agents.mission_planning_agent import MissionPlanningAgent
        
        # Create legacy mission planner
        mission_planner = MissionPlanningAgent(
            api_key=self.api_key,
            config=self.config.get('legacy_mission_planner', {})
        )
        
        # Perform legacy analysis
        legacy_analysis = mission_planner.create_strategic_mission_plan(
            mission, platform
        )
        
        # Add legacy metadata
        legacy_analysis['legacy_metadata'] = {
            'architecture': 'Legacy',
            'agent_type': 'MissionPlanningAgent'
        }
        
        return legacy_analysis
    
    def _convert_decisions_to_legacy_format(self, decision_results: Dict[str, DecisionResult], 
                                          context: DecisionContext) -> Dict[str, Any]:
        """Convert SOLID decision results to legacy format."""
        legacy_format = {
            'success': True,
            'decisions': {},
            'confidence_scores': {},
            'reasoning': {},
            'context': {
                'mission': context.mission,
                'platform': context.platform,
                'duration': context.duration
            }
        }
        
        for decision_type, result in decision_results.items():
            legacy_format['decisions'][decision_type] = result.value
            legacy_format['confidence_scores'][decision_type] = result.confidence
            legacy_format['reasoning'][decision_type] = result.reasoning
        
        return legacy_format
    
    def _convert_analysis_to_legacy_format(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SOLID analysis results to legacy format."""
        legacy_format = {
            'success': True,
            'mission_analysis': analysis_results.get('mission_type'),
            'credibility_analysis': analysis_results.get('credibility'),
            'audience_analysis': analysis_results.get('audience'),
            'ethical_analysis': analysis_results.get('ethical'),
            'comprehensive': True
        }
        
        return legacy_format
    
    def get_architecture_info(self) -> Dict[str, Any]:
        """Get information about the current architecture configuration."""
        return {
            'solid_decisions_enabled': self._use_solid_decisions,
            'solid_mission_analysis_enabled': self._use_solid_mission_analysis,
            'legacy_fallback_enabled': self._fallback_to_legacy,
            'registered_strategies': self._decision_orchestrator.registered_strategies,
            'service_factory_cache': self._service_factory.get_cache_info(),
            'bridge_config': self.config
        }
    
    def enable_solid_mode(self) -> None:
        """Enable full SOLID mode for all operations."""
        self._use_solid_decisions = True
        self._use_solid_mission_analysis = True
        logger.info("✅ Enabled full SOLID mode")
    
    def enable_legacy_mode(self) -> None:
        """Enable legacy mode for all operations."""
        self._use_solid_decisions = False
        self._use_solid_mission_analysis = False
        logger.info("✅ Enabled legacy mode")
    
    def enable_hybrid_mode(self) -> None:
        """Enable hybrid mode with SOLID primary and legacy fallback."""
        self._use_solid_decisions = True
        self._use_solid_mission_analysis = True
        self._fallback_to_legacy = True
        logger.info("✅ Enabled hybrid mode (SOLID + legacy fallback)")
    
    def __str__(self) -> str:
        """String representation for debugging."""
        mode = "SOLID" if self._use_solid_decisions else "Legacy"
        fallback = " + Fallback" if self._fallback_to_legacy else ""
        return f"SOLIDBridge(mode={mode}{fallback})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"SOLIDBridge(solid_decisions={self._use_solid_decisions}, " \
               f"solid_analysis={self._use_solid_mission_analysis}, " \
               f"fallback={self._fallback_to_legacy})"