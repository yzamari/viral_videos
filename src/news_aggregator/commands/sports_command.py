"""Sports Video Command - Creates videos from scraped sports media"""

import asyncio
import click
from typing import Optional

from ..scrapers.sports_scraper import scrape_funny_sports_videos
from ..composers.scraped_media_composer import create_scraped_media_video
from ...utils.logging_config import get_logger

logger = get_logger(__name__)


async def create_sports_video_from_scraped_media(
    duration_seconds: int = 30,
    style: str = "fast-paced",
    content_type: str = "funny",
    output_filename: Optional[str] = None
) -> str:
    """Create sports video using ONLY scraped media"""
    
    logger.info(f"🏈 Creating {content_type} sports video ({duration_seconds}s)")
    logger.info("📸 Using SCRAPED MEDIA ONLY - NO VEO GENERATION")
    
    # 1. Scrape sports videos
    logger.info("🔍 Scraping sports videos from Reddit and other sources...")
    sports_content = await scrape_funny_sports_videos(max_items=30)
    
    if not sports_content:
        raise ValueError("No sports content found to scrape!")
    
    logger.info(f"✅ Found {len(sports_content)} sports videos/images")
    
    # 2. Filter by content type
    if content_type == "funny":
        # Filter for funny/fail content
        filtered = [
            item for item in sports_content
            if any(tag in item.tags for tag in ['funny', 'fails', 'blooper'])
        ]
        if filtered:
            sports_content = filtered
    
    # 3. Sort by relevance
    sports_content.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # 4. Show what we found
    logger.info("📋 Top sports content found:")
    for i, item in enumerate(sports_content[:5]):
        media_count = len(item.media_assets)
        logger.info(f"   {i+1}. {item.title[:60]}... ({media_count} media)")
    
    # 5. Create video from scraped media
    logger.info("🎬 Creating video from scraped media...")
    output_path = await create_scraped_media_video(
        content_items=sports_content,
        duration_seconds=duration_seconds,
        style=style,
        output_filename=output_filename
    )
    
    return output_path


@click.command()
@click.option('--duration', '-d', type=int, default=30,
              help='Video duration in seconds')
@click.option('--style', type=click.Choice(['fast-paced', 'normal', 'dramatic']),
              default='fast-paced', help='Video style')
@click.option('--type', 'content_type', 
              type=click.Choice(['funny', 'highlights', 'all']),
              default='funny', help='Type of sports content')
@click.option('--output', '-o', help='Output filename')
def sports_video(duration: int, style: str, content_type: str, output: Optional[str]):
    """Create sports video from scraped media (NO VEO)"""
    
    try:
        output_path = asyncio.run(create_sports_video_from_scraped_media(
            duration_seconds=duration,
            style=style,
            content_type=content_type,
            output_filename=output
        ))
        
        click.echo(f"\n✅ Sports video created: {output_path}")
        click.echo("📸 Used ONLY scraped media - NO AI generation")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        raise


if __name__ == "__main__":
    sports_video()