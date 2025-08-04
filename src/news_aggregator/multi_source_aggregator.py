#!/usr/bin/env python3
"""
Multi-Source News Aggregator
Aggregates media from multiple sources for each news story
Uses AI agents to decide on presentation
"""

import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import json
import re
from datetime import datetime
from collections import defaultdict
import hashlib

from .agents.news_discussion_agents import (
    NewsItem, NewsDiscussionModerator
)


class MultiSourceNewsAggregator:
    """Aggregates news from multiple sources and groups by story"""
    
    def __init__(self):
        self.sources = {
            'cnn': {
                'url': 'https://www.cnn.com',
                'name': 'CNN',
                'selector': 'article',
                'reliability': 0.9
            },
            'bbc': {
                'url': 'https://www.bbc.com/news',
                'name': 'BBC',
                'selector': 'article',
                'reliability': 0.95
            },
            'reuters': {
                'url': 'https://www.reuters.com',
                'name': 'Reuters',
                'selector': 'article',
                'reliability': 0.95
            },
            'ap': {
                'url': 'https://apnews.com',
                'name': 'Associated Press',
                'selector': 'div.FeedCard',
                'reliability': 0.95
            },
            'guardian': {
                'url': 'https://www.theguardian.com/international',
                'name': 'The Guardian',
                'selector': 'article',
                'reliability': 0.85
            },
            'nytimes': {
                'url': 'https://www.nytimes.com',
                'name': 'New York Times',
                'selector': 'article',
                'reliability': 0.9
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        self.story_groups = defaultdict(list)
        self.media_cache = {}
    
    async def aggregate_news(self, categories: List[str] = None, 
                           max_stories: int = 10) -> List[NewsItem]:
        """Aggregate news from all sources and group by story"""
        
        print("🌐 Aggregating news from multiple sources...")
        
        # Fetch from all sources
        all_articles = await self._fetch_all_sources(categories)
        
        # Group similar stories
        story_clusters = self._cluster_stories(all_articles)
        
        # Create NewsItem objects with aggregated data
        news_items = []
        for cluster_id, articles in story_clusters.items():
            if len(articles) > 0:
                news_item = await self._create_news_item(articles)
                if news_item:
                    news_items.append(news_item)
        
        # Sort by importance (number of sources covering the story)
        news_items.sort(key=lambda x: len(x.sources), reverse=True)
        
        return news_items[:max_stories]
    
    async def _fetch_all_sources(self, categories: List[str] = None) -> List[Dict]:
        """Fetch articles from all news sources"""
        
        all_articles = []
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = []
            
            for source_id, source_info in self.sources.items():
                task = self._fetch_source(session, source_id, source_info, categories)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            for articles in results:
                all_articles.extend(articles)
        
        print(f"📰 Fetched {len(all_articles)} articles from {len(self.sources)} sources")
        return all_articles
    
    async def _fetch_source(self, session: aiohttp.ClientSession, 
                          source_id: str, source_info: Dict,
                          categories: List[str] = None) -> List[Dict]:
        """Fetch articles from a single source"""
        
        articles = []
        
        try:
            # Build URL with category if specified
            url = source_info['url']
            if categories and source_id == 'cnn':
                # Example: CNN category URLs
                if 'sports' in categories:
                    url = 'https://www.cnn.com/sport'
                elif 'tech' in categories:
                    url = 'https://www.cnn.com/business/tech'
            
            async with session.get(url, headers=self.headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find articles based on source selector
                    article_elements = soup.select(source_info['selector'])[:20]
                    
                    for elem in article_elements:
                        article = self._parse_article(elem, source_info)
                        if article:
                            articles.append(article)
                    
                    print(f"  ✅ {source_info['name']}: {len(articles)} articles")
                
        except Exception as e:
            print(f"  ❌ {source_info['name']}: {str(e)}")
        
        return articles
    
    def _parse_article(self, element, source_info: Dict) -> Optional[Dict]:
        """Parse article element based on source"""
        
        try:
            # Extract title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if len(title) < 10:
                return None
            
            # Extract URL
            url = None
            link_elem = element.find('a', href=True)
            if link_elem:
                url = link_elem['href']
                if not url.startswith('http'):
                    url = source_info['url'] + url
            
            # Extract image
            image_url = None
            img_elem = element.find('img', src=True)
            if img_elem:
                image_url = img_elem['src']
                if not image_url.startswith('http'):
                    image_url = 'https:' + image_url if image_url.startswith('//') else source_info['url'] + image_url
            
            # Extract video if available
            video_url = None
            video_elem = element.find('video')
            if video_elem:
                source_elem = video_elem.find('source', src=True)
                if source_elem:
                    video_url = source_elem['src']
            
            # Extract description
            desc_elem = element.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Determine category
            category = self._determine_category(title, description, url)
            
            return {
                'title': title,
                'url': url,
                'source': source_info['name'],
                'source_id': source_info.get('id'),
                'reliability': source_info['reliability'],
                'image_url': image_url,
                'video_url': video_url,
                'description': description,
                'category': category,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return None
    
    def _determine_category(self, title: str, description: str, url: str) -> str:
        """Determine article category based on content"""
        
        text = f"{title} {description} {url}".lower()
        
        # Category keywords
        categories = {
            'breaking_news': ['breaking', 'urgent', 'just in', 'alert', 'developing'],
            'politics': ['president', 'election', 'government', 'senate', 'congress', 'minister'],
            'sports': ['game', 'match', 'player', 'team', 'score', 'championship', 'league'],
            'technology': ['tech', 'ai', 'software', 'app', 'startup', 'digital', 'cyber'],
            'finance': ['stock', 'market', 'economy', 'dollar', 'bitcoin', 'inflation', 'bank'],
            'entertainment': ['movie', 'celebrity', 'music', 'hollywood', 'oscar', 'singer'],
            'health': ['covid', 'virus', 'vaccine', 'health', 'medical', 'doctor'],
            'science': ['research', 'study', 'scientist', 'discovery', 'space', 'nasa'],
            'weather': ['storm', 'hurricane', 'weather', 'temperature', 'forecast', 'climate']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general'
    
    def _cluster_stories(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Cluster similar stories together"""
        
        clusters = defaultdict(list)
        
        for article in articles:
            # Create a signature for the story
            signature = self._create_story_signature(article['title'])
            clusters[signature].append(article)
        
        # Merge similar clusters
        merged_clusters = self._merge_similar_clusters(clusters)
        
        return merged_clusters
    
    def _create_story_signature(self, title: str) -> str:
        """Create a signature for story clustering"""
        
        # Extract key terms
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'}
        
        # Extract important words
        words = re.findall(r'\b\w+\b', title.lower())
        key_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Sort and create signature
        key_words.sort()
        signature = '-'.join(key_words[:5])  # Use top 5 key words
        
        return hashlib.md5(signature.encode()).hexdigest()[:8]
    
    def _merge_similar_clusters(self, clusters: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Merge clusters that are similar"""
        
        # For now, return as-is
        # TODO: Implement similarity comparison between clusters
        
        return clusters
    
    async def _create_news_item(self, articles: List[Dict]) -> Optional[NewsItem]:
        """Create a NewsItem from clustered articles"""
        
        if not articles:
            return None
        
        # Use the most common title or the one from most reliable source
        articles.sort(key=lambda x: x.get('reliability', 0), reverse=True)
        main_article = articles[0]
        
        # Collect all sources
        sources = []
        for article in articles:
            sources.append({
                'name': article['source'],
                'headline': article['title'],
                'url': article.get('url'),
                'reliability': article.get('reliability', 0.5)
            })
        
        # Collect all media items
        media_items = await self._collect_media_items(articles)
        
        # Determine category (most common)
        categories = [a.get('category', 'general') for a in articles]
        category = max(set(categories), key=categories.count)
        
        news_item = NewsItem(
            title=main_article['title'],
            category=category,
            sources=sources,
            media_items=media_items
        )
        
        return news_item
    
    async def _collect_media_items(self, articles: List[Dict]) -> List[Dict]:
        """Collect all unique media items from articles"""
        
        media_items = []
        seen_urls = set()
        
        for article in articles:
            # Add image
            if article.get('image_url') and article['image_url'] not in seen_urls:
                media_items.append({
                    'type': 'image',
                    'url': article['image_url'],
                    'source': article['source'],
                    'quality_score': self._assess_media_quality(article['image_url'], 'image')
                })
                seen_urls.add(article['image_url'])
            
            # Add video
            if article.get('video_url') and article['video_url'] not in seen_urls:
                media_items.append({
                    'type': 'video',
                    'url': article['video_url'],
                    'source': article['source'],
                    'quality_score': self._assess_media_quality(article['video_url'], 'video')
                })
                seen_urls.add(article['video_url'])
        
        # Sort by quality score
        media_items.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return media_items
    
    def _assess_media_quality(self, url: str, media_type: str) -> float:
        """Assess quality of media based on source and type"""
        
        quality = 0.5  # Base quality
        
        # Video generally higher quality
        if media_type == 'video':
            quality += 0.2
        
        # High-res indicators
        if any(indicator in url for indicator in ['hd', '1080', '720', 'high']):
            quality += 0.1
        
        # Trusted domains
        trusted_domains = ['cnn.com', 'bbc.com', 'reuters.com', 'apnews.com']
        if any(domain in url for domain in trusted_domains):
            quality += 0.2
        
        return min(quality, 1.0)


class IntelligentNewsCompiler:
    """Compiles news using AI agent decisions and multi-source aggregation"""
    
    def __init__(self):
        self.aggregator = MultiSourceNewsAggregator()
        self.moderator = NewsDiscussionModerator()
        os.makedirs("intelligent_news_output", exist_ok=True)
    
    async def create_intelligent_compilation(self, 
                                           categories: List[str] = None,
                                           total_duration: int = 60,
                                           output_name: str = None):
        """Create an intelligent news compilation"""
        
        print(f"""
🤖 INTELLIGENT NEWS COMPILATION
==============================
📡 Multi-source aggregation
🎭 AI agent discussions
📊 Smart media selection
⏱️  Target duration: {total_duration}s
""")
        
        # Step 1: Aggregate news from multiple sources
        print("\n📡 Step 1: Aggregating news from multiple sources...")
        news_items = await self.aggregator.aggregate_news(categories)
        
        print(f"\n📰 Found {len(news_items)} unique stories:")
        for i, item in enumerate(news_items[:5]):
            print(f"  {i+1}. {item.title[:60]}... ({len(item.sources)} sources)")
        
        # Step 2: AI agents discuss each story
        print("\n🎭 Step 2: AI agents discussing each story...")
        
        for item in news_items:
            consensus = self.moderator.conduct_discussion(item)
            item.agent_consensus = consensus
            item.recommended_duration = consensus['final_duration']
            item.selected_media = consensus['selected_media']
            item.summary = consensus['summary']
        
        # Step 3: Select stories based on total duration
        print("\n📊 Step 3: Selecting stories for compilation...")
        selected_items = self._select_stories_for_duration(news_items, total_duration)
        
        # Step 4: Download media for selected stories
        print("\n📥 Step 4: Downloading media for selected stories...")
        for item in selected_items:
            await self._download_story_media(item)
        
        # Step 5: Create video segments
        print("\n🎬 Step 5: Creating video segments...")
        segments = []
        for i, item in enumerate(selected_items):
            segment_path = await self._create_story_segment(item, i)
            if segment_path:
                segments.append(segment_path)
        
        # Step 6: Compile final video
        print("\n🎬 Step 6: Creating final compilation...")
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"intelligent_news_{timestamp}.mp4"
        
        final_path = self._compile_segments(segments, output_name)
        
        # Create summary report
        self._create_summary_report(selected_items, final_path)
        
        return final_path
    
    def _select_stories_for_duration(self, news_items: List[NewsItem], 
                                   target_duration: int) -> List[NewsItem]:
        """Select stories that fit within target duration"""
        
        selected = []
        current_duration = 0
        
        # Sort by importance score
        news_items.sort(key=lambda x: x.agent_consensus.get('importance_score', 0), 
                       reverse=True)
        
        for item in news_items:
            item_duration = item.recommended_duration
            
            if current_duration + item_duration <= target_duration:
                selected.append(item)
                current_duration += item_duration
            elif current_duration + 3 <= target_duration:
                # Can fit a shortened version
                item.recommended_duration = target_duration - current_duration
                selected.append(item)
                break
        
        print(f"\n✅ Selected {len(selected)} stories for {current_duration}s total")
        
        return selected
    
    async def _download_story_media(self, news_item: NewsItem):
        """Download media for a story"""
        
        downloaded_media = []
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            for media in news_item.selected_media:
                try:
                    filename = f"intelligent_news_output/{news_item.category}_{len(downloaded_media)}.jpg"
                    
                    # For demo, create placeholder
                    if 'placeholder' in media.get('url', '') or not media.get('url'):
                        # Create placeholder image
                        from PIL import Image, ImageDraw, ImageFont
                        
                        img = Image.new('RGB', (1920, 1080), color=(30, 30, 30))
                        draw = ImageDraw.Draw(img)
                        
                        try:
                            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
                            font_source = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
                        except:
                            font_title = ImageFont.load_default()
                            font_source = ImageFont.load_default()
                        
                        # Draw title
                        draw.text((100, 400), news_item.title[:60], 
                                fill=(255, 255, 255), font=font_title)
                        
                        # Draw source
                        draw.text((100, 500), f"Source: {media.get('source', 'Unknown')}", 
                                fill=(150, 150, 150), font=font_source)
                        
                        img.save(filename)
                    else:
                        # Download real media
                        async with session.get(media['url'], timeout=10) as response:
                            if response.status == 200:
                                content = await response.read()
                                with open(filename, 'wb') as f:
                                    f.write(content)
                    
                    media['local_path'] = filename
                    downloaded_media.append(media)
                    
                except Exception as e:
                    print(f"    ❌ Failed to download media: {e}")
        
        news_item.selected_media = downloaded_media
    
    async def _create_story_segment(self, news_item: NewsItem, index: int) -> Optional[str]:
        """Create a video segment for a news story"""
        
        try:
            # Create title card
            from PIL import Image, ImageDraw, ImageFont
            
            title_card = Image.new('RGB', (1920, 1080), color=(20, 20, 20))
            draw = ImageDraw.Draw(title_card)
            
            try:
                font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
                font_summary = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
                font_source = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except:
                font_title = ImageFont.load_default()
                font_summary = ImageFont.load_default()
                font_source = ImageFont.load_default()
            
            # Draw breaking news style
            if news_item.category == 'breaking_news':
                draw.rectangle([(0, 0), (1920, 150)], fill=(200, 0, 0))
                draw.text((100, 50), "BREAKING NEWS", fill=(255, 255, 255), font=font_title)
            
            # Draw title (word wrap)
            y_pos = 300
            words = news_item.title.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=font_title)
                if bbox[2] > 1720:  # Line too long
                    draw.text((100, y_pos), line, fill=(255, 255, 255), font=font_title)
                    y_pos += 80
                    line = word
                else:
                    line = test_line
            if line:
                draw.text((100, y_pos), line, fill=(255, 255, 255), font=font_title)
            
            # Draw summary
            y_pos += 120
            draw.text((100, y_pos), news_item.summary[:100], 
                     fill=(200, 200, 200), font=font_summary)
            
            # Draw sources
            y_pos += 100
            sources_text = f"Sources: {', '.join([s['name'] for s in news_item.sources[:3]])}"
            if len(news_item.sources) > 3:
                sources_text += f" +{len(news_item.sources) - 3} more"
            draw.text((100, y_pos), sources_text, fill=(150, 150, 150), font=font_source)
            
            # Save title card
            title_card_path = f"intelligent_news_output/title_{index}.jpg"
            title_card.save(title_card_path)
            
            # Create video segment
            output_path = f"intelligent_news_output/segment_{index}.mp4"
            
            # Determine how to split duration
            title_duration = 2  # Title card
            media_duration = news_item.recommended_duration - title_duration
            
            if news_item.selected_media:
                # Create media montage
                clips = [title_card_path]
                
                # Add selected media
                for media in news_item.selected_media:
                    if media.get('local_path'):
                        clips.append(media['local_path'])
                
                # Calculate duration per clip
                duration_per_clip = media_duration / len(news_item.selected_media)
                
                # Create concat file
                concat_path = f"intelligent_news_output/concat_{index}.txt"
                with open(concat_path, 'w') as f:
                    # Title card
                    f.write(f"file '{os.path.abspath(title_card_path)}'\n")
                    f.write(f"duration {title_duration}\n")
                    
                    # Media clips
                    for i, media in enumerate(news_item.selected_media):
                        if media.get('local_path'):
                            f.write(f"file '{os.path.abspath(media['local_path'])}'\n")
                            if i < len(news_item.selected_media) - 1:
                                f.write(f"duration {duration_per_clip}\n")
                
                # Create video with crossfade transitions
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_path,
                    '-vf', 'scale=1920:1080,fps=25',
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    '-t', str(news_item.recommended_duration),
                    output_path
                ]
                
                import subprocess
                subprocess.run(cmd, capture_output=True)
                
                # Cleanup
                os.remove(concat_path)
                
            else:
                # Just use title card for full duration
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', title_card_path,
                    '-t', str(news_item.recommended_duration),
                    '-vf', 'scale=1920:1080',
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    output_path
                ]
                
                import subprocess
                subprocess.run(cmd, capture_output=True)
            
            return output_path
            
        except Exception as e:
            print(f"    ❌ Failed to create segment: {e}")
            return None
    
    def _compile_segments(self, segments: List[str], output_name: str) -> str:
        """Compile all segments into final video"""
        
        # Create concat file
        concat_path = "intelligent_news_output/final_concat.txt"
        with open(concat_path, 'w') as f:
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        # Compile with transitions
        output_path = f"intelligent_news_output/{output_name}"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_path,
            '-c', 'copy',
            output_path
        ]
        
        import subprocess
        subprocess.run(cmd, capture_output=True)
        
        # Cleanup
        os.remove(concat_path)
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        return output_path
    
    def _create_summary_report(self, selected_items: List[NewsItem], video_path: str):
        """Create a summary report of the compilation"""
        
        report = {
            'video_path': video_path,
            'total_duration': sum(item.recommended_duration for item in selected_items),
            'story_count': len(selected_items),
            'creation_time': datetime.now().isoformat(),
            'stories': []
        }
        
        for item in selected_items:
            story_data = {
                'title': item.title,
                'category': item.category,
                'duration': item.recommended_duration,
                'sources': [s['name'] for s in item.sources],
                'media_count': len(item.selected_media),
                'summary': item.summary,
                'importance_score': item.agent_consensus.get('importance_score', 0),
                'agent_decisions': {
                    'visual_strategy': item.agent_consensus.get('media_strategy'),
                    'pacing': item.agent_consensus.get('pacing'),
                    'agent_reasoning': [
                        {
                            'agent': a.get('agent'),
                            'reasoning': a.get('reasoning')
                        }
                        for a in item.agent_consensus.get('agent_analyses', [])
                    ]
                }
            }
            report['stories'].append(story_data)
        
        # Save report
        report_path = video_path.replace('.mp4', '_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"""
📊 COMPILATION SUMMARY
====================
📹 Video: {video_path}
⏱️  Duration: {report['total_duration']}s
📰 Stories: {report['story_count']}
📄 Report: {report_path}

📰 STORY BREAKDOWN:
""")
        
        for i, story in enumerate(report['stories']):
            print(f"\n{i+1}. {story['title'][:60]}...")
            print(f"   Duration: {story['duration']}s")
            print(f"   Sources: {', '.join(story['sources'][:3])}")
            print(f"   Media: {story['media_count']} items")
            print(f"   Importance: {story['importance_score']:.2f}")


async def demo_intelligent_news():
    """Demo the intelligent news compilation system"""
    
    compiler = IntelligentNewsCompiler()
    
    # Example: Create a 60-second news compilation
    video_path = await compiler.create_intelligent_compilation(
        categories=['politics', 'technology', 'sports'],
        total_duration=60,
        output_name="intelligent_news_demo.mp4"
    )
    
    print(f"\n✅ Compilation complete: {video_path}")


if __name__ == "__main__":
    asyncio.run(demo_intelligent_news())