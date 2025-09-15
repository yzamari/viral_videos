"""
LangGraph Video Quality Analyzer with Adaptive Generation
Analyzes video, audio, and script quality in real-time and adjusts future clips
"""

import os
import json
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, TypedDict, Annotated, Sequence, Literal
from dataclasses import dataclass, asdict
from enum import Enum
import operator
from datetime import datetime
import logging

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from ..utils.logging_config import get_logger
# VEO2 client removed - using VEO3 only

logger = get_logger(__name__)

# Quality Analysis State
class QualityState(TypedDict):
    """State for video quality analysis"""
    clip_number: int
    video_path: str
    audio_path: str
    script_segment: str
    quality_scores: Dict[str, float]
    issues_found: List[str]
    recommendations: List[str]
    should_regenerate: bool
    adjusted_prompt: Optional[str]
    analysis_history: Annotated[List[Dict], operator.add]
    
@dataclass
class QualityMetrics:
    """Quality metrics for video analysis"""
    visual_quality: float  # 0-1 score
    audio_quality: float   # 0-1 score
    script_alignment: float  # 0-1 score
    continuity_score: float  # 0-1 score
    engagement_score: float  # 0-1 score
    technical_issues: List[str]
    creative_issues: List[str]
    
class VideoQualityAnalyzer:
    """Analyzes video quality using computer vision and AI"""
    
    def __init__(self, gemini_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=gemini_api_key,
            temperature=0.3
        )
        self.cv_initialized = False
        try:
            import cv2
            self.cv_initialized = True
        except ImportError:
            logger.warning("OpenCV not available for video analysis")
    
    def analyze_visual_quality(self, video_path: str) -> Dict[str, Any]:
        """Analyze visual quality of video using computer vision"""
        if not self.cv_initialized or not os.path.exists(video_path):
            return {"error": "Video analysis not available"}
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Extract key metrics
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Sample frames for quality analysis
            issues = []
            quality_scores = []
            
            for i in range(0, frame_count, max(1, frame_count // 10)):  # Sample 10 frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Check for common issues
                # 1. Blur detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                if laplacian_var < 100:
                    issues.append(f"Blurry frame at position {i}")
                
                # 2. Darkness detection
                mean_brightness = np.mean(gray)
                if mean_brightness < 50:
                    issues.append(f"Dark frame at position {i}")
                elif mean_brightness > 200:
                    issues.append(f"Overexposed frame at position {i}")
                
                # 3. Color distribution
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                entropy = -np.sum(hist * np.log2(hist + 1e-10))
                
                # Calculate frame quality score
                blur_score = min(1.0, laplacian_var / 500)
                brightness_score = 1.0 - abs(mean_brightness - 127) / 127
                color_score = min(1.0, entropy / 5)
                
                frame_quality = (blur_score + brightness_score + color_score) / 3
                quality_scores.append(frame_quality)
            
            cap.release()
            
            avg_quality = np.mean(quality_scores) if quality_scores else 0.5
            
            return {
                "resolution": f"{width}x{height}",
                "fps": fps,
                "frame_count": frame_count,
                "average_quality": float(avg_quality),
                "issues": issues[:5],  # Limit to top 5 issues
                "metrics": {
                    "sharpness": float(np.mean([s for s in quality_scores])),
                    "exposure": 1.0 - len([i for i in issues if "Dark" in i or "Overexposed" in i]) / max(1, len(issues)),
                    "stability": 1.0 - len([i for i in issues if "Blurry" in i]) / max(1, len(issues))
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return {"error": str(e)}
    
    def analyze_script_alignment(self, video_path: str, script_text: str) -> float:
        """Analyze how well the video aligns with the script"""
        prompt = f"""
        Analyze if this video content matches the script intention:
        
        Script: {script_text}
        
        Based on visual analysis, rate from 0-1 how well the video represents the script.
        Consider:
        1. Are the visuals relevant to the script content?
        2. Does the mood match the script tone?
        3. Are key elements from the script visible?
        
        Return only a JSON with:
        {{
            "alignment_score": 0.0-1.0,
            "missing_elements": ["list of script elements not shown"],
            "unexpected_elements": ["list of elements not in script"],
            "recommendation": "brief suggestion for improvement"
        }}
        """
        
        response = self.llm.invoke(prompt)
        try:
            result = json.loads(response.content)
            return result
        except:
            return {"alignment_score": 0.5, "missing_elements": [], "unexpected_elements": [], "recommendation": "Unable to analyze"}

class LangGraphQualityOrchestrator:
    """Orchestrates quality analysis and adaptive generation using LangGraph"""
    
    def __init__(self, gemini_api_key: str, session_id: str):
        self.session_id = session_id
        self.analyzer = VideoQualityAnalyzer(gemini_api_key)
        self.checkpoint = MemorySaver()
        
        # Initialize LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=self.checkpoint)
        
        # Quality thresholds
        self.min_visual_quality = 0.6
        self.min_audio_quality = 0.7
        self.min_script_alignment = 0.7
        self.max_regeneration_attempts = 2
        
        logger.info(f"🎬 LangGraph Quality Orchestrator initialized for {session_id}")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for quality analysis"""
        workflow = StateGraph(QualityState)
        
        # Add nodes
        workflow.add_node("analyze_video", self._analyze_video_node)
        workflow.add_node("analyze_audio", self._analyze_audio_node)
        workflow.add_node("analyze_script", self._analyze_script_node)
        workflow.add_node("evaluate_quality", self._evaluate_quality_node)
        workflow.add_node("generate_recommendations", self._generate_recommendations_node)
        workflow.add_node("adjust_generation", self._adjust_generation_node)
        
        # Add edges
        workflow.add_edge(START, "analyze_video")
        workflow.add_edge("analyze_video", "analyze_audio")
        workflow.add_edge("analyze_audio", "analyze_script")
        workflow.add_edge("analyze_script", "evaluate_quality")
        workflow.add_edge("evaluate_quality", "generate_recommendations")
        
        # Conditional edge based on quality
        workflow.add_conditional_edges(
            "generate_recommendations",
            self._should_adjust_generation,
            {
                "adjust": "adjust_generation",
                "continue": END
            }
        )
        
        workflow.add_edge("adjust_generation", END)
        
        return workflow
    
    def _analyze_video_node(self, state: QualityState) -> Dict:
        """Analyze video quality"""
        logger.info(f"🎥 Analyzing video quality for clip {state['clip_number']}")
        
        visual_analysis = self.analyzer.analyze_visual_quality(state["video_path"])
        
        # Update quality scores
        if "quality_scores" not in state:
            state["quality_scores"] = {}
        
        state["quality_scores"]["visual"] = visual_analysis.get("average_quality", 0.5)
        
        # Add issues if found
        if "issues" in visual_analysis:
            if "issues_found" not in state:
                state["issues_found"] = []
            state["issues_found"].extend(visual_analysis["issues"])
        
        # Add to analysis history
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "visual",
            "clip": state["clip_number"],
            "score": state["quality_scores"]["visual"],
            "details": visual_analysis
        }
        
        return {
            "quality_scores": state["quality_scores"],
            "issues_found": state.get("issues_found", []),
            "analysis_history": [analysis_entry]
        }
    
    def _analyze_audio_node(self, state: QualityState) -> Dict:
        """Analyze audio quality"""
        logger.info(f"🎵 Analyzing audio quality for clip {state['clip_number']}")
        
        # For now, basic audio analysis (can be enhanced with librosa)
        audio_score = 0.8  # Placeholder
        
        if "quality_scores" not in state:
            state["quality_scores"] = {}
        
        state["quality_scores"]["audio"] = audio_score
        
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "audio",
            "clip": state["clip_number"],
            "score": audio_score,
            "details": {"placeholder": "Audio analysis to be implemented"}
        }
        
        return {
            "quality_scores": state["quality_scores"],
            "analysis_history": [analysis_entry]
        }
    
    def _analyze_script_node(self, state: QualityState) -> Dict:
        """Analyze script alignment"""
        logger.info(f"📝 Analyzing script alignment for clip {state['clip_number']}")
        
        alignment_result = self.analyzer.analyze_script_alignment(
            state["video_path"],
            state["script_segment"]
        )
        
        if "quality_scores" not in state:
            state["quality_scores"] = {}
        
        state["quality_scores"]["script_alignment"] = alignment_result.get("alignment_score", 0.5)
        
        # Add issues if elements are missing
        if alignment_result.get("missing_elements"):
            if "issues_found" not in state:
                state["issues_found"] = []
            for element in alignment_result["missing_elements"]:
                state["issues_found"].append(f"Missing from video: {element}")
        
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "script_alignment",
            "clip": state["clip_number"],
            "score": state["quality_scores"]["script_alignment"],
            "details": alignment_result
        }
        
        return {
            "quality_scores": state["quality_scores"],
            "issues_found": state.get("issues_found", []),
            "analysis_history": [analysis_entry]
        }
    
    def _evaluate_quality_node(self, state: QualityState) -> Dict:
        """Evaluate overall quality and determine if regeneration is needed"""
        logger.info(f"⚖️ Evaluating overall quality for clip {state['clip_number']}")
        
        scores = state.get("quality_scores", {})
        
        # Calculate overall score
        overall_score = np.mean([
            scores.get("visual", 0.5),
            scores.get("audio", 0.5),
            scores.get("script_alignment", 0.5)
        ])
        
        scores["overall"] = float(overall_score)
        
        # Determine if regeneration is needed
        should_regenerate = (
            scores.get("visual", 1.0) < self.min_visual_quality or
            scores.get("audio", 1.0) < self.min_audio_quality or
            scores.get("script_alignment", 1.0) < self.min_script_alignment
        )
        
        logger.info(f"📊 Quality scores: {scores}")
        logger.info(f"🔄 Should regenerate: {should_regenerate}")
        
        return {
            "quality_scores": scores,
            "should_regenerate": should_regenerate
        }
    
    def _generate_recommendations_node(self, state: QualityState) -> Dict:
        """Generate recommendations for improvement"""
        logger.info(f"💡 Generating recommendations for clip {state['clip_number']}")
        
        recommendations = []
        scores = state.get("quality_scores", {})
        issues = state.get("issues_found", [])
        
        # Visual recommendations
        if scores.get("visual", 1.0) < self.min_visual_quality:
            recommendations.append("Improve visual quality: enhance lighting, reduce blur, stabilize camera")
        
        # Audio recommendations
        if scores.get("audio", 1.0) < self.min_audio_quality:
            recommendations.append("Improve audio quality: reduce background noise, enhance clarity")
        
        # Script alignment recommendations
        if scores.get("script_alignment", 1.0) < self.min_script_alignment:
            recommendations.append("Better align visuals with script: include mentioned elements, match tone")
        
        # Specific issue recommendations
        if "Blurry" in str(issues):
            recommendations.append("Add 'sharp focus, high definition' to prompt")
        if "Dark" in str(issues):
            recommendations.append("Add 'well-lit, bright' to prompt")
        if "Missing from video" in str(issues):
            missing_items = [i.replace("Missing from video: ", "") for i in issues if "Missing from video" in i]
            recommendations.append(f"Explicitly include: {', '.join(missing_items[:3])}")
        
        logger.info(f"📋 Recommendations: {recommendations}")
        
        return {
            "recommendations": recommendations
        }
    
    def _should_adjust_generation(self, state: QualityState) -> str:
        """Decide whether to adjust generation parameters"""
        if state.get("should_regenerate", False):
            return "adjust"
        return "continue"
    
    def _adjust_generation_node(self, state: QualityState) -> Dict:
        """Adjust generation parameters for next clips"""
        logger.info(f"🔧 Adjusting generation parameters based on quality analysis")
        
        current_issues = state.get("issues_found", [])
        recommendations = state.get("recommendations", [])
        
        # Build adjusted prompt
        prompt_adjustments = []
        
        # Add quality modifiers based on issues
        if any("Blurry" in issue for issue in current_issues):
            prompt_adjustments.append("crystal clear, sharp focus, high definition")
        
        if any("Dark" in issue for issue in current_issues):
            prompt_adjustments.append("bright, well-lit, vibrant colors")
        
        if any("Missing" in issue for issue in current_issues):
            missing_elements = [i.split(": ")[1] for i in current_issues if "Missing from video:" in i]
            if missing_elements:
                prompt_adjustments.append(f"prominently featuring {', '.join(missing_elements[:2])}")
        
        # Add style consistency
        if state.get("quality_scores", {}).get("script_alignment", 1.0) < 0.7:
            prompt_adjustments.append("closely following the script narrative")
        
        adjusted_prompt = ", ".join(prompt_adjustments) if prompt_adjustments else None
        
        logger.info(f"✨ Adjusted prompt additions: {adjusted_prompt}")
        
        return {
            "adjusted_prompt": adjusted_prompt
        }
    
    def analyze_clip(self, 
                    clip_number: int,
                    video_path: str,
                    audio_path: str,
                    script_segment: str) -> Dict[str, Any]:
        """Analyze a single clip and return quality results"""
        
        initial_state = {
            "clip_number": clip_number,
            "video_path": video_path,
            "audio_path": audio_path,
            "script_segment": script_segment,
            "quality_scores": {},
            "issues_found": [],
            "recommendations": [],
            "should_regenerate": False,
            "adjusted_prompt": None,
            "analysis_history": []
        }
        
        # Run the workflow
        config = {"configurable": {"thread_id": f"{self.session_id}_clip_{clip_number}"}}
        
        try:
            result = self.app.invoke(initial_state, config)
            
            # Save analysis results
            self._save_analysis(clip_number, result)
            
            return {
                "clip_number": clip_number,
                "quality_scores": result.get("quality_scores", {}),
                "issues_found": result.get("issues_found", []),
                "recommendations": result.get("recommendations", []),
                "should_regenerate": result.get("should_regenerate", False),
                "adjusted_prompt": result.get("adjusted_prompt"),
                "analysis_history": result.get("analysis_history", [])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing clip {clip_number}: {e}")
            return {
                "clip_number": clip_number,
                "error": str(e),
                "quality_scores": {"overall": 0.5}
            }
    
    def _save_analysis(self, clip_number: int, analysis: Dict):
        """Save analysis results to session directory"""
        session_dir = f"outputs/{self.session_id}/quality_analysis"
        os.makedirs(session_dir, exist_ok=True)
        
        analysis_file = os.path.join(session_dir, f"clip_{clip_number}_analysis.json")
        
        with open(analysis_file, 'w') as f:
            json.dump({
                "clip_number": clip_number,
                "timestamp": datetime.now().isoformat(),
                "quality_scores": analysis.get("quality_scores", {}),
                "issues_found": analysis.get("issues_found", []),
                "recommendations": analysis.get("recommendations", []),
                "should_regenerate": analysis.get("should_regenerate", False),
                "adjusted_prompt": analysis.get("adjusted_prompt")
            }, f, indent=2)
        
        logger.info(f"💾 Analysis saved to {analysis_file}")
    
    def get_adaptive_improvements(self, clip_history: List[Dict]) -> Dict[str, Any]:
        """Get adaptive improvements based on analysis history"""
        
        if not clip_history:
            return {}
        
        # Analyze trends
        quality_trends = {
            "visual": [],
            "audio": [],
            "script_alignment": []
        }
        
        for clip_analysis in clip_history:
            scores = clip_analysis.get("quality_scores", {})
            for key in quality_trends:
                if key in scores:
                    quality_trends[key].append(scores[key])
        
        # Identify persistent issues
        all_issues = []
        for clip_analysis in clip_history:
            all_issues.extend(clip_analysis.get("issues_found", []))
        
        # Count issue frequency
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.split(" ")[0] if issue else "unknown"
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Generate adaptive improvements
        improvements = {
            "persistent_issues": [k for k, v in issue_counts.items() if v > 2],
            "quality_trend": {
                k: "improving" if len(v) > 1 and v[-1] > v[0] else "declining" if len(v) > 1 and v[-1] < v[0] else "stable"
                for k, v in quality_trends.items()
            },
            "recommended_adjustments": []
        }
        
        # Add specific recommendations
        if "Blurry" in improvements["persistent_issues"]:
            improvements["recommended_adjustments"].append({
                "type": "prompt_modifier",
                "add": "ultra high definition, crystal clear, sharp focus",
                "priority": "high"
            })
        
        if improvements["quality_trend"]["script_alignment"] == "declining":
            improvements["recommended_adjustments"].append({
                "type": "script_review",
                "action": "enhance script-to-visual mapping",
                "priority": "high"
            })
        
        return improvements
    
    def generate_quality_report(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive quality report for entire session"""
        
        session_dir = f"outputs/{session_id}/quality_analysis"
        
        if not os.path.exists(session_dir):
            return {"error": "No quality analysis found for session"}
        
        # Load all clip analyses
        clip_analyses = []
        for file in sorted(os.listdir(session_dir)):
            if file.endswith("_analysis.json"):
                with open(os.path.join(session_dir, file), 'r') as f:
                    clip_analyses.append(json.load(f))
        
        if not clip_analyses:
            return {"error": "No clip analyses found"}
        
        # Calculate aggregate metrics
        avg_scores = {
            "visual": np.mean([c.get("quality_scores", {}).get("visual", 0) for c in clip_analyses]),
            "audio": np.mean([c.get("quality_scores", {}).get("audio", 0) for c in clip_analyses]),
            "script_alignment": np.mean([c.get("quality_scores", {}).get("script_alignment", 0) for c in clip_analyses]),
            "overall": np.mean([c.get("quality_scores", {}).get("overall", 0) for c in clip_analyses])
        }
        
        # Identify clips needing regeneration
        clips_to_regenerate = [
            c["clip_number"] for c in clip_analyses 
            if c.get("should_regenerate", False)
        ]
        
        # Compile all issues
        all_issues = []
        for analysis in clip_analyses:
            all_issues.extend(analysis.get("issues_found", []))
        
        # Get adaptive improvements
        improvements = self.get_adaptive_improvements(clip_analyses)
        
        report = {
            "session_id": session_id,
            "total_clips_analyzed": len(clip_analyses),
            "average_quality_scores": avg_scores,
            "clips_needing_regeneration": clips_to_regenerate,
            "total_issues_found": len(all_issues),
            "top_issues": list(set(all_issues))[:10],
            "adaptive_improvements": improvements,
            "quality_grade": self._calculate_grade(avg_scores["overall"]),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report
        report_file = os.path.join(session_dir, "quality_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Quality report generated: {report_file}")
        
        return report
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate quality grade from score"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.85:
            return "A"
        elif score >= 0.8:
            return "B+"
        elif score >= 0.75:
            return "B"
        elif score >= 0.7:
            return "C+"
        elif score >= 0.65:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"


# Integration with main video generation
class AdaptiveVideoGenerator:
    """Enhanced video generator with quality analysis and adaptive generation"""
    
    def __init__(self, gemini_api_key: str, session_id: str):
        self.quality_orchestrator = LangGraphQualityOrchestrator(gemini_api_key, session_id)
        self.session_id = session_id
        self.clip_history = []
        
    def generate_and_analyze_clip(self, 
                                  clip_number: int,
                                  prompt: str,
                                  script_segment: str,
                                  previous_analysis: Optional[Dict] = None) -> Dict:
        """Generate a clip and analyze its quality"""
        
        # Adjust prompt based on previous analysis
        if previous_analysis and previous_analysis.get("adjusted_prompt"):
            enhanced_prompt = f"{prompt}, {previous_analysis['adjusted_prompt']}"
            logger.info(f"🔧 Using enhanced prompt with quality adjustments")
        else:
            enhanced_prompt = prompt
        
        # Generate the clip (placeholder - integrate with actual VEO client)
        video_path = f"outputs/{self.session_id}/video_clips/clip_{clip_number}.mp4"
        audio_path = f"outputs/{self.session_id}/audio/clip_{clip_number}.mp3"
        
        # Analyze the generated clip
        analysis = self.quality_orchestrator.analyze_clip(
            clip_number=clip_number,
            video_path=video_path,
            audio_path=audio_path,
            script_segment=script_segment
        )
        
        # Store in history
        self.clip_history.append(analysis)
        
        # Check if regeneration is needed
        if analysis.get("should_regenerate", False):
            logger.warning(f"⚠️ Clip {clip_number} quality below threshold, recommending regeneration")
            logger.info(f"📋 Issues: {analysis.get('issues_found', [])}")
            logger.info(f"💡 Recommendations: {analysis.get('recommendations', [])}")
        
        return analysis
    
    def get_session_report(self) -> Dict:
        """Get quality report for the entire session"""
        return self.quality_orchestrator.generate_quality_report(self.session_id)


if __name__ == "__main__":
    # Example usage
    import os
    
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("Please set GOOGLE_AI_API_KEY environment variable")
        exit(1)
    
    # Initialize adaptive generator
    generator = AdaptiveVideoGenerator(api_key, "test_session_quality")
    
    # Simulate generating and analyzing clips
    for i in range(3):
        print(f"\n{'='*50}")
        print(f"Generating and analyzing clip {i+1}")
        
        previous = generator.clip_history[-1] if generator.clip_history else None
        
        analysis = generator.generate_and_analyze_clip(
            clip_number=i+1,
            prompt="A festive Rosh Hashana celebration with honey and apples",
            script_segment="celebrating the Jewish New Year with traditional foods",
            previous_analysis=previous
        )
        
        print(f"Quality Scores: {analysis.get('quality_scores', {})}")
        print(f"Issues Found: {len(analysis.get('issues_found', []))}")
        print(f"Should Regenerate: {analysis.get('should_regenerate', False)}")
    
    # Generate final report
    print(f"\n{'='*50}")
    print("Final Quality Report:")
    report = generator.get_session_report()
    print(f"Overall Grade: {report.get('quality_grade')}")
    print(f"Average Scores: {report.get('average_quality_scores')}")
    print(f"Clips needing regeneration: {report.get('clips_needing_regeneration')}")