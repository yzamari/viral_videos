"""
Video analyzer using Google's Gemini API
"""
import google.generativeai as genai
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
import re
from collections import Counter

from ..models.video_models import TrendingVideo, VideoAnalysis, Platform
from ..utils.logging_config import get_logger
from ..scrapers.youtube_scraper import YouTubeScraper

logger = get_logger(__name__)

class VideoAnalyzer:
    """Analyze trending videos using Gemini AI"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.youtube_scraper = None  # Will be initialized if needed
        
    def analyze_video(self, video: TrendingVideo, fetch_comments: bool = True) -> VideoAnalysis:
        """
        Analyze a single video for viral factors
        
        Args:
            video: TrendingVideo object to analyze
            fetch_comments: Whether to fetch and analyze comments
            
        Returns:
            VideoAnalysis object with insights
        """
        try:
            # Calculate viral velocity
            # Make datetime timezone-aware for comparison
            upload_date = video.upload_date.replace(tzinfo=None) if video.upload_date.tzinfo else video.upload_date
            hours_since_upload = (datetime.now() - upload_date).total_seconds() / 3600
            viral_velocity = video.view_count / max(hours_since_upload, 1)
            
            # Calculate engagement rate
            total_engagements = video.like_count + video.comment_count
            engagement_rate = total_engagements / max(video.view_count, 1)
            
            # Fetch comments if requested
            comments_data = {}
            if fetch_comments and video.platform == Platform.YOUTUBE:
                comments_data = self._fetch_youtube_comments(video.video_id)
            
            # Prepare context for Gemini
            context = self._prepare_analysis_context(video, comments_data)
            
            # Get AI analysis
            ai_insights = self._get_ai_analysis(context)
            
            # Create VideoAnalysis object
            analysis = VideoAnalysis(
                video_id=video.video_id,
                platform=video.platform,
                content_themes=ai_insights.get('content_themes', []),
                emotional_tone=ai_insights.get('emotional_tone', 'neutral'),
                target_audience=ai_insights.get('target_audience', 'general'),
                key_moments=ai_insights.get('key_moments', []),
                viral_score=self._calculate_viral_score(video, viral_velocity, engagement_rate),
                viral_velocity=viral_velocity,
                engagement_rate=engagement_rate,
                title_keywords=self._extract_keywords(video.title),
                title_sentiment=ai_insights.get('title_sentiment', 'neutral'),
                hook_analysis=ai_insights.get('hook_analysis', ''),
                cta_present=self._detect_cta(video.title, video.description or ''),
                comment_themes=comments_data.get('themes', []),
                comment_sentiment=comments_data.get('sentiment', {}),
                top_comments=comments_data.get('top_comments', []),
                video_quality='high',  # Would need actual video analysis
                editing_style=ai_insights.get('editing_style', 'standard'),
                music_genre=ai_insights.get('music_genre'),
                speech_pace=ai_insights.get('speech_pace'),
                success_factors=ai_insights.get('success_factors', []),
                improvement_suggestions=ai_insights.get('improvement_suggestions', [])
            )
            
            logger.info(f"Successfully analyzed video {video.video_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video {video.video_id}: {e}")
            raise
            
    def _prepare_analysis_context(self, video: TrendingVideo, comments_data: Dict) -> str:
        """Prepare context string for AI analysis"""
        context = f"""
        Analyze this viral video:
        
        Title: {video.title}
        Description: {video.description[:500]}...
        
        Metrics:
        - Views: {video.view_count:,}
        - Likes: {video.like_count:,}
        - Comments: {video.comment_count:,}
        - Upload Date: {video.upload_date}
        - Duration: {video.duration_seconds} seconds
        - Category: {video.category}
        - Tags: {', '.join(video.tags[:10])}
        
                 Channel:
         - Name: {video.channel_name}
         - Subscribers: {f'{video.channel_subscribers:,}' if video.channel_subscribers else 'Unknown'}
         """
        
        if comments_data.get('top_comments'):
            context += "\n\nTop Comments:\n"
            for comment in comments_data['top_comments'][:5]:
                context += f"- {comment}\n"
                
        return context
        
    def _get_ai_analysis(self, context: str) -> Dict[str, Any]:
        """Get AI analysis using Gemini with robust JSON parsing"""
        prompt = f"""
        {context}
        
        Analyze this video and return your insights as a JSON object.
        
        REQUIREMENTS:
        1. Return ONLY valid JSON - no text before or after
        2. No markdown code blocks (```json)
        3. No explanations or commentary
        4. Use double quotes for all strings
        5. Ensure all arrays and objects are properly closed
        
        EXACT FORMAT REQUIRED:
        {{
            "content_themes": ["theme1", "theme2", "theme3"],
            "emotional_tone": "positive/negative/neutral/excited/calm",
            "target_audience": "brief description",
            "key_moments": [
                {{"timestamp": "0:00", "description": "opening hook"}},
                {{"timestamp": "0:05", "description": "main content"}}
            ],
            "title_sentiment": "positive/negative/neutral",
            "hook_analysis": "brief analysis of opening hook",
            "editing_style": "fast-paced/slow/standard/dynamic",
            "music_genre": "genre or null",
            "speech_pace": "fast/moderate/slow or null",
            "success_factors": ["factor1", "factor2", "factor3"],
            "improvement_suggestions": ["suggestion1", "suggestion2"]
        }}
        
        JSON Response:"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try multiple JSON extraction methods
            ai_insights = self._extract_json_safely(response_text)
            
            if ai_insights:
                return ai_insights
            else:
                logger.warning("Could not parse AI response as JSON, using fallback")
                return self._get_fallback_analysis()
                
        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            return self._get_fallback_analysis()
    
    def _extract_json_safely(self, text: str) -> Dict[str, Any]:
        """Safely extract JSON from AI response text with multiple fallback methods"""
        import re
        
        # Clean the text first
        text = text.strip()
        
        # Method 1: Try direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Method 2: Look for JSON after "JSON Response:" marker
        try:
            if "JSON Response:" in text:
                json_part = text.split("JSON Response:")[-1].strip()
                return json.loads(json_part)
        except json.JSONDecodeError:
            pass
        
        # Method 3: Extract JSON block with regex (most permissive)
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                return json.loads(json_text)
        except json.JSONDecodeError:
            pass
            
        # Method 4: Look for JSON between code blocks
        try:
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                return json.loads(json_text)
        except json.JSONDecodeError:
            pass
            
        # Method 5: Clean common formatting issues and retry
        try:
            if '{' in text and '}' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                json_candidate = text[start:end]
                
                # Fix common JSON issues
                json_candidate = re.sub(r',\s*}', '}', json_candidate)  # Remove trailing commas in objects
                json_candidate = re.sub(r',\s*]', ']', json_candidate)   # Remove trailing commas in arrays
                json_candidate = re.sub(r'([^"\\])\n', r'\1', json_candidate)  # Remove unescaped line breaks
                json_candidate = re.sub(r'\n\s*', ' ', json_candidate)  # Replace newlines with spaces
                json_candidate = re.sub(r'\s+', ' ', json_candidate)    # Normalize whitespace
                
                return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass
            
        # Method 6: Try to fix quotes and parse
        try:
            if '{' in text and '}' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                json_candidate = text[start:end]
                
                # Fix quote issues
                json_candidate = re.sub(r"'([^']*)':", r'"\1":', json_candidate)  # Fix single quotes in keys
                json_candidate = re.sub(r":\s*'([^']*)'", r': "\1"', json_candidate)  # Fix single quotes in values
                json_candidate = re.sub(r',\s*}', '}', json_candidate)  # Remove trailing commas
                json_candidate = re.sub(r',\s*]', ']', json_candidate)   # Remove trailing commas
                
                return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass
            
        logger.warning("All JSON extraction methods failed")
        logger.debug(f"Failed to parse text: {text[:200]}...")
        return {}
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Provide fallback analysis when AI parsing fails"""
        return {
            "content_themes": ["entertaining", "engaging"],
            "emotional_tone": "positive",
            "target_audience": "general audience",
            "key_moments": [{"timestamp": "0:00", "description": "video content"}],
            "title_sentiment": "positive",
            "hook_analysis": "engaging opening",
            "editing_style": "standard",
            "music_genre": None,
            "speech_pace": "moderate",
            "success_factors": ["engaging content", "good timing"],
            "improvement_suggestions": ["optimize for target audience"]
        }
        
    def _calculate_viral_score(self, video: TrendingVideo, viral_velocity: float, engagement_rate: float) -> float:
        """Calculate viral score (0-1) based on multiple factors"""
        score = 0.0
        
        # View velocity factor (40%)
        if viral_velocity > 10000:
            score += 0.4
        elif viral_velocity > 5000:
            score += 0.3
        elif viral_velocity > 1000:
            score += 0.2
        else:
            score += 0.1
            
        # Engagement rate factor (30%)
        if engagement_rate > 0.1:
            score += 0.3
        elif engagement_rate > 0.05:
            score += 0.2
        elif engagement_rate > 0.01:
            score += 0.1
        else:
            score += 0.05
            
        # Trending position factor (20%)
        if video.trending_position and video.trending_position <= 10:
            score += 0.2
        elif video.trending_position and video.trending_position <= 25:
            score += 0.15
        elif video.trending_position and video.trending_position <= 50:
            score += 0.1
        else:
            score += 0.05
            
        # Channel authority factor (10%)
        if video.channel_subscribers and video.channel_subscribers > 1000000:
            score += 0.1
        elif video.channel_subscribers and video.channel_subscribers > 100000:
            score += 0.07
        else:
            score += 0.03
            
        return min(score, 1.0)
        
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract keywords from title"""
        # Remove common words and extract significant terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', title.lower())
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        return keywords
        
    def _detect_cta(self, title: str, description: str) -> bool:
        """Detect if there's a call-to-action"""
        cta_patterns = [
            r'subscribe', r'like', r'comment', r'share', r'follow',
            r'click', r'watch', r'join', r'sign up', r'download'
        ]
        
        text = (title + ' ' + description).lower()
        for pattern in cta_patterns:
            if re.search(pattern, text):
                return True
        return False
        
    def _fetch_youtube_comments(self, video_id: str, max_comments: int = 100) -> Dict[str, Any]:
        """Fetch and analyze YouTube comments"""
        # This would use YouTube API to fetch comments
        # For now, returning placeholder data
        return {
            'themes': ['entertaining', 'funny', 'relatable'],
            'sentiment': {'positive': 0.7, 'negative': 0.1, 'neutral': 0.2},
            'top_comments': [
                "This is so relatable!",
                "Best video I've seen today",
                "Can't stop watching this"
            ]
        }
        
    def batch_analyze(self, videos: List[TrendingVideo], fetch_comments: bool = True) -> List[VideoAnalysis]:
        """Analyze multiple videos in batch"""
        analyses = []
        for video in videos:
            try:
                analysis = self.analyze_video(video, fetch_comments)
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze video {video.video_id}: {e}")
                continue
                
        return analyses
        
    def generate_insights_report(self, analyses: List[VideoAnalysis]) -> Dict[str, Any]:
        """Generate insights report from multiple video analyses"""
        if not analyses:
            return {}
            
        # Aggregate insights
        all_themes = []
        all_success_factors = []
        viral_scores = []
        engagement_rates = []
        
        for analysis in analyses:
            all_themes.extend(analysis.content_themes)
            all_success_factors.extend(analysis.success_factors)
            viral_scores.append(analysis.viral_score)
            engagement_rates.append(analysis.engagement_rate)
            
        # Count frequencies
        theme_counts = Counter(all_themes)
        factor_counts = Counter(all_success_factors)
        
        report = {
            'total_videos_analyzed': len(analyses),
            'average_viral_score': sum(viral_scores) / len(viral_scores),
            'average_engagement_rate': sum(engagement_rates) / len(engagement_rates),
            'top_themes': theme_counts.most_common(10),
            'top_success_factors': factor_counts.most_common(10),
            'insights': {
                'best_performing_category': self._get_best_category(analyses),
                'optimal_duration': self._get_optimal_duration(analyses),
                'common_hooks': self._get_common_hooks(analyses)
            }
        }
        
        return report
        
    def _get_best_category(self, analyses: List[VideoAnalysis]) -> str:
        """Determine best performing category"""
        # Would need access to original video data
        return "Entertainment"
        
    def _get_optimal_duration(self, analyses: List[VideoAnalysis]) -> str:
        """Determine optimal video duration"""
        # Would need access to original video data
        return "15-30 seconds"
        
    def _get_common_hooks(self, analyses: List[VideoAnalysis]) -> List[str]:
        """Extract common successful hooks"""
        hooks = [a.hook_analysis for a in analyses if a.hook_analysis]
        # Would need more sophisticated analysis
        return hooks[:5] 