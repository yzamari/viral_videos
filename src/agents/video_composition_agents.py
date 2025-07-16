"""
Video Composition AI Agents
Specialized agents for making granular video composition decisions
"""

import google.generativeai as genai
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class VideoStructureAgent:
    """
    AI Agent specialized in video structure and clip composition strategy
    Decides how to break down video into segments with different continuity approaches
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.agent_profile = {
            'name': 'StructureMaster',
            'role': 'Video Structure Strategist',
            'expertise': [
                'Video segmentation and flow analysis',
                'Narrative structure optimization',
                'Continuity vs. jump-cut strategy',
                'Audience attention management',
                'Platform-specific pacing'
            ]
        }

    def analyze_video_structure(self,
                                topic: str,
                                category: str,
                                platform: str,
                                total_duration: int,
                                style: str = "viral") -> Dict[str,
                                                              Any]:
        """
        Analyze and decide optimal video structure with mixed continuity approaches
        """
        logger.info(
            f"🏗️ StructureMaster analyzing video structure for: {topic}")

        try:
            analysis_prompt = """
You are StructureMaster, an expert AI agent specializing in video structure and
        composition strategy.

ANALYZE THIS VIDEO CONTENT:
- Topic: {topic}
- Category: {category}
- Platform: {platform}
- Total Duration: {total_duration} seconds
- Style: {style}

DESIGN OPTIMAL VIDEO STRUCTURE:

1. SEGMENT ANALYSIS:
   - How should this video be broken into segments?
   - Which segments benefit from continuity vs. jump cuts?
   - What's the optimal pacing for each segment?

2. CONTINUITY STRATEGY:
   - Identify segments that should flow continuously (
       e.g.,
       3 clips of 8s = 24s continuous)
   - Identify segments that should be standalone clips
   - Consider narrative flow and audience engagement

3. PLATFORM OPTIMIZATION:
   - TikTok: Fast hooks, varied pacing
   - YouTube: Longer continuity, structured flow
   - Instagram: Visual consistency, quick payoffs

4. ENGAGEMENT ARCHITECTURE:
   - Hook placement and structure
   - Attention retention strategies
   - Climax and resolution timing

PROVIDE DETAILED STRUCTURE PLAN:

Respond in JSON format:
{{
    "total_segments": number,
    "structure_strategy": "string describing overall approach",
    "segments": [
        {{
            "segment_id": 1,
            "start_time": 0,
            "duration": number_in_seconds,
            "continuity_type": "continuous" or "standalone",
            "purpose": "hook/development/climax/resolution",
            "clip_count": number_of_clips_in_segment,
            "pacing": "fast/medium/slow",
            "narrative_function": "description"
        }}
    ],
    "continuity_groups": [
        {{
            "group_id": 1,
            "segments": [1, 2, 3],
            "total_duration": number,
            "flow_strategy": "description"
        }}
    ],
    "engagement_strategy": "description",
    "platform_optimization": "description"
}}
"""

            response = self.model.generate_content(analysis_prompt)

            try:
                response_text = response.text.strip() if response.text else ""
                
                # Log the raw response for debugging
                logger.debug(f"StructureMaster raw response: {response_text[:200]}...")
                
                if not response_text:
                    logger.warning("⚠️ Empty response from StructureMaster API")
                    return self._create_fallback_structure(total_duration)
                
                # Clean up response text
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                # Remove any leading/trailing whitespace and newlines
                response_text = response_text.strip()
                
                # Try to find JSON content in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    structure_data = json.loads(json_text)
                else:
                    logger.warning("⚠️ No JSON found in StructureMaster response")
                    return self._create_fallback_structure(total_duration)

                structure_data.update({
                    'agent_name': 'StructureMaster',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'input_parameters': {
                        'topic': topic,
                        'category': category,
                        'platform': platform,
                        'total_duration': total_duration,
                        'style': style
                    }
                })

                logger.info(
                    f"🏗️ StructureMaster Decision: {
                        structure_data.get('total_segments', 0)} segments")
                logger.info(
                    f"   Strategy: {
                        structure_data.get('structure_strategy', 'Unknown')}")

                return structure_data

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse StructureMaster response: {e}")
                logger.error(f"Raw response was: {response_text}")
                return self._create_fallback_structure(total_duration)

        except Exception as e:
            logger.error(f"StructureMaster analysis failed: {e}")
            return self._create_fallback_structure(total_duration)

    def _create_fallback_structure(
            self, total_duration: int) -> Dict[str, Any]:
        """Create fallback structure when AI analysis fails"""

        # Simple 3-segment structure
        segments = []
        if total_duration <= 15:
            # Short video: 2 segments
            segments = [
                {
                    "segment_id": 1,
                    "start_time": 0,
                    "duration": total_duration // 2,
                    "continuity_type": "standalone",
                    "purpose": "hook",
                    "clip_count": 1,
                    "pacing": "fast",
                    "narrative_function": "Opening hook"
                },
                {
                    "segment_id": 2,
                    "start_time": total_duration // 2,
                    "duration": total_duration - (total_duration // 2),
                    "continuity_type": "standalone",
                    "purpose": "climax",
                    "clip_count": 1,
                    "pacing": "fast",
                    "narrative_function": "Main content"
                }
            ]
        else:
            # Longer video: 3 segments
            segment_duration = total_duration // 3
            segments = [
                {
                    "segment_id": 1,
                    "start_time": 0,
                    "duration": segment_duration,
                    "continuity_type": "standalone",
                    "purpose": "hook",
                    "clip_count": 1,
                    "pacing": "fast",
                    "narrative_function": "Opening hook"
                },
                {
                    "segment_id": 2,
                    "start_time": segment_duration,
                    "duration": segment_duration,
                    "continuity_type": "continuous",
                    "purpose": "development",
                    "clip_count": 2,
                    "pacing": "medium",
                    "narrative_function": "Main development"
                },
                {
                    "segment_id": 3,
                    "start_time": segment_duration * 2,
                    "duration": total_duration - (segment_duration * 2),
                    "continuity_type": "standalone",
                    "purpose": "resolution",
                    "clip_count": 1,
                    "pacing": "fast",
                    "narrative_function": "Conclusion"
                }
            ]

        return {
            'total_segments': len(segments),
            'structure_strategy': 'Fallback balanced structure',
            'segments': segments,
            'continuity_groups': [
                {
                    'group_id': 1,
                    'segments': [2],
                    'total_duration': segments[1]['duration'],
                    'flow_strategy': 'Continuous flow'}] if len(segments) > 2 else [],
            'engagement_strategy': 'Balanced pacing with hook and resolution',
            'platform_optimization': 'Generic optimization',
            'agent_name': 'StructureMaster (Fallback)',
            'analysis_timestamp': datetime.now().isoformat()}

class ClipTimingAgent:
    """
    AI Agent specialized in determining optimal timing for individual clips
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.agent_profile = {
            'name': 'TimingMaster',
            'role': 'Clip Timing Specialist',
            'expertise': [
                'Optimal clip duration analysis',
                'Attention span optimization',
                'Content density evaluation',
                'Platform timing preferences',
                'Narrative pacing control'
            ]
        }

    def analyze_clip_timings(self,
                             video_structure: Dict[str,
                                                   Any],
                             content_details: Dict[str,
                                                   Any]) -> Dict[str,
                                                                 Any]:
        """
        Analyze and decide optimal timing for each individual clip
        """
        logger.info(
            f"⏱️ TimingMaster analyzing clip timings for {
                video_structure['total_segments']} segments")

        try:
            timing_prompt = """
You are TimingMaster, an expert AI agent specializing in clip timing and
        pacing optimization.

ANALYZE CLIP TIMING REQUIREMENTS:

Video Structure: {json.dumps(video_structure, indent=2)}
Content Details: {json.dumps(content_details, indent=2)}

DETERMINE OPTIMAL CLIP TIMINGS:

1. SEGMENT ANALYSIS:
   For each segment, determine optimal clip breakdown:
   - How many clips should each segment contain?
   - What should be the duration of each clip?
   - How should clips flow within segments?

2. TIMING STRATEGY:
   - Consider content density and complexity
   - Optimize for platform attention spans
   - Balance information delivery with engagement
   - Account for continuity vs. standalone requirements

3. PACING OPTIMIZATION:
   - Fast clips for hooks and climax
   - Medium clips for development
   - Varied pacing for engagement

PROVIDE DETAILED TIMING PLAN:

Respond in JSON format:
{{
    "timing_strategy": "overall approach description",
    "total_clips": number,
    "clips": [
        {{
            "clip_id": 1,
            "segment_id": 1,
            "start_time": 0,
            "duration": number_in_seconds,
            "purpose": "hook/development/climax/transition",
            "pacing": "fast/medium/slow",
            "content_density": "high/medium/low",
            "timing_rationale": "why this duration"
        }}
    ],
    "pacing_flow": "description of overall pacing strategy",
    "attention_optimization": "how timing supports attention retention"
}}
"""

            response = self.model.generate_content(timing_prompt)

            try:
                response_text = response.text.strip() if response.text else ""
                
                # Log the raw response for debugging
                logger.debug(f"TimingMaster raw response: {response_text[:200]}...")
                
                if not response_text:
                    logger.warning("TimingMaster received empty response from Gemini")
                    return self._create_fallback_timing(video_structure)
                
                # Clean up response text
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                # Remove any leading/trailing whitespace and newlines
                response_text = response_text.strip()
                
                # Try to find JSON content in the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    timing_data = json.loads(json_text)
                else:
                    logger.warning("No JSON found in TimingMaster response")
                    return self._create_fallback_timing(video_structure)

                timing_data.update({
                    'agent_name': 'TimingMaster',
                    'analysis_timestamp': datetime.now().isoformat()
                })

                logger.info(
                    f"⏱️ TimingMaster Decision: {
                        timing_data.get('total_clips', 0)} clips")
                logger.info(f"   Strategy: {timing_data.get('timing_strategy', 'Unknown')}")

                return timing_data

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse TimingMaster response: {e}")
                logger.error(f"Raw response was: {response_text}")
                return self._create_fallback_timing(video_structure)

        except Exception as e:
            logger.error(f"TimingMaster analysis failed: {e}")
            return self._create_fallback_timing(video_structure)

    def _create_fallback_timing(
            self, video_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback timing when AI analysis fails"""

        clips = []
        clip_id = 1
        current_time = 0

        for segment in video_structure['segments']:
            clip_count = int(segment['clip_count'])
            segment_duration = float(segment['duration'])
            clip_duration = segment_duration / clip_count

            for i in range(clip_count):
                clips.append({
                    "clip_id": clip_id,
                    "segment_id": segment['segment_id'],
                    "start_time": current_time,
                    "duration": clip_duration,
                    "purpose": segment['purpose'],
                    "pacing": segment['pacing'],
                    "content_density": "medium",
                    "timing_rationale": f"Equal division of {segment_duration}s segment"
                })
                clip_id += 1
                current_time += clip_duration

        return {
            'timing_strategy': 'Fallback equal distribution',
            'total_clips': len(clips),
            'clips': clips,
            'pacing_flow': 'Balanced pacing across segments',
            'attention_optimization': 'Standard timing optimization',
            'agent_name': 'TimingMaster (Fallback)',
            'analysis_timestamp': datetime.now().isoformat()
        }

class VisualElementsAgent:
    """
    AI Agent specialized in visual elements design (headers, titles, subtitles)
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.agent_profile = {
            'name': 'VisualDesigner',
            'role': 'Visual Elements Specialist',
            'expertise': [
                'Typography and text design',
                'Color psychology and branding',
                'Visual hierarchy optimization',
                'Platform-specific design standards',
                'Accessibility and readability'
            ]
        }

    def design_visual_elements(self,
                               video_structure: Dict[str,
                                                     Any],
                               content_theme: str,
                               platform: str) -> Dict[str,
                                                      Any]:
        """
        Design headers, titles, subtitles with optimal positioning and styling
        """
        logger.info(
            f"🎨 VisualDesigner designing visual elements for {platform}")

        try:
            design_prompt = """
You are VisualDesigner, an expert AI agent specializing in visual elements and
        typography design.

DESIGN VISUAL ELEMENTS FOR:

Video Structure: {json.dumps(video_structure, indent=2)}
Content Theme: {content_theme}
Platform: {platform}

DESIGN REQUIREMENTS:

1. HEADERS & TITLES:
   - Main title design and positioning
   - Segment headers for different parts
   - Typography that matches content style
   - Platform-optimized sizing

2. SUBTITLES & CAPTIONS:
   - Subtitle styling and positioning
   - Readability optimization
   - Color contrast for accessibility
   - Animation and timing

3. VISUAL HIERARCHY:
   - Primary, secondary, tertiary text elements
   - Size, weight, and color relationships
   - Positioning for different screen sizes

4. PLATFORM OPTIMIZATION:
   - TikTok: Bold, high-contrast, mobile-first
   - YouTube: Professional, varied sizing
   - Instagram: Aesthetic, brand-consistent

PROVIDE COMPREHENSIVE DESIGN SPECIFICATION:

Respond in JSON format:
{{
    "design_strategy": "overall visual approach",
    "color_palette": {{
        "primary": "#hex",
        "secondary": "#hex",
        "accent": "#hex",
        "text": "#hex",
        "background": "#hex"
    }},
    "typography": {{
        "main_font": "font family",
        "header_font": "font family",
        "subtitle_font": "font family",
        "font_weights": ["normal", "bold", "extra-bold"]
    }},
    "text_elements": [
        {{
            "element_id": 1,
            "type": "main_title/header/subtitle/caption",
            "content": "text content",
            "position": {{"x": "percentage", "y": "percentage"}},
            "size": "pixels or percentage",
            "color": "#hex",
            "font_weight": "normal/bold/extra-bold",
            "animation": "fade-in/slide-up/none",
            "duration": "seconds on screen",
            "timing": "when to appear"
        }}
    ],
    "accessibility": {{
        "contrast_ratio": "4.5:1 minimum",
        "font_size_minimum": "16px",
        "readability_score": "high/medium/low"
    }},
    "platform_adaptations": "platform-specific adjustments"
}}
"""

            response = self.model.generate_content(design_prompt)

            try:
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]

                design_data = json.loads(response_text)

                design_data.update({
                    'agent_name': 'VisualDesigner',
                    'analysis_timestamp': datetime.now().isoformat()
                })

                logger.info(
                    f"🎨 VisualDesigner Decision: {len(design_data['text_elements'])} text elements")
                logger.info(f"   Strategy: {design_data['design_strategy']}")

                return design_data

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse VisualDesigner response: {e}")
                return self._create_fallback_design(platform)

        except Exception as e:
            logger.error(f"VisualDesigner analysis failed: {e}")
            return self._create_fallback_design(platform)

    def _create_fallback_design(self, platform: str) -> Dict[str, Any]:
        """Create fallback design when AI analysis fails"""

        # Platform-specific defaults
        if platform.lower() == 'tiktok':
            color_palette = {
                "primary": "#FF0050",
                "secondary": "#00F2EA",
                "accent": "#FFFF00",
                "text": "#FFFFFF",
                "background": "#000000"
            }
        elif platform.lower() == 'youtube':
            color_palette = {
                "primary": "#FF0000",
                "secondary": "#282828",
                "accent": "#FFFFFF",
                "text": "#FFFFFF",
                "background": "#0F0F0F"
            }
        else:  # Instagram/default
            color_palette = {
                "primary": "#E4405F",
                "secondary": "#833AB4",
                "accent": "#F77737",
                "text": "#FFFFFF",
                "background": "#000000"
            }

        return {
            'design_strategy': f'Fallback design optimized for {platform}',
            'color_palette': color_palette,
            'typography': {
                "main_font": "Arial, sans-seri",
                "header_font": "Arial Black, sans-seri",
                "subtitle_font": "Arial, sans-seri",
                "font_weights": ["normal", "bold", "extra-bold"]
            },
            'text_elements': [
                {
                    "element_id": 1,
                    "type": "main_title",
                    "content": "Video Title",
                    "position": {"x": "50%", "y": "20%"},
                    "size": "24px",
                    "color": color_palette["text"],
                    "font_weight": "extra-bold",
                    "animation": "fade-in",
                    "duration": "3",
                    "timing": "0s"
                }
            ],
            'accessibility': {
                "contrast_ratio": "4.5:1",
                "font_size_minimum": "16px",
                "readability_score": "high"
            },
            'platform_adaptations': f'Standard {platform} optimizations',
            'agent_name': 'VisualDesigner (Fallback)',
            'analysis_timestamp': datetime.now().isoformat()
        }

class MediaTypeAgent:
    """
    AI Agent specialized in deciding between VEO2 video clips vs static images
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.agent_profile = {
            'name': 'MediaStrategist',
            'role': 'Media Type Decision Specialist',
            'expertise': [
                'Video vs. image effectiveness analysis',
                'Content type optimization',
                'Resource allocation strategy',
                'Visual impact assessment',
                'Platform media preferences'
            ]
        }

    def analyze_media_types(self,
                            clip_plan: Dict[str,
                                            Any],
                            content_analysis: Dict[str,
                                                   Any]) -> Dict[str,
                                                                 Any]:
        """
        Decide whether each clip should be VEO2 video or static images
        """
        logger.info(
            f"📱 MediaStrategist analyzing media types for {
                clip_plan['total_clips']} clips")

        try:
            media_prompt = """
You are MediaStrategist, an expert AI agent specializing in media type optimization.

ANALYZE MEDIA TYPE REQUIREMENTS:

Clip Plan: {json.dumps(clip_plan, indent=2)}
Content Analysis: {json.dumps(content_analysis, indent=2)}

DECIDE OPTIMAL MEDIA TYPES:

1. CLIP-BY-CLIP ANALYSIS:
   For each clip, decide:
   - VEO2 video clip: For dynamic content, movement, action
   - Static images: For text-heavy content, infographics, pauses
   - Image sequences: For step-by-step content, comparisons

2. DECISION FACTORS:
   - Content complexity and movement requirements
   - Information density and reading time
   - Visual impact and engagement needs
   - Resource optimization and generation time
   - Platform preferences and user expectations

3. OPTIMIZATION STRATEGY:
   - Balance video and static content
   - Consider narrative flow and pacing
   - Optimize for attention retention
   - Account for accessibility needs

PROVIDE DETAILED MEDIA STRATEGY:

Respond in JSON format:
{{
    "media_strategy": "overall approach description",
    "resource_allocation": {{
        "veo2_clips": number,
        "static_images": number,
        "image_sequences": number
    }},
    "clip_media_decisions": [
        {{
            "clip_id": 1,
            "media_type": "veo2_video/static_image/image_sequence",
            "duration": number_in_seconds,
            "rationale": "why this media type",
            "content_description": "what will be shown",
            "visual_requirements": "specific visual needs",
            "generation_parameters": {{
                "style": "description",
                "quality": "high/medium/standard",
                "effects": ["list of effects"]
            }}
        }}
    ],
    "flow_optimization": "how media types support narrative flow",
    "engagement_strategy": "how media mix enhances engagement"
}}
"""

            response = self.model.generate_content(media_prompt)

            try:
                response_text = response.text.strip() if response.text else ""
                
                # Log the raw response for debugging
                logger.debug(f"MediaStrategist raw response: {response_text[:200]}...")
                
                if not response_text:
                    logger.warning("MediaStrategist received empty response from Gemini")
                    return self._create_fallback_media_plan(clip_plan)
                
                # Clean up response text
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                # Remove any leading/trailing whitespace and newlines
                response_text = response_text.strip()
                
                # Try to find JSON content in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    media_data = json.loads(json_text)
                else:
                    logger.warning("No JSON found in MediaStrategist response")
                    return self._create_fallback_media_plan(clip_plan)

                media_data.update({
                    'agent_name': 'MediaStrategist',
                    'analysis_timestamp': datetime.now().isoformat()
                })

                allocation = media_data.get('resource_allocation', {})
                logger.info(
                    f"📱 MediaStrategist Decision: {
                        allocation.get('veo2_clips', 0)} VEO2 clips, {
                        allocation.get('static_images', 0)} images")
                logger.info(f"   Strategy: {media_data.get('media_strategy', 'Unknown')}")

                return media_data

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse MediaStrategist response: {e}")
                logger.error(f"Raw response was: {response_text}")
                return self._create_fallback_media_plan(clip_plan)

        except Exception as e:
            logger.error(f"MediaStrategist analysis failed: {e}")
            return self._create_fallback_media_plan(clip_plan)

    def _create_fallback_media_plan(
            self, clip_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback media plan when AI analysis fails"""

        clip_decisions = []
        veo2_count = 0
        image_count = 0

        for clip in clip_plan['clips']:
            # Default: use VEO2 for most clips, images for very short ones
            if clip['duration'] < 3 and clip['purpose'] in [
                    'transition', 'text']:
                media_type = 'static_image'
                image_count += 1
            else:
                media_type = 'veo2_video'
                veo2_count += 1

            clip_decisions.append({
                "clip_id": clip['clip_id'],
                "media_type": media_type,
                "duration": clip['duration'],
                "rationale": f"Fallback decision based on {clip['duration']}s duration",
                "content_description": f"Content for {clip['purpose']}",
                "visual_requirements": "Standard quality",
                "generation_parameters": {
                    "style": "viral",
                    "quality": "high",
                    "effects": []
                }
            })

        return {
            'media_strategy': 'Fallback mixed media approach',
            'resource_allocation': {
                "veo2_clips": veo2_count,
                "static_images": image_count,
                "image_sequences": 0
            },
            'clip_media_decisions': clip_decisions,
            'flow_optimization': 'Balanced video and image content',
            'engagement_strategy': 'Standard engagement optimization',
            'agent_name': 'MediaStrategist (Fallback)',
            'analysis_timestamp': datetime.now().isoformat()
        }

def get_composition_agents_summary() -> Dict[str, Any]:
    """Get summary of all video composition agents"""
    return {
        'StructureMaster': {
            'role': 'Video Structure Strategist',
            'decisions': [
                'Video segmentation',
                'Continuity strategy',
                'Narrative flow']},
        'TimingMaster': {
            'role': 'Clip Timing Specialist',
            'decisions': [
                    'Individual clip durations',
                    'Pacing optimization',
                    'Attention management']},
        'VisualDesigner': {
            'role': 'Visual Elements Specialist',
            'decisions': [
                'Headers and titles',
                'Typography and colors',
                'Text positioning']},
        'MediaStrategist': {
            'role': 'Media Type Decision Specialist',
            'decisions': [
                'VEO2 vs. images',
                'Resource allocation',
                'Visual impact optimization']}}
