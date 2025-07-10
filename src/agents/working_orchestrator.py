"""
Working AI Agent Orchestrator
Uses the actual AI agents for discussions and intelligent decision-making
"""

import os
from typing import Dict, Any
from datetime import datetime

from ..generators.video_generator import VideoGenerator
from ..generators.director import Director
from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from ..utils.logging_config import get_logger
from .continuity_decision_agent import ContinuityDecisionAgent
from .voice_director_agent import VoiceDirectorAgent
from .video_composition_agents import VideoStructureAgent, ClipTimingAgent, VisualElementsAgent, MediaTypeAgent
from .multi_agent_discussion import MultiAgentDiscussionSystem, AgentRole, DiscussionTopic

logger = get_logger(__name__)


class WorkingOrchestrator:
    """
    Working orchestrator that uses AI agents for intelligent decisions
    """
    
    def __init__(self, api_key: str, topic: str, platform: Platform, 
                 category: VideoCategory, duration: int):
        self.api_key = api_key
        self.topic = topic
        self.platform = platform
        self.category = category
        self.duration = duration
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize AI agents
        self.director = Director(api_key)
        self.continuity_agent = ContinuityDecisionAgent(api_key)
        self.voice_agent = VoiceDirectorAgent(api_key)
        self.structure_agent = VideoStructureAgent(api_key)
        self.timing_agent = ClipTimingAgent(api_key)
        self.visual_agent = VisualElementsAgent(api_key)
        self.media_agent = MediaTypeAgent(api_key)
        self.discussion_system = MultiAgentDiscussionSystem(api_key, self.session_id)
        
        # Results storage
        self.agent_decisions = {}
        self.discussion_results = {}
        
        logger.info("🎬 Working Orchestrator initialized with AI agents")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Session: {self.session_id}")
        logger.info(f"   AI Agents: 7 specialists + discussion system")
    
    def generate_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video using AI agent discussions and decisions
        """
        logger.info("🎬 Starting AI agent video generation")
        
        try:
            # Phase 1: AI Agent Discussions (30%)
            logger.info("🤝 Phase 1: AI Agent Discussions...")
            self._conduct_agent_discussions(config)
            
            # Phase 2: Script Generation with AI Director (50%)
            logger.info("📝 Phase 2: AI Director Script Generation...")
            script_data = self._generate_script_with_ai_director(config)
            
            # Phase 3: Video Structure & Timing Decisions (70%)
            logger.info("🎯 Phase 3: AI Structure & Timing Analysis...")
            structure_decisions = self._make_structure_decisions(script_data, config)
            
            # Phase 4: Voice & Media Type Decisions (80%)
            logger.info("🎤 Phase 4: AI Voice & Media Decisions...")
            voice_decisions = self._make_voice_decisions(script_data, config)
            media_decisions = self._make_media_decisions(script_data, config)
            
            # Phase 5: Generate Video with AI Decisions (100%)
            logger.info("🎬 Phase 5: Video Generation with AI Decisions...")
            video_path = self._generate_video_with_ai_decisions(
                script_data, structure_decisions, voice_decisions, media_decisions, config
            )
            
            logger.info(f"✅ AI agent video generation completed: {video_path}")
            
            return {
                'success': True,
                'final_video_path': video_path,
                'session_id': self.session_id,
                'agent_decisions': self.agent_decisions,
                'discussion_results': self.discussion_results,
                'agents_used': 7,
                'discussions_conducted': len(self.discussion_results),
                'optimization_level': 'ai_agent_enhanced'
            }
            
        except Exception as e:
            logger.error(f"❌ AI agent video generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'agent_decisions': self.agent_decisions,
                'discussion_results': self.discussion_results
            }
    
    def _conduct_agent_discussions(self, config: Dict[str, Any]):
        """Conduct AI agent discussions for strategic decisions"""
        
        # Discussion 1: Script Strategy
        script_topic = DiscussionTopic(
            title="Script Strategy & Viral Optimization",
            description=f"How to create the most engaging script for: {self.topic}",
            context={
                'topic': self.topic,
                'platform': self.platform.value,
                'duration': self.duration,
                'category': self.category.value
            },
            participants=[AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR],
            discussion_type="strategic",
            priority="high"
        )
        
        script_result = self.discussion_system.conduct_discussion(script_topic)
        self.discussion_results['script_strategy'] = script_result
        
        # Discussion 2: Visual & Technical Strategy
        visual_topic = DiscussionTopic(
            title="Visual Composition & Technical Approach",
            description=f"Optimal visual strategy for {self.platform.value} content",
            context={
                'topic': self.topic,
                'platform': self.platform.value,
                'force_generation': config.get('force_generation', 'auto')
            },
            participants=[AgentRole.VIDEO_GENERATOR, AgentRole.EDITOR],
            discussion_type="technical",
            priority="high"
        )
        
        visual_result = self.discussion_system.conduct_discussion(visual_topic)
        self.discussion_results['visual_strategy'] = visual_result
        
        # Discussion 3: Audio & Production Strategy
        audio_topic = DiscussionTopic(
            title="Audio Production & Voice Strategy",
            description="Optimal audio approach for maximum engagement",
            context={
                'topic': self.topic,
                'duration': self.duration,
                'platform': self.platform.value
            },
            participants=[AgentRole.SOUNDMAN, AgentRole.EDITOR],
            discussion_type="production",
            priority="medium"
        )
        
        audio_result = self.discussion_system.conduct_discussion(audio_topic)
        self.discussion_results['audio_strategy'] = audio_result
        
        logger.info(f"✅ Completed {len(self.discussion_results)} AI agent discussions")
    
    def _generate_script_with_ai_director(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI Director to generate script"""
        
        # Create video config for director
        video_config = GeneratedVideoConfig(
            target_platform=self.platform,
            category=self.category,
            duration_seconds=self.duration,
            topic=self.topic,
            style="viral",
            tone="engaging",
            target_audience="young adults",
            hook=f"Amazing {self.topic}",
            main_content=[f"Content about {self.topic}"],
            call_to_action="Follow for more!",
            visual_style="dynamic",
            color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
            text_overlays=[],
            transitions=["fade", "slide"],
            background_music_style="upbeat",
            voiceover_style="energetic",
            sound_effects=[],
            inspired_by_videos=[],
            predicted_viral_score=0.85
        )
        
        # Use Director to write script
        script_data = self.director.write_script(
            topic=self.topic,
            style="viral",
            duration=self.duration,
            platform=self.platform,
            category=self.category,
            patterns={'hooks': [], 'themes': ['engaging'], 'success_factors': ['viral']},
            incorporate_news=False
        )
        
        self.agent_decisions['script'] = {
            'agent': 'Director',
            'decision': 'Script generated with viral optimization',
            'data': script_data
        }
        
        return script_data
    
    def _make_structure_decisions(self, script_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI agents to make structure and timing decisions"""
        
        # Video structure analysis
        structure_analysis = self.structure_agent.analyze_video_structure(
            topic=self.topic,
            duration=self.duration,
            platform=self.platform.value,
            script_content=str(script_data)
        )
        
        # Timing analysis
        timing_analysis = self.timing_agent.analyze_clip_timing(
            structure_analysis=structure_analysis,
            total_duration=self.duration
        )
        
        # Continuity decision
        continuity_decision = self.continuity_agent.analyze_and_decide(
            topic=self.topic,
            content_type="educational",
            platform=self.platform.value,
            duration=self.duration
        )
        
        decisions = {
            'structure': structure_analysis,
            'timing': timing_analysis,
            'continuity': continuity_decision
        }
        
        self.agent_decisions['structure'] = {
            'agents': ['VideoStructureAgent', 'ClipTimingAgent', 'ContinuityDecisionAgent'],
            'decisions': decisions
        }
        
        return decisions
    
    def _make_voice_decisions(self, script_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Use Voice Director Agent for voice decisions"""
        
        voice_decision = self.voice_agent.select_optimal_voice(
            script=str(script_data),
            topic=self.topic,
            platform=self.platform,
            category=self.category,
            duration=self.duration
        )
        
        self.agent_decisions['voice'] = {
            'agent': 'VoiceDirectorAgent',
            'decision': voice_decision
        }
        
        return voice_decision
    
    def _make_media_decisions(self, script_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Use Media Type Agent for VEO2 vs image decisions"""
        
        # Create clip plan for media analysis
        clip_plan = {
            'total_clips': 4,
            'clip_duration': self.duration / 4,
            'topic': self.topic,
            'platform': self.platform.value
        }
        
        content_analysis = {
            'script': script_data,
            'topic': self.topic,
            'category': self.category.value
        }
        
        media_decision = self.media_agent.analyze_media_types(
            clip_plan=clip_plan,
            content_analysis=content_analysis
        )
        
        self.agent_decisions['media'] = {
            'agent': 'MediaTypeAgent',
            'decision': media_decision
        }
        
        return media_decision
    
    def _generate_video_with_ai_decisions(self, script_data: Dict[str, Any], 
                                        structure_decisions: Dict[str, Any],
                                        voice_decisions: Dict[str, Any],
                                        media_decisions: Dict[str, Any],
                                        config: Dict[str, Any]) -> str:
        """Generate video using all AI agent decisions"""
        
        # Create video generator
        video_generator = VideoGenerator(
            api_key=self.api_key,
            use_real_veo2=config.get('force_generation') != 'force_image_gen',
            use_vertex_ai=True
        )
        
        # Create enhanced video config with AI decisions
        video_config = GeneratedVideoConfig(
            target_platform=self.platform,
            category=self.category,
            duration_seconds=self.duration,
            topic=self.topic,
            style="viral",
            tone="engaging",
            target_audience="young adults",
            hook=self._extract_hook_from_script(script_data),
            main_content=self._extract_content_from_script(script_data),
            call_to_action=self._extract_cta_from_script(script_data),
            visual_style="dynamic",
            color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
            text_overlays=[],
            transitions=["fade", "slide"],
            background_music_style="upbeat",
            voiceover_style=voice_decisions.get('voice_style', 'energetic'),
            sound_effects=[],
            inspired_by_videos=[],
            predicted_viral_score=0.85,
            frame_continuity=structure_decisions.get('continuity', {}).get('recommendation') == 'enable',
            image_only_mode=config.get('force_generation') == 'force_image_gen',
            use_real_veo2=config.get('force_generation') != 'force_image_gen'
        )
        
        # Generate video with AI-enhanced config
        video_path = video_generator.generate_video(video_config)
        
        return video_path
    
    def _extract_hook_from_script(self, script_data: Dict[str, Any]) -> str:
        """Extract hook from script data"""
        if isinstance(script_data, dict):
            if 'hook' in script_data:
                hook = script_data['hook']
                if isinstance(hook, dict) and 'text' in hook:
                    return hook['text']
                return str(hook)
        return f"Amazing {self.topic}"
    
    def _extract_content_from_script(self, script_data: Dict[str, Any]) -> list:
        """Extract main content from script data"""
        if isinstance(script_data, dict):
            if 'segments' in script_data and isinstance(script_data['segments'], list):
                content = []
                for segment in script_data['segments']:
                    if isinstance(segment, dict) and 'text' in segment:
                        content.append(segment['text'])
                    else:
                        content.append(str(segment))
                return content
        return [f"Content about {self.topic}"]
    
    def _extract_cta_from_script(self, script_data: Dict[str, Any]) -> str:
        """Extract call-to-action from script data"""
        if isinstance(script_data, dict):
            if 'call_to_action' in script_data:
                return str(script_data['call_to_action'])
        return "Follow for more!"
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress for real-time UI"""
        return {
            'progress': 100,  # Working orchestrator completes when called
            'session_id': self.session_id,
            'current_phase': 'completed',
            'results': self.agent_decisions,
            'discussions_completed': len(self.discussion_results)
        }


def create_working_orchestrator(topic: str, platform: str, category: str,
                              duration: int, api_key: str) -> WorkingOrchestrator:
    """
    Factory function to create working orchestrator with AI agents
    """
    try:
        platform_enum = Platform(platform.lower())
    except ValueError:
        platform_enum = Platform.INSTAGRAM
    
    try:
        category_enum = VideoCategory(category.upper())
    except ValueError:
        category_enum = VideoCategory.LIFESTYLE
    
    return WorkingOrchestrator(
        api_key=api_key,
        topic=topic,
        platform=platform_enum,
        category=category_enum,
        duration=duration
    ) 