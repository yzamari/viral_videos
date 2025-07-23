"""Cultural Sensitivity Agent - Ensures content respects cultural guidelines."""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class CulturalGuidelines:
    """Cultural guidelines for content generation."""
    culture: str
    dress_code: Dict[str, List[str]]
    content_restrictions: List[str]
    appropriate_topics: List[str]
    visual_guidelines: List[str]
    language_considerations: List[str]


class CulturalSensitivityAgent:
    """Agent responsible for ensuring cultural sensitivity in content generation."""
    
    def __init__(self, api_key: str):
        """Initialize the cultural sensitivity agent.
        
        Args:
            api_key: API key for AI services
        """
        self.api_key = api_key
        self._guidelines_cache: Dict[str, CulturalGuidelines] = {}
        self._load_default_guidelines()
        
    def _load_default_guidelines(self):
        """Load default cultural guidelines."""
        # Iranian/Persian cultural guidelines
        self._guidelines_cache['iranian'] = CulturalGuidelines(
            culture='iranian',
            dress_code={
                'women': [
                    'MUST wear hijab/headscarf covering hair',
                    'Modest clothing covering arms and legs',
                    'No tight or revealing clothing',
                    'Professional attire for news/formal settings'
                ],
                'men': [
                    'Modest clothing, no bare chest',
                    'Long pants preferred',
                    'Professional attire for formal settings',
                    'No overly casual beach wear'
                ]
            },
            content_restrictions=[
                'NO alcohol or drinking scenes',
                'NO romantic physical contact between non-married individuals',
                'NO mixed-gender dancing',
                'NO gambling or casino imagery',
                'NO pork or non-halal food',
                'NO mockery of religious beliefs',
                'NO disrespect to religious figures',
                'NO inappropriate gestures',
                'NO bikinis or swimwear',
                'NO nightclub or bar scenes'
            ],
            appropriate_topics=[
                'Government inefficiency (with respect)',
                'Bureaucracy and red tape',
                'Economic challenges',
                'Environmental issues',
                'Technology adoption',
                'Traffic and urban problems',
                'Education system',
                'Generational differences',
                'Cultural traditions',
                'Persian hospitality (tarof)'
            ],
            visual_guidelines=[
                'Include Persian/Farsi text where appropriate',
                'Use traditional Persian design elements',
                'Show respect for elders',
                'Avoid Western-centric imagery',
                'Include Persian cultural symbols appropriately',
                'Maintain professional broadcast standards',
                'Use modest, culturally appropriate settings'
            ],
            language_considerations=[
                'Use formal Persian when appropriate',
                'Include cultural idioms and proverbs',
                'Avoid crude or vulgar language',
                'Reference Persian poetry when relevant',
                'Use respectful titles and honorifics'
            ]
        )
        
    def validate_content_request(
        self, 
        mission: str, 
        culture: str = 'iranian',
        content_type: str = 'video'
    ) -> Dict[str, Any]:
        """Validate and adjust content request for cultural sensitivity.
        
        Args:
            mission: The content generation mission/prompt
            culture: The target culture
            content_type: Type of content (video, audio, script)
            
        Returns:
            Validation result with adjusted mission if needed
        """
        guidelines = self._guidelines_cache.get(culture)
        if not guidelines:
            logger.warning(f"No guidelines found for culture: {culture}")
            return {
                'valid': True,
                'adjusted_mission': mission,
                'warnings': []
            }
            
        violations = []
        suggestions = []
        
        # Check for potential violations
        mission_lower = mission.lower()
        
        for restriction in guidelines.content_restrictions:
            key_terms = restriction.lower().replace('no ', '').split(' or ')
            for term in key_terms:
                if term in mission_lower:
                    violations.append(f"Potential violation: {restriction}")
                    
        # Add cultural requirements
        cultural_requirements = []
        
        if 'women' in mission_lower or 'female' in mission_lower or 'leila' in mission_lower:
            cultural_requirements.append(
                "IMPORTANT: Female characters MUST wear appropriate hijab/headscarf. "
                "Clothing must be modest, covering arms and legs."
            )
            
        if content_type == 'video':
            cultural_requirements.append(
                "VISUAL REQUIREMENTS: Maintain cultural sensitivity in all visuals. "
                "No alcohol, no inappropriate physical contact, modest dress for all characters."
            )
            
        # Build adjusted mission
        adjusted_mission = f"CULTURAL SENSITIVITY GUIDELINES FOR {culture.upper()} AUDIENCE:\n"
        adjusted_mission += "\n".join(cultural_requirements) + "\n\n"
        adjusted_mission += "ORIGINAL REQUEST: " + mission
        
        # Add appropriate suggestions
        if 'humor' in mission_lower or 'comedy' in mission_lower or 'satire' in mission_lower:
            adjusted_mission += "\n\nCOMEDY GUIDELINES: Use intelligent satire focusing on "
            adjusted_mission += ", ".join(guidelines.appropriate_topics[:3])
            adjusted_mission += ". Avoid crude humor or cultural insensitivity."
            
        return {
            'valid': len(violations) == 0,
            'adjusted_mission': adjusted_mission,
            'violations': violations,
            'suggestions': suggestions,
            'cultural_requirements': cultural_requirements
        }
        
    def get_visual_guidelines(self, culture: str = 'iranian') -> List[str]:
        """Get visual guidelines for video generation.
        
        Args:
            culture: Target culture
            
        Returns:
            List of visual guidelines
        """
        guidelines = self._guidelines_cache.get(culture)
        if not guidelines:
            return []
            
        visual_rules = []
        
        # Dress code rules
        visual_rules.append("DRESS CODE REQUIREMENTS:")
        for gender, rules in guidelines.dress_code.items():
            visual_rules.append(f"{gender.upper()}: {'; '.join(rules)}")
            
        # Visual restrictions
        visual_rules.append("\nVISUAL RESTRICTIONS:")
        visual_rules.extend([r for r in guidelines.content_restrictions if 'NO' in r])
        
        # Positive visual elements
        visual_rules.append("\nRECOMMENDED VISUAL ELEMENTS:")
        visual_rules.extend(guidelines.visual_guidelines)
        
        return visual_rules
        
    def get_audio_guidelines(self, culture: str = 'iranian') -> List[str]:
        """Get audio guidelines for content generation.
        
        Args:
            culture: Target culture
            
        Returns:
            List of audio guidelines
        """
        guidelines = self._guidelines_cache.get(culture)
        if not guidelines:
            return []
            
        audio_rules = [
            "AUDIO CONTENT GUIDELINES:",
            "- Use respectful language and tone",
            "- Include culturally appropriate music only",
            "- No music during prayer times or religious content",
            "- Avoid crude jokes or vulgar language",
            "- Use formal language for news/professional content",
            "- Include Persian/Farsi where appropriate"
        ]
        
        if guidelines.language_considerations:
            audio_rules.append("\nLANGUAGE CONSIDERATIONS:")
            audio_rules.extend([f"- {consideration}" for consideration in guidelines.language_considerations])
            
        return audio_rules
        
    def create_cultural_brief(
        self, 
        culture: str = 'iranian',
        content_type: str = 'news_satire'
    ) -> str:
        """Create a comprehensive cultural brief for content creators.
        
        Args:
            culture: Target culture
            content_type: Type of content being created
            
        Returns:
            Cultural brief as formatted string
        """
        guidelines = self._guidelines_cache.get(culture)
        if not guidelines:
            return "No specific cultural guidelines available."
            
        brief = f"""
CULTURAL SENSITIVITY BRIEF - {culture.upper()} CONTENT

CONTENT TYPE: {content_type.replace('_', ' ').title()}

MANDATORY REQUIREMENTS:
{chr(10).join([f"✓ {req}" for req in guidelines.dress_code.get('women', [])])}
{chr(10).join([f"✓ {req}" for req in guidelines.dress_code.get('men', [])])}

PROHIBITED CONTENT:
{chr(10).join([f"✗ {restriction}" for restriction in guidelines.content_restrictions[:5]])}

APPROPRIATE TOPICS FOR SATIRE/HUMOR:
{chr(10).join([f"• {topic}" for topic in guidelines.appropriate_topics[:5]])}

VISUAL STYLE GUIDELINES:
{chr(10).join([f"• {guideline}" for guideline in guidelines.visual_guidelines[:5]])}

REMEMBER: Respect the culture while creating engaging content. Intelligence and wit are preferred over crude humor.
"""
        return brief
        
    def format_for_ai_agents(self, culture: str = 'iranian') -> Dict[str, Any]:
        """Format cultural guidelines for AI agent consumption.
        
        Args:
            culture: Target culture
            
        Returns:
            Formatted guidelines for AI agents
        """
        guidelines = self._guidelines_cache.get(culture)
        if not guidelines:
            return {}
            
        return {
            'culture': culture,
            'mandatory_rules': {
                'dress_code': guidelines.dress_code,
                'visual_restrictions': [r for r in guidelines.content_restrictions if 'NO' in r],
                'content_restrictions': guidelines.content_restrictions
            },
            'recommendations': {
                'appropriate_topics': guidelines.appropriate_topics,
                'visual_elements': guidelines.visual_guidelines,
                'language_tips': guidelines.language_considerations
            },
            'key_principles': [
                'Respect religious and cultural values',
                'Use intelligent humor over crude jokes',
                'Maintain modest dress codes',
                'Avoid Western-centric perspectives',
                'Include cultural references appropriately'
            ]
        }