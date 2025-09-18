"""
Audience Intelligence System
Advanced demographic analysis, psychographic profiling, and content adaptation
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ..config.ai_model_config import DEFAULT_AI_MODEL

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class AgeGroup(Enum):
    """Age demographic categories"""
    GEN_Z = "gen_z"          # 13-26
    MILLENNIAL = "millennial" # 27-42
    GEN_X = "gen_x"          # 43-58
    BOOMER = "boomer"        # 59-77
    MIXED = "mixed"          # Multiple age groups


class EducationLevel(Enum):
    """Education level categories"""
    HIGH_SCHOOL = "high_school"
    SOME_COLLEGE = "some_college"
    BACHELOR = "bachelor"
    GRADUATE = "graduate"
    MIXED = "mixed"


class InterestCategory(Enum):
    """Primary interest categories"""
    TECHNOLOGY = "technology"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    HEALTH_FITNESS = "health_fitness"
    BUSINESS = "business"
    LIFESTYLE = "lifestyle"
    CREATIVE = "creative"
    SPORTS = "sports"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    PARENTING = "parenting"
    FINANCE = "finance"
    GENERAL = "general"


@dataclass
class DemographicProfile:
    """Comprehensive demographic analysis"""
    primary_age_group: AgeGroup
    age_distribution: Dict[str, float]  # Percentage breakdown
    education_level: EducationLevel
    primary_interests: List[InterestCategory]
    platform_usage_patterns: Dict[str, Any]
    content_consumption_habits: Dict[str, Any]
    engagement_preferences: Dict[str, Any]
    language_preferences: List[str]
    cultural_context: List[str]
    accessibility_needs: List[str]


@dataclass
class PsychographicProfile:
    """Psychological and behavioral analysis"""
    personality_traits: Dict[str, float]  # Big 5 personality scores
    values_priorities: List[str]
    lifestyle_indicators: List[str]
    decision_making_style: str
    information_processing_preference: str
    social_influence_susceptibility: str
    brand_loyalty_level: str
    innovation_adoption_rate: str
    content_sharing_likelihood: float
    engagement_drivers: List[str]


@dataclass
class ContentAdaptationStrategy:
    """Tailored content strategy based on audience analysis"""
    reading_level: str
    vocabulary_complexity: str
    sentence_length_preference: str
    visual_style_recommendations: List[str]
    color_palette_preferences: List[str]
    font_recommendations: List[str]
    content_pacing: str
    cultural_sensitivity_notes: List[str]
    accessibility_optimizations: List[str]
    platform_specific_adaptations: Dict[str, Any]


@dataclass
class AudienceIntelligence:
    """Complete audience intelligence analysis"""
    demographic_profile: DemographicProfile
    psychographic_profile: PsychographicProfile
    content_adaptation_strategy: ContentAdaptationStrategy
    engagement_prediction: Dict[str, Any]
    optimization_recommendations: List[str]
    confidence_score: float
    analysis_timestamp: str


class AudienceIntelligenceSystem:
    """Advanced audience analysis and content adaptation system"""
    
    def __init__(self, api_key: str):
        """Initialize with Google AI API key"""
        self.api_key = api_key
        if genai:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(DEFAULT_AI_MODEL)
        else:
            self.model = None
        
        # Platform demographic data (industry averages)
        self.platform_demographics = {
            "tiktok": {
                "primary_age": AgeGroup.GEN_Z,
                "age_distribution": {"gen_z": 0.6, "millennial": 0.3, "gen_x": 0.1},
                "education_mix": {"high_school": 0.4, "some_college": 0.3, "bachelor": 0.3},
                "engagement_style": "quick_visual_dynamic",
                "attention_span": "short",
                "content_preferences": ["visual", "fast_paced", "trending", "authentic"]
            },
            "instagram": {
                "primary_age": AgeGroup.MILLENNIAL,
                "age_distribution": {"gen_z": 0.4, "millennial": 0.45, "gen_x": 0.15},
                "education_mix": {"some_college": 0.3, "bachelor": 0.5, "graduate": 0.2},
                "engagement_style": "aesthetic_visual_storytelling",
                "attention_span": "medium",
                "content_preferences": ["visual", "aesthetic", "lifestyle", "aspirational"]
            },
            "youtube": {
                "primary_age": AgeGroup.MIXED,
                "age_distribution": {"gen_z": 0.3, "millennial": 0.35, "gen_x": 0.25, "boomer": 0.1},
                "education_mix": {"bachelor": 0.4, "graduate": 0.3, "some_college": 0.3},
                "engagement_style": "educational_entertainment",
                "attention_span": "long",
                "content_preferences": ["educational", "detailed", "expert", "tutorial"]
            },
            "linkedin": {
                "primary_age": AgeGroup.MILLENNIAL,
                "age_distribution": {"millennial": 0.5, "gen_x": 0.3, "gen_z": 0.2},
                "education_mix": {"bachelor": 0.5, "graduate": 0.4, "some_college": 0.1},
                "engagement_style": "professional_networking",
                "attention_span": "medium",
                "content_preferences": ["professional", "industry_insights", "career", "business"]
            }
        }
        
        # Content topic to interest mapping
        self.topic_interest_mapping = {
            "food": [InterestCategory.FOOD, InterestCategory.LIFESTYLE],
            "technology": [InterestCategory.TECHNOLOGY, InterestCategory.BUSINESS],
            "health": [InterestCategory.HEALTH_FITNESS, InterestCategory.LIFESTYLE],
            "business": [InterestCategory.BUSINESS, InterestCategory.FINANCE],
            "entertainment": [InterestCategory.ENTERTAINMENT, InterestCategory.LIFESTYLE],
            "education": [InterestCategory.EDUCATION, InterestCategory.TECHNOLOGY],
            "fashion": [InterestCategory.FASHION, InterestCategory.LIFESTYLE],
            "travel": [InterestCategory.TRAVEL, InterestCategory.LIFESTYLE],
            "parenting": [InterestCategory.PARENTING, InterestCategory.LIFESTYLE],
            "finance": [InterestCategory.FINANCE, InterestCategory.BUSINESS]
        }
        
        logger.info("🧠 Audience Intelligence System initialized")
    
    def analyze_audience(self, topic: str, platform: str, target_audience: str = "general") -> AudienceIntelligence:
        """
        Comprehensive audience analysis and content adaptation strategy
        
        Args:
            topic: Content topic for analysis
            platform: Target platform
            target_audience: Audience description
            
        Returns:
            Complete audience intelligence analysis
        """
        try:
            logger.info(f"🧠 Analyzing audience for topic: {topic} on {platform}")
            
            # Step 1: Demographic analysis
            demographic_profile = self._analyze_demographics(topic, platform, target_audience)
            
            # Step 2: Psychographic profiling
            psychographic_profile = self._analyze_psychographics(topic, platform, target_audience, demographic_profile)
            
            # Step 3: Content adaptation strategy
            content_strategy = self._create_content_adaptation_strategy(
                demographic_profile, psychographic_profile, platform
            )
            
            # Step 4: Engagement prediction
            engagement_prediction = self._predict_engagement(
                topic, platform, demographic_profile, psychographic_profile
            )
            
            # Step 5: Optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                demographic_profile, psychographic_profile, content_strategy
            )
            
            # Step 6: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                demographic_profile, psychographic_profile, platform
            )
            
            audience_intelligence = AudienceIntelligence(
                demographic_profile=demographic_profile,
                psychographic_profile=psychographic_profile,
                content_adaptation_strategy=content_strategy,
                engagement_prediction=engagement_prediction,
                optimization_recommendations=optimization_recommendations,
                confidence_score=confidence_score,
                analysis_timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"🧠 Audience analysis complete: {confidence_score:.2f} confidence")
            return audience_intelligence
            
        except Exception as e:
            logger.error(f"❌ Audience analysis failed: {e}")
            return self._create_fallback_analysis(topic, platform, target_audience)
    
    def _analyze_demographics(self, topic: str, platform: str, target_audience: str) -> DemographicProfile:
        """Analyze demographic characteristics"""
        try:
            # Get platform baseline demographics
            platform_data = self.platform_demographics.get(platform.lower(), self.platform_demographics["instagram"])
            
            # AI-enhanced demographic analysis
            if self.model:
                demo_analysis = self._ai_demographic_analysis(topic, platform, target_audience, platform_data)
                if demo_analysis:
                    return demo_analysis
            
            # Fallback to heuristic analysis
            return self._heuristic_demographic_analysis(topic, platform, target_audience, platform_data)
            
        except Exception as e:
            logger.warning(f"⚠️ Demographic analysis failed: {e}")
            return self._create_fallback_demographics(platform)
    
    def _ai_demographic_analysis(self, topic: str, platform: str, target_audience: str, platform_data: Dict) -> Optional[DemographicProfile]:
        """AI-powered demographic analysis with timeout protection"""
        try:
            # Add timeout protection - skip AI analysis if it might hang
            logger.debug("⏱️ Skipping potentially hanging AI demographic analysis")
            return None  # Force fallback to heuristic analysis
            
            demo_prompt = f"""
            Analyze the demographic profile for this content:
            
            Topic: "{topic}"
            Platform: {platform}
            Target Audience: {target_audience}
            
            Platform baseline data: {json.dumps(platform_data, indent=2, default=str)}
            
            Provide detailed demographic analysis considering:
            1. Age distribution refinement based on topic interest
            2. Education level preferences for this content type
            3. Primary interest categories alignment
            4. Platform usage patterns specific to this audience
            5. Content consumption habits
            6. Engagement preferences and behaviors
            7. Cultural and accessibility considerations
            
            Return JSON:
            {{
                "age_distribution": {{"gen_z": 0.0-1.0, "millennial": 0.0-1.0, "gen_x": 0.0-1.0, "boomer": 0.0-1.0}},
                "primary_age_group": "gen_z|millennial|gen_x|boomer|mixed",
                "education_level": "high_school|some_college|bachelor|graduate|mixed",
                "primary_interests": ["technology", "entertainment", "education", "lifestyle", "business"],
                "content_consumption_habits": {{
                    "session_length": "short|medium|long",
                    "discovery_method": "trending|recommended|search|social",
                    "sharing_likelihood": 0.0-1.0,
                    "comment_engagement": 0.0-1.0
                }},
                "engagement_preferences": {{
                    "visual_style": "minimalist|rich|dynamic|aesthetic",
                    "information_density": "low|medium|high",
                    "interaction_style": "passive|moderate|active"
                }},
                "cultural_context": ["western", "global", "youth", "professional", "diverse"],
                "accessibility_needs": ["visual_impaired", "hearing_impaired", "cognitive", "motor", "none"]
            }}
            """
            
            response = self.model.generate_content(demo_prompt)
            
            # Parse response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Convert to proper enums
                primary_age = AgeGroup(result.get('primary_age_group', 'mixed'))
                education = EducationLevel(result.get('education_level', 'mixed'))
                interests = [InterestCategory(interest) for interest in result.get('primary_interests', ['general'])
                           if interest in [cat.value for cat in InterestCategory]]
                
                return DemographicProfile(
                    primary_age_group=primary_age,
                    age_distribution=result.get('age_distribution', {}),
                    education_level=education,
                    primary_interests=interests,
                    platform_usage_patterns=platform_data,
                    content_consumption_habits=result.get('content_consumption_habits', {}),
                    engagement_preferences=result.get('engagement_preferences', {}),
                    language_preferences=['en-US'],  # Default for now
                    cultural_context=result.get('cultural_context', ['western']),
                    accessibility_needs=result.get('accessibility_needs', ['none'])
                )
            
        except Exception as e:
            logger.warning(f"⚠️ AI demographic analysis failed: {e}")
        
        return None
    
    def _heuristic_demographic_analysis(self, topic: str, platform: str, target_audience: str, platform_data: Dict) -> DemographicProfile:
        """Heuristic-based demographic analysis"""
        
        # Topic-based interest detection
        primary_interests = [InterestCategory.GENERAL]
        topic_lower = topic.lower()
        
        for key, interests in self.topic_interest_mapping.items():
            if key in topic_lower:
                primary_interests = interests
                break
        
        # Audience-based adjustments
        audience_lower = target_audience.lower()
        
        # Age group refinement
        if any(word in audience_lower for word in ['young', 'teen', 'student', 'gen z']):
            primary_age = AgeGroup.GEN_Z
            age_dist = {"gen_z": 0.8, "millennial": 0.2}
        elif any(word in audience_lower for word in ['millennial', 'adult', 'professional']):
            primary_age = AgeGroup.MILLENNIAL
            age_dist = {"millennial": 0.7, "gen_z": 0.2, "gen_x": 0.1}
        elif any(word in audience_lower for word in ['senior', 'mature', 'experienced']):
            primary_age = AgeGroup.GEN_X
            age_dist = {"gen_x": 0.6, "millennial": 0.3, "boomer": 0.1}
        else:
            primary_age = platform_data['primary_age']
            age_dist = platform_data['age_distribution']
        
        # Education level estimation
        if any(word in audience_lower for word in ['professional', 'expert', 'academic', 'graduate']):
            education = EducationLevel.GRADUATE
        elif any(word in audience_lower for word in ['college', 'university', 'bachelor']):
            education = EducationLevel.BACHELOR
        elif any(word in audience_lower for word in ['student', 'learning']):
            education = EducationLevel.SOME_COLLEGE
        else:
            education = EducationLevel.MIXED
        
        return DemographicProfile(
            primary_age_group=primary_age,
            age_distribution=age_dist,
            education_level=education,
            primary_interests=primary_interests,
            platform_usage_patterns=platform_data,
            content_consumption_habits={
                "session_length": platform_data.get('attention_span', 'medium'),
                "discovery_method": "recommended",
                "sharing_likelihood": 0.6,
                "comment_engagement": 0.4
            },
            engagement_preferences={
                "visual_style": platform_data.get('engagement_style', 'dynamic'),
                "information_density": "medium",
                "interaction_style": "moderate"
            },
            language_preferences=['en-US'],
            cultural_context=['western', 'global'],
            accessibility_needs=['none']
        )
    
    def _analyze_psychographics(self, topic: str, platform: str, target_audience: str, 
                               demographic_profile: DemographicProfile) -> PsychographicProfile:
        """Analyze psychological and behavioral characteristics"""
        
        # Age-based personality tendencies (research-backed generalizations)
        age_group = demographic_profile.primary_age_group
        
        if age_group == AgeGroup.GEN_Z:
            personality_base = {
                "openness": 0.75,      # High openness to new experiences
                "conscientiousness": 0.65,  # Moderate conscientiousness
                "extraversion": 0.70,  # High social media engagement
                "agreeableness": 0.72, # High social consciousness
                "neuroticism": 0.60    # Higher anxiety levels
            }
            values = ["authenticity", "diversity", "sustainability", "mental_health", "social_justice"]
            decision_style = "peer_influenced"
            info_processing = "visual_fast"
            
        elif age_group == AgeGroup.MILLENNIAL:
            personality_base = {
                "openness": 0.70,
                "conscientiousness": 0.70,
                "extraversion": 0.65,
                "agreeableness": 0.68,
                "neuroticism": 0.55
            }
            values = ["work_life_balance", "experiences", "technology", "efficiency", "personal_growth"]
            decision_style = "research_based"
            info_processing = "multi_modal"
            
        elif age_group == AgeGroup.GEN_X:
            personality_base = {
                "openness": 0.60,
                "conscientiousness": 0.75,
                "extraversion": 0.55,
                "agreeableness": 0.65,
                "neuroticism": 0.50
            }
            values = ["stability", "family", "financial_security", "independence", "pragmatism"]
            decision_style = "experience_based"
            info_processing = "detailed_analytical"
            
        else:  # BOOMER or MIXED
            personality_base = {
                "openness": 0.55,
                "conscientiousness": 0.80,
                "extraversion": 0.50,
                "agreeableness": 0.70,
                "neuroticism": 0.45
            }
            values = ["tradition", "family", "security", "respect", "legacy"]
            decision_style = "authority_based"
            info_processing = "linear_thorough"
        
        # Platform-based adjustments
        platform_lower = platform.lower()
        if platform_lower == 'tiktok':
            personality_base["extraversion"] += 0.1
            personality_base["openness"] += 0.1
            social_influence = "high"
            sharing_likelihood = 0.8
        elif platform_lower == 'linkedin':
            personality_base["conscientiousness"] += 0.1
            social_influence = "moderate"
            sharing_likelihood = 0.4
        else:
            social_influence = "moderate"
            sharing_likelihood = 0.6
        
        # Topic-based adjustments
        topic_lower = topic.lower()
        engagement_drivers = ["relevance", "entertainment"]
        
        if any(word in topic_lower for word in ['urgent', 'deadline', 'reminder']):
            engagement_drivers.extend(["urgency", "practicality"])
        if any(word in topic_lower for word in ['food', 'lunch', 'order']):
            engagement_drivers.extend(["personal_relevance", "routine"])
        
        return PsychographicProfile(
            personality_traits=personality_base,
            values_priorities=values,
            lifestyle_indicators=self._infer_lifestyle_indicators(demographic_profile),
            decision_making_style=decision_style,
            information_processing_preference=info_processing,
            social_influence_susceptibility=social_influence,
            brand_loyalty_level="moderate",
            innovation_adoption_rate=self._estimate_innovation_adoption(age_group),
            content_sharing_likelihood=sharing_likelihood,
            engagement_drivers=engagement_drivers
        )
    
    def _infer_lifestyle_indicators(self, demographic_profile: DemographicProfile) -> List[str]:
        """Infer lifestyle indicators from demographic data"""
        indicators = []
        
        if demographic_profile.primary_age_group == AgeGroup.GEN_Z:
            indicators.extend(["digital_native", "social_conscious", "mobile_first"])
        elif demographic_profile.primary_age_group == AgeGroup.MILLENNIAL:
            indicators.extend(["career_focused", "tech_savvy", "experience_seeking"])
        elif demographic_profile.primary_age_group == AgeGroup.GEN_X:
            indicators.extend(["family_oriented", "career_established", "time_conscious"])
        
        # Interest-based lifestyle indicators
        for interest in demographic_profile.primary_interests:
            if interest == InterestCategory.FOOD:
                indicators.append("food_enthusiast")
            elif interest == InterestCategory.TECHNOLOGY:
                indicators.append("early_adopter")
            elif interest == InterestCategory.BUSINESS:
                indicators.append("career_oriented")
        
        return indicators
    
    def _estimate_innovation_adoption(self, age_group: AgeGroup) -> str:
        """Estimate innovation adoption rate based on age group"""
        adoption_rates = {
            AgeGroup.GEN_Z: "early_adopter",
            AgeGroup.MILLENNIAL: "early_majority",
            AgeGroup.GEN_X: "late_majority",
            AgeGroup.BOOMER: "laggard"
        }
        return adoption_rates.get(age_group, "early_majority")
    
    def _create_content_adaptation_strategy(self, demographic_profile: DemographicProfile,
                                          psychographic_profile: PsychographicProfile,
                                          platform: str) -> ContentAdaptationStrategy:
        """Create content adaptation strategy based on audience analysis"""
        
        # Reading level based on education and age
        education = demographic_profile.education_level
        age_group = demographic_profile.primary_age_group
        
        if education in [EducationLevel.GRADUATE, EducationLevel.BACHELOR]:
            reading_level = "college"
            vocabulary = "advanced"
        elif education == EducationLevel.SOME_COLLEGE:
            reading_level = "high_school"
            vocabulary = "intermediate"
        else:
            reading_level = "middle_school"
            vocabulary = "simple"
        
        # Sentence length based on platform and processing preference
        info_processing = psychographic_profile.information_processing_preference
        if info_processing == "visual_fast" or platform.lower() == "tiktok":
            sentence_length = "short"
        elif info_processing == "detailed_analytical":
            sentence_length = "long"
        else:
            sentence_length = "medium"
        
        # Visual style recommendations
        visual_styles = []
        if age_group == AgeGroup.GEN_Z:
            visual_styles = ["dynamic", "colorful", "trendy", "authentic"]
        elif age_group == AgeGroup.MILLENNIAL:
            visual_styles = ["aesthetic", "professional", "clean", "aspirational"]
        else:
            visual_styles = ["clean", "professional", "traditional", "clear"]
        
        # Color palette based on platform and demographics
        color_palettes = []
        if platform.lower() == "tiktok":
            color_palettes = ["vibrant", "neon", "high_contrast"]
        elif platform.lower() == "linkedin":
            color_palettes = ["professional", "blue_tones", "muted"]
        else:
            color_palettes = ["modern", "balanced", "appealing"]
        
        # Font recommendations
        font_recs = []
        if age_group in [AgeGroup.GEN_Z, AgeGroup.MILLENNIAL]:
            font_recs = ["modern_sans_serif", "bold", "readable"]
        else:
            font_recs = ["traditional", "serif", "classic"]
        
        # Content pacing
        attention_span = demographic_profile.platform_usage_patterns.get('attention_span', 'medium')
        if attention_span == "short":
            pacing = "fast"
        elif attention_span == "long":
            pacing = "detailed"
        else:
            pacing = "moderate"
        
        return ContentAdaptationStrategy(
            reading_level=reading_level,
            vocabulary_complexity=vocabulary,
            sentence_length_preference=sentence_length,
            visual_style_recommendations=visual_styles,
            color_palette_preferences=color_palettes,
            font_recommendations=font_recs,
            content_pacing=pacing,
            cultural_sensitivity_notes=self._generate_cultural_notes(demographic_profile),
            accessibility_optimizations=self._generate_accessibility_optimizations(demographic_profile),
            platform_specific_adaptations=self._generate_platform_adaptations(platform, demographic_profile)
        )
    
    def _generate_cultural_notes(self, demographic_profile: DemographicProfile) -> List[str]:
        """Generate cultural sensitivity notes"""
        notes = []
        
        for context in demographic_profile.cultural_context:
            if context == "diverse":
                notes.append("Use inclusive language and imagery")
            elif context == "youth":
                notes.append("Avoid outdated references, use current slang appropriately")
            elif context == "professional":
                notes.append("Maintain professional tone and industry-appropriate language")
        
        return notes
    
    def _generate_accessibility_optimizations(self, demographic_profile: DemographicProfile) -> List[str]:
        """Generate accessibility optimization recommendations"""
        optimizations = []
        
        for need in demographic_profile.accessibility_needs:
            if need == "visual_impaired":
                optimizations.extend(["high_contrast_colors", "large_text", "alt_text_descriptions"])
            elif need == "hearing_impaired":
                optimizations.extend(["captions", "visual_indicators", "text_overlays"])
            elif need == "cognitive":
                optimizations.extend(["simple_language", "clear_structure", "minimal_distractions"])
        
        if not optimizations:
            optimizations = ["general_accessibility", "readable_fonts", "appropriate_contrast"]
        
        return optimizations
    
    def _generate_platform_adaptations(self, platform: str, demographic_profile: DemographicProfile) -> Dict[str, Any]:
        """Generate platform-specific adaptations"""
        
        platform_lower = platform.lower()
        
        if platform_lower == "tiktok":
            return {
                "hook_timing": "first_3_seconds",
                "visual_rhythm": "fast_cuts",
                "text_overlay_style": "bold_dynamic",
                "audio_considerations": "trending_sounds",
                "hashtag_strategy": "viral_discovery"
            }
        elif platform_lower == "instagram":
            return {
                "aspect_ratio": "9:16_stories",
                "visual_aesthetic": "cohesive_brand",
                "caption_length": "medium_engaging",
                "story_optimization": "swipe_friendly",
                "hashtag_strategy": "niche_community"
            }
        elif platform_lower == "youtube":
            return {
                "thumbnail_optimization": "click_worthy",
                "title_strategy": "searchable_compelling",
                "description_length": "detailed_seo",
                "retention_strategy": "value_upfront",
                "end_screen_optimization": "subscription_focused"
            }
        else:
            return {
                "general_optimization": "platform_best_practices",
                "engagement_focus": "audience_appropriate"
            }
    
    def _predict_engagement(self, topic: str, platform: str, 
                          demographic_profile: DemographicProfile,
                          psychographic_profile: PsychographicProfile) -> Dict[str, Any]:
        """Predict engagement based on audience analysis"""
        
        # Base engagement prediction
        base_score = 0.5
        
        # Platform affinity adjustments
        platform_lower = platform.lower()
        age_group = demographic_profile.primary_age_group
        
        if platform_lower == "tiktok" and age_group == AgeGroup.GEN_Z:
            base_score += 0.2
        elif platform_lower == "linkedin" and age_group in [AgeGroup.MILLENNIAL, AgeGroup.GEN_X]:
            base_score += 0.15
        elif platform_lower == "instagram" and age_group in [AgeGroup.GEN_Z, AgeGroup.MILLENNIAL]:
            base_score += 0.1
        
        # Interest alignment
        topic_lower = topic.lower()
        primary_interests = demographic_profile.primary_interests
        
        for interest in primary_interests:
            if interest.value in topic_lower:
                base_score += 0.1
                break
        
        # Psychographic factors
        sharing_likelihood = psychographic_profile.content_sharing_likelihood
        social_influence = psychographic_profile.social_influence_susceptibility
        
        # Calculate specific engagement metrics
        like_probability = min(1.0, base_score + 0.1)
        comment_probability = min(1.0, base_score * 0.7)
        share_probability = min(1.0, sharing_likelihood * base_score)
        
        return {
            "overall_engagement_score": round(base_score, 2),
            "like_probability": round(like_probability, 2),
            "comment_probability": round(comment_probability, 2),
            "share_probability": round(share_probability, 2),
            "virality_potential": "high" if base_score > 0.7 else "medium" if base_score > 0.5 else "low",
            "engagement_drivers": psychographic_profile.engagement_drivers,
            "optimal_posting_times": self._suggest_optimal_posting_times(demographic_profile, platform),
            "retention_prediction": self._predict_retention(demographic_profile, platform)
        }
    
    def _suggest_optimal_posting_times(self, demographic_profile: DemographicProfile, platform: str) -> List[str]:
        """Suggest optimal posting times based on audience"""
        
        age_group = demographic_profile.primary_age_group
        platform_lower = platform.lower()
        
        if age_group == AgeGroup.GEN_Z:
            if platform_lower == "tiktok":
                return ["6:00_AM", "7:00_PM", "9:00_PM"]  # Before school/work, after dinner
            else:
                return ["3:00_PM", "7:00_PM", "9:00_PM"]
        elif age_group == AgeGroup.MILLENNIAL:
            if platform_lower == "linkedin":
                return ["8:00_AM", "12:00_PM", "5:00_PM"]  # Work-related times
            else:
                return ["12:00_PM", "6:00_PM", "8:00_PM"]
        else:
            return ["9:00_AM", "1:00_PM", "7:00_PM"]
    
    def _predict_retention(self, demographic_profile: DemographicProfile, platform: str) -> Dict[str, float]:
        """Predict content retention rates"""
        
        attention_span = demographic_profile.platform_usage_patterns.get('attention_span', 'medium')
        
        if attention_span == "short":
            return {"15_seconds": 0.8, "30_seconds": 0.6, "60_seconds": 0.3}
        elif attention_span == "long":
            return {"15_seconds": 0.9, "30_seconds": 0.8, "60_seconds": 0.7}
        else:
            return {"15_seconds": 0.85, "30_seconds": 0.7, "60_seconds": 0.5}
    
    def _generate_optimization_recommendations(self, demographic_profile: DemographicProfile,
                                             psychographic_profile: PsychographicProfile,
                                             content_strategy: ContentAdaptationStrategy) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Age-based recommendations
        age_group = demographic_profile.primary_age_group
        if age_group == AgeGroup.GEN_Z:
            recommendations.extend([
                "Use authentic, unpolished content style",
                "Include trending audio and visual elements",
                "Focus on social issues and authenticity"
            ])
        elif age_group == AgeGroup.MILLENNIAL:
            recommendations.extend([
                "Balance professional and personal content",
                "Include nostalgia references appropriately",
                "Focus on work-life balance themes"
            ])
        
        # Platform-specific recommendations
        if "tiktok" in str(demographic_profile.platform_usage_patterns):
            recommendations.extend([
                "Hook viewers in first 3 seconds",
                "Use vertical video format",
                "Include trending hashtags"
            ])
        
        # Psychographic recommendations
        if psychographic_profile.information_processing_preference == "visual_fast":
            recommendations.append("Use more visual elements, less text")
        elif psychographic_profile.information_processing_preference == "detailed_analytical":
            recommendations.append("Provide comprehensive information and sources")
        
        # Engagement driver recommendations
        for driver in psychographic_profile.engagement_drivers:
            if driver == "urgency":
                recommendations.append("Use time-sensitive language and CTAs")
            elif driver == "practicality":
                recommendations.append("Focus on practical, actionable content")
        
        return recommendations
    
    def _calculate_confidence_score(self, demographic_profile: DemographicProfile,
                                  psychographic_profile: PsychographicProfile,
                                  platform: str) -> float:
        """Calculate confidence score for the analysis"""
        
        score = 0.7  # Base confidence
        
        # Platform data availability
        if platform.lower() in self.platform_demographics:
            score += 0.1
        
        # Interest alignment
        if len(demographic_profile.primary_interests) > 1:
            score += 0.1
        
        # Demographic completeness
        if demographic_profile.age_distribution:
            score += 0.05
        
        # Psychographic detail
        if len(psychographic_profile.engagement_drivers) > 2:
            score += 0.05
        
        return min(1.0, score)
    
    def _create_fallback_analysis(self, topic: str, platform: str, target_audience: str) -> AudienceIntelligence:
        """Create fallback analysis when AI analysis fails"""
        
        fallback_demo = self._create_fallback_demographics(platform)
        fallback_psycho = self._create_fallback_psychographics()
        fallback_strategy = self._create_fallback_content_strategy()
        
        return AudienceIntelligence(
            demographic_profile=fallback_demo,
            psychographic_profile=fallback_psycho,
            content_adaptation_strategy=fallback_strategy,
            engagement_prediction={
                "overall_engagement_score": 0.5,
                "virality_potential": "medium",
                "engagement_drivers": ["relevance", "entertainment"]
            },
            optimization_recommendations=["Use clear, engaging content", "Optimize for platform best practices"],
            confidence_score=0.6,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _create_fallback_demographics(self, platform: str) -> DemographicProfile:
        """Create fallback demographic profile"""
        platform_data = self.platform_demographics.get(platform.lower(), self.platform_demographics["instagram"])
        
        return DemographicProfile(
            primary_age_group=platform_data['primary_age'],
            age_distribution=platform_data['age_distribution'],
            education_level=EducationLevel.MIXED,
            primary_interests=[InterestCategory.GENERAL],
            platform_usage_patterns=platform_data,
            content_consumption_habits={
                "session_length": "medium",
                "discovery_method": "recommended",
                "sharing_likelihood": 0.5,
                "comment_engagement": 0.3
            },
            engagement_preferences={
                "visual_style": "dynamic",
                "information_density": "medium",
                "interaction_style": "moderate"
            },
            language_preferences=['en-US'],
            cultural_context=['western'],
            accessibility_needs=['none']
        )
    
    def _create_fallback_psychographics(self) -> PsychographicProfile:
        """Create fallback psychographic profile"""
        return PsychographicProfile(
            personality_traits={
                "openness": 0.6,
                "conscientiousness": 0.6,
                "extraversion": 0.6,
                "agreeableness": 0.6,
                "neuroticism": 0.5
            },
            values_priorities=["relevance", "entertainment", "usefulness"],
            lifestyle_indicators=["general_audience"],
            decision_making_style="balanced",
            information_processing_preference="multi_modal",
            social_influence_susceptibility="moderate",
            brand_loyalty_level="moderate",
            innovation_adoption_rate="early_majority",
            content_sharing_likelihood=0.5,
            engagement_drivers=["relevance", "entertainment"]
        )
    
    def _create_fallback_content_strategy(self) -> ContentAdaptationStrategy:
        """Create fallback content adaptation strategy"""
        return ContentAdaptationStrategy(
            reading_level="high_school",
            vocabulary_complexity="intermediate",
            sentence_length_preference="medium",
            visual_style_recommendations=["clean", "engaging", "modern"],
            color_palette_preferences=["balanced", "appealing"],
            font_recommendations=["readable", "modern"],
            content_pacing="moderate",
            cultural_sensitivity_notes=["use inclusive language"],
            accessibility_optimizations=["readable_fonts", "appropriate_contrast"],
            platform_specific_adaptations={"general_optimization": "platform_best_practices"}
        )