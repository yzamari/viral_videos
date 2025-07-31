"""
Hashtag Generator - AI-powered trending hashtag suggestions
Generates platform-specific hashtags based on content analysis and REAL current trends
"""

import google.generativeai as genai
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re
import os
from ..utils.logging_config import get_logger
from ..config.ai_model_config import DEFAULT_AI_MODEL
from ..services.trending import UnifiedTrendingAnalyzer

logger = get_logger(__name__)

class HashtagGenerator:
    """AI-powered hashtag generator with REAL trend analysis from platform APIs"""

    def __init__(self, api_key: str):
        """Initialize the hashtag generator with real trending data"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(DEFAULT_AI_MODEL)
        
        # Initialize unified trending analyzer for REAL data
        self.trending_analyzer = UnifiedTrendingAnalyzer()
        
        logger.info("🏷️ HashtagGenerator initialized with REAL trending data")

    def generate_trending_hashtags(self, 
                                 mission: str, 
                                 platform: str, 
                                 category: str,
                                 script_content: str,
                                 num_hashtags: int = 30):
        """Generate trending hashtags based on topic, platform, and current trends"""
        
        logger.info(f"🏷️ Generating {num_hashtags} trending hashtags for: {mission}")
        logger.info(f"📱 Platform: {platform}, Category: {category}")
        
        try:
            # Get REAL trending hashtags from platform APIs
            real_trending_hashtags = self.trending_analyzer.get_trending_hashtags_unified(
                platform=platform,
                mission=mission,
                category=category,
                limit=num_hashtags + 10  # Get extra for filtering
            )
            
            # Format real trends for the prompt
            real_trends_text = self._format_real_trends_for_prompt(real_trending_hashtags, platform)
            trending_hashtags_text = ' '.join([h['tag'] for h in real_trending_hashtags[:10]])
            # Create comprehensive hashtag generation prompt
            hashtag_prompt = f"""
            You are a viral social media hashtag expert with access to current trends and platform-specific insights.
            
            CONTENT ANALYSIS:
            Topic: {mission}
            Platform: {platform}
            Category: {category}
            Script: {script_content[:200]}...
            
            TASK: Generate {num_hashtags} trending hashtags that will maximize reach and engagement.
            
            PLATFORM REQUIREMENTS:
            - TikTok: Trending, viral, challenge-based hashtags
            - Instagram: Aesthetic, lifestyle, discoverable hashtags
            - YouTube: Searchable, descriptive, SEO-optimized hashtags
            - Twitter: Trending topics, conversational hashtags
            
            HASHTAG CATEGORIES TO INCLUDE:
            1. PRIMARY (5-7 hashtags): Directly related to topic
            2. TRENDING (8-10 hashtags): Current viral trends and challenges
            3. NICHE (5-8 hashtags): Category-specific expert hashtags
            4. BROAD (5-8 hashtags): General reach and discovery hashtags
            5. ENGAGEMENT (3-5 hashtags): Call-to-action and community hashtags
            
            REAL CURRENT TRENDS TO CONSIDER:
            {real_trends}
            
            ACTUAL TRENDING HASHTAGS ON {platform}:
            {trending_hashtags}
            
            Return JSON with:
            {{
                "hashtags": [
                    {{
                        "tag": "#hashtag",
                        "category": "primary|trending|niche|broad|engagement",
                        "estimated_reach": "high|medium|low",
                        "reasoning": "Why this hashtag is effective",
                        "trend_score": 0.0-1.0
                    }}
                ],
                "strategy": {{
                    "total_hashtags": {num_hashtags},
                    "platform_optimization": "{platform}",
                    "trend_analysis": "Summary of current trends incorporated",
                    "engagement_strategy": "How hashtags drive engagement"
                }},
                "usage_tips": [
                    "Platform-specific usage guidelines"
                ]
            }}
            """.format(
                real_trends=real_trends_text,
                trending_hashtags=trending_hashtags_text,
                platform=platform
            )
            
            response = self.model.generate_content(hashtag_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL | re.MULTILINE)
            if json_match:
                try:
                    hashtag_data = json.loads(json_match.group())
                    
                    # Merge with real trending hashtags
                    hashtag_data = self._merge_with_real_trends(
                        hashtag_data, 
                        real_trending_hashtags,
                        num_hashtags
                    )
                    
                    # Validate and enhance hashtag data
                    validated_data = self._validate_hashtag_data(hashtag_data, num_hashtags)
                    
                    # Add metadata
                    validated_data['generation_metadata'] = {
                        'generated_at': datetime.now().isoformat(),
                        'topic': mission,
                        'platform': platform,
                        'category': category,
                        'model': 'gemini-2.5-flash',
                        'total_generated': len(validated_data.get('hashtags', []))
                    }
                    
                    logger.info(f"✅ Generated {len(validated_data.get('hashtags', []))} trending hashtags")
                    return validated_data
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Failed to parse hashtag JSON: {e}")
                    return self._generate_fallback_hashtags(mission, platform, category, num_hashtags)
            else:
                logger.warning("⚠️ No valid JSON found in hashtag response")
                return self._generate_fallback_hashtags(topic, platform, category, num_hashtags)
                
        except Exception as e:
            logger.error(f"❌ Hashtag generation failed: {e}")
            return self._generate_fallback_hashtags(topic, platform, category, num_hashtags)

    def _validate_hashtag_data(self, data: Dict[str, Any], expected_count: int) -> Dict[str, Any]:
        """Validate and enhance hashtag data"""
        try:
            hashtags = data.get('hashtags', [])
            
            # Ensure all hashtags start with #
            for hashtag in hashtags:
                if not hashtag.get('tag', '').startswith('#'):
                    hashtag['tag'] = '#' + hashtag.get('tag', '').lstrip('#')
            
            # Remove duplicates
            seen_tags = set()
            unique_hashtags = []
            for hashtag in hashtags:
                tag = hashtag.get('tag', '').lower()
                if tag not in seen_tags:
                    seen_tags.add(tag)
                    unique_hashtags.append(hashtag)
            
            data['hashtags'] = unique_hashtags[:expected_count]
            
            # Ensure strategy exists
            if 'strategy' not in data:
                data['strategy'] = {
                    'total_hashtags': len(data['hashtags']),
                    'platform_optimization': 'general',
                    'trend_analysis': 'Generated based on current trends',
                    'engagement_strategy': 'Optimized for maximum reach and engagement'
                }
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Hashtag validation failed: {e}")
            return data

    def _generate_fallback_hashtags(self, mission: str, platform: str, category: str, num_hashtags: int) -> Dict[str, Any]:
        """Generate fallback hashtags when AI generation fails"""
        
        logger.info("🏷️ Creating fallback trending hashtags")
        
        # Extract key words from mission
        mission_words = re.findall(r'\b\w+\b', mission.lower())
        main_keywords = [word for word in mission_words if len(word) > 3][:3]
        
        # Platform-specific base hashtags
        platform_hashtags = {
            'tiktok': ['#fyp', '#foryou', '#viral', '#trending', '#foryoupage', '#tiktok'],
            'instagram': ['#instagram', '#instagood', '#photooftheday', '#follow', '#reels', '#explore'],
            'youtube': ['#youtube', '#subscribe', '#viral', '#trending', '#youtubeshorts', '#content'],
            'twitter': ['#twitter', '#trending', '#viral', '#follow', '#retweet', '#news']
        }
        
        # Category-specific hashtags
        category_hashtags = {
            'technology': ['#tech', '#ai', '#innovation', '#future', '#digital', '#software'],
            'comedy': ['#funny', '#humor', '#comedy', '#laugh', '#entertainment', '#meme'],
            'educational': ['#education', '#learn', '#knowledge', '#tutorial', '#tips', '#facts'],
            'entertainment': ['#entertainment', '#fun', '#viral', '#trending', '#amazing', '#cool'],
            'news': ['#news', '#breaking', '#update', '#current', '#today', '#world']
        }
        
        # Generate fallback hashtags
        fallback_hashtags = []
        
        # Add topic-specific hashtags
        for keyword in main_keywords:
            fallback_hashtags.extend([
                {
                    'tag': f'#{keyword}',
                    'category': 'primary',
                    'estimated_reach': 'medium',
                    'reasoning': f'Direct keyword from topic: {keyword}',
                    'trend_score': 0.7
                },
                {
                    'tag': f'#{keyword}tips',
                    'category': 'niche',
                    'estimated_reach': 'medium',
                    'reasoning': f'Educational angle for {keyword}',
                    'trend_score': 0.6
                }
            ])
        
        # Add platform-specific hashtags
        platform_key = platform.lower()
        for tag in platform_hashtags.get(platform_key, platform_hashtags['instagram']):
            fallback_hashtags.append({
                'tag': tag,
                'category': 'trending',
                'estimated_reach': 'high',
                'reasoning': f'Platform-specific trending hashtag for {platform}',
                'trend_score': 0.9
            })
        
        # Add category-specific hashtags
        category_key = category.lower()
        for tag in category_hashtags.get(category_key, category_hashtags['entertainment']):
            fallback_hashtags.append({
                'tag': tag,
                'category': 'niche',
                'estimated_reach': 'medium',
                'reasoning': f'Category-specific hashtag for {category}',
                'trend_score': 0.8
            })
        
        # Add general engagement hashtags
        engagement_hashtags = ['#like', '#follow', '#share', '#comment', '#engage', '#viral']
        for tag in engagement_hashtags:
            fallback_hashtags.append({
                'tag': tag,
                'category': 'engagement',
                'estimated_reach': 'high',
                'reasoning': 'General engagement hashtag',
                'trend_score': 0.8
            })
        
        # Remove duplicates and limit to requested count
        seen_tags = set()
        unique_hashtags = []
        for hashtag in fallback_hashtags:
            tag = hashtag['tag'].lower()
            if tag not in seen_tags and len(unique_hashtags) < num_hashtags:
                seen_tags.add(tag)
                unique_hashtags.append(hashtag)
        
        return {
            'hashtags': unique_hashtags,
            'strategy': {
                'total_hashtags': len(unique_hashtags),
                'platform_optimization': platform,
                'trend_analysis': 'Fallback hashtags based on keyword analysis and platform trends',
                'engagement_strategy': 'Balanced approach with topic, platform, and engagement hashtags'
            },
            'usage_tips': [
                f'Use all hashtags in your {platform} post for maximum reach',
                'Mix primary topic hashtags with trending platform hashtags',
                'Monitor performance and adjust hashtag strategy accordingly'
            ],
            'generation_metadata': {
                'generated_at': datetime.now().isoformat(),
                'topic': mission,
                'platform': platform,
                'category': category,
                'model': 'fallback',
                'total_generated': len(unique_hashtags)
            }
        }

    def save_hashtags_to_session(self, hashtag_data: Dict[str, Any], session_context, filename: str = "trending_hashtags.json"):
        """Save generated hashtags to session directory"""
        try:
            hashtags_path = session_context.get_output_path("hashtags", filename)
            os.makedirs(os.path.dirname(hashtags_path), exist_ok=True)
            
            with open(hashtags_path, 'w', encoding='utf-8') as f:
                json.dump(hashtag_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📁 Hashtags saved to: {hashtags_path}")
            
            # Also create a simple text file for easy copying
            text_path = session_context.get_output_path("hashtags", "hashtags_text.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write("# Trending Hashtags\n\n")
                f.write(f"Generated for: {hashtag_data.get('generation_metadata', {}).get('mission', hashtag_data.get('generation_metadata', {}).get('topic', 'Unknown'))}\n")
                f.write(f"Platform: {hashtag_data.get('generation_metadata', {}).get('platform', 'Unknown')}\n")
                f.write(f"Generated at: {hashtag_data.get('generation_metadata', {}).get('generated_at', 'Unknown')}\n\n")
                
                # Group hashtags by category
                hashtags_by_category = {}
                for hashtag in hashtag_data.get('hashtags', []):
                    category = hashtag.get('category', 'other')
                    if category not in hashtags_by_category:
                        hashtags_by_category[category] = []
                    hashtags_by_category[category].append(hashtag)
                
                # Write hashtags by category
                for category, hashtags in hashtags_by_category.items():
                    f.write(f"\n## {category.upper()} HASHTAGS\n")
                    for hashtag in hashtags:
                        f.write(f"{hashtag.get('tag', '')} ")
                    f.write("\n")
                
                # Write all hashtags in one line for easy copying
                f.write("\n## ALL HASHTAGS (Copy-paste ready)\n")
                all_tags = [h.get('tag', '') for h in hashtag_data.get('hashtags', [])]
                f.write(' '.join(all_tags))
                f.write("\n")
            
            logger.info(f"📄 Hashtags text file saved to: {text_path}")
            return hashtags_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save hashtags: {e}")
            return None
    
    def _format_real_trends_for_prompt(self, hashtags: List[Dict], platform: str) -> str:
        """Format real trending hashtags for AI prompt"""
        trends_text = f"Based on REAL {platform} API data:\n"
        
        # Group by category
        by_category = {}
        for hashtag in hashtags[:20]:
            cat = hashtag.get('category', 'general')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(hashtag)
        
        # Format by category
        for category, tags in by_category.items():
            trends_text += f"\n{category.upper()} trends:\n"
            for tag in tags[:5]:
                score = tag.get('trend_score', 0.5)
                usage = tag.get('usage_count', 0)
                trends_text += f"- {tag['tag']} (score: {score:.2f}, usage: {usage:,})\n"
        
        return trends_text
    
    def _merge_with_real_trends(self, 
                               ai_data: Dict[str, Any], 
                               real_hashtags: List[Dict],
                               num_hashtags: int) -> Dict[str, Any]:
        """Merge AI suggestions with real trending hashtags"""
        
        # Get AI suggested hashtags
        ai_hashtags = ai_data.get('hashtags', [])
        
        # Create a map of real hashtags for quick lookup
        real_map = {h['tag'].lower(): h for h in real_hashtags}
        
        # Update AI hashtags with real data where available
        for ai_tag in ai_hashtags:
            tag_lower = ai_tag['tag'].lower()
            if tag_lower in real_map:
                # Merge real data
                real_data = real_map[tag_lower]
                ai_tag['trend_score'] = real_data.get('trend_score', ai_tag.get('trend_score', 0.5))
                ai_tag['usage_count'] = real_data.get('usage_count', 0)
                ai_tag['data_source'] = 'real_api'
        
        # Add top real trending hashtags that AI didn't suggest
        ai_tags_lower = {tag['tag'].lower() for tag in ai_hashtags}
        additional_real = []
        
        for real_tag in real_hashtags:
            if real_tag['tag'].lower() not in ai_tags_lower and len(additional_real) < 5:
                additional_real.append({
                    'tag': real_tag['tag'],
                    'category': 'trending',
                    'estimated_reach': 'high',
                    'reasoning': f"Currently trending on {real_tag.get('platform', 'platform')}",
                    'trend_score': real_tag.get('trend_score', 0.9),
                    'usage_count': real_tag.get('usage_count', 0),
                    'data_source': 'real_api'
                })
        
        # Combine hashtags
        all_hashtags = ai_hashtags + additional_real
        
        # Sort by trend score
        all_hashtags.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
        
        # Update the data
        ai_data['hashtags'] = all_hashtags[:num_hashtags]
        ai_data['real_trends_incorporated'] = True
        
        return ai_data