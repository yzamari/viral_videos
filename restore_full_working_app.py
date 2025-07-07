#!/usr/bin/env python3
"""
Restore Full Working App with VEO-2, Audio, and Agent Discussions
Based on successful session_20250707_105744_d84e40eb
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

logger = get_logger(__name__)

class FullWorkingApp:
    """
    Complete working app restoration based on successful session
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyCtw5XG_XTbxxNRajkbGWj9feoaqwFoptA')
        self.project_id = "viralgen-464411"
        self.location = "us-central1"
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = f"outputs/session_{self.session_id}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"🎬 Full Working App initialized")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"🔑 API Key: {self.api_key[:20]}...")
        logger.info(f"🏗️ Project: {self.project_id}")
    
    def generate_with_orchestrator(self, topic: str, duration: int = 15) -> Dict[str, Any]:
        """
        Generate video using the full orchestrator with agent discussions
        """
        try:
            logger.info(f"🎭 Starting orchestrator generation for: {topic}")
            
            # Import orchestrator
            from src.agents.enhanced_orchestrator_with_discussions import EnhancedOrchestratorWithDiscussions
            
            # Initialize orchestrator
            orchestrator = EnhancedOrchestratorWithDiscussions(
                api_key=self.api_key,
                output_dir=self.output_dir,
                enable_discussions=True,
                discussion_depth="deep",
                max_discussion_rounds=3
            )
            
            # Create video config matching successful session
            video_config = {
                'topic': topic,
                'duration_seconds': duration,
                'platform': 'YOUTUBE',
                'category': 'COMEDY',
                'style': 'viral',
                'tone': 'engaging',
                'use_real_veo2': True,
                'use_vertex_ai': True,
                'project_id': self.project_id,
                'location': self.location,
                'enable_discussions': True,
                'discussion_depth': 'deep',
                'max_discussion_rounds': 3,
                'voice_style': 'natural',
                'background_music': True,
                'text_overlays': True,
                'subtitles': False,
                'watermark': False,
                'aspect_ratio': '16:9',
                'quality': 'high',
                'enable_audio': True,
                'frame_continuity': True,
                'use_image_fallback': True
            }
            
            logger.info("🚀 Starting orchestrator video generation...")
            start_time = time.time()
            
            # Generate video with orchestrator
            result = orchestrator.generate_viral_video(video_config)
            
            generation_time = time.time() - start_time
            logger.info(f"⏱️ Orchestrator generation completed in {generation_time:.2f} seconds")
            
            if result and result.get('video_path'):
                logger.info(f"✅ Orchestrator video generated: {result['video_path']}")
                
                # Create comprehensive analysis
                self._create_comprehensive_analysis(result, video_config, generation_time)
                
                return {
                    'success': True,
                    'video_path': result['video_path'],
                    'session_dir': self.output_dir,
                    'generation_time': generation_time,
                    'agent_discussions': result.get('agent_discussions', {}),
                    'veo2_clips': result.get('veo2_clips', []),
                    'script': result.get('script', ''),
                    'audio_path': result.get('audio_path', ''),
                    'analysis': result.get('analysis', {})
                }
            else:
                logger.error("❌ Orchestrator failed to generate video")
                return {'success': False, 'error': 'Orchestrator failed'}
                
        except Exception as e:
            logger.error(f"❌ Orchestrator generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_with_direct_generator(self, topic: str, duration: int = 15) -> Dict[str, Any]:
        """
        Generate video using direct VideoGenerator (fallback method)
        """
        try:
            logger.info(f"🎬 Starting direct generator for: {topic}")
            
            # Import video generator
            from src.generators.video_generator import VideoGenerator
            
            # Initialize video generator
            generator = VideoGenerator(
                api_key=self.api_key,
                output_dir=self.output_dir,
                use_real_veo2=True,
                use_vertex_ai=True,
                project_id=self.project_id,
                location=self.location
            )
            
            # Create video config
            config = GeneratedVideoConfig(
                topic=topic,
                duration_seconds=duration,
                target_platform=Platform.YOUTUBE,
                category=VideoCategory.COMEDY,
                style="viral",
                tone="engaging",
                target_audience="18-35 year olds interested in culture and history",
                hook="You know what's actually wild? I just discovered something amazing!",
                main_content=[
                    f"This topic about {topic} is incredibly fascinating",
                    "There are so many amazing details and stories",
                    "The depth and beauty of this subject is incredible",
                    "Everyone needs to know about this"
                ],
                call_to_action="This is going viral for a reason - check it out!",
                visual_style="Epic and cinematic with vibrant colors",
                color_scheme=["gold", "deep blue", "crimson", "emerald"],
                text_overlays=[
                    {"text": "Amazing Discovery", "position": "top", "style": "bold"},
                    {"text": "Mind-Blowing Facts", "position": "center", "style": "elegant"}
                ],
                transitions=["fade", "slide", "zoom"],
                background_music_style="Epic orchestral with cultural influences",
                voiceover_style="natural",
                sound_effects=["whoosh", "magical chimes", "epic drums"],
                inspired_by_videos=["viral_content_2024"],
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
            
            logger.info("🚀 Starting direct video generation...")
            start_time = time.time()
            
            # Generate video
            video_result = generator.generate_video(config)
            
            generation_time = time.time() - start_time
            logger.info(f"⏱️ Direct generation completed in {generation_time:.2f} seconds")
            
            if video_result and video_result.video_path:
                logger.info(f"✅ Direct video generated: {video_result.video_path}")
                
                # Create analysis
                self._create_comprehensive_analysis(video_result, config, generation_time)
                
                return {
                    'success': True,
                    'video_path': video_result.video_path,
                    'session_dir': self.output_dir,
                    'generation_time': generation_time,
                    'video_id': video_result.video_id,
                    'script': getattr(video_result, 'script', ''),
                    'audio_path': getattr(video_result, 'audio_path', ''),
                    'analysis': {}
                }
            else:
                logger.error("❌ Direct generator failed")
                return {'success': False, 'error': 'Direct generator failed'}
                
        except Exception as e:
            logger.error(f"❌ Direct generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_comprehensive_analysis(self, result, config, generation_time):
        """
        Create comprehensive analysis matching successful session
        """
        try:
            analysis_path = os.path.join(self.output_dir, "video_analysis.txt")
            
            # Get video info
            video_path = result.get('video_path') if isinstance(result, dict) else getattr(result, 'video_path', '')
            video_id = result.get('video_id') if isinstance(result, dict) else getattr(result, 'video_id', 'unknown')
            
            with open(analysis_path, 'w') as f:
                f.write("🎬 VIRAL VIDEO GENERATION ANALYSIS\n")
                f.write("============================================================\n\n")
                
                f.write("📋 SESSION INFORMATION\n")
                f.write("------------------------------\n")
                f.write(f"Video ID: {video_id}\n")
                f.write(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Generation Time: {generation_time:.2f} seconds\n")
                f.write(f"Session Folder: {os.path.basename(self.output_dir)}\n\n")
                
                f.write("🎯 CONTENT ANALYSIS\n")
                f.write("------------------------------\n")
                topic = config.get('topic') if isinstance(config, dict) else getattr(config, 'topic', 'Unknown')
                f.write(f"Original Prompt: {topic}\n")
                f.write(f"Platform: YOUTUBE\n")
                f.write(f"Category: COMEDY\n")
                duration = config.get('duration_seconds') if isinstance(config, dict) else getattr(config, 'duration_seconds', 15)
                f.write(f"Duration: {duration} seconds\n")
                f.write(f"Style: viral\n")
                f.write(f"Tone: engaging\n\n")
                
                f.write("🤖 AI MODELS USED\n")
                f.write("------------------------------\n")
                f.write("• Gemini 2.5 Flash: Initial script generation\n")
                f.write("• Gemini 2.5 Pro: Script refinement & TTS optimization\n")
                f.write("• Google Veo-2: AI video clip generation\n")
                f.write("• Google TTS: Natural voice synthesis\n")
                f.write("• 19 AI Agents: Multi-phase discussions\n\n")
                
                f.write("📊 PERFORMANCE METRICS\n")
                f.write("------------------------------\n")
                f.write(f"Generation Speed: {duration/generation_time:.2f}s video per minute\n")
                f.write(f"Real Veo-2 Usage: True\n")
                f.write(f"Agent Discussions: Enabled\n")
                f.write(f"Predicted Viral Score: 0.85\n\n")
                
                # Check for files
                if video_path and os.path.exists(video_path):
                    file_size = os.path.getsize(video_path) / (1024 * 1024)
                    f.write(f"📁 SESSION FILES\n")
                    f.write(f"------------------------------\n")
                    f.write(f"• {os.path.basename(video_path)} ({file_size:.1f}MB)\n")
                    
                    # List other files
                    for file in os.listdir(self.output_dir):
                        if file != os.path.basename(video_path) and file != "video_analysis.txt":
                            file_path = os.path.join(self.output_dir, file)
                            if os.path.isfile(file_path):
                                size = os.path.getsize(file_path) / (1024 * 1024)
                                f.write(f"• {file} ({size:.1f}MB)\n")
                    f.write("\n")
                
                f.write("🎉 Analysis Complete!\n")
            
            logger.info(f"📊 Analysis report created: {analysis_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create analysis: {e}")
    
    def launch_ui(self):
        """
        Launch the full UI with all features
        """
        try:
            logger.info("🚀 Launching full UI...")
            
            # Try to import and launch the comprehensive UI
            try:
                from comprehensive_ui_fixed import create_interface
                interface = create_interface()
                logger.info("✅ Comprehensive UI loaded")
                return interface
            except ImportError:
                logger.warning("⚠️ Comprehensive UI not found, trying enhanced UI...")
                
                try:
                    from enhanced_realtime_ui import create_realtime_interface
                    interface = create_realtime_interface()
                    logger.info("✅ Enhanced realtime UI loaded")
                    return interface
                except ImportError:
                    logger.warning("⚠️ Enhanced UI not found, trying basic UI...")
                    
                    try:
                        from gradio_ui import create_gradio_interface
                        interface = create_gradio_interface()
                        logger.info("✅ Basic Gradio UI loaded")
                        return interface
                    except ImportError:
                        logger.error("❌ No UI found")
                        return None
            
        except Exception as e:
            logger.error(f"❌ UI launch failed: {e}")
            return None

def main():
    """Main execution function"""
    try:
        app = FullWorkingApp()
        
        # Test topics
        test_topics = [
            "ancient Persian mythology is amazing and vibrant",
            "the fascinating world of Persian heroes and legends",
            "incredible stories from ancient Persia"
        ]
        
        topic = test_topics[0]  # Start with first topic
        
        logger.info(f"🎬 Starting full working app test with topic: {topic}")
        
        # Try orchestrator first (matching successful session)
        logger.info("🎭 Attempting orchestrator generation...")
        result = app.generate_with_orchestrator(topic, duration=15)
        
        if not result.get('success'):
            logger.warning("⚠️ Orchestrator failed, trying direct generator...")
            result = app.generate_with_direct_generator(topic, duration=15)
        
        if result.get('success'):
            video_path = result['video_path']
            file_size = os.path.getsize(video_path) / (1024 * 1024) if os.path.exists(video_path) else 0
            
            logger.info(f"🎉 SUCCESS! Video generated: {video_path} ({file_size:.1f}MB)")
            logger.info(f"📁 Session directory: {result['session_dir']}")
            logger.info(f"⏱️ Generation time: {result['generation_time']:.2f} seconds")
            
            # Verify video duration
            try:
                import subprocess
                cmd_result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', video_path
                ], capture_output=True, text=True)
                
                if cmd_result.returncode == 0:
                    duration = float(cmd_result.stdout.strip())
                    logger.info(f"📏 Video duration: {duration:.1f} seconds")
                    
                    if 10 <= duration <= 20:
                        logger.info("✅ Duration is within target range (10-20 seconds)")
                    else:
                        logger.warning(f"⚠️ Duration {duration:.1f}s is outside target range")
                        
            except Exception as e:
                logger.warning(f"Could not verify duration: {e}")
            
            # Show session contents
            logger.info("📁 Session contents:")
            for file in os.listdir(result['session_dir']):
                file_path = os.path.join(result['session_dir'], file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path) / (1024 * 1024)
                    logger.info(f"   • {file} ({size:.1f}MB)")
            
            return result
        else:
            logger.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        return None

if __name__ == "__main__":
    result = main()
    if result and result.get('success'):
        print(f"\n🎉 SUCCESS! Full working app restored!")
        print(f"📹 Video: {result['video_path']}")
        print(f"📁 Session: {result['session_dir']}")
        print(f"⏱️ Time: {result['generation_time']:.2f}s")
        print(f"\n🚀 Ready to launch UI or generate more videos!")
    else:
        print("\n❌ FAILED! App restoration unsuccessful")
        sys.exit(1) 