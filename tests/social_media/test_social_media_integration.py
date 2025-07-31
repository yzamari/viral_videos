#!/usr/bin/env python3
"""
Test Script for Social Media Integration
Demonstrates WhatsApp and Telegram video sending capabilities
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.social.social_media_manager import SocialMediaManager
from src.social.whatsapp_sender import WhatsAppSender
from src.social.telegram_sender import TelegramSender

def test_whatsapp_integration():
    """Test WhatsApp integration"""
    print("🧪 Testing WhatsApp Integration")
    print("=" * 50)
    
    # Check if credentials are available
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    if not access_token or not phone_number_id:
        print("❌ WhatsApp credentials not found in environment variables")
        print("   Set WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID")
        return False
    
    try:
        # Initialize WhatsApp sender
        whatsapp = WhatsAppSender(
            access_token=access_token,
            phone_number_id=phone_number_id
        )
        
        # Validate credentials
        if not whatsapp.validate_credentials():
            print("❌ Invalid WhatsApp credentials")
            return False
        
        print("✅ WhatsApp credentials validated")
        
        # Test group info (if group ID is provided)
        test_group_id = os.getenv('WHATSAPP_TEST_GROUP_ID')
        if test_group_id:
            group_info = whatsapp.get_group_info(test_group_id)
            if group_info:
                print(f"✅ Group info retrieved: {group_info.get('name', 'Unknown')}")
            else:
                print("⚠️ Could not retrieve group info")
        
        return True
        
    except Exception as e:
        print(f"❌ WhatsApp test failed: {e}")
        return False

def test_telegram_integration():
    """Test Telegram integration"""
    print("\n🧪 Testing Telegram Integration")
    print("=" * 50)
    
    # Check if credentials are available
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ Telegram bot token not found in environment variables")
        print("   Set TELEGRAM_BOT_TOKEN")
        return False
    
    try:
        # Initialize Telegram sender
        telegram = TelegramSender(bot_token=bot_token)
        
        # Validate credentials
        if not telegram.validate_credentials():
            print("❌ Invalid Telegram bot token")
            return False
        
        print("✅ Telegram bot credentials validated")
        
        # Test getting updates
        updates = telegram.get_updates()
        print(f"✅ Retrieved {len(updates)} updates from Telegram")
        
        # Test chat info (if chat ID is provided)
        test_chat_id = os.getenv('TELEGRAM_TEST_CHAT_ID')
        if test_chat_id:
            chat_info = telegram.get_chat_info(test_chat_id)
            if chat_info:
                print(f"✅ Chat info retrieved: {chat_info.get('title', 'Unknown')}")
                member_count = telegram.get_chat_members_count(test_chat_id)
                print(f"✅ Member count: {member_count}")
            else:
                print("⚠️ Could not retrieve chat info")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False

def test_social_media_manager():
    """Test unified social media manager"""
    print("\n🧪 Testing Social Media Manager")
    print("=" * 50)
    
    try:
        # Initialize manager
        manager = SocialMediaManager()
        
        # Get status
        status = manager.get_status()
        print("📊 Platform Status:")
        for platform, info in status.items():
            print(f"   {platform.title()}:")
            print(f"     Enabled: {info['enabled']}")
            print(f"     Configured: {info['configured']}")
            print(f"     Groups: {info['groups_count']}")
        
        # Test analytics
        analytics = manager.get_sending_analytics()
        print(f"\n📈 Analytics:")
        print(f"   Total sent: {analytics['total_sent']}")
        print(f"   Success rate: {analytics['success_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Social media manager test failed: {e}")
        return False

def test_video_sending_simulation():
    """Simulate video sending (without actually sending)"""
    print("\n🧪 Testing Video Sending Simulation")
    print("=" * 50)
    
    # Create a dummy video file for testing
    test_video_path = "test_video.mp4"
    if not os.path.exists(test_video_path):
        # Create a dummy file
        with open(test_video_path, 'w') as f:
            f.write("Dummy video content for testing")
        print(f"✅ Created test video file: {test_video_path}")
    
    try:
        # Initialize manager
        manager = SocialMediaManager()
        
        # Simulate sending (this won't actually send if credentials aren't configured)
        print("📤 Simulating video sending...")
        
        # Test WhatsApp (if configured)
        if manager.whatsapp_sender:
            print("   WhatsApp: Ready to send")
        else:
            print("   WhatsApp: Not configured")
        
        # Test Telegram (if configured)
        if manager.telegram_sender:
            print("   Telegram: Ready to send")
        else:
            print("   Telegram: Not configured")
        
        # Clean up test file
        if os.path.exists(test_video_path):
            os.remove(test_video_path)
            print(f"✅ Cleaned up test file: {test_video_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Video sending simulation failed: {e}")
        return False

def demonstrate_usage():
    """Demonstrate usage examples"""
    print("\n📚 Usage Examples")
    print("=" * 50)
    
    print("1. Basic Setup:")
    print("""
from src.social.social_media_manager import SocialMediaManager

# Initialize manager
manager = SocialMediaManager("config/social_media.json")

# Configure WhatsApp
manager.configure_whatsapp(
    access_token="YOUR_ACCESS_TOKEN",
    phone_number_id="YOUR_PHONE_NUMBER_ID",
    enabled=True
)

# Configure Telegram
manager.configure_telegram(
    bot_token="YOUR_BOT_TOKEN",
    bot_username="your_bot_username",
    enabled=True
)
""")
    
    print("2. Send Video to All Platforms:")
    print("""
# Send video to all configured platforms
results = manager.send_video_to_all_platforms(
    video_path="outputs/viral_video.mp4",
    mission="Teach about climate change",
    platform="instagram",
    hashtags=["climate", "education", "viral"]
)

print(f"Results: {results}")
""")
    
    print("3. Platform-Specific Sending:")
    print("""
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
""")
    
    print("4. Analytics:")
    print("""
# Get sending analytics
analytics = manager.get_sending_analytics()
print(f"Total sent: {analytics['total_sent']}")
print(f"Success rate: {analytics['success_rate']:.1%}")
print(f"Platform breakdown: {analytics['platform_breakdown']}")
""")

def main():
    """Main test function"""
    print("🚀 ViralAI Social Media Integration Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Run tests
    tests = [
        ("WhatsApp Integration", test_whatsapp_integration),
        ("Telegram Integration", test_telegram_integration),
        ("Social Media Manager", test_social_media_manager),
        ("Video Sending Simulation", test_video_sending_simulation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Show usage examples
    demonstrate_usage()
    
    # Print next steps
    print("\n🎯 Next Steps")
    print("=" * 50)
    print("1. Set up your credentials in environment variables:")
    print("   export WHATSAPP_ACCESS_TOKEN='your_token'")
    print("   export WHATSAPP_PHONE_NUMBER_ID='your_phone_id'")
    print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
    print()
    print("2. Create a configuration file:")
    print("   cp config/social_media.example.json config/social_media.json")
    print("   # Edit the file with your credentials")
    print()
    print("3. Add target groups:")
    print("   manager.add_whatsapp_group('GROUP_ID')")
    print("   manager.add_telegram_group('CHAT_ID')")
    print()
    print("4. Start sending videos!")
    print("   manager.send_video_to_all_platforms(...)")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 