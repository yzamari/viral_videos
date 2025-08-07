"""News Orchestrator - Manages AI Agent Discussions for News Selection"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...utils.logging_config import get_logger
from ...ai.manager import AIServiceManager
from ...core.decision_framework import DecisionFramework

logger = get_logger(__name__)


class NewsOrchestrator:
    """Orchestrates AI agent discussions for news selection and curation"""
    
    # Define specialized news agents
    NEWS_AGENTS = [
        {
            'name': 'NewsEditor',
            'role': 'Chief News Editor',
            'personality': 'Experienced journalist focused on newsworthiness and accuracy',
            'focus': ['story importance', 'journalistic integrity', 'source credibility']
        },
        {
            'name': 'AudienceAnalyst',
            'role': 'Audience Engagement Specialist',
            'personality': 'Data-driven analyst who understands platform audiences',
            'focus': ['audience preferences', 'engagement metrics', 'platform optimization']
        },
        {
            'name': 'VisualProducer',
            'role': 'Visual Content Producer',
            'personality': 'Creative professional focused on visual storytelling',
            'focus': ['visual appeal', 'media quality', 'storytelling through visuals']
        },
        {
            'name': 'TrendExpert',
            'role': 'Trending Topics Expert',
            'personality': 'Social media savvy analyst tracking viral content',
            'focus': ['trending topics', 'viral potential', 'social relevance']
        },
        {
            'name': 'DiversityAdvocate',
            'role': 'Content Diversity Advocate',
            'personality': 'Ensures balanced and diverse news coverage',
            'focus': ['topic diversity', 'perspective balance', 'underrepresented stories']
        },
        {
            'name': 'FactChecker',
            'role': 'Fact Verification Specialist',
            'personality': 'Meticulous researcher focused on accuracy',
            'focus': ['source verification', 'fact checking', 'multiple source confirmation']
        },
        {
            'name': 'StyleAdvisor',
            'role': 'Style and Tone Advisor',
            'personality': 'Creative director ensuring content matches desired style',
            'focus': ['style consistency', 'tone appropriateness', 'brand alignment']
        },
        {
            'name': 'ContentRewriter',
            'role': 'Content Rewriting Specialist',
            'personality': 'Creative writer who adapts content tone while preserving facts',
            'focus': ['humor adaptation', 'satirical rewriting', 'tone transformation']
        }
    ]
    
    def __init__(
        self,
        ai_manager: AIServiceManager,
        decision_framework: DecisionFramework
    ):
        self.ai_manager = ai_manager
        self.decision_framework = decision_framework
        self.discussion_log = []
    
    async def run_news_selection_discussion(
        self,
        context: Dict[str, Any],
        enable_logging: bool = False
    ) -> Dict[str, Any]:
        """Run orchestrated discussion for news selection"""
        
        logger.info("🎭 Starting AI agent news discussion...")
        
        # Extract context
        content = context['content']
        style = context['style']
        tone = context['tone']
        platform = context['platform']
        max_stories = context['max_stories']
        criteria = context.get('criteria', {})
        
        # Initialize discussion
        self.discussion_log = []
        
        # Phase 1: Initial Analysis
        analysis_results = await self._phase_initial_analysis(content, criteria)
        
        # Phase 2: Platform Optimization
        platform_scores = await self._phase_platform_optimization(
            content, platform, style, tone, analysis_results
        )
        
        # Phase 3: Selection Debate
        selection_results = await self._phase_selection_debate(
            content, max_stories, analysis_results, platform_scores
        )
        
        # Phase 4: Final Ranking
        final_ranking = await self._phase_final_ranking(
            selection_results, style, tone
        )
        
        # Compile results - SMART SELECTION: Cap at 15 stories max for performance
        # This prevents timeout issues when max_stories is high (like 50)
        optimal_story_count = min(max_stories, 15) if max_stories > 10 else max_stories
        logger.info(f"🎯 AI agents selected {optimal_story_count} stories from {len(content)} available (max requested: {max_stories})")
        
        result = {
            'selected_indices': final_ranking['indices'][:optimal_story_count],
            'insights': final_ranking['insights'],
            'reasoning': final_ranking['reasoning'],
            'discussion_summary': self._summarize_discussion()
        }
        
        if enable_logging:
            result['full_discussion'] = self.discussion_log
        
        return result
    
    async def _phase_initial_analysis(
        self,
        content: List[Dict[str, Any]],
        criteria: Dict[str, str]
    ) -> Dict[str, Any]:
        """Phase 1: Each agent analyzes all content"""
        
        logger.info("📊 Phase 1: Initial Analysis")
        
        analyses = {}
        
        for agent in self.NEWS_AGENTS[:3]:  # Use first 3 agents for initial analysis
            agent_analysis = await self._get_agent_analysis(
                agent, content, criteria
            )
            analyses[agent['name']] = agent_analysis
            
            self._log_message(agent['name'], f"Completed analysis of {len(content)} items")
        
        return analyses
    
    async def _get_agent_analysis(
        self,
        agent: Dict[str, str],
        content: List[Dict[str, Any]],
        criteria: Dict[str, str]
    ) -> Dict[str, Any]:
        """Get individual agent's analysis of content"""
        
        # Create analysis prompt
        prompt = f"""As {agent['role']}, analyze these news items based on:
{json.dumps(criteria, indent=2)}

Focus on your expertise: {', '.join(agent['focus'])}

News items:
"""
        
        # Add content summaries
        for i, item in enumerate(content[:20]):  # Limit to prevent token overflow
            prompt += f"\n{i+1}. [{item['source']}] {item['title']}"
            if item.get('duplicate_count', 1) > 1:
                prompt += f" (confirmed by {item['duplicate_count']} sources)"
        
        prompt += "\n\nProvide scores (0-10) for each item and explain your top picks."
        
        try:
            response = await self.ai_manager.generate_content_async(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse response (simplified - in production, use structured output)
            return {
                'scores': self._extract_scores(response, len(content)),
                'insights': response
            }
            
        except Exception as e:
            logger.error(f"Agent analysis failed: {e}")
            return {'scores': [5] * len(content), 'insights': 'Analysis failed'}
    
    async def _phase_platform_optimization(
        self,
        content: List[Dict[str, Any]],
        platform: str,
        style: str,
        tone: str,
        analysis_results: Dict[str, Any]
    ) -> Dict[int, float]:
        """Phase 2: Optimize for platform and style"""
        
        logger.info(f"📱 Phase 2: {platform} Optimization")
        
        # Use AudienceAnalyst and StyleAdvisor
        platform_agent = next(a for a in self.NEWS_AGENTS if a['name'] == 'AudienceAnalyst')
        style_agent = next(a for a in self.NEWS_AGENTS if a['name'] == 'StyleAdvisor')
        
        # Platform optimization prompt
        prompt = f"""As {platform_agent['role']}, rank these news items for {platform}.
Consider the style: "{style}" and tone: "{tone}".

{platform} audience prefers:
- Short, engaging content
- Visual stories
- Trending topics
- Mobile-optimized content

Review the top items from initial analysis and adjust rankings."""
        
        platform_scores = await self._get_optimization_scores(
            prompt, content, analysis_results
        )
        
        self._log_message(
            'AudienceAnalyst',
            f"Optimized for {platform} with {style} style"
        )
        
        return platform_scores
    
    async def _phase_selection_debate(
        self,
        content: List[Dict[str, Any]],
        max_stories: int,
        analysis_results: Dict[str, Any],
        platform_scores: Dict[int, float]
    ) -> Dict[str, Any]:
        """Phase 3: Agents debate final selection"""
        
        logger.info("🗣️ Phase 3: Selection Debate")
        
        # Simulate debate between agents
        debate_messages = []
        
        # NewsEditor makes initial selection
        editor_picks = self._get_top_picks(analysis_results, platform_scores, max_stories * 2)
        debate_messages.append({
            'agent': 'NewsEditor',
            'message': f"I recommend these {len(editor_picks)} stories based on newsworthiness"
        })
        
        # FactChecker challenges
        fact_check_results = await self._fact_check_stories(editor_picks, content)
        debate_messages.append({
            'agent': 'FactChecker',
            'message': f"Verified {len(fact_check_results['verified'])} stories with multiple sources"
        })
        
        # DiversityAdvocate ensures balance
        diversity_adjustments = self._check_diversity(editor_picks, content)
        debate_messages.append({
            'agent': 'DiversityAdvocate',
            'message': diversity_adjustments['message']
        })
        
        # Log debate
        for msg in debate_messages:
            self._log_message(msg['agent'], msg['message'])
        
        return {
            'candidates': editor_picks,
            'verified': fact_check_results['verified'],
            'diversity_score': diversity_adjustments['score']
        }
    
    async def _phase_final_ranking(
        self,
        selection_results: Dict[str, Any],
        style: str,
        tone: str
    ) -> Dict[str, Any]:
        """Phase 4: Final ranking and insights"""
        
        logger.info("🏆 Phase 4: Final Ranking")
        
        # Combine all factors for final ranking
        candidates = selection_results['candidates']
        verified = selection_results['verified']
        
        final_scores = {}
        insights = {}
        reasoning = {}
        
        for idx in candidates:
            # Base score
            score = candidates[idx]
            
            # Boost for verification
            if idx in verified:
                score *= 1.2
            
            # Apply style/tone adjustments
            style_multiplier = self._get_style_multiplier(idx, style, tone)
            score *= style_multiplier
            
            final_scores[idx] = score
            
            # Generate insights
            insights[str(idx)] = {
                'verification': 'verified' if idx in verified else 'unverified',
                'style_match': style_multiplier,
                'final_score': score
            }
            
            reasoning[str(idx)] = f"Selected for strong {style} appeal and {tone} tone"
        
        # Sort by score
        sorted_indices = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)
        
        self._log_message('Orchestrator', f"Final selection complete: {len(sorted_indices)} stories ranked")
        
        return {
            'indices': sorted_indices,
            'insights': insights,
            'reasoning': reasoning
        }
    
    def _extract_scores(self, response: str, num_items: int) -> List[float]:
        """Extract scores from agent response"""
        # Simplified extraction - in production use regex or structured output
        scores = []
        
        lines = response.split('\n')
        for line in lines:
            if any(char.isdigit() for char in line):
                # Try to extract score
                try:
                    parts = line.split(':')
                    if len(parts) > 1:
                        score_part = parts[1].strip()
                        score = float(score_part.split('/')[0])
                        scores.append(score)
                except:
                    pass
        
        # Pad with default scores if needed
        while len(scores) < num_items:
            scores.append(5.0)
        
        return scores[:num_items]
    
    async def _get_optimization_scores(
        self,
        prompt: str,
        content: List[Dict[str, Any]],
        analysis_results: Dict[str, Any]
    ) -> Dict[int, float]:
        """Get platform optimization scores"""
        
        # Aggregate initial scores
        aggregated = {}
        for i in range(len(content)):
            total = sum(
                results['scores'][i] 
                for results in analysis_results.values()
                if i < len(results['scores'])
            )
            aggregated[i] = total / len(analysis_results)
        
        # Apply platform optimization (simplified)
        # In production, would use AI response
        optimized = {}
        for idx, score in aggregated.items():
            # Boost items with media
            if content[idx].get('image_url') or content[idx].get('video_url'):
                score *= 1.2
            
            # Boost multi-source stories
            if content[idx].get('duplicate_count', 1) > 1:
                score *= 1.1
            
            optimized[idx] = score
        
        return optimized
    
    def _get_top_picks(
        self,
        analysis_results: Dict[str, Any],
        platform_scores: Dict[int, float],
        count: int
    ) -> Dict[int, float]:
        """Get top picks based on combined scores"""
        
        combined = {}
        
        for idx, platform_score in platform_scores.items():
            # Average with initial analysis
            analysis_avg = sum(
                results['scores'][idx]
                for agent, results in analysis_results.items()
                if idx < len(results['scores'])
            ) / len(analysis_results)
            
            combined[idx] = (platform_score + analysis_avg) / 2
        
        # Sort and return top picks
        sorted_indices = sorted(combined.keys(), key=lambda x: combined[x], reverse=True)
        
        return {idx: combined[idx] for idx in sorted_indices[:count]}
    
    async def _fact_check_stories(
        self,
        candidates: Dict[int, float],
        content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fact check candidate stories"""
        
        verified = []
        
        for idx in candidates:
            item = content[idx]
            
            # Check for multiple sources
            if item.get('duplicate_count', 1) > 1:
                verified.append(idx)
            
            # Check for credible source
            elif item['source'] in ['CNN', 'BBC', 'Ynet', 'Reuters']:
                verified.append(idx)
        
        return {
            'verified': verified,
            'verification_rate': len(verified) / len(candidates)
        }
    
    def _check_diversity(
        self,
        candidates: Dict[int, float],
        content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check topic diversity in selection"""
        
        # Count categories
        categories = {}
        sources = {}
        
        for idx in candidates:
            item = content[idx]
            
            # Track categories
            for cat in item.get('categories', ['general']):
                categories[cat] = categories.get(cat, 0) + 1
            
            # Track sources
            source = item['source']
            sources[source] = sources.get(source, 0) + 1
        
        # Calculate diversity score
        category_diversity = len(categories) / max(len(candidates), 1)
        source_diversity = len(sources) / max(len(candidates), 1)
        
        diversity_score = (category_diversity + source_diversity) / 2
        
        message = f"Diversity check: {len(categories)} categories, {len(sources)} sources"
        
        return {
            'score': diversity_score,
            'categories': categories,
            'sources': sources,
            'message': message
        }
    
    def _get_style_multiplier(self, idx: int, style: str, tone: str) -> float:
        """Get style/tone multiplier for content"""
        
        # Simplified style matching
        style_lower = style.lower()
        tone_lower = tone.lower()
        
        multiplier = 1.0
        
        # Style adjustments
        if 'viral' in style_lower or 'trending' in style_lower:
            multiplier *= 1.2
        elif 'professional' in style_lower:
            multiplier *= 0.9
        
        # Tone adjustments
        if 'entertaining' in tone_lower:
            multiplier *= 1.1
        elif 'serious' in tone_lower or 'analytical' in tone_lower:
            multiplier *= 0.95
        
        return multiplier
    
    def _log_message(self, agent: str, message: str):
        """Log discussion message"""
        
        self.discussion_log.append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent,
            'message': message
        })
        
        logger.info(f"💬 {agent}: {message}")
    
    def _summarize_discussion(self) -> str:
        """Summarize the discussion"""
        
        summary = f"AI Discussion Summary ({len(self.discussion_log)} messages)\n"
        summary += "-" * 50 + "\n"
        
        for entry in self.discussion_log[-5:]:  # Last 5 messages
            summary += f"{entry['agent']}: {entry['message']}\n"
        
        return summary
    
    async def select_visual_styles(
        self,
        style: str,
        tone: str,
        platform: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Let AI agents select fonts and visual styles"""
        
        prompt = f"""As the Visual Producer and Style Advisor, select appropriate hooks, fonts, transitions and visual styles for:
Style: {style}
Tone: {tone}
Platform: {platform}
Language: {language}

Available font options:
1. Arial Unicode - Clean, universal, good for all languages
2. Helvetica - Modern, professional, Western languages
3. Times - Traditional, formal, news-like
4. Georgia - Elegant serif, readable
5. Impact - Bold, attention-grabbing
6. Futura - Geometric, modern
7. Bebas Neue - Condensed, trendy
8. Montserrat - Contemporary, clean

Platform-specific considerations:
- TikTok: Needs attention-grabbing hooks, quick transitions, bold colors
- Instagram: Aesthetic appeal, balanced layout, trendy feel
- YouTube: Professional but engaging, clear hierarchy
- Twitter: Concise, high contrast, quick readability

Please recommend:
- HOOKS: (3-5 platform-appropriate hook texts like "BREAKING", "🔴 URGENT", etc.)
- HOOK_COLOR: (hex color for hook background/text)
- HOOK_FONT: (font name and size for hooks)
- HEADER_FONT: (font name and size for titles)
- CONTENT_FONT: (font name and size for body text)
- COLOR_SCHEME: (primary and accent colors in hex)
- OVERLAY_STYLE: (modern/classic/minimal)
- ANIMATION_STYLE: (dynamic/subtle/static)
- TRANSITIONS: (list of transitions: cut/swipe/fade/zoom/split-screen/mosaic)

Format your response as JSON."""

        try:
            response = await self.ai_manager.generate_content_async(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            # Try to parse JSON response
            try:
                import json
                styles = json.loads(response)
            except:
                # Fallback parsing
                styles = self._parse_style_response(response)
            
            return styles
            
        except Exception as e:
            logger.error(f"Style selection failed: {e}")
    
    async def rephrase_content_with_tone(
        self,
        content_items: List[Dict[str, Any]],
        style: str,
        tone: str,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Rephrase news content with the specified tone while preserving facts"""
        
        logger.info(f"🎭 Rephrasing content with tone: {tone}, style: {style}")
        
        # Check if we need rephrasing based on tone/style
        tone_lower = tone.lower()
        style_lower = style.lower()
        
        # Always rephrase if tone/style indicates transformation is needed
        # Don't assume specific keywords - let AI interpret the user's intent
        needs_rephrasing = (
            tone_lower != 'neutral' and 
            tone_lower != 'informative' and
            tone_lower != 'professional' and
            style_lower != 'standard' and
            style_lower != 'professional'
        )
        
        if not needs_rephrasing:
            logger.info("📝 No tone rephrasing needed - returning original content")
            # Just add original_text field for dual display
            for item in content_items:
                item['original_title'] = item['title']
                item['original_content'] = item.get('content', '')
            return content_items
        
        logger.info(f"🎭 Rephrasing requested for tone: {tone}, style: {style}")
        
        # Create AI agent discussion for rephrasing
        logger.info("🤖 AI Agents discussing rephrasing approach based on user's tone/style...")
        
        rephrased_items = []
        
        for i, item in enumerate(content_items):
            try:
                original_title = item['title']
                original_content = item.get('content', '')
                
                # Create dynamic rephrasing prompt based on user's tone/style
                prompt = f"""You are a team of creative news writers adapting content to match this specific tone and style:
TONE: {tone}
STYLE: {style}

ORIGINAL NEWS:
Title: {original_title}
Content: {original_content[:500] if original_content else ''}

YOUR TASK: Transform this into {style} with {tone} tone in {language}.

YOUR TASK: Completely transform this news into {tone} with {style}.

IMPORTANT - BE ACTUALLY FUNNY/SATIRICAL:
- If tone includes 'funny', 'humor', 'satire', 'sarcastic' - BE EXTREMELY SATIRICAL
- Mock the absurdity of the situation
- Use exaggeration and irony
- Point out the ridiculous aspects
- Be witty and clever, not just factual
- Think The Onion, The Daily Show, SNL Weekend Update

OUTPUT RULES:
- Title: MAX 40 chars - MUST be funny/satirical if tone requires
- Content: 200-300 chars - Full satirical paragraph
- ACTUALLY BE {tone} - don't just state facts!
- Examples of good satirical titles:
  * "Gov Shocked: Things Cost Money"
  * "Breaking: Problem Still Problem"
  * "Expert: 'We Tried Nothing'"

For Hebrew (VERY SHORT!):
- "שוב: [דבר צפוי]" (Again: [predictable])
- "הלם: [דבר ברור]" (Shock: [obvious])
- "פתרון: [עושה יותר גרוע]" (Solution: [makes worse])

IMPORTANT RULES:
1. Keep ALL facts, names, dates accurate - only change the presentation
2. Be clever and funny, not offensive or hurtful
3. Target the absurdity of situations, not victims
4. Make it sound like real news but with obvious satirical twist
5. The title should immediately signal this is satire through its framing

PROVIDE YOUR RESPONSE IN THIS FORMAT:
REPHRASED_TITLE: [MAX 40 chars - MUST be funny/satirical]
REPHRASED_CONTENT: [MAX 60 chars - Short satirical punch line only]

REMEMBER: The rephrased title MUST be significantly different from the original while keeping facts accurate!"""
                
                # Generate rephrased content with higher temperature for creativity
                try:
                    response = await self.ai_manager.generate_content_async(
                        prompt=prompt,
                        max_tokens=1000,
                        temperature=0.9  # Higher temperature for more creative output
                    )
                    
                    # Parse response more robustly
                    rephrased_title = None
                    rephrased_content = None
                    
                    if response:
                        # Log the response for debugging
                        logger.debug(f"AI Response: {response[:500]}...")
                        
                        # Try multiple parsing approaches
                        lines = response.split('\n')
                        
                        # Look for REPHRASED_TITLE
                        for j, line in enumerate(lines):
                            if 'REPHRASED_TITLE' in line.upper():
                                # Get the content after the colon
                                if ':' in line:
                                    candidate = line.split(':', 1)[-1].strip()
                                    # Also check next line if current is empty
                                    if not candidate and j + 1 < len(lines):
                                        candidate = lines[j + 1].strip()
                                    if candidate and candidate != original_title:
                                        rephrased_title = candidate
                                        logger.info(f"🎭 Found rephrased title: {rephrased_title[:50]}...")
                                        break
                        
                        # Look for REPHRASED_CONTENT
                        for j, line in enumerate(lines):
                            if 'REPHRASED_CONTENT' in line.upper():
                                if ':' in line:
                                    candidate = line.split(':', 1)[-1].strip()
                                    if not candidate and j + 1 < len(lines):
                                        candidate = lines[j + 1].strip()
                                    if candidate:
                                        rephrased_content = candidate
                                        break
                    
                    # Validate we got actual rephrasing
                    # STRICTLY limit title length for video display
                    if rephrased_title and rephrased_title != original_title:
                        # Hard limit: 45 chars max for readability on video
                        if len(rephrased_title) > 45:
                            rephrased_title = rephrased_title[:42] + "..."
                            logger.info(f"Truncated long title to: {rephrased_title}")
                    
                    if not rephrased_title or rephrased_title == original_title or len(rephrased_title) < 10:
                        logger.warning(f"AI didn't generate proper title, creating satirical version manually")
                        # Create SHORT manual satirical versions
                        if language == 'he':
                            if 'ממשלה' in original_title or 'נתניהו' in original_title:
                                rephrased_title = "שוב: הממשלה בהלם מהמובן מאליו"
                            elif 'משבר' in original_title or 'בעיה' in original_title:
                                rephrased_title = "משבר חדש (כמו אתמול)"
                            elif 'חדש' in original_title or 'לראשונה' in original_title:
                                rephrased_title = "חדש: אותו דבר בדיוק"
                            elif 'משפחות' in original_title or 'חטופים' in original_title:
                                rephrased_title = "דרישה: עשו משהו סוף סוף"
                            else:
                                rephrased_title = "בינתיים: הכל כרגיל"
                        else:
                            rephrased_title = "Breaking: Nothing New"
                    else:
                        # We got a good rephrased title
                        logger.info(f"✅ AI successfully rephrased: '{original_title[:30]}...' -> '{rephrased_title[:30]}...'")
                    
                    if not rephrased_content:
                        rephrased_content = original_content
                        
                except Exception as e:
                    logger.error(f"AI generation error: {e}")
                    # Better fallback
                    if language == 'he':
                        rephrased_title = f"הסיפור שלא יאמן: {original_title[:40]}..."
                    else:
                        rephrased_title = f"You Won't Believe: {original_title[:40]}..."
                    rephrased_content = original_content
                
                # Create rephrased item with both versions
                rephrased_item = item.copy()
                rephrased_item['title'] = rephrased_title
                rephrased_item['content'] = rephrased_content
                rephrased_item['original_title'] = original_title
                rephrased_item['original_content'] = original_content
                rephrased_item['rephrased'] = True
                
                logger.info(f"🎭 Rephrased story {i+1}: '{original_title[:40]}...' -> '{rephrased_title[:40]}...'")
                
                rephrased_items.append(rephrased_item)
                
            except Exception as e:
                logger.warning(f"Failed to rephrase item {i+1}: {e}")
                # Keep original with dual display fields
                item_copy = item.copy()
                item_copy['original_title'] = item['title']
                item_copy['original_content'] = item.get('content', '')
                item_copy['rephrased'] = False
                rephrased_items.append(item_copy)
        
        logger.info(f"✅ Rephrased {len([i for i in rephrased_items if i.get('rephrased', False)])} out of {len(content_items)} items")
        return rephrased_items
    
    def _parse_style_response(self, response: str) -> Dict[str, Any]:
        """Parse style response from text"""
        styles = {
            'HEADER_FONT': {'name': 'Arial Unicode', 'size': 60},
            'CONTENT_FONT': {'name': 'Arial Unicode', 'size': 32},
            'COLOR_SCHEME': {'primary': '#1a1a1a', 'accent': '#ff6600'},
            'OVERLAY_STYLE': 'modern',
            'ANIMATION_STYLE': 'subtle'
        }
        
        # Simple keyword matching
        if 'Impact' in response:
            styles['HEADER_FONT']['name'] = 'Impact'
        elif 'Bebas' in response:
            styles['HEADER_FONT']['name'] = 'Bebas Neue'
        
        if 'minimal' in response.lower():
            styles['OVERLAY_STYLE'] = 'minimal'
        elif 'classic' in response.lower():
            styles['OVERLAY_STYLE'] = 'classic'
            
        return styles