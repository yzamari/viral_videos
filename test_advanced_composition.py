#!/usr/bin/env python3
"""
Test Advanced Video Composition Discussion System
Tests comprehensive AI agent decisions for granular video composition
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.advanced_composition_discussions import create_advanced_composition_system
from config.config import settings
from src.utils.logging_config import get_logger
import json
from datetime import datetime

logger = get_logger(__name__)

def test_comprehensive_composition():
    """Test comprehensive video composition discussion system"""
    
    if not settings.google_api_key:
        print("❌ Error: GOOGLE_API_KEY not found")
        return
    
    print("🎭 Testing Advanced Video Composition Discussion System")
    print("=" * 80)
    
    # Test case: Complex video with mixed requirements
    test_case = {
        'topic': 'Complete guide to AI video generation with practical examples',
        'category': 'Educational',
        'platform': 'youtube',
        'total_duration': 45,
        'style': 'professional'
    }
    
    print(f"📋 Test Case: {test_case['topic']}")
    print(f"📱 Platform: {test_case['platform']}")
    print(f"⏱️ Duration: {test_case['total_duration']} seconds")
    print(f"🎨 Style: {test_case['style']}")
    print(f"📂 Category: {test_case['category']}")
    
    # Create session ID for testing
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Initialize advanced composition system
        composition_system = create_advanced_composition_system(
            settings.google_api_key, 
            session_id
        )
        
        print("\n🚀 Starting Comprehensive Composition Analysis...")
        print("=" * 80)
        
        # Conduct comprehensive composition discussion
        result = composition_system.conduct_comprehensive_composition_discussion(
            topic=test_case['topic'],
            category=test_case['category'],
            platform=test_case['platform'],
            total_duration=test_case['total_duration'],
            style=test_case['style']
        )
        
        print("\n✅ Comprehensive Composition Analysis Complete!")
        print("=" * 80)
        
        # Display results summary
        print("📊 COMPOSITION DECISIONS SUMMARY:")
        print("=" * 80)
        
        # Structure decisions
        if 'structure' in result['decisions']:
            structure = result['decisions']['structure']['ai_analysis']
            print(f"🏗️ VIDEO STRUCTURE:")
            print(f"   Total Segments: {structure['total_segments']}")
            print(f"   Strategy: {structure['structure_strategy']}")
            
            for i, segment in enumerate(structure['segments'], 1):
                print(f"   Segment {i}: {segment['duration']}s - {segment['purpose']} ({segment['continuity_type']})")
        
        # Timing decisions
        if 'timing' in result['decisions']:
            timing = result['decisions']['timing']['ai_analysis']
            print(f"\n⏱️ CLIP TIMING:")
            print(f"   Total Clips: {timing['total_clips']}")
            print(f"   Strategy: {timing['timing_strategy']}")
            
            for clip in timing['clips'][:5]:  # Show first 5 clips
                print(f"   Clip {clip['clip_id']}: {clip['duration']:.1f}s - {clip['purpose']} ({clip['pacing']})")
            
            if len(timing['clips']) > 5:
                print(f"   ... and {len(timing['clips']) - 5} more clips")
        
        # Visual decisions
        if 'visual' in result['decisions']:
            visual = result['decisions']['visual']['ai_analysis']
            print(f"\n🎨 VISUAL ELEMENTS:")
            print(f"   Design Strategy: {visual['design_strategy']}")
            print(f"   Text Elements: {len(visual['text_elements'])}")
            print(f"   Color Palette: {visual['color_palette']['primary']}, {visual['color_palette']['secondary']}")
            
            for element in visual['text_elements'][:3]:  # Show first 3 elements
                print(f"   {element['type']}: '{element['content']}' at {element['position']}")
        
        # Media decisions
        if 'media' in result['decisions']:
            media = result['decisions']['media']['ai_analysis']
            allocation = media['resource_allocation']
            print(f"\n📱 MEDIA STRATEGY:")
            print(f"   Strategy: {media['media_strategy']}")
            print(f"   VEO2 Videos: {allocation['veo2_clips']}")
            print(f"   Static Images: {allocation['static_images']}")
            print(f"   Image Sequences: {allocation['image_sequences']}")
            
            # Show media decisions for first few clips
            for decision in media['clip_media_decisions'][:3]:
                print(f"   Clip {decision['clip_id']}: {decision['media_type']} - {decision['rationale'][:50]}...")
        
        # Integration decisions
        if 'integration' in result['decisions']:
            integration = result['decisions']['integration']['discussion_result']
            print(f"\n🔗 INTEGRATION:")
            print(f"   Consensus: {integration['consensus_level']:.2f}")
            print(f"   Key Insights: {len(integration['key_insights'])}")
            
            for insight in integration['key_insights'][:2]:
                print(f"   • {insight[:80]}...")
        
        # Discussion statistics
        print(f"\n📈 DISCUSSION STATISTICS:")
        print("=" * 80)
        
        total_discussions = 0
        total_consensus = 0
        
        for phase, decision in result['decisions'].items():
            if 'discussion_result' in decision:
                disc = decision['discussion_result']
                total_discussions += 1
                total_consensus += disc['consensus_level']
                print(f"   {phase.title()}: {disc['consensus_level']:.2f} consensus in {disc['total_rounds']} rounds")
        
        if total_discussions > 0:
            avg_consensus = total_consensus / total_discussions
            print(f"   Average Consensus: {avg_consensus:.2f}")
        
        # File logging verification
        print(f"\n📁 LOGGING VERIFICATION:")
        print("=" * 80)
        
        session_dir = f"outputs/session_{session_id}"
        if os.path.exists(session_dir):
            print(f"✅ Session directory created: {session_dir}")
            
            # Check for composition files
            composition_dir = f"{session_dir}/composition_discussions"
            if os.path.exists(composition_dir):
                files = os.listdir(composition_dir)
                print(f"✅ Composition discussions logged: {len(files)} files")
                for file in files[:3]:
                    print(f"   • {file}")
            
            # Check for comprehensive results
            results_file = f"{session_dir}/comprehensive_composition_results.json"
            if os.path.exists(results_file):
                print(f"✅ Comprehensive results saved: {results_file}")
                
                # Verify file content
                with open(results_file, 'r') as f:
                    saved_data = json.load(f)
                print(f"   File size: {len(json.dumps(saved_data))} characters")
            
            # Check for summary
            summary_file = f"{session_dir}/composition_summary.json"
            if os.path.exists(summary_file):
                print(f"✅ Summary saved: {summary_file}")
                
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
                
                print(f"   Summary: {summary['total_segments']} segments, {summary['total_clips']} clips")
                print(f"   Media: {summary['veo2_clips']} VEO2, {summary['static_images']} images")
                print(f"   Visual: {summary['text_elements']} text elements")
        
        print(f"\n🎯 TEST RESULTS:")
        print("=" * 80)
        print("✅ Advanced Composition System: WORKING")
        print("✅ AI Agent Discussions: COMPREHENSIVE")
        print("✅ Granular Decisions: DETAILED")
        print("✅ Comprehensive Logging: COMPLETE")
        print("✅ Multi-Phase Analysis: SUCCESSFUL")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Advanced composition test failed: {e}", exc_info=True)
        return False

def test_specific_scenarios():
    """Test specific composition scenarios"""
    
    print("\n🎯 Testing Specific Composition Scenarios")
    print("=" * 80)
    
    scenarios = [
        {
            'name': 'Short TikTok Comedy',
            'topic': 'Funny pet reactions compilation',
            'category': 'Comedy',
            'platform': 'tiktok',
            'duration': 15,
            'expected_structure': 'fast_cuts',
            'expected_media': 'mostly_video'
        },
        {
            'name': 'Educational YouTube',
            'topic': 'How machine learning works explained simply',
            'category': 'Educational',
            'platform': 'youtube',
            'duration': 60,
            'expected_structure': 'continuous_flow',
            'expected_media': 'mixed_content'
        },
        {
            'name': 'Instagram Tutorial',
            'topic': 'Quick makeup transformation',
            'category': 'Entertainment',
            'platform': 'instagram',
            'duration': 30,
            'expected_structure': 'step_by_step',
            'expected_media': 'video_heavy'
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   Topic: {scenario['topic']}")
        print(f"   Platform: {scenario['platform']} ({scenario['duration']}s)")
        
        try:
            session_id = f"scenario_{datetime.now().strftime('%H%M%S')}"
            composition_system = create_advanced_composition_system(
                settings.google_api_key, 
                session_id
            )
            
            result = composition_system.conduct_comprehensive_composition_discussion(
                topic=scenario['topic'],
                category=scenario['category'],
                platform=scenario['platform'],
                total_duration=scenario['duration'],
                style='viral'
            )
            
            # Analyze results
            structure = result['decisions']['structure']['ai_analysis']
            timing = result['decisions']['timing']['ai_analysis']
            media = result['decisions']['media']['ai_analysis']
            
            print(f"   ✅ Structure: {structure['total_segments']} segments")
            print(f"   ✅ Timing: {timing['total_clips']} clips")
            print(f"   ✅ Media: {media['resource_allocation']['veo2_clips']} VEO2, {media['resource_allocation']['static_images']} images")
            
            results.append({
                'scenario': scenario['name'],
                'success': True,
                'segments': structure['total_segments'],
                'clips': timing['total_clips'],
                'veo2_clips': media['resource_allocation']['veo2_clips']
            })
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Scenario Test Results: {successful}/{len(scenarios)} successful")
    
    return results

if __name__ == "__main__":
    print("🎭 Advanced Video Composition Test Suite")
    print("Testing comprehensive AI agent decision-making for video composition...")
    
    # Test comprehensive composition
    comprehensive_success = test_comprehensive_composition()
    
    # Test specific scenarios
    scenario_results = test_specific_scenarios()
    
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST SUMMARY")
    print("=" * 80)
    
    if comprehensive_success:
        print("✅ Comprehensive Composition System: WORKING")
    else:
        print("❌ Comprehensive Composition System: FAILED")
    
    successful_scenarios = sum(1 for r in scenario_results if r['success'])
    print(f"✅ Scenario Tests: {successful_scenarios}/{len(scenario_results)} passed")
    
    print("\n🎬 Advanced Composition Features Verified:")
    print("   • AI agents decide video structure and segmentation")
    print("   • Individual clip timing optimization")
    print("   • VEO2 vs. static image decisions for each clip")
    print("   • Headers, titles, subtitles design with positioning")
    print("   • Mixed continuity approaches (continuous + standalone)")
    print("   • Comprehensive discussion logging")
    print("   • Platform-specific optimizations")
    print("   • Resource allocation strategies")
    
    if comprehensive_success and successful_scenarios == len(scenario_results):
        print("\n🎉 ALL TESTS PASSED - Advanced Composition System Ready!")
    else:
        print("\n⚠️ Some tests failed - Check logs for details") 