"""
Comprehensive unit tests for WorkingOrchestrator class
Tests all methods, modes, and error conditions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.working_orchestrator import WorkingOrchestrator, OrchestratorMode
from src.models.video_models import Platform, VideoCategory, Language


class TestWorkingOrchestrator(unittest.TestCase):
    """Comprehensive tests for WorkingOrchestrator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.mission = "Create a viral cat video"
        self.platform = Platform.TIKTOK
        self.category = VideoCategory.COMEDY
        self.duration = 15
        self.session_id = "test_session_123"
        
        # Mock dependencies
        self.mock_video_generator = Mock()
        self.mock_director = Mock()
        self.mock_script_processor = Mock()
        self.mock_multilang_generator = Mock()
        self.mock_continuity_agent = Mock()
        self.mock_voice_director = Mock()
        self.mock_discussion_system = Mock()
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    def test_init_simple_mode(self, mock_discussion, mock_voice, mock_continuity, 
                             mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test initialization in simple mode"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_discussion.return_value = self.mock_discussion_system
        
        # Create orchestrator in simple mode
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id,
            mode=OrchestratorMode.SIMPLE
        )
        
        # Verify initialization
        self.assertEqual(orchestrator.api_key, self.api_key)
        self.assertEqual(orchestrator.mission, self.mission)
        self.assertEqual(orchestrator.platform, self.platform)
        self.assertEqual(orchestrator.category, self.category)
        self.assertEqual(orchestrator.duration, self.duration)
        self.assertEqual(orchestrator.session_id, self.session_id)
        self.assertEqual(orchestrator.mode, OrchestratorMode.SIMPLE)
        
        # Verify core components are initialized
        mock_director.assert_called_once()
        
        # Verify discussion system is None in simple mode
        self.assertIsNone(orchestrator.discussion_system)
        
        # Verify simple mode agents are None
        self.assertIsNone(orchestrator.script_processor)
        self.assertIsNone(orchestrator.structure_agent)
        self.assertIsNone(orchestrator.timing_agent)
        self.assertIsNone(orchestrator.visual_agent)
        self.assertIsNone(orchestrator.media_agent)
        self.assertIsNone(orchestrator.multilang_generator)
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    @patch('src.agents.working_orchestrator.VideoStructureAgent')
    @patch('src.agents.working_orchestrator.ClipTimingAgent')
    @patch('src.agents.working_orchestrator.VisualElementsAgent')
    @patch('src.agents.working_orchestrator.MediaTypeAgent')
    def test_init_enhanced_mode(self, mock_media, mock_visual, mock_timing, mock_structure,
                               mock_discussion, mock_voice, mock_continuity, 
                               mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test initialization in enhanced mode"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_script.return_value = self.mock_script_processor
        mock_structure.return_value = Mock()
        mock_timing.return_value = Mock()
        mock_visual.return_value = Mock()
        mock_media.return_value = Mock()
        mock_discussion.return_value = self.mock_discussion_system
        
        # Create orchestrator in enhanced mode
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id,
            mode=OrchestratorMode.ENHANCED
        )
        
        # Verify enhanced mode agents are initialized
        self.assertIsNotNone(orchestrator.script_processor)
        self.assertIsNotNone(orchestrator.structure_agent)
        self.assertIsNotNone(orchestrator.timing_agent)
        self.assertIsNotNone(orchestrator.visual_agent)
        self.assertIsNotNone(orchestrator.media_agent)
        self.assertIsNone(orchestrator.multilang_generator)  # Not in enhanced mode
        
        # Verify all agents are called
        mock_script.assert_called_once_with(self.api_key)
        mock_structure.assert_called_once_with(self.api_key)
        mock_timing.assert_called_once_with(self.api_key)
        mock_visual.assert_called_once_with(self.api_key)
        mock_media.assert_called_once_with(self.api_key)
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    @patch('src.agents.working_orchestrator.MediaTypeAgent')
    @patch('src.agents.working_orchestrator.VisualElementsAgent')
    @patch('src.agents.working_orchestrator.ClipTimingAgent')
    @patch('src.agents.working_orchestrator.VideoStructureAgent')
    def test_init_multilingual_mode(self, mock_structure, mock_timing, mock_visual, mock_media,
                                   mock_discussion, mock_voice, mock_continuity, 
                                   mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test initialization in multilingual mode"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_script.return_value = self.mock_script_processor
        mock_multilang.return_value = self.mock_multilang_generator
        mock_structure.return_value = Mock()
        mock_timing.return_value = Mock()
        mock_visual.return_value = Mock()
        mock_media.return_value = Mock()
        mock_discussion.return_value = self.mock_discussion_system
        
        # Create orchestrator in multilingual mode
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id,
            mode=OrchestratorMode.MULTILINGUAL
        )
        
        # Verify multilingual generator was called
        mock_multilang.assert_called_with(self.api_key)
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    def test_init_with_defaults(self, mock_discussion, mock_voice, mock_continuity, 
                               mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test initialization with default parameters"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_discussion.return_value = self.mock_discussion_system
        
        # Create orchestrator with minimal parameters
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id
        )
        
        # Verify defaults
        self.assertEqual(orchestrator.mode, OrchestratorMode.ENHANCED)  # Default mode
        self.assertEqual(orchestrator.style, "viral")
        self.assertEqual(orchestrator.tone, "engaging")
        self.assertEqual(orchestrator.target_audience, "general audience")
        self.assertEqual(orchestrator.visual_style, "dynamic")
        self.assertEqual(orchestrator.language, Language.ENGLISH_US)
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    def test_generate_video_simple_mode(self, mock_discussion, mock_voice, mock_continuity, 
                                       mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test video generation in simple mode"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_discussion.return_value = self.mock_discussion_system
        
        # Setup continuity agent mock
        mock_continuity_agent = Mock()
        mock_continuity_agent.analyze_frame_continuity_need.return_value = {
            'use_frame_continuity': True,
            'confidence': 0.85,
            'primary_reason': 'Content benefits from smooth transitions',
            'agent_name': 'ContinuityDecisionAgent',
            'requires_veo2_only': True,
            'frame_overlap_handling': 'remove_first_frame',
            'transition_strategy': 'last_to_first_frame'
        }
        mock_continuity.return_value = mock_continuity_agent
        
        # Mock video generator result
        self.mock_video_generator.generate_video.return_value = "test_video.mp4"
        
        # Create orchestrator
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id,
            mode=OrchestratorMode.SIMPLE
        )
        
        # Test video generation
        config = {
            'language': Language.ENGLISH_US,
            'output_dir': 'test_output'
        }
        result = orchestrator.generate_video(config)
        
        # Verify result
        self.assertIn('success', result)
        self.assertIn('final_video_path', result)
        self.assertTrue(result['success'])
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    @patch('src.agents.working_orchestrator.VideoStructureAgent')
    @patch('src.agents.working_orchestrator.ClipTimingAgent')
    @patch('src.agents.working_orchestrator.VisualElementsAgent')
    @patch('src.agents.working_orchestrator.MediaTypeAgent')
    def test_generate_video_enhanced_mode(self, mock_media, mock_visual, mock_timing, mock_structure,
                                         mock_discussion, mock_voice, mock_continuity, 
                                         mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test video generation in enhanced mode"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_script.return_value = self.mock_script_processor
        mock_structure.return_value = Mock()
        mock_timing.return_value = Mock()
        mock_visual.return_value = Mock()
        mock_media.return_value = Mock()
        mock_discussion.return_value = self.mock_discussion_system
        mock_continuity.return_value = self.mock_continuity_agent
        
        # Mock discussion system
        self.mock_discussion_system.start_discussion.return_value = {
            'consensus': 0.9,
            'rounds': 2,
            'participants': ['agent1', 'agent2']
        }
        
        # Mock continuity decision
        self.mock_continuity_agent.analyze_frame_continuity_need.return_value = {
            'use_frame_continuity': False,
            'confidence': 0.8,
            'primary_reason': 'Short video works better with cuts'
        }
        
        # Mock script generation
        self.mock_director.write_script.return_value = {
            'hook': 'Test hook',
            'segments': [{'text': 'Test segment'}],
            'call_to_action': 'Test CTA'
        }
        
        # Mock script processing
        self.mock_script_processor.process_script_for_tts.return_value = {
            'final_script': 'Processed script',
            'segments': [{'text': 'Processed segment', 'duration': 5}]
        }
        
        # Mock video generation
        self.mock_video_generator.generate_video.return_value = "enhanced_video.mp4"
        
        # Create orchestrator
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id,
            mode=OrchestratorMode.ENHANCED
        )
        
        # Test enhanced video generation
        config = {
            'language': Language.ENGLISH_US,
            'output_dir': 'test_output'
        }
        result = orchestrator.generate_video(config)
        
        # Verify result
        self.assertIn('success', result)
        self.assertIn('final_video_path', result)
        
        # Verify discussions were conducted
        self.mock_discussion_system.start_discussion.assert_called()
        
        # Verify continuity decision was made
        self.mock_continuity_agent.analyze_frame_continuity_need.assert_called_once()
        
        # Verify script was generated and processed
        self.mock_director.write_script.assert_called_once()
        self.mock_script_processor.process_script_for_tts.assert_called_once()
        
        # Verify video was generated
        self.mock_video_generator.generate_video.assert_called_once()
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    def test_generate_video_failure(self, mock_discussion, mock_voice, mock_continuity, 
                                   mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test video generation failure handling"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_discussion.return_value = self.mock_discussion_system
        
        # Mock video generator failure
        self.mock_video_generator.generate_video.side_effect = Exception("Generation failed")
        
        # Create orchestrator
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id,
            mode=OrchestratorMode.SIMPLE
        )
        
        # Test video generation failure
        config = {
            'language': Language.ENGLISH_US,
            'output_dir': 'test_output'
        }
        result = orchestrator.generate_video(config)
        
        # Verify failure result
        self.assertIn('success', result)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    def test_orchestrator_mode_enum(self, mock_discussion, mock_voice, mock_continuity, 
                                   mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test OrchestratorMode enum values"""
        # Test enum values
        self.assertEqual(OrchestratorMode.SIMPLE.value, "simple")
        self.assertEqual(OrchestratorMode.ENHANCED.value, "enhanced")
        self.assertEqual(OrchestratorMode.MULTILINGUAL.value, "multilingual")
        self.assertEqual(OrchestratorMode.ADVANCED.value, "advanced")
        self.assertEqual(OrchestratorMode.PROFESSIONAL.value, "professional")
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    def test_session_id_generation(self, mock_discussion, mock_voice, mock_continuity, 
                                  mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test session ID generation when not provided"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_discussion.return_value = self.mock_discussion_system
        
        # Create orchestrator without session ID
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration
        )
        
        # Verify session ID was generated
        self.assertIsNotNone(orchestrator.session_id)
        self.assertIsInstance(orchestrator.session_id, str)
        self.assertGreater(len(orchestrator.session_id), 0)
    
    @patch('src.agents.working_orchestrator.VideoGenerator')
    @patch('src.agents.working_orchestrator.Director')
    @patch('src.agents.working_orchestrator.EnhancedScriptProcessor')
    @patch('src.agents.working_orchestrator.IntegratedMultilingualGenerator')
    @patch('src.agents.working_orchestrator.ContinuityDecisionAgent')
    @patch('src.agents.working_orchestrator.VoiceDirectorAgent')
    @patch('src.agents.working_orchestrator.MultiAgentDiscussionSystem')
    def test_custom_parameters(self, mock_discussion, mock_voice, mock_continuity, 
                              mock_multilang, mock_script, mock_director, mock_video_gen):
        """Test orchestrator with custom parameters"""
        # Setup mocks
        mock_video_gen.return_value = self.mock_video_generator
        mock_director.return_value = self.mock_director
        mock_discussion.return_value = self.mock_discussion_system
        
        # Create orchestrator with custom parameters
        orchestrator = WorkingOrchestrator(
            api_key=self.api_key,
            mission=self.mission,
            platform=self.platform,
            category=self.category,
            duration=self.duration,
            session_id=self.session_id,
            style="humorous",
            tone="playful",
            target_audience="teenagers",
            visual_style="cartoon",
            language=Language.ENGLISH_US
        )
        
        # Verify custom parameters
        self.assertEqual(orchestrator.style, "humorous")
        self.assertEqual(orchestrator.tone, "playful")
        self.assertEqual(orchestrator.target_audience, "teenagers")
        self.assertEqual(orchestrator.visual_style, "cartoon")
        self.assertEqual(orchestrator.language, Language.ENGLISH_US)


if __name__ == '__main__':
    unittest.main() 