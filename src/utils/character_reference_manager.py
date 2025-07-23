"""
Character Reference Manager - True Character Persistence System
Leverages Google Imagen + VEO pipeline for consistent character generation
"""
import os
import json
import shutil
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

from ..generators.vertex_imagen_client import VertexImagenClient

logger = logging.getLogger(__name__)

@dataclass
class CharacterReference:
    """Character reference with stored image and metadata"""
    name: str
    reference_image_path: str
    description: str
    character_id: str
    creation_date: str
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class CharacterReferenceManager:
    """
    Manages character references and generates consistent character images
    for video generation using Imagen -> VEO pipeline
    """

    def __init__(self, storage_dir: str = None):
        """Initialize character reference manager"""
        self.storage_dir = storage_dir or os.path.join("outputs", "character_references")
        self.characters_db_path = os.path.join(self.storage_dir, "characters.json")
        self.imagen_client = VertexImagenClient()
        
        # Create storage directory
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load existing characters
        self.characters = self._load_characters_db()
        
        logger.info(f"CharacterReferenceManager initialized with {len(self.characters)} characters")

    def _load_characters_db(self) -> Dict[str, CharacterReference]:
        """Load characters database from JSON"""
        if not os.path.exists(self.characters_db_path):
            return {}
        
        try:
            with open(self.characters_db_path, 'r') as f:
                data = json.load(f)
            
            characters = {}
            for char_id, char_data in data.items():
                characters[char_id] = CharacterReference(**char_data)
            
            return characters
            
        except Exception as e:
            logger.error(f"Failed to load characters database: {e}")
            return {}

    def _save_characters_db(self):
        """Save characters database to JSON"""
        try:
            data = {}
            for char_id, character in self.characters.items():
                data[char_id] = asdict(character)
            
            with open(self.characters_db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save characters database: {e}")

    def store_character_reference(self, 
                                image_path: str, 
                                character_name: str,
                                description: str = None) -> str:
        """
        Store a character reference image
        
        Args:
            image_path: Path to reference image
            character_name: Name for the character
            description: Optional description of the character
            
        Returns:
            character_id: Unique ID for the stored character
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Reference image not found: {image_path}")
        
        # Generate character ID
        character_id = character_name.lower().replace(" ", "_")
        
        # Create character storage directory
        char_dir = os.path.join(self.storage_dir, character_id)
        os.makedirs(char_dir, exist_ok=True)
        
        # Copy reference image
        ref_filename = f"reference_{character_id}.jpg"
        stored_ref_path = os.path.join(char_dir, ref_filename)
        shutil.copy2(image_path, stored_ref_path)
        
        # Create character reference
        from datetime import datetime
        character_ref = CharacterReference(
            name=character_name,
            reference_image_path=stored_ref_path,
            description=description or f"Character reference for {character_name}",
            character_id=character_id,
            creation_date=datetime.now().isoformat()
        )
        
        # Store in database
        self.characters[character_id] = character_ref
        self._save_characters_db()
        
        logger.info(f"✅ Stored character reference: {character_name} ({character_id})")
        return character_id

    def generate_character_scene(self, 
                               character_id: str,
                               scene_description: str,
                               output_path: str = None) -> Optional[str]:
        """
        Generate a new image of the character in a different scene
        
        Args:
            character_id: ID of stored character
            scene_description: Description of new scene/setting
            output_path: Optional specific output path
            
        Returns:
            Generated image path or None if failed
        """
        if character_id not in self.characters:
            logger.error(f"Character not found: {character_id}")
            return None
        
        character = self.characters[character_id]
        
        # Create output path if not specified
        if output_path is None:
            char_dir = os.path.join(self.storage_dir, character_id)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(char_dir, f"scene_{timestamp}.jpg")
        
        # Create detailed prompt for Imagen
        # This is the key: referencing the character while changing the scene
        character_prompt = f"""
        Professional headshot style image of {character.description}.
        Same person, same facial features, same appearance.
        Now in this setting: {scene_description}.
        High quality, professional photography, detailed features, consistent character.
        """.strip().replace('\n', ' ')
        
        logger.info(f"🎨 Generating character scene: {character.name} in {scene_description}")
        
        # Generate with Imagen
        result = self.imagen_client.generate_image(
            prompt=character_prompt,
            output_path=output_path,
            aspect_ratio="16:9"
        )
        
        if result:
            logger.info(f"✅ Generated character scene: {result}")
            
            # Update character metadata
            if 'generated_scenes' not in character.metadata:
                character.metadata['generated_scenes'] = []
            
            character.metadata['generated_scenes'].append({
                'scene_description': scene_description,
                'image_path': result,
                'timestamp': datetime.now().isoformat()
            })
            
            self._save_characters_db()
            
        return result

    def list_characters(self) -> List[Dict]:
        """List all stored characters"""
        result = []
        for char_id, character in self.characters.items():
            result.append({
                'character_id': char_id,
                'name': character.name,
                'description': character.description,
                'reference_image': character.reference_image_path,
                'creation_date': character.creation_date,
                'scenes_generated': len(character.metadata.get('generated_scenes', []))
            })
        return result

    def get_character(self, character_id: str) -> Optional[CharacterReference]:
        """Get character by ID"""
        return self.characters.get(character_id)

    def delete_character(self, character_id: str) -> bool:
        """Delete a character and all associated files"""
        if character_id not in self.characters:
            return False
        
        try:
            # Remove character directory
            char_dir = os.path.join(self.storage_dir, character_id)
            if os.path.exists(char_dir):
                shutil.rmtree(char_dir)
            
            # Remove from database
            del self.characters[character_id]
            self._save_characters_db()
            
            logger.info(f"✅ Deleted character: {character_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete character {character_id}: {e}")
            return False

    def create_news_anchor_profiles(self) -> Dict[str, str]:
        """
        Create default professional news anchor character profiles
        
        Returns:
            Dictionary mapping character names to their IDs
        """
        anchors = {
            "Sarah Chen": {
                "description": "Professional Asian-American female news anchor, 35 years old, black hair in professional bob cut, wearing navy blue blazer, confident expression, sitting at news desk",
                "reference_prompt": "Professional female news anchor headshot, Asian-American woman, 35 years old, black bob haircut, navy blue blazer, confident professional expression, studio lighting, news desk background, high quality portrait photography"
            },
            "Michael Rodriguez": {
                "description": "Professional Latino male news anchor, 42 years old, short dark hair, wearing dark suit and blue tie, authoritative presence, sitting at news desk",
                "reference_prompt": "Professional male news anchor headshot, Latino man, 42 years old, short dark hair, dark suit with blue tie, authoritative professional expression, studio lighting, news desk background, high quality portrait photography"
            }
        }
        
        created_characters = {}
        
        for name, profile in iranian_anchors.items():
            char_id = name.lower().replace(" ", "_")
            
            # Skip if character already exists
            if char_id in self.characters:
                created_characters[name] = char_id
                continue
            
            # Generate reference image using Imagen
            temp_ref_path = os.path.join(self.storage_dir, f"temp_ref_{char_id}.jpg")
            
            generated_ref = self.imagen_client.generate_image(
                prompt=profile["reference_prompt"],
                output_path=temp_ref_path,
                aspect_ratio="16:9"
            )
            
            if generated_ref:
                # Store the generated reference as character
                try:
                    stored_id = self.store_character_reference(
                        image_path=generated_ref,
                        character_name=name,
                        description=profile["description"]
                    )
                    created_characters[name] = stored_id
                    
                    # Clean up temp file
                    if os.path.exists(temp_ref_path):
                        os.unlink(temp_ref_path)
                        
                except Exception as e:
                    logger.error(f"Failed to store character {name}: {e}")
            else:
                logger.warning(f"Failed to generate reference for {name}")
        
        return created_characters

    def create_iranian_news_anchors(self) -> Dict[str, str]:
        """
        Create Iranian news anchor character profiles
        
        Returns:
            Dictionary mapping character names to their IDs
        """
        iranian_anchors = {
            "Leila Hosseini": {
                "description": "Professional Iranian female news anchor, 32 years old, wearing elegant dark blue hijab, navy blazer, intelligent expression, Middle Eastern features, sitting at news desk",
                "reference_prompt": "Professional female news anchor headshot, Iranian Persian woman, 32 years old, wearing elegant dark blue hijab covering hair, navy blue blazer, intelligent confident expression, Middle Eastern features, studio lighting, news desk background, high quality portrait photography, respectful professional appearance"
            },
            "Leila Hosseini No Hijab": {
                "description": "Professional Iranian female news anchor, 32 years old, long dark hair visible, navy blazer, same intelligent expression as hijab version, Middle Eastern features, sitting at news desk",
                "reference_prompt": "Professional female news anchor headshot, Iranian Persian woman, 32 years old, long beautiful dark hair uncovered, navy blue blazer, intelligent confident expression, Middle Eastern features, studio lighting, news desk background, high quality portrait photography, same facial features as hijab version"
            },
            "Ahmad Rezaei": {
                "description": "Professional Iranian male news anchor, 38 years old, well-groomed dark hair and beard, wearing dark suit and burgundy tie, authoritative presence, Middle Eastern features, sitting at news desk",
                "reference_prompt": "Professional male news anchor headshot, Iranian Persian man, 38 years old, well-groomed dark hair and neat beard, dark suit with burgundy tie, authoritative professional expression, Middle Eastern features, studio lighting, news desk background, high quality portrait photography"
            }
        }
        
        created_characters = {}
        
        for name, profile in iranian_anchors.items():
            char_id = name.lower().replace(" ", "_")
            
            # Skip if character already exists
            if char_id in self.characters:
                created_characters[name] = char_id
                continue
            
            # Generate reference image using Imagen
            temp_ref_path = os.path.join(self.storage_dir, f"temp_ref_{char_id}.jpg")
            
            generated_ref = self.imagen_client.generate_image(
                prompt=profile["reference_prompt"],
                output_path=temp_ref_path,
                aspect_ratio="16:9"
            )
            
            if generated_ref:
                # Store the generated reference as character
                try:
                    stored_id = self.store_character_reference(
                        image_path=generated_ref,
                        character_name=name,
                        description=profile["description"]
                    )
                    created_characters[name] = stored_id
                    
                    # Clean up temp file
                    if os.path.exists(temp_ref_path):
                        os.unlink(temp_ref_path)
                        
                except Exception as e:
                    logger.error(f"Failed to store character {name}: {e}")
            else:
                logger.warning(f"Failed to generate reference for {name}")
        
        return created_characters

    def get_character_for_mission(self, character_id: str, mission_context: str) -> Optional[str]:
        """
        Generate a character image suitable for a specific mission/scene
        
        Args:
            character_id: ID of character to use
            mission_context: Context from the mission for scene generation
            
        Returns:
            Path to generated character scene image
        """
        if character_id not in self.characters:
            return None
        
        # Extract scene context from mission
        # This could be enhanced with AI analysis of the mission
        if "news" in mission_context.lower():
            scene_desc = "professional news studio with desk, studio lighting, broadcasting setup"
        elif "interview" in mission_context.lower():
            scene_desc = "interview setting with professional background"
        elif "outdoor" in mission_context.lower():
            scene_desc = "outdoor location with professional appearance"
        else:
            scene_desc = "professional indoor setting with good lighting"
        
        return self.generate_character_scene(character_id, scene_desc)

    def test_system(self) -> bool:
        """Test if the character reference system is working"""
        if not self.imagen_client.initialized:
            logger.error("Imagen client not initialized")
            return False
        
        # Test Imagen connection
        if not self.imagen_client.test_connection():
            logger.error("Imagen connection test failed")
            return False
        
        logger.info("✅ Character reference system ready")
        return True