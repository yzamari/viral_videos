#!/usr/bin/env python3
"""
🚀 FastAPI Backend Server for Viral AI Video Generator
Provides REST API and WebSocket endpoints for the React frontend
"""

import os
import sys
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.workflows.generate_viral_video import main as generate_viral_video
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.utils.session_manager import session_manager
from src.utils.logging_config import get_logger

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Viral AI Video Generator API",
    description="REST API for generating viral videos with AI agents",
    version="2.4.1"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class VideoGenerationRequest(BaseModel):
    mission: str
    platform: str = "tiktok"
    duration: int = 20
    category: str = "Educational"
    style: str = "viral"
    tone: str = "comedic"
    mode: str = "enhanced"
    force: bool = False
    target_audience: str = "general audience"
    language: str = "en"

class VideoGenerationResponse(BaseModel):
    session_id: str
    status: str
    message: str
    progress: float = 0.0

# Global state for active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}
websocket_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# API Routes
@app.get("/")
async def root():
    return {"message": "Viral AI Video Generator API", "version": "2.4.1"}

@app.post("/api/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Start video generation process"""
    try:
        # Create session
        session_id = session_manager.create_session(
            topic=request.mission,
            platform=request.platform,
            duration=request.duration,
            category=request.category
        )
        
        # Store request in active sessions
        active_sessions[session_id] = {
            "request": request.dict(),
            "status": "starting",
            "progress": 0.0,
            "start_time": datetime.now().isoformat(),
            "logs": []
        }
        
        # Start generation in background
        background_tasks.add_task(run_video_generation, session_id, request)
        
        return VideoGenerationResponse(
            session_id=session_id,
            status="started",
            message="Video generation started successfully",
            progress=0.0
        )
        
    except Exception as e:
        logger.error(f"Failed to start video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current session status"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]

@app.get("/api/sessions/{session_id}/logs")
async def get_session_logs(session_id: str):
    """Get session logs"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get logs from session directory
        if session_manager.current_session == session_id:
            log_file = session_manager.get_session_path("logs") + "/viral_video_*.log"
            import glob
            log_files = glob.glob(log_file)
            
            if log_files:
                with open(log_files[0], 'r') as f:
                    logs = f.readlines()[-100:]  # Last 100 lines
                return {"logs": logs}
        
        return {"logs": active_sessions[session_id].get("logs", [])}
        
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return {"logs": []}

@app.get("/api/sessions/{session_id}/files")
async def get_session_files(session_id: str):
    """Get session files (videos, audio, scripts, etc.)"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session_dir = f"outputs/{session_id}"
        if not os.path.exists(session_dir):
            return {"files": {}}
        
        files = {}
        
        # Scan for different file types
        for subdir in ["final_output", "video_clips", "audio", "scripts", "subtitles"]:
            subdir_path = os.path.join(session_dir, subdir)
            if os.path.exists(subdir_path):
                files[subdir] = []
                for file in os.listdir(subdir_path):
                    file_path = os.path.join(subdir_path, file)
                    if os.path.isfile(file_path):
                        files[subdir].append({
                            "name": file,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
        
        return {"files": files}
        
    except Exception as e:
        logger.error(f"Failed to get session files: {e}")
        return {"files": {}}

@app.get("/api/sessions/{session_id}/download/{file_type}/{filename}")
async def download_file(session_id: str, file_type: str, filename: str):
    """Download a specific file from session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = f"outputs/{session_id}/{file_type}/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    websocket_connections[session_id] = websocket
    
    try:
        while True:
            # Keep connection alive and send updates
            if session_id in active_sessions:
                await websocket.send_text(json.dumps(active_sessions[session_id]))
            
            await asyncio.sleep(2)  # Send updates every 2 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if session_id in websocket_connections:
            del websocket_connections[session_id]

async def run_video_generation(session_id: str, request: VideoGenerationRequest):
    """Run video generation in background"""
    try:
        # Update status
        active_sessions[session_id]["status"] = "generating"
        active_sessions[session_id]["progress"] = 10.0
        
        # Create config
        config = GeneratedVideoConfig(
            topic=request.mission,
            duration_seconds=request.duration,
            target_platform=Platform(request.platform.upper()),
            category=VideoCategory(request.category.upper()),
            visual_style=request.style,
            tone=request.tone,
            target_audience=request.target_audience,
            language=request.language
        )
        
        # Update progress
        active_sessions[session_id]["progress"] = 20.0
        
        # Generate video
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            generate_viral_video,
            request.mission,
            request.category,
            request.platform,
            request.duration,
            False,  # image_only
            False,  # fallback_only
            request.force,
            request.mode,  # discussions
            False,  # discussion_log
            session_id,
            "auto",  # frame_continuity
            request.target_audience,
            request.style,
            request.tone,
            request.style,  # visual_style
            request.mode
        )
        
        # Update final status
        active_sessions[session_id]["status"] = "completed"
        active_sessions[session_id]["progress"] = 100.0
        active_sessions[session_id]["result"] = result
        active_sessions[session_id]["end_time"] = datetime.now().isoformat()
        
        # Send WebSocket update
        if session_id in websocket_connections:
            await websocket_connections[session_id].send_text(
                json.dumps(active_sessions[session_id])
            )
        
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        active_sessions[session_id]["status"] = "failed"
        active_sessions[session_id]["error"] = str(e)
        active_sessions[session_id]["end_time"] = datetime.now().isoformat()

# Serve static files (build frontend)
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    print("🚀 Starting Viral AI Backend Server")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🎬 Frontend: http://localhost:8000")
    print("🔌 WebSocket: ws://localhost:8000/ws/{session_id}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)