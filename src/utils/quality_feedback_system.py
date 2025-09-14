"""
Quality Feedback System - Learn and improve from generated videos
Implements SOLID principles for continuous quality improvement
"""

import os
import json
import pickle
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Protocol
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import numpy as np
from collections import defaultdict

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


# Interface Segregation
class IFeedbackCollector(Protocol):
    """Interface for collecting feedback"""
    def collect(self, video_path: str, metadata: Dict) -> Dict:
        ...
    
    def store(self, feedback: Dict) -> bool:
        ...


class IQualityAnalyzer(Protocol):
    """Interface for analyzing quality"""
    def analyze(self, video_path: str) -> Dict[str, float]:
        ...
    
    def compare(self, metrics1: Dict, metrics2: Dict) -> float:
        ...


class ILearningEngine(Protocol):
    """Interface for learning from feedback"""
    def learn(self, feedback_data: List[Dict]) -> Dict:
        ...
    
    def predict(self, features: Dict) -> float:
        ...


# Single Responsibility - Data classes
class FeedbackType(Enum):
    """Types of feedback"""
    AUTOMATIC = "automatic"
    USER = "user"
    ENGAGEMENT = "engagement"
    TECHNICAL = "technical"
    AESTHETIC = "aesthetic"


@dataclass
class VideoFeedback:
    """Feedback data for a video"""
    video_id: str
    timestamp: datetime
    video_path: str
    quality_metrics: Dict[str, float]
    user_rating: Optional[float] = None
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    technical_issues: List[str] = field(default_factory=list)
    improvements_applied: List[str] = field(default_factory=list)
    generation_params: Dict[str, Any] = field(default_factory=dict)
    platform: Optional[str] = None
    success: bool = True


@dataclass
class QualityTrend:
    """Quality trend over time"""
    metric_name: str
    values: List[float]
    timestamps: List[datetime]
    trend_direction: str  # 'improving', 'declining', 'stable'
    average: float
    std_deviation: float


@dataclass
class LearningInsight:
    """Insights from quality learning"""
    insight_type: str
    description: str
    confidence: float
    recommendations: List[str]
    affected_metrics: List[str]


@dataclass
class FeedbackReport:
    """Comprehensive feedback analysis report"""
    total_videos: int
    average_quality: float
    quality_trends: List[QualityTrend]
    top_issues: List[Tuple[str, int]]
    insights: List[LearningInsight]
    recommendations: List[str]
    improvement_rate: float


# Abstract base classes
class BaseFeedbackCollector(ABC):
    """Base class for feedback collection"""
    
    @abstractmethod
    def collect(self, video_path: str, metadata: Dict) -> VideoFeedback:
        """Collect feedback for a video"""
        pass
    
    @abstractmethod
    def store(self, feedback: VideoFeedback) -> bool:
        """Store feedback data"""
        pass


class BaseLearningEngine(ABC):
    """Base class for learning engines"""
    
    @abstractmethod
    def learn(self, feedback_data: List[VideoFeedback]) -> Dict:
        """Learn from feedback data"""
        pass
    
    @abstractmethod
    def predict_quality(self, params: Dict) -> float:
        """Predict quality based on parameters"""
        pass


# Concrete implementations
class AutomaticFeedbackCollector(BaseFeedbackCollector):
    """Collects automatic quality feedback"""
    
    def __init__(self):
        from ..agents.advanced_quality_controller import VisualQualityChecker, AudioQualityChecker
        self.visual_checker = VisualQualityChecker()
        self.audio_checker = AudioQualityChecker()
    
    def collect(self, video_path: str, metadata: Dict) -> VideoFeedback:
        """Collect automatic feedback"""
        try:
            # Analyze video quality
            visual_metrics = self.visual_checker.check(video_path)
            
            # Analyze audio if available
            audio_path = metadata.get('audio_path')
            if audio_path and os.path.exists(audio_path):
                audio_metrics = self.audio_checker.check(audio_path)
            else:
                audio_metrics = {}
            
            # Combine metrics
            quality_metrics = {
                **{f'visual_{k}': v for k, v in visual_metrics.items()},
                **{f'audio_{k}': v for k, v in audio_metrics.items()}
            }
            
            # Create feedback
            feedback = VideoFeedback(
                video_id=metadata.get('session_id', 'unknown'),
                timestamp=datetime.now(),
                video_path=video_path,
                quality_metrics=quality_metrics,
                generation_params=metadata.get('config', {}),
                platform=metadata.get('platform'),
                success=True
            )
            
            return feedback
            
        except Exception as e:
            logger.error(f"❌ Automatic feedback collection failed: {e}")
            return VideoFeedback(
                video_id='error',
                timestamp=datetime.now(),
                video_path=video_path,
                quality_metrics={},
                success=False
            )
    
    def store(self, feedback: VideoFeedback) -> bool:
        """Store feedback to file"""
        try:
            feedback_dir = Path('outputs/quality_feedback')
            feedback_dir.mkdir(parents=True, exist_ok=True)
            
            # Store as JSON
            feedback_file = feedback_dir / f"feedback_{feedback.video_id}_{feedback.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            
            feedback_dict = asdict(feedback)
            feedback_dict['timestamp'] = feedback.timestamp.isoformat()
            
            with open(feedback_file, 'w') as f:
                json.dump(feedback_dict, f, indent=2)
            
            logger.info(f"💾 Feedback stored: {feedback_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store feedback: {e}")
            return False


class PatternLearningEngine(BaseLearningEngine):
    """Learns quality patterns from feedback"""
    
    def __init__(self):
        self.model = None
        self.feature_importance = {}
        self.quality_patterns = defaultdict(list)
        self.model_path = Path('outputs/quality_models/pattern_model.pkl')
    
    def learn(self, feedback_data: List[VideoFeedback]) -> Dict:
        """Learn patterns from feedback"""
        try:
            if not feedback_data:
                return {}
            
            # Extract features and labels
            features = []
            labels = []
            
            for feedback in feedback_data:
                # Extract feature vector
                feature_vector = self._extract_features(feedback)
                features.append(feature_vector)
                
                # Calculate overall quality label
                quality = np.mean(list(feedback.quality_metrics.values()))
                labels.append(quality)
            
            features = np.array(features)
            labels = np.array(labels)
            
            # Train simple model (could use sklearn in production)
            self._train_model(features, labels)
            
            # Identify patterns
            patterns = self._identify_patterns(feedback_data)
            
            # Calculate feature importance
            self.feature_importance = self._calculate_feature_importance(features, labels)
            
            return {
                'patterns_learned': len(patterns),
                'samples_processed': len(feedback_data),
                'average_quality': np.mean(labels),
                'feature_importance': self.feature_importance
            }
            
        except Exception as e:
            logger.error(f"❌ Learning failed: {e}")
            return {}
    
    def predict_quality(self, params: Dict) -> float:
        """Predict quality based on parameters"""
        try:
            if self.model is None:
                self._load_model()
            
            if self.model is None:
                return 0.5  # Default prediction
            
            # Extract features from params
            feature_vector = self._extract_features_from_params(params)
            
            # Make prediction
            prediction = self._predict_with_model(feature_vector)
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return 0.5
    
    def _extract_features(self, feedback: VideoFeedback) -> np.ndarray:
        """Extract feature vector from feedback"""
        features = []
        
        # Quality metrics features
        for metric in ['sharpness', 'brightness', 'contrast', 'clarity']:
            for prefix in ['visual_', 'audio_']:
                key = f'{prefix}{metric}'
                features.append(feedback.quality_metrics.get(key, 0))
        
        # Generation parameter features
        params = feedback.generation_params
        features.append(params.get('duration_seconds', 30) / 60)  # Normalize
        features.append(1 if params.get('platform') == 'youtube' else 0)
        features.append(1 if params.get('platform') == 'tiktok' else 0)
        
        # Engagement features (if available)
        features.append(feedback.engagement_metrics.get('views', 0) / 1000)  # Normalize
        features.append(feedback.engagement_metrics.get('likes', 0) / 100)
        
        return np.array(features)
    
    def _extract_features_from_params(self, params: Dict) -> np.ndarray:
        """Extract features from generation parameters"""
        features = []
        
        # Default quality metrics (will be refined by model)
        for _ in range(8):  # 8 quality metrics
            features.append(0.5)
        
        # Generation parameters
        features.append(params.get('duration_seconds', 30) / 60)
        features.append(1 if params.get('platform') == 'youtube' else 0)
        features.append(1 if params.get('platform') == 'tiktok' else 0)
        
        # Default engagement
        features.append(0)
        features.append(0)
        
        return np.array(features)
    
    def _train_model(self, features: np.ndarray, labels: np.ndarray):
        """Train quality prediction model"""
        try:
            # Simple linear regression (would use sklearn in production)
            # Calculate weights using least squares
            X = np.c_[np.ones(features.shape[0]), features]  # Add bias term
            weights = np.linalg.lstsq(X.T @ X, X.T @ labels, rcond=None)[0]
            
            self.model = {'weights': weights, 'type': 'linear'}
            
            # Save model
            self._save_model()
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    def _predict_with_model(self, features: np.ndarray) -> float:
        """Make prediction with trained model"""
        if self.model and self.model['type'] == 'linear':
            X = np.r_[1, features]  # Add bias term
            prediction = np.dot(X, self.model['weights'])
            return np.clip(prediction, 0, 1)
        return 0.5
    
    def _identify_patterns(self, feedback_data: List[VideoFeedback]) -> List[Dict]:
        """Identify quality patterns"""
        patterns = []
        
        # Group by platform
        platform_groups = defaultdict(list)
        for feedback in feedback_data:
            platform = feedback.generation_params.get('platform', 'unknown')
            quality = np.mean(list(feedback.quality_metrics.values()))
            platform_groups[platform].append(quality)
        
        # Identify platform patterns
        for platform, qualities in platform_groups.items():
            if qualities:
                avg_quality = np.mean(qualities)
                patterns.append({
                    'type': 'platform',
                    'platform': platform,
                    'average_quality': avg_quality,
                    'sample_size': len(qualities)
                })
        
        # Duration patterns
        duration_groups = defaultdict(list)
        for feedback in feedback_data:
            duration = feedback.generation_params.get('duration_seconds', 30)
            quality = np.mean(list(feedback.quality_metrics.values()))
            
            if duration < 30:
                duration_groups['short'].append(quality)
            elif duration < 60:
                duration_groups['medium'].append(quality)
            else:
                duration_groups['long'].append(quality)
        
        for duration_type, qualities in duration_groups.items():
            if qualities:
                patterns.append({
                    'type': 'duration',
                    'duration_type': duration_type,
                    'average_quality': np.mean(qualities)
                })
        
        self.quality_patterns['all'] = patterns
        return patterns
    
    def _calculate_feature_importance(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """Calculate feature importance"""
        importance = {}
        
        if self.model and 'weights' in self.model:
            weights = self.model['weights'][1:]  # Exclude bias
            
            feature_names = [
                'visual_sharpness', 'visual_brightness', 'visual_contrast', 'visual_clarity',
                'audio_sharpness', 'audio_brightness', 'audio_contrast', 'audio_clarity',
                'duration', 'is_youtube', 'is_tiktok', 'views', 'likes'
            ]
            
            for i, name in enumerate(feature_names[:len(weights)]):
                importance[name] = abs(weights[i])
        
        return importance
    
    def _save_model(self):
        """Save trained model"""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"💾 Model saved: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def _load_model(self):
        """Load trained model"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("📂 Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")


class TrendAnalyzer:
    """Analyzes quality trends over time"""
    
    def analyze_trends(self, feedback_history: List[VideoFeedback]) -> List[QualityTrend]:
        """Analyze quality trends"""
        if not feedback_history:
            return []
        
        # Sort by timestamp
        feedback_history.sort(key=lambda x: x.timestamp)
        
        # Group metrics by name
        metric_series = defaultdict(lambda: {'values': [], 'timestamps': []})
        
        for feedback in feedback_history:
            for metric_name, value in feedback.quality_metrics.items():
                metric_series[metric_name]['values'].append(value)
                metric_series[metric_name]['timestamps'].append(feedback.timestamp)
        
        # Analyze each metric
        trends = []
        for metric_name, data in metric_series.items():
            if len(data['values']) < 2:
                continue
            
            values = np.array(data['values'])
            
            # Calculate trend
            trend_direction = self._calculate_trend_direction(values)
            
            trend = QualityTrend(
                metric_name=metric_name,
                values=data['values'],
                timestamps=data['timestamps'],
                trend_direction=trend_direction,
                average=float(np.mean(values)),
                std_deviation=float(np.std(values))
            )
            
            trends.append(trend)
        
        return trends
    
    def _calculate_trend_direction(self, values: np.ndarray) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear regression for trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'declining'
        else:
            return 'stable'


# Main Quality Feedback System
class QualityFeedbackSystem:
    """Comprehensive quality feedback and learning system"""
    
    def __init__(self):
        """Initialize feedback system"""
        self.collector = AutomaticFeedbackCollector()
        self.learning_engine = PatternLearningEngine()
        self.trend_analyzer = TrendAnalyzer()
        self.feedback_history = []
        
        # Load existing feedback
        self._load_feedback_history()
        
        logger.info("✅ Quality Feedback System initialized")
    
    def analyze_output_quality(self, video_path: str, metadata: Dict) -> VideoFeedback:
        """
        Analyze quality of generated video
        
        Args:
            video_path: Path to video file
            metadata: Generation metadata
            
        Returns:
            VideoFeedback with quality analysis
        """
        logger.info(f"🔍 Analyzing output quality: {video_path}")
        
        # Collect feedback
        feedback = self.collector.collect(video_path, metadata)
        
        # Store feedback
        if self.collector.store(feedback):
            self.feedback_history.append(feedback)
        
        # Log quality summary
        avg_quality = np.mean(list(feedback.quality_metrics.values()))
        logger.info(f"📊 Quality score: {avg_quality:.2f}")
        
        return feedback
    
    def update_quality_models(self, min_samples: int = 10):
        """
        Update quality prediction models
        
        Args:
            min_samples: Minimum samples required for training
        """
        if len(self.feedback_history) < min_samples:
            logger.info(f"⏳ Not enough samples for training ({len(self.feedback_history)}/{min_samples})")
            return
        
        logger.info("🧠 Updating quality models...")
        
        # Learn from feedback
        learning_result = self.learning_engine.learn(self.feedback_history)
        
        if learning_result:
            logger.info(f"✅ Model updated: {learning_result}")
    
    def predict_quality(self, generation_params: Dict) -> float:
        """
        Predict quality for given parameters
        
        Args:
            generation_params: Video generation parameters
            
        Returns:
            Predicted quality score (0-1)
        """
        return self.learning_engine.predict_quality(generation_params)
    
    def generate_feedback_report(self) -> FeedbackReport:
        """Generate comprehensive feedback report"""
        if not self.feedback_history:
            return FeedbackReport(
                total_videos=0,
                average_quality=0,
                quality_trends=[],
                top_issues=[],
                insights=[],
                recommendations=[],
                improvement_rate=0
            )
        
        # Calculate average quality
        all_qualities = []
        for feedback in self.feedback_history:
            if feedback.quality_metrics:
                all_qualities.append(np.mean(list(feedback.quality_metrics.values())))
        
        avg_quality = np.mean(all_qualities) if all_qualities else 0
        
        # Analyze trends
        trends = self.trend_analyzer.analyze_trends(self.feedback_history)
        
        # Identify top issues
        issue_counts = defaultdict(int)
        for feedback in self.feedback_history:
            for issue in feedback.technical_issues:
                issue_counts[issue] += 1
        
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate insights
        insights = self._generate_insights(trends)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(avg_quality, trends, top_issues)
        
        # Calculate improvement rate
        if len(all_qualities) >= 2:
            recent_quality = np.mean(all_qualities[-5:])
            older_quality = np.mean(all_qualities[:5])
            improvement_rate = (recent_quality - older_quality) / older_quality if older_quality > 0 else 0
        else:
            improvement_rate = 0
        
        return FeedbackReport(
            total_videos=len(self.feedback_history),
            average_quality=avg_quality,
            quality_trends=trends,
            top_issues=top_issues,
            insights=insights,
            recommendations=recommendations,
            improvement_rate=improvement_rate
        )
    
    def _generate_insights(self, trends: List[QualityTrend]) -> List[LearningInsight]:
        """Generate insights from trends"""
        insights = []
        
        for trend in trends:
            if trend.trend_direction == 'improving':
                insights.append(LearningInsight(
                    insight_type='positive_trend',
                    description=f"{trend.metric_name} is improving over time",
                    confidence=0.8,
                    recommendations=[f"Continue current approach for {trend.metric_name}"],
                    affected_metrics=[trend.metric_name]
                ))
            elif trend.trend_direction == 'declining':
                insights.append(LearningInsight(
                    insight_type='negative_trend',
                    description=f"{trend.metric_name} is declining",
                    confidence=0.8,
                    recommendations=[f"Review and adjust {trend.metric_name} processing"],
                    affected_metrics=[trend.metric_name]
                ))
        
        # Feature importance insights
        if self.learning_engine.feature_importance:
            top_features = sorted(
                self.learning_engine.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            insights.append(LearningInsight(
                insight_type='feature_importance',
                description=f"Most important quality factors: {', '.join([f[0] for f in top_features])}",
                confidence=0.7,
                recommendations=["Focus optimization on high-impact features"],
                affected_metrics=[f[0] for f in top_features]
            ))
        
        return insights
    
    def _generate_recommendations(self, avg_quality: float, 
                                trends: List[QualityTrend],
                                top_issues: List[Tuple[str, int]]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Quality-based recommendations
        if avg_quality < 0.5:
            recommendations.append("Urgently review video generation pipeline")
            recommendations.append("Consider using higher quality presets")
        elif avg_quality < 0.7:
            recommendations.append("Enable multi-pass quality enhancement")
            recommendations.append("Apply professional effects and transitions")
        
        # Trend-based recommendations
        declining_metrics = [t.metric_name for t in trends if t.trend_direction == 'declining']
        if declining_metrics:
            recommendations.append(f"Address declining metrics: {', '.join(declining_metrics)}")
        
        # Issue-based recommendations
        if top_issues:
            recommendations.append(f"Fix recurring issue: {top_issues[0][0]}")
        
        # General recommendations
        if len(self.feedback_history) < 50:
            recommendations.append("Generate more videos to improve learning accuracy")
        
        return recommendations
    
    def _load_feedback_history(self):
        """Load existing feedback from storage"""
        try:
            feedback_dir = Path('outputs/quality_feedback')
            if feedback_dir.exists():
                for feedback_file in feedback_dir.glob('feedback_*.json'):
                    try:
                        with open(feedback_file, 'r') as f:
                            data = json.load(f)
                            # Convert back to VideoFeedback
                            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                            feedback = VideoFeedback(**data)
                            self.feedback_history.append(feedback)
                    except Exception as e:
                        logger.error(f"Failed to load feedback file {feedback_file}: {e}")
                
                logger.info(f"📂 Loaded {len(self.feedback_history)} feedback records")
        except Exception as e:
            logger.error(f"Failed to load feedback history: {e}")
    
    def export_analytics(self, output_path: str):
        """Export analytics data for external analysis"""
        try:
            analytics = {
                'feedback_count': len(self.feedback_history),
                'average_quality': float(np.mean([
                    np.mean(list(f.quality_metrics.values()))
                    for f in self.feedback_history
                    if f.quality_metrics
                ])),
                'quality_distribution': self._calculate_quality_distribution(),
                'platform_performance': self._analyze_platform_performance(),
                'temporal_analysis': self._analyze_temporal_patterns()
            }
            
            with open(output_path, 'w') as f:
                json.dump(analytics, f, indent=2)
            
            logger.info(f"📊 Analytics exported: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export analytics: {e}")
    
    def _calculate_quality_distribution(self) -> Dict[str, int]:
        """Calculate quality score distribution"""
        distribution = defaultdict(int)
        
        for feedback in self.feedback_history:
            if feedback.quality_metrics:
                avg_quality = np.mean(list(feedback.quality_metrics.values()))
                bucket = f"{int(avg_quality * 10) / 10:.1f}"
                distribution[bucket] += 1
        
        return dict(distribution)
    
    def _analyze_platform_performance(self) -> Dict[str, float]:
        """Analyze performance by platform"""
        platform_scores = defaultdict(list)
        
        for feedback in self.feedback_history:
            platform = feedback.platform or 'unknown'
            if feedback.quality_metrics:
                score = np.mean(list(feedback.quality_metrics.values()))
                platform_scores[platform].append(score)
        
        return {
            platform: float(np.mean(scores))
            for platform, scores in platform_scores.items()
        }
    
    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in quality"""
        if not self.feedback_history:
            return {}
        
        # Group by hour of day
        hourly_scores = defaultdict(list)
        
        for feedback in self.feedback_history:
            hour = feedback.timestamp.hour
            if feedback.quality_metrics:
                score = np.mean(list(feedback.quality_metrics.values()))
                hourly_scores[hour].append(score)
        
        return {
            'hourly_average': {
                str(hour): float(np.mean(scores))
                for hour, scores in hourly_scores.items()
            }
        }


# Global feedback system instance
quality_feedback_system = QualityFeedbackSystem()