"""
Centralized JSON Fixer Utility
Handles JSON parsing errors and uses AI to fix corrupted JSON responses
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Union
from google.generativeai import GenerativeModel

logger = logging.getLogger(__name__)

class JSONFixer:
    """
    Centralized JSON fixing utility that handles various parsing issues
    and uses AI to fix corrupted JSON when needed
    """
    
    def __init__(self, api_key: str):
        """
        Initialize JSON Fixer
        
        Args:
            api_key: Google AI API key for fixing corrupted JSON
        """
        self.api_key = api_key
        self.model = GenerativeModel('gemini-1.5-flash')
        
    def fix_json(self, raw_response: str, expected_structure: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Fix JSON parsing issues using multiple strategies
        
        Args:
            raw_response: Raw response string that may contain JSON
            expected_structure: Optional expected structure for validation
            
        Returns:
            Fixed JSON dict or None if unfixable
        """
        logger.info("🔧 Attempting to fix JSON response...")
        
        # Strategy 1: Try direct JSON parsing
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parsing failed: {e}")
        
        # Strategy 2: Extract JSON from markdown code blocks
        json_content = self._extract_json_from_markdown(raw_response)
        if json_content:
            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e:
                logger.debug(f"Markdown JSON extraction failed: {e}")
        
        # Strategy 3: Clean common issues
        cleaned_json = self._clean_common_issues(raw_response)
        if cleaned_json:
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError as e:
                logger.debug(f"Common issues cleaning failed: {e}")
        
        # Strategy 4: Remove control characters and try again
        cleaned_response = self._remove_control_characters(raw_response)
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.debug(f"Control character removal failed: {e}")
        
        # Strategy 5: Try to fix truncated JSON
        fixed_json = self._fix_truncated_json(raw_response)
        if fixed_json:
            try:
                return json.loads(fixed_json)
            except json.JSONDecodeError as e:
                logger.debug(f"Truncated JSON fix failed: {e}")
        
        # Strategy 6: Use AI to fix corrupted JSON
        logger.warning("⚠️ All automatic JSON fixes failed, using AI to fix...")
        return self._fix_with_ai(raw_response, expected_structure)
    
    def _extract_json_from_markdown(self, raw_response: str) -> Optional[str]:
        """Extract JSON from markdown code blocks"""
        # Look for ```json ... ``` blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for ``` ... ``` blocks (without json specifier)
        code_pattern = r'```\s*(.*?)\s*```'
        match = re.search(code_pattern, raw_response, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Check if it looks like JSON
            if content.startswith('{') and content.endswith('}'):
                return content
        
        return None
    
    def _clean_common_issues(self, raw_response: str) -> Optional[str]:
        """Clean common JSON issues"""
        # Remove leading/trailing whitespace and newlines
        cleaned = raw_response.strip()
        
        # Remove any text before the first {
        start_idx = cleaned.find('{')
        if start_idx > 0:
            cleaned = cleaned[start_idx:]
        
        # Remove any text after the last }
        end_idx = cleaned.rfind('}')
        if end_idx >= 0 and end_idx < len(cleaned) - 1:
            cleaned = cleaned[:end_idx + 1]
        
        # Fix common template variable issues
        cleaned = self._fix_template_variables(cleaned)
        
        # Fix common JavaScript-style issues
        cleaned = self._fix_javascript_syntax(cleaned)
        
        return cleaned if cleaned.startswith('{') and cleaned.endswith('}') else None
    
    def _fix_template_variables(self, json_str: str) -> str:
        """Fix template variables in JSON"""
        # Replace common template variables with safe values
        replacements = {
            r'\{topic\}': '"topic"',
            r'\{platform\.value\}': '"platform"',
            r'\{platform\}': '"platform"',
            r'\{category\.value\}': '"category"',
            r'\{category\}': '"category"',
            r'\{duration\}': '30',
            r'\{total_duration\}': '30',
            r'\{Math\.ceil\((.*?)\)\}': '5',
            r'\{Math\.min\((.*?)\)\}': '10',
            r'\{0\.\d+ \* total_duration\}': '5',
            r'\{0\.\d+ \* total_duration / \d+\}': '3',
        }
        
        for pattern, replacement in replacements.items():
            json_str = re.sub(pattern, replacement, json_str)
        
        return json_str
    
    def _fix_javascript_syntax(self, json_str: str) -> str:
        """Fix JavaScript-style syntax in JSON"""
        # Replace JavaScript-style property names without quotes
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)
        
        # Fix JavaScript-style comments
        json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str
    
    def _remove_control_characters(self, text: str) -> str:
        """Remove control characters that break JSON parsing"""
        # Remove control characters except newlines and tabs
        cleaned = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Remove null bytes
        cleaned = cleaned.replace('\x00', '')
        
        return cleaned
    
    def _fix_truncated_json(self, raw_response: str) -> Optional[str]:
        """Try to fix truncated JSON by finding proper end"""
        # Find the last complete object
        brace_count = 0
        last_complete_end = -1
        
        for i, char in enumerate(raw_response):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    last_complete_end = i
        
        if last_complete_end > 0:
            return raw_response[:last_complete_end + 1]
        
        return None
    
    def _fix_with_ai(self, raw_response: str, expected_structure: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Use AI to fix corrupted JSON"""
        try:
            # Create prompt for AI to fix JSON
            prompt = self._create_fix_prompt(raw_response, expected_structure)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            ai_fixed_json = response.text.strip()
            
            # Extract JSON from AI response
            json_content = self._extract_json_from_markdown(ai_fixed_json)
            if not json_content:
                json_content = ai_fixed_json
            
            # Try to parse the AI-fixed JSON
            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ AI JSON fix failed: {e}")
                logger.error(f"AI response: {ai_fixed_json}")
                return None
                
        except Exception as e:
            logger.error(f"❌ AI JSON fixing failed: {e}")
            return None
    
    def _create_fix_prompt(self, raw_response: str, expected_structure: Optional[Dict[str, Any]] = None) -> str:
        """Create prompt for AI to fix JSON"""
        prompt = f"""
You are a JSON fixing expert. The following response contains corrupted JSON that needs to be fixed.

Raw response:
{raw_response}

Please fix the JSON and return ONLY valid JSON. The response should be a complete, valid JSON object.

Common issues to fix:
1. Missing quotes around property names
2. Invalid control characters
3. Template variables that need to be replaced with actual values
4. Truncated responses
5. JavaScript-style syntax in JSON
6. Unclosed brackets or braces

"""
        
        if expected_structure:
            prompt += f"""
Expected structure (for reference):
{json.dumps(expected_structure, indent=2)}

Please ensure the fixed JSON follows a similar structure.
"""
        
        prompt += """
Return ONLY the fixed JSON, no explanations or markdown formatting.
"""
        
        return prompt
    
    def validate_json_structure(self, json_data: Dict[str, Any], expected_structure: Dict[str, Any]) -> bool:
        """
        Validate that JSON data matches expected structure
        
        Args:
            json_data: Parsed JSON data
            expected_structure: Expected structure template
            
        Returns:
            True if structure is valid, False otherwise
        """
        try:
            return self._validate_structure_recursive(json_data, expected_structure)
        except Exception as e:
            logger.error(f"JSON structure validation failed: {e}")
            return False
    
    def _validate_structure_recursive(self, data: Any, expected: Any) -> bool:
        """Recursively validate JSON structure"""
        if isinstance(expected, dict):
            if not isinstance(data, dict):
                return False
            for key, expected_type in expected.items():
                if key not in data:
                    return False
                if not self._validate_structure_recursive(data[key], expected_type):
                    return False
        elif isinstance(expected, list):
            if not isinstance(data, list):
                return False
            if data and not self._validate_structure_recursive(data[0], expected[0]):
                return False
        elif isinstance(expected, type):
            if not isinstance(data, expected):
                return False
        
        return True


def create_json_fixer(api_key: str) -> JSONFixer:
    """
    Factory function to create JSON fixer instance
    
    Args:
        api_key: Google AI API key
        
    Returns:
        Configured JSONFixer instance
    """
    return JSONFixer(api_key) 