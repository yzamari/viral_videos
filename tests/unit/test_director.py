"""
Unit tests for Director AI
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from src.generators.director import Director
from src.models.video_models import Platform, VideoCategory
from src.utils.exceptions import GenerationFailedError, ContentPolicyViolation


class TestDirector:
    """Test suite for Director AI"""
    
    @pytest.fixture
    def director(self):
        """Create Director instance"""
        with patch('src.generators.director.genai'):
            return Director(api_key="test_api_key")
            
    @pytest.fixture
    def mock_patterns(self):
        """Mock successful patterns"""
        return {
            'themes': ['entertainment', 'comedy', 'viral'],
            'hooks': ['You won\'t believe...', 'This is amazing...'],
            'success_factors': ['fast pacing', 'emotional appeal'],
            'emotional_tones': ['exciting', 'funny', 'surprising']
        }
        
    @pytest.fixture
    def mock_news_items(self):
        """Mock news items"""
        return [
            {
                'title': 'Breaking: AI Creates Amazing Videos',
                'description': 'New AI technology revolutionizes content',
                'published_at': datetime.now(),
                'relevance_score': 0.9
            }
        ]
        
    def test_init(self, director):
        """Test Director initialization"""
        assert director.model is not None
        assert director.news_scraper is not None
        assert director.hook_templates is not None
        assert director.content_structures is not None
        
    @patch('src.generators.director.genai.GenerativeModel')
    def test_write_script_success(self, mock_genai, director, mock_patterns):
        """Test successful script writing"""
        # Setup mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'hook': {
                'text': 'Amazing hook!',
                'type': 'shock',
                'visual_cue': 'Dramatic reveal',
                'duration_seconds': 3
            },
            'segments': [
                {
                    'text': 'First segment',
                    'visual': 'Cool visual',
                    'duration': 10,
                    'transition': 'cut'
                }
            ],
            'cta': {
                'text': 'Subscribe now!',
                'visual': 'Button animation',
                'action': 'subscribe'
            },
            'duration': 30
        })
        
        director.model.generate_content.return_value = mock_response
        
        # Mock news scraper
        with patch.object(director.news_scraper, 'search_news', return_value=[]):
            # Execute
            script = director.write_script(
                topic="Test Topic",
                style="comedy",
                duration=30,
                platform=Platform.YOUTUBE,
                category=VideoCategory.COMEDY,
                patterns=mock_patterns,
                incorporate_news=False
            )
            
        # Assert
        assert 'hook' in script
        assert script['hook']['text'] == 'Amazing hook!'
        assert 'segments' in script
        assert len(script['segments']) > 0
        
    def test_write_script_with_news(self, director, mock_patterns, mock_news_items):
        """Test script writing with news incorporation"""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'hook': {'text': 'News hook!', 'type': 'story'},
            'segments': [{'text': 'News segment', 'visual': 'News visual', 'duration': 10}],
            'duration': 30
        })
        
        director.model.generate_content.return_value = mock_response
        
        # Mock news fetching
        with patch.object(director, '_fetch_relevant_news', return_value=mock_news_items):
            script = director.write_script(
                topic="AI Technology",
                style="informative",
                duration=30,
                platform=Platform.YOUTUBE,
                category=VideoCategory.TECHNOLOGY,
                patterns=mock_patterns,
                incorporate_news=True
            )
            
        # Assert news was incorporated
        assert 'has_news' in script
        assert script['has_news'] == True
        
    def test_generate_hook_fallback(self, director):
        """Test hook generation fallback when AI fails"""
        # Make AI fail
        director.model.generate_content.side_effect = Exception("AI Error")
        
        # Execute
        hook = director._generate_hook("Test Topic", "comedy", [])
        
        # Assert fallback was used
        assert 'text' in hook
        assert 'Test Topic' in hook['text']
        assert hook['type'] in ['question', 'shock', 'promise', 'story']
        
    def test_adapt_to_platform(self, director):
        """Test platform adaptation"""
        script = {
            'duration': 120,  # 2 minutes
            'segments': [{'text': 'Test'}],
            'hook': {'text': 'Hook'}
        }
        
        # Adapt to TikTok (max 60 seconds)
        adapted = director.adapt_to_platform(script, Platform.TIKTOK)
        
        # Assert
        assert adapted['duration'] <= 60
        assert 'platform_features' in adapted
        assert 'sounds' in adapted['platform_features']
        
    def test_optimize_for_virality(self, director, mock_patterns):
        """Test virality optimization"""
        script = {
            'hook': {'text': 'Basic hook'},
            'segments': [
                {'text': 'Segment 1', 'duration': 10},
                {'text': 'Segment 2', 'duration': 10}
            ]
        }
        
        # Execute
        optimized = director.optimize_for_virality(script, mock_patterns)
        
        # Assert
        assert 'viral_elements' in optimized
        assert 'shareability_score' in optimized['viral_elements']
        assert 'emotional_arc' in optimized['viral_elements']
        
    def test_content_policy_validation(self, director):
        """Test content policy validation"""
        # Script with prohibited content
        script = {
            'hook': {'text': 'This contains hate speech'},
            'segments': [{'text': 'More inappropriate content'}]
        }
        
        # Should raise ContentPolicyViolation
        with pytest.raises(ContentPolicyViolation):
            director._validate_content_policy(script, Platform.YOUTUBE)
            
    def test_calculate_news_relevance(self, director):
        """Test news relevance calculation"""
        news_item = {
            'title': 'AI Technology Breakthrough',
            'description': 'New AI model creates amazing videos',
            'published_at': datetime.now()
        }
        
        # High relevance
        score = director._calculate_news_relevance(news_item, "AI video technology")
        assert score > 0.5
        
        # Low relevance
        score = director._calculate_news_relevance(news_item, "cooking recipes")
        assert score < 0.5
        
    def test_extract_json_from_response(self, director):
        """Test JSON extraction from AI response"""
        # Valid JSON
        text = "Here's the response: {'key': 'value'}"
        result = director._extract_json(text)
        assert result == {'key': 'value'}
        
        # Invalid JSON
        text = "No JSON here"
        result = director._extract_json(text)
        assert result is None
        
    def test_calculate_segments(self, director):
        """Test segment calculation"""
        assert director._calculate_segments(30) == 4  # 30/7 ≈ 4
        assert director._calculate_segments(60) == 8  # Max 8
        assert director._calculate_segments(15) == 3  # Min 3
        
    def test_error_handling(self, director, mock_patterns):
        """Test error handling in script writing"""
        # Make AI fail
        director.model.generate_content.side_effect = Exception("API Error")
        
        # Should raise GenerationFailedError
        with pytest.raises(GenerationFailedError):
            director.write_script(
                topic="Test",
                style="comedy",
                duration=30,
                platform=Platform.YOUTUBE,
                category=VideoCategory.COMEDY,
                patterns=mock_patterns
            ) 