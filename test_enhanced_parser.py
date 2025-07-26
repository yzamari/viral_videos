#!/usr/bin/env python3
"""Test Enhanced Mission Parser with API key"""

import asyncio
import os
from src.agents.enhanced_mission_parser import EnhancedMissionParser
from src.models.video_models import Platform

async def test_parser():
    """Test the Enhanced Mission Parser"""
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found (tried GOOGLE_AI_API_KEY, GOOGLE_API_KEY, GEMINI_API_KEY)")
        return
        
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Initialize parser with API key
    parser = EnhancedMissionParser(ai_manager=None, model_name="gemini-2.5-pro", api_key=api_key)
    
    # Test mission
    mission = """Family Guy style animated news. Nuclear News logo ticker. Maryam the anchor with huge eyes, disheveled hijab. Maryam says: 'This just in: Tehran has gone full Mad Max.' Cut to cartoon map showing water fleeing Iran with little legs. Maryam reports: 'It is a shocking water apocalypse unfolding.' Show Peter Griffin-style warriors fighting over last bottle. One yells: 'WITNESS ME!' and drinks it all greedily. Brian-style intellectual dog starts: 'This reminds me of my novel about—' but gets hit by a rogue water truck. Maryam removes hijab completely and states: 'F*** it, there is no water to wash it.' End card displays: 'Iran International: We are as thirsty as you are!'"""
    
    print("\n📝 Testing mission parsing...")
    print(f"Mission: {mission[:100]}...")
    
    try:
        # Parse the mission
        parsed = await parser.parse_mission(
            mission_statement=mission,
            platform=Platform.YOUTUBE
        )
        
        print("\n✅ Parsing successful!")
        print(f"\n📖 Script content ({len(parsed.script_content)} chars):")
        print(f"   {parsed.script_content[:200]}...")
        print(f"\n🎬 Visual instructions ({len(parsed.visual_instructions)} items):")
        for i, inst in enumerate(parsed.visual_instructions[:3]):
            print(f"   {i+1}. {inst}")
        print(f"\n👥 Characters: {list(parsed.character_descriptions.keys())}")
        print(f"🎨 Style: {parsed.style_notes}")
        print(f"😂 Is satirical: {parsed.is_satirical}")
        print(f"📊 Confidence: {parsed.parsing_confidence}")
        
    except Exception as e:
        print(f"\n❌ Error parsing mission: {e}")
        import traceback
        traceback.print_exc()
            
    # Also test with a different mission to see if we can get AI parsing to work
    print("\n\n🔄 Testing with simpler mission...")
    simple_mission = "News anchor says: 'Breaking news about water crisis.' Show map of Iran. Reporter states: 'The situation is critical.'"
    
    try:
        parsed2 = await parser.parse_mission(
            mission_statement=simple_mission,
            platform=Platform.YOUTUBE
        )
        print(f"\n📖 Script: {parsed2.script_content}")
        print(f"🎬 Visuals: {parsed2.visual_instructions}")
        print(f"📊 Confidence: {parsed2.parsing_confidence}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_parser())