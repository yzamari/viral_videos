#!/usr/bin/env python3
"""
CLI Integration for Social Media Features
Provides command-line interface for WhatsApp and Telegram integration
"""

import click
import os
import json
from typing import List, Optional

from .social_media_manager import SocialMediaManager
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@click.group()
def social():
    """Social Media Management Commands"""
    pass

@social.command()
@click.option('--config', default='config/social_media.json', help='Configuration file path')
def status(config):
    """Show social media platform status"""
    try:
        config_path = config if os.path.exists(config) else None
        manager = SocialMediaManager(config_path) if config_path else SocialMediaManager()
        status_info = manager.get_status()
        
        click.echo("📱 Social Media Platform Status")
        click.echo("=" * 40)
        
        for platform, info in status_info.items():
            status_emoji = "✅" if info['configured'] else "❌"
            enabled_emoji = "🟢" if info['enabled'] else "🔴"
            
            click.echo(f"{status_emoji} {platform.title()}:")
            click.echo(f"   Status: {enabled_emoji} {'Enabled' if info['enabled'] else 'Disabled'}")
            click.echo(f"   Configured: {'Yes' if info['configured'] else 'No'}")
            click.echo(f"   Target Groups: {info['groups_count']}")
            click.echo()
        
        # Show analytics
        analytics = manager.get_sending_analytics()
        click.echo("📊 Analytics:")
        click.echo(f"   Total Videos Sent: {analytics['total_sent']}")
        click.echo(f"   Success Rate: {analytics['success_rate']:.1%}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@social.command()
@click.option('--access-token', envvar='WHATSAPP_ACCESS_TOKEN', help='WhatsApp access token')
@click.option('--phone-number-id', envvar='WHATSAPP_PHONE_NUMBER_ID', help='WhatsApp phone number ID')
@click.option('--verify-token', envvar='WHATSAPP_VERIFY_TOKEN', help='WhatsApp verify token')
@click.option('--enabled/--disabled', default=True, help='Enable/disable WhatsApp')
def configure_whatsapp(access_token, phone_number_id, verify_token, enabled):
    """Configure WhatsApp integration"""
    if not access_token or not phone_number_id:
        click.echo("❌ WhatsApp access token and phone number ID are required")
        click.echo("   Set environment variables or use --access-token and --phone-number-id")
        return
    
    try:
        manager = SocialMediaManager()
        manager.configure_whatsapp(
            access_token=access_token,
            phone_number_id=phone_number_id,
            verify_token=verify_token,
            enabled=enabled
        )
        
        click.echo(f"✅ WhatsApp configured successfully (enabled: {enabled})")
        
        # Validate credentials
        if manager.whatsapp_sender and manager.whatsapp_sender.validate_credentials():
            click.echo("✅ WhatsApp credentials validated")
        else:
            click.echo("⚠️ WhatsApp credentials validation failed")
            
    except Exception as e:
        click.echo(f"❌ Error configuring WhatsApp: {e}")

@social.command()
@click.option('--bot-token', envvar='TELEGRAM_BOT_TOKEN', help='Telegram bot token')
@click.option('--bot-username', envvar='TELEGRAM_BOT_USERNAME', help='Telegram bot username')
@click.option('--enabled/--disabled', default=True, help='Enable/disable Telegram')
def configure_telegram(bot_token, bot_username, enabled):
    """Configure Telegram integration"""
    if not bot_token:
        click.echo("❌ Telegram bot token is required")
        click.echo("   Set TELEGRAM_BOT_TOKEN environment variable or use --bot-token")
        return
    
    try:
        manager = SocialMediaManager()
        manager.configure_telegram(
            bot_token=bot_token,
            bot_username=bot_username,
            enabled=enabled
        )
        
        click.echo(f"✅ Telegram configured successfully (enabled: {enabled})")
        
        # Validate credentials
        if manager.telegram_sender and manager.telegram_sender.validate_credentials():
            click.echo("✅ Telegram credentials validated")
        else:
            click.echo("⚠️ Telegram credentials validation failed")
            
    except Exception as e:
        click.echo(f"❌ Error configuring Telegram: {e}")

@social.command()
@click.argument('group_id')
def add_whatsapp_group(group_id):
    """Add WhatsApp group to target list"""
    try:
        manager = SocialMediaManager()
        manager.add_whatsapp_group(group_id)
        click.echo(f"✅ WhatsApp group added: {group_id}")
        
    except Exception as e:
        click.echo(f"❌ Error adding WhatsApp group: {e}")

@social.command()
@click.argument('chat_id')
def add_telegram_group(chat_id):
    """Add Telegram group to target list"""
    try:
        manager = SocialMediaManager()
        manager.add_telegram_group(chat_id)
        click.echo(f"✅ Telegram group added: {chat_id}")
        
    except Exception as e:
        click.echo(f"❌ Error adding Telegram group: {e}")

@social.command()
@click.argument('group_id')
def remove_whatsapp_group(group_id):
    """Remove WhatsApp group from target list"""
    try:
        manager = SocialMediaManager()
        manager.remove_whatsapp_group(group_id)
        click.echo(f"✅ WhatsApp group removed: {group_id}")
        
    except Exception as e:
        click.echo(f"❌ Error removing WhatsApp group: {e}")

@social.command()
@click.argument('chat_id')
def remove_telegram_group(chat_id):
    """Remove Telegram group from target list"""
    try:
        manager = SocialMediaManager()
        manager.remove_telegram_group(chat_id)
        click.echo(f"✅ Telegram group removed: {chat_id}")
        
    except Exception as e:
        click.echo(f"❌ Error removing Telegram group: {e}")

@social.command()
@click.argument('video_path')
@click.argument('mission')
@click.argument('platform')
@click.option('--hashtags', '-h', multiple=True, help='Hashtags to include')
@click.option('--caption', '-c', help='Custom caption')
@click.option('--config', default='config/social_media.json', help='Configuration file path')
def send_video(video_path, mission, platform, hashtags, caption, config):
    """Send video to all configured social media platforms"""
    if not os.path.exists(video_path):
        click.echo(f"❌ Video file not found: {video_path}")
        return
    
    try:
        config_path = config if os.path.exists(config) else None
        manager = SocialMediaManager(config_path) if config_path else SocialMediaManager()
        
        click.echo(f"📤 Sending video to social media platforms...")
        click.echo(f"   Video: {video_path}")
        click.echo(f"   Mission: {mission}")
        click.echo(f"   Platform: {platform}")
        click.echo(f"   Hashtags: {list(hashtags)}")
        
        hashtags_list = list(hashtags) if hashtags else []
        results = manager.send_video_to_all_platforms(
            video_path=video_path,
            mission=mission,
            platform=platform,
            hashtags=hashtags_list,
            custom_caption=caption
        )
        
        click.echo("\n📊 Results:")
        for platform_name, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            click.echo(f"   {platform_name.title()}: {status}")
        
        if any(results.values()):
            click.echo("\n🎉 Video sent successfully!")
        else:
            click.echo("\n❌ Failed to send to any platform")
            
    except Exception as e:
        click.echo(f"❌ Error sending video: {e}")

@social.command()
@click.option('--config', default='config/social_media.json', help='Configuration file path')
def analytics(config):
    """Show social media analytics"""
    try:
        config_path = config if os.path.exists(config) else None
        manager = SocialMediaManager(config_path) if config_path else SocialMediaManager()
        analytics_data = manager.get_sending_analytics()
        
        click.echo("📊 Social Media Analytics")
        click.echo("=" * 40)
        click.echo(f"Total Videos Sent: {analytics_data['total_sent']}")
        click.echo(f"Success Rate: {analytics_data['success_rate']:.1%}")
        
        if analytics_data['platform_breakdown']:
            click.echo("\nPlatform Breakdown:")
            for platform, stats in analytics_data['platform_breakdown'].items():
                success_rate = stats['success_rate']
                click.echo(f"   {platform.title()}: {stats['successful']}/{stats['total']} ({success_rate:.1%})")
        
        if analytics_data['recent_activity']:
            click.echo("\nRecent Activity:")
            for entry in analytics_data['recent_activity'][-5:]:  # Last 5 entries
                timestamp = entry['timestamp'][:19]  # Remove microseconds
                success = "✅" if entry['success'] else "❌"
                click.echo(f"   {timestamp} {success} {entry['mission']}")
                
    except Exception as e:
        click.echo(f"❌ Error getting analytics: {e}")

@social.command()
@click.option('--config', default='config/social_media.json', help='Configuration file path')
def list_groups(config):
    """List all configured groups"""
    try:
        config_path = config if os.path.exists(config) else None
        manager = SocialMediaManager(config_path) if config_path else SocialMediaManager()
        
        click.echo("📋 Configured Groups")
        click.echo("=" * 40)
        
        # WhatsApp groups
        if manager.configs.get('whatsapp'):
            whatsapp_config = manager.configs['whatsapp']
            click.echo(f"📱 WhatsApp Groups ({len(whatsapp_config.target_groups)}):")
            for group_id in whatsapp_config.target_groups:
                click.echo(f"   {group_id}")
            click.echo()
        
        # Telegram groups
        if manager.configs.get('telegram'):
            telegram_config = manager.configs['telegram']
            click.echo(f"📱 Telegram Groups ({len(telegram_config.target_groups)}):")
            for chat_id in telegram_config.target_groups:
                click.echo(f"   {chat_id}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Error listing groups: {e}")

@social.command()
@click.option('--config', default='config/social_media.json', help='Configuration file path')
def save_config(config):
    """Save current configuration to file"""
    try:
        manager = SocialMediaManager()
        manager.save_config(config)
        click.echo(f"✅ Configuration saved to {config}")
        
    except Exception as e:
        click.echo(f"❌ Error saving configuration: {e}")

@social.command()
def setup_guide():
    """Show setup guide for social media integration"""
    click.echo("🚀 Social Media Integration Setup Guide")
    click.echo("=" * 50)
    
    click.echo("\n📱 WhatsApp Business API Setup:")
    click.echo("1. Create Facebook Developer account at developers.facebook.com")
    click.echo("2. Create a new app with 'Business' type")
    click.echo("3. Add WhatsApp product to your app")
    click.echo("4. Configure WhatsApp Business API")
    click.echo("5. Get your access token and phone number ID")
    click.echo("6. Set environment variables:")
    click.echo("   export WHATSAPP_ACCESS_TOKEN='your_token'")
    click.echo("   export WHATSAPP_PHONE_NUMBER_ID='your_phone_id'")
    
    click.echo("\n📱 Telegram Bot Setup:")
    click.echo("1. Open Telegram and search for @BotFather")
    click.echo("2. Send /newbot command")
    click.echo("3. Follow instructions to create your bot")
    click.echo("4. Save the bot token provided")
    click.echo("5. Add bot to target groups")
    click.echo("6. Set environment variable:")
    click.echo("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
    
    click.echo("\n🔧 Configuration:")
    click.echo("1. Copy example config:")
    click.echo("   cp config/social_media.example.json config/social_media.json")
    click.echo("2. Edit config file with your credentials")
    click.echo("3. Add target groups using CLI commands")
    click.echo("4. Test with: python -m src.social.cli_integration status")
    
    click.echo("\n📤 Usage:")
    click.echo("python -m src.social.cli_integration send-video video.mp4 'Mission' instagram -h hashtag1 -h hashtag2")

def add_social_commands(cli_group):
    """Add social media commands to main CLI"""
    cli_group.add_command(social)

def auto_post_if_enabled(video_path: str, mission: str, platform: str, 
                        hashtags: List[str] = None, config_path: str = None) -> bool:
    """
    Automatically post video if social media integration is enabled
    
    Args:
        video_path: Path to the generated video
        mission: Video mission/topic
        platform: Target platform
        hashtags: List of hashtags
        config_path: Path to social media config file
        
    Returns:
        True if posted successfully, False otherwise
    """
    try:
        # Check if config file exists
        if not config_path:
            config_path = 'config/social_media.json'
        
        if not os.path.exists(config_path):
            logger.info("📱 No social media config found, skipping auto-post")
            return False
        
        # Initialize manager
        manager = SocialMediaManager(config_path) if config_path else SocialMediaManager()
        
        # Check if any platform is enabled
        status = manager.get_status()
        enabled_platforms = [p for p, info in status.items() if info['enabled'] and info['configured']]
        
        if not enabled_platforms:
            logger.info("📱 No social media platforms enabled, skipping auto-post")
            return False
        
        logger.info(f"📱 Auto-posting to platforms: {', '.join(enabled_platforms)}")
        
        # Send video
        hashtags_list = hashtags if hashtags else []
        results = manager.send_video_to_all_platforms(
            video_path=video_path,
            mission=mission,
            platform=platform,
            hashtags=hashtags_list
        )
        
        # Log results
        success_count = sum(1 for success in results.values() if success)
        total_platforms = len(results)
        
        if success_count > 0:
            logger.info(f"✅ Auto-post successful: {success_count}/{total_platforms} platforms")
            return True
        else:
            logger.warning(f"⚠️ Auto-post failed: 0/{total_platforms} platforms")
            return False
            
    except Exception as e:
        logger.error(f"❌ Auto-post error: {e}")
        return False