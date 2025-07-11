# 🚀 AI Video Generator - Production Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying the enterprise-grade AI Video Generator system to production environments. The system is now production-ready with enterprise patterns, monitoring, caching, and resilience features.

## 🎯 **DEPLOYMENT PREREQUISITES**

### **System Requirements**
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- **Python**: 3.9+ (3.11+ recommended)
- **Memory**: 8GB RAM minimum, 16GB+ recommended
- **Storage**: 100GB+ available space for video generation
- **CPU**: 4+ cores recommended for concurrent processing
- **Network**: Stable internet connection for API calls

### **Required Services**
- **Google Cloud Platform**: Vertex AI, Cloud Storage access
- **API Keys**: Google AI Studio / Vertex AI credentials
- **Optional**: Redis for distributed caching (production)
- **Optional**: PostgreSQL for session metadata (enterprise)

## 🔧 **DEPLOYMENT METHODS**

### **Method 1: Direct Server Deployment (Recommended)**

#### **Step 1: System Preparation**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3.11-dev -y
sudo apt install build-essential ffmpeg -y

# Create deployment user
sudo useradd -m -s /bin/bash viralai
sudo usermod -aG sudo viralai
```

#### **Step 2: Application Setup**
```bash
# Switch to deployment user
sudo su - viralai

# Clone repository
git clone https://github.com/yzamari/viral_videos.git
cd viral_videos

# Switch to production branch
git checkout comprehensive-refactoring

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn supervisor redis psutil
```

#### **Step 3: Configuration**
```bash
# Copy configuration template
cp config.env.example config.env

# Edit configuration (replace with your values)
nano config.env
```

**Required Configuration:**
```env
# Google AI Configuration
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
VERTEX_AI_PROJECT_ID=your_vertex_project_id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_GCS_BUCKET=your_gcs_bucket_name

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
SESSION_CLEANUP_INTERVAL=3600
CACHE_ENABLED=true
MONITORING_ENABLED=true

# Optional: Redis for distributed caching
REDIS_URL=redis://localhost:6379/0

# Optional: PostgreSQL for session metadata
DATABASE_URL=postgresql://user:password@localhost:5432/viralai
```

#### **Step 4: System Services Setup**
```bash
# Create systemd service file
sudo tee /etc/systemd/system/viralai.service > /dev/null <<EOF
[Unit]
Description=AI Video Generator Service
After=network.target

[Service]
Type=simple
User=viralai
WorkingDirectory=/home/viralai/viral_videos
Environment=PATH=/home/viralai/viral_videos/venv/bin
ExecStart=/home/viralai/viral_videos/venv/bin/python main.py --mode production
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create GUI service file
sudo tee /etc/systemd/system/viralai-gui.service > /dev/null <<EOF
[Unit]
Description=AI Video Generator GUI Service
After=network.target

[Service]
Type=simple
User=viralai
WorkingDirectory=/home/viralai/viral_videos
Environment=PATH=/home/viralai/viral_videos/venv/bin
ExecStart=/home/viralai/viral_videos/venv/bin/python modern_ui.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable viralai
sudo systemctl enable viralai-gui
sudo systemctl start viralai
sudo systemctl start viralai-gui
```

#### **Step 5: Nginx Reverse Proxy (Optional)**
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/viralai > /dev/null <<EOF
server {
    listen 80;
    server_name your_domain.com;
    
    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for real-time updates
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Large file uploads
        client_max_body_size 100M;
    }
    
    location /static/ {
        alias /home/viralai/viral_videos/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/viralai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Method 2: Docker Deployment**

#### **Step 1: Create Dockerfile**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -s /bin/bash viralai
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R viralai:viralai /app

# Switch to application user
USER viralai

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start application
CMD ["python", "modern_ui.py"]
```

#### **Step 2: Docker Compose**
```yaml
version: '3.8'

services:
  viralai:
    build: .
    ports:
      - "7860:7860"
    environment:
      - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
      - VERTEX_AI_PROJECT_ID=${VERTEX_AI_PROJECT_ID}
      - VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION}
      - VERTEX_AI_GCS_BUCKET=${VERTEX_AI_GCS_BUCKET}
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./outputs:/app/outputs
      - ./logs:/app/logs
      - ./cache:/app/cache
    depends_on:
      - redis
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - viralai
    restart: unless-stopped

volumes:
  redis_data:
```

#### **Step 3: Deploy with Docker**
```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f viralai
```

### **Method 3: Kubernetes Deployment**

#### **Step 1: Create Kubernetes Manifests**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: viralai-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: viralai
  template:
    metadata:
      labels:
        app: viralai
    spec:
      containers:
      - name: viralai
        image: viralai:latest
        ports:
        - containerPort: 7860
        env:
        - name: GOOGLE_AI_API_KEY
          valueFrom:
            secretKeyRef:
              name: viralai-secrets
              key: google-ai-api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: outputs
          mountPath: /app/outputs
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: outputs
        persistentVolumeClaim:
          claimName: viralai-outputs-pvc
      - name: cache
        persistentVolumeClaim:
          claimName: viralai-cache-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: viralai-service
spec:
  selector:
    app: viralai
  ports:
  - port: 80
    targetPort: 7860
  type: LoadBalancer
```

## 📊 **MONITORING & OBSERVABILITY**

### **Production Monitoring Setup**

#### **Step 1: Enable System Monitoring**
```python
# Add to your production configuration
MONITORING_CONFIG = {
    'enabled': True,
    'metrics_interval': 30,
    'performance_thresholds': {
        'cpu_usage': 80.0,
        'memory_usage': 85.0,
        'disk_usage': 90.0,
        'api_response_time': 10.0,
        'generation_time': 300.0
    },
    'alerting': {
        'email_notifications': True,
        'slack_webhook': 'your_slack_webhook_url',
        'pagerduty_integration': True
    }
}
```

#### **Step 2: Log Management**
```bash
# Configure log rotation
sudo tee /etc/logrotate.d/viralai > /dev/null <<EOF
/home/viralai/viral_videos/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 viralai viralai
    postrotate
        systemctl reload viralai
    endscript
}
EOF
```

#### **Step 3: Health Checks**
```python
# Add health check endpoint
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.2.0',
        'components': {
            'session_manager': 'healthy',
            'cache_manager': 'healthy',
            'circuit_breaker': 'healthy',
            'performance_monitor': 'healthy'
        }
    }
```

## 🔒 **SECURITY CONFIGURATION**

### **API Security**
```python
# Add to production configuration
SECURITY_CONFIG = {
    'api_rate_limiting': {
        'enabled': True,
        'requests_per_minute': 60,
        'burst_limit': 10
    },
    'authentication': {
        'required': True,
        'method': 'api_key',  # or 'oauth2', 'jwt'
        'api_key_header': 'X-API-Key'
    },
    'cors': {
        'enabled': True,
        'allowed_origins': ['https://your-domain.com'],
        'allowed_methods': ['GET', 'POST'],
        'allowed_headers': ['Content-Type', 'Authorization']
    }
}
```

### **File System Security**
```bash
# Set proper permissions
chmod 750 /home/viralai/viral_videos
chmod 640 /home/viralai/viral_videos/config.env
chown -R viralai:viralai /home/viralai/viral_videos

# Secure outputs directory
chmod 755 /home/viralai/viral_videos/outputs
```

## 🔧 **PERFORMANCE OPTIMIZATION**

### **Production Optimizations**
```python
# Add to production configuration
PERFORMANCE_CONFIG = {
    'caching': {
        'enabled': True,
        'strategy': 'redis',  # or 'memory', 'disk'
        'ttl_seconds': 3600,
        'max_size': 1000
    },
    'concurrency': {
        'max_workers': 4,
        'thread_pool_size': 8,
        'async_processing': True
    },
    'resource_limits': {
        'max_memory_mb': 4096,
        'max_disk_gb': 100,
        'max_generation_time': 600
    }
}
```

### **Database Optimization (Optional)**
```sql
-- PostgreSQL session metadata schema
CREATE TABLE sessions (
    id VARCHAR(50) PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    duration INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB
);

CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_status ON sessions(status);
```

## 📋 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] Environment variables configured
- [ ] API keys and credentials secured
- [ ] Database migrations completed (if applicable)
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Backup strategy implemented

### **Deployment**
- [ ] Application deployed and running
- [ ] Services started and enabled
- [ ] Health checks passing
- [ ] Monitoring enabled
- [ ] Logs configured and rotating
- [ ] Performance metrics collecting

### **Post-Deployment**
- [ ] End-to-end testing completed
- [ ] Performance benchmarks validated
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Rollback plan prepared

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

#### **Service Won't Start**
```bash
# Check service status
sudo systemctl status viralai

# Check logs
sudo journalctl -u viralai -f

# Check configuration
python -c "from config.config import settings; print(settings)"
```

#### **High Memory Usage**
```bash
# Monitor memory usage
htop

# Check cache usage
redis-cli info memory

# Restart services if needed
sudo systemctl restart viralai
```

#### **API Quota Exceeded**
```bash
# Check quota usage
python check_quota.py

# Monitor API calls
tail -f logs/api_calls.log
```

## 📞 **SUPPORT & MAINTENANCE**

### **Regular Maintenance Tasks**
- **Daily**: Check system health and logs
- **Weekly**: Review performance metrics and optimize
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Capacity planning and scaling review

### **Backup Strategy**
```bash
# Backup configuration
tar -czf backup-config-$(date +%Y%m%d).tar.gz config/

# Backup outputs (if needed)
rsync -av outputs/ backup-server:/backups/viralai/outputs/

# Backup database (if applicable)
pg_dump viralai > backup-db-$(date +%Y%m%d).sql
```

### **Scaling Considerations**
- **Horizontal Scaling**: Add more application instances
- **Vertical Scaling**: Increase CPU/memory resources
- **Caching**: Implement Redis cluster for distributed caching
- **Load Balancing**: Use Nginx or cloud load balancers
- **Database**: Consider read replicas for session metadata

## 🎯 **PRODUCTION READY**

Your AI Video Generator is now ready for production deployment with:

- **✅ Enterprise-grade architecture**
- **✅ Comprehensive monitoring and alerting**
- **✅ Scalable deployment options**
- **✅ Security best practices**
- **✅ Performance optimizations**
- **✅ Operational procedures**

The system is production-ready and can handle enterprise-scale video generation workloads with high availability and reliability. 