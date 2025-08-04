#!/usr/bin/env python3
"""
Intelligent News Demo - Complete AI-Driven News Compilation
Shows the full workflow with AI agents, multi-source aggregation, and smart media selection
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.news_aggregator.multi_source_aggregator import IntelligentNewsCompiler
from src.news_aggregator.agents.news_discussion_agents import NewsDiscussionModerator, NewsItem


async def create_intelligent_news_compilation():
    """Create an intelligent news compilation with AI agent discussions"""
    
    print("""
🤖 INTELLIGENT NEWS COMPILATION SYSTEM
=====================================
✨ Features:
  • Multi-source news aggregation
  • AI agents discuss each story
  • Smart duration calculation
  • Best media selection per story
  • Professional summaries
  • Multiple angles per story
""")
    
    # Get user preferences
    print("\n📋 Select news categories (comma-separated):")
    print("Options: politics, technology, sports, finance, entertainment, health, breaking_news")
    print("Example: technology,sports,finance")
    print("Press Enter for all categories")
    
    # For demo, use default categories
    categories = ['technology', 'sports', 'breaking_news']
    
    print(f"\n✅ Selected categories: {', '.join(categories)}")
    
    # Get duration
    print("\n⏱️  Enter total duration in seconds (30-300):")
    print("Press Enter for 60 seconds")
    
    # For demo, use 60 seconds
    duration = 60
    
    print(f"\n✅ Target duration: {duration} seconds")
    
    # Create compilation
    compiler = IntelligentNewsCompiler()
    
    try:
        video_path = await compiler.create_intelligent_compilation(
            categories=categories,
            total_duration=duration,
            output_name=f"intelligent_news_{duration}s.mp4"
        )
        
        print(f"""
✅ INTELLIGENT NEWS COMPILATION COMPLETE!
======================================
📹 Video: {os.path.abspath(video_path)}
📊 Report: {video_path.replace('.mp4', '_report.json')}

🎯 What makes this intelligent:
  1. Stories aggregated from 6+ news sources
  2. AI agents discussed each story's importance
  3. Duration calculated based on complexity
  4. Best media selected from all sources
  5. Professional summaries generated
  6. Smooth pacing and transitions

🎬 The video includes:
  • Title cards with summaries
  • Multiple media angles per story
  • Source attribution
  • Importance-based ordering
  • Category-appropriate pacing

📺 Ready for viewing!
""")
        
    except Exception as e:
        print(f"\n❌ Error creating compilation: {e}")
        import traceback
        traceback.print_exc()


async def test_ai_agents_only():
    """Test just the AI agent discussion system"""
    
    print("""
🎭 TESTING AI AGENT DISCUSSIONS
==============================
""")
    
    # Create a test news item
    test_item = NewsItem(
        title="OpenAI Announces GPT-5 with Breakthrough Capabilities",
        category="technology",
        sources=[
            {"name": "TechCrunch", "headline": "OpenAI's GPT-5 Revolutionizes AI"},
            {"name": "The Verge", "headline": "GPT-5: Everything You Need to Know"},
            {"name": "Wired", "headline": "Inside OpenAI's Game-Changing GPT-5"},
            {"name": "MIT Tech Review", "headline": "GPT-5's Scientific Breakthroughs"},
            {"name": "Reuters", "headline": "OpenAI Unveils Most Advanced AI Model"}
        ],
        media_items=[
            {"type": "video", "source": "TechCrunch", "url": "demo.mp4", "quality_score": 0.9},
            {"type": "image", "source": "The Verge", "url": "gpt5_demo.jpg", "quality_score": 0.85},
            {"type": "image", "source": "Wired", "url": "sam_altman.jpg", "quality_score": 0.8},
            {"type": "video", "source": "OpenAI", "url": "official_demo.mp4", "quality_score": 0.95}
        ]
    )
    
    # Run agent discussion
    moderator = NewsDiscussionModerator()
    consensus = moderator.conduct_discussion(test_item)
    
    print(f"""
📊 FINAL CONSENSUS:
==================
⏱️  Duration: {consensus['final_duration']} seconds
📹 Media Strategy: {consensus['media_strategy']}
📊 Selected {len(consensus['selected_media'])} media items
📝 Summary: {consensus['summary']}
⭐ Importance: {consensus['importance_score']:.2f}
🎬 Pacing: {consensus['pacing']}
""")


async def main():
    """Main demo function"""
    
    print("Choose demo mode:")
    print("1. Full intelligent news compilation")
    print("2. Test AI agents discussion only")
    print("3. Exit")
    
    # For automated demo, choose option 1
    choice = "1"
    
    if choice == "1":
        await create_intelligent_news_compilation()
    elif choice == "2":
        await test_ai_agents_only()
    else:
        print("Exiting...")


if __name__ == "__main__":
    # First, let's test the AI agents
    print("\n🧪 First, testing AI agent discussions...\n")
    asyncio.run(test_ai_agents_only())
    
    # Then run the full demo
    print("\n\n🎬 Now creating full intelligent news compilation...\n")
    asyncio.run(create_intelligent_news_compilation())