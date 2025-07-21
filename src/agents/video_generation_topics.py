"""
Video Generation Topics for Enhanced Multi-Agent Discussions
"""

from typing import Dict, Any
from .enhanced_multi_agent_discussion import DiscussionTopic
class VideoGenerationTopics:
    """Pre-defined discussion topics for video generation phases"""

    @staticmethod
    def script_optimization(context: Dict[str, Any]) -> DiscussionTopic:
        """Script content and structure optimization topic"""
        return DiscussionTopic(
            topic_id="script_optimization",
            title=f"Script Content and Structure Optimization for '{context.get('topic', 'video content')}'",
            description="Optimize script content, structure, and timing for maximum viral impact",
            context=context,
            required_decisions=[
                "narrative_structure",
                "content_pacing",
                "viral_hooks",
                "audience_engagement",
                "platform_optimization"
            ],
            max_rounds=5,
            min_consensus=0.7
        )

    @staticmethod
    def visual_strategy(context: Dict[str, Any]) -> DiscussionTopic:
        """Visual style and video generation strategy topic"""
        return DiscussionTopic(
            topic_id="visual_strategy",
            title="Visual Style and Video Generation Strategy",
            description="Define visual approach, style, and VEO-2 generation strategy",
            context=context,
            required_decisions=[
                "visual_style",
                "veo2_approach",
                "scene_composition",
                "color_palette",
                "visual_pacing"
            ],
            max_rounds=5,
            min_consensus=0.7
        )

    @staticmethod
    def audio_syn(c(context: Dict[str, Any]) -> DiscussionTopic:
        """Audio generation and synchronization strategy topic"""
        return DiscussionTopic(
            topic_id="audio_sync",
            title="Audio Generation and Synchronization Strategy",
            description="Plan audio generation, voice selection, and"
                    synchronization approach","
            context=context,
            required_decisions=[
                "voice_selection",
                "audio_timing",
                "synchronization_strategy",
                "sound_design",
                "tts_configuration"
            ],
            max_rounds=5,
            min_consensus=0.7
        )

    @staticmethod
    def audio_synchronizatio(n(context: Dict[str, Any]) -> DiscussionTopic:
        """Audio generation and synchronization strategy topic (alias)"""
        return VideoGenerationTopics.audio_sync(context)

    @staticmethod
    def final_assembl(y(context: Dict[str, Any]) -> DiscussionTopic:
        """Final video assembly strategy topic"""
        return DiscussionTopic(
            topic_id="final_assembly",
            title="Final Video Assembly Strategy",
            description="Coordinate final video assembly, quality checks, and delivery",
            context=context,
            required_decisions=[
                "assembly_workflow",
                "quality_standards",
                "final_optimizations",
                "delivery_format",
                "platform_compliance"
            ],
            max_rounds=3,
            min_consensus=0.8
        )
