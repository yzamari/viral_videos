"""
Monitoring and Metrics Microservice
Runs as independent HTTP server on port 8003
Collects metrics from all other services
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import requests
import logging

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and aggregates metrics from all services"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.events = deque(maxlen=10000)
        self.service_health = {}
        self.alerts = deque(maxlen=100)
        
        # Service endpoints to monitor
        self.services = {
            "prompt-optimizer": "http://localhost:8001",
            "video-generator": "http://localhost:8002",
            "script-generator": "http://localhost:8004",
            "orchestrator": "http://localhost:8005"
        }
        
        # Start health check thread
        self.start_health_monitoring()
        
        # Start metrics aggregation
        self.start_metrics_aggregation()
    
    def record_metric(self, service: str, name: str, value: Any, tags: Dict[str, str] = None):
        """Record a metric"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "name": name,
            "value": value,
            "tags": tags or {}
        }
        
        key = f"{service}.{name}"
        self.metrics[key].append(metric)
        
        # Check for alerts
        self._check_alerts(key, value)
        
        # Emit to WebSocket clients
        socketio.emit('metric', metric)
        
        return metric
    
    def record_event(self, service: str, event_type: str, data: Dict[str, Any]):
        """Record an event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "type": event_type,
            "data": data
        }
        
        self.events.append(event)
        
        # Emit to WebSocket clients
        socketio.emit('event', event)
        
        return event
    
    def get_metrics(self, service: str = None, name: str = None, 
                   last_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics with filtering"""
        cutoff_time = datetime.now() - timedelta(minutes=last_minutes)
        result = []
        
        for key, metrics_list in self.metrics.items():
            if service and not key.startswith(service):
                continue
            if name and name not in key:
                continue
            
            for metric in metrics_list:
                metric_time = datetime.fromisoformat(metric["timestamp"])
                if metric_time >= cutoff_time:
                    result.append(metric)
        
        return result
    
    def get_aggregated_metrics(self, service: str = None) -> Dict[str, Any]:
        """Get aggregated metrics summary"""
        summary = {}
        
        for key, metrics_list in self.metrics.items():
            if service and not key.startswith(service):
                continue
            
            if metrics_list:
                values = [m["value"] for m in metrics_list if isinstance(m["value"], (int, float))]
                if values:
                    summary[key] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "latest": metrics_list[-1]["value"],
                        "latest_timestamp": metrics_list[-1]["timestamp"]
                    }
        
        return summary
    
    def start_health_monitoring(self):
        """Start background health monitoring"""
        def monitor_health():
            while True:
                for service_name, service_url in self.services.items():
                    try:
                        response = requests.get(f"{service_url}/health", timeout=2)
                        if response.status_code == 200:
                            self.service_health[service_name] = {
                                "status": "healthy",
                                "last_check": datetime.now().isoformat(),
                                "details": response.json()
                            }
                        else:
                            self.service_health[service_name] = {
                                "status": "unhealthy",
                                "last_check": datetime.now().isoformat(),
                                "error": f"Status code: {response.status_code}"
                            }
                    except Exception as e:
                        self.service_health[service_name] = {
                            "status": "down",
                            "last_check": datetime.now().isoformat(),
                            "error": str(e)
                        }
                
                # Emit health status
                socketio.emit('health_update', self.service_health)
                time.sleep(10)  # Check every 10 seconds
        
        thread = threading.Thread(target=monitor_health, daemon=True)
        thread.start()
    
    def start_metrics_aggregation(self):
        """Start collecting metrics from services"""
        def collect_metrics():
            while True:
                for service_name, service_url in self.services.items():
                    try:
                        response = requests.get(f"{service_url}/stats", timeout=2)
                        if response.status_code == 200:
                            stats = response.json()
                            for key, value in stats.items():
                                if isinstance(value, (int, float)):
                                    self.record_metric(service_name, key, value)
                    except:
                        pass  # Service might be down
                
                time.sleep(30)  # Collect every 30 seconds
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
    
    def _check_alerts(self, metric_key: str, value: Any):
        """Check if metric triggers any alerts"""
        # Alert rules
        alert_rules = {
            "video-generator.failure_count": {"threshold": 5, "operator": ">"},
            "prompt-optimizer.success_rate": {"threshold": 0.5, "operator": "<"},
            "orchestrator.processing_time": {"threshold": 30000, "operator": ">"}
        }
        
        if metric_key in alert_rules:
            rule = alert_rules[metric_key]
            triggered = False
            
            if rule["operator"] == ">" and value > rule["threshold"]:
                triggered = True
            elif rule["operator"] == "<" and value < rule["threshold"]:
                triggered = True
            
            if triggered:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "metric": metric_key,
                    "value": value,
                    "threshold": rule["threshold"],
                    "message": f"Alert: {metric_key} = {value} (threshold: {rule['threshold']})"
                }
                self.alerts.append(alert)
                socketio.emit('alert', alert)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "services": self.service_health,
            "metrics_summary": self.get_aggregated_metrics(),
            "recent_events": list(self.events)[-20:],
            "recent_alerts": list(self.alerts)[-10:],
            "system_status": self._calculate_system_status()
        }
    
    def _calculate_system_status(self) -> str:
        """Calculate overall system status"""
        healthy_count = sum(1 for s in self.service_health.values() 
                          if s.get("status") == "healthy")
        total_count = len(self.service_health)
        
        if healthy_count == total_count:
            return "operational"
        elif healthy_count >= total_count * 0.5:
            return "degraded"
        else:
            return "critical"


# Initialize collector
collector = MetricsCollector()


# ============= HTTP API Endpoints =============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "monitoring",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/metrics', methods=['POST'])
def record_metric():
    """Record a metric"""
    try:
        data = request.json
        metric = collector.record_metric(
            service=data.get('service', 'unknown'),
            name=data.get('name'),
            value=data.get('value'),
            tags=data.get('tags')
        )
        return jsonify(metric)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/events', methods=['POST'])
def record_event():
    """Record an event"""
    try:
        data = request.json
        event = collector.record_event(
            service=data.get('service', 'unknown'),
            event_type=data.get('type'),
            data=data.get('data', {})
        )
        return jsonify(event)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get metrics with optional filtering"""
    service = request.args.get('service')
    name = request.args.get('name')
    last_minutes = int(request.args.get('last_minutes', 60))
    
    metrics = collector.get_metrics(service, name, last_minutes)
    return jsonify(metrics)


@app.route('/metrics/summary', methods=['GET'])
def get_metrics_summary():
    """Get aggregated metrics summary"""
    service = request.args.get('service')
    summary = collector.get_aggregated_metrics(service)
    return jsonify(summary)


@app.route('/services/health', methods=['GET'])
def get_service_health():
    """Get health status of all services"""
    return jsonify(collector.service_health)


@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get complete dashboard data"""
    return jsonify(collector.get_dashboard_data())


@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Get recent alerts"""
    return jsonify(list(collector.alerts))


@app.route('/events', methods=['GET'])
def get_events():
    """Get recent events"""
    limit = int(request.args.get('limit', 100))
    return jsonify(list(collector.events)[-limit:])


# ============= WebSocket Events =============

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected")
    emit('connected', {'message': 'Connected to monitoring service'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to specific metrics"""
    # Implement subscription logic if needed
    emit('subscribed', {'message': f'Subscribed to {data}'})


# ============= HTML Dashboard =============

@app.route('/')
def dashboard_page():
    """Serve monitoring dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ViralAI Monitoring Dashboard</title>
        <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
            .container { max-width: 1400px; margin: auto; }
            .service-card { 
                background: white; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 10px;
                display: inline-block;
                width: 300px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .healthy { border-left: 4px solid #4CAF50; }
            .unhealthy { border-left: 4px solid #f44336; }
            .down { border-left: 4px solid #9E9E9E; }
            .metric { margin: 5px 0; }
            h1 { color: #333; }
            .alert { 
                background: #fff3cd; 
                border-left: 4px solid #ffc107; 
                padding: 10px;
                margin: 10px 0;
            }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ViralAI Microservices Monitor</h1>
            <div id="services"></div>
            <h2>📊 Metrics</h2>
            <div id="metrics" class="metrics-grid"></div>
            <h2>⚠️ Alerts</h2>
            <div id="alerts"></div>
        </div>
        
        <script>
            const socket = io();
            
            socket.on('connect', function() {
                console.log('Connected to monitoring service');
            });
            
            socket.on('health_update', function(data) {
                updateServices(data);
            });
            
            socket.on('metric', function(data) {
                console.log('New metric:', data);
            });
            
            socket.on('alert', function(data) {
                addAlert(data);
            });
            
            function updateServices(health) {
                const container = document.getElementById('services');
                container.innerHTML = '';
                
                for (const [service, status] of Object.entries(health)) {
                    const card = document.createElement('div');
                    card.className = `service-card ${status.status}`;
                    card.innerHTML = `
                        <h3>${service}</h3>
                        <div>Status: ${status.status}</div>
                        <div>Last Check: ${new Date(status.last_check).toLocaleTimeString()}</div>
                    `;
                    container.appendChild(card);
                }
            }
            
            function addAlert(alert) {
                const container = document.getElementById('alerts');
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert';
                alertDiv.innerHTML = `${alert.message} (${new Date(alert.timestamp).toLocaleTimeString()})`;
                container.insertBefore(alertDiv, container.firstChild);
            }
            
            // Load initial data
            fetch('/dashboard')
                .then(r => r.json())
                .then(data => {
                    updateServices(data.services);
                    if (data.recent_alerts) {
                        data.recent_alerts.forEach(addAlert);
                    }
                });
        </script>
    </body>
    </html>
    """


if __name__ == '__main__':
    logger.info("📊 Starting Monitoring Service on port 8003")
    socketio.run(app, host='0.0.0.0', port=8003, debug=False)