"""
Comprehensive unit tests for MultiAgentDiscussionSystem class
Tests all methods, discussion flow, and error conditions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from src.agents.multi_agent_discussion import (
    MultiAgentDiscussionSystem, 
    AgentRole, 
    AgentMessage, 
    DiscussionTopic, 
    DiscussionResult
)

class TestMultiAgentDiscussionSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.session_id = "test_session_123"
        
    def test_agent_role_enum(self):
        """Test AgentRole enum values"""
        self.assertEqual(AgentRole.TREND_ANALYST.value, "trend_analyst")
        self.assertEqual(AgentRole.SCRIPT_WRITER.value, "script_writer")
        self.assertEqual(AgentRole.DIRECTOR.value, "director")
        self.assertEqual(AgentRole.VIDEO_GENERATOR.value, "video_generator")
        self.assertEqual(AgentRole.SOUNDMAN.value, "soundman")
        self.assertEqual(AgentRole.EDITOR.value, "editor")
        self.assertEqual(AgentRole.ORCHESTRATOR.value, "orchestrator")

    @patch('src.agents.multi_agent_discussion.genai')
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    @patch('src.agents.multi_agent_discussion.DiscussionVisualizer')
    def test_init_success(self, mock_visualizer, mock_makedirs, mock_genai):
        """Test successful initialization"""
        mock_genai.GenerativeModel.return_value = Mock()
        mock_visualizer.return_value = Mock()
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id,
            enable_visualization=True
        )
        
        self.assertEqual(system.api_key, self.api_key)
        self.assertEqual(system.session_id, self.session_id)
        self.assertTrue(system.enable_visualization)
        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        mock_makedirs.assert_called()

    @patch('src.agents.multi_agent_discussion.genai', None)
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    @patch('src.agents.multi_agent_discussion.DiscussionVisualizer')
    def test_init_no_genai(self, mock_visualizer, mock_makedirs):
        """Test initialization without genai available"""
        mock_visualizer.return_value = Mock()
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id,
            enable_visualization=True
        )
        
        self.assertEqual(system.api_key, self.api_key)
        self.assertEqual(system.session_id, self.session_id)
        self.assertIsNone(system.model)

    @patch('src.agents.multi_agent_discussion.genai')
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    def test_init_no_visualization(self, mock_makedirs, mock_genai):
        """Test initialization without visualization"""
        mock_genai.GenerativeModel.return_value = Mock()
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id,
            enable_visualization=False
        )
        
        self.assertEqual(system.api_key, self.api_key)
        self.assertEqual(system.session_id, self.session_id)
        self.assertFalse(system.enable_visualization)

    @patch('src.agents.multi_agent_discussion.genai')
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    @patch('src.agents.multi_agent_discussion.DiscussionVisualizer')
    def test_calculate_consensus_level(self, mock_visualizer, mock_makedirs, mock_genai):
        """Test consensus level calculation"""
        mock_genai.GenerativeModel.return_value = Mock()
        mock_visualizer.return_value = Mock()
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id
        )
        
        # Test with messages that should have high consensus
        messages = [
            AgentMessage(
                agent_role=AgentRole.TREND_ANALYST,
                agent_name="TrendAgent",
                message="This is a great idea",
                timestamp=datetime.now(),
                message_id="msg1",
                vote="agree"
            ),
            AgentMessage(
                agent_role=AgentRole.SCRIPT_WRITER,
                agent_name="ScriptAgent", 
                message="I agree completely",
                timestamp=datetime.now(),
                message_id="msg2",
                vote="agree"
            )
        ]
        
        consensus = system._calculate_consensus(messages)
        
        # Should be high consensus since both agree
        self.assertGreater(consensus, 0.5)
        self.assertLessEqual(consensus, 1.0)

    @patch('src.agents.multi_agent_discussion.genai')
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    @patch('src.agents.multi_agent_discussion.DiscussionVisualizer')
    def test_parse_agent_response_success(self, mock_visualizer, mock_makedirs, mock_genai):
        """Test successful agent response parsing"""
        mock_genai.GenerativeModel.return_value = Mock()
        mock_visualizer.return_value = Mock()
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id
        )
        
        # Test valid JSON response
        response_text = '''
        {
            "message": "This is a great concept",
            "reasoning": "The idea has strong viral potential",
            "suggestions": ["Add more humor", "Include trending topics"],
            "concerns": ["Duration might be too long"],
            "vote": "agree"
        }
        '''
        
        result = system._parse_agent_response(response_text, AgentRole.TREND_ANALYST)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["message"], "This is a great concept")
        self.assertEqual(result["reasoning"], "The idea has strong viral potential")
        self.assertEqual(result["vote"], "agree")
        self.assertEqual(len(result["suggestions"]), 2)
        self.assertEqual(len(result["concerns"]), 1)

    @patch('src.agents.multi_agent_discussion.genai')
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    @patch('src.agents.multi_agent_discussion.DiscussionVisualizer')
    def test_parse_agent_response_invalid_json(self, mock_visualizer, mock_makedirs, mock_genai):
        """Test agent response parsing with invalid JSON"""
        mock_genai.GenerativeModel.return_value = Mock()
        mock_visualizer.return_value = Mock()
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id
        )
        
        # Test invalid JSON response
        response_text = "This is not valid JSON"
        
        result = system._parse_agent_response(response_text, AgentRole.TREND_ANALYST)
        
        self.assertIsInstance(result, dict)
        self.assertIn("message", result)
        self.assertIn("reasoning", result)
        self.assertEqual(result["vote"], "neutral")

    @patch('src.agents.multi_agent_discussion.genai')
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    @patch('src.agents.multi_agent_discussion.DiscussionVisualizer')
    @patch('builtins.open', new_callable=Mock)
    def test_start_discussion_success(self, mock_open, mock_visualizer, mock_makedirs, mock_genai):
        """Test successful discussion start"""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_visualizer.return_value = Mock()
        
        # Mock file operations with proper context manager
        mock_file = Mock()
        mock_open.return_value = mock_file
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        
        # Mock AI response
        mock_response = Mock()
        mock_response.text = '''
        {
            "message": "This concept has great potential",
            "reasoning": "Strong viral elements present",
            "suggestions": ["Add humor"],
            "concerns": [],
            "vote": "agree"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id
        )
        
        topic = DiscussionTopic(
            topic_id="test_topic",
            title="Test Video Concept",
            description="A test video concept",
            context={"platform": "tiktok"},
            required_decisions=["approve", "reject"],
            max_rounds=2,
            min_consensus=0.6
        )
        
        participating_agents = [AgentRole.TREND_ANALYST, AgentRole.SCRIPT_WRITER]
        result = system.start_discussion(topic, participating_agents)
        
        self.assertIsInstance(result, DiscussionResult)
        self.assertEqual(result.topic_id, "test_topic")
        self.assertIsNotNone(result.decision)
        self.assertGreater(result.consensus_level, 0.0)

    @patch('src.agents.multi_agent_discussion.genai')
    @patch('src.agents.multi_agent_discussion.os.makedirs')
    @patch('src.agents.multi_agent_discussion.DiscussionVisualizer')
    @patch('builtins.open', new_callable=Mock)
    def test_start_discussion_no_consensus(self, mock_open, mock_visualizer, mock_makedirs, mock_genai):
        """Test discussion that doesn't reach consensus"""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_visualizer.return_value = Mock()
        
        # Mock file operations with proper context manager
        mock_file = Mock()
        mock_open.return_value = mock_file
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        
        # Mock AI response with mixed votes
        mock_response = Mock()
        mock_response.text = '''
        {
            "message": "I have concerns about this concept",
            "reasoning": "Needs more work",
            "suggestions": ["Revise approach"],
            "concerns": ["Too risky"],
            "vote": "disagree"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        
        system = MultiAgentDiscussionSystem(
            api_key=self.api_key,
            session_id=self.session_id
        )
        
        topic = DiscussionTopic(
            topic_id="test_topic",
            title="Test Video Concept",
            description="A test video concept",
            context={"platform": "tiktok"},
            required_decisions=["approve", "reject"],
            max_rounds=2,
            min_consensus=0.9  # Very high consensus requirement
        )
        
        participating_agents = [AgentRole.TREND_ANALYST, AgentRole.SCRIPT_WRITER]
        result = system.start_discussion(topic, participating_agents)
        
        self.assertIsInstance(result, DiscussionResult)
        self.assertEqual(result.topic_id, "test_topic")
        self.assertLess(result.consensus_level, 0.9)

if __name__ == '__main__':
    unittest.main() 