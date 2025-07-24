"""
Enhanced Script Processor
Ensures proper punctuation, short sentences, and TTS-optimized formatting
"""
import re
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from ..utils.logging_config import get_logger
from ..models.video_models import Language, Platform, VideoCategory
from ..utils.json_fixer import JSONFixer
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest

logger = get_logger(__name__)

class EnhancedScriptProcessor:
    """Processes scripts for optimal TTS delivery with proper punctuation and structure"""

    def __init__(self, api_key: str = None, ai_manager: AIServiceManager = None):
        if ai_manager:
            self.ai_manager = ai_manager
        else:
            if not api_key:
                raise ValueError("Either api_key or ai_manager must be provided")
            # Create AI configuration with the provided API key
            from ..ai.config import AIConfiguration, AIProvider
            from ..ai.factory import AIServiceType
            config = AIConfiguration()
            config.api_keys[AIProvider.GEMINI] = api_key
            config.default_providers[AIServiceType.TEXT_GENERATION] = AIProvider.GEMINI
            self.ai_manager = AIServiceManager(config)
        
        # Keep json_fixer for compatibility
        self.json_fixer = JSONFixer(api_key or "dummy")

        # TTS optimization rules by language
        self.language_rules = {
            Language.ENGLISH_US: {
                "max_sentence_length": 15,  # words
                "preferred_punctuation": [".", "!", "?", ","],
                "pause_markers": [". ", ", ", "! ", "? "],
                "avoid_patterns": ["...", "—", "–"],
                "sentence_endings": [".", "!", "?"]
            },
            Language.HEBREW: {
                "max_sentence_length": 12,  # Hebrew words tend to be longer
                "preferred_punctuation": [".", "!", "?", ","],
                "pause_markers": [". ", ", ", "! ", "? "],
                "avoid_patterns": ["...", "—", "–", "(", ")", "[", "]"],
                "sentence_endings": [".", "!", "?"],
                "rtl_specific": True
            },
            Language.ARABIC: {
                "max_sentence_length": 12,
                "preferred_punctuation": [".", "!", "?", ",", "؟", "!"],
                "pause_markers": [". ", ", ", "! ", "? ", "؟ ", "! "],
                "avoid_patterns": ["...", "—", "–", "(", ")", "[", "]"],
                "sentence_endings": [".", "!", "?", "؟"],
                "rtl_specific": True
            },
            Language.FRENCH: {
                "max_sentence_length": 16,
                "preferred_punctuation": [".", "!", "?", ",", ";", ":"],
                "pause_markers": [". ", ", ", "! ", "? ", "; ", ": "],
                "avoid_patterns": ["...", "—", "–"],
                "sentence_endings": [".", "!", "?"]
            },
            Language.SPANISH: {
                "max_sentence_length": 16,
                "preferred_punctuation": [".", "!", "?", ",", "¿", "¡"],
                "pause_markers": [". ", ", ", "! ", "? ", "¿ ", "¡ "],
                "avoid_patterns": ["...", "—", "–"],
                "sentence_endings": [".", "!", "?"]
            },
            Language.GERMAN: {
                "max_sentence_length": 18,  # German compound words
                "preferred_punctuation": [".", "!", "?", ","],
                "pause_markers": [". ", ", ", "! ", "? "],
                "avoid_patterns": ["...", "—", "–"],
                "sentence_endings": [".", "!", "?"]
            }
        }

        logger.info("✅ Enhanced Script Processor initialized")

    async def process_script_for_tts(self, script_content: str, language,
                             target_duration: float = None) -> Dict[str, Any]:
        """Process script with AI optimization for exact duration matching"""
        try:
            # Handle both string and enum inputs for language
            if isinstance(language, str):
                language_value = language
                # Try to convert to enum if possible
                try:
                    from src.models.video_models import Language
                    language_enum = Language(language)
                    language_value = language_enum.value
                except (ValueError, ImportError):
                    # If conversion fails, use string as-is
                    language_value = language
            else:
                # Assume it's already an enum
                language_value = language.value if hasattr(language, 'value') else str(language)
            
            logger.info(f"📝 Processing script for TTS optimization ({language_value})")
            if target_duration:
                logger.info(f"🎯 Target duration: {target_duration} seconds")

            # Enhanced prompt for duration-aware script processing
            processing_prompt = f"""
You are an expert script processor specializing in TTS optimization and duration control.

ORIGINAL SCRIPT:
{script_content}

TARGET LANGUAGE: {language_value}
TARGET DURATION: {target_duration} seconds (STRICT LIMIT - DO NOT EXCEED!)

TASK: Optimize this script to FIT EXACTLY {target_duration} seconds - no more, no less.

REQUIREMENTS:
1. DURATION CONTROL: Target is EXACTLY {target_duration}s - aim for {int(target_duration * 2.3)} to {int(target_duration * 2.5)} words MAXIMUM
2. TTS OPTIMIZATION: Use clear, pronounceable words
3. NATURAL FLOW: Maintain conversational tone
4. SEGMENT BREAKDOWN: Split into segments of EXACTLY 1 SENTENCE per segment - NEVER combine sentences
5. TIMING CALCULATION: Estimate speaking time (average 2.3-2.5 words per second for natural pace)
6. CONTRACTION AVOIDANCE: NEVER use contractions - always write full forms (use "do not" instead of "don't", "it is" instead of "it's", "let us" instead of "let's", etc.)
7. SENTENCE INTEGRITY: Each segment must contain exactly ONE complete sentence with proper punctuation
8. SUBTITLE CONSTRAINTS: Each segment MUST be exactly 1 sentence for proper subtitle display
9. SENTENCE LENGTH: Each sentence should be ~10-20 words for optimal subtitle readability
10. CRITICAL RULE: NEVER put two sentences in one segment - always split them into separate segments

CRITICAL TTS RULES:
- Replace ALL contractions with their full expanded forms
- Use "is not" instead of "isn't" 
- Use "do not" instead of "don't"
- Use "let us" instead of "let's"
- Use "it is" instead of "it's"
- Use "we are" instead of "we're"
- Use "they are" instead of "they're"
- Use "will not" instead of "won't"
- Use "cannot" instead of "can't"
- This prevents TTS from pronouncing contractions as separate letters (like "I S N T")

DURATION CALCULATION AND STRATEGY:
- PRIORITY: Create scripts that fit EXACTLY within the duration - NOT MORE!
- Average speaking speed: 2.3-2.5 words per second (comfortable pace)
- TARGET word count for {target_duration}s: {int(target_duration * 2.3)} to {int(target_duration * 2.5)} words MAXIMUM
- DO NOT EXCEED this word count!
- IMPORTANT: Account for contraction expansion when calculating word count (e.g., "don't" becomes "do not" = 2 words)
- STRATEGY: Be concise and impactful - quality over quantity
- Remove any filler or redundant content
- Use active voice and direct statements
- Each sentence should deliver value
- NEVER pad content just to fill time

Please return a JSON response with the following structure:
{{
    "optimized_script": "The optimized script text (exactly the right length for {target_duration}s)",
    "segments": [
        {{
            "text": "First segment text",
            "duration": estimated_seconds,
            "word_count": number_of_words,
            "voice_suggestion": "storyteller/narrator/enthusiastic/calm"
        }}
    ],
    "total_estimated_duration": total_seconds,
    "total_word_count": total_words,
    "optimization_notes": "Brief notes about changes made",
    "duration_match": "perfect/close/adjusted",
    "tts_optimizations": ["List of TTS-specific improvements made"]
}}

CRITICAL: If target duration is {target_duration}s, ensure total_estimated_duration is within ±2 seconds of this target.
"""

            # Use the AI service manager to generate content
            text_service = self.ai_manager.get_text_service()
            request = TextGenerationRequest(
                prompt=processing_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            response = await text_service.generate(request)
            
            # Parse AI response
            response_text = response.text.strip()
            
            try:
                # Use the centralized JSON fixer to handle all parsing issues
                expected_structure = {
                    "optimized_script": str,
                    "segments": list,
                    "total_estimated_duration": float,
                    "total_word_count": int,
                    "optimization_notes": str,
                    "duration_match": str,
                    "tts_optimizations": list
                }
                
                result = self.json_fixer.fix_json(response_text, expected_structure)
                
                if not result:
                    raise ValueError("JSON fixer returned None")
                
                # Validate duration matching if target was specified
                if target_duration:
                    estimated_duration = result.get('total_estimated_duration', 0)
                    duration_diff = abs(estimated_duration - target_duration)
                    
                    if duration_diff > 5:  # More than 5 seconds off
                        logger.warning(f"⚠️ Duration mismatch: {estimated_duration}s vs target {target_duration}s")
                        # Trigger re-processing with stricter constraints
                        result = self._reprocess_for_duration(script_content, target_duration, language)
                    else:
                        logger.info(f"✅ Duration match: {estimated_duration}s (target: {target_duration}s)")
                
                # Add metadata
                result['language'] = language_value
                result['processing_timestamp'] = datetime.now().isoformat()
                result['target_duration'] = target_duration
                
                # Ensure final_script key exists for compatibility
                if 'optimized_script' in result and 'final_script' not in result:
                    result['final_script'] = result['optimized_script']
                
                logger.info(f"✅ AI enhanced script: {result.get('total_word_count', 0)} words")
                return result
                
            except Exception as json_error:
                logger.error(f"JSON fixing failed: {json_error}")
                logger.error(f"Raw response preview: {response_text[:500]}...")
                # Fall back to creating a basic result
                return self._create_fallback_result(script_content, language, target_duration)
                
        except Exception as e:
            logger.error(f"Script processing failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Script content preview: {script_content[:100]}...")
            
            # Log specific error types
            if "API" in str(e) or "api" in str(e):
                logger.error("🔑 Possible API key or authentication issue")
            elif "Network" in str(e) or "connection" in str(e).lower():
                logger.error("🌐 Network connection issue")
            elif "rate" in str(e).lower() or "quota" in str(e).lower():
                logger.error("⏱️ Rate limiting or quota exceeded")
            else:
                logger.error(f"❌ Unknown error - check logs for details")
                
            return self._create_fallback_result(script_content, language, target_duration)


    def _reprocess_for_duration(self, script_content: str, target_duration: float, language) -> Dict[str, Any]:
        """Re-process script with stricter duration constraints"""
        try:
            # Handle both string and enum inputs for language
            if isinstance(language, str):
                language_value = language
            else:
                # Assume it's already an enum
                language_value = language.value if hasattr(language, 'value') else str(language)
                
            target_words = int(target_duration * 2.5)  # 2.5 words per second (matching prompt)
            
            # Simple word-based trimming/expansion
            words = script_content.split()
            
            if len(words) > target_words * 1.2:
                # Only trim if script is significantly over (20% longer than target)
                # Find a natural breakpoint (sentence ending) near the target
                sentences = script_content.split('. ')
                optimized_sentences = []
                current_words = 0
                
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if current_words + sentence_words <= target_words * 1.1:  # Allow 10% overage
                        optimized_sentences.append(sentence)
                        current_words += sentence_words
                    else:
                        break
                
                optimized_text = '. '.join(optimized_sentences)
                if not optimized_text.endswith('.'):
                    optimized_text += '.'
                logger.info(f"📏 Trimmed script to complete sentences: {len(words)} → {len(optimized_text.split())} words")
            elif len(words) < target_words * 0.6:
                # Only expand if script is significantly short (less than 60% of target)
                optimized_text = script_content + " " + script_content[:target_words - len(words)]
                logger.info(f"📏 Expanded script to reach target word count")
            else:
                # Keep original script - prioritize content completeness over exact timing
                optimized_text = script_content
                logger.info(f"📏 Keeping original script: {len(words)} words (target: {target_words})")
            
            # Create segments - ENFORCE ONE SENTENCE PER SEGMENT
            sentences = self._split_into_sentences(optimized_text, language)
            segments = []
            
            for sentence in sentences:
                sentence_words = len(sentence.split())
                sentence_duration = sentence_words / 2.5  # 2.5 words per second
                
                segments.append({
                    "text": sentence,
                    "duration": sentence_duration,
                    "word_count": sentence_words,
                    "voice_suggestion": "storyteller"
                })
            
            return {
                "optimized_script": optimized_text,
                "segments": segments,
                "total_estimated_duration": sum(seg['duration'] for seg in segments),
                "total_word_count": len(optimized_text.split()),
                "optimization_notes": f"Reprocessed for exact {target_duration}s duration",
                "duration_match": "adjusted",
                "tts_optimizations": ["Duration-based word count adjustment"],
                "language": language_value,
                "processing_timestamp": datetime.now().isoformat(),
                "target_duration": target_duration
            }
            
        except Exception as e:
            logger.error(f"Script reprocessing failed: {e}")
            return self._create_fallback_result(script_content, language, target_duration)
    
    def _manual_parse_response(self, response_text: str, script_content: str, language, target_duration: float = None) -> Dict[str, Any]:
        """Manually parse response when JSON parsing fails"""
        try:
            # Handle both string and enum inputs for language
            if isinstance(language, str):
                language_value = language
            else:
                language_value = language.value if hasattr(language, 'value') else str(language)
            
            # Try to extract key fields using regex
            import re
            
            # Extract optimized_script
            # First try standard pattern with colon
            script_match = re.search(r'"optimized_script":\s*"([^"]*)"', response_text)
            if script_match:
                optimized_script = script_match.group(1)
            else:
                # Try pattern without colon (malformed JSON)
                script_match = re.search(r'"optimized_script""\s*([^"]*)"', response_text)
                if script_match:
                    optimized_script = script_match.group(1)
                else:
                    # Try multiline pattern
                    script_match = re.search(r'"optimized_script":\s*"([^"]*(?:\\.[^"]*)*)"', response_text, re.DOTALL)
                    if script_match:
                        optimized_script = script_match.group(1).replace('\\"', '"')
                    else:
                        # Final fallback - just use the original script
                        optimized_script = script_content
            
            # Calculate basic metrics
            words = optimized_script.split()
            word_count = len(words)
            estimated_duration = word_count / 2.5  # 2.5 words per second (matching prompt)
            
            # If target duration specified, trim to fit
            if target_duration and estimated_duration > target_duration:
                target_words = int(target_duration * 3)
                optimized_script = ' '.join(words[:target_words])
                word_count = target_words
                estimated_duration = target_duration
            
            # Split into sentences for segments
            sentences = self._split_into_sentences(optimized_script, language)
            segments = []
            total_words = 0
            
            for sentence in sentences:
                sentence_words = len(sentence.split())
                sentence_duration = sentence_words / 2.5
                segments.append({
                    "text": sentence,
                    "duration": sentence_duration,
                    "word_count": sentence_words,
                    "voice_suggestion": "storyteller"
                })
                total_words += sentence_words
            
            # If no valid sentences, create single segment
            if not segments:
                segments = [{
                    "text": optimized_script,
                    "duration": estimated_duration,
                    "word_count": word_count,
                    "voice_suggestion": "storyteller"
                }]
                total_words = word_count
            
            return {
                "optimized_script": optimized_script,
                "final_script": optimized_script,
                "segments": segments,
                "total_estimated_duration": sum(seg['duration'] for seg in segments),
                "total_word_count": total_words,
                "optimization_notes": "Manual parsing with single-sentence segments",
                "duration_match": "manual",
                "tts_optimizations": ["Manual parsing recovery", "Single sentence per segment enforced"],
                "language": language_value,
                "processing_timestamp": datetime.now().isoformat(),
                "target_duration": target_duration
            }
            
        except Exception as e:
            logger.error(f"Manual parsing failed: {e}")
            return None

    def _split_into_sentences(self, text: str, language=None) -> List[str]:
        """Split text into individual sentences
        
        Args:
            text: Text to split
            language: Optional language parameter (not used currently)
            
        Returns:
            List of sentences
        """
        import re
        # Split on sentence endings including colons and semicolons
        sentences = re.split(r'([.!?:;]+)', text)
        
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
        
        # Filter out empty sentences
        return [s for s in complete_sentences if s.strip()]

    def _create_fallback_result(self, script_content: str, language, target_duration: float = None) -> Dict[str, Any]:
        """Create fallback result when AI processing fails"""
        
        # Check for truncated text and warn
        if "..." in script_content and len(script_content.split("...")) > 3:
            logger.warning("⚠️ Script appears to be truncated with multiple '...' - this may cause issues")
            logger.warning(f"⚠️ Script preview: {script_content[:200]}")
        
        # Handle both string and enum inputs for language
        if isinstance(language, str):
            language_value = language
        else:
            # Assume it's already an enum
            language_value = language.value if hasattr(language, 'value') else str(language)
            
        # Split into sentences - ENFORCE ONE SENTENCE PER SEGMENT
        sentences = self._split_into_sentences(script_content, language)
        
        # Create segments with exactly one sentence each
        segments = []
        total_words = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            sentence_duration = sentence_words / 2.5  # 2.5 words per second
            
            segments.append({
                "text": sentence,
                "duration": sentence_duration,
                "word_count": sentence_words,
                "voice_suggestion": "storyteller"
            })
            total_words += sentence_words
        
        total_duration = sum(seg['duration'] for seg in segments)
        
        # If no valid sentences, create single segment
        if not segments:
            words = script_content.split()
            word_count = len(words)
            estimated_duration = word_count / 2.5
            segments = [{
                "text": script_content,
                "duration": estimated_duration,
                "word_count": word_count,
                "voice_suggestion": "storyteller"
            }]
            total_words = word_count
            total_duration = estimated_duration
        
        return {
            "optimized_script": script_content,
            "final_script": script_content,  # Add this key for compatibility
            "segments": segments,
            "total_estimated_duration": total_duration,
            "total_word_count": total_words,
            "optimization_notes": "Fallback processing with single-sentence segments",
            "duration_match": "fallback",
            "tts_optimizations": ["Single sentence per segment enforced"],
            "language": language_value,
            "processing_timestamp": datetime.now().isoformat(),
            "target_duration": target_duration
        }

    def _apply_language_formatting(
            self,
            script: str,
            language: Language) -> str:
        """Apply language-specific formatting rules"""

        formatted_script = script
        language_rules = self.language_rules.get(
            language, self.language_rules[Language.ENGLISH_US])

        # Remove problematic patterns
        for pattern in language_rules["avoid_patterns"]:
            formatted_script = formatted_script.replace(pattern, "")

        # Ensure proper spacing after punctuation
        for punct in language_rules["preferred_punctuation"]:
            # Fix spacing after punctuation
            formatted_script = re.sub(
                f'\\{punct}(?!\\s)', f'{punct} ', formatted_script)
            # Remove multiple spaces
            formatted_script = re.sub(
                f'\\{punct}\\s+', f'{punct} ', formatted_script)

        # Language-specific formatting
        if language in [Language.HEBREW, Language.ARABIC]:
            # RTL languages - remove parentheses and brackets that confuse TTS
            formatted_script = re.sub(r'[()[\]{}]', '', formatted_script)
            # Ensure proper spacing
            formatted_script = re.sub(r'\s+', ' ', formatted_script)

        return formatted_script.strip()

    def _optimize_for_tts(self, script: str, language: Language) -> str:
        """Optimize script structure for TTS delivery"""

        language_rules = self.language_rules.get(
            language, self.language_rules[Language.ENGLISH_US])
        max_length = language_rules["max_sentence_length"]

        # Split into sentences
        sentences = self._split_into_sentences(script, language)

        optimized_sentences = []

        for sentence in sentences:
            words = sentence.strip().split()

            if len(words) <= max_length:
                # Sentence is good as-is, just ensure proper punctuation
                optimized_sentence = self._ensure_sentence_punctuation(
                    sentence, language)
                optimized_sentences.append(optimized_sentence)
            else:
                # Split long sentence into shorter ones
                split_sentences = self._split_long_sentence(
                    sentence, max_length, language)
                optimized_sentences.extend(split_sentences)

        # Join with proper spacing
        optimized_script = " ".join(optimized_sentences)

        # Final cleanup
        optimized_script = self._final_cleanup(optimized_script, language)

        return optimized_script

    def _split_into_sentences(
            self,
            text: str,
            language: Language) -> List[str]:
        """Split text into sentences based on language rules"""

        language_rules = self.language_rules.get(
            language, self.language_rules[Language.ENGLISH_US])
        endings = language_rules["sentence_endings"]

        # Create pattern for sentence endings
        endings_pattern = "|".join(re.escape(ending) for ending in endings)

        # Split on sentence endings followed by space or end of string
        sentences = re.split(f'({endings_pattern})\\s*', text)

        # Reconstruct sentences with their endings
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
                if sentence.strip():
                    result.append(sentence.strip())

        # Handle last sentence if it doesn't end with punctuation'
        if sentences and sentences[-1].strip():
            result.append(sentences[-1].strip())

        return result

    def _split_long_sentence(
            self,
            sentence: str,
            max_length: int,
            language: Language) -> List[str]:
        """Split a long sentence into shorter TTS-friendly sentences"""

        words = sentence.strip().split()

        if len(words) <= max_length:
            return [self._ensure_sentence_punctuation(sentence, language)]

        result = []
        current_sentence = []

        # Split at natural break points (commas, conjunctions, etc.)
        break_words = [
            "and",
            "but",
            "or",
            "so",
            "because",
            "when",
            "while",
            "i",
            "although"]

        for word in words:
            current_sentence.append(word)

            # Check if we should break here
            should_break = (
                len(current_sentence) >= max_length or(len(current_sentence) >= max_length // 2 and
                 (word.endswith(',') or word.lower() in break_words))
            )

            if should_break:
                sentence_text = " ".join(current_sentence)
                sentence_text = self._ensure_sentence_punctuation(
                    sentence_text, language)
                result.append(sentence_text)
                current_sentence = []

        # Add remaining words
        if current_sentence:
            sentence_text = " ".join(current_sentence)
            sentence_text = self._ensure_sentence_punctuation(
                sentence_text, language)
            result.append(sentence_text)

        return result

    def _ensure_sentence_punctuation(
            self,
            sentence: str,
            language: Language) -> str:
        """Ensure sentence has proper ending punctuation"""

        language_rules = self.language_rules.get(
            language, self.language_rules[Language.ENGLISH_US])
        endings = language_rules["sentence_endings"]

        sentence = sentence.strip()

        # Check if sentence already ends with proper punctuation
        if any(sentence.endswith(ending) for ending in endings):
            return sentence

        # Add appropriate punctuation
        if "?" in sentence or sentence.lower().startswith(
                ("what", "who", "when", "where", "why", "how")):
            return sentence + "?"
        elif "!" in sentence or any(
            word in sentence.lower() for word in ["amazing",
            "wow",
            "incredible",
            "awesome"]):
            return sentence + "!"
        else:
            return sentence + "."

    def _final_cleanup(self, script: str, language: Language) -> str:
        """Final cleanup and optimization"""

        # Remove multiple spaces
        script = re.sub(r'\s+', ' ', script)

        # Ensure proper spacing after punctuation
        script = re.sub(r'([.!?])([^\s])', r'\1 \2', script)
        script = re.sub(r'([,;:])([^\s])', r'\1 \2', script)

        # Remove leading/trailing whitespace
        script = script.strip()

        # Language-specific final cleanup
        if language in [Language.HEBREW, Language.ARABIC]:
            # Remove any remaining problematic characters for RTL TTS
            script = re.sub(r'["""''`]', '', script)

        return script

    def _basic_cleanup(self, script: str, language: Language) -> str:
        """Basic cleanup when AI processing fails"""

        # Remove multiple spaces
        script = re.sub(r'\s+', ' ', script)

        # Ensure sentences end with punctuation
        sentences = script.split('.')
        cleaned_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            if sentence:
                cleaned_sentences.append(sentence)

        return ' '.join(cleaned_sentences)

    def _validate_script(self, script: str, language: Language,
                         target_duration: int) -> Dict[str, Any]:
        """Validate script for TTS readiness"""

        issues = []

        # Check sentence lengths
        sentences = self._split_into_sentences(script, language)
        language_rules = self.language_rules.get(
            language, self.language_rules[Language.ENGLISH_US])
        max_length = language_rules["max_sentence_length"]

        long_sentences = [s for s in sentences if len(s.split()) > max_length * 1.5]  # More lenient
        if len(long_sentences) > len(sentences) * 0.3:  # Only flag if more than 30% are too long
            issues.append(
                f"Found {len(long_sentences)} sentences significantly longer than {max_length} words")

        # Check punctuation - more lenient
        has_punctuation = any(script.endswith(ending)
                   for ending in language_rules["sentence_endings"])
        has_internal_punctuation = any(
            punct in script for punct in ['.',
            '!',
            '?',
            ','
            ])

        if not has_punctuation and not has_internal_punctuation:
            issues.append("Script lacks proper punctuation")

        # Check duration estimate - more lenient
        estimated_duration = self._estimate_duration(script, language)
        duration_diff = abs(estimated_duration - target_duration)

        if duration_diff > target_duration * 0.5:  # More lenient: 50% difference
            issues.append(
                f"Duration estimate ({estimated_duration}s) differs significantly from target ({target_duration}s)")

        # Script is valid if it has basic punctuation and reasonable length
        is_valid = (has_punctuation or has_internal_punctuation) and \
                len(script.strip()) > 10

        return {
            "is_valid": is_valid,
            "issues": issues,
            "estimated_duration": estimated_duration,
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / \
            len(sentences) if sentences else 0}

    def _estimate_duration(self, script: str, language: Language) -> float:
        """Estimate TTS duration for script"""

        word_count = len(script.split())

        # Words per minute by language (approximate)
        wpm_rates = {
            Language.ENGLISH_US: 150,
            Language.HEBREW: 120,  # Hebrew tends to be slower
            Language.ARABIC: 120,
            Language.FRENCH: 140,
            Language.SPANISH: 145,
            Language.GERMAN: 130   # German compound words
        }

        wpm = wpm_rates.get(language, 140)
        estimated_minutes = word_count / wpm
        estimated_seconds = estimated_minutes * 60

        return estimated_seconds

    def ensure_complete_sentences(
        self,
        text: str,
        max_duration: float,
        speech_rate: float = 2.2) -> str:
        """Ensure script fits within duration without cutting sentences"""

        logger.info(f"📝 Ensuring complete sentences within {max_duration:.1f}s duration")

        try:
            import re

            # Clean the text
            clean_text = text.strip()

            # Split into sentences using proper sentence boundaries
            sentence_endings = r'[.!?]+(?:\s|$)'
            sentences = re.split(sentence_endings, clean_text)
            sentences = [s.strip() for s in sentences if s.strip()]

            # Calculate words and timing
            total_words = sum(len(sentence.split()) for sentence in sentences)
            estimated_duration = total_words / speech_rate

            logger.info(
                f"📊 Original: {len(sentences)} sentences,"
                f"{total_words} words, "
                f"{estimated_duration:.1f}s estimated")

            # If it fits, return as-is
            if estimated_duration <= max_duration:
                logger.info("✅ Script fits within duration perfectly")
                return clean_text

            # If too long, trim sentences from the end (never cut mid-sentence)
            target_words = int(max_duration * speech_rate)

            logger.info(f"🎯 Target: {target_words} words for {max_duration:.1f}s duration")

            # Build script up to target word count
            selected_sentences = []
            current_word_count = 0

            for sentence in sentences:
                sentence_words = len(sentence.split())

                # Check if adding this sentence would exceed target
                if current_word_count + sentence_words > target_words:
                    # If we haven't selected any sentences yet, include this one anyway'
                    # to avoid empty script
                    if not selected_sentences:
                        selected_sentences.append(sentence)
                        current_word_count += sentence_words
                        logger.info("⚠️ Including oversized sentence to avoid empty script")
                    break

                selected_sentences.append(sentence)
                current_word_count += sentence_words

                logger.info(f"✅ Added sentence: {sentence_words} words (total: {current_word_count}")

            # Reconstruct the script with proper sentence endings
            if selected_sentences:
                final_script = '. '.join(selected_sentences)
                if not final_script.endswith(('.', '!', '?')):
                    final_script += '.'

                final_words = len(final_script.split())
                final_duration = final_words / speech_rate

                logger.info(
                    f"✅ Final script: {len(selected_sentences)} sentences,"
                    f"{final_words} words, "
                    f"{final_duration:.1f}s")

                return final_script
            else:
                logger.warning("⚠️ No sentences selected, returning original text")
                return clean_text

        except Exception as e:
            logger.error(f"❌ Sentence completion failed: {e}")
            return text

    def validate_script_timing(self, script: str, target_duration: float,
                             tolerance: float = 5.0) -> Dict[str, Any]:
        """Validate that script timing matches target duration within tolerance"""

        try:
            words = len(script.split())

            # Calculate timing with different speech rates
            speech_rates = {
                'slow': 2.0,     # Slow, clear speech
                'normal': 2.5,   # Normal conversational pace (matching prompt)
                'fast': 3.0      # Fast, energetic pace
            }

            timing_analysis = {}

            for rate_name, rate_value in speech_rates.items():
                duration = words / rate_value
                within_tolerance = abs(duration - target_duration) <= tolerance

                timing_analysis[rate_name] = {
                    'duration': duration,
                    'within_tolerance': within_tolerance,
                    'difference': duration - target_duration
                }

            # Find the best matching rate
            best_rate = min(timing_analysis.items(),
                          key=lambda x: abs(x[1]['difference']))

            logger.info("📊 Script timing analysis:")
            logger.info(f"   Words: {words}")
            logger.info(f"   Target duration: {target_duration:.1f}s")
            logger.info(f"   Best rate: {best_rate[0]} ({speech_rates[best_rate[0]]:.1f} words/sec)")
            logger.info(f"   Estimated duration: {best_rate[1]['duration']:.1f}s")
            logger.info(f"   Within tolerance: {best_rate[1]['within_tolerance']}")

            return {
                'words': words,
                'target_duration': target_duration,
                'timing_analysis': timing_analysis,
                'best_rate': best_rate[0],
                'recommended_speech_rate': speech_rates[best_rate[0]],
                'estimated_duration': best_rate[1]['duration'],
                'within_tolerance': best_rate[1]['within_tolerance'],
                'needs_adjustment': not best_rate[1]['within_tolerance']
            }

        except Exception as e:
            logger.error(f"❌ Script timing validation failed: {e}")
            return {
                'words': 0,
                'target_duration': target_duration,
                'needs_adjustment': True,
                'error': str(e)
            }
