"""
Mission-Focused Discussion Topics for Multi-Agent System
"""
from typing import Dict, Any
from .multi_agent_discussion import DiscussionTopic

class MissionDiscussionTopics:
    """Mission-specific discussion topics for deeper content strategy"""
    
    @staticmethod
    def mission_strategy(context: Dict[str, Any]) -> DiscussionTopic:
        """Strategic approach to accomplish the mission"""
        return DiscussionTopic(
            topic_id="mission_strategy",
            title=f"Strategic Approach to Accomplish: {context.get('mission', 'mission')[:100]}",
            description="Develop comprehensive strategy to achieve mission objectives and create lasting impact",
            context=context,
            required_decisions=[
                "core_message_crystallization",
                "persuasion_techniques",
                "resistance_handling",
                "evidence_selection",
                "emotional_journey_design",
                "call_to_action_optimization"
            ],
            max_rounds=7,
            min_consensus=0.8
        )
    
    @staticmethod
    def impact_maximization(context: Dict[str, Any]) -> DiscussionTopic:
        """Maximize mission impact and viewer transformation"""
        return DiscussionTopic(
            topic_id="impact_maximization",
            title="Maximizing Mission Impact and Viewer Transformation",
            description="Design content elements that create maximum impact and drive desired outcomes",
            context=context,
            required_decisions=[
                "hook_psychology",
                "transformation_moments",
                "reinforcement_patterns",
                "memory_anchors",
                "action_triggers",
                "viral_mechanics"
            ],
            max_rounds=6,
            min_consensus=0.75
        )
    
    @staticmethod
    def coherence_enforcement(context: Dict[str, Any]) -> DiscussionTopic:
        """Ensure absolute mission coherence throughout content"""
        return DiscussionTopic(
            topic_id="coherence_enforcement",
            title="Mission Coherence and Message Consistency",
            description="Ensure every second advances the mission without distraction or dilution",
            context=context,
            required_decisions=[
                "content_filtering",
                "message_repetition",
                "visual_mission_alignment",
                "audio_reinforcement",
                "pacing_for_impact",
                "distraction_elimination"
            ],
            max_rounds=5,
            min_consensus=0.85
        )
    
    @staticmethod
    def audience_psychology(context: Dict[str, Any]) -> DiscussionTopic:
        """Deep dive into audience psychology for mission success"""
        return DiscussionTopic(
            topic_id="audience_psychology", 
            title="Audience Psychology and Behavioral Drivers",
            description="Understand and leverage audience psychology to accomplish mission objectives",
            context=context,
            required_decisions=[
                "motivational_triggers",
                "objection_preemption",
                "trust_building",
                "social_proof_integration",
                "urgency_creation",
                "commitment_escalation"
            ],
            max_rounds=6,
            min_consensus=0.75
        )
    
    @staticmethod
    def measurement_strategy(context: Dict[str, Any]) -> DiscussionTopic:
        """Define success metrics and measurement approach"""
        return DiscussionTopic(
            topic_id="measurement_strategy",
            title="Mission Success Measurement and Optimization",
            description="Define how to measure mission accomplishment and optimize for results",
            context=context,
            required_decisions=[
                "success_metrics",
                "engagement_indicators",
                "behavior_tracking",
                "feedback_loops",
                "iteration_strategy",
                "long_term_impact"
            ],
            max_rounds=4,
            min_consensus=0.7
        )
    
    @staticmethod
    def platform_mission_optimization(context: Dict[str, Any]) -> DiscussionTopic:
        """Optimize mission delivery for specific platform"""
        return DiscussionTopic(
            topic_id="platform_mission_optimization",
            title=f"Platform-Specific Mission Optimization for {context.get('platform', 'platform')}",
            description="Adapt mission delivery to platform algorithms and user behaviors",
            context=context,
            required_decisions=[
                "platform_hook_style",
                "algorithm_alignment",
                "sharing_triggers",
                "comment_catalysts",
                "retention_tactics",
                "cta_placement"
            ],
            max_rounds=5,
            min_consensus=0.75
        )
    
    @staticmethod
    def visual_mission_storytelling(context: Dict[str, Any]) -> DiscussionTopic:
        """Visual storytelling that powerfully conveys the mission"""
        return DiscussionTopic(
            topic_id="visual_mission_storytelling",
            title="Visual Storytelling for Mission Impact",
            description="Design visuals that emotionally convey and reinforce the mission message",
            context=context,
            required_decisions=[
                "visual_metaphors",
                "color_psychology",
                "symbolic_elements",
                "emotional_imagery",
                "progression_visualization",
                "memorable_moments"
            ],
            max_rounds=5,
            min_consensus=0.75
        )