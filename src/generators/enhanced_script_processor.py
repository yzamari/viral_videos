"""
Enhanced Script Processor
Ensures proper punctuation, short sentences, and TTS-optimized formatting
"""
import re
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from ..utils.logging_config import get_logger
from ..models.video_models import Language, Platform, VideoCategory

logger = get_logger(__name__)


class EnhancedScriptProcessor:
    """Processes scripts for optimal TTS delivery with proper punctuation and structure"""

    def __init__(self, api_key: str):
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

    def process_script_for_tts(self,
                               script: str,
                               language: Language,
                               target_duration: int,
                               platform: Platform,
                               category: VideoCategory) -> Dict[str, Any]:
        """Process script for optimal TTS delivery"""

        logger.info(
            f"📝 Processing script for TTS optimization ({
                language.value})")

        try:
            # Step 1: AI-enhanced script improvement
            enhanced_script = self._ai_enhance_script(
                script, language, target_duration, platform, category)

            # Step 2: Apply language-specific formatting
            formatted_script = self._apply_language_formatting(
                enhanced_script, language)

            # Step 3: Optimize punctuation and sentence structure
            optimized_script = self._optimize_for_tts(
                formatted_script, language)

            # Step 4: Validate and measure
            validation_results = self._validate_script(
                optimized_script, language, target_duration)

            return {
                "original_script": script,
                "enhanced_script": enhanced_script,
                "formatted_script": formatted_script,
                "final_script": optimized_script,
                "validation": validation_results,
                "word_count": len(
                    optimized_script.split()),
                "sentence_count": len(
                    self._split_into_sentences(
                        optimized_script,
                        language)),
                "estimated_duration": self._estimate_duration(
                    optimized_script,
                    language),
                "tts_ready": validation_results["is_valid"]}

        except Exception as e:
            logger.error(f"❌ Script processing failed: {e}")
            # Return basic processed version
            return {
                "original_script": script,
                "final_script": self._basic_cleanup(script, language),
                "validation": {"is_valid": True, "issues": []},
                "word_count": len(script.split()),
                "tts_ready": True
            }

    def _ai_enhance_script(
            self,
            script: str,
            language: Language,
            target_duration: int,
            platform: Platform,
            category: VideoCategory) -> str:
        """Use AI to enhance script for better TTS delivery"""

        try:
            language_rules = self.language_rules.get(
                language, self.language_rules[Language.ENGLISH_US])
            max_sentence_length = language_rules["max_sentence_length"]

            enhancement_prompt = f"""
            You are a professional script writer specializing in TTS-optimized content for {platform.value} videos.

            TASK: Enhance this script for optimal Text-to-Speech delivery in {language.value}

            ORIGINAL SCRIPT:
            {script}

            TARGET SPECIFICATIONS:
            - Language: {language.value}
            - Platform: {platform.value}
            - Category: {category.value}
            - Target Duration: {target_duration} seconds
            - Max words per sentence: {max_sentence_length}

            TTS OPTIMIZATION REQUIREMENTS:
            1. SHORT SENTENCES: Maximum {max_sentence_length} words per sentence
            2. CLEAR PUNCTUATION: Use proper punctuation marks for natural pauses
            3. NATURAL FLOW: Ensure smooth transitions between sentences
            4. PRONUNCIATION-FRIENDLY: Avoid complex words that TTS might mispronounce
            5. ENGAGING RHYTHM: Vary sentence lengths for dynamic delivery
            6. PLATFORM OPTIMIZATION: Match {platform.value} content style

            LANGUAGE-SPECIFIC RULES:
            {"- RTL LANGUAGE: Ensure proper word order and sentence structure" if language in [Language.HEBREW, Language.ARABIC] else ""}
            {"- Use native punctuation marks where appropriate" if language in [Language.ARABIC, Language.SPANISH] else ""}

            OUTPUT REQUIREMENTS:
            - Keep the same core message and content
            - Maintain engaging and viral-worthy tone
            - Ensure every sentence ends with proper punctuation
            - Add natural pauses with commas where needed
            - Make it sound conversational and natural when spoken

            Return ONLY the enhanced script text, nothing else.
            """

            response = self.model.generate_content(enhancement_prompt)
            enhanced_script = response.text.strip()

            logger.info(
                f"✅ AI enhanced script: {
                    len(enhanced_script)} characters")
            return enhanced_script

        except Exception as e:
            logger.error(f"❌ AI script enhancement failed: {e}")
            return script

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

        # Handle last sentence if it doesn't end with punctuation
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
            "if",
            "although"]

        for word in words:
            current_sentence.append(word)

            # Check if we should break here
            should_break = (
                len(current_sentence) >= max_length or
                (len(current_sentence) >= max_length // 2 and
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
        elif "!" in sentence or any(word in sentence.lower() for word in ["amazing", "wow", "incredible", "awesome"]):
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
                f"Found {
                    len(long_sentences)} sentences significantly longer than {max_length} words")

        # Check punctuation - more lenient
        has_punctuation = any(script.endswith(ending)
                   for ending in language_rules["sentence_endings"])
        has_internal_punctuation = any(punct in script for punct in ['.', '!', '?', ','])
        
        if not has_punctuation and not has_internal_punctuation:
            issues.append("Script lacks proper punctuation")

        # Check duration estimate - more lenient
        estimated_duration = self._estimate_duration(script, language)
        duration_diff = abs(estimated_duration - target_duration)

        if duration_diff > target_duration * 0.5:  # More lenient: 50% difference
            issues.append(
                f"Duration estimate ({estimated_duration}s) differs significantly from target ({target_duration}s)")

        # Script is valid if it has basic punctuation and reasonable length
        is_valid = (has_punctuation or has_internal_punctuation) and len(script.strip()) > 10

        return {
            "is_valid": is_valid,
            "issues": issues,
            "estimated_duration": estimated_duration,
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(
                len(
                    s.split()) for s in sentences) /
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

    def ensure_complete_sentences(self, text: str, max_duration: float, speech_rate: float = 2.2) -> str:
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
            
            logger.info(f"📊 Original: {len(sentences)} sentences, {total_words} words, {estimated_duration:.1f}s estimated")
            
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
                    # If we haven't selected any sentences yet, include this one anyway
                    # to avoid empty script
                    if not selected_sentences:
                        selected_sentences.append(sentence)
                        current_word_count += sentence_words
                        logger.info(f"⚠️ Including oversized sentence to avoid empty script")
                    break
                
                selected_sentences.append(sentence)
                current_word_count += sentence_words
                
                logger.info(f"✅ Added sentence: {sentence_words} words (total: {current_word_count})")
            
            # Reconstruct the script with proper sentence endings
            if selected_sentences:
                final_script = '. '.join(selected_sentences)
                if not final_script.endswith(('.', '!', '?')):
                    final_script += '.'
                
                final_words = len(final_script.split())
                final_duration = final_words / speech_rate
                
                logger.info(f"✅ Final script: {len(selected_sentences)} sentences, {final_words} words, {final_duration:.1f}s")
                
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
            
            logger.info(f"📊 Script timing analysis:")
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
