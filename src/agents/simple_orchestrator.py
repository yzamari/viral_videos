"""
Simple Video Generation Orchestrator
One orchestrator that actually works - calls the real video generator directly
"""

import os
from typing import Dict, Any
from datetime import datetime

from ..generators.video_generator import VideoGenerator
from ..models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class SimpleOrchestrator:
    """
    Simple orchestrator that actually generates videos
    No complex discussions, just direct video generation
    """
    
    def __init__(self, api_key: str, topic: str, platform: Platform, 
                 category: VideoCategory, duration: int):
        self.api_key = api_key
        self.topic = topic
        self.platform = platform
        self.category = category
        self.duration = duration
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("🎬 Simple Orchestrator initialized")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Session: {self.session_id}")
    
    def generate_video(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video directly using the real video generator
        """
        logger.info("🎬 Starting simple video generation")
        
        try:
            # Create video generator
            video_generator = VideoGenerator(
                api_key=self.api_key,
                use_real_veo2=config.get('force_generation') != 'force_image_gen',
                use_vertex_ai=True
            )
            
            # Create video config
            video_config = GeneratedVideoConfig(
                target_platform=self.platform,
                category=self.category,
                duration_seconds=self.duration,
                topic=self.topic,
                style="viral",
                tone="engaging",
                target_audience="young adults",
                hook=f"Amazing {self.topic}",
                main_content=[f"Content about {self.topic}"],
                call_to_action="Follow for more!",
                visual_style="dynamic",
                color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
                text_overlays=[],
                transitions=["fade", "slide"],
                background_music_style="upbeat",
                voiceover_style="energetic",
                sound_effects=[],
                inspired_by_videos=[],
                predicted_viral_score=0.85,
                frame_continuity=config.get('frame_continuity') == 'on',
                image_only_mode=config.get('force_generation') == 'force_image_gen',
                use_real_veo2=config.get('force_generation') != 'force_image_gen'
            )
            
            logger.info("🎬 Generating video with real video generator...")
            
            # Generate actual video
            video_path = video_generator.generate_video(video_config)
            
            logger.info(f"✅ Video generated successfully: {video_path}")
            
            return {
                'success': True,
                'final_video_path': video_path,
                'session_id': self.session_id,
                'generation_time': 'calculated_externally',
                'agents_used': 1,
                'optimization_level': 'simple_direct'
            }
            
        except Exception as e:
            logger.error(f"❌ Simple video generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id
            }
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress (simple orchestrator doesn't have complex progress tracking)"""
        return {
            'progress': 100,  # Simple orchestrator completes immediately
            'session_id': self.session_id,
            'current_phase': 'completed',
            'results': {}
        }


def create_simple_orchestrator(topic: str, platform: str, category: str,
                             duration: int, api_key: str) -> SimpleOrchestrator:
    """
    Factory function to create simple orchestrator
    """
    try:
        platform_enum = Platform(platform.lower())
    except ValueError:
        platform_enum = Platform.INSTAGRAM
    
    try:
        category_enum = VideoCategory(category.upper())
    except ValueError:
        category_enum = VideoCategory.LIFESTYLE
    
    return SimpleOrchestrator(
        api_key=api_key,
        topic=topic,
        platform=platform_enum,
        category=category_enum,
        duration=duration
    ) 