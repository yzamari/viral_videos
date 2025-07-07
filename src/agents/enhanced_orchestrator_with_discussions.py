"""
Enhanced AI Agent Orchestrator with Multi-Agent Discussions
Integrates collaborative decision-making through agent discussions
"""

import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .enhanced_orchestrator import EnhancedOrchestratorAgent
from .enhanced_multi_agent_discussion import (
    EnhancedMultiAgentDiscussionSystem, 
    AgentRole, 
    DiscussionTopic, 
    DiscussionResult
)
from .video_generation_topics import VideoGenerationTopics
from ..utils.logging_config import get_logger
from ..models.video_models import Platform, VideoCategory

logger = get_logger(__name__)

class DiscussionEnhancedOrchestrator(EnhancedOrchestratorAgent):
    """
    Enhanced orchestrator that uses multi-agent discussions for decision making
    
    This orchestrator extends the base EnhancedOrchestratorAgent to include
    collaborative decision-making through structured agent discussions.
    """
    
    def __init__(self, api_key: str, topic: str, category: str, platform: str, 
                 duration: int = 30, session_id: Optional[str] = None,
                 enable_discussions: bool = True, discussion_depth: str = "standard"):
        
        # Convert string parameters to expected enum types
        from ..models.video_models import Platform, VideoCategory
        
        # Convert platform string to enum
        platform_enum = Platform.YOUTUBE  # Default
        if platform.lower() == 'tiktok':
            platform_enum = Platform.TIKTOK
        elif platform.lower() == 'instagram':
            platform_enum = Platform.INSTAGRAM
        elif platform.lower() == 'facebook':
            platform_enum = Platform.FACEBOOK
        
        # Convert category string to enum
        category_enum = VideoCategory.COMEDY  # Default
        if category.lower() == 'education':
            category_enum = VideoCategory.EDUCATION
        elif category.lower() == 'entertainment':
            category_enum = VideoCategory.ENTERTAINMENT
        elif category.lower() == 'news':
            category_enum = VideoCategory.NEWS
        elif category.lower() == 'technology':
            category_enum = VideoCategory.TECHNOLOGY
        
        # CRITICAL FIX: Use provided session_id or create one, but don't inherit from base class
        # that creates its own session_id
        if session_id:
            self.session_id = session_id
        else:
            # Create new session_id only if not provided
            from datetime import datetime
            import uuid
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_id = f"{timestamp}_{str(uuid.uuid4())[:8]}"
        
        # Store parameters for discussion system (don't call super() to avoid session conflicts)
        self.api_key = api_key
        self.topic = topic  # Store as self.topic for compatibility
        self.original_topic = topic
        self.original_category = category
        self.original_platform = platform
        self.platform = platform  # Store as self.platform for compatibility
        self.category = category  # Store as self.category for compatibility  
        self.duration = duration  # Store duration for later use
        
        # CRITICAL: Agent discussions are ALWAYS ON
        self.enable_discussions = True  # Force enable
        self.discussion_depth = discussion_depth  # "light", "standard", "deep"
        
        # Initialize enhanced discussion system if enabled
        if self.enable_discussions:
            try:
                self.discussion_system = EnhancedMultiAgentDiscussionSystem(
                    api_key=api_key, 
                    session_id=self.session_id
                )
                logger.info("🤖 Enhanced Multi-Agent Discussion System ENABLED")
            except Exception as e:
                logger.error(f"Failed to initialize Enhanced Discussion System: {e}")
                self.discussion_system = None
                logger.warning("🔄 Continuing without enhanced discussions")
        else:
            self.discussion_system = None
            logger.info("🤖 Enhanced Multi-Agent Discussion System DISABLED")
        
        # Discussion results storage
        self.discussion_results = {}
        
        # Vertex AI configuration (will be set by factory function)
        self.vertex_ai_config = {
            'use_vertex_ai': False,
            'vertex_project_id': None,
            'vertex_location': None,
            'vertex_gcs_bucket': None
        }
        
        # Configure discussion depth
        self.discussion_configs = {
            "light": {
                "max_rounds": 3,
                "min_consensus": 0.5,
                "participating_agents": 3
            },
            "standard": {
                "max_rounds": 5,
                "min_consensus": 0.7,
                "participating_agents": 4
            },
            "deep": {
                "max_rounds": 8,
                "min_consensus": 0.8,
                "participating_agents": 6
            }
        }
    
    def orchestrate_complete_generation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate complete video generation with agent discussions
        
        This method extends the base orchestration to include collaborative
        decision-making at key stages.
        """
        logger.info("🎭 Starting Discussion-Enhanced Video Generation")
        logger.info(f"💬 Discussion mode: {self.discussion_depth}")
        
        # Phase 1: Initial Planning Discussion
        if self.enable_discussions:
            planning_result = self._conduct_planning_discussion(config)
            config.update(planning_result.decision)
            self.discussion_results['planning'] = planning_result
        
        # Phase 2: Master Planning (enhanced with discussion insights)
        master_plan = self._create_enhanced_master_plan(config)
        
        # Phase 3: Script Generation Discussion
        if self.enable_discussions:
            script_result = self._conduct_script_discussion(master_plan)
            master_plan.update(script_result.decision)
            self.discussion_results['script'] = script_result
        
        # Phase 4: Script Generation (with discussion guidance)
        script_data = self._orchestrate_script_generation(master_plan)
        
        # Phase 5: Visual Strategy Discussion
        if self.enable_discussions:
            visual_result = self._conduct_visual_discussion(script_data, master_plan)
            master_plan.update(visual_result.decision)
            self.discussion_results['visual'] = visual_result
        
        # Phase 6: Video Generation (with discussion guidance)
        video_data = self._orchestrate_video_generation(script_data, master_plan)
        
        # Phase 7: Audio Strategy Discussion
        if self.enable_discussions:
            audio_result = self._conduct_audio_discussion(script_data, video_data, master_plan)
            master_plan.update(audio_result.decision)
            self.discussion_results['audio'] = audio_result
        
        # Phase 8: Audio Generation (with discussion guidance)
        audio_data = self._orchestrate_audio_generation(script_data, video_data, master_plan)
        
        # Phase 9: Final Assembly Discussion
        if self.enable_discussions:
            assembly_result = self._conduct_assembly_discussion(script_data, video_data, audio_data, master_plan)
            master_plan.update(assembly_result.decision)
            self.discussion_results['assembly'] = assembly_result
        
        # Phase 10: Final Assembly (with discussion guidance)
        final_video = self._orchestrate_final_assembly(script_data, video_data, audio_data, master_plan)
        
        # Phase 11: Save Discussion Results
        self._save_discussion_summary()
        
        # Create comprehensive result
        result = {
            'success': True,
            'final_video_path': final_video.get('final_video_path'),
            'master_plan': master_plan,
            'script_data': script_data,
            'video_data': video_data,
            'audio_data': audio_data,
            'discussion_results': self.discussion_results,
            'session_id': self.session_id,
            'generation_metadata': {
                'discussions_enabled': self.enable_discussions,
                'discussion_depth': self.discussion_depth,
                'total_discussions': len(self.discussion_results),
                'average_consensus': self._calculate_average_consensus(),
                'key_insights': self._extract_all_insights()
            }
        }
        
        logger.info("🎯 Discussion-Enhanced Generation Complete!")
        logger.info(f"📊 Conducted {len(self.discussion_results)} agent discussions")
        logger.info(f"🤝 Average consensus: {result['generation_metadata']['average_consensus']:.2f}")
        
        return result
    
    def _conduct_planning_discussion(self, config: Dict[str, Any]) -> Any:
        """Conduct initial planning discussion"""
        logger.info("🗣️ Starting Planning Discussion")
        
        # Create planning context
        context = {
            'topic': self.topic,
            'category': self.category,
            'platform': self.platform,
            'duration': self.duration,
            'config': config
        }
        
        # Define participating agents based on discussion depth - ALWAYS include Senior Manager
        depth_config = self.discussion_configs[self.discussion_depth]
        base_participating_agents = [
            AgentRole.SENIOR_MANAGER,  # Always included for oversight
            AgentRole.ORCHESTRATOR,
            AgentRole.TREND_ANALYST,
            AgentRole.SCRIPT_WRITER,
            AgentRole.DIRECTOR
        ]
        
        # Add more agents based on depth
        if self.discussion_depth in ['standard', 'deep']:
            base_participating_agents.extend([
                AgentRole.AUDIENCE_ADVOCATE,
                AgentRole.QUALITY_GUARD
            ])
        
        if self.discussion_depth == 'deep':
            base_participating_agents.extend([
                AgentRole.DATA_SCIENTIST,
                AgentRole.PSYCHOLOGY_EXPERT,
                AgentRole.BRAND_STRATEGIST
            ])
        
        participating_agents = base_participating_agents[:depth_config['participating_agents']]
        
        # Create discussion topic
        topic = DiscussionTopic(
            topic_id="initial_planning",
            title="Initial Video Generation Planning",
            description="Determine overall strategy and approach for video generation",
            context=context,
            required_decisions=[
                "overall_strategy",
                "content_approach",
                "style_direction",
                "target_audience_focus",
                "success_metrics"
            ],
            max_rounds=depth_config['max_rounds'],
            min_consensus=depth_config['min_consensus']
        )
        
        # Conduct discussion
        if self.discussion_system:
            result = self.discussion_system.start_discussion(topic, participating_agents)
            logger.info(f"✅ Planning Discussion: {result.consensus_level:.2f} consensus")
            return result
        else:
            # Return dummy result when discussions are disabled
            class DummyResult:
                def __init__(self):
                    self.consensus_level = 1.0
                    self.decision = {}
                    self.key_insights = []
                    self.total_rounds = 0
                    self.participating_agents = []
            return DummyResult()
    
    def _conduct_script_discussion(self, master_plan: Dict[str, Any]) -> Any:
        """Conduct script optimization discussion"""
        logger.info("🗣️ Starting Script Discussion")
        
        context = {
            'master_plan': master_plan,
            'topic': self.topic,
            'platform': self.platform,
            'target_duration': self.duration
        }
        
        # Script optimization discussion with comprehensive agent participation
        participating_agents = [
            AgentRole.SENIOR_MANAGER,     # Strategic oversight
            AgentRole.SCRIPT_WRITER,      # Core script expertise
            AgentRole.DIALOGUE_MASTER,    # Natural dialogue
            AgentRole.PACE_MASTER,        # Timing optimization
            AgentRole.TREND_ANALYST,      # Viral patterns
            AgentRole.DIRECTOR,           # Visual storytelling
            AgentRole.AUDIENCE_ADVOCATE,  # User experience
            AgentRole.ORCHESTRATOR        # Coordination
        ]
        
        # Limit based on discussion depth
        if self.discussion_depth == 'light':
            participating_agents = participating_agents[:4]
        elif self.discussion_depth == 'standard':
            participating_agents = participating_agents[:6]
        # Deep mode uses all agents
        
        # Create discussion topic
        topic = VideoGenerationTopics.script_optimization(context)
        topic.max_rounds = self.discussion_configs[self.discussion_depth]['max_rounds']
        topic.min_consensus = self.discussion_configs[self.discussion_depth]['min_consensus']
        
        if self.discussion_system:
            result = self.discussion_system.start_discussion(topic, participating_agents)
            logger.info(f"✅ Script Discussion: {result.consensus_level:.2f} consensus")
            return result
        else:
            # Return dummy result when discussions are disabled
            class DummyResult:
                def __init__(self):
                    self.consensus_level = 1.0
                    self.decision = {}
                    self.key_insights = []
                    self.total_rounds = 0
                    self.participating_agents = []
            return DummyResult()
    
    def _conduct_visual_discussion(self, script_data: Dict[str, Any], master_plan: Dict[str, Any]) -> Any:
        """Conduct visual strategy discussion"""
        logger.info("🗣️ Starting Visual Strategy Discussion")
        
        context = {
            'script_data': script_data,
            'master_plan': master_plan,
            'platform': self.platform,
            'veo_capabilities': 'veo-2-available'
        }
        
        topic = VideoGenerationTopics.visual_strategy(context)
        topic.max_rounds = self.discussion_configs[self.discussion_depth]['max_rounds']
        topic.min_consensus = self.discussion_configs[self.discussion_depth]['min_consensus']
        
        participating_agents = [
            AgentRole.DIRECTOR,
            AgentRole.VIDEO_GENERATOR,
            AgentRole.SCRIPT_WRITER,
            AgentRole.ORCHESTRATOR
        ]
        
        if self.discussion_system:
            result = self.discussion_system.start_discussion(topic, participating_agents)
            logger.info(f"✅ Visual Discussion: {result.consensus_level:.2f} consensus")
            return result
        else:
            # Return dummy result when discussions are disabled
            class DummyResult:
                def __init__(self):
                    self.consensus_level = 1.0
                    self.decision = {}
                    self.key_insights = []
                    self.total_rounds = 0
                    self.participating_agents = []
            return DummyResult()
    
    def _conduct_audio_discussion(self, script_data: Dict[str, Any], video_data: Dict[str, Any], 
                                master_plan: Dict[str, Any]) -> Any:
        """Conduct audio synchronization discussion"""
        logger.info("🗣️ Starting Audio Discussion")
        
        context = {
            'script_data': script_data,
            'video_data': video_data,
            'master_plan': master_plan,
            'video_duration': video_data.get('total_duration', self.duration)
        }
        
        topic = VideoGenerationTopics.audio_synchronization(context)
        topic.max_rounds = self.discussion_configs[self.discussion_depth]['max_rounds']
        topic.min_consensus = self.discussion_configs[self.discussion_depth]['min_consensus']
        
        participating_agents = [
            AgentRole.SOUNDMAN,
            AgentRole.EDITOR,
            AgentRole.ORCHESTRATOR,
            AgentRole.SCRIPT_WRITER
        ]
        
        if self.discussion_system:
            result = self.discussion_system.start_discussion(topic, participating_agents)
            logger.info(f"✅ Audio Discussion: {result.consensus_level:.2f} consensus")
            return result
        else:
            # Return dummy result when discussions are disabled
            class DummyResult:
                def __init__(self):
                    self.consensus_level = 1.0
                    self.decision = {}
                    self.key_insights = []
                    self.total_rounds = 0
                    self.participating_agents = []
            return DummyResult()
    
    def _conduct_assembly_discussion(self, script_data: Dict[str, Any], video_data: Dict[str, Any], 
                                   audio_data: Dict[str, Any], master_plan: Dict[str, Any]) -> Any:
        """Conduct final assembly discussion"""
        logger.info("🗣️ Starting Assembly Discussion")
        
        context = {
            'script_data': script_data,
            'video_data': video_data,
            'audio_data': audio_data,
            'master_plan': master_plan,
            'platform': self.platform
        }
        
        topic = DiscussionTopic(
            topic_id="final_assembly",
            title="Final Video Assembly Strategy",
            description="Determine final assembly approach and quality optimization",
            context=context,
            required_decisions=[
                "assembly_approach",
                "quality_optimization",
                "final_adjustments",
                "platform_specific_tweaks",
                "quality_control_measures"
            ],
            max_rounds=self.discussion_configs[self.discussion_depth]['max_rounds'],
            min_consensus=self.discussion_configs[self.discussion_depth]['min_consensus']
        )
        
        participating_agents = [
            AgentRole.EDITOR,
            AgentRole.ORCHESTRATOR,
            AgentRole.SOUNDMAN,
            AgentRole.VIDEO_GENERATOR
        ]
        
        if self.discussion_system:
            result = self.discussion_system.start_discussion(topic, participating_agents)
            logger.info(f"✅ Assembly Discussion: {result.consensus_level:.2f} consensus")
            return result
        else:
            # Return dummy result when discussions are disabled
            class DummyResult:
                def __init__(self):
                    self.consensus_level = 1.0
                    self.decision = {}
                    self.key_insights = []
                    self.total_rounds = 0
                    self.participating_agents = []
            return DummyResult()
    
    def _create_enhanced_master_plan(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create master plan enhanced with discussion insights"""
        # Create base plan manually since super() method doesn't exist
        base_plan = {
            'topic': self.original_topic,
            'category': self.original_category,
            'platform': self.original_platform,
            'duration': self.duration,
            'target_audience': '18-34 viral content consumers',
            'style': 'viral',
            'tone': 'engaging',
            'hook': 'Stop scrolling! You won\'t believe this...',
            'call_to_action': 'Follow for more viral content!',
            'visual_style': 'dynamic',
            'color_scheme': ['#FF6B6B', '#4ECDC4', '#FFFFFF'],
            'transitions': ['fade', 'slide'],
            'background_music_style': 'upbeat',
            'voiceover_style': 'natural',
            'image_only_mode': config.get('image_only', False),
            'use_real_veo2': config.get('use_real_veo2', True),
            'session_id': self.session_id
        }
        
        # Enhance with discussion insights if available
        if 'planning' in self.discussion_results:
            planning_insights = self.discussion_results['planning']
            
            # Update plan with discussion decisions
            if hasattr(planning_insights, 'decision'):
                if 'overall_strategy' in planning_insights.decision:
                    base_plan['strategy'] = planning_insights.decision['overall_strategy']
                
                if 'content_approach' in planning_insights.decision:
                    base_plan['content_approach'] = planning_insights.decision['content_approach']
                
                if 'style_direction' in planning_insights.decision:
                    base_plan['visual_style'] = planning_insights.decision['style_direction']
                
                if 'target_audience_focus' in planning_insights.decision:
                    base_plan['target_audience'] = planning_insights.decision['target_audience_focus']
            
            # Add discussion metadata
            base_plan['discussion_enhanced'] = True
            base_plan['planning_consensus'] = planning_insights.consensus_level
            base_plan['planning_insights'] = planning_insights.key_insights
        
        return base_plan
    
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
            import json
            json.dump(summary, f, indent=2, default=str)
        
        # Also save individual discussion files
        discussions_dir = os.path.join(main_session_dir, "agent_discussions")
        os.makedirs(discussions_dir, exist_ok=True)
        
        for topic_name, result in self.discussion_results.items():
            discussion_file = os.path.join(discussions_dir, f"discussion_{topic_name}.json")
            with open(discussion_file, 'w') as f:
                import json
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
        if hasattr(self.discussion_system, 'visualizer'):
            session_summary = self.discussion_system.visualizer.generate_session_summary()
            if session_summary:
                logger.info("📊 ENHANCED SESSION ANALYTICS:")
                logger.info(f"   Success Rate: {session_summary['session_overview']['success_rate']:.1%}")
                logger.info(f"   Total Duration: {session_summary['session_overview']['total_duration_seconds']:.1f}s")
                logger.info(f"   Most Active Agent: {list(session_summary['most_active_agents'].keys())[0] if session_summary['most_active_agents'] else 'N/A'}")
        
        # Log key metrics
        logger.info("📊 DISCUSSION SUMMARY:")
        logger.info(f"   Total Discussions: {len(self.discussion_results)}")
        logger.info(f"   Average Consensus: {summary['overall_metrics']['average_consensus']:.2f}")
        logger.info(f"   Total Discussion Rounds: {summary['overall_metrics']['total_rounds']}")
        logger.info(f"   Participating Agents: {summary['overall_metrics']['unique_participating_agents']}")
        
        # Print enhanced summary
        logger.info("🎯 Discussion-Enhanced Generation Complete!")
    
    def _calculate_average_consensus(self) -> float:
        """Calculate average consensus across all discussions"""
        if not self.discussion_results:
            return 0.0
        
        total_consensus = sum(result.consensus_level for result in self.discussion_results.values())
        return total_consensus / len(self.discussion_results)
    
    def _extract_all_insights(self) -> List[str]:
        """Extract key insights from all discussions"""
        all_insights = []
        for result in self.discussion_results.values():
            all_insights.extend(result.key_insights)
        
        # Return unique insights
        return list(set(all_insights))[:10]  # Top 10 unique insights

    def _orchestrate_script_generation(self, master_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script with discussion guidance"""
        try:
            # Use the original video generator for script generation
            from ..generators.video_generator import VideoGenerator
            from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory
            
            # Create video generator with Vertex AI VEO-3 configuration
            generator = VideoGenerator(
                api_key=self.api_key,
                use_real_veo2=master_plan.get('use_real_veo2', True),
                use_vertex_ai=self.vertex_ai_config.get('use_vertex_ai', True),
                project_id=self.vertex_ai_config.get('vertex_project_id') or "viralgen-464411",
                location=self.vertex_ai_config.get('vertex_location') or "us-central1"
            )
            
            # Convert platform and category strings to enums
            platform_enum = Platform.YOUTUBE
            if master_plan['platform'].lower() == 'tiktok':
                platform_enum = Platform.TIKTOK
            elif master_plan['platform'].lower() == 'instagram':
                platform_enum = Platform.INSTAGRAM
            
            category_enum = VideoCategory.COMEDY
            if master_plan['category'].lower() == 'news':
                category_enum = VideoCategory.NEWS
            elif master_plan['category'].lower() == 'education':
                category_enum = VideoCategory.EDUCATION
            
            # Create configuration
            config = GeneratedVideoConfig(
                target_platform=platform_enum,
                category=category_enum,
                duration_seconds=master_plan['duration'],
                topic=master_plan['topic'],
                style=master_plan.get('style', 'viral'),
                tone=master_plan.get('tone', 'engaging'),
                target_audience=master_plan.get('target_audience', '18-34 viral content consumers'),
                hook=master_plan.get('hook', 'Stop scrolling! You won\'t believe this...'),
                main_content=[f"Amazing content about {master_plan['topic']}"],
                call_to_action=master_plan.get('call_to_action', 'Follow for more viral content!'),
                visual_style=master_plan.get('visual_style', 'dynamic'),
                color_scheme=master_plan.get('color_scheme', ['#FF6B6B', '#4ECDC4', '#FFFFFF']),
                text_overlays=[],
                transitions=master_plan.get('transitions', ['fade', 'slide']),
                background_music_style=master_plan.get('background_music_style', 'upbeat'),
                voiceover_style=master_plan.get('voiceover_style', 'natural'),
                sound_effects=[],
                inspired_by_videos=[],
                predicted_viral_score=0.85,
                frame_continuity=True,
                image_only_mode=master_plan.get('image_only_mode', False)
            )
            
            # Generate video
            result = generator.generate_video(config)
            
            return {
                'script': result.script if result else f"This is a {master_plan['duration']} second video about {master_plan['topic']}",
                'scenes': getattr(result, 'scenes', []) if result else [],
                'duration': master_plan['duration'],
                'success': True,
                'config': config,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Script generation failed: {e}")
            return {
                'script': f"This is a {master_plan['duration']} second video about {master_plan['topic']}",
                'scenes': [],
                'duration': master_plan['duration'],
                'success': False,
                'error': str(e)
            }
    
    def _orchestrate_video_generation(self, script_data: Dict[str, Any], master_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video with discussion guidance"""
        try:
            # If script generation already produced a result, use it
            if 'result' in script_data and script_data['result']:
                result = script_data['result']
                return {
                    'clips': getattr(result, 'clips', []),
                    'total_duration': master_plan['duration'],
                    'success': True,
                    'video_path': result.file_path if result else None,
                    'result': result
                }
            else:
                return {
                    'clips': [],
                    'total_duration': master_plan['duration'],
                    'success': False,
                    'error': 'No video result from script generation'
                }
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            return {
                'clips': [],
                'total_duration': master_plan['duration'],
                'success': False,
                'error': str(e)
            }
    
    def _orchestrate_audio_generation(self, script_data: Dict[str, Any], video_data: Dict[str, Any], master_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio with discussion guidance"""
        try:
            # Audio is typically generated as part of the video generation process
            if 'result' in script_data and script_data['result']:
                result = script_data['result']
                return {
                    'audio_path': getattr(result, 'audio_path', None),
                    'duration': master_plan['duration'],
                    'success': True,
                    'result': result
                }
            else:
                return {
                    'audio_path': None,
                    'duration': master_plan['duration'],
                    'success': False,
                    'error': 'No audio result from video generation'
                }
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            return {
                'audio_path': None,
                'duration': master_plan['duration'],
                'success': False,
                'error': str(e)
            }
    
    def _orchestrate_final_assembly(self, script_data: Dict[str, Any], video_data: Dict[str, Any], audio_data: Dict[str, Any], master_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble final video with discussion guidance"""
        try:
            # Final assembly is typically done as part of the video generation process
            if 'result' in script_data and script_data['result']:
                result = script_data['result']
                return {
                    'final_video_path': result.file_path if result else None,
                    'success': True,
                    'result': result
                }
            else:
                return {
                    'final_video_path': None,
                    'success': False,
                    'error': 'No final video result'
                }
        except Exception as e:
            logger.error(f"❌ Final assembly failed: {e}")
            return {
                'final_video_path': None,
                'success': False,
                'error': str(e)
            }

# Factory function for easy creation
def create_discussion_enhanced_orchestrator(api_key: str, topic: str, category: str, 
                                          platform: str, duration: int = 30,
                                          discussion_mode: str = "standard",
                                          session_id: Optional[str] = None,
                                          use_vertex_ai: bool = True,
                                          vertex_project_id: str = "viralgen-464411",
                                          vertex_location: str = "us-central1",
                                          vertex_gcs_bucket: str = "viral-veo2-results",
                                          prefer_veo3: bool = True,
                                          enable_native_audio: bool = True) -> DiscussionEnhancedOrchestrator:
    """
    Factory function to create discussion-enhanced orchestrator
    
    Args:
        api_key: Google AI API key
        topic: Video topic
        category: Video category
        platform: Target platform
        duration: Video duration in seconds
        discussion_mode: "light", "standard", or "deep"
        session_id: Optional session ID
        use_vertex_ai: Enable Vertex AI VEO-2/VEO-3 (default: True)
        vertex_project_id: Google Cloud project ID
        vertex_location: Google Cloud location
        vertex_gcs_bucket: GCS bucket for VEO-2/VEO-3 videos
        prefer_veo3: Prefer VEO-3 over VEO-2 (default: True)
        enable_native_audio: Enable native audio generation with VEO-3 (default: True)
    
    Returns:
        DiscussionEnhancedOrchestrator instance
    """
    orchestrator = DiscussionEnhancedOrchestrator(
        api_key=api_key,
        topic=topic,
        category=category,
        platform=platform,
        duration=duration,
        session_id=session_id,
        enable_discussions=True,
        discussion_depth=discussion_mode
    )
    
    # Store Vertex AI configuration for video generation
    orchestrator.vertex_ai_config = {
        'use_vertex_ai': use_vertex_ai,
        'vertex_project_id': vertex_project_id,
        'vertex_location': vertex_location,
        'vertex_gcs_bucket': vertex_gcs_bucket,
        'prefer_veo3': prefer_veo3,
        'enable_native_audio': enable_native_audio
    }
    
    return orchestrator 