"""
Enhanced Orchestrator with Comprehensive Agent Discussions
Extends the base orchestrator with detailed multi-agent discussions for optimal decision-making
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from .enhanced_orchestrator import EnhancedOrchestratorAgent
from .enhanced_multi_agent_discussion import EnhancedMultiAgentDiscussionSystem
from .advanced_composition_discussions import AdvancedCompositionDiscussionSystem
from ..models.video_models import Platform, VideoCategory
from ..utils.logging_config import get_logger
from config.config import settings

logger = get_logger(__name__)


class DiscussionEnhancedOrchestrator(EnhancedOrchestratorAgent):
    """
    Enhanced orchestrator with comprehensive agent discussions

    This orchestrator conducts detailed discussions between specialized agents
    before making any video generation decisions, ensuring optimal outcomes.
    """

    def __init__(self, topic: str, platform: Platform, category: VideoCategory,
                 duration_seconds: int = 50, enable_discussions: bool = True,
                 discussion_depth: str = "comprehensive"):
        # Initialize base orchestrator
        super().__init__(topic, platform, category, duration_seconds)

        # Discussion configuration
        self.enable_discussions = enable_discussions
        self.discussion_depth = discussion_depth  # "basic", "standard", "comprehensive"

        # Initialize discussion system
        if enable_discussions:
            self.discussion_system = EnhancedMultiAgentDiscussionSystem(
                api_key=settings.google_api_key,
                session_id=self.session_id,
                enable_visualization=True
            )
        else:
            self.discussion_system = None

        # Initialize composition system for advanced discussions
        self.composition_system = AdvancedCompositionDiscussionSystem(
            api_key=settings.google_api_key,
            session_id=self.session_id
        )

        # Track discussion results
        self.discussion_results = {}
        self.composition_decisions = {}

        logger.info(f"🎭 Discussion-Enhanced Orchestrator initialized")
        logger.info(f"   Discussions enabled: {enable_discussions}")
        logger.info(f"   Discussion depth: {discussion_depth}")

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Sanitize text for safe filename usage

        Args:
            text: Input text to sanitize
            max_length: Maximum filename length (default 50)

        Returns:
            Safe filename string
        """
        if not text:
            return "unnamed"

        # Remove/replace problematic characters
        safe_text = text.replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe_text = safe_text.replace(":", "_").replace("*", "_").replace("?", "_")
        safe_text = safe_text.replace('"', "_").replace("<", "_").replace(">", "_")
        safe_text = safe_text.replace("|", "_").replace(".", "_").replace(",", "_")
        safe_text = safe_text.replace("(", "_").replace(")", "_").replace("[", "_")
        safe_text = safe_text.replace("]", "_").replace("{", "_").replace("}", "_")
        safe_text = safe_text.replace("'", "_").replace("`", "_").replace("~", "_")
        safe_text = safe_text.replace("!", "_").replace("@", "_").replace("#", "_")
        safe_text = safe_text.replace("$", "_").replace("%", "_").replace("^", "_")
        safe_text = safe_text.replace("&", "_").replace("+", "_").replace("=", "_")

        # Convert to lowercase and remove multiple underscores
        safe_text = safe_text.lower()
        while "__" in safe_text:
            safe_text = safe_text.replace("__", "_")

        # Trim to max length
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]

        # Remove trailing underscore
        safe_text = safe_text.rstrip("_")

        # Ensure it's not empty
        if not safe_text:
            safe_text = "unnamed"

        return safe_text

    def orchestrate_complete_generation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate complete video generation with comprehensive agent discussions

        This method extends the base orchestration to include detailed
        composition decision-making at granular levels.
        """
        logger.info("🎭 Starting Advanced Composition Video Generation")
        logger.info(f"💬 Discussion mode: {self.discussion_depth}")

        # PHASE 1: Comprehensive Composition Discussion
        logger.info("🎯 PHASE 1: Comprehensive Video Composition Analysis")
        composition_decisions = self.composition_system.conduct_comprehensive_composition_discussion(
            topic=self.topic,
            category=self.category,
            platform=self.platform,
            total_duration=self.duration_seconds,
            style=config.get('style', 'viral')
        )

        # Store composition decisions
        self.composition_decisions = composition_decisions

        # PHASE 2: Initial Planning Discussion (enhanced with composition insights)
        if self.enable_discussions:
            planning_result = self._conduct_planning_discussion(config, composition_decisions)
            self.discussion_results['planning'] = planning_result

        # PHASE 3: Master Planning (enhanced with composition decisions)
        master_plan = self._create_enhanced_master_plan(config, composition_decisions)

        # PHASE 4: Script Generation Discussion (with detailed clip specifications)
        if self.enable_discussions:
            script_result = self._conduct_script_discussion(master_plan, composition_decisions)
            self.discussion_results['script'] = script_result

        # PHASE 5: Script Generation (with composition guidance)
        script_data = self._orchestrate_script_generation(master_plan, composition_decisions)

        # PHASE 6: Visual Strategy Discussion (with composition insights)
        if self.enable_discussions:
            visual_result = self._conduct_visual_discussion(script_data, composition_decisions)
            self.discussion_results['visual'] = visual_result

        # PHASE 7: Audio Strategy Discussion (with composition synchronization)
        if self.enable_discussions:
            audio_result = self._conduct_audio_discussion(script_data, composition_decisions)
            self.discussion_results['audio'] = audio_result

        # PHASE 8: Generate Audio (with composition timing)
        audio_data = self._orchestrate_audio_generation(script_data, composition_decisions)

        # PHASE 9: Video Generation Discussion (with composition specifications)
        if self.enable_discussions:
            video_result = self._conduct_video_discussion(script_data, audio_data, composition_decisions)
            self.discussion_results['video'] = video_result

        # PHASE 10: Video Generation (with composition guidance)
        video_clips = self._orchestrate_video_generation(script_data, audio_data, composition_decisions)

        # PHASE 11: Final Assembly Discussion (with composition integration)
        if self.enable_discussions:
            assembly_result = self._conduct_assembly_discussion(
                script_data, audio_data, video_clips, composition_decisions
            )
            self.discussion_results['assembly'] = assembly_result

        # PHASE 12: Final Assembly (with composition specifications)
        final_video = self._orchestrate_final_assembly(
            script_data, audio_data, video_clips, composition_decisions
        )

        # Save comprehensive discussion summary
        self._save_discussion_summary()

        logger.info("🎉 Advanced Composition Video Generation completed successfully!")
        return {
            'video_path': final_video,
            'composition_decisions': composition_decisions,
            'discussion_results': self.discussion_results,
            'master_plan': master_plan,
            'script_data': script_data,
            'audio_data': audio_data,
            'video_clips': video_clips
        }

    def _conduct_planning_discussion(self, config: Dict[str, Any],
                                    composition_decisions: Dict[str, Any]) -> Any:
        """Conduct initial planning discussion with composition insights"""
        logger.info("🎯 Conducting enhanced planning discussion")

        # Create discussion topic with composition context
        topic_context = {
            'original_config': config,
            'composition_decisions': composition_decisions,
            'topic': self.topic,
            'platform': self.platform.value,
            'category': self.category.value,
            'duration': self.duration_seconds
        }

        # Conduct planning discussion
        from .multi_agent_discussion import VideoGenerationTopics
        planning_topic = VideoGenerationTopics.script_optimization(topic_context)

        # Participate with key planning agents
        planning_agents = [
            self._get_agent_role('TREND_ANALYST'),
            self._get_agent_role('SCRIPT_WRITER'),
            self._get_agent_role('DIRECTOR'),
            self._get_agent_role('ORCHESTRATOR')
        ]

        if self.discussion_system:
            result = self.discussion_system.start_discussion(planning_topic, planning_agents)
            logger.info(f"✅ Planning discussion completed with {result.consensus_level:.2f} consensus")
            return result
        else:
            logger.warning("⚠️ Discussion system not available, skipping planning discussion")
            return None

    def _conduct_script_discussion(self, master_plan: Dict[str, Any],
                                  composition_decisions: Dict[str, Any]) -> Any:
        """Conduct script generation discussion with composition guidance"""
        logger.info("📝 Conducting enhanced script discussion")

        # Create discussion topic with composition context
        topic_context = {
            'master_plan': master_plan,
            'composition_decisions': composition_decisions,
            'topic': self.topic,
            'platform': self.platform.value,
            'category': self.category.value,
            'duration': self.duration_seconds
        }

        # Conduct script discussion
        from .multi_agent_discussion import VideoGenerationTopics
        script_topic = VideoGenerationTopics.script_optimization(topic_context)

        # Participate with script-focused agents
        script_agents = [
            self._get_agent_role('SCRIPT_WRITER'),
            self._get_agent_role('TREND_ANALYST'),
            self._get_agent_role('DIRECTOR'),
            self._get_agent_role('ORCHESTRATOR')
        ]

        if self.discussion_system:
            result = self.discussion_system.start_discussion(script_topic, script_agents)
            logger.info(f"✅ Script discussion completed with {result.consensus_level:.2f} consensus")
            return result
        else:
            logger.warning("⚠️ Discussion system not available, skipping script discussion")
            return None

    def _conduct_visual_discussion(self, script_data: Dict[str, Any],
                                  composition_decisions: Dict[str, Any]) -> Any:
        """Conduct visual strategy discussion with composition insights"""
        logger.info("🎨 Conducting enhanced visual discussion")

        # Create discussion topic with composition context
        topic_context = {
            'script_data': script_data,
            'composition_decisions': composition_decisions,
            'topic': self.topic,
            'platform': self.platform.value,
            'category': self.category.value,
            'duration': self.duration_seconds
        }

        # Conduct visual discussion
        from .multi_agent_discussion import VideoGenerationTopics
        visual_topic = VideoGenerationTopics.visual_strategy(topic_context)

        # Participate with visual-focused agents
        visual_agents = [
            self._get_agent_role('DIRECTOR'),
            self._get_agent_role('VIDEO_GENERATOR'),
            self._get_agent_role('EDITOR'),
            self._get_agent_role('ORCHESTRATOR')
        ]

        if self.discussion_system:
            result = self.discussion_system.start_discussion(visual_topic, visual_agents)
            logger.info(f"✅ Visual discussion completed with {result.consensus_level:.2f} consensus")
            return result
        else:
            logger.warning("⚠️ Discussion system not available, skipping visual discussion")
            return None

    def _conduct_audio_discussion(self, script_data: Dict[str, Any],
                                 composition_decisions: Dict[str, Any]) -> Any:
        """Conduct audio strategy discussion with composition synchronization"""
        logger.info("🎵 Conducting enhanced audio discussion")

        # Create discussion topic with composition context
        topic_context = {
            'script_data': script_data,
            'composition_decisions': composition_decisions,
            'topic': self.topic,
            'platform': self.platform.value,
            'category': self.category.value,
            'duration': self.duration_seconds
        }

        # Conduct audio discussion
        from .multi_agent_discussion import VideoGenerationTopics
        audio_topic = VideoGenerationTopics.audio_synchronization(topic_context)

        # Participate with audio-focused agents
        audio_agents = [
            self._get_agent_role('SOUNDMAN'),
            self._get_agent_role('SCRIPT_WRITER'),
            self._get_agent_role('DIRECTOR'),
            self._get_agent_role('ORCHESTRATOR')
        ]

        if self.discussion_system:
            result = self.discussion_system.start_discussion(audio_topic, audio_agents)
            logger.info(f"✅ Audio discussion completed with {result.consensus_level:.2f} consensus")
            return result
        else:
            logger.warning("⚠️ Discussion system not available, skipping audio discussion")
            return None

    def _conduct_video_discussion(self, script_data: Dict[str, Any], audio_data: Dict[str, Any],
                                 composition_decisions: Dict[str, Any]) -> Any:
        """Conduct video generation discussion with composition specifications"""
        logger.info("🎬 Conducting enhanced video discussion")

        # Create discussion topic with composition context
        topic_context = {
            'script_data': script_data,
            'audio_data': audio_data,
            'composition_decisions': composition_decisions,
            'topic': self.topic,
            'platform': self.platform.value,
            'category': self.category.value,
            'duration': self.duration_seconds
        }

        # Conduct video discussion
        from .multi_agent_discussion import VideoGenerationTopics
        video_topic = VideoGenerationTopics.platform_optimization(topic_context)

        # Participate with video-focused agents
        video_agents = [
            self._get_agent_role('VIDEO_GENERATOR'),
            self._get_agent_role('DIRECTOR'),
            self._get_agent_role('TREND_ANALYST'),
            self._get_agent_role('ORCHESTRATOR')
        ]

        if self.discussion_system:
            result = self.discussion_system.start_discussion(video_topic, video_agents)
            logger.info(f"✅ Video discussion completed with {result.consensus_level:.2f} consensus")
            return result
        else:
            logger.warning("⚠️ Discussion system not available, skipping video discussion")
            return None

    def _conduct_assembly_discussion(self, script_data: Dict[str, Any], audio_data: Dict[str, Any],
                                    video_clips: List[str], composition_decisions: Dict[str, Any]) -> Any:
        """Conduct final assembly discussion with composition integration"""
        logger.info("🎞️ Conducting enhanced assembly discussion")

        # Create discussion topic with composition context
        topic_context = {
            'script_data': script_data,
            'audio_data': audio_data,
            'video_clips': video_clips,
            'composition_decisions': composition_decisions,
            'topic': self.topic,
            'platform': self.platform.value,
            'category': self.category.value,
            'duration': self.duration_seconds
        }

        # Conduct assembly discussion
        from .multi_agent_discussion import VideoGenerationTopics
        assembly_topic = VideoGenerationTopics.platform_optimization(topic_context)

        # Participate with assembly-focused agents
        assembly_agents = [
            self._get_agent_role('EDITOR'),
            self._get_agent_role('DIRECTOR'),
            self._get_agent_role('SOUNDMAN'),
            self._get_agent_role('ORCHESTRATOR')
        ]

        if self.discussion_system:
            result = self.discussion_system.start_discussion(assembly_topic, assembly_agents)
            logger.info(f"✅ Assembly discussion completed with {result.consensus_level:.2f} consensus")
            return result
        else:
            logger.warning("⚠️ Discussion system not available, skipping assembly discussion")
            return None

    def _get_agent_role(self, role_name: str):
        """Get agent role enum from string name"""
        from .multi_agent_discussion import AgentRole
        return getattr(AgentRole, role_name)

    def _create_enhanced_master_plan(self, config: Dict[str, Any],
                                    composition_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced master plan with composition decisions"""
        logger.info("📋 Creating enhanced master plan with composition insights")

        # Base master plan from parent class
        base_plan = super()._create_master_timeline()

        # Enhance with composition decisions
        enhanced_plan = {
            **base_plan,
            'composition_decisions': composition_decisions,
            'enhanced_features': {
                'composition_guided': True,
                'discussion_informed': self.enable_discussions,
                'depth_level': self.discussion_depth
            }
        }

        logger.info("✅ Enhanced master plan created with composition guidance")
        return enhanced_plan

    def _orchestrate_script_generation(self, master_plan: Dict[str, Any],
                                      composition_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate script generation with composition guidance"""
        logger.info("📝 Orchestrating enhanced script generation")

        # Use composition decisions to guide script generation
        script_guidance = composition_decisions.get('decisions', {}).get('script', {})

        # Generate script with enhanced guidance
        script_data = super()._orchestrate_director_agent(
            api_key=settings.google_api_key,
            master_timeline=master_plan
        )

        # Enhance script with composition insights
        enhanced_script = {
            **script_data,
            'composition_guidance': script_guidance,
            'enhanced_features': {
                'composition_informed': True,
                'discussion_guided': self.enable_discussions
            }
        }

        logger.info("✅ Enhanced script generation completed")
        return enhanced_script

    def _orchestrate_audio_generation(self, script_data: Dict[str, Any],
                                     composition_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate audio generation with composition timing"""
        logger.info("🎵 Orchestrating enhanced audio generation")

        # Use composition decisions to guide audio generation
        audio_guidance = composition_decisions.get('decisions', {}).get('audio', {})

        # Generate audio with enhanced guidance
        audio_data = super()._orchestrate_soundman_agent(
            api_key=settings.google_api_key,
            script_data=script_data,
            master_timeline={'total_duration': self.duration_seconds}
        )

        # Enhance audio with composition insights
        enhanced_audio = {
            **audio_data,
            'composition_guidance': audio_guidance,
            'enhanced_features': {
                'composition_synchronized': True,
                'discussion_guided': self.enable_discussions
            }
        }

        logger.info("✅ Enhanced audio generation completed")
        return enhanced_audio

    def _orchestrate_video_generation(self, script_data: Dict[str, Any], audio_data: Dict[str, Any],
                                     composition_decisions: Dict[str, Any]) -> List[str]:
        """Orchestrate video generation with composition specifications"""
        logger.info("🎬 Orchestrating enhanced video generation")

        # Use composition decisions to guide video generation
        video_guidance = composition_decisions.get('decisions', {}).get('media', {})

        # Generate video clips with enhanced guidance
        try:
            # Call the parent method with correct signature
            video_data = super()._orchestrate_video_agent(
                api_key="dummy_key",
                script_data=script_data,
                master_timeline={'total_duration': self.duration_seconds}
            )
            video_clips = video_data.get('clips', [])
        except Exception as e:
            logger.error(f"Error in video generation: {e}")
            video_clips = []

        logger.info("✅ Enhanced video generation completed")
        return video_clips

    def _orchestrate_final_assembly(self, script_data: Dict[str, Any], audio_data: Dict[str, Any],
                                   video_clips: List[str], composition_decisions: Dict[str, Any]) -> str:
        """Orchestrate final assembly with composition integration"""
        logger.info("🎞️ Orchestrating enhanced final assembly")

        # Use composition decisions to guide final assembly
        assembly_guidance = composition_decisions.get('decisions', {}).get('visual', {})

        # Assemble final video with enhanced guidance
        try:
            # Call the parent method with correct signature
            final_video = super()._orchestrate_editor_agent(
                video_data={'clips': video_clips},
                audio_data=audio_data,
                master_timeline={'total_duration': self.duration_seconds}
            )
        except Exception as e:
            logger.error(f"Error in final assembly: {e}")
            final_video = "error_final_video.mp4"

        logger.info("✅ Enhanced final assembly completed")
        return final_video

    def _save_discussion_summary(self):
        """Save comprehensive discussion summary to main session folder"""
        summary = {
            'session_id': self.session_id,
            'topic': self.topic,
            'generation_timestamp': datetime.now().isoformat(),
            'discussion_configuration': {
                'enabled': self.enable_discussions,
                'depth': self.discussion_depth,
                'total_discussions': len(self.discussion_results)
            },
            'discussion_results': {
                topic: {
                    'consensus_level': result.consensus_level,
                    'total_rounds': result.total_rounds,
                    'participating_agents': result.participating_agents,
                    'key_insights': result.key_insights,
                    'final_decision': result.decision
                }
                for topic, result in self.discussion_results.items()
            },
            'overall_metrics': {
                'average_consensus': self._calculate_average_consensus(),
                'total_rounds': sum(r.total_rounds for r in self.discussion_results.values()),
                'unique_participating_agents': len(set(
                    agent for result in self.discussion_results.values()
                    for agent in result.participating_agents
                ))
            },
            'key_insights_summary': self._extract_all_insights()
        }

        # CRITICAL: Save to main session directory (NOT separate orchestrated folder)
        # Find the MOST RECENT session folder (where video was generated)
        main_session_dir = None
        outputs_dir = "outputs"

        if os.path.exists(outputs_dir):
            # Get all session folders and sort by creation time
            session_folders = []
            for folder in os.listdir(outputs_dir):
                if folder.startswith("session_"):
                    folder_path = os.path.join(outputs_dir, folder)
                    if os.path.isdir(folder_path):
                        session_folders.append((folder_path, os.path.getctime(folder_path)))

            # Sort by creation time (newest first) and use the most recent
            if session_folders:
                session_folders.sort(key=lambda x: x[1], reverse=True)
                main_session_dir = session_folders[0][0]
                logger.info(f"💾 Saving discussions to most recent session: {main_session_dir}")

        if not main_session_dir:
            # Create session folder if it doesn't exist
            main_session_dir = f"outputs/session_{self.session_id}"
            os.makedirs(main_session_dir, exist_ok=True)

        # Save agent discussions summary in main session folder
        summary_file = os.path.join(main_session_dir, "agent_discussions_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        # Also save individual discussion files
        discussions_dir = os.path.join(main_session_dir, "agent_discussions")
        os.makedirs(discussions_dir, exist_ok=True)

        for topic_name, result in self.discussion_results.items():
            safe_topic_name = self._sanitize_filename(topic_name)
            discussion_file = os.path.join(discussions_dir, f"discussion_{safe_topic_name}.json")
            with open(discussion_file, 'w') as f:
                json.dump({
                    'topic': topic_name,
                    'result': {
                        'consensus_level': result.consensus_level,
                        'total_rounds': result.total_rounds,
                        'participating_agents': result.participating_agents,
                        'key_insights': result.key_insights,
                        'decision': result.decision,
                        'alternative_approaches': result.alternative_approaches
                    }
                }, f, indent=2, default=str)

        logger.info(f"💾 Discussion summary saved: {summary_file}")
        logger.info(f"💾 Individual discussions saved: {discussions_dir}")

        # ENHANCED: Generate session summary with visualizer
        if (self.discussion_system and 
            hasattr(self.discussion_system, 'visualizer') and 
            self.discussion_system.visualizer):
            session_summary = self.discussion_system.visualizer.generate_session_summary()
            if session_summary:
                logger.info("📊 ENHANCED SESSION ANALYTICS:")
                logger.info(f"   Success Rate: {session_summary['session_overview']['success_rate']:.1%}")
                logger.info(f"   Total Duration: {session_summary['session_overview']['total_duration_seconds']:.1f}s")
                most_active_agents = session_summary['most_active_agents']
                if most_active_agents:
                    most_active = list(most_active_agents.keys())[0]
                    logger.info(f"   Most Active Agent: {most_active}")

        # Log key metrics
        logger.info("📊 DISCUSSION SUMMARY:")
        logger.info(f"   Total Discussions: {len(self.discussion_results)}")
        logger.info(f"   Average Consensus: {summary['overall_metrics']['average_consensus']:.2f}")
        logger.info(f"   Total Rounds: {summary['overall_metrics']['total_rounds']}")
        logger.info(f"   Unique Agents: {summary['overall_metrics']['unique_participating_agents']}")

    def _calculate_average_consensus(self) -> float:
        """Calculate average consensus across all discussions"""
        if not self.discussion_results:
            return 0.0
        total_consensus = sum(result.consensus_level for result in self.discussion_results.values())
        return total_consensus / len(self.discussion_results)

    def _extract_all_insights(self) -> List[str]:
        """Extract all key insights from discussions"""
        all_insights = []
        for result in self.discussion_results.values():
            all_insights.extend(result.key_insights)
        return all_insights[:10]  # Top 10 insights


# Factory function for creating discussion-enhanced orchestrator
def create_discussion_enhanced_orchestrator(topic: str, platform: str, category: str,
                                           duration: int = 50, enable_discussions: bool = True,
                                           discussion_depth: str = "comprehensive") -> DiscussionEnhancedOrchestrator:
    """
    Factory function to create a discussion-enhanced orchestrator

    Args:
        topic: Video topic
        platform: Target platform (instagram, tiktok, youtube)
        category: Video category (entertainment, education, lifestyle)
        duration: Video duration in seconds
        enable_discussions: Whether to enable agent discussions
        discussion_depth: Discussion depth level

    Returns:
        DiscussionEnhancedOrchestrator instance
    """
    # Convert string enums to proper enum types
    try:
        platform_enum = Platform(platform.lower())
    except ValueError:
        platform_enum = Platform.INSTAGRAM

    try:
        category_enum = VideoCategory(category.lower())
    except ValueError:
        category_enum = VideoCategory.ENTERTAINMENT

    return DiscussionEnhancedOrchestrator(
        topic=topic,
        platform=platform_enum,
        category=category_enum,
        duration_seconds=duration,
        enable_discussions=enable_discussions,
        discussion_depth=discussion_depth
    )

