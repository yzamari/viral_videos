#!/usr/bin/env python3
"""
AI Agents Discussion System for News Analysis
Multiple agents discuss and decide on duration, media selection, and presentation
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import random
from datetime import datetime


@dataclass
class NewsItem:
    """Represents a news item with multiple media sources"""
    title: str
    category: str
    sources: List[Dict]  # Multiple sources covering same story
    media_items: List[Dict]  # All available media (images/videos)
    importance_score: float = 0.0
    summary: str = ""
    recommended_duration: int = 5
    selected_media: List[Dict] = None
    agent_consensus: Dict = None


class NewsAgent:
    """Base class for news analysis agents"""
    
    def __init__(self, name: str, role: str, personality: str):
        self.name = name
        self.role = role
        self.personality = personality
    
    def analyze(self, news_item: NewsItem) -> Dict:
        """Analyze a news item and provide recommendations"""
        raise NotImplementedError
    
    def discuss(self, news_item: NewsItem, other_opinions: List[Dict]) -> Dict:
        """Respond to other agents' opinions"""
        raise NotImplementedError


class EditorInChief(NewsAgent):
    """Makes final decisions on importance and duration"""
    
    def __init__(self):
        super().__init__(
            "Sarah Chen",
            "Editor-in-Chief",
            "Experienced, balanced, focuses on newsworthiness and audience engagement"
        )
    
    def analyze(self, news_item: NewsItem) -> Dict:
        analysis = {
            "agent": self.name,
            "role": self.role,
            "importance": self._calculate_importance(news_item),
            "recommended_duration": self._recommend_duration(news_item),
            "reasoning": ""
        }
        
        # Analyze based on news value
        if news_item.category == "breaking_news":
            analysis["importance"] = 0.9
            analysis["recommended_duration"] = 10
            analysis["reasoning"] = "Breaking news requires extended coverage for full context"
        elif len(news_item.sources) > 5:
            analysis["importance"] = 0.8
            analysis["recommended_duration"] = 8
            analysis["reasoning"] = "Multiple sources indicate high news value"
        else:
            analysis["importance"] = 0.6
            analysis["recommended_duration"] = 5
            analysis["reasoning"] = "Standard news item, balanced coverage needed"
        
        return analysis
    
    def _calculate_importance(self, news_item: NewsItem) -> float:
        base_score = 0.5
        
        # More sources = more important
        source_bonus = min(len(news_item.sources) * 0.1, 0.3)
        
        # Category bonuses
        category_scores = {
            "breaking_news": 0.3,
            "politics": 0.2,
            "disaster": 0.25,
            "sports": 0.1,
            "entertainment": 0.05
        }
        category_bonus = category_scores.get(news_item.category, 0.1)
        
        return min(base_score + source_bonus + category_bonus, 1.0)
    
    def _recommend_duration(self, news_item: NewsItem) -> int:
        base_duration = 5
        
        # Adjust based on importance
        if news_item.importance_score > 0.8:
            return base_duration + 5
        elif news_item.importance_score > 0.6:
            return base_duration + 2
        
        return base_duration


class VisualDirector(NewsAgent):
    """Focuses on media selection and visual impact"""
    
    def __init__(self):
        super().__init__(
            "Marcus Rodriguez",
            "Visual Director",
            "Creative, visual storyteller, emphasizes compelling imagery"
        )
    
    def analyze(self, news_item: NewsItem) -> Dict:
        analysis = {
            "agent": self.name,
            "role": self.role,
            "media_recommendations": self._select_best_media(news_item),
            "visual_strategy": self._determine_visual_strategy(news_item),
            "recommended_duration": self._visual_duration(news_item),
            "reasoning": ""
        }
        
        # Analyze media quality and variety
        video_count = sum(1 for m in news_item.media_items if m.get('type') == 'video')
        image_count = sum(1 for m in news_item.media_items if m.get('type') == 'image')
        
        if video_count > 0:
            analysis["visual_strategy"] = "video-first"
            analysis["reasoning"] = f"Found {video_count} videos - dynamic content available"
            analysis["recommended_duration"] = 8
        elif image_count > 3:
            analysis["visual_strategy"] = "multi-image-sequence"
            analysis["reasoning"] = f"{image_count} images allow for visual storytelling"
            analysis["recommended_duration"] = 7
        else:
            analysis["visual_strategy"] = "single-image-focus"
            analysis["reasoning"] = "Limited visuals - focus on quality over quantity"
            analysis["recommended_duration"] = 4
        
        return analysis
    
    def _select_best_media(self, news_item: NewsItem) -> List[Dict]:
        """Select the best media items for the story"""
        selected = []
        
        # Prioritize videos
        videos = [m for m in news_item.media_items if m.get('type') == 'video']
        images = [m for m in news_item.media_items if m.get('type') == 'image']
        
        # Take best video if available
        if videos:
            # Sort by quality indicators (resolution, source reliability)
            videos.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            selected.append(videos[0])
        
        # Add complementary images
        if images:
            # Diversify sources
            seen_sources = set()
            for img in images:
                if img.get('source') not in seen_sources and len(selected) < 4:
                    selected.append(img)
                    seen_sources.add(img.get('source'))
        
        return selected
    
    def _determine_visual_strategy(self, news_item: NewsItem) -> str:
        if news_item.category in ["sports", "entertainment"]:
            return "dynamic-fast-cuts"
        elif news_item.category in ["politics", "finance"]:
            return "steady-professional"
        else:
            return "balanced-pacing"
    
    def _visual_duration(self, news_item: NewsItem) -> int:
        # Calculate based on media complexity
        media_count = len(news_item.media_items)
        if media_count > 5:
            return 8  # More time to show multiple angles
        elif media_count > 2:
            return 6
        else:
            return 4


class AudienceAnalyst(NewsAgent):
    """Focuses on audience engagement and comprehension"""
    
    def __init__(self):
        super().__init__(
            "Dr. Aisha Patel",
            "Audience Analyst",
            "Data-driven, user-focused, emphasizes clarity and engagement"
        )
    
    def analyze(self, news_item: NewsItem) -> Dict:
        analysis = {
            "agent": self.name,
            "role": self.role,
            "audience_appeal": self._calculate_audience_appeal(news_item),
            "complexity_score": self._assess_complexity(news_item),
            "recommended_duration": self._audience_based_duration(news_item),
            "summary_style": self._recommend_summary_style(news_item),
            "reasoning": ""
        }
        
        # Analyze for audience
        if news_item.category in ["sports", "entertainment"]:
            analysis["audience_appeal"] = 0.8
            analysis["summary_style"] = "conversational"
            analysis["reasoning"] = "High engagement topics benefit from casual tone"
        elif news_item.category in ["politics", "finance"]:
            analysis["audience_appeal"] = 0.6
            analysis["summary_style"] = "informative"
            analysis["reasoning"] = "Complex topics need clear, structured presentation"
        else:
            analysis["audience_appeal"] = 0.7
            analysis["summary_style"] = "balanced"
            analysis["reasoning"] = "General news should be accessible yet informative"
        
        return analysis
    
    def _calculate_audience_appeal(self, news_item: NewsItem) -> float:
        # Categories that typically have high engagement
        high_appeal_categories = ["sports", "entertainment", "technology", "breaking_news"]
        
        if news_item.category in high_appeal_categories:
            return 0.8
        
        # Check for trending indicators
        if any(word in news_item.title.lower() for word in ["viral", "trending", "shocked"]):
            return 0.85
        
        return 0.6
    
    def _assess_complexity(self, news_item: NewsItem) -> float:
        # Simple word count analysis
        word_count = len(news_item.title.split())
        
        # Technical terms increase complexity
        technical_categories = ["finance", "technology", "science", "politics"]
        
        if news_item.category in technical_categories:
            return 0.7
        
        return 0.4
    
    def _audience_based_duration(self, news_item: NewsItem) -> int:
        complexity = self._assess_complexity(news_item)
        appeal = self._calculate_audience_appeal(news_item)
        
        # High complexity needs more time
        if complexity > 0.7:
            base_duration = 8
        else:
            base_duration = 5
        
        # High appeal can sustain longer duration
        if appeal > 0.8:
            base_duration += 2
        
        return base_duration
    
    def _recommend_summary_style(self, news_item: NewsItem) -> str:
        if news_item.category == "breaking_news":
            return "urgent-factual"
        elif news_item.category in ["sports", "entertainment"]:
            return "engaging-narrative"
        else:
            return "clear-informative"


class PacingSpecialist(NewsAgent):
    """Focuses on flow and rhythm of the news compilation"""
    
    def __init__(self):
        super().__init__(
            "James Thompson",
            "Pacing Specialist",
            "Rhythmic, flow-conscious, ensures smooth transitions"
        )
    
    def analyze(self, news_item: NewsItem) -> Dict:
        analysis = {
            "agent": self.name,
            "role": self.role,
            "pacing_recommendation": self._recommend_pacing(news_item),
            "transition_style": self._suggest_transition(news_item),
            "recommended_duration": self._pacing_based_duration(news_item),
            "position_preference": self._suggest_position(news_item),
            "reasoning": ""
        }
        
        # Analyze pacing needs
        if news_item.category == "breaking_news":
            analysis["pacing_recommendation"] = "immediate-attention"
            analysis["transition_style"] = "hard-cut"
            analysis["position_preference"] = "opener"
            analysis["reasoning"] = "Breaking news should grab attention immediately"
        elif news_item.category in ["sports", "entertainment"]:
            analysis["pacing_recommendation"] = "energetic"
            analysis["transition_style"] = "dynamic"
            analysis["position_preference"] = "middle"
            analysis["reasoning"] = "High-energy content maintains momentum"
        else:
            analysis["pacing_recommendation"] = "steady"
            analysis["transition_style"] = "smooth"
            analysis["position_preference"] = "flexible"
            analysis["reasoning"] = "Standard pacing for general news"
        
        return analysis
    
    def _recommend_pacing(self, news_item: NewsItem) -> str:
        pacing_map = {
            "breaking_news": "urgent",
            "sports": "fast",
            "entertainment": "upbeat",
            "politics": "measured",
            "finance": "steady",
            "weather": "calm"
        }
        
        return pacing_map.get(news_item.category, "moderate")
    
    def _suggest_transition(self, news_item: NewsItem) -> str:
        if news_item.importance_score > 0.8:
            return "dramatic-pause"
        elif news_item.category in ["sports", "entertainment"]:
            return "quick-cut"
        else:
            return "standard-fade"
    
    def _pacing_based_duration(self, news_item: NewsItem) -> int:
        pacing = self._recommend_pacing(news_item)
        
        duration_map = {
            "urgent": 8,
            "fast": 4,
            "upbeat": 5,
            "measured": 7,
            "steady": 6,
            "calm": 6,
            "moderate": 5
        }
        
        return duration_map.get(pacing, 5)
    
    def _suggest_position(self, news_item: NewsItem) -> str:
        if news_item.importance_score > 0.8:
            return "lead"
        elif news_item.category in ["sports", "entertainment"]:
            return "mid-section"
        else:
            return "flexible"


class ContentStrategist(NewsAgent):
    """Focuses on narrative and information architecture"""
    
    def __init__(self):
        super().__init__(
            "Elena Volkov",
            "Content Strategist", 
            "Strategic, narrative-focused, ensures comprehensive coverage"
        )
    
    def analyze(self, news_item: NewsItem) -> Dict:
        analysis = {
            "agent": self.name,
            "role": self.role,
            "narrative_approach": self._determine_narrative(news_item),
            "key_points": self._extract_key_points(news_item),
            "recommended_duration": self._content_based_duration(news_item),
            "multi_source_strategy": self._multi_source_approach(news_item),
            "reasoning": ""
        }
        
        # Analyze content depth
        source_count = len(news_item.sources)
        
        if source_count > 5:
            analysis["narrative_approach"] = "comprehensive-coverage"
            analysis["multi_source_strategy"] = "show-multiple-perspectives"
            analysis["reasoning"] = f"{source_count} sources provide rich, multi-angle coverage"
            analysis["recommended_duration"] = 10
        elif source_count > 2:
            analysis["narrative_approach"] = "balanced-reporting"
            analysis["multi_source_strategy"] = "highlight-consensus"
            analysis["reasoning"] = "Multiple sources allow for verified, balanced reporting"
            analysis["recommended_duration"] = 7
        else:
            analysis["narrative_approach"] = "focused-story"
            analysis["multi_source_strategy"] = "deep-dive-single-source"
            analysis["reasoning"] = "Limited sources require focused, in-depth coverage"
            analysis["recommended_duration"] = 5
        
        return analysis
    
    def _determine_narrative(self, news_item: NewsItem) -> str:
        if news_item.category == "breaking_news":
            return "developing-story"
        elif len(news_item.sources) > 3:
            return "multi-perspective"
        else:
            return "single-narrative"
    
    def _extract_key_points(self, news_item: NewsItem) -> List[str]:
        # Extract main points from title and sources
        key_points = []
        
        # Main point from title
        key_points.append(news_item.title)
        
        # Additional points from sources
        for source in news_item.sources[:3]:
            if source.get('headline') and source['headline'] != news_item.title:
                key_points.append(source['headline'])
        
        return key_points
    
    def _content_based_duration(self, news_item: NewsItem) -> int:
        key_points = self._extract_key_points(news_item)
        
        # More key points need more time
        base_duration = 4
        additional_time = len(key_points) * 1.5
        
        return int(min(base_duration + additional_time, 12))
    
    def _multi_source_approach(self, news_item: NewsItem) -> str:
        source_count = len(news_item.sources)
        
        if source_count > 5:
            return "montage-style"
        elif source_count > 2:
            return "comparison-style"
        else:
            return "single-focus"


class NewsDiscussionModerator:
    """Moderates discussions between agents and builds consensus"""
    
    def __init__(self):
        self.agents = [
            EditorInChief(),
            VisualDirector(),
            AudienceAnalyst(),
            PacingSpecialist(),
            ContentStrategist()
        ]
    
    def conduct_discussion(self, news_item: NewsItem) -> Dict:
        """Conduct a full discussion about a news item"""
        
        print(f"\n🎭 AGENT DISCUSSION: {news_item.title[:50]}...")
        print("=" * 70)
        
        # Round 1: Initial analysis
        analyses = []
        for agent in self.agents:
            analysis = agent.analyze(news_item)
            analyses.append(analysis)
            print(f"\n👤 {agent.name} ({agent.role}):")
            print(f"   {analysis.get('reasoning', 'No reasoning provided')}")
            if 'recommended_duration' in analysis:
                print(f"   Recommended duration: {analysis['recommended_duration']}s")
        
        # Calculate consensus
        consensus = self._build_consensus(news_item, analyses)
        
        # Round 2: Response to consensus
        print(f"\n🤝 CONSENSUS REACHED:")
        print(f"   Duration: {consensus['final_duration']}s")
        print(f"   Media strategy: {consensus['media_strategy']}")
        print(f"   Summary: {consensus['summary']}")
        
        return consensus
    
    def _build_consensus(self, news_item: NewsItem, analyses: List[Dict]) -> Dict:
        """Build consensus from all agent analyses"""
        
        # Collect all duration recommendations
        durations = [a.get('recommended_duration', 5) for a in analyses]
        
        # Weight editor's opinion more heavily
        editor_duration = analyses[0].get('recommended_duration', 5)
        weighted_duration = (sum(durations) + editor_duration * 2) / (len(durations) + 2)
        
        # Round to nearest second
        final_duration = int(round(weighted_duration))
        
        # Determine media strategy
        visual_analysis = next((a for a in analyses if a.get('role') == 'Visual Director'), {})
        media_recommendations = visual_analysis.get('media_recommendations', [])
        
        # Create summary based on content strategist and audience analyst
        content_analysis = next((a for a in analyses if a.get('role') == 'Content Strategist'), {})
        audience_analysis = next((a for a in analyses if a.get('role') == 'Audience Analyst'), {})
        
        summary = self._create_summary(
            news_item,
            content_analysis.get('key_points', []),
            audience_analysis.get('summary_style', 'balanced')
        )
        
        # Select best media items
        selected_media = self._select_final_media(
            news_item.media_items,
            media_recommendations,
            final_duration
        )
        
        consensus = {
            'final_duration': final_duration,
            'media_strategy': visual_analysis.get('visual_strategy', 'balanced'),
            'selected_media': selected_media,
            'summary': summary,
            'importance_score': self._calculate_final_importance(analyses),
            'pacing': next((a.get('pacing_recommendation') for a in analyses 
                          if a.get('role') == 'Pacing Specialist'), 'moderate'),
            'agent_analyses': analyses
        }
        
        return consensus
    
    def _create_summary(self, news_item: NewsItem, key_points: List[str], style: str) -> str:
        """Create a summary based on the agreed style"""
        
        if style == "urgent-factual":
            summary = f"BREAKING: {news_item.title}. "
            if key_points:
                summary += f"Key developments: {'; '.join(key_points[:2])}"
        
        elif style == "engaging-narrative":
            summary = f"{news_item.title}! "
            if len(news_item.sources) > 1:
                summary += f"Multiple sources confirm this exciting development. "
        
        elif style == "informative":
            summary = f"{news_item.title}. "
            if key_points:
                summary += f"Important points: {', '.join(key_points[:3])}"
        
        else:  # balanced
            summary = news_item.title
            if len(news_item.sources) > 2:
                summary += f" (Confirmed by {len(news_item.sources)} sources)"
        
        return summary[:200]  # Limit length
    
    def _select_final_media(self, all_media: List[Dict], 
                          recommendations: List[Dict], 
                          duration: int) -> List[Dict]:
        """Select final media items based on duration and recommendations"""
        
        # Use recommendations if available
        if recommendations:
            selected = recommendations
        else:
            selected = all_media
        
        # Determine how many media items to show based on duration
        if duration >= 10:
            max_items = 4  # Show multiple angles
        elif duration >= 7:
            max_items = 3
        elif duration >= 5:
            max_items = 2
        else:
            max_items = 1
        
        # Prioritize videos, then images from different sources
        videos = [m for m in selected if m.get('type') == 'video']
        images = [m for m in selected if m.get('type') == 'image']
        
        final_selection = []
        
        # Add best video first
        if videos:
            final_selection.append(videos[0])
        
        # Add images from different sources
        seen_sources = set()
        for img in images:
            if len(final_selection) < max_items:
                source = img.get('source', '')
                if source not in seen_sources:
                    final_selection.append(img)
                    seen_sources.add(source)
        
        # Fill remaining slots
        for media in selected:
            if media not in final_selection and len(final_selection) < max_items:
                final_selection.append(media)
        
        return final_selection
    
    def _calculate_final_importance(self, analyses: List[Dict]) -> float:
        """Calculate final importance score from all agents"""
        
        importance_scores = []
        
        for analysis in analyses:
            if 'importance' in analysis:
                importance_scores.append(analysis['importance'])
            elif 'audience_appeal' in analysis:
                importance_scores.append(analysis['audience_appeal'])
        
        if importance_scores:
            return sum(importance_scores) / len(importance_scores)
        
        return 0.5


def test_agent_discussion():
    """Test the agent discussion system"""
    
    # Create test news items
    test_items = [
        NewsItem(
            title="Major Earthquake Strikes California - Thousands Evacuated",
            category="breaking_news",
            sources=[
                {"name": "CNN", "headline": "7.2 Earthquake Hits Southern California"},
                {"name": "BBC", "headline": "California Earthquake: Thousands Flee Homes"},
                {"name": "Reuters", "headline": "Major Quake Rocks California Coast"},
                {"name": "AP", "headline": "Breaking: California Earthquake Causes Widespread Damage"},
                {"name": "NBC", "headline": "Live Updates: California Earthquake Emergency"}
            ],
            media_items=[
                {"type": "video", "source": "CNN", "url": "cnn_video.mp4", "quality_score": 0.9},
                {"type": "image", "source": "Reuters", "url": "damage1.jpg", "quality_score": 0.8},
                {"type": "image", "source": "AP", "url": "evacuation.jpg", "quality_score": 0.85},
                {"type": "image", "source": "BBC", "url": "aerial_view.jpg", "quality_score": 0.7},
                {"type": "video", "source": "NBC", "url": "live_report.mp4", "quality_score": 0.85}
            ]
        ),
        NewsItem(
            title="Lakers Win Championship in Overtime Thriller",
            category="sports",
            sources=[
                {"name": "ESPN", "headline": "Lakers Crown Champions After OT Victory"},
                {"name": "Sports Illustrated", "headline": "LeBron Leads Lakers to Title"}
            ],
            media_items=[
                {"type": "video", "source": "ESPN", "url": "highlights.mp4", "quality_score": 0.95},
                {"type": "image", "source": "SI", "url": "celebration.jpg", "quality_score": 0.8}
            ]
        ),
        NewsItem(
            title="Tech Giant Announces Revolutionary AI Assistant",
            category="technology",
            sources=[
                {"name": "TechCrunch", "headline": "Apple Unveils Next-Gen AI"},
                {"name": "The Verge", "headline": "Apple's AI Changes Everything"},
                {"name": "Wired", "headline": "Inside Apple's AI Revolution"}
            ],
            media_items=[
                {"type": "image", "source": "TechCrunch", "url": "ai_demo.jpg", "quality_score": 0.7},
                {"type": "image", "source": "Verge", "url": "presentation.jpg", "quality_score": 0.75},
                {"type": "video", "source": "Apple", "url": "keynote.mp4", "quality_score": 0.9}
            ]
        )
    ]
    
    # Create moderator and run discussions
    moderator = NewsDiscussionModerator()
    
    all_consensus = []
    for item in test_items:
        consensus = moderator.conduct_discussion(item)
        item.recommended_duration = consensus['final_duration']
        item.selected_media = consensus['selected_media']
        item.summary = consensus['summary']
        item.agent_consensus = consensus
        all_consensus.append(consensus)
    
    # Summary report
    print("\n\n📊 FINAL EDITORIAL DECISIONS")
    print("=" * 70)
    
    total_duration = 0
    for i, (item, consensus) in enumerate(zip(test_items, all_consensus)):
        print(f"\n{i+1}. {item.title}")
        print(f"   Duration: {consensus['final_duration']}s")
        print(f"   Media: {len(consensus['selected_media'])} items selected")
        print(f"   Summary: {consensus['summary'][:100]}...")
        print(f"   Importance: {consensus['importance_score']:.2f}")
        print(f"   Pacing: {consensus['pacing']}")
        total_duration += consensus['final_duration']
    
    print(f"\n📺 Total Duration: {total_duration} seconds")
    
    # Save decisions
    with open("agent_decisions.json", "w") as f:
        decisions = []
        for item, consensus in zip(test_items, all_consensus):
            decisions.append({
                "title": item.title,
                "category": item.category,
                "duration": consensus['final_duration'],
                "media_count": len(consensus['selected_media']),
                "summary": consensus['summary'],
                "importance": consensus['importance_score'],
                "pacing": consensus['pacing']
            })
        json.dump(decisions, f, indent=2)
    
    print("\n💾 Saved agent decisions to: agent_decisions.json")


if __name__ == "__main__":
    test_agent_discussion()