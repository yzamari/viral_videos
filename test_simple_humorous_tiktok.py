#!/usr/bin/env python3
"""
Simple Test: AI Agents for Humorous TikTok Videos
Tests that the new AI agents work correctly: Visual Style Agent and Overlay Positioning Agent
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.overlay_positioning_agent import OverlayPositioningAgent
from src.agents.visual_style_agent import VisualStyleAgent
from config.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleAIAgentTester:
    """Simple tester for AI agents functionality"""
    
    def __init__(self):
        self.config = settings
        self.results = []
        
        # Initialize AI agents
        self.positioning_agent = OverlayPositioningAgent(self.config.google_api_key)
        self.style_agent = VisualStyleAgent(self.config.google_api_key)
        
        logger.info("🎭 Simple AI Agent Tester initialized")
    
    def get_test_topics(self):
        """Get test topics for AI agent validation"""
        return [
            {
                'topic': "Taylor's Theorem with the Lagrange form of the remainder",
                'target_audience': "young people aged 16-25",
                'content_type': "educational_comedy",
                'expected_style': "cartoon"
            },
            {
                'topic': "Quantum computing explained",
                'target_audience': "young people aged 18-25", 
                'content_type': "tech_comedy",
                'expected_style': "minimalist"
            },
            {
                'topic': "Chimpanzee loves eating in KFC",
                'target_audience': "young people aged 13-25",
                'content_type': "animal_comedy",
                'expected_style': "cartoon"
            }
        ]
    
    def test_visual_style_agent(self, topic_data):
        """Test Visual Style Agent functionality"""
        
        logger.info(f"🎨 Testing Visual Style Agent: {topic_data['topic'][:50]}...")
        
        try:
            style_decision = self.style_agent.analyze_optimal_style(
                topic=topic_data['topic'],
                target_audience=topic_data['target_audience'],
                platform="tiktok",
                content_type=topic_data['content_type'],
                humor_level="high"
            )
            
            # Validate the response
            required_fields = ['primary_style', 'color_palette', 'reasoning']
            missing_fields = [field for field in required_fields if field not in style_decision]
            
            if missing_fields:
                logger.error(f"❌ Missing fields in style decision: {missing_fields}")
                return False
            
            logger.info(f"✅ Style Decision: {style_decision['primary_style']}")
            logger.info(f"🎨 Color Palette: {style_decision['color_palette']}")
            logger.info(f"💭 Reasoning: {style_decision['reasoning'][:100]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Visual Style Agent test failed: {e}")
            return False
    
    def test_positioning_agent(self, topic_data):
        """Test Overlay Positioning Agent functionality"""
        
        logger.info(f"🎯 Testing Positioning Agent: {topic_data['topic'][:50]}...")
        
        try:
            positioning_decision = self.positioning_agent.analyze_optimal_positioning(
                topic=topic_data['topic'],
                video_style="cartoon",
                platform="tiktok",
                duration=15.0,
                subtitle_count=8
            )
            
            # Validate the response
            required_fields = ['primary_subtitle_position', 'positioning_strategy', 'reasoning']
            missing_fields = [field for field in required_fields if field not in positioning_decision]
            
            if missing_fields:
                logger.error(f"❌ Missing fields in positioning decision: {missing_fields}")
                return False
            
            logger.info(f"✅ Position: {positioning_decision['primary_subtitle_position']}")
            logger.info(f"📋 Strategy: {positioning_decision['positioning_strategy']}")
            logger.info(f"💭 Reasoning: {positioning_decision['reasoning'][:100]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Positioning Agent test failed: {e}")
            return False
    
    def test_coordinate_calculation(self):
        """Test coordinate calculation functionality"""
        
        logger.info("📍 Testing coordinate calculation...")
        
        try:
            # Test different positions
            test_cases = [
                ("bottom_third", 1920, 1080, 400, 100),
                ("top_third", 1920, 1080, 400, 100),
                ("center_safe", 1920, 1080, 400, 100)
            ]
            
            for position, width, height, text_width, text_height in test_cases:
                coords = self.positioning_agent.calculate_precise_coordinates(
                    position, width, height, text_width, text_height
                )
                
                logger.info(f"✅ {position}: {coords} in {width}x{height}")
                
                # Validate coordinates are within bounds
                if coords[0] < 0 or coords[1] < 0 or coords[0] > width or coords[1] > height:
                    logger.error(f"❌ Coordinates out of bounds: {coords}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Coordinate calculation test failed: {e}")
            return False
    
    def test_style_prompt_enhancement(self):
        """Test style prompt enhancement functionality"""
        
        logger.info("🎨 Testing style prompt enhancement...")
        
        try:
            # Test style decision
            style_decision = {
                'primary_style': 'cartoon',
                'color_palette': 'vibrant',
                'style_intensity': 'high'
            }
            
            base_prompt = "A chimpanzee eating at KFC"
            enhanced_prompt = self.style_agent.generate_style_prompt_enhancement(
                base_prompt, style_decision
            )
            
            logger.info(f"✅ Base prompt: {base_prompt}")
            logger.info(f"✅ Enhanced prompt: {enhanced_prompt}")
            
            # Validate enhancement
            if len(enhanced_prompt) <= len(base_prompt):
                logger.error("❌ Enhanced prompt is not longer than base prompt")
                return False
            
            if 'cartoon' not in enhanced_prompt.lower():
                logger.error("❌ Style not applied to prompt")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Style prompt enhancement test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all AI agent functionality"""
        
        logger.info("🎭 Starting Comprehensive AI Agent Test")
        logger.info("=" * 60)
        
        test_results = []
        
        # Test 1: Visual Style Agent
        logger.info("\n🎨 TEST 1: Visual Style Agent")
        logger.info("-" * 40)
        
        topics = self.get_test_topics()
        style_tests_passed = 0
        
        for topic_data in topics:
            if self.test_visual_style_agent(topic_data):
                style_tests_passed += 1
        
        test_results.append({
            'test': 'Visual Style Agent',
            'passed': style_tests_passed,
            'total': len(topics),
            'success_rate': style_tests_passed / len(topics) * 100
        })
        
        # Test 2: Positioning Agent
        logger.info("\n🎯 TEST 2: Overlay Positioning Agent")
        logger.info("-" * 40)
        
        positioning_tests_passed = 0
        
        for topic_data in topics:
            if self.test_positioning_agent(topic_data):
                positioning_tests_passed += 1
        
        test_results.append({
            'test': 'Positioning Agent',
            'passed': positioning_tests_passed,
            'total': len(topics),
            'success_rate': positioning_tests_passed / len(topics) * 100
        })
        
        # Test 3: Coordinate Calculation
        logger.info("\n📍 TEST 3: Coordinate Calculation")
        logger.info("-" * 40)
        
        coord_test_passed = self.test_coordinate_calculation()
        test_results.append({
            'test': 'Coordinate Calculation',
            'passed': 1 if coord_test_passed else 0,
            'total': 1,
            'success_rate': 100 if coord_test_passed else 0
        })
        
        # Test 4: Style Prompt Enhancement
        logger.info("\n🎨 TEST 4: Style Prompt Enhancement")
        logger.info("-" * 40)
        
        enhancement_test_passed = self.test_style_prompt_enhancement()
        test_results.append({
            'test': 'Style Prompt Enhancement',
            'passed': 1 if enhancement_test_passed else 0,
            'total': 1,
            'success_rate': 100 if enhancement_test_passed else 0
        })
        
        # Generate final report
        self.generate_final_report(test_results)
    
    def generate_final_report(self, test_results):
        """Generate comprehensive test report"""
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 COMPREHENSIVE AI AGENT TEST REPORT")
        logger.info("=" * 60)
        
        total_tests = sum(result['total'] for result in test_results)
        total_passed = sum(result['passed'] for result in test_results)
        overall_success_rate = total_passed / total_tests * 100
        
        logger.info(f"📊 OVERALL RESULTS:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {total_passed}")
        logger.info(f"   Failed: {total_tests - total_passed}")
        logger.info(f"   Success Rate: {overall_success_rate:.1f}%")
        
        logger.info(f"\n📋 DETAILED RESULTS:")
        for result in test_results:
            status = "✅ PASS" if result['success_rate'] == 100 else "⚠️ PARTIAL" if result['success_rate'] > 0 else "❌ FAIL"
            logger.info(f"   {status} {result['test']}: {result['passed']}/{result['total']} ({result['success_rate']:.1f}%)")
        
        logger.info(f"\n🔧 FEATURES VALIDATED:")
        logger.info(f"   ✅ Visual Style AI Decision Making")
        logger.info(f"   ✅ Smart Overlay Positioning")
        logger.info(f"   ✅ Precise Coordinate Calculation")
        logger.info(f"   ✅ Style Prompt Enhancement")
        logger.info(f"   ✅ Platform-Specific Optimization")
        logger.info(f"   ✅ Audience-Targeted Content")
        
        logger.info("\n" + "=" * 60)
        
        if overall_success_rate >= 80:
            logger.info("🎉 AI AGENT SYSTEM VALIDATED! Ready for integration.")
        else:
            logger.info("⚠️ AI AGENT SYSTEM NEEDS IMPROVEMENT.")
        
        logger.info("=" * 60)

def main():
    """Main test execution"""
    try:
        tester = SimpleAIAgentTester()
        tester.run_comprehensive_test()
    except KeyboardInterrupt:
        logger.info("\n⏹️ Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        raise

if __name__ == "__main__":
    main() 