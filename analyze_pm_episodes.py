#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging

def extract_duration_from_log(log_content: str) -> Dict[str, any]:
    """Extract duration information from log content."""
    result = {
        'target_duration': None,
        'actual_duration': None,
        'audio_duration': None,
        'video_duration': None,
        'warnings': [],
        'errors': []
    }
    
    # Extract target duration
    target_match = re.search(r'Target duration:\s*([\d.]+)', log_content)
    if target_match:
        result['target_duration'] = float(target_match.group(1))
    
    # Extract actual/final duration
    final_match = re.search(r'Final video duration:\s*([\d.]+)', log_content)
    if final_match:
        result['actual_duration'] = float(final_match.group(1))
    
    # Extract audio duration
    audio_match = re.search(r'Audio duration:\s*([\d.]+)', log_content)
    if audio_match:
        result['audio_duration'] = float(audio_match.group(1))
    
    # Extract warnings
    warning_matches = re.findall(r'WARNING.*?$', log_content, re.MULTILINE)
    result['warnings'] = warning_matches[:5]  # Keep first 5 warnings
    
    # Extract errors
    error_matches = re.findall(r'ERROR.*?$', log_content, re.MULTILINE)
    result['errors'] = error_matches[:5]  # Keep first 5 errors
    
    # Check for TTS speed warnings
    tts_warning = re.search(r'TTS speed factor:\s*([\d.]+)', log_content)
    if tts_warning and float(tts_warning.group(1)) > 1.2:
        result['warnings'].append(f"High TTS speed factor: {tts_warning.group(1)}")
    
    return result

def count_segments(episode_dir: Path) -> Dict[str, int]:
    """Count audio and subtitle segments."""
    result = {
        'audio_segments': 0,
        'subtitle_segments': 0,
        'script_segments': 0
    }
    
    # Count audio segments
    audio_dir = episode_dir / 'audio'
    if audio_dir.exists():
        result['audio_segments'] = len(list(audio_dir.glob('segment_*.mp3')))
    
    # Count subtitle segments
    subtitles_file = episode_dir / 'subtitles' / 'subtitles.srt'
    if subtitles_file.exists():
        content = subtitles_file.read_text()
        # Count subtitle entries (they start with numbers)
        result['subtitle_segments'] = len(re.findall(r'^\d+$', content, re.MULTILINE))
    
    # Count script segments from final script
    script_file = episode_dir / 'scripts' / 'final_script.json'
    if script_file.exists():
        try:
            with open(script_file) as f:
                script_data = json.load(f)
                if 'segments' in script_data:
                    result['script_segments'] = len(script_data['segments'])
        except:
            pass
    
    return result

def check_output_files(episode_dir: Path) -> Dict[str, bool]:
    """Check if all expected output files exist."""
    expected_files = {
        'final_video': 'final_output/final_video.mp4',
        'audio_track': 'audio/final_audio.mp3',
        'subtitles': 'subtitles/subtitles.srt',
        'final_script': 'scripts/final_script.json',
        'metadata': 'metadata/session_metadata.json'
    }
    
    result = {}
    for name, path in expected_files.items():
        full_path = episode_dir / path
        result[name] = full_path.exists()
    
    return result

def analyze_episode(episode_dir: Path) -> Dict:
    """Analyze a single episode."""
    episode_name = episode_dir.name
    
    # Find the main log file
    log_files = list(episode_dir.glob('logs/*.log'))
    main_log = None
    for log_file in log_files:
        if 'main' in log_file.name or 'session' in log_file.name:
            main_log = log_file
            break
    
    if not main_log and log_files:
        main_log = log_files[0]
    
    # Extract duration info
    duration_info = {'target_duration': None, 'actual_duration': None, 'audio_duration': None, 'warnings': [], 'errors': []}
    if main_log and main_log.exists():
        try:
            log_content = main_log.read_text()
            duration_info = extract_duration_from_log(log_content)
        except:
            duration_info['errors'].append("Failed to read log file")
    
    # Count segments
    segments = count_segments(episode_dir)
    
    # Check output files
    output_files = check_output_files(episode_dir)
    
    # Determine sync status
    sync_status = "Good"
    issues = []
    
    if duration_info['target_duration'] and duration_info['actual_duration']:
        diff = abs(duration_info['actual_duration'] - duration_info['target_duration'])
        if diff > 5:
            sync_status = "Warning"
            issues.append(f"Duration mismatch: {diff:.1f}s")
    
    if segments['audio_segments'] != segments['script_segments'] and segments['script_segments'] > 0:
        sync_status = "Warning" if sync_status == "Good" else "Error"
        issues.append(f"Segment mismatch: {segments['audio_segments']} audio vs {segments['script_segments']} script")
    
    if duration_info['errors']:
        sync_status = "Error"
        issues.extend(duration_info['errors'][:2])
    
    if not all(output_files.values()):
        sync_status = "Error"
        missing = [k for k, v in output_files.items() if not v]
        issues.append(f"Missing files: {', '.join(missing)}")
    
    return {
        'episode': episode_name,
        'target_duration': duration_info['target_duration'],
        'actual_duration': duration_info['actual_duration'],
        'audio_duration': duration_info['audio_duration'],
        'audio_segments': segments['audio_segments'],
        'script_segments': segments['script_segments'],
        'subtitle_segments': segments['subtitle_segments'],
        'sync_status': sync_status,
        'issues': issues[:3],  # Limit to 3 issues
        'warnings': duration_info['warnings'][:2],
        'output_files': output_files
    }

def main():
    # Find all episode directories
    outputs_dir = Path('/Users/yahavzamari/viralAi/outputs')
    episode_dirs = sorted([d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith('israeli_pm_ep')])
    
    results = []
    for episode_dir in episode_dirs:
        print(f"Analyzing {episode_dir.name}...")
        result = analyze_episode(episode_dir)
        results.append(result)
    
    # Print summary table
    print("\n" + "="*120)
    print("ISRAELI PRIME MINISTER SERIES - HEALTH CHECK SUMMARY")
    print("="*120)
    print(f"{'Episode':<25} {'Target':<8} {'Actual':<8} {'Audio':<8} {'Segments':<15} {'Sync':<10} {'Key Issues'}")
    print("-"*120)
    
    for r in results:
        target = f"{r['target_duration']:.1f}s" if r['target_duration'] else "N/A"
        actual = f"{r['actual_duration']:.1f}s" if r['actual_duration'] else "N/A"
        audio = f"{r['audio_duration']:.1f}s" if r['audio_duration'] else "N/A"
        segments = f"{r['audio_segments']}/{r['script_segments']}/{r['subtitle_segments']}"
        issues = "; ".join(r['issues']) if r['issues'] else "None"
        
        # Color code the sync status
        status_color = ""
        if r['sync_status'] == "Good":
            status_color = "\033[92m"  # Green
        elif r['sync_status'] == "Warning":
            status_color = "\033[93m"  # Yellow
        else:
            status_color = "\033[91m"  # Red
        
        print(f"{r['episode']:<25} {target:<8} {actual:<8} {audio:<8} {segments:<15} {status_color}{r['sync_status']:<10}\033[0m {issues}")
    
    print("-"*120)
    
    # Summary statistics
    total = len(results)
    good = sum(1 for r in results if r['sync_status'] == "Good")
    warnings = sum(1 for r in results if r['sync_status'] == "Warning")
    errors = sum(1 for r in results if r['sync_status'] == "Error")
    
    print(f"\nSUMMARY: Total Episodes: {total} | Good: {good} | Warnings: {warnings} | Errors: {errors}")
    
    # Common issues
    print("\n" + "="*120)
    print("COMMON ISSUES FOUND:")
    print("="*120)
    
    all_issues = []
    for r in results:
        all_issues.extend(r['issues'])
        all_issues.extend(r['warnings'])
    
    from collections import Counter
    issue_counts = Counter(all_issues)
    for issue, count in issue_counts.most_common(10):
        print(f"- {issue} (found in {count} episodes)")
    
    # File completeness check
    print("\n" + "="*120)
    print("FILE COMPLETENESS CHECK:")
    print("="*120)
    
    file_types = ['final_video', 'audio_track', 'subtitles', 'final_script', 'metadata']
    for file_type in file_types:
        complete = sum(1 for r in results if r['output_files'].get(file_type, False))
        print(f"- {file_type}: {complete}/{total} episodes complete")

if __name__ == "__main__":
    main()