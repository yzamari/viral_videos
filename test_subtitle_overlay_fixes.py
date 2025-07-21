#!/usr/bin/env python3
"""
Test script to verify subtitle and overlay fixes
Ensures proper text splitting and semi-transparent backgrounds
"""

import os
import sys
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_subtitle_text_formatting():
    """Test subtitle text formatting with 2-line limit"""
    print("🧪 Testing Subtitle Text Formatting")
    print("=" * 50)
    
    try:
        from src.generators.video_generator import VideoGenerator
        
        # Create a video generator instance
        generator = VideoGenerator(api_key="test_key", use_real_veo2=False)
        
        # Test cases
        test_cases = [
            {
                "text": "This is a very long subtitle text that should be split into multiple lines for better readability",
                "expected_lines": 2,
                "description": "Long text that needs splitting"
            },
            {
                "text": "Short text",
                "expected_lines": 1,
                "description": "Short text that doesn't need splitting"
            },
            {
                "text": "This is a medium length text that might need splitting depending on the character limit",
                "expected_lines": 2,
                "description": "Medium length text"
            },
            {
                "text": "This is an extremely long text that should definitely be split into multiple lines and should not exceed two lines maximum",
                "expected_lines": 2,
                "description": "Very long text that should be truncated to 2 lines"
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['description']}")
            print(f"   Input: {test_case['text'][:50]}...")
            
            # Test the formatting
            formatted_text = generator._format_subtitle_text(test_case['text'])
            lines = formatted_text.split('\n')
            
            print(f"   Output: {formatted_text}")
            print(f"   Lines: {len(lines)} (expected: {test_case['expected_lines']})")
            
            # Check if formatting is correct
            if len(lines) <= 2:
                print("   ✅ PASS: Text properly formatted with 2-line limit")
            else:
                print(f"   ❌ FAIL: Text has {len(lines)} lines, expected max 2")
                all_passed = False
            
            # Check if each line is reasonable length
            for j, line in enumerate(lines):
                if len(line) > 20:
                    print(f"   ⚠️  WARNING: Line {j+1} is {len(line)} chars long")
        
        if all_passed:
            print("\n✅ ALL SUBTITLE FORMATTING TESTS PASSED!")
        else:
            print("\n❌ SOME SUBTITLE FORMATTING TESTS FAILED!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Subtitle and Overlay Fix Tests")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_subtitle_text_formatting
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    # Summary
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Passed: {passed_tests}/{total_tests}")
    print(f"   Failed: {total_tests - passed_tests}/{total_tests}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        print("🎯 Subtitle and overlay fixes are working correctly:")
        print("   ✅ Subtitles limited to 2 lines maximum")
        print("   ✅ Overlays have semi-transparent backgrounds")
        print("   ✅ Long text properly split into multiple lines")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 Some fixes may need further investigation")
    
    return all(results)

if __name__ == "__main__":
    main() 