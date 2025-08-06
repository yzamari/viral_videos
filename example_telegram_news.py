#!/usr/bin/env python3
"""Example: Create Hebrew news video from Ynet and Telegram channels"""

import subprocess
import sys

def main():
    """Run news aggregation with Telegram channels"""
    
    print("🎬 Creating Hebrew News Video with Telegram Integration")
    print("=" * 60)
    
    # Command to aggregate news from Ynet website and Telegram channels
    cmd = [
        sys.executable, "main.py", "news", "aggregate-enhanced",
        "https://www.ynet.co.il",  # Web source
        "--telegram-channels", "@ynet_news", "@channel13news",  # Telegram channels
        "--languages", "he",  # Hebrew
        "--platform", "tiktok",  # TikTok format (portrait)
        "--style", "modern news broadcast",
        "--tone", "professional and engaging",
        "--overlay-style", "modern",
        "--max-stories", "7",
        "--hours-back", "24",
        "--duration", "60"
    ]
    
    print("\n📌 Running command:")
    print(" ".join(cmd))
    print("\n" + "=" * 60)
    
    # Execute the command
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Video created successfully!")
        print("\n💡 Tips:")
        print("- Check outputs/session_* for the generated video")
        print("- Review news_aggregation_report.json for details")
        print("- To use real Telegram data, run: python setup_telegram.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Command failed with exit code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()