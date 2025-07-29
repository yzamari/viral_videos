"""
Separated Script Generator - Two-phase approach for visual and dialogue generation
"""
import json
import re
from typing import Dict, List, Any, Tuple, Optional
from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest
from ..ai.interfaces.base import AIServiceType
from ..models.video_models import Language, Platform
from .ai_content_analyzer import AIContentAnalyzer

logger = get_logger(__name__)

class SeparatedScriptGenerator:
    """
    Generates scripts using separate LLM calls for visual and dialogue content
    This prevents confusion between visual descriptions and spoken text
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize AI service manager
        from ..ai.config import AIConfiguration, AIProvider
        config = AIConfiguration()
        config.api_keys[AIProvider.GEMINI] = api_key
        config.default_providers[AIServiceType.TEXT_GENERATION] = AIProvider.GEMINI
        self.ai_manager = AIServiceManager(config)
        
        # Initialize content analyzer
        self.content_analyzer = AIContentAnalyzer(api_key)
        
        logger.info("✅ Separated Script Generator initialized")
    
    async def generate_separated_script(
        self,
        mission: str,
        duration: int,
        style: str,
        platform: Platform,
        language: Language = Language.ENGLISH_US,
        character_description: str = None
    ) -> Dict[str, Any]:
        """
        Generate script with separate visual and dialogue components
        
        Args:
            mission: The content mission/topic
            duration: Video duration in seconds
            style: Visual style (e.g., "studio ghibli")
            platform: Target platform
            language: Target language for dialogue
            character_description: Character appearance details
            
        Returns:
            Dictionary with separated visual and dialogue data
        """
        logger.info(f"🎬 Generating separated script for '{mission}' ({duration}s)")
        
        # Ensure language is a Language enum for defensive programming
        if isinstance(language, str):
            # Convert string to Language enum
            language_str = language
            language = Language.ENGLISH_US  # Default
            for lang in Language:
                if lang.value == language_str:
                    language = lang
                    break
            logger.debug(f"Converted language string '{language_str}' to enum {language}")
        
        # Calculate segments (8-second clips)
        num_segments = max(1, duration // 8)
        segment_duration = duration / num_segments
        
        logger.info(f"📊 Creating {num_segments} segments of {segment_duration:.1f}s each")
        
        # Phase 1: Generate visual descriptions
        visual_data = await self._generate_visual_descriptions(
            mission, num_segments, style, character_description
        )
        
        # Phase 2: Generate dialogue/narration
        dialogue_data = await self._generate_dialogue_content(
            mission, num_segments, duration, language
        )
        
        # Phase 3: Combine and structure
        combined_script = self._combine_visual_and_dialogue(
            visual_data, dialogue_data, segment_duration
        )
        
        logger.info(f"✅ Generated separated script with {len(combined_script['segments'])} segments")
        return combined_script
    
    async def _generate_visual_descriptions(
        self,
        mission: str,
        num_segments: int,
        style: str,
        character_description: str = None
    ) -> List[Dict[str, Any]]:
        """Generate detailed visual descriptions for each segment"""
        
        # Enhance style description for better results
        style_enhancement = self._enhance_style_description(style, character_description)
        
        prompt = f"""
Create {num_segments} detailed visual descriptions for: "{mission}"

CRITICAL REQUIREMENTS:
1. Generate ONLY visual descriptions - what the camera sees
2. NO dialogue, NO spoken text, NO narration
3. Focus on visual storytelling and cinematography
4. Each description should be 2-3 sentences maximum
5. Include camera movements, lighting, character actions, environments
6. Make descriptions cinematic and detailed for AI image generation

Visual Style: {style_enhancement}
Character Details: {character_description or "Standard realistic appearance"}

COHERENT VISUAL STORYTELLING:
- Focus on ONE MAIN TOPIC throughout all segments
- Ensure visual continuity - each scene flows to the next
- Beginning (Segment 1): Establish setting and introduce topic
- Middle (Segments 2-{num_segments-1}): Develop the single concept step-by-step
- End (Segment {num_segments}): Complete the visual story with satisfying conclusion
- NO ABRUPT CUTS - ensure the story feels complete

Return JSON array:
[
    {{
        "segment_id": 1,
        "visual_description": "Detailed description of what we see visually",
        "camera_work": "Camera angle, movement, focus details",
        "lighting": "Lighting mood and style",
        "character_action": "What the character is doing (no dialogue)"
    }},
    ...
]

Make each visual description rich and cinematic for compelling image generation.
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=2000,  # Larger response for detailed visuals
                temperature=0.8   # More creative for visual descriptions
            )
            
            response = await text_service.generate(request)
            
            # Parse JSON response with better error handling
            try:
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                
                # Try to find JSON array in response
                if response_text.startswith('['):
                    visual_data = json.loads(response_text)
                elif '```json' in response_text:
                    # Extract JSON from markdown code block
                    json_start = response_text.find('[')
                    json_end = response_text.rfind(']') + 1
                    if json_start != -1 and json_end > json_start:
                        visual_data = json.loads(response_text[json_start:json_end])
                    else:
                        raise ValueError("No valid JSON array found in response")
                else:
                    # Try to parse as-is
                    visual_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                logger.debug(f"Response text: {response_text[:500]}...")
                raise RuntimeError(f"Failed to parse visual descriptions: {e}")
            
            logger.info(f"🎨 Generated {len(visual_data)} visual descriptions")
            
            # CRITICAL: Validate segment count to prevent duration mismatches
            if len(visual_data) != num_segments:
                logger.warning(f"⚠️ VISUAL SEGMENT COUNT MISMATCH: Expected {num_segments}, got {len(visual_data)}")
                logger.warning(f"⚠️ This will cause audio-video duration issues!")
                
                # Truncate or pad to match expected count
                if len(visual_data) > num_segments:
                    visual_data = visual_data[:num_segments]
                    logger.info(f"🔧 Truncated to {num_segments} segments")
                elif len(visual_data) < num_segments:
                    # Pad with fallback segments
                    while len(visual_data) < num_segments:
                        visual_data.append({
                            "segment_id": len(visual_data) + 1,
                            "visual_description": f"Scene {len(visual_data) + 1} continuing {mission}",
                            "camera_work": "Standard shot composition",
                            "lighting": "Natural lighting",
                            "character_action": "Relevant character activity"
                        })
                    logger.info(f"🔧 Padded to {num_segments} segments")
            
            return visual_data
            
        except Exception as e:
            logger.error(f"❌ Visual description generation failed: {e}")
            # Fallback to simple visual descriptions
            return self._create_fallback_visuals(num_segments, mission)
    
    async def _generate_dialogue_content(
        self,
        mission: str,
        num_segments: int,
        duration: int,
        language: Language
    ) -> List[Dict[str, Any]]:
        """Generate dialogue/narration content separately"""
        
        # Language instruction - handle both enum and string inputs defensively
        language_instruction = ""
        is_non_english = False
        
        if isinstance(language, str):
            is_non_english = language != "english_us" and language != Language.ENGLISH_US.value
        else:
            is_non_english = language != Language.ENGLISH_US
            
        if is_non_english:
            language_name = self._get_language_name(language)
            language_instruction = f"\\nIMPORTANT: Generate ALL dialogue and narration in {language_name}."
        
        # Calculate word limits
        total_words = int(duration * 2.8)  # 2.8 words per second
        words_per_segment = total_words // num_segments
        
        prompt = f"""
Create EXACTLY {num_segments} dialogue/narration segments for: "{mission}"

🎤 AUDIO-ONLY CONTENT REQUIREMENTS:
1. Generate ONLY what a narrator/character SPEAKS OUT LOUD
2. ABSOLUTELY NO visual descriptions, camera work, or stage directions
3. DO NOT mention what we "see" - only what we "hear"
4. NO phrases like "we see", "the camera shows", "visual", "scene", "shot"
5. Pure spoken dialogue, narration, or voiceover ONLY
6. Each segment: 1-2 sentences maximum for subtitle readability
7. Total word limit: {total_words} words (~{words_per_segment} words per segment)
8. Focus on compelling storytelling through SPOKEN WORD ONLY
9. CRITICAL: Generate EXACTLY {num_segments} segments - no more, no less!

📚 EDUCATIONAL COHERENCE REQUIREMENTS:
- Focus on teaching ONE SINGLE CONCEPT throughout
- No tangents or multiple topics - stay focused
- Beginning: Clear introduction of what we'll learn
- Middle: Step-by-step explanation building knowledge
- End: Satisfying summary and key takeaway
- Each segment should flow naturally to the next
- Ensure the lesson feels COMPLETE, not cut off
{language_instruction}

❌ BAD EXAMPLES (DON'T DO):
- "We see Dragon floating in space"
- "The scene shows a rocket"
- "Visual of math equations"

✅ GOOD EXAMPLES (DO THIS):
- "Welcome to our space adventure!"
- "Dragon explains the math concept"  
- "Here's how ratios work"

DIALOGUE REQUIREMENTS:
- Natural speech patterns and rhythm
- Emotional engagement and compelling delivery
- Clear message progression across segments
- Appropriate tone for the content
- NO contractions (use "do not" instead of "don't")

CONTENT STRUCTURE:
- Opening: Hook the audience immediately
- Middle: Build the story/argument progressively  
- Closing: Strong conclusion or call-to-action

Return JSON array:
[
    {{
        "segment_id": 1,
        "dialogue": "The exact words to be spoken",
        "tone": "emotional tone (excited, serious, mysterious, etc.)",
        "pacing": "delivery pacing (fast, normal, slow)",
        "emphasis": "key words to emphasize"
    }},
    ...
]

Focus on creating engaging, speakable content that tells the story effectively.
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=1500,  # Focused on dialogue content
                temperature=0.7   # Balanced creativity for dialogue
            )
            
            response = await text_service.generate(request)
            
            # Parse JSON response with better error handling
            try:
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                
                # Try to find JSON array in response
                if response_text.startswith('['):
                    dialogue_data = json.loads(response_text)
                elif '```json' in response_text:
                    # Extract JSON from markdown code block
                    json_start = response_text.find('[')
                    json_end = response_text.rfind(']') + 1
                    if json_start != -1 and json_end > json_start:
                        dialogue_data = json.loads(response_text[json_start:json_end])
                    else:
                        raise ValueError("No valid JSON array found in response")
                else:
                    # Try to parse as-is
                    dialogue_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                logger.debug(f"Response text: {response_text[:500]}...")
                raise RuntimeError(f"Failed to parse dialogue content: {e}")
            
            logger.info(f"🗣️ Generated {len(dialogue_data)} dialogue segments")
            
            # CRITICAL: Validate segment count to prevent duration mismatches
            if len(dialogue_data) != num_segments:
                logger.warning(f"⚠️ DIALOGUE SEGMENT COUNT MISMATCH: Expected {num_segments}, got {len(dialogue_data)}")
                logger.warning(f"⚠️ This will cause audio-video duration issues!")
                
                # Truncate or pad to match expected count
                if len(dialogue_data) > num_segments:
                    dialogue_data = dialogue_data[:num_segments]
                    logger.info(f"🔧 Truncated to {num_segments} segments")
                elif len(dialogue_data) < num_segments:
                    # Pad with fallback segments
                    while len(dialogue_data) < num_segments:
                        dialogue_data.append({
                            "segment_id": len(dialogue_data) + 1,
                            "dialogue": f"Continuing our discussion about {mission}",
                            "tone": "neutral",
                            "pacing": "normal",
                            "emphasis": ""
                        })
                    logger.info(f"🔧 Padded to {num_segments} segments")
            
            return dialogue_data
            
        except Exception as e:
            logger.error(f"❌ Dialogue generation failed: {e}")
            # Fallback to simple dialogue
            return self._create_fallback_dialogue(num_segments, mission, language)
    
    def _combine_visual_and_dialogue(
        self,
        visual_data: List[Dict[str, Any]],
        dialogue_data: List[Dict[str, Any]],
        segment_duration: float
    ) -> Dict[str, Any]:
        """Combine visual and dialogue data into final script structure"""
        
        segments = []
        
        # Ensure we have matching numbers of visual and dialogue segments
        min_segments = min(len(visual_data), len(dialogue_data))
        
        # CRITICAL: Warn about segment count mismatches that cause duration issues
        if len(visual_data) != len(dialogue_data):
            logger.warning(f"⚠️ SEGMENT COUNT MISMATCH: Visual={len(visual_data)}, Dialogue={len(dialogue_data)}")
            logger.warning(f"⚠️ This will cause audio-video sync issues and missing content!")
        
        expected_segments = max(1, int(segment_duration * min_segments))
        if min_segments * segment_duration < expected_segments:
            logger.warning(f"⚠️ DURATION MISMATCH: Generated {min_segments} segments but need content for {expected_segments}s")
            logger.warning(f"⚠️ This will cause missing audio at the end of the video!")
        
        for i in range(min_segments):
            visual = visual_data[i]
            dialogue = dialogue_data[i]
            
            segment = {
                "segment_id": i + 1,
                "duration": segment_duration,
                "visual": {
                    "description": visual.get("visual_description", ""),
                    "camera_work": visual.get("camera_work", ""),
                    "lighting": visual.get("lighting", ""),
                    "character_action": visual.get("character_action", "")
                },
                "audio": {
                    "dialogue": dialogue.get("dialogue", ""),
                    "tone": dialogue.get("tone", "neutral"),
                    "pacing": dialogue.get("pacing", "normal"),
                    "emphasis": dialogue.get("emphasis", "")
                },
                # Legacy format for compatibility
                "text": dialogue.get("dialogue", "")
            }
            
            segments.append(segment)
        
        # Create dialogue-only script for TTS
        dialogue_only_script = " ".join([
            dialogue.get("dialogue", "") for dialogue in dialogue_data if dialogue.get("dialogue")
        ]).strip()
        
        return {
            "optimized_script": dialogue_only_script,  # PURE DIALOGUE ONLY
            "final_script": dialogue_only_script,     # PURE DIALOGUE ONLY
            "hook": {
                "text": dialogue_data[0].get("dialogue", "") if dialogue_data else "",
                "type": "ai_generated",
                "duration_seconds": segment_duration
            },
            "segments": segments,
            "total_duration": len(segments) * segment_duration,
            "generation_method": "separated_llm_calls",
            "dialogue_only_script": dialogue_only_script,  # Extra safety
            "visual_descriptions": visual_data  # Keep visual separate
        }
    
    def _enhance_style_description(self, style: str, character_description: str = None) -> str:
        """Enhance style description for better visual generation"""
        
        style_enhancements = {
            "studio ghibli": "Studio Ghibli animation style with magical realism, hand-drawn aesthetic, soft lighting, whimsical characters, detailed backgrounds, nature integration, dreamy atmosphere, and Japanese animation quality",
            "ghibli": "Studio Ghibli animation style with magical realism, hand-drawn aesthetic, soft lighting, whimsical characters, detailed backgrounds, nature integration, dreamy atmosphere, and Japanese animation quality",
            "realistic": "Photorealistic style with natural lighting, detailed textures, authentic human expressions, real-world environments, and cinematic composition",
            "cinematic": "Hollywood cinematic style with dramatic lighting, professional cinematography, movie-quality production values, and epic visual storytelling",
            "anime": "High-quality anime style with detailed character designs, vibrant colors, dynamic poses, and expressive animation"
        }
        
        enhanced = style_enhancements.get(style.lower(), style)
        
        if character_description:
            enhanced += f". Character appearance: {character_description}"
        
        return enhanced
    
    def _get_language_name(self, language) -> str:
        """Get human-readable language name"""
        # Handle both Language enum and string inputs for defensive programming
        if isinstance(language, str):
            # Convert string back to enum if possible
            try:
                for lang_enum in Language:
                    if lang_enum.value == language:
                        language = lang_enum
                        break
                else:
                    # If string doesn't match any enum value, default to English
                    return "English"
            except Exception:
                return "English"
        
        language_names = {
            Language.HEBREW: "Hebrew (עברית)",
            Language.ARABIC: "Arabic (العربية)",
            Language.PERSIAN: "Persian/Farsi (فارسی)",
            Language.FRENCH: "French (Français)",
            Language.SPANISH: "Spanish (Español)",
            Language.GERMAN: "German (Deutsch)",
            Language.ITALIAN: "Italian (Italiano)",
            Language.PORTUGUESE: "Portuguese (Português)",
            Language.RUSSIAN: "Russian (Русský)",
            Language.CHINESE: "Chinese (中文)",
            Language.JAPANESE: "Japanese (日本語)",
            Language.ENGLISH_UK: "British English",
            Language.ENGLISH_IN: "Indian English"
        }
        return language_names.get(language, "English")
    
    def _create_fallback_visuals(self, num_segments: int, mission: str) -> List[Dict[str, Any]]:
        """Create fallback visual descriptions if AI generation fails"""
        fallback_visuals = []
        
        for i in range(num_segments):
            fallback_visuals.append({
                "segment_id": i + 1,
                "visual_description": f"Scene {i + 1} related to {mission}",
                "camera_work": "Standard shot composition",
                "lighting": "Natural lighting",
                "character_action": "Relevant character activity"
            })
        
        return fallback_visuals
    
    def _create_fallback_dialogue(
        self,
        num_segments: int,
        mission: str,
        language: Language
    ) -> List[Dict[str, Any]]:
        """Create fallback dialogue if AI generation fails"""
        fallback_dialogue = []
        
        base_text = "This is about " + mission
        
        # Handle both enum and string inputs defensively
        is_hebrew = False
        if isinstance(language, str):
            is_hebrew = language == "hebrew" or language == Language.HEBREW.value
        else:
            is_hebrew = language == Language.HEBREW
            
        if is_hebrew:
            base_text = "זה על " + mission
        
        for i in range(num_segments):
            fallback_dialogue.append({
                "segment_id": i + 1,
                "dialogue": f"{base_text} - part {i + 1}",
                "tone": "neutral",
                "pacing": "normal",
                "emphasis": ""
            })
        
        return fallback_dialogue