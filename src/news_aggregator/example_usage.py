"""Example usage of the News Aggregator system"""

import asyncio
from datetime import datetime
from typing import List

from .scrapers.web_scraper import WebNewsScraper
from .models.content_models import NewsSource, SourceType, ScrapingConfig
from .themes.theme_manager import ThemeManager
from .integration.viralai_bridge import ViralAIBridge


async def create_news_video_from_urls(
    urls: List[str],
    channel_name: str = "Daily News Digest",
    languages: List[str] = ["en", "he"],
    theme_name: str = "professional_news"
):
    """Create a news video from a list of URLs"""
    
    print(f"\n=== {channel_name} - {datetime.now().strftime('%Y-%m-%d')} ===\n")
    
    # 1. Initialize components
    scraper = WebNewsScraper()
    theme_manager = ThemeManager()
    bridge = ViralAIBridge()
    
    # 2. Load theme
    theme = theme_manager.load_theme(theme_name)
    print(f"Loaded theme: {theme.name}")
    
    # 3. Create session
    session_id = await bridge.create_news_session(
        channel_name=channel_name,
        episode_title=f"Episode {datetime.now().strftime('%Y%m%d')}",
        language=languages[0]
    )
    print(f"Created session: {session_id}")
    
    # 4. Scrape content from URLs
    all_articles = []
    for url in urls:
        print(f"\nScraping: {url}")
        source = NewsSource(
            id=f"source_{len(all_articles)}",
            name=url.split('/')[2],  # Extract domain
            source_type=SourceType.WEB,
            url=url,
            scraping_config=ScrapingConfig(max_items=5)
        )
        
        articles = await scraper.scrape(source)
        print(f"Found {len(articles)} articles")
        all_articles.extend(articles)
    
    # 5. Process articles for each language
    for lang in languages:
        print(f"\n--- Processing for {lang.upper()} ---")
        
        video_segments = []
        audio_tracks = []
        subtitles = []
        
        # 6. Create intro
        intro_text = {
            "en": f"Welcome to {channel_name}. Here are today's top stories.",
            "he": f"ברוכים הבאים ל{channel_name}. הנה הסיפורים המובילים של היום."
        }
        
        # Generate intro audio
        intro_audio = await bridge.generate_audio_narration(
            text=intro_text.get(lang, intro_text["en"]),
            language=lang,
            voice_style="news_anchor"
        )
        audio_tracks.append(intro_audio)
        
        # 7. Process each article
        for i, article in enumerate(all_articles[:5]):  # Top 5 stories
            print(f"\nProcessing article {i+1}: {article.title[:50]}...")
            
            # Translate if needed
            if article.language != lang:
                title = await bridge.translate_content(
                    article.title, article.language, lang
                )
                summary = await bridge.summarize_content(
                    article.content, max_length=100, language=lang
                )
            else:
                title = article.title
                summary = await bridge.summarize_content(
                    article.content, max_length=100, language=lang
                )
            
            # Generate narration
            narration_text = f"{title}. {summary}"
            audio_path = await bridge.generate_audio_narration(
                text=narration_text,
                language=lang,
                voice_style="news_anchor"
            )
            audio_tracks.append(audio_path)
            
            # Generate or use existing video
            if article.media_assets and article.has_video():
                # Download and use existing video
                video_asset = article.get_primary_media()
                local_video = await scraper.download_media(video_asset)
                video_segments.append({
                    "path": local_video,
                    "duration": 10.0,
                    "title": title
                })
            else:
                # Generate video with VEO-3
                video_prompt = f"News footage related to: {title}"
                video_path = await bridge.generate_video_segment(
                    prompt=video_prompt,
                    duration=10.0,
                    use_veo3_fast=True
                )
                video_segments.append({
                    "path": video_path,
                    "duration": 10.0,
                    "title": title
                })
            
            # Generate subtitles
            subtitle_path = await bridge.generate_subtitles(
                audio_path=audio_path,
                text=narration_text,
                language=lang,
                style="news_lower_third"
            )
            subtitles.append(subtitle_path)
        
        # 8. Create outro
        outro_text = {
            "en": f"Thanks for watching {channel_name}. See you next time!",
            "he": f"תודה שצפיתם ב{channel_name}. נתראה בפעם הבאה!"
        }
        
        outro_audio = await bridge.generate_audio_narration(
            text=outro_text.get(lang, outro_text["en"]),
            language=lang,
            voice_style="news_anchor"
        )
        audio_tracks.append(outro_audio)
        
        # 9. Compose final video
        output_filename = f"{channel_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}_{lang}.mp4"
        output_path = f"outputs/news_videos/{output_filename}"
        
        final_video = await bridge.compose_final_video(
            segments=video_segments,
            audio_tracks=audio_tracks,
            subtitles=subtitles,
            output_path=output_path,
            theme_config=theme_manager.apply_theme_to_video(
                theme, bridge.get_video_config()
            )
        )
        
        print(f"\n✅ Created video: {final_video}")
    
    print(f"\n=== Completed {channel_name} ===\n")


async def main():
    """Example: Create a bilingual news video"""
    
    # Example news sources
    urls = [
        "https://www.bbc.com/news/technology",
        "https://www.ynet.co.il/digital",
        # Add more URLs as needed
    ]
    
    # Create news video
    await create_news_video_from_urls(
        urls=urls,
        channel_name="Tech News Today",
        languages=["en", "he"],
        theme_name="modern_tech"  # or "professional_news" or "hebrew_news"
    )


if __name__ == "__main__":
    asyncio.run(main())