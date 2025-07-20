#!/usr/bin/env python3
"""
Telegram Video Sender Module
Sends generated videos to Telegram groups using Telegram Bot API
"""

import os
import requests
import json
import time
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import logging

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class TelegramSender:
    """
    Telegram video sender for ViralAI generated content
    
    Supports:
    - Telegram Bot API integration
    - Group message sending
    - Video file upload and sharing
    - Message scheduling
    - Delivery status tracking
    - Channel posting
    """
    
    def __init__(self, bot_token: str, bot_username: str = None):
        """
        Initialize Telegram sender
        
        Args:
            bot_token: Telegram bot token from @BotFather
            bot_username: Bot username (optional, for logging)
        """
        self.bot_token = bot_token
        self.bot_username = bot_username
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        logger.info("📱 Telegram Sender initialized")
        logger.info(f"   Bot Token: {bot_token[:10]}...")
        if bot_username:
            logger.info(f"   Bot Username: @{bot_username}")
    
    def send_video_to_group(self, chat_id: Union[str, int], video_path: str,
                           caption: str = "", reply_to_message_id: int = None,
                           supports_streaming: bool = True) -> bool:
        """
        Send video to Telegram group/channel
        
        Args:
            chat_id: Telegram chat ID (group, channel, or user)
            video_path: Path to the video file
            caption: Optional caption for the video
            reply_to_message_id: Message ID to reply to (optional)
            supports_streaming: Whether video supports streaming
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"❌ File not found: {video_path}")
                return False
            
            # Check file size (Telegram limit: 50MB for videos)
            file_size = os.path.getsize(video_path)
            max_size = 50 * 1024 * 1024  # 50MB
            
            if file_size > max_size:
                logger.error(f"❌ File too large: {file_size / 1024 / 1024:.2f}MB > 50MB")
                return False
            
            # Prepare files and data
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'chat_id': chat_id,
                    'supports_streaming': supports_streaming
                }
                
                if caption:
                    data['caption'] = caption
                
                if reply_to_message_id:
                    data['reply_to_message_id'] = reply_to_message_id
                
                # Send video
                response = requests.post(
                    f"{self.base_url}/sendVideo",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        message_id = result['result']['message_id']
                        logger.info(f"✅ Video sent to chat {chat_id}: {message_id}")
                        return True
                    else:
                        logger.error(f"❌ Telegram API error: {result.get('description')}")
                        return False
                else:
                    logger.error(f"❌ Failed to send video: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error sending video to group: {e}")
            return False
    
    def send_text_to_group(self, chat_id: Union[str, int], message: str,
                          reply_to_message_id: int = None, parse_mode: str = "Markdown") -> bool:
        """
        Send text message to Telegram group/channel
        
        Args:
            chat_id: Telegram chat ID
            message: Text message to send
            reply_to_message_id: Message ID to reply to (optional)
            parse_mode: Message parsing mode (Markdown, HTML, or None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            
            if reply_to_message_id:
                payload['reply_to_message_id'] = reply_to_message_id
            
            if parse_mode:
                payload['parse_mode'] = parse_mode
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    message_id = result['result']['message_id']
                    logger.info(f"✅ Text sent to chat {chat_id}: {message_id}")
                    return True
                else:
                    logger.error(f"❌ Telegram API error: {result.get('description')}")
                    return False
            else:
                logger.error(f"❌ Failed to send text: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending text to group: {e}")
            return False
    
    def send_viral_video_package(self, chat_id: Union[str, int], video_path: str,
                                mission: str, platform: str, hashtags: List[str] = None) -> bool:
        """
        Send complete viral video package to Telegram group/channel
        
        Args:
            chat_id: Telegram chat ID
            video_path: Path to the generated video
            mission: Video mission/topic
            platform: Target platform (instagram, tiktok, etc.)
            hashtags: List of hashtags to include
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create engaging caption
            caption = self._create_viral_caption(mission, platform, hashtags)
            
            # Send video with caption
            success = self.send_video_to_group(chat_id, video_path, caption)
            
            if success:
                # Send follow-up message with engagement prompt
                engagement_msg = (
                    f"🎯 **Viral Video Generated!**\n\n"
                    f"📱 Platform: {platform.title()}\n"
                    f"🎬 Mission: {mission}\n\n"
                    f"💬 What do you think? Share your thoughts below! 👇\n"
                    f"🔄 Feel free to forward to other groups!\n"
                    f"🤖 Generated with ViralAI"
                )
                
                # Small delay between messages
                time.sleep(2)
                self.send_text_to_group(chat_id, engagement_msg)
                
                logger.info(f"✅ Complete viral video package sent to chat {chat_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending viral video package: {e}")
            return False
    
    def _create_viral_caption(self, mission: str, platform: str, hashtags: List[str] = None) -> str:
        """
        Create engaging caption for viral video
        
        Args:
            mission: Video mission/topic
            platform: Target platform
            hashtags: List of hashtags
            
        Returns:
            Formatted caption string
        """
        # Base caption
        caption = f"🎬 **AI-Generated Viral Video**\n\n"
        caption += f"📱 Optimized for: {platform.title()}\n"
        caption += f"🎯 Mission: {mission}\n\n"
        
        # Add hashtags if provided
        if hashtags:
            caption += "🏷️ Hashtags:\n"
            for hashtag in hashtags[:10]:  # Limit to 10 hashtags
                caption += f"#{hashtag} "
            caption += "\n\n"
        
        # Add engagement prompt
        caption += "🔥 Generated with ViralAI - AI-powered video creation!\n"
        caption += "💬 What's your take on this content?"
        
        return caption
    
    def send_photo_to_group(self, chat_id: Union[str, int], photo_path: str,
                           caption: str = "", reply_to_message_id: int = None) -> bool:
        """
        Send photo to Telegram group/channel
        
        Args:
            chat_id: Telegram chat ID
            photo_path: Path to the photo file
            caption: Optional caption for the photo
            reply_to_message_id: Message ID to reply to (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(photo_path):
                logger.error(f"❌ File not found: {photo_path}")
                return False
            
            with open(photo_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                data = {
                    'chat_id': chat_id
                }
                
                if caption:
                    data['caption'] = caption
                
                if reply_to_message_id:
                    data['reply_to_message_id'] = reply_to_message_id
                
                response = requests.post(
                    f"{self.base_url}/sendPhoto",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        message_id = result['result']['message_id']
                        logger.info(f"✅ Photo sent to chat {chat_id}: {message_id}")
                        return True
                    else:
                        logger.error(f"❌ Telegram API error: {result.get('description')}")
                        return False
                else:
                    logger.error(f"❌ Failed to send photo: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error sending photo to group: {e}")
            return False
    
    def send_document_to_group(self, chat_id: Union[str, int], document_path: str,
                              caption: str = "", reply_to_message_id: int = None) -> bool:
        """
        Send document to Telegram group/channel
        
        Args:
            chat_id: Telegram chat ID
            document_path: Path to the document file
            caption: Optional caption for the document
            reply_to_message_id: Message ID to reply to (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(document_path):
                logger.error(f"❌ File not found: {document_path}")
                return False
            
            # Check file size (Telegram limit: 2GB for documents)
            file_size = os.path.getsize(document_path)
            max_size = 2 * 1024 * 1024 * 1024  # 2GB
            
            if file_size > max_size:
                logger.error(f"❌ File too large: {file_size / 1024 / 1024 / 1024:.2f}GB > 2GB")
                return False
            
            with open(document_path, 'rb') as doc_file:
                files = {'document': doc_file}
                data = {
                    'chat_id': chat_id
                }
                
                if caption:
                    data['caption'] = caption
                
                if reply_to_message_id:
                    data['reply_to_message_id'] = reply_to_message_id
                
                response = requests.post(
                    f"{self.base_url}/sendDocument",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        message_id = result['result']['message_id']
                        logger.info(f"✅ Document sent to chat {chat_id}: {message_id}")
                        return True
                    else:
                        logger.error(f"❌ Telegram API error: {result.get('description')}")
                        return False
                else:
                    logger.error(f"❌ Failed to send document: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error sending document to group: {e}")
            return False
    
    def get_chat_info(self, chat_id: Union[str, int]) -> Dict[str, Any]:
        """
        Get information about a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Chat information dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/getChat",
                params={'chat_id': chat_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return result['result']
                else:
                    logger.error(f"❌ Telegram API error: {result.get('description')}")
                    return {}
            else:
                logger.error(f"❌ Failed to get chat info: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting chat info: {e}")
            return {}
    
    def get_chat_members_count(self, chat_id: Union[str, int]) -> int:
        """
        Get number of members in a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Number of members, 0 if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/getChatMemberCount",
                params={'chat_id': chat_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    count = result['result']
                    logger.info(f"📊 Chat {chat_id} has {count} members")
                    return count
                else:
                    logger.error(f"❌ Telegram API error: {result.get('description')}")
                    return 0
            else:
                logger.error(f"❌ Failed to get member count: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Error getting member count: {e}")
            return 0
    
    def pin_message(self, chat_id: Union[str, int], message_id: int, 
                   disable_notification: bool = False) -> bool:
        """
        Pin a message in a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            message_id: Message ID to pin
            disable_notification: Whether to disable notification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                'chat_id': chat_id,
                'message_id': message_id,
                'disable_notification': disable_notification
            }
            
            response = requests.post(
                f"{self.base_url}/pinChatMessage",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"✅ Message {message_id} pinned in chat {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Telegram API error: {result.get('description')}")
                    return False
            else:
                logger.error(f"❌ Failed to pin message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error pinning message: {e}")
            return False
    
    def delete_message(self, chat_id: Union[str, int], message_id: int) -> bool:
        """
        Delete a message in a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            message_id: Message ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                'chat_id': chat_id,
                'message_id': message_id
            }
            
            response = requests.post(
                f"{self.base_url}/deleteMessage",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"✅ Message {message_id} deleted from chat {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Telegram API error: {result.get('description')}")
                    return False
            else:
                logger.error(f"❌ Failed to delete message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting message: {e}")
            return False
    
    def validate_credentials(self) -> bool:
        """
        Validate Telegram bot credentials
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/getMe")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    bot_info = result['result']
                    logger.info(f"✅ Telegram bot validated: @{bot_info.get('username')}")
                    return True
                else:
                    logger.error(f"❌ Invalid Telegram bot token: {result.get('description')}")
                    return False
            else:
                logger.error(f"❌ Failed to validate bot: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error validating bot credentials: {e}")
            return False
    
    def get_updates(self, offset: int = None, limit: int = 100, timeout: int = 0) -> List[Dict[str, Any]]:
        """
        Get updates from Telegram (for webhook handling)
        
        Args:
            offset: Identifier of the first update to be returned
            limit: Limits the number of updates to be retrieved
            timeout: Timeout in seconds for long polling
            
        Returns:
            List of updates
        """
        try:
            params = {
                'limit': limit,
                'timeout': timeout
            }
            
            if offset:
                params['offset'] = offset
            
            response = requests.get(
                f"{self.base_url}/getUpdates",
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return result['result']
                else:
                    logger.error(f"❌ Telegram API error: {result.get('description')}")
                    return []
            else:
                logger.error(f"❌ Failed to get updates: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting updates: {e}")
            return [] 