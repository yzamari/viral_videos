"""
FastAPI Backend for ViralAI Advertising Platform
Complete REST API with WebSocket support
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
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

# Core video generation dependencies
try:
    from src.ai.manager import AIServiceManager
    ai_manager = AIServiceManager()
except ImportError:
    print("Warning: AI manager not available")
    ai_manager = None

# Video generation imports
import asyncio
from typing import Optional
import time
import logging

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

class CampaignCreate(BaseModel):
    name: str
    objective: str
    platforms: List[str]
    budget: float
    target_audience: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    target_audience: Optional[Dict[str, Any]] = None

class WorkflowCreate(BaseModel):
    name: str
    description: str
    triggers: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    variables: Optional[Dict[str, Any]] = {}

class AnalyticsQuery(BaseModel):
    metric_types: Optional[List[str]] = None
    dimensions: Optional[Dict[str, str]] = None
    time_range: Optional[Dict[str, str]] = None
    granularity: Optional[str] = "daily"

class TrendingQuery(BaseModel):
    platform: Optional[str] = None
    keyword: Optional[str] = None
    limit: int = 20

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
        "name": "ViralAI Advertising Platform",
        "version": "3.0.0",
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

# Campaign endpoints
@app.post("/api/campaigns")
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new campaign"""
    try:
        # Parse objective and platforms
        objective = CampaignObjective[campaign_data.objective.upper()]
        platforms = [Platform[p.upper()] for p in campaign_data.platforms]
        
        # Create target audience if provided
        target_audience = None
        if campaign_data.target_audience:
            target_audience = TargetAudience(**campaign_data.target_audience)
        
        # Create campaign
        campaign = campaign_manager.create_campaign(
            name=campaign_data.name,
            objective=objective,
            platforms=platforms,
            budget=campaign_data.budget,
            target_audience=target_audience
        )
        
        # Broadcast update via WebSocket
        await manager.broadcast(json.dumps({
            "event": "campaign_created",
            "data": {
                "campaign_id": campaign.campaign_id,
                "name": campaign.name,
                "status": campaign.status.value
            }
        }))
        
        return {
            "campaign_id": campaign.campaign_id,
            "name": campaign.name,
            "status": campaign.status.value,
            "created_at": campaign.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/campaigns")
async def list_campaigns(
    current_user: dict = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0
):
    """List all campaigns"""
    campaigns = list(campaign_manager.campaigns.values())[offset:offset+limit]
    
    return {
        "campaigns": [
            {
                "campaign_id": c.campaign_id,
                "name": c.name,
                "objective": c.objective.value,
                "status": c.status.value,
                "platforms": [p.value for p in c.platforms],
                "budget": sum(b.amount for b in c.budget_allocations),
                "created_at": c.created_at.isoformat()
            }
            for c in campaigns
        ],
        "total": len(campaign_manager.campaigns),
        "limit": limit,
        "offset": offset
    }

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get campaign details"""
    campaign = campaign_manager.campaigns.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get performance metrics
    metrics = campaign_manager.performance_tracker.get_metrics(campaign_id)
    
    return {
        "campaign": {
            "campaign_id": campaign.campaign_id,
            "name": campaign.name,
            "objective": campaign.objective.value,
            "status": campaign.status.value,
            "platforms": [p.value for p in campaign.platforms],
            "budget_allocations": [
                {
                    "platform": b.platform.value,
                    "amount": b.amount,
                    "daily_limit": b.daily_limit
                }
                for b in campaign.budget_allocations
            ],
            "target_audience": campaign.target_audience.__dict__ if campaign.target_audience else {},
            "created_at": campaign.created_at.isoformat()
        },
        "metrics": metrics
    }

@app.put("/api/campaigns/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    updates: CampaignUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update campaign"""
    campaign = campaign_manager.campaigns.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Apply updates
    if updates.name:
        campaign.name = updates.name
    if updates.budget:
        # Redistribute budget
        total_platforms = len(campaign.platforms)
        for allocation in campaign.budget_allocations:
            allocation.amount = updates.budget / total_platforms
    if updates.status:
        campaign.status = updates.status
    
    campaign.updated_at = datetime.now()
    
    return {"message": "Campaign updated", "campaign_id": campaign_id}

@app.post("/api/campaigns/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Launch a campaign"""
    try:
        result = await campaign_manager.launch_campaign(campaign_id)
        
        # Broadcast update
        await manager.broadcast(json.dumps({
            "event": "campaign_launched",
            "data": {"campaign_id": campaign_id}
        }))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pause a campaign"""
    try:
        campaign = campaign_manager.pause_campaign(campaign_id)
        return {"message": "Campaign paused", "status": campaign.status.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/campaigns/{campaign_id}/optimize")
async def optimize_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Optimize a campaign"""
    try:
        optimizations = campaign_manager.optimize_campaign(campaign_id)
        return optimizations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Analytics endpoints
@app.post("/api/analytics/query")
async def query_analytics(
    query: AnalyticsQuery,
    current_user: dict = Depends(get_current_user)
):
    """Query analytics data"""
    # Parse time range
    time_range = None
    if query.time_range:
        start = datetime.fromisoformat(query.time_range["start"])
        end = datetime.fromisoformat(query.time_range["end"])
        time_range = (start, end)
    
    # Parse metric types
    metric_types = None
    if query.metric_types:
        metric_types = [MetricType[m.upper()] for m in query.metric_types]
    
    # Get metrics
    df = analytics_dashboard.get_metrics(
        metric_types=metric_types,
        dimensions=query.dimensions,
        time_range=time_range
    )
    
    # Convert to JSON-serializable format
    if not df.empty:
        data = df.to_dict(orient='records')
    else:
        data = []
    
    return {"data": data, "count": len(data)}

@app.get("/api/analytics/report/{campaign_id}")
async def get_campaign_report(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get campaign performance report"""
    report = campaign_manager.get_campaign_report(campaign_id)
    return report

@app.get("/api/analytics/dashboard")
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get dashboard overview data"""
    # Get summary metrics for all campaigns
    total_campaigns = len(campaign_manager.campaigns)
    active_campaigns = sum(
        1 for c in campaign_manager.campaigns.values()
        if c.status.value == "active"
    )
    
    # Calculate total spend and revenue
    total_spend = 0
    total_revenue = 0
    
    for campaign_id in campaign_manager.campaigns:
        metrics = campaign_manager.performance_tracker.get_metrics(campaign_id)
        total_spend += metrics.get("spend", 0)
        total_revenue += metrics.get("revenue", 0)
    
    return {
        "overview": {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_spend": total_spend,
            "total_revenue": total_revenue,
            "overall_roas": total_revenue / total_spend if total_spend > 0 else 0
        },
        "recent_campaigns": [
            {
                "campaign_id": c.campaign_id,
                "name": c.name,
                "status": c.status.value,
                "created_at": c.created_at.isoformat()
            }
            for c in sorted(
                campaign_manager.campaigns.values(),
                key=lambda x: x.created_at,
                reverse=True
            )[:5]
        ]
    }

# Trending endpoints
@app.post("/api/trending/analyze")
async def analyze_trending(
    query: TrendingQuery,
    current_user: dict = Depends(get_current_user)
):
    """Get trending data analysis"""
    trending_data = trending_analyzer.get_all_trending_data(
        platform=query.platform,
        keyword=query.keyword,
        limit=query.limit
    )
    
    return trending_data

@app.get("/api/trending/viral")
async def get_viral_opportunities(current_user: dict = Depends(get_current_user)):
    """Get current viral opportunities"""
    # Get trending data from all platforms
    trending = trending_analyzer.get_all_trending_data(limit=10)
    
    # Calculate viral scores
    opportunities = []
    for platform, data in trending.get("platforms", {}).items():
        if "error" not in data:
            # Calculate viral score (simplified)
            viral_score = 0.5  # Base score
            
            if "trending_hashtags" in data:
                top_score = max(
                    (h.get("trend_score", 0) for h in data["trending_hashtags"][:3]),
                    default=0
                )
                viral_score += top_score * 0.5
            
            opportunities.append({
                "platform": platform,
                "viral_score": min(viral_score, 1.0),
                "top_trends": data.get("trending_hashtags", [])[:3]
            })
    
    # Sort by viral score
    opportunities.sort(key=lambda x: x["viral_score"], reverse=True)
    
    return {"opportunities": opportunities}

# Workflow endpoints
@app.post("/api/workflows")
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new workflow"""
    template = WorkflowTemplate(
        name=workflow_data.name,
        description=workflow_data.description,
        triggers=workflow_data.triggers,
        actions=workflow_data.actions,
        variables=workflow_data.variables
    )
    
    workflow_id = workflow_engine.create_workflow(template)
    
    return {
        "workflow_id": workflow_id,
        "name": workflow_data.name,
        "status": "created"
    }

@app.get("/api/workflows")
async def list_workflows(current_user: dict = Depends(get_current_user)):
    """List all workflows"""
    workflows = [
        {
            "workflow_id": w.template_id,
            "name": w.name,
            "description": w.description,
            "triggers": len(w.triggers),
            "actions": len(w.actions),
            "created_at": w.created_at.isoformat()
        }
        for w in workflow_engine.workflows.values()
    ]
    
    return {"workflows": workflows}

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    variables: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Execute a workflow manually"""
    try:
        execution = await workflow_engine.execute_workflow(
            workflow_id,
            trigger_data={"trigger": "manual", "user": current_user["username"]},
            variables=variables
        )
        
        return {
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/workflows/executions/{execution_id}")
async def get_workflow_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workflow execution status"""
    status = workflow_engine.get_workflow_status(execution_id)
    return status

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
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session status
    sessions_db[session_id]["status"] = "generating"
    sessions_db[session_id]["updated_at"] = datetime.now().isoformat()
    
    # Start background generation task with real main.py CLI
    asyncio.create_task(run_real_video_generation(session_id, config))
    
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
        # Build command arguments
        cmd = [
            "python", "main.py",
            "--mission", config.mission,
            "--duration", str(config.duration),
            "--platform", config.platform or "youtube",
            "--discussions", config.discussion_mode,
            "--session-id", session_id
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
            cmd.extend(["--language", config.language])
        if config.voice_preference:
            cmd.extend(["--voice", config.voice_preference])
            
        logger.info(f"Starting real video generation: {' '.join(cmd)}")
        
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
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=Path(__file__).parent.parent.parent  # Go to project root
        )
        
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

# AI endpoints
@app.post("/api/ai/generate-creative")
async def generate_creative(
    prompt: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Generate creative content with AI"""
    try:
        # Get trending context
        trending = trending_analyzer.get_all_trending_data(limit=5)
        
        # Build AI prompt
        ai_prompt = f"""
        Generate creative content for advertising:
        Brief: {json.dumps(prompt)}
        Current Trends: {json.dumps(trending['unified_insights'])}
        
        Provide creative concept, copy, and visual suggestions.
        """
        
        response = ai_manager.generate_text(ai_prompt)
        
        return {
            "creative_id": str(uuid.uuid4()),
            "content": response,
            "trending_context": trending['unified_insights']
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
            "campaign_manager": "online",
            "analytics": "online",
            "trending": "online",
            "workflows": "online"
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

# Serve static files in production
# app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)