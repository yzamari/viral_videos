#!/usr/bin/env python3
"""
Generate reference images for news anchors Sarah Chen and Michael Roberts
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generators.gemini_image_client import GeminiImageClient
import asyncio
import json

async def generate_anchor_references():
    """Generate reference images for both news anchors"""
    
    client = GeminiImageClient()
    
    # Sarah Chen reference
    sarah_prompt = """
    Professional news anchor portrait, photorealistic:
    - Asian woman, 35 years old
    - Shoulder-length straight black hair, professional style
    - Navy blue blazer over white blouse
    - Subtle makeup, professional appearance
    - Confident, friendly expression
    - Sitting at news desk
    - Professional studio lighting
    - CNN/BBC style professional headshot
    - High resolution, broadcast quality
    """
    
    # Michael Roberts reference
    michael_prompt = """
    Professional news anchor portrait, photorealistic:
    - Caucasian man, 40 years old
    - Short brown hair, neatly styled
    - Gray suit with blue tie
    - Clean-shaven, professional appearance
    - Authoritative but approachable expression
    - Sitting at news desk
    - Professional studio lighting
    - CNN/BBC style professional headshot
    - High resolution, broadcast quality
    """
    
    # Generate Sarah's reference
    print("🎨 Generating Sarah Chen reference image...")
    sarah_path = await client.generate_image(
        prompt=sarah_prompt,
        style="photorealistic",
        mission_context="News anchor reference",
        session_id="anchor_references"
    )
    print(f"✅ Sarah Chen reference: {sarah_path}")
    
    # Generate Michael's reference
    print("🎨 Generating Michael Roberts reference image...")
    michael_path = await client.generate_image(
        prompt=michael_prompt,
        style="photorealistic",
        mission_context="News anchor reference",
        session_id="anchor_references"
    )
    print(f"✅ Michael Roberts reference: {michael_path}")
    
    # Save reference metadata
    references = {
        "sarah_chen": {
            "image_path": sarah_path,
            "description": "Asian woman, 35, navy suit, black hair",
            "full_prompt": sarah_prompt
        },
        "michael_roberts": {
            "image_path": michael_path,
            "description": "Caucasian man, 40, gray suit, brown hair",
            "full_prompt": michael_prompt
        }
    }
    
    with open("news_anchors_reference.json", "w") as f:
        json.dump(references, f, indent=2)
    
    print("\n📁 Reference data saved to: news_anchors_reference.json")
    print("\n🎬 Use these images as style references for consistent anchors!")
    
    return references

if __name__ == "__main__":
    asyncio.run(generate_anchor_references())