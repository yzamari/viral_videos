#!/usr/bin/env python3
"""
Viral Video Generator - Main Entry Point
Enhanced with Multi-Agent Discussion System
"""

import click
import os
import sys
from datetime import datetime
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import settings
from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.utils.logging_config import get_logger
from src.utils.quota_verifier_class import QuotaVerifier
from src.agents.enhanced_orchestrator_with_discussions import (
    create_discussion_enhanced_orchestrator,
    DiscussionEnhancedOrchestrator
)
from src.features.topic_generator_simple import TopicGeneratorSystem

logger = get_logger(__name__)

@click.group()
def cli():
    """🎬 Viral Video Generator with AI Agent Discussions"""
    pass

@cli.command()
@click.option('--category', type=click.Choice(['Comedy', 'Educational', 'Entertainment', 'News', 'Tech']), 
              default='Comedy', help='Video category')
@click.option('--topic', required=True, help='Video topic')
@click.option('--platform', type=click.Choice(['youtube', 'tiktok', 'instagram', 'twitter']), 
              default='youtube', help='Target platform')
@click.option('--duration', type=int, default=20, help='Video duration in seconds (default: 20)')
@click.option('--image-only', is_flag=True, help='Force image-only generation (Gemini images)')
@click.option('--fallback-only', is_flag=True, help='Use fallback generation only')
@click.option('--force', is_flag=True, help='Force generation even with quota warnings')
@click.option('--discussions', type=click.Choice(['off', 'light', 'standard', 'deep']), 
              default='standard', help='Enable AI agent discussions (default: standard)')
@click.option('--discussion-log', is_flag=True, default=True, help='Show detailed discussion logs')
@click.option('--session-id', help='Custom session ID')
@click.option('--frame-continuity', type=click.Choice(['auto', 'on', 'off']), 
              default='auto', help='Frame continuity mode: auto (AI decides), on (always enabled), off (disabled)')
def generate(category: str, topic: str, platform: str, duration: int, 
            image_only: bool, fallback_only: bool, force: bool, 
            discussions: str, discussion_log: bool, session_id: str, frame_continuity: str):
    """🎬 Generate viral video with AI agent discussions (enabled by default)"""
    
    try:
        # Validate API key
        if not settings.google_api_key:
            click.echo("❌ Error: GOOGLE_API_KEY not found in environment variables")
            click.echo("Please set your Google AI API key in the .env file")
            sys.exit(1)
        
        # Display generation info
        click.echo(f"🎬 Generating {category} video about: {topic}")
        click.echo(f"📱 Platform: {platform}")
        click.echo(f"⏱️ Duration: {duration} seconds")
        
        # Display frame continuity mode
        continuity_modes = {
            'auto': '🤖 AI Agent Decision',
            'on': '✅ Always Enabled',
            'off': '❌ Always Disabled'
        }
        click.echo(f"🎬 Frame Continuity: {continuity_modes[frame_continuity]}")
        
        # CRITICAL: Force agent discussions to ALWAYS be ON
        if discussions == 'off':
            logger.info("🚨 OVERRIDING: Agent discussions forced ON (was set to off)")
            discussions = 'standard'
        
        # Force discussion logging to be ON
        discussion_log = True
        
        logger.info(f"🤖 AI Agent Discussions: {discussions.upper()} MODE (FORCED ON)")
        click.echo("🎭 Orchestrated Video Generation: ALWAYS ENABLED")
        logger.info(f"📝 Discussion logging: {'✅ ENABLED' if discussion_log else '❌ DISABLED'} (FORCED ON)")
        
        # Check quotas unless forced
        if not force:
            click.echo("📊 Checking API quotas...")
            quota_verifier = QuotaVerifier(settings.google_api_key)
            quota_status = quota_verifier.check_all_quotas()
            
            if not quota_status['overall_status']:
                click.echo("⚠️ Warning: Quota issues detected")
                for service, status in quota_status.items():
                    if isinstance(status, dict) and not status.get('available', True):
                        click.echo(f"   {service}: {status.get('message', 'Limited')}")
                
                if not click.confirm("Continue anyway?"):
                    sys.exit(1)
        
        # Choose generation method based on discussions setting
        if discussions == 'off':
            # Traditional generation without discussions
            result = _generate_traditional(category, topic, platform, duration, 
                                         image_only, fallback_only, frame_continuity)
        else:
            # Enhanced generation with agent discussions
            result = _generate_with_discussions(category, topic, platform, duration, 
                                              image_only, fallback_only, discussions, 
                                              discussion_log, frame_continuity)
        
        # Display results
        if result.get('success'):
            click.echo("✅ Video generation completed successfully!")
            click.echo(f"📁 Output: {result.get('final_video_path', 'Check outputs directory')}")
            
            # Display frame continuity decision if available
            if result.get('frame_continuity_decision'):
                decision = result['frame_continuity_decision']
                status = "✅ ENABLED" if decision['use_frame_continuity'] else "❌ DISABLED"
                click.echo(f"🎬 Frame Continuity Decision: {status}")
                click.echo(f"   AI Confidence: {decision['confidence']:.2f}")
                click.echo(f"   Reason: {decision['primary_reason']}")
            
            if discussions != 'off' and 'discussion_results' in result:
                _display_discussion_summary(result['discussion_results'], result['generation_metadata'])
        else:
            click.echo("❌ Video generation failed")
            if 'error' in result:
                click.echo(f"Error: {result['error']}")
    
    except KeyboardInterrupt:
        click.echo("\n🛑 Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        logger.error(f"Generation error: {e}", exc_info=True)
        sys.exit(1)

def _generate_traditional(category: str, topic: str, platform: str, duration: int,
                         image_only: bool, fallback_only: bool, frame_continuity: str) -> dict:
    """Generate video using traditional method without discussions"""
    
    # Create video generator
    generator = VideoGenerator(
        api_key=settings.google_api_key,
        use_real_veo2=not fallback_only
    )
    
    # Determine frame continuity setting
    use_frame_continuity = True  # Default
    frame_continuity_decision = None
    
    if frame_continuity == 'on':
        use_frame_continuity = True
        frame_continuity_decision = {
            'use_frame_continuity': True,
            'confidence': 1.0,
            'primary_reason': 'User forced frame continuity ON',
            'agent_name': 'User Override'
        }
    elif frame_continuity == 'off':
        use_frame_continuity = False
        frame_continuity_decision = {
            'use_frame_continuity': False,
            'confidence': 1.0,
            'primary_reason': 'User forced frame continuity OFF',
            'agent_name': 'User Override'
        }
    else:  # auto mode
        # Use AI agent to decide (even in traditional mode)
        from src.agents.continuity_decision_agent import ContinuityDecisionAgent
        continuity_agent = ContinuityDecisionAgent(settings.google_api_key)
        
        frame_continuity_decision = continuity_agent.analyze_frame_continuity_need(
            topic=topic,
            category=category,
            platform=platform,
            duration=duration,
            style="viral"
        )
        
        use_frame_continuity = frame_continuity_decision['use_frame_continuity']
        logger.info(f"🎬 AI Frame Continuity Decision: {use_frame_continuity}")
        logger.info(f"   Confidence: {frame_continuity_decision['confidence']:.2f}")
        logger.info(f"   Reason: {frame_continuity_decision['primary_reason']}")
    
    # Create configuration
    config = GeneratedVideoConfig(
        target_platform=Platform(platform),
        category=VideoCategory(category),
        duration_seconds=duration,
        topic=topic,
        style="viral",
        tone="engaging",
        target_audience="18-34 viral content consumers",
        hook="Stop scrolling! You won't believe this...",
        main_content=[f"Amazing content about {topic}"],
        call_to_action="Follow for more viral content!",
        visual_style="dynamic",
        color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
        text_overlays=[],
        transitions=["fade", "slide"],
        background_music_style="upbeat",
        voiceover_style="enthusiastic",
        sound_effects=[],
        inspired_by_videos=[],
        predicted_viral_score=0.85,
        frame_continuity=use_frame_continuity  # Use AI decision or user override
    )
    
    # Force image-only if requested
    if image_only:
        config.image_only_mode = True
    
    # Generate video
    result = generator.generate_video(config)
    
    return {
        'success': True,
        'final_video_path': result if result else None,
        'frame_continuity_decision': frame_continuity_decision,
        'error': None
    }

def _generate_with_discussions(category: str, topic: str, platform: str, duration: int,
                              image_only: bool, fallback_only: bool, discussions: str,
                              discussion_log: bool, frame_continuity: str) -> dict:
    """Generate video using enhanced method with agent discussions"""
    
    # CRITICAL FIX: Create session_id first and pass it to orchestrator
    import uuid
    session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    # Create discussion-enhanced orchestrator with shared session_id
    orchestrator = create_discussion_enhanced_orchestrator(
        api_key=settings.google_api_key,
        topic=topic,
        category=category,
        platform=platform,
        duration=duration,
        discussion_mode=discussions,
        session_id=session_id  # CRITICAL: Pass session_id
    )
    
    # Create configuration
    config = {
        'image_only': image_only,
        'fallback_only': fallback_only,
        'image_only_mode': image_only,
        'use_real_veo2': not fallback_only,
        'discussion_logging': discussion_log,
        'frame_continuity': frame_continuity
    }
    
    # Generate video with discussions
    result = orchestrator.orchestrate_complete_generation(config)
    
    # Add frame continuity decision to result if available
    if hasattr(orchestrator, 'frame_continuity_decision') and orchestrator.frame_continuity_decision:
        result['frame_continuity_decision'] = orchestrator.frame_continuity_decision
    
    return result

def _display_discussion_summary(discussion_results: dict, metadata: dict):
    """Display summary of agent discussions"""
    click.echo("\n🤖 AI AGENT DISCUSSION SUMMARY:")
    click.echo(f"   Total Discussions: {metadata['total_discussions']}")
    click.echo(f"   Average Consensus: {metadata['average_consensus']:.2f}")
    
    for topic, result in discussion_results.items():
        click.echo(f"\n💬 {topic.replace('_', ' ').title()}:")
        click.echo(f"   Consensus: {result.consensus_level:.2f}")
        click.echo(f"   Rounds: {result.total_rounds}")
        click.echo(f"   Participants: {', '.join(result.participating_agents)}")
        
        if result.key_insights:
            click.echo(f"   Key Insight: {result.key_insights[0]}")

@cli.command()
def veo_quota():
    """📊 Check VEO and Gemini API quotas"""
    
    if not settings.google_api_key:
        click.echo("❌ Error: GOOGLE_API_KEY not found")
        sys.exit(1)
    
    click.echo("📊 Checking API quotas...")
    
    quota_verifier = QuotaVerifier(settings.google_api_key)
    quota_status = quota_verifier.check_all_quotas()
    
    # Display results
    click.echo("\n🔍 QUOTA STATUS:")
    
    for service, status in quota_status.items():
        if service == 'overall_status':
            continue
            
        if isinstance(status, dict):
            status_icon = "✅" if status.get('available', True) else "❌"
            click.echo(f"{status_icon} {service}: {status.get('message', 'Available')}")
            
            if 'details' in status:
                for detail in status['details']:
                    click.echo(f"   • {detail}")
    
    # Overall status
    overall_icon = "✅" if quota_status['overall_status'] else "⚠️"
    click.echo(f"\n{overall_icon} Overall Status: {'Good' if quota_status['overall_status'] else 'Limited'}")

@cli.command()
@click.option('--session-id', help='Specific session ID to analyze')
@click.option('--recent', type=int, default=5, help='Number of recent sessions to show')
def discussions(session_id: str, recent: int):
    """📊 Analyze AI agent discussions from previous generations"""
    
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        click.echo("❌ No outputs directory found")
        return
    
    if session_id:
        # Analyze specific session
        _analyze_session_discussions(session_id)
    else:
        # Show recent sessions with discussions
        _show_recent_discussions(recent)

def _analyze_session_discussions(session_id: str):
    """Analyze discussions from a specific session"""
    session_dir = f"outputs/session_{session_id}"
    
    if not os.path.exists(session_dir):
        click.echo(f"❌ Session {session_id} not found")
        return
    
    discussions_dir = os.path.join(session_dir, "agent_discussions")
    summary_file = os.path.join(session_dir, "agent_discussions_summary.json")
    
    if os.path.exists(summary_file):
        import json
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        click.echo(f"🤖 DISCUSSION ANALYSIS - Session {session_id}")
        click.echo(f"Topic: {summary.get('topic', 'Unknown')}")
        click.echo(f"Generated: {summary.get('generation_timestamp', 'Unknown')}")
        
        config = summary.get('discussion_configuration', {})
        click.echo(f"Discussion Mode: {config.get('depth', 'Unknown')}")
        click.echo(f"Total Discussions: {config.get('total_discussions', 0)}")
        
        metrics = summary.get('overall_metrics', {})
        click.echo(f"Average Consensus: {metrics.get('average_consensus', 0):.2f}")
        click.echo(f"Total Rounds: {metrics.get('total_rounds', 0)}")
        
        # Show key insights
        insights = summary.get('key_insights_summary', [])
        if insights:
            click.echo("\n💡 Key Insights:")
            for insight in insights[:3]:
                click.echo(f"   • {insight}")
    else:
        click.echo(f"❌ No discussion summary found for session {session_id}")

def _show_recent_discussions(recent: int):
    """Show recent sessions with discussions"""
    outputs_dir = "outputs"
    sessions = []
    
    for item in os.listdir(outputs_dir):
        if item.startswith("session_"):
            session_path = os.path.join(outputs_dir, item)
            summary_file = os.path.join(session_path, "agent_discussions_summary.json")
            
            if os.path.exists(summary_file):
                try:
                    import json
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                    
                    sessions.append({
                        'session_id': item.replace('session_', ''),
                        'topic': summary.get('topic', 'Unknown'),
                        'timestamp': summary.get('generation_timestamp', ''),
                        'discussions': summary.get('discussion_configuration', {}).get('total_discussions', 0),
                        'consensus': summary.get('overall_metrics', {}).get('average_consensus', 0)
                    })
                except:
                    continue
    
    # Sort by timestamp
    sessions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    click.echo(f"📊 RECENT SESSIONS WITH DISCUSSIONS (Last {recent}):")
    
    for session in sessions[:recent]:
        click.echo(f"\n🎬 Session: {session['session_id']}")
        click.echo(f"   Topic: {session['topic']}")
        click.echo(f"   Discussions: {session['discussions']}")
        click.echo(f"   Avg Consensus: {session['consensus']:.2f}")
        click.echo(f"   Generated: {session['timestamp'][:19]}")

@cli.command()
@click.option('--idea', required=True, help='High-level idea or goal (e.g., "convince people to vote")')
@click.option('--platform', type=click.Choice(['youtube', 'tiktok', 'instagram', 'twitter']), 
              default='youtube', help='Target platform')
@click.option('--audience', help='Target audience (e.g., "Young adults", "Professionals")')
@click.option('--style', help='Content style (e.g., "Engaging", "Educational", "Humorous")')
@click.option('--duration', type=int, default=30, help='Target video duration in seconds')
@click.option('--category', type=click.Choice(['Comedy', 'Educational', 'Entertainment', 'News', 'Technology']), 
              default='Educational', help='Video category')
@click.option('--discussions', type=click.Choice(['light', 'standard', 'deep']), 
              default='standard', help='Discussion mode for video generation')
@click.option('--frame-continuity', type=click.Choice(['auto', 'on', 'off']), 
              default='auto', help='Frame continuity mode for video generation')
@click.option('--generate-video', is_flag=True, help='Automatically generate video after topic generation')
def generate_topic(idea: str, platform: str, audience: str, style: str, duration: int, 
                  category: str, discussions: str, frame_continuity: str, generate_video: bool):
    """🎯 Generate a topic using AI agents"""
    try:
        click.echo(f"🎯 Generating topic for idea: '{idea}'")
        
        # Validate API key
        if not settings.google_api_key:
            click.echo("❌ Error: GOOGLE_API_KEY not found in environment variables")
            click.echo("Please set your Google AI API key in the .env file")
            sys.exit(1)
        
        # Prepare context
        context = {
            'platform': platform,
            'audience': audience or 'General',
            'style': style or 'Engaging',
            'duration': duration,
            'category': category
        }
        
        # Generate topic
        generator = TopicGeneratorSystem(settings.google_api_key)
        result = generator.generate_topic(idea, context)
        
        # Display results
        final_topic = result['final_topic']
        click.echo(f"\n✅ Generated Topic: {final_topic['topic']}")
        click.echo(f"📋 Reasoning: {final_topic['reasoning']}")
        click.echo(f"🎯 Viral Potential: {final_topic['viral_potential']}")
        click.echo(f"🛡️ Ethical Considerations: {final_topic['ethical_considerations']}")
        click.echo(f"📁 Full results saved to: {result.get('session_directory', 'outputs/')}")
        
        # If generate flag is set, automatically generate video with this topic
        if generate_video:
            click.echo(f"\n🎬 Automatically generating video with topic: '{final_topic['topic']}'")
            
            # Call the generate command with the generated topic
            from click.testing import CliRunner
            runner = CliRunner()
            
            # Prepare arguments for video generation
            video_args = [
                'generate',
                '--topic', final_topic['topic'],
                '--duration', str(duration),
                '--category', category,
                '--platform', platform,
                '--discussions', discussions,
                '--frame-continuity', frame_continuity
            ]
            
            # Run the generate command
            result = runner.invoke(cli, video_args)
            
            if result.exit_code != 0:
                click.echo(f"❌ Video generation failed: {result.output}")
                return
            
            click.echo("✅ Video generation completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Topic generation failed: {e}")
        logger.error(f"Topic generation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli() 