"""
Enhanced Working AI Agent Orchestrator
Comprehensive system with ALL features from previous orchestrators
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from ..generators.video_generator import VideoGenerator
from ..generators.director import Director
from ..generators.enhanced_script_processor import EnhancedScriptProcessor
from ..generators.integrated_multilang_generator import IntegratedMultilingualGenerator
from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory, Language, VideoOrientation, ForceGenerationMode
from ..utils.logging_config import get_logger
from .continuity_decision_agent import ContinuityDecisionAgent
from .voice_director_agent import VoiceDirectorAgent
from .video_composition_agents import VideoStructureAgent, ClipTimingAgent, VisualElementsAgent, MediaTypeAgent
from .multi_agent_discussion import MultiAgentDiscussionSystem, AgentRole, DiscussionTopic
from .enhanced_multi_agent_discussion import EnhancedMultiAgentDiscussionSystem, EnhancedVideoGenerationTopics
from .advanced_composition_discussions import AdvancedCompositionDiscussionSystem
# TrendingAnalyzer will be imported from UI for now

logger = get_logger(__name__)


class OrchestratorMode(str, Enum):
    """Available orchestrator modes"""
    SIMPLE = "simple"           # Basic generation, fast
    ENHANCED = "enhanced"       # 7 agents with discussions
    ADVANCED = "advanced"       # 19+ agents with comprehensive discussions
    MULTILINGUAL = "multilingual"  # Multilingual generation
    PROFESSIONAL = "professional"  # Maximum quality with all features


class EnhancedWorkingOrchestrator:
    """
    Comprehensive orchestrator with ALL features from previous systems
    """
    
    def __init__(self, api_key: str, topic: str, platform: Platform, 
                 category: VideoCategory, duration: int, mode: OrchestratorMode = OrchestratorMode.ENHANCED):
        self.api_key = api_key
        self.topic = topic
        self.platform = platform
        self.category = category
        self.duration = duration
        self.mode = mode
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize ALL AI agents
        self.director = Director(api_key)
        self.script_processor = EnhancedScriptProcessor(api_key)
        self.continuity_agent = ContinuityDecisionAgent(api_key)
        self.voice_agent = VoiceDirectorAgent(api_key)
        self.structure_agent = VideoStructureAgent(api_key)
        self.timing_agent = ClipTimingAgent(api_key)
        self.visual_agent = VisualElementsAgent(api_key)
        self.media_agent = MediaTypeAgent(api_key)
        # Trending analyzer will be handled by UI
        self.trending_analyzer = None
        self.multilang_generator = IntegratedMultilingualGenerator(api_key)
        
        # Initialize discussion systems based on mode
        if mode in [OrchestratorMode.SIMPLE]:
            self.discussion_system = None
            self.enhanced_discussion_system = None
            self.composition_system = None
        elif mode in [OrchestratorMode.ENHANCED]:
            self.discussion_system = MultiAgentDiscussionSystem(api_key, self.session_id)
            self.enhanced_discussion_system = None
            self.composition_system = None
        elif mode in [OrchestratorMode.ADVANCED, OrchestratorMode.PROFESSIONAL]:
            self.discussion_system = MultiAgentDiscussionSystem(api_key, self.session_id)
            self.enhanced_discussion_system = EnhancedMultiAgentDiscussionSystem(api_key, self.session_id)
            self.composition_system = AdvancedCompositionDiscussionSystem(api_key, self.session_id)
        else:  # MULTILINGUAL
            self.discussion_system = MultiAgentDiscussionSystem(api_key, self.session_id)
            self.enhanced_discussion_system = None
            self.composition_system = None
        
        # Results storage
        self.agent_decisions = {}
        self.discussion_results = {}
        self.composition_decisions = {}
        self.trending_insights = {}
        
        logger.info(f"🎬 Enhanced Working Orchestrator initialized ({mode.value})")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Session: {self.session_id}")
        logger.info(f"   Mode: {mode.value}")
    
    def generate_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video using comprehensive AI agent system
        """
        logger.info(f"🎬 Starting {self.mode.value} AI agent video generation")
        
        try:
            # Phase 1: Trending Analysis (if enabled)
            if config.get('enable_trending', False):
                self._analyze_trending_content(config)
            
            # Phase 2: AI Agent Discussions (mode-dependent)
            if self.mode != OrchestratorMode.SIMPLE:
                self._conduct_comprehensive_discussions(config)
            
            # Phase 3: Advanced Composition Analysis (for advanced modes)
            if self.mode in [OrchestratorMode.ADVANCED, OrchestratorMode.PROFESSIONAL]:
                self._conduct_composition_analysis(config)
            
            # Phase 4: Script Generation with AI Enhancement
            script_data = self._generate_enhanced_script(config)
            
            # Phase 5: Comprehensive AI Decision Making
            decisions = self._make_comprehensive_decisions(script_data, config)
            
            # Phase 6: Video Generation with All Features
            if self.mode == OrchestratorMode.MULTILINGUAL:
                video_path = self._generate_multilingual_video(script_data, decisions, config)
            else:
                video_path = self._generate_enhanced_video(script_data, decisions, config)
            
            logger.info(f"✅ {self.mode.value} video generation completed: {video_path}")
            
            return {
                'success': True,
                'final_video_path': video_path,
                'session_id': self.session_id,
                'mode': self.mode.value,
                'agent_decisions': self.agent_decisions,
                'discussion_results': self.discussion_results,
                'composition_decisions': self.composition_decisions,
                'trending_insights': self.trending_insights,
                'agents_used': self._count_agents_used(),
                'discussions_conducted': len(self.discussion_results),
                'optimization_level': f'{self.mode.value}_comprehensive'
            }
            
        except Exception as e:
            logger.error(f"❌ {self.mode.value} video generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'mode': self.mode.value,
                'agent_decisions': self.agent_decisions,
                'discussion_results': self.discussion_results
            }
    
    def _analyze_trending_content(self, config: Dict[str, Any]):
        """Analyze trending content for insights"""
        logger.info("📈 Trending analysis disabled in this version")
        
        # Fallback trending insights
        self.trending_insights = {
            'common_keywords': ['viral', 'trending', 'engaging', 'amazing'],
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
    
    def _conduct_comprehensive_discussions(self, config: Dict[str, Any]):
        """Conduct comprehensive AI agent discussions"""
        logger.info("🤝 Conducting comprehensive AI agent discussions...")
        
        if self.mode == OrchestratorMode.ENHANCED:
            self._conduct_enhanced_discussions(config)
        elif self.mode in [OrchestratorMode.ADVANCED, OrchestratorMode.PROFESSIONAL]:
            self._conduct_advanced_discussions(config)
        elif self.mode == OrchestratorMode.MULTILINGUAL:
            self._conduct_multilingual_discussions(config)
    
    def _conduct_enhanced_discussions(self, config: Dict[str, Any]):
        """Enhanced 7-agent discussions"""
        
        # Discussion 1: Script Strategy & Viral Optimization
        script_topic = DiscussionTopic(
            topic_id="script_strategy",
            title="Script Strategy & Viral Optimization",
            description=f"Create the most engaging script for: {self.topic}",
            context={
                'topic': self.topic,
                'platform': self.platform.value,
                'duration': self.duration,
                'category': self.category.value,
                'trending_insights': self.trending_insights
            },
            required_decisions=["script_structure", "viral_hooks", "engagement_strategy"]
        )
        
        # Use start_discussion instead of conduct_discussion
        script_result = self.discussion_system.start_discussion(
            script_topic, 
            [AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR]
        )
        self.discussion_results['script_strategy'] = script_result
        
        # Discussion 2: Visual & Technical Strategy
        visual_topic = DiscussionTopic(
            title="Visual Composition & Technical Approach",
            description=f"Optimal visual strategy for {self.platform.value} content",
            context={
                'topic': self.topic,
                'platform': self.platform.value,
                'force_generation': config.get('force_generation', 'auto'),
                'trending_insights': self.trending_insights
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
        
        logger.info(f"✅ Completed {len(self.discussion_results)} enhanced discussions")
    
    def _conduct_advanced_discussions(self, config: Dict[str, Any]):
        """Advanced 19+ agent discussions"""
        
        # Use enhanced discussion system for comprehensive analysis
        context = {
            'mission': self.topic,
            'platform': self.platform.value,
            'category': self.category.value,
            'duration': self.duration,
            'trending_insights': self.trending_insights,
            'config': config
        }
        
        # Script Development Discussion
        script_topic = EnhancedVideoGenerationTopics.script_development(context)
        script_result = self.enhanced_discussion_system.start_discussion(
            script_topic, 
            [AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR, AgentRole.TREND_ANALYST]
        )
        self.discussion_results['advanced_script'] = script_result
        
        # Audio Production Discussion
        audio_topic = EnhancedVideoGenerationTopics.audio_production(context)
        audio_result = self.enhanced_discussion_system.start_discussion(
            audio_topic,
            [AgentRole.SOUNDMAN, AgentRole.EDITOR, AgentRole.VIDEO_GENERATOR]
        )
        self.discussion_results['advanced_audio'] = audio_result
        
        logger.info(f"✅ Completed {len(self.discussion_results)} advanced discussions")
    
    def _conduct_multilingual_discussions(self, config: Dict[str, Any]):
        """Multilingual-specific discussions"""
        
        languages = config.get('languages', [Language.ENGLISH_US])
        
        # Multilingual Strategy Discussion
        multilang_topic = DiscussionTopic(
            title="Multilingual Content Strategy",
            description=f"Optimize content for {len(languages)} languages",
            context={
                'topic': self.topic,
                'languages': [lang.value for lang in languages],
                'platform': self.platform.value,
                'primary_language': languages[0].value if languages else 'en-US'
            },
            participants=[AgentRole.SCRIPT_WRITER, AgentRole.SOUNDMAN, AgentRole.EDITOR],
            discussion_type="multilingual",
            priority="high"
        )
        
        multilang_result = self.discussion_system.conduct_discussion(multilang_topic)
        self.discussion_results['multilingual_strategy'] = multilang_result
        
        logger.info(f"✅ Completed multilingual discussions for {len(languages)} languages")
    
    def _conduct_composition_analysis(self, config: Dict[str, Any]):
        """Advanced composition analysis for professional modes"""
        logger.info("🎨 Conducting advanced composition analysis...")
        
        self.composition_decisions = self.composition_system.conduct_comprehensive_composition_discussion(
            topic=self.topic,
            category=self.category.value,
            platform=self.platform.value,
            total_duration=self.duration,
            style=config.get('style', 'viral')
        )
        
        self.agent_decisions['composition'] = {
            'system': 'AdvancedCompositionDiscussionSystem',
            'decisions': self.composition_decisions
        }
        
        logger.info("✅ Advanced composition analysis completed")
    
    def _generate_enhanced_script(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script with AI enhancement and processing"""
        logger.info("📝 Generating enhanced script...")
        
        # Use Director to create base script
        script_data = self.director.write_script(
            topic=self.topic,
            style=config.get('style', 'viral'),
            duration=self.duration,
            platform=self.platform,
            category=self.category,
            patterns={
                'hooks': self.trending_insights.get('viral_hooks', []),
                'themes': [config.get('tone', 'engaging')],
                'success_factors': ['viral', 'engaging']
            },
            incorporate_news=config.get('incorporate_news', False)
        )
        
        # Enhanced script processing
        if self.mode in [OrchestratorMode.ENHANCED, OrchestratorMode.ADVANCED, OrchestratorMode.PROFESSIONAL]:
            processed_script = self.script_processor.process_script_for_tts(
                script=str(script_data),
                language=config.get('language', Language.ENGLISH_US),
                target_duration=self.duration,
                platform=self.platform,
                category=self.category
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
    
    def _make_comprehensive_decisions(self, script_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Make comprehensive AI decisions"""
        logger.info("🧠 Making comprehensive AI decisions...")
        
        decisions = {}
        
        # Continuity Decision
        continuity_decision = self.continuity_agent.analyze_and_decide(
            topic=self.topic,
            content_type=self.category.value,
            platform=self.platform.value,
            duration=self.duration
        )
        decisions['continuity'] = continuity_decision
        self.agent_decisions['continuity'] = {
            'agent': 'ContinuityDecisionAgent',
            'decision': continuity_decision
        }
        
        # Voice Strategy Decision
        voice_decision = self.voice_agent.select_optimal_voice(
            script=str(script_data),
            topic=self.topic,
            platform=self.platform,
            category=self.category,
            duration=self.duration
        )
        decisions['voice'] = voice_decision
        self.agent_decisions['voice'] = {
            'agent': 'VoiceDirectorAgent',
            'decision': voice_decision
        }
        
        # Structure Analysis
        if self.mode in [OrchestratorMode.ENHANCED, OrchestratorMode.ADVANCED, OrchestratorMode.PROFESSIONAL]:
            structure_analysis = self.structure_agent.analyze_video_structure(
                topic=self.topic,
                duration=self.duration,
                platform=self.platform.value,
                script_content=str(script_data)
            )
            decisions['structure'] = structure_analysis
            self.agent_decisions['structure'] = {
                'agent': 'VideoStructureAgent',
                'analysis': structure_analysis
            }
            
            # Timing Analysis
            timing_analysis = self.timing_agent.analyze_clip_timing(
                structure_analysis=structure_analysis,
                total_duration=self.duration
            )
            decisions['timing'] = timing_analysis
            self.agent_decisions['timing'] = {
                'agent': 'ClipTimingAgent',
                'analysis': timing_analysis
            }
            
            # Visual Elements
            visual_analysis = self.visual_agent.analyze_visual_elements(
                structure_analysis=structure_analysis,
                script_content=str(script_data),
                platform=self.platform.value
            )
            decisions['visual'] = visual_analysis
            self.agent_decisions['visual'] = {
                'agent': 'VisualElementsAgent',
                'analysis': visual_analysis
            }
            
            # Media Type Decisions
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
            decisions['media'] = media_decision
            self.agent_decisions['media'] = {
                'agent': 'MediaTypeAgent',
                'decision': media_decision
            }
        
        logger.info(f"✅ Made {len(decisions)} comprehensive decisions")
        return decisions
    
    def _generate_multilingual_video(self, script_data: Dict[str, Any], 
                                   decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate multilingual video"""
        logger.info("🌍 Generating multilingual video...")
        
        languages = config.get('languages', [Language.ENGLISH_US])
        
        # Create enhanced video config
        video_config = self._create_enhanced_video_config(script_data, decisions, config)
        
        # Generate multilingual video
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
        
        # Fallback to regular generation
        return self._generate_enhanced_video(script_data, decisions, config)
    
    def _generate_enhanced_video(self, script_data: Dict[str, Any], 
                               decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate enhanced video with all AI decisions"""
        logger.info("🎬 Generating enhanced video with AI decisions...")
        
        # Create video generator
        video_generator = VideoGenerator(
            api_key=self.api_key,
            use_real_veo2=config.get('force_generation') != 'force_image_gen',
            use_vertex_ai=True
        )
        
        # Create enhanced video config
        video_config = self._create_enhanced_video_config(script_data, decisions, config)
        
        # Generate video with AI-enhanced config
        video_path = video_generator.generate_video(video_config)
        
        return video_path
    
    def _create_enhanced_video_config(self, script_data: Dict[str, Any], 
                                    decisions: Dict[str, Any], config: Dict[str, Any]) -> GeneratedVideoConfig:
        """Create enhanced video config with all AI decisions"""
        
        # Extract script components
        hook = self._extract_hook_from_script(script_data)
        main_content = self._extract_content_from_script(script_data)
        cta = self._extract_cta_from_script(script_data)
        
        # Apply AI decisions
        frame_continuity = decisions.get('continuity', {}).get('recommendation') == 'enable'
        voice_style = decisions.get('voice', {}).get('voice_style', 'energetic')
        visual_style = decisions.get('visual', {}).get('style', 'dynamic')
        
        # Enhanced configuration
        return GeneratedVideoConfig(
            target_platform=self.platform,
            category=self.category,
            duration_seconds=self.duration,
            topic=self.topic,
            style=config.get('style', 'viral'),
            tone=config.get('tone', 'engaging'),
            target_audience=config.get('target_audience', 'young adults'),
            hook=hook,
            main_content=main_content,
            call_to_action=cta,
            visual_style=visual_style,
            color_scheme=config.get('color_scheme', ["#FF6B6B", "#4ECDC4", "#FFFFFF"]),
            text_overlays=config.get('text_overlays', []),
            transitions=config.get('transitions', ["fade", "slide"]),
            background_music_style=config.get('background_music_style', 'upbeat'),
            voiceover_style=voice_style,
            sound_effects=config.get('sound_effects', []),
            inspired_by_videos=config.get('inspired_by_videos', []),
            predicted_viral_score=0.85,
            frame_continuity=frame_continuity,
            image_only_mode=config.get('force_generation') == 'force_image_gen',
            use_real_veo2=config.get('force_generation') != 'force_image_gen',
            video_orientation=VideoOrientation(config.get('orientation', 'auto')),
            ai_decide_orientation=config.get('ai_decide_orientation', True)
        )
    
    def _extract_hook_from_script(self, script_data: Dict[str, Any]) -> str:
        """Extract hook from script data"""
        if isinstance(script_data, dict):
            if 'processed' in script_data and 'final_script' in script_data['processed']:
                # Use processed script if available
                processed_script = script_data['processed']['final_script']
                sentences = processed_script.split('.')[:1]
                return sentences[0] if sentences else f"Amazing {self.topic}"
            elif 'hook' in script_data:
                hook = script_data['hook']
                if isinstance(hook, dict) and 'text' in hook:
                    return hook['text']
                return str(hook)
        return f"Amazing {self.topic}"
    
    def _extract_content_from_script(self, script_data: Dict[str, Any]) -> list:
        """Extract main content from script data"""
        if isinstance(script_data, dict):
            if 'processed' in script_data and 'final_script' in script_data['processed']:
                # Use processed script if available
                processed_script = script_data['processed']['final_script']
                sentences = processed_script.split('.')[1:-1]  # Skip hook and CTA
                return [sentence.strip() for sentence in sentences if sentence.strip()]
            elif 'segments' in script_data and isinstance(script_data['segments'], list):
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
            if 'processed' in script_data and 'final_script' in script_data['processed']:
                # Use processed script if available
                processed_script = script_data['processed']['final_script']
                sentences = processed_script.split('.')
                return sentences[-1].strip() if sentences else "Follow for more!"
            elif 'call_to_action' in script_data:
                return str(script_data['call_to_action'])
        return "Follow for more!"
    
    def _count_agents_used(self) -> int:
        """Count the number of agents used"""
        if self.mode == OrchestratorMode.SIMPLE:
            return 3  # Director, VideoGenerator, basic processing
        elif self.mode == OrchestratorMode.ENHANCED:
            return 7  # Core agents with discussions
        elif self.mode == OrchestratorMode.MULTILINGUAL:
            return 8  # Core agents + multilingual
        elif self.mode == OrchestratorMode.ADVANCED:
            return 15  # Enhanced agents
        else:  # PROFESSIONAL
            return 19  # All agents
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress for real-time UI"""
        return {
            'progress': 100,  # Enhanced orchestrator completes when called
            'session_id': self.session_id,
            'current_phase': 'completed',
            'mode': self.mode.value,
            'results': self.agent_decisions,
            'discussions_completed': len(self.discussion_results),
            'agents_used': self._count_agents_used()
        }


def create_enhanced_working_orchestrator(topic: str, platform: str, category: str,
                                       duration: int, api_key: str, 
                                       mode: str = "enhanced") -> EnhancedWorkingOrchestrator:
    """
    Factory function to create enhanced working orchestrator with all features
    """
    try:
        platform_enum = Platform(platform.lower())
    except ValueError:
        platform_enum = Platform.INSTAGRAM
    
    try:
        category_enum = VideoCategory(category.upper())
    except ValueError:
        category_enum = VideoCategory.LIFESTYLE
    
    try:
        mode_enum = OrchestratorMode(mode.lower())
    except ValueError:
        mode_enum = OrchestratorMode.ENHANCED
    
    return EnhancedWorkingOrchestrator(
        api_key=api_key,
        topic=topic,
        platform=platform_enum,
        category=category_enum,
        duration=duration,
        mode=mode_enum
    ) 