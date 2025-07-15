"""
Enhanced Script Processor
Ensures proper punctuation, short sentences, and TTS-optimized formatting
"""
import re
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import json
from datetime import datetime

from ..utils.logging_config import get_logger
from ..models.video_models import Language, Platform, VideoCategory

logger = get_logger(__name__)

class EnhancedScriptProcessor:
    """Processes scripts for optimal TTS delivery with proper punctuation and structure"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be None or empty")
        
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

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

    def process_script_for_tts(self, script_content: str, language,
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
TARGET DURATION: {target_duration} seconds (if specified)

TASK: Optimize this script for Text-to-Speech generation with perfect duration control.

REQUIREMENTS:
1. DURATION CONTROL: If target duration is specified ({target_duration}s), ensure the script can be spoken in exactly that time
2. TTS OPTIMIZATION: Use clear, pronounceable words
3. NATURAL FLOW: Maintain conversational tone
4. SEGMENT BREAKDOWN: Split into logical segments for multi-voice generation
5. TIMING CALCULATION: Estimate speaking time (average 3 words per second)

DURATION CALCULATION:
- Average speaking speed: 3 words per second
- Target words for {target_duration}s: {int(target_duration * 3) if target_duration else 'Not specified'}
- Adjust content to fit this word count precisely

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

            response = self.model.generate_content(processing_prompt)
            
            # Parse AI response
            response_text = response.text.strip()
            
            # Clean response and extract JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            try:
                result = json.loads(response_text)
                
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
                
                logger.info(f"✅ AI enhanced script: {result.get('total_word_count', 0)} words")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response: {e}")
                return self._create_fallback_result(script_content, language, target_duration)
                
        except Exception as e:
            logger.error(f"Script processing failed: {e}")
            return self._create_fallback_result(script_content, language, target_duration)

    def _reprocess_for_duration(self, script_content: str, target_duration: float, language: Language) -> Dict[str, Any]:
        """Re-process script with stricter duration constraints"""
        try:
            target_words = int(target_duration * 3)  # 3 words per second
            
            # Simple word-based trimming/expansion
            words = script_content.split()
            
            if len(words) > target_words:
                # Trim to target word count
                optimized_text = ' '.join(words[:target_words])
                logger.info(f"📏 Trimmed script from {len(words)} to {target_words} words")
            elif len(words) < target_words * 0.8:
                # Expand if significantly short (less than 80% of target)
                optimized_text = script_content + " " + script_content[:target_words - len(words)]
                logger.info(f"📏 Expanded script to reach target word count")
            else:
                optimized_text = script_content
            
            # Create segments
            segment_count = max(1, min(4, target_duration // 3))  # 1-4 segments based on duration
            words_per_segment = len(optimized_text.split()) // segment_count
            
            segments = []
            words = optimized_text.split()
            
            for i in range(segment_count):
                start_idx = i * words_per_segment
                end_idx = (i + 1) * words_per_segment if i < segment_count - 1 else len(words)
                
                segment_text = ' '.join(words[start_idx:end_idx])
                segment_duration = len(segment_text.split()) / 3.0  # 3 words per second
                
                segments.append({
                    "text": segment_text,
                    "duration": segment_duration,
                    "word_count": len(segment_text.split()),
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

    def _create_fallback_result(self, script_content: str, language: Language, target_duration: float = None) -> Dict[str, Any]:
        """Create fallback result when AI processing fails"""
        words = script_content.split()
        word_count = len(words)
        estimated_duration = word_count / 3.0  # 3 words per second
        
        # If target duration specified, trim to fit
        if target_duration and estimated_duration > target_duration:
            target_words = int(target_duration * 3)
            script_content = ' '.join(words[:target_words])
            word_count = target_words
            estimated_duration = target_duration
        
        return {
            "optimized_script": script_content,
            "segments": [{
                "text": script_content,
                "duration": estimated_duration,
                "word_count": word_count,
                "voice_suggestion": "storyteller"
            }],
            "total_estimated_duration": estimated_duration,
            "total_word_count": word_count,
            "optimization_notes": "Fallback processing applied",
            "duration_match": "fallback",
            "tts_optimizations": ["Basic fallback processing"],
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
        sentences = re.split(f'(endings_pattern)\\s*', text)

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
                'slow': 1.8,     # Slow, clear speech
                'normal': 2.2,   # Normal conversational pace
                'fast': 2.6      # Fast, energetic pace
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
