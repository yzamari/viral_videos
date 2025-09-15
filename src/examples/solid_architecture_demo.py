"""
SOLID Architecture Demonstration

This script demonstrates the properly implemented SOLID principles
in the ViralAI system, showing how to use the new architecture.
"""

import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

# SOLID Architecture Imports
from src.core.services.service_factory import ServiceFactory
from src.core.decisions.interfaces.decision_strategy import DecisionContext
from src.core.integration.solid_bridge import SOLIDBridge
from src.utils.session_context import SessionContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SOLIDArchitectureDemo:
    """
    Demonstration of SOLID principles implementation.
    
    This class shows how the new architecture solves the previous
    OOP violations and provides a maintainable, testable system.
    """
    
    def __init__(self, api_key: str):
        """Initialize demo with API key."""
        self.api_key = api_key
        
        # Create session context (required for compatibility)
        self.session_context = SessionContext.get_instance()
        if not self.session_context:
            session_id = f"solid_demo_{int(time.time())}"
            self.session_context = SessionContext(
                session_id=session_id,
                base_output_dir=Path("outputs")
            )
        
        # Configuration for SOLID architecture
        self.config = {
            'service_factory': {
                'enable_service_caching': True
            },
            'mission_analyzer': {
                'parallel_analysis': True,
                'max_workers': 3,
                'ethical_timeout': 30
            },
            'decision_orchestrator': {
                'strategy_timeout': 10
            },
            'use_solid_decisions': True,
            'use_solid_mission_analysis': True,
            'fallback_to_legacy': True
        }
        
        logger.info("🎆 SOLID Architecture Demo initialized")
    
    async def demonstrate_solid_principles(self) -> Dict[str, Any]:
        """
        Demonstrate all SOLID principles in action.
        
        Returns:
            Dict[str, Any]: Demonstration results
        """
        logger.info("🚀 Starting SOLID Principles Demonstration")
        
        results = {
            'srp_demo': await self._demonstrate_single_responsibility(),
            'ocp_demo': await self._demonstrate_open_closed(),
            'lsp_demo': await self._demonstrate_liskov_substitution(),
            'isp_demo': await self._demonstrate_interface_segregation(),
            'dip_demo': await self._demonstrate_dependency_inversion()
        }
        
        logger.info("✅ SOLID Principles Demonstration completed")
        return results
    
    async def _demonstrate_single_responsibility(self) -> Dict[str, Any]:
        """
        Demonstrate Single Responsibility Principle.
        
        Shows how each class has only one reason to change.
        """
        logger.info("🎯 Demonstrating Single Responsibility Principle (SRP)")
        
        # Create service factory (responsibility: create services)
        service_factory = ServiceFactory(self.config['service_factory'])
        
        # Create mission analyzer (responsibility: analyze missions)
        mission_analyzer = service_factory.create_mission_analyzer(
            self.api_key, 
            self.config['mission_analyzer']
        )
        
        # Create decision orchestrator (responsibility: coordinate decisions)
        decision_orchestrator = service_factory.create_decision_orchestrator(
            self.config['decision_orchestrator']
        )
        
        return {
            'principle': 'Single Responsibility Principle',
            'demonstration': 'Each class has one clear responsibility',
            'examples': {
                'ServiceFactory': 'Creates and configures services',
                'MissionAnalyzerService': 'Analyzes mission requirements',
                'DecisionOrchestrator': 'Coordinates decision strategies',
                'DurationDecisionStrategy': 'Makes duration decisions only'
            },
            'benefit': 'Easy to test, modify, and extend individual components',
            'previous_violation': 'DecisionFramework did everything (1000+ lines)'
        }
    
    async def _demonstrate_open_closed(self) -> Dict[str, Any]:
        """
        Demonstrate Open/Closed Principle.
        
        Shows how new functionality can be added without modifying existing code.
        """
        logger.info("🔓 Demonstrating Open/Closed Principle (OCP)")
        
        # Create decision orchestrator
        decision_orchestrator = ServiceFactory().create_decision_orchestrator()
        
        # Show that new strategies can be added without modifying orchestrator
        initial_strategies = len(decision_orchestrator.registered_strategies)
        
        # We could add new strategies here without changing existing code
        # Example: orchestrator.register_strategy(StyleDecisionStrategy())
        
        return {
            'principle': 'Open/Closed Principle',
            'demonstration': 'New decision strategies can be added without modifying orchestrator',
            'examples': {
                'DecisionOrchestrator': 'Open for extension via strategy registration',
                'IDecisionStrategy': 'New implementations can be created',
                'ServiceFactory': 'New services can be added without modification'
            },
            'benefit': 'Add features without risking existing functionality',
            'implementation': f'Currently {initial_strategies} strategies registered',
            'extensibility': 'New strategies just implement IDecisionStrategy interface'
        }
    
    async def _demonstrate_liskov_substitution(self) -> Dict[str, Any]:
        """
        Demonstrate Liskov Substitution Principle.
        
        Shows how derived classes can replace base classes without breaking functionality.
        """
        logger.info("🔄 Demonstrating Liskov Substitution Principle (LSP)")
        
        # Create different decision strategies
        from src.core.decisions.strategies.duration_decision_strategy import DurationDecisionStrategy
        
        duration_strategy = DurationDecisionStrategy()
        
        # All strategies can be used interchangeably via IDecisionStrategy interface
        context = DecisionContext(
            mission="Test mission for LSP demonstration",
            platform="tiktok"
        )
        
        # Any strategy implementing IDecisionStrategy can be substituted
        can_decide = duration_strategy.can_decide(context)
        decision_type = duration_strategy.decision_type
        
        return {
            'principle': 'Liskov Substitution Principle',
            'demonstration': 'All strategy implementations are interchangeable',
            'examples': {
                'IDecisionStrategy': 'Base interface for all strategies',
                'DurationDecisionStrategy': 'Substitutable implementation',
                'can_decide_result': can_decide,
                'decision_type': decision_type
            },
            'benefit': 'Strategies can be swapped without breaking code',
            'substitutability': 'All strategies have consistent interface behavior'
        }
    
    async def _demonstrate_interface_segregation(self) -> Dict[str, Any]:
        """
        Demonstrate Interface Segregation Principle.
        
        Shows how interfaces are focused and clients only depend on what they need.
        """
        logger.info("⚙️ Demonstrating Interface Segregation Principle (ISP)")
        
        return {
            'principle': 'Interface Segregation Principle',
            'demonstration': 'Focused interfaces for specific responsibilities',
            'examples': {
                'IDecisionStrategy': 'Only decision-making methods',
                'IMissionAnalyzer': 'Only mission analysis methods',
                'IContentValidator': 'Only validation methods',
                'IDecisionOrchestrator': 'Only orchestration methods'
            },
            'benefit': 'Clients only depend on methods they actually use',
            'previous_violation': 'Fat interfaces forced unnecessary dependencies',
            'interface_count': 4,
            'focused_responsibility': 'Each interface has single, clear purpose'
        }
    
    async def _demonstrate_dependency_inversion(self) -> Dict[str, Any]:
        """
        Demonstrate Dependency Inversion Principle.
        
        Shows how high-level modules depend on abstractions, not concretions.
        """
        logger.info("🔌 Demonstrating Dependency Inversion Principle (DIP)")
        
        # Create SOLID bridge with dependency injection
        solid_bridge = SOLIDBridge(
            api_key=self.api_key,
            session_context=self.session_context,
            config=self.config
        )
        
        # Show that bridge depends on abstractions (interfaces) not concretions
        architecture_info = solid_bridge.get_architecture_info()
        
        return {
            'principle': 'Dependency Inversion Principle',
            'demonstration': 'High-level modules depend on abstractions',
            'examples': {
                'SOLIDBridge': 'Depends on IMissionAnalyzer interface',
                'DecisionOrchestrator': 'Depends on IDecisionStrategy interface',
                'ServiceFactory': 'Injects dependencies via constructor',
                'MissionAnalyzerService': 'Receives injected analysis systems'
            },
            'benefit': 'Easy to test with mocks, swap implementations',
            'dependency_injection': 'Constructor injection used throughout',
            'architecture_info': architecture_info,
            'testability': 'All dependencies can be mocked for unit testing'
        }
    
    async def demonstrate_complete_workflow(self) -> Dict[str, Any]:
        """
        Demonstrate complete workflow using SOLID architecture.
        
        This shows how all components work together following SOLID principles.
        """
        logger.info("🌎 Demonstrating Complete SOLID Workflow")
        
        # Create SOLID bridge
        solid_bridge = SOLIDBridge(
            api_key=self.api_key,
            session_context=self.session_context,
            config=self.config
        )
        
        # Test mission
        test_mission = (
            "Create a compelling TikTok video about sustainable technology "
            "that educates viewers while promoting environmental awareness"
        )
        
        try:
            # Step 1: Comprehensive mission analysis
            logger.info("🔍 Step 1: Mission Analysis")
            mission_analysis = solid_bridge.analyze_mission_comprehensive(
                mission=test_mission,
                platform="tiktok"
            )
            
            # Step 2: Core decision making
            logger.info("🎯 Step 2: Decision Making")
            decisions = solid_bridge.make_core_decisions(
                mission=test_mission,
                platform="tiktok",
                target_audience="young_adults",
                language="en-US"
            )
            
            # Step 3: Architecture information
            architecture_info = solid_bridge.get_architecture_info()
            
            return {
                'workflow_success': True,
                'mission': test_mission,
                'mission_analysis': mission_analysis.get('success', False),
                'decisions_made': decisions.get('success', False),
                'architecture': architecture_info,
                'solid_benefits_demonstrated': [
                    'Single Responsibility: Each service has one job',
                    'Open/Closed: New strategies can be added easily',
                    'Liskov Substitution: All strategies are interchangeable',
                    'Interface Segregation: Focused, minimal interfaces',
                    'Dependency Inversion: Depends on abstractions'
                ],
                'performance_improvements': {
                    'parallel_analysis': mission_analysis.get('solid_metadata', {}).get('analysis_types', []),
                    'strategy_count': len(architecture_info.get('registered_strategies', [])),
                    'service_caching': architecture_info.get('service_factory_cache', {})
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Complete workflow failed: {e}")
            return {
                'workflow_success': False,
                'error': str(e),
                'fallback_available': solid_bridge._fallback_to_legacy
            }
    
    async def run_full_demonstration(self) -> Dict[str, Any]:
        """
        Run the complete SOLID principles demonstration.
        
        Returns:
            Dict[str, Any]: Complete demonstration results
        """
        logger.info("🎆 Starting Full SOLID Architecture Demonstration")
        
        results = {
            'demonstration_type': 'SOLID Principles in ViralAI',
            'timestamp': str(datetime.now()),
            'solid_principles': await self.demonstrate_solid_principles(),
            'complete_workflow': await self.demonstrate_complete_workflow(),
            'summary': {
                'architecture_type': 'SOLID-compliant with legacy bridge',
                'key_improvements': [
                    'Eliminated god classes (DecisionFramework 1000+ lines → focused services)',
                    'Implemented proper dependency injection',
                    'Created focused interfaces following ISP',
                    'Enabled easy testing through DIP',
                    'Made system extensible through OCP'
                ],
                'migration_strategy': 'Gradual replacement with bridge pattern',
                'testing_benefits': 'All components now mockable and testable',
                'maintenance_benefits': 'Clear responsibilities, easy to modify'
            }
        }
        
        logger.info("✅ Full SOLID Architecture Demonstration completed")
        return results


async def main():
    """Main demonstration function."""
    import os
    
    # Get API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        logger.error("GOOGLE_AI_API_KEY environment variable required")
        return
    
    # Run demonstration
    demo = SOLIDArchitectureDemo(api_key)
    results = await demo.run_full_demonstration()
    
    # Print results
    import json
    print("\n" + "="*80)
    print("SOLID ARCHITECTURE DEMONSTRATION RESULTS")
    print("="*80)
    print(json.dumps(results, indent=2, default=str))
    print("="*80)


if __name__ == "__main__":
    import time
    from datetime import datetime
    
    asyncio.run(main())