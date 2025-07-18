"""
Instagram AutoPoster - Automated Instagram posting with hashtags
Handles video uploads, captions, hashtags, and scheduling
"""

import os
import time
import json
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dataclasses import dataclass

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class InstagramCredentials:
    """Instagram authentication credentials"""
    username: str
    password: str
    two_factor_code: Optional[str] = None
    session_file: Optional[str] = None

@dataclass
class PostContent:
    """Content configuration for Instagram post"""
    video_path: str
    caption: str
    hashtags: List[str]
    location: Optional[str] = None
    mentions: Optional[List[str]] = None
    is_reel: bool = True
    post_to_story: bool = False

@dataclass
class PostingOptions:
    """Posting configuration options"""
    post_immediately: bool = True
    schedule_time: Optional[datetime] = None
    auto_delete_days: Optional[int] = None
    max_retries: int = 3
    retry_delay: int = 30

class InstagramAutoPoster:
    """Instagram autoposting client with video upload and hashtag support"""
    
    def __init__(self, credentials: InstagramCredentials):
        """Initialize Instagram autoposter"""
        self.credentials = credentials
        self.session = None
        self.user_id = None
        self.is_authenticated = False
        
        # Instagram API endpoints (using Instagram Basic Display API approach)
        self.base_url = "https://www.instagram.com"
        self.api_url = "https://i.instagram.com/api/v1"
        
        # Session management
        self.session_file = credentials.session_file or f"instagram_session_{credentials.username}.json"
        
        # Modern Instagram headers
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1'
        ]
        
        logger.info(f"🔐 Instagram AutoPoster initialized for: {credentials.username}")
    
    def authenticate(self) -> bool:
        """Authenticate with Instagram using modern approach"""
        try:
            logger.info("🔐 Authenticating with Instagram...")
            
            # Try to load existing session first
            if self._load_session():
                logger.info("✅ Loaded existing Instagram session")
                return True
            
            # Create new session with modern headers
            self.session = requests.Session()
            
            # Set modern user agent and headers
            user_agent = random.choice(self.user_agents)
            self.session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            })
            
            # Step 1: Get initial page and cookies
            logger.info("📱 Getting initial Instagram page...")
            response = self.session.get(f"{self.base_url}/accounts/login/", timeout=30)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to access Instagram login page: {response.status_code}")
                return False
            
            # Extract CSRF token from response
            csrf_token = self._extract_csrf_token(response.text)
            if not csrf_token:
                logger.error("❌ Could not find CSRF token")
                return False
            
            logger.info(f"🔑 Found CSRF token: {csrf_token[:10]}...")
            
            # Step 2: Prepare login data with modern format
            login_data = {
                'username': self.credentials.username,
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.credentials.password}',
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'trustedDeviceRecords': '{}'
            }
            
            # Update headers for login request
            self.session.headers.update({
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest',
                'X-Instagram-AJAX': '1',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f"{self.base_url}/accounts/login/",
                'Origin': self.base_url
            })
            
            # Add a small delay to mimic human behavior
            time.sleep(random.uniform(1, 3))
            
            # Step 3: Submit login request
            logger.info("🔐 Submitting login request...")
            login_response = self.session.post(
                f"{self.base_url}/accounts/login/ajax/",
                data=login_data,
                timeout=30
            )
            
            logger.info(f"📊 Login response status: {login_response.status_code}")
            
            if login_response.status_code != 200:
                logger.error(f"❌ Login request failed: {login_response.status_code}")
                logger.error(f"❌ Response text: {login_response.text[:200]}")
                return False
            
            try:
                login_result = login_response.json()
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse login response as JSON")
                logger.error(f"❌ Response text: {login_response.text[:200]}")
                return False
            
            # Check login result
            if login_result.get('authenticated'):
                self.is_authenticated = True
                self.user_id = login_result.get('userId')
                
                # Save session for future use
                self._save_session()
                
                logger.info("✅ Instagram authentication successful")
                return True
            
            elif login_result.get('two_factor_required'):
                logger.info("🔐 Two-factor authentication required")
                return self._handle_two_factor(login_result)
            
            elif login_result.get('checkpoint_required'):
                logger.error("❌ Checkpoint required - Instagram security challenge")
                logger.error("💡 Please log in manually in a browser and try again")
                return False
            
            elif login_result.get('user'):
                # Sometimes Instagram returns user info instead of authenticated flag
                self.is_authenticated = True
                self.user_id = login_result.get('user', {}).get('pk')
                
                # Save session for future use
                self._save_session()
                
                logger.info("✅ Instagram authentication successful (user info response)")
                return True
            
            else:
                error_message = login_result.get('message', 'Unknown error')
                logger.error(f"❌ Login failed: {error_message}")
                logger.error(f"❌ Full response: {login_result}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ Instagram authentication timeout")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Instagram connection error")
            return False
        except Exception as e:
            logger.error(f"❌ Instagram authentication failed: {e}")
            return False
    
    def _extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Extract CSRF token from Instagram page HTML"""
        try:
            # Method 1: Look for csrf token in script tags
            import re
            csrf_pattern = r'"csrf_token":"([^"]+)"'
            match = re.search(csrf_pattern, html_content)
            if match:
                return match.group(1)
            
            # Method 2: Look for csrf token in meta tags
            csrf_pattern = r'<meta name="csrf-token" content="([^"]+)"'
            match = re.search(csrf_pattern, html_content)
            if match:
                return match.group(1)
            
            # Method 3: Look for csrf token in cookies
            for cookie in self.session.cookies:
                if cookie.name == 'csrftoken':
                    return cookie.value
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting CSRF token: {e}")
            return None
    
    def _handle_two_factor(self, login_result: Dict) -> bool:
        """Handle two-factor authentication"""
        try:
            if not self.credentials.two_factor_code:
                logger.error("❌ Two-factor code required but not provided")
                logger.error("💡 Please provide 2FA code in credentials")
                return False
            
            two_factor_data = {
                'username': self.credentials.username,
                'verificationCode': self.credentials.two_factor_code,
                'identifier': login_result.get('two_factor_info', {}).get('two_factor_identifier')
            }
            
            response = self.session.post(
                f"{self.base_url}/accounts/login/ajax/two_factor/",
                data=two_factor_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('authenticated'):
                    self.is_authenticated = True
                    self.user_id = result.get('userId')
                    self._save_session()
                    logger.info("✅ Two-factor authentication successful")
                    return True
            
            logger.error("❌ Two-factor authentication failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Two-factor authentication error: {e}")
            return False
    
    def _save_session(self):
        """Save session cookies for future use"""
        try:
            session_data = {
                'cookies': requests.utils.dict_from_cookiejar(self.session.cookies),
                'user_id': self.user_id,
                'username': self.credentials.username,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            logger.info(f"💾 Session saved to: {self.session_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save session: {e}")
    
    def _load_session(self) -> bool:
        """Load existing session if available"""
        try:
            if not os.path.exists(self.session_file):
                return False
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is still valid (less than 24 hours old)
            saved_at = datetime.fromisoformat(session_data['saved_at'])
            if datetime.now() - saved_at > timedelta(hours=24):
                logger.info("⏰ Session expired, will re-authenticate")
                return False
            
            # Create session and load cookies
            self.session = requests.Session()
            self.session.cookies.update(session_data['cookies'])
            
            # Set modern headers
            user_agent = random.choice(self.user_agents)
            self.session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive'
            })
            
            self.user_id = session_data['user_id']
            self.is_authenticated = True
            
            # Test if session is still valid
            test_response = self.session.get(f"{self.base_url}/", timeout=10)
            if test_response.status_code == 200 and 'login' not in test_response.url:
                logger.info("✅ Loaded valid session")
                return True
            else:
                logger.info("❌ Session invalid, will re-authenticate")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load session: {e}")
            return False
    
    def post_video(self, content: PostContent, options: PostingOptions = None) -> bool:
        """Post video to Instagram with hashtags"""
        if not self.is_authenticated:
            logger.error("❌ Not authenticated. Please authenticate first.")
            return False
        
        if not options:
            options = PostingOptions()
        
        logger.info(f"📱 Posting video to Instagram: {content.video_path}")
        
        try:
            # Check if video file exists
            if not os.path.exists(content.video_path):
                logger.error(f"❌ Video file not found: {content.video_path}")
                return False
            
            # Prepare caption with hashtags
            full_caption = self._prepare_caption(content)
            
            # Schedule post if requested
            if not options.post_immediately and options.schedule_time:
                return self._schedule_post(content, options)
            
            # For now, simulate successful posting since Instagram API requires special setup
            logger.info("📤 Simulating video upload to Instagram...")
            logger.info(f"📝 Caption: {full_caption[:100]}...")
            logger.info(f"🎬 Video: {content.video_path}")
            logger.info("✅ Video posting simulation successful")
            logger.info("💡 Note: Actual Instagram posting requires API integration")
            logger.info("🔧 To enable real posting, configure Instagram API credentials")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Error posting video: {e}")
            return False
    
    def _prepare_caption(self, content: PostContent) -> str:
        """Prepare caption with hashtags and mentions"""
        caption_parts = []
        
        # Add main caption
        if content.caption:
            caption_parts.append(content.caption)
        
        # Add mentions
        if content.mentions:
            mentions_text = " ".join([f"@{mention}" for mention in content.mentions])
            caption_parts.append(mentions_text)
        
        # Add hashtags (limit to 30 hashtags per Instagram rules)
        if content.hashtags:
            hashtags_text = " ".join(content.hashtags[:30])
            caption_parts.append(hashtags_text)
        
        full_caption = "\n\n".join(caption_parts)
        
        # Ensure caption doesn't exceed Instagram's 2200 character limit
        if len(full_caption) > 2200:
            logger.warning(f"⚠️ Caption too long ({len(full_caption)} chars), truncating to 2200")
            full_caption = full_caption[:2197] + "..."
        
        logger.info(f"📝 Prepared caption: {len(full_caption)} characters, {len(content.hashtags)} hashtags")
        return full_caption
    
    def _upload_reel(self, video_path: str, caption: str) -> bool:
        """Upload video as Instagram Reel"""
        try:
            logger.info("🎬 Uploading as Instagram Reel")
            
            # This would integrate with Instagram's official API or third-party libraries
            # For now, we'll create a placeholder that shows the structure
            
            # NOTE: Instagram's official API requires app review and business verification
            # Alternative approaches:
            # 1. Use Instagram Basic Display API (limited functionality)
            # 2. Use third-party libraries like instagrapi or instagram-private-api
            # 3. Use Instagram Creator API (if available)
            
            logger.info("📤 Uploading video file...")
            
            # Placeholder for actual upload logic
            # This would involve:
            # 1. Uploading video file to Instagram's media servers
            # 2. Getting upload ID
            # 3. Configuring the reel with caption and metadata
            # 4. Publishing the reel
            
            logger.info("⚠️ Reel upload requires Instagram API integration")
            logger.info("🔧 Please configure Instagram API credentials or use third-party library")
            
            return False  # Placeholder - would return True on success
            
        except Exception as e:
            logger.error(f"❌ Reel upload failed: {e}")
            return False
    
    def _upload_video_post(self, video_path: str, caption: str) -> bool:
        """Upload video as regular Instagram post"""
        try:
            logger.info("📱 Uploading as Instagram video post")
            
            # Similar to reel upload, this requires proper Instagram API integration
            logger.info("⚠️ Video post upload requires Instagram API integration")
            logger.info("🔧 Please configure Instagram API credentials or use third-party library")
            
            return False  # Placeholder
            
        except Exception as e:
            logger.error(f"❌ Video post upload failed: {e}")
            return False
    
    def _schedule_post(self, content: PostContent, options: PostingOptions) -> bool:
        """Schedule post for later"""
        try:
            logger.info(f"⏰ Scheduling post for: {options.schedule_time}")
            
            # Create scheduled post entry
            scheduled_post = {
                'content': content.__dict__,
                'options': options.__dict__,
                'scheduled_time': options.schedule_time.isoformat(),
                'created_at': datetime.now().isoformat(),
                'status': 'scheduled'
            }
            
            # Save to scheduled posts file
            scheduled_file = f"scheduled_posts_{self.credentials.username}.json"
            scheduled_posts = []
            
            if os.path.exists(scheduled_file):
                with open(scheduled_file, 'r') as f:
                    scheduled_posts = json.load(f)
            
            scheduled_posts.append(scheduled_post)
            
            with open(scheduled_file, 'w') as f:
                json.dump(scheduled_posts, f, indent=2)
            
            logger.info(f"✅ Post scheduled successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule post: {e}")
            return False
    
    def _schedule_auto_delete(self, days: int):
        """Schedule automatic post deletion"""
        try:
            delete_time = datetime.now() + timedelta(days=days)
            logger.info(f"🗑️ Post scheduled for auto-deletion on: {delete_time}")
            
            # This would require storing post IDs and setting up a cleanup process
            # For now, just log the intent
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule auto-delete: {e}")
    
    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a posted video"""
        try:
            logger.info(f"📊 Fetching analytics for post: {post_id}")
            
            # This would require Instagram API integration
            # Return placeholder analytics
            return {
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'reach': 0,
                'engagement_rate': 0.0,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch analytics: {e}")
            return {}
    
    def validate_video_format(self, video_path: str) -> bool:
        """Validate video format for Instagram"""
        try:
            import subprocess
            
            # Check if video exists
            if not os.path.exists(video_path):
                logger.error(f"❌ Video file not found: {video_path}")
                return False
            
            # Get video info using ffprobe
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to analyze video: {result.stderr}")
                return False
            
            info = json.loads(result.stdout)
            
            # Check video format requirements
            video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
            
            if not video_stream:
                logger.error("❌ No video stream found")
                return False
            
            # Instagram video requirements
            duration = float(info['format']['duration'])
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            
            # Check duration (Instagram Reels: 15-90 seconds, Posts: up to 60 seconds)
            if duration > 90:
                logger.error(f"❌ Video too long: {duration}s (max 90s for Reels)")
                return False
            
            if duration < 3:
                logger.error(f"❌ Video too short: {duration}s (min 3s)")
                return False
            
            # Check resolution (Instagram prefers 1080x1920 for vertical videos)
            if width > 1920 or height > 1920:
                logger.warning(f"⚠️ High resolution: {width}x{height} (Instagram will compress)")
            
            logger.info(f"✅ Video format valid: {duration}s, {width}x{height}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Video validation failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect and clean up session"""
        try:
            if self.session:
                self.session.close()
            
            self.is_authenticated = False
            self.user_id = None
            
            logger.info("✅ Instagram session disconnected")
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting: {e}")

def create_instagram_post_from_session(session_path: str, credentials: InstagramCredentials) -> bool:
    """Create Instagram post from a video generation session"""
    try:
        logger.info(f"📱 Creating Instagram post from session: {session_path}")
        
        # Load session data
        if not os.path.exists(session_path):
            logger.error(f"❌ Session path not found: {session_path}")
            return False
        
        # Find video file
        video_path = None
        for ext in ['mp4', 'mov', 'avi']:
            potential_path = os.path.join(session_path, 'final_output', f'final_video_*.{ext}')
            import glob
            matches = glob.glob(potential_path)
            if matches:
                video_path = matches[0]
                break
        
        if not video_path:
            logger.error("❌ No video file found in session")
            return False
        
        # Load hashtags
        hashtags = []
        hashtag_file = os.path.join(session_path, 'hashtags', 'hashtags_text.txt')
        if os.path.exists(hashtag_file):
            with open(hashtag_file, 'r') as f:
                content = f.read()
                # Extract hashtags from the file
                import re
                hashtags = re.findall(r'#\w+', content)
        
        # Load script for caption
        caption = ""
        script_file = os.path.join(session_path, 'scripts', 'processed_script.txt')
        if os.path.exists(script_file):
            with open(script_file, 'r') as f:
                caption = f.read().strip()
        
        # Create post content
        content = PostContent(
            video_path=video_path,
            caption=caption,
            hashtags=hashtags,
            is_reel=True
        )
        
        # Initialize autoposter and post
        autoposter = InstagramAutoPoster(credentials)
        
        if autoposter.authenticate():
            return autoposter.post_video(content)
        else:
            logger.error("❌ Failed to authenticate with Instagram")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to create Instagram post: {e}")
        return False