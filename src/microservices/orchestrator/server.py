"""
Orchestrator Microservice
Runs as independent HTTP server on port 8005
Coordinates all other microservices for end-to-end video generation
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
import asyncio
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Workflow stages for video generation"""
    INITIALIZED = "initialized"
    SCRIPT_GENERATION = "script_generation"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowRequest:
    """End-to-end generation request"""
    mission: str
    duration: int
    platform: str = "youtube"
    style: str = "cinematic"
    optimize_prompts: bool = True
    parallel_generation: bool = True
    max_retries: int = 3


@dataclass
class WorkflowStatus:
    """Workflow execution status"""
    workflow_id: str
    stage: WorkflowStage
    progress: float
    started_at: str
    updated_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    results: Dict[str, Any] = None


class OrchestratorService:
    """Orchestrates all microservices for video generation"""
    
    def __init__(self):
        # Service endpoints
        self.services = {
            "prompt_optimizer": "http://localhost:8001",
            "video_generator": "http://localhost:8002",
            "monitoring": "http://localhost:8003",
            "script_generator": "http://localhost:8004",
            "audio_generator": "http://localhost:8006"
        }
        
        # Workflow storage
        self.workflows = {}
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Statistics
        self.stats = {
            "total_workflows": 0,
            "successful": 0,
            "failed": 0,
            "in_progress": 0
        }
        
        logger.info("✅ Orchestrator Service initialized")
    
    def execute_workflow(self, request: WorkflowRequest) -> str:
        """
        Execute complete video generation workflow
        
        Args:
            request: Workflow request
            
        Returns:
            Workflow ID for tracking
        """
        workflow_id = str(uuid.uuid4())
        
        # Initialize workflow status
        status = WorkflowStatus(
            workflow_id=workflow_id,
            stage=WorkflowStage.INITIALIZED,
            progress=0.0,
            started_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.workflows[workflow_id] = status
        self.stats["total_workflows"] += 1
        self.stats["in_progress"] += 1
        
        # Start workflow in background
        self.executor.submit(self._run_workflow, workflow_id, request)
        
        return workflow_id
    
    def _run_workflow(self, workflow_id: str, request: WorkflowRequest):
        """Run the complete workflow"""
        try:
            # Stage 1: Generate script
            self._update_status(workflow_id, WorkflowStage.SCRIPT_GENERATION, 0.1)
            script = self._generate_script(request)
            
            # Stage 2: Optimize prompts
            self._update_status(workflow_id, WorkflowStage.PROMPT_OPTIMIZATION, 0.3)
            optimized_prompts = self._optimize_prompts(script, request)
            
            # Stage 3: Generate audio (parallel with video if enabled)
            self._update_status(workflow_id, WorkflowStage.AUDIO_GENERATION, 0.4)
            
            if request.parallel_generation:
                # Parallel execution
                futures = []
                
                # Audio generation
                audio_future = self.executor.submit(
                    self._generate_audio, script, request
                )
                futures.append(("audio", audio_future))
                
                # Video generation for each clip
                self._update_status(workflow_id, WorkflowStage.VIDEO_GENERATION, 0.5)
                for i, prompt in enumerate(optimized_prompts):
                    video_future = self.executor.submit(
                        self._generate_video, prompt, f"clip_{i}", request
                    )
                    futures.append((f"video_{i}", video_future))
                
                # Collect results
                results = {}
                for name, future in futures:
                    try:
                        results[name] = future.result(timeout=60)
                    except Exception as e:
                        logger.error(f"Parallel task {name} failed: {e}")
                        results[name] = {"error": str(e)}
            else:
                # Sequential execution
                audio_results = self._generate_audio(script, request)
                
                self._update_status(workflow_id, WorkflowStage.VIDEO_GENERATION, 0.6)
                video_results = []
                for i, prompt in enumerate(optimized_prompts):
                    video_result = self._generate_video(prompt, f"clip_{i}", request)
                    video_results.append(video_result)
                
                results = {
                    "audio": audio_results,
                    "videos": video_results
                }
            
            # Stage 4: Post-processing
            self._update_status(workflow_id, WorkflowStage.POST_PROCESSING, 0.8)
            final_output = self._post_process(results, request)
            
            # Complete workflow
            self._complete_workflow(workflow_id, final_output)
            
        except Exception as e:
            self._fail_workflow(workflow_id, str(e))
    
    def _generate_script(self, request: WorkflowRequest) -> Dict[str, Any]:
        """Generate script via script service"""
        try:
            # For now, create a simple script
            # In production, call the script generator service
            script = {
                "segments": [
                    {"text": "Introduction to the topic", "duration": request.duration / 3},
                    {"text": "Main content and details", "duration": request.duration / 3},
                    {"text": "Conclusion and call to action", "duration": request.duration / 3}
                ],
                "total_duration": request.duration,
                "mission": request.mission
            }
            
            self._send_metric("script.generated", 1)
            return script
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise
    
    def _optimize_prompts(self, script: Dict[str, Any], request: WorkflowRequest) -> List[str]:
        """Optimize prompts for each video segment"""
        optimized = []
        
        if not request.optimize_prompts:
            # Return raw prompts
            for segment in script["segments"]:
                optimized.append(f"{request.mission}: {segment['text']}")
            return optimized
        
        try:
            # Call prompt optimizer service
            for segment in script["segments"]:
                prompt = f"{request.mission}: {segment['text']} in {request.style} style"
                
                response = requests.post(
                    f"{self.services['prompt_optimizer']}/optimize",
                    json={
                        "prompt": prompt,
                        "level": "moderate"
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    optimized.append(result["optimized_prompt"])
                else:
                    optimized.append(prompt)  # Use original if optimization fails
            
            self._send_metric("prompts.optimized", len(optimized))
            return optimized
            
        except Exception as e:
            logger.warning(f"Prompt optimization failed: {e}")
            # Return unoptimized prompts
            return [f"{request.mission}: {s['text']}" for s in script["segments"]]
    
    def _generate_audio(self, script: Dict[str, Any], request: WorkflowRequest) -> Dict[str, Any]:
        """Generate audio for script"""
        try:
            # Simulate audio generation
            # In production, call audio generator service
            audio_files = []
            for i, segment in enumerate(script["segments"]):
                audio_files.append(f"audio_segment_{i}.mp3")
            
            self._send_metric("audio.generated", len(audio_files))
            
            return {
                "audio_files": audio_files,
                "total_duration": request.duration
            }
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_video(self, prompt: str, clip_id: str, request: WorkflowRequest) -> Dict[str, Any]:
        """Generate video clip"""
        try:
            response = requests.post(
                f"{self.services['video_generator']}/generate",
                json={
                    "prompt": prompt,
                    "clip_id": clip_id,
                    "duration": request.duration / 3,  # Divide by number of segments
                    "platform": request.platform,
                    "style": request.style,
                    "optimize_prompt": False  # Already optimized
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self._send_metric("video.generated", 1)
                return result
            else:
                raise Exception(f"Video generation failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Video generation for {clip_id} failed: {e}")
            return {"error": str(e), "clip_id": clip_id}
    
    def _post_process(self, results: Dict[str, Any], request: WorkflowRequest) -> Dict[str, Any]:
        """Post-process and combine results"""
        try:
            # Combine videos and audio
            final_output = {
                "workflow_complete": True,
                "total_duration": request.duration,
                "components": results,
                "final_video": "final_output.mp4"  # In production, actually combine files
            }
            
            self._send_metric("workflow.completed", 1)
            return final_output
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            raise
    
    def _update_status(self, workflow_id: str, stage: WorkflowStage, progress: float):
        """Update workflow status"""
        if workflow_id in self.workflows:
            status = self.workflows[workflow_id]
            status.stage = stage
            status.progress = progress
            status.updated_at = datetime.now().isoformat()
            
            # Send event to monitoring
            self._send_event("workflow.stage_changed", {
                "workflow_id": workflow_id,
                "stage": stage.value,
                "progress": progress
            })
    
    def _complete_workflow(self, workflow_id: str, results: Dict[str, Any]):
        """Mark workflow as completed"""
        if workflow_id in self.workflows:
            status = self.workflows[workflow_id]
            status.stage = WorkflowStage.COMPLETED
            status.progress = 1.0
            status.completed_at = datetime.now().isoformat()
            status.results = results
            
            self.stats["successful"] += 1
            self.stats["in_progress"] -= 1
            
            self._send_event("workflow.completed", {
                "workflow_id": workflow_id,
                "duration": (datetime.fromisoformat(status.completed_at) - 
                           datetime.fromisoformat(status.started_at)).total_seconds()
            })
    
    def _fail_workflow(self, workflow_id: str, error: str):
        """Mark workflow as failed"""
        if workflow_id in self.workflows:
            status = self.workflows[workflow_id]
            status.stage = WorkflowStage.FAILED
            status.error = error
            status.completed_at = datetime.now().isoformat()
            
            self.stats["failed"] += 1
            self.stats["in_progress"] -= 1
            
            self._send_event("workflow.failed", {
                "workflow_id": workflow_id,
                "error": error
            })
    
    def _send_metric(self, name: str, value: Any):
        """Send metric to monitoring service"""
        try:
            requests.post(
                f"{self.services['monitoring']}/metrics",
                json={
                    "service": "orchestrator",
                    "name": name,
                    "value": value
                },
                timeout=1
            )
        except:
            pass  # Don't fail if monitoring is down
    
    def _send_event(self, event_type: str, data: Dict[str, Any]):
        """Send event to monitoring service"""
        try:
            requests.post(
                f"{self.services['monitoring']}/events",
                json={
                    "service": "orchestrator",
                    "type": event_type,
                    "data": data
                },
                timeout=1
            )
        except:
            pass
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """Get workflow status"""
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows"""
        return [asdict(w) for w in self.workflows.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            **self.stats,
            "active_workflows": [
                wid for wid, w in self.workflows.items() 
                if w.stage not in [WorkflowStage.COMPLETED, WorkflowStage.FAILED]
            ]
        }


# Initialize service
orchestrator = OrchestratorService()


# ============= HTTP API Endpoints =============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "orchestrator",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/workflow', methods=['POST'])
def create_workflow():
    """Create new workflow"""
    try:
        data = request.json
        
        # Create workflow request
        workflow_request = WorkflowRequest(
            mission=data.get('mission'),
            duration=data.get('duration', 30),
            platform=data.get('platform', 'youtube'),
            style=data.get('style', 'cinematic'),
            optimize_prompts=data.get('optimize_prompts', True),
            parallel_generation=data.get('parallel', True),
            max_retries=data.get('max_retries', 3)
        )
        
        # Execute workflow
        workflow_id = orchestrator.execute_workflow(workflow_request)
        
        return jsonify({
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Workflow execution started"
        })
        
    except Exception as e:
        logger.error(f"Workflow creation failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/workflow/<workflow_id>', methods=['GET'])
def get_workflow_status(workflow_id):
    """Get workflow status"""
    status = orchestrator.get_workflow_status(workflow_id)
    
    if not status:
        return jsonify({"error": "Workflow not found"}), 404
    
    return jsonify(asdict(status))


@app.route('/workflows', methods=['GET'])
def list_workflows():
    """List all workflows"""
    return jsonify(orchestrator.get_all_workflows())


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get orchestrator statistics"""
    return jsonify(orchestrator.get_stats())


@app.route('/services/status', methods=['GET'])
def check_services():
    """Check status of all dependent services"""
    service_status = {}
    
    for service_name, service_url in orchestrator.services.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            service_status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
        except:
            service_status[service_name] = {"status": "down"}
    
    return jsonify(service_status)


if __name__ == '__main__':
    logger.info("🎭 Starting Orchestrator Service on port 8005")
    app.run(host='0.0.0.0', port=8005, debug=False)