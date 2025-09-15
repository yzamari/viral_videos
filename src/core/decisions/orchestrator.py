"""
Decision Orchestrator - Dependency Inversion Principle Implementation

This orchestrator depends on abstractions (IDecisionStrategy) rather than
concrete implementations, following DIP and enabling easy testing and extension.
"""

import logging
from typing import Dict, List, Optional, Set
from .interfaces.decision_strategy import IDecisionStrategy, DecisionContext, DecisionResult
from .interfaces.decision_orchestrator import IDecisionOrchestrator

logger = logging.getLogger(__name__)


class DecisionOrchestrator(IDecisionOrchestrator):
    """
    Orchestrates multiple decision strategies following SOLID principles.
    
    This class demonstrates:
    - SRP: Only responsible for coordinating decision strategies
    - OCP: New strategies can be added without modifying this class
    - DIP: Depends on IDecisionStrategy abstraction, not concrete classes
    - ISP: Uses focused interfaces for each responsibility
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize decision orchestrator."""
        self.config = config or {}
        self._strategies: Dict[str, IDecisionStrategy] = {}
        self._strategy_order: List[str] = []
        
        logger.info("🎯 Decision Orchestrator initialized (SOLID-compliant)")
    
    def register_strategy(self, strategy: IDecisionStrategy) -> None:
        """
        Register a decision strategy.
        
        This method demonstrates Open/Closed Principle - new strategies
        can be added without modifying existing code.
        
        Args:
            strategy: Decision strategy to register
        """
        decision_type = strategy.decision_type
        
        if decision_type in self._strategies:
            logger.warning(f"Replacing existing strategy for {decision_type}")
        
        self._strategies[decision_type] = strategy
        
        # Maintain registration order for dependency resolution
        if decision_type not in self._strategy_order:
            self._strategy_order.append(decision_type)
        
        logger.info(f"✅ Registered strategy: {decision_type} ({strategy.__class__.__name__})")
    
    def make_decisions(self, context: DecisionContext) -> Dict[str, DecisionResult]:
        """
        Make all applicable decisions based on context.
        
        Args:
            context: Decision context with relevant data
            
        Returns:
            Dict[str, DecisionResult]: Map of decision type to result
        """
        logger.info(f"🎯 Making decisions for mission: {context.mission[:50]}...")
        
        results = {}
        enhanced_context = self._create_enhanced_context(context)
        
        # Process strategies in registration order to handle dependencies
        for decision_type in self._strategy_order:
            strategy = self._strategies[decision_type]
            
            try:
                if strategy.can_decide(enhanced_context):
                    logger.debug(f"Making {decision_type} decision...")
                    result = strategy.decide(enhanced_context)
                    results[decision_type] = result
                    
                    # Update context with new decision for dependent strategies
                    enhanced_context = self._update_context_with_result(
                        enhanced_context, decision_type, result
                    )
                    
                    logger.info(
                        f"✅ {decision_type}: {result.value} "
                        f"(confidence: {result.confidence:.2f})"
                    )
                else:
                    missing_fields = self._get_missing_fields(strategy, enhanced_context)
                    logger.warning(
                        f"⏭️ Skipping {decision_type} decision: "
                        f"missing {missing_fields}"
                    )
                    
            except Exception as e:
                logger.error(f"❌ Error making {decision_type} decision: {e}")
                # Don't fail the entire process for one strategy failure
                continue
        
        logger.info(f"🎯 Completed {len(results)} decisions")
        return results
    
    def make_decision(self, decision_type: str, context: DecisionContext) -> Optional[DecisionResult]:
        """
        Make a specific decision by type.
        
        Args:
            decision_type: Type of decision to make
            context: Decision context with relevant data
            
        Returns:
            Optional[DecisionResult]: Decision result or None if not available
        """
        strategy = self._strategies.get(decision_type)
        if not strategy:
            logger.warning(f"No strategy registered for {decision_type}")
            return None
        
        if not strategy.can_decide(context):
            missing_fields = self._get_missing_fields(strategy, context)
            logger.warning(
                f"Cannot make {decision_type} decision: missing {missing_fields}"
            )
            return None
        
        try:
            result = strategy.decide(context)
            logger.info(
                f"✅ {decision_type}: {result.value} "
                f"(confidence: {result.confidence:.2f})"
            )
            return result
        except Exception as e:
            logger.error(f"❌ Error making {decision_type} decision: {e}")
            return None
    
    def get_available_decisions(self, context: DecisionContext) -> List[str]:
        """
        Get list of decisions that can be made with the given context.
        
        Args:
            context: Decision context to evaluate
            
        Returns:
            List[str]: List of available decision types
        """
        available = []
        for decision_type, strategy in self._strategies.items():
            if strategy.can_decide(context):
                available.append(decision_type)
        
        return available
    
    def validate_context(self, context: DecisionContext) -> Dict[str, bool]:
        """
        Validate if context has required fields for each decision type.
        
        Args:
            context: Decision context to validate
            
        Returns:
            Dict[str, bool]: Map of decision type to validation result
        """
        validation_results = {}
        
        for decision_type, strategy in self._strategies.items():
            validation_results[decision_type] = strategy.can_decide(context)
        
        return validation_results
    
    def get_strategy_info(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about registered strategies.
        
        Returns:
            Dict[str, Dict[str, any]]: Strategy information
        """
        info = {}
        
        for decision_type, strategy in self._strategies.items():
            info[decision_type] = {
                'class': strategy.__class__.__name__,
                'required_fields': strategy.required_context_fields,
                'decision_type': strategy.decision_type
            }
        
        return info
    
    def _create_enhanced_context(self, context: DecisionContext) -> DecisionContext:
        """
        Create enhanced context with default values and configuration.
        
        Args:
            context: Original context
            
        Returns:
            DecisionContext: Enhanced context
        """
        # Create a copy to avoid modifying original
        enhanced_config = dict(context.config or {})
        enhanced_config.update(self.config)
        
        return DecisionContext(
            mission=context.mission,
            platform=context.platform,
            duration=context.duration,
            target_audience=context.target_audience,
            language=context.language,
            config=enhanced_config,
            session_data=dict(context.session_data or {})
        )
    
    def _update_context_with_result(self, context: DecisionContext, 
                                   decision_type: str, result: DecisionResult) -> DecisionContext:
        """
        Update context with a new decision result for dependent strategies.
        
        Args:
            context: Current context
            decision_type: Type of decision made
            result: Decision result
            
        Returns:
            DecisionContext: Updated context
        """
        # Update the relevant field based on decision type
        updates = {}
        
        if decision_type == "duration":
            updates['duration'] = result.value
        elif decision_type == "platform":
            updates['platform'] = result.value
        elif decision_type == "target_audience":
            updates['target_audience'] = result.value
        elif decision_type == "language":
            updates['language'] = result.value
        
        # Update session data with decision result
        session_data = dict(context.session_data or {})
        session_data[f"{decision_type}_decision"] = {
            'value': result.value,
            'confidence': result.confidence,
            'source': result.source
        }
        
        return DecisionContext(
            mission=context.mission,
            platform=updates.get('platform', context.platform),
            duration=updates.get('duration', context.duration),
            target_audience=updates.get('target_audience', context.target_audience),
            language=updates.get('language', context.language),
            config=context.config,
            session_data=session_data
        )
    
    def _get_missing_fields(self, strategy: IDecisionStrategy, 
                           context: DecisionContext) -> List[str]:
        """
        Get list of missing required fields for a strategy.
        
        Args:
            strategy: Strategy to check
            context: Context to validate
            
        Returns:
            List[str]: Missing field names
        """
        return [
            field for field in strategy.required_context_fields
            if getattr(context, field, None) is None
        ]
    
    @property
    def registered_strategies(self) -> List[str]:
        """Get list of registered strategy types."""
        return list(self._strategies.keys())
    
    def __str__(self) -> str:
        """String representation for debugging."""
        strategies = ", ".join(self._strategies.keys())
        return f"DecisionOrchestrator(strategies=[{strategies}])"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"DecisionOrchestrator(strategies={self._strategies}, config={self.config})"