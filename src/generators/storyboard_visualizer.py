"""
Storyboard Visualizer - Creates visual storyboard representations
Generates HTML/SVG storyboards for video planning and review
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class StoryboardVisualizer:
    """
    Creates visual storyboard representations for video sessions
    """
    
    def __init__(self, session_dir: Path):
        """Initialize storyboard visualizer"""
        self.session_dir = session_dir
        self.storyboard_dir = session_dir / "storyboard"
        self.storyboard_dir.mkdir(exist_ok=True)
        
        logger.info("🎨 Storyboard Visualizer initialized")
    
    def generate_storyboard(self, video_clips: List[Dict[str, Any]], 
                          script_data: Dict[str, Any], 
                          decisions: Dict[str, Any]) -> str:
        """
        Generate comprehensive storyboard visualization
        
        Args:
            video_clips: List of video clip information
            script_data: Script content and timing
            decisions: Core decisions made for the video
            
        Returns:
            str: Path to generated storyboard HTML file
        """
        logger.info("🎨 Generating storyboard visualization...")
        
        # Create storyboard data structure
        storyboard_data = {
            'metadata': {
                'session_id': str(self.session_dir.name),
                'generated_at': datetime.now().isoformat(),
                'platform': decisions.get('platform', 'unknown'),
                'duration': decisions.get('duration_seconds', 0),
                'style': decisions.get('style', 'unknown')
            },
            'clips': self._process_video_clips(video_clips),
            'script': self._process_script_data(script_data),
            'decisions': decisions
        }
        
        # Generate HTML storyboard
        html_path = self._generate_html_storyboard(storyboard_data)
        
        # Generate JSON data for programmatic access
        json_path = self._save_storyboard_data(storyboard_data)
        
        logger.info(f"✅ Storyboard generated: {html_path}")
        return html_path
    
    def _process_video_clips(self, video_clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process video clip data for storyboard"""
        processed_clips = []
        
        for i, clip in enumerate(video_clips):
            processed_clip = {
                'sequence': i + 1,
                'duration': clip.get('duration', 8.0),
                'start_time': i * 8.0,
                'end_time': (i + 1) * 8.0,
                'description': clip.get('description', f'Scene {i + 1}'),
                'visual_style': clip.get('visual_style', 'dynamic'),
                'key_elements': clip.get('key_elements', []),
                'file_path': clip.get('file_path', ''),
                'thumbnail': self._generate_clip_thumbnail(clip, i)
            }
            processed_clips.append(processed_clip)
        
        return processed_clips
    
    def _process_script_data(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process script data for storyboard"""
        return {
            'segments': script_data.get('segments', []),
            'total_duration': script_data.get('duration', 0),
            'language': script_data.get('language', 'en-US'),
            'word_count': script_data.get('word_count', 0),
            'speaking_rate': script_data.get('speaking_rate', 150)
        }
    
    def _generate_clip_thumbnail(self, clip: Dict[str, Any], index: int) -> str:
        """Generate SVG thumbnail representation for clip"""
        # Create simple SVG thumbnail based on clip content
        svg_content = f'''
        <svg width="120" height="68" viewBox="0 0 120 68" style="border: 2px solid #333; border-radius: 4px;">
            <rect width="120" height="68" fill="#1a1a1a"/>
            <text x="60" y="25" text-anchor="middle" fill="white" font-size="10" font-family="Arial">Scene {index + 1}</text>
            <text x="60" y="40" text-anchor="middle" fill="#888" font-size="8" font-family="Arial">{clip.get('duration', 8.0)}s</text>
            <text x="60" y="55" text-anchor="middle" fill="#666" font-size="7" font-family="Arial">{clip.get('visual_style', 'dynamic')}</text>
        </svg>
        '''
        return svg_content.strip()
    
    def _generate_html_storyboard(self, storyboard_data: Dict[str, Any]) -> str:
        """Generate HTML storyboard visualization"""
        html_template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Storyboard - {storyboard_data['metadata']['session_id']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 20px;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metadata-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        .storyboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        .clip-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }}
        .clip-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .clip-number {{
            background: #ff6b6b;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }}
        .timeline {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin-top: 30px;
        }}
        .timeline-bar {{
            height: 40px;
            background: #333;
            border-radius: 20px;
            position: relative;
            margin: 10px 0;
        }}
        .timeline-segment {{
            position: absolute;
            height: 100%;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Video Storyboard</h1>
            <h2>{storyboard_data['metadata']['session_id']}</h2>
            <p>Generated: {datetime.fromisoformat(storyboard_data['metadata']['generated_at']).strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="metadata">
            <div class="metadata-item">
                <h3>📱 Platform</h3>
                <p>{storyboard_data['metadata']['platform'].upper()}</p>
            </div>
            <div class="metadata-item">
                <h3>⏱️ Duration</h3>
                <p>{storyboard_data['metadata']['duration']} seconds</p>
            </div>
            <div class="metadata-item">
                <h3>🎨 Style</h3>
                <p>{storyboard_data['metadata']['style'].title()}</p>
            </div>
            <div class="metadata-item">
                <h3>🎬 Clips</h3>
                <p>{len(storyboard_data['clips'])} scenes</p>
            </div>
        </div>
        
        <div class="storyboard-grid">
'''

        # Add clip cards
        for clip in storyboard_data['clips']:
            html_template += f'''
            <div class="clip-card">
                <div class="clip-header">
                    <div class="clip-number">{clip['sequence']}</div>
                    <div>
                        <h3>Scene {clip['sequence']}</h3>
                        <p>{clip['start_time']:.1f}s - {clip['end_time']:.1f}s ({clip['duration']:.1f}s)</p>
                    </div>
                </div>
                
                <div class="clip-thumbnail">
                    {clip['thumbnail']}
                </div>
                
                <div class="clip-details">
                    <h4>📝 Description</h4>
                    <p>{clip['description']}</p>
                    
                    <h4>🎨 Visual Style</h4>
                    <p>{clip['visual_style']}</p>
                    
                    {f'<h4>🔑 Key Elements</h4><ul>{"".join([f"<li>{elem}</li>" for elem in clip["key_elements"]])}</ul>' if clip['key_elements'] else ''}
                </div>
            </div>
            '''
        
        # Add timeline visualization
        html_template += f'''
        </div>
        
        <div class="timeline">
            <h2>🕐 Timeline Visualization</h2>
            <div class="timeline-bar">
'''
        
        # Add timeline segments
        total_duration = storyboard_data['metadata']['duration']
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3']
        
        for i, clip in enumerate(storyboard_data['clips']):
            start_percent = (clip['start_time'] / total_duration) * 100
            width_percent = (clip['duration'] / total_duration) * 100
            color = colors[i % len(colors)]
            
            html_template += f'''
                <div class="timeline-segment" style="left: {start_percent}%; width: {width_percent}%; background: {color};">
                    S{clip['sequence']}
                </div>
            '''
        
        html_template += '''
            </div>
            <p style="text-align: center; margin-top: 10px;">Complete Video Timeline</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; opacity: 0.7;">
            <p>🤖 Generated by ViralAI Storyboard System</p>
        </div>
    </div>
</body>
</html>
        '''
        
        # Save HTML file
        html_path = self.storyboard_dir / "storyboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return str(html_path)
    
    def _save_storyboard_data(self, storyboard_data: Dict[str, Any]) -> str:
        """Save storyboard data as JSON"""
        json_path = self.storyboard_dir / "storyboard_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(storyboard_data, f, indent=2, default=str)
        
        return str(json_path)
    
    def generate_scene_breakdown(self, scenes: List[Dict[str, Any]]) -> str:
        """
        Generate detailed scene breakdown markdown
        
        Args:
            scenes: List of scene information
            
        Returns:
            str: Path to generated scene breakdown markdown
        """
        logger.info("📝 Generating scene breakdown...")
        
        markdown_content = f"""# 🎬 Scene Breakdown

**Session**: {self.session_dir.name}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        
        for i, scene in enumerate(scenes, 1):
            markdown_content += f"""## Scene {i}

**Duration**: {scene.get('duration', 8.0)} seconds  
**Timing**: {scene.get('start_time', (i-1)*8):.1f}s - {scene.get('end_time', i*8):.1f}s

### 📝 Description
{scene.get('description', 'No description available')}

### 🎨 Visual Elements
- **Style**: {scene.get('visual_style', 'dynamic')}
- **Key Elements**: {', '.join(scene.get('key_elements', ['Standard elements']))}

### 🎬 Technical Specifications
- **File**: `{scene.get('file_path', 'Not generated')}`
- **Resolution**: {scene.get('resolution', '1080x1920 (9:16)')}
- **Frame Rate**: {scene.get('fps', 30)} FPS

---

"""
        
        # Save markdown file
        md_path = self.storyboard_dir / "scene_breakdown.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"✅ Scene breakdown saved: {md_path}")
        return str(md_path)
    
    def generate_production_notes(self, decisions: Dict[str, Any], 
                                analysis_results: Dict[str, Any]) -> str:
        """
        Generate production notes for the video
        
        Args:
            decisions: Core decisions made
            analysis_results: Analysis results from mission planning
            
        Returns:
            str: Path to production notes file
        """
        logger.info("📋 Generating production notes...")
        
        notes_content = f"""# 📋 Production Notes

**Session**: {self.session_dir.name}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Mission Overview
{decisions.get('mission', 'No mission specified')}

## 📊 Core Decisions
- **Platform**: {decisions.get('platform', 'unknown')}
- **Duration**: {decisions.get('duration_seconds', 0)} seconds
- **Style**: {decisions.get('style', 'unknown')}
- **Tone**: {decisions.get('tone', 'unknown')}
- **Target Audience**: {decisions.get('target_audience', 'unknown')}
- **Language**: {decisions.get('language', 'unknown')}

## 🎬 Technical Specifications
- **Number of Clips**: {decisions.get('num_clips', 0)}
- **Clip Durations**: {decisions.get('clip_durations', [])}
- **Frame Continuity**: {decisions.get('frame_continuity', False)}
- **Visual Style**: {decisions.get('visual_style', 'unknown')}

## 📈 Analysis Results
"""
        
        if analysis_results:
            notes_content += f"""### 🎯 Mission Analysis
- **Type**: {analysis_results.get('mission_type', 'unknown')}
- **Strategic**: {analysis_results.get('is_strategic', False)}
- **Confidence**: {analysis_results.get('confidence', 0):.1%}

### 🔍 Content Credibility
- **Score**: {analysis_results.get('credibility_score', 0):.1f}/10
- **Level**: {analysis_results.get('credibility_level', 'unknown')}

### 🧠 Audience Intelligence
- **Primary Age Group**: {analysis_results.get('primary_age_group', 'unknown')}
- **Engagement Prediction**: {analysis_results.get('engagement_prediction', 0):.1%}

### 🎯 Ethical Assessment
- **Rating**: {analysis_results.get('ethical_rating', 'unknown')}
- **Compliance Score**: {analysis_results.get('ethical_compliance', 0):.1f}/10
"""
        
        notes_content += f"""

## 📁 Output Files
- **Storyboard**: `storyboard/storyboard.html`
- **Scene Breakdown**: `storyboard/scene_breakdown.md`
- **Final Video**: `final_output/final_video_*.mp4`
- **Raw Data**: `storyboard/storyboard_data.json`

---
*Generated by ViralAI Storyboard System*
"""
        
        # Save production notes
        notes_path = self.storyboard_dir / "production_notes.md"
        with open(notes_path, 'w', encoding='utf-8') as f:
            f.write(notes_content)
        
        logger.info(f"✅ Production notes saved: {notes_path}")
        return str(notes_path)
    
    def create_complete_storyboard_package(self, 
                                         video_clips: List[Dict[str, Any]], 
                                         script_data: Dict[str, Any], 
                                         decisions: Dict[str, Any],
                                         analysis_results: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Create complete storyboard package with all visualizations
        
        Args:
            video_clips: Video clip information
            script_data: Script content and timing
            decisions: Core decisions
            analysis_results: Optional analysis results
            
        Returns:
            Dict[str, str]: Paths to all generated files
        """
        logger.info("🎨 Creating complete storyboard package...")
        
        results = {
            'html_storyboard': self.generate_storyboard(video_clips, script_data, decisions),
            'scene_breakdown': self.generate_scene_breakdown(video_clips),
            'production_notes': self.generate_production_notes(decisions, analysis_results or {}),
            'storyboard_data': str(self.storyboard_dir / "storyboard_data.json")
        }
        
        # Create index file
        index_content = f"""# 🎬 Storyboard Package

**Session**: {self.session_dir.name}

## 📁 Files Generated
- [📺 Interactive Storyboard](storyboard.html) - Main visual storyboard
- [📝 Scene Breakdown](scene_breakdown.md) - Detailed scene analysis
- [📋 Production Notes](production_notes.md) - Complete production overview
- [📊 Raw Data](storyboard_data.json) - Machine-readable storyboard data

## 🚀 Quick Access
```bash
# Open storyboard in browser
open {results['html_storyboard']}

# View scene breakdown
cat {results['scene_breakdown']}

# Read production notes
cat {results['production_notes']}
```

---
*🤖 Generated by ViralAI Storyboard System*
"""
        
        index_path = self.storyboard_dir / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        results['index'] = str(index_path)
        
        logger.info(f"✅ Complete storyboard package created: {len(results)} files")
        return results