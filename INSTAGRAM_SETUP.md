# 📱 Instagram API Integration Setup Guide

This guide will help you set up real Instagram posting functionality for the Viral AI Video Generator.

## 🎯 Overview

The system now supports **3 approaches** for Instagram posting:

1. **instagrapi Library** (Recommended - Most Reliable)
2. **Instagram Basic Display API** (Official - Requires App Review)
3. **Simulation Mode** (Fallback - For Testing)

## 🚀 Quick Start: instagrapi (Recommended)

### Step 1: Install instagrapi
```bash
pip install instagrapi
```

### Step 2: Configure Credentials
Add your Instagram credentials to your `.env` file:

```env
# Instagram Credentials (for instagrapi)
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
INSTAGRAM_2FA_CODE=your_2fa_code_if_needed
```

### Step 3: Test the Integration
```bash
python -c "
from src.social.instagram_autoposter import InstagramAutoPoster, InstagramCredentials, PostContent
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Test credentials
credentials = InstagramCredentials(
    username='your_username',
    password='your_password'
)

autoposter = InstagramAutoPoster(credentials)
if autoposter.authenticate():
    print('✅ Instagram authentication successful!')
else:
    print('❌ Instagram authentication failed')
"
```

## 🔧 Advanced Setup: Instagram Basic Display API

### Step 1: Create Instagram App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Instagram Basic Display product
4. Configure OAuth redirect URIs

### Step 2: Get Access Token
1. Complete app review process (required for posting)
2. Generate access token with `instagram_basic` and `instagram_content_publish` permissions
3. Add to `.env`:

```env
# Instagram Basic Display API
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
```

### Step 3: Update InstagramAutoPoster
Add access token to the constructor:

```python
# In src/social/instagram_autoposter.py, update __init__ method
def __init__(self, credentials: InstagramCredentials, access_token: str = None):
    self.credentials = credentials
    self.instagram_access_token = access_token or os.getenv('INSTAGRAM_ACCESS_TOKEN')
    # ... rest of initialization
```

## 📋 Environment Configuration

### Complete .env Setup
```env
# =============================================================================
# INSTAGRAM INTEGRATION SETTINGS
# =============================================================================

# Method 1: instagrapi (Recommended)
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
INSTAGRAM_2FA_CODE=your_2fa_code_if_needed

# Method 2: Instagram Basic Display API
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret

# Posting Preferences
INSTAGRAM_POST_AS_REEL=true
INSTAGRAM_AUTO_HASHTAGS=true
INSTAGRAM_SCHEDULE_POSTS=false
INSTAGRAM_AUTO_DELETE_DAYS=0

# Error Handling
INSTAGRAM_MAX_RETRIES=3
INSTAGRAM_RETRY_DELAY=30
```

## 🧪 Testing Your Setup

### Test 1: Authentication
```bash
python -c "
from src.social.instagram_autoposter import InstagramAutoPoster, InstagramCredentials
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

credentials = InstagramCredentials(
    username='your_username',
    password='your_password'
)

autoposter = InstagramAutoPoster(credentials)
success = autoposter.authenticate()
print(f'Authentication: {\"✅ Success\" if success else \"❌ Failed\"}')
"
```

### Test 2: Video Upload
```bash
python -c "
from src.social.instagram_autoposter import InstagramAutoPoster, InstagramCredentials, PostContent
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Test with a sample video
credentials = InstagramCredentials(username='your_username', password='your_password')
autoposter = InstagramAutoPoster(credentials)

if autoposter.authenticate():
    content = PostContent(
        video_path='path/to/test/video.mp4',
        caption='Test video from Viral AI Generator',
        hashtags=['#test', '#viralai', '#automation'],
        is_reel=True
    )
    
    success = autoposter.post_video(content)
    print(f'Upload: {\"✅ Success\" if success else \"❌ Failed\"}')
else:
    print('❌ Authentication failed')
"
```

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit credentials to version control
- Use `.env` files for local development
- Use secure environment variables in production

### 2. Two-Factor Authentication
- Enable 2FA on your Instagram account
- Provide 2FA code when needed
- Consider using app-specific passwords

### 3. Rate Limiting
- Respect Instagram's rate limits
- Implement exponential backoff
- Monitor for account restrictions

## 🚨 Troubleshooting

### Common Issues

#### 1. Authentication Failed
```
❌ instagrapi login failed
```
**Solutions:**
- Check username/password
- Disable 2FA temporarily
- Use app-specific password
- Clear browser cookies

#### 2. Video Upload Failed
```
❌ Video format not supported
```
**Solutions:**
- Ensure video meets Instagram requirements
- Check file size (max 4GB for API)
- Verify video codec (H.264 recommended)

#### 3. API Rate Limits
```
❌ Rate limit exceeded
```
**Solutions:**
- Implement delays between posts
- Use multiple accounts
- Respect daily posting limits

### Debug Mode
Enable debug logging:
```python
import logging
logging.getLogger('src.social.instagram_autoposter').setLevel(logging.DEBUG)
```

## 📊 Monitoring & Analytics

### Post Analytics
```python
# Get post analytics
analytics = autoposter.get_post_analytics(post_id)
print(f"Views: {analytics.get('views', 0)}")
print(f"Likes: {analytics.get('likes', 0)}")
print(f"Comments: {analytics.get('comments', 0)}")
```

### Scheduled Posts
```python
# Schedule a post
from datetime import datetime, timedelta
options = PostingOptions(
    post_immediately=False,
    schedule_time=datetime.now() + timedelta(hours=2)
)
autoposter.post_video(content, options)
```

## 🎯 Integration with Video Generator

### Automatic Posting
The video generator will automatically attempt to post to Instagram when:
1. Platform is set to "instagram"
2. Credentials are configured
3. Video generation completes successfully

### Manual Posting
```bash
# Post a specific video
python -c "
from src.social.instagram_autoposter import create_instagram_post_from_session
from src.social.instagram_autoposter import InstagramCredentials

credentials = InstagramCredentials(username='your_username', password='your_password')
session_path = 'outputs/session_20250718_123456'

success = create_instagram_post_from_session(session_path, credentials)
print(f'Post: {\"✅ Success\" if success else \"❌ Failed\"}')
"
```

## 🔄 Migration from Simulation

### Current Status
- ✅ Video format validation
- ✅ Caption and hashtag preparation
- ✅ Session-based workflow
- ✅ Multiple API fallback options

### Next Steps
1. Choose your preferred method (instagrapi recommended)
2. Install required dependencies
3. Configure credentials
4. Test authentication
5. Test video upload
6. Monitor for any issues

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Enable debug logging
3. Verify Instagram account status
4. Check API rate limits
5. Review Instagram's terms of service

---

**Note**: Instagram's API policies change frequently. Always check the latest documentation and ensure compliance with Instagram's terms of service. 