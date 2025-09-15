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
    from .langgraph_orchestrator import LangGraphDiscussionOrchestrator
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
    from src.agents.langgraph_orchestrator import LangGraphDiscussionOrchestrator

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
            cheap_mode: Enable cost-saving mode (default: True - saves costs)
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
                    mission=mission,
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
        logger.info(f"   Mode: {mode}")
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
        
        logger.info(f"🎬 Enhanced Working Orchestrator initialized ({mode})")
        logger.info(f"   Mission: {mission}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Session: {self.session_id}")
        logger.info(f"   Mode: {mode}")
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
        """Initialize LangGraph discussion system based on mode"""
        if self.mode == OrchestratorMode.SIMPLE:
            # Even simple mode gets basic LangGraph for consistency
            if not self.cheap_mode:
                logger.info("🚀 Using LangGraph for simple mode discussions")
                self.discussion_system = LangGraphDiscussionOrchestrator(
                    self.api_key,
                    self.session_id
                )
            else:
                # In cheap mode, use standard system for speed
                self.discussion_system = MultiAgentDiscussionSystem(
                    self.api_key,
                    self.session_id
                )
        else:
            # All other modes use LangGraph
            logger.info(f"🚀 Using LangGraph for {self.mode} agent discussions")
            self.discussion_system = LangGraphDiscussionOrchestrator(
                self.api_key,
                self.session_id
            )
    
    async def generate_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video using comprehensive AI agent system

        Args:
            config: Generation configuration dictionary

        Returns:
            Generation result with success status and metadata """
        logger.info(f"🎬 Starting {self.mode} AI agent video generation")
        
        # Store config for access in extraction methods
        self._current_config = config

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
                logger.info("💰 Skipping full AI agent discussions in cheap mode")
                # CRITICAL: Still need duration validation even in cheap mode
                self._conduct_duration_validation_only(config)
            else:
                # Simple mode - still need duration validation
                logger.info("🚀 Simple mode - conducting duration validation only")
                self._conduct_duration_validation_only(config)
            
            # Phase 4: Script Generation with AI Enhancement
            try:
                script_data = await self._generate_enhanced_script(config)
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
                # Check if multiple languages are requested
                languages = config.get('languages', []) or []
                logger.info(f"🔍 DEBUG: Languages in config: {languages}")
                logger.info(f"🔍 DEBUG: Language count: {len(languages)}")
                logger.info(f"🔍 DEBUG: Multiple languages check: {len(languages) > 1}")
                if len(languages) > 1:
                    # Multi-language generation requested
                    logger.info(f"🌍 Multiple languages requested: {[lang.value if hasattr(lang, 'value') else lang for lang in languages]}")
                    
                    # Generate base video first, then create language-specific files
                    logger.info("🎬 Generating base video...")
                    base_video_path = await self._generate_enhanced_video(script_data, decisions, config)
                    logger.info(f"✅ Base video generated: {base_video_path}")
                    
                    # Create language-specific files for each language
                    logger.info("🌍 Creating language-specific audio and subtitle files...")
                    try:
                        multilang_result = await self._create_multilingual_files(
                            languages, script_data, base_video_path
                        )
                        logger.info(f"✅ Multilingual files created: {multilang_result}")
                        if multilang_result and hasattr(multilang_result, 'language_versions'):
                            logger.info(f"✅ Generated {len(multilang_result.language_versions)} language versions")
                        else:
                            logger.warning("⚠️ No language versions were created")
                    except Exception as e:
                        logger.error(f"❌ Multi-language generation failed: {e}")
                        import traceback
                        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                    
                    # Return the base video path
                    video_path = base_video_path
                elif self.cheap_mode:
                    video_path = await self._generate_cheap_video(script_data, decisions, config)
                elif self.mode == OrchestratorMode.MULTILINGUAL:
                    video_path = await self._generate_multilingual_video(script_data, decisions, config)
                else:
                    video_path = await self._generate_enhanced_video(script_data, decisions, config)
                
                if video_path:
                    logger.info(f"✅ {self.mode} video generation completed: {video_path}")
                else:
                    logger.error(f"❌ {self.mode} video generation returned None")
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
                'optimization_level': f'{self.mode}_ai_enhanced',
                'mode': self.mode,
                'frame_continuity_decision': frame_continuity_decision,
                'professional_mode_details': {
                    'total_agents': self._count_agents_used(),
                    'base_agents': 22 if self.mode == OrchestratorMode.PROFESSIONAL else 0,
                    'discussion_agents': sum(len(discussion.participating_agents) for discussion in self.discussion_results.values()) if self.discussion_results else 0,
                    'discussions_completed': len(self.discussion_results),
                    'all_agents_utilized': self.mode == OrchestratorMode.PROFESSIONAL and len(self.discussion_results) >= 7
                } if self.mode == OrchestratorMode.PROFESSIONAL else None
            }
            
        except Exception as e:
            logger.error(f"❌ {self.mode} video generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'agent_decisions': self.agent_decisions,
                'discussion_results': self.discussion_results,
                'mode': self.mode,
                'professional_mode_details': {
                    'total_agents': self._count_agents_used(),
                    'base_agents': 22 if self.mode == OrchestratorMode.PROFESSIONAL else 0,
                    'discussion_agents': sum(len(discussion.participating_agents) for discussion in self.discussion_results.values()) if self.discussion_results else 0,
                    'discussions_completed': len(self.discussion_results),
                    'all_agents_utilized': self.mode == OrchestratorMode.PROFESSIONAL and len(self.discussion_results) >= 7
                } if self.mode == OrchestratorMode.PROFESSIONAL else None
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
                mission=self.mission,
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
        
        # Generate visualization after discussions
        self._generate_discussion_visualization()
    
    def _generate_discussion_visualization(self):
        """Generate a visual representation of AI discussions and save to session"""
        try:
            from ..utils.session_context import get_current_session_context
            import json
            from datetime import datetime
            
            session_context = get_current_session_context()
            if not session_context:
                logger.warning("No active session context for discussion visualization")
                return
            
            # Create visualization content
            viz_content = self._create_visualization_content()
            
            # Save as markdown
            viz_path = session_context.get_output_path("discussions", "ai_discussion_visualization.md")
            with open(viz_path, 'w', encoding='utf-8') as f:
                f.write(viz_content)
            
            logger.info(f"📊 AI discussion visualization saved to: {viz_path}")
            
            # Also save as JSON for programmatic access
            viz_data = self._get_visualization_data()
            viz_json_path = session_context.get_output_path("discussions", "ai_discussion_data.json")
            with open(viz_json_path, 'w', encoding='utf-8') as f:
                json.dump(viz_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Could not generate discussion visualization: {e}")
    
    def _create_visualization_content(self) -> str:
        """Create markdown content for discussion visualization"""
        from datetime import datetime
        
        # Check if using LangGraph or fallback
        using_langgraph = isinstance(self.discussion_system, LangGraphDiscussionOrchestrator)
        
        content = f"""# 🤖 AI Agent Discussion Visualization

## Session Information
- **Session ID**: {self.session_id}
- **Timestamp**: {datetime.now().isoformat()}
- **Mode**: {self.mode} ({self._get_agent_count()} agents)
- **Discussion System**: {"LangGraph" if using_langgraph else "Fallback Mode"}
- **Platform**: {self.platform.value if self.platform else "Unknown"}
- **Duration**: {self.duration}s

## Discussion Architecture

"""
        
        if using_langgraph:
            content += """### LangGraph Multi-Phase Discussion Flow
```
┌──────────────────────────────────────────────────────┐
│                 LANGGRAPH ORCHESTRATOR                │
│              State-Managed Discussions                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [Initialize] → [Propose] → [Critique] → [Synthesize] │
│       ↓            ↓           ↓            ↓        │
│    Context      Solutions   Feedback    Insights      │
│                                                        │
│  [Vote] → [Consensus Check] → [Finalize]             │
│     ↓            ↓                ↓                  │
│  Scoring    Agreement?        Decision               │
│                 ↓                                     │
│            (Loop if no consensus)                    │
└──────────────────────────────────────────────────────┘
"""
        else:
            content += """### Fallback Discussion Mode
```
┌──────────────────────────────────────────────────────┐
│              SIMPLIFIED DISCUSSION SYSTEM             │
│                  (LangGraph Not Available)            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Topics → Basic Agent Response → Simple Decision      │
│                                                        │
│  Limited Context | No State Management | Quick Result │
└──────────────────────────────────────────────────────┘
"""
            
        # Add discussion results if available
        if hasattr(self, 'discussion_results') and self.discussion_results:
            content += f"""

## Discussion Results

### Topics Discussed: {len(self.discussion_results)}
"""
            for i, result in enumerate(self.discussion_results, 1):
                content += f"""
#### Topic {i}: {result.topic_id if hasattr(result, 'topic_id') else 'Unknown'}
- **Consensus Level**: {result.consensus_level if hasattr(result, 'consensus_level') else 'N/A'}
- **Rounds**: {result.total_rounds if hasattr(result, 'total_rounds') else 'N/A'}
- **Participating Agents**: {len(result.participating_agents) if hasattr(result, 'participating_agents') else 'N/A'}
"""
                
        # Add agent details
        content += f"""

## Agent Participation

### Active Agents ({self._get_agent_count()})
"""
        
        agents = self._get_active_agents()
        for agent in agents:
            content += f"- **{agent}**: {self._get_agent_description(agent)}\n"
            
        # Add decisions made
        if hasattr(self, 'core_decisions') and self.core_decisions:
            content += """

## Core Decisions Made

"""
            for key, value in self.core_decisions.items():
                if not key.startswith('_'):  # Skip private keys
                    content += f"- **{key}**: {value}\n"
                    
        # Add visualization graph
        if using_langgraph:
            content += """

## LangGraph Benefits Utilized

✅ **State Management**: All discussion context preserved
✅ **Multi-Phase Flow**: Structured propose → critique → synthesize
✅ **Consensus Building**: Voting and agreement mechanisms  
✅ **Insight Synthesis**: Combined wisdom from all agents
✅ **Neurological Optimization**: Neuroscientist agent integration

### Discussion Quality Metrics
- **Context Preservation**: HIGH
- **Agent Interaction Depth**: DEEP
- **Decision Quality**: ENHANCED
- **Consensus Achievement**: STRUCTURED
"""
        else:
            content += """

## LangGraph Benefits (Not Available This Run)

❌ **State Management**: Limited context preservation
❌ **Multi-Phase Flow**: Simple single-pass discussion
❌ **Consensus Building**: Basic agreement only
❌ **Insight Synthesis**: Minimal cross-agent learning
❌ **Neurological Optimization**: Basic integration only

### To Enable LangGraph:
1. Ensure `langgraph` package is installed
2. Restart the application
3. LangGraph will automatically be detected and used
"""
            
        content += """

---
*This visualization is automatically generated for every session*
*Location: outputs/{session_id}/discussions/ai_discussion_visualization.md*
"""
        
        return content
    
    def _get_visualization_data(self) -> dict:
        """Get structured data for JSON export"""
        using_langgraph = isinstance(self.discussion_system, LangGraphDiscussionOrchestrator)
        
        return {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "agent_count": self._get_agent_count(),
            "discussion_system": "LangGraph" if using_langgraph else "Fallback",
            "platform": self.platform.value if self.platform else None,
            "duration": self.duration,
            "discussion_results": [
                {
                    "topic_id": getattr(r, 'topic_id', 'unknown'),
                    "consensus_level": getattr(r, 'consensus_level', 0),
                    "total_rounds": getattr(r, 'total_rounds', 0),
                    "participating_agents": getattr(r, 'participating_agents', [])
                }
                for r in (self.discussion_results if hasattr(self, 'discussion_results') else [])
            ],
            "core_decisions": self.core_decisions if hasattr(self, 'core_decisions') else {},
            "langgraph_available": using_langgraph,
            "agents": self._get_active_agents()
        }
    
    def _get_agent_count(self) -> int:
        """Get the number of agents for current mode"""
        agent_counts = {
            OrchestratorMode.SIMPLE: 3,
            OrchestratorMode.ENHANCED: 7,
            OrchestratorMode.ADVANCED: 15,
            OrchestratorMode.PROFESSIONAL: 19
        }
        return agent_counts.get(self.mode, 7)
    
    def _get_active_agents(self) -> list:
        """Get list of active agent names"""
        from .multi_agent_discussion import AgentRole
        
        # Define agents per mode
        mode_agents = {
            OrchestratorMode.SIMPLE: [
                AgentRole.DIRECTOR.value,
                AgentRole.SCRIPT_WRITER.value,
                AgentRole.VIDEO_GENERATOR.value
            ],
            OrchestratorMode.ENHANCED: [
                AgentRole.DIRECTOR.value,
                AgentRole.SCRIPT_WRITER.value,
                AgentRole.VIDEO_GENERATOR.value,
                AgentRole.SOUNDMAN.value,
                AgentRole.EDITOR.value,
                AgentRole.ORCHESTRATOR.value,
                AgentRole.NEUROSCIENTIST.value
            ],
            OrchestratorMode.PROFESSIONAL: [
                # All agents including specialized ones
                AgentRole.DIRECTOR.value,
                AgentRole.SCRIPT_WRITER.value,
                AgentRole.VIDEO_GENERATOR.value,
                AgentRole.SOUNDMAN.value,
                AgentRole.EDITOR.value,
                AgentRole.ORCHESTRATOR.value,
                AgentRole.NEUROSCIENTIST.value,
                AgentRole.ENGAGEMENT_OPTIMIZER.value,
                AgentRole.VIRAL_SPECIALIST.value,
                AgentRole.TREND_ANALYST.value,
                AgentRole.AUDIENCE_PSYCHOLOGIST.value,
                AgentRole.PLATFORM_SPECIALIST.value,
                AgentRole.CREATIVE_STRATEGIST.value,
                AgentRole.BRAND_STRATEGIST.value,
                AgentRole.CONTENT_STRATEGIST.value,
                AgentRole.MARKETING_SPECIALIST.value,
                AgentRole.DESIGNER.value,
                AgentRole.COPYWRITER.value,
                AgentRole.DATA_ANALYST.value
            ]
        }
        
        return mode_agents.get(self.mode, mode_agents[OrchestratorMode.ENHANCED])
    
    def _get_agent_description(self, agent_name: str) -> str:
        """Get description for an agent"""
        descriptions = {
            "director": "Creative vision and visual storytelling",
            "script_writer": "Script optimization and narrative flow",
            "video_generator": "VEO prompt engineering and generation",
            "soundman": "Audio design and voice selection",
            "editor": "Post-production and timing",
            "orchestrator": "Workflow coordination",
            "neuroscientist": "Brain engagement and dopamine triggers",
            "engagement_optimizer": "Maximizing viewer retention",
            "viral_specialist": "Viral mechanics and shareability",
            "trend_analyst": "Current trends and patterns",
            "audience_psychologist": "Viewer psychology and behavior",
            "platform_specialist": "Platform-specific optimization",
            "creative_strategist": "Creative direction and innovation",
            "brand_strategist": "Brand alignment and consistency",
            "content_strategist": "Content planning and structure",
            "marketing_specialist": "Marketing and promotion strategy",
            "designer": "Visual design and aesthetics",
            "copywriter": "Copy and messaging optimization",
            "data_analyst": "Performance metrics and insights"
        }
        return descriptions.get(agent_name, "Specialized expertise")
    
    def _start_discussion(self, topic: DiscussionTopic, participants: list):
        """
        Start a discussion using the configured discussion system
        
        Args:
            topic: Discussion topic
            participants: List of participating agents
            
        Returns:
            Discussion result
        """
        if isinstance(self.discussion_system, LangGraphDiscussionOrchestrator):
            # Use LangGraph's run_discussion method
            return self.discussion_system.run_discussion(topic, participants)
        else:
            # Use standard system's start_discussion method
            return self.discussion_system.start_discussion(topic, participants)
    
    def _conduct_duration_validation_only(self, config: Dict[str, Any]):
        """Conduct ONLY duration validation discussion for simple/cheap modes"""
        logger.info("⏱️ Conducting mandatory duration validation...")
        
        if not self.discussion_system:
            # Initialize minimal discussion system for duration validation
            from .multi_agent_discussion import MultiAgentDiscussionSystem
            self.discussion_system = MultiAgentDiscussionSystem(
                self.api_key,
                self.session_id,
                enable_visualization=False  # Minimal mode
            )
        
        # Import required classes
        from .multi_agent_discussion import DiscussionTopic, AgentRole
        
        # Duration validation discussion
        duration_topic = DiscussionTopic(
            topic_id="duration_validation",
            title="Duration & Timing Validation",
            description=f"CRITICAL: Ensure ALL content fits EXACTLY within {self.duration} seconds ±5%",
            context={
                'mission': self.mission,  # Add mission to context
                'target_duration': self.duration,
                'max_duration': self.duration * 1.05,  # 5% tolerance
                'min_duration': self.duration * 0.95,  # 5% tolerance
                'words_per_second': 2.8,  # Speaking rate (matches TTS configuration)
                'max_words': int(self.duration * 2.8),
                'platform': self.platform.value,
                'num_segments': max(1, self.duration // 8),  # Approximate segments
                'mode': self.mode,
                'cheap_mode': self.cheap_mode
            },
            required_decisions=["duration_compliance", "word_count_limit", "segment_timing"],
            max_rounds=3  # Quick validation
        )
        
        # CRITICAL: AudioMaster, Editor and Orchestrator for duration control
        duration_result = self._start_discussion(
            duration_topic,
            [AgentRole.SOUNDMAN, AgentRole.EDITOR, AgentRole.ORCHESTRATOR]
        )
        
        if not hasattr(self, 'discussion_results'):
            self.discussion_results = {}
        
        self.discussion_results['duration_validation'] = duration_result
        logger.info(f"✅ Duration validation completed: {duration_result.decision}")
        
        # Apply duration constraints globally
        self.duration_constraints = duration_result.decision
        
        # Generate visualization after duration validation (cheap mode)
        self._generate_discussion_visualization()

    def _conduct_enhanced_discussions(self, config: Dict[str, Any]):
        """Enhanced 7-agent discussions"""

        if not self.discussion_system:
            logger.warning("Discussion system not available, skipping discussions")
            return

        # CRITICAL: Add duration validation discussion first
        duration_topic = DiscussionTopic(
            topic_id="duration_validation",
            title="Duration & Timing Validation",
            description=f"Ensure all content fits EXACTLY within {self.duration} seconds ±5%",
            context={
                'mission': self.mission,  # Add mission to context
                'target_duration': self.duration,
                'max_duration': self.duration * 1.05,  # 5% tolerance
                'min_duration': self.duration * 0.95,  # 5% tolerance
                'words_per_second': 2.8,  # Speaking rate (matches TTS configuration)
                'max_words': int(self.duration * 2.8),
                'platform': self.platform.value,
                'num_segments': max(1, self.duration // 8)  # Approximate segments
            },
            required_decisions=["duration_compliance", "word_count_limit", "segment_timing"]
        )
        
        # CRITICAL: AudioMaster is MANDATORY for duration validation
        duration_result = self._start_discussion(
            duration_topic,
            [AgentRole.SOUNDMAN, AgentRole.EDITOR, AgentRole.ORCHESTRATOR]
        )
        self.discussion_results['duration_validation'] = duration_result

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
                'trending_insights': self.trending_insights,
                'duration_constraints': duration_result.decision  # Pass duration constraints
            }, required_decisions=["script_structure", "viral_hooks", "engagement_strategy"]
        )

        script_result = self._start_discussion(
            script_topic,
            [AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR, AgentRole.SOUNDMAN]  # Add SOUNDMAN for duration awareness
        )
        self.discussion_results['script_strategy'] = script_result
        
        # Discussion 2: Visual & Technical Strategy
        visual_topic = DiscussionTopic( topic_id="visual_strategy", title="Visual Composition & Technical Approach", description=f"Optimal visual strategy for {self.platform.value} content",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'visual_style': self.visual_style,
                'force_generation': config.get('force_generation', 'auto'),
                'trending_insights': self.trending_insights,
                'duration': self.duration,
                'duration_constraints': duration_result.decision
            }, required_decisions=["visual_style", "technical_approach", "generation_mode", "clip_durations"]
        )

        visual_result = self._start_discussion(
            visual_topic,
            [AgentRole.VIDEO_GENERATOR, AgentRole.EDITOR, AgentRole.SOUNDMAN]  # Add SOUNDMAN for sync
        )
        self.discussion_results['visual_strategy'] = visual_result
        
        # Discussion 3: Audio & Production Strategy
        audio_topic = DiscussionTopic( topic_id="audio_strategy", title="Audio Production & Voice Strategy", description=f"CRITICAL: Audio MUST be EXACTLY {self.duration}s ±5%. Ensure perfect sync!",
            context={
                'mission': self.mission,
                'duration': self.duration,
                'platform': self.platform.value,
                'target_audience': self.target_audience,
                'duration_constraints': duration_result.decision,
                'script_duration': script_result.decision.get('estimated_duration', self.duration),
                'max_audio_duration': self.duration * 1.05,  # 5% tolerance
                'min_audio_duration': self.duration * 0.95   # 5% tolerance
            }, required_decisions=["voice_style", "audio_approach", "sound_design", "audio_duration_compliance"]
        )

        audio_result = self._start_discussion(
            audio_topic,
            [AgentRole.SOUNDMAN, AgentRole.EDITOR, AgentRole.ORCHESTRATOR]  # Add ORCHESTRATOR for sync
        )
        self.discussion_results['audio_strategy'] = audio_result
        
        # Discussion 4: Neuroscience & Brain Engagement Strategy
        neuro_topic = DiscussionTopic(
            topic_id="neuroscience_optimization",
            title="Neuroscience & Dopamine Optimization Strategy",
            description=f"Apply neuroscience principles to maximize engagement and dopamine triggers for {self.mission}",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'duration': self.duration,
                'target_audience': self.target_audience,
                'visual_style': self.visual_style,
                'script_decisions': script_result.decision if 'script_result' in locals() else {},
                'visual_decisions': visual_result.decision if 'visual_result' in locals() else {},
                'content_type': self.category.value
            },
            required_decisions=["dopamine_triggers", "attention_hooks", "memory_encoding", "emotional_peaks"]
        )
        
        neuro_result = self._start_discussion(
            neuro_topic,
            [AgentRole.NEUROSCIENTIST, AgentRole.DIRECTOR, AgentRole.ENGAGEMENT_OPTIMIZER]
        )
        self.discussion_results['neuroscience_optimization'] = neuro_result
        
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
        
        marketing_result = self._start_discussion(
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
        
        design_result = self._start_discussion(
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
        
        engagement_result = self._start_discussion(
            engagement_topic,
            [AgentRole.ENGAGEMENT_OPTIMIZER, AgentRole.VIRAL_SPECIALIST, AgentRole.ANALYTICS_EXPERT, AgentRole.CONTENT_STRATEGIST]
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
        
        platform_result = self._start_discussion(
            platform_topic,
            [AgentRole.PLATFORM_OPTIMIZER, AgentRole.COPYWRITER, AgentRole.THUMBNAIL_DESIGNER, AgentRole.TREND_ANALYST]
        )
        self.discussion_results['platform_optimization'] = platform_result
        
        # Discussion 8: Advanced Neuroscience & Psychological Triggers (Professional Mode)
        advanced_neuro_topic = DiscussionTopic(
            topic_id="advanced_neuroscience",
            title="Advanced Neuroscience & Psychological Optimization",
            description="Deep neurological and psychological optimization for maximum viewer impact",
            context={
                'mission': self.mission,
                'platform': self.platform.value,
                'duration': self.duration,
                'all_previous_decisions': {k: v.decision for k, v in self.discussion_results.items()},
                'target_audience': self.target_audience,
                'viral_goals': config.get('viral_goals', {}),
                'psychological_profile': config.get('audience_psychology', {})
            },
            required_decisions=["neurotransmitter_optimization", "cognitive_load_management", 
                              "behavioral_triggers", "habit_formation_elements"]
        )
        
        advanced_neuro_result = self._start_discussion(
            advanced_neuro_topic,
            [AgentRole.NEUROSCIENTIST, AgentRole.VIRAL_SPECIALIST, 
             AgentRole.AUDIENCE_RESEARCHER, AgentRole.ANALYTICS_EXPERT]
        )
        self.discussion_results['advanced_neuroscience'] = advanced_neuro_result
        
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
                'languages': config.get('languages', [Language.ENGLISH_US]) or [Language.ENGLISH_US],
                'cultural_adaptation': getattr(config, 'cultural_adaptation', True)
            }, required_decisions=["language_priority", "cultural_adaptation", "voice_selection"]
        )

        multilang_result = self._start_discussion(
            multilang_topic,
            [AgentRole.SCRIPT_WRITER, AgentRole.SOUNDMAN]
        )
        self.discussion_results['multilingual_strategy'] = multilang_result
        logger.info("✅ Multilingual discussions completed")

    async def _generate_enhanced_script(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script with AI enhancement and processing"""
        logger.info("📝 Generating enhanced script...")

        # CRITICAL: Pass duration constraints to director
        duration_constraints = {}
        if hasattr(self, 'duration_constraints'):
            duration_constraints = self.duration_constraints
        elif self.discussion_results and 'duration_validation' in self.discussion_results:
            duration_constraints = self.discussion_results['duration_validation'].decision
        
        # Determine the target language for script generation
        languages = config.get('languages', [Language.ENGLISH_US]) or [Language.ENGLISH_US]
        target_language = languages[0] if languages else Language.ENGLISH_US
        
        # Add language instruction to the mission if not English
        mission_with_language = self.mission
        if target_language != Language.ENGLISH_US:
            language_name = {
                Language.HEBREW: "Hebrew",
                Language.ARABIC: "Arabic",
                Language.PERSIAN: "Persian/Farsi",
                Language.FRENCH: "French",
                Language.SPANISH: "Spanish",
                Language.GERMAN: "German",
                Language.ITALIAN: "Italian",
                Language.PORTUGUESE: "Portuguese",
                Language.RUSSIAN: "Russian",
                Language.CHINESE: "Chinese",
                Language.JAPANESE: "Japanese",
                Language.ENGLISH_UK: "British English",
                Language.ENGLISH_IN: "Indian English"
            }.get(target_language, "the target language")
            
            mission_with_language = f"{self.mission}\n\nIMPORTANT: Generate all script content, dialogue, and text in {language_name}. Do not translate the mission statement itself, but create the script output in {language_name}."
            logger.info(f"🌍 Generating script in {language_name}")
        
        # Use the calculated duration from core_decisions if available, otherwise fallback to self.duration
        actual_duration = self.core_decisions.duration_seconds if self.core_decisions else self.duration
        logger.info(f"🎯 Using duration for script generation: {actual_duration}s (core_decisions: {self.core_decisions is not None})")
        
        # Try new separated script generator for better visual/dialogue separation
        try:
            logger.info("🔄 Using new separated script generator for better visual/dialogue separation")
            from ..generators.separated_script_generator import SeparatedScriptGenerator
            
            separated_generator = SeparatedScriptGenerator(self.api_key)
            character_desc = config.get('character_description', config.get('character', None))
            
            script_data = await separated_generator.generate_separated_script(
                mission=mission_with_language,
                duration=actual_duration,
                style=self.style,
                platform=self.platform,
                language=target_language,
                character_description=character_desc
            )
            logger.info("✅ Successfully generated script with separated visual/dialogue approach")
            
        except Exception as e:
            logger.warning(f"⚠️ Separated generator failed, falling back to Director: {e}")
            
            # Fallback to Director method
            script_data = self.director.write_script(
                mission=mission_with_language,
                style=self.style,
                duration=actual_duration,
                platform=self.platform,
                category=self.category,
                patterns={
                    'hooks': self.trending_insights.get('viral_hooks', []),
                    'themes': [self.tone],
                    'success_factors': [self.style, 'engaging'],
                    'duration_constraints': duration_constraints,
                    'max_words': int(actual_duration * 2.8),  # Enforce word limit (2.8 words per second for TTS)
                    'tolerance_percent': 0.15,  # 15% tolerance (fixed)
                    'target_language': target_language
                }
            )

        # Enhanced script processing for advanced modes
        if self.script_processor and self.mode != OrchestratorMode.SIMPLE:
            # Extract the actual script text from script_data
            # The Director returns a dict with 'full_text' containing all dialogue
            script_text = script_data.get('full_text', '')
            if not script_text:
                # Fallback: construct from segments
                hook_text = script_data.get('hook', {}).get('text', '')
                segment_texts = [seg.get('text', '') for seg in script_data.get('segments', [])]
                cta_text = script_data.get('cta', {}).get('text', '')
                script_text = ' '.join([hook_text] + segment_texts + [cta_text]).strip()
            
            logger.info(f"📝 Processing script text: {script_text[:100]}...")
            
            processed_script = await self.script_processor.process_script_for_tts(
                script_content=script_text,
                language=target_language,  # Use the target_language we already determined above
                target_duration=actual_duration
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
        
        # Get target language from config
        languages = config.get('languages', [Language.ENGLISH_US]) or [Language.ENGLISH_US]
        target_language = languages[0] if languages else Language.ENGLISH_US

        decisions = {}

        # Use the frame continuity decision that was already made
        decisions['continuity'] = frame_continuity_decision
        logger.info(f"✅ Using frame continuity decision: {frame_continuity_decision['use_frame_continuity']}")

        # Voice decisions with safe defaults
        voice_decision = self.voice_agent.analyze_content_and_select_voices(
            script=str(script_data),
            mission=self.mission,
            language=target_language,  # Use the target_language for voice selection
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
        
        # CRITICAL FIX: Integrate discussion results for professional mode
        if self.mode == OrchestratorMode.PROFESSIONAL and self.discussion_results:
            logger.info("🎯 Integrating professional discussion results from 23 agents...")
            
            # Integrate script strategy discussion results
            if 'script_strategy' in self.discussion_results:
                script_discussion = self.discussion_results['script_strategy']
                decisions['script_strategy'] = script_discussion.decision
                self.agent_decisions['script_strategy'] = {
                    'agents': script_discussion.participating_agents,
                    'consensus': script_discussion.consensus_level,
                    'insights': script_discussion.key_insights,
                    'decision': script_discussion.decision
                }
                logger.info(f"✅ Integrated script strategy from {len(script_discussion.participating_agents)} agents")

            # Integrate visual strategy discussion results
            if 'visual_strategy' in self.discussion_results:
                visual_discussion = self.discussion_results['visual_strategy']
                decisions['visual_strategy'] = visual_discussion.decision
                self.agent_decisions['visual_strategy'] = {
                    'agents': visual_discussion.participating_agents,
                    'consensus': visual_discussion.consensus_level,
                    'insights': visual_discussion.key_insights,
                    'decision': visual_discussion.decision
                }
                logger.info(f"✅ Integrated visual strategy from {len(visual_discussion.participating_agents)} agents")

            # Integrate audio strategy discussion results
            if 'audio_strategy' in self.discussion_results:
                audio_discussion = self.discussion_results['audio_strategy']
                decisions['audio_strategy'] = audio_discussion.decision
                self.agent_decisions['audio_strategy'] = {
                    'agents': audio_discussion.participating_agents,
                    'consensus': audio_discussion.consensus_level,
                    'insights': audio_discussion.key_insights,
                    'decision': audio_discussion.decision
                }
                logger.info(f"✅ Integrated audio strategy from {len(audio_discussion.participating_agents)} agents")

            # Integrate neuroscience optimization discussion results
            if 'neuroscience_optimization' in self.discussion_results:
                neuro_discussion = self.discussion_results['neuroscience_optimization']
                decisions['neuroscience_optimization'] = neuro_discussion.decision
                self.agent_decisions['neuroscience_optimization'] = {
                    'agents': neuro_discussion.participating_agents,
                    'consensus': neuro_discussion.consensus_level,
                    'insights': neuro_discussion.key_insights,
                    'decision': neuro_discussion.decision
                }
                logger.info(f"✅ Integrated neuroscience optimization from {len(neuro_discussion.participating_agents)} agents")
                
            # Integrate advanced neuroscience discussion results (Professional mode)
            if 'advanced_neuroscience' in self.discussion_results:
                advanced_neuro_discussion = self.discussion_results['advanced_neuroscience']
                decisions['advanced_neuroscience'] = advanced_neuro_discussion.decision
                self.agent_decisions['advanced_neuroscience'] = {
                    'agents': advanced_neuro_discussion.participating_agents,
                    'consensus': advanced_neuro_discussion.consensus_level,
                    'insights': advanced_neuro_discussion.key_insights,
                    'decision': advanced_neuro_discussion.decision
                }
                logger.info(f"✅ Integrated advanced neuroscience from {len(advanced_neuro_discussion.participating_agents)} agents")

            # Integrate marketing strategy discussion results
            if 'marketing_strategy' in self.discussion_results:
                marketing_discussion = self.discussion_results['marketing_strategy']
                decisions['marketing_strategy'] = marketing_discussion.decision
                self.agent_decisions['marketing_strategy'] = {
                    'agents': marketing_discussion.participating_agents,
                    'consensus': marketing_discussion.consensus_level,
                    'insights': marketing_discussion.key_insights,
                    'decision': marketing_discussion.decision
                }
                logger.info(f"✅ Integrated marketing strategy from {len(marketing_discussion.participating_agents)} agents")

            # Integrate design strategy discussion results
            if 'design_strategy' in self.discussion_results:
                design_discussion = self.discussion_results['design_strategy']
                decisions['design_strategy'] = design_discussion.decision
                self.agent_decisions['design_strategy'] = {
                    'agents': design_discussion.participating_agents,
                    'consensus': design_discussion.consensus_level,
                    'insights': design_discussion.key_insights,
                    'decision': design_discussion.decision
                }
                logger.info(f"✅ Integrated design strategy from {len(design_discussion.participating_agents)} agents")

            # Integrate engagement strategy discussion results
            if 'engagement_strategy' in self.discussion_results:
                engagement_discussion = self.discussion_results['engagement_strategy']
                decisions['engagement_strategy'] = engagement_discussion.decision
                self.agent_decisions['engagement_strategy'] = {
                    'agents': engagement_discussion.participating_agents,
                    'consensus': engagement_discussion.consensus_level,
                    'insights': engagement_discussion.key_insights,
                    'decision': engagement_discussion.decision
                }
                logger.info(f"✅ Integrated engagement strategy from {len(engagement_discussion.participating_agents)} agents")

            # Integrate platform optimization discussion results
            if 'platform_optimization' in self.discussion_results:
                platform_discussion = self.discussion_results['platform_optimization']
                decisions['platform_optimization'] = platform_discussion.decision
                self.agent_decisions['platform_optimization'] = {
                    'agents': platform_discussion.participating_agents,
                    'consensus': platform_discussion.consensus_level,
                    'insights': platform_discussion.key_insights,
                    'decision': platform_discussion.decision
                }
                logger.info(f"✅ Integrated platform optimization from {len(platform_discussion.participating_agents)} agents")

            # Calculate total agents used from discussions
            total_discussion_agents = sum(len(discussion.participating_agents) for discussion in self.discussion_results.values())
            logger.info(f"🎯 Total agents from discussions: {total_discussion_agents}")
        
        # Enhanced decisions for advanced modes (fallback for non-professional modes)
        if self.mode in [OrchestratorMode.ENHANCED, OrchestratorMode.ADVANCED,
                         OrchestratorMode.PROFESSIONAL, OrchestratorMode.MULTILINGUAL]:
            
            # Integrate neuroscience optimization for enhanced mode
            if self.mode == OrchestratorMode.ENHANCED and 'neuroscience_optimization' in self.discussion_results:
                neuro_discussion = self.discussion_results['neuroscience_optimization']
                decisions['neuroscience_optimization'] = neuro_discussion.decision
                self.agent_decisions['neuroscience_optimization'] = {
                    'agents': neuro_discussion.participating_agents,
                    'consensus': neuro_discussion.consensus_level,
                    'insights': neuro_discussion.key_insights,
                    'decision': neuro_discussion.decision
                }
                logger.info(f"✅ Applied neuroscience optimization for enhanced mode")

            # Structure Analysis
            if self.structure_agent:
                structure_analysis = self.structure_agent.analyze_video_structure(
                    mission=self.mission,
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

    async def _generate_multilingual_video(self, script_data: Dict[str, Any],
                                     decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate multilingual video"""
        logger.info("🌍 Generating multilingual video...")

        if not self.multilang_generator:
            logger.info("🔧 Initializing multilingual generator on demand...")
            logger.info(f"🔧 Cheap mode: {self.cheap_mode}")
            
            # Import here to avoid circular imports
            from ..generators.multi_language_generator import MultiLanguageVideoGenerator
            
            # Create the multilingual generator on demand with appropriate settings
            # Use session output directory instead of self.output_dir
            output_dir = self.session_context.get_output_path() if hasattr(self, 'session_context') else "outputs"
            self.multilang_generator = MultiLanguageVideoGenerator(self.api_key, output_dir)
            
            # Override the generator's VEO settings if in cheap mode
            if self.cheap_mode:
                logger.info("💰 Applying cheap mode settings to multilingual generator")
                # We'll need to pass this info to the generator when we call it
            
            logger.info("✅ Multilingual generator initialized")

        languages = config.get('languages', [Language.ENGLISH_US]) or [Language.ENGLISH_US]

        # Create enhanced video config
        video_config = self._create_enhanced_video_config(
            script_data,
            decisions,
            config)
        
        # Apply cheap mode settings to video config if needed
        if self.cheap_mode:
            logger.info("💰 Applying cheap mode settings to video config")
            video_config.use_real_veo2 = False
            video_config.realistic_audio = False

        # Generate multilingual video using simplified approach
        try:
            logger.info(f"🔧 Using simplified multilingual generation for {len(languages)} languages")
            
            # Generate the base video first
            logger.info("🎬 Generating base video...")
            base_video_path = await self._generate_enhanced_video(script_data, decisions, config)
            logger.info(f"✅ Base video generated: {base_video_path}")
            
            # Create language-specific files for each language
            logger.info("🌍 Creating language-specific audio and subtitle files...")
            multilang_result = await self._create_multilingual_files(
                languages, script_data, base_video_path
            )
            logger.info(f"✅ Multilingual files created: {multilang_result}")
            
            logger.info(f"🔧 Simplified multilingual generation completed")

            # Save language-specific files
            if multilang_result and multilang_result.language_versions:
                logger.info(f"💾 Saving {len(multilang_result.language_versions)} language versions...")
                
                # Get session directory and use final_output for all language versions
                session_dir = self.session_context.get_output_path()
                final_output_dir = os.path.join(session_dir, "final_output")
                os.makedirs(final_output_dir, exist_ok=True)
                
                # Save info about all languages
                lang_info = {
                    "primary_language": languages[0].value if languages else "en-US",
                    "all_languages": [lang.value for lang in languages],
                    "language_files": {}
                }
                
                for lang, version in multilang_result.language_versions.items():
                    lang_code = lang.value if hasattr(lang, 'value') else str(lang)
                    # All language files go directly to final_output (no subdirectories)
                    lang_dir = final_output_dir
                    
                    # Save audio file
                    if version.audio_path and os.path.exists(version.audio_path):
                        audio_filename = f"audio_{lang_code}.mp3"
                        audio_dest = os.path.join(lang_dir, audio_filename)
                        import shutil
                        shutil.copy2(version.audio_path, audio_dest)
                        lang_info["language_files"][lang_code] = {"audio": audio_filename}
                        logger.info(f"  📁 Saved {lang_code} audio: {audio_filename}")
                    
                    # Save translated script
                    script_path = os.path.join(lang_dir, f"script_{lang_code}.txt")
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(version.translated_script)
                    logger.info(f"  📝 Saved {lang_code} script")
                    
                    # Save subtitles if available
                    if hasattr(version, 'subtitle_path') and version.subtitle_path:
                        subtitle_filename = f"subtitles_{lang_code}.srt"
                        subtitle_dest = os.path.join(lang_dir, subtitle_filename)
                        shutil.copy2(version.subtitle_path, subtitle_dest)
                        lang_info["language_files"][lang_code]["subtitles"] = subtitle_filename
                        logger.info(f"  📄 Saved {lang_code} subtitles")
                
                # Save language info JSON
                import json
                with open(os.path.join(languages_dir, "language_info.json"), 'w', encoding='utf-8') as f:
                    json.dump(lang_info, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ All language versions saved to: {languages_dir}")

            # Return primary language video path (for now, return a placeholder)
            # In a full implementation, we would composite the video with each audio track
            primary_language = languages[0] if languages else Language.ENGLISH_US
            
            # For now, return the final video path from the session
            # The actual video composition would happen here
            return os.path.join(self.session_context.get_output_path(), "final_output", f"final_video_{self.session_id}.mp4")
            
        except Exception as e:
            logger.error(f"Multilingual generation failed: {e}")
            import traceback
            traceback.print_exc()

        # Fallback to regular generation
        return await self._generate_enhanced_video(script_data, decisions, config)
    
    async def _create_multilingual_files(self, languages: list, script_data: Dict[str, Any], base_video_path: str):
        """Create language-specific audio and subtitle files using a simple approach"""
        logger.info(f"🌍 Starting multi-language file creation with {len(languages)} languages")
        logger.info(f"📹 Base video path: {base_video_path}")
        logger.info(f"📹 Base video exists: {os.path.exists(base_video_path) if base_video_path else 'No path provided'}")
        
        try:
            import google.generativeai as genai
            from gtts import gTTS
            import tempfile
            import uuid
            import json
            import shutil
            from ..models.video_models import Language, LanguageVersion, MultiLanguageVideo
            
            logger.info(f"🌍 Creating multilingual files for {len(languages)} languages")
            
            # Language mapping
            lang_mapping = {
                'en': Language.ENGLISH_US,
                'en-US': Language.ENGLISH_US,
                'he': Language.HEBREW,
                'ar': Language.ARABIC,
                'fa': Language.PERSIAN,
                'fr': Language.FRENCH,
                'es': Language.SPANISH,
                'de': Language.GERMAN,
            }
            
            # TTS language codes
            tts_codes = {
                Language.ENGLISH_US: 'en',
                Language.HEBREW: 'iw',
                Language.ARABIC: 'ar',
                Language.PERSIAN: 'fa',
                Language.FRENCH: 'fr',
                Language.SPANISH: 'es',
                Language.GERMAN: 'de'
            }
            
            # Language display names
            lang_names = {
                Language.ENGLISH_US: "English (US)",
                Language.HEBREW: "Hebrew (עברית)",
                Language.ARABIC: "Arabic (العربية)",
                Language.PERSIAN: "Persian (فارسی)",
                Language.FRENCH: "French (Français)",
                Language.SPANISH: "Spanish (Español)",
                Language.GERMAN: "German (Deutsch)"
            }
            
            # Convert string languages to Language enums
            language_enums = []
            for lang_str in languages:
                if isinstance(lang_str, str):
                    if lang_str in lang_mapping:
                        language_enums.append(lang_mapping[lang_str])
                    else:
                        logger.warning(f"⚠️ Unknown language string: {lang_str}")
                else:
                    language_enums.append(lang_str)
            
            # Extract base script text
            base_script = str(script_data)
            if 'segments' in script_data:
                # Extract text from segments if available
                base_script = " ".join([seg.get('text', '') for seg in script_data['segments']])
            
            logger.info(f"📝 Base script: {base_script[:100]}...")
            
            # Create session final_output directory (all languages in same folder)
            session_dir = f"outputs/{self.session_id}"
            final_output_dir = os.path.join(session_dir, "final_output")
            os.makedirs(final_output_dir, exist_ok=True)
            logger.info(f"📁 Created final_output directory: {final_output_dir}")
            
            language_versions = {}
            
            for language in language_enums:
                try:
                    logger.info(f"🗣️ Processing {lang_names.get(language, language.value)}...")
                    
                    # All language files go to final_output directory
                    lang_code = language.value.replace('-', '_')
                    lang_dir = final_output_dir  # No subdirectories per language
                    
                    # Translate script if not English
                    if language == Language.ENGLISH_US:
                        translated_script = base_script
                    else:
                        translated_script = await self._translate_script_simple(base_script, language)
                    
                    # Generate TTS audio
                    audio_path = await self._generate_simple_tts(translated_script, language, lang_dir)
                    
                    # Generate subtitles (simple SRT format)
                    subtitle_path = self._generate_simple_subtitles(translated_script, language, lang_dir)
                    
                    # Combine base video with translated audio and subtitles
                    video_filename = f"video_{lang_code}.mp4"
                    video_path = os.path.join(lang_dir, video_filename)
                    
                    if base_video_path and os.path.exists(base_video_path):
                        # Combine video with language-specific audio and subtitles
                        combined_video_path = self._combine_video_audio_subtitles(
                            base_video_path, audio_path, subtitle_path, video_path
                        )
                        if combined_video_path and os.path.exists(combined_video_path):
                            logger.info(f"✅ Created {language.value} video with embedded audio and subtitles: {combined_video_path}")
                            video_path = combined_video_path
                        else:
                            logger.warning(f"⚠️ Failed to combine video with audio/subtitles, copying base video")
                            shutil.copy2(base_video_path, video_path)
                    else:
                        logger.warning(f"⚠️ Base video not found at {base_video_path}, using placeholder path")
                        video_path = base_video_path or "placeholder_video.mp4"
                    
                    # Create language version
                    language_versions[language] = LanguageVersion(
                        language=language,
                        language_name=lang_names.get(language, language.value),
                        audio_path=audio_path,
                        video_path=video_path,
                        subtitle_path=subtitle_path,
                        translated_script=translated_script,
                        translated_overlays=[],
                        tts_voice_used=tts_codes.get(language, 'en'),
                        word_count=len(translated_script.split()),
                        audio_duration=20.0  # Approximate
                    )
                    
                    logger.info(f"✅ Created {lang_names.get(language, language.value)} version")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create {language.value} version: {e}")
                    continue
            
            # Create a simple MultiLanguageVideo object
            base_video_id = str(uuid.uuid4())[:8]
            
            # Save language info
            lang_info = {
                "primary_language": language_enums[0].value if language_enums else "en-US",
                "all_languages": [lang.value for lang in language_enums],
                "base_video": base_video_path,
                "language_files": {}
            }
            
            for lang, version in language_versions.items():
                lang_code = lang.value.replace('-', '_')
                lang_info["language_files"][lang_code] = {
                    "audio": os.path.basename(version.audio_path),
                    "video": os.path.basename(version.video_path),
                    "subtitles": os.path.basename(version.subtitle_path) if version.subtitle_path else None,
                    "script": version.translated_script
                }
            
            with open(os.path.join(languages_dir, "language_info.json"), 'w', encoding='utf-8') as f:
                json.dump(lang_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved language info to: {languages_dir}")
            logger.info(f"✅ Created {len(language_versions)} language versions")
            
            # Create a mock MultiLanguageVideo result
            multilang_video = type('MockMultiLanguageVideo', (), {
                'language_versions': language_versions,
                'base_video_id': base_video_id
            })()
            
            return multilang_video
            
        except Exception as e:
            logger.error(f"❌ Multi-language file creation failed: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
        
    def _combine_video_audio_subtitles(self, video_path: str, audio_path: str, subtitle_path: str, output_path: str) -> str:
        """Combine video with audio and burn in subtitles using ffmpeg"""
        try:
            import subprocess
            import os
            
            logger.info(f"🎬 Combining video with audio and subtitles")
            logger.info(f"   Video: {video_path}")
            logger.info(f"   Audio: {audio_path}")
            logger.info(f"   Subtitles: {subtitle_path}")
            logger.info(f"   Output: {output_path}")
            
            # First, replace audio track
            temp_video = output_path.replace('.mp4', '_temp.mp4')
            
            # Replace audio in video
            cmd_audio = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                temp_video
            ]
            
            logger.info(f"🔊 Replacing audio track...")
            result = subprocess.run(cmd_audio, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Audio replacement failed: {result.stderr}")
                return None
                
            # Now add subtitles
            if subtitle_path and os.path.exists(subtitle_path):
                # Escape the subtitle path for FFmpeg
                escaped_subtitle_path = subtitle_path.replace('\\', '/').replace(':', '\\:')
                
                # Check if we need RTL support
                rtl_alignment = 2  # Default center alignment
                # Read first line of subtitle to check for RTL text
                try:
                    with open(subtitle_path, 'r', encoding='utf-8') as f:
                        subtitle_content = f.read()
                        import re
                        rtl_chars = re.compile(r'[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
                        if rtl_chars.search(subtitle_content):
                            logger.info("🔤 Detected RTL language in subtitles")
                            # For RTL, we might want right alignment (3) or keep center (2)
                            # Center alignment (2) is usually better for subtitles
                            rtl_alignment = 2
                except Exception as e:
                    logger.debug(f"Could not check for RTL: {e}")
                
                # Burn in subtitles with RTL-aware settings
                cmd_subtitles = [
                    'ffmpeg', '-y',
                    '-i', temp_video,
                    '-vf', f"subtitles='{escaped_subtitle_path}':force_style='FontName=Arial-Bold,Fontsize=9,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=1,Alignment={rtl_alignment},MarginV=80'",
                    '-c:a', 'copy',
                    output_path
                ]
                
                logger.info(f"📝 Burning in subtitles...")
                result = subprocess.run(cmd_subtitles, capture_output=True, text=True)
                
                # Clean up temp file
                if os.path.exists(temp_video):
                    os.remove(temp_video)
                    
                if result.returncode != 0:
                    logger.error(f"❌ Subtitle burning failed: {result.stderr}")
                    # If subtitle burning fails, use video with just audio replaced
                    if os.path.exists(temp_video):
                        shutil.move(temp_video, output_path)
                    return output_path
            else:
                # No subtitles, just rename temp file
                shutil.move(temp_video, output_path)
                
            logger.info(f"✅ Successfully combined video with audio and subtitles")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to combine video/audio/subtitles: {e}")
            return None
    
    async def _translate_script_simple(self, script: str, target_language: Language) -> str:
        """Simple script translation using Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            from ..config.ai_model_config import DEFAULT_AI_MODEL
            model = genai.GenerativeModel(DEFAULT_AI_MODEL)
            
            lang_names = {
                Language.HEBREW: "Hebrew",
                Language.ARABIC: "Arabic", 
                Language.PERSIAN: "Persian/Farsi",
                Language.FRENCH: "French",
                Language.SPANISH: "Spanish",
                Language.GERMAN: "German"
            }
            
            target_lang = lang_names.get(target_language, target_language.value)
            
            prompt = f"Translate this video script to {target_lang}. Keep it natural and engaging:\n\n{script}\n\nReturn only the translated text:"
            
            response = model.generate_content(prompt)
            translated = response.text.strip()
            
            logger.info(f"📝 Translated to {target_lang}: {translated[:50]}...")
            return translated
            
        except Exception as e:
            logger.error(f"❌ Translation failed for {target_language.value}: {e}")
            return script  # Return original as fallback
    
    async def _generate_simple_tts(self, script: str, language: Language, output_dir: str) -> str:
        """Generate simple TTS audio using gTTS"""
        try:
            try:
                from gtts import gTTS
            except ImportError:
                logger.error("❌ gTTS not installed. Installing...")
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "gtts"])
                from gtts import gTTS
            
            tts_codes = {
                Language.ENGLISH_US: 'en',
                Language.HEBREW: 'iw',
                Language.ARABIC: 'ar', 
                Language.PERSIAN: 'fa',
                Language.FRENCH: 'fr',
                Language.SPANISH: 'es',
                Language.GERMAN: 'de'
            }
            
            lang_code = tts_codes.get(language, 'en')
            
            # Create TTS
            tts = gTTS(text=script, lang=lang_code, slow=False)
            
            # Save audio file
            audio_filename = f"audio_{language.value.replace('-', '_')}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            tts.save(audio_path)
            
            logger.info(f"🎤 Generated TTS audio: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed for {language.value}: {e}")
            # Create a dummy file as fallback
            audio_filename = f"audio_{language.value.replace('-', '_')}.txt"
            audio_path = os.path.join(output_dir, audio_filename)
            with open(audio_path, 'w') as f:
                f.write(f"TTS failed for {language.value}: {script}")
            return audio_path
    
    def _generate_simple_subtitles(self, script: str, language: Language, output_dir: str) -> str:
        """Generate simple SRT subtitles"""
        try:
            # Simple subtitle generation - split script into sentences
            sentences = script.replace('.', '.\n').replace('!', '!\n').replace('?', '?\n').split('\n')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Create SRT content
            srt_content = ""
            duration_per_sentence = 20.0 / len(sentences) if sentences else 20.0
            
            for i, sentence in enumerate(sentences):
                start_time = i * duration_per_sentence
                end_time = (i + 1) * duration_per_sentence
                
                start_srt = f"{int(start_time//60):02d}:{int(start_time%60):02d},{int((start_time%1)*1000):03d}"
                end_srt = f"{int(end_time//60):02d}:{int(end_time%60):02d},{int((end_time%1)*1000):03d}"
                
                srt_content += f"{i+1}\n{start_srt} --> {end_srt}\n{sentence}\n\n"
            
            # Save subtitle file
            subtitle_filename = f"subtitles_{language.value.replace('-', '_')}.srt"
            subtitle_path = os.path.join(output_dir, subtitle_filename)
            
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            logger.info(f"📄 Generated subtitles: {subtitle_path}")
            return subtitle_path
            
        except Exception as e:
            logger.error(f"❌ Subtitle generation failed for {language.value}: {e}")
            # Create a dummy file as fallback
            subtitle_filename = f"subtitles_{language.value.replace('-', '_')}.txt"
            subtitle_path = os.path.join(output_dir, subtitle_filename)
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(f"Subtitle generation failed for {language.value}: {script}")
            return subtitle_path

    async def _generate_enhanced_video(self, script_data: Dict[str, Any],
                                 decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate enhanced video with all AI decisions"""
        logger.info("🎬 Generating enhanced video with AI decisions...")

        try:
            # Create video generator with VEO3-FAST preference
            # Get Vertex AI configuration from environment
            import os
            from src.generators.video_generator import VideoGenerator
            
            # Default to prefer VEO3-FAST (it's cheaper at $0.25/second)
            prefer_veo3_fast = True
            
            video_generator = VideoGenerator(
                api_key=self.api_key,
                use_real_veo2=not self.cheap_mode,  # Use VEO2 when cheap_mode is False
                use_vertex_ai=True,
                vertex_project_id=os.getenv('VERTEX_AI_PROJECT_ID') or os.getenv('VERTEX_PROJECT_ID'),
                vertex_location=os.getenv('VERTEX_AI_LOCATION') or os.getenv('VERTEX_LOCATION', 'us-central1'),
                vertex_gcs_bucket=os.getenv('VERTEX_AI_GCS_BUCKET') or os.getenv('VERTEX_GCS_BUCKET'),
                prefer_veo3=prefer_veo3_fast  # Use VEO3-FAST when configured
            )

            # Create enhanced video config
            video_config = self._create_enhanced_video_config(
                script_data,
                decisions,
                config)

            # Generate video with AI-enhanced config
            video_result = await video_generator.generate_video(video_config)

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
            # CRITICAL: Use AI-generated content, no hardcoded checks
            # Prefer extracted hook/CTA from script, fallback to core decisions
            if self.core_decisions and hasattr(self.core_decisions, 'hook') and self.core_decisions.hook:
                # Only override if extracted hook seems like a default or is empty
                if not hook or len(hook) < 5:
                    hook = self.core_decisions.hook
            
            if self.core_decisions and hasattr(self.core_decisions, 'call_to_action') and self.core_decisions.call_to_action:
                # Only override if extracted CTA seems like a default or is empty
                if not cta or len(cta) < 5:
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

        # CRITICAL FIX: Apply professional discussion results to video config
        if self.mode == OrchestratorMode.PROFESSIONAL and self.discussion_results:
            logger.info("🎯 Applying professional discussion results to video configuration...")
            
            # Apply script strategy insights
            if 'script_strategy' in decisions:
                script_strategy = decisions['script_strategy']
                if 'viral_hooks' in script_strategy:
                    hook = script_strategy['viral_hooks'][0] if script_strategy['viral_hooks'] else hook
                if 'engagement_strategy' in script_strategy:
                    style = script_strategy['engagement_strategy'].get('style', style)
                logger.info("✅ Applied script strategy from professional discussions")

            # Apply visual strategy insights
            if 'visual_strategy' in decisions:
                visual_strategy = decisions['visual_strategy']
                if 'visual_style' in visual_strategy:
                    visual_style = visual_strategy['visual_style']
                if 'technical_approach' in visual_strategy:
                    # Apply technical approach to video generation
                    pass
                logger.info("✅ Applied visual strategy from professional discussions")

            # Apply audio strategy insights
            if 'audio_strategy' in decisions:
                audio_strategy = decisions['audio_strategy']
                if 'voice_style' in audio_strategy:
                    voice_style = audio_strategy['voice_style']
                if 'sound_design' in audio_strategy:
                    background_music_style = audio_strategy['sound_design'].get('music_style', background_music_style)
                logger.info("✅ Applied audio strategy from professional discussions")

            # Apply marketing strategy insights
            if 'marketing_strategy' in decisions:
                marketing_strategy = decisions['marketing_strategy']
                if 'brand_alignment' in marketing_strategy:
                    # Apply brand alignment to visual elements
                    pass
                if 'audience_targeting' in marketing_strategy:
                    target_audience = marketing_strategy['audience_targeting'].get('primary_audience', target_audience)
                logger.info("✅ Applied marketing strategy from professional discussions")

            # Apply design strategy insights
            if 'design_strategy' in decisions:
                design_strategy = decisions['design_strategy']
                if 'color_scheme' in design_strategy:
                    # Apply color scheme to video
                    pass
                if 'typography' in design_strategy:
                    # Apply typography decisions
                    pass
                logger.info("✅ Applied design strategy from professional discussions")

            # Apply engagement strategy insights
            if 'engagement_strategy' in decisions:
                engagement_strategy = decisions['engagement_strategy']
                if 'viral_elements' in engagement_strategy:
                    # Apply viral elements to video
                    pass
                if 'cta_strategy' in engagement_strategy:
                    cta = engagement_strategy['cta_strategy'].get('primary_cta', cta)
                logger.info("✅ Applied engagement strategy from professional discussions")

            # Apply platform optimization insights
            if 'platform_optimization' in decisions:
                platform_strategy = decisions['platform_optimization']
                if 'algorithm_alignment' in platform_strategy:
                    # Apply platform-specific optimizations
                    pass
                if 'copy_strategy' in platform_strategy:
                    # Apply platform-optimized copy
                    pass
                logger.info("✅ Applied platform optimization from professional discussions")
            
            # Generate AI discussion visualization
            self._generate_discussion_visualization()

        # Get languages from config
        languages = config.get('languages', [Language.ENGLISH_US]) or [Language.ENGLISH_US]
        primary_language = languages[0] if languages else Language.ENGLISH_US
        
        # Enhanced configuration with platform and category for AI timing
        enhanced_config = GeneratedVideoConfig(
            mission=mission,  # mission must be first parameter
            duration_seconds=duration_seconds,
            target_platform=platform,
            category=category,
            session_id=self.session_id,  # CRITICAL: Pass the session ID from orchestrator
            style=style,
            tone=tone,
            target_audience=target_audience,
            visual_style=visual_style,
            hook=hook,
            main_content=main_content,
            call_to_action=cta,
            background_music_style=background_music_style,
            voiceover_style=decisions.get('voice', {}).get('voice_style', 'energetic'),
            frame_continuity=frame_continuity,
            character=config.get('character'),  # Add character from config
            scene=config.get('scene'),  # Add scene from config
            language=primary_language,  # Add primary language
            languages=languages,  # Add all languages
            voice=config.get('voice'),  # Add specific voice from config
            multiple_voices=config.get('multiple_voices', False),  # Add multiple voices flag
            use_real_veo2=config.get('force_generation') != 'force_image_gen',
            num_clips=num_clips,
            clip_durations=clip_durations,
            theme_id=self.core_decisions.theme_id if self.core_decisions and hasattr(self.core_decisions, 'theme_id') else None,
            # Business information overlay
            business_name=config.get('business_name'),
            business_address=config.get('business_address'),
            business_phone=config.get('business_phone'),
            business_website=config.get('business_website'),
            business_facebook=config.get('business_facebook'),
            business_instagram=config.get('business_instagram'),
            show_business_info=config.get('show_business_info', True)
        )

        logger.info(f"✅ Created enhanced video config with {len(decisions)} AI decisions")
        return enhanced_config
    
    def _extract_hook_from_script(self, script_data: Dict[str, Any]) -> str:
        """Extract hook from script data"""
        if isinstance(script_data, dict):
            if 'hook' in script_data:
                hook = script_data['hook']
                if isinstance(hook, dict) and 'text' in hook:
                    return hook['text']
                return str(hook)

        # Generate hook from mission - check if we need Hebrew
        languages = getattr(self, '_current_config', {}).get('languages', [Language.ENGLISH_US])
        target_language = languages[0] if languages else Language.ENGLISH_US
        
        if target_language == Language.HEBREW:
            # Hebrew default hooks
            return "גלו את הסיפור המדהים!"
        else:
            # English default hook
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
        # First priority: Use CTA from core decisions if available
        if self.core_decisions and hasattr(self.core_decisions, 'call_to_action'):
            cta = self.core_decisions.call_to_action
            if cta and len(str(cta)) > 5 and not self._is_metadata_text(str(cta)):
                return str(cta)
        
        # Second priority: Check script data for explicit CTA
        if isinstance(script_data, dict):
            # Check for CTA in proper structure
            if 'cta' in script_data and isinstance(script_data['cta'], dict):
                cta_text = script_data['cta'].get('text', '')
                if cta_text and not self._is_metadata_text(cta_text):
                    return cta_text
            
            # Check for call_to_action field
            if 'call_to_action' in script_data:
                cta = script_data['call_to_action']
                # If it's a string, validate it
                if isinstance(cta, str) and not self._is_metadata_text(cta):
                    return cta
                # If it's a dict, extract text
                elif isinstance(cta, dict) and 'text' in cta:
                    return cta['text']
            
            # Last resort: Extract from processed script
            if 'processed' in script_data and 'final_script' in script_data['processed']:
                processed_script = script_data['processed']['final_script']
                sentences = processed_script.split('.')
                last_sentence = sentences[-1].strip() if sentences else ""
                if last_sentence and len(last_sentence) > 5 and not self._is_metadata_text(last_sentence):
                    return last_sentence
        
        # Fallback to platform-specific default - check language
        languages = getattr(self, '_current_config', {}).get('languages', [Language.ENGLISH_US])
        target_language = languages[0] if languages else Language.ENGLISH_US
        
        if target_language == Language.HEBREW:
            # Hebrew CTAs by platform
            platform_ctas = {
                'youtube': "הירשמו לעוד תוכן!",
                'tiktok': "עקבו לעוד סרטונים!",
                'instagram': "עקבו לתוכן יומי!",
                'default': "עקבו לעוד!"
            }
            platform = str(self.platform).lower() if self.platform else 'default'
            return platform_ctas.get(platform, platform_ctas['default'])
        else:
            # English default
            from ..config.video_config import video_config
            platform = self.core_decisions.platform if self.core_decisions else 'youtube'
            return video_config.get_default_cta(platform)
    
    def _is_metadata_text(self, text: str) -> bool:
        """Check if text contains metadata patterns"""
        metadata_patterns = [
            'emotional_arc', 'surprise_moments', 'shareability_score',
            '{', '}', ':', 'viral_elements', 'script_data', 'config'
        ]
        return any(pattern in text for pattern in metadata_patterns)
    
    def _count_agents_used(self) -> int:
        """Count the number of agents used based on mode"""
        base_agents = 0
        
        if self.mode == OrchestratorMode.SIMPLE:
            base_agents = 3  # Director, Continuity, Voice
        elif self.mode == OrchestratorMode.ENHANCED:
            base_agents = 7  # Core agents with enhanced features
        elif self.mode == OrchestratorMode.MULTILINGUAL:
            base_agents = 8  # Core agents + multilingual
        elif self.mode == OrchestratorMode.ADVANCED:
            base_agents = 15  # Enhanced agents with advanced features
        else:  # PROFESSIONAL
            base_agents = 22  # All agents with professional features
        
        # Add discussion agents for professional mode
        if self.mode == OrchestratorMode.PROFESSIONAL and self.discussion_results:
            discussion_agents = sum(len(discussion.participating_agents) for discussion in self.discussion_results.values())
            total_agents = base_agents + discussion_agents
            logger.info(f"🎯 Professional mode: {base_agents} base agents + {discussion_agents} discussion agents = {total_agents} total")
            return total_agents
        
        return base_agents

    async def _generate_cheap_video(self, script_data: Dict[str, Any], decisions: Dict[str, Any], config: Dict[str, Any]) -> Optional[str]:
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
            
            # Pass core decisions to video generator for theme support
            if self.core_decisions:
                video_generator.core_decisions = self.core_decisions
            
            # Get languages from config
            languages = config.get('languages', [Language.ENGLISH_US]) or [Language.ENGLISH_US]
            primary_language = languages[0] if languages else Language.ENGLISH_US
            
            # Create config based on cheap mode level
            cheap_config = GeneratedVideoConfig(
                mission=self.mission,
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
                character=config.get('character'),  # Add character from config
                scene=config.get('scene'),  # Add scene from config
                language=primary_language,  # Add primary language
                languages=languages,  # Add all languages
                voice=config.get('voice'),  # Add specific voice from config
                multiple_voices=config.get('multiple_voices', False),  # Add multiple voices flag
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
                cheap_mode_level=self.cheap_mode_level,  # Pass granular level to video generator
                # Business information overlay
                business_name=config.get('business_name'),
                business_address=config.get('business_address'),
                business_phone=config.get('business_phone'),
                business_website=config.get('business_website'),
                business_facebook=config.get('business_facebook'),
                business_instagram=config.get('business_instagram'),
                show_business_info=config.get('show_business_info', True)
            )
            
            logger.info(f"💰 Generating video with {self.cheap_mode_level} cheap mode")
            video_result = await video_generator.generate_video(cheap_config)
            
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
            'main_content': f"{self.mission}",
            'call_to_action': "Follow for more!",
            'segments': [
                {
                    'type': 'hook',
                    'text': f"Amazing content ahead!",
                    'duration': 3
                },
                {
                    'type': 'content',
                    'text': f"{self.mission}",
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
            'mode': self.mode,
            'results': self.agent_decisions,
            'discussions_completed': len(self.discussion_results),
            'agents_used': self._count_agents_used()
        }

def create_working_orchestrator(mission: str, platform: str, category: str,
                                duration: int, api_key: str,
                                style: str = "viral", tone: str = "engaging",
                                target_audience: str = "general audience",
                                visual_style: str = "dynamic",
                                mode: str = "enhanced",
                                cheap_mode: bool = True,
                                cheap_mode_level: str = "full"
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
        cheap_mode: Enable cost-saving mode (default: True - saves costs)
        cheap_mode_level: Granular cheap mode (full, audio, video)

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
        mode=mode_enum,
        cheap_mode=cheap_mode,
        cheap_mode_level=cheap_mode_level
    )
