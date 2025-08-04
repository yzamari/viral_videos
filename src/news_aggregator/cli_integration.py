"""CLI integration for news aggregator"""

import click
import asyncio
from pathlib import Path
from typing import List, Optional

from .israeli_news_generator import generate_israeli_news
from .aggregator import create_news_edition
from .mock_aggregator import create_mock_news_edition
from .aggregator_scraped_media import create_scraped_media_news_edition
from .commands.sports_command import create_sports_video_from_scraped_media
# from .aggregator_v2 import create_news_edition_from_csv, create_news_edition_from_sources
# from .parsers.csv_parser import NewsCSVParser


def add_news_commands(cli_group):
    """Add news aggregator commands to CLI"""
    
    @cli_group.group()
    def news():
        """📰 News aggregation and video generation commands"""
        pass
    
    @news.command()
    @click.option('--style', type=click.Choice(['dark_humor', 'professional', 'casual', 'satirical']), 
                  default='dark_humor', help='Content style (default: dark_humor)')
    @click.option('--no-alien', is_flag=True, help='Disable alien presenter')
    @click.option('--output', help='Output filename')
    @click.option('--sources', multiple=True, default=['ynet', 'rotter'], 
                  help='News sources to scrape (default: ynet rotter)')
    def israeli(**kwargs):
        """🇮🇱 Generate Israeli news video with Ynet style and alien presenter"""
        try:
            print("🎬 Starting Israeli News Video Generation...")
            print(f"📰 Style: {kwargs['style']}")
            print(f"👽 Alien presenter: {'Disabled' if kwargs['no_alien'] else 'Enabled'}")
            
            # Run async generation
            output_path = asyncio.run(generate_israeli_news(
                style=kwargs['style'],
                include_alien=not kwargs['no_alien'],
                output_filename=kwargs.get('output')
            ))
            
            print(f"\n✅ Video created: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Failed to generate Israeli news: {e}")
            raise click.ClickException(str(e))
    
    @news.command()
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
    @click.option('--visual-style',
                  type=click.Choice(['modern', 'classic', 'dynamic', 'minimalist']),
                  default='modern',
                  help='Visual effects and design style')
    @click.option('--language', '-l',
                  default='en',
                  help='Primary language (en, he, es, etc.)')
    @click.option('--duration', '-d',
                  type=int,
                  default=5,
                  help='Duration in minutes')
    @click.option('--no-presenter', is_flag=True,
                  help='Disable AI presenter')
    @click.option('--output', '-o',
                  help='Output filename')
    def aggregate(sources: List[str], edition_type: str, style: str, tone: str,
                  visual_style: str, language: str, duration: int, 
                  no_presenter: bool, output: Optional[str]):
        """🌐 Create news edition from multiple sources
        
        Examples:
            
            # General news from CNN and Ynet
            python main.py news aggregate https://www.cnn.com https://www.ynet.co.il
            
            # Tech news with modern style
            python main.py news aggregate https://www.cnn.com/tech --type tech --visual-style modern
            
            # Gossip news with entertaining tone
            python main.py news aggregate https://reddit.com/r/entertainment --type gossip --tone entertaining
            
            # Sports highlights
            python main.py news aggregate https://cnn.com/sport https://reddit.com/r/sports --type sports
        """
        
        print(f"🎬 Creating {edition_type} news edition from {len(sources)} sources...")
        print(f"Style: {style}, Tone: {tone}, Visual: {visual_style}")
        print(f"Duration: {duration} minutes, Language: {language}")
        
        try:
            # Use mock aggregator for now to avoid dependency issues
            output_path = asyncio.run(create_mock_news_edition(
                sources=list(sources),
                edition_type=edition_type,
                style=style,
                tone=tone,
                duration_minutes=duration
            ))
            print(f"\n✅ News edition created: {output_path}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise click.ClickException(str(e))
    
    # CSV commands temporarily disabled - need to fix imports
    # @news.command()
    # def csv():
    #     """📄 Create news edition from CSV file"""
    #     print("CSV support coming soon - currently being fixed")
    
    # @news.command()  
    # def create_samples():
    #     """📝 Create sample CSV files for news aggregation"""
    #     print("Sample creation coming soon - currently being fixed")
    
    @news.command('scraped')
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
    def scraped_media(sources: List[str], edition_type: str, style: str, tone: str,
                     language: str, duration: int, output: Optional[str]):
        """🎥 Create news using SCRAPED MEDIA ONLY (NO VEO)
        
        This creates news videos using actual media from news sources.
        NO AI video generation - only real scraped content!
        
        Examples:
            python main.py news scraped https://www.ynet.co.il https://www.cnn.com
            python main.py news scraped https://www.cnn.com/tech --type tech --duration 3
        """
        
        print("🎬 Creating news edition using SCRAPED MEDIA ONLY")
        print("📸 NO VEO/AI generation - using actual media from news sources")
        print(f"📰 Sources: {', '.join(sources)}")
        
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
            print("📸 Used ONLY scraped media - NO AI generation")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise click.ClickException(str(e))
    
    @news.command('sports')
    @click.option('--duration', '-d', type=int, default=30,
                  help='Video duration in seconds')
    @click.option('--style', type=click.Choice(['fast-paced', 'normal', 'dramatic']),
                  default='fast-paced', help='Video style')
    @click.option('--type', 'content_type', 
                  type=click.Choice(['funny', 'highlights', 'all']),
                  default='funny', help='Type of sports content')
    @click.option('--output', '-o', help='Output filename')
    def sports_scraped(duration: int, style: str, content_type: str, output: Optional[str]):
        """⚽ Create sports video from scraped Reddit/social media
        
        Downloads actual sports videos and creates compilation.
        NO VEO generation - only real sports clips!
        """
        
        try:
            output_path = asyncio.run(create_sports_video_from_scraped_media(
                duration_seconds=duration,
                style=style,
                content_type=content_type,
                output_filename=output
            ))
            
            print(f"\n✅ Sports video created: {output_path}")
            print("📸 Used ONLY scraped media - NO AI generation")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise click.ClickException(str(e))
    
    @news.command()
    def examples():
        """📚 Show example commands"""
        examples_text = """
📰 News Aggregator Examples:

🎥 SCRAPED MEDIA COMMANDS (NO VEO - Uses Real Media):
================================================

🔹 NEWS FROM SCRAPED MEDIA:
   # Create news using actual media from Ynet and CNN
   python main.py news scraped https://www.ynet.co.il https://www.cnn.com
   
   # Hebrew news with scraped media (7 minutes)
   python main.py news scraped https://www.ynet.co.il --language he --duration 7
   
   # Tech news using real media from CNN Tech
   python main.py news scraped https://www.cnn.com/tech --type tech --duration 3

🔹 SPORTS FROM SCRAPED MEDIA:
   # Funny sports fails compilation (30 seconds)
   python main.py news sports --type funny --duration 30
   
   # Sports highlights (60 seconds, dramatic style)
   python main.py news sports --type highlights --duration 60 --style dramatic

📺 LEGACY COMMANDS (Uses VEO Generation):
========================================

🔹 YNET.CO.IL NEWS EDITION:
   python main.py news aggregate https://www.ynet.co.il --type general --language he

🔹 CSV INPUT:
   # First create sample CSV files
   python main.py news create-samples
   
   # Then use them to create news editions
   python main.py news csv samples/sample_articles.csv --type general
   python main.py news csv samples/sample_events.csv --type sports --duration 10
   python main.py news csv samples/sample_sources.csv --type tech

🔹 URL SOURCES:
1. Israeli News (with dark humor):
   python main.py news israeli --style dark_humor

2. General News from Multiple Sources:
   python main.py news aggregate https://www.cnn.com https://www.ynet.co.il

3. Tech News Edition:
   python main.py news aggregate https://www.cnn.com/tech https://reddit.com/r/technology --type tech

4. Sports Highlights (10 minutes):
   python main.py news aggregate https://cnn.com/sport --type sports --duration 10

5. Gossip/Entertainment News:
   python main.py news aggregate https://reddit.com/r/entertainment --type gossip --tone entertaining

6. Finance News (Professional):
   python main.py news aggregate https://cnn.com/business --type finance --style professional

7. Telegram Channel News:
   python main.py news aggregate https://t.me/breaking_news_channel

8. Multi-language (Hebrew) from Ynet:
   python main.py news aggregate https://www.ynet.co.il --language he --duration 7

9. Combined Sources with AI Agents:
   python main.py news aggregate https://www.ynet.co.il https://www.cnn.com https://rotter.net/scoopscache.html

10. Sports Event Summary from CSV:
    python main.py news csv sports_events.csv --type sports --visual-style dynamic --tone exciting

🔹 ADVANCED OPTIONS:
   --no-agents    : Disable AI agent discussions
   --no-media     : Don't download/use scraped media
   --output NAME  : Custom output filename
   --duration MIN : Video duration in minutes
"""
        print(examples_text)
    
    return cli_group