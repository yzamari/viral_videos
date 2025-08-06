"""CLI integration for news aggregator"""

import click
import asyncio
from pathlib import Path
from typing import List, Optional

# Lazy imports to avoid circular dependencies
# from .israeli_news_generator import generate_israeli_news
# from .aggregator import create_news_edition
# from .mock_aggregator import create_mock_news_edition
# from .aggregator_scraped_media import create_scraped_media_news_edition
# from .commands.sports_command import create_sports_video_from_scraped_media
# from .aggregator_v2 import create_news_edition_from_csv, create_news_edition_from_sources
# from .parsers.csv_parser import NewsCSVParser


def add_news_commands(cli_group):
    """Add news aggregator commands to CLI"""
    
    @cli_group.group()
    def news():
        """📰 News aggregation and video generation commands"""
        pass
    
    @news.command('aggregate-enhanced')
    @click.argument('sources', nargs=-1, required=True)
    @click.option('--csv', type=click.Path(exists=True), help='CSV file with additional news items')
    @click.option('--languages', '-l', multiple=True, default=['en'], 
                  help='Output languages (e.g., -l en -l he -l ru). Creates one video per language.')
    @click.option('--style', '-s', default='professional', 
                  help='Free-form style description (AI will interpret)')
    @click.option('--tone', '-t', default='informative',
                  help='Free-form tone description (AI will interpret)')
    @click.option('--platform', '-p', type=click.Choice(['youtube', 'tiktok', 'instagram', 'twitter']),
                  default='youtube', help='Target platform for formatting')
    @click.option('--duration', '-d', type=int, default=60,
                  help='Duration in seconds per video')
    @click.option('--max-stories', '-m', type=int, default=10,
                  help='Maximum number of stories to include')
    @click.option('--ai-discussion/--no-ai-discussion', default=True,
                  help='Enable AI agent discussions for content selection')
    @click.option('--discussion-log', is_flag=True,
                  help='Show detailed AI discussion log')
    @click.option('--overlay-style', type=click.Choice(['modern', 'classic', 'minimal']),
                  default='modern', help='Overlay visual style')
    @click.option('--output-dir', '-o', default='outputs/news',
                  help='Output directory for videos')
    @click.option('--hours-back', type=int, default=24,
                  help='Number of hours back to scrape news (default: 24)')
    @click.option('--telegram-channels', '-tc', multiple=True,
                  help='Telegram channels to scrape (e.g., -tc @ynet_news -tc @channel13news)')
    @click.option('--use-youtube-videos', is_flag=True,
                  help='Search and use YouTube videos for news stories')
    @click.option('--logo-path', type=click.Path(exists=True),
                  help='Path to logo PNG file for overlay')
    @click.option('--channel-name', default='NEWS',
                  help='News channel name for header (default: NEWS)')
    @click.option('--dynamic-transitions', is_flag=True, default=True,
                  help='Enable dynamic transitions between media (split-screen, mosaic, etc.)')
    def aggregate_enhanced(sources, csv, languages, style, tone, platform, duration,
                          max_stories, ai_discussion, discussion_log, overlay_style, output_dir,
                          hours_back, telegram_channels, use_youtube_videos, logo_path, 
                          channel_name, dynamic_transitions):
        """🌐 Enhanced news aggregator with all features
        
        Examples:
            # Basic usage with multiple sources
            python main.py news aggregate-enhanced https://ynet.co.il https://rotter.net https://i24news.tv
            
            # Multi-language output (creates 3 videos)
            python main.py news aggregate-enhanced ynet rotter cnn -l he -l ru -l en
            
            # With CSV file containing additional items
            python main.py news aggregate-enhanced ynet rotter --csv my_news.csv -l he -l ar
            
            # Custom style and tone (AI interprets)
            python main.py news aggregate-enhanced ynet cnn --style "viral and energetic" --tone "humorous but respectful"
            
            # Platform-specific with AI discussions
            python main.py news aggregate-enhanced ynet rotter i24 --platform tiktok --discussion-log
            
            # Full example
            python main.py news aggregate-enhanced ynet rotter cnn i24 \\
                --csv extra_news.csv \\
                --languages he --languages ru --languages en \\
                --style "modern and dynamic" \\
                --tone "engaging and informative" \\
                --platform youtube \\
                --duration 90 \\
                --max-stories 15 \\
                --discussion-log \\
                --overlay-style modern
        
        Sources can be:
            - Full URLs: Any website URL (e.g., https://example.com/news)
            - Source names: Any source with a .json config file in scraper_configs/
            - Telegram channels: Use --telegram-channels flag
            - Instagram profiles: Direct profile URLs
            
        Configuration:
            Add .json files to scraper_configs/ directory to configure new sources.
            Examples available in example_scraper_configs/
            
        CSV format can be:
            - Simple list: One news item per line
            - Structured: title,content,url,source,image_url,video_url,priority
        """
        
        print(f"🌐 Enhanced News Aggregator")
        print(f"📰 Sources: {', '.join(sources)}")
        print(f"📺 Channel Name (from CLI): {channel_name}")
        if csv:
            print(f"📄 CSV: {csv}")
        print(f"🌍 Languages: {', '.join(languages)}")
        print(f"🎨 Style: {style}")
        print(f"🎭 Tone: {tone}")
        print(f"📱 Platform: {platform}")
        print(f"⏱️  Duration: {duration}s per video")
        print(f"📊 Max stories: {max_stories}")
        print(f"🤖 AI discussions: {'Enabled' if ai_discussion else 'Disabled'}")
        if hours_back != 24:
            print(f"⏰ Hours back: {hours_back}")
        if telegram_channels:
            print(f"📱 Telegram channels: {', '.join(telegram_channels)}")
        
        try:
            from .enhanced_aggregator import create_enhanced_news_edition
            
            output_videos = asyncio.run(create_enhanced_news_edition(
                sources=list(sources),
                csv_file=csv,
                languages=list(languages),
                style=style,
                tone=tone,
                platform=platform,
                duration_seconds=duration,
                max_stories=max_stories,
                enable_ai_discussion=ai_discussion,
                discussion_log=discussion_log,
                overlay_style=overlay_style,
                output_dir=output_dir,
                hours_back=hours_back,
                telegram_channels=list(telegram_channels),
                use_youtube_videos=use_youtube_videos,
                logo_path=logo_path,
                channel_name=channel_name,
                dynamic_transitions=dynamic_transitions
            ))
            
            print("\n✅ News videos created:")
            for lang, path in output_videos.items():
                print(f"   {lang}: {path}")
            
            print(f"\n📊 Total videos created: {len(output_videos)}")
            print("📸 All videos use ONLY scraped media - NO AI generation")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise click.ClickException(str(e))
    
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
            # Lazy import to avoid circular dependencies
            from .israeli_news_generator import generate_israeli_news
            
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
            # Use real scraper instead of mock
            from .aggregator_scraped_media import create_scraped_media_news_edition
            
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
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise click.ClickException(str(e))
    
    # Note: The csv command is now implemented below as 'csv-input'
    
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
            # Lazy import to avoid circular dependencies
            from .aggregator_scraped_media import create_scraped_media_news_edition
            
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
            # Lazy import to avoid circular dependencies
            from .commands.sports_command import create_sports_video_from_scraped_media
            
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
    
    @news.command('hebrew-multi')
    @click.option('--duration', '-d', type=int, default=60,
                  help='Video duration in seconds (default: 60)')
    @click.option('--stories', '-s', type=int, default=8,
                  help='Maximum number of stories (default: 8)')
    @click.option('--output', '-o', help='Output filename')
    @click.option('--sources', multiple=True, 
                  default=['ynet', 'rotter', 'bbc'],
                  help='Sources to include (default: ynet rotter bbc)')
    def hebrew_multi_source(duration: int, stories: int, output: Optional[str], sources: tuple):
        """🇮🇱 Create Hebrew news from Ynet, Rotter, and BBC
        
        Aggregates news from multiple Israeli and international sources,
        downloads actual media, and creates a professional Hebrew news video.
        
        Examples:
            # Default: 60-second video from all sources
            python main.py news hebrew-multi
            
            # 30-second quick news
            python main.py news hebrew-multi --duration 30 --stories 5
            
            # Only from Ynet and Rotter
            python main.py news hebrew-multi --sources ynet --sources rotter
        """
        
        print("🇮🇱 Creating Hebrew news from multiple sources...")
        print(f"📰 Sources: {', '.join(sources)}")
        print(f"⏱️  Duration: {duration} seconds")
        print(f"📊 Max stories: {stories}")
        
        try:
            # Import the multi-source aggregator
            import sys
            sys.path.append('.')
            from multi_source_hebrew_news import HebrewMultiSourceNews
            
            aggregator = HebrewMultiSourceNews()
            
            # Filter sources based on user selection
            if 'ynet' not in sources:
                aggregator.scraper.configs.pop('ynet', None)
            if 'rotter' not in sources:
                aggregator.scraper.configs.pop('rotter', None)
            if 'bbc' not in sources:
                aggregator.scraper.configs.pop('bbc_hebrew', None)
            
            output_path = asyncio.run(aggregator.aggregate_hebrew_news(
                duration_seconds=duration,
                max_stories=stories
            ))
            
            if output:
                import shutil
                shutil.move(output_path, output)
                output_path = output
            
            print(f"\n✅ Hebrew news video created: {output_path}")
            print("📸 Used real scraped media from news sources")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise click.ClickException(str(e))
    
    @news.command('csv')
    @click.argument('csv_file', type=click.Path(exists=True))
    @click.option('--duration', '-d', type=int, default=60,
                  help='Video duration in seconds (default: 60)')
    @click.option('--language', '-l', default='he',
                  help='Language code (default: he)')
    @click.option('--style', type=click.Choice(['professional', 'casual', 'dramatic']),
                  default='professional', help='Visual style')
    @click.option('--platform', '-p', type=click.Choice(['tiktok', 'instagram', 'youtube', 'twitter', 'general']),
                  default='general', help='Target platform (affects format, pacing, style)')
    @click.option('--output', '-o', help='Output filename')
    def csv_input(csv_file: str, duration: int, language: str, style: str, platform: str, output: Optional[str]):
        """📄 Create news from CSV file with flexible format
        
        CSV can contain any combination of:
        - title (required): Article headline
        - content/description: Article text
        - source: Source name/website
        - url: Article URL (will scrape if no content)
        - image_url/image: Direct image URL
        - video_url/video: Direct video URL
        - category: Category/type
        - priority: 1-10 importance
        - date: Publication date
        - author: Author name
        - language: Language code
        
        Examples:
            # Basic usage
            python main.py news csv my_articles.csv
            
            # 30-second English news
            python main.py news csv articles.csv --duration 30 --language en
            
            # Custom output
            python main.py news csv news.csv --output custom_news.mp4
        """
        
        print(f"📄 Creating news from CSV: {csv_file}")
        print(f"⏱️  Duration: {duration} seconds")
        print(f"🌐 Language: {language}")
        print(f"📱 Platform: {platform}")
        
        try:
            import sys
            sys.path.append('.')
            from csv_news_aggregator import CSVNewsAggregator
            
            aggregator = CSVNewsAggregator()
            output_path = asyncio.run(aggregator.create_news_from_csv(
                csv_file,
                duration_seconds=duration,
                language=language,
                style=style,
                platform=platform,
                output_filename=output
            ))
            
            print(f"\n✅ News video created: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise click.ClickException(str(e))
    
    @news.command('create-csv-sample')
    @click.option('--output', '-o', default='sample_news.csv',
                  help='Output filename (default: sample_news.csv)')
    def create_csv_sample(output: str):
        """📝 Create a sample CSV file for news aggregation
        
        Creates a sample CSV with various article types showing
        all supported columns and formats.
        """
        
        try:
            import sys
            sys.path.append('.')
            from csv_news_aggregator import create_sample_csv
            
            create_sample_csv(output)
            print(f"\n✅ Sample CSV created: {output}")
            print("\nYou can now use it with:")
            print(f"  python main.py news csv {output}")
            
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

🇮🇱 HEBREW MULTI-SOURCE NEWS (NEW!):
   # Create Hebrew news from Ynet, Rotter, and BBC (60 seconds)
   python main.py news hebrew-multi
   
   # Quick 30-second Hebrew news with 5 stories
   python main.py news hebrew-multi --duration 30 --stories 5
   
   # Hebrew news from specific sources only
   python main.py news hebrew-multi --sources ynet --sources rotter
   
   # 90-second extended Hebrew news edition
   python main.py news hebrew-multi --duration 90 --stories 12

📄 CSV-BASED NEWS (FLEXIBLE INPUT):
   # First, create a sample CSV to see the format
   python main.py news create-csv-sample
   
   # Create news from your CSV file
   python main.py news csv my_articles.csv
   
   # 30-second news in English from CSV
   python main.py news csv articles.csv --duration 30 --language en
   
   # Hebrew news with custom output
   python main.py news csv hebrew_news.csv --language he --output today_news.mp4
   
   # CSV supports: URLs to scrape, direct content, image/video links, priorities

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