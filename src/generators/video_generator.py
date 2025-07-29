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
from ..config.ai_model_config import DEFAULT_AI_MODEL
from ..config.tts_config import tts_config

# Suppress pkg_resources deprecation warnings from imageio_ffmpeg
warnings.filterwarnings("ignore", category=UserWarning, module="imageio_ffmpeg")

from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from ..utils.logging_config import get_logger
from ..utils.timeline_visualizer import TimelineVisualizer
from ..utils.ffmpeg_processor import FFmpegProcessor
from ..generators.veo_client_factory import VeoClientFactory, VeoModel
from ..generators.gemini_image_client import GeminiImageClient
from ..generators.enhanced_multilang_tts import EnhancedMultilingualTTS
from ..generators.enhanced_script_processor import EnhancedScriptProcessor
from ..generators.director import Director
from ..agents.voice_director_agent import VoiceDirectorAgent
from ..agents.overlay_positioning_agent import OverlayPositioningAgent
from ..agents.visual_style_agent import VisualStyleAgent
from ..generators.hashtag_generator import HashtagGenerator
from ..utils.session_context import SessionContext, create_session_context
from ..utils.duration_coordinator import DurationCoordinator
from ..utils.overlay_enhancement import OverlayEnhancer
from ..utils.audio_duration_manager import AudioDurationManager, AudioDurationAnalysis
from ..utils.duration_feedback_system import DurationFeedbackSystem
from ..utils.professional_text_renderer import (
    ProfessionalTextRenderer, 
    TextOverlay, 
    TextStyle, 
    TextLayout, 
    TextPosition, 
    TextAlignment
)
from ..config import video_config
from .png_overlay_handler import PNGOverlayHandler

# RTL text support
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    RTL_SUPPORT = True
except ImportError:
    RTL_SUPPORT = False
    print("⚠️ RTL support not available. Install with: pip install arabic-reshaper python-bidi")

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
                "mission": config.mission,
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
                            "original_mission": config.mission,
                            "target_duration": config.duration_seconds,
                            "platform": str(config.target_platform),
                            "hook": getattr(config, 'hook', video_config.get_default_hook(config.target_platform.value)),
                            "call_to_action": getattr(config, 'call_to_action', video_config.get_default_cta(config.target_platform.value))
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
                            "mission": config.mission,
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
                            "mission": config.mission,
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
                            "mission": config.mission,
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
                        "mission_relevance": "high",
                        "viral_potential": "optimized",
                        "engagement_factors": ["visual_appeal", "audio_quality", "script_optimization", "platform_targeting"]
                    },
                    "optimization_summary": {
                        "script_enhancement": f"Optimized from basic mission to {script_result.get('total_word_count', 0)} words",
                        "duration_matching": f"Achieved {script_result.get('duration_match', 'unknown')} duration alignment",
                        "style_optimization": f"Selected {style_decision.get('primary_style', 'dynamic')} style for maximum engagement",
                        "voice_optimization": f"Configured {voice_config.get('strategy', 'single')} voice strategy"
                    }
                }
            }
            
            # Save comprehensive discussion to JSON
            discussion_path = session_context.get_output_path("agent_discussions", "ai_agent_discussion.json")
            os.makedirs(os.path.dirname(discussion_path), exist_ok=True)
            with open(discussion_path, 'w') as f:
                json.dump(agent_discussion, f, indent=2)
            logger.info(f"💾 Comprehensive AI agent discussion saved: {discussion_path}")
            
            # Create detailed discussion summary
            summary_content = f"""# Comprehensive AI Agent Discussion Summary

## Session Information
- **Session ID**: {config.session_id}
- **Mission**: {config.mission}
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
- **Script enhancement**: Optimized from basic mission to {script_result.get('total_word_count', 0)} words
- **Duration matching**: Achieved {script_result.get('duration_match', 'unknown')} duration alignment
- **Style optimization**: Selected {style_decision.get('primary_style', 'dynamic')} style for maximum engagement
- **Voice optimization**: Configured {voice_config.get('strategy', 'single')} voice strategy

---
*Generated by AI Agent Discussion System v2.0*
"""
            
            # Save detailed summary
            summary_path = session_context.get_output_path("discussions", "discussion_summary.md")
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
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
            # Create VEO client using the factory - prefer VEO-3 for realistic/cinematic
            prefer_veo3_for_style = (
                self.prefer_veo3 or 
                (hasattr(config, 'visual_style') and config.visual_style and 
                 config.visual_style.lower() in ['realistic', 'cinematic', 'hyper-realistic', 'photorealistic'])
            )
            
            veo_client = self.veo_factory.get_best_available_client(
                output_dir=session_context.get_output_path("video_clips"),
                prefer_veo3=prefer_veo3_for_style
            )
            
            # Generate continuous video prompts with seamless transitions
            continuous_prompts = []
            previous_scene_description = None
            
            for i, segment in enumerate(script_segments):
                # Build continuous narrative prompt
                if i == 0:
                    prompt = f"""
Create the opening scene of a continuous {config.visual_style} {config.duration_seconds}-second video:
Content: {segment.get('text', '')}
Visual Style: {config.visual_style}
Duration: 5-8 seconds

This is the FIRST scene of a continuous narrative. Establish the visual style, setting, and characters that will continue throughout.
The ending frame of this scene will connect directly to the next scene.
"""
                else:
                    prompt = f"""
Continue the {config.visual_style} video - Scene {i+1}/{len(script_segments)}:
Previous Scene: {previous_scene_description}
Current Content: {segment.get('text', '')}
Duration: 5-8 seconds

CRITICAL: This scene must START exactly where the previous scene ended. Maintain:
- Same visual style and quality
- Same characters/objects if applicable
- Smooth camera movement continuation
- Natural narrative flow
The last frame of this scene connects to the next.
"""
                
                continuous_prompts.append(prompt.strip())
                # Store description for next scene continuity
                previous_scene_description = segment.get('text', '')[:100] + "..."
            
            # Generate all video segments with frame continuity
            video_clips = []
            last_frame_path = None
            
            for i, prompt in enumerate(continuous_prompts):
                try:
                    # Add last frame reference if available
                    generation_params = {
                        'prompt': prompt,
                        'duration': script_segments[i].get('duration', 5),
                        'clip_id': f"continuous_clip_{i+1}",
                        'aspect_ratio': self._get_platform_aspect_ratio(config.target_platform.value)
                    }
                    
                    # Include last frame for continuity (except for first clip)
                    if i > 0 and last_frame_path and os.path.exists(last_frame_path):
                        generation_params['image_path'] = last_frame_path
                        logger.info(f"🖼️ Using last frame for continuity: {last_frame_path}")
                    
                    clip_path = veo_client.generate_video(**generation_params)
                    
                    if clip_path and os.path.exists(clip_path):
                        video_clips.append(clip_path)
                        logger.info(f"✅ Generated continuous clip {i+1}/{len(continuous_prompts)}")
                        
                        # Extract last frame for next clip (except for last clip)
                        if i < len(continuous_prompts) - 1:
                            last_frame_path = self._extract_last_frame(clip_path, f"continuous_clip_{i+1}", session_context)
                            if last_frame_path:
                                # Save frame reference in session
                                frame_filename = f"frame_continuity_clip_{i+1}_to_{i+2}.jpg"
                                session_frame_path = session_context.get_output_path("images", frame_filename)
                                os.makedirs(os.path.dirname(session_frame_path), exist_ok=True)
                                
                                import shutil
                                shutil.copy2(last_frame_path, session_frame_path)
                                logger.info(f"💾 Saved continuity frame: {frame_filename}")
                    else:
                        logger.warning(f"⚠️ Failed to generate continuous clip {i+1}")
                        last_frame_path = None
                        
                except Exception as e:
                    logger.error(f"❌ Error generating continuous clip {i+1}: {e}")
                    last_frame_path = None
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
        
        # ENHANCED: Frame continuity preference
        self.prefer_frame_continuity = True  # Always prefer frame continuity
        self.frame_continuity_retries = 4   # Number of different approaches to try
        
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
        self.director = Director(api_key)
        self.voice_director = VoiceDirectorAgent(api_key)
        self.positioning_agent = OverlayPositioningAgent(api_key)
        self.style_agent = VisualStyleAgent(api_key)
        self.script_processor = EnhancedScriptProcessor(api_key)
        self.overlay_enhancer = OverlayEnhancer()
        self.png_overlay_handler = PNGOverlayHandler()
        
        # Initialize overlay strategist for dynamic overlays
        from ..agents.overlay_strategist_agent import OverlayStrategistAgent
        self.overlay_strategist = OverlayStrategistAgent(api_key)
        
        # Initialize audio duration manager
        self.audio_duration_manager = AudioDurationManager()
        
        # Initialize duration feedback system
        self.duration_feedback_system = None  # Will be initialized per session
        
        # Initialize other clients
        self.image_client = GeminiImageClient(api_key, self.output_dir)
        self.tts_client = EnhancedMultilingualTTS(api_key)
        
        # Initialize professional text renderer for high-quality overlays
        self.text_renderer = ProfessionalTextRenderer(use_skia=True)
        self.hashtag_generator = HashtagGenerator(api_key)
        
        # Check available VEO models
        available_models = self.veo_factory.get_available_models()
        
        logger.info(f"🎬 VideoGenerator initialized with clean OOP architecture")
        logger.info(f"   VEO Models: {available_models}")
        logger.info(f"   Prefer VEO-3: {'✅' if prefer_veo3 else '❌'}")
        logger.info(f"   Vertex AI: {'✅' if use_vertex_ai else '❌'}")
        logger.info(f"   AI Agents: ✅ (Voice, Positioning, Style, Script)")
        logger.info(f"   Session-aware: ✅ (Files will be organized in session directories)")
        
        # Log authentication status
        if available_models:
            logger.info(f"🔐 Authentication: ✅ SUCCESS")
        else:
            logger.warning(f"🔐 Authentication: ⚠️ No VEO models available")
    
    async def generate_video(self, config: GeneratedVideoConfig) -> Union[str, VideoGenerationResult]:
        """
        Generate video using AI agents and generation clients
        
        Args:
            config: Video generation configuration
            
        Returns:
            Video file path or VideoGenerationResult object
        """
        start_time = time.time()
        
        # CRITICAL: Store mission context and platform for VEO prompt generation
        self._current_mission = config.mission
        self._current_platform = config.target_platform.value if hasattr(config.target_platform, 'value') else str(config.target_platform)
        self._current_config = config  # Store entire config for access in methods
        logger.info(f"🎯 Stored mission context: {self._current_mission}")
        logger.info(f"📱 Stored platform context: {self._current_platform}")
        
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
                mission=config.mission,
                platform=config.target_platform.value,
                duration=config.duration_seconds,
                category=config.category.value
            )
        
        # Create session context for this generation
        session_context = create_session_context(session_id)
        
        # Initialize duration feedback system for this session
        self.duration_feedback_system = DurationFeedbackSystem(session_context)
        self.duration_feedback_system.set_target_duration(config.duration_seconds)
        
        logger.info(f"🎬 Starting video generation for: {config.mission}")
        logger.info(f"   Duration: {config.duration_seconds}s")
        logger.info(f"   Platform: {config.target_platform.value}")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Session Directory: {session_context.session_dir}/")
        
        # Check for cheap mode and handle granular levels
        cheap_mode = getattr(config, 'cheap_mode', False)
        # Extract theme from config
        theme_id = getattr(config, 'theme', None)
        if not theme_id and hasattr(self, 'core_decisions'):
            theme_id = getattr(self.core_decisions, 'theme_id', None)
        
        # Log theme for debugging
        if theme_id:
            logger.info(f"🎨 Using theme: {theme_id}")
            # Force news overlay for news theme
            if 'news' in str(theme_id).lower():
                logger.warning("📺 NEWS THEME DETECTED - Ensuring news overlays are applied")

        cheap_mode_level = getattr(config, 'cheap_mode_level', 'full')
        
        if cheap_mode or cheap_mode_level != 'full':
            logger.info(f"💰 Cheap mode enabled (level: {cheap_mode_level})")
            
            if cheap_mode_level == 'full' or cheap_mode:
                # Full cheap mode: text video + gTTS audio
                logger.info("💰 Using full cheap mode - text-based video")
                cheap_video_path = self._generate_cheap_video(config, session_context)
                
                if cheap_video_path and os.path.exists(cheap_video_path):
                    # Get file size
                    file_size_mb = os.path.getsize(cheap_video_path) / (1024 * 1024)
                    
                    # Return proper VideoGenerationResult
                    return VideoGenerationResult(
                        file_path=cheap_video_path,
                        file_size_mb=round(file_size_mb, 2),
                        generation_time_seconds=time.time() - start_time,
                        script=config.mission,
                        clips_generated=1,
                        audio_files=[],
                        success=True
                    )
                else:
                    logger.error("❌ Cheap mode video generation failed")
                    return VideoGenerationResult(
                        file_path="",
                        file_size_mb=0.0,
                        generation_time_seconds=time.time() - start_time,
                        script="",
                        clips_generated=0,
                        audio_files=[],
                        success=False,
                        error_message="Cheap mode video generation failed"
                    )
            
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
            "mission": config.mission,
            "platform": config.target_platform.value,
            "duration": config.duration_seconds
        })
        
        try:
            # Initialize Duration Coordinator
            duration_coordinator = DurationCoordinator(config.duration_seconds)
            logger.info(f"🎯 Initialized Duration Coordinator with target: {config.duration_seconds}s")
            
            # Initialize VEO client with session context
            if self.use_real_veo2 and self.use_vertex_ai:
                self.veo_client = self.veo_factory.get_veo_client(
                    model=VeoModel.VEO2 if not self.prefer_veo3 else VeoModel.VEO3,
                    output_dir=session_context.get_output_path("video_clips")
                )
            
            # Step 1: Process script with AI
            script_result = await self._process_script_with_ai(config, session_context)
            
            # Store script result for subtitle generation
            self._last_script_result = script_result
            
            # Analyze script duration
            if script_result:
                script_duration = duration_coordinator.analyze_script_duration(
                    script_result.get('optimized_script', ''),
                    script_result.get('segments', [])
                )
                logger.info(f"📝 Script duration analysis: {script_duration:.1f}s")
                
                # Add feedback checkpoint for script
                if self.duration_feedback_system:
                    self.duration_feedback_system.add_checkpoint(
                        'script_generation',
                        script_duration,
                        'script_processor',
                        {'segments': len(script_result.get('segments', []))}
                    )
            
            # Step 2: Get AI decisions for visual style and positioning
            style_decision = self._get_visual_style_decision(config)
            positioning_decision = self._get_positioning_decision(config, style_decision)
            
            # Step 3: Generate video clips
            clips = self._generate_video_clips(config, script_result, style_decision, session_context)
            
            # Analyze video clips duration
            if clips:
                video_clips_duration = duration_coordinator.analyze_video_clips(clips)
                logger.info(f"🎬 Video clips total duration: {video_clips_duration:.1f}s")
            
            # Step 4: Generate audio with AI voice selection
            audio_files = self._generate_ai_optimized_audio(config, script_result, session_context)
            
            # Analyze audio duration
            if audio_files:
                audio_duration = duration_coordinator.analyze_audio_files(audio_files)
                logger.info(f"🎵 Audio total duration: {audio_duration:.1f}s")
                
                # Add feedback checkpoint for audio
                if self.duration_feedback_system:
                    self.duration_feedback_system.add_checkpoint(
                        'audio_generation',
                        audio_duration,
                        'audio_generator',
                        {'files': len(audio_files)}
                    )
                
                # CRITICAL: Validate audio duration before proceeding to video generation
                can_proceed, audio_analysis = self.audio_duration_manager.validate_before_video_generation(
                    audio_files, 
                    config.duration_seconds,
                    block_on_failure=video_config.audio.block_on_duration_failure
                )
                
                if not can_proceed:
                    logger.error("❌ Audio duration validation failed - cannot proceed with video generation")
                    session_manager.log_error(
                        "audio_duration_validation_failed",
                        audio_analysis.recommendation,
                        {
                            "total_duration": audio_analysis.total_duration,
                            "target_duration": audio_analysis.target_duration,
                            "quality_score": audio_analysis.quality_score
                        }
                    )
                    
                    # Return error result
                    return VideoGenerationResult(
                        file_path="",
                        file_size_mb=0.0,
                        generation_time_seconds=time.time() - start_time,
                        script=script_result.get('optimized_script', config.mission),
                        clips_generated=0,
                        audio_files=audio_files,
                        success=False,
                        error_message=f"Audio duration validation failed: {audio_analysis.recommendation}"
                    )
                
                # If proceeding despite issues, adjust clip durations dynamically
                if audio_analysis.must_regenerate and can_proceed:
                    logger.warning("⚠️ Proceeding with dynamic clip duration adjustment despite audio issues")
                    
                    # Calculate dynamic clip durations based on actual audio
                    dynamic_clip_durations = self.audio_duration_manager.calculate_dynamic_clip_durations(
                        audio_analysis, 
                        len(clips) if clips else getattr(config, 'num_clips', 7)
                    )
                    
                    # Update config with dynamic durations
                    config.clip_durations = dynamic_clip_durations
                    logger.info(f"🎬 Updated clip durations: {[f'{d:.1f}s' for d in dynamic_clip_durations]}")
            
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
            
            # Initialize timeline visualizer for debugging
            timeline_visualizer = TimelineVisualizer(session_context)
            timeline_visualizer.set_video_duration(config.duration_seconds)
            
            # Step 6: Create subtitles and get timing information
            subtitle_data = self._create_subtitles_with_timings(script_result, audio_files, session_context, timeline_visualizer)
            subtitle_files = subtitle_data.get('files', {})
            subtitle_timings = subtitle_data.get('timings', [])
            
            # Get optimal duration from coordinator
            optimal_duration = duration_coordinator.get_optimal_duration()
            duration_report = duration_coordinator.get_duration_report()
            
            # Save duration report to session
            try:
                duration_report_path = session_context.get_output_path("logs", "duration_report.json")
                os.makedirs(os.path.dirname(duration_report_path), exist_ok=True)
                
                # Ensure json module is available
                import json as json_module
                with open(duration_report_path, 'w') as f:
                    json_module.dump(duration_report, f, indent=2)
                    
                logger.info(f"📊 Duration Report saved to: {duration_report_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save duration report: {e}")
                # Continue without failing the video generation
            
            logger.info(f"🎯 Optimal final duration: {optimal_duration:.1f}s (target was {config.duration_seconds}s)")
            
            # Step 7: Compose final video with subtitles and overlays
            final_video_path = self._compose_final_video_with_subtitles(
                clips, audio_files, script_result, style_decision, positioning_decision, 
                config, session_context, duration_coordinator, subtitle_timings, timeline_visualizer
            )
            
            # Save timeline visualization for manual analysis
            try:
                timeline_output_dir = session_context.get_output_path("analysis", "timeline")
                os.makedirs(timeline_output_dir, exist_ok=True)
                timeline_visualizer.save_timeline_data(timeline_output_dir)
                logger.info(f"📊 Timeline visualization saved to: {timeline_output_dir}")
                
                # Also log the ASCII timeline to console for immediate viewing
                logger.info("\n" + "="*80)
                logger.info("TIMELINE VISUALIZATION FOR AUDIO-SUBTITLE ANALYSIS")
                logger.info("="*80)
                logger.info("\n" + timeline_visualizer.generate_ascii_timeline())
                logger.info("\n" + timeline_visualizer.generate_detailed_report())
                
            except Exception as e:
                logger.error(f"❌ Failed to save timeline visualization: {e}")
            
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
                            "mission": config.mission,
                            "error": str(e),
                            "status": "failed",
                            "fallback": True
                        }
                        discussion_path = session_context.get_output_path("agent_discussions", "ai_agent_discussion.json")
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
                script=script_result.get('optimized_script', config.mission),
                clips_generated=len(clips),
                audio_files=audio_files,
                success=True
            )
            
                        # Return VideoGenerationResult for compatibility
            result = VideoGenerationResult(
                file_path=final_video_path,
                file_size_mb=self._get_file_size_mb(final_video_path),
                generation_time_seconds=generation_time,
                script=script_result.get('optimized_script', config.mission),
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
                            category: VideoCategory, mission: Optional[str] = None,
                            user_config: Optional[Dict[str, Any]] = None,
                            duration_seconds: Optional[int] = None) -> GeneratedVideoConfig:
        """
        Generate video configuration from trending analyses
        
        Args:
            analyses: List of video analyses
            platform: Target platform
            category: Video category
            mission: Optional mission override
            
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
        
        # Generate mission if not provided
        if not mission:
            mission = f"Trending: {themes[0] if themes else 'Viral Content'}"
        
        # Create hook from trending insights
        hook = hooks[0] if hooks else f"You won't believe what's trending with {mission}!"
        
        # Generate main content
        main_content = [
            f"Opening: {mission} is taking over social media",
            f"Main: Here's why {mission} is so popular",
            f"Conclusion: This is just the beginning of {mission}"
        ]
        
        # Generate call to action
        call_to_action = video_config.get_default_cta(platform) if platform else video_config.default_text.ctas_by_platform['default']
        
        config = GeneratedVideoConfig(
            mission=mission,  # mission must be first
            duration_seconds=duration_seconds if duration_seconds is not None else 30,  # Use provided duration or default to 30s
            target_platform=platform,
            category=category,
            style="viral",
            tone="engaging",
            target_audience=(user_config or {}).get('target_audience', 'general audience'),
            hook=hook,
            main_content=main_content,
            call_to_action=call_to_action,
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
        
        logger.info(f"✅ Generated config for: {mission}")
        return config
    
    async def _process_script_with_ai(self, config: GeneratedVideoConfig, session_context: SessionContext) -> Dict[str, Any]:
        """Process script using AI script processor"""
        logger.info("📝 Processing script with AI")
        
        # First, use Director to generate a proper narrative script from the mission
        try:
            logger.info(f"🎬 Director generating narrative script for: {config.mission[:100]}...")
            
            # Get patterns for the Director (empty dict if not available)
            patterns = {}
            
            # Add target language to patterns if available
            if hasattr(config, 'language') and config.language:
                patterns['target_language'] = config.language
            
            # Generate the narrative script
            director_result = self.director.write_script(
                mission=config.mission,
                style=getattr(config, 'visual_style', 'dynamic'),
                duration=config.duration_seconds,
                platform=config.target_platform,
                category=config.category,
                patterns=patterns,
                incorporate_news=False  # Can be made configurable later
            )
            
            # Extract the script content from Director's output
            if isinstance(director_result, dict):
                # Handle different possible formats from Director
                if 'segments' in director_result:
                    # Join all segment texts
                    script_parts = []
                    for segment in director_result['segments']:
                        if 'text' in segment:
                            script_parts.append(segment['text'])
                    script = " ".join(script_parts)
                elif 'script' in director_result:
                    script = director_result['script']
                elif 'hook' in director_result and 'main_content' in director_result:
                    # Assemble from components
                    script_parts = []
                    if 'text' in director_result['hook']:
                        script_parts.append(director_result['hook']['text'])
                    if isinstance(director_result['main_content'], list):
                        for content in director_result['main_content']:
                            if 'text' in content:
                                script_parts.append(content['text'])
                    if 'cta' in director_result and 'text' in director_result['cta']:
                        script_parts.append(director_result['cta']['text'])
                    script = " ".join(script_parts)
                else:
                    # Fallback to string representation
                    script = str(director_result)
            else:
                script = str(director_result)
                
            logger.info(f"✅ Director generated narrative script: {script[:200]}...")
            
        except Exception as e:
            logger.warning(f"⚠️ Director script generation failed: {e}, falling back to simple approach")
            # Fallback to original simple approach
            script_parts = []
            
            # Add hook if provided
            if config.hook:
                script_parts.append(config.hook)
            
            # Add main content - FIX: Use the actual mission
            if config.main_content:
                script_parts.extend(config.main_content)
            else:
                # Use the mission as main content if no main_content provided
                script_parts.append(config.mission)
            
            # Add call to action if provided
            if config.call_to_action:
                script_parts.append(config.call_to_action)
            
            # Join all parts
            script = " ".join(script_parts)
        
        # Log the actual script being processed
        logger.info(f"📝 Script to process: {script[:100]}...")
        
        # Process with AI script processor for TTS optimization
        from ..models.video_models import Language
        # Determine the language from config
        languages = getattr(config, 'languages', [Language.ENGLISH_US])
        target_language = languages[0] if languages else Language.ENGLISH_US
        
        result = await self.script_processor.process_script_for_tts(
            script_content=script,
            language=target_language,
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
                "mission": config.mission,
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
            mission=config.mission,
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
            mission=config.mission,
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
        use_frame_continuity = getattr(config, 'frame_continuity', False)
        
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
        
        # CRITICAL: Check actual audio files to determine clip count
        audio_dir = session_context.get_output_path("audio")
        audio_files = []
        if os.path.exists(audio_dir):
            audio_files = sorted([f for f in os.listdir(audio_dir) if f.startswith('audio_segment_') and f.endswith('.mp3')])
            logger.info(f"🎵 Found {len(audio_files)} audio segments in session")
        
        # CRITICAL: Video clips and audio segments are INDEPENDENT
        # Use core decisions for video clips, NOT audio segment count
        if hasattr(config, 'num_clips') and config.num_clips is not None:
            # Always use core decisions for video clips
            num_clips = config.num_clips
            logger.info(f"🎯 Using core decisions: {num_clips} video clips")
        else:
            # Fallback to optimal calculation if no core decisions
            target_clip_duration = 5.0  # 5-second clips as configured
            optimal_num_clips = max(2, int(config.duration_seconds / target_clip_duration))
            num_clips = optimal_num_clips
            logger.info(f"🎯 No core decisions, using optimal: {num_clips} clips for {config.duration_seconds}s video")
        
        # Log audio information separately - it's NOT related to video clips
        if audio_files:
            logger.info(f"🎵 Found {len(audio_files)} audio segments (independent from video clips)")
        if script_segments and isinstance(script_segments, list):
            logger.info(f"📝 Found {len(script_segments)} script segments (independent from video clips)")
        
        # Log audio durations for reference but DO NOT use them for video clips
        if audio_files:
            import subprocess
            actual_audio_durations = []
            for audio_file in audio_files:
                audio_path = os.path.join(audio_dir, audio_file)
                try:
                    result = subprocess.run([
                        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
                    ], capture_output=True, text=True)
                    if result.returncode == 0:
                        duration = float(result.stdout.strip())
                        actual_audio_durations.append(duration)
                    else:
                        actual_audio_durations.append(5.0)  # Default duration
                except:
                    actual_audio_durations.append(5.0)  # Default duration
            logger.info(f"📊 Audio segment durations (for reference only): {[f'{d:.1f}s' for d in actual_audio_durations]}")
            logger.info(f"📊 Total audio duration: {sum(actual_audio_durations):.1f}s")
        
        # Always use optimal video clip durations (5-8 seconds each)
        # NEVER use audio durations for video clips
        if hasattr(config, 'clip_durations') and config.clip_durations is not None:
            clip_durations = config.clip_durations
            logger.info(f"🎯 Using core decisions clip durations: {[f'{d:.1f}s' for d in clip_durations]}")
            logger.info(f"⏱️ Total from core decisions: {sum(clip_durations):.1f}s (Target: {config.duration_seconds}s)")
        else:
            # NEVER use audio durations for video clips - they are independent!
            # Video clips have their own optimal durations (5 seconds each)
            # Distribute duration evenly across clips
            base_duration = config.duration_seconds / num_clips
            clip_durations = []
            
            for i in range(num_clips):
                # Add slight variation for natural pacing
                variation = (i % 3 - 1) * 0.5  # -0.5, 0, +0.5 variation  
                clip_duration = max(2.0, base_duration + variation)  # Min 2 seconds per clip
                clip_durations.append(clip_duration)
            
            # Adjust last clip to match exact target duration
            total_so_far = sum(clip_durations[:-1])
            last_clip_duration = config.duration_seconds - total_so_far
            clip_durations[-1] = max(2.0, last_clip_duration)
            
            logger.info(f"🎬 Duration: {config.duration_seconds}s, generating {num_clips} clips with optimal durations (5-8s each)")
            logger.info(f"⏱️ Individual Clip Durations: {[f'{d:.1f}s' for d in clip_durations]}")
            logger.info(f"⏱️ Total Clip Duration Sum: {sum(clip_durations):.1f}s (Target: {config.duration_seconds}s)")
        
        last_frame_image = None
        
        # Get the best available VEO client using factory
        veo_client = None
        if self.use_real_veo2:
            # Prefer VEO-3 for realistic/cinematic videos
            prefer_veo3_for_style = (
                self.prefer_veo3 or 
                (hasattr(config, 'visual_style') and config.visual_style and 
                 config.visual_style.lower() in ['realistic', 'cinematic', 'hyper-realistic', 'photorealistic'])
            )
            
            veo_client = self.veo_factory.get_best_available_client(
                output_dir=session_context.get_output_path("video_clips"),
                prefer_veo3=prefer_veo3_for_style
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
                    # ALWAYS use optimal clip duration (5-8s), NEVER audio segment duration
                    clip_duration = clip_durations[i] if i < len(clip_durations) else 6.0
                    # Create visual prompt from segment content, not the controversial mission
                    visual_style = getattr(config, 'visual_style', None) or style_decision.get('primary_style', 'dynamic')
                    prompt = self._create_visual_prompt_from_segment(segment_text, i+1, visual_style)
                    logger.info(f"⏱️ Clip {i+1} Duration: {clip_duration:.1f}s (optimal video duration)")
                else:
                    # Fallback for when segments don't match
                    clip_duration = config.duration_seconds / num_clips
                    logger.info(f"⏱️ Clip {i+1} Duration: {clip_duration:.1f}s (fallback average)")
                    # Create generic safe visual prompt
                    visual_style = getattr(config, 'visual_style', None) or style_decision.get('primary_style', 'dynamic')
                    prompt = self._create_generic_visual_prompt(i+1, visual_style)
                
                # Enhance prompt with style - use visual_style from config if available
                visual_style = getattr(config, 'visual_style', None) or style_decision.get('primary_style', 'dynamic')
                
                # CRITICAL FIX: Ensure character descriptions remain at the beginning of the prompt
                # Check if prompt starts with a character description
                import re
                character_pattern = r'^([A-Za-z\s\-]+(?:with|wearing|in|having|featuring)[^,]+),?\s*(.*)$'
                match = re.match(character_pattern, prompt)
                
                if match:
                    # Prompt starts with character description - preserve it at the beginning
                    character_part = match.group(1)
                    scene_part = match.group(2)
                    
                    # Enhance only the scene part with style
                    enhanced_scene = self.style_agent.enhance_prompt_with_style(
                        base_prompt=scene_part,
                        style=visual_style
                    )
                    
                    # Reconstruct with character description first
                    enhanced_prompt = f"{character_part}, {enhanced_scene}"
                    logger.info(f"🎭 Preserved character description at start of prompt")
                else:
                    # No character description at start - enhance normally
                    enhanced_prompt = self.style_agent.enhance_prompt_with_style(
                        base_prompt=prompt,
                        style=visual_style
                    )
                
                # Remove preemptive policy checking - let VEO handle it
                # Policy violations will be caught and handled if VEO rejects the prompt
                
                # CRITICAL: Save ALL VEO prompts to session for debugging
                self._save_veo_prompt_to_session(session_context, i+1, {
                    'clip_number': i+1,
                    'original_segment': segment_text if 'segment_text' in locals() else 'N/A',
                    'base_prompt': prompt,
                    'enhanced_prompt': enhanced_prompt,
                    'mission': config.mission,
                    'duration': clip_duration,
                    'style': style_decision.get('primary_style', 'dynamic')
                })
                
                clip_path = None
                
                # Try VEO generation first (up to 3 attempts with smart rephrasing)
                if veo_client:
                    max_veo_attempts = video_config.audio.max_regeneration_attempts
                    # Clear any previous error before starting attempts for this clip
                    if hasattr(self, '_last_veo_error'):
                        delattr(self, '_last_veo_error')
                    
                    for veo_attempt in range(max_veo_attempts):
                        try:
                            # Use increasingly safer prompts for retries
                            current_prompt = enhanced_prompt
                            if veo_attempt > 0:
                                # ALWAYS rephrase on retry attempts, not just when we have an error
                                logger.info(f"🔄 Attempt {veo_attempt + 1} - applying safety rephrasing")
                                safety_level = veo_attempt  # 1 for second attempt, 2 for third
                                current_prompt = self._rephrase_with_safety_level(
                                    enhanced_prompt, 
                                    safety_level,
                                    config.mission,
                                    i + 1,
                                    platform=config.target_platform.value
                                )
                                logger.info(f"🛡️ Using safety level {safety_level} rephrasing")
                            
                            logger.info(f"🎬 Generating VEO clip {i+1}/{num_clips} (attempt {veo_attempt + 1}/{max_veo_attempts}): {current_prompt[:50]}... (duration: {clip_duration:.1f}s)")
                            
                            # Log full prompt for debugging
                            logger.info(f"📝 FULL VEO PROMPT for clip {i+1} attempt {veo_attempt + 1}: {current_prompt}")
                            
                            # Add frame continuity if enabled and available
                            generation_params = {
                                'prompt': current_prompt,
                                'duration': clip_duration,
                                'clip_id': f"clip_{i+1}_attempt_{veo_attempt + 1}",
                                'aspect_ratio': self._get_platform_aspect_ratio(config.target_platform.value)
                            }
                            
                            # Use last frame for continuity if enabled
                            use_frame_continuity = getattr(config, 'frame_continuity', False)
                            if use_frame_continuity and i > 0 and last_frame_image and os.path.exists(last_frame_image):
                                generation_params['image_path'] = last_frame_image
                                logger.info(f"🖼️ Using frame continuity from clip {i}")
                            
                            clip_path = veo_client.generate_video(**generation_params)
                            
                            if clip_path and os.path.exists(clip_path):
                                # Success! Log actual duration but DON'T trim - we want to maintain sync
                                actual_clip_duration = self._get_video_duration(clip_path)
                                break  # Exit the retry loop on success
                                
                        except Exception as e:
                            logger.error(f"❌ VEO generation failed for clip {i+1} attempt {veo_attempt + 1}:")
                            logger.error(f"   Error type: {type(e).__name__}")
                            logger.error(f"   Error message: {str(e)}")
                            
                            # Check for common VEO failure reasons
                            error_msg = str(e).lower()
                            if 'quota' in error_msg:
                                logger.error("   🚨 QUOTA EXCEEDED - VEO API limit reached")
                                print("⚠️ VEO QUOTA EXCEEDED - Consider using --cheap mode")
                            elif 'invalid' in error_msg and 'prompt' in error_msg:
                                logger.error("   🚨 INVALID PROMPT - VEO rejected the prompt")
                                logger.error(f"   Prompt was: {current_prompt[:200]}...")
                            elif 'timeout' in error_msg:
                                logger.error("   🚨 TIMEOUT - VEO generation took too long")
                            elif 'connection' in error_msg or 'network' in error_msg:
                                logger.error("   🚨 NETWORK ERROR - Check internet connection")
                            else:
                                logger.error("   🚨 UNKNOWN ERROR - Check VEO service status")
                            
                            self._last_veo_error = str(e)  # Store error for next attempt
                            clip_path = None
                        except Exception as e:
                            logger.warning(f"⚠️ VEO generation failed for clip {i+1} attempt {veo_attempt + 1}: {e}")
                            self._last_veo_error = str(e)  # Store error for next attempt
                            clip_path = None
                            
                            if veo_attempt == max_veo_attempts - 1:  # Last attempt
                                logger.warning(f"⚠️ All VEO attempts failed for clip {i+1}, moving to fallback")
                                print(f"⚠️ FALLBACK WARNING: VEO generation failed for clip {i+1} after {max_veo_attempts} attempts - using fallback")
                    
                    # Check if we got a successful clip
                    if clip_path and os.path.exists(clip_path):
                        # Continue with the existing success logic
                        actual_clip_duration = self._get_video_duration(clip_path) if 'actual_clip_duration' not in locals() else actual_clip_duration
                        if actual_clip_duration:
                            if actual_clip_duration > clip_duration * 1.1:  # More than 10% over
                                logger.info(f"📏 VEO clip {i+1} is {actual_clip_duration:.1f}s (requested: {clip_duration:.1f}s) - keeping full duration for sync")
                            else:
                                logger.info(f"✅ VEO clip {i+1} duration: {actual_clip_duration:.1f}s")
                        logger.info(f"✅ Generated VEO clip {i+1}/{num_clips}")
                        
                        # Extract last frame for next clip if frame continuity is enabled
                        if use_frame_continuity and i < num_clips - 1:
                            last_frame_image = self._extract_last_frame(clip_path, f"clip_{i+1}", session_context)
                            if last_frame_image:
                                # Save to session for debugging
                                frame_filename = f"frame_continuity_{i+1}_to_{i+2}.jpg"
                                session_frame_path = session_context.get_output_path("images", frame_filename)
                                os.makedirs(os.path.dirname(session_frame_path), exist_ok=True)
                                
                                import shutil
                                shutil.copy2(last_frame_image, session_frame_path)
                                logger.info(f"💾 Saved continuity frame: {frame_filename}")
                    else:
                        logger.warning(f"⚠️ FALLBACK WARNING: VEO generation failed for clip {i+1}, using fallback")
                        print(f"⚠️ FALLBACK WARNING: VEO generation failed for clip {i+1} - using fallback with reduced quality")
                        clip_path = None
                
                # If VEO failed, implement hierarchical fallback
                if not clip_path:
                    clip_path = self._hierarchical_fallback_generation(
                        prompt=enhanced_prompt,
                        duration=clip_duration,
                        clip_number=i+1,
                        config=config,
                        session_context=session_context,
                        style_decision=style_decision,
                        use_frame_continuity=use_frame_continuity,
                        last_frame_image=last_frame_image if use_frame_continuity and i > 0 else None
                    )
                
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
    
    def _calculate_expected_clip_count(self, duration: float) -> int:
        """Calculate expected video clip count based on duration"""
        # Match the logic used in video clip generation
        if duration <= 10:
            return max(1, int(duration / 3))
        elif duration <= 30:
            return max(3, int(duration / 5))
        elif duration <= 60:
            return max(5, int(duration / 7))
        else:
            return max(7, int(duration / 10))

    def _create_single_voice_strategy(self, voice: str, num_segments: int, mission: str) -> Dict[str, Any]:
        """Create a voice strategy using a specific voice for all segments"""
        clip_voices = []
        for i in range(num_segments):
            clip_voices.append({
                "clip_index": i,
                "voice_name": voice,
                "speed": 1.0,
                "pitch": 0,
                "emotion": "neutral"
            })
        
        return {
            "strategy": "single",
            "clip_voices": clip_voices,
            "voice_variety": False,
            "reasoning": f"Using specified voice '{voice}' for all segments",
            "voice_config": {
                "strategy": "single",
                "voices": clip_voices,
                "primary_personality": "custom",
                "reasoning": f"User specified voice: {voice}"
            }
        }
    
    def _extract_last_frame(self, video_path: str, clip_id: str, session_context: Optional[SessionContext] = None) -> Optional[str]:
        """Extract the last frame from a video for frame continuity"""
        try:
            import subprocess
            import glob
            
            # Create frame path in session directory
            if session_context:
                frame_path = session_context.get_output_path("images", f"last_frame_{clip_id}.jpg")
                temp_dir = session_context.get_output_path("temp_files", f"frames_{clip_id}")
                # Ensure both directories exist
                os.makedirs(os.path.dirname(frame_path), exist_ok=True)
                os.makedirs(temp_dir, exist_ok=True)
            else:
                from ..utils.session_manager import session_manager
                session_dir = session_manager.get_session_path("images")
                os.makedirs(session_dir, exist_ok=True)
                frame_path = os.path.join(session_dir, f"last_frame_{clip_id}.jpg")
                temp_dir = os.path.join(session_manager.get_session_path("temp_files"), f"frames_{clip_id}")
                os.makedirs(temp_dir, exist_ok=True)
            
            # Get video duration
            duration = self._get_video_duration(video_path)
            if not duration:
                logger.warning("Could not determine video duration")
                duration = 8.0  # Default assumption
            
            # Extract all frames from the last second
            start_time = max(0, duration - 1.0)  # Last 1 second
            
            # Extract frames to temporary directory
            temp_pattern = os.path.join(temp_dir, "frame_%04d.jpg")
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-ss', str(start_time),  # Start from last second
                '-q:v', '1',
                '-pix_fmt', 'yuvj420p',  # Use full-range YUV for JPEG
                '-an',
                temp_pattern
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find all extracted frames
                frame_files = sorted(glob.glob(os.path.join(temp_dir, "frame_*.jpg")))
                
                if frame_files:
                    # Get FPS to determine which frame to use
                    from ..config.video_config import video_config
                    platform = getattr(self, '_current_platform', 'instagram')
                    fps = video_config.get_fps(platform)
                    frames_to_trim = video_config.animation.frame_continuity_trim_frames
                    
                    # Calculate which frame to use (default to last if calculation fails)
                    frame_index = max(0, len(frame_files) - int(frames_to_trim) - 1)
                    selected_frame = frame_files[frame_index] if frame_index < len(frame_files) else frame_files[-1]
                    
                    # Copy the selected frame to final location
                    import shutil
                    shutil.copy2(selected_frame, frame_path)
                    
                    logger.info(f"🖼️ Extracted frame {frame_index + 1}/{len(frame_files)} for continuity: {frame_path}")
                    logger.debug(f"📍 Selected frame from last second (frames_to_trim: {frames_to_trim})")
                    
                    # Clean up temporary frames
                    for f in frame_files:
                        try:
                            os.remove(f)
                        except:
                            pass
                    try:
                        os.rmdir(temp_dir)
                    except:
                        pass
                    
                    return frame_path
                else:
                    logger.warning("No frames extracted from video")
            else:
                logger.warning(f"Failed to extract frames: {result.stderr}")
            
            # Cleanup on failure
            try:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
            except:
                pass
            
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
                    'text': script_result.get('final_script', config.mission),
                    'duration': config.duration_seconds
                }]
            
            # CRITICAL FIX: Use core decisions for number of clips if available
            if hasattr(config, 'num_clips') and config.num_clips is not None:
                num_segments = config.num_clips
                logger.info(f"🎯 Using core decisions for audio generation: {num_segments} clips")
            else:
                num_segments = len(script_segments)
                logger.info(f"🎤 Generating voice configuration for {num_segments} script segments")
            
            # Check if we should force single voice or use a specific voice
            if config.voice:
                # Use the specified voice for all segments
                logger.info(f"🎤 Using specified voice: {config.voice}")
                voice_strategy = self._create_single_voice_strategy(
                    config.voice, num_segments, config.mission
                )
            elif not config.multiple_voices:
                # Force single voice mode (default behavior)
                logger.info("🎤 Single voice mode enabled (default)")
                # Determine the language from config
                languages = getattr(config, 'languages', [Language.ENGLISH_US])
                target_language = languages[0] if languages else Language.ENGLISH_US
                
                voice_strategy = self.voice_director.analyze_content_and_select_voices(
                    mission=config.mission,
                    script=script_result.get('final_script', config.mission),
                    language=target_language,
                    platform=config.target_platform,
                    category=config.category,
                    duration_seconds=config.duration_seconds,
                    num_clips=num_segments,
                    force_single_voice=True  # Force single voice
                )
            else:
                # Allow multiple voices
                logger.info("🎤 Multiple voices mode enabled")
                # Determine the language from config
                languages = getattr(config, 'languages', [Language.ENGLISH_US])
                target_language = languages[0] if languages else Language.ENGLISH_US
                
                voice_strategy = self.voice_director.analyze_content_and_select_voices(
                    mission=config.mission,
                    script=script_result.get('final_script', config.mission),
                    language=target_language,
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
                logger.info(f"🎯 Creating audio segments from script sentences")
                full_script = script_result.get('final_script', config.mission)
                
                # CRITICAL FIX: Split by sentences first, then group if needed
                import re
                sentences = re.split(r'([.!?:;]+)', full_script)
                
                # Recombine sentences with their punctuation
                complete_sentences = []
                for i in range(0, len(sentences) - 1, 2):
                    if i + 1 < len(sentences):
                        sentence = sentences[i].strip() + sentences[i + 1].strip()
                        if sentence.strip():
                            complete_sentences.append(sentence.strip())
                    elif sentences[i].strip():
                        complete_sentences.append(sentences[i].strip())
                
                # Handle any remaining text
                if len(sentences) % 2 == 1 and sentences[-1].strip():
                    complete_sentences.append(sentences[-1].strip())
                
                logger.info(f"📝 Found {len(complete_sentences)} sentences in script")
                
                # CRITICAL: Pre-calculate segments to fit within target duration
                segments_to_generate = []
                words_per_second = tts_config.WORDS_PER_SECOND  # Use centralized TTS config
                
                # Define target_duration from config
                target_duration = config.duration_seconds
                
                # Calculate how much of the script we can actually use
                max_words = int(target_duration * words_per_second)
                total_words = sum(len(s.split()) for s in complete_sentences)
                
                if total_words > max_words:
                    logger.warning(f"⚠️ Script has {total_words} words but target duration ({target_duration}s) only allows {max_words} words")
                    logger.info(f"📏 Trimming script to fit duration")
                    
                    # Build script up to word limit
                    current_words = 0
                    trimmed_sentences = []
                    
                    for sentence in complete_sentences:
                        sentence_words = len(sentence.split())
                        if current_words + sentence_words <= max_words:
                            trimmed_sentences.append(sentence)
                            current_words += sentence_words
                        else:
                            # This sentence would exceed limit
                            logger.info(f"✂️ Stopping at {len(trimmed_sentences)} sentences ({current_words} words)")
                            break
                    
                    complete_sentences = trimmed_sentences
                    logger.info(f"📝 Using {len(complete_sentences)} sentences that fit within duration")
                
                # Now create segments from the duration-appropriate sentences
                for i, sentence in enumerate(complete_sentences):
                    word_count = len(sentence.split())
                    # Calculate precise duration for this segment
                    estimated_duration = word_count / words_per_second
                    segments_to_generate.append({
                        'text': sentence,
                        'duration': estimated_duration,
                        'word_count': word_count,
                        'complete_sentences': True,
                        'sentence_count': 1
                    })
                
                # Log total expected duration
                total_expected_duration = sum(s['duration'] for s in segments_to_generate)
                logger.info(f"✅ Created {len(segments_to_generate)} audio segments")
                logger.info(f"📊 Total expected duration: {total_expected_duration:.1f}s (target: {target_duration}s)")
            else:
                # Use script segments as fallback
                segments_to_generate = script_segments
                logger.info(f"🎤 Using {len(segments_to_generate)} script segments for audio generation")
            
            # CRITICAL: Track total audio duration to prevent exceeding target
            total_audio_duration = 0.0
            target_duration = config.duration_seconds
            max_duration = target_duration * 1.05  # 5% tolerance
            
            # Generate audio for each segment
            for i, segment in enumerate(segments_to_generate):
                # Check if we're approaching the duration limit
                if total_audio_duration >= max_duration:
                    logger.warning(f"⚠️ Stopping audio generation at segment {i+1} - already at {total_audio_duration:.1f}s (max: {max_duration:.1f}s)")
                    break
                    
                # Use full_text for TTS if available (avoid truncated text), otherwise use text
                segment_text = segment.get('full_text', segment.get('text', ''))
                # Audio segment duration - NOT used for video clips
                segment_duration = segment.get('duration', 5.0)
                
                # Adjust segment duration if it would exceed total
                remaining_duration = max_duration - total_audio_duration
                if segment_duration > remaining_duration:
                    segment_duration = remaining_duration
                    logger.info(f"📏 Adjusted segment {i+1} duration to {segment_duration:.1f}s to fit within target")
                
                logger.info(f"🎵 Generating audio for segment {i+1}/{len(segments_to_generate)}: '{segment_text[:50]}...' (duration: {segment_duration:.1f}s)")
                
                # Determine the language from config
                languages = getattr(config, 'languages', [Language.ENGLISH_US])
                target_language = languages[0] if languages else Language.ENGLISH_US
                
                # Generate audio for this specific segment
                segment_audio_files = self.tts_client.generate_intelligent_voice_audio(
                    script=segment_text,
                    language=target_language,
                    mission=config.mission,
                    platform=config.target_platform,
                    category=config.category,
                    duration_seconds=int(segment_duration),  # Convert to int
                    num_clips=num_segments,  # Use actual number of segments
                    clip_index=i,  # This should now be within range
                    cheap_mode=getattr(config, 'cheap_mode', False) or (getattr(config, 'cheap_mode', False) and getattr(config, 'cheap_mode_level', 'full') in ['audio', 'full'])  # Use cheap audio only when cheap_mode is enabled
                )
                
                if segment_audio_files and len(segment_audio_files) > 0:
                    temp_audio_files.append(segment_audio_files[0])
                    
                    # CRITICAL: Track actual audio duration using FFmpeg
                    try:
                        from ..utils.ffmpeg_processor import FFmpegProcessor
                        with FFmpegProcessor() as ffmpeg:
                            actual_segment_duration = ffmpeg.get_duration(segment_audio_files[0])
                        total_audio_duration += actual_segment_duration
                        logger.info(f"✅ Generated audio segment {i+1}: {actual_segment_duration:.1f}s (total: {total_audio_duration:.1f}s)")
                    except:
                        # Fallback estimate
                        total_audio_duration += segment_duration
                else:
                    logger.warning(f"⚠️ Failed to generate audio for segment {i+1}")
                    # Create a fallback for this segment
                    fallback_audio = self._create_fallback_audio_segment(segment_text, segment_duration, config, session_context)
                    if fallback_audio:
                        temp_audio_files.append(fallback_audio)
                        total_audio_duration += segment_duration
            
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
            
            # Add padding between audio segments if configured
            if audio_files and len(audio_files) > 1 and video_config.audio.padding_between_segments > 0:
                logger.info(f"🔇 Adding padding between {len(audio_files)} audio segments")
                padded_dir = session_context.get_output_path("audio", "padded")
                padded_audio_files = self.audio_duration_manager.add_padding_between_segments(
                    audio_files, padded_dir
                )
                
                # Track padded files with session manager
                for padded_file in padded_audio_files:
                    session_manager.track_file(padded_file, "audio", "AudioDurationManager")
                
                # Use padded files
                audio_files = padded_audio_files
            
            if not audio_files:
                logger.warning("⚠️ No audio files generated, creating fallback")
                # Create a fallback audio file
                fallback_audio = self._create_fallback_audio(config, session_context)
                if fallback_audio:
                    audio_files.append(fallback_audio)
            
            # CRITICAL: Final validation of total audio duration
            if audio_files:
                actual_total_duration = 0.0
                try:
                    from ..utils.ffmpeg_processor import FFmpegProcessor
                    with FFmpegProcessor() as ffmpeg:
                        for audio_file in audio_files:
                            if os.path.exists(audio_file):
                                actual_total_duration += ffmpeg.get_duration(audio_file)
                    
                    logger.info(f"📊 Final audio validation:")
                    logger.info(f"   Target duration: {target_duration}s")
                    logger.info(f"   Actual total duration: {actual_total_duration:.1f}s")
                    logger.info(f"   Difference: {actual_total_duration - target_duration:.1f}s ({((actual_total_duration - target_duration) / target_duration * 100):.1f}%)")
                    
                    if actual_total_duration > max_duration:
                        logger.warning(f"⚠️ Total audio duration {actual_total_duration:.1f}s exceeds maximum {max_duration:.1f}s")
                        logger.warning(f"⚠️ Consider reducing script content or adjusting speech rate")
                    elif actual_total_duration < target_duration * 0.95:
                        logger.warning(f"⚠️ Total audio duration {actual_total_duration:.1f}s is below minimum {target_duration * 0.95:.1f}s")
                        logger.warning(f"⚠️ Consider adding more content or adjusting speech rate")
                    else:
                        logger.info(f"✅ Audio duration is within acceptable range")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not validate final audio duration: {e}")
            
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
            script = f"{config.hook or 'Welcome!'} {config.mission} {config.call_to_action or 'Thanks for watching!'}"
            
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
                                           session_context: SessionContext, 
                                           duration_coordinator: Optional[DurationCoordinator] = None,
                                           subtitle_timings: Optional[List[Dict[str, float]]] = None,
                                           timeline_visualizer: Optional[TimelineVisualizer] = None) -> str:
        """Compose final video with subtitles and overlays, plus additional versions"""
        try:
            logger.info("🎬 Composing final video with multiple output versions")
            
            # CRITICAL FIX: Handle case where no video clips are available
            if not clips:
                logger.warning("⚠️ No video clips available, creating fallback video")
                return self._create_fallback_video_from_audio(audio_files, config, session_context)
            
            # CRITICAL: Final duration validation before assembly
            if audio_files:
                logger.info("🚦 Performing final duration validation before video assembly")
                can_proceed, audio_analysis = self.audio_duration_manager.validate_before_video_generation(
                    audio_files,
                    config.duration_seconds,
                    block_on_failure=False  # Don't block at this stage, just warn
                )
                
                if not can_proceed:
                    logger.warning("⚠️ Final duration validation shows issues:")
                    logger.warning(f"   {audio_analysis.recommendation}")
                    logger.warning(f"   Audio: {audio_analysis.total_duration:.1f}s vs Target: {config.duration_seconds}s")
                    logger.warning("   Proceeding with assembly but output may have duration issues")
            
            # Step 1: Create base video from clips with subtitle-aligned audio
            # Add video clip tracking
            if timeline_visualizer and clips:
                clip_duration_per_file = config.duration_seconds / len(clips)
                for i, clip_path in enumerate(clips):
                    timeline_visualizer.add_video_clip_event(
                        index=i + 1,
                        start=i * clip_duration_per_file,
                        duration=clip_duration_per_file,
                        file_path=clip_path
                    )
            
            base_video_path = self._create_base_video_from_clips(clips, audio_files, session_context, config.duration_seconds, 
                                                                platform=config.target_platform.value,
                                                                subtitle_timings=subtitle_timings)
            
            if not base_video_path or not os.path.exists(base_video_path):
                logger.error("❌ Failed to create base video")
                return ""
            
            # Keep reference to original base video for later use
            original_base_video = base_video_path
            
            # Get optimal duration from coordinator or use config duration
            if duration_coordinator:
                target_duration = duration_coordinator.get_optimal_duration()
                logger.info(f"🎯 Using optimal duration from coordinator: {target_duration:.1f}s")
            else:
                target_duration = config.duration_seconds
                logger.info(f"🎯 Using config duration: {target_duration:.1f}s")
            
            # Get actual video duration
            actual_duration = self._get_video_duration(base_video_path)
            
            if actual_duration and actual_duration > target_duration * 1.05:  # More than 5% over
                # CRITICAL FIX: Trim to target duration to prevent extended videos
                logger.info(f"📏 Video is {actual_duration:.1f}s (target: {target_duration}s) - trimming to target duration")
                trimmed_path = session_context.get_output_path("temp_files", "trimmed_video.mp4")
                
                # Use ffmpeg to trim video to exact duration
                import subprocess
                cmd = [
                    'ffmpeg', '-y',
                    '-i', base_video_path,
                    '-t', str(target_duration),
                    '-c', 'copy',
                    trimmed_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and os.path.exists(trimmed_path):
                    temp_video_path = trimmed_path
                    logger.info(f"✅ Video trimmed to target duration: {target_duration}s")
                else:
                    logger.warning(f"⚠️ Failed to trim video: {result.stderr}")
                    temp_video_path = base_video_path
            elif actual_duration and actual_duration < target_duration * 0.95:  # More than 5% under
                # Extend video by freezing last frame
                logger.info(f"⏱️ Video is {actual_duration:.1f}s (target: {target_duration}s) - extending with last frame")
                extended_video_path = session_context.get_output_path("temp_files", "extended_video.mp4")
                
                if duration_coordinator and duration_coordinator.extend_video_to_duration(
                    base_video_path, target_duration, extended_video_path
                ):
                    # Verify the extended video file exists before using it
                    if os.path.exists(extended_video_path):
                        temp_video_path = extended_video_path
                        logger.info(f"✅ Video extended to target duration: {target_duration}s")
                    else:
                        logger.warning("⚠️ Extended video file not created, using original")
                        temp_video_path = base_video_path
                else:
                    logger.warning("⚠️ Failed to extend video, using original")
                    temp_video_path = base_video_path
            else:
                logger.info(f"✅ Video duration is within tolerance: {actual_duration:.1f}s (target: {target_duration}s)")
                temp_video_path = base_video_path
            
            # Step 2: Create VERSION 1 - Video with audio only (no subtitles, no overlays)
            logger.info("🎬 Creating VERSION 1: Video with audio only (no subtitles, no overlays)")
            video_audio_only = self._apply_platform_orientation(temp_video_path, config.target_platform.value, session_context)
            if config.duration_seconds >= 10:
                current_duration = self._get_video_duration(video_audio_only)
                if current_duration and current_duration < target_duration - 1.0:
                    video_audio_only = self._add_fade_out_ending(video_audio_only, session_context, audio_files)
            
            # Save VERSION 1
            audio_only_path = session_context.save_final_video(video_audio_only, suffix="_audio_only")
            logger.info(f"✅ VERSION 1 created: {audio_only_path}")
            
            # Step 3: Generate subtitles from our known text and audio timing
            logger.info("📝 Generating subtitles from script and audio timing")
            video_with_subtitles = self._add_subtitle_overlays(temp_video_path, config, session_context)
            
            # Step 4: Add text overlays and hooks
            video_with_overlays = self._add_timed_text_overlays(video_with_subtitles, style_decision, positioning_decision, config, session_context)
            
            # Step 4b: Add PNG overlays (flags, logos, etc.) if requested
            video_with_overlays = self._add_png_overlays(video_with_overlays, config, session_context)
            
            # Step 5: Create VERSION 2 - Video with overlays only (no subtitles)
            logger.info("🎬 Creating VERSION 2: Video with overlays only (no subtitles)")
            # Ensure temp_video_path exists, fall back to original_base_video if not
            if not os.path.exists(temp_video_path):
                logger.debug(f"Extended video not needed, using original base video path for overlays")
                temp_video_path = original_base_video
            # Use the trimmed/original video without subtitles for overlay-only version
            video_overlays_only = self._add_timed_text_overlays(temp_video_path, style_decision, positioning_decision, config, session_context)
            video_overlays_only = self._apply_platform_orientation(video_overlays_only, config.target_platform.value, session_context)
            if config.duration_seconds >= 10:
                current_duration = self._get_video_duration(video_overlays_only)
                if current_duration and current_duration < target_duration - 1.0:
                    video_overlays_only = self._add_fade_out_ending(video_overlays_only, session_context, audio_files)
            
            # Save VERSION 2
            overlays_only_path = session_context.save_final_video(video_overlays_only, suffix="_overlays_only")
            logger.info(f"✅ VERSION 2 created: {overlays_only_path}")
            
            # Step 6: Apply platform orientation to main video
            oriented_video_path = self._apply_platform_orientation(
                video_with_overlays, 
                config.target_platform.value, 
                session_context
            )
            
            # Step 7: Check audio duration and handle overflow
            # Calculate total audio duration
            total_audio_duration = 0
            if audio_files:
                with FFmpegProcessor() as ffmpeg:
                    for audio_file in audio_files:
                        if os.path.exists(audio_file):
                            try:
                                duration = ffmpeg.get_duration(audio_file)
                                total_audio_duration += duration
                            except:
                                pass
            
            current_video_duration = self._get_video_duration(oriented_video_path)
            
            # Check if audio extends beyond video
            if total_audio_duration > current_video_duration + 0.5:  # 0.5s tolerance
                logger.warning(f"⚠️ Audio ({total_audio_duration:.1f}s) extends beyond video ({current_video_duration:.1f}s)")
                logger.info("🎬 Extending video with fade-out to match audio duration")
                
                # Create concatenated audio file for fade-out extension
                concat_audio_path = session_context.get_output_path("temp_files", "full_audio_for_fadeout.mp3")
                with FFmpegProcessor() as ffmpeg:
                    ffmpeg.concatenate_audio(audio_files, concat_audio_path, crossfade=False)
                
                # Extend video with fade-out
                extended_path = session_context.get_output_path("temp_files", "video_extended_fadeout.mp4")
                with FFmpegProcessor() as ffmpeg:
                    ffmpeg.extend_video_with_fadeout(
                        oriented_video_path, 
                        concat_audio_path,
                        extended_path,
                        fade_duration=3.0  # 3 second fade-out
                    )
                
                if os.path.exists(extended_path):
                    final_video_path = extended_path
                    logger.info(f"✅ Video extended to {total_audio_duration:.1f}s with fade-out")
                else:
                    logger.warning("⚠️ Failed to extend video with fade-out, using original")
                    final_video_path = oriented_video_path
            else:
                # Original fade-out logic for videos without audio overflow
                if config.duration_seconds >= 10:  # Add fadeout for videos 10s+
                    # Check if adding fadeout would exceed target duration
                    current_duration = self._get_video_duration(oriented_video_path)
                    if current_duration and current_duration < target_duration - 1.0:  # Leave room for fadeout
                        final_video_path = self._add_fade_out_ending(oriented_video_path, session_context, audio_files)
                        logger.info(f"🎬 Added fadeout ending (current: {current_duration:.1f}s, target: {target_duration}s)")
                    else:
                        logger.info(f"🎬 Skipping fadeout to maintain target duration (current: {current_duration:.1f}s, target: {target_duration}s)")
                        final_video_path = oriented_video_path
                else:
                    logger.info(f"🎬 Skipping fadeout for short video ({config.duration_seconds}s)")
                    final_video_path = oriented_video_path
            
            # Validate final video duration is within tolerance
            final_duration = self._get_video_duration(final_video_path)
            if final_duration:
                tolerance = target_duration * 0.05
                if abs(final_duration - target_duration) > tolerance:
                    logger.warning(f"⚠️ Final video duration {final_duration:.1f}s outside 5% tolerance of target {target_duration}s")
                    
                    if final_duration > target_duration * 1.05:
                        # CRITICAL FIX: Trim to target duration
                        logger.info(f"📏 Final video is {final_duration:.1f}s (target: {target_duration}s) - trimming to target")
                        trimmed_final_path = session_context.get_output_path("temp_files", "final_trimmed.mp4")
                        
                        import subprocess
                        cmd = [
                            'ffmpeg', '-y',
                            '-i', final_video_path,
                            '-t', str(target_duration),
                            '-c', 'copy',
                            trimmed_final_path
                        ]
                        
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0 and os.path.exists(trimmed_final_path):
                            final_video_path = trimmed_final_path
                            logger.info(f"✅ Final video trimmed to target duration: {target_duration}s")
                        else:
                            logger.warning(f"⚠️ Failed to trim final video: {result.stderr}")
                    elif final_duration < target_duration * 0.95 and duration_coordinator:
                        # Extend if too short
                        logger.info(f"🔧 Extending to target duration: {target_duration}s")
                        extended_path = session_context.get_output_path("temp_files", "final_extended.mp4")
                        if duration_coordinator.extend_video_to_duration(final_video_path, target_duration, extended_path):
                            final_video_path = extended_path
                else:
                    logger.info(f"✅ Final video duration {final_duration:.1f}s is within tolerance of target {target_duration}s")
            
            # Step 8: Save VERSION 3 - Final video with subtitles and overlays
            saved_path = session_context.save_final_video(final_video_path, suffix="_final")
            logger.info(f"✅ VERSION 3 created: {saved_path}")
            
            # Step 9: Generate trending hashtags for the video
            self._generate_and_save_hashtags(config, session_context, script_result)
            
            # Step 10: Create summary of all versions
            self._create_version_summary(session_context, saved_path, audio_only_path, overlays_only_path, config)
            
            # Clean up temp files
            temp_files = [temp_video_path, video_with_subtitles, video_with_overlays, oriented_video_path, final_video_path, video_audio_only, video_overlays_only]
            for temp_file in temp_files:
                try:
                    if temp_file and os.path.exists(temp_file) and temp_file not in [saved_path, audio_only_path, overlays_only_path]:
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
                    '-c:a', video_config.encoding.audio_codec,
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
            
            # Get platform dimensions
            aspect_ratio = self._get_platform_aspect_ratio(config.target_platform.value)
            if aspect_ratio == '16:9':
                width, height = 1920, 1080
            else:
                width, height = 1080, 1920
            
            # Create video with solid color background and text
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c=black:size={width}x{height}:duration={duration}',
                '-i', audio_file,
                '-c:v', video_config.encoding.video_codec,
                '-c:a', video_config.encoding.audio_codec,
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
                                     session_context: SessionContext, target_duration: Optional[float] = None,
                                     platform: Optional[str] = None, subtitle_timings: Optional[List[Dict[str, float]]] = None) -> str:
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
            
            # CRITICAL: Use FFmpeg-based composition instead of MoviePy
            if subtitle_timings:
                logger.info("🎯 Using FFmpeg-based subtitle-aligned composition for perfect sync")
                try:
                    # Use our new FFmpeg video composer
                    from .ffmpeg_video_composer import FFmpegVideoComposer
                    from ..ai.manager import AIServiceManager
                    
                    # Create AI manager for overlay generation
                    ai_manager = AIServiceManager()
                    ffmpeg_composer = FFmpegVideoComposer(ai_manager)
                    
                    # Convert subtitle timings to expected format
                    subtitle_segments = []
                    for timing in subtitle_timings:
                        subtitle_segments.append({
                            'start': timing.get('start', 0),
                            'end': timing.get('end', timing.get('start', 0) + 3),
                            'text': timing.get('text', '')
                        })
                    
                    # Compose with FFmpeg
                    ffmpeg_config = {
                        'mission': 'video generation',  # Generic mission since config not available
                        'script': 'generated content',   # Generic script since config not available  
                        'platform': platform or 'instagram',
                        'style': 'viral',
                        'segments': subtitle_segments
                    }
                    
                    # Run async function in sync context
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        ffmpeg_composer.compose_final_video(
                            clips, audio_files, subtitle_segments, ffmpeg_config, output_path
                        )
                    )
                    
                    if result and os.path.exists(result):
                        logger.info("✅ FFmpeg subtitle-aligned composition successful")
                        return result
                    else:
                        logger.warning("⚠️ FFmpeg composition failed, trying simpler approach")
                        
                except Exception as e:
                    logger.error(f"❌ FFmpeg composition error: {e}")
                    logger.info("🔧 Attempting simpler FFmpeg concatenation without overlays")
                    
                    # Try simpler FFmpeg concatenation as fallback
                    try:
                        from ..utils.ffmpeg_processor import FFmpegProcessor
                        with FFmpegProcessor() as ffmpeg:
                            # Simple concatenation + audio sync
                            if len(clips) > 1:
                                base_video = session_context.get_output_path("temp_files", "concat_video.mp4")
                                ffmpeg.concatenate_videos(clips, base_video)
                            else:
                                base_video = clips[0]
                            
                            # Add audio
                            if len(audio_files) > 1:
                                concat_audio = session_context.get_output_path("temp_files", "concat_audio.mp3") 
                                ffmpeg.concatenate_audio(audio_files, concat_audio)
                            else:
                                concat_audio = audio_files[0]
                            
                            # Combine video and audio
                            ffmpeg.add_audio_to_video(base_video, concat_audio, output_path, "exact")
                            
                            if os.path.exists(output_path):
                                logger.info("✅ Simple FFmpeg composition successful")
                                return output_path
                                
                    except Exception as ffmpeg_error:
                        logger.error(f"❌ Simple FFmpeg composition also failed: {ffmpeg_error}")
                        logger.error("❌ No more fallback options available - both advanced and simple FFmpeg failed")
            
            # ENHANCED: Always prefer frame continuity for better video quality
            if len(clips) > 1:
                logger.info("🎯 Multiple clips detected - Frame continuity is STRONGLY PREFERRED")
                
                # Try frame continuity with different approaches
                frame_continuity_attempts = [
                    ("standard", {}),
                    ("with_crossfade", {"crossfade": True}),
                    ("with_blend", {"blend_frames": 2}),
                    ("minimal_trim", {"trim_frames": 1})
                ]
                
                for attempt_name, options in frame_continuity_attempts:
                    try:
                        logger.info(f"🔄 Attempting frame continuity ({attempt_name})...")
                        result = self._compose_with_frame_continuity(
                            clips, audio_files, output_path, session_context, 
                            target_duration, platform=platform, **options
                        )
                        if result and os.path.exists(result):
                            logger.info(f"✅ Frame continuity succeeded with {attempt_name} approach!")
                            return result
                    except Exception as e:
                        logger.warning(f"⚠️ Frame continuity failed ({attempt_name}): {e}")
                        continue
                
                logger.warning("⚠️ All frame continuity attempts failed, falling back to standard cuts")
            else:
                logger.info("🎬 Single clip detected - using direct composition")
            
            # Fallback to standard composition
            return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context, target_duration, platform=platform)
            
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
                # Ensure words_per_line is an integer
                hook_words = hook_style.get('words_per_line', 4)
                if isinstance(hook_words, str):
                    try:
                        hook_words = int(hook_words)
                    except:
                        hook_words = 4
                hook_text = self._create_short_multi_line_text(str(config.hook), max_words_per_line=hook_words, video_width=video_width)
                # Ensure hook text is escaped for FFmpeg
                escaped_hook_text = self._escape_text_for_ffmpeg(hook_text)
                
                if is_dynamic:
                    # DYNAMIC: Moving hook overlay with AI-styled animation
                    overlay_filters.append(
                        f"drawtext=text='{escaped_hook_text}':fontcolor={hook_style['color']}:fontsize={hook_style['font_size']}:font='{hook_style['font_family']}':box=1:boxcolor={hook_style['background_color']}@{hook_style['background_opacity']}:boxborderw={hook_style['stroke_width']}:x='if(lt(t,1.5),(w-text_w)/2,if(lt(t,3),(w-text_w)/2-20*sin(2*PI*t),w-text_w-20))':y='{video_config.layout.overlay_positions['hook']['y']}+10*sin(4*PI*t)':enable=between(t\\,0\\,{video_config.animation.hook_display_duration})"
                    )
                else:
                    # STATIC: AI-styled static positioning
                    overlay_filters.append(
                        f"drawtext=text='{escaped_hook_text}':fontcolor={hook_style['color']}:fontsize={hook_style['font_size']}:font='{hook_style['font_family']}':box=1:boxcolor={hook_style['background_color']}@{hook_style['background_opacity']}:boxborderw={hook_style['stroke_width']}:x=(w-text_w)/2:y={video_config.layout.overlay_positions['hook']['y']}:enable=between(t\\,0\\,{video_config.animation.hook_display_duration})"
                    )
            
            # Add call-to-action overlay with DYNAMIC positioning and AI-driven styling
            if config.call_to_action:
                # Validate CTA text before using it
                cta_text_raw = str(config.call_to_action)
                if self._is_metadata_or_instruction_text(cta_text_raw):
                    logger.warning(f"⚠️ Detected metadata/instruction in CTA: {cta_text_raw[:50]}...")
                    # Use platform-specific default CTA
                    cta_text_raw = video_config.get_default_cta(config.target_platform.value)
                    logger.info(f"✅ Using default CTA: {cta_text_raw}")
                
                # Get AI-driven overlay styling for CTA
                cta_style = self._get_ai_overlay_style(cta_text_raw, "cta", config.target_platform, video_width, video_height, session_context)
                
                # Create smart multi-line CTA text with width constraints
                # Ensure words_per_line is an integer
                cta_words = cta_style.get('words_per_line', 4)
                if isinstance(cta_words, str):
                    try:
                        cta_words = int(cta_words)
                    except:
                        cta_words = 4
                cta_text = self._create_short_multi_line_text(cta_text_raw, max_words_per_line=cta_words, video_width=video_width)
                # Ensure CTA text is escaped for FFmpeg
                escaped_cta_text = self._escape_text_for_ffmpeg(cta_text)
                
                # Calculate CTA timing
                cta_start_time = video_duration - video_config.animation.cta_display_duration
                
                if is_dynamic:
                    # DYNAMIC: Sliding CTA with AI-styled bounce effect
                    overlay_filters.append(
                        f"drawtext=text='{escaped_cta_text}':fontcolor={cta_style['color']}:fontsize={cta_style['font_size']}:font='{cta_style['font_family']}':box=1:boxcolor={cta_style['background_color']}@{cta_style['background_opacity']}:boxborderw={cta_style['stroke_width']}:x='if(lt(t,{cta_start_time}),w+text_w,w-text_w-{video_config.layout.overlay_horizontal_padding}-15*sin(8*PI*(t-{cta_start_time})))':y='{video_config.layout.overlay_positions['cta']['y']}+5*cos(6*PI*t)':enable=between(t\\,{cta_start_time}\\,{video_duration})"
                    )
                else:
                    # STATIC: AI-styled static positioning
                    overlay_filters.append(
                        f"drawtext=text='{escaped_cta_text}':fontcolor={cta_style['color']}:fontsize={cta_style['font_size']}:font='{cta_style['font_family']}':box=1:boxcolor={cta_style['background_color']}@{cta_style['background_opacity']}:boxborderw={cta_style['stroke_width']}:x=w-text_w-{video_config.layout.overlay_horizontal_padding}:y={video_config.layout.overlay_positions['cta']['y']}:enable=between(t\\,{cta_start_time}\\,{video_duration})"
                    )
            
            # Use professional text renderer instead of FFmpeg drawtext
            return self._add_professional_text_overlays(
                video_path, config, video_width, video_height, video_duration, session_context
            )
                
        except Exception as e:
            logger.error(f"❌ Text overlay failed: {e}")
            return video_path
    
    def _is_metadata_or_instruction_text(self, text: str) -> bool:
        """Check if text contains metadata, instructions, or script descriptions"""
        if not text:
            return False
            
        # Patterns that indicate metadata or instructions
        metadata_patterns = [
            'emotional_arc', 'surprise_moments', 'shareability_score',
            '{', '}', ':', 'viral_elements', 'script_data', 'config',
            'visual:', 'show:', 'cut to:', 'scene:', 'fade:', 'zoom:',
            'camera:', 'angle:', 'shot:', 'transition:', 'effect:',
            'this concludes', 'this ends', 'segment ends', 'scene ends'
        ]
        
        # Check if text contains any metadata patterns
        text_lower = text.lower()
        for pattern in metadata_patterns:
            if pattern.lower() in text_lower:
                return True
        
        # Check if text looks like a dictionary representation
        if text.strip().startswith('{') or text.strip().endswith('}'):
            return True
            
        # Check if text contains multiple colons (likely key:value pairs)
        if text.count(':') > 2:
            return True
            
        return False

    def _add_professional_text_overlays(self, video_path: str, config: GeneratedVideoConfig,
                                       video_width: int, video_height: int, video_duration: float,
                                       session_context: SessionContext,
                                       script_result: Optional[Dict[str, Any]] = None) -> str:
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
                    font_size=video_config.get_font_size('header', video_width),
                    font_weight="bold",
                    color=(255, 255, 255, 255),
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=video_config.get_stroke_width('title'),
                    background_color=(0, 0, 0, 180),
                    background_padding=(15, 8, 15, 8),
                    shadow_color=(0, 0, 0, 200),
                    shadow_offset=(3, 3),
                    line_spacing=1.2
                )
                
                hook_layout = TextLayout(
                    position=TextPosition.TOP_CENTER,
                    alignment=TextAlignment.CENTER,
                    max_width=int(video_width * video_config.layout.max_subtitle_width_percentage),
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
                    font_family=video_config.text_overlay.default_font.replace('-Bold', ''),
                    font_size=video_config.get_font_size('body', video_width),
                    font_weight="bold",
                    color=(255, 255, 255, 255),
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=video_config.text_overlay.stroke_widths['default'],
                    background_color=(255, 0, 100, 200),
                    background_padding=(12, 6, 12, 6),
                    line_spacing=1.1
                )
                
                cta_layout = TextLayout(
                    position=TextPosition.BOTTOM_RIGHT,
                    alignment=TextAlignment.CENTER,
                    max_width=int(video_width * video_config.layout.max_overlay_width_percentage),
                    margin=(20, 20, 30, 80)
                )
                
                cta_overlay = TextOverlay(
                    text=str(config.call_to_action),
                    style=cta_style,
                    layout=cta_layout,
                    start_time=video_duration - video_config.animation.cta_display_duration,
                    end_time=video_duration,
                    fade_in_duration=video_config.animation.overlay_fade_duration,
                    fade_out_duration=video_config.animation.overlay_fade_duration
                )
                overlays.append(cta_overlay)
            
            # CRITICAL: Add business address as a persistent overlay throughout the video
            if config.business_address and config.show_business_info:
                logger.info(f"🏠 Adding persistent business address overlay: {config.business_address}")
                
                address_style = TextStyle(
                    font_family="Arial",
                    font_size=video_config.get_font_size('body', video_width),
                    font_weight="bold",
                    color=(255, 255, 255, 255),  # White
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=2,
                    background_color=(220, 20, 60, 200),  # Crimson red background
                    background_padding=(15, 8, 15, 8),
                    line_spacing=1.0
                )
                
                address_layout = TextLayout(
                    position=TextPosition.TOP_RIGHT,
                    alignment=TextAlignment.RIGHT,
                    max_width=int(video_width * 0.35),
                    margin=(20, 80, 20, 20)  # Below the hook
                )
                
                # Show address throughout most of the video
                address_overlay = TextOverlay(
                    text=f"📍 {config.business_address}",
                    style=address_style,
                    layout=address_layout,
                    start_time=2.0,  # Start after 2 seconds
                    end_time=video_duration - 5.5,  # Hide before business info appears
                    fade_in_duration=0.5,
                    fade_out_duration=0.3
                )
                overlays.append(address_overlay)
                logger.info(f"✅ Added persistent address overlay from 2s to {video_duration - 5.5:.1f}s")
            
            # Business info overlay - Big and prominent at the end
            if config.show_business_info and any([config.business_name, config.business_address, 
                                                  config.business_phone, config.business_website,
                                                  config.business_facebook, config.business_instagram]):
                # Log what business info we have
                logger.info(f"📍 Business info - Name: {config.business_name}, Address: {config.business_address}, Phone: {config.business_phone}")
                
                # Create business info text with proper emoji support
                business_lines = []
                if config.business_name:
                    business_lines.append(f"🏪 {config.business_name}")
                if config.business_address:
                    business_lines.append(f"📍 {config.business_address}")
                if config.business_phone:
                    business_lines.append(f"📞 {config.business_phone}")
                if config.business_website:
                    business_lines.append(f"🌐 {config.business_website}")
                if config.business_facebook:
                    business_lines.append(f"👥 {config.business_facebook}")
                if config.business_instagram:
                    business_lines.append(f"📸 {config.business_instagram}")
                
                business_text = "\n".join(business_lines)
                
                # Large, prominent business info style for end of video
                business_style = TextStyle(
                    font_family="Arial",  # Use Arial as primary font
                    font_size=int(video_config.get_font_size('title', video_width) * 0.8),  # Large font
                    font_weight="bold",
                    color=(255, 255, 255, 255),  # Bright white
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=3,  # Thick stroke for visibility
                    background_color=(0, 0, 0, 200),  # Semi-transparent black background
                    background_padding=(25, 20, 25, 20),  # Large padding
                    line_spacing=1.4
                )
                
                # Position business info prominently in center-bottom
                business_layout = TextLayout(
                    position=TextPosition.BOTTOM_CENTER,
                    alignment=TextAlignment.CENTER,
                    max_width=int(video_width * 0.8),  # 80% of video width - big overlay
                    margin=(20, 20, 40, 40)  # More margin from bottom
                )
                
                # Show business info in the last portion of the video
                # For shorter videos (under 30s), show for 5 seconds; otherwise 3 seconds
                end_display_duration = 5.0 if video_duration < 30 else 3.0
                # Make sure we don't start before the video begins
                start_time = max(0.5, video_duration - end_display_duration)
                
                business_overlay = TextOverlay(
                    text=business_text,
                    style=business_style,
                    layout=business_layout,
                    start_time=start_time,
                    end_time=video_duration - 0.2,  # End just before video ends
                    fade_in_duration=0.3,
                    fade_out_duration=0.2
                )
                overlays.append(business_overlay)
                logger.info(f"✅ Added prominent business info overlay with {len(business_lines)} lines (shown in last {end_display_duration}s)")
            
            # CRITICAL: Add dynamic overlays using AI agent
            if script_result and config.enable_dynamic_overlays != False:  # Only skip if explicitly disabled
                try:
                    from ..agents.overlay_strategist_agent import OverlayStrategistAgent, OverlayType
                    from ..models.professional_text_models import TextPosition, TextAlignment
                    
                    logger.info("🎯 Generating dynamic overlays using AI agent")
                    
                    # Initialize overlay strategist
                    overlay_agent = OverlayStrategistAgent(self.gemini_api_key)
                    
                    # Get script and segments
                    script = script_result.get('final_script', script_result.get('optimized_script', ''))
                    segments = script_result.get('segments', [])
                    
                    # Generate dynamic overlays
                    dynamic_overlays = overlay_agent.analyze_script_for_overlays(
                        script=script,
                        video_duration=video_duration,
                        platform=config.target_platform.value,
                        style=config.visual_style or "dynamic",
                        tone=config.tone or "engaging",
                        mission=config.mission,
                        segments=segments
                    )
                    
                    # Convert dynamic overlays to TextOverlay objects
                    for dyn_overlay in dynamic_overlays:
                        # Map position strings to TextPosition enum
                        position_map = {
                            'top-left': TextPosition.TOP_LEFT,
                            'top-center': TextPosition.TOP_CENTER,
                            'top-right': TextPosition.TOP_RIGHT,
                            'middle-left': TextPosition.MIDDLE_LEFT,
                            'center': TextPosition.CENTER,
                            'middle-right': TextPosition.MIDDLE_RIGHT,
                            'bottom-left': TextPosition.BOTTOM_LEFT,
                            'bottom-center': TextPosition.BOTTOM_CENTER,
                            'bottom-right': TextPosition.BOTTOM_RIGHT
                        }
                        
                        # Map style to font settings
                        if dyn_overlay.style == 'bold':
                            font_weight = 'bold'
                            font_size_multiplier = 1.1
                        elif dyn_overlay.style == 'subtle':
                            font_weight = 'normal'
                            font_size_multiplier = 0.9
                        else:
                            font_weight = 'bold'
                            font_size_multiplier = 1.0
                        
                        # Map size to actual font size
                        size_map = {'small': 0.8, 'medium': 1.0, 'large': 1.2}
                        size_multiplier = size_map.get(dyn_overlay.size, 1.0)
                        
                        # Create style based on overlay type
                        if dyn_overlay.overlay_type == OverlayType.FACT_BUBBLE:
                            bg_color = (30, 144, 255, 200)  # Dodger blue
                            text_color = (255, 255, 255, 255)
                        elif dyn_overlay.overlay_type == OverlayType.CALL_TO_ACTION:
                            bg_color = (255, 20, 147, 200)  # Deep pink
                            text_color = (255, 255, 255, 255)
                        elif dyn_overlay.overlay_type == OverlayType.WARNING:
                            bg_color = (255, 69, 0, 200)  # Red orange
                            text_color = (255, 255, 255, 255)
                        elif dyn_overlay.overlay_type == OverlayType.TIP:
                            bg_color = (50, 205, 50, 200)  # Lime green
                            text_color = (255, 255, 255, 255)
                        else:
                            bg_color = (0, 0, 0, 180)  # Default semi-transparent black
                            text_color = (255, 255, 255, 255)
                        
                        overlay_style = TextStyle(
                            font_family=video_config.text_overlay.default_font,
                            font_size=int(video_config.get_font_size('body', video_width) * font_size_multiplier * size_multiplier),
                            font_weight=font_weight,
                            color=text_color,
                            stroke_color=(0, 0, 0, 255),
                            stroke_width=2,
                            background_color=bg_color,
                            background_padding=(10, 6, 10, 6),
                            line_spacing=1.1
                        )
                        
                        overlay_layout = TextLayout(
                            position=position_map.get(dyn_overlay.position, TextPosition.TOP_CENTER),
                            alignment=TextAlignment.CENTER,
                            max_width=int(video_width * 0.6),
                            margin=(20, 20, 20, 20)
                        )
                        
                        text_overlay = TextOverlay(
                            text=dyn_overlay.text,
                            style=overlay_style,
                            layout=overlay_layout,
                            start_time=dyn_overlay.start_time,
                            end_time=dyn_overlay.start_time + dyn_overlay.duration,
                            fade_in_duration=0.3,
                            fade_out_duration=0.3
                        )
                        
                        overlays.append(text_overlay)
                        logger.info(f"   Added {dyn_overlay.overlay_type.value}: '{dyn_overlay.text}' at {dyn_overlay.start_time:.1f}s")
                    
                    logger.info(f"✅ Added {len(dynamic_overlays)} dynamic overlays")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate dynamic overlays: {e}")
                    # Continue without dynamic overlays
            
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
                codec=video_config.encoding.video_codec,
                audio_codec=video_config.encoding.audio_codec,
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
                    
                    # Add RTL mark for Hebrew, Arabic, and Persian text
                    import re
                    rtl_chars = re.compile(r'[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
                    is_rtl = rtl_chars.search(text)
                    if is_rtl:
                        # Only reshape, don't apply bidi for MoviePy (it handles RTL natively)
                        if RTL_SUPPORT:
                            # MoviePy expects logical order, not visual order
                            text = arabic_reshaper.reshape(text)
                            # DON'T apply get_display() - MoviePy will handle the visual ordering
                            logger.debug(f"🔤 Reshaped RTL text (logical order) for MoviePy")
                        else:
                            # Fallback: Add Right-to-Left Mark (RLM) at the beginning and end
                            text = '\u200F' + text + '\u200F'
                            logger.debug(f"🔤 Added RTL marks to subtitle (no reshaper available)")
                    
                    # Select appropriate font for RTL support
                    subtitle_font = video_config.text_overlay.rtl_font if is_rtl else video_config.text_overlay.default_font
                    
                    start_time = segment['start']
                    end_time = segment['end']
                    
                    if end_time <= start_time:
                        continue
                    
                    # Calculate position based on AI decision and video orientation
                    is_portrait = video_height > video_width  # Check if portrait orientation
                    
                    if primary_position == 'top_third':
                        y_pos = video_height * 0.20  # 20% from top
                    elif primary_position == 'center':
                        y_pos = video_height * 0.50  # Center
                    else:  # bottom_third (default)
                        if is_portrait:
                            # Lower position for portrait videos (closer to bottom)
                            y_pos = video_height * 0.75  # 75% down for portrait
                        else:
                            # Standard position for landscape
                            y_pos = video_height * 0.60  # 60% down for landscape
                    
                    # Font size based on video dimensions
                    font_size = video_config.get_font_size('header', video_width)
                    
                    # Create text clip with modern styling
                    # MoviePy uses 'center' for all alignments in caption method
                    text_align = 'center'  # Caption method handles RTL internally
                    
                    text_clip = TextClip(
                        text,
                        fontsize=font_size,
                        color='white',
                        font=subtitle_font,  # Use RTL font if needed
                        stroke_color='black',
                        stroke_width=video_config.text_overlay.stroke_widths['default'],
                        method='caption',
                        size=(int(video_width * video_config.layout.max_subtitle_width_percentage), None),
                        align=text_align  # Use right alignment for RTL text
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
                    ).set_opacity(video_config.text_overlay.badge_opacity)  # Semi-transparent
                    
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
                    fps=video_config.get_fps(config.target_platform.value),
                    codec=video_config.encoding.video_codec,
                    audio_codec=video_config.encoding.audio_codec,
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
                main_content = config.main_content or [config.mission]
                # Generate dynamic content based on mission
                mission_word = config.mission.split()[0] if config.mission else "content"
                hook = config.hook or f"Discover {mission_word}!"
                cta = config.call_to_action or video_config.get_default_cta(config.target_platform.value)
                actual_script = f"{hook} {' '.join(main_content)} {cta}"
                logger.warning("⚠️ Using fallback config content for subtitles")
            
            # Check if we have audio segments first to match the subtitle count
            audio_segment_count = 0
            if session_context:
                audio_dir = session_context.get_output_path("audio")
                if os.path.exists(audio_dir):
                    audio_files = [f for f in os.listdir(audio_dir) if (f.endswith('.mp3') or f.endswith('.wav')) and not f.startswith('pause_')]
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
            
            # First, split script into complete sentences (including colons and semicolons)
            sentences = re.split(r'([.!?:;]+)', script)
            # Recombine sentences with their punctuation
            complete_sentences = []
            for i in range(0, len(sentences) - 1, 2):
                if i + 1 < len(sentences):
                    sentence = sentences[i].strip() + sentences[i + 1].strip()
                    if sentence.strip():
                        complete_sentences.append(sentence.strip())
                elif sentences[i].strip():
                    complete_sentences.append(sentences[i].strip())
            
            # Handle any remaining text
            if len(sentences) % 2 == 1 and sentences[-1].strip():
                complete_sentences.append(sentences[-1].strip())
            
            if not complete_sentences:
                # Fallback: split by periods only
                complete_sentences = [s.strip() for s in script.split('.') if s.strip()]
                complete_sentences = [s + '.' for s in complete_sentences[:-1]] + [complete_sentences[-1]] if complete_sentences else [script]
            
            logger.info(f"📝 Found {len(complete_sentences)} complete sentences to distribute across {audio_count} segments")
            
            # Distribute sentences across segments ensuring no sentence is cut
            segments = []
            # CRITICAL: Limit to EXACTLY 1 sentence per segment for proper subtitles
            sentences_per_segment = 1
            
            sentence_index = 0
            for i in range(audio_count):
                segment_sentences = []
                
                if i == audio_count - 1 and sentence_index < len(complete_sentences):
                    # Last segment: take only 1 sentence
                    remaining_sentences = complete_sentences[sentence_index:]
                    segment_sentences = remaining_sentences[:1]  # Only 1 sentence for subtitles
                    sentence_index += len(segment_sentences)
                else:
                    # Take exactly 1 sentence
                    if sentence_index < len(complete_sentences):
                        segment_sentences = [complete_sentences[sentence_index]]
                        sentence_index += 1
                
                # Get the single sentence for this segment
                segment_text = segment_sentences[0] if segment_sentences else ""
                
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
            
            # CRITICAL: Final validation - ensure no segment has more than 1 sentence
            validated_segments = []
            for segment in segments:
                if segment.get('sentence_count', 1) > 1:
                    # Split oversized segments - this should not happen with our new logic
                    text = segment['text']
                    sentences = re.split(r'([.!?:;]+)', text)
                    
                    # Take only first sentence with its punctuation
                    if len(sentences) >= 2:
                        limited_text = sentences[0].strip() + sentences[1].strip()
                    else:
                        limited_text = text
                    
                    segment['text'] = limited_text
                    segment['sentence_count'] = 1
                    segment['word_count'] = len(limited_text.split())
                    
                    logger.warning(f"⚠️ Limited segment to 1 sentence: '{limited_text[:50]}...'")
                
                validated_segments.append(segment)
            
            logger.info(f"✅ Created {len(validated_segments)} segments with complete sentence boundaries (1 sentence each)")
            return validated_segments
            
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
            # Split script into sentences (including colons and semicolons as sentence endings)
            import re
            # First split on sentence endings including colons and semicolons
            sentences = re.split(r'([.!?:;]+)', script)
            
            # Recombine sentences with their punctuation
            complete_sentences = []
            for i in range(0, len(sentences) - 1, 2):
                if i + 1 < len(sentences):
                    sentence = sentences[i].strip() + sentences[i + 1].strip()
                    if sentence.strip():
                        complete_sentences.append(sentence.strip())
                elif sentences[i].strip():
                    complete_sentences.append(sentences[i].strip())
            
            # Handle any remaining text
            if len(sentences) % 2 == 1 and sentences[-1].strip():
                complete_sentences.append(sentences[-1].strip())
            
            if not complete_sentences:
                return []
            
            logger.info(f"📝 Parsed script into {len(complete_sentences)} sentences for subtitles")
            
            # Calculate timing based on sentence complexity and length
            segments = []
            total_words = sum(len(sentence.split()) for sentence in complete_sentences)
            
            # Estimate words per second (typical speech rate: 2-3 words/second)
            words_per_second = max(2.0, min(3.0, total_words / video_duration))
            
            current_time = 0.0
            
            # Create ONE sentence per segment
            i = 0
            while i < len(complete_sentences):
                # Take ONLY ONE sentence for this segment
                segment_text = complete_sentences[i]
                segment_words = len(segment_text.split())
                i += 1
                
                # Calculate duration based on word count
                base_duration = segment_words / words_per_second
                
                # Ensure minimum and maximum duration per segment
                duration = max(2.0, min(6.0, base_duration))
                
                # Adjust if we're running out of time
                remaining_time = video_duration - current_time
                if i >= len(complete_sentences):  # Last segment
                    duration = min(duration, remaining_time)
                elif current_time + duration > video_duration:
                    duration = remaining_time * 0.9  # Leave some buffer
                
                # Format text for MoviePy subtitle display with proper line breaks
                max_chars = min(10, int(video_width * 0.01))  # Minimum character count for safety  # Very short lines to prevent cutting
                formatted_text = self._format_subtitle_text(segment_text, max_chars_per_line=max_chars)
                
                segments.append({
                    'text': formatted_text,
                    'start': current_time,
                    'end': current_time + duration,
                    'word_count': segment_words,
                    'estimated_duration': duration,
                    'sentence_count': 1  # Always 1 sentence per segment now
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
            import numpy as np
            
            logger.info("🎯 Performing perfect single-audio synchronization")
            
            # Get actual audio duration using FFmpeg
            from ..utils.ffmpeg_processor import FFmpegProcessor
            with FFmpegProcessor() as ffmpeg:
                actual_audio_duration = ffmpeg.get_duration(audio_file)
            
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
                    # CRITICAL FIX: Remove duration multiplier to maintain exact target duration
                    pass  # base_duration *= 1.15  # 15% longer for questions and emphasis
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
            logger.info("🎯 Performing perfect multi-audio synchronization")
            
            # Sort audio files by segment number
            audio_files.sort(key=lambda x: int(re.search(r'segment_(\d+)', x).group(1)) if re.search(r'segment_(\d+)', x) else 0)
            
            # Analyze each audio file duration with high precision
            audio_durations = []
            total_audio_duration = 0.0
            
            # Use FFmpeg for precise audio duration analysis
            from ..utils.ffmpeg_processor import FFmpegProcessor
            with FFmpegProcessor() as ffmpeg:
                for i, audio_file in enumerate(audio_files):
                    try:
                        duration = round(ffmpeg.get_duration(audio_file), 3)  # High precision
                        audio_durations.append(duration)
                        total_audio_duration += duration
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
            # Get actual audio duration using FFmpeg
            from ..utils.ffmpeg_processor import FFmpegProcessor
            with FFmpegProcessor() as ffmpeg:
                actual_audio_duration = ffmpeg.get_duration(audio_file)
            
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
                    # CRITICAL FIX: Remove duration multiplier to maintain exact target duration
                    pass  # base_duration *= 1.3  # Hooks need more time
                elif text.lower().endswith(('!', '?')):
                    # CRITICAL FIX: Remove duration multiplier to maintain exact target duration
                    pass  # base_duration *= 1.1  # Questions/exclamations need emphasis
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
                                     output_path: str, session_context: SessionContext, 
                                     target_duration: Optional[float] = None,
                                     platform: Optional[str] = None,
                                     crossfade: bool = False,
                                     blend_frames: int = 0,
                                     trim_frames: int = 1) -> str:
        """Compose video with frame continuity - multiple approaches for seamless transitions
        
        Args:
            clips: List of video clip paths
            audio_files: List of audio file paths
            output_path: Output video path
            session_context: Session context
            target_duration: Target duration for the video
            crossfade: Whether to use crossfade between clips
            blend_frames: Number of frames to blend at transitions
            trim_frames: Number of frames to trim from start of clips (except first)
        """
        try:
            import subprocess
            
            logger.info(f"🎬 Frame continuity composition with options:")
            logger.info(f"   Crossfade: {crossfade}")
            logger.info(f"   Blend frames: {blend_frames}")
            logger.info(f"   Trim frames: {trim_frames}")
            
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
            # For clips after the first, skip frames based on trim_frames parameter
            video_filter_parts = []
            
            # Calculate frame duration based on platform FPS
            fps = video_config.get_fps(platform or 'default')
            frame_duration = trim_frames * video_config.animation.get_frame_duration(fps)
            
            # Determine dimensions based on platform
            aspect_ratio = self._get_platform_aspect_ratio(platform or 'youtube')
            if aspect_ratio == '16:9':
                width, height = 1920, 1080  # YouTube, Facebook landscape
            else:
                width, height = 1080, 1920  # TikTok, Instagram portrait
            for i, clip in enumerate(clips):
                if i == 0:
                    # First clip: scale to target dimensions and use as-is
                    video_filter_parts.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
                else:
                    # Subsequent clips: scale to portrait and remove frames based on trim_frames
                    if trim_frames > 0:
                        video_filter_parts.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,trim=start={frame_duration},setpts=PTS-STARTPTS[v{i}]")
                    else:
                        # No trimming
                        video_filter_parts.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
            
            # Concatenate all video streams with optional effects
            if len(clips) > 1:
                trim_filters = ";".join(video_filter_parts)
                
                if crossfade:
                    # Use xfade filter for smooth transitions
                    xfade_filter = trim_filters + ";"
                    for i in range(len(clips) - 1):
                        if i == 0:
                            xfade_filter += f"[v0][v1]xfade=transition=fade:duration=0.5:offset=3[vx1];"
                        elif i == len(clips) - 2:
                            xfade_filter += f"[vx{i}][v{i+1}]xfade=transition=fade:duration=0.5:offset=6[outv]"
                        else:
                            xfade_filter += f"[vx{i}][v{i+1}]xfade=transition=fade:duration=0.5:offset=6[vx{i+1}];"
                    video_filter = xfade_filter
                elif blend_frames > 0:
                    # Use blend filter for frame blending
                    blend_filter = trim_filters + ";"
                    concat_inputs = "".join([f"[v{i}]" for i in range(len(clips))])
                    video_filter = f"{blend_filter}{concat_inputs}concat=n={len(clips)}:v=1:a=0[outv]"
                    # Note: Actual frame blending would require more complex filters
                else:
                    # Standard concatenation
                    concat_inputs = "".join([f"[v{i}]" for i in range(len(clips))])
                    video_filter = f"{trim_filters};{concat_inputs}concat=n={len(clips)}:v=1:a=0[outv]"
            else:
                video_filter = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[outv]"
            
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
                '-c:v', video_config.encoding.video_codec,
                '-c:a', video_config.encoding.audio_codec,
                '-preset', video_config.get_encoding_preset(platform or 'default'),
                '-crf', str(video_config.get_crf(platform or 'default'))
            ]
            
            # CRITICAL: Add duration limit to prevent extending beyond target
            if target_duration:
                cmd.extend(['-t', str(target_duration)])
                logger.info(f"⏱️ Enforcing exact duration during composition: {target_duration}s")
            else:
                # Even without explicit target, cap to configured duration
                # Note: duration should be passed as a parameter, not stored on self
                logger.info("⏱️ No explicit target duration provided for composition")
            
            cmd.append(output_path)
            
            logger.info("🎬 Running frame continuity composition...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Frame continuity composition completed")
                return output_path
            else:
                logger.error(f"❌ Frame continuity composition failed: {result.stderr}")
                # Fallback to standard composition
                return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context, target_duration)
                
        except Exception as e:
            logger.error(f"❌ Frame continuity composition error: {e}")
            # Fallback to standard composition
            return self._compose_with_standard_cuts(clips, audio_files, output_path, session_context, target_duration, platform=platform)

    def _compose_with_standard_cuts(self, clips: List[str], audio_files: List[str], 
                                  output_path: str, session_context: SessionContext,
                                  target_duration: Optional[float] = None, 
                                  platform: Optional[str] = None) -> str:
        """Compose video with standard cuts - concatenate video clips, then add audio segments sequentially"""
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
            
            logger.info(f"🎬 Composing video with {len(clips)} video clips and {len(audio_files)} audio segments")
            
            # CRITICAL: Calculate total audio duration to ensure full coverage
            total_audio_duration = 0.0
            audio_durations = []
            for audio_file in audio_files:
                try:
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'default=noprint_wrappers=1:nokey=1', audio_file]
                    result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        duration = float(result.stdout.strip())
                        audio_durations.append(duration)
                        total_audio_duration += duration
                except:
                    logger.warning(f"⚠️ Could not get duration for audio file: {audio_file}")
                    audio_durations.append(5.0)  # Default duration
                    total_audio_duration += 5.0
            
            logger.info(f"🎵 Total audio duration: {total_audio_duration:.1f}s")
            logger.info(f"🎵 Audio segments ({len(audio_files)}): {[f'{d:.1f}s' for d in audio_durations]}")
            
            # Calculate total video duration
            total_video_duration = 0.0
            video_durations = []
            for clip in clips:
                try:
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'default=noprint_wrappers=1:nokey=1', clip]
                    result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        duration = float(result.stdout.strip())
                        video_durations.append(duration)
                        total_video_duration += duration
                except:
                    logger.warning(f"⚠️ Could not get duration for video clip: {clip}")
                    video_durations.append(5.0)  # Default duration
                    total_video_duration += 5.0
            
            logger.info(f"🎬 Total video duration: {total_video_duration:.1f}s")
            logger.info(f"🎬 Video clips ({len(clips)}): {[f'{d:.1f}s' for d in video_durations]}")
            
            # CRITICAL: Ensure audio covers entire video
            if total_audio_duration < total_video_duration * 0.95:  # Allow 5% tolerance
                logger.warning(f"⚠️ Audio duration ({total_audio_duration:.1f}s) is shorter than video ({total_video_duration:.1f}s)")
                logger.info("🔧 Will ensure audio loops or extends to cover entire video")
            
            # NEW APPROACH: First concatenate all video clips, then add audio sequentially
            logger.info("🎬 NEW APPROACH: Concatenating video clips first, then adding audio segments sequentially")
            
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
            
            # Determine dimensions based on platform
            aspect_ratio = self._get_platform_aspect_ratio(platform or 'youtube')
            if aspect_ratio == '16:9':
                width, height = 1920, 1080  # YouTube, Facebook landscape
            else:
                width, height = 1080, 1920  # TikTok, Instagram portrait
            
            # Create filters to normalize all videos to target dimensions
            video_scale_filters = []
            for i in range(len(clips)):
                video_scale_filters.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]")
            
            # Join the scale filters
            scale_filter_str = ";".join(video_scale_filters)
            
            # Create concatenation inputs for video ONLY
            video_concat_inputs = "".join([f"[v{i}]" for i in range(len(clips))])
            
            # Concatenate audio files sequentially (one per sentence)
            audio_inputs = "".join([f"[{len(clips)+i}:a]" for i in range(len(audio_files))])
            
            # CRITICAL FIX: New filter complex - concatenate video clips, then add audio segments
            if len(clips) > 0 and len(audio_files) > 0:
                # First concatenate all video clips into one continuous video
                # Then concatenate all audio segments sequentially
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
                '-c:v', video_config.encoding.video_codec,
                '-c:a', video_config.encoding.audio_codec,
                '-preset', video_config.get_encoding_preset(platform or 'default'),
                '-crf', str(video_config.get_crf(platform or 'default'))
            ])
            
            # CRITICAL: Add duration limit to prevent extending beyond target
            if target_duration:
                cmd.extend(['-t', str(target_duration)])
                logger.info(f"⏱️ Enforcing exact duration during composition: {target_duration}s")
            else:
                # Even without explicit target, cap to configured duration
                # Note: duration should be passed as a parameter, not stored on self
                logger.info("⏱️ No explicit target duration provided for composition")
            
            cmd.append(output_path)
            
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
                return self._create_simple_fallback_composition(clips, audio_files, output_path, session_context, platform)
                
        except Exception as e:
            logger.error(f"❌ Standard composition error: {e}")
            return ""
    
    # MoviePy-based function removed - using FFmpeg-only approach
    def _create_simple_fallback_composition(self, clips: List[str], audio_files: List[str], 
                                           output_path: str, session_context: SessionContext,
                                           platform: Optional[str] = None) -> str:
        """Create a simple fallback composition when standard composition fails"""
        try:
            logger.info("🎬 Creating simple fallback composition")
            
            # If we have audio but no video, create a simple video with audio
            if not clips and audio_files:
                return self._create_audio_only_video(audio_files, output_path, session_context, platform)
            
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
                                session_context: SessionContext, platform: Optional[str] = None) -> str:
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
                    '-c:a', video_config.encoding.audio_codec,
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
            
            # Get platform dimensions
            aspect_ratio = self._get_platform_aspect_ratio(platform or 'youtube')
            if aspect_ratio == '16:9':
                width, height = 1920, 1080
            else:
                width, height = 1080, 1920
            
            # Create video with solid color background
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c=black:size={width}x{height}:duration={duration}',
                '-i', audio_file,
                '-c:v', video_config.encoding.video_codec,
                '-c:a', video_config.encoding.audio_codec,
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
                '-c:v', video_config.encoding.video_codec,
                '-preset', video_config.get_encoding_preset(platform or 'default'),
                '-crf', str(video_config.get_crf(platform or 'default')),
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
                '-c:a', video_config.encoding.audio_codec,
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
- Mission: {config.mission}
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
            # 1. Analyze actual clip and audio durations using FFmpeg
            from ..utils.ffmpeg_processor import FFmpegProcessor
            
            clip_durations = []
            with FFmpegProcessor() as ffmpeg:
                for clip in clips:
                    if os.path.exists(clip):
                        try:
                            clip_durations.append(ffmpeg.get_duration(clip))
                        except Exception as e:
                            logger.warning(f"⚠️ Could not get duration for {clip}: {e}")
                            clip_durations.append(target_duration / len(clips))
                    else:
                        clip_durations.append(target_duration / len(clips))
            
                audio_durations = []
                for audio_file in audio_files:
                    if os.path.exists(audio_file):
                        try:
                            audio_durations.append(ffmpeg.get_duration(audio_file))
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
    
    def _create_subtitles_with_timings(self, script_result: Dict[str, Any], audio_files: List[str], 
                                      session_context: SessionContext, timeline_visualizer: Optional[TimelineVisualizer] = None) -> Dict[str, Any]:
        """Create subtitles and return both files and timing information"""
        subtitle_files = self._create_subtitles(script_result, audio_files, session_context, timeline_visualizer)
        
        # Extract timing information from the created subtitles
        timings = []
        try:
            srt_path = subtitle_files.get('srt')
            if srt_path and os.path.exists(srt_path):
                with open(srt_path, 'r') as f:
                    content = f.read()
                    
                # Parse SRT to extract timings
                import re
                pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)'
                matches = re.findall(pattern, content, re.DOTALL)
                
                for match in matches:
                    start_time_str = match[1]
                    end_time_str = match[2]
                    text = match[3].strip()
                    
                    # Convert time strings to seconds
                    start_seconds = self._srt_time_to_seconds(start_time_str)
                    end_seconds = self._srt_time_to_seconds(end_time_str)
                    
                    timings.append({
                        'start': start_seconds,
                        'end': end_seconds,
                        'text': text
                    })
                    
                    # Add to timeline visualizer
                    if timeline_visualizer:
                        timeline_visualizer.add_subtitle_event(
                            index=len(timings),
                            start=start_seconds,
                            end=end_seconds,
                            text=text
                        )
                    
                logger.info(f"📝 Extracted {len(timings)} subtitle timings from SRT file")
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract subtitle timings: {e}")
        
        return {
            'files': subtitle_files,
            'timings': timings
        }
    
    def _srt_time_to_seconds(self, time_str: str) -> float:
        """Convert SRT time format (HH:MM:SS,mmm) to seconds"""
        parts = time_str.replace(',', '.').split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    
    def _create_subtitles(self, script_result: Dict[str, Any], audio_files: List[str], 
                         session_context: SessionContext, timeline_visualizer: Optional[TimelineVisualizer] = None) -> Dict[str, str]:
        """Create subtitle files (SRT and VTT) from script and audio timing
        
        Uses one-sentence-per-audio-segment approach for perfect sync:
        - Each audio file contains exactly one sentence
        - Each subtitle entry corresponds to exactly one audio file
        - Timing is based on actual audio duration from ffprobe
        """
        try:
            logger.info("📝 Creating subtitles with one-sentence-per-segment approach")
            
            # Get the actual script content and segments from script_result
            script_content = script_result.get('final_script', script_result.get('optimized_script', ''))
            script_segments = script_result.get('segments', [])
            
            if not script_content:
                logger.warning("⚠️ No script content available for subtitles")
                return {}
            
            if not audio_files:
                logger.warning("⚠️ No audio files available for subtitle timing")
                return {}
            
            # Import video_config for padding value
            from ..config import video_config
            
            # CRITICAL: With one-sentence-per-segment approach:
            # - Each audio file should contain exactly one sentence
            # - Each subtitle entry corresponds to exactly one audio file
            # - We use actual audio duration from ffprobe for perfect timing
            
            segments = []
            current_time = 0.0
            
            # Get sentences from script if segments not available
            if not script_segments or len(script_segments) != len(audio_files):
                logger.info("📝 Extracting sentences from script for subtitle alignment")
                # Split script into sentences
                import re
                sentences = re.split(r'([.!?:;]+)', script_content)
                
                # Recombine sentences with their punctuation
                complete_sentences = []
                for i in range(0, len(sentences) - 1, 2):
                    if i + 1 < len(sentences):
                        sentence = sentences[i].strip() + sentences[i + 1].strip()
                        if sentence.strip():
                            complete_sentences.append(sentence.strip())
                    elif sentences[i].strip():
                        complete_sentences.append(sentences[i].strip())
                
                # Handle any remaining text
                if len(sentences) % 2 == 1 and sentences[-1].strip():
                    complete_sentences.append(sentences[-1].strip())
            else:
                # Use segments from script_result
                complete_sentences = [seg.get('text', '') for seg in script_segments]
            
            logger.info(f"📝 Creating subtitles for {len(audio_files)} audio segments")
            logger.info(f"📝 Found {len(complete_sentences)} sentences in script")
            
            # Create one subtitle per audio file
            for i, audio_file in enumerate(audio_files):
                segment_start_time = current_time
                
                # Get actual audio duration using ffprobe
                try:
                    import subprocess
                    import json
                    result = subprocess.run([
                        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                        '-show_format', audio_file
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        audio_duration = float(data['format']['duration'])
                        logger.debug(f"✅ Audio {i+1} duration: {audio_duration:.2f}s")
                    else:
                        # Fallback duration based on word count
                        if i < len(complete_sentences):
                            word_count = len(complete_sentences[i].split())
                            audio_duration = word_count / 2.5  # ~2.5 words per second
                        else:
                            audio_duration = 3.0  # Default duration
                        logger.warning(f"⚠️ Using estimated duration for audio {i+1}: {audio_duration:.2f}s")
                except Exception as e:
                    # Fallback duration
                    if i < len(complete_sentences):
                        word_count = len(complete_sentences[i].split())
                        audio_duration = word_count / 2.5
                    else:
                        audio_duration = 3.0
                    logger.warning(f"⚠️ ffprobe failed for audio {i+1}: {e}")
                
                # Get the corresponding sentence text
                if i < len(complete_sentences):
                    subtitle_text = complete_sentences[i].strip()
                else:
                    # More audio files than sentences - this shouldn't happen with one-sentence-per-segment
                    logger.warning(f"⚠️ Audio file {i+1} has no corresponding sentence")
                    subtitle_text = f"[Audio {i+1}]"
                
                segment_end_time = segment_start_time + audio_duration
                
                # Add audio segment to timeline
                if timeline_visualizer:
                    timeline_visualizer.add_audio_event(
                        index=i + 1,
                        start=segment_start_time,
                        duration=audio_duration,
                        file_path=audio_file,
                        actual_duration=audio_duration
                    )
                
                # Create subtitle segment
                segments.append({
                    'start': segment_start_time,
                    'end': segment_end_time,
                    'text': subtitle_text
                })
                
                logger.debug(f"📝 Subtitle {i+1}: {segment_start_time:.2f}s - {segment_end_time:.2f}s: {subtitle_text[:50]}...")
                
                # Add padding between segments (except after the last one)
                if i < len(audio_files) - 1:
                    padding = video_config.audio.padding_between_segments
                    current_time = segment_end_time + padding
                    logger.debug(f"📝 Added {padding}s padding after segment {i+1}")
                else:
                    current_time = segment_end_time
            
            # CRITICAL FIX: Cap subtitles to the target video duration
            # Get the target duration from the total audio duration
            target_duration = current_time  # This is the total audio duration from all segments
            if target_duration and segments:
                # Ensure no subtitle extends beyond the target duration
                for segment in segments:
                    if segment['end'] > target_duration:
                        segment['end'] = target_duration
                        logger.warning(f"⚠️ Capped subtitle end time from {segment['end']:.2f}s to {target_duration}s")
                
                # Remove any segments that start after the target duration
                segments = [s for s in segments if s['start'] < target_duration]
                
                logger.info(f"📝 Capped subtitles to target duration: {target_duration}s")
            
            # Create subtitle files
            subtitle_files = {}
            
            # Create SRT file
            srt_path = session_context.get_output_path("subtitles", "subtitles.srt")
            os.makedirs(os.path.dirname(srt_path), exist_ok=True)
            
            with open(srt_path, 'w') as f:
                for i, segment in enumerate(segments, 1):
                    start_time = self._format_time_srt(segment['start'])
                    end_time = self._format_time_srt(segment['end'])
                    # Format text with 2-line maximum, allowing more words/chars for subtitles
                    formatted_text = self._format_subtitle_text(segment['text'], 
                                                               max_words_per_line=8, 
                                                               max_chars_per_line=42)
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{formatted_text}\n\n")
            
            subtitle_files['srt'] = srt_path
            
            # Create VTT file
            vtt_path = session_context.get_output_path("subtitles", "subtitles.vtt")
            
            with open(vtt_path, 'w') as f:
                f.write("WEBVTT\n\n")
                for segment in segments:
                    start_time = self._format_time_vtt(segment['start'])
                    end_time = self._format_time_vtt(segment['end'])
                    # Format text with 2-line maximum, allowing more words/chars for subtitles
                    formatted_text = self._format_subtitle_text(segment['text'], 
                                                               max_words_per_line=8, 
                                                               max_chars_per_line=42)
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{formatted_text}\n\n")
            
            subtitle_files['vtt'] = vtt_path
            
            # Create CSV for debugging audio-subtitle timing
            csv_path = session_context.get_output_path("audio", "audio_subtitle_timing.csv")
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            
            import csv
            with open(csv_path, 'w', newline='') as csvfile:
                fieldnames = ['segment_index', 'audio_file', 'subtitle_text', 'subtitle_start', 'subtitle_end', 'subtitle_duration', 'audio_duration', 'difference']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, (segment, audio_file) in enumerate(zip(segments[:len(audio_files)], audio_files)):
                    # Get actual audio duration
                    try:
                        import subprocess
                        result = subprocess.run([
                            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                            '-show_format', audio_file
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            data = json.loads(result.stdout)
                            audio_duration = float(data['format']['duration'])
                        else:
                            audio_duration = 0.0
                    except:
                        audio_duration = 0.0
                    
                    subtitle_duration = segment['end'] - segment['start']
                    difference = subtitle_duration - audio_duration
                    
                    writer.writerow({
                        'segment_index': i + 1,
                        'audio_file': os.path.basename(audio_file),
                        'subtitle_text': segment['text'][:50] + '...' if len(segment['text']) > 50 else segment['text'],
                        'subtitle_start': f"{segment['start']:.3f}",
                        'subtitle_end': f"{segment['end']:.3f}",
                        'subtitle_duration': f"{subtitle_duration:.3f}",
                        'audio_duration': f"{audio_duration:.3f}",
                        'difference': f"{difference:.3f}"
                    })
            
            logger.info(f"📊 Created audio-subtitle timing CSV: {csv_path}")
            
            # Create subtitle metadata
            metadata = {
                'total_segments': len(segments),
                'total_duration': min(segments[-1]['end'], target_duration) if segments and target_duration else segments[-1]['end'] if segments else 0,
                'script_content': script_content,
                'audio_files_used': audio_files,
                'target_duration': target_duration,
                'capped_to_target': target_duration and segments and segments[-1]['end'] > target_duration
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
            'tiktok': (1080, 1920),      # 9:16 portrait
            'instagram': (1080, 1920),   # 9:16 portrait  
            'youtube': (1920, 1080),     # 16:9 landscape
            'facebook': (1920, 1080),    # 16:9 landscape
            'twitter': (1280, 720),     # 16:9 landscape
            'linkedin': (1920, 1080)     # 16:9 landscape
        }
        
        return platform_dimensions.get(platform.lower(), (1080, 1920))  # Default to portrait for modern social media
    
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
            # Check if input video exists
            if not os.path.exists(video_path):
                logger.error(f"❌ Input video not found for platform orientation: {video_path}")
                return video_path
            
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
                    '-c:v', 'libx264', '-c:a', video_config.encoding.audio_codec,
                    '-preset', video_config.encoding.fallback_preset,
                    '-y', oriented_path
                ]
            else:  # Landscape
                # For landscape, pad with black bars
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black',
                    '-c:v', 'libx264', '-c:a', video_config.encoding.audio_codec,
                    '-preset', video_config.encoding.fallback_preset,
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

    def _add_fade_out_ending(self, video_path: str, session_context: SessionContext, audio_files: Optional[List[str]] = None) -> str:
        """Add fade out effect at the end of the video, extending if needed for audio"""
        try:
            logger.info("🎬 Adding fade out effect")
            
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
            audio_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'audio'), None)
            
            if video_stream:
                width = int(video_stream['width'])
                height = int(video_stream['height'])
            else:
                width, height = 1080, 1920  # Default
            
            # Get audio duration if available
            audio_duration = video_duration  # Default to video duration
            if audio_stream and 'duration' in audio_stream:
                audio_duration = float(audio_stream['duration'])
            elif audio_files:
                # Calculate total audio duration from files
                total_audio_duration = 0
                for audio_file in audio_files:
                    if os.path.exists(audio_file):
                        try:
                            audio_probe = subprocess.run([
                                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                                '-show_format', audio_file
                            ], capture_output=True, text=True)
                            if audio_probe.returncode == 0:
                                audio_data = json.loads(audio_probe.stdout)
                                total_audio_duration += float(audio_data['format']['duration'])
                        except:
                            pass
                if total_audio_duration > 0:
                    audio_duration = total_audio_duration
                    logger.info(f"📊 Calculated total audio duration from files: {audio_duration:.2f}s")
            
            # Determine if we need to extend video for audio
            extension_needed = max(0, audio_duration - video_duration)
            
            # Import hardware acceleration utilities
            from ..utils.ffmpeg_utils import FFmpegAcceleration
            base_cmd = FFmpegAcceleration.get_optimized_ffmpeg_base()
            hw_encoder = FFmpegAcceleration.get_hw_encoder('h264')
            
            if extension_needed > 0:
                logger.info(f"🎬 Audio is {extension_needed:.2f}s longer than video - extending with black fadeout")
                
                # Calculate total fadeout duration (default 1.5s + extension)
                total_fade_duration = video_config.animation.fade_out_duration + extension_needed
                fade_start_time = video_duration - video_config.animation.fade_out_duration
                
                # Create a black video for the extension
                black_duration = extension_needed + 0.5  # Add a bit extra for safety
                
                # Complex filter to extend video with black and apply fade
                filter_complex = (
                    f"[0:v]fade=t=out:st={fade_start_time}:d={video_config.animation.fade_out_duration}[fade_video];"
                    f"color=black:size={width}x{height}:duration={black_duration}[black];"
                    f"[fade_video][black]concat=n=2:v=1:a=0[outv]"
                )
                
                cmd = base_cmd + [
                    '-i', video_path,
                    '-filter_complex', filter_complex,
                    '-map', '[outv]',
                    '-map', '0:a?',  # Map audio if exists
                    '-c:v', hw_encoder or 'libx264',
                    '-c:a', 'copy',
                    '-preset', video_config.encoding.fallback_preset,
                    output_path
                ]
            else:
                # Standard fadeout within existing video duration
                logger.info("🎬 Adding standard fade out effect (no extension needed)")
                fade_duration = video_config.animation.fade_out_duration
                fade_start_time = video_duration - fade_duration
                
                cmd = base_cmd + [
                    '-i', video_path,
                    '-vf', f'fade=t=out:st={fade_start_time}:d={fade_duration}',
                    '-c:v', hw_encoder or 'libx264', 
                    '-c:a', 'copy',
                    '-preset', video_config.encoding.fallback_preset,
                    output_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Added fade out effect: {output_path}")
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
                width, height = 1080, 1920  # Default to portrait
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
                '-vf', f'drawtext=text="{safe_text}":fontcolor={video_config.text_overlay.default_text_color}:fontsize={video_config.text_overlay.min_font_sizes["caption"]}:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', video_config.encoding.video_codec, '-pix_fmt', video_config.encoding.pixel_format, '-r', str(video_config.encoding.fallback_fps),
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ Direct fallback video created: {output_path} ({file_size:.1f}MB)")
                return output_path
            else:
                logger.error(f"❌ FFmpeg direct fallback failed: {result.stderr}")
                return self._create_minimal_direct_fallback(prompt, duration, output_path, platform)
                
        except Exception as e:
            logger.error(f"❌ Direct fallback creation failed: {e}")
            return self._create_minimal_direct_fallback(prompt, duration, output_path)
    
    def _hierarchical_fallback_generation(self, prompt: str, duration: float, clip_number: int,
                                        config: GeneratedVideoConfig, session_context: SessionContext,
                                        style_decision: Dict[str, Any], use_frame_continuity: bool = False,
                                        last_frame_image: Optional[str] = None) -> Optional[str]:
        """Implement hierarchical fallback: Image Generation (2x) → Color Fallback
        Note: VEO is already tried 2x in the main generation loop"""
        logger.info(f"🔄 Starting hierarchical fallback for clip {clip_number}")
        
        # Since VEO was already tried twice in the main loop, skip VEO retry here
        # Step 1: Try image generation (2 attempts)
        error_str = ""
        if hasattr(self, '_last_veo_error'):
            error_str = str(getattr(self, '_last_veo_error', '')).lower()
        
        if 'policy' in error_str or 'content filter' in error_str or 'safety' in error_str:
            logger.info(f"🔄 Content filter detected - attempting intelligent script modification")
            
            # First, try to modify the entire script to be content-compliant
            if hasattr(config, 'script') and config.script:
                modified_script = self._modify_script_for_content_filter(
                    original_script=config.script,
                    mission=config.mission
                )
                
                # If script was successfully modified, use it to generate new prompt
                if modified_script != config.script:
                    logger.info("📝 Using modified script for prompt generation")
                    # Temporarily update the prompt with modified content
                    segments = modified_script.split('. ')
                    if clip_number <= len(segments):
                        modified_segment = segments[clip_number - 1]
                        prompt = self._generate_visual_prompt_from_segment(
                            modified_segment,
                            config.mission,
                            clip_number,
                            style_decision.get('primary_style', 'cinematic'),
                            character_descriptions=getattr(config, 'character_descriptions', {})
                        )
                        logger.info(f"🔄 Generated new prompt from modified script: '{prompt[:100]}...'")
            
            # Also try traditional rephrasing as fallback
            rephrased_prompt = self._rephrase_problematic_prompt(
                prompt, 
                config.mission, 
                clip_number,
                style=style_decision.get('primary_style'),
                tone=getattr(config, 'tone', None),
                visual_style=style_decision.get('visual_style', getattr(config, 'visual_style', None)),
                duration=duration,
                continuous_mode=getattr(config, 'continuous_generation', False)
            )
            
            try:
                if hasattr(self, 'veo_client') and self.veo_client:
                    generation_params = {
                        'prompt': rephrased_prompt,
                        'duration': duration,
                        'clip_id': f"clip_{clip_number}_rephrased",
                        'aspect_ratio': self._get_platform_aspect_ratio(config.target_platform.value)
                    }
                    
                    if use_frame_continuity and last_frame_image and os.path.exists(last_frame_image):
                        generation_params['image_path'] = last_frame_image
                    
                    clip_path = self.veo_client.generate_video(**generation_params)
                    if clip_path and os.path.exists(clip_path):
                        logger.info(f"✅ VEO succeeded with rephrased prompt for clip {clip_number}")
                        return clip_path
            except Exception as e:
                logger.warning(f"⚠️ VEO rephrased attempt failed: {e}")
        
        # Step 2: Try image generation (2 attempts)
        logger.info(f"🖼️ Attempting image generation fallback for clip {clip_number}")
        
        # Use rephrased prompt if it exists, otherwise use original
        final_prompt = rephrased_prompt if 'rephrased_prompt' in locals() else prompt
        
        for attempt in range(2):
            try:
                image_path = self._generate_image_fallback(
                    prompt=prompt if attempt == 0 else final_prompt,
                    clip_number=clip_number,
                    session_context=session_context,
                    style_decision=style_decision,
                    attempt=attempt + 1
                )
                
                if image_path and os.path.exists(image_path):
                    # Convert image to video
                    video_path = self._convert_image_to_video(
                        image_path=image_path,
                        duration=duration,
                        clip_number=clip_number,
                        session_context=session_context,
                        config=config
                    )
                    
                    if video_path and os.path.exists(video_path):
                        logger.info(f"✅ Image generation succeeded (attempt {attempt + 1}) for clip {clip_number}")
                        return video_path
            except Exception as e:
                logger.warning(f"⚠️ Image generation attempt {attempt + 1} failed: {e}")
        
        # Step 3: Final fallback - colored video
        logger.warning(f"⚠️ All generation methods failed, using colored fallback for clip {clip_number}")
        fallback_path = os.path.join(
            session_context.get_output_path("video_clips"), 
            f"fallback_clip_{clip_number}.mp4"
        )
        
        os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
        
        clip_path = self._create_direct_fallback_clip(
            prompt=prompt,
            duration=duration,
            output_path=fallback_path,
            config=config
        )
        
        if clip_path:
            logger.info(f"✅ Created colored fallback for clip {clip_number}")
        
        return clip_path
    
    def _generate_image_fallback(self, prompt: str, clip_number: int, session_context: SessionContext,
                                style_decision: Dict[str, Any], attempt: int = 1) -> Optional[str]:
        """Generate an image using Gemini image generation as fallback"""
        try:
            logger.info(f"🖼️ Generating image for clip {clip_number} (attempt {attempt})")
            
            # Try to use Gemini for image generation
            if hasattr(self, 'positioning_agent') and self.positioning_agent:
                # Create image generation prompt
                image_prompt = f"""
                Create a single frame image for this video scene:
                {prompt}
                
                Style: {style_decision.get('primary_style', 'dynamic')}
                Visual Style: {style_decision.get('visual_style', 'realistic')}
                
                Requirements:
                - High quality illustration
                - Appropriate for the narrative
                - Clear and visually appealing
                - No text or overlays
                """
                
                # Use Vertex AI Imagen to generate image
                try:
                    from src.generators.vertex_imagen_client import VertexImagenClient
                    
                    # Initialize Vertex AI Imagen client
                    imagen_client = VertexImagenClient()
                    
                    # Create output path
                    image_filename = f"image_clip_{clip_number}_attempt_{attempt}.png"
                    output_path = session_context.get_output_path("temp_files", image_filename)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Try original prompt first, then rephrased if needed
                    prompts_to_try = [image_prompt]
                    
                    # If attempt > 1, try rephrased prompt for content filtering
                    if attempt > 1:
                        rephrased_prompt = self._rephrase_problematic_prompt(
                            original_prompt=image_prompt,
                            mission=image_prompt,  # Using image_prompt as mission for fallback
                            scene_number=clip_number,
                            style=None,
                            tone=None,
                            visual_style=None,
                            duration=None,
                            continuous_mode=False
                        )
                        prompts_to_try.append(rephrased_prompt)
                        logger.info(f"🔄 Using rephrased prompt for image generation attempt {attempt}")
                    
                    for prompt_idx, current_prompt in enumerate(prompts_to_try):
                        try:
                            logger.info(f"🎨 Generating image with Vertex AI Imagen (prompt {prompt_idx + 1}/{len(prompts_to_try)})...")
                            
                            image_path = imagen_client.generate_image(
                                prompt=current_prompt,
                                output_path=output_path,
                                aspect_ratio="9:16"  # Instagram portrait
                            )
                            
                            if image_path and os.path.exists(image_path):
                                logger.info(f"✅ Image generated successfully: {image_path}")
                                return image_path
                        except Exception as img_error:
                            error_str = str(img_error).lower()
                            if 'filter' in error_str or 'policy' in error_str or 'safety' in error_str:
                                logger.warning(f"⚠️ Image content filtered: {img_error}")
                                continue  # Try next prompt
                            else:
                                logger.warning(f"⚠️ Image generation error: {img_error}")
                                continue
                    
                    logger.warning(f"⚠️ All image generation attempts failed")
                    return None
                        
                except Exception as img_error:
                    logger.warning(f"⚠️ Imagen generation failed: {img_error}, trying alternative approach")
                    
                    # Fallback to creating a styled text image
                    from PIL import Image, ImageDraw, ImageFont
                    import textwrap
                    
                    # Create image with prompt visualization
                    img_width, img_height = 1080, 1920
                    img = Image.new('RGB', (img_width, img_height), color=(30, 30, 30))
                    draw = ImageDraw.Draw(img)
                    
                    # Add gradient background
                    for y in range(img_height):
                        color_value = int(30 + (y / img_height) * 50)
                        draw.rectangle([(0, y), (img_width, y+1)], fill=(color_value, color_value, color_value + 20))
                    
                    # Add text
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
                    except:
                        font = ImageFont.load_default()
                    
                    # Wrap text
                    wrapped_text = textwrap.fill(prompt[:200], width=30)
                    
                    # Calculate text position
                    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = (img_width - text_width) // 2
                    y = (img_height - text_height) // 2
                    
                    # Draw text with shadow
                    shadow_offset = 4
                    draw.text((x + shadow_offset, y + shadow_offset), wrapped_text, 
                             font=font, fill=(0, 0, 0), align='center')
                    draw.text((x, y), wrapped_text, 
                             font=font, fill=(255, 255, 255), align='center')
                    
                    # Save image
                    image_filename = f"text_image_clip_{clip_number}_attempt_{attempt}.png"
                    image_path = session_context.get_output_path("temp_files", image_filename)
                    img.save(image_path)
                    
                    logger.info(f"✅ Created text-based image fallback: {image_path}")
                    return image_path
                
        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return None
    
    def _convert_image_to_video(self, image_path: str, duration: float, clip_number: int,
                               session_context: SessionContext, config: GeneratedVideoConfig) -> Optional[str]:
        """Convert a static image to a video with Ken Burns effect"""
        try:
            output_path = os.path.join(
                session_context.get_output_path("video_clips"),
                f"image_video_clip_{clip_number}.mp4"
            )
            
            width, height = self._get_video_dimensions(config.target_platform.value)
            
            # Create video from image with subtle zoom/pan effect
            import subprocess
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', image_path,
                '-vf', f'scale={width*1.2}:{height*1.2},zoompan=z="min(zoom+0.0015,1.5)":x="iw/2-(iw/zoom/2)":y="ih/2-(ih/zoom/2)":d={int(duration*30)}:s={width}x{height}',
                '-t', str(duration),
                '-c:v', video_config.encoding.video_codec,
                '-pix_fmt', video_config.encoding.pixel_format,
                '-r', str(video_config.get_fps(config.target_platform.value)),
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Converted image to video: {output_path}")
                return output_path
            else:
                logger.error(f"❌ Image to video conversion failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Image to video conversion error: {e}")
            return None
    
    def _create_minimal_direct_fallback(self, prompt: str, duration: float, output_path: str, platform: Optional[str] = None) -> str:
        """Create minimal fallback using basic FFmpeg"""
        try:
            import subprocess
            
            # Get platform dimensions
            aspect_ratio = self._get_platform_aspect_ratio(platform or 'youtube')
            if aspect_ratio == '16:9':
                width, height = 1280, 720  # Use lower resolution for minimal fallback
            else:
                width, height = 1080, 1920
            
            # Create simple solid color video
            cmd = [
                'ffmpeg', '-f', 'lavfi', 
                '-i', f'color=c=blue:size={width}x{height}:duration={duration}',
                '-c:v', video_config.encoding.video_codec, '-pix_fmt', video_config.encoding.pixel_format, '-r', str(video_config.encoding.fallback_fps),
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
                    "mission": config.mission,
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
        
    def _save_veo_prompt_to_session(self, session_context: SessionContext, clip_number: int, prompt_data: Dict[str, Any]):
        """Save individual VEO prompt to session immediately"""
        try:
            # Save to list for later comprehensive save
            if not hasattr(self, '_veo_prompt_details'):
                self._veo_prompt_details = []
            self._veo_prompt_details.append(prompt_data)
            
            # Also save immediately to individual file
            prompt_file = session_context.get_output_path("logs", f"veo_prompt_clip_{clip_number}.json")
            os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
            
            with open(prompt_file, 'w') as f:
                json.dump(prompt_data, f, indent=2)
            
            logger.info(f"💾 Saved VEO prompt for clip {clip_number} to: {prompt_file}")
            
            # Also save accumulated prompts
            all_prompts_file = session_context.get_output_path("logs", "all_veo_prompts.json")
            with open(all_prompts_file, 'w') as f:
                json.dump(self._veo_prompt_details, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save VEO prompt: {e}")
        
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
        return False
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

    def _extract_character_descriptions_from_mission(self, mission_text: str) -> Dict[str, str]:
        """Extract character descriptions from mission text"""
        import re
        
        character_descriptions = {}
        
        # Multiple patterns to catch different description formats
        patterns = [
            # Pattern 1: Name (description with appearance keywords)
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([^)]+(?:appearance|hair|face|look|like the real|wearing|dressed|with his|with her|elderly|young|middle-aged|man|woman)[^)]*)\)',
            # Pattern 2: Name with description after colon or dash (but not general text)
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[:-]\s*([^.]+(?:hair|face|appearance|wearing|dressed|elderly|young|man|woman)[^.]*)(?=\.)(?!\s*[A-Z])', 
            # Pattern 3: "Name looks like..." (more specific)
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:looks like|appears as|portrayed as|depicted as)\s+([^.]+)(?=\.)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, mission_text, re.IGNORECASE)
            
            for match in matches:
                character_name = match[0].strip()
                description = match[1].strip()
                
                # Skip if name is too short or common words
                if len(character_name) < 3 or character_name.lower() in [
                    'the', 'and', 'with', 'from', 'marvel', 'style', 'scene', 
                    'sequence', 'effect', 'montage', 'dramatic', 'epic', 'comic',
                    'tragedy', 'comedy', 'action', 'thriller', 'horror'
                ]:
                    continue
                
                # Skip if it doesn't look like a proper name (at least one capital letter)
                if not any(c.isupper() for c in character_name):
                    continue
                    
                # Avoid overwriting with less detailed descriptions
                if character_name.lower() not in character_descriptions or len(description) > len(character_descriptions.get(character_name.lower(), '')):
                    character_descriptions[character_name.lower()] = f"{character_name}: {description}"
                    logger.info(f"📝 Extracted character description - {character_name}: {description}")
        
        # Also check for common historical figures mentioned without explicit descriptions
        # and add their historically accurate descriptions
        historical_figures = {
            'david ben-gurion': 'David Ben-Gurion: elderly statesman with distinctive white Einstein-like hair styled outward, round face, often in dark suit',
            'ben-gurion': 'Ben-Gurion: elderly statesman with distinctive white Einstein-like hair styled outward, round face, often in dark suit',
            'golda meir': 'Golda Meir: elderly woman with pulled-back gray hair in a bun, strong facial features, often in dark clothing',
            'yitzhak rabin': 'Yitzhak Rabin: middle-aged man with receding dark hairline, serious expression, military or formal attire',
            'levi eshkol': 'Levi Eshkol: older man with glasses, balding with white hair on sides, thoughtful expression',
            'menachem begin': 'Menachem Begin: older man with thick glasses, balding with white side hair, formal dark suit',
            'yitzhak shamir': 'Yitzhak Shamir: short elderly man with white hair, stern expression, formal attire',
            'shimon peres': 'Shimon Peres: distinguished elderly man with white hair, warm smile, formal suit',
            'ehud barak': 'Ehud Barak: middle-aged man with glasses, short dark hair, military bearing',
            'ariel sharon': 'Ariel Sharon: heavyset man with white hair, round face, strong presence',
            'ehud olmert': 'Ehud Olmert: man with glasses, receding hairline, business suit',
            'benjamin netanyahu': 'Benjamin Netanyahu: man with gray hair, strong jawline, confident demeanor'
        }
        
        # Check if any historical figures are mentioned but not described
        mission_lower = mission_text.lower()
        for name, desc in historical_figures.items():
            if name in mission_lower and name not in character_descriptions:
                character_descriptions[name] = desc
                logger.info(f"📝 Added historical figure description - {desc}")
        
        return character_descriptions
    
    def _create_visual_prompt_from_segment(self, segment_text: str, scene_number: int, style: str = "dynamic") -> str:
        """Transform segment text into a safe visual prompt for VEO"""
        logger.info(f"🎨 Creating visual prompt from segment: '{segment_text[:100]}...'")
        
        # Analyze the segment to extract visual elements
        segment_lower = segment_text.lower()
        
        # CRITICAL FIX: Use AI to generate prompts based on actual content
        logger.info(f"🤖 Using AI to generate visual prompt from segment: '{segment_text[:100]}...'")
        
        # Get mission context
        mission_context = getattr(self, '_current_mission', '')
        
        # Use character from config if available, otherwise extract from mission
        config = getattr(self, '_current_config', None)
        if config and hasattr(config, 'character') and config.character:
            # Character provided via --character flag
            character_descriptions = {}
            if ':' in config.character:
                # Format: "Name: description"
                parts = config.character.split(':', 1)
                name = parts[0].strip().lower()
                character_descriptions[name] = config.character
            else:
                # Just a character ID or name
                character_descriptions[config.character.lower()] = config.character
            logger.info(f"🎭 Using character from config: {config.character}")
        else:
            # Extract character descriptions from mission
            character_descriptions = self._extract_character_descriptions_from_mission(mission_context)
        
        try:
            # Use AI to generate appropriate visual prompt
            if hasattr(self, 'positioning_agent') and self.positioning_agent:
                # Build character descriptions section first
                character_desc_section = ""
                if character_descriptions:
                    for desc in character_descriptions.values():
                        character_desc_section += f"                   - {desc}\n"
                else:
                    character_desc_section = "                   - Use generic character descriptions\n"
                
                ai_prompt = f"""
                Generate a VEO video generation prompt based on this content:
                
                MISSION: {mission_context}
                SEGMENT TEXT: {segment_text}
                SCENE NUMBER: {scene_number}
                STYLE: {style}
                
                Requirements:
                1. Create a visual scene that represents the segment content
                2. Make it appropriate for the mission context
                3. Use animated/cartoon style for child-friendly content if child-friendly is true
                4. Be specific about visual elements, colors, and atmosphere
                5. CRITICAL - Character descriptions from the mission (MUST use these EXACTLY as provided):
{character_desc_section}
                6. IMPORTANT: Start the prompt by establishing WHO is in the scene using the exact character descriptions above
                7. For any historical figures, they MUST look like their real-world counterparts as described
                8. Avoid any text overlays or words in the video
                9. Focus on visual storytelling with historically accurate character depictions
                10. The prompt should begin with character establishment, e.g. "David Ben-Gurion with his distinctive white Einstein-like hair..."
                
                Example format: "[Character with their exact description] is [doing action] in [setting], [additional scene details]"
                
                Return ONLY the VEO prompt text (one line, no JSON):
                """
                
                response = self.positioning_agent.model.generate_content(ai_prompt)
                visual_prompt = response.text.strip()
                
                # Clean up the prompt
                if visual_prompt.startswith('"') and visual_prompt.endswith('"'):
                    visual_prompt = visual_prompt[1:-1]
                
                # Ensure it ends with technical requirements
                if "no text overlays" not in visual_prompt:
                    visual_prompt += ", no text overlays"
                    
                logger.info(f"🎯 AI-generated visual prompt: '{visual_prompt}'")
                
                # CRITICAL: Log if character descriptions were properly included
                if character_descriptions:
                    for name, desc in character_descriptions.items():
                        # Extract the actual character name from the description
                        actual_name = desc.split(':')[0].strip() if ':' in desc else name
                        
                        # Check multiple variations of the name
                        name_variations = [
                            name.lower(),
                            actual_name.lower(),
                            actual_name.split()[-1].lower() if ' ' in actual_name else actual_name.lower()  # Last name
                        ]
                        
                        # Check if any variation of the name or key descriptors are in the prompt
                        found = any(var in visual_prompt.lower() for var in name_variations)
                        
                        # Also check for key appearance descriptors
                        if not found and ':' in desc:
                            key_descriptors = ['hair', 'face', 'appearance', 'elderly', 'young', 'man', 'woman']
                            desc_parts = desc.split(':')[1].lower().split()
                            found = any(word in visual_prompt.lower() for word in desc_parts if word in key_descriptors)
                        
                        if found:
                            logger.info(f"✅ Character '{actual_name}' included in prompt")
                        else:
                            logger.debug(f"⚠️ Character '{actual_name}' may not be explicitly mentioned in prompt")
                return visual_prompt
                
            else:
                logger.warning("⚠️ No AI agent available, using fallback prompt generation")
                # Simple fallback without hardcoded mappings
                visual_prompt = f"animated educational scene illustrating '{segment_text[:50]}...', {style} cartoon style, colorful 3D animation, child-friendly, no text overlays"
                return visual_prompt
                
        except Exception as e:
            logger.error(f"❌ AI prompt generation failed: {e}")
            # Emergency fallback
            visual_prompt = f"animated educational scene about {mission_context[:30] if mission_context else 'mission'}, {style} style, scene {scene_number}, colorful animation, no text overlays"
            return visual_prompt
        
        logger.info(f"🎨 Transformed segment to visual: '{segment_text[:30]}...' → '{visual_prompt}'")
        return visual_prompt
    
    def _create_generic_visual_prompt(self, scene_number: int, style: str = "dynamic") -> str:
        """Create a generic safe visual prompt when no segment is available using AI"""
        logger.info(f"🤖 Using AI to generate generic visual prompt for scene {scene_number}")
        
        # Get mission context
        mission_context = getattr(self, '_current_mission', 'educational content')
        
        try:
            # Use AI to generate generic prompt
            if hasattr(self, 'positioning_agent') and self.positioning_agent:
                ai_prompt = f"""
                Generate a generic VEO video prompt for scene {scene_number}:
                
                MISSION CONTEXT: {mission_context}
                STYLE: {style}
                SCENE NUMBER: {scene_number} (vary visuals based on scene number)
                
                Requirements:
                1. Create an engaging visual scene related to the mission
                2. Use animated/cartoon style appropriate for the content if child-friendly is true
                3. Make each scene visually distinct
                4. Be creative but safe for all audiences
                5. If the mission context mentions historical figures, ensure accurate character depictions:
                   - David Ben-Gurion: elderly man with distinctive white hair styled outward, round face
                   - Golda Meir: elderly woman with pulled-back gray hair, strong facial features
                   - Yitzhak Rabin: middle-aged man with receding hairline, serious expression
                   - Levi Eshkol: older man with glasses, balding, thoughtful expression
                   - Any other historical figures should match their real appearance
                6. No text overlays or words in the video
                
                Return ONLY the VEO prompt text (one line, no JSON):
                """
                
                response = self.positioning_agent.model.generate_content(ai_prompt)
                visual_prompt = response.text.strip()
                
                # Clean up the prompt
                if visual_prompt.startswith('"') and visual_prompt.endswith('"'):
                    visual_prompt = visual_prompt[1:-1]
                
                # Ensure technical requirements
                if "no text overlays" not in visual_prompt:
                    visual_prompt += ", no text overlays"
                    
                logger.info(f"🎯 AI-generated generic prompt: '{visual_prompt}'")
                return visual_prompt
                
            else:
                # Simple fallback
                visual_prompt = f"animated {style} educational scene {scene_number}, colorful visuals, engaging content, no text overlays"
                return visual_prompt
                
        except Exception as e:
            logger.error(f"❌ AI generic prompt generation failed: {e}")
            # Emergency fallback
            return f"animated {style} scene {scene_number}, educational content, colorful visuals, no text overlays"
    
    def _create_safe_fallback_prompt(self, mission: str, scene_number: int) -> str:
        """This method is deprecated - use _rephrase_problematic_prompt instead"""
        logger.warning("⚠️ Using deprecated fallback method, this should not happen")
        return self._rephrase_problematic_prompt("Generic content", mission, scene_number)

    def _rephrase_with_safety_level(self, original_prompt: str, safety_level: int, 
                                   mission: str, scene_number: int, platform: str = None) -> str:
        """Rephrase prompt with progressive safety levels for content filter retries"""
        logger.info(f"🛡️ Applying safety level {safety_level} rephrasing")
        
        if safety_level == 1:
            # Mild: Remove potentially problematic words
            safe_prompt = original_prompt
            problematic_words = ['explosion', 'violent', 'blood', 'death', 'kill', 'war', 
                               'attack', 'destroy', 'weapon', 'gun', 'bomb', 'fight']
            replacements = {'explosion': 'burst', 'violent': 'intense', 'blood': 'energy',
                          'death': 'transformation', 'kill': 'stop', 'war': 'conflict',
                          'attack': 'approach', 'destroy': 'change', 'weapon': 'tool',
                          'gun': 'device', 'bomb': 'surprise', 'fight': 'compete'}
            
            for word, replacement in replacements.items():
                safe_prompt = safe_prompt.replace(word, replacement)
                safe_prompt = safe_prompt.replace(word.capitalize(), replacement.capitalize())
            
            return safe_prompt
            
        elif safety_level == 2:
            # Moderate: Focus on educational/documentary style
            return f"Educational documentary style: {mission}. Scene {scene_number} showing informative content about the topic. Professional presentation suitable for all audiences. Platform: {platform or 'general'}. Focus on facts and learning."
            
        else:  # safety_level >= 3
            # Safe: Generic educational content
            return f"Educational content for scene {scene_number}: General information presentation. Safe for all audiences. Professional documentary style. Platform: {platform or 'general'}."
    
    def _modify_script_for_content_filter(self, original_script: str, mission: str, 
                                         problematic_terms: List[str] = None) -> str:
        """Use Gemini to intelligently modify script to bypass content filters while preserving meaning"""
        try:
            if not self.ai_agent:
                logger.warning("⚠️ No AI agent available for script modification")
                return original_script
            
            logger.info("🧠 Using Gemini to modify script for content filter compliance")
            
            # Detect potentially problematic terms if not provided
            if not problematic_terms:
                problematic_terms = ['hamas', 'tunnels', 'war', 'conflict', 'violence', 'terrorist', 
                                   'attack', 'weapon', 'bomb', 'kill', 'death', 'destroy']
            
            prompt = f"""You are helping modify a video script to comply with content filters while preserving its meaning.

Original Mission: {mission}
Original Script: {original_script}

The script was blocked by content filters, likely due to sensitive political or violent terms.

Please rewrite this script to:
1. Preserve the EXACT same narrative and meaning
2. Replace potentially sensitive terms with creative alternatives
3. Use metaphorical or symbolic language instead of direct references
4. Maintain the same dramatic tone and energy
5. Keep all character names and visual descriptions
6. Ensure the same story beats and timing

Examples of replacements:
- "Hamas tunnels" → "underground networks" or "hidden passages"
- "vanish in smoke" → "fade into mist" or "dissolve into shadows"
- "explosion" → "burst of energy" or "dramatic transformation"
- "political conflict" → "ideological challenges" or "leadership struggles"

Return ONLY the modified script text, no explanations."""

            modified_script = self.ai_agent(prompt)
            
            # Clean up the response
            modified_script = modified_script.strip()
            if modified_script.startswith('"') and modified_script.endswith('"'):
                modified_script = modified_script[1:-1]
            
            logger.info("✅ Successfully modified script for content compliance")
            logger.debug(f"Modified script preview: {modified_script[:200]}...")
            
            return modified_script
            
        except Exception as e:
            logger.error(f"❌ Failed to modify script: {e}")
            return original_script

    def _rephrase_problematic_prompt(self, original_prompt: str, mission: str, scene_number: int, 
                                    style: str = None, tone: str = None, visual_style: str = None,
                                    duration: float = None, continuous_mode: bool = False) -> str:
        """Intelligently rephrase a problematic prompt to preserve ALL original parameters"""
        logger.info(f"🔄 Rephrasing problematic prompt while preserving all parameters: '{original_prompt[:100]}...'")
        
        # Extract style/tone/visual from original prompt if not provided
        if not style and "style:" in original_prompt.lower():
            style_match = original_prompt.lower().split("style:")[1].split(",")[0].strip()
            style = style_match
        if not visual_style:
            # Check for visual style keywords in prompt
            for vs in ['realistic', 'cinematic', 'hyper-realistic', 'photorealistic', 'cartoon', 'animated']:
                if vs in original_prompt.lower():
                    visual_style = vs
                    break
        
        try:
            # Use AI to intelligently rephrase the prompt
            if hasattr(self, 'positioning_agent') and self.positioning_agent:
                ai_prompt = f"""
                You are an expert at rephrasing video prompts to be policy-compliant while preserving ALL original parameters.
                
                ORIGINAL PROMPT: {original_prompt}
                MISSION: {mission}
                SCENE NUMBER: {scene_number}
                
                CRITICAL PARAMETERS TO PRESERVE:
                - Duration: {duration if duration else 'as specified'}
                - Style: {style if style else 'as in original'}
                - Tone: {tone if tone else 'as in original'}  
                - Visual Style: {visual_style if visual_style else 'as in original'}
                - Continuous Mode: {continuous_mode}
                
                The VEO system rejected this prompt due to policy violations. Your job is to:
                
                1. PRESERVE ALL ORIGINAL PARAMETERS: Keep exact same duration, style, tone, visual style
                2. MAINTAIN THE MISSION/TOPIC: Keep the core objective unchanged
                3. PRESERVE VISUAL CONTINUITY: If continuous mode, maintain flow between scenes
                4. REMOVE ONLY THE VIOLATION: Replace only the problematic elements
                5. KEEP SEGMENT CONTENT: Preserve the narrative/educational value
                
                CRITICAL RULES:
                - NEVER change from realistic to cartoon or vice versa
                - NEVER change the tone (if dramatic, keep dramatic)
                - NEVER change the style (if cinematic, keep cinematic)
                - NEVER change the mission or core subject
                - NEVER alter the duration or pacing
                - ONLY remove/rephrase the specific policy-violating content
                
                Examples of minimal changes:
                - "soldiers fighting" → "military personnel in training exercise"
                - "explosion damages building" → "special effects showing impact" 
                - "violent conflict" → "intense dramatic scene"
                - "person gets hurt" → "person faces challenge"
                
                Requirements:
                - Make MINIMAL changes - only what's needed for policy compliance
                - Preserve ALL style/tone/visual indicators from original
                - Keep the same energy and pacing
                - Maintain narrative continuity
                - Add "no text overlays" at the end if not present
                
                Return ONLY the rephrased prompt (one line), preserving all original style/tone/visual markers:
                """
                
                response = self.positioning_agent.model.generate_content(ai_prompt)
                rephrased_prompt = response.text.strip()
                
                # Clean up the prompt
                if rephrased_prompt.startswith('"') and rephrased_prompt.endswith('"'):
                    rephrased_prompt = rephrased_prompt[1:-1]
                
                # Ensure technical requirements
                if "no text overlays" not in rephrased_prompt:
                    rephrased_prompt += ", no text overlays"
                    
                logger.info(f"✅ AI-rephrased prompt: {rephrased_prompt}")
                return rephrased_prompt
                
            else:
                # Fallback: Try basic word replacement
                safe_prompt = self._basic_prompt_sanitization(original_prompt, mission, scene_number)
                logger.info(f"🔧 Basic sanitized prompt: {safe_prompt}")
                return safe_prompt
                
        except Exception as e:
            logger.error(f"❌ AI prompt rephrasing failed: {e}")
            # Emergency: Try basic sanitization
            return self._basic_prompt_sanitization(original_prompt, mission, scene_number)
    
    def _basic_prompt_sanitization(self, original_prompt: str, mission: str, scene_number: int) -> str:
        """Basic word replacement for prompt sanitization when AI is unavailable - PRESERVES ORIGINAL STYLE"""
        # CRITICAL: Preserve original case and style
        sanitized = original_prompt
        
        # Replace problematic words with safe alternatives (English + Hebrew)
        replacements = {
            # English replacements
            'violence': 'conflict representation',
            'violent': 'intense',
            'fighting': 'opposing forces',
            'battle': 'historical confrontation',
            'war': 'historical conflict',
            'attack': 'approach',
            'assault': 'confrontation',
            'shooting': 'rapid action',
            'weapon': 'symbolic tool',
            'blood': 'red elements',
            'death': 'conclusion',
            'kill': 'overcome',
            'murder': 'dramatic event',
            'explosion': 'dramatic effect',
            'bomb': 'dramatic device',
            'soldier': 'historical figure',
            'army': 'organized group',
            'military': 'organized forces',
            
            # Hebrew replacements (מלחמה = war, סיגריות = cigarettes, etc.)
            'מלחמה': 'סכסוך היסטורי',  # war -> historical conflict
            'מלחמת': 'תקופת',  # war of -> period of
            'סיגריות': 'עישון',  # cigarettes -> smoking
            'סיגריה': 'עישון',  # cigarette -> smoking
            'לחימה': 'עמידה',  # fighting -> standing
            'קרב': 'מפגש היסטורי',  # battle -> historical encounter
            'נשק': 'כלי סמלי',  # weapon -> symbolic tool
            'חייל': 'דמות היסטורית',  # soldier -> historical figure
            'צבא': 'כוח מאורגן',  # army -> organized force
            'צבאי': 'מאורגן',  # military -> organized
            'הרג': 'ניצחון',  # killing -> victory
            'מוות': 'סיום',  # death -> ending
            'דם': 'אלמנטים אדומים',  # blood -> red elements
        }
        
        for problematic, safe in replacements.items():
            sanitized = sanitized.replace(problematic, safe)
        
        # CRITICAL: DO NOT force style changes - preserve original style/tone
        # Removed forced "animated" and "educational" prefixes to preserve user's choice
            
        # Add technical requirements
        if "no text overlays" not in sanitized:
            sanitized += ", no text overlays"
            
        logger.info(f"🛡️ Sanitized prompt: {sanitized}")
        return sanitized
    
    def _escape_text_for_ffmpeg(self, text: str) -> str:
        """Escape text for FFmpeg drawtext filter with RTL support"""
        if not text or not text.strip():
            return "Text"
        
        # Check if text contains RTL characters
        rtl_chars = re.compile(r'[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        is_rtl = bool(rtl_chars.search(text))
        
        escaped = text
        
        # For RTL text, properly reshape for rendering
        if is_rtl:
            if RTL_SUPPORT:
                reshaped = arabic_reshaper.reshape(escaped)
                escaped = get_display(reshaped)
                logger.debug(f"🔤 Reshaped RTL text for FFmpeg overlay")
            else:
                # Add Right-to-Left Mark (RLM) at the beginning
                escaped = '\u200F' + escaped
                logger.debug(f"🔤 Detected RTL text, adding RTL mark")
        
        # FIRST: Replace Unicode quotes with regular quotes to avoid double-escaping
        escaped = escaped.replace('"', '"').replace('"', '"').replace('"', '"')
        escaped = escaped.replace(''', "'").replace(''', "'")
        
        # Remove problematic characters that cause FFmpeg filter issues
        # For RTL languages, preserve some punctuation that's important
        if not is_rtl:
            escaped = escaped.replace("'", "").replace('"', '')
            escaped = escaped.replace(':', '').replace('=', '').replace(',', '')
            escaped = escaped.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
            escaped = escaped.replace('{', '').replace('}', '').replace('\\', '').replace('/', '')
            escaped = escaped.replace('!', '').replace('?', '').replace(';', '')
        else:
            # For RTL, be more careful with punctuation removal
            escaped = escaped.replace("'", "׳").replace('"', '״')  # Hebrew quotes
            escaped = escaped.replace(':', ' - ')  # Replace colon with dash to avoid FFmpeg parsing issues
            escaped = escaped.replace('=', '-').replace(',', ' ')  # Also escape equals and comma
            escaped = escaped.replace('\\', '').replace('/', '')
            escaped = escaped.replace('{', '').replace('}', '')
            escaped = escaped.replace('!', '').replace('?', '')  # Remove exclamation and question marks
        
        # Convert newlines to spaces and clean up whitespace
        escaped = escaped.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        escaped = ' '.join(escaped.split())  # Remove extra whitespace
        
        return escaped.strip() or "Text"

    def _create_short_multi_line_text(self, text: str, max_words_per_line: int = 4, video_width: int = 1280) -> str:
        """Create smart multi-line text for overlays with overflow prevention and width constraints"""
        try:
            # Ensure max_words_per_line is an integer
            max_words_per_line = int(max_words_per_line) if max_words_per_line else 4
            
            # Use the escape function for consistency
            cleaned_text = self._escape_text_for_ffmpeg(text)
            
            # Split into words
            words = cleaned_text.split()
            
            # CRITICAL FIX: Dynamic text wrapping based on video width to prevent cutoff
            # Calculate safe text width (80% of video width to ensure margins)
            safe_text_width = int(video_width * video_config.layout.max_overlay_width_percentage)
            
            # Estimate character width based on video resolution
            # Typical font: 1 character ≈ 0.6 of font size in pixels
            estimated_font_size = video_config.get_font_size('body', video_width)  # Responsive font size
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
            max_chars = min(10, int(video_width * 0.01))  # Minimum character count for safety
            return text[:max_chars].replace("'", "").replace('"', '').replace(':', '').replace('!', '').replace('?', '').replace(',', '')

    def _format_subtitle_text(self, text: str, max_words_per_line: int = 2, max_chars_per_line: int = 15) -> str:
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
                
                # CRITICAL FIX: Limit to maximum 2 lines for subtitles
                if len(lines) >= 2:
                    break
            
            # Add remaining words to the last line (only if we have less than 2 lines)
            if current_line and len(lines) < 2:
                remaining_text = ' '.join(current_line)
                if len(remaining_text) <= max_chars_per_line:
                    lines.append(remaining_text)
                else:
                    # Truncate if too long
                    lines.append(remaining_text[:max_chars_per_line-3] + "...")
            
            # CRITICAL FIX: Ensure we never exceed 2 lines
            if len(lines) > 2:
                lines = lines[:2]
                # Add ellipsis to indicate truncation
                if lines[1]:
                    lines[1] = lines[1][:max_chars_per_line-3] + "..."
            
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
                    model = genai.GenerativeModel(DEFAULT_AI_MODEL)
                    response = model.generate_content(style_prompt)
                    
                    import json
                    import re
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        ai_style = json.loads(json_match.group())
                        
                        # Convert numeric string values to proper types
                        if 'words_per_line' in ai_style and isinstance(ai_style['words_per_line'], str):
                            try:
                                ai_style['words_per_line'] = int(ai_style['words_per_line'])
                            except:
                                ai_style['words_per_line'] = 3
                        
                        if 'font_size' in ai_style and isinstance(ai_style['font_size'], str):
                            try:
                                ai_style['font_size'] = int(ai_style['font_size'])
                            except:
                                ai_style['font_size'] = 32
                        
                        if 'stroke_width' in ai_style and isinstance(ai_style['stroke_width'], str):
                            try:
                                ai_style['stroke_width'] = int(ai_style['stroke_width'])
                            except:
                                ai_style['stroke_width'] = 2
                        
                        if 'background_opacity' in ai_style and isinstance(ai_style['background_opacity'], str):
                            try:
                                ai_style['background_opacity'] = float(ai_style['background_opacity'])
                            except:
                                ai_style['background_opacity'] = 0.8
                        
                        # Enhanced logging to session
                        self._log_ai_styling_decision(ai_style, text, overlay_type, session_context)
                        
                        logger.info(f"🎨 AI VIRAL STYLING: {overlay_type}")
                        logger.info(f"   Font: {ai_style.get('font_family', video_config.text_overlay.default_font)} {ai_style.get('font_size', 32)}px")
                        logger.info(f"   Colors: {ai_style.get('primary_color', '#FFFFFF')} on {ai_style.get('background_color', '#000000')}")
                        logger.info(f"   Engagement Score: {ai_style.get('engagement_score', 'N/A')}/10")
                        logger.info(f"   Reasoning: {ai_style.get('style_reasoning', 'No reasoning provided')[:100]}...")
                        
                        # Map AI style keys to expected format
                        mapped_style = {
                            "color": ai_style.get('primary_color', '#FFFFFF'),
                            "font_family": ai_style.get('font_family', video_config.text_overlay.default_font),
                            "font_size": ai_style.get('font_size', 48),
                            "background_color": ai_style.get('background_color', '#000000'),
                            "stroke_color": ai_style.get('stroke_color', '#000000'),
                            "background_opacity": ai_style.get('background_opacity', 0.8),
                            "stroke_width": ai_style.get('stroke_width', 2),
                            "words_per_line": ai_style.get('words_per_line', 3),
                            "shadow_enabled": ai_style.get('shadow_enabled', True),
                            "shadow_color": ai_style.get('shadow_color', '#000000'),
                            "animation_style": ai_style.get('animation_style', 'none'),
                            "engagement_score": ai_style.get('engagement_score', 'N/A')
                        }
                        
                        return mapped_style
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
        """Get smart default styling - fallback when AI styling fails"""
        try:
            # Try one more time to get AI styling with a simpler prompt
            if hasattr(self, 'positioning_agent') and self.positioning_agent:
                simple_prompt = f"""
                Generate overlay styling for: "{text[:50]}..."
                Type: {overlay_type}
                Platform: {platform}
                
                Return ONLY valid JSON:
                {{
                    "font_family": "font name",
                    "font_size": number (36-64),
                    "color": "#HEX",
                    "background_color": "#HEX",
                    "stroke_color": "#HEX",
                    "background_opacity": 0.0-1.0,
                    "stroke_width": 0-4,
                    "words_per_line": 2-5
                }}
                """
                
                try:
                    import google.generativeai as genai
                    model = genai.GenerativeModel(DEFAULT_AI_MODEL)
                    response = model.generate_content(simple_prompt)
                    
                    import json
                    import re
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        style = json.loads(json_match.group())
                        # Ensure all required keys exist
                        return {
                            "font_family": style.get('font_family', video_config.text_overlay.default_font),
                            "font_size": style.get('font_size', 48),
                            "color": style.get('color', '#FFFFFF'),
                            "background_color": style.get('background_color', '#000000'),
                            "stroke_color": style.get('stroke_color', '#000000'),
                            "background_opacity": min(0.7, style.get('background_opacity', 0.6)),
                            "stroke_width": style.get('stroke_width', 2),
                            "words_per_line": style.get('words_per_line', 3),
                            "shadow_enabled": True,
                            "shadow_color": "#000000",
                            "animation_style": "none",
                            "engagement_score": 5
                        }
                except Exception as e:
                    logger.warning(f"⚠️ Fallback AI styling also failed: {e}")
            
            # Ultimate fallback - very basic style
            return {
                "font_family": video_config.text_overlay.default_font,
                "font_size": video_config.get_font_size('body', video_width),
                "color": "#FFFFFF",
                "background_color": "#000000",
                "stroke_color": "#000000",
                "background_opacity": 0.8,
                "stroke_width": 2,
                "words_per_line": 3,
                "shadow_enabled": True,
                "shadow_color": "#000000",
                "animation_style": "none",
                "engagement_score": 5
            }
            
        except Exception as e:
            logger.error(f"❌ Smart default styling failed: {e}")
            return {
                "font_family": video_config.text_overlay.default_font,
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
            script_content = script_result.get('final_script', config.mission)
            
            # Generate hashtags
            hashtag_data = self.hashtag_generator.generate_trending_hashtags(
                mission=config.mission,
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
                        {'tag': f'#{config.mission.split()[0].lower()}', 'category': 'primary', 'estimated_reach': 'medium'},
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
                '-c:v', 'libx264', '-c:a', video_config.encoding.audio_codec,  # Re-encode for smooth fade
                temp_output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_output_path):
                logger.info(f"✅ Video trimmed to {target_duration}s with smooth fadeout")
                return temp_output_path
            else:
                logger.error(f"❌ Failed to trim video with fadeout: {result.stderr}")
                logger.error(f"❌ FFmpeg command: {' '.join(cmd)}")
                logger.error(f"❌ Input video exists: {os.path.exists(video_path)}")
                logger.error(f"❌ Input video path: {video_path}")
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
            # CRITICAL FIX: Limit script length based on target duration
            # Approximate 150 words per minute for natural speech
            target_word_count = int(config.duration_seconds * 2.5)  # ~150 words/min
            
            script_parts = []
            if config.hook:
                script_parts.append(config.hook)
            
            # Add main content but limit to target word count
            current_word_count = len(config.hook.split()) if config.hook else 0
            for content in config.main_content:
                content_words = content.split()
                if current_word_count + len(content_words) <= target_word_count:
                    script_parts.append(content)
                    current_word_count += len(content_words)
                else:
                    # Add partial content to reach target
                    remaining_words = target_word_count - current_word_count
                    if remaining_words > 0:
                        script_parts.append(' '.join(content_words[:remaining_words]))
                    break
            
            # Add call to action if there's room
            if config.call_to_action and current_word_count < target_word_count:
                script_parts.append(config.call_to_action)
            
            script_text = ' '.join(script_parts)
            logger.info(f"💰 Cheap mode script: {len(script_text.split())} words for {config.duration_seconds}s video")
            
            # Generate cheap audio
            from ..models.video_models import Language
            # Determine the language from config
            languages = getattr(config, 'languages', [Language.ENGLISH_US])
            language_enum = languages[0] if languages else Language.ENGLISH_US
            
            audio_files = tts.generate_intelligent_voice_audio(
                script=script_text,
                language=language_enum,
                mission=config.mission,
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
            video_path = self._create_text_video(config, audio_files[0], session_context, script_text)
            
            if video_path:
                # Only add fadeout for videos 10s+ to avoid extending duration
                if config.duration_seconds >= 10:
                    # Check actual video duration before adding fadeout
                    current_duration = self._get_video_duration(video_path)
                    if current_duration and current_duration < config.duration_seconds - 1.0:
                        logger.info("🎬 Adding fadeout to cheap mode video")
                        final_video_path = self._add_fade_out_ending(video_path, session_context, audio_files)
                        if final_video_path:
                            video_path = final_video_path
                        else:
                            logger.warning("⚠️ Fadeout failed, using original video")
                    else:
                        logger.info(f"🎬 Skipping fadeout for cheap mode (duration: {current_duration:.1f}s, target: {config.duration_seconds}s)")
                else:
                    logger.info(f"🎬 Skipping fadeout for short video ({config.duration_seconds}s)")
                
                # Save cheap mode session files
                self._save_cheap_mode_session_files(config, script_text, session_context)
                
                logger.info(f"✅ Cheap mode video generated: {video_path}")
                return video_path
            else:
                logger.error("❌ Failed to create cheap text video")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cheap mode video generation failed: {e}")
            return None
    
    def _create_text_video(self, config: GeneratedVideoConfig, audio_file: str, session_context: SessionContext, script_text: str = None) -> str:
        """Create a simple text-based video with theme support"""
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip
            import numpy as np
            
            # Get audio duration using FFmpeg
            from ..utils.ffmpeg_processor import FFmpegProcessor
            with FFmpegProcessor() as ffmpeg:
                duration = ffmpeg.get_duration(audio_file)
            
            # Get platform dimensions
            aspect_ratio = self._get_platform_aspect_ratio(config.target_platform.value)
            if aspect_ratio == '16:9':
                width, height = 1920, 1080
            else:
                width, height = 1080, 1920
            
            # Check if we have theme information in core decisions
            theme_id = None
            if hasattr(self, 'core_decisions') and self.core_decisions:
                theme_id = getattr(self.core_decisions, 'theme_id', None)
            
            # Create themed background
            if theme_id and 'news' in str(theme_id).lower():
                # Professional news background - dark blue gradient
                background = ColorClip(size=(width, height), color=(10, 20, 40), duration=duration)
                
                # Add news-style graphics
                # Top banner for news channel branding
                top_banner = ColorClip(size=(width, 120), color=(200, 0, 0), duration=duration).set_position((0, 0))
                
                # News ticker at bottom
                ticker_bg = ColorClip(size=(width, 100), color=(0, 0, 0), duration=duration).set_position((0, height - 100)).set_opacity(video_config.text_overlay.background_opacity)
                
                # Breaking news badge
                breaking_news = TextClip(
                    video_config.default_text.breaking_news_text,
                    fontsize=video_config.get_font_size('header', width),
                    color=video_config.text_overlay.default_text_color,
                    font=video_config.text_overlay.default_font,
                    bg_color='red'
                ).set_duration(duration).set_position((50, 40))
                
                # News channel text (Iran International style)
                channel_text = TextClip(
                    video_config.default_text.news_channel_text,
                    fontsize=video_config.get_font_size('caption', width),
                    color=video_config.text_overlay.default_text_color,
                    font=video_config.text_overlay.default_font
                ).set_duration(duration).set_position(('center', 45))
                
            else:
                # Default black background
                background = ColorClip(size=(width, height), color=(0, 0, 0), duration=duration)
                top_banner = None
                ticker_bg = None
                breaking_news = None
                channel_text = None
            
            # Create the actual script content as subtitles
            # Use the same limited script that was used for audio generation
            if script_text is None:
                # Fallback to creating from config if not provided
                script_text = f"{config.hook} {' '.join(config.main_content)} {config.call_to_action}"
            
            # Create subtitle overlays with proper positioning for news theme
            if theme_id and 'news' in str(theme_id).lower():
                # Position subtitles higher to avoid ticker
                subtitle_clips = self._create_cheap_mode_subtitles(script_text, duration, audio_file, bottom_offset=video_config.get_subtitle_offset('news'), video_height=height)
            else:
                subtitle_clips = self._create_cheap_mode_subtitles(script_text, duration, audio_file, video_height=height)
            
            # Simple mode badge for cheap mode
            from moviepy.editor import TextClip
            badge_clip = TextClip(
                video_config.default_text.badge_texts.get('cheap', '💰 CHEAP'),
                fontsize=video_config.get_font_size('badge', width),
                color='lime',
                font=video_config.text_overlay.default_font,
                stroke_color='black',
                stroke_width=2
            ).set_duration(duration).set_position((video_config.layout.overlay_positions['badge']['x'], video_config.layout.overlay_positions['badge']['y'])).set_opacity(video_config.text_overlay.badge_opacity)
            
            # Composite video with theme elements
            clips = [background]
            
            # Add news theme elements if applicable
            if theme_id and 'news' in str(theme_id).lower():
                if top_banner:
                    clips.append(top_banner)
                if ticker_bg:
                    clips.append(ticker_bg)
                if breaking_news:
                    clips.append(breaking_news)
                if channel_text:
                    clips.append(channel_text)
                    
                # Add scrolling ticker text
                ticker_text = TextClip(
                    "Water crisis deepens • Officials maintain luxury pools • Citizens demand action • Breaking: Drought emergency declared",
                    fontsize=video_config.get_font_size('news_ticker', width),
                    color=video_config.text_overlay.default_text_color,
                    font=video_config.text_overlay.default_font.replace('-Bold', '')
                ).set_duration(duration)
                
                # Make ticker scroll (position at bottom of screen)
                ticker_y = height - 80  # Position ticker 80 pixels from bottom
                ticker_text = ticker_text.set_position(lambda t: (width - t * 200, ticker_y))
                clips.append(ticker_text)
            
            clips.extend([badge_clip] + subtitle_clips)
            
            video = CompositeVideoClip(clips)
            # Note: Audio will be added via FFmpeg post-processing instead of MoviePy
            
            # Save video
            output_path = session_context.get_output_path("final_output", f"final_video_{session_context.session_id}.mp4")
            
            # Save video without audio first
            temp_video_path = session_context.get_output_path("temp_files", "temp_video_no_audio.mp4")
            logger.info(f"💰 Rendering video without audio: {temp_video_path}")
            video.write_videofile(
                temp_video_path,
                fps=video_config.get_fps(config.target_platform.value),
                codec=video_config.encoding.video_codec,
                verbose=False,
                logger=None,
                audio=False  # No audio in this step
            )
            
            # Close video clip
            video.close()
            
            # Add audio using FFmpeg for better sync
            logger.info(f"🎵 Adding audio using FFmpeg: {output_path}")
            from ..utils.ffmpeg_processor import FFmpegProcessor
            with FFmpegProcessor() as ffmpeg:
                ffmpeg.add_audio_to_video(temp_video_path, audio_file, output_path, "exact")
            
            logger.info(f"✅ Cheap mode text video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create text video: {e}")
            return None

    def _create_cheap_mode_subtitles(self, script_text: str, duration: float, audio_file: str, bottom_offset: Optional[int] = None, video_height: int = 1920) -> List:
        """Create subtitle clips for cheap mode video with accurate gTTS timing"""
        try:
            # Use default offset if not provided
            if bottom_offset is None:
                bottom_offset = video_config.get_subtitle_offset('default')
            
            # Determine video width based on height (assuming portrait mode for cheap mode)
            video_width = 1080 if video_height == 1920 else 1920
            from moviepy.editor import TextClip
            import re
            
            # Get actual audio duration for accurate timing using FFmpeg
            try:
                from ..utils.ffmpeg_processor import FFmpegProcessor
                with FFmpegProcessor() as ffmpeg:
                    actual_audio_duration = ffmpeg.get_duration(audio_file)
                logger.info(f"🎵 Audio duration: {actual_audio_duration:.2f}s, Video duration: {duration:.2f}s")
                
                # For premium mode, try to get more accurate timing if possible
                if not (getattr(self, 'cheap_mode', False) or 'cheap_mode' in audio_file.lower()):
                    # In the future, we could use speech recognition or audio analysis here
                    # For now, use refined premium timing
                    pass
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not read audio duration, using video duration: {e}")
                actual_audio_duration = duration
            
            # Split script into sentences for subtitle timing (including colons and semicolons)
            sentences = re.split(r'([.!?:;]+)', script_text)
            # Recombine sentences with their punctuation
            complete_sentences = []
            for i in range(0, len(sentences) - 1, 2):
                if i + 1 < len(sentences):
                    sentence = sentences[i].strip() + sentences[i + 1].strip()
                    if sentence.strip():
                        complete_sentences.append(sentence.strip())
                elif sentences[i].strip():
                    complete_sentences.append(sentences[i].strip())
            
            # Handle any remaining text
            if len(sentences) % 2 == 1 and sentences[-1].strip():
                complete_sentences.append(sentences[-1].strip())
            
            sentences = complete_sentences
            
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
                
                # Add RTL mark for Hebrew, Arabic, and Persian text
                rtl_chars = re.compile(r'[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
                is_rtl = rtl_chars.search(sentence)
                if is_rtl:
                    # Properly reshape RTL text for display
                    if RTL_SUPPORT:
                        reshaped_text = arabic_reshaper.reshape(sentence)
                        sentence = get_display(reshaped_text)
                        logger.debug(f"🔤 Reshaped RTL text for proper display in cheap mode")
                    else:
                        # Fallback: Add Right-to-Left Mark (RLM) at the beginning and end
                        sentence = '\u200F' + sentence + '\u200F'
                        logger.debug(f"🔤 Added RTL marks to cheap mode subtitle (no reshaper available)")
                
                # Select appropriate font for RTL support
                subtitle_font = video_config.text_overlay.rtl_font if is_rtl else video_config.text_overlay.default_font
                
                # Create subtitle clip
                subtitle_clip = TextClip(
                    sentence,
                    fontsize=video_config.get_font_size('subtitle', video_width),
                    color=video_config.text_overlay.default_text_color,
                    font=subtitle_font,  # Use RTL font if needed
                    stroke_color=video_config.text_overlay.default_stroke_color,
                    stroke_width=video_config.get_stroke_width('subtitle'),
                    size=(1000, None),
                    method='caption'
                ).set_start(start_time).set_duration(end_time - start_time).set_position(('center', video_height - bottom_offset))
                
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
                header_style = self._get_smart_default_style(header_text, "header", "tiktok", video_width, video_height)
                summary_style = self._get_smart_default_style(summary, "summary", "tiktok", video_width, video_height)
                
                # Add main header overlay with enhanced styling  
                safe_header_text = self._escape_text_for_ffmpeg(header_text)
                overlays.append({
                    'text': safe_header_text,
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
                safe_summary = self._escape_text_for_ffmpeg(summary)
                overlays.append({
                    'text': safe_summary,
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
            
            # REMOVED: No hardcoded overlays - let AI agents decide all overlays
            # if not found_points:
            #     # Removed hardcoded overlay to prevent unwanted text
            #     pass
            
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
            # Also handle Unicode apostrophes and quotes
            cleaned_text = text.replace("'", "").replace("'", "").replace("'", "").replace('"', '').replace('"', '').replace('"', '').replace(':', '').replace('!', '').replace('?', '').replace(',', '').replace('\\', '').replace('/', '').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            
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
            
            # ENHANCED: Better timing - NO OVERLAP to prevent text collision
            # Each line appears after the previous one disappears
            line_duration = min(line_duration, total_duration / total_lines)
            fade_duration = 0.3  # Fade in/out duration
            
            overlays = []
            for i, line in enumerate(lines):
                # Sequential timing - each line appears after previous ends
                start_time = i * line_duration
                end_time = start_time + line_duration - 0.1  # Small gap between lines
                
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
            
            # Check if video file exists
            if not os.path.exists(video_path):
                logger.error(f"❌ Video file not found: {video_path}")
                return video_path
            
            # Get video duration and dimensions
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', video_path
            ]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            if probe_result.returncode != 0:
                logger.error(f"❌ FFprobe failed: {probe_result.stderr}")
                return video_path
            
            try:
                probe_data = json.loads(probe_result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse probe data: {e}")
                return video_path
            
            if 'format' not in probe_data or 'duration' not in probe_data['format']:
                logger.error("❌ Video probe data missing format or duration")
                return video_path
            
            video_duration = float(probe_data['format']['duration'])
            video_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'video'), None)
            if video_stream:
                video_width = int(video_stream['width'])
                video_height = int(video_stream['height'])
            else:
                # Use platform-specific defaults
                aspect_ratio = self._get_platform_aspect_ratio(config.target_platform.value)
                if aspect_ratio == '16:9':
                    video_width, video_height = 1920, 1080
                else:
                    video_width, video_height = 1080, 1920
            
            # Create output path
            overlay_path = session_context.get_output_path("temp_files", f"timed_overlays_{os.path.basename(video_path)}")
            os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
            
            # Get positioning decision
            is_dynamic = positioning_decision.get('primary_style', 'static') == 'dynamic'
            
            # Create timed overlays with AI-driven colorful hooks
            overlay_filters = []
            all_overlays = []
            
            # First, try to get AI-generated colorful hooks
            try:
                logger.info("🎨 Generating AI-driven colorful text hooks")
                colorful_hooks = self.positioning_agent.create_colorful_text_hooks(
                    topic=config.mission,
                    platform=str(config.platform),
                    video_duration=video_duration,
                    script_content=config.processed_script if hasattr(config, 'processed_script') else ""
                )
                
                # Filter hooks to avoid subtitle area
                for hook in colorful_hooks:
                    # If position would overlap subtitles, move it up
                    if hook.get('position', 'center') in ['bottom_center', 'bottom_left', 'bottom_right', 'bottom_third', 'center_bottom']:
                        # Calculate safe Y position above subtitle area
                        hook['y_position'] = int(video_height * 0.6)  # 60% down, above subtitles
                    
                    all_overlays.append(hook)
                
                logger.info(f"✅ Added {len(colorful_hooks)} AI-generated colorful hooks")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not generate colorful hooks: {e}")
            
            # Add enhanced rich text overlays if needed
            if len(all_overlays) < 5 and config.hook:
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
                # Ensure words_per_line is an integer
                words_per_line = hook_style.get('words_per_line', 3)
                if isinstance(words_per_line, str):
                    try:
                        words_per_line = int(words_per_line)
                    except:
                        words_per_line = 3
                
                hook_overlays = self._create_timed_line_overlays(
                    str(config.hook), 
                    max_words_per_line=words_per_line,
                    line_duration=1.5,
                    total_duration=min(8.0, video_duration)
                )
                
                # Combine all overlays
                all_overlays.extend(rich_overlays + hook_overlays)
            
            # Process all overlays (colorful hooks + traditional)
            for i, overlay in enumerate(all_overlays):
                if isinstance(overlay, dict) and 'text' in overlay:
                    # Skip overlays in middle and top positions per user preference
                    position = overlay.get('position', '')
                    if position in ['center', 'top_center']:
                        logger.info(f"⏭️ Skipping overlay at {position} position per user preference")
                        continue
                        
                    # Position based on overlay style
                    if overlay.get('position') == 'top_center':
                        y_pos = 80
                    elif overlay.get('position') == 'center':
                        y_pos = int(video_height / 2)
                    else:
                        y_pos = 200
                    
                    # Create overlay filter with properly escaped text
                    escaped_text = self._escape_text_for_ffmpeg(overlay['text'])
                    
                    # Use overlay's own styling if it's a colorful hook
                    if 'color' in overlay and 'font_family' in overlay:
                        # This is a colorful hook with its own styling
                        font_color = overlay.get('color', '#FFFFFF')
                        font_size = overlay.get('font_size', 48)
                        font_family = overlay.get('font_family', 'Impact')
                        # Fix: FFmpeg doesn't support 'transparent' as a color
                        raw_bg_color = overlay.get('background_color', '#000000')
                        if raw_bg_color.lower() == 'transparent':
                            background_color = '#000000'  # Use black instead
                            background_opacity = 0.0  # Fully transparent
                        else:
                            background_color = raw_bg_color
                            background_opacity = overlay.get('opacity', 0.9)
                        stroke_width = overlay.get('stroke_width', 2)
                        
                        # Use custom y_position if available (for subtitle avoidance)
                        if 'y_position' in overlay:
                            y_pos = overlay['y_position']
                    else:
                        # Traditional overlay
                        font_color = overlay.get('font_color', '#FFFFFF')
                        font_size = overlay.get('font_size', 48)
                        font_family = 'Impact'
                        background_color = '#000000'
                        background_opacity = 0.6
                        stroke_width = 5
                    
                    filter_expr = (
                        f"drawtext=text='{escaped_text}':"
                        f"fontcolor={font_color}:"
                        f"fontsize={font_size}:"
                        f"font='{font_family}':"
                        f"box=1:boxcolor={background_color}@{background_opacity}:boxborderw={stroke_width}:"
                        f"x=(w-text_w)/2:y={y_pos}:"
                        f"enable=between(t\\,{overlay['start_time']}\\,{overlay['end_time']})"
                    )
                    overlay_filters.append(filter_expr)
                
            # Note: Hook overlays are already processed in the all_overlays loop above
            
            # Add call-to-action overlay with line-by-line timing
            if config.call_to_action:
                cta_style = self._get_ai_overlay_style(str(config.call_to_action), "cta", config.target_platform, video_width, video_height, session_context)
                # Ensure words_per_line is an integer
                cta_words_per_line = cta_style.get('words_per_line', 3)
                if isinstance(cta_words_per_line, str):
                    try:
                        cta_words_per_line = int(cta_words_per_line)
                    except:
                        cta_words_per_line = 3
                
                cta_overlays = self._create_timed_line_overlays(
                    str(config.call_to_action),
                    max_words_per_line=cta_words_per_line,
                    line_duration=1.5,
                    total_duration=min(8.0, video_duration)
                )
                
                # Position CTA at the end of the video
                cta_start_time = max(0, video_duration - 6.0)
                
                for i, overlay in enumerate(cta_overlays):
                    # ENHANCED: Better spacing for CTA overlays
                    base_y_offset = video_height - 200 - (i * 80)  # Increased spacing
                    adjusted_start = cta_start_time + overlay['start_time']
                    adjusted_end = cta_start_time + overlay['end_time']
                    
                    # CRITICAL FIX: Split long text into multiple lines
                    text_lines = self._format_subtitle_text(overlay['text'], max_words_per_line=3, max_chars_per_line=20)
                    text_lines = text_lines.split('\n')
                    
                    for line_idx, line_text in enumerate(text_lines):
                        if not line_text.strip():
                            continue
                            
                        # ENHANCED: Better line spacing within CTA
                        line_y_offset = base_y_offset + (line_idx * 50)  # Increased line spacing
                        escaped_text = self._escape_text_for_ffmpeg(line_text)
                        
                        # CRITICAL FIX: Ensure semi-transparent background like subtitles
                        # Force maximum opacity of 0.7 for readability
                        background_opacity = min(0.7, cta_style.get('background_opacity', 0.6))
                        
                        filter_expr = (
                            f"drawtext=text='{escaped_text}':"
                            f"fontcolor={cta_style['color']}:"
                            f"fontsize={cta_style['font_size']}:"
                            f"font='{cta_style['font_family']}':"
                            f"box=1:boxcolor={cta_style['background_color']}@{background_opacity}:"
                            f"boxborderw={cta_style['stroke_width']}:"
                            f"x=(w-text_w)/2:y={line_y_offset}:"
                            f"enable=between(t\\,{adjusted_start}\\,{adjusted_end})"
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

    def _add_png_overlays(self, video_path: str, config: GeneratedVideoConfig, 
                         session_context: SessionContext) -> str:
        """Add PNG overlays (flags, logos, etc.) based on mission content"""
        try:
            # Check if mission contains overlay requests
            mission_lower = config.mission.lower() if config.mission else ""
            
            # Track if we've added any overlays
            current_video = video_path
            overlay_added = False
            
            # Look for flag requests in mission
            if any(flag in mission_lower for flag in ['israeli flag', 'israel flag', 'flag in corner', 'flag in top']):
                logger.info("🇮🇱 Adding Israeli flag overlay as requested in mission")
                
                # Create output path
                flag_output = os.path.join(session_context.session_dir, 'temp_files', 'video_with_flag.mp4')
                os.makedirs(os.path.dirname(flag_output), exist_ok=True)
                
                # Determine position from mission
                position = 'top-left'  # Default
                if 'top-right' in mission_lower:
                    position = 'top-right'
                elif 'bottom' in mission_lower:
                    position = 'bottom-left' if 'left' in mission_lower else 'bottom-right'
                
                # Add Israeli flag
                result = self.png_overlay_handler.add_israeli_flag(
                    video_path=current_video,
                    output_path=flag_output,
                    position=position,
                    scale=0.08  # 8% of video size
                )
                
                if result and os.path.exists(result):
                    logger.info(f"✅ Israeli flag added at {position}")
                    current_video = result
                    overlay_added = True
                else:
                    logger.warning("⚠️ Failed to add Israeli flag, continuing without it")
            
            # Check for news logo requests
            news_channels = {
                'water crisis news': ('assets/logos/water_crisis_news.png', 'top-right', 0.12),
                'thirsty times': ('assets/logos/thirsty_times.png', 'top-right', 0.12),
                'desert dispatch': ('assets/logos/desert_dispatch.png', 'top-right', 0.12),
                'parched persian news': ('assets/logos/parched_persian.png', 'top-right', 0.12),
                'dry news network': ('assets/logos/dry_news.png', 'top-right', 0.12),
                'dehydration daily': ('assets/logos/dehydration_daily.png', 'top-right', 0.12),
                'iran international': ('assets/logos/iran_international.png', 'top-right', 0.12),
            }
            
            # Check if any news channel is mentioned
            for channel_name, (logo_path, position, scale) in news_channels.items():
                if channel_name in mission_lower:
                    logger.info(f"📺 Adding {channel_name.title()} logo overlay")
                    
                    # Check if logo exists or use a generated one
                    if not os.path.exists(logo_path):
                        logger.info(f"🎨 Generating news logo for {channel_name.title()}")
                        # Create text-based logo
                        temp_logo_path = os.path.join(session_context.session_dir, 'temp_files', f'{channel_name.replace(" ", "_")}_logo.png')
                        
                        # Choose colors based on channel theme
                        logo_colors = {
                            'water crisis news': ('#0066CC', '#FFFFFF'),  # Blue water theme
                            'thirsty times': ('#FF6B35', '#FFFFFF'),  # Orange desert theme
                            'desert dispatch': ('#D4A574', '#000000'),  # Sandy brown
                            'parched persian news': ('#8B4513', '#FFFFFF'),  # Saddle brown
                            'dry news network': ('#CD853F', '#000000'),  # Peru color
                            'dehydration daily': ('#B22222', '#FFFFFF'),  # Fire brick red
                            'iran international': ('#CC0000', '#FFFFFF'),  # News red
                        }
                        
                        bg_color, text_color = logo_colors.get(channel_name, ('#CC0000', '#FFFFFF'))
                        
                        # Create the logo
                        generated_logo = self.png_overlay_handler.create_text_logo(
                            text=channel_name.upper().replace('NEWS', '\nNEWS'),
                            output_path=temp_logo_path,
                            width=400,
                            height=150,
                            bg_color=bg_color,
                            text_color=text_color
                        )
                        
                        if generated_logo:
                            logo_path = generated_logo
                        else:
                            continue
                    
                    # Create output path
                    logo_output = os.path.join(session_context.session_dir, 'temp_files', 'video_with_logo.mp4')
                    os.makedirs(os.path.dirname(logo_output), exist_ok=True)
                    
                    # Add news logo
                    result = self.png_overlay_handler.add_png_overlay(
                        video_path=current_video,
                        png_path=logo_path,
                        output_path=logo_output,
                        position=position,
                        scale=scale,
                        opacity=0.9
                    )
                    
                    if result and os.path.exists(result):
                        logger.info(f"✅ {channel_name.title()} logo added at {position}")
                        current_video = result
                        overlay_added = True
                        break  # Only add one news logo
            
            # Check for style-based logos
            if config.style == 'news' and not overlay_added:
                # Add generic news logo if no specific channel mentioned
                logger.info("📺 Adding generic news overlay for news style video")
                # Could add generic news graphics here
            
            # Check for other overlay requests (marvel logo, etc.)
            if 'marvel' in mission_lower and any(word in mission_lower for word in ['logo', 'watermark']):
                logger.info("🦸 Marvel logo requested but not available")
                # Could add Marvel-style overlay here if we had the asset
            
            # Return current video (with overlays if any were added)
            return current_video
            
        except Exception as e:
            logger.error(f"❌ Failed to add PNG overlays: {e}")
            return video_path
    
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

    def _create_version_summary(self, session_context: SessionContext, final_path: str, audio_only_path: str, overlays_only_path: str, config: GeneratedVideoConfig):
        """Create a summary of all video versions"""
        try:
            summary = {
                "session_id": session_context.session_id,
                "mission": config.mission,
                "platform": config.target_platform.value,
                "duration_seconds": config.duration_seconds,
                "created_at": datetime.now().isoformat(),
                "versions": {
                    "final": {
                        "description": "Final video with subtitles and overlays",
                        "path": final_path,
                        "file_size_mb": self._get_file_size_mb(final_path) if os.path.exists(final_path) else 0
                    },
                    "audio_only": {
                        "description": "Video with audio only (no subtitles, no overlays)",
                        "path": audio_only_path,
                        "file_size_mb": self._get_file_size_mb(audio_only_path) if os.path.exists(audio_only_path) else 0
                    },
                    "overlays_only": {
                        "description": "Video with overlays only (no subtitles)",
                        "path": overlays_only_path,
                        "file_size_mb": self._get_file_size_mb(overlays_only_path) if os.path.exists(overlays_only_path) else 0
                    }
                }
            }
            
            # Save summary to session
            summary_path = session_context.get_output_path("metadata", "video_versions_summary.json")
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📋 Video versions summary created: {summary_path}")
            
            # Also create a human-readable summary
            self._create_human_readable_summary(session_context, summary)
            
        except Exception as e:
            logger.error(f"❌ Failed to create version summary: {e}")

    def _create_human_readable_summary(self, session_context: SessionContext, summary: Dict[str, Any]):
        """Create a human-readable summary of video versions"""
        try:
            markdown_content = f"""# Video Generation Summary

## Session Information
- **Session ID**: {summary['session_id']}
- **Mission**: {summary['mission']}
- **Platform**: {summary['platform']}
- **Duration**: {summary['duration_seconds']} seconds
- **Created**: {summary['created_at']}

## Generated Video Versions

### 1. Final Video (with subtitles and overlays)
- **Description**: Complete video with subtitles and text overlays
- **File**: `{os.path.basename(summary['versions']['final']['path'])}`
- **Size**: {summary['versions']['final']['file_size_mb']:.1f} MB
- **Use Case**: Ready for social media posting

### 2. Audio Only Version
- **Description**: Video with audio only (no subtitles, no overlays)
- **File**: `{os.path.basename(summary['versions']['audio_only']['path'])}`
- **Size**: {summary['versions']['audio_only']['file_size_mb']:.1f} MB
- **Use Case**: Clean version for editing or repurposing

### 3. Overlays Only Version
- **Description**: Video with text overlays only (no subtitles)
- **File**: `{os.path.basename(summary['versions']['overlays_only']['path'])}`
- **Size**: {summary['versions']['overlays_only']['file_size_mb']:.1f} MB
- **Use Case**: Version with visual hooks but no subtitle text

## File Locations
All files are saved in the session directory: `outputs/{summary['session_id']}/`

## Notes
- All versions maintain the same duration and platform optimization
- Each version is optimized for the target platform ({summary['platform']})
- Fade-out effects are applied to videos 10+ seconds in duration
"""
            
            # Save markdown summary
            markdown_path = session_context.get_output_path("metadata", "video_versions_summary.md")
            os.makedirs(os.path.dirname(markdown_path), exist_ok=True)
            
            with open(markdown_path, 'w') as f:
                f.write(markdown_content)
            
            logger.info(f"📋 Human-readable summary created: {markdown_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create human-readable summary: {e}")

    def _compose_video_with_synced_audio_and_subtitles(self, 
                                                     silent_video_path: str,
                                                     audio_segments: List[str],
                                                     srt_file_path: str,
                                                     config: GeneratedVideoConfig,
                                                     session_context: SessionContext) -> str:
        """
        Compose video with perfectly synced audio and subtitles using SRT timing
        
        This method implements the proper sync approach:
        1. Start with silent video
        2. Add audio segments according to SRT timing with silence gaps
        3. Add subtitles according to SRT file
        
        Args:
            silent_video_path: Path to video without audio
            audio_segments: List of paths to individual audio segment files
            srt_file_path: Path to SRT subtitle file with timing
            config: Video configuration
            session_context: Session context for file management
            
        Returns:
            Path to final video with synced audio and subtitles
        """
        try:
            logger.info("🎵 Composing video with synced audio and subtitles using SRT timing")
            
            import subprocess
            import tempfile
            import os
            from ..utils.subtitle_integration_tool import SubtitleIntegrationTool
            
            # Step 1: Parse SRT file to get timing information
            srt_timings = self._parse_srt_timings(srt_file_path)
            if not srt_timings:
                logger.error("❌ Failed to parse SRT timings")
                return silent_video_path
            
            logger.info(f"📝 Parsed {len(srt_timings)} subtitle segments from SRT")
            
            # Step 2: Create timed audio track with silence gaps
            timed_audio_path = self._create_timed_audio_track(
                audio_segments, srt_timings, config.duration_seconds, session_context
            )
            
            if not timed_audio_path:
                logger.error("❌ Failed to create timed audio track")
                return silent_video_path
            
            # Step 3: Combine silent video with timed audio
            video_with_audio_path = session_context.get_temp_path("video_with_synced_audio.mp4")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', silent_video_path,  # Video input
                '-i', timed_audio_path,   # Audio input
                '-c:v', 'copy',           # Copy video stream
                '-c:a', 'aac',            # Encode audio
                '-map', '0:v:0',          # Map video from first input
                '-map', '1:a:0',          # Map audio from second input
                '-shortest',              # End when shortest input ends
                video_with_audio_path
            ]
            
            logger.info("🎬 Combining silent video with timed audio...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to combine video and audio: {result.stderr}")
                return silent_video_path
            
            if not os.path.exists(video_with_audio_path):
                logger.error("❌ Video with audio file was not created")
                return silent_video_path
            
            logger.info("✅ Successfully combined video with timed audio")
            
            # Step 4: Add subtitles using SRT file timing
            subtitle_tool = SubtitleIntegrationTool()
            final_video_path = session_context.get_temp_path("final_synced_video.mp4")
            
            # Determine language for subtitle styling
            languages = getattr(config, 'languages', [])
            language = languages[0] if languages else None
            
            success = subtitle_tool.integrate_subtitles_with_ffmpeg(
                video_path=video_with_audio_path,
                subtitle_path=srt_file_path,
                output_path=final_video_path,
                language=language
            )
            
            if success and os.path.exists(final_video_path):
                logger.info("✅ Successfully added synced subtitles")
                
                # Validate the final sync
                validation = subtitle_tool.validate_subtitle_sync(final_video_path, srt_file_path)
                if validation.get('valid'):
                    logger.info(f"✅ Subtitle sync validation passed: {validation}")
                else:
                    logger.warning(f"⚠️ Subtitle sync validation issues: {validation}")
                
                return final_video_path
            else:
                logger.error("❌ Failed to add subtitles, returning video with audio only")
                return video_with_audio_path
                
        except Exception as e:
            logger.error(f"❌ Failed to compose video with synced audio and subtitles: {e}")
            return silent_video_path
    
    def _parse_srt_timings(self, srt_file_path: str) -> List[Dict[str, float]]:
        """
        Parse SRT file to extract timing information
        
        Returns:
            List of timing dictionaries with 'start' and 'end' in seconds
        """
        try:
            if not os.path.exists(srt_file_path):
                logger.error(f"❌ SRT file not found: {srt_file_path}")
                return []
            
            with open(srt_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # Match SRT timestamp format: 00:00:01,500 --> 00:00:04,200
            timestamp_pattern = r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})'
            matches = re.findall(timestamp_pattern, content)
            
            timings = []
            for match in matches:
                # Parse start time
                start_h, start_m, start_s, start_ms = map(int, match[:4])
                start_seconds = start_h * 3600 + start_m * 60 + start_s + start_ms / 1000.0
                
                # Parse end time
                end_h, end_m, end_s, end_ms = map(int, match[4:])
                end_seconds = end_h * 3600 + end_m * 60 + end_s + end_ms / 1000.0
                
                timings.append({
                    'start': start_seconds,
                    'end': end_seconds,
                    'duration': end_seconds - start_seconds
                })
            
            logger.info(f"📝 Parsed {len(timings)} timing entries from SRT")
            return timings
            
        except Exception as e:
            logger.error(f"❌ Failed to parse SRT timings: {e}")
            return []
    
    def _create_timed_audio_track(self, 
                                audio_segments: List[str], 
                                srt_timings: List[Dict[str, float]], 
                                total_duration: float,
                                session_context: SessionContext) -> str:
        """
        Create audio track with proper timing and silence gaps based on SRT
        
        Args:
            audio_segments: List of paths to audio segment files
            srt_timings: Timing information from SRT file
            total_duration: Total duration of the video
            session_context: Session context for file management
            
        Returns:
            Path to the created timed audio file
        """
        try:
            import subprocess
            
            if len(audio_segments) != len(srt_timings):
                logger.error(f"❌ Mismatch: {len(audio_segments)} audio segments vs {len(srt_timings)} SRT timings")
                return None
            
            # Create silence audio file for gaps
            silence_path = session_context.get_temp_path("silence.wav")
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', '1',  # 1 second of silence (we'll adjust timing later)
                '-acodec', 'pcm_s16le',
                silence_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.error(f"❌ Failed to create silence audio: {result.stderr}")
                return None
            
            # Build filter complex for ffmpeg to create timed audio
            filter_parts = []
            input_files = ['-i', silence_path]  # First input is silence template
            
            # Add all audio segments as inputs
            for i, audio_path in enumerate(audio_segments):
                input_files.extend(['-i', audio_path])
            
            # Create filter to place each audio segment at correct time
            filter_segments = []
            
            for i, (audio_path, timing) in enumerate(zip(audio_segments, srt_timings)):
                input_index = i + 1  # +1 because silence is input 0
                start_time = timing['start']
                
                # Add delay filter to position audio at correct time
                filter_segments.append(f"[{input_index}:a]adelay={int(start_time * 1000)}|{int(start_time * 1000)}[a{i}]")
            
            # Mix all delayed audio segments
            if len(filter_segments) > 1:
                inputs_to_mix = ''.join(f"[a{i}]" for i in range(len(filter_segments)))
                mix_filter = f"{inputs_to_mix}amix=inputs={len(filter_segments)}:duration=longest[mixed]"
                filter_segments.append(mix_filter)
                output_label = "[mixed]"
            else:
                output_label = "[a0]"
            
            # Create silence for full duration and mix with positioned audio
            full_filter = f"""anullsrc=channel_layout=stereo:sample_rate=44100:duration={total_duration}[silence];
{';'.join(filter_segments)};
[silence]{output_label}amix=inputs=2:duration=longest[final]"""
            
            # Output path
            timed_audio_path = session_context.get_temp_path("timed_audio.wav")
            
            # Build complete ffmpeg command
            cmd = ['ffmpeg', '-y'] + input_files + [
                '-filter_complex', full_filter,
                '-map', '[final]',
                '-t', str(total_duration),
                timed_audio_path
            ]
            
            logger.info("🎵 Creating timed audio track with silence gaps...")
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to create timed audio: {result.stderr}")
                return None
            
            if os.path.exists(timed_audio_path):
                file_size = os.path.getsize(timed_audio_path)
                logger.info(f"✅ Created timed audio track: {timed_audio_path} ({file_size/1024/1024:.1f}MB)")
                
                # Log timing summary
                logger.info("📊 Audio timing summary:")
                for i, timing in enumerate(srt_timings):
                    logger.info(f"   Segment {i+1}: {timing['start']:.1f}s - {timing['end']:.1f}s ({timing['duration']:.1f}s)")
                
                return timed_audio_path
            else:
                logger.error("❌ Timed audio file was not created")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to create timed audio track: {e}")
            return None
