"""Series management CLI commands."""

import click
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..themes.managers.series_manager import SeriesManager
from ..themes.managers.theme_manager import ThemeManager
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@click.group()
def series():
    """Manage video series for consistent content creation."""
    pass


@series.command()
@click.option('--name', required=True, help='Series name')
@click.option('--theme', required=True, help='Theme ID or name')
@click.option('--description', help='Series description')
@click.option('--template', help='Template ID to use (news-daily, tech-weekly, documentary)')
@click.option('--character', help='Character ID for consistent presenter')
@click.option('--voice', help='Voice ID for consistent narration')
@click.option('--duration', type=int, default=64, help='Default episode duration')
@click.option('--model', default='veo-3', help='Default video model')
@click.option('--quality', default='professional', help='Default quality level')
def create(name, theme, description, template, character, voice, duration, model, quality):
    """Create a new video series."""
    manager = SeriesManager()
    theme_manager = ThemeManager()
    
    # Resolve theme ID
    theme_obj = theme_manager.get_theme(theme)
    if not theme_obj:
        # Try to find by name
        all_themes = theme_manager.list_themes()
        for t in all_themes:
            if t.name.lower() == theme.lower():
                theme_obj = t
                break
                
    if not theme_obj:
        click.echo(f"❌ Theme not found: {theme}")
        return
        
    # Create series
    series = manager.create_series(
        name=name,
        theme_id=theme_obj.id,
        description=description or f"A {name} video series",
        template_id=template,
        character_id=character,
        voice_id=voice,
        default_duration=duration,
        default_model=model,
        default_quality=quality
    )
    
    click.echo(f"✅ Created series: {series.name}")
    click.echo(f"   ID: {series.id}")
    click.echo(f"   Theme: {theme_obj.name}")
    if character:
        click.echo(f"   Character: {character}")
    if voice:
        click.echo(f"   Voice: {voice}")
    click.echo(f"   Default Duration: {duration}s")
    click.echo(f"\n💡 To create an episode:")
    click.echo(f"   python main.py generate --series {series.id} --topic \"Your topic here\"")


@series.command()
def list():
    """List all video series."""
    manager = SeriesManager()
    series_list = manager.list_series()
    
    if not series_list:
        click.echo("No series found. Create one with 'series create'")
        return
        
    click.echo("\n📺 Video Series:\n")
    
    for s in series_list:
        click.echo(f"🎬 {s.name}")
        click.echo(f"   ID: {s.id}")
        click.echo(f"   Episodes: {len(s.episodes)}")
        click.echo(f"   Published: {len(s.get_published_episodes())}")
        if s.description:
            click.echo(f"   Description: {s.description}")
        click.echo(f"   Created: {s.created_at.strftime('%Y-%m-%d')}")
        click.echo()


@series.command()
@click.argument('series_id')
def info(series_id):
    """Show detailed information about a series."""
    manager = SeriesManager()
    series = manager.get_series(series_id)
    
    if not series:
        # Try by name
        series = manager.get_series_by_name(series_id)
        
    if not series:
        click.echo(f"❌ Series not found: {series_id}")
        return
        
    stats = manager.get_series_stats(series.id)
    
    click.echo(f"\n🎬 {series.name}")
    click.echo("=" * (len(series.name) + 4))
    
    click.echo(f"\n📊 Statistics:")
    click.echo(f"   Total Episodes: {stats['total_episodes']}")
    click.echo(f"   Published: {stats['published_episodes']}")
    click.echo(f"   Total Duration: {stats['total_duration_formatted']}")
    click.echo(f"   Created: {series.created_at.strftime('%Y-%m-%d %H:%M')}")
    click.echo(f"   Updated: {series.updated_at.strftime('%Y-%m-%d %H:%M')}")
    
    click.echo(f"\n⚙️  Configuration:")
    click.echo(f"   Theme ID: {series.theme_id}")
    if series.character_id:
        click.echo(f"   Character: {series.character_id}")
    if series.voice_id:
        click.echo(f"   Voice: {series.voice_id}")
    click.echo(f"   Default Duration: {series.default_duration}s")
    click.echo(f"   Model: {series.default_model}")
    click.echo(f"   Quality: {series.default_quality}")
    
    if series.episodes:
        click.echo(f"\n📺 Recent Episodes:")
        for episode in sorted(series.episodes, key=lambda e: e.episode_number, reverse=True)[:5]:
            status = "✅" if episode.published else "⏳"
            click.echo(f"   {status} Episode {episode.episode_number}: {episode.title}")
            if episode.published and episode.video_path:
                click.echo(f"      Video: {episode.video_path}")


@series.command()
@click.argument('series_id')
@click.option('--force', is_flag=True, help='Force deletion without confirmation')
def delete(series_id, force):
    """Delete a video series."""
    manager = SeriesManager()
    series = manager.get_series(series_id)
    
    if not series:
        series = manager.get_series_by_name(series_id)
        
    if not series:
        click.echo(f"❌ Series not found: {series_id}")
        return
        
    if not force:
        click.confirm(
            f"Delete series '{series.name}' with {len(series.episodes)} episodes?",
            abort=True
        )
        
    if manager.delete_series(series.id):
        click.echo(f"✅ Deleted series: {series.name}")
    else:
        click.echo(f"❌ Failed to delete series")


@series.command()
@click.argument('series_id')
def episodes(series_id):
    """List all episodes in a series."""
    manager = SeriesManager()
    series = manager.get_series(series_id)
    
    if not series:
        series = manager.get_series_by_name(series_id)
        
    if not series:
        click.echo(f"❌ Series not found: {series_id}")
        return
        
    if not series.episodes:
        click.echo(f"No episodes in series: {series.name}")
        return
        
    click.echo(f"\n📺 Episodes in '{series.name}':\n")
    
    for episode in sorted(series.episodes, key=lambda e: e.episode_number):
        status = "✅ Published" if episode.published else "⏳ Draft"
        click.echo(f"Episode {episode.episode_number}: {episode.title}")
        click.echo(f"   Status: {status}")
        click.echo(f"   Session: {episode.session_id}")
        if episode.duration:
            click.echo(f"   Duration: {int(episode.duration)}s")
        click.echo(f"   Created: {episode.created_at.strftime('%Y-%m-%d %H:%M')}")
        if episode.published_at:
            click.echo(f"   Published: {episode.published_at.strftime('%Y-%m-%d %H:%M')}")
        click.echo()


@series.command()
@click.argument('series_id')
@click.argument('export_path', type=click.Path())
def export(series_id, export_path):
    """Export series configuration."""
    manager = SeriesManager()
    series = manager.get_series(series_id)
    
    if not series:
        series = manager.get_series_by_name(series_id)
        
    if not series:
        click.echo(f"❌ Series not found: {series_id}")
        return
        
    export_file = Path(export_path)
    if manager.export_series(series.id, export_file):
        click.echo(f"✅ Exported series to: {export_file}")
    else:
        click.echo(f"❌ Failed to export series")


@series.command()
@click.argument('import_path', type=click.Path(exists=True))
def import_series(import_path):
    """Import series configuration from file."""
    manager = SeriesManager()
    
    series = manager.import_series(Path(import_path))
    if series:
        click.echo(f"✅ Imported series: {series.name}")
        click.echo(f"   New ID: {series.id}")
        click.echo(f"   Episodes: {len(series.episodes)}")
    else:
        click.echo(f"❌ Failed to import series")


@series.command()
def templates():
    """List available series templates."""
    manager = SeriesManager()
    templates = manager.list_templates()
    
    if not templates:
        click.echo("No templates found")
        return
        
    click.echo("\n📋 Series Templates:\n")
    
    for template in templates:
        click.echo(f"🎯 {template.name} ({template.id})")
        click.echo(f"   Category: {template.category}")
        click.echo(f"   Duration: {template.default_duration}s")
        click.echo(f"   Schedule: {template.suggested_schedule}")
        if template.description:
            click.echo(f"   Description: {template.description}")
        click.echo()


# CLI Integration - Add this to your main CLI
def add_series_commands(cli):
    """Add series commands to main CLI."""
    cli.add_command(series)