"""
Director AI for script writing and creative content generation
"""
import google.generativeai as genai
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict
import requests

from ..models.video_models import (
    VideoAnalysis, Platform, VideoCategory, 
    GeneratedVideoConfig
)
from ..utils.logging_config import get_logger
from ..utils.exceptions import (
    GenerationFailedError, APIException, 
    ContentPolicyViolation, NetworkError
)
from ..scrapers.news_scraper import HotNewsScaper

logger = get_logger(__name__)

class Director:
    """
    AI-powered director for script writing and content creation
    
    Responsibilities:
    - Analyze trending patterns and create engaging scripts
    - Adapt content to different platforms
    - Incorporate current news and events
    - Optimize scripts for maximum virality
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize Director with AI model"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.news_scraper = HotNewsScaper()
        self.hook_templates = self._load_hook_templates()
        self.content_structures = self._load_content_structures()
        
        logger.info(f"Director initialized with model: {model_name}")
        
    def write_script(self, 
                    topic: str, 
                    style: str, 
                    duration: int,
                    platform: Platform,
                    category: VideoCategory,
                    patterns: Dict[str, Any],
                    incorporate_news: bool = True) -> Dict[str, Any]:
        """
        Write a complete video script
        
        Args:
            topic: Main topic for the video
            style: Visual/narrative style
            duration: Video duration in seconds
            platform: Target platform
            category: Content category
            patterns: Successful patterns from analysis
            incorporate_news: Whether to include current events
            
        Returns:
            Dictionary containing script elements
        """
        try:
            logger.info(f"Writing script for {topic} ({duration}s) on {platform.value}")
            
            # Fetch relevant news if requested
            news_context = ""
            if incorporate_news:
                news_items = self._fetch_relevant_news(topic, category)
                if news_items:
                    news_context = self._format_news_context(news_items)
                    logger.info(f"Incorporated {len(news_items)} news items")
            
            # Generate script components
            hook = self._generate_hook(topic, style, patterns.get('hooks', []))
            main_content = self._structure_content(
                topic, duration, patterns, news_context
            )
            cta = self._create_cta(platform, category)
            
            # Assemble complete script
            script = self._assemble_script(
                hook, main_content, cta, duration, platform
            )
            
            # Optimize for virality
            optimized_script = self.optimize_for_virality(script, patterns)
            
            # Validate content policy
            self._validate_content_policy(optimized_script, platform)
            
            logger.info("Script generation completed successfully")
            
            # Log script details for debugging
            if isinstance(optimized_script, dict):
                script_text = json.dumps(optimized_script, indent=2)
            else:
                script_text = str(optimized_script)
                
            logger.info(f"📝 Generated script preview:")
            logger.info(f"   Length: {len(script_text)} characters")
            logger.info(f"   First 300 chars: {script_text[:300]}...")
            
            # Log any voiceover content found
            if isinstance(optimized_script, dict):
                # Check for voiceover in segments
                segments = optimized_script.get('segments', [])
                voiceover_count = 0
                for segment in segments:
                    if 'text' in segment and segment['text']:
                        voiceover_count += 1
                        logger.info(f"   Segment {voiceover_count} text: {segment['text'][:100]}...")
            else:
                # Check for voiceover markers in text
                voiceover_lines = [line for line in script_text.split('\n') if '**VOICEOVER:**' in line or 'voiceover' in line.lower()]
                if voiceover_lines:
                    logger.info(f"🎤 Found {len(voiceover_lines)} voiceover lines:")
                    for i, line in enumerate(voiceover_lines[:3]):  # Show first 3
                        logger.info(f"   VO {i+1}: {line.strip()[:100]}...")
            
            return optimized_script
            
        except Exception as e:
            logger.error(f"Script writing failed: {str(e)}")
            raise GenerationFailedError("script_writing", str(e))
            
    def _generate_hook(self, topic: str, style: str, 
                      successful_hooks: List[str]) -> Dict[str, str]:
        """Generate attention-grabbing hook"""
        try:
            # Analyze successful hooks for patterns
            hook_analysis = self._analyze_hook_patterns(successful_hooks)
            
            prompt = f"""
            Create an attention-grabbing hook for a video about: {topic}
            Style: {style}
            
            Successful hook patterns:
            {json.dumps(hook_analysis, indent=2)}
            
            Create a hook that:
            1. Grabs attention in the first 3 seconds
            2. Creates curiosity or emotional response
            3. Promises value or entertainment
            4. Uses pattern that works for this topic
            
            Return JSON:
            {{
                "text": "hook text",
                "type": "question/shock/promise/story",
                "visual_cue": "what should be shown",
                "duration_seconds": 3
            }}
            """
            
            response = self.model.generate_content(prompt)
            hook_data = self._extract_json(response.text)
            
            # Fallback to template if AI fails
            if not hook_data:
                hook_data = self._get_template_hook(topic, style)
                
            return hook_data
            
        except Exception as e:
            logger.warning(f"Hook generation failed, using fallback: {e}")
            return self._get_template_hook(topic, style)
            
    def _structure_content(self, topic: str, duration: int, 
                         patterns: Dict, news_context: str) -> List[Dict[str, Any]]:
        """Structure main content based on duration and patterns"""
        try:
            # Calculate content segments
            num_segments = self._calculate_segments(duration)
            
            prompt = f"""
            Create {num_segments} content segments for a {duration}-second video about: {topic}
            
            Successful content patterns:
            - Themes: {patterns.get('themes', [])}
            - Pacing: Fast cuts every 3-5 seconds
            - Engagement triggers: {patterns.get('success_factors', [])}
            
            {news_context}
            
            Each segment should:
            1. Deliver value or entertainment
            2. Build on previous segment
            3. Maintain viewer attention
            4. Include visual variety
            
            Return JSON array:
            [
                {{
                    "text": "segment narration",
                    "visual": "what to show",
                    "duration": seconds,
                    "transition": "cut/fade/zoom"
                }}
            ]
            """
            
            response = self.model.generate_content(prompt)
            segments = self._extract_json(response.text)
            
            if not segments or not isinstance(segments, list):
                segments = self._get_default_segments(topic, num_segments)
                
            return segments
            
        except Exception as e:
            logger.warning(f"Content structuring failed, using defaults: {e}")
            return self._get_default_segments(topic, self._calculate_segments(duration))
            
    def _create_cta(self, platform: Platform, category: VideoCategory) -> Dict[str, str]:
        """Create platform-optimized call-to-action"""
        cta_templates = {
            Platform.YOUTUBE: {
                "text": "Subscribe for more {category} content!",
                "visual": "Subscribe button animation",
                "action": "subscribe"
            },
            Platform.TIKTOK: {
                "text": "Follow for part 2! 👀",
                "visual": "Follow button highlight",
                "action": "follow"
            },
            Platform.INSTAGRAM: {
                "text": "Save this for later! ❤️",
                "visual": "Heart animation",
                "action": "save"
            },
            Platform.FACEBOOK: {
                "text": "Share if you found this helpful!",
                "visual": "Share button",
                "action": "share"
            }
        }
        
        cta = cta_templates.get(platform, cta_templates[Platform.YOUTUBE])
        cta['text'] = cta['text'].format(category=category.value.lower())
        
        return cta
        
    def adapt_to_platform(self, script: Dict[str, Any], 
                         target_platform: Platform) -> Dict[str, Any]:
        """Adapt script to platform-specific requirements"""
        try:
            logger.info(f"Adapting script for {target_platform.value}")
            
            platform_specs = {
                Platform.YOUTUBE: {
                    "max_duration": 60,
                    "aspect_ratio": "9:16",
                    "features": ["captions", "chapters", "cards"]
                },
                Platform.TIKTOK: {
                    "max_duration": 60,
                    "aspect_ratio": "9:16", 
                    "features": ["sounds", "effects", "duet"]
                },
                Platform.INSTAGRAM: {
                    "max_duration": 90,
                    "aspect_ratio": "9:16",
                    "features": ["music", "stickers", "polls"]
                },
                Platform.FACEBOOK: {
                    "max_duration": 240,
                    "aspect_ratio": "16:9",
                    "features": ["captions", "thumbnails"]
                }
            }
            
            spec = platform_specs[target_platform]
            
            # Adjust duration if needed
            if script['duration'] > spec['max_duration']:
                script = self._trim_script(script, spec['max_duration'])
                
            # Add platform-specific elements
            script['platform_features'] = spec['features']
            script['aspect_ratio'] = spec['aspect_ratio']
            
            # Optimize text for platform
            script = self._optimize_text_for_platform(script, target_platform)
            
            return script
            
        except Exception as e:
            logger.error(f"Platform adaptation failed: {e}")
            return script  # Return original if adaptation fails
            
    def incorporate_news(self, script: Dict[str, Any], 
                        news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Incorporate current news into script"""
        try:
            if not news_items:
                return script
                
            logger.info(f"Incorporating {len(news_items)} news items into script")
            
            # Find relevant insertion points
            segments = script.get('segments', [])
            
            for i, segment in enumerate(segments):
                # Check if segment could incorporate news
                if self._can_incorporate_news(segment, news_items):
                    relevant_news = self._find_relevant_news(segment, news_items)
                    if relevant_news:
                        segment['news_context'] = relevant_news
                        segment['text'] = self._blend_news_into_text(
                            segment['text'], relevant_news
                        )
                        
            script['has_news'] = True
            script['news_items'] = news_items
            
            return script
            
        except Exception as e:
            logger.warning(f"News incorporation failed: {e}")
            return script
            
    def optimize_for_virality(self, script: Dict[str, Any], 
                            patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize script elements for maximum viral potential"""
        try:
            logger.info("Optimizing script for virality")
            
            # Analyze successful patterns
            viral_elements = {
                'emotional_triggers': patterns.get('emotional_tones', []),
                'engagement_hooks': patterns.get('success_factors', []),
                'optimal_pacing': patterns.get('pacing', 'fast')
            }
            
            # Enhance hook
            if 'hook' in script:
                script['hook'] = self._enhance_hook_virality(
                    script['hook'], viral_elements
                )
                
            # Optimize pacing
            script['segments'] = self._optimize_segment_pacing(
                script.get('segments', []), viral_elements['optimal_pacing']
            )
            
            # Add viral elements
            script['viral_elements'] = {
                'shareability_score': self._calculate_shareability(script),
                'emotional_arc': self._analyze_emotional_arc(script),
                'surprise_moments': self._identify_surprise_moments(script)
            }
            
            return script
            
        except Exception as e:
            logger.warning(f"Virality optimization failed: {e}")
            return script
            
    def _fetch_relevant_news(self, topic: str, 
                           category: VideoCategory) -> List[Dict[str, Any]]:
        """Fetch news relevant to topic and category"""
        try:
            # Search for news related to topic
            news_items = self.news_scraper.search_news(
                query=topic,
                category=category.value.lower(),
                max_results=5
            )
            
            # Filter by relevance and recency
            relevant_news = []
            for item in news_items:
                relevance_score = self._calculate_news_relevance(item, topic)
                if relevance_score > 0.7:  # Threshold for relevance
                    item['relevance_score'] = relevance_score
                    relevant_news.append(item)
                    
            # Sort by relevance
            relevant_news.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return relevant_news[:3]  # Top 3 most relevant
            
        except Exception as e:
            logger.warning(f"News fetching failed: {e}")
            return []
            
    def _calculate_news_relevance(self, news_item: Dict[str, Any], 
                                topic: str) -> float:
        """Calculate relevance score between news and topic"""
        # Simple keyword matching (could be enhanced with NLP)
        title = news_item.get('title', '').lower()
        description = news_item.get('description', '').lower()
        topic_words = topic.lower().split()
        
        matches = sum(1 for word in topic_words if word in title or word in description)
        relevance = matches / len(topic_words) if topic_words else 0
        
        # Boost score for recent news
        published = news_item.get('published_at')
        if published:
            age_hours = (datetime.now() - published).total_seconds() / 3600
            recency_boost = max(0, 1 - (age_hours / 168))  # Decay over a week
            relevance = (relevance * 0.7) + (recency_boost * 0.3)
            
        return min(relevance, 1.0)
        
    def _validate_content_policy(self, script: Dict[str, Any], 
                               platform: Platform) -> None:
        """Validate script against platform content policies"""
        # Check for prohibited content
        prohibited_terms = {
            'violence': ['kill', 'murder', 'assault'],
            'adult': ['explicit', 'nude', 'sexual'],
            'hate': ['hate', 'discriminate', 'racist'],
            'dangerous': ['dangerous', 'harmful', 'illegal']
        }
        
        full_text = self._extract_full_text(script)
        
        for category, terms in prohibited_terms.items():
            for term in terms:
                if term in full_text.lower():
                    raise ContentPolicyViolation(
                        platform.value, category, full_text
                    )
                    
    def _extract_json(self, text: str) -> Any:
        """Extract JSON from AI response"""
        try:
            # Find JSON in response
            json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except:
            pass
        return None
        
    def _load_hook_templates(self) -> Dict[str, List[str]]:
        """Load hook templates for fallback"""
        return {
            'question': [
                "Did you know that {topic}?",
                "What if I told you {topic}?",
                "Have you ever wondered about {topic}?"
            ],
            'shock': [
                "You won't believe what happened with {topic}!",
                "This {topic} will blow your mind!",
                "The truth about {topic} is shocking!"
            ],
            'promise': [
                "Here's how to master {topic} in seconds!",
                "Learn the secret of {topic}!",
                "The ultimate guide to {topic}!"
            ],
            'story': [
                "This is what happened when I tried {topic}...",
                "My experience with {topic} changed everything!",
                "The day I discovered {topic}..."
            ]
        }
        
    def _load_content_structures(self) -> Dict[str, Any]:
        """Load content structure templates"""
        return {
            'list': {
                'segments': ['intro', 'item1', 'item2', 'item3', 'outro'],
                'transitions': ['number_overlay', 'swipe', 'zoom']
            },
            'tutorial': {
                'segments': ['problem', 'step1', 'step2', 'result'],
                'transitions': ['arrow', 'highlight', 'checkmark']
            },
            'story': {
                'segments': ['setup', 'conflict', 'resolution'],
                'transitions': ['fade', 'cut', 'dissolve']
            }
        }
        
    def decide_frame_continuity(self, topic: str, style: str, category: VideoCategory, 
                              duration: int, platform: Platform) -> Dict[str, Any]:
        """
        Decide whether to use frame continuity for seamless video generation
        
        Frame continuity creates a single flowing video where each clip's last frame
        becomes the first frame of the next clip, creating smooth transitions.
        
        Returns:
            Dictionary with continuity decision and reasoning
        """
        try:
            logger.info(f"Analyzing whether to use frame continuity for {topic}")
            
            # Analyze content type for continuity suitability
            continuity_suitable_styles = [
                'story', 'narrative', 'journey', 'process', 'tutorial',
                'documentary', 'vlog', 'tour', 'exploration', 'evolution'
            ]
            
            continuity_unsuitable_styles = [
                'compilation', 'list', 'countdown', 'comparison', 'reaction',
                'meme', 'montage', 'highlights', 'quick cuts'
            ]
            
            # Check if style suggests continuity
            style_lower = style.lower()
            suggests_continuity = any(s in style_lower for s in continuity_suitable_styles)
            suggests_cuts = any(s in style_lower for s in continuity_unsuitable_styles)
            
            # Platform preferences
            platform_continuity_preference = {
                Platform.YOUTUBE: 0.7,      # YouTube favors longer, flowing content
                Platform.TIKTOK: 0.3,       # TikTok prefers quick cuts
                Platform.INSTAGRAM: 0.5,     # Instagram is neutral
                Platform.FACEBOOK: 0.6       # Facebook slightly favors continuity
            }
            
            # Category preferences
            category_continuity_preference = {
                VideoCategory.EDUCATION: 0.8,
                VideoCategory.TECHNOLOGY: 0.7,
                VideoCategory.NEWS: 0.6,
                VideoCategory.LIFESTYLE: 0.7,
                VideoCategory.ENTERTAINMENT: 0.4,
                VideoCategory.COMEDY: 0.3,
                VideoCategory.GAMING: 0.5,
                VideoCategory.MUSIC: 0.4,
                VideoCategory.SPORTS: 0.5,
                VideoCategory.OTHER: 0.5
            }
            
            # Duration factor (longer videos benefit more from continuity)
            duration_factor = min(1.0, duration / 60)  # Normalize to 0-1
            
            # Calculate continuity score
            base_score = 0.5
            
            if suggests_continuity:
                base_score += 0.3
            if suggests_cuts:
                base_score -= 0.3
                
            platform_score = platform_continuity_preference.get(platform, 0.5)
            category_score = category_continuity_preference.get(category, 0.5)
            
            # Weighted final score
            continuity_score = (
                base_score * 0.4 +
                platform_score * 0.2 +
                category_score * 0.2 +
                duration_factor * 0.2
            )
            
            # Make decision
            use_continuity = continuity_score >= 0.6
            
            # Generate reasoning
            reasoning = []
            if suggests_continuity:
                reasoning.append(f"Style '{style}' suggests flowing narrative")
            if suggests_cuts:
                reasoning.append(f"Style '{style}' typically uses quick cuts")
            reasoning.append(f"{platform.value} platform preference: {platform_score:.1f}")
            reasoning.append(f"{category.value} category preference: {category_score:.1f}")
            reasoning.append(f"Duration factor ({duration}s): {duration_factor:.1f}")
            
            # Transition strategy if using continuity
            transition_strategy = None
            if use_continuity:
                transition_strategy = self._determine_transition_strategy(
                    topic, style, category
                )
            
            decision = {
                'use_frame_continuity': use_continuity,
                'continuity_score': round(continuity_score, 2),
                'reasoning': reasoning,
                'transition_strategy': transition_strategy,
                'recommended_clip_count': self._calculate_continuity_clips(duration, use_continuity),
                'frame_overlap_type': 'last_to_first' if use_continuity else None
            }
            
            logger.info(f"Frame continuity decision: {use_continuity} (score: {continuity_score:.2f})")
            return decision
            
        except Exception as e:
            logger.error(f"Error deciding frame continuity: {e}")
            return {
                'use_frame_continuity': False,
                'continuity_score': 0.5,
                'reasoning': ['Error in analysis, defaulting to standard cuts'],
                'transition_strategy': None,
                'recommended_clip_count': self._calculate_segments(duration),
                'frame_overlap_type': None
            }
    
    def _determine_transition_strategy(self, topic: str, style: str, 
                                     category: VideoCategory) -> Dict[str, Any]:
        """Determine the transition strategy for continuous videos"""
        
        # Define transition types for continuous flow
        transition_types = {
            'smooth_motion': {
                'description': 'Camera or subject movement continues across clips',
                'suitable_for': ['journey', 'tour', 'exploration', 'vlog'],
                'instructions': 'End each clip with motion that continues in next clip'
            },
            'object_tracking': {
                'description': 'Follow same object/person across clips',
                'suitable_for': ['story', 'documentary', 'tutorial', 'process'],
                'instructions': 'Keep main subject in similar position at clip boundaries'
            },
            'environment_flow': {
                'description': 'Natural environment progression',
                'suitable_for': ['nature', 'travel', 'lifestyle', 'meditation'],
                'instructions': 'Transition through connected spaces or time progression'
            },
            'narrative_continuity': {
                'description': 'Story or explanation flows seamlessly',
                'suitable_for': ['education', 'news', 'technology', 'narrative'],
                'instructions': 'Visual elements support continuous narration'
            }
        }
        
        # Select best transition type
        style_lower = style.lower()
        selected_type = 'narrative_continuity'  # Default
        
        for trans_type, config in transition_types.items():
            if any(keyword in style_lower for keyword in config['suitable_for']):
                selected_type = trans_type
                break
        
        return {
            'type': selected_type,
            'config': transition_types[selected_type],
            'frame_blend_duration': 0.1,  # 100ms blend between clips
            'maintain_subject_position': selected_type in ['object_tracking', 'smooth_motion'],
            'color_correction': True,  # Match colors between clips
            'audio_crossfade': True    # Smooth audio transitions
        }
    
    def _calculate_continuity_clips(self, duration: int, use_continuity: bool) -> int:
        """Calculate optimal number of clips for continuity mode"""
        if use_continuity:
            # Fewer, longer clips for smooth continuity
            if duration <= 30:
                return 3  # 10s each
            elif duration <= 60:
                return 4  # 15s each
            elif duration <= 120:
                return 6  # 20s each
            else:
                return 8  # For longer videos
        else:
            # More clips for dynamic cutting
            return self._calculate_segments(duration)

    def _get_template_hook(self, topic: str, style: str) -> Dict[str, str]:
        """Get fallback hook from templates"""
        hook_type = 'question' if 'tutorial' in style else 'shock'
        template = self.hook_templates[hook_type][0]
        
        return {
            'text': template.format(topic=topic),
            'type': hook_type,
            'visual_cue': f"Text overlay with {style} background",
            'duration_seconds': 3
        }
        
    def _calculate_segments(self, duration: int) -> int:
        """Calculate optimal number of segments"""
        # Roughly 5-10 seconds per segment
        return max(3, min(duration // 7, 8))
        
    def _get_default_segments(self, topic: str, num_segments: int) -> List[Dict]:
        """Get default content segments"""
        segments = []
        segment_duration = 30 // num_segments  # Assume 30s default
        
        for i in range(num_segments):
            segments.append({
                'text': f"Point {i+1} about {topic}",
                'visual': f"Relevant visual for point {i+1}",
                'duration': segment_duration,
                'transition': 'cut'
            })
            
        return segments

    def _analyze_hook_patterns(self, successful_hooks: List[str]) -> Dict[str, Any]:
        """Analyze patterns in successful hooks"""
        if not successful_hooks:
            return {
                'common_words': ['amazing', 'incredible', 'shocking'],
                'patterns': ['question', 'promise', 'shock'],
                'avg_length': 15
            }
        
        # Simple pattern analysis
        all_words = []
        for hook in successful_hooks:
            all_words.extend(hook.lower().split())
        
        # Count word frequency
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most common words
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'common_words': [word for word, freq in common_words],
            'patterns': ['question', 'promise', 'shock'],
            'avg_length': sum(len(hook) for hook in successful_hooks) // len(successful_hooks)
        }
    
    def _assemble_script(self, hook: Dict[str, str], main_content: List[Dict[str, Any]], 
                        cta: Dict[str, str], duration: int, platform: Platform) -> Dict[str, Any]:
        """Assemble complete script from components"""
        try:
            # Calculate timing
            hook_duration = hook.get('duration_seconds', 3)
            cta_duration = 2
            content_duration = duration - hook_duration - cta_duration
            
            # Distribute content duration across segments
            if main_content:
                segment_duration = content_duration / len(main_content)
                for segment in main_content:
                    segment['duration'] = segment_duration
            
            # Assemble complete script
            script = {
                'hook': hook,
                'segments': main_content,
                'cta': cta,
                'total_duration': duration,
                'platform': platform.value,
                'created_at': datetime.now().isoformat(),
                'structure': {
                    'hook_duration': hook_duration,
                    'content_duration': content_duration,
                    'cta_duration': cta_duration
                }
            }
            
            # Add full text for analysis
            full_text = hook.get('text', '')
            for segment in main_content:
                full_text += ' ' + segment.get('text', '')
            full_text += ' ' + cta.get('text', '')
            script['full_text'] = full_text.strip()
            
            return script
            
        except Exception as e:
            logger.error(f"Script assembly failed: {e}")
            # Return minimal script as fallback
            return {
                'hook': hook,
                'segments': main_content or [{'text': f'Amazing content about {hook.get("text", "this topic")}', 'duration': duration-5}],
                'cta': cta,
                'total_duration': duration,
                'platform': platform.value,
                'created_at': datetime.now().isoformat(),
                'full_text': f'{hook.get("text", "")} Amazing content. {cta.get("text", "")}'
            }

    def _format_news_context(self, news_items: List[Dict[str, Any]]) -> str:
        """Format news items into context string"""
        if not news_items:
            return ""
        
        context = "Recent news context:\n"
        for item in news_items[:3]:
            title = item.get('title', 'Unknown')
            context += f"- {title}\n"
        return context
    
    def _extract_full_text(self, script: Dict[str, Any]) -> str:
        """Extract all text from script for analysis"""
        text_parts = []
        
        # Add hook text
        if 'hook' in script and 'text' in script['hook']:
            text_parts.append(script['hook']['text'])
        
        # Add segment texts
        for segment in script.get('segments', []):
            if 'text' in segment:
                text_parts.append(segment['text'])
        
        # Add CTA text
        if 'cta' in script and 'text' in script['cta']:
            text_parts.append(script['cta']['text'])
        
        return ' '.join(text_parts)
    
    def _enhance_hook_virality(self, hook: Dict[str, str], viral_elements: Dict[str, Any]) -> Dict[str, str]:
        """Enhance hook for viral potential"""
        # Add emotional triggers if missing
        emotional_words = ['amazing', 'incredible', 'shocking', 'unbelievable', 'mind-blowing']
        hook_text = hook.get('text', '')
        
        if not any(word in hook_text.lower() for word in emotional_words):
            # Add emotional trigger
            hook['text'] = f"This is {emotional_words[0]}! {hook_text}"
        
        return hook
    
    def _optimize_segment_pacing(self, segments: List[Dict[str, Any]], pacing: str) -> List[Dict[str, Any]]:
        """Optimize segment pacing for engagement"""
        if pacing == 'fast':
            # Ensure segments are short and punchy
            for segment in segments:
                if segment.get('duration', 0) > 5:
                    segment['duration'] = 5
                # Make text more concise
                text = segment.get('text', '')
                if len(text) > 100:
                    segment['text'] = text[:97] + '...'
        
        return segments
    
    def _calculate_shareability(self, script: Dict[str, Any]) -> float:
        """Calculate shareability score"""
        # Simple scoring based on content elements
        score = 0.5  # Base score
        
        full_text = self._extract_full_text(script)
        
        # Check for viral keywords
        viral_keywords = ['amazing', 'incredible', 'shocking', 'unbelievable', 'secret', 'truth']
        for keyword in viral_keywords:
            if keyword in full_text.lower():
                score += 0.1
        
        # Check for questions (engagement)
        if '?' in full_text:
            score += 0.1
        
        # Check for emotional language
        emotional_words = ['love', 'hate', 'excited', 'angry', 'surprised', 'happy']
        for word in emotional_words:
            if word in full_text.lower():
                score += 0.05
        
        return min(score, 1.0)
    
    def _analyze_emotional_arc(self, script: Dict[str, Any]) -> str:
        """Analyze emotional progression in script"""
        # Simple emotional arc analysis
        segments = script.get('segments', [])
        if len(segments) <= 2:
            return 'flat'
        elif len(segments) <= 4:
            return 'rising'
        else:
            return 'complex'
    
    def _identify_surprise_moments(self, script: Dict[str, Any]) -> List[str]:
        """Identify potential surprise moments in script"""
        surprises = []
        full_text = self._extract_full_text(script)
        
        surprise_indicators = ['but', 'however', 'actually', 'suddenly', 'unexpectedly', 'plot twist']
        for indicator in surprise_indicators:
            if indicator in full_text.lower():
                surprises.append(f"Surprise at: {indicator}")
        
        return surprises 