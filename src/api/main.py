"""
FastAPI Backend for ViralAI Advertising Platform
Complete REST API with WebSocket support
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
import uuid
import jwt
import bcrypt
from pathlib import Path
import logging

# Core video generation dependencies
try:
    from src.ai.manager import AIServiceManager
    ai_manager = AIServiceManager()
except ImportError:
    print("Warning: AI manager not available")
    ai_manager = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ViralAI Video Generation Platform",  
    description="AI-powered video generation with real main.py CLI integration",
    version="3.11.0-rc1"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Global instances for video generation only
# (advertising components removed for simplicity)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    organization: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Removed advertising platform models - keeping only video generation models

# Video generation models
class VideoGenerationConfig(BaseModel):
    mission: str
    category: Optional[str] = None
    platform: Optional[str] = 'youtube'
    duration: int = 20
    image_only: bool = False
    fallback_only: bool = False
    force_generation: bool = False
    skip_auth_test: bool = False
    discussion_mode: str = 'enhanced'
    show_discussion_logs: bool = True
    style: Optional[str] = None
    visual_style: Optional[str] = None
    language: str = 'english'
    voice_preference: Optional[str] = None
    
class GenerationSession(BaseModel):
    id: str
    config: VideoGenerationConfig
    status: str = "created"
    created_at: str
    updated_at: str

# In-memory storage (use database in production)
users_db = {}
sessions_db = {}  # Store video generation sessions
generation_progress = {}  # Store generation progress

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ViralAI Video Generation Platform",
        "version": "3.11.0-rc1",
        "status": "online"
    }

# Authentication endpoints
@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user"""
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "organization": user.organization,
        "created_at": datetime.now().isoformat()
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "organization": current_user.get("organization")
    }

# Video Generation Endpoints - Core functionality only

# Video Generation Endpoints
@app.post("/sessions")
async def create_session(config: VideoGenerationConfig):
    """Create a new video generation session"""
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    session = {
        "id": session_id,
        "config": config.dict(),
        "status": "created",
        "created_at": now,
        "updated_at": now
    }
    
    sessions_db[session_id] = session
    generation_progress[session_id] = {
        "progress": 0,
        "status": "created",
        "currentPhase": "Initialization",
        "message": "Session created successfully",
        "startTime": now,
        "agents": [],
        "discussions": []
    }
    
    return session

@app.post("/sessions/{session_id}/generate")
async def start_generation(session_id: str, config: VideoGenerationConfig):
    """Start video generation for a session"""
    logger.info(f"Starting generation for session {session_id}")
    logger.info(f"Config: {config}")
    
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session status
    sessions_db[session_id]["status"] = "generating"
    sessions_db[session_id]["updated_at"] = datetime.now().isoformat()
    
    # Start background generation task with real main.py CLI
    try:
        task = asyncio.create_task(run_real_video_generation(session_id, config))
        logger.info(f"Background task created for session {session_id}")
    except Exception as e:
        logger.error(f"Failed to create background task: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message": "Generation started", "session_id": session_id}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions_db[session_id]

@app.post("/sessions/{session_id}/stop")
async def stop_generation(session_id: str):
    """Stop video generation"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_db[session_id]["status"] = "stopped"
    sessions_db[session_id]["updated_at"] = datetime.now().isoformat()
    
    return {"message": "Generation stopped", "session_id": session_id}

async def run_real_video_generation(session_id: str, config: VideoGenerationConfig):
    """Run actual video generation using main.py CLI"""
    import subprocess
    import os
    from pathlib import Path
    
    try:
        # Check if we need to activate virtual environment
        project_root = Path(__file__).parent.parent.parent
        venv_path = project_root / ".venv"  # Changed to .venv
        
        # Build command with venv activation if needed
        if venv_path.exists() and not os.environ.get('VIRTUAL_ENV'):
            # Virtual environment exists but not activated
            logger.info(f"Activating virtual environment at {venv_path}")
            
            # Use the venv's python directly
            python_executable = venv_path / "bin" / "python3"
            if not python_executable.exists():
                # Windows path
                python_executable = venv_path / "Scripts" / "python.exe"
            
            cmd = [
                str(python_executable), "main.py", "generate",
                "--mission", config.mission,
                "--duration", str(config.duration),
                "--platform", config.platform or "youtube",
                "--discussions", config.discussion_mode,
                "--session-id", session_id,
                "--cheap"  # Use cheap mode for faster testing
            ]
        else:
            # Either venv is already active or doesn't exist
            cmd = [
                "python3", "main.py", "generate",
                "--mission", config.mission,
                "--duration", str(config.duration),
                "--platform", config.platform or "youtube",
                "--discussions", config.discussion_mode,
                "--session-id", session_id,
                "--cheap"  # Use cheap mode for faster testing
            ]
        
        # Add optional arguments
        if config.category:
            cmd.extend(["--category", config.category])
        if config.image_only:
            cmd.append("--image-only")
        if config.fallback_only:
            cmd.append("--fallback-only")
        if config.force_generation:
            cmd.append("--force")
        if config.skip_auth_test:
            cmd.append("--skip-auth-test")
        if config.style:
            cmd.extend(["--style", config.style])
        if config.visual_style:
            cmd.extend(["--visual-style", config.visual_style])
        if config.language:
            # Use --languages (plural) and map language codes
            lang_code = config.language
            if lang_code == "english":
                lang_code = "en-US"
            elif lang_code == "hebrew":
                lang_code = "he"
            elif lang_code == "farsi":
                lang_code = "fa"
            cmd.extend(["--languages", lang_code])
        if config.voice_preference:
            # Voice preference might not be a valid option, skip for now
            pass
            
        logger.info(f"Starting real video generation: {' '.join(cmd)}")
        logger.info(f"Working directory: {Path(__file__).parent.parent.parent}")
        logger.info(f"Python executable: {cmd[0]}")
        
        # Update initial progress
        generation_progress[session_id].update({
            "progress": 5,
            "status": "processing",
            "currentPhase": "Initialization",
            "message": "Starting video generation process..."
        })
        
        await manager.broadcast(json.dumps({
            "event": "progress_update",
            "session_id": session_id,
            "data": generation_progress[session_id]
        }))
        
        # Run the actual generation command
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(__file__).parent.parent.parent  # Go to project root
            )
            logger.info(f"Process started with PID: {process.pid}")
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            raise
        
        # Monitor the process and update progress
        while process.returncode is None:
            if sessions_db[session_id]["status"] == "stopped":
                process.terminate()
                break
                
            # Check for output to parse progress
            try:
                stdout_data = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
                if stdout_data:
                    line = stdout_data.decode().strip()
                    logger.info(f"Generation output: {line}")
                    
                    # Parse progress from output (you'll need to add progress indicators to main.py)
                    if "Discussion phase" in line:
                        generation_progress[session_id].update({
                            "progress": 25,
                            "currentPhase": "AI Discussion",
                            "message": "AI agents discussing and planning..."
                        })
                    elif "Generating script" in line:
                        generation_progress[session_id].update({
                            "progress": 40,
                            "currentPhase": "Script Generation", 
                            "message": "Creating video script..."
                        })
                    elif "Generating video" in line:
                        generation_progress[session_id].update({
                            "progress": 60,
                            "currentPhase": "Video Generation",
                            "message": "AI generating video content..."
                        })
                    elif "Processing audio" in line:
                        generation_progress[session_id].update({
                            "progress": 80,
                            "currentPhase": "Audio Processing",
                            "message": "Creating voiceover and background music..."
                        })
                    elif "Final assembly" in line:
                        generation_progress[session_id].update({
                            "progress": 95,
                            "currentPhase": "Final Assembly",
                            "message": "Combining all elements..."
                        })
                    
                    # Broadcast updated progress
                    await manager.broadcast(json.dumps({
                        "event": "progress_update",
                        "session_id": session_id,
                        "data": generation_progress[session_id]
                    }))
                        
            except asyncio.TimeoutError:
                # No output yet, continue waiting
                pass
            
            await asyncio.sleep(0.5)
        
        # Wait for process to complete
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Generation successful
            sessions_db[session_id]["status"] = "completed"
            sessions_db[session_id]["updated_at"] = datetime.now().isoformat()
            
            generation_progress[session_id].update({
                "progress": 100,
                "status": "completed",
                "currentPhase": "Completed",
                "message": "Video generation completed successfully!"
            })
            
            # Find the generated video file
            output_dir = Path("outputs") / session_id
            video_files = list(output_dir.glob("**/*.mp4"))
            final_video = None
            
            if video_files:
                final_video = {
                    "url": str(video_files[0]),
                    "duration": config.duration,
                    "thumbnail": str(video_files[0]).replace('.mp4', '_thumbnail.jpg')
                }
            
            # Broadcast completion
            await manager.broadcast(json.dumps({
                "event": "generation_complete", 
                "session_id": session_id,
                "data": {
                    "session": sessions_db[session_id],
                    "finalVideo": final_video
                }
            }))
            
        else:
            # Generation failed
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"Generation failed for session {session_id}: {error_msg}")
            sessions_db[session_id]["status"] = "failed"
            generation_progress[session_id].update({
                "status": "failed",
                "message": f"Generation failed: {error_msg}"
            })
            
    except Exception as e:
        logger.error(f"Exception during generation for session {session_id}: {e}")
        sessions_db[session_id]["status"] = "failed"
        generation_progress[session_id].update({
            "status": "failed",
            "message": f"Generation failed: {str(e)}"
        })

# AI endpoints for video generation
@app.post("/api/ai/generate-creative")
async def generate_creative(
    prompt: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Generate creative content with AI"""
    try:
        if not ai_manager:
            raise HTTPException(status_code=503, detail="AI service not available")
            
        # Build AI prompt for video content
        ai_prompt = f"""
        Generate creative video content:
        Brief: {json.dumps(prompt)}
        
        Provide creative concept, script, and visual suggestions for video.
        """
        
        response = ai_manager.generate_text(ai_prompt)
        
        return {
            "creative_id": str(uuid.uuid4()),
            "content": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Parse message
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    websocket
                )
            elif message.get("type") == "subscribe":
                # Handle subscription to specific events
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscribed",
                        "channel": message.get("channel")
                    }),
                    websocket
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Health check endpoints
@app.get("/health") 
async def simple_health_check():
    """Simple health check for frontend"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_manager": "online" if ai_manager else "offline",
            "video_generation": "online",
            "websocket": "online"
        }
    }

# Start background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup"""
    print("✅ ViralAI Video Generation API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 ViralAI Video Generation API stopped")

# Static files can be served in production if needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)