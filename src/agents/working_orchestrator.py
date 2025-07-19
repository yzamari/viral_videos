"""
Enhanced Working AI Agent Orchestrator
Comprehensive mission-driven system with ALL features and proper OOP design """

import os
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
    from .fact_checker_agent import InternetFactCheckerAgent
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
    from src.agents.fact_checker_agent import InternetFactCheckerAgent

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
                 cheap_mode_level: str = "full",
                 core_decisions = None):
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
        
        # CRITICAL: Store core decisions for system-wide use
        self.core_decisions = core_decisions
        if core_decisions:
            logger.info(f"✅ Core decisions received: {core_decisions.num_clips} clips, {core_decisions.clip_durations}")
        else:
            logger.warning("⚠️ No core decisions provided - using legacy parameters")
        
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
        self.fact_checker = InternetFactCheckerAgent(api_key, enable_web_search=True)

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
            try:
                script_data = self._generate_enhanced_script(config)
                logger.info("✅ Script generation completed successfully")
            except Exception as e:
                logger.error(f"❌ Script generation failed: {e}")
                logger.error(f"❌ Script generation error details: {type(e).__name__}: {str(e)}")
                
                # Create fallback script for cheap mode to continue generation
                if self.cheap_mode:
                    logger.info("💰 Creating fallback script for cheap mode")
                    script_data = self._create_fallback_script()
                else:
                    logger.error("❌ Script generation failed in non-cheap mode, aborting")
                    raise

            # Phase 5: Comprehensive AI Decision Making (with continuity context)
            try:
                decisions = self._make_comprehensive_decisions(
                    script_data,
                    config,
                    frame_continuity_decision)
                logger.info("✅ Decision making completed successfully")
            except Exception as e:
                logger.error(f"❌ Decision making failed: {e}")
                # Create fallback decisions for cheap mode
                if self.cheap_mode:
                    logger.info("💰 Creating fallback decisions for cheap mode")
                    decisions = self._create_fallback_decisions()
                else:
                    raise

            # Phase 6: Video Generation with All Features (continuity-aware)
            try:
                if self.cheap_mode:
                    video_path = self._generate_cheap_video(script_data, decisions, config)
                elif self.mode == OrchestratorMode.MULTILINGUAL and config.get('languages'):
                    video_path = self._generate_multilingual_video(script_data, decisions, config)
                else:
                    video_path = self._generate_enhanced_video(script_data, decisions, config)
                
                if video_path:
                    logger.info(f"✅ {self.mode.value} video generation completed: {video_path}")
                else:
                    logger.error(f"❌ {self.mode.value} video generation returned None")
                    return {
                        'success': False,
                        'error': 'Video generation returned None',
                        'session_id': self.session_id
                    }
            except Exception as e:
                logger.error(f"❌ Video generation failed: {e}")
                logger.error(f"❌ Video generation error details: {type(e).__name__}: {str(e)}")
                return {
                    'success': False,
                    'error': f'Video generation failed: {str(e)}',
                    'session_id': self.session_id
                }
            
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
            [AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR, AgentRole.FACT_CHECKER]
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
        
        # Discussion 4: Fact Checking & Content Verification
        fact_check_topic = DiscussionTopic(
            topic_id="fact_checking", 
            title="Content Fact Checking & Information Verification", 
            description="Verify factual accuracy and provide current information for content",
            context={
                'mission': self.mission,
                'category': self.category.value,
                'platform': self.platform.value,
                'content_claims': script_result.decision.get('content_claims', []) if hasattr(script_result, 'decision') else [],
                'trending_insights': self.trending_insights
            }, 
            required_decisions=["fact_verification", "source_credibility", "misinformation_prevention"]
        )

        fact_check_result = self.discussion_system.start_discussion(
            fact_check_topic,
            [AgentRole.FACT_CHECKER]
        )
        self.discussion_results['fact_checking'] = fact_check_result
        
        logger.info(f"✅ Completed {len(self.discussion_results)} enhanced discussions")

    def _conduct_advanced_discussions(self, config: Dict[str, Any]):
        """Advanced discussions for professional modes with 19+ agents"""
        logger.info("🎯 Starting professional mode discussions with 19+ agents")
        
        if not self.discussion_system:
            logger.warning("Discussion system not available, falling back to enhanced mode")
            self._conduct_enhanced_discussions(config)
            return
        
        # Professional discussions build on enhanced base
        self._conduct_enhanced_discussions(config)
        
        # Discussion 4: Marketing & Brand Strategy (4 agents)
        marketing_topic = DiscussionTopic(
            topic_id="marketing_strategy", 
            title="Marketing Strategy & Brand Alignment",
            description=f"Comprehensive marketing strategy for {self.platform.value} content optimization",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'target_audience': self.target_audience,
                'brand_requirements': config.get('brand_requirements', {}),
                'campaign_goals': config.get('campaign_goals', ['engagement', 'reach'])
            },
            required_decisions=["marketing_strategy", "brand_alignment", "audience_targeting"]
        )
        
        marketing_result = self.discussion_system.start_discussion(
            marketing_topic,
            [AgentRole.MARKETING_STRATEGIST, AgentRole.BRAND_SPECIALIST, AgentRole.SOCIAL_MEDIA_EXPERT, AgentRole.AUDIENCE_RESEARCHER]
        )
        self.discussion_results['marketing_strategy'] = marketing_result
        
        # Discussion 5: Visual Design & Typography (4 agents)
        design_topic = DiscussionTopic(
            topic_id="design_strategy",
            title="Visual Design & Typography Optimization", 
            description="Comprehensive visual design strategy for maximum impact",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'visual_style': self.visual_style,
                'duration': self.duration,
                'brand_colors': config.get('brand_colors', [])
            },
            required_decisions=["visual_design", "typography", "color_scheme", "motion_graphics"]
        )
        
        design_result = self.discussion_system.start_discussion(
            design_topic,
            [AgentRole.VISUAL_DESIGNER, AgentRole.TYPOGRAPHY_EXPERT, AgentRole.COLOR_SPECIALIST, AgentRole.MOTION_GRAPHICS]
        )
        self.discussion_results['design_strategy'] = design_result
        
        # Discussion 6: Engagement & Virality Strategy (4 agents)
        engagement_topic = DiscussionTopic(
            topic_id="engagement_strategy",
            title="Engagement Optimization & Virality Mechanics",
            description="Advanced engagement and viral potential optimization",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'target_metrics': config.get('target_metrics', {}),
                'viral_triggers': self.trending_insights.get('viral_triggers', [])
            },
            required_decisions=["engagement_hooks", "viral_elements", "cta_strategy", "shareability"]
        )
        
        engagement_result = self.discussion_system.start_discussion(
            engagement_topic,
            [AgentRole.ENGAGEMENT_OPTIMIZER, AgentRole.VIRAL_SPECIALIST, AgentRole.ANALYTICS_EXPERT, AgentRole.CONTENT_STRATEGIST, AgentRole.FACT_CHECKER]
        )
        self.discussion_results['engagement_strategy'] = engagement_result
        
        # Discussion 7: Platform Optimization & Copy Strategy (4 agents)
        platform_topic = DiscussionTopic(
            topic_id="platform_optimization",
            title="Platform-Specific Optimization & Copywriting",
            description="Platform algorithm optimization and persuasive copywriting",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'algorithm_factors': config.get('algorithm_factors', {}),
                'conversion_goals': config.get('conversion_goals', [])
            },
            required_decisions=["platform_optimization", "copy_strategy", "thumbnail_design", "algorithm_alignment"]
        )
        
        platform_result = self.discussion_system.start_discussion(
            platform_topic,
            [AgentRole.PLATFORM_OPTIMIZER, AgentRole.COPYWRITER, AgentRole.THUMBNAIL_DESIGNER, AgentRole.TREND_ANALYST]
        )
        self.discussion_results['platform_optimization'] = platform_result
        
        total_discussions = len(self.discussion_results)
        total_agents = sum(len(discussion.participating_agents) for discussion in self.discussion_results.values())
        
        logger.info(f"✅ Professional discussions completed: {total_discussions} discussions with {total_agents}+ agent interactions")
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
            [AgentRole.SCRIPT_WRITER, AgentRole.SOUNDMAN, AgentRole.FACT_CHECKER]
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
        
        # Add fact checking for enhanced modes
        if self.mode != OrchestratorMode.SIMPLE and not self.cheap_mode:
            logger.info("🔍 Performing fact checking on generated script...")
            try:
                # Fact check the script content
                script_content = str(script_data)
                fact_check_result = self.fact_checker.verify_facts_for_discussion(
                    content=script_content,
                    topic=self.mission,
                    platform=self.platform.value
                )
                
                # Store fact check results
                self.agent_decisions['fact_checking'] = {
                    'agent': 'InternetFactCheckerAgent',
                    'verification_summary': fact_check_result.get('verification_summary', {}),
                    'recommendations': fact_check_result.get('recommendations', {}),
                    'confidence_level': fact_check_result.get('confidence_level', 'medium')
                }
                
                # Log fact checking summary
                verification = fact_check_result.get('verification_summary', {})
                logger.info(f"✅ Fact checking completed: {verification.get('total_claims_checked', 0)} claims checked, "
                           f"accuracy: {verification.get('overall_accuracy', 0.5):.2f}")
                
            except Exception as e:
                logger.warning(f"⚠️ Fact checking failed: {e}")
        
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

        # CRITICAL: Use core decisions if available, otherwise fallback to local decisions
        if self.core_decisions:
            logger.info(f"🎯 Using core decisions: {self.core_decisions.num_clips} clips, {self.core_decisions.clip_durations}")
            duration_seconds = self.core_decisions.duration_seconds
            platform = self.core_decisions.platform
            category = self.core_decisions.category
            mission = self.core_decisions.mission
            style = self.core_decisions.style
            tone = self.core_decisions.tone
            target_audience = self.core_decisions.target_audience
            visual_style = self.core_decisions.visual_style
            frame_continuity = self.core_decisions.frame_continuity
            background_music_style = self.core_decisions.background_music_style
            # Extract core decisions for video generation
            num_clips = self.core_decisions.num_clips
            clip_durations = self.core_decisions.clip_durations
            # CRITICAL: Prioritize AI-generated hook and CTA over default values
            if hook == "Amazing content ahead!" and self.core_decisions.hook != "Amazing content ahead!":
                # Use AI-generated hook from script if core decisions has default
                pass  # Keep the extracted hook
            elif self.core_decisions.hook != "Amazing content ahead!":
                hook = self.core_decisions.hook
            
            if cta == "Subscribe for more!" and self.core_decisions.call_to_action != "Subscribe for more!":
                # Use AI-generated CTA from script if core decisions has default
                pass  # Keep the extracted CTA
            elif self.core_decisions.call_to_action != "Subscribe for more!":
                cta = self.core_decisions.call_to_action
        else:
            logger.warning("⚠️ No core decisions available, using legacy orchestrator parameters")
            # Apply AI decisions with safe defaults
            frame_continuity = decisions.get('continuity', {}).get('use_frame_continuity', False)
            voice_style = decisions.get('voice', {}).get('voice_style', 'energetic')
            visual_style = decisions.get('visual', {}).get('style', self.visual_style)
            duration_seconds = self.duration
            platform = self.platform
            category = self.category
            mission = self.mission
            style = self.style
            tone = self.tone
            target_audience = self.target_audience
            background_music_style = config.get('background_music_style', "upbeat")
            # Default clip settings
            num_clips = None
            clip_durations = None

        # Enhanced configuration with platform and category for AI timing
        enhanced_config = GeneratedVideoConfig(
            target_platform=platform,
            category=category,
            duration_seconds=duration_seconds,
            topic=mission,
            session_id=self.session_id,  # CRITICAL: Pass the session ID from orchestrator
            style=style,
            tone=tone,
            target_audience=target_audience,
            hook=hook,
            main_content=main_content,
            call_to_action=cta,
            visual_style=visual_style,
            color_scheme=config.get('color_scheme', ["#FF6B6B", "#4ECDC4", "#FFFFFF"]),
            text_overlays=config.get('text_overlays', []),
            transitions=config.get('transitions', ["fade", "slide"]),
            background_music_style=background_music_style,
            voiceover_style=decisions.get('voice', {}).get('voice_style', 'energetic'),
            sound_effects=config.get('sound_effects', []),
            inspired_by_videos=config.get('inspired_by_videos', []),
            predicted_viral_score=config.get('predicted_viral_score', 0.85),
            frame_continuity=frame_continuity,
            image_only_mode=config.get('force_generation') == 'force_image_gen',
            use_real_veo2=config.get('force_generation') != 'force_image_gen',
            video_orientation=config.get('orientation', 'auto'),
            ai_decide_orientation=config.get('ai_decide_orientation', True),
            # CRITICAL: Pass core decisions clip information
            num_clips=num_clips,
            clip_durations=clip_durations
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
            return 4  # Director, Continuity, Voice, Fact Checker
        elif self.mode == OrchestratorMode.ENHANCED:
            return 8  # Core agents with enhanced features + Fact Checker
        elif self.mode == OrchestratorMode.MULTILINGUAL:
            return 9  # Core agents + multilingual + Fact Checker
        elif self.mode == OrchestratorMode.ADVANCED:
            return 16  # Enhanced agents with advanced features + Fact Checker
        else:  # PROFESSIONAL
            return 23  # All agents with professional features + Fact Checker

    def _generate_cheap_video(self, script_data: Dict[str, Any], decisions: Dict[str, Any], config: Dict[str, Any]) -> Optional[str]:
        """Generate video in cheap mode with granular level control"""
        logger.info(f"💰 Starting cheap mode video generation (level: {self.cheap_mode_level})")
        
        try:
            # Create a simple text-based video configuration
            from ..utils.session_context import create_session_context
            session_context = create_session_context(self.session_id)
            
            # Save script data to session for cheap mode
            self._save_script_to_session(script_data, session_context)
            
            # Save decisions to session for cheap mode
            self._save_decisions_to_session(decisions, session_context)
            
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
                background_music_style="none" if cheap_mode else "upbeat",
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
            video_result = video_generator.generate_video(cheap_config)
            
            # Handle different return types
            if isinstance(video_result, str):
                video_path = video_result
            elif hasattr(video_result, 'file_path'):
                video_path = video_result.file_path
            else:
                video_path = str(video_result) if video_result else None
            
            if video_path:
                logger.info(f"✅ Cheap mode video generated: {video_path}")
                return video_path
            else:
                logger.error("❌ Cheap mode video generation failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cheap mode video generation failed: {e}")
            return None

    def _create_fallback_script(self) -> Dict[str, Any]:
        """Create a fallback script when Director fails"""
        logger.info("🔄 Creating fallback script for cheap mode")
        
        # Create a simple script based on the mission
        fallback_script = {
            'hook': f"Amazing content ahead!",
            'main_content': f"Here's what you need to know about {self.mission}.",
            'call_to_action': "Follow for more!",
            'segments': [
                {
                    'type': 'hook',
                    'text': f"Amazing content ahead!",
                    'duration': 3
                },
                {
                    'type': 'content',
                    'text': f"Here's what you need to know about {self.mission}.",
                    'duration': self.duration - 6
                },
                {
                    'type': 'cta',
                    'text': "Follow for more!",
                    'duration': 3
                }
            ],
            'total_duration': self.duration,
            'fallback': True
        }
        
        logger.info("✅ Fallback script created successfully")
        return fallback_script

    def _create_fallback_decisions(self) -> Dict[str, Any]:
        """Create fallback decisions when comprehensive decision making fails"""
        logger.info("🔄 Creating fallback decisions for cheap mode")
        
        fallback_decisions = {
            'voice_config': {
                'voice': 'en-US-Neural2-C',
                'personality': 'storyteller',
                'single_voice': True
            },
            'visual_style': {
                'style': 'minimal',
                'colors': ['#000000', '#FFFFFF'],
                'typography': 'simple'
            },
            'audio_config': {
                'tts_engine': 'gtts',
                'speed': 1.0,
                'pitch': 1.0
            },
            'composition': {
                'num_clips': 1,
                'transitions': ['none'],
                'overlays': []
            },
            'fallback': True
        }
        
        logger.info("✅ Fallback decisions created successfully")
        return fallback_decisions

    def _save_script_to_session(self, script_data: Dict[str, Any], session_context) -> None:
        """Save script data to session directories"""
        try:
            import json
            import os
            
            # Extract script text for saving
            script_text = ""
            if isinstance(script_data, dict):
                if 'processed' in script_data and 'final_script' in script_data['processed']:
                    script_text = script_data['processed']['final_script']
                elif 'segments' in script_data:
                    # PRIORITY: Use segments first to avoid contaminated full_text
                    # Use full_text if available (to avoid truncated text), otherwise use text
                    script_text = " ".join([segment.get('full_text', segment.get('text', '')) for segment in script_data['segments']])
                elif 'full_text' in script_data:
                    # Use the complete full_text if available (avoids truncated segments)
                    script_text = script_data['full_text']
                elif 'main_content' in script_data:
                    script_text = f"{script_data.get('hook', '')} {script_data['main_content']} {script_data.get('call_to_action', '')}"
                else:
                    script_text = str(script_data)
            else:
                script_text = str(script_data)
            
            # Save processed script
            scripts_dir = os.path.join(session_context.session_dir, 'scripts')
            os.makedirs(scripts_dir, exist_ok=True)
            
            with open(os.path.join(scripts_dir, 'processed_script.txt'), 'w') as f:
                f.write(script_text)
            
            # Save full script data as JSON
            with open(os.path.join(scripts_dir, 'script_data.json'), 'w') as f:
                json.dump(script_data, f, indent=2, default=str)
            
            logger.info("✅ Script saved to session successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save script to session: {e}")

    def _save_decisions_to_session(self, decisions: Dict[str, Any], session_context) -> None:
        """Save decisions to session directories"""
        try:
            import json
            import os
            
            # Save AI agent decisions
            decisions_dir = os.path.join(session_context.session_dir, 'decisions')
            os.makedirs(decisions_dir, exist_ok=True)
            
            # Save agent decisions
            with open(os.path.join(decisions_dir, 'agent_decisions.json'), 'w') as f:
                json.dump(self.agent_decisions, f, indent=2, default=str)
            
            # Save comprehensive decisions
            with open(os.path.join(decisions_dir, 'comprehensive_decisions.json'), 'w') as f:
                json.dump(decisions, f, indent=2, default=str)
            
            # Create placeholder discussions for cheap mode
            discussions_dir = os.path.join(session_context.session_dir, 'discussions')
            os.makedirs(discussions_dir, exist_ok=True)
            
            cheap_mode_discussion = {
                "mode": "cheap_mode",
                "discussions_skipped": True,
                "reason": "Cheap mode enabled - skipped AI agent discussions for cost efficiency",
                "fallback_used": decisions.get('fallback', False)
            }
            
            with open(os.path.join(discussions_dir, 'cheap_mode_summary.json'), 'w') as f:
                json.dump(cheap_mode_discussion, f, indent=2)
            
            # Create basic hashtags for cheap mode
            hashtags_dir = os.path.join(session_context.session_dir, 'hashtags')
            os.makedirs(hashtags_dir, exist_ok=True)
            
            basic_hashtags = f"#viral #content #{self.platform.value.lower()} #trending #amazing"
            
            with open(os.path.join(hashtags_dir, 'hashtags_text.txt'), 'w') as f:
                f.write(basic_hashtags)
            
            logger.info("✅ Decisions and metadata saved to session successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save decisions to session: {e}")

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
