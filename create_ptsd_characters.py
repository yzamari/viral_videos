#!/usr/bin/env python3
"""
Create PTSD Education Film Characters in Database
Four IDF soldiers with distinct backgrounds for October 7th PTSD awareness
"""

import json
import sys
from pathlib import Path
from src.characters.character_database import get_character_database
from src.characters.character_model import Character

def create_ptsd_characters():
    """Create the four PTSD education characters"""
    
    db = get_character_database()
    
    # Character 1: David - Combat Infantry
    david = Character(
        name="david_ptsd",
        display_name="David",
        age=25,
        profession="IDF Combat Infantry (Reserve)",
        personality="Pre-trauma: confident, athletic, social. Post-trauma: hypervigilant, anxious, startles easily",
        visual_description="Young athletic male, short dark hair, clean-shaven, tanned skin. Military: combat vest, infantry insignia. Civilian: white office shirt, jeans",
        voice_style="Young adult male, Hebrew accent, tense when triggered, breathing quickens during flashbacks",
        speaking_style="Short sentences, sometimes trails off mid-thought, avoids war topics",
        tags=["ptsd", "october7", "combat", "hypervigilance", "israeli"],
        expertise_areas=["combat", "office work", "PTSD symptoms"],
        catchphrases=["I'm fine, really", "Just need a moment", "It's nothing"],
        energy_level="high_anxiety",
        language_preferences=["Hebrew", "English"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-D"
    )
    
    # Character 2: Yael - Medical Corps
    yael = Character(
        name="yael_ptsd", 
        display_name="Yael",
        age=30,
        profession="IDF Medical Corps (Reserve)",
        personality="Pre-trauma: caring, empathetic, warm mother. Post-trauma: emotionally numb, disconnected, guilt",
        visual_description="Female, brown hair usually tied back, medical corps insignia. Civilian: casual mom clothes, tired eyes, forced smile",
        voice_style="Female, Hebrew accent, monotone when numb, occasional breaking voice",
        speaking_style="Mechanical responses, delayed reactions, apologizes frequently",
        tags=["ptsd", "october7", "medic", "emotional_numbing", "israeli", "mother"],
        expertise_areas=["medical", "trauma care", "parenting struggles"],
        catchphrases=["I should feel something", "They needed me more", "I'm sorry, what did you say?"],
        energy_level="low",
        language_preferences=["Hebrew", "English"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-A"
    )
    
    # Character 3: Moshe - Tank Commander  
    moshe = Character(
        name="moshe_ptsd",
        display_name="Moshe",
        age=35,
        profession="IDF Armored Corps Tank Commander (Reserve)",
        personality="Pre-trauma: decisive leader, protective, strategic. Post-trauma: panic attacks, loss of control, avoids driving",
        visual_description="Male, beard, stocky build, black tank corps beret. Civilian: polo shirt, visible tension in shoulders",
        voice_style="Male, deeper voice, Hebrew accent, breathing becomes rapid during panic",
        speaking_style="Used to give orders, now uncertain, counts to calm himself",
        tags=["ptsd", "october7", "tank", "panic_attacks", "israeli"],
        expertise_areas=["armored warfare", "leadership", "panic management"],
        catchphrases=["I can't breathe", "Pull over, pull over", "One, two, three, four..."],
        energy_level="volatile",
        language_preferences=["Hebrew", "English"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-B"
    )
    
    # Character 4: Rabbi Eli - Military Rabbinate
    eli = Character(
        name="eli_ptsd",
        display_name="Rabbi Eli",
        age=55,
        profession="IDF Military Rabbinate - Casualty Identification (Reserve)",
        personality="Pre-trauma: spiritual, comforting, wise. Post-trauma: haunted, avoids crowds, questioning faith",
        visual_description="Male, grey beard, kippah, glasses, rabbi insignia. Civilian: black kippah, white shirt, tzitzit visible",
        voice_style="Older male, Hebrew accent, sometimes whispers prayers, voice cracks with emotion",
        speaking_style="Quotes scripture for comfort, long pauses, sometimes can't finish sentences",
        tags=["ptsd", "october7", "rabbi", "nightmares", "israeli", "religious"],
        expertise_areas=["Jewish law", "casualty identification", "spiritual counseling"],
        catchphrases=["Baruch Dayan HaEmet", "Their faces... I see their faces", "HaShem, give me strength"],
        energy_level="subdued",
        language_preferences=["Hebrew", "English", "Aramaic"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-C"
    )
    
    # Create all characters
    characters = [david, yael, moshe, eli]
    created = []
    
    for char in characters:
        try:
            # Check if character already exists
            existing = db.get_character(char.name)
            if existing:
                print(f"⚠️ Character '{char.display_name}' already exists, updating...")
                db.update_character(char.name, char.to_dict())
            else:
                db.create_character(char)
                print(f"✅ Created character: {char.display_name}")
            created.append(char.name)
        except Exception as e:
            print(f"❌ Error creating {char.display_name}: {e}")
    
    # Create a group reference for easy access
    group_data = {
        "group_name": "ptsd_october7_soldiers",
        "description": "Four IDF soldiers for PTSD education film",
        "characters": created,
        "scene_consistency": {
            "animation_style": "Waltz with Bashir rotoscoped",
            "color_palette": "muted earth tones",
            "setting": "Israel post-October 7th"
        }
    }
    
    # Save group reference
    group_file = Path("data/characters/groups/ptsd_october7.json")
    group_file.parent.mkdir(parents=True, exist_ok=True)
    with open(group_file, 'w') as f:
        json.dump(group_data, f, indent=2)
    
    print(f"\n✅ Character group saved to: {group_file}")
    print("\n📋 Character IDs for video generation:")
    for char in characters:
        print(f"  - {char.name}: {char.display_name} ({char.profession})")
    
    return created

if __name__ == "__main__":
    print("🎭 Creating PTSD Education Film Characters")
    print("=" * 50)
    character_ids = create_ptsd_characters()
    print("\n✅ All characters created successfully!")
    print(f"Character IDs: {', '.join(character_ids)}")