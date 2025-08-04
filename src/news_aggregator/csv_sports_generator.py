"""CSV-based Sports Video Generator - Uses scraped media only"""

import csv
import asyncio
import os
from typing import List, Dict, Any
from datetime import datetime

from ..utils.logging_config import get_logger
from .models.content_models import ContentItem, MediaAsset, AssetType, NewsSource, SourceType
from .processors.media_downloader import MediaDownloader
from .composers.scraped_media_composer import create_scraped_media_video

logger = get_logger(__name__)


async def create_sports_video_from_csv(csv_path: str, duration_seconds: int = 30, style: str = "fast-paced") -> str:
    """Create sports video from CSV file containing media URLs"""
    
    logger.info(f"📄 Reading sports content from CSV: {csv_path}")
    logger.info("📸 Using SCRAPED MEDIA ONLY - NO VEO GENERATION")
    
    # 1. Parse CSV file
    content_items = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Create media asset
            media_type = row.get('type', 'video')
            media_asset = MediaAsset(
                id=f"csv_{len(content_items)}",
                asset_type=AssetType.VIDEO if media_type == 'video' else AssetType.IMAGE,
                source_url=row['media_url'],
                duration=float(row.get('duration', 0)) if media_type == 'video' else None
            )
            
            # Create content item
            source = NewsSource(
                id="csv_sports",
                name="Sports CSV",
                source_type=SourceType.CSV,
                url=csv_path
            )
            
            # Parse tags
            tags = [tag.strip() for tag in row.get('tags', '').split(',')]
            
            content = ContentItem(
                id=f"csv_item_{len(content_items)}",
                source=source,
                title=row['title'],
                content=row.get('description', row['title']),
                url=row.get('url', ''),
                media_assets=[media_asset],
                tags=tags,
                categories=['sports'],
                relevance_score=0.9 if 'funny' in tags else 0.8
            )
            
            content_items.append(content)
    
    logger.info(f"✅ Loaded {len(content_items)} sports items from CSV")
    
    # 2. Show what we found
    logger.info("📋 Sports content loaded:")
    for i, item in enumerate(content_items[:5]):
        logger.info(f"   {i+1}. {item.title} ({item.media_assets[0].asset_type.value})")
    
    # 3. Create video from scraped media
    logger.info("🎬 Creating video from scraped media...")
    output_path = await create_scraped_media_video(
        content_items=content_items,
        duration_seconds=duration_seconds,
        style=style
    )
    
    return output_path


def create_sample_sports_csv(output_path: str = "sample_sports.csv"):
    """Create a sample CSV file for sports content"""
    
    sample_data = [
        {
            "title": "Epic Soccer Goal Fail",
            "url": "https://reddit.com/r/sportsfails/example1",
            "media_url": "https://v.redd.it/soccerfail123.mp4",
            "type": "video",
            "tags": "funny,fails,soccer",
            "duration": "15",
            "description": "Player attempts bicycle kick, hits referee instead"
        },
        {
            "title": "Basketball Trick Shot Gone Wrong",
            "url": "https://reddit.com/r/nba/example2",
            "media_url": "https://v.redd.it/basketballfail456.mp4",
            "type": "video",
            "tags": "funny,fails,basketball,nba",
            "duration": "12",
            "description": "Half-court shot attempt ends in embarrassment"
        },
        {
            "title": "Golf Cart Disaster",
            "url": "https://reddit.com/r/golf/example3",
            "media_url": "https://i.imgur.com/golfcart789.jpg",
            "type": "image",
            "tags": "funny,golf,fails",
            "duration": "5",
            "description": "Golf cart ends up in water hazard"
        },
        {
            "title": "Tennis Serve Mishap",
            "url": "https://reddit.com/r/tennis/example4",
            "media_url": "https://gfycat.com/tennisfail.mp4",
            "type": "video",
            "tags": "funny,tennis,fails",
            "duration": "8",
            "description": "Professional player's serve hits ball boy"
        },
        {
            "title": "Football Celebration Fail",
            "url": "https://reddit.com/r/nfl/example5",
            "media_url": "https://streamable.com/footballfail.mp4",
            "type": "video",
            "tags": "funny,football,nfl,celebration",
            "duration": "10",
            "description": "Touchdown celebration goes hilariously wrong"
        }
    ]
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['title', 'url', 'media_url', 'type', 'tags', 'duration', 'description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(sample_data)
    
    logger.info(f"✅ Created sample sports CSV: {output_path}")
    return output_path


# CLI function
async def sports_csv_command(csv_path: str, duration: int = 30, style: str = "fast-paced"):
    """Command to create sports video from CSV"""
    
    try:
        # Check if CSV exists
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            logger.info("Creating sample CSV for you...")
            csv_path = create_sample_sports_csv()
            logger.info(f"Please edit {csv_path} with your media URLs and run again")
            return
        
        # Create video
        output_path = await create_sports_video_from_csv(csv_path, duration, style)
        
        logger.info(f"\n✅ Sports video created: {output_path}")
        logger.info("📸 Used ONLY media from CSV - NO AI generation")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create sports video: {str(e)}")
        raise