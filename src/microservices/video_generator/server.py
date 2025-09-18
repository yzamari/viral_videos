"""
Video Generator Microservice
Runs as independent HTTP server on port 8002
Handles VEO3 video generation with retry logic
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import time
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import requests
import redis
import logging
from queue import Queue
import threading

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis for job queue (optional)
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
    REDIS_ENABLED = True
    logger.info("✅ Redis connected for job queue")
except:
    REDIS_ENABLED = False
    logger.warning("⚠️ Redis not available, using in-memory queue")

# Job queue for async processing
job_queue = Queue()
jobs_status = {}


class VideoGenerationService:
    """Core video generation logic with retry"""
    
    def __init__(self):
        self.generation_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.retry_config = {
            "max_attempts": 3,
            "initial_delay": 2.0,
            "max_delay": 30.0,
            "exponential_base": 2.0
        }
        
        # Connection to prompt optimizer service
        self.prompt_optimizer_url = os.getenv("PROMPT_OPTIMIZER_URL", "http://localhost:8001")
        
        # Output directory
        self.output_dir = "/tmp/video_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_video(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video with retry logic"""
        job_id = str(uuid.uuid4())
        start_time = datetime.now()
        self.generation_count += 1
        
        # Update job status
        jobs_status[job_id] = {
            "status": "processing",
            "started_at": start_time.isoformat(),
            "request": request
        }
        
        try:
            # Step 1: Optimize prompt if needed
            optimized_prompt = self._optimize_prompt_if_needed(request)
            
            # Step 2: Try generation with retry
            result = self._generate_with_retry(optimized_prompt, request)
            
            if result["success"]:
                self.success_count += 1
                jobs_status[job_id] = {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                }
            else:
                self.failure_count += 1
                jobs_status[job_id] = {
                    "status": "failed",
                    "error": result.get("error"),
                    "completed_at": datetime.now().isoformat()
                }
            
            return {
                "job_id": job_id,
                **result
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            self.failure_count += 1
            jobs_status[job_id] = {
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
            return {
                "job_id": job_id,
                "success": False,
                "error": str(e)
            }
    
    def _optimize_prompt_if_needed(self, request: Dict[str, Any]) -> str:
        """Optimize prompt using prompt optimizer service"""
        prompt = request.get("prompt")
        optimize = request.get("optimize_prompt", True)
        
        if not optimize:
            return prompt
        
        try:
            # Call prompt optimizer service
            response = requests.post(
                f"{self.prompt_optimizer_url}/optimize",
                json={
                    "prompt": prompt,
                    "level": request.get("optimization_level", "moderate")
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Prompt optimized: {result['original_length']} -> {result['optimized_length']}")
                return result["optimized_prompt"]
            else:
                logger.warning("Prompt optimization failed, using original")
                return prompt
                
        except Exception as e:
            logger.warning(f"Could not reach prompt optimizer: {e}")
            return prompt
    
    def _generate_with_retry(self, prompt: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video with retry logic"""
        attempts = 0
        last_error = None
        
        while attempts < self.retry_config["max_attempts"]:
            attempts += 1
            logger.info(f"Generation attempt {attempts}/{self.retry_config['max_attempts']}")
            
            try:
                # Simulate VEO3 generation (in production, call actual VEO3 API)
                video_path = self._simulate_veo3_generation(
                    prompt,
                    request.get("duration", 8),
                    request.get("clip_id", f"clip_{attempts}")
                )
                
                if video_path:
                    return {
                        "success": True,
                        "video_path": video_path,
                        "attempts": attempts,
                        "prompt_used": prompt
                    }
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempts} failed: {e}")
                
                # Calculate backoff delay
                if attempts < self.retry_config["max_attempts"]:
                    delay = min(
                        self.retry_config["initial_delay"] * (self.retry_config["exponential_base"] ** (attempts - 1)),
                        self.retry_config["max_delay"]
                    )
                    logger.info(f"Waiting {delay}s before retry...")
                    time.sleep(delay)
                    
                    # Simplify prompt for next attempt
                    if attempts == 2:
                        prompt = self._simplify_prompt_further(prompt)
        
        return {
            "success": False,
            "error": last_error or "Generation failed after all attempts",
            "attempts": attempts
        }
    
    def _simulate_veo3_generation(self, prompt: str, duration: float, clip_id: str) -> str:
        """Simulate VEO3 generation (replace with actual API call)"""
        # Simulate processing time
        time.sleep(2)
        
        # Simulate occasional failures
        import random
        if random.random() < 0.3:  # 30% failure rate for testing
            if "war" in prompt.lower() or "soldier" in prompt.lower():
                raise Exception("Safety block: prompt contains sensitive content")
            else:
                raise Exception("VEO3 API timeout")
        
        # Create dummy video file
        video_path = os.path.join(self.output_dir, f"{clip_id}.mp4")
        with open(video_path, 'w') as f:
            f.write(f"DUMMY VIDEO: {prompt[:50]}")
        
        return video_path
    
    def _simplify_prompt_further(self, prompt: str) -> str:
        """Further simplify prompt after failure"""
        # Keep only first 100 chars and add safe keywords
        simplified = prompt[:100] + " cinematic professional 4K"
        logger.info(f"Simplified prompt to: {simplified}")
        return simplified
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "total_generations": self.generation_count,
            "successful": self.success_count,
            "failed": self.failure_count,
            "success_rate": self.success_count / max(1, self.generation_count),
            "active_jobs": len([j for j in jobs_status.values() if j["status"] == "processing"])
        }


# Initialize service
video_service = VideoGenerationService()


# Background worker for async processing
def process_jobs():
    """Background worker to process jobs from queue"""
    while True:
        try:
            if not job_queue.empty():
                job = job_queue.get()
                logger.info(f"Processing job from queue: {job['job_id']}")
                result = video_service.generate_video(job['request'])
                jobs_status[job['job_id']] = result
        except Exception as e:
            logger.error(f"Job processing error: {e}")
        time.sleep(1)


# Start background worker
worker_thread = threading.Thread(target=process_jobs, daemon=True)
worker_thread.start()


# ============= HTTP API Endpoints =============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "video-generator",
        "timestamp": datetime.now().isoformat(),
        "prompt_optimizer_connected": True  # Check actual connection
    })


@app.route('/generate', methods=['POST'])
def generate_video():
    """Generate video synchronously"""
    try:
        request_data = request.json
        
        if not request_data.get('prompt'):
            return jsonify({"error": "No prompt provided"}), 400
        
        result = video_service.generate_video(request_data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate-async', methods=['POST'])
def generate_video_async():
    """Queue video generation for async processing"""
    try:
        request_data = request.json
        
        if not request_data.get('prompt'):
            return jsonify({"error": "No prompt provided"}), 400
        
        job_id = str(uuid.uuid4())
        job = {
            "job_id": job_id,
            "request": request_data
        }
        
        # Add to queue
        job_queue.put(job)
        
        # Store initial status
        jobs_status[job_id] = {
            "status": "queued",
            "queued_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "job_id": job_id,
            "status": "queued",
            "message": "Job queued for processing"
        })
        
    except Exception as e:
        logger.error(f"Queue error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    if job_id not in jobs_status:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(jobs_status[job_id])


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get service statistics"""
    return jsonify(video_service.get_stats())


@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({
        "total_jobs": len(jobs_status),
        "jobs": list(jobs_status.keys()),
        "summary": {
            "queued": len([j for j in jobs_status.values() if j.get("status") == "queued"]),
            "processing": len([j for j in jobs_status.values() if j.get("status") == "processing"]),
            "completed": len([j for j in jobs_status.values() if j.get("status") == "completed"]),
            "failed": len([j for j in jobs_status.values() if j.get("status") == "failed"])
        }
    })


if __name__ == '__main__':
    logger.info("🎬 Starting Video Generator Service on port 8002")
    app.run(host='0.0.0.0', port=8002, debug=False)