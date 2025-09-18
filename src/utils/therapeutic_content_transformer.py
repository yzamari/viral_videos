"""
Therapeutic Content Transformer
Transforms war/trauma narratives into VEO3-safe therapeutic visualizations
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ContentApproach(Enum):
    METAPHORICAL = "metaphorical"  # Use symbolic representations
    ARTISTIC = "artistic"  # Abstract artistic interpretation
    HEALING = "healing"  # Focus on recovery journey
    DOCUMENTARY = "documentary"  # Educational historical context


@dataclass
class TransformationResult:
    original: str
    transformed: str
    approach: ContentApproach
    therapeutic_elements: List[str]
    safety_score: float


class TherapeuticContentTransformer:
    """Transform war/trauma content into therapeutic, VEO3-safe narratives"""
    
    # Map triggers to therapeutic alternatives
    THERAPEUTIC_MAPPINGS = {
        # Combat terms -> Therapeutic metaphors
        "war": "challenging journey",
        "battle": "inner struggle",
        "soldier": "individual",
        "combat": "difficult experience",
        "explosion": "overwhelming moment",
        "weapon": "coping tool",
        "enemy": "challenge",
        "attack": "difficult event",
        "kill": "overcome",
        "death": "transformation",
        "blood": "emotional pain",
        "wound": "emotional scar",
        
        # Specific conflicts -> Universal themes
        "Gaza": "conflicted region",
        "Lebanon": "northern frontier",
        "Israel": "homeland",
        "Palestine": "disputed territory",
        "Hamas": "opposing force",
        "Hezbollah": "northern threat",
        "IDF": "defense forces",
        "terrorist": "hostile actor",
        
        # Trauma terms -> Healing language
        "PTSD": "post-trauma healing journey",
        "flashback": "memory surfacing",
        "nightmare": "difficult dream",
        "trauma": "challenging experience",
        "trigger": "emotional activation",
        "panic": "overwhelming feeling"
    }
    
    THERAPEUTIC_VISUAL_ELEMENTS = [
        "soft lighting filtering through clouds",
        "abstract watercolor transitions",
        "flowing sand patterns",
        "birds flying toward horizon",
        "trees growing from barren ground",
        "sunrise over mountains",
        "calm water reflecting sky",
        "pathways through forests",
        "bridges over calm rivers",
        "doors opening to light"
    ]
    
    def __init__(self):
        self.transformation_history = []
    
    def transform_content(
        self,
        original_content: str,
        client_context: Dict = None,
        approach: ContentApproach = ContentApproach.THERAPEUTIC
    ) -> TransformationResult:
        """
        Transform war/trauma content into therapeutic visualization
        
        Args:
            original_content: Original narrative with potentially triggering content
            client_context: Optional context about the client's specific needs
            approach: Transformation approach to use
        """
        transformed = original_content
        therapeutic_elements = []
        
        # Step 1: Replace direct war terms with therapeutic metaphors
        for trigger, replacement in self.THERAPEUTIC_MAPPINGS.items():
            pattern = re.compile(r'\b' + re.escape(trigger) + r'\b', re.IGNORECASE)
            transformed = pattern.sub(replacement, transformed)
        
        # Step 2: Add therapeutic framing
        if approach == ContentApproach.HEALING:
            transformed = self._add_healing_frame(transformed)
            therapeutic_elements.append("healing journey focus")
        elif approach == ContentApproach.METAPHORICAL:
            transformed = self._create_metaphorical_version(transformed)
            therapeutic_elements.append("metaphorical representation")
        elif approach == ContentApproach.ARTISTIC:
            transformed = self._create_artistic_interpretation(transformed)
            therapeutic_elements.append("artistic abstraction")
        
        # Step 3: Ensure emotional safety
        transformed = self._add_safety_elements(transformed)
        therapeutic_elements.append("emotional safety anchors")
        
        # Step 4: Add grounding elements
        transformed = self._add_grounding_elements(transformed)
        therapeutic_elements.append("grounding techniques")
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(transformed)
        
        result = TransformationResult(
            original=original_content,
            transformed=transformed,
            approach=approach,
            therapeutic_elements=therapeutic_elements,
            safety_score=safety_score
        )
        
        self.transformation_history.append(result)
        return result
    
    def _add_healing_frame(self, content: str) -> str:
        """Frame content within healing journey context"""
        healing_prefix = "A journey of healing and understanding. "
        healing_suffix = " Moving toward peace and resolution."
        
        # Add breathing space
        content = content.replace(". ", ". Take a breath. ")
        
        return healing_prefix + content + healing_suffix
    
    def _create_metaphorical_version(self, content: str) -> str:
        """Convert literal descriptions to metaphorical ones"""
        metaphors = {
            "walking through": "navigating the landscape of",
            "searching": "seeking understanding in",
            "fighting": "wrestling with",
            "running": "moving through",
            "hiding": "finding shelter within",
            "shooting": "releasing",
            "exploding": "transforming suddenly"
        }
        
        result = content
        for literal, metaphor in metaphors.items():
            result = result.replace(literal, metaphor)
        
        # Add metaphorical visual layer
        result = f"Like a dream unfolding, {result.lower()}"
        return result
    
    def _create_artistic_interpretation(self, content: str) -> str:
        """Create artistic, abstract version"""
        # Add artistic framing
        artistic_intro = "In the style of healing art therapy: "
        
        # Convert to more abstract language
        abstractions = {
            "person": "silhouette",
            "place": "landscape",
            "building": "structure",
            "street": "pathway",
            "room": "space",
            "door": "threshold",
            "wall": "boundary"
        }
        
        result = content
        for concrete, abstract in abstractions.items():
            result = result.replace(concrete, abstract)
        
        # Add artistic elements
        result = f"{artistic_intro}Abstract shapes and colors representing {result.lower()}"
        
        # Add one random therapeutic visual element
        import random
        visual = random.choice(self.THERAPEUTIC_VISUAL_ELEMENTS)
        result = f"{result}, transitioning to {visual}"
        
        return result
    
    def _add_safety_elements(self, content: str) -> str:
        """Add emotional safety anchors"""
        safety_phrases = [
            "You are safe now",
            "This is just a memory",
            "You have survived this",
            "You are in control",
            "You can pause anytime"
        ]
        
        # Add safety reminder every few sentences
        sentences = content.split('. ')
        result = []
        for i, sentence in enumerate(sentences):
            result.append(sentence)
            if i % 3 == 2 and i < len(sentences) - 1:  # Every 3rd sentence
                import random
                safety = random.choice(safety_phrases)
                result.append(f"({safety})")
        
        return '. '.join(result)
    
    def _add_grounding_elements(self, content: str) -> str:
        """Add grounding techniques"""
        grounding_elements = [
            "Notice five things you can see",
            "Feel your feet on the ground",
            "Take three deep breaths",
            "Listen to the sounds around you now",
            "Feel the temperature of the air"
        ]
        
        # Add grounding at beginning
        import random
        grounding = random.choice(grounding_elements)
        return f"[{grounding}] {content}"
    
    def _calculate_safety_score(self, content: str) -> float:
        """Calculate how safe the content is for VEO3"""
        unsafe_terms = [
            "war", "kill", "death", "blood", "weapon", "bomb", "shoot",
            "Israel", "Gaza", "Hamas", "soldier", "IDF", "combat"
        ]
        
        content_lower = content.lower()
        unsafe_count = sum(1 for term in unsafe_terms if term in content_lower)
        
        # Score from 0 to 1 (1 being safest)
        safety_score = max(0, 1 - (unsafe_count * 0.1))
        return safety_score
    
    def create_therapeutic_prompt(
        self,
        client_experience: str,
        therapeutic_goal: str = "processing and healing"
    ) -> Dict:
        """
        Create a complete therapeutic video prompt
        
        Args:
            client_experience: The client's actual experience
            therapeutic_goal: What the visualization aims to achieve
        """
        # Transform the experience
        result = self.transform_content(
            client_experience,
            approach=ContentApproach.HEALING
        )
        
        # Create structured prompt for video generation
        prompt = {
            "visual_style": "Soft, healing, therapeutic visualization",
            "animation_style": "Gentle transitions, calming movements",
            "color_palette": "Soothing blues, greens, warm earth tones",
            "narrative": result.transformed,
            "therapeutic_elements": result.therapeutic_elements,
            "pacing": "Slow, allowing time for processing",
            "music": "Calming, therapeutic soundscape",
            "safety_score": result.safety_score,
            "original_preserved": client_experience  # Keep original for therapist reference
        }
        
        return prompt


class TherapeuticPromptBuilder:
    """Build complete therapeutic video generation prompts"""
    
    def __init__(self):
        self.transformer = TherapeuticContentTransformer()
    
    def build_ptsd_healing_prompt(
        self,
        client_story: str,
        session_type: str = "processing"
    ) -> str:
        """
        Build a complete prompt for PTSD healing visualization
        
        Args:
            client_story: The client's actual experience
            session_type: Type of therapeutic session (processing, grounding, resource-building)
        """
        # Transform the story
        transformed = self.transformer.transform_content(
            client_story,
            approach=ContentApproach.HEALING
        )
        
        if session_type == "processing":
            prompt = f"""
            Therapeutic visualization for trauma processing:
            {transformed.transformed}
            
            Visual style: Soft watercolor animations, gentle transitions
            Include: Breathing cues, safety reminders, grounding anchors
            Avoid: Sudden movements, loud sounds, graphic imagery
            Goal: Safe processing and integration of experiences
            """
        elif session_type == "grounding":
            prompt = f"""
            Grounding and stabilization visualization:
            Present moment awareness while acknowledging: {transformed.transformed}
            
            Focus on: Sensory experiences, nature elements, safe spaces
            Include: 5-4-3-2-1 technique, body scan, breath work
            Visual style: Clear, stable imagery with natural elements
            """
        elif session_type == "resource-building":
            prompt = f"""
            Building inner resources and resilience:
            Transforming the experience of: {transformed.transformed}
            Into sources of strength and wisdom.
            
            Visual elements: Growing trees, building bridges, sunrise imagery
            Include: Affirmations, strength symbols, support networks
            Style: Empowering, hopeful, forward-moving
            """
        
        return prompt.strip()
    
    def validate_therapeutic_safety(self, prompt: str) -> Tuple[bool, List[str]]:
        """
        Validate that a prompt is therapeutically appropriate
        
        Returns:
            (is_safe, list_of_concerns)
        """
        concerns = []
        
        # Check for potentially triggering content
        triggers = ["graphic", "violent", "explicit", "disturbing", "shocking"]
        for trigger in triggers:
            if trigger in prompt.lower():
                concerns.append(f"Contains potentially triggering word: {trigger}")
        
        # Check for therapeutic elements
        therapeutic_required = ["safe", "healing", "calm", "ground", "breath"]
        has_therapeutic = any(word in prompt.lower() for word in therapeutic_required)
        
        if not has_therapeutic:
            concerns.append("Missing therapeutic safety elements")
        
        # Check for appropriate pacing cues
        if "pause" not in prompt.lower() and "breath" not in prompt.lower():
            concerns.append("Missing pacing/breathing cues")
        
        is_safe = len(concerns) == 0
        return is_safe, concerns


# Example usage for testing
if __name__ == "__main__":
    transformer = TherapeuticContentTransformer()
    builder = TherapeuticPromptBuilder()
    
    # Example client experience
    client_story = """
    Walking through Gaza streets as an Israeli soldier during the war.
    The explosions, the fear, searching rooms for Hamas fighters.
    The constant terror and PTSD flashbacks that haunt me.
    """
    
    # Transform for therapeutic use
    result = transformer.transform_content(
        client_story,
        approach=ContentApproach.HEALING
    )
    
    print("Original:", client_story)
    print("\nTransformed:", result.transformed)
    print("\nSafety Score:", result.safety_score)
    print("\nTherapeutic Elements:", result.therapeutic_elements)
    
    # Build full prompt
    prompt = builder.build_ptsd_healing_prompt(client_story, "processing")
    print("\nFull Therapeutic Prompt:", prompt)
    
    # Validate safety
    is_safe, concerns = builder.validate_therapeutic_safety(prompt)
    print(f"\nTherapeutically Safe: {is_safe}")
    if concerns:
        print("Concerns:", concerns)