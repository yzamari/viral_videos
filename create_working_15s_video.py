#!/usr/bin/env python3
"""
Create a working 15-second video that replicates the successful session structure
Based on session_20250707_105744_d84e40eb analysis
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.logging_config import get_logger
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory, Narrative, Feeling, Language, TTSVoice
from src.generators.video_generator import VideoGenerator

logger = get_logger(__name__)

class WorkingVideoReplicator:
    """
    Replicates the successful video generation session structure
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyCtw5XG_XTbxxNRajkbGWj9feoaqwFoptA')
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = f"outputs/session_{self.session_id}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"🎬 Working Video Replicator initialized")
        logger.info(f"📁 Output directory: {self.output_dir}")
    
    def create_15_second_video(self, topic: str = "ancient Persian mythology vs modern politics") -> str:
        """
        Create a 15-second video following the successful session pattern
        """
        try:
            logger.info(f"🎯 Creating 15-second video on topic: {topic}")
            
            # Step 1: Create video config (matching successful session)
            config = GeneratedVideoConfig(
                topic=topic,
                duration_seconds=15,  # 15 seconds instead of 45
                target_platform=Platform.YOUTUBE,
                category=VideoCategory.COMEDY,
                style="viral",
                tone="engaging",
                target_audience="18-35 year olds interested in culture and history",
                hook="You know what's actually wild? I just discovered something amazing!",
                main_content=[
                    "Ancient Persian mythology is incredibly rich and vibrant",
                    "Epic heroes like Rostam who can move mountains",
                    "Mythical creatures like the Simorgh, a bird of pure knowledge",
                    "Stories of courage, wisdom, and good vs evil"
                ],
                call_to_action="Go look up the Shahnameh - this is amazing!",
                visual_style="Epic and cinematic with vibrant colors",
                color_scheme=["gold", "deep blue", "crimson", "emerald"],
                text_overlays=[
                    {"text": "Persian Mythology", "position": "top", "style": "bold"},
                    {"text": "Epic Heroes & Legends", "position": "center", "style": "elegant"}
                ],
                transitions=["fade", "slide", "zoom"],
                background_music_style="Epic orchestral with Middle Eastern influences",
                voiceover_style="natural",
                sound_effects=["whoosh", "magical chimes", "epic drums"],
                inspired_by_videos=["persian_mythology_viral_2024"],
                predicted_viral_score=0.85,
                narrative=Narrative.PRO_EDUCATION,
                feeling=Feeling.INSPIRATIONAL,
                primary_language=Language.ENGLISH,
                tts_voice=TTSVoice.EN_US_MALE_NATURAL,
                frame_continuity=True,
                fallback_only=False,
                image_only_mode=False,
                use_image_fallback=True,
                images_per_second=2
            )
            
            # Step 2: Initialize video generator with proper parameters
            generator = VideoGenerator(
                api_key=self.api_key,
                output_dir=self.output_dir,
                use_real_veo2=True,
                use_vertex_ai=True,
                project_id="viralgen-464411",
                location="us-central1"
            )
            
            # Step 3: Generate video using the working pattern
            logger.info("🚀 Starting video generation...")
            start_time = time.time()
            
            video_result = generator.generate_video(config)
            
            generation_time = time.time() - start_time
            logger.info(f"⏱️ Video generation completed in {generation_time:.2f} seconds")
            
            # Step 4: Create analysis report (matching successful session)
            self._create_analysis_report(video_result, config, generation_time)
            
            return video_result.video_path
            
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            raise
    
    def _create_analysis_report(self, video_result, config, generation_time):
        """
        Create analysis report matching the successful session format
        """
        try:
            analysis_path = os.path.join(self.output_dir, "video_analysis.txt")
            
            with open(analysis_path, 'w') as f:
                f.write("🎬 VIRAL VIDEO GENERATION ANALYSIS\n")
                f.write("============================================================\n\n")
                
                f.write("📋 SESSION INFORMATION\n")
                f.write("------------------------------\n")
                f.write(f"Video ID: {video_result.video_id}\n")
                f.write(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Generation Time: {generation_time:.2f} seconds\n")
                f.write(f"Session Folder: {os.path.basename(self.output_dir)}\n\n")
                
                f.write("🎯 CONTENT ANALYSIS\n")
                f.write("------------------------------\n")
                f.write(f"Original Prompt: {config.topic}\n")
                f.write(f"Platform: {config.target_platform}\n")
                f.write(f"Category: {config.category}\n")
                f.write(f"Duration: {config.duration_seconds} seconds\n")
                f.write(f"Style: {config.style}\n")
                f.write(f"Tone: {config.tone}\n\n")
                
                f.write("🤖 AI MODELS USED\n")
                f.write("------------------------------\n")
                f.write("• Gemini 2.5 Flash: Initial script generation\n")
                f.write("• Gemini 2.5 Pro: Script refinement & TTS optimization\n")
                f.write("• Google Veo-2: AI video clip generation\n")
                f.write("• Google TTS: Natural voice synthesis\n\n")
                
                f.write("📊 PERFORMANCE METRICS\n")
                f.write("------------------------------\n")
                f.write(f"Generation Speed: {config.duration_seconds/generation_time:.2f}s video per minute\n")
                f.write(f"Real Veo-2 Usage: {config.use_real_veo2}\n")
                f.write(f"Predicted Viral Score: {config.predicted_viral_score}\n\n")
                
                f.write("🎉 Analysis Complete!\n")
            
            logger.info(f"📊 Analysis report created: {analysis_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create analysis report: {e}")

def main():
    """Main execution function"""
    try:
        replicator = WorkingVideoReplicator()
        
        # Test topic for 15-second video
        topic = "ancient Persian mythology is amazing and vibrant"
        
        logger.info("🎬 Starting working video replication...")
        
        # Create video
        video_path = replicator.create_15_second_video(topic)
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"🎉 SUCCESS! Video generated: {video_path} ({file_size:.1f}MB)")
            
            # Verify video duration
            try:
                import subprocess
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', video_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    duration = float(result.stdout.strip())
                    logger.info(f"📏 Video duration: {duration:.1f} seconds")
                    
                    if 10 <= duration <= 20:
                        logger.info("✅ Duration is within target range (10-20 seconds)")
                    else:
                        logger.warning(f"⚠️ Duration {duration:.1f}s is outside target range")
                        
            except Exception as e:
                logger.warning(f"Could not verify duration: {e}")
            
            return video_path
        else:
            logger.error("❌ Video generation failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n🎉 SUCCESS! Video created: {result}")
    else:
        print("\n❌ FAILED! No video was created")
        sys.exit(1) 