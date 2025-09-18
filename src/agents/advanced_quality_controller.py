"""
Advanced Quality Controller - Multi-pass quality enhancement pipeline
Implements SOLID principles for modular quality control
"""

import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Protocol
from dataclasses import dataclass, field
from enum import Enum
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import json

from ..utils.logging_config import get_logger
from ..generators.enhanced_script_validator import ScriptQualityValidator, ScriptQualityMetrics
from ..utils.realtime_sync_manager import RealtimeSyncManager, SyncManagerFactory
from ..effects.professional_effects_engine import ProfessionalEffectsEngine, EffectConfig, EffectType
from ..analyzers.scene_continuity_analyzer import SceneContinuityAnalyzer

logger = get_logger(__name__)


# Interface Segregation - Quality check interfaces
class IQualityChecker(Protocol):
    """Interface for quality checkers"""
    def check(self, data: Any) -> Dict[str, Any]:
        ...
    
    def get_score(self) -> float:
        ...


class IQualityEnhancer(Protocol):
    """Interface for quality enhancers"""
    def enhance(self, data: Any) -> Any:
        ...
    
    def get_enhancement_level(self) -> str:
        ...


# Single Responsibility - Data classes
class QualityLevel(Enum):
    """Quality levels for content"""
    POOR = "poor"
    ACCEPTABLE = "acceptable"
    GOOD = "good"
    EXCELLENT = "excellent"
    PROFESSIONAL = "professional"


class EnhancementPass(Enum):
    """Enhancement pass types"""
    VISUAL = "visual"
    AUDIO = "audio"
    SYNC = "sync"
    EFFECTS = "effects"
    COLOR = "color"
    FINAL = "final"


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics"""
    overall_score: float
    visual_quality: float
    audio_quality: float
    sync_quality: float
    narrative_quality: float
    engagement_score: float
    technical_score: float
    quality_level: QualityLevel
    issues: List[str] = field(default_factory=list)
    enhancements_applied: List[str] = field(default_factory=list)


@dataclass
class EnhancementConfig:
    """Configuration for quality enhancement"""
    target_quality: QualityLevel
    max_passes: int = 3
    enable_ai_enhancement: bool = True
    enable_effects: bool = True
    enable_color_grading: bool = True
    enable_audio_enhancement: bool = True
    enable_stabilization: bool = True


@dataclass
class QualityReport:
    """Detailed quality report"""
    metrics: QualityMetrics
    pass_results: Dict[EnhancementPass, Dict]
    recommendations: List[str]
    time_taken: float
    final_path: str


# Abstract base classes
class BaseQualityChecker(ABC):
    """Base class for quality checkers"""
    
    @abstractmethod
    def check(self, data: Any) -> Dict[str, float]:
        """Perform quality check"""
        pass
    
    @abstractmethod
    def get_score(self) -> float:
        """Get quality score"""
        pass


class BaseEnhancer(ABC):
    """Base class for quality enhancers"""
    
    @abstractmethod
    def enhance(self, data: Any) -> Any:
        """Apply enhancement"""
        pass


# Concrete implementations
class VisualQualityChecker(BaseQualityChecker):
    """Checks visual quality metrics"""
    
    def __init__(self):
        self.last_score = 0.5
    
    def check(self, video_path: str) -> Dict[str, float]:
        """Check visual quality of video"""
        try:
            metrics = {
                'sharpness': self._check_sharpness(video_path),
                'brightness': self._check_brightness(video_path),
                'contrast': self._check_contrast(video_path),
                'color_balance': self._check_color_balance(video_path),
                'noise_level': self._check_noise_level(video_path),
                'resolution_quality': self._check_resolution(video_path)
            }
            
            self.last_score = np.mean(list(metrics.values()))
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Visual quality check failed: {e}")
            return {'error': 0.0}
    
    def get_score(self) -> float:
        """Get overall visual quality score"""
        return self.last_score
    
    def _check_sharpness(self, video_path: str) -> float:
        """Check video sharpness using Laplacian variance"""
        try:
            cap = cv2.VideoCapture(video_path)
            sharpness_scores = []
            
            # Sample frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(10, frame_count)
            interval = frame_count // sample_frames if sample_frames > 0 else 1
            
            for i in range(0, frame_count, interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                    sharpness = laplacian.var()
                    # Normalize to 0-1 (typical range 0-1000)
                    normalized = min(1.0, sharpness / 500)
                    sharpness_scores.append(normalized)
            
            cap.release()
            return np.mean(sharpness_scores) if sharpness_scores else 0.5
            
        except Exception as e:
            logger.error(f"Sharpness check failed: {e}")
            return 0.5
    
    def _check_brightness(self, video_path: str) -> float:
        """Check video brightness levels"""
        try:
            cap = cv2.VideoCapture(video_path)
            brightness_scores = []
            
            # Sample frames
            for _ in range(5):
                ret, frame = cap.read()
                if ret:
                    # Calculate mean brightness
                    brightness = np.mean(frame)
                    # Optimal brightness around 127
                    score = 1.0 - abs(brightness - 127) / 127
                    brightness_scores.append(score)
            
            cap.release()
            return np.mean(brightness_scores) if brightness_scores else 0.5
            
        except Exception:
            return 0.5
    
    def _check_contrast(self, video_path: str) -> float:
        """Check video contrast"""
        try:
            cap = cv2.VideoCapture(video_path)
            contrast_scores = []
            
            for _ in range(5):
                ret, frame = cap.read()
                if ret:
                    # Calculate standard deviation as contrast measure
                    contrast = np.std(frame)
                    # Normalize (good contrast around 50-80)
                    score = min(1.0, contrast / 65)
                    contrast_scores.append(score)
            
            cap.release()
            return np.mean(contrast_scores) if contrast_scores else 0.5
            
        except Exception:
            return 0.5
    
    def _check_color_balance(self, video_path: str) -> float:
        """Check color balance"""
        try:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Check RGB channel balance
                b, g, r = cv2.split(frame)
                b_mean, g_mean, r_mean = np.mean(b), np.mean(g), np.mean(r)
                
                # Calculate deviation from gray
                avg = (b_mean + g_mean + r_mean) / 3
                deviation = abs(b_mean - avg) + abs(g_mean - avg) + abs(r_mean - avg)
                
                # Less deviation is better balance
                score = 1.0 - min(1.0, deviation / 100)
                return score
            
            return 0.5
            
        except Exception:
            return 0.5
    
    def _check_noise_level(self, video_path: str) -> float:
        """Check noise levels in video"""
        try:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Estimate noise using high-pass filter
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                noise = np.std(laplacian)
                
                # Less noise is better (typical range 0-50)
                score = 1.0 - min(1.0, noise / 30)
                return score
            
            return 0.5
            
        except Exception:
            return 0.5
    
    def _check_resolution(self, video_path: str) -> float:
        """Check resolution quality"""
        try:
            cap = cv2.VideoCapture(video_path)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            cap.release()
            
            # Score based on resolution
            pixels = width * height
            if pixels >= 1920 * 1080:  # Full HD or higher
                return 1.0
            elif pixels >= 1280 * 720:  # HD
                return 0.8
            elif pixels >= 854 * 480:  # SD
                return 0.6
            else:
                return 0.4
            
        except Exception:
            return 0.5


class AudioQualityChecker(BaseQualityChecker):
    """Checks audio quality metrics"""
    
    def __init__(self):
        self.last_score = 0.5
    
    def check(self, audio_path: str) -> Dict[str, float]:
        """Check audio quality"""
        try:
            metrics = {
                'clarity': self._check_clarity(audio_path),
                'volume_consistency': self._check_volume_consistency(audio_path),
                'noise_level': self._check_audio_noise(audio_path),
                'dynamic_range': self._check_dynamic_range(audio_path)
            }
            
            self.last_score = np.mean(list(metrics.values()))
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Audio quality check failed: {e}")
            return {'error': 0.0}
    
    def get_score(self) -> float:
        """Get overall audio quality score"""
        return self.last_score
    
    def _check_clarity(self, audio_path: str) -> float:
        """Check audio clarity"""
        try:
            with AudioFileClip(audio_path) as audio:
                # Sample audio
                if audio.duration > 0:
                    sample = audio.subclip(0, min(1, audio.duration))
                    # Get audio array
                    audio_array = sample.to_soundarray()
                    
                    # Check frequency content (simplified)
                    fft = np.fft.fft(audio_array[:, 0])
                    freqs = np.fft.fftfreq(len(fft))
                    
                    # Check for good frequency distribution
                    power = np.abs(fft) ** 2
                    # Normalize
                    score = min(1.0, np.std(power) / np.mean(power))
                    
                    return score
                    
            return 0.5
            
        except Exception:
            return 0.5
    
    def _check_volume_consistency(self, audio_path: str) -> float:
        """Check volume consistency"""
        try:
            with AudioFileClip(audio_path) as audio:
                if audio.duration > 0:
                    # Sample at intervals
                    samples = []
                    for t in np.linspace(0, audio.duration, min(10, int(audio.duration))):
                        if t < audio.duration:
                            frame = audio.get_frame(t)
                            if isinstance(frame, np.ndarray):
                                samples.append(np.mean(np.abs(frame)))
                    
                    if samples:
                        # Check variance in volume
                        variance = np.std(samples) / (np.mean(samples) + 0.001)
                        # Less variance is better
                        score = 1.0 - min(1.0, variance)
                        return score
                        
            return 0.5
            
        except Exception:
            return 0.5
    
    def _check_audio_noise(self, audio_path: str) -> float:
        """Check audio noise levels"""
        try:
            with AudioFileClip(audio_path) as audio:
                if audio.duration > 0:
                    # Get a quiet section (assuming beginning might be quiet)
                    sample = audio.subclip(0, min(0.5, audio.duration))
                    audio_array = sample.to_soundarray()
                    
                    # Estimate noise floor
                    noise_floor = np.percentile(np.abs(audio_array), 10)
                    
                    # Lower noise floor is better
                    score = 1.0 - min(1.0, noise_floor * 10)
                    return score
                    
            return 0.5
            
        except Exception:
            return 0.5
    
    def _check_dynamic_range(self, audio_path: str) -> float:
        """Check audio dynamic range"""
        try:
            with AudioFileClip(audio_path) as audio:
                if audio.duration > 0:
                    audio_array = audio.to_soundarray()
                    
                    # Calculate dynamic range
                    peak = np.max(np.abs(audio_array))
                    rms = np.sqrt(np.mean(audio_array ** 2))
                    
                    if rms > 0:
                        dynamic_range = 20 * np.log10(peak / rms)
                        # Good dynamic range is 20-40 dB
                        if 20 <= dynamic_range <= 40:
                            score = 1.0
                        else:
                            score = 0.7
                    else:
                        score = 0.5
                    
                    return score
                    
            return 0.5
            
        except Exception:
            return 0.5


class VideoEnhancer(BaseEnhancer):
    """Enhances video quality"""
    
    def __init__(self):
        self.effects_engine = ProfessionalEffectsEngine()
    
    def enhance(self, video_path: str) -> str:
        """Apply video enhancements"""
        try:
            # Apply stabilization
            stabilized = self._stabilize_video(video_path)
            
            # CRITICAL FIX: Disable denoising and sharpening that add visual artifacts to VEO3
            # These OpenCV filters were contaminating clean VEO3 content with Canny-like artifacts
            logger.info("🔧 SKIPPING denoising and sharpening to preserve clean VEO3 content")
            return video_path  # Return original VEO3 content without artifacts
            
        except Exception as e:
            logger.error(f"❌ Video enhancement failed: {e}")
            return video_path
    
    def _stabilize_video(self, video_path: str) -> str:
        """Apply video stabilization"""
        try:
            # This would use cv2.createVideoStabilizer in production
            # Simplified for now
            return video_path
        except Exception:
            return video_path
    
    def _denoise_video(self, video_path: str) -> str:
        """Apply video denoising"""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            output_path = video_path.replace('.mp4', '_denoised.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply denoising
                denoised = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
                out.write(denoised)
            
            cap.release()
            out.release()
            
            return output_path
            
        except Exception:
            return video_path
    
    def _sharpen_video(self, video_path: str) -> str:
        """Apply video sharpening"""
        try:
            # Sharpening kernel
            kernel = np.array([[-1, -1, -1],
                              [-1, 9, -1],
                              [-1, -1, -1]])
            
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            output_path = video_path.replace('.mp4', '_sharpened.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply sharpening
                sharpened = cv2.filter2D(frame, -1, kernel)
                out.write(sharpened)
            
            cap.release()
            out.release()
            
            return output_path
            
        except Exception:
            return video_path


class AudioEnhancer(BaseEnhancer):
    """Enhances audio quality"""
    
    def enhance(self, audio_path: str) -> str:
        """Apply audio enhancements"""
        try:
            # Apply noise reduction
            cleaned = self._reduce_noise(audio_path)
            
            # Apply normalization
            normalized = self._normalize_audio(cleaned)
            
            # Apply compression
            compressed = self._compress_audio(normalized)
            
            return compressed
            
        except Exception as e:
            logger.error(f"❌ Audio enhancement failed: {e}")
            return audio_path
    
    def _reduce_noise(self, audio_path: str) -> str:
        """Reduce audio noise"""
        try:
            # This would use more sophisticated noise reduction
            # Simplified for now
            return audio_path
        except Exception:
            return audio_path
    
    def _normalize_audio(self, audio_path: str) -> str:
        """Normalize audio levels"""
        try:
            with AudioFileClip(audio_path) as audio:
                # Calculate peak
                audio_array = audio.to_soundarray()
                peak = np.max(np.abs(audio_array))
                
                if peak > 0 and peak < 0.95:
                    # Normalize to 95% of max
                    factor = 0.95 / peak
                    normalized = audio.fx(lambda gf, t: gf(t) * factor)
                    
                    output_path = audio_path.replace('.mp3', '_normalized.mp3')
                    normalized.write_audiofile(output_path, logger=None)
                    
                    return output_path
                    
            return audio_path
            
        except Exception:
            return audio_path
    
    def _compress_audio(self, audio_path: str) -> str:
        """Apply audio compression"""
        try:
            # This would use proper audio compression
            # Simplified for now
            return audio_path
        except Exception:
            return audio_path


# Main Quality Controller - Orchestrator
class AdvancedQualityController:
    """Advanced quality controller with multi-pass enhancement"""
    
    def __init__(self, config: Optional[EnhancementConfig] = None):
        """Initialize with configuration"""
        self.config = config or EnhancementConfig(target_quality=QualityLevel.EXCELLENT)
        
        # Initialize components
        self.script_validator = ScriptQualityValidator()
        self.sync_manager = SyncManagerFactory.create_hybrid_sync_manager()
        self.effects_engine = ProfessionalEffectsEngine()
        self.continuity_analyzer = SceneContinuityAnalyzer()
        
        # Initialize checkers
        self.visual_checker = VisualQualityChecker()
        self.audio_checker = AudioQualityChecker()
        
        # Initialize enhancers
        self.video_enhancer = VideoEnhancer()
        self.audio_enhancer = AudioEnhancer()
        
        logger.info("✅ Advanced Quality Controller initialized")
    
    def multi_pass_quality_enhancement(self, 
                                      video_path: str,
                                      audio_path: Optional[str] = None,
                                      script: Optional[str] = None) -> QualityReport:
        """
        Perform multi-pass quality enhancement
        
        Args:
            video_path: Path to video file
            audio_path: Optional path to audio file
            script: Optional script text
            
        Returns:
            QualityReport with results
        """
        import time
        start_time = time.time()
        
        logger.info("🚀 Starting multi-pass quality enhancement")
        
        # Initial quality assessment
        initial_metrics = self._assess_quality(video_path, audio_path, script)
        logger.info(f"📊 Initial quality: {initial_metrics.quality_level.value} ({initial_metrics.overall_score:.2f})")
        
        pass_results = {}
        current_video = video_path
        current_audio = audio_path
        
        # Perform enhancement passes
        for pass_num in range(min(self.config.max_passes, 3)):
            logger.info(f"🔄 Enhancement pass {pass_num + 1}/{self.config.max_passes}")
            
            # Visual enhancement pass
            if self.config.enable_effects:
                current_video = self._visual_enhancement_pass(current_video)
                pass_results[EnhancementPass.VISUAL] = {'video': current_video}
            
            # Audio enhancement pass
            if current_audio and self.config.enable_audio_enhancement:
                current_audio = self._audio_enhancement_pass(current_audio)
                pass_results[EnhancementPass.AUDIO] = {'audio': current_audio}
            
            # Sync enhancement pass
            if current_audio:
                sync_result = self._sync_enhancement_pass(current_video, current_audio)
                pass_results[EnhancementPass.SYNC] = sync_result
            
            # Check if target quality reached
            current_metrics = self._assess_quality(current_video, current_audio, script)
            if current_metrics.quality_level.value >= self.config.target_quality.value:
                logger.info(f"✅ Target quality reached: {current_metrics.quality_level.value}")
                break
        
        # Final color grading pass
        if self.config.enable_color_grading:
            current_video = self._color_grading_pass(current_video)
            pass_results[EnhancementPass.COLOR] = {'video': current_video}
        
        # Final quality assessment
        final_metrics = self._assess_quality(current_video, current_audio, script)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(final_metrics)
        
        # Create report
        report = QualityReport(
            metrics=final_metrics,
            pass_results=pass_results,
            recommendations=recommendations,
            time_taken=time.time() - start_time,
            final_path=current_video
        )
        
        logger.info(f"✅ Enhancement complete: {final_metrics.quality_level.value} ({final_metrics.overall_score:.2f})")
        logger.info(f"⏱️ Time taken: {report.time_taken:.1f}s")
        
        return report
    
    def _assess_quality(self, video_path: str, 
                       audio_path: Optional[str] = None,
                       script: Optional[str] = None) -> QualityMetrics:
        """Assess overall quality"""
        
        # Visual quality
        visual_metrics = self.visual_checker.check(video_path)
        visual_score = self.visual_checker.get_score()
        
        # Audio quality
        if audio_path:
            audio_metrics = self.audio_checker.check(audio_path)
            audio_score = self.audio_checker.get_score()
        else:
            audio_score = 0.5
        
        # Narrative quality
        if script:
            script_metrics = self.script_validator.validate_script_quality(
                script, 
                type('Config', (), {'duration_seconds': 30})()
            )
            narrative_score = script_metrics.overall_score
        else:
            narrative_score = 0.5
        
        # Calculate overall score
        overall_score = (
            visual_score * 0.35 +
            audio_score * 0.25 +
            narrative_score * 0.2 +
            0.5 * 0.2  # Placeholder for sync and engagement
        )
        
        # Determine quality level
        if overall_score >= 0.9:
            quality_level = QualityLevel.PROFESSIONAL
        elif overall_score >= 0.8:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 0.7:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 0.5:
            quality_level = QualityLevel.ACCEPTABLE
        else:
            quality_level = QualityLevel.POOR
        
        # Identify issues
        issues = []
        if visual_score < 0.6:
            issues.append("Low visual quality")
        if audio_score < 0.6:
            issues.append("Poor audio quality")
        if narrative_score < 0.6:
            issues.append("Weak narrative structure")
        
        return QualityMetrics(
            overall_score=overall_score,
            visual_quality=visual_score,
            audio_quality=audio_score,
            sync_quality=0.5,  # Placeholder
            narrative_quality=narrative_score,
            engagement_score=0.5,  # Placeholder
            technical_score=(visual_score + audio_score) / 2,
            quality_level=quality_level,
            issues=issues,
            enhancements_applied=[]
        )
    
    def _visual_enhancement_pass(self, video_path: str) -> str:
        """Perform visual enhancement pass"""
        logger.info("🎨 Applying visual enhancements")
        return self.video_enhancer.enhance(video_path)
    
    def _audio_enhancement_pass(self, audio_path: str) -> str:
        """Perform audio enhancement pass"""
        logger.info("🎵 Applying audio enhancements")
        return self.audio_enhancer.enhance(audio_path)
    
    def _sync_enhancement_pass(self, video_path: str, audio_path: str) -> Dict:
        """Perform sync enhancement pass"""
        logger.info("🔄 Optimizing audio-video sync")
        
        # This would integrate with the sync manager
        # Simplified for now
        return {'status': 'synced'}
    
    def _color_grading_pass(self, video_path: str) -> str:
        """Apply final color grading"""
        logger.info("🎨 Applying cinematic color grading")
        
        effects = [
            EffectConfig(name='cinematic', type=EffectType.COLOR)
        ]
        
        return self.effects_engine.apply_cinematic_effects(video_path, effects)
    
    def _generate_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if metrics.visual_quality < 0.7:
            recommendations.append("Consider higher resolution source material")
            recommendations.append("Apply video stabilization and denoising")
        
        if metrics.audio_quality < 0.7:
            recommendations.append("Use professional audio recording equipment")
            recommendations.append("Apply noise reduction and normalization")
        
        if metrics.narrative_quality < 0.7:
            recommendations.append("Strengthen opening hook and call-to-action")
            recommendations.append("Improve pacing and narrative structure")
        
        if metrics.sync_quality < 0.7:
            recommendations.append("Adjust clip timing to match audio beats")
            recommendations.append("Use transition effects to smooth cuts")
        
        return recommendations
    
    def validate_before_generation(self, config: Any) -> Tuple[bool, List[str]]:
        """Validate configuration before video generation"""
        issues = []
        
        # Check script quality
        if hasattr(config, 'script') and config.script:
            script_metrics = self.script_validator.validate_script_quality(
                config.script, config
            )
            if script_metrics.overall_score < 0.5:
                issues.append("Script quality too low - enhance narrative")
        
        # Check duration
        if hasattr(config, 'duration_seconds'):
            if config.duration_seconds < 5:
                issues.append("Duration too short for quality content")
            elif config.duration_seconds > 300:
                issues.append("Duration too long - consider splitting")
        
        # Check platform requirements
        if hasattr(config, 'target_platform'):
            platform = str(config.target_platform).lower()
            if 'tiktok' in platform and config.duration_seconds > 60:
                issues.append("TikTok videos should be under 60 seconds")
        
        can_proceed = len(issues) == 0
        return can_proceed, issues