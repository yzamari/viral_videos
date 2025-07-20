#!/usr/bin/env python3
"""
WhatsApp Video Sender Module
Sends generated videos to WhatsApp groups using WhatsApp Business API
"""

import os
import requests
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class WhatsAppSender:
    """
    WhatsApp video sender for ViralAI generated content
    
    Supports:
    - WhatsApp Business API integration
    - Group message sending
    - Video file upload and sharing
    - Message scheduling
    - Delivery status tracking
    """
    
    def __init__(self, access_token: str, phone_number_id: str, verify_token: str = None):
        """
        Initialize WhatsApp sender
        
        Args:
            access_token: WhatsApp Business API access token
            phone_number_id: WhatsApp Business phone number ID
            verify_token: Webhook verification token (optional)
        """
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.api_url = f"{self.base_url}/{phone_number_id}"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info("📱 WhatsApp Sender initialized")
        logger.info(f"   Phone Number ID: {phone_number_id}")
        logger.info(f"   API URL: {self.api_url}")
    
    def upload_media(self, file_path: str, media_type: str = "video") -> Optional[str]:
        """
        Upload media file to WhatsApp servers
        
        Args:
            file_path: Path to the video file
            media_type: Type of media (video, image, audio, document)
            
        Returns:
            Media ID if successful, None otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ File not found: {file_path}")
                return None
            
            # Check file size (WhatsApp limit: 16MB for videos)
            file_size = os.path.getsize(file_path)
            max_size = 16 * 1024 * 1024  # 16MB
            
            if file_size > max_size:
                logger.error(f"❌ File too large: {file_size / 1024 / 1024:.2f}MB > 16MB")
                return None
            
            # Upload media
            upload_url = f"{self.api_url}/media"
            
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    'messaging_product': 'whatsapp',
                    'type': media_type
                }
                
                response = requests.post(
                    upload_url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    media_id = response.json().get('id')
                    logger.info(f"✅ Media uploaded successfully: {media_id}")
                    return media_id
                else:
                    logger.error(f"❌ Media upload failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Media upload error: {e}")
            return None
    
    def send_video_to_group(self, group_id: str, video_path: str, 
                           caption: str = "", reply_to: str = None) -> bool:
        """
        Send video to WhatsApp group
        
        Args:
            group_id: WhatsApp group ID
            video_path: Path to the video file
            caption: Optional caption for the video
            reply_to: Message ID to reply to (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Upload video first
            media_id = self.upload_media(video_path, "video")
            if not media_id:
                return False
            
            # Prepare message payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "group",
                "to": group_id,
                "type": "video",
                "video": {
                    "id": media_id
                }
            }
            
            # Add caption if provided
            if caption:
                payload["video"]["caption"] = caption
            
            # Add reply if specified
            if reply_to:
                payload["context"] = {
                    "message_id": reply_to
                }
            
            # Send message
            response = requests.post(
                f"{self.api_url}/messages",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                message_id = response.json().get('messages', [{}])[0].get('id')
                logger.info(f"✅ Video sent to group {group_id}: {message_id}")
                return True
            else:
                logger.error(f"❌ Failed to send video: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending video to group: {e}")
            return False
    
    def send_text_to_group(self, group_id: str, message: str, 
                          reply_to: str = None) -> bool:
        """
        Send text message to WhatsApp group
        
        Args:
            group_id: WhatsApp group ID
            message: Text message to send
            reply_to: Message ID to reply to (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "group",
                "to": group_id,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            # Add reply if specified
            if reply_to:
                payload["context"] = {
                    "message_id": reply_to
                }
            
            response = requests.post(
                f"{self.api_url}/messages",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                message_id = response.json().get('messages', [{}])[0].get('id')
                logger.info(f"✅ Text sent to group {group_id}: {message_id}")
                return True
            else:
                logger.error(f"❌ Failed to send text: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending text to group: {e}")
            return False
    
    def send_viral_video_package(self, group_id: str, video_path: str, 
                                mission: str, platform: str, hashtags: List[str] = None) -> bool:
        """
        Send complete viral video package to WhatsApp group
        
        Args:
            group_id: WhatsApp group ID
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
            success = self.send_video_to_group(group_id, video_path, caption)
            
            if success:
                # Send follow-up message with engagement prompt
                engagement_msg = (
                    f"🎯 **Viral Video Generated!**\n\n"
                    f"📱 Platform: {platform.title()}\n"
                    f"🎬 Mission: {mission}\n\n"
                    f"💬 What do you think? Share your thoughts below! 👇\n"
                    f"🔄 Feel free to forward to other groups!"
                )
                
                # Small delay between messages
                time.sleep(2)
                self.send_text_to_group(group_id, engagement_msg)
                
                logger.info(f"✅ Complete viral video package sent to group {group_id}")
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
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get delivery status of a message
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            Status information dictionary
        """
        try:
            response = requests.get(
                f"{self.api_url}/messages/{message_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get message status: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting message status: {e}")
            return {}
    
    def schedule_message(self, group_id: str, video_path: str, 
                        schedule_time: datetime, caption: str = "") -> bool:
        """
        Schedule a video message for later delivery
        
        Args:
            group_id: WhatsApp group ID
            video_path: Path to the video file
            schedule_time: When to send the message
            caption: Optional caption
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        try:
            # Upload video first
            media_id = self.upload_media(video_path, "video")
            if not media_id:
                return False
            
            # Calculate delay in seconds
            delay = int((schedule_time - datetime.now()).total_seconds())
            if delay <= 0:
                logger.error("❌ Schedule time must be in the future")
                return False
            
            # Schedule message
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "group",
                "to": group_id,
                "type": "video",
                "video": {
                    "id": media_id
                },
                "scheduled_time": schedule_time.isoformat()
            }
            
            if caption:
                payload["video"]["caption"] = caption
            
            response = requests.post(
                f"{self.api_url}/messages",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Message scheduled for {schedule_time}")
                return True
            else:
                logger.error(f"❌ Failed to schedule message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error scheduling message: {e}")
            return False
    
    def get_group_info(self, group_id: str) -> Dict[str, Any]:
        """
        Get information about a WhatsApp group
        
        Args:
            group_id: WhatsApp group ID
            
        Returns:
            Group information dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/{group_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get group info: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting group info: {e}")
            return {}
    
    def validate_credentials(self) -> bool:
        """
        Validate WhatsApp Business API credentials
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info("✅ WhatsApp credentials validated successfully")
                return True
            else:
                logger.error(f"❌ Invalid WhatsApp credentials: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error validating credentials: {e}")
            return False 