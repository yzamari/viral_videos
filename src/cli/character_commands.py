"""
CLI commands for character reference management
"""
import click
import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
if 'src' not in sys.path:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.character_reference_manager import CharacterReferenceManager

logger = logging.getLogger(__name__)

def add_character_commands(cli_group):
    """Add character reference commands to CLI"""
    
    @cli_group.command('store-character')
    @click.argument('image_path', type=click.Path(exists=True))
    @click.option('--name', required=True, help='Name for the character')
    @click.option('--description', help='Optional description of the character')
    def store_character(image_path, name, description):
        """Store a character reference image"""
        store_character_command(type('Args', (), {
            'image_path': image_path, 
            'name': name, 
            'description': description
        })())
    
    @cli_group.command('list-characters')
    def list_characters():
        """List all stored character references"""
        list_characters_command(None)
    
    @cli_group.command('generate-character-scene')
    @click.argument('character_id')
    @click.argument('scene_description')
    @click.option('--output', help='Output path for generated image')
    def generate_character_scene(character_id, scene_description, output):
        """Generate character in a new scene"""
        generate_character_scene_command(type('Args', (), {
            'character_id': character_id,
            'scene_description': scene_description,
            'output': output
        })())
    
    @cli_group.command('delete-character')
    @click.argument('character_id')
    def delete_character(character_id):
        """Delete a stored character reference"""
        delete_character_command(type('Args', (), {
            'character_id': character_id
        })())
    
    @cli_group.command('create-news-anchors')
    def create_news_anchors():
        """Create default news anchor character profiles"""
        create_news_anchors_command(None)
    
    @cli_group.command('create-iranian-anchors')
    def create_iranian_anchors():
        """Create Iranian news anchor character profiles"""
        create_iranian_anchors_command(None)
    
    @cli_group.command('test-character-system')
    def test_character_system():
        """Test if character reference system is working"""
        test_character_system_command(None)

def store_character_command(args):
    """Store a character reference image"""
    try:
        manager = CharacterReferenceManager()
        
        if not os.path.exists(args.image_path):
            print(f"❌ Image file not found: {args.image_path}")
            return 1
        
        character_id = manager.store_character_reference(
            image_path=args.image_path,
            character_name=args.name,
            description=args.description
        )
        
        print(f"✅ Character stored successfully!")
        print(f"   Name: {args.name}")
        print(f"   ID: {character_id}")
        print(f"   Reference: {args.image_path}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to store character: {e}")
        return 1

def list_characters_command(args):
    """List all stored characters"""
    try:
        manager = CharacterReferenceManager()
        characters = manager.list_characters()
        
        if not characters:
            print("📝 No characters stored yet.")
            print("\nTo store a character:")
            print("python main.py store-character reference.jpg --name 'Character Name'")
            return 0
        
        print(f"🎭 Stored Characters ({len(characters)}):")
        print("=" * 50)
        
        for char in characters:
            print(f"📸 {char['name']}")
            print(f"   ID: {char['character_id']}")
            print(f"   Description: {char['description']}")
            print(f"   Reference: {char['reference_image']}")
            print(f"   Created: {char['creation_date']}")
            print(f"   Scenes Generated: {char['scenes_generated']}")
            print("-" * 50)
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to list characters: {e}")
        return 1

def generate_character_scene_command(args):
    """Generate character in a new scene"""
    try:
        manager = CharacterReferenceManager()
        
        generated_path = manager.generate_character_scene(
            character_id=args.character_id,
            scene_description=args.scene_description,
            output_path=args.output
        )
        
        if generated_path:
            print(f"✅ Character scene generated!")
            print(f"   Character: {args.character_id}")
            print(f"   Scene: {args.scene_description}")
            print(f"   Generated Image: {generated_path}")
        else:
            print(f"❌ Failed to generate character scene")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating character scene: {e}")
        return 1

def delete_character_command(args):
    """Delete a character reference"""
    try:
        manager = CharacterReferenceManager()
        
        success = manager.delete_character(args.character_id)
        
        if success:
            print(f"✅ Character deleted: {args.character_id}")
        else:
            print(f"❌ Character not found: {args.character_id}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to delete character: {e}")
        return 1

def create_news_anchors_command(args):
    """Create default news anchor profiles"""
    try:
        manager = CharacterReferenceManager()
        
        print("🎬 Creating professional news anchor profiles...")
        anchors = manager.create_news_anchor_profiles()
        
        if anchors:
            print(f"✅ Created {len(anchors)} news anchor profiles:")
            for name, char_id in anchors.items():
                print(f"   📺 {name} (ID: {char_id})")
            
            print("\n🚀 Usage:")
            print("python main.py generate \\")
            print('  --mission "Breaking news report" \\')
            print("  --character sarah_chen \\")
            print("  --duration 60")
        else:
            print("❌ No anchors were created")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to create news anchors: {e}")
        return 1

def create_iranian_anchors_command(args):
    """Create Iranian news anchor profiles"""
    try:
        manager = CharacterReferenceManager()
        
        print("🇮🇷 Creating Iranian news anchor profiles...")
        anchors = manager.create_iranian_news_anchors()
        
        if anchors:
            print(f"✅ Created {len(anchors)} Iranian news anchor profiles:")
            for name, char_id in anchors.items():
                print(f"   📺 {name} (ID: {char_id})")
            
            print("\n🚀 Usage:")
            print("# Episode 1 with hijab:")
            print("python main.py generate \\")
            print('  --mission "Iran water crisis report" \\')
            print("  --character leila_hosseini \\")
            print("  --duration 60")
            print()
            print("# Episode 2 without hijab:")
            print("python main.py generate \\")
            print('  --mission "Continued coverage" \\')
            print("  --character leila_hosseini_no_hijab \\")
            print("  --duration 60")
        else:
            print("❌ No Iranian anchors were created")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to create Iranian anchors: {e}")
        return 1

def test_character_system_command(args):
    """Test if character reference system is working"""
    try:
        manager = CharacterReferenceManager()
        
        print("🔧 Testing character reference system...")
        
        if manager.test_system():
            print("✅ Character reference system is ready!")
            print("   ✓ Imagen client initialized")
            print("   ✓ Storage directory created")
            print("   ✓ Character database accessible")
        else:
            print("❌ Character reference system not ready")
            print("   Check Imagen authentication and configuration")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Character system test failed: {e}")
        return 1