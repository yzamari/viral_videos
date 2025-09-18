#!/usr/bin/env python3
"""
Directly test what's causing VEO3 prompt generation timeouts
"""

import os
import sys
import time

# Test the AI call directly
def test_direct_ai_call():
    """Test a direct AI call to see if it times out"""
    
    print("=" * 60)
    print("TESTING DIRECT AI CALL")
    print("=" * 60)
    
    # Import the Gemini helper directly
    from src.agents.gemini_helper import GeminiModelHelper
    
    # Initialize model
    print("\n🔍 Initializing Gemini model...")
    start = time.time()
    model = GeminiModelHelper("gemini-2.5-flash")
    print(f"✅ Model initialized in {time.time() - start:.1f}s")
    
    # Create a simple test prompt
    simple_prompt = """
    Create a simple JSON structure for a video scene.
    Keep it brief and simple.
    
    Return JSON with these fields:
    - description: One sentence description
    - style: One word style
    - duration: Number in seconds
    
    Example:
    {
        "description": "A robot walking",
        "style": "futuristic",
        "duration": 5
    }
    """
    
    print("\n📝 Testing SIMPLE prompt (should work)...")
    start = time.time()
    try:
        response = model.generate_content(simple_prompt)
        elapsed = time.time() - start
        print(f"✅ Simple prompt succeeded in {elapsed:.1f}s")
        print(f"   Response preview: {response.text[:100]}...")
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Simple prompt failed after {elapsed:.1f}s: {e}")
    
    # Now test with the actual complex prompt the agent uses
    print("\n📝 Loading actual VEO3 agent prompt...")
    
    # Get the actual prompt content
    from src.agents.detailed_veo3_json_agent import DetailedVEO3JsonAgent
    
    # Create a mock agent to get the prompt
    class MockSession:
        def __init__(self):
            self.session_id = "test"
    
    agent = DetailedVEO3JsonAgent(MockSession())
    
    # Get the example content that's being sent
    detailed_examples = agent._get_detailed_professional_examples()
    
    # This is the prompt that's timing out
    complex_prompt = f"""
    You are a cinematographer agent specializing in shot composition, camera motion, frame rate, film grain.
    
    MISSION: AI technology demonstration
    STYLE: modern
    TONE: engaging
    DURATION: 8 seconds
    PLATFORM: youtube
    
    PROFESSIONAL EXAMPLES:
    {detailed_examples[:5000]}  # Truncate for testing
    
    Create a detailed JSON structure for the 'shot' object with:
    - composition
    - camera_motion
    - frame_rate
    - film_grain
    
    Return ONLY valid JSON, no explanation.
    """
    
    print(f"\n📊 Complex prompt size: {len(complex_prompt)} characters")
    print(f"   (Original examples size: {len(detailed_examples)} characters)")
    
    print("\n📝 Testing COMPLEX prompt (this is what's timing out)...")
    start = time.time()
    try:
        # Try with timeout wrapper
        from src.utils.ai_timeout_wrapper import ai_wrapper
        
        response = ai_wrapper.safe_ai_call(
            model.generate_content,
            complex_prompt,
            timeout=10.0  # 10 second timeout for testing
        )
        
        if response:
            elapsed = time.time() - start
            print(f"✅ Complex prompt succeeded in {elapsed:.1f}s")
            print(f"   Response preview: {str(response)[:100]}...")
        else:
            elapsed = time.time() - start
            print(f"⚠️ Complex prompt timed out after {elapsed:.1f}s")
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Complex prompt failed after {elapsed:.1f}s: {e}")
    
    # Test with even larger prompt
    print("\n📝 Testing HUGE prompt (full examples)...")
    huge_prompt = f"""
    {detailed_examples}
    
    Now create your own detailed JSON following these examples.
    """
    
    print(f"📊 Huge prompt size: {len(huge_prompt)} characters")
    
    start = time.time()
    try:
        response = ai_wrapper.safe_ai_call(
            model.generate_content,
            huge_prompt,
            timeout=5.0  # Even shorter timeout
        )
        
        if response:
            elapsed = time.time() - start
            print(f"✅ Huge prompt succeeded in {elapsed:.1f}s")
        else:
            elapsed = time.time() - start
            print(f"⚠️ Huge prompt timed out after {elapsed:.1f}s")
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Huge prompt failed after {elapsed:.1f}s: {e}")

if __name__ == "__main__":
    test_direct_ai_call()
    
    print("\n" + "=" * 60)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 60)
    print("""
The DetailedVEO3JsonAgent is sending MASSIVE prompts to the AI:
1. It includes 7000+ character examples in EVERY agent call
2. It makes 7+ separate AI calls (one per agent role)
3. Each call times out after 30 seconds
4. The prompts are too complex for fast response

SOLUTION:
1. Reduce or remove the huge example prompts
2. Use simpler, direct prompts
3. Skip the multi-agent system for VEO3
4. Use a fallback simple prompt generator
    """)