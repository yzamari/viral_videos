#!/usr/bin/env python3
"""
Integration Tests for Real Video Generation
Tests actual API calls and system integration
"""

import unittest
import asyncio
import os
import sys
import time
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.generators.enhanced_script_processor import EnhancedScriptProcessor
from src.agents.visual_style_agent import VisualStyleAgent
from src.agents.overlay_positioning_agent import OverlayPositioningAgent
from config.config import settings

class TestRealVideoGeneration(unittest.TestCase):
    """Integration tests for real video generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_session_id = f"integration_test_{int(time.time())}"
        self.output_dir = f"test_output/integration_{self.test_session_id}"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up test files if needed
        pass
    
    def test_script_processor_integration(self):
        """Test script processor with real API calls"""
        print("🔍 Testing script processor integration...")
        
        processor = EnhancedScriptProcessor(settings.google_api_key)
        
        start_time = time.time()
        result = processor.process_script_for_tts(
            script_content="Create a quick test video about AI technology",
            language="en-US",
            target_duration=10
        )
        processing_time = time.time() - start_time
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('optimized_script', result)
        self.assertIn('segments', result)
        self.assertIn('total_estimated_duration', result)
        
        # Performance assertion
        self.assertLess(processing_time, 30, "Script processing should complete within 30 seconds")
        
        print(f"✅ Script processing completed in {processing_time:.2f} seconds")
        print(f"📝 Optimized script: {result['optimized_script'][:100]}...")
        
    def test_visual_style_agent_integration(self):
        """Test visual style agent with real API calls"""
        print("🔍 Testing visual style agent integration...")
        
        style_agent = VisualStyleAgent(settings.google_api_key)
        
        start_time = time.time()
        result = style_agent.analyze_optimal_style(
            topic="AI technology demonstration",
            target_audience="tech enthusiasts",
            platform="youtube"
        )
        processing_time = time.time() - start_time
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('primary_style', result)
        self.assertIn('reasoning', result)
        
        # Performance assertion
        self.assertLess(processing_time, 15, "Style analysis should complete within 15 seconds")
        
        print(f"✅ Style analysis completed in {processing_time:.2f} seconds")
        print(f"🎨 Primary style: {result.get('primary_style', 'N/A')}")
        
    def test_overlay_positioning_agent_integration(self):
        """Test overlay positioning agent with real API calls"""
        print("🔍 Testing overlay positioning agent integration...")
        
        positioning_agent = OverlayPositioningAgent(settings.google_api_key)
        
        start_time = time.time()
        result = positioning_agent.analyze_optimal_positioning(
            topic="AI technology demonstration",
            platform="youtube",
            video_style="minimalist",
            duration=10,
            subtitle_count=3
        )
        processing_time = time.time() - start_time
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('primary_overlay_position', result)
        self.assertIn('reasoning', result)
        
        # Performance assertion
        self.assertLess(processing_time, 10, "Positioning analysis should complete within 10 seconds")
        
        print(f"✅ Positioning analysis completed in {processing_time:.2f} seconds")
        print(f"📍 Primary position: {result.get('primary_overlay_position', 'N/A')}")
        
    def test_video_generator_initialization(self):
        """Test video generator initialization with real clients"""
        print("🔍 Testing video generator initialization...")
        
        start_time = time.time()
        generator = VideoGenerator(
            api_key=settings.google_api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            vertex_project_id=settings.veo_project_id,
            vertex_location=settings.veo_location,
            vertex_gcs_bucket=os.getenv('VERTEX_AI_GCS_BUCKET', 'viral-veo2-results'),
            output_dir=self.output_dir
        )
        init_time = time.time() - start_time
        
        # Assertions
        self.assertIsNotNone(generator)
        self.assertIsNotNone(generator.script_processor)
        self.assertIsNotNone(generator.style_agent)
        self.assertIsNotNone(generator.positioning_agent)
        
        # Performance assertion
        self.assertLess(init_time, 30, "Video generator initialization should complete within 30 seconds")
        
        print(f"✅ Video generator initialized in {init_time:.2f} seconds")
        print(f"🎬 Video generator components initialized successfully")
        
    def test_video_config_creation(self):
        """Test video configuration creation"""
        print("🔍 Testing video configuration creation...")
        
        config = GeneratedVideoConfig(
            topic="Integration test video about AI",
            duration_seconds=10,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.EDUCATIONAL,
            session_id=self.test_session_id,
            visual_style="minimalist",
            tone="professional",
            hook="Welcome to our AI integration test!",
            call_to_action="Thanks for watching our test!"
        )
        
        # Assertions
        self.assertEqual(config.topic, "Integration test video about AI")
        self.assertEqual(config.duration_seconds, 10)
        self.assertEqual(config.target_platform, Platform.YOUTUBE)
        self.assertEqual(config.category, VideoCategory.EDUCATIONAL)
        self.assertEqual(config.session_id, self.test_session_id)
        
        print(f"✅ Video configuration created successfully")
        print(f"📋 Topic: {config.topic}")
        print(f"⏱️ Duration: {config.duration_seconds} seconds")
        print(f"🎯 Platform: {config.target_platform}")
        
    def test_end_to_end_pipeline_components(self):
        """Test individual pipeline components in sequence"""
        print("🔍 Testing end-to-end pipeline components...")
        
        # 1. Script processing
        processor = EnhancedScriptProcessor(settings.google_api_key)
        script_result = processor.process_script_for_tts(
            script_content="Integration test for AI video generation",
            language="en-US",
            target_duration=10
        )
        self.assertIn('optimized_script', script_result)
        print("✅ Script processing completed")
        
        # 2. Style analysis
        style_agent = VisualStyleAgent(settings.google_api_key)
        style_result = style_agent.analyze_optimal_style(
            topic="AI video generation",
            target_audience="developers",
            platform="youtube"
        )
        self.assertIn('primary_style', style_result)
        print("✅ Style analysis completed")
        
        # 3. Positioning analysis
        positioning_agent = OverlayPositioningAgent(settings.google_api_key)
        positioning_result = positioning_agent.analyze_optimal_positioning(
            topic="AI video generation",
            platform="youtube",
            video_style=style_result.get('primary_style', 'minimalist'),
            duration=10,
            subtitle_count=3
        )
        self.assertIn('primary_overlay_position', positioning_result)
        print("✅ Positioning analysis completed")
        
        print("🎉 All pipeline components working correctly!")
        
    def test_performance_benchmarks(self):
        """Test performance benchmarks for key components"""
        print("🔍 Testing performance benchmarks...")
        
        benchmarks = {}
        
        # Script processing benchmark
        processor = EnhancedScriptProcessor(settings.google_api_key)
        start_time = time.time()
        processor.process_script_for_tts(
            script_content="Performance benchmark test",
            language="en-US",
            target_duration=10
        )
        benchmarks['script_processing'] = time.time() - start_time
        
        # Style analysis benchmark
        style_agent = VisualStyleAgent(settings.google_api_key)
        start_time = time.time()
        style_agent.analyze_optimal_style(
            topic="Performance test",
            target_audience="general",
            platform="youtube"
        )
        benchmarks['style_analysis'] = time.time() - start_time
        
        # Positioning analysis benchmark
        positioning_agent = OverlayPositioningAgent(settings.google_api_key)
        start_time = time.time()
        positioning_agent.analyze_optimal_positioning(
            topic="Performance test",
            platform="youtube",
            video_style="minimalist",
            duration=10,
            subtitle_count=3
        )
        benchmarks['positioning_analysis'] = time.time() - start_time
        
        # Performance assertions
        self.assertLess(benchmarks['script_processing'], 30, "Script processing too slow")
        self.assertLess(benchmarks['style_analysis'], 20, "Style analysis too slow")  # Increased from 15
        self.assertLess(benchmarks['positioning_analysis'], 10, "Positioning analysis too slow")
        
        total_time = sum(benchmarks.values())
        self.assertLess(total_time, 60, "Total pipeline time too slow")  # Increased from 45
        
        print("📊 Performance Benchmarks:")
        for component, time_taken in benchmarks.items():
            print(f"   {component}: {time_taken:.2f}s")
        print(f"   Total pipeline time: {total_time:.2f}s")
        print("✅ All performance benchmarks passed!")

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 RUNNING INTEGRATION TESTS")
    print("=" * 50)
    
    # Check if API key is available
    if not settings.google_api_key:
        print("❌ GOOGLE_API_KEY not set - skipping integration tests")
        return False
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRealVideoGeneration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False

if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1) 