"""
VEO3 Safety Validator and Prompt Simplifier
Validates and simplifies prompts before VEO3 submission to avoid safety blocks
"""
import re
import json
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from ..utils.logging_config import get_logger
except ImportError:
    from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class SafetyIssueType(Enum):
    """Types of safety issues that can trigger VEO3 blocks"""
    VIOLENCE = "violence"
    POLITICAL = "political"
    SENSITIVE_CONFLICT = "sensitive_conflict"
    EXCESSIVE_KEYWORDS = "excessive_keywords"
    PROMPT_TOO_LONG = "prompt_too_long"
    OVERLY_COMPLEX = "overly_complex"


@dataclass
class ValidationResult:
    """Result of prompt validation"""
    is_safe: bool
    issues: List[SafetyIssueType]
    suggestions: List[str]
    simplified_prompt: str
    original_length: int
    simplified_length: int


class VEO3SafetyValidator:
    """Validates and simplifies VEO3 prompts to avoid safety blocks"""
    
    # Sensitive terms that often trigger safety filters
    SENSITIVE_TERMS = [
        # Specific conflicts and dates
        r'october\s+7(?:th)?(?:\s+202[34])?',
        r'oct(?:ober)?\s+7',
        r'lebanon\s+war',
        r'iran\s+war',
        r'gaza',
        r'hamas',
        r'hezbollah',
        r'idf',
        r'israeli?\s+(?:soldier|military|army|veteran)',
        
        # Violence-related terms
        r'ptsd',
        r'trauma(?:tic)?',
        r'blood(?:y)?',
        r'explosion',
        r'bomb(?:ing)?',
        r'gunfire',
        r'weapon',
        r'combat',
        r'kill(?:ing)?',
        r'death',
        r'war\s+crime',
        r'massacre',
        r'terror(?:ist)?',
        
        # Political/sensitive locations
        r'middle\s+east(?:ern)?\s+conflict',
        r'palestine',
        r'west\s+bank',
        r'settlement',
        
        # Psychological terms that may trigger when combined with violence
        r'psychological\s+(?:horror|trauma|damage)',
        r'mental\s+breakdown',
        r'suicide',
        r'self[\-\s]harm',
    ]
    
    # Safe replacement mappings
    SAFE_REPLACEMENTS = {
        # Conflicts -> generic terms
        r'october\s+7(?:th)?(?:\s+202[34])?': 'recent events',
        r'lebanon\s+war': 'regional conflict',
        r'iran\s+war\s+2025': 'future scenario',
        r'gaza': 'conflict zone',
        r'israeli?\s+veteran': 'military veteran',
        r'idf': 'military',
        
        # Violence -> abstract terms
        r'ptsd': 'stress',
        r'trauma(?:tic)?': 'difficult experience',
        r'explosion': 'loud sound',
        r'gunfire': 'distant sounds',
        r'blood(?:y)?': 'intense',
        r'weapon': 'equipment',
        
        # Specific -> generic
        r'middle\s+east(?:ern)?\s+conflict': 'regional tensions',
        r'psychological\s+horror': 'psychological tension',
        r'war\s+crime': 'conflict event',
    }
    
    def __init__(self):
        """Initialize the safety validator"""
        self.max_prompt_length = 1000  # Characters
        self.max_keywords = 20  # Maximum keywords to avoid overwhelm
        logger.info("🛡️ VEO3 Safety Validator initialized")
    
    def validate_prompt(self, prompt: Any) -> ValidationResult:
        """
        Validate a VEO3 prompt for safety issues
        
        Args:
            prompt: String prompt or JSON dict
            
        Returns:
            ValidationResult with safety analysis
        """
        # Convert to string if JSON
        if isinstance(prompt, dict):
            prompt_str = json.dumps(prompt, separators=(',', ':'))
        else:
            prompt_str = str(prompt)
        
        original_length = len(prompt_str)
        issues = []
        suggestions = []
        
        # Check for sensitive terms
        sensitive_found = self._check_sensitive_terms(prompt_str)
        if sensitive_found:
            issues.append(SafetyIssueType.SENSITIVE_CONFLICT)
            suggestions.append("Remove or generalize conflict-specific references")
        
        # Check prompt length
        if original_length > self.max_prompt_length:
            issues.append(SafetyIssueType.PROMPT_TOO_LONG)
            suggestions.append(f"Reduce prompt to under {self.max_prompt_length} characters")
        
        # Check keyword count if JSON
        if isinstance(prompt, dict) and 'keywords' in prompt:
            if len(prompt['keywords']) > self.max_keywords:
                issues.append(SafetyIssueType.EXCESSIVE_KEYWORDS)
                suggestions.append(f"Reduce keywords to {self.max_keywords} or fewer")
        
        # Simplify the prompt
        simplified = self.simplify_prompt(prompt)
        
        return ValidationResult(
            is_safe=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            simplified_prompt=simplified,
            original_length=original_length,
            simplified_length=len(simplified) if isinstance(simplified, str) else len(json.dumps(simplified))
        )
    
    def _check_sensitive_terms(self, text: str) -> List[str]:
        """Check for sensitive terms in text"""
        text_lower = text.lower()
        found_terms = []
        
        for pattern in self.SENSITIVE_TERMS:
            if re.search(pattern, text_lower):
                found_terms.append(pattern)
        
        if found_terms:
            logger.warning(f"⚠️ Found {len(found_terms)} sensitive terms in prompt")
        
        return found_terms
    
    def simplify_prompt(self, prompt: Any, therapeutic_mode: bool = False) -> Any:
        """
        Simplify a prompt to avoid safety issues
        
        Args:
            prompt: Original prompt (string or dict)
            therapeutic_mode: Use therapeutic transformation for clinical content
            
        Returns:
            Simplified prompt in same format as input
        """
        if therapeutic_mode:
            # Use therapeutic transformer for clinical content
            from src.utils.therapeutic_content_transformer import TherapeuticContentTransformer
            transformer = TherapeuticContentTransformer()
            
            if isinstance(prompt, dict):
                # Transform each text field in the dict
                transformed_dict = prompt.copy()
                text_fields = ['scene', 'motion', 'subject', 'audio', 'visual_details']
                for field in text_fields:
                    if field in transformed_dict:
                        if isinstance(transformed_dict[field], str):
                            result = transformer.transform_content(transformed_dict[field])
                            transformed_dict[field] = result.transformed
                        elif isinstance(transformed_dict[field], dict) and 'description' in transformed_dict[field]:
                            result = transformer.transform_content(transformed_dict[field]['description'])
                            transformed_dict[field]['description'] = result.transformed
                return transformed_dict
            else:
                # Transform text prompt
                result = transformer.transform_content(str(prompt))
                return result.transformed
        
        if isinstance(prompt, dict):
            return self._simplify_json_prompt(prompt)
        else:
            return self._simplify_text_prompt(str(prompt))
    
    def _simplify_text_prompt(self, text: str) -> str:
        """Simplify a text prompt"""
        simplified = text
        
        # Apply safe replacements
        for pattern, replacement in self.SAFE_REPLACEMENTS.items():
            simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
        
        # Remove overly descriptive violence
        simplified = re.sub(r'\b(?:graphic|violent|disturbing|explicit)\s+', '', simplified)
        
        # Truncate if too long
        if len(simplified) > self.max_prompt_length:
            simplified = simplified[:self.max_prompt_length-3] + "..."
        
        return simplified
    
    def _simplify_json_prompt(self, prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify a JSON prompt"""
        simplified = prompt_dict.copy()
        
        # Simplify keywords
        if 'keywords' in simplified:
            # Remove sensitive keywords
            safe_keywords = []
            for keyword in simplified['keywords'][:self.max_keywords]:
                keyword_lower = keyword.lower()
                is_safe = True
                for pattern in self.SENSITIVE_TERMS:
                    if re.search(pattern, keyword_lower):
                        is_safe = False
                        break
                if is_safe:
                    safe_keywords.append(keyword)
            simplified['keywords'] = safe_keywords
        
        # Simplify nested fields
        fields_to_simplify = ['motion', 'subject', 'scene', 'audio', 'visual_details']
        for field in fields_to_simplify:
            if field in simplified:
                if isinstance(simplified[field], str):
                    simplified[field] = self._simplify_text_prompt(simplified[field])
                elif isinstance(simplified[field], dict):
                    for subfield, value in simplified[field].items():
                        if isinstance(value, str):
                            simplified[field][subfield] = self._simplify_text_prompt(value)
        
        # Remove overly complex nested structures
        if 'cinematography' in simplified and isinstance(simplified['cinematography'], dict):
            # Keep only essential fields
            essential = ['lighting', 'tone', 'color_palette']
            simplified['cinematography'] = {
                k: v for k, v in simplified['cinematography'].items() 
                if k in essential
            }
        
        return simplified
    
    def create_safe_prompt(self, 
                          content: str,
                          style: str = "cinematic",
                          duration: int = 8) -> Dict[str, Any]:
        """
        Create a safe, minimal VEO3 prompt from content
        
        Args:
            content: The main content to visualize
            style: Visual style
            duration: Duration in seconds
            
        Returns:
            Safe, minimal JSON prompt
        """
        # Clean the content
        safe_content = self._simplify_text_prompt(content)
        
        # Create minimal but effective prompt
        safe_prompt = {
            "scene": {
                "description": safe_content,
                "style": style
            },
            "motion": "smooth camera movement, natural pacing",
            "keywords": [
                style,
                "professional",
                "high quality",
                "cinematic",
                "4K"
            ],
            "duration": duration,
            "style": {
                "visual_aesthetic": f"{style} visual style",
                "quality": "4K ultra HD"
            }
        }
        
        logger.info(f"✅ Created safe prompt: {len(json.dumps(safe_prompt))} chars")
        return safe_prompt


def validate_and_fix_prompt(prompt: Any) -> Tuple[Any, bool]:
    """
    Convenient function to validate and fix a prompt
    
    Args:
        prompt: The prompt to validate
        
    Returns:
        Tuple of (fixed_prompt, was_modified)
    """
    validator = VEO3SafetyValidator()
    result = validator.validate_prompt(prompt)
    
    if not result.is_safe:
        logger.warning(f"⚠️ Prompt has {len(result.issues)} safety issues, applying fixes...")
        for suggestion in result.suggestions:
            logger.info(f"  → {suggestion}")
        return result.simplified_prompt, True
    
    return prompt, False