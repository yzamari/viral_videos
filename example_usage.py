#!/usr/bin/env python3
"""
Enhanced Example usage of the viral video generator with custom prompt support
"""
import argparse
from datetime import datetime
from src.scrapers.youtube_scraper import YouTubeScraper
from src.analyzers.video_analyzer import VideoAnalyzer
from src.generators.video_generator import VideoGenerator
from src.models.video_models import Platform, VideoCategory
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_custom_video_config_with_narrative(
        prompt, duration, platform, category, narrative, feeling):
    """Create video config with narrative and feeling parameters"""
    from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory, Narrative, Feeling

    # Convert string values to enums
    platform_enum = Platform(platform)
    category_enum = VideoCategory(category.title())
    narrative_enum = Narrative(narrative)
    feeling_enum = Feeling(feeling)

    config = GeneratedVideoConfig(
        target_platform=platform_enum,
        category=category_enum,
        duration_seconds=duration,
        narrative=narrative_enum,
        feeling=feeling_enum,
        topic=prompt,
        style=f"{feeling} {narrative} content",
        tone=feeling,
        target_audience="social media users",
        hook=f"Get ready for {feeling} content about {prompt}",
        main_content=[
            f"Opening scene introducing {prompt}",
            f"Main content with {narrative} perspective",
            f"Conclusion with {feeling} impact"
        ],
        call_to_action="Follow for more!",
        visual_style=f"{feeling} and engaging",
        color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
        text_overlays=[],
        transitions=["fade", "zoom"],
        background_music_style=f"{feeling} background music",
        voiceover_style=f"{feeling} and {narrative}",
        sound_effects=[],
        inspired_by_videos=[],
        predicted_viral_score=0.75
    )

    return config


def main():
    parser = argparse.ArgumentParser(description='Generate viral videos with narrative and feeling')
    parser.add_argument('--prompt', '-p', help='Custom video prompt/topic')
    parser.add_argument('--duration', '-d', type=int, default=15, help='Video duration in seconds')
    parser.add_argument(
        '--platform',
        choices=[
            'instagram',
            'tiktok',
            'youtube'],
        default='instagram',
        help='Target platform')
    parser.add_argument(
        '--category',
        choices=[
            'lifestyle',
            'entertainment',
            'education'],
        default='lifestyle',
        help='Video category')

    # NEW: Narrative and feeling parameters
    parser.add_argument('--narrative', choices=[
        'pro_american_government', 'pro_soccer', 'against_animal_abuse',
        'pro_environment', 'pro_technology', 'pro_health', 'pro_education',
        'pro_family', 'neutral'
    ], default='neutral', help='Video narrative/viewpoint')

    parser.add_argument('--feeling', choices=[
        'serious', 'funny', 'cynical', 'inspirational', 'dramatic',
        'playful', 'emotional', 'energetic', 'calm'
    ], default='funny', help='Video emotional tone')

    args = parser.parse_args()

    # Load API key
    import os
    from dotenv import load_dotenv
    load_dotenv()

    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not found in environment variables")
        return

    logger.info("🚀 Starting Enhanced Viral Video Generator...")

    if args.prompt:
        logger.info(f"📝 Custom prompt: {args.prompt}")
        logger.info(f"⏱️  Duration: {args.duration} seconds")
        logger.info(f"📱 Platform: {args.platform}")
        logger.info(f"🎯 Category: {args.category}")
        logger.info(f"📖 Narrative: {args.narrative}")
        logger.info(f"🎭 Feeling: {args.feeling}")

        # Generate custom video directly with Vertex AI support
        use_vertex_ai = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'
        generator = VideoGenerator(
            api_key=google_api_key,
            use_real_veo2=not use_vertex_ai,  # Use Google AI Studio if not Vertex AI
            use_vertex_ai=use_vertex_ai,
            vertex_project_id=os.getenv('VERTEX_AI_PROJECT_ID', 'viralgen-464411'),
            vertex_location=os.getenv('VERTEX_AI_LOCATION', 'us-central1'),
            vertex_gcs_bucket=os.getenv('VERTEX_AI_GCS_BUCKET', 'viral-veo2-results')
        )

        # Import the narrative and feeling enums

        # Create enhanced config with narrative and feeling
        config = create_custom_video_config_with_narrative(
            args.prompt, args.duration, args.platform, args.category,
            args.narrative, args.feeling
        )

        logger.info("🎬 Generating custom video...")
        generated_video = generator.generate_video(config)

        logger.info("✅ Custom video generated successfully!")
        logger.info(f"📁 File: {generated_video.file_path}")
        logger.info(f"📏 Size: {generated_video.file_size_mb:.2f} MB")
        logger.info(f"⏱️  Duration: {args.duration} seconds")

        return

    # Original trending analysis workflow
    logger.info("Checking current Google Trends...")

    # Initialize components with Vertex AI support
    youtube_scraper = YouTubeScraper()  # Will use mock mode
    analyzer = VideoAnalyzer(google_api_key)
    use_vertex_ai = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'
    generator = VideoGenerator(
        api_key=google_api_key,
        use_real_veo2=not use_vertex_ai,  # Use Google AI Studio if not Vertex AI
        use_vertex_ai=use_vertex_ai,
        vertex_project_id=os.getenv('VERTEX_AI_PROJECT_ID', 'viralgen-464411'),
        vertex_location=os.getenv('VERTEX_AI_LOCATION', 'us-central1'),
        vertex_gcs_bucket=os.getenv('VERTEX_AI_GCS_BUCKET', 'viral-veo2-results')
    )

    # Get trending data
    trending_data = youtube_scraper.get_trends()
    logger.info(f"Trends data shape: {trending_data.shape}")

    # Scrape trending videos
    logger.info("\nScraping trending YouTube videos...")
    videos = youtube_scraper.scrape_trending_videos(limit=4)
    logger.info(f"Found {len(videos)} trending videos")

    for i, video in enumerate(videos, 1):
        logger.info(f"{i}. {video.title[:50]}...")
        logger.info(f"   Views: {video.view_count:,} | Engagement: {video.engagement_rate:.2f}%")

    # Analyze viral patterns
    logger.info("\nAnalyzing viral patterns...")
    analyses = [analyzer.analyze_video(video) for video in videos]

    # Calculate insights
    avg_viral_score = sum(a.viral_score for a in analyses) / len(analyses)
    all_themes = [theme for a in analyses for theme in a.content_themes]
    top_themes = list(set(all_themes))[:3]

    logger.info(f"Average viral score: {avg_viral_score:.2f}")
    logger.info(f"Top themes: {top_themes}")

    # Save trending analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    analysis_file = f"outputs/trending_analysis_{timestamp}.txt"

    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write("🔥 TRENDING VIDEO ANALYSIS\n")
        f.write("=" * 50 + "\n\n")

        for i, (video, analysis) in enumerate(zip(videos, analyses), 1):
            f.write(f"{i}. {video.title}\n")
            f.write(f"   🔗 {video.url}\n")
            f.write(f"   👀 Views: {video.view_count:,}\n")
            f.write(f"   ❤️  Likes: {video.like_count:,}\n")
            f.write(f"   🚀 Viral Score: {analysis.viral_score:.2f}\n")
            f.write(f"   🎯 Themes: {', '.join(analysis.content_themes[:3])}\n")
            f.write(f"   💡 Success Factors: {', '.join(analysis.success_factors[:2])}\n\n")

        f.write("📊 INSIGHTS:\n")
        f.write(f"   • Average viral score: {avg_viral_score:.2f}\n")
        f.write(f"   • Top themes: {', '.join(top_themes)}\n")
        f.write(f"   • Total videos analyzed: {len(videos)}\n")

    logger.info(f"📊 Trending analysis saved to: {analysis_file}")

    # Display beautiful console output
    logger.info("\n" + "=" * 60)
    logger.info("🔥 TOP TRENDING VIDEOS ANALYZED:")
    logger.info("=" * 60)

    for i, (video, analysis) in enumerate(zip(videos, analyses), 1):
        logger.info(f"\n{i}. {video.title[:50]}...")
        logger.info(f"   🔗 {video.url}")
        logger.info(f"   👀 Views: {video.view_count:,}")
        logger.info(f"   ❤️  Likes: {video.like_count:,}")
        logger.info(f"   🚀 Viral Score: {analysis.viral_score:.2f}")

    logger.info("\n🎯 Key Insights:")
    logger.info(f"   • Average viral score: {avg_viral_score:.2f}")
    logger.info(f"   • Top themes: {', '.join(top_themes)}")
    logger.info("=" * 60)

    # Generate video configuration
    logger.info("\nGenerating video configuration...")
    config = generator.generate_video_config(
        analyses=analyses,
        platform=Platform.INSTAGRAM,
        category=VideoCategory.LIFESTYLE,
        topic=None  # Let AI decide based on trends
    )

    logger.info("Generated config:")
    logger.info(f"  Topic: {config.topic}")
    logger.info(f"  Style: {config.style}")
    logger.info(f"  Hook: {config.hook[:100]}...")
    logger.info(f"  Predicted viral score: {config.predicted_viral_score:.2f}")

    # Generate the video
    logger.info("\nGenerating video (this may take a few minutes)...")
    generated_video = generator.generate_video(config)

    logger.info("\n✅ Video generated successfully!")
    logger.info(f"  File: {generated_video.file_path}")
    logger.info(f"  Size: {generated_video.file_size_mb:.2f} MB")
    logger.info(f"  Duration: {config.duration_seconds} seconds")
    logger.info(f"  Generation time: {generated_video.generation_time_seconds:.1f} seconds")

    logger.info("\nScript preview:")
    logger.info(generated_video.script[:200] + "...")

    # Search for similar videos for comparison
    logger.info("\nSearching for similar videos to compare...")
    try:
        similar_videos = youtube_scraper.search_videos(config.topic, max_results=3)
        if similar_videos:
            logger.info("Found similar videos:")
            for vid in similar_videos:
                logger.info(f"  - {vid.title[:50]}... ({vid.view_count:,} views)")
    except Exception as e:
        logger.error(f"Error searching videos: {e}")


if __name__ == "__main__":
    main()
