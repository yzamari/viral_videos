#!/usr/bin/env python3
"""
Social Media Manager
Unified interface for sending ViralAI videos to WhatsApp and Telegram groups
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

from .whatsapp_sender import WhatsAppSender
from .telegram_sender import TelegramSender
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class SocialMediaConfig:
    """Configuration for social media platforms"""
    platform: str
    enabled: bool
    credentials: Dict[str, Any]
    target_groups: List[str]
    auto_send: bool = True
    include_caption: bool = True
    include_hashtags: bool = True

class SocialMediaManager:
    """
    Unified social media manager for ViralAI
    
    Supports:
    - WhatsApp Business API integration
    - Telegram Bot API integration
    - Multi-platform video distribution
    - Automated posting workflows
    - Delivery tracking and analytics
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize social media manager
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.whatsapp_sender = None
        self.telegram_sender = None
        self.configs = {}
        self.sending_history = []
        
        # Load configuration
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        else:
            self._load_default_config()
        
        # Initialize senders
        self._initialize_senders()
        
        logger.info("📱 Social Media Manager initialized")
        logger.info(f"   WhatsApp: {'✅' if self.whatsapp_sender else '❌'}")
        logger.info(f"   Telegram: {'✅' if self.telegram_sender else '❌'}")
    
    def _load_default_config(self):
        """Load default configuration"""
        self.configs = {
            'whatsapp': SocialMediaConfig(
                platform='whatsapp',
                enabled=False,
                credentials={},
                target_groups=[],
                auto_send=True,
                include_caption=True,
                include_hashtags=True
            ),
            'telegram': SocialMediaConfig(
                platform='telegram',
                enabled=False,
                credentials={},
                target_groups=[],
                auto_send=True,
                include_caption=True,
                include_hashtags=True
            )
        }
    
    def load_config(self, config_path: str):
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            for platform, config in config_data.items():
                self.configs[platform] = SocialMediaConfig(**config)
            
            logger.info(f"✅ Configuration loaded from {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            self._load_default_config()
    
    def save_config(self, config_path: str):
        """Save configuration to file"""
        try:
            config_data = {}
            for platform, config in self.configs.items():
                config_data[platform] = {
                    'platform': config.platform,
                    'enabled': config.enabled,
                    'credentials': config.credentials,
                    'target_groups': config.target_groups,
                    'auto_send': config.auto_send,
                    'include_caption': config.include_caption,
                    'include_hashtags': config.include_hashtags
                }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"✅ Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
    
    def _initialize_senders(self):
        """Initialize platform senders"""
        # Initialize WhatsApp sender
        if (self.configs.get('whatsapp') and 
            self.configs['whatsapp'].enabled and 
            self.configs['whatsapp'].credentials):
            
            try:
                creds = self.configs['whatsapp'].credentials
                self.whatsapp_sender = WhatsAppSender(
                    access_token=creds.get('access_token'),
                    phone_number_id=creds.get('phone_number_id'),
                    verify_token=creds.get('verify_token')
                )
                
                # Validate credentials
                if not self.whatsapp_sender.validate_credentials():
                    logger.warning("⚠️ WhatsApp credentials validation failed")
                    self.whatsapp_sender = None
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize WhatsApp sender: {e}")
                self.whatsapp_sender = None
        
        # Initialize Telegram sender
        if (self.configs.get('telegram') and 
            self.configs['telegram'].enabled and 
            self.configs['telegram'].credentials):
            
            try:
                creds = self.configs['telegram'].credentials
                self.telegram_sender = TelegramSender(
                    bot_token=creds.get('bot_token'),
                    bot_username=creds.get('bot_username')
                )
                
                # Validate credentials
                if not self.telegram_sender.validate_credentials():
                    logger.warning("⚠️ Telegram credentials validation failed")
                    self.telegram_sender = None
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize Telegram sender: {e}")
                self.telegram_sender = None
    
    def send_video_to_all_platforms(self, video_path: str, mission: str, 
                                   platform: str, hashtags: List[str] = None,
                                   custom_caption: str = None) -> Dict[str, bool]:
        """
        Send video to all configured social media platforms
        
        Args:
            video_path: Path to the video file
            mission: Video mission/topic
            platform: Target platform (instagram, tiktok, etc.)
            hashtags: List of hashtags to include
            custom_caption: Custom caption (overrides default)
            
        Returns:
            Dictionary with platform results
        """
        results = {}
        
        # Send to WhatsApp
        if self.whatsapp_sender and self.configs['whatsapp'].auto_send:
            results['whatsapp'] = self._send_to_whatsapp(
                video_path, mission, platform, hashtags, custom_caption
            )
        else:
            results['whatsapp'] = False
        
        # Send to Telegram
        if self.telegram_sender and self.configs['telegram'].auto_send:
            results['telegram'] = self._send_to_telegram(
                video_path, mission, platform, hashtags, custom_caption
            )
        else:
            results['telegram'] = False
        
        # Record sending history
        self._record_sending_history(video_path, mission, platform, results)
        
        return results
    
    def _send_to_whatsapp(self, video_path: str, mission: str, platform: str,
                         hashtags: List[str] = None, custom_caption: str = None) -> bool:
        """Send video to WhatsApp groups"""
        try:
            config = self.configs['whatsapp']
            success_count = 0
            total_groups = len(config.target_groups)
            
            for group_id in config.target_groups:
                try:
                    success = self.whatsapp_sender.send_viral_video_package(
                        group_id, video_path, mission, platform, hashtags
                    )
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ WhatsApp: Video sent to group {group_id}")
                    else:
                        logger.error(f"❌ WhatsApp: Failed to send to group {group_id}")
                    
                    # Small delay between groups
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ WhatsApp: Error sending to group {group_id}: {e}")
            
            success_rate = success_count / total_groups if total_groups > 0 else 0
            logger.info(f"📊 WhatsApp: {success_count}/{total_groups} groups successful ({success_rate:.1%})")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ WhatsApp sending error: {e}")
            return False
    
    def _send_to_telegram(self, video_path: str, mission: str, platform: str,
                         hashtags: List[str] = None, custom_caption: str = None) -> bool:
        """Send video to Telegram groups"""
        try:
            config = self.configs['telegram']
            success_count = 0
            total_groups = len(config.target_groups)
            
            for chat_id in config.target_groups:
                try:
                    success = self.telegram_sender.send_viral_video_package(
                        chat_id, video_path, mission, platform, hashtags
                    )
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ Telegram: Video sent to chat {chat_id}")
                    else:
                        logger.error(f"❌ Telegram: Failed to send to chat {chat_id}")
                    
                    # Small delay between groups
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Telegram: Error sending to chat {chat_id}: {e}")
            
            success_rate = success_count / total_groups if total_groups > 0 else 0
            logger.info(f"📊 Telegram: {success_count}/{total_groups} chats successful ({success_rate:.1%})")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Telegram sending error: {e}")
            return False
    
    def _record_sending_history(self, video_path: str, mission: str, platform: str, results: Dict[str, bool]):
        """Record sending history for analytics"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'video_path': video_path,
            'mission': mission,
            'platform': platform,
            'results': results,
            'success': any(results.values())
        }
        
        self.sending_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.sending_history) > 100:
            self.sending_history = self.sending_history[-100:]
    
    def get_sending_analytics(self) -> Dict[str, Any]:
        """Get sending analytics"""
        if not self.sending_history:
            return {'total_sent': 0, 'success_rate': 0, 'platform_breakdown': {}}
        
        total_sent = len(self.sending_history)
        successful = sum(1 for entry in self.sending_history if entry['success'])
        success_rate = successful / total_sent
        
        # Platform breakdown
        platform_stats = {}
        for entry in self.sending_history:
            for platform, success in entry['results'].items():
                if platform not in platform_stats:
                    platform_stats[platform] = {'total': 0, 'successful': 0}
                
                platform_stats[platform]['total'] += 1
                if success:
                    platform_stats[platform]['successful'] += 1
        
        # Calculate platform success rates
        for platform in platform_stats:
            stats = platform_stats[platform]
            stats['success_rate'] = stats['successful'] / stats['total']
        
        return {
            'total_sent': total_sent,
            'success_rate': success_rate,
            'platform_breakdown': platform_stats,
            'recent_activity': self.sending_history[-10:]  # Last 10 entries
        }
    
    def add_whatsapp_group(self, group_id: str):
        """Add WhatsApp group to target list"""
        if 'whatsapp' not in self.configs:
            self.configs['whatsapp'] = SocialMediaConfig(
                platform='whatsapp',
                enabled=False,
                credentials={},
                target_groups=[],
                auto_send=True,
                include_caption=True,
                include_hashtags=True
            )
        
        if group_id not in self.configs['whatsapp'].target_groups:
            self.configs['whatsapp'].target_groups.append(group_id)
            logger.info(f"✅ WhatsApp group added: {group_id}")
    
    def add_telegram_group(self, chat_id: Union[str, int]):
        """Add Telegram group to target list"""
        if 'telegram' not in self.configs:
            self.configs['telegram'] = SocialMediaConfig(
                platform='telegram',
                enabled=False,
                credentials={},
                target_groups=[],
                auto_send=True,
                include_caption=True,
                include_hashtags=True
            )
        
        chat_id_str = str(chat_id)
        if chat_id_str not in self.configs['telegram'].target_groups:
            self.configs['telegram'].target_groups.append(chat_id_str)
            logger.info(f"✅ Telegram group added: {chat_id_str}")
    
    def remove_whatsapp_group(self, group_id: str):
        """Remove WhatsApp group from target list"""
        if ('whatsapp' in self.configs and 
            group_id in self.configs['whatsapp'].target_groups):
            self.configs['whatsapp'].target_groups.remove(group_id)
            logger.info(f"✅ WhatsApp group removed: {group_id}")
    
    def remove_telegram_group(self, chat_id: Union[str, int]):
        """Remove Telegram group from target list"""
        chat_id_str = str(chat_id)
        if ('telegram' in self.configs and 
            chat_id_str in self.configs['telegram'].target_groups):
            self.configs['telegram'].target_groups.remove(chat_id_str)
            logger.info(f"✅ Telegram group removed: {chat_id_str}")
    
    def configure_whatsapp(self, access_token: str, phone_number_id: str, 
                          verify_token: str = None, enabled: bool = True):
        """Configure WhatsApp settings"""
        if 'whatsapp' not in self.configs:
            self.configs['whatsapp'] = SocialMediaConfig(
                platform='whatsapp',
                enabled=enabled,
                credentials={},
                target_groups=[],
                auto_send=True,
                include_caption=True,
                include_hashtags=True
            )
        
        self.configs['whatsapp'].enabled = enabled
        self.configs['whatsapp'].credentials = {
            'access_token': access_token,
            'phone_number_id': phone_number_id,
            'verify_token': verify_token
        }
        
        # Reinitialize sender
        self._initialize_senders()
        
        logger.info(f"✅ WhatsApp configured (enabled: {enabled})")
    
    def configure_telegram(self, bot_token: str, bot_username: str = None, 
                          enabled: bool = True):
        """Configure Telegram settings"""
        if 'telegram' not in self.configs:
            self.configs['telegram'] = SocialMediaConfig(
                platform='telegram',
                enabled=enabled,
                credentials={},
                target_groups=[],
                auto_send=True,
                include_caption=True,
                include_hashtags=True
            )
        
        self.configs['telegram'].enabled = enabled
        self.configs['telegram'].credentials = {
            'bot_token': bot_token,
            'bot_username': bot_username
        }
        
        # Reinitialize sender
        self._initialize_senders()
        
        logger.info(f"✅ Telegram configured (enabled: {enabled})")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all platforms"""
        status = {
            'whatsapp': {
                'enabled': self.configs.get('whatsapp', {}).enabled if hasattr(self.configs.get('whatsapp', {}), 'enabled') else False,
                'configured': self.whatsapp_sender is not None,
                'groups_count': len(self.configs.get('whatsapp', {}).target_groups) if hasattr(self.configs.get('whatsapp', {}), 'target_groups') else 0
            },
            'telegram': {
                'enabled': self.configs.get('telegram', {}).enabled if hasattr(self.configs.get('telegram', {}), 'enabled') else False,
                'configured': self.telegram_sender is not None,
                'groups_count': len(self.configs.get('telegram', {}).target_groups) if hasattr(self.configs.get('telegram', {}), 'target_groups') else 0
            }
        }
        
        return status 