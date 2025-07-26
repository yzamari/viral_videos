"""
Video Generation Fallback System
Implements a robust fallback chain for video generation
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from moviepy.editor import *

from ..utils.logging_config import get_logger
from ..models.video_models import GeneratedVideoConfig

logger = get_logger(__name__)


@dataclass
class FallbackResult:
    """Result from fallback generation"""
    success: bool
    video_path: Optional[str]
    method_used: str  # veo, image_sequence, color_fallback
    attempts: int
    error_message: Optional[str] = None
    clips_generated: List[str] = None


class VideoGenerationFallback:
    """
    Robust fallback system for video generation
    1. Try VEO generation (2 attempts)
    2. Try image sequence generation (2 attempts)
    3. Use color-based fallback as last resort
    """
    
    def __init__(self, veo_client, image_client, api_key: str):
        """Initialize fallback system"""
        self.veo_client = veo_client
        self.image_client = image_client
        self.api_key = api_key
        logger.info("🛡️ Video Generation Fallback System initialized")
    
    async def generate_with_fallback(self,
                                    prompt: str,
                                    duration: float,
                                    config: GeneratedVideoConfig,
                                    output_path: str,
                                    scene_data: Dict[str, Any] = None) -> FallbackResult:
        """
        Generate video with comprehensive fallback chain
        
        Args:
            prompt: Video generation prompt
            duration: Duration in seconds
            config: Video generation configuration
            output_path: Where to save the video
            scene_data: Optional scene data from analyzer
            
        Returns:
            FallbackResult with generation details
        """
        logger.info(f"🎬 Starting video generation with fallback for {duration}s clip")
        
        # Attempt 1 & 2: VEO Generation
        if not getattr(config, 'fallback_only', False):
            for attempt in range(2):
                logger.info(f"🎥 VEO Generation Attempt {attempt + 1}/2")
                try:
                    success = await self._try_veo_generation(
                        prompt, duration, output_path, config
                    )
                    if success:
                        return FallbackResult(
                            success=True,
                            video_path=output_path,
                            method_used="veo",
                            attempts=attempt + 1
                        )
                except Exception as e:
                    logger.warning(f"⚠️ VEO attempt {attempt + 1} failed: {e}")
        
        # Attempt 3 & 4: Image Sequence Generation
        logger.info("🖼️ Falling back to image sequence generation")
        for attempt in range(2):
            logger.info(f"🎨 Image Generation Attempt {attempt + 1}/2")
            try:
                success = await self._try_image_sequence_generation(
                    prompt, duration, output_path, config, scene_data
                )
                if success:
                    return FallbackResult(
                        success=True,
                        video_path=output_path,
                        method_used="image_sequence",
                        attempts=2 + attempt + 1
                    )
            except Exception as e:
                logger.warning(f"⚠️ Image sequence attempt {attempt + 1} failed: {e}")
        
        # Final Fallback: Color-based generation
        logger.info("🎨 Using color-based fallback generation")
        try:
            success = await self._generate_color_fallback(
                prompt, duration, output_path, config, scene_data
            )
            if success:
                return FallbackResult(
                    success=True,
                    video_path=output_path,
                    method_used="color_fallback",
                    attempts=5
                )
        except Exception as e:
            logger.error(f"❌ Color fallback failed: {e}")
        
        return FallbackResult(
            success=False,
            video_path=None,
            method_used="none",
            attempts=5,
            error_message="All generation methods failed"
        )
    
    async def _try_veo_generation(self, prompt: str, duration: float, 
                                 output_path: str, config: GeneratedVideoConfig) -> bool:
        """Try VEO generation"""
        if not self.veo_client:
            return False
            
        try:
            # Generate with VEO
            result = await self.veo_client.generate_video(
                prompt=prompt,
                duration=int(duration),
                aspect_ratio=self._get_aspect_ratio(config),
                style=getattr(config, 'visual_style', 'dynamic')
            )
            
            if result and os.path.exists(result):
                # Move to output path
                os.rename(result, output_path)
                return True
                
        except Exception as e:
            logger.error(f"VEO generation error: {e}")
            
        return False
    
    async def _try_image_sequence_generation(self, prompt: str, duration: float,
                                           output_path: str, config: GeneratedVideoConfig,
                                           scene_data: Optional[Dict[str, Any]]) -> bool:
        """Generate video from image sequence (4-5 images per second)"""
        try:
            # Calculate number of images needed
            fps = 24  # Standard FPS
            images_per_second = 4.5  # 4-5 images per second
            total_frames = int(duration * fps)
            num_images = int(duration * images_per_second)
            
            logger.info(f"📸 Generating {num_images} images for {duration}s video")
            
            # Generate images
            images = []
            for i in range(num_images):
                # Create varied prompts if scene data available
                if scene_data and 'visual_sequence' in scene_data:
                    image_prompt = self._create_image_prompt(
                        prompt, i, num_images, scene_data
                    )
                else:
                    # Add variation to prompt
                    image_prompt = f"{prompt}, frame {i+1} of {num_images}"
                
                logger.info(f"🎨 Generating image {i+1}/{num_images}")
                image_path = await self._generate_single_image(
                    image_prompt, config, i
                )
                
                if image_path and os.path.exists(image_path):
                    images.append(image_path)
                else:
                    # Generate placeholder if image generation fails
                    placeholder = self._create_placeholder_image(
                        f"Scene {i+1}", config
                    )
                    images.append(placeholder)
            
            # Create video from images
            if images:
                return self._create_video_from_images(
                    images, output_path, duration, fps
                )
                
        except Exception as e:
            logger.error(f"Image sequence generation error: {e}")
            
        return False
    
    def _create_image_prompt(self, base_prompt: str, index: int, 
                            total: int, scene_data: Dict[str, Any]) -> str:
        """Create varied prompt for each image based on scene data"""
        try:
            visual_sequence = scene_data.get('visual_sequence', [])
            if visual_sequence:
                # Find which scene this image belongs to
                scene_index = int(index / total * len(visual_sequence))
                scene = visual_sequence[min(scene_index, len(visual_sequence) - 1)]
                
                # Build detailed prompt
                prompt_parts = [base_prompt]
                
                if 'description' in scene:
                    prompt_parts.append(scene['description'])
                if 'camera_angle' in scene:
                    prompt_parts.append(f"camera angle: {scene['camera_angle']}")
                if 'key_elements' in scene:
                    elements = ', '.join(scene['key_elements'])
                    prompt_parts.append(f"showing: {elements}")
                
                return ', '.join(prompt_parts)
        except:
            pass
            
        return f"{base_prompt}, moment {index+1} of {total}"
    
    async def _generate_single_image(self, prompt: str, 
                                   config: GeneratedVideoConfig, 
                                   index: int) -> Optional[str]:
        """Generate a single image"""
        if not self.image_client:
            return None
            
        try:
            # Use image client to generate
            result = await self.image_client.generate_image(
                prompt=prompt,
                style=getattr(config, 'visual_style', 'dynamic'),
                width=self._get_width(config),
                height=self._get_height(config)
            )
            
            if result and 'path' in result:
                return result['path']
                
        except Exception as e:
            logger.warning(f"Image generation failed: {e}")
            
        return None
    
    def _create_video_from_images(self, images: List[str], 
                                 output_path: str, 
                                 duration: float, 
                                 fps: int) -> bool:
        """Create video from image sequence"""
        try:
            # Calculate display duration for each image
            image_duration = duration / len(images)
            
            # Load images as clips
            clips = []
            for img_path in images:
                if os.path.exists(img_path):
                    clip = ImageClip(img_path, duration=image_duration)
                    clips.append(clip)
            
            if not clips:
                return False
            
            # Concatenate clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Set FPS
            final_video = final_video.set_fps(fps)
            
            # Add smooth transitions
            final_video = self._add_transitions(final_video, len(clips))
            
            # Write video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio=False,
                preset='medium',
                bitrate="8000k"
            )
            
            # Clean up
            final_video.close()
            for clip in clips:
                clip.close()
            
            return os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"Video creation from images failed: {e}")
            return False
    
    def _add_transitions(self, video: VideoClip, num_clips: int) -> VideoClip:
        """Add smooth transitions between images"""
        try:
            # Add crossfade transitions
            transition_duration = 0.2  # 200ms transitions
            
            # This is a simplified version - MoviePy's crossfade is complex
            # In production, you'd want more sophisticated transitions
            return video.crossfadein(transition_duration).crossfadeout(transition_duration)
            
        except:
            return video
    
    async def _generate_color_fallback(self, prompt: str, duration: float,
                                     output_path: str, config: GeneratedVideoConfig,
                                     scene_data: Optional[Dict[str, Any]]) -> bool:
        """Generate color-based fallback video"""
        try:
            width = self._get_width(config)
            height = self._get_height(config)
            fps = 24
            
            # Extract colors from prompt or use defaults
            colors = self._extract_colors_from_prompt(prompt, config)
            
            # Create color clips
            clips = []
            segment_duration = duration / len(colors)
            
            for i, color in enumerate(colors):
                # Create color clip
                color_clip = ColorClip(
                    size=(width, height),
                    color=color,
                    duration=segment_duration
                )
                
                # Add text overlay
                text = self._get_fallback_text(i, scene_data)
                if text:
                    txt_clip = TextClip(
                        text,
                        fontsize=int(height * 0.06),
                        color='white',
                        font='Arial',
                        stroke_color='black',
                        stroke_width=2,
                        method='caption',
                        size=(width * 0.8, None),
                        align='center'
                    ).set_duration(segment_duration)
                    
                    txt_clip = txt_clip.set_position('center')
                    color_clip = CompositeVideoClip([color_clip, txt_clip])
                
                clips.append(color_clip)
            
            # Concatenate clips
            final_video = concatenate_videoclips(clips, method="compose")
            final_video = final_video.set_fps(fps)
            
            # Write video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio=False,
                preset='fast'
            )
            
            # Clean up
            final_video.close()
            for clip in clips:
                clip.close()
            
            return os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"Color fallback generation failed: {e}")
            return False
    
    def _extract_colors_from_prompt(self, prompt: str, 
                                   config: GeneratedVideoConfig) -> List[tuple]:
        """Extract or generate colors based on prompt and style"""
        # Default color schemes based on content type
        style = getattr(config, 'visual_style', '').lower()
        
        if 'news' in prompt.lower() or 'news' in style:
            return [(200, 0, 0), (0, 0, 200), (255, 255, 255)]  # Red, Blue, White
        elif 'comedy' in prompt.lower() or 'family guy' in style:
            return [(255, 200, 0), (0, 200, 255), (255, 100, 0)]  # Yellow, Cyan, Orange
        elif 'educational' in prompt.lower():
            return [(0, 150, 0), (0, 0, 150), (150, 150, 150)]  # Green, Blue, Gray
        else:
            # Generate gradient
            return [
                (100, 100, 200),  # Light blue
                (150, 100, 200),  # Purple
                (200, 100, 150),  # Pink
            ]
    
    def _get_fallback_text(self, index: int, 
                          scene_data: Optional[Dict[str, Any]]) -> str:
        """Get text for fallback video"""
        if scene_data and 'script_content' in scene_data:
            # Split script into segments
            script = scene_data['script_content']
            words = script.split()
            segment_size = len(words) // 3
            
            if index == 0:
                return ' '.join(words[:segment_size])
            elif index == 1:
                return ' '.join(words[segment_size:segment_size*2])
            else:
                return ' '.join(words[segment_size*2:])
        
        return f"Scene {index + 1}"
    
    def _get_aspect_ratio(self, config: GeneratedVideoConfig) -> str:
        """Get aspect ratio for video"""
        platform = str(config.target_platform).lower()
        if 'tiktok' in platform or 'instagram' in platform:
            return "9:16"
        return "16:9"
    
    def _get_width(self, config: GeneratedVideoConfig) -> int:
        """Get video width"""
        platform = str(config.target_platform).lower()
        if 'tiktok' in platform or 'instagram' in platform:
            return 1080
        return 1920
    
    def _get_height(self, config: GeneratedVideoConfig) -> int:
        """Get video height"""
        platform = str(config.target_platform).lower()
        if 'tiktok' in platform or 'instagram' in platform:
            return 1920
        return 1080
    
    def _create_placeholder_image(self, text: str, 
                                 config: GeneratedVideoConfig) -> str:
        """Create a placeholder image when generation fails"""
        try:
            width = self._get_width(config)
            height = self._get_height(config)
            
            # Create color clip and export as image
            color = (100, 100, 100)  # Gray
            img = ColorClip(size=(width, height), color=color, duration=1)
            
            # Add text
            txt = TextClip(
                text,
                fontsize=60,
                color='white',
                font='Arial',
                stroke_color='black',
                stroke_width=2
            ).set_duration(1)
            
            txt = txt.set_position('center')
            composite = CompositeVideoClip([img, txt])
            
            # Save as image
            temp_path = f"/tmp/placeholder_{hash(text)}.png"
            composite.save_frame(temp_path, t=0)
            
            composite.close()
            img.close()
            txt.close()
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Placeholder creation failed: {e}")
            return ""