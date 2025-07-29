"""
Comprehensive Text Validation Pipeline
Ensures no metadata, instructions, or script descriptions appear in user-visible text
"""
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from ..utils.logging_config import get_logger
from ..models.video_models import Language
from ..config.video_config import video_config
from ..generators.ai_content_analyzer import AIContentAnalyzer

logger = get_logger(__name__)


@dataclass
class TextValidationResult:
    """Result of text validation"""
    original_text: str
    cleaned_text: str
    is_valid: bool
    issues_found: List[str]
    is_rtl: bool
    language_detected: Optional[Language]
    metadata_removed: bool
    instructions_removed: bool


class TextValidator:
    """Comprehensive text validation and cleaning"""
    
    def __init__(self, api_key: str = None):
        """Initialize text validator with AI capabilities"""
        
        # Initialize AI Content Analyzer for intelligent pattern detection
        try:
            self.ai_analyzer = AIContentAnalyzer(api_key or "dummy")
            self.use_ai = True
            logger.info("✅ Text Validator initialized with AI capabilities")
        except Exception as e:
            logger.warning(f"AI analyzer unavailable, using fallback patterns: {e}")
            self.ai_analyzer = None
            self.use_ai = False
        
        # Fallback patterns only used when AI is unavailable
        # These are minimal patterns for basic functionality
        self.fallback_metadata_patterns = [
            r'^\d+\s*,\s*[\'"]',  # Dictionary-like structures
            r'}\s*}$', r'{\s*{',   # Nested braces
            r'_id\s*:', r'created_at\s*:', r'updated_at\s*:',  # Database fields
        ]
        
        # Basic instruction patterns for fallback
        self.fallback_instruction_patterns = [
            r'\[VISUAL:[^\]]*\]',  # New tagging format
            r'^(Scene|Visual|SCENE|VISUAL):.*$',  # Scene markers
        ]
        
        # RTL character ranges (still needed for language detection)
        self.rtl_ranges = [
            (0x0590, 0x05FF),  # Hebrew
            (0x0600, 0x06FF),  # Arabic
            (0x0750, 0x077F),  # Arabic Supplement
            (0x08A0, 0x08FF),  # Arabic Extended-A
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        ]
    
    def validate_text(self, text: str, context: str = "general", 
                     expected_language: Optional[Language] = None) -> TextValidationResult:
        """Validate and clean text for user visibility"""
        
        if not text:
            return TextValidationResult(
                original_text="",
                cleaned_text="",
                is_valid=True,
                issues_found=[],
                is_rtl=False,
                language_detected=None,
                metadata_removed=False,
                instructions_removed=False
            )
        
        original_text = text
        cleaned_text = text
        issues_found = []
        metadata_removed = False
        instructions_removed = False
        
        # Step 1: Detect language and RTL
        is_rtl, detected_language = self._detect_language_and_rtl(text)
        
        # Step 2: Remove instructions FIRST (before metadata)
        cleaned_text, instruction_issues = self._remove_instructions(cleaned_text)
        if instruction_issues:
            issues_found.extend(instruction_issues)
            instructions_removed = True
            logger.debug(f"📝 Removed instructions from {context}: {instruction_issues}")
        
        # Step 3: Remove metadata SECOND
        cleaned_text, metadata_issues = self._remove_metadata(cleaned_text)
        if metadata_issues:
            issues_found.extend(metadata_issues)
            metadata_removed = True
            logger.debug(f"📝 Removed metadata from {context}: {metadata_issues}")
        
        # Step 4: Clean up text
        cleaned_text = self._clean_text(cleaned_text, is_rtl)
        
        # Step 5: Validate final text
        is_valid = len(cleaned_text.strip()) > 0 and not self._contains_invalid_patterns(cleaned_text)
        
        # If text became empty or invalid, use default
        if not is_valid or not cleaned_text.strip():
            if context == "cta":
                cleaned_text = video_config.get_default_cta('youtube')
            elif context == "hook":
                cleaned_text = video_config.get_default_hook('youtube')
            else:
                cleaned_text = "Content"
            issues_found.append(f"Text validation failed, using default: {cleaned_text}")
        
        return TextValidationResult(
            original_text=original_text,
            cleaned_text=cleaned_text,
            is_valid=is_valid,
            issues_found=issues_found,
            is_rtl=is_rtl,
            language_detected=detected_language,
            metadata_removed=metadata_removed,
            instructions_removed=instructions_removed
        )
    
    def _detect_language_and_rtl(self, text: str) -> Tuple[bool, Optional[Language]]:
        """Detect if text is RTL and identify language using AI or fallback"""
        
        # Try AI detection first if available
        if self.use_ai and self.ai_analyzer:
            try:
                lang_info = self.ai_analyzer.detect_language_intent(text)
                if lang_info:
                    is_rtl = lang_info.get('is_rtl', False)
                    language_code = lang_info.get('language_code', '').lower()
                    
                    # Map language codes to our Language enum
                    language_map = {
                        'he': Language.HEBREW,
                        'ar': Language.ARABIC,
                        'en': Language.ENGLISH_US,
                        'fr': Language.FRENCH,
                        'es': Language.SPANISH,
                        'de': Language.GERMAN,
                    }
                    
                    detected_language = language_map.get(language_code[:2])
                    return is_rtl, detected_language
            except Exception as e:
                logger.debug(f"AI language detection failed, using fallback: {e}")
        
        # Fallback to character-based detection
        # Count RTL characters
        rtl_count = 0
        for char in text:
            char_code = ord(char)
            for start, end in self.rtl_ranges:
                if start <= char_code <= end:
                    rtl_count += 1
                    break
        
        # If more than 30% of characters are RTL, consider it RTL text
        is_rtl = rtl_count > len(text) * 0.3
        
        # Detect specific language
        detected_language = None
        if is_rtl:
            # Hebrew detection
            hebrew_count = sum(1 for c in text if 0x0590 <= ord(c) <= 0x05FF)
            # Arabic detection
            arabic_count = sum(1 for c in text if 0x0600 <= ord(c) <= 0x06FF)
            
            if hebrew_count > arabic_count:
                detected_language = Language.HEBREW
            elif arabic_count > 0:
                detected_language = Language.ARABIC
            # Note: Persian uses Arabic script, so additional context needed
        
        return is_rtl, detected_language
    
    def _remove_metadata(self, text: str) -> Tuple[str, List[str]]:
        """Remove metadata patterns from text using AI or fallback patterns"""
        
        cleaned = text
        issues = []
        
        # Try AI-powered metadata detection first
        if self.use_ai and self.ai_analyzer:
            try:
                # Ask AI to identify and remove metadata
                prompt = f"""
                Analyze this text and identify ONLY genuine metadata, configuration values, or system-generated non-content elements.
                
                DO NOT REMOVE:
                - Brand names (like "Family Guy", "Instagram", "TikTok")
                - Character names or show references
                - Creative content descriptions
                - Story elements or narrative text
                
                ONLY REMOVE:
                - System timestamps
                - Configuration parameters
                - Debug information
                - Auto-generated IDs or codes
                - Technical metadata
                
                Text: "{text}"
                
                Return JSON:
                {{
                    "is_metadata": true/false,
                    "cleaned_text": "text with metadata removed",  
                    "metadata_found": ["list of ONLY genuine metadata elements"]
                }}
                """
                
                # Use the AI's text service directly for quick analysis
                from ..ai.interfaces.text_generation import TextGenerationRequest
                text_service = self.ai_analyzer.model
                if text_service:
                    response = text_service.generate_content(prompt)
                    result = self.ai_analyzer._extract_json(response.text)
                    
                    if result and result.get('is_metadata'):
                        cleaned = result.get('cleaned_text', '')
                        metadata_found = result.get('metadata_found', [])
                        for item in metadata_found:
                            issues.append(f"AI detected metadata: {item}")
                        return cleaned.strip(), issues
                    elif result:
                        cleaned = result.get('cleaned_text', text)
            except Exception as e:
                logger.debug(f"AI metadata detection failed, using fallback: {e}")
        
        # Fallback to basic pattern matching
        # Check if text is RTL (Hebrew/Arabic) - be less aggressive
        is_rtl, _ = self._detect_language_and_rtl(text)
        
        # First check if the entire text looks like metadata
        if not is_rtl and (re.match(r'^\d+\s*,\s*[\'\"]', cleaned) or cleaned.count(':') > 5):
            # This is likely corrupted metadata, not real text
            issues.append("Entire text appears to be metadata")
            return "", issues
        
        # Use minimal fallback patterns
        for pattern in self.fallback_metadata_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                issues.append(f"Found metadata pattern: {pattern}")
                cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove dictionary-like structures
        if '{' in cleaned or '}' in cleaned:
            cleaned = re.sub(r'\{[^}]*\}', ' ', cleaned)
            cleaned = cleaned.replace('{', ' ').replace('}', ' ')
            issues.append("Removed dictionary structures")
        
        # Clean up any resulting mess
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip(), issues
    
    def _remove_instructions(self, text: str) -> Tuple[str, List[str]]:
        """Remove instruction patterns from text using AI or fallback patterns"""
        
        cleaned = text
        issues = []
        
        # Skip ALL instruction removal if text appears to be already cleaned
        has_visual_markers = '[VISUAL:' in text or 'DIALOGUE:' in text or any(
            marker in text.lower() for marker in ['scene:', 'visual:', 'cut to:', 'fade:', '(', '[']
        )
        
        if not has_visual_markers:
            # Text is already clean, no instructions to remove
            logger.debug("Text appears to be already cleaned - skipping instruction removal")
            return cleaned, issues
        
        # Try AI-powered instruction detection first
        if self.use_ai and self.ai_analyzer:
            try:
                # Use AI to separate visual instructions from dialogue
                visual_analysis = self.ai_analyzer.analyze_visual_elements(text)
                
                if visual_analysis and 'dialogue' in visual_analysis:
                    dialogue_parts = visual_analysis['dialogue']
                    visual_parts = visual_analysis.get('visual', [])
                    
                    if dialogue_parts:
                        cleaned = ' '.join(dialogue_parts)
                        for visual in visual_parts[:3]:  # Show first 3 visual elements
                            issues.append(f"AI removed visual: {visual[:50]}...")
                        if len(visual_parts) > 3:
                            issues.append(f"And {len(visual_parts) - 3} more visual elements")
                        return cleaned.strip(), issues
            except Exception as e:
                logger.debug(f"AI instruction detection failed, using fallback: {e}")
        
        # Fallback to basic pattern matching
        # Check for new tagging format first
        if '[VISUAL:' in cleaned:
            cleaned = re.sub(r'\[VISUAL:[^\]]*\]', '', cleaned)
            issues.append("Removed [VISUAL:] tags")
        
        # Remove basic instruction patterns
        for pattern in self.fallback_instruction_patterns:
            matches = re.finditer(pattern, cleaned, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                issues.append(f"Found instruction: {match.group()[:30]}...")
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up any resulting double spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip(), issues
    
    def _clean_text(self, text: str, is_rtl: bool) -> str:
        """Clean up text formatting"""
        
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove leading/trailing punctuation
        cleaned = cleaned.strip('.,;:!?-_')
        
        # For RTL text, preserve RTL marks
        if is_rtl and not cleaned.startswith('\u200F'):
            cleaned = '\u200F' + cleaned
        
        return cleaned
    
    def _contains_invalid_patterns(self, text: str) -> bool:
        """Check if text still contains invalid patterns using AI or fallback"""
        
        # Try AI-powered validation first
        if self.use_ai and self.ai_analyzer:
            try:
                # Ask AI to validate the text
                prompt = f"""
                Analyze if this text contains any metadata, instructions, or invalid patterns:
                
                Text: "{text}"
                
                Return JSON:
                {{
                    "is_valid": true/false,
                    "invalid_patterns_found": ["list of issues found"],
                    "confidence": 0.0-1.0
                }}
                """
                
                # Use the AI's text service directly
                from ..ai.interfaces.text_generation import TextGenerationRequest
                text_service = self.ai_analyzer.model
                if text_service:
                    response = text_service.generate_content(prompt)
                    result = self.ai_analyzer._extract_json(response.text)
                    
                    if result and 'is_valid' in result:
                        # If AI is confident, use its judgment
                        if result.get('confidence', 0) > 0.7:
                            return not result['is_valid']
            except Exception as e:
                logger.debug(f"AI validation failed, using fallback: {e}")
        
        # Fallback to basic checks
        # Check if text is RTL to be less aggressive
        is_rtl, _ = self._detect_language_and_rtl(text)
        
        # Check for obvious invalid patterns
        if text.count('{') > 0 or text.count('}') > 0:
            return True
        
        # Check for metadata indicators
        if not is_rtl and text.count(':') > 3:
            return True
        
        # Check if text is too short
        if is_rtl:
            # Count actual RTL characters
            rtl_chars = sum(1 for c in text if any(start <= ord(c) <= end for start, end in self.rtl_ranges))
            if rtl_chars < 2:
                return True
        else:
            cleaned_for_check = re.sub(r'[^\w\s]', '', text).strip()
            if len(cleaned_for_check) < 3:
                return True
        
        return False
    
    def validate_script_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate all segments in a script"""
        
        validated_segments = []
        
        for i, segment in enumerate(segments):
            if 'text' in segment:
                validation = self.validate_text(
                    segment['text'], 
                    context=f"segment_{i}",
                    expected_language=segment.get('language')
                )
                
                if validation.cleaned_text != segment['text']:
                    logger.info(f"📝 Cleaned segment {i}: {segment['text'][:50]}... -> {validation.cleaned_text[:50]}...")
                
                segment['text'] = validation.cleaned_text
                segment['validation_result'] = validation
            
            validated_segments.append(segment)
        
        return validated_segments