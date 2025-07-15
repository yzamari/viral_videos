#!/usr/bin/env python3
""""
🎬 Enhanced Ultimate Modern Video Generator UI
All features with real-time updates, force generation options, trending analysis, and more
""""

from config.config import settings
import os
import sys
import threading
import logging
from typing import List, Dict, Any

import gradio as gr

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Removed complex orchestrators - using simple one that works

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrendingAnalyzer:
    """Analyze trending videos for content optimization"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_trending_videos(self, platform: str, hours: int = 24, count: int = 10) -> List[Dict]:
        """Get trending videos from platform"""
        try:
            # This is a placeholder - in production you'd use actual APIs
            # YouTube Data API, TikTok API, etc.
            logger.info(f"🔍 Analyzing {count} trending videos from {platform} (past {hours}h)")

            # Simulated trending data for demo
            trending_videos = []
            for i in range(count):
                trending_videos.append({
                    'title': f'Trending Video {i + 1}',
                    'views': 1000000 + i * 100000,
                    'engagement_rate': 0.05 + i * 0.01,
                    'keywords': ['viral', 'trending', 'engaging'],
                    'hook_type': 'question' if i % 2 == 0 else 'statement',
                    'duration': 15 + i * 5,
                    'platform': platform
                })

            return trending_videos

        except Exception as e:
            logger.error(f"Error getting trending videos: {e}")
            return []

    def analyze_trends(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze trending patterns"""
        if not videos:
            return {'error': 'No videos to analyze'}

        analysis = {
            'common_keywords': ['viral', 'trending', 'engaging', 'amazing'],
            'avg_duration': sum(v['duration'] for v in videos) / len(videos),
            'best_hook_type': 'question',
            'optimal_engagement_triggers': [
                'Start with a question',
                'Use emotional hooks',
                'Include trending keywords',
                'Keep under 30 seconds'
            ],
            'platform_insights': {
                'instagram': 'Focus on visual appeal and quick engagement',
                'tiktok': 'Use trending sounds and quick cuts',
                'youtube': 'Strong thumbnails and compelling titles'
            }
        }

        return analysis


class EnhancedModernVideoGeneratorUI:
    """Enhanced ultimate modern video generator UI with all features"""

    def __init__(self):
        self.current_session = None
        self.orchestrator = None
        self.is_generating = False
        self.generation_thread = None
        self.generation_result = {}
        self.progress_data = {'progress': 0, 'message': 'Ready'}
        self.discussion_data = {}
        self.trending_analyzer = TrendingAnalyzer(settings.google_api_key)
        self.final_video_path = None

        # Real-time monitoring
        self.progress_file = None
        self.discussion_file = None

    def create_interface(self):
        """Create the enhanced ultimate modern interface"""

        # Enhanced CSS for modern look
        custom_css = """"
        /* Modern Design System */
        .gradio-container {
            max-width: 1400px !important;
            margin: 0 auto;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .feature-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }

        .progress-container {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            color: white;
        }

        .progress-bar {
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            height: 12px;
            overflow: hidden;
            margin: 1rem 0;
        }

        .progress-fill {
            background: white;
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }

        .agent-status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }

        .agent-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border-left: 4px solid #cbd5e0;
            transition: all 0.3s ease;
        }

        .agent-card.active {
            border-left-color: #10b981;
            background: #f0fdf4;
            transform: scale(1.02);
        }

        .agent-card.completed {
            border-left-color: #059669;
            background: #ecfdf5;
        }

        .discussion-container {
            background: #f8fafc;
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            border: 1px solid #e2e8f0;
            max-height: 400px;
            overflow-y: auto;
        }

        .discussion-pair {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .discussion-pair.active {
            border-left-color: #10b981;
            background: #f0fdf4;
        }

        .discussion-pair.completed {
            border-left-color: #059669;
            background: #ecfdf5;
        }

        .force-option {
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }

        .trending-section {
            background: #ede9fe;
            border: 1px solid #8b5cf6;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }

        .video-result {
            background: #dcfce7;
            border: 1px solid #16a34a;
            border-radius: 12px;
            padding: 2rem;
            margin: 2rem 0;
            text-align: center;
        }

        .download-button {
            background: #059669;
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            margin: 0.5rem;
        }

        .download-button:hover {
            background: #047857;
        }
        """"

        with gr.Blocks(
            css=custom_css,
            title="🎬 Enhanced Ultimate Modern Video Generator"
        ) as interface:

            # Header
            gr.HTML(""""
            <div class="main-header">
                <h1>🎬 Enhanced Ultimate Modern Video Generator</h1>
                <p>AI-Powered Viral Content Creation with Real-Time Updates & Advanced Features</p>
            </div>
            """")

            with gr.Row():
                with gr.Column(scale=2):
                    # Configuration Section
                    gr.HTML("<h2>📝 Video Configuration</h2>")

                    mission_input = gr.Textbox(
                        label="Mission/Topic",
                        placeholder="Enter your video mission or topic...",
                        lines=3,
                        value="Create engaging content about Hila Pinto's Ashtanga Yoga journey, balancing family life with spiritual practice"
                    )

                    with gr.Row():
                        platform_dropdown = gr.Dropdown(
                            choices=["instagram", "tiktok", "youtube", "twitter"],
                            value="instagram",
                            label="Platform",
                            info="Target social media platform"
                        )

                        category_dropdown = gr.Dropdown(
                            choices=[
                                "Educational",
                                "Comedy",
                                "Entertainment",
                                "News",
                                "Tech",
                                "Health",
                                "Lifestyle"],
                            value="Educational",
                            label="Category",
                            info="Video content category")

                    with gr.Row():
                        duration_slider = gr.Slider(
                            minimum=10,
                            maximum=60,
                            value=25,
                            step=5,
                            label="Duration (seconds)",
                            info="Video length in seconds"
                        )

                        system_dropdown = gr.Dropdown(
                            choices=[
                                "simple",
                                "enhanced",
                                "advanced",
                                "multilingual",
                                "professional"],
                            value="enhanced",
                            label="AI System",
                            info="Simple=3 agents",
                                Enhanced=7 agents, Advanced=15 agents, Multilingual=8 agents, Professional=19 agents"")

                    # Force Generation Options
                    with gr.Accordion("⚡ Force Generation Options", open=False):
                        gr.HTML('<div class="force-option">Choose specific generation method to force</div>')

                        force_generation = gr.Dropdown(
                            choices=["auto", "force_veo3", "force_veo2", "force_image_gen"],
                            value="auto",
                            label="Force Generation Method",
                            info="Auto uses intelligent fallback, force options override"
                        )

                        gr.HTML(""""
                        <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                            <strong>force_veo3:</strong> Latest VEO-3 model (highest quality)<br>
                            <strong>force_veo2:</strong> Stable VEO-2 model (reliable)<br>
                            <strong>force_image_gen:</strong> Image-based generation (fastest)
                        </div>
                        """")

                    # Trending Analysis Options
                    with gr.Accordion("📈 Trending Analysis (ContentSpecialist)", open=False):
                        gr.HTML(
                            '<div class="trending-section">Analyze trending content for 
                                optimization</div>')

                        enable_trending = gr.Checkbox(
                            label="Enable Trending Analysis",
                            value=False,
                            info="ContentSpecialist will analyze trending videos"
                        )

                        with gr.Row():
                            trending_count = gr.Slider(
                                minimum=5,
                                maximum=50,
                                value=10,
                                step=5,
                                label="Videos to Analyze",
                                info="Number of trending videos to study"
                            )

                            trending_hours = gr.Slider(
                                minimum=1,
                                maximum=72,
                                value=24,
                                step=1,
                                label="Time Range (hours)",
                                info="How recent should trending videos be"
                            )

                    # Advanced Options
                    with gr.Accordion("⚙️ Advanced Options", open=False):
                        with gr.Row():
                            image_only = gr.Checkbox(
                                label="Image Only Mode",
                                value=False,
                                info="Generate using images only"
                            )

                            fallback_only = gr.Checkbox(
                                label="Fallback Only",
                                value=False,
                                info="Use fallback generation methods"
                            )

                        frame_continuity = gr.Dropdown(
                            choices=["auto", "on", "of"],
                            value="auto",
                            label="Frame Continuity",
                            info="AI decides frame continuity automatically"
                        )

                    # Generation Controls
                    with gr.Row():
                        generate_btn = gr.Button(
                            "🚀 Generate Video",
                            variant="primary",
                            size="lg",
                            scale=3
                        )

                        stop_btn = gr.Button(
                            "⏹️ Stop",
                            variant="stop",
                            visible=False,
                            scale=1
                        )

                with gr.Column(scale=1):
                    # Real-time Status Section
                    gr.HTML("<h2>⚡ Live Status</h2>")

                    status_display = gr.HTML(
                        """"
                        <div style="background: #e0e7ff; color: #3730a3; padding: 1rem; border-radius: 8px;">
                            <strong>🎯 Ready to Generate</strong><br>
                            <small>Configure your video and click Generate</small>
                        </div>
                        """"
                    )

                    # Progress Section with auto-refresh
                    progress_display = gr.HTML(
                        """"
                        <div style="display: grid; grid-template-columns: repeat(3",
                            1fr); gap: 1rem; margin: 1rem 0;">"
                            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: bold;">7</div>
                                <div style="color: #6b7280; font-size: 0.9rem;">AI Agents</div>
                            </div>
                            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: bold;">3</div>
                                <div style="color: #6b7280; font-size: 0.9rem;">Discussions</div>
                            </div>
                            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: bold;">0%</div>
                                <div style="color: #6b7280; font-size: 0.9rem;">Progress</div>
                            </div>
                        </div>
                        """"
                    )

            # Agent Status Section with auto-refresh
            gr.HTML("<h2>🤖 AI Agent Status</h2>")
            agent_status_display = gr.HTML(self._create_initial_agent_status())

            # Discussion Section with auto-refresh
            gr.HTML("<h2>💬 Real-Time Agent Discussions</h2>")
            discussion_display = gr.HTML(self._create_initial_discussion_display())

            # Results Section
            gr.HTML("<h2>📊 Generation Results</h2>")

            with gr.Row():
                with gr.Column():
                    # Video Display
                    video_output = gr.Video(
                        label="Generated Video",
                        visible=False
                    )

                    # Video Result Section
                    video_result_display = gr.HTML(
                        "<p>Video will appear here after generation</p>"
                    )

                    # Results JSON
                    results_json = gr.JSON(
                        label="Detailed Results",
                        visible=False
                    )

                with gr.Column():
                    # Download Section
                    download_section = gr.HTML(
                        "<p>Download links will appear here after generation</p>"
                    )

                    # Session Info
                    session_info = gr.JSON(
                        label="Session Information",
                        visible=False
                    )

            # Auto-refresh components for real-time updates
            def update_progress():
                """Update progress in real-time"""
                if self.is_generating and self.orchestrator:
                    try:
                        progress_info = self.orchestrator.get_progress()
                        progress = progress_info.get('progress', 0)
                        current_phase = progress_info.get('current_phase', 'Processing')
                        discussions_completed = progress_info.get('discussions_completed', 0)

                        # Update progress display
                        progress_html = """"
                        <div class="progress-container">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                                <h3 style="margin: 0;">Progress: {progress}%</h3>
                                <div style="opacity: 0.9;">{current_phase}</div>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {progress}%;"></div>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(3",
                            1fr); gap: 1rem;">"
                            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: bold;">7</div>
                                <div style="color: #6b7280; font-size: 0.9rem;">AI Agents</div>
                            </div>
                            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: bold;">{discussions_completed}/3</div>
                                <div style="color: #6b7280; font-size: 0.9rem;">Discussions</div>
                            </div>
                            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                                <div style="font-size: 1.5rem; font-weight: bold;">{progress}%</div>
                                <div style="color: #6b7280; font-size: 0.9rem;">Progress</div>
                            </div>
                        </div>
                        """"

                        # Update agent status
                        agent_html = self._create_agent_status(progress)

                        # Update discussion display
                        discussion_html = self._create_discussion_display(progress_info)

                        return progress_html, agent_html, discussion_html

                    except Exception as e:
                        logger.error(f"Progress update error: {e}")

                return progress_display.value, agent_status_display.value, discussion_display.value

            # Event Handlers
            generate_btn.click(
                fn=self.start_generation,
                inputs=[mission_input, platform_dropdown, category_dropdown,
                        duration_slider, system_dropdown, force_generation,
                        enable_trending, trending_count, trending_hours,
                        image_only, fallback_only, frame_continuity],
                outputs=[status_display, generate_btn, stop_btn, progress_display]
            )

            stop_btn.click(
                fn=self.stop_generation,
                outputs=[status_display, generate_btn, stop_btn]
            )

            # Auto-refresh timer for real-time updates
            timer = gr.Timer(value=2.0)  # Update every 2 seconds
            timer.tick(
                fn=update_progress,
                outputs=[progress_display, agent_status_display, discussion_display]
            )

            # Periodic check for completion
            completion_timer = gr.Timer(value=5.0)  # Check every 5 seconds
            completion_timer.tick(
                fn=self.check_completion,
                outputs=[
                    video_output,
                    video_result_display,
                    download_section,
                    results_json,
                    session_info,
                    generate_btn,
                    stop_btn,
                    timer,
                    completion_timer])

        return interface

    def start_generation(self, mission: str, platform: str, category: str,
                         duration: int, system: str, force_generation: str,
                         enable_trending: bool, trending_count: int, trending_hours: int,
                         image_only: bool, fallback_only: bool, frame_continuity: str,
                         target_audience: str = "general audience"):
        """Start video generation process with all options"""

        if self.is_generating:
            return (
                """"
                <div style="background: #fef3c7; color: #92400e; padding: 1rem; border-radius: 8px;">
                    <strong>🔄 Generation in Progress</strong><br>
                    <small>Please wait for current generation to complete</small>
                </div>
                """",
                gr.update(visible=False),
                gr.update(visible=True),
                self._create_progress_display(0, "Generation in progress...")
            )

        self.is_generating = True
        self.progress_data = {'progress': 0, 'message': 'Initializing...'}
        self.discussion_data = {}
        self.final_video_path = None

        # Trending analysis if enabled
        trending_insights = None
        if enable_trending:
            logger.info(
                f"🔍 Performing trending analysis: {trending_count} videos, {trending_hours}h")
            trending_videos = self.trending_analyzer.get_trending_videos(
                platform, trending_hours, trending_count
            )
            trending_insights = self.trending_analyzer.analyze_trends(trending_videos)

        # Create working orchestrator with AI agents
        try:
            from src.agents.working_orchestrator import create_working_orchestrator
            self.orchestrator = create_working_orchestrator(
                mission=mission,
                platform=platform,
                category=category,
                duration=duration,
                api_key=settings.google_api_key
            )
        except Exception as e:
            self.is_generating = False
            return (
                """"
                <div style="background: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 8px;">
                    <strong>❌ Initialization Failed</strong><br>
                    <small>{str(e)}</small>
                </div>
                """",
                gr.update(visible=True),
                gr.update(visible=False),
                self._create_progress_display(0, "Failed to initialize")
            )

        # Start generation in background thread
        def generate():
            try:
                config = {
                    'image_only': image_only,
                    'fallback_only': fallback_only,
                    'target_audience': target_audience,
                    'style': 'viral',
                    'visual_style': 'dynamic',
                    'voice_style': 'energetic',
                    'content_strategy': 'engagement_focused',
                    'frame_continuity': frame_continuity,
                    'quality_requirements': 'high',
                    'force_generation': force_generation,
                    'trending_insights': trending_insights,
                    'enable_trending': enable_trending,
                    'trending_count': trending_count,
                    'trending_hours': trending_hours
                }

                if self.orchestrator:
                    result = self.orchestrator.generate_video(config)
                else:
                    result = {'success': False, 'error': 'Orchestrator not initialized'}
                self.generation_result = result

                # Log final video path
                if result.get('success'):
                    video_path = result.get('final_video_path')
                    if video_path:
                        self.final_video_path = video_path
                        logger.info(f"🎬 FINAL VIDEO CREATED: {self.final_video_path}")
                        print(f"\n🎬 FINAL VIDEO PATH: {self.final_video_path}\n")
                    else:
                        # Check if there are any results that might contain the path
                        logger.info(f"🔍 Generation result: {result}")
                        print(f"\n🔍 GENERATION RESULT: {result}\n")

            except Exception as e:
                logger.error(f"Generation failed: {e}")
                self.generation_result = {'success': False, 'error': str(e)}

        self.generation_thread = threading.Thread(target=generate)
        self.generation_thread.daemon = True
        self.generation_thread.start()

        return (
            """"
            <div style="background: #dcfce7; color: #166534; padding: 1rem; border-radius: 8px;">
                <strong>🚀 Generation Started</strong><br>
                <small>Using {system.title()} AI System</small>
                {f'<br><small>📈 Trending analysis enabled ({trending_count} videos)</small>' if enable_trending else ''}
                {f'<br><small>⚡ Force: {force_generation}</small>' if force_generation != 'auto' else ''}
            </div>
            """",
            gr.update(visible=False),
            gr.update(visible=True),
            self._create_progress_display(0, f"Started {system} generation...")
        )

    def check_completion(self):
        """Check if generation is completed and update UI"""
        if not self.is_generating or not hasattr(self, 'generation_result'):
            return (
                gr.update(visible=False),  # video_output
                "<p>No video generated yet</p>",  # video_result_display
                "<p>No download available</p>",  # download_section
                gr.update(visible=False),  # results_json
                gr.update(visible=False),  # session_info
                gr.update(visible=True),   # generate_btn
                gr.update(visible=False),  # stop_btn
                gr.update(active=True),    # timer
                gr.update(active=True)     # completion_timer
            )

        result = getattr(self, 'generation_result', {})

        if result and result.get('success') is not None:
            self.is_generating = False

            if result.get('success'):
                video_path = result.get('final_video_path')
                session_id = result.get('session_id', 'N/A')

                # Create proper video result display
                video_result_html = """"
                <div class="video-result">
                    <h3>✅ Video Generation Completed!</h3>
                    <p><strong>Session:</strong> {session_id}</p>
                    <p><strong>Agents Used:</strong> {result.get('agents_used', 7)}</p>
                    <p><strong>Discussions:</strong> {result.get('discussions_conducted', 3)}</p>
                    {f'<p><strong>Video Path:</strong> {video_path}</p>' if video_path else ''}
                </div>
                """"

                # Create download section with proper video download
                download_html = self._create_download_section(result)

                return (
                    gr.update(
                        visible=True,
                        value=video_path if video_path and os.path.exists(video_path) else None),
                    video_result_html,
                    download_html,
                    gr.update(visible=True, value=result),
                    gr.update(visible=True, value={'session_id': session_id}),
                    gr.update(visible=True),   # generate_btn
                    gr.update(visible=False),  # stop_btn
                    gr.update(active=False),   # timer
                    gr.update(active=False)    # completion_timer
                )
            else:
                error_msg = result.get('error', 'Unknown error')
                return (
                    gr.update(visible=False),
                    """"
                    <div style="background: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 8px;">
                        <strong>❌ Generation Failed</strong><br>
                        <small>{error_msg}</small>
                    </div>
                    """",
                    "<p>Generation failed</p>",
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(active=False),
                    gr.update(active=False)
                )

        # Still generating
        return (
            gr.update(visible=False),
            "<p>Generation in progress...</p>",
            "<p>Download will be available after completion</p>",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(active=True),
            gr.update(active=True)
        )

    def stop_generation(self):
        """Stop video generation"""
        self.is_generating = False

        return (
            """"
            <div style="background: #e0e7ff; color: #3730a3; padding: 1rem; border-radius: 8px;">
                <strong>⏹️ Generation Stopped</strong><br>
                <small>Ready for new generation</small>
            </div>
            """",
            gr.update(visible=True),
            gr.update(visible=False)
        )

    def _create_initial_agent_status(self):
        """Create initial agent status display"""
        agents = [
            ("ScriptMaster", "📝", "Script generation & narrative structure"),
            ("ViralismSpecialist", "🧠", "Viral psychology & social media expertise"),
            ("ContentSpecialist", "🎯", "Content strategy & audience engagement"),
            ("VisualDirector", "🎨", "Visual storytelling & composition"),
            ("AudioEngineer", "🎵", "Audio production & voice optimization"),
            ("VideoEditor", "✂️", "Video assembly & post-production"),
            ("QualityController", "🛡️", "Quality assurance & optimization")
        ]

        html = '<div class="agent-status-grid">'
        for name, emoji, desc in agents:
            html += '''
            <div class="agent-card">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem;">{emoji}</span>
                    <strong>{name}</strong>
                </div>
                <div style="font-size: 0.9rem; color: #6b7280;">{desc}</div>
                <div style="margin-top: 0.5rem;">
                    <span style="color: #9ca3af; font-size: 0.8rem;">⏳ Ready</span>
                </div>
            </div>
            '''
        html += '</div>'
        return html

    def _create_initial_discussion_display(self):
        """Create initial discussion display"""
        return """"
        <div class="discussion-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3>🤝 AI Agent Discussions</h3>
                <div style="background: #dbeafe; color: #1e40af; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">Enhanced Mode Active</div>
            </div>

            <div style="text-align: center; padding: 2rem; color: #6b7280;">
                <p>💬 AI agents are ready to discuss your content strategy</p>
                <p>Start generation to see live discussions!</p>

                <div style="margin-top: 1.5rem;">
                    <div class="discussion-pair">
                        <strong>📝 ScriptMaster ↔ 🧠 ViralismSpecialist</strong>
                        <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                            Script optimization with viral psychology
                        </div>
                    </div>

                    <div class="discussion-pair">
                        <strong>🎯 ContentSpecialist ↔ 🎨 VisualDirector</strong>
                        <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                            Content strategy meets visual storytelling
                        </div>
                    </div>

                    <div class="discussion-pair">
                        <strong>🎵 AudioEngineer ↔ ✂️ VideoEditor</strong>
                        <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                            Audio-visual integration and final assembly
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """"

    def _create_progress_display(self, progress: int, message: str):
        """Create progress display HTML"""
        return """"
        <div class="progress-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: white;">Progress: {progress}%</h3>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">{message}</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%;"></div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold;">7</div>
                <div style="color: #6b7280; font-size: 0.9rem;">AI Agents</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold;">3</div>
                <div style="color: #6b7280; font-size: 0.9rem;">Discussions</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold;">{progress}%</div>
                <div style="color: #6b7280; font-size: 0.9rem;">Progress</div>
            </div>
        </div>
        """"

    def _create_agent_status(self, progress: int):
        """Create agent status based on progress"""
        agents = [
            ("ScriptMaster", "📝", 0, 30),
            ("ViralismSpecialist", "🧠", 0, 30),
            ("ContentSpecialist", "🎯", 30, 50),
            ("VisualDirector", "🎨", 30, 50),
            ("AudioEngineer", "🎵", 50, 70),
            ("VideoEditor", "✂️", 50, 85),
            ("QualityController", "🛡️", 85, 100)
        ]

        html = '<div class="agent-status-grid">'
        for name, emoji, start, end in agents:
            if progress < start:
                status_class = ""
                status_text = "⏳ Waiting"
                status_color = "#9ca3a"
            elif start <= progress < end:
                status_class = "active"
                status_text = "🔄 Active"
                status_color = "#10b981"
            else:
                status_class = "completed"
                status_text = "✅ Completed"
                status_color = "#059669"

            html += '''
            <div class="agent-card {status_class}">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem;">{emoji}</span>
                    <strong>{name}</strong>
                </div>
                <div style="margin-top: 0.5rem;">
                    <span style="color: {status_color}; font-size: 0.8rem; font-weight: 500;">{status_text}</span>
                </div>
            </div>
            '''
        html += '</div>'
        return html

    def _create_discussion_display(self, progress_info: dict):
        """Create discussion display based on progress"""
        discussions_completed = progress_info.get('discussions_completed', 0)

        pairs = [
            ("ScriptMaster", "ViralismSpecialist", "Script & Viral Psychology", "📝", "🧠"),
            ("ContentSpecialist", "VisualDirector", "Content Strategy & Visuals", "🎯", "🎨"),
            ("AudioEngineer", "VideoEditor", "Audio-Visual Integration", "🎵", "✂️")
        ]

        html = """"
        <div class="discussion-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3>🤝 AI Agent Discussions</h3>
                <div style="background: #dbeafe; color: #1e40af; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">Enhanced Mode Active</div>
            </div>

            <div style="margin-bottom: 1rem;">
                <strong>Discussions Completed: {discussions_completed}/3</strong>
            </div>
        """"

        for i, (agent1, agent2, topic, emoji1, emoji2) in enumerate(pairs):
            if discussions_completed > i:
                status_class = "completed"
                status_text = "✅ Completed"
            elif discussions_completed == i:
                status_class = "active"
                status_text = "🔄 In Progress"
            else:
                status_class = ""
                status_text = "⏳ Waiting"

            html += '''
            <div class="discussion-pair {status_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{emoji1} {agent1} ↔ {emoji2} {agent2}</strong>
                    <span style="font-size: 0.8rem; font-weight: 500;">{status_text}</span>
                </div>
                <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                    {topic}
                </div>
            </div>
            '''

        html += '</div>'
        return html

    def _create_download_section(self, result: dict):
        """Create download section with proper video file handling"""
        if not result or not result.get('success'):
            return "<p>No download available</p>"

        video_path = result.get('final_video_path', '')
        session_id = result.get('session_id', 'N/A')
        agents_used = result.get('agents_used', 7)
        discussions = result.get('discussions_conducted', 3)

        # Create actual file download link
        download_link = f"/file={video_path}" if video_path and os.path.exists(video_path) else "#"

        return """"
        <div style="background: #dcfce7; border: 1px solid #16a34a; border-radius: 12px; padding: 2rem; margin: 2rem 0;">
            <h3 style="color: #166534; margin-bottom: 1rem;">📁 Download & Results</h3>
            
            <div style="margin-bottom: 1.5rem;">
                <a href="{download_link}" download class="download-button">
                    🎬 Download Video
                </a>
                <a href="#" class="download-button" style="background: #3b82f6;">
                    📊 View Analytics
                </a>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3",
                1fr); gap: 1rem; text-align: center; padding-top: 1rem; border-top: 1px solid #16a34a;">"
                <div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #166534;">{agents_used}</div>
                    <div style="font-size: 0.9rem; color: #6b7280;">AI Agents</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #166534;">{discussions}</div>
                    <div style="font-size: 0.9rem; color: #6b7280;">Discussions</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #166534;">{session_id[:8]}...</div>
                    <div style="font-size: 0.9rem; color: #6b7280;">Session ID</div>
                </div>
            </div>
            
            {f'<div style="margin-top: 1rem; padding: 0.5rem; background: #f0fdf4; border-radius: 6px; font-size: 0.9rem;"><strong>Path:</strong> {video_path}</div>' if video_path else ''}
        </div>
        """"


def launch_enhanced_ultimate_ui():
    """Launch the enhanced ultimate UI with all features"""
    print("🎬 Starting Enhanced Ultimate Modern Video Generator UI...")
    print("🎯 Enhanced AI discussions enabled by default")
    print("⚡ Force generation options available")
    print("📈 Trending analysis for ContentSpecialist")
    print("🔄 Real-time progress and discussion updates")
    print("📁 Proper video download and display")
    print("📍 Access at: http://localhost:7860")
    print()

    ui = EnhancedModernVideoGeneratorUI()
    interface = ui.create_interface()

    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        debug=False
    )


def main():
    """Main entry point for the Enhanced Ultimate Modern Video Generator UI"""
    print("🎬 Enhanced Ultimate Modern Video Generator v2.2")
    print("🎯 Enhanced AI discussions enabled by default")
    print("⚡ Force generation options available")
    print("📈 Trending analysis for ContentSpecialist")
    print("🔄 Real-time progress and discussion updates")
    print("📁 Proper video download and display")
    print("📍 Access at: http://localhost:7860")
    print()
    launch_enhanced_ultimate_ui()


if __name__ == "__main__":
    main()
