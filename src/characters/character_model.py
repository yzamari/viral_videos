"""
Character Model for ViralAI System
Defines the structure and validation for character entities
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid


@dataclass
class Character:
    """Comprehensive character model for video generation"""
    
    # Core identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""  # Unique identifier name (e.g., "prof_educator")
    display_name: str = ""  # Human-friendly name (e.g., "Professor Smith")
    
    # Personality and behavior
    personality: str = ""  # Detailed personality description
    profession: str = ""  # Role/occupation
    backstory: Optional[str] = None  # Character background story
    
    # Voice characteristics
    voice_style: str = "professional"  # How they speak
    speaking_style: str = "formal"  # formal/casual/energetic/calm
    voice_provider: str = "google"  # google/elevenlabs/azure
    voice_id: Optional[str] = None  # Specific voice ID for TTS
    voice_speed: float = 1.0  # Speech rate multiplier
    voice_pitch: float = 0.0  # Voice pitch adjustment
    
    # Visual characteristics
    visual_description: str = ""  # Detailed appearance description
    age_range: str = "30-40"  # Approximate age
    gender: str = "neutral"  # male/female/neutral
    ethnicity: Optional[str] = None  # Cultural background
    clothing_style: str = "professional"  # Dress code
    
    # Behavioral attributes
    energy_level: str = "medium"  # low/medium/high
    formality_level: str = "medium"  # casual/medium/formal
    humor_style: Optional[str] = None  # Type of humor they use
    catchphrases: List[str] = field(default_factory=list)
    
    # Content preferences
    preferred_topics: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)
    language_preferences: List[str] = field(default_factory=lambda: ["en-US"])
    cultural_references: List[str] = field(default_factory=list)
    
    # Media assets
    character_image_path: Optional[str] = None  # Reference image
    character_video_samples: List[str] = field(default_factory=list)
    voice_samples: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)  # For searching/filtering
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "system"
    is_active: bool = True
    usage_count: int = 0
    
    # Platform-specific settings
    platform_preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert character to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create character from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Character':
        """Create character from JSON string"""
        return cls.from_dict(json.loads(json_str))
    
    def validate(self) -> List[str]:
        """Validate character data and return list of errors"""
        errors = []
        
        if not self.name:
            errors.append("Character name is required")
        if not self.display_name:
            errors.append("Display name is required")
        if not self.personality:
            errors.append("Personality description is required")
        if not self.visual_description:
            errors.append("Visual description is required")
        
        # Validate voice settings
        valid_providers = ["google", "elevenlabs", "azure", "openai"]
        if self.voice_provider not in valid_providers:
            errors.append(f"Voice provider must be one of: {valid_providers}")
        
        # Validate ranges
        if not 0.5 <= self.voice_speed <= 2.0:
            errors.append("Voice speed must be between 0.5 and 2.0")
        if not -20 <= self.voice_pitch <= 20:
            errors.append("Voice pitch must be between -20 and 20")
        
        return errors
    
    def get_prompt_context(self) -> str:
        """Generate context string for AI prompts"""
        context = f"""
Character: {self.display_name}
Personality: {self.personality}
Profession: {self.profession}
Speaking Style: {self.speaking_style}, {self.voice_style}
Energy Level: {self.energy_level}
Age: {self.age_range}
"""
        if self.backstory:
            context += f"Backstory: {self.backstory}\n"
        if self.catchphrases:
            context += f"Catchphrases: {', '.join(self.catchphrases)}\n"
        if self.expertise_areas:
            context += f"Expertise: {', '.join(self.expertise_areas)}\n"
        
        return context.strip()
    
    def __str__(self) -> str:
        return f"Character({self.name}: {self.display_name})"
    
    def __repr__(self) -> str:
        return f"Character(id={self.id}, name={self.name}, display_name={self.display_name})"


# Character template factory
def create_character_from_template(template_name: str) -> Character:
    """Create a character from a predefined template"""
    
    templates = {
        "educator": {
            "name": "prof_educator",
            "display_name": "Professor Smith",
            "personality": "Knowledgeable, patient, and enthusiastic about teaching. Uses clear explanations and relatable examples.",
            "profession": "University Professor",
            "voice_style": "clear and articulate",
            "speaking_style": "formal",
            "visual_description": "Middle-aged professional with glasses, wearing business casual attire",
            "age_range": "45-55",
            "energy_level": "medium",
            "formality_level": "formal",
            "expertise_areas": ["education", "science", "technology"],
            "tags": ["educational", "professional", "teacher"]
        },
        "influencer": {
            "name": "energetic_influencer",
            "display_name": "Alex Energy",
            "personality": "Highly energetic, trendy, and engaging. Uses current slang and viral references.",
            "profession": "Social Media Influencer",
            "voice_style": "upbeat and dynamic",
            "speaking_style": "casual",
            "visual_description": "Young, trendy person with stylish clothing and accessories",
            "age_range": "20-30",
            "energy_level": "high",
            "formality_level": "casual",
            "catchphrases": ["Let's go!", "That's fire!", "No cap!"],
            "expertise_areas": ["social media", "trends", "lifestyle"],
            "tags": ["energetic", "trendy", "social"]
        },
        "mentor": {
            "name": "wise_mentor",
            "display_name": "Sage Williams",
            "personality": "Wise, thoughtful, and supportive. Provides deep insights and encouragement.",
            "profession": "Life Coach",
            "voice_style": "calm and reassuring",
            "speaking_style": "formal",
            "visual_description": "Distinguished older person with warm expression and professional attire",
            "age_range": "55-65",
            "energy_level": "low",
            "formality_level": "medium",
            "expertise_areas": ["personal development", "wisdom", "guidance"],
            "tags": ["wise", "mentor", "coach"]
        },
        "tech_enthusiast": {
            "name": "tech_guru",
            "display_name": "Tech Taylor",
            "personality": "Passionate about technology, innovative, and forward-thinking. Explains complex topics simply.",
            "profession": "Tech Entrepreneur",
            "voice_style": "enthusiastic and clear",
            "speaking_style": "casual",
            "visual_description": "Modern professional in smart casual tech wear",
            "age_range": "30-40",
            "energy_level": "high",
            "formality_level": "casual",
            "expertise_areas": ["technology", "innovation", "startups"],
            "tags": ["tech", "innovative", "entrepreneur"]
        },
        "business_coach": {
            "name": "biz_coach",
            "display_name": "Morgan Success",
            "personality": "Confident, motivating, and results-oriented. Focuses on practical strategies.",
            "profession": "Business Consultant",
            "voice_style": "confident and authoritative",
            "speaking_style": "formal",
            "visual_description": "Sharp business professional in formal attire",
            "age_range": "35-45",
            "energy_level": "medium",
            "formality_level": "formal",
            "expertise_areas": ["business", "leadership", "strategy"],
            "tags": ["business", "professional", "coach"]
        }
    }
    
    if template_name not in templates:
        raise ValueError(f"Template '{template_name}' not found. Available: {list(templates.keys())}")
    
    return Character(**templates[template_name])