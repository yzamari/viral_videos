#!/bin/bash

# 🚀 AI Video Generator - Production Deployment Script
# Comprehensive automated deployment for enterprise-grade system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_USER="viralai"
APP_DIR="/home/${DEPLOY_USER}/viral_videos"
SERVICE_NAME="viralai"
GUI_SERVICE_NAME="viralai-gui"
BACKUP_DIR="/home/${DEPLOY_USER}/backups"
LOG_FILE="/var/log/viralai_deploy.log"

# Functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log "INFO: $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log "ERROR: $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot determine OS version"
        exit 1
    fi
    
    # Check Python version
    if ! command -v python3.11 &> /dev/null; then
        print_warning "Python 3.11 not found, installing..."
        apt update
        apt install -y python3.11 python3.11-venv python3.11-dev
    fi
    
    # Check required packages
    local packages=("git" "curl" "wget" "build-essential" "ffmpeg" "nginx")
    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            print_warning "$package not installed, installing..."
            apt install -y "$package"
        fi
    done
    
    print_success "Prerequisites check completed"
}

create_user() {
    print_status "Creating deployment user..."
    
    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$DEPLOY_USER"
        usermod -aG sudo "$DEPLOY_USER"
        print_success "Created user: $DEPLOY_USER"
    else
        print_status "User $DEPLOY_USER already exists"
    fi
}

backup_existing() {
    print_status "Creating backup of existing installation..."
    
    if [[ -d "$APP_DIR" ]]; then
        local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
        local backup_path="$BACKUP_DIR/$backup_name"
        
        mkdir -p "$BACKUP_DIR"
        cp -r "$APP_DIR" "$backup_path"
        print_success "Backup created: $backup_path"
    else
        print_status "No existing installation to backup"
    fi
}

deploy_application() {
    print_status "Deploying application..."
    
    # Switch to deploy user
    sudo -u "$DEPLOY_USER" bash << 'EOF'
set -e

DEPLOY_USER="viralai"
APP_DIR="/home/${DEPLOY_USER}/viral_videos"

# Create app directory
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Clone or update repository
if [[ -d ".git" ]]; then
    echo "Updating existing repository..."
    git fetch origin
    git checkout comprehensive-refactoring
    git pull origin comprehensive-refactoring
else
    echo "Cloning repository..."
    git clone https://github.com/yzamari/viral_videos.git .
    git checkout comprehensive-refactoring
fi

# Create virtual environment
if [[ ! -d "venv" ]]; then
    python3.11 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install production dependencies
pip install gunicorn supervisor psutil

# Create necessary directories
mkdir -p outputs logs cache config

# Set permissions
chmod 750 "$APP_DIR"
chmod 755 "$APP_DIR/outputs"
chmod 755 "$APP_DIR/logs"
chmod 755 "$APP_DIR/cache"

EOF

    print_success "Application deployed successfully"
}

configure_environment() {
    print_status "Configuring environment..."
    
    # Create configuration file if it doesn't exist
    if [[ ! -f "$APP_DIR/config.env" ]]; then
        sudo -u "$DEPLOY_USER" cp "$APP_DIR/config.env.example" "$APP_DIR/config.env"
        print_warning "Created config.env from template - please update with your API keys"
    fi
    
    # Set secure permissions on config file
    chmod 640 "$APP_DIR/config.env"
    chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR/config.env"
    
    print_success "Environment configured"
}

create_systemd_services() {
    print_status "Creating systemd services..."
    
    # Main service
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=AI Video Generator Service
After=network.target

[Service]
Type=simple
User=$DEPLOY_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python main.py --mode production
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=60
TimeoutStopSec=30

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR/outputs $APP_DIR/logs $APP_DIR/cache

[Install]
WantedBy=multi-user.target
EOF

    # GUI service
    cat > "/etc/systemd/system/${GUI_SERVICE_NAME}.service" << EOF
[Unit]
Description=AI Video Generator GUI Service
After=network.target

[Service]
Type=simple
User=$DEPLOY_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python modern_ui.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=60
TimeoutStopSec=30

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR/outputs $APP_DIR/logs $APP_DIR/cache

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload
    
    print_success "Systemd services created"
}

configure_nginx() {
    print_status "Configuring Nginx..."
    
    # Create Nginx configuration
    cat > "/etc/nginx/sites-available/viralai" << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Main application
    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Large file uploads
        client_max_body_size 100M;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:7860/health;
        access_log off;
    }
    
    # Static files (if any)
    location /static/ {
        alias /home/viralai/viral_videos/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(env|ini|conf)$ {
        deny all;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/viralai /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    print_success "Nginx configured"
}

configure_logging() {
    print_status "Configuring logging..."
    
    # Create log rotation configuration
    cat > "/etc/logrotate.d/viralai" << EOF
$APP_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $DEPLOY_USER $DEPLOY_USER
    postrotate
        systemctl reload $SERVICE_NAME
        systemctl reload $GUI_SERVICE_NAME
    endscript
}
EOF

    # Create rsyslog configuration for application logs
    cat > "/etc/rsyslog.d/50-viralai.conf" << 'EOF'
# AI Video Generator logs
:programname, isequal, "viralai" /var/log/viralai/application.log
:programname, isequal, "viralai-gui" /var/log/viralai/gui.log
& stop
EOF

    # Create log directory
    mkdir -p /var/log/viralai
    chown syslog:adm /var/log/viralai
    
    # Restart rsyslog
    systemctl restart rsyslog
    
    print_success "Logging configured"
}

setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create monitoring script
    cat > "/usr/local/bin/viralai-monitor" << 'EOF'
#!/bin/bash

# Simple monitoring script for AI Video Generator
LOG_FILE="/var/log/viralai/monitor.log"
ALERT_EMAIL="admin@example.com"

check_service() {
    local service=$1
    if ! systemctl is-active --quiet "$service"; then
        echo "$(date): Service $service is not running" >> "$LOG_FILE"
        # Attempt to restart
        systemctl restart "$service"
        if systemctl is-active --quiet "$service"; then
            echo "$(date): Service $service restarted successfully" >> "$LOG_FILE"
        else
            echo "$(date): Failed to restart service $service" >> "$LOG_FILE"
        fi
    fi
}

check_disk_space() {
    local usage=$(df /home/viralai/viral_videos/outputs | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$usage" -gt 90 ]; then
        echo "$(date): Disk space usage is $usage%" >> "$LOG_FILE"
    fi
}

# Check services
check_service "viralai"
check_service "viralai-gui"
check_service "nginx"

# Check disk space
check_disk_space

# Check application health
if ! curl -f http://localhost:7860/health > /dev/null 2>&1; then
    echo "$(date): Application health check failed" >> "$LOG_FILE"
fi
EOF

    chmod +x /usr/local/bin/viralai-monitor
    
    # Create cron job for monitoring
    cat > "/etc/cron.d/viralai-monitor" << 'EOF'
# AI Video Generator monitoring
*/5 * * * * root /usr/local/bin/viralai-monitor
EOF

    print_success "Monitoring configured"
}

run_tests() {
    print_status "Running deployment tests..."
    
    sudo -u "$DEPLOY_USER" bash << 'EOF'
set -e

APP_DIR="/home/viralai/viral_videos"
cd "$APP_DIR"
source venv/bin/activate

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit/ -v --tb=short

# Run session management tests
echo "Running session management tests..."
python -c "
import sys
sys.path.append('src')
from utils.session_manager import session_manager
from utils.session_context import create_session_context
session_id = session_manager.create_session('Test', 'tiktok', 15, 'Educational')
context = create_session_context(session_id)
print(f'✅ Session test passed: {context.session_id}')
session_manager.cleanup_session(session_id)
"

echo "✅ All tests passed"
EOF

    print_success "Tests completed successfully"
}

start_services() {
    print_status "Starting services..."
    
    # Enable and start services
    systemctl enable "$SERVICE_NAME"
    systemctl enable "$GUI_SERVICE_NAME"
    systemctl enable nginx
    
    systemctl start "$SERVICE_NAME"
    systemctl start "$GUI_SERVICE_NAME"
    systemctl restart nginx
    
    # Wait for services to start
    sleep 10
    
    # Check service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Main service started successfully"
    else
        print_error "Failed to start main service"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
    
    if systemctl is-active --quiet "$GUI_SERVICE_NAME"; then
        print_success "GUI service started successfully"
    else
        print_error "Failed to start GUI service"
        systemctl status "$GUI_SERVICE_NAME"
        exit 1
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "Nginx started successfully"
    else
        print_error "Failed to start Nginx"
        systemctl status nginx
        exit 1
    fi
}

health_check() {
    print_status "Performing health checks..."
    
    # Check if GUI is accessible
    local max_attempts=12
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:7860/health > /dev/null 2>&1; then
            print_success "Application is healthy and responding"
            break
        else
            print_status "Waiting for application to start... (attempt $attempt/$max_attempts)"
            sleep 5
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Application failed to start properly"
        exit 1
    fi
    
    # Check Nginx
    if curl -f http://localhost/ > /dev/null 2>&1; then
        print_success "Nginx is serving requests"
    else
        print_error "Nginx is not responding"
        exit 1
    fi
}

show_deployment_info() {
    print_success "Deployment completed successfully!"
    echo
    echo "=================================================="
    echo "🚀 AI Video Generator - Production Deployment"
    echo "=================================================="
    echo
    echo "📋 Deployment Information:"
    echo "  • Application Directory: $APP_DIR"
    echo "  • User: $DEPLOY_USER"
    echo "  • Services: $SERVICE_NAME, $GUI_SERVICE_NAME"
    echo "  • Web Interface: http://localhost/"
    echo "  • Direct Access: http://localhost:7860/"
    echo
    echo "📊 Service Status:"
    systemctl is-active "$SERVICE_NAME" && echo "  • Main Service: ✅ Running" || echo "  • Main Service: ❌ Stopped"
    systemctl is-active "$GUI_SERVICE_NAME" && echo "  • GUI Service: ✅ Running" || echo "  • GUI Service: ❌ Stopped"
    systemctl is-active nginx && echo "  • Nginx: ✅ Running" || echo "  • Nginx: ❌ Stopped"
    echo
    echo "🔧 Management Commands:"
    echo "  • View logs: journalctl -u $SERVICE_NAME -f"
    echo "  • Restart service: systemctl restart $SERVICE_NAME"
    echo "  • Check status: systemctl status $SERVICE_NAME"
    echo "  • Monitor: tail -f /var/log/viralai/monitor.log"
    echo
    echo "⚠️  Next Steps:"
    echo "  1. Update config.env with your API keys"
    echo "  2. Configure SSL certificate (recommended)"
    echo "  3. Set up domain name and DNS"
    echo "  4. Configure firewall rules"
    echo "  5. Set up backup strategy"
    echo
    echo "=================================================="
}

# Main deployment process
main() {
    print_status "Starting AI Video Generator production deployment..."
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # Run deployment steps
    check_root
    check_prerequisites
    create_user
    backup_existing
    deploy_application
    configure_environment
    create_systemd_services
    configure_nginx
    configure_logging
    setup_monitoring
    run_tests
    start_services
    health_check
    show_deployment_info
    
    print_success "Deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "AI Video Generator Production Deployment Script"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --dry-run      Show what would be done without executing"
        echo "  --update       Update existing installation"
        echo
        exit 0
        ;;
    --dry-run)
        echo "DRY RUN MODE - Would perform the following steps:"
        echo "1. Check prerequisites"
        echo "2. Create deployment user"
        echo "3. Backup existing installation"
        echo "4. Deploy application"
        echo "5. Configure environment"
        echo "6. Create systemd services"
        echo "7. Configure Nginx"
        echo "8. Configure logging"
        echo "9. Setup monitoring"
        echo "10. Run tests"
        echo "11. Start services"
        echo "12. Perform health checks"
        exit 0
        ;;
    --update)
        print_status "Updating existing installation..."
        backup_existing
        deploy_application
        systemctl restart "$SERVICE_NAME"
        systemctl restart "$GUI_SERVICE_NAME"
        health_check
        print_success "Update completed successfully!"
        exit 0
        ;;
    *)
        main
        ;;
esac 