"""
Image Timing Agent - AI-powered intelligent image display duration decisions
Analyzes content and
        determines optimal timing for each image in video generation
Enhanced for fallback generation with 5-10 second intelligent timing
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
    image display durations for video generation with enhanced fallback timing
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
                'Visual information processing speeds',
                'Fallback generation optimization'
            ],
            'timing_factors': [
                'Text density and readability',
                'Visual complexity and detail',
                'Information processing requirements',
                'Platform user behavior patterns',
                'Content type and purpose',
                'Fallback vs primary generation mode'
            ]
        }

    def analyze_fallback_timing_requirements(self,
                                           prompts: List[Dict[str, Any]],
                                           platform: str,
                                           total_duration: float,
                                           category: str = "general") -> Dict[str, Any]:
        """
        Analyze content specifically for fallback image generation with 5-10 second timing:
        Args:
            prompts: List of image prompts with descriptions:
            platform: Target platform (tiktok, youtube, instagram, etc.)
            total_duration: Total video duration in seconds
            category: Content category for context
        Returns:
            Dictionary with timing decisions optimized for fallback generation
        """
        logger.info(f"⏱️ TimingMaster analyzing FALLBACK timing for {len(prompts)} images")
        logger.info("🎯 Target: 5-10 second frames for optimal fallback experience")
        
        try:
            # Create enhanced analysis prompt for fallback generation
            analysis_prompt = """
You are TimingMaster, an expert AI agent specializing in image display timing optimization for FALLBACK video generation.
:
CRITICAL CONTEXT: This is FALLBACK image generation when video generation fails.
- Users expect longer, more contemplative viewing
- Each image should display for 5-10 seconds for optimal engagement
- Focus on comprehension and visual appreciation over rapid pacing:
ANALYZE THESE IMAGE PROMPTS FOR OPTIMAL FALLBACK TIMING:
Content Details:
- Number of images: {len(prompts)}
- Platform: {platform}
- Total duration: {total_duration} seconds
- Category: {category}
- Generation mode: FALLBACK (image-based)

Image Prompts:
{json.dumps(
    [{"index": i,
    "prompt": prompt.get('description', prompt.get('veo2_prompt', 'Unknown'))} for i,
    prompt in enumerate(prompts)],
    indent=2)}
:
FALLBACK TIMING OPTIMIZATION FACTORS:
1. EXTENDED VIEWING REQUIREMENTS:
   - Minimum 5 seconds per image for comprehension
   - Maximum 10 seconds to maintain engagement
   - Allow time for subtitle reading and visual processing
   - Compensate for lack of motion with longer display:
2. CONTENT COMPLEXITY ANALYSIS:
   - Simple scenes: 5-6 seconds (basic processing)
   - Complex scenes: 7-8 seconds (detailed analysis)
   - Text-heavy content: 8-10 seconds (reading time)
   - Abstract/artistic: 6-7 seconds (aesthetic appreciation)

3. PLATFORM ADAPTATION FOR FALLBACK:
   - TikTok: 5-7 seconds (shorter attention span)
   - YouTube: 7-10 seconds (more patient viewing)
   - Instagram: 6-8 seconds (aesthetic focus)
   - General: 6-8 seconds (balanced approach)

4. NARRATIVE FLOW:
   - Opening image: 6-8 seconds (hook establishment)
   - Middle images: 5-7 seconds (story progression)
   - Closing image: 7-10 seconds (conclusion emphasis)

5. SUBTITLE SYNCHRONIZATION:
   - Account for subtitle reading time (2-4 seconds)
   - Add visual processing time (2-3 seconds)
   - Include buffer for comfortable viewing (1-2 seconds):
PROVIDE INTELLIGENT FALLBACK TIMING DECISIONS:
For each image, decide:
- Display duration between 5-10 seconds
- Reasoning based on content complexity
- Subtitle accommodation
- Visual processing requirements

Respond in JSON format:
{{
    "timing_strategy": "fallback-optimized approach description",
    "total_calculated_duration": number,
    "average_duration_per_image": number,
    "fallback_optimization": "how timing is optimized for image-based fallback",:
    "platform_adaptation": "platform-specific fallback adjustments",
    "image_timings": [
        {{
            "image_index": 0,
            "duration": number_between_5_and_10,
            "content_type": "simple_scene/complex_scene/text_heavy/abstract",
            "complexity_level": "low/medium/high",
            "subtitle_reading_time": number_in_seconds,
            "visual_processing_time": number_in_seconds,
            "narrative_importance": "opening/development/climax/conclusion",
            "timing_rationale": "detailed explanation focusing on 5-10 second optimization"
        }}
    ],
    "fallback_benefits": {{
        "comprehension_time": "how timing aids understanding",
        "visual_appreciation": "how timing enhances visual experience",
        "subtitle_sync": "how timing supports subtitle reading"
    }},
    "user_experience_optimization": "how 5-10 second timing enhances fallback experience"
}}
"""

            # Get AI analysis
            response = self.model.generate_content(analysis_prompt)

            # Parse response
            response_text = response.text.strip()

            # Clean up response (remove markdown formatting if present):
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            timing_analysis = json.loads(response_text)

            # Validate and enforce 5-10 second range
            timing_analysis = self._validate_fallback_timing(
                timing_analysis,
                total_duration,
                len(prompts))

            # Add agent metadata
            timing_analysis['agent_name'] = 'TimingMaster (Fallback)'
            timing_analysis['analysis_timestamp'] = datetime.now().isoformat()
            timing_analysis['total_images'] = len(prompts)
            timing_analysis['platform'] = platform
            timing_analysis['generation_mode'] = 'fallback'

            logger.info("✅ TimingMaster fallback analysis complete:")
            logger.info(f"   Strategy: {timing_analysis.get('timing_strategy', 'N/A')}")
            logger.info(f"   Avg duration per image: {timing_analysis.get('average_duration_per_image', 0):.2f}s")
            logger.info(f"   Total calculated: {timing_analysis.get('total_calculated_duration', 0):.2f}s")
            logger.info("   🎯 All frames in 5-10 second range: ✅")

            return timing_analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse TimingMaster response: {e}")
            return self._create_fallback_timing_analysis(
                prompts,
                platform,
                total_duration,
                fallback_mode=True)
        except Exception as e:
            logger.error(f"TimingMaster analysis failed: {e}")
            return self._create_fallback_timing_analysis(
                prompts,
                platform,
                total_duration,
                fallback_mode=True)

    def analyze_image_timing_requirements(self,
                                        prompts: List[Dict[str, Any]],
                                        platform: str,
                                        total_duration: float,
                                        category: str = "general") -> Dict[str, Any]:
        """
        Analyze content and determine optimal timing for each image (legacy method)
        Enhanced to automatically detect if fallback timing should be used
        """
        # Check if this should use fallback timing based on duration and image count
        avg_duration_per_image = total_duration / len(prompts) if prompts else 1.0

        # If average duration suggests fallback generation (>4 seconds per image), use fallback timing:
        if avg_duration_per_image >= 4.0:
            logger.info(
                f"🎯 Detected fallback scenario (avg {avg_duration_per_image:.1f}s/image), "
                f"using fallback timing")
            return self.analyze_fallback_timing_requirements(
                prompts,
                platform,
                total_duration,
                category)

        # Otherwise use original timing logic
        logger.info(f"⏱️ TimingMaster analyzing standard timing for {len(prompts)} images")
        try:
            # Create comprehensive analysis prompt
            analysis_prompt = """
You are TimingMaster, an expert AI agent specializing in image display timing optimization for video content.
ANALYZE THESE IMAGE PROMPTS FOR OPTIMAL TIMING:
Content Details:
- Number of images: {len(prompts)}
- Platform: {platform}
- Total duration: {total_duration} seconds
- Category: {category}

Image Prompts:
{json.dumps(
    [{"index": i,
    "prompt": prompt.get('description', prompt.get('veo2_prompt', 'Unknown'))} for i,
    prompt in enumerate(prompts)],
    indent=2)}
:
TIMING ANALYSIS FACTORS:
1. CONTENT COMPLEXITY ANALYSIS:
   - Text-heavy content: Needs 2-4 seconds for reading:
   - Visual-only content: Can be faster, 1-2 seconds
   - Complex scenes: Need 3-5 seconds for processing:
   - Simple graphics: Can be quick, 0.8-1.5 seconds

2. PLATFORM OPTIMIZATION:
   - TikTok: Fast-paced, 0.8-2 seconds per image
   - YouTube: More flexible, 1.5-4 seconds per image
   - Instagram: Aesthetic focus, 2-3 seconds per image
   - Twitter: Quick consumption, 1-2 seconds per image

3. INFORMATION PROCESSING:
   - News/Facts: Longer duration for comprehension:
   - Entertainment: Faster pace for engagement:
   - Educational: Balanced timing for learning:
   - Comedy: Quick timing for punchlines:
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
- Attention requirements:
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

            # Clean up response (remove markdown formatting if present):
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            timing_analysis = json.loads(response_text)

            # Validate and adjust timing analysis
            timing_analysis = self._validate_timing_analysis(
                timing_analysis,
                total_duration,
                len(prompts))

            # Add agent metadata
            timing_analysis['agent_name'] = 'TimingMaster'
            timing_analysis['analysis_timestamp'] = datetime.now().isoformat()
            timing_analysis['total_images'] = len(prompts)
            timing_analysis['platform'] = platform

            logger.info("✅ TimingMaster analysis complete:")
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

    def _validate_fallback_timing(self,
                                   analysis: Dict[str, Any],
                                   target_duration: float,
                                   num_images: int) -> Dict[str, Any]:
        """Validate and enforce 5-10 second timing for fallback generation"""

        # Ensure image_timings exists:
        if 'image_timings' not in analysis:
            analysis['image_timings'] = []

        # Calculate default duration based on target duration and number of images
        default_duration = target_duration / num_images if num_images > 0 else 7.0
        default_duration = max(5.0, min(10.0, default_duration))  # Keep within 5-10 range
        
        # Enforce 5-10 second range for each image:
        for img_timing in analysis['image_timings']:
            duration = img_timing.get('duration', default_duration)

            # Enforce 5-10 second range
            if duration < 5.0:
                img_timing['duration'] = 5.0
                img_timing['timing_rationale'] = f"Adjusted to minimum 5s for fallback generation. {img_timing.get('timing_rationale', '')}"
            elif duration > 10.0:
                img_timing['duration'] = 10.0
                img_timing['timing_rationale'] = f"Adjusted to maximum 10s for fallback generation. {img_timing.get('timing_rationale', '')}"
            else:
                img_timing['duration'] = round(duration, 1)

        # If we don't have enough images to fill duration, adjust proportionally
        total_from_timings = sum(img.get('duration', default_duration) for img in analysis['image_timings'])
        if total_from_timings < target_duration and num_images > 0:
            # Distribute extra time across images, keeping within 5-10 second range
            extra_time = target_duration - total_from_timings
            extra_per_image = extra_time / num_images

            for img_timing in analysis['image_timings']:
                current_duration = img_timing.get('duration', default_duration)
                new_duration = min(10.0, current_duration + extra_per_image)
                img_timing['duration'] = round(new_duration, 1)

                if new_duration != current_duration:
                    img_timing['timing_rationale'] += f" (Extended by {new_duration - current_duration:.1f}s to fill target duration)"

        # Recalculate totals
        analysis['total_calculated_duration'] = sum(img.get('duration', default_duration) for img in analysis['image_timings'])
        analysis['average_duration_per_image'] = analysis['total_calculated_duration'] / num_images if num_images > 0 else default_duration

        # Ensure average is in 5-10 range:
        if analysis['average_duration_per_image'] < 5.0:
            analysis['average_duration_per_image'] = 5.0
        elif analysis['average_duration_per_image'] > 10.0:
            analysis['average_duration_per_image'] = 10.0

        logger.info("📊 Fallback timing validation complete:")
        logger.info("   All images in 5-10 second range: ✅")
        logger.info(f"   Average: {analysis['average_duration_per_image']:.1f}s")

        return analysis

    def _validate_timing_analysis(self,
                                   analysis: Dict[str, Any],
                                   target_duration: float,
                                   num_images: int) -> Dict[str, Any]:
        """Validate and adjust timing analysis to fit constraints"""

        # Ensure image_timings exists
        if 'image_timings' not in analysis:
            analysis['image_timings'] = []

        # Calculate total duration from individual timings
        total_from_timings = sum(img.get('duration', 1.0) for img in analysis['image_timings'])

        # If total is significantly different from target, adjust proportionally:
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

    def _create_fallback_timing_analysis(self,
                                          prompts: List[Dict[str, Any]],
                                          platform: str,
                                          total_duration: float,
                                          fallback_mode: bool = False) -> Dict[str, Any]:
        """Create fallback timing analysis when AI analysis fails"""

        if fallback_mode:
            logger.info("🔄 Using fallback heuristics for FALLBACK image timing (5-10 seconds)")
        else:
            logger.info("🔄 Using fallback heuristics for standard image timing")

        num_images = len(prompts)
        if fallback_mode:
            # Fallback generation: use 5-10 second range
            target_avg = total_duration / num_images if num_images > 0 else 7.0
            # Clamp to 5-10 second range
            base_duration = max(5.0, min(10.0, target_avg))

            # Platform adjustments within 5-10 range:
            if platform.lower() == 'tiktok':
                base_duration = max(5.0, min(7.0, base_duration))  # 5-7 seconds for TikTok:
            elif platform.lower() == 'youtube':
                base_duration = max(7.0, min(10.0, base_duration))  # 7-10 seconds for YouTube:
            elif platform.lower() == 'instagram':
                base_duration = max(6.0, min(8.0, base_duration))  # 6-8 seconds for Instagram:
        else:
            # Standard generation: calculate base duration from target
            target_avg = total_duration / num_images if num_images > 0 else 1.5
            if platform.lower() == 'tiktok':
                # CRITICAL FIX: Remove duration multiplier to maintain exact target duration
                # Fast-paced: slightly shorter than average
                base_duration = target_avg * 0.9
            elif platform.lower() == 'youtube':
                # More relaxed: slightly longer than average
                base_duration = target_avg * 1.1
            elif platform.lower() == 'instagram':
                # Aesthetic focus: close to average
                base_duration = target_avg * 1.0
            else:
                base_duration = target_avg  # Use calculated average

            # Ensure reasonable bounds while respecting target duration
            base_duration = max(0.5, min(base_duration, 8.0))

        # Create timing for each image
        image_timings = []
        for i, prompt in enumerate(prompts):
            if fallback_mode:
                # Slight variation within 5-10 range
                variation = 0.5 if i % 2 == 0 else -0.5
                duration = max(5.0, min(10.0, base_duration + variation))

                # First and last images get slight bonus (within range):
                if i == 0 or i == len(prompts) - 1:
                    duration = min(10.0, duration + 0.5)
            else:
                # Original logic
                variation = 0.2 if i % 2 == 0 else -0.2
                duration = max(0.5, base_duration + variation)

                # First and last images get slight bonus:
                if i == 0 or i == len(prompts) - 1:
                    duration += 0.3

            image_timings.append({
                "image_index": i,
                "duration": round(duration, 1),
                "content_type": "mixed_content",
                "complexity_level": "medium",
                "reading_time_required": 1.0 if fallback_mode else 0.5,
                "processing_time_required": 1.0 if fallback_mode else 0.5,
                "attention_weight": "medium",
                "timing_rationale": f"{'Fallback' if fallback_mode else 'Standard'} timing for {platform} platform"
            })

        total_calculated = sum(img['duration'] for img in image_timings)

        return {
            'timing_strategy': f'{"Fallback 5-10 second" if fallback_mode else "Standard"} platform-optimized timing for {platform}',
            'total_calculated_duration': total_calculated,
            'average_duration_per_image': total_calculated / num_images,
            'platform_optimization': f'Optimized for {platform} user behavior',
            'image_timings': image_timings,
            'timing_adjustments': {
                'first_image_bonus': 0.5 if fallback_mode else 0.3,
                'last_image_bonus': 0.5 if fallback_mode else 0.3,
                'complex_content_bonus': 0.0
            },
            'user_experience_optimization': f'{"Extended timing for fallback generation" if fallback_mode else "Balanced timing for optimal engagement"}',
            'agent_name': f'TimingMaster ({"Fallback" if fallback_mode else "Standard"} Heuristics)',
            'analysis_timestamp': datetime.now().isoformat(),
            'total_images': num_images,
            'platform': platform,
            'generation_mode': 'fallback' if fallback_mode else 'standard'
        }

    def get_timing_for_image(self,
                              image_index: int,
                              timing_analysis: Dict[str, Any]) -> float:
        """Get the timing for a specific image from the analysis"""

        image_timings = timing_analysis.get('image_timings', [])
        if image_index < len(image_timings):
            return image_timings[image_index].get('duration', 1.5)
        else:
            # Fallback to average
            return timing_analysis.get('average_duration_per_image', 1.5)

    def create_ffmpeg_timing_list(self,
                                   timing_analysis: Dict[str, Any],
                                   image_paths: List[str]) -> List[Dict[str, Any]]:
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
