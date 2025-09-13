"""
Refactored FastAPI Backend for ViralAI using OOP Architecture.

This refactored version implements proper OOP principles, SOLID design patterns,
and clean architecture separation while maintaining backward compatibility.
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import asyncio
import logging

# Enhanced DI Container
from src.infrastructure.enhanced_di_container import (
    get_enhanced_container, 
    configure_enhanced_container,
    get_enhanced_health_status
)

# Controllers
from src.api.controllers.auth_controller import (
    AuthController, 
    UserRegistrationRequest,
    UserLoginRequest, 
    PasswordChangeRequest
)
from src.api.controllers.video_controller import (
    VideoController,
    VideoGenerationRequest
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with enhanced metadata
app = FastAPI(
    title="ViralAI Video Generation Platform",  
    description="AI-powered video generation with OOP architecture and clean design patterns",
    version="4.0.0-oop-refactor",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# WebSocket connection manager (keeping existing implementation for compatibility)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

# Global WebSocket manager
manager = ConnectionManager()

# Initialize DI Container with configuration
container_config = {
    "data_path": "data",
    "jwt": {
        "secret_key": "your-secret-key-change-in-production",  # TODO: Use environment variable
        "algorithm": "HS256",
        "access_token_expire_minutes": 30
    },
    "video_generation": {
        "max_concurrent_generations": 5
    }
}

# Configure container
container = configure_enhanced_container(container_config)

# Initialize controllers
auth_controller = AuthController(container.get_authentication_service())
video_controller = VideoController(
    container.get_authentication_service(),
    container.get_video_generation_service()
)


# Dependency functions for FastAPI
async def get_current_user_token(token: str = Depends(oauth2_scheme)) -> str:
    """Extract JWT token for dependency injection"""
    return token


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "ViralAI Video Generation Platform",
        "version": "4.0.0-oop-refactor",
        "status": "online",
        "architecture": "OOP with SOLID principles",
        "timestamp": datetime.now().isoformat()
    }


# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(request: UserRegistrationRequest):
    """Register a new user"""
    return await auth_controller.register_user(request)


@app.post("/api/auth/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token"""
    return await auth_controller.login_user(form_data)


@app.get("/api/auth/me")
async def get_current_user(token: str = Depends(get_current_user_token)):
    """Get current user profile"""
    return await auth_controller.get_current_user_profile(token)


@app.post("/api/auth/change-password")
async def change_password(request: PasswordChangeRequest, token: str = Depends(get_current_user_token)):
    """Change user password"""
    return await auth_controller.change_password(token, request)


@app.post("/api/auth/refresh")
async def refresh_token(token: str = Depends(get_current_user_token)):
    """Refresh access token"""
    return await auth_controller.refresh_token(token)


@app.post("/api/auth/verify-email/{user_id}")
async def verify_email(user_id: str, verification_token: str):
    """Verify user email address"""
    return await auth_controller.verify_email(user_id, verification_token)


@app.post("/api/auth/reset-password")
async def request_password_reset(email: str):
    """Request password reset"""
    return await auth_controller.request_password_reset(email)


# Video generation endpoints
@app.post("/api/video/sessions")
async def create_video_session(request: VideoGenerationRequest, token: str = Depends(get_current_user_token)):
    """Create a new video generation session"""
    return await video_controller.create_video_session(token, request)


@app.post("/api/video/sessions/{session_id}/start")
async def start_video_generation(session_id: str, token: str = Depends(get_current_user_token)):
    """Start video generation for a session"""
    return await video_controller.start_video_generation(token, session_id)


@app.get("/api/video/sessions/{session_id}/progress")
async def get_generation_progress(session_id: str, token: str = Depends(get_current_user_token)):
    """Get generation progress for a session"""
    return await video_controller.get_generation_progress(token, session_id)


@app.post("/api/video/sessions/{session_id}/cancel")
async def cancel_generation(session_id: str, token: str = Depends(get_current_user_token)):
    """Cancel video generation for a session"""
    return await video_controller.cancel_generation(token, session_id)


@app.get("/api/video/sessions")
async def get_user_sessions(
    token: str = Depends(get_current_user_token),
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None
):
    """Get user's video sessions with pagination"""
    return await video_controller.get_user_sessions(token, page, limit, status)


@app.get("/api/video/sessions/{session_id}")
async def get_session_details(session_id: str, token: str = Depends(get_current_user_token)):
    """Get detailed information about a specific session"""
    return await video_controller.get_session_details(token, session_id)


@app.post("/api/video/validate")
async def validate_generation_config(request: VideoGenerationRequest, token: str = Depends(get_current_user_token)):
    """Validate video generation configuration"""
    return await video_controller.validate_generation_config(token, request)


@app.get("/api/video/queue")
async def get_generation_queue_status(token: str = Depends(get_current_user_token)):
    """Get current video generation queue status"""
    return await video_controller.get_generation_queue_status(token)


# Legacy endpoints for backward compatibility
@app.post("/sessions")
async def create_session_legacy(config: Dict[str, Any]):
    """Legacy session creation endpoint for backward compatibility"""
    logger.warning("Using legacy session creation endpoint - consider upgrading to /api/video/sessions")
    
    try:
        # Convert legacy config to new format
        request = VideoGenerationRequest(
            mission=config.get("mission", ""),
            platform=config.get("platform", "youtube"),
            duration=config.get("duration", 20),
            discussion_mode=config.get("discussion_mode", "enhanced"),
            **{k: v for k, v in config.items() if k in VideoGenerationRequest.__fields__}
        )
        
        # For legacy compatibility, we'll need a way to handle authentication
        # This is a simplified version - in production, you'd need proper auth handling
        return {
            "id": f"legacy-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": "Legacy endpoint - please upgrade to /api/video/sessions",
            "status": "deprecated"
        }
        
    except Exception as e:
        logger.error(f"Legacy endpoint error: {e}")
        raise HTTPException(status_code=400, detail="Legacy endpoint error")


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                        websocket
                    )
                elif message.get("type") == "subscribe":
                    channel = message.get("channel", "default")
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "subscribed",
                            "channel": channel,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                else:
                    logger.warning(f"Unknown WebSocket message type: {message.get('type')}")
                    
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in WebSocket message")
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON"}),
                    websocket
                )
            except Exception as e:
                logger.error(f"WebSocket message processing error: {e}")
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


# Health check endpoints
@app.get("/health")
async def simple_health_check():
    """Simple health check for load balancers"""
    return {
        "status": "ok", 
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0-oop-refactor"
    }


@app.get("/api/health")
async def detailed_health_check():
    """Detailed health check with component status"""
    try:
        # Get health status from enhanced container
        container_health = get_enhanced_health_status()
        
        # Add additional service checks
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "4.0.0-oop-refactor",
            "container": container_health,
            "services": {
                "websocket": "online",
                "api": "online"
            },
            "active_connections": len(manager.active_connections)
        }
        
        # Determine overall health
        if container_health.get("status") != "healthy":
            health_data["status"] = "degraded"
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


# System information endpoint
@app.get("/api/system/info")
async def get_system_info(token: str = Depends(get_current_user_token)):
    """Get system information (authenticated endpoint)"""
    try:
        # Verify user is authenticated
        user = await container.get_authentication_service().verify_access_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        container_health = get_enhanced_health_status()
        
        return {
            "architecture": "OOP with SOLID principles",
            "version": "4.0.0-oop-refactor",
            "components": {
                "controllers": ["AuthController", "VideoController"],
                "services": ["AuthenticationService", "VideoGenerationService"],
                "repositories": ["UserRepository", "VideoSessionRepository"],
                "container": "EnhancedDIContainer"
            },
            "health": container_health,
            "request_user": {
                "id": user.id,
                "username": user.username,
                "role": user.role.value
            }
        }
        
    except Exception as e:
        logger.error(f"System info error: {e}")
        raise HTTPException(status_code=500, detail="System information unavailable")


# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 ViralAI OOP Refactored API starting up...")
    
    # Perform health check on startup
    health = get_enhanced_health_status()
    if health.get("status") == "healthy":
        logger.info("✅ All components initialized successfully")
    else:
        logger.warning(f"⚠️ Some components have issues: {health}")
    
    logger.info("📡 WebSocket manager initialized")
    logger.info("🎯 OOP Architecture with SOLID principles active")
    logger.info("🔒 Enhanced authentication and authorization ready")
    logger.info("🎬 Video generation services online")
    

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 ViralAI OOP Refactored API shutting down...")
    
    # Close all WebSocket connections
    if manager.active_connections:
        logger.info(f"📡 Closing {len(manager.active_connections)} WebSocket connections")
        for connection in manager.active_connections.copy():
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {e}")
    
    logger.info("👋 ViralAI OOP Refactored API stopped")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "success": False,
        "message": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "success": False,
        "message": "Internal server error",
        "status_code": 500,
        "timestamp": datetime.now().isoformat()
    }


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting ViralAI OOP Refactored API server...")
    uvicorn.run(
        "src.api.refactored_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )