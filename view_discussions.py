#!/usr/bin/env python3
"""
AI Agent Discussion Viewer
Beautiful visualization of multi-agent discussions
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
import argparse

def get_latest_session() -> Optional[str]:
    """Get the most recent session directory"""
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        return None
    
    session_dirs = []
    for item in os.listdir(outputs_dir):
        if item.startswith("session_") and os.path.isdir(os.path.join(outputs_dir, item)):
            session_path = os.path.join(outputs_dir, item)
            session_dirs.append((session_path, os.path.getctime(session_path)))
    
    if session_dirs:
        session_dirs.sort(key=lambda x: x[1], reverse=True)
        return session_dirs[0][0]
    
    return None

def list_available_sessions() -> List[str]:
    """List all available session directories"""
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        return []
    
    sessions = []
    for item in os.listdir(outputs_dir):
        if item.startswith("session_") and os.path.isdir(os.path.join(outputs_dir, item)):
            session_path = os.path.join(outputs_dir, item)
            sessions.append((session_path, os.path.getctime(session_path)))
    
    sessions.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in sessions]

def load_discussion_summary(session_dir: str) -> Optional[Dict]:
    """Load discussion summary from session"""
    summary_file = os.path.join(session_dir, "agent_discussions_summary.json")
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            return json.load(f)
    return None

def load_individual_discussions(session_dir: str) -> Dict:
    """Load individual discussion files"""
    discussions_dir = os.path.join(session_dir, "agent_discussions")
    discussions = {}
    
    if os.path.exists(discussions_dir):
        for file in os.listdir(discussions_dir):
            if file.startswith("discussion_") and file.endswith(".json"):
                topic = file.replace("discussion_", "").replace(".json", "")
                file_path = os.path.join(discussions_dir, file)
                with open(file_path, 'r') as f:
                    discussions[topic] = json.load(f)
    
    return discussions

def print_header():
    """Print beautiful header"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                          🤖 AI AGENT DISCUSSION VIEWER                              ║
║                         Enhanced Multi-Agent Collaboration                          ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
""")

def print_session_info(session_dir: str, summary: Dict):
    """Print session information"""
    session_name = os.path.basename(session_dir)
    
    print(f"""
📁 Session: {session_name}
📋 Topic: {summary.get('topic', 'Unknown')}
📊 Configuration: {summary.get('discussion_configuration', {}).get('depth', 'Unknown')} mode
⏰ Generated: {summary.get('generation_timestamp', 'Unknown')}
""")

def print_overall_metrics(summary: Dict):
    """Print overall discussion metrics"""
    metrics = summary.get('overall_metrics', {})
    config = summary.get('discussion_configuration', {})
    
    print("╔═══════════════════════════════════════════════════════════════════════════════════╗")
    print("║                                 📊 OVERALL METRICS                               ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"🎯 Total Discussions: {config.get('total_discussions', 0)}")
    print(f"🤝 Average Consensus: {metrics.get('average_consensus', 0):.1%}")
    print(f"🔄 Total Rounds: {metrics.get('total_rounds', 0)}")
    print(f"👥 Unique Agents: {metrics.get('unique_participating_agents', 0)}")
    print()

def print_discussion_details(topic: str, result: Dict, summary: Dict):
    """Print detailed discussion information"""
    discussion_data = summary.get('discussion_results', {}).get(topic, {})
    
    # Get emoji for topic
    topic_emojis = {
        'planning': '📋',
        'script': '📝', 
        'visual': '🎨',
        'audio': '🎵',
        'assembly': '✂️'
    }
    
    emoji = topic_emojis.get(topic, '💬')
    consensus = discussion_data.get('consensus_level', 0)
    rounds = discussion_data.get('total_rounds', 0)
    agents = discussion_data.get('participating_agents', [])
    
    # Status indicator
    status = "✅ SUCCESS" if consensus >= 0.7 else "⚠️ PARTIAL" if consensus >= 0.5 else "❌ FAILED"
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  {emoji} {topic.upper()} DISCUSSION                                                   
╚═══════════════════════════════════════════════════════════════════════════════════╝

🎯 Status: {status}
🤝 Consensus: {consensus:.1%}
🔄 Rounds: {rounds}
👥 Participants: {', '.join(agents)}
""")
    
    # Key insights
    insights = discussion_data.get('key_insights', [])
    if insights:
        print("💡 Key Insights:")
        for i, insight in enumerate(insights[:3], 1):
            # Wrap long insights
            if len(insight) > 80:
                insight = insight[:77] + "..."
            print(f"   {i}. {insight}")
        print()
    
    # Decision summary
    decision = discussion_data.get('final_decision', {})
    if decision and 'final_approach' in decision:
        approach = decision['final_approach']
        if len(approach) > 100:
            approach = approach[:97] + "..."
        print(f"🎯 Final Approach: {approach}")
        print()

def print_key_insights_summary(summary: Dict):
    """Print summary of all key insights"""
    insights = summary.get('key_insights_summary', [])
    
    if insights:
        print("╔═══════════════════════════════════════════════════════════════════════════════════╗")
        print("║                              💡 KEY INSIGHTS SUMMARY                             ║")
        print("╚═══════════════════════════════════════════════════════════════════════════════════╝")
        print()
        
        for i, insight in enumerate(insights[:5], 1):
            # Wrap long insights
            lines = []
            words = insight.split()
            current_line = ""
            
            for word in words:
                if len(current_line + word) > 75:
                    lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    current_line += word + " "
            
            if current_line.strip():
                lines.append(current_line.strip())
            
            print(f"{i}. {lines[0]}")
            for line in lines[1:]:
                print(f"   {line}")
            print()

def view_session_discussions(session_dir: str, detailed: bool = False):
    """View discussions for a specific session"""
    print_header()
    
    # Load summary
    summary = load_discussion_summary(session_dir)
    if not summary:
        print(f"❌ No discussion summary found in {session_dir}")
        return
    
    # Print session info
    print_session_info(session_dir, summary)
    
    # Print overall metrics
    print_overall_metrics(summary)
    
    # Print individual discussions
    discussion_results = summary.get('discussion_results', {})
    
    for topic, result in discussion_results.items():
        print_discussion_details(topic, result, summary)
    
    # Print key insights summary
    print_key_insights_summary(summary)
    
    # Print file locations
    print("╔═══════════════════════════════════════════════════════════════════════════════════╗")
    print("║                                📁 FILE LOCATIONS                                 ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"📄 Summary: {os.path.join(session_dir, 'agent_discussions_summary.json')}")
    print(f"📁 Details: {os.path.join(session_dir, 'agent_discussions/')}")
    
    # Check for visualization files
    viz_dir = os.path.join(session_dir, "agent_discussions")
    if os.path.exists(viz_dir):
        viz_files = [f for f in os.listdir(viz_dir) if f.startswith("visualization_")]
        if viz_files:
            print(f"📊 Visualizations: {len(viz_files)} available")
        
        report_files = [f for f in os.listdir(viz_dir) if f.startswith("report_")]
        if report_files:
            print(f"📋 Reports: {len(report_files)} markdown reports")
    
    print()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="View AI Agent Discussions")
    parser.add_argument("--session", "-s", help="Session directory to view")
    parser.add_argument("--list", "-l", action="store_true", help="List available sessions")
    parser.add_argument("--latest", action="store_true", help="View latest session")
    parser.add_argument("--detailed", "-d", action="store_true", help="Show detailed view")
    
    args = parser.parse_args()
    
    if args.list:
        print_header()
        sessions = list_available_sessions()
        if sessions:
            print("📁 Available Sessions:")
            print()
            for i, session in enumerate(sessions, 1):
                session_name = os.path.basename(session)
                creation_time = datetime.fromtimestamp(os.path.getctime(session))
                
                # Check if it has discussions
                has_discussions = os.path.exists(os.path.join(session, "agent_discussions_summary.json"))
                status = "✅" if has_discussions else "❌"
                
                print(f"{i:2d}. {status} {session_name}")
                print(f"     Created: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"     Path: {session}")
                print()
        else:
            print("❌ No sessions found")
        return
    
    # Determine session to view
    session_dir = None
    
    if args.session:
        if os.path.exists(args.session):
            session_dir = args.session
        else:
            # Try to find session by name
            for session in list_available_sessions():
                if args.session in session:
                    session_dir = session
                    break
    elif args.latest:
        session_dir = get_latest_session()
    else:
        # Default to latest
        session_dir = get_latest_session()
    
    if not session_dir:
        print("❌ No session found. Use --list to see available sessions.")
        return
    
    # View the session
    view_session_discussions(session_dir, args.detailed)

if __name__ == "__main__":
    main() 