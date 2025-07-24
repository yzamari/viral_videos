"""
Voice Director Agent - AI-powered intelligent voice selection
Decides optimal voice configurations for videos based on content, emotion, and
        narrative flow
"""
import os
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from ..config.ai_model_config import DEFAULT_AI_MODEL
try:
    from google.generativeai.generative_models import GenerativeModel
    genai_available = True
except ImportError:
    GenerativeModel = None
    genai_available = False

from ..utils.logging_config import get_logger
from ..models.video_models import Language, Platform, VideoCategory
from ..utils.json_fixer import create_json_fixer
from .gemini_helper import GeminiModelHelper, ensure_api_key

logger = get_logger(__name__)

class VoicePersonality(str, Enum):
    """Voice personality types for different content"""
    NARRATOR = "narrator"           # Professional, authoritative
    STORYTELLER = "storyteller"     # Warm, engaging
    EDUCATOR = "educator"           # Clear, patient
    COMEDIAN = "comedian"           # Playful, energetic
    DRAMATIC = "dramatic"           # Deep, emotional
    YOUNG_ADULT = "young_adult"     # Fresh, relatable
    WISE = "wise"                   # Mature, experienced
    ENTHUSIAST = "enthusiast"       # Excited, passionate

class VoiceGender(str, Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"  # Use both throughout video
    AUTO = "auto"    # Let AI decide

class VoiceDirectorAgent:
    """AI agent that intelligently selects voices for optimal content delivery"""

    def __init__(self, api_key: str):
        self.api_key = ensure_api_key(api_key)
        if genai_available and GenerativeModel:
            self.model = GeminiModelHelper.get_configured_model(self.api_key)
        else:
            logger.warning("Google Generative AI is not available. Voice selection will be limited.")
            self.model = None
        
        # Initialize JSON fixer
        self.json_fixer = create_json_fixer(api_key)

        # Voice mapping for different languages and personalities
        self.voice_database = {
            Language.ENGLISH_US: {
                VoicePersonality.NARRATOR: {
                    "male": ["en-US-Journey-D", "en-US-Neural2-D", "en-US-Neural2-J"],
                    "female": ["en-US-Journey-O", "en-US-Neural2-F", "en-US-Neural2-H"]
                },
                VoicePersonality.STORYTELLER: {
                    "male": ["en-US-Journey-D", "en-US-Neural2-I"],
                    "female": ["en-US-Journey-F", "en-US-Neural2-A", "en-US-Neural2-C"]
                },
                VoicePersonality.EDUCATOR: {
                    "male": ["en-US-Neural2-D", "en-US-Studio-Q"],
                    "female": ["en-US-Journey-O", "en-US-Neural2-F", "en-US-Studio-O"]
                },
                VoicePersonality.COMEDIAN: {
                    "male": ["en-US-Neural2-I"],
                    "female": ["en-US-Journey-F", "en-US-Neural2-C", "en-US-Neural2-G"]
                },
                VoicePersonality.DRAMATIC: {
                    "male": ["en-US-Journey-D", "en-US-Neural2-D", "en-US-Neural2-J"],
                    "female": ["en-US-Neural2-H", "en-US-Neural2-F"]
                },
                VoicePersonality.YOUNG_ADULT: {
                    "male": ["en-US-Neural2-I"],
                    "female": ["en-US-Journey-F", "en-US-Neural2-C", "en-US-Neural2-G"]
                },
                VoicePersonality.WISE: {
                    "male": ["en-US-Neural2-J", "en-US-Studio-Q"],
                    "female": ["en-US-Neural2-F", "en-US-Studio-O"]
                },
                VoicePersonality.ENTHUSIAST: {
                    "male": ["en-US-Neural2-I"],
                    "female": ["en-US-Journey-F", "en-US-Neural2-G"]
                }
            },
            Language.HEBREW: {
                VoicePersonality.NARRATOR: {
                    "male": ["he-IL-Wavenet-B", "he-IL-Standard-B"],
                    "female": ["he-IL-Wavenet-A", "he-IL-Standard-A", "he-IL-Wavenet-C"]
                },
                VoicePersonality.STORYTELLER: {
                    "male": ["he-IL-Wavenet-B"],
                    "female": ["he-IL-Wavenet-A", "he-IL-Wavenet-C"]
                },
                VoicePersonality.EDUCATOR: {
                    "male": ["he-IL-Standard-B", "he-IL-Wavenet-D"],
                    "female": ["he-IL-Standard-A", "he-IL-Wavenet-A"]
                },
                VoicePersonality.COMEDIAN: {
                    "male": ["he-IL-Wavenet-B"],
                    "female": ["he-IL-Wavenet-C"]
                },
                VoicePersonality.DRAMATIC: {
                    "male": ["he-IL-Wavenet-B", "he-IL-Wavenet-D"],
                    "female": ["he-IL-Wavenet-A"]
                },
                VoicePersonality.YOUNG_ADULT: {
                    "male": ["he-IL-Wavenet-B"],
                    "female": ["he-IL-Wavenet-C"]
                },
                VoicePersonality.WISE: {
                    "male": ["he-IL-Standard-B", "he-IL-Wavenet-D"],
                    "female": ["he-IL-Standard-A"]
                },
                VoicePersonality.ENTHUSIAST: {
                    "male": ["he-IL-Wavenet-B"],
                    "female": ["he-IL-Wavenet-C"]
                }
            },
            Language.ARABIC: {
                VoicePersonality.NARRATOR: {
                    "male": ["ar-XA-Wavenet-B", "ar-XA-Standard-B"],
                    "female": ["ar-XA-Wavenet-A", "ar-XA-Standard-A", "ar-XA-Wavenet-C"]
                },
                VoicePersonality.STORYTELLER: {
                    "male": ["ar-XA-Wavenet-B"],
                    "female": ["ar-XA-Wavenet-A", "ar-XA-Wavenet-C"]
                },
                VoicePersonality.EDUCATOR: {
                    "male": ["ar-XA-Standard-B", "ar-XA-Wavenet-D"],
                    "female": ["ar-XA-Standard-A", "ar-XA-Wavenet-A"]
                },
                VoicePersonality.COMEDIAN: {
                    "male": ["ar-XA-Wavenet-B"],
                    "female": ["ar-XA-Wavenet-C"]
                },
                VoicePersonality.DRAMATIC: {
                    "male": ["ar-XA-Wavenet-B", "ar-XA-Wavenet-D"],
                    "female": ["ar-XA-Wavenet-A"]
                },
                VoicePersonality.YOUNG_ADULT: {
                    "male": ["ar-XA-Wavenet-B"],
                    "female": ["ar-XA-Wavenet-C"]
                },
                VoicePersonality.WISE: {
                    "male": ["ar-XA-Standard-B", "ar-XA-Wavenet-D"],
                    "female": ["ar-XA-Standard-A"]
                },
                VoicePersonality.ENTHUSIAST: {
                    "male": ["ar-XA-Wavenet-B"],
                    "female": ["ar-XA-Wavenet-C"]
                }
            },
            Language.FRENCH: {
                VoicePersonality.NARRATOR: {
                    "male": ["fr-FR-Wavenet-B", "fr-FR-Standard-B"],
                    "female": ["fr-FR-Wavenet-A", "fr-FR-Standard-A", "fr-FR-Wavenet-C"]
                },
                VoicePersonality.STORYTELLER: {
                    "male": ["fr-FR-Wavenet-B"],
                    "female": ["fr-FR-Wavenet-A", "fr-FR-Wavenet-C"]
                },
                VoicePersonality.EDUCATOR: {
                    "male": ["fr-FR-Standard-B", "fr-FR-Wavenet-D"],
                    "female": ["fr-FR-Standard-A", "fr-FR-Wavenet-A"]
                },
                VoicePersonality.COMEDIAN: {
                    "male": ["fr-FR-Wavenet-B"],
                    "female": ["fr-FR-Wavenet-C"]
                },
                VoicePersonality.DRAMATIC: {
                    "male": ["fr-FR-Wavenet-B", "fr-FR-Wavenet-D"],
                    "female": ["fr-FR-Wavenet-A"]
                },
                VoicePersonality.YOUNG_ADULT: {
                    "male": ["fr-FR-Wavenet-B"],
                    "female": ["fr-FR-Wavenet-C"]
                },
                VoicePersonality.WISE: {
                    "male": ["fr-FR-Standard-B", "fr-FR-Wavenet-D"],
                    "female": ["fr-FR-Standard-A"]
                },
                VoicePersonality.ENTHUSIAST: {
                    "male": ["fr-FR-Wavenet-B"],
                    "female": ["fr-FR-Wavenet-C"]
                }
            },
            Language.SPANISH: {
                VoicePersonality.NARRATOR: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                },
                VoicePersonality.STORYTELLER: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                },
                VoicePersonality.EDUCATOR: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                },
                VoicePersonality.COMEDIAN: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                },
                VoicePersonality.DRAMATIC: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                },
                VoicePersonality.YOUNG_ADULT: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                },
                VoicePersonality.WISE: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                },
                VoicePersonality.ENTHUSIAST: {
                    "male": ["es-ES-Standard-B"],
                    "female": ["es-ES-Standard-A"]
                }
            }
        }

        logger.info(
            "🎭 Voice Director Agent initialized with AI-powered voice selection")

    def get_voice_config(self, content: str, platform: Platform, num_clips: int, 
                        duration_seconds: int,
                        style: str = "professional", tone: str = "engaging") -> Dict[str, Any]:
        """Get voice configuration for the given content"""
        try:
            # Use the existing analyze_content_and_select_voices method
            result = self.analyze_content_and_select_voices(
                mission=content,
                script=content,
                language=Language.ENGLISH_US,
                platform=platform,
                category=VideoCategory.COMEDY,  # Default category
                duration_seconds=duration_seconds,  # Use actual duration
                num_clips=num_clips
            )
            
            # Extract voice configuration
            if 'voices' in result:
                return {
                    'voices': result['voices'],
                    'strategy': result.get('strategy', 'single'),
                    'primary_personality': result.get('primary_personality', 'professional')
                }
            else:
                # Fallback configuration
                return self._create_fallback_voice_config(content, Language.ENGLISH_US, num_clips)
                
        except Exception as e:
            logger.error(f"❌ Voice config generation failed: {e}")
            return self._create_fallback_voice_config(content, Language.ENGLISH_US, num_clips)

    def analyze_content_and_select_voices(self,
                                          mission: str,
                                          script: str,
                                          language: Language,
                                          platform: Platform,
                                          category: VideoCategory,
                                          duration_seconds: int,
                                          num_clips: int) -> Dict[str, Any]:
        """AI-powered analysis to select optimal voice configuration"""

        logger.info(f"🎭 AI analyzing content for voice selection: {mission}")

        try:
            # Create comprehensive AI prompt for voice analysis
            analysis_prompt = f"""
            You are an expert Voice Director for viral video content. Analyze this content and
                    decide the optimal voice strategy.

            CONTENT ANALYSIS:
            Mission: {mission}
            Script Preview: {script[:300]}...
            Language: {language.value if hasattr(language, 'value') else str(language)}
            Platform: {platform.value if hasattr(platform, 'value') else str(platform)}
            Category: {category.value if hasattr(category, 'value') else str(category)}
            Duration: {duration_seconds}s
            Number of clips: {num_clips}

            VOICE STRATEGY OPTIONS:
            1. Single Voice: One consistent voice throughout (PREFERRED - most professional)
            2. Multiple Speakers: ONLY when content has distinct speakers/characters in dialogue
            
            CRITICAL RULES:
            - ALWAYS USE SINGLE VOICE for consistency and professionalism
            - NEVER switch voices mid-sentence, mid-word, or mid-phrase
            - Multiple voices are ONLY allowed when content has explicit dialogue between different speakers
            - Voice changes can ONLY happen at complete sentence boundaries (after punctuation: . ! ?)
            - Each voice segment must contain complete sentences only
            - If content doesn't have distinct speakers/dialogue, use single voice strategy
            - Single voice ensures consistent pronunciation and natural flow
            - Voice switching creates jarring audio experience and should be avoided

            PERSONALITY OPTIONS:
            - narrator: Professional, authoritative
            - storyteller: Warm, engaging
            - educator: Clear, patient
            - comedian: Playful, energetic
            - dramatic: Deep, emotional
            - young_adult: Fresh, relatable
            - wise: Mature, experienced
            - enthusiast: Excited, passionate

            GENDER OPTIONS:
            - male: Male voice(s)
            - female: Female voice(s)
            - mixed: Both male and female
            - auto: AI decides best fit

            ANALYSIS REQUIREMENTS:
            1. DEFAULT TO SINGLE VOICE - only use multiple if content has distinct speakers
            2. Analyze if content contains dialogue, interviews, or conversations between different people
            3. Select personality type that matches the content tone and target audience
            4. Choose gender approach that fits the content context
            5. Consider platform-specific preferences while maintaining single voice preference
            6. EMOTION ANALYSIS: Analyze content emotion and assign appropriate emotions
            7. PITCH & SPEED: Consider target audience age and content energy level
            8. CONTEXT AWARENESS: Factor in business type, target demographics, and call-to-action
            9. SENTENCE BOUNDARY ANALYSIS: Ensure voice changes ONLY at sentence/speaker boundaries
            10. ENGAGEMENT OPTIMIZATION: Single consistent voice is more professional and engaging

            EMOTION OPTIONS:
            - excited: High energy, enthusiastic (pitch +2.0, speed 1.1)
            - enthusiastic: Positive energy (pitch +1.0, speed 1.05)
            - neutral: Balanced, professional (pitch 0.0, speed 1.0)
            - dramatic: Deep, impactful (pitch -1.0, speed 0.9)
            - authoritative: Confident, commanding (pitch -0.5, speed 0.95)
            - conversational: Natural, friendly (pitch 0.0, speed 1.0)
            - calm: Relaxed, soothing (pitch -0.5, speed 0.9)
            - playful: Fun, energetic (pitch +1.5, speed 1.1)
            - urgent: Time-sensitive, compelling (pitch +0.5, speed 1.15)
            - warm: Inviting, welcoming (pitch +0.5, speed 1.0)

            OUTPUT FORMAT (JSON):
            {{
                "strategy": "single|multiple_speakers",
                "has_distinct_speakers": true/false,
                "speaker_count": 1,
                "primary_personality": "personality_type",
                "primary_gender": "male|female|auto",
                "use_multiple_voices": true/false,
                "voice_changes_per_clip": true/false,
                "reasoning": "detailed explanation including speaker analysis and why single/multiple voice was chosen",
                "clip_voice_plan": [
                    {{
                        "clip_index": 0,
                        "personality": "narrator",
                        "gender": "female",
                        "emotion": "neutral",
                        "pitch_adjustment": 0.0,
                        "speed_adjustment": 1.0,
                        "energy_level": "medium",
                        "content_focus": "introduction",
                        "speaker_id": "main"
                    }},
                    {{
                        "clip_index": 1,
                        "personality": "narrator",
                        "gender": "female",
                        "emotion": "conversational",
                        "pitch_adjustment": 0.0,
                        "speed_adjustment": 1.0,
                        "energy_level": "medium",
                        "content_focus": "main_content",
                        "speaker_id": "main"
                    }}
                ],
                "confidence_score": 0.85,
                "target_audience_analysis": "analysis of target demographic and
                        voice preferences"
            }}

            IMPORTANT: Unless the content clearly contains dialogue, interviews, or multiple distinct speakers,
            you MUST use a single voice throughout. Set "strategy": "single", "use_multiple_voices": false,
            "has_distinct_speakers": false, "speaker_count": 1, and use the same personality/gender
            for ALL clips with only emotion variations.
            
            Make strategic decisions that will maximize engagement for {platform.value if hasattr(
                platform,
                'value') else str(platform)} in {language.value if hasattr(language,
                'value') else str(language)}.
            Return ONLY the JSON response.
            """

            if not self.model:
                raise ImportError("Google Generative AI is not available. Cannot generate voice analysis.")

            response = self.model.generate_content(analysis_prompt)

            # Use centralized JSON fixer to handle parsing
            expected_structure = {
                "strategy": str,
                "has_distinct_speakers": bool,
                "speaker_count": int,
                "primary_personality": str,
                "primary_gender": str,
                "use_multiple_voices": bool,
                "voice_changes_per_clip": bool,
                "reasoning": str,
                "clip_voice_plan": list
            }
            
            analysis = self.json_fixer.fix_json(response.text, expected_structure)
            
            if analysis:
                logger.info(f"🎭 AI Voice Strategy: {analysis.get('strategy', 'unknown')}")
                logger.info(f"🗣️ Distinct Speakers: {analysis.get('has_distinct_speakers', False)}")
                logger.info(f"👥 Speaker Count: {analysis.get('speaker_count', 1)}")
                logger.info(f"🎤 Primary Personality: {analysis.get('primary_personality', 'unknown')}")
                logger.info(f"👥 Multiple Voices: {analysis.get('use_multiple_voices', False)}")
                logger.info(f"🧠 AI Reasoning: {analysis.get('reasoning', 'No reasoning provided')[:100]}...")

                # Convert to voice selections
                voice_config = self._convert_analysis_to_voices(analysis, language, num_clips)
            else:
                logger.error("❌ JSON fixer could not parse AI response")
                logger.info("🔄 Creating fallback voice configuration")
                voice_config = self._create_fallback_voice_config(mission, language, num_clips)

        except Exception as e:
            logger.error(f"❌ AI voice analysis failed: {e}")
            voice_config = self._create_fallback_voice_config(mission, language, num_clips)
        
        return voice_config

    def _convert_analysis_to_voices(
            self, analysis: Dict, language: Language, num_clips: int) -> Dict[str, Any]:
        """Convert AI analysis to specific voice selections"""

        voice_config = {
            "strategy": analysis["strategy"],
            "clip_voices": [],
            "voice_variety": analysis.get("use_multiple_voices", False)
        }

        # Get clip voice plan from AI or create one
        clip_plan = analysis.get("clip_voice_plan", [])

        if not clip_plan:
            # Create plan based on strategy
            clip_plan = self._create_clip_voice_plan(analysis, num_clips)

        # Ensure we have enough clips - if not, extend the plan
        while len(clip_plan) < num_clips:
            # Use the last clip info for additional clips
            last_clip = clip_plan[-1] if clip_plan else {
                "personality": analysis["primary_personality"],
                "gender": analysis["primary_gender"],
                "emotion": "neutral"
            }
            clip_plan.append({
                "clip_index": len(clip_plan),
                "personality": last_clip["personality"],
                "gender": last_clip["gender"],
                "emotion": last_clip.get("emotion", "neutral")
            })

        # Convert each clip plan to actual voice selection
        # For single voice strategy, select voice once and reuse
        single_voice_name = None
        if analysis["strategy"] == "single":
            single_voice_name = self._select_voice_for_clip(
                language,
                analysis["primary_personality"],
                analysis["primary_gender"],
                "neutral"
            )
        
        for i in range(num_clips):
            if i < len(clip_plan):
                clip_info = clip_plan[i]
            else:
                # Use last clip info for remaining clips
                clip_info = clip_plan[-1] if clip_plan else {
                    "personality": analysis["primary_personality"],
                    "gender": analysis["primary_gender"],
                    "emotion": "neutral"
                }

            # Select actual voice - use single voice if strategy is single
            if single_voice_name:
                voice_name = single_voice_name
            else:
                voice_name = self._select_voice_for_clip(
                    language,
                    clip_info["personality"],
                    clip_info["gender"],
                    clip_info.get("emotion", "neutral")
                )

            # Use AI-provided adjustments if available, otherwise use
            # emotion-based defaults
            pitch_adjustment = clip_info.get(
                "pitch_adjustment",
                self._get_pitch_for_emotion(
                    clip_info.get(
                        "emotion",
                        "neutral")))
            speed_adjustment = clip_info.get(
                "speed_adjustment",
                self._get_speed_for_emotion(
                    clip_info.get(
                        "emotion",
                        "neutral")))

            voice_config["clip_voices"].append({
                "clip_index": i,
                "voice_name": voice_name,
                "personality": clip_info["personality"],
                "gender": clip_info["gender"],
                "emotion": clip_info.get("emotion", "neutral"),
                "speed": speed_adjustment,
                "pitch": pitch_adjustment,
                "energy_level": clip_info.get("energy_level", "medium"),
                "content_focus": clip_info.get("content_focus", "general"),
                "ai_reasoning": clip_info.get("reasoning", "")
            })

        logger.info(
            f"🎤 Generated voice config for {num_clips} clips with {
                len(
                    set(
                        v['voice_name'] for v in voice_config['clip_voices']))} unique voices")

        return voice_config

    def _create_clip_voice_plan(
            self,
            analysis: Dict,
            num_clips: int) -> List[Dict]:
        """Create voice plan for clips based on strategy"""

        strategy = analysis["strategy"]
        primary_personality = analysis["primary_personality"]
        primary_gender = analysis["primary_gender"]

        clip_plan = []

        if strategy == "single" or strategy == "multiple_speakers":
            # For single strategy: Same voice for all clips
            # For multiple_speakers: Only use different voices if truly distinct speakers
            has_distinct_speakers = analysis.get("has_distinct_speakers", False)
            speaker_count = analysis.get("speaker_count", 1)
            
            if strategy == "multiple_speakers" and has_distinct_speakers and speaker_count > 1:
                # Only use multiple voices for actual different speakers
                for i in range(num_clips):
                    speaker_id = i % speaker_count  # Distribute clips among speakers
                    # Alternate gender for different speakers
                    gender = "male" if speaker_id % 2 == 0 else "female" if primary_gender == "mixed" else primary_gender
                    clip_plan.append({
                        "clip_index": i,
                        "personality": primary_personality,
                        "gender": gender,
                        "emotion": "conversational",
                        "speaker_id": f"speaker_{speaker_id}"
                    })
            else:
                # Default to single voice (even if strategy was multiple_speakers but no distinct speakers)
                for i in range(num_clips):
                    clip_plan.append({
                        "clip_index": i,
                        "personality": primary_personality,
                        "gender": primary_gender,
                        "emotion": "neutral",
                        "speaker_id": "main"
                    })

        elif strategy == "dialogue":
            # Alternating voices for dialogue effect
            genders = [
                "male",
                "female"] if primary_gender == "mixed" else [
                primary_gender,
                primary_gender]
            personalities = [primary_personality, "storyteller"]

            for i in range(num_clips):
                clip_plan.append({
                    "clip_index": i,
                    "personality": personalities[i % 2],
                    "gender": genders[i % 2],
                    "emotion": "conversational"
                })

        elif strategy == "narrator_character":
            # Main narrator with character voices
            for i in range(num_clips):
                if i == 0 or i == num_clips - 1:
                    # Narrator for intro/outro
                    clip_plan.append({
                        "clip_index": i,
                        "personality": "narrator",
                        "gender": primary_gender,
                        "emotion": "authoritative"
                    })
                else:
                    # Character voices for content
                    clip_plan.append({
                        "clip_index": i,
                        "personality": "enthusiast",
                        "gender": "auto",
                        "emotion": "excited"
                    })
        else:
            # Fallback to single voice for any unrecognized strategy
            logger.warning(f"⚠️ Unknown strategy '{strategy}', defaulting to single voice")
            for i in range(num_clips):
                clip_plan.append({
                    "clip_index": i,
                    "personality": primary_personality,
                    "gender": primary_gender,
                    "emotion": "neutral",
                    "speaker_id": "main"
                })

        return clip_plan

    def _select_voice_for_clip(
            self,
            language: Language,
            personality: str,
            gender: str,
            emotion: str) -> str:
        """Select specific voice for a clip"""

        try:
            personality_enum = VoicePersonality(personality)
        except ValueError:
            personality_enum = VoicePersonality.NARRATOR

        # Get voice options for this language and personality
        if language in self.voice_database and personality_enum in self.voice_database[
                language]:
            voice_options = self.voice_database[language][personality_enum]

            # Select gender
            if gender == "auto":
                # Choose randomly between male and female
                gender = random.choice(["male", "female"])
            elif gender == "mixed":
                # For mixed, alternate or choose randomly
                gender = random.choice(["male", "female"])

            if gender in voice_options and voice_options[gender]:
                # Select voice from available options
                selected_voice = random.choice(voice_options[gender])
                logger.info(
                    f"🎤 Selected voice: {selected_voice} ({personality}, {gender}, {emotion})")
                return selected_voice

        # Fallback to default voice for language
        fallback_voices = {
            Language.ENGLISH_US: "en-US-Journey-F",
            Language.HEBREW: "he-IL-Wavenet-A",
            Language.ARABIC: "ar-XA-Wavenet-A",
            Language.FRENCH: "fr-FR-Wavenet-A",
            Language.SPANISH: "es-ES-Wavenet-A"
        }

        fallback = fallback_voices.get(language, "en-US-Journey-F")
        logger.warning(f"⚠️ Using fallback voice: {fallback}")
        return fallback

    def _get_speed_for_emotion(self, emotion: str) -> float:
        """Get speaking speed based on emotion"""
        speed_map = {
            "excited": 1.1,
            "enthusiastic": 1.05,
            "neutral": 1.0,
            "dramatic": 0.9,
            "authoritative": 0.95,
            "conversational": 1.0,
            "calm": 0.9,
            "playful": 1.1,
            "urgent": 1.2,  # Updated to match test expectation
            "warm": 1.0
        }
        return speed_map.get(emotion, 1.0)

    def _get_pitch_for_emotion(self, emotion: str) -> float:
        """Get pitch adjustment based on emotion"""
        pitch_map = {
            "excited": 2.0,
            "enthusiastic": 1.0,
            "neutral": 0.0,
            "dramatic": -1.0,
            "authoritative": -0.5,
            "conversational": 0.0,
            "calm": -0.5,
            "playful": 1.5,
            "urgent": 0.5,
            "warm": 0.5,
            "sad": -2.0,  # Added to match test expectation
            "angry": 1.0   # Added to match test expectation
        }
        return pitch_map.get(emotion, 0.0)

    def _create_fallback_voice_config(
            self, mission: str, language: Language, num_clips: int) -> Dict[str, Any]:
        """Create fallback voice configuration when AI analysis fails"""

        logger.info("🔄 Creating fallback voice configuration")

        # Simple heuristics for fallback
        if "comedy" in mission.lower() or "funny" in mission.lower():
            personality = VoicePersonality.COMEDIAN
            emotion = "excited"
        elif "education" in mission.lower() or "learn" in mission.lower():
            personality = VoicePersonality.EDUCATOR
            emotion = "neutral"
        elif "story" in mission.lower() or "tale" in mission.lower():
            personality = VoicePersonality.STORYTELLER
            emotion = "conversational"
        else:
            personality = VoicePersonality.NARRATOR
            emotion = "neutral"

        # Create voice list for all clips
        voices = []
        for i in range(num_clips):
            voice_name = self._select_voice_for_clip(
                language, personality.value, "auto", emotion)

            voices.append({
                "clip_index": i,
                "voice_name": voice_name,
                "personality": personality.value,
                "gender": "auto",
                "emotion": emotion,
                "speed": self._get_speed_for_emotion(emotion),
                "pitch": self._get_pitch_for_emotion(emotion)
            })

        # Return structure that matches the expected format
        return {
            "strategy": "single",
            "clip_voices": voices,
            "voice_variety": False,
            "reasoning": "Fallback configuration when AI analysis fails"
        }
