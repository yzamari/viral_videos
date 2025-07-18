"""
Social Media Configuration Manager
Handles user credentials and posting preferences for social platforms
"""

import os
import json
import getpass
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import keyring
from cryptography.fernet import Fernet

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class SocialCredentials:
    """Social media platform credentials"""
    platform: str
    username: str
    password: str
    two_factor_code: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = None

@dataclass
class PostingPreferences:
    """User posting preferences"""
    auto_post: bool = False
    platforms: list = None
    default_caption_template: str = "{script}"
    always_use_hashtags: bool = True
    max_hashtags: int = 30
    schedule_posts: bool = False
    auto_delete_days: Optional[int] = None
    location_tagging: bool = False
    default_location: Optional[str] = None
    mention_accounts: list = None
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = []
        if self.mention_accounts is None:
            self.mention_accounts = []

class SocialConfigManager:
    """Manages social media configuration and credentials"""
    
    def __init__(self, config_dir: str = None):
        """Initialize configuration manager"""
        self.config_dir = config_dir or os.path.expanduser("~/.viralai/social")
        self.credentials_file = os.path.join(self.config_dir, "credentials.json")
        self.preferences_file = os.path.join(self.config_dir, "preferences.json")
        self.encryption_key_file = os.path.join(self.config_dir, "key.key")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Initialize encryption
        self.cipher = self._get_or_create_cipher()
        
        logger.info(f"🔧 Social config manager initialized: {self.config_dir}")
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption cipher for sensitive data"""
        try:
            if os.path.exists(self.encryption_key_file):
                with open(self.encryption_key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(self.encryption_key_file, 'wb') as f:
                    f.write(key)
                os.chmod(self.encryption_key_file, 0o600)  # Read-only for owner
            
            return Fernet(key)
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize encryption: {e}")
            # Fallback to no encryption
            return None
    
    def setup_instagram_credentials(self) -> bool:
        """Interactive setup for Instagram credentials"""
        try:
            logger.info("🔐 Setting up Instagram credentials")
            
            print("\n📱 Instagram Account Setup")
            print("=" * 30)
            
            username = input("Enter Instagram username: ").strip()
            if not username:
                logger.error("❌ Username cannot be empty")
                return False
            
            password = getpass.getpass("Enter Instagram password: ").strip()
            if not password:
                logger.error("❌ Password cannot be empty")
                return False
            
            # Check if 2FA is enabled
            use_2fa = input("Do you have 2FA enabled? (y/n): ").strip().lower() == 'y'
            two_factor_code = None
            
            if use_2fa:
                print("💡 Note: You'll need to provide 2FA codes when posting")
                print("💡 Consider using app passwords or session persistence")
            
            # Additional configuration
            additional_config = {}
            
            # Ask about session persistence
            save_session = input("Save login session for faster future posts? (y/n): ").strip().lower() == 'y'
            additional_config['save_session'] = save_session
            
            # Ask about posting preferences
            print("\n📝 Posting Preferences")
            print("=" * 20)
            
            preferences = PostingPreferences()
            
            auto_post = input("Enable automatic posting after video generation? (y/n): ").strip().lower() == 'y'
            preferences.auto_post = auto_post
            
            if auto_post:
                preferences.platforms = ['instagram']
                
                # Caption template
                print("\n💬 Caption Template Options:")
                print("1. Use video script as caption")
                print("2. Custom template")
                print("3. Script + custom message")
                
                choice = input("Choose caption option (1-3): ").strip()
                
                if choice == '1':
                    preferences.default_caption_template = "{script}"
                elif choice == '2':
                    custom_template = input("Enter custom caption template: ").strip()
                    preferences.default_caption_template = custom_template
                elif choice == '3':
                    custom_message = input("Enter custom message to add: ").strip()
                    preferences.default_caption_template = f"{custom_message}\\n\\n{{script}}"
                
                # Hashtag preferences
                use_hashtags = input("Always include generated hashtags? (y/n): ").strip().lower() == 'y'
                preferences.always_use_hashtags = use_hashtags
                
                if use_hashtags:
                    max_hashtags = input("Maximum hashtags to use (default 30): ").strip()
                    try:
                        preferences.max_hashtags = int(max_hashtags) if max_hashtags else 30
                    except ValueError:
                        preferences.max_hashtags = 30
                
                # Mentions
                mentions = input("Default accounts to mention (comma-separated, optional): ").strip()
                if mentions:
                    preferences.mention_accounts = [m.strip() for m in mentions.split(',')]
                
                # Location tagging
                location_tag = input("Enable location tagging? (y/n): ").strip().lower() == 'y'
                preferences.location_tagging = location_tag
                
                if location_tag:
                    default_location = input("Default location (optional): ").strip()
                    if default_location:
                        preferences.default_location = default_location
            
            # Save credentials
            instagram_creds = SocialCredentials(
                platform='instagram',
                username=username,
                password=password,
                two_factor_code=two_factor_code,
                additional_config=additional_config
            )
            
            if self.save_credentials('instagram', instagram_creds):
                logger.info("✅ Instagram credentials saved securely")
            else:
                logger.error("❌ Failed to save Instagram credentials")
                return False
            
            # Save preferences
            if self.save_preferences(preferences):
                logger.info("✅ Posting preferences saved")
            else:
                logger.error("❌ Failed to save posting preferences")
                return False
            
            print("\n✅ Instagram setup completed successfully!")
            print("💡 You can now use --auto-post flag to automatically post generated videos")
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user")
            return False
        except Exception as e:
            logger.error(f"❌ Instagram setup failed: {e}")
            return False
    
    def save_credentials(self, platform: str, credentials: SocialCredentials) -> bool:
        """Save encrypted credentials for a platform"""
        try:
            # Load existing credentials
            all_credentials = self.load_all_credentials()
            
            # Convert credentials to dict for serialization
            creds_dict = asdict(credentials)
            
            # Encrypt sensitive data
            if self.cipher:
                creds_dict['password'] = self.cipher.encrypt(credentials.password.encode()).decode()
                if credentials.two_factor_code:
                    creds_dict['two_factor_code'] = self.cipher.encrypt(credentials.two_factor_code.encode()).decode()
                if credentials.access_token:
                    creds_dict['access_token'] = self.cipher.encrypt(credentials.access_token.encode()).decode()
                creds_dict['encrypted'] = True
            else:
                creds_dict['encrypted'] = False
            
            # Update credentials
            all_credentials[platform] = creds_dict
            
            # Save to file
            with open(self.credentials_file, 'w') as f:
                json.dump(all_credentials, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.credentials_file, 0o600)
            
            logger.info(f"✅ Credentials saved for {platform}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save credentials: {e}")
            return False
    
    def load_credentials(self, platform: str) -> Optional[SocialCredentials]:
        """Load decrypted credentials for a platform"""
        try:
            if not os.path.exists(self.credentials_file):
                return None
            
            with open(self.credentials_file, 'r') as f:
                all_credentials = json.load(f)
            
            if platform not in all_credentials:
                return None
            
            creds_dict = all_credentials[platform]
            
            # Decrypt sensitive data
            if creds_dict.get('encrypted', False) and self.cipher:
                creds_dict['password'] = self.cipher.decrypt(creds_dict['password'].encode()).decode()
                if creds_dict.get('two_factor_code'):
                    creds_dict['two_factor_code'] = self.cipher.decrypt(creds_dict['two_factor_code'].encode()).decode()
                if creds_dict.get('access_token'):
                    creds_dict['access_token'] = self.cipher.decrypt(creds_dict['access_token'].encode()).decode()
            
            # Remove encryption flag
            creds_dict.pop('encrypted', None)
            
            # Convert back to dataclass
            return SocialCredentials(**creds_dict)
            
        except Exception as e:
            logger.error(f"❌ Failed to load credentials for {platform}: {e}")
            return None
    
    def load_all_credentials(self) -> Dict[str, Dict]:
        """Load all stored credentials"""
        try:
            if not os.path.exists(self.credentials_file):
                return {}
            
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"❌ Failed to load credentials: {e}")
            return {}
    
    def save_preferences(self, preferences: PostingPreferences) -> bool:
        """Save posting preferences"""
        try:
            prefs_dict = asdict(preferences)
            
            with open(self.preferences_file, 'w') as f:
                json.dump(prefs_dict, f, indent=2)
            
            logger.info("✅ Posting preferences saved")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save preferences: {e}")
            return False
    
    def load_preferences(self) -> PostingPreferences:
        """Load posting preferences"""
        try:
            if not os.path.exists(self.preferences_file):
                return PostingPreferences()
            
            with open(self.preferences_file, 'r') as f:
                prefs_dict = json.load(f)
            
            return PostingPreferences(**prefs_dict)
            
        except Exception as e:
            logger.error(f"❌ Failed to load preferences: {e}")
            return PostingPreferences()
    
    def delete_credentials(self, platform: str) -> bool:
        """Delete credentials for a platform"""
        try:
            all_credentials = self.load_all_credentials()
            
            if platform in all_credentials:
                del all_credentials[platform]
                
                with open(self.credentials_file, 'w') as f:
                    json.dump(all_credentials, f, indent=2)
                
                logger.info(f"✅ Credentials deleted for {platform}")
                return True
            else:
                logger.warning(f"⚠️ No credentials found for {platform}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to delete credentials: {e}")
            return False
    
    def list_configured_platforms(self) -> list:
        """List all configured platforms"""
        try:
            all_credentials = self.load_all_credentials()
            return list(all_credentials.keys())
            
        except Exception as e:
            logger.error(f"❌ Failed to list platforms: {e}")
            return []
    
    def test_credentials(self, platform: str) -> bool:
        """Test if credentials are valid"""
        try:
            credentials = self.load_credentials(platform)
            if not credentials:
                logger.error(f"❌ No credentials found for {platform}")
                return False
            
            if platform == 'instagram':
                from .instagram_autoposter import InstagramAutoPoster, InstagramCredentials
                
                ig_creds = InstagramCredentials(
                    username=credentials.username,
                    password=credentials.password,
                    two_factor_code=credentials.two_factor_code
                )
                
                autoposter = InstagramAutoPoster(ig_creds)
                return autoposter.authenticate()
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to test credentials: {e}")
            return False
    
    def get_posting_summary(self) -> Dict[str, Any]:
        """Get summary of posting configuration"""
        try:
            preferences = self.load_preferences()
            platforms = self.list_configured_platforms()
            
            return {
                'auto_post_enabled': preferences.auto_post,
                'configured_platforms': platforms,
                'default_caption_template': preferences.default_caption_template,
                'use_hashtags': preferences.always_use_hashtags,
                'max_hashtags': preferences.max_hashtags,
                'mention_accounts': preferences.mention_accounts,
                'location_tagging': preferences.location_tagging
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get posting summary: {e}")
            return {}