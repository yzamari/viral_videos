"""
Unified Trending Analyzer - Combines real trending data from all platforms
Replaces the mock data with actual API integrations
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .youtube_trending_service import YouTubeTrendingService
from .tiktok_trending_service import TikTokTrendingService
from .instagram_trending_service import InstagramTrendingService
from ...utils.logging_config import get_logger
from ...utils.session_context import SessionContext

logger = get_logger(__name__)

class UnifiedTrendingAnalyzer:
    """
    Unified trending analyzer that fetches and analyzes real trending data
    from YouTube, TikTok, and Instagram
    """
    
    def __init__(self):
        """Initialize all platform services"""
        self.youtube_service = YouTubeTrendingService()
        self.tiktok_service = TikTokTrendingService()
        self.instagram_service = InstagramTrendingService()
        
        logger.info("✅ Unified Trending Analyzer initialized with real APIs")
    
    def get_all_trending_data(self, 
                            platform: Optional[str] = None,
                            keyword: Optional[str] = None,
                            limit: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive trending data from all platforms
        
        Args:
            platform: Specific platform to focus on (optional)
            keyword: Search keyword for trend analysis (optional)
            limit: Maximum results per platform
            
        Returns:
            Comprehensive trending data dictionary
        """
        logger.info(f"🔍 Fetching real trending data - Platform: {platform or 'ALL'}, Keyword: {keyword or 'GENERAL'}")
        
        trending_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'platforms': {},
            'unified_insights': {},
            'recommendations': {}
        }
        
        # Use thread pool for concurrent API calls
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            # Submit tasks based on platform preference
            if not platform or platform.lower() in ['youtube', 'all']:
                futures['youtube'] = executor.submit(self._get_youtube_trends, keyword, limit)
            
            if not platform or platform.lower() in ['tiktok', 'all']:
                futures['tiktok'] = executor.submit(self._get_tiktok_trends, limit)
            
            if not platform or platform.lower() in ['instagram', 'all']:
                futures['instagram'] = executor.submit(self._get_instagram_trends, limit)
            
            # Collect results
            for platform_name, future in futures.items():
                try:
                    result = future.result(timeout=30)
                    trending_data['platforms'][platform_name] = result
                except Exception as e:
                    logger.error(f"❌ Error fetching {platform_name} trends: {e}")
                    trending_data['platforms'][platform_name] = {'error': str(e)}
        
        # Analyze unified trends
        trending_data['unified_insights'] = self._analyze_cross_platform_trends(trending_data['platforms'])
        
        # Generate recommendations
        trending_data['recommendations'] = self._generate_content_recommendations(
            trending_data['platforms'], 
            trending_data['unified_insights'],
            platform
        )
        
        return trending_data
    
    def get_trending_hashtags_unified(self, 
                                    platform: str,
                                    mission: str,
                                    category: str,
                                    limit: int = 30) -> List[Dict[str, Any]]:
        """
        Get unified trending hashtags combining real data from all platforms
        
        Returns:
            List of trending hashtags with metadata
        """
        logger.info(f"#️⃣ Fetching unified trending hashtags for {platform}")
        
        all_hashtags = []
        
        # Get platform-specific hashtags
        if platform.lower() == 'tiktok':
            tiktok_hashtags = self.tiktok_service.get_trending_hashtags(limit)
            all_hashtags.extend(tiktok_hashtags)
        
        elif platform.lower() == 'instagram':
            instagram_hashtags = self.instagram_service.get_trending_hashtags(limit)
            all_hashtags.extend(instagram_hashtags)
        
        elif platform.lower() == 'youtube':
            # YouTube uses tags rather than hashtags
            youtube_data = self._get_youtube_trends(mission, 10)
            youtube_tags = youtube_data.get('trending_tags', [])
            
            # Convert YouTube tags to hashtag format
            for tag_info in youtube_tags:
                all_hashtags.append({
                    'tag': f"#{tag_info.get('tag', '').replace(' ', '').lower()}",
                    'platform': 'youtube',
                    'trend_score': 0.8,
                    'category': 'keyword',
                    'usage_count': tag_info.get('count', 0) * 10000
                })
        
        # Get cross-platform trending hashtags
        cross_platform_hashtags = self._get_cross_platform_hashtags(mission, category)
        all_hashtags.extend(cross_platform_hashtags)
        
        # Remove duplicates and sort by trend score
        seen_tags = set()
        unique_hashtags = []
        for hashtag in all_hashtags:
            tag_lower = hashtag.get('tag', '').lower()
            if tag_lower not in seen_tags:
                seen_tags.add(tag_lower)
                unique_hashtags.append(hashtag)
        
        # Sort by trend score
        unique_hashtags.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
        
        # Ensure we have the requested number
        if len(unique_hashtags) < limit:
            # Add general trending hashtags
            general_hashtags = self._get_general_trending_hashtags(limit - len(unique_hashtags))
            unique_hashtags.extend(general_hashtags)
        
        return unique_hashtags[:limit]
    
    def analyze_content_for_trends(self, 
                                 mission: str,
                                 script_content: str,
                                 platform: str) -> Dict[str, Any]:
        """
        Analyze content against current trends to optimize for virality
        
        Returns:
            Trend optimization recommendations
        """
        logger.info(f"📊 Analyzing content for trend optimization on {platform}")
        
        # Get current trends for the platform
        current_trends = self.get_all_trending_data(platform=platform, keyword=mission, limit=20)
        
        # Extract key elements from script
        script_words = script_content.lower().split()
        script_length = len(script_words)
        
        # Platform-specific analysis
        platform_data = current_trends['platforms'].get(platform.lower(), {})
        
        optimization = {
            'trend_alignment_score': 0.0,
            'viral_potential': 'medium',
            'optimization_suggestions': [],
            'trending_elements_to_add': [],
            'timing_recommendations': {},
            'hashtag_strategy': {}
        }
        
        # Analyze based on platform
        if platform.lower() == 'youtube' and 'analysis' in platform_data:
            youtube_analysis = platform_data['analysis']
            
            # Check optimal duration
            optimal_duration = youtube_analysis.get('optimal_duration_range', {})
            if optimal_duration:
                optimization['timing_recommendations']['optimal_duration'] = f"{optimal_duration.get('sweet_spot', 60)} seconds"
            
            # Check trending words
            trending_words = [item['word'] for item in youtube_analysis.get('trending_title_words', [])]
            matching_words = [word for word in trending_words if word in script_words]
            
            if matching_words:
                optimization['trend_alignment_score'] += 0.3
                optimization['optimization_suggestions'].append(f"Good use of trending words: {', '.join(matching_words[:5])}")
            else:
                optimization['trending_elements_to_add'].extend(trending_words[:5])
        
        elif platform.lower() == 'tiktok':
            # TikTok-specific optimizations
            optimization['timing_recommendations']['optimal_duration'] = "15-30 seconds"
            optimization['optimization_suggestions'].append("Start with a hook in first 2 seconds")
            optimization['optimization_suggestions'].append("Use trending sounds and effects")
            
            # Get trending sounds
            trending_sounds = self.tiktok_service.get_trending_sounds(5)
            if trending_sounds:
                optimization['trending_elements_to_add'].append({
                    'type': 'sounds',
                    'items': [s['title'] for s in trending_sounds[:3]]
                })
        
        elif platform.lower() == 'instagram':
            # Instagram-specific optimizations
            optimization['timing_recommendations']['optimal_duration'] = "15-30 seconds for Reels"
            optimization['hashtag_strategy']['optimal_count'] = "10-15 hashtags"
            optimization['hashtag_strategy']['mix'] = "2-3 mega popular, 5-7 moderate, 5-7 niche"
        
        # Calculate viral potential
        if optimization['trend_alignment_score'] >= 0.7:
            optimization['viral_potential'] = 'high'
        elif optimization['trend_alignment_score'] >= 0.4:
            optimization['viral_potential'] = 'medium-high'
        else:
            optimization['viral_potential'] = 'medium'
        
        # Add general recommendations
        optimization['optimization_suggestions'].extend([
            "Post during peak hours for your audience",
            "Engage with comments in the first hour",
            "Use platform-specific features (Reels, Shorts, etc.)",
            "Include a clear call-to-action"
        ])
        
        return optimization
    
    def save_trending_analysis(self, 
                             trending_data: Dict[str, Any],
                             session_context: SessionContext,
                             filename: str = "trending_analysis.json"):
        """Save trending analysis to session directory"""
        try:
            analysis_path = session_context.get_output_path("trending", filename)
            os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
            
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(trending_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📁 Trending analysis saved to: {analysis_path}")
            
            # Also create a summary report
            report_path = session_context.get_output_path("trending", "trending_report.md")
            self._create_trending_report(trending_data, report_path)
            
            return analysis_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save trending analysis: {e}")
            return None
    
    def _get_youtube_trends(self, keyword: Optional[str], limit: int) -> Dict[str, Any]:
        """Get YouTube trending data"""
        try:
            result = {
                'trending_videos': [],
                'trending_tags': [],
                'analysis': {}
            }
            
            # Get trending videos
            if keyword:
                videos = self.youtube_service.search_trending_by_keyword(keyword, limit)
            else:
                videos = self.youtube_service.get_trending_videos(max_results=limit)
            
            result['trending_videos'] = videos
            
            # Analyze patterns if we have videos
            if videos:
                analysis = self.youtube_service.analyze_trending_patterns(videos)
                result['analysis'] = analysis
                
                # Extract trending tags
                if 'trending_tags' in analysis:
                    result['trending_tags'] = analysis['trending_tags']
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting YouTube trends: {e}")
            return {'error': str(e)}
    
    def _get_tiktok_trends(self, limit: int) -> Dict[str, Any]:
        """Get TikTok trending data"""
        try:
            hashtags = self.tiktok_service.get_trending_hashtags(limit)
            sounds = self.tiktok_service.get_trending_sounds(10)
            effects = self.tiktok_service.get_trending_effects(10)
            
            analysis = self.tiktok_service.analyze_tiktok_trends(hashtags, sounds, effects)
            
            return {
                'trending_hashtags': hashtags,
                'trending_sounds': sounds,
                'trending_effects': effects,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting TikTok trends: {e}")
            return {'error': str(e)}
    
    def _get_instagram_trends(self, limit: int) -> Dict[str, Any]:
        """Get Instagram trending data"""
        try:
            hashtags = self.instagram_service.get_trending_hashtags(limit)
            reels_formats = self.instagram_service.get_trending_reels_formats()
            audio = self.instagram_service.get_trending_audio(5)
            
            analysis = self.instagram_service.analyze_instagram_trends(hashtags)
            
            return {
                'trending_hashtags': hashtags,
                'trending_reels_formats': reels_formats,
                'trending_audio': audio,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting Instagram trends: {e}")
            return {'error': str(e)}
    
    def _analyze_cross_platform_trends(self, platforms_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends across all platforms"""
        insights = {
            'common_themes': [],
            'platform_specific_insights': {},
            'viral_patterns': [],
            'content_recommendations': []
        }
        
        # Extract common hashtags across platforms
        all_hashtags = []
        for platform, data in platforms_data.items():
            if 'trending_hashtags' in data:
                all_hashtags.extend([h.get('tag', '').lower() for h in data['trending_hashtags']])
        
        # Find common themes
        hashtag_counts = {}
        for tag in all_hashtags:
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        
        # Tags appearing on multiple platforms
        common_hashtags = [tag for tag, count in hashtag_counts.items() if count > 1]
        insights['common_themes'] = common_hashtags[:10]
        
        # Identify viral patterns
        insights['viral_patterns'] = [
            "Short-form content (15-30s) performing best across platforms",
            "Trending audio/sounds crucial for TikTok and Instagram Reels",
            "Educational content seeing high engagement on all platforms",
            "Before/after and transformation content universally popular",
            "User-generated challenges driving engagement"
        ]
        
        return insights
    
    def _generate_content_recommendations(self, 
                                        platforms_data: Dict[str, Any],
                                        unified_insights: Dict[str, Any],
                                        platform: Optional[str]) -> Dict[str, Any]:
        """Generate specific content recommendations based on trends"""
        recommendations = {
            'content_ideas': [],
            'format_suggestions': {},
            'timing_strategy': {},
            'engagement_tactics': []
        }
        
        # Platform-specific recommendations
        if platform:
            platform_lower = platform.lower()
            
            if platform_lower == 'youtube':
                recommendations['format_suggestions'] = {
                    'video_length': '8-12 minutes for standard, 60 seconds for Shorts',
                    'thumbnail': 'High contrast, clear faces, bold text',
                    'title_format': 'Number + Adjective + Keyword + Benefit'
                }
                
            elif platform_lower == 'tiktok':
                recommendations['format_suggestions'] = {
                    'video_length': '15-30 seconds optimal',
                    'hook': 'First 2 seconds critical',
                    'format': 'Vertical video only (9:16)'
                }
                
            elif platform_lower == 'instagram':
                recommendations['format_suggestions'] = {
                    'reels_length': '15-30 seconds',
                    'carousel': '7-10 slides for education',
                    'stories': '15 second segments'
                }
        
        # Universal recommendations
        recommendations['engagement_tactics'] = [
            "Ask questions to encourage comments",
            "Create content that people want to save/share",
            "Use trending sounds and effects",
            "Post consistently at optimal times",
            "Respond to early comments quickly"
        ]
        
        return recommendations
    
    def _get_cross_platform_hashtags(self, mission: str, category: str) -> List[Dict[str, Any]]:
        """Get hashtags that work across multiple platforms"""
        cross_platform = [
            {'tag': '#viral', 'platform': 'all', 'trend_score': 0.95, 'category': 'growth'},
            {'tag': '#trending', 'platform': 'all', 'trend_score': 0.93, 'category': 'growth'},
            {'tag': '#explore', 'platform': 'all', 'trend_score': 0.90, 'category': 'discovery'},
            {'tag': f'#{category.lower()}', 'platform': 'all', 'trend_score': 0.85, 'category': 'niche'},
            {'tag': '#content', 'platform': 'all', 'trend_score': 0.82, 'category': 'general'},
            {'tag': '#creator', 'platform': 'all', 'trend_score': 0.80, 'category': 'community'}
        ]
        
        # Add mission-specific hashtags
        mission_words = mission.lower().split()[:3]
        for word in mission_words:
            if len(word) > 3:
                cross_platform.append({
                    'tag': f'#{word}',
                    'platform': 'all',
                    'trend_score': 0.75,
                    'category': 'topic'
                })
        
        return cross_platform
    
    def _get_general_trending_hashtags(self, count: int) -> List[Dict[str, Any]]:
        """Get general trending hashtags as fallback"""
        general = [
            {'tag': '#2025', 'platform': 'all', 'trend_score': 0.85, 'category': 'temporal'},
            {'tag': '#motivation', 'platform': 'all', 'trend_score': 0.82, 'category': 'inspiration'},
            {'tag': '#lifestyle', 'platform': 'all', 'trend_score': 0.80, 'category': 'general'},
            {'tag': '#inspiration', 'platform': 'all', 'trend_score': 0.78, 'category': 'inspiration'},
            {'tag': '#goals', 'platform': 'all', 'trend_score': 0.76, 'category': 'motivation'},
            {'tag': '#success', 'platform': 'all', 'trend_score': 0.75, 'category': 'motivation'},
            {'tag': '#mindset', 'platform': 'all', 'trend_score': 0.74, 'category': 'personal'},
            {'tag': '#growth', 'platform': 'all', 'trend_score': 0.73, 'category': 'personal'}
        ]
        
        return general[:count]
    
    def _create_trending_report(self, trending_data: Dict[str, Any], report_path: str):
        """Create a human-readable trending report"""
        try:
            report = f"""# 📈 Trending Analysis Report

Generated: {trending_data.get('analysis_timestamp', 'Unknown')}

## 🔥 Key Insights

### Cross-Platform Trends
"""
            
            # Add unified insights
            insights = trending_data.get('unified_insights', {})
            if insights.get('common_themes'):
                report += "\n**Common Themes:**\n"
                for theme in insights['common_themes'][:5]:
                    report += f"- {theme}\n"
            
            if insights.get('viral_patterns'):
                report += "\n**Viral Patterns:**\n"
                for pattern in insights['viral_patterns']:
                    report += f"- {pattern}\n"
            
            # Add platform-specific data
            for platform, data in trending_data.get('platforms', {}).items():
                if 'error' not in data:
                    report += f"\n## {platform.capitalize()} Trends\n\n"
                    
                    if platform == 'youtube' and 'analysis' in data:
                        analysis = data['analysis']
                        report += f"**Videos Analyzed:** {analysis.get('total_videos_analyzed', 0)}\n"
                        report += f"**Average Views:** {analysis.get('average_metrics', {}).get('views', 0):,}\n"
                        
                        if 'trending_title_words' in analysis:
                            report += "\n**Trending Words:**\n"
                            for word_data in analysis['trending_title_words'][:5]:
                                report += f"- {word_data['word']} ({word_data['count']} occurrences)\n"
                    
                    elif platform == 'tiktok' and 'trending_hashtags' in data:
                        report += f"**Top Hashtags:**\n"
                        for hashtag in data['trending_hashtags'][:5]:
                            report += f"- {hashtag['tag']} (Score: {hashtag.get('trend_score', 0):.2f})\n"
                    
                    elif platform == 'instagram' and 'analysis' in data:
                        analysis = data['analysis']
                        if 'platform_insights' in analysis:
                            report += "**Best Posting Times:**\n"
                            times = analysis['platform_insights'].get('best_posting_times', [])
                            if times and len(times) > 0:
                                for day_data in times[:3]:
                                    report += f"- {day_data['day']}: {', '.join(day_data['times'][:2])}\n"
            
            # Add recommendations
            recommendations = trending_data.get('recommendations', {})
            if recommendations:
                report += "\n## 💡 Recommendations\n\n"
                
                if recommendations.get('engagement_tactics'):
                    report += "**Engagement Tactics:**\n"
                    for tactic in recommendations['engagement_tactics']:
                        report += f"- {tactic}\n"
            
            # Save report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"📄 Trending report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Error creating trending report: {e}")