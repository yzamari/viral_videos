"""
CLI Integration for Social Media Autoposting
Adds autoposting commands to the main CLI interface
"""

import click
import os
from typing import Optional
from ..social.social_config import SocialConfigManager
from ..social.instagram_autoposter import InstagramAutoPoster, InstagramCredentials, PostContent, PostingOptions, create_instagram_autoposter_from_env
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@click.group()
def social():
    """Social media autoposting commands"""
    pass

@social.command()
@click.option('--platform', default='instagram', help='Social media platform')
def setup(platform: str):
    """Setup social media credentials and preferences"""
    try:
        config_manager = SocialConfigManager()
        
        if platform.lower() == 'instagram':
            success = config_manager.setup_instagram_credentials()
            if success:
                click.echo("✅ Instagram setup completed successfully!")
            else:
                click.echo("❌ Instagram setup failed")
        else:
            click.echo(f"❌ Platform '{platform}' not supported yet")
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        click.echo(f"❌ Setup failed: {e}")

@social.command()
@click.option('--platform', default='instagram', help='Social media platform')
def test(platform: str):
    """Test social media credentials"""
    try:
        config_manager = SocialConfigManager()
        
        click.echo(f"🔐 Testing {platform} credentials...")
        
        if config_manager.test_credentials(platform):
            click.echo(f"✅ {platform} credentials are valid")
        else:
            click.echo(f"❌ {platform} credentials are invalid or not configured")
            
    except Exception as e:
        logger.error(f"❌ Credential test failed: {e}")
        click.echo(f"❌ Credential test failed: {e}")

@social.command()
def status():
    """Show social media configuration status"""
    try:
        config_manager = SocialConfigManager()
        summary = config_manager.get_posting_summary()
        
        click.echo("📊 Social Media Configuration Status")
        click.echo("=" * 40)
        
        click.echo(f"Auto-posting: {'✅ Enabled' if summary.get('auto_post_enabled') else '❌ Disabled'}")
        
        platforms = summary.get('configured_platforms', [])
        if platforms:
            click.echo(f"Configured platforms: {', '.join(platforms)}")
        else:
            click.echo("Configured platforms: None")
        
        click.echo(f"Use hashtags: {'✅ Yes' if summary.get('use_hashtags') else '❌ No'}")
        click.echo(f"Max hashtags: {summary.get('max_hashtags', 'N/A')}")
        
        mentions = summary.get('mention_accounts', [])
        if mentions:
            click.echo(f"Default mentions: {', '.join(mentions)}")
        
        if summary.get('location_tagging'):
            click.echo("Location tagging: ✅ Enabled")
        
        click.echo(f"Caption template: {summary.get('default_caption_template', 'Default')}")
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        click.echo(f"❌ Status check failed: {e}")

@social.command()
@click.argument('session_path')
@click.option('--platform', default='instagram', help='Platform to post to')
@click.option('--caption', help='Custom caption (overrides template)')
@click.option('--no-hashtags', is_flag=True, help='Skip hashtags')
@click.option('--schedule', help='Schedule post (format: YYYY-MM-DD HH:MM)')
@click.option('--location', help='Location tag')
@click.option('--mentions', help='Additional mentions (comma-separated)')
def post(session_path: str, platform: str, caption: Optional[str], no_hashtags: bool, 
         schedule: Optional[str], location: Optional[str], mentions: Optional[str]):
    """Post video from session to social media"""
    try:
        if not os.path.exists(session_path):
            click.echo(f"❌ Session path not found: {session_path}")
            return
        
        config_manager = SocialConfigManager()
        
        # Load credentials
        credentials = config_manager.load_credentials(platform)
        if not credentials:
            click.echo(f"❌ No credentials configured for {platform}")
            click.echo(f"💡 Run 'python main.py social setup --platform {platform}' first")
            return
        
        # Load preferences
        preferences = config_manager.load_preferences()
        
        if platform.lower() == 'instagram':
            success = post_to_instagram(
                session_path, credentials, preferences, 
                caption, no_hashtags, schedule, location, mentions
            )
            
            if success:
                click.echo("✅ Video posted successfully!")
            else:
                click.echo("❌ Failed to post video")
        else:
            click.echo(f"❌ Platform '{platform}' not supported yet")
            
    except Exception as e:
        logger.error(f"❌ Posting failed: {e}")
        click.echo(f"❌ Posting failed: {e}")

def post_to_instagram(session_path: str, credentials, preferences, 
                     custom_caption: Optional[str], no_hashtags: bool,
                     schedule: Optional[str], location: Optional[str], 
                     mentions: Optional[str]) -> bool:
    """Post video to Instagram"""
    try:
        # Find video file
        video_path = None
        import glob
        
        logger.info(f"🔍 Looking for video in session: {session_path}")
        
        for ext in ['mp4', 'mov', 'avi']:
            pattern = os.path.join(session_path, 'final_output', f'final_video_*.{ext}')
            logger.debug(f"🔍 Trying pattern: {pattern}")
            matches = glob.glob(pattern)
            logger.debug(f"🔍 Matches: {matches}")
            if matches:
                video_path = matches[0]
                logger.info(f"✅ Found video: {video_path}")
                break
        
        if not video_path:
            logger.error(f"❌ No video file found in session: {session_path}")
            logger.error(f"❌ Checked pattern: {pattern}")
            # Try to list what's actually in the directory
            try:
                final_output_dir = os.path.join(session_path, 'final_output')
                if os.path.exists(final_output_dir):
                    files = os.listdir(final_output_dir)
                    logger.error(f"❌ Files in final_output: {files}")
                else:
                    logger.error(f"❌ final_output directory doesn't exist: {final_output_dir}")
            except Exception as e:
                logger.error(f"❌ Error checking directory: {e}")
            
            click.echo("❌ No video file found in session")
            return False
        
        # Load script for caption
        caption = custom_caption
        if not caption:
            script_file = os.path.join(session_path, 'scripts', 'processed_script.txt')
            if os.path.exists(script_file):
                with open(script_file, 'r') as f:
                    script_content = f.read().strip()
                
                # Apply caption template
                caption = preferences.default_caption_template.format(script=script_content)
        
        # Load hashtags
        hashtags = []
        if not no_hashtags and preferences.always_use_hashtags:
            hashtag_file = os.path.join(session_path, 'hashtags', 'hashtags_text.txt')
            if os.path.exists(hashtag_file):
                with open(hashtag_file, 'r') as f:
                    content = f.read()
                    import re
                    hashtags = re.findall(r'#\w+', content)
                    hashtags = hashtags[:preferences.max_hashtags]
        
        # Process mentions
        mention_list = preferences.mention_accounts.copy() if preferences.mention_accounts else []
        if mentions:
            mention_list.extend([m.strip() for m in mentions.split(',')])
        
        # Create post content
        post_content = PostContent(
            video_path=video_path,
            caption=caption or "",
            hashtags=hashtags,
            location=location or preferences.default_location,
            mentions=mention_list,
            is_reel=True
        )
        
        # Create posting options
        posting_options = PostingOptions()
        
        if schedule:
            from datetime import datetime
            try:
                schedule_time = datetime.strptime(schedule, '%Y-%m-%d %H:%M')
                posting_options.post_immediately = False
                posting_options.schedule_time = schedule_time
            except ValueError:
                click.echo("❌ Invalid schedule format. Use YYYY-MM-DD HH:MM")
                return False
        
        # Initialize autoposter
        ig_credentials = InstagramCredentials(
            username=credentials.username,
            password=credentials.password,
            two_factor_code=credentials.two_factor_code
        )
        
        autoposter = InstagramAutoPoster(ig_credentials)
        
        # Validate video
        if not autoposter.validate_video_format(video_path):
            click.echo("❌ Video format validation failed")
            return False
        
        # Authenticate and post
        click.echo("🔐 Authenticating with Instagram...")
        if not autoposter.authenticate():
            click.echo("❌ Instagram authentication failed")
            click.echo("💡 Instagram has strict security measures that may block automated login")
            click.echo("🔧 Consider using Instagram API or manual posting for now")
            return False
        
        click.echo("📱 Posting video to Instagram...")
        success = autoposter.post_video(post_content, posting_options)
        
        autoposter.disconnect()
        return success
        
    except Exception as e:
        logger.error(f"❌ Instagram posting failed: {e}")
        return False

@social.command()
@click.option('--platform', default='instagram', help='Platform to remove')
def remove(platform: str):
    """Remove social media credentials"""
    try:
        config_manager = SocialConfigManager()
        
        if click.confirm(f"Are you sure you want to remove {platform} credentials?"):
            if config_manager.delete_credentials(platform):
                click.echo(f"✅ {platform} credentials removed")
            else:
                click.echo(f"❌ Failed to remove {platform} credentials")
        
    except Exception as e:
        logger.error(f"❌ Removal failed: {e}")
        click.echo(f"❌ Removal failed: {e}")

# Integration function to add to main CLI
def add_social_commands(cli_group):
    """Add social media commands to main CLI"""
    cli_group.add_command(social)

# Auto-posting integration for video generation
def auto_post_if_enabled(session_path: str) -> bool:
    """Automatically post if auto-posting is enabled"""
    try:
        # Extract session directory from video path if needed
        if session_path.endswith('.mp4') or session_path.endswith('.mov') or session_path.endswith('.avi'):
            # session_path is actually a video file path, extract session directory
            session_dir = os.path.dirname(os.path.dirname(session_path))  # Go up from final_output/video.mp4 to session/
            logger.info(f"📁 Extracted session directory from video path: {session_dir}")
        else:
            session_dir = session_path
            
        config_manager = SocialConfigManager()
        preferences = config_manager.load_preferences()
        
        if not preferences.auto_post:
            return True  # Not enabled, but not an error
        
        success_count = 0
        total_platforms = len(preferences.platforms)
        
        for platform in preferences.platforms:
            logger.info(f"📱 Auto-posting to {platform}...")
            
            if platform.lower() == 'instagram':
                # Use the new factory function to load credentials from .env
                autoposter = create_instagram_autoposter_from_env()
                if not autoposter:
                    logger.warning(f"⚠️ No Instagram credentials found in .env file, skipping")
                    continue
                
                success = post_to_instagram_auto(
                    session_dir, autoposter, preferences,
                    None, False, None, None, None
                )
                
                if success:
                    success_count += 1
                    logger.info(f"✅ Auto-posted to {platform}")
                else:
                    logger.error(f"❌ Failed to auto-post to {platform}")
            else:
                # Handle other platforms with existing method
                credentials = config_manager.load_credentials(platform)
                if not credentials:
                    logger.warning(f"⚠️ No credentials for {platform}, skipping")
                    continue
                
                if platform.lower() == 'instagram':
                    success = post_to_instagram(
                        session_dir, credentials, preferences,
                        None, False, None, None, None
                    )
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ Auto-posted to {platform}")
                    else:
                        logger.error(f"❌ Failed to auto-post to {platform}")
        
        if success_count == total_platforms:
            logger.info("✅ All auto-posts completed successfully")
            return True
        elif success_count > 0:
            logger.warning(f"⚠️ {success_count}/{total_platforms} auto-posts successful")
            return True
        else:
            logger.error("❌ All auto-posts failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Auto-posting failed: {e}")
        return False

def post_to_instagram_auto(session_path: str, autoposter: InstagramAutoPoster, preferences, 
                          custom_caption: Optional[str], no_hashtags: bool,
                          schedule: Optional[str], location: Optional[str], 
                          mentions: Optional[str]) -> bool:
    """Post video to Instagram using autoposter instance"""
    try:
        # Find video file
        video_path = None
        import glob
        
        logger.info(f"🔍 Looking for video in session: {session_path}")
        
        for ext in ['mp4', 'mov', 'avi']:
            pattern = os.path.join(session_path, 'final_output', f'final_video_*.{ext}')
            logger.debug(f"🔍 Trying pattern: {pattern}")
            matches = glob.glob(pattern)
            logger.debug(f"🔍 Matches: {matches}")
            if matches:
                video_path = matches[0]
                logger.info(f"✅ Found video: {video_path}")
                break
        
        if not video_path:
            logger.error(f"❌ No video file found in session: {session_path}")
            return False
        
        # Load script for caption
        caption = custom_caption
        if not caption:
            script_file = os.path.join(session_path, 'scripts', 'processed_script.txt')
            if os.path.exists(script_file):
                with open(script_file, 'r') as f:
                    script_content = f.read().strip()
                
                # Apply caption template
                caption = preferences.default_caption_template.format(script=script_content)
        
        # Load hashtags
        hashtags = []
        if not no_hashtags and preferences.always_use_hashtags:
            hashtag_file = os.path.join(session_path, 'hashtags', 'hashtags_text.txt')
            if os.path.exists(hashtag_file):
                with open(hashtag_file, 'r') as f:
                    content = f.read()
                    import re
                    hashtags = re.findall(r'#\w+', content)
                    hashtags = hashtags[:preferences.max_hashtags]
        
        # Process mentions
        mention_list = preferences.mention_accounts.copy() if preferences.mention_accounts else []
        if mentions:
            mention_list.extend([m.strip() for m in mentions.split(',')])
        
        # Create post content
        post_content = PostContent(
            video_path=video_path,
            caption=caption or "",
            hashtags=hashtags,
            location=location or preferences.default_location,
            mentions=mention_list,
            is_reel=True
        )
        
        # Create posting options
        posting_options = PostingOptions()
        
        if schedule:
            from datetime import datetime
            try:
                schedule_time = datetime.strptime(schedule, '%Y-%m-%d %H:%M')
                posting_options.post_immediately = False
                posting_options.schedule_time = schedule_time
            except ValueError:
                logger.error("❌ Invalid schedule format. Use YYYY-MM-DD HH:MM")
                return False
        
        # Validate video
        if not autoposter.validate_video_format(video_path):
            logger.error("❌ Video format validation failed")
            return False
        
        # Authenticate and post
        logger.info("🔐 Authenticating with Instagram...")
        if not autoposter.authenticate():
            logger.error("❌ Instagram authentication failed")
            return False
        
        logger.info("📱 Posting video to Instagram...")
        success = autoposter.post_video(post_content, posting_options)
        
        autoposter.disconnect()
        return success
        
    except Exception as e:
        logger.error(f"❌ Instagram posting failed: {e}")
        return False