"""News Command using SCRAPED MEDIA ONLY - NO VEO"""

import click
import asyncio
from typing import List, Optional

from ..aggregator_scraped_media import create_scraped_media_news_edition
from ...utils.logging_config import get_logger

logger = get_logger(__name__)


@click.command()
@click.argument('sources', nargs=-1, required=True)
@click.option('--type', 'edition_type',
              type=click.Choice(['general', 'gossip', 'sports', 'finance', 'tech']),
              default='general',
              help='Type of news edition')
@click.option('--style',
              type=click.Choice(['professional', 'casual', 'humorous', 'dramatic']),
              default='professional',
              help='Visual and presentation style')
@click.option('--tone',
              type=click.Choice(['informative', 'entertaining', 'critical', 'analytical']),
              default='informative',
              help='Tone of the content')
@click.option('--language', '-l',
              default='en',
              help='Primary language (en, he, es, etc.)')
@click.option('--duration', '-d',
              type=int,
              default=5,
              help='Duration in minutes')
@click.option('--output', '-o',
              help='Output filename')
def news_scraped(sources: List[str], edition_type: str, style: str, tone: str,
                language: str, duration: int, output: Optional[str]):
    """Create news edition using ONLY scraped media (NO VEO)
    
    This command:
    1. Scrapes actual news articles and media from sources
    2. Downloads real images/videos from the articles
    3. Uses AI agents to plan the editorial flow
    4. Creates video using ONLY the scraped media with FFmpeg
    5. NO VEO/AI video generation is used
    
    Examples:
        
        # News from Ynet and CNN using scraped media
        python main.py news-scraped https://www.ynet.co.il https://www.cnn.com
        
        # Tech news with scraped media
        python main.py news-scraped https://www.cnn.com/tech --type tech
        
        # Hebrew news from Ynet (7 minutes)
        python main.py news-scraped https://www.ynet.co.il --language he --duration 7
    """
    
    print("🎬 Creating news edition using SCRAPED MEDIA ONLY")
    print("📸 NO VEO/AI generation - using actual media from news sources")
    print(f"📰 Sources: {', '.join(sources)}")
    print(f"⚙️  Type: {edition_type}, Style: {style}, Tone: {tone}")
    print(f"⏱️  Duration: {duration} minutes, Language: {language}")
    
    try:
        output_path = asyncio.run(create_scraped_media_news_edition(
            source_urls=list(sources),
            edition_type=edition_type,
            style=style,
            tone=tone,
            duration_minutes=duration,
            language=language,
            output_filename=output
        ))
        
        print(f"\n✅ News edition created: {output_path}")
        print("📸 Used ONLY scraped media from news sources")
        print("🚫 NO VEO/AI video generation was used")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    news_scraped()