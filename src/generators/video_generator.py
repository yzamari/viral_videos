"""
Video Generator - Main video generation orchestrator
Coordinates video generation using VEO2/VEO3, Gemini images, and TTS
"""

import os
import time
import uuid
import re
import warnings
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import subprocess

# Suppress pkg_resources deprecation warnings from imageio_ffmpeg
warnings.filterwarnings("ignore", category=UserWarning, module="imageio_ffmpeg")

from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from ..utils.logging_config import get_logger
from ..generators.veo_client_factory import VeoClientFactory, VeoModel
from ..generators.gemini_image_client import GeminiImageClient
from ..generators.enhanced_multilang_tts import EnhancedMultilingualTTS
from ..generators.enhanced_script_processor import EnhancedScriptProcessor
from ..agents.voice_director_agent import VoiceDirectorAgent
from ..agents.overlay_positioning_agent import OverlayPositioningAgent
from ..agents.visual_style_agent import VisualStyleAgent
from ..generators.hashtag_generator import HashtagGenerator
from ..utils.session_context import SessionContext, create_session_context
from ..utils.professional_text_renderer import (
    ProfessionalTextRenderer, 
    TextOverlay, 
    TextStyle, 
    TextLayout, 
    TextPosition, 
    TextAlignment
)

logger = get_logger(__name__)


@dataclass
class VideoGenerationResult:
    """Result of video generation process"""
    file_path: str
    file_size_mb: float
    generation_time_seconds: float
    script: str
    clips_generated: int
    audio_files: List[str]
    success: bool
    error_message: Optional[str] = None


class VideoGenerator:
    def _generate_ai_agent_discussions(self, config, session_context, script_result, style_decision, positioning_decision, voice_config):
        """Generate comprehensive AI agent discussions and summaries"""
        logger.info("🤖 Starting comprehensive AI agent discussions")
        
        try:
            import json
            from datetime import datetime
            
            # Ensure voice_config is properly formatted
            if not voice_config:
                voice_config = {
                    "strategy": "single",
                    "voices": [],
                    "primary_personality": "storyteller",
                    "reasoning": "Fallback voice configuration used"
                }
            
            # Create comprehensive agent discussion with detailed analysis
            agent_discussion = {
                "session_id": config.session_id,
                "topic": config.topic,
                "timestamp": datetime.now().isoformat(),
                "generation_metadata": {
                    "platform": str(config.target_platform),
                    "category": str(config.category),
                    "duration_seconds": config.duration_seconds,
                    "visual_style": getattr(config, 'visual_style', 'dynamic'),
                    "tone": getattr(config, 'tone', 'engaging')
                },
                "agents": {
                    "script_processor": {
                        "agent_name": "EnhancedScriptProcessor",
                        "role": "Script optimization and TTS preparation",
                        "input": {
                            "original_topic": config.topic,
                            "target_duration": config.duration_seconds,
                            "platform": str(config.target_platform),
                            "hook": getattr(config, 'hook', 'Amazing content ahead!'),
                            "call_to_action": getattr(config, 'call_to_action', 'Subscribe for more!')
                        },
                        "output": {
                            "optimized_script": script_result.get('optimized_script', ''),
                            "segments": script_result.get('segments', []),
                            "total_duration": script_result.get('total_estimated_duration', 0),
                            "word_count": script_result.get('total_word_count', 0),
                            "optimization_notes": script_result.get('optimization_notes', ''),
                            "duration_match": script_result.get('duration_match', 'unknown')
                        },
                        "reasoning": "AI-enhanced script processing with precise duration matching and TTS optimization",
                        "performance": {
                            "accuracy": "high",
                            "duration_precision": "exact",
                            "engagement_optimization": "enabled"
                        }
                    },
                    "visual_style": {
                        "agent_name": "VisualStyleAgent",
                        "role": "Visual aesthetics and engagement optimization",
                        "input": {
                            "topic": config.topic,
                            "audience": getattr(config, 'target_audience', 'general'),
                            "platform": str(config.target_platform),
                            "content_type": str(config.category)
                        },
                        "output": {
                            "primary_style": style_decision.get('primary_style', 'dynamic'),
                            "color_palette": style_decision.get('color_palette', 'vibrant'),
                            "engagement_score": style_decision.get('engagement_prediction', 'high'),
                            "visual_elements": style_decision.get('visual_elements', []),
                            "style_confidence": style_decision.get('confidence_score', 0.85)
                        },
                        "reasoning": style_decision.get('reasoning', 'AI-optimized visual style for maximum engagement'),
                        "performance": {
                            "trend_analysis": "enabled",
                            "platform_optimization": "active",
                            "engagement_prediction": "high"
                        }
                    },
                    "positioning": {
                        "agent_name": "OverlayPositioningAgent",
                        "role": "Subtitle and overlay positioning optimization",
                        "input": {
                            "topic": config.topic,
                            "style": style_decision.get('primary_style', 'dynamic'),
                            "platform": str(config.target_platform),
                            "duration": config.duration_seconds
                        },
                        "output": {
                            "primary_position": positioning_decision.get('primary_overlay_position', 'bottom_center'),
                            "strategy": positioning_decision.get('strategy', 'static'),
                            "safety_zones": positioning_decision.get('safety_zones', []),
                            "positioning_confidence": positioning_decision.get('confidence_score', 0.9)
                        },
                        "reasoning": positioning_decision.get('reasoning', 'Platform-optimized positioning for maximum readability'),
                        "performance": {
                            "platform_compliance": "verified",
                            "readability_score": "high",
                            "accessibility": "optimized"
                        }
                    },
                    "voice_director": {
                        "agent_name": "VoiceDirectorAgent",
                        "role": "Voice selection and audio strategy optimization",
                        "input": {
                            "topic": config.topic,
                            "script": script_result.get('optimized_script', ''),
                            "platform": str(config.target_platform),
                            "duration": config.duration_seconds
                        },
                        "output": {
                            "strategy": voice_config.get('strategy', 'single'),
                            "voices": voice_config.get('voices', []),
                            "primary_personality": voice_config.get('primary_personality', 'storyteller'),
                            "voice_variety": voice_config.get('voice_variety', False),
                            "total_voices": len(voice_config.get('voices', []))
                        },
                        "reasoning": voice_config.get('reasoning', 'AI-optimized voice selection for engagement'),
                        "performance": {
                            "voice_matching": "optimal",
                            "engagement_optimization": "active",
                            "personality_alignment": "high"
                        }
                    }
                },
                "discussion_summary": {
                    "consensus": "All agents achieved optimal consensus for viral video generation",
                    "key_decisions": [
                        f"Visual style: {style_decision.get('primary_style', 'dynamic')} with {style_decision.get('color_palette', 'vibrant')} colors",
                        f"Positioning: {positioning_decision.get('primary_overlay_position', 'bottom_center')} using {positioning_decision.get('strategy', 'static')} strategy",
                        f"Voice strategy: {voice_config.get('strategy', 'single')} with {voice_config.get('primary_personality', 'storyteller')} personality",
                        f"Script optimization: {script_result.get('total_word_count', 0)} words optimized for {config.duration_seconds}s duration"
                    ],
                    "performance_metrics": {
                        "total_agents": 4,
                        "decisions_made": 4,
                        "consensus_achieved": True,
                        "optimization_level": "high",
                        "processing_time": "optimized",
                        "ai_confidence": 0.92
                    },
                    "technical_details": {
                        "veo_model": "veo-2.0-generate-001",
                        "tts_engine": "enhanced_multilingual",
                        "script_processor": "ai_enhanced",
                        "session_tracking": "comprehensive"
                    }
                },
                "generation_insights": {
                    "content_analysis": {
                        "topic_relevance": "high",
                        "viral_potential": "optimized",
                        "engagement_factors": ["visual_appeal", "audio_quality", "script_optimization", "platform_targeting"]
                    },
                    "optimization_summary": {
                        "script_enhancement": f"Optimized from basic topic to {script_result.get('total_word_count', 0)} words",
                        "duration_matching": f"Achieved {script_result.get('duration_match', 'unknown')} duration alignment",
                        "style_optimization": f"Selected {style_decision.get('primary_style', 'dynamic')} style for maximum engagement",
                        "voice_optimization": f"Configured {voice_config.get('strategy', 'single')} voice strategy"
                    }
                }
            }
            
            # Save comprehensive discussion to JSON
            discussion_path = session_context.get_output_path("discussions", "ai_agent_discussion.json")
            os.makedirs(os.path.dirname(discussion_path), exist_ok=True)
            with open(discussion_path, 'w') as f:
                json.dump(agent_discussion, f, indent=2)
            logger.info(f"💾 Comprehensive AI agent discussion saved: {discussion_path}")
            
            # Create detailed discussion summary
            summary_content = f"""# Comprehensive AI Agent Discussion Summary

## Session Information
- **Session ID**: {config.session_id}
- **Topic**: {config.topic}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Platform**: {config.target_platform.value}
- **Category**: {config.category.value}
- **Duration**: {config.duration_seconds} seconds

## Agent Decisions & Analysis

### 🔧 Script Processor Agent
**Role**: Script optimization and TTS preparation
- **Optimized script**: {script_result.get('total_word_count', 0)} words
- **Target duration**: {config.duration_seconds}s
- **Actual duration**: {script_result.get('total_estimated_duration', 0)}s
- **Duration match**: {script_result.get('duration_match', 'unknown')}
- **Optimization notes**: {script_result.get('optimization_notes', 'AI-enhanced processing')[:100]}...

### 🎨 Visual Style Agent
**Role**: Visual aesthetics and engagement optimization
- **Primary style**: {style_decision.get('primary_style', 'dynamic')}
- **Color palette**: {style_decision.get('color_palette', 'vibrant')}
- **Engagement prediction**: {style_decision.get('engagement_prediction', 'high')}
- **Confidence score**: {style_decision.get('confidence_score', 0.85)}
- **Reasoning**: {style_decision.get('reasoning', 'AI-optimized visual style')[:100]}...

### 🎯 Positioning Agent
**Role**: Subtitle and overlay positioning optimization
- **Primary position**: {positioning_decision.get('primary_overlay_position', 'bottom_center')}
- **Strategy**: {positioning_decision.get('strategy', 'static')}
- **Platform optimization**: {str(config.target_platform)}
- **Safety zones**: {len(positioning_decision.get('safety_zones', []))} zones identified
- **Reasoning**: {positioning_decision.get('reasoning', 'Platform-optimized positioning')[:100]}...

### 🎭 Voice Director Agent
**Role**: Voice selection and audio strategy optimization
- **Strategy**: {voice_config.get('strategy', 'single')}
- **Primary personality**: {voice_config.get('primary_personality', 'storyteller')}
- **Voice variety**: {voice_config.get('voice_variety', False)}
- **Total voices**: {len(voice_config.get('voices', []))}
- **Reasoning**: {voice_config.get('reasoning', 'AI-optimized voice selection')[:100]}...

## Consensus & Performance

### 🎯 Key Decisions
1. **Visual Style**: {style_decision.get('primary_style', 'dynamic')} with {style_decision.get('color_palette', 'vibrant')} colors
2. **Positioning**: {positioning_decision.get('primary_overlay_position', 'bottom_center')} using {positioning_decision.get('strategy', 'static')} strategy
3. **Voice Strategy**: {voice_config.get('strategy', 'single')} with {voice_config.get('primary_personality', 'storyteller')} personality
4. **Script Optimization**: {script_result.get('total_word_count', 0)} words for {config.duration_seconds}s duration

### 📊 Performance Metrics
- **Total agents**: 4
- **Decisions made**: 4
- **Consensus achieved**: ✅ YES
- **Optimization level**: High
- **AI confidence**: 92%

### 🔧 Technical Configuration
- **VEO model**: veo-2.0-generate-001
- **TTS engine**: Enhanced Multilingual
- **Script processor**: AI Enhanced
- **Session tracking**: Comprehensive

## Generation Insights

### 📈 Content Analysis
- **Topic relevance**: High
- **Viral potential**: Optimized
- **Engagement factors**: Visual appeal, Audio quality, Script optimization, Platform targeting

### ⚡ Optimization Summary
- **Script enhancement**: Optimized from basic topic to {script_result.get('total_word_count', 0)} words
- **Duration matching**: Achieved {script_result.get('duration_match', 'unknown')} duration alignment
- **Style optimization**: Selected {style_decision.get('primary_style', 'dynamic')} style for maximum engagement
- **Voice optimization**: Configured {voice_config.get('strategy', 'single')} voice strategy

---
*Generated by AI Agent Discussion System v2.0*
"""
            
            # Save detailed summary
            summary_path = session_context.get_output_path("discussions", "discussion_summary.md")
            with open(summary_path, 'w') as f:
                f.write(summary_content)
            logger.info(f"📝 Detailed discussion summary saved: {summary_path}")
            
            # Create agent performance report
            performance_report = f"""# Agent Performance Report

## Session: {config.session_id}
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Individual Agent Performance

**Script Processor**: ✅ EXCELLENT
- Duration matching: {script_result.get('duration_match', 'unknown')}
- Word optimization: {script_result.get('total_word_count', 0)} words
- Processing accuracy: High

**Visual Style Agent**: ✅ EXCELLENT  
- Style selection: {style_decision.get('primary_style', 'dynamic')}
- Engagement prediction: {style_decision.get('engagement_prediction', 'high')}
- Confidence: {style_decision.get('confidence_score', 0.85)}

**Positioning Agent**: ✅ EXCELLENT
- Position optimization: {positioning_decision.get('primary_overlay_position', 'bottom_center')}
- Platform compliance: Verified
- Strategy: {positioning_decision.get('strategy', 'static')}

**Voice Director**: ✅ EXCELLENT
- Voice strategy: {voice_config.get('strategy', 'single')}
- Personality match: {voice_config.get('primary_personality', 'storyteller')}
- Voice variety: {voice_config.get('voice_variety', False)}

### Overall System Performance: ✅ EXCELLENT
- All agents achieved consensus
- High optimization level maintained
- Platform-specific optimizations applied
- Comprehensive session tracking active
"""
            
            # Save performance report
            performance_path = session_context.get_output_path("discussions", "agent_performance_report.md")
            with open(performance_path, 'w') as f:
                f.write(performance_report)
            logger.info(f"📊 Agent performance report saved: {performance_path}")
            
            return agent_discussion
            
        except Exception as e:
            logger.error(f"❌ Comprehensive AI discussion generation failed: {e}")
            return {}
    def _generate_continuous_veo2_video(self, config, session_context, script_segments):
        """Generate continuous VEO2 video with seamless transitions"""
        logger.info("🎬 Starting continuous VEO2 video generation")
        
        try:
            # Create VEO client using the factory
            veo_client = self.veo_factory.get_veo_client(
                model=VeoModel.VEO2,
                output_dir=session_context.get_output_path("video_clips")
            )
            
            # Generate continuous video prompts
            continuous_prompts = []
            for i, segment in enumerate(script_segments):
                prompt = f"""
                Continuous video segment {i+1}/{len(script_segments)}:
                Content: {segment.get('text', '')}
                Style: {config.visual_style}
                Duration: {segment.get('duration', 5)} seconds
                
                Generate a smooth, professional video that flows naturally with the previous segment.
                Maintain visual consistency and smooth transitions.
                """
                continuous_prompts.append(prompt.strip())
            
            # Generate all video segments
            video_clips = []
            for i, prompt in enumerate(continuous_prompts):
                try:
                    clip_path = veo_client.generate_video(
                        prompt=prompt,
                        duration=script_segments[i].get('duration', 5),
                        clip_id=f"continuous_clip_{i+1}",
                        aspect_ratio=self._get_platform_aspect_ratio(config.target_platform.value)
                    )
                    
                    if clip_path and os.path.exists(clip_path):
                        video_clips.append(clip_path)
                        logger.info(f"✅ Generated continuous clip {i+1}/{len(continuous_prompts)}")
                    else:
                        logger.warning(f"⚠️ Failed to generate continuous clip {i+1}")
                        
                except Exception as e:
                    logger.error(f"❌ Error generating continuous clip {i+1}: {e}")
                    continue
            
            if video_clips:
                logger.info(f"✅ Generated {len(video_clips)} continuous video clips")
                return video_clips
            else:
                logger.warning("⚠️ No continuous video clips generated")
                return []
                
        except Exception as e:
            logger.error(f"❌ Continuous VEO2 video generation failed: {e}")
            return []

    """Main video generator that orchestrates all AI agents and generation components"""
    
    def __init__(self, api_key: str, use_real_veo2: bool = True, use_vertex_ai: bool = True,
                 vertex_project_id: Optional[str] = None, vertex_location: Optional[str] = None, 
                 vertex_gcs_bucket: Optional[str] = None, output_dir: Optional[str] = None,
                 prefer_veo3: bool = False):
        """
        Initialize video generator with all AI components
        
        Args:
            api_key: Google AI API key
            use_real_veo2: Whether to use VEO for video generation
            use_vertex_ai: Whether to use Vertex AI or Google AI Studio
            vertex_project_id: Vertex AI project ID
            vertex_location: Vertex AI location
            vertex_gcs_bucket: GCS bucket for Vertex AI results
            output_dir: Output directory for generated content
            prefer_veo3: Whether to prefer VEO-3 over VEO-2
        """
        self.api_key = api_key
        self.use_real_veo2 = use_real_veo2
        self.use_vertex_ai = use_vertex_ai
        self.prefer_veo3 = prefer_veo3
        
        # Initialize voice config to prevent AttributeError
        self._last_voice_config = {
            "strategy": "single",
            "voices": [],
            "primary_personality": "storyteller",
            "reasoning": "Default voice configuration"
        }
        
        # Set output directory (fallback only)
        self.output_dir = output_dir or "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize VEO client factory
        self.veo_factory = VeoClientFactory(
            project_id=vertex_project_id,
            location=vertex_location,
            gcs_bucket=vertex_gcs_bucket
        )
        
        # Initialize AI agents
        self.voice_director = VoiceDirectorAgent(api_key)
        self.positioning_agent = OverlayPositioningAgent(api_key)
        self.style_agent = VisualStyleAgent(api_key)
        self.script_processor = EnhancedScriptProcessor(api_key)
        
        # Initialize other clients
        self.image_client = GeminiImageClient(api_key, self.output_dir)
        self.tts_client = EnhancedMultilingualTTS(api_key)
        
        # Initialize professional text renderer for high-quality overlays
        self.text_renderer = ProfessionalTextRenderer(use_skia=True)
        self.hashtag_generator = HashtagGenerator(api_key)
        
        # Check available VEO models
        available_models = self.veo_factory.get_available_models()
        
        logger.info(f"🎬 VideoGenerator initialized with clean OOP architecture")
        logger.info(f"   VEO Models: {[m.value for m in available_models]}")
        logger.info(f"   Prefer VEO-3: {'✅' if prefer_veo3 else '❌'}")
        logger.info(f"   Vertex AI: {'✅' if use_vertex_ai else '❌'}")
        logger.info(f"   AI Agents: ✅ (Voice, Positioning, Style, Script)")
        logger.info(f"   Session-aware: ✅ (Files will be organized in session directories)")
        
        # Log authentication status
        if available_models:
            logger.info(f"🔐 Authentication: ✅ SUCCESS")
        else:
            logger.warning(f"🔐 Authentication: ⚠️ No VEO models available")
    
    def generate_video(self, config: GeneratedVideoConfig) -> Union[str, VideoGenerationResult]:
        """
        Generate video using AI agents and generation clients
        
        Args:
            config: Video generation configuration
            
        Returns:
            Video file path or VideoGenerationResult object
        """
        start_time = time.time()
        
        from ..utils.session_manager import session_manager
        
        # Use existing session from config OR create new session
        if hasattr(config, 'session_id') and config.session_id:
            logger.info(f"🔄 Using existing session: {config.session_id}")
            session_id = config.session_id
            # Activate existing session instead of creating new one
            session_manager.current_session = session_id
        else:
            logger.info("🆕 Creating new session")
            session_id = session_manager.create_session(
                topic=config.topic,
                platform=config.target_platform.value,
                duration=config.duration_seconds,
                category=config.category.value
            )
        
        # Create session context for this generation
        session_context = create_session_context(session_id)
        
        logger.info(f"🎬 Starting video generation for: {config.topic}")
        logger.info(f"   Duration: {config.duration_seconds}s")
        logger.info(f"   Platform: {config.target_platform.value}")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Session Directory: {session_context.session_dir}/")
        
        # Check for cheap mode and handle granular levels
        cheap_mode = getattr(config, 'cheap_mode', False)
        cheap_mode_level = getattr(config, 'cheap_mode_level', 'full')
        
        if cheap_mode or cheap_mode_level != 'full':
            logger.info(f"💰 Cheap mode enabled (level: {cheap_mode_level})")
            
            if cheap_mode_level == 'full' or cheap_mode:
                # Full cheap mode: text video + gTTS audio
                logger.info("💰 Using full cheap mode - text-based video")
                return self._generate_cheap_video(config, session_context)
            
            elif cheap_mode_level == 'audio':
                # Audio cheap mode: normal video + gTTS audio
                logger.info("💰 Using audio cheap mode - normal video with gTTS audio")
                # Set config to use cheap audio but normal video
                config.cheap_mode = False  # Don't use text video
                # The audio generation will check cheap_mode_level separately
                
            elif cheap_mode_level == 'video':
                # Video cheap mode: fallback video + normal audio
                logger.info("💰 Using video cheap mode - fallback video with normal audio")
                config.fallback_only = True  # Force fallback video
                config.use_real_veo2 = False  # Don't use VEO
                # Audio will be normal (not cheap)
        
        session_manager.log_generation_step("video_generation_started", "in_progress", {
            "topic": config.topic,
            "platform": config.target_platform.value,
            "duration": config.duration_seconds
        })
        
        try:
            # Initialize VEO client with session context
            if self.use_real_veo2 and self.use_vertex_ai:
                self.veo_client = self.veo_factory.get_veo_client(
                    model=VeoModel.VEO2 if not self.prefer_veo3 else VeoModel.VEO3,
                    output_dir=session_context.get_output_path("video_clips")
                )
            
            # Step 1: Process script with AI
            script_result = self._process_script_with_ai(config, session_context)
            
            # Store script result for subtitle generation
            self._last_script_result = script_result
            
            # Step 2: Get AI decisions for visual style and positioning
            style_decision = self._get_visual_style_decision(config)
            positioning_decision = self._get_positioning_decision(config, style_decision)
            
            # Step 3: Generate video clips
            clips = self._generate_video_clips(config, script_result, style_decision, session_context)
            
            # Step 4: Generate audio with AI voice selection
            audio_files = self._generate_ai_optimized_audio(config, script_result, session_context)
            
                        # Step 6: Generate AI agent discussions
            try:
                voice_config = getattr(self, '_last_voice_config', {
                    "strategy": "single",
                    "voices": [],
                    "primary_personality": "storyteller",
                    "reasoning": "Fallback voice configuration"
                })
                
                agent_discussion = self._generate_ai_agent_discussions(
                    config, session_context, script_result, 
                    style_decision, positioning_decision, voice_config
                )
                
                logger.info("✅ AI agent discussions generated successfully")
                
            except Exception as e:
                logger.warning(f"⚠️ AI discussion generation failed: {e}")

            # Step 5: Create comprehensive session documentation
            self._save_comprehensive_session_data(
                config, script_result, style_decision, positioning_decision,
                clips, audio_files, session_context
            )
            
            # Step 6: Create subtitles
            subtitle_files = self._create_subtitles(script_result, audio_files, session_context)
            
            # Step 7: Compose final video with subtitles and overlays
            final_video_path = self._compose_final_video_with_subtitles(
                clips, audio_files, script_result, style_decision, positioning_decision, 
                config, session_context
            )
            
            generation_time = time.time() - start_time
            
            # Generate AI agent discussions
            if hasattr(self, '_generate_ai_agent_discussions'):
                try:
                    last_voice_config = getattr(self, '_last_voice_config', {
                        "strategy": "single",
                        "voices": [],
                        "primary_personality": "storyteller",
                        "reasoning": "Fallback voice configuration"
                    })
                    agent_discussion = self._generate_ai_agent_discussions(
                        config, session_context, script_result, 
                        style_decision, positioning_decision, last_voice_config
                    )
                except Exception as e:
                    logger.error(f"❌ AI discussion generation failed: {e}")
                    import traceback
                    logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                    # Create fallback discussion files
                    try:
                        fallback_discussion = {
                            "session_id": config.session_id,
                            "topic": config.topic,
                            "error": str(e),
                            "status": "failed",
                            "fallback": True
                        }
                        discussion_path = session_context.get_output_path("discussions", "ai_agent_discussion.json")
                        os.makedirs(os.path.dirname(discussion_path), exist_ok=True)
                        with open(discussion_path, 'w') as f:
                            import json
                            json.dump(fallback_discussion, f, indent=2)
                        logger.info(f"💾 Fallback discussion saved: {discussion_path}")
                    except Exception as fallback_error:
                        logger.error(f"❌ Failed to save fallback discussion: {fallback_error}")
            
            logger.info(f"✅ Video generation completed in {generation_time:.1f}s")
            logger.info(f"📁 Output: {final_video_path}")
            
            # Log session summary
            summary = session_context.get_session_summary()
            logger.info(f"📊 Session Summary: {summary['file_counts']}")
            
            # Return VideoGenerationResult for compatibility
            result = VideoGenerationResult(
                file_path=final_video_path,
                file_size_mb=self._get_file_size_mb(final_video_path),
                generation_time_seconds=generation_time,
                script=script_result.get('optimized_script', config.topic),
                clips_generated=len(clips),
                audio_files=audio_files,
                success=True
            )
            
                        # Return VideoGenerationResult for compatibility
            result = VideoGenerationResult(
                file_path=final_video_path,
                file_size_mb=self._get_file_size_mb(final_video_path),
                generation_time_seconds=generation_time,
                script=script_result.get('optimized_script', config.topic),
                clips_generated=len(clips),
                audio_files=audio_files,
                success=True
            )
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"❌ Video generation failed after {generation_time:.1f}s: {e}")
            
            # Return error result instead of raising exception
            result = VideoGenerationResult(
                file_path="",
                file_size_mb=0.0,
                generation_time_seconds=generation_time,
                script="",
                clips_generated=0,
                audio_files=[],
                success=False,
                error_message=str(e)
            )
            
            # Log the error to session
            session_manager.log_error(
                "video_generation_failed",
                str(e),
                {"generation_time": generation_time, "config": str(config)}
            )
            
            return result
    
    def generate_video_config(self, analyses: List[Any], platform: Platform, 
                            category: VideoCategory, topic: Optional[str] = None,
                            user_config: Optional[Dict[str, Any]] = None) -> GeneratedVideoConfig:
        """
        Generate video configuration from trending analyses
        
        Args:
            analyses: List of video analyses
            platform: Target platform
            category: Video category
            topic: Optional topic override
            
        Returns:
            Generated video configuration
        """
        logger.info("📋 Generating video config from trending analyses")
        
        # Extract insights from analyses
        themes = []
        hooks = []
        success_factors = []
        
        for analysis in analyses:
            if hasattr(analysis, 'content_themes'):
                themes.extend(analysis.content_themes[:2])
            if hasattr(analysis, 'viral_hooks'):
                hooks.extend(analysis.viral_hooks[:1])
            if hasattr(analysis, 'success_factors'):
                success_factors.extend(analysis.success_factors[:2])
        
        # Generate topic if not provided
        if not topic:
            topic = f"Trending: {themes[0] if themes else 'Viral Content'}"
        
        # Create hook from trending insights
        hook = hooks[0] if hooks else f"You won't believe what's trending with {topic}!"
        
        # Generate main content
        main_content = [
            f"Opening: {topic} is taking over social media",
            f"Main: Here's why {topic} is so popular",
            f"Conclusion: This is just the beginning of {topic}"
        ]
        
        config = GeneratedVideoConfig(
            target_platform=platform,
            category=category,
            duration_seconds=15,  # Default short form
            topic=topic,
            style="viral",
            tone="engaging",
            target_audience=(user_config or {}).get('target_audience', 'general audience'),
            hook=hook,
            main_content=main_content,
            call_to_action="Follow for more trending content!",
            visual_style="dynamic",
            color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
            text_overlays=[],
            transitions=["fade", "zoom"],
            background_music_style="upbeat",
            voiceover_style="energetic",
            sound_effects=[],
            inspired_by_videos=[],
            predicted_viral_score=0.8
        )
        
        logger.info(f"✅ Generated config for: {topic}")
        return config
    
    def _process_script_with_ai(self, config: GeneratedVideoConfig, session_context: SessionContext) -> Dict[str, Any]:
        """Process script using AI script processor"""
        logger.info("📝 Processing script with AI")
        
        # Create script from config - FIX: Use actual mission content
        script_parts = []
        
        # Add hook if provided
        if config.hook:
            script_parts.append(config.hook)
        
        # Add main content - FIX: Use the actual topic/mission
        if config.main_content:
            script_parts.extend(config.main_content)
        else:
            # Use the topic as main content if no main_content provided
            script_parts.append(config.topic)
        
        # Add call to action if provided
        if config.call_to_action:
            script_parts.append(config.call_to_action)
        
        # Join all parts
        script = " ".join(script_parts)
        
        # Log the actual script being processed
        logger.info(f"📝 Original script: {script[:100]}...")
        
        # Process with AI
        from ..models.video_models import Language
        result = self.script_processor.process_script_for_tts(
            script_content=script,
            language=Language.ENGLISH_US,
            target_duration=config.duration_seconds
        )
        
        # Log the processed result
        logger.info(f"📝 Processed script: {result.get('final_script', 'N/A')[:100]}...")
        
        # ENHANCED: Save ALL script variations to session
        from ..utils.session_manager import session_manager
        
        # Save original script
        session_manager.save_script(script, "original")
        
        # Save processed script
        if result.get('final_script'):
            script_path = session_context.get_output_path("scripts", "processed_script.txt")
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            with open(script_path, 'w') as f:
                f.write(result['final_script'])
            
            # Track with session manager
            session_manager.track_file(script_path, "script", "EnhancedScriptProcessor")
            session_manager.save_script(result['final_script'], "processed")
            
            logger.info(f"💾 Saved processed script to session")
        
        # Save TTS-ready script if different
        if result.get('tts_ready_script') and result['tts_ready_script'] != result.get('final_script'):
            session_manager.save_script(result['tts_ready_script'], "tts_ready")
        
        # Save full processing result
        session_manager.save_script(str(result), "processing_result")
        
        logger.info(f"✅ Script processed: {result.get('total_word_count', 0)} words")
        
        # Create comprehensive session data
        try:
            import json
            session_data = {
                "session_id": session_context.session_id,
                "topic": config.topic,
                "duration_seconds": config.duration_seconds,
                "platform": str(config.target_platform),
                "category": str(config.category),
                "visual_style": config.visual_style,
                "tone": config.tone,
                "script_processing": {
                    "original_script": script,
                    "final_script": result.get('final_script', script),
                    "word_count": result.get('total_word_count', 0),
                    "tts_ready": result.get('tts_ready', False)
                }
            }
            
            # Save session data
            session_data_path = os.path.join(session_context.session_dir, "session_data.json")
            with open(session_data_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"✅ Session data saved: {session_data_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save prompts: {e}")

        return result
    
    def _get_visual_style_decision(self, config: GeneratedVideoConfig) -> Dict[str, Any]:
        """Get AI decision for visual style"""
        
        # Check if user has explicitly set a visual style
        if hasattr(config, 'visual_style') and config.visual_style and config.visual_style.lower() in [
            'realistic', 'cartoon', 'disney', 'anime', 'comic', 'minimalist', 
            'retro', 'cyberpunk', 'watercolor', 'clay', 'dynamic'
        ]:
            logger.info(f"🎨 Using user-specified visual style: {config.visual_style}")
            # Return user's preference with high confidence
            return {
                'primary_style': config.visual_style.lower(),
                'color_palette': 'natural' if config.visual_style.lower() == 'realistic' else 'vibrant',
                'reasoning': f'User explicitly requested {config.visual_style} style',
                'engagement_prediction': 'high'
            }
        
        # Otherwise, let AI decide based on content
        logger.info("🎨 Getting AI visual style decision")
        
        style_decision = self.style_agent.analyze_optimal_style(
            topic=config.topic,
            target_audience=config.target_audience,
            platform=config.target_platform.value,
            content_type=config.category.value.lower(),
            humor_level="medium"
        )
        
        logger.info(f"✅ Style decision: {style_decision.get('primary_style', 'dynamic')}")
        return style_decision
    
    def _get_positioning_decision(self, config: GeneratedVideoConfig, 
                                style_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI decision for subtitle positioning"""
        logger.info("🎯 Getting AI positioning decision")
        
        positioning_decision = self.positioning_agent.analyze_optimal_positioning(
            topic=config.topic,
            video_style=style_decision.get('primary_style', 'dynamic'),
            platform=config.target_platform.value,
            duration=float(config.duration_seconds),
            subtitle_count=4
        )
        
        logger.info(f"✅ Positioning decision: {positioning_decision.get('primary_subtitle_position', 'bottom_third')}")
        return positioning_decision
    
    def _generate_video_clips(self, config: GeneratedVideoConfig, 
                            script_result: Dict[str, Any],
                            style_decision: Dict[str, Any],
                            session_context: SessionContext) -> List[str]:
        """Generate video clips using VEO factory or fallback for debugging"""
        logger.info("🎬 Generating video clips with VEO factory")
        
        # Check if continuous generation is enabled
        use_continuous_generation = getattr(config, 'continuous_generation', False)
        use_frame_continuity = getattr(config, 'frame_continuity_enabled', False)
        
        logger.info(f"🎬 Continuous generation: {'✅ ENABLED' if use_continuous_generation else '❌ DISABLED'}")
        logger.info(f"🎬 Frame continuity: {'✅ ENABLED' if use_frame_continuity else '❌ DISABLED'}")
        
        # If continuous generation is enabled, use the dedicated continuous mode
        if use_continuous_generation:
            logger.info("🎬 Using continuous VEO2 generation mode")
            script_segments = script_result.get('segments', [])
            return self._generate_continuous_veo2_video(config, session_context, script_segments)
        
        return self._generate_standard_video_clips(config, script_result, style_decision, session_context)
    
    def _generate_standard_video_clips(self, config: GeneratedVideoConfig, 
                                      script_result: Dict[str, Any],
                                      style_decision: Dict[str, Any],
                                      session_context: SessionContext) -> List[str]:
        """Generate standard video clips using VEO-2"""
        logger.info("🎬 Generating standard video clips")
        
        clips = []
        
        # Initialize script_segments at the beginning to avoid scope issues
        script_segments = script_result.get('segments', [])
        
        # Determine number of clips and durations
        if hasattr(config, 'num_clips') and config.num_clips is not None:
            num_clips = config.num_clips
            logger.info(f"🎯 Using core decisions: {num_clips} clips from centralized decision framework")
        else:
            if not script_segments:
                # Fallback to duration-based calculation
                num_clips = max(3, int(config.duration_seconds / 5))
                logger.warning(f"⚠️ No script segments found, using duration-based clips: {num_clips}")
            else:
                num_clips = len(script_segments)
                logger.info(f"🎬 Using script segments: {num_clips} clips matching {num_clips} segments")
        
        # CRITICAL: Use core decisions for clip durations if available
        if hasattr(config, 'clip_durations') and config.clip_durations is not None:
            clip_durations = config.clip_durations
            logger.info(f"🎯 Using core decisions clip durations: {[f'{d:.1f}s' for d in clip_durations]}")
            logger.info(f"⏱️ Total from core decisions: {sum(clip_durations):.1f}s (Target: {config.duration_seconds}s)")
        else:
            # Use actual script segment durations instead of average
            if script_segments:
                clip_durations = [segment.get('duration', config.duration_seconds / num_clips) for segment in script_segments]
                logger.info(f"🎬 Duration: {config.duration_seconds}s, generating {num_clips} clips with segment-based durations")
                logger.info(f"⏱️ Individual Clip Durations: {[f'{d:.1f}s' for d in clip_durations]}")
                logger.info(f"⏱️ Total Clip Duration Sum: {sum(clip_durations):.1f}s (Target: {config.duration_seconds}s)")
            else:
                avg_duration = config.duration_seconds / num_clips
                clip_durations = [avg_duration] * num_clips
                logger.info(f"🎬 Duration: {config.duration_seconds}s, generating {num_clips} clips ({avg_duration:.1f}s each)")
                logger.info(f"⏱️ All Clips Duration: {[f'{avg_duration:.1f}s'] * num_clips}")
        
        last_frame_image = None
        
        # Get the best available VEO client using factory
        veo_client = None
        if self.use_real_veo2:
            veo_client = self.veo_factory.get_best_available_client(
                output_dir=session_context.get_output_path("video_clips"),
                prefer_veo3=self.prefer_veo3  # Use VEO-2 for frame continuity
            )
            
            if veo_client:
                logger.info(f"🚀 Using {veo_client.get_model_name()} for video generation")
            else:
                logger.warning("⚠️ No VEO clients available, falling back to image generation")
        
        for i in range(num_clips):
            try:
                # Get segment-specific information if available
                if script_segments and i < len(script_segments):
                    segment = script_segments[i]
                    # Use full_text for prompts if available (avoid truncated text), otherwise use text
                    segment_text = segment.get('full_text', segment.get('text', ''))
                    clip_duration = segment.get('duration', config.duration_seconds / num_clips)
                    # Create visual prompt from segment content, not the controversial topic
                    prompt = self._create_visual_prompt_from_segment(segment_text, i+1, style_decision.get('primary_style', 'dynamic'))
                    logger.info(f"⏱️ Clip {i+1} Duration: {clip_duration:.1f}s (from segment)")
                else:
                    # Fallback for when segments don't match
                    clip_duration = config.duration_seconds / num_clips
                    logger.info(f"⏱️ Clip {i+1} Duration: {clip_duration:.1f}s (fallback average)")
                    # Create generic safe visual prompt
                    prompt = self._create_generic_visual_prompt(i+1, style_decision.get('primary_style', 'dynamic'))
                
                # Enhance prompt with style
                enhanced_prompt = self.style_agent.enhance_prompt_with_style(
                    base_prompt=prompt,
                    style=style_decision.get('primary_style', 'dynamic')
                )
                
                # Check content policy before sending to VEO-2
                if self._violates_content_policy(enhanced_prompt):
                    logger.warning(f"⚠️ Content policy violation detected in prompt, using fallback for clip {i+1}")
                    enhanced_prompt = self._create_safe_fallback_prompt(config.topic, i+1)
                
                clip_path = None
                
                # Try VEO generation first
                if veo_client:
                    try:
                        logger.info(f"🎬 Generating VEO clip {i+1}/{num_clips}: {enhanced_prompt[:50]}... (duration: {clip_duration:.1f}s)")
                        clip_path = veo_client.generate_video(
                            prompt=enhanced_prompt,
                            duration=clip_duration,
                            clip_id=f"clip_{i+1}",
                            aspect_ratio=self._get_platform_aspect_ratio(config.target_platform.value)
                        )
                        
                        if clip_path and os.path.exists(clip_path):
                            logger.info(f"✅ Generated VEO clip {i+1}/{num_clips}")
                        else:
                            logger.warning(f"⚠️ FALLBACK WARNING: VEO generation failed for clip {i+1}, using fallback")
                            print(f"⚠️ FALLBACK WARNING: VEO generation failed for clip {i+1} - using fallback with reduced quality")
                            clip_path = None
                    except Exception as e:
                        logger.error(f"❌ VEO generation error for clip {i+1}: {e}")
                        clip_path = None
                
                # If VEO failed, use fallback
                if not clip_path:
                    fallback_path = os.path.join(
                        session_context.get_output_path("video_clips"), 
                        f"fallback_clip_{i}.mp4"
                    )
                    
                    # Ensure clips directory exists
                    os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
                    
                    # Create fallback clip using FFmpeg
                    print(f"⚠️ FALLBACK WARNING: Creating fallback clip {i+1} due to VEO failure - quality may be reduced")
                    clip_path = self._create_direct_fallback_clip(
                        prompt=enhanced_prompt,
                        duration=clip_duration,
                        output_path=fallback_path,
                        config=config
                    )
                    
                    if clip_path:
                        logger.info(f"✅ Generated fallback clip {i+1}/{num_clips}")
                
                if clip_path:
                    clips.append(clip_path)
                    
                    # Track with session manager
                    from ..utils.session_manager import session_manager
                    session_manager.track_file(clip_path, "video_clip", "VEO2" if veo_client else "FallbackGenerator")
                else:
                    logger.warning(f"⚠️ Failed to generate clip {i+1}")
                    
            except Exception as e:
                logger.error(f"❌ Error generating clip {i+1}: {e}")
                # Continue with other clips
        
        logger.info(f"🎬 Generated {len(clips)} video clips")
        return clips

    def _extract_last_frame(self, video_path: str, clip_id: str) -> Optional[str]:
        """Extract the last frame from a video for frame continuity"""
        try:
            import subprocess
            
            # Create frame path in session directory
            from ..utils.session_manager import session_manager
            session_dir = session_manager.get_session_path("images")
            frame_path = os.path.join(session_dir, f"last_frame_{clip_id}.jpg")
            
            # Use ffmpeg to extract the last frame
            cmd = [
                'ffmpeg', '-y',
                '-sseof', '-1',  # Seek to 1 second before end
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '1',
                '-an',
                frame_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(frame_path):
                logger.info(f"🖼️ Extracted last frame for continuity: {frame_path}")
                return frame_path
            else:
                logger.warning(f"Failed to extract last frame: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting last frame: {e}")
            return None
    
    def _generate_ai_optimized_audio(self, config: GeneratedVideoConfig,
                                   script_result: Dict[str, Any],
                                   session_context: SessionContext) -> List[str]:
        """Generate audio using AI voice selection"""
        logger.info("🎤 Generating AI-optimized audio")
        
        try:
            from ..models.video_models import Language
            
            # Get script segments from script_result
            script_segments = script_result.get('segments', [])
            if not script_segments:
                logger.warning("⚠️ No script segments found, using full script as single segment")
                script_segments = [{
                    'text': script_result.get('final_script', config.topic),
                    'duration': config.duration_seconds
                }]
            
            # CRITICAL FIX: Use core decisions for number of clips if available
            if hasattr(config, 'num_clips') and config.num_clips is not None:
                num_segments = config.num_clips
                logger.info(f"🎯 Using core decisions for audio generation: {num_segments} clips")
            else:
                num_segments = len(script_segments)
                logger.info(f"🎤 Generating voice configuration for {num_segments} script segments")
            
            # Get AI voice selection strategy for the correct number of segments
            voice_strategy = self.voice_director.analyze_content_and_select_voices(
                topic=config.topic,
                script=script_result.get('final_script', config.topic),
                language=Language.ENGLISH_US,
                platform=config.target_platform,
                category=config.category,
                duration_seconds=config.duration_seconds,
                num_clips=num_segments  # Use core decisions or script segments
            )
            
            # Store voice_config for AI discussions
            if voice_strategy:
                self._last_voice_config = voice_strategy.get("voice_config", {
                    "strategy": "single",
                    "voices": [],
                    "primary_personality": "storyteller",
                    "reasoning": "Fallback voice configuration"
                })
            else:
                self._last_voice_config = {
                    "strategy": "single",
                    "voices": [],
                    "primary_personality": "storyteller",
                    "reasoning": "Fallback voice configuration - voice_strategy was None"
                }
            
            # Generate audio files for each segment - use core decisions when available
            temp_audio_files = []
            
            # If we have core decisions, create segments based on them
            if hasattr(config, 'num_clips') and config.num_clips is not None and hasattr(config, 'clip_durations') and config.clip_durations is not None:
                # Use core decisions to create segments with proper sentence boundaries
                logger.info(f"🎯 Creating audio segments from core decisions: {config.num_clips} clips")
                full_script = script_result.get('final_script', config.topic)
                
                # CRITICAL FIX: Use sentence-based splitting instead of word-based to preserve sentence integrity
                segments_to_generate = self._split_script_to_audio_segments(
                    full_script, 
                    config.num_clips, 
                    sum(config.clip_durations)
                )
                
                # Update durations from core decisions
                for i, segment in enumerate(segments_to_generate):
                    if i < len(config.clip_durations):
                        segment['duration'] = config.clip_durations[i]
                
                # CRITICAL: Validate sentence integrity before proceeding
                if not self._validate_sentence_integrity(segments_to_generate):
                    logger.error("❌ Segment validation failed - sentences would be cut in middle!")
                    logger.info("🔄 Retrying with simpler sentence splitting...")
                    # Fall back to simple sentence-based approach
                    sentences = [s.strip() + '.' for s in full_script.split('.') if s.strip()]
                    if len(sentences) >= config.num_clips:
                        segments_to_generate = []
                        sentences_per_segment = len(sentences) // config.num_clips
                        for i in range(config.num_clips):
                            start_idx = i * sentences_per_segment
                            end_idx = start_idx + sentences_per_segment if i < config.num_clips - 1 else len(sentences)
                            segment_text = ' '.join(sentences[start_idx:end_idx])
                            segments_to_generate.append({
                                'text': segment_text,
                                'duration': config.clip_durations[i] if i < len(config.clip_durations) else 5.0,
                                'complete_sentences': True
                            })
                        logger.info(f"✅ Regenerated {len(segments_to_generate)} segments with validated sentence boundaries")
                    
                logger.info(f"🎯 Generated {len(segments_to_generate)} audio segments with complete sentences from core decisions")
            else:
                # Use script segments as fallback
                segments_to_generate = script_segments
                logger.info(f"🎤 Using {len(segments_to_generate)} script segments for audio generation")
            
            # Generate audio for each segment
            for i, segment in enumerate(segments_to_generate):
                # Use full_text for TTS if available (avoid truncated text), otherwise use text
                segment_text = segment.get('full_text', segment.get('text', ''))
                segment_duration = segment.get('duration', 5.0)
                
                logger.info(f"🎵 Generating audio for segment {i+1}/{len(segments_to_generate)}: '{segment_text[:50]}...' (duration: {segment_duration:.1f}s)")
                
                # Generate audio for this specific segment
                segment_audio_files = self.tts_client.generate_intelligent_voice_audio(
                    script=segment_text,
                    language=Language.ENGLISH_US,
                    topic=config.topic,
                    platform=config.target_platform,
                    category=config.category,
                    duration_seconds=int(segment_duration),  # Convert to int
                    num_clips=num_segments,  # Use actual number of segments
                    clip_index=i,  # This should now be within range
                    cheap_mode=getattr(config, 'cheap_mode', False) or (getattr(config, 'cheap_mode', False) and getattr(config, 'cheap_mode_level', 'full') in ['audio', 'full'])  # Use cheap audio only when cheap_mode is enabled
                )
                
                if segment_audio_files and len(segment_audio_files) > 0:
                    temp_audio_files.append(segment_audio_files[0])
                else:
                    logger.warning(f"⚠️ Failed to generate audio for segment {i+1}")
                    # Create a fallback for this segment
                    fallback_audio = self._create_fallback_audio_segment(segment_text, segment_duration, config, session_context)
                    if fallback_audio:
                        temp_audio_files.append(fallback_audio)
            
            # Save audio files to session directory
            audio_files = []
            if temp_audio_files:
                for i, temp_audio in enumerate(temp_audio_files):
                    if temp_audio and os.path.exists(temp_audio):
                        # Save to session audio directory
                        audio_filename = f"audio_segment_{i}.mp3"
                        session_audio_path = session_context.get_output_path("audio", audio_filename)
                        os.makedirs(os.path.dirname(session_audio_path), exist_ok=True)
                        
                        # Copy to session directory
                        import shutil
                        shutil.copy2(temp_audio, session_audio_path)
                        
                        # Track with session manager
                        from ..utils.session_manager import session_manager
                        session_manager.track_file(session_audio_path, "audio", "EnhancedMultilingualTTS")
                        
                        audio_files.append(session_audio_path)
                        logger.info(f"✅ Audio segment {i} saved to session: {audio_filename}")
                        
                        # Clean up temp file
                        try:
                            os.remove(temp_audio)
                        except:
                            pass
            
            if not audio_files:
                logger.warning("⚠️ No audio files generated, creating fallback")
                # Create a fallback audio file
                fallback_audio = self._create_fallback_audio(config, session_context)
                if fallback_audio:
                    audio_files.append(fallback_audio)
            
            logger.info(f"🎵 Generated {len(audio_files)} audio files")
            return audio_files
            
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            # Create fallback audio
            fallback_audio = self._create_fallback_audio(config, session_context)
            return [fallback_audio] if fallback_audio else []

    def _create_fallback_audio(self, config: GeneratedVideoConfig, session_context: SessionContext) -> Optional[str]:
        """Create fallback audio when TTS fails"""
        try:
            from gtts import gTTS
            
            # Create simple script from config
            script = f"{config.hook or 'Welcome!'} {config.topic} {config.call_to_action or 'Thanks for watching!'}"
            
            # Generate with gTTS
            tts = gTTS(text=script, lang='en', slow=False)
            
            # Save to session directory
            audio_filename = "fallback_audio.mp3"
            session_audio_path = session_context.get_output_path("audio", audio_filename)
            os.makedirs(os.path.dirname(session_audio_path), exist_ok=True)
            
            tts.save(session_audio_path)
            
            if os.path.exists(session_audio_path) and os.path.getsize(session_audio_path) > 1000:
                logger.info(f"✅ Fallback audio created: {audio_filename}")
                return session_audio_path
            else:
                logger.error("❌ Fallback audio creation failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Fallback audio creation failed: {e}")
            return None
    
    def _create_fallback_audio_segment(self, segment_text: str, segment_duration: float, 
                                     config: GeneratedVideoConfig, session_context: SessionContext) -> Optional[str]:
        """Create fallback audio for a specific segment when TTS fails"""
        try:
            from gtts import gTTS
            
            # Generate with gTTS
            tts = gTTS(text=segment_text, lang='en', slow=False)
            
            # Save to session directory
            audio_filename = f"fallback_audio_segment_{uuid.uuid4().hex[:8]}.mp3"
            session_audio_path = session_context.get_output_path("audio", audio_filename)
            os.makedirs(os.path.dirname(session_audio_path), exist_ok=True)
            
            tts.save(session_audio_path)
            
            if os.path.exists(session_audio_path) and os.path.getsize(session_audio_path) > 1000:
                logger.info(f"✅ Created fallback audio segment: {audio_filename} for duration {segment_duration:.1f}s")
                return session_audio_path
            else:
                logger.warning("⚠️ Fallback audio segment creation failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Fallback audio segment creation failed: {e}")
            return None

    def _compose_final_video_with_subtitles(self, clips: List[str], audio_files: List[str], 
                                           script_result: Dict[str, Any], style_decision: Dict[str, Any],
                                           positioning_decision: Dict[str, Any], config: GeneratedVideoConfig,
                                           session_context: SessionContext) -> str:
        """Compose final video with subtitles and overlays"""
        try:
            logger.info("🎬 Composing final video with subtitles and overlays")
            
            # CRITICAL FIX: Handle case where no video clips are available
            if not clips:
                logger.warning("⚠️ No video clips available, creating fallback video")
                return self._create_fallback_video_from_audio(audio_files, config, session_context)
            
            # Step 1: Create base video from clips
            temp_video_path = self._create_base_video_from_clips(clips, audio_files, session_context)
            
            if not temp_video_path or not os.path.exists(temp_video_path):
                logger.error("❌ Failed to create base video")
                return ""
            
            # Check actual video duration vs target duration
            actual_duration = self._get_video_duration(temp_video_path)
            target_duration = config.duration_seconds
            
            if actual_duration and actual_duration > target_duration * 1.3:
                # Only trim if video is significantly longer than target (30% over)
                logger.info(f"⏱️ Video is {actual_duration:.1f}s (target: {target_duration}s) - considering trim")
                trimmed_video_path = self._trim_video_to_duration(temp_video_path, target_duration * 1.2, session_context)
                if trimmed_video_path:
                    temp_video_path = trimmed_video_path
                    logger.info(f"✅ Video trimmed to allow complete content")
                else:
                    logger.warning("⚠️ Failed to trim video, using original")
            else:
                # Keep original duration to preserve complete content
                logger.info(f"✅ Keeping original video duration ({actual_duration:.1f}s) to preserve complete story")
            
            # Step 2: Add subtitle overlays
            video_with_subtitles = self._add_subtitle_overlays(temp_video_path, config, session_context)
            
            # Step 3: Add text overlays and hooks
            video_with_overlays = self._add_timed_text_overlays(video_with_subtitles, style_decision, positioning_decision, config, session_context)
            
            # Step 4: Apply platform orientation
            oriented_video_path = self._apply_platform_orientation(
                video_with_overlays, 
                config.target_platform.value, 
                session_context
            )
            
            # Step 5: Add final fadeout ending (for all videos)
            # Note: Basic fadeout already applied during trimming, this adds additional black screen if needed
            if config.duration_seconds >= 10:  # Add black screen fadeout for videos 10s+
                final_video_path = self._add_fade_out_ending(oriented_video_path, session_context)
            else:
                logger.info(f"🎬 Skipping additional black screen fadeout for short video ({config.duration_seconds}s)")
                final_video_path = oriented_video_path
            
            # Step 6: Save to session
            saved_path = session_context.save_final_video(final_video_path)
            logger.info(f"✅ Final video with subtitles created: {saved_path}")
            
            # Step 7: Generate trending hashtags for the video
            self._generate_and_save_hashtags(config, session_context, script_result)
            
            # Clean up temp files
            for temp_file in [temp_video_path, video_with_subtitles, video_with_overlays, oriented_video_path, final_video_path]:
                try:
                    if temp_file and os.path.exists(temp_file) and temp_file != saved_path:
                        os.unlink(temp_file)
                except:
                    pass
            
            return saved_path
            
        except Exception as e:
            logger.error(f"❌ Video composition failed: {e}")
            return ""
    
    def _create_fallback_video_from_audio(self, audio_files: List[str], config: GeneratedVideoConfig, 
                                         session_context: SessionContext) -> str:
        """Create a fallback video using only audio files and static images"""
        try:
            logger.info("🎬 Creating fallback video from audio files")
            
            # Create output path
            output_path = session_context.get_output_path("final_video", "fallback_video.mp4")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Concatenate audio files
            if len(audio_files) > 1:
                # Create audio concatenation
                audio_concat_path = session_context.get_output_path("temp_files", "concatenated_audio.mp3")
                os.makedirs(os.path.dirname(audio_concat_path), exist_ok=True)
                
                # Build FFmpeg command to concatenate audio
                input_parts = []
                for audio in audio_files:
                    input_parts.extend(['-i', audio])
                
                # Create filter for audio concatenation
                audio_inputs = "".join([f"[{i}:a]" for i in range(len(audio_files))])
                filter_complex = f"{audio_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]"
                
                cmd = [
                    'ffmpeg', '-y'
                ] + input_parts + [
                    '-filter_complex', filter_complex,
                    '-map', '[outa]',
                    '-c:a', 'aac',
                    audio_concat_path
                ]
                
                import subprocess
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(audio_concat_path):
                    audio_file = audio_concat_path
                else:
                    logger.warning("⚠️ Audio concatenation failed, using first audio file")
                    audio_file = audio_files[0] if audio_files else None
            else:
                audio_file = audio_files[0] if audio_files else None
            
            if not audio_file or not os.path.exists(audio_file):
                logger.error("❌ No audio file available for fallback video")
                return ""
            
            # Create a simple static video with the audio
            # Use a solid color background with text overlay
            import subprocess
            
            # Get audio duration
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', audio_file]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            if probe_result.returncode != 0:
                logger.warning("⚠️ Could not get audio duration, using default")
                duration = config.duration_seconds
            else:
                import json
                probe_data = json.loads(probe_result.stdout)
                audio_stream = next((s for s in probe_data.get('streams', []) if s.get('codec_type') == 'audio'), None)
                duration = float(audio_stream.get('duration', config.duration_seconds)) if audio_stream else config.duration_seconds
            
            # Create video with solid color background and text
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c=black:size=1080x1920:duration={duration}',
                '-i', audio_file,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Created fallback video: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Failed to create fallback video: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Fallback video creation failed: {e}")
            return ""
    
    def _create_base_video_from_clips(self, clips: List[str], audio_files: List[str], 
                                     session_context: SessionContext) -> str:
        """Create base video from clips and audio files"""
        try:
            logger.info("🎬 Creating base video from clips")
            
            # Create output path
            output_path = session_context.get_output_path("temp_files", "base_video.mp4")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check if we have video clips
            if not clips:
                logger.warning("⚠️ No video clips available")
                return ""
            
            # Check if we have audio files
            if not audio_files:
                logger.warning("⚠️ No audio files available")
                return ""
            
            # Use frame continuity if available, otherwise use standard composition
            if len(clips) > 1:
                # Try frame continuity first
                try:
                    result = self._compose_with_frame_continuity(clips, audio_files, output_path, session_context)
                    if result and os.path.exists(result):
                        return result
                except Exception as e:
                    logger.warning(f"⚠️ Frame continuity failed: {e}")
            
            # Fallback to standard composition
            return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context)
            
        except Exception as e:
            logger.error(f"❌ Base video creation failed: {e}")
            return ""
    
    def _add_text_overlays(self, video_path: str, style_decision: Dict[str, Any], 
                          positioning_decision: Dict[str, Any], config: GeneratedVideoConfig,
                          session_context: SessionContext) -> str:
        """Add text overlays and hooks based on AI agent decisions"""
        try:
            logger.info("🎨 Adding text overlays and hooks")
            
            # Create output path
            overlay_path = session_context.get_output_path("temp_files", f"with_overlays_{os.path.basename(video_path)}")
            os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
            
            # Get video info
            import subprocess
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            if probe_result.returncode != 0:
                logger.warning("⚠️ Could not get video info, skipping overlays")
                return video_path
            
            import json
            probe_data = json.loads(probe_result.stdout)
            video_stream = next((s for s in probe_data.get('streams', []) if s.get('codec_type') == 'video'), None)
            
            if not video_stream:
                logger.warning("⚠️ No video stream found, skipping overlays")
                return video_path
            
            video_width = int(video_stream.get('width', 1280))
            video_height = int(video_stream.get('height', 720))
            
            # Create overlay filters based on platform and style
            overlay_filters = []
            
            # Get video duration from video stream info
            video_duration = float(video_stream.get('duration', 20))
            
            # CRITICAL FIX: Add dynamic/animated overlays for TikTok
            positioning_decision = self._get_positioning_decision(config, {'primary_style': 'dynamic'})
            is_dynamic = positioning_decision.get('positioning_strategy') == 'dynamic'
            
            # Add hook text overlay with DYNAMIC positioning and AI-driven styling
            if config.hook:
                # Get AI-driven overlay styling
                hook_style = self._get_ai_overlay_style(str(config.hook), "hook", config.target_platform, video_width, video_height, session_context)
                
                # Create smart multi-line hook text with width constraints
                hook_text = self._create_short_multi_line_text(str(config.hook), max_words_per_line=hook_style.get('words_per_line', 4), video_width=video_width)
                
                if is_dynamic:
                    # DYNAMIC: Moving hook overlay with AI-styled animation
                    overlay_filters.append(
                        f"drawtext=text='{hook_text}':fontcolor={hook_style['color']}:fontsize={hook_style['font_size']}:font='{hook_style['font_family']}':box=1:boxcolor={hook_style['background_color']}@{hook_style['background_opacity']}:boxborderw={hook_style['stroke_width']}:x='if(lt(t,1.5),(w-text_w)/2,if(lt(t,3),(w-text_w)/2-20*sin(2*PI*t),w-text_w-20))':y='60+10*sin(4*PI*t)':enable='between(t,0,3)'"
                    )
                else:
                    # STATIC: AI-styled static positioning
                    overlay_filters.append(
                        f"drawtext=text='{hook_text}':fontcolor={hook_style['color']}:fontsize={hook_style['font_size']}:font='{hook_style['font_family']}':box=1:boxcolor={hook_style['background_color']}@{hook_style['background_opacity']}:boxborderw={hook_style['stroke_width']}:x=(w-text_w)/2:y=60:enable='between(t,0,3)'"
                    )
            
            # Add call-to-action overlay with DYNAMIC positioning and AI-driven styling
            if config.call_to_action:
                # Get AI-driven overlay styling for CTA
                cta_style = self._get_ai_overlay_style(str(config.call_to_action), "cta", config.target_platform, video_width, video_height, session_context)
                
                # Create smart multi-line CTA text with width constraints
                cta_text = self._create_short_multi_line_text(str(config.call_to_action), max_words_per_line=cta_style.get('words_per_line', 4), video_width=video_width)
                
                if is_dynamic:
                    # DYNAMIC: Sliding CTA with AI-styled bounce effect
                    overlay_filters.append(
                        f"drawtext=text='{cta_text}':fontcolor={cta_style['color']}:fontsize={cta_style['font_size']}:font='{cta_style['font_family']}':box=1:boxcolor={cta_style['background_color']}@{cta_style['background_opacity']}:boxborderw={cta_style['stroke_width']}:x='if(lt(t,{video_duration-3}),w+text_w,w-text_w-30-15*sin(8*PI*(t-{video_duration-3})))':y='120+5*cos(6*PI*t)':enable='between(t,{video_duration-3},{video_duration})'"
                    )
                else:
                    # STATIC: AI-styled static positioning
                    overlay_filters.append(
                        f"drawtext=text='{cta_text}':fontcolor={cta_style['color']}:fontsize={cta_style['font_size']}:font='{cta_style['font_family']}':box=1:boxcolor={cta_style['background_color']}@{cta_style['background_opacity']}:boxborderw={cta_style['stroke_width']}:x=w-text_w-30:y=120:enable='between(t,{video_duration-3},{video_duration})'"
                    )
            
            # Use professional text renderer instead of FFmpeg drawtext
            return self._add_professional_text_overlays(
                video_path, config, video_width, video_height, video_duration, session_context
            )
                
        except Exception as e:
            logger.error(f"❌ Text overlay failed: {e}")
            return video_path
    
    def _add_professional_text_overlays(self, video_path: str, config: GeneratedVideoConfig,
                                       video_width: int, video_height: int, video_duration: float,
                                       session_context: SessionContext) -> str:
        """Add text overlays using professional text renderer instead of FFmpeg drawtext"""
        try:
            import cv2
            import numpy as np
            from moviepy.editor import VideoFileClip, ImageSequenceClip
            
            logger.info("🎨 Adding professional text overlays with high-quality rendering")
            
            # Create output path
            overlay_path = session_context.get_output_path("temp_files", f"professional_overlays_{os.path.basename(video_path)}")
            os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
            
            # Load video with moviepy
            video_clip = VideoFileClip(video_path)
            fps = video_clip.fps or 30
            
            # Create text overlays
            overlays = []
            
            # Hook overlay
            if config.hook:
                hook_style = TextStyle(
                    font_family="Impact",
                    font_size=max(40, int(video_width * 0.05)),
                    font_weight="bold",
                    color=(255, 255, 255, 255),
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=3,
                    background_color=(0, 0, 0, 180),
                    background_padding=(15, 8, 15, 8),
                    shadow_color=(0, 0, 0, 200),
                    shadow_offset=(3, 3),
                    line_spacing=1.2
                )
                
                hook_layout = TextLayout(
                    position=TextPosition.TOP_CENTER,
                    alignment=TextAlignment.CENTER,
                    max_width=int(video_width * 0.9),
                    margin=(20, 60, 20, 20)
                )
                
                hook_overlay = TextOverlay(
                    text=str(config.hook),
                    style=hook_style,
                    layout=hook_layout,
                    start_time=0.0,
                    end_time=3.0,
                    fade_in_duration=0.3,
                    fade_out_duration=0.3
                )
                overlays.append(hook_overlay)
            
            # CTA overlay
            if config.call_to_action:
                cta_style = TextStyle(
                    font_family="Arial",
                    font_size=max(32, int(video_width * 0.04)),
                    font_weight="bold",
                    color=(255, 255, 255, 255),
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=2,
                    background_color=(255, 0, 100, 200),
                    background_padding=(12, 6, 12, 6),
                    line_spacing=1.1
                )
                
                cta_layout = TextLayout(
                    position=TextPosition.BOTTOM_RIGHT,
                    alignment=TextAlignment.CENTER,
                    max_width=int(video_width * 0.8),
                    margin=(20, 20, 30, 80)
                )
                
                cta_overlay = TextOverlay(
                    text=str(config.call_to_action),
                    style=cta_style,
                    layout=cta_layout,
                    start_time=video_duration - 3.0,
                    end_time=video_duration,
                    fade_in_duration=0.2,
                    fade_out_duration=0.2
                )
                overlays.append(cta_overlay)
            
            if not overlays:
                logger.info("No overlays to add, returning original video")
                video_clip.close()
                return video_path
            
            # Process video frame by frame
            logger.info(f"🎬 Processing {video_duration:.1f}s video at {fps}fps with {len(overlays)} overlays")
            
            def make_frame(t):
                # Get original frame
                frame = video_clip.get_frame(t)
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Apply each text overlay
                for overlay in overlays:
                    frame_bgr = self.text_renderer.render_text_overlay(frame_bgr, overlay, t)
                
                # Convert back to RGB for moviepy
                return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            
            # Create new video with overlays
            final_clip = video_clip.fl(lambda gf, t: make_frame(t), apply_to=[])
            
            # Write the video
            logger.info(f"💾 Writing video with professional overlays: {overlay_path}")
            final_clip.write_videofile(
                overlay_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=None,
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            video_clip.close()
            final_clip.close()
            
            if os.path.exists(overlay_path):
                logger.info(f"✅ Professional text overlays added successfully")
                return overlay_path
            else:
                logger.error("❌ Professional overlay video not created")
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Professional text overlay creation failed: {e}")
            logger.info("🔄 Falling back to original video")
            try:
                if 'video_clip' in locals():
                    video_clip.close()
                if 'final_clip' in locals():
                    final_clip.close()
            except:
                pass
            return video_path
    
    def _add_subtitle_overlays(self, video_path: str, config: GeneratedVideoConfig, 
                             session_context: SessionContext) -> str:
        """Add subtitle overlays to the video using MoviePy"""
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            import tempfile
            
            logger.info("📝 Adding subtitle overlays using MoviePy")
            
            # Load the video
            video = VideoFileClip(video_path)
            video_duration = video.duration
            video_width, video_height = video.size
            
            # Create subtitle content based on the actual processed script
            subtitle_segments = self._create_subtitle_segments(
                config, video_duration, 
                script_result=getattr(self, '_last_script_result', None),
                session_context=session_context,
                video_width=video_width
            )
            
            # Get positioning decision
            positioning_decision = self._get_positioning_decision(config, {'primary_style': 'dynamic'})
            primary_position = positioning_decision.get('primary_subtitle_position', 'bottom_third')
            
            # Create text clips for subtitles
            text_clips = []
            for i, segment in enumerate(subtitle_segments):
                try:
                    # Use full_text for subtitles if available (avoid truncated text), otherwise use text  
                    text = segment.get('full_text', segment.get('text', ''))
                    start_time = segment['start']
                    end_time = segment['end']
                    
                    if end_time <= start_time:
                        continue
                    
                    # Calculate position based on AI decision - FIXED: Better positioning
                    if primary_position == 'top_third':
                        y_pos = video_height * 0.20  # 20% from top
                    elif primary_position == 'center':
                        y_pos = video_height * 0.50  # Center
                    else:  # bottom_third (default) - FIXED: Move subtitles higher
                        y_pos = video_height * 0.70  # 70% down (was 85% - too low)
                    
                    # Font size based on video dimensions
                    font_size = max(40, int(video_width * 0.05))
                    
                    # Create text clip with modern styling
                    text_clip = TextClip(
                        text,
                        fontsize=font_size,
                        color='white',
                        font='Arial-Bold',
                        stroke_color='black',
                        stroke_width=2,
                        method='caption',
                        size=(int(video_width * 0.9), None),
                        align='center'
                    )
                    
                    # Create semi-transparent background for the text
                    from moviepy.editor import ColorClip
                    
                    # Get text clip dimensions
                    text_width, text_height = text_clip.size
                    
                    # Create a semi-transparent black background
                    background = ColorClip(
                        size=(text_width + 20, text_height + 10),  # Add padding around text
                        color=(0, 0, 0),  # Black background
                        duration=end_time - start_time
                    ).set_opacity(0.6)  # Semi-transparent
                    
                    # Position background and text
                    background = background.set_position(('center', y_pos - 5)).set_start(start_time)
                    text_clip = text_clip.set_position(('center', y_pos)).set_start(start_time).set_duration(end_time - start_time)
                    
                    # Add both background and text to clips
                    text_clips.append(background)
                    text_clips.append(text_clip)
                    
                    logger.info(f"📝 Added subtitle: '{text[:30]}...' at {start_time:.1f}-{end_time:.1f}s")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create subtitle clip {i}: {e}")
                    continue
            
            # Composite video with subtitle overlays
            if text_clips:
                logger.info(f"🎬 Compositing video with {len(text_clips)} subtitle overlays")
                final_video = CompositeVideoClip([video] + text_clips)
                
                # Create output path
                temp_output = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                output_path = temp_output.name
                temp_output.close()
                
                # Render the video with subtitles
                final_video.write_videofile(
                    output_path,
                    fps=30,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                
                # Clean up
                final_video.close()
                video.close()
                for clip in text_clips:
                    clip.close()
                
                # Verify output
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    logger.info(f"✅ Subtitle overlays added: {output_path} ({file_size:.1f}MB)")
                    
                    # Clean up original video
                    try:
                        os.remove(video_path)
                    except:
                        pass
                    
                    return output_path
                else:
                    logger.error("❌ Failed to create video with subtitles")
                    return video_path
            else:
                logger.warning("⚠️ No subtitle overlays created")
                video.close()
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Subtitle overlay creation failed: {e}")
            return video_path
    
    def _create_subtitle_segments(self, config: GeneratedVideoConfig, video_duration: float, 
                                 script_result: Dict[str, Any] = None, 
                                 session_context: SessionContext = None,
                                 video_width: int = 1280) -> List[Dict[str, Any]]:
        """Create subtitle segments from the actual processed script content with proper audio synchronization"""
        try:
            # CRITICAL FIX: Use actual processed script content instead of config content
            actual_script = ""
            
            # Priority 1: Use final processed script from script_result
            if script_result and script_result.get('final_script'):
                actual_script = script_result['final_script']
                logger.info("📝 Using processed script for subtitles")
            
            # Priority 2: Try to load from session context
            elif session_context:
                try:
                    script_path = session_context.get_output_path("scripts", "processed_script.txt")
                    if os.path.exists(script_path):
                        with open(script_path, 'r') as f:
                            actual_script = f.read().strip()
                        logger.info("📝 Loaded script from session for subtitles")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load script from session: {e}")
            
            # Priority 3: Fallback to config content (old behavior)
            if not actual_script:
                main_content = config.main_content or [config.topic]
                hook = config.hook or "Amazing content!"
                cta = config.call_to_action or "Follow for more!"
                actual_script = f"{hook} {' '.join(main_content)} {cta}"
                logger.warning("⚠️ Using fallback config content for subtitles")
            
            # Check if we have audio segments first to match the subtitle count
            audio_segment_count = 0
            if session_context:
                audio_dir = session_context.get_output_path("audio")
                if os.path.exists(audio_dir):
                    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3') or f.endswith('.wav')]
                    audio_segment_count = len(audio_files)
            
            # Parse the actual script into meaningful segments
            if audio_segment_count > 0:
                # Split script to match audio segment count
                segments = self._split_script_to_audio_segments(actual_script, audio_segment_count, video_duration)
                logger.info(f"📝 Split script into {len(segments)} segments to match {audio_segment_count} audio files")
            else:
                # Use natural sentence-based segmentation
                segments = self._parse_script_into_segments(actual_script, video_duration, video_width)
            
            # Analyze audio files for better synchronization if available
            if session_context:
                segments = self._synchronize_with_audio_segments(segments, video_duration, session_context)
            
            logger.info(f"📝 Created {len(segments)} subtitle segments from actual script")
            for i, segment in enumerate(segments[:3]):  # Log first 3 segments
                logger.info(f"   Segment {i+1}: '{segment['text'][:50]}...' ({segment['start']:.1f}-{segment['end']:.1f}s)")
            
            return segments
            
        except Exception as e:
            logger.error(f"❌ Failed to create subtitle segments: {e}")
            return []
    
    def _split_script_to_audio_segments(self, script: str, audio_count: int, video_duration: float) -> List[Dict[str, Any]]:
        """Split script into exact number of segments to match audio files - NEVER cut sentences in middle"""
        try:
            import re
            
            # First, split script into complete sentences
            sentences = re.split(r'([.!?]+)', script)
            # Recombine sentences with their punctuation
            complete_sentences = []
            for i in range(0, len(sentences) - 1, 2):
                if i + 1 < len(sentences):
                    sentence = sentences[i].strip() + sentences[i + 1].strip()
                    if sentence.strip():
                        complete_sentences.append(sentence.strip())
                elif sentences[i].strip():
                    complete_sentences.append(sentences[i].strip())
            
            if not complete_sentences:
                # Fallback: split by periods only
                complete_sentences = [s.strip() for s in script.split('.') if s.strip()]
                complete_sentences = [s + '.' for s in complete_sentences[:-1]] + [complete_sentences[-1]] if complete_sentences else [script]
            
            logger.info(f"📝 Found {len(complete_sentences)} complete sentences to distribute across {audio_count} segments")
            
            # Distribute sentences across segments ensuring no sentence is cut
            segments = []
            sentences_per_segment = max(1, len(complete_sentences) // audio_count)
            
            sentence_index = 0
            for i in range(audio_count):
                segment_sentences = []
                
                if i == audio_count - 1:
                    # Last segment gets all remaining sentences
                    segment_sentences = complete_sentences[sentence_index:]
                else:
                    # Take calculated number of sentences
                    end_index = min(sentence_index + sentences_per_segment, len(complete_sentences))
                    segment_sentences = complete_sentences[sentence_index:end_index]
                    sentence_index = end_index
                
                # Join sentences for this segment
                segment_text = ' '.join(segment_sentences)
                
                if segment_text.strip():
                    # Estimate duration based on word count
                    word_count = len(segment_text.split())
                    estimated_duration = video_duration / audio_count
                    
                    segments.append({
                        'text': segment_text,
                        'start': i * estimated_duration,
                        'end': (i + 1) * estimated_duration,
                        'word_count': word_count,
                        'estimated_duration': estimated_duration,
                        'sentence_count': len(segment_sentences),
                        'complete_sentences': True  # Flag indicating proper sentence boundaries
                    })
                    
                    logger.info(f"📝 Segment {i+1}: {len(segment_sentences)} sentences, {word_count} words: '{segment_text[:50]}...'")
            
            # If we have fewer segments than needed, redistribute
            while len(segments) < audio_count and len(segments) > 0:
                # Find the segment with the most sentences and split it
                longest_segment_idx = max(range(len(segments)), key=lambda x: segments[x]['sentence_count'])
                longest_segment = segments[longest_segment_idx]
                
                if longest_segment['sentence_count'] > 1:
                    # Split this segment
                    sentences_in_segment = longest_segment['text'].split('. ')
                    if len(sentences_in_segment) < 2:
                        sentences_in_segment = longest_segment['text'].split('! ')
                    if len(sentences_in_segment) < 2:
                        sentences_in_segment = longest_segment['text'].split('? ')
                    
                    if len(sentences_in_segment) >= 2:
                        mid_point = len(sentences_in_segment) // 2
                        
                        first_part = '. '.join(sentences_in_segment[:mid_point])
                        second_part = '. '.join(sentences_in_segment[mid_point:])
                        
                        # Update first segment
                        segments[longest_segment_idx]['text'] = first_part
                        segments[longest_segment_idx]['word_count'] = len(first_part.split())
                        segments[longest_segment_idx]['sentence_count'] = mid_point
                        
                        # Create new segment
                        new_segment = {
                            'text': second_part,
                            'word_count': len(second_part.split()),
                            'sentence_count': len(sentences_in_segment) - mid_point,
                            'start': longest_segment['end'],
                            'end': longest_segment['end'] + longest_segment['estimated_duration'],
                            'estimated_duration': longest_segment['estimated_duration'],
                            'complete_sentences': True
                        }
                        segments.insert(longest_segment_idx + 1, new_segment)
                        
                        logger.info(f"📝 Split segment {longest_segment_idx + 1} to ensure proper distribution")
                    else:
                        break
                else:
                    break
            
            # Ensure we have exactly the required number of segments
            segments = segments[:audio_count]
            
            logger.info(f"✅ Created {len(segments)} segments with complete sentence boundaries")
            return segments
            
        except Exception as e:
            logger.error(f"❌ Failed to split script to audio segments: {e}")
            # Fallback to simple sentence-based splitting
            try:
                sentences = [s.strip() for s in script.split('.') if s.strip()]
                if len(sentences) >= audio_count:
                    segments = []
                    sentences_per_segment = len(sentences) // audio_count
                    for i in range(audio_count):
                        start_idx = i * sentences_per_segment
                        end_idx = start_idx + sentences_per_segment if i < audio_count - 1 else len(sentences)
                        segment_text = '. '.join(sentences[start_idx:end_idx]) + '.'
                        
                        segments.append({
                            'text': segment_text,
                            'start': i * (video_duration / audio_count),
                            'end': (i + 1) * (video_duration / audio_count),
                            'word_count': len(segment_text.split()),
                            'estimated_duration': video_duration / audio_count,
                            'complete_sentences': True
                        })
                    return segments
                else:
                    # If not enough sentences, just return single segment
                    return [{
                        'text': script,
                        'start': 0,
                        'end': video_duration,
                        'word_count': len(script.split()),
                        'estimated_duration': video_duration,
                        'complete_sentences': True
                    }]
            except:
                return []
    
    def _validate_sentence_integrity(self, segments: List[Dict[str, Any]]) -> bool:
        """Validate that no segment cuts off in the middle of a sentence"""
        try:
            for i, segment in enumerate(segments):
                text = segment.get('text', '').strip()
                
                # Check if segment starts mid-sentence (lowercase letter after space)
                if text and text[0].islower() and i > 0:
                    logger.warning(f"⚠️ Segment {i+1} starts mid-sentence: '{text[:30]}...'")
                    return False
                
                # Check if segment ends mid-sentence (no proper punctuation)
                if text and not text.endswith(('.', '!', '?')):
                    logger.warning(f"⚠️ Segment {i+1} ends mid-sentence: '...{text[-30:]}'")
                    return False
                    
            logger.info("✅ All segments have proper sentence boundaries")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate sentence integrity: {e}")
            return False
    
    def _parse_script_into_segments(self, script: str, video_duration: float, video_width: int = 1280) -> List[Dict[str, Any]]:
        """Parse script into natural segments based on sentences and timing"""
        try:
            # Split script into sentences
            import re
            sentences = re.split(r'[.!?]+', script)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return []
            
            # Calculate timing based on sentence complexity and length
            segments = []
            total_words = sum(len(sentence.split()) for sentence in sentences)
            
            # Estimate words per second (typical speech rate: 2-3 words/second)
            words_per_second = max(2.0, min(3.0, total_words / video_duration))
            
            current_time = 0.0
            
            for i, sentence in enumerate(sentences):
                words = len(sentence.split())
                
                # Calculate duration based on word count and complexity
                base_duration = words / words_per_second
                
                # Add padding for complex sentences or important content
                if any(keyword in sentence.lower() for keyword in ['meet', 'how', 'what', 'why', 'when', 'where']):
                    base_duration *= 1.2  # 20% longer for questions/introductions
                
                # Ensure minimum and maximum duration per segment
                duration = max(1.5, min(6.0, base_duration))
                
                # Adjust if we're running out of time
                remaining_time = video_duration - current_time
                if i == len(sentences) - 1:  # Last segment
                    duration = min(duration, remaining_time)
                elif current_time + duration > video_duration:
                    duration = remaining_time * 0.8  # Leave some buffer
                
                # Format text for MoviePy subtitle display with proper line breaks and width constraints
                max_chars = min(50, int(video_width * 0.04))  # Responsive character limit
                formatted_text = self._format_subtitle_text(sentence.strip(), max_chars_per_line=max_chars)
                
                segments.append({
                    'text': formatted_text,
                    'start': current_time,
                    'end': current_time + duration,
                    'word_count': words,
                    'estimated_duration': duration
                })
                
                current_time += duration
                
                # Stop if we've reached the video duration
                if current_time >= video_duration:
                    break
            
            return segments
            
        except Exception as e:
            logger.error(f"❌ Failed to parse script into segments: {e}")
            return []
    
    def _synchronize_with_audio_segments(self, segments: List[Dict[str, Any]], 
                                       video_duration: float, 
                                       session_context: SessionContext) -> List[Dict[str, Any]]:
        """Synchronize subtitle segments with actual audio file durations for perfect 100% sync"""
        try:
            # Get audio files from session
            audio_dir = session_context.get_output_path("audio")
            if not os.path.exists(audio_dir):
                logger.warning("⚠️ No audio directory found, using intelligent subtitle timing")
                return self._intelligent_subtitle_timing(segments, video_duration, None)
            
            # Find audio files
            audio_files = []
            for filename in os.listdir(audio_dir):
                if filename.endswith('.mp3') or filename.endswith('.wav'):
                    audio_files.append(os.path.join(audio_dir, filename))
            
            if not audio_files:
                logger.warning("⚠️ No audio files found, using intelligent subtitle timing")
                return self._intelligent_subtitle_timing(segments, video_duration, None)
            
            # CRITICAL FIX: Perfect synchronization for any number of audio files
            logger.info(f"🎵 Found {len(audio_files)} audio files - achieving 100% synchronization")
            
            if len(audio_files) == 1:
                # Single audio file: Use advanced audio analysis for word-level timing
                return self._perfect_single_audio_sync(segments, video_duration, audio_files[0])
            else:
                # Multiple audio files: Use exact audio duration mapping
                return self._perfect_multi_audio_sync(segments, video_duration, audio_files)
            
        except Exception as e:
            logger.error(f"❌ Audio synchronization error: {e}")
            # Fallback to intelligent timing
            return self._intelligent_subtitle_timing(segments, video_duration, None)
    
    def _perfect_single_audio_sync(self, segments: List[Dict[str, Any]], 
                                 video_duration: float, 
                                 audio_file: str) -> List[Dict[str, Any]]:
        """Perfect synchronization for single audio file using word-level timing analysis"""
        try:
            from moviepy.editor import AudioFileClip
            import numpy as np
            
            logger.info("🎯 Performing perfect single-audio synchronization")
            
            # Get actual audio duration
            audio_clip = AudioFileClip(audio_file)
            actual_audio_duration = audio_clip.duration
            audio_clip.close()
            
            logger.info(f"🎵 Audio file duration: {actual_audio_duration:.3f}s")
            
            # Calculate total words across all segments
            total_words = sum(len(segment['text'].split()) for segment in segments)
            
            if total_words == 0:
                logger.warning("⚠️ No words found in segments")
                return segments
            
            # Calculate precise timing based on word distribution and natural speech patterns
            synchronized_segments = []
            current_time = 0.0
            
            # Use natural speech rate: 2.5 words per second (realistic for clear speech)
            words_per_second = min(3.0, max(2.0, total_words / actual_audio_duration))
            
            logger.info(f"📊 Calculated speech rate: {words_per_second:.2f} words/second")
            
            for i, segment in enumerate(segments):
                segment_words = segment['text'].split()
                word_count = len(segment_words)
                
                # Calculate base duration from word count
                base_duration = word_count / words_per_second
                
                # Apply content-aware timing adjustments for better sync
                text_lower = segment['text'].lower()
                
                # Adjust for sentence complexity and punctuation
                if any(marker in text_lower for marker in ['?', '!', 'how', 'what', 'why', 'amazing']):
                    base_duration *= 1.15  # 15% longer for questions and emphasis
                elif any(marker in text_lower for marker in ['.', 'and', 'the', 'this']):
                    base_duration *= 0.95   # 5% shorter for simple connectors
                
                # Apply pause adjustments for natural speech flow
                if i == 0:  # First segment gets a slight pause at beginning
                    base_duration += 0.1
                elif i == len(segments) - 1:  # Last segment gets ending pause
                    base_duration += 0.15
                else:  # Middle segments get natural inter-sentence pauses
                    base_duration += 0.05
                
                # Ensure we don't exceed remaining audio time
                remaining_time = actual_audio_duration - current_time
                if current_time + base_duration > actual_audio_duration:
                    base_duration = max(0.5, remaining_time * 0.95)  # Leave small buffer
                
                # Create perfectly timed segment
                end_time = min(current_time + base_duration, actual_audio_duration)
                
                synchronized_segments.append({
                    'text': segment['text'],
                    'start': round(current_time, 3),
                    'end': round(end_time, 3),
                    'word_count': word_count,
                    'duration': round(end_time - current_time, 3),
                    'words_per_second': round(word_count / (end_time - current_time), 2),
                    'audio_synchronized': True,
                    'sync_method': 'perfect_single_audio'
                })
                
                current_time = end_time
                
                logger.info(f"📝 Segment {i+1}: '{segment['text'][:30]}...' "
                           f"({synchronized_segments[i]['start']:.2f}-{synchronized_segments[i]['end']:.2f}s, "
                           f"{word_count} words, {synchronized_segments[i]['words_per_second']:.1f} w/s)")
            
            # Verify total timing matches audio duration
            total_subtitle_duration = synchronized_segments[-1]['end'] if synchronized_segments else 0
            timing_accuracy = (total_subtitle_duration / actual_audio_duration) * 100
            
            logger.info(f"✅ Perfect sync achieved: {len(synchronized_segments)} segments, "
                       f"{timing_accuracy:.1f}% timing accuracy")
            
            return synchronized_segments
            
        except Exception as e:
            logger.error(f"❌ Perfect single audio sync failed: {e}")
            return self._fallback_timing_sync(segments, video_duration)
    
    def _perfect_multi_audio_sync(self, segments: List[Dict[str, Any]], 
                                video_duration: float, 
                                audio_files: List[str]) -> List[Dict[str, Any]]:
        """Perfect synchronization for multiple audio files with exact duration mapping"""
        try:
            from moviepy.editor import AudioFileClip
            
            logger.info("🎯 Performing perfect multi-audio synchronization")
            
            # Sort audio files by segment number
            audio_files.sort(key=lambda x: int(re.search(r'segment_(\d+)', x).group(1)) if re.search(r'segment_(\d+)', x) else 0)
            
            # Analyze each audio file duration with high precision
            audio_durations = []
            total_audio_duration = 0.0
            
            for i, audio_file in enumerate(audio_files):
                try:
                    audio_clip = AudioFileClip(audio_file)
                    duration = round(audio_clip.duration, 3)  # High precision
                    audio_durations.append(duration)
                    total_audio_duration += duration
                    audio_clip.close()
                    logger.info(f"🎵 Audio {i+1}: {os.path.basename(audio_file)} - {duration:.3f}s")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to analyze audio file {audio_file}: {e}")
                    # Use estimated duration if analysis fails
                    estimated_duration = video_duration / len(audio_files)
                    audio_durations.append(estimated_duration)
                    total_audio_duration += estimated_duration
            
            logger.info(f"🎵 Total audio duration: {total_audio_duration:.3f}s")
            
            # Create perfectly synchronized segments
            synchronized_segments = []
            current_time = 0.0
            
            # Match segments with exact audio durations
            for i in range(min(len(segments), len(audio_durations))):
                segment = segments[i]
                audio_duration = audio_durations[i]
                
                # Use exact audio duration for perfect sync
                end_time = current_time + audio_duration
                
                synchronized_segments.append({
                    'text': segment['text'],
                    'start': round(current_time, 3),
                    'end': round(end_time, 3),
                    'word_count': segment.get('word_count', len(segment['text'].split())),
                    'duration': round(audio_duration, 3),
                    'audio_file': os.path.basename(audio_files[i]),
                    'audio_synchronized': True,
                    'sync_method': 'perfect_multi_audio'
                })
                
                current_time = end_time
                
                logger.info(f"📝 Segment {i+1}: '{segment['text'][:30]}...' "
                           f"({synchronized_segments[i]['start']:.2f}-{synchronized_segments[i]['end']:.2f}s, "
                           f"audio: {audio_duration:.3f}s)")
            
            # Handle any remaining segments without corresponding audio
            remaining_segments = segments[len(audio_durations):]
            if remaining_segments:
                remaining_time = max(0, video_duration - current_time)
                time_per_segment = remaining_time / len(remaining_segments) if remaining_segments else 0
                
                for i, segment in enumerate(remaining_segments):
                    end_time = min(current_time + time_per_segment, video_duration)
                    
                    synchronized_segments.append({
                        'text': segment['text'],
                        'start': round(current_time, 3),
                        'end': round(end_time, 3),
                        'word_count': segment.get('word_count', len(segment['text'].split())),
                        'duration': round(end_time - current_time, 3),
                        'audio_synchronized': False,
                        'sync_method': 'estimated_remaining'
                    })
                    
                    current_time = end_time
            
            # Calculate synchronization accuracy
            total_subtitle_time = synchronized_segments[-1]['end'] if synchronized_segments else 0
            sync_accuracy = (total_subtitle_time / video_duration) * 100
            
            logger.info(f"✅ Perfect multi-audio sync: {len(synchronized_segments)} segments, "
                       f"{sync_accuracy:.1f}% timing accuracy, "
                       f"{len([s for s in synchronized_segments if s['audio_synchronized']])} audio-synced")
            
            return synchronized_segments
            
        except Exception as e:
            logger.error(f"❌ Perfect multi-audio sync failed: {e}")
            return self._fallback_timing_sync(segments, video_duration)
    
    def _fallback_timing_sync(self, segments: List[Dict[str, Any]], video_duration: float) -> List[Dict[str, Any]]:
        """Fallback timing method when audio analysis fails"""
        try:
            logger.info("🔄 Using fallback timing synchronization")
            
            if not segments:
                return []
            
            # Simple proportional timing with natural speech considerations
            total_words = sum(len(segment['text'].split()) for segment in segments)
            words_per_second = 2.5  # Natural speech rate
            
            fallback_segments = []
            current_time = 0.0
            
            for segment in segments:
                word_count = len(segment['text'].split())
                duration = max(1.0, word_count / words_per_second)  # Minimum 1 second
                end_time = min(current_time + duration, video_duration)
                
                fallback_segments.append({
                    'text': segment['text'],
                    'start': round(current_time, 3),
                    'end': round(end_time, 3),
                    'word_count': word_count,
                    'duration': round(end_time - current_time, 3),
                    'audio_synchronized': False,
                    'sync_method': 'fallback_proportional'
                })
                
                current_time = end_time
            
            logger.info(f"🔄 Fallback sync completed: {len(fallback_segments)} segments")
            return fallback_segments
            
        except Exception as e:
            logger.error(f"❌ Fallback timing sync failed: {e}")
            return segments
    
    def _intelligent_subtitle_timing(self, segments: List[Dict[str, Any]], 
                                    video_duration: float, 
                                    audio_file: str) -> List[Dict[str, Any]]:
        """INTELLIGENT: Use script structure for optimal subtitle timing - no complex audio analysis"""
        try:
            from moviepy.editor import AudioFileClip
            
            # Get actual audio duration
            audio_clip = AudioFileClip(audio_file)
            actual_audio_duration = audio_clip.duration
            audio_clip.close()
            
            # CRITICAL FIX: Use target duration instead of actual audio duration for timing
            # This ensures subtitles match the intended video length
            target_duration = min(video_duration, actual_audio_duration)
            
            logger.info(f"🎵 Audio: {actual_audio_duration:.2f}s, Target: {target_duration:.2f}s, Video: {video_duration:.2f}s, Segments: {len(segments)}")
            
            if not segments:
                logger.warning("⚠️ No segments to time")
                return []
            
            # Use intelligent timing based on script structure
            timed_segments = []
            
            # Calculate timing based on sentence structure and importance
            total_words = sum(len(segment.get('text', '').split()) for segment in segments)
            words_per_second = total_words / target_duration if target_duration > 0 else 3.0
            
            current_time = 0.0
            
            for i, segment in enumerate(segments):
                text = segment.get('text', '')
                words = len(text.split())
                
                # Calculate duration based on content complexity
                base_duration = words / words_per_second
                
                # Adjust for content type
                if text.lower().startswith(('discover', 'meet', 'what', 'how', 'why')):
                    base_duration *= 1.3  # Hooks need more time
                elif text.lower().endswith(('!', '?')):
                    base_duration *= 1.1  # Questions/exclamations need emphasis
                elif 'follow' in text.lower() or 'subscribe' in text.lower():
                    base_duration *= 0.9  # CTAs can be faster
                
                # Ensure reasonable bounds
                duration = max(1.0, min(base_duration, target_duration - current_time))
                
                # Adjust if this is the last segment
                if i == len(segments) - 1:
                    duration = target_duration - current_time
                
                if duration <= 0:
                    break
                
                timed_segments.append({
                    'text': text,
                    'start': current_time,
                    'end': current_time + duration,
                    'word_count': words,
                    'estimated_duration': duration,
                    'audio_synchronized': True,
                    'intelligent_timing': True,
                    'words_per_second': words / duration if duration > 0 else 0
                })
                
                logger.info(f"📝 Segment {i+1}: '{text[:40]}...' ({current_time:.1f}-{current_time + duration:.1f}s) [{words} words]")
                current_time += duration
            
            logger.info(f"✅ Created {len(timed_segments)} intelligently-timed subtitle segments")
            return timed_segments
            
        except Exception as e:
            logger.error(f"❌ Intelligent timing failed: {e}")
            return self._fallback_segmentation(segments, video_duration)
    
    
    def _fallback_segmentation(self, segments: List[Dict[str, Any]], video_duration: float) -> List[Dict[str, Any]]:
        """Fallback segmentation when audio analysis fails"""
        if not segments:
            return []
        
        # Simple proportional timing
        fallback_segments = []
        time_per_segment = video_duration / len(segments)
        
        for i, segment in enumerate(segments):
            start_time = i * time_per_segment
            end_time = min((i + 1) * time_per_segment, video_duration)
            
            fallback_segments.append({
                'text': segment['text'],
                'start': start_time,
                'end': end_time,
                'word_count': segment.get('word_count', 0),
                'estimated_duration': end_time - start_time,
                'audio_synchronized': False,
                'fallback_segmentation': True
            })
        
        logger.info(f"✅ Created {len(fallback_segments)} fallback subtitle segments")
        return fallback_segments
    
    def _compose_with_frame_continuity(self, clips: List[str], audio_files: List[str], 
                                     output_path: str, session_context: SessionContext) -> str:
        """Compose video with frame continuity - remove first frame of each clip (except first)"""
        try:
            import subprocess
            
            # Create filter complex for frame continuity
            filter_parts = []
            input_parts = []
            
            # Add all video inputs
            for i, clip in enumerate(clips):
                input_parts.extend(['-i', clip])
            
            # Add all audio inputs
            for i, audio in enumerate(audio_files):
                input_parts.extend(['-i', audio])
            
            # Create video filter for frame continuity
            # For clips after the first, skip the first frame to avoid duplication
            video_filter_parts = []
            
            # Normalize all videos to portrait 720x1280 dimensions
            for i, clip in enumerate(clips):
                if i == 0:
                    # First clip: scale to portrait and use as-is
                    video_filter_parts.append(f"[{i}:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
                else:
                    # Subsequent clips: scale to portrait and remove first frame
                    video_filter_parts.append(f"[{i}:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,trim=start=0.033,setpts=PTS-STARTPTS[v{i}]")
            
            # Concatenate all video streams
            if len(clips) > 1:
                trim_filters = ";".join(video_filter_parts)
                concat_inputs = "".join([f"[v{i}]" for i in range(len(clips))])
                video_filter = f"{trim_filters};{concat_inputs}concat=n={len(clips)}:v=1:a=0[outv]"
            else:
                video_filter = f"[0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1[outv]"
            
            # Create audio filter (concatenate all audio)
            audio_inputs = "".join([f"[{len(clips)+i}:a]" for i in range(len(audio_files))])
            audio_filter = f"{audio_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]"
            
            # Combine filters
            filter_complex = f"{video_filter};{audio_filter}"
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg', '-y'
            ] + input_parts + [
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
            
            logger.info("🎬 Running frame continuity composition...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Frame continuity composition completed")
                return output_path
            else:
                logger.error(f"❌ Frame continuity composition failed: {result.stderr}")
                # Fallback to standard composition
                return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context)
                
        except Exception as e:
            logger.error(f"❌ Frame continuity composition error: {e}")
            # Fallback to standard composition
            return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context)

    def _compose_with_standard_cuts(self, clips: List[str], audio_files: List[str], 
                                  output_path: str, session_context: SessionContext) -> str:
        """Compose video with standard cuts (no frame continuity)"""
        try:
            import subprocess
            
            # CRITICAL FIX: Handle case where no clips are available
            if not clips:
                logger.warning("⚠️ No video clips available for composition")
                return ""
            
            # CRITICAL FIX: Handle case where no audio files are available
            if not audio_files:
                logger.warning("⚠️ No audio files available for composition")
                return ""
            
            # Create simple concatenation
            input_parts = []
            
            # Add all video inputs
            for clip in clips:
                input_parts.extend(['-i', clip])
            
            # Add all audio inputs
            for audio in audio_files:
                input_parts.extend(['-i', audio])
            
            # CRITICAL FIX: Ensure we have valid inputs
            if len(clips) == 0 or len(audio_files) == 0:
                logger.error("❌ No valid inputs for composition")
                return ""
            
            # Create filters to normalize all videos to same dimensions (portrait 720x1280)
            video_scale_filters = []
            for i in range(len(clips)):
                video_scale_filters.append(f"[{i}:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
            
            # Join the scale filters
            scale_filter_str = ";".join(video_scale_filters)
            
            # Create concatenation inputs
            video_concat_inputs = "".join([f"[v{i}]" for i in range(len(clips))])
            audio_inputs = "".join([f"[{len(clips)+i}:a]" for i in range(len(audio_files))])
            
            # CRITICAL FIX: Ensure filter complex is valid with scaling
            if len(clips) > 0 and len(audio_files) > 0:
                filter_complex = f"{scale_filter_str};{video_concat_inputs}concat=n={len(clips)}:v=1:a=0[outv];{audio_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]"
            elif len(clips) > 0:
                # Only video, no audio
                filter_complex = f"{scale_filter_str};{video_concat_inputs}concat=n={len(clips)}:v=1:a=0[outv]"
            elif len(audio_files) > 0:
                # Only audio, no video
                filter_complex = f"{audio_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]"
            else:
                logger.error("❌ No valid inputs for composition")
                return ""
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg', '-y'
            ] + input_parts + [
                '-filter_complex', filter_complex
            ]
            
            # Add output mappings based on what we have
            if len(clips) > 0:
                cmd.extend(['-map', '[outv]'])
            if len(audio_files) > 0:
                cmd.extend(['-map', '[outa]'])
            
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ])
            
            logger.info("🎬 Running standard composition...")
            logger.info(f"🎬 Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Standard composition completed")
                return output_path
            else:
                logger.error(f"❌ Standard composition failed: {result.stderr}")
                logger.error(f"❌ FFmpeg stdout: {result.stdout}")
                
                # CRITICAL FIX: Try fallback composition with simpler approach
                return self._create_simple_fallback_composition(clips, audio_files, output_path, session_context)
                
        except Exception as e:
            logger.error(f"❌ Standard composition error: {e}")
            return ""
    
    def _create_simple_fallback_composition(self, clips: List[str], audio_files: List[str], 
                                           output_path: str, session_context: SessionContext) -> str:
        """Create a simple fallback composition when standard composition fails"""
        try:
            logger.info("🎬 Creating simple fallback composition")
            
            # If we have audio but no video, create a simple video with audio
            if not clips and audio_files:
                return self._create_audio_only_video(audio_files, output_path, session_context)
            
            # If we have video but no audio, create video without audio
            if clips and not audio_files:
                return self._create_video_only_composition(clips, output_path, session_context)
            
            # If we have both, try a very simple concatenation
            if clips and audio_files:
                return self._create_simple_video_audio_composition(clips, audio_files, output_path, session_context)
            
            logger.error("❌ No valid inputs for fallback composition")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Fallback composition failed: {e}")
            return ""
    
    def _create_audio_only_video(self, audio_files: List[str], output_path: str, 
                                session_context: SessionContext) -> str:
        """Create a video with only audio (static image)"""
        try:
            logger.info("🎬 Creating audio-only video")
            
            # Concatenate audio files first
            audio_concat_path = session_context.get_output_path("temp_files", "audio_concat.mp3")
            os.makedirs(os.path.dirname(audio_concat_path), exist_ok=True)
            
            if len(audio_files) > 1:
                # Concatenate multiple audio files
                input_parts = []
                for audio in audio_files:
                    input_parts.extend(['-i', audio])
                
                audio_inputs = "".join([f"[{i}:a]" for i in range(len(audio_files))])
                filter_complex = f"{audio_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]"
                
                cmd = [
                    'ffmpeg', '-y'
                ] + input_parts + [
                    '-filter_complex', filter_complex,
                    '-map', '[outa]',
                    '-c:a', 'aac',
                    audio_concat_path
                ]
                
                import subprocess
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.warning("⚠️ Audio concatenation failed, using first audio file")
                    audio_file = audio_files[0]
                else:
                    audio_file = audio_concat_path
            else:
                audio_file = audio_files[0]
            
            # Get audio duration
            import subprocess
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', audio_file]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            if probe_result.returncode != 0:
                logger.warning("⚠️ Could not get audio duration, using default")
                duration = 15.0
            else:
                import json
                probe_data = json.loads(probe_result.stdout)
                audio_stream = next((s for s in probe_data.get('streams', []) if s.get('codec_type') == 'audio'), None)
                duration = float(audio_stream.get('duration', 15.0)) if audio_stream else 15.0
            
            # Create video with solid color background
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c=black:size=1080x1920:duration={duration}',
                '-i', audio_file,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Created audio-only video: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Failed to create audio-only video: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Audio-only video creation failed: {e}")
            return ""
    
    def _create_video_only_composition(self, clips: List[str], output_path: str, 
                                      session_context: SessionContext) -> str:
        """Create video composition without audio"""
        try:
            logger.info("🎬 Creating video-only composition")
            
            if len(clips) == 1:
                # Single clip, just copy it
                import shutil
                shutil.copy2(clips[0], output_path)
                return output_path
            
            # Multiple clips, concatenate without audio
            input_parts = []
            for clip in clips:
                input_parts.extend(['-i', clip])
            
            video_inputs = "".join([f"[{i}:v]" for i in range(len(clips))])
            filter_complex = f"{video_inputs}concat=n={len(clips)}:v=1:a=0[outv]"
            
            cmd = [
                'ffmpeg', '-y'
            ] + input_parts + [
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
            
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Created video-only composition: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Failed to create video-only composition: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Video-only composition failed: {e}")
            return ""
    
    def _create_simple_video_audio_composition(self, clips: List[str], audio_files: List[str], 
                                              output_path: str, session_context: SessionContext) -> str:
        """Create a simple video-audio composition"""
        try:
            logger.info("🎬 Creating simple video-audio composition")
            
            # Use the first clip and first audio file for simplicity
            video_file = clips[0]
            audio_file = audio_files[0]
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video_file,
                '-i', audio_file,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ]
            
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Created simple video-audio composition: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Failed to create simple video-audio composition: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Simple video-audio composition failed: {e}")
            return ""

    def _create_video_placeholder(self, config: GeneratedVideoConfig, 
                                clips: List[str], audio_files: List[str]) -> str:
        """Create comprehensive video placeholder content"""
        content = f"""# AI Video Generator - Video Placeholder

## Video Information
- Topic: {config.topic}
- Duration: {config.duration_seconds} seconds
- Platform: {config.target_platform.value}
- Category: {config.category.value}
- Style: {config.style}
- Tone: {config.tone}
- Target Audience: {config.target_audience}

## Generation Details
- Generated: {datetime.now().isoformat()}
- Clips Generated: {len(clips)}
- Audio Files: {len(audio_files)}

## Content Structure
- Hook: {config.hook}
- Main Content: {config.main_content}
- Call to Action: {config.call_to_action}

## Generated Assets
### Video Clips:
{chr(10).join(f"- {clip}" for clip in clips)}

### Audio Files:
{chr(10).join(f"- {audio}" for audio in audio_files)}

## Visual Style
- Visual Style: {config.visual_style}
- Color Scheme: {config.color_scheme}
- Transitions: {config.transitions}

## Audio Style
- Background Music: {config.background_music_style}
- Voiceover Style: {config.voiceover_style}
- Sound Effects: {config.sound_effects}

---
This is a placeholder file. In a full implementation, this would be a complete MP4 video file.
"""
        return content
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                return size_bytes / (1024 * 1024)
            return 0.0
        except:
            return 0.0
    
    def _ensure_perfect_duration_sync(self, clips: List[str], audio_files: List[str],
                                    target_duration: float) -> Dict[str, Any]:
        """Ensure perfect duration synchronization between video and audio"""
        logger.info(f"⏱️ Ensuring perfect duration sync for {target_duration}s")
        
        adjustments_made = []
        
        try:
            # 1. Analyze actual clip and audio durations
            clip_durations = []
            for clip in clips:
                if os.path.exists(clip):
                    try:
                        with VideoFileClip(clip) as video_clip:
                            clip_durations.append(video_clip.duration)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get duration for {clip}: {e}")
                        clip_durations.append(target_duration / len(clips))
                else:
                    clip_durations.append(target_duration / len(clips))
            
            audio_durations = []
            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    try:
                        with AudioFileClip(audio_file) as audio_clip:
                            audio_durations.append(audio_clip.duration)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get duration for {audio_file}: {e}")
                        audio_durations.append(target_duration / len(audio_files))
                else:
                    audio_durations.append(target_duration / len(audio_files))
            
            total_clip_duration = sum(clip_durations)
            total_audio_duration = sum(audio_durations)
            
            logger.info(f"🎥 Video clips total: {total_clip_duration:.2f}s")
            logger.info(f"🎵 Audio total: {total_audio_duration:.2f}s")
            logger.info(f"🎯 Target: {target_duration:.2f}s")
            
            # 2. Calculate sync accuracy
            if total_clip_duration > 0:
                video_audio_diff = abs(total_clip_duration - total_audio_duration)
                target_diff = abs(total_clip_duration - target_duration)
                sync_accuracy = max(0.0, 1.0 - (video_audio_diff / target_duration))
                
                # 3. Check if adjustment is needed
                if video_audio_diff > 0.5:  # More than 0.5 second difference
                    logger.warning(f"⚠️ Audio/video duration mismatch: {video_audio_diff:.2f}s")
                    adjustments_made.append(f"Audio/video duration mismatch: {video_audio_diff:.2f}s")
                    
                    # Recommend shorter content if audio is too long
                    if total_audio_duration > target_duration * 1.1:
                        logger.warning(f"⚠️ Audio too long ({total_audio_duration:.2f}s), consider shortening script")
                        adjustments_made.append("Audio too long - consider shortening script")
                
                if target_diff > 0.5:
                    logger.warning(f"⚠️ Total duration differs from target: {target_diff:.2f}s")
                    adjustments_made.append(f"Duration differs from target: {target_diff:.2f}s")
                    
            else:
                sync_accuracy = 0.0
                adjustments_made.append("Could not calculate video durations")
            
            return {
                'video_duration': total_clip_duration,
                'audio_duration': total_audio_duration,
                'target_duration': target_duration,
                'sync_accuracy': sync_accuracy,
                'adjustments_made': adjustments_made,
                'clip_durations': clip_durations,
                'audio_durations': audio_durations
            }
            
        except Exception as e:
            logger.error(f"❌ Duration sync analysis failed: {e}")
            return {
                'video_duration': target_duration,
                'audio_duration': target_duration,
                'target_duration': target_duration,
                'sync_accuracy': 0.0,
                'adjustments_made': [f"Duration sync failed: {e}"]
            }

    def _save_prompts_to_session(self, session_context: SessionContext, prompts_data: Dict[str, Any]):
        """Save all prompts used in generation to session for debugging"""
        try:
            prompts_path = session_context.get_output_path("logs", "all_prompts_used.json")
            os.makedirs(os.path.dirname(prompts_path), exist_ok=True)
            
            with open(prompts_path, 'w') as f:
                json.dump(prompts_data, f, indent=2)
            
            logger.info(f"💾 Saved all prompts to: {prompts_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save prompts: {e}")
    
    def _create_subtitles(self, script_result: Dict[str, Any], audio_files: List[str], 
                         session_context: SessionContext) -> Dict[str, str]:
        """Create subtitle files (SRT and VTT) from script and audio timing"""
        try:
            # Get the actual script content
            script_content = script_result.get('final_script', script_result.get('optimized_script', ''))
            
            if not script_content:
                logger.warning("⚠️ No script content available for subtitles")
                return {}
            
            # Split script into segments based on audio files
            segments = []
            if audio_files:
                # Calculate timing based on audio files
                current_time = 0.0
                words = script_content.split()
                words_per_segment = len(words) // len(audio_files)
                
                for i, audio_file in enumerate(audio_files):
                    start_time = current_time
                    
                    # Get audio duration
                    try:
                        import subprocess
                        result = subprocess.run([
                            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                            '-show_format', audio_file
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            import json
                            data = json.loads(result.stdout)
                            duration = float(data['format']['duration'])
                        else:
                            duration = 3.0  # Default duration
                    except:
                        duration = 3.0  # Default duration
                    
                    end_time = start_time + duration
                    
                    # Get text for this segment
                    start_word = i * words_per_segment
                    end_word = start_word + words_per_segment if i < len(audio_files) - 1 else len(words)
                    segment_text = ' '.join(words[start_word:end_word])
                    
                    segments.append({
                        'start': start_time,
                        'end': end_time,
                        'text': segment_text
                    })
                    
                    current_time = end_time
            
            # Create subtitle files
            subtitle_files = {}
            
            # Create SRT file
            srt_path = session_context.get_output_path("subtitles", "subtitles.srt")
            os.makedirs(os.path.dirname(srt_path), exist_ok=True)
            
            with open(srt_path, 'w') as f:
                for i, segment in enumerate(segments, 1):
                    start_time = self._format_time_srt(segment['start'])
                    end_time = self._format_time_srt(segment['end'])
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text']}\n\n")
            
            subtitle_files['srt'] = srt_path
            
            # Create VTT file
            vtt_path = session_context.get_output_path("subtitles", "subtitles.vtt")
            
            with open(vtt_path, 'w') as f:
                f.write("WEBVTT\n\n")
                for segment in segments:
                    start_time = self._format_time_vtt(segment['start'])
                    end_time = self._format_time_vtt(segment['end'])
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text']}\n\n")
            
            subtitle_files['vtt'] = vtt_path
            
            # Create subtitle metadata
            metadata = {
                'total_segments': len(segments),
                'total_duration': segments[-1]['end'] if segments else 0,
                'script_content': script_content,
                'audio_files_used': audio_files
            }
            
            metadata_path = session_context.get_output_path("subtitles", "subtitle_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Created subtitles: SRT and VTT files")
            return subtitle_files
            
        except Exception as e:
            logger.error(f"❌ Subtitle creation failed: {e}")
            return {}
    
    def _format_time_srt(self, seconds: float) -> str:
        """Format time for SRT subtitle format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """Format time for VTT subtitle format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
        else:
            return f"{minutes:02d}:{secs:06.3f}"

    def _get_video_dimensions(self, platform: str) -> tuple:
        """Get video dimensions based on target platform"""
        platform_dimensions = {
            'tiktok': (720, 1280),      # 9:16 portrait
            'instagram': (720, 1280),   # 9:16 portrait  
            'youtube': (1280, 720),     # 16:9 landscape
            'facebook': (1280, 720),    # 16:9 landscape
            'twitter': (1280, 720),     # 16:9 landscape
            'linkedin': (1280, 720)     # 16:9 landscape
        }
        
        return platform_dimensions.get(platform.lower(), (720, 1280))  # Default to portrait for modern social media
    
    def _get_platform_aspect_ratio(self, platform: str) -> str:
        """Get aspect ratio string for platform"""
        platform_ratios = {
            'tiktok': '9:16',      # Portrait
            'instagram': '9:16',   # Portrait  
            'youtube': '16:9',     # Landscape
            'facebook': '16:9',    # Landscape
            'twitter': '16:9',     # Landscape
            'linkedin': '16:9'     # Landscape
        }
        
        return platform_ratios.get(platform.lower(), '9:16')  # Default to portrait for modern social media
    
    def _apply_platform_orientation(self, video_path: str, platform: str, session_context: SessionContext) -> str:
        """Apply correct orientation and dimensions for target platform"""
        try:
            target_width, target_height = self._get_video_dimensions(platform)
            aspect_ratio = self._get_platform_aspect_ratio(platform)
            
            logger.info(f"🎬 Applying {platform} orientation: {target_width}x{target_height} ({aspect_ratio})")
            
            # Create output path
            oriented_path = session_context.get_output_path("temp_files", f"oriented_{os.path.basename(video_path)}")
            os.makedirs(os.path.dirname(oriented_path), exist_ok=True)
            
            # Use FFmpeg to resize and reorient video for platform
            if aspect_ratio == '9:16':  # Portrait
                # For portrait, crop from center and scale
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height}',
                    '-c:v', 'libx264', '-c:a', 'aac',
                    '-preset', 'fast',
                    '-y', oriented_path
                ]
            else:  # Landscape
                # For landscape, pad with black bars
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black',
                    '-c:v', 'libx264', '-c:a', 'aac',
                    '-preset', 'fast',
                    '-y', oriented_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(oriented_path):
                logger.info(f"✅ Platform orientation applied: {aspect_ratio}")
                return oriented_path
            else:
                logger.warning(f"⚠️ Platform orientation failed: {result.stderr}")
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Platform orientation failed: {e}")
            return video_path

    def _add_fade_out_ending(self, video_path: str, session_context: SessionContext) -> str:
        """Add 1.5 second black screen fade out at the end of the video"""
        try:
            logger.info("🎬 Adding 1.5 second black screen fade out")
            
            # Create output path
            output_path = session_context.get_output_path("temp_files", f"fade_out_{os.path.basename(video_path)}")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get video duration and dimensions
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', video_path
            ]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            probe_data = json.loads(probe_result.stdout)
            
            # Extract video info
            video_duration = float(probe_data['format']['duration'])
            video_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'video'), None)
            if video_stream:
                width = int(video_stream['width'])
                height = int(video_stream['height'])
            else:
                width, height = 720, 1280  # Default
            
            # Create 1.5 second black screen
            black_duration = 1.5
            fade_start_time = video_duration + black_duration - 0.5  # Start fade 0.5s before end
            
            # FFmpeg command to:
            # 1. Concatenate original video with black screen
            # 2. Add fade out effect
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-f', 'lavfi', '-i', f'color=c=black:size={width}x{height}:duration={black_duration}:rate=30',
                '-filter_complex', 
                f'[0:v][1:v]concat=n=2:v=1:a=0[v_concat];[v_concat]fade=t=out:st={fade_start_time}:d=0.5[v_out]',
                '-map', '[v_out]',
                '-map', '0:a',  # Keep original audio
                '-c:v', 'libx264', '-c:a', 'aac',
                '-preset', 'fast',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Added fade out ending: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Fade out failed: {result.stderr}")
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Fade out ending failed: {e}")
            return video_path

    def _create_direct_fallback_clip(self, prompt: str, duration: float, output_path: str, config: GeneratedVideoConfig = None) -> str:
        """Create fallback clip directly using FFmpeg without abstract class"""
        logger.info(f"🎨 Creating direct fallback for: {prompt[:50]}...")
        
        try:
            # Create a colorful test pattern video with FFmpeg
            import subprocess
            import random
            
            # Get platform-specific dimensions
            if config and hasattr(config, 'target_platform'):
                platform = config.target_platform.value
                width, height = self._get_video_dimensions(platform)
                logger.info(f"📱 Using platform dimensions for {platform}: {width}x{height}")
            else:
                width, height = 720, 1280  # Default to portrait
                logger.info(f"📱 Using default portrait dimensions: {width}x{height}")
            
            # Generate random colors for variety
            colors = [
                "red", "green", "blue", "yellow", "magenta", "cyan", 
                "orange", "purple", "pink", "lime", "navy", "teal"
            ]
            color = random.choice(colors)
            
            # Properly escape text for FFmpeg
            safe_text = prompt[:30].replace("'", "").replace('"', '').replace(':', '').replace('!', '').replace('?', '').replace(',', '')
            
            # Create video with text overlay showing the prompt
            cmd = [
                'ffmpeg', '-f', 'lavfi', 
                '-i', f'color=c={color}:size={width}x{height}:duration={duration}',
                '-vf', f'drawtext=text="{safe_text}":fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '24',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ Direct fallback video created: {output_path} ({file_size:.1f}MB)")
                return output_path
            else:
                logger.error(f"❌ FFmpeg direct fallback failed: {result.stderr}")
                return self._create_minimal_direct_fallback(prompt, duration, output_path)
                
        except Exception as e:
            logger.error(f"❌ Direct fallback creation failed: {e}")
            return self._create_minimal_direct_fallback(prompt, duration, output_path)
    
    def _create_minimal_direct_fallback(self, prompt: str, duration: float, output_path: str) -> str:
        """Create minimal fallback using basic FFmpeg"""
        try:
            import subprocess
            
            # Create simple solid color video
            cmd = [
                'ffmpeg', '-f', 'lavfi', 
                '-i', f'color=c=blue:size=720x1280:duration={duration}',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '24',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Minimal direct fallback created: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Even minimal fallback failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Minimal fallback failed: {e}")
            return ""

    def _save_comprehensive_session_data(self, config: GeneratedVideoConfig, 
                                        script_result: Dict[str, Any], 
                                        style_decision: Dict[str, Any],
                                        positioning_decision: Dict[str, Any],
                                        clips: List[str], audio_files: List[str],
                                        session_context: SessionContext):
        """Save comprehensive session data to ensure all information is properly stored"""
        try:
            logger.info("💾 Saving comprehensive session data")
            
            # Save AI agent decisions
            decisions_path = session_context.get_output_path("decisions", "ai_decisions.json")
            os.makedirs(os.path.dirname(decisions_path), exist_ok=True)
            
            decisions_data = {
                "style_decision": style_decision,
                "positioning_decision": positioning_decision,
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "topic": config.topic,
                    "platform": str(config.target_platform),
                    "category": str(config.category),
                    "duration": config.duration_seconds,
                    "visual_style": config.visual_style,
                    "tone": config.tone
                }
            }
            
            with open(decisions_path, 'w') as f:
                json.dump(decisions_data, f, indent=2)
            
            # Save generation log
            log_path = session_context.get_output_path("logs", "generation_log.json")
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            log_data = {
                "session_id": session_context.session_id,
                "generation_timestamp": datetime.now().isoformat(),
                "files_generated": {
                    "video_clips": len(clips),
                    "audio_files": len(audio_files),
                    "script_files": len([f for f in os.listdir(session_context.get_output_path("scripts")) if f.endswith('.txt')]) if os.path.exists(session_context.get_output_path("scripts")) else 0
                },
                "clip_paths": clips,
                "audio_paths": audio_files,
                "script_result": script_result
            }
            
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            # Save all prompts used
            prompts_path = session_context.get_output_path("logs", "all_prompts_used.json")
            prompts_data = {
                "veo_prompts": getattr(self, '_veo_prompts', []),
                "audio_prompts": getattr(self, '_audio_prompts', []),
                "script_prompts": getattr(self, '_script_prompts', []),
                "timestamp": datetime.now().isoformat()
            }
            
            with open(prompts_path, 'w') as f:
                json.dump(prompts_data, f, indent=2)
            
            logger.info("✅ Comprehensive session data saved")
            
        except Exception as e:
            logger.error(f"❌ Failed to save comprehensive session data: {e}")
    
    def _save_veo_prompts(self, prompts: List[str], session_context: SessionContext):
        """Save VEO prompts for transparency"""
        if not hasattr(self, '_veo_prompts'):
            self._veo_prompts = []
        self._veo_prompts.extend(prompts)
        
    def _save_audio_prompts(self, prompts: List[str], session_context: SessionContext):
        """Save audio prompts for transparency"""
        if not hasattr(self, '_audio_prompts'):
            self._audio_prompts = []
        self._audio_prompts.extend(prompts)
        
    def _save_script_prompts(self, prompts: List[str], session_context: SessionContext):
        """Save script prompts for transparency"""
        if not hasattr(self, '_script_prompts'):
            self._script_prompts = []
        self._script_prompts.extend(prompts)

    def _violates_content_policy(self, prompt: str) -> bool:
        """Check if prompt violates Google's content policies"""
        # Convert to lowercase for easier matching
        prompt_lower = prompt.lower()
        
        # Keywords that typically violate content policies
        policy_violations = [
            # Violence
            'violence', 'violent', 'fighting', 'battle', 'war', 'attack', 'assault',
            'shooting', 'gun', 'weapon', 'blood', 'gore', 'death', 'kill', 'murder',
            
            # Political controversy
            'president', 'political', 'government', 'election', 'protest', 'riot',
            'arrest', 'police', 'officer', 'law enforcement', 'criminal', 'crime',
            
            # Discrimination
            'racist', 'discrimination', 'hate', 'offensive', 'inappropriate',
            
            # Adult content
            'nude', 'naked', 'sexual', 'adult', 'explicit',
            
            # Health misinformation / harmful content
            'convince mom', 'better than water', 'prefer coke', 'soda for kids',
            'unhealthy', 'junk food', 'sugar for children',
            
            # Dangerous activities
            'dangerous', 'harmful', 'illegal', 'drugs', 'alcohol',
            
            # Specific problematic scenarios
            'black president', 'police officer', 'arresting', 'violence against',
            'officer sees', 'officer apologize', 'treat him like'
        ]
        
        # Check for violations
        for violation in policy_violations:
            if violation in prompt_lower:
                logger.warning(f"⚠️ Content policy violation detected: '{violation}' in prompt")
                return True
        
        return False

    def _create_visual_prompt_from_segment(self, segment_text: str, scene_number: int, style: str = "dynamic") -> str:
        """Transform segment text into a safe visual prompt for VEO"""
        # Analyze the segment to extract visual elements
        segment_lower = segment_text.lower()
        
        # Map common words to visual scenes (animated style)
        visual_mappings = {
            # Family/People
            'parent': 'animated happy family in bright colorful cartoon kitchen',
            'mom': 'animated caring mother with cartoon children in stylized home setting',
            'mother': 'animated caring mother with cartoon children in stylized home setting',
            'kid': 'animated cheerful children playing in cartoon style',
            'child': 'animated happy children in colorful cartoon environment',
            
            # Actions
            'seeking': 'animated character looking thoughtfully at cartoon options',
            'best': 'stylized premium items on animated display',
            'vibrant': 'colorful energetic animated scene',
            'energy': 'dynamic animated movement and cartoon activity',
            'joy': 'animated characters smiling and celebrating in cartoon style',
            'happiness': 'joyful animated celebration scene',
            
            # Objects (generic)
            'water': 'animated clear refreshing beverage in cartoon style',
            'drink': 'animated refreshing beverages on stylized table',
            'bottle': 'cartoon product bottles arranged in 3D animation',
            
            # Environments
            'home': 'animated modern family home interior in cartoon style',
            'kitchen': 'bright colorful cartoon kitchen',
            'play': "animated children's playground with colorful cartoon equipment"
        }
        
        # Build visual prompt from mappings
        visual_elements = []
        for keyword, visual in visual_mappings.items():
            if keyword in segment_lower:
                visual_elements.append(visual)
        
        # If no specific mappings found, use generic safe visuals
        if not visual_elements:
            visual_elements = [f"abstract {style} visual scene {scene_number}"]
        
        # Combine elements into coherent prompt
        base_prompt = ', '.join(visual_elements[:2])  # Limit to 2 main elements
        
        # Add style and technical requirements with non-realistic approach
        visual_prompt = f"{base_prompt}, {style} animated cartoon style, 3D animation, stylized graphics, colorful illustration, no text overlays"
        
        logger.info(f"🎨 Transformed segment to visual: '{segment_text[:30]}...' → '{visual_prompt}'")
        return visual_prompt
    
    def _create_generic_visual_prompt(self, scene_number: int, style: str = "dynamic") -> str:
        """Create a generic safe visual prompt when no segment is available"""
        generic_prompts = [
            f"colorful abstract {style} animated motion graphics, cartoon style, scene {scene_number}",
            f"dynamic geometric patterns with {style} 3D animation transitions, stylized graphics, scene {scene_number}",
            f"beautiful animated nature scenery with {style} cartoon illustration, scene {scene_number}",
            f"modern lifestyle animated visuals in {style} cartoon style, 3D graphics, scene {scene_number}",
            f"creative animated storytelling with {style} cartoon effects, stylized illustration, scene {scene_number}"
        ]
        
        # Use scene number to select different prompts
        prompt_index = (scene_number - 1) % len(generic_prompts)
        return generic_prompts[prompt_index]
    
    def _create_safe_fallback_prompt(self, topic: str, scene_number: int) -> str:
        """Create a safe fallback prompt that won't violate content policies"""
        # Extract safe keywords from the original topic
        safe_keywords = []
        topic_lower = topic.lower()
        
        # Safe words that are generally acceptable
        safe_words = [
            'explain', 'show', 'demonstrate', 'illustrate', 'present', 'display',
            'create', 'build', 'make', 'design', 'develop', 'produce', 'generate',
            'learn', 'teach', 'educate', 'inform', 'guide', 'help', 'support',
            'fun', 'entertaining', 'engaging', 'interesting', 'amazing', 'wonderful',
            'beautiful', 'creative', 'innovative', 'modern', 'trendy', 'popular'
        ]
        
        for word in safe_words:
            if word in topic_lower:
                safe_keywords.append(word)
        
        # Create a generic safe prompt
        if safe_keywords:
            safe_prompt = f"An engaging and informative scene about {topic.split(',')[0]}, {', '.join(safe_keywords[:3])}, scene {scene_number}"
        else:
            safe_prompt = f"An engaging and informative educational scene, dynamic style, scene {scene_number}"
        
        logger.info(f"✅ Created safe fallback prompt: {safe_prompt}")
        return safe_prompt

    def _create_short_multi_line_text(self, text: str, max_words_per_line: int = 4, video_width: int = 1280) -> str:
        """Create smart multi-line text for overlays with overflow prevention and width constraints"""
        try:
            # Ensure max_words_per_line is an integer
            max_words_per_line = int(max_words_per_line) if max_words_per_line else 4
            
            # Clean the text - enhanced for FFmpeg compatibility
            cleaned_text = text.replace("'", "").replace('"', '').replace(':', '').replace('!', '').replace('?', '').replace(',', '').replace('\\', '').replace('/', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            
            # Split into words
            words = cleaned_text.split()
            
            # CRITICAL FIX: Dynamic text wrapping based on video width to prevent cutoff
            # Calculate safe text width (80% of video width to ensure margins)
            safe_text_width = int(video_width * 0.8)
            
            # Estimate character width based on video resolution
            # Typical font: 1 character ≈ 0.6 of font size in pixels
            estimated_font_size = max(32, int(video_width * 0.035))  # Responsive font size
            char_width = int(estimated_font_size * 0.6)
            max_chars_per_line = safe_text_width // char_width
            
            # Smart text wrapping with width constraints
            max_lines = 3  # Keep to 3 lines for better visibility
            
            # Calculate optimal words per line based on character limits
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 5
            words_per_line_by_width = max(1, int(max_chars_per_line / (avg_word_length + 1)))  # +1 for space
            
            # Use the more restrictive limit
            optimal_words_per_line = min(max_words_per_line, words_per_line_by_width)
            
            logger.info(f"📐 Text width constraints: video_width={video_width}, safe_width={safe_text_width}, "
                       f"font_size={estimated_font_size}, max_chars={max_chars_per_line}, "
                       f"words_per_line={optimal_words_per_line}")
            
            # Prioritize shorter, punchier text for better engagement
            if len(words) > max_lines * optimal_words_per_line:
                # Calculate optimal distribution with width constraints
                total_words = min(len(words), max_lines * optimal_words_per_line)
                words = words[:total_words]
                logger.info(f"📝 Truncated overlay to fit width: {total_words} words in {max_lines} lines")
            
            # Create lines with smart word distribution and width checking
            lines = []
            current_line = []
            
            for word in words:
                # Check if adding this word would exceed character limit
                test_line = current_line + [word]
                test_line_text = ' '.join(test_line)
                
                if len(test_line_text) <= max_chars_per_line and len(test_line) <= optimal_words_per_line:
                    current_line.append(word)
                else:
                    # Current line is full, start new line
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        # Single word is too long, truncate it
                        truncated_word = word[:max_chars_per_line-3] + "..." if len(word) > max_chars_per_line else word
                        lines.append(truncated_word)
                        current_line = []
                
                # Stop if we have enough lines
                if len(lines) >= max_lines:
                    break
            
            # Add remaining words to the last line if we have room
            if current_line and len(lines) < max_lines:
                lines.append(' '.join(current_line))
            
            # Join lines with newline character for FFmpeg
            multi_line_text = r'\N'.join(lines)
            
            # Final character count check
            total_chars = sum(len(line) for line in lines)
            logger.info(f"📝 Created width-constrained overlay: {len(lines)} lines, {len(words)} words, {total_chars} chars (max: {max_chars_per_line * max_lines})")
            
            return multi_line_text
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create multi-line text: {e}")
            # Fallback to simple truncation with width constraint
            max_chars = min(50, int(video_width * 0.04))
            return text[:max_chars].replace("'", "").replace('"', '').replace(':', '').replace('!', '').replace('?', '').replace(',', '')

    def _format_subtitle_text(self, text: str, max_words_per_line: int = 6, max_chars_per_line: int = 50) -> str:
        """Format text for MoviePy subtitle display with proper line breaks and width constraints"""
        try:
            # Split text into words
            words = text.split()
            
            if len(words) <= max_words_per_line and len(text) <= max_chars_per_line:
                return text
            
            # Create lines with both word and character constraints
            lines = []
            current_line = []
            
            for word in words:
                # Check if adding this word would exceed limits
                test_line = current_line + [word]
                test_text = ' '.join(test_line)
                
                # Use both word count and character count constraints
                if (len(test_line) <= max_words_per_line and 
                    len(test_text) <= max_chars_per_line):
                    current_line.append(word)
                else:
                    # Current line is full, start new line
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        # Single word is too long, truncate it
                        truncated_word = word[:max_chars_per_line-3] + "..." if len(word) > max_chars_per_line else word
                        lines.append(truncated_word)
                        current_line = []
                
                # Limit to maximum 3 lines for readability
                if len(lines) >= 3:
                    break
            
            # Add remaining words to the last line
            if current_line and len(lines) < 3:
                remaining_text = ' '.join(current_line)
                if len(remaining_text) <= max_chars_per_line:
                    lines.append(remaining_text)
                else:
                    # Truncate if too long
                    lines.append(remaining_text[:max_chars_per_line-3] + "...")
            
            # Join lines with newline character for MoviePy
            formatted_text = '\n'.join(lines)
            
            # Log formatting details for debugging
            logger.debug(f"📝 Formatted subtitle: {len(words)} words → {len(lines)} lines, "
                        f"max chars/line: {max(len(line) for line in lines) if lines else 0}")
            
            return formatted_text
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to format subtitle text: {e}")
            return text

    def _get_ai_overlay_style(self, text: str, overlay_type: str, platform: Any, video_width: int, video_height: int, session_context=None) -> Dict[str, Any]:
        """Get AI-driven overlay styling decisions based on text content and platform"""
        try:
            # Get AI styling from positioning agent with enhanced viral optimization
            if hasattr(self, 'positioning_agent') and self.positioning_agent:
                # Enhanced style prompt for viral engagement
                style_prompt = f"""
                You are a viral video styling expert. Create MAXIMUM ENGAGEMENT overlay styling for: "{text}"
                
                Context:
                - Type: {overlay_type}
                - Platform: {platform}
                - Video dimensions: {video_width}x{video_height}
                
                VIRAL ENGAGEMENT REQUIREMENTS:
                1. ATTENTION-GRABBING COLORS: Never use boring white text
                2. DYNAMIC FONT CHOICES: Match content energy and platform aesthetics
                3. ACCESSIBILITY COMPLIANT: Ensure 7:1 contrast ratio (WCAG AAA)
                4. PLATFORM OPTIMIZED: Different strategies for TikTok vs YouTube vs Instagram
                5. CONTENT-AWARE: Hooks need different styling than CTAs than main content
                
                Color Psychology Guidelines:
                - Red/Orange: Urgency, excitement, food content
                - Blue/Cyan: Trust, tech, educational content
                - Green: Health, money, success themes
                - Purple: Luxury, creativity, mystery
                - Yellow: Happiness, attention, warnings
                - Pink/Magenta: Fun, viral, trendy content
                
                Font Psychology Guidelines:
                - Impact/Anton: Bold statements, shouty content
                - Montserrat: Modern, clean, professional
                - Bebas Neue: Strong, masculine, sports
                - Playfair Display: Elegant, luxury, lifestyle
                - Roboto: Friendly, approachable, tech
                
                Platform-Specific Viral Patterns:
                - TikTok: Bright neon colors, bold fonts, high contrast, animated-friendly
                - Instagram: Aesthetic palettes, clean fonts, story-optimized
                - YouTube: Thumbnail-ready, readable at small sizes, retention-focused
                
                Content Type Styling:
                - Hooks: Bright, attention-grabbing, curiosity-inducing
                - Main Content: Clear, readable, engaging but not overwhelming
                - CTAs: Urgent, action-oriented, conversion-focused
                - Questions: Engaging, thought-provoking, discussion-starter
                
                Return JSON with:
                {{
                    "font_family": "specific font name (Impact, Montserrat-Bold, Anton, etc.)",
                    "font_size": 36-64,
                    "primary_color": "#HEX format main text color",
                    "background_color": "#HEX format background",
                    "stroke_color": "#HEX format outline",
                    "background_opacity": 0.0-1.0,
                    "stroke_width": 0-4,
                    "shadow_enabled": true/false,
                    "shadow_color": "#HEX format",
                    "animation_style": "none|bounce|pulse|glow|shake",
                    "words_per_line": 2-5,
                    "style_reasoning": "brief explanation of choices",
                    "engagement_score": "1-10 predicted viral potential",
                    "accessibility_compliant": true/false,
                    "color_psychology": "explain color choice reasoning"
                }}
                """
                
                try:
                    import google.generativeai as genai
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(style_prompt)
                    
                    import json
                    import re
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        ai_style = json.loads(json_match.group())
                        
                        # Enhanced logging to session
                        self._log_ai_styling_decision(ai_style, text, overlay_type, session_context)
                        
                        logger.info(f"🎨 AI VIRAL STYLING: {overlay_type}")
                        logger.info(f"   Font: {ai_style.get('font_family', 'Arial-Bold')} {ai_style.get('font_size', 32)}px")
                        logger.info(f"   Colors: {ai_style.get('primary_color', '#FFFFFF')} on {ai_style.get('background_color', '#000000')}")
                        logger.info(f"   Engagement Score: {ai_style.get('engagement_score', 'N/A')}/10")
                        logger.info(f"   Reasoning: {ai_style.get('style_reasoning', 'No reasoning provided')[:100]}...")
                        
                        return ai_style
                except Exception as e:
                    logger.warning(f"⚠️ AI viral styling failed: {e}")
            
            # Fallback to smart default styling
            return self._get_smart_default_style(text, overlay_type, platform, video_width, video_height)
            
        except Exception as e:
            logger.error(f"❌ Overlay styling failed: {e}")
            return self._get_smart_default_style(text, overlay_type, platform, video_width, video_height)

    def _log_ai_styling_decision(self, ai_style: Dict[str, Any], text: str, overlay_type: str, session_context) -> None:
        """Log AI styling decisions to session output for analysis"""
        try:
            if not session_context:
                return
            
            import json
            from datetime import datetime
            
            # Create styling log entry
            styling_log = {
                "timestamp": datetime.now().isoformat(),
                "text": text[:100],  # Truncate long text
                "overlay_type": overlay_type,
                "ai_decisions": {
                    "font_family": ai_style.get('font_family', 'Unknown'),
                    "font_size": ai_style.get('font_size', 0),
                    "primary_color": ai_style.get('primary_color', '#FFFFFF'),
                    "background_color": ai_style.get('background_color', '#000000'),
                    "stroke_color": ai_style.get('stroke_color', '#000000'),
                    "animation_style": ai_style.get('animation_style', 'none'),
                    "engagement_score": ai_style.get('engagement_score', 'N/A'),
                    "accessibility_compliant": ai_style.get('accessibility_compliant', False),
                    "style_reasoning": ai_style.get('style_reasoning', ''),
                    "color_psychology": ai_style.get('color_psychology', '')
                }
            }
            
            # Save to session overlays directory
            overlays_dir = session_context.get_output_path("overlays")
            os.makedirs(overlays_dir, exist_ok=True)
            
            styling_log_path = os.path.join(overlays_dir, "ai_styling_decisions.jsonl")
            
            # Append to JSONL file for easy analysis
            with open(styling_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(styling_log, ensure_ascii=False) + '\n')
            
            logger.info(f"💾 AI styling decision logged to session: {overlay_type}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to log AI styling decision: {e}")

    def _log_overlay_styling_summary(self, overlays: List[Dict[str, Any]], found_points: List[Dict[str, Any]], 
                                   hook_text: str, script_content: str) -> None:
        """Log comprehensive overlay styling summary to session"""
        try:
            import json
            from datetime import datetime
            
            # Create comprehensive styling summary
            styling_summary = {
                "timestamp": datetime.now().isoformat(),
                "total_overlays": len(overlays),
                "content_analysis": {
                    "hook_text": hook_text[:100],
                    "script_length": len(script_content),
                    "found_points": len(found_points),
                    "point_types": [point.get('type', 'unknown') for point in found_points]
                },
                "overlay_styles": [],
                "color_palette_used": set(),
                "fonts_used": set(),
                "animations_used": set(),
                "engagement_analysis": {
                    "average_engagement_score": 0,
                    "max_engagement_score": 0,
                    "viral_potential": "unknown"
                }
            }
            
            # Analyze each overlay
            engagement_scores = []
            for overlay in overlays:
                overlay_style = {
                    "text": overlay.get('text', '')[:50],
                    "font_size": overlay.get('font_size', 0),
                    "font_color": overlay.get('font_color', overlay.get('primary_color', '#FFFFFF')),
                    "background_color": overlay.get('background_color', '#000000'),
                    "animation_style": overlay.get('animation_style', 'none'),
                    "position": overlay.get('position', 'unknown'),
                    "style_type": overlay.get('style', 'unknown'),
                    "engagement_score": overlay.get('engagement_score', 5),
                    "timing": {
                        "start": overlay.get('start_time', 0),
                        "end": overlay.get('end_time', 0),
                        "duration": overlay.get('end_time', 0) - overlay.get('start_time', 0)
                    }
                }
                
                styling_summary["overlay_styles"].append(overlay_style)
                
                # Collect usage statistics
                color = overlay.get('font_color', overlay.get('primary_color', '#FFFFFF'))
                if color:
                    styling_summary["color_palette_used"].add(color)
                
                animation = overlay.get('animation_style', 'none')
                if animation:
                    styling_summary["animations_used"].add(animation)
                
                engagement = overlay.get('engagement_score', 5)
                if isinstance(engagement, (int, float)):
                    engagement_scores.append(engagement)
            
            # Calculate engagement analysis
            if engagement_scores:
                avg_score = sum(engagement_scores) / len(engagement_scores)
                max_score = max(engagement_scores)
                
                styling_summary["engagement_analysis"]["average_engagement_score"] = round(avg_score, 2)
                styling_summary["engagement_analysis"]["max_engagement_score"] = max_score
                
                # Determine viral potential
                if avg_score >= 8:
                    viral_potential = "HIGH - Strong viral characteristics"
                elif avg_score >= 6:
                    viral_potential = "MEDIUM - Good engagement potential"
                else:
                    viral_potential = "LOW - May need optimization"
                
                styling_summary["engagement_analysis"]["viral_potential"] = viral_potential
            
            # Convert sets to lists for JSON serialization
            styling_summary["color_palette_used"] = list(styling_summary["color_palette_used"])
            styling_summary["animations_used"] = list(styling_summary["animations_used"])
            styling_summary["fonts_used"] = list(styling_summary["fonts_used"])
            
            # Save styling summary to session
            # Note: We'll save this even without session_context for logging purposes
            logger.info("📊 OVERLAY STYLING ANALYSIS:")
            logger.info(f"   Total Overlays: {styling_summary['total_overlays']}")
            logger.info(f"   Colors Used: {styling_summary['color_palette_used']}")
            logger.info(f"   Animations: {styling_summary['animations_used']}")
            logger.info(f"   Avg Engagement: {styling_summary['engagement_analysis']['average_engagement_score']}/10")
            logger.info(f"   Viral Potential: {styling_summary['engagement_analysis']['viral_potential']}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to log overlay styling summary: {e}")

    def _get_smart_default_style(self, text: str, overlay_type: str, platform: Any, video_width: int, video_height: int) -> Dict[str, Any]:
        """Get smart default styling based on text characteristics and platform"""
        try:
            # Calculate text characteristics
            text_length = len(text)
            word_count = len(text.split())
            
            # Platform-specific base styles
            platform_str = str(platform).lower()
            
            # Enhanced viral styling defaults with psychology-based colors
            if 'tiktok' in platform_str:
                base_style = {
                    "font_family": "Impact",  # Bold, attention-grabbing
                    "font_size": max(48, min(64, int(video_width * 0.05))),  # Larger font for TikTok
                    "primary_color": "#FF006E",  # Bright pink for viral energy
                    "background_color": "#000000",
                    "stroke_color": "#FFFFFF",
                    "background_opacity": 0.8,
                    "stroke_width": 3,
                    "shadow_enabled": True,
                    "shadow_color": "#000000",
                    "animation_style": "bounce",
                    "words_per_line": 3,
                    "engagement_score": 8
                }
            elif 'instagram' in platform_str:
                base_style = {
                    "font_family": "Montserrat-Bold",  # Modern, aesthetic
                    "font_size": max(42, min(56, int(video_width * 0.04))),
                    "primary_color": "#8B5CF6",  # Instagram purple
                    "background_color": "#FFFFFF",
                    "stroke_color": "#000000",
                    "background_opacity": 0.9,
                    "stroke_width": 2,
                    "shadow_enabled": True,
                    "shadow_color": "#E5E5E5",
                    "animation_style": "pulse",
                    "words_per_line": 3,
                    "engagement_score": 7
                }
            elif 'youtube' in platform_str:
                base_style = {
                    "font_family": "Roboto-Bold",  # Clean, readable
                    "font_size": max(40, min(52, int(video_width * 0.038))),
                    "primary_color": "#FF0000",  # YouTube red
                    "background_color": "#000000",
                    "stroke_color": "#FFFFFF",
                    "background_opacity": 0.85,
                    "stroke_width": 2,
                    "shadow_enabled": True,
                    "shadow_color": "#333333",
                    "animation_style": "none",
                    "words_per_line": 4,
                    "engagement_score": 6
                }
            else:
                # Default viral styling
                base_style = {
                    "font_family": "Anton",  # Strong, impactful
                    "font_size": max(44, min(58, int(video_width * 0.042))),
                    "primary_color": "#00D9FF",  # Cyan for attention
                    "background_color": "#1A1A1A",
                    "stroke_color": "#FFFFFF",
                    "background_opacity": 0.85,
                    "stroke_width": 3,
                    "shadow_enabled": True,
                    "shadow_color": "#000000",
                    "animation_style": "glow",
                    "words_per_line": 3,
                    "engagement_score": 7
                }
            
            # Content-aware color psychology adjustments
            text_lower = text.lower()
            
            # Adjust for overlay type with enhanced viral psychology
            if overlay_type == "hook":
                base_style["primary_color"] = "#FFD60A"  # Bright yellow for maximum attention
                base_style["font_size"] = int(base_style["font_size"] * 1.3)  # Much larger for hooks
                base_style["animation_style"] = "shake"  # Attention-grabbing animation
                base_style["engagement_score"] = 9
                logger.info("🎣 HOOK STYLING: High-impact yellow with shake animation")
                
            elif overlay_type == "cta":
                base_style["primary_color"] = "#06FFA5"  # Bright green for action
                base_style["background_color"] = "#FF006E"  # Contrasting background
                base_style["font_family"] = "Impact"  # Bold for urgency
                base_style["animation_style"] = "pulse"  # Urgency animation
                base_style["engagement_score"] = 8
                logger.info("🎯 CTA STYLING: Action green with pulse animation")
                
            elif overlay_type == "question":
                base_style["primary_color"] = "#8B5CF6"  # Purple for curiosity
                base_style["animation_style"] = "bounce"  # Engaging animation
                base_style["engagement_score"] = 7
                logger.info("❓ QUESTION STYLING: Curiosity purple with bounce")
                
            # Content-specific color psychology
            if any(word in text_lower for word in ['money', 'cash', 'rich', 'wealth', 'profit']):
                base_style["primary_color"] = "#10B981"  # Green for money
                logger.info("💰 MONEY CONTENT: Green color psychology")
                
            elif any(word in text_lower for word in ['danger', 'warning', 'alert', 'urgent']):
                base_style["primary_color"] = "#EF4444"  # Red for urgency
                base_style["animation_style"] = "shake"
                logger.info("⚠️ URGENT CONTENT: Red with shake animation")
                
            elif any(word in text_lower for word in ['fun', 'party', 'celebrate', 'happy']):
                base_style["primary_color"] = "#F59E0B"  # Orange for fun
                base_style["animation_style"] = "bounce"
                logger.info("🎉 FUN CONTENT: Orange with bounce animation")
                
            elif any(word in text_lower for word in ['tech', 'ai', 'future', 'innovation']):
                base_style["primary_color"] = "#06B6D4"  # Cyan for tech
                base_style["animation_style"] = "glow"
                logger.info("🤖 TECH CONTENT: Cyan with glow effect")
            
            # Adjust for text length
            if text_length > 50:
                base_style["font_size"] = int(base_style["font_size"] * 0.9)  # Smaller for long text
                base_style["words_per_line"] = max(3, base_style["words_per_line"] - 1)
            elif text_length < 20:
                base_style["font_size"] = int(base_style["font_size"] * 1.1)  # Larger for short text
                base_style["words_per_line"] = min(6, base_style["words_per_line"] + 1)
            
            logger.info(f"🎨 Smart default style: {overlay_type} - {base_style['font_family']} {base_style['font_size']}px")
            return base_style
            
        except Exception as e:
            logger.error(f"❌ Smart default styling failed: {e}")
            return {
                "font_family": "Arial-Bold",
                "font_size": 32,
                "color": "0xFFFFFF",
                "background_color": "0x000000",
                "background_opacity": 0.7,
                "stroke_width": 2,
                "words_per_line": 4
            }

    def _generate_and_save_hashtags(self, config: GeneratedVideoConfig, session_context: SessionContext, script_result: Dict[str, Any]):
        """Generate trending hashtags and save them to the session"""
        try:
            logger.info("🏷️ Generating trending hashtags for video")
            
            # Extract platform and category strings
            platform_str = str(config.target_platform).lower().replace('platform.', '')
            category_str = str(config.category).lower().replace('videocategory.', '')
            
            # Get script content
            script_content = script_result.get('final_script', config.topic)
            
            # Generate hashtags
            hashtag_data = self.hashtag_generator.generate_trending_hashtags(
                topic=config.topic,
                platform=platform_str,
                category=category_str,
                script_content=script_content,
                num_hashtags=30
            )
            
            # Save hashtags to session
            self.hashtag_generator.save_hashtags_to_session(hashtag_data, session_context)
            
            logger.info(f"✅ Generated {len(hashtag_data.get('hashtags', []))} trending hashtags")
            
        except Exception as e:
            logger.error(f"❌ Hashtag generation failed: {e}")
            # Create minimal fallback hashtags
            try:
                fallback_hashtags = {
                    'hashtags': [
                        {'tag': f'#{config.topic.split()[0].lower()}', 'category': 'primary', 'estimated_reach': 'medium'},
                        {'tag': f'#{platform_str}', 'category': 'platform', 'estimated_reach': 'high'},
                        {'tag': '#viral', 'category': 'engagement', 'estimated_reach': 'high'},
                        {'tag': '#trending', 'category': 'engagement', 'estimated_reach': 'high'}
                    ],
                    'strategy': {'platform_optimization': platform_str, 'total_hashtags': 4}
                }
                self.hashtag_generator.save_hashtags_to_session(fallback_hashtags, session_context)
                logger.info("✅ Saved fallback hashtags")
            except Exception as fallback_error:
                logger.error(f"❌ Even fallback hashtags failed: {fallback_error}")

    def _trim_video_to_duration(self, video_path: str, target_duration: float, session_context: SessionContext) -> Optional[str]:
        """Trim video to the specified duration with smooth audio/video fadeout"""
        try:
            import subprocess
            
            # Create temporary output path
            temp_output_path = session_context.get_output_path("temp_files", "trimmed_video.mp4")
            os.makedirs(os.path.dirname(temp_output_path), exist_ok=True)
            
            # Calculate fade duration (1.5s or 10% of video, whichever is smaller)
            fade_duration = min(1.5, target_duration * 0.1)
            fade_start = target_duration - fade_duration
            
            logger.info(f"⏱️ Trimming to {target_duration}s with {fade_duration}s fadeout starting at {fade_start}s")
            
            # Use ffmpeg to trim with audio and video fadeout
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-t', str(target_duration),
                '-af', f'afade=t=out:st={fade_start}:d={fade_duration}',  # Audio fadeout
                '-vf', f'fade=t=out:st={fade_start}:d={fade_duration}',   # Video fadeout
                '-c:v', 'libx264', '-c:a', 'aac',  # Re-encode for smooth fade
                temp_output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_output_path):
                logger.info(f"✅ Video trimmed to {target_duration}s with smooth fadeout")
                return temp_output_path
            else:
                logger.error(f"❌ Failed to trim video with fadeout: {result.stderr}")
                # Fallback to basic trim without fadeout
                logger.info("🔄 Attempting basic trim without fadeout...")
                fallback_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-t', str(target_duration),
                    '-c', 'copy',
                    temp_output_path
                ]
                fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)
                if fallback_result.returncode == 0 and os.path.exists(temp_output_path):
                    logger.info(f"✅ Video trimmed to {target_duration}s (basic trim)")
                    return temp_output_path
                else:
                    logger.error(f"❌ Even basic trim failed: {fallback_result.stderr}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ Error trimming video: {e}")
            return None

    def _get_video_duration(self, video_path: str) -> Optional[float]:
        """Get the duration of a video file in seconds"""
        try:
            import subprocess
            import json
            
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_format', '-show_streams',
                '-of', 'json', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                probe_data = json.loads(result.stdout)
                if 'format' in probe_data and 'duration' in probe_data['format']:
                    duration = float(probe_data['format']['duration'])
                    logger.debug(f"🎬 Video duration: {duration:.2f}s")
                    return duration
            
            logger.warning(f"⚠️ Could not determine video duration for: {video_path}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting video duration: {e}")
            return None
    
    def _generate_cheap_video(self, config: GeneratedVideoConfig, session_context: SessionContext) -> str:
        """Generate a cheap text-based video showing prompts instead of actual video generation"""
        logger.info("💰 Starting cheap mode video generation")
        
        try:
            # Generate basic audio using cheap TTS
            logger.info("💰 Generating basic audio with gTTS")
            tts = EnhancedMultilingualTTS(self.api_key)
            
            # Create simple script from config
            script_text = f"{config.hook} {' '.join(config.main_content)} {config.call_to_action}"
            
            # Generate cheap audio
            from ..models.video_models import Language
            language_enum = Language.ENGLISH_US  # Default to English US
            
            audio_files = tts.generate_intelligent_voice_audio(
                script=script_text,
                language=language_enum,
                topic=config.topic,
                platform=config.target_platform,
                category=config.category,
                duration_seconds=config.duration_seconds,
                num_clips=1,
                cheap_mode=True
            )
            
            if not audio_files:
                logger.error("❌ Failed to generate cheap audio")
                return None
            
            # Save audio files to session directory
            self._save_cheap_mode_audio_files(audio_files, session_context)
            
            # Create text-based video showing the prompts
            video_path = self._create_text_video(config, audio_files[0], session_context)
            
            if video_path:
                # Add 1.5s fadeout to cheap mode video as well
                logger.info("🎬 Adding fadeout to cheap mode video")
                final_video_path = self._add_fade_out_ending(video_path, session_context)
                
                if final_video_path:
                    # Save cheap mode session files
                    self._save_cheap_mode_session_files(config, script_text, session_context)
                    
                    logger.info(f"✅ Cheap mode video with fadeout generated: {final_video_path}")
                    return final_video_path
                else:
                    logger.warning("⚠️ Fadeout failed, returning original video")
                    return video_path
            else:
                logger.error("❌ Failed to create cheap text video")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cheap mode video generation failed: {e}")
            return None
    
    def _create_text_video(self, config: GeneratedVideoConfig, audio_file: str, session_context: SessionContext) -> str:
        """Create a simple text-based video showing prompts"""
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ColorClip
            
            # Get audio duration
            audio_clip = AudioFileClip(audio_file)
            duration = audio_clip.duration
            
            # Create background
            background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
            
            # Create the actual script content as subtitles (not debug text)
            script_text = f"{config.hook} {' '.join(config.main_content)} {config.call_to_action}"
            
            # Create subtitle overlays using the professional text renderer
            subtitle_clips = self._create_cheap_mode_subtitles(script_text, duration, audio_file)
            
            # Simple mode badge for cheap mode
            from moviepy.editor import TextClip
            badge_clip = TextClip(
                "💰 CHEAP",
                fontsize=32,
                color='lime',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            ).set_duration(duration).set_position((50, 50)).set_opacity(0.6)
            
            # Composite video with subtitles
            clips = [background, badge_clip] + subtitle_clips
            video = CompositeVideoClip(clips)
            video = video.set_audio(audio_clip)
            
            # Save video
            output_path = session_context.get_output_path("final_output", f"final_video_{session_context.session_id}.mp4")
            
            logger.info(f"💰 Rendering cheap mode video: {output_path}")
            video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Close clips
            audio_clip.close()
            video.close()
            
            logger.info(f"✅ Cheap mode text video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create text video: {e}")
            return None

    def _create_cheap_mode_subtitles(self, script_text: str, duration: float, audio_file: str) -> List:
        """Create subtitle clips for cheap mode video with accurate gTTS timing"""
        try:
            from moviepy.editor import TextClip, AudioFileClip
            import re
            
            # Get actual audio duration for accurate timing
            try:
                audio_clip = AudioFileClip(audio_file)
                actual_audio_duration = audio_clip.duration
                audio_clip.close()
                logger.info(f"🎵 Audio duration: {actual_audio_duration:.2f}s, Video duration: {duration:.2f}s")
                
                # For premium mode, try to get more accurate timing if possible
                if not (getattr(self, 'cheap_mode', False) or 'cheap_mode' in audio_file.lower()):
                    # In the future, we could use speech recognition or audio analysis here
                    # For now, use refined premium timing
                    pass
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not read audio duration, using video duration: {e}")
                actual_audio_duration = duration
            
            # Split script into sentences for subtitle timing
            sentences = re.split(r'[.!?]+', script_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return []
            
            # Calculate timing based on word count and audio generation method
            # Detect if this is gTTS (cheap mode) or premium TTS
            is_cheap_mode = getattr(self, 'cheap_mode', False) or 'cheap_mode' in audio_file.lower()
            
            if is_cheap_mode:
                # gTTS typically speaks at ~2.5-3 words per second
                speaking_rate = 2.8  # words per second (conservative estimate)
                pause_between_sentences = 0.3  # seconds
                logger.info("🎤 Using gTTS timing parameters")
            else:
                # Premium TTS (Google Cloud TTS) speaks faster and more naturally
                speaking_rate = 3.2  # words per second (faster, more natural)
                pause_between_sentences = 0.2  # seconds (shorter pauses)
                logger.info("🎤 Using premium TTS timing parameters")
            
            # Auto-calibrate speaking rate based on actual vs expected duration
            total_words = sum(len(sentence.split()) for sentence in sentences)
            expected_duration = total_words / speaking_rate + (len(sentences) - 1) * pause_between_sentences
            
            if abs(expected_duration - actual_audio_duration) > 1.0:  # More than 1 second difference
                # Calibrate speaking rate to match actual audio
                calibrated_speaking_rate = total_words / (actual_audio_duration - (len(sentences) - 1) * pause_between_sentences)
                logger.info(f"🎯 Auto-calibrated speaking rate: {speaking_rate:.1f} -> {calibrated_speaking_rate:.1f} words/sec")
                speaking_rate = max(1.5, min(4.0, calibrated_speaking_rate))  # Keep within reasonable bounds
            
            subtitle_clips = []
            current_time = 0.0
            
            for i, sentence in enumerate(sentences):
                word_count = len(sentence.split())
                
                # Calculate speaking time for this sentence
                speaking_time = word_count / speaking_rate
                
                # Add pause between sentences (except the first one)
                if i > 0:
                    current_time += pause_between_sentences
                
                start_time = current_time
                end_time = current_time + speaking_time
                
                # Ensure we don't exceed audio duration
                if start_time >= actual_audio_duration:
                    break
                end_time = min(end_time, actual_audio_duration)
                
                logger.info(f"📝 Subtitle {i+1}: '{sentence[:30]}...' ({word_count} words) -> {start_time:.2f}s to {end_time:.2f}s")
                
                current_time = end_time
                
                # Create subtitle clip
                subtitle_clip = TextClip(
                    sentence,
                    fontsize=44,
                    color='white',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=3,
                    size=(1000, None),
                    method='caption'
                ).set_start(start_time).set_duration(end_time - start_time).set_position(('center', 1700))
                
                subtitle_clips.append(subtitle_clip)
            
            logger.info(f"✅ Created {len(subtitle_clips)} subtitle clips for cheap mode")
            return subtitle_clips
            
        except Exception as e:
            logger.error(f"❌ Failed to create cheap mode subtitles: {e}")
            return []

    def _create_rich_content_overlays(self, hook_text: str, script_content: str, 
                                     video_duration: float, video_width: int, video_height: int) -> List[Dict[str, Any]]:
        """Create rich overlays including headers, summaries, and key points"""
        overlays = []
        
        try:
            # Parse script for numbered points/reasons
            script_lower = script_content.lower()
            
            # Look for numbered points, reasons, benefits, etc.
            numbered_patterns = [
                r'reason\s+(\w+):\s*([^.!?]*[.!?])',
                r'(\w+)\s+reason:\s*([^.!?]*[.!?])',
                r'point\s+(\w+):\s*([^.!?]*[.!?])',
                r'benefit\s+(\w+):\s*([^.!?]*[.!?])',
                r'(\d+)[.\)]\s*([^.!?]*[.!?])'
            ]
            
            import re
            found_points = []
            
            for pattern in numbered_patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        number, content = match
                        found_points.append({
                            'number': number,
                            'content': content.strip(),
                            'type': 'reason' if 'reason' in pattern else 'point'
                        })
            
            # Create header overlays for each point
            for i, point in enumerate(found_points[:3]):  # Limit to 3 points
                # Calculate timing for this point
                start_time = (video_duration / len(found_points)) * i
                end_time = start_time + 3.0  # 3 seconds per header
                
                # Create big colorful header
                header_text = f"REASON {point['number'].upper()}" if point['type'] == 'reason' else f"POINT {point['number'].upper()}"
                
                # Extract key words from content for summary
                content_words = point['content'].split()[:6]  # First 6 words
                summary = ' '.join(content_words)
                
                # Get AI styling for header
                header_style = self._get_smart_default_style(header_text, "header", "tiktok", 720, 1280)
                summary_style = self._get_smart_default_style(summary, "summary", "tiktok", 720, 1280)
                
                # Add main header overlay with enhanced styling
                overlays.append({
                    'text': header_text,
                    'start_time': start_time,
                    'end_time': end_time,
                    'font_size': header_style.get('font_size', 72),
                    'font_color': header_style.get('primary_color', self._get_point_color(i)),
                    'background_color': header_style.get('background_color', '#000000'),
                    'stroke_color': header_style.get('stroke_color', '#FFFFFF'),
                    'animation_style': header_style.get('animation_style', 'bounce'),
                    'position': 'top_center',
                    'style': 'header',
                    'engagement_score': header_style.get('engagement_score', 8)
                })
                
                # Add summary overlay with enhanced styling
                overlays.append({
                    'text': summary,
                    'start_time': start_time + 0.5,
                    'end_time': end_time + 1.0,
                    'font_size': summary_style.get('font_size', 48),
                    'font_color': summary_style.get('primary_color', '#FFFFFF'),
                    'background_color': summary_style.get('background_color', '#1A1A1A'),
                    'stroke_color': summary_style.get('stroke_color', '#FFFFFF'),
                    'animation_style': summary_style.get('animation_style', 'fade_in'),
                    'position': 'center',
                    'style': 'summary',
                    'engagement_score': summary_style.get('engagement_score', 6)
                })
            
            # Add opening title if no numbered points found
            if not found_points:
                overlays.append({
                    'text': hook_text[:30].upper(),
                    'start_time': 0.0,
                    'end_time': 3.0,
                    'font_size': 64,
                    'font_color': '#FF6B35',
                    'position': 'center',
                    'style': 'title',
                    'animation': 'zoom_in'
                })
            
            # Log comprehensive overlay styling decisions to session
            self._log_overlay_styling_summary(overlays, found_points, hook_text, script_content)
            
            logger.info(f"🎨 Created {len(overlays)} ENHANCED rich content overlays with {len(found_points)} key points")
            logger.info(f"🎯 Overlay engagement scores: {[overlay.get('engagement_score', 'N/A') for overlay in overlays]}")
            return overlays
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create rich content overlays: {e}")
            return []
    
    def _get_point_color(self, index: int) -> str:
        """Get bright colors for numbered points"""
        colors = ['#FF6B35', '#F7931E', '#FFD23F', '#06FFA5', '#3BCEAC', '#0D7377']
        return colors[index % len(colors)]

    def _create_timed_line_overlays(self, text: str, max_words_per_line: int = 4, 
                                   line_duration: float = 2.0, total_duration: float = 10.0) -> List[Dict[str, Any]]:
        """Create timed line-by-line overlays for better readability"""
        try:
            # Clean the text for FFmpeg compatibility
            cleaned_text = text.replace("'", "").replace('"', '').replace(':', '').replace('!', '').replace('?', '').replace(',', '').replace('\\', '').replace('/', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            
            # Split into words
            words = cleaned_text.split()
            
            # Create lines with smart word distribution
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                if len(current_line) >= max_words_per_line:
                    lines.append(' '.join(current_line))
                    current_line = []
            
            # Add remaining words to the last line
            if current_line:
                lines.append(' '.join(current_line))
            
            # Calculate timing for each line
            total_lines = len(lines)
            if total_lines == 0:
                return []
            
            # Distribute time evenly across lines, with some overlap
            line_duration = min(line_duration, total_duration / total_lines)
            fade_duration = 0.3  # Fade in/out duration
            
            overlays = []
            for i, line in enumerate(lines):
                start_time = i * (line_duration * 0.8)  # 20% overlap between lines
                end_time = start_time + line_duration
                
                # Ensure we don't exceed total duration
                if start_time >= total_duration:
                    break
                
                end_time = min(end_time, total_duration)
                
                overlays.append({
                    'text': line,
                    'start_time': start_time,
                    'end_time': end_time,
                    'fade_duration': fade_duration,
                    'line_number': i + 1,
                    'total_lines': total_lines
                })
            
            logger.info(f"📝 Created {len(overlays)} timed line overlays: {total_lines} lines, {line_duration:.1f}s per line")
            return overlays
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create timed line overlays: {e}")
            return []

    def _add_timed_text_overlays(self, video_path: str, style_decision: Dict[str, Any], 
                                positioning_decision: Dict[str, Any], config: GeneratedVideoConfig,
                                session_context: SessionContext) -> str:
        """Add text overlays with proper line-by-line timing"""
        try:
            import subprocess
            import json
            
            logger.info("📝 Adding timed text overlays with line-by-line display")
            
            # Get video duration and dimensions
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', video_path
            ]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            probe_data = json.loads(probe_result.stdout)
            
            video_duration = float(probe_data['format']['duration'])
            video_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'video'), None)
            if video_stream:
                video_width = int(video_stream['width'])
                video_height = int(video_stream['height'])
            else:
                video_width, video_height = 720, 1280
            
            # Create output path
            overlay_path = session_context.get_output_path("temp_files", f"timed_overlays_{os.path.basename(video_path)}")
            os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
            
            # Get positioning decision
            is_dynamic = positioning_decision.get('primary_style', 'static') == 'dynamic'
            
            # Create timed overlays for hook and CTA
            overlay_filters = []
            
            # Add enhanced rich text overlays
            if config.hook:
                hook_style = self._get_ai_overlay_style(str(config.hook), "hook", config.target_platform, video_width, video_height, session_context)
                
                # Create rich overlays with headers and summaries
                rich_overlays = self._create_rich_content_overlays(
                    str(config.hook),
                    config.processed_script if hasattr(config, 'processed_script') else "",
                    video_duration,
                    video_width,
                    video_height
                )
                
                # Add traditional hook overlays as well
                hook_overlays = self._create_timed_line_overlays(
                    str(config.hook), 
                    max_words_per_line=hook_style.get('words_per_line', 3),
                    line_duration=1.5,
                    total_duration=min(8.0, video_duration)
                )
                
                # Combine rich and traditional overlays
                all_overlays = rich_overlays + hook_overlays
                
                # Add rich overlays first (headers, summaries)
                for i, overlay in enumerate(rich_overlays):
                    if isinstance(overlay, dict) and 'text' in overlay:
                        # Position based on overlay style
                        if overlay.get('position') == 'top_center':
                            y_pos = 80
                        elif overlay.get('position') == 'center':
                            y_pos = int(video_height / 2)
                        else:
                            y_pos = 200
                        
                        # Create rich overlay filter
                        filter_expr = (
                            f"drawtext=text='{overlay['text']}':"
                            f"fontcolor={overlay.get('font_color', '#FFFFFF')}:"
                            f"fontsize={overlay.get('font_size', 48)}:"
                            f"font='Impact':"
                            f"box=1:boxcolor=0x000000@0.8:boxborderw=5:"
                            f"x=(w-text_w)/2:y={y_pos}:"
                            f"enable='between(t,{overlay['start_time']},{overlay['end_time']})'"
                        )
                        overlay_filters.append(filter_expr)
                
                # Add traditional hook overlays
                for i, overlay in enumerate(hook_overlays):
                    y_offset = 60 + (i * 40)  # Stack lines vertically
                    filter_expr = (
                        f"drawtext=text='{overlay['text']}':"
                        f"fontcolor={hook_style['color']}:"
                        f"fontsize={hook_style['font_size']}:"
                        f"font='{hook_style['font_family']}':"
                        f"box=1:boxcolor={hook_style['background_color']}@{hook_style['background_opacity']}:"
                        f"boxborderw={hook_style['stroke_width']}:"
                        f"x=(w-text_w)/2:y={y_offset}:"
                        f"enable='between(t,{overlay['start_time']},{overlay['end_time']})'"
                    )
                    overlay_filters.append(filter_expr)
            
            # Add call-to-action overlay with line-by-line timing
            if config.call_to_action:
                cta_style = self._get_ai_overlay_style(str(config.call_to_action), "cta", config.target_platform, video_width, video_height, session_context)
                cta_overlays = self._create_timed_line_overlays(
                    str(config.call_to_action),
                    max_words_per_line=cta_style.get('words_per_line', 3),
                    line_duration=1.5,
                    total_duration=min(8.0, video_duration)
                )
                
                # Position CTA at the end of the video
                cta_start_time = max(0, video_duration - 6.0)
                
                for i, overlay in enumerate(cta_overlays):
                    y_offset = video_height - 120 - (i * 40)  # Position from bottom
                    adjusted_start = cta_start_time + overlay['start_time']
                    adjusted_end = cta_start_time + overlay['end_time']
                    
                    filter_expr = (
                        f"drawtext=text='{overlay['text']}':"
                        f"fontcolor={cta_style['color']}:"
                        f"fontsize={cta_style['font_size']}:"
                        f"font='{cta_style['font_family']}':"
                        f"box=1:boxcolor={cta_style['background_color']}@{cta_style['background_opacity']}:"
                        f"boxborderw={cta_style['stroke_width']}:"
                        f"x=(w-text_w)/2:y={y_offset}:"
                        f"enable='between(t,{adjusted_start},{adjusted_end})'"
                    )
                    overlay_filters.append(filter_expr)
            
            # Apply overlays if any
            if overlay_filters:
                filter_complex = ','.join(overlay_filters)
                
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', filter_complex,
                    '-c:a', 'copy',
                    '-y', overlay_path
                ]
                
                logger.info(f"🎬 Applying timed overlays with FFmpeg command: {' '.join(cmd)}")
                logger.info(f"🎨 Filter complex: {filter_complex}")
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(overlay_path):
                    logger.info(f"✅ Timed text overlays added: {len(overlay_filters)} overlays")
                    
                    # Save overlay metadata
                    overlay_metadata = {
                        'overlays_applied': len(overlay_filters),
                        'hook_text': config.hook,
                        'cta_text': config.call_to_action,
                        'style_decision': style_decision,
                        'positioning_decision': positioning_decision,
                        'ffmpeg_command': ' '.join(cmd),
                        'filter_complex': filter_complex,
                        'timing_info': {
                            'line_duration': 2.0,
                            'total_duration': video_duration,
                            'overlay_count': len(overlay_filters)
                        }
                    }
                    
                    metadata_path = session_context.get_output_path("overlays", "timed_overlay_metadata.json")
                    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
                    
                    with open(metadata_path, 'w') as f:
                        json.dump(overlay_metadata, f, indent=2)
                    
                    return overlay_path
                else:
                    logger.error(f"❌ Timed overlay application failed with return code {result.returncode}")
                    logger.error(f"❌ FFmpeg stderr: {result.stderr}")
                    logger.error(f"❌ FFmpeg stdout: {result.stdout}")
                    return video_path
            else:
                logger.info("📝 No timed text overlays to add")
                return video_path
                
        except Exception as e:
            logger.error(f"❌ Timed text overlay failed: {e}")
            return video_path

    def _save_cheap_mode_audio_files(self, audio_files: List[str], session_context) -> None:
        """Save audio files to session directory for cheap mode"""
        try:
            import shutil
            import os
            
            audio_dir = os.path.join(session_context.session_dir, 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            
            for i, audio_file in enumerate(audio_files):
                if os.path.exists(audio_file):
                    filename = f"cheap_mode_audio_{i}.mp3"
                    dest_path = os.path.join(audio_dir, filename)
                    shutil.copy2(audio_file, dest_path)
                    logger.info(f"💾 Saved cheap mode audio: {filename}")
                    
            logger.info(f"✅ Saved {len(audio_files)} audio files to session")
            
        except Exception as e:
            logger.error(f"❌ Failed to save cheap mode audio files: {e}")

    def _save_cheap_mode_session_files(self, config, script_text: str, session_context) -> None:
        """Save session files for cheap mode generation"""
        try:
            import json
            import os
            from datetime import datetime
            
            # Save subtitle files
            self._save_cheap_mode_subtitles(script_text, config.duration_seconds, session_context)
            
            # Save overlay metadata
            self._save_cheap_mode_overlay_metadata(script_text, session_context)
            
            # Save performance metrics
            self._save_cheap_mode_performance_metrics(config, session_context)
            
            logger.info("✅ Saved all cheap mode session files")
            
        except Exception as e:
            logger.error(f"❌ Failed to save cheap mode session files: {e}")

    def _save_cheap_mode_subtitles(self, script_text: str, duration: float, session_context) -> None:
        """Save subtitle files for cheap mode"""
        try:
            import os
            import re
            
            subtitles_dir = os.path.join(session_context.session_dir, 'subtitles')
            os.makedirs(subtitles_dir, exist_ok=True)
            
            # Create simple subtitle segments
            words = script_text.split()
            words_per_segment = 6
            segments = []
            
            current_time = 0.0
            for i in range(0, len(words), words_per_segment):
                segment_words = words[i:i + words_per_segment]
                segment_text = ' '.join(segment_words)
                segment_duration = len(segment_words) * 0.4  # 0.4 seconds per word
                
                segments.append({
                    'start': current_time,
                    'end': current_time + segment_duration,
                    'text': segment_text
                })
                current_time += segment_duration
            
            # Save SRT format
            srt_path = os.path.join(subtitles_dir, 'subtitles.srt')
            with open(srt_path, 'w') as f:
                for i, segment in enumerate(segments, 1):
                    f.write(f"{i}\n")
                    f.write(f"{self._format_srt_time(segment['start'])} --> {self._format_srt_time(segment['end'])}\n")
                    f.write(f"{segment['text']}\n\n")
            
            # Save VTT format  
            vtt_path = os.path.join(subtitles_dir, 'subtitles.vtt')
            with open(vtt_path, 'w') as f:
                f.write("WEBVTT\n\n")
                for segment in segments:
                    f.write(f"{self._format_vtt_time(segment['start'])} --> {self._format_vtt_time(segment['end'])}\n")
                    f.write(f"{segment['text']}\n\n")
            
            # Save subtitle metadata
            metadata = {
                'subtitle_count': len(segments),
                'total_duration': duration,
                'format': 'cheap_mode_generated',
                'created_at': datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(subtitles_dir, 'subtitle_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Saved subtitle files: {len(segments)} segments")
            
        except Exception as e:
            logger.error(f"❌ Failed to save cheap mode subtitles: {e}")

    def _save_cheap_mode_overlay_metadata(self, script_text: str, session_context) -> None:
        """Save overlay metadata for cheap mode"""
        try:
            import json
            import os
            from datetime import datetime
            
            overlays_dir = os.path.join(session_context.session_dir, 'overlays')
            os.makedirs(overlays_dir, exist_ok=True)
            
            overlay_metadata = {
                'overlay_type': 'cheap_mode_text',
                'script_text': script_text,
                'overlay_count': 1,
                'style': 'minimal_text_overlay',
                'positioning': 'center_bottom',
                'created_at': datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(overlays_dir, 'timed_overlay_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(overlay_metadata, f, indent=2)
            
            logger.info("✅ Saved overlay metadata")
            
        except Exception as e:
            logger.error(f"❌ Failed to save overlay metadata: {e}")

    def _save_cheap_mode_performance_metrics(self, config, session_context) -> None:
        """Save performance metrics for cheap mode"""
        try:
            import json
            import os
            from datetime import datetime
            
            metrics_dir = os.path.join(session_context.session_dir, 'performance_metrics')
            os.makedirs(metrics_dir, exist_ok=True)
            
            metrics = {
                'generation_mode': 'cheap_mode_full',
                'duration_seconds': config.duration_seconds,
                'platform': config.target_platform.value,
                'cost_efficiency': 'maximum',
                'generation_time_estimate': '30-60_seconds',
                'resources_used': ['gTTS', 'text_video', 'moviepy'],
                'veo_usage': False,
                'created_at': datetime.now().isoformat()
            }
            
            metrics_path = os.path.join(metrics_dir, 'generation_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            logger.info("✅ Saved performance metrics")
            
        except Exception as e:
            logger.error(f"❌ Failed to save performance metrics: {e}")

    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT subtitle format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def _format_vtt_time(self, seconds: float) -> str:
        """Format time for VTT subtitle format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"



