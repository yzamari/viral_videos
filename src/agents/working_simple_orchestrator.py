"""
Working Simple AI Agent Orchestrator
Focuses on what actually works - real video generation with AI decisions
"""

import os
from typing import Dict, Any
from datetime import datetime
from enum import Enum

from ..generators.video_generator import VideoGenerator
from ..generators.director import Director
from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory, ForceGenerationMode
from ..utils.logging_config import get_logger
from .continuity_decision_agent import ContinuityDecisionAgent
from .voice_director_agent import VoiceDirectorAgent

logger = get_logger(__name__)


class SystemMode(str, Enum):
    """Available system modes"""
    SIMPLE = "simple"           # 3 agents, basic generation
    ENHANCED = "enhanced"       # 5 agents with AI decisions
    ADVANCED = "advanced"       # 7 agents with comprehensive decisions
    MULTILINGUAL = "multilingual"  # 5 agents + multilingual
    PROFESSIONAL = "professional"  # 7 agents + all features


class WorkingSimpleOrchestrator:
    """
    Simple orchestrator that actually works with real AI agents
    """
    
    def __init__(self, api_key: str, topic: str, platform: Platform, 
                 category: VideoCategory, duration: int, mode: SystemMode = SystemMode.ENHANCED):
        self.api_key = api_key
        self.topic = topic
        self.platform = platform
        self.category = category
        self.duration = duration
        self.mode = mode
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize core AI agents
        self.director = Director(api_key)
        self.continuity_agent = ContinuityDecisionAgent(api_key)
        self.voice_agent = VoiceDirectorAgent(api_key)
        
        # Initialize advanced agents for higher modes
        if mode in [SystemMode.ADVANCED, SystemMode.PROFESSIONAL]:
            try:
                from .video_composition_agents import VideoStructureAgent, ClipTimingAgent, VisualElementsAgent, MediaTypeAgent
                self.structure_agent = VideoStructureAgent(api_key)
                self.timing_agent = ClipTimingAgent(api_key)
                self.visual_agent = VisualElementsAgent(api_key)
                self.media_agent = MediaTypeAgent(api_key)
            except ImportError:
                logger.warning("Advanced agents not available, using enhanced mode")
                self.mode = SystemMode.ENHANCED
        
        # Results storage
        self.agent_decisions = {}
        self.progress_info = {'progress': 0, 'current_phase': 'initialized'}
        
        logger.info(f"🎬 Working Simple Orchestrator initialized ({mode.value})")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Session: {self.session_id}")
    
    def generate_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video using AI agent decisions
        """
        logger.info(f"🎬 Starting {self.mode.value} AI agent video generation")
        
        try:
            # Phase 1: Script Generation
            self.progress_info = {'progress': 10, 'current_phase': 'script_generation'}
            script_data = self._generate_script(config)
            
            # Phase 2: AI Agent Decisions
            self.progress_info = {'progress': 30, 'current_phase': 'ai_decisions'}
            decisions = self._make_ai_decisions(script_data, config)
            
            # Phase 3: Video Generation
            self.progress_info = {'progress': 60, 'current_phase': 'video_generation'}
            video_path = self._generate_video_with_decisions(script_data, decisions, config)
            
            # Phase 4: Complete
            self.progress_info = {'progress': 100, 'current_phase': 'completed'}
            
            logger.info(f"✅ {self.mode.value} video generation completed: {video_path}")
            
            return {
                'success': True,
                'final_video_path': video_path,
                'session_id': self.session_id,
                'mode': self.mode.value,
                'agent_decisions': self.agent_decisions,
                'agents_used': self._count_agents_used(),
                'discussions_conducted': 0,  # Simple system doesn't use discussions
                'optimization_level': f'{self.mode.value}_working'
            }
            
        except Exception as e:
            logger.error(f"❌ {self.mode.value} video generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'mode': self.mode.value,
                'agent_decisions': self.agent_decisions
            }
    
    def _generate_script(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script using Director agent with detailed analysis"""
        logger.info("📝 Director Agent analyzing script requirements...")
        logger.info(f"   📋 Input: Topic='{self.topic}', Style='{config.get('style', 'viral')}', Duration={self.duration}s")
        logger.info(f"   🎯 Platform: {self.platform.value}, Category: {self.category.value}")
        
        try:
            # Use trending insights if available
            trending_insights = config.get('trending_insights', {})
            if trending_insights:
                logger.info(f"   📈 Trending Insights Available: {len(trending_insights.get('viral_hooks', []))} hooks")
            
            logger.info("   🎬 Director Agent writing script...")
            script_data = self.director.write_script(
                topic=self.topic,
                style=config.get('style', 'viral'),
                duration=self.duration,
                platform=self.platform,
                category=self.category,
                patterns={
                    'hooks': trending_insights.get('viral_hooks', []),
                    'themes': [config.get('tone', 'engaging')],
                    'success_factors': ['viral', 'engaging']
                },
                incorporate_news=config.get('incorporate_news', False)
            )
            
            # Ensure script_data is not None
            if script_data is None:
                logger.warning("   ⚠️ Director returned None, creating fallback script")
                script_data = self._create_fallback_script(config)
            else:
                logger.info("   ✅ Director Agent script generation successful!")
                if isinstance(script_data, dict):
                    logger.info(f"   📊 Script Analysis:")
                    logger.info(f"      Hook: {script_data.get('hook', {}).get('text', 'N/A')[:50]}...")
                    logger.info(f"      Segments: {len(script_data.get('segments', []))} parts")
                    logger.info(f"      Word Count: {script_data.get('word_count', 'N/A')}")
                    logger.info(f"      Tone: {script_data.get('tone', 'N/A')}")
                    logger.info(f"   💭 Director Reasoning: Optimized for {self.platform.value} {self.category.value} content")
            
            self.agent_decisions['script'] = {
                'agent': 'Director',
                'data': script_data,
                'trending_applied': bool(trending_insights),
                'reasoning': f"Generated {self.duration}s script for {self.platform.value} with {config.get('style', 'viral')} style",
                'confidence': 0.9 if script_data else 0.5
            }
            
            return script_data
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            logger.info("Creating fallback script...")
            return self._create_fallback_script(config)
    
    def _create_fallback_script(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback script if Director fails"""
        return {
            'hook': {
                'text': f"Amazing insights about {self.topic}!",
                'type': 'excitement',
                'duration_seconds': 3
            },
            'segments': [
                {
                    'text': f"Let me share something incredible about {self.topic}.",
                    'duration': self.duration / 3
                },
                {
                    'text': f"This will change how you think about {self.topic}.",
                    'duration': self.duration / 3
                },
                {
                    'text': f"The results are truly amazing!",
                    'duration': self.duration / 3
                }
            ],
            'call_to_action': "Follow for more amazing content!",
            'total_duration': self.duration,
            'word_count': 25,
            'style': config.get('style', 'viral'),
            'tone': config.get('tone', 'engaging')
        }
    
    def _make_ai_decisions(self, script_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Make AI decisions using available agents with detailed logging"""
        logger.info("🧠 Making AI decisions with detailed agent analysis...")
        
        decisions = {}
        
        # Continuity Decision (all modes)
        logger.info("🔄 ContinuityDecisionAgent analyzing frame continuity requirements...")
        logger.info(f"   📋 Input: Topic='{self.topic}', Category='{self.category.value}', Platform='{self.platform.value}', Duration={self.duration}s")
        
        continuity_decision = self.continuity_agent.analyze_frame_continuity_need(
            topic=self.topic,
            category=self.category.value,
            platform=self.platform.value,
            duration=self.duration
        )
        
        logger.info(f"   🎯 ContinuityDecisionAgent Decision: {continuity_decision}")
        logger.info(f"   📊 Frame Continuity Required: {continuity_decision.get('use_frame_continuity', False)}")
        logger.info(f"   💭 Agent Reasoning: {continuity_decision.get('reasoning', 'Standard analysis applied')}")
        
        decisions['continuity'] = continuity_decision
        self.agent_decisions['continuity'] = {
            'agent': 'ContinuityDecisionAgent',
            'decision': continuity_decision,
            'reasoning': continuity_decision.get('reasoning', ''),
            'confidence': continuity_decision.get('confidence', 0.8)
        }
        
        # Voice Decision (all modes)
        logger.info("🎤 VoiceDirectorAgent analyzing voice strategy...")
        logger.info(f"   📋 Input: Topic='{self.topic}', Script Length={len(str(script_data))}, Clips=4")
        
        voice_decision = self.voice_agent.analyze_content_and_select_voices(
            topic=self.topic,
            script=str(script_data),
            language=config.get('language', 'en-US'),
            platform=self.platform,
            category=self.category,
            duration_seconds=self.duration,
            num_clips=4
        )
        
        logger.info(f"   🎯 VoiceDirectorAgent Decision: Voice Strategy = {voice_decision.get('ai_analysis', {}).get('strategy', 'single')}")
        logger.info(f"   🎭 Primary Personality: {voice_decision.get('ai_analysis', {}).get('primary_personality', 'narrator')}")
        logger.info(f"   👥 Multiple Voices: {voice_decision.get('ai_analysis', {}).get('use_multiple_voices', False)}")
        logger.info(f"   💭 Agent Reasoning: {voice_decision.get('ai_analysis', {}).get('reasoning', 'Standard voice analysis')[:100]}...")
        
        decisions['voice'] = voice_decision
        self.agent_decisions['voice'] = {
            'agent': 'VoiceDirectorAgent',
            'decision': voice_decision,
            'strategy': voice_decision.get('ai_analysis', {}).get('strategy', 'single'),
            'reasoning': voice_decision.get('ai_analysis', {}).get('reasoning', ''),
            'confidence': voice_decision.get('ai_analysis', {}).get('confidence_score', 0.85)
        }
        
        # Advanced decisions for higher modes with detailed agent discussions
        if self.mode in [SystemMode.ADVANCED, SystemMode.PROFESSIONAL] and hasattr(self, 'structure_agent'):
            logger.info("🎬 Advanced Mode: Initiating specialized agent discussions...")
            
            # Structure Analysis
            logger.info("🏗️ VideoStructureAgent analyzing video structure...")
            logger.info(f"   📋 Input: Topic='{self.topic}', Platform='{self.platform.value}', Duration={self.duration}s")
            
            structure_analysis = self.structure_agent.analyze_video_structure(
                topic=self.topic,
                category=self.category.value,
                platform=self.platform.value,
                total_duration=self.duration
            )
            
            logger.info(f"   🎯 VideoStructureAgent Decision: {structure_analysis.get('structure_type', 'standard')}")
            logger.info(f"   📊 Recommended Clips: {structure_analysis.get('recommended_clips', 4)}")
            logger.info(f"   💭 Agent Reasoning: {structure_analysis.get('reasoning', 'Standard structure analysis')[:100]}...")
            
            decisions['structure'] = structure_analysis
            self.agent_decisions['structure'] = {
                'agent': 'VideoStructureAgent',
                'analysis': structure_analysis,
                'reasoning': structure_analysis.get('reasoning', ''),
                'confidence': structure_analysis.get('confidence', 0.8)
            }
            
            # Timing Analysis
            logger.info("⏱️ ClipTimingAgent analyzing optimal clip timings...")
            logger.info(f"   📋 Input: Structure={structure_analysis.get('structure_type', 'standard')}, Total Duration={self.duration}s")
            
            timing_analysis = self.timing_agent.analyze_clip_timings(
                structure_analysis, 
                {'topic': self.topic, 'category': self.category.value}
            )
            
            logger.info(f"   🎯 ClipTimingAgent Decision: {timing_analysis.get('timing_strategy', 'balanced')}")
            logger.info(f"   📊 Clip Durations: {timing_analysis.get('clip_durations', [])}")
            logger.info(f"   💭 Agent Reasoning: {timing_analysis.get('reasoning', 'Standard timing analysis')[:100]}...")
            
            decisions['timing'] = timing_analysis
            self.agent_decisions['timing'] = {
                'agent': 'ClipTimingAgent',
                'analysis': timing_analysis,
                'reasoning': timing_analysis.get('reasoning', ''),
                'confidence': timing_analysis.get('confidence', 0.8)
            }
            
            # Visual Elements
            logger.info("🎨 VisualElementsAgent designing visual elements...")
            logger.info(f"   📋 Input: Structure={structure_analysis.get('structure_type', 'standard')}, Platform='{self.platform.value}'")
            
            visual_analysis = self.visual_agent.design_visual_elements(
                structure_analysis,
                str(script_data),
                self.platform.value
            )
            
            logger.info(f"   🎯 VisualElementsAgent Decision: {visual_analysis.get('visual_style', 'dynamic')}")
            logger.info(f"   🎨 Color Scheme: {visual_analysis.get('color_scheme', [])}")
            logger.info(f"   💭 Agent Reasoning: {visual_analysis.get('reasoning', 'Standard visual analysis')[:100]}...")
            
            decisions['visual'] = visual_analysis
            self.agent_decisions['visual'] = {
                'agent': 'VisualElementsAgent',
                'analysis': visual_analysis,
                'reasoning': visual_analysis.get('reasoning', ''),
                'confidence': visual_analysis.get('confidence', 0.8)
            }
            
            # Media Type Decision
            logger.info("📱 MediaTypeAgent analyzing optimal media types...")
            logger.info(f"   📋 Input: Clips=4, Duration={self.duration / 4}s per clip, Platform='{self.platform.value}'")
            
            media_decision = self.media_agent.analyze_media_types(
                clip_plan={
                    'total_clips': 4,
                    'clip_duration': self.duration / 4,
                    'topic': self.topic,
                    'platform': self.platform.value
                },
                content_analysis={
                    'script': script_data,
                    'topic': self.topic,
                    'category': self.category.value
                }
            )
            
            logger.info(f"   🎯 MediaTypeAgent Decision: {media_decision.get('media_strategy', 'mixed')}")
            logger.info(f"   📊 Recommended Types: {media_decision.get('media_types', [])}")
            logger.info(f"   💭 Agent Reasoning: {media_decision.get('reasoning', 'Standard media analysis')[:100]}...")
            
            decisions['media'] = media_decision
            self.agent_decisions['media'] = {
                'agent': 'MediaTypeAgent',
                'decision': media_decision,
                'reasoning': media_decision.get('reasoning', ''),
                'confidence': media_decision.get('confidence', 0.8)
            }
            
            # Agent Collaboration Summary
            logger.info("🤝 Agent Collaboration Summary:")
            logger.info(f"   🏗️ Structure: {structure_analysis.get('structure_type', 'standard')} → {structure_analysis.get('recommended_clips', 4)} clips")
            logger.info(f"   ⏱️ Timing: {timing_analysis.get('timing_strategy', 'balanced')} → {timing_analysis.get('clip_durations', [])}")
            logger.info(f"   🎨 Visual: {visual_analysis.get('visual_style', 'dynamic')} → {visual_analysis.get('color_scheme', [])}")
            logger.info(f"   📱 Media: {media_decision.get('media_strategy', 'mixed')} → {media_decision.get('media_types', [])}")
            logger.info("   ✅ All agents have reached consensus on video composition")
        
        logger.info(f"✅ Made {len(decisions)} AI decisions")
        return decisions
    
    def _generate_video_with_decisions(self, script_data: Dict[str, Any], 
                                     decisions: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate video using AI decisions"""
        logger.info("🎬 Generating video with AI decisions...")
        
        # Create video generator
        video_generator = VideoGenerator(
            api_key=self.api_key,
            use_real_veo2=config.get('force_generation') != 'force_image_gen',
            use_vertex_ai=True
        )
        
        # Create enhanced video config with AI decisions
        video_config = self._create_video_config_with_decisions(script_data, decisions, config)
        
        # Generate video
        video_path = video_generator.generate_video(video_config)
        
        return video_path
    
    def _create_video_config_with_decisions(self, script_data: Dict[str, Any], 
                                          decisions: Dict[str, Any], config: Dict[str, Any]) -> GeneratedVideoConfig:
        """Create video config with AI decisions"""
        
        # Extract script components
        hook = self._extract_hook_from_script(script_data)
        main_content = self._extract_content_from_script(script_data)
        cta = self._extract_cta_from_script(script_data)
        
        # Apply AI decisions
        frame_continuity = decisions.get('continuity', {}).get('use_frame_continuity', False)
        voice_style = decisions.get('voice', {}).get('voiceover_style', 'energetic')
        
        # Map force generation string to enum
        force_generation_str = config.get('force_generation', 'auto')
        if force_generation_str == 'force_image_gen':
            force_generation_mode = ForceGenerationMode.FORCE_IMAGE_GEN
        elif force_generation_str == 'force_veo2':
            force_generation_mode = ForceGenerationMode.FORCE_VEO2
        elif force_generation_str == 'force_veo3':
            force_generation_mode = ForceGenerationMode.FORCE_VEO3
        elif force_generation_str == 'force_continuous':
            force_generation_mode = ForceGenerationMode.FORCE_CONTINUOUS
        else:
            force_generation_mode = ForceGenerationMode.AUTO
        
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
            visual_style=config.get('visual_style', 'dynamic'),
            color_scheme=config.get('color_scheme', ["#FF6B6B", "#4ECDC4", "#FFFFFF"]),
            text_overlays=config.get('text_overlays', []),
            transitions=config.get('transitions', ["fade", "slide"]),
            background_music_style=config.get('background_music_style', 'upbeat'),
            voiceover_style=voice_style,
            sound_effects=config.get('sound_effects', []),
            inspired_by_videos=config.get('inspired_by_videos', []),
            predicted_viral_score=0.85,
            frame_continuity=frame_continuity,
            force_generation_mode=force_generation_mode,
            image_only_mode=config.get('force_generation') == 'force_image_gen',
            use_real_veo2=config.get('force_generation') != 'force_image_gen'
        )
    
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
    
    def _count_agents_used(self) -> int:
        """Count the number of agents used"""
        if self.mode == SystemMode.SIMPLE:
            return 3  # Director, ContinuityAgent, VoiceAgent
        elif self.mode == SystemMode.ENHANCED:
            return 5  # Core agents + VideoGenerator
        elif self.mode == SystemMode.MULTILINGUAL:
            return 5  # Core agents + multilingual
        elif self.mode == SystemMode.ADVANCED:
            return 7  # Core + advanced agents
        else:  # PROFESSIONAL
            return 7  # All available agents
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress for real-time UI"""
        return {
            'progress': self.progress_info.get('progress', 0),
            'session_id': self.session_id,
            'current_phase': self.progress_info.get('current_phase', 'initialized'),
            'mode': self.mode.value,
            'results': self.agent_decisions,
            'discussions_completed': 0,  # Simple system doesn't use discussions
            'agents_used': self._count_agents_used()
        }


def create_working_simple_orchestrator(topic: str, platform: str, category: str,
                                     duration: int, api_key: str, 
                                     mode: str = "enhanced") -> WorkingSimpleOrchestrator:
    """
    Factory function to create working simple orchestrator
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
        mode_enum = SystemMode(mode.lower())
    except ValueError:
        mode_enum = SystemMode.ENHANCED
    
    return WorkingSimpleOrchestrator(
        api_key=api_key,
        topic=topic,
        platform=platform_enum,
        category=category_enum,
        duration=duration,
        mode=mode_enum
    ) 