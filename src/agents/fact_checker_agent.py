"""
Internet-Connected Fact Checker Agent
Provides real-time fact checking, current events, and verified information for AI discussions
Uses web search and multiple sources to ensure accuracy
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import re
import asyncio
import time
from ..services.news_api_service import news_service

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False

from ..utils.logging_config import get_logger
from ..utils.json_fixer import create_json_fixer
from ..config.ai_model_config import DEFAULT_AI_MODEL

logger = get_logger(__name__)


@dataclass
class FactCheckResult:
    """Result of fact checking operation"""
    claim: str
    verification_status: str  # "verified", "false", "partially_true", "unverified", "outdated"
    confidence_score: float  # 0-1
    sources: List[str]
    evidence: List[str]
    corrections: List[str]
    last_updated: datetime
    reasoning: str


@dataclass
class NewsUpdate:
    """Current news and events information"""
    topic: str
    headline: str
    summary: str
    source: str
    publish_date: datetime
    relevance_score: float  # 0-1, how relevant to the topic
    url: Optional[str] = None


@dataclass
class FactualInsight:
    """Factual insights and current information for content creation"""
    topic: str
    key_facts: List[str]
    recent_developments: List[NewsUpdate]
    expert_perspectives: List[str]
    statistics: Dict[str, Any]
    common_misconceptions: List[str]
    verification_sources: List[str]
    last_updated: datetime


class InternetFactCheckerAgent:
    """AI agent that provides real-time fact checking and current information"""
    
    def __init__(self, api_key: str, enable_web_search: bool = True):
        self.api_key = api_key
        self.enable_web_search = enable_web_search
        
        if GEMINI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(DEFAULT_AI_MODEL)
        else:
            self.model = None
            logger.warning("⚠️ Gemini not available. Fact checking will be limited.")
        
        self.json_fixer = create_json_fixer(api_key)
        
        # Cache for recent searches to avoid redundant API calls
        self.fact_cache = {}
        self.news_cache = {}
        self.cache_timeout = timedelta(hours=1)  # Cache expires after 1 hour
        
        # Trusted news sources for fact checking
        self.trusted_sources = [
            "reuters.com", "ap.org", "bbc.com", "npr.org",
            "factcheck.org", "snopes.com", "politifact.com",
            "cdc.gov", "who.int", "nasa.gov", "nist.gov"
        ]
        
        logger.info("🔍 Internet Fact Checker Agent initialized")
    
    def verify_facts_for_discussion(self, content: str, topic: str, 
                                  platform: str = "general") -> Dict[str, Any]:
        """Verify facts and provide current information for AI agent discussions"""
        try:
            logger.info(f"🔍 Starting fact verification for topic: {topic}")
            
            # Extract claims that need verification
            claims = self._extract_verifiable_claims(content)
            
            # Fact check each claim
            fact_check_results = []
            for claim in claims:
                result = self._fact_check_claim(claim, topic)
                fact_check_results.append(result)
            
            # Get current information about the topic
            factual_insights = self._get_current_factual_insights(topic)
            
            # Generate fact checker recommendations
            recommendations = self._generate_fact_checker_recommendations(
                content, fact_check_results, factual_insights, platform
            )
            
            return {
                "agent_name": "FactCheckerAgent",
                "verification_summary": {
                    "total_claims_checked": len(claims),
                    "verified_claims": len([r for r in fact_check_results if r.verification_status == "verified"]),
                    "false_claims": len([r for r in fact_check_results if r.verification_status == "false"]),
                    "unverified_claims": len([r for r in fact_check_results if r.verification_status == "unverified"]),
                    "overall_accuracy": self._calculate_overall_accuracy(fact_check_results)
                },
                "fact_check_results": [self._format_fact_check_result(r) for r in fact_check_results],
                "current_information": self._format_factual_insights(factual_insights),
                "recommendations": recommendations,
                "sources_consulted": list(set([s for r in fact_check_results for s in r.sources])),
                "last_updated": datetime.now().isoformat(),
                "confidence_level": self._calculate_confidence_level(fact_check_results, factual_insights)
            }
            
        except Exception as e:
            logger.error(f"❌ Fact verification failed: {e}")
            return self._create_fallback_response(content, topic)
    
    def _extract_verifiable_claims(self, content: str) -> List[str]:
        """Extract factual claims that can be verified from content"""
        try:
            if not self.model:
                return self._extract_claims_basic(content)
            
            prompt = f"""
            Analyze the following content and extract specific factual claims that can be verified:
            
            Content: "{content}"
            
            CRITICAL REQUIREMENTS:
            - Extract only specific, verifiable factual statements
            - Focus on statistics, dates, scientific facts, historical events, current events
            - Avoid opinions, subjective statements, or general claims
            - Include claims about recent developments or trends
            - Each claim should be a complete, standalone statement
            
            Return as JSON array of strings:
            {{
                "verifiable_claims": [
                    "specific factual claim 1",
                    "specific factual claim 2"
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract and parse JSON
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                claims = result.get("verifiable_claims", [])
                logger.info(f"🔍 Extracted {len(claims)} verifiable claims")
                return claims
            
            return self._extract_claims_basic(content)
            
        except Exception as e:
            logger.warning(f"⚠️ Claim extraction failed: {e}")
            return self._extract_claims_basic(content)
    
    def _extract_claims_basic(self, content: str) -> List[str]:
        """Basic claim extraction without AI"""
        # Simple pattern-based extraction
        claims = []
        
        # Look for sentences with numbers, percentages, dates
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if (re.search(r'\d+%', sentence) or  # Percentages
                re.search(r'\d{4}', sentence) or  # Years
                re.search(r'\$\d+', sentence) or  # Money amounts
                re.search(r'\d+\s*(million|billion|thousand)', sentence, re.IGNORECASE) or  # Large numbers
                any(word in sentence.lower() for word in ['study', 'research', 'report', 'according to'])):
                claims.append(sentence)
        
        return claims[:5]  # Limit to 5 claims
    
    def _fact_check_claim(self, claim: str, topic: str) -> FactCheckResult:
        """Fact check a specific claim using web search and AI analysis"""
        try:
            # Check cache first
            cache_key = f"{claim}_{topic}"
            if cache_key in self.fact_cache:
                cached_result, timestamp = self.fact_cache[cache_key]
                if datetime.now() - timestamp < self.cache_timeout:
                    logger.info(f"📋 Using cached fact check for: {claim[:50]}...")
                    return cached_result
            
            logger.info(f"🔍 Fact checking claim: {claim[:100]}...")
            
            # Search for information about the claim
            search_results = self._search_for_verification(claim, topic)
            
            # Analyze the claim with AI
            verification_result = self._analyze_claim_with_ai(claim, search_results)
            
            # Cache the result
            self.fact_cache[cache_key] = (verification_result, datetime.now())
            
            return verification_result
            
        except Exception as e:
            logger.warning(f"⚠️ Fact checking failed for claim: {e}")
            return FactCheckResult(
                claim=claim,
                verification_status="unverified",
                confidence_score=0.0,
                sources=[],
                evidence=[],
                corrections=[],
                last_updated=datetime.now(),
                reasoning=f"Fact checking failed: {e}"
            )
    
    def _search_for_verification(self, claim: str, topic: str) -> List[Dict[str, str]]:
        """Search for information to verify the claim"""
        search_results = []
        
        if not WEB_SCRAPING_AVAILABLE or not self.enable_web_search:
            logger.warning("⚠️ Web search not available - using limited verification")
            return search_results
        
        try:
            # Create search query
            search_query = f'"{claim}" {topic} fact check verify'
            
            # Use a simple web search approach (in production, you'd use proper APIs)
            # This is a simplified example - in practice, use Google Search API, Bing API, etc.
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Search on fact-checking sites
            fact_check_sites = [
                f"site:factcheck.org {claim}",
                f"site:snopes.com {claim}",
                f"site:reuters.com {claim}",
                f"site:ap.org {claim}"
            ]
            
            for site_query in fact_check_sites[:2]:  # Limit to 2 to avoid rate limits
                try:
                    # Use news API to search for fact checks
                    fact_check_articles = news_service.search_news(
                        query=site_query,
                        max_results=3,
                        days_back=30
                    )
                    
                    for article in fact_check_articles:
                        search_results.append({
                            "title": article.get('title', ''),
                            "url": article.get('url', ''),
                            "snippet": article.get('description', ''),
                            "source": article.get('source', 'Unknown')
                        })
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"⚠️ Search failed for {site_query}: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"⚠️ Web search failed: {e}")
        
        return search_results
    
    def _analyze_claim_with_ai(self, claim: str, search_results: List[Dict[str, str]]) -> FactCheckResult:
        """Analyze claim using AI with search results"""
        try:
            if not self.model:
                return self._create_basic_fact_check_result(claim)
            
            # Prepare search context
            search_context = ""
            if search_results:
                search_context = "\n".join([
                    f"Source: {result.get('source', 'Unknown')}\n"
                    f"Title: {result.get('title', '')}\n"
                    f"Content: {result.get('snippet', '')}\n"
                    for result in search_results[:3]  # Limit to 3 results
                ])
            
            prompt = f"""
            As an expert fact checker, analyze the following claim using the provided search results:
            
            CLAIM TO VERIFY: "{claim}"
            
            SEARCH RESULTS:
            {search_context}
            
            ANALYSIS REQUIREMENTS:
            - Determine if the claim is verified, false, partially true, or unverified
            - Provide confidence score (0-1) based on evidence quality
            - List specific evidence supporting or contradicting the claim
            - Identify any corrections needed if the claim is false or outdated
            - Consider the recency and reliability of sources
            
            Return analysis as JSON:
            {{
                "verification_status": "verified|false|partially_true|unverified|outdated",
                "confidence_score": 0.0-1.0,
                "evidence": ["evidence point 1", "evidence point 2"],
                "corrections": ["correction 1 if needed", "correction 2 if needed"],
                "reasoning": "detailed explanation of the verification process",
                "sources_used": ["source 1", "source 2"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                
                return FactCheckResult(
                    claim=claim,
                    verification_status=analysis.get("verification_status", "unverified"),
                    confidence_score=float(analysis.get("confidence_score", 0.5)),
                    sources=analysis.get("sources_used", []),
                    evidence=analysis.get("evidence", []),
                    corrections=analysis.get("corrections", []),
                    last_updated=datetime.now(),
                    reasoning=analysis.get("reasoning", "AI analysis completed")
                )
            
            return self._create_basic_fact_check_result(claim)
            
        except Exception as e:
            logger.warning(f"⚠️ AI claim analysis failed: {e}")
            return self._create_basic_fact_check_result(claim)
    
    def _get_current_factual_insights(self, topic: str) -> FactualInsight:
        """Get current factual insights and recent developments for a topic"""
        try:
            # Check cache first
            if topic in self.news_cache:
                cached_insights, timestamp = self.news_cache[topic]
                if datetime.now() - timestamp < self.cache_timeout:
                    logger.info(f"📋 Using cached insights for topic: {topic}")
                    return cached_insights
            
            logger.info(f"🌐 Gathering current factual insights for: {topic}")
            
            # Get recent news and developments
            recent_news = self._get_recent_news(topic)
            
            # Get expert perspectives and key facts
            insights = self._analyze_topic_with_ai(topic, recent_news)
            
            # Cache the insights
            self.news_cache[topic] = (insights, datetime.now())
            
            return insights
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get factual insights: {e}")
            return self._create_basic_factual_insight(topic)
    
    def _get_recent_news(self, topic: str) -> List[NewsUpdate]:
        """Get recent news about the topic"""
        try:
            if not self.enable_web_search:
                return []
            
            # Use real news API service
            news_updates = []
            
            # Search for recent news about the topic
            try:
                articles = news_service.search_news(
                    query=topic,
                    max_results=10,
                    days_back=7
                )
                
                for article in articles:
                    # Parse published date
                    try:
                        published = datetime.fromisoformat(article.get('published_at', '').replace('Z', '+00:00'))
                    except:
                        published = datetime.now()
                    
                    news_updates.append(NewsUpdate(
                        topic=topic,
                        headline=article.get('title', ''),
                        summary=article.get('description', ''),
                        source=article.get('source', 'Unknown'),
                        publish_date=published,
                        relevance_score=article.get('relevance_score', 0.5),
                        url=article.get('url')
                    ))
                
                logger.info(f"✅ Found {len(news_updates)} real news articles for '{topic}'")
                
            except Exception as e:
                logger.warning(f"⚠️ News API error: {e}")
                # Return empty list if API fails
                return []
            
            return news_updates
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get recent news: {e}")
            return []
    
    def _analyze_topic_with_ai(self, topic: str, recent_news: List[NewsUpdate]) -> FactualInsight:
        """Analyze topic with AI to provide comprehensive factual insights"""
        try:
            if not self.model:
                return self._create_basic_factual_insight(topic)
            
            # Prepare news context
            news_context = ""
            if recent_news:
                news_context = "\n".join([
                    f"Headline: {news.headline}\n"
                    f"Summary: {news.summary}\n"
                    f"Source: {news.source}\n"
                    f"Date: {news.publish_date.strftime('%Y-%m-%d')}\n"
                    for news in recent_news[:3]
                ])
            
            prompt = f"""
            As an expert researcher with access to current information, provide comprehensive factual insights about: "{topic}"
            
            RECENT NEWS CONTEXT:
            {news_context}
            
            PROVIDE INSIGHTS INCLUDING:
            - Key factual information and statistics
            - Recent developments and trends
            - Expert perspectives and authoritative viewpoints
            - Common misconceptions that should be corrected
            - Reliable sources for verification
            
            Return as JSON:
            {{
                "key_facts": ["fact 1", "fact 2", "fact 3"],
                "statistics": {{"statistic_name": "value", "another_stat": "value"}},
                "recent_developments": ["development 1", "development 2"],
                "expert_perspectives": ["perspective 1", "perspective 2"],
                "common_misconceptions": ["misconception 1", "misconception 2"],
                "verification_sources": ["source 1", "source 2", "source 3"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                insights_data = json.loads(json_match.group())
                
                return FactualInsight(
                    topic=topic,
                    key_facts=insights_data.get("key_facts", []),
                    recent_developments=recent_news,  # Use actual news data
                    expert_perspectives=insights_data.get("expert_perspectives", []),
                    statistics=insights_data.get("statistics", {}),
                    common_misconceptions=insights_data.get("common_misconceptions", []),
                    verification_sources=insights_data.get("verification_sources", []),
                    last_updated=datetime.now()
                )
            
            return self._create_basic_factual_insight(topic)
            
        except Exception as e:
            logger.warning(f"⚠️ AI topic analysis failed: {e}")
            return self._create_basic_factual_insight(topic)
    
    def _generate_fact_checker_recommendations(self, content: str, 
                                             fact_check_results: List[FactCheckResult],
                                             factual_insights: FactualInsight,
                                             platform: str) -> Dict[str, Any]:
        """Generate recommendations based on fact checking results"""
        try:
            if not self.model:
                return self._create_basic_recommendations()
            
            # Summarize fact check results
            verification_summary = ""
            for result in fact_check_results:
                verification_summary += f"Claim: {result.claim}\n"
                verification_summary += f"Status: {result.verification_status}\n"
                verification_summary += f"Confidence: {result.confidence_score}\n"
                if result.corrections:
                    verification_summary += f"Corrections: {'; '.join(result.corrections)}\n"
                verification_summary += "\n"
            
            prompt = f"""
            As a fact-checking expert, provide recommendations for content creators based on this analysis:
            
            ORIGINAL CONTENT: "{content}"
            
            FACT CHECK RESULTS:
            {verification_summary}
            
            CURRENT FACTUAL INSIGHTS:
            Key Facts: {'; '.join(factual_insights.key_facts)}
            Recent Developments: {'; '.join([news.headline for news in factual_insights.recent_developments])}
            Common Misconceptions: {'; '.join(factual_insights.common_misconceptions)}
            
            TARGET PLATFORM: {platform}
            
            PROVIDE RECOMMENDATIONS FOR:
            - Content accuracy improvements
            - Fact corrections needed
            - Additional context to include
            - Sources to cite
            - Claims to strengthen with evidence
            - Potential misinformation risks
            - Suggestions for current/trending information to add
            
            Return as JSON:
            {{
                "accuracy_improvements": ["improvement 1", "improvement 2"],
                "fact_corrections": ["correction 1", "correction 2"],
                "additional_context": ["context 1", "context 2"],
                "recommended_sources": ["source 1", "source 2"],
                "evidence_needed": ["claim needing evidence 1", "claim needing evidence 2"],
                "misinformation_risks": ["risk 1", "risk 2"],
                "trending_additions": ["trending info 1", "trending info 2"],
                "overall_assessment": "brief overall assessment",
                "confidence_in_content": 0.0-1.0
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                return recommendations
            
            return self._create_basic_recommendations()
            
        except Exception as e:
            logger.warning(f"⚠️ Recommendation generation failed: {e}")
            return self._create_basic_recommendations()
    
    def _calculate_overall_accuracy(self, fact_check_results: List[FactCheckResult]) -> float:
        """Calculate overall accuracy score"""
        if not fact_check_results:
            return 0.5
        
        total_score = 0
        for result in fact_check_results:
            if result.verification_status == "verified":
                total_score += result.confidence_score
            elif result.verification_status == "false":
                total_score += (1 - result.confidence_score)
            elif result.verification_status == "partially_true":
                total_score += result.confidence_score * 0.7
            else:  # unverified or outdated
                total_score += 0.5
        
        return total_score / len(fact_check_results)
    
    def _calculate_confidence_level(self, fact_check_results: List[FactCheckResult],
                                  factual_insights: FactualInsight) -> str:
        """Calculate overall confidence level"""
        accuracy = self._calculate_overall_accuracy(fact_check_results)
        
        if accuracy >= 0.8:
            return "high"
        elif accuracy >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _format_fact_check_result(self, result: FactCheckResult) -> Dict[str, Any]:
        """Format fact check result for JSON output"""
        return {
            "claim": result.claim,
            "verification_status": result.verification_status,
            "confidence_score": round(result.confidence_score, 2),
            "sources": result.sources,
            "evidence": result.evidence,
            "corrections": result.corrections,
            "reasoning": result.reasoning,
            "last_updated": result.last_updated.isoformat()
        }
    
    def _format_factual_insights(self, insights: FactualInsight) -> Dict[str, Any]:
        """Format factual insights for JSON output"""
        return {
            "topic": insights.topic,
            "key_facts": insights.key_facts,
            "recent_developments": [
                {
                    "headline": news.headline,
                    "summary": news.summary,
                    "source": news.source,
                    "publish_date": news.publish_date.isoformat(),
                    "relevance_score": news.relevance_score
                }
                for news in insights.recent_developments
            ],
            "expert_perspectives": insights.expert_perspectives,
            "statistics": insights.statistics,
            "common_misconceptions": insights.common_misconceptions,
            "verification_sources": insights.verification_sources,
            "last_updated": insights.last_updated.isoformat()
        }
    
    # Fallback methods for when AI/web services are not available
    
    def _create_basic_fact_check_result(self, claim: str) -> FactCheckResult:
        """Create basic fact check result when full analysis is not available"""
        return FactCheckResult(
            claim=claim,
            verification_status="unverified",
            confidence_score=0.5,
            sources=["Manual verification recommended"],
            evidence=["Claim requires manual verification"],
            corrections=[],
            last_updated=datetime.now(),
            reasoning="Automated fact checking not available - manual verification recommended"
        )
    
    def _create_basic_factual_insight(self, topic: str) -> FactualInsight:
        """Create basic factual insight when full analysis is not available"""
        return FactualInsight(
            topic=topic,
            key_facts=[f"Manual research recommended for {topic}"],
            recent_developments=[],
            expert_perspectives=["Consult authoritative sources for expert opinions"],
            statistics={},
            common_misconceptions=["Verify all claims about this topic"],
            verification_sources=["Trusted academic and news sources"],
            last_updated=datetime.now()
        )
    
    def _create_basic_recommendations(self) -> Dict[str, Any]:
        """Create basic recommendations when full analysis is not available"""
        return {
            "accuracy_improvements": ["Verify all factual claims with authoritative sources"],
            "fact_corrections": ["Manual fact checking recommended"],
            "additional_context": ["Include source citations"],
            "recommended_sources": ["Academic institutions", "Government agencies", "Established news organizations"],
            "evidence_needed": ["All statistical and factual claims"],
            "misinformation_risks": ["Unverified claims"],
            "trending_additions": ["Check current news for latest developments"],
            "overall_assessment": "Manual fact checking recommended for accuracy",
            "confidence_in_content": 0.5
        }
    
    def _create_fallback_response(self, content: str, topic: str) -> Dict[str, Any]:
        """Create fallback response when fact checking fails"""
        return {
            "agent_name": "FactCheckerAgent",
            "verification_summary": {
                "total_claims_checked": 0,
                "verified_claims": 0,
                "false_claims": 0,
                "unverified_claims": 0,
                "overall_accuracy": 0.5
            },
            "fact_check_results": [],
            "current_information": {
                "topic": topic,
                "key_facts": ["Manual verification recommended"],
                "recent_developments": [],
                "expert_perspectives": [],
                "statistics": {},
                "common_misconceptions": [],
                "verification_sources": ["Authoritative sources recommended"],
                "last_updated": datetime.now().isoformat()
            },
            "recommendations": self._create_basic_recommendations(),
            "sources_consulted": [],
            "last_updated": datetime.now().isoformat(),
            "confidence_level": "low",
            "error_message": "Fact checking services unavailable - manual verification recommended"
        }