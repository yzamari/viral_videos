"""
Advanced Video Composition Discussion System
Orchestrates detailed AI agent discussions for granular video composition decisions
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .video_composition_agents import (
    VideoStructureAgent,
    ClipTimingAgent,
    VisualElementsAgent,
    MediaTypeAgent
)
from .enhanced_multi_agent_discussion import (
    EnhancedMultiAgentDiscussionSystem,
    AgentRole,
    DiscussionTopic,
    DiscussionResult
)
from ..utils.logging_config import get_logger
logger = get_logger(__name__)
class AdvancedCompositionDiscussionSystem:
    """
    Orchestrates comprehensive AI agent discussions for video composition decisions
    """
    def __init__(self, api_key: str, session_id: str):
        self.api_key = api_key
        self.session_id = session_id
        # Initialize specialized composition agents
        self.structure_agent = VideoStructureAgent(api_key)
        self.timing_agent = ClipTimingAgent(api_key)
        self.visual_agent = VisualElementsAgent(api_key)
        self.media_agent = MediaTypeAgent(api_key)
        # Initialize enhanced discussion system
        self.discussion_system = EnhancedMultiAgentDiscussionSystem(
            api_key=api_key,
            session_id=session_id
        )
        # Results storage
        self.composition_decisions = {}
        self.discussion_logs = []
        logger.info("🎭 Advanced Composition Discussion System initialized")
        logger.info("🤖 Specialized agents: StructureMaster, TimingMaster, VisualDesigner, MediaStrategist")
    def conduct_comprehensive_composition_discussion(self,
                                                     topic: str,
                                                     category: str,
                                                     platform: str,
                                                     total_duration: int,
                                                     style: str = "viral") -> Dict[str, Any]:
        """
        Conduct comprehensive discussion covering all aspects of video composition
        """
        logger.info("🎭 Starting Comprehensive Video Composition Discussion")
        logger.info(f"📋 Topic: {topic}")
        logger.info(f"⏱️ Duration: {total_duration}s on {platform}")
        composition_result = {
            'topic': topic,
            'category': category,
            'platform': platform,
            'total_duration': total_duration,
            'style': style,
            'discussion_timestamp': datetime.now().isoformat(),
            'decisions': {},
            'discussion_logs': []
        }
        # PHASE 1: Video Structure Discussion
        logger.info("🏗️ PHASE 1: Video Structure Analysis")
        structure_decision = self._conduct_structure_discussion(
            topic, category, platform, total_duration, style
        )
        composition_result['decisions']['structure'] = structure_decision
        # PHASE 2: Clip Timing Discussion
        logger.info("⏱️ PHASE 2: Clip Timing Optimization")
        timing_decision = self._conduct_timing_discussion(
            structure_decision, {'topic': topic, 'category': category, 'platform': platform}
        )
        composition_result['decisions']['timing'] = timing_decision
        # PHASE 3: Visual Elements Discussion
        logger.info("🎨 PHASE 3: Visual Elements Design")
        visual_decision = self._conduct_visual_discussion(
            structure_decision, topic, platform
        )
        composition_result['decisions']['visual'] = visual_decision
        # PHASE 4: Media Type Discussion
        logger.info("📱 PHASE 4: Media Type Strategy")
        media_decision = self._conduct_media_discussion(
            timing_decision, {'topic': topic, 'category': category, 'style': style}
        )
        composition_result['decisions']['media'] = media_decision
        # PHASE 5: Integration Discussion
        logger.info("🔗 PHASE 5: Integration and Optimization")
        integration_decision = self._conduct_integration_discussion(
            structure_decision, timing_decision, visual_decision, media_decision
        )
        composition_result['decisions']['integration'] = integration_decision
        # Save comprehensive results
        self._save_comprehensive_results(composition_result)
        logger.info("✅ Comprehensive Video Composition Discussion Complete!")
        logger.info(f"📊 Total decisions made: {len(composition_result['decisions'])}")
        return composition_result
    def _conduct_structure_discussion(self, topic: str, category: str,
                                      platform: str, total_duration: int,
                                      style: str) -> Dict[str, Any]:
        """Conduct video structure discussion"""
        # Get AI agent's structure analysis
        structure_analysis = self.structure_agent.analyze_video_structure(
            topic, category, platform, total_duration, style
        )
        # Create discussion context
        context = {
            'topic': topic,
            'category': category,
            'platform': platform,
            'total_duration': total_duration,
            'ai_structure_recommendation': structure_analysis
        }
        # Create discussion topic
        discussion_topic = DiscussionTopic(
            topic_id="video_structure_composition",
            title="Video Structure and Segmentation Strategy",
            description="Determine optimal video structure with mixed continuity approaches",
            context=context,
            required_decisions=[
                "segment_breakdown",
                "continuity_strategy",
                "narrative_flow",
                "engagement_architecture",
                "platform_optimization"
            ],
            max_rounds=5,
            min_consensus=0.7
        )
        # Participating agents for structure discussion
        participating_agents = [
            AgentRole.ORCHESTRATOR,    # Strategic oversight (was SENIOR_MANAGER)
            AgentRole.DIRECTOR,        # Visual storytelling
            AgentRole.SCRIPT_WRITER,   # Narrative structure
            AgentRole.TREND_ANALYST,   # Platform optimization
            AgentRole.SOUNDMAN         # User experience (was AUDIENCE_ADVOCATE)
        ]
        # Conduct discussion
        discussion_result = self.discussion_system.start_discussion(
            discussion_topic, participating_agents
        )
        # Combine AI analysis with discussion result
        combined_result = {
            'ai_analysis': structure_analysis,
            'discussion_result': {
                'consensus_level': discussion_result.consensus_level,
                'total_rounds': discussion_result.total_rounds,
                'participating_agents': discussion_result.participating_agents,
                'key_insights': discussion_result.key_insights,
                'final_decisions': discussion_result.decision
            },
            'final_structure': self._merge_structure_decisions(
                structure_analysis, discussion_result.decision
            )
        }
        # Log the discussion
        self._log_composition_discussion("structure", combined_result)
        logger.info(f"🏗️ Structure Decision: {structure_analysis['total_segments']} segments")
        logger.info(f"   Discussion Consensus: {discussion_result.consensus_level:.2f}")
        return combined_result
    def _conduct_timing_discussion(self, structure_decision: Dict[str, Any],
                                   content_details: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct clip timing discussion"""
        # Get AI agent's timing analysis
        timing_analysis = self.timing_agent.analyze_clip_timings(
            structure_decision['final_structure'], content_details
        )
        # Create discussion context
        context = {
            'structure_decision': structure_decision,
            'content_details': content_details,
            'ai_timing_recommendation': timing_analysis
        }
        # Create discussion topic
        discussion_topic = DiscussionTopic(
            topic_id="clip_timing_optimization",
            title="Individual Clip Timing and Pacing Strategy",
            description="Optimize timing for each clip to maximize engagement and flow",
            context=context,
            required_decisions=[
                "clip_durations",
                "pacing_strategy",
                "attention_optimization",
                "flow_management",
                "timing_rationale"
            ],
            max_rounds=4,
            min_consensus=0.7
        )
        # Participating agents for timing discussion
        participating_agents = [
            AgentRole.DIRECTOR,        # Timing specialist (was PACE_MASTER)
            AgentRole.EDITOR,          # Cutting and flow
            AgentRole.ORCHESTRATOR,    # Attention management (was AUDIENCE_ADVOCATE)
            AgentRole.TREND_ANALYST    # Platform timing preferences
        ]
        # Conduct discussion
        discussion_result = self.discussion_system.start_discussion(
            discussion_topic, participating_agents
        )
        # Combine results
        combined_result = {
            'ai_analysis': timing_analysis,
            'discussion_result': {
                'consensus_level': discussion_result.consensus_level,
                'total_rounds': discussion_result.total_rounds,
                'participating_agents': discussion_result.participating_agents,
                'key_insights': discussion_result.key_insights,
                'final_decisions': discussion_result.decision
            },
            'final_timing': self._merge_timing_decisions(
                timing_analysis, discussion_result.decision
            )
        }
        # Log the discussion
        self._log_composition_discussion("timing", combined_result)
        logger.info(f"⏱️ Timing Decision: {timing_analysis['total_clips']} clips")
        logger.info(f"   Discussion Consensus: {discussion_result.consensus_level:.2f}")
        return combined_result
    def _conduct_visual_discussion(self, structure_decision: Dict[str, Any],
                                   topic: str, platform: str) -> Dict[str, Any]:
        """Conduct visual elements discussion"""
        # Get AI agent's visual design analysis
        visual_analysis = self.visual_agent.design_visual_elements(
            structure_decision['final_structure'], topic, platform
        )
        # Create discussion context
        context = {
            'structure_decision': structure_decision,
            'topic': topic,
            'platform': platform,
            'ai_visual_recommendation': visual_analysis
        }
        # Create discussion topic
        discussion_topic = DiscussionTopic(
            topic_id="visual_elements_design",
            title="Headers, Titles, and Visual Elements Design",
            description="Design optimal visual elements including typography, colors, and positioning",
            context=context,
            required_decisions=[
                "typography_strategy",
                "color_palette",
                "text_positioning",
                "visual_hierarchy",
                "accessibility_compliance"
            ],
            max_rounds=4,
            min_consensus=0.7
        )
        # Participating agents for visual discussion
        participating_agents = [
            AgentRole.DIRECTOR,        # Visual direction
            AgentRole.VIDEO_GENERATOR, # Brand consistency (was BRAND_STRATEGIST)
            AgentRole.EDITOR,          # Accessibility (was ACCESSIBILITY_EXPERT)
            AgentRole.TREND_ANALYST    # User experience (was AUDIENCE_ADVOCATE)
        ]
        # Conduct discussion
        discussion_result = self.discussion_system.start_discussion(
            discussion_topic, participating_agents
        )
        # Combine results
        combined_result = {
            'ai_analysis': visual_analysis,
            'discussion_result': {
                'consensus_level': discussion_result.consensus_level,
                'total_rounds': discussion_result.total_rounds,
                'participating_agents': discussion_result.participating_agents,
                'key_insights': discussion_result.key_insights,
                'final_decisions': discussion_result.decision
            },
            'final_visual_design': self._merge_visual_decisions(
                visual_analysis, discussion_result.decision
            )
        }
        # Log the discussion
        self._log_composition_discussion("visual", combined_result)
        logger.info(f"🎨 Visual Decision: {len(visual_analysis['text_elements'])} text elements")
        logger.info(f"   Discussion Consensus: {discussion_result.consensus_level:.2f}")
        return combined_result
    def _conduct_media_discussion(self, timing_decision: Dict[str, Any],
                                  content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct media type discussion"""
        # Get AI agent's media type analysis
        media_analysis = self.media_agent.analyze_media_types(
            timing_decision['final_timing'], content_analysis
        )
        # Create discussion context
        context = {
            'timing_decision': timing_decision,
            'content_analysis': content_analysis,
            'ai_media_recommendation': media_analysis
        }
        # Create discussion topic
        discussion_topic = DiscussionTopic(
            topic_id="media_type_strategy",
            title="VEO2 Video vs. Static Images Strategy",
            description="Decide optimal media types for each clip to maximize impact and efficiency",
            context=context,
            required_decisions=[
                "media_allocation",
                "veo2_vs_images_strategy",
                "resource_optimization",
                "visual_impact_balance",
                "generation_efficiency"
            ],
            max_rounds=4,
            min_consensus=0.7
        )
        # Participating agents for media discussion
        participating_agents = [
            AgentRole.VIDEO_GENERATOR,  # VEO2 expertise
            AgentRole.DIRECTOR,        # Visual impact
            AgentRole.EDITOR,          # Resource optimization (was PERFORMANCE_OPTIMIZER)
            AgentRole.SOUNDMAN         # Quality standards (was QUALITY_GUARD)
        ]
        # Conduct discussion
        discussion_result = self.discussion_system.start_discussion(
            discussion_topic, participating_agents
        )
        # Combine results
        combined_result = {
            'ai_analysis': media_analysis,
            'discussion_result': {
                'consensus_level': discussion_result.consensus_level,
                'total_rounds': discussion_result.total_rounds,
                'participating_agents': discussion_result.participating_agents,
                'key_insights': discussion_result.key_insights,
                'final_decisions': discussion_result.decision
            },
            'final_media_strategy': self._merge_media_decisions(
                media_analysis, discussion_result.decision
            )
        }
        # Log the discussion
        self._log_composition_discussion("media", combined_result)
        allocation = media_analysis['resource_allocation']
        logger.info(f"📱 Media Decision: {allocation['veo2_clips']} VEO2, {allocation['static_images']} images")
        logger.info(f"   Discussion Consensus: {discussion_result.consensus_level:.2f}")
        return combined_result
    def _conduct_integration_discussion(self, structure_decision: Dict[str, Any],
                                        timing_decision: Dict[str, Any],
                                        visual_decision: Dict[str, Any],
                                        media_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct final integration discussion"""
        # Create discussion context
        context = {
            'structure_decision': structure_decision,
            'timing_decision': timing_decision,
            'visual_decision': visual_decision,
            'media_decision': media_decision
        }
        # Create discussion topic
        discussion_topic = DiscussionTopic(
            topic_id="composition_integration",
            title="Final Integration and Optimization",
            description="Integrate all composition decisions and optimize for final production",
            context=context,
            required_decisions=[
                "integration_strategy",
                "quality_optimization",
                "final_adjustments",
                "production_workflow",
                "success_metrics"
            ],
            max_rounds=3,
            min_consensus=0.8
        )
        # Participating agents for integration discussion
        participating_agents = [
            AgentRole.ORCHESTRATOR,    # Strategic oversight (was SENIOR_MANAGER)
            AgentRole.ORCHESTRATOR,    # Integration coordination
            AgentRole.EDITOR,          # Quality assurance (was QUALITY_GUARD)
            AgentRole.VIDEO_GENERATOR  # Workflow optimization (was PERFORMANCE_OPTIMIZER)
        ]
        # Conduct discussion
        discussion_result = self.discussion_system.start_discussion(
            discussion_topic, participating_agents
        )
        # Create integrated result
        integrated_result = {
            'discussion_result': {
                'consensus_level': discussion_result.consensus_level,
                'total_rounds': discussion_result.total_rounds,
                'participating_agents': discussion_result.participating_agents,
                'key_insights': discussion_result.key_insights,
                'final_decisions': discussion_result.decision
            },
            'integrated_composition': self._create_integrated_composition(
                structure_decision, timing_decision, visual_decision, media_decision
            )
        }
        # Log the discussion
        self._log_composition_discussion("integration", integrated_result)
        logger.info(f"🔗 Integration Decision completed")
        logger.info(f"   Discussion Consensus: {discussion_result.consensus_level:.2f}")
        return integrated_result
    def _merge_structure_decisions(self, ai_analysis: Dict[str, Any],
                                   discussion_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Merge AI analysis with discussion decisions for structure"""
        merged = ai_analysis.copy()
        # Apply discussion refinements
        if 'segment_breakdown' in discussion_decisions:
            merged['discussion_refinements'] = discussion_decisions['segment_breakdown']
        if 'continuity_strategy' in discussion_decisions:
            merged['continuity_strategy_enhanced'] = discussion_decisions['continuity_strategy']
        return merged
    def _merge_timing_decisions(self, ai_analysis: Dict[str, Any],
                                discussion_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Merge AI analysis with discussion decisions for timing"""
        merged = ai_analysis.copy()
        # Apply discussion refinements
        if 'clip_durations' in discussion_decisions:
            merged['discussion_refinements'] = discussion_decisions['clip_durations']
        if 'pacing_strategy' in discussion_decisions:
            merged['pacing_strategy_enhanced'] = discussion_decisions['pacing_strategy']
        return merged
    def _merge_visual_decisions(self, ai_analysis: Dict[str, Any],
                                discussion_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Merge AI analysis with discussion decisions for visual elements"""
        merged = ai_analysis.copy()
        # Apply discussion refinements
        if 'typography_strategy' in discussion_decisions:
            merged['typography_enhanced'] = discussion_decisions['typography_strategy']
        if 'color_palette' in discussion_decisions:
            merged['color_palette_refined'] = discussion_decisions['color_palette']
        return merged
    def _merge_media_decisions(self, ai_analysis: Dict[str, Any],
                               discussion_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Merge AI analysis with discussion decisions for media types"""
        merged = ai_analysis.copy()
        # Apply discussion refinements
        if 'media_allocation' in discussion_decisions:
            merged['allocation_refined'] = discussion_decisions['media_allocation']
        if 'veo2_vs_images_strategy' in discussion_decisions:
            merged['strategy_enhanced'] = discussion_decisions['veo2_vs_images_strategy']
        return merged
    def _create_integrated_composition(self, structure_decision: Dict[str, Any],
                                       timing_decision: Dict[str, Any],
                                       visual_decision: Dict[str, Any],
                                       media_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Create final integrated composition plan"""
        return {
            'structure': structure_decision['final_structure'],
            'timing': timing_decision['final_timing'],
            'visual': visual_decision['final_visual_design'],
            'media': media_decision['final_media_strategy'],
            'integration_timestamp': datetime.now().isoformat(),
            'production_ready': True
        }
    def _log_composition_discussion(self, phase: str, result: Dict[str, Any]):
        """Log detailed composition discussion results"""
        log_entry = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'result': result
        }
        self.discussion_logs.append(log_entry)
        # Save to file
        log_file = f"outputs/session_{self.session_id}/composition_discussions/{phase}_discussion.json"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2, default=str)
        logger.info(f"📝 {phase.title()} discussion logged: {log_file}")
    def _save_comprehensive_results(self, composition_result: Dict[str, Any]):
        """Save comprehensive composition results"""
        # Save main results file
        results_file = f"outputs/session_{self.session_id}/comprehensive_composition_results.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(composition_result, f, indent=2, default=str)
        # Save summary file
        summary = {
            'session_id': self.session_id,
            'topic': composition_result['topic'],
            'total_duration': composition_result['total_duration'],
            'platform': composition_result['platform'],
            'decisions_made': list(
                composition_result['decisions'].keys()),
            'total_segments': composition_result['decisions']['structure']['ai_analysis']['total_segments'],
            'total_clips': composition_result['decisions']['timing']['ai_analysis']['total_clips'],
            'veo2_clips': composition_result['decisions']['media']['ai_analysis']['resource_allocation']['veo2_clips'],
            'static_images': composition_result['decisions']['media']['ai_analysis']['resource_allocation']['static_images'],
            'text_elements': len(
                composition_result['decisions']['visual']['ai_analysis']['text_elements']),
            'generation_timestamp': composition_result['discussion_timestamp']}
        summary_file = f"outputs/session_{self.session_id}/composition_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f"💾 Comprehensive results saved: {results_file}")
        logger.info(f"📊 Summary saved: {summary_file}")
        # Log final summary
        logger.info("📊 COMPREHENSIVE COMPOSITION SUMMARY:")
        logger.info(f"   Segments: {summary['total_segments']}")
        logger.info(f"   Clips: {summary['total_clips']}")
        logger.info(f"   VEO2 Videos: {summary['veo2_clips']}")
        logger.info(f"   Static Images: {summary['static_images']}")
        logger.info(f"   Text Elements: {summary['text_elements']}")
def create_advanced_composition_system(api_key: str, session_id: str) -> AdvancedCompositionDiscussionSystem:
    """Factory function to create advanced composition discussion system"""
    return AdvancedCompositionDiscussionSystem(api_key, session_id)

