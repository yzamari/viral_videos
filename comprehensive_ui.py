#!/usr/bin/env python3
"""
Comprehensive Viral Video Generator UI
Complete interface with all options, real-time monitoring, and AI agent discussion visualization
"""

import gradio as gr
import os
import sys
import json
import time
import threading
import subprocess
import tempfile
import uuid
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from PIL import Image
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Global state for real-time updates
current_session = {"id": None, "status": "idle", "progress": 0, "message": "Ready", "start_time": None}
generation_process = None
session_data = {}

def get_all_app_flags():
    """Get all available command line flags from main.py"""
    return {
        'topic': {'type': 'text', 'required': True, 'help': 'Video topic'},
        'duration': {'type': 'number', 'default': 15, 'min': 5, 'max': 60, 'help': 'Duration in seconds'},
        'platform': {'type': 'dropdown', 'choices': ['youtube', 'tiktok', 'instagram', 'twitter'], 'default': 'youtube', 'help': 'Target platform'},
        'category': {'type': 'dropdown', 'choices': ['comedy', 'educational', 'news', 'entertainment', 'lifestyle'], 'default': 'comedy', 'help': 'Video category'},
        'discussions': {'type': 'dropdown', 'choices': ['light', 'standard', 'deep'], 'default': 'standard', 'help': 'AI discussion depth'},
        'style': {'type': 'dropdown', 'choices': ['viral', 'professional', 'casual', 'dramatic'], 'default': 'viral', 'help': 'Video style'},
        'tone': {'type': 'dropdown', 'choices': ['engaging', 'informative', 'humorous', 'serious'], 'default': 'engaging', 'help': 'Content tone'},
        'image_only': {'type': 'checkbox', 'default': False, 'help': 'Generate image-only video (no real video clips)'},
        'frame_continuity': {'type': 'checkbox', 'default': True, 'help': 'Enable frame continuity between clips'},
        'realistic_audio': {'type': 'checkbox', 'default': True, 'help': 'Use realistic neural voice synthesis'},
        'use_trending': {'type': 'checkbox', 'default': True, 'help': 'Incorporate trending elements'},
        'enhance_prompts': {'type': 'checkbox', 'default': True, 'help': 'Use AI prompt enhancement'},
        'quota_optimization': {'type': 'checkbox', 'default': True, 'help': 'Enable quota optimization'},
        'multilingual': {'type': 'checkbox', 'default': False, 'help': 'Generate multilingual versions'},
        'languages': {'type': 'text', 'default': '', 'help': 'Additional languages (comma-separated)'},
        'custom_voice': {'type': 'text', 'default': '', 'help': 'Custom voice settings'},
        'background_music': {'type': 'checkbox', 'default': False, 'help': 'Add background music'},
        'text_overlays': {'type': 'checkbox', 'default': True, 'help': 'Add text overlays'},
        'emoji_style': {'type': 'checkbox', 'default': True, 'help': 'Use emoji in text overlays'},
        'viral_hooks': {'type': 'checkbox', 'default': True, 'help': 'Use viral hooks and patterns'},
        'trending_topics': {'type': 'checkbox', 'default': True, 'help': 'Incorporate trending topics'},
        'audience_targeting': {'type': 'dropdown', 'choices': ['general', 'gen_z', 'millennials', 'gen_x', 'boomers'], 'default': 'general', 'help': 'Target audience'},
        'content_rating': {'type': 'dropdown', 'choices': ['family_friendly', 'teen', 'mature'], 'default': 'family_friendly', 'help': 'Content rating'},
        'optimization_level': {'type': 'dropdown', 'choices': ['basic', 'standard', 'aggressive'], 'default': 'standard', 'help': 'Optimization level'},
        'debug_mode': {'type': 'checkbox', 'default': False, 'help': 'Enable debug logging'},
        'save_intermediates': {'type': 'checkbox', 'default': True, 'help': 'Save intermediate files'},
        'gpu_acceleration': {'type': 'checkbox', 'default': False, 'help': 'Use GPU acceleration if available'},
        'high_quality': {'type': 'checkbox', 'default': True, 'help': 'Enable high quality mode'},
        'fast_mode': {'type': 'checkbox', 'default': False, 'help': 'Enable fast generation mode'},
    }

def start_generation(topic, duration, platform, category, discussions, style, tone, 
                    image_only, frame_continuity, realistic_audio, use_trending, 
                    enhance_prompts, quota_optimization, multilingual, languages,
                    custom_voice, background_music, text_overlays, emoji_style,
                    viral_hooks, trending_topics, audience_targeting, content_rating,
                    optimization_level, debug_mode, save_intermediates, 
                    gpu_acceleration, high_quality, fast_mode):
    """Start video generation with all parameters"""
    
    global current_session, generation_process
    
    if not topic.strip():
        return "❌ Please enter a topic", get_status_display(), "", "", ""
    
    # Create session ID
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    current_session = {
        "id": session_id,
        "status": "starting",
        "progress": 0,
        "message": f"Starting generation for '{topic}'",
        "start_time": datetime.now(),
        "topic": topic
    }
    
    # Build command with all parameters
    cmd = [
        "python", "main.py", "generate",
        "--topic", topic,
        "--duration", str(duration),
        "--platform", platform,
        "--category", category,
        "--discussions", discussions,
        "--style", style,
        "--tone", tone
    ]
    
    # Add boolean flags
    if image_only:
        cmd.append("--image-only")
    if not frame_continuity:
        cmd.append("--no-frame-continuity")
    if not realistic_audio:
        cmd.append("--no-realistic-audio")
    if not use_trending:
        cmd.append("--no-trending")
    if not enhance_prompts:
        cmd.append("--no-enhance-prompts")
    if not quota_optimization:
        cmd.append("--no-quota-optimization")
    if multilingual and languages:
        cmd.extend(["--languages", languages])
    if custom_voice:
        cmd.extend(["--custom-voice", custom_voice])
    if background_music:
        cmd.append("--background-music")
    if not text_overlays:
        cmd.append("--no-text-overlays")
    if not emoji_style:
        cmd.append("--no-emoji")
    if not viral_hooks:
        cmd.append("--no-viral-hooks")
    if not trending_topics:
        cmd.append("--no-trending-topics")
    if audience_targeting != "general":
        cmd.extend(["--audience", audience_targeting])
    if content_rating != "family_friendly":
        cmd.extend(["--rating", content_rating])
    if optimization_level != "standard":
        cmd.extend(["--optimization", optimization_level])
    if debug_mode:
        cmd.append("--debug")
    if not save_intermediates:
        cmd.append("--no-save-intermediates")
    if gpu_acceleration:
        cmd.append("--gpu")
    if not high_quality:
        cmd.append("--no-high-quality")
    if fast_mode:
        cmd.append("--fast")
    
    # Start generation in background
    def run_generation():
        global generation_process, current_session
        try:
            current_session["status"] = "running"
            current_session["message"] = "Executing generation command..."
            
            generation_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress
            stdout, stderr = generation_process.communicate()
            
            if generation_process.returncode == 0:
                current_session["status"] = "completed"
                current_session["progress"] = 100
                current_session["message"] = "✅ Generation completed successfully!"
                
                # Find the generated session folder
                outputs_dir = Path("outputs")
                if outputs_dir.exists():
                    session_folders = sorted([
                        d for d in outputs_dir.iterdir() 
                        if d.is_dir() and d.name.startswith("session_")
                    ], key=lambda x: x.stat().st_mtime, reverse=True)
                    
                    if session_folders:
                        current_session["folder"] = str(session_folders[0])
                        load_session_data(current_session["folder"])
            else:
                current_session["status"] = "error"
                current_session["message"] = f"❌ Generation failed: {stderr}"
                
        except Exception as e:
            current_session["status"] = "error"
            current_session["message"] = f"❌ Error: {str(e)}"
    
    thread = threading.Thread(target=run_generation)
    thread.daemon = True
    thread.start()
    
    return (f"🚀 Started generation for '{topic}'", 
            get_status_display(), 
            get_session_info(),
            get_ai_discussions_display(),
            get_media_gallery())

def get_status_display():
    """Get formatted status display"""
    global current_session
    
    status_emoji = {
        "idle": "⏸️",
        "starting": "🚀",
        "running": "⚡",
        "completed": "✅",
        "error": "❌"
    }
    
    emoji = status_emoji.get(current_session["status"], "❓")
    message = current_session["message"]
    progress = current_session.get("progress", 0)
    
    if current_session["start_time"]:
        elapsed = datetime.now() - current_session["start_time"]
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        return f"{emoji} {message} ({progress}%) | Elapsed: {elapsed_str}"
    else:
        return f"{emoji} {message} ({progress}%)"

def load_session_data(session_folder):
    """Load all data from a session folder"""
    global session_data
    
    session_path = Path(session_folder)
    if not session_path.exists():
        return
    
    session_data = {
        "folder": session_folder,
        "videos": [],
        "images": [],
        "audio": [],
        "scripts": [],
        "discussions": [],
        "analysis": None
    }
    
    # Find all files
    for file_path in session_path.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(session_path)
            
            if file_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
                session_data["videos"].append(str(file_path))
            elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                session_data["images"].append(str(file_path))
            elif file_path.suffix.lower() in ['.mp3', '.wav', '.aac']:
                session_data["audio"].append(str(file_path))
            elif file_path.suffix.lower() == '.txt' and 'script' in file_path.name:
                session_data["scripts"].append(str(file_path))
            elif file_path.suffix.lower() == '.json' and 'discussion' in file_path.name:
                session_data["discussions"].append(str(file_path))
            elif file_path.name == 'video_analysis.txt':
                session_data["analysis"] = str(file_path)

def get_session_info():
    """Get session information display"""
    global current_session, session_data
    
    if not current_session.get("id"):
        return "No active session"
    
    info = f"📁 **Session:** {current_session['id']}\n"
    info += f"🎯 **Topic:** {current_session.get('topic', 'N/A')}\n"
    info += f"📊 **Status:** {current_session['status']}\n"
    
    if current_session.get("folder") and session_data:
        info += f"\n📂 **Generated Files:**\n"
        info += f"🎬 Videos: {len(session_data.get('videos', []))}\n"
        info += f"🖼️ Images: {len(session_data.get('images', []))}\n"
        info += f"🎵 Audio: {len(session_data.get('audio', []))}\n"
        info += f"📝 Scripts: {len(session_data.get('scripts', []))}\n"
        info += f"🤖 AI Discussions: {len(session_data.get('discussions', []))}\n"
    
    return info

def get_ai_discussions_display():
    """Get AI discussions visualization"""
    global session_data
    
    if not session_data or not session_data.get("discussions"):
        return "No AI discussions available"
    
    discussions_html = "<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;'>"
    discussions_html += "<h3>🤖 AI Agent Discussions</h3>"
    
    for discussion_file in session_data["discussions"]:
        try:
            with open(discussion_file, 'r') as f:
                discussion = json.load(f)
            
            topic_id = discussion.get("topic_id", "Unknown")
            consensus = discussion.get("consensus_level", 0)
            participants = discussion.get("participating_agents", [])
            
            discussions_html += f"<div style='background: rgba(255,255,255,0.1); margin: 10px 0; padding: 15px; border-radius: 8px;'>"
            discussions_html += f"<h4>📋 {topic_id.replace('_', ' ').title()}</h4>"
            discussions_html += f"<p><strong>Consensus:</strong> {consensus:.2f} ({consensus*100:.0f}%)</p>"
            discussions_html += f"<p><strong>Participants:</strong> {', '.join(participants)}</p>"
            
            # Add consensus bar
            consensus_color = "green" if consensus > 0.7 else "orange" if consensus > 0.5 else "red"
            discussions_html += f"<div style='background: rgba(255,255,255,0.2); border-radius: 10px; height: 10px; overflow: hidden;'>"
            discussions_html += f"<div style='background: {consensus_color}; height: 100%; width: {consensus*100}%; transition: width 0.3s;'></div>"
            discussions_html += "</div>"
            
            # Add key insights
            if "key_insights" in discussion:
                discussions_html += "<details style='margin-top: 10px;'>"
                discussions_html += "<summary style='cursor: pointer;'>💡 Key Insights</summary>"
                discussions_html += "<ul style='margin: 10px 0;'>"
                for insight in discussion["key_insights"][:3]:  # Show top 3 insights
                    discussions_html += f"<li style='margin: 5px 0;'>{insight[:100]}...</li>"
                discussions_html += "</ul></details>"
            
            discussions_html += "</div>"
            
        except Exception as e:
            discussions_html += f"<p>❌ Error loading discussion: {e}</p>"
    
    discussions_html += "</div>"
    return discussions_html

def get_media_gallery():
    """Get media gallery with images and videos"""
    global session_data
    
    if not session_data:
        return "No media available"
    
    gallery_html = "<div style='background: #f8f9fa; padding: 20px; border-radius: 10px;'>"
    gallery_html += "<h3>🎨 Media Gallery</h3>"
    
    # Videos section
    if session_data.get("videos"):
        gallery_html += "<h4>🎬 Generated Videos</h4>"
        gallery_html += "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
        for video_path in session_data["videos"]:
            video_name = Path(video_path).name
            gallery_html += f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px;'>"
            gallery_html += f"<video width='200' height='150' controls>"
            gallery_html += f"<source src='{video_path}' type='video/mp4'>"
            gallery_html += f"</video>"
            gallery_html += f"<p style='margin: 5px 0; font-size: 12px;'>{video_name}</p>"
            gallery_html += "</div>"
        gallery_html += "</div>"
    
    # Images section
    if session_data.get("images"):
        gallery_html += "<h4>🖼️ Generated Images</h4>"
        gallery_html += "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
        for image_path in session_data["images"]:
            image_name = Path(image_path).name
            gallery_html += f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px;'>"
            gallery_html += f"<img src='{image_path}' width='150' height='150' style='object-fit: cover;'>"
            gallery_html += f"<p style='margin: 5px 0; font-size: 12px;'>{image_name}</p>"
            gallery_html += "</div>"
        gallery_html += "</div>"
    
    # Audio section
    if session_data.get("audio"):
        gallery_html += "<h4>🎵 Generated Audio</h4>"
        for audio_path in session_data["audio"]:
            audio_name = Path(audio_path).name
            gallery_html += f"<div style='margin: 10px 0;'>"
            gallery_html += f"<audio controls style='width: 100%;'>"
            gallery_html += f"<source src='{audio_path}' type='audio/mpeg'>"
            gallery_html += f"</audio>"
            gallery_html += f"<p style='margin: 5px 0; font-size: 12px;'>{audio_name}</p>"
            gallery_html += "</div>"
    
    gallery_html += "</div>"
    return gallery_html

def get_recent_sessions():
    """Get list of recent sessions"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return "No sessions found"
    
    session_dirs = [
        d for d in outputs_dir.iterdir() 
        if d.is_dir() and d.name.startswith("session_")
    ]
    
    if not session_dirs:
        return "No sessions found"
    
    # Sort by creation time (newest first)
    session_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    sessions_html = "<div style='max-height: 400px; overflow-y: auto;'>"
    sessions_html += "<h4>📁 Recent Sessions</h4>"
    
    for session_dir in session_dirs[:10]:  # Show last 10 sessions
        session_name = session_dir.name
        created_time = datetime.fromtimestamp(session_dir.stat().st_mtime)
        
        # Count files in session
        video_count = len(list(session_dir.glob("**/*.mp4")))
        image_count = len(list(session_dir.glob("**/*.jpg")) + list(session_dir.glob("**/*.png")))
        discussion_count = len(list(session_dir.glob("**/discussion_*.json")))
        
        sessions_html += f"<div style='border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; background: white;'>"
        sessions_html += f"<h5 style='margin: 0 0 10px 0; color: #333;'>{session_name}</h5>"
        sessions_html += f"<p style='margin: 5px 0; color: #666; font-size: 12px;'>Created: {created_time.strftime('%Y-%m-%d %H:%M:%S')}</p>"
        sessions_html += f"<div style='display: flex; gap: 15px; margin-top: 10px;'>"
        sessions_html += f"<span style='background: #e3f2fd; padding: 4px 8px; border-radius: 4px; font-size: 11px;'>🎬 {video_count} videos</span>"
        sessions_html += f"<span style='background: #f3e5f5; padding: 4px 8px; border-radius: 4px; font-size: 11px;'>🖼️ {image_count} images</span>"
        sessions_html += f"<span style='background: #e8f5e8; padding: 4px 8px; border-radius: 4px; font-size: 11px;'>🤖 {discussion_count} discussions</span>"
        sessions_html += "</div>"
        sessions_html += "</div>"
    
    sessions_html += "</div>"
    return sessions_html

def load_session(session_name):
    """Load a specific session"""
    session_path = Path("outputs") / session_name
    if session_path.exists():
        load_session_data(str(session_path))
        return get_session_info(), get_ai_discussions_display(), get_media_gallery()
    return "Session not found", "", ""

def create_comprehensive_interface():
    """Create the comprehensive Gradio interface"""
    
    # Get all app flags
    app_flags = get_all_app_flags()
    
    with gr.Blocks(
        title="🎬 Viral Video Generator - Comprehensive Interface",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        .status-display {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .media-gallery {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        """
    ) as demo:
        
        gr.Markdown("# 🎬 Viral Video Generator - Comprehensive Interface")
        gr.Markdown("Complete control panel with all options, real-time monitoring, and AI agent visualization")
        
        with gr.Tab("🎬 Generate Video"):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 📋 Generation Parameters")
                    
                    # Create input components for all flags
                    inputs = {}
                    
                    # Essential parameters
                    with gr.Group():
                        gr.Markdown("#### Essential Settings")
                        inputs['topic'] = gr.Textbox(
                            label="Video Topic",
                            placeholder="Enter your video topic (e.g., 'USA political news test with real images')",
                            lines=2
                        )
                        
                        with gr.Row():
                            inputs['duration'] = gr.Slider(
                                minimum=5, maximum=60, value=15, step=1,
                                label="Duration (seconds)"
                            )
                            inputs['platform'] = gr.Dropdown(
                                choices=app_flags['platform']['choices'],
                                value=app_flags['platform']['default'],
                                label="Platform"
                            )
                    
                    # Content settings
                    with gr.Group():
                        gr.Markdown("#### Content Settings")
                        with gr.Row():
                            inputs['category'] = gr.Dropdown(
                                choices=app_flags['category']['choices'],
                                value=app_flags['category']['default'],
                                label="Category"
                            )
                            inputs['style'] = gr.Dropdown(
                                choices=app_flags['style']['choices'],
                                value=app_flags['style']['default'],
                                label="Style"
                            )
                            inputs['tone'] = gr.Dropdown(
                                choices=app_flags['tone']['choices'],
                                value=app_flags['tone']['default'],
                                label="Tone"
                            )
                    
                    # AI settings
                    with gr.Group():
                        gr.Markdown("#### AI & Orchestration Settings")
                        inputs['discussions'] = gr.Dropdown(
                            choices=app_flags['discussions']['choices'],
                            value=app_flags['discussions']['default'],
                            label="AI Discussion Depth"
                        )
                        
                        with gr.Row():
                            inputs['image_only'] = gr.Checkbox(
                                label="Image-only mode",
                                value=app_flags['image_only']['default']
                            )
                            inputs['frame_continuity'] = gr.Checkbox(
                                label="Frame continuity",
                                value=app_flags['frame_continuity']['default']
                            )
                            inputs['realistic_audio'] = gr.Checkbox(
                                label="Realistic audio",
                                value=app_flags['realistic_audio']['default']
                            )
                    
                    # Advanced features
                    with gr.Group():
                        gr.Markdown("#### Advanced Features")
                        with gr.Row():
                            inputs['use_trending'] = gr.Checkbox(
                                label="Use trending",
                                value=app_flags['use_trending']['default']
                            )
                            inputs['enhance_prompts'] = gr.Checkbox(
                                label="Enhance prompts",
                                value=app_flags['enhance_prompts']['default']
                            )
                            inputs['quota_optimization'] = gr.Checkbox(
                                label="Quota optimization",
                                value=app_flags['quota_optimization']['default']
                            )
                        
                        with gr.Row():
                            inputs['viral_hooks'] = gr.Checkbox(
                                label="Viral hooks",
                                value=app_flags['viral_hooks']['default']
                            )
                            inputs['trending_topics'] = gr.Checkbox(
                                label="Trending topics",
                                value=app_flags['trending_topics']['default']
                            )
                            inputs['text_overlays'] = gr.Checkbox(
                                label="Text overlays",
                                value=app_flags['text_overlays']['default']
                            )
                    
                    # Multilingual settings
                    with gr.Group():
                        gr.Markdown("#### Multilingual & Voice Settings")
                        inputs['multilingual'] = gr.Checkbox(
                            label="Multilingual generation",
                            value=app_flags['multilingual']['default']
                        )
                        inputs['languages'] = gr.Textbox(
                            label="Additional Languages",
                            placeholder="e.g., spanish,french,german",
                            value=app_flags['languages']['default']
                        )
                        inputs['custom_voice'] = gr.Textbox(
                            label="Custom Voice Settings",
                            placeholder="Voice configuration",
                            value=app_flags['custom_voice']['default']
                        )
                    
                    # Quality & Performance
                    with gr.Group():
                        gr.Markdown("#### Quality & Performance")
                        with gr.Row():
                            inputs['high_quality'] = gr.Checkbox(
                                label="High quality",
                                value=app_flags['high_quality']['default']
                            )
                            inputs['fast_mode'] = gr.Checkbox(
                                label="Fast mode",
                                value=app_flags['fast_mode']['default']
                            )
                            inputs['gpu_acceleration'] = gr.Checkbox(
                                label="GPU acceleration",
                                value=app_flags['gpu_acceleration']['default']
                            )
                        
                        with gr.Row():
                            inputs['background_music'] = gr.Checkbox(
                                label="Background music",
                                value=app_flags['background_music']['default']
                            )
                            inputs['emoji_style'] = gr.Checkbox(
                                label="Emoji style",
                                value=app_flags['emoji_style']['default']
                            )
                            inputs['save_intermediates'] = gr.Checkbox(
                                label="Save intermediates",
                                value=app_flags['save_intermediates']['default']
                            )
                    
                    # Targeting & Optimization
                    with gr.Group():
                        gr.Markdown("#### Targeting & Optimization")
                        with gr.Row():
                            inputs['audience_targeting'] = gr.Dropdown(
                                choices=app_flags['audience_targeting']['choices'],
                                value=app_flags['audience_targeting']['default'],
                                label="Target Audience"
                            )
                            inputs['content_rating'] = gr.Dropdown(
                                choices=app_flags['content_rating']['choices'],
                                value=app_flags['content_rating']['default'],
                                label="Content Rating"
                            )
                            inputs['optimization_level'] = gr.Dropdown(
                                choices=app_flags['optimization_level']['choices'],
                                value=app_flags['optimization_level']['default'],
                                label="Optimization Level"
                            )
                    
                    # Debug & Development
                    with gr.Group():
                        gr.Markdown("#### Debug & Development")
                        inputs['debug_mode'] = gr.Checkbox(
                            label="Debug mode",
                            value=app_flags['debug_mode']['default']
                        )
                    
                    generate_btn = gr.Button("🚀 Generate Video", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Real-time Status")
                    status_output = gr.Textbox(
                        label="Generation Status",
                        value="Ready to generate",
                        interactive=False,
                        elem_classes=["status-display"]
                    )
                    
                    session_info_output = gr.Markdown(
                        value="No active session",
                        label="Session Information"
                    )
        
        with gr.Tab("🤖 AI Agent Discussions"):
            gr.Markdown("### 🤖 AI Agent Collaboration Visualization")
            ai_discussions_output = gr.HTML(
                value="No AI discussions available",
                label="AI Agent Discussions"
            )
            
            refresh_discussions_btn = gr.Button("🔄 Refresh Discussions")
        
        with gr.Tab("🎨 Media Gallery"):
            gr.Markdown("### 🎨 Generated Media Gallery")
            media_gallery_output = gr.HTML(
                value="No media available",
                label="Media Gallery",
                elem_classes=["media-gallery"]
            )
            
            refresh_media_btn = gr.Button("🔄 Refresh Media")
        
        with gr.Tab("📁 Session Manager"):
            gr.Markdown("### 📁 Session Management")
            sessions_display = gr.HTML(
                value=get_recent_sessions(),
                label="Recent Sessions"
            )
            
            with gr.Row():
                refresh_sessions_btn = gr.Button("🔄 Refresh Sessions")
                clear_sessions_btn = gr.Button("🗑️ Clear All Sessions", variant="secondary")
        
        with gr.Tab("ℹ️ Help & Documentation"):
            gr.Markdown("""
            ## 🎬 Viral Video Generator - Complete Guide
            
            ### 🚀 Quick Start
            1. **Enter Topic**: Describe what you want your video to be about
            2. **Configure Settings**: Adjust duration, platform, and style
            3. **Enable AI Features**: Use AI discussions and orchestration
            4. **Generate**: Click the generate button and monitor progress
            
            ### 🤖 AI Agent Discussions
            - **Always Enabled**: AI agents collaborate on every decision
            - **Real-time Visualization**: See agents reaching consensus
            - **Detailed Insights**: Access full discussion transcripts
            - **Multiple Phases**: Planning, Script, Visual, Audio, Assembly
            
            ### 📊 All Available Options
            - **Essential**: Topic, duration, platform, category
            - **AI & Orchestration**: Discussion depth, frame continuity
            - **Advanced**: Trending elements, prompt enhancement
            - **Multilingual**: Multiple language support
            - **Quality**: High quality mode, GPU acceleration
            - **Targeting**: Audience, content rating, optimization
            
            ### 🎨 Media Gallery
            - **Videos**: All generated video files
            - **Images**: Generated images and thumbnails
            - **Audio**: Voice-over and background music
            - **Scripts**: Generated scripts and prompts
            
            ### 📁 Session Management
            - **Organized Storage**: All files in session folders
            - **Complete History**: Track all generations
            - **Easy Access**: Browse and reload previous sessions
            
            ### 🔧 Advanced Features
            - **Real-time Monitoring**: Live progress updates
            - **AI Orchestration**: Multi-agent coordination
            - **Quota Management**: Intelligent API usage
            - **Error Recovery**: Automatic fallbacks
            """)
        
        # Event handlers
        input_list = [inputs[key] for key in [
            'topic', 'duration', 'platform', 'category', 'discussions', 'style', 'tone',
            'image_only', 'frame_continuity', 'realistic_audio', 'use_trending',
            'enhance_prompts', 'quota_optimization', 'multilingual', 'languages',
            'custom_voice', 'background_music', 'text_overlays', 'emoji_style',
            'viral_hooks', 'trending_topics', 'audience_targeting', 'content_rating',
            'optimization_level', 'debug_mode', 'save_intermediates',
            'gpu_acceleration', 'high_quality', 'fast_mode'
        ]]
        
        generate_btn.click(
            fn=start_generation,
            inputs=input_list,
            outputs=[status_output, status_output, session_info_output, ai_discussions_output, media_gallery_output]
        )
        
        refresh_discussions_btn.click(
            fn=get_ai_discussions_display,
            outputs=ai_discussions_output
        )
        
        refresh_media_btn.click(
            fn=get_media_gallery,
            outputs=media_gallery_output
        )
        
        refresh_sessions_btn.click(
            fn=get_recent_sessions,
            outputs=sessions_display
        )
        
        # Auto-refresh status every 3 seconds
        status_output.change(
            fn=get_status_display,
            outputs=status_output,
            every=3
        )
    
    return demo

def main():
    """Main function to launch the comprehensive UI"""
    print("🎬 Viral Video Generator - Comprehensive Interface")
    print("=" * 60)
    print("🚀 Features:")
    print("  ✅ All command-line options available")
    print("  ✅ Real-time generation monitoring")
    print("  ✅ AI agent discussion visualization")
    print("  ✅ Complete media gallery")
    print("  ✅ Session management")
    print("  ✅ Orchestrated video generation")
    print()
    
    # Check environment
    if not os.path.exists("config"):
        print("❌ Error: Please run from the viralAi directory")
        return
    
    print("✅ Environment check passed")
    print("🚀 Starting comprehensive Gradio UI...")
    
    try:
        demo = create_comprehensive_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_api=False,
            share=False,
            show_error=True,
            favicon_path=None,
            app_kwargs={"docs_url": None, "redoc_url": None}
        )
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        print("💡 Make sure all dependencies are installed")

if __name__ == "__main__":
    main() 