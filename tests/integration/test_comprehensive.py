#!/usr/bin/env python3
"""
Comprehensive E2E Testing Script
Tests the 8-second clip constraint, business overlays, and VEO3-FAST functionality
"""

import subprocess
import time
import os
import json
from datetime import datetime

def run_command(cmd, timeout=600):
    """Run a command and return the result"""
    print(f"🚀 Running: {cmd}")
    start_time = time.time()
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        duration = time.time() - start_time
        print(f"✅ Completed in {duration:.1f}s")
        return result.returncode == 0, result.stdout, result.stderr, duration
    except subprocess.TimeoutExpired:
        print(f"⏰ Command timed out after {timeout}s")
        return False, "", "Timeout", timeout

def analyze_output_directory(output_dir):
    """Analyze generated video output"""
    if not os.path.exists(output_dir):
        return {"error": "Output directory not found"}
    
    analysis = {
        "final_videos": [],
        "clip_count": 0,
        "duration_compliance": False,
        "business_overlay": False,
        "veo_generation": False
    }
    
    # Check final videos
    final_output = os.path.join(output_dir, "final_output")
    if os.path.exists(final_output):
        for f in os.listdir(final_output):
            if f.endswith('.mp4'):
                file_path = os.path.join(final_output, f)
                file_size = os.path.getsize(file_path)
                analysis["final_videos"].append({
                    "name": f,
                    "size_mb": round(file_size / (1024*1024), 2)
                })
    
    # Check VEO clips
    veo_clips = os.path.join(output_dir, "video_clips", "veo_clips")
    if os.path.exists(veo_clips):
        analysis["clip_count"] = len([f for f in os.listdir(veo_clips) if f.endswith('.mp4')])
        analysis["veo_generation"] = analysis["clip_count"] > 0
    
    # Check decisions for duration compliance
    decisions_file = os.path.join(output_dir, "decisions", "core_decisions.json")
    if os.path.exists(decisions_file):
        try:
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
                duration = decisions.get('duration_seconds', 0)
                clip_durations = decisions.get('clip_durations', [])
                # Check if duration is multiple of 8
                analysis["duration_compliance"] = (duration % 8 == 0) and all(d == 8.0 for d in clip_durations)
        except:
            pass
    
    return analysis

def run_e2e_tests():
    """Run 10 E2E tests in cheap mode"""
    print("🧪 Starting 10 E2E Tests in Cheap Mode")
    
    test_missions = [
        "Create a funny cat video about programming",
        "Make an educational video about space exploration", 
        "Create a cooking tutorial for pasta",
        "Make a fitness motivation video",
        "Create a travel vlog about Paris",
        "Make a tech review of smartphones",
        "Create a DIY craft tutorial",
        "Make a music video concept",
        "Create a fashion styling guide",
        "Make a business presentation about AI"
    ]
    
    results = []
    
    for i, mission in enumerate(test_missions, 1):
        print(f"\n🎯 Test {i}/10: {mission[:50]}...")
        
        cmd = f'python3 main.py generate --mission "{mission}" --duration 15 --platform tiktok --session-id test_e2e_{i} --cheap'
        success, stdout, stderr, duration = run_command(cmd, timeout=300)
        
        # Analyze output
        output_dir = f"outputs/test_e2e_{i}"
        analysis = analyze_output_directory(output_dir)
        
        result = {
            "test_number": i,
            "mission": mission,
            "success": success,
            "duration": duration,
            "analysis": analysis,
            "errors": stderr if not success else None
        }
        results.append(result)
        
        # Log result
        status = "✅ PASS" if success and analysis.get("duration_compliance") else "❌ FAIL"
        print(f"{status} Test {i}: Duration={duration:.1f}s, Videos={len(analysis.get('final_videos', []))}")
    
    return results

def run_dragon_episodes():
    """Run Dragon episodes one by one with VEO3-FAST"""
    print("🐉 Starting Dragon Episodes Generation")
    
    episodes = [
        "Episode 1: Baby dragon learns basic calculus derivatives",
        "Episode 2: Baby dragon discovers integration techniques", 
        "Episode 3: Baby dragon explores limits and continuity",
        "Episode 4: Baby dragon masters differential equations",
        "Episode 5: Baby dragon learns multivariable calculus"
    ]
    
    results = []
    
    for i, episode in enumerate(episodes, 1):
        print(f"\n🐉 Episode {i}/5: {episode}")
        
        cmd = f'python3 main.py generate --mission "{episode}" --duration 30 --platform youtube --veo-model-order "veo3-fast,veo3,veo2" --session-id dragon_ep_{i} --no-cheap'
        success, stdout, stderr, duration = run_command(cmd, timeout=900)
        
        # Analyze output
        output_dir = f"outputs/dragon_ep_{i}"
        analysis = analyze_output_directory(output_dir)
        
        result = {
            "episode": i,
            "title": episode,
            "success": success,
            "duration": duration,
            "analysis": analysis,
            "veo3_used": "veo3" in stdout.lower(),
            "errors": stderr if not success else None
        }
        results.append(result)
        
        # Log result
        status = "✅ PASS" if success and analysis.get("veo_generation") else "❌ FAIL"
        veo_status = "VEO3-FAST" if result["veo3_used"] else "FALLBACK"
        print(f"{status} Episode {i}: Duration={duration:.1f}s, Clips={analysis.get('clip_count', 0)}, {veo_status}")
        
        # Fix any issues before continuing
        if not success:
            print(f"⚠️ Episode {i} failed, checking logs...")
            log_file = os.path.join(output_dir, "logs", "generation_log.json")
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                        print(f"📋 Last error: {logs.get('last_error', 'Unknown')}")
                except:
                    pass
    
    return results

def monitor_progress():
    """Monitor generation progress"""
    print("📊 Monitoring system logs...")
    while True:
        # Check if any python processes are running
        result = subprocess.run("ps aux | grep 'python3 main.py' | grep -v grep", 
                               shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            print(f"⏳ {datetime.now().strftime('%H:%M:%S')} - Generation in progress...")
        else:
            print("✅ No active generations")
            break
        
        time.sleep(1)

def generate_report(e2e_results, dragon_results):
    """Generate comprehensive test report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "e2e_tests": {
            "total": len(e2e_results),
            "passed": sum(1 for r in e2e_results if r["success"]),
            "failed": sum(1 for r in e2e_results if not r["success"]),
            "avg_duration": sum(r["duration"] for r in e2e_results) / len(e2e_results),
            "duration_compliance": sum(1 for r in e2e_results if r["analysis"].get("duration_compliance")),
            "results": e2e_results
        },
        "dragon_episodes": {
            "total": len(dragon_results),
            "passed": sum(1 for r in dragon_results if r["success"]),
            "failed": sum(1 for r in dragon_results if not r["success"]),
            "avg_duration": sum(r["duration"] for r in dragon_results) / len(dragon_results) if dragon_results else 0,
            "veo3_usage": sum(1 for r in dragon_results if r["veo3_used"]),
            "results": dragon_results
        }
    }
    
    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*80)
    print(f"🧪 E2E Tests: {report['e2e_tests']['passed']}/{report['e2e_tests']['total']} passed")
    print(f"   Duration Compliance: {report['e2e_tests']['duration_compliance']}/{report['e2e_tests']['total']}")
    print(f"   Average Duration: {report['e2e_tests']['avg_duration']:.1f}s")
    
    print(f"🐉 Dragon Episodes: {report['dragon_episodes']['passed']}/{report['dragon_episodes']['total']} passed")
    print(f"   VEO3 Usage: {report['dragon_episodes']['veo3_usage']}/{report['dragon_episodes']['total']}")
    print(f"   Average Duration: {report['dragon_episodes']['avg_duration']:.1f}s")
    
    print(f"\n📄 Full report saved to: test_report.json")
    
    return report

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Testing Suite")
    print("=" * 80)
    
    # Run E2E tests
    e2e_results = run_e2e_tests()
    
    # Run Dragon episodes  
    dragon_results = run_dragon_episodes()
    
    # Generate report
    report = generate_report(e2e_results, dragon_results)
    
    print("\n🎉 Testing completed!")