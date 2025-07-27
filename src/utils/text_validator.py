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
    
    def __init__(self):
        """Initialize text validator with patterns"""
        
        # Metadata patterns that should never appear in user-visible text
        self.metadata_patterns = [
            r'emotional_arc', r'surprise_moments', r'shareability_score',
            r'viral_elements', r'script_data', r'config\[', r'config\.',
            r'engagement_score', r'platform_optimization', r'trending_score',
            r'_id\s*:', r'created_at\s*:', r'updated_at\s*:',
            r'^\d+\s*,\s*[\'"]', r'}\s*}$', r'{\s*{',  # Dictionary patterns
            r'None\s*,', r'True\s*,', r'False\s*,',  # Python literals
            # Note: Removed 'visual' as it conflicts with instruction patterns
        ]
        
        # Instruction patterns (stage directions, camera instructions, etc.)
        self.instruction_patterns = [
            r'\([^)]*(?:visual|scene|audio|camera|shot|effect|zoom|fade|cut to|angle|transition|music)[^)]*\)',
            r'visual\s*:\s*[^.!?]*[.!?]?', r'scene\s*:\s*[^.!?]*[.!?]?', 
            r'cut to\s*:\s*[^.!?]*[.!?]?', r'fade\s*:\s*[^.!?]*[.!?]?', 
            r'zoom\s*:\s*[^.!?]*[.!?]?', r'camera\s*:\s*[^.!?]*[.!?]?', 
            r'angle\s*:\s*[^.!?]*[.!?]?', r'shot\s*:\s*[^.!?]*[.!?]?', 
            r'transition\s*:\s*[^.!?]*[.!?]?', r'effect\s*:\s*[^.!?]*[.!?]?',
            r'show\s*:\s*[^.!?]*[.!?]?', r'display\s*:\s*[^.!?]*[.!?]?', 
            r'pan to\s*:\s*[^.!?]*[.!?]?', r'focus on\s*:\s*[^.!?]*[.!?]?',
            r'this concludes', r'this ends', r'segment ends', r'scene ends',
            r'end of', r'conclusion of', r'wrapping up', r'to summarize',
        ]
        
        # RTL character ranges
        self.rtl_ranges = [
            (0x0590, 0x05FF),  # Hebrew
            (0x0600, 0x06FF),  # Arabic
            (0x0750, 0x077F),  # Arabic Supplement
            (0x08A0, 0x08FF),  # Arabic Extended-A
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        ]
        
        logger.info("✅ Text Validator initialized")
    
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
        """Detect if text is RTL and identify language"""
        
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
        """Remove metadata patterns from text"""
        
        cleaned = text
        issues = []
        
        # Check if text is RTL (Hebrew/Arabic) - be less aggressive
        is_rtl, _ = self._detect_language_and_rtl(text)
        
        # First check if the entire text looks like metadata
        # BUT be careful with RTL text which might have different patterns
        if not is_rtl and (re.match(r'^\d+\s*,\s*[\'\"]', cleaned) or cleaned.count(':') > 5):
            # This is likely corrupted metadata, not real text
            issues.append("Entire text appears to be metadata")
            return "", issues
        
        # Check each metadata pattern
        for pattern in self.metadata_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                issues.append(f"Found metadata pattern: {pattern}")
                cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove dictionary-like structures more aggressively
        if '{' in cleaned or '}' in cleaned:
            # Remove everything between braces and the braces themselves
            cleaned = re.sub(r'\{[^}]*\}', ' ', cleaned)
            # Also remove any remaining braces
            cleaned = cleaned.replace('{', ' ').replace('}', ' ')
            issues.append("Removed dictionary structures")
        
        # Remove key:value patterns more aggressively
        if ':' in cleaned:
            # Remove patterns like 'key': 'value' or key: value
            cleaned = re.sub(r"[\'\"]?\w+[\'\"]?\s*:\s*[\'\"]?[^,\'\"\s]+[\'\"]?", ' ', cleaned)
            # If still too many colons, it's probably all metadata
            if cleaned.count(':') > 1:
                cleaned = re.sub(r'\w+\s*:\s*[^,\s]+', ' ', cleaned)
                issues.append("Removed key:value patterns")
        
        # Remove quotes that might be from dict values
        cleaned = re.sub(r"[\'\"]\s*[:,]\s*[\'\"]", ' ', cleaned)
        
        # Clean up any resulting mess
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip(), issues
    
    def _remove_instructions(self, text: str) -> Tuple[str, List[str]]:
        """Remove instruction patterns from text"""
        
        cleaned = text
        issues = []
        
        # Remove parenthetical instructions first (most common)
        paren_pattern = r'\([^)]*\)'
        paren_matches = re.findall(paren_pattern, cleaned)
        for match in paren_matches:
            # Check if it contains instruction keywords
            if any(keyword in match.lower() for keyword in ['visual', 'scene', 'audio', 'camera', 'shot', 'effect', 'zoom', 'fade', 'cut to', 'angle', 'transition', 'music']):
                cleaned = cleaned.replace(match, ' ')
                issues.append(f"Removed parenthetical instruction: {match}")
        
        # Check each instruction pattern
        for pattern in self.instruction_patterns:
            matches = re.finditer(pattern, cleaned, re.IGNORECASE)
            for match in matches:
                issues.append(f"Found instruction: {match.group()[:30]}...")
                cleaned = cleaned[:match.start()] + ' ' + cleaned[match.end():]
        
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
        """Check if text still contains invalid patterns"""
        
        # Check if text is RTL to be less aggressive
        is_rtl, _ = self._detect_language_and_rtl(text)
        
        # Check for remaining metadata (less aggressive for RTL)
        for pattern in self.metadata_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for remaining instructions
        for pattern in self.instruction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for suspicious patterns (less aggressive for RTL text)
        if not is_rtl:
            if text.count('{') > 0 or text.count('}') > 0:
                return True
            if text.count(':') > 2:
                return True
            if re.search(r'^\d+\s*,', text):  # Starts with number and comma
                return True
        
        # Check if text is too short or contains only punctuation/quotes after cleaning
        # For RTL text, we need to handle Unicode properly
        if is_rtl:
            # Count actual Hebrew/Arabic characters
            rtl_chars = sum(1 for c in text if any(start <= ord(c) <= end for start, end in self.rtl_ranges))
            if rtl_chars < 2:  # Too few RTL characters
                return True
        else:
            cleaned_for_check = re.sub(r'[^\w\s]', '', text).strip()
            if len(cleaned_for_check) < 3:  # Too short to be meaningful
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