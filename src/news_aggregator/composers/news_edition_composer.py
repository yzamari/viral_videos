"""News Edition Composer - Creates news videos using AI agents and scraped media"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

from ...utils.logging_config import get_logger
from ...utils.session_manager import SessionManager
from ...ai.manager import AIServiceManager
from ...core.decision_framework import DecisionFramework, CoreDecisions
# from ...agents.discussions.professional_panel import get_professional_discussions
# TODO: Fix missing module
from ...models.video_models import Platform, VideoCategory, Language
from ..models.content_models import ContentItem, ContentCollection
from ..models.composition_models import CompositionProject, VideoSegment, VideoLayer
from ..processors.media_downloader import MediaDownloader

logger = get_logger(__name__)


class NewsEditionComposer:
    """Composes news editions using AI agents and scraped media"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        ai_manager: AIServiceManager,
        decision_framework: DecisionFramework,
        media_downloader: MediaDownloader
    ):
        self.session_manager = session_manager
        self.ai_manager = ai_manager
        self.decision_framework = decision_framework
        self.media_downloader = media_downloader
        
        # AI Agent configurations for different news types
        self.agent_configs = {
            "general": {
                "agents": ["reporter", "analyst", "fact_checker", "editor"],
                "discussion_topics": [
                    "headline_selection",
                    "story_ordering",
                    "narrative_flow",
                    "visual_presentation"
                ]
            },
            "sports": {
                "agents": ["sports_analyst", "statistician", "commentator", "highlight_editor"],
                "discussion_topics": [
                    "key_moments",
                    "player_performance",
                    "match_analysis",
                    "highlight_selection"
                ]
            },
            "tech": {
                "agents": ["tech_expert", "innovation_analyst", "security_specialist", "trend_predictor"],
                "discussion_topics": [
                    "technical_implications",
                    "market_impact",
                    "future_trends",
                    "user_benefits"
                ]
            },
            "finance": {
                "agents": ["market_analyst", "economist", "risk_assessor", "investment_advisor"],
                "discussion_topics": [
                    "market_movements",
                    "economic_indicators",
                    "investment_opportunities",
                    "risk_factors"
                ]
            },
            "gossip": {
                "agents": ["entertainment_reporter", "social_media_analyst", "celebrity_expert", "trend_watcher"],
                "discussion_topics": [
                    "celebrity_news",
                    "viral_moments",
                    "relationship_updates",
                    "fashion_trends"
                ]
            }
        }
    
    async def compose_news_edition(
        self,
        content_collections: List[ContentCollection],
        edition_type: str,
        composition_project: CompositionProject,
        use_scraped_media: bool = True
    ) -> Dict[str, Any]:
        """Compose a complete news edition using AI agents and media"""
        
        logger.info(f"Composing {edition_type} news edition with {len(content_collections)} stories")
        
        # 1. Download all media from content
        if use_scraped_media:
            media_assets = await self._download_all_media(content_collections)
        else:
            media_assets = {}
        
        # 2. Run AI agent discussions
        agent_decisions = await self._run_agent_discussions(
            content_collections,
            edition_type,
            media_assets
        )
        
        # 3. Create detailed script with agent insights
        script = await self._create_edition_script(
            content_collections,
            agent_decisions,
            edition_type
        )
        
        # 4. Create visual composition plan
        composition_plan = await self._create_composition_plan(
            script,
            media_assets,
            agent_decisions,
            composition_project
        )
        
        # 5. Generate video segments
        video_segments = await self._generate_video_segments(
            composition_plan,
            media_assets,
            use_scraped_media
        )
        
        # Store everything in session
        self.session_manager.session_data.update({
            "edition_type": edition_type,
            "agent_decisions": agent_decisions,
            "script": script,
            "composition_plan": composition_plan,
            "media_assets": media_assets,
            "video_segments": video_segments
        })
        
        return {
            "script": script,
            "composition_plan": composition_plan,
            "video_segments": video_segments,
            "agent_insights": agent_decisions,
            "media_count": len(media_assets)
        }
    
    async def _download_all_media(
        self,
        content_collections: List[ContentCollection]
    ) -> Dict[str, Any]:
        """Download all media from content collections"""
        
        all_media_urls = []
        media_metadata = {}
        
        # Collect all media URLs
        for collection in content_collections:
            for item in collection.items:
                for asset in item.media_assets:
                    url = asset.source_url
                    all_media_urls.append(url)
                    media_metadata[url] = {
                        "content_id": item.id,
                        "collection_id": collection.id,
                        "asset_type": asset.asset_type.value,
                        "metadata": asset.metadata
                    }
        
        # Download media
        logger.info(f"Downloading {len(all_media_urls)} media assets...")
        downloaded = await self.media_downloader.download_media_batch(
            all_media_urls,
            media_metadata
        )
        
        # Organize by content
        media_by_content = {}
        for media in downloaded:
            content_id = media['metadata'].get('content_id')
            if content_id:
                if content_id not in media_by_content:
                    media_by_content[content_id] = []
                media_by_content[content_id].append(media)
        
        return media_by_content
    
    async def _run_agent_discussions(
        self,
        content_collections: List[ContentCollection],
        edition_type: str,
        media_assets: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run AI agent discussions for news edition"""
        
        logger.info(f"Running AI agent discussions for {edition_type} edition...")
        
        # Get agent configuration
        config = self.agent_configs.get(edition_type, self.agent_configs["general"])
        
        # Prepare discussion context
        context = {
            "edition_type": edition_type,
            "num_stories": len(content_collections),
            "stories": [
                {
                    "title": collection.name,
                    "description": collection.description,
                    "num_items": len(collection.items),
                    "tags": collection.tags,
                    "has_media": any(
                        media_assets.get(item.id) for item in collection.items
                    )
                }
                for collection in content_collections
            ],
            "total_media": sum(
                len(media_list) for media_list in media_assets.values()
            )
        }
        
        # Run discussions on each topic
        discussions = {}
        for topic in config["discussion_topics"]:
            discussion_prompt = self._create_discussion_prompt(topic, context)
            
            # Get agent responses
            agent_responses = await self._get_agent_responses(
                config["agents"],
                discussion_prompt,
                topic
            )
            
            # Synthesize consensus
            consensus = await self._synthesize_consensus(
                agent_responses,
                topic
            )
            
            discussions[topic] = {
                "responses": agent_responses,
                "consensus": consensus
            }
        
        return discussions
    
    def _create_discussion_prompt(
        self,
        topic: str,
        context: Dict[str, Any]
    ) -> str:
        """Create prompt for agent discussion"""
        
        prompts = {
            "headline_selection": f"""
                As a news {context['edition_type']} expert, analyze these {context['num_stories']} stories 
                and recommend which should be the lead story and why. Consider newsworthiness, 
                audience interest, and visual impact.
                
                Stories: {json.dumps(context['stories'], indent=2)}
            """,
            
            "story_ordering": f"""
                Recommend the optimal order for presenting these {context['num_stories']} stories 
                in a {context['edition_type']} news edition. Consider narrative flow, 
                audience engagement, and pacing.
                
                Stories: {json.dumps(context['stories'], indent=2)}
            """,
            
            "narrative_flow": f"""
                Design the narrative structure for this {context['edition_type']} news edition.
                How should we transition between stories? What's the overall narrative arc?
                
                Stories: {json.dumps(context['stories'], indent=2)}
            """,
            
            "visual_presentation": f"""
                Recommend visual treatment for each story. We have {context['total_media']} 
                media assets available. How should we use them effectively?
                
                Stories with media availability: {json.dumps(context['stories'], indent=2)}
            """,
            
            "key_moments": f"""
                Identify the most important moments or highlights from these stories 
                that must be included in the video edition.
                
                Stories: {json.dumps(context['stories'], indent=2)}
            """,
            
            "highlight_selection": f"""
                From the available media, select the most impactful visuals and moments
                for a compelling {context['edition_type']} video.
                
                Available media per story: {json.dumps(context['stories'], indent=2)}
            """
        }
        
        return prompts.get(topic, prompts["headline_selection"])
    
    async def _get_agent_responses(
        self,
        agents: List[str],
        prompt: str,
        topic: str
    ) -> Dict[str, str]:
        """Get responses from each agent"""
        
        responses = {}
        
        for agent in agents:
            agent_prompt = f"As a {agent}, {prompt}"
            
            try:
                response = await self.ai_manager.generate_text(
                    agent_prompt,
                    max_tokens=500
                )
                responses[agent] = response.strip()
            except Exception as e:
                logger.error(f"Agent {agent} failed: {str(e)}")
                responses[agent] = f"Error: {str(e)}"
        
        return responses
    
    async def _synthesize_consensus(
        self,
        agent_responses: Dict[str, str],
        topic: str
    ) -> Dict[str, Any]:
        """Synthesize consensus from agent responses"""
        
        synthesis_prompt = f"""
        Synthesize these expert opinions on {topic} into a consensus decision:
        
        {json.dumps(agent_responses, indent=2)}
        
        Provide:
        1. Key decision/recommendation
        2. Reasoning
        3. Any dissenting views
        4. Confidence level (0-1)
        """
        
        try:
            synthesis = await self.ai_manager.generate_text(
                synthesis_prompt,
                max_tokens=300
            )
            
            # Parse synthesis (simplified - in production would use structured output)
            return {
                "decision": synthesis.strip(),
                "confidence": 0.8,
                "topic": topic
            }
        except Exception as e:
            logger.error(f"Consensus synthesis failed: {str(e)}")
            return {
                "decision": "Use default approach",
                "confidence": 0.5,
                "topic": topic
            }
    
    async def _create_edition_script(
        self,
        content_collections: List[ContentCollection],
        agent_decisions: Dict[str, Any],
        edition_type: str
    ) -> Dict[str, Any]:
        """Create detailed script based on agent decisions"""
        
        # Get story ordering from agents
        ordering_decision = agent_decisions.get("story_ordering", {}).get("consensus", {})
        
        script = {
            "edition_type": edition_type,
            "total_duration": 0,
            "segments": []
        }
        
        # Create intro
        intro_segment = {
            "type": "intro",
            "duration": 5,
            "narration": self._generate_intro_narration(edition_type, len(content_collections)),
            "visuals": "edition_opener"
        }
        script["segments"].append(intro_segment)
        script["total_duration"] += 5
        
        # Process each story
        for i, collection in enumerate(content_collections):
            # Calculate segment duration based on importance
            base_duration = 30  # Base 30 seconds per story
            if i == 0:  # Lead story gets more time
                segment_duration = base_duration * 1.5
            else:
                segment_duration = base_duration
            
            segment = {
                "type": "news_story",
                "story_index": i,
                "collection_id": collection.id,
                "title": collection.name,
                "duration": segment_duration,
                "narration": await self._generate_story_narration(
                    collection,
                    agent_decisions,
                    segment_duration
                ),
                "visuals": self._plan_story_visuals(
                    collection,
                    agent_decisions.get("visual_presentation", {})
                ),
                "transition": self._get_transition_type(i, len(content_collections))
            }
            
            script["segments"].append(segment)
            script["total_duration"] += segment_duration
        
        # Create outro
        outro_segment = {
            "type": "outro",
            "duration": 5,
            "narration": self._generate_outro_narration(edition_type),
            "visuals": "edition_closer"
        }
        script["segments"].append(outro_segment)
        script["total_duration"] += 5
        
        return script
    
    def _generate_intro_narration(self, edition_type: str, num_stories: int) -> str:
        """Generate intro narration"""
        
        intros = {
            "general": f"Good evening, I'm your AI news anchor. Tonight we have {num_stories} important stories from around the world.",
            "sports": f"Welcome to sports highlights! We've got {num_stories} exciting stories from the world of sports.",
            "tech": f"Hello and welcome to tech news. Today we're covering {num_stories} groundbreaking developments in technology.",
            "finance": f"Good day, welcome to financial news. We have {num_stories} important market updates for you.",
            "gossip": f"Hey there! Welcome to entertainment news. We've got {num_stories} juicy stories from the world of celebrities."
        }
        
        return intros.get(edition_type, intros["general"])
    
    async def _generate_story_narration(
        self,
        collection: ContentCollection,
        agent_decisions: Dict[str, Any],
        duration: float
    ) -> str:
        """Generate narration for a story segment"""
        
        # Get key points from agent decisions
        key_moments = agent_decisions.get("key_moments", {}).get("consensus", {})
        
        # Calculate word count for duration (150 words per minute)
        target_words = int((duration / 60) * 150)
        
        prompt = f"""
        Write news narration for this story in exactly {target_words} words:
        
        Title: {collection.name}
        Description: {collection.description}
        Key Points: {key_moments.get('decision', '')}
        
        Style: Professional news anchor
        Tone: Informative and engaging
        """
        
        try:
            narration = await self.ai_manager.generate_text(prompt, max_tokens=300)
            return narration.strip()
        except:
            # Fallback narration
            return collection.description
    
    def _plan_story_visuals(
        self,
        collection: ContentCollection,
        visual_decisions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Plan visuals for story segment"""
        
        visuals = []
        
        # Add title card
        visuals.append({
            "type": "title_card",
            "duration": 2,
            "text": collection.name,
            "style": "lower_third"
        })
        
        # Add media visuals
        for i, item in enumerate(collection.items[:3]):  # Top 3 items
            if item.has_images() or item.has_video():
                visuals.append({
                    "type": "content_media",
                    "content_id": item.id,
                    "duration": 5,
                    "caption": item.title[:50]
                })
        
        # Add data visualization if relevant
        if any(tag in ["finance", "statistics", "data"] for tag in collection.tags):
            visuals.append({
                "type": "data_viz",
                "duration": 3,
                "style": "animated_chart"
            })
        
        return visuals
    
    def _get_transition_type(self, index: int, total: int) -> str:
        """Determine transition type between segments"""
        
        if index == 0:
            return "fade_in"
        elif index == total - 1:
            return "fade_to_outro"
        else:
            transitions = ["wipe", "dissolve", "slide"]
            return transitions[index % len(transitions)]
    
    def _generate_outro_narration(self, edition_type: str) -> str:
        """Generate outro narration"""
        
        outros = {
            "general": "That's all for now. Thank you for watching, and we'll see you next time.",
            "sports": "That wraps up today's sports highlights. Stay tuned for more action!",
            "tech": "Thanks for joining us for tech news. Keep innovating!",
            "finance": "That concludes our market update. Invest wisely.",
            "gossip": "That's all the buzz for now! See you next time for more entertainment news."
        }
        
        return outros.get(edition_type, outros["general"])
    
    async def _create_composition_plan(
        self,
        script: Dict[str, Any],
        media_assets: Dict[str, Any],
        agent_decisions: Dict[str, Any],
        composition_project: CompositionProject
    ) -> Dict[str, Any]:
        """Create detailed composition plan"""
        
        composition_plan = {
            "timeline": [],
            "assets_needed": [],
            "effects": [],
            "audio_tracks": []
        }
        
        current_time = 0.0
        
        for segment in script["segments"]:
            segment_plan = {
                "start_time": current_time,
                "end_time": current_time + segment["duration"],
                "type": segment["type"],
                "layers": []
            }
            
            # Plan layers based on segment type
            if segment["type"] == "intro":
                segment_plan["layers"].extend([
                    {
                        "type": "background",
                        "asset": "news_intro_bg",
                        "duration": segment["duration"]
                    },
                    {
                        "type": "text",
                        "content": composition_project.name,
                        "style": "title",
                        "animation": "zoom_in"
                    }
                ])
            
            elif segment["type"] == "news_story":
                # Add media layers
                content_id = segment.get("collection_id")
                if content_id and content_id in media_assets:
                    for i, media in enumerate(media_assets[content_id][:3]):
                        segment_plan["layers"].append({
                            "type": "media",
                            "asset_path": media["local_path"],
                            "media_type": media["media_type"],
                            "start_offset": i * 5,
                            "duration": 5
                        })
                
                # Add text overlays
                segment_plan["layers"].append({
                    "type": "lower_third",
                    "text": segment["title"],
                    "duration": segment["duration"]
                })
            
            # Add narration audio
            segment_plan["audio"] = {
                "type": "narration",
                "text": segment["narration"],
                "voice": "news_anchor"
            }
            
            composition_plan["timeline"].append(segment_plan)
            current_time += segment["duration"]
        
        # Add background music track
        composition_plan["audio_tracks"].append({
            "type": "background_music",
            "style": "news_theme",
            "volume": 0.3,
            "duration": current_time
        })
        
        return composition_plan
    
    async def _generate_video_segments(
        self,
        composition_plan: Dict[str, Any],
        media_assets: Dict[str, Any],
        use_scraped_media: bool
    ) -> List[Dict[str, Any]]:
        """Generate video segment instructions"""
        
        video_segments = []
        
        for timeline_item in composition_plan["timeline"]:
            segment = {
                "start": timeline_item["start_time"],
                "end": timeline_item["end_time"],
                "duration": timeline_item["end_time"] - timeline_item["start_time"],
                "type": timeline_item["type"],
                "instructions": []
            }
            
            # Generate instructions based on layers
            for layer in timeline_item["layers"]:
                if layer["type"] == "media" and use_scraped_media:
                    segment["instructions"].append({
                        "action": "use_media",
                        "source": layer["asset_path"],
                        "type": layer["media_type"],
                        "duration": layer["duration"]
                    })
                elif layer["type"] == "text":
                    segment["instructions"].append({
                        "action": "add_text",
                        "content": layer.get("content", layer.get("text")),
                        "style": layer.get("style", "default"),
                        "position": "lower_third"
                    })
                elif layer["type"] == "background":
                    segment["instructions"].append({
                        "action": "set_background",
                        "asset": layer["asset"]
                    })
            
            # Add audio instruction
            if "audio" in timeline_item:
                segment["instructions"].append({
                    "action": "add_narration",
                    "text": timeline_item["audio"]["text"],
                    "voice": timeline_item["audio"]["voice"]
                })
            
            video_segments.append(segment)
        
        return video_segments