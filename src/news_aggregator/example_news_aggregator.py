"""Example usage of the News Aggregator"""

import asyncio
from aggregator import create_news_edition


async def main():
    """Example news aggregation scenarios"""
    
    print("🎬 News Aggregator Examples\n")
    
    # Example 1: General news from multiple sources
    print("1. Creating general news edition from CNN and Ynet...")
    try:
        video_path = await create_news_edition(
            sources=["https://www.cnn.com", "https://www.ynet.co.il"],
            edition_type="general",
            style="professional",
            tone="informative",
            visual_style="modern",
            language="en",
            duration_minutes=5,
            presenter_enabled=True,
            output_filename="general_news_edition.mp4"
        )
        print(f"✅ Created: {video_path}\n")
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
    
    # Example 2: Tech news edition
    print("2. Creating tech news edition...")
    try:
        video_path = await create_news_edition(
            sources=["https://www.cnn.com/tech", "https://reddit.com/r/technology"],
            edition_type="tech",
            style="casual",
            tone="entertaining",
            visual_style="dynamic",
            language="en",
            duration_minutes=7,
            presenter_enabled=True,
            output_filename="tech_news_edition.mp4"
        )
        print(f"✅ Created: {video_path}\n")
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
    
    # Example 3: Sports highlights
    print("3. Creating sports highlights...")
    try:
        video_path = await create_news_edition(
            sources=["https://cnn.com/sport", "https://reddit.com/r/sports"],
            edition_type="sports",
            style="dramatic",
            tone="exciting",
            visual_style="dynamic",
            language="en",
            duration_minutes=10,
            presenter_enabled=True,
            output_filename="sports_highlights.mp4"
        )
        print(f"✅ Created: {video_path}\n")
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
    
    # Example 4: Finance news (professional)
    print("4. Creating finance news edition...")
    try:
        video_path = await create_news_edition(
            sources=["https://cnn.com/business"],
            edition_type="finance",
            style="professional",
            tone="analytical",
            visual_style="minimalist",
            language="en",
            duration_minutes=5,
            presenter_enabled=False,  # No presenter for serious finance news
            output_filename="finance_news.mp4"
        )
        print(f"✅ Created: {video_path}\n")
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
    
    # Example 5: Entertainment/Gossip news
    print("5. Creating entertainment news...")
    try:
        video_path = await create_news_edition(
            sources=["https://reddit.com/r/entertainment"],
            edition_type="gossip",
            style="casual",
            tone="entertaining",
            visual_style="dynamic",
            language="en",
            duration_minutes=5,
            presenter_enabled=True,
            output_filename="entertainment_news.mp4"
        )
        print(f"✅ Created: {video_path}\n")
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())