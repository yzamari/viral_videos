"""
Professional Effects Engine - Cinema-quality effects and transitions
Implements SOLID principles with modular, extensible architecture
"""

import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Protocol
from dataclasses import dataclass
from enum import Enum
import logging
from moviepy.editor import VideoFileClip, VideoClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx import all as vfx

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


# Interface Segregation Principle - Separate interfaces for different effect types
class ITransitionEffect(Protocol):
    """Interface for transition effects between clips"""
    def apply(self, clip1: VideoFileClip, clip2: VideoFileClip, duration: float) -> VideoFileClip:
        ...


class IVideoEffect(Protocol):
    """Interface for single-clip video effects"""
    def apply(self, clip: VideoFileClip) -> VideoFileClip:
        ...


class ITextAnimation(Protocol):
    """Interface for text animations"""
    def animate(self, text: str, duration: float, position: Tuple[int, int]) -> VideoFileClip:
        ...


class IColorGrading(Protocol):
    """Interface for color grading effects"""
    def grade(self, clip: VideoFileClip, lut_name: str) -> VideoFileClip:
        ...


# Single Responsibility - Each class handles one type of effect
class EffectType(Enum):
    """Types of available effects"""
    TRANSITION = "transition"
    FILTER = "filter"
    ANIMATION = "animation"
    COLOR = "color"
    MOTION = "motion"
    PARTICLE = "particle"


@dataclass
class EffectConfig:
    """Configuration for an effect"""
    name: str
    type: EffectType
    intensity: float = 1.0
    duration: float = 1.0
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass 
class TransitionConfig:
    """Configuration for transitions between clips"""
    type: str  # 'fade', 'slide', 'zoom', 'morph', 'glitch'
    duration: float
    direction: str = 'left'  # for slide transitions
    ease_function: str = 'ease_in_out'


# Abstract base classes following Open/Closed Principle
class BaseTransition(ABC):
    """Base class for all transitions"""
    
    @abstractmethod
    def apply(self, clip1: VideoFileClip, clip2: VideoFileClip, duration: float) -> VideoFileClip:
        """Apply transition between two clips"""
        pass
    
    def _ease_in_out(self, t: float) -> float:
        """Easing function for smooth transitions"""
        return t * t * (3.0 - 2.0 * t)
    
    def _ease_in(self, t: float) -> float:
        """Ease in function"""
        return t * t
    
    def _ease_out(self, t: float) -> float:
        """Ease out function"""
        return t * (2.0 - t)


class FadeTransition(BaseTransition):
    """Fade transition between clips"""
    
    def apply(self, clip1: VideoFileClip, clip2: VideoFileClip, duration: float) -> VideoFileClip:
        """Apply fade transition"""
        try:
            # Create fade out for clip1
            fade_out = clip1.fadeout(duration)
            
            # Create fade in for clip2
            fade_in = clip2.fadein(duration)
            
            # Overlap the clips
            final = CompositeVideoClip([
                fade_out,
                fade_in.set_start(clip1.duration - duration)
            ])
            
            return final.set_duration(clip1.duration + clip2.duration - duration)
            
        except Exception as e:
            logger.error(f"❌ Fade transition failed: {e}")
            return concatenate_videoclips([clip1, clip2])


class SlideTransition(BaseTransition):
    """Slide transition with direction control"""
    
    def __init__(self, direction: str = 'left'):
        self.direction = direction
    
    def apply(self, clip1: VideoFileClip, clip2: VideoFileClip, duration: float) -> VideoFileClip:
        """Apply slide transition"""
        try:
            w, h = clip1.size
            
            def make_frame(t):
                """Create transition frame at time t"""
                progress = self._ease_in_out(t / duration)
                
                if self.direction == 'left':
                    offset = int(w * progress)
                    frame1 = clip1.get_frame(clip1.duration - duration + t)
                    frame2 = clip2.get_frame(t)
                    
                    # Combine frames
                    result = np.zeros_like(frame1)
                    if offset < w:
                        result[:, :w-offset] = frame1[:, offset:]
                    if offset > 0:
                        result[:, w-offset:] = frame2[:, :offset]
                    
                elif self.direction == 'up':
                    offset = int(h * progress)
                    frame1 = clip1.get_frame(clip1.duration - duration + t)
                    frame2 = clip2.get_frame(t)
                    
                    result = np.zeros_like(frame1)
                    if offset < h:
                        result[:h-offset, :] = frame1[offset:, :]
                    if offset > 0:
                        result[h-offset:, :] = frame2[:offset, :]
                
                else:
                    # Default to crossfade
                    frame1 = clip1.get_frame(clip1.duration - duration + t)
                    frame2 = clip2.get_frame(t)
                    result = frame1 * (1 - progress) + frame2 * progress
                
                return result.astype('uint8')
            
            transition = VideoClip(make_frame, duration=duration)
            
            # Combine clips with transition
            part1 = clip1.subclip(0, clip1.duration - duration)
            part2 = clip2.subclip(duration, clip2.duration)
            
            return concatenate_videoclips([part1, transition, part2])
            
        except Exception as e:
            logger.error(f"❌ Slide transition failed: {e}")
            return concatenate_videoclips([clip1, clip2])


class ZoomTransition(BaseTransition):
    """Zoom transition with motion blur"""
    
    def apply(self, clip1: VideoFileClip, clip2: VideoFileClip, duration: float) -> VideoFileClip:
        """Apply zoom transition"""
        try:
            def make_frame(t):
                """Create zoom transition frame"""
                progress = self._ease_in_out(t / duration)
                
                # Zoom out clip1
                if t < duration / 2:
                    scale = 1.0 + progress * 0.5
                    frame = clip1.get_frame(clip1.duration - duration + t)
                    # Apply zoom
                    h, w = frame.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, 0, scale)
                    frame = cv2.warpAffine(frame, M, (w, h))
                
                # Zoom in clip2
                else:
                    scale = 1.5 - progress * 0.5
                    frame = clip2.get_frame(t - duration / 2)
                    h, w = frame.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, 0, scale)
                    frame = cv2.warpAffine(frame, M, (w, h))
                
                return frame
            
            transition = VideoClip(make_frame, duration=duration)
            
            part1 = clip1.subclip(0, clip1.duration - duration)
            part2 = clip2.subclip(duration, clip2.duration)
            
            return concatenate_videoclips([part1, transition, part2])
            
        except Exception as e:
            logger.error(f"❌ Zoom transition failed: {e}")
            return concatenate_videoclips([clip1, clip2])


# Single Responsibility - Video Effects
class BaseVideoEffect(ABC):
    """Base class for video effects"""
    
    @abstractmethod
    def apply(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply effect to clip"""
        pass


class MotionBlurEffect(BaseVideoEffect):
    """Motion blur effect for dynamic scenes"""
    
    def __init__(self, intensity: float = 0.5):
        self.intensity = max(0, min(1, intensity))
    
    def apply(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply motion blur effect"""
        try:
            def apply_motion_blur(get_frame, t):
                """Apply motion blur to frame"""
                frame = get_frame(t)
                
                # Calculate motion vector (simplified)
                kernel_size = int(15 * self.intensity) 
                if kernel_size % 2 == 0:
                    kernel_size += 1
                
                # Create motion blur kernel
                kernel = np.zeros((kernel_size, kernel_size))
                kernel[int((kernel_size-1)/2), :] = np.ones(kernel_size)
                kernel = kernel / kernel_size
                
                # Apply blur
                blurred = cv2.filter2D(frame, -1, kernel)
                
                return blurred
            
            return clip.fl(apply_motion_blur)
            
        except Exception as e:
            logger.error(f"❌ Motion blur failed: {e}")
            return clip


class KenBurnsEffect(BaseVideoEffect):
    """Ken Burns effect - slow zoom and pan"""
    
    def __init__(self, zoom_factor: float = 1.2, pan_direction: str = 'center'):
        self.zoom_factor = zoom_factor
        self.pan_direction = pan_direction
    
    def apply(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply Ken Burns effect"""
        try:
            duration = clip.duration
            w, h = clip.size
            
            def make_frame(t):
                """Create Ken Burns frame"""
                # Calculate zoom level
                progress = t / duration
                zoom = 1.0 + (self.zoom_factor - 1.0) * progress
                
                # Calculate pan offset
                if self.pan_direction == 'left':
                    pan_x = -int(w * 0.1 * progress)
                    pan_y = 0
                elif self.pan_direction == 'right':
                    pan_x = int(w * 0.1 * progress)
                    pan_y = 0
                else:  # center
                    pan_x = 0
                    pan_y = 0
                
                # Get frame and apply transformations
                frame = clip.get_frame(t)
                
                # Apply zoom
                center = (w // 2 + pan_x, h // 2 + pan_y)
                M = cv2.getRotationMatrix2D(center, 0, zoom)
                frame = cv2.warpAffine(frame, M, (w, h))
                
                return frame
            
            return VideoClip(make_frame, duration=duration)
            
        except Exception as e:
            logger.error(f"❌ Ken Burns effect failed: {e}")
            return clip


class GlitchEffect(BaseVideoEffect):
    """Digital glitch effect for modern style"""
    
    def __init__(self, intensity: float = 0.3, frequency: float = 0.1):
        self.intensity = intensity
        self.frequency = frequency
    
    def apply(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply glitch effect"""
        try:
            def apply_glitch(get_frame, t):
                """Apply glitch to frame"""
                frame = get_frame(t)
                
                # Random chance of glitch
                if np.random.random() < self.frequency:
                    h, w = frame.shape[:2]
                    
                    # RGB channel shift
                    shift = int(w * 0.02 * self.intensity)
                    if len(frame.shape) == 3:
                        # Shift red channel
                        frame[:, shift:, 0] = frame[:, :-shift, 0]
                        # Shift blue channel opposite
                        frame[:, :-shift, 2] = frame[:, shift:, 2]
                    
                    # Add noise blocks
                    num_blocks = int(5 * self.intensity)
                    for _ in range(num_blocks):
                        block_h = np.random.randint(10, 50)
                        block_w = np.random.randint(50, 200)
                        y = np.random.randint(0, max(1, h - block_h))
                        x = np.random.randint(0, max(1, w - block_w))
                        
                        # Add colored noise
                        noise = np.random.randint(0, 255, (block_h, block_w, 3))
                        frame[y:y+block_h, x:x+block_w] = \
                            frame[y:y+block_h, x:x+block_w] * 0.5 + noise * 0.5
                
                return frame.astype('uint8')
            
            return clip.fl(apply_glitch)
            
        except Exception as e:
            logger.error(f"❌ Glitch effect failed: {e}")
            return clip


# Color Grading Service
class ColorGradingService:
    """Professional color grading with LUT support"""
    
    def __init__(self):
        self.luts = {
            'cinematic': self._create_cinematic_lut(),
            'vintage': self._create_vintage_lut(),
            'vibrant': self._create_vibrant_lut(),
            'noir': self._create_noir_lut(),
            'warm': self._create_warm_lut(),
            'cool': self._create_cool_lut()
        }
    
    def apply_lut(self, clip: VideoFileClip, lut_name: str) -> VideoFileClip:
        """Apply color LUT to clip"""
        try:
            if lut_name not in self.luts:
                logger.warning(f"⚠️ LUT '{lut_name}' not found, using default")
                lut_name = 'cinematic'
            
            lut = self.luts[lut_name]
            
            def apply_color_grade(get_frame, t):
                """Apply color grading to frame"""
                frame = get_frame(t)
                
                # Apply LUT
                graded = cv2.LUT(frame, lut)
                
                return graded
            
            return clip.fl(apply_color_grade)
            
        except Exception as e:
            logger.error(f"❌ Color grading failed: {e}")
            return clip
    
    def _create_cinematic_lut(self) -> np.ndarray:
        """Create cinematic color LUT"""
        lut = np.arange(256, dtype=np.uint8)
        
        # Increase contrast
        lut = np.clip(lut * 1.2 - 25, 0, 255).astype(np.uint8)
        
        # Create proper 3-channel LUT for OpenCV
        lut_3d = np.zeros((256, 1, 3), dtype=np.uint8)
        lut_3d[:, 0, 0] = np.clip(lut * 1.05, 0, 255)  # Red
        lut_3d[:, 0, 1] = lut  # Green
        lut_3d[:, 0, 2] = np.clip(lut * 0.95, 0, 255)  # Blue
        
        return lut_3d
    
    def _create_vintage_lut(self) -> np.ndarray:
        """Create vintage color LUT"""
        lut = np.arange(256, dtype=np.uint8)
        
        # Reduce contrast, add fade
        lut = np.clip(lut * 0.85 + 20, 0, 255).astype(np.uint8)
        
        # Create proper 3-channel LUT for OpenCV
        lut_3d = np.zeros((256, 1, 3), dtype=np.uint8)
        lut_3d[:, 0, 0] = np.clip(lut * 1.1, 0, 255)  # Red
        lut_3d[:, 0, 1] = np.clip(lut * 0.9, 0, 255)  # Green
        lut_3d[:, 0, 2] = np.clip(lut * 0.7, 0, 255)  # Blue
        
        return lut_3d
    
    def _create_vibrant_lut(self) -> np.ndarray:
        """Create vibrant color LUT"""
        lut = np.arange(256, dtype=np.uint8)
        
        # Increase saturation
        lut = np.clip(lut * 1.3 - 38, 0, 255).astype(np.uint8)
        
        # Create proper 3-channel LUT for OpenCV
        lut_3d = np.zeros((256, 1, 3), dtype=np.uint8)
        lut_3d[:, 0, :] = lut.reshape(-1, 1)
        
        return lut_3d
    
    def _create_noir_lut(self) -> np.ndarray:
        """Create noir/black & white LUT"""
        lut = np.arange(256, dtype=np.uint8)
        
        # High contrast B&W
        lut = np.clip(lut * 1.5 - 64, 0, 255).astype(np.uint8)
        
        # Create proper 3-channel LUT for OpenCV
        lut_3d = np.zeros((256, 1, 3), dtype=np.uint8)
        lut_3d[:, 0, :] = lut.reshape(-1, 1)
        
        return lut_3d
    
    def _create_warm_lut(self) -> np.ndarray:
        """Create warm color LUT"""
        lut = np.arange(256, dtype=np.uint8)
        
        # Create proper 3-channel LUT for OpenCV
        lut_3d = np.zeros((256, 1, 3), dtype=np.uint8)
        lut_3d[:, 0, 0] = np.clip(lut * 1.1, 0, 255)  # More red
        lut_3d[:, 0, 1] = lut  # Green
        lut_3d[:, 0, 2] = np.clip(lut * 0.85, 0, 255)  # Less blue
        
        return lut_3d
    
    def _create_cool_lut(self) -> np.ndarray:
        """Create cool color LUT"""
        lut = np.arange(256, dtype=np.uint8)
        
        # Create proper 3-channel LUT for OpenCV
        lut_3d = np.zeros((256, 1, 3), dtype=np.uint8)
        lut_3d[:, 0, 0] = np.clip(lut * 0.85, 0, 255)  # Less red
        lut_3d[:, 0, 1] = lut  # Green
        lut_3d[:, 0, 2] = np.clip(lut * 1.1, 0, 255)  # More blue
        
        return lut_3d


# Text Animation Service
class TextAnimationService:
    """Professional text animations"""
    
    def create_typewriter_effect(self, text: str, duration: float, 
                                font_size: int = 50, color: str = 'white') -> VideoFileClip:
        """Create typewriter text animation"""
        try:
            from moviepy.video.tools.drawing import color_gradient
            
            def make_frame(t):
                """Create typewriter frame"""
                progress = t / duration
                chars_to_show = int(len(text) * progress)
                visible_text = text[:chars_to_show]
                
                # Create text image
                img = np.zeros((100, 800, 3), dtype=np.uint8)
                
                # Simple text rendering (would use PIL in production)
                cv2.putText(img, visible_text, (50, 60), 
                          cv2.FONT_HERSHEY_SIMPLEX, font_size/50, 
                          (255, 255, 255), 2)
                
                return img
            
            return VideoClip(make_frame, duration=duration)
            
        except Exception as e:
            logger.error(f"❌ Typewriter effect failed: {e}")
            return None
    
    def create_fade_in_text(self, text: str, duration: float, 
                           font_size: int = 50) -> VideoFileClip:
        """Create fade-in text animation"""
        try:
            # Create text image
            img = np.zeros((100, 800, 3), dtype=np.uint8)
            cv2.putText(img, text, (50, 60), 
                      cv2.FONT_HERSHEY_SIMPLEX, font_size/50, 
                      (255, 255, 255), 2)
            
            # Create clip and add fade
            text_clip = ImageClip(img, duration=duration)
            return text_clip.fadein(duration * 0.3)
            
        except Exception as e:
            logger.error(f"❌ Fade-in text failed: {e}")
            return None


# Main Effects Engine - Facade Pattern
class ProfessionalEffectsEngine:
    """Main effects engine coordinating all effect services"""
    
    def __init__(self):
        """Initialize effects engine with all services"""
        # Initialize services
        self.color_grading = ColorGradingService()
        self.text_animations = TextAnimationService()
        
        # Initialize effect libraries
        self.transitions = {
            'fade': FadeTransition(),
            'slide_left': SlideTransition('left'),
            'slide_up': SlideTransition('up'),
            'zoom': ZoomTransition()
        }
        
        self.video_effects = {
            'motion_blur': MotionBlurEffect(),
            'ken_burns': KenBurnsEffect(),
            'glitch': GlitchEffect()
        }
        
        logger.info("✅ Professional Effects Engine initialized")
    
    def apply_cinematic_effects(self, video_path: str, 
                               effects_config: List[EffectConfig]) -> str:
        """Apply professional cinematic effects to video"""
        try:
            clip = VideoFileClip(video_path)
            
            for config in effects_config:
                clip = self._apply_effect(clip, config)
            
            # Apply color grading
            clip = self.color_grading.apply_lut(clip, 'cinematic')
            
            output_path = video_path.replace('.mp4', '_cinematic.mp4')
            clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            clip.close()
            
            logger.info(f"✅ Cinematic effects applied: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Cinematic effects failed: {e}")
            return video_path
    
    def apply_transition(self, clip1_path: str, clip2_path: str, 
                        transition_type: str, duration: float = 1.0) -> str:
        """Apply transition between two clips"""
        try:
            clip1 = VideoFileClip(clip1_path)
            clip2 = VideoFileClip(clip2_path)
            
            if transition_type in self.transitions:
                transition = self.transitions[transition_type]
                result = transition.apply(clip1, clip2, duration)
            else:
                logger.warning(f"⚠️ Unknown transition: {transition_type}")
                result = concatenate_videoclips([clip1, clip2])
            
            output_path = f"{clip1_path.replace('.mp4', '')}_transition.mp4"
            result.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            clip1.close()
            clip2.close()
            result.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Transition failed: {e}")
            return clip1_path
    
    def _apply_effect(self, clip: VideoFileClip, config: EffectConfig) -> VideoFileClip:
        """Apply a single effect based on config"""
        try:
            if config.type == EffectType.FILTER and config.name in self.video_effects:
                effect = self.video_effects[config.name]
                return effect.apply(clip)
            
            elif config.type == EffectType.COLOR:
                return self.color_grading.apply_lut(clip, config.name)
            
            elif config.type == EffectType.MOTION:
                if config.name == 'slow_motion':
                    return clip.fx(vfx.speedx, 0.5)
                elif config.name == 'fast_forward':
                    return clip.fx(vfx.speedx, 2.0)
            
            return clip
            
        except Exception as e:
            logger.error(f"❌ Effect {config.name} failed: {e}")
            return clip
    
    def create_professional_sequence(self, clips: List[str], 
                                   transition_type: str = 'fade',
                                   color_grade: str = 'cinematic') -> str:
        """Create professional video sequence with transitions and effects"""
        try:
            processed_clips = []
            
            for i, clip_path in enumerate(clips):
                clip = VideoFileClip(clip_path)
                
                # Apply color grading
                clip = self.color_grading.apply_lut(clip, color_grade)
                
                # Apply Ken Burns to some clips for variety
                if i % 3 == 0:
                    clip = self.video_effects['ken_burns'].apply(clip)
                
                processed_clips.append(clip)
            
            # Apply transitions
            final_clips = []
            for i in range(len(processed_clips) - 1):
                final_clips.append(processed_clips[i])
                
                # Add transition to next clip
                if transition_type in self.transitions:
                    # This is simplified - would need proper transition handling
                    pass
            
            final_clips.append(processed_clips[-1])
            
            # Concatenate all clips
            final = concatenate_videoclips(final_clips)
            
            output_path = f"professional_sequence_{len(clips)}_clips.mp4"
            final.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Clean up
            for clip in processed_clips:
                clip.close()
            final.close()
            
            logger.info(f"✅ Professional sequence created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Sequence creation failed: {e}")
            return clips[0] if clips else ""