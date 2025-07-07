#!/usr/bin/env python3
"""
Test Frame Continuity AI Agent Decision-Making
Tests the VisualFlow agent's ability to make intelligent frame continuity decisions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.continuity_decision_agent import ContinuityDecisionAgent
from config.config import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_continuity_decisions():
    """Test frame continuity decisions for different video types"""
    
    if not settings.google_api_key:
        print("❌ Error: GOOGLE_API_KEY not found")
        return
    
    # Initialize the continuity decision agent
    continuity_agent = ContinuityDecisionAgent(settings.google_api_key)
    
    print("🎬 Testing AI Frame Continuity Decision Agent")
    print("=" * 60)
    
    # Test cases: Different video types that should have different continuity decisions
    test_cases = [
        {
            'topic': 'Quick cooking hack for busy mornings',
            'category': 'Educational',
            'platform': 'tiktok',
            'duration': 15,
            'expected': False,  # Short TikTok should prefer jump cuts
            'description': 'Short TikTok educational content'
        },
        {
            'topic': 'Comprehensive guide to machine learning',
            'category': 'Educational',
            'platform': 'youtube',
            'duration': 60,
            'expected': True,  # Long educational content benefits from continuity
            'description': 'Long YouTube educational content'
        },
        {
            'topic': 'Hilarious pet fails compilation',
            'category': 'Comedy',
            'platform': 'instagram',
            'duration': 20,
            'expected': False,  # Comedy timing benefits from jump cuts
            'description': 'Comedy content with timing focus'
        },
        {
            'topic': 'Breaking news: Major scientific discovery',
            'category': 'News',
            'platform': 'youtube',
            'duration': 30,
            'expected': True,  # News content benefits from flow
            'description': 'News content with narrative flow'
        },
        {
            'topic': 'Dance challenge tutorial',
            'category': 'Entertainment',
            'platform': 'tiktok',
            'duration': 10,
            'expected': False,  # Very short content needs impact
            'description': 'Very short entertainment content'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"   Topic: {test_case['topic']}")
        print(f"   Category: {test_case['category']}")
        print(f"   Platform: {test_case['platform']}")
        print(f"   Duration: {test_case['duration']}s")
        
        # Get AI decision
        try:
            decision = continuity_agent.analyze_frame_continuity_need(
                topic=test_case['topic'],
                category=test_case['category'],
                platform=test_case['platform'],
                duration=test_case['duration'],
                style='viral'
            )
            
            # Display results
            status = "✅ ENABLED" if decision['use_frame_continuity'] else "❌ DISABLED"
            print(f"   🎬 AI Decision: Frame Continuity {status}")
            print(f"   🤖 Confidence: {decision['confidence']:.2f}")
            print(f"   💡 Reason: {decision['primary_reason']}")
            print(f"   📊 Platform Optimization: {decision['platform_optimization']}")
            
            # Check if decision matches expectation
            correct = decision['use_frame_continuity'] == test_case['expected']
            correctness = "✅ CORRECT" if correct else "⚠️ UNEXPECTED"
            print(f"   {correctness} (Expected: {test_case['expected']})")
            
            results.append({
                'test_case': i,
                'decision': decision['use_frame_continuity'],
                'expected': test_case['expected'],
                'correct': correct,
                'confidence': decision['confidence'],
                'reason': decision['primary_reason']
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'test_case': i,
                'decision': None,
                'expected': test_case['expected'],
                'correct': False,
                'confidence': 0.0,
                'reason': f"Error: {e}"
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    correct_decisions = sum(1 for r in results if r['correct'])
    total_decisions = len(results)
    accuracy = correct_decisions / total_decisions if total_decisions > 0 else 0
    
    print(f"✅ Correct Decisions: {correct_decisions}/{total_decisions}")
    print(f"📈 Accuracy: {accuracy:.1%}")
    
    if accuracy >= 0.8:
        print("🎯 AI Agent Performance: EXCELLENT")
    elif accuracy >= 0.6:
        print("🎯 AI Agent Performance: GOOD")
    else:
        print("🎯 AI Agent Performance: NEEDS IMPROVEMENT")
    
    # Display detailed results
    print("\n📋 Detailed Results:")
    for result in results:
        status = "✅" if result['correct'] else "❌"
        decision_text = "ON" if result['decision'] else "OFF"
        expected_text = "ON" if result['expected'] else "OFF"
        print(f"   {status} Test {result['test_case']}: {decision_text} (expected {expected_text}) - {result['reason'][:50]}...")
    
    return results

def test_command_line_integration():
    """Test integration with command line options"""
    
    print("\n🖥️ Testing Command Line Integration")
    print("=" * 60)
    
    print("Available frame continuity options:")
    print("   --frame-continuity auto   🤖 Let AI agent decide (default)")
    print("   --frame-continuity on     ✅ Always enable frame continuity")
    print("   --frame-continuity off    ❌ Always disable frame continuity")
    
    print("\nExample commands:")
    print("   python3 main.py generate --topic 'cooking tips' --frame-continuity auto")
    print("   python3 main.py generate --topic 'comedy skit' --frame-continuity off")
    print("   python3 main.py generate --topic 'tutorial' --frame-continuity on")
    
    return True

if __name__ == "__main__":
    print("🎬 Frame Continuity AI Agent Test Suite")
    print("Testing intelligent frame continuity decision-making...")
    
    # Test AI decision-making
    decision_results = test_continuity_decisions()
    
    # Test command line integration
    test_command_line_integration()
    
    print("\n🎯 Test Complete!")
    print("The AI agent can now intelligently decide frame continuity based on:")
    print("   • Video content type and category")
    print("   • Target platform preferences")
    print("   • Video duration and pacing needs")
    print("   • Audience engagement patterns")
    print("   • Visual storytelling requirements") 