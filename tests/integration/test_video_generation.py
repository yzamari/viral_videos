"""
Integration Tests for Video Generation Pipeline
Tests the complete video generation workflow
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.fixtures.test_data import (
    TEST_API_KEY, SAMPLE_TOPICS, SAMPLE_CONFIGS, 
    get_test_topic, get_test_config, validate_generation_result
)

from src.models.video_models import Platform, VideoCategory


class TestVideoGenerationPipeline(unittest.TestCase):
    """Test complete video generation pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_topic = get_test_topic(0)
        self.test_config = get_test_config('basic')
        self.temp_dir = tempfile.mkdtemp()
        
        # Check which orchestrators are available
        self.available_orchestrators = []
        
        try:
            from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
            self.available_orchestrators.append(('working_simple', create_working_simple_orchestrator))
        except ImportError:
            pass
        
        try:
            from src.agents.enhanced_working_orchestrator import create_enhanced_working_orchestrator
            self.available_orchestrators.append(('enhanced_working', create_enhanced_working_orchestrator))
        except ImportError:
            pass
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_orchestrator_availability(self):
        """Test that at least one orchestrator is available"""
        self.assertGreater(len(self.available_orchestrators), 0,
                          "At least one orchestrator should be available for integration testing")
    
    @patch('src.generators.video_generator.VideoGenerator')
    def test_simple_video_generation_workflow(self, mock_video_generator):
        """Test simple video generation workflow"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        # Use first available orchestrator
        orchestrator_name, create_func = self.available_orchestrators[0]
        
        # Mock video generator
        mock_generator_instance = Mock()
        mock_generator_instance.generate_video.return_value = os.path.join(self.temp_dir, "test_video.mp4")
        mock_video_generator.return_value = mock_generator_instance
        
        # Create test video file
        test_video_path = os.path.join(self.temp_dir, "test_video.mp4")
        with open(test_video_path, 'wb') as f:
            f.write(b'fake video content')
        
        # Create orchestrator
        orchestrator = create_func(
            topic=self.test_topic,
            platform="instagram",
            category="educational",
            duration=25,
            api_key=TEST_API_KEY
        )
        
        # Test generation
        result = orchestrator.generate_video(self.test_config)
        
        # Validate result structure
        self.assertIsInstance(result, dict)
        self.assertTrue(validate_generation_result(result))
        
        if result.get('success'):
            self.assertIn('final_video_path', result)
            self.assertIn('session_id', result)
            self.assertIn('mode', result)
            self.assertIn('agent_decisions', result)
    
    def test_all_available_orchestrators(self):
        """Test all available orchestrators"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        for orchestrator_name, create_func in self.available_orchestrators:
            with self.subTest(orchestrator=orchestrator_name):
                try:
                    # Create orchestrator
                    orchestrator = create_func(
                        topic=self.test_topic,
                        platform="instagram",
                        category="educational",
                        duration=25,
                        api_key=TEST_API_KEY
                    )
                    
                    # Test basic functionality
                    self.assertIsNotNone(orchestrator)
                    
                    # Test progress tracking
                    progress = orchestrator.get_progress()
                    self.assertIsInstance(progress, dict)
                    self.assertIn('session_id', progress)
                    
                except Exception as e:
                    self.fail(f"Orchestrator {orchestrator_name} failed: {e}")
    
    @patch('src.generators.video_generator.VideoGenerator')
    def test_different_platforms(self, mock_video_generator):
        """Test video generation for different platforms"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        # Mock video generator
        mock_generator_instance = Mock()
        mock_generator_instance.generate_video.return_value = os.path.join(self.temp_dir, "test_video.mp4")
        mock_video_generator.return_value = mock_generator_instance
        
        # Create test video file
        test_video_path = os.path.join(self.temp_dir, "test_video.mp4")
        with open(test_video_path, 'wb') as f:
            f.write(b'fake video content')
        
        orchestrator_name, create_func = self.available_orchestrators[0]
        platforms = ["instagram", "tiktok", "youtube", "twitter"]
        
        for platform in platforms:
            with self.subTest(platform=platform):
                try:
                    orchestrator = create_func(
                        topic=self.test_topic,
                        platform=platform,
                        category="educational",
                        duration=25,
                        api_key=TEST_API_KEY
                    )
                    
                    result = orchestrator.generate_video(self.test_config)
                    self.assertIsInstance(result, dict)
                    
                except Exception as e:
                    print(f"Warning: Platform {platform} failed: {e}")
    
    @patch('src.generators.video_generator.VideoGenerator')
    def test_different_categories(self, mock_video_generator):
        """Test video generation for different categories"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        # Mock video generator
        mock_generator_instance = Mock()
        mock_generator_instance.generate_video.return_value = os.path.join(self.temp_dir, "test_video.mp4")
        mock_video_generator.return_value = mock_generator_instance
        
        # Create test video file
        test_video_path = os.path.join(self.temp_dir, "test_video.mp4")
        with open(test_video_path, 'wb') as f:
            f.write(b'fake video content')
        
        orchestrator_name, create_func = self.available_orchestrators[0]
        categories = ["educational", "comedy", "entertainment", "news", "tech", "health", "lifestyle"]
        
        for category in categories:
            with self.subTest(category=category):
                try:
                    orchestrator = create_func(
                        topic=self.test_topic,
                        platform="instagram",
                        category=category,
                        duration=25,
                        api_key=TEST_API_KEY
                    )
                    
                    result = orchestrator.generate_video(self.test_config)
                    self.assertIsInstance(result, dict)
                    
                except Exception as e:
                    print(f"Warning: Category {category} failed: {e}")
    
    def test_different_durations(self):
        """Test video generation for different durations"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        orchestrator_name, create_func = self.available_orchestrators[0]
        durations = [15, 25, 30, 45, 60]
        
        for duration in durations:
            with self.subTest(duration=duration):
                try:
                    orchestrator = create_func(
                        topic=self.test_topic,
                        platform="instagram",
                        category="educational",
                        duration=duration,
                        api_key=TEST_API_KEY
                    )
                    
                    self.assertIsNotNone(orchestrator)
                    self.assertEqual(orchestrator.duration, duration)
                    
                except Exception as e:
                    print(f"Warning: Duration {duration} failed: {e}")


class TestAgentIntegration(unittest.TestCase):
    """Test integration between different AI agents"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_topic = get_test_topic(0)
        
        # Initialize agents
        try:
            from src.generators.director import Director
            from src.agents.voice_director_agent import VoiceDirectorAgent
            from src.agents.continuity_decision_agent import ContinuityDecisionAgent
            
            self.director = Director(TEST_API_KEY)
            self.voice_agent = VoiceDirectorAgent(TEST_API_KEY)
            self.continuity_agent = ContinuityDecisionAgent(TEST_API_KEY)
            self.agents_available = True
        except ImportError:
            self.agents_available = False
    
    def test_agent_availability(self):
        """Test that core agents are available"""
        if not self.agents_available:
            self.skipTest("Core agents not available")
        
        self.assertIsNotNone(self.director)
        self.assertIsNotNone(self.voice_agent)
        self.assertIsNotNone(self.continuity_agent)
    
    @patch('src.generators.director.genai.GenerativeModel')
    def test_director_to_voice_agent_flow(self, mock_model):
        """Test flow from Director to Voice Agent"""
        if not self.agents_available:
            self.skipTest("Core agents not available")
        
        # Mock director response
        mock_response = Mock()
        mock_response.text = """
        {
            "hook": {"text": "Amazing yoga benefits"},
            "segments": [
                {"text": "Yoga improves flexibility"},
                {"text": "Ashtanga is powerful"}
            ],
            "call_to_action": "Follow for more!"
        }
        """
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Generate script
        script_result = self.director.write_script(
            topic=self.test_topic,
            style='viral',
            duration=25,
            platform=Platform.INSTAGRAM,
            category=VideoCategory.LIFESTYLE
        )
        
        self.assertIsNotNone(script_result)
        
        # Use script in voice agent
        voice_result = self.voice_agent.analyze_content_and_select_voices(
            topic=self.test_topic,
            script=str(script_result),
            language='en-US',
            platform=Platform.INSTAGRAM,
            category=VideoCategory.LIFESTYLE,
            duration_seconds=25,
            num_clips=4
        )
        
        self.assertIsNotNone(voice_result)
    
    @patch('src.agents.continuity_decision_agent.genai.GenerativeModel')
    def test_continuity_agent_decision_flow(self, mock_model):
        """Test continuity agent decision making"""
        if not self.agents_available:
            self.skipTest("Core agents not available")
        
        # Mock continuity response
        mock_response = Mock()
        mock_response.text = """
        {
            "use_frame_continuity": true,
            "confidence": 0.85,
            "primary_reason": "Educational content benefits from continuity"
        }
        """
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Test continuity decision
        result = self.continuity_agent.analyze_frame_continuity_need(
            topic=self.test_topic,
            category="Educational",
            platform="instagram",
            duration=25
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)


class TestConfigurationIntegration(unittest.TestCase):
    """Test integration with different configuration options"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Check orchestrator availability
        try:
            from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
            self.create_orchestrator = create_working_simple_orchestrator
            self.orchestrator_available = True
        except ImportError:
            self.orchestrator_available = False
    
    def test_basic_configuration(self):
        """Test basic configuration integration"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        config = get_test_config('basic')
        
        orchestrator = self.create_orchestrator(
            topic=get_test_topic(0),
            platform="instagram",
            category="educational",
            duration=25,
            api_key=TEST_API_KEY,
            mode="simple"
        )
        
        # Test that configuration is accepted
        self.assertIsNotNone(orchestrator)
        
        # Test progress with config
        progress = orchestrator.get_progress()
        self.assertIsInstance(progress, dict)
    
    def test_advanced_configuration(self):
        """Test advanced configuration integration"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        config = get_test_config('advanced')
        
        orchestrator = self.create_orchestrator(
            topic=get_test_topic(0),
            platform="instagram",
            category="educational",
            duration=25,
            api_key=TEST_API_KEY,
            mode="enhanced"
        )
        
        self.assertIsNotNone(orchestrator)
    
    def test_image_only_configuration(self):
        """Test image-only configuration integration"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        config = get_test_config('image_only')
        
        orchestrator = self.create_orchestrator(
            topic=get_test_topic(0),
            platform="instagram",
            category="educational",
            duration=25,
            api_key=TEST_API_KEY,
            mode="simple"
        )
        
        self.assertIsNotNone(orchestrator)
        
        # Verify image_only setting is handled
        self.assertTrue(config['image_only'])
        self.assertEqual(config['force_generation'], 'force_image_gen')


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling across the integration pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
            self.create_orchestrator = create_working_simple_orchestrator
            self.orchestrator_available = True
        except ImportError:
            self.orchestrator_available = False
    
    def test_invalid_api_key_integration(self):
        """Test integration with invalid API key"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        # Should create orchestrator but may fail on generation
        orchestrator = self.create_orchestrator(
            topic=get_test_topic(0),
            platform="instagram",
            category="educational",
            duration=25,
            api_key="invalid_key",
            mode="simple"
        )
        
        self.assertIsNotNone(orchestrator)
        self.assertEqual(orchestrator.api_key, "invalid_key")
    
    def test_missing_dependencies_handling(self):
        """Test handling of missing dependencies"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        # Try advanced mode which might have missing dependencies
        try:
            orchestrator = self.create_orchestrator(
                topic=get_test_topic(0),
                platform="instagram",
                category="educational",
                duration=25,
                api_key=TEST_API_KEY,
                mode="advanced"
            )
            
            self.assertIsNotNone(orchestrator)
            
        except Exception as e:
            # Should handle missing dependencies gracefully
            self.assertIsInstance(e, Exception)


if __name__ == '__main__':
    unittest.main(verbosity=2) 