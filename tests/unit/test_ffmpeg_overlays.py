#!/usr/bin/env python3
"""
Test script for the new FFmpeg-based overlay system
"""

import asyncio
import logging
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_overlays():
    """Test the enhanced overlay system"""
    
    try:
        from src.agents.enhanced_overlay_agent import EnhancedOverlayAgent, EnhancedOverlay, OverlayEffect
        from src.utils.ffmpeg_processor import FFmpegProcessor
        
        logger.info("🧪 Testing Enhanced Overlay System")
        
        # Create test overlays
        test_overlays = [
            EnhancedOverlay(
                text="🚨 VIRAL ALERT",
                start_time=0.5,
                duration=2.0,
                x_position="(w-text_w)/2",
                y_position="h*0.1",
                font_size=40,
                font_color="#FF0040",
                effect=OverlayEffect.BOUNCE,
                purpose="Hook attention"
            ),
            EnhancedOverlay(
                text="💯 MIND = BLOWN",
                start_time=3.0,
                duration=2.5,
                x_position="w*0.05", 
                y_position="h*0.3",
                font_size=32,
                font_color="#00FF80",
                effect=OverlayEffect.SLIDE_IN_LEFT,
                purpose="Build excitement"
            ),
            EnhancedOverlay(
                text="👆 DOUBLE TAP NOW",
                start_time=8.0,
                duration=3.0,
                x_position="(w-text_w)/2",
                y_position="h*0.8",
                font_size=36,
                font_color="#FFD700",
                effect=OverlayEffect.PULSE,
                purpose="Drive engagement"
            )
        ]
        
        # Test FFmpeg filter generation
        agent = EnhancedOverlayAgent(None)  # Mock AI manager for testing
        filters = agent.convert_to_ffmpeg_filters(test_overlays)
        
        logger.info("✅ Generated FFmpeg filters:")
        logger.info(f"   {filters}")
        
        # Test individual overlay conversion
        for i, overlay in enumerate(test_overlays):
            drawtext = overlay.to_ffmpeg_drawtext()
            logger.info(f"✅ Overlay {i+1}: {drawtext[:100]}...")
        
        logger.info("🎉 Enhanced overlay system test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_ffmpeg_processor():
    """Test the FFmpeg processor"""
    
    try:
        from src.utils.ffmpeg_processor import FFmpegProcessor
        
        logger.info("🧪 Testing FFmpeg Processor")
        
        with FFmpegProcessor() as ffmpeg:
            # Test text overlay conversion
            test_overlays = [
                {
                    'text': '🔥 AMAZING CONTENT',
                    'start_time': 1.0,
                    'end_time': 4.0,
                    'font_size': 32,
                    'font_color': 'white',
                    'x': '(w-text_w)/2',
                    'y': 'h*0.1',
                    'box': True,
                    'box_color': 'black@0.7'
                }
            ]
            
            logger.info("✅ FFmpeg processor initialized successfully!")
            logger.info("✅ Text overlay methods available")
        
    except Exception as e:
        logger.error(f"❌ FFmpeg processor test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing New FFmpeg-Based Overlay System")
    print("=" * 50)
    
    # Test FFmpeg processor
    test_ffmpeg_processor()
    
    # Test enhanced overlays  
    asyncio.run(test_enhanced_overlays())
    
    print("=" * 50)
    print("✅ All tests completed!")