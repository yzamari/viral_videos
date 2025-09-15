"""
AI Artifact Detection System for Video Quality Validation
Detects common AI generation artifacts, hallucinations, and quality issues
"""

import os
import cv2
import numpy as np
import json
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import tempfile
import asyncio
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class ArtifactType(Enum):
    """Types of AI artifacts commonly found in generated videos"""
    ANATOMICAL_ERROR = "anatomical_error"  # Extra fingers, distorted faces
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"  # Morphing between frames
    TEXT_GIBBERISH = "text_gibberish"  # Malformed or nonsensical text
    PHYSICS_VIOLATION = "physics_violation"  # Impossible shadows, floating objects
    PATTERN_REPETITION = "pattern_repetition"  # Unnatural repeating patterns
    STYLE_INCONSISTENCY = "style_inconsistency"  # Sudden style changes
    OBJECT_HALLUCINATION = "object_hallucination"  # Objects appearing/disappearing
    LIGHTING_ERROR = "lighting_error"  # Impossible lighting conditions
    PERSPECTIVE_ERROR = "perspective_error"  # Broken perspective/geometry
    TEXTURE_ARTIFACT = "texture_artifact"  # Unnatural textures, smoothness

@dataclass
class ArtifactDetection:
    """Represents a detected artifact in video"""
    artifact_type: ArtifactType
    severity: str  # "low", "medium", "high", "critical"
    confidence: float  # 0-1 confidence in detection
    frame_number: int
    timestamp: float
    description: str
    bounding_box: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h
    suggestion: Optional[str] = None

@dataclass
class VideoQualityReport:
    """Comprehensive video quality assessment"""
    overall_score: float  # 0-1 overall quality
    realism_score: float  # 0-1 how realistic/natural
    consistency_score: float  # 0-1 temporal consistency
    artifact_free_score: float  # 0-1 freedom from artifacts
    artifacts_detected: List[ArtifactDetection]
    frame_analysis: Dict[int, Dict]
    recommendations: List[str]
    should_regenerate: bool
    regeneration_prompts: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class AIArtifactDetector:
    """Advanced AI artifact detection using computer vision and Gemini Vision"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        
        # Initialize Gemini for text analysis
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=gemini_api_key,
            temperature=0.2
        )
        
        # Initialize Gemini Vision for visual analysis
        genai.configure(api_key=gemini_api_key)
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Detection thresholds
        self.quality_threshold = 0.7
        self.artifact_threshold = 0.3  # Lower is better
        self.regeneration_threshold = 0.6
        
        # Frame sampling strategy
        self.sample_rate = 10  # Sample every 10th frame
        self.min_samples = 5
        self.max_samples = 30
        
        logger.info("🔍 AI Artifact Detector initialized")
    
    async def analyze_video(self, video_path: str, script_segment: Optional[str] = None) -> VideoQualityReport:
        """Comprehensive video analysis for AI artifacts and quality issues"""
        logger.info(f"🎬 Analyzing video for AI artifacts: {video_path}")
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return self._create_error_report("Video file not found")
        
        try:
            # Extract frames for analysis
            frames_data = self._extract_frames(video_path)
            
            # Perform multi-level analysis
            cv_analysis = await self._computer_vision_analysis(frames_data)
            gemini_analysis = await self._gemini_vision_analysis(frames_data, script_segment)
            temporal_analysis = self._temporal_consistency_analysis(frames_data)
            
            # Combine all analyses
            report = self._generate_comprehensive_report(
                cv_analysis, gemini_analysis, temporal_analysis, frames_data
            )
            
            # Save report to session directory
            self._save_report(video_path, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return self._create_error_report(str(e))
    
    def _extract_frames(self, video_path: str) -> List[Dict]:
        """Extract frames from video for analysis"""
        frames_data = []
        cap = cv2.VideoCapture(video_path)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Calculate sampling strategy
        sample_interval = max(1, total_frames // self.max_samples)
        samples_to_take = min(self.max_samples, max(self.min_samples, total_frames // sample_interval))
        
        for i in range(samples_to_take):
            frame_num = i * sample_interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                timestamp = frame_num / fps if fps > 0 else 0
                frames_data.append({
                    'frame': frame,
                    'frame_number': frame_num,
                    'timestamp': timestamp,
                    'index': i
                })
        
        cap.release()
        logger.info(f"📊 Extracted {len(frames_data)} frames for analysis")
        return frames_data
    
    async def _computer_vision_analysis(self, frames_data: List[Dict]) -> Dict:
        """Perform computer vision analysis for basic artifacts"""
        logger.info("🖼️ Running computer vision analysis...")
        
        artifacts = []
        quality_scores = []
        
        for frame_data in frames_data:
            frame = frame_data['frame']
            frame_num = frame_data['frame_number']
            
            # 1. Blur/sharpness detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if laplacian_var < 50:
                artifacts.append(ArtifactDetection(
                    artifact_type=ArtifactType.TEXTURE_ARTIFACT,
                    severity="high" if laplacian_var < 20 else "medium",
                    confidence=0.8,
                    frame_number=frame_num,
                    timestamp=frame_data['timestamp'],
                    description="Excessive blur detected, possible AI smoothing artifact"
                ))
            
            # 2. Exposure analysis
            mean_brightness = np.mean(gray)
            if mean_brightness < 30 or mean_brightness > 225:
                artifacts.append(ArtifactDetection(
                    artifact_type=ArtifactType.LIGHTING_ERROR,
                    severity="medium",
                    confidence=0.7,
                    frame_number=frame_num,
                    timestamp=frame_data['timestamp'],
                    description=f"Extreme exposure: {'underexposed' if mean_brightness < 30 else 'overexposed'}"
                ))
            
            # 3. Edge detection for unnatural patterns
            edges = cv2.Canny(frame, 50, 150)
            edge_density = np.count_nonzero(edges) / edges.size
            
            if edge_density > 0.3:  # Too many edges might indicate artifacts
                artifacts.append(ArtifactDetection(
                    artifact_type=ArtifactType.PATTERN_REPETITION,
                    severity="low",
                    confidence=0.6,
                    frame_number=frame_num,
                    timestamp=frame_data['timestamp'],
                    description="Excessive edge patterns detected"
                ))
            
            # 4. Color distribution analysis
            hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            
            # Calculate frame quality
            sharpness_score = min(1.0, laplacian_var / 200)
            exposure_score = 1.0 - abs(mean_brightness - 127) / 127
            color_score = min(1.0, entropy / 5)
            
            frame_quality = (sharpness_score * 0.4 + exposure_score * 0.3 + color_score * 0.3)
            quality_scores.append(frame_quality)
        
        return {
            'artifacts': artifacts,
            'average_quality': np.mean(quality_scores) if quality_scores else 0.5,
            'quality_scores': quality_scores
        }
    
    async def _gemini_vision_analysis(self, frames_data: List[Dict], script_segment: Optional[str]) -> Dict:
        """Use Gemini Vision API for advanced artifact detection"""
        logger.info("🤖 Running Gemini Vision analysis...")
        
        artifacts = []
        realism_scores = []
        
        # Sample fewer frames for Gemini analysis (API cost consideration)
        sample_indices = np.linspace(0, len(frames_data) - 1, min(5, len(frames_data)), dtype=int)
        
        for idx in sample_indices:
            frame_data = frames_data[idx]
            frame = frame_data['frame']
            frame_num = frame_data['frame_number']
            
            # Convert frame to image for Gemini
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()
            
            # Create analysis prompt
            prompt = f"""Analyze this video frame for AI generation artifacts and quality issues.

{f"This frame should represent: {script_segment}" if script_segment else ""}

Please check for:
1. Anatomical errors (extra fingers, distorted faces, impossible body positions)
2. Text readability and coherence (any text should be legible)
3. Physics violations (floating objects, impossible shadows, wrong reflections)
4. Unnatural elements or patterns
5. Overall realism and naturalness

Respond in JSON format:
{{
    "realism_score": 0.0-1.0,
    "artifacts_found": [
        {{
            "type": "anatomical_error|text_gibberish|physics_violation|object_hallucination|other",
            "description": "detailed description",
            "severity": "low|medium|high|critical",
            "location": "general area in frame"
        }}
    ],
    "quality_issues": ["list of quality problems"],
    "looks_ai_generated": true/false,
    "confidence": 0.0-1.0
}}"""
            
            try:
                # Upload image to Gemini
                image = genai.upload_file(path=self._save_temp_image(frame), display_name=f"frame_{frame_num}")
                
                # Generate analysis
                response = self.vision_model.generate_content([prompt, image])
                
                # Parse response
                result = self._parse_gemini_response(response.text)
                
                # Convert to artifacts
                for artifact in result.get('artifacts_found', []):
                    artifact_type_map = {
                        'anatomical_error': ArtifactType.ANATOMICAL_ERROR,
                        'text_gibberish': ArtifactType.TEXT_GIBBERISH,
                        'physics_violation': ArtifactType.PHYSICS_VIOLATION,
                        'object_hallucination': ArtifactType.OBJECT_HALLUCINATION,
                        'other': ArtifactType.TEXTURE_ARTIFACT
                    }
                    
                    artifacts.append(ArtifactDetection(
                        artifact_type=artifact_type_map.get(artifact['type'], ArtifactType.TEXTURE_ARTIFACT),
                        severity=artifact.get('severity', 'medium'),
                        confidence=result.get('confidence', 0.7),
                        frame_number=frame_num,
                        timestamp=frame_data['timestamp'],
                        description=artifact.get('description', 'AI artifact detected'),
                        suggestion=self._generate_fix_suggestion(artifact)
                    ))
                
                realism_scores.append(result.get('realism_score', 0.5))
                
                # Clean up uploaded file
                genai.delete_file(image.name)
                
            except Exception as e:
                logger.warning(f"Gemini Vision analysis failed for frame {frame_num}: {e}")
                continue
        
        return {
            'artifacts': artifacts,
            'average_realism': np.mean(realism_scores) if realism_scores else 0.5,
            'realism_scores': realism_scores
        }
    
    def _temporal_consistency_analysis(self, frames_data: List[Dict]) -> Dict:
        """Analyze temporal consistency between frames"""
        logger.info("⏱️ Running temporal consistency analysis...")
        
        artifacts = []
        consistency_scores = []
        
        for i in range(1, len(frames_data)):
            prev_frame = frames_data[i-1]['frame']
            curr_frame = frames_data[i]['frame']
            
            # Calculate optical flow for motion consistency
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(prev_gray, curr_gray)
            diff_score = np.mean(diff) / 255.0
            
            # Detect sudden changes (potential morphing/warping)
            if diff_score > 0.3:
                artifacts.append(ArtifactDetection(
                    artifact_type=ArtifactType.TEMPORAL_INCONSISTENCY,
                    severity="high" if diff_score > 0.5 else "medium",
                    confidence=0.75,
                    frame_number=frames_data[i]['frame_number'],
                    timestamp=frames_data[i]['timestamp'],
                    description=f"Sudden change detected between frames (score: {diff_score:.2f})",
                    suggestion="Consider adding more intermediate frames or adjusting motion parameters"
                ))
            
            # Calculate histogram correlation for style consistency
            hist_prev = cv2.calcHist([prev_frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist_curr = cv2.calcHist([curr_frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            correlation = cv2.compareHist(hist_prev, hist_curr, cv2.HISTCMP_CORREL)
            consistency_scores.append(correlation)
            
            if correlation < 0.7:
                artifacts.append(ArtifactDetection(
                    artifact_type=ArtifactType.STYLE_INCONSISTENCY,
                    severity="medium",
                    confidence=0.7,
                    frame_number=frames_data[i]['frame_number'],
                    timestamp=frames_data[i]['timestamp'],
                    description="Style inconsistency detected between frames",
                    suggestion="Ensure consistent style parameters across all frames"
                ))
        
        return {
            'artifacts': artifacts,
            'average_consistency': np.mean(consistency_scores) if consistency_scores else 0.8,
            'consistency_scores': consistency_scores
        }
    
    def _generate_comprehensive_report(self, cv_analysis: Dict, gemini_analysis: Dict, 
                                      temporal_analysis: Dict, frames_data: List[Dict]) -> VideoQualityReport:
        """Generate comprehensive quality report combining all analyses"""
        
        # Combine all artifacts
        all_artifacts = (cv_analysis.get('artifacts', []) + 
                        gemini_analysis.get('artifacts', []) + 
                        temporal_analysis.get('artifacts', []))
        
        # Sort by severity and frame number
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_artifacts.sort(key=lambda x: (severity_order.get(x.severity, 4), x.frame_number))
        
        # Calculate overall scores
        overall_quality = cv_analysis.get('average_quality', 0.5)
        realism_score = gemini_analysis.get('average_realism', 0.5)
        consistency_score = temporal_analysis.get('average_consistency', 0.8)
        
        # Calculate artifact-free score (inverse of artifact count/severity)
        artifact_penalty = sum(
            0.3 if a.severity == 'critical' else
            0.2 if a.severity == 'high' else
            0.1 if a.severity == 'medium' else
            0.05
            for a in all_artifacts
        )
        artifact_free_score = max(0, 1.0 - artifact_penalty)
        
        # Calculate final overall score
        overall_score = (
            overall_quality * 0.25 +
            realism_score * 0.35 +
            consistency_score * 0.2 +
            artifact_free_score * 0.2
        )
        
        # Determine if regeneration is needed
        critical_artifacts = [a for a in all_artifacts if a.severity in ['critical', 'high']]
        should_regenerate = (
            overall_score < self.regeneration_threshold or
            len(critical_artifacts) > 2 or
            realism_score < 0.5
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_artifacts, overall_score)
        
        # Generate regeneration prompts if needed
        regeneration_prompts = None
        if should_regenerate:
            regeneration_prompts = self._generate_regeneration_prompts(all_artifacts)
        
        # Create frame analysis summary
        frame_analysis = {}
        for i, frame_data in enumerate(frames_data):
            frame_num = frame_data['frame_number']
            frame_artifacts = [a for a in all_artifacts if a.frame_number == frame_num]
            
            frame_analysis[frame_num] = {
                'timestamp': frame_data['timestamp'],
                'quality_score': cv_analysis['quality_scores'][i] if i < len(cv_analysis['quality_scores']) else 0.5,
                'artifacts': [asdict(a) for a in frame_artifacts],
                'artifact_count': len(frame_artifacts)
            }
        
        return VideoQualityReport(
            overall_score=overall_score,
            realism_score=realism_score,
            consistency_score=consistency_score,
            artifact_free_score=artifact_free_score,
            artifacts_detected=all_artifacts,
            frame_analysis=frame_analysis,
            recommendations=recommendations,
            should_regenerate=should_regenerate,
            regeneration_prompts=regeneration_prompts,
            metadata={
                'total_frames_analyzed': len(frames_data),
                'critical_artifacts': len(critical_artifacts),
                'analysis_timestamp': datetime.now().isoformat(),
                'thresholds': {
                    'quality': self.quality_threshold,
                    'artifact': self.artifact_threshold,
                    'regeneration': self.regeneration_threshold
                }
            }
        )
    
    def _generate_recommendations(self, artifacts: List[ArtifactDetection], overall_score: float) -> List[str]:
        """Generate actionable recommendations based on artifacts found"""
        recommendations = []
        
        # Group artifacts by type
        artifact_types = {}
        for artifact in artifacts:
            if artifact.artifact_type not in artifact_types:
                artifact_types[artifact.artifact_type] = []
            artifact_types[artifact.artifact_type].append(artifact)
        
        # Generate type-specific recommendations
        if ArtifactType.ANATOMICAL_ERROR in artifact_types:
            recommendations.append("Add negative prompts for anatomical accuracy (e.g., 'correct number of fingers', 'proper facial features')")
        
        if ArtifactType.TEMPORAL_INCONSISTENCY in artifact_types:
            recommendations.append("Increase frame interpolation or use consistent seed values for better temporal coherence")
        
        if ArtifactType.TEXT_GIBBERISH in artifact_types:
            recommendations.append("Avoid generating text in visuals or use post-processing to add text overlays")
        
        if ArtifactType.PHYSICS_VIOLATION in artifact_types:
            recommendations.append("Add physics constraints to prompts (e.g., 'realistic shadows', 'proper gravity')")
        
        if ArtifactType.STYLE_INCONSISTENCY in artifact_types:
            recommendations.append("Use style locking or consistent style tokens across all frames")
        
        # Overall score recommendations
        if overall_score < 0.5:
            recommendations.append("Consider regenerating with more specific and constrained prompts")
        elif overall_score < 0.7:
            recommendations.append("Minor adjustments needed - focus on the most severe artifacts")
        
        return recommendations
    
    def _generate_regeneration_prompts(self, artifacts: List[ArtifactDetection]) -> List[str]:
        """Generate improved prompts for regeneration based on artifacts"""
        prompts = []
        
        # Base negative prompts to avoid common artifacts
        negative_base = "distorted, blurry, bad anatomy, extra limbs, poorly drawn, ugly, duplicate"
        
        # Add specific fixes based on artifacts found
        if any(a.artifact_type == ArtifactType.ANATOMICAL_ERROR for a in artifacts):
            prompts.append("Ensure anatomically correct humans with proper proportions, exactly 5 fingers per hand")
        
        if any(a.artifact_type == ArtifactType.TEMPORAL_INCONSISTENCY for a in artifacts):
            prompts.append("Maintain consistent appearance and smooth motion between frames")
        
        if any(a.artifact_type == ArtifactType.TEXT_GIBBERISH for a in artifacts):
            prompts.append("Clear, legible text only or no text in visuals")
        
        prompts.append(f"Negative: {negative_base}")
        
        return prompts
    
    def _generate_fix_suggestion(self, artifact: Dict) -> str:
        """Generate specific fix suggestion for an artifact"""
        suggestions = {
            'anatomical_error': "Use reference images or add 'anatomically correct' to prompt",
            'text_gibberish': "Remove text generation or use post-processing overlays",
            'physics_violation': "Add physics constraints like 'realistic lighting' to prompt",
            'object_hallucination': "Use more specific object descriptions and negative prompts",
            'other': "Review prompt specificity and add negative prompts"
        }
        return suggestions.get(artifact.get('type', 'other'), "Review and adjust generation parameters")
    
    def _save_temp_image(self, frame: np.ndarray) -> str:
        """Save frame as temporary image for Gemini upload"""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"frame_{datetime.now().timestamp()}.jpg")
        cv2.imwrite(temp_path, frame)
        return temp_path
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini response with error handling"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
        except:
            logger.warning("Failed to parse Gemini response")
            return {}
    
    def _save_report(self, video_path: str, report: VideoQualityReport) -> None:
        """Save quality report to session directory"""
        try:
            # Extract session directory from video path
            video_dir = os.path.dirname(video_path)
            report_dir = os.path.join(video_dir, '..', 'quality_reports')
            os.makedirs(report_dir, exist_ok=True)
            
            # Save report as JSON
            report_path = os.path.join(report_dir, f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            # Convert report to dict
            report_dict = {
                'overall_score': report.overall_score,
                'realism_score': report.realism_score,
                'consistency_score': report.consistency_score,
                'artifact_free_score': report.artifact_free_score,
                'should_regenerate': report.should_regenerate,
                'artifacts_count': len(report.artifacts_detected),
                'artifacts': [asdict(a) for a in report.artifacts_detected[:10]],  # Top 10 artifacts
                'recommendations': report.recommendations,
                'regeneration_prompts': report.regeneration_prompts,
                'metadata': report.metadata
            }
            
            with open(report_path, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            logger.info(f"📊 Quality report saved to: {report_path}")
            
            # Log summary
            logger.info(f"📈 Quality Summary:")
            logger.info(f"   Overall Score: {report.overall_score:.2%}")
            logger.info(f"   Realism: {report.realism_score:.2%}")
            logger.info(f"   Consistency: {report.consistency_score:.2%}")
            logger.info(f"   Artifact-Free: {report.artifact_free_score:.2%}")
            logger.info(f"   Regenerate: {'YES' if report.should_regenerate else 'NO'}")
            
        except Exception as e:
            logger.error(f"Failed to save quality report: {e}")
    
    def _create_error_report(self, error_message: str) -> VideoQualityReport:
        """Create an error report when analysis fails"""
        return VideoQualityReport(
            overall_score=0.0,
            realism_score=0.0,
            consistency_score=0.0,
            artifact_free_score=0.0,
            artifacts_detected=[],
            frame_analysis={},
            recommendations=[f"Analysis failed: {error_message}"],
            should_regenerate=True,
            metadata={'error': error_message}
        )


class VideoQualityGatekeeper:
    """Enforces quality standards and manages regeneration"""
    
    def __init__(self, detector: AIArtifactDetector):
        self.detector = detector
        self.max_regeneration_attempts = 3
        self.quality_threshold = 0.7
        
    async def validate_and_regenerate(self, video_path: str, generation_func, 
                                     script: str, attempt: int = 1) -> Tuple[str, VideoQualityReport]:
        """Validate video quality and regenerate if needed"""
        
        logger.info(f"🎬 Validating video quality (attempt {attempt}/{self.max_regeneration_attempts})")
        
        # Analyze video quality
        report = await self.detector.analyze_video(video_path, script)
        
        # Check if quality meets standards
        if report.overall_score >= self.quality_threshold and not report.should_regenerate:
            logger.info(f"✅ Video quality approved: {report.overall_score:.2%}")
            return video_path, report
        
        # Check regeneration attempts
        if attempt >= self.max_regeneration_attempts:
            logger.warning(f"⚠️ Max regeneration attempts reached. Accepting video with score: {report.overall_score:.2%}")
            return video_path, report
        
        # Regenerate with improved prompts
        logger.info(f"🔄 Regenerating video due to quality issues (score: {report.overall_score:.2%})")
        
        # Add regeneration prompts to generation parameters
        improved_params = {
            'negative_prompts': report.regeneration_prompts,
            'quality_boost': True,
            'seed': attempt * 1000  # Different seed for variety
        }
        
        # Generate new video
        new_video_path = await generation_func(**improved_params)
        
        # Recursive validation
        return await self.validate_and_regenerate(
            new_video_path, generation_func, script, attempt + 1
        )