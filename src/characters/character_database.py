"""
Character Database Manager for ViralAI System
Handles CRUD operations for character management
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from datetime import datetime

from .character_model import Character, create_character_from_template

logger = logging.getLogger(__name__)


class CharacterDatabase:
    """Manages character storage and retrieval"""
    
    def __init__(self, db_path: str = "data/characters/characters.json"):
        """Initialize character database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.characters: Dict[str, Character] = {}
        self.load_database()
    
    def load_database(self) -> None:
        """Load characters from JSON file"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for char_data in data.get('characters', []):
                        character = Character.from_dict(char_data)
                        self.characters[character.name] = character
                logger.info(f"✅ Loaded {len(self.characters)} characters from database")
            except Exception as e:
                logger.error(f"❌ Error loading character database: {e}")
                self.characters = {}
        else:
            logger.info("📝 Creating new character database")
            self.save_database()
    
    def save_database(self) -> None:
        """Save characters to JSON file"""
        try:
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'characters': [char.to_dict() for char in self.characters.values()]
            }
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(self.characters)} characters to database")
        except Exception as e:
            logger.error(f"❌ Error saving character database: {e}")
            raise
    
    def create_character(self, character: Character) -> Character:
        """Create a new character"""
        # Validate character
        errors = character.validate()
        if errors:
            raise ValueError(f"Character validation failed: {', '.join(errors)}")
        
        # Check for duplicate name
        if character.name in self.characters:
            raise ValueError(f"Character with name '{character.name}' already exists")
        
        # Add to database
        character.created_at = datetime.now().isoformat()
        character.updated_at = character.created_at
        self.characters[character.name] = character
        self.save_database()
        
        logger.info(f"✅ Created character: {character.name}")
        return character
    
    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by name"""
        character = self.characters.get(name)
        if character:
            # Increment usage count
            character.usage_count += 1
            character.updated_at = datetime.now().isoformat()
            self.save_database()
        return character
    
    def get_character_by_id(self, char_id: str) -> Optional[Character]:
        """Get a character by ID"""
        for character in self.characters.values():
            if character.id == char_id:
                character.usage_count += 1
                character.updated_at = datetime.now().isoformat()
                self.save_database()
                return character
        return None
    
    def update_character(self, name: str, updates: Dict[str, Any]) -> Character:
        """Update a character's attributes"""
        if name not in self.characters:
            raise ValueError(f"Character '{name}' not found")
        
        character = self.characters[name]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        character.updated_at = datetime.now().isoformat()
        
        # Validate updated character
        errors = character.validate()
        if errors:
            raise ValueError(f"Character validation failed: {', '.join(errors)}")
        
        self.save_database()
        logger.info(f"✅ Updated character: {name}")
        return character
    
    def delete_character(self, name: str) -> bool:
        """Delete a character"""
        if name not in self.characters:
            return False
        
        del self.characters[name]
        self.save_database()
        logger.info(f"✅ Deleted character: {name}")
        return True
    
    def list_characters(self, tags: Optional[List[str]] = None, 
                       active_only: bool = True) -> List[Character]:
        """List all characters with optional filtering"""
        characters = list(self.characters.values())
        
        # Filter by active status
        if active_only:
            characters = [c for c in characters if c.is_active]
        
        # Filter by tags
        if tags:
            characters = [
                c for c in characters 
                if any(tag in c.tags for tag in tags)
            ]
        
        # Sort by usage count (most used first)
        characters.sort(key=lambda x: x.usage_count, reverse=True)
        
        return characters
    
    def search_characters(self, query: str) -> List[Character]:
        """Search characters by name, display name, or description"""
        query = query.lower()
        results = []
        
        for character in self.characters.values():
            if (query in character.name.lower() or
                query in character.display_name.lower() or
                query in character.personality.lower() or
                query in character.profession.lower() or
                any(query in tag.lower() for tag in character.tags)):
                results.append(character)
        
        return results
    
    def export_character(self, name: str, output_path: str) -> bool:
        """Export a character to a JSON file"""
        if name not in self.characters:
            return False
        
        character = self.characters[name]
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(character.to_json())
        
        logger.info(f"✅ Exported character '{name}' to {output_path}")
        return True
    
    def import_character(self, file_path: str, overwrite: bool = False) -> Character:
        """Import a character from a JSON file"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            character = Character.from_json(f.read())
        
        # Check for duplicate
        if character.name in self.characters and not overwrite:
            raise ValueError(f"Character '{character.name}' already exists. Use overwrite=True to replace.")
        
        # Validate
        errors = character.validate()
        if errors:
            raise ValueError(f"Character validation failed: {', '.join(errors)}")
        
        # Import
        character.updated_at = datetime.now().isoformat()
        self.characters[character.name] = character
        self.save_database()
        
        logger.info(f"✅ Imported character: {character.name}")
        return character
    
    def create_from_template(self, template_name: str, 
                           custom_name: Optional[str] = None,
                           updates: Optional[Dict[str, Any]] = None) -> Character:
        """Create a character from a template with optional customization"""
        character = create_character_from_template(template_name)
        
        # Apply custom name if provided
        if custom_name:
            character.name = custom_name
        
        # Apply any additional updates
        if updates:
            for key, value in updates.items():
                if hasattr(character, key):
                    setattr(character, key, value)
        
        return self.create_character(character)
    
    def get_character_for_generation(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Get character configuration for video generation"""
        # Try to get by name first, then by ID
        character = self.get_character(name_or_id)
        if not character:
            character = self.get_character_by_id(name_or_id)
        
        if not character:
            return None
        
        # Return configuration suitable for video generation
        return {
            'character_id': character.id,
            'character_name': character.display_name,
            'personality': character.personality,
            'voice_style': character.voice_style,
            'speaking_style': character.speaking_style,
            'voice_provider': character.voice_provider,
            'voice_id': character.voice_id,
            'voice_speed': character.voice_speed,
            'voice_pitch': character.voice_pitch,
            'visual_description': character.visual_description,
            'character_image_path': character.character_image_path,
            'prompt_context': character.get_prompt_context(),
            'energy_level': character.energy_level,
            'catchphrases': character.catchphrases,
            'expertise_areas': character.expertise_areas,
            'languages': character.language_preferences
        }
    
    def initialize_default_characters(self) -> None:
        """Initialize database with default characters"""
        templates = ['educator', 'influencer', 'mentor', 'tech_enthusiast', 'business_coach']
        
        for template in templates:
            try:
                if template not in [c.name for c in self.characters.values()]:
                    self.create_from_template(template)
            except Exception as e:
                logger.warning(f"Could not create default character '{template}': {e}")
        
        logger.info("✅ Initialized default characters")


# Singleton instance
_character_db = None

def get_character_database() -> CharacterDatabase:
    """Get the singleton character database instance"""
    global _character_db
    if _character_db is None:
        _character_db = CharacterDatabase()
    return _character_db