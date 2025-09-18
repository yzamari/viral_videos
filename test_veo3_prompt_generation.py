#!/usr/bin/env python3
"""
Test VEO3 prompt generation to understand why it's timing out
"""

import asyncio
import json
import time
from src.agents.detailed_veo3_json_agent import DetailedVEO3JsonAgent
from src.utils.session_context import SessionContext
from src.models.video_models import Platform

async def test_veo3_prompt():
    """Test VEO3 prompt generation with timing"""
    
    # Create a mock session context
    session_context = SessionContext(
        session_id="test_veo3",
        root_path="outputs/test_veo3"
    )
    
    # Initialize the agent
    print("🔍 Initializing DetailedVEO3JsonAgent...")
    start = time.time()
    agent = DetailedVEO3JsonAgent(session_context)
    print(f"✅ Agent initialized in {time.time() - start:.1f}s")
    
    # Test parameters
    mission = "AI technology demonstration"
    style = "modern" 
    tone = "engaging"
    duration = 8
    platform = Platform.YOUTUBE
    
    print(f"\n📝 Testing with simple mission: '{mission}'")
    print(f"   Style: {style}, Tone: {tone}, Duration: {duration}s")
    
    # Test the method that's timing out
    print("\n🚀 Starting prompt generation...")
    start = time.time()
    
    try:
        # Call the method directly
        result = await agent.generate_detailed_json_prompt(
            mission=mission,
            style=style, 
            tone=tone,
            duration=duration,
            platform=platform,
            additional_context={}
        )
        
        elapsed = time.time() - start
        print(f"✅ Generation completed in {elapsed:.1f}s")
        
        # Show the result
        json_prompt, text_prompt = result
        print(f"\n📊 JSON prompt keys: {list(json_prompt.keys()) if json_prompt else 'None'}")
        print(f"📝 Text prompt length: {len(text_prompt) if text_prompt else 0} chars")
        
        if json_prompt:
            print(f"\n🔍 JSON structure:")
            print(json.dumps(json_prompt, indent=2)[:500] + "...")
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Generation failed after {elapsed:.1f}s: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("VEO3 PROMPT GENERATION TEST")
    print("=" * 60)
    asyncio.run(test_veo3_prompt())