# Social Media Integration Guide

## Overview

ViralAI now supports comprehensive social media integration, including WhatsApp and Telegram group messaging. This guide explains how to set up and use these features to automatically distribute your AI-generated videos.

## Supported Platforms

### 1. WhatsApp Business API
- Send videos to WhatsApp groups
- Support for captions and hashtags
- Message scheduling capabilities
- Delivery status tracking

### 2. Telegram Bot API
- Send videos to Telegram groups and channels
- Support for photos, documents, and text messages
- Message pinning and deletion
- Member count tracking

### 3. Instagram (Existing)
- Auto-posting to Instagram feed and stories
- Hashtag optimization
- Engagement tracking

## Setup Instructions

### WhatsApp Business API Setup

#### Prerequisites
1. **Facebook Developer Account**: Create an account at [developers.facebook.com](https://developers.facebook.com)
2. **WhatsApp Business Account**: Set up a WhatsApp Business account
3. **Phone Number**: A dedicated phone number for your business

#### Step-by-Step Setup

1. **Create Facebook App**
   ```bash
   # Go to Facebook Developers Console
   # Create a new app with "Business" type
   # Add WhatsApp product to your app
   ```

2. **Configure WhatsApp Business API**
   ```bash
   # In your app dashboard:
   # 1. Go to WhatsApp > Getting Started
   # 2. Add your phone number
   # 3. Verify your phone number
   # 4. Get your access token and phone number ID
   ```

3. **Configure ViralAI**
   ```python
   from src.social.social_media_manager import SocialMediaManager
   
   # Initialize manager
   manager = SocialMediaManager()
   
   # Configure WhatsApp
   manager.configure_whatsapp(
       access_token="YOUR_ACCESS_TOKEN",
       phone_number_id="YOUR_PHONE_NUMBER_ID",
       enabled=True
   )
   
   # Add target groups
   manager.add_whatsapp_group("GROUP_ID_1")
   manager.add_whatsapp_group("GROUP_ID_2")
   ```

#### Getting Group IDs
1. **Using WhatsApp Web**: 
   - Open group in WhatsApp Web
   - Check browser console for group ID
   
2. **Using API**:
   ```python
   # Get group info
   group_info = whatsapp_sender.get_group_info("GROUP_ID")
   print(f"Group: {group_info.get('name')}")
   ```

### Telegram Bot Setup

#### Prerequisites
1. **Telegram Account**: Create a Telegram account
2. **BotFather**: Contact @BotFather on Telegram

#### Step-by-Step Setup

1. **Create Telegram Bot**
   ```bash
   # 1. Open Telegram and search for @BotFather
   # 2. Send /newbot command
   # 3. Follow instructions to create your bot
   # 4. Save the bot token provided
   ```

2. **Add Bot to Groups**
   ```bash
   # 1. Add your bot to target groups
   # 2. Make bot admin if needed
   # 3. Get group chat IDs
   ```

3. **Configure ViralAI**
   ```python
   from src.social.social_media_manager import SocialMediaManager
   
   # Initialize manager
   manager = SocialMediaManager()
   
   # Configure Telegram
   manager.configure_telegram(
       bot_token="YOUR_BOT_TOKEN",
       bot_username="your_bot_username",
       enabled=True
   )
   
   # Add target groups
   manager.add_telegram_group("CHAT_ID_1")
   manager.add_telegram_group("CHAT_ID_2")
   ```

#### Getting Chat IDs
1. **Using Bot API**:
   ```python
   # Send a message to your bot and check updates
   updates = telegram_sender.get_updates()
   for update in updates:
       if 'message' in update:
           chat_id = update['message']['chat']['id']
           chat_type = update['message']['chat']['type']
           print(f"Chat ID: {chat_id}, Type: {chat_type}")
   ```

2. **Using @userinfobot**:
   - Add @userinfobot to your group
   - Send any message
   - Bot will reply with chat information

## Usage Examples

### Basic Video Sending

```python
from src.social.social_media_manager import SocialMediaManager

# Initialize manager
manager = SocialMediaManager("config/social_media.json")

# Send video to all platforms
results = manager.send_video_to_all_platforms(
    video_path="outputs/viral_video.mp4",
    mission="Teach about climate change",
    platform="instagram",
    hashtags=["climate", "education", "viral"]
)

print(f"Results: {results}")
# Output: {'whatsapp': True, 'telegram': True}
```

### Platform-Specific Sending

```python
# Send only to WhatsApp
if manager.whatsapp_sender:
    success = manager.whatsapp_sender.send_viral_video_package(
        group_id="GROUP_ID",
        video_path="video.mp4",
        mission="Mission description",
        platform="instagram",
        hashtags=["hashtag1", "hashtag2"]
    )

# Send only to Telegram
if manager.telegram_sender:
    success = manager.telegram_sender.send_viral_video_package(
        chat_id="CHAT_ID",
        video_path="video.mp4",
        mission="Mission description",
        platform="instagram",
        hashtags=["hashtag1", "hashtag2"]
    )
```

### Advanced Features

#### Message Scheduling
```python
from datetime import datetime, timedelta

# Schedule WhatsApp message
schedule_time = datetime.now() + timedelta(hours=2)
manager.whatsapp_sender.schedule_message(
    group_id="GROUP_ID",
    video_path="video.mp4",
    schedule_time=schedule_time,
    caption="Scheduled viral video!"
)
```

#### Message Management
```python
# Pin message in Telegram
manager.telegram_sender.pin_message(
    chat_id="CHAT_ID",
    message_id=12345,
    disable_notification=True
)

# Delete message
manager.telegram_sender.delete_message(
    chat_id="CHAT_ID",
    message_id=12345
)
```

#### Analytics
```python
# Get sending analytics
analytics = manager.get_sending_analytics()
print(f"Total sent: {analytics['total_sent']}")
print(f"Success rate: {analytics['success_rate']:.1%}")
print(f"Platform breakdown: {analytics['platform_breakdown']}")
```

## Configuration File

Create a configuration file `config/social_media.json`:

```json
{
  "whatsapp": {
    "platform": "whatsapp",
    "enabled": true,
    "credentials": {
      "access_token": "YOUR_ACCESS_TOKEN",
      "phone_number_id": "YOUR_PHONE_NUMBER_ID",
      "verify_token": "YOUR_VERIFY_TOKEN"
    },
    "target_groups": [
      "GROUP_ID_1",
      "GROUP_ID_2"
    ],
    "auto_send": true,
    "include_caption": true,
    "include_hashtags": true
  },
  "telegram": {
    "platform": "telegram",
    "enabled": true,
    "credentials": {
      "bot_token": "YOUR_BOT_TOKEN",
      "bot_username": "your_bot_username"
    },
    "target_groups": [
      "CHAT_ID_1",
      "CHAT_ID_2"
    ],
    "auto_send": true,
    "include_caption": true,
    "include_hashtags": true
  }
}
```

## Integration with Video Generation

### Automatic Posting
```python
# In your video generation workflow
from src.social.social_media_manager import SocialMediaManager

def generate_and_post_video(mission, platform, duration):
    # Generate video
    video_path = generate_video(mission, platform, duration)
    
    # Initialize social media manager
    manager = SocialMediaManager()
    
    # Auto-post to all platforms
    results = manager.send_video_to_all_platforms(
        video_path=video_path,
        mission=mission,
        platform=platform,
        hashtags=generate_hashtags(mission, platform)
    )
    
    return results
```

### CLI Integration
```bash
# Generate video and auto-post
python main.py generate \
  --mission "Teach about recycling" \
  --platform instagram \
  --duration 30 \
  --auto-post

# Generate video and post to specific platforms
python main.py generate \
  --mission "Climate change awareness" \
  --platform tiktok \
  --duration 45 \
  --post-to whatsapp,telegram
```

## Best Practices

### 1. Content Optimization
- **WhatsApp**: Keep videos under 16MB, use engaging captions
- **Telegram**: Support up to 50MB, use Markdown formatting
- **Timing**: Post during peak engagement hours

### 2. Group Management
- **WhatsApp**: Use business groups, respect group rules
- **Telegram**: Use public channels for broader reach
- **Frequency**: Don't spam groups, maintain quality

### 3. Error Handling
```python
# Always check for errors
try:
    results = manager.send_video_to_all_platforms(...)
    if not any(results.values()):
        logger.error("Failed to send to any platform")
except Exception as e:
    logger.error(f"Social media error: {e}")
```

### 4. Rate Limiting
- **WhatsApp**: 1000 messages per day (business)
- **Telegram**: 30 messages per second
- **Implementation**: Built-in delays between sends

## Troubleshooting

### Common Issues

#### WhatsApp Issues
1. **Invalid Access Token**
   ```python
   # Validate credentials
   if not manager.whatsapp_sender.validate_credentials():
       print("Invalid WhatsApp credentials")
   ```

2. **File Too Large**
   ```python
   # Check file size before sending
   file_size = os.path.getsize(video_path)
   if file_size > 16 * 1024 * 1024:  # 16MB
       print("File too large for WhatsApp")
   ```

#### Telegram Issues
1. **Bot Not in Group**
   ```python
   # Check bot permissions
   chat_info = manager.telegram_sender.get_chat_info(chat_id)
   print(f"Bot can send messages: {chat_info.get('can_send_messages')}")
   ```

2. **Invalid Chat ID**
   ```python
   # Validate chat ID
   try:
       chat_info = manager.telegram_sender.get_chat_info(chat_id)
       print(f"Valid chat: {chat_info.get('title')}")
   except:
       print("Invalid chat ID")
   ```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check platform status
status = manager.get_status()
print(f"Platform status: {status}")
```

## Security Considerations

### 1. Credential Management
- Store tokens securely (environment variables)
- Rotate tokens regularly
- Use least privilege access

### 2. Group Privacy
- Respect group privacy settings
- Don't share private group IDs
- Follow platform terms of service

### 3. Content Guidelines
- Ensure content complies with platform policies
- Avoid spam and excessive posting
- Monitor engagement and feedback

## Future Enhancements

### Planned Features
1. **Analytics Dashboard**: Visual analytics for posting performance
2. **A/B Testing**: Test different captions and posting times
3. **Multi-language Support**: Localized content for different regions
4. **Advanced Scheduling**: AI-powered optimal posting times
5. **Engagement Tracking**: Monitor likes, shares, and comments

### API Extensions
1. **Webhook Support**: Real-time delivery notifications
2. **Bulk Operations**: Send to multiple groups efficiently
3. **Content Templates**: Pre-defined message templates
4. **Automated Responses**: Handle user interactions

## Support and Resources

### Documentation
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [ViralAI Social Media Integration](docs/SOCIAL_MEDIA_INTEGRATION.md)

### Community
- GitHub Issues: Report bugs and request features
- Discord Community: Get help and share experiences
- Documentation Wiki: User-contributed guides

### Updates
- Follow ViralAI releases for new social media features
- Subscribe to platform API updates
- Monitor platform policy changes 