"""
Content Credibility System
Implements fact-checking, source verification, and credibility scoring
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CredibilityScore:
    """Credibility assessment for content"""
    overall_score: float  # 0-10 scale
    factual_accuracy: float  # 0-10 scale
    source_quality: float  # 0-10 scale
    bias_level: float  # 0-10 scale (lower is better)
    evidence_strength: float  # 0-10 scale
    claims_verified: int
    sources_found: int
    confidence_level: str  # HIGH, MEDIUM, LOW
    verification_timestamp: str
    issues_detected: List[str]
    improvement_suggestions: List[str]


@dataclass
class FactCheckResult:
    """Result of fact-checking process"""
    claim: str
    verification_status: str  # VERIFIED, DISPUTED, UNVERIFIABLE, FALSE
    evidence_sources: List[str]
    confidence: float
    explanation: str
    last_updated: str


class ContentCredibilitySystem:
    """Advanced content credibility and fact-checking system"""
    
    def __init__(self, api_key: str):
        """Initialize with Google AI API key"""
        self.api_key = api_key
        if genai:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        # Credibility thresholds
        self.credibility_thresholds = {
            "excellent": 9.0,
            "good": 7.0,
            "acceptable": 6.0,
            "questionable": 4.0,
            "poor": 2.0
        }
        
        # Source quality rankings
        self.source_rankings = {
            "academic_journals": 10.0,
            "government_agencies": 9.0,
            "research_institutions": 9.0,
            "news_organizations": 7.0,
            "expert_interviews": 8.0,
            "industry_reports": 6.0,
            "social_media": 3.0,
            "blogs": 4.0,
            "unknown": 2.0
        }
        
        logger.info("🔍 Content Credibility System initialized")
    
    def evaluate_content_credibility(self, content: str, topic: str, 
                                   platform: str = "general") -> CredibilityScore:
        """
        Comprehensive credibility evaluation of content
        
        Args:
            content: Text content to evaluate
            topic: Main topic/subject matter
            platform: Target platform for context
            
        Returns:
            CredibilityScore with detailed assessment
        """
        try:
            logger.info(f"🔍 Evaluating content credibility for topic: {topic}")
            
            # Step 1: Extract and verify claims
            claims = self._extract_claims(content)
            fact_check_results = []
            
            for claim in claims:
                result = self._fact_check_claim(claim, topic)
                fact_check_results.append(result)
            
            # Step 2: Analyze source quality
            sources = self._identify_sources(content)
            source_quality = self._evaluate_source_quality(sources)
            
            # Step 3: Detect bias
            bias_analysis = self._analyze_bias(content, topic)
            
            # Step 4: Calculate overall credibility
            credibility_score = self._calculate_credibility_score(
                fact_check_results, source_quality, bias_analysis
            )
            
            logger.info(f"✅ Credibility evaluation complete: {credibility_score.overall_score}/10")
            return credibility_score
            
        except Exception as e:
            logger.error(f"❌ Credibility evaluation failed: {e}")
            return self._create_fallback_score(content)
    
    def _extract_claims(self, content: str) -> List[str]:
        """Extract factual claims from content"""
        try:
            if not self.model:
                # Fallback: Simple pattern-based extraction
                return self._simple_claim_extraction(content)
            
            claim_extraction_prompt = f"""
            Analyze this content and extract all factual claims that can be verified:
            
            Content: "{content}"
            
            Extract only statements that:
            1. Make specific factual assertions
            2. Can potentially be verified with evidence
            3. Are not obvious opinions or subjective statements
            
            Return a JSON list of claims:
            {{
                "claims": [
                    "specific factual claim 1",
                    "specific factual claim 2"
                ]
            }}
            """
            
            response = self.model.generate_content(claim_extraction_prompt)
            
            # Parse response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                claims = result.get('claims', [])
                logger.info(f"🔍 Extracted {len(claims)} factual claims")
                return claims
            else:
                return self._simple_claim_extraction(content)
                
        except Exception as e:
            logger.warning(f"⚠️ Claim extraction failed: {e}")
            return self._simple_claim_extraction(content)
    
    def _simple_claim_extraction(self, content: str) -> List[str]:
        """Fallback claim extraction using patterns"""
        claims = []
        
        # Pattern-based claim detection
        claim_patterns = [
            r'(\d+%|\d+\.\d+%)\s+of\s+[^.!?]*[.!?]',  # Percentage claims
            r'studies?\s+show[^.!?]*[.!?]',  # Study references
            r'research\s+indicates?[^.!?]*[.!?]',  # Research claims
            r'according\s+to[^.!?]*[.!?]',  # Attribution claims
            r'experts?\s+say[^.!?]*[.!?]',  # Expert claims
        ]
        
        for pattern in claim_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            claims.extend(matches)
        
        # Clean and deduplicate
        claims = list(set([claim.strip() for claim in claims if len(claim.strip()) > 10]))
        logger.info(f"🔍 Simple extraction found {len(claims)} potential claims")
        return claims[:5]  # Limit to top 5 claims
    
    def _fact_check_claim(self, claim: str, topic: str) -> FactCheckResult:
        """Fact-check a specific claim"""
        try:
            if not self.model:
                return self._create_basic_fact_check_result(claim)
            
            fact_check_prompt = f"""
            Fact-check this claim in the context of the topic:
            
            Claim: "{claim}"
            Topic: "{topic}"
            
            Analyze:
            1. Is this claim factually accurate?
            2. What evidence supports or contradicts it?
            3. Are there reliable sources that verify this?
            4. What is the confidence level of verification?
            
            Return JSON:
            {{
                "verification_status": "VERIFIED|DISPUTED|UNVERIFIABLE|FALSE",
                "confidence": 0.0-1.0,
                "evidence_summary": "Brief summary of evidence",
                "source_types": ["academic", "government", "news", "expert"],
                "reliability_assessment": "HIGH|MEDIUM|LOW"
            }}
            """
            
            response = self.model.generate_content(fact_check_prompt)
            
            # Parse response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                return FactCheckResult(
                    claim=claim,
                    verification_status=result.get('verification_status', 'UNVERIFIABLE'),
                    evidence_sources=result.get('source_types', []),
                    confidence=result.get('confidence', 0.5),
                    explanation=result.get('evidence_summary', 'No detailed analysis available'),
                    last_updated=datetime.now().isoformat()
                )
            else:
                return self._create_basic_fact_check_result(claim)
                
        except Exception as e:
            logger.warning(f"⚠️ Fact-check failed for claim: {claim[:50]}... Error: {e}")
            return self._create_basic_fact_check_result(claim)
    
    def _create_basic_fact_check_result(self, claim: str) -> FactCheckResult:
        """Create basic fact-check result when AI fails"""
        return FactCheckResult(
            claim=claim,
            verification_status="UNVERIFIABLE",
            evidence_sources=["manual_review_needed"],
            confidence=0.5,
            explanation="Automated fact-checking unavailable, manual review recommended",
            last_updated=datetime.now().isoformat()
        )
    
    def _identify_sources(self, content: str) -> List[str]:
        """Identify potential sources mentioned in content"""
        sources = []
        
        # Pattern-based source detection
        source_patterns = [
            r'according\s+to\s+([^,\n.!?]+)',
            r'study\s+by\s+([^,\n.!?]+)',
            r'research\s+from\s+([^,\n.!?]+)',
            r'survey\s+by\s+([^,\n.!?]+)',
            r'report\s+from\s+([^,\n.!?]+)',
            r'data\s+from\s+([^,\n.!?]+)',
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            sources.extend([match.strip() for match in matches])
        
        return list(set(sources))
    
    def _evaluate_source_quality(self, sources: List[str]) -> float:
        """Evaluate the quality of identified sources"""
        if not sources:
            return 3.0  # Low score for no sources
        
        total_score = 0
        for source in sources:
            source_lower = source.lower()
            
            # Categorize source type
            if any(keyword in source_lower for keyword in ['university', 'college', 'institute', 'journal']):
                total_score += self.source_rankings['academic_journals']
            elif any(keyword in source_lower for keyword in ['government', 'agency', 'department']):
                total_score += self.source_rankings['government_agencies']
            elif any(keyword in source_lower for keyword in ['news', 'times', 'post', 'bbc', 'cnn']):
                total_score += self.source_rankings['news_organizations']
            elif any(keyword in source_lower for keyword in ['expert', 'professor', 'doctor']):
                total_score += self.source_rankings['expert_interviews']
            else:
                total_score += self.source_rankings['unknown']
        
        average_score = total_score / len(sources)
        logger.info(f"📊 Source quality score: {average_score:.1f}/10 ({len(sources)} sources)")
        return average_score
    
    def _analyze_bias(self, content: str, topic: str) -> Dict[str, Any]:
        """Analyze content for potential bias"""
        try:
            if not self.model:
                return self._simple_bias_analysis(content)
            
            bias_analysis_prompt = f"""
            Analyze this content for potential bias in relation to the topic:
            
            Content: "{content}"
            Topic: "{topic}"
            
            Check for:
            1. Language bias (loaded words, emotional language)
            2. Selection bias (cherry-picking facts)
            3. Confirmation bias (one-sided presentation)
            4. Cultural or demographic bias
            5. Commercial bias (promoting products/services)
            
            Return JSON:
            {{
                "bias_score": 0.0-10.0,
                "bias_types": ["language", "selection", "confirmation", "cultural", "commercial"],
                "bias_indicators": ["specific examples of biased language/presentation"],
                "neutrality_suggestions": ["how to make content more neutral"],
                "overall_assessment": "LOW|MEDIUM|HIGH bias level"
            }}
            """
            
            response = self.model.generate_content(bias_analysis_prompt)
            
            # Parse response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(f"🎯 Bias analysis complete: {result.get('overall_assessment', 'UNKNOWN')} bias level")
                return result
            else:
                return self._simple_bias_analysis(content)
                
        except Exception as e:
            logger.warning(f"⚠️ Bias analysis failed: {e}")
            return self._simple_bias_analysis(content)
    
    def _simple_bias_analysis(self, content: str) -> Dict[str, Any]:
        """Simple pattern-based bias detection"""
        bias_score = 5.0  # Neutral starting point
        bias_indicators = []
        
        # Check for loaded language
        loaded_words = ['amazing', 'terrible', 'best', 'worst', 'incredible', 'awful', 'perfect', 'disaster']
        loaded_count = sum(1 for word in loaded_words if word in content.lower())
        
        if loaded_count > 3:
            bias_score += 2.0
            bias_indicators.append("High use of emotionally loaded language")
        
        # Check for absolute statements
        absolute_patterns = [r'\ball\b', r'\bnever\b', r'\balways\b', r'\beveryone\b', r'\bno one\b']
        absolute_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in absolute_patterns)
        
        if absolute_count > 2:
            bias_score += 1.5
            bias_indicators.append("Frequent use of absolute statements")
        
        return {
            "bias_score": min(10.0, bias_score),
            "bias_types": ["language"] if bias_indicators else [],
            "bias_indicators": bias_indicators,
            "neutrality_suggestions": ["Use more neutral language", "Include multiple perspectives"],
            "overall_assessment": "HIGH" if bias_score > 7 else "MEDIUM" if bias_score > 5 else "LOW"
        }
    
    def _calculate_credibility_score(self, fact_check_results: List[FactCheckResult], 
                                   source_quality: float, bias_analysis: Dict[str, Any]) -> CredibilityScore:
        """Calculate overall credibility score"""
        
        # Calculate factual accuracy score
        if fact_check_results:
            verified_claims = sum(1 for result in fact_check_results if result.verification_status == "VERIFIED")
            false_claims = sum(1 for result in fact_check_results if result.verification_status == "FALSE")
            total_claims = len(fact_check_results)
            
            factual_accuracy = ((verified_claims * 10 - false_claims * 5) / total_claims) if total_claims > 0 else 5.0
            factual_accuracy = max(0, min(10, factual_accuracy))
        else:
            factual_accuracy = 6.0  # Neutral when no claims to check
        
        # Bias level (invert so lower is better)
        bias_level = bias_analysis.get('bias_score', 5.0)
        
        # Evidence strength based on verification confidence
        if fact_check_results:
            avg_confidence = sum(result.confidence for result in fact_check_results) / len(fact_check_results)
            evidence_strength = avg_confidence * 10
        else:
            evidence_strength = 5.0
        
        # Overall score calculation (weighted average)
        overall_score = (
            factual_accuracy * 0.35 +  # 35% weight on factual accuracy
            source_quality * 0.25 +    # 25% weight on source quality
            evidence_strength * 0.25 + # 25% weight on evidence strength
            (10 - bias_level) * 0.15   # 15% weight on low bias (inverted)
        )
        
        # Determine confidence level
        if overall_score >= 8.5:
            confidence_level = "HIGH"
        elif overall_score >= 6.5:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        # Generate issues and suggestions
        issues_detected = []
        improvement_suggestions = []
        
        if factual_accuracy < 7.0:
            issues_detected.append("Low factual accuracy")
            improvement_suggestions.append("Verify claims with reliable sources")
        
        if source_quality < 6.0:
            issues_detected.append("Poor source quality")
            improvement_suggestions.append("Use more credible sources")
        
        if bias_level > 7.0:
            issues_detected.append("High bias detected")
            improvement_suggestions.append("Use more neutral language and balanced perspectives")
        
        return CredibilityScore(
            overall_score=round(overall_score, 1),
            factual_accuracy=round(factual_accuracy, 1),
            source_quality=round(source_quality, 1),
            bias_level=round(bias_level, 1),
            evidence_strength=round(evidence_strength, 1),
            claims_verified=len([r for r in fact_check_results if r.verification_status == "VERIFIED"]),
            sources_found=len(set(result.evidence_sources[0] if result.evidence_sources else "none" 
                                for result in fact_check_results)),
            confidence_level=confidence_level,
            verification_timestamp=datetime.now().isoformat(),
            issues_detected=issues_detected,
            improvement_suggestions=improvement_suggestions
        )
    
    def _create_fallback_score(self, content: str) -> CredibilityScore:
        """Create fallback credibility score when AI analysis fails"""
        return CredibilityScore(
            overall_score=6.0,
            factual_accuracy=6.0,
            source_quality=5.0,
            bias_level=5.0,
            evidence_strength=5.0,
            claims_verified=0,
            sources_found=0,
            confidence_level="MEDIUM",
            verification_timestamp=datetime.now().isoformat(),
            issues_detected=["AI analysis unavailable"],
            improvement_suggestions=["Manual review recommended"]
        )
    
    def get_credibility_assessment(self, score: CredibilityScore) -> str:
        """Get human-readable credibility assessment"""
        if score.overall_score >= self.credibility_thresholds["excellent"]:
            return "EXCELLENT - Highly credible content with strong evidence"
        elif score.overall_score >= self.credibility_thresholds["good"]:
            return "GOOD - Credible content with adequate support"
        elif score.overall_score >= self.credibility_thresholds["acceptable"]:
            return "ACCEPTABLE - Moderately credible, some improvements needed"
        elif score.overall_score >= self.credibility_thresholds["questionable"]:
            return "QUESTIONABLE - Significant credibility concerns"
        else:
            return "POOR - Low credibility, major issues detected"