"""
Character Description Agent - Researches and describes characters accurately
"""

import json
import re
from typing import Dict, Any, Optional
from ..utils.logging_config import get_logger
from .gemini_helper import GeminiModelHelper, ensure_api_key

logger = get_logger(__name__)

class CharacterDescriptionAgent:
    """AI agent for accurate character description with cultural awareness"""
    
    def __init__(self, api_key: str):
        """Initialize Character Description Agent"""
        self.api_key = ensure_api_key(api_key)
        self.model = GeminiModelHelper.get_configured_model(self.api_key)
        logger.info("👤 CharacterDescriptionAgent initialized")
    
    def describe_character(self, mission: str, character_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Research and describe characters based on mission context
        """
        try:
            # Enhanced prompt for character research
            prompt = f"""
IMPORTANT: Research the characters thoroughly based on the mission context.

Mission: "{mission}"
{f"Character hint: {character_hint}" if character_hint else ""}

Tasks:
1. ETHNICITY: If the mission mentions specific countries/cultures (Iranian, Israeli, Japanese, etc.), 
   research what people from that region typically look like
2. HISTORICAL FIGURES: If real people are mentioned (Ben-Gurion, Netanyahu, etc.), 
   research their actual appearance
3. Be SPECIFIC about:
   - Facial features
   - Hair color and style
   - Typical clothing
   - Age appearance
   - Distinctive features

For Iranian characters: Research typical Persian/Iranian features
For Israeli characters: Research diverse Israeli appearances
For historical figures: Use their actual documented appearance

Return JSON:
{{
    "character_description": "Detailed physical description",
    "ethnicity": "Specific ethnic appearance",
    "clothing": "Typical attire",
    "distinctive_features": "Unique identifying features",
    "age_range": "Approximate age",
    "additional_notes": "Cultural or historical context"
}}
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    character_data = json.loads(json_match.group())
                    logger.info(f"👤 Character described: {character_data.get('ethnicity', 'Unknown')}")
                    return character_data
            
            # Fallback
            return {
                "character_description": "Person appropriate to the context",
                "ethnicity": "Contextually appropriate",
                "clothing": "Standard attire",
                "distinctive_features": "None specified",
                "age_range": "Adult",
                "additional_notes": "Generic character"
            }
            
        except Exception as e:
            logger.error(f"❌ Character description failed: {e}")
            return self._get_fallback_character()
    
    def _get_fallback_character(self) -> Dict[str, Any]:
        """Fallback character description"""
        return {
            "character_description": "Generic person",
            "ethnicity": "Neutral",
            "clothing": "Casual attire",
            "distinctive_features": "None",
            "age_range": "30-50",
            "additional_notes": "Fallback character"
        }
