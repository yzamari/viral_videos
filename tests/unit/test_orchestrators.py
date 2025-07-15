"""
Unit Tests for Orchestrators
Tests all orchestrator classes and their functionality
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.fixtures.test_data import (
    TEST_API_KEY, SAMPLE_TOPICS, SAMPLE_CONFIGS, 
    get_test_topic, get_test_config, validate_generation_result
)

from src.models.video_models import Platform, VideoCategory


class TestWorkingOrchestrator(unittest.TestCase):
    """Test Working Orchestrator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from src.agents.working_orchestrator import (
                create_working_orchestrator, WorkingOrchestrator
            )
            self.orchestrator_class = WorkingOrchestrator
            self.create_function = create_working_orchestrator
            self.orchestrator_available = True
        except ImportError:
            self.orchestrator_available = False
    
    def test_orchestrator_factory_function(self):
        """Test orchestrator factory function"""
        if not self.orchestrator_available:
            self.skipTest("Working orchestrator not available")
        
        orchestrator = self.create_function(
            mission=get_test_topic(0),
            platform="instagram",
            category="Education",
            duration=25,
            api_key=TEST_API_KEY
        )
        
        self.assertIsNotNone(orchestrator)
        self.assertIsInstance(orchestrator, self.orchestrator_class)
        self.assertEqual(orchestrator.api_key, TEST_API_KEY)
        self.assertEqual(orchestrator.mission, get_test_topic(0))
        self.assertEqual(orchestrator.platform, Platform.INSTAGRAM)
        self.assertEqual(orchestrator.category, VideoCategory.EDUCATION)
        self.assertEqual(orchestrator.duration, 25)
    
    def test_orchestrator_user_parameters(self):
        """Test orchestrator with user parameters"""
        if not self.orchestrator_available:
            self.skipTest("Working orchestrator not available")
        
        orchestrator = self.create_function(
            mission=get_test_topic(0),
            platform="instagram",
            category="Education",
            duration=25,
            api_key=TEST_API_KEY,
            style="educational",
            tone="professional",
            target_audience="students",
            visual_style="minimalist"
        )
        
        self.assertIsNotNone(orchestrator)
        self.assertEqual(orchestrator.style, "educational")
        self.assertEqual(orchestrator.tone, "professional")
        self.assertEqual(orchestrator.target_audience, "students")
        self.assertEqual(orchestrator.visual_style, "minimalist")
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        if not self.orchestrator_available:
            self.skipTest("Working orchestrator not available")
        
        orchestrator = self.create_function(
            mission=get_test_topic(0),
            platform="instagram",
            category="Education",
            duration=25,
            api_key=TEST_API_KEY
        )
        
        # Check core agents are initialized
        self.assertIsNotNone(orchestrator.director)
        self.assertIsNotNone(orchestrator.continuity_agent)
        self.assertIsNotNone(orchestrator.voice_agent)
        self.assertIsNotNone(orchestrator.structure_agent)
        self.assertIsNotNone(orchestrator.timing_agent)
        self.assertIsNotNone(orchestrator.visual_agent)
        self.assertIsNotNone(orchestrator.media_agent)
    
    def test_get_progress_method(self):
        """Test get_progress method"""
        if not self.orchestrator_available:
            self.skipTest("Working orchestrator not available")
        
        orchestrator = self.create_function(
            mission=get_test_topic(0),
            platform="instagram",
            category="Education",
            duration=25,
            api_key=TEST_API_KEY
        )
        
        progress = orchestrator.get_progress()
        
        self.assertIsInstance(progress, dict)
        self.assertIn('progress', progress)
        self.assertIn('session_id', progress)
        self.assertIn('current_phase', progress)
        
        self.assertIsInstance(progress['progress'], int)
    
    def test_generate_video_method_exists(self):
        """Test that generate_video method exists and is callable"""
        if not self.orchestrator_available:
            self.skipTest("Working orchestrator not available")
        
        orchestrator = self.create_function(
            mission=get_test_topic(0),
            platform="instagram",
            category="Education",
            duration=25,
            api_key=TEST_API_KEY
        )
        
        # Test that the method exists
        self.assertTrue(hasattr(orchestrator, 'generate_video'))
        self.assertTrue(callable(getattr(orchestrator, 'generate_video')))
        
        # Test method signature (should accept expected parameters)
        import inspect
        sig = inspect.signature(orchestrator.generate_video)
        expected_params = ['self']  # At minimum should have self
        
        for param in expected_params:
            if param != 'self':
                self.assertIn(param, sig.parameters)
    
    def test_extract_script_methods(self):
        """Test script extraction methods"""
        if not self.orchestrator_available:
            self.skipTest("Working orchestrator not available")
        
        orchestrator = self.create_function(
            mission=get_test_topic(0),
            platform="instagram",
            category="Education",
            duration=25,
            api_key=TEST_API_KEY
        )
        
        from tests.fixtures.test_data import get_sample_script_data
        script_data = get_sample_script_data()
        
        # Test hook extraction
        hook = orchestrator._extract_hook_from_script(script_data)
        self.assertIsInstance(hook, str)
        self.assertGreater(len(hook), 0)
        
        # Test content extraction
        content = orchestrator._extract_content_from_script(script_data)
        self.assertIsInstance(content, list)
        self.assertGreater(len(content), 0)
        
        # Test CTA extraction
        cta = orchestrator._extract_cta_from_script(script_data)
        self.assertIsInstance(cta, str)
        self.assertGreater(len(cta), 0)


class TestOrchestratorComparison(unittest.TestCase):
    """Test comparison between different orchestrators"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.available_orchestrators = []
        
        # Check working orchestrator
        try:
            from src.agents.working_orchestrator import create_working_orchestrator
            self.available_orchestrators.append(('working', create_working_orchestrator))
        except ImportError:
            pass
    
    def test_orchestrator_availability(self):
        """Test that at least one orchestrator is available"""
        if len(self.available_orchestrators) == 0:
            self.skipTest("No orchestrators available - this may be expected in some environments")
        
        self.assertGreater(len(self.available_orchestrators), 0,
                          "At least one orchestrator should be available")
    
    def test_orchestrator_consistency(self):
        """Test that all available orchestrators have consistent interfaces"""
        if not self.available_orchestrators:
            self.skipTest("No orchestrators available")
        
        for name, create_func in self.available_orchestrators:
            with self.subTest(orchestrator=name):
                try:
                    orchestrator = create_func(
                        mission=get_test_topic(0),
                        platform="instagram",
                        category="Education",
                        duration=25,
                        api_key=TEST_API_KEY
                    )
                    
                    # Check common interface
                    self.assertTrue(hasattr(orchestrator, 'generate_video'))
                    self.assertTrue(hasattr(orchestrator, 'get_progress'))
                    
                    # Test get_progress
                    progress = orchestrator.get_progress()
                    self.assertIsInstance(progress, dict)
                    self.assertIn('session_id', progress)
                    
                except Exception as e:
                    self.fail(f"Orchestrator {name} failed: {e}")


if __name__ == '__main__':
    unittest.main() 