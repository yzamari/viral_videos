from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService
from src.services.trending import UnifiedTrendingAnalyzer
from config.config import settings
import os

class TrendAnalystAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)
        
        # Initialize unified trending analyzer for REAL data
        self.trending_analyzer = UnifiedTrendingAnalyzer()
        self.monitoring_service.log("TrendAnalystAgent: Initialized with REAL API trending data")

    def analyze(self, topic, platform=None):
        self.monitoring_service.log(f"TrendAnalystAgent: Analyzing REAL trends for topic - {topic}")
        
        try:
            # Get comprehensive trending data from all platforms
            trending_data = self.trending_analyzer.get_all_trending_data(
                platform=platform,
                keyword=topic,
                limit=20
            )
            
            # Extract platform-specific insights
            insights = {
                "topic": topic,
                "analysis_timestamp": trending_data.get('analysis_timestamp'),
                "platforms": {},
                "unified_insights": trending_data.get('unified_insights', {}),
                "recommendations": trending_data.get('recommendations', {}),
                "source": "Real Platform APIs"
            }
            
            # Process each platform's data
            for platform_name, platform_data in trending_data.get('platforms', {}).items():
                if 'error' not in platform_data:
                    platform_insights = {
                        'trending_content': [],
                        'trending_hashtags': [],
                        'key_metrics': {}
                    }
                    
                    if platform_name == 'youtube':
                        videos = platform_data.get('trending_videos', [])
                        platform_insights['trending_content'] = [
                            {
                                'title': v.get('title'),
                                'views': v.get('view_count'),
                                'engagement': v.get('engagement_score'),
                                'url': v.get('url')
                            } for v in videos[:5]
                        ]
                        
                        analysis = platform_data.get('analysis', {})
                        platform_insights['key_metrics'] = {
                            'avg_views': analysis.get('average_metrics', {}).get('views', 0),
                            'optimal_duration': analysis.get('optimal_duration_range', {}).get('sweet_spot', 60),
                            'trending_words': [w['word'] for w in analysis.get('trending_title_words', [])[:5]]
                        }
                    
                    elif platform_name in ['tiktok', 'instagram']:
                        hashtags = platform_data.get('trending_hashtags', [])
                        platform_insights['trending_hashtags'] = [
                            {
                                'tag': h.get('tag'),
                                'score': h.get('trend_score'),
                                'category': h.get('category')
                            } for h in hashtags[:10]
                        ]
                    
                    insights['platforms'][platform_name] = platform_insights
            
            # Add content optimization recommendations
            content_analysis = self.trending_analyzer.analyze_content_for_trends(
                mission=topic,
                script_content="",
                platform=platform or 'youtube'
            )
            
            insights['content_optimization'] = {
                'viral_potential': content_analysis.get('viral_potential'),
                'optimization_suggestions': content_analysis.get('optimization_suggestions', []),
                'trending_elements_to_add': content_analysis.get('trending_elements_to_add', [])
            }
            
            self.monitoring_service.log(f"TrendAnalystAgent: Analyzed trends from {len(insights['platforms'])} platforms")
            
            trends = insights
            
        except Exception as e:
            self.monitoring_service.log(f"TrendAnalystAgent: Error fetching real trends: {e}")
            # Fallback to basic data
            trends = self._get_basic_fallback_data(topic)
        
        # Save the analysis
        self.file_service.save_json("trend_analysis.json", trends)
        self.monitoring_service.log("TrendAnalystAgent: Trend analysis complete with REAL data.")
        return trends

    def _get_basic_fallback_data(self, topic):
        """Basic fallback data when APIs are unavailable"""
        return {
            "topic": topic,
            "platforms": {
                "general": {
                    "trending_hashtags": [
                        {"tag": "#viral", "score": 0.9},
                        {"tag": "#trending", "score": 0.85},
                        {"tag": f"#{topic.replace(' ', '').lower()}", "score": 0.8}
                    ],
                    "key_metrics": {
                        "optimal_duration": 30,
                        "best_format": "short-form"
                    }
                }
            },
            "source": "Fallback Data",
            "note": "Real API data temporarily unavailable"
        }
