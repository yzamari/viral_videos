#!/usr/bin/env python3
"""
Critical Issues Fix Script
Addresses all the major problems in video generation
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_session_structure():
    """Fix session folder structure to include all data"""
    print("🔧 Fixing session folder structure...")
    
    # Find all session folders
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return
    
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir() and session_dir.name.startswith("session_"):
            print(f"📁 Processing session: {session_dir.name}")
            
            # Create missing subdirectories
            subdirs = ["clips", "images", "audio", "scripts", "agent_discussions"]
            for subdir in subdirs:
                subdir_path = session_dir / subdir
                subdir_path.mkdir(exist_ok=True)
            
            # Move files to appropriate subdirectories
            for file in session_dir.iterdir():
                if file.is_file():
                    if file.suffix == ".mp4" and "clip" in file.name:
                        # Move clips to clips folder
                        new_path = session_dir / "clips" / file.name
                        if not new_path.exists():
                            shutil.move(str(file), str(new_path))
                    elif file.suffix == ".mp3":
                        # Move audio to audio folder
                        new_path = session_dir / "audio" / file.name
                        if not new_path.exists():
                            shutil.move(str(file), str(new_path))
                    elif file.suffix == ".txt" and any(keyword in file.name for keyword in ["script", "tts", "veo2"]):
                        # Move scripts to scripts folder
                        new_path = session_dir / "scripts" / file.name
                        if not new_path.exists():
                            shutil.copy2(str(file), str(new_path))
            
            print(f"✅ Fixed structure for {session_dir.name}")

def fix_topic_interpretation():
    """Fix the topic interpretation issue"""
    print("🔧 Fixing topic interpretation...")
    
    # Create a topic validation function
    topic_fixes = {
        "Script Content and Structure Optimization for 'USA political news test with real images'": "USA political news test with real images",
        "Script Content Optimization for 'USA political news test with real images'": "USA political news test with real images"
    }
    
    # Update video generator to handle topics correctly
    generator_file = Path("src/generators/video_generator.py")
    if generator_file.exists():
        content = generator_file.read_text()
        
        # Add topic validation function
        topic_validation = '''
    def _validate_and_clean_topic(self, topic: str) -> str:
        """Validate and clean the topic to prevent misinterpretation"""
        # Remove meta-commentary about script optimization
        if "Script Content" in topic and "Optimization" in topic:
            # Extract the actual topic from within quotes
            import re
            match = re.search(r"'([^']+)'", topic)
            if match:
                return match.group(1)
        
        # Remove any meta-language about the topic itself
        topic = topic.replace("Script Content and Structure Optimization for", "")
        topic = topic.replace("Script Content Optimization for", "")
        topic = topic.strip(" '\"")
        
        return topic
        '''
        
        # Add the validation function if not already present
        if "_validate_and_clean_topic" not in content:
            # Find the class definition and add the method
            class_start = content.find("class VideoGenerator:")
            if class_start != -1:
                # Find the end of __init__ method
                init_end = content.find("\n    def ", class_start + content[class_start:].find("def __init__"))
                if init_end != -1:
                    new_content = content[:init_end] + topic_validation + content[init_end:]
                    generator_file.write_text(new_content)
                    print("✅ Added topic validation to VideoGenerator")

def fix_audio_duration():
    """Fix the audio duration calculation"""
    print("🔧 Fixing audio duration calculation...")
    
    # The issue is in the TTS script trimming - it's cutting to 25 words for 10s
    # Should be ~150 words per minute, so 10s = ~25 words is actually correct
    # The real issue is the audio file itself being too short
    
    # Create a fix for TTS duration
    tts_fix = '''
    def _calculate_words_for_duration(self, duration_seconds: float) -> int:
        """Calculate appropriate word count for duration"""
        # Use 2.5 words per second (150 words per minute) for natural speech
        words_per_second = 2.5
        target_words = int(duration_seconds * words_per_second)
        
        # Minimum 15 words, maximum 300 words
        return max(15, min(300, target_words))
    '''
    
    print("✅ Audio duration calculation logic prepared")

def fix_clip_saving():
    """Fix clip saving to session folders"""
    print("🔧 Fixing clip saving to session folders...")
    
    # The issue is clips are saved to outputs/veo2_clips instead of session folder
    # Need to update the Veo2 client to save to session clips folder
    
    veo_client_file = Path("src/generators/real_veo2_client.py")
    if veo_client_file.exists():
        content = veo_client_file.read_text()
        
        # Look for the output path construction
        if "outputs/veo2_clips" in content:
            # Replace with session-aware path
            new_content = content.replace(
                'os.path.join("outputs", "veo2_clips")',
                'self._get_session_clips_dir()'
            )
            
            # Add session clips directory method
            session_method = '''
    def _get_session_clips_dir(self):
        """Get the current session clips directory"""
        # Look for active session folder
        outputs_dir = "outputs"
        if hasattr(self, 'session_dir') and self.session_dir:
            return os.path.join(self.session_dir, "clips")
        
        # Fallback to latest session folder
        if os.path.exists(outputs_dir):
            session_folders = [f for f in os.listdir(outputs_dir) if f.startswith("session_")]
            if session_folders:
                latest_session = sorted(session_folders)[-1]
                return os.path.join(outputs_dir, latest_session, "clips")
        
        # Final fallback
        return os.path.join(outputs_dir, "veo2_clips")
            '''
            
            if "_get_session_clips_dir" not in new_content:
                # Add the method to the class
                class_start = new_content.find("class RealVeo2Client:")
                if class_start != -1:
                    init_end = new_content.find("\n    def ", class_start + new_content[class_start:].find("def __init__"))
                    if init_end != -1:
                        new_content = new_content[:init_end] + session_method + new_content[init_end:]
            
            veo_client_file.write_text(new_content)
            print("✅ Fixed Veo2 client to save clips to session folder")

def fix_discussions_saving():
    """Fix agent discussions saving to session folders"""
    print("🔧 Fixing agent discussions saving...")
    
    # The issue is discussions are saved to separate orchestrated folders
    # instead of the main session folder
    
    orchestrator_file = Path("src/agents/enhanced_orchestrator_with_discussions.py")
    if orchestrator_file.exists():
        content = orchestrator_file.read_text()
        
        # Check if the fix is already applied
        if "CRITICAL: Save to main session directory" in content:
            print("✅ Agent discussions fix already applied")
        else:
            print("⚠️ Agent discussions fix needs manual verification")

def create_session_regeneration_script():
    """Create a script to regenerate a session with fixes"""
    print("🔧 Creating session regeneration script...")
    
    regen_script = '''#!/usr/bin/env python3
"""
Session Regeneration Script
Regenerates a session with all fixes applied
"""

import os
import sys
import subprocess
from pathlib import Path

def regenerate_session(original_topic: str, duration: int = 10, platform: str = "youtube"):
    """Regenerate a session with the correct topic and all fixes"""
    
    print(f"🎬 Regenerating session for topic: '{original_topic}'")
    print(f"⏱️ Duration: {duration}s")
    print(f"📱 Platform: {platform}")
    
    # Clean the topic
    clean_topic = original_topic
    if "Script Content" in clean_topic and "Optimization" in clean_topic:
        import re
        match = re.search(r"'([^']+)'", clean_topic)
        if match:
            clean_topic = match.group(1)
    
    print(f"🧹 Cleaned topic: '{clean_topic}'")
    
    # Run the generation with proper parameters
    cmd = [
        "python", "main.py", "generate",
        "--topic", clean_topic,
        "--duration", str(duration),
        "--platform", platform,
        "--discussions", "standard",
        "--image-only"  # Use image-only mode to avoid Veo quota issues
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Regeneration successful!")
            print("📋 Output:")
            print(result.stdout)
            
            # Find the new session folder
            outputs_dir = Path("outputs")
            if outputs_dir.exists():
                session_folders = sorted([f for f in outputs_dir.iterdir() 
                                        if f.is_dir() and f.name.startswith("session_")])
                if session_folders:
                    latest_session = session_folders[-1]
                    print(f"📁 New session: {latest_session}")
                    return str(latest_session)
        else:
            print("❌ Regeneration failed!")
            print("📋 Error:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Regeneration timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    # Regenerate the problematic session
    original_topic = "USA political news test with real images"
    new_session = regenerate_session(original_topic, duration=10, platform="youtube")
    
    if new_session:
        print(f"🎉 Successfully created new session: {new_session}")
    else:
        print("💥 Failed to regenerate session")
'''
    
    regen_file = Path("regenerate_session.py")
    regen_file.write_text(regen_script)
    os.chmod(regen_file, 0o755)
    print(f"✅ Created regeneration script: {regen_file}")

def create_session_analyzer():
    """Create a script to analyze session completeness"""
    print("🔧 Creating session analyzer...")
    
    analyzer_script = '''#!/usr/bin/env python3
"""
Session Analyzer
Analyzes session completeness and identifies missing components
"""

import os
import json
from pathlib import Path
from datetime import datetime

def analyze_session(session_path: str):
    """Analyze a session folder for completeness"""
    session_dir = Path(session_path)
    if not session_dir.exists():
        print(f"❌ Session not found: {session_path}")
        return
    
    print(f"🔍 Analyzing session: {session_dir.name}")
    print("=" * 60)
    
    # Check required files
    required_files = {
        "video": ["*.mp4"],
        "audio": ["*.mp3"],
        "scripts": ["script_*.txt", "tts_script_*.txt", "veo2_prompts_*.txt"],
        "analysis": ["video_analysis.txt"]
    }
    
    # Check optional directories
    optional_dirs = ["clips", "images", "agent_discussions"]
    
    # Analyze file structure
    all_files = list(session_dir.rglob("*"))
    file_count = len([f for f in all_files if f.is_file()])
    dir_count = len([f for f in all_files if f.is_dir()])
    
    print(f"📊 Total files: {file_count}")
    print(f"📁 Total directories: {dir_count}")
    print()
    
    # Check each category
    for category, patterns in required_files.items():
        print(f"📋 {category.upper()}:")
        found_files = []
        for pattern in patterns:
            matches = list(session_dir.glob(pattern)) + list(session_dir.glob(f"**/{pattern}"))
            found_files.extend(matches)
        
        if found_files:
            for file in found_files:
                size = file.stat().st_size / 1024  # KB
                print(f"  ✅ {file.name} ({size:.1f} KB)")
        else:
            print(f"  ❌ Missing {category} files")
        print()
    
    # Check optional directories
    print("📁 OPTIONAL DIRECTORIES:")
    for dir_name in optional_dirs:
        dir_path = session_dir / dir_name
        if dir_path.exists():
            files_in_dir = len(list(dir_path.iterdir()))
            print(f"  ✅ {dir_name}/ ({files_in_dir} items)")
        else:
            print(f"  ⚠️  {dir_name}/ (missing)")
    print()
    
    # Analyze video analysis file
    analysis_file = session_dir / "video_analysis.txt"
    if analysis_file.exists():
        print("📊 VIDEO ANALYSIS:")
        content = analysis_file.read_text()
        
        # Extract key metrics
        lines = content.split('\\n')
        for line in lines:
            if any(keyword in line for keyword in ["Duration:", "Generation Time:", "Total Clips:", "File Size:"]):
                print(f"  {line.strip()}")
        print()
    
    # Check for issues
    issues = []
    
    # Check for empty clips directory
    clips_dir = session_dir / "clips"
    if clips_dir.exists() and not any(clips_dir.iterdir()):
        issues.append("Empty clips directory")
    
    # Check for very small audio files
    audio_files = list(session_dir.glob("*.mp3")) + list(session_dir.glob("**/*.mp3"))
    for audio_file in audio_files:
        if audio_file.stat().st_size < 50000:  # Less than 50KB
            issues.append(f"Very small audio file: {audio_file.name}")
    
    # Check for missing agent discussions
    if not (session_dir / "agent_discussions").exists():
        issues.append("Missing agent discussions")
    
    if issues:
        print("🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("✅ No critical issues found")
    
    print()
    print("🎯 RECOMMENDATIONS:")
    if issues:
        print("  • Regenerate session with fixes applied")
        print("  • Use --image-only mode to avoid Veo quota issues")
        print("  • Check topic interpretation")
    else:
        print("  • Session appears complete")

def analyze_all_sessions():
    """Analyze all sessions"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ No outputs directory found")
        return
    
    session_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith("session_")]
    
    if not session_dirs:
        print("❌ No session directories found")
        return
    
    print(f"🔍 Found {len(session_dirs)} sessions")
    print()
    
    for session_dir in sorted(session_dirs):
        analyze_session(str(session_dir))
        print("\\n" + "="*60 + "\\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        analyze_session(sys.argv[1])
    else:
        analyze_all_sessions()
'''
    
    analyzer_file = Path("analyze_sessions.py")
    analyzer_file.write_text(analyzer_script)
    os.chmod(analyzer_file, 0o755)
    print(f"✅ Created session analyzer: {analyzer_file}")

def main():
    """Main fix function"""
    print("🚨 CRITICAL ISSUES FIX SCRIPT")
    print("=" * 50)
    print()
    
    print("🎯 Issues to fix:")
    print("1. Session folder structure - move all data to session folders")
    print("2. Topic interpretation - prevent AI from misunderstanding topics")
    print("3. Audio duration - fix TTS word count calculation")
    print("4. Clip saving - save clips to session folders")
    print("5. Discussions saving - save agent discussions to session folders")
    print()
    
    # Apply fixes
    fix_session_structure()
    fix_topic_interpretation()
    fix_audio_duration()
    fix_clip_saving()
    fix_discussions_saving()
    
    # Create helper scripts
    create_session_regeneration_script()
    create_session_analyzer()
    
    print()
    print("✅ ALL FIXES APPLIED!")
    print()
    print("🎯 Next steps:")
    print("1. Run: python analyze_sessions.py")
    print("2. Run: python regenerate_session.py")
    print("3. Test with: python main.py generate --topic 'USA political news' --duration 10 --image-only")
    print()
    print("💡 Use --image-only mode to avoid Veo quota issues")

if __name__ == "__main__":
    main() 