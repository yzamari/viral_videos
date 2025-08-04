"""Alien Character Presenter for Israeli News"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import random

from ...utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class AlienCharacter:
    """Alien news presenter configuration"""
    name: str = "זורג מכוכב קסם"  # Zorg from Planet Qesem
    personality: str = "sarcastic_observer"
    appearance: str = "green_humanoid"
    position: Tuple[int, int] = (1520, 780)  # Bottom right
    size: Tuple[int, int] = (200, 200)
    
    # Character traits for Israeli audience
    traits: List[str] = None
    
    def __post_init__(self):
        if self.traits is None:
            self.traits = [
                "cynical",
                "humorous", 
                "direct",
                "slightly_confused_by_humans",
                "loves_hummus"
            ]


class AlienPresenterGenerator:
    """Generate alien commentary for news stories"""
    
    def __init__(self, character: Optional[AlienCharacter] = None):
        self.character = character or AlienCharacter()
        
        # Commentary templates with dark humor
        self.commentary_templates = {
            "political_scandal": [
                "בכוכב שלי, פוליטיקאים כאלה הופכים לדשן... ממש כמו אצלכם, רק יותר מהר",
                "מעניין, אצלכם שחיתות זה באג או פיצ'ר?",
                "רגע, זה אותו פוליטיקאי מפעם שעברה? קשה להבדיל, כולם נראים אותו דבר"
            ],
            "bizarre_news": [
                "וחשבתי שרק בכוכב שלי יש משוגעים...",
                "זה מה שקורה כשאוכלים יותר מדי חומוס?",
                "אני כבר 500 שנה על כדור הארץ וזה עדיין מפתיע אותי"
            ],
            "tech_news": [
                "חמוד, הם חושבים שהם המציאו טכנולוגיה",
                "אצלנו בכוכב קסם יש את זה כבר 3000 שנה, אבל בטח, 'חדשנות'",
                "AI? אנחנו קוראים לזה 'בן דוד מהכוכב השכן'"
            ],
            "sports": [
                "22 בני אדם רודפים אחרי כדור... ואני החייזר המוזר?",
                "בכוכב שלי המפסידים הופכים לאסטרואידים. פה רק מפטרים את המאמן",
                "כדורגל זה בעצם מלחמה, רק עם פחות נשק גרעיני"
            ],
            "economy": [
                "שקל חדש? אצלנו המטבע לא מזדקן אף פעם",
                "אינפלציה... זה כשהכסף שלכם שווה פחות מהאוויר שאתם נושמים?",
                "מעניין למה אתם קוראים לזה 'כלכלה' ולא 'קזינו לאומי'"
            ],
            "general": [
                "עוד יום רגיל בכדור הארץ המטורף הזה",
                "אם זה החדשות הטובות, אני לא רוצה לשמוע את הרעות",
                "תזכירו לי למה בחרתי לנחות דווקא כאן?"
            ]
        }
        
        # Alien observations about Israeli culture
        self.cultural_observations = [
            "למדתי שבישראל 'מיד' זה בין שעה לשבוע",
            "גיליתי שחומוס זה לא רק אוכל, זה דת",
            "מסתבר ש'יהיה בסדר' זה הפתרון הישראלי לכל בעיה",
            "הבנתי שצפירה בכביש זה אמצעי תקשורת לגיטימי",
            "נדהמתי לגלות שאפשר להתווכח על הכל, כולל על מה להתווכח"
        ]
    
    def generate_intro(self, episode_title: str) -> str:
        """Generate alien intro for the news"""
        intros = [
            f"שלום בני אדם! אני {self.character.name}, והיום אני כאן להסביר לכם מה קרה בכוכב המשוגע שלכם",
            f"ברוכים הבאים ל{episode_title}. אני החייזר שלכם, וגם אני לא מבין מה קורה פה",
            f"זורג כאן. ישבתי כל היום וצפיתי בחדשות שלכם. עכשיו אני צריך טיפול"
        ]
        
        observation = random.choice(self.cultural_observations)
        return f"{random.choice(intros)}. דרך אגב, {observation}."
    
    def generate_commentary(self, article: Dict[str, Any]) -> str:
        """Generate alien commentary for a news article"""
        # Determine article category
        category = self._determine_category(article)
        
        # Get appropriate templates
        templates = self.commentary_templates.get(
            category, 
            self.commentary_templates["general"]
        )
        
        # Select random template
        commentary = random.choice(templates)
        
        # Add specific observations based on content
        if "ביבי" in article.get("title", "") or "נתניהו" in article.get("title", ""):
            commentary += " ...שוב"
        
        if article.get("is_bizarre", False):
            commentary += " ברצינות, אפילו אני לא מצליח להמציא דבר כזה."
        
        return commentary
    
    def generate_outro(self) -> str:
        """Generate alien outro"""
        outros = [
            "זהו להיום. אני חוזר לחללית לקחת כדור ראש. נתראה מחר... אם אשרוד",
            "תודה שצפיתם. עכשיו אני הולך לאכול חומוס ולבכות על מצב האנושות",
            "עד כאן החדשות. זכרו - אם חייזר מבין את החדשות שלכם, יש בעיה",
            "נתראה בפרק הבא, אם לא יגרשו אותי מהכוכב הזה קודם"
        ]
        
        return f"{random.choice(outros)} {self.character.name}, חוזר לכוכב קסם. או לפחות מנסה."
    
    def _determine_category(self, article: Dict[str, Any]) -> str:
        """Determine article category for appropriate commentary"""
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        full_text = f"{title} {content}"
        
        category_keywords = {
            "political_scandal": ["שחיתות", "חקירה", "חשד", "פרשה", "שוחד"],
            "tech_news": ["טכנולוגיה", "סטארטאפ", "אפליקציה", "AI", "חדשנות"],
            "sports": ["כדורגל", "ספורט", "משחק", "ליגה", "אליפות"],
            "economy": ["כלכלה", "שקל", "מחירים", "יוקר", "תקציב"],
            "bizarre_news": ["מוזר", "תמוה", "מפתיע", "הזוי"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in full_text for keyword in keywords):
                return category
        
        return "general"
    
    def get_animation_sequence(self, commentary_type: str = "talking") -> Dict[str, Any]:
        """Get animation sequence for alien character"""
        animations = {
            "talking": {
                "mouth_movement": "sync_to_audio",
                "eye_blinks": "random_interval",
                "antenna_wiggle": "continuous",
                "hand_gestures": "emphasis_points"
            },
            "thinking": {
                "head_scratch": True,
                "eye_movement": "looking_up",
                "antenna_glow": "pulsing"
            },
            "shocked": {
                "eyes_wide": True,
                "antenna_straight": True,
                "mouth_open": True
            },
            "sarcastic": {
                "eye_roll": True,
                "smirk": True,
                "antenna_droop": "slight"
            }
        }
        
        return animations.get(commentary_type, animations["talking"])


class AlienVideoComposer:
    """Compose video with alien character overlay"""
    
    def __init__(self, character: AlienCharacter):
        self.character = character
    
    def get_alien_layer_config(self) -> Dict[str, Any]:
        """Get configuration for alien video layer"""
        return {
            "layer_type": "presenter",
            "asset_path": "assets/alien_character/zorg_transparent.mp4",  # Pre-rendered alien
            "position": self.character.position,
            "size": self.character.size,
            "z_index": 100,  # On top of most elements
            "blend_mode": "normal",
            "opacity": 1.0,
            "chroma_key": {
                "enabled": True,
                "color": "#00FF00",  # Green screen
                "tolerance": 0.3
            }
        }
    
    def generate_alien_prompt_for_veo(self, animation_type: str) -> str:
        """Generate VEO prompt for alien character"""
        base_prompt = (
            "A friendly green humanoid alien news presenter, "
            "professional studio lighting, transparent background, "
            "wearing a small Israeli flag pin, holding a tablet"
        )
        
        animation_prompts = {
            "talking": f"{base_prompt}, speaking and gesturing naturally",
            "reacting": f"{base_prompt}, showing surprised expression",
            "thinking": f"{base_prompt}, looking puzzled and scratching head"
        }
        
        return animation_prompts.get(animation_type, animation_prompts["talking"])