"""
Simplified API for testing - bypasses complex dependencies
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import jwt
import json
import uuid
import asyncio
from collections import defaultdict

# Initialize FastAPI app
app = FastAPI(title="ViralAI Test API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage (for testing)
users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "testpass123",  # In real app, this would be hashed
        "full_name": "Test User"
    }
}

campaigns_db = {}
analytics_db = defaultdict(list)
trending_db = {}
workflows_db = {}

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
    full_name: str

class Campaign(BaseModel):
    name: str
    objective: str
    platforms: List[str]
    budget: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CampaignResponse(BaseModel):
    id: str
    name: str
    objective: str
    platforms: List[str]
    budget: float
    status: str
    created_at: str

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
async def root():
    return {"message": "ViralAI Test API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["hashed_password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/user/profile", response_model=User)
async def get_profile(username: str = Depends(verify_token)):
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"]
    )

# Campaign endpoints
@app.post("/api/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: Campaign,
    username: str = Depends(verify_token)
):
    campaign_id = str(uuid.uuid4())
    campaign_data = {
        "id": campaign_id,
        "name": campaign.name,
        "objective": campaign.objective,
        "platforms": campaign.platforms,
        "budget": campaign.budget,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "user": username
    }
    campaigns_db[campaign_id] = campaign_data
    
    return CampaignResponse(**campaign_data)

@app.get("/api/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(username: str = Depends(verify_token)):
    user_campaigns = [
        CampaignResponse(**c) 
        for c in campaigns_db.values() 
        if c.get("user") == username
    ]
    return user_campaigns

@app.get("/api/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    username: str = Depends(verify_token)
):
    campaign = campaigns_db.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.get("user") != username:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return CampaignResponse(**campaign)

@app.post("/api/campaigns/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: str,
    username: str = Depends(verify_token)
):
    campaign = campaigns_db.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.get("user") != username:
        raise HTTPException(status_code=403, detail="Access denied")
    
    campaign["status"] = "active"
    return {"message": "Campaign launched", "campaign_id": campaign_id}

# Analytics endpoints
@app.get("/api/analytics/overview")
async def get_analytics_overview(username: str = Depends(verify_token)):
    # Return mock analytics data
    return {
        "total_impressions": 125000,
        "total_clicks": 3500,
        "total_conversions": 250,
        "total_spend": 2500.00,
        "average_ctr": 0.028,
        "average_cvr": 0.071,
        "average_cpa": 10.00,
        "roas": 3.5
    }

@app.get("/api/analytics/campaigns/{campaign_id}")
async def get_campaign_analytics(
    campaign_id: str,
    username: str = Depends(verify_token)
):
    campaign = campaigns_db.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "impressions": 25000,
        "clicks": 750,
        "conversions": 50,
        "spend": campaign["budget"] * 0.5,
        "ctr": 0.03,
        "cvr": 0.067,
        "cpa": campaign["budget"] * 0.01,
        "roas": 2.8
    }

# Trending endpoints
@app.get("/api/trending")
async def get_trending(username: str = Depends(verify_token)):
    return {
        "trending_topics": [
            {"topic": "AI Innovation", "score": 0.92, "platform": "twitter"},
            {"topic": "Sustainable Tech", "score": 0.87, "platform": "linkedin"},
            {"topic": "Viral Dance", "score": 0.95, "platform": "tiktok"}
        ],
        "trending_hashtags": [
            {"hashtag": "#TechTrends2024", "usage_count": 150000},
            {"hashtag": "#AIRevolution", "usage_count": 125000},
            {"hashtag": "#FutureOfWork", "usage_count": 98000}
        ],
        "viral_content": [
            {
                "title": "AI Breakthrough Announcement",
                "views": 2500000,
                "engagement_rate": 0.12,
                "platform": "youtube"
            }
        ]
    }

# Workflow endpoints
@app.post("/api/workflows")
async def create_workflow(
    workflow: Dict[str, Any],
    username: str = Depends(verify_token)
):
    workflow_id = str(uuid.uuid4())
    workflow_data = {
        "id": workflow_id,
        "name": workflow.get("name", "New Workflow"),
        "triggers": workflow.get("triggers", []),
        "actions": workflow.get("actions", []),
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "user": username
    }
    workflows_db[workflow_id] = workflow_data
    
    return workflow_data

@app.get("/api/workflows")
async def list_workflows(username: str = Depends(verify_token)):
    user_workflows = [
        w for w in workflows_db.values() 
        if w.get("user") == username
    ]
    return user_workflows

# WebSocket endpoint for real-time updates (simplified)
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)