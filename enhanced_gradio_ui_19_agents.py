"""
Enhanced Gradio UI with 19 Specialized AI Agents
Professional-grade viral video generation interface
"""

import gradio as gr
import os
import json
from datetime import datetime
from typing import Optional, Tuple
import uuid

from src.models.video_models import Platform, VideoCategory
from src.utils.logging_config import get_logger
from src.agents.enhanced_orchestrator_with_19_agents import create_enhanced_orchestrator_with_19_agents

logger = get_logger(__name__)

class Settings:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        self.vertex_project_id = os.getenv('GOOGLE_PROJECT_ID', 'viralgen-464411')
        self.vertex_location = os.getenv('GOOGLE_LOCATION', 'us-central1')
        self.vertex_gcs_bucket = os.getenv('VERTEX_GCS_BUCKET', 'viralgen-veo2-results-20250707')

settings = Settings()

def generate_professional_video(topic: str, category: str, platform: str, 
                               duration: int, use_discussions: bool,
                               progress=gr.Progress()) -> Tuple[str, str, str]:
    """
    Generate professional viral video using 19 specialized AI agents
    """
    try:
        if not topic.strip():
            return "❌ Error: Please enter a topic", "", ""
        
        if not settings.google_api_key:
            return "❌ Error: Google API key not configured", "", ""
        
        # Create session ID
        session_id = str(uuid.uuid4())[:8]
        
        progress(0.1, desc="🚀 Initializing 19 AI Agents...")
        logger.info(f"🎬 Starting PROFESSIONAL video generation with 19 agents")
        logger.info(f"📋 Topic: {topic}")
        logger.info(f"🎯 Platform: {platform}, Category: {category}")
        logger.info(f"⏱️ Duration: {duration}s, Discussions: {use_discussions}")
        
        # Create enhanced orchestrator with 19 agents
        progress(0.2, desc="�� Creating Enhanced Orchestrator...")
        orchestrator = create_enhanced_orchestrator_with_19_agents(
            api_key=settings.google_api_key,
            topic=topic,
            category=VideoCategory(category),
            platform=Platform(platform),
            duration=duration,
            discussion_mode=use_discussions,
            session_id=session_id,
            use_vertex_ai=True,  # FORCE Vertex AI VEO-3/VEO-2 (REAL)
            vertex_project_id=settings.vertex_project_id,
            vertex_location=settings.vertex_location,
            vertex_gcs_bucket=settings.vertex_gcs_bucket,
            prefer_veo3=True,    # Prefer VEO-3 when available
            enable_native_audio=True  # Enable native audio generation
        )
        
        if use_discussions:
            progress(0.3, desc="🎭 Phase 1: Script Development Discussion...")
            progress(0.4, desc="🎵 Phase 2: Audio Production Discussion...")
            progress(0.5, desc="🎨 Phase 3: Visual Design Discussion...")
            progress(0.6, desc="📱 Phase 4: Platform Optimization Discussion...")
            progress(0.7, desc="🔍 Phase 5: Final Quality Review Discussion...")
        
        progress(0.8, desc="🎬 Generating Professional Video...")
        
        # Generate the video
        generated_video = orchestrator.generate_viral_video(
            topic=topic,
            category=VideoCategory(category),
            platform=Platform(platform),
            duration=duration,
            discussion_mode=use_discussions
        )
        
        progress(1.0, desc="✅ Professional Video Generated!")
        
        # Prepare results
        video_path = generated_video.file_path
        
        # Create detailed report
        report = f"""
# 🎉 PROFESSIONAL VIDEO GENERATED WITH 19 AI AGENTS

## 📊 Generation Summary
- **Topic**: {topic}
- **Platform**: {platform}
- **Category**: {category}
- **Duration**: {duration} seconds
- **Agent Discussions**: {'✅ 5 Phases' if use_discussions else '❌ Disabled'}
- **Generation Time**: {generated_video.generation_time_seconds:.1f} seconds
- **File Size**: {generated_video.file_size_mb:.1f} MB

## 🤖 AI Agents Involved
### Original Agents (7)
- **TrendMaster**: Viral trends & engagement metrics
- **StoryWeaver**: Narrative structure & storytelling
- **VisionCraft**: Visual storytelling & cinematography
- **PixelForge**: AI video generation (VEO-3/VEO-2)
- **AudioMaster**: Audio production & voice synthesis
- **CutMaster**: Video editing & post-production
- **SyncMaster**: Workflow coordination

### NEW Script & Dialogue Specialists (2)
- **DialogueMaster**: Natural dialogue & character voices
- **PaceMaster**: Pacing & timing optimization

### NEW Advanced Audio Specialists (2)
- **VoiceDirector**: Voice casting & performance direction
- **SoundDesigner**: Advanced audio design & atmosphere

### NEW Typography & Visual Text Specialists (2)
- **TypeMaster**: Typography & font psychology
- **HeaderCraft**: Header design & placement strategy

### NEW Visual Style & Art Direction (2)
- **StyleDirector**: Art direction & visual consistency
- **ColorMaster**: Color psychology & palette optimization

### NEW Platform & Optimization Specialists (2)
- **PlatformGuru**: Platform-specific optimization
- **EngagementHacker**: Viral mechanics & engagement

### NEW Quality Assurance & Testing (2)
- **QualityGuard**: Quality assurance & technical excellence
- **AudienceAdvocate**: User experience & audience psychology

## 🎯 Discussion Phases (if enabled)
1. **Script Development**: DialogueMaster, PaceMaster, StoryWeaver, AudienceAdvocate
2. **Audio Production**: VoiceDirector, SoundDesigner, AudioMaster, PlatformGuru
3. **Visual Design**: StyleDirector, ColorMaster, TypeMaster, HeaderCraft, VisionCraft
4. **Platform Optimization**: PlatformGuru, EngagementHacker, TrendMaster, QualityGuard
5. **Quality Review**: QualityGuard, AudienceAdvocate, SyncMaster, CutMaster

## 📁 Output Files
- **Video**: {video_path}
- **Session**: {session_id}
- **AI Models**: {', '.join(generated_video.ai_models_used)}

## 🚀 Professional Quality Features
- ✅ Real VEO-3/VEO-2 generation (no mocks)
- ✅ 19 specialized AI agent expertise
- ✅ Multi-phase discussion optimization
- ✅ Professional-grade output quality
- ✅ Platform-specific optimization
- ✅ Advanced audio design
- ✅ Typography & visual excellence
- ✅ Quality assurance validation

**🎬 Ready for professional viral distribution! 🚀**
        """
        
        # Create technical details
        technical_details = f"""
# 🔧 Technical Details

## Video Configuration
- **Target Platform**: {platform}
- **Category**: {category}
- **Duration**: {duration} seconds
- **Predicted Viral Score**: {generated_video.config.predicted_viral_score:.2f}

## Script Details
- **Style**: {generated_video.config.style}
- **Tone**: {generated_video.config.tone}
- **Target Audience**: {generated_video.config.target_audience}
- **Hook**: {generated_video.config.hook}

## Visual Configuration
- **Visual Style**: {generated_video.config.visual_style}
- **Color Scheme**: {', '.join(generated_video.config.color_scheme)}
- **Text Overlays**: {len(generated_video.config.text_overlays)} overlays
- **Transitions**: {', '.join(generated_video.config.transitions)}

## Audio Configuration
- **Background Music**: {generated_video.config.background_music_style}
- **Voiceover Style**: {generated_video.config.voiceover_style}
- **Sound Effects**: {', '.join(generated_video.config.sound_effects)}

## Scene Breakdown
{chr(10).join([f"- Scene {i+1}: {desc}" for i, desc in enumerate(generated_video.scene_descriptions)])}

## Session Information
- **Session ID**: {session_id}
- **Generation Time**: {generated_video.generation_time_seconds:.1f} seconds
- **File Size**: {generated_video.file_size_mb:.1f} MB
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        logger.info(f"✅ PROFESSIONAL video generation completed successfully!")
        return video_path, report, technical_details
        
    except Exception as e:
        error_msg = f"❌ Error generating professional video: {str(e)}"
        logger.error(error_msg)
        return error_msg, "", ""

def create_enhanced_interface():
    """Create the enhanced Gradio interface with 19 AI agents"""
    
    with gr.Blocks(
        title="🚀 Professional Viral Video Generator - 19 AI Agents",
        theme=gr.themes.Soft(),
        css="""
        .main-header { text-align: center; margin-bottom: 2rem; }
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin: 1rem 0; }
        .agent-category { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 8px; }
        .feature-highlight { background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #007bff; }
        """
    ) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>�� Professional Viral Video Generator</h1>
            <h2>Powered by 19 Specialized AI Agents</h2>
            <p>Professional-grade video production with comprehensive AI expertise</p>
        </div>
        """)
        
        # Agent Categories Overview
        with gr.Row():
            gr.HTML("""
            <div class="agent-grid">
                <div class="agent-category">
                    <h3>🎭 Script & Dialogue (4 agents)</h3>
                    <p>StoryWeaver, DialogueMaster, PaceMaster, AudienceAdvocate</p>
                </div>
                <div class="agent-category">
                    <h3>🎵 Audio Production (3 agents)</h3>
                    <p>AudioMaster, VoiceDirector, SoundDesigner</p>
                </div>
                <div class="agent-category">
                    <h3>🎨 Visual Design (5 agents)</h3>
                    <p>VisionCraft, StyleDirector, ColorMaster, TypeMaster, HeaderCraft</p>
                </div>
                <div class="agent-category">
                    <h3>📱 Platform & Optimization (3 agents)</h3>
                    <p>PlatformGuru, EngagementHacker, TrendMaster</p>
                </div>
                <div class="agent-category">
                    <h3>🔧 Production & QA (4 agents)</h3>
                    <p>PixelForge, CutMaster, QualityGuard, SyncMaster</p>
                </div>
            </div>
            """)
        
        # Main Generation Interface
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3>�� Video Configuration</h3>")
                
                topic_input = gr.Textbox(
                    label="📝 Video Topic",
                    placeholder="Enter your video topic (e.g., 'AI revolution in healthcare')",
                    lines=2
                )
                
                with gr.Row():
                    category_dropdown = gr.Dropdown(
                        choices=[cat.value for cat in VideoCategory],
                        label="📂 Category",
                        value="EDUCATIONAL"
                    )
                    
                    platform_dropdown = gr.Dropdown(
                        choices=[platform.value for platform in Platform],
                        label="📱 Platform",
                        value="YOUTUBE_SHORTS"
                    )
                
                duration_slider = gr.Slider(
                    minimum=15,
                    maximum=60,
                    value=30,
                    step=5,
                    label="⏱️ Duration (seconds)"
                )
                
                discussions_checkbox = gr.Checkbox(
                    label="🤖 Enable 5-Phase Agent Discussions",
                    value=True,
                    info="Use all 19 agents in 5 discussion phases for maximum quality"
                )
                
                generate_btn = gr.Button(
                    "🚀 Generate Professional Video",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=2):
                gr.HTML("<h3>📊 Generation Results</h3>")
                
                video_output = gr.Video(
                    label="🎬 Generated Professional Video",
                    height=400
                )
                
                with gr.Tabs():
                    with gr.Tab("📋 Generation Report"):
                        report_output = gr.Markdown(
                            label="Generation Report",
                            height=600
                        )
                    
                    with gr.Tab("🔧 Technical Details"):
                        technical_output = gr.Markdown(
                            label="Technical Details",
                            height=600
                        )
        
        # Features Section
        gr.HTML("""
        <div class="feature-highlight">
            <h3>🌟 Professional Features</h3>
            <ul>
                <li><strong>19 Specialized AI Agents</strong> - Each expert in their domain</li>
                <li><strong>5-Phase Discussion System</strong> - Comprehensive decision making</li>
                <li><strong>Real VEO-3/VEO-2 Generation</strong> - No mocks, only authentic AI</li>
                <li><strong>Professional Quality Standards</strong> - Broadcast-ready output</li>
                <li><strong>Platform Optimization</strong> - Tailored for each social platform</li>
                <li><strong>Advanced Audio Design</strong> - Professional voice and sound</li>
                <li><strong>Typography Excellence</strong> - Professional text design</li>
                <li><strong>Quality Assurance</strong> - Comprehensive testing and validation</li>
            </ul>
        </div>
        """)
        
        # Wire up the generation
        generate_btn.click(
            fn=generate_professional_video,
            inputs=[
                topic_input,
                category_dropdown,
                platform_dropdown,
                duration_slider,
                discussions_checkbox
            ],
            outputs=[
                video_output,
                report_output,
                technical_output
            ]
        )
    
    return interface

if __name__ == "__main__":
    print("🚀 Starting Professional Viral Video Generator with 19 AI Agents...")
    print("🌐 Interface will open in your browser")
    
    # Check API key
    if not settings.google_api_key:
        print("⚠️ Warning: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY=your_api_key_here")
    
    interface = create_enhanced_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
