#!/usr/bin/env python3
"""
Test script for Netanyahu Marvel Episode with enhanced duration management
"""

import subprocess
import sys
import os

def test_netanyahu_marvel_episode():
    """Test the enhanced system with the Netanyahu Marvel Episode script"""
    
    print("🚀 Testing Enhanced Duration Management with Netanyahu Marvel Episode")
    print("=" * 70)
    
    # Netanyahu Marvel Episode mission
    mission = """Marvel Comics explosion! Benjamin Netanyahu with slicked-back hair bursts from Tel Aviv skyline. 
    'I am the GUARDIAN of Israel!' SNAP! Hamas tunnels vanish in comic smoke. 
    Security barrier with exploding panels. KA-POW! Speaking at UN with energy effects. 
    Building high-tech nation. Political comebacks. 'Bibi will return!' Israeli flag waves."""
    
    # Test command
    cmd = [
        "python", "main.py", "generate",
        "--mission", mission,
        "--duration", "50",
        "--platform", "instagram",
        "--style", "cinematic",
        "--tone", "dramatic",
        "--visual-style", "marvel comics",
        "--character", "Benjamin Netanyahu with slicked-back gray hair, sharp features, determined expression, wearing dark suit like Israeli PM",
        "--scene", "Tel Aviv skyline background, Marvel Comics style, dramatic lighting, Israeli flag prominent",
        "--session-id", "netanyahu_marvel_test",
        "--mode", "enhanced",
        "--voice", "Anthony",
        "--no-cheap"  # Ensure full VEO generation
    ]
    
    print("📋 Test Configuration:")
    print(f"   Mission: {mission[:100]}...")
    print(f"   Duration: 50 seconds")
    print(f"   Platform: Instagram")
    print(f"   Mode: Enhanced (7 agents)")
    print(f"   Character: Netanyahu in Marvel style")
    print()
    
    print("🎬 Running video generation...")
    print("Command:", " ".join(cmd))
    print()
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/yahavzamari/viralAi")
        
        # Check for specific enhancements in output
        enhancements_found = []
        
        # Check for audio duration validation
        if "Audio Duration Analysis:" in result.stdout:
            enhancements_found.append("✅ Audio duration validation")
        
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
        
        print("\n📊 Enhancement Detection Results:")
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
            print("\n✅ Video generation completed successfully!")
            
            # Check output directory
            output_dir = f"/Users/yahavzamari/viralAi/outputs/netanyahu_marvel_test"
            if os.path.exists(output_dir):
                print(f"\n📁 Output directory: {output_dir}")
                
                # Check for key files
                key_files = [
                    "final_output/final_video_netanyahu_marvel_test__final.mp4",
                    "audio/audio_segment_0.mp3",
                    "subtitles/subtitles.srt",
                    "logs/duration_report.json",
                    "duration_feedback/"  # New feedback directory
                ]
                
                for file_path in key_files:
                    full_path = os.path.join(output_dir, file_path)
                    if os.path.exists(full_path):
                        print(f"   ✅ {file_path}")
                    else:
                        print(f"   ❌ {file_path} (missing)")
        
        # Save full output for analysis
        with open("/Users/yahavzamari/viralAi/test_output.log", "w") as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
        
        print(f"\n📝 Full output saved to: test_output.log")
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_netanyahu_marvel_episode()