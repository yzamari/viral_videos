#!/usr/bin/env python3
"""
Simple Analytics UI for Testing Trending Analysis
"""

import gradio as gr
import sys
import os
sys.path.append('.')

from trending_analysis import TrendingAnalyzer
from config.config import settings

def analyze_trending_simple(topic: str, max_videos: int, days_back: int):
    """Simple trending analysis function"""
    try:
        print(f"🔍 Analyzing: {topic or 'general trending'} (last {days_back} days, max {max_videos} videos)")
        
        analyzer = TrendingAnalyzer(settings.google_api_key)
        report = analyzer.analyze_trending(
            topic=topic if topic.strip() else None,
            max_videos=max_videos,
            days_back=days_back
        )
        
        # Generate simple summary
        metadata = report.get('analysis_metadata', {})
        videos = report.get('trending_videos', [])
        
        summary = f"""📊 ANALYSIS RESULTS

🎯 Configuration:
• Topic: {metadata.get('topic', 'General Trending')}
• Time Range: Last {metadata.get('days_back', 6)} days
• Videos Found: {metadata.get('total_videos_found', 0)}
• Videos Analyzed: {metadata.get('total_videos_analyzed', 0)}

🎬 Top Videos:"""
        
        for i, video in enumerate(videos[:5], 1):
            summary += f"""
{i}. {video['title'][:60]}...
   👀 {video['view_count']:,} views | ❤️ {video.get('like_count', 0):,} likes
   📺 {video.get('channel_name', 'Unknown')}"""
        
        return "✅ Analysis Complete!", report, summary
        
    except Exception as e:
        error_msg = f"❌ Analysis failed: {str(e)}"
        print(error_msg)
        return error_msg, {}, error_msg

def create_simple_interface():
    """Create simple interface focused on analytics"""
    
    with gr.Blocks(title="📊 Trending Analysis", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 📊 Trending Video Analysis
        ### Test the new time filtering feature
        
        This interface tests the trending analysis with configurable time range.
        """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🔥 Trending Analysis")
                
                topic_input = gr.Textbox(
                    label="Topic to Analyze",
                    placeholder="Enter topic (e.g., 'AI technology') or leave empty for general trending",
                    value=""
                )
                
                with gr.Row():
                    max_videos_slider = gr.Slider(
                        minimum=3,
                        maximum=15,
                        value=5,
                        step=1,
                        label="Max Videos to Analyze"
                    )
                    
                    days_back_slider = gr.Slider(
                        minimum=1,
                        maximum=30,
                        value=6,
                        step=1,
                        label="Days Back to Search (NEW FEATURE!)"
                    )
                
                analyze_btn = gr.Button("🔍 Analyze Trending", variant="primary", size="lg")
                
                status_text = gr.Textbox(
                    label="Status",
                    value="Ready to analyze trending videos",
                    interactive=False,
                    lines=2
                )
                
            with gr.Column():
                gr.Markdown("### 📊 Results")
                
                results_json = gr.JSON(
                    label="Full Analysis Results",
                    value={}
                )
                
                summary_text = gr.Textbox(
                    label="Quick Summary",
                    lines=15,
                    interactive=False
                )
        
        # Examples section
        gr.Markdown("""
        ### 📝 Example Queries:
        - **General trending**: Leave topic empty, try different time ranges
        - **AI Technology**: Enter "AI technology" and set days back to 3
        - **Cute cats**: Enter "cute cats" and set days back to 7
        - **Breaking news**: Enter "breaking news" and set days back to 1
        """)
        
        # Connect events
        analyze_btn.click(
            analyze_trending_simple,
            inputs=[topic_input, max_videos_slider, days_back_slider],
            outputs=[status_text, results_json, summary_text]
        )
    
    return interface

def main():
    """Launch the simple analytics interface"""
    print("🚀 Starting Simple Analytics UI...")
    print("📊 Testing trending analysis with time filtering")
    
    interface = create_simple_interface()
    
    print("🌐 Launching interface...")
    print("🔗 URL: http://127.0.0.1:7860")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main() 