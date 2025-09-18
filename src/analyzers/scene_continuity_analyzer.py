"""
Scene Continuity Analyzer - Ensures smooth visual flow between clips
Implements SOLID principles for modular scene analysis
"""

import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Protocol
from dataclasses import dataclass
from enum import Enum
import logging
from moviepy.editor import VideoFileClip
import colorsys

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


# Interface Segregation - Separate interfaces for different analysis types
class IColorAnalyzer(Protocol):
    """Interface for color analysis"""
    def analyze_color_palette(self, frame: np.ndarray) -> Dict[str, Any]:
        ...
    
    def calculate_color_distance(self, palette1: Dict, palette2: Dict) -> float:
        ...


class IMotionAnalyzer(Protocol):
    """Interface for motion analysis"""
    def analyze_motion_vectors(self, frame1: np.ndarray, frame2: np.ndarray) -> Dict[str, Any]:
        ...
    
    def predict_camera_movement(self, frames: List[np.ndarray]) -> str:
        ...


class IObjectTracker(Protocol):
    """Interface for object tracking"""
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        ...
    
    def track_objects_across_frames(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        ...


class ICompositionAnalyzer(Protocol):
    """Interface for composition analysis"""
    def analyze_composition(self, frame: np.ndarray) -> Dict[str, Any]:
        ...
    
    def check_rule_of_thirds(self, frame: np.ndarray) -> float:
        ...


# Single Responsibility - Data classes
@dataclass
class SceneFeatures:
    """Features extracted from a scene"""
    dominant_colors: List[Tuple[int, int, int]]
    color_histogram: np.ndarray
    brightness: float
    contrast: float
    saturation: float
    motion_intensity: float
    camera_movement: str  # 'static', 'pan', 'zoom', 'tilt'
    detected_objects: List[str]
    composition_score: float
    timestamp: float


@dataclass
class ContinuityScore:
    """Continuity score between scenes"""
    overall_score: float
    color_continuity: float
    motion_continuity: float
    object_continuity: float
    composition_continuity: float
    lighting_continuity: float


@dataclass
class ContinuityAnalysis:
    """Complete continuity analysis result"""
    scene_features: List[SceneFeatures]
    continuity_scores: List[ContinuityScore]
    overall_flow_score: float
    issues: List[str]
    suggestions: List[str]
    recommended_transitions: List[str]


# Abstract base classes
class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """Perform analysis"""
        pass


# Concrete implementations
class ColorPaletteAnalyzer(BaseAnalyzer):
    """Analyzes color palettes and continuity"""
    
    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze color palette of a frame"""
        try:
            # Convert to RGB if needed
            if len(frame.shape) == 2:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif frame.shape[2] == 4:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            else:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Extract dominant colors using k-means
            dominant_colors = self._extract_dominant_colors(frame_rgb, k=5)
            
            # Calculate color histogram
            hist = self._calculate_color_histogram(frame_rgb)
            
            # Calculate color properties
            brightness = np.mean(frame_rgb)
            contrast = np.std(frame_rgb)
            saturation = self._calculate_saturation(frame_rgb)
            
            return {
                'dominant_colors': dominant_colors,
                'histogram': hist,
                'brightness': brightness,
                'contrast': contrast,
                'saturation': saturation
            }
            
        except Exception as e:
            logger.error(f"❌ Color analysis failed: {e}")
            return {}
    
    def _extract_dominant_colors(self, frame: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using k-means clustering"""
        try:
            # Reshape frame to list of pixels
            pixels = frame.reshape((-1, 3))
            
            # Sample pixels for performance
            sample_size = min(1000, len(pixels))
            sample_indices = np.random.choice(len(pixels), sample_size, replace=False)
            pixel_sample = pixels[sample_indices]
            
            # Simple k-means implementation
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(pixel_sample)
            
            # Get cluster centers as dominant colors
            colors = kmeans.cluster_centers_.astype(int)
            
            return [tuple(color) for color in colors]
            
        except ImportError:
            # Fallback without sklearn
            return self._extract_dominant_colors_simple(frame, k)
        except Exception as e:
            logger.error(f"❌ Dominant color extraction failed: {e}")
            return []
    
    def _extract_dominant_colors_simple(self, frame: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Simple dominant color extraction without sklearn"""
        # Quantize colors
        quantized = (frame // 32) * 32
        
        # Get unique colors and their counts
        reshaped = quantized.reshape(-1, 3)
        unique_colors, counts = np.unique(reshaped, axis=0, return_counts=True)
        
        # Get top k colors
        top_indices = np.argsort(counts)[-k:]
        dominant_colors = unique_colors[top_indices]
        
        return [tuple(color) for color in dominant_colors]
    
    def _calculate_color_histogram(self, frame: np.ndarray) -> np.ndarray:
        """Calculate color histogram"""
        hist_r = cv2.calcHist([frame], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([frame], [2], None, [256], [0, 256])
        
        return np.concatenate([hist_r, hist_g, hist_b]).flatten()
    
    def _calculate_saturation(self, frame: np.ndarray) -> float:
        """Calculate average saturation"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        return np.mean(hsv[:, :, 1])
    
    def calculate_color_distance(self, palette1: List[Tuple], palette2: List[Tuple]) -> float:
        """Calculate distance between two color palettes"""
        if not palette1 or not palette2:
            return 1.0
        
        total_distance = 0
        comparisons = 0
        
        for color1 in palette1[:3]:  # Compare top 3 colors
            for color2 in palette2[:3]:
                # Calculate Euclidean distance in RGB space
                distance = np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))
                total_distance += distance
                comparisons += 1
        
        # Normalize to 0-1 range
        if comparisons > 0:
            avg_distance = total_distance / comparisons
            normalized = avg_distance / 441.67  # Max possible distance in RGB
            return min(1.0, normalized)
        
        return 0.5


class MotionFlowAnalyzer(BaseAnalyzer):
    """Analyzes motion and camera movement"""
    
    def analyze(self, frame_pair: Tuple[np.ndarray, np.ndarray]) -> Dict[str, Any]:
        """Analyze motion between two frames"""
        try:
            frame1, frame2 = frame_pair
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                gray1, gray2, None, 
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0
            )
            
            # Analyze flow
            motion_intensity = np.mean(np.abs(flow))
            camera_movement = self._detect_camera_movement(flow)
            
            return {
                'motion_intensity': motion_intensity,
                'camera_movement': camera_movement,
                'flow_field': flow
            }
            
        except Exception as e:
            logger.error(f"❌ Motion analysis failed: {e}")
            return {
                'motion_intensity': 0,
                'camera_movement': 'static',
                'flow_field': None
            }
    
    def _detect_camera_movement(self, flow: np.ndarray) -> str:
        """Detect type of camera movement from optical flow"""
        if flow is None:
            return 'static'
        
        # Calculate average flow vectors
        mean_x = np.mean(flow[:, :, 0])
        mean_y = np.mean(flow[:, :, 1])
        std_x = np.std(flow[:, :, 0])
        std_y = np.std(flow[:, :, 1])
        
        # Detect movement patterns
        if abs(mean_x) < 0.5 and abs(mean_y) < 0.5:
            return 'static'
        elif abs(mean_x) > abs(mean_y) * 2:
            return 'pan_horizontal'
        elif abs(mean_y) > abs(mean_x) * 2:
            return 'tilt_vertical'
        elif std_x > 5 and std_y > 5:
            return 'zoom'
        else:
            return 'complex'


class CompositionAnalyzer(BaseAnalyzer):
    """Analyzes frame composition and aesthetics"""
    
    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze composition of a frame"""
        try:
            # Check rule of thirds
            thirds_score = self._check_rule_of_thirds(frame)
            
            # Check golden ratio
            golden_score = self._check_golden_ratio(frame)
            
            # Check symmetry
            symmetry_score = self._check_symmetry(frame)
            
            # Check leading lines
            lines_score = self._detect_leading_lines(frame)
            
            # Overall composition score
            composition_score = (thirds_score + golden_score + symmetry_score + lines_score) / 4
            
            return {
                'composition_score': composition_score,
                'rule_of_thirds': thirds_score,
                'golden_ratio': golden_score,
                'symmetry': symmetry_score,
                'leading_lines': lines_score
            }
            
        except Exception as e:
            logger.error(f"❌ Composition analysis failed: {e}")
            return {'composition_score': 0.5}
    
    def _check_rule_of_thirds(self, frame: np.ndarray) -> float:
        """Check if important elements follow rule of thirds"""
        h, w = frame.shape[:2]
        
        # Define rule of thirds lines
        v_lines = [w // 3, 2 * w // 3]
        h_lines = [h // 3, 2 * h // 3]
        
        # Detect edges
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        edges = cv2.Canny(gray, 50, 150)
        
        # Check edge density near thirds lines
        score = 0
        for x in v_lines:
            region = edges[:, max(0, x-10):min(w, x+10)]
            score += np.sum(region) / (h * 20 * 255)
        
        for y in h_lines:
            region = edges[max(0, y-10):min(h, y+10), :]
            score += np.sum(region) / (w * 20 * 255)
        
        return min(1.0, score / 4)
    
    def _check_golden_ratio(self, frame: np.ndarray) -> float:
        """Check golden ratio composition"""
        h, w = frame.shape[:2]
        
        # Golden ratio points
        golden = 0.618
        points = [
            (int(w * golden), int(h * golden)),
            (int(w * (1 - golden)), int(h * golden)),
            (int(w * golden), int(h * (1 - golden))),
            (int(w * (1 - golden)), int(h * (1 - golden)))
        ]
        
        # Check for important features near golden points
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        
        score = 0
        for x, y in points:
            region = gray[max(0, y-20):min(h, y+20), max(0, x-20):min(w, x+20)]
            # Check variance (indicates interesting content)
            if region.size > 0:
                variance = np.var(region)
                score += min(1.0, variance / 1000)
        
        return score / 4
    
    def _check_symmetry(self, frame: np.ndarray) -> float:
        """Check frame symmetry"""
        h, w = frame.shape[:2]
        
        # Compare left and right halves
        left = frame[:, :w//2]
        right = frame[:, w//2:]
        
        # Flip right half for comparison
        right_flipped = cv2.flip(right, 1)
        
        # Resize if needed
        if left.shape != right_flipped.shape:
            right_flipped = cv2.resize(right_flipped, (left.shape[1], left.shape[0]))
        
        # Calculate similarity
        difference = cv2.absdiff(left, right_flipped)
        similarity = 1.0 - (np.mean(difference) / 255.0)
        
        # Perfect symmetry is not always good, so adjust score
        if similarity > 0.9:
            return 0.8
        elif similarity > 0.7:
            return 0.9
        elif similarity > 0.5:
            return 0.7
        else:
            return 0.5
    
    def _detect_leading_lines(self, frame: np.ndarray) -> float:
        """Detect leading lines in composition"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        
        # Detect lines using Hough transform
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return 0.3
        
        # Score based on number and quality of lines
        num_lines = len(lines)
        if num_lines == 0:
            return 0.3
        elif num_lines < 3:
            return 0.6
        elif num_lines < 10:
            return 0.8
        else:
            return 0.7  # Too many lines can be cluttered


# Main Scene Continuity Analyzer
class SceneContinuityAnalyzer:
    """Analyzes and ensures visual continuity between scenes"""
    
    def __init__(self):
        """Initialize with analyzer components"""
        self.color_analyzer = ColorPaletteAnalyzer()
        self.motion_analyzer = MotionFlowAnalyzer()
        self.composition_analyzer = CompositionAnalyzer()
        
        logger.info("✅ Scene Continuity Analyzer initialized")
    
    def ensure_visual_continuity(self, video_clips: List[str]) -> ContinuityAnalysis:
        """
        Analyze visual continuity across video clips
        
        Args:
            video_clips: List of video clip file paths
            
        Returns:
            ContinuityAnalysis with detailed results
        """
        logger.info(f"🔍 Analyzing continuity for {len(video_clips)} clips")
        
        # Extract features from each clip
        scene_features = []
        for clip_path in video_clips:
            features = self._extract_scene_features(clip_path)
            scene_features.append(features)
        
        # Calculate continuity scores between consecutive scenes
        continuity_scores = []
        for i in range(len(scene_features) - 1):
            score = self._calculate_continuity_score(
                scene_features[i], 
                scene_features[i + 1]
            )
            continuity_scores.append(score)
        
        # Calculate overall flow score
        if continuity_scores:
            overall_flow = np.mean([s.overall_score for s in continuity_scores])
        else:
            overall_flow = 0.5
        
        # Identify issues and generate suggestions
        issues, suggestions = self._identify_continuity_issues(
            scene_features, continuity_scores
        )
        
        # Recommend transitions
        recommended_transitions = self._recommend_transitions(continuity_scores)
        
        analysis = ContinuityAnalysis(
            scene_features=scene_features,
            continuity_scores=continuity_scores,
            overall_flow_score=overall_flow,
            issues=issues,
            suggestions=suggestions,
            recommended_transitions=recommended_transitions
        )
        
        logger.info(f"✅ Continuity analysis complete. Flow score: {overall_flow:.2f}")
        
        return analysis
    
    def _extract_scene_features(self, clip_path: str) -> SceneFeatures:
        """Extract visual features from a video clip"""
        try:
            with VideoFileClip(clip_path) as clip:
                # Sample frames
                duration = clip.duration
                sample_times = [0, duration * 0.25, duration * 0.5, duration * 0.75, max(0, duration - 0.1)]
                
                frames = []
                for t in sample_times:
                    if t < duration:
                        frame = clip.get_frame(t)
                        frames.append(frame)
                
                if not frames:
                    logger.warning(f"⚠️ No frames extracted from {clip_path}")
                    return self._create_default_features()
                
                # Analyze first frame for static features
                first_frame = frames[0]
                color_analysis = self.color_analyzer.analyze(first_frame)
                composition_analysis = self.composition_analyzer.analyze(first_frame)
                
                # Analyze motion between frames
                motion_intensities = []
                camera_movements = []
                
                for i in range(len(frames) - 1):
                    motion_analysis = self.motion_analyzer.analyze((frames[i], frames[i + 1]))
                    motion_intensities.append(motion_analysis.get('motion_intensity', 0))
                    camera_movements.append(motion_analysis.get('camera_movement', 'static'))
                
                # Determine dominant camera movement
                if camera_movements:
                    camera_movement = max(set(camera_movements), key=camera_movements.count)
                else:
                    camera_movement = 'static'
                
                return SceneFeatures(
                    dominant_colors=color_analysis.get('dominant_colors', []),
                    color_histogram=color_analysis.get('histogram', np.array([])),
                    brightness=color_analysis.get('brightness', 128),
                    contrast=color_analysis.get('contrast', 50),
                    saturation=color_analysis.get('saturation', 0.5),
                    motion_intensity=np.mean(motion_intensities) if motion_intensities else 0,
                    camera_movement=camera_movement,
                    detected_objects=[],  # Would use object detection here
                    composition_score=composition_analysis.get('composition_score', 0.5),
                    timestamp=0
                )
                
        except Exception as e:
            logger.error(f"❌ Feature extraction failed for {clip_path}: {e}")
            return self._create_default_features()
    
    def _create_default_features(self) -> SceneFeatures:
        """Create default scene features"""
        return SceneFeatures(
            dominant_colors=[(128, 128, 128)],
            color_histogram=np.zeros(768),
            brightness=128,
            contrast=50,
            saturation=0.5,
            motion_intensity=0,
            camera_movement='static',
            detected_objects=[],
            composition_score=0.5,
            timestamp=0
        )
    
    def _calculate_continuity_score(self, scene1: SceneFeatures, 
                                   scene2: SceneFeatures) -> ContinuityScore:
        """Calculate continuity score between two scenes"""
        
        # Color continuity
        color_distance = self.color_analyzer.calculate_color_distance(
            scene1.dominant_colors, scene2.dominant_colors
        )
        color_continuity = 1.0 - color_distance
        
        # Motion continuity
        motion_diff = abs(scene1.motion_intensity - scene2.motion_intensity)
        motion_continuity = 1.0 - min(1.0, motion_diff / 10)
        
        # Lighting continuity
        brightness_diff = abs(scene1.brightness - scene2.brightness)
        lighting_continuity = 1.0 - min(1.0, brightness_diff / 128)
        
        # Composition continuity
        comp_diff = abs(scene1.composition_score - scene2.composition_score)
        composition_continuity = 1.0 - comp_diff
        
        # Object continuity (simplified for now)
        object_continuity = 0.7  # Would use actual object tracking
        
        # Overall score
        overall = (
            color_continuity * 0.3 +
            motion_continuity * 0.2 +
            lighting_continuity * 0.2 +
            composition_continuity * 0.15 +
            object_continuity * 0.15
        )
        
        return ContinuityScore(
            overall_score=overall,
            color_continuity=color_continuity,
            motion_continuity=motion_continuity,
            object_continuity=object_continuity,
            composition_continuity=composition_continuity,
            lighting_continuity=lighting_continuity
        )
    
    def _identify_continuity_issues(self, features: List[SceneFeatures], 
                                   scores: List[ContinuityScore]) -> Tuple[List[str], List[str]]:
        """Identify continuity issues and generate suggestions"""
        issues = []
        suggestions = []
        
        for i, score in enumerate(scores):
            if score.overall_score < 0.5:
                issues.append(f"Poor continuity between clips {i+1} and {i+2}")
                
                if score.color_continuity < 0.5:
                    suggestions.append(f"Add color correction between clips {i+1} and {i+2}")
                
                if score.motion_continuity < 0.5:
                    suggestions.append(f"Use motion blur transition between clips {i+1} and {i+2}")
                
                if score.lighting_continuity < 0.5:
                    suggestions.append(f"Apply brightness matching between clips {i+1} and {i+2}")
        
        # Check for jarring camera movements
        for i in range(len(features) - 1):
            if (features[i].camera_movement == 'static' and 
                features[i+1].camera_movement in ['zoom', 'pan_horizontal']):
                issues.append(f"Abrupt camera movement change at clip {i+2}")
                suggestions.append(f"Add smooth transition or match camera movement")
        
        return issues, suggestions
    
    def _recommend_transitions(self, scores: List[ContinuityScore]) -> List[str]:
        """Recommend appropriate transitions based on continuity scores"""
        recommendations = []
        
        for score in scores:
            if score.overall_score > 0.8:
                # Good continuity - simple cut or fast fade
                recommendations.append("cut")
            elif score.color_continuity < 0.5:
                # Poor color match - use fade
                recommendations.append("fade")
            elif score.motion_continuity < 0.5:
                # Motion mismatch - use motion blur
                recommendations.append("motion_blur")
            elif score.composition_continuity < 0.5:
                # Composition change - use zoom or slide
                recommendations.append("zoom")
            else:
                # Default to fade
                recommendations.append("fade")
        
        return recommendations
    
    def apply_continuity_corrections(self, clips: List[str], 
                                    analysis: ContinuityAnalysis) -> List[str]:
        """Apply corrections to improve continuity"""
        corrected_clips = []
        
        for i, clip_path in enumerate(clips):
            try:
                clip = VideoFileClip(clip_path)
                
                # Apply corrections based on analysis
                if i > 0 and i - 1 < len(analysis.continuity_scores):
                    score = analysis.continuity_scores[i - 1]
                    
                    # Color correction
                    if score.color_continuity < 0.5:
                        # Match colors to previous clip
                        target_brightness = analysis.scene_features[i - 1].brightness
                        current_brightness = analysis.scene_features[i].brightness
                        brightness_adjust = target_brightness / current_brightness if current_brightness > 0 else 1
                        
                        # Create proper lambda with captured value
                        def adjust_brightness(gf, t):
                            return gf(t) * brightness_adjust
                        clip = clip.fx(adjust_brightness)
                
                # Save corrected clip
                output_path = clip_path.replace('.mp4', '_corrected.mp4')
                clip.write_videofile(output_path, logger=None)
                clip.close()
                
                corrected_clips.append(output_path)
                
            except Exception as e:
                logger.error(f"❌ Correction failed for {clip_path}: {e}")
                corrected_clips.append(clip_path)
        
        return corrected_clips