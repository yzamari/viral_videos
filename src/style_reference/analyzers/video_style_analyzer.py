"""
Video Style Analyzer
Analyzes videos to extract comprehensive style attributes
"""
import os
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
import colorsys
from collections import Counter
from sklearn.cluster import KMeans

from ..models.style_reference import StyleReference
from ..models.style_attributes import (
    ReferenceType, ColorPalette, Typography, Composition,
    MotionStyle, VisualEffect, LogoPlacement
)

logger = logging.getLogger(__name__)


class VideoStyleAnalyzer:
    """Analyzes videos to extract style attributes"""
    
    def __init__(self, ai_service=None):
        """Initialize analyzer with optional AI service for advanced analysis"""
        self.ai_service = ai_service
        self.frame_sample_rate = 30  # Sample every 30 frames
        self.color_clusters = 5  # Number of color clusters to extract
        
    async def analyze_video(self, video_path: str, name: str = None) -> StyleReference:
        """Extract comprehensive style from video"""
        logger.info(f"🎥 Analyzing video style: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        # Extract sample frames
        frames = self._extract_sample_frames(video_path)
        logger.info(f"📊 Extracted {len(frames)} sample frames")
        
        # Get video properties
        tech_specs = self._get_video_specs(video_path)
        
        # Analyze different aspects
        color_palette = self._analyze_color_palette(frames)
        typography = await self._analyze_typography(frames) if self.ai_service else self._basic_typography()
        composition = self._analyze_composition(frames)
        motion_style = self._analyze_motion(video_path, frames)
        visual_effects = self._detect_visual_effects(frames)
        
        # Create style reference
        style_ref = StyleReference(
            reference_id=f"style_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=name or os.path.basename(video_path),
            reference_type=ReferenceType.VIDEO,
            source_path=video_path,
            template_id=None,
            color_palette=color_palette,
            typography=typography,
            composition=composition,
            motion_style=motion_style,
            visual_effects=visual_effects,
            logo_placement=self._detect_logo_placement(frames),
            watermark=None,  # TODO: Implement watermark detection
            lower_thirds=None,  # TODO: Implement lower thirds detection
            aspect_ratio=tech_specs['aspect_ratio'],
            resolution=tech_specs['resolution'],
            frame_rate=tech_specs['fps'],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=[],
            description=None,
            confidence_scores=self._calculate_confidence_scores()
        )
        
        logger.info(f"✅ Video style analysis complete")
        return style_ref
    
    def _extract_sample_frames(self, video_path: str) -> List[np.ndarray]:
        """Extract sample frames from video"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % self.frame_sample_rate == 0:
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            frame_count += 1
            
            # Limit to 100 frames max
            if len(frames) >= 100:
                break
        
        cap.release()
        return frames
    
    def _get_video_specs(self, video_path: str) -> Dict[str, any]:
        """Get technical specifications of video"""
        cap = cv2.VideoCapture(video_path)
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        cap.release()
        
        # Determine aspect ratio
        gcd = np.gcd(width, height)
        aspect_ratio = f"{width//gcd}:{height//gcd}"
        
        return {
            'width': width,
            'height': height,
            'resolution': f"{width}x{height}",
            'aspect_ratio': aspect_ratio,
            'fps': fps,
            'frame_count': frame_count,
            'duration': frame_count / fps if fps > 0 else 0
        }
    
    def _analyze_color_palette(self, frames: List[np.ndarray]) -> ColorPalette:
        """Extract dominant colors from frames"""
        # Sample pixels from all frames
        all_pixels = []
        for frame in frames[::5]:  # Sample every 5th frame
            # Resize for faster processing
            small_frame = cv2.resize(frame, (150, 150))
            pixels = small_frame.reshape(-1, 3)
            all_pixels.extend(pixels[::10])  # Sample every 10th pixel
        
        all_pixels = np.array(all_pixels)
        
        # Use KMeans to find dominant colors
        kmeans = KMeans(n_clusters=self.color_clusters, random_state=42)
        kmeans.fit(all_pixels)
        
        # Get cluster centers (dominant colors)
        colors = kmeans.cluster_centers_.astype(int)
        
        # Sort by frequency
        labels = kmeans.labels_
        color_counts = Counter(labels)
        sorted_colors = [colors[i] for i, _ in color_counts.most_common()]
        
        # Convert to hex
        hex_colors = ['#%02x%02x%02x' % tuple(color) for color in sorted_colors]
        
        # Analyze color properties
        brightness = np.mean([self._get_brightness(color) for color in sorted_colors])
        saturation = np.mean([self._get_saturation(color) for color in sorted_colors])
        
        # Determine mood
        mood = self._determine_color_mood(sorted_colors, brightness, saturation)
        
        return ColorPalette(
            primary_color=hex_colors[0],
            secondary_color=hex_colors[1] if len(hex_colors) > 1 else hex_colors[0],
            accent_color=hex_colors[2] if len(hex_colors) > 2 else hex_colors[1],
            background_colors=hex_colors[3:] if len(hex_colors) > 3 else [],
            text_colors=self._estimate_text_colors(sorted_colors),
            saturation_level=saturation,
            brightness_level=brightness,
            contrast_ratio=self._calculate_contrast_ratio(sorted_colors),
            mood=mood
        )
    
    def _get_brightness(self, rgb: np.ndarray) -> float:
        """Calculate brightness of RGB color (0-1)"""
        return np.mean(rgb) / 255.0
    
    def _get_saturation(self, rgb: np.ndarray) -> float:
        """Calculate saturation of RGB color (0-1)"""
        r, g, b = rgb / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return s
    
    def _determine_color_mood(self, colors: List[np.ndarray], 
                            brightness: float, saturation: float) -> str:
        """Determine overall color mood"""
        if brightness > 0.7:
            if saturation > 0.5:
                return "vibrant"
            else:
                return "bright"
        elif brightness < 0.3:
            return "dark"
        elif saturation > 0.6:
            return "rich"
        elif saturation < 0.2:
            return "muted"
        else:
            # Check color temperature
            avg_color = np.mean(colors[:3], axis=0)
            if avg_color[0] > avg_color[2]:  # More red than blue
                return "warm"
            else:
                return "cool"
    
    def _estimate_text_colors(self, bg_colors: List[np.ndarray]) -> List[str]:
        """Estimate suitable text colors based on background"""
        text_colors = []
        
        for bg_color in bg_colors[:2]:  # Check first two background colors
            brightness = self._get_brightness(bg_color)
            if brightness > 0.5:
                # Dark text for light background
                text_colors.append("#000000")
            else:
                # Light text for dark background
                text_colors.append("#FFFFFF")
        
        return text_colors
    
    def _calculate_contrast_ratio(self, colors: List[np.ndarray]) -> float:
        """Calculate average contrast ratio between colors"""
        if len(colors) < 2:
            return 1.0
        
        # Simple contrast calculation between first two colors
        brightness1 = self._get_brightness(colors[0])
        brightness2 = self._get_brightness(colors[1])
        
        return abs(brightness1 - brightness2)
    
    def _analyze_composition(self, frames: List[np.ndarray]) -> Composition:
        """Analyze visual composition of frames"""
        # Simple composition analysis
        # TODO: Implement more sophisticated composition analysis
        
        return Composition(
            rule_of_thirds_adherence=0.7,  # Placeholder
            symmetry_score=0.5,  # Placeholder
            primary_layout="centered",  # Placeholder
            text_placement_zones=["lower-third", "center"],  # Common zones
            margin_ratio=0.1,
            padding_ratio=0.05,
            focal_point_strategy="center-weighted",
            depth_layers=3
        )
    
    def _analyze_motion(self, video_path: str, frames: List[np.ndarray]) -> MotionStyle:
        """Analyze motion characteristics"""
        # Calculate average shot duration by detecting scene changes
        scene_changes = self._detect_scene_changes(frames)
        avg_shot_duration = len(frames) / (len(scene_changes) + 1) * (self.frame_sample_rate / 30.0)
        
        # Detect motion intensity
        motion_intensity = self._calculate_motion_intensity(frames)
        
        # Determine pacing
        if avg_shot_duration < 2:
            pacing = "fast"
        elif avg_shot_duration > 5:
            pacing = "slow"
        else:
            pacing = "medium"
        
        return MotionStyle(
            camera_movement="dynamic" if motion_intensity > 0.5 else "static",
            transition_style="cut",  # Most common
            average_shot_duration=avg_shot_duration,
            movement_intensity=motion_intensity,
            text_animation_type=None,  # TODO: Detect text animations
            element_animation_style=None,  # TODO: Detect element animations
            pacing=pacing,
            rhythm_pattern=None
        )
    
    def _detect_scene_changes(self, frames: List[np.ndarray]) -> List[int]:
        """Detect scene changes in frames"""
        scene_changes = []
        
        for i in range(1, len(frames)):
            # Calculate histogram difference
            hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()
            
            # Compare histograms
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Threshold for scene change
            if correlation < 0.7:
                scene_changes.append(i)
        
        return scene_changes
    
    def _calculate_motion_intensity(self, frames: List[np.ndarray]) -> float:
        """Calculate overall motion intensity"""
        motion_scores = []
        
        for i in range(1, len(frames)):
            # Convert to grayscale
            gray1 = cv2.cvtColor(frames[i-1], cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            # Calculate magnitude
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            motion_scores.append(np.mean(magnitude))
        
        # Normalize to 0-1
        if motion_scores:
            max_motion = max(motion_scores)
            if max_motion > 0:
                return min(np.mean(motion_scores) / max_motion, 1.0)
        
        return 0.0
    
    def _detect_visual_effects(self, frames: List[np.ndarray]) -> List[VisualEffect]:
        """Detect visual effects applied to frames"""
        effects = []
        
        # Check for blur
        blur_score = self._detect_blur(frames)
        if blur_score > 0.3:
            effects.append(VisualEffect(
                effect_type="blur",
                intensity=blur_score,
                apply_to="background",
                parameters={"type": "gaussian"}
            ))
        
        # Check for grain/noise
        noise_score = self._detect_noise(frames)
        if noise_score > 0.2:
            effects.append(VisualEffect(
                effect_type="grain",
                intensity=noise_score,
                apply_to="full-frame",
                parameters={"type": "film-grain"}
            ))
        
        return effects
    
    def _detect_blur(self, frames: List[np.ndarray]) -> float:
        """Detect blur level in frames"""
        blur_scores = []
        
        for frame in frames[::10]:  # Sample every 10th frame
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Lower variance indicates more blur
            blur_score = 1.0 - min(laplacian_var / 1000.0, 1.0)
            blur_scores.append(blur_score)
        
        return np.mean(blur_scores) if blur_scores else 0.0
    
    def _detect_noise(self, frames: List[np.ndarray]) -> float:
        """Detect noise/grain level in frames"""
        # Simple noise detection
        # TODO: Implement more sophisticated noise detection
        return 0.1  # Placeholder
    
    def _detect_logo_placement(self, frames: List[np.ndarray]) -> Optional[LogoPlacement]:
        """Detect logo placement in frames"""
        # TODO: Implement logo detection using template matching or ML
        return None
    
    async def _analyze_typography(self, frames: List[np.ndarray]) -> Typography:
        """Analyze typography using AI service"""
        # TODO: Implement AI-based typography analysis
        return self._basic_typography()
    
    def _basic_typography(self) -> Typography:
        """Return basic typography settings"""
        return Typography(
            primary_font_family=None,
            secondary_font_family=None,
            title_size_ratio=0.1,
            body_size_ratio=0.05,
            font_weight="regular",
            letter_spacing=1.0,
            line_height=1.2,
            has_shadow=False,
            has_outline=False,
            text_animation_style=None
        )
    
    def _calculate_confidence_scores(self) -> Dict[str, float]:
        """Calculate confidence scores for different aspects"""
        return {
            "color_palette": 0.9,  # High confidence with KMeans
            "composition": 0.6,    # Basic analysis
            "motion_style": 0.7,   # Optical flow analysis
            "typography": 0.3,     # Basic without AI
            "effects": 0.5         # Simple detection
        }