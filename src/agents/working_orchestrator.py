"""
Enhanced Working AI Agent Orchestrator
Comprehensive mission-driven system with ALL features and proper OOP design """

import time
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

try:
    from ..generators.video_generator  import VideoGenerator
    from ..generators.director  import Director
    from ..generators.enhanced_script_processor  import EnhancedScriptProcessor
    from ..generators.integrated_multilang_generator  import IntegratedMultilingualGenerator
    from ..models.video_models import (
        GeneratedVideoConfig,
        Platform,
        VideoCategory,
        Language
    )
    from ..utils.logging_config  import get_logger
    from .continuity_decision_agent  import ContinuityDecisionAgent
    from .voice_director_agent  import VoiceDirectorAgent
    from .video_composition_agents import (
        VideoStructureAgent,
        ClipTimingAgent,
        VisualElementsAgent,
        MediaTypeAgent
    )
    from .multi_agent_discussion import (
        MultiAgentDiscussionSystem,
        AgentRole,
        DiscussionTopic
    )
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from src.generators.video_generator import VideoGenerator
    from src.generators.director import Director
    from src.generators.enhanced_script_processor import EnhancedScriptProcessor
    from src.generators.integrated_multilang_generator import IntegratedMultilingualGenerator
    from src.models.video_models import (
        GeneratedVideoConfig,
        Platform,
        VideoCategory,
        Language
    )
    from src.utils.logging_config import get_logger
    from src.agents.continuity_decision_agent import ContinuityDecisionAgent
    from src.agents.voice_director_agent import VoiceDirectorAgent
    from src.agents.video_composition_agents import (
        VideoStructureAgent,
        ClipTimingAgent,
        VisualElementsAgent,
        MediaTypeAgent
    )
    from src.agents.multi_agent_discussion import (
        MultiAgentDiscussionSystem,
        AgentRole,
        DiscussionTopic
    )

logger = get_logger(__name__)

class OrchestratorMode(str, Enum):
    """Available orchestrator modes for different use cases"""
    SIMPLE = "simple"           # Basic generation, fast (3 agents)
    ENHANCED = "enhanced"       # 7 agents with discussions
    ADVANCED = "advanced"       # 15+ agents with comprehensive discussions
    MULTILINGUAL = "multilingual"  # Multilingual generation (8 agents)
    PROFESSIONAL = "professional"  # Maximum quality with all features (19+ agents)

class WorkingOrchestrator:
    """
    Enhanced working orchestrator with multi-agent AI system
    Supports multiple generation modes and comprehensive video creation
    """

    def __init__(self, api_key: str, mission: str, platform: Platform,
                 category: VideoCategory, duration: int,
                 style: str = "viral", tone: str = "engaging",
                 target_audience: str = "general audience",
                 visual_style: str = "dynamic",
                 mode: OrchestratorMode = OrchestratorMode.ENHANCED,
                 session_id: Optional[str] = None,
                 language: Language = Language.ENGLISH_US,
                 cheap_mode: bool = True,
                 cheap_mode_level: str = "full"):
        """
        Initialize Working Orchestrator

        Args:
            api_key: Google AI API key
            mission: Video mission/topic
            platform: Target platform
            category: Video category
            duration: Video duration in seconds
            style: Content style (viral, educational, professional)
            tone: Content tone (engaging, professional, humorous)
            target_audience: Target audience description
            visual_style: Visual style (dynamic, minimalist, cinematic)
            mode: Orchestrator mode (simple to professional)
            session_id: Optional session ID
            language: Target language for content
            cheap_mode: Enable cost-saving mode (default: True)
            cheap_mode_level: Granular cheap mode (full, audio, video)
        """
        self.api_key = api_key
        self.mission = mission
        self.platform = platform
        self.category = category
        self.duration = duration
        self.style = style
        self.tone = tone
        self.target_audience = target_audience
        self.visual_style = visual_style
        self.mode = mode
        self.language = language
        self.cheap_mode = cheap_mode
        self.cheap_mode_level = cheap_mode_level
        
        # Generate session ID if not provided
        if session_id:
            self.session_id = session_id
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_id = f"session_{timestamp}"
        
        # CRITICAL FIX: Activate session in session manager
        from ..utils.session_manager import session_manager
        if session_manager:
            # If session_id was provided, we need to activate it in session manager
            if session_id:
                # Check if session exists, if not create it
                try:
                    session_info = session_manager.get_session_info(session_id)
                    logger.info(f"🔄 Activating existing session: {session_id}")
                    # Properly activate the session with all required data
                    session_manager.current_session = session_id
                    # Reconstruct session data from the session info
                    session_manager.session_data = {
                        "session_id": session_id,
                        "session_dir": session_info.get("session_dir", os.path.join("outputs", session_id)),
                        "subdirs": {
                            "logs": os.path.join("outputs", session_id, "logs"),
                            "scripts": os.path.join("outputs", session_id, "scripts"),
                            "audio": os.path.join("outputs", session_id, "audio"),
                            "video_clips": os.path.join("outputs", session_id, "video_clips"),
                            "images": os.path.join("outputs", session_id, "images"),
                            "ai_agents": os.path.join("outputs", session_id, "ai_agents"),
                            "discussions": os.path.join("outputs", session_id, "discussions"),
                            "final_output": os.path.join("outputs", session_id, "final_output"),
                            "metadata": os.path.join("outputs", session_id, "metadata"),
                            "comprehensive_logs": os.path.join("outputs", session_id, "comprehensive_logs"),
                            "temp_files": os.path.join("outputs", session_id, "temp_files"),
                            "fallback_content": os.path.join("outputs", session_id, "fallback_content"),
                            "debug_info": os.path.join("outputs", session_id, "debug_info"),
                            "performance_metrics": os.path.join("outputs", session_id, "performance_metrics"),
                            "user_configs": os.path.join("outputs", session_id, "user_configs"),
                            "error_logs": os.path.join("outputs", session_id, "error_logs"),
                            "success_metrics": os.path.join("outputs", session_id, "success_metrics"),
                            "decisions": os.path.join("outputs", session_id, "decisions"),
                            "subtitles": os.path.join("outputs", session_id, "subtitles"),
                            "overlays": os.path.join("outputs", session_id, "overlays")
                        },
                        "ai_decisions": session_info.get("ai_decisions", {}),
                        "generation_log": session_info.get("generation_steps", []),
                        "errors": session_info.get("errors", []),
                        "warnings": session_info.get("warnings", []),
                        "tracked_files": {},
                        "file_counts": {subdir: 0 for subdir in [
                            "logs", "scripts", "audio", "video_clips", "images", "ai_agents", 
                            "discussions", "final_output", "metadata", "comprehensive_logs",
                            "temp_files", "fallback_content", "debug_info", "performance_metrics",
                            "user_configs", "error_logs", "success_metrics", "decisions", 
                            "subtitles", "overlays"
                        ]},
                        "total_files_created": session_info.get("total_files", 0),
                        "comprehensive_logger": None
                    }
                except ValueError:
                    # Session doesn't exist, create it
                    logger.info(f"🆕 Creating new session in session manager: {session_id}")
                    session_manager.create_session(
                        topic=mission,
                        platform=platform.value,
                        duration=duration,
                        category=category.value
                    )
            else:
                # Create new session in session manager
                logger.info(f"🆕 Creating new session in session manager: {self.session_id}")
                session_manager.create_session(
                    topic=mission,
                    platform=platform.value,
                    duration=duration,
                    category=category.value
                )
        else:
            logger.warning("⚠️ Session manager not available")
        
        # Initialize AI clients
        self.multilang_generator = IntegratedMultilingualGenerator(api_key, "outputs")

        logger.info(f"🎬 WorkingOrchestrator initialized")
        logger.info(f"   Mission: {mission}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Mode: {mode.value}")
        logger.info(f"   Style: {style}")
        logger.info(f"   Tone: {tone}")
        logger.info(f"   Target Audience: {target_audience}")
        logger.info(f"   Visual Style: {visual_style}")

        # Initialize core AI agents (always available)
        self.director = Director(api_key)
        self.continuity_agent = ContinuityDecisionAgent(api_key)
        self.voice_agent = VoiceDirectorAgent(api_key)

        # Initialize enhanced agents based on mode
        self._initialize_agents_by_mode()

        # Initialize discussion systems based on mode
        self._initialize_discussion_systems()
        
        # Results storage
        self.agent_decisions = {}
        self.discussion_results = {}
        self.composition_decisions = {}
        self.trending_insights = {}
        # Session ID already set above, don't overwrite it
        
        logger.info(f"🎬 Enhanced Working Orchestrator initialized ({mode.value})")
        logger.info(f"   Mission: {mission}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Session: {self.session_id}")
        logger.info(f"   Mode: {mode.value}")
        logger.info(f"   Agents: {self._count_agents_used()}")

    def _initialize_agents_by_mode(self):
        """Initialize agents based on orchestrator mode"""
        if self.mode == OrchestratorMode.SIMPLE:
            # Simple mode: Core agents only
            self.script_processor = None
            self.structure_agent = None
            self.timing_agent = None
            self.visual_agent = None
            self.media_agent = None
            self.multilang_generator = None

        elif self.mode == OrchestratorMode.ENHANCED:
            # Enhanced mode: 7 agents with discussions
            self.script_processor = EnhancedScriptProcessor(self.api_key)
            self.structure_agent = VideoStructureAgent(self.api_key)
            self.timing_agent = ClipTimingAgent(self.api_key)
            self.visual_agent = VisualElementsAgent(self.api_key)
            self.media_agent = MediaTypeAgent(self.api_key)
            self.multilang_generator = None

        elif self.mode == OrchestratorMode.MULTILINGUAL:
            # Multilingual mode: Core agents + multilingual support
            self.script_processor = EnhancedScriptProcessor(self.api_key)
            self.structure_agent = VideoStructureAgent(self.api_key)
            self.timing_agent = ClipTimingAgent(self.api_key)
            self.visual_agent = VisualElementsAgent(self.api_key)
            self.media_agent = MediaTypeAgent(self.api_key)
            self.multilang_generator = IntegratedMultilingualGenerator(self.api_key)

        else:  # ADVANCED or PROFESSIONAL
            # Full feature set: All agents
            self.script_processor = EnhancedScriptProcessor(self.api_key)
            self.structure_agent = VideoStructureAgent(self.api_key)
            self.timing_agent = ClipTimingAgent(self.api_key)
            self.visual_agent = VisualElementsAgent(self.api_key)
            self.media_agent = MediaTypeAgent(self.api_key)
            self.multilang_generator = IntegratedMultilingualGenerator(self.api_key)

    def _initialize_discussion_systems(self):
        """Initialize discussion systems based on mode"""
        if self.mode == OrchestratorMode.SIMPLE:
            self.discussion_system = None

        elif self.mode in [OrchestratorMode.ENHANCED, OrchestratorMode.MULTILINGUAL]:
            self.discussion_system = MultiAgentDiscussionSystem(
                self.api_key,
                self.session_id)

        else:  # ADVANCED or PROFESSIONAL
            self.discussion_system = MultiAgentDiscussionSystem(
                self.api_key,
                self.session_id)
            # Enhanced discussion systems would be initialized here for future expansion
    
    def generate_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video using comprehensive AI agent system

        Args:
            config: Generation configuration dictionary

        Returns:
            Generation result with success status and metadata """
        logger.info(f"🎬 Starting {self.mode.value} AI agent video generation")

        try:
            # Phase 1: CRITICAL - Make frame continuity decision FIRST
            # This decision impacts ALL subsequent choices (VEO model selection, composition, etc.)
            frame_continuity_decision = self._make_frame_continuity_decision(config)

            # Store decision for use throughout generation
            self.agent_decisions['frame_continuity'] = {
                'agent': 'ContinuityDecisionAgent',
                'decision': frame_continuity_decision
            }

            # Log the decision prominently
            continuity_status = "✅ ENABLED" if frame_continuity_decision['use_frame_continuity'] else "❌ DISABLED"
            logger.info(f"🎬 Frame Continuity Decision: {continuity_status}")
            logger.info(f"   Confidence: {frame_continuity_decision['confidence']:.2f}")
            logger.info(f"   Reason: {frame_continuity_decision['primary_reason']}")

            # Phase 2: Trending Analysis (if enabled)
            if config.get('enable_trending', False):
                self._analyze_trending_content(config)

            # Phase 3: AI Agent Discussions (mode-dependent)
            if self.mode != OrchestratorMode.SIMPLE and not self.cheap_mode:
                self._conduct_agent_discussions(config)
            elif self.cheap_mode:
                logger.info("💰 Skipping AI agent discussions in cheap mode")
            
            # Phase 4: Script Generation with AI Enhancement
            script_data = self._generate_enhanced_script(config)

            # Phase 5: Comprehensive AI Decision Making (with continuity context)
            decisions = self._make_comprehensive_decisions(
                script_data,
                config,
                frame_continuity_decision)

            # Phase 6: Video Generation with All Features (continuity-aware)
            if self.cheap_mode:
                video_path = self._generate_cheap_video(script_data, decisions, config)
            elif self.mode == OrchestratorMode.MULTILINGUAL and config.get('languages'):
                video_path = self._generate_multilingual_video(script_data, decisions, config)
            else:
                video_path = self._generate_enhanced_video(script_data, decisions, config)
            logger.info(f"✅ {self.mode.value} video generation completed: {video_path}")
            
            return {
                'success': True,
                'final_video_path': video_path,
                'session_id': self.session_id,
                'agent_decisions': self.agent_decisions,
                'discussion_results': self.discussion_results,
                'agents_used': self._count_agents_used(),
                'discussions_conducted': len(self.discussion_results),
                'optimization_level': f'{self.mode.value}_ai_enhanced',
                'mode': self.mode.value,
                'frame_continuity_decision': frame_continuity_decision
            }
            
        except Exception as e:
            logger.error(f"❌ {self.mode.value} video generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'agent_decisions': self.agent_decisions,
                'discussion_results': self.discussion_results,
                'mode': self.mode.value
            }

    def _make_frame_continuity_decision(
        self,
        config: Dict[str,
        Any]) -> Dict[str, Any]:
        """
        Make frame continuity decision at the beginning of generation
        This decision impacts:
        - VEO model selection (continuity requires VEO2 only)
        - Video composition (frame overlap handling)
        - Clip generation strategy
        """
        frame_continuity_mode = config.get('frame_continuity', 'auto')

        if frame_continuity_mode == 'on':
            # User forced continuity ON
            decision = {
                'use_frame_continuity': True,
                'confidence': 1.0,
                'primary_reason': 'User forced frame continuity ON',
                'agent_name': 'User Override',
                'requires_veo2_only': True,
                'frame_overlap_handling': 'remove_first_frame',
                'transition_strategy': 'last_to_first_frame'
            }
        elif frame_continuity_mode == 'off':
            # User forced continuity OFF
            decision = {
                'use_frame_continuity': False,
                'confidence': 1.0,
                'primary_reason': 'User forced frame continuity OFF',
                'agent_name': 'User Override',
                'requires_veo2_only': False,
                'frame_overlap_handling': 'none',
                'transition_strategy': 'standard_cuts'
            }
        else:
            # Auto mode - use AI agent to decide
            decision = self.continuity_agent.analyze_frame_continuity_need(
                topic=self.mission,
                category=self.category.value,
                platform=self.platform.value,
                duration=self.duration,
                style=self.style
            )

            # Enhance decision with technical requirements
            if decision['use_frame_continuity']:
                decision['requires_veo2_only'] = True
                decision['frame_overlap_handling'] = 'remove_first_frame'
                decision['transition_strategy'] = 'last_to_first_frame'
            else:
                decision['requires_veo2_only'] = False
                decision['frame_overlap_handling'] = 'none'
                decision['transition_strategy'] = 'standard_cuts'

        return decision

    def _analyze_trending_content(self, config: Dict[str, Any]):
        """Analyze trending content for insights"""
        logger.info("📈 Analyzing trending content...")

        # Fallback trending insights (could be enhanced with real trending analysis)
        self.trending_insights = {
            'common_keywords': ['viral', 'trending', 'engaging', 'compelling'],
            'avg_duration': 25,
            'best_hook_type': 'question',
            'optimal_engagement_triggers': [
                'Start with a question',
                'Use emotional hooks',
                'Include trending keywords',
                'Keep under 30 seconds'
            ],
            'viral_hooks': [
                'Did you know...',
                'This will blow your mind...',
                'Here\'s what nobody tells you...',
                'The secret to...'
            ]
        }

        self.agent_decisions['trending'] = {
            'agent': 'TrendingAnalyzer',
            'insights': self.trending_insights,
            'videos_analyzed': 0,
            'note': 'Using fallback trending data'
            }
    
    def _conduct_agent_discussions(self, config: Dict[str, Any]):
        """Conduct AI agent discussions based on mode"""
        logger.info("🤝 Conducting AI agent discussions...")

        if self.mode == OrchestratorMode.ENHANCED:
            self._conduct_enhanced_discussions(config)
        elif self.mode in [OrchestratorMode.ADVANCED, OrchestratorMode.PROFESSIONAL]:
            self._conduct_advanced_discussions(config)
        elif self.mode == OrchestratorMode.MULTILINGUAL:
            self._conduct_multilingual_discussions(config)

    def _conduct_enhanced_discussions(self, config: Dict[str, Any]):
        """Enhanced 7-agent discussions"""

        if not self.discussion_system:
            logger.warning("Discussion system not available, skipping discussions")
            return

        # Discussion 1: Script Strategy & Viral Optimization
        script_topic = DiscussionTopic( topic_id="script_strategy", title="Script Strategy & Viral Optimization", description=f"Create the most engaging script for mission: {self.mission}",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'duration': self.duration,
                'category': self.category.value,
                'style': self.style,
                'tone': self.tone,
                'target_audience': self.target_audience,
                'trending_insights': self.trending_insights
            }, required_decisions=["script_structure", "viral_hooks", "engagement_strategy"]
        )

        script_result = self.discussion_system.start_discussion(
            script_topic,
            [AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR]
        )
        self.discussion_results['script_strategy'] = script_result
        
        # Discussion 2: Visual & Technical Strategy
        visual_topic = DiscussionTopic( topic_id="visual_strategy", title="Visual Composition & Technical Approach", description=f"Optimal visual strategy for {self.platform.value} content",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'visual_style': self.visual_style,
                'force_generation': config.get('force_generation', 'auto'),
                'trending_insights': self.trending_insights
            }, required_decisions=["visual_style", "technical_approach", "generation_mode"]
        )

        visual_result = self.discussion_system.start_discussion(
            visual_topic,
            [AgentRole.VIDEO_GENERATOR, AgentRole.EDITOR]
        )
        self.discussion_results['visual_strategy'] = visual_result
        
        # Discussion 3: Audio & Production Strategy
        audio_topic = DiscussionTopic( topic_id="audio_strategy", title="Audio Production & Voice Strategy", description="Optimal audio approach for maximum engagement",
            context={
                'mission': self.mission,
                'duration': self.duration,
                'platform': self.platform.value,
                'target_audience': self.target_audience
            }, required_decisions=["voice_style", "audio_approach", "sound_design"]
        )

        audio_result = self.discussion_system.start_discussion(
            audio_topic,
            [AgentRole.SOUNDMAN, AgentRole.EDITOR]
        )
        self.discussion_results['audio_strategy'] = audio_result
        logger.info(f"✅ Completed {len(self.discussion_results)} enhanced discussions")

    def _conduct_advanced_discussions(self, config: Dict[str, Any]):
        """Advanced discussions for professional modes"""
        # Enhanced discussions would be implemented here
        # For now, use enhanced discussions as base
        self._conduct_enhanced_discussions(config)
        logger.info("✅ Advanced discussions completed")

    def _conduct_multilingual_discussions(self, config: Dict[str, Any]):
        """Multilingual-specific discussions"""
        # Conduct base discussions
        self._conduct_enhanced_discussions(config)

        if not self.discussion_system:
            logger.warning( "Discussion system not available, " "skipping enhanced discussions"
            )
            return

        # Add multilingual-specific discussion
        multilang_topic = DiscussionTopic( topic_id="multilingual_strategy", title="Multilingual Content Strategy", description="Optimize content for multiple languages and cultures",
            context={
                'mission': self.mission,
                'languages': config.get('languages', [Language.ENGLISH_US]),
                'cultural_adaptation': config.get('cultural_adaptation', True)
            }, required_decisions=["language_priority", "cultural_adaptation", "voice_selection"]
        )

        multilang_result = self.discussion_system.start_discussion(
            multilang_topic,
            [AgentRole.SCRIPT_WRITER, AgentRole.SOUNDMAN]
        )
        self.discussion_results['multilingual_strategy'] = multilang_result
        logger.info("✅ Multilingual discussions completed")

    def _generate_enhanced_script(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script with AI enhancement and processing"""
        logger.info("📝 Generating enhanced script...")

        # Use Director to create base script
        script_data = self.director.write_script(
            topic=self.mission,
            style=self.style,
            duration=self.duration,
            platform=self.platform,
            category=self.category,
            patterns={
                'hooks': self.trending_insights.get('viral_hooks', []),
                'themes': [self.tone],
                'success_factors': [self.style, 'engaging']
            }
        )

        # Enhanced script processing for advanced modes
        if self.script_processor and self.mode != OrchestratorMode.SIMPLE:
            processed_script = self.script_processor.process_script_for_tts(
                script_content=str(script_data),
                language=config.get('language', Language.ENGLISH_US),
                target_duration=self.duration
            )

            script_data['processed'] = processed_script

            self.agent_decisions['script_processing'] = {
                'agent': 'EnhancedScriptProcessor',
                'original_length': len(str(script_data)),
                'processed_length': len(processed_script.get('final_script', '')),
                'tts_ready': processed_script.get('tts_ready', False)
            }

        self.agent_decisions['script'] = {
            'agent': 'Director',
            'data': script_data,
            'enhanced': self.mode != OrchestratorMode.SIMPLE
        }
        
        return script_data
    
    def _make_comprehensive_decisions(self, script_data: Dict[str, Any], config: Dict[str, Any],
                                      frame_continuity_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Make comprehensive AI decisions based on mode"""
        logger.info("🧠 Making comprehensive AI decisions...")

        decisions = {}

        # Use the frame continuity decision that was already made
        decisions['continuity'] = frame_continuity_decision
        logger.info(f"✅ Using frame continuity decision: {frame_continuity_decision['use_frame_continuity']}")

        # Voice decisions with safe defaults
        voice_decision = self.voice_agent.analyze_content_and_select_voices(
            script=str(script_data),
            topic=self.mission,
            language=Language.ENGLISH_US,
            platform=self.platform,
            category=self.category,
            duration_seconds=self.duration,
            num_clips=4
        )
        
        # Ensure voice_decision is not None
        if voice_decision is None:
            voice_decision = {'voice_style': 'energetic', 'voices': []}
            
        decisions['voice'] = voice_decision
        self.agent_decisions['voice'] = {
            'agent': 'VoiceDirectorAgent',
            'decision': voice_decision
        }
        
        # Enhanced decisions for advanced modes
        if self.mode in [OrchestratorMode.ENHANCED, OrchestratorMode.ADVANCED,
                         OrchestratorMode.PROFESSIONAL, OrchestratorMode.MULTILINGUAL]:

            # Structure Analysis
            if self.structure_agent:
                structure_analysis = self.structure_agent.analyze_video_structure(
                    topic=self.mission,
                    category=self.category.value,
                    platform=self.platform.value,
                    total_duration=self.duration
                )
                decisions['structure'] = structure_analysis
                self.agent_decisions['structure'] = {
                    'agent': 'VideoStructureAgent',
                    'analysis': structure_analysis
                }

            # Timing Analysis
            if self.timing_agent and 'structure' in decisions:
                timing_analysis = self.timing_agent.analyze_clip_timings(
                    video_structure=decisions['structure'],
                    content_details={'duration': self.duration, 'mission': self.mission}
                )
                decisions['timing'] = timing_analysis
                self.agent_decisions['timing'] = {
                    'agent': 'ClipTimingAgent',
                    'analysis': timing_analysis
                }

            # Visual Elements
            if self.visual_agent:
                visual_analysis = self.visual_agent.design_visual_elements(
                    video_structure=decisions.get('structure', {}),
                    content_theme=self.mission,
                    platform=self.platform.value
                )
                decisions['visual'] = visual_analysis
                self.agent_decisions['visual'] = {
                    'agent': 'VisualElementsAgent',
                    'analysis': visual_analysis
                }

            # Media Type Analysis
            if self.media_agent and 'timing' in decisions:
                media_analysis = self.media_agent.analyze_media_types(
                    clip_plan=decisions['timing'],
                    content_analysis={'mission': self.mission, 'platform': self.platform.value}
                )
                decisions['media'] = media_analysis
                self.agent_decisions['media'] = {
                    'agent': 'MediaTypeAgent',
                    'analysis': media_analysis
                }
        
        logger.info(f"✅ Made {len(decisions)} comprehensive AI decisions")
        return decisions

    def _generate_multilingual_video(self, script_data: Dict[str, Any],
                                     decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate multilingual video"""
        logger.info("🌍 Generating multilingual video...")

        if not self.multilang_generator:
            logger.warning( "Multilingual generator not available, " "using standard video generation"
            )
            return self._generate_enhanced_video(script_data, decisions, config)

        languages = config.get('languages', [Language.ENGLISH_US])

        # Create enhanced video config
        video_config = self._create_enhanced_video_config(
            script_data,
            decisions,
            config)

        # Generate multilingual video
        try:
            multilang_result = self.multilang_generator.generate_multilingual_video_with_ai_voices(
                config=video_config,
                languages=languages,
                base_script=str(script_data)
            )

            # Return primary language video path
            primary_language = languages[0] if languages else Language.ENGLISH_US
            primary_video = multilang_result.language_versions.get(primary_language)

            if primary_video and hasattr(primary_video, 'video_path'):
                return primary_video.video_path
        except Exception as e:
            logger.error(f"Multilingual generation failed: {e}")

        # Fallback to regular generation
        return self._generate_enhanced_video(script_data, decisions, config)

    def _generate_enhanced_video(self, script_data: Dict[str, Any],
                                 decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate enhanced video with all AI decisions"""
        logger.info("🎬 Generating enhanced video with AI decisions...")

        try:
            # Create video generator with VEO3 disabled
            video_generator = VideoGenerator(
                api_key=self.api_key,
                use_real_veo2=config.get('force_generation') != 'force_image_gen',
                use_vertex_ai=True,
                prefer_veo3=False  # CRITICAL: Disable VEO3 as requested
            )

            # Create enhanced video config
            video_config = self._create_enhanced_video_config(
                script_data,
                decisions,
                config)

            # Generate video with AI-enhanced config
            video_result = video_generator.generate_video(video_config)

            # Handle different return types properly
            if isinstance(video_result, str):
                logger.info(f"✅ Video generation completed: {video_result}")
                return video_result
            elif hasattr(video_result, 'file_path'):
                logger.info(f"✅ Video generation completed: {video_result.file_path}")
                return video_result.file_path
            else:
                logger.warning(f"⚠️ Unexpected video result type: {type(video_result)}")
                return str(video_result)
                
        except Exception as e:
            logger.error(f"❌ enhanced video generation failed: {e}")
            # Re-raise the exception to be handled by the calling method
            raise

    def _create_enhanced_video_config(self, script_data: Dict[str, Any],
                                      decisions: Dict[str, Any], config: Dict[str, Any]) -> GeneratedVideoConfig:
        """Create enhanced video config with all AI decisions"""

        # Extract script components
        hook = self._extract_hook_from_script(script_data)
        main_content = self._extract_content_from_script(script_data)
        cta = self._extract_cta_from_script(script_data)

        # Apply AI decisions with safe defaults
        frame_continuity = decisions.get('continuity', {}).get('use_frame_continuity', False)
        voice_style = decisions.get('voice', {}).get('voice_style', 'energetic')
        visual_style = decisions.get('visual', {}).get('style', self.visual_style)

        # Enhanced configuration with platform and category for AI timing
        enhanced_config = GeneratedVideoConfig(
            target_platform=self.platform,
            category=self.category,
            duration_seconds=self.duration,
            topic=self.mission,
            session_id=self.session_id,  # CRITICAL: Pass the session ID from orchestrator
            style=self.style,
            tone=self.tone,
            target_audience=self.target_audience,
            hook=hook,
            main_content=main_content,
            call_to_action=cta,
            visual_style=visual_style,
            color_scheme=config.get('color_scheme', ["#FF6B6B", "#4ECDC4", "#FFFFFF"]),
            text_overlays=config.get('text_overlays', []),
            transitions=config.get('transitions', ["fade", "slide"]),
            background_music_style=config.get('background_music_style', "upbeat"),
            voiceover_style=voice_style,
            sound_effects=config.get('sound_effects', []),
            inspired_by_videos=config.get('inspired_by_videos', []),
            predicted_viral_score=config.get('predicted_viral_score', 0.85),
            frame_continuity=frame_continuity,
            image_only_mode=config.get('force_generation') == 'force_image_gen',
            use_real_veo2=config.get('force_generation') != 'force_image_gen',
            video_orientation=config.get('orientation', 'auto'),
            ai_decide_orientation=config.get('ai_decide_orientation', True)
        )
        
        logger.info(f"✅ Enhanced video config created with session_id: {self.session_id}")
        return enhanced_config
    
    def _extract_hook_from_script(self, script_data: Dict[str, Any]) -> str:
        """Extract hook from script data"""
        if isinstance(script_data, dict):
            if 'hook' in script_data:
                hook = script_data['hook']
                if isinstance(hook, dict) and 'text' in hook:
                    return hook['text']
                return str(hook)

        # Generate hook from mission
        mission_words = self.mission.split()
        meaningful_words = [word for word in mission_words if len(word) > 3]
            
        if meaningful_words:
            return f"Mission: {meaningful_words[0]}"
        else:
            return f"Mission: {self.mission}"
    
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
        return [f"Content for mission: {self.mission}"]
    
    def _extract_cta_from_script(self, script_data: Dict[str, Any]) -> str:
        """Extract call-to-action from script data"""
        if isinstance(script_data, dict):
            if 'processed' in script_data and 'final_script' in script_data['processed']:
                # Use processed script if available
                processed_script = script_data['processed']['final_script']
                sentences = processed_script.split('.')
                return sentences[-1].strip() if sentences else "Follow for more!"
            elif 'call_to_action' in script_data:
                return str(script_data['call_to_action'])
        return "Follow for more!"
    
    def _count_agents_used(self) -> int:
        """Count the number of agents used based on mode"""
        if self.mode == OrchestratorMode.SIMPLE:
            return 3  # Director, Continuity, Voice
        elif self.mode == OrchestratorMode.ENHANCED:
            return 7  # Core agents with enhanced features
        elif self.mode == OrchestratorMode.MULTILINGUAL:
            return 8  # Core agents + multilingual
        elif self.mode == OrchestratorMode.ADVANCED:
            return 15  # Enhanced agents with advanced features
        else:  # PROFESSIONAL
            return 19  # All agents with professional features

    def _generate_cheap_video(self, script_data: Dict[str, Any], decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate video in cheap mode with granular level control"""
        logger.info(f"💰 Starting cheap mode video generation (level: {self.cheap_mode_level})")
        
        try:
            # Create a simple text-based video configuration
            from ..utils.session_context import create_session_context
            session_context = create_session_context(self.session_id)
            
            # Configure based on cheap mode level
            if self.cheap_mode_level == "full":
                # Full cheap mode: text video + gTTS audio
                logger.info("💰 FULL cheap mode: Text video + gTTS audio")
                use_real_veo2 = False
                fallback_only = True
                cheap_mode = True
                
            elif self.cheap_mode_level == "audio":
                # Audio cheap mode: normal video + gTTS audio
                logger.info("💰 AUDIO cheap mode: Normal video + gTTS audio")
                use_real_veo2 = True
                fallback_only = False
                cheap_mode = False  # Normal video generation
                
            elif self.cheap_mode_level == "video":
                # Video cheap mode: fallback video + normal audio
                logger.info("💰 VIDEO cheap mode: Fallback video + normal audio")
                use_real_veo2 = False
                fallback_only = True
                cheap_mode = False  # Normal audio
                
            else:
                # Default to full cheap mode
                logger.warning(f"⚠️ Unknown cheap mode level '{self.cheap_mode_level}', using 'full'")
                use_real_veo2 = False
                fallback_only = True
                cheap_mode = True
            
            # Generate the video with configured settings
            video_generator = VideoGenerator(
                api_key=self.api_key,
                use_real_veo2=use_real_veo2,
                use_vertex_ai=False   # Always disable Vertex AI in cheap modes
            )
            
            # Create config based on cheap mode level
            cheap_config = GeneratedVideoConfig(
                topic=self.mission,
                duration_seconds=self.duration,
                target_platform=self.platform,
                category=self.category,
                session_id=self.session_id,
                style=self.style,
                tone=self.tone,
                target_audience=self.target_audience,
                hook=self._extract_hook_from_script(script_data),
                main_content=self._extract_content_from_script(script_data),
                call_to_action=self._extract_cta_from_script(script_data),
                visual_style="minimal" if cheap_mode else self.visual_style,
                color_scheme=["#000000", "#FFFFFF"] if cheap_mode else None,
                text_overlays=[],
                transitions=["none"] if cheap_mode else None,
                background_music_style="none" if cheap_mode else None,
                voiceover_style="simple",
                sound_effects=[],
                inspired_by_videos=[],
                predicted_viral_score=0.5,
                frame_continuity=False,  # No frame continuity in cheap modes
                image_only_mode=False,
                use_real_veo2=use_real_veo2,
                fallback_only=fallback_only,
                cheap_mode=cheap_mode,  # Controls text video vs normal video
                cheap_mode_level=self.cheap_mode_level  # Pass granular level to video generator
            )
            
            logger.info(f"💰 Generating video with {self.cheap_mode_level} cheap mode")
            video_path = video_generator.generate_video(cheap_config)
            
            if video_path:
                logger.info(f"✅ Cheap mode video generated: {video_path}")
                return video_path
            else:
                logger.error("❌ Cheap mode video generation failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cheap mode video generation failed: {e}")
            return None

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress for real-time UI"""
        return {
            'progress': 100,  # Orchestrator completes when called
            'session_id': self.session_id,
            'current_phase': 'completed',
            'mode': self.mode.value,
            'results': self.agent_decisions,
            'discussions_completed': len(self.discussion_results),
            'agents_used': self._count_agents_used()
        }

def create_working_orchestrator(mission: str, platform: str, category: str,
                                duration: int, api_key: str,
                                style: str = "viral", tone: str = "engaging",
                                target_audience: str = "general audience",
                                visual_style: str = "dynamic",
                                mode: str = "enhanced"
                                ) -> WorkingOrchestrator:
    """
    Factory function to create working orchestrator with all features

    Args:
        mission: What you want to accomplish (mission-driven)
        platform: Target platform
        category: Video category
        duration: Duration in seconds
        api_key: Google AI API key
        style: Content style
        tone: Content tone
        target_audience: Target audience
        visual_style: Visual style
        mode: Orchestrator mode (
            simple,
            enhanced,
            advanced,
            multilingual,
            professional)

    Returns:
        Configured WorkingOrchestrator instance """
    try:
        platform_enum = Platform(platform.lower())
    except ValueError:
        platform_enum = Platform.INSTAGRAM
    
    try:
        # Try direct match first
        category_enum = VideoCategory(category)
    except ValueError:
        try:
            # Try uppercase for backwards compatibility
            category_enum = VideoCategory(category.upper())
        except ValueError:
            # Map common category names
            category_mapping = {
                'education': VideoCategory.EDUCATION,
                'educational': VideoCategory.EDUCATION,
                'comedy': VideoCategory.COMEDY,
                'entertainment': VideoCategory.ENTERTAINMENT,
                'news': VideoCategory.NEWS,
                'tech': VideoCategory.TECHNOLOGY,
                'technology': VideoCategory.TECHNOLOGY,
                'lifestyle': VideoCategory.LIFESTYLE,
                'sports': VideoCategory.SPORTS,
                'music': VideoCategory.MUSIC,
                'gaming': VideoCategory.GAMING,
                'food': VideoCategory.FOOD,
                'travel': VideoCategory.TRAVEL,
                'fitness': VideoCategory.FITNESS,
                'fashion': VideoCategory.FASHION,
                'science': VideoCategory.SCIENCE,
                'business': VideoCategory.BUSINESS,
                'health': VideoCategory.HEALTH,
                'arts': VideoCategory.ARTS,
                'automotive': VideoCategory.AUTOMOTIVE,
                'pets': VideoCategory.PETS
            }
            category_enum = category_mapping.get(category.lower(), VideoCategory.LIFESTYLE)

    try:
        mode_enum = OrchestratorMode(mode.lower())
    except ValueError:
        mode_enum = OrchestratorMode.ENHANCED
    
    return WorkingOrchestrator(
        api_key=api_key,
        mission=mission,
        platform=platform_enum,
        category=category_enum,
        duration=duration,
        style=style,
        tone=tone,
        target_audience=target_audience,
        visual_style=visual_style,
        mode=mode_enum
    )
