#!/usr/bin/env python3
"""
Decision Framework - Centralized Decision Making System
Makes all key decisions upfront and propagates them throughout the system
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import numpy as np

from ..utils.logging_config import get_logger
from ..models.video_models import Platform, VideoCategory, Language
from ..utils.session_context import SessionContext
from ..agents.mission_planning_agent import MissionPlanningAgent
from ..agents.character_description_agent import CharacterDescriptionAgent


logger = get_logger(__name__)


class DecisionSource(Enum):
    """Source of a decision"""
    USER_CLI = "user_cli"
    USER_CONFIG = "user_config"
    AI_AGENT = "ai_agent"
    SYSTEM_DEFAULT = "system_default"


@dataclass
class Decision:
    """A single decision with metadata"""
    key: str
    value: Any
    source: DecisionSource
    confidence: float = 1.0
    reasoning: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CoreDecisions:
    """Core decisions that affect the entire system"""
    # Basic video parameters (no defaults)
    duration_seconds: int
    platform: Platform
    category: VideoCategory
    target_audience: str
    language: Language
    
    # Creative decisions (AI agents interpret these strings)
    style: str
    tone: str
    visual_style: str
    
    # Technical decisions (no defaults)
    frame_continuity: bool
    continuous_generation: bool
    mode: str
    cheap_mode: bool
    cheap_mode_level: str
    
    # Content decisions (no defaults)
    mission: str
    hook: str
    call_to_action: str
    
    # Voice decisions (no defaults)
    voice_strategy: str
    voice_personality: str
    voice_variety: bool
    
    # Visual decisions (no defaults)
    color_palette: str
    typography_style: str
    animation_style: str
    
    # Audio decisions (no defaults)
    background_music_style: str
    sound_effects_enabled: bool
    
    # Generation decisions (no defaults)
    num_clips: int
    clip_durations: List[float]
    
    # Theme and style reference (optional)
    theme_id: Optional[str] = None
    style_reference_id: Optional[str] = None
    
    # Character consistency system (optional)
    character_id: Optional[str] = None
    character_scene: Optional[str] = None
    character_image_path: Optional[str] = None
    
    # Original string values for AI agents to interpret (with defaults)
    category_string: str = ""
    style_string: str = ""
    tone_string: str = ""
    visual_style_string: str = ""
    
    # Clip structure optimization scores (with defaults)
    cost_efficiency_score: float = 0.0
    content_quality_score: float = 0.0
    optimal_balance_score: float = 0.0
    
    # Metadata (with defaults)
    decision_timestamp: str = ""
    session_id: str = ""
    
    def __post_init__(self):
        if not self.decision_timestamp:
            self.decision_timestamp = datetime.now().isoformat()


class DecisionFramework:
    """Central decision-making system"""
    
    def __init__(self, session_context: SessionContext, api_key: str = None):
        self.session_context = session_context
        self.decisions: Dict[str, Decision] = {}
        self.core_decisions: Optional[CoreDecisions] = None
        self.mission_planning_agent = None
        
        # Initialize Mission Planning Agent if API key is available
        if api_key:
            try:
                self.mission_planning_agent = MissionPlanningAgent(api_key)
                logger.info("🎯 Decision Framework initialized with Mission Planning Agent")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Mission Planning Agent: {e}")
                logger.info("🎯 Decision Framework initialized without Mission Planning Agent")
        else:
            logger.info("🎯 Decision Framework initialized without Mission Planning Agent")
    
    async def make_all_decisions(self, 
                          cli_args: Dict[str, Any],
                          user_config: Dict[str, Any] = None,
                          ai_agents_available: bool = True) -> CoreDecisions:
        """
        Make all core decisions upfront before any generation starts
        
        Args:
            cli_args: Arguments from CLI
            user_config: User configuration file
            ai_agents_available: Whether AI agents are available for decisions
            
        Returns:
            CoreDecisions object with all decisions made
        """
        logger.info("🎯 Making all core decisions upfront...")
        
        # 1. Basic video parameters (highest priority: CLI > config > default)
        duration_seconds = self._decide_duration(cli_args, user_config)
        platform = self._decide_platform(cli_args, user_config)
        category, category_string = self._decide_category(cli_args, user_config)
        target_audience = self._decide_target_audience(cli_args, user_config)
        language = self._decide_language(cli_args, user_config)
        
        # 2. Creative decisions (CLI > config > AI agents > default)
        style = self._decide_style(cli_args, user_config, ai_agents_available)
        tone = self._decide_tone(cli_args, user_config, ai_agents_available)
        visual_style = self._decide_visual_style(cli_args, user_config, ai_agents_available)
        
        # 2.5. Theme and style reference decisions
        theme_id = self._decide_theme(cli_args, user_config)
        style_reference_id = self._decide_style_reference(cli_args, user_config)
        
        # 2.6. Character consistency decisions
        character_id, character_scene, character_image_path = self._decide_character_consistency(cli_args, user_config)
        
        # 3. Technical decisions
        frame_continuity = self._decide_frame_continuity(duration_seconds, platform, ai_agents_available)
        continuous_generation = self._decide_continuous_generation(cli_args, duration_seconds, platform, ai_agents_available)
        mode = self._decide_mode(cli_args, user_config)
        cheap_mode = self._decide_cheap_mode(cli_args, user_config)
        cheap_mode_level = self._decide_cheap_mode_level(cli_args, user_config)
        
        # 4. Content decisions
        mission = self._decide_mission(cli_args, user_config)
        hook, call_to_action = self._decide_content_elements(mission, platform, ai_agents_available)
        
        # 5. Voice decisions (based on previous decisions)
        voice_strategy, voice_personality, voice_variety = self._decide_voice_strategy(
            mission, duration_seconds, platform, ai_agents_available
        )
        
        # 6. Visual decisions (based on previous decisions)
        color_palette, typography_style, animation_style = self._decide_visual_elements(
            visual_style, platform, ai_agents_available
        )
        
        # 7. Audio decisions
        background_music_style, sound_effects_enabled = self._decide_audio_elements(
            style, tone, platform, ai_agents_available
        )
        
        # 8. Generation decisions (based on all previous decisions)
        clip_structure = await self._decide_clip_structure_with_scores(
            duration_seconds, voice_strategy, ai_agents_available
        )
        num_clips = clip_structure['num_clips']
        clip_durations = clip_structure['clip_durations']
        
        # Create core decisions object
        self.core_decisions = CoreDecisions(
            duration_seconds=duration_seconds,
            platform=platform,
            category=category,
            target_audience=target_audience,
            language=language,
            style=style,
            tone=tone,
            visual_style=visual_style,
            category_string=category_string,
            style_string=style,
            tone_string=tone,
            visual_style_string=visual_style,
            frame_continuity=frame_continuity,
            continuous_generation=continuous_generation,
            mode=mode,
            cheap_mode=cheap_mode,
            cheap_mode_level=cheap_mode_level,
            mission=mission,
            hook=hook,
            call_to_action=call_to_action,
            voice_strategy=voice_strategy,
            voice_personality=voice_personality,
            voice_variety=voice_variety,
            color_palette=color_palette,
            typography_style=typography_style,
            animation_style=animation_style,
            background_music_style=background_music_style,
            sound_effects_enabled=sound_effects_enabled,
            num_clips=num_clips,
            clip_durations=clip_durations,
            theme_id=theme_id,
            style_reference_id=style_reference_id,
            character_id=character_id,
            character_scene=character_scene,
            character_image_path=character_image_path,
            cost_efficiency_score=clip_structure.get('cost_efficiency_score', 0.0),
            content_quality_score=clip_structure.get('content_quality_score', 0.0),
            optimal_balance_score=clip_structure.get('optimal_balance_score', 0.0),
            session_id=self.session_context.session_id
        )
        
        # Save decisions to session
        self._save_decisions_to_session()
        
        logger.info("✅ All core decisions made and saved")
        logger.info(f"   Duration: {duration_seconds}s")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Style: {style}")
        logger.info(f"   Tone: {tone}")
        logger.info(f"   Visual Style: {visual_style}")
        logger.info(f"   Voice Strategy: {voice_strategy}")
        logger.info(f"   Clips: {num_clips} clips")
        logger.info(f"   Clip Durations: {clip_durations}")
        logger.info(f"   Cost Efficiency: {clip_structure.get('cost_efficiency_score', 0):.2f}")
        logger.info(f"   Content Quality: {clip_structure.get('content_quality_score', 0):.2f}")
        logger.info(f"   Balance Score: {clip_structure.get('optimal_balance_score', 0):.2f}")
        
        return self.core_decisions
    
    def _decide_duration(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> int:
        """Decide video duration with 8-second clip constraint"""
        # Get base duration request
        requested_duration = None
        
        # CLI takes absolute priority
        if cli_args.get('duration'):
            requested_duration = int(cli_args['duration'])
            source = DecisionSource.USER_CLI
            source_desc = "User specified via CLI"
        # User config second priority
        elif user_config and user_config.get('duration_seconds'):
            requested_duration = int(user_config['duration_seconds'])
            source = DecisionSource.USER_CONFIG
            source_desc = "User specified in config"
        # System default
        else:
            requested_duration = 20
            source = DecisionSource.SYSTEM_DEFAULT
            source_desc = "System default"
        
        # Apply 8-second clip constraint: duration must be multiple of 8
        # Videos must be in 8-second aligned segments
        CLIP_DURATION = 8
        
        # Calculate number of clips needed - use ceiling to ensure we have enough clips
        import math
        num_clips = max(1, math.ceil(requested_duration / CLIP_DURATION))
        actual_content_duration = num_clips * CLIP_DURATION
        
        logger.info(f"📏 Duration calculation:")
        logger.info(f"   Requested: {requested_duration}s")
        logger.info(f"   Clips: {num_clips} x {CLIP_DURATION}s = {actual_content_duration}s")
        logger.info(f"   Aligned to 8-second segments (no fadeout addition)")
        
        # Record the actual content duration
        self._record_decision('duration_seconds', actual_content_duration, source, 1.0, 
                            f"{source_desc} - Aligned to {num_clips} x {CLIP_DURATION}s segments")
        
        return actual_content_duration
    
    def _decide_platform(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> Platform:
        """Decide target platform"""
        platform_str = cli_args.get('platform') or (user_config or {}).get('platform', 'tiktok')
        platform = Platform(platform_str.lower())
        source = DecisionSource.USER_CLI if cli_args.get('platform') else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('platform', platform.value, source, 1.0, f"Platform: {platform_str}")
        return platform
    
    def _decide_category(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> tuple[VideoCategory, str]:
        """Decide video category"""
        category_str = cli_args.get('category') or (user_config or {}).get('category', 'Entertainment')
        
        # Try to map to enum, but allow free-form strings for AI agents to interpret
        try:
            category = VideoCategory(category_str)
        except ValueError:
            # If not a valid enum, use OTHER and let AI agents handle the string
            category = VideoCategory.OTHER
            logger.info(f"🤖 Free-form category '{category_str}' will be interpreted by AI agents")
        
        source = DecisionSource.USER_CLI if cli_args.get('category') else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('category', category.value, source, 1.0, f"Category: {category_str}")
        self._record_decision('category_string', category_str, source, 1.0, f"Original category string: {category_str}")
        return category, category_str
    
    def _decide_target_audience(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> str:
        """Decide target audience"""
        audience = cli_args.get('target_audience') or (user_config or {}).get('target_audience', 'general audience')
        source = DecisionSource.USER_CLI if cli_args.get('target_audience') else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('target_audience', audience, source, 1.0, f"Target audience: {audience}")
        return audience
    
    def _decide_language(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> Language:
        """Decide content language"""
        # Check CLI args for languages
        if cli_args.get('languages'):
            languages = cli_args['languages']
            if languages and len(languages) > 0:
                # First language in the list is the primary language
                primary_language = languages[0]
                self._record_decision('language', primary_language, DecisionSource.USER_CLI, 1.0, f"Primary language from CLI: {primary_language.value}")
                # Also record all languages for multi-language support
                language_values = [lang.value for lang in languages]
                self._record_decision('all_languages', language_values, DecisionSource.USER_CLI, 1.0, f"All languages: {', '.join(language_values)}")
                return primary_language
        
        # Check user config
        if user_config and user_config.get('languages'):
            languages = user_config['languages']
            if languages and len(languages) > 0:
                primary_language = languages[0]
                self._record_decision('language', primary_language, DecisionSource.USER_CONFIG, 0.9, f"Primary language from config: {primary_language.value}")
                # Also record all languages
                language_values = [lang.value for lang in languages]
                self._record_decision('all_languages', language_values, DecisionSource.USER_CONFIG, 0.9, f"All languages: {', '.join(language_values)}")
                return primary_language
        
        # Default to English
        language = Language.ENGLISH_US
        self._record_decision('language', language, DecisionSource.SYSTEM_DEFAULT, 1.0, "Default language")
        self._record_decision('all_languages', [language.value], DecisionSource.SYSTEM_DEFAULT, 1.0, "Default language only")
        return language
    
    def _decide_style(self, cli_args: Dict[str, Any], user_config: Dict[str, Any], ai_available: bool) -> str:
        """Decide content style"""
        # CLI priority
        if cli_args.get('style'):
            style = cli_args['style']
            self._record_decision('style', style, DecisionSource.USER_CLI, 1.0, "User specified via CLI")
            self._record_decision('style_string', style, DecisionSource.USER_CLI, 1.0, f"Original style string: {style}")
            return style
        
        # Config priority
        if user_config and user_config.get('style'):
            style = user_config['style']
            self._record_decision('style', style, DecisionSource.USER_CONFIG, 0.9, "User specified in config")
            self._record_decision('style_string', style, DecisionSource.USER_CONFIG, 0.9, f"Original style string: {style}")
            return style
        
        # AI decision (if available)
        if ai_available:
            style = "viral"  # AI would decide this
            self._record_decision('style', style, DecisionSource.AI_AGENT, 0.8, "AI agent decision")
            self._record_decision('style_string', style, DecisionSource.AI_AGENT, 0.8, f"AI-generated style string: {style}")
            return style
        
        # Default
        style = "viral"
        self._record_decision('style', style, DecisionSource.SYSTEM_DEFAULT, 0.5, "System default")
        self._record_decision('style_string', style, DecisionSource.SYSTEM_DEFAULT, 0.5, f"Default style string: {style}")
        return style
    
    def _decide_tone(self, cli_args: Dict[str, Any], user_config: Dict[str, Any], ai_available: bool) -> str:
        """Decide content tone"""
        # Similar logic as style
        tone = cli_args.get('tone') or (user_config or {}).get('tone', 'engaging')
        source = DecisionSource.USER_CLI if cli_args.get('tone') else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('tone', tone, source, 1.0, f"Tone: {tone}")
        self._record_decision('tone_string', tone, source, 1.0, f"Original tone string: {tone}")
        return tone
    
    def _decide_visual_style(self, cli_args: Dict[str, Any], user_config: Dict[str, Any], ai_available: bool) -> str:
        """Decide visual style"""
        visual_style = cli_args.get('visual_style') or (user_config or {}).get('visual_style', 'dynamic')
        source = DecisionSource.USER_CLI if cli_args.get('visual_style') else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('visual_style', visual_style, source, 1.0, f"Visual style: {visual_style}")
        self._record_decision('visual_style_string', visual_style, source, 1.0, f"Original visual style string: {visual_style}")
        return visual_style
    
    def _decide_frame_continuity(self, duration: int, platform: Platform, ai_available: bool) -> bool:
        """Decide frame continuity - ENHANCED to prefer continuity"""
        # ENHANCED: Always prefer frame continuity for better quality
        # Only disable for very long videos (>120s) where cuts might be needed
        if ai_available:
            # Frame continuity is preferred for all durations up to 2 minutes
            continuity = duration <= 120  # Changed from 20 to 120 seconds
            self._record_decision('frame_continuity', continuity, DecisionSource.AI_AGENT, 0.95, 
                                f"AI decision: {duration}s duration on {platform.value} - continuity preferred for quality")
            return continuity
        
        # Default: Always enable frame continuity
        continuity = True
        self._record_decision('frame_continuity', continuity, DecisionSource.SYSTEM_DEFAULT, 0.9, "System default - frame continuity preferred")
        return continuity
    
    def _decide_continuous_generation(self, cli_args: Dict[str, Any], duration: int, platform: Platform, ai_available: bool) -> bool:
        """Decide continuous generation mode"""
        # First check if explicitly set in CLI
        if 'continuous' in cli_args:
            continuous = cli_args.get('continuous', False)
            self._record_decision('continuous_generation', continuous, DecisionSource.USER_CLI, 1.0, 
                                f"User specified continuous: {continuous}")
            return continuous
        
        # Otherwise let AI decide based on content
        if ai_available:
            # Continuous generation is good for longer narrative content
            continuous = duration >= 30 and platform in [Platform.YOUTUBE, Platform.INSTAGRAM]
            self._record_decision('continuous_generation', continuous, DecisionSource.AI_AGENT, 0.85, 
                                f"AI decision: {duration}s on {platform.value} - continuous={'enabled' if continuous else 'disabled'}")
            return continuous
        
        # Default: Disable continuous generation
        continuous = False
        self._record_decision('continuous_generation', continuous, DecisionSource.SYSTEM_DEFAULT, 0.7, 
                            "System default - continuous generation disabled")
        return continuous
    
    def _decide_mode(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> str:
        """Decide orchestrator mode"""
        mode = cli_args.get('mode', 'enhanced')
        source = DecisionSource.USER_CLI if cli_args.get('mode') else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('mode', mode, source, 1.0, f"Mode: {mode}")
        return mode
    
    def _decide_cheap_mode(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> bool:
        """Decide cheap mode"""
        cheap_mode = cli_args.get('cheap_mode', False)
        source = DecisionSource.USER_CLI if 'cheap_mode' in cli_args else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('cheap_mode', cheap_mode, source, 1.0, f"Cheap mode: {cheap_mode}")
        return cheap_mode
    
    def _decide_cheap_mode_level(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> str:
        """Decide cheap mode level"""
        level = cli_args.get('cheap_mode_level', 'full')
        source = DecisionSource.USER_CLI if 'cheap_mode_level' in cli_args else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('cheap_mode_level', level, source, 1.0, f"Cheap mode level: {level}")
        return level
    
    def _decide_mission(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> str:
        """Decide mission/topic"""
        mission = cli_args.get('mission') or cli_args.get('topic', 'Create engaging content')
        source = DecisionSource.USER_CLI if cli_args.get('mission') else DecisionSource.SYSTEM_DEFAULT
        self._record_decision('mission', mission, source, 1.0, f"Mission: {mission[:50]}...")
        return mission
    
    def _decide_content_elements(self, mission: str, platform: Platform, ai_available: bool) -> tuple:
        """Decide hook and call-to-action"""
        # Check if we're generating Hebrew content
        # Get the language decision we already made
        language = self.decisions.get('language', Decision(key='language', value=Language.ENGLISH_US, source=DecisionSource.SYSTEM_DEFAULT)).value
        
        if language == Language.HEBREW:
            # Hebrew defaults
            if ai_available:
                hook = "גלו את הסיפור המדהים!"
                cta = self._get_hebrew_cta_for_platform(platform)
                self._record_decision('hook', hook, DecisionSource.AI_AGENT, 0.8, "AI-generated Hebrew hook")
                self._record_decision('call_to_action', cta, DecisionSource.AI_AGENT, 0.8, "AI-generated Hebrew CTA")
            else:
                hook = "בואו לראות!"
                cta = "עקבו לעוד!"
                self._record_decision('hook', hook, DecisionSource.SYSTEM_DEFAULT, 0.5, "Default Hebrew hook")
                self._record_decision('call_to_action', cta, DecisionSource.SYSTEM_DEFAULT, 0.5, "Default Hebrew CTA")
        else:
            # English defaults
            if ai_available:
                # AI would generate these based on mission and platform
                hook = "Amazing content ahead!"
                cta = "Follow for more!"
                self._record_decision('hook', hook, DecisionSource.AI_AGENT, 0.8, "AI-generated hook")
                self._record_decision('call_to_action', cta, DecisionSource.AI_AGENT, 0.8, "AI-generated CTA")
            else:
                hook = "Check this out!"
                cta = "Like and subscribe!"
                self._record_decision('hook', hook, DecisionSource.SYSTEM_DEFAULT, 0.5, "Default hook")
                self._record_decision('call_to_action', cta, DecisionSource.SYSTEM_DEFAULT, 0.5, "Default CTA")
        
        return hook, cta
    
    def _get_hebrew_cta_for_platform(self, platform: Platform) -> str:
        """Get Hebrew CTA based on platform"""
        hebrew_ctas = {
            Platform.YOUTUBE: "הירשמו לעוד תוכן!",
            Platform.TIKTOK: "עקבו לחלק 2! 👀",
            Platform.INSTAGRAM: "שמרו לאחר כך! ❤️",
            Platform.FACEBOOK: "שתפו אם זה עזר לכם!"
        }
        return hebrew_ctas.get(platform, "עקבו לעוד!")
    
    def _decide_voice_strategy(self, mission: str, duration: int, platform: Platform, ai_available: bool) -> tuple:
        """Decide voice strategy"""
        if ai_available:
            # AI would decide based on content and duration
            strategy = "single" if duration <= 15 else "variety"
            personality = "storyteller"
            variety = strategy == "variety"
            self._record_decision('voice_strategy', strategy, DecisionSource.AI_AGENT, 0.8, 
                                f"AI decision: {duration}s duration")
        else:
            strategy = "single"
            personality = "narrator"
            variety = False
            self._record_decision('voice_strategy', strategy, DecisionSource.SYSTEM_DEFAULT, 0.5, "Default voice")
        
        return strategy, personality, variety
    
    def _decide_visual_elements(self, visual_style: str, platform: Platform, ai_available: bool) -> tuple:
        """Decide visual elements using AI"""
        if ai_available and hasattr(self, 'mission_agent') and self.mission_agent:
            try:
                prompt = f"""
                Decide visual elements for this video:
                
                VISUAL STYLE: {visual_style}
                PLATFORM: {platform.value}
                
                Consider platform aesthetics and style requirements.
                
                Return JSON:
                {{
                    "color_palette": "palette description",
                    "typography": "typography style",
                    "animation": "animation style",
                    "reasoning": "why these choices"
                }}
                """
                
                response = self.mission_agent.model.generate_content(prompt)
                result = self._parse_json_response(response.text)
                
                color_palette = result.get('color_palette', f'{visual_style} colors')
                typography = result.get('typography', f'{platform.value} optimized')
                animation = result.get('animation', f'{visual_style} transitions')
                
                self._record_decision('color_palette', color_palette, DecisionSource.AI_AGENT, 0.85, 
                                    result.get('reasoning', f"AI decision for {visual_style} style"))
                
            except Exception as e:
                logger.warning(f"AI visual elements failed: {e}")
                # Dynamic fallback
                color_palette = f"{visual_style} palette"
                typography = f"{platform.value} optimized"
                animation = f"{visual_style} transitions"
                self._record_decision('color_palette', color_palette, DecisionSource.SYSTEM_DEFAULT, 0.6, "Dynamic fallback")
        else:
            # Dynamic fallback
            color_palette = f"{visual_style} palette"
            typography = f"{platform.value} style"
            animation = f"{visual_style} motion"
            self._record_decision('color_palette', color_palette, DecisionSource.SYSTEM_DEFAULT, 0.5, "Style-based fallback")
        
        return color_palette, typography, animation
    
    def _decide_audio_elements(self, style: str, tone: str, platform: Platform, ai_available: bool) -> tuple:
        """Decide audio elements"""
        if ai_available:
            # AI would decide based on style and tone
            music_style = "upbeat" if style == "viral" else "ambient"
            sound_effects = tone == "engaging"
            self._record_decision('background_music_style', music_style, DecisionSource.AI_AGENT, 0.8, 
                                f"AI decision: {style} style, {tone} tone")
        else:
            music_style = "upbeat"
            sound_effects = True
            self._record_decision('background_music_style', music_style, DecisionSource.SYSTEM_DEFAULT, 0.5, "Default audio")
        
        return music_style, sound_effects
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from AI, handling markdown formatting"""
        try:
            # Clean up response
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            return json.loads(text.strip())
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI JSON response")
            return {}
    
    async def _decide_clip_structure_with_scores(self, duration: int, voice_strategy: str, ai_available: bool) -> Dict[str, Any]:
        """Decide clip structure using AI-based optimization with scores"""
        if ai_available:
            # AI-driven clip structure optimization
            clip_structure = await self._ai_optimize_clip_structure(duration, voice_strategy)
            self._record_decision('num_clips', clip_structure['num_clips'], DecisionSource.AI_AGENT, 0.9, 
                                clip_structure['reasoning'])
        else:
            # Simple fallback
            num_clips = max(2, duration // 5)
            clip_durations = [duration / num_clips] * num_clips
            clip_structure = {
                'num_clips': num_clips,
                'clip_durations': clip_durations,
                'reasoning': 'Default clip structure',
                'cost_efficiency_score': 0.5,
                'content_quality_score': 0.5,
                'optimal_balance_score': 0.5
            }
            self._record_decision('num_clips', num_clips, DecisionSource.SYSTEM_DEFAULT, 0.5, "Default clip structure")
        
        return clip_structure
    
    async def _ai_optimize_clip_structure(self, duration: int, voice_strategy: str) -> Dict[str, Any]:
        """AI-driven clip structure optimization using Mission Planning Agent"""
        # CRITICAL: Pre-calculate clip constraints BEFORE AI optimization
        # Force 8-second clips as per user requirement
        import math
        CLIP_DURATION = 8.0
        num_clips = max(1, math.ceil(duration / CLIP_DURATION))
        
        # Ensure duration is exactly multiple of 8
        if duration != num_clips * CLIP_DURATION:
            logger.warning(f"⚠️ Duration {duration}s is not multiple of 8. Adjusting to {num_clips * CLIP_DURATION}s")
            duration = int(num_clips * CLIP_DURATION)
        
        logger.info(f"📏 Pre-calculating clip constraints:")
        logger.info(f"   Total duration: {duration}s")
        logger.info(f"   Clip duration: {CLIP_DURATION}s")
        logger.info(f"   Number of clips: {num_clips}")
        
        try:
            # Use Mission Planning Agent if available
            if self.mission_planning_agent:
                # Get mission information from core decisions
                mission = self.decisions.get('mission', {}).value if 'mission' in self.decisions else "Create engaging content"
                platform = self.decisions.get('platform', {}).value if 'platform' in self.decisions else "tiktok"
                category = self.decisions.get('category', {}).value if 'category' in self.decisions else "Entertainment"
                
                # Convert platform and category to proper enums
                platform_enum = Platform(platform.lower()) if isinstance(platform, str) else platform
                category_enum = VideoCategory(category) if isinstance(category, str) else category
                
                # Analyze mission and get strategic clip recommendations
                # Pass the clip constraints to the mission planning agent
                mission_plan = await self.mission_planning_agent.analyze_mission(
                    mission_statement=mission,
                    duration=duration,
                    platform=platform_enum,
                    category=category_enum,
                    target_audience="general audience",
                    min_clips=num_clips  # Pass constraint to agent
                )
                
                # Get clip recommendations from mission plan
                clip_recommendation = self.mission_planning_agent.get_clip_recommendation(mission_plan)
                
                # Force 8-second clips
                clip_recommendation['num_clips'] = num_clips
                clip_recommendation['clip_durations'] = [CLIP_DURATION] * num_clips
                
                logger.info(f"🎯 Mission-Based Clip Structure:")
                logger.info(f"   Mission Type: {mission_plan.mission_type.value}")
                logger.info(f"   Strategic Mission: {mission_plan.is_strategic_mission}")
                logger.info(f"   Target Outcome: {mission_plan.target_outcome}")
                logger.info(f"   Recommended Clips: {clip_recommendation['num_clips']}")
                logger.info(f"   Strategic Reasoning: {clip_recommendation['reasoning'][:100]}...")
                logger.info(f"   Cost Efficiency: {clip_recommendation['cost_efficiency_score']:.2f}")
                logger.info(f"   Content Quality: {clip_recommendation['content_quality_score']:.2f}")
                
                # Save mission plan to session
                self._save_mission_plan(mission_plan)
                
                return clip_recommendation
            
            # Fallback to basic AI optimization if Mission Planning Agent not available
            logger.info("🤖 Using basic AI optimization (Mission Planning Agent not available)")
            clip_recommendation = self._basic_ai_optimize_clip_structure(duration, voice_strategy, num_clips)
            # Force 8-second clips
            clip_recommendation['num_clips'] = num_clips
            clip_recommendation['clip_durations'] = [CLIP_DURATION] * num_clips
            return clip_recommendation
            
        except Exception as e:
            logger.warning(f"⚠️ Mission-based clip optimization failed: {e}")
            logger.info("📋 Falling back to heuristic-based optimization")
        
        # Fallback to smart heuristic-based optimization
        clip_recommendation = self._heuristic_optimize_clip_structure(duration, voice_strategy, num_clips)
        # Force 8-second clips
        clip_recommendation['num_clips'] = num_clips
        clip_recommendation['clip_durations'] = [CLIP_DURATION] * num_clips
        return clip_recommendation
    
    def _enforce_max_clip_duration(self, clip_recommendation: Dict[str, Any], total_duration: int) -> Dict[str, Any]:
        """Enforce the clip duration constraint for VEO generation"""
        # Force 8-second clips as per requirement
        CLIP_DURATION = 8.0
        
        original_clips = clip_recommendation['num_clips']
        original_durations = clip_recommendation['clip_durations']
        
        # Check if any clip exceeds the 8-second limit
        needs_adjustment = any(duration > MAX_CLIP_DURATION for duration in original_durations)
        
        if needs_adjustment:
            logger.info(f"🔧 Enforcing 8-second maximum clip duration constraint")
            logger.info(f"   Original: {original_clips} clips, durations: {[f'{d:.1f}s' for d in original_durations]}")
            
            # Calculate minimum number of clips needed to stay under 8 seconds
            min_clips_needed = max(2, int(total_duration / MAX_CLIP_DURATION) + 1)
            
            # Use the higher of the original recommendation or the minimum needed
            new_num_clips = max(original_clips, min_clips_needed)
            
            # Redistribute duration evenly across clips
            new_durations = [total_duration / new_num_clips] * new_num_clips
            
            # Verify all clips are under the limit
            if any(duration > MAX_CLIP_DURATION for duration in new_durations):
                # If still over limit, add more clips
                new_num_clips = int(total_duration / MAX_CLIP_DURATION) + 1
                new_durations = [total_duration / new_num_clips] * new_num_clips
            
            # Update clip recommendation
            clip_recommendation['num_clips'] = new_num_clips
            clip_recommendation['clip_durations'] = new_durations
            
            # Update reasoning
            original_reasoning = clip_recommendation.get('reasoning', '')
            clip_recommendation['reasoning'] = f"{original_reasoning} [ADJUSTED: Enforced 5-second maximum clip duration constraint - increased from {original_clips} to {new_num_clips} clips]"
            
            # Adjust scores for the constraint enforcement
            if new_num_clips > original_clips:
                # More clips = slightly lower cost efficiency, slightly higher content quality
                clip_recommendation['cost_efficiency_score'] = max(0.6, clip_recommendation.get('cost_efficiency_score', 0.8) - 0.1)
                clip_recommendation['content_quality_score'] = min(1.0, clip_recommendation.get('content_quality_score', 0.8) + 0.05)
                clip_recommendation['optimal_balance_score'] = (clip_recommendation['cost_efficiency_score'] + clip_recommendation['content_quality_score']) / 2
            
            logger.info(f"   Adjusted: {new_num_clips} clips, durations: {[f'{d:.1f}s' for d in new_durations]}")
            logger.info(f"   Reason: VEO generation has 8-second maximum per clip")
            logger.info(f"   Updated Cost Efficiency: {clip_recommendation['cost_efficiency_score']:.2f}")
            logger.info(f"   Updated Content Quality: {clip_recommendation['content_quality_score']:.2f}")
            logger.info(f"   Updated Balance Score: {clip_recommendation['optimal_balance_score']:.2f}")
        else:
            logger.info(f"✅ All clips within 8-second limit: {[f'{d:.1f}s' for d in original_durations]}")
        
        return clip_recommendation
    
    def _heuristic_optimize_clip_structure(self, duration: int, voice_strategy: str, num_clips: int = 1) -> Dict[str, Any]:
        """Heuristic-based clip structure optimization with fixed 8-second clips"""
        
        # We're using fixed 8-second clips
        CLIP_DURATION = 8.0
        
        reasoning = f"Using {num_clips} fixed {CLIP_DURATION}-second clips for {duration}s video"
        
        # Calculate clip durations (all 8 seconds)
        clip_durations = [CLIP_DURATION] * num_clips
        
        # Calculate heuristic scores
        cost_efficiency_score = max(0, 1 - (num_clips - 2) * 0.2)  # Fewer clips = higher score
        content_quality_score = min(1, num_clips * 0.25)  # More clips = higher quality score
        optimal_balance_score = (cost_efficiency_score + content_quality_score) / 2
        
        logger.info(f"🧠 Heuristic Clip Structure Decision:")
        logger.info(f"   Duration: {duration}s → {num_clips} clips")
        logger.info(f"   Durations: {[f'{d:.1f}s' for d in clip_durations]}")
        logger.info(f"   Cost Efficiency: {cost_efficiency_score:.2f}")
        logger.info(f"   Content Quality: {content_quality_score:.2f}")
        logger.info(f"   Balance Score: {optimal_balance_score:.2f}")
        
        return {
            'num_clips': num_clips,
            'clip_durations': clip_durations,
            'reasoning': reasoning,
            'cost_efficiency_score': cost_efficiency_score,
            'content_quality_score': content_quality_score,
            'optimal_balance_score': optimal_balance_score
        }
    
    def _record_decision(self, key: str, value: Any, source: DecisionSource, confidence: float, reasoning: str):
        """Record a decision with metadata"""
        decision = Decision(
            key=key,
            value=value,
            source=source,
            confidence=confidence,
            reasoning=reasoning
        )
        self.decisions[key] = decision
        logger.debug(f"🎯 Decision: {key} = {value} (source: {source.value}, confidence: {confidence:.2f})")
    
    def _save_mission_plan(self, mission_plan):
        """Save mission plan to session"""
        try:
            mission_plan_path = self.session_context.get_output_path("decisions", "mission_plan.json")
            os.makedirs(os.path.dirname(mission_plan_path), exist_ok=True)
            
            # Convert mission plan to dict
            mission_dict = {
                'mission_statement': mission_plan.mission_statement,
                'mission_type': mission_plan.mission_type.value,
                'is_strategic_mission': mission_plan.is_strategic_mission,
                'target_outcome': mission_plan.target_outcome,
                'strategic_approach': mission_plan.strategic_approach,
                'success_metrics': mission_plan.success_metrics,
                'content_strategy': mission_plan.content_strategy,
                'clip_strategy': mission_plan.clip_strategy,
                'persuasion_tactics': mission_plan.persuasion_tactics,
                'timing_strategy': mission_plan.timing_strategy,
                'platform_optimization': mission_plan.platform_optimization,
                'risk_mitigation': mission_plan.risk_mitigation,
                'confidence_score': mission_plan.confidence_score,
                'reasoning': mission_plan.reasoning,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add new enhanced fields if available
            if hasattr(mission_plan, 'credibility_score') and mission_plan.credibility_score:
                mission_dict['credibility_score'] = {
                    'overall_score': mission_plan.credibility_score.overall_score,
                    'factual_accuracy': mission_plan.credibility_score.factual_accuracy,
                    'source_quality': mission_plan.credibility_score.source_quality,
                    'bias_level': mission_plan.credibility_score.bias_level,
                    'evidence_strength': mission_plan.credibility_score.evidence_strength,
                    'claims_verified': mission_plan.credibility_score.claims_verified,
                    'sources_found': mission_plan.credibility_score.sources_found,
                    'improvement_suggestions': mission_plan.credibility_score.improvement_suggestions,
                    'issues_detected': mission_plan.credibility_score.issues_detected,
                    'confidence_level': mission_plan.credibility_score.confidence_level,
                    'verification_timestamp': mission_plan.credibility_score.verification_timestamp
                }
            
            if hasattr(mission_plan, 'content_quality_analysis') and mission_plan.content_quality_analysis:
                mission_dict['content_quality_analysis'] = mission_plan.content_quality_analysis
            
            if hasattr(mission_plan, 'audience_intelligence') and mission_plan.audience_intelligence:
                mission_dict['audience_intelligence'] = {
                    'demographic_profile': {
                        'primary_age_group': mission_plan.audience_intelligence.demographic_profile.primary_age_group.value,
                        'age_distribution': mission_plan.audience_intelligence.demographic_profile.age_distribution,
                        'education_level': mission_plan.audience_intelligence.demographic_profile.education_level.value,
                        'primary_interests': [interest.value for interest in mission_plan.audience_intelligence.demographic_profile.primary_interests],
                        'platform_usage_patterns': mission_plan.audience_intelligence.demographic_profile.platform_usage_patterns,
                        'content_consumption_habits': mission_plan.audience_intelligence.demographic_profile.content_consumption_habits,
                        'engagement_preferences': mission_plan.audience_intelligence.demographic_profile.engagement_preferences,
                        'language_preferences': mission_plan.audience_intelligence.demographic_profile.language_preferences,
                        'cultural_context': mission_plan.audience_intelligence.demographic_profile.cultural_context,
                        'accessibility_needs': mission_plan.audience_intelligence.demographic_profile.accessibility_needs
                    },
                    'psychographic_profile': {
                        'personality_traits': mission_plan.audience_intelligence.psychographic_profile.personality_traits,
                        'values_priorities': mission_plan.audience_intelligence.psychographic_profile.values_priorities,
                        'lifestyle_indicators': mission_plan.audience_intelligence.psychographic_profile.lifestyle_indicators,
                        'decision_making_style': mission_plan.audience_intelligence.psychographic_profile.decision_making_style,
                        'information_processing_preference': mission_plan.audience_intelligence.psychographic_profile.information_processing_preference,
                        'social_influence_susceptibility': mission_plan.audience_intelligence.psychographic_profile.social_influence_susceptibility,
                        'brand_loyalty_level': mission_plan.audience_intelligence.psychographic_profile.brand_loyalty_level,
                        'innovation_adoption_rate': mission_plan.audience_intelligence.psychographic_profile.innovation_adoption_rate,
                        'content_sharing_likelihood': mission_plan.audience_intelligence.psychographic_profile.content_sharing_likelihood,
                        'engagement_drivers': mission_plan.audience_intelligence.psychographic_profile.engagement_drivers
                    },
                    'content_adaptation_strategy': {
                        'reading_level': mission_plan.audience_intelligence.content_adaptation_strategy.reading_level,
                        'vocabulary_complexity': mission_plan.audience_intelligence.content_adaptation_strategy.vocabulary_complexity,
                        'sentence_length_preference': mission_plan.audience_intelligence.content_adaptation_strategy.sentence_length_preference,
                        'visual_style_recommendations': mission_plan.audience_intelligence.content_adaptation_strategy.visual_style_recommendations,
                        'color_palette_preferences': mission_plan.audience_intelligence.content_adaptation_strategy.color_palette_preferences,
                        'font_recommendations': mission_plan.audience_intelligence.content_adaptation_strategy.font_recommendations,
                        'content_pacing': mission_plan.audience_intelligence.content_adaptation_strategy.content_pacing,
                        'cultural_sensitivity_notes': mission_plan.audience_intelligence.content_adaptation_strategy.cultural_sensitivity_notes,
                        'accessibility_optimizations': mission_plan.audience_intelligence.content_adaptation_strategy.accessibility_optimizations,
                        'platform_specific_adaptations': mission_plan.audience_intelligence.content_adaptation_strategy.platform_specific_adaptations
                    },
                    'engagement_prediction': mission_plan.audience_intelligence.engagement_prediction,
                    'optimization_recommendations': mission_plan.audience_intelligence.optimization_recommendations,
                    'confidence_score': mission_plan.audience_intelligence.confidence_score,
                    'analysis_timestamp': mission_plan.audience_intelligence.analysis_timestamp
                }
            
            if hasattr(mission_plan, 'ethical_optimization') and mission_plan.ethical_optimization:
                mission_dict['ethical_optimization'] = {
                    'transparency_assessment': {
                        'level': mission_plan.ethical_optimization.transparency_assessment.level.value,
                        'intent_clarity': mission_plan.ethical_optimization.transparency_assessment.intent_clarity,
                        'source_attribution': mission_plan.ethical_optimization.transparency_assessment.source_attribution,
                        'bias_disclosure': mission_plan.ethical_optimization.transparency_assessment.bias_disclosure,
                        'method_transparency': mission_plan.ethical_optimization.transparency_assessment.method_transparency,
                        'ethical_considerations': mission_plan.ethical_optimization.transparency_assessment.ethical_considerations,
                        'disclosure_recommendations': mission_plan.ethical_optimization.transparency_assessment.disclosure_recommendations,
                        'transparency_score': mission_plan.ethical_optimization.transparency_assessment.transparency_score,
                        'assessment_timestamp': mission_plan.ethical_optimization.transparency_assessment.assessment_timestamp
                    },
                    'educational_value_metrics': {
                        'value_category': mission_plan.ethical_optimization.educational_value_metrics.value_category.value,
                        'learning_objectives': mission_plan.ethical_optimization.educational_value_metrics.learning_objectives,
                        'knowledge_transfer_potential': mission_plan.ethical_optimization.educational_value_metrics.knowledge_transfer_potential,
                        'skill_development_opportunities': mission_plan.ethical_optimization.educational_value_metrics.skill_development_opportunities,
                        'retention_likelihood': mission_plan.ethical_optimization.educational_value_metrics.retention_likelihood,
                        'practical_applicability': mission_plan.ethical_optimization.educational_value_metrics.practical_applicability,
                        'cognitive_engagement_level': mission_plan.ethical_optimization.educational_value_metrics.cognitive_engagement_level,
                        'educational_effectiveness': mission_plan.ethical_optimization.educational_value_metrics.educational_effectiveness,
                        'measurement_timestamp': mission_plan.ethical_optimization.educational_value_metrics.measurement_timestamp
                    },
                    'positive_engagement_profile': {
                        'engagement_type': mission_plan.ethical_optimization.positive_engagement_profile.engagement_type.value,
                        'constructive_discussion_potential': mission_plan.ethical_optimization.positive_engagement_profile.constructive_discussion_potential,
                        'critical_thinking_stimulation': mission_plan.ethical_optimization.positive_engagement_profile.critical_thinking_stimulation,
                        'collaborative_learning_opportunities': mission_plan.ethical_optimization.positive_engagement_profile.collaborative_learning_opportunities,
                        'positive_behavior_promotion': mission_plan.ethical_optimization.positive_engagement_profile.positive_behavior_promotion,
                        'harmful_engagement_risks': mission_plan.ethical_optimization.positive_engagement_profile.harmful_engagement_risks,
                        'mitigation_strategies': mission_plan.ethical_optimization.positive_engagement_profile.mitigation_strategies,
                        'overall_positive_impact': mission_plan.ethical_optimization.positive_engagement_profile.overall_positive_impact,
                        'engagement_timestamp': mission_plan.ethical_optimization.positive_engagement_profile.engagement_timestamp
                    },
                    'ethical_compliance_score': mission_plan.ethical_optimization.ethical_compliance_score,
                    'optimization_recommendations': mission_plan.ethical_optimization.optimization_recommendations,
                    'ethical_guidelines_followed': mission_plan.ethical_optimization.ethical_guidelines_followed,
                    'potential_improvements': mission_plan.ethical_optimization.potential_improvements,
                    'overall_ethical_rating': mission_plan.ethical_optimization.overall_ethical_rating,
                    'analysis_timestamp': mission_plan.ethical_optimization.analysis_timestamp
                }
            
            with open(mission_plan_path, 'w') as f:
                json.dump(mission_dict, f, indent=2, default=str)
            
            logger.info(f"💾 Mission plan saved to session: {mission_plan_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save mission plan: {e}")
    
    def _basic_ai_optimize_clip_structure(self, duration: int, voice_strategy: str, num_clips: int = 1) -> Dict[str, Any]:
        """Basic AI optimization without Mission Planning Agent"""
        try:
            import google.generativeai as genai
            from ..config.ai_model_config import DEFAULT_AI_MODEL
            
            # Configure AI model
            model = genai.GenerativeModel(DEFAULT_AI_MODEL)
            
            # Simple AI prompt for clip structure optimization
            prompt = f"""
You are an expert video production optimizer. Provide strategic reasoning for a {duration}-second video.

CONSTRAINTS:
- Duration: {duration} seconds
- Number of clips: {num_clips} (fixed at 8 seconds each)
- Voice Strategy: {voice_strategy}

VIDEO STRUCTURE:
- Each clip is exactly 8 seconds long
- Total content duration: {num_clips} x 8 = {duration} seconds
- A 1.5-second fadeout will be added after the final clip

Provide strategic reasoning in this exact JSON format:
{{
    "num_clips": {num_clips},
    "clip_durations": {[8.0] * num_clips},
    "reasoning": "<explain how to best use these {num_clips} 8-second clips>",
    "cost_efficiency_score": <float 0-1>,
    "content_quality_score": <float 0-1>,
    "optimal_balance_score": <float 0-1>
}}
"""
            
            response = model.generate_content(prompt)
            
            # Parse AI response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                ai_decision = json.loads(json_match.group())
                
                # Validate AI decision
                num_clips = max(max(2, min_clips_needed), min(5, int(ai_decision['num_clips'])))
                clip_durations = ai_decision['clip_durations']
                
                # Ensure durations sum to target duration
                total_duration = sum(clip_durations)
                if abs(total_duration - duration) > 0.5:
                    # Adjust proportionally
                    scaling_factor = duration / total_duration
                    clip_durations = [d * scaling_factor for d in clip_durations]
                
                # Ensure we have the right number of clips
                if len(clip_durations) != num_clips:
                    clip_durations = [duration / num_clips] * num_clips
                
                logger.info(f"🤖 Basic AI Clip Structure Decision:")
                logger.info(f"   Duration: {duration}s → {num_clips} clips")
                logger.info(f"   Durations: {[f'{d:.1f}s' for d in clip_durations]}")
                logger.info(f"   Reasoning: {ai_decision['reasoning'][:100]}...")
                
                return {
                    'num_clips': num_clips,
                    'clip_durations': clip_durations,
                    'reasoning': ai_decision['reasoning'],
                    'cost_efficiency_score': ai_decision.get('cost_efficiency_score', 0),
                    'content_quality_score': ai_decision.get('content_quality_score', 0),
                    'optimal_balance_score': ai_decision.get('optimal_balance_score', 0)
                }
            
        except Exception as e:
            logger.warning(f"⚠️ Basic AI clip structure optimization failed: {e}")
        
        # Fallback to heuristic
        return self._heuristic_optimize_clip_structure(duration, voice_strategy, min_clips_needed)
    
    def _decide_theme(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> Optional[str]:
        """Decide which theme to use if any"""
        # Check CLI args first
        if cli_args.get('theme'):
            self._record_decision("theme_id", cli_args['theme'], DecisionSource.USER_CLI, 
                                confidence=1.0, reasoning=f"Theme specified by user: {cli_args['theme']}")
            return cli_args['theme']
        
        # Check user config
        if user_config and user_config.get('theme'):
            self._record_decision("theme_id", user_config['theme'], DecisionSource.USER_CONFIG,
                                confidence=1.0, reasoning=f"Theme from user config: {user_config['theme']}")
            return user_config['theme']
        
        # No theme specified
        self._record_decision("theme_id", None, DecisionSource.SYSTEM_DEFAULT, 
                            confidence=1.0, reasoning="No theme specified")
        return None
    
    def _decide_style_reference(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> Optional[str]:
        """Decide which style reference to use if any"""
        # Check CLI args first
        if cli_args.get('style_reference'):
            self._record_decision("style_reference_id", cli_args['style_reference'], DecisionSource.USER_CLI,
                                confidence=1.0, reasoning=f"Style reference specified by user: {cli_args['style_reference']}")
            return cli_args['style_reference']
        
        # Check user config
        if user_config and user_config.get('style_reference'):
            self._record_decision("style_reference_id", user_config['style_reference'], DecisionSource.USER_CONFIG,
                                confidence=1.0, reasoning=f"Style reference from user config: {user_config['style_reference']}")
            return user_config['style_reference']
        
        # No style reference specified
        self._record_decision("style_reference_id", None, DecisionSource.SYSTEM_DEFAULT, 
                            confidence=1.0, reasoning="No style reference specified")
        return None
    
    def _decide_character_consistency(self, cli_args: Dict[str, Any], user_config: Dict[str, Any]) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Decide character consistency parameters"""
        character_id = None
        character_scene = None
        character_image_path = None
        
        # Check CLI args for character
        if cli_args.get('character'):
            character_id = cli_args['character']
            character_scene = cli_args.get('scene', 'professional setting')
            
            self._record_decision("character_id", character_id, DecisionSource.USER_CLI,
                                confidence=1.0, reasoning=f"Character specified by user: {character_id}")
            self._record_decision("character_scene", character_scene, DecisionSource.USER_CLI,
                                confidence=1.0, reasoning=f"Character scene: {character_scene}")
            
            # Generate character image for this scene
            try:
                from ..utils.character_reference_manager import CharacterReferenceManager
                char_manager = CharacterReferenceManager()
                
                # Check if character_id is an existing stored character or a description
                if character_id in char_manager.characters:
                    # It's a stored character ID, use the existing system
                    character_image_path = char_manager.get_character_for_mission(character_id, character_scene)
                    
                    if character_image_path:
                        self._record_decision("character_image_path", character_image_path, DecisionSource.SYSTEM_DEFAULT,
                                            confidence=0.9, reasoning="Generated character scene image for video consistency")
                    else:
                        logger.warning(f"Failed to generate character scene for stored character {character_id}")
                else:
                    # It's a character description, not a stored ID
                    # Log info instead of warning since this is expected behavior
                    logger.info(f"Character description provided instead of stored ID: {character_id[:50]}...")
                    logger.info("Character consistency will be handled by video generation prompts")
                    # Don't generate image for descriptions, let the video generator handle it
                    
            except Exception as e:
                logger.error(f"Character image generation failed: {e}")
        
        return character_id, character_scene, character_image_path
    
    def _save_decisions_to_session(self):
        """Save all decisions to session"""
        try:
            # Save core decisions
            decisions_path = self.session_context.get_output_path("decisions", "core_decisions.json")
            os.makedirs(os.path.dirname(decisions_path), exist_ok=True)
            
            with open(decisions_path, 'w') as f:
                json.dump(asdict(self.core_decisions), f, indent=2, default=str)
            
            # Save individual decisions with metadata
            individual_decisions_path = self.session_context.get_output_path("decisions", "decision_log.json")
            decisions_dict = {k: asdict(v) for k, v in self.decisions.items()}
            
            with open(individual_decisions_path, 'w') as f:
                json.dump(decisions_dict, f, indent=2, default=str)
            
            logger.info(f"💾 Decisions saved to session: {decisions_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save decisions: {e}")
    
    def get_decisions(self) -> CoreDecisions:
        """Get the core decisions"""
        if not self.core_decisions:
            raise ValueError("Decisions not yet made. Call make_all_decisions() first.")
        return self.core_decisions
    
    def get_decision(self, key: str) -> Any:
        """Get a specific decision value"""
        if key in self.decisions:
            return self.decisions[key].value
        elif self.core_decisions and hasattr(self.core_decisions, key):
            return getattr(self.core_decisions, key)
        else:
            raise KeyError(f"Decision '{key}' not found")
    def _extract_character_description(self, mission_text: str) -> str:
        """Extract character description from mission text using AI research"""
        try:
            # Use Character Description Agent for accurate descriptions
            from ..agents.character_description_agent import CharacterDescriptionAgent
            char_agent = CharacterDescriptionAgent(self.api_service_config.get('google_ai_api_key'))
            
            character_data = char_agent.describe_character(mission_text)
            
            # Build comprehensive description
            description_parts = []
            if character_data.get('character_description'):
                description_parts.append(character_data['character_description'])
            if character_data.get('ethnicity'):
                description_parts.append(character_data['ethnicity'])
            if character_data.get('distinctive_features'):
                description_parts.append(character_data['distinctive_features'])
            
            full_description = ", ".join(description_parts)
            self.logger.info(f"🎭 Character description: {full_description[:100]}...")
            
            return full_description
            
        except Exception as e:
            self.logger.error(f"❌ Character extraction failed: {e}")
            # Fallback to pattern matching
            return self._fallback_character_extraction(mission_text)
    
    def _fallback_character_extraction(self, mission_text: str) -> str:
        """Fallback character extraction"""
        import re
        patterns = [
            r"character[:\s]+([^.]+)",
            r"protagonist[:\s]+([^.]+)",
            r"featuring[:\s]+([^.]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, mission_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""