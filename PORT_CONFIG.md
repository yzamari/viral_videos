# Port Configuration

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| **Backend API** | 8770 | http://localhost:8770 |
| **Frontend** | 5173 | http://localhost:5173 |
| **Frontend (alt)** | 5174 | http://localhost:5174 |

## Files Updated for Port 8770

1. **Shell Scripts:**
   - `start_app.sh` - Backend port set to 8770
   - `stop_app.sh` - Kills processes on port 8770

2. **Frontend Configuration:**
   - `frontend/src/services/api.ts` - API base URL: http://localhost:8770
   - `frontend/src/services/websocket.ts` - WebSocket URL: ws://localhost:8770

3. **Backend:**
   - API runs on port 8770 when using `start_app.sh`

## Quick Start

```bash
# Start both backend and frontend
./start_app.sh

# Stop all services
./stop_app.sh
```

## Manual Start Commands

```bash
# Backend (port 8770)
python3 -m uvicorn src.api.main_test:app --host 0.0.0.0 --port 8770

# Frontend (port 5173)
cd frontend && npm run dev
```

## API Endpoints

- Health Check: http://localhost:8770/health
- API Documentation: http://localhost:8770/docs
- Frontend: http://localhost:5173