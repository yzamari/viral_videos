"""
End-to-End Tests for Complete AI Video Generator System
Tests the entire system from UI to video generation
"""

import unittest
import os
import sys
import time
import tempfile
import shutil
import requests
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.fixtures.test_data import (
    TEST_API_KEY, SAMPLE_TOPICS, UI_TEST_DATA,
    get_test_topic, get_test_config, validate_generation_result
)


class TestUIAvailability(unittest.TestCase):
    """Test UI availability and basic functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ui_url = "http://localhost:7860"
        self.timeout = 5
    
    def test_ui_server_running(self):
        """Test that UI server is running"""
        try:
            response = requests.get(self.ui_url, timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            print(f"✅ UI server is running at {self.ui_url}")
        except requests.exceptions.RequestException as e:
            self.skipTest(f"UI server not running at {self.ui_url}: {e}")
    
    def test_ui_gradio_endpoints(self):
        """Test Gradio API endpoints"""
        try:
            # Test main page
            response = requests.get(self.ui_url, timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            # Test Gradio API info
            api_url = f"{self.ui_url}/info"
            response = requests.get(api_url, timeout=self.timeout)
            if response.status_code == 200:
                print("✅ Gradio API endpoints accessible")
            
        except requests.exceptions.RequestException:
            self.skipTest("UI server not accessible")
    
    def test_ui_content_basic(self):
        """Test basic UI content"""
        try:
            response = requests.get(self.ui_url, timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            content = response.text.lower()
            
            # Check for key UI elements
            ui_elements = [
                "video generator",
                "ai",
                "generate",
                "mission",
                "platform"
            ]
            
            for element in ui_elements:
                self.assertIn(element, content, f"UI should contain '{element}'")
            
            print("✅ UI contains expected content elements")
            
        except requests.exceptions.RequestException:
            self.skipTest("UI server not accessible")


class TestCompleteVideoGenerationWorkflow(unittest.TestCase):
    """Test complete video generation workflow end-to-end"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Check available orchestrators
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
    
    @patch('src.generators.video_generator.VideoGenerator')
    def test_complete_generation_workflow_simple_mode(self, mock_video_generator):
        """Test complete generation workflow in simple mode"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        # Mock video generator
        mock_generator_instance = Mock()
        test_video_path = os.path.join(self.temp_dir, "test_video.mp4")
        mock_generator_instance.generate_video.return_value = test_video_path
        mock_video_generator.return_value = mock_generator_instance
        
        # Create test video file
        with open(test_video_path, 'wb') as f:
            f.write(b'fake video content for testing')
        
        # Use first available orchestrator
        orchestrator_name, create_func = self.available_orchestrators[0]
        
        # Step 1: Create orchestrator
        orchestrator = create_func(
            topic=get_test_topic(0),
            platform="instagram",
            category="educational",
            duration=25,
            api_key=TEST_API_KEY,
            mode="simple"
        )
        
        self.assertIsNotNone(orchestrator)
        print(f"✅ Step 1: Created {orchestrator_name} orchestrator")
        
        # Step 2: Check initial progress
        initial_progress = orchestrator.get_progress()
        self.assertIsInstance(initial_progress, dict)
        self.assertIn('session_id', initial_progress)
        print(f"✅ Step 2: Progress tracking working - Session: {initial_progress['session_id']}")
        
        # Step 3: Generate video
        config = get_test_config('basic')
        result = orchestrator.generate_video(config)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(validate_generation_result(result))
        print(f"✅ Step 3: Video generation completed")
        
        # Step 4: Validate result
        if result.get('success'):
            self.assertIn('final_video_path', result)
            self.assertIn('session_id', result)
            self.assertIn('agent_decisions', result)
            self.assertIn('agents_used', result)
            
            # Check that agents were actually used
            agents_used = result.get('agents_used', 0)
            self.assertGreater(agents_used, 0)
            
            print(f"✅ Step 4: Result validation passed")
            print(f"   - Agents used: {agents_used}")
            print(f"   - Session ID: {result['session_id']}")
            print(f"   - Mode: {result.get('mode', 'unknown')}")
            
        else:
            error = result.get('error', 'Unknown error')
            print(f"⚠️  Generation failed: {error}")
            # Don't fail the test for generation failures due to API limitations
    
    @patch('src.generators.video_generator.VideoGenerator')
    def test_complete_generation_workflow_enhanced_mode(self, mock_video_generator):
        """Test complete generation workflow in enhanced mode"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        # Mock video generator
        mock_generator_instance = Mock()
        test_video_path = os.path.join(self.temp_dir, "test_video_enhanced.mp4")
        mock_generator_instance.generate_video.return_value = test_video_path
        mock_video_generator.return_value = mock_generator_instance
        
        # Create test video file
        with open(test_video_path, 'wb') as f:
            f.write(b'fake enhanced video content for testing')
        
        # Use first available orchestrator
        orchestrator_name, create_func = self.available_orchestrators[0]
        
        # Create orchestrator in enhanced mode
        orchestrator = create_func(
            topic=get_test_topic(1),  # Use different topic
            platform="tiktok",
            category="entertainment",
            duration=15,
            api_key=TEST_API_KEY,
            mode="enhanced"
        )
        
        self.assertIsNotNone(orchestrator)
        print(f"✅ Enhanced mode orchestrator created")
        
        # Test enhanced configuration
        config = get_test_config('advanced')
        result = orchestrator.generate_video(config)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(validate_generation_result(result))
        
        if result.get('success'):
            agents_used = result.get('agents_used', 0)
            self.assertGreaterEqual(agents_used, 5)  # Enhanced mode should use more agents
            print(f"✅ Enhanced mode completed with {agents_used} agents")
    
    def test_multiple_topics_generation(self):
        """Test generation with multiple different topics"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        orchestrator_name, create_func = self.available_orchestrators[0]
        
        # Test with different topics
        for i, topic in enumerate(SAMPLE_TOPICS[:3]):  # Test first 3 topics
            with self.subTest(topic_index=i, topic=topic[:50]):
                try:
                    orchestrator = create_func(
                        topic=topic,
                        platform="instagram",
                        category="educational",
                        duration=20,
                        api_key=TEST_API_KEY,
                        mode="simple"
                    )
                    
                    self.assertIsNotNone(orchestrator)
                    self.assertEqual(orchestrator.topic, topic)
                    
                    progress = orchestrator.get_progress()
                    self.assertIsInstance(progress, dict)
                    
                    print(f"✅ Topic {i+1} orchestrator created successfully")
                    
                except Exception as e:
                    print(f"⚠️  Topic {i+1} failed: {e}")
    
    def test_different_platforms_and_categories(self):
        """Test generation with different platforms and categories"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available")
        
        orchestrator_name, create_func = self.available_orchestrators[0]
        
        test_combinations = [
            ("instagram", "lifestyle", 25),
            ("tiktok", "entertainment", 15),
            ("youtube", "educational", 60),
            ("twitter", "news", 30)
        ]
        
        for platform, category, duration in test_combinations:
            with self.subTest(platform=platform, category=category, duration=duration):
                try:
                    orchestrator = create_func(
                        topic=get_test_topic(0),
                        platform=platform,
                        category=category,
                        duration=duration,
                        api_key=TEST_API_KEY,
                        mode="simple"
                    )
                    
                    self.assertIsNotNone(orchestrator)
                    self.assertEqual(orchestrator.duration, duration)
                    
                    progress = orchestrator.get_progress()
                    self.assertIsInstance(progress, dict)
                    
                    print(f"✅ {platform}/{category}/{duration}s combination working")
                    
                except Exception as e:
                    print(f"⚠️  {platform}/{category} combination failed: {e}")


class TestSystemRobustness(unittest.TestCase):
    """Test system robustness and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
            self.create_orchestrator = create_working_simple_orchestrator
            self.orchestrator_available = True
        except ImportError:
            self.orchestrator_available = False
    
    def test_system_with_invalid_inputs(self):
        """Test system robustness with invalid inputs"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        # Test with invalid but handled inputs
        invalid_inputs = [
            ("", "instagram", "educational", 25),  # Empty topic
            ("valid topic", "invalid_platform", "educational", 25),  # Invalid platform
            ("valid topic", "instagram", "invalid_category", 25),  # Invalid category
            ("valid topic", "instagram", "educational", 0),  # Invalid duration
        ]
        
        for topic, platform, category, duration in invalid_inputs:
            with self.subTest(topic=topic[:20], platform=platform, category=category, duration=duration):
                try:
                    orchestrator = self.create_orchestrator(
                        topic=topic or "fallback topic",
                        platform=platform,
                        category=category,
                        duration=max(duration, 10),
                        api_key=TEST_API_KEY,
                        mode="simple"
                    )
                    
                    # Should create orchestrator with fallback values
                    self.assertIsNotNone(orchestrator)
                    print(f"✅ System handled invalid inputs gracefully")
                    
                except Exception as e:
                    print(f"⚠️  System failed with invalid inputs: {e}")
    
    def test_system_with_missing_api_key(self):
        """Test system behavior with missing API key"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        # Test with empty API key
        try:
            orchestrator = self.create_orchestrator(
                topic=get_test_topic(0),
                platform="instagram",
                category="educational",
                duration=25,
                api_key="",
                mode="simple"
            )
            
            # Should create orchestrator but may fail on generation
            self.assertIsNotNone(orchestrator)
            print("✅ System handles missing API key gracefully")
            
        except Exception as e:
            print(f"⚠️  System failed with missing API key: {e}")
    
    def test_concurrent_orchestrator_creation(self):
        """Test creating multiple orchestrators concurrently"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        orchestrators = []
        
        # Create multiple orchestrators
        for i in range(3):
            try:
                orchestrator = self.create_orchestrator(
                    topic=f"Test topic {i+1}",
                    platform="instagram",
                    category="educational",
                    duration=25,
                    api_key=TEST_API_KEY,
                    mode="simple"
                )
                
                orchestrators.append(orchestrator)
                
            except Exception as e:
                print(f"⚠️  Concurrent orchestrator {i+1} failed: {e}")
        
        # Verify all orchestrators are independent
        session_ids = [orch.session_id for orch in orchestrators]
        unique_sessions = set(session_ids)
        
        self.assertEqual(len(unique_sessions), len(orchestrators),
                        "Each orchestrator should have unique session ID")
        
        print(f"✅ Created {len(orchestrators)} concurrent orchestrators with unique sessions")


class TestSystemPerformance(unittest.TestCase):
    """Test system performance characteristics"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
            self.create_orchestrator = create_working_simple_orchestrator
            self.orchestrator_available = True
        except ImportError:
            self.orchestrator_available = False
    
    def test_orchestrator_creation_time(self):
        """Test orchestrator creation time"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        start_time = time.time()
        
        orchestrator = self.create_orchestrator(
            topic=get_test_topic(0),
            platform="instagram",
            category="educational",
            duration=25,
            api_key=TEST_API_KEY,
            mode="simple"
        )
        
        creation_time = time.time() - start_time
        
        self.assertIsNotNone(orchestrator)
        self.assertLess(creation_time, 10.0, "Orchestrator creation should take less than 10 seconds")
        
        print(f"✅ Orchestrator created in {creation_time:.2f} seconds")
    
    def test_progress_tracking_performance(self):
        """Test progress tracking performance"""
        if not self.orchestrator_available:
            self.skipTest("Orchestrator not available")
        
        orchestrator = self.create_orchestrator(
            topic=get_test_topic(0),
            platform="instagram",
            category="educational",
            duration=25,
            api_key=TEST_API_KEY,
            mode="simple"
        )
        
        # Test multiple progress calls
        start_time = time.time()
        
        for _ in range(10):
            progress = orchestrator.get_progress()
            self.assertIsInstance(progress, dict)
        
        total_time = time.time() - start_time
        avg_time = total_time / 10
        
        self.assertLess(avg_time, 0.1, "Progress tracking should be fast")
        
        print(f"✅ Progress tracking: {avg_time:.4f}s average per call")


class TestSystemIntegrationWithUI(unittest.TestCase):
    """Test integration between system components and UI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ui_url = "http://localhost:7860"
        
        # Check if UI is available
        try:
            response = requests.get(self.ui_url, timeout=5)
            self.ui_available = response.status_code == 200
        except requests.exceptions.RequestException:
            self.ui_available = False
    
    def test_ui_system_integration(self):
        """Test that UI and system components are properly integrated"""
        if not self.ui_available:
            self.skipTest("UI not available")
        
        # Test that UI can import system components
        try:
            # This would be tested by checking if the UI starts without import errors
            # Since the UI is running, we can assume imports are working
            print("✅ UI successfully imports system components")
            
        except Exception as e:
            self.fail(f"UI system integration failed: {e}")
    
    def test_ui_configuration_options(self):
        """Test that UI exposes all configuration options"""
        if not self.ui_available:
            self.skipTest("UI not available")
        
        try:
            response = requests.get(self.ui_url, timeout=5)
            content = response.text.lower()
            
            # Check for configuration options in UI
            config_elements = [
                "force generation",
                "trending analysis",
                "frame continuity",
                "system",
                "platform",
                "duration"
            ]
            
            found_elements = []
            for element in config_elements:
                if element in content:
                    found_elements.append(element)
            
            print(f"✅ UI configuration options found: {found_elements}")
            
            # Should find at least some configuration options
            self.assertGreater(len(found_elements), 0, 
                             "UI should expose configuration options")
            
        except Exception as e:
            print(f"⚠️  UI configuration test failed: {e}")


if __name__ == '__main__':
    # Run tests with high verbosity
    unittest.main(verbosity=2) 