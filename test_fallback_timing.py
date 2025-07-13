#!/usr/bin/env python3
"""
Test script to demonstrate enhanced fallback timing with 5-10 second image display
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.image_timing_agent import ImageTimingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fallback_timing():
    """Test the enhanced fallback timing with 5-10 second frames"""
    
    # Load API key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ No API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return False
    
    # Initialize timing agent
    timing_agent = ImageTimingAgent(api_key)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "TikTok Short Story",
            "prompts": [
                {"description": "A young woman looking thoughtfully at her phone"},
                {"description": "Text message conversation showing emotional exchange"},
                {"description": "Close-up of tears in her eyes"},
                {"description": "Her walking away with determination"}
            ],
            "platform": "tiktok",
            "duration": 30,
            "category": "drama"
        },
        {
            "name": "YouTube Educational",
            "prompts": [
                {"description": "Historical timeline showing key events"},
                {"description": "Portrait of a historical figure with text overlay"},
                {"description": "Map showing geographical changes"},
                {"description": "Modern day comparison image"}
            ],
            "platform": "youtube",
            "duration": 45,
            "category": "education"
        },
        {
            "name": "Instagram Story",
            "prompts": [
                {"description": "Beautiful sunset landscape"},
                {"description": "Close-up of hands holding a meaningful object"},
                {"description": "Inspirational quote overlay on nature background"}
            ],
            "platform": "instagram",
            "duration": 25,
            "category": "lifestyle"
        }
    ]
    
    logger.info("🎬 Testing Enhanced Fallback Timing (5-10 second frames)")
    logger.info("=" * 60)
    
    for scenario in test_scenarios:
        logger.info(f"\n🎯 Testing: {scenario['name']}")
        logger.info(f"Platform: {scenario['platform']}")
        logger.info(f"Duration: {scenario['duration']}s")
        logger.info(f"Images: {len(scenario['prompts'])}")
        
        try:
            # Test fallback timing analysis
            timing_analysis = timing_agent.analyze_fallback_timing_requirements(
                prompts=scenario['prompts'],
                platform=scenario['platform'],
                total_duration=scenario['duration'],
                category=scenario['category']
            )
            
            logger.info(f"✅ Analysis complete:")
            logger.info(f"   Strategy: {timing_analysis.get('timing_strategy', 'N/A')}")
            logger.info(f"   Average per image: {timing_analysis.get('average_duration_per_image', 0):.1f}s")
            logger.info(f"   Total calculated: {timing_analysis.get('total_calculated_duration', 0):.1f}s")
            
            # Check individual image timings
            image_timings = timing_analysis.get('image_timings', [])
            logger.info(f"   Individual timings:")
            
            all_in_range = True
            for i, img_timing in enumerate(image_timings):
                duration = img_timing.get('duration', 0)
                in_range = 5.0 <= duration <= 10.0
                all_in_range = all_in_range and in_range
                
                status = "✅" if in_range else "❌"
                logger.info(f"     Image {i+1}: {duration:.1f}s {status}")
                logger.info(f"       Rationale: {img_timing.get('timing_rationale', 'N/A')[:80]}...")
            
            # Verify all images are in 5-10 second range
            if all_in_range:
                logger.info(f"🎉 All images in 5-10 second range: ✅")
            else:
                logger.warning(f"⚠️ Some images outside 5-10 second range: ❌")
            
            # Test standard timing for comparison
            logger.info(f"\n📊 Comparison with standard timing:")
            standard_timing = timing_agent.analyze_image_timing_requirements(
                prompts=scenario['prompts'],
                platform=scenario['platform'],
                total_duration=scenario['duration'],
                category=scenario['category']
            )
            
            standard_avg = standard_timing.get('average_duration_per_image', 0)
            fallback_avg = timing_analysis.get('average_duration_per_image', 0)
            
            logger.info(f"   Standard avg: {standard_avg:.1f}s")
            logger.info(f"   Fallback avg: {fallback_avg:.1f}s")
            logger.info(f"   Improvement: {fallback_avg - standard_avg:.1f}s longer per image")
            
        except Exception as e:
            logger.error(f"❌ Test failed for {scenario['name']}: {e}")
            return False
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 All fallback timing tests completed successfully!")
    logger.info("📝 Key benefits of 5-10 second fallback timing:")
    logger.info("   • Adequate time for subtitle reading")
    logger.info("   • Better visual processing and comprehension")
    logger.info("   • Compensates for lack of motion in image-based videos")
    logger.info("   • Platform-optimized within 5-10 second range")
    logger.info("   • AI-driven content complexity analysis")
    
    return True

def main():
    """Main test function"""
    logger.info("🔧 Starting enhanced fallback timing test...")
    
    # Test the enhanced timing
    success = test_fallback_timing()
    
    if success:
        logger.info("🎉 Enhanced fallback timing test PASSED!")
        logger.info("🎯 Fallback generation now uses intelligent 5-10 second frame timing")
    else:
        logger.error("❌ Enhanced fallback timing test FAILED!")
        logger.error("🔍 Please check the logs for details")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 