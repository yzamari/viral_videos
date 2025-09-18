"""
CLI Command for Multi-Scene Series Generation
"""

import click
import asyncio
from typing import Optional
from pathlib import Path
import json

from ..orchestrators.narrative_orchestrator import (
    NarrativeOrchestrator,
    NarrativeStructure
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@click.command()
@click.option(
    '--narrative',
    '-n',
    required=True,
    help='Narrative description (e.g., "2-minute PTSD education film with 4 soldiers")'
)
@click.option(
    '--duration',
    '-d',
    type=float,
    required=True,
    help='Total duration in seconds'
)
@click.option(
    '--characters',
    '-c',
    type=int,
    help='Number of characters to create (if not using existing)'
)
@click.option(
    '--character-ids',
    help='Comma-separated list of existing character IDs to use'
)
@click.option(
    '--structure',
    type=click.Choice([
        'three_act', 'five_act', 'heros_journey',
        'parallel', 'circular', 'educational', 'documentary'
    ]),
    default='educational',
    help='Narrative structure to follow'
)
@click.option(
    '--scenes',
    '-s',
    type=int,
    help='Number of scenes (auto-calculated if not specified)'
)
@click.option(
    '--style',
    default='cinematic',
    help='Overall visual style'
)
@click.option(
    '--visual-style',
    default='realistic',
    help='Specific visual treatment'
)
@click.option(
    '--platform',
    type=click.Choice(['youtube', 'tiktok', 'instagram', 'twitter']),
    default='youtube',
    help='Target platform'
)
@click.option(
    '--parallel/--sequential',
    default=True,
    help='Generate scenes in parallel or sequentially'
)
@click.option(
    '--auto-combine/--no-combine',
    default=True,
    help='Automatically combine scenes into final video'
)
@click.option(
    '--session-id',
    help='Custom session ID for this narrative'
)
@click.option(
    '--no-cheap',
    is_flag=True,
    help='Use premium generation (VEO3)'
)
@click.option(
    '--therapeutic-mode',
    is_flag=True,
    help='Enable therapeutic content transformation'
)
@click.option(
    '--veo-model-order',
    default='veo3',
    help='VEO model preference'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output path for final video'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Only create narrative plan without generating videos'
)
def generate_series(
    narrative: str,
    duration: float,
    characters: Optional[int],
    character_ids: Optional[str],
    structure: str,
    scenes: Optional[int],
    style: str,
    visual_style: str,
    platform: str,
    parallel: bool,
    auto_combine: bool,
    session_id: Optional[str],
    no_cheap: bool,
    therapeutic_mode: bool,
    veo_model_order: str,
    output: Optional[str],
    dry_run: bool
):
    """
    Generate a complete multi-scene narrative series
    
    This command orchestrates the creation of complex narratives with:
    - Multiple scenes
    - Multiple characters
    - Character arcs
    - Narrative structure
    - Automatic scene decomposition
    - Parallel generation
    - Final assembly
    
    Examples:
    
    # PTSD education film with 4 characters
    python main.py generate-series \\
        --narrative "2-minute PTSD education film showing 4 IDF soldiers with different symptoms" \\
        --duration 120 \\
        --characters 4 \\
        --structure educational \\
        --style "Waltz with Bashir animation" \\
        --therapeutic-mode
    
    # Using existing characters
    python main.py generate-series \\
        --narrative "Corporate training on teamwork" \\
        --duration 180 \\
        --character-ids "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \\
        --structure parallel
    
    # Documentary style narrative
    python main.py generate-series \\
        --narrative "History of artificial intelligence" \\
        --duration 300 \\
        --structure documentary \\
        --scenes 10
    """
    
    async def run():
        try:
            click.echo(click.style("\n🎬 NARRATIVE SERIES GENERATOR", fg='magenta', bold=True))
            click.echo(click.style("=" * 50, fg='magenta'))
            click.echo(f"\n📝 Narrative: {narrative}")
            click.echo(f"⏱️  Duration: {duration} seconds")
            click.echo(f"🏗️  Structure: {structure}")
            
            # Parse character IDs if provided
            char_ids = None
            if character_ids:
                char_ids = [cid.strip() for cid in character_ids.split(',')]
                click.echo(f"👥 Using characters: {', '.join(char_ids)}")
            elif characters:
                click.echo(f"👥 Creating {characters} new characters")
            
            # Initialize orchestrator
            orchestrator = NarrativeOrchestrator(session_id)
            
            # Create narrative structure
            click.echo("\n" + click.style("Step 1: Planning Narrative", fg='cyan'))
            click.echo("-" * 40)
            
            narrative_obj = await orchestrator.create_narrative(
                mission=narrative,
                duration=duration,
                num_characters=characters,
                character_ids=char_ids,
                structure=NarrativeStructure[structure.upper()],
                style=style,
                visual_style=visual_style,
                platform=platform,
                specified_scenes=scenes
            )
            
            # Display narrative plan
            click.echo(f"\n✅ Created narrative: {narrative_obj.title}")
            click.echo(f"   Scenes: {len(narrative_obj.scenes)}")
            click.echo(f"   Characters: {len(narrative_obj.characters)}")
            
            # Show scene breakdown
            click.echo("\n" + click.style("Scene Breakdown:", fg='yellow'))
            for scene in narrative_obj.scenes:
                char_count = len(scene.characters)
                click.echo(
                    f"  {scene.scene_number}. {scene.title} "
                    f"({scene.duration:.1f}s, {char_count} chars) - {scene.mood}"
                )
            
            if dry_run:
                click.echo("\n" + click.style("DRY RUN - Skipping generation", fg='yellow'))
                
                # Save plan
                plan_path = Path(f"outputs/{orchestrator.session_id}/narrative_plan.json")
                plan_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(plan_path, 'w') as f:
                    json.dump({
                        "title": narrative_obj.title,
                        "scenes": [
                            {
                                "number": s.scene_number,
                                "title": s.title,
                                "duration": s.duration,
                                "description": s.description
                            }
                            for s in narrative_obj.scenes
                        ]
                    }, f, indent=2)
                
                click.echo(f"\n💾 Narrative plan saved to: {plan_path}")
                return
            
            # Generate all scenes
            click.echo("\n" + click.style("Step 2: Generating Scenes", fg='cyan'))
            click.echo("-" * 40)
            
            generation_kwargs = {
                "cheap_mode": not no_cheap,
                "therapeutic_mode": therapeutic_mode,
                "veo_model_order": veo_model_order,
                "auto_combine": auto_combine
            }
            
            if parallel:
                click.echo("🚀 Generating scenes in parallel...")
            else:
                click.echo("📝 Generating scenes sequentially...")
            
            results = await orchestrator.generate_narrative(
                narrative_obj,
                parallel=parallel,
                **generation_kwargs
            )
            
            # Display results
            click.echo("\n" + click.style("Generation Results:", fg='green'))
            successful = len([s for s in results['scenes'] if s.get('success')])
            click.echo(f"  ✅ Successful: {successful}/{len(narrative_obj.scenes)}")
            
            if results.get('errors'):
                click.echo(click.style(f"  ❌ Errors: {len(results['errors'])}", fg='red'))
                for error in results['errors'][:3]:  # Show first 3 errors
                    click.echo(f"     - {error}")
            
            # Final output
            if results.get('final_video'):
                final_path = results['final_video']
                
                # Move to custom output if specified
                if output:
                    import shutil
                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(final_path, output_path)
                    final_path = str(output_path)
                
                click.echo(
                    "\n" + click.style(
                        f"🎬 COMPLETE! Final video: {final_path}",
                        fg='green',
                        bold=True
                    )
                )
            else:
                click.echo(
                    "\n" + click.style(
                        f"📁 Individual scenes saved to: outputs/{orchestrator.session_id}/",
                        fg='yellow'
                    )
                )
            
            # Summary
            click.echo("\n" + click.style("Summary:", fg='blue'))
            click.echo(orchestrator.get_narrative_summary())
            
        except Exception as e:
            click.echo(click.style(f"\n❌ Error: {e}", fg='red'))
            raise click.ClickException(str(e))
    
    # Run the async function
    asyncio.run(run())


# Export for CLI registration
generate_series_command = generate_series