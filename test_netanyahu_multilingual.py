#!/usr/bin/env python3
"""
Test script for Netanyahu Marvel Episode with multilingual support (English + Hebrew)
Tests enhanced duration management and content filter handling
"""

import subprocess
import sys
import os
import time
import json

def run_test(language_options, test_name):
    """Run a single test with given language options"""
    print(f"\n{'='*70}")
    print(f"🚀 Running {test_name}")
    print(f"{'='*70}\n")
    
    # Netanyahu Marvel Episode mission
    mission = """Marvel Comics explosion! Benjamin Netanyahu with slicked-back hair bursts from Tel Aviv skyline. 
    'I am the GUARDIAN of Israel!' SNAP! Hamas tunnels vanish in comic smoke. 
    Security barrier with exploding panels. KA-POW! Speaking at UN with energy effects. 
    Building high-tech nation. Political comebacks. 'Bibi will return!' Israeli flag waves."""
    
    # Test command
    cmd = [
        "python", "main.py", "generate",
        "--mission", mission,
        "--duration", "30",  # Shorter duration for testing
        "--platform", "instagram",
        "--style", "cinematic",
        "--tone", "dramatic",
        "--visual-style", "marvel comics",
        "--character", "Benjamin Netanyahu with slicked-back gray hair, sharp features, determined expression, wearing dark suit like Israeli PM",
        "--scene", "Tel Aviv skyline background, Marvel Comics style, dramatic lighting, Israeli flag prominent",
        "--session-id", f"netanyahu_test_{test_name.lower().replace(' ', '_')}",
        "--mode", "enhanced",
        "--voice", "Anthony",
        "--no-cheap"  # Ensure full VEO generation
    ] + language_options
    
    print("📋 Test Configuration:")
    print(f"   Languages: {' + '.join([opt for opt in language_options if opt != '--languages'])}")
    print(f"   Duration: 30 seconds")
    print(f"   Platform: Instagram")
    print(f"   Mode: Enhanced (7 agents)")
    print()
    
    print("🎬 Running video generation...")
    print("Command:", " ".join(cmd))
    print()
    
    # Track start time
    start_time = time.time()
    
    try:
        # Run the command with a timeout
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd="/Users/yahavzamari/viralAi",
            timeout=300  # 5 minute timeout per test
        )
        
        # Track end time
        end_time = time.time()
        duration = end_time - start_time
        
        # Check for specific enhancements in output
        enhancements_found = []
        
        # Check for audio duration validation
        if "Audio Duration Analysis:" in result.stdout:
            enhancements_found.append("✅ Audio duration validation")
        
        # Check for script modification for content filter
        if "Using Gemini to modify script" in result.stdout or "modified script for content compliance" in result.stdout:
            enhancements_found.append("✅ Gemini script modification for content filter")
        
        # Check for minimum segment duration
        if "Applying minimum segment duration threshold" in result.stdout:
            enhancements_found.append("✅ Minimum segment duration thresholds")
        
        # Check for sound effect handling
        if "Processing sound effects in script segments" in result.stdout:
            enhancements_found.append("✅ Sound effect handling")
        
        # Check for padding between segments
        if "Adding padding between" in result.stdout:
            enhancements_found.append("✅ Audio segment padding")
        
        # Check for content filter retry
        if "Using safety level" in result.stdout or "rephrasing" in result.stdout:
            enhancements_found.append("✅ Content filter retry mechanism")
        
        # Check for duration feedback
        if "Duration Feedback" in result.stdout:
            enhancements_found.append("✅ Duration feedback system")
        
        # Check for final validation
        if "Performing final duration validation" in result.stdout:
            enhancements_found.append("✅ Final duration validation")
        
        # Check for multilingual support
        if "languages:" in result.stdout.lower() and ("hebrew" in result.stdout.lower() or "he" in result.stdout.lower()):
            enhancements_found.append("✅ Multilingual processing (Hebrew)")
        
        print(f"\n📊 Enhancement Detection Results:")
        for enhancement in enhancements_found:
            print(f"   {enhancement}")
        
        if not enhancements_found:
            print("   ⚠️ No enhancements detected in output")
        
        # Check for errors
        if result.returncode != 0:
            print(f"\n❌ Command failed with return code: {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr[-2000:])  # Last 2000 chars of error
        else:
            print(f"\n✅ Video generation completed successfully in {duration:.1f}s!")
            
            # Check output directory
            session_id = f"netanyahu_test_{test_name.lower().replace(' ', '_')}"
            output_dir = f"/Users/yahavzamari/viralAi/outputs/{session_id}"
            if os.path.exists(output_dir):
                print(f"\n📁 Output directory: {output_dir}")
                
                # Check for key files
                key_files = [
                    "final_output/",
                    "audio/",
                    "subtitles/subtitles.srt",
                    "logs/duration_report.json",
                    "duration_feedback/"
                ]
                
                for file_path in key_files:
                    full_path = os.path.join(output_dir, file_path)
                    if os.path.exists(full_path):
                        if os.path.isdir(full_path):
                            file_count = len(os.listdir(full_path))
                            print(f"   ✅ {file_path} ({file_count} files)")
                        else:
                            print(f"   ✅ {file_path}")
                    else:
                        print(f"   ❌ {file_path} (missing)")
                
                # Check duration feedback
                feedback_dir = os.path.join(output_dir, "duration_feedback")
                if os.path.exists(feedback_dir):
                    feedback_files = os.listdir(feedback_dir)
                    if feedback_files:
                        print(f"\n📊 Duration Feedback Checkpoints:")
                        for ff in sorted(feedback_files):
                            if ff.endswith('.json'):
                                with open(os.path.join(feedback_dir, ff), 'r') as f:
                                    data = json.load(f)
                                    print(f"   - {data['stage']}: {data['actual_duration']:.1f}s " +
                                          f"(target: {data['target_duration']}s) - " +
                                          ("✅" if data['is_within_tolerance'] else "⚠️"))
        
        # Save full output for analysis
        log_file = f"/Users/yahavzamari/viralAi/test_output_{test_name.lower().replace(' ', '_')}.log"
        with open(log_file, "w") as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
        
        print(f"\n📝 Full output saved to: {log_file}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"\n⏱️ Test timed out after 300 seconds")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all multilingual tests"""
    print("🎬 Netanyahu Marvel Episode - Multilingual Test Suite")
    print("Testing enhanced duration management and content filter handling")
    print("=" * 70)
    
    tests = [
        (["--languages", "en-US"], "English Only"),
        (["--languages", "en-US", "--languages", "he"], "English + Hebrew"),
        (["--languages", "he"], "Hebrew Only")
    ]
    
    results = []
    
    for language_opts, test_name in tests:
        success = run_test(language_opts, test_name)
        results.append((test_name, success))
        
        # Brief pause between tests
        if test_name != tests[-1][1]:
            print("\n⏸️ Pausing before next test...\n")
            time.sleep(5)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())