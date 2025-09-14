#!/usr/bin/env python3
"""
Test script for generating a state-of-the-art 30-second Hebrew commercial for chess classes.
This demonstrates the new LangGraph quality monitoring system with all enhancements active.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.generators.video_generator import VideoGenerator
from src.utils.session_manager import session_manager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_hebrew_chess_commercial():
    """Create a professional 30-second Hebrew commercial for chess classes"""
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not found in environment")
        return None
    
    # Configure the commercial
    config = GeneratedVideoConfig(
        mission="חוג שחמט קהילתי - לימוד אסטרטגיה וחשיבה מתקדמת לילדים ומבוגרים. הצטרפו לחוג השחמט המוביל בעיר! פיתוח חשיבה לוגית, שיפור ריכוז, ובניית ביטחון עצמי. מתאים לכל הגילאים - מתחילים עד מתקדמים. מדריכים מוסמכים, אווירה חמה ותומכת. ההרשמה פתוחה עכשיו!",
        target_platform=Platform.YOUTUBE,
        category=VideoCategory.EDUCATION,
        duration_seconds=30,
        target_audience="הורים וילדים בקהילה המקומית",
        languages=["he"],  # Hebrew
        hook="🏆 גלה את עולם השחמט - המשחק שמפתח את המוח! ♟️",
        call_to_action="הירשמו עכשיו ותקבלו שיעור ניסיון חינם! 📞 055-CHESS-NOW",
        visual_style="professional educational",
        tone="inspiring and welcoming",
        style="modern community center promotional video",
        theme="preset_education_teaching",  # Use education theme
        cheap_mode=False,  # Full quality mode
        use_langgraph=True  # Use new LangGraph system
    )
    
    # Create session for tracking
    session_id = session_manager.create_session(
        mission=config.mission,
        platform="youtube",
        duration=30,
        category="education"
    )
    config.session_id = session_id
    
    logger.info("=" * 80)
    logger.info("🎬 CREATING HEBREW CHESS COMMERCIAL")
    logger.info("=" * 80)
    logger.info(f"📝 Mission: {config.mission[:100]}...")
    logger.info(f"⏱️ Duration: {config.duration_seconds} seconds")
    logger.info(f"🌍 Language: Hebrew")
    logger.info(f"🎯 Target: {config.target_audience}")
    logger.info(f"🎨 Style: {config.visual_style}")
    logger.info(f"🚀 Quality: Professional (LangGraph monitoring active)")
    logger.info("=" * 80)
    
    try:
        # Initialize video generator with all quality enhancements
        generator = VideoGenerator(
            api_key=api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            enable_quality_enhancement=True,
            quality_preset='professional',  # Use professional quality preset
            use_langgraph=True  # Enable LangGraph monitoring
        )
        
        # Generate the commercial
        logger.info("\n🎬 Starting video generation with LangGraph quality monitoring...")
        result = await generator.generate_video(config)
        
        if result and hasattr(result, 'file_path') and result.file_path:
            logger.info("\n" + "=" * 80)
            logger.info("✅ COMMERCIAL GENERATION COMPLETE!")
            logger.info("=" * 80)
            logger.info(f"📹 Video: {result.file_path}")
            logger.info(f"📊 Size: {result.file_size_mb:.2f} MB")
            logger.info(f"⏱️ Generation time: {result.generation_time_seconds:.1f} seconds")
            logger.info(f"🎬 Clips generated: {result.clips_generated}")
            logger.info(f"🎵 Audio files: {len(result.audio_files)}")
            
            # Check for quality report
            session_dir = f"outputs/session_{session_id}"
            quality_report_path = f"{session_dir}/reports/quality_report.json"
            if os.path.exists(quality_report_path):
                logger.info(f"📊 Quality report: {quality_report_path}")
                
                # Read and display key metrics
                import json
                with open(quality_report_path, 'r') as f:
                    report = json.load(f)
                    if 'overall_score' in report:
                        logger.info(f"🎯 Overall quality score: {report['overall_score']:.2%}")
                    if 'steps' in report:
                        logger.info("📈 Step-by-step quality scores:")
                        for step, data in report['steps'].items():
                            if 'score' in data:
                                logger.info(f"  - {step}: {data['score']:.2%}")
            
            logger.info("\n🎉 Hebrew chess commercial created successfully!")
            logger.info(f"📁 Session directory: {session_dir}")
            logger.info("=" * 80)
            
            return result.file_path
        else:
            logger.error("❌ Video generation failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error creating commercial: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main entry point"""
    logger.info("🚀 Starting Hebrew Chess Commercial Generator")
    logger.info("📦 Using LangGraph Quality Monitoring System")
    
    # Run the async function
    result = asyncio.run(create_hebrew_chess_commercial())
    
    if result:
        logger.info(f"\n✅ Success! Video saved at: {result}")
        logger.info("\n💡 The video includes:")
        logger.info("  • Professional Hebrew narration")
        logger.info("  • Synchronized Hebrew subtitles")
        logger.info("  • Chess-themed visuals")
        logger.info("  • Educational overlays")
        logger.info("  • Community-focused messaging")
        logger.info("  • Professional quality transitions")
        logger.info("  • LangGraph quality validation at each step")
    else:
        logger.error("\n❌ Failed to create commercial")
        sys.exit(1)

if __name__ == "__main__":
    main()