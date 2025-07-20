"""
Comprehensive Constructor Syntax Tests
Tests ALL class constructors to catch syntax errors like missing underscores in __init__
This should have caught all the constructor issues we found during runtime.
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

TEST_API_KEY = "test_api_key_12345"
TEST_PROJECT_ID = "test-project-123"
TEST_LOCATION = "us-central1"
TEST_BUCKET = "test-bucket"


class TestConstructorSyntax(unittest.TestCase):
    """Test that ALL class constructors have correct syntax and can be instantiated"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_session_manager_constructor(self):
        """Test SessionManager constructor syntax"""
        try:
            from src.utils.session_manager import SessionManager
            session_manager = SessionManager()
            self.assertIsNotNone(session_manager)
        except Exception as e:
            self.fail(f"SessionManager constructor failed: {e}")
    
    def test_director_constructor(self):
        """Test Director constructor syntax"""
        try:
            from src.generators.director import Director
            director = Director(api_key=TEST_API_KEY)
            self.assertIsNotNone(director)
            self.assertEqual(director.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"Director constructor failed: {e}")
    
    def test_enhanced_script_processor_constructor(self):
        """Test EnhancedScriptProcessor constructor syntax"""
        try:
            from src.generators.enhanced_script_processor import EnhancedScriptProcessor
            processor = EnhancedScriptProcessor(api_key=TEST_API_KEY)
            self.assertIsNotNone(processor)
            self.assertEqual(processor.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"EnhancedScriptProcessor constructor failed: {e}")
    
    def test_video_generator_constructor(self):
        """Test VideoGenerator constructor syntax"""
        try:
            from src.generators.video_generator import VideoGenerator
            generator = VideoGenerator(api_key=TEST_API_KEY)
            self.assertIsNotNone(generator)
            self.assertEqual(generator.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"VideoGenerator constructor failed: {e}")
    
    def test_multi_language_generator_constructor(self):
        """Test MultiLanguageVideoGenerator constructor syntax"""
        try:
            from src.generators.multi_language_generator import MultiLanguageVideoGenerator
            generator = MultiLanguageVideoGenerator(api_key=TEST_API_KEY)
            self.assertIsNotNone(generator)
            self.assertEqual(generator.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"MultiLanguageVideoGenerator constructor failed: {e}")
    
    def test_working_orchestrator_constructor(self):
        """Test WorkingOrchestrator constructor syntax"""
        try:
            from src.agents.working_orchestrator import WorkingOrchestrator
            from src.models.video_models import Platform, VideoCategory
            
            orchestrator = WorkingOrchestrator(
                api_key=TEST_API_KEY,
                mission="Test mission",
                platform=Platform.INSTAGRAM,
                category=VideoCategory.EDUCATION,
                duration=30
            )
            self.assertIsNotNone(orchestrator)
            self.assertEqual(orchestrator.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"WorkingOrchestrator constructor failed: {e}")
    
    def test_voice_director_agent_constructor(self):
        """Test VoiceDirectorAgent constructor syntax"""
        try:
            from src.agents.voice_director_agent import VoiceDirectorAgent
            agent = VoiceDirectorAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(agent)
            self.assertEqual(agent.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"VoiceDirectorAgent constructor failed: {e}")
    
    def test_visual_style_agent_constructor(self):
        """Test VisualStyleAgent constructor syntax"""
        try:
            from src.agents.visual_style_agent import VisualStyleAgent
            agent = VisualStyleAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(agent)
            self.assertEqual(agent.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"VisualStyleAgent constructor failed: {e}")
    
    def test_overlay_positioning_agent_constructor(self):
        """Test OverlayPositioningAgent constructor syntax"""
        try:
            from src.agents.overlay_positioning_agent import OverlayPositioningAgent
            agent = OverlayPositioningAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(agent)
        except Exception as e:
            self.fail(f"OverlayPositioningAgent constructor failed: {e}")
    
    def test_continuity_decision_agent_constructor(self):
        """Test ContinuityDecisionAgent constructor syntax"""
        try:
            from src.agents.continuity_decision_agent import ContinuityDecisionAgent
            agent = ContinuityDecisionAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(agent)
            self.assertEqual(agent.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"ContinuityDecisionAgent constructor failed: {e}")
    
    def test_multi_agent_discussion_constructor(self):
        """Test MultiAgentDiscussionSystem constructor syntax"""
        try:
            from src.agents.multi_agent_discussion import MultiAgentDiscussionSystem
            system = MultiAgentDiscussionSystem(
                api_key=TEST_API_KEY,
                session_id="test_session"
            )
            self.assertIsNotNone(system)
            self.assertEqual(system.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"MultiAgentDiscussionSystem constructor failed: {e}")
    
    def test_gemini_image_client_constructor(self):
        """Test GeminiImageClient constructor syntax"""
        try:
            from src.generators.gemini_image_client import GeminiImageClient
            client = GeminiImageClient(
                api_key=TEST_API_KEY,
                output_dir=self.temp_dir
            )
            self.assertIsNotNone(client)
            self.assertEqual(client.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"GeminiImageClient constructor failed: {e}")
    
    def test_enhanced_multilang_tts_constructor(self):
        """Test EnhancedMultilingualTTS constructor syntax"""
        try:
            from src.generators.enhanced_multilang_tts import EnhancedMultilingualTTS
            tts = EnhancedMultilingualTTS(api_key=TEST_API_KEY)
            self.assertIsNotNone(tts)
            self.assertEqual(tts.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"EnhancedMultilingualTTS constructor failed: {e}")
    
    def test_integrated_multilang_generator_constructor(self):
        """Test IntegratedMultilingualGenerator constructor syntax"""
        try:
            from src.generators.integrated_multilang_generator import IntegratedMultilingualGenerator
            generator = IntegratedMultilingualGenerator(api_key=TEST_API_KEY)
            self.assertIsNotNone(generator)
            self.assertEqual(generator.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"IntegratedMultilingualGenerator constructor failed: {e}")
    
    def test_rtl_validator_constructor(self):
        """Test RTLValidator constructor syntax"""
        try:
            from src.generators.rtl_validator import RTLValidator
            validator = RTLValidator(api_key=TEST_API_KEY)
            self.assertIsNotNone(validator)
            self.assertEqual(validator.api_key, TEST_API_KEY)
        except Exception as e:
            self.fail(f"RTLValidator constructor failed: {e}")
    
    def test_veo_client_factory_constructor(self):
        """Test VeoClientFactory constructor syntax"""
        try:
            from src.generators.veo_client_factory import VeoClientFactory
            factory = VeoClientFactory(
                project_id=TEST_PROJECT_ID,
                location=TEST_LOCATION,
                gcs_bucket=TEST_BUCKET
            )
            self.assertIsNotNone(factory)
            self.assertEqual(factory.project_id, TEST_PROJECT_ID)
        except Exception as e:
            self.fail(f"VeoClientFactory constructor failed: {e}")
    
    def test_vertex_ai_veo2_client_constructor(self):
        """Test VertexAIVeo2Client constructor syntax"""
        try:
            from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
            client = VertexAIVeo2Client(
                project_id=TEST_PROJECT_ID,
                location=TEST_LOCATION,
                gcs_bucket=TEST_BUCKET,
                output_dir=self.temp_dir
            )
            self.assertIsNotNone(client)
            self.assertEqual(client.project_id, TEST_PROJECT_ID)
        except Exception as e:
            self.fail(f"VertexAIVeo2Client constructor failed: {e}")
    
    def test_vertex_veo3_client_constructor(self):
        """Test VertexAIVeo3Client constructor syntax"""
        try:
            from src.generators.vertex_veo3_client import VertexAIVeo3Client
            client = VertexAIVeo3Client(
                project_id=TEST_PROJECT_ID,
                location=TEST_LOCATION,
                gcs_bucket=TEST_BUCKET,
                output_dir=self.temp_dir
            )
            self.assertIsNotNone(client)
            self.assertEqual(client.project_id, TEST_PROJECT_ID)
        except Exception as e:
            self.fail(f"VertexAIVeo3Client constructor failed: {e}")
    
    def test_base_veo_client_constructor(self):
        """Test BaseVeoClient constructor syntax (abstract class)"""
        try:
            from src.generators.base_veo_client import BaseVeoClient
            # BaseVeoClient is abstract, so we can't instantiate it directly
            # But we can test that the constructor syntax is correct by checking the class
            self.assertTrue(hasattr(BaseVeoClient, '__init__'))
            
            # Test that the method signature is correct
            import inspect
            sig = inspect.signature(BaseVeoClient.__init__)
            expected_params = ['self', 'project_id', 'location', 'output_dir']
            for param in expected_params:
                self.assertIn(param, sig.parameters)
        except Exception as e:
            self.fail(f"BaseVeoClient constructor signature check failed: {e}")
    
    def test_vertex_imagen_client_constructor(self):
        """Test VertexImagenClient constructor syntax"""
        try:
            from src.generators.vertex_imagen_client import VertexImagenClient
            client = VertexImagenClient(
                project_id=TEST_PROJECT_ID,
                location=TEST_LOCATION
            )
            self.assertIsNotNone(client)
        except Exception as e:
            self.fail(f"VertexImagenClient constructor failed: {e}")
    
    def test_video_composition_agents_constructors(self):
        """Test Video Composition Agents constructor syntax"""
        try:
            from src.agents.video_composition_agents import (
                VideoStructureAgent, ClipTimingAgent, 
                VisualElementsAgent, MediaTypeAgent
            )
            
            # Test VideoStructureAgent
            structure_agent = VideoStructureAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(structure_agent)
            self.assertEqual(structure_agent.api_key, TEST_API_KEY)
            
            # Test ClipTimingAgent
            timing_agent = ClipTimingAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(timing_agent)
            self.assertEqual(timing_agent.api_key, TEST_API_KEY)
            
            # Test VisualElementsAgent
            visual_agent = VisualElementsAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(visual_agent)
            self.assertEqual(visual_agent.api_key, TEST_API_KEY)
            
            # Test MediaTypeAgent
            media_agent = MediaTypeAgent(api_key=TEST_API_KEY)
            self.assertIsNotNone(media_agent)
            self.assertEqual(media_agent.api_key, TEST_API_KEY)
            
        except Exception as e:
            self.fail(f"Video Composition Agents constructor failed: {e}")
    
    def test_script_writer_agent_constructor(self):
        """Test ScriptWriterAgent constructor syntax"""
        try:
            from src.agents.script_writer_agent import ScriptWriterAgent
            agent = ScriptWriterAgent(session_id="test_session")
            self.assertIsNotNone(agent)
            self.assertEqual(agent.session_id, "test_session")
        except Exception as e:
            self.fail(f"ScriptWriterAgent constructor failed: {e}")
    
    def test_video_generator_agent_constructor(self):
        """Test VideoGeneratorAgent constructor syntax"""
        try:
            from src.agents.video_generator_agent import VideoGeneratorAgent
            agent = VideoGeneratorAgent(session_id="test_session")
            self.assertIsNotNone(agent)
            self.assertEqual(agent.session_id, "test_session")
        except Exception as e:
            self.fail(f"VideoGeneratorAgent constructor failed: {e}")
    
    def test_editor_agent_constructor(self):
        """Test EditorAgent constructor syntax"""
        try:
            from src.agents.editor_agent import EditorAgent
            agent = EditorAgent(session_id="test_session")
            self.assertIsNotNone(agent)
            self.assertEqual(agent.session_id, "test_session")
        except Exception as e:
            self.fail(f"EditorAgent constructor failed: {e}")


class TestConstructorParameters(unittest.TestCase):
    """Test that constructors accept the expected parameters"""
    
    def test_constructor_parameter_validation(self):
        """Test that constructors validate their parameters correctly"""
        
        # Test that empty API key is handled
        try:
            from src.generators.director import Director
            with self.assertRaises((ValueError, TypeError)):
                Director(api_key="")
        except ImportError:
            self.skipTest("Director not available")
        
        # Test that None API key is handled
        try:
            from src.generators.enhanced_script_processor import EnhancedScriptProcessor
            with self.assertRaises((ValueError, TypeError)):
                EnhancedScriptProcessor(api_key=None)
        except ImportError:
            self.skipTest("EnhancedScriptProcessor not available")
    
    def test_constructor_with_optional_parameters(self):
        """Test constructors with optional parameters"""
        try:
            from src.generators.video_generator import VideoGenerator
            
            # Test with minimal parameters
            generator1 = VideoGenerator(api_key=TEST_API_KEY)
            self.assertIsNotNone(generator1)
            
            # Test with all parameters
            generator2 = VideoGenerator(
                api_key=TEST_API_KEY,
                use_real_veo2=True,
                use_vertex_ai=True,
                vertex_project_id=TEST_PROJECT_ID,
                vertex_location=TEST_LOCATION,
                vertex_gcs_bucket=TEST_BUCKET,
                output_dir="/tmp/test",
                prefer_veo3=False
            )
            self.assertIsNotNone(generator2)
            
        except Exception as e:
            self.fail(f"VideoGenerator optional parameters test failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2) 