#!/usr/bin/env python3
"""Quick multi-language e2e test script"""

import subprocess
import json
import os
import time
from datetime import datetime

def run_test(test_num, languages, mission):
    """Run a single multi-language test"""
    session_id = f"multilang_e2e_test_{test_num}_{int(time.time())}"
    
    cmd = [
        "python3", "main.py", "generate",
        "--mission", mission,
        "--cheap",
        "--duration", "15",
        "--session-id", session_id
    ]
    
    # Add languages
    for lang in languages:
        cmd.extend(["--languages", lang])
    
    print(f"\n{'='*60}")
    print(f"Test {test_num}: {', '.join(languages)}")
    print(f"Mission: {mission[:50]}...")
    print(f"Session: {session_id}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    
    # Check results
    output_dir = f"outputs/{session_id}"
    languages_dir = f"{output_dir}/languages"
    
    success = False
    language_files = {}
    
    if os.path.exists(languages_dir):
        # Check each language
        for lang in languages:
            lang_code = lang.replace('-', '_')
            lang_dir = f"{languages_dir}/{lang_code}"
            
            if os.path.exists(lang_dir):
                files = {
                    'audio': os.path.exists(f"{lang_dir}/audio_{lang_code}.mp3"),
                    'subtitles': os.path.exists(f"{lang_dir}/subtitles_{lang_code}.srt"),
                    'video': os.path.exists(f"{lang_dir}/video_{lang_code}.mp4")
                }
                language_files[lang] = files
                
                if all(files.values()):
                    success = True
    
    # Print results
    print(f"\nTest {test_num} Results:")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Success: {'✅' if success else '❌'}")
    print(f"  Languages generated: {len(language_files)}/{len(languages)}")
    
    for lang, files in language_files.items():
        print(f"  {lang}: Audio={'✅' if files.get('audio') else '❌'} "
              f"Subtitles={'✅' if files.get('subtitles') else '❌'} "
              f"Video={'✅' if files.get('video') else '❌'}")
    
    if result.stderr:
        print(f"  Errors: {result.stderr[:200]}...")
    
    return success, duration, language_files

def main():
    """Run multiple multi-language e2e tests"""
    print("🌍 Multi-Language E2E Tests")
    print(f"Started: {datetime.now()}")
    
    tests = [
        # Test 1: Basic 2 languages
        {
            'languages': ['en-US', 'he'],
            'mission': 'Breaking news about renewable energy'
        },
        # Test 2: 3 languages with RTL
        {
            'languages': ['en-US', 'he', 'ar'],
            'mission': 'Technology transforms daily life'
        },
        # Test 3: 4 languages
        {
            'languages': ['en-US', 'es', 'fr', 'de'],
            'mission': 'Climate change solutions discovered'
        },
        # Test 4: 5 languages with mixed scripts
        {
            'languages': ['en-US', 'he', 'ar', 'th', 'ja'],
            'mission': 'Global cooperation saves planet'
        },
        # Test 5: Persian/Farsi specific
        {
            'languages': ['en-US', 'fa', 'ar'],
            'mission': 'Water crisis innovations emerge'
        }
    ]
    
    results = []
    total_tests = len(tests)
    successful_tests = 0
    
    for i, test in enumerate(tests, 1):
        success, duration, lang_files = run_test(
            i, 
            test['languages'], 
            test['mission']
        )
        
        results.append({
            'test_num': i,
            'success': success,
            'duration': duration,
            'languages': test['languages'],
            'language_files': lang_files
        })
        
        if success:
            successful_tests += 1
        
        # Brief pause between tests
        if i < total_tests:
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\n📈 Test Details:")
    for result in results:
        status = '✅' if result['success'] else '❌'
        print(f"  Test {result['test_num']}: {status} - "
              f"{len(result['language_files'])}/{len(result['languages'])} languages - "
              f"{result['duration']:.1f}s")
    
    # Save results
    with open('multilang_e2e_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: multilang_e2e_results.json")
    print(f"Completed: {datetime.now()}")

if __name__ == "__main__":
    main()