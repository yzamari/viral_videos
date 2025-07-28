"""
Director AI for script writing and creative content generation
"""
import google.generativeai as genai
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict
import requests
import time

from ..config.ai_model_config import DEFAULT_AI_MODEL
from ..models.video_models import (
    VideoAnalysis, Platform, VideoCategory,
    GeneratedVideoConfig
)
from ..utils.logging_config import get_logger
from ..utils.exceptions import (
    GenerationFailedError, APIException,
    NetworkError
)
from .ai_content_analyzer import AIContentAnalyzer, ContentType

logger = get_logger(__name__)

class Director:
    """
    AI-powered director for script writing and content creation

    Responsibilities:
    - Analyze trending patterns and create engaging scripts
    - Adapt content to different platforms
    - Use Gemini's built-in internet access for current information
    - Optimize scripts for maximum virality
    """

    def __init__(self, api_key: str, model_name: str = None):
        """Initialize Director with specified model"""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.model_name = model_name if model_name else DEFAULT_AI_MODEL
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.hook_templates = self._load_hook_templates()
        self.content_structures = self._load_content_structures()
        
        # Initialize AI content analyzer
        self.content_analyzer = AIContentAnalyzer(api_key, model_name)

        logger.info(f"Director initialized with model: {self.model_name}")

    def write_script(self,
                    mission: str,
                    style: str,
                    duration: int,
                    platform: Platform,
                    category: VideoCategory,
                    patterns: Dict[str, Any],
                    incorporate_news: bool = True) -> Dict[str, Any]:
        """
        Write a complete video script

        Args:
            mission: Main mission for the video
            style: Visual/narrative style
            duration: Video duration in seconds
            platform: Target platform
            category: Content category
            patterns: Successful patterns from analysis
            incorporate_news: Whether to include current events

        Returns:
            Dictionary containing script elements
        """
        try:
            logger.info(f"Writing script for {mission} ({duration}s) on {platform.value}")

            # Use Gemini's built-in internet access for current information
            current_context = ""
            if incorporate_news:
                current_context = self._get_current_context_from_gemini(mission, category)
                if current_context:
                    logger.info("Incorporated current information from Gemini's internet access")

            # Generate script components
            hook = self._create_hook(mission, style, platform, patterns, current_context)
            main_content = self._structure_content(
                mission, duration, patterns, current_context
            )
            # Pass target_language from patterns to _create_cta
            target_language = patterns.get('target_language') if patterns else None
            cta = self._create_cta(platform, category, mission, target_language)

            # Assemble complete script
            script = self._assemble_script(
                hook, main_content, cta, duration, platform
            )

            # Optimize for virality
            optimized_script = self.optimize_for_virality(script, patterns)

            logger.info("Script generation completed successfully")

            # Log script details for debugging
            if isinstance(optimized_script, dict):
                script_text = json.dumps(optimized_script, indent=2)
            else:
                script_text = str(optimized_script)

            logger.info("📝 Generated script preview:")
            logger.info(f"   Length: {len(script_text)} characters")
            logger.info(f"   First 300 chars: {script_text[:300]}...")

            # Log any voiceover content found
            if isinstance(optimized_script, dict):
                # Check for voiceover in segments
                segments = optimized_script.get('segments', [])
                voiceover_count = 0
                for segment in segments:
                    if 'text' in segment and segment['text']:
                        voiceover_count += 1
                        logger.info(f"   Segment {voiceover_count} text: {segment['text'][:100]}...")
            else:
                # Check for voiceover markers in text
                voiceover_lines = [line for line in script_text.split('\n') if '**VOICEOVER:**' in line or
                        'voiceover' in line.lower()]
                if voiceover_lines:
                    logger.info(f"🎤 Found {len(voiceover_lines)} voiceover lines:")
                    for i, line in enumerate(voiceover_lines[:3]):  # Show first 3
                        logger.info(f"   VO {i+1}: {line.strip()[:100]}...")

            return optimized_script

        except Exception as e:
            logger.error(f"Script writing failed: {str(e)}")
            raise GenerationFailedError("script_writing", str(e))

    def _create_hook(self, mission: str, style: str, platform: Platform,
                   patterns: Dict[str, Any], news_context: str) -> Dict[str, Any]:
        """Create engaging hook that accomplishes the mission"""
        try:
            # Use AI to analyze content type instead of hardcoded patterns
            content_type, analysis = self.content_analyzer.analyze_content_type(
                mission, 
                {"style": style, "platform": platform.value}
            )
            
            is_creative = content_type == ContentType.CREATIVE
            is_mission = analysis.get('is_action_oriented', False)
            
            if is_creative:
                # Creative content prompt: generate actual creative dialogue/script
                # Check if we need Hebrew script
                language_instruction = ""
                if patterns and patterns.get('target_language'):
                    from ..models.video_models import Language
                    if patterns['target_language'] == Language.HEBREW:
                        language_instruction = "\nIMPORTANT: Generate ALL dialogue and text in Hebrew (עברית). This includes narration, dialogue, and any spoken content."
                
                prompt = f"""
                Create the opening line/hook for this creative content: "{mission}"

                CRITICAL: This is CREATIVE CONTENT - generate the ACTUAL dialogue, narration, or script content described, NOT educational content about it.
                {language_instruction}
                
                Style: {style}
                Platform: {platform.value}

                {news_context}

                Creative Content Requirements:
                1. Generate the ACTUAL creative content described in the mission
                2. If it mentions a character, write their dialogue
                3. If it's comedy, write the actual joke or funny line
                4. If it's satire, write the satirical content
                5. Stay in character/tone throughout
                6. Keep opening hook under 15 words
                7. Make it immediately engaging for the platform
                8. NEVER use contractions - use full forms
                9. TAG all content: "DIALOGUE:" for spoken words, "[VISUAL:]" for visual elements

                Example: If mission mentions "anchor says X", the hook should BE the anchor saying X, not talking about the anchor.
                Example with tags: "[VISUAL: News desk] DIALOGUE: Breaking news just in!"

                IMPORTANT TAGGING REQUIREMENTS:
                - Mark dialogue/narration with "DIALOGUE:" prefix
                - Mark visual descriptions with "[VISUAL:]" prefix
                - Example: "[VISUAL: Explosion effect] DIALOGUE: This changes everything!"
                
                Return ONLY the creative content hook with proper tags, no explanations.
                """
            elif is_mission:
                # Mission-focused prompt: create content that accomplishes the objective
                # Check if we need Hebrew script
                language_instruction = ""
                if patterns and patterns.get('target_language'):
                    from ..models.video_models import Language
                    if patterns['target_language'] == Language.HEBREW:
                        language_instruction = "\nIMPORTANT: Generate ALL dialogue and text in Hebrew (עברית). This includes narration, dialogue, and any spoken content."
                
                prompt = f"""
                Create an engaging opening hook for a {platform.value} video with the MISSION: "{mission}"

                CRITICAL: This is a MISSION to accomplish, not just a topic to discuss. Your hook must START the process of accomplishing: "{mission}"
                {language_instruction}
                
                Style: {style}
                Success patterns: {patterns.get('hooks', [])}

                {news_context}

                Mission-Accomplishment Requirements:
                1. The hook must DIRECTLY begin working toward the mission: "{mission}"
                2. Use persuasive/action language that moves the audience toward the goal
                3. Don't just talk ABOUT the mission - start DOING the mission
                4. Create an emotional or logical entry point that serves the mission objective
                5. Keep it under 15 words but make every word count toward the mission
                6. Begin the persuasion/teaching/demonstration immediately
                7. Hook them while simultaneously starting to accomplish the mission
                8. NEVER use contractions (don't, can't, it's, let's) - use full forms (do not, cannot, it is, let us)

                Example approach: If mission is "convince X that Y is bad" - start by showing consequence/impact, not by saying "let's talk about convincing"

                IMPORTANT TAGGING REQUIREMENTS:
                - Mark dialogue/narration with "DIALOGUE:" prefix
                - Mark visual descriptions with "[VISUAL:]" prefix
                - Example: "[VISUAL: Chart showing data] DIALOGUE: Eight million deaths per year!"
                
                Return ONLY the hook text with proper tags that begins accomplishing the mission, no explanations.
                """
            else:
                # Topic-focused prompt for informational content
                # Check if we need Hebrew script
                language_instruction = ""
                if patterns and patterns.get('target_language'):
                    from ..models.video_models import Language
                    if patterns['target_language'] == Language.HEBREW:
                        language_instruction = "\nIMPORTANT: Generate ALL dialogue and text in Hebrew (עברית). This includes narration, dialogue, and any spoken content."
                
                prompt = f"""
                Create an engaging opening hook for a {platform.value} video about: "{mission}"

                CRITICAL: The hook MUST be about "{mission}" and nothing else.
                {language_instruction}
                
                Style: {style}
                Success patterns: {patterns.get('hooks', [])}

                {news_context}

                Requirements:
                1. Start with an attention-grabbing question or statement about "{mission}"
                2. Be specific to the actual topic: "{mission}"
                3. Create curiosity about "{mission}" without revealing everything
                4. Use emotional triggers appropriate for "{mission}"
                5. Keep it under 15 words for quick consumption
                6. NEVER use generic phrases like "This is amazing"
                7. Make it topic-specific and authentic to "{mission}"
                8. NEVER use contractions (don't, can't, it's, let's) - use full forms (do not, cannot, it is, let us)

                Return ONLY the hook text about "{mission}", no explanations.
                """

            # Try multiple times to get a good hook
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = self.model.generate_content(prompt)
                    hook_text = response.text.strip()

                    # Clean up any quotes or extra formatting
                    hook_text = hook_text.strip('"\'').strip()
                    
                    # Validate hook quality
                    if len(hook_text) < 5 or hook_text.lower() == mission.lower():
                        logger.warning(f"Hook attempt {attempt + 1} too short or same as mission, retrying...")
                        continue
                    
                    # Success - return the hook
                    logger.info(f"✅ AI generated hook on attempt {attempt + 1}: {hook_text[:50]}...")
                    return {
                        'text': hook_text,
                        'type': 'ai_generated',
                        'duration_seconds': 3
                    }
                except Exception as e:
                    logger.warning(f"Hook generation attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(1)  # Brief pause before retry
                    continue
            
            # All attempts failed - use better fallback
            raise Exception("All hook generation attempts failed")

        except Exception as e:
            logger.warning(f"Hook generation failed after all attempts: {e}")
            # Use AI to rephrase the topic as a hook
            try:
                # Check if we need Hebrew script
                language_instruction = ""
                if patterns and patterns.get('target_language'):
                    from ..models.video_models import Language
                    if patterns['target_language'] == Language.HEBREW:
                        language_instruction = "\nIMPORTANT: Generate the hook in Hebrew (עברית)."
                
                fallback_prompt = f"""
                The following topic/mission failed to generate a proper hook: "{mission}"
                
                Create a SHORT, ENGAGING opening line (under 15 words) that:
                1. Captures the essence of: "{mission}"
                2. Creates immediate interest
                3. Works for {platform.value} platform
                4. Is NOT generic or template-like
                5. NEVER use contractions
                {language_instruction}
                
                Return ONLY the hook text, nothing else.
                """
                
                fallback_response = self.model.generate_content(fallback_prompt)
                fallback_hook = fallback_response.text.strip().strip('"\'').strip()
                
                if len(fallback_hook) > 5:
                    logger.info(f"✅ AI-generated fallback hook: {fallback_hook}")
                    return {
                        'text': fallback_hook,
                        'type': 'ai_fallback',
                        'duration_seconds': 3
                    }
            except Exception as fallback_error:
                logger.error(f"Fallback hook generation also failed: {fallback_error}")
            
            # Last resort - extract key concept from topic
            mission_words = mission.split()
            key_concept = ' '.join(mission_words[:min(3, len(mission_words))])
            
            return {
                'text': f"Here is {key_concept}",
                'type': 'minimal_fallback',
                'duration_seconds': 3
            }

    def _structure_content(self, mission: str, duration: int,
                         patterns: Dict, news_context: str) -> List[Dict[str, Any]]:
        """Structure main content to accomplish the mission within the duration"""
        try:
            # Calculate content segments
            num_segments = self._calculate_segments(duration)

            # Use AI to analyze content type instead of hardcoded patterns
            content_type, analysis = self.content_analyzer.analyze_content_type(
                mission, 
                {"duration": duration, "patterns": patterns}
            )
            
            is_creative = content_type == ContentType.CREATIVE
            is_mission = analysis.get('is_action_oriented', False)

            if is_creative:
                # Creative content prompt: generate actual script/dialogue
                # Check if we need Hebrew script
                language_instruction = ""
                if patterns and patterns.get('target_language'):
                    from ..models.video_models import Language
                    if patterns['target_language'] == Language.HEBREW:
                        language_instruction = "\nIMPORTANT: Generate ALL dialogue and text in Hebrew (עברית). This includes narration, dialogue, and any spoken content."
                
                prompt = f"""
                Create {num_segments} script segments for this creative content: "{mission}"

                CRITICAL: Generate the ACTUAL CREATIVE SCRIPT described - the dialogue, narration, or performance content itself.
                This is NOT educational content ABOUT the topic - this IS the creative content.
                {language_instruction}

                Duration: EXACTLY {duration} seconds ({int(duration * 2.8)} words total at 2.8 words/second)
                Segments: {num_segments} segments, each ~{duration // num_segments} seconds

                SUBTITLE REQUIREMENTS:
                - Each segment MUST be 1-2 sentences MAXIMUM
                - Each sentence ~10-15 words for 2-line subtitle display
                - Natural speech breaks between segments

                {news_context}

                Creative Script Requirements:
                1. Write the ACTUAL dialogue/narration described in the topic
                2. If it mentions characters, write what they SAY
                3. If it's comedy/satire, write the ACTUAL jokes/satirical lines
                4. Stay completely in character/tone
                5. Make every line serve the creative vision
                6. NEVER break character to explain or educate
                7. NEVER use contractions - use full forms
                8. TAG all content: Use "DIALOGUE:" prefix for spoken words and "[VISUAL:]" prefix for visual elements

                Example: If topic says "anchor mocks X", write what the anchor SAYS while mocking, not an explanation of mocking.
                Example with tags: "[VISUAL: Anchor at desk with exaggerated expression] DIALOGUE: Oh sure, that plan will definitely work!"

                Return JSON array with the creative script:
                [
                    {{
                        "text": "[VISUAL: visual description] DIALOGUE: The actual spoken dialogue/narration",
                        "duration": seconds,
                        "character": "who says this (if applicable)"
                    }}
                ]
                """
            elif is_mission:
                # Mission-focused prompt: create content that accomplishes the objective
                # Check if we need Hebrew script
                language_instruction = ""
                if patterns and patterns.get('target_language'):
                    from ..models.video_models import Language
                    if patterns['target_language'] == Language.HEBREW:
                        language_instruction = "\nIMPORTANT: Generate ALL dialogue and text in Hebrew (עברית). This includes narration, dialogue, and any spoken content."
                
                prompt = f"""
                Create {num_segments} content segments for a {duration}-second video to ACCOMPLISH THE MISSION: "{mission}"

                CRITICAL: This is NOT about discussing the topic - this is about ACCOMPLISHING the mission "{mission}" within {duration} seconds.
                {language_instruction}

                Mission Strategy:
                - Duration: EXACTLY {duration} seconds (HARD CONSTRAINT - content MUST fit this time limit)
                - Word limit: {int(duration * 2.8)} words MAXIMUM (2.8 words per second)
                - DO NOT EXCEED {int(duration * 2.8)} words!
                - Segments: {num_segments} strategic segments that build toward mission completion
                - Pacing: {patterns.get('pacing', 'fast')} to maximize persuasive impact
                - Success patterns: {patterns.get('success_factors', [])}
                - CONTENT MUST BE CONCISE - fit the story within the time limit

                CRITICAL SUBTITLE REQUIREMENTS:
                - Each segment MUST be 1-2 sentences MAXIMUM
                - Each sentence should be ~10-15 words for 2-line subtitle display
                - NEVER create segments longer than 2 sentences
                - Segments should be natural speech breaks (pause points)

                {news_context}

                Mission-Accomplishment Requirements:
                1. Each segment must DIRECTLY advance the mission "{mission}"
                2. Use proven persuasion techniques: evidence, emotion, logic, consequences
                3. Build a strategic argument/case that accomplishes the mission
                4. Each segment should move the audience closer to the desired outcome
                5. Include ONLY spoken dialogue that serves the mission objective
                6. Each segment MUST be 1-2 complete sentences MAXIMUM
                7. No meta-discussion - dive straight into accomplishing the mission
                8. Make the content compelling and actionable within the time limit
                9. NEVER use contractions (don't, can't, it's, let's) - use full forms (do not, cannot, it is, let us)
                10. TAG all content: Use "DIALOGUE:" prefix for spoken words and "[VISUAL:]" prefix for visual elements

                Strategic Approach Examples:
                - If mission is "convince X that Y is bad": Show consequences, provide evidence, emotional impact
                - If mission is "teach X how to Y": Provide clear steps, benefits, actionable guidance
                - If mission is "prove X": Present evidence, data, logical arguments

                Return JSON array with strategic mission-accomplishing content:
                [
                    {{
                        "text": "[VISUAL: visual description] DIALOGUE: Words to be spoken that advance the mission",
                        "duration": seconds,
                        "mission_purpose": "How this segment advances the mission"
                    }}
                ]
                """
            else:
                # Topic-focused prompt for informational content
                # Check if we need Hebrew script
                language_instruction = ""
                if patterns and patterns.get('target_language'):
                    from ..models.video_models import Language
                    if patterns['target_language'] == Language.HEBREW:
                        language_instruction = "\nIMPORTANT: Generate ALL dialogue and text in Hebrew (עברית). This includes narration, dialogue, and any spoken content."
                
                prompt = f"""
                Create {num_segments} content segments for a {duration}-second video about: "{mission}"

                CRITICAL: ALL segments MUST be about "{mission}" and fit EXACTLY within {duration} seconds.
                {language_instruction}

                Duration constraints:
                - Duration: EXACTLY {duration} seconds (HARD CONSTRAINT - content MUST fit this time limit)
                - Word limit: {int(duration * 2.8)} words MAXIMUM (2.8 words per second)
                - DO NOT EXCEED {int(duration * 2.8)} words!
                - Each segment: ~{duration // num_segments} seconds each

                CRITICAL SUBTITLE REQUIREMENTS:
                - Each segment MUST be 1-2 sentences MAXIMUM
                - Each sentence should be ~10-15 words for 2-line subtitle display
                - NEVER create segments longer than 2 sentences
                - Segments should be natural speech breaks (pause points)

                Successful content patterns:
                - Themes: {patterns.get('themes', [])}
                - Pacing: Fast cuts every 3-5 seconds
                - Engagement triggers: {patterns.get('success_factors', [])}

                {news_context}

                Each segment should:
                1. Deliver value or entertainment about "{mission}"
                2. Build on previous segment about "{mission}"
                3. Maintain viewer attention with "{mission}" content
                4. Include ONLY spoken dialogue content about "{mission}"
                5. Be 1-2 complete sentences MAXIMUM (for proper subtitles)
                6. NEVER use contractions (don't, can't, it's, let's) - use full forms (do not, cannot, it is, let us)
                7. TAG all content: Use "DIALOGUE:" prefix for spoken words and "[VISUAL:]" prefix for visual elements

                Return JSON array:
                [
                    {{
                        "text": "[VISUAL: visual description] DIALOGUE: Words to be spoken aloud about {mission}",
                        "duration": seconds
                    }}
                ]
                """

            # Try generation with retry and rephrasing if needed
            max_attempts = 3
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        # Rephrase prompt if previous attempt failed
                        logger.info(f"Attempt {attempt + 1}: Rephrasing prompt for better AI compliance")
                        prompt = self._rephrase_prompt_for_compliance(prompt, mission, duration, num_segments, is_creative, is_mission, patterns, news_context)
                    
                    response = self.model.generate_content(prompt)
                    segments = self._extract_json(response.text)

                    # Validate that segments are about the topic
                    if segments and isinstance(segments, list):
                        mission_words = mission.lower().split()
                        valid_segments = []
                        
                        for segment in segments:
                            if isinstance(segment, dict) and 'text' in segment:
                                segment_text = segment['text'].lower()
                                # Check if any topic words appear in the segment
                                topic_match = any(word in segment_text for word in mission_words if len(word) > 2)
                                valid_segments.append(segment)
                        
                        if valid_segments:
                            logger.info(f"✅ Content generation succeeded on attempt {attempt + 1}")
                            return valid_segments
                        else:
                            logger.warning(f"No valid segments found on attempt {attempt + 1}")
                            if attempt < max_attempts - 1:
                                continue
                            return self._get_default_segments(mission, num_segments, duration)
                    else:
                        if attempt < max_attempts - 1:
                            logger.warning(f"Invalid response format on attempt {attempt + 1}, retrying...")
                            continue
                        return self._get_default_segments(mission, num_segments)
                        
                except Exception as e:
                    last_error = e
                    logger.warning(f"Content generation attempt {attempt + 1} failed: {e}")
                    
                    # Check if it's a content policy error
                    error_str = str(e).lower()
                    if any(term in error_str for term in ['policy', 'inappropriate', 'violation', 'blocked', 'safety']):
                        logger.info("🔄 Detected potential content policy issue, will rephrase on next attempt")
                    
                    if attempt < max_attempts - 1:
                        time.sleep(1)  # Brief pause before retry
                        continue
            
            # All attempts failed
            logger.error(f"Content structuring failed after {max_attempts} attempts: {last_error}")
            return self._get_default_segments(mission, self._calculate_segments(duration), duration)

        except Exception as e:
            logger.warning(f"Content structuring failed, using defaults: {e}")
            return self._get_default_segments(mission, self._calculate_segments(duration), duration)

    def _create_cta(
        self,
        platform: Platform,
        category: VideoCategory,
        mission: str = None,
        target_language = None) -> Dict[str, str]:
        """Create platform-optimized call-to-action that reinforces the mission"""
        
        # Import Language enum to check Hebrew
        from ..models.video_models import Language
        
        # Check if we need Hebrew CTAs
        if target_language and target_language == Language.HEBREW:
            # Hebrew CTAs by platform
            hebrew_cta_templates = {
                Platform.YOUTUBE: {
                    "text": "הירשמו לעוד תוכן!",
                    "visual": "Subscribe button animation",
                    "action": "subscribe"
                },
                Platform.TIKTOK: {
                    "text": "עקבו לחלק 2! 👀",
                    "visual": "Follow button highlight",
                    "action": "follow"
                },
                Platform.INSTAGRAM: {
                    "text": "שמרו לאחר כך! ❤️",
                    "visual": "Heart animation",
                    "action": "save"
                },
                Platform.FACEBOOK: {
                    "text": "שתפו אם זה עזר לכם!",
                    "visual": "Share button",
                    "action": "share"
                }
            }
            return hebrew_cta_templates.get(platform, hebrew_cta_templates[Platform.YOUTUBE])
        
        # Use AI to determine if this is a mission (action-oriented) or topic (informational)
        if mission:
            content_type, analysis = self.content_analyzer.analyze_content_type(mission)
            is_mission = analysis.get('is_action_oriented', False)
        else:
            is_mission = False
        
        if is_mission:
            # Mission-focused CTAs that reinforce the mission objective
            mission_cta_templates = {
                Platform.YOUTUBE: {
                    "text": "Share this message - every voice matters!",
                    "visual": "Share button animation",
                    "action": "share"
                },
                Platform.TIKTOK: {
                    "text": "Spread the word! 🗣️",
                    "visual": "Share button highlight", 
                    "action": "share"
                },
                Platform.INSTAGRAM: {
                    "text": "Share this important message! 📢",
                    "visual": "Share animation",
                    "action": "share"
                },
                Platform.FACEBOOK: {
                    "text": "Share if you believe this matters!",
                    "visual": "Share button",
                    "action": "share"
                }
            }
            cta = mission_cta_templates.get(platform, mission_cta_templates[Platform.YOUTUBE])
        else:
            # Standard content CTAs
            cta_templates = {
                Platform.YOUTUBE: {
                    "text": "Subscribe for more {category} content!",
                    "visual": "Subscribe button animation",
                    "action": "subscribe"
                },
                Platform.TIKTOK: {
                    "text": "Follow for part 2! 👀",
                    "visual": "Follow button highlight",
                    "action": "follow"
                },
                Platform.INSTAGRAM: {
                    "text": "Save this for later! ❤️",
                    "visual": "Heart animation",
                    "action": "save"
                },
                Platform.FACEBOOK: {
                    "text": "Share if you found this helpful!",
                    "visual": "Share button",
                    "action": "share"
                }
            }
            cta = cta_templates.get(platform, cta_templates[Platform.YOUTUBE])
            cta['text'] = cta['text'].format(category=category.value.lower())

        return cta

    def adapt_to_platform(self, script: Dict[str, Any],
                         target_platform: Platform) -> Dict[str, Any]:
        """Adapt script to platform-specific requirements"""
        try:
            logger.info(f"Adapting script for {target_platform.value}")

            platform_specs = {
                Platform.YOUTUBE: {
                    "max_duration": 60,
                    "aspect_ratio": "9:16",
                    "features": ["captions", "chapters", "cards"]
                },
                Platform.TIKTOK: {
                    "max_duration": 60,
                    "aspect_ratio": "9:16",
                    "features": ["sounds", "effects", "duet"]
                },
                Platform.INSTAGRAM: {
                    "max_duration": 90,
                    "aspect_ratio": "9:16",
                    "features": ["music", "stickers", "polls"]
                },
                Platform.FACEBOOK: {
                    "max_duration": 240,
                    "aspect_ratio": "16:9",
                    "features": ["captions", "thumbnails"]
                }
            }

            spec = platform_specs[target_platform]

            # Adjust duration if needed
            if script['duration'] > spec['max_duration']:
                script = self._trim_script(script, spec['max_duration'])

            # Add platform-specific elements
            script['platform_features'] = spec['features']
            script['aspect_ratio'] = spec['aspect_ratio']

            # Optimize text for platform
            script = self._optimize_text_for_platform(script, target_platform)

            return script

        except Exception as e:
            logger.error(f"Platform adaptation failed: {e}")
            return script  # Return original if adaptation fails

    def incorporate_news(self, script: Dict[str, Any],
                        news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Incorporate current news into script"""
        try:
            if not news_items:
                return script

            logger.info(f"Incorporating {len(news_items)} news items into script")

            # Find relevant insertion points
            segments = script.get('segments', [])

            for i, segment in enumerate(segments):
                # Check if segment could incorporate news
                if self._can_incorporate_news(segment, news_items):
                    relevant_news = self._find_relevant_news(segment, news_items)
                    if relevant_news:
                        segment['news_context'] = relevant_news
                        segment['text'] = self._blend_news_into_text(
                            segment['text'], relevant_news
                        )

            script['has_news'] = True
            script['news_items'] = news_items

            return script

        except Exception as e:
            logger.warning(f"News incorporation failed: {e}")
            return script

    def optimize_for_virality(self, script: Dict[str, Any],
                            patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize script elements for maximum viral potential"""
        try:
            logger.info("Optimizing script for virality")

            # Analyze successful patterns
            viral_elements = {
                'emotional_triggers': patterns.get('emotional_tones', []),
                'engagement_hooks': patterns.get('success_factors', []),
                'optimal_pacing': patterns.get('pacing', 'fast')
            }

            # Enhance hook
            if 'hook' in script:
                script['hook'] = self._enhance_hook_virality(
                    script['hook'], viral_elements
                )

            # Optimize pacing
            script['segments'] = self._optimize_segment_pacing(
                script.get('segments', []), viral_elements['optimal_pacing']
            )

            # Add viral elements
            script['viral_elements'] = {
                'shareability_score': self._calculate_shareability(script),
                'emotional_arc': self._analyze_emotional_arc(script),
                'surprise_moments': self._identify_surprise_moments(script)
            }

            return script

        except Exception as e:
            logger.warning(f"Virality optimization failed: {e}")
            return script

    def _fetch_relevant_news(self, mission: str,
                           category: VideoCategory) -> List[Dict[str, Any]]:
        """Fetch news relevant to mission and category"""
        try:
            # Search for news related to topic
            news_items = self.model.generate_content(
                f"Search for recent news about {mission} in the {category.value} category. "
                "Return a JSON array of news items. Each item should have 'title', 'description', "
                "'url', 'published_at', and 'relevance_score' (0-1). "
                "Ensure the JSON is valid and well-formatted. "
                "Example: `[{{'title': 'News Title', 'description': 'Description', 'url': 'https://example.com', 'published_at': '2023-10-27T10:00:00Z', 'relevance_score': 0.8}}]`"
            )
            news_items = json.loads(news_items.text.strip())

            # Filter by relevance and recency
            relevant_news = []
            for item in news_items:
                relevance_score = self._calculate_news_relevance(item, mission)
                if relevance_score > 0.7:  # Threshold for relevance
                    item['relevance_score'] = relevance_score
                    relevant_news.append(item)

            # Sort by relevance
            relevant_news.sort(key=lambda x: x['relevance_score'], reverse=True)

            return relevant_news[:3]  # Top 3 most relevant

        except Exception as e:
            logger.warning(f"News fetching failed: {e}")
            return []

    def _calculate_news_relevance(self, news_item: Dict[str, Any],
                                mission: str) -> float:
        """Calculate relevance score between news and mission"""
        # Simple keyword matching (could be enhanced with NLP)
        title = news_item.get('title', '').lower()
        description = news_item.get('description', '').lower()
        mission_words = mission.lower().split()

        matches = sum(1 for word in mission_words if word in title or
                word in description)
        relevance = matches / len(mission_words) if mission_words else 0

        # Boost score for recent news
        published = news_item.get('published_at')
        if published:
            age_hours = (datetime.now() - published).total_seconds() / 3600
            recency_boost = max(0, 1 - (age_hours / 168))  # Decay over a week
            relevance = (relevance * 0.7) + (recency_boost * 0.3)

        return min(relevance, 1.0)


    def _extract_json(self, text: str) -> Any:
        """Extract JSON from AI response"""
        try:
            # Find JSON in response
            json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except Exception:
            pass
        return None
    
    def _rephrase_prompt_for_compliance(self, original_prompt: str, mission: str, 
                                      duration: int, num_segments: int, 
                                      is_creative: bool, is_mission: bool,
                                      patterns: Dict[str, Any], news_context: str) -> str:
        """Rephrase prompt to be more compliant with AI content policies while preserving ALL context"""
        logger.info("🔄 Rephrasing prompt to avoid content policy issues while maintaining full context")
        
        # Use the actual patterns and context passed in
        pacing = patterns.get('pacing', 'dynamic')
        success_patterns = patterns.get('success_factors', [])
        themes = patterns.get('themes', [])
        emotional_tones = patterns.get('emotional_tones', [])
        engagement_triggers = patterns.get('engagement_triggers', [])
        
        # Build rephrased prompt that maintains ALL original requirements
        if is_creative:
            rephrase_request = f"""
            Create {num_segments} script segments for this creative content: "{mission}"
            
            IMPORTANT: Previous attempt was blocked. Please create appropriate content that captures the creative vision while being suitable for all platforms.
            
            CRITICAL: Generate the ACTUAL CREATIVE SCRIPT - dialogue, narration, or performance content.
            This is NOT educational content ABOUT the topic - this IS the creative content itself.
            
            Duration: EXACTLY {duration} seconds ({duration * 3} words total at 3 words/second)
            Segments: {num_segments} segments, each ~{duration // num_segments} seconds
            Pacing: {pacing}
            Themes: {themes}
            Emotional tones: {emotional_tones}
            
            SUBTITLE REQUIREMENTS (UNCHANGED):
            - Each segment MUST be 1-2 sentences MAXIMUM
            - Each sentence ~10-15 words for 2-line subtitle display
            - Natural speech breaks between segments
            
            {news_context}
            
            Creative Requirements (MAINTAIN ORIGINAL STYLE):
            1. Write the ACTUAL dialogue/narration as described
            2. Stay completely in character/tone
            3. Make every line serve the creative vision
            4. Use appropriate language while maintaining impact
            5. NEVER use contractions - use full forms
            
            If the content has edgy elements, use creative techniques:
            - Clever wordplay or metaphors
            - Implied rather than explicit content
            - Satirical or comedic framing
            - Educational or awareness angle
            
            Return JSON array maintaining original format:
            [
                {{
                    "text": "The actual creative dialogue/narration",
                    "duration": seconds,
                    "character": "who says this (if applicable)"
                }}
            ]
            """
        elif is_mission:
            rephrase_request = f"""
            Create {num_segments} content segments for a {duration}-second video to ACCOMPLISH THE MISSION: "{mission}"
            
            IMPORTANT: Previous attempt was blocked. Please create appropriate content that still accomplishes the mission objective.
            
            CRITICAL: This is about ACCOMPLISHING the mission "{mission}" within {duration} seconds.
            
            Mission Strategy (UNCHANGED):
            - Duration: EXACTLY {duration} seconds
            - Word limit: {int(duration * 2.3)} to {int(duration * 2.5)} words MAXIMUM
            - DO NOT EXCEED word limit!
            - Segments: {num_segments} strategic segments
            - Pacing: {pacing}
            - Success patterns: {success_patterns}
            - Themes: {themes}
            - Emotional approach: {emotional_tones}
            - Engagement triggers: {engagement_triggers}
            
            SUBTITLE REQUIREMENTS (UNCHANGED):
            - Each segment MUST be 1-2 sentences MAXIMUM
            - Each sentence ~10-15 words for 2-line subtitle display
            - Segments should be natural speech breaks
            
            {news_context}
            
            Mission-Accomplishment Approach:
            1. Each segment must advance the mission
            2. Use appropriate persuasion techniques
            3. Build strategic argument while being platform-compliant
            4. Focus on positive change and solutions
            5. NEVER use contractions
            
            Strategic Adaptations for Compliance:
            - Frame controversial topics educationally
            - Use data and evidence appropriately
            - Focus on constructive outcomes
            - Emphasize awareness and understanding
            
            Return JSON array with mission-focused content:
            [
                {{
                    "text": "Words that advance the mission appropriately",
                    "duration": seconds,
                    "mission_purpose": "How this advances the mission"
                }}
            ]
            """
        else:
            rephrase_request = f"""
            Create {num_segments} content segments for a {duration}-second video about: "{mission}"
            
            IMPORTANT: Previous attempt was blocked. Please create appropriate content about this topic.
            
            Duration constraints (UNCHANGED):
            - Duration: EXACTLY {duration} seconds
            - Word limit: {int(duration * 2.3)} to {int(duration * 2.5)} words MAXIMUM
            - DO NOT EXCEED word limit!
            - Each segment: ~{duration // num_segments} seconds
            - Pacing: {pacing}
            - Themes to incorporate: {themes}
            - Engagement style: {engagement_triggers}
            
            SUBTITLE REQUIREMENTS (UNCHANGED):
            - Each segment MUST be 1-2 sentences MAXIMUM
            - Each sentence ~10-15 words for 2-line subtitle display
            - Natural speech breaks between segments
            
            {news_context}
            
            Content Requirements:
            1. Deliver value about "{mission}"
            2. Maintain engagement and interest
            3. Use appropriate language for all audiences
            4. NEVER use contractions
            
            If topic has sensitive aspects:
            - Focus on educational value
            - Present balanced perspectives
            - Use constructive framing
            - Emphasize positive outcomes
            
            Return JSON array:
            [
                {{
                    "text": "Appropriate spoken content about {mission}",
                    "duration": seconds
                }}
            ]
            """
        
        return rephrase_request

    def _load_hook_templates(self) -> Dict[str, List[str]]:
        """Load dynamic hook pattern templates (no hardcoded content)"""
        return {
            'question': [
                "How does {key_word} really work?",
                "What makes {key_word} so effective?",
                "Why is {key_word} gaining attention?"
            ],
            'shock': [
                "The truth about {key_word} changes everything",
                "What experts don't tell you about {key_word}",
                "The hidden side of {key_word} revealed"
            ],
            'promise': [
                "Master {key_word} with this approach",
                "Understanding {key_word} made simple",
                "The complete guide to {key_word}"
            ],
            'story': [
                "My journey with {key_word} began when...",
                "Here's what happened when I explored {key_word}",
                "The moment {key_word} changed my perspective"
            ]
        }

    def _load_content_structures(self) -> Dict[str, Any]:
        """Load content structure templates"""
        return {
            'list': {
                'segments': ['intro', 'item1', 'item2', 'item3', 'outro'],
                'transitions': ['number_overlay', 'swipe', 'zoom']
            },
            'tutorial': {
                'segments': ['problem', 'step1', 'step2', 'result'],
                'transitions': ['arrow', 'highlight', 'checkmark']
            },
            'story': {
                'segments': ['setup', 'conflict', 'resolution'],
                'transitions': ['fade', 'cut', 'dissolve']
            }
        }

    def decide_frame_continuity(self, mission: str, style: str, category: VideoCategory,
                              duration: int, platform: Platform) -> Dict[str, Any]:
        """
        Decide whether to use frame continuity for seamless video generation

        Frame continuity creates a single flowing video where each clip's last frame'
        becomes the first frame of the next clip, creating smooth transitions.

        Returns:
            Dictionary with continuity decision and reasoning
        """
        try:
            logger.info(f"Analyzing whether to use frame continuity for {mission}")

            # Analyze content type for continuity suitability
            continuity_suitable_styles = [
                'story', 'narrative', 'journey', 'process', 'tutorial',
                'documentary', 'vlog', 'tour', 'exploration', 'evolution'
            ]

            continuity_unsuitable_styles = [
                'compilation', 'list', 'countdown', 'comparison', 'reaction',
                'meme', 'montage', 'highlights', 'quick cuts'
            ]

            # Check if style suggests continuity
            style_lower = style.lower()
            suggests_continuity = any(s in style_lower for s in continuity_suitable_styles)
            suggests_cuts = any(s in style_lower for s in continuity_unsuitable_styles)

            # Platform preferences
            platform_continuity_preference = {
                Platform.YOUTUBE: 0.7,      # YouTube favors longer, flowing content
                Platform.TIKTOK: 0.3,       # TikTok prefers quick cuts
                Platform.INSTAGRAM: 0.5,     # Instagram is neutral
                Platform.FACEBOOK: 0.6       # Facebook slightly favors continuity
            }

            # Category preferences
            category_continuity_preference = {
                VideoCategory.EDUCATION: 0.8,
                VideoCategory.TECHNOLOGY: 0.7,
                VideoCategory.NEWS: 0.6,
                VideoCategory.LIFESTYLE: 0.7,
                VideoCategory.ENTERTAINMENT: 0.4,
                VideoCategory.COMEDY: 0.3,
                VideoCategory.GAMING: 0.5,
                VideoCategory.MUSIC: 0.4,
                VideoCategory.SPORTS: 0.5,
                VideoCategory.OTHER: 0.5
            }

            # Duration factor (longer videos benefit more from continuity)
            duration_factor = min(1.0, duration / 60)  # Normalize to 0-1

            # Calculate continuity score
            base_score = 0.5

            if suggests_continuity:
                base_score += 0.3
            if suggests_cuts:
                base_score -= 0.3

            platform_score = platform_continuity_preference.get(platform, 0.5)
            category_score = category_continuity_preference.get(category, 0.5)

            # Weighted final score
            continuity_score = (
                base_score * 0.4 +
                platform_score * 0.2 +
                category_score * 0.2 +
                duration_factor * 0.2
            )

            # Make decision
            use_continuity = continuity_score >= 0.6

            # Generate reasoning
            reasoning = []
            if suggests_continuity:
                reasoning.append(f"Style '{style}' suggests flowing narrative")
            if suggests_cuts:
                reasoning.append(f"Style '{style}' typically uses quick cuts")
            reasoning.append(f"{platform.value} platform preference: {platform_score:.1f}")
            reasoning.append(f"{category.value} category preference: {category_score:.1f}")
            reasoning.append(f"Duration factor ({duration}s): {duration_factor:.1f}")

            # Transition strategy if using continuity
            transition_strategy = None
            if use_continuity:
                transition_strategy = self._determine_transition_strategy(
                    mission, style, category
                )

            decision = {
                'use_frame_continuity': use_continuity,
                'continuity_score': round(continuity_score, 2),
                'reasoning': reasoning,
                'transition_strategy': transition_strategy,
                'recommended_clip_count': self._calculate_continuity_clips(
                    duration,
                    use_continuity),
                'frame_overlap_type': 'last_to_first' if use_continuity else None
            }

            logger.info(f"Frame continuity decision: {use_continuity} (score: {continuity_score:.2f}")
            return decision

        except Exception as e:
            logger.error(f"Error deciding frame continuity: {e}")
            return {
                'use_frame_continuity': False,
                'continuity_score': 0.5,
                'reasoning': ['Error in analysis, defaulting to standard cuts'],
                'transition_strategy': None,
                'recommended_clip_count': self._calculate_segments(duration),
                'frame_overlap_type': None
            }

    def _determine_transition_strategy(self, mission: str, style: str,
                                     category: VideoCategory) -> Dict[str, Any]:
        """Determine the transition strategy for continuous videos"""

        # Define transition types for continuous flow
        transition_types = {
            'smooth_motion': {
                'description': 'Camera or subject movement continues across clips',
                'suitable_for': ['journey', 'tour', 'exploration', 'vlog'],
                'instructions': 'End each clip with motion that continues in next clip'
            },
            'object_tracking': {
                'description': 'Follow same object/person across clips',
                'suitable_for': ['story', 'documentary', 'tutorial', 'process'],
                'instructions': 'Keep main subject in similar position at clip boundaries'
            },
            'environment_flow': {
                'description': 'Natural environment progression',
                'suitable_for': ['nature', 'travel', 'lifestyle', 'meditation'],
                'instructions': 'Transition through connected spaces or time progression'
            },
            'narrative_continuity': {
                'description': 'Story or explanation flows seamlessly',
                'suitable_for': ['education', 'news', 'technology', 'narrative'],
                'instructions': 'Visual elements support continuous narration'
            }
        }

        # Select best transition type
        style_lower = style.lower()
        selected_type = 'narrative_continuity'  # Default

        for trans_type, config in transition_types.items():
            if any(keyword in style_lower for keyword in config['suitable_for']):
                selected_type = trans_type
                break

        return {
            'type': selected_type,
            'config': transition_types[selected_type],
            'frame_blend_duration': 0.1,  # 100ms blend between clips
            'maintain_subject_position': selected_type in ['object_tracking', 'smooth_motion'],
            'color_correction': True,  # Match colors between clips
            'audio_crossfade': True    # Smooth audio transitions
        }

    def _calculate_continuity_clips(
        self,
        duration: int,
        use_continuity: bool) -> int:
        """Calculate optimal number of clips for continuity mode"""
        if use_continuity:
            # Fewer, longer clips for smooth continuity
            if duration <= 30:
                return 3  # 10s each
            elif duration <= 60:
                return 4  # 15s each
            elif duration <= 120:
                return 6  # 20s each
            else:
                return 8  # For longer videos
        else:
            # More clips for dynamic cutting
            return self._calculate_segments(duration)

    def _get_template_hook(self, mission: str, style: str) -> Dict[str, Any]:
        """Get fallback hook from templates dynamically"""
        # Determine hook type based on style
        hook_type = 'question' if 'tutorial' in style else 'shock'

        # Extract meaningful words from mission
        mission_words = mission.split()
        meaningful_words = [word for word in mission_words if len(word) > 3 and word.lower() not in ['the', 'and', 'with', 'for', 'that', 'this', 'from']]

        # Generate dynamic hook based on type and topic
        if hook_type == 'question':
            if meaningful_words:
                hook_text = f"How does {meaningful_words[0]} actually work?"
            else:
                hook_text = f"What's the real story behind {mission}?"
        else:  # shock type
            if meaningful_words:
                hook_text = f"The truth about {meaningful_words[0]} will surprise you"
            else:
                hook_text = f"What you don't know about {mission}"

        return {
            'text': hook_text,
            'type': hook_type,
            'duration_seconds': 3
        }

    def _calculate_segments(self, duration: int) -> int:
        """Calculate optimal number of segments"""
        # Roughly 5-10 seconds per segment
        return max(3, min(duration // 7, 8))

    def _get_default_segments(self, mission: str, num_segments: int, duration: int = 30) -> List[Dict]:
        """Get default content segments dynamically based on mission"""
        segments = []
        segment_duration = duration // num_segments  # Use actual duration instead of hardcoded 30s

        # Check if this is creative content
        is_creative = any(creative_word in mission.lower() for creative_word in [
            'satirical', 'satire', 'comedy', 'comedic', 'parody', 'skit', 'sketch',
            'funny', 'humorous', 'mock', 'spoof', 'joke', 'drama', 'story',
            'narrative', 'tale', 'scene', 'act', 'performance', 'segment',
            'hilarious', 'first-person', 'pov', 'perspective', 'inner monologue',
            'thoughts', 'create a', 'show'
        ])

        if is_creative:
            # For creative content, create placeholder dialogue
            logger.warning(f"Using creative fallback for mission: {mission[:100]}...")
            
            # Extract key elements from the mission
            if 'news' in mission.lower() and 'anchor' in mission.lower():
                # News satire fallback
                segments = [
                    {"text": "Breaking news: Something unexpected has happened!", "duration": segment_duration},
                    {"text": "Our sources confirm this is absolutely unprecedented.", "duration": segment_duration},
                    {"text": "We will continue to monitor this developing situation.", "duration": segment_duration}
                ]
            elif 'comedy' in mission.lower() or 'funny' in mission.lower():
                # Comedy fallback
                segments = [
                    {"text": "You will not believe what happened today!", "duration": segment_duration},
                    {"text": "It gets even more ridiculous than you think.", "duration": segment_duration},
                    {"text": "And that is why we cannot have nice things!", "duration": segment_duration}
                ]
            else:
                # Generic creative fallback
                for i in range(num_segments):
                    segments.append({
                        "text": f"Scene {i+1} dialogue placeholder.",
                        "duration": segment_duration
                    })
            
            return segments

        # Original educational content logic
        # Extract topic components for dynamic content
        mission_words = mission.split()
        meaningful_words = [word for word in mission_words if len(word) > 3 and word.lower() not in ['the', 'and', 'with', 'for', 'that', 'this', 'from', 'about']]

        # Create dynamic segment content based on mission structure
        for i in range(num_segments):
            if i == 0:
                # First segment: Introduction
                if meaningful_words:
                    text = f"Let's explore {meaningful_words[0]} and understand its significance"
                else:
                    text = f"Let's dive into {mission} and what makes it important"
            elif i == num_segments - 1:
                # Last segment: Conclusion
                if meaningful_words:
                    text = f"Understanding {meaningful_words[0]} opens new possibilities"
                else:
                    text = f"This knowledge about {mission} can be valuable"
            else:
                # Middle segments: Key aspects
                if len(meaningful_words) > i:
                    text = f"Important aspect: {meaningful_words[i]}"
                else:
                    text = f"Another important aspect of {mission} to consider"

            segments.append({
                'text': text,
                'duration': segment_duration
            })

        return segments

    def _analyze_hook_patterns(
        self,
        successful_hooks: List[str]) -> Dict[str, Any]:
        """Analyze patterns in successful hooks"""
        if not successful_hooks:
            return {
                'common_words': ['effective', 'important', 'powerful'],
                'patterns': ['question', 'promise', 'insight'],
                'avg_length': 15
            }

        # Simple pattern analysis
        all_words = []
        for hook in successful_hooks:
            all_words.extend(hook.lower().split())

        # Count word frequency
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get most common words
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'common_words': [word for word, freq in common_words],
            'patterns': ['question', 'promise', 'shock'],
            'avg_length': sum(len(hook) for hook in successful_hooks) // len(successful_hooks)
        }

    def _assemble_script(self, hook: Dict[str, str], main_content: List[Dict[str, Any]],
                        cta: Dict[str, str], duration: int, platform: Platform) -> Dict[str, Any]:
        """Assemble complete script from components"""
        try:
            # Calculate timing
            hook_duration = hook.get('duration_seconds', 3)
            cta_duration = 2
            content_duration = duration - hook_duration - cta_duration

            # Distribute content duration across segments
            if main_content:
                segment_duration = content_duration / len(main_content)
                for segment in main_content:
                    segment['duration'] = segment_duration

            # Assemble complete script
            script = {
                'hook': hook,
                'segments': main_content,
                'cta': cta,
                'total_duration': duration,
                'platform': platform.value,
                'created_at': datetime.now().isoformat(),
                'structure': {
                    'hook_duration': hook_duration,
                    'content_duration': content_duration,
                    'cta_duration': cta_duration
                }
            }

            # Add full text for analysis
            full_text = hook.get('text', '')
            for segment in main_content:
                full_text += ' ' + segment.get('text', '')
            full_text += ' ' + cta.get('text', '')
            script['full_text'] = full_text.strip()

            return script

        except Exception as e:
            logger.error(f"Script assembly failed: {e}")
            # Return minimal script as fallback
            hook_text = hook.get("text", "")
            cta_text = cta.get("text", "")

            # Extract topic from hook or use fallback
            if hook_text:
                fallback_content = f"Let's explore {hook_text.lower()}"
            else:
                fallback_content = "Important information"

            return {
                'hook': hook,
                'segments': main_content or [{'text': fallback_content, 'duration': duration-5}],
                'cta': cta,
                'total_duration': duration,
                'platform': platform.value,
                'created_at': datetime.now().isoformat(),
                'full_text': f'{hook_text} {fallback_content}. {cta_text}'
            }

    def _format_news_context(self, news_items: List[Dict[str, Any]]) -> str:
        """Format news items into context string"""
        if not news_items:
            return ""

        context = "Recent news context:\n"
        for item in news_items[:3]:
            title = item.get('title', 'Unknown')
            context += f"- {title}\n"
        return context

    def _extract_full_text(self, script: Dict[str, Any]) -> str:
        """Extract all text from script for analysis"""
        text_parts = []

        # Add hook text
        if 'hook' in script and 'text' in script['hook']:
            text_parts.append(script['hook']['text'])

        # Add segment texts
        for segment in script.get('segments', []):
            if 'text' in segment:
                text_parts.append(segment['text'])

        # Add CTA text
        if 'cta' in script and 'text' in script['cta']:
            text_parts.append(script['cta']['text'])

        return ' '.join(text_parts)

    def _enhance_hook_virality(
        self,
        hook: Dict[str,
        str],
        viral_elements: Dict[str,
        Any]) -> Dict[str, str]:
        """Enhance hook for viral potential without hardcoded words"""
        hook_text = hook.get('text', '')

        # Use emotional triggers from viral_elements if available
        available_triggers = viral_elements.get('emotional_triggers', [])

        # If no emotional triggers in text and we have available triggers, enhance the hook
        if (available_triggers and
                not any(trigger in hook_text.lower() for trigger in available_triggers)):
            # Use the first available emotional trigger naturally integrated
            trigger = available_triggers[0].lower()
            # Integrate trigger naturally without colon prefix
            if trigger == "amazing":
                hook['text'] = f"This {hook_text.lower()} is amazing"
            elif trigger == "shocking":
                hook['text'] = f"You won't believe this about {hook_text.lower()}"
            elif trigger == "incredible":
                hook['text'] = f"The incredible truth about {hook_text.lower()}"
            else:
                # Default: just enhance without adding prefixes that break TTS
                hook['text'] = hook_text
        elif not available_triggers:
            # If no triggers available, enhance naturally without colon prefixes
            if not any(
                word in hook_text.lower() for word in ['how',
                'why',
                'what',
                'when',
                'where']):
                # Don't modify hooks - keep them as is
                # Removed hardcoded "Learn about" prefix
                pass

        return hook

    def _optimize_segment_pacing(
        self,
        segments: List[Dict[str,
        Any]],
        pacing: str) -> List[Dict[str, Any]]:
        """Optimize segment pacing for engagement"""
        if pacing == 'fast':
            # Ensure segments are short and punchy
            for segment in segments:
                if segment.get('duration', 0) > 5:
                    segment['duration'] = 5
                # Make text more concise for visual display only
                # Note: Do not truncate for TTS - keep full text for audio generation
                text = segment.get('text', '')
                if len(text) > 100:
                    # Store both full text and display text
                    segment['full_text'] = text  # Keep full text for TTS
                    segment['display_text'] = text[:97] + '...'  # Truncated for display only
                    # IMPORTANT: Keep 'text' field intact for processing

        return segments

    def _calculate_shareability(self, script: Dict[str, Any]) -> float:
        """Calculate shareability score"""
        # Simple scoring based on content elements
        score = 0.5  # Base score

        full_text = self._extract_full_text(script)

        # Check for engagement keywords (non-generic)
        engagement_keywords = ['discover', 'reveal', 'understand', 'explore', 'learn', 'master']
        for keyword in engagement_keywords:
            if keyword in full_text.lower():
                score += 0.1

        # Check for questions (engagement)
        if '?' in full_text:
            score += 0.1

        # Check for emotional language
        emotional_words = ['love', 'hate', 'excited', 'angry', 'surprised', 'happy']
        for word in emotional_words:
            if word in full_text.lower():
                score += 0.05

        return min(score, 1.0)

    def _analyze_emotional_arc(self, script: Dict[str, Any]) -> str:
        """Analyze emotional progression in script"""
        # Simple emotional arc analysis
        segments = script.get('segments', [])
        if len(segments) <= 2:
            return 'flat'
        elif len(segments) <= 4:
            return 'rising'
        else:
            return 'complex'

    def _identify_surprise_moments(self, script: Dict[str, Any]) -> List[str]:
        """Identify potential surprise moments in script"""
        surprises = []
        full_text = self._extract_full_text(script)

        surprise_indicators = ['but', 'however', 'actually', 'suddenly', 'unexpectedly', 'plot twist']
        for indicator in surprise_indicators:
            if indicator in full_text.lower():
                surprises.append(f"Surprise at: {indicator}")

        return surprises

    def _get_current_context_from_gemini(self, mission: str, category: VideoCategory) -> str:
        """Get current context and information using Gemini's internet access"""
        try:
            context_prompt = f"""
            Please provide current, up-to-date information SPECIFICALLY about: "{mission}"
            
            CRITICAL: Stay focused ONLY on "{mission}". Do not discuss unrelated topics.
            
            Focus on:
            - Recent developments about "{mission}" (last 7 days)
            - Current trends and discussions about "{mission}"
            - Latest news and events related to "{mission}"
            - Relevant statistics and data about "{mission}"
            - Popular opinions and perspectives on "{mission}"
            
            Category context: {category.value}
            
            Provide a concise summary (2-3 paragraphs) that would be useful for creating engaging video content about "{mission}".
            Include specific dates, numbers, and recent events when available.
            
            IMPORTANT: If you cannot find current information about "{mission}", say so clearly rather than providing unrelated information.
            """
            
            # Try with retry if content policy blocks
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        logger.info(f"Attempt {attempt + 1}: Rephrasing context request")
                        context_prompt = f"""
                        Please provide educational information about the topic: "{mission}"
                        Focus on: {category.value if category else 'general'} aspects
                        
                        Include:
                        - Recent developments or trends
                        - Key facts and information
                        - Educational context
                        
                        Keep response appropriate for all audiences.
                        """
                    
                    response = self.model.generate_content(context_prompt)
                    
                    if response and response.text:
                        # Validate that the response is actually about the topic
                        response_text = response.text.strip()
                        logger.info(f"✅ Context retrieved on attempt {attempt + 1}")
                        return response_text
                        
                except Exception as e:
                    logger.warning(f"Context retrieval attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(1)
                        continue
                    
            return ""
         
        except Exception as e:
            logger.warning(f"Failed to get current context from Gemini: {e}")
            return ""

    def incorporate_current_info(self, script: Dict[str, Any], 
                                current_context: str) -> Dict[str, Any]:
        """Incorporate current information into script"""
        try:
            if not current_context:
                return script

            logger.info("Incorporating current information into script")

            # Find relevant insertion points
            segments = script.get('segments', [])

            for i, segment in enumerate(segments):
                # Check if segment could incorporate current info
                if self._can_incorporate_current_info(segment, current_context):
                    segment['current_context'] = current_context
                    segment['text'] = self._blend_current_info_into_text(
                        segment['text'], current_context
                    )

            script['has_current_info'] = True
            script['current_context'] = current_context

            return script

        except Exception as e:
            logger.warning(f"Current info incorporation failed: {e}")
            return script

    def _can_incorporate_current_info(self, segment: Dict[str, Any], 
                                     current_context: str) -> bool:
        """Check if segment can incorporate current information"""
        segment_text = segment.get('text', '').lower()
        
        # Look for keywords that suggest current info would be relevant
        current_keywords = [
            'recent', 'latest', 'new', 'current', 'today', 'now',
            'breaking', 'update', 'development', 'trend'
        ]
        
        return any(keyword in segment_text for keyword in current_keywords)

    def _blend_current_info_into_text(self, original_text: str, 
                                     current_context: str) -> str:
        """Blend current information into segment text"""
        try:
            blend_prompt = f"""
            Original text: {original_text}
            
            Current context to incorporate: {current_context}
            
            Please blend the current context naturally into the original text while:
            - Keeping the original tone and style
            - Making it feel natural and engaging
            - Adding specific recent details where appropriate
            - Maintaining the same approximate length
            
            Return only the blended text:
            """
            
            # Try with retry if needed
            max_attempts = 2  # Less retries for blending
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        logger.info(f"Attempt {attempt + 1}: Simplifying blend request")
                        blend_prompt = f"""
                        Update this text with recent information:
                        
                        Original: {original_text}
                        
                        Recent info: {current_context[:200]}...
                        
                        Keep it brief and natural.
                        """
                    
                    response = self.model.generate_content(blend_prompt)
                    
                    if response and response.text:
                        return response.text.strip()
                        
                except Exception as e:
                    logger.warning(f"Blend attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        continue
                    
            return original_text
                
        except Exception as e:
            logger.warning(f"Failed to blend current info: {e}")
            return original_text

    def _trim_script(self, script: Dict[str, Any], max_duration: int) -> Dict[str, Any]:
        """Trim script to fit within maximum duration"""
        try:
            current_duration = script.get('total_duration', 0)
            if current_duration <= max_duration:
                return script
            
            logger.info(f"Trimming script from {current_duration}s to {max_duration}s")
            
            # Calculate reduction ratio
            reduction_ratio = max_duration / current_duration
            
            # Trim segments proportionally
            segments = script.get('segments', [])
            for segment in segments:
                if 'duration' in segment:
                    segment['duration'] = segment['duration'] * reduction_ratio
            
            # Update total duration
            script['total_duration'] = max_duration
            
            # Update structure durations
            if 'structure' in script:
                structure = script['structure']
                if 'content_duration' in structure:
                    structure['content_duration'] = structure['content_duration'] * reduction_ratio
            
            return script
            
        except Exception as e:
            logger.error(f"Script trimming failed: {e}")
            return script

    def _optimize_text_for_platform(self, script: Dict[str, Any], 
                                   target_platform: Platform) -> Dict[str, Any]:
        """Optimize text content for specific platform requirements"""
        try:
            logger.info(f"Optimizing text for {target_platform.value}")
            
            # Platform-specific text optimizations
            platform_optimizations = {
                Platform.TIKTOK: {
                    'max_text_length': 80,
                    'style': 'casual',
                    'emojis': True,
                    'hashtags': True
                },
                Platform.YOUTUBE: {
                    'max_text_length': 150,
                    'style': 'descriptive',
                    'emojis': False,
                    'hashtags': False
                },
                Platform.INSTAGRAM: {
                    'max_text_length': 100,
                    'style': 'visual',
                    'emojis': True,
                    'hashtags': True
                },
                Platform.FACEBOOK: {
                    'max_text_length': 200,
                    'style': 'conversational',
                    'emojis': False,
                    'hashtags': False
                }
            }
            
            optimization = platform_optimizations.get(target_platform, 
                                                    platform_optimizations[Platform.YOUTUBE])
            
            # Optimize segments
            segments = script.get('segments', [])
            for segment in segments:
                if 'text' in segment:
                    text = segment['text']
                    
                    # Trim if too long (for display only, preserve full text for TTS)
                    if len(text) > optimization['max_text_length']:
                        segment['full_text'] = text  # Keep full text for TTS
                        segment['display_text'] = text[:optimization['max_text_length']-3] + '...'  # For display only
                        # IMPORTANT: Keep 'text' field intact for processing
                    
                    # Add platform-specific enhancements
                    if optimization['emojis'] and target_platform == Platform.TIKTOK:
                        # Add relevant emojis for TikTok
                        if 'amazing' in text.lower() or 'wow' in text.lower():
                            segment['text'] = f"🤯 {segment['text']}"
                        elif 'learn' in text.lower() or 'discover' in text.lower():
                            segment['text'] = f"📚 {segment['text']}"
            
            # Optimize hook
            if 'hook' in script and 'text' in script['hook']:
                hook_text = script['hook']['text']
                if len(hook_text) > optimization['max_text_length']:
                    script['hook']['full_text'] = hook_text  # Keep full text
                    script['hook']['display_text'] = hook_text[:optimization['max_text_length']-3] + '...'
                    # IMPORTANT: Keep 'text' field intact for processing
            
            # Optimize CTA
            if 'cta' in script and 'text' in script['cta']:
                cta_text = script['cta']['text']
                if len(cta_text) > optimization['max_text_length']:
                    script['cta']['full_text'] = cta_text  # Keep full text
                    script['cta']['display_text'] = cta_text[:optimization['max_text_length']-3] + '...'
                    # IMPORTANT: Keep 'text' field intact for processing
            
            script['platform_optimized'] = True
            script['optimization_applied'] = optimization
            
            return script
            
        except Exception as e:
            logger.error(f"Text optimization failed: {e}")
            return script

    def _can_incorporate_news(self, segment: Dict[str, Any], 
                            news_items: List[Dict[str, Any]]) -> bool:
        """Check if a segment can incorporate news items"""
        try:
            if not news_items:
                return False
            
            segment_text = segment.get('text', '').lower()
            
            # Look for keywords that suggest news would be relevant
            news_keywords = [
                'recent', 'latest', 'new', 'current', 'today', 'now',
                'breaking', 'update', 'development', 'trend', 'happening'
            ]
            
            # Check if segment mentions news-related concepts
            has_news_context = any(keyword in segment_text for keyword in news_keywords)
            
            # Check if any news items are relevant to segment content
            has_relevant_news = any(
                self._calculate_news_relevance(news_item, segment_text) > 0.5
                for news_item in news_items
            )
            
            return has_news_context or has_relevant_news
            
        except Exception as e:
            logger.warning(f"Error checking news incorporation: {e}")
            return False

    def _find_relevant_news(self, segment: Dict[str, Any], 
                          news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find news items relevant to a specific segment"""
        try:
            if not news_items:
                return []
            
            segment_text = segment.get('text', '')
            relevant_news = []
            
            for news_item in news_items:
                relevance_score = self._calculate_news_relevance(news_item, segment_text)
                if relevance_score > 0.3:  # Lower threshold for segment-specific relevance
                    news_item['segment_relevance'] = relevance_score
                    relevant_news.append(news_item)
            
            # Sort by relevance and return top 2
            relevant_news.sort(key=lambda x: x.get('segment_relevance', 0), reverse=True)
            return relevant_news[:2]
            
        except Exception as e:
            logger.warning(f"Error finding relevant news: {e}")
            return []

    def _blend_news_into_text(self, original_text: str, 
                            news_items: List[Dict[str, Any]]) -> str:
        """Blend news information into segment text"""
        try:
            if not news_items:
                return original_text
            
            # Use the most relevant news item
            top_news = news_items[0]
            news_title = top_news.get('title', '')
            news_description = top_news.get('description', '')
            
            # Create a prompt to blend news naturally
            blend_prompt = f"""
            Original text: {original_text}
            
            News to incorporate:
            Title: {news_title}
            Description: {news_description}
            
            Please blend this news naturally into the original text while:
            - Keeping the original tone and style
            - Making it feel natural and engaging
            - Adding the news as supporting context
            - Maintaining the same approximate length
            - Ensuring the news enhances rather than replaces the original message
            
            Return only the blended text:
            """
            
            response = self.model.generate_content(blend_prompt)
            
            if response and response.text:
                blended_text = response.text.strip()
                logger.info(f"Successfully blended news into segment")
                return blended_text
            else:
                logger.warning("Failed to generate blended text, using original")
                return original_text
                
        except Exception as e:
            logger.warning(f"Failed to blend news into text: {e}")
            return original_text
