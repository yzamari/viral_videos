#!/usr/bin/env python3
"""
Real-time UI for Viral Video Generator with AI Agent Discussions and Video Playback
Shows live agent discussions and plays generated videos in browser
"""

import streamlit as st
import os
import sys
import time
import json
import asyncio
from datetime import datetime
from pathlib import Path
import threading
import queue
import base64

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.video_models import Platform, VideoCategory, ForceGenerationMode, VideoOrientation
from src.agents.enhanced_orchestrator_with_discussions import EnhancedOrchestratorWithDiscussions

# Configure Streamlit page
st.set_page_config(
    page_title="🎬 Viral Video Generator - Real-time AI Discussions",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .agent-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .consensus-bar {
        background: linear-gradient(90deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
        height: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .discussion-phase {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #4ecdc4;
    }
    
    .video-container {
        border: 2px solid #4ecdc4;
        border-radius: 10px;
        padding: 1rem;
        background: rgba(78, 205, 196, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'generation_status' not in st.session_state:
        st.session_state.generation_status = "idle"
    if 'current_discussions' not in st.session_state:
        st.session_state.current_discussions = []
    if 'generated_video_path' not in st.session_state:
        st.session_state.generated_video_path = None
    if 'discussion_queue' not in st.session_state:
        st.session_state.discussion_queue = queue.Queue()
    if 'generation_thread' not in st.session_state:
        st.session_state.generation_thread = None

def display_agent_discussion(discussion_data):
    """Display real-time agent discussion"""
    st.markdown(f"""
    <div class="discussion-phase">
        <h4>🎭 {discussion_data.get('topic', 'Agent Discussion')}</h4>
        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
            <span><strong>Consensus:</strong> {discussion_data.get('consensus_level', 0):.1%}</span>
            <span><strong>Round:</strong> {discussion_data.get('current_round', 1)}</span>
            <span><strong>Participants:</strong> {len(discussion_data.get('participants', []))}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Consensus progress bar
    consensus = discussion_data.get('consensus_level', 0)
    st.progress(consensus, text=f"Consensus: {consensus:.1%}")
    
    # Agent messages
    messages = discussion_data.get('messages', [])
    for msg in messages[-5:]:  # Show last 5 messages
        agent_name = msg.get('agent', 'Unknown')
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', '')
        
        st.markdown(f"""
        <div class="agent-message">
            <strong>🤖 {agent_name}</strong> <small>{timestamp}</small><br/>
            {content[:200]}{'...' if len(content) > 200 else ''}
        </div>
        """, unsafe_allow_html=True)

def get_video_base64(video_path):
    """Convert video to base64 for embedding"""
    try:
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode()
        return video_base64
    except Exception as e:
        st.error(f"Error loading video: {e}")
        return None

def display_video_player(video_path):
    """Display video player in browser"""
    if not video_path or not os.path.exists(video_path):
        st.warning("No video file found")
        return
    
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    st.subheader("🎬 Generated Video")
    
    # Get video info
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
    st.info(f"📁 File: {os.path.basename(video_path)} ({file_size:.1f}MB)")
    
    # Video player
    video_file = open(video_path, 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
    video_file.close()
    
    # Download button
    st.download_button(
        label="📥 Download Video",
        data=video_bytes,
        file_name=os.path.basename(video_path),
        mime="video/mp4"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_video_with_discussions(mission, platform, category, duration):
    """Generate video with real-time discussion updates"""
    try:
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("❌ GEMINI_API_KEY not found in environment variables")
            return None
        
        # Create orchestrator
        orchestrator = EnhancedOrchestratorWithDiscussions(
            api_key=api_key,
            use_vertex_ai=True,
            enable_discussions=True
        )
        
        # Generate video with discussions
        st.session_state.generation_status = "generating"
        
        # Mock discussion updates (in real implementation, this would come from the orchestrator)
        discussion_phases = [
            "Initial Video Generation Planning",
            "Script Content and Structure Optimization", 
            "Visual Style and Video Generation Strategy",
            "Audio Generation and Synchronization Strategy",
            "Final Video Assembly Strategy"
        ]
        
        for i, phase in enumerate(discussion_phases):
            # Simulate discussion progress
            for round_num in range(1, 3):
                discussion_data = {
                    'topic': phase,
                    'consensus_level': min(0.9, 0.3 + (round_num * 0.3) + (i * 0.1)),
                    'current_round': round_num,
                    'participants': ['ExecutiveChief', 'StoryWeaver', 'AudioMaster', 'VisionCraft'],
                    'messages': [
                        {
                            'agent': 'ExecutiveChief',
                            'content': f"Analyzing strategic approach for {mission}...",
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        },
                        {
                            'agent': 'StoryWeaver', 
                            'content': f"Crafting narrative structure for {platform} platform...",
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        }
                    ]
                }
                
                # Update discussion in session state
                st.session_state.current_discussions.append(discussion_data)
                time.sleep(2)  # Simulate processing time
        
        # Generate actual video
        result = orchestrator.generate_video_with_discussions(
            mission=mission,
            platform=Platform(platform.lower()),
            category=VideoCategory(category),
            duration=duration
        )
        
        st.session_state.generated_video_path = result.file_path
        st.session_state.generation_status = "completed"
        
        return result.file_path
        
    except Exception as e:
        st.error(f"❌ Video generation failed: {e}")
        st.session_state.generation_status = "error"
        return None

def main():
    """Main Streamlit app"""
    initialize_session_state()
    
    # Header
    st.title("🎬 Unified Real-time VEO-2 Video Generator")
    st.markdown("**Mission-based video generation with 19 AI agents, live discussions, and force generation controls**")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎛️ Generation Controls")
        
        # Mission input
        mission = st.text_area(
            "📝 Mission Statement",
            value="An ad for Shakes bar that during day time is shakes bar and during night it is alcholic shakes bar. the ad is for ages 18-31. it is business in Israel",
            height=100,
            help="Describe what video you want to create"
        )
        
        # Platform and category
        col1, col2 = st.columns(2)
        with col1:
            platform = st.selectbox("📱 Target Platform", ["TikTok", "YouTube", "Instagram", "Facebook"])
        with col2:
            category = st.selectbox("📂 Video Category", ["Business", "Entertainment", "Education", "Comedy"])
        
        # Duration
        duration = st.slider("⏱️ Video Duration (seconds)", 15, 120, 35)
        
        # Force generation controls
        st.subheader("🎮 Force Generation Controls")
        force_mode = st.selectbox(
            "Generation Mode",
            ["auto", "force_veo3", "force_veo2", "force_image_gen"],
            help="Control which AI models to use"
        )
        
        # Generation button
        if st.button("🚀 Generate Video", type="primary"):
            if mission.strip():
                # Start generation in background thread
                generation_thread = threading.Thread(
                    target=generate_video_with_discussions,
                    args=(mission, platform, category, duration)
                )
                generation_thread.start()
                st.session_state.generation_thread = generation_thread
            else:
                st.error("Please enter a mission statement")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Video display area
        if st.session_state.generated_video_path:
            display_video_player(st.session_state.generated_video_path)
        else:
            st.info("🎬 Generated video will appear here")
    
    with col2:
        # AI Agent discussions
        st.subheader("🤖 AI Agent Discussions")
        
        if st.session_state.generation_status == "generating":
            st.info("🔄 AI agents are discussing...")
            
            # Display current discussions
            if st.session_state.current_discussions:
                latest_discussion = st.session_state.current_discussions[-1]
                display_agent_discussion(latest_discussion)
            
            # Auto-refresh every 2 seconds during generation
            time.sleep(2)
            st.rerun()
            
        elif st.session_state.generation_status == "completed":
            st.success("✅ Video generation completed!")
            
            # Show final discussion summary
            if st.session_state.current_discussions:
                st.subheader("📊 Discussion Summary")
                total_discussions = len(st.session_state.current_discussions)
                avg_consensus = sum(d.get('consensus_level', 0) for d in st.session_state.current_discussions) / max(1, total_discussions)
                
                st.metric("Total Discussions", total_discussions)
                st.metric("Average Consensus", f"{avg_consensus:.1%}")
                
        elif st.session_state.generation_status == "error":
            st.error("❌ Video generation failed")
            
        else:
            st.info("👋 Ready to generate your viral video!")
    
    # Status footer
    st.markdown("---")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("Generation Status", st.session_state.generation_status.title())
    
    with status_col2:
        if st.session_state.current_discussions:
            st.metric("Active Discussions", len(st.session_state.current_discussions))
        else:
            st.metric("Active Discussions", 0)
    
    with status_col3:
        if st.session_state.generated_video_path:
            st.metric("Video Ready", "✅ Yes")
        else:
            st.metric("Video Ready", "⏳ No")

if __name__ == "__main__":
    main() 