#!/usr/bin/env python3
"""
Test script to verify Instagram credentials are automatically loaded from .env file
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_env_credentials():
    """Test loading Instagram credentials from .env file"""
    print("🔧 Testing Instagram credentials from .env file")
    print("=" * 50)
    
    try:
        # Import the factory function
        from src.social.instagram_autoposter import create_instagram_autoposter_from_env
        
        # Try to create autoposter from .env
        autoposter = create_instagram_autoposter_from_env()
        
        if autoposter:
            print("✅ Successfully created Instagram autoposter from .env file")
            print(f"👤 Username: {autoposter.credentials.username}")
            print(f"🔐 Password: {'*' * len(autoposter.credentials.password)}")
            print(f"📁 Session file: {autoposter.session_file}")
            
            # Test authentication
            print("\n🔐 Testing authentication...")
            if autoposter.authenticate():
                print("✅ Authentication successful!")
                autoposter.disconnect()
                return True
            else:
                print("❌ Authentication failed")
                return False
        else:
            print("❌ Failed to create Instagram autoposter from .env file")
            print("💡 Make sure you have INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in your .env file")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_env_file():
    """Check if .env file exists and has Instagram credentials"""
    print("\n📁 Checking .env file...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Run 'python setup_instagram_credentials.py' to create it")
        return False
    
    print("✅ .env file found")
    
    # Check for Instagram credentials
    with open(env_file, 'r') as f:
        content = f.read()
        
    if 'INSTAGRAM_USERNAME' in content and 'INSTAGRAM_PASSWORD' in content:
        print("✅ Instagram credentials found in .env file")
        return True
    else:
        print("❌ Instagram credentials not found in .env file")
        print("💡 Add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to your .env file")
        return False

def main():
    """Main test function"""
    print("🧪 Instagram .env Credentials Test")
    print("=" * 50)
    
    # Check .env file first
    if not check_env_file():
        return False
    
    # Test the factory function
    if test_env_credentials():
        print("\n🎉 All tests passed!")
        print("💡 Instagram autoposter can now automatically load credentials from .env file")
        return True
    else:
        print("\n❌ Tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 