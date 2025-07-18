#!/usr/bin/env python3
"""
Instagram Credentials Setup Script
Helps you configure Instagram credentials for the Viral AI Video Generator
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create or update .env file with Instagram credentials"""
    
    # Check if .env exists
    env_path = Path(".env")
    env_content = ""
    
    if env_path.exists():
        print("📁 Found existing .env file")
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        print("📁 Creating new .env file")
    
    # Instagram credentials section
    instagram_section = """# =============================================================================
# INSTAGRAM INTEGRATION SETTINGS
# =============================================================================

# Instagram Credentials (for instagrapi - RECOMMENDED)
INSTAGRAM_USERNAME=yzamari@gmail.com
INSTAGRAM_PASSWORD=Nvnnh@123
INSTAGRAM_2FA_CODE=your_2fa_code_if_needed

# Instagram Basic Display API (Alternative - requires app review)
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret

# Instagram Posting Preferences
INSTAGRAM_POST_AS_REEL=true
INSTAGRAM_AUTO_HASHTAGS=true
INSTAGRAM_SCHEDULE_POSTS=false
INSTAGRAM_AUTO_DELETE_DAYS=0

# Instagram Error Handling
INSTAGRAM_MAX_RETRIES=3
INSTAGRAM_RETRY_DELAY=30

"""
    
    # Check if Instagram section already exists
    if "INSTAGRAM_USERNAME" not in env_content:
        # Add Instagram section to existing content
        if env_content:
            env_content += "\n" + instagram_section
        else:
            # Create basic .env file
            env_content = """# =============================================================================
# VIRAL AI VIDEO GENERATOR - ENVIRONMENT CONFIGURATION
# =============================================================================

# Core API Keys
GOOGLE_API_KEY=your_google_ai_studio_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

""" + instagram_section
    
    # Write the .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created/updated successfully!")
    return True

def test_credentials():
    """Test the configured Instagram credentials"""
    print("\n🧪 Testing Instagram Credentials...")
    
    # Get credentials from environment
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("❌ Instagram credentials not found in environment")
        print("💡 Make sure to set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD")
        return False
    
    print(f"👤 Username: {username}")
    print(f"🔐 Password: {'*' * len(password)}")
    
    try:
        # Test with instagrapi
        from instagrapi import Client
        
        cl = Client()
        login_success = cl.login(username=username, password=password)
        
        if login_success:
            print("✅ Instagram authentication successful!")
            return True
        else:
            print("❌ Instagram authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def show_usage_examples():
    """Show examples of how to use Instagram posting"""
    print("\n📚 Usage Examples:")
    print("=" * 50)
    
    print("\n1. 🎬 Generate and post a video to Instagram:")
    print("   python main.py generate --mission \"Your mission\" --platform instagram --duration 15")
    
    print("\n2. 📤 Post an existing video:")
    print("   python test_instagram_real_posting.py")
    
    print("\n3. 🧪 Test credentials:")
    print("   python test_instagram_integration.py")
    
    print("\n4. 📁 Post from a session:")
    print("   python -c \"")
    print("   from src.social.instagram_autoposter import create_instagram_post_from_session, InstagramCredentials")
    print("   credentials = InstagramCredentials(username='yzamari@gmail.com', password='Nvnnh@123')")
    print("   create_instagram_post_from_session('outputs/session_YYYYMMDD_HHMMSS', credentials)")
    print("   \"")

def main():
    """Main setup function"""
    print("📱 Instagram Credentials Setup")
    print("=" * 50)
    
    # Step 1: Create/update .env file
    print("\n🔧 Step 1: Setting up .env file...")
    if create_env_file():
        print("✅ .env file configured")
    else:
        print("❌ Failed to configure .env file")
        return
    
    # Step 2: Load environment variables
    print("\n🔧 Step 2: Loading environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded")
    
    # Step 3: Test credentials
    print("\n🔧 Step 3: Testing credentials...")
    if test_credentials():
        print("✅ Credentials are working!")
    else:
        print("⚠️ Credentials test failed - check your username/password")
    
    # Step 4: Show usage examples
    show_usage_examples()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n💡 Next steps:")
    print("1. Your Instagram credentials are now configured")
    print("2. You can generate videos with --platform instagram")
    print("3. Videos will be automatically posted to your Instagram account")
    print("4. Check the usage examples above for more options")

if __name__ == "__main__":
    main() 