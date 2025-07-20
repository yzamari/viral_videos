#!/usr/bin/env python3
"""
Quick Test Verification Script
Verify that all 216 unit tests are passing
"""

import subprocess
import sys
import os

def verify_all_tests():
    """Quickly verify all tests are passing"""
    
    print("🔍 VERIFYING UNIT TESTS...")
    print("Expected: 216 tests passing")
    print("-" * 40)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with minimal output
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/unit/", 
        "--tb=no",
        "-q",
        "--disable-warnings"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS: All tests passed!")
            print("🎉 Status: PRODUCTION READY")
            print("\n📊 Details:")
            print(result.stdout)
            return True
        else:
            print("❌ FAILURE: Some tests failed!")
            print("🔧 Action required: Fix failing tests")
            print("\n📊 Details:")
            print(result.stdout)
            if result.stderr:
                print("\nErrors:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Test execution failed: {e}")
        return False

def main():
    """Main entry point"""
    success = verify_all_tests()
    
    if success:
        print("\n🚀 SYSTEM READY FOR DEPLOYMENT")
        sys.exit(0)
    else:
        print("\n⚠️  SYSTEM NOT READY - FIX TESTS FIRST")
        sys.exit(1)

if __name__ == '__main__':
    main() 