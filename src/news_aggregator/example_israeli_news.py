"""Example: Generate Israeli News Video

This example shows how to create an Israeli news video with:
- Ynet and Rotter content scraping
- Dark humor commentary
- Alien presenter (Zorg)
- Ynet-style graphics
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.news_aggregator.israeli_news_generator import generate_israeli_news


async def main():
    """Generate Israeli news video with different styles"""
    
    print("🎬 Israeli News Generator Example")
    print("=" * 50)
    
    # Example 1: Dark humor style with alien
    print("\n1️⃣ Generating dark humor news with alien presenter...")
    try:
        video_path = await generate_israeli_news(
            style="dark_humor",
            include_alien=True,
            output_filename="israeli_news_dark_humor.mp4"
        )
        print(f"✅ Created: {video_path}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Example 2: Professional style without alien
    print("\n2️⃣ Generating professional news without alien...")
    try:
        video_path = await generate_israeli_news(
            style="professional",
            include_alien=False,
            output_filename="israeli_news_professional.mp4"
        )
        print(f"✅ Created: {video_path}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Example 3: Satirical style with alien
    print("\n3️⃣ Generating satirical news with alien...")
    try:
        video_path = await generate_israeli_news(
            style="satirical",
            include_alien=True,
            output_filename="israeli_news_satirical.mp4"
        )
        print(f"✅ Created: {video_path}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    # Usage via CLI (recommended):
    # python main.py news israeli --style dark_humor
    # python main.py news israeli --style professional --no-alien
    # python main.py news israeli --output my_news.mp4
    
    print("\n💡 Tip: Use the CLI for easier access:")
    print("   python main.py news israeli --style dark_humor")
    print("   python main.py news israeli --help\n")
    
    # Run examples
    asyncio.run(main())