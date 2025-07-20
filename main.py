#!/usr/bin/env python3
"""AI Video Generator - Main Entry Point
Comprehensive AI-powered video generation system with VEO-2/3, multi-agent discussions, and session management
"""
import os
import sys
import click
from pathlib import Path
import traceback

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import core modules
from src.generators.veo_client_factory import VeoClientFactory
from src.utils.auto_auth_handler import AutoAuthHandler
from src.utils.gcloud_auth_tester import test_gcloud_authentication
from src.utils.logging_config import get_logger
from src.social.cli_integration import add_social_commands, auto_post_if_enabled

logger = get_logger(__name__)

def handle_authentication_automatically():
    """Automatically handle authentication problems
    
    Returns:
        True if authentication is working, False otherwise
    """
    try:
        # Initialize auth handler
        auth_handler = AutoAuthHandler()
        
        # Quick check first
        status = auth_handler.quick_auth_check()
        if status.get("overall_ready", False):
            logger.info("✅ Authentication already configured")
            return True
        
        # Auto-fix authentication issues
        logger.info("🔧 Detected authentication issues, auto-fixing...")
        return auth_handler.auto_fix_authentication()
        
    except Exception as e:
        logger.error(f"❌ Auto-authentication failed: {e}")
        return False


@click.group()
def cli():
    """🎬 AI Video Generator - Create viral videos with AI agents"""
    pass


@cli.command()
def test_auth():
    """🔐 Test Google Cloud authentication comprehensively"""
    try:
        # Initialize VEO factory (this will show if it's working)
        veo_factory = VeoClientFactory()
        print("🔐 Testing Google Cloud authentication...")
        
        # Run comprehensive authentication test
        results = test_gcloud_authentication()
        
        # Check if we can run the app
        analysis = results.get('analysis', {})
        can_run = analysis.get('can_run_app', False)
        
        if can_run:
            print("✅ Authentication tests passed!")
        else:
            print("❌ Authentication tests failed!")
            # Try to auto-fix
            if handle_authentication_automatically():
                print("✅ Authentication auto-fixed!")
            else:
                print("❌ Could not auto-fix authentication")
                sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--category', type=click.Choice(['Comedy', 'Educational', 'Entertainment', 'News', 'Tech']), help='Video category')
@click.option('--mission', required=True, help='Video mission - what you want to accomplish')
@click.option('--platform', type=click.Choice(['youtube', 'tiktok', 'instagram', 'twitter']), help='Target platform')
@click.option('--duration', type=int, default=20, help='Video duration in seconds (default: 20)')
@click.option('--image-only', is_flag=True, help='Force image-only generation (Gemini images)')
@click.option('--fallback-only', is_flag=True, help='Use fallback generation only')
@click.option('--force', is_flag=True, help='Force generation even with quota warnings')
@click.option('--skip-auth-test', is_flag=True, help='Skip authentication test (not recommended)')
@click.option('--discussions', type=click.Choice(['off', 'light', 'standard', 'deep', 'streamlined', 'enhanced']), default='enhanced', help='AI agent mode (default: enhanced with discussions for best viral content)')
@click.option('--discussion-log', is_flag=True, help='Show detailed discussion logs')
@click.option('--session-id', help='Custom session ID')
@click.option('--frame-continuity', type=click.Choice(['auto', 'on', 'off']), default='auto', help='Frame continuity mode: auto (AI decides), on (always enabled), off (disabled)')
@click.option('--target-audience', help='Target audience (e.g., "young adults", "professionals")')
@click.option('--style', help='Content style (e.g., "viral", "educational", "professional")')
@click.option('--tone', help='Content tone (e.g., "engaging", "professional", "humorous")')
@click.option('--visual-style', help='Visual style (e.g., "dynamic", "minimalist", "professional")')
@click.option('--mode', type=click.Choice(['simple', 'enhanced', 'advanced', 'professional']), default='enhanced', help='Orchestrator mode (simple=3 agents, enhanced=7 agents, advanced=15 agents, professional=19 agents)')
@click.option('--auto-post', is_flag=True, help='Automatically post to configured social media platforms')
@click.option('--cheap/--no-cheap', default=True, help='Enable basic cheap mode (default: enabled)')
@click.option('--cheap-mode', type=click.Choice(['full', 'audio', 'video']), default='full', help='Cheap mode level: full=text+gTTS, audio=gTTS only, video=fallback only (default: full)')
def generate(**kwargs):
    """🎬 Generate viral video with optimized AI system"""
    try:
        # Test authentication first (unless skipped)
        if not kwargs.get('skip_auth_test', False):
            logger.info("🔐 Checking authentication...")
            if not handle_authentication_automatically():
                logger.error("❌ Authentication failed")
                print("\n🔧 Try running: python main.py test-auth")
                sys.exit(1)
        
        # Import and run the generation
        from src.workflows.generate_viral_video import main as generate_main
        
        # Convert click options to the format expected by the workflow
        session_path = generate_main(
            mission=kwargs['mission'],
            category=kwargs.get('category', 'Comedy'),
            platform=kwargs.get('platform', 'tiktok'),
            duration=kwargs.get('duration', 20),
            image_only=kwargs.get('image_only', False),
            fallback_only=kwargs.get('fallback_only', False),
            force=kwargs.get('force', False),
            discussions=kwargs.get('discussions', 'enhanced'),
            discussion_log=kwargs.get('discussion_log', False),
            session_id=kwargs.get('session_id'),
            frame_continuity=kwargs.get('frame_continuity', 'on'),
            target_audience=kwargs.get('target_audience'),
            style=kwargs.get('style'),
            tone=kwargs.get('tone'),
            visual_style=kwargs.get('visual_style'),
            mode=kwargs.get('mode', 'enhanced'),
            cheap_mode=kwargs.get('cheap', True),
            cheap_mode_level=kwargs.get('cheap_mode', 'full')
        )
        
        # Auto-post if requested
        if kwargs.get('auto_post', False) and session_path:
            logger.info("📱 Auto-posting to social media...")
            # Get the final video path from session
            import os
            final_video_path = os.path.join(session_path, 'final_output', f'final_video_{session_name}.mp4')
            if os.path.exists(final_video_path):
                auto_post_if_enabled(
                    video_path=final_video_path,
                    mission=kwargs.get('mission', ''),
                    platform=kwargs.get('platform', 'tiktok')
                )
            else:
                logger.error(f"❌ Final video not found at: {final_video_path}")
    
    except KeyboardInterrupt:
        print("\n🛑 Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        traceback.print_exc()
        sys.exit(1)
    

# Add social media commands
add_social_commands(cli)

if __name__ == '__main__':
    cli() 
