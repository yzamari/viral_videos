"""
Image Timing Agent - AI-powered intelligent image display duration decisions
Analyzes content and determines optimal timing for each image in video generation
"""

import google.generativeai as genai
from typing import Dict, Any, List
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageTimingAgent:
    """
    AI Agent specialized in analyzing content and determining optimal
    image display durations for video generation
    """

    def __init__(self, api_key: str):
        """Initialize the Image Timing Agent"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Agent personality and expertise
        self.agent_profile = {
            'name': 'TimingMaster',
            'role': 'Image Display Timing Specialist',
            'expertise': [
                'Content complexity analysis',
                'Reading time optimization',
                'Attention span management',
                'Platform-specific timing preferences',
                'Visual information processing speeds'
            ],
            'timing_factors': [
                'Text density and readability',
                'Visual complexity and detail',
                'Information processing requirements',
                'Platform user behavior patterns',
                'Content type and purpose'
            ]
        }

    def analyze_image_timing_requirements(self, 
                                        prompts: List[Dict[str, Any]], 
                                        platform: str, 
                                        total_duration: float,
                                        category: str = "general") -> Dict[str, Any]:
        """
        Analyze content and determine optimal timing for each image
        
        Args:
            prompts: List of image prompts with descriptions
            platform: Target platform (tiktok, youtube, instagram, etc.)
            total_duration: Total video duration in seconds
            category: Content category for context
            
        Returns:
            Dictionary with timing decisions for each image
        """
        logger.info(f"⏱️ TimingMaster analyzing image timing for {len(prompts)} images")
        
        try:
            # Create comprehensive analysis prompt
            analysis_prompt = f"""
You are TimingMaster, an expert AI agent specializing in image display timing optimization for video content.

ANALYZE THESE IMAGE PROMPTS FOR OPTIMAL TIMING:

Content Details:
- Number of images: {len(prompts)}
- Platform: {platform}
- Total duration: {total_duration} seconds
- Category: {category}

Image Prompts:
{json.dumps([{"index": i, "prompt": prompt.get('description', prompt.get('veo2_prompt', 'Unknown'))} for i, prompt in enumerate(prompts)], indent=2)}

TIMING ANALYSIS FACTORS:

1. CONTENT COMPLEXITY ANALYSIS:
   - Text-heavy content: Needs 2-4 seconds for reading
   - Visual-only content: Can be faster, 1-2 seconds
   - Complex scenes: Need 3-5 seconds for processing
   - Simple graphics: Can be quick, 0.8-1.5 seconds

2. PLATFORM OPTIMIZATION:
   - TikTok: Fast-paced, 0.8-2 seconds per image
   - YouTube: More flexible, 1.5-4 seconds per image
   - Instagram: Aesthetic focus, 2-3 seconds per image
   - Twitter: Quick consumption, 1-2 seconds per image

3. INFORMATION PROCESSING:
   - News/Facts: Longer duration for comprehension
   - Entertainment: Faster pace for engagement
   - Educational: Balanced timing for learning
   - Comedy: Quick timing for punchlines

4. USER ATTENTION PATTERNS:
   - First image: Can be longer (hook)
   - Middle images: Balanced timing
   - Last image: Slightly longer (conclusion)

5. READING TIME CALCULATIONS:
   - Average reading speed: 200-250 words per minute
   - Visual processing: 0.5-1 second base time
   - Complex visuals: Add 1-2 seconds
   - Text overlay: Add reading time

PROVIDE DETAILED TIMING DECISIONS:

For each image, decide:
- Display duration (in seconds)
- Reasoning for the timing
- Content type classification
- Attention requirements

Respond in JSON format:
{{
    "timing_strategy": "overall approach description",
    "total_calculated_duration": number,
    "average_duration_per_image": number,
    "platform_optimization": "platform-specific adjustments",
    "image_timings": [
        {{
            "image_index": 0,
            "duration": number_in_seconds,
            "content_type": "text_heavy/visual_only/complex_scene/simple_graphic",
            "complexity_level": "low/medium/high",
            "reading_time_required": number_in_seconds,
            "processing_time_required": number_in_seconds,
            "attention_weight": "high/medium/low",
            "timing_rationale": "detailed explanation of timing decision"
        }}
    ],
    "timing_adjustments": {{
        "first_image_bonus": number_in_seconds,
        "last_image_bonus": number_in_seconds,
        "complex_content_bonus": number_in_seconds
    }},
    "user_experience_optimization": "how timing enhances user experience"
}}
"""

            # Get AI analysis
            response = self.model.generate_content(analysis_prompt)
            
            # Parse response
            response_text = response.text.strip()
            
            # Clean up response (remove markdown formatting if present)
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            timing_analysis = json.loads(response_text)
            
            # Validate and adjust timing analysis
            timing_analysis = self._validate_timing_analysis(timing_analysis, total_duration, len(prompts))
            
            # Add agent metadata
            timing_analysis['agent_name'] = 'TimingMaster'
            timing_analysis['analysis_timestamp'] = datetime.now().isoformat()
            timing_analysis['total_images'] = len(prompts)
            timing_analysis['platform'] = platform
            
            logger.info(f"✅ TimingMaster analysis complete:")
            logger.info(f"   Strategy: {timing_analysis.get('timing_strategy', 'N/A')}")
            logger.info(f"   Avg duration per image: {timing_analysis.get('average_duration_per_image', 0):.2f}s")
            logger.info(f"   Total calculated: {timing_analysis.get('total_calculated_duration', 0):.2f}s")
            
            return timing_analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse TimingMaster response: {e}")
            return self._create_fallback_timing_analysis(prompts, platform, total_duration)
        except Exception as e:
            logger.error(f"TimingMaster analysis failed: {e}")
            return self._create_fallback_timing_analysis(prompts, platform, total_duration)

    def _validate_timing_analysis(self, analysis: Dict[str, Any], target_duration: float, num_images: int) -> Dict[str, Any]:
        """Validate and adjust timing analysis to fit constraints"""
        
        # Ensure image_timings exists
        if 'image_timings' not in analysis:
            analysis['image_timings'] = []
        
        # Calculate total duration from individual timings
        total_from_timings = sum(img.get('duration', 1.0) for img in analysis['image_timings'])
        
        # If total is significantly different from target, adjust proportionally
        if abs(total_from_timings - target_duration) > 2.0:  # More than 2 seconds difference
            adjustment_factor = target_duration / total_from_timings if total_from_timings > 0 else 1.0
            
            logger.info(f"📊 Adjusting timing: {total_from_timings:.2f}s -> {target_duration:.2f}s (factor: {adjustment_factor:.2f})")
            
            # Apply adjustment to each image
            for img_timing in analysis['image_timings']:
                original_duration = img_timing.get('duration', 1.0)
                adjusted_duration = original_duration * adjustment_factor
                
                # Ensure minimum and maximum bounds
                adjusted_duration = max(0.5, min(8.0, adjusted_duration))  # Between 0.5 and 8 seconds
                
                img_timing['duration'] = round(adjusted_duration, 2)
                
                # Update rationale
                if 'timing_rationale' in img_timing:
                    img_timing['timing_rationale'] += f" (Adjusted by {adjustment_factor:.2f} to fit {target_duration}s total)"
        
        # Recalculate totals
        analysis['total_calculated_duration'] = sum(img.get('duration', 1.0) for img in analysis['image_timings'])
        analysis['average_duration_per_image'] = analysis['total_calculated_duration'] / num_images if num_images > 0 else 1.0
        
        return analysis

    def _create_fallback_timing_analysis(self, prompts: List[Dict[str, Any]], platform: str, total_duration: float) -> Dict[str, Any]:
        """Create fallback timing analysis when AI analysis fails"""
        
        logger.info("🔄 Using fallback heuristics for image timing")
        
        num_images = len(prompts)
        
        # Platform-based base timing
        if platform.lower() == 'tiktok':
            base_duration = 1.2  # Fast-paced
        elif platform.lower() == 'youtube':
            base_duration = 2.0  # More relaxed
        elif platform.lower() == 'instagram':
            base_duration = 1.8  # Aesthetic focus
        else:
            base_duration = 1.5  # General default
        
        # Adjust to fit total duration
        target_avg = total_duration / num_images if num_images > 0 else base_duration
        actual_duration = min(max(target_avg, 0.8), 4.0)  # Clamp between 0.8 and 4 seconds
        
        # Create timing for each image
        image_timings = []
        for i, prompt in enumerate(prompts):
            # Slight variation for natural feel
            variation = 0.2 if i % 2 == 0 else -0.2
            duration = max(0.5, actual_duration + variation)
            
            # First and last images get slight bonus
            if i == 0 or i == len(prompts) - 1:
                duration += 0.3
            
            image_timings.append({
                "image_index": i,
                "duration": round(duration, 2),
                "content_type": "mixed_content",
                "complexity_level": "medium",
                "reading_time_required": 0.5,
                "processing_time_required": 0.5,
                "attention_weight": "medium",
                "timing_rationale": f"Fallback timing for {platform} platform"
            })
        
        total_calculated = sum(img['duration'] for img in image_timings)
        
        return {
            'timing_strategy': f'Fallback platform-optimized timing for {platform}',
            'total_calculated_duration': total_calculated,
            'average_duration_per_image': total_calculated / num_images,
            'platform_optimization': f'Optimized for {platform} user behavior',
            'image_timings': image_timings,
            'timing_adjustments': {
                'first_image_bonus': 0.3,
                'last_image_bonus': 0.3,
                'complex_content_bonus': 0.0
            },
            'user_experience_optimization': 'Balanced timing for optimal engagement',
            'agent_name': 'TimingMaster (Fallback)',
            'analysis_timestamp': datetime.now().isoformat(),
            'total_images': num_images,
            'platform': platform
        }

    def get_timing_for_image(self, image_index: int, timing_analysis: Dict[str, Any]) -> float:
        """Get the timing for a specific image from the analysis"""
        
        image_timings = timing_analysis.get('image_timings', [])
        
        if image_index < len(image_timings):
            return image_timings[image_index].get('duration', 1.5)
        else:
            # Fallback to average
            return timing_analysis.get('average_duration_per_image', 1.5)

    def create_ffmpeg_timing_list(self, timing_analysis: Dict[str, Any], image_paths: List[str]) -> List[Dict[str, Any]]:
        """Create a list of timing instructions for FFmpeg"""
        
        timing_list = []
        
        for i, image_path in enumerate(image_paths):
            duration = self.get_timing_for_image(i, timing_analysis)
            
            timing_list.append({
                'image_path': image_path,
                'duration': duration,
                'image_index': i
            })
        
        return timing_list 