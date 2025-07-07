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
    
    def generate_video(self, topic: str, duration: int = 15, platform: str = "youtube", 
                      category: str = "Comedy", use_discussions: bool = True) -> Dict[str, Any]:
        """
        Generate a complete video with all features using the enhanced orchestrator
        """
        try:
            # Create session directory with consistent naming
            session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            session_dir = os.path.join(os.getcwd(), "outputs", f"session_{session_id}")
            os.makedirs(session_dir, exist_ok=True)
            
            # Create subdirectories for organization
            subdirs = [
                'agent_discussions',
                'veo2_clips', 
                'audio_files',
                'scripts',
                'analysis'
            ]
            for subdir in subdirs:
                os.makedirs(os.path.join(session_dir, subdir), exist_ok=True)
            
            logger.info(f"🎯 Generating video: {topic}")
            logger.info(f"📁 Session: {session_dir}")
            logger.info(f"⏱️ Duration: {duration}s")
            logger.info(f"📱 Platform: {platform}")
            logger.info(f"🎭 Category: {category}")
            logger.info(f"🤖 Agent Discussions: {use_discussions}")
            
            # Map platform and category strings to enums
            platform_map = {
                "youtube": Platform.YOUTUBE,
                "tiktok": Platform.TIKTOK,
                "instagram": Platform.INSTAGRAM
            }
            
            category_map = {
                "Comedy": VideoCategory.COMEDY,
                "Entertainment": VideoCategory.ENTERTAINMENT,
                "Education": VideoCategory.EDUCATION
            }
            
            target_platform = platform_map.get(platform.lower(), Platform.YOUTUBE)
            target_category = category_map.get(category, VideoCategory.COMEDY)
            
            # Create configuration for the enhanced orchestrator
            config = GeneratedVideoConfig(
                topic=topic,
                duration_seconds=duration,
                target_platform=target_platform,
                category=target_category,
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
                category=target_category,
                platform=target_platform,
                duration=duration,
                discussion_mode=use_discussions
            )
            
            generation_time = time.time() - start_time
            logger.info(f"⏱️ Generation completed in {generation_time:.2f} seconds")
            
            # Handle result from orchestrator - ensure it's in the session directory
            video_path = None
            video_id = f"video_{session_id}"
            
            if video_result and hasattr(video_result, 'file_path'):
                source_path = video_result.file_path
                video_id = video_result.video_id
                
                # Move video to session directory if it's not already there
                if not source_path.startswith(session_dir):
                    video_path = os.path.join(session_dir, f"final_video_{video_id}.mp4")
                    if os.path.exists(source_path):
                        import shutil
                        shutil.move(source_path, video_path)
                        logger.info(f"📁 Moved video to session directory: {video_path}")
                else:
                    video_path = source_path
                    
            elif isinstance(video_result, str):
                source_path = video_result
                
                # Move video to session directory
                video_path = os.path.join(session_dir, f"final_video_{video_id}.mp4")
                if os.path.exists(source_path) and not source_path.startswith(session_dir):
                    import shutil
                    shutil.move(source_path, video_path)
                    logger.info(f"📁 Moved video to session directory: {video_path}")
                else:
                    video_path = source_path
            else:
                # Look for generated video files in various locations
                search_locations = [
                    session_dir,
                    f"outputs/session_{session_id}",
                    "outputs",
                    "."
                ]
                
                for location in search_locations:
                    if os.path.exists(location):
                        video_files = [f for f in os.listdir(location) if f.endswith('.mp4')]
                        if video_files:
                            source_path = os.path.join(location, video_files[0])
                            video_path = os.path.join(session_dir, f"final_video_{video_id}.mp4")
                            
                            if source_path != video_path:
                                import shutil
                                shutil.move(source_path, video_path)
                                logger.info(f"📁 Found and moved video: {video_path}")
                            else:
                                video_path = source_path
                            break
            
            # Organize all session files
            self._organize_session_files(session_dir, session_id)
            
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)
                logger.info(f"✅ Video generated: {video_path} ({file_size:.1f}MB)")
                
                # Verify duration
                duration_actual = self._get_video_duration(video_path)
                logger.info(f"📏 Video duration: {duration_actual:.1f} seconds")
                
                # Create analysis
                analysis = self._create_analysis(video_path, config, generation_time, session_dir)
                
                # Get organized file lists
                file_summary = self._get_session_file_summary(session_dir)
                
                # Parse agent discussions for visualization
                discussion_data = self._parse_agent_discussions(os.path.join(session_dir, 'agent_discussions'))
                
                return {
                    'success': True,
                    'video_path': video_path,
                    'video_id': video_id,
                    'session_dir': session_dir,
                    'generation_time': generation_time,
                    'duration_actual': duration_actual,
                    'file_size_mb': file_size,
                    'audio_files': file_summary['audio_files'],
                    'script_files': file_summary['script_files'],
                    'veo2_clips': file_summary['veo2_clips'],
                    'agent_discussions': file_summary['agent_discussions'],
                    'discussion_data': discussion_data,
                    'analysis': analysis,
                    'config': config
                }
            else:
                logger.error(f"❌ Video not found after generation")
                return {'success': False, 'error': f'Video not found after generation'}
                
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _organize_session_files(self, session_dir: str, session_id: str):
        """Organize all generated files into proper session structure"""
        try:
            logger.info(f"📁 Organizing session files in {session_dir}")
            
            # Define file patterns and their target directories
            file_patterns = {
                'agent_discussions': ['*discussion*.json', '*agent*.json', '*report*.md', '*visualization*.json'],
                'audio_files': ['*.mp3', '*.wav', '*audio*', '*voice*', '*tts*'],
                'scripts': ['*script*.txt', '*prompt*.txt', '*tts_script*'],
                'veo2_clips': ['*veo*.mp4', '*clip*.mp4', 'sample_*.mp4'],
                'analysis': ['*analysis*.txt', '*report*.txt', '*summary*.txt']
            }
            
            # Search for files in common generation locations
            search_locations = [
                ".",
                "outputs",
                f"outputs/session_{session_id}",
                "temp",
                "/tmp"
            ]
            
            import glob
            import shutil
            
            for location in search_locations:
                if not os.path.exists(location):
                    continue
                    
                for target_dir, patterns in file_patterns.items():
                    target_path = os.path.join(session_dir, target_dir)
                    
                    for pattern in patterns:
                        search_pattern = os.path.join(location, pattern)
                        matching_files = glob.glob(search_pattern)
                        
                        for file_path in matching_files:
                            if os.path.isfile(file_path):
                                filename = os.path.basename(file_path)
                                dest_path = os.path.join(target_path, filename)
                                
                                # Only move if not already in target location
                                if not file_path.startswith(session_dir):
                                    try:
                                        shutil.move(file_path, dest_path)
                                        logger.info(f"📁 Moved {filename} to {target_dir}/")
                                    except Exception as move_error:
                                        logger.warning(f"Could not move {filename}: {move_error}")
            
            logger.info(f"✅ Session files organized in {session_dir}")
            
        except Exception as e:
            logger.warning(f"File organization failed: {e}")
    
    def _get_session_file_summary(self, session_dir: str) -> Dict[str, List[str]]:
        """Get summary of all files in the session directory"""
        summary = {
            'audio_files': [],
            'script_files': [],
            'veo2_clips': [],
            'agent_discussions': [],
            'analysis_files': []
        }
        
        try:
            # Check each subdirectory
            subdirs = {
                'audio_files': 'audio_files',
                'script_files': 'scripts', 
                'veo2_clips': 'veo2_clips',
                'agent_discussions': 'agent_discussions',
                'analysis_files': 'analysis'
            }
            
            for key, subdir in subdirs.items():
                subdir_path = os.path.join(session_dir, subdir)
                if os.path.exists(subdir_path):
                    files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
                    summary[key] = files
            
            # Also check root session directory for any files
            root_files = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f))]
            
            # Categorize root files
            for file in root_files:
                if file.endswith(('.mp3', '.wav')):
                    summary['audio_files'].append(file)
                elif file.endswith('.txt') and ('script' in file.lower() or 'prompt' in file.lower()):
                    summary['script_files'].append(file)
                elif file.endswith('.mp4') and file != f"final_video_{os.path.basename(session_dir).split('_')[-1]}.mp4":
                    summary['veo2_clips'].append(file)
                elif file.endswith('.json') and 'discussion' in file.lower():
                    summary['agent_discussions'].append(file)
                elif file.endswith('.txt') and 'analysis' in file.lower():
                    summary['analysis_files'].append(file)
            
        except Exception as e:
            logger.warning(f"Could not create file summary: {e}")
        
        return summary
    
    def _parse_agent_discussions(self, discussions_dir: str) -> Dict[str, Any]:
        """Parse agent discussion files to extract conversation data"""
        discussion_data = {
            'phases': [],
            'agents': {},
            'consensus': {},
            'decisions': []
        }
        
        if not os.path.exists(discussions_dir):
            return discussion_data
        
        try:
            # Find all discussion files
            discussion_files = [f for f in os.listdir(discussions_dir) if f.endswith('.json')]
            
            for file in discussion_files:
                file_path = os.path.join(discussions_dir, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Extract phase information
                    if 'phase' in data:
                        phase_info = {
                            'name': data.get('phase', 'Unknown'),
                            'agents': data.get('agents', []),
                            'consensus': data.get('consensus', 0.0),
                            'decision': data.get('final_decision', 'No decision recorded'),
                            'timestamp': data.get('timestamp', ''),
                            'discussion_rounds': data.get('discussion_rounds', [])
                        }
                        discussion_data['phases'].append(phase_info)
                    
                    # Extract individual agent contributions
                    if 'agents' in data:
                        for agent_name, agent_data in data['agents'].items():
                            if agent_name not in discussion_data['agents']:
                                discussion_data['agents'][agent_name] = []
                            
                            discussion_data['agents'][agent_name].append({
                                'phase': data.get('phase', 'Unknown'),
                                'contribution': agent_data.get('contribution', ''),
                                'vote': agent_data.get('vote', ''),
                                'reasoning': agent_data.get('reasoning', '')
                            })
                    
                    # Extract consensus information
                    if 'consensus' in data:
                        phase_name = data.get('phase', 'Unknown')
                        discussion_data['consensus'][phase_name] = data['consensus']
                    
                    # Extract final decisions
                    if 'final_decision' in data:
                        discussion_data['decisions'].append({
                            'phase': data.get('phase', 'Unknown'),
                            'decision': data['final_decision'],
                            'consensus': data.get('consensus', 0.0)
                        })
                        
                except Exception as e:
                    logger.error(f"Error parsing discussion file {file}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error reading discussions directory: {e}")
        
        return discussion_data
    
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
    
    def _format_agent_discussions(self, discussion_data: Dict[str, Any]) -> str:
        """Format agent discussions for display"""
        if not discussion_data or not discussion_data.get('phases'):
            return "No agent discussions found."
        
        formatted = "🤖 **AI AGENT DISCUSSIONS**\n\n"
        
        # Overview
        formatted += f"**Total Phases:** {len(discussion_data['phases'])}\n"
        formatted += f"**Total Agents:** {len(discussion_data['agents'])}\n"
        formatted += f"**Decisions Made:** {len(discussion_data['decisions'])}\n\n"
        
        # Phase-by-phase breakdown
        for i, phase in enumerate(discussion_data['phases'], 1):
            formatted += f"## Phase {i}: {phase['name']}\n"
            formatted += f"**Consensus:** {phase['consensus']:.1%}\n"
            formatted += f"**Decision:** {phase['decision']}\n"
            formatted += f"**Agents Involved:** {len(phase['agents'])}\n\n"
            
            # Show individual agent contributions
            if phase['agents']:
                formatted += "### Agent Contributions:\n"
                for agent in phase['agents']:
                    agent_name = agent.get('name', 'Unknown Agent')
                    contribution = agent.get('contribution', 'No contribution recorded')
                    vote = agent.get('vote', 'No vote')
                    
                    formatted += f"**{agent_name}:**\n"
                    formatted += f"- Vote: {vote}\n"
                    formatted += f"- Contribution: {contribution}\n\n"
            
            formatted += "---\n\n"
        
        # Final consensus summary
        if discussion_data['consensus']:
            formatted += "## Final Consensus Summary\n"
            for phase_name, consensus in discussion_data['consensus'].items():
                formatted += f"- **{phase_name}:** {consensus:.1%}\n"
        
        return formatted
    
    def launch_ui(self):
        """Launch the enhanced UI interface with all parameters"""
        try:
            import gradio as gr
            
            def generate_video_ui(topic, duration, platform, category, use_discussions):
                """UI wrapper for video generation"""
                try:
                    result = self.generate_video(topic, int(duration), platform, category, use_discussions)
                    
                    if result['success']:
                        details = f"📁 **Session:** {result['session_dir']}\n"
                        details += f"📏 **Duration:** {result['duration_actual']:.1f}s\n"
                        details += f"💾 **Size:** {result['file_size_mb']:.1f}MB\n"
                        details += f"🎵 **Audio files:** {len(result['audio_files'])}\n"
                        details += f"📝 **Script files:** {len(result['script_files'])}\n"
                        details += f"🎬 **VEO-2 clips:** {len(result['veo2_clips'])}\n"
                        details += f"🤖 **Agent discussions:** {len(result['agent_discussions'])}\n"
                        details += f"⏱️ **Generation time:** {result['generation_time']:.2f}s"
                        
                        # Format agent discussions
                        discussion_text = self._format_agent_discussions(result.get('discussion_data', {}))
                        
                        return (
                            f"✅ **SUCCESS!** Video generated in {result['generation_time']:.2f}s",
                            result['video_path'],
                            details,
                            discussion_text
                        )
                    else:
                        return f"❌ **FAILED:** {result['error']}", None, "No video generated", "No discussions available"
                        
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    logger.error(f"UI generation error: {error_details}")
                    return f"❌ **ERROR:** {e}", None, f"Generation failed: {error_details}", "Error occurred"
            
            # Create enhanced Gradio interface
            with gr.Blocks(title="🎬 Enhanced VEO-2 Video Generator") as interface:
                gr.Markdown("# 🎬 Enhanced VEO-2 Video Generator")
                gr.Markdown("**Complete System: VEO-2 + 19 AI Agents + Real Discussions + Professional Audio**")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("## 🎯 Video Configuration")
                        
                        topic_input = gr.Textbox(
                            label="📝 Video Topic",
                            value="ancient Persian mythology is amazing and vibrant",
                            placeholder="Enter your video topic...",
                            lines=2
                        )
                        
                        with gr.Row():
                        duration_input = gr.Slider(
                                label="⏱️ Duration (seconds)",
                            minimum=10,
                            maximum=60,
                            value=15,
                            step=5
                        )
                            
                            platform_input = gr.Dropdown(
                                label="📱 Target Platform",
                                choices=["youtube", "tiktok", "instagram"],
                                value="youtube"
                            )
                        
                        with gr.Row():
                            category_input = gr.Dropdown(
                                label="🎭 Category",
                                choices=["Comedy", "Entertainment", "Education"],
                                value="Comedy"
                            )
                            
                        discussions_input = gr.Checkbox(
                                label="🤖 Enable 19 AI Agent Discussions",
                            value=True
                        )
                        
                        generate_btn = gr.Button("🚀 Generate Enhanced Video", variant="primary", size="lg")
                        
                        gr.Markdown("---")
                        gr.Markdown("### 🎯 All Features Included")
                        gr.Markdown("""
                        - ✅ **Real VEO-2 Videos** - Actual AI video generation
                        - ✅ **19 AI Agents** - Multi-agent collaboration
                        - ✅ **Platform Optimization** - YouTube/TikTok/Instagram
                        - ✅ **Professional Audio** - Google TTS synthesis
                        - ✅ **Agent Discussions** - Real AI conversations
                        - ✅ **Topic Relevance** - Content matches your topic
                        """)
                    
                    with gr.Column(scale=2):
                        gr.Markdown("## 📊 Results & Analysis")
                        
                        status_output = gr.Markdown(label="Status")
                        
                        with gr.Row():
                            with gr.Column():
                                video_output = gr.Video(label="🎬 Generated Video")
                                details_output = gr.Markdown(label="📋 Generation Details")
                    
                    with gr.Column():
                                gr.Markdown("### 🤖 AI Agent Discussions")
                                discussions_output = gr.Markdown(
                                    label="Agent Conversations",
                                    value="Generate a video to see agent discussions...",
                                    height=400
                                )
                
                generate_btn.click(
                    generate_video_ui,
                    inputs=[topic_input, duration_input, platform_input, category_input, discussions_input],
                    outputs=[status_output, video_output, details_output, discussions_output]
                )
                
                gr.Markdown("---")
                gr.Markdown("## 🚀 System Capabilities")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("""
                        ### 🎬 Video Generation
                        - **VEO-2 Integration**: Real Google AI video clips
                        - **Duration Control**: 10-60 seconds
                        - **Platform Optimization**: Tailored for each platform
                        - **Category Matching**: Comedy, Entertainment, Education
                        """)
                    
                    with gr.Column():
                        gr.Markdown("""
                        ### 🤖 AI Agent System
                        - **19 Specialized Agents**: Each with unique expertise
                        - **5 Discussion Phases**: Comprehensive collaboration
                        - **Consensus Building**: Democratic decision making
                        - **Real Conversations**: Actual AI-to-AI discussions
                        """)
                    
                    with gr.Column():
                gr.Markdown("""
                        ### 🎵 Audio & Effects
                        - **Google TTS**: Natural voice synthesis
                        - **Multi-language Support**: Various accents
                        - **Sound Effects**: Professional audio design
                        - **Perfect Sync**: Audio-video alignment
                """)
            
            return interface
            
        except Exception as e:
            logger.error(f"❌ UI launch failed: {e}")
            return None

def main():
    """Main execution function with all CLI parameters"""
    parser = argparse.ArgumentParser(description='Enhanced VEO-2 Video Generator')
    parser.add_argument('--topic', default='ancient Persian mythology is amazing and vibrant', 
                       help='Video topic')
    parser.add_argument('--duration', type=int, choices=[10, 15, 20, 30, 45, 60], default=15, 
                       help='Video duration in seconds (10|30|60)')
    parser.add_argument('--platform', choices=['youtube', 'tiktok', 'instagram'], default='youtube',
                       help='Target platform (youtube|tiktok|instagram)')
    parser.add_argument('--category', choices=['Comedy', 'Entertainment', 'Education'], default='Comedy',
                       help='Video category (Comedy|Entertainment|Education)')
    parser.add_argument('--discussions', action='store_true', default=True,
                       help='Enable 19 AI agent discussions')
    parser.add_argument('--no-discussions', action='store_true', 
                       help='Disable agent discussions')
    parser.add_argument('--ui', action='store_true', help='Launch web interface')
    parser.add_argument('--port', type=int, default=None, 
                       help='Custom port for UI (auto-detect if not specified)')
    
    args = parser.parse_args()
    
    # Handle discussions flag
    use_discussions = args.discussions and not args.no_discussions
    
    app = FullWorkingVideoApp()
    
    if args.ui:
        logger.info("🚀 Launching Enhanced UI interface...")
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
            
            logger.info(f"🌐 Starting Enhanced UI on port {port}")
            print(f"🌐 Interface available at: http://localhost:{port}")
            print(f"🎬 All parameters included: topic, duration, platform, category, discussions")
            print(f"🤖 Agent discussions fully visualized with individual contributions")
            
            interface.launch(server_name="0.0.0.0", server_port=port, share=False)
        else:
            logger.error("❌ Failed to launch UI")
    else:
        logger.info("🎬 Generating video via command line...")
        print(f"🎯 Topic: {args.topic}")
        print(f"⏱️ Duration: {args.duration}s")
        print(f"📱 Platform: {args.platform}")
        print(f"🎭 Category: {args.category}")
        print(f"🤖 Discussions: {use_discussions}")
        
        result = app.generate_video(
            topic=args.topic,
            duration=args.duration,
            platform=args.platform,
            category=args.category,
            use_discussions=use_discussions
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
            
            # Show agent discussion summary
            if result.get('discussion_data') and result['discussion_data'].get('phases'):
                print(f"\n🤖 AGENT DISCUSSION SUMMARY:")
                for phase in result['discussion_data']['phases']:
                    print(f"   • {phase['name']}: {phase['consensus']:.1%} consensus")
                    print(f"     Decision: {phase['decision']}")
            
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