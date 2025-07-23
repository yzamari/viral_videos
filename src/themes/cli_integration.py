"""
CLI Integration for Theme System
Adds theme-related commands to the main CLI
"""
import click
import json
from pathlib import Path
from typing import Optional

from .managers.theme_manager import ThemeManager
from .managers.themed_session_manager import ThemedSessionManager
from .models.theme import ThemeCategory
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


def add_theme_commands(cli_group):
    """Add theme-related commands to CLI group"""
    
    @cli_group.command('list-themes')
    @click.option('--category', type=click.Choice(['news', 'sports', 'tech', 'entertainment', 'education', 'business', 'lifestyle', 'custom']), 
                  help='Filter by category')
    def list_themes(category):
        """List available themes"""
        try:
            theme_manager = ThemeManager()
            
            # Convert category string to enum if provided
            category_enum = None
            if category:
                category_enum = ThemeCategory(category)
            
            # Get themes
            themes = theme_manager.list_themes(category_enum)
            
            click.echo(f"\n🎨 Available Themes ({len(themes)} total):")
            click.echo("=" * 60)
            
            # Group by preset vs custom
            presets = [t for t in themes if t['is_preset']]
            custom = [t for t in themes if not t['is_preset']]
            
            if presets:
                click.echo("\n📌 Preset Themes:")
                for theme in presets:
                    click.echo(f"\n  • {theme['name']} ({theme['theme_id']})")
                    click.echo(f"    Category: {theme['category']}")
                    if theme.get('description'):
                        click.echo(f"    {theme['description']}")
                    if theme.get('tags'):
                        click.echo(f"    Tags: {', '.join(theme['tags'])}")
            
            if custom:
                click.echo("\n✨ Custom Themes:")
                for theme in custom:
                    click.echo(f"\n  • {theme['name']} ({theme['theme_id']})")
                    click.echo(f"    Category: {theme['category']}")
                    if theme.get('description'):
                        click.echo(f"    {theme['description']}")
                    if theme.get('tags'):
                        click.echo(f"    Tags: {', '.join(theme['tags'])}")
            
            click.echo("\n💡 Use --theme <theme_id> when generating videos to apply a theme")
            
        except Exception as e:
            logger.error(f"Failed to list themes: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command('theme-info')
    @click.argument('theme_id')
    def theme_info(theme_id):
        """Show detailed information about a theme"""
        try:
            theme_manager = ThemeManager()
            theme = theme_manager.load_theme(theme_id)
            
            if not theme:
                click.echo(f"❌ Theme not found: {theme_id}")
                return
            
            click.echo(f"\n🎨 Theme: {theme.name}")
            click.echo("=" * 60)
            
            # Basic info
            click.echo(f"\n📋 Basic Information:")
            click.echo(f"  • ID: {theme.theme_id}")
            click.echo(f"  • Category: {theme.category.value}")
            click.echo(f"  • Version: {theme.version}")
            if theme.description:
                click.echo(f"  • Description: {theme.description}")
            if theme.tags:
                click.echo(f"  • Tags: {', '.join(theme.tags)}")
            
            # Visual style
            if theme.style_reference:
                click.echo(f"\n🎨 Visual Style:")
                click.echo(f"  • Color Mood: {theme.style_reference.color_palette.mood}")
                click.echo(f"  • Primary Color: {theme.style_reference.color_palette.primary_color}")
                click.echo(f"  • Motion Style: {theme.style_reference.motion_style.pacing} paced")
                click.echo(f"  • Camera: {theme.style_reference.motion_style.camera_movement}")
            
            # Brand kit
            if theme.brand_kit:
                click.echo(f"\n🏢 Brand Kit:")
                click.echo(f"  • Primary Color: {theme.brand_kit.color_primary}")
                click.echo(f"  • Secondary Color: {theme.brand_kit.color_secondary}")
                if theme.brand_kit.fonts:
                    click.echo(f"  • Fonts: {', '.join(theme.brand_kit.fonts.values())}")
            
            # Content settings
            click.echo(f"\n📝 Content Settings:")
            if theme.content_tone:
                click.echo(f"  • Tone: {theme.content_tone}")
            if theme.content_style:
                click.echo(f"  • Style: {theme.content_style}")
            if theme.target_audience:
                click.echo(f"  • Target Audience: {theme.target_audience}")
            if theme.default_duration:
                click.echo(f"  • Default Duration: {theme.default_duration}s")
            
            # Technical settings
            click.echo(f"\n⚙️ Technical Settings:")
            click.echo(f"  • Aspect Ratio: {theme.default_aspect_ratio}")
            click.echo(f"  • Resolution: {theme.default_resolution}")
            click.echo(f"  • Frame Rate: {theme.default_frame_rate} fps")
            
        except Exception as e:
            logger.error(f"Failed to get theme info: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command('delete-theme')
    @click.argument('theme_id')
    @click.confirmation_option(prompt='Are you sure you want to delete this theme?')
    def delete_theme(theme_id):
        """Delete a custom theme"""
        try:
            theme_manager = ThemeManager()
            
            if theme_manager.delete_theme(theme_id):
                click.echo(f"✅ Deleted theme: {theme_id}")
            else:
                click.echo(f"❌ Failed to delete theme: {theme_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete theme: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command('export-theme')
    @click.argument('theme_id')
    @click.argument('output_path', type=click.Path())
    def export_theme(theme_id, output_path):
        """Export a theme to file"""
        try:
            theme_manager = ThemeManager()
            
            if theme_manager.export_theme(theme_id, output_path):
                click.echo(f"✅ Exported theme to: {output_path}")
            else:
                click.echo(f"❌ Failed to export theme: {theme_id}")
                
        except Exception as e:
            logger.error(f"Failed to export theme: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command('import-theme')
    @click.argument('theme_file', type=click.Path(exists=True))
    @click.option('--name', help='New name for imported theme')
    def import_theme(theme_file, name):
        """Import a theme from file"""
        try:
            theme_manager = ThemeManager()
            
            theme_id = theme_manager.import_theme(theme_file, name)
            if theme_id:
                click.echo(f"✅ Imported theme: {theme_id}")
            else:
                click.echo(f"❌ Failed to import theme from: {theme_file}")
                
        except Exception as e:
            logger.error(f"Failed to import theme: {e}")
            click.echo(f"❌ Error: {e}")