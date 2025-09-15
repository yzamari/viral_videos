#!/usr/bin/env python3
"""
Test script for AI Artifact Detection System
Demonstrates the new video quality validation with automatic regeneration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.generators.video_generator import VideoGenerator
from src.agents.ai_artifact_detector import AIArtifactDetector, VideoQualityGatekeeper
from src.utils.session_manager import session_manager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ai_artifact_detection():
    """Test the AI artifact detection system on a generated video"""
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not found in environment")
        return None
    
    # Configure the test video
    config = GeneratedVideoConfig(
        mission="AI Test: Create a professional product demo showing a futuristic smartphone with holographic display, human hands interacting with the device, and text overlays describing features",
        target_platform=Platform.YOUTUBE,
        category=VideoCategory.TECHNOLOGY,
        duration_seconds=15,
        target_audience="Tech enthusiasts and early adopters",
        languages=["en"],
        hook="🔮 Experience the Future of Mobile Technology",
        call_to_action="Pre-order now at future-tech.com",
        visual_style="ultra-modern tech showcase",
        tone="exciting and innovative",
        style="high-tech product demo",
        theme="preset_tech_startup",
        cheap_mode=True,  # Start with cheap mode for faster testing
        use_langgraph=True
    )
    
    # Create session for tracking
    session_id = session_manager.create_session(
        mission=config.mission,
        platform="youtube",
        duration=15,
        category="technology"
    )
    config.session_id = session_id
    
    logger.info("=" * 80)
    logger.info("🔬 AI ARTIFACT DETECTION TEST")
    logger.info("=" * 80)
    logger.info(f"📝 Mission: {config.mission[:100]}...")
    logger.info(f"⏱️ Duration: {config.duration_seconds} seconds")
    logger.info(f"🎯 Focus: Testing for AI artifacts and hallucinations")
    logger.info("=" * 80)
    
    try:
        # Initialize video generator with quality enhancements
        generator = VideoGenerator(
            api_key=api_key,
            use_real_veo2=False,  # Mock VEO for testing
            use_vertex_ai=True,
            enable_quality_enhancement=True,
            quality_preset='professional',
            use_langgraph=True
        )
        
        # Generate the initial video
        logger.info("\n🎬 Generating test video with potential AI artifacts...")
        result = await generator.generate_video(config)
        
        if result and hasattr(result, 'file_path') and result.file_path:
            logger.info(f"✅ Initial video generated: {result.file_path}")
            
            # Initialize AI artifact detector
            logger.info("\n🔍 Initializing AI Artifact Detection System...")
            detector = AIArtifactDetector(
                api_key=api_key,
                enable_gemini_vision=True,
                confidence_threshold=0.7
            )
            
            # Analyze the video for AI artifacts
            logger.info("🎯 Analyzing video for AI artifacts and hallucinations...")
            quality_report = await detector.analyze_video(
                video_path=result.file_path,
                script_segment=config.mission
            )
            
            # Display detailed analysis results
            logger.info("\n" + "=" * 80)
            logger.info("📊 AI ARTIFACT DETECTION REPORT")
            logger.info("=" * 80)
            logger.info(f"🎯 Overall Quality Score: {quality_report.overall_score:.2%}")
            logger.info(f"📈 Confidence Level: {quality_report.confidence:.2%}")
            logger.info(f"⚠️ Artifacts Detected: {len(quality_report.artifacts)}")
            
            if quality_report.artifacts:
                logger.info("\n🚨 Detected AI Artifacts:")
                for artifact in quality_report.artifacts[:5]:  # Show first 5
                    logger.info(f"  • {artifact.type.value}: {artifact.description}")
                    logger.info(f"    - Severity: {artifact.severity}")
                    logger.info(f"    - Confidence: {artifact.confidence:.2%}")
                    if artifact.frame_numbers:
                        logger.info(f"    - Frames: {artifact.frame_numbers[:5]}")
            
            # Frame-level analysis
            if quality_report.frame_analysis:
                logger.info(f"\n📹 Frame Analysis: {len(quality_report.frame_analysis)} frames analyzed")
                problematic_frames = [f for f, score in quality_report.frame_analysis.items() if score < 0.7]
                if problematic_frames:
                    logger.info(f"  ⚠️ Problematic frames: {problematic_frames[:10]}")
            
            # Recommendations
            if quality_report.recommendations:
                logger.info("\n💡 Recommendations:")
                for rec in quality_report.recommendations[:3]:
                    logger.info(f"  • {rec}")
            
            # Test the quality gatekeeper with automatic regeneration
            if quality_report.overall_score < 0.8:
                logger.info("\n🔄 Quality below threshold - Testing automatic regeneration...")
                gatekeeper = VideoQualityGatekeeper(
                    detector=detector,
                    quality_threshold=0.8,
                    max_regeneration_attempts=2
                )
                
                # Define regeneration function
                async def regenerate_clip(attempt: int):
                    logger.info(f"  🎬 Regeneration attempt {attempt}...")
                    # Modify prompt to reduce artifacts
                    improved_config = config
                    improved_config.mission += f" [Quality Enhancement {attempt}: Ensure realistic human anatomy, clear readable text, consistent physics, no morphing or distortions]"
                    return await generator.generate_video(improved_config)
                
                # Validate and potentially regenerate
                final_path, final_report = await gatekeeper.validate_and_regenerate(
                    video_path=result.file_path,
                    generation_func=regenerate_clip,
                    script=config.mission,
                    attempt=1
                )
                
                logger.info(f"\n✅ Final video after quality validation: {final_path}")
                logger.info(f"📊 Final quality score: {final_report.overall_score:.2%}")
            else:
                logger.info(f"\n✅ Video quality acceptable: {quality_report.overall_score:.2%}")
            
            # Save quality report
            session_dir = f"outputs/session_{session_id}"
            report_path = f"{session_dir}/reports/ai_artifact_report.json"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            import json
            with open(report_path, 'w') as f:
                json.dump({
                    'overall_score': quality_report.overall_score,
                    'confidence': quality_report.confidence,
                    'artifacts_count': len(quality_report.artifacts),
                    'artifacts': [
                        {
                            'type': a.type.value,
                            'description': a.description,
                            'severity': a.severity,
                            'confidence': a.confidence
                        }
                        for a in quality_report.artifacts[:10]
                    ],
                    'recommendations': quality_report.recommendations[:5]
                }, f, indent=2)
            
            logger.info(f"\n📁 AI artifact report saved: {report_path}")
            logger.info("=" * 80)
            
            return result.file_path
        else:
            logger.error("❌ Video generation failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error in AI artifact detection test: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main entry point"""
    logger.info("🚀 Starting AI Artifact Detection Test")
    logger.info("🔬 Testing video quality validation and automatic regeneration")
    
    # Run the async function
    result = asyncio.run(test_ai_artifact_detection())
    
    if result:
        logger.info(f"\n✅ Test completed successfully! Video: {result}")
        logger.info("\n🎯 AI Artifact Detection Features Tested:")
        logger.info("  • Anatomical error detection (extra fingers, distorted faces)")
        logger.info("  • Temporal inconsistency detection (morphing, flickering)")
        logger.info("  • Text gibberish detection (malformed letters)")
        logger.info("  • Physics violation detection (impossible shadows)")
        logger.info("  • Pattern repetition detection (AI-generated patterns)")
        logger.info("  • Automatic quality-based regeneration")
        logger.info("  • Gemini Vision API integration")
    else:
        logger.error("\n❌ Test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()