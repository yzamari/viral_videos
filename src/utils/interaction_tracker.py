"""
Interaction Tracking and Optimization System
Tracks user interactions and optimizes content for maximum engagement
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest
from ..ai.interfaces.base import AIServiceType

logger = get_logger(__name__)

class InteractionTracker:
    """
    Tracks and analyzes user interactions to optimize future content
    Focuses on likes, follows, reactions, and behavioral patterns
    """
    
    def __init__(self, session_context, ai_manager: AIServiceManager = None):
        self.session_context = session_context
        self.ai_manager = ai_manager
        self.tracking_data = {}
        self.interaction_history = []
        
        # Create tracking directory
        self.tracking_dir = Path(session_context.session_dir) / "interaction_tracking"
        self.tracking_dir.mkdir(exist_ok=True)
        
        logger.info("✅ Interaction Tracker initialized")
    
    def track_engagement_metrics(
        self,
        content_id: str,
        platform: str,
        metrics: Dict[str, Any],
        timestamp: Optional[str] = None
    ) -> None:
        """
        Track engagement metrics for specific content
        
        Args:
            content_id: Unique identifier for the content
            platform: Platform where content was posted
            metrics: Dictionary containing engagement metrics
            timestamp: When metrics were recorded
        """
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        logger.info(f"📊 Tracking engagement for {content_id} on {platform}")
        
        interaction_data = {
            "content_id": content_id,
            "platform": platform,
            "timestamp": timestamp,
            "metrics": {
                "views": metrics.get("views", 0),
                "likes": metrics.get("likes", 0),
                "comments": metrics.get("comments", 0),
                "shares": metrics.get("shares", 0),
                "follows": metrics.get("follows", 0),
                "saves": metrics.get("saves", 0),
                "reach": metrics.get("reach", 0),
                "impressions": metrics.get("impressions", 0),
                "click_through_rate": metrics.get("click_through_rate", 0),
                "completion_rate": metrics.get("completion_rate", 0),
                "average_watch_time": metrics.get("average_watch_time", 0),
                "retention_rate": metrics.get("retention_rate", 0)
            },
            "calculated_rates": self._calculate_engagement_rates(metrics),
            "engagement_score": self._calculate_engagement_score(metrics)
        }
        
        # Store in tracking data
        if content_id not in self.tracking_data:
            self.tracking_data[content_id] = []
        
        self.tracking_data[content_id].append(interaction_data)
        self.interaction_history.append(interaction_data)
        
        # Save to file
        self._save_tracking_data(content_id, interaction_data)
        
        logger.info(f"✅ Tracked engagement - Score: {interaction_data['engagement_score']:.1f}")
    
    def track_behavioral_patterns(
        self,
        content_id: str,
        behavioral_data: Dict[str, Any]
    ) -> None:
        """
        Track user behavioral patterns for optimization insights
        """
        logger.info(f"🧠 Tracking behavioral patterns for {content_id}")
        
        behavior_tracking = {
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "patterns": {
                "peak_engagement_times": behavioral_data.get("peak_times", []),
                "drop_off_points": behavioral_data.get("drop_offs", []),
                "replay_segments": behavioral_data.get("replays", []),
                "skip_patterns": behavioral_data.get("skips", []),
                "comment_sentiment": behavioral_data.get("sentiment", {}),
                "user_demographics": behavioral_data.get("demographics", {}),
                "device_types": behavioral_data.get("devices", {}),
                "traffic_sources": behavioral_data.get("sources", {})
            }
        }
        
        # Save behavioral data
        behavior_file = self.tracking_dir / f"{content_id}_behavior.json"
        with open(behavior_file, 'w') as f:
            json.dump(behavior_tracking, f, indent=2)
        
        logger.info("✅ Behavioral patterns tracked")
    
    async def analyze_interaction_patterns(
        self,
        content_ids: List[str] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze interaction patterns to identify optimization opportunities
        """
        logger.info("🔍 Analyzing interaction patterns")
        
        # Get data for analysis
        if content_ids:
            analysis_data = [data for content_id in content_ids 
                           for data in self.tracking_data.get(content_id, [])]
        else:
            # Analyze recent data
            cutoff_date = datetime.now() - timedelta(days=time_range_days)
            analysis_data = [data for data in self.interaction_history 
                           if datetime.fromisoformat(data['timestamp']) > cutoff_date]
        
        if not analysis_data:
            logger.warning("No interaction data available for analysis")
            return {"error": "No data available"}
        
        # Perform analysis
        patterns = self._analyze_patterns(analysis_data)
        
        # Generate AI insights if available
        ai_insights = {}
        if self.ai_manager:
            ai_insights = await self._generate_ai_insights(patterns, analysis_data)
        
        analysis_result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_points_analyzed": len(analysis_data),
            "time_range_days": time_range_days,
            "patterns": patterns,
            "ai_insights": ai_insights,
            "optimization_recommendations": self._generate_optimization_recommendations(patterns),
            "success_factors": self._identify_success_factors(analysis_data),
            "failure_indicators": self._identify_failure_indicators(analysis_data)
        }
        
        # Save analysis
        analysis_file = self.tracking_dir / f"interaction_analysis_{int(time.time())}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        logger.info("✅ Interaction pattern analysis complete")
        return analysis_result
    
    def track_content_performance_over_time(
        self,
        content_id: str,
        tracking_duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Track how content performance evolves over time
        """
        logger.info(f"⏰ Tracking performance over time for {content_id}")
        
        content_data = self.tracking_data.get(content_id, [])
        if not content_data:
            return {"error": "No data available for content"}
        
        # Sort by timestamp
        content_data.sort(key=lambda x: x['timestamp'])
        
        # Analyze performance evolution
        performance_timeline = []
        growth_rates = {}
        
        for i, data_point in enumerate(content_data):
            if i == 0:
                # First data point
                growth_rates = {metric: 0 for metric in data_point['metrics'].keys()}
            else:
                # Calculate growth rates
                prev_metrics = content_data[i-1]['metrics']
                curr_metrics = data_point['metrics']
                
                for metric, current_value in curr_metrics.items():
                    prev_value = prev_metrics.get(metric, 0)
                    if prev_value > 0:
                        growth_rate = ((current_value - prev_value) / prev_value) * 100
                    else:
                        growth_rate = 100 if current_value > 0 else 0
                    growth_rates[metric] = round(growth_rate, 2)
            
            performance_timeline.append({
                "timestamp": data_point['timestamp'],
                "metrics": data_point['metrics'],
                "engagement_score": data_point['engagement_score'],
                "growth_rates": growth_rates.copy()
            })
        
        # Identify performance phases
        phases = self._identify_performance_phases(performance_timeline)
        
        return {
            "content_id": content_id,
            "tracking_start": content_data[0]['timestamp'],
            "tracking_end": content_data[-1]['timestamp'],
            "data_points": len(content_data),
            "performance_timeline": performance_timeline,
            "performance_phases": phases,
            "peak_performance": max(performance_timeline, key=lambda x: x['engagement_score']),
            "overall_growth": self._calculate_overall_growth(content_data[0], content_data[-1])
        }
    
    def predict_optimal_posting_times(
        self,
        platform: str,
        content_type: str = None
    ) -> Dict[str, Any]:
        """
        Predict optimal posting times based on historical interaction data
        """
        logger.info(f"🎯 Predicting optimal posting times for {platform}")
        
        # Filter data by platform
        platform_data = [data for data in self.interaction_history 
                        if data['platform'].lower() == platform.lower()]
        
        if not platform_data:
            return {"error": f"No data available for {platform}"}
        
        # Analyze posting times vs engagement
        hourly_performance = {}
        daily_performance = {}
        
        for data in platform_data:
            dt = datetime.fromisoformat(data['timestamp'])
            hour = dt.hour
            day = dt.strftime('%A')
            score = data['engagement_score']
            
            # Hourly analysis
            if hour not in hourly_performance:
                hourly_performance[hour] = []
            hourly_performance[hour].append(score)
            
            # Daily analysis
            if day not in daily_performance:
                daily_performance[day] = []
            daily_performance[day].append(score)
        
        # Calculate averages
        best_hours = {hour: sum(scores)/len(scores) 
                     for hour, scores in hourly_performance.items()}
        best_days = {day: sum(scores)/len(scores) 
                    for day, scores in daily_performance.items()}
        
        # Get top recommendations
        top_hours = sorted(best_hours.items(), key=lambda x: x[1], reverse=True)[:3]
        top_days = sorted(best_days.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "platform": platform,
            "analysis_based_on": len(platform_data),
            "optimal_hours": [{"hour": hour, "avg_score": round(score, 1)} 
                             for hour, score in top_hours],
            "optimal_days": [{"day": day, "avg_score": round(score, 1)} 
                            for day, score in top_days],
            "recommendations": self._generate_timing_recommendations(top_hours, top_days),
            "hourly_breakdown": {hour: round(avg, 1) for hour, avg in best_hours.items()},
            "daily_breakdown": {day: round(avg, 1) for day, avg in best_days.items()}
        }
    
    def compare_content_performance(
        self,
        content_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare performance across multiple pieces of content
        """
        logger.info(f"📊 Comparing performance across {len(content_ids)} pieces of content")
        
        comparison_data = {}
        
        for content_id in content_ids:
            if content_id in self.tracking_data:
                latest_data = self.tracking_data[content_id][-1]  # Get latest metrics
                comparison_data[content_id] = {
                    "metrics": latest_data['metrics'],
                    "engagement_score": latest_data['engagement_score'],
                    "calculated_rates": latest_data['calculated_rates']
                }
        
        if not comparison_data:
            return {"error": "No data available for comparison"}
        
        # Find best and worst performers
        sorted_by_score = sorted(comparison_data.items(), 
                               key=lambda x: x[1]['engagement_score'], 
                               reverse=True)
        
        best_performer = sorted_by_score[0]
        worst_performer = sorted_by_score[-1]
        
        # Calculate averages
        total_scores = [data['engagement_score'] for data in comparison_data.values()]
        average_score = sum(total_scores) / len(total_scores)
        
        # Identify top performing metrics
        metric_averages = {}
        for metric in ['likes', 'comments', 'shares', 'follows']:
            values = [data['metrics'].get(metric, 0) for data in comparison_data.values()]
            metric_averages[metric] = sum(values) / len(values) if values else 0
        
        return {
            "comparison_timestamp": datetime.now().isoformat(),
            "content_analyzed": len(comparison_data),
            "best_performer": {
                "content_id": best_performer[0],
                "engagement_score": best_performer[1]['engagement_score'],
                "metrics": best_performer[1]['metrics']
            },
            "worst_performer": {
                "content_id": worst_performer[0],
                "engagement_score": worst_performer[1]['engagement_score'],
                "metrics": worst_performer[1]['metrics']
            },
            "average_engagement_score": round(average_score, 1),
            "metric_averages": {k: round(v, 1) for k, v in metric_averages.items()},
            "performance_distribution": {
                "excellent": len([s for s in total_scores if s >= 80]),
                "good": len([s for s in total_scores if 60 <= s < 80]),
                "average": len([s for s in total_scores if 40 <= s < 60]),
                "poor": len([s for s in total_scores if s < 40])
            },
            "detailed_comparison": comparison_data
        }
    
    def export_tracking_data(
        self,
        output_format: str = "json",
        include_behavioral: bool = False
    ) -> str:
        """
        Export all tracking data for external analysis
        """
        logger.info(f"📤 Exporting tracking data in {output_format} format")
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_interactions": len(self.interaction_history),
            "content_pieces": len(self.tracking_data),
            "interaction_history": self.interaction_history
        }
        
        if include_behavioral:
            # Include behavioral data
            behavioral_files = list(self.tracking_dir.glob("*_behavior.json"))
            behavioral_data = {}
            
            for file_path in behavioral_files:
                with open(file_path, 'r') as f:
                    content_id = file_path.stem.replace('_behavior', '')
                    behavioral_data[content_id] = json.load(f)
            
            export_data["behavioral_data"] = behavioral_data
        
        # Save export file
        timestamp = int(time.time())
        export_file = self.tracking_dir / f"interaction_export_{timestamp}.{output_format}"
        
        if output_format.lower() == "json":
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        else:
            # For other formats, convert to JSON first
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        logger.info(f"✅ Data exported to {export_file}")
        return str(export_file)
    
    def _calculate_engagement_rates(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate various engagement rates"""
        views = metrics.get('views', 0)
        if views == 0:
            return {metric: 0.0 for metric in ['like_rate', 'comment_rate', 'share_rate', 'follow_rate']}
        
        return {
            'like_rate': round((metrics.get('likes', 0) / views) * 100, 2),
            'comment_rate': round((metrics.get('comments', 0) / views) * 100, 2),
            'share_rate': round((metrics.get('shares', 0) / views) * 100, 2),
            'follow_rate': round((metrics.get('follows', 0) / views) * 100, 2),
            'save_rate': round((metrics.get('saves', 0) / views) * 100, 2)
        }
    
    def _calculate_engagement_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall engagement score"""
        views = metrics.get('views', 1)  # Avoid division by zero
        
        # Weighted engagement score
        likes_weight = 1
        comments_weight = 3
        shares_weight = 5
        follows_weight = 10
        saves_weight = 2
        
        score = (
            (metrics.get('likes', 0) * likes_weight) +
            (metrics.get('comments', 0) * comments_weight) +
            (metrics.get('shares', 0) * shares_weight) +
            (metrics.get('follows', 0) * follows_weight) +
            (metrics.get('saves', 0) * saves_weight)
        ) / views * 100
        
        # Add completion rate bonus
        completion_bonus = metrics.get('completion_rate', 0) * 0.5
        
        return round(score + completion_bonus, 1)
    
    def _save_tracking_data(self, content_id: str, data: Dict[str, Any]) -> None:
        """Save tracking data to file"""
        file_path = self.tracking_dir / f"{content_id}_tracking.json"
        
        # Load existing data if file exists
        existing_data = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
        
        # Append new data
        existing_data.append(data)
        
        # Save updated data
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def _analyze_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in interaction data"""
        if not data:
            return {}
        
        # Platform performance
        platform_performance = {}
        for item in data:
            platform = item['platform']
            score = item['engagement_score']
            
            if platform not in platform_performance:
                platform_performance[platform] = []
            platform_performance[platform].append(score)
        
        # Calculate platform averages
        platform_averages = {platform: sum(scores)/len(scores) 
                           for platform, scores in platform_performance.items()}
        
        # Time-based patterns
        hour_performance = {}
        for item in data:
            hour = datetime.fromisoformat(item['timestamp']).hour
            score = item['engagement_score']
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(score)
        
        hour_averages = {hour: sum(scores)/len(scores) 
                        for hour, scores in hour_performance.items()}
        
        return {
            "platform_performance": {k: round(v, 1) for k, v in platform_averages.items()},
            "hourly_performance": {k: round(v, 1) for k, v in hour_averages.items()},
            "best_platform": max(platform_averages.items(), key=lambda x: x[1])[0],
            "best_hour": max(hour_averages.items(), key=lambda x: x[1])[0],
            "total_data_points": len(data),
            "average_engagement": round(sum(item['engagement_score'] for item in data) / len(data), 1)
        }
    
    async def _generate_ai_insights(self, patterns: Dict[str, Any], data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered insights from interaction data"""
        if not self.ai_manager:
            return {}
        
        try:
            prompt = f"""
Analyze this interaction tracking data and provide optimization insights:

PATTERNS FOUND:
{json.dumps(patterns, indent=2)}

SAMPLE DATA POINTS: {len(data)}

Provide insights on:
1. What content performs best and why
2. Optimal timing strategies
3. Platform-specific recommendations
4. Engagement improvement opportunities
5. Patterns that predict viral content

Return JSON with actionable insights.
"""
            
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            response = await text_service.generate(request)
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {}
    
    def _generate_optimization_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on patterns"""
        recommendations = []
        
        if 'best_platform' in patterns:
            recommendations.append(f"Focus more content on {patterns['best_platform']} platform for better performance")
        
        if 'best_hour' in patterns:
            recommendations.append(f"Post at {patterns['best_hour']}:00 for optimal engagement")
        
        if patterns.get('average_engagement', 0) < 50:
            recommendations.extend([
                "Overall engagement is below average - review content quality",
                "Consider A/B testing different content formats",
                "Analyze successful competitors for inspiration"
            ])
        
        return recommendations
    
    def _identify_success_factors(self, data: List[Dict[str, Any]]) -> List[str]:
        """Identify factors that correlate with high engagement"""
        high_performers = [item for item in data if item['engagement_score'] > 70]
        
        if not high_performers:
            return ["No high-performing content identified in dataset"]
        
        # Analyze common factors
        factors = []
        
        # Platform analysis
        platforms = [item['platform'] for item in high_performers]
        most_common_platform = max(set(platforms), key=platforms.count)
        factors.append(f"High performance on {most_common_platform}")
        
        # Timing analysis
        hours = [datetime.fromisoformat(item['timestamp']).hour for item in high_performers]
        most_common_hour = max(set(hours), key=hours.count)
        factors.append(f"Posting around {most_common_hour}:00 shows strong performance")
        
        return factors
    
    def _identify_failure_indicators(self, data: List[Dict[str, Any]]) -> List[str]:
        """Identify factors that correlate with low engagement"""
        low_performers = [item for item in data if item['engagement_score'] < 30]
        
        if not low_performers:
            return ["No significant failure patterns identified"]
        
        indicators = []
        
        # Platform analysis
        platforms = [item['platform'] for item in low_performers]
        if platforms:
            most_common_platform = max(set(platforms), key=platforms.count)
            indicators.append(f"Poor performance patterns on {most_common_platform}")
        
        # Timing analysis
        hours = [datetime.fromisoformat(item['timestamp']).hour for item in low_performers]
        if hours:
            most_common_hour = max(set(hours), key=hours.count)
            indicators.append(f"Low engagement when posting around {most_common_hour}:00")
        
        return indicators
    
    def _identify_performance_phases(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify different phases in content performance"""
        if len(timeline) < 3:
            return {"phases": ["insufficient_data"]}
        
        scores = [point['engagement_score'] for point in timeline]
        
        # Simple phase detection
        early_avg = sum(scores[:len(scores)//3]) / (len(scores)//3)
        middle_avg = sum(scores[len(scores)//3:2*len(scores)//3]) / (len(scores)//3)
        late_avg = sum(scores[2*len(scores)//3:]) / (len(scores) - 2*len(scores)//3)
        
        phases = []
        if early_avg > middle_avg and early_avg > late_avg:
            phases.append("strong_start_decline")
        elif late_avg > early_avg and late_avg > middle_avg:
            phases.append("slow_start_growth")
        elif middle_avg > early_avg and middle_avg > late_avg:
            phases.append("peak_in_middle")
        else:
            phases.append("steady_performance")
        
        return {
            "phases": phases,
            "early_performance": round(early_avg, 1),
            "middle_performance": round(middle_avg, 1),
            "late_performance": round(late_avg, 1)
        }
    
    def _calculate_overall_growth(self, first_data: Dict, last_data: Dict) -> Dict[str, float]:
        """Calculate overall growth between first and last data points"""
        growth = {}
        
        for metric in ['likes', 'comments', 'shares', 'follows']:
            first_value = first_data['metrics'].get(metric, 0)
            last_value = last_data['metrics'].get(metric, 0)
            
            if first_value > 0:
                growth_rate = ((last_value - first_value) / first_value) * 100
            else:
                growth_rate = 100 if last_value > 0 else 0
            
            growth[f"{metric}_growth"] = round(growth_rate, 1)
        
        return growth
    
    def _generate_timing_recommendations(self, top_hours: List[Tuple], top_days: List[Tuple]) -> List[str]:
        """Generate timing recommendations based on performance data"""
        recommendations = []
        
        if top_hours:
            best_hour = top_hours[0][0]
            recommendations.append(f"Optimal posting time: {best_hour}:00")
        
        if top_days:
            best_day = top_days[0][0]
            recommendations.append(f"Best day for posting: {best_day}")
        
        recommendations.extend([
            "Consider scheduling content during peak performance windows",
            "Test different time slots to validate patterns",
            "Monitor audience timezone differences for global reach"
        ])
        
        return recommendations