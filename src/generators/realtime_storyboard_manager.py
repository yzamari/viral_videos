"""
Real-time Storyboard Manager
Updates storyboard HTML during scene planning and decision-making process
Provides live preview of video planning as decisions are made
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from ..utils.logging_config import get_logger
from .storyboard_visualizer import StoryboardVisualizer

logger = get_logger(__name__)


class RealtimeStoryboardManager:
    """
    Manages real-time storyboard updates during video planning
    Creates and updates HTML storyboard as decisions are made
    """
    
    def __init__(self, session_dir: Path):
        """Initialize real-time storyboard manager"""
        self.session_dir = session_dir
        self.storyboard_dir = session_dir / "storyboard"
        self.storyboard_dir.mkdir(exist_ok=True)
        
        # Initialize the main storyboard visualizer
        self.visualizer = StoryboardVisualizer(session_dir)
        
        # Track storyboard state
        self.current_state = {
            'metadata': {
                'session_id': str(session_dir.name),
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'status': 'planning',
                'platform': 'unknown',
                'duration': 0,
                'style': 'unknown',
                'stage': 'initialization'
            },
            'planning_stages': [],
            'scenes': [],
            'decisions': {},
            'prompts': []
        }
        
        # Create initial storyboard
        self._create_initial_storyboard()
        
        logger.info("🎬 Real-time Storyboard Manager initialized")
        logger.info(f"📍 Storyboard URL: {self.get_storyboard_url()}")
    
    def get_storyboard_url(self) -> str:
        """Get the file:// URL to the storyboard HTML"""
        html_path = self.storyboard_dir / "realtime_storyboard.html"
        return f"file://{html_path.absolute()}"
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update storyboard metadata and refresh HTML"""
        self.current_state['metadata'].update(metadata)
        self.current_state['metadata']['last_updated'] = datetime.now().isoformat()
        self._update_storyboard_html()
        logger.info(f"🔄 Updated storyboard metadata: {list(metadata.keys())}")
    
    def add_planning_stage(self, stage_name: str, description: str, data: Dict[str, Any] = None) -> None:
        """Add a new planning stage to the storyboard"""
        stage = {
            'name': stage_name,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'data': data or {}
        }
        
        self.current_state['planning_stages'].append(stage)
        self.current_state['metadata']['stage'] = stage_name
        self.current_state['metadata']['last_updated'] = datetime.now().isoformat()
        
        self._update_storyboard_html()
        logger.info(f"📝 Added planning stage: {stage_name}")
    
    def update_scenes(self, scenes: List[Dict[str, Any]]) -> None:
        """Update the scene list and refresh storyboard"""
        self.current_state['scenes'] = scenes
        self.current_state['metadata']['last_updated'] = datetime.now().isoformat()
        self.current_state['metadata']['scene_count'] = len(scenes)
        
        self._update_storyboard_html()
        logger.info(f"🎬 Updated scenes: {len(scenes)} scenes")
    
    def add_decision(self, decision_type: str, decision_value: Any, reasoning: str = None) -> None:
        """Add a core decision to the storyboard"""
        decision = {
            'value': decision_value,
            'reasoning': reasoning,
            'timestamp': datetime.now().isoformat()
        }
        
        self.current_state['decisions'][decision_type] = decision
        self.current_state['metadata']['last_updated'] = datetime.now().isoformat()
        
        self._update_storyboard_html()
        logger.info(f"🎯 Added decision: {decision_type} = {decision_value}")
    
    def add_prompt(self, clip_number: int, prompt_text: str, scene_type: str = None) -> None:
        """Add a video generation prompt to the storyboard"""
        prompt = {
            'clip_number': clip_number,
            'prompt': prompt_text,
            'scene_type': scene_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self.current_state['prompts'].append(prompt)
        self.current_state['metadata']['last_updated'] = datetime.now().isoformat()
        
        self._update_storyboard_html()
        logger.info(f"📝 Added prompt for clip {clip_number}")
    
    def set_status(self, status: str) -> None:
        """Update the overall storyboard status"""
        self.current_state['metadata']['status'] = status
        self.current_state['metadata']['last_updated'] = datetime.now().isoformat()
        
        self._update_storyboard_html()
        logger.info(f"📊 Status updated: {status}")
    
    def _create_initial_storyboard(self) -> None:
        """Create the initial storyboard HTML"""
        self._update_storyboard_html()
    
    def _update_storyboard_html(self) -> None:
        """Update the storyboard HTML file"""
        try:
            html_content = self._generate_realtime_html()
            html_path = self.storyboard_dir / "realtime_storyboard.html"
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Also save JSON data for debugging
            json_path = self.storyboard_dir / "realtime_data.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_state, f, indent=2, default=str)
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to update storyboard HTML: {e}")
    
    def _generate_realtime_html(self) -> str:
        """Generate HTML for real-time storyboard"""
        metadata = self.current_state['metadata']
        
        # Auto-refresh every 2 seconds during planning
        refresh_meta = '<meta http-equiv="refresh" content="2">' if metadata['status'] == 'planning' else ''
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 Real-time Storyboard - {metadata['session_id']}</title>
    {refresh_meta}
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(45deg, #ff6b6b, #ffd93d);
            padding: 30px;
            text-align: center;
            color: white;
        }}
        .status-bar {{
            background: #2c3e50;
            color: white;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .status-badge {{
            background: #27ae60;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .planning-badge {{
            background: #f39c12;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
            padding-left: 20px;
        }}
        .section h2 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .planning-stages {{
            display: grid;
            gap: 15px;
        }}
        .stage {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #3498db;
        }}
        .stage.active {{
            border-left-color: #27ae60;
            background: #e8f5e8;
        }}
        .scenes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .scene-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .scene-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .scene-type {{
            background: #3498db;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            text-transform: uppercase;
        }}
        .decisions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .decision {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
        }}
        .decision-key {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .decision-value {{
            margin-top: 5px;
            color: #27ae60;
            font-weight: 500;
        }}
        .prompts-list {{
            display: grid;
            gap: 15px;
        }}
        .prompt-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #9b59b6;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 10px;
        }}
        .live-indicator {{
            color: #27ae60;
            font-size: 12px;
        }}
        .live-indicator::before {{
            content: "●";
            color: #27ae60;
            animation: blink 1s infinite;
        }}
        @keyframes blink {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Real-time Storyboard</h1>
            <h2>{metadata['session_id']}</h2>
            <p>Live Video Planning Preview</p>
        </div>
        
        <div class="status-bar">
            <div>
                <span class="status-badge {'planning-badge' if metadata['status'] == 'planning' else ''}">{metadata['status']}</span>
                <span style="margin-left: 15px;">Stage: {metadata.get('stage', 'Unknown')}</span>
            </div>
            <div>
                <span class="live-indicator">LIVE</span>
                <span style="margin-left: 10px;">Last updated: {datetime.fromisoformat(metadata['last_updated']).strftime('%H:%M:%S')}</span>
            </div>
        </div>
        
        <div class="content">
"""
        
        # Planning Stages Section
        if self.current_state['planning_stages']:
            html += """
            <div class="section">
                <h2>📝 Planning Progress</h2>
                <div class="planning-stages">
            """
            
            current_stage = metadata.get('stage', '')
            for stage in self.current_state['planning_stages']:
                active_class = 'active' if stage['name'] == current_stage else ''
                html += f"""
                    <div class="stage {active_class}">
                        <strong>{stage['name']}</strong>
                        <p>{stage['description']}</p>
                        <div class="timestamp">⏰ {datetime.fromisoformat(stage['timestamp']).strftime('%H:%M:%S')}</div>
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        # Core Decisions Section
        if self.current_state['decisions']:
            html += """
            <div class="section">
                <h2>🎯 Core Decisions</h2>
                <div class="decisions-grid">
            """
            
            for decision_type, decision_data in self.current_state['decisions'].items():
                reasoning = f"<p><em>{decision_data.get('reasoning', '')}</em></p>" if decision_data.get('reasoning') else ''
                html += f"""
                    <div class="decision">
                        <div class="decision-key">{decision_type.replace('_', ' ').title()}</div>
                        <div class="decision-value">{decision_data['value']}</div>
                        {reasoning}
                        <div class="timestamp">⏰ {datetime.fromisoformat(decision_data['timestamp']).strftime('%H:%M:%S')}</div>
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        # Scenes Section
        if self.current_state['scenes']:
            html += """
            <div class="section">
                <h2>🎬 Scene Breakdown</h2>
                <div class="scenes-grid">
            """
            
            for i, scene in enumerate(self.current_state['scenes'], 1):
                duration = scene.get('duration', 'Unknown')
                scene_type = scene.get('type', 'Unknown')
                description = scene.get('description', 'No description available')
                
                html += f"""
                    <div class="scene-card">
                        <div class="scene-header">
                            <h3>Scene {i}</h3>
                            <span class="scene-type">{scene_type}</span>
                        </div>
                        <p><strong>Duration:</strong> {duration}s</p>
                        <p>{description}</p>
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        # Prompts Section
        if self.current_state['prompts']:
            html += """
            <div class="section">
                <h2>📝 Generation Prompts</h2>
                <div class="prompts-list">
            """
            
            for prompt_data in self.current_state['prompts']:
                scene_type_badge = f"<span class='scene-type'>{prompt_data.get('scene_type', 'General')}</span>" if prompt_data.get('scene_type') else ''
                html += f"""
                    <div class="prompt-card">
                        <div class="scene-header">
                            <h4>Clip {prompt_data['clip_number']}</h4>
                            {scene_type_badge}
                        </div>
                        <p>{prompt_data['prompt']}</p>
                        <div class="timestamp">⏰ {datetime.fromisoformat(prompt_data['timestamp']).strftime('%H:%M:%S')}</div>
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        # If no content yet, show waiting message
        if not any([self.current_state['planning_stages'], self.current_state['decisions'], 
                   self.current_state['scenes'], self.current_state['prompts']]):
            html += """
            <div class="section">
                <h2>⏳ Waiting for Planning to Begin...</h2>
                <p>The storyboard will update automatically as decisions are made and scenes are planned.</p>
            </div>
            """
        
        html += f"""
        </div>
        
        <div style="background: #2c3e50; color: white; text-align: center; padding: 20px;">
            <p>🤖 Generated by ViralAI Real-time Storyboard System</p>
            <p class="live-indicator">This page auto-refreshes during planning</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html