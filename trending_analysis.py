#!/usr/bin/env python3
"""
Trending Analysis Tool
Analyze current trending videos and generate insights
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.youtube_scraper import YouTubeScraper
from src.analyzers.video_analyzer import VideoAnalyzer
from src.models.video_models import TrendingVideo, VideoAnalysis
from src.utils.logging_config import get_logger
from config.config import settings

logger = get_logger(__name__)

class TrendingAnalyzer:
    """Analyze trending videos and generate insights"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube_scraper = YouTubeScraper(api_key=api_key, use_mock_data=not api_key)
        self.video_analyzer = VideoAnalyzer(api_key=api_key)
        
    def analyze_trending(self, topic: Optional[str] = None, max_videos: int = 10, days_back: int = 6) -> Dict:
        """
        Analyze trending videos and generate insights
        
        Args:
            topic: Optional topic to search for (if None, gets general trending)
            max_videos: Maximum number of videos to analyze
            days_back: Number of days back to search for trending videos (default: 6)
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"🔥 Starting trending analysis for: {topic or 'general trending'} (last {days_back} days)")
        
        try:
            # Get trending videos
            if topic:
                logger.info(f"📊 Searching for videos about: {topic} from last {days_back} days")
                videos = self.youtube_scraper.search_videos(
                    query=topic,
                    max_results=max_videos,
                    order='viewCount',
                    days_back=days_back
                )
            else:
                logger.info(f"📊 Getting general trending videos from last {days_back} days")
                videos = self.youtube_scraper.get_trending_videos(
                    max_results=max_videos,
                    days_back=days_back
                )
            
            if not videos:
                logger.warning(f"No videos found for analysis in the last {days_back} days")
                return self._get_empty_analysis(topic, days_back)
            
            logger.info(f"✅ Found {len(videos)} videos to analyze from last {days_back} days")
            
            # Analyze each video
            analyses = []
            for i, video in enumerate(videos, 1):
                logger.info(f"🔍 Analyzing video {i}/{len(videos)}: {video.title[:50]}...")
                try:
                    analysis = self.video_analyzer.analyze_video(video)
                    analyses.append(analysis)
                except Exception as e:
                    logger.error(f"Failed to analyze video {video.video_id}: {e}")
                    continue
            
            # Generate insights report
            insights = self.video_analyzer.generate_insights_report(analyses)
            
            # Create comprehensive report
            report = {
                'analysis_metadata': {
                    'topic': topic,
                    'days_back': days_back,
                    'timestamp': datetime.now().isoformat(),
                    'total_videos_found': len(videos),
                    'total_videos_analyzed': len(analyses),
                    'analysis_success_rate': len(analyses) / len(videos) if videos else 0
                },
                'trending_videos': [self._video_to_dict(video) for video in videos],
                'video_analyses': [self._analysis_to_dict(analysis) for analysis in analyses],
                'insights': insights,
                'recommendations': self._generate_recommendations(analyses, insights)
            }
            
            # Save report
            self._save_report(report, topic, days_back)
            
            logger.info(f"🎯 Analysis complete! {len(analyses)} videos analyzed from last {days_back} days")
            return report
            
        except Exception as e:
            logger.error(f"Trending analysis failed: {e}")
            return self._get_error_analysis(topic, str(e), days_back)
    
    def _video_to_dict(self, video: TrendingVideo) -> Dict:
        """Convert TrendingVideo to dictionary"""
        return {
            'video_id': video.video_id,
            'title': video.title,
            'description': video.description[:200] + "..." if video.description and len(video.description) > 200 else video.description,
            'url': str(video.url),
            'view_count': video.view_count,
            'like_count': video.like_count,
            'comment_count': video.comment_count,
            'upload_date': video.upload_date.isoformat(),
            'channel_name': video.channel_name,
            'duration_seconds': video.duration_seconds,
            'category': video.category.value if hasattr(video.category, 'value') else str(video.category),
            'tags': video.tags[:10],  # Limit tags
            'trending_position': video.trending_position
        }
    
    def _analysis_to_dict(self, analysis: VideoAnalysis) -> Dict:
        """Convert VideoAnalysis to dictionary"""
        return {
            'video_id': analysis.video_id,
            'viral_score': analysis.viral_score,
            'viral_velocity': analysis.viral_velocity,
            'engagement_rate': analysis.engagement_rate,
            'content_themes': analysis.content_themes,
            'emotional_tone': analysis.emotional_tone,
            'target_audience': analysis.target_audience,
            'success_factors': analysis.success_factors,
            'title_keywords': analysis.title_keywords,
            'hook_analysis': analysis.hook_analysis,
            'improvement_suggestions': analysis.improvement_suggestions[:3]  # Top 3
        }
    
    def _generate_recommendations(self, analyses: List[VideoAnalysis], insights: Dict) -> Dict:
        """Generate actionable recommendations"""
        if not analyses:
            return {}
        
        # Calculate averages
        avg_viral_score = sum(a.viral_score for a in analyses) / len(analyses)
        avg_engagement = sum(a.engagement_rate for a in analyses) / len(analyses)
        
        # Get most common themes and factors
        all_themes = [theme for a in analyses for theme in a.content_themes]
        all_factors = [factor for a in analyses for factor in a.success_factors]
        
        from collections import Counter
        top_themes = Counter(all_themes).most_common(5)
        top_factors = Counter(all_factors).most_common(5)
        
        return {
            'content_strategy': {
                'recommended_themes': [theme for theme, count in top_themes],
                'viral_score_benchmark': f"{avg_viral_score:.2f}",
                'engagement_benchmark': f"{avg_engagement:.4f}",
                'top_success_factors': [factor for factor, count in top_factors]
            },
            'optimization_tips': [
                f"Focus on {top_themes[0][0]} content (appears in {top_themes[0][1]} trending videos)" if top_themes else "Create engaging content",
                f"Target {avg_engagement:.2%} engagement rate or higher",
                f"Aim for viral score above {avg_viral_score:.2f}",
                "Use trending keywords in titles and descriptions",
                "Create strong hooks in first 3 seconds"
            ],
            'trending_patterns': {
                'most_viral_category': insights.get('insights', {}).get('best_performing_category', 'Unknown'),
                'optimal_duration': insights.get('insights', {}).get('optimal_duration', 'Unknown'),
                'common_hooks': insights.get('insights', {}).get('common_hooks', [])
            }
        }
    
    def _save_report(self, report: Dict, topic: Optional[str], days_back: int):
        """Save analysis report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        topic_safe = topic.replace(' ', '_').lower() if topic else 'general'
        filename = f"trending_analysis_{topic_safe}_{timestamp}_last_{days_back}days.json"
        
        os.makedirs("outputs", exist_ok=True)
        filepath = os.path.join("outputs", filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Analysis report saved: {filepath}")
    
    def _get_empty_analysis(self, topic: Optional[str], days_back: int) -> Dict:
        """Return empty analysis when no videos found"""
        return {
            'analysis_metadata': {
                'topic': topic,
                'days_back': days_back,
                'timestamp': datetime.now().isoformat(),
                'total_videos_found': 0,
                'total_videos_analyzed': 0,
                'analysis_success_rate': 0
            },
            'trending_videos': [],
            'video_analyses': [],
            'insights': {},
            'recommendations': {
                'message': 'No trending videos found for analysis. Try a different topic or check your API connection.'
            }
        }
    
    def _get_error_analysis(self, topic: Optional[str], error: str, days_back: int) -> Dict:
        """Return error analysis"""
        return {
            'analysis_metadata': {
                'topic': topic,
                'days_back': days_back,
                'timestamp': datetime.now().isoformat(),
                'error': error,
                'total_videos_found': 0,
                'total_videos_analyzed': 0,
                'analysis_success_rate': 0
            },
            'trending_videos': [],
            'video_analyses': [],
            'insights': {},
            'recommendations': {
                'message': f'Analysis failed: {error}'
            }
        }

def print_analysis_summary(report: Dict):
    """Print a beautiful summary of the analysis"""
    metadata = report.get('analysis_metadata', {})
    insights = report.get('insights', {})
    recommendations = report.get('recommendations', {})
    
    print("\n" + "="*80)
    print("🔥 TRENDING VIDEO ANALYSIS REPORT")
    print("="*80)
    
    # Metadata
    print(f"\n📊 Analysis Overview:")
    print(f"   Topic: {metadata.get('topic', 'General Trending')}")
    print(f"   Time Range: Last {metadata.get('days_back', 6)} days")
    print(f"   Timestamp: {metadata.get('timestamp', 'Unknown')}")
    print(f"   Videos Found: {metadata.get('total_videos_found', 0)}")
    print(f"   Videos Analyzed: {metadata.get('total_videos_analyzed', 0)}")
    print(f"   Success Rate: {metadata.get('analysis_success_rate', 0):.1%}")
    
    # Top videos
    videos = report.get('trending_videos', [])
    if videos:
        print(f"\n🎬 Top Trending Videos:")
        for i, video in enumerate(videos[:5], 1):
            print(f"   {i}. {video['title'][:60]}...")
            print(f"      👀 {video['view_count']:,} views | ❤️ {video['like_count']:,} likes | 💬 {video['comment_count']:,} comments")
            print(f"      📺 {video['channel_name']} | ⏱️ {video['duration_seconds']}s")
    
    # Insights
    if insights:
        print(f"\n💡 Key Insights:")
        print(f"   Average Viral Score: {insights.get('average_viral_score', 0):.2f}")
        print(f"   Average Engagement: {insights.get('average_engagement_rate', 0):.4f}")
        
        top_themes = insights.get('top_themes', [])
        if top_themes:
            print(f"   Top Content Themes:")
            for theme, count in top_themes[:3]:
                print(f"     • {theme} ({count} videos)")
    
    # Recommendations
    content_strategy = recommendations.get('content_strategy', {})
    if content_strategy:
        print(f"\n🎯 Recommendations:")
        themes = content_strategy.get('recommended_themes', [])
        if themes:
            print(f"   Recommended Themes: {', '.join(themes[:3])}")
        
        factors = content_strategy.get('top_success_factors', [])
        if factors:
            print(f"   Success Factors: {', '.join(factors[:3])}")
    
    tips = recommendations.get('optimization_tips', [])
    if tips:
        print(f"\n✨ Optimization Tips:")
        for tip in tips[:3]:
            print(f"   • {tip}")
    
    print("\n" + "="*80)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Analyze trending videos")
    parser.add_argument("--topic", "-t", help="Topic to analyze (optional)")
    parser.add_argument("--max-videos", "-m", type=int, default=10, help="Maximum videos to analyze")
    parser.add_argument("--days-back", "-d", type=int, default=6, help="Number of days back to search (default: 6)")
    parser.add_argument("--api-key", help="Google API key (optional, uses config if not provided)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode - minimal output")
    
    args = parser.parse_args()
    
    # Validate days_back
    if args.days_back < 1 or args.days_back > 30:
        print("❌ Error: days-back must be between 1 and 30")
        sys.exit(1)
    
    # Get API key
    api_key = args.api_key or settings.google_api_key
    if not api_key:
        print("❌ Error: No Google API key provided. Set GOOGLE_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Show configuration
    if not args.quiet:
        print(f"🔍 Analyzing trending videos...")
        print(f"   Topic: {args.topic or 'General trending'}")
        print(f"   Time range: Last {args.days_back} days")
        print(f"   Max videos: {args.max_videos}")
        print()
    
    # Run analysis
    analyzer = TrendingAnalyzer(api_key)
    report = analyzer.analyze_trending(args.topic, args.max_videos, args.days_back)
    
    # Print results
    if not args.quiet:
        print_analysis_summary(report)
    
    # Return report for programmatic use
    return report

if __name__ == "__main__":
    main() 