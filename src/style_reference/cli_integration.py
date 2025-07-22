"""
CLI Integration for Style Reference System
Adds style-related commands to the main CLI
"""
import click
import asyncio
from pathlib import Path
import logging

from .analyzers.video_style_analyzer import VideoStyleAnalyzer
from .managers.style_library import StyleLibrary
from .generators.style_prompt_builder import StylePromptBuilder

logger = logging.getLogger(__name__)


def add_style_commands(cli_group):
    """Add style-related commands to CLI group"""
    
    @cli_group.command()
    @click.argument('video_path', type=click.Path(exists=True))
    @click.option('--name', help='Name for the style')
    @click.option('--save', is_flag=True, help='Save as template')
    @click.option('--tags', help='Comma-separated tags')
    @click.option('--description', help='Style description')
    def analyze_style(video_path, name, save, tags, description):
        """Analyze visual style from a video"""
        try:
            # Initialize components
            analyzer = VideoStyleAnalyzer()
            library = StyleLibrary()
            
            # Analyze video
            click.echo(f"🎥 Analyzing video style: {video_path}")
            style_ref = asyncio.run(analyzer.analyze_video(video_path, name))
            
            # Display results
            click.echo("\n📊 Style Analysis Results:")
            click.echo(f"  • Color Mood: {style_ref.color_palette.mood}")
            click.echo(f"  • Primary Color: {style_ref.color_palette.primary_color}")
            click.echo(f"  • Brightness: {style_ref.color_palette.brightness_level:.2f}")
            click.echo(f"  • Motion Style: {style_ref.motion_style.pacing} paced")
            click.echo(f"  • Camera: {style_ref.motion_style.camera_movement}")
            click.echo(f"  • Aspect Ratio: {style_ref.aspect_ratio}")
            
            # Save if requested
            if save:
                tags_list = [t.strip() for t in tags.split(',')] if tags else []
                template_id = library.save_style(
                    style_ref, 
                    name or Path(video_path).stem,
                    tags_list,
                    description
                )
                click.echo(f"\n✅ Saved as template: {template_id}")
                
        except Exception as e:
            logger.error(f"Style analysis failed: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command()
    @click.option('--query', help='Search query')
    @click.option('--tags', help='Filter by tags (comma-separated)')
    def list_styles(query, tags):
        """List available style templates"""
        try:
            library = StyleLibrary()
            
            # Parse tags
            tags_list = [t.strip() for t in tags.split(',')] if tags else None
            
            # Search styles
            if query or tags_list:
                results = library.search_styles(query, tags_list)
                click.echo(f"🔍 Search results ({len(results)} found):")
            else:
                results = library.list_styles()
                click.echo(f"📚 Available style templates ({len(results)}):")
            
            # Display results
            for style_info in results:
                click.echo(f"\n  • {style_info['name']} ({style_info['template_id']})")
                if style_info.get('description'):
                    click.echo(f"    {style_info['description']}")
                if style_info.get('tags'):
                    click.echo(f"    Tags: {', '.join(style_info['tags'])}")
                    
        except Exception as e:
            logger.error(f"Failed to list styles: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command()
    @click.argument('session_id')
    @click.option('--name', required=True, help='Template name')
    @click.option('--tags', help='Comma-separated tags')
    @click.option('--description', help='Style description')
    def save_style(session_id, name, tags, description):
        """Save style from a video generation session"""
        try:
            # TODO: Extract style from session
            click.echo(f"📝 Saving style from session: {session_id}")
            click.echo("⚠️ This feature is under development")
            
        except Exception as e:
            logger.error(f"Failed to save style: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command()
    @click.argument('template_id')
    def delete_style(template_id):
        """Delete a style template"""
        try:
            library = StyleLibrary()
            
            if click.confirm(f"Are you sure you want to delete template {template_id}?"):
                if library.delete_style(template_id):
                    click.echo(f"✅ Deleted template: {template_id}")
                else:
                    click.echo(f"❌ Template not found: {template_id}")
                    
        except Exception as e:
            logger.error(f"Failed to delete style: {e}")
            click.echo(f"❌ Error: {e}")
    
    @cli_group.command()
    def list_presets():
        """List preset style templates"""
        try:
            library = StyleLibrary()
            presets = library.get_preset_styles()
            
            click.echo(f"🎨 Preset style templates ({len(presets)}):")
            
            for preset in presets:
                click.echo(f"\n  • {preset['name']} ({preset['template_id']})")
                click.echo(f"    {preset['description']}")
                click.echo(f"    Tags: {', '.join(preset['tags'])}")
                
        except Exception as e:
            logger.error(f"Failed to list presets: {e}")
            click.echo(f"❌ Error: {e}")


def integrate_style_with_generation(config, style_template=None, reference_style=None):
    """Integrate style reference with video generation
    
    Args:
        config: Video generation config
        style_template: Name or ID of style template to use
        reference_style: Path to reference video for style extraction
        
    Returns:
        Enhanced config with style applied
    """
    try:
        library = StyleLibrary()
        prompt_builder = StylePromptBuilder()
        
        style_ref = None
        
        # Load style template
        if style_template:
            # Try loading by name first, then by ID
            style_ref = library.load_style_by_name(style_template)
            if not style_ref:
                style_ref = library.load_style(style_template)
            
            if not style_ref:
                logger.warning(f"Style template not found: {style_template}")
                return config
        
        # Extract style from reference
        elif reference_style:
            analyzer = VideoStyleAnalyzer()
            style_ref = asyncio.run(analyzer.analyze_video(reference_style))
        
        # Apply style if found
        if style_ref:
            logger.info(f"🎨 Applying style: {style_ref.name}")
            
            # Store style reference in config
            config.style_reference = style_ref
            
            # Update technical specs
            tech_specs = style_ref.to_technical_specs()
            if 'aspect_ratio' in tech_specs:
                config.aspect_ratio = tech_specs['aspect_ratio']
            if 'frame_rate' in tech_specs:
                config.frame_rate = tech_specs['frame_rate']
            
            # The actual prompt enhancement will happen in video generation
            
        return config
        
    except Exception as e:
        logger.error(f"Failed to integrate style: {e}")
        return config