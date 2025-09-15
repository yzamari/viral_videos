#!/usr/bin/env python3
"""
Generate Hollywood-Level 5-Minute Movie
Optimized for laptop execution with Google AI tools
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.laptop_hollywood_pipeline_fixed import LaptopHollywoodPipeline
from src.utils.session_context import SessionContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hollywood_generation.log')
    ]
)
logger = logging.getLogger(__name__)


def generate_hollywood_movie(
    concept: str,
    genre: str = "drama",
    style: str = "cinematic",
    test_mode: bool = False,
    use_cache: bool = True
):
    """
    Generate a Hollywood-quality 5-minute movie
    
    Args:
        concept: Movie concept/story idea
        genre: Movie genre (drama, action, sci-fi, comedy, thriller)
        style: Visual style (cinematic, noir, vibrant, documentary)
        test_mode: Run in test mode with minimal resources
        use_cache: Use cached assets when available
    """
    
    print("\n" + "="*60)
    print("🎬 HOLLYWOOD MOVIE GENERATOR - LAPTOP EDITION")
    print("="*60)
    print(f"📝 Concept: {concept}")
    print(f"🎭 Genre: {genre}")
    print(f"🎨 Style: {style}")
    print(f"💻 Mode: {'Test' if test_mode else 'Production'}")
    print(f"💾 Cache: {'Enabled' if use_cache else 'Disabled'}")
    print("="*60 + "\n")
    
    # Initialize pipeline
    pipeline = LaptopHollywoodPipeline(
        project_id="viralgen-464411",
        gcp_email="admin@al-ai.net"
    )
    
    # Configure for laptop optimization
    if not test_mode:
        pipeline.config.max_parallel_veo_calls = 2
        pipeline.config.veo_batch_size = 5
        pipeline.config.use_imagen4_fast = True
        pipeline.config.enable_aggressive_caching = use_cache
    
    try:
        # Setup GCP authentication
        print("🔐 Setting up GCP authentication...")
        pipeline.setup_gcp_auth()
        
        # Generate movie
        print("\n🎬 Starting movie generation...")
        print("⏱️  This will take approximately:")
        if test_mode:
            print("   - Test mode: 2-5 minutes")
        else:
            print("   - Full movie: 30-45 minutes on laptop")
            print("   - API calls will be throttled to avoid quota issues")
        
        movie_path = pipeline.generate_5_minute_movie(
            concept=concept,
            genre=genre,
            style=style,
            test_mode=test_mode
        )
        
        print("\n" + "="*60)
        print("✅ MOVIE GENERATION COMPLETE!")
        print("="*60)
        print(f"📁 Output: {movie_path}")
        print(f"🎬 Duration: {'30 seconds' if test_mode else '5 minutes'}")
        
        # Display file info
        if os.path.exists(movie_path):
            size_mb = os.path.getsize(movie_path) / (1024 * 1024)
            print(f"📦 File size: {size_mb:.1f} MB")
        
        print("\n💡 Next steps:")
        print("   1. Review the generated movie")
        print("   2. Upload to YouTube/social media")
        print("   3. Iterate on concept and style")
        print("="*60 + "\n")
        
        return movie_path
        
    except Exception as e:
        logger.error(f"Movie generation failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check GCP credentials and project")
        print("   2. Ensure APIs are enabled (VEO, Imagen, Gemini)")
        print("   3. Check API quotas")
        print("   4. Try test mode first: --test")
        raise


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Generate Hollywood-quality 5-minute movies with Google AI"
    )
    
    parser.add_argument(
        "concept",
        nargs="?",
        default=None,
        help="Movie concept or story idea (e.g., 'AI discovers love')"
    )
    
    parser.add_argument(
        "--genre",
        default="drama",
        choices=["drama", "action", "sci-fi", "comedy", "thriller", "romance"],
        help="Movie genre (default: drama)"
    )
    
    parser.add_argument(
        "--style",
        default="cinematic",
        choices=["cinematic", "noir", "vibrant", "documentary", "artistic"],
        help="Visual style (default: cinematic)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (30 seconds, minimal resources)"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (regenerate all assets)"
    )
    
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Show example commands"
    )
    
    args = parser.parse_args()
    
    if args.examples:
        print("\n📚 EXAMPLE COMMANDS:\n")
        print("# Quick test (30 seconds):")
        print("python generate_hollywood_movie.py 'Robot learns to paint' --test\n")
        
        print("# Sci-fi action movie:")
        print("python generate_hollywood_movie.py 'Time travelers save Earth' --genre sci-fi --style vibrant\n")
        
        print("# Romantic comedy:")
        print("python generate_hollywood_movie.py 'AI matchmaker gone wrong' --genre comedy --style cinematic\n")
        
        print("# Film noir thriller:")
        print("python generate_hollywood_movie.py 'Detective in digital world' --genre thriller --style noir\n")
        
        print("# Full production without cache:")
        print("python generate_hollywood_movie.py 'Epic space adventure' --no-cache\n")
        
        sys.exit(0)
    
    # Check concept is provided
    if not args.concept:
        parser.error("concept argument is required unless using --examples")
    
    # Run movie generation
    generate_hollywood_movie(
        concept=args.concept,
        genre=args.genre,
        style=args.style,
        test_mode=args.test,
        use_cache=not args.no_cache
    )


if __name__ == "__main__":
    main()