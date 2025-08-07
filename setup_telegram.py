#!/usr/bin/env python3
"""Setup script for Telegram API credentials"""

import sys
import os
from pathlib import Path
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.news_aggregator.scrapers.telegram_api_scraper import TelegramConfig

def main():
    """Setup Telegram API credentials"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         TELEGRAM NEWS SCRAPER SETUP                       ║
║                                                            ║
║  Configure Telegram API for news channel scraping         ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Check if credentials already exist
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        if "TELEGRAM_API_ID=" in content:
            print("⚠️  Telegram credentials already configured!")
            
            # Extract existing credentials for display
            import re
            api_id_match = re.search(r'TELEGRAM_API_ID=(\d+)', content)
            api_hash_match = re.search(r'TELEGRAM_API_HASH=(\w+)', content)
            
            if api_id_match and api_hash_match:
                print(f"   API ID: {api_id_match.group(1)}")
                print(f"   API Hash: {api_hash_match.group(1)[:10]}...")
            
            response = input("\nDo you want to reconfigure? (y/N): ").strip().lower()
            if response != 'y':
                print("Keeping existing credentials.")
                show_usage()
                return
    
    # Run setup
    try:
        credentials = TelegramConfig.setup_credentials()
        print("\n✅ Setup complete!")
        
        # Test connection
        test = input("\nWould you like to test the connection? (Y/n): ").strip().lower()
        if test != 'n':
            test_connection(credentials)
        
        show_usage()
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")

def test_connection(credentials):
    """Test Telegram connection"""
    print("\n🧪 Testing Telegram connection...")
    
    try:
        from src.news_aggregator.scrapers.telegram_api_scraper import TelegramAPIScraper
        
        async def test():
            scraper = TelegramAPIScraper(
                api_id=credentials['api_id'],
                api_hash=credentials['api_hash'],
                phone=credentials.get('phone'),
                session_name='test_session'
            )
            
            try:
                await scraper.initialize()
                print("✅ Successfully connected to Telegram!")
                
                # Try to get user info
                if scraper.client:
                    me = await scraper.client.get_me()
                    print(f"   Logged in as: {me.first_name} {me.last_name or ''}")
                    if me.username:
                        print(f"   Username: @{me.username}")
                
            finally:
                await scraper.close()
                
                # Clean up test session
                for session_file in Path('.').glob('test_session*'):
                    session_file.unlink()
        
        asyncio.run(test())
        
    except ImportError:
        print("❌ Required packages not installed. Run: pip3 install telethon")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPlease check your credentials and try again.")

def show_usage():
    """Show usage examples"""
    print("\n" + "="*60)
    print("📱 TELEGRAM CHANNEL SCRAPING EXAMPLES")
    print("="*60)
    
    print("\n1️⃣  Scrape a single Telegram channel:")
    print("   python3 main.py news aggregate-enhanced \\")
    print("     --telegram-channels @channel_name \\")
    print("     --platform tiktok --duration 60")
    
    print("\n2️⃣  Scrape multiple Telegram channels:")
    print("   python3 main.py news aggregate-enhanced \\")
    print("     --telegram-channels @ynet_news \\")
    print("     --telegram-channels @channel13news \\")
    print("     --telegram-channels @kann_news")
    
    print("\n3️⃣  Mix Telegram with web sources:")
    print("   python3 main.py news aggregate-enhanced \\")
    print("     https://www.ynet.co.il \\")
    print("     --telegram-channels @breaking_news \\")
    print("     --style 'dark humor satire'")
    
    print("\n📺 Popular Israeli News Channels:")
    print("   @ynet_news       - Ynet News")
    print("   @channel13news   - Channel 13 News")
    print("   @kann_news       - Kann News")
    print("   @N12News         - Channel 12 News")
    print("   @glz_news        - Galei Tzahal")
    print("   @srugim_news     - Srugim News")
    print("   @news0404        - 0404 News")
    
    print("\n💡 Tips:")
    print("   • Channels can be specified with or without @ prefix")
    print("   • Use --hours-back to control how far back to scrape")
    print("   • Add --use-youtube-videos to include video backgrounds")
    print("   • Use --no-ai-discussion for faster processing")

if __name__ == "__main__":
    main()