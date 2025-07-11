#!/usr/bin/env python3
"""
Main CLI interface for the AI Video Generator
Enhanced with intelligent AI agents for voice selection, positioning, and style decisions
"""

from src.features.topic_generator_simple import TopicGeneratorSystem
from src.utils.quota_verifier_class import QuotaVerifier
from src.utils.logging_config import get_logger
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.generators.video_generator import VideoGenerator
from src.utils.gcloud_auth_tester import test_gcloud_authentication
from config.config import settings
import sys
import os
import click

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


logger = get_logger(__name__)


@click.group()
def cli():
    """🎬 Viral Video Generator with AI Agent Discussions"""
    pass


@cli.command()
def test_auth():
    """🔐 Test Google Cloud authentication and API access"""
    click.echo("🔐 Testing Google Cloud authentication...")
    results = test_gcloud_authentication()
    
    # Exit with appropriate code
    analysis = results.get('analysis', {})
    if analysis.get('can_run_app', False):
        click.echo("\n✅ Authentication tests completed successfully!")
        sys.exit(0)
    else:
        click.echo("\n❌ Critical authentication failures detected!")
        sys.exit(1)


@cli.command()
@click.option('--category',
              type=click.Choice(['Comedy',
                                 'Educational',
                                 'Entertainment',
                                 'News',
                                 'Tech'], case_sensitive=False),
              default='Comedy',
              help='Video category')
@click.option('--mission', required=True,
              help='Video mission - what you want to accomplish')
@click.option('--platform',
              type=click.Choice(['youtube',
                                 'tiktok',
                                 'instagram',
                                 'twitter']),
              default='youtube',
              help='Target platform')
@click.option('--duration', type=int, default=20,
              help='Video duration in seconds (default: 20)')
@click.option('--image-only', is_flag=True,
              help='Force image-only generation (Gemini images)')
@click.option('--fallback-only', is_flag=True,
              help='Use fallback generation only')
@click.option('--force', is_flag=True,
              help='Force generation even with quota warnings')
@click.option('--skip-auth-test', is_flag=True,
              help='Skip authentication test (not recommended)')
@click.option('--discussions',
              type=click.Choice(['off',
                                 'light',
                                 'standard',
                                 'deep',
                                 'streamlined',
                                 'enhanced']),
              default='enhanced',
              help='AI agent mode (default: enhanced with discussions for best viral content)')
@click.option('--discussion-log', is_flag=True, default=True,
              help='Show detailed discussion logs')
@click.option('--session-id', help='Custom session ID')
@click.option('--frame-continuity',
              type=click.Choice(['auto',
                                 'on',
                                 'off']),
              default='auto',
              help='Frame continuity mode: auto (AI decides), on (always enabled), off (disabled)')
@click.option('--target-audience', default='general audience',
              help='Target audience (e.g., "young adults", "professionals")')
@click.option('--style', default='viral',
              help='Content style (e.g., "viral", "educational", "professional")')
@click.option('--tone', default='engaging',
              help='Content tone (e.g., "engaging", "professional", "humorous")')
@click.option('--visual-style', default='dynamic',
              help='Visual style (e.g., "dynamic", "minimalist", "professional")')
@click.option('--mode', 
              type=click.Choice(['simple', 'enhanced', 'advanced', 'multilingual', 'professional']),
              default='enhanced',
              help='Orchestrator mode (simple=3 agents, enhanced=7 agents, advanced=15 agents, professional=19 agents)')
def generate(
        category: str,
        mission: str,
        platform: str,
        duration: int,
        image_only: bool,
        fallback_only: bool,
        force: bool,
        skip_auth_test: bool,
        discussions: str,
        discussion_log: bool,
        session_id: str,
        frame_continuity: str,
        target_audience: str,
        style: str,
        tone: str,
        visual_style: str,
        mode: str):
    """🎬 Generate viral video with optimized AI system"""
    
    try:
        # STEP 1: Authentication Testing (unless skipped)
        if not skip_auth_test:
            click.echo("🔐 Running Google Cloud authentication tests...")
            auth_results = test_gcloud_authentication()
            
            analysis = auth_results.get('analysis', {})
            
            if not analysis.get('can_run_app', False):
                click.echo("❌ Authentication tests failed! Cannot proceed with video generation.")
                click.echo("💡 Use --skip-auth-test to bypass (not recommended)")
                sys.exit(1)
            
            click.echo("✅ Authentication tests passed!")
        else:
            click.echo("⚠️ Skipping authentication tests (not recommended)")
        
        # STEP 2: Validate API key
        if not settings.google_api_key:
            click.echo(
                "❌ Error: GOOGLE_API_KEY not found in environment variables")
            click.echo("Please set your Google AI API key in the .env file")
            sys.exit(1)
        
        # STEP 3: Display generation info
        click.echo(f"🎯 Generating {category} video for mission: {mission}")
        click.echo(f"📱 Platform: {platform}")
        click.echo(f"⏱️ Duration: {duration} seconds")
        click.echo(f"🎭 Mode: {mode} ({_get_mode_description(mode)})")
        
        # Display frame continuity mode
        continuity_modes = {
            'auto': '🤖 AI Agent Decision',
            'on': '✅ Always Enabled',
            'off': '❌ Always Disabled'
        }
        click.echo(f"🎬 Frame Continuity: {continuity_modes[frame_continuity]}")
        
        # Show AI system mode
        system_modes = {
            'enhanced': '🎯 Enhanced (7 agents with discussions, best viral content)',
            'streamlined': '⚡ Streamlined (5 agents, fastest)',
            'light': '🔥 Light (7 agents, fast)',
            'standard': '🎭 Standard (19 agents, comprehensive)',
            'deep': '🧠 Deep (19+ agents, detailed)',
            'off': '🚫 Traditional (no agents)'}
        click.echo(
            f"🤖 AI System: {
                system_modes.get(
                    discussions,
                    discussions)}")
        
        # STEP 4: Check quotas unless forced
        if not force:
            click.echo("📊 Checking API quotas...")
            quota_verifier = QuotaVerifier(settings.google_api_key)
            quota_status = quota_verifier.check_all_quotas()
            
            if not quota_status['overall_status']:
                click.echo("⚠️ Warning: Quota issues detected")
                for service, status in quota_status.items():
                    if isinstance(
                            status, dict) and not status.get(
                            'available', True):
                        click.echo(
                            f"   {service}: {
                                status.get(
                                    'message',
                                    'Limited')}")
                
                if not click.confirm("Continue anyway?"):
                    sys.exit(1)
        
        # STEP 5: Choose generation method
        if discussions == 'enhanced':
            # Use enhanced streamlined system with discussions
            result = _generate_enhanced_streamlined(
                category,
                mission,
                platform,
                duration,
                image_only,
                fallback_only,
                frame_continuity,
                target_audience,
                style,
                tone,
                visual_style,
                mode)
        elif discussions == 'streamlined':
            # Use basic streamlined system
            result = _generate_streamlined(
                category,
                mission,
                platform,
                duration,
                image_only,
                fallback_only,
                frame_continuity,
                target_audience,
                style,
                tone,
                visual_style,
                mode)
        elif discussions == 'off':
            # Traditional generation without discussions
            result = _generate_traditional(
                category,
                mission,
                platform,
                duration,
                image_only,
                fallback_only,
                frame_continuity,
                target_audience,
                style,
                tone,
                visual_style,
                mode)
        else:
            # Enhanced generation with agent discussions
            result = _generate_with_discussions(
                category,
                mission,
                platform,
                duration,
                image_only,
                fallback_only,
                discussions,
                discussion_log,
                frame_continuity,
                target_audience,
                style,
                tone,
                visual_style,
                mode)
        
        # STEP 6: Display results
        if result.get('success'):
            click.echo("✅ Video generation completed successfully!")
            click.echo(
                f"📁 Output: {
                    result.get(
                        'final_video_path',
                        'Check outputs directory')}")
            
            # Show performance metrics for streamlined modes
            if discussions in ['streamlined', 'enhanced']:
                click.echo(f"⚡ Agents Used: {result.get('agents_used', 5)}")
                click.echo(
                    f"🕒 Generation Time: {
                        result.get(
                            'generation_time',
                            'N/A')}")
                click.echo(
                    f"🎯 Optimization: {
                        result.get(
                            'optimization_level',
                            'streamlined')}")
                
                # Show discussion metrics for enhanced mode
                if discussions == 'enhanced':
                    click.echo(
                        f"🤝 Discussions: {
                            result.get(
                                'discussions_conducted',
                                0)}")
                    click.echo("💬 Agent Discussions:")
                    click.echo("   • ScriptMaster ↔ ViralismSpecialist")
                    click.echo("   • ContentSpecialist ↔ VisualDirector") 
                    click.echo("   • AudioEngineer ↔ VideoEditor")
            
            # Display frame continuity decision if available
            if result.get('frame_continuity_decision'):
                decision = result['frame_continuity_decision']
                status = "✅ ENABLED" if decision['use_frame_continuity'] else "❌ DISABLED"
                click.echo(f"🎬 Frame Continuity Decision: {status}")
                click.echo(f"   AI Confidence: {decision['confidence']:.2f}")
                click.echo(f"   Reason: {decision['primary_reason']}")
            
            if discussions not in [
                    'off', 'streamlined'] and 'discussion_results' in result:
                _display_discussion_summary(
                    result['discussion_results'], result.get(
                        'generation_metadata', {}))
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


def _generate_traditional(
        category: str,
        mission: str,
        platform: str,
        duration: int,
        image_only: bool,
        fallback_only: bool,
        frame_continuity: str,
        target_audience: str,
        style: str,
        tone: str,
        visual_style: str,
        mode: str) -> dict:
    """Generate video using traditional method without discussions"""
    
    # CRITICAL: Make frame continuity decision FIRST
    frame_continuity_decision = _make_frame_continuity_decision(
        frame_continuity, category, mission, platform, duration, style
    )
    
    # Log the decision prominently
    continuity_status = "✅ ENABLED" if frame_continuity_decision['use_frame_continuity'] else "❌ DISABLED"
    logger.info(f"🎬 Frame Continuity Decision: {continuity_status}")
    logger.info(f"   Confidence: {frame_continuity_decision['confidence']:.2f}")
    logger.info(f"   Reason: {frame_continuity_decision['primary_reason']}")
    
    # Create video generator
    generator = VideoGenerator(
        api_key=settings.google_api_key,
        use_real_veo2=not fallback_only
    )
    
    # Create configuration with frame continuity decision
    config = GeneratedVideoConfig(
        target_platform=Platform(platform),
        category=VideoCategory(_map_category_to_enum(category)),
        duration_seconds=duration,
        topic=mission,
        style=style,
        tone=tone,
        target_audience=target_audience,
        hook="Stop scrolling! You won't believe this...",
        main_content=[f"Amazing content for mission: {mission}"],
        call_to_action="Follow for more viral content!",
        visual_style=visual_style,
        color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
        text_overlays=[],
        transitions=["fade", "slide"],
        background_music_style="upbeat",
        voiceover_style="enthusiastic",
        sound_effects=[],
        inspired_by_videos=[],
        predicted_viral_score=0.85,
        frame_continuity=frame_continuity_decision['use_frame_continuity']  # Use AI decision or user override
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


def _make_frame_continuity_decision(frame_continuity: str, category: str, mission: str, 
                                  platform: str, duration: int, style: str) -> dict:
    """
    Make frame continuity decision at the beginning of generation
    This decision impacts ALL subsequent choices
    """
    if frame_continuity == 'on':
        return {
            'use_frame_continuity': True,
            'confidence': 1.0,
            'primary_reason': 'User forced frame continuity ON',
            'agent_name': 'User Override',
            'requires_veo2_only': True,
            'frame_overlap_handling': 'remove_first_frame',
            'transition_strategy': 'last_to_first_frame'
        }
    elif frame_continuity == 'off':
        return {
            'use_frame_continuity': False,
            'confidence': 1.0,
            'primary_reason': 'User forced frame continuity OFF',
            'agent_name': 'User Override',
            'requires_veo2_only': False,
            'frame_overlap_handling': 'none',
            'transition_strategy': 'standard_cuts'
        }
    else:  # auto mode
        # Use AI agent to decide
        from src.agents.continuity_decision_agent import ContinuityDecisionAgent
        continuity_agent = ContinuityDecisionAgent(settings.google_api_key)
        
        decision = continuity_agent.analyze_frame_continuity_need(
            topic=mission,
            category=category,
            platform=platform,
            duration=duration,
            style=style
        )
        
        # Enhance decision with technical requirements
        if decision['use_frame_continuity']:
            decision['requires_veo2_only'] = True
            decision['frame_overlap_handling'] = 'remove_first_frame'
            decision['transition_strategy'] = 'last_to_first_frame'
        else:
            decision['requires_veo2_only'] = False
            decision['frame_overlap_handling'] = 'none'
            decision['transition_strategy'] = 'standard_cuts'
        
        return decision


def _generate_with_discussions(
        category: str,
        mission: str,
        platform: str,
        duration: int,
        image_only: bool,
        fallback_only: bool,
        discussions: str,
        discussion_log: bool,
        frame_continuity: str,
        target_audience: str,
        style: str,
        tone: str,
        visual_style: str,
        mode: str) -> dict:
    """Generate video using working orchestrator with AI agents"""

    click.echo("🎯 Using Working Orchestrator with AI Agents")
    click.echo(
        "🤖 AI agents: Voice Director, Continuity Agent, Visual Style, Positioning")
    
    # Import working orchestrator
    from src.agents.working_orchestrator import create_working_orchestrator

    # Create orchestrator with user parameters
    orchestrator = create_working_orchestrator(
        api_key=settings.google_api_key,
        mission=mission,
        platform=platform,
        category=_map_category_to_enum(category),
        duration=duration,
        style=style,
        tone=tone,
        target_audience=target_audience,
        visual_style=visual_style,
        mode=mode
    )
    
    # Create configuration
    config = {
        'image_only': image_only,
        'fallback_only': fallback_only,
        'image_only_mode': image_only,
        'use_real_veo2': not fallback_only,
        'discussion_logging': discussion_log,
        'frame_continuity': frame_continuity,
        'style': style,
        'tone': tone,
        'target_audience': target_audience
    }
    
    # Generate video with AI agents
    result = orchestrator.generate_video(config)
    
    return result


def _generate_streamlined(
        category: str,
        mission: str,
        platform: str,
        duration: int,
        image_only: bool,
        fallback_only: bool,
        frame_continuity: str,
        target_audience: str,
        style: str,
        tone: str,
        visual_style: str,
        mode: str) -> dict:
    """Generate video using working orchestrator in simple mode"""
    
    click.echo("⚡ Using Simple Mode for fast generation")
    
    # Import working orchestrator
    from src.agents.working_orchestrator import create_working_orchestrator
    
    # Create orchestrator with user parameters
    orchestrator = create_working_orchestrator(
        api_key=settings.google_api_key,
        mission=mission,
        platform=platform,
        category=_map_category_to_enum(category),
        duration=duration,
        style=style,
        tone=tone,
        target_audience=target_audience,
        visual_style=visual_style,
        mode=mode
    )
    
    # Configuration for streamlined generation
    config = {
        'image_only': image_only,
        'fallback_only': fallback_only,
        'target_audience': target_audience,
        'style': style,
        'visual_style': visual_style,
        'voice_style': 'energetic',
        'frame_continuity': frame_continuity,
        'quality_requirements': 'high'
    }
    
    # Generate video
    result = orchestrator.generate_video(config)
    
    return result


def _generate_enhanced_streamlined(
        category: str,
        mission: str,
        platform: str,
        duration: int,
        image_only: bool,
        fallback_only: bool,
        frame_continuity: str,
        target_audience: str,
        style: str,
        tone: str,
        visual_style: str,
        mode: str) -> dict:
    """Generate video using working orchestrator in enhanced mode"""
    
    click.echo("🎯 Using Enhanced Mode with AI Agent Intelligence")
    click.echo(
        "🤖 Full AI agent system: Voice, Style, Positioning, Continuity decisions")
    
    # Import working orchestrator
    from src.agents.working_orchestrator import create_working_orchestrator
    
    # Create orchestrator with user parameters
    orchestrator = create_working_orchestrator(
        api_key=settings.google_api_key,
        mission=mission,
        platform=platform,
        category=_map_category_to_enum(category),
        duration=duration,
        style=style,
        tone=tone,
        target_audience=target_audience,
        visual_style=visual_style,
        mode=mode
    )
    
    # Configuration for enhanced generation
    config = {
        'image_only': image_only,
        'fallback_only': fallback_only,
        'target_audience': target_audience,
        'style': style,
        'visual_style': visual_style,
        'voice_style': 'energetic',
        'content_strategy': 'engagement_focused',
        'frame_continuity': frame_continuity,
        'quality_requirements': 'high'
    }
    
    # Generate video with AI agents
    result = orchestrator.generate_video(config)
    
    return result


def _get_mode_description(mode: str) -> str:
    """Get description for orchestrator mode"""
    mode_descriptions = {
        'simple': '3 agents, fast generation',
        'enhanced': '7 agents with discussions',
        'advanced': '15+ agents, comprehensive',
        'multilingual': '8 agents with multi-language support',
        'professional': '19+ agents, maximum quality'
    }
    return mode_descriptions.get(mode, mode)


def _map_category_to_enum(category: str) -> str:
    """Map CLI category names to VideoCategory enum values"""
    category_mapping = {
        'Comedy': 'Comedy',
        'Educational': 'Education',
        'Entertainment': 'Entertainment',
        'News': 'News',
        'Tech': 'Technology'
    }
    return category_mapping.get(category, category)


def _display_discussion_summary(discussion_results: dict, metadata: dict):
    """Display summary of agent discussions"""
    click.echo("\n🤖 AI AGENT DISCUSSION SUMMARY:")
    
    # Handle missing metadata gracefully
    total_discussions = metadata.get('total_discussions', len(discussion_results))
    average_consensus = metadata.get('average_consensus', 0.0)
    
    # Calculate average consensus if not provided
    if average_consensus == 0.0 and discussion_results:
        consensus_values = []
        for result in discussion_results.values():
            if hasattr(result, 'consensus_level'):
                consensus_values.append(result.consensus_level)
        if consensus_values:
            average_consensus = sum(consensus_values) / len(consensus_values)
    
    click.echo(f"   Total Discussions: {total_discussions}")
    click.echo(f"   Average Consensus: {average_consensus:.2f}")

    for mission_topic, result in discussion_results.items():
        click.echo(f"\n💬 {mission_topic.replace('_', ' ').title()}:")
        
        # Handle both dict and object results
        if hasattr(result, 'consensus_level'):
            click.echo(f"   Consensus: {result.consensus_level:.2f}")
            click.echo(f"   Rounds: {result.total_rounds}")
            click.echo(f"   Participants: {', '.join(result.participating_agents)}")
            
            if hasattr(result, 'key_insights') and result.key_insights:
                click.echo(f"   Key Insight: {result.key_insights[0]}")
        else:
            # Handle dict-style results
            click.echo(f"   Consensus: {result.get('consensus_level', 0.0):.2f}")
            click.echo(f"   Rounds: {result.get('total_rounds', 0)}")
            participants = result.get('participating_agents', [])
            if participants:
                click.echo(f"   Participants: {', '.join(participants)}")
            
            insights = result.get('key_insights', [])
            if insights:
                click.echo(f"   Key Insight: {insights[0]}")


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
            click.echo(
                f"{status_icon} {service}: {
                    status.get(
                        'message',
                        'Available')}")
            
            if 'details' in status:
                for detail in status['details']:
                    click.echo(f"   • {detail}")
    
    # Overall status
    overall_icon = "✅" if quota_status['overall_status'] else "⚠️"
    click.echo(
        f"\n{overall_icon} Overall Status: {
            'Good' if quota_status['overall_status'] else 'Limited'}")


@cli.command()
@click.option('--session-id', help='Specific session ID to analyze')
@click.option('--recent', type=int, default=5,
              help='Number of recent sessions to show')
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
    
    # Remove unused discussions_dir variable
    summary_file = os.path.join(session_dir, "agent_discussions_summary.json")
    
    if os.path.exists(summary_file):
        import json
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        click.echo(f"🤖 DISCUSSION ANALYSIS - Session {session_id}")
        click.echo(
            f"Mission: {
                summary.get(
                    'mission',
                    summary.get(
                        'topic',
                        'Unknown'))}")
        click.echo(
            f"Generated: {
                summary.get(
                    'generation_timestamp',
                    'Unknown')}")
        
        config = summary.get('discussion_configuration', {})
        click.echo(f"Discussion Mode: {config.get('depth', 'Unknown')}")
        click.echo(f"Total Discussions: {config.get('total_discussions', 0)}")
        
        metrics = summary.get('overall_metrics', {})
        click.echo(
            f"Average Consensus: {
                metrics.get(
                    'average_consensus',
                    0):.2f}")
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
            summary_file = os.path.join(
                session_path, "agent_discussions_summary.json")
            
            if os.path.exists(summary_file):
                try:
                    import json
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                    
                    sessions.append(
                        {
                            'session_id': item.replace(
                                'session_', ''), 'mission': summary.get(
                                'mission', summary.get(
                                    'topic', 'Unknown')), 'timestamp': summary.get(
                                'generation_timestamp', ''), 'discussions': summary.get(
                                'discussion_configuration', {}).get(
                                'total_discussions', 0), 'consensus': summary.get(
                                    'overall_metrics', {}).get(
                                        'average_consensus', 0)})
                except BaseException:
                    continue
    
    # Sort by timestamp
    sessions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    click.echo(f"📊 RECENT SESSIONS WITH DISCUSSIONS (Last {recent}):")
    
    for session in sessions[:recent]:
        click.echo(f"\n🎬 Session: {session['session_id']}")
        click.echo(f"   Mission: {session['mission']}")
        click.echo(f"   Discussions: {session['discussions']}")
        click.echo(f"   Avg Consensus: {session['consensus']:.2f}")
        click.echo(f"   Generated: {session['timestamp'][:19]}")


@cli.command()
@click.option('--idea', required=True,
              help='High-level idea or goal (e.g., "convince people to vote")')
@click.option('--platform',
              type=click.Choice(['youtube',
                                 'tiktok',
                                 'instagram',
                                 'twitter']),
              default='youtube',
              help='Target platform')
@click.option('--audience',
              help='Target audience (e.g., "Young adults", "Professionals")')
@click.option('--style',
              help='Content style (e.g., "Engaging", "Educational", "Humorous")')
@click.option('--duration', type=int, default=30,
              help='Target video duration in seconds')
@click.option('--category',
              type=click.Choice(['Comedy',
                                 'Educational',
                                 'Entertainment',
                                 'News',
                                 'Technology']),
              default='Educational',
              help='Video category')
@click.option('--discussions',
              type=click.Choice(['light',
                                 'standard',
                                 'deep']),
              default='standard',
              help='Discussion mode for video generation')
@click.option('--frame-continuity',
              type=click.Choice(['auto',
                                 'on',
                                 'off']),
              default='auto',
              help='Frame continuity mode for video generation')
@click.option('--generate-video', is_flag=True,
              help='Automatically generate video after topic generation')
def generate_topic(
        idea: str,
        platform: str,
        audience: str,
        style: str,
        duration: int,
        category: str,
        discussions: str,
        frame_continuity: str,
        generate_video: bool):
    """🎯 Generate a mission using AI agents"""
    try:
        click.echo(f"🎯 Generating mission for idea: '{idea}'")
        
        # Validate API key
        if not settings.google_api_key:
            click.echo(
                "❌ Error: GOOGLE_API_KEY not found in environment variables")
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
        
        # Generate mission
        generator = TopicGeneratorSystem(settings.google_api_key)
        result = generator.generate_topic(idea, context)
        
        # Display results
        final_mission = result['final_topic']
        click.echo(f"\n✅ Generated Mission: {final_mission['topic']}")
        click.echo(f"📋 Reasoning: {final_mission['reasoning']}")
        click.echo(f"�� Viral Potential: {final_mission['viral_potential']}")
        click.echo(
            f"🛡️ Ethical Considerations: {
                final_mission['ethical_considerations']}")
        click.echo(
            f"📁 Full results saved to: {
                result.get(
                    'session_directory',
                    'outputs/')}")

        # If generate flag is set, automatically generate video with this
        # mission
        if generate_video:
            click.echo(
                f"\n🎬 Automatically generating video with mission: '{
                    final_mission['topic']}'")
            
            # Call the generate command with the generated mission
            from click.testing import CliRunner
            runner = CliRunner()
            
            # Prepare arguments for video generation
            video_args = [
                'generate',
                '--mission', final_mission['topic'],
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
        click.echo(f"❌ Mission generation failed: {e}")
        logger.error(f"Mission generation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli() 
