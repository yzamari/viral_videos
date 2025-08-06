#!/usr/bin/env python3
"""Setup script for Telegram API credentials"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.news_aggregator.scrapers.telegram_api_scraper import TelegramConfig

def main():
    """Setup Telegram API credentials"""
    print("🚀 ViralAI Telegram Setup")
    print("=" * 50)
    
    # Check if credentials already exist
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        if "TELEGRAM_API_ID=" in content:
            print("⚠️  Telegram credentials already configured!")
            response = input("Do you want to reconfigure? (y/N): ").strip().lower()
            if response != 'y':
                print("Setup cancelled.")
                return
    
    # Run setup
    try:
        credentials = TelegramConfig.setup_credentials()
        print("\n✅ Setup complete!")
        print("\nYou can now use Telegram channels as news sources:")
        print("python main.py news aggregate-enhanced https://www.ynet.co.il --telegram-channels @channel_name")
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")

if __name__ == "__main__":
    main()