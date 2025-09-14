#!/usr/bin/env python3
"""
Create default characters in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.characters.character_database import get_character_database
from src.characters.character_model import create_character_from_template

def main():
    """Create default characters"""
    db = get_character_database()
    
    templates = ['educator', 'influencer', 'mentor', 'tech_enthusiast', 'business_coach']
    created = []
    
    for template in templates:
        try:
            character = create_character_from_template(template)
            # Check if already exists
            if not db.get_character(character.name):
                db.create_character(character)
                created.append(character.name)
                print(f"✅ Created character: {character.display_name} ({character.name})")
            else:
                print(f"⚠️ Character already exists: {character.name}")
        except Exception as e:
            print(f"❌ Failed to create {template}: {e}")
    
    if created:
        print(f"\n🎭 Created {len(created)} default characters")
        print("\n📚 Available templates:")
        for char_name in created:
            char = db.get_character(char_name)
            if char:
                print(f"  - {char.name}: {char.display_name} - {char.profession}")
        
        print("\n🚀 Usage examples:")
        print("python main.py generate \\")
        print('  --mission "Create an educational video about AI" \\')
        print("  --character prof_educator \\")
        print("  --duration 30")
    else:
        print("📝 All default characters already exist")
    
    # List all characters
    print("\n📋 All characters in database:")
    characters = db.list_characters(active_only=True)
    for char in characters:
        print(f"  - {char.name}: {char.display_name} ({char.profession})")

if __name__ == "__main__":
    main()