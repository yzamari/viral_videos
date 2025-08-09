"""
Comprehensive tests for the Trending Intelligence System
Tests real API integration and fallback mechanisms
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from src.services.trending import UnifiedTrendingAnalyzer
from src.agents.trend_analyst_agent import TrendAnalystAgent
from src.utils.trending_analyzer import TrendingAnalyzer


class TestUnifiedTrendingAnalyzer:
    """Test the unified trending analyzer with real and mock data"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return UnifiedTrendingAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test proper initialization of all platform clients"""
        assert analyzer is not None
        assert hasattr(analyzer, 'youtube')
        assert hasattr(analyzer, 'tiktok_api')
        assert hasattr(analyzer, 'instagram_client')
        assert hasattr(analyzer, 'twitter_client')
        assert hasattr(analyzer, 'reddit')
        assert hasattr(analyzer, 'linkedin_api')
    
    @pytest.mark.skipif(not os.getenv('YOUTUBE_API_KEY'), reason="YouTube API key not set")
    def test_youtube_trending_real(self, analyzer):
        """Test real YouTube API integration"""
        data = analyzer._get_youtube_trending(keyword=None, limit=5)
        
        assert 'trending_videos' in data
        assert 'analysis' in data
        assert len(data['trending_videos']) > 0
        
        # Check video structure
        video = data['trending_videos'][0]
        assert 'title' in video
        assert 'view_count' in video
        assert 'engagement_score' in video
        assert 'url' in video
    
    @patch('src.services.trending.UnifiedTrendingAnalyzer._get_youtube_trending')
    def test_youtube_trending_mock(self, mock_youtube, analyzer):
        """Test YouTube trending with mock data"""
        mock_youtube.return_value = {
            'trending_videos': [
                {
                    'title': 'Test Video',
                    'view_count': 1000000,
                    'engagement_score': 85.5,
                    'url': 'https://youtube.com/watch?v=test'
                }
            ],
            'analysis': {
                'average_metrics': {'views': 1000000},
                'optimal_duration_range': {'sweet_spot': 45}
            }
        }
        
        data = analyzer.get_all_trending_data(platform='youtube', limit=5)
        assert 'platforms' in data
        assert 'youtube' in data['platforms']
    
    def test_cache_functionality(self, analyzer):
        """Test that caching works properly"""
        # First call
        data1 = analyzer.get_all_trending_data(platform='youtube', keyword='test', limit=5)
        
        # Second call (should use cache)
        data2 = analyzer.get_all_trending_data(platform='youtube', keyword='test', limit=5)
        
        # Check timestamps are identical (indicating cache hit)
        assert data1['analysis_timestamp'] == data2['analysis_timestamp']
    
    def test_multi_platform_aggregation(self, analyzer):
        """Test aggregation across multiple platforms"""
        with patch.object(analyzer, '_get_youtube_trending') as mock_yt, \
             patch.object(analyzer, '_get_tiktok_trending') as mock_tt:
            
            mock_yt.return_value = {'trending_videos': []}
            mock_tt.return_value = {'trending_hashtags': []}
            
            data = analyzer.get_all_trending_data(platform=None, limit=5)
            
            assert 'platforms' in data
            assert 'unified_insights' in data
            assert 'recommendations' in data
    
    def test_error_handling(self, analyzer):
        """Test graceful error handling"""
        with patch.object(analyzer, '_get_youtube_trending', side_effect=Exception("API Error")):
            data = analyzer.get_all_trending_data(platform='youtube', limit=5)
            
            assert 'platforms' in data
            assert 'youtube' in data['platforms']
            assert 'error' in data['platforms']['youtube']
    
    def test_keyword_search(self, analyzer):
        """Test keyword-based trending search"""
        with patch.object(analyzer, '_get_youtube_trending') as mock_yt:
            mock_yt.return_value = {
                'trending_videos': [
                    {
                        'title': 'AI Tutorial',
                        'keyword_relevance': True
                    }
                ]
            }
            
            data = analyzer.get_all_trending_data(platform='youtube', keyword='AI', limit=5)
            mock_yt.assert_called_with('AI', 5)
    
    def test_unified_insights_generation(self, analyzer):
        """Test unified insights across platforms"""
        platform_data = {
            'youtube': {
                'analysis': {
                    'trending_title_words': [
                        {'word': 'viral', 'count': 10},
                        {'word': 'amazing', 'count': 8}
                    ]
                }
            },
            'tiktok': {
                'trending_hashtags': [
                    {'tag': '#viral', 'trend_score': 0.9}
                ]
            }
        }
        
        insights = analyzer._generate_unified_insights(platform_data)
        
        assert 'top_trending_topics' in insights
        assert 'cross_platform_trends' in insights
        assert 'viral_content_patterns' in insights
        assert 'content_recommendations' in insights
    
    def test_recommendations_generation(self, analyzer):
        """Test recommendation generation"""
        platform_data = {
            'youtube': {
                'analysis': {
                    'optimal_duration_range': {'sweet_spot': 45}
                }
            }
        }
        
        recommendations = analyzer._generate_recommendations(platform_data, 'AI')
        
        assert 'content_strategy' in recommendations
        assert 'hashtag_strategy' in recommendations
        assert 'timing_strategy' in recommendations
        assert 'format_recommendations' in recommendations
        assert 'engagement_tactics' in recommendations
    
    def test_content_analysis_for_trends(self, analyzer):
        """Test content analysis against trends"""
        with patch.object(analyzer, 'get_all_trending_data') as mock_trends:
            mock_trends.return_value = {
                'platforms': {
                    'youtube': {
                        'trending_hashtags': [
                            {'tag': '#ai'},
                            {'tag': '#tech'}
                        ],
                        'analysis': {
                            'optimal_duration_range': {'sweet_spot': 60},
                            'trending_title_words': [
                                {'word': 'amazing', 'count': 10}
                            ]
                        }
                    }
                }
            }
            
            analysis = analyzer.analyze_content_for_trends(
                mission="Amazing AI Technology",
                script_content="Did you know that AI is changing the world?",
                platform="youtube"
            )
            
            assert 'viral_potential' in analysis
            assert 'optimization_suggestions' in analysis
            assert 'trending_elements_to_add' in analysis
            assert analysis['viral_potential'] > 0.5  # Should be high due to hook and keyword


class TestTrendAnalystAgent:
    """Test the trend analyst agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        with patch('src.agents.trend_analyst_agent.MonitoringService'), \
             patch('src.agents.trend_analyst_agent.FileService'):
            return TrendAnalystAgent(session_id='test_session')
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert hasattr(agent, 'trending_analyzer')
        assert agent.session_id == 'test_session'
    
    def test_analyze_with_real_data(self, agent):
        """Test analysis with real trending data"""
        with patch.object(agent.trending_analyzer, 'get_all_trending_data') as mock_get, \
             patch.object(agent.trending_analyzer, 'analyze_content_for_trends') as mock_analyze:
            
            mock_get.return_value = {
                'analysis_timestamp': datetime.now().isoformat(),
                'platforms': {
                    'youtube': {
                        'trending_videos': [
                            {'title': 'Test', 'view_count': 1000}
                        ]
                    }
                },
                'unified_insights': {},
                'recommendations': {}
            }
            
            mock_analyze.return_value = {
                'viral_potential': 0.8,
                'optimization_suggestions': []
            }
            
            result = agent.analyze('test topic', platform='youtube')
            
            assert 'topic' in result
            assert result['topic'] == 'test topic'
            assert 'platforms' in result
            assert 'content_optimization' in result
            assert result['source'] == 'Real Platform APIs'
    
    def test_fallback_on_error(self, agent):
        """Test fallback to basic data on error"""
        with patch.object(agent.trending_analyzer, 'get_all_trending_data', side_effect=Exception("API Error")):
            result = agent.analyze('test topic')
            
            assert 'topic' in result
            assert result['source'] == 'Fallback Data'
            assert 'platforms' in result
            assert 'general' in result['platforms']


class TestTrendingAnalyzer:
    """Test the trending analyzer wrapper"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return TrendingAnalyzer()
    
    def test_get_trending_videos(self, analyzer):
        """Test getting trending videos"""
        with patch.object(analyzer.unified_analyzer, 'get_all_trending_data') as mock_get:
            mock_get.return_value = {
                'platforms': {
                    'youtube': {
                        'trending_videos': [
                            {
                                'title': 'Test Video',
                                'view_count': 1000000,
                                'engagement_score': 85000,
                                'tags': ['test', 'video'],
                                'duration_seconds': 120,
                                'url': 'https://youtube.com/watch?v=test',
                                'channel_title': 'Test Channel',
                                'published_at': '2024-01-01T00:00:00Z'
                            }
                        ]
                    }
                }
            }
            
            videos = analyzer.get_trending_videos('youtube', hours=24, count=10)
            
            assert len(videos) > 0
            assert videos[0]['platform'] == 'youtube'
            assert 'title' in videos[0]
            assert 'views' in videos[0]
    
    def test_analyze_trends(self, analyzer):
        """Test trend analysis"""
        videos = [
            {
                'title': 'How to build AI?',
                'duration': 60,
                'keywords': ['ai', 'tutorial'],
                'platform': 'youtube'
            }
        ]
        
        with patch.object(analyzer.unified_analyzer, 'analyze_content_for_trends') as mock_analyze:
            mock_analyze.return_value = {
                'optimization_suggestions': ['Use trending hashtags'],
                'trending_elements_to_add': ['#AI', '#Tech']
            }
            
            analysis = analyzer.analyze_trends(videos)
            
            assert 'common_keywords' in analysis
            assert 'avg_duration' in analysis
            assert 'best_hook_type' in analysis
            assert analysis['best_hook_type'] == 'question'  # Due to '?' in title
    
    def test_viral_hooks_extraction(self, analyzer):
        """Test extraction of viral hooks from titles"""
        videos = [
            {'title': 'How to become successful in 2024'},
            {'title': 'Why you should learn AI now'},
            {'title': 'The truth about social media'},
            {'title': 'Nobody talks about this secret'}
        ]
        
        hooks = analyzer._extract_viral_hooks_from_titles(videos)
        
        assert len(hooks) > 0
        assert any('how to' in hook.lower() for hook in hooks)


@pytest.mark.integration
class TestEndToEndTrending:
    """End-to-end integration tests"""
    
    def test_full_trending_pipeline(self):
        """Test the complete trending pipeline"""
        # Create agent
        with patch('src.agents.trend_analyst_agent.MonitoringService'), \
             patch('src.agents.trend_analyst_agent.FileService') as mock_file:
            
            agent = TrendAnalystAgent('test_session')
            
            # Mock the unified analyzer to return consistent data
            with patch.object(agent.trending_analyzer, 'get_all_trending_data') as mock_get:
                mock_get.return_value = {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'platforms': {
                        'youtube': {
                            'trending_videos': [
                                {
                                    'title': 'AI Revolution 2024',
                                    'view_count': 5000000,
                                    'engagement_score': 95.0
                                }
                            ],
                            'analysis': {
                                'optimal_duration_range': {'sweet_spot': 45}
                            }
                        },
                        'tiktok': {
                            'trending_hashtags': [
                                {'tag': '#AIRevolution', 'trend_score': 0.95}
                            ]
                        }
                    },
                    'unified_insights': {
                        'cross_platform_trends': [
                            {'trend': '#ai', 'platforms': ['youtube', 'tiktok']}
                        ]
                    },
                    'recommendations': {
                        'content_strategy': ['Focus on AI content']
                    }
                }
                
                # Run analysis
                result = agent.analyze('AI Revolution')
                
                # Verify results
                assert result['source'] == 'Real Platform APIs'
                assert 'youtube' in result['platforms']
                assert 'tiktok' in result['platforms']
                
                # Verify file was saved
                mock_file.return_value.save_json.assert_called_once()
                saved_data = mock_file.return_value.save_json.call_args[0][1]
                assert saved_data['topic'] == 'AI Revolution'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])