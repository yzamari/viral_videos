"""
Video Composition AI Agents
Specialized agents for making granular video composition decisions
"""

try:
    from google.generativeai.generative_models import GenerativeModel
    genai_available = True
except ImportError:
    GenerativeModel = None
    genai_available = False

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import json
import re
from ..utils.json_fixer import create_json_fixer
from ..config.ai_model_config import DEFAULT_AI_MODEL

logger = logging.getLogger(__name__)

class VideoStructureAgent:
    """
    AI Agent specialized in video structure and clip composition strategy
    Decides how to break down video into segments with different continuity approaches
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        if genai_available and GenerativeModel:
            self.model = GenerativeModel(DEFAULT_AI_MODEL)
        else:
            logger.warning("Google Generative AI is not available. Structure analysis will be limited.")
            self.model = None
        
        # Initialize JSON fixer
        self.json_fixer = create_json_fixer(api_key)

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
                                mission: str,
                                category: str,
                                platform: str,
                                total_duration: int,
                                style: str = "viral") -> Dict[str,
                                                              Any]:
        """
        Analyze and decide optimal video structure with mixed continuity approaches
        """
        logger.info(
            f"🏗️ StructureMaster analyzing video structure for: {mission}")

        try:
            analysis_prompt = """
You are StructureMaster, an expert AI agent specializing in video structure and
        composition strategy.

ANALYZE THIS VIDEO CONTENT:
- Mission: {mission}
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

            if not self.model:
                logger.warning("⚠️ AI model not available, using fallback structure")
                return self._create_fallback_structure(total_duration)

            response = self.model.generate_content(
                analysis_prompt.format(
                    mission=mission,
                    category=category,
                    platform=platform,
                    total_duration=total_duration,
                    style=style
                )
            )

            # Use centralized JSON fixer to handle parsing
            expected_structure = {
                "total_segments": int,
                "structure_strategy": str,
                "segments": list,
                "continuity_groups": list,
                "engagement_strategy": str,
                "platform_optimization": str
            }
            
            structure_data = self.json_fixer.fix_json(response.text, expected_structure)
            
            if structure_data:
                structure_data.update({
                    'agent_name': 'StructureMaster',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'input_parameters': {
                        'mission': mission,
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
            else:
                logger.warning("⚠️ JSON fixer could not parse StructureMaster response")
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
        if genai_available and GenerativeModel:
            self.model = GenerativeModel(DEFAULT_AI_MODEL)
        else:
            logger.warning("Google Generative AI is not available. Timing analysis will be limited.")
            self.model = None
        
        # Initialize JSON fixer
        self.json_fixer = create_json_fixer(api_key)

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

            if not self.model:
                logger.warning("⚠️ AI model not available, using fallback timing")
                return self._create_fallback_timing(video_structure)

            response = self.model.generate_content(timing_prompt)

            # Use centralized JSON fixer to handle parsing
            expected_timing = {
                "timing_strategy": str,
                "total_clips": int,
                "clips": list,
                "pacing_flow": str,
                "attention_optimization": str
            }
            
            timing_data = self.json_fixer.fix_json(response.text, expected_timing)
            
            if timing_data:
                timing_data.update({
                    'agent_name': 'TimingMaster',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'input_parameters': {
                        'video_structure': video_structure,
                        'content_details': content_details
                    }
                })

                logger.info(
                    f"⏱️ TimingMaster Decision: {
                        timing_data.get('total_clips', 0)} clips")
                logger.info(f"   Strategy: {timing_data.get('timing_strategy', 'Unknown')}")

                return timing_data
            else:
                logger.warning("⚠️ JSON fixer could not parse TimingMaster response")
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
        if genai_available and GenerativeModel:
            self.model = GenerativeModel(DEFAULT_AI_MODEL)
        else:
            logger.warning("Google Generative AI is not available. Visual design analysis will be limited.")
            self.model = None
        
        # Initialize JSON fixer
        self.json_fixer = create_json_fixer(api_key)

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
        Design visual elements for the video (headers, overlays, etc.)
        """
        logger.info(f"🎨 VisualDesigner designing visual elements for {platform}")

        try:
            design_prompt = """
You are VisualDesigner, an expert AI agent specializing in visual elements design.

ANALYZE VISUAL DESIGN REQUIREMENTS:

Video Structure: {json.dumps(video_structure, indent=2)}
Content Theme: {content_theme}
Platform: {platform}

DESIGN OPTIMAL VISUAL ELEMENTS:

1. HEADER/TITLE DESIGN:
   - What should the main header/title look like?
   - Font, color, size, placement recommendations

2. OVERLAY STRATEGY:
   - When and where should overlays appear?
   - How to maximize readability and engagement?

3. SUBTITLE DESIGN:
   - Subtitle style, placement, and timing
   - Accessibility considerations

4. PLATFORM-SPECIFIC DESIGN:
   - TikTok: Bold, high-contrast, large text
   - YouTube: Professional, clean, brand-aligned
   - Instagram: Aesthetic, visually consistent

PROVIDE DETAILED VISUAL DESIGN PLAN:

Respond in JSON format:
{
    "header": {"text": "string", "font": "string", "color": "string", "size": "string", "placement": "string"},
    "overlays": [
        {"text": "string", "start_time": number, "end_time": number, "style": "string", "placement": "string"}
    ],
    "subtitles": {"style": "string", "placement": "string", "timing": "string"},
    "color_palette": ["#RRGGBB", ...],
    "platform_guidelines": "string"
}
"""

            if not self.model:
                logger.warning("⚠️ AI model not available, using fallback design")
                return self._create_fallback_design(platform)

            response = self.model.generate_content(design_prompt)

            # Use centralized JSON fixer to handle parsing
            expected_design = {
                "header": dict,
                "overlays": list,
                "subtitles": dict,
                "color_palette": list,
                "platform_guidelines": str
            }
            
            design_data = self.json_fixer.fix_json(response.text, expected_design)
            
            if design_data:
                design_data.update({
                    'agent_name': 'VisualDesigner',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'input_parameters': {
                        'video_structure': video_structure,
                        'content_theme': content_theme,
                        'platform': platform
                    }
                })

                logger.info(f"🎨 VisualDesigner Decision: Header: {design_data.get('header', {}).get('text', 'N/A')}")
                logger.info(f"   Overlays: {len(design_data.get('overlays', []))}")

                return design_data
            else:
                logger.warning("⚠️ JSON fixer could not parse VisualDesigner response")
                return self._create_fallback_design(platform)
        except Exception as e:
            logger.error(f"VisualDesigner analysis failed: {e}")
            return self._create_fallback_design(platform)

    def _create_fallback_design(self, platform: str) -> Dict[str, Any]:
        """Create fallback design when AI analysis fails"""

        # Enhanced color palette - avoiding redundant orange
        color_palette = {
            'primary': '#FF6B6B',  # Coral Red
            'secondary': '#4ECDC4',  # Turquoise
            'accent': '#45B7D1',  # Sky Blue
            'text': '#FFFFFF',
            'background': '#000000'
        }

        return {
            'design_strategy': f'Enhanced design optimized for {platform}',
            'color_palette': color_palette,
            'typography': {
                "main_font": "Helvetica-Bold, sans-serif",
                "header_font": "Arial-Bold, sans-serif",
                "subtitle_font": "Georgia-Bold, sans-serif",
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
            'platform_adaptations': f'Enhanced {platform} optimizations with improved typography',
            'agent_name': 'VisualDesigner (Enhanced)',
            'analysis_timestamp': datetime.now().isoformat()
        }

class MediaTypeAgent:
    """
    AI Agent specialized in deciding between VEO3 video clips vs static images
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        if genai_available and GenerativeModel:
            self.model = GenerativeModel(DEFAULT_AI_MODEL)
        else:
            logger.warning("Google Generative AI is not available. Media type analysis will be limited.")
            self.model = None
        
        # Initialize JSON fixer
        self.json_fixer = create_json_fixer(api_key)

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
        Analyze and decide optimal media types for each clip (image, video, animation)
        """
        logger.info(f"🖼️ MediaTypeAgent analyzing media types for {len(clip_plan.get('clips', []))} clips")

        try:
            media_prompt = """
You are MediaTypeAgent, an expert AI agent specializing in media type selection.

ANALYZE MEDIA TYPE REQUIREMENTS:

Clip Plan: {json.dumps(clip_plan, indent=2)}
Content Analysis: {json.dumps(content_analysis, indent=2)}

DETERMINE OPTIMAL MEDIA TYPES:

1. CLIP ANALYSIS:
   - For each clip, decide if it should be image, video, or animation
   - Consider content, pacing, and engagement

2. PLATFORM OPTIMIZATION:
   - TikTok: Fast, dynamic visuals
   - YouTube: Mix of video and image
   - Instagram: Aesthetic, high-quality images

3. ENGAGEMENT STRATEGY:
   - Use of animation for emphasis
   - When to use real video vs. generated images

PROVIDE DETAILED MEDIA PLAN:

Respond in JSON format:
{
    "media_strategy": "string",
    "clip_media_types": [
        {"clip_id": 1, "media_type": "image/video/animation", "rationale": "string"}
    ],
    "platform_guidelines": "string"
}
"""

            if not self.model:
                logger.warning("⚠️ AI model not available, using fallback media plan")
                return self._create_fallback_media_plan(clip_plan)

            response = self.model.generate_content(media_prompt)

            # Use centralized JSON fixer to handle parsing
            expected_media = {
                "media_strategy": str,
                "clip_media_types": list,
                "platform_guidelines": str
            }
            
            media_data = self.json_fixer.fix_json(response.text, expected_media)
            
            if media_data:
                media_data.update({
                    'agent_name': 'MediaTypeAgent',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'input_parameters': {
                        'clip_plan': clip_plan,
                        'content_analysis': content_analysis
                    }
                })

                logger.info(f"🖼️ MediaTypeAgent Decision: Strategy: {media_data.get('media_strategy', 'N/A')}")
                logger.info(f"   Clip Media Types: {len(media_data.get('clip_media_types', []))}")

                return media_data
            else:
                logger.warning("⚠️ JSON fixer could not parse MediaTypeAgent response")
                return self._create_fallback_media_plan(clip_plan)
        except Exception as e:
            logger.error(f"MediaTypeAgent analysis failed: {e}")
            return self._create_fallback_media_plan(clip_plan)

    def _create_fallback_media_plan(
            self, clip_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback media plan when AI analysis fails"""

        clip_decisions = []
        veo3_count = 0
        image_count = 0

        for clip in clip_plan['clips']:
            # Default: use VEO3 for most clips, images for very short ones
            if clip['duration'] < 3 and clip['purpose'] in [
                    'transition', 'text']:
                media_type = 'static_image'
                image_count += 1
            else:
                media_type = 'veo3_video'
                veo3_count += 1

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
