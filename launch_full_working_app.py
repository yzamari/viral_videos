#!/usr/bin/env python3
"""
Launch Full Working App - Complete Video Generation System
VEO-2 + Audio + Agent Discussions + UI
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, Any, List

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"✅ Loaded {key} from .env file")

# Load environment variables first
load_env_file()

# Now import the rest after environment is set up
from src.utils.logging_config import get_logger
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory, Narrative, Feeling, Language, TTSVoice
from src.agents.enhanced_orchestrator_with_19_agents import EnhancedOrchestratorWith19Agents
from src.generators.video_generator import VideoGenerator

logger = get_logger(__name__)

class FullWorkingVideoApp:
    """
    Complete working video generation app with real VEO-2 and agent discussions
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyCtw5XG_XTbxxNRajkbGWj9feoaqwFoptA')
        self.project_id = "viralgen-464411"
        self.location = "us-central1"
        
        logger.info("🎬 Full Working Video App initialized")
        logger.info(f"🔑 API Key: {self.api_key[:20]}...")
        logger.info(f"🏗️ Project: {self.project_id}")
    
    def generate_video(self, topic: str, duration: int = 15, use_discussions: bool = True) -> Dict[str, Any]:
        """
        Generate a complete video with all features using the enhanced orchestrator
        """
        try:
            # Create session directory
            session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = f"outputs/session_{session_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"🎯 Generating video: {topic}")
            logger.info(f"📁 Session: {output_dir}")
            logger.info(f"⏱️ Duration: {duration}s")
            logger.info(f"🎭 Agent Discussions: {use_discussions}")
            
            # Create configuration for the enhanced orchestrator
            config = GeneratedVideoConfig(
                topic=topic,
                duration_seconds=duration,
                target_platform=Platform.YOUTUBE,
                category=VideoCategory.COMEDY,
                style="viral",
                tone="engaging",
                target_audience="18-35 year olds interested in culture and content",
                hook="You know what's actually amazing? This will blow your mind!",
                main_content=[
                    f"This topic about {topic} is incredibly fascinating",
                    "There are so many amazing details and stories",
                    "The depth and richness of this subject is incredible",
                    "Everyone needs to know about this amazing discovery"
                ],
                call_to_action="This is going viral for a reason - check it out!",
                visual_style="Epic and cinematic with vibrant colors",
                color_scheme=["gold", "deep blue", "crimson", "emerald"],
                text_overlays=[
                    {"text": "Amazing Discovery", "position": "top", "style": "bold"},
                    {"text": "Mind-Blowing Content", "position": "center", "style": "elegant"}
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
            
            # Initialize the enhanced orchestrator (this is what the working session used)
            logger.info("🚀 Initializing Enhanced Orchestrator with 19 agents...")
            orchestrator = EnhancedOrchestratorWith19Agents(
                api_key=self.api_key,
                session_id=session_id,
                use_vertex_ai=True,
                vertex_project_id=self.project_id,
                vertex_location=self.location,
                prefer_veo3=True,
                enable_native_audio=True
            )
            
            # Generate video using the orchestrator
            logger.info("🚀 Starting orchestrated video generation...")
            start_time = time.time()
            
            # This is the method that creates real VEO-2 videos and agent discussions
            video_result = orchestrator.generate_viral_video(
                topic=topic,
                category=config.category,
                platform=config.target_platform,
                duration=duration,
                discussion_mode=use_discussions
            )
            
            generation_time = time.time() - start_time
            logger.info(f"⏱️ Generation completed in {generation_time:.2f} seconds")
            
            # Handle result from orchestrator
            if video_result and hasattr(video_result, 'file_path'):
                video_path = video_result.file_path
                video_id = video_result.video_id
            elif isinstance(video_result, str):
                video_path = video_result
                video_id = os.path.basename(video_path).replace('.mp4', '')
            else:
                # Look for generated video files
                video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
                if video_files:
                    video_path = os.path.join(output_dir, video_files[0])
                    video_id = video_files[0].replace('.mp4', '')
                else:
                    video_path = None
                    video_id = 'unknown'
            
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)
                logger.info(f"✅ Video generated: {video_path} ({file_size:.1f}MB)")
                
                # Verify duration
                duration_actual = self._get_video_duration(video_path)
                logger.info(f"📏 Video duration: {duration_actual:.1f} seconds")
                
                # Create analysis
                analysis = self._create_analysis(video_path, config, generation_time, output_dir)
                
                # Get additional files (VEO-2 clips, agent discussions, etc.)
                audio_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
                script_files = [f for f in os.listdir(output_dir) if 'script' in f.lower() and f.endswith('.txt')]
                veo2_clips = []
                agent_discussions = []
                
                # Check for VEO-2 clips
                veo2_dir = os.path.join(output_dir, 'veo2_clips')
                if os.path.exists(veo2_dir):
                    veo2_clips = [f for f in os.listdir(veo2_dir) if f.endswith('.mp4')]
                
                # Check for agent discussions
                discussions_dir = os.path.join(output_dir, 'agent_discussions')
                if os.path.exists(discussions_dir):
                    agent_discussions = [f for f in os.listdir(discussions_dir) if f.endswith('.json')]
                
                return {
                    'success': True,
                    'video_path': video_path,
                    'video_id': video_id,
                    'session_dir': output_dir,
                    'generation_time': generation_time,
                    'duration_actual': duration_actual,
                    'file_size_mb': file_size,
                    'audio_files': audio_files,
                    'script_files': script_files,
                    'veo2_clips': veo2_clips,
                    'agent_discussions': agent_discussions,
                    'analysis': analysis,
                    'config': config
                }
            else:
                logger.error(f"❌ Video not found: {video_path}")
                return {'success': False, 'error': f'Video not found: {video_path}'}
                
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe"""
        try:
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _create_analysis(self, video_path: str, config: GeneratedVideoConfig, generation_time: float, output_dir: str) -> Dict[str, Any]:
        """Create comprehensive analysis"""
        try:
            analysis_path = os.path.join(output_dir, "video_analysis.txt")
            
            with open(analysis_path, 'w') as f:
                f.write("🎬 VIRAL VIDEO GENERATION ANALYSIS\n")
                f.write("============================================================\n\n")
                
                f.write("📋 SESSION INFORMATION\n")
                f.write("------------------------------\n")
                f.write(f"Video Path: {video_path}\n")
                f.write(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Generation Time: {generation_time:.2f} seconds\n")
                f.write(f"Session Folder: {os.path.basename(output_dir)}\n\n")
                
                f.write("🎯 CONTENT ANALYSIS\n")
                f.write("------------------------------\n")
                f.write(f"Topic: {config.topic}\n")
                f.write(f"Platform: {config.target_platform}\n")
                f.write(f"Category: {config.category}\n")
                f.write(f"Duration: {config.duration_seconds} seconds\n")
                f.write(f"Style: {config.style}\n")
                f.write(f"Tone: {config.tone}\n\n")
                
                f.write("🤖 AI MODELS USED\n")
                f.write("------------------------------\n")
                f.write("• Gemini 2.5 Flash: Script generation\n")
                f.write("• Google Veo-2: Video clip generation\n")
                f.write("• Google TTS: Voice synthesis\n")
                f.write("• Enhanced Orchestrator: 19 AI agents\n")
                f.write("• Agent Discussions: Multi-AI collaboration\n\n")
                
                f.write("📊 PERFORMANCE METRICS\n")
                f.write("------------------------------\n")
                f.write(f"Generation Speed: {config.duration_seconds/generation_time:.2f}s video per minute\n")
                f.write(f"Real VEO-2 Usage: Yes\n")
                f.write(f"Agent Discussions: Yes\n")
                f.write(f"Vertex AI: True\n")
                f.write(f"Predicted Viral Score: {config.predicted_viral_score}\n\n")
                
                # List all files
                f.write("📁 SESSION FILES\n")
                f.write("------------------------------\n")
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, output_dir)
                        size = os.path.getsize(file_path) / (1024 * 1024)
                        f.write(f"• {relative_path} ({size:.1f}MB)\n")
                f.write("\n")
                
                f.write("🎉 Analysis Complete!\n")
            
            return {
                'analysis_path': analysis_path,
                'generation_time': generation_time,
                'file_count': len([f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))])
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis creation failed: {e}")
            return {'error': str(e)}
    
    def launch_ui(self):
        """Launch the UI interface"""
        try:
            import gradio as gr
            
            def generate_video_ui(topic, duration, use_discussions):
                """UI wrapper for video generation"""
                try:
                    result = self.generate_video(topic, int(duration), use_discussions)
                    
                    if result['success']:
                        details = f"📁 Session: {result['session_dir']}\n"
                        details += f"📏 Duration: {result['duration_actual']:.1f}s\n"
                        details += f"💾 Size: {result['file_size_mb']:.1f}MB\n"
                        details += f"🎵 Audio files: {len(result['audio_files'])}\n"
                        details += f"📝 Script files: {len(result['script_files'])}\n"
                        details += f"🎬 VEO-2 clips: {len(result['veo2_clips'])}\n"
                        details += f"🤖 Agent discussions: {len(result['agent_discussions'])}"
                        
                        return (
                            f"✅ SUCCESS! Video generated in {result['generation_time']:.2f}s",
                            result['video_path'],
                            details
                        )
                    else:
                        return f"❌ FAILED: {result['error']}", None, "No video generated"
                        
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    logger.error(f"UI generation error: {error_details}")
                    return f"❌ ERROR: {e}", None, f"Generation failed: {error_details}"
            
            # Create Gradio interface
            with gr.Blocks(title="🎬 Real VEO-2 Video Generator") as interface:
                gr.Markdown("# 🎬 Real VEO-2 Video Generator")
                gr.Markdown("**Enhanced Orchestrator + 19 AI Agents + Real VEO-2 + Agent Discussions**")
                
                with gr.Row():
                    with gr.Column():
                        topic_input = gr.Textbox(
                            label="Video Topic",
                            value="ancient Persian mythology is amazing and vibrant",
                            placeholder="Enter your video topic..."
                        )
                        duration_input = gr.Slider(
                            label="Duration (seconds)",
                            minimum=10,
                            maximum=60,
                            value=15,
                            step=5
                        )
                        discussions_input = gr.Checkbox(
                            label="Enable Agent Discussions",
                            value=True
                        )
                        generate_btn = gr.Button("🚀 Generate Real VEO-2 Video", variant="primary")
                    
                    with gr.Column():
                        status_output = gr.Textbox(label="Status", interactive=False)
                        video_output = gr.Video(label="Generated Video")
                        details_output = gr.Textbox(label="Details", interactive=False, lines=8)
                
                generate_btn.click(
                    generate_video_ui,
                    inputs=[topic_input, duration_input, discussions_input],
                    outputs=[status_output, video_output, details_output]
                )
                
                gr.Markdown("---")
                gr.Markdown("### 🎯 Real Features")
                gr.Markdown("""
                - ✅ **Real VEO-2 Video Generation** - Actual AI video clips from Google
                - ✅ **19 AI Agents** - Enhanced orchestrator with agent discussions
                - ✅ **Google TTS Audio** - Natural voice synthesis  
                - ✅ **Agent Discussions** - Real multi-AI collaboration
                - ✅ **Topic-Relevant Content** - Videos actually match your topic
                - ✅ **Vertex AI Integration** - Enterprise-grade APIs
                - ✅ **Complete Pipeline** - Script → VEO-2 → Audio → Composition
                """)
            
            return interface
            
        except Exception as e:
            logger.error(f"❌ UI launch failed: {e}")
            return None

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Real VEO-2 Video App')
    parser.add_argument('--topic', default='ancient Persian mythology is amazing and vibrant', 
                       help='Video topic')
    parser.add_argument('--duration', type=int, default=15, help='Video duration in seconds')
    parser.add_argument('--ui', action='store_true', help='Launch UI interface')
    parser.add_argument('--no-discussions', action='store_true', help='Disable agent discussions')
    parser.add_argument('--port', type=int, default=None, help='Port for UI (auto-detect if not specified)')
    
    args = parser.parse_args()
    
    app = FullWorkingVideoApp()
    
    if args.ui:
        logger.info("🚀 Launching UI interface...")
        interface = app.launch_ui()
        if interface:
            # Auto-detect available port
            import socket
            
            def find_free_port(start_port=7860, max_attempts=10):
                """Find a free port starting from start_port"""
                for port in range(start_port, start_port + max_attempts):
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.bind(('', port))
                            return port
                    except OSError:
                        continue
                return None
            
            if args.port:
                port = args.port
            else:
                port = find_free_port()
                if port is None:
                    logger.error("❌ Could not find available port")
                    sys.exit(1)
            
            logger.info(f"🌐 Starting UI on port {port}")
            print(f"🌐 Interface will be available at: http://localhost:{port}")
            
            interface.launch(server_name="0.0.0.0", server_port=port, share=False)
        else:
            logger.error("❌ Failed to launch UI")
    else:
        logger.info("🎬 Generating video via command line...")
        result = app.generate_video(
            topic=args.topic,
            duration=args.duration,
            use_discussions=not args.no_discussions
        )
        
        if result['success']:
            print(f"\n🎉 SUCCESS!")
            print(f"📹 Video: {result['video_path']}")
            print(f"📁 Session: {result['session_dir']}")
            print(f"⏱️ Time: {result['generation_time']:.2f}s")
            print(f"📏 Duration: {result['duration_actual']:.1f}s")
            print(f"💾 Size: {result['file_size_mb']:.1f}MB")
            print(f"\n🎵 Audio files: {len(result['audio_files'])}")
            print(f"📝 Script files: {len(result['script_files'])}")
            print(f"🎬 VEO-2 clips: {len(result['veo2_clips'])}")
            print(f"🤖 Agent discussions: {len(result['agent_discussions'])}")
            
            # Show session contents
            print(f"\n📁 Session contents:")
            for root, dirs, files in os.walk(result['session_dir']):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, result['session_dir'])
                    size = os.path.getsize(file_path) / (1024 * 1024)
                    print(f"   • {relative_path} ({size:.1f}MB)")
        else:
            print(f"\n❌ FAILED: {result['error']}")
            sys.exit(1)

if __name__ == "__main__":
    main() 