#!/usr/bin/env python3
import gradio as gr
import os

def generate_video(topic):
    if not topic:
        return "❌ Please enter a topic"
    
    return f"✅ Would generate video about: {topic}"

demo = gr.Interface(
    fn=generate_video,
    inputs=gr.Textbox(label="Video Topic", placeholder="Enter topic"),
    outputs=gr.Textbox(label="Result"),
    title="🎬 Basic Video Generator",
    description="Simple working interface"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True) 